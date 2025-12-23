"""
Cloud Orchestrator API
FastAPI application for Render deployment.
Routes requests to appropriate agents and proxies desktop commands via Tailscale.
"""

import os
import httpx
import time
import logging
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

# Initialize logging
from core.logging_config import setup_logging

setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
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

DESKTOP_SERVER_URL = os.getenv("DESKTOP_SERVER_URL", "http://localhost:8765")
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=401, detail="Invalid API Key")


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
Break down design into sketch, extrude, pattern. Verify alignment (±1/16").""",
    "sketch": """You are the Sketch Agent. Vision-to-CAD specialist.
Interpret drawings/photos into 3D intent and generation parameters.""",
    "work": """You are the Work Agent. Manage J2 Tracker, Outlook, and Teams.
Generate status reports and track project deadlines via Microsoft API.""",
    "general": """General Vulcan Orchestrator. Route to Trading, CAD, Sketch, or Work.""",
}


@app.on_event("startup")
async def startup_event():
    """Register agents and initialize resources."""
    orchestrator = get_orchestrator()
    # In a full deployment, we would instantiate and register actual agent classes here.
    # For now, we use the OrchestratorAdapter's detection and routing logic.
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

    # Augment with RAG if available
    try:
        from core.memory.rag_engine import RAGEngine

        rag = RAGEngine()
        context = rag.retrieve(last_message, top_k=3)
        if context:
            system_prompt += f"\n\nRelevant Context:\n{context}"
    except Exception:
        pass

    # Generate response
    try:
        from core.llm import llm

        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = llm.generate(
            messages=messages, system=system_prompt, agent_type=agent_type.value
        )
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
