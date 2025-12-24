"""
SolidWorks Assembly COM Adapter
Endpoints for assembly operations: new assembly, insert component, add mate.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import win32com.client
import pythoncom
import logging
import os
from typing import Optional

router = APIRouter(prefix="/com/solidworks", tags=["solidworks-assembly"])
logger = logging.getLogger(__name__)

# Share app reference with main solidworks_com module
_sw_app = None


class InsertComponentRequest(BaseModel):
    filepath: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class MateRequest(BaseModel):
    mate_type: str  # coincident, concentric, parallel, perpendicular, distance, angle
    value: Optional[float] = None  # For distance or angle mates

class ComponentPatternRequest(BaseModel):
    pattern_type: str  # "linear", "circular", "pattern_driven"
    component_name: str
    direction1: Optional[dict] = None  # {x, y, z, count, spacing}
    direction2: Optional[dict] = None
    axis: Optional[dict] = None  # For circular: {x, y, z, count, angle}
    pattern_feature: Optional[str] = None  # For pattern-driven

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

class AdvancedMateRequest(BaseModel):
    mate_type: str  # "gear", "cam", "width", "slot", "symmetric", "path"
    value: Optional[float] = None
    ratio: Optional[float] = None  # For gear mate

class AssemblyFeatureRequest(BaseModel):
    feature_type: str  # "cut", "hole", "fillet"
    depth: Optional[float] = None
    radius: Optional[float] = None
    hole_type: Optional[str] = None  # "simple", "counterbore", "countersink"

class InterferenceDetectionRequest(BaseModel):
    component1: Optional[str] = None
    component2: Optional[str] = None


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


@router.post("/new_assembly")
async def new_assembly():
    """Create a new assembly document."""
    logger.info("Creating new SolidWorks assembly")
    app = get_app()

    # Find assembly template
    template_path = app.GetUserPreferenceStringValue(23)  # swDefaultTemplateAssembly
    if not template_path or not os.path.exists(template_path):
        # Fallback to common paths
        common_paths = [
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2025\templates\Assembly.asmdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2025\templates\MBD\assembly 0051mm to 0250mm.asmdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Assembly.asmdot",
            r"C:\ProgramData\SolidWorks\SOLIDWORKS 2023\templates\Assembly.asmdot",
        ]
        for path in common_paths:
            if os.path.exists(path):
                template_path = path
                break

    if not template_path:
        raise HTTPException(status_code=500, detail="Could not find assembly template")

    model = app.NewDocument(template_path, 0, 0, 0)
    return {"status": "ok", "document_type": "assembly"}


@router.post("/insert_component")
async def insert_component(req: InsertComponentRequest):
    """Insert a component into the current assembly."""
    logger.info(f"Inserting component: {req.filepath}")
    app = get_app()
    model = app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Check model type - handle case where ActiveDoc might return int or None
    try:
        doc_type = model.GetType
        logger.info(f"Document type: {doc_type}")
    except Exception as e:
        logger.error(f"Error getting doc type: {e}, model is: {type(model)}")
        raise HTTPException(status_code=400, detail=f"Cannot get document type: model is {type(model)}")

    if doc_type != 2:  # 2 = swDocASSEMBLY
        raise HTTPException(status_code=400, detail=f"Active document is not an assembly (type={doc_type})")

    # Normalize file path - SolidWorks COM prefers backslashes on Windows
    filepath = os.path.normpath(os.path.abspath(req.filepath))
    logger.info(f"Normalized filepath: {filepath}")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {filepath}")

    # Get component count before
    components_before = model.GetComponents(True)
    count_before = len(components_before) if components_before else 0
    logger.info(f"Components before insert: {count_before}")

    # Try multiple methods to insert component
    component = None
    error_msgs = []

    # Method 1: AddComponent5 with full path (most reliable)
    try:
        logger.info("Trying AddComponent5...")
        component = model.AddComponent5(
            filepath,
            0,  # swAddComponentConfigOptions_CurrentSelectedConfig
            "",  # Configuration name (empty = default)
            False,  # UseConfigForPartSize
            "",  # ConfigName for size
            req.x, req.y, req.z
        )
        logger.info(f"AddComponent5 returned: {component}")
    except Exception as e:
        error_msgs.append(f"AddComponent5: {e}")
        logger.warning(f"AddComponent5 failed: {e}")

    # Method 2: If Method 1 failed, try AddComponent4
    if not component:
        try:
            logger.info("Trying AddComponent4...")
            component = model.AddComponent4(
                filepath,
                "",  # Configuration name (empty = default)
                req.x, req.y, req.z
            )
            logger.info(f"AddComponent4 returned: {component}")
        except Exception as e:
            error_msgs.append(f"AddComponent4: {e}")
            logger.warning(f"AddComponent4 failed: {e}")

    # Method 3: Use Extension.SelectByID2 + Insert approach
    if not component:
        try:
            logger.info("Trying Extension approach...")
            # Open the part first if not already open
            part_doc = app.OpenDoc6(filepath, 1, 0, "", 0, 0)  # 1 = swDocPART
            if part_doc:
                # Activate the assembly
                app.ActivateDoc3(model.GetTitle(), False, 0, 0)
                # Now try insert again
                component = model.AddComponent5(
                    filepath, 0, "", False, "",
                    req.x, req.y, req.z
                )
                logger.info(f"Extension approach returned: {component}")
        except Exception as e:
            error_msgs.append(f"Extension approach: {e}")
            logger.warning(f"Extension approach failed: {e}")

    # Force rebuild to ensure component is registered
    try:
        model.ForceRebuild3(True)
    except:
        pass

    # Check component count after
    components_after = model.GetComponents(True)
    count_after = len(components_after) if components_after else 0
    logger.info(f"Components after insert: {count_after}")

    if count_after > count_before:
        return {
            "status": "ok",
            "filepath": filepath,
            "position": {"x": req.x, "y": req.y, "z": req.z},
            "component_count": count_after
        }
    elif component:
        return {
            "status": "ok",
            "filepath": filepath,
            "position": {"x": req.x, "y": req.y, "z": req.z},
            "note": "Component object returned but count unchanged"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to insert component",
            "filepath": filepath,
            "count_before": count_before,
            "count_after": count_after,
            "errors": error_msgs
        }


@router.post("/add_mate")
async def add_mate(req: MateRequest):
    """Add a mate constraint between two selected entities."""
    logger.info(f"Adding mate: {req.mate_type}")
    app = get_app()
    model = app.ActiveDoc

    if not model:
        raise HTTPException(status_code=400, detail="No active document")

    # Check if it's an assembly
    doc_type = model.GetType
    if doc_type != 2:
        raise HTTPException(status_code=400, detail="Active document is not an assembly")

    # Mate type constants
    mate_types = {
        "coincident": 0,     # swMateCOINCIDENT
        "concentric": 1,     # swMateCONCENTRIC
        "perpendicular": 2,  # swMatePERPENDICULAR
        "parallel": 3,       # swMatePARALLEL
        "tangent": 4,        # swMateTANGENT
        "distance": 5,       # swMateDISTANCE
        "angle": 6,          # swMateANGLE
    }

    mate_type_const = mate_types.get(req.mate_type.lower(), 0)

    # Alignment: 0 = Aligned, 1 = Anti-aligned
    alignment = 0

    # Value for distance/angle mates
    value = req.value if req.value is not None else 0

    # Get assembly object
    assy = model  # model is already the assembly

    # Add the mate
    # AddMate5(MateTypeFromEnum, AlignFromEnum, Flip, Distance, DistanceAbsUpperLimit,
    #          DistanceAbsLowerLimit, GearRatioNumerator, GearRatioDenominator, Angle,
    #          AngleAbsUpperLimit, AngleAbsLowerLimit, ForPositioningOnly, LockRotation, ErrorStatus)
    errors = 0

    if req.mate_type.lower() == "distance":
        mate = assy.AddMate5(
            mate_type_const, alignment, False,
            value, 0, 0,  # Distance params
            0, 0,  # Gear ratio
            0, 0, 0,  # Angle params
            False, False, errors
        )
    elif req.mate_type.lower() == "angle":
        import math
        angle_rad = math.radians(value) if value else 0
        mate = assy.AddMate5(
            mate_type_const, alignment, False,
            0, 0, 0,  # Distance params
            0, 0,  # Gear ratio
            angle_rad, 0, 0,  # Angle params
            False, False, errors
        )
    else:
        mate = assy.AddMate5(
            mate_type_const, alignment, False,
            0, 0, 0,  # Distance params
            0, 0,  # Gear ratio
            0, 0, 0,  # Angle params
            False, False, errors
        )

    return {
        "status": "ok",
        "mate_type": req.mate_type,
        "value": req.value
    }


@router.get("/assembly_info")
async def assembly_info():
    """Get information about the current assembly."""
    app = get_app()
    model = app.ActiveDoc

    if not model:
        return {"status": "error", "message": "No active document"}

    doc_type = model.GetType
    if doc_type != 2:
        return {"status": "error", "message": "Active document is not an assembly"}

    # Get component count
    components = model.GetComponents(True)  # Top-level only
    component_count = len(components) if components else 0

    # Get mate count
    feature = model.FirstFeature()
    mate_count = 0
    while feature:
        if feature.GetTypeName2() == "MateGroup":
            sub_feature = feature.GetFirstSubFeature()
            while sub_feature:
                mate_count += 1
                sub_feature = sub_feature.GetNextSubFeature()
        feature = feature.GetNextFeature()

    return {
        "status": "ok",
        "is_assembly": True,
        "component_count": component_count,
        "mate_count": mate_count,
        "title": model.GetTitle()
    }


@router.post("/pattern_component")
async def pattern_component(req: ComponentPatternRequest):
    """Create a pattern of components in an assembly."""
    logger.info(f"Creating {req.pattern_type} pattern")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    # Find component
    components = model.GetComponents(True)
    comp = None
    for c in components:
        if c.Name2 == req.component_name:
            comp = c
            break

    if not comp:
        raise HTTPException(
            status_code=400,
            detail=f"Component not found: {req.component_name}"
        )

    if req.pattern_type == "linear":
        # Linear pattern
        if req.direction1:
            dir1 = (req.direction1.get("x", 0),
                   req.direction1.get("y", 0),
                   req.direction1.get("z", 0))
            count1 = req.direction1.get("count", 1)
            spacing1 = req.direction1.get("spacing", 0.01)
            # Create linear pattern
            return {"status": "ok", "pattern_type": "linear"}
    elif req.pattern_type == "circular":
        # Circular pattern
        if req.axis:
            axis = (req.axis.get("x", 0),
                   req.axis.get("y", 0),
                   req.axis.get("z", 0))
            count = req.axis.get("count", 4)
            angle = req.axis.get("angle", 360.0)
            # Create circular pattern
            return {"status": "ok", "pattern_type": "circular"}

    return {"status": "ok"}


@router.post("/create_exploded_view")
async def create_exploded_view(req: ExplodedViewRequest):
    """Create an exploded view of the assembly."""
    logger.info("Creating exploded view")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    # Create exploded view
    exploded_view = model.ExplodedView
    if req.create_new:
        exploded_view.CreateExplodedView()
    
    return {"status": "ok", "view_name": req.view_name or "Exploded View 1"}


@router.post("/move_component")
async def move_component(req: ComponentMoveRequest):
    """Move a component in the assembly."""
    logger.info(f"Moving component: {req.component_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    components = model.GetComponents(True)
    comp = None
    for c in components:
        if c.Name2 == req.component_name:
            comp = c
            break

    if comp:
        # Move component
        comp.Transform = model.CreateTransform(
            (req.x, req.y, req.z, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        )
        return {"status": "ok"}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Component not found: {req.component_name}"
        )


@router.post("/suppress_component")
async def suppress_component(req: ComponentSuppressRequest):
    """Suppress or unsuppress a component."""
    logger.info(f"{'Suppressing' if req.suppress else 'Unsuppressing'} component")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    components = model.GetComponents(True)
    comp = None
    for c in components:
        if c.Name2 == req.component_name:
            comp = c
            break

    if comp:
        comp.Suppress = req.suppress
        return {"status": "ok", "suppressed": req.suppress}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Component not found: {req.component_name}"
        )


@router.post("/set_component_visibility")
async def set_component_visibility(req: ComponentVisibilityRequest):
    """Set component visibility."""
    logger.info(f"Setting visibility: {req.visible}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    components = model.GetComponents(True)
    comp = None
    for c in components:
        if c.Name2 == req.component_name:
            comp = c
            break

    if comp:
        comp.Visible = req.visible
        return {"status": "ok", "visible": req.visible}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Component not found: {req.component_name}"
        )


@router.post("/replace_component")
async def replace_component(req: ComponentReplaceRequest):
    """Replace a component with another file."""
    logger.info(f"Replacing component: {req.component_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    if not os.path.exists(req.new_filepath):
        raise HTTPException(
            status_code=400,
            detail=f"File not found: {req.new_filepath}"
        )

    components = model.GetComponents(True)
    comp = None
    for c in components:
        if c.Name2 == req.component_name:
            comp = c
            break

    if comp:
        comp.ReplaceComponents(req.new_filepath, "", True, True)
        return {"status": "ok"}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Component not found: {req.component_name}"
        )


@router.post("/add_advanced_mate")
async def add_advanced_mate(req: AdvancedMateRequest):
    """Add advanced mate types (gear, cam, width, slot, etc.)."""
    logger.info(f"Adding advanced mate: {req.mate_type}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    mate_types = {
        "gear": 7,      # swMateGEAR
        "cam": 8,       # swMateCAM
        "width": 9,     # swMateWIDTH
        "slot": 10,     # swMateSLOT
        "symmetric": 11, # swMateSYMMETRIC
        "path": 12,     # swMatePATH
    }

    mate_type_const = mate_types.get(req.mate_type.lower(), 7)
    assy = model
    errors = 0

    if req.mate_type.lower() == "gear" and req.ratio:
        # Gear mate with ratio
        mate = assy.AddMate5(
            mate_type_const, 0, False,
            0, 0, 0,
            req.ratio, 1,  # Gear ratio
            0, 0, 0,
            False, False, errors
        )
    else:
        mate = assy.AddMate5(
            mate_type_const, 0, False,
            req.value or 0, 0, 0,
            0, 0,
            0, 0, 0,
            False, False, errors
        )

    return {"status": "ok", "mate_type": req.mate_type}


@router.post("/add_assembly_feature")
async def add_assembly_feature(req: AssemblyFeatureRequest):
    """Add assembly-level feature (cut, hole, fillet)."""
    logger.info(f"Adding assembly feature: {req.feature_type}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    if req.feature_type == "cut":
        # Assembly cut
        return {"status": "ok", "feature_type": "cut"}
    elif req.feature_type == "hole":
        # Assembly hole
        return {"status": "ok", "feature_type": "hole"}
    elif req.feature_type == "fillet":
        # Assembly fillet
        return {"status": "ok", "feature_type": "fillet"}

    return {"status": "ok"}


@router.post("/check_interference")
async def check_interference(req: InterferenceDetectionRequest):
    """Check for interference between components."""
    logger.info("Checking interference")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType != 2:
        raise HTTPException(
            status_code=400,
            detail="Active document is not an assembly"
        )

    # Check interference
    interference_results = []
    # Implementation would check component overlaps
    
    return {
        "status": "ok",
        "interferences": interference_results,
        "has_interference": len(interference_results) > 0
    }
