"""
SolidWorks Equations & Global Variables API
============================================
Full equation management including:
- Global variables
- Dimension equations
- Linked values
- Equation-driven geometry
- Suppression equations
"""

import logging
from typing import Optional, Dict, Any, List
from enum import IntEnum
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


class EquationType(IntEnum):
    """Equation types."""
    GLOBAL_VARIABLE = 0
    DIMENSION = 1
    FEATURE_SUPPRESSION = 2
    COMPONENT_SUPPRESSION = 3


# Pydantic models
class AddGlobalVariableRequest(BaseModel):
    name: str
    value: float
    units: str = "mm"  # mm, in, deg, etc.


class AddEquationRequest(BaseModel):
    equation: str  # e.g., '"D1@Sketch1" = "Width" * 2'
    index: int = -1  # -1 = append to end


class LinkDimensionsRequest(BaseModel):
    source_dimension: str  # e.g., "D1@Sketch1"
    target_dimension: str  # e.g., "D2@Sketch2"
    multiplier: float = 1.0
    offset: float = 0.0


class SuppressionEquationRequest(BaseModel):
    feature_name: str
    condition: str  # e.g., '"Width" > 100'


router = APIRouter(prefix="/solidworks-equations", tags=["solidworks-equations"])


def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


def get_equation_manager(doc):
    """Get equation manager from document."""
    eq_mgr = doc.GetEquationMgr()
    if not eq_mgr:
        raise HTTPException(status_code=501, detail="Equation manager not available")
    return eq_mgr


# =============================================================================
# Global Variables
# =============================================================================

@router.post("/global-variable/add")
async def add_global_variable(request: AddGlobalVariableRequest):
    """
    Add a global variable to the model.
    Global variables can be referenced in equations and dimensions.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        # Format: "name" = value
        equation = f'"{request.name}" = {request.value}'

        # Add as global variable
        index = eq_mgr.Add2(-1, equation, True)  # True = global variable

        doc.EditRebuild3()

        return {
            "success": index >= 0,
            "name": request.name,
            "value": request.value,
            "units": request.units,
            "index": index,
            "message": f"Global variable '{request.name}' = {request.value} added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add global variable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/global-variables")
async def list_global_variables():
    """
    List all global variables in the model.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        variables = []
        count = eq_mgr.GetCount()

        for i in range(count):
            try:
                eq = eq_mgr.Equation(i)
                if eq_mgr.GlobalVariable(i):
                    # Parse equation to get name and value
                    parts = eq.split("=")
                    if len(parts) >= 2:
                        name = parts[0].strip().strip('"')
                        value = eq_mgr.Value(i)
                        variables.append({
                            "index": i,
                            "name": name,
                            "value": value,
                            "equation": eq
                        })
            except Exception:
                pass

        return {
            "count": len(variables),
            "variables": variables
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List global variables failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.put("/global-variable/{name}")
async def update_global_variable(name: str, value: float):
    """
    Update a global variable value.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        # Find the variable
        count = eq_mgr.GetCount()
        found = False

        for i in range(count):
            if eq_mgr.GlobalVariable(i):
                eq = eq_mgr.Equation(i)
                if f'"{name}"' in eq:
                    # Update the equation
                    new_eq = f'"{name}" = {value}'
                    eq_mgr.Equation(i, new_eq)
                    found = True
                    break

        if not found:
            raise HTTPException(status_code=404, detail=f"Variable '{name}' not found")

        doc.EditRebuild3()

        return {
            "success": True,
            "name": name,
            "new_value": value,
            "message": f"Variable '{name}' updated to {value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update global variable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/global-variable/{name}")
async def delete_global_variable(name: str):
    """
    Delete a global variable.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        count = eq_mgr.GetCount()
        for i in range(count):
            if eq_mgr.GlobalVariable(i):
                eq = eq_mgr.Equation(i)
                if f'"{name}"' in eq:
                    eq_mgr.Delete(i)
                    doc.EditRebuild3()
                    return {"success": True, "deleted": name}

        raise HTTPException(status_code=404, detail=f"Variable '{name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete global variable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Dimension Equations
# =============================================================================

@router.post("/equation/add")
async def add_equation(request: AddEquationRequest):
    """
    Add an equation to link dimensions.

    Example equations:
    - '"D1@Sketch1" = "Width"'
    - '"D2@Sketch1" = "D1@Sketch1" * 2'
    - '"D3@Boss-Extrude1" = "Length" + 10'
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        index = eq_mgr.Add2(request.index, request.equation, False)

        doc.EditRebuild3()

        return {
            "success": index >= 0,
            "equation": request.equation,
            "index": index,
            "message": "Equation added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add equation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/equations")
async def list_equations():
    """
    List all equations in the model.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        equations = []
        count = eq_mgr.GetCount()

        for i in range(count):
            try:
                eq = eq_mgr.Equation(i)
                value = eq_mgr.Value(i)
                is_global = eq_mgr.GlobalVariable(i)
                status = eq_mgr.Status(i)  # 0=OK, 1=Error

                equations.append({
                    "index": i,
                    "equation": eq,
                    "value": value,
                    "is_global_variable": is_global,
                    "status": "OK" if status == 0 else "Error",
                    "suppressed": eq_mgr.Suppression(i) if hasattr(eq_mgr, 'Suppression') else False
                })
            except Exception:
                pass

        return {
            "count": len(equations),
            "equations": equations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List equations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.put("/equation/{index}")
async def update_equation(index: int, equation: str):
    """
    Update an equation at specified index.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        if index >= eq_mgr.GetCount():
            raise HTTPException(status_code=404, detail=f"Equation index {index} not found")

        eq_mgr.Equation(index, equation)
        doc.EditRebuild3()

        return {
            "success": True,
            "index": index,
            "new_equation": equation
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update equation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/equation/{index}")
async def delete_equation(index: int):
    """
    Delete an equation at specified index.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        if index >= eq_mgr.GetCount():
            raise HTTPException(status_code=404, detail=f"Equation index {index} not found")

        eq_mgr.Delete(index)
        doc.EditRebuild3()

        return {"success": True, "deleted_index": index}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete equation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Linked Dimensions
# =============================================================================

@router.post("/link-dimensions")
async def link_dimensions(request: LinkDimensionsRequest):
    """
    Link two dimensions with optional multiplier and offset.
    target = source * multiplier + offset
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        # Build equation
        if request.multiplier == 1.0 and request.offset == 0.0:
            equation = f'"{request.target_dimension}" = "{request.source_dimension}"'
        elif request.offset == 0.0:
            equation = f'"{request.target_dimension}" = "{request.source_dimension}" * {request.multiplier}'
        else:
            equation = f'"{request.target_dimension}" = "{request.source_dimension}" * {request.multiplier} + {request.offset}'

        index = eq_mgr.Add2(-1, equation, False)
        doc.EditRebuild3()

        return {
            "success": index >= 0,
            "source": request.source_dimension,
            "target": request.target_dimension,
            "multiplier": request.multiplier,
            "offset": request.offset,
            "equation": equation,
            "index": index
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Link dimensions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Suppression Equations
# =============================================================================

@router.post("/suppression-equation")
async def add_suppression_equation(request: SuppressionEquationRequest):
    """
    Add a conditional suppression equation for a feature.
    Feature will be suppressed when condition is true.

    Example conditions:
    - '"Width" > 100' - Suppress when Width > 100
    - '"Type" = 1' - Suppress when Type equals 1
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        # Format: "FeatureName" = if(condition, "suppressed", "unsuppressed")
        equation = f'"{request.feature_name}" = if({request.condition}, "suppressed", "unsuppressed")'

        index = eq_mgr.Add2(-1, equation, False)
        doc.EditRebuild3()

        return {
            "success": index >= 0,
            "feature": request.feature_name,
            "condition": request.condition,
            "equation": equation,
            "index": index
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add suppression equation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Equation Utilities
# =============================================================================

@router.post("/evaluate")
async def evaluate_expression(expression: str):
    """
    Evaluate a mathematical expression using SolidWorks equation solver.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        # Add temporary equation to evaluate
        temp_name = "__temp_eval__"
        equation = f'"{temp_name}" = {expression}'

        index = eq_mgr.Add2(-1, equation, True)

        if index >= 0:
            value = eq_mgr.Value(index)
            eq_mgr.Delete(index)

            return {
                "expression": expression,
                "result": value
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid expression")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluate expression failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/import")
async def import_equations(equations: List[str]):
    """
    Import multiple equations at once.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        results = []
        for eq in equations:
            try:
                index = eq_mgr.Add2(-1, eq, "=" not in eq or eq.count("=") == 1)
                results.append({
                    "equation": eq,
                    "success": index >= 0,
                    "index": index
                })
            except Exception as e:
                results.append({
                    "equation": eq,
                    "success": False,
                    "error": str(e)
                })

        doc.EditRebuild3()

        return {
            "imported": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import equations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/export")
async def export_equations():
    """
    Export all equations as text.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        equations = []
        count = eq_mgr.GetCount()

        for i in range(count):
            try:
                eq = eq_mgr.Equation(i)
                equations.append(eq)
            except Exception:
                pass

        return {
            "count": len(equations),
            "equations": equations,
            "text": "\n".join(equations)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export equations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/rebuild")
async def rebuild_equations():
    """
    Force rebuild of all equations.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        eq_mgr = get_equation_manager(doc)

        # Trigger recalculation
        eq_mgr.UpdateReferences()
        doc.EditRebuild3()

        return {"success": True, "message": "Equations rebuilt"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rebuild equations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
