"""
SolidWorks COM Adapter - Thin wrapper around SolidWorks COM API
~100 lines as per RULES.md

Requires: SolidWorks installed and licensed on the machine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import win32com.client
import pythoncom
import logging
import os

router = APIRouter(prefix="/com/solidworks", tags=["solidworks"])
logger = logging.getLogger(__name__)

# Global SolidWorks application reference
_sw_app = None
_sw_model = None


class SketchRequest(BaseModel):
    plane: str = "Front"  # Front, Top, Right

class CircleRequest(BaseModel):
    x: float  # Center X (meters)
    y: float  # Center Y (meters)
    radius: float  # Radius (meters)

class RectangleRequest(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class ExtrudeRequest(BaseModel):
    depth: float  # Depth in meters
    direction: int = 0  # 0=one direction, 1=both

class RevolveRequest(BaseModel):
    angle: float = 360.0  # Degrees

class PatternRequest(BaseModel):
    count: int
    spacing: float  # Radians for circular, meters for linear

class SaveRequest(BaseModel):
    filepath: str


def get_app():
    """Get or create SolidWorks application instance."""
    global _sw_app
    if _sw_app is None:
        pythoncom.CoInitialize()
        try:
            _sw_app = win32com.client.Dispatch("SldWorks.Application")
            _sw_app.Visible = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not connect to SolidWorks: {e}")
    return _sw_app


@router.post("/connect")
async def connect():
    """Connect to running SolidWorks instance."""
    logger.info("Connecting to SolidWorks")
    app = get_app()
    return {"status": "ok", "version": app.RevisionNumber()}


@router.post("/new_part")
async def new_part():
    """Create a new part document."""
    global _sw_model
    logger.info("Creating new SolidWorks part")
    app = get_app()

    # Find part template
    template_path = app.GetUserPreferenceStringValue(21)  # swDefaultTemplatePart
    if not template_path or not os.path.exists(template_path):
        # Fallback to common paths
        common_paths = [
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Part.prtdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2023\templates\Part.prtdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2022\templates\Part.prtdot",
        ]
        for path in common_paths:
            if os.path.exists(path):
                template_path = path
                break

    _sw_model = app.NewDocument(template_path, 0, 0, 0)
    return {"status": "ok", "document_type": "part"}


@router.post("/create_sketch")
async def create_sketch(req: SketchRequest):
    """Start a new sketch on the specified plane."""
    global _sw_model
    logger.info(f"Creating sketch on {req.plane} plane")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Select the plane
    plane_name = f"{req.plane} Plane"
    model.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, None, 0)
    model.SketchManager.InsertSketch(True)

    return {"status": "ok", "plane": req.plane}


@router.post("/draw_circle")
async def draw_circle(req: CircleRequest):
    """Draw a circle in the active sketch."""
    logger.info(f"Drawing circle at ({req.x}, {req.y}) r={req.radius}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Create circle (x, y, z of center, x, y, z of point on circle)
    model.SketchManager.CreateCircle(req.x, req.y, 0, req.x + req.radius, req.y, 0)

    return {"status": "ok", "center": {"x": req.x, "y": req.y}, "radius": req.radius}


@router.post("/draw_rectangle")
async def draw_rectangle(req: RectangleRequest):
    """Draw a rectangle in the active sketch."""
    logger.info(f"Drawing rectangle from ({req.x1}, {req.y1}) to ({req.x2}, {req.y2})")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.SketchManager.CreateCornerRectangle(req.x1, req.y1, 0, req.x2, req.y2, 0)

    return {"status": "ok"}


@router.post("/close_sketch")
async def close_sketch():
    """Close the active sketch."""
    logger.info("Closing sketch")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.SketchManager.InsertSketch(True)
    return {"status": "ok"}


@router.post("/extrude")
async def extrude(req: ExtrudeRequest):
    """Extrude the current sketch."""
    logger.info(f"Extruding depth={req.depth}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # FeatureExtrusion2 parameters:
    # (Sd, Flip, Dir, T1, T2, D1, D2, Dchk1, Dchk2, Ddir1, Ddir2, Dang1, Dang2, OffsetReverse1, OffsetReverse2, TranslateSurface1, TranslateSurface2, Merge, UseFeatScope, UseAutoSelect, T0, StartOffset, FlipStartOffset)
    feature = model.FeatureManager.FeatureExtrusion2(
        True, False, False,  # Sd, Flip, Dir
        0, 0,  # T1, T2 (end conditions: 0=blind)
        req.depth, 0,  # D1, D2 (depths)
        False, False, False, False,  # Draft options
        0, 0,  # Draft angles
        False, False, False, False,  # Offset options
        True, True, True,  # Merge, UseFeatScope, UseAutoSelect
        0, 0, False  # T0, StartOffset, FlipStartOffset
    )

    return {"status": "ok", "depth": req.depth}


@router.post("/revolve")
async def revolve(req: RevolveRequest):
    """Revolve the current sketch."""
    logger.info(f"Revolving angle={req.angle}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    import math
    angle_rad = math.radians(req.angle)

    feature = model.FeatureManager.FeatureRevolve2(
        True, True, False,  # SingleDir, IsSolid, IsThin
        False, False, False,  # Merge, UseFeatScope, UseAutoSelect
        0, 0,  # Type1, Type2
        angle_rad, 0,  # Angle1, Angle2
        False, False,  # OffsetReverse1, OffsetReverse2
        0, 0, 0,  # ThinWallType, Thickness1, Thickness2
        True  # UseDefaultThinWallType
    )

    return {"status": "ok", "angle": req.angle}


@router.post("/pattern_circular")
async def pattern_circular(req: PatternRequest):
    """Create a circular pattern of the last feature."""
    logger.info(f"Circular pattern: count={req.count}, spacing={req.spacing}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    import math

    # Create circular pattern
    # This is simplified - would need proper feature selection
    feature = model.FeatureManager.FeatureCircularPattern4(
        req.count,  # Number of instances
        req.spacing,  # Spacing angle in radians
        True,  # Equal spacing
        "Y Axis",  # Axis
        False, False  # Geometry pattern, propagate
    )

    return {"status": "ok", "count": req.count}


@router.post("/save")
async def save(req: SaveRequest):
    """Save the current document."""
    logger.info(f"Saving to {req.filepath}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Ensure directory exists
    os.makedirs(os.path.dirname(req.filepath), exist_ok=True)

    errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    model.Extension.SaveAs(req.filepath, 0, 0, None, errors, warnings)

    return {"status": "ok", "filepath": req.filepath}


@router.get("/status")
async def status():
    """Get SolidWorks status."""
    try:
        app = get_app()
        model = app.ActiveDoc
        return {
            "connected": True,
            "version": app.RevisionNumber(),
            "has_document": model is not None,
            "document_name": model.GetTitle() if model else None
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
