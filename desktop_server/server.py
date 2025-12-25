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
