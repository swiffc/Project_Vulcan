"""
SolidWorks Design Study & Optimization API
==========================================
Parametric optimization and design exploration including:
- Design study creation and management
- Parameter sweeps and DOE (Design of Experiments)
- Optimization goals and constraints
- Sensitivity analysis
- What-if scenarios
"""

import logging
import itertools
from typing import Optional, Dict, Any, List
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


class StudyType(IntEnum):
    """Design study types."""
    EVALUATION = 0  # What-if scenarios
    OPTIMIZATION = 1  # Find optimal values
    DOE = 2  # Design of Experiments


class OptimizationGoal(IntEnum):
    """Optimization objectives."""
    MINIMIZE = 0
    MAXIMIZE = 1
    TARGET = 2  # Target specific value


class ConstraintType(IntEnum):
    """Design constraint types."""
    LESS_THAN = 0
    GREATER_THAN = 1
    EQUAL_TO = 2
    RANGE = 3


class DOEMethod(IntEnum):
    """DOE sampling methods."""
    FULL_FACTORIAL = 0
    FRACTIONAL_FACTORIAL = 1
    BOX_BEHNKEN = 2
    LATIN_HYPERCUBE = 3
    CUSTOM = 4


@dataclass
class DesignVariable:
    """Design variable for optimization."""
    name: str
    dimension_name: str
    min_value: float
    max_value: float
    current_value: float
    step_size: Optional[float] = None
    num_levels: int = 3


@dataclass
class DesignConstraint:
    """Constraint for optimization."""
    name: str
    sensor_name: str
    constraint_type: str
    limit_value: float
    limit_value2: Optional[float] = None  # For range constraints


@dataclass
class OptimizationResult:
    """Result from optimization study."""
    optimal_values: Dict[str, float]
    objective_value: float
    constraints_satisfied: bool
    iterations: int


# Pydantic models
class CreateDesignStudyRequest(BaseModel):
    name: str
    study_type: str = "optimization"  # evaluation, optimization, doe


class AddVariableRequest(BaseModel):
    dimension_name: str  # Full dimension name like "D1@Sketch1"
    min_value: float
    max_value: float
    num_levels: int = 5  # Number of discrete values to test


class AddSensorRequest(BaseModel):
    sensor_name: str
    sensor_type: str = "mass"  # mass, volume, displacement, stress, etc.
    component_name: Optional[str] = None


class SetGoalRequest(BaseModel):
    sensor_name: str
    goal_type: str = "minimize"  # minimize, maximize, target
    target_value: Optional[float] = None  # Required if goal_type is "target"


class AddConstraintRequest(BaseModel):
    sensor_name: str
    constraint_type: str  # less_than, greater_than, range
    limit_value: float
    limit_value2: Optional[float] = None  # Upper limit for range


class ParameterSweepRequest(BaseModel):
    dimension_name: str
    start_value: float
    end_value: float
    num_steps: int = 10


class WhatIfRequest(BaseModel):
    parameters: Dict[str, float]  # {"D1@Sketch1": 15.0, "D2@Sketch1": 20.0}


class DOERequest(BaseModel):
    method: str = "latin_hypercube"  # full_factorial, latin_hypercube, box_behnken
    num_samples: int = 20
    variables: List[Dict[str, Any]]  # [{"name": "D1@Sketch1", "min": 10, "max": 20}, ...]


router = APIRouter(prefix="/solidworks-optimization", tags=["solidworks-optimization"])


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


# =============================================================================
# Design Study Management
# =============================================================================

@router.post("/study/create")
async def create_design_study(request: CreateDesignStudyRequest):
    """
    Create a new design study.

    study_type options:
    - evaluation: Run what-if scenarios
    - optimization: Find optimal parameter values
    - doe: Design of Experiments analysis
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Get design study manager
        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        if not ds_mgr:
            raise HTTPException(status_code=501, detail="Design Study Manager not available")

        type_map = {
            "evaluation": 0,
            "optimization": 1,
            "doe": 2
        }
        study_type = type_map.get(request.study_type.lower(), 1)

        # Create study
        study = ds_mgr.CreateDesignStudy(request.name, study_type)

        return {
            "success": study is not None,
            "name": request.name,
            "study_type": request.study_type,
            "message": f"Design study '{request.name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create design study failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/study/list")
async def list_design_studies():
    """
    List all design studies in active document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        if not ds_mgr:
            return {"count": 0, "studies": [], "message": "Design Study Manager not available"}

        count = ds_mgr.GetDesignStudyCount()
        studies = []

        for i in range(count):
            study = ds_mgr.GetDesignStudy(i)
            if study:
                studies.append({
                    "index": i,
                    "name": study.Name if hasattr(study, 'Name') else f"Study_{i}"
                })

        return {
            "count": count,
            "studies": studies
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List studies failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/study/{name}")
async def delete_design_study(name: str):
    """
    Delete a design study by name.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        if not ds_mgr:
            raise HTTPException(status_code=501, detail="Design Study Manager not available")

        result = ds_mgr.DeleteDesignStudy(name)

        return {
            "success": result,
            "deleted": name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete study failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Variables (Parameters to Optimize)
# =============================================================================

@router.post("/variable/add")
async def add_design_variable(request: AddVariableRequest):
    """
    Add a design variable (dimension) to the active study.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        study = ds_mgr.GetActiveDesignStudy() if ds_mgr else None

        if not study:
            raise HTTPException(status_code=404, detail="No active design study")

        # Add variable
        var = study.AddVariable(
            request.dimension_name,
            request.min_value / 1000.0,  # Convert mm to meters
            request.max_value / 1000.0,
            request.num_levels
        )

        return {
            "success": var is not None,
            "dimension": request.dimension_name,
            "min_mm": request.min_value,
            "max_mm": request.max_value,
            "levels": request.num_levels,
            "message": f"Variable '{request.dimension_name}' added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add variable failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/variables")
async def list_design_variables():
    """
    List all variables in active design study.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        study = ds_mgr.GetActiveDesignStudy() if ds_mgr else None

        if not study:
            raise HTTPException(status_code=404, detail="No active design study")

        count = study.GetVariableCount() if hasattr(study, 'GetVariableCount') else 0
        variables = []

        for i in range(count):
            var = study.GetVariable(i)
            if var:
                variables.append({
                    "index": i,
                    "name": var.Name if hasattr(var, 'Name') else f"Var_{i}",
                    "min": var.MinValue * 1000 if hasattr(var, 'MinValue') else 0,
                    "max": var.MaxValue * 1000 if hasattr(var, 'MaxValue') else 0
                })

        return {
            "count": count,
            "variables": variables
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List variables failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Sensors (Output to Monitor)
# =============================================================================

@router.post("/sensor/add")
async def add_sensor(request: AddSensorRequest):
    """
    Add a sensor to monitor during optimization.

    sensor_type options:
    - mass: Total mass
    - volume: Total volume
    - surface_area: Surface area
    - dimension: Track dimension value
    - simulation: FEA result (stress, displacement)
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        study = ds_mgr.GetActiveDesignStudy() if ds_mgr else None

        if not study:
            raise HTTPException(status_code=404, detail="No active design study")

        type_map = {
            "mass": 0,
            "volume": 1,
            "surface_area": 2,
            "dimension": 3,
            "simulation": 4
        }
        sensor_type = type_map.get(request.sensor_type.lower(), 0)

        # Add sensor
        sensor = study.AddSensor(
            request.sensor_name,
            sensor_type
        )

        return {
            "success": sensor is not None,
            "sensor_name": request.sensor_name,
            "sensor_type": request.sensor_type,
            "message": f"Sensor '{request.sensor_name}' added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add sensor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Goals and Constraints
# =============================================================================

@router.post("/goal/set")
async def set_optimization_goal(request: SetGoalRequest):
    """
    Set the optimization goal (what to minimize/maximize).
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        study = ds_mgr.GetActiveDesignStudy() if ds_mgr else None

        if not study:
            raise HTTPException(status_code=404, detail="No active design study")

        goal_map = {
            "minimize": 0,
            "maximize": 1,
            "target": 2
        }
        goal_type = goal_map.get(request.goal_type.lower(), 0)

        # Set goal
        result = study.SetGoal(
            request.sensor_name,
            goal_type,
            request.target_value if goal_type == 2 else 0
        )

        return {
            "success": result,
            "sensor": request.sensor_name,
            "goal_type": request.goal_type,
            "target_value": request.target_value,
            "message": f"Goal set: {request.goal_type} {request.sensor_name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set goal failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/constraint/add")
async def add_design_constraint(request: AddConstraintRequest):
    """
    Add a constraint to the optimization.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        study = ds_mgr.GetActiveDesignStudy() if ds_mgr else None

        if not study:
            raise HTTPException(status_code=404, detail="No active design study")

        type_map = {
            "less_than": 0,
            "greater_than": 1,
            "equal_to": 2,
            "range": 3
        }
        constraint_type = type_map.get(request.constraint_type.lower(), 0)

        # Add constraint
        constraint = study.AddConstraint(
            request.sensor_name,
            constraint_type,
            request.limit_value,
            request.limit_value2 if constraint_type == 3 else 0
        )

        return {
            "success": constraint is not None,
            "sensor": request.sensor_name,
            "constraint_type": request.constraint_type,
            "limit": request.limit_value,
            "message": f"Constraint added: {request.sensor_name} {request.constraint_type} {request.limit_value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add constraint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Run Studies
# =============================================================================

@router.post("/run")
async def run_design_study():
    """
    Run the active design study.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        study = ds_mgr.GetActiveDesignStudy() if ds_mgr else None

        if not study:
            raise HTTPException(status_code=404, detail="No active design study")

        # Run study
        result = study.Run()

        return {
            "success": result,
            "message": "Design study completed" if result else "Study failed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run study failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/results")
async def get_study_results():
    """
    Get results from the last design study run.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        ext = doc.Extension
        ds_mgr = ext.GetDesignStudyManager()
        study = ds_mgr.GetActiveDesignStudy() if ds_mgr else None

        if not study:
            raise HTTPException(status_code=404, detail="No active design study")

        # Get results
        results = {
            "study_name": study.Name if hasattr(study, 'Name') else "Unknown",
            "scenarios_run": study.GetScenarioCount() if hasattr(study, 'GetScenarioCount') else 0,
            "optimal_scenario": None,
            "variables": [],
            "constraints_satisfied": True
        }

        # Get optimal values if available
        if hasattr(study, 'GetOptimalScenario'):
            optimal = study.GetOptimalScenario()
            if optimal:
                results["optimal_scenario"] = optimal

        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get results failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Parameter Sweep (Manual)
# =============================================================================

@router.post("/sweep")
async def parameter_sweep(request: ParameterSweepRequest):
    """
    Perform a parameter sweep on a single dimension.
    Returns values at each step.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Get the dimension
        dim = doc.Parameter(request.dimension_name)
        if not dim:
            raise HTTPException(status_code=404, detail=f"Dimension '{request.dimension_name}' not found")

        original_value = dim.SystemValue * 1000  # Convert to mm

        # Calculate step size
        step = (request.end_value - request.start_value) / (request.num_steps - 1)

        results = []
        for i in range(request.num_steps):
            value = request.start_value + (i * step)

            # Set dimension value
            dim.SetSystemValue3(value / 1000.0, 1, None)  # Convert mm to m
            doc.EditRebuild3()

            # Get mass properties
            props = doc.Extension.CreateMassProperty()
            mass = props.Mass if props else 0
            volume = props.Volume if props else 0

            results.append({
                "step": i,
                "value_mm": round(value, 3),
                "mass_kg": round(mass, 4),
                "volume_m3": round(volume, 9)
            })

        # Restore original value
        dim.SetSystemValue3(original_value / 1000.0, 1, None)
        doc.EditRebuild3()

        return {
            "dimension": request.dimension_name,
            "start_mm": request.start_value,
            "end_mm": request.end_value,
            "steps": request.num_steps,
            "results": results,
            "original_value_mm": original_value
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parameter sweep failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/what-if")
async def what_if_scenario(request: WhatIfRequest):
    """
    Run a what-if scenario with specific parameter values.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Store original values
        originals = {}
        for dim_name, value in request.parameters.items():
            dim = doc.Parameter(dim_name)
            if dim:
                originals[dim_name] = dim.SystemValue * 1000

        # Apply new values
        for dim_name, value in request.parameters.items():
            dim = doc.Parameter(dim_name)
            if dim:
                dim.SetSystemValue3(value / 1000.0, 1, None)

        # Rebuild
        doc.EditRebuild3()

        # Get results
        props = doc.Extension.CreateMassProperty()
        results = {
            "parameters_set": request.parameters,
            "mass_kg": round(props.Mass, 4) if props else 0,
            "volume_m3": round(props.Volume, 9) if props else 0,
            "surface_area_m2": round(props.SurfaceArea, 6) if props else 0,
            "center_of_mass": list(props.CenterOfMass) if props and props.CenterOfMass else None
        }

        # Restore original values
        for dim_name, value in originals.items():
            dim = doc.Parameter(dim_name)
            if dim:
                dim.SetSystemValue3(value / 1000.0, 1, None)
        doc.EditRebuild3()

        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"What-if failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# DOE (Design of Experiments)
# =============================================================================

@router.post("/doe/generate")
async def generate_doe_matrix(request: DOERequest):
    """
    Generate a DOE sampling matrix.

    Methods:
    - full_factorial: All combinations (n^k samples)
    - latin_hypercube: Space-filling design
    - box_behnken: Response surface method
    """
    try:
        import random

        variables = request.variables
        num_vars = len(variables)

        if num_vars == 0:
            raise HTTPException(status_code=400, detail="No variables provided")

        samples = []

        if request.method == "full_factorial":
            # Generate all combinations
            levels = []
            for var in variables:
                var_levels = []
                step = (var["max"] - var["min"]) / (request.num_samples - 1) if request.num_samples > 1 else 0
                for i in range(request.num_samples):
                    var_levels.append(var["min"] + i * step)
                levels.append(var_levels)

            # Full factorial combination
            for combo in itertools.product(*levels[:min(3, num_vars)]):  # Limit for practicality
                sample = {}
                for i, var in enumerate(variables[:len(combo)]):
                    sample[var["name"]] = round(combo[i], 3)
                samples.append(sample)

        elif request.method == "latin_hypercube":
            # Latin Hypercube Sampling
            for i in range(request.num_samples):
                sample = {}
                for var in variables:
                    # Divide range into n intervals, pick one from each
                    interval = (var["max"] - var["min"]) / request.num_samples
                    value = var["min"] + (i + random.random()) * interval
                    sample[var["name"]] = round(value, 3)
                samples.append(sample)

            # Shuffle columns for better space filling
            random.shuffle(samples)

        elif request.method == "box_behnken":
            # Box-Behnken design (3 levels per factor: -1, 0, +1)
            for var in variables:
                var["levels"] = [var["min"], (var["min"] + var["max"]) / 2, var["max"]]

            # Center point
            center = {var["name"]: var["levels"][1] for var in variables}
            samples.append(center)

            # Edge points (pairs at extremes, others at center)
            for i in range(num_vars):
                for j in range(i + 1, num_vars):
                    for vi in [0, 2]:
                        for vj in [0, 2]:
                            sample = dict(center)
                            sample[variables[i]["name"]] = variables[i]["levels"][vi]
                            sample[variables[j]["name"]] = variables[j]["levels"][vj]
                            samples.append(sample)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown DOE method: {request.method}")

        return {
            "method": request.method,
            "variables": [v["name"] for v in variables],
            "sample_count": len(samples),
            "samples": samples
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate DOE failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/doe/run")
async def run_doe_study(samples: List[Dict[str, float]]):
    """
    Run DOE samples and collect results.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if not samples:
            raise HTTPException(status_code=400, detail="No samples provided")

        # Store original values
        first_sample = samples[0]
        originals = {}
        for dim_name in first_sample.keys():
            dim = doc.Parameter(dim_name)
            if dim:
                originals[dim_name] = dim.SystemValue * 1000

        results = []
        for i, sample in enumerate(samples):
            # Apply values
            for dim_name, value in sample.items():
                dim = doc.Parameter(dim_name)
                if dim:
                    dim.SetSystemValue3(value / 1000.0, 1, None)

            # Rebuild
            doc.EditRebuild3()

            # Collect output
            props = doc.Extension.CreateMassProperty()
            result = {
                "sample_index": i,
                "inputs": sample,
                "outputs": {
                    "mass_kg": round(props.Mass, 4) if props else 0,
                    "volume_m3": round(props.Volume, 9) if props else 0
                }
            }
            results.append(result)

        # Restore originals
        for dim_name, value in originals.items():
            dim = doc.Parameter(dim_name)
            if dim:
                dim.SetSystemValue3(value / 1000.0, 1, None)
        doc.EditRebuild3()

        return {
            "samples_run": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run DOE failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Sensitivity Analysis
# =============================================================================

@router.post("/sensitivity")
async def sensitivity_analysis(dimension_names: List[str], perturbation_percent: float = 5.0):
    """
    Perform sensitivity analysis on specified dimensions.
    Shows how much output changes when input changes by given percentage.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Get baseline
        props = doc.Extension.CreateMassProperty()
        baseline_mass = props.Mass if props else 0

        results = []
        for dim_name in dimension_names:
            dim = doc.Parameter(dim_name)
            if not dim:
                continue

            original = dim.SystemValue
            perturbed = original * (1 + perturbation_percent / 100)

            # Apply perturbation
            dim.SetSystemValue3(perturbed, 1, None)
            doc.EditRebuild3()

            # Measure change
            props = doc.Extension.CreateMassProperty()
            new_mass = props.Mass if props else 0

            mass_change = (new_mass - baseline_mass) / baseline_mass * 100 if baseline_mass else 0
            sensitivity = mass_change / perturbation_percent if perturbation_percent else 0

            results.append({
                "dimension": dim_name,
                "original_mm": round(original * 1000, 3),
                "perturbed_mm": round(perturbed * 1000, 3),
                "mass_change_percent": round(mass_change, 2),
                "sensitivity": round(sensitivity, 3),  # % mass change per % dim change
                "impact": "high" if abs(sensitivity) > 1 else ("medium" if abs(sensitivity) > 0.5 else "low")
            })

            # Restore
            dim.SetSystemValue3(original, 1, None)

        doc.EditRebuild3()

        # Sort by impact
        results.sort(key=lambda x: abs(x["sensitivity"]), reverse=True)

        return {
            "baseline_mass_kg": round(baseline_mass, 4),
            "perturbation_percent": perturbation_percent,
            "dimensions_analyzed": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sensitivity analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
