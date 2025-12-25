"""
Project Vulcan - Desktop Control Server
FastAPI server for physical PC control via mouse, keyboard, screen,
and window management.

Security features:
- Kill switch: Move mouse to corner to abort
- Action logging: Every action logged with timestamp
- App whitelist: Only approved applications can be controlled
- Runs on Tailscale IP only (no public exposure)
"""

import os
import logging
import socket
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import yaml
import pyautogui
import sys
from pathlib import Path

# Windows COM imports for CAD status checking
try:
    import win32com.client
    import pythoncom

    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False

sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
from core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Import controllers
from controllers import (
    mouse_router,
    keyboard_router,
    screen_router,
    window_router,
    tradingview_router,
    TRADINGVIEW_AVAILABLE,
    browser_router,
    BROWSER_AVAILABLE,
    j2_tracker_router,
    J2_AVAILABLE,
    memory_router,
    MEMORY_AVAILABLE,
    cad_validation_router,
    CAD_VALIDATION_AVAILABLE,
    recorder_router,
    verifier_router,
    events_router,
    EVENTS_AVAILABLE,
)

# Import CAD COM adapters (optional - only if CAD software is installed)
try:
    from com import (
        solidworks_router,
        solidworks_assembly_router,
        solidworks_drawings_router,
        inventor_router,
        inventor_imates_router,
        inventor_drawings_router,
        solidworks_mate_refs_router,
        assembly_analyzer_router,
        feature_reader_router,
        inventor_feature_reader_router,
        assembly_component_analyzer_router,
    )

    CAD_AVAILABLE = True
except ImportError:
    CAD_AVAILABLE = False
    solidworks_router = None
    solidworks_assembly_router = None
    solidworks_drawings_router = None
    inventor_router = None
    inventor_imates_router = None
    inventor_drawings_router = None
    solidworks_mate_refs_router = None
    assembly_analyzer_router = None
    feature_reader_router = None
    inventor_feature_reader_router = None
    assembly_component_analyzer_router = None
    logger.warning("CAD COM adapters not available")

# Global state
KILL_SWITCH_ACTIVE = False
ACTION_LOG = []
COMMAND_QUEUE: asyncio.Queue = asyncio.Queue()
QUEUE_WORKER_TASK = None


class CommandRequest(BaseModel):
    """Command request model."""

    type: str  # e.g., 'mouse', 'keyboard', 'cad'
    action: str  # e.g., 'move', 'click', 'extrude'
    params: Dict[str, Any] = {}
    priority: int = 1  # 1=Normal, 0=High


async def process_command_queue():
    """Background worker to process commands sequentially."""
    logger.info("Queue Worker Started")
    # Store port locally to avoid relying on global port during startup
    port = int(os.environ.get("PORT", 8000))
    # Wait for server to be ready before processing queue
    await asyncio.sleep(2)

    async with httpx.AsyncClient(
        base_url=f"http://127.0.0.1:{port}", timeout=60.0
    ) as client:
        while True:
            try:
                # Get a "unit of work"
                command: CommandRequest = await COMMAND_QUEUE.get()

                # Check kill switch before processing
                if KILL_SWITCH_ACTIVE:
                    logger.warning(
                        f"Skipping command {command.type}/{command.action} due to Kill Switch"
                    )
                    COMMAND_QUEUE.task_done()
                    continue

                logger.info(f"Processing command: {command.type}/{command.action}")

                # Map command types to router prefixes
                endpoint = f"/{command.type}/{command.action}"

                # Execute command via local API call
                try:
                    resp = await client.post(endpoint, json=command.params)
                    result = (
                        resp.json() if resp.status_code < 400 else {"error": resp.text}
                    )
                    logger.info(
                        f"Command {command.type}/{command.action} result: {resp.status_code}"
                    )
                except Exception as e:
                    logger.error(f"Failed to execute command locally: {e}")
                    result = {"error": str(e)}

                # Log completion
                ACTION_LOG.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "type": "queue_execution",
                        "command": command.dict(),
                        "result": result,
                    }
                )

                # Notify queue that content is processed
                COMMAND_QUEUE.task_done()

            except asyncio.CancelledError:
                logger.info("Queue Worker Cancelled")
                break
            except Exception as e:
                logger.error(f"Error in queue worker loop: {e}")
                # Don't call task_done() here if we didn't successfully get a command
                await asyncio.sleep(1)


def get_tailscale_ip() -> str | None:
    """Get the Tailscale IP address if available."""
    try:
        # Tailscale IPs are in the 100.x.x.x range
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip.startswith("100."):
                return ip
    except Exception:
        pass
    return None


def load_config() -> dict:
    """Load configuration from apps.yaml."""
    config_path = os.path.join(os.path.dirname(__file__), "config", "apps.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def check_kill_switch():
    """Check if mouse is in corner (kill switch)."""
    global KILL_SWITCH_ACTIVE
    pos = pyautogui.position()
    screen_width, screen_height = pyautogui.size()

    # Kill switch: mouse in top-left corner (within 10 pixels)
    if pos.x <= 10 and pos.y <= 10:
        KILL_SWITCH_ACTIVE = True
        logger.warning("KILL SWITCH ACTIVATED - Mouse in corner")
        return True
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("=" * 50)
    logger.info("Project Vulcan Desktop Control Server Starting")
    logger.info("=" * 50)

    tailscale_ip = get_tailscale_ip()
    if tailscale_ip:
        logger.info(f"Tailscale IP detected: {tailscale_ip}")
    else:
        logger.warning("No Tailscale IP detected - running on localhost only")

    config = load_config()
    logger.info(
        f"Loaded config: {len(config.get('whitelisted_apps', []))} whitelisted apps"
    )

    # Enable pyautogui failsafe (move to corner to abort)
    pyautogui.FAILSAFE = True
    logger.info("pyautogui failsafe ENABLED (move mouse to corner to abort)")

    # Start Queue Worker
    global QUEUE_WORKER_TASK
    QUEUE_WORKER_TASK = asyncio.create_task(process_command_queue())
    logger.info("Background Queue Worker initialized")

    yield

    # Cleanup
    if QUEUE_WORKER_TASK:
        QUEUE_WORKER_TASK.cancel()
        try:
            await QUEUE_WORKER_TASK
        except asyncio.CancelledError:
            pass

    logger.info("Desktop Control Server shutting down")


# Create FastAPI app
app = FastAPI(
    title="Project Vulcan - Desktop Control Server",
    description="Physical PC control API for mouse, keyboard, screen, and window management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - Allow from Render.com and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_and_check_killswitch(request: Request, call_next):
    """Middleware to log actions and check kill switch."""
    global KILL_SWITCH_ACTIVE

    # Check kill switch before every action
    if check_kill_switch():
        raise HTTPException(
            status_code=503,
            detail="KILL SWITCH ACTIVE - Move mouse away from corner to resume",
        )

    if KILL_SWITCH_ACTIVE:
        # Allow reset via health check
        if request.url.path == "/health":
            pos = pyautogui.position()
            if pos.x > 50 or pos.y > 50:
                KILL_SWITCH_ACTIVE = False
                logger.info("Kill switch DEACTIVATED")
        else:
            raise HTTPException(
                status_code=503,
                detail="KILL SWITCH ACTIVE - Move mouse away from corner and call /health to resume",
            )

    # Log the action
    action = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else "unknown",
    }
    ACTION_LOG.append(action)
    logger.info(f"Action: {request.method} {request.url.path}")

    response = await call_next(request)
    return response


# Include routers
app.include_router(mouse_router)
app.include_router(keyboard_router)
app.include_router(screen_router)
app.include_router(window_router)

# Include CAD routers if available
if CAD_AVAILABLE:
    if solidworks_router:
        app.include_router(solidworks_router)
    if solidworks_assembly_router:
        app.include_router(solidworks_assembly_router)
    if solidworks_drawings_router:
        app.include_router(solidworks_drawings_router)
    if inventor_router:
        app.include_router(inventor_router)
    if inventor_imates_router:
        app.include_router(inventor_imates_router)
    if inventor_drawings_router:
        app.include_router(inventor_drawings_router)
    if solidworks_mate_refs_router:
        app.include_router(solidworks_mate_refs_router)
    if assembly_analyzer_router:
        app.include_router(assembly_analyzer_router)
        logger.info("Assembly analyzer loaded")
    if feature_reader_router:
        app.include_router(feature_reader_router)
        logger.info("Feature reader loaded")
    if inventor_feature_reader_router:
        app.include_router(inventor_feature_reader_router)
        logger.info("Inventor feature reader loaded")
    if assembly_component_analyzer_router:
        app.include_router(assembly_component_analyzer_router)
        logger.info("Assembly component analyzer loaded")
    logger.info("CAD COM adapters loaded")

# Include Events router if available
if EVENTS_AVAILABLE:
    app.include_router(events_router)
    logger.info("Events controller loaded")

# Include memory router if available
if MEMORY_AVAILABLE:
    app.include_router(memory_router)
    logger.info("Memory/RAG module loaded")

# Include TradingView router if available
if TRADINGVIEW_AVAILABLE:
    app.include_router(tradingview_router)
    logger.info("TradingView browser controller loaded")

# Include browser and J2 Tracker routers if available
if BROWSER_AVAILABLE:
    app.include_router(browser_router)
    logger.info("Browser automation controller loaded")

if J2_AVAILABLE:
    app.include_router(j2_tracker_router)
    logger.info("J2 Tracker controller loaded")

# Include CAD validation router if available
if CAD_VALIDATION_AVAILABLE:
    app.include_router(cad_validation_router)
    logger.info("CAD validation controller loaded")

# Include recorder and verifier routers
app.include_router(recorder_router)
app.include_router(verifier_router)
logger.info("Recorder and Verifier routers loaded")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Project Vulcan Desktop Control Server",
        "version": "1.0.0",
        "status": "running",
        "kill_switch": KILL_SWITCH_ACTIVE,
    }


def check_cad_status() -> dict:
    """Check CAD application connection status."""
    cad_status = {
        "solidworks": {"connected": False, "version": ""},
        "inventor": {"connected": False, "version": ""},
    }

    if not COM_AVAILABLE:
        return cad_status

    # Check SolidWorks
    try:
        pythoncom.CoInitialize()
        sw = win32com.client.GetActiveObject("SldWorks.Application")
        if sw:
            cad_status["solidworks"]["connected"] = True
            try:
                cad_status["solidworks"]["version"] = str(sw.RevisionNumber)[:4]
            except:
                cad_status["solidworks"]["version"] = "Unknown"
    except:
        pass

    # Check Inventor
    try:
        inv = win32com.client.GetActiveObject("Inventor.Application")
        if inv:
            cad_status["inventor"]["connected"] = True
            try:
                cad_status["inventor"]["version"] = inv.SoftwareVersion.DisplayVersion
            except:
                cad_status["inventor"]["version"] = "Unknown"
    except:
        pass

    try:
        pythoncom.CoUninitialize()
    except:
        pass

    return cad_status


@app.get("/health")
async def health():
    """Health check endpoint with CAD status."""
    tailscale_ip = get_tailscale_ip()
    cad_status = check_cad_status()

    return {
        "status": "ok" if not KILL_SWITCH_ACTIVE else "kill_switch_active",
        "tailscale_ip": tailscale_ip,
        "timestamp": datetime.now().isoformat(),
        "actions_logged": len(ACTION_LOG),
        "solidworks": cad_status["solidworks"],
        "inventor": cad_status["inventor"],
        "queue_depth": COMMAND_QUEUE.qsize(),
    }


@app.post("/kill")
async def kill():
    """Emergency stop - activate kill switch."""
    global KILL_SWITCH_ACTIVE
    KILL_SWITCH_ACTIVE = True
    logger.warning("KILL SWITCH MANUALLY ACTIVATED via /kill endpoint")
    return {"status": "kill_switch_activated"}


@app.post("/resume")
async def resume():
    """Resume after kill switch (if mouse is away from corner)."""
    global KILL_SWITCH_ACTIVE
    pos = pyautogui.position()
    if pos.x > 50 or pos.y > 50:
        KILL_SWITCH_ACTIVE = False
        logger.info("Kill switch DEACTIVATED via /resume endpoint")
        return {"status": "resumed"}
    else:
        return {"status": "move_mouse_away_from_corner_first"}


@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent action logs."""
    return {"logs": ACTION_LOG[-limit:]}


@app.post("/queue/add")
async def add_to_queue(command: CommandRequest):
    """Add a command to the execution queue."""
    if KILL_SWITCH_ACTIVE:
        raise HTTPException(status_code=503, detail="Kill switch active")

    await COMMAND_QUEUE.put(command)
    return {"status": "queued", "position": COMMAND_QUEUE.qsize(), "command": command}


@app.get("/queue/status")
async def get_queue_status():
    """Get current queue status."""
    return {
        "size": COMMAND_QUEUE.qsize(),
        "worker_active": QUEUE_WORKER_TASK is not None and not QUEUE_WORKER_TASK.done(),
    }


if __name__ == "__main__":
    import uvicorn

    # Get host - prefer Tailscale IP, fallback to localhost
    tailscale_ip = get_tailscale_ip()
    host = tailscale_ip or "127.0.0.1"
    port = int(os.environ.get("PORT", 8000))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run("server:app", host=host, port=port, reload=False, log_level="info")
