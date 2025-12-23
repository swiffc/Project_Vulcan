"""
SolidWorks COM Adapter - Thin wrapper around SolidWorks COM API
~100 lines as per RULES.md

Requires: SolidWorks installed and licensed on the machine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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

class LinearPatternRequest(BaseModel):
    count_x: int = 1
    count_y: int = 1
    spacing_x: float = 0.01  # meters
    spacing_y: float = 0.01  # meters

class FilletRequest(BaseModel):
    radius: float  # meters

class DimensionRequest(BaseModel):
    value: float  # meters

class SaveRequest(BaseModel):
    filepath: str

class OpenRequest(BaseModel):
    filepath: str

class ExportRequest(BaseModel):
    filepath: str
    format: str  # "step", "iges", "stl", "pdf", etc.


class LineRequest(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class ExtrudeCutRequest(BaseModel):
    depth: float  # Use 999 for "Through All"


class ChamferRequest(BaseModel):
    distance: float
    angle: float = 45.0


class SelectRequest(BaseModel):
    x: float
    y: float
    z: float


class ViewRequest(BaseModel):
    view: str = "isometric"  # front, back, top, bottom, left, right, isometric, trimetric

class LoftRequest(BaseModel):
    profiles: List[str]  # List of sketch names or indices
    guide_curves: Optional[List[str]] = None

class SweepRequest(BaseModel):
    profile: str  # Profile sketch name
    path: str  # Path sketch name

class ShellRequest(BaseModel):
    thickness: float  # meters
    faces_to_remove: Optional[List[str]] = None

class MirrorRequest(BaseModel):
    plane: str  # "Front", "Top", "Right", or custom plane name
    features: Optional[List[str]] = None  # Feature names to mirror


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
    model.FeatureManager.FeatureCircularPattern4(
        req.count, req.spacing, True, "Y Axis", False, False
    )
    return {"status": "ok", "count": req.count}


@router.post("/pattern_linear")
async def pattern_linear(req: LinearPatternRequest):
    """Create a linear pattern of the last feature."""
    logger.info(f"Linear pattern: {req.count_x}x{req.count_y}")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")
    model.FeatureManager.FeatureLinearPattern4(
        req.count_x, req.spacing_x, req.count_y, req.spacing_y,
        True, True, "X Axis", "Y Axis", False, False
    )
    return {"status": "ok", "count_x": req.count_x, "count_y": req.count_y}


@router.post("/fillet")
async def fillet(req: FilletRequest):
    """Apply fillet to selected edges."""
    logger.info(f"Fillet radius={req.radius}")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")
    model.FeatureManager.FeatureFillet3(
        195, req.radius, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    )
    return {"status": "ok", "radius": req.radius}


@router.post("/add_dimension")
async def add_dimension(req: DimensionRequest):
    """Add a dimension to selected sketch entity."""
    logger.info(f"Adding dimension: {req.value}")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")
    model.AddDimension2(0, 0, 0)
    dim = model.IGetLastFeature()
    if dim:
        dim.SystemValue = req.value
    return {"status": "ok", "value": req.value}


@router.post("/open")
async def open_document(req: OpenRequest):
    """Open an existing SolidWorks document."""
    logger.info(f"Opening document: {req.filepath}")
    global _sw_model
    app = get_app()

    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {req.filepath}")

    # Determine document type
    if req.filepath.endswith('.sldprt'):
        doc_type = 1  # swDocPART
    elif req.filepath.endswith('.sldasm'):
        doc_type = 2  # swDocASSEMBLY
    elif req.filepath.endswith('.slddrw'):
        doc_type = 3  # swDocDRAWING
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

    _sw_model = app.OpenDoc6(
        req.filepath,
        doc_type,
        0,  # swOpenDocOptions_Silent
        "",
        errors,
        warnings
    )

    if not _sw_model:
        raise HTTPException(status_code=400, detail="Failed to open document")

    return {
        "status": "ok",
        "filepath": req.filepath,
        "document_type": "part" if doc_type == 1 else "assembly" if doc_type == 2 else "drawing"
    }


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


@router.post("/export")
async def export_document(req: ExportRequest):
    """Export the current document to another format."""
    logger.info(f"Exporting to {req.format}: {req.filepath}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Format mapping for SolidWorks
    format_map = {
        "step": 6,    # swSaveAsVersion_STEP214
        "iges": 5,    # swSaveAsVersion_IGES
        "stl": 7,     # swSaveAsVersion_STL
        "pdf": 1,     # swSaveAsVersion_PDF
        "dwg": 2,     # swSaveAsVersion_DWG
        "dxf": 3,     # swSaveAsVersion_DXF
    }

    format_type = format_map.get(req.format.lower())
    if not format_type:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {req.format}")

    errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

    # Export
    model.Extension.SaveAs(req.filepath, format_type, 0, None, errors, warnings)

    return {"status": "ok", "filepath": req.filepath, "format": req.format}


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


@router.post("/draw_line")
async def draw_line(req: LineRequest):
    """Draw a line in the active sketch."""
    logger.info(f"Drawing line from ({req.x1}, {req.y1}) to ({req.x2}, {req.y2})")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.SketchManager.CreateLine(req.x1, req.y1, 0, req.x2, req.y2, 0)
    return {"status": "ok"}


@router.post("/extrude_cut")
async def extrude_cut(req: ExtrudeCutRequest):
    """Extrude cut to remove material."""
    logger.info(f"Extrude cut depth={req.depth}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # End condition: 0=Blind, 1=Through All
    end_cond = 1 if req.depth >= 999 else 0
    actual_depth = 0 if end_cond == 1 else req.depth

    feature = model.FeatureManager.FeatureCut3(
        True, False, False,  # Sd, Flip, Dir
        end_cond, 0,  # T1, T2
        actual_depth, 0,  # D1, D2
        False, False, False, False,  # Draft options
        0, 0,  # Draft angles
        False, False, False, False,  # Offset options
        False, True, True,  # NormalCut, UseFeatScope, UseAutoSelect
        False, 0, 0, False  # AssemblyFeatureScope options
    )

    return {"status": "ok", "depth": req.depth, "through_all": end_cond == 1}


@router.post("/chamfer")
async def chamfer(req: ChamferRequest):
    """Apply chamfer to selected edges."""
    logger.info(f"Chamfer distance={req.distance}, angle={req.angle}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    import math
    angle_rad = math.radians(req.angle)

    model.FeatureManager.InsertFeatureChamfer(
        4,  # Type: Distance-Angle
        1,  # Options
        req.distance,
        angle_rad,
        0, 0, 0, 0  # Other parameters
    )

    return {"status": "ok", "distance": req.distance, "angle": req.angle}


@router.post("/select_face")
async def select_face(req: SelectRequest):
    """Select a face at the given coordinates."""
    logger.info(f"Selecting face at ({req.x}, {req.y}, {req.z})")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    result = model.Extension.SelectByID2("", "FACE", req.x, req.y, req.z, False, 0, None, 0)
    return {"status": "ok", "selected": result}


@router.post("/select_edge")
async def select_edge(req: SelectRequest):
    """Select an edge at the given coordinates."""
    logger.info(f"Selecting edge at ({req.x}, {req.y}, {req.z})")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    result = model.Extension.SelectByID2("", "EDGE", req.x, req.y, req.z, False, 0, None, 0)
    return {"status": "ok", "selected": result}


@router.post("/clear_selection")
async def clear_selection():
    """Clear all selections."""
    logger.info("Clearing selection")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.ClearSelection2(True)
    return {"status": "ok"}


@router.post("/zoom_fit")
async def zoom_fit():
    """Zoom to fit all geometry."""
    logger.info("Zoom to fit")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.ViewZoomtofit2()
    return {"status": "ok"}


@router.post("/set_view")
async def set_view(req: ViewRequest):
    """Set the view orientation."""
    logger.info(f"Setting view to {req.view}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # SolidWorks view constants
    view_map = {
        "front": 1,      # swFrontView
        "back": 2,       # swBackView
        "left": 3,       # swLeftView
        "right": 4,      # swRightView
        "top": 5,        # swTopView
        "bottom": 6,     # swBottomView
        "isometric": 7,  # swIsometricView
        "trimetric": 8,  # swTrimetricView
    }

    view_const = view_map.get(req.view.lower(), 7)
    model.ShowNamedView2("", view_const)
    model.ViewZoomtofit2()

    return {"status": "ok", "view": req.view}


@router.post("/loft")
async def loft(req: LoftRequest):
    """Create a loft feature between multiple profiles."""
    logger.info(f"Creating loft with {len(req.profiles)} profiles")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Get sketches for profiles
    feature_mgr = model.FeatureManager
    
    # Select profiles
    for i, profile_name in enumerate(req.profiles):
        model.Extension.SelectByID2(profile_name, "SKETCH", 0, 0, 0, i > 0, 0, None, 0)

    # Create loft
    guide_curves = req.guide_curves if req.guide_curves else []
    
    feature = feature_mgr.FeatureLoft2(
        False, None, guide_curves, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0
    )

    return {"status": "ok", "profiles": len(req.profiles)}


@router.post("/sweep")
async def sweep(req: SweepRequest):
    """Create a sweep feature along a path."""
    logger.info(f"Creating sweep: profile={req.profile}, path={req.path}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Select profile and path sketches
    model.Extension.SelectByID2(req.profile, "SKETCH", 0, 0, 0, False, 0, None, 0)
    model.Extension.SelectByID2(req.path, "SKETCH", 0, 0, 0, True, 0, None, 0)

    # Create sweep
    feature_mgr = model.FeatureManager
    feature = feature_mgr.FeatureSweep2(
        False, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    )

    return {"status": "ok"}


@router.post("/shell")
async def shell(req: ShellRequest):
    """Create a shell feature."""
    logger.info(f"Creating shell: thickness={req.thickness}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Select faces to remove if specified
    if req.faces_to_remove:
        for face_name in req.faces_to_remove:
            model.Extension.SelectByID2(face_name, "FACE", 0, 0, 0, True, 0, None, 0)

    # Create shell
    feature_mgr = model.FeatureManager
    feature = feature_mgr.FeatureShell2(
        req.thickness,
        0,
        len(req.faces_to_remove) if req.faces_to_remove else 0,
        False,
        req.faces_to_remove is None or len(req.faces_to_remove) == 0
    )

    return {"status": "ok", "thickness": req.thickness}


@router.post("/mirror")
async def mirror(req: MirrorRequest):
    """Mirror features or bodies."""
    logger.info(f"Creating mirror: plane={req.plane}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Select mirror plane
    plane_name = f"{req.plane} Plane" if req.plane in ["Front", "Top", "Right"] else req.plane
    model.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, None, 0)

    # Select features to mirror if specified
    if req.features:
        for feature_name in req.features:
            model.Extension.SelectByID2(feature_name, "BODYFEATURE", 0, 0, 0, True, 0, None, 0)

    # Create mirror
    feature_mgr = model.FeatureManager
    feature = feature_mgr.FeatureMirror2(
        0, True, False, False, False, False,
        req.features is None or len(req.features) == 0,
        req.features is None or len(req.features) == 0,
        False
    )

    return {"status": "ok", "plane": req.plane}
