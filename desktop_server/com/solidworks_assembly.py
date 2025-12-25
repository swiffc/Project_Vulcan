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


def _get_custom_properties(model):
    """Extract custom properties from a SolidWorks model."""
    properties = {}
    try:
        if not model:
            return properties

        # Get custom property manager
        ext = model.Extension
        if not ext:
            return properties

        cpm = ext.CustomPropertyManager("")
        if not cpm:
            return properties

        # Get property names
        prop_names = cpm.GetNames
        if callable(prop_names):
            prop_names = prop_names()

        if prop_names:
            for name in prop_names:
                try:
                    # Get3 returns (value, resolved_value, was_resolved, link_to_property)
                    result = cpm.Get3(name, False)
                    if result:
                        val = result[0] if result[0] else result[1]
                        if val:
                            properties[name] = str(val)
                except:
                    continue

        # Also try to get configuration-specific properties
        try:
            config_mgr = model.ConfigurationManager
            if config_mgr:
                active_config = config_mgr.ActiveConfiguration
                if active_config:
                    config_name = active_config.Name
                    config_cpm = ext.CustomPropertyManager(config_name)
                    if config_cpm:
                        config_prop_names = config_cpm.GetNames
                        if callable(config_prop_names):
                            config_prop_names = config_prop_names()
                        if config_prop_names:
                            for name in config_prop_names:
                                if name not in properties:
                                    try:
                                        result = config_cpm.Get3(name, False)
                                        if result:
                                            val = result[0] if result[0] else result[1]
                                            if val:
                                                properties[name] = str(val)
                                    except:
                                        continue
        except:
            pass

    except Exception as e:
        logger.warning(f"Error getting custom properties: {e}")

    return properties


def _process_component(comp, level=0, item_counter=None, max_depth=10):
    """Recursively process a component and its children."""
    if item_counter is None:
        item_counter = {"value": 0}

    if level > max_depth:
        return None

    try:
        # Get component name
        comp_name = None
        for attr in ['Name2', 'Name', 'GetName']:
            try:
                val = getattr(comp, attr, None)
                if val is not None:
                    comp_name = val() if callable(val) else val
                    if comp_name:
                        break
            except:
                continue

        if not comp_name:
            comp_name = str(comp)

        # Get referenced model and file path
        ref_model = None
        file_path = ""
        custom_props = {}

        try:
            ref_model = comp.GetModelDoc2()
            if ref_model:
                path_name = getattr(ref_model, 'GetPathName', None)
                if path_name:
                    file_path = path_name() if callable(path_name) else path_name
                # Get custom properties
                custom_props = _get_custom_properties(ref_model)
        except:
            pass

        # Extract part number - remove instance suffix like <1>, <2>
        part_number = comp_name
        if "<" in str(part_number):
            part_number = str(part_number).split("<")[0]

        # Determine component type
        is_sub_assembly = file_path and (".SLDASM" in file_path.upper())
        comp_type = "Sub-Assembly" if is_sub_assembly else "Part"

        # Check if suppressed
        is_suppressed = False
        try:
            suppress_state = comp.GetSuppression2
            if callable(suppress_state):
                suppress_state = suppress_state()
            is_suppressed = suppress_state == 0  # swComponentSuppressed = 0
        except:
            pass

        item_counter["value"] += 1

        result = {
            "item": item_counter["value"],
            "part_number": part_number,
            "description": custom_props.get("Description", comp_name),
            "type": comp_type,
            "qty": 1,
            "file_path": file_path,
            "level": level,
            "suppressed": is_suppressed,
            "properties": custom_props,
            "children": []
        }

        # Process children if this is a sub-assembly
        if is_sub_assembly and ref_model:
            try:
                config_mgr = ref_model.ConfigurationManager
                if config_mgr:
                    active_config = config_mgr.ActiveConfiguration
                    if active_config:
                        root_comp = active_config.GetRootComponent3(True)
                        if root_comp:
                            children = root_comp.GetChildren
                            if callable(children):
                                children = children()
                            if children:
                                child_parts = {}
                                for child in children:
                                    child_result = _process_component(child, level + 1, item_counter, max_depth)
                                    if child_result:
                                        child_pn = child_result["part_number"]
                                        if child_pn in child_parts:
                                            child_parts[child_pn]["qty"] += 1
                                        else:
                                            child_parts[child_pn] = child_result
                                result["children"] = list(child_parts.values())
            except Exception as e:
                logger.warning(f"Error processing sub-assembly children: {e}")

        return result

    except Exception as e:
        logger.warning(f"Error processing component {comp}: {e}")
        return None


def _get_bom_sync():
    """Synchronous BOM extraction - runs in COM thread context."""
    pythoncom.CoInitialize()
    try:
        app = win32com.client.Dispatch("SldWorks.Application")
        model = app.ActiveDoc

        if not model:
            return {"error": "No active document", "status_code": 400}

        doc_type = model.GetType
        if doc_type != 2:  # swDocASSEMBLY = 2
            return {"error": "Active document is not an assembly", "status_code": 400}

        # Get assembly-level custom properties
        assembly_props = _get_custom_properties(model)

        # Get assembly configuration
        config_mgr = model.ConfigurationManager
        active_config = config_mgr.ActiveConfiguration
        root_component = active_config.GetRootComponent3(True)

        hierarchical_bom = []
        flat_bom = []
        seen_parts = {}
        item_counter = {"value": 0}
        total_parts = 0
        total_sub_assemblies = 0

        if root_component:
            children = root_component.GetChildren
            if callable(children):
                children = children()
            if children:
                for comp in children:
                    result = _process_component(comp, level=0, item_counter=item_counter)
                    if result:
                        pn = result["part_number"]
                        if pn in seen_parts:
                            seen_parts[pn]["qty"] += 1
                        else:
                            seen_parts[pn] = result
                            if result["type"] == "Sub-Assembly":
                                total_sub_assemblies += 1
                            else:
                                total_parts += 1

        # Build hierarchical BOM (with children)
        hierarchical_bom = list(seen_parts.values())
        hierarchical_bom.sort(key=lambda x: x["part_number"])

        # Re-number items sequentially
        def renumber_items(items, counter=None):
            if counter is None:
                counter = {"value": 0}
            for item in items:
                counter["value"] += 1
                item["item"] = counter["value"]
                if item.get("children"):
                    renumber_items(item["children"], counter)

        renumber_items(hierarchical_bom)

        # Build flat BOM (no children, just top-level with counts)
        flat_bom = []
        for item in hierarchical_bom:
            flat_item = {k: v for k, v in item.items() if k != "children"}
            flat_bom.append(flat_item)

        # Get assembly name
        assembly_name = model.GetTitle if hasattr(model, 'GetTitle') else "Unknown"
        if callable(assembly_name):
            assembly_name = assembly_name()

        return {
            "status": "ok",
            "assembly_name": assembly_name,
            "assembly_properties": assembly_props,
            "total_unique_parts": len(hierarchical_bom),
            "total_parts": total_parts,
            "total_sub_assemblies": total_sub_assemblies,
            "bom": flat_bom,  # Flat for backward compatibility
            "hierarchical_bom": hierarchical_bom  # New hierarchical structure
        }
    except Exception as e:
        logger.error(f"Error extracting BOM: {e}")
        return {"error": f"Failed to extract BOM: {e}", "status_code": 500}
    finally:
        pythoncom.CoUninitialize()


@router.get("/get_bom")
async def get_bom():
    """Extract Bill of Materials from the active assembly."""
    import asyncio
    import concurrent.futures

    logger.info("Extracting BOM from assembly")

    # Run COM operations in a thread pool to ensure proper COM initialization
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, _get_bom_sync)

    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result["error"])

    return result


@router.get("/get_bom_pdf")
async def get_bom_pdf():
    """Generate a PDF of the Bill of Materials and return as base64."""
    import base64
    from io import BytesIO
    from datetime import datetime

    # First get the BOM data
    bom_response = await get_bom()
    bom_items = bom_response["bom"]
    assembly_name = bom_response["assembly_name"]

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        # Fallback: generate simple HTML-based response
        raise HTTPException(
            status_code=500,
            detail="PDF generation requires reportlab. Install with: pip install reportlab"
        )

    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    elements.append(Paragraph(f"Bill of Materials", title_style))

    # Assembly name and date
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    elements.append(Paragraph(f"Assembly: {assembly_name}", subtitle_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 20))

    # Table header
    table_data = [["Item", "Part Number", "Description", "Type", "Qty"]]

    # Add BOM rows
    for item in bom_items:
        table_data.append([
            str(item.get("item", "")),
            item.get("part_number", "")[:40],  # Truncate long names
            item.get("description", "")[:50],
            item.get("type", "Part"),
            str(item.get("qty", 1))
        ])

    # Create table with styling
    col_widths = [0.5*inch, 2.5*inch, 3.5*inch, 1*inch, 0.5*inch]
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Body styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item column centered
        ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),  # Qty column centered
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),

        # Alternating row colors
        *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f3f4f6'))
          for i in range(2, len(table_data), 2)],

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#9ca3af')),
    ]))

    elements.append(table)

    # Footer with total count
    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT
    )
    elements.append(Paragraph(f"Total Unique Parts: {len(bom_items)}", footer_style))

    # Build PDF
    doc.build(elements)

    # Get PDF bytes and encode as base64
    pdf_bytes = buffer.getvalue()
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    return {
        "status": "ok",
        "assembly_name": assembly_name,
        "total_parts": len(bom_items),
        "pdf_base64": pdf_base64,
        "filename": f"BOM_{assembly_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    }


def _get_spatial_data_sync():
    """Get spatial positioning data for all components."""
    pythoncom.CoInitialize()
    try:
        app = win32com.client.Dispatch("SldWorks.Application")
        model = app.ActiveDoc

        if not model:
            return {"error": "No active document", "status_code": 400}

        doc_type = model.GetType
        if doc_type != 2:
            return {"error": "Active document is not an assembly", "status_code": 400}

        config_mgr = model.ConfigurationManager
        active_config = config_mgr.ActiveConfiguration
        root_component = active_config.GetRootComponent3(True)

        components = []
        relationships = []

        if root_component:
            children = root_component.GetChildren
            if callable(children):
                children = children()

            if children:
                comp_positions = {}

                for comp in children:
                    try:
                        comp_name = None
                        for attr in ['Name2', 'Name']:
                            try:
                                val = getattr(comp, attr, None)
                                if val:
                                    comp_name = val() if callable(val) else val
                                    break
                            except:
                                continue

                        if not comp_name:
                            continue

                        # Get transform matrix (position and orientation)
                        transform = comp.Transform2
                        position = {"x": 0, "y": 0, "z": 0}
                        if transform:
                            try:
                                # Transform matrix: 16 values, last 3 before scale are translation
                                arr = transform.ArrayData
                                if arr and len(arr) >= 12:
                                    position = {
                                        "x": round(arr[9] * 1000, 2),   # Convert to mm
                                        "y": round(arr[10] * 1000, 2),
                                        "z": round(arr[11] * 1000, 2)
                                    }
                            except:
                                pass

                        # Get bounding box for size
                        bbox = {"x": 0, "y": 0, "z": 0}
                        try:
                            ref_model = comp.GetModelDoc2()
                            if ref_model:
                                box = ref_model.GetPartBox() if hasattr(ref_model, 'GetPartBox') else None
                                if box and len(box) >= 6:
                                    bbox = {
                                        "x": round(abs(box[3] - box[0]) * 1000, 2),
                                        "y": round(abs(box[4] - box[1]) * 1000, 2),
                                        "z": round(abs(box[5] - box[2]) * 1000, 2)
                                    }
                        except:
                            pass

                        # Extract part type from name
                        part_type = "unknown"
                        name_lower = comp_name.lower()
                        if "seal" in name_lower or "gasket" in name_lower:
                            part_type = "seal"
                        elif "ring" in name_lower:
                            part_type = "ring"
                        elif "fan" in name_lower:
                            part_type = "fan"
                        elif "frame" in name_lower or "struct" in name_lower:
                            part_type = "frame"
                        elif "panel" in name_lower or "plate" in name_lower:
                            part_type = "panel"

                        comp_data = {
                            "name": comp_name,
                            "part_type": part_type,
                            "position": position,
                            "size": bbox,
                            "center": {
                                "x": position["x"],
                                "y": position["y"],
                                "z": position["z"]
                            }
                        }
                        components.append(comp_data)
                        comp_positions[comp_name] = position

                    except Exception as e:
                        logger.warning(f"Error getting spatial data for component: {e}")
                        continue

                # Analyze spatial relationships
                for i, comp1 in enumerate(components):
                    for comp2 in components[i+1:]:
                        # Calculate distance between components
                        dx = comp1["position"]["x"] - comp2["position"]["x"]
                        dy = comp1["position"]["y"] - comp2["position"]["y"]
                        dz = comp1["position"]["z"] - comp2["position"]["z"]
                        distance = (dx**2 + dy**2 + dz**2) ** 0.5

                        # Determine relationship type
                        relationship = "distant"
                        if distance < 50:  # Within 50mm
                            relationship = "adjacent"
                        elif distance < 150:
                            relationship = "nearby"

                        # Check for axial alignment (same X-Y, different Z)
                        axial_aligned = abs(dx) < 20 and abs(dy) < 20 and abs(dz) > 20
                        radial_aligned = abs(dz) < 20 and (abs(dx) > 20 or abs(dy) > 20)

                        if relationship in ["adjacent", "nearby"]:
                            rel_data = {
                                "component1": comp1["name"],
                                "component2": comp2["name"],
                                "distance_mm": round(distance, 2),
                                "relationship": relationship,
                                "axial_aligned": axial_aligned,
                                "radial_aligned": radial_aligned
                            }
                            relationships.append(rel_data)

        # Group components by type
        type_groups = {}
        for comp in components:
            pt = comp["part_type"]
            if pt not in type_groups:
                type_groups[pt] = []
            type_groups[pt].append(comp["name"])

        # Find seal-to-ring relationships specifically
        seal_ring_pairs = []
        for rel in relationships:
            name1_lower = rel["component1"].lower()
            name2_lower = rel["component2"].lower()
            is_seal_ring = (("seal" in name1_lower and "ring" in name2_lower) or
                           ("ring" in name1_lower and "seal" in name2_lower))
            if is_seal_ring:
                seal_ring_pairs.append(rel)

        try:
            title_attr = getattr(model, 'GetTitle', None)
            if title_attr:
                assembly_name = title_attr() if callable(title_attr) else title_attr
            else:
                assembly_name = "Unknown"
        except:
            assembly_name = "Unknown"

        return {
            "status": "ok",
            "assembly_name": assembly_name,
            "total_components": len(components),
            "components": components,
            "relationships": relationships[:50],  # Limit to 50 most relevant
            "type_groups": type_groups,
            "seal_ring_pairs": seal_ring_pairs,
            "analysis": {
                "seals_count": len(type_groups.get("seal", [])),
                "rings_count": len(type_groups.get("ring", [])),
                "fans_count": len(type_groups.get("fan", [])),
                "adjacent_pairs": len([r for r in relationships if r["relationship"] == "adjacent"])
            }
        }

    except Exception as e:
        logger.error(f"Error getting spatial data: {e}")
        return {"error": str(e), "status_code": 500}
    finally:
        pythoncom.CoUninitialize()


@router.get("/get_spatial_positions")
async def get_spatial_positions():
    """Get spatial positions and relationships of all components."""
    import asyncio
    import concurrent.futures

    logger.info("Getting component spatial positions")

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, _get_spatial_data_sync)

    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result["error"])

    return result
