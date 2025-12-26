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
from typing import Dict, Any, Optional, List

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
    cad_vision_router,
    CAD_VISION_AVAILABLE,
    recorder_router,
    verifier_router,
    events_router,
    EVENTS_AVAILABLE,
)

# Import Phase 24 components
try:
    from watchers import get_watcher
    from extractors import PropertiesExtractor, HolePatternExtractor
    from analyzers import (
        BendRadiusAnalyzer,
        InterferenceAnalyzer,
        WeldAnalyzer,
        NozzleAnalyzer,
        ASMECalculator,
        MatesAnalyzer,
        StandardsChecker,
        ThermalAnalyzer,
        ReportGenerator,
        DrawingAnalyzer,
        CostEstimator,
        ComponentAnalyzer,
        StructuralAnalyzer,
    )

    PHASE24_AVAILABLE = True
except ImportError:
    PHASE24_AVAILABLE = False
    logger.warning("Phase 24 components not available")

# Import CAD COM adapters (optional - only if CAD software is installed)
try:
    from com import (
        solidworks_router,
        solidworks_assembly_router,
        solidworks_drawings_router,
        solidworks_batch_router,
        SOLIDWORKS_BATCH_AVAILABLE,
        solidworks_advanced_router,
        SOLIDWORKS_ADVANCED_AVAILABLE,
        solidworks_simulation_router,
        SOLIDWORKS_SIMULATION_AVAILABLE,
        solidworks_pdm_router,
        SOLIDWORKS_PDM_AVAILABLE,
        inventor_router,
        inventor_imates_router,
        inventor_drawings_router,
        solidworks_mate_refs_router,
        assembly_analyzer_router,
        feature_reader_router,
        inventor_feature_reader_router,
        assembly_component_analyzer_router,
        configuration_router,
        measurement_router,
        properties_router,
        document_exporter_router,
        bom_router,
    )

    CAD_AVAILABLE = True
except ImportError:
    CAD_AVAILABLE = False
    solidworks_router = None
    solidworks_assembly_router = None
    solidworks_drawings_router = None
    solidworks_advanced_router = None
    solidworks_simulation_router = None
    solidworks_pdm_router = None
    inventor_router = None
    inventor_imates_router = None
    inventor_drawings_router = None
    solidworks_mate_refs_router = None
    assembly_analyzer_router = None
    feature_reader_router = None
    inventor_feature_reader_router = None
    assembly_component_analyzer_router = None
    configuration_router = None
    measurement_router = None
    properties_router = None
    document_exporter_router = None
    bom_router = None
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

    # Start SolidWorks Watcher (Phase 24)
    watcher_task = None
    if PHASE24_AVAILABLE:
        try:
            watcher = get_watcher()
            watcher_task = asyncio.create_task(watcher.start())
            logger.info("SolidWorks watcher started (Phase 24)")
        except Exception as e:
            logger.warning(f"Could not start SolidWorks watcher: {e}")

    yield

    # Cleanup watcher
    if watcher_task:
        try:
            get_watcher().stop()
            watcher_task.cancel()
        except Exception:
            pass

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
    if SOLIDWORKS_BATCH_AVAILABLE and solidworks_batch_router:
        app.include_router(solidworks_batch_router)
        logger.info("SolidWorks batch operations loaded")
    if SOLIDWORKS_ADVANCED_AVAILABLE and solidworks_advanced_router:
        app.include_router(solidworks_advanced_router)
        logger.info("SolidWorks advanced features loaded (Routing, Weldments, Sheet Metal, etc.)")
    if SOLIDWORKS_SIMULATION_AVAILABLE and solidworks_simulation_router:
        app.include_router(solidworks_simulation_router)
        logger.info("SolidWorks Simulation API loaded (FEA, Thermal, Frequency)")
    if SOLIDWORKS_PDM_AVAILABLE and solidworks_pdm_router:
        app.include_router(solidworks_pdm_router)
        logger.info("SolidWorks PDM integration loaded (Vault operations)")
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
    if configuration_router:
        app.include_router(configuration_router)
        logger.info("Configuration manager loaded")
    if measurement_router:
        app.include_router(measurement_router)
        logger.info("Measurement tools loaded")
    if properties_router:
        app.include_router(properties_router)
        logger.info("Properties reader loaded")
    if document_exporter_router:
        app.include_router(document_exporter_router)
        logger.info("Document exporter loaded")
    if bom_router:
        app.include_router(bom_router)
        logger.info("BOM manager loaded")
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

# Include CAD vision router if available
if CAD_VISION_AVAILABLE:
    app.include_router(cad_vision_router)
    logger.info("CAD vision analysis controller loaded")

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

    # Get watcher state if available
    watcher_state = None
    if PHASE24_AVAILABLE:
        try:
            watcher = get_watcher()
            watcher_state = {
                "is_running": watcher.state.is_running,
                "document_name": watcher.state.document_name,
                "document_type": watcher.state.document_type.value,
            }
        except Exception:
            pass

    return {
        "status": "ok" if not KILL_SWITCH_ACTIVE else "kill_switch_active",
        "tailscale_ip": tailscale_ip,
        "timestamp": datetime.now().isoformat(),
        "actions_logged": len(ACTION_LOG),
        "solidworks": cad_status["solidworks"],
        "inventor": cad_status["inventor"],
        "queue_depth": COMMAND_QUEUE.qsize(),
        "watcher": watcher_state,
    }


# =============================================================================
# Phase 24 Endpoints
# =============================================================================


@app.get("/phase24/model-overview")
async def get_model_overview():
    """Get comprehensive model overview (Phase 24.2)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        props_extractor = PropertiesExtractor()
        holes_extractor = HolePatternExtractor()
        bend_analyzer = BendRadiusAnalyzer()

        return {
            "properties": props_extractor.get_all_properties(),
            "hole_analysis": holes_extractor.to_dict(),
            "bend_analysis": bend_analyzer.to_dict(),
        }
    except Exception as e:
        logger.error(f"Model overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/properties")
async def get_properties():
    """Get all properties from active document (Phase 24.3)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        extractor = PropertiesExtractor()
        return extractor.get_all_properties()
    except Exception as e:
        logger.error(f"Properties extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/hole-analysis")
async def get_hole_analysis():
    """Analyze hole patterns (Phase 24.7)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        extractor = HolePatternExtractor()
        return extractor.to_dict()
    except Exception as e:
        logger.error(f"Hole analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/bend-analysis")
async def get_bend_analysis():
    """Analyze sheet metal bends (Phase 24.6)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = BendRadiusAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Bend analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/watcher-state")
async def get_watcher_state():
    """Get current SolidWorks watcher state (Phase 24.1)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        watcher = get_watcher()
        state = watcher.state
        return {
            "is_running": state.is_running,
            "process_id": state.process_id,
            "document_path": state.document_path,
            "document_name": state.document_name,
            "document_type": state.document_type.value,
            "last_change": state.last_change,
        }
    except Exception as e:
        logger.error(f"Watcher state error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/interference-check")
async def get_interference_check():
    """Run interference detection (Phase 24.10)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = InterferenceAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Interference check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/weld-analysis")
async def get_weld_analysis():
    """Analyze welds in drawing (Phase 24.17)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = WeldAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Weld analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/nozzle-schedule")
async def get_nozzle_schedule():
    """Get nozzle schedule (Phase 24.16)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = NozzleAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Nozzle analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ASMECalcRequest(BaseModel):
    """Request model for ASME calculations."""
    material: str = "SA-516-70"
    design_pressure_psi: float = 150.0
    shell_inside_radius_in: Optional[float] = None
    head_inside_diameter_in: Optional[float] = None
    tubesheet_diameter_in: Optional[float] = None
    joint_efficiency: float = 0.85
    corrosion_allowance_in: float = 0.0625
    ligament_efficiency: float = 0.5
    head_type: str = "2:1_ellipsoidal"


@app.post("/phase24/asme-calculations")
async def run_asme_calculations(request: ASMECalcRequest):
    """Run ASME VIII Div 1 calculations (Phase 24.13)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        calculator = ASMECalculator()
        return calculator.to_dict(request.dict())
    except Exception as e:
        logger.error(f"ASME calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/full-analysis")
async def get_full_analysis():
    """Get comprehensive Phase 24 analysis of active model."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        results = {
            "properties": PropertiesExtractor().get_all_properties(),
            "hole_analysis": HolePatternExtractor().to_dict(),
            "bend_analysis": BendRadiusAnalyzer().to_dict(),
            "interference_check": InterferenceAnalyzer().to_dict(),
            "nozzle_schedule": NozzleAnalyzer().to_dict(),
            "mates_analysis": MatesAnalyzer().to_dict(),
        }
        return results
    except Exception as e:
        logger.error(f"Full analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/mates-analysis")
async def get_mates_analysis():
    """Analyze assembly mates (Phase 24.9)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = MatesAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Mates analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/component-analysis")
async def get_component_analysis():
    """Comprehensive component analysis (Phase 24.8)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = ComponentAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Component analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/structural-analysis")
async def get_structural_analysis():
    """ACHE Structural component analysis (Phase 24.22-24.33)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = StructuralAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Structural analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class StandardsCheckRequest(BaseModel):
    """Request model for standards check."""
    tube_support_spacing_m: Optional[float] = None
    bundle_lateral_movement_mm: Optional[float] = None
    design_pressure_psi: Optional[float] = None
    header_type: Optional[str] = None
    plug_hardness_hb: Optional[int] = None
    mawp_psi: Optional[float] = None
    joint_efficiency: Optional[float] = None
    tema_class: Optional[str] = None
    ligament_factor: Optional[float] = None
    handrail_height_in: Optional[float] = None
    toeboard_height_in: Optional[float] = None


@app.post("/phase24/standards-check")
async def run_standards_check(request: StandardsCheckRequest):
    """Run standards compliance check (Phase 24.24)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        checker = StandardsChecker()
        return checker.to_dict(request.dict())
    except Exception as e:
        logger.error(f"Standards check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ThermalAnalysisRequest(BaseModel):
    """Request model for thermal analysis."""
    tube_material: str = "carbon_steel"
    tube_length_in: float = 240.0
    shell_material: str = "carbon_steel"
    shell_length_in: float = 240.0
    design_temp_f: float = 300.0
    ambient_temp_f: float = 70.0
    material_pnum: str = "P-1"
    max_thickness_in: float = 1.0


@app.post("/phase24/thermal-analysis")
async def run_thermal_analysis(request: ThermalAnalysisRequest):
    """Run thermal expansion analysis (Phase 24.14)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = ThermalAnalyzer()
        return analyzer.to_dict(request.dict())
    except Exception as e:
        logger.error(f"Thermal analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase24/drawing-analysis")
async def get_drawing_analysis():
    """Analyze drawing completeness (Phase 24.18)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        analyzer = DrawingAnalyzer()
        return analyzer.to_dict()
    except Exception as e:
        logger.error(f"Drawing analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CostEstimateRequest(BaseModel):
    """Request model for cost estimate."""
    mass_properties: Optional[Dict[str, Any]] = None
    material: str = "SA-516-70"
    weld_weight_lbs: Optional[float] = None
    total_holes: int = 0
    avg_hole_diameter_in: float = 1.0
    plate_thickness_in: float = 1.0
    component_count: int = 10


@app.post("/phase24/cost-estimate")
async def get_cost_estimate(request: CostEstimateRequest):
    """Generate cost estimate (Phase 24.28)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        estimator = CostEstimator()
        return estimator.to_dict(request.dict())
    except Exception as e:
        logger.error(f"Cost estimate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase24/generate-report")
async def generate_report(format: str = "pdf"):
    """Generate PDF/Excel report (Phase 24.26)."""
    if not PHASE24_AVAILABLE:
        raise HTTPException(status_code=501, detail="Phase 24 not available")

    try:
        # Gather all model data
        model_data = {
            "properties": PropertiesExtractor().get_all_properties(),
            "hole_analysis": HolePatternExtractor().to_dict(),
            "bend_analysis": BendRadiusAnalyzer().to_dict(),
            "mates_analysis": MatesAnalyzer().to_dict(),
        }

        generator = ReportGenerator()
        return generator.to_dict(model_data, format)
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Phase 25: PDF Drawing Validation Endpoints
# =============================================================================

class PDFValidationRequest(BaseModel):
    """Request model for PDF validation."""
    file_path: str
    standards: list = ["api_661", "asme", "aws_d1_1"]


@app.post("/phase25/validate-pdf")
async def validate_pdf_drawing(request: PDFValidationRequest):
    """
    Validate a PDF engineering drawing against standards.

    Phase 25.1-25.10 Implementation.

    Args:
        request: PDFValidationRequest with file_path and standards list

    Returns:
        Validation results including extraction and all standard checks
    """
    try:
        # Import PDF validation engine
        from extractors.pdf_drawing_extractor import PDFDrawingExtractor

        # Import validators from agents
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.pdf_validation_engine import PDFValidationEngine

        engine = PDFValidationEngine()
        result = engine.validate(request.file_path, request.standards)
        return engine.to_dict(result)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"PDF validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase25/extract-pdf")
async def extract_pdf_data(file_path: str):
    """
    Extract data from a PDF engineering drawing without validation.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted drawing data (title block, BOM, dimensions, etc.)
    """
    try:
        from extractors.pdf_drawing_extractor import PDFDrawingExtractor

        extractor = PDFDrawingExtractor()
        result = extractor.extract(file_path)
        return extractor.to_dict(result)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase25/validation-report")
async def get_validation_report(file_path: str, format: str = "json"):
    """
    Validate a PDF and generate a formatted report.

    Args:
        file_path: Path to the PDF file
        format: Report format (json, text, or summary)

    Returns:
        Validation report in requested format
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.pdf_validation_engine import PDFValidationEngine

        engine = PDFValidationEngine()
        result = engine.validate(file_path)

        if format == "text":
            return {"report": engine.generate_report_summary(result)}
        elif format == "summary":
            return {
                "file": result.file_name,
                "part_number": result.part_number,
                "revision": result.revision,
                "total_checks": result.total_checks,
                "pass_rate": result.pass_rate,
                "critical_issues": result.critical_failures,
                "status": "PASS" if result.critical_failures == 0 else "FAIL",
            }
        else:
            return engine.to_dict(result)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Validation report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Phase 25 Drawing Checker Endpoints
# ============================================================================

@app.post("/phase25/check-holes")
async def check_holes(request: dict):
    """
    Validate hole patterns against AISC requirements.

    Request body:
        holes: List of {diameter, x, y, edge_distance_x, edge_distance_y}
        material_thickness: Optional plate thickness
        edge_type: "sheared" or "rolled"

    Returns:
        AISC hole validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.aisc_hole_validator import AISCHoleValidator, HoleData

        validator = AISCHoleValidator()

        holes = [
            HoleData(
                diameter=h.get("diameter", 0),
                x=h.get("x", 0),
                y=h.get("y", 0),
                edge_distance_x=h.get("edge_distance_x"),
                edge_distance_y=h.get("edge_distance_y"),
            )
            for h in request.get("holes", [])
        ]

        result = validator.validate_holes(
            holes=holes,
            material_thickness=request.get("material_thickness"),
            edge_type=request.get("edge_type", "sheared")
        )

        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Hole check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-structural")
async def check_structural(request: dict):
    """
    Validate structural connection capacity.

    Request body:
        check_type: "bolt_shear", "bearing", "weld", "net_section"
        ... parameters specific to check type

    Returns:
        Structural capacity validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.structural_capacity_validator import (
            StructuralCapacityValidator, BoltData, WeldData
        )

        validator = StructuralCapacityValidator()
        check_type = request.get("check_type", "bolt_shear")

        if check_type == "bolt_shear":
            bolt = BoltData(
                diameter=request.get("bolt_diameter", 0.75),
                grade=request.get("bolt_grade", "A325"),
                threads_excluded=request.get("threads_excluded", False),
                num_bolts=request.get("num_bolts", 1),
                num_shear_planes=request.get("num_shear_planes", 1),
            )
            result = validator.check_bolt_shear(
                bolt=bolt,
                applied_load_kips=request.get("applied_load_kips")
            )

        elif check_type == "bearing":
            bolt = BoltData(
                diameter=request.get("bolt_diameter", 0.75),
                num_bolts=request.get("num_bolts", 1),
            )
            result = validator.check_bearing(
                bolt=bolt,
                material_thickness=request.get("material_thickness", 0.5),
                material_grade=request.get("material_grade", "A572-50"),
                applied_load_kips=request.get("applied_load_kips")
            )

        elif check_type == "weld":
            weld = WeldData(
                weld_type=request.get("weld_type", "fillet"),
                leg_size=request.get("leg_size", 0.25),
                length=request.get("weld_length", 1.0),
            )
            result = validator.check_fillet_weld(
                weld=weld,
                base_metal_thickness=request.get("base_metal_thickness", 0.5),
                applied_load_kips=request.get("applied_load_kips")
            )

        elif check_type == "net_section":
            result = validator.check_net_section(
                gross_width=request.get("gross_width", 6.0),
                thickness=request.get("thickness", 0.5),
                hole_diameters=request.get("hole_diameters", []),
                material_grade=request.get("material_grade", "A572-50"),
                applied_load_kips=request.get("applied_load_kips")
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown check_type: {check_type}")

        return validator.to_dict(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Structural check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-shaft")
async def check_shaft(request: dict):
    """
    Validate shaft/machining requirements.

    Request body:
        check_type: "shaft", "keyway", "retaining_ring", "chamfer"
        ... parameters specific to check type

    Returns:
        Shaft validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.shaft_validator import (
            ShaftValidator, ShaftData, KeywayData
        )

        validator = ShaftValidator()
        check_type = request.get("check_type", "shaft")

        if check_type == "shaft":
            shaft = ShaftData(
                diameter=request.get("diameter", 1.0),
                length=request.get("length"),
                tolerance_plus=request.get("tolerance_plus"),
                tolerance_minus=request.get("tolerance_minus"),
                surface_finish_ra=request.get("surface_finish_ra"),
                runout_tir=request.get("runout_tir"),
                concentricity=request.get("concentricity"),
            )
            result = validator.validate_shaft(
                shaft=shaft,
                feature_type=request.get("feature_type", "general")
            )

        elif check_type == "keyway":
            keyway = KeywayData(
                width=request.get("keyway_width", 0.25),
                depth=request.get("keyway_depth", 0.125),
                length=request.get("keyway_length"),
                angular_location=request.get("angular_location"),
            )
            result = validator.validate_keyway(
                keyway=keyway,
                shaft_diameter=request.get("shaft_diameter", 1.0)
            )

        elif check_type == "retaining_ring":
            result = validator.validate_retaining_ring_groove(
                shaft_diameter=request.get("shaft_diameter", 1.0),
                groove_width=request.get("groove_width"),
                groove_depth=request.get("groove_depth"),
            )

        elif check_type == "chamfer":
            result = validator.check_chamfers(
                has_chamfer=request.get("has_chamfer", False),
                chamfer_size=request.get("chamfer_size"),
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown check_type: {check_type}")

        return validator.to_dict(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shaft check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-handling")
async def check_handling(request: dict):
    """
    Validate handling and lifting requirements.

    Request body:
        total_weight_lbs: Assembly weight
        length_in, width_in, height_in: Dimensions
        has_lifting_lugs, num_lifting_lugs, lug_capacity_lbs
        cg_marked, cg_location
        has_rigging_diagram

    Returns:
        Handling validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.handling_validator import HandlingValidator, HandlingData

        validator = HandlingValidator()

        handling = HandlingData(
            total_weight_lbs=request.get("total_weight_lbs", 0),
            length_in=request.get("length_in"),
            width_in=request.get("width_in"),
            height_in=request.get("height_in"),
            has_lifting_lugs=request.get("has_lifting_lugs", False),
            num_lifting_lugs=request.get("num_lifting_lugs", 0),
            lug_capacity_lbs=request.get("lug_capacity_lbs"),
            cg_marked=request.get("cg_marked", False),
            cg_location=request.get("cg_location"),
            has_rigging_diagram=request.get("has_rigging_diagram", False),
        )

        result = validator.validate(handling)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Handling check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-weld")
async def check_weld(request: dict):
    """
    Validate welding against AWS D1.1 requirements.

    Request body:
        welds: List of weld data (procedure, size, type, etc.)
        drawing_type: "M", "S", or "CS"

    Returns:
        AWS D1.1 validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.aws_d1_1_validator import AWSD11Validator

        validator = AWSD11Validator()

        # Create a mock extraction result for standalone use
        class MockExtraction:
            def __init__(self, data):
                self.weld_symbols = []
                self.general_notes = []
                self.bom_items = []

                # Convert weld data to weld symbols
                from dataclasses import dataclass
                @dataclass
                class WeldSymbol:
                    weld_type: str = ""
                    size: float = 0.0
                    length: float = 0.0
                    procedure: str = ""
                    note: str = ""

                for w in data.get("welds", []):
                    self.weld_symbols.append(WeldSymbol(
                        weld_type=w.get("weld_type", "fillet"),
                        size=w.get("size", 0.25),
                        length=w.get("length", 1.0),
                        procedure=w.get("procedure", ""),
                        note=w.get("note", ""),
                    ))

        extraction = MockExtraction(request)
        result = validator.validate(extraction)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Weld check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-bom")
async def check_bom(request: dict):
    """
    Validate Bill of Materials.

    Request body:
        items: List of BOM items {item_number, part_number, description, material, quantity}

    Returns:
        BOM validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.bom_validator import BOMValidator

        validator = BOMValidator()

        # Create mock extraction for standalone use
        class MockExtraction:
            def __init__(self, data):
                self.bom_items = []

                from dataclasses import dataclass
                @dataclass
                class BOMItem:
                    item_number: str = ""
                    part_number: str = ""
                    description: str = ""
                    material: str = ""
                    quantity: int = 1

                for item in data.get("items", []):
                    self.bom_items.append(BOMItem(
                        item_number=str(item.get("item_number", "")),
                        part_number=item.get("part_number", ""),
                        description=item.get("description", ""),
                        material=item.get("material", ""),
                        quantity=item.get("quantity", 1),
                    ))

        extraction = MockExtraction(request)
        result = validator.validate(extraction)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"BOM check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-dimensions")
async def check_dimensions(request: dict):
    """
    Validate dimensions (tolerances, conversions).

    Request body:
        dimensions: List of {value_imperial, value_metric, is_dual_unit, description}

    Returns:
        Dimension validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.dimension_validator import DimensionValidator

        validator = DimensionValidator()

        # Create mock extraction
        class MockExtraction:
            def __init__(self, data):
                self.dimensions = []
                self.design_data = None
                self.drawing_type = None

                from dataclasses import dataclass
                @dataclass
                class Dimension:
                    value_imperial: float = None
                    value_metric: float = None
                    is_dual_unit: bool = False
                    description: str = ""
                    tolerance_plus: float = None
                    tolerance_minus: float = None
                    tolerance_bilateral: float = None

                for d in data.get("dimensions", []):
                    self.dimensions.append(Dimension(
                        value_imperial=d.get("value_imperial"),
                        value_metric=d.get("value_metric"),
                        is_dual_unit=d.get("is_dual_unit", False),
                        description=d.get("description", ""),
                        tolerance_plus=d.get("tolerance_plus"),
                        tolerance_minus=d.get("tolerance_minus"),
                    ))

        extraction = MockExtraction(request)
        result = validator.validate(extraction)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Dimension check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-osha")
async def check_osha(request: dict):
    """
    Validate OSHA structural safety requirements.

    Request body:
        handrail_height: Height in inches
        has_midrail: Boolean
        has_toeboard: Boolean
        ladder_rung_spacing: Spacing in inches
        platform_width: Width in inches

    Returns:
        OSHA validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.osha_validator import OSHAValidator

        validator = OSHAValidator()

        # Create mock extraction
        class MockExtraction:
            def __init__(self, data):
                self.dimensions = []
                self.bom_items = []
                self.general_notes = []
                self.weld_symbols = []

                from dataclasses import dataclass
                from enum import Enum

                class DrawingType(Enum):
                    HEADER = "M"
                    STRUCTURE = "S"
                    SHIPPING = "CS"

                self.drawing_type = DrawingType.STRUCTURE

                @dataclass
                class Dimension:
                    value_imperial: float = None
                    description: str = ""

                # Add handrail dimension if provided
                if data.get("handrail_height"):
                    self.dimensions.append(Dimension(
                        value_imperial=data["handrail_height"],
                        description="TOP RAIL HEIGHT"
                    ))

                if data.get("ladder_rung_spacing"):
                    self.dimensions.append(Dimension(
                        value_imperial=data["ladder_rung_spacing"],
                        description="LADDER RUNG SPACING"
                    ))

                if data.get("platform_width"):
                    self.dimensions.append(Dimension(
                        value_imperial=data["platform_width"],
                        description="PLATFORM WIDTH"
                    ))

        extraction = MockExtraction(request)
        result = validator.validate(extraction)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"OSHA check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-completeness")
async def check_completeness(request: dict):
    """
    Validate drawing completeness.

    Request body:
        title_block: {part_number, revision, title, date, drawn_by, scale, ...}
        has_revision_history: Boolean
        has_general_notes: Boolean
        has_bom: Boolean
        drawing_type: "M", "S", or "CS"

    Returns:
        Completeness validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.drawing_completeness_validator import DrawingCompletenessValidator

        validator = DrawingCompletenessValidator()

        # Create mock extraction
        class MockExtraction:
            def __init__(self, data):
                from dataclasses import dataclass
                from enum import Enum

                class DrawingType(Enum):
                    HEADER = "M"
                    STRUCTURE = "S"
                    SHIPPING = "CS"

                @dataclass
                class TitleBlock:
                    part_number: str = ""
                    revision: str = ""
                    title: str = ""
                    customer: str = ""
                    project_number: str = ""
                    date: str = ""
                    drawn_by: str = ""
                    checked_by: str = ""
                    approved_by: str = ""
                    scale: str = ""

                @dataclass
                class GeneralNote:
                    text: str = ""

                @dataclass
                class RevisionEntry:
                    revision: str = ""
                    date: str = ""
                    description: str = ""

                tb = data.get("title_block", {})
                self.title_block = TitleBlock(
                    part_number=tb.get("part_number", ""),
                    revision=tb.get("revision", ""),
                    title=tb.get("title", ""),
                    customer=tb.get("customer", ""),
                    project_number=tb.get("project_number", ""),
                    date=tb.get("date", ""),
                    drawn_by=tb.get("drawn_by", ""),
                    checked_by=tb.get("checked_by", ""),
                    approved_by=tb.get("approved_by", ""),
                    scale=tb.get("scale", ""),
                )

                dt = data.get("drawing_type", "S")
                self.drawing_type = DrawingType.STRUCTURE if dt == "S" else \
                                   DrawingType.HEADER if dt == "M" else \
                                   DrawingType.SHIPPING

                self.revision_history = []
                if data.get("has_revision_history"):
                    self.revision_history = [RevisionEntry(revision="A", date="2025-01-01")]

                self.general_notes = []
                if data.get("has_general_notes"):
                    self.general_notes = [GeneralNote(text="MATERIAL PER BOM")]

                self.bom_items = []
                self.weld_symbols = []
                self.page_count = data.get("page_count", 1)

        extraction = MockExtraction(request)
        result = validator.validate(extraction)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Completeness check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-api661-full")
async def check_api661_full(request: dict):
    """
    Comprehensive API 661 / ISO 13706 validation (82 checks).

    Covers:
    - Bundle Assembly (22 checks)
    - Header Box Design (18 checks)
    - Plug Requirements (8 checks)
    - Nozzle Requirements (12 checks)
    - Tube-to-Tubesheet Joints (8 checks)
    - Fan System (10 checks)
    - Drive System (4 checks)

    Request body includes all API 661 parameters.
    See API661FullData dataclass for complete list.

    Returns:
        Comprehensive validation result with 82 checks
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.api661_full_scope_validator import (
            API661FullScopeValidator, API661FullData,
            HeaderType, JointType, FinType, DriveType
        )

        validator = API661FullScopeValidator()

        # Parse enums
        header_type = None
        if request.get("header_type"):
            header_type = HeaderType(request["header_type"])

        joint_type = None
        if request.get("joint_type"):
            joint_type = JointType(request["joint_type"])

        fin_type = None
        if request.get("fin_type"):
            fin_type = FinType(request["fin_type"])

        drive_type = None
        if request.get("drive_type"):
            drive_type = DriveType(request["drive_type"])

        data = API661FullData(
            # Bundle Assembly
            tube_support_spacing_m=request.get("tube_support_spacing_m"),
            has_tube_keepers=request.get("has_tube_keepers", False),
            tube_keepers_bolted=request.get("tube_keepers_bolted", False),
            has_air_seals=request.get("has_air_seals", False),
            has_p_strips=request.get("has_p_strips", False),
            lateral_movement_mm=request.get("lateral_movement_mm"),
            lateral_both_directions=request.get("lateral_both_directions", True),
            is_condenser=request.get("is_condenser", False),
            is_single_pass=request.get("is_single_pass", True),
            tube_slope_mm_per_m=request.get("tube_slope_mm_per_m"),
            has_thermal_expansion_provision=request.get("has_thermal_expansion_provision", False),

            # Tube specs
            tube_od_mm=request.get("tube_od_mm"),
            tube_wall_mm=request.get("tube_wall_mm"),
            tube_material=request.get("tube_material", "carbon_steel"),
            fin_type=fin_type,
            operating_temp_c=request.get("operating_temp_c"),
            fin_gap_mm=request.get("fin_gap_mm"),

            # Header Box
            header_type=header_type,
            design_pressure_psi=request.get("design_pressure_psi"),
            is_h2_service=request.get("is_h2_service", False),
            inlet_temp_c=request.get("inlet_temp_c"),
            outlet_temp_c=request.get("outlet_temp_c"),
            has_split_header=request.get("has_split_header", False),
            has_restraint_analysis=request.get("has_restraint_analysis", False),
            has_full_pen_flange_welds=request.get("has_full_pen_flange_welds", False),

            # Gaskets
            through_bolt_dia_mm=request.get("through_bolt_dia_mm"),
            gasket_width_perimeter_mm=request.get("gasket_width_perimeter_mm"),

            # Plugs
            plug_type=request.get("plug_type", "shoulder"),
            plug_head_type=request.get("plug_head_type", "hexagonal"),

            # Nozzles
            nozzle_sizes_dn=request.get("nozzle_sizes_dn", []),
            nozzles_flanged=request.get("nozzles_flanged", True),
            has_threaded_nozzles=request.get("has_threaded_nozzles", False),

            # Joints
            joint_type=joint_type,
            num_grooves=request.get("num_grooves", 2),
            groove_width_mm=request.get("groove_width_mm"),

            # Fan
            fan_diameter_m=request.get("fan_diameter_m"),
            tip_clearance_mm=request.get("tip_clearance_mm"),
            bundle_coverage_pct=request.get("bundle_coverage_pct"),
            dispersion_angle_deg=request.get("dispersion_angle_deg"),
            airflow_reserve_pct=request.get("airflow_reserve_pct"),

            # Drive
            drive_type=drive_type,
            motor_power_kw=request.get("motor_power_kw"),
            motor_bearing_l10_hrs=request.get("motor_bearing_l10_hrs"),
            shaft_bearing_l10_hrs=request.get("shaft_bearing_l10_hrs"),
            belt_service_factor=request.get("belt_service_factor"),
        )

        result = validator.validate(data)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"API 661 full scope check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-gdt")
async def check_gdt(request: dict):
    """
    Validate GD&T per ASME Y14.5-2018.

    All 14 geometric tolerance symbols supported:
    - Form: Flatness, Straightness, Circularity, Cylindricity
    - Orientation: Perpendicularity, Angularity, Parallelism
    - Location: Position, Concentricity, Symmetry
    - Runout: Circular Runout, Total Runout
    - Profile: Profile of Line, Profile of Surface

    Request body:
        tolerance_type: str - Type of tolerance to validate
        tolerance_value: float - Tolerance value in inches
        material_condition: str - "M" (MMC), "L" (LMC), or "S" (RFS)
        primary_datum: str - Primary datum reference
        secondary_datum: str - Secondary datum reference (optional)
        tertiary_datum: str - Tertiary datum reference (optional)

        For Position tolerance:
            feature_type: str - "hole", "pin", "slot", "tab"
            feature_size: float - Nominal feature size
            feature_size_tolerance: float - Size tolerance
            actual_x: float - Actual X position (optional)
            actual_y: float - Actual Y position (optional)
            nominal_x: float - Nominal X position
            nominal_y: float - Nominal Y position

        For Form tolerances:
            surface_length: float - Length of surface
            surface_width: float - Width of surface
            process: str - Manufacturing process
            diameter: float - For circular features

    Returns:
        GD&T validation results including bonus tolerance calculations
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.gdt_validator import (
            GDTValidator, FeatureControlFrame, PositionData,
            ToleranceType, MaterialCondition, FeatureType
        )

        validator = GDTValidator()
        tol_type = request.get("tolerance_type", "position").lower()

        # Map string to enum
        type_map = {
            "flatness": ToleranceType.FLATNESS,
            "straightness": ToleranceType.STRAIGHTNESS,
            "circularity": ToleranceType.CIRCULARITY,
            "cylindricity": ToleranceType.CYLINDRICITY,
            "perpendicularity": ToleranceType.PERPENDICULARITY,
            "angularity": ToleranceType.ANGULARITY,
            "parallelism": ToleranceType.PARALLELISM,
            "position": ToleranceType.POSITION,
            "concentricity": ToleranceType.CONCENTRICITY,
            "symmetry": ToleranceType.SYMMETRY,
            "circular_runout": ToleranceType.CIRCULAR_RUNOUT,
            "total_runout": ToleranceType.TOTAL_RUNOUT,
            "profile_line": ToleranceType.PROFILE_LINE,
            "profile_surface": ToleranceType.PROFILE_SURFACE,
        }

        mc_map = {
            "M": MaterialCondition.MMC,
            "L": MaterialCondition.LMC,
            "S": MaterialCondition.RFS,
            "MMC": MaterialCondition.MMC,
            "LMC": MaterialCondition.LMC,
            "RFS": MaterialCondition.RFS,
        }

        feature_map = {
            "hole": FeatureType.HOLE,
            "pin": FeatureType.PIN,
            "slot": FeatureType.SLOT,
            "tab": FeatureType.TAB,
            "surface": FeatureType.SURFACE,
        }

        tolerance_type = type_map.get(tol_type, ToleranceType.POSITION)
        material_condition = mc_map.get(request.get("material_condition", "S"), MaterialCondition.RFS)

        # Handle different tolerance types
        if tolerance_type == ToleranceType.POSITION:
            # Build FCF for position
            fcf = FeatureControlFrame(
                tolerance_type=ToleranceType.POSITION,
                tolerance_value=request.get("tolerance_value", 0.010),
                material_condition=material_condition,
                primary_datum=request.get("primary_datum"),
                secondary_datum=request.get("secondary_datum"),
                tertiary_datum=request.get("tertiary_datum"),
                feature_type=feature_map.get(request.get("feature_type", "hole"), FeatureType.HOLE),
                feature_size=request.get("feature_size"),
                feature_size_tolerance=request.get("feature_size_tolerance"),
            )

            # Position data if actual measurements provided
            pos_data = None
            if request.get("actual_x") is not None and request.get("actual_y") is not None:
                pos_data = PositionData(
                    nominal_x=request.get("nominal_x", 0.0),
                    nominal_y=request.get("nominal_y", 0.0),
                    actual_x=request.get("actual_x"),
                    actual_y=request.get("actual_y"),
                )

            result = validator.validate_position(fcf, pos_data)

        elif tolerance_type == ToleranceType.FLATNESS:
            result = validator.validate_flatness(
                tolerance=request.get("tolerance_value", 0.005),
                surface_length=request.get("surface_length", 6.0),
                surface_width=request.get("surface_width", 4.0),
                process=request.get("process", "milling"),
            )

        elif tolerance_type == ToleranceType.STRAIGHTNESS:
            result = validator.validate_straightness(
                tolerance=request.get("tolerance_value", 0.005),
                feature_length=request.get("feature_length", 6.0),
                is_axis=request.get("is_axis", False),
                material_condition=material_condition,
            )

        elif tolerance_type == ToleranceType.CIRCULARITY:
            result = validator.validate_circularity(
                tolerance=request.get("tolerance_value", 0.003),
                diameter=request.get("diameter", 1.0),
                process=request.get("process", "turning"),
            )

        elif tolerance_type == ToleranceType.CYLINDRICITY:
            result = validator.validate_cylindricity(
                tolerance=request.get("tolerance_value", 0.005),
                diameter=request.get("diameter", 1.0),
                length=request.get("feature_length", 3.0),
                process=request.get("process", "turning"),
            )

        elif tolerance_type == ToleranceType.PERPENDICULARITY:
            result = validator.validate_perpendicularity(
                tolerance=request.get("tolerance_value", 0.005),
                feature_length=request.get("feature_length", 4.0),
                datum=request.get("primary_datum", "A"),
                material_condition=material_condition,
            )

        elif tolerance_type == ToleranceType.ANGULARITY:
            result = validator.validate_angularity(
                tolerance=request.get("tolerance_value", 0.005),
                specified_angle=request.get("specified_angle", 45.0),
                feature_length=request.get("feature_length", 4.0),
                datum=request.get("primary_datum", "A"),
            )

        elif tolerance_type == ToleranceType.PARALLELISM:
            result = validator.validate_parallelism(
                tolerance=request.get("tolerance_value", 0.005),
                feature_length=request.get("feature_length", 4.0),
                datum=request.get("primary_datum", "A"),
                material_condition=material_condition,
            )

        elif tolerance_type == ToleranceType.CONCENTRICITY:
            result = validator.validate_concentricity(
                tolerance=request.get("tolerance_value", 0.002),
                datum=request.get("primary_datum", "A"),
            )

        elif tolerance_type == ToleranceType.SYMMETRY:
            result = validator.validate_symmetry(
                tolerance=request.get("tolerance_value", 0.005),
                datum=request.get("primary_datum", "A"),
            )

        elif tolerance_type == ToleranceType.CIRCULAR_RUNOUT:
            result = validator.validate_circular_runout(
                tolerance=request.get("tolerance_value", 0.003),
                datum=request.get("primary_datum", "A"),
            )

        elif tolerance_type == ToleranceType.TOTAL_RUNOUT:
            result = validator.validate_total_runout(
                tolerance=request.get("tolerance_value", 0.005),
                datum=request.get("primary_datum", "A"),
            )

        elif tolerance_type == ToleranceType.PROFILE_LINE:
            result = validator.validate_profile_line(
                tolerance=request.get("tolerance_value", 0.010),
                is_bilateral=request.get("is_bilateral", True),
                datum=request.get("primary_datum"),
            )

        elif tolerance_type == ToleranceType.PROFILE_SURFACE:
            result = validator.validate_profile_surface(
                tolerance=request.get("tolerance_value", 0.010),
                is_bilateral=request.get("is_bilateral", True),
                datum=request.get("primary_datum"),
            )
        else:
            # Generic FCF validation
            fcf = FeatureControlFrame(
                tolerance_type=tolerance_type,
                tolerance_value=request.get("tolerance_value", 0.005),
                material_condition=material_condition,
                primary_datum=request.get("primary_datum"),
            )
            result = validator.validate_fcf(fcf)

        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"GD&T check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-api661-bundle")
async def check_api661_bundle(request: dict):
    """
    Validate tube bundle assembly per API 661.

    Request body:
        tube_support_spacing_in: Float (max 72" / 6 ft)
        has_tube_keepers: Boolean
        tube_keepers_bolted: Boolean
        has_air_seals: Boolean
        lateral_movement_both_dir_mm: Float
        is_condenser: Boolean
        tube_slope_mm_per_m: Float
        header_type: "plug", "cover_plate", "bonnet"
        design_pressure_psi: Float
        is_h2_service: Boolean
        plug_type: "shoulder", "hollow"
        nozzle_sizes_dn: List[int]
        has_vent: Boolean
        has_drain: Boolean

    Returns:
        API 661 bundle validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.api661_bundle_validator import API661BundleValidator, BundleData

        validator = API661BundleValidator()

        bundle = BundleData(
            tube_support_spacing_in=request.get("tube_support_spacing_in"),
            has_tube_keepers=request.get("has_tube_keepers", False),
            tube_keepers_bolted=request.get("tube_keepers_bolted", False),
            has_air_seals=request.get("has_air_seals", False),
            has_p_strips=request.get("has_p_strips", False),
            lateral_movement_both_dir_mm=request.get("lateral_movement_both_dir_mm"),
            lateral_movement_one_dir_mm=request.get("lateral_movement_one_dir_mm"),
            is_condenser=request.get("is_condenser", False),
            tube_slope_mm_per_m=request.get("tube_slope_mm_per_m"),
            header_type=request.get("header_type"),
            design_pressure_psi=request.get("design_pressure_psi"),
            is_h2_service=request.get("is_h2_service", False),
            plug_type=request.get("plug_type"),
            plug_head_type=request.get("plug_head_type"),
            nozzle_sizes_dn=request.get("nozzle_sizes_dn", []),
            has_vent=request.get("has_vent", False),
            vent_at_high_point=request.get("vent_at_high_point", False),
            has_drain=request.get("has_drain", False),
            drain_at_low_point=request.get("drain_at_low_point", False),
        )

        result = validator.validate_bundle(bundle)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"API 661 bundle check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-nema-motor")
async def check_nema_motor(request: dict):
    """
    Validate motor frame dimensions per NEMA MG-1.

    Request body:
        frame_size: String (e.g., "286T", "324T")
        horsepower: Float
        shaft_diameter: Float (inches)
        shaft_length: Float (inches)
        mounting_hole_spacing_f: Float (2F dimension)
        mounting_hole_spacing_h: Float (H dimension)
        service_factor: Float

    Returns:
        NEMA motor validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.nema_motor_validator import NEMAMotorValidator, MotorData

        validator = NEMAMotorValidator()

        motor = MotorData(
            frame_size=request.get("frame_size"),
            horsepower=request.get("horsepower"),
            shaft_diameter=request.get("shaft_diameter"),
            shaft_length=request.get("shaft_length"),
            mounting_hole_spacing_f=request.get("mounting_hole_spacing_f"),
            mounting_hole_spacing_h=request.get("mounting_hole_spacing_h"),
            shaft_height_d=request.get("shaft_height_d"),
            service_factor=request.get("service_factor"),
        )

        result = validator.validate_motor(motor)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"NEMA motor check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-sspc-coating")
async def check_sspc_coating(request: dict):
    """
    Validate coating specifications per SSPC standards.

    Request body:
        surface_prep: String (e.g., "SP-6", "SP-10")
        primer_type: String (e.g., "zinc_rich", "epoxy")
        primer_dft_mils: Float
        intermediate_type: String
        intermediate_dft_mils: Float
        topcoat_type: String
        topcoat_dft_mils: Float
        total_dft_mils: Float
        environment: String (e.g., "immersion", "marine", "industrial")

    Returns:
        SSPC coating validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.sspc_coating_validator import SSPCCoatingValidator, CoatingSpec

        validator = SSPCCoatingValidator()

        spec = CoatingSpec(
            surface_prep=request.get("surface_prep"),
            primer_type=request.get("primer_type"),
            primer_dft_mils=request.get("primer_dft_mils"),
            intermediate_type=request.get("intermediate_type"),
            intermediate_dft_mils=request.get("intermediate_dft_mils"),
            topcoat_type=request.get("topcoat_type"),
            topcoat_dft_mils=request.get("topcoat_dft_mils"),
            total_dft_mils=request.get("total_dft_mils"),
            environment=request.get("environment"),
            substrate=request.get("substrate", "carbon_steel"),
        )

        result = validator.validate_coating(spec)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"SSPC coating check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-asme-viii")
async def check_asme_viii(request: dict):
    """
    Validate pressure vessel design per ASME Section VIII Division 1.

    Request body:
        design_pressure_psi: Float
        shell_inside_diameter_in: Float
        shell_wall_thickness_in: Float
        material: String (e.g., "SA-516-70")
        joint_efficiency: Float (0.0-1.0)
        corrosion_allowance_in: Float
        design_temperature_f: Float
        hydro_test_pressure_psi: Float (optional)
        nozzle_diameter_in: Float (optional)
        nozzle_reinforcement_area_sqin: Float (optional)
        flange_rating: String (e.g., "150", "300")
        flange_temp_f: Float (optional)
        mtr_available: Boolean
        material_certs: List of cert types

    Returns:
        ASME VIII validation results with 8 checks
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.asme_viii_validator import ASMEVIIIValidator, VesselData

        validator = ASMEVIIIValidator()

        vessel = VesselData(
            design_pressure_psi=request.get("design_pressure_psi", 150.0),
            inside_diameter_in=request.get("inside_diameter_in") or request.get("shell_inside_diameter_in"),
            wall_thickness_in=request.get("wall_thickness_in") or request.get("shell_wall_thickness_in"),
            material=request.get("material", "SA-516-70"),
            corrosion_allowance_in=request.get("corrosion_allowance_in", 0.0625),
            design_temp_f=request.get("design_temp_f") or request.get("design_temperature_f", 650.0),
        )

        result = validator.validate_vessel(vessel)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"ASME VIII check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-geometry")
async def check_geometry(request: dict):
    """
    Validate geometry features: corner radii, copes, notches, web openings.

    Request body:
        corners: List of {radius, angle_deg, cutting_process, location}
        copes: List of {cope_depth_in, cope_length_in, corner_radius_in, beam_depth_in}
        notches: List of {notch_depth_in, notch_radius_in, is_fatigue_critical}
        web_openings: List of {opening_depth_in, opening_length_in, beam_depth_in, ...}

    Returns:
        Geometry validation results (4 checks)
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.geometry_profile_validator import (
            GeometryProfileValidator, CornerData, CopeData, NotchData, WebOpeningData
        )

        validator = GeometryProfileValidator()

        corners = [CornerData(**c) for c in request.get("corners", [])]
        copes = [CopeData(**c) for c in request.get("copes", [])]
        notches = [NotchData(**n) for n in request.get("notches", [])]
        openings = [WebOpeningData(**o) for o in request.get("web_openings", [])]

        result = validator.validate_all(corners, copes, notches, openings)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Geometry check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-tolerances")
async def check_tolerances(request: dict):
    """
    Validate GD&T tolerances: flatness, squareness, parallelism.

    Request body:
        flatness: List of {surface_length_in, surface_width_in, specified_tolerance_in, surface_grade}
        squareness: List of {feature_length_in, specified_tolerance_in, surface_grade}
        parallelism: List of {feature_length_in, separation_distance_in, specified_tolerance_in}

    Returns:
        Tolerance validation results (3 checks)
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.tolerance_validator import (
            ToleranceValidator, FlatnessData, SquarenessData, ParallelismData
        )

        validator = ToleranceValidator()

        flatness = [FlatnessData(**f) for f in request.get("flatness", [])]
        squareness = [SquarenessData(**s) for s in request.get("squareness", [])]
        parallelism = [ParallelismData(**p) for p in request.get("parallelism", [])]

        result = validator.validate_all(flatness, squareness, parallelism)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Tolerance check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-sheet-metal")
async def check_sheet_metal(request: dict):
    """
    Validate sheet metal: bend allowance, grain direction, springback.

    Request body:
        bends: List of {
            material_thickness_in, inside_bend_radius_in, bend_angle_deg,
            material_type, bend_method, grain_direction
        }

    Returns:
        Sheet metal validation results (3 checks per bend)
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.sheet_metal_validator import SheetMetalValidator, BendData

        validator = SheetMetalValidator()

        bends = [BendData(**b) for b in request.get("bends", [])]
        result = validator.validate_all(bends)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Sheet metal check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-member-capacity")
async def check_member_capacity(request: dict):
    """
    Validate structural member capacity and deflection.

    Request body:
        members: List of {
            section: "W12X40",
            length_in: 240,
            material: "A992",
            applied_moment_kip_in, applied_shear_kips, applied_axial_kips,
            uniform_load_kip_per_in, application, is_cantilever
        }

    Returns:
        Member capacity and deflection validation results (2 checks)
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.member_capacity_validator import MemberCapacityValidator, MemberData

        validator = MemberCapacityValidator()

        members = [MemberData(**m) for m in request.get("members", [])]
        result = validator.validate_all(members)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Member capacity check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-tema")
async def check_tema(request: dict):
    """
    Validate heat exchanger design per TEMA standards (Class R/B/C).

    Request body:
        tema_class: String ("R", "B", or "C")
        shell_id_in: Float
        tube_od_in: Float
        tube_pitch_in: Float
        tube_layout: String ("triangular", "square", etc.)
        tubesheet_thickness_in: Float
        tube_joint_type: String ("expanded", "welded", "expanded_welded", "strength_welded")
        baffle_spacing_in: Float
        baffle_cut_percent: Float
        tube_side_velocity_fps: Float (optional)
        shell_side_velocity_fps: Float (optional)
        tube_side_fluid: String ("liquid" or "gas")
        shell_side_fluid: String ("liquid" or "gas")

    Returns:
        TEMA validation results with 6 checks
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.tema_validator import (
            TEMAValidator, TEMAClass, HeatExchangerData, TubeJointType
        )

        validator = TEMAValidator()

        # Parse TEMA class
        tema_class_str = request.get("tema_class", "R").upper()
        tema_class = TEMAClass.R
        if tema_class_str == "B":
            tema_class = TEMAClass.B
        elif tema_class_str == "C":
            tema_class = TEMAClass.C

        # Parse tube joint type
        joint_str = request.get("tube_joint_type", "expanded").lower()
        tube_joint = TubeJointType.EXPANDED
        if joint_str == "welded":
            tube_joint = TubeJointType.WELDED
        elif joint_str == "expanded_welded":
            tube_joint = TubeJointType.EXPANDED_WELDED
        elif joint_str == "strength_welded":
            tube_joint = TubeJointType.STRENGTH_WELDED

        hx = HeatExchangerData(
            tema_class=tema_class,
            shell_id_in=request.get("shell_id_in"),
            tube_od_in=request.get("tube_od_in"),
            tube_pitch_in=request.get("tube_pitch_in"),
            tube_layout=request.get("tube_layout", "triangular"),
            num_tubes=request.get("num_tubes", 0),
            tubesheet_thickness_in=request.get("tubesheet_thickness_in"),
            tube_joint_type=tube_joint,
            num_baffles=request.get("num_baffles", 0),
            baffle_spacing_in=request.get("baffle_spacing_in"),
            baffle_cut_percent=request.get("baffle_cut_percent", 25.0),
            tube_side_velocity_fps=request.get("tube_side_velocity_fps"),
            shell_side_velocity_fps=request.get("shell_side_velocity_fps"),
            tube_side_fluid=request.get("tube_side_fluid", "liquid"),
            shell_side_fluid=request.get("shell_side_fluid", "liquid"),
        )

        result = validator.validate_exchanger(hx)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"TEMA check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PHASE 25.3-25.13 - NEW VALIDATOR ENDPOINTS
# =============================================================================


@app.post("/phase25/check-fabrication")
async def check_fabrication(request: dict):
    """
    Validate part fabrication feasibility.

    Request body:
        thickness_in: Float - Material thickness
        length_in: Float - Part length
        width_in: Float - Part width
        holes: List[dict] - Hole data [{diameter, x, y}]
        slots: List[dict] - Slot data [{width, length, x, y}]
        bends: List[dict] - Bend data [{angle, radius, length}]
        notches: List[dict] - Notch data [{width, depth}]
        process: String - "plasma", "laser", "waterjet", "oxyfuel" (optional)

    Returns:
        Fabrication feasibility results with manufacturability assessment
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.fabrication_feasibility_validator import (
            FabricationFeasibilityValidator, PartGeometry, FabricationProcess
        )

        validator = FabricationFeasibilityValidator()

        # Parse process
        process_str = request.get("process", "plasma").lower()
        process_map = {
            "plasma": FabricationProcess.PLASMA_CUT,
            "laser": FabricationProcess.LASER_CUT,
            "waterjet": FabricationProcess.WATER_JET,
            "oxyfuel": FabricationProcess.OXY_FUEL,
        }
        process = process_map.get(process_str, FabricationProcess.PLASMA_CUT)

        geometry = PartGeometry(
            thickness=request.get("thickness_in", 0.5),
            length=request.get("length_in", 48),
            width=request.get("width_in", 24),
            holes=request.get("holes", []),
            slots=request.get("slots", []),
            bends=request.get("bends", []),
            notches=request.get("notches", []),
        )

        result = validator.validate_part(geometry, process)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Fabrication check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-inspection")
async def check_inspection(request: dict):
    """
    Validate inspection and QC requirements.

    Request body:
        welds: List[dict] - Weld inspection data
        dimensional_features: List[dict] - Critical dimensions
        surface_requirements: dict - Surface finish requirements
        pressure_test: dict - Pressure test data (optional)
        material_certs: List[str] - Required certifications

    Returns:
        Inspection/QC validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.inspection_qc_validator import (
            InspectionQCValidator, WeldInspectionData, InspectionPlanData, NDEMethod, WeldCategory
        )

        validator = InspectionQCValidator()

        # Parse welds from request
        welds = []
        for i, w in enumerate(request.get("welds", [])):
            cat_str = w.get("category", "primary").lower()
            # Map test categories to actual enum values
            category_map = {
                "critical": WeldCategory.PRESSURE_RETAINING,
                "primary": WeldCategory.STRUCTURAL_PRIMARY,
                "secondary": WeldCategory.STRUCTURAL_SECONDARY,
            }
            category = category_map.get(cat_str, WeldCategory.STRUCTURAL_PRIMARY)
            welds.append(WeldInspectionData(
                weld_id=f"W{i+1}",
                category=category,
                length_in=w.get("length", 12),
                size_in=w.get("size", 0.25),
                joint_type=w.get("type", "fillet"),
                code=request.get("code", "AWS D1.1"),
            ))

        # Create inspection plan
        plan = InspectionPlanData(
            part_number=request.get("drawing_number", "DWG-001"),
            applicable_codes=[request.get("code", "AWS D1.1")],
            welds=welds,
        )

        result = validator.validate_inspection_plan(plan)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Inspection check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-cross-part")
async def check_cross_part(request: dict):
    """
    Validate cross-part interface compatibility.

    Request body:
        interfaces: List[dict] - Part interface definitions
            Each: {part_a, part_b, interface_type, hole_patterns, fit_class}

    Returns:
        Cross-part compatibility results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.cross_part_validator import (
            CrossPartValidator, PartInterface, HolePattern, InterfaceType, FitClass
        )

        validator = CrossPartValidator()

        interfaces = []
        for i, iface in enumerate(request.get("interfaces", [])):
            iface_type_str = iface.get("interface_type", "bolted").upper()
            iface_type = InterfaceType.BOLTED if iface_type_str == "BOLTED" else InterfaceType.WELDED

            # Parse hole patterns if present
            hole_pattern = None
            if iface.get("hole_patterns"):
                hp = iface["hole_patterns"][0]
                num_holes = hp.get("holes", 4)
                diameter = hp.get("diameter", 0.8125)
                bolt_circle = hp.get("bolt_circle", 6.0)
                # Create holes list for bolt circle pattern
                import math
                holes_list = []
                for h in range(num_holes):
                    angle = 2 * math.pi * h / num_holes
                    x = bolt_circle / 2 * math.cos(angle)
                    y = bolt_circle / 2 * math.sin(angle)
                    holes_list.append({"x": x, "y": y, "diameter": diameter, "type": "bolt"})
                hole_pattern = HolePattern(
                    holes=holes_list,
                    bolt_circle_diameter=bolt_circle,
                    pattern_type="circular",
                )

            # Create interface for part A
            interface_a = PartInterface(
                part_id=iface.get("part_a", f"PART-A-{i}"),
                interface_id=f"INTF-{i}-A",
                interface_type=iface_type,
                holes=hole_pattern,
            )
            interfaces.append(interface_a)

            # Create interface for part B
            interface_b = PartInterface(
                part_id=iface.get("part_b", f"PART-B-{i}"),
                interface_id=f"INTF-{i}-B",
                interface_type=iface_type,
                holes=hole_pattern,
            )
            interfaces.append(interface_b)

        result = validator.validate_assembly(interfaces)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Cross-part check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-materials")
async def check_materials(request: dict):
    """
    Validate material specifications and surface finishing.

    Request body:
        material_spec: String - Material specification (e.g., "A36", "A572-50")
        thickness_in: Float - Material thickness
        coating_system: String - Coating system ID (e.g., "C1", "HDG")
        surface_prep: String - Surface prep level (e.g., "SP6", "SP10")
        service_environment: String - "mild", "moderate", "severe"
        galvanizing: dict - Galvanizing requirements (optional)

    Returns:
        Materials and finishing validation results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.materials_finishing_validator import (
            MaterialsFinishingValidator, MaterialSpec, CoatingSpec, SurfacePrep
        )

        validator = MaterialsFinishingValidator()

        # Validate material
        material = MaterialSpec(
            specification=request.get("material_spec", "A36"),
            thickness=request.get("thickness_in"),
            mtr_required=request.get("mtr_required", False),
        )

        mat_result = validator.validate_material(
            material,
            application=request.get("application", "structural")
        )

        # Validate coating if specified
        coating_result = None
        if request.get("coating_system"):
            prep_str = request.get("surface_prep", "SP6").upper()
            prep_map = {
                "SP1": SurfacePrep.SP1, "SP2": SurfacePrep.SP2, "SP3": SurfacePrep.SP3,
                "SP5": SurfacePrep.SP5, "SP6": SurfacePrep.SP6, "SP7": SurfacePrep.SP7,
                "SP10": SurfacePrep.SP10, "SP11": SurfacePrep.SP11, "SP14": SurfacePrep.SP14,
            }

            coating = CoatingSpec(
                coating_system=request.get("coating_system"),
                surface_prep=prep_map.get(prep_str, SurfacePrep.SP6),
                total_dft_mils=request.get("dft_mils"),
                service_environment=request.get("service_environment", "moderate"),
            )

            coating_result = validator.validate_coating_system(
                coating,
                service_life_years=request.get("service_life_years", 20)
            )

        combined = validator.to_dict(mat_result)
        if coating_result:
            combined["coating"] = validator.to_dict(coating_result)

        return combined

    except Exception as e:
        logger.error(f"Materials check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-fasteners")
async def check_fasteners(request: dict):
    """
    Validate fastener and bolted connection specifications.

    Request body:
        bolts: List[dict] - Bolt specifications
            Each: {diameter, grade, connection_type, hole_type}
        connection: dict - Connection data
            {grip_length, load_kips, load_type, edge_distance, bolt_spacing}

    Returns:
        Fastener validation results with torque calculations
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.fastener_validator import (
            FastenerValidator, BoltData, ConnectionData, BoltGrade, ConnectionType, HoleType
        )

        validator = FastenerValidator()

        # Parse bolts
        bolts = []
        for b in request.get("bolts", []):
            grade_str = b.get("grade", "A325").upper()
            grade_map = {
                "A325": BoltGrade.A325, "A490": BoltGrade.A490, "A307": BoltGrade.A307,
                "F1852": BoltGrade.F1852, "F2280": BoltGrade.F2280,
            }

            conn_str = b.get("connection_type", "snug_tight").lower()
            conn_map = {
                "snug_tight": ConnectionType.SNUG_TIGHT,
                "pretensioned": ConnectionType.PRETENSIONED,
                "slip_critical": ConnectionType.SLIP_CRITICAL,
            }

            hole_str = b.get("hole_type", "STD").upper()
            hole_map = {
                "STD": HoleType.STANDARD, "OVS": HoleType.OVERSIZED,
                "SSL": HoleType.SHORT_SLOT, "LSL": HoleType.LONG_SLOT,
            }

            bolt = BoltData(
                diameter=b.get("diameter", 0.75),
                grade=grade_map.get(grade_str, BoltGrade.A325),
                length=b.get("length"),
                connection_type=conn_map.get(conn_str, ConnectionType.SNUG_TIGHT),
                hole_type=hole_map.get(hole_str, HoleType.STANDARD),
                specified_torque=b.get("torque"),
                lubricated=b.get("lubricated", False),
            )
            bolts.append(bolt)

        # Create connection
        conn_data = request.get("connection", {})
        connection = ConnectionData(
            bolts=bolts,
            grip_length=conn_data.get("grip_length", 0),
            load_kips=conn_data.get("load_kips", 0),
            load_type=conn_data.get("load_type", "shear"),
            faying_surface=conn_data.get("faying_surface", "class_a"),
            edge_distance=conn_data.get("edge_distance"),
            bolt_spacing=conn_data.get("bolt_spacing"),
        )

        result = validator.validate_connection(connection)
        return validator.to_dict(result)

    except Exception as e:
        logger.error(f"Fastener check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-rigging")
async def check_rigging(request: dict):
    """
    Validate lifting lugs and rigging arrangements per ASME BTH-1.

    Request body:
        lug: dict - Lifting lug data
            {plate_thickness, plate_width, hole_diameter, edge_distance,
             throat_width, material, rated_load_lbs, sling_angle_deg,
             weld_size, weld_length, load_class}
        rigging: dict - Rigging arrangement (optional)
            {total_load_lbs, center_of_gravity, lift_points}

    Returns:
        Rigging validation with stress calculations
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.rigging_validator import (
            RiggingValidator, LiftingLugData, RiggingData, LoadClass
        )

        validator = RiggingValidator()

        lug_data = request.get("lug", {})
        load_class_str = lug_data.get("load_class", "A").upper()
        load_class_map = {
            "A": LoadClass.CLASS_A, "B": LoadClass.CLASS_B,
            "C": LoadClass.CLASS_C, "D": LoadClass.CLASS_D,
        }

        lug = LiftingLugData(
            load_class=load_class_map.get(load_class_str, LoadClass.CLASS_A),
            plate_thickness=lug_data.get("plate_thickness", 0.5),
            plate_width=lug_data.get("plate_width", 4),
            hole_diameter=lug_data.get("hole_diameter", 1.0),
            edge_distance=lug_data.get("edge_distance", 1.5),
            throat_width=lug_data.get("throat_width", 3),
            material=lug_data.get("material", "A36"),
            rated_load_lbs=lug_data.get("rated_load_lbs", 5000),
            sling_angle_deg=lug_data.get("sling_angle_deg", 90),
            weld_size=lug_data.get("weld_size", 0.25),
            weld_length=lug_data.get("weld_length", 8),
        )

        result = validator.validate_lifting_lug(lug)
        output = validator.to_dict(result)

        # Check rigging arrangement if provided
        if request.get("rigging"):
            rig_data = request["rigging"]
            rigging = RiggingData(
                total_load_lbs=rig_data.get("total_load_lbs", 0),
                center_of_gravity=tuple(rig_data.get("center_of_gravity", [0, 0, 0])),
                lift_points=[tuple(p) for p in rig_data.get("lift_points", [])],
            )
            rig_result = validator.validate_rigging_arrangement(rigging)
            output["rigging_arrangement"] = validator.to_dict(rig_result)

        return output

    except Exception as e:
        logger.error(f"Rigging check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/check-documentation")
async def check_documentation(request: dict):
    """
    Validate drawing documentation completeness.

    Request body:
        title_block: dict - Title block fields
            {drawing_number, revision, title, scale, sheet, drawn_by, etc.}
        notes: dict - Drawing notes
            {general_notes: [], local_notes: [], flag_notes: []}
        drawing_type: String - "detail", "assembly", "weldment", etc.
        documentation_level: String - "commercial", "industrial", "nuclear", etc.
        bom: List[dict] - Bill of materials (optional)

    Returns:
        Documentation completeness results
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.documentation_validator import (
            DocumentationValidator, TitleBlockData, DrawingNotes,
            DrawingType, DocumentationLevel
        )

        validator = DocumentationValidator()

        # Parse title block
        tb_data = request.get("title_block", {})
        title_block = TitleBlockData(
            drawing_number=tb_data.get("drawing_number"),
            revision=tb_data.get("revision"),
            title=tb_data.get("title"),
            scale=tb_data.get("scale"),
            sheet=tb_data.get("sheet"),
            drawn_by=tb_data.get("drawn_by"),
            drawn_date=tb_data.get("date"),
            checked_by=tb_data.get("checked_by"),
            approved_by=tb_data.get("approved_by"),
            material=tb_data.get("material"),
            finish=tb_data.get("finish"),
        )

        # Parse notes
        notes_data = request.get("notes", {})
        notes = DrawingNotes(
            general_notes=notes_data.get("general_notes", []),
            local_notes=notes_data.get("local_notes", []),
            flag_notes=notes_data.get("flag_notes", []),
            bill_of_materials=request.get("bom", []),
        )

        # Parse enums
        type_str = request.get("drawing_type", "detail").lower()
        type_map = {
            "detail": DrawingType.DETAIL, "assembly": DrawingType.ASSEMBLY,
            "weldment": DrawingType.WELDMENT, "machined_part": DrawingType.MACHINED_PART,
            "sheet_metal": DrawingType.SHEET_METAL, "pressure_vessel": DrawingType.PRESSURE_VESSEL,
        }

        level_str = request.get("documentation_level", "industrial").lower()
        level_map = {
            "commercial": DocumentationLevel.COMMERCIAL,
            "industrial": DocumentationLevel.INDUSTRIAL,
            "nuclear": DocumentationLevel.NUCLEAR,
            "aerospace": DocumentationLevel.AEROSPACE,
            "pressure": DocumentationLevel.PRESSURE_VESSEL,
        }

        # Run validations
        tb_result = validator.validate_title_block(
            title_block,
            level=level_map.get(level_str, DocumentationLevel.INDUSTRIAL)
        )

        notes_result = validator.validate_notes(
            notes,
            drawing_type=type_map.get(type_str, DrawingType.DETAIL),
            level=level_map.get(level_str, DocumentationLevel.INDUSTRIAL)
        )

        # Combine results
        output = validator.to_dict(tb_result)
        output["notes_validation"] = validator.to_dict(notes_result)

        # BOM validation if assembly
        if request.get("bom") and type_str in ["assembly", "weldment"]:
            bom_result = validator.validate_bom(
                request["bom"],
                drawing_type=type_map.get(type_str, DrawingType.ASSEMBLY)
            )
            output["bom_validation"] = validator.to_dict(bom_result)

        return output

    except Exception as e:
        logger.error(f"Documentation check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/generate-report")
async def generate_report(request: dict):
    """
    Generate comprehensive validation report from multiple validator results.

    Request body:
        drawing_number: String
        drawing_revision: String
        project_name: String (optional)
        validator_results: dict - Results from individual validators
            {validator_name: result_dict, ...}
        format: String - "json", "html", "markdown" (default: json)
        level: String - "summary", "standard", "detailed" (default: standard)

    Returns:
        Comprehensive validation report in specified format
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.report_generator import (
            ReportGenerator, ReportFormat, ReportLevel
        )

        generator = ReportGenerator()

        # Add all validator results
        for name, result in request.get("validator_results", {}).items():
            generator.add_result(name, result)

        # Parse level
        level_str = request.get("level", "standard").lower()
        level_map = {
            "summary": ReportLevel.SUMMARY,
            "standard": ReportLevel.STANDARD,
            "detailed": ReportLevel.DETAILED,
            "debug": ReportLevel.DEBUG,
        }

        # Generate report
        report = generator.generate_report(
            drawing_number=request.get("drawing_number"),
            drawing_revision=request.get("drawing_revision"),
            project_name=request.get("project_name"),
            level=level_map.get(level_str, ReportLevel.STANDARD)
        )

        # Export in requested format
        format_str = request.get("format", "json").lower()

        if format_str == "html":
            return {"format": "html", "content": generator.export_html()}
        elif format_str == "markdown":
            return {"format": "markdown", "content": generator.export_markdown()}
        else:
            return {"format": "json", "content": generator.export_json()}

    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/generate-pdf-report")
async def generate_pdf_report(request: dict):
    """
    Generate PDF validation report.

    Request body:
        drawing_number: String
        drawing_revision: String
        project_name: String (optional)
        validator_results: dict - Results from individual validators
        level: String - "summary", "standard", "detailed" (default: standard)
        include_charts: Boolean (default: true)
        summary_only: Boolean (default: false) - Generate 1-page executive summary

    Returns:
        PDF file as base64-encoded bytes with metadata
    """
    try:
        import sys
        import base64
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.report_generator import (
            ReportGenerator, ReportLevel
        )

        generator = ReportGenerator()

        # Add all validator results
        for name, result in request.get("validator_results", {}).items():
            generator.add_result(name, result)

        # Parse level
        level_str = request.get("level", "standard").lower()
        level_map = {
            "summary": ReportLevel.SUMMARY,
            "standard": ReportLevel.STANDARD,
            "detailed": ReportLevel.DETAILED,
            "debug": ReportLevel.DEBUG,
        }

        # Generate report
        report = generator.generate_report(
            drawing_number=request.get("drawing_number"),
            drawing_revision=request.get("drawing_revision"),
            project_name=request.get("project_name"),
            level=level_map.get(level_str, ReportLevel.STANDARD)
        )

        # Generate PDF
        summary_only = request.get("summary_only", False)
        include_charts = request.get("include_charts", True)

        if summary_only:
            pdf_bytes = generator.export_pdf_summary(filepath=None)
        else:
            pdf_bytes = generator.export_pdf(filepath=None, include_charts=include_charts)

        # Return as base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        return {
            "format": "pdf",
            "filename": f"validation_report_{request.get('drawing_number', 'unknown')}.pdf",
            "content_base64": pdf_base64,
            "size_bytes": len(pdf_bytes),
            "overall_status": report.overall_status,
            "pass_rate": round(report.overall_pass_rate, 1),
        }

    except ImportError as e:
        logger.error(f"PDF generation requires reportlab: {e}")
        raise HTTPException(status_code=500, detail="reportlab not installed. Run: pip install reportlab")
    except Exception as e:
        logger.error(f"PDF report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/export-bom-excel")
async def export_bom_excel(request: dict):
    """
    Export BOM to Excel format.

    Request body:
        items: List of BOM items with fields:
            - item/item_number: int
            - part_number: str
            - description: str
            - qty/quantity: int
            - unit: str (default: EA)
            - material: str
            - weight_lbs/weight: float
            - unit_cost/cost: float
            - supplier/vendor: str
            - lead_time_days/lead_time: int
            - category/type: str
            - stock_size/size: str
            - finish/coating: str
            - drawing_ref/dwg: str
            - notes/remarks: str
        metadata: Optional dict with:
            - assembly_number: str
            - assembly_name: str
            - revision: str
            - project_name: str
            - customer: str
            - prepared_by: str
        include_charts: bool (default: true)

    Returns:
        Excel file as base64-encoded bytes with summary
    """
    try:
        import sys
        import base64
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.bom_exporter import BOMExporter, BOMMetadata

        exporter = BOMExporter()

        # Set metadata
        meta = request.get("metadata", {})
        exporter.set_metadata(BOMMetadata(
            assembly_number=meta.get("assembly_number", ""),
            assembly_name=meta.get("assembly_name", ""),
            revision=meta.get("revision", ""),
            project_name=meta.get("project_name", ""),
            project_number=meta.get("project_number", ""),
            customer=meta.get("customer", ""),
            prepared_by=meta.get("prepared_by", ""),
            date=meta.get("date", ""),
        ))

        # Load items
        exporter.from_dict_list(request.get("items", []))

        # Export to Excel
        include_charts = request.get("include_charts", True)
        result = exporter.export_excel(filepath=None, include_charts=include_charts)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)

        # Return as base64
        excel_base64 = base64.b64encode(result.content).decode('utf-8')

        return {
            "format": "excel",
            "filename": result.filename,
            "content_base64": excel_base64,
            "size_bytes": result.size_bytes,
            "summary": exporter.get_summary(),
        }

    except Exception as e:
        logger.error(f"BOM Excel export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/validate-beam")
async def validate_beam(request: dict):
    """
    Validate beam design per AISC 360-16.

    Request body:
        shape: str (e.g., "W16X77")
        span_ft: float
        unbraced_length_ft: float
        moment_kip_ft: float
        shear_kips: float
        axial_kips: float (optional, default 0)
        material: str (optional, default "A992")
        deflection_limit: str (optional, default "floor_live")
        calculated_deflection_in: float (optional)

    Returns:
        Validation result with DCR calculations
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.aisc_structural_validator import AISCStructuralValidator, BeamData

        validator = AISCStructuralValidator()
        beam = BeamData(
            shape=request.get("shape", "W16X77"),
            span_ft=request.get("span_ft", 20),
            unbraced_length_ft=request.get("unbraced_length_ft", request.get("span_ft", 20)),
            moment_kip_ft=request.get("moment_kip_ft", 0),
            shear_kips=request.get("shear_kips", 0),
            axial_kips=request.get("axial_kips", 0),
            material=request.get("material", "A992"),
            deflection_limit=request.get("deflection_limit", "floor_live"),
            calculated_deflection_in=request.get("calculated_deflection_in", 0),
        )

        result = validator.validate_beam(beam)
        return result.to_dict()

    except Exception as e:
        logger.error(f"Beam validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/validate-column")
async def validate_column(request: dict):
    """
    Validate column design per AISC 360-16.

    Request body:
        shape: str (e.g., "W14X68")
        height_ft: float
        axial_load_kips: float
        moment_x_kip_ft: float (optional)
        moment_y_kip_ft: float (optional)
        k_factor: float (optional, default 1.0)
        material: str (optional, default "A992")

    Returns:
        Validation result with slenderness and capacity calculations
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.aisc_structural_validator import AISCStructuralValidator, ColumnData

        validator = AISCStructuralValidator()
        column = ColumnData(
            shape=request.get("shape", "W14X68"),
            height_ft=request.get("height_ft", 12),
            axial_load_kips=request.get("axial_load_kips", 0),
            moment_x_kip_ft=request.get("moment_x_kip_ft", 0),
            moment_y_kip_ft=request.get("moment_y_kip_ft", 0),
            k_factor=request.get("k_factor", 1.0),
            material=request.get("material", "A992"),
        )

        result = validator.validate_column(column)
        return result.to_dict()

    except Exception as e:
        logger.error(f"Column validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/validate-connection")
async def validate_steel_connection(request: dict):
    """
    Validate steel connection per AISC 360-16 Chapter J.

    Request body:
        connection_type: str ("bolted_shear", "welded_shear", etc.)
        load_kips: float
        bolt_diameter: float (optional, default 0.75)
        bolt_grade: str (optional, default "A325")
        num_bolts: int (optional, default 4)
        weld_size: float (optional, default 0.25)
        weld_length: float (optional)
        electrode: str (optional, default "E70XX")
        plate_thickness: float (optional, default 0.5)
        plate_material: str (optional, default "A36")

    Returns:
        Validation result with capacity calculations
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.aisc_structural_validator import (
            AISCStructuralValidator, ConnectionData, ConnectionType
        )

        conn_type_map = {
            "bolted_shear": ConnectionType.BOLTED_SHEAR,
            "bolted_moment": ConnectionType.BOLTED_MOMENT,
            "welded_shear": ConnectionType.WELDED_SHEAR,
            "welded_moment": ConnectionType.WELDED_MOMENT,
            "shear_tab": ConnectionType.SHEAR_TAB,
            "clip_angle": ConnectionType.CLIP_ANGLE,
        }

        validator = AISCStructuralValidator()
        conn = ConnectionData(
            connection_type=conn_type_map.get(request.get("connection_type", "bolted_shear"),
                                              ConnectionType.BOLTED_SHEAR),
            load_kips=request.get("load_kips", 0),
            bolt_diameter=request.get("bolt_diameter", 0.75),
            bolt_grade=request.get("bolt_grade", "A325"),
            num_bolts=request.get("num_bolts", 4),
            weld_size=request.get("weld_size", 0.25),
            weld_length=request.get("weld_length", 0),
            electrode=request.get("electrode", "E70XX"),
            plate_thickness=request.get("plate_thickness", 0.5),
            plate_material=request.get("plate_material", "A36"),
        )

        result = validator.validate_connection(conn)
        return result.to_dict()

    except Exception as e:
        logger.error(f"Connection validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/validate-base-plate")
async def validate_base_plate(request: dict):
    """
    Validate base plate design per AISC Design Guide 1.

    Request body:
        plate_length: float
        plate_width: float
        plate_thickness: float
        column_depth: float
        column_bf: float
        axial_load_kips: float
        moment_kip_ft: float (optional)
        concrete_fc_psi: float (optional, default 3000)
        material: str (optional, default "A36")
        anchor_diameter: float (optional, default 0.75)
        anchor_embedment: float (optional, default 9)

    Returns:
        Validation result with bearing and bending calculations
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.aisc_structural_validator import AISCStructuralValidator, BasePlateData

        validator = AISCStructuralValidator()
        bp = BasePlateData(
            plate_length=request.get("plate_length", 12),
            plate_width=request.get("plate_width", 12),
            plate_thickness=request.get("plate_thickness", 1.0),
            column_depth=request.get("column_depth", 8),
            column_bf=request.get("column_bf", 8),
            axial_load_kips=request.get("axial_load_kips", 0),
            moment_kip_ft=request.get("moment_kip_ft", 0),
            concrete_fc_psi=request.get("concrete_fc_psi", 3000),
            material=request.get("material", "A36"),
            anchor_diameter=request.get("anchor_diameter", 0.75),
            anchor_embedment=request.get("anchor_embedment", 9),
        )

        result = validator.validate_base_plate(bp)
        return result.to_dict()

    except Exception as e:
        logger.error(f"Base plate validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/generate-markup")
async def generate_drawing_markup(request: dict):
    """
    Generate SVG markup overlay for validation issues.

    Request body:
        drawing_number: String
        revision: String
        width: Float (default: 1100)
        height: Float (default: 850)
        issues: List of validation issues with optional location:
            - severity: str (critical/error/warning/info)
            - message: str
            - location: {x: float, y: float} (optional)
            - check_type: str
            - suggestion: str
            - standard_reference: str
        include_legend: Boolean (default: true)

    Returns:
        SVG markup as string with issue table
    """
    try:
        import sys
        import base64
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.drawing_markup import DrawingMarkupGenerator

        generator = DrawingMarkupGenerator()

        # Set drawing info
        generator.set_drawing_info(
            drawing_number=request.get("drawing_number", "DRAWING"),
            revision=request.get("revision", ""),
            width=request.get("width", 1100),
            height=request.get("height", 850),
        )

        # Add issues as markups
        issues = request.get("issues", [])
        generator.add_from_validation_issues(issues)

        # Generate SVG
        include_legend = request.get("include_legend", True)
        svg_content = generator.generate_svg(include_legend=include_legend)

        # Get issue table
        issue_table = generator.get_issue_table()

        return {
            "format": "svg",
            "filename": f"markup_{request.get('drawing_number', 'drawing')}.svg",
            "content": svg_content,
            "size_bytes": len(svg_content.encode('utf-8')),
            "total_markups": len(issue_table),
            "issue_table": issue_table,
        }

    except Exception as e:
        logger.error(f"Drawing markup generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/phase25/export-bom-csv")
async def export_bom_csv(request: dict):
    """
    Export BOM to CSV format.

    Request body:
        items: List of BOM items (same format as Excel export)
        metadata: Optional metadata dict

    Returns:
        CSV file as base64-encoded bytes with summary
    """
    try:
        import sys
        import base64
        sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
        from validators.bom_exporter import BOMExporter, BOMMetadata

        exporter = BOMExporter()

        # Set metadata
        meta = request.get("metadata", {})
        exporter.set_metadata(BOMMetadata(
            assembly_number=meta.get("assembly_number", ""),
            assembly_name=meta.get("assembly_name", ""),
            revision=meta.get("revision", ""),
        ))

        # Load items
        exporter.from_dict_list(request.get("items", []))

        # Export to CSV
        result = exporter.export_csv(filepath=None)

        # Return as base64
        csv_base64 = base64.b64encode(result.content).decode('utf-8')

        return {
            "format": "csv",
            "filename": result.filename,
            "content_base64": csv_base64,
            "size_bytes": result.size_bytes,
            "summary": exporter.get_summary(),
        }

    except Exception as e:
        logger.error(f"BOM CSV export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


# =============================================================================
# PHASE 24: ACHE DESIGN ASSISTANT ENDPOINTS
# =============================================================================

# Global ACHE event listener instance
_ache_listener = None
_ache_detector = None
_ache_property_reader = None


def _get_ache_modules():
    """Lazy load ACHE modules."""
    global _ache_listener, _ache_detector, _ache_property_reader
    if _ache_listener is None:
        try:
            from ache.event_listener import ACHEEventListener
            from ache.detector import ACHEModelDetector
            from ache.property_reader import ACHEPropertyReader
            _ache_listener = ACHEEventListener()
            _ache_detector = ACHEModelDetector()
            _ache_property_reader = ACHEPropertyReader()
        except ImportError as e:
            logger.warning(f"ACHE modules not available: {e}")
    return _ache_listener, _ache_detector, _ache_property_reader


@app.get("/ache/status")
async def get_ache_status():
    """
    Get ACHE Design Assistant status.
    Phase 24.1 - Auto-launch system status
    """
    listener, detector, reader = _get_ache_modules()
    if listener is None:
        return {"status": "unavailable", "reason": "ACHE modules not loaded"}

    return {
        "status": "available",
        "listener": listener.get_status() if listener else None,
        "detector_config": detector.get_detection_config() if detector else None,
    }


@app.post("/ache/listener/start")
async def start_ache_listener():
    """
    Start the ACHE model event listener.
    Phase 24.1.1 - SolidWorks event listener
    """
    listener, _, _ = _get_ache_modules()
    if listener is None:
        raise HTTPException(status_code=503, detail="ACHE modules not available")

    success = listener.start()
    return {
        "started": success,
        "status": listener.get_status()
    }


@app.post("/ache/listener/stop")
async def stop_ache_listener():
    """Stop the ACHE model event listener."""
    listener, _, _ = _get_ache_modules()
    if listener is None:
        raise HTTPException(status_code=503, detail="ACHE modules not available")

    listener.stop()
    return {"stopped": True}


@app.get("/ache/detect")
async def detect_ache_model():
    """
    Detect if current model is an ACHE component.
    Phase 24.1.2 - ACHE model detection
    """
    _, detector, reader = _get_ache_modules()
    if detector is None or reader is None:
        raise HTTPException(status_code=503, detail="ACHE modules not available")

    # Get current model properties
    props = reader.read_properties()
    if props is None:
        raise HTTPException(status_code=404, detail="No active model in SolidWorks")

    # Detect if ACHE
    component_names = [c.name for c in props.components] if props.components else []
    result = detector.detect(
        filepath=props.filepath,
        custom_properties=props.custom_properties,
        component_names=component_names
    )

    return {
        "filepath": props.filepath,
        "filename": props.filename,
        "is_ache": result.is_ache,
        "confidence": result.confidence,
        "component_type": result.component_type.value,
        "detection_reasons": result.detection_reasons,
        "api_661_applicable": result.api_661_applicable,
        "suggested_validators": result.suggested_validators,
    }


@app.get("/ache/overview")
async def get_ache_overview():
    """
    Get ACHE model overview - comprehensive property extraction.
    Phase 24.2 - Model Overview Tab
    """
    _, detector, reader = _get_ache_modules()
    if reader is None:
        raise HTTPException(status_code=503, detail="ACHE modules not available")

    props = reader.read_properties()
    if props is None:
        raise HTTPException(status_code=404, detail="No active model in SolidWorks")

    # Add ACHE detection info
    component_names = [c.name for c in props.components] if props.components else []
    detection = detector.detect(
        filepath=props.filepath,
        custom_properties=props.custom_properties,
        component_names=component_names
    ) if detector else None

    overview = reader.to_dict(props)
    if detection:
        overview["ache_detection"] = {
            "is_ache": detection.is_ache,
            "confidence": detection.confidence,
            "component_type": detection.component_type.value,
            "api_661_applicable": detection.api_661_applicable,
            "suggested_validators": detection.suggested_validators,
        }

    return overview


@app.get("/ache/properties")
async def get_ache_properties():
    """
    Get ACHE-specific properties from current model.
    Phase 24.3 - Properties Extraction
    """
    _, _, reader = _get_ache_modules()
    if reader is None:
        raise HTTPException(status_code=503, detail="ACHE modules not available")

    props = reader.read_properties()
    if props is None:
        raise HTTPException(status_code=404, detail="No active model in SolidWorks")

    return reader.to_dict(props)


# ============================================================================
# Phase 24.4-24.8: ACHE Assistant Endpoints
# ============================================================================

def _get_ache_assistant_modules():
    """Lazy load ACHE assistant modules."""
    try:
        from agents.cad_agent.ache_assistant import (
            ACHECalculator,
            StructuralDesigner,
            AccessoryDesigner,
            ACHEAssistant,
            ErectionPlanner,
        )
        return ACHECalculator, StructuralDesigner, AccessoryDesigner, ACHEAssistant, ErectionPlanner
    except ImportError as e:
        logger.warning(f"ACHE assistant modules not available: {e}")
        return None, None, None, None, None


class ThermalCalcRequest(BaseModel):
    """Request model for thermal calculations."""
    duty_kw: float
    process_inlet_temp_c: float
    process_outlet_temp_c: float
    air_inlet_temp_c: float
    air_flow_kg_s: float
    surface_area_m2: float
    u_clean_w_m2_k: float = 45.0
    fouling_factor: float = 0.0002


class PressureDropRequest(BaseModel):
    """Request model for pressure drop calculations."""
    mass_flow_kg_s: float
    tube_id_mm: float
    tube_length_m: float
    num_tubes: int
    num_passes: int
    fluid_density_kg_m3: float = 1000.0
    fluid_viscosity_pa_s: float = 0.001


class FanCalcRequest(BaseModel):
    """Request model for fan calculations."""
    air_flow_m3_s: float
    static_pressure_pa: float
    fan_diameter_m: float
    fan_rpm: float
    fan_efficiency: float = 0.75


class ACHESizingRequest(BaseModel):
    """Request model for ACHE sizing."""
    duty_kw: float
    process_inlet_temp_c: float
    process_outlet_temp_c: float
    air_inlet_temp_c: float


class StructuralFrameRequest(BaseModel):
    """Request model for structural frame design."""
    bundle_weight_kn: float
    bundle_length_m: float
    bundle_width_m: float
    bundle_height_m: float
    num_bays: int = 1
    elevation_m: float = 3.0
    wind_speed_m_s: float = 40.0


class AccessSystemRequest(BaseModel):
    """Request model for access system design."""
    bundle_length_m: float
    bundle_width_m: float
    elevation_m: float
    num_bays: int = 1
    fan_deck_required: bool = True
    header_access_required: bool = True


class ComplianceCheckRequest(BaseModel):
    """Request model for API 661 compliance check."""
    ache_properties: Dict[str, Any]


class ErectionPlanRequest(BaseModel):
    """Request model for erection plan."""
    project_name: str
    equipment_tag: str
    ache_properties: Dict[str, Any]


@app.post("/ache/calculate/thermal")
async def calculate_thermal_performance(request: ThermalCalcRequest):
    """
    Calculate ACHE thermal performance.
    Phase 24.4 - Analysis & Calculations
    """
    Calculator, _, _, _, _ = _get_ache_assistant_modules()
    if Calculator is None:
        raise HTTPException(status_code=503, detail="ACHE calculator not available")

    try:
        from agents.cad_agent.ache_assistant import FluidProperties
        calc = Calculator()

        # Create default fluid properties
        fluid = FluidProperties(
            density_kg_m3=1000.0,
            specific_heat_j_kg_k=4186.0,
            viscosity_pa_s=0.001,
            thermal_conductivity_w_m_k=0.6,
            prandtl_number=7.0,
        )

        results = calc.calculate_thermal_performance(
            duty_kw=request.duty_kw,
            process_inlet_temp_c=request.process_inlet_temp_c,
            process_outlet_temp_c=request.process_outlet_temp_c,
            air_inlet_temp_c=request.air_inlet_temp_c,
            air_flow_kg_s=request.air_flow_kg_s,
            surface_area_m2=request.surface_area_m2,
            process_fluid=fluid,
            u_clean_w_m2_k=request.u_clean_w_m2_k,
            fouling_factor=request.fouling_factor,
        )

        return {
            "duty_kw": results.duty_kw,
            "lmtd_k": results.lmtd_k,
            "lmtd_correction_factor": results.lmtd_correction_factor,
            "overall_u_w_m2_k": results.overall_u_w_m2_k,
            "effectiveness": results.effectiveness,
            "ntu": results.ntu,
            "air_outlet_temp_c": results.air_outlet_temp_c,
            "overdesign_percent": results.overdesign_percent,
            "min_approach_temp_c": results.min_approach_temp_c,
            "is_acceptable": results.is_acceptable,
            "warnings": results.warnings,
        }
    except Exception as e:
        logger.error(f"Thermal calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/calculate/fan")
async def calculate_fan_performance(request: FanCalcRequest):
    """
    Calculate fan performance and power.
    Phase 24.4 - Analysis & Calculations
    """
    Calculator, _, _, _, _ = _get_ache_assistant_modules()
    if Calculator is None:
        raise HTTPException(status_code=503, detail="ACHE calculator not available")

    try:
        calc = Calculator()
        results = calc.calculate_fan_performance(
            air_flow_m3_s=request.air_flow_m3_s,
            static_pressure_pa=request.static_pressure_pa,
            fan_diameter_m=request.fan_diameter_m,
            fan_rpm=request.fan_rpm,
            fan_efficiency=request.fan_efficiency,
        )

        return {
            "air_flow_m3_s": results.air_flow_m3_s,
            "air_flow_acfm": results.air_flow_acfm,
            "static_pressure_pa": results.static_pressure_pa,
            "static_pressure_inwg": results.static_pressure_inwg,
            "shaft_power_kw": results.shaft_power_kw,
            "motor_power_kw": results.motor_power_kw,
            "tip_speed_m_s": results.tip_speed_m_s,
            "tip_speed_acceptable": results.tip_speed_acceptable,
            "noise_db_a": results.noise_db_a,
            "warnings": results.warnings,
        }
    except Exception as e:
        logger.error(f"Fan calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/calculate/pressure-drop/tube")
async def calculate_tube_pressure_drop(request: PressureDropRequest):
    """
    Calculate tube-side pressure drop.
    Phase 24.4 - Analysis & Calculations
    """
    Calculator, _, _, _, _ = _get_ache_assistant_modules()
    if Calculator is None:
        raise HTTPException(status_code=503, detail="ACHE calculator not available")

    try:
        from agents.cad_agent.ache_assistant import FluidProperties
        calc = Calculator()

        fluid = FluidProperties(
            density_kg_m3=request.fluid_density_kg_m3,
            specific_heat_j_kg_k=4186.0,
            viscosity_pa_s=request.fluid_viscosity_pa_s,
            thermal_conductivity_w_m_k=0.6,
            prandtl_number=7.0,
        )

        results = calc.calculate_tube_side_pressure_drop(
            mass_flow_kg_s=request.mass_flow_kg_s,
            fluid=fluid,
            tube_id_mm=request.tube_id_mm,
            tube_length_m=request.tube_length_m,
            num_tubes=request.num_tubes,
            num_passes=request.num_passes,
        )

        return {
            "tube_side_dp_kpa": results.tube_side_dp_kpa,
            "tube_friction_dp_kpa": results.tube_friction_dp_kpa,
            "tube_entrance_exit_dp_kpa": results.tube_entrance_exit_dp_kpa,
            "tube_return_bend_dp_kpa": results.tube_return_bend_dp_kpa,
            "is_within_limits": results.is_within_limits,
            "warnings": results.warnings,
        }
    except Exception as e:
        logger.error(f"Pressure drop calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AirPressureDropRequest(BaseModel):
    """Request model for air-side pressure drop."""
    air_flow_kg_s: float
    air_inlet_temp_c: float
    bundle_face_area_m2: float
    tube_od_mm: float = 25.4
    fin_pitch_mm: float = 2.5
    fin_height_mm: float = 12.7
    num_tube_rows: int = 4


@app.post("/ache/calculate/pressure-drop/air")
async def calculate_air_pressure_drop(request: AirPressureDropRequest):
    """
    Calculate air-side pressure drop across tube bundle.
    Phase 24.4 - Analysis & Calculations
    """
    Calculator, _, _, _, _ = _get_ache_assistant_modules()
    if Calculator is None:
        raise HTTPException(status_code=503, detail="ACHE calculator not available")

    try:
        calc = Calculator()

        results = calc.calculate_air_side_pressure_drop(
            air_flow_kg_s=request.air_flow_kg_s,
            air_inlet_temp_c=request.air_inlet_temp_c,
            bundle_face_area_m2=request.bundle_face_area_m2,
            tube_od_mm=request.tube_od_mm,
            fin_pitch_mm=request.fin_pitch_mm,
            fin_height_mm=request.fin_height_mm,
            num_tube_rows=request.num_tube_rows,
        )

        return {
            "air_side_dp_pa": results.air_side_dp_pa,
            "bundle_dp_pa": results.bundle_dp_pa,
            "plenum_dp_pa": results.plenum_dp_pa,
            "is_within_limits": results.is_within_limits,
            "warnings": results.warnings,
        }
    except Exception as e:
        logger.error(f"Air pressure drop calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/calculate/size")
async def size_ache(request: ACHESizingRequest):
    """
    Preliminary ACHE sizing.
    Phase 24.4 - Analysis & Calculations
    """
    Calculator, _, _, _, _ = _get_ache_assistant_modules()
    if Calculator is None:
        raise HTTPException(status_code=503, detail="ACHE calculator not available")

    try:
        from agents.cad_agent.ache_assistant import FluidProperties
        calc = Calculator()

        fluid = FluidProperties(
            density_kg_m3=1000.0,
            specific_heat_j_kg_k=4186.0,
            viscosity_pa_s=0.001,
            thermal_conductivity_w_m_k=0.6,
            prandtl_number=7.0,
        )

        results = calc.size_ache(
            duty_kw=request.duty_kw,
            process_inlet_temp_c=request.process_inlet_temp_c,
            process_outlet_temp_c=request.process_outlet_temp_c,
            air_inlet_temp_c=request.air_inlet_temp_c,
            process_fluid=fluid,
        )

        return results
    except Exception as e:
        logger.error(f"ACHE sizing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/design/frame")
async def design_structural_frame(request: StructuralFrameRequest):
    """
    Design ACHE structural support frame.
    Phase 24.5 - Structural Components
    """
    _, Designer, _, _, _ = _get_ache_assistant_modules()
    if Designer is None:
        raise HTTPException(status_code=503, detail="Structural designer not available")

    try:
        designer = Designer()
        frame = designer.design_ache_frame(
            bundle_weight_kn=request.bundle_weight_kn,
            bundle_length_m=request.bundle_length_m,
            bundle_width_m=request.bundle_width_m,
            bundle_height_m=request.bundle_height_m,
            num_bays=request.num_bays,
            elevation_m=request.elevation_m,
            wind_speed_m_s=request.wind_speed_m_s,
        )

        return {
            "num_columns": frame.num_columns,
            "num_beams": frame.num_beams,
            "total_steel_weight_kg": frame.total_steel_weight_kg,
            "max_utilization": frame.max_utilization,
            "governing_case": frame.governing_case,
            "is_adequate": frame.is_adequate,
            "columns": [
                {
                    "profile": c.profile,
                    "height_m": c.height_m,
                    "utilization": c.utilization_ratio,
                    "is_adequate": c.is_adequate,
                }
                for c in frame.columns[:4]  # Sample
            ],
            "beams": [
                {
                    "profile": b.profile,
                    "span_m": b.span_m,
                    "utilization": b.utilization_ratio,
                    "is_adequate": b.is_adequate,
                }
                for b in frame.beams[:4]  # Sample
            ],
            "warnings": frame.warnings,
        }
    except Exception as e:
        logger.error(f"Frame design error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ColumnDesignRequest(BaseModel):
    """Request model for column design."""
    axial_load_kn: float
    moment_kn_m: float = 0.0
    height_m: float
    k_factor: float = 1.0
    profile_type: str = "HSS_RECT"  # HSS_RECT or W_SHAPE


class BeamDesignRequest(BaseModel):
    """Request model for beam design."""
    span_m: float
    distributed_load_kn_m: float
    point_loads: Optional[List[Dict[str, float]]] = None
    deflection_limit: str = "L/240"
    profile_type: str = "W_SHAPE"


@app.post("/ache/design/column")
async def design_column(request: ColumnDesignRequest):
    """
    Design individual column per AISC.
    Phase 24.5 - Structural Components
    """
    _, Designer, _, _, _ = _get_ache_assistant_modules()
    if Designer is None:
        raise HTTPException(status_code=503, detail="Structural designer not available")

    try:
        from agents.cad_agent.ache_assistant.structural import ProfileType
        designer = Designer()

        profile_type = ProfileType.HSS_RECT if request.profile_type == "HSS_RECT" else ProfileType.W_SHAPE

        column = designer.design_column(
            axial_load_kn=request.axial_load_kn,
            moment_kn_m=request.moment_kn_m,
            height_m=request.height_m,
            k_factor=request.k_factor,
            profile_type=profile_type,
        )

        return {
            "profile": column.profile,
            "profile_type": column.profile_type.value,
            "height_m": column.height_m,
            "area_mm2": column.area_mm2,
            "axial_capacity_kn": column.axial_capacity_kn,
            "moment_capacity_knm": column.moment_capacity_knm,
            "applied_axial_kn": column.applied_axial_kn,
            "applied_moment_knm": column.applied_moment_knm,
            "kl_r": column.kl_r,
            "is_slender": column.is_slender,
            "utilization_ratio": column.utilization_ratio,
            "is_adequate": column.is_adequate,
            "warnings": column.warnings,
        }
    except Exception as e:
        logger.error(f"Column design error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/design/beam")
async def design_beam(request: BeamDesignRequest):
    """
    Design individual beam per AISC.
    Phase 24.5 - Structural Components
    """
    _, Designer, _, _, _ = _get_ache_assistant_modules()
    if Designer is None:
        raise HTTPException(status_code=503, detail="Structural designer not available")

    try:
        from agents.cad_agent.ache_assistant.structural import ProfileType
        designer = Designer()

        profile_type = ProfileType.W_SHAPE if request.profile_type == "W_SHAPE" else ProfileType.HSS_RECT

        # Convert point loads if provided
        point_loads = None
        if request.point_loads:
            point_loads = [(p["position_m"], p["load_kn"]) for p in request.point_loads]

        beam = designer.design_beam(
            span_m=request.span_m,
            distributed_load_kn_m=request.distributed_load_kn_m,
            point_loads=point_loads,
            deflection_limit=request.deflection_limit,
            profile_type=profile_type,
        )

        return {
            "profile": beam.profile,
            "profile_type": beam.profile_type.value,
            "span_m": beam.span_m,
            "area_mm2": beam.area_mm2,
            "moment_capacity_knm": beam.moment_capacity_knm,
            "shear_capacity_kn": beam.shear_capacity_kn,
            "applied_moment_knm": beam.applied_moment_knm,
            "applied_shear_kn": beam.applied_shear_kn,
            "deflection_mm": beam.deflection_mm,
            "deflection_limit_mm": beam.deflection_limit_mm,
            "utilization_ratio": beam.utilization_ratio,
            "is_adequate": beam.is_adequate,
            "warnings": beam.warnings,
        }
    except Exception as e:
        logger.error(f"Beam design error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/design/access")
async def design_access_system(request: AccessSystemRequest):
    """
    Design ACHE access system (platforms, ladders, handrails).
    Phase 24.6 - Walkways/Handrails/Ladders
    """
    _, _, AccessoryDesigner, _, _ = _get_ache_assistant_modules()
    if AccessoryDesigner is None:
        raise HTTPException(status_code=503, detail="Accessory designer not available")

    try:
        designer = AccessoryDesigner()
        bom = designer.design_ache_access_system(
            bundle_length_m=request.bundle_length_m,
            bundle_width_m=request.bundle_width_m,
            elevation_m=request.elevation_m,
            num_bays=request.num_bays,
            fan_deck_required=request.fan_deck_required,
            header_access_required=request.header_access_required,
        )

        return {
            "total_grating_m2": bom.total_grating_m2,
            "total_steel_kg": bom.total_steel_kg,
            "platforms": [
                {
                    "type": p["type"],
                    "quantity": p["quantity"],
                    "length_m": p["length_m"],
                    "width_m": p["width_m"],
                }
                for p in bom.platforms
            ],
            "ladders": [
                {
                    "type": l["type"],
                    "quantity": l["quantity"],
                    "height_m": l["height_m"],
                }
                for l in bom.ladders
            ],
            "handrails": [
                {
                    "type": h["type"],
                    "quantity": h["quantity"],
                    "length_m": h["length_m"],
                }
                for h in bom.handrails
            ],
            "bom_items": bom.items,
        }
    except Exception as e:
        logger.error(f"Access system design error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/compliance/check")
async def check_api661_compliance(request: ComplianceCheckRequest):
    """
    Check ACHE design against API 661 requirements.
    Phase 24.7 - AI Features
    """
    _, _, _, Assistant, _ = _get_ache_assistant_modules()
    if Assistant is None:
        raise HTTPException(status_code=503, detail="ACHE assistant not available")

    try:
        assistant = Assistant()
        report = assistant.check_api661_compliance(request.ache_properties)

        return {
            "standard": report.standard,
            "is_compliant": report.is_compliant,
            "total_checks": report.total_checks,
            "passed": report.passed,
            "failed": report.failed,
            "warnings": report.warnings,
            "summary": report.summary,
            "issues": [
                {
                    "code_reference": i.code_reference,
                    "requirement": i.requirement,
                    "actual_value": str(i.actual_value),
                    "required_value": str(i.required_value),
                    "status": i.status.value,
                    "severity": i.severity,
                    "recommendation": i.recommendation,
                }
                for i in report.issues
            ],
        }
    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/ai/recommendations")
async def get_design_recommendations(request: ComplianceCheckRequest):
    """
    Get AI-powered design recommendations.
    Phase 24.7 - AI Features
    """
    _, _, _, Assistant, _ = _get_ache_assistant_modules()
    if Assistant is None:
        raise HTTPException(status_code=503, detail="ACHE assistant not available")

    try:
        assistant = Assistant()
        recommendations = assistant.get_design_recommendations(request.ache_properties)

        return {
            "recommendations": [
                {
                    "category": r.category,
                    "recommendation": r.recommendation,
                    "rationale": r.rationale,
                    "impact": r.impact,
                    "references": r.references,
                    "alternatives": r.alternatives,
                }
                for r in recommendations
            ]
        }
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ache/ai/troubleshoot/{problem}")
async def troubleshoot_problem(problem: str):
    """
    Get troubleshooting guidance for ACHE issues.
    Phase 24.7 - AI Features
    """
    _, _, _, Assistant, _ = _get_ache_assistant_modules()
    if Assistant is None:
        raise HTTPException(status_code=503, detail="ACHE assistant not available")

    try:
        assistant = Assistant()
        result = assistant.troubleshoot(problem)
        return result
    except Exception as e:
        logger.error(f"Troubleshooting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ache/ai/knowledge")
async def query_knowledge_base(query: str, category: Optional[str] = None):
    """
    Query ACHE knowledge base.
    Phase 24.7 - AI Features
    """
    _, _, _, Assistant, _ = _get_ache_assistant_modules()
    if Assistant is None:
        raise HTTPException(status_code=503, detail="ACHE assistant not available")

    try:
        assistant = Assistant()
        result = assistant.query_knowledge_base(query, category)
        return result
    except Exception as e:
        logger.error(f"Knowledge query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/erection/plan")
async def create_erection_plan(request: ErectionPlanRequest):
    """
    Create complete erection plan for ACHE.
    Phase 24.8 - Field Erection Support
    """
    _, _, _, _, Planner = _get_ache_assistant_modules()
    if Planner is None:
        raise HTTPException(status_code=503, detail="Erection planner not available")

    try:
        planner = Planner()
        plan = planner.create_erection_plan(
            project_name=request.project_name,
            equipment_tag=request.equipment_tag,
            ache_properties=request.ache_properties,
        )

        return {
            "project_name": plan.project_name,
            "equipment_tag": plan.equipment_tag,
            "total_weight_kg": plan.total_weight_kg,
            "shipment_type": plan.shipment_type.value,
            "is_feasible": plan.is_feasible,
            "total_lift_hours": plan.total_lift_hours,
            "crane_days": plan.crane_days,
            "lifting_lugs": [
                {
                    "location": lug.location,
                    "design_load_kn": lug.design_load_kn,
                    "plate_thickness_mm": lug.plate_thickness_mm,
                    "hole_diameter_mm": lug.hole_diameter_mm,
                    "utilization": lug.utilization,
                    "is_adequate": lug.is_adequate,
                }
                for lug in plan.lifting_lugs
            ],
            "rigging_plan": {
                "num_slings": plan.rigging_plan.num_slings if plan.rigging_plan else 0,
                "sling_diameter_mm": plan.rigging_plan.sling_diameter_mm if plan.rigging_plan else 0,
                "crane_capacity_tonnes": plan.rigging_plan.crane_capacity_tonnes if plan.rigging_plan else 0,
                "needs_spreader": plan.rigging_plan.needs_spreader if plan.rigging_plan else False,
            } if plan.rigging_plan else None,
            "shipping_splits": [
                {
                    "split_id": s.split_id,
                    "location_mm": s.location_mm,
                    "description": s.description,
                    "requires_permit": s.requires_permit,
                }
                for s in plan.shipping_splits
            ],
            "erection_sequence": [
                {
                    "step": step.step_number,
                    "description": step.description,
                    "weight_kg": step.weight_kg,
                    "crane": step.crane_required,
                    "duration_hours": step.duration_hours,
                    "safety_notes": step.safety_notes,
                }
                for step in plan.erection_sequence
            ],
            "warnings": plan.warnings,
        }
    except Exception as e:
        logger.error(f"Erection plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/erection/lifting-lug")
async def design_lifting_lug(design_load_kn: float, sling_angle_deg: float = 60.0):
    """
    Design individual lifting lug.
    Phase 24.8 - Field Erection Support
    """
    _, _, _, _, Planner = _get_ache_assistant_modules()
    if Planner is None:
        raise HTTPException(status_code=503, detail="Erection planner not available")

    try:
        planner = Planner()
        lug = planner.design_lifting_lug(
            design_load_kn=design_load_kn,
            sling_angle_deg=sling_angle_deg,
        )

        return {
            "design_load_kn": lug.design_load_kn,
            "total_design_load_kn": lug.total_design_load_kn,
            "hole_diameter_mm": lug.hole_diameter_mm,
            "plate_thickness_mm": lug.plate_thickness_mm,
            "plate_width_mm": lug.plate_width_mm,
            "plate_height_mm": lug.plate_height_mm,
            "weld_size_mm": lug.weld_size_mm,
            "bearing_capacity_kn": lug.bearing_capacity_kn,
            "tearout_capacity_kn": lug.tearout_capacity_kn,
            "tension_capacity_kn": lug.tension_capacity_kn,
            "weld_capacity_kn": lug.weld_capacity_kn,
            "utilization": lug.utilization,
            "is_adequate": lug.is_adequate,
            "warnings": lug.warnings,
        }
    except Exception as e:
        logger.error(f"Lifting lug design error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class BatchFanCalcRequest(BaseModel):
    """Request for batch fan calculations."""
    calculations: List[FanCalcRequest]


@app.post("/ache/calculate/batch/fan")
async def calculate_batch_fan(request: BatchFanCalcRequest):
    """
    Batch calculate fan performance for multiple configurations.
    Phase 24.4 - Engineering Calculations
    """
    Calculator = _get_ache_assistant_modules()[0]
    if Calculator is None:
        raise HTTPException(status_code=503, detail="ACHE calculator not available")

    try:
        calc = Calculator()
        results = []

        for calc_request in request.calculations:
            result = calc.calculate_fan_performance(
                air_flow_m3_s=calc_request.air_flow_m3_s,
                static_pressure_pa=calc_request.static_pressure_pa,
                fan_diameter_m=calc_request.fan_diameter_m,
                fan_rpm=calc_request.fan_rpm,
                fan_efficiency=calc_request.fan_efficiency,
            )
            results.append({
                "air_flow_m3_s": result.air_flow_m3_s,
                "static_pressure_pa": result.static_pressure_pa,
                "shaft_power_kw": result.shaft_power_kw,
                "motor_power_kw": result.motor_power_kw,
                "tip_speed_m_s": result.tip_speed_m_s,
                "tip_speed_acceptable": result.tip_speed_acceptable,
                "warnings": result.warnings,
            })

        return {
            "total_calculations": len(results),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Batch fan calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/export/datasheet")
async def export_ache_datasheet(ache_properties: Dict[str, Any], format: str = "json"):
    """
    Export ACHE design data to various formats.
    Phase 24.9 - Export Features
    """
    try:
        datasheet = {
            "document_type": "ACHE Datasheet",
            "standard": "API 661 / ISO 13706",
            "generated_at": datetime.now().isoformat(),
            "equipment_data": ache_properties,
            "sections": {
                "general": {
                    "equipment_tag": ache_properties.get("equipment_tag", "TBD"),
                    "service": ache_properties.get("service", "TBD"),
                    "design_code": "API 661",
                },
                "thermal": ache_properties.get("thermal", {}),
                "mechanical": ache_properties.get("mechanical", {}),
                "fan_system": ache_properties.get("fan_system", {}),
                "structural": ache_properties.get("structural", {}),
            },
        }

        if format == "json":
            return datasheet
        else:
            return {"error": f"Format '{format}' not yet supported", "supported": ["json"]}

    except Exception as e:
        logger.error(f"Export datasheet error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ache/export/bom")
async def export_ache_bom(ache_properties: Dict[str, Any]):
    """
    Generate Bill of Materials for ACHE.
    Phase 24.9 - Export Features
    """
    try:
        # Generate BOM from properties
        bom_items = []

        # Tube bundle items
        if "tube_bundle" in ache_properties:
            bundle = ache_properties["tube_bundle"]
            bom_items.append({
                "item": 1,
                "component": "Finned Tubes",
                "description": f"{bundle.get('tube_od_mm', 25.4)}mm OD x {bundle.get('tube_length_m', 6)}m",
                "quantity": bundle.get("num_tubes", 0),
                "unit": "EA",
                "material": bundle.get("tube_material", "A179"),
            })

        # Fan system items
        if "fan_system" in ache_properties:
            fan = ache_properties["fan_system"]
            bom_items.append({
                "item": len(bom_items) + 1,
                "component": "Axial Fan",
                "description": f"{fan.get('fan_diameter_m', 3.0)}m diameter",
                "quantity": fan.get("num_fans", 1),
                "unit": "EA",
                "material": "Aluminum",
            })

        return {
            "document_type": "Bill of Materials",
            "equipment_tag": ache_properties.get("equipment_tag", "TBD"),
            "generated_at": datetime.now().isoformat(),
            "total_items": len(bom_items),
            "items": bom_items,
        }
    except Exception as e:
        logger.error(f"Export BOM error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ache/standards/api661")
async def get_api661_reference():
    """
    Get API 661 quick reference data.
    Phase 24.7 - Standards Reference
    """
    return {
        "standard": "API 661 / ISO 13706",
        "edition": "7th Edition (2013)",
        "key_requirements": {
            "tube_bundle": {
                "max_tube_length_m": 12.0,
                "min_tube_wall_mm": 2.11,
                "reference": "5.1.1, 5.1.3",
            },
            "fan_system": {
                "max_tip_speed_m_s": 61.0,
                "min_blade_clearance_mm": 12.7,
                "reference": "6.1.1, Table 6",
            },
            "header": {
                "split_required_delta_t_c": 110,
                "reference": "7.1.6.1.2",
            },
            "air_side": {
                "max_pressure_drop_pa": 250,
                "reference": "6.2.1",
            },
        },
        "material_codes": {
            "tubes": ["A179", "A214", "A334-1", "A334-6"],
            "headers": ["SA516-70", "SA285-C", "SA516-60"],
            "fins": ["Aluminum 1100", "Aluminum 3003"],
        },
    }


# =============================================================================
# Data Hub Endpoints - Unified Standards, Components, Rules, Templates
# =============================================================================

# Import data hub components
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))
    from data_hub import (
        get_standards_hub,
        ComponentLookup,
        RulesEngine,
        TemplateEngine,
    )
    DATA_HUB_AVAILABLE = True
except ImportError:
    DATA_HUB_AVAILABLE = False
    logger.warning("Data Hub components not available")


class StandardsSearchRequest(BaseModel):
    """Request model for standards search."""
    query: str
    standard: Optional[str] = None
    category: Optional[str] = None
    limit: int = 20


class ComponentSearchRequest(BaseModel):
    """Request model for component search."""
    query: str
    category: Optional[str] = None
    fuzzy: bool = False


class RulesEvaluationRequest(BaseModel):
    """Request model for rules evaluation."""
    data: Dict[str, Any]
    standard: Optional[str] = None
    tags: Optional[List[str]] = None


class ReportRenderRequest(BaseModel):
    """Request model for report rendering."""
    template_id: str
    data: Dict[str, Any]
    format: Optional[str] = None


@app.get("/data-hub/status")
async def get_data_hub_status():
    """Get data hub availability and statistics."""
    if not DATA_HUB_AVAILABLE:
        return {"available": False, "error": "Data Hub not loaded"}

    try:
        hub = get_standards_hub()
        components = ComponentLookup()
        rules = RulesEngine()
        templates = TemplateEngine()

        return {
            "available": True,
            "standards_hub": hub.to_dict(),
            "components": {
                "beams": len(components.list_beams()),
                "bolts": len(components.list_bolts()),
                "materials": len(components.list_materials()),
                "pipes": len(components.list_pipe_sizes()),
            },
            "rules": rules.get_summary(),
            "templates": templates.list_templates(),
        }
    except Exception as e:
        logger.error(f"Data hub status error: {e}")
        return {"available": False, "error": str(e)}


@app.post("/data-hub/search")
async def search_standards(request: StandardsSearchRequest):
    """Search standards database."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        results = hub.search(
            query=request.query,
            standard=request.standard,
            category=request.category,
            limit=request.limit
        )
        return {
            "query": request.query,
            "count": len(results),
            "results": [
                {
                    "standard": r.standard,
                    "category": r.category,
                    "designation": r.designation,
                    "properties": r.properties,
                    "reference": r.reference,
                    "score": r.relevance_score,
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Standards search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/beam/{designation}")
async def get_beam(designation: str):
    """Get beam properties by designation."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        beam = hub.get_beam(designation)
        if beam:
            return {"designation": designation, "properties": beam}
        raise HTTPException(status_code=404, detail=f"Beam {designation} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/bolt/{size}")
async def get_bolt(size: str):
    """Get bolt properties by size."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        bolt = hub.get_bolt(size)
        if bolt:
            return {"size": size, "properties": bolt}
        raise HTTPException(status_code=404, detail=f"Bolt {size} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/material/{grade}")
async def get_material(grade: str):
    """Get material properties by grade."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        material = hub.get_material(grade)
        if material:
            return {"grade": grade, "properties": material}
        raise HTTPException(status_code=404, detail=f"Material {grade} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/pipe/{nps}")
async def get_pipe(nps: str, schedule: str = "40"):
    """Get pipe dimensions by NPS and schedule."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        pipe = hub.get_pipe(nps, schedule)
        if pipe:
            return pipe
        raise HTTPException(status_code=404, detail=f"Pipe NPS {nps} Sch {schedule} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/data-hub/components/search")
async def search_components(request: ComponentSearchRequest):
    """Search component database."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        lookup = ComponentLookup()
        if request.fuzzy:
            results = lookup.fuzzy_search(request.query)
        else:
            results = lookup.search(request.query, request.category)

        return {
            "query": request.query,
            "fuzzy": request.fuzzy,
            "count": len(results),
            "results": [r.to_dict() for r in results]
        }
    except Exception as e:
        logger.error(f"Component search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/components/weight")
async def calculate_weight(designation: str, length_ft: float):
    """Calculate component weight."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        lookup = ComponentLookup()
        result = lookup.calculate_beam_weight(designation, length_ft)
        if result:
            return result
        raise HTTPException(status_code=404, detail=f"Component {designation} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/rules")
async def list_rules(standard: Optional[str] = None, tag: Optional[str] = None):
    """List available validation rules."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        engine = RulesEngine()
        if standard:
            rules = engine.get_rules_by_standard(standard)
        elif tag:
            rules = engine.get_rules_by_tag(tag)
        else:
            rules = list(engine._rules.values())

        return {
            "count": len(rules),
            "standards": engine.list_standards(),
            "tags": engine.list_tags(),
            "rules": [r.to_dict() for r in rules[:50]]  # Limit to 50
        }
    except Exception as e:
        logger.error(f"Rules listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/data-hub/rules/evaluate")
async def evaluate_rules(request: RulesEvaluationRequest):
    """Evaluate validation rules against data."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        engine = RulesEngine()
        violations = engine.evaluate(
            data=request.data,
            standard=request.standard,
            tags=request.tags
        )

        return {
            "evaluated": True,
            "data_keys": list(request.data.keys()),
            "violations_count": len(violations),
            "violations": [v.to_dict() for v in violations]
        }
    except Exception as e:
        logger.error(f"Rules evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/templates")
async def list_templates():
    """List available report templates."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        engine = TemplateEngine()
        return {"templates": engine.list_templates()}
    except Exception as e:
        logger.error(f"Template listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/data-hub/templates/render")
async def render_template(request: ReportRenderRequest):
    """Render a report template with data."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        engine = TemplateEngine()

        # Parse format if provided
        from data_hub.template_engine import OutputFormat
        fmt = None
        if request.format:
            try:
                fmt = OutputFormat(request.format.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid format: {request.format}")

        output = engine.render(request.template_id, request.data, fmt)

        return {
            "template_id": request.template_id,
            "format": request.format or "html",
            "content": output
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Template render error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/validate/bolt-spacing")
async def validate_bolt_spacing(bolt_size: str, spacing: float):
    """Validate bolt spacing per AISC J3.3."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        result = hub.validate_bolt_spacing(bolt_size, spacing)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/validate/edge-distance")
async def validate_edge_distance(bolt_size: str, edge_dist: float, edge_type: str = "rolled"):
    """Validate edge distance per AISC J3.4."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        result = hub.validate_edge_distance(bolt_size, edge_dist, edge_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data-hub/weld/minimum-fillet")
async def get_minimum_fillet_weld(thickness: float):
    """Get minimum fillet weld size per AWS D1.1."""
    if not DATA_HUB_AVAILABLE:
        raise HTTPException(status_code=501, detail="Data Hub not available")

    try:
        hub = get_standards_hub()
        result = hub.get_minimum_fillet_weld(thickness)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # Get host - prefer Tailscale IP, fallback to localhost
    tailscale_ip = get_tailscale_ip()
    host = tailscale_ip or "127.0.0.1"
    port = int(os.environ.get("PORT", 8000))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run("server:app", host=host, port=port, reload=False, log_level="info")
