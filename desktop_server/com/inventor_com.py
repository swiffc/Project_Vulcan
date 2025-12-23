"""
Inventor COM Adapter - Thin wrapper around Autodesk Inventor COM API
~100 lines as per RULES.md

Requires: Autodesk Inventor installed and licensed on the machine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import win32com.client
import pythoncom
import logging
import os

router = APIRouter(prefix="/com/inventor", tags=["inventor"])
logger = logging.getLogger(__name__)

# Global Inventor application reference
_inv_app = None
_inv_doc = None


class SketchRequest(BaseModel):
    plane: str = "XY"  # XY, XZ, YZ

class CircleRequest(BaseModel):
    x: float  # Center X (cm)
    y: float  # Center Y (cm)
    radius: float  # Radius (cm)

class RectangleRequest(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class ExtrudeRequest(BaseModel):
    depth: float  # Depth in cm
    direction: str = "positive"  # positive, negative, symmetric

class RevolveRequest(BaseModel):
    angle: float = 360.0  # Degrees

class PatternRequest(BaseModel):
    count: int
    spacing: float  # cm

class FilletRequest(BaseModel):
    radius: float  # cm

class LineRequest(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class ArcRequest(BaseModel):
    center_x: float
    center_y: float
    radius: float
    start_angle: float  # degrees
    end_angle: float  # degrees

class LoftRequest(BaseModel):
    profiles: list  # List of profile names or indices
    guide_curves: Optional[list] = None

class SweepRequest(BaseModel):
    profile: str  # Profile name or index
    path: str  # Path curve name or index

class ShellRequest(BaseModel):
    thickness: float  # cm
    faces_to_remove: Optional[list] = None

class SaveRequest(BaseModel):
    filepath: str

class OpenRequest(BaseModel):
    filepath: str

class ExportRequest(BaseModel):
    filepath: str
    format: str  # "step", "iges", "stl", "pdf", etc.

class InsertComponentRequest(BaseModel):
    filepath: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

class JointRequest(BaseModel):
    joint_type: str  # rigid, revolute, slider, cylindrical, planar, ball, etc.
    component1: str
    component2: str
    geometry1: str  # Face or edge name
    geometry2: str  # Face or edge name


def get_app():
    """Get or create Inventor application instance."""
    global _inv_app
    if _inv_app is None:
        pythoncom.CoInitialize()
        try:
            _inv_app = win32com.client.Dispatch("Inventor.Application")
            _inv_app.Visible = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not connect to Inventor: {e}")
    return _inv_app


@router.post("/connect")
async def connect():
    """Connect to running Inventor instance."""
    logger.info("Connecting to Inventor")
    app = get_app()
    return {"status": "ok", "version": app.SoftwareVersion.DisplayVersion}


@router.post("/new_part")
async def new_part():
    """Create a new part document."""
    global _inv_doc
    logger.info("Creating new Inventor part")
    app = get_app()

    # Create new part document
    _inv_doc = app.Documents.Add(
        12290,  # kPartDocumentObject
        "",  # Use default template
        True  # Create visible
    )

    return {"status": "ok", "document_type": "part"}


@router.post("/create_sketch")
async def create_sketch(req: SketchRequest):
    """Start a new sketch on the specified plane."""
    global _inv_doc
    logger.info(f"Creating sketch on {req.plane} plane")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    # Get the component definition
    comp_def = doc.ComponentDefinition

    # Get the work plane
    plane_map = {
        "XY": comp_def.WorkPlanes.Item(3),  # XY Plane
        "XZ": comp_def.WorkPlanes.Item(2),  # XZ Plane
        "YZ": comp_def.WorkPlanes.Item(1),  # YZ Plane
    }

    plane = plane_map.get(req.plane.upper())
    if not plane:
        raise HTTPException(status_code=400, detail=f"Invalid plane: {req.plane}")

    # Create sketch
    sketch = comp_def.Sketches.Add(plane)

    return {"status": "ok", "plane": req.plane}


@router.post("/draw_circle")
async def draw_circle(req: CircleRequest):
    """Draw a circle in the active sketch."""
    logger.info(f"Drawing circle at ({req.x}, {req.y}) r={req.radius}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    # Get active sketch
    sketches = doc.ComponentDefinition.Sketches
    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No active sketch")

    sketch = sketches.Item(sketches.Count)  # Get last sketch

    # Create a transient geometry point for center
    tg = app.TransientGeometry
    center = tg.CreatePoint2d(req.x, req.y)

    # Draw circle
    sketch.SketchCircles.AddByCenterRadius(center, req.radius)

    return {"status": "ok", "center": {"x": req.x, "y": req.y}, "radius": req.radius}


@router.post("/draw_rectangle")
async def draw_rectangle(req: RectangleRequest):
    """Draw a rectangle in the active sketch."""
    logger.info(f"Drawing rectangle from ({req.x1}, {req.y1}) to ({req.x2}, {req.y2})")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    sketches = doc.ComponentDefinition.Sketches
    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No active sketch")

    sketch = sketches.Item(sketches.Count)
    tg = app.TransientGeometry

    # Create corner points
    p1 = tg.CreatePoint2d(req.x1, req.y1)
    p2 = tg.CreatePoint2d(req.x2, req.y2)

    # Draw rectangle using two corner points
    sketch.SketchLines.AddAsTwoPointRectangle(p1, p2)

    return {"status": "ok"}


@router.post("/draw_line")
async def draw_line(req: LineRequest):
    """Draw a line in the active sketch."""
    logger.info(f"Drawing line from ({req.x1}, {req.y1}) to ({req.x2}, {req.y2})")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    sketches = doc.ComponentDefinition.Sketches
    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No active sketch")

    sketch = sketches.Item(sketches.Count)
    tg = app.TransientGeometry

    # Create points
    p1 = tg.CreatePoint2d(req.x1, req.y1)
    p2 = tg.CreatePoint2d(req.x2, req.y2)

    # Draw line
    sketch.SketchLines.AddByTwoPoints(p1, p2)

    return {"status": "ok"}


@router.post("/draw_arc")
async def draw_arc(req: ArcRequest):
    """Draw an arc in the active sketch."""
    logger.info(f"Drawing arc at ({req.center_x}, {req.center_y}) r={req.radius}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    sketches = doc.ComponentDefinition.Sketches
    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No active sketch")

    sketch = sketches.Item(sketches.Count)
    tg = app.TransientGeometry

    import math
    center = tg.CreatePoint2d(req.center_x, req.center_y)
    start_angle_rad = math.radians(req.start_angle)
    end_angle_rad = math.radians(req.end_angle)

    # Calculate start and end points
    start_x = req.center_x + req.radius * math.cos(start_angle_rad)
    start_y = req.center_y + req.radius * math.sin(start_angle_rad)
    end_x = req.center_x + req.radius * math.cos(end_angle_rad)
    end_y = req.center_y + req.radius * math.sin(end_angle_rad)

    start_point = tg.CreatePoint2d(start_x, start_y)
    end_point = tg.CreatePoint2d(end_x, end_y)

    # Draw arc
    sketch.SketchArcs.AddByCenterStartEndPoint(
        center, start_point, end_point
    )

    return {"status": "ok"}


@router.post("/extrude")
async def extrude(req: ExtrudeRequest):
    """Extrude the current sketch profile."""
    logger.info(f"Extruding depth={req.depth}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    comp_def = doc.ComponentDefinition
    sketches = comp_def.Sketches

    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No sketch to extrude")

    sketch = sketches.Item(sketches.Count)

    # Get profile from sketch
    if sketch.Profiles.Count == 0:
        raise HTTPException(status_code=400, detail="No profile in sketch")

    profile = sketch.Profiles.AddForSolid()

    # Create extrusion
    features = comp_def.Features.ExtrudeFeatures

    # Direction mapping
    direction_map = {
        "positive": 30465,  # kPositiveExtentDirection
        "negative": 30466,  # kNegativeExtentDirection
        "symmetric": 30467  # kSymmetricExtentDirection
    }

    direction = direction_map.get(req.direction, 30465)

    # Create distance extent
    feature = features.AddByDistanceExtent(
        profile,
        req.depth,
        direction,
        30464  # kJoinOperation
    )

    return {"status": "ok", "depth": req.depth}


@router.post("/revolve")
async def revolve(req: RevolveRequest):
    """Revolve the current sketch profile."""
    logger.info(f"Revolving angle={req.angle}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    comp_def = doc.ComponentDefinition
    sketches = comp_def.Sketches

    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No sketch to revolve")

    sketch = sketches.Item(sketches.Count)
    profile = sketch.Profiles.AddForSolid()

    # Get axis line (first line in sketch as axis)
    axis = sketch.SketchLines.Item(1)

    # Create revolve
    import math
    angle_rad = math.radians(req.angle)

    features = comp_def.Features.RevolveFeatures
    feature = features.AddFull(
        profile,
        axis,
        30464  # kJoinOperation
    )

    return {"status": "ok", "angle": req.angle}


@router.post("/save")
async def save(req: SaveRequest):
    """Save the current document."""
    logger.info(f"Saving to {req.filepath}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    # Ensure directory exists
    os.makedirs(os.path.dirname(req.filepath), exist_ok=True)

    doc.SaveAs(req.filepath, False)

    return {"status": "ok", "filepath": req.filepath}


@router.post("/new_assembly")
async def new_assembly():
    """Create a new assembly document."""
    global _inv_doc
    logger.info("Creating new Inventor assembly")
    app = get_app()

    # Create new assembly document
    _inv_doc = app.Documents.Add(
        12291,  # kAssemblyDocumentObject
        "",  # Use default template
        True  # Create visible
    )

    return {"status": "ok", "document_type": "assembly"}


@router.post("/insert_component")
async def insert_component(req: InsertComponentRequest):
    """Insert a component into the current assembly."""
    logger.info(f"Inserting component: {req.filepath}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    # Check if it's an assembly
    if doc.DocumentType != 12291:  # kAssemblyDocumentObject
        raise HTTPException(status_code=400, detail="Active document is not an assembly")

    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {req.filepath}")

    # Get assembly component definition
    comp_def = doc.ComponentDefinition

    # Create matrix for positioning
    tg = app.TransientGeometry
    matrix = tg.CreateMatrix()
    matrix.SetTranslation(tg.CreateVector(req.x, req.y, req.z))

    # Insert component
    occurrence = comp_def.Occurrences.Add(
        req.filepath,
        matrix
    )

    return {
        "status": "ok",
        "filepath": req.filepath,
        "position": {"x": req.x, "y": req.y, "z": req.z},
        "occurrence_name": occurrence.Name
    }


@router.post("/add_joint")
async def add_joint(req: JointRequest):
    """Add a joint constraint between two components in an assembly."""
    logger.info(f"Adding joint: {req.joint_type}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    if doc.DocumentType != 12291:  # kAssemblyDocumentObject
        raise HTTPException(status_code=400, detail="Active document is not an assembly")

    comp_def = doc.ComponentDefinition

    # Joint type mapping
    joint_types = {
        "rigid": 12288,      # kRigidJointType
        "revolute": 12289,   # kRevoluteJointType
        "slider": 12290,     # kSliderJointType
        "cylindrical": 12291, # kCylindricalJointType
        "planar": 12292,     # kPlanarJointType
        "ball": 12293,       # kBallJointType
    }

    joint_type_const = joint_types.get(req.joint_type.lower(), 12288)

    # Get components
    occ1 = comp_def.Occurrences.ItemByName(req.component1)
    occ2 = comp_def.Occurrences.ItemByName(req.component2)

    if not occ1 or not occ2:
        raise HTTPException(status_code=400, detail="Component not found")

    # Create joint
    joints = comp_def.Joints
    joint = joints.Add(
        joint_type_const,
        occ1,
        occ2,
        None  # Geometry will be set via selections
    )

    return {
        "status": "ok",
        "joint_type": req.joint_type,
        "component1": req.component1,
        "component2": req.component2
    }


@router.get("/status")
async def status():
    """Get Inventor status."""
    try:
        app = get_app()
        doc = app.ActiveDocument
        return {
            "connected": True,
            "version": app.SoftwareVersion.DisplayVersion,
            "has_document": doc is not None,
            "document_name": doc.DisplayName if doc else None
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
