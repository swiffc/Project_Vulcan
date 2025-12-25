"""
Cloud Orchestrator API
FastAPI application for Render deployment.
Routes requests to appropriate agents and proxies desktop commands via Tailscale.
"""

import os
import httpx
import time
import logging
import secrets
from collections import defaultdict
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import APIKeyHeader

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from core.trading_journal import router as trading_journal_router
from core.validation_history import router as validation_history_router
from core.orchestrator_adapter import get_orchestrator, TaskRequest, AgentType
from core.database_adapter import get_db_adapter
from core.metrics.strategy_scoring import get_strategy_scorer
from core.audit_logger import get_audit_logger

# Initialize logging
from core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info("Vulcan Orchestrator starting up...")

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
RELEASE_VERSION = os.getenv("RELEASE_VERSION", "dev")


def filter_sensitive_data(event, hint):
    """Filter sensitive data from Sentry events."""
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["authorization", "x-api-key", "cookie"]
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"
    return event


# Initialize Sentry
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=ENVIRONMENT,
        release=f"vulcan-orchestrator@{RELEASE_VERSION}",
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0 if ENVIRONMENT == "development" else 0.1,
        profiles_sample_rate=1.0 if ENVIRONMENT == "development" else 0.1,
        send_default_pii=False,
        before_send=filter_sensitive_data,
    )
    logger.info(f"Sentry initialized for environment: {ENVIRONMENT}")

app = FastAPI(
    title="Vulcan Orchestrator",
    description="Cloud-hosted AI orchestrator for Project Vulcan",
    version="1.1.0",
)

app.add_middleware(SentryAsgiMiddleware)

# Rate limiting
RATE_LIMIT_DURATION = 60
RATE_LIMIT_REQUESTS = 100
rate_limiter = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    request_times = rate_limiter[client_ip]
    current_time = time.time()
    while request_times and request_times[0] < current_time - RATE_LIMIT_DURATION:
        request_times.pop(0)
    if len(request_times) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    request_times.append(time.time())
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vulcan-web.onrender.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trading_journal_router, prefix="/api")
app.include_router(validation_history_router, prefix="/api")

# =============================================================================
# API Key Authentication
# =============================================================================

DESKTOP_SERVER_URL = os.getenv("DESKTOP_SERVER_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=401, detail="Invalid API Key")


# =============================================================================
# Strategy Management Endpoints (Phase 20)
# =============================================================================


class StrategyCreate(BaseModel):
    name: str
    product_type: str
    schema_json: Dict[str, Any]
    is_experimental: bool = True


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    schema_json: Optional[Dict[str, Any]] = None
    is_experimental: Optional[bool] = None


class PerformanceRecord(BaseModel):
    validation_passed: bool
    error_count: int = 0
    errors_json: Optional[List[Dict]] = None
    execution_time: Optional[float] = None
    user_rating: Optional[int] = None


@app.get("/api/strategies")
async def list_strategies(
    product_type: Optional[str] = None,
    is_experimental: Optional[bool] = None,
    api_key: str = Depends(get_api_key),
):
    """List all strategies with optional filters."""
    db = get_db_adapter()
    strategies = db.list_strategies(
        product_type=product_type, is_experimental=is_experimental
    )
    get_audit_logger().log_api_call("/api/strategies", "GET", "api_user", 200)
    return {"strategies": strategies, "count": len(strategies)}


@app.get("/api/strategies/rankings")
async def get_strategy_rankings(
    product_type: Optional[str] = None,
    limit: int = 10,
    api_key: str = Depends(get_api_key),
):
    """Get ranked list of strategies by score."""
    scorer = get_strategy_scorer()
    rankings = scorer.rank_strategies(product_type=product_type, limit=limit)
    return {"rankings": rankings}


@app.get("/api/strategies/{strategy_id}")
async def get_strategy(strategy_id: int, api_key: str = Depends(get_api_key)):
    """Get a single strategy by ID."""
    db = get_db_adapter()
    strategy = db.load_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    get_audit_logger().log_api_call(
        f"/api/strategies/{strategy_id}", "GET", "api_user", 200
    )
    return strategy


@app.post("/api/strategies")
async def create_strategy(data: StrategyCreate, api_key: str = Depends(get_api_key)):
    """Create a new strategy."""
    db = get_db_adapter()
    strategy_data = {
        "name": data.name,
        "product_type": data.product_type,
        "schema_json": data.schema_json,
        "is_experimental": data.is_experimental,
    }
    strategy_id = db.save_strategy(strategy_data)
    get_audit_logger().log_strategy_action(
        "create", strategy_id=strategy_id, strategy_name=data.name
    )
    return {"id": strategy_id, "message": "Strategy created"}


@app.put("/api/strategies/{strategy_id}")
async def update_strategy(
    strategy_id: int, data: StrategyUpdate, api_key: str = Depends(get_api_key)
):
    """Update an existing strategy."""
    db = get_db_adapter()
    existing = db.load_strategy(strategy_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # Merge updates
    updated_schema = (
        data.schema_json if data.schema_json else existing.get("schema_json")
    )
    updated_name = data.name if data.name else existing.get("name")

    update_data = {
        "id": strategy_id,
        "name": updated_name,
        "product_type": existing.get("product_type"),
        "schema_json": updated_schema,
        "is_experimental": (
            data.is_experimental
            if data.is_experimental is not None
            else existing.get("is_experimental")
        ),
    }
    db.save_strategy(update_data)
    get_audit_logger().log_strategy_action("update", strategy_id=strategy_id)
    return {"id": strategy_id, "message": "Strategy updated"}


@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int, api_key: str = Depends(get_api_key)):
    """Delete a strategy."""
    db = get_db_adapter()
    success = db.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    get_audit_logger().log_strategy_action("delete", strategy_id=strategy_id)
    return {"message": "Strategy deleted"}


@app.get("/api/strategies/{strategy_id}/performance")
async def get_strategy_performance(
    strategy_id: int, days: int = 30, api_key: str = Depends(get_api_key)
):
    """Get performance history for a strategy."""
    db = get_db_adapter()
    performance = db.get_strategy_performance(strategy_id, days=days)
    return {"strategy_id": strategy_id, "days": days, "records": performance}


@app.post("/api/strategies/{strategy_id}/performance")
async def record_performance(
    strategy_id: int, data: PerformanceRecord, api_key: str = Depends(get_api_key)
):
    """Record a performance execution for a strategy."""
    db = get_db_adapter()
    existing = db.load_strategy(strategy_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Strategy not found")

    db.record_performance(
        strategy_id=strategy_id,
        validation_passed=data.validation_passed,
        error_count=data.error_count,
        errors=data.errors_json or [],
        execution_time=data.execution_time,
        user_rating=data.user_rating,
    )
    get_audit_logger().log_strategy_action(
        "record_performance",
        strategy_id=strategy_id,
        details={"passed": data.validation_passed},
    )
    return {"message": "Performance recorded"}


@app.get("/api/strategies/{strategy_id}/score")
async def get_strategy_score(
    strategy_id: int, days: int = 30, api_key: str = Depends(get_api_key)
):
    """Calculate and return strategy score."""
    scorer = get_strategy_scorer()
    score = scorer.calculate_score(strategy_id, days=days)
    return {"strategy_id": strategy_id, **score}


@app.post("/api/strategies/{strategy_id}/evolve")
async def evolve_strategy(strategy_id: int, api_key: str = Depends(get_api_key)):
    """Trigger LLM-powered evolution for a strategy."""
    try:
        from agents.cad_agent.strategy_evolution import get_evolution_engine

        engine = get_evolution_engine()
        result = await engine.evolve_strategy(strategy_id, force=True)
        if result:
            get_audit_logger().log_strategy_action(
                "evolve", strategy_id=strategy_id, details={"success": True}
            )
            return {"message": "Strategy evolved", "new_version": result}
        else:
            return {"message": "Evolution not needed or failed"}
    except Exception as e:
        logger.error(f"Evolution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Explain Layer (Phase 21 Gap 16)
# =============================================================================


class ExplanationResponse(BaseModel):
    strategy_id: int
    summary: str
    key_factors: List[str]
    confidence_score: float


@app.get("/api/explain/{strategy_id}")
async def explain_strategy_decision(
    strategy_id: int, api_key: str = Depends(get_api_key)
) -> ExplanationResponse:
    """Generate LLM-based explanation for a strategy's recent performance."""
    # V1: Mock explanation until phase 22 fully connects the LLM-as-Judge
    return ExplanationResponse(
        strategy_id=strategy_id,
        summary=f"Strategy {strategy_id} works well for standard bolt circles but struggles with irregular patterns.",
        key_factors=["Geometry Complexity", "Material Hardness", "Tolerance Stackup"],
        confidence_score=0.92,
    )


# =============================================================================


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    agent: Optional[str] = None


class DesktopCommand(BaseModel):
    endpoint: str
    method: str = "POST"
    payload: Optional[Dict[str, Any]] = None


AGENT_PROMPTS = {
    "trading": """You are the Trading Agent. Specialize in ICT, BTMM, and Stacey Burke.
Analyze setups, bias, and journal lessons. Use desktop commands for TradingView.""",
    "cad": """You are the CAD Agent. Automate SolidWorks/Inventor via COM.
Break down design into sketch, extrude, pattern. Verify alignment (±1/16").
You can read and modify CAD properties. To modify a dimension or custom property, 
respond with: [ACTION: com.solidworks.modify_selection_property(property_name='DIM_NAME', new_value=VALUE_IN_METERS)]
Dimensions provided in context use 'display_value' (e.g. 50mm) and 'value' (meters).""",
    "sketch": """You are the Sketch Agent. Vision-to-CAD specialist.
Interpret drawings/photos into 3D intent and generation parameters.""",
    "work": """You are the Work Agent. Manage J2 Tracker, Outlook, and Teams.
Generate status reports and track project deadlines via Microsoft API.""",
    "general": """General Vulcan Orchestrator. Route to Trading, CAD, Sketch, or Work.""",
}


@app.on_event("startup")
async def startup_event():
    """Register agents and initialize resources."""
    # Start Hands-Free Loop if enabled
    if os.getenv("ENABLE_HANDS_FREE") == "true":
        try:
            from core.hands_free import get_hands_free_loop

            hf = get_hands_free_loop(desktop_url=DESKTOP_SERVER_URL)
            await hf.start()
            logger.info("Hands-Free Voice System ACTIVE")
        except Exception as e:
            logger.error(f"Failed to start Hands-Free system: {e}")

    logger.info("Orchestrator ready with agents: Trading, CAD, Sketch, Work")


@app.get("/health")
async def health():
    """Health check with desktop connectivity."""
    desktop_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DESKTOP_SERVER_URL}/health")
            desktop_status = "connected" if resp.status_code == 200 else "error"
    except Exception:
        desktop_status = "unreachable"

    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "desktop_server": desktop_status,
        "desktop_url": DESKTOP_SERVER_URL,
    }


@app.post("/chat")
async def chat(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """Process chat via OrchestratorAdapter."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = request.messages[-1].content
    orchestrator = get_orchestrator()

    # Use adapter to detect and route
    try:
        agent_type = (
            AgentType(request.agent)
            if request.agent
            else orchestrator.detect_agent(last_message)
        )
    except ValueError:
        logger.warning(
            f"Invalid agent type requested: {request.agent}, falling back to general"
        )
        agent_type = AgentType.GENERAL
    system_prompt = AGENT_PROMPTS.get(agent_type.value, AGENT_PROMPTS["general"])

    # Augment with Active Desktop Context if CAD agent
    desktop_context = ""
    if agent_type == AgentType.CAD:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(
                    f"{DESKTOP_SERVER_URL}/com/solidworks/get_selection_properties"
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("features"):
                        feat = result["features"][0]
                        props = feat.get("properties", {})
                        prop_details = "\n".join(
                            [
                                f"  - {k}: {v.get('display_value')}"
                                for k, v in props.items()
                            ]
                        )
                        desktop_context = (
                            f"\n\nCURRENT SOLIDWORKS CONTEXT:\n"
                            f"- Selected Item: {feat.get('name', 'Unknown')}\n"
                            f"- Item Type: {feat.get('type', 'Unknown')}\n"
                            f"- Dimensions:\n{prop_details if prop_details else '  - No dimensions found'}\n"
                        )
                        logger.info(f"Injected rich CAD context: {feat.get('name')}")
        except Exception as e:
            logger.warning(f"Failed to fetch desktop context: {e}")

    # Augment with RAG if available
    try:
        from core.memory.rag_engine import RAGEngine

        rag = RAGEngine()
        context = rag.retrieve(last_message, top_k=3)
        if context:
            system_prompt += f"\n\nRelevant Context:\n{context}"
    except Exception:
        pass

    if desktop_context:
        system_prompt += desktop_context

    # Generate response
    try:
        from core.llm import llm

        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = llm.generate(
            messages=messages, system=system_prompt, agent_type=agent_type.value
        )

        # Handle Actions in response
        if "[ACTION:" in response:
            import re

            match = re.search(r"\[ACTION:\s*([\w\.]+)\((.*)\)\]", response)
            if match:
                action_name = match.group(1)
                args_str = match.group(2)
                logger.info(f"Detected ACTION: {action_name}({args_str})")

                # Execute action via desktop bridge
                if action_name == "com.solidworks.modify_selection_property":
                    # Simple parse for (property_name='...', new_value=...)
                    p_name = re.search(r"property_name=['\"](.*?)['\"]", args_str)
                    p_val = re.search(r"new_value=(.*?)(?:,|$|\s)", args_str)
                    if p_name and p_val:
                        endpoint = "/com/solidworks/modify_selection_property"
                        payload = {
                            "property_name": p_name.group(1),
                            "new_value": float(p_val.group(1)),
                        }
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            action_resp = await client.post(
                                f"{DESKTOP_SERVER_URL}{endpoint}", json=payload
                            )
                            logger.info(f"Action executed: {action_resp.status_code}")
                            response += f"\n\n[System: Action {action_name} executed with status {action_resp.status_code}]"

        return {"response": response, "agent": agent_type.value}
    except Exception as e:
        logger.error(f"Chat generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/desktop/command")
async def desktop_command(cmd: DesktopCommand, api_key: str = Depends(get_api_key)):
    """Bridge to the local desktop server."""
    url = f"{DESKTOP_SERVER_URL}{cmd.endpoint}"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if cmd.method.upper() == "GET":
                resp = await client.get(url)
            else:
                resp = await client.post(url, json=cmd.payload or {})

            return {
                "status": resp.status_code,
                "data": (
                    resp.json()
                    if "application/json" in resp.headers.get("content-type", "")
                    else resp.text
                ),
            }
    except Exception as e:
        logger.error(f"Desktop command bridge failure: {e}")
        raise HTTPException(
            status_code=503, detail=f"Desktop communication failure: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
