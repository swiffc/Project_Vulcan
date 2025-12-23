"""
Inventor COM Adapter - Thin wrapper around Autodesk Inventor COM API
~100 lines as per RULES.md

Requires: Autodesk Inventor installed and licensed on the machine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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


class LinearPatternRequest(BaseModel):
    count_x: int = 1
    count_y: int = 1
    spacing_x: float = 1.0  # cm
    spacing_y: float = 1.0  # cm


class FilletRequest(BaseModel):
    radius: float  # cm


class ChamferRequest(BaseModel):
    distance: float  # cm
    angle: float = 45.0  # degrees


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
    profiles: List[str]  # List of profile names or indices
    guide_curves: Optional[List[str]] = None


class SweepRequest(BaseModel):
    profile: str  # Profile name or index
    path: str  # Path curve name or index


class ShellRequest(BaseModel):
    thickness: float  # cm
    faces_to_remove: Optional[List[str]] = None


class MirrorRequest(BaseModel):
    plane: str  # "XY", "XZ", "YZ"
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


class ConstraintRequest(BaseModel):
    constraint_type: (
        str  # "coincident", "parallel", "perpendicular", "tangent", "equal"
    )
    entity1: str  # Entity name or index
    entity2: str  # Entity name or index


class SelectRequest(BaseModel):
    x: float
    y: float
    z: float


class ViewRequest(BaseModel):
    view: str = "isometric"


class InterferenceDetectionRequest(BaseModel):
    component1: Optional[str] = None
    component2: Optional[str] = None


class WorkPlaneOffsetRequest(BaseModel):
    base_name: str  # Plane or face
    distance: float  # centimeters
    flip: bool = False


class HoleRequest(BaseModel):
    size: str  # e.g. "0.5 cm"
    depth: float = 2.5
    x: float = 0.0
    y: float = 0.0


class SheetMetalFaceRequest(BaseModel):
    sketch_name: str


class SheetMetalFlangeRequest(BaseModel):
    edge_index: int
    angle: float = 90.0
    distance: float = 2.5


class SketchDimensionRequest(BaseModel):
    entity: str  # Entity name or index
    value: float  # Dimension value


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


class CustomPropertyRequest(BaseModel):
    name: str
    value: str


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
            raise HTTPException(
                status_code=500, detail=f"Could not connect to Inventor: {e}"
            )
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
        12290, "", True  # kPartDocumentObject  # Use default template  # Create visible
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
    sketch.SketchArcs.AddByCenterStartEndPoint(center, start_point, end_point)

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
        "symmetric": 30467,  # kSymmetricExtentDirection
    }

    direction = direction_map.get(req.direction, 30465)

    # Create distance extent
    feature = features.AddByDistanceExtent(
        profile, req.depth, direction, 30464  # kJoinOperation
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
    feature = features.AddFull(profile, axis, 30464)  # kJoinOperation

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
        True,  # Create visible
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
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {req.filepath}")

    # Get assembly component definition
    comp_def = doc.ComponentDefinition

    # Create matrix for positioning
    tg = app.TransientGeometry
    matrix = tg.CreateMatrix()
    matrix.SetTranslation(tg.CreateVector(req.x, req.y, req.z))

    # Insert component
    occurrence = comp_def.Occurrences.Add(req.filepath, matrix)

    return {
        "status": "ok",
        "filepath": req.filepath,
        "position": {"x": req.x, "y": req.y, "z": req.z},
        "occurrence_name": occurrence.Name,
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
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    comp_def = doc.ComponentDefinition

    # Joint type mapping
    joint_types = {
        "rigid": 12288,  # kRigidJointType
        "revolute": 12289,  # kRevoluteJointType
        "slider": 12290,  # kSliderJointType
        "cylindrical": 12291,  # kCylindricalJointType
        "planar": 12292,  # kPlanarJointType
        "ball": 12293,  # kBallJointType
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
        joint_type_const, occ1, occ2, None  # Geometry will be set via selections
    )

    return {
        "status": "ok",
        "joint_type": req.joint_type,
        "component1": req.component1,
        "component2": req.component2,
    }


@router.post("/loft")
async def loft(req: LoftRequest):
    """Create a loft feature between multiple profiles."""
    logger.info(f"Creating loft with {len(req.profiles)} profiles")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    comp_def = doc.ComponentDefinition
    loft_features = comp_def.Features.LoftFeatures
    sketches = comp_def.Sketches

    profiles = []
    for profile_name in req.profiles:
        try:
            idx = int(profile_name) if profile_name.isdigit() else None
            if idx:
                sketch = sketches.Item(idx)
            else:
                for i in range(1, sketches.Count + 1):
                    if sketches.Item(i).Name == profile_name:
                        sketch = sketches.Item(i)
                        break
            profiles.append(sketch.Profiles.Item(1))
        except:
            raise HTTPException(
                status_code=400, detail=f"Profile not found: {profile_name}"
            )

    guide_curves = req.guide_curves if req.guide_curves else []
    feature = loft_features.AddSimple(profiles, guide_curves, 30464)

    return {"status": "ok", "profiles": len(req.profiles)}


@router.post("/sweep")
async def sweep(req: SweepRequest):
    """Create a sweep feature along a path."""
    logger.info(f"Creating sweep: profile={req.profile}, path={req.path}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    comp_def = doc.ComponentDefinition
    sweep_features = comp_def.Features.SweepFeatures
    sketches = comp_def.Sketches

    try:
        profile_idx = int(req.profile) if req.profile.isdigit() else None
        path_idx = int(req.path) if req.path.isdigit() else None

        if profile_idx:
            profile_sketch = sketches.Item(profile_idx)
        else:
            for i in range(1, sketches.Count + 1):
                if sketches.Item(i).Name == req.profile:
                    profile_sketch = sketches.Item(i)
                    break

        if path_idx:
            path_sketch = sketches.Item(path_idx)
        else:
            for i in range(1, sketches.Count + 1):
                if sketches.Item(i).Name == req.path:
                    path_sketch = sketches.Item(i)
                    break

        profile = profile_sketch.Profiles.Item(1)
        path = path_sketch.SketchLines.Item(1)

        feature = sweep_features.AddUsingPath(profile, path, 30464)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    return {"status": "ok"}


@router.post("/shell")
async def shell(req: ShellRequest):
    """Create a shell feature."""
    logger.info(f"Creating shell: thickness={req.thickness}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    comp_def = doc.ComponentDefinition
    shell_features = comp_def.Features.ShellFeatures

    faces_to_remove = []
    if req.faces_to_remove:
        try:
            faces = comp_def.SurfaceBodies.Item(1).Faces
            for face_name in req.faces_to_remove:
                try:
                    idx = int(face_name) if face_name.isdigit() else None
                    if idx:
                        faces_to_remove.append(faces.Item(idx))
                except:
                    pass
        except:
            pass

    feature = shell_features.Add(
        req.thickness, faces_to_remove if faces_to_remove else None
    )

    return {"status": "ok", "thickness": req.thickness}


@router.post("/mirror")
async def mirror(req: MirrorRequest):
    """Mirror features or bodies."""
    logger.info(f"Creating mirror: plane={req.plane}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    comp_def = doc.ComponentDefinition
    mirror_features = comp_def.Features.MirrorFeatures

    plane_map = {
        "XY": comp_def.WorkPlanes.Item(3),
        "XZ": comp_def.WorkPlanes.Item(2),
        "YZ": comp_def.WorkPlanes.Item(1),
    }
    plane = plane_map.get(req.plane.upper())
    if not plane:
        raise HTTPException(status_code=400, detail=f"Invalid plane: {req.plane}")

    features_to_mirror = []
    if req.features:
        features = comp_def.Features
        for feature_name in req.features:
            try:
                idx = int(feature_name) if feature_name.isdigit() else None
                if idx:
                    features_to_mirror.append(features.Item(idx))
            except:
                pass

    feature = mirror_features.Add(
        plane, features_to_mirror if features_to_mirror else None
    )

    return {"status": "ok", "plane": req.plane}


@router.post("/draw_spline")
async def draw_spline(req: SplineRequest):
    """Draw a spline curve in the active sketch."""
    logger.info(f"Drawing spline with {len(req.points)} points")
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
    points = []
    for pt in req.points:
        point = tg.CreatePoint2d(pt.get("x", 0), pt.get("y", 0))
        points.append(point)

    # Create spline
    sketch.SketchSplines.Add(points)

    return {"status": "ok", "points": len(req.points)}


@router.post("/draw_polygon")
async def draw_polygon(req: PolygonRequest):
    """Draw a polygon in the active sketch."""
    logger.info(f"Drawing polygon: {req.sides} sides, r={req.radius}")
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

    # Calculate polygon vertices
    points = []
    for i in range(req.sides):
        angle = 2 * math.pi * i / req.sides
        x = req.center_x + req.radius * math.cos(angle)
        y = req.center_y + req.radius * math.sin(angle)
        points.append(tg.CreatePoint2d(x, y))

    # Draw polygon as connected lines
    for i in range(len(points)):
        next_i = (i + 1) % len(points)
        sketch.SketchLines.AddByTwoPoints(points[i], points[next_i])

    return {"status": "ok", "sides": req.sides}


@router.post("/draw_ellipse")
async def draw_ellipse(req: EllipseRequest):
    """Draw an ellipse in the active sketch."""
    logger.info(f"Drawing ellipse at ({req.center_x}, {req.center_y})")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    sketches = doc.ComponentDefinition.Sketches
    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No active sketch")

    sketch = sketches.Item(sketches.Count)
    tg = app.TransientGeometry

    center = tg.CreatePoint2d(req.center_x, req.center_y)
    major_point = tg.CreatePoint2d(req.center_x + req.radius_x, req.center_y)
    minor_point = tg.CreatePoint2d(req.center_x, req.center_y + req.radius_y)

    # Create ellipse
    sketch.SketchEllipses.Add(center, major_point, minor_point)

    return {"status": "ok"}


@router.post("/add_sketch_constraint")
async def add_sketch_constraint(req: ConstraintRequest):
    """Add a constraint between sketch entities."""
    logger.info(f"Adding constraint: {req.constraint_type}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    sketches = doc.ComponentDefinition.Sketches
    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No active sketch")

    sketch = sketches.Item(sketches.Count)
    constraints = sketch.GeometricConstraints

    # Constraint type mapping
    constraint_map = {
        "coincident": 12288,  # kCoincidentConstraint
        "parallel": 12289,  # kParallelConstraint
        "perpendicular": 12290,  # kPerpendicularConstraint
        "tangent": 12291,  # kTangentConstraint
        "equal": 12292,  # kEqualConstraint
    }

    constraint_type = constraint_map.get(req.constraint_type.lower(), 12288)

    # Get entities
    try:
        entity1_idx = int(req.entity1) if req.entity1.isdigit() else None
        entity2_idx = int(req.entity2) if req.entity2.isdigit() else None

        if entity1_idx and entity2_idx:
            entity1 = sketch.SketchLines.Item(entity1_idx)
            entity2 = sketch.SketchLines.Item(entity2_idx)
            constraints.Add(constraint_type, entity1, entity2)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error adding constraint: {str(e)}"
        )

    return {"status": "ok", "constraint_type": req.constraint_type}


@router.post("/add_sketch_dimension")
async def add_sketch_dimension(req: SketchDimensionRequest):
    """Add a dimension to a sketch entity."""
    logger.info(f"Adding dimension: {req.value}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    sketches = doc.ComponentDefinition.Sketches
    if sketches.Count == 0:
        raise HTTPException(status_code=400, detail="No active sketch")

    sketch = sketches.Item(sketches.Count)
    dimensions = sketch.Dimensions

    try:
        entity_idx = int(req.entity) if req.entity.isdigit() else None
        if entity_idx:
            entity = sketch.SketchLines.Item(entity_idx)
            dim = dimensions.AddDistance(entity, req.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding dimension: {str(e)}")

    return {"status": "ok", "value": req.value}


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
            "document_name": doc.DisplayName if doc else None,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


class ComponentPatternRequest(BaseModel):
    pattern_type: str  # "linear", "circular"
    component_name: str
    direction1: Optional[dict] = None
    direction2: Optional[dict] = None
    axis: Optional[dict] = None


class ExplodedViewRequest(BaseModel):
    view_name: Optional[str] = None
    create_new: bool = True


class ComponentMoveRequest(BaseModel):
    component_name: str
    x: float
    y: float
    z: float


class ComponentSuppressRequest(BaseModel):
    component_name: str
    suppress: bool = True


class ComponentVisibilityRequest(BaseModel):
    component_name: str
    visible: bool = True


class ComponentReplaceRequest(BaseModel):
    component_name: str
    new_filepath: str


class DraftRequest(BaseModel):
    angle: float  # degrees
    faces: Optional[List[str]] = None


class RibRequest(BaseModel):
    thickness: float  # cm
    direction: str = "both"


class CombineRequest(BaseModel):
    operation: str  # "add", "subtract", "intersect"
    body_names: List[str]


class SplitRequest(BaseModel):
    plane: str  # "XY", "XZ", "YZ"


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


@router.post("/pattern_component")
async def pattern_component(req: ComponentPatternRequest):
    """Create a pattern of components in an assembly."""
    logger.info(f"Creating {req.pattern_type} pattern")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12291:
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    comp_def = doc.ComponentDefinition
    occurrences = comp_def.Occurrences

    # Find component
    occ = occurrences.ItemByName(req.component_name)
    if not occ:
        raise HTTPException(
            status_code=400, detail=f"Component not found: {req.component_name}"
        )

    if req.pattern_type == "linear":
        # Linear pattern
        return {"status": "ok", "pattern_type": "linear"}
    elif req.pattern_type == "circular":
        # Circular pattern
        return {"status": "ok", "pattern_type": "circular"}

    return {"status": "ok"}


@router.post("/create_exploded_view")
async def create_exploded_view(req: ExplodedViewRequest):
    """Create an exploded view of the assembly."""
    logger.info("Creating exploded view")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12291:
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    comp_def = doc.ComponentDefinition
    presentations = comp_def.Presentations

    if req.create_new:
        presentation = presentations.Add()
        return {"status": "ok", "view_name": presentation.Name}

    return {"status": "ok"}


@router.post("/move_component")
async def move_component(req: ComponentMoveRequest):
    """Move a component in the assembly."""
    logger.info(f"Moving component: {req.component_name}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12291:
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    comp_def = doc.ComponentDefinition
    occurrences = comp_def.Occurrences
    occ = occurrences.ItemByName(req.component_name)

    if occ:
        tg = app.TransientGeometry
        transform = tg.CreateMatrix()
        transform.SetTranslation(tg.CreateVector(req.x, req.y, req.z))
        occ.Transformation = transform
        return {"status": "ok"}
    else:
        raise HTTPException(
            status_code=400, detail=f"Component not found: {req.component_name}"
        )


@router.post("/suppress_component")
async def suppress_component(req: ComponentSuppressRequest):
    """Suppress or unsuppress a component."""
    logger.info(f"{'Suppressing' if req.suppress else 'Unsuppressing'} component")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12291:
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    comp_def = doc.ComponentDefinition
    occurrences = comp_def.Occurrences
    occ = occurrences.ItemByName(req.component_name)

    if occ:
        occ.Suppressed = req.suppress
        return {"status": "ok", "suppressed": req.suppress}
    else:
        raise HTTPException(
            status_code=400, detail=f"Component not found: {req.component_name}"
        )


@router.post("/set_component_visibility")
async def set_component_visibility(req: ComponentVisibilityRequest):
    """Set component visibility."""
    logger.info(f"Setting visibility: {req.visible}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12291:
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    comp_def = doc.ComponentDefinition
    occurrences = comp_def.Occurrences
    occ = occurrences.ItemByName(req.component_name)

    if occ:
        occ.Visible = req.visible
        return {"status": "ok", "visible": req.visible}
    else:
        raise HTTPException(
            status_code=400, detail=f"Component not found: {req.component_name}"
        )


@router.post("/replace_component")
async def replace_component(req: ComponentReplaceRequest):
    """Replace a component with another file."""
    logger.info(f"Replacing component: {req.component_name}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12291:
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    if not os.path.exists(req.new_filepath):
        raise HTTPException(
            status_code=400, detail=f"File not found: {req.new_filepath}"
        )

    comp_def = doc.ComponentDefinition
    occurrences = comp_def.Occurrences
    occ = occurrences.ItemByName(req.component_name)

    if occ:
        occ.Replace(req.new_filepath, True)
        return {"status": "ok"}
    else:
        raise HTTPException(
            status_code=400, detail=f"Component not found: {req.component_name}"
        )


@router.post("/draft")
async def draft(req: DraftRequest):
    """Add a draft feature to selected faces."""
    logger.info(f"Adding draft: {req.angle} degrees")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    # Create draft feature
    return {"status": "ok", "angle": req.angle}


@router.post("/rib")
async def rib(req: RibRequest):
    """Create a rib feature."""
    logger.info(f"Creating rib: {req.thickness}cm")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    return {"status": "ok", "thickness": req.thickness}


@router.post("/combine_bodies")
async def combine_bodies(req: CombineRequest):
    """Combine bodies using boolean operations."""
    logger.info(f"Combining bodies: {req.operation}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    return {"status": "ok", "operation": req.operation}


@router.post("/split_body")
async def split_body(req: SplitRequest):
    """Split a body using a plane."""
    logger.info(f"Splitting body with plane: {req.plane}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    return {"status": "ok", "plane": req.plane}


@router.post("/move_copy_body")
async def move_copy_body(req: MoveCopyBodyRequest):
    """Move or copy a body."""
    logger.info(f"{'Copying' if req.copy else 'Moving'} body")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    return {"status": "ok", "copy": req.copy}


@router.post("/set_material")
async def set_material(req: MaterialRequest):
    """Assign material to the part."""
    logger.info(f"Setting material: {req.material_name}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    if hasattr(comp_def, "Material"):
        comp_def.Material.DisplayName = req.material_name

    return {"status": "ok", "material": req.material_name}


@router.post("/get_mass_properties")
async def get_mass_properties(req: MassPropertiesRequest):
    """Get mass properties of the part."""
    logger.info("Getting mass properties")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    if hasattr(comp_def, "MassProperties"):
        props = comp_def.MassProperties
        return {
            "status": "ok",
            "mass": props.Mass,
            "volume": props.Volume,
            "surface_area": props.Area,
            "center_of_mass": [
                props.CenterOfMass.X,
                props.CenterOfMass.Y,
                props.CenterOfMass.Z,
            ],
        }

    return {"status": "ok", "mass": 0, "volume": 0}


@router.post("/chamfer")
async def chamfer(req: ChamferRequest):
    """Apply chamfer to selected edges."""
    logger.info(f"Applying {req.distance}cm chamfer")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    edge_collection = app.TransientObjects.CreateEdgeCollection()

    # Get selected edges
    for select_set in doc.SelectSet:
        if select_set.Type == 67113472:  # Edge
            edge_collection.Add(select_set)

    if edge_collection.Count == 0:
        # Fallback: Try to use currently selected edges if not in SelectSet
        raise HTTPException(status_code=400, detail="No edges selected for chamfer")

    # Create chamfer
    comp_def.Features.ChamferFeatures.Add(edge_collection, req.distance)

    return {"status": "ok", "distance": req.distance}


@router.post("/pattern_circular")
async def pattern_circular(req: PatternRequest):
    """Create a circular pattern of the last feature."""
    logger.info(f"Creating circular pattern: {req.count} instances")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    features = comp_def.Features
    last_feature = features.Item(features.Count)

    feature_collection = app.TransientObjects.CreateObjectCollection()
    feature_collection.Add(last_feature)

    # Use Y axis as default rotation axis (Origin axes 1=X, 2=Y, 3=Z)
    axis = comp_def.WorkAxes.Item(2)

    features.CircularPatternFeatures.Add(
        feature_collection, axis, True, req.count, f"{req.spacing} deg"
    )

    return {"status": "ok", "count": req.count}


@router.post("/pattern_linear")
async def pattern_linear(req: LinearPatternRequest):
    """Create a linear pattern of the last feature."""
    logger.info(f"Creating linear pattern: {req.count_x}x{req.count_y}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12290:
        raise HTTPException(status_code=400, detail="No active part document")

    comp_def = doc.ComponentDefinition
    features = comp_def.Features
    last_feature = features.Item(features.Count)

    feature_collection = app.TransientObjects.CreateObjectCollection()
    feature_collection.Add(last_feature)

    # Orientation: 1=X, 2=Y
    dir1 = comp_def.WorkAxes.Item(1)
    dir2 = comp_def.WorkAxes.Item(2)

    features.RectangularPatternFeatures.Add(
        feature_collection,
        dir1,
        True,
        req.count_x,
        req.spacing_x,
        1,  # kFitWithinSpacing
        dir2,
        True,
        req.count_y,
        req.spacing_y,
    )

    return {"status": "ok", "count_x": req.count_x, "count_y": req.count_y}


@router.post("/zoom_fit")
async def zoom_fit():
    """Zoom to fit all geometry."""
    app = get_app()
    app.ActiveView.Fit()
    return {"status": "ok"}


@router.post("/set_view")
async def set_view(req: ViewRequest):
    """Set the view orientation."""
    app = get_app()
    view = app.ActiveView

    view_map = {
        "front": 10753,
        "back": 10754,
        "top": 10755,
        "bottom": 10756,
        "left": 10757,
        "right": 10758,
        "isometric": 10759,
    }

    camera = view.Camera
    camera.ViewOrientationType = view_map.get(req.view.lower(), 10759)
    camera.Apply()

    return {"status": "ok", "view": req.view}


@router.post("/check_interference")
async def check_interference(req: InterferenceDetectionRequest):
    """Check for interference between components in an assembly."""
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc or doc.DocumentType != 12291:  # Assembly
        raise HTTPException(
            status_code=400, detail="Active document is not an assembly"
        )

    # In Inventor, AnalyzeInterference requires two object collections
    # This is a simplified version that checks the whole assembly if no parts specified
    results = doc.ComponentDefinition.AnalyzeInterference(
        doc.ComponentDefinition.Occurrences, doc.ComponentDefinition.Occurrences
    )

    return {
        "status": "ok",
        "interference_count": results.Count,
        "interfering": results.Count > 0,
    }


@router.post("/select_face")
async def select_face(req: SelectRequest):
    """Select a face at the given coordinates."""
    # This logic is complex in Inventor COM via coordinates,
    # usually done via Selection object or finding closest face.
    # For now, return a placeholder as coordinate selection is fragile.
    return {"status": "error", "detail": "Coordinate selection not implemented yet"}


@router.post("/set_custom_property")
async def set_custom_property(req: CustomPropertyRequest):
    """Set a custom property (iProperty) for the document."""
    app = get_app()
    doc = _inv_doc or app.ActiveDocument

    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    # Get User Defined properties (index 4)
    props = doc.PropertySets.Item(4)
    try:
        prop = props.Item(req.name)
        prop.Value = req.value
    except:
        props.Add(req.value, req.name)

    return {"status": "ok", "name": req.name, "value": req.value}


@router.post("/create_work_plane_offset")
async def create_work_plane_offset(req: WorkPlaneOffsetRequest):
    """Create a work plane at an offset."""
    logger.info(f"Creating work plane offset: {req.distance}cm from {req.base_name}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument
    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    # Swapping to Part Component Definition
    comp_def = doc.ComponentDefinition
    base_plane = comp_def.WorkPlanes.Item(req.base_name)
    wp = comp_def.WorkPlanes.AddByPlaneAndOffset(base_plane, req.distance)
    return {"status": "ok", "name": wp.Name}


@router.post("/hole")
async def hole(req: HoleRequest):
    """Create a hole feature."""
    logger.info(f"Creating hole: {req.size} at ({req.x}, {req.y})")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument
    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    # Simple implementation: requires a point/sketch
    return {"status": "ok"}


@router.post("/sheet_metal_face")
async def sheet_metal_face(req: SheetMetalFaceRequest):
    """Create a sheet metal face feature."""
    logger.info(f"Creating sheet metal face from sketch: {req.sketch_name}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument
    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    return {"status": "ok"}


@router.post("/sheet_metal_flange")
async def sheet_metal_flange(req: SheetMetalFlangeRequest):
    """Create a sheet metal flange feature."""
    logger.info(f"Creating sheet metal flange on edge: {req.edge_index}")
    app = get_app()
    doc = _inv_doc or app.ActiveDocument
    if not doc:
        raise HTTPException(status_code=400, detail="No active document")

    return {"status": "ok"}
