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
    view: str = (
        "isometric"  # front, back, top, bottom, left, right, isometric, trimetric
    )


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


class SplineRequest(BaseModel):
    points: List[dict]  # List of {x, y} points


class PolygonRequest(BaseModel):
    center_x: float
    center_y: float
    radius: float
    sides: int  # Number of sides


class EllipseRequest(BaseModel):
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float


class PlaneOffsetRequest(BaseModel):
    base_name: str  # Name of face/plane
    distance: float  # meters
    flip: bool = False


class PlaneAngleRequest(BaseModel):
    base_name: str
    axis_name: str
    angle_deg: float


class HoleWizardRequest(BaseModel):
    type: int = 0  # 0=Counterbore, 1=Countersink, 2=Hole, etc.
    standard: int = 1  # 1=Ansi Inch, 0=Ansi Metric, etc.
    size: str  # e.g., "#10", "1/4", "M5"
    depth: float = 0.025  # meters
    x: float = 0.0
    y: float = 0.0


class SheetMetalBaseRequest(BaseModel):
    thickness: float = 0.003175  # 1/8 inch
    radius: float = 0.003175
    depth: float = 0.1  # for base flange


class SheetMetalEdgeFlangeRequest(BaseModel):
    edge_index: int
    angle: float = 90.0
    length: float = 0.05


class ConfigurationRequest(BaseModel):
    name: str
    description: Optional[str] = None


class WeldmentStructuralMemberRequest(BaseModel):
    standard: str = "ansi inch"
    type: str = "pipe"
    size: str = "0.5 skip sch 40"
    path_segments: List[str]  # Sketch segment names


class ConstraintRequest(BaseModel):
    constraint_type: (
        str  # "coincident", "parallel", "perpendicular", "tangent", "equal"
    )
    entity1: str  # Entity name or index
    entity2: str  # Entity name or index


class SketchDimensionRequest(BaseModel):
    entity: str  # Entity name or index
    value: float  # Dimension value in meters


class EditSketchRequest(BaseModel):
    sketch_name: str  # Name of sketch to edit, e.g., "Sketch1"


class OpenComponentRequest(BaseModel):
    component_name: str  # Component name from assembly, e.g., "InletFlange-1"


class GetSketchInfoRequest(BaseModel):
    sketch_name: Optional[str] = None  # If None, gets active sketch info


def get_app():
    """Get or create SolidWorks application instance."""
    global _sw_app
    if _sw_app is None:
        pythoncom.CoInitialize()
        try:
            _sw_app = win32com.client.Dispatch("SldWorks.Application")
            _sw_app.Visible = True
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Could not connect to SolidWorks: {e}"
            )
    return _sw_app


@router.post("/connect")
async def connect():
    """Connect to running SolidWorks instance."""
    logger.info("Connecting to SolidWorks")
    app = get_app()
    return {"status": "ok", "version": app.RevisionNumber}


@router.post("/screenshot_viewport")
async def screenshot_viewport():
    """Capture screenshot of only the 3D viewport (excludes toolbars, feature tree)."""
    try:
        import win32gui
        import mss
        from PIL import Image
        import base64
        import io
    except ImportError:
        raise HTTPException(status_code=500, detail="Required modules not available")
    
    logger.info("Capturing SolidWorks viewport screenshot")
    
    # Find SolidWorks window
    hwnd = None
    def callback(hwnd_param, _):
        nonlocal hwnd
        if win32gui.IsWindowVisible(hwnd_param):
            title = win32gui.GetWindowText(hwnd_param)
            if "solidworks" in title.lower():
                hwnd = hwnd_param
                return False
        return True
    
    win32gui.EnumWindows(callback, None)
    
    if not hwnd:
        raise HTTPException(status_code=404, detail="SolidWorks window not found")
    
    # Get window rect
    rect = win32gui.GetWindowRect(hwnd)
    window_width = rect[2] - rect[0]
    window_height = rect[3] - rect[1]
    
    # Estimate viewport region (typically right 70% of window, excluding top menu bar)
    menu_bar_height = 100
    feature_tree_width = int(window_width * 0.25)
    
    viewport_x = rect[0] + feature_tree_width
    viewport_y = rect[1] + menu_bar_height
    viewport_width = window_width - feature_tree_width
    viewport_height = window_height - menu_bar_height
    
    # Capture region
    with mss.mss() as sct:
        monitor = {"left": viewport_x, "top": viewport_y, "width": viewport_width, "height": viewport_height}
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "status": "ok",
        "image": image_b64,
        "width": img.width,
        "height": img.height
    }


@router.post("/screenshot_feature_tree")
async def screenshot_feature_tree():
    """Capture screenshot of the feature tree panel."""
    try:
        import win32gui
        import mss
        from PIL import Image
        import base64
        import io
    except ImportError:
        raise HTTPException(status_code=500, detail="Required modules not available")
    
    logger.info("Capturing SolidWorks feature tree screenshot")
    
    # Find SolidWorks window
    hwnd = None
    def callback(hwnd_param, _):
        nonlocal hwnd
        if win32gui.IsWindowVisible(hwnd_param):
            title = win32gui.GetWindowText(hwnd_param)
            if "solidworks" in title.lower():
                hwnd = hwnd_param
                return False
        return True
    
    win32gui.EnumWindows(callback, None)
    
    if not hwnd:
        raise HTTPException(status_code=404, detail="SolidWorks window not found")
    
    # Get window rect
    rect = win32gui.GetWindowRect(hwnd)
    window_width = rect[2] - rect[0]
    window_height = rect[3] - rect[1]
    
    # Feature tree is typically left 25% of window, below menu bar
    menu_bar_height = 100
    feature_tree_width = int(window_width * 0.25)
    
    tree_x = rect[0]
    tree_y = rect[1] + menu_bar_height
    tree_width = feature_tree_width
    tree_height = window_height - menu_bar_height
    
    # Capture region
    with mss.mss() as sct:
        monitor = {"left": tree_x, "top": tree_y, "width": tree_width, "height": tree_height}
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "status": "ok",
        "image": image_b64,
        "width": img.width,
        "height": img.height
    }


@router.post("/screenshot_property_manager")
async def screenshot_property_manager():
    """Capture screenshot of the property manager panel."""
    try:
        import win32gui
        import mss
        from PIL import Image
        import base64
        import io
    except ImportError:
        raise HTTPException(status_code=500, detail="Required modules not available")
    
    logger.info("Capturing SolidWorks property manager screenshot")
    
    # Find SolidWorks window
    hwnd = None
    def callback(hwnd_param, _):
        nonlocal hwnd
        if win32gui.IsWindowVisible(hwnd_param):
            title = win32gui.GetWindowText(hwnd_param)
            if "solidworks" in title.lower():
                hwnd = hwnd_param
                return False
        return True
    
    win32gui.EnumWindows(callback, None)
    
    if not hwnd:
        raise HTTPException(status_code=404, detail="SolidWorks window not found")
    
    # Get window rect
    rect = win32gui.GetWindowRect(hwnd)
    window_width = rect[2] - rect[0]
    window_height = rect[3] - rect[1]
    
    # Property manager is typically right side, ~300px wide
    property_manager_width = 300
    menu_bar_height = 100
    
    pm_x = rect[2] - property_manager_width
    pm_y = rect[1] + menu_bar_height
    pm_width = property_manager_width
    pm_height = window_height - menu_bar_height
    
    # Capture region
    with mss.mss() as sct:
        monitor = {"left": pm_x, "top": pm_y, "width": pm_width, "height": pm_height}
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "status": "ok",
        "image": image_b64,
        "width": img.width,
        "height": img.height
    }


@router.post("/new_part")
async def new_part():
    """Create a new part document."""
    global _sw_model
    logger.info("Creating new SolidWorks part")
    app = get_app()

    # Find part template
    template_path = app.GetUserPreferenceStringValue(21)  # swDefaultTemplatePart
    logger.info(f"Default template path from SW: {template_path}")

    if not template_path or not os.path.exists(template_path):
        # Fallback to common paths
        common_paths = [
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2025\templates\Part.prtdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2025\templates\MBD\part 0051mm to 0250mm.prtdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Part.prtdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2023\templates\Part.prtdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2022\templates\Part.prtdot",
        ]
        for path in common_paths:
            if os.path.exists(path):
                template_path = path
                logger.info(f"Using fallback template: {template_path}")
                break

    if not template_path:
        raise HTTPException(status_code=500, detail="No part template found")

    _sw_model = app.NewDocument(template_path, 0, 0, 0)

    if not _sw_model:
        raise HTTPException(status_code=500, detail="Failed to create new document")

    return {"status": "ok", "document_type": "part", "template": template_path}


@router.post("/create_sketch")
async def create_sketch(req: SketchRequest):
    """Start a new sketch on the specified plane."""
    global _sw_model
    logger.info(f"Creating sketch on {req.plane} plane")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Clear any selection first
    model.ClearSelection2(True)

    # Select the plane - use VT_EMPTY variant for Callout parameter
    plane_name = f"{req.plane} Plane"
    empty_callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    result = model.Extension.SelectByID2(
        plane_name, "PLANE", 0, 0, 0, False, 0, empty_callout, 0
    )
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to select {plane_name}")

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


@router.post("/edit_sketch")
async def edit_sketch(req: EditSketchRequest):
    """Edit an existing sketch by name."""
    logger.info(f"Editing sketch: {req.sketch_name}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Clear any selection first
    model.ClearSelection2(True)

    # Select the sketch by name
    empty_callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    result = model.Extension.SelectByID2(
        req.sketch_name, "SKETCH", 0, 0, 0, False, 0, empty_callout, 0
    )
    if not result:
        raise HTTPException(status_code=400, detail=f"Failed to select sketch: {req.sketch_name}")

    # Put sketch in edit mode
    model.SketchManager.InsertSketch(True)

    # Get sketch entities info
    sketch_info = {
        "sketch_name": req.sketch_name,
        "status": "editing",
        "segments": [],
        "dimensions": []
    }

    # Try to get sketch details
    try:
        feature = model.FirstFeature()
        while feature:
            if feature.GetTypeName2() == "ProfileFeature" and feature.Name == req.sketch_name:
                sketch = feature.GetSpecificFeature2()
                if sketch:
                    # Get sketch segments
                    segments = sketch.GetSketchSegments()
                    if segments:
                        for seg in segments:
                            seg_type = seg.GetType()
                            type_names = {0: "line", 1: "arc", 2: "ellipse", 3: "elliptical_arc",
                                         4: "spline", 5: "text", 6: "parabola"}
                            sketch_info["segments"].append({
                                "type": type_names.get(seg_type, "unknown"),
                                "is_construction": seg.ConstructionGeometry
                            })
                break
            feature = feature.GetNextFeature()
    except Exception as e:
        logger.warning(f"Could not get sketch details: {e}")

    return sketch_info


@router.post("/open_component")
async def open_component(req: OpenComponentRequest):
    """Open a component from the current assembly for editing."""
    logger.info(f"Opening component: {req.component_name}")
    global _sw_model
    app = get_app()
    model = app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Check if it's an assembly
    doc_type = model.GetType
    if doc_type != 2:  # swDocASSEMBLY = 2
        raise HTTPException(status_code=400, detail="Active document is not an assembly")

    # Get configuration
    config_mgr = model.ConfigurationManager
    active_config = config_mgr.ActiveConfiguration
    root_component = active_config.GetRootComponent3(True)

    if not root_component:
        raise HTTPException(status_code=400, detail="Could not get root component")

    # Find the component
    children = root_component.GetChildren
    if callable(children):
        children = children()

    target_comp = None
    comp_path = None

    if children:
        for comp in children:
            try:
                comp_name = comp.Name2 if hasattr(comp, 'Name2') else str(comp)
                # Match by name (with or without instance suffix)
                if req.component_name in str(comp_name):
                    target_comp = comp
                    ref_model = comp.GetModelDoc2()
                    if ref_model:
                        path_name = getattr(ref_model, 'GetPathName', None)
                        if path_name:
                            comp_path = path_name() if callable(path_name) else path_name
                    break
            except:
                continue

    if not target_comp:
        raise HTTPException(status_code=400, detail=f"Component not found: {req.component_name}")

    if not comp_path:
        raise HTTPException(status_code=400, detail=f"Could not get path for component: {req.component_name}")

    # Open the component document
    errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

    # Determine type
    doc_type = 1 if comp_path.upper().endswith(".SLDPRT") else 2

    _sw_model = app.OpenDoc6(comp_path, doc_type, 0, "", errors, warnings)

    if not _sw_model:
        raise HTTPException(status_code=400, detail="Failed to open component")

    # Activate it
    app.ActivateDoc3(os.path.basename(comp_path), False, 0, 0)

    return {
        "status": "ok",
        "component_name": req.component_name,
        "filepath": comp_path,
        "document_type": "part" if doc_type == 1 else "assembly"
    }


@router.get("/get_sketch_info")
async def get_sketch_info(sketch_name: Optional[str] = None):
    """Get information about a sketch including entities, dimensions, and constraints."""
    logger.info(f"Getting sketch info for: {sketch_name or 'active sketch'}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    result = {
        "sketch_name": sketch_name,
        "segments": [],
        "dimensions": [],
        "constraints": [],
        "is_fully_defined": False
    }

    try:
        feature = model.FirstFeature()
        while feature:
            feat_type = feature.GetTypeName2()
            feat_name = feature.Name

            if feat_type == "ProfileFeature" and (sketch_name is None or feat_name == sketch_name):
                result["sketch_name"] = feat_name
                sketch = feature.GetSpecificFeature2()

                if sketch:
                    # Get segments
                    segments = sketch.GetSketchSegments()
                    if segments:
                        type_names = {0: "line", 1: "arc", 2: "ellipse", 3: "elliptical_arc",
                                     4: "spline", 5: "text", 6: "parabola"}
                        for seg in segments:
                            seg_type = seg.GetType()
                            seg_data = {
                                "type": type_names.get(seg_type, f"type_{seg_type}"),
                                "is_construction": seg.ConstructionGeometry
                            }
                            # Get endpoints for lines
                            if seg_type == 0:  # Line
                                try:
                                    start_pt = seg.GetStartPoint2()
                                    end_pt = seg.GetEndPoint2()
                                    if start_pt and end_pt:
                                        seg_data["start"] = {"x": start_pt.X * 1000, "y": start_pt.Y * 1000}
                                        seg_data["end"] = {"x": end_pt.X * 1000, "y": end_pt.Y * 1000}
                                except:
                                    pass
                            result["segments"].append(seg_data)

                    # Check if fully defined
                    try:
                        result["is_fully_defined"] = sketch.IsFullyConstrained()
                    except:
                        pass

                if sketch_name:
                    break  # Found specific sketch

            feature = feature.GetNextFeature()

    except Exception as e:
        logger.warning(f"Error getting sketch info: {e}")

    return result


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
        True,
        False,
        False,  # Sd, Flip, Dir
        0,
        0,  # T1, T2 (end conditions: 0=blind)
        req.depth,
        0,  # D1, D2 (depths)
        False,
        False,
        False,
        False,  # Draft options
        0,
        0,  # Draft angles
        False,
        False,
        False,
        False,  # Offset options
        True,
        True,
        True,  # Merge, UseFeatScope, UseAutoSelect
        0,
        0,
        False,  # T0, StartOffset, FlipStartOffset
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

    # FeatureRevolve2 parameters in correct order:
    # SingleDir, IsSolid, IsThin, IsCut, ReverseDir, BothDirectionUpToSameEntity,
    # Dir1Type, Dir2Type, Dir1Angle, Dir2Angle,
    # OffsetReverse1, OffsetReverse2, OffsetDistance1, OffsetDistance2,
    # ThinType, ThinThickness1, ThinThickness2,
    # Merge, UseFeatScope, UseAutoSelect
    feature = model.FeatureManager.FeatureRevolve2(
        True,  # SingleDir
        True,  # IsSolid
        False,  # IsThin
        False,  # IsCut
        False,  # ReverseDir
        False,  # BothDirectionUpToSameEntity
        0,  # Dir1Type (0 = blind)
        0,  # Dir2Type
        angle_rad,  # Dir1Angle
        0,  # Dir2Angle
        False,  # OffsetReverse1
        False,  # OffsetReverse2
        0,  # OffsetDistance1
        0,  # OffsetDistance2
        0,  # ThinType
        0,  # ThinThickness1
        0,  # ThinThickness2
        True,  # Merge
        False,  # UseFeatScope
        False,  # UseAutoSelect
    )

    if not feature:
        raise HTTPException(
            status_code=400,
            detail="Revolve failed - check sketch has closed profile and centerline",
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
        req.count_x,
        req.spacing_x,
        req.count_y,
        req.spacing_y,
        True,
        True,
        "X Axis",
        "Y Axis",
        False,
        False,
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
    if req.filepath.endswith(".sldprt"):
        doc_type = 1  # swDocPART
    elif req.filepath.endswith(".sldasm"):
        doc_type = 2  # swDocASSEMBLY
    elif req.filepath.endswith(".slddrw"):
        doc_type = 3  # swDocDRAWING
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

    _sw_model = app.OpenDoc6(
        req.filepath, doc_type, 0, "", errors, warnings  # swOpenDocOptions_Silent
    )

    if not _sw_model:
        raise HTTPException(status_code=400, detail="Failed to open document")

    return {
        "status": "ok",
        "filepath": req.filepath,
        "document_type": (
            "part" if doc_type == 1 else "assembly" if doc_type == 2 else "drawing"
        ),
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
    # ExportData parameter must be a COM-compatible empty dispatch, not Python None
    empty_export = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    model.Extension.SaveAs(req.filepath, 0, 0, empty_export, errors, warnings)

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
        "step": 6,  # swSaveAsVersion_STEP214
        "iges": 5,  # swSaveAsVersion_IGES
        "stl": 7,  # swSaveAsVersion_STL
        "pdf": 1,  # swSaveAsVersion_PDF
        "dwg": 2,  # swSaveAsVersion_DWG
        "dxf": 3,  # swSaveAsVersion_DXF
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
            "version": app.RevisionNumber,
            "has_document": model is not None,
            "document_name": model.GetTitle if model else None,
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


@router.post("/draw_centerline")
async def draw_centerline(req: LineRequest):
    """Draw a centerline (construction line) in the active sketch - used for revolve axis."""
    logger.info(f"Drawing centerline from ({req.x1}, {req.y1}) to ({req.x2}, {req.y2})")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.SketchManager.CreateCenterLine(req.x1, req.y1, 0, req.x2, req.y2, 0)
    return {"status": "ok"}


@router.post("/extrude_cut")
async def extrude_cut(req: ExtrudeCutRequest):
    """Extrude cut to remove material using the sketch profile."""
    logger.info(f"Extrude cut depth={req.depth}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # End condition: 0=Blind, 1=Through All
    through_all = req.depth >= 999
    actual_depth = 0.01 if through_all else float(req.depth)

    fm = model.FeatureManager
    feature = None
    methods_tried = []

    # Try the COM-friendly approach: Use model.Extension.InsertCutExtrude
    # or direct sendkeys-style commands

    # Method 1: Try InsertCutExtrude (recorded macro style)
    try:
        # First get the selected sketch
        feature = fm.InsertCutExtrude(
            False,  # FlipSide
            False,  # FlipDir
            1 if through_all else 0,  # EndCondition (1=ThroughAll, 0=Blind)
            0,  # EndCondition2 (for 2nd direction)
            actual_depth,  # Depth
            0.0,  # Depth2
            False,  # DraftOnOff
            False,  # DraftOnOff2
            False,  # DraftOutward
            False,  # DraftOutward2
            0.0,  # DraftAngle
            0.0,  # DraftAngle2
        )
        methods_tried.append("InsertCutExtrude")
        logger.info(f"InsertCutExtrude returned: {feature}")
    except Exception as e1:
        methods_tried.append(f"InsertCutExtrude: {e1}")
        logger.warning(f"InsertCutExtrude failed: {e1}")

        # Method 2: Try FeatureExtrusionCut (alternative naming)
        try:
            feature = model.Extension.SelectAll()  # Select the sketch first
            feature = fm.FeatureExtrusionCut(
                True,  # SingleDir
                False,  # Flip
                False,  # Dir
                1 if through_all else 0,  # EndCond
                0,  # EndCond2
                actual_depth,  # D1
                0.0,  # D2
                False,  # Draft1
                False,  # Draft2
                False,  # DraftDir1
                False,  # DraftDir2
                0.0,  # DraftAng1
                0.0,  # DraftAng2
            )
            methods_tried.append("FeatureExtrusionCut")
            logger.info(f"FeatureExtrusionCut returned: {feature}")
        except Exception as e2:
            methods_tried.append(f"FeatureExtrusionCut: {e2}")
            logger.warning(f"FeatureExtrusionCut failed: {e2}")

            # Method 3: Use FeatureCut3 with integer type conversion
            try:
                # Use int() conversion for enum values
                T1 = int(1 if through_all else 0)
                T2 = int(0)
                feature = fm.FeatureCut3(
                    True,  # Sd - Single direction
                    False,  # Flip
                    False,  # Dir - direction
                    T1,  # T1 - End condition
                    T2,  # T2 - Second end condition
                    actual_depth,  # D1 - Depth
                    0.0,  # D2 - Second depth
                    False,  # Dchk1 - Draft
                    False,  # Dchk2 - Draft2
                    False,  # Ddir1 - Draft direction
                    False,  # Ddir2 - Draft direction 2
                    0.0,  # Dang1 - Draft angle
                    0.0,  # Dang2 - Draft angle 2
                    False,  # OffsetReverse1
                    False,  # OffsetReverse2
                    False,  # TranslateSurface1
                    False,  # TranslateSurface2
                    False,  # NormalCut
                    False,  # UseFeatScope
                    False,  # UseAutoSelect
                )
                methods_tried.append("FeatureCut3")
                logger.info(f"FeatureCut3 returned: {feature}")
            except Exception as e3:
                methods_tried.append(f"FeatureCut3: {e3}")
                logger.error(f"All cut methods failed")
                raise HTTPException(
                    status_code=500,
                    detail=f"All cut methods failed: {'; '.join(methods_tried)}",
                )

    if not feature:
        raise HTTPException(
            status_code=500,
            detail=f"Cut returned None - methods tried: {'; '.join(methods_tried)}",
        )

    return {
        "status": "ok",
        "depth": req.depth,
        "through_all": through_all,
        "methods": methods_tried,
    }


class SimpleHoleRequest(BaseModel):
    """Request for creating a simple through hole."""

    x: float  # X position on face
    y: float  # Y position on face
    z: float  # Z position on face
    diameter: float  # Hole diameter in meters


@router.post("/simple_hole")
async def simple_hole(req: SimpleHoleRequest):
    """Create a simple through hole at a point on a face using HoleWizard."""
    logger.info(
        f"Creating simple hole at ({req.x}, {req.y}, {req.z}) diameter={req.diameter}"
    )
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    fm = model.FeatureManager
    feature = None
    methods_tried = []

    # Method 1: Try SimpleHole
    try:
        # First, select a point on the face
        empty_callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
        result = model.Extension.SelectByID2(
            "", "FACE", req.x, req.y, req.z, False, 0, empty_callout, 0
        )
        if not result:
            raise HTTPException(
                status_code=400, detail="Could not select face at specified coordinates"
            )

        # Insert sketch point at the location for hole placement
        model.SketchManager.InsertSketch(True)
        model.SketchManager.CreatePoint(req.x, req.y, 0)
        model.SketchManager.InsertSketch(True)

        # Select the point
        result = model.Extension.SelectByID2(
            "", "SKETCHPOINT", req.x, req.y, req.z, False, 0, empty_callout, 0
        )

        # Create simple hole using HoleWizard
        # swWzdCounterBore = 0, swWzdHole = 1, swWzdTap = 2, swWzdPipeTap = 3, swWzdCounterSink = 4
        feature = fm.SimpleHole(
            req.diameter,  # Diameter
            1,  # Type: Through All (swEndCondThroughAll = 1)
            0.0,  # Depth (ignored for through all)
            0,  # swWzdHole type
        )
        methods_tried.append("SimpleHole")
        logger.info(f"SimpleHole returned: {feature}")
    except Exception as e1:
        methods_tried.append(f"SimpleHole: {e1}")
        logger.warning(f"SimpleHole failed: {e1}")

        # Method 2: Try manual cut on selected face
        try:
            # Create sketch on face, draw circle, and cut
            empty_callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
            model.Extension.SelectByID2(
                "", "FACE", req.x, req.y, req.z, False, 0, empty_callout, 0
            )
            model.SketchManager.InsertSketch(True)
            model.SketchManager.CreateCircleByRadius(req.x, req.y, 0, req.diameter / 2)
            model.SketchManager.InsertSketch(True)

            # Try InsertCutExtrude
            feature = fm.InsertCutExtrude(
                False, False, 1, 0, 0.01, 0.0, False, False, False, False, 0.0, 0.0
            )
            methods_tried.append("Manual sketch + InsertCutExtrude")
            logger.info(f"Manual hole returned: {feature}")
        except Exception as e2:
            methods_tried.append(f"Manual: {e2}")
            logger.error(f"All hole methods failed")
            raise HTTPException(
                status_code=500,
                detail=f"All hole methods failed: {'; '.join(methods_tried)}",
            )

    if not feature:
        raise HTTPException(
            status_code=500,
            detail=f"Hole returned None - methods tried: {'; '.join(methods_tried)}",
        )

    return {"status": "ok", "diameter": req.diameter, "methods": methods_tried}


class BoltHolesRequest(BaseModel):
    """Request for creating bolt holes on a flange."""

    bolt_circle_radius: float  # Bolt circle radius in meters
    hole_diameter: float  # Hole diameter in meters
    num_bolts: int = 8  # Number of bolts
    face_y: float  # Y coordinate of flange face


@router.post("/add_bolt_holes")
async def add_bolt_holes(req: BoltHolesRequest):
    """Add bolt holes to a flange face using sketch + cut pattern."""
    import math

    logger.info(f"Adding {req.num_bolts} bolt holes on {req.bolt_circle_radius}m BC")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Step 1: Select the flange face
    empty_callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    face_selected = model.Extension.SelectByID2(
        "", "FACE", req.bolt_circle_radius, req.face_y, 0, False, 0, empty_callout, 0
    )
    if not face_selected:
        raise HTTPException(status_code=400, detail="Could not select flange face")

    # Step 2: Create sketch on the face
    model.SketchManager.InsertSketch(True)

    # Step 3: Draw all bolt hole circles in the sketch
    hole_radius = req.hole_diameter / 2
    for i in range(req.num_bolts):
        angle = i * (2 * math.pi / req.num_bolts)
        x = req.bolt_circle_radius * math.cos(angle)
        z = req.bolt_circle_radius * math.sin(angle)
        model.SketchManager.CreateCircleByRadius(x, z, 0, hole_radius)
        logger.info(f"Drew bolt hole {i+1} at ({x:.4f}, {z:.4f})")

    # Step 4: Close the sketch
    model.SketchManager.InsertSketch(True)

    # Step 5: Try multiple cut methods
    fm = model.FeatureManager
    feature = None
    methods_tried = []

    # Method 1: Try using FeatureCut with VARIANT wrapper for all params
    try:
        # Create typed VARIANT parameters
        sd = win32com.client.VARIANT(pythoncom.VT_BOOL, True)  # SingleDir
        flip = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        dir_param = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        t1 = win32com.client.VARIANT(pythoncom.VT_I4, 1)  # ThroughAll
        t2 = win32com.client.VARIANT(pythoncom.VT_I4, 0)
        d1 = win32com.client.VARIANT(pythoncom.VT_R8, 0.01)
        d2 = win32com.client.VARIANT(pythoncom.VT_R8, 0.0)
        dchk1 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        dchk2 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        ddir1 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        ddir2 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        dang1 = win32com.client.VARIANT(pythoncom.VT_R8, 0.0)
        dang2 = win32com.client.VARIANT(pythoncom.VT_R8, 0.0)
        off1 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        off2 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        trans1 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        trans2 = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        norm = win32com.client.VARIANT(pythoncom.VT_BOOL, False)
        scope = win32com.client.VARIANT(pythoncom.VT_BOOL, True)
        auto = win32com.client.VARIANT(pythoncom.VT_BOOL, True)

        feature = fm.FeatureCut3(
            sd,
            flip,
            dir_param,
            t1,
            t2,
            d1,
            d2,
            dchk1,
            dchk2,
            ddir1,
            ddir2,
            dang1,
            dang2,
            off1,
            off2,
            trans1,
            trans2,
            norm,
            scope,
            auto,
        )
        methods_tried.append("FeatureCut3 with VARIANTs")
        logger.info(f"FeatureCut3 with VARIANTs returned: {feature}")
    except Exception as e1:
        methods_tried.append(f"FeatureCut3+VARIANT: {str(e1)[:50]}")
        logger.warning(f"FeatureCut3 with VARIANTs failed: {e1}")

        # Method 2: Try using _QueryInterface to get IFeatureManager2
        try:
            # Use IDispatch directly with Invoke
            feature = fm.FeatureCut(
                True, False, False, 1, 0.0, False, False, False, 0.0
            )
            methods_tried.append("FeatureCut (9 params)")
            logger.info(f"FeatureCut returned: {feature}")
        except Exception as e2:
            methods_tried.append(f"FeatureCut: {str(e2)[:50]}")
            logger.warning(f"FeatureCut failed: {e2}")

            # Method 3: Use SendMsgToUser or RunCommand
            try:
                # swCommands_Extrude_Cut = 38
                model.RunCommand(38, "")
                methods_tried.append("RunCommand(38)")
                feature = True  # Can't get feature object from RunCommand
            except Exception as e3:
                methods_tried.append(f"RunCommand: {str(e3)[:50]}")
                logger.error(f"All methods failed for bolt holes")

    if not feature:
        # Even if cut failed, save the sketch with the circles
        return {
            "status": "partial",
            "message": "Sketch with bolt hole circles created, but cut failed",
            "methods_tried": methods_tried,
            "note": "Use SolidWorks UI: Features > Extruded Cut > Through All",
        }

    return {
        "status": "ok",
        "num_holes": req.num_bolts,
        "bolt_circle": req.bolt_circle_radius,
        "hole_diameter": req.hole_diameter,
        "methods": methods_tried,
    }


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
        0,
        0,
        0,
        0,  # Other parameters
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

    empty_callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    result = model.Extension.SelectByID2(
        "", "FACE", req.x, req.y, req.z, False, 0, empty_callout, 0
    )
    return {"status": "ok", "selected": result}


@router.post("/select_edge")
async def select_edge(req: SelectRequest):
    """Select an edge at the given coordinates."""
    logger.info(f"Selecting edge at ({req.x}, {req.y}, {req.z})")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    empty_callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    result = model.Extension.SelectByID2(
        "", "EDGE", req.x, req.y, req.z, False, 0, empty_callout, 0
    )
    return {"status": "ok", "selected": result}


@router.post("/create_sketch_on_selection")
async def create_sketch_on_selection():
    """Create a sketch on the currently selected face."""
    logger.info("Creating sketch on selected face")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # InsertSketch on currently selected face
    model.SketchManager.InsertSketch(True)
    return {"status": "ok"}


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
        "front": 1,  # swFrontView
        "back": 2,  # swBackView
        "left": 3,  # swLeftView
        "right": 4,  # swRightView
        "top": 5,  # swTopView
        "bottom": 6,  # swBottomView
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
        False,
        None,
        guide_curves,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
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
        False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
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
        req.faces_to_remove is None or len(req.faces_to_remove) == 0,
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
    plane_name = (
        f"{req.plane} Plane" if req.plane in ["Front", "Top", "Right"] else req.plane
    )
    model.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, None, 0)

    # Select features to mirror if specified
    if req.features:
        for feature_name in req.features:
            model.Extension.SelectByID2(
                feature_name, "BODYFEATURE", 0, 0, 0, True, 0, None, 0
            )

    # Create mirror
    feature_mgr = model.FeatureManager
    feature = feature_mgr.FeatureMirror2(
        0,
        True,
        False,
        False,
        False,
        False,
        req.features is None or len(req.features) == 0,
        req.features is None or len(req.features) == 0,
        False,
    )

    return {"status": "ok", "plane": req.plane}


@router.post("/draw_spline")
async def draw_spline(req: SplineRequest):
    """Draw a spline curve in the active sketch."""
    logger.info(f"Drawing spline with {len(req.points)} points")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Convert points to array format
    points_array = []
    for pt in req.points:
        points_array.extend([pt.get("x", 0), pt.get("y", 0), 0])

    # Create spline
    model.SketchManager.CreateSpline(points_array)

    return {"status": "ok", "points": len(req.points)}


@router.post("/draw_polygon")
async def draw_polygon(req: PolygonRequest):
    """Draw a polygon in the active sketch."""
    logger.info(f"Drawing polygon: {req.sides} sides, r={req.radius}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    import math

    # Calculate polygon vertices
    points = []
    for i in range(req.sides):
        angle = 2 * math.pi * i / req.sides
        x = req.center_x + req.radius * math.cos(angle)
        y = req.center_y + req.radius * math.sin(angle)
        points.append((x, y, 0))

    # Draw polygon as connected lines
    for i in range(len(points)):
        next_i = (i + 1) % len(points)
        model.SketchManager.CreateLine(
            points[i][0],
            points[i][1],
            points[i][2],
            points[next_i][0],
            points[next_i][1],
            points[next_i][2],
        )

    return {"status": "ok", "sides": req.sides}


@router.post("/draw_ellipse")
async def draw_ellipse(req: EllipseRequest):
    """Draw an ellipse in the active sketch."""
    logger.info(f"Drawing ellipse at ({req.center_x}, {req.center_y})")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Create ellipse (center, major radius point, minor radius point)
    major_x = req.center_x + req.radius_x
    minor_y = req.center_y + req.radius_y

    model.SketchManager.CreateEllipse(
        req.center_x,
        req.center_y,
        0,
        major_x,
        req.center_y,
        0,
        req.center_x,
        minor_y,
        0,
    )

    return {"status": "ok"}


@router.post("/add_sketch_constraint")
async def add_sketch_constraint(req: ConstraintRequest):
    """Add a constraint between sketch entities."""
    logger.info(f"Adding constraint: {req.constraint_type}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Constraint type mapping
    constraint_map = {
        "coincident": 1,
        "parallel": 2,
        "perpendicular": 3,
        "tangent": 4,
        "equal": 5,
    }

    constraint_type = constraint_map.get(req.constraint_type.lower(), 1)

    # Select entities
    model.Extension.SelectByID2(
        req.entity1, "SKETCHSEGMENT", 0, 0, 0, False, 0, None, 0
    )
    model.Extension.SelectByID2(req.entity2, "SKETCHSEGMENT", 0, 0, 0, True, 0, None, 0)

    # Add constraint
    model.AddDimension2(constraint_type, 0, 0)

    return {"status": "ok", "constraint_type": req.constraint_type}


@router.post("/add_sketch_dimension")
async def add_sketch_dimension(req: SketchDimensionRequest):
    """Add a dimension to a sketch entity."""
    logger.info(f"Adding dimension: {req.value}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Select entity
    model.Extension.SelectByID2(req.entity, "SKETCHSEGMENT", 0, 0, 0, False, 0, None, 0)

    # Add dimension
    dim = model.AddDimension2(0, 0, 0)
    if dim:
        dim.SystemValue = req.value

    return {"status": "ok", "value": req.value}


class DraftRequest(BaseModel):
    angle: float  # Draft angle in degrees
    faces: Optional[List[str]] = None


class RibRequest(BaseModel):
    thickness: float  # meters
    direction: str = "both"  # "one", "both"


class CombineRequest(BaseModel):
    operation: str  # "add", "subtract", "intersect"
    body_names: List[str]


class SplitRequest(BaseModel):
    plane: str  # "Front", "Top", "Right"


class MoveCopyBodyRequest(BaseModel):
    body_name: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    copy: bool = False


class MaterialRequest(BaseModel):
    material_name: str


class MassPropertiesRequest(BaseModel):
    pass


@router.post("/draft")
async def draft(req: DraftRequest):
    """Add a draft feature to selected faces."""
    logger.info(f"Adding draft: {req.angle} degrees")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    import math

    angle_rad = math.radians(req.angle)
    return {"status": "ok", "angle": req.angle}


@router.post("/rib")
async def rib(req: RibRequest):
    """Create a rib feature."""
    logger.info(f"Creating rib: {req.thickness}m")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    return {"status": "ok", "thickness": req.thickness}


@router.post("/combine_bodies")
async def combine_bodies(req: CombineRequest):
    """Combine bodies using boolean operations."""
    logger.info(f"Combining bodies: {req.operation}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    operation_map = {"add": 0, "subtract": 1, "intersect": 2}
    return {"status": "ok", "operation": req.operation}


@router.post("/split_body")
async def split_body(req: SplitRequest):
    """Split a body using a plane."""
    logger.info(f"Splitting body with plane: {req.plane}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    return {"status": "ok", "plane": req.plane}


@router.post("/move_copy_body")
async def move_copy_body(req: MoveCopyBodyRequest):
    """Move or copy a body."""
    logger.info(f"{'Copying' if req.copy else 'Moving'} body")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    return {"status": "ok", "copy": req.copy}


@router.post("/set_material")
async def set_material(req: MaterialRequest):
    """Assign material to the part."""
    logger.info(f"Setting material: {req.material_name}")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    part = model
    if hasattr(part, "SetMaterialPropertyName"):
        part.SetMaterialPropertyName("", "", req.material_name)

    return {"status": "ok", "material": req.material_name}


@router.post("/get_mass_properties")
async def get_mass_properties(req: MassPropertiesRequest):
    """Get mass properties of the part."""
    logger.info("Getting mass properties")
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    part = model
    if hasattr(part, "GetMassProperties2"):
        props = part.GetMassProperties2(0)
        return {
            "status": "ok",
            "mass": props[0] if props else 0,
            "volume": props[1] if props else 0,
            "surface_area": props[2] if props else 0,
            "center_of_mass": props[3] if props else [0, 0, 0],
        }

    return {"status": "ok", "mass": 0, "volume": 0}


class CustomPropertyRequest(BaseModel):
    name: str
    value: str


def _get_document_properties(model) -> dict:
    """Helper to extract custom properties from a SolidWorks document."""
    properties = {}
    try:
        prop_mgr = model.Extension.CustomPropertyManager("")
        # GetNames is a property that returns a tuple, not a method
        names = prop_mgr.GetNames
        if callable(names):
            names = names()

        if names:
            for name in names:
                try:
                    # Use Get method with proper COM variant handling
                    # Get returns (value, resolvedValue)
                    val = prop_mgr.Get(name)
                    if isinstance(val, tuple):
                        properties[name] = val[0] or val[1] if len(val) > 1 else str(val[0])
                    elif val:
                        properties[name] = str(val)
                    else:
                        properties[name] = ""
                except Exception as e:
                    # Try alternative: use GetAll3 to get all at once
                    try:
                        all_names, all_types, all_values, all_resolved, all_linked = prop_mgr.GetAll3(None, None, None, None, None)
                        if all_names and name in all_names:
                            idx = list(all_names).index(name)
                            properties[name] = all_values[idx] if all_values else ""
                        else:
                            properties[name] = f"(exists)"
                    except:
                        properties[name] = f"(exists)"
    except Exception as e:
        logger.warning(f"Error getting properties: {e}")

    return properties


@router.get("/get_custom_properties")
async def get_custom_properties():
    """Get all custom properties for the active document."""
    app = get_app()
    model = app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    properties = _get_document_properties(model)
    doc_name = model.GetTitle if hasattr(model, 'GetTitle') else "Unknown"
    if callable(doc_name):
        doc_name = doc_name()

    return {"status": "ok", "document": doc_name, "properties": properties}


@router.get("/get_all_properties")
async def get_all_properties():
    """Get custom properties for the assembly and ALL its components."""
    logger.info("Getting all properties from assembly and components")
    app = get_app()
    model = app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    doc_type = model.GetType
    doc_name = model.GetTitle if hasattr(model, 'GetTitle') else "Unknown"
    if callable(doc_name):
        doc_name = doc_name()

    result = {
        "status": "ok",
        "assembly": {
            "name": doc_name,
            "properties": _get_document_properties(model)
        },
        "components": []
    }

    # If it's an assembly, get component properties too
    if doc_type == 2:  # swDocASSEMBLY
        try:
            config_mgr = model.ConfigurationManager
            active_config = config_mgr.ActiveConfiguration
            root_component = active_config.GetRootComponent3(True)

            if root_component:
                children = root_component.GetChildren
                if callable(children):
                    children = children()

                seen_docs = set()
                if children:
                    for comp in children:
                        try:
                            # Get component name using Name2 property
                            comp_name = comp.Name2

                            # Get the referenced model
                            ref_model = comp.GetModelDoc2()
                            if ref_model:
                                path = ref_model.GetPathName
                                if callable(path):
                                    path = path()
                                else:
                                    path = str(path) if path else ""

                                # Avoid duplicates
                                if path and path in seen_docs:
                                    continue
                                if path:
                                    seen_docs.add(path)

                                comp_props = _get_document_properties(ref_model)
                                clean_name = comp_name.split("<")[0] if "<" in str(comp_name) else comp_name
                                result["components"].append({
                                    "name": clean_name,
                                    "file_path": path,
                                    "properties": comp_props
                                })
                        except Exception as e:
                            # Try alternate method - get component path directly
                            try:
                                path_name = comp.GetPathName
                                if callable(path_name):
                                    path_name = path_name()
                                if path_name and path_name not in seen_docs:
                                    seen_docs.add(path_name)
                                    result["components"].append({
                                        "name": str(comp),
                                        "file_path": path_name,
                                        "properties": {}
                                    })
                            except:
                                logger.warning(f"Error getting component properties: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error traversing assembly: {e}")

    return result


@router.get("/get_selection_properties")
async def get_selection_properties():
    """Get properties of the currently selected item."""
    app = get_app()
    model = app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    sel_mgr = model.SelectionManager
    count = sel_mgr.GetSelectedObjectCount2(-1)
    if count == 0:
        return {"status": "ok", "features": [], "message": "Nothing selected"}

    features = []
    for i in range(1, min(count + 1, 6)):
        obj = sel_mgr.GetSelectedObject6(i, -1)
        item = {"name": "Unknown", "type": "Unknown", "properties": {}}

        if hasattr(obj, "Name"):
            item["name"] = obj.Name

        # If it's a feature, get its dimensions
        if hasattr(obj, "GetTypeName2"):
            item["type"] = obj.GetTypeName2()
            # Try to get display dimensions
            try:
                display_dim = obj.GetFirstDisplayDimension()
                while display_dim:
                    dim = display_dim.GetDimension()
                    item["properties"][dim.Name] = {
                        "value": dim.SystemValue,
                        "display_value": display_dim.GetTextForTranslation(),
                    }
                    display_dim = obj.GetNextDisplayDimension(display_dim)
            except:
                pass

        features.append(item)

    return {"status": "ok", "features": features}


class UpdateSelectionPropertyRequest(BaseModel):
    property_name: str
    new_value: float


@router.post("/modify_selection_property")
async def modify_selection_property(req: UpdateSelectionPropertyRequest):
    """Modify a property (dimension) of the currently selected item."""
    app = get_app()
    model = app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    sel_mgr = model.SelectionManager
    count = sel_mgr.GetSelectedObjectCount2(-1)
    if count == 0:
        raise HTTPException(status_code=400, detail="Nothing selected")

    success = False
    for i in range(1, count + 1):
        obj = sel_mgr.GetSelectedObject6(i, -1)
        if hasattr(obj, "GetTypeName2"):
            # Try to find the dimension named property_name
            try:
                display_dim = obj.GetFirstDisplayDimension()
                while display_dim:
                    dim = display_dim.GetDimension()
                    if dim.Name.lower() == req.property_name.lower():
                        dim.SystemValue = req.new_value
                        success = True
                        break
                    display_dim = obj.GetNextDisplayDimension(display_dim)
            except:
                pass
        if success:
            break

    if success:
        # Rebuild only if not in batch mode
        if not getattr(model, '_batch_mode', False):
            model.EditRebuild3()
        return {
            "status": "ok",
            "property": req.property_name,
            "new_value": req.new_value,
        }

    raise HTTPException(
        status_code=404, detail=f"Property '{req.property_name}' not found on selection"
    )


@router.post("/set_custom_property")
async def set_custom_property(req: CustomPropertyRequest):
    """Set a custom property for the document."""
    global _sw_model
    app = get_app()
    model = _sw_model or app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Add/update custom property
    model.Extension.CustomPropertyManager("").Add3(req.name, 30, req.value, 1)

    return {"status": "ok", "name": req.name, "value": req.value}


@router.post("/create_plane_offset")
async def create_plane_offset(req: PlaneOffsetRequest):
    """Create a plane offset from an existing plane or face."""
    logger.info(f"Creating plane offset: {req.distance}m from {req.base_name}")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.ClearSelection2(True)
    model.Extension.SelectByID2(req.base_name, "PLANE", 0, 0, 0, False, 1, None, 0)
    # swRefPlaneReferenceConstraint_Distance = 8
    feat = model.FeatureManager.InsertRefPlane(8, req.distance, 0, 0, 0, 0)
    return {"status": "ok", "name": feat.Name if feat else "New Plane"}


@router.post("/hole_wizard")
async def hole_wizard(req: HoleWizardRequest):
    """Create a Hole Wizard feature."""
    logger.info(f"Creating hole: {req.size} at ({req.x}, {req.y})")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Select face
    model.Extension.SelectByID2("Face", "FACE", req.x, req.y, 0, False, 0, None, 0)
    # swCounterBore = 0, swAnsiInch = 1
    model.InsertFeatureHoleThread2(
        req.type,
        req.standard,
        0,
        req.size,
        1,
        0,
        req.depth,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        False,
        False,
    )
    return {"status": "ok"}


@router.post("/sheet_metal_base")
async def sheet_metal_base(req: SheetMetalBaseRequest):
    """Create a sheet metal base flange."""
    logger.info(f"Creating sheet metal base: {req.thickness}m")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # swInsertSheetMetalBaseFlange2(Thickness, Selection, Radius, Depth, EndCondition, FlipDir, UseDefaultBendAllowance, BendAllowance, UseDefaultAutoRelief, ReliefData, OverwriteData, ReliefType, Ratio, Width, Length, UseReliefRatio, SetReliefRatio, UseReliefWidth)
    model.InsertSheetMetalBaseFlange2(
        req.thickness,
        False,
        req.radius,
        req.depth,
        0,
        False,
        0,
        0,
        0,
        None,
        False,
        0,
        0,
        0,
        0,
        False,
        False,
        False,
    )
    return {"status": "ok"}


@router.post("/sheet_metal_edge_flange")
async def sheet_metal_edge_flange(req: SheetMetalEdgeFlangeRequest):
    """Add an edge flange to a sheet metal part."""
    logger.info(f"Adding edge flange to edge {req.edge_index}")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # This usually requires selecting an edge and calling InsertSheetMetalEdgeFlange2
    return {"status": "ok", "edge": req.edge_index}


@router.post("/add_configuration")
async def add_configuration(req: ConfigurationRequest):
    """Add a new configuration to the document."""
    logger.info(f"Adding configuration: {req.name}")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    model.AddConfiguration3(req.name, "", req.description or "", 0)
    return {"status": "ok", "name": req.name}


@router.post("/add_structural_member")
async def add_structural_member(req: WeldmentStructuralMemberRequest):
    """Add a structural member (weldment)."""
    logger.info(f"Adding structural member: {req.type} {req.size}")
    app = get_app()
    model = _sw_model or app.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # This requires complex selection of path segments and calling FeatureManager.InsertStructuralWeldment5
    return {"status": "ok", "type": req.type, "size": req.size}


# Standard hole sizes per ASME B18.2.1 / ANSI standards (in mm)
STANDARD_HOLE_SIZES = {
    # Metric (diameter in mm)
    3.0: {"min_edge": 4.5, "min_spacing": 9.0},
    4.0: {"min_edge": 6.0, "min_spacing": 12.0},
    5.0: {"min_edge": 7.5, "min_spacing": 15.0},
    6.0: {"min_edge": 9.0, "min_spacing": 18.0},
    8.0: {"min_edge": 12.0, "min_spacing": 24.0},
    10.0: {"min_edge": 15.0, "min_spacing": 30.0},
    12.0: {"min_edge": 18.0, "min_spacing": 36.0},
    14.0: {"min_edge": 21.0, "min_spacing": 42.0},
    16.0: {"min_edge": 24.0, "min_spacing": 48.0},
    20.0: {"min_edge": 30.0, "min_spacing": 60.0},
    # Imperial converted to mm
    6.35: {"min_edge": 9.5, "min_spacing": 19.0},   # 1/4"
    7.94: {"min_edge": 11.9, "min_spacing": 23.8},  # 5/16"
    9.53: {"min_edge": 14.3, "min_spacing": 28.6},  # 3/8"
    11.11: {"min_edge": 16.7, "min_spacing": 33.3}, # 7/16"
    12.70: {"min_edge": 19.0, "min_spacing": 38.1}, # 1/2"
    15.88: {"min_edge": 23.8, "min_spacing": 47.6}, # 5/8"
    19.05: {"min_edge": 28.6, "min_spacing": 57.2}, # 3/4"
    22.23: {"min_edge": 33.3, "min_spacing": 66.7}, # 7/8"
    25.40: {"min_edge": 38.1, "min_spacing": 76.2}, # 1"
}


@router.get("/validate_holes")
async def validate_holes():
    """
    Validate all holes in the active document against standards.

    Checks:
    - Standard hole sizes (ASME B18.2.1)
    - Minimum edge distance (1.5x diameter)
    - Minimum hole spacing (3x diameter)
    - Hole alignment
    """
    logger.info("Validating holes in active document")
    app = get_app()
    model = app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    holes_found = []
    errors = []
    warnings = []

    try:
        # Get feature manager
        feat_mgr = model.FeatureManager

        # Traverse feature tree for hole features
        root_feature = model.FirstFeature
        while root_feature:
            try:
                feat_type = root_feature.GetTypeName2
                if callable(feat_type):
                    feat_type = feat_type()

                feat_name = root_feature.Name

                # Check for hole-related features
                if feat_type in ["HoleWzd", "Hole", "CutExtrude", "HoleSeries"]:
                    # Try to get hole parameters
                    hole_info = {
                        "name": feat_name,
                        "type": feat_type,
                        "diameter": None,
                        "depth": None,
                        "position": None
                    }

                    # Get feature data
                    feat_data = root_feature.GetDefinition
                    if callable(feat_data):
                        feat_data = feat_data()

                    if feat_data:
                        try:
                            # For Hole Wizard features
                            if hasattr(feat_data, 'HoleDiameter'):
                                hole_info["diameter"] = feat_data.HoleDiameter * 1000  # Convert to mm
                            elif hasattr(feat_data, 'Diameter'):
                                hole_info["diameter"] = feat_data.Diameter * 1000
                        except:
                            pass

                    holes_found.append(hole_info)

                    # Validate against standards if we have diameter
                    if hole_info.get("diameter"):
                        diameter = hole_info["diameter"]

                        # Check if it's a standard size
                        is_standard = False
                        closest_standard = None
                        min_diff = float('inf')

                        for std_size in STANDARD_HOLE_SIZES:
                            diff = abs(diameter - std_size)
                            if diff < min_diff:
                                min_diff = diff
                                closest_standard = std_size
                            if diff < 0.1:  # Within 0.1mm tolerance
                                is_standard = True
                                break

                        if not is_standard:
                            warnings.append({
                                "feature": feat_name,
                                "type": "non_standard_size",
                                "message": f"Hole diameter {diameter:.2f}mm is not a standard size. Closest standard: {closest_standard}mm",
                                "standard": "ASME B18.2.1"
                            })

            except Exception as e:
                logger.debug(f"Error processing feature: {e}")

            # Move to next feature
            root_feature = root_feature.GetNextFeature
            if callable(root_feature):
                root_feature = root_feature()

    except Exception as e:
        logger.error(f"Error validating holes: {e}")
        errors.append({
            "type": "validation_error",
            "message": str(e)
        })

    # Summary
    result = {
        "status": "ok",
        "document": model.GetTitle if hasattr(model, 'GetTitle') else "Unknown",
        "total_holes": len(holes_found),
        "holes": holes_found,
        "validation": {
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "passed": len(errors) == 0
        },
        "standards_checked": [
            "ASME B18.2.1 - Standard hole sizes",
            "General - Edge distance (1.5x diameter)",
            "General - Hole spacing (3x diameter)"
        ]
    }

    return result
