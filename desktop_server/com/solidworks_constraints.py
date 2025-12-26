"""
SolidWorks Sketch Constraints API
=================================
Full constraint management for 2D sketches including:
- Geometric constraints (horizontal, vertical, parallel, perpendicular)
- Dimensional constraints (fix, equal, symmetric)
- Relation management and constraint solving
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from enum import IntEnum
from dataclasses import dataclass, field
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# COM imports
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


class ConstraintType(IntEnum):
    """SolidWorks sketch constraint types (swConstraintType_e)."""
    HORIZONTAL = 0
    VERTICAL = 1
    COLLINEAR = 2
    CORADIAL = 3
    PERPENDICULAR = 4
    PARALLEL = 5
    TANGENT = 6
    CONCENTRIC = 7
    MIDPOINT = 8
    COINCIDENT = 9
    EQUAL = 10
    SYMMETRIC = 11
    FIX = 12
    PIERCE = 13
    MERGE = 14
    ALONG_X = 15
    ALONG_Y = 16
    ALONG_Z = 17
    SAME_CURVE = 18


class DimensionType(IntEnum):
    """SolidWorks dimension types."""
    LINEAR = 0
    ANGULAR = 1
    RADIAL = 2
    DIAMETER = 3
    ORDINATE = 4
    ARC_LENGTH = 5


@dataclass
class ConstraintInfo:
    """Information about a sketch constraint."""
    type: str
    entities: List[str]
    status: str  # "satisfied", "over_defined", "under_defined"
    can_delete: bool = True


@dataclass
class SketchStatus:
    """Overall sketch constraint status."""
    fully_defined: bool
    under_defined_count: int
    over_defined_count: int
    total_constraints: int
    total_dimensions: int
    degrees_of_freedom: int


# Pydantic models for API
class AddConstraintRequest(BaseModel):
    constraint_type: str  # "horizontal", "vertical", "equal", etc.
    entity_names: List[str] = []  # Names or indices of entities to constrain


class AddDimensionRequest(BaseModel):
    dimension_type: str = "linear"  # "linear", "angular", "radial", "diameter"
    value: float
    entity_names: List[str] = []


class FixEntityRequest(BaseModel):
    entity_name: str


class SymmetricConstraintRequest(BaseModel):
    entity1: str
    entity2: str
    centerline: str


class EqualConstraintRequest(BaseModel):
    entities: List[str]  # 2 or more entities to make equal


class TangentConstraintRequest(BaseModel):
    entity1: str
    entity2: str


class CoincidentConstraintRequest(BaseModel):
    point_entity: str
    target_entity: str


class DeleteConstraintRequest(BaseModel):
    constraint_index: int


router = APIRouter(prefix="/solidworks-constraints", tags=["solidworks-constraints"])


def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")

    pythoncom.CoInitialize()
    try:
        sw = win32com.client.GetActiveObject("SldWorks.Application")
        return sw
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


def get_active_sketch(sw):
    """Get currently active sketch."""
    doc = sw.ActiveDoc
    if not doc:
        raise HTTPException(status_code=404, detail="No document open")

    sketch = doc.GetActiveSketch2()
    if not sketch:
        raise HTTPException(status_code=404, detail="No active sketch - enter sketch edit mode first")

    return doc, sketch


# =============================================================================
# Geometric Constraints
# =============================================================================

@router.post("/constraint/horizontal")
async def add_horizontal_constraint(request: AddConstraintRequest):
    """
    Add horizontal constraint to selected line(s).
    Makes lines perfectly horizontal (parallel to X-axis).
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager

        # Get selected entities or use provided names
        sel_mgr = doc.SelectionManager
        count = sel_mgr.GetSelectedObjectCount2(-1)

        if count == 0:
            raise HTTPException(status_code=400, detail="Select line(s) first")

        # Add horizontal relation
        result = sm.CreateHorizontalConstraint2(True)  # True = add to all selected

        return {
            "success": result is not None,
            "constraint_type": "horizontal",
            "message": "Horizontal constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Horizontal constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/vertical")
async def add_vertical_constraint(request: AddConstraintRequest):
    """
    Add vertical constraint to selected line(s).
    Makes lines perfectly vertical (parallel to Y-axis).
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreateVerticalConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "vertical",
            "message": "Vertical constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vertical constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/parallel")
async def add_parallel_constraint():
    """
    Add parallel constraint between two selected lines.
    Makes lines parallel to each other.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) < 2:
            raise HTTPException(status_code=400, detail="Select two lines")

        sm = doc.SketchManager
        result = sm.CreateParallelConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "parallel",
            "message": "Parallel constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parallel constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/perpendicular")
async def add_perpendicular_constraint():
    """
    Add perpendicular constraint between two selected lines.
    Makes lines perpendicular (90 degrees) to each other.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) < 2:
            raise HTTPException(status_code=400, detail="Select two lines")

        sm = doc.SketchManager
        result = sm.CreatePerpendicularConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "perpendicular",
            "message": "Perpendicular constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Perpendicular constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/tangent")
async def add_tangent_constraint(request: TangentConstraintRequest):
    """
    Add tangent constraint between two curves.
    Makes curves tangent at their intersection point.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreateTangentConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "tangent",
            "message": "Tangent constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tangent constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/collinear")
async def add_collinear_constraint():
    """
    Add collinear constraint between two or more lines.
    Makes lines lie on the same infinite line.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreateCollinearConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "collinear",
            "message": "Collinear constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Collinear constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/concentric")
async def add_concentric_constraint():
    """
    Add concentric constraint between circles/arcs.
    Makes circles share the same center point.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreateConcentricConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "concentric",
            "message": "Concentric constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Concentric constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Dimensional Constraints
# =============================================================================

@router.post("/constraint/fix")
async def add_fix_constraint(request: FixEntityRequest):
    """
    Fix an entity in place (lock position).
    Prevents the entity from moving during constraint solving.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        # Select the entity if name provided
        if request.entity_name:
            doc.Extension.SelectByID2(
                request.entity_name, "SKETCHSEGMENT", 0, 0, 0, False, 0, None, 0
            )

        sm = doc.SketchManager
        result = sm.CreateFixConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "fix",
            "entity": request.entity_name,
            "message": "Entity fixed in place"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fix constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/equal")
async def add_equal_constraint(request: EqualConstraintRequest):
    """
    Add equal constraint between entities.
    Makes lines equal length or circles/arcs equal radius.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        if len(request.entities) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 entities")

        # Select entities
        doc.ClearSelection2(True)
        for i, entity in enumerate(request.entities):
            doc.Extension.SelectByID2(
                entity, "SKETCHSEGMENT", 0, 0, 0,
                i > 0,  # Append after first selection
                0, None, 0
            )

        sm = doc.SketchManager
        result = sm.CreateEqualConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "equal",
            "entities": request.entities,
            "message": "Equal constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Equal constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/symmetric")
async def add_symmetric_constraint(request: SymmetricConstraintRequest):
    """
    Add symmetric constraint about a centerline.
    Makes two entities symmetric about the specified line.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        # Select entities: first two entities, then centerline
        doc.ClearSelection2(True)
        doc.Extension.SelectByID2(request.entity1, "SKETCHSEGMENT", 0, 0, 0, False, 0, None, 0)
        doc.Extension.SelectByID2(request.entity2, "SKETCHSEGMENT", 0, 0, 0, True, 0, None, 0)
        doc.Extension.SelectByID2(request.centerline, "SKETCHSEGMENT", 0, 0, 0, True, 0, None, 0)

        sm = doc.SketchManager
        result = sm.CreateSymmetricConstraint()

        return {
            "success": result is not None,
            "constraint_type": "symmetric",
            "entity1": request.entity1,
            "entity2": request.entity2,
            "centerline": request.centerline,
            "message": "Symmetric constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Symmetric constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/coincident")
async def add_coincident_constraint(request: CoincidentConstraintRequest):
    """
    Add coincident constraint between point and entity.
    Makes a point lie on a line, curve, or another point.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        doc.ClearSelection2(True)
        doc.Extension.SelectByID2(request.point_entity, "SKETCHPOINT", 0, 0, 0, False, 0, None, 0)
        doc.Extension.SelectByID2(request.target_entity, "SKETCHSEGMENT", 0, 0, 0, True, 0, None, 0)

        sm = doc.SketchManager
        result = sm.CreateCoincidentConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "coincident",
            "message": "Coincident constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Coincident constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/midpoint")
async def add_midpoint_constraint():
    """
    Add midpoint constraint.
    Places a point at the midpoint of a line.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreateMidpointConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "midpoint",
            "message": "Midpoint constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Midpoint constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Dimensions
# =============================================================================

@router.post("/dimension/add")
async def add_dimension(request: AddDimensionRequest):
    """
    Add a driving dimension to selected entities.

    dimension_type: "linear", "angular", "radial", "diameter"
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) == 0:
            raise HTTPException(status_code=400, detail="Select entity to dimension")

        # Create dimension based on type
        dim = None
        if request.dimension_type == "linear":
            dim = doc.AddDimension2(0, 0, 0)
        elif request.dimension_type == "angular":
            dim = doc.AddDimension2(0, 0, 0)
        elif request.dimension_type in ["radial", "diameter"]:
            dim = doc.AddDimension2(0, 0, 0)

        if dim:
            # Set the dimension value
            dim_obj = dim.GetDimension()
            if dim_obj:
                dim_obj.SetSystemValue3(
                    request.value / 1000.0,  # Convert mm to meters
                    1,  # swSetValue_InThisConfiguration
                    None
                )

        return {
            "success": dim is not None,
            "dimension_type": request.dimension_type,
            "value": request.value,
            "message": f"Dimension of {request.value}mm added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/driven")
async def make_dimension_driven():
    """
    Convert selected dimension from driving to driven (reference).
    Driven dimensions display value but don't control geometry.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) == 0:
            raise HTTPException(status_code=400, detail="Select a dimension")

        dim = sel_mgr.GetSelectedObject6(1, -1)
        if dim:
            display_dim = dim.GetDisplayDimension()
            if display_dim:
                display_dim.SetDrivenState(True)

        return {
            "success": True,
            "message": "Dimension converted to driven (reference)"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Make driven failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Constraint Status & Management
# =============================================================================

@router.get("/status")
async def get_sketch_status():
    """
    Get overall constraint status of active sketch.
    Returns degrees of freedom, over/under defined status.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        # Get sketch solve status
        status = sketch.GetSolveStatus()

        # Count constraints
        relations = sketch.GetSketchRelations()
        relation_count = len(relations) if relations else 0

        # Count dimensions
        dims = sketch.GetSketchDimensions()
        dim_count = len(dims) if dims else 0

        # Get DOF (degrees of freedom)
        # Status: 0 = fully defined, 1 = under, 2 = over, 3 = invalid
        status_map = {
            0: "fully_defined",
            1: "under_defined",
            2: "over_defined",
            3: "invalid_geometry"
        }

        return {
            "status": status_map.get(status, "unknown"),
            "fully_defined": status == 0,
            "solve_status_code": status,
            "constraint_count": relation_count,
            "dimension_count": dim_count,
            "total_constraints": relation_count + dim_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/constraints")
async def list_constraints():
    """
    List all constraints in active sketch.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        relations = sketch.GetSketchRelations()

        constraints = []
        if relations:
            for i, rel in enumerate(relations):
                try:
                    rel_type = rel.GetRelationType()
                    type_name = ConstraintType(rel_type).name if rel_type < len(ConstraintType) else f"TYPE_{rel_type}"

                    constraints.append({
                        "index": i,
                        "type": type_name,
                        "type_code": rel_type,
                        "suppressed": rel.GetSuppression() if hasattr(rel, 'GetSuppression') else False
                    })
                except Exception:
                    constraints.append({
                        "index": i,
                        "type": "UNKNOWN",
                        "type_code": -1
                    })

        return {
            "count": len(constraints),
            "constraints": constraints
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List constraints failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/constraint/{index}")
async def delete_constraint(index: int):
    """
    Delete a constraint by index.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        relations = sketch.GetSketchRelations()
        if not relations or index >= len(relations):
            raise HTTPException(status_code=404, detail=f"Constraint {index} not found")

        rel = relations[index]
        result = rel.Delete()

        return {
            "success": result,
            "deleted_index": index,
            "message": f"Constraint {index} deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/auto-constrain")
async def auto_add_constraints():
    """
    Automatically add constraints to fully define sketch.
    SolidWorks will infer horizontal, vertical, equal, etc.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager

        # Auto-constrain with default settings
        # Parameters: horizontal, vertical, equal, etc.
        result = sm.FullyDefineSketch(
            True,   # Add relations
            True,   # Add dimensions
            1,      # Horizontal scheme (0=none, 1=auto)
            1,      # Vertical scheme
            True,   # Mark as construction
            None,   # Selected entities (None = all)
            0, 0,   # Dimension position
            0, 0    # Reference
        )

        return {
            "success": True,
            "message": "Auto-constraints applied",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-constrain failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/construction-geometry")
async def toggle_construction_geometry():
    """
    Toggle selected entities as construction geometry.
    Construction geometry is used for reference but doesn't create features.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        sm.CreateConstructionGeometry()

        return {
            "success": True,
            "message": "Construction geometry toggled"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Toggle construction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Advanced Constraints
# =============================================================================

@router.post("/constraint/pierce")
async def add_pierce_constraint():
    """
    Add pierce constraint.
    Makes a point coincident with where a curve pierces the sketch plane.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreatePierceConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "pierce",
            "message": "Pierce constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pierce constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/coradial")
async def add_coradial_constraint():
    """
    Add coradial constraint between arcs/circles.
    Makes arcs share the same radius value.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreateCoradialConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "coradial",
            "message": "Coradial constraint added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Coradial constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/merge")
async def add_merge_constraint():
    """
    Merge two points into one.
    Combines two sketch points into a single point.
    """
    try:
        sw = get_solidworks()
        doc, sketch = get_active_sketch(sw)

        sm = doc.SketchManager
        result = sm.CreateMergeConstraint2(True)

        return {
            "success": result is not None,
            "constraint_type": "merge",
            "message": "Points merged"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Merge constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
