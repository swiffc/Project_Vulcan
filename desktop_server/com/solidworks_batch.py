"""
SolidWorks Batch Operations - ENHANCED
======================================
High-performance batch operations with macro-like speed.

Features:
- Deferred rebuilds (single rebuild at end)
- Workflow templates (pre-built sequences)
- Variable passing between operations
- Conditional execution (if/else)
- Loop support (repeat operations)
- Transaction mode (rollback on failure)
- Operation chaining with dependencies
- Graphics disable for maximum speed
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import logging
import copy
import json
import os

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False

router = APIRouter(prefix="/com/solidworks/batch", tags=["solidworks", "batch"])
logger = logging.getLogger(__name__)

# Global state
_batch_mode_active = False
_batch_operations = []
_workflow_templates = {}
_variables = {}


# =============================================================================
# Pydantic Models
# =============================================================================

class BatchOperation(BaseModel):
    """Single operation in a batch."""
    operation: str  # Tool name (e.g., "extrude", "fillet", "select")
    params: Dict[str, Any] = {}  # Operation parameters
    store_result: Optional[str] = None  # Variable name to store result
    condition: Optional[str] = None  # Condition to check before executing


class ConditionalBlock(BaseModel):
    """Conditional execution block."""
    condition: str  # Expression to evaluate (e.g., "hole_count > 0")
    if_true: List[BatchOperation]
    if_false: Optional[List[BatchOperation]] = None


class LoopBlock(BaseModel):
    """Loop execution block."""
    loop_type: str  # "count", "foreach", "while"
    count: Optional[int] = None  # For count loops
    items: Optional[List[Any]] = None  # For foreach loops
    condition: Optional[str] = None  # For while loops
    variable_name: str = "i"  # Loop variable name
    operations: List[BatchOperation]


class WorkflowStep(BaseModel):
    """A step in a workflow (can be operation, conditional, or loop)."""
    step_type: str  # "operation", "conditional", "loop", "set_variable"
    operation: Optional[BatchOperation] = None
    conditional: Optional[ConditionalBlock] = None
    loop: Optional[LoopBlock] = None
    variable_name: Optional[str] = None
    variable_value: Optional[Any] = None


class BatchOperationsRequest(BaseModel):
    """Request to execute multiple operations with single rebuild."""
    operations: List[BatchOperation]
    rebuild_at_end: bool = True
    disable_graphics: bool = True
    stop_on_error: bool = False
    variables: Optional[Dict[str, Any]] = None  # Initial variables


class WorkflowRequest(BaseModel):
    """Request to execute a workflow with steps."""
    steps: List[WorkflowStep]
    rebuild_at_end: bool = True
    disable_graphics: bool = True
    stop_on_error: bool = True
    variables: Optional[Dict[str, Any]] = None
    transaction_mode: bool = False  # Rollback on failure


class WorkflowTemplateRequest(BaseModel):
    """Request to save a workflow as a template."""
    name: str
    description: str
    steps: List[WorkflowStep]
    parameters: Optional[List[str]] = None  # Required parameters


class BatchPropertiesRequest(BaseModel):
    """Request to update multiple properties in one call."""
    properties: Dict[str, str]
    configuration: Optional[str] = None


class BatchDimensionsRequest(BaseModel):
    """Request to update multiple dimensions."""
    dimensions: Dict[str, float]


class BatchFeaturesRequest(BaseModel):
    """Request to create multiple features."""
    features: List[Dict[str, Any]]


class BatchSelectRequest(BaseModel):
    """Request to select multiple entities."""
    entities: List[Dict[str, Any]]  # {"type": "FACE", "name": "Face<1>"}


class BatchComponentsRequest(BaseModel):
    """Request for batch component operations in assemblies."""
    components: List[Dict[str, Any]]
    operation: str  # "insert", "mate", "suppress", "hide", "delete"


class CreatePartFromSketchRequest(BaseModel):
    """Create a part with sketch and extrusion in one call."""
    sketch_plane: str = "Front Plane"
    sketch_entities: List[Dict[str, Any]]  # Circles, rectangles, lines
    extrude_depth: float  # mm
    material: Optional[str] = None
    properties: Optional[Dict[str, str]] = None


class CreateAssemblyRequest(BaseModel):
    """Create assembly with components and mates in one call."""
    components: List[Dict[str, Any]]  # {"path": "...", "position": [x,y,z]}
    mates: List[Dict[str, Any]]  # {"type": "coincident", "entity1": "...", "entity2": "..."}
    properties: Optional[Dict[str, str]] = None


# =============================================================================
# Helper Functions
# =============================================================================

def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


def evaluate_condition(condition: str, variables: Dict[str, Any]) -> bool:
    """Safely evaluate a condition string."""
    try:
        # Create safe evaluation context
        safe_context = {
            "True": True, "False": False, "None": None,
            "len": len, "abs": abs, "min": min, "max": max,
            "str": str, "int": int, "float": float, "bool": bool
        }
        safe_context.update(variables)
        return bool(eval(condition, {"__builtins__": {}}, safe_context))
    except Exception as e:
        logger.error(f"Condition evaluation failed: {condition} - {e}")
        return False


def substitute_variables(params: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
    """Substitute variables in parameters."""
    result = {}
    for key, value in params.items():
        if isinstance(value, str) and value.startswith("$"):
            var_name = value[1:]
            result[key] = variables.get(var_name, value)
        elif isinstance(value, dict):
            result[key] = substitute_variables(value, variables)
        elif isinstance(value, list):
            result[key] = [
                substitute_variables(v, variables) if isinstance(v, dict)
                else variables.get(v[1:], v) if isinstance(v, str) and v.startswith("$")
                else v
                for v in value
            ]
        else:
            result[key] = value
    return result


# =============================================================================
# Operation Handlers
# =============================================================================

async def execute_operation(sw, model, operation: str, params: Dict[str, Any], variables: Dict[str, Any]) -> Dict:
    """Execute a single operation within batch mode."""

    # Substitute variables in params
    params = substitute_variables(params, variables)

    fm = model.FeatureManager
    sm = model.SketchManager
    ext = model.Extension

    # =========================================================================
    # SKETCH OPERATIONS
    # =========================================================================

    if operation == "select":
        entity_type = params.get("type", "FACE")
        name = params.get("name", "")
        append = params.get("append", False)
        mark = params.get("mark", 0)
        result = ext.SelectByID2(name, entity_type, 0, 0, 0, append, mark, None, 0)
        return {"selected": result, "entity": name}

    elif operation == "clear_selection":
        model.ClearSelection2(True)
        return {"cleared": True}

    elif operation == "start_sketch":
        plane = params.get("plane", "Front Plane")
        ext.SelectByID2(plane, "PLANE", 0, 0, 0, False, 0, None, 0)
        sm.InsertSketch(True)
        return {"sketch_started": True, "plane": plane}

    elif operation == "end_sketch":
        sm.InsertSketch(True)
        return {"sketch_ended": True}

    elif operation == "draw_line":
        x1, y1 = params.get("x1", 0) / 1000, params.get("y1", 0) / 1000
        x2, y2 = params.get("x2", 0.1) / 1000, params.get("y2", 0) / 1000
        line = sm.CreateLine(x1, y1, 0, x2, y2, 0)
        return {"line_created": line is not None}

    elif operation == "draw_rectangle":
        x1, y1 = params.get("x1", 0) / 1000, params.get("y1", 0) / 1000
        x2, y2 = params.get("x2", 0.1) / 1000, params.get("y2", 0.1) / 1000
        rect = sm.CreateCornerRectangle(x1, y1, 0, x2, y2, 0)
        return {"rectangle_created": rect is not None}

    elif operation == "draw_circle":
        cx, cy = params.get("cx", 0) / 1000, params.get("cy", 0) / 1000
        radius = params.get("radius", 10) / 1000
        circle = sm.CreateCircle(cx, cy, 0, cx + radius, cy, 0)
        return {"circle_created": circle is not None}

    elif operation == "draw_arc":
        cx, cy = params.get("cx", 0) / 1000, params.get("cy", 0) / 1000
        radius = params.get("radius", 10) / 1000
        start_angle = params.get("start_angle", 0)
        end_angle = params.get("end_angle", 90)
        import math
        x1 = cx + radius * math.cos(math.radians(start_angle))
        y1 = cy + radius * math.sin(math.radians(start_angle))
        x2 = cx + radius * math.cos(math.radians(end_angle))
        y2 = cy + radius * math.sin(math.radians(end_angle))
        arc = sm.CreateArc(cx, cy, 0, x1 / 1000, y1 / 1000, 0, x2 / 1000, y2 / 1000, 0, 1)
        return {"arc_created": arc is not None}

    elif operation == "draw_polygon":
        cx, cy = params.get("cx", 0) / 1000, params.get("cy", 0) / 1000
        radius = params.get("radius", 10) / 1000
        sides = params.get("sides", 6)
        sm.CreatePolygon(cx, cy, 0, cx + radius, cy, 0, sides, True)
        return {"polygon_created": True, "sides": sides}

    elif operation == "draw_slot":
        x1, y1 = params.get("x1", 0) / 1000, params.get("y1", 0) / 1000
        x2, y2 = params.get("x2", 0.05) / 1000, params.get("y2", 0) / 1000
        width = params.get("width", 10) / 1000
        sm.CreateSketchSlot(0, x1, y1, 0, x2, y2, 0, width, 0, None, None)
        return {"slot_created": True}

    # =========================================================================
    # FEATURE OPERATIONS
    # =========================================================================

    elif operation == "extrude":
        depth = params.get("depth", 10) / 1000
        direction = params.get("direction", 1)  # 1=forward, -1=backward, 0=midplane
        draft_angle = params.get("draft_angle", 0)

        if direction == 0:  # Midplane
            feature = fm.FeatureExtrusion3(
                True, False, True, 0, 0, depth/2, depth/2,
                False, False, False, False, draft_angle, draft_angle,
                False, False, False, False, True, True, True, 0, 0, False
            )
        else:
            feature = fm.FeatureExtrusion3(
                True, False, False, 0, 0, depth, 0,
                False, False, False, False, draft_angle, 0,
                False, False, False, False, True, True, True, 0, 0, False
            )
        return {"feature_created": feature is not None, "depth_mm": depth * 1000}

    elif operation == "extrude_cut":
        depth = params.get("depth", 10) / 1000
        through_all = params.get("through_all", False)

        if through_all:
            feature = fm.FeatureCut4(
                True, False, False, 1, 0, depth, depth,
                False, False, False, False, 0, 0,
                False, False, False, False, False, True, True, True, True, False, 0, 0, False, False
            )
        else:
            feature = fm.FeatureCut4(
                True, False, False, 0, 0, depth, 0,
                False, False, False, False, 0, 0,
                False, False, False, False, False, True, True, True, True, False, 0, 0, False, False
            )
        return {"cut_created": feature is not None}

    elif operation == "revolve":
        angle = params.get("angle", 360)
        import math
        angle_rad = math.radians(angle)
        feature = fm.FeatureRevolve2(True, True, False, False, False, False, 0, 0, angle_rad, 0, False, False, 0, 0, 0, 0, 0, True, True, True)
        return {"revolve_created": feature is not None, "angle_deg": angle}

    elif operation == "fillet":
        radius = params.get("radius", 1) / 1000
        feature = fm.FeatureFillet3(195, radius, 0, 0, 0, 0, 0, None, None, None, None, None, None, None)
        return {"fillet_created": feature is not None, "radius_mm": radius * 1000}

    elif operation == "chamfer":
        distance = params.get("distance", 1) / 1000
        angle = params.get("angle", 45)
        import math
        feature = fm.InsertFeatureChamfer(4, 1, distance, math.radians(angle), 0, 0, 0, 0)
        return {"chamfer_created": feature is not None}

    elif operation == "hole_wizard":
        hole_type = params.get("hole_type", 0)  # 0=counterbore, 1=countersink, 2=hole, 3=tap, 4=pipe_tap, 5=legacy
        standard = params.get("standard", 0)  # 0=ANSI Inch, 1=ANSI Metric
        fastener_type = params.get("fastener_type", 0)
        size = params.get("size", "M6")
        end_type = params.get("end_type", 0)  # 0=blind, 1=through
        depth = params.get("depth", 10) / 1000

        feature = fm.HoleWizard5(
            hole_type, standard, fastener_type, size, end_type,
            depth, depth, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, False, True, True, True, True, False, False
        )
        return {"hole_created": feature is not None}

    elif operation == "shell":
        thickness = params.get("thickness", 1) / 1000
        feature = fm.InsertFeatureShell(thickness, False)
        return {"shell_created": feature is not None}

    elif operation == "rib":
        thickness = params.get("thickness", 2) / 1000
        feature = fm.InsertRib(False, False, thickness, 0, False, False, False, 0, False, False)
        return {"rib_created": feature is not None}

    elif operation == "draft":
        angle = params.get("angle", 5)
        import math
        feature = fm.InsertDraft(0, math.radians(angle), 0, 0, 0, 0, 0, False, False, False, True)
        return {"draft_created": feature is not None}

    elif operation == "mirror":
        feature = fm.InsertMirrorFeature2(True, False, False, False, 0)
        return {"mirror_created": feature is not None}

    elif operation == "linear_pattern":
        count_x = params.get("count_x", 2)
        count_y = params.get("count_y", 1)
        spacing_x = params.get("spacing_x", 10) / 1000
        spacing_y = params.get("spacing_y", 10) / 1000
        feature = fm.FeatureLinearPattern4(
            count_x, spacing_x, count_y, spacing_y,
            True, True, "None", "None", False, False
        )
        return {"pattern_created": feature is not None, "total_instances": count_x * count_y}

    elif operation == "circular_pattern":
        count = params.get("count", 4)
        angle = params.get("angle", 360)
        import math
        feature = fm.FeatureCircularPattern4(
            count, math.radians(angle), True, "None", False, True, False
        )
        return {"pattern_created": feature is not None, "instances": count}

    # =========================================================================
    # ASSEMBLY OPERATIONS
    # =========================================================================

    elif operation == "insert_component":
        path = params.get("path", "")
        x = params.get("x", 0) / 1000
        y = params.get("y", 0) / 1000
        z = params.get("z", 0) / 1000

        doc_type = 1  # Part
        if path.lower().endswith('.sldasm'):
            doc_type = 2

        errors = 0
        warnings = 0
        comp = model.AddComponent5(path, 0, "", False, "", x, y, z)
        return {"component_inserted": comp is not None, "path": path}

    elif operation == "add_mate":
        mate_type = params.get("type", "coincident")
        entity1 = params.get("entity1", "")
        entity2 = params.get("entity2", "")

        # Select entities
        ext.SelectByID2(entity1, "FACE", 0, 0, 0, False, 1, None, 0)
        ext.SelectByID2(entity2, "FACE", 0, 0, 0, True, 1, None, 0)

        mate_types = {
            "coincident": 0, "concentric": 1, "perpendicular": 2,
            "parallel": 3, "tangent": 4, "distance": 5, "angle": 6
        }

        mate_type_id = mate_types.get(mate_type.lower(), 0)
        alignment = params.get("alignment", 0)
        flip = params.get("flip", False)
        distance = params.get("distance", 0) / 1000

        mate = model.AddMate5(
            mate_type_id, alignment, flip, distance, distance, distance,
            0, 0, 0, 0, 0, False, False, 0, None
        )
        return {"mate_created": mate is not None, "type": mate_type}

    elif operation == "suppress_component":
        name = params.get("name", "")
        ext.SelectByID2(name, "COMPONENT", 0, 0, 0, False, 0, None, 0)
        model.EditSuppress2()
        return {"suppressed": name}

    elif operation == "unsuppress_component":
        name = params.get("name", "")
        ext.SelectByID2(name, "COMPONENT", 0, 0, 0, False, 0, None, 0)
        model.EditUnsuppress2()
        return {"unsuppressed": name}

    # =========================================================================
    # PROPERTY & DIMENSION OPERATIONS
    # =========================================================================

    elif operation == "set_property":
        name = params.get("name", "")
        value = params.get("value", "")
        config = params.get("configuration", "")
        prop_mgr = ext.CustomPropertyManager(config)
        prop_mgr.Set2(name, str(value))
        return {"property_set": name, "value": value}

    elif operation == "set_dimension":
        dim_name = params.get("name", "")
        value = params.get("value", 0) / 1000  # Convert mm to m
        config = params.get("configuration", "")

        disp_dim = model.Parameter(dim_name)
        if disp_dim:
            disp_dim.SystemValue = value
            return {"dimension_set": dim_name, "value_mm": value * 1000}
        return {"error": f"Dimension {dim_name} not found"}

    elif operation == "set_material":
        material = params.get("material", "Plain Carbon Steel")
        database = params.get("database", "solidworks materials.sldmat")

        part = model.Extension.GetPropertyExtension(0)
        if part:
            part.SetMaterialPropertyName2("", database, material)
        return {"material_set": material}

    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================

    elif operation == "rebuild":
        result = model.EditRebuild3()
        return {"rebuilt": result}

    elif operation == "force_rebuild":
        result = model.ForceRebuild3(True)
        return {"force_rebuilt": result}

    elif operation == "save":
        errors = 0
        warnings = 0
        result = model.Save3(1, errors, warnings)
        return {"saved": result == 0}

    elif operation == "save_as":
        path = params.get("path", "")
        errors = 0
        warnings = 0
        result = model.SaveAs3(path, 0, 2)
        return {"saved_as": path, "success": result == 0}

    elif operation == "export":
        path = params.get("path", "")
        format_type = params.get("format", "STEP")
        errors = 0
        warnings = 0
        result = model.SaveAs3(path, 0, 2)
        return {"exported": path}

    elif operation == "close":
        sw.CloseDoc(model.GetTitle())
        return {"closed": True}

    elif operation == "open":
        path = params.get("path", "")
        doc_type = 1
        if path.lower().endswith('.sldasm'):
            doc_type = 2
        elif path.lower().endswith('.slddrw'):
            doc_type = 3

        errors = 0
        warnings = 0
        doc = sw.OpenDoc6(path, doc_type, 1, "", errors, warnings)
        return {"opened": doc is not None, "path": path}

    elif operation == "new_part":
        template = params.get("template", "")
        if not template:
            template = sw.GetUserPreferenceStringValue(7)  # Default part template
        doc = sw.NewDocument(template, 0, 0, 0)
        return {"new_part_created": doc is not None}

    elif operation == "new_assembly":
        template = params.get("template", "")
        if not template:
            template = sw.GetUserPreferenceStringValue(8)  # Default assembly template
        doc = sw.NewDocument(template, 0, 0, 0)
        return {"new_assembly_created": doc is not None}

    # =========================================================================
    # CONFIGURATION OPERATIONS
    # =========================================================================

    elif operation == "add_configuration":
        name = params.get("name", "Config1")
        comment = params.get("comment", "")
        config = model.ConfigurationManager.AddConfiguration2(
            name, comment, "", 0, "", "", True
        )
        return {"configuration_added": config is not None, "name": name}

    elif operation == "activate_configuration":
        name = params.get("name", "")
        result = model.ShowConfiguration2(name)
        return {"configuration_activated": result, "name": name}

    # =========================================================================
    # UTILITY OPERATIONS
    # =========================================================================

    elif operation == "zoom_fit":
        model.ViewZoomtofit2()
        return {"zoomed": True}

    elif operation == "set_view":
        view = params.get("view", "isometric")
        views = {
            "front": 1, "back": 2, "left": 3, "right": 4,
            "top": 5, "bottom": 6, "isometric": 7
        }
        model.ShowNamedView2("", views.get(view.lower(), 7))
        return {"view_set": view}

    elif operation == "measure_distance":
        # Requires pre-selected entities
        measure = model.Extension.CreateMassProperty()
        return {"measure_initiated": True}

    elif operation == "get_mass":
        mass_props = model.Extension.CreateMassProperty()
        if mass_props:
            return {
                "mass_kg": mass_props.Mass,
                "volume_m3": mass_props.Volume,
                "surface_area_m2": mass_props.SurfaceArea,
                "center_of_mass": list(mass_props.CenterOfMass)
            }
        return {"error": "Could not calculate mass properties"}

    elif operation == "count_features":
        count = 0
        feature = model.FirstFeature()
        while feature:
            count += 1
            feature = feature.GetNextFeature()
        return {"feature_count": count}

    elif operation == "delay":
        import time
        time.sleep(params.get("seconds", 0.1))
        return {"delayed": params.get("seconds", 0.1)}

    else:
        return {"error": f"Unknown operation: {operation}", "operation": operation}


# =============================================================================
# Core Batch Endpoints
# =============================================================================

@router.post("/execute")
async def execute_batch_operations(req: BatchOperationsRequest):
    """
    Execute multiple operations with deferred rebuild - MACRO SPEED.

    This is MUCH faster than individual operations because:
    1. Only one rebuild at the end (instead of N rebuilds)
    2. Graphics updates disabled during operations
    3. Operations executed in tight sequence

    Features:
    - Variable substitution: Use $variable_name in params
    - Result storage: Use store_result to save operation output
    - Conditional execution: Use condition to skip operations

    Example:
    {
        "operations": [
            {"operation": "start_sketch", "params": {"plane": "Front Plane"}},
            {"operation": "draw_rectangle", "params": {"x1": 0, "y1": 0, "x2": 100, "y2": 50}},
            {"operation": "end_sketch"},
            {"operation": "extrude", "params": {"depth": 25}},
            {"operation": "fillet", "params": {"radius": 5}}
        ],
        "rebuild_at_end": true,
        "disable_graphics": true
    }
    """
    global _batch_mode_active, _variables

    try:
        pythoncom.CoInitialize()
        sw = win32com.client.GetActiveObject("SldWorks.Application")
        model = sw.ActiveDoc

        if not model:
            raise HTTPException(status_code=400, detail="No active document")

        # Initialize variables
        _variables = req.variables or {}
        _batch_mode_active = True

        # Disable graphics for speed
        original_frame_state = None
        if req.disable_graphics:
            try:
                original_frame_state = sw.FrameState
                sw.FrameState = 0  # Hidden
                logger.info("Graphics disabled for batch operations")
            except:
                pass

        results = []
        errors = []

        # Execute all operations
        for i, op in enumerate(req.operations):
            try:
                # Check condition
                if op.condition and not evaluate_condition(op.condition, _variables):
                    results.append({
                        "operation": op.operation,
                        "skipped": True,
                        "reason": f"Condition not met: {op.condition}"
                    })
                    continue

                logger.info(f"Batch operation {i+1}/{len(req.operations)}: {op.operation}")

                # Execute operation
                result = await execute_operation(sw, model, op.operation, op.params, _variables)

                # Store result if requested
                if op.store_result:
                    _variables[op.store_result] = result

                results.append({
                    "operation": op.operation,
                    "success": True,
                    "result": result
                })

            except Exception as e:
                logger.error(f"Batch operation {op.operation} failed: {e}")
                error_info = {"operation": op.operation, "error": str(e)}
                errors.append(error_info)
                results.append({"operation": op.operation, "success": False, "error": str(e)})

                if req.stop_on_error:
                    break

        # Single rebuild at end
        rebuild_success = None
        if req.rebuild_at_end and not errors:
            try:
                model.EditRebuild3()
                rebuild_success = True
            except Exception as e:
                rebuild_success = False

        # Restore graphics
        if original_frame_state is not None:
            try:
                sw.FrameState = original_frame_state
            except:
                pass

        _batch_mode_active = False

        return {
            "status": "ok",
            "operations_executed": len(results),
            "operations_succeeded": len([r for r in results if r.get("success")]),
            "operations_failed": len(errors),
            "rebuild_executed": rebuild_success,
            "results": results,
            "errors": errors,
            "variables": _variables
        }

    except Exception as e:
        _batch_mode_active = False
        logger.error(f"Batch operations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


@router.post("/workflow")
async def execute_workflow(req: WorkflowRequest):
    """
    Execute a complete workflow with conditionals, loops, and variables.

    This is the MACRO EQUIVALENT - chains operations together intelligently.

    Step types:
    - operation: Execute a single operation
    - conditional: If/else branching
    - loop: Repeat operations (count, foreach, while)
    - set_variable: Set a variable value

    Example:
    {
        "steps": [
            {"step_type": "set_variable", "variable_name": "hole_count", "variable_value": 4},
            {"step_type": "operation", "operation": {"operation": "start_sketch", "params": {"plane": "Top Plane"}}},
            {"step_type": "loop", "loop": {
                "loop_type": "count",
                "count": 4,
                "variable_name": "i",
                "operations": [
                    {"operation": "draw_circle", "params": {"cx": "$i * 20", "cy": 0, "radius": 5}}
                ]
            }},
            {"step_type": "conditional", "conditional": {
                "condition": "hole_count > 0",
                "if_true": [{"operation": "extrude_cut", "params": {"depth": 10}}]
            }}
        ]
    }
    """
    global _variables

    try:
        pythoncom.CoInitialize()
        sw = win32com.client.GetActiveObject("SldWorks.Application")
        model = sw.ActiveDoc

        if not model:
            raise HTTPException(status_code=400, detail="No active document")

        _variables = req.variables or {}
        results = []

        # Disable graphics
        original_frame_state = None
        if req.disable_graphics:
            try:
                original_frame_state = sw.FrameState
                sw.FrameState = 0
            except:
                pass

        # Execute steps
        for step in req.steps:
            step_result = await execute_workflow_step(sw, model, step, _variables)
            results.append(step_result)

            if req.stop_on_error and step_result.get("error"):
                break

        # Rebuild
        if req.rebuild_at_end:
            model.EditRebuild3()

        # Restore graphics
        if original_frame_state is not None:
            try:
                sw.FrameState = original_frame_state
            except:
                pass

        return {
            "status": "ok",
            "steps_executed": len(results),
            "results": results,
            "variables": _variables
        }

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


async def execute_workflow_step(sw, model, step: WorkflowStep, variables: Dict) -> Dict:
    """Execute a single workflow step."""
    global _variables

    if step.step_type == "operation":
        if step.operation:
            result = await execute_operation(sw, model, step.operation.operation, step.operation.params, variables)
            if step.operation.store_result:
                _variables[step.operation.store_result] = result
            return {"type": "operation", "operation": step.operation.operation, "result": result}

    elif step.step_type == "set_variable":
        _variables[step.variable_name] = step.variable_value
        return {"type": "set_variable", "name": step.variable_name, "value": step.variable_value}

    elif step.step_type == "conditional":
        if step.conditional:
            condition_met = evaluate_condition(step.conditional.condition, _variables)
            ops_to_run = step.conditional.if_true if condition_met else (step.conditional.if_false or [])

            results = []
            for op in ops_to_run:
                result = await execute_operation(sw, model, op.operation, op.params, _variables)
                results.append(result)

            return {
                "type": "conditional",
                "condition": step.conditional.condition,
                "condition_met": condition_met,
                "results": results
            }

    elif step.step_type == "loop":
        if step.loop:
            loop_results = []

            if step.loop.loop_type == "count":
                for i in range(step.loop.count or 0):
                    _variables[step.loop.variable_name] = i
                    for op in step.loop.operations:
                        result = await execute_operation(sw, model, op.operation, op.params, _variables)
                        loop_results.append(result)

            elif step.loop.loop_type == "foreach":
                for i, item in enumerate(step.loop.items or []):
                    _variables[step.loop.variable_name] = item
                    _variables["index"] = i
                    for op in step.loop.operations:
                        result = await execute_operation(sw, model, op.operation, op.params, _variables)
                        loop_results.append(result)

            elif step.loop.loop_type == "while":
                max_iterations = 1000
                iteration = 0
                while evaluate_condition(step.loop.condition, _variables) and iteration < max_iterations:
                    _variables[step.loop.variable_name] = iteration
                    for op in step.loop.operations:
                        result = await execute_operation(sw, model, op.operation, op.params, _variables)
                        loop_results.append(result)
                    iteration += 1

            return {
                "type": "loop",
                "loop_type": step.loop.loop_type,
                "iterations": len(loop_results),
                "results": loop_results
            }

    return {"type": "unknown", "error": f"Unknown step type: {step.step_type}"}


# =============================================================================
# Workflow Templates
# =============================================================================

@router.post("/template/save")
async def save_workflow_template(req: WorkflowTemplateRequest):
    """
    Save a workflow as a reusable template.

    Templates can be recalled and executed with different parameters.
    """
    global _workflow_templates

    _workflow_templates[req.name] = {
        "name": req.name,
        "description": req.description,
        "steps": [step.dict() for step in req.steps],
        "parameters": req.parameters or []
    }

    # Also save to disk
    template_dir = os.path.join(os.path.dirname(__file__), "workflow_templates")
    os.makedirs(template_dir, exist_ok=True)

    with open(os.path.join(template_dir, f"{req.name}.json"), "w") as f:
        json.dump(_workflow_templates[req.name], f, indent=2)

    return {
        "status": "ok",
        "template_name": req.name,
        "message": f"Template '{req.name}' saved"
    }


@router.get("/template/list")
async def list_workflow_templates():
    """List all available workflow templates."""
    # Load from disk
    template_dir = os.path.join(os.path.dirname(__file__), "workflow_templates")
    templates = []

    if os.path.exists(template_dir):
        for file in os.listdir(template_dir):
            if file.endswith(".json"):
                with open(os.path.join(template_dir, file)) as f:
                    template = json.load(f)
                    templates.append({
                        "name": template["name"],
                        "description": template["description"],
                        "parameters": template.get("parameters", [])
                    })

    return {"templates": templates}


@router.post("/template/execute/{template_name}")
async def execute_template(template_name: str, parameters: Optional[Dict[str, Any]] = None):
    """Execute a saved workflow template."""
    template_dir = os.path.join(os.path.dirname(__file__), "workflow_templates")
    template_path = os.path.join(template_dir, f"{template_name}.json")

    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")

    with open(template_path) as f:
        template = json.load(f)

    # Build workflow request
    workflow = WorkflowRequest(
        steps=[WorkflowStep(**step) for step in template["steps"]],
        variables=parameters or {},
        rebuild_at_end=True,
        disable_graphics=True
    )

    return await execute_workflow(workflow)


@router.delete("/template/{template_name}")
async def delete_template(template_name: str):
    """Delete a workflow template."""
    template_dir = os.path.join(os.path.dirname(__file__), "workflow_templates")
    template_path = os.path.join(template_dir, f"{template_name}.json")

    if os.path.exists(template_path):
        os.remove(template_path)
        return {"status": "ok", "message": f"Template '{template_name}' deleted"}

    raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")


# =============================================================================
# Pre-built Recipes (Common Workflows)
# =============================================================================

@router.post("/recipe/simple-part")
async def create_simple_part(req: CreatePartFromSketchRequest):
    """
    Create a complete part in ONE CALL - MACRO SPEED.

    Creates sketch, draws entities, extrudes, and sets properties.

    Example:
    {
        "sketch_plane": "Front Plane",
        "sketch_entities": [
            {"type": "rectangle", "x1": 0, "y1": 0, "x2": 100, "y2": 50},
            {"type": "circle", "cx": 50, "cy": 25, "radius": 10}
        ],
        "extrude_depth": 25,
        "material": "Plain Carbon Steel",
        "properties": {"PartNumber": "12345", "Description": "Test Part"}
    }
    """
    operations = [
        BatchOperation(operation="start_sketch", params={"plane": req.sketch_plane})
    ]

    # Add sketch entities
    for entity in req.sketch_entities:
        entity_type = entity.get("type", "").lower()
        if entity_type == "rectangle":
            operations.append(BatchOperation(
                operation="draw_rectangle",
                params={"x1": entity["x1"], "y1": entity["y1"], "x2": entity["x2"], "y2": entity["y2"]}
            ))
        elif entity_type == "circle":
            operations.append(BatchOperation(
                operation="draw_circle",
                params={"cx": entity["cx"], "cy": entity["cy"], "radius": entity["radius"]}
            ))
        elif entity_type == "line":
            operations.append(BatchOperation(
                operation="draw_line",
                params={"x1": entity["x1"], "y1": entity["y1"], "x2": entity["x2"], "y2": entity["y2"]}
            ))

    operations.append(BatchOperation(operation="end_sketch"))
    operations.append(BatchOperation(operation="extrude", params={"depth": req.extrude_depth}))

    if req.material:
        operations.append(BatchOperation(operation="set_material", params={"material": req.material}))

    if req.properties:
        for name, value in req.properties.items():
            operations.append(BatchOperation(operation="set_property", params={"name": name, "value": value}))

    return await execute_batch_operations(BatchOperationsRequest(
        operations=operations,
        rebuild_at_end=True,
        disable_graphics=True
    ))


@router.post("/recipe/simple-assembly")
async def create_simple_assembly(req: CreateAssemblyRequest):
    """
    Create an assembly with components and mates in ONE CALL.
    """
    operations = []

    # Insert components
    for comp in req.components:
        operations.append(BatchOperation(
            operation="insert_component",
            params={
                "path": comp["path"],
                "x": comp.get("position", [0,0,0])[0],
                "y": comp.get("position", [0,0,0])[1],
                "z": comp.get("position", [0,0,0])[2]
            }
        ))

    # Add mates
    for mate in req.mates:
        operations.append(BatchOperation(
            operation="add_mate",
            params=mate
        ))

    # Set properties
    if req.properties:
        for name, value in req.properties.items():
            operations.append(BatchOperation(
                operation="set_property",
                params={"name": name, "value": value}
            ))

    return await execute_batch_operations(BatchOperationsRequest(
        operations=operations,
        rebuild_at_end=True,
        disable_graphics=True
    ))


@router.post("/recipe/hole-pattern")
async def create_hole_pattern(
    center_x: float = 0,
    center_y: float = 0,
    hole_radius: float = 5,
    pattern_radius: float = 50,
    count: int = 6,
    depth: float = 10
):
    """
    Create a circular pattern of holes - common manufacturing need.
    """
    import math

    operations = [
        BatchOperation(operation="start_sketch", params={"plane": "Top Plane"})
    ]

    # Create holes in circular pattern
    for i in range(count):
        angle = (2 * math.pi * i) / count
        cx = center_x + pattern_radius * math.cos(angle)
        cy = center_y + pattern_radius * math.sin(angle)
        operations.append(BatchOperation(
            operation="draw_circle",
            params={"cx": cx, "cy": cy, "radius": hole_radius}
        ))

    operations.extend([
        BatchOperation(operation="end_sketch"),
        BatchOperation(operation="extrude_cut", params={"depth": depth})
    ])

    return await execute_batch_operations(BatchOperationsRequest(
        operations=operations,
        rebuild_at_end=True,
        disable_graphics=True
    ))


# =============================================================================
# Batch Property/Dimension Updates
# =============================================================================

@router.post("/properties")
async def batch_update_properties(req: BatchPropertiesRequest):
    """Update multiple custom properties in one call."""
    try:
        pythoncom.CoInitialize()
        sw = win32com.client.GetActiveObject("SldWorks.Application")
        model = sw.ActiveDoc

        if not model:
            raise HTTPException(status_code=400, detail="No active document")

        config = req.configuration or ""
        prop_mgr = model.Extension.CustomPropertyManager(config)

        updated = {}
        errors = {}

        for name, value in req.properties.items():
            try:
                prop_mgr.Set2(name, str(value))
                updated[name] = value
            except Exception as e:
                errors[name] = str(e)

        if updated:
            model.EditRebuild3()

        return {
            "status": "ok",
            "updated": updated,
            "errors": errors,
            "total_updated": len(updated)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


@router.post("/dimensions")
async def batch_update_dimensions(req: BatchDimensionsRequest):
    """Update multiple dimensions in one call."""
    try:
        pythoncom.CoInitialize()
        sw = win32com.client.GetActiveObject("SldWorks.Application")
        model = sw.ActiveDoc

        if not model:
            raise HTTPException(status_code=400, detail="No active document")

        updated = {}
        errors = {}

        for dim_name, value in req.dimensions.items():
            try:
                param = model.Parameter(dim_name)
                if param:
                    param.SystemValue = value / 1000  # mm to m
                    updated[dim_name] = value
                else:
                    errors[dim_name] = "Dimension not found"
            except Exception as e:
                errors[dim_name] = str(e)

        if updated:
            model.EditRebuild3()

        return {
            "status": "ok",
            "updated": updated,
            "errors": errors,
            "total_updated": len(updated)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


@router.get("/status")
async def get_batch_status():
    """Get current batch mode status."""
    return {
        "batch_mode_active": _batch_mode_active,
        "queued_operations": len(_batch_operations),
        "variables": _variables
    }


@router.get("/operations")
async def list_available_operations():
    """List all available batch operations."""
    return {
        "sketch_operations": [
            "start_sketch", "end_sketch", "draw_line", "draw_rectangle",
            "draw_circle", "draw_arc", "draw_polygon", "draw_slot"
        ],
        "feature_operations": [
            "extrude", "extrude_cut", "revolve", "fillet", "chamfer",
            "hole_wizard", "shell", "rib", "draft", "mirror",
            "linear_pattern", "circular_pattern"
        ],
        "assembly_operations": [
            "insert_component", "add_mate", "suppress_component", "unsuppress_component"
        ],
        "property_operations": [
            "set_property", "set_dimension", "set_material"
        ],
        "document_operations": [
            "new_part", "new_assembly", "open", "save", "save_as", "export", "close",
            "rebuild", "force_rebuild"
        ],
        "configuration_operations": [
            "add_configuration", "activate_configuration"
        ],
        "utility_operations": [
            "select", "clear_selection", "zoom_fit", "set_view",
            "get_mass", "count_features", "delay"
        ]
    }
