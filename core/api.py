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
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.security import APIKeyHeader

from core.trading_journal import router as trading_journal_router
from core.validation_history import router as validation_history_router

# Initialize logging
from core.logging_config import setup_logging

setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

logger.info("Vulcan Orchestrator starting up...")


# Lazy imports for heavy modules
def get_llm_client():
    from core.llm import LLMClient

    return LLMClient()


def get_rag_engine():
    from core.memory.rag_engine import RAGEngine

    return RAGEngine()


app = FastAPI(
    title="Vulcan Orchestrator",
    description="Cloud-hosted AI orchestrator for Project Vulcan",
    version="1.0.0",
)

# Rate limiting
RATE_LIMIT_DURATION = 60  # seconds
RATE_LIMIT_REQUESTS = 100  # requests per duration
rate_limiter = defaultdict(lambda: [])


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    request_times = rate_limiter[client_ip]

    # Remove old timestamps
    while request_times and request_times[0] < time.time() - RATE_LIMIT_DURATION:
        request_times.pop(0)

    if len(request_times) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    request_times.append(time.time())
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


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
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )


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
    "trading": """You are a trading analysis agent for Project Vulcan.
You specialize in ICT, BTMM, and Stacey Burke trading methodologies.
Analyze setups, provide bias, and help with trade journaling.
When the user wants to interact with TradingView, use desktop commands.""",
    "cad": """You are a CAD automation agent for Project Vulcan.
You help create 3D models in SolidWorks and Inventor via COM automation.
Break down part creation into steps: sketch, extrude, pattern, etc.
When ready to execute, use desktop commands to control the CAD software.""",
    "general": """You are the general assistant for Project Vulcan.
You help with life management, calendar, notes, and general queries.
Route specialized tasks to trading or CAD agents when appropriate.""",
}


def detect_agent(message: str) -> str:
    """Detect which agent should handle the request based on keywords."""
    message_lower = message.lower()

    trading_keywords = [
        "trade",
        "trading",
        "forex",
        "gbp",
        "usd",
        "eur",
        "setup",
        "bias",
        "ict",
        "btmm",
        "order block",
        "fvg",
        "liquidity",
    ]
    cad_keywords = [
        "cad",
        "solidworks",
        "inventor",
        "part",
        "sketch",
        "extrude",
        "flange",
        "model",
        "3d",
        "drawing",
        "assembly",
    ]

    if any(kw in message_lower for kw in trading_keywords):
        return "trading"
    elif any(kw in message_lower for kw in cad_keywords):
        return "cad"
    return "general"


@app.get("/health")
async def health():
    """Health check endpoint."""
    desktop_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DESKTOP_SERVER_URL}/health")
            if resp.status_code == 200:
                desktop_status = "connected"
            else:
                desktop_status = "error"
    except Exception:
        desktop_status = "unreachable"

    return {
        "status": "healthy",
        "desktop_server": desktop_status,
        "desktop_url": DESKTOP_SERVER_URL,
    }


@app.post("/chat")
async def chat(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """Process a chat message and return AI response."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = request.messages[-1].content
    agent_type = request.agent or detect_agent(last_message)
    system_prompt = AGENT_PROMPTS.get(agent_type, AGENT_PROMPTS["general"])

    # Augment with RAG context
    try:
        rag = get_rag_engine()
        context = rag.retrieve(last_message, top_k=3)
        if context:
            system_prompt += f"\n\nRelevant context from memory:\n{context}"
    except Exception:
        pass  # RAG not available, continue without it

    # Generate response
    try:
        llm = get_llm_client()
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = llm.generate(messages=messages, system=system_prompt)
        return {"response": response, "agent": agent_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/desktop/command")
async def desktop_command(cmd: DesktopCommand, api_key: str = Depends(get_api_key)):
    """Proxy a command to the local desktop server via Tailscale."""
    url = f"{DESKTOP_SERVER_URL}{cmd.endpoint}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if cmd.method.upper() == "GET":
                resp = await client.get(url)
            else:
                resp = await client.post(url, json=cmd.payload or {})

            return {
                "status": resp.status_code,
                "data": (
                    resp.json()
                    if resp.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else resp.text
                ),
            }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Desktop server timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to desktop server")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/desktop/health")
async def desktop_health(api_key: str = Depends(get_api_key)):
    """Check desktop server connectivity."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DESKTOP_SERVER_URL}/health")
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Desktop unreachable: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
