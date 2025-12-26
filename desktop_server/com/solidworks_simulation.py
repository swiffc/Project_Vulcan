"""
SolidWorks Simulation API
=========================
Interface to SOLIDWORKS Simulation (formerly Cosmos) for:
- FEA Static Analysis
- Frequency Analysis
- Thermal Analysis
- Motion Studies
- Flow Simulation

Phase 26 - Simulation API Integration
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum, IntEnum
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


router = APIRouter(prefix="/solidworks-simulation", tags=["solidworks-simulation"])


# =============================================================================
# Enumerations
# =============================================================================

class StudyType(IntEnum):
    """Simulation study types."""
    STATIC = 0
    FREQUENCY = 1
    BUCKLING = 2
    THERMAL = 3
    DROP_TEST = 4
    FATIGUE = 5
    NONLINEAR = 6
    LINEAR_DYNAMIC = 7
    PRESSURE_VESSEL = 8
    DESIGN_STUDY = 9
    SUBMODELING = 10
    TOPOLOGY = 11
    TWO_D_SIMPLIFICATION = 12


class LoadType(IntEnum):
    """Load types for simulation."""
    FORCE = 0
    PRESSURE = 1
    TORQUE = 2
    GRAVITY = 3
    CENTRIFUGAL = 4
    BEARING_LOAD = 5
    REMOTE_LOAD = 6
    DISTRIBUTED_MASS = 7
    TEMPERATURE = 8
    HEAT_FLUX = 9
    CONVECTION = 10
    RADIATION = 11


class FixtureType(IntEnum):
    """Fixture/constraint types."""
    FIXED = 0
    IMMOVABLE = 1
    ROLLER_SLIDER = 2
    FIXED_HINGE = 3
    SYMMETRY = 4
    CYCLIC_SYMMETRY = 5
    USE_REFERENCE = 6
    ELASTIC_SUPPORT = 7
    FOUNDATION = 8


class MeshQuality(IntEnum):
    """Mesh quality settings."""
    DRAFT = 0
    HIGH = 1
    CURVATURE_BASED = 2


class ResultType(str, Enum):
    """Result plot types."""
    STRESS = "stress"
    DISPLACEMENT = "displacement"
    STRAIN = "strain"
    FACTOR_OF_SAFETY = "fos"
    REACTION_FORCE = "reaction"
    TEMPERATURE = "temperature"
    HEAT_FLUX = "heat_flux"


# =============================================================================
# Request Models
# =============================================================================

class CreateStudyRequest(BaseModel):
    """Request to create a simulation study."""
    name: str = "Static Study"
    study_type: int = 0  # StudyType.STATIC
    mesh_quality: int = 1  # MeshQuality.HIGH
    mesh_size: Optional[float] = None  # Auto if None


class MaterialAssignmentRequest(BaseModel):
    """Request to assign material to bodies."""
    material_name: str = "AISI 1020 Steel, cold rolled"
    apply_to_all: bool = True
    body_names: Optional[List[str]] = None


class FixtureRequest(BaseModel):
    """Request to add fixture/constraint."""
    fixture_type: int = 0  # FixtureType.FIXED
    face_indices: List[int] = []  # Indices of selected faces


class ForceLoadRequest(BaseModel):
    """Request to add force load."""
    magnitude: float  # Force in Newtons
    direction: List[float] = [0, 0, -1]  # Unit vector
    face_indices: List[int] = []
    per_item: bool = False  # True = force per face, False = total force


class PressureLoadRequest(BaseModel):
    """Request to add pressure load."""
    magnitude: float  # Pressure in Pa
    face_indices: List[int] = []
    normal_to_face: bool = True


class GravityLoadRequest(BaseModel):
    """Request to add gravity load."""
    magnitude: float = 9.81  # m/s²
    direction: List[float] = [0, -1, 0]  # Down


class ThermalLoadRequest(BaseModel):
    """Request for thermal analysis."""
    temperature: float  # Kelvin or Celsius
    temperature_unit: str = "C"  # "C" or "K"
    face_indices: List[int] = []


class ConvectionRequest(BaseModel):
    """Request to add convection BC."""
    coefficient: float  # W/(m²·K)
    ambient_temperature: float  # Temperature
    face_indices: List[int] = []


class MeshRequest(BaseModel):
    """Request to control mesh settings."""
    element_size: Optional[float] = None  # Auto if None
    tolerance: Optional[float] = None
    quality: int = 1  # MeshQuality
    curvature_based: bool = False
    min_elements_in_circle: int = 8


class RunAnalysisRequest(BaseModel):
    """Request to run simulation."""
    study_name: Optional[str] = None  # Active study if None


class ResultPlotRequest(BaseModel):
    """Request for result plot."""
    result_type: str = "stress"  # ResultType
    component: Optional[str] = None  # "von_mises", "x", "y", "z", "max_principal"
    deformation_scale: float = 1.0


# =============================================================================
# Global State
# =============================================================================

_sw_app = None
_cosmos = None


def get_app():
    """Get SolidWorks application."""
    global _sw_app
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")

    if _sw_app is None:
        pythoncom.CoInitialize()
        try:
            _sw_app = win32com.client.GetActiveObject("SldWorks.Application")
        except Exception:
            _sw_app = win32com.client.Dispatch("SldWorks.Application")
            _sw_app.Visible = True

    return _sw_app


def get_cosmos():
    """Get SOLIDWORKS Simulation (Cosmos) add-in."""
    global _cosmos
    sw = get_app()

    if _cosmos is None:
        try:
            # Try to get Simulation add-in
            _cosmos = sw.GetAddInObject("SldWorks.Simulation")
            if _cosmos is None:
                _cosmos = sw.GetAddInObject("CosmosWorks.COSMOSWORKS")
        except Exception:
            pass

    return _cosmos


def get_model():
    """Get active model."""
    sw = get_app()
    model = sw.ActiveDoc
    if not model:
        raise HTTPException(status_code=400, detail="No active document")
    return model


# =============================================================================
# Study Management Endpoints
# =============================================================================

@router.get("/status")
async def get_simulation_status() -> Dict[str, Any]:
    """
    Check if SOLIDWORKS Simulation is available.
    """
    try:
        sw = get_app()
        cosmos = get_cosmos()

        available = cosmos is not None

        return {
            "simulation_available": available,
            "addon_name": "SOLIDWORKS Simulation",
            "study_types": [t.name for t in StudyType],
            "message": "Simulation ready" if available else "Install SOLIDWORKS Simulation add-in",
        }

    except Exception as e:
        logger.error(f"Simulation status error: {e}")
        return {"simulation_available": False, "error": str(e)}


@router.post("/study/create")
async def create_study(request: CreateStudyRequest) -> Dict[str, Any]:
    """
    Create a new simulation study.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation add-in not available"}

        model = get_model()

        # Get active document in Cosmos
        doc = cosmos.ActiveDoc()
        if not doc:
            return {"success": False, "error": "Cannot access document in Simulation"}

        # Create study
        study = doc.Study.Add(request.name, request.study_type)

        if study:
            # Set mesh parameters if specified
            if request.mesh_size:
                mesh = study.Mesh
                if mesh:
                    mesh.Quality = request.mesh_quality
                    mesh.ElementSize = request.mesh_size

            return {
                "success": True,
                "study_name": request.name,
                "study_type": StudyType(request.study_type).name,
            }

        return {"success": False, "error": "Failed to create study"}

    except Exception as e:
        logger.error(f"Create study error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/study/list")
async def list_studies() -> Dict[str, Any]:
    """
    List all simulation studies in active document.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        if not doc:
            return {"success": False, "error": "No active document"}

        # Get studies
        study_mgr = doc.Study
        studies = []

        if study_mgr:
            count = study_mgr.StudyCount
            for i in range(count):
                study = study_mgr.Item(i)
                if study:
                    studies.append({
                        "index": i,
                        "name": study.Name,
                        "type": study.AnalysisType,
                        "meshed": study.IsMeshed(),
                        "has_results": study.ResultsAvailable(),
                    })

        return {
            "success": True,
            "count": len(studies),
            "studies": studies,
        }

    except Exception as e:
        logger.error(f"List studies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/study/{study_name}")
async def delete_study(study_name: str) -> Dict[str, Any]:
    """Delete a simulation study."""
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study_mgr = doc.Study

        result = study_mgr.Delete(study_name)

        return {
            "success": result,
            "deleted": study_name if result else None,
        }

    except Exception as e:
        logger.error(f"Delete study error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Material Assignment
# =============================================================================

@router.post("/material/assign")
async def assign_material(request: MaterialAssignmentRequest) -> Dict[str, Any]:
    """
    Assign material to model bodies.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study_mgr = doc.Study
        study = study_mgr.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        # Get solid manager
        solid_mgr = study.SolidManager

        if request.apply_to_all:
            # Apply to all solid bodies
            result = solid_mgr.SetMaterialByName(0, request.material_name)
        else:
            # Apply to specific bodies
            for body_name in (request.body_names or []):
                solid_mgr.SetMaterialByName(body_name, request.material_name)
            result = True

        return {
            "success": result,
            "material": request.material_name,
            "apply_to_all": request.apply_to_all,
        }

    except Exception as e:
        logger.error(f"Assign material error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/material/library")
async def get_material_library() -> Dict[str, Any]:
    """
    Get list of available materials from library.
    """
    try:
        # Common materials in SOLIDWORKS Simulation library
        materials = {
            "steels": [
                "AISI 1020 Steel, cold rolled",
                "AISI 304 Stainless Steel",
                "AISI 316 Stainless Steel",
                "AISI 4340 Steel, normalized",
                "Alloy Steel",
                "Carbon Steel",
            ],
            "aluminum": [
                "6061-T6 Aluminum",
                "7075-T6 Aluminum",
                "2024-T4 Aluminum",
                "Aluminum Alloy",
            ],
            "plastics": [
                "ABS",
                "Nylon 6/10",
                "Polycarbonate",
                "PEEK",
                "PTFE",
            ],
            "other": [
                "Cast Iron",
                "Copper",
                "Titanium Ti-6Al-4V",
                "Concrete",
            ],
        }

        return {
            "success": True,
            "categories": list(materials.keys()),
            "materials": materials,
        }

    except Exception as e:
        logger.error(f"Material library error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Fixtures (Boundary Conditions)
# =============================================================================

@router.post("/fixture/add")
async def add_fixture(request: FixtureRequest) -> Dict[str, Any]:
    """
    Add fixture/constraint to selected faces.
    Select faces in SolidWorks before calling.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        # Get load/restraint manager
        lr_mgr = study.LoadsAndRestraintsManager

        # Add fixture on selected faces
        fixture = lr_mgr.AddRestraint(
            request.fixture_type,  # Type
            None,  # Selected entities (uses current selection)
            None,  # Reference
            0, 0, 0,  # Translation
            0, 0, 0,  # Rotation
            0  # Options
        )

        if fixture:
            return {
                "success": True,
                "fixture_type": FixtureType(request.fixture_type).name,
                "fixture_name": fixture.Name if hasattr(fixture, 'Name') else "Fixture",
            }

        return {"success": False, "error": "Failed to add fixture - ensure faces are selected"}

    except Exception as e:
        logger.error(f"Add fixture error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Loads
# =============================================================================

@router.post("/load/force")
async def add_force_load(request: ForceLoadRequest) -> Dict[str, Any]:
    """
    Add force load to selected faces.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        lr_mgr = study.LoadsAndRestraintsManager

        # Direction components
        dx, dy, dz = request.direction

        load = lr_mgr.AddForce(
            0,  # Type (0 = force)
            None,  # Selection (uses current)
            None,  # Reference
            request.magnitude,  # Value
            dx, dy, dz,  # Direction
            request.per_item,  # Per item
            0  # Options
        )

        if load:
            return {
                "success": True,
                "load_type": "Force",
                "magnitude_N": request.magnitude,
                "direction": request.direction,
            }

        return {"success": False, "error": "Failed to add force"}

    except Exception as e:
        logger.error(f"Add force error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load/pressure")
async def add_pressure_load(request: PressureLoadRequest) -> Dict[str, Any]:
    """
    Add pressure load to selected faces.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        lr_mgr = study.LoadsAndRestraintsManager

        load = lr_mgr.AddPressure(
            0,  # Type
            None,  # Selection
            request.magnitude,  # Value (Pa)
            request.normal_to_face,  # Normal direction
            0  # Options
        )

        if load:
            return {
                "success": True,
                "load_type": "Pressure",
                "magnitude_Pa": request.magnitude,
            }

        return {"success": False, "error": "Failed to add pressure"}

    except Exception as e:
        logger.error(f"Add pressure error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load/gravity")
async def add_gravity(request: GravityLoadRequest) -> Dict[str, Any]:
    """
    Add gravity load to study.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        lr_mgr = study.LoadsAndRestraintsManager

        dx, dy, dz = request.direction

        load = lr_mgr.AddGravity(
            request.magnitude,
            dx, dy, dz,
            0  # Options
        )

        if load:
            return {
                "success": True,
                "load_type": "Gravity",
                "magnitude_m_s2": request.magnitude,
                "direction": request.direction,
            }

        return {"success": False, "error": "Failed to add gravity"}

    except Exception as e:
        logger.error(f"Add gravity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Mesh
# =============================================================================

@router.post("/mesh/create")
async def create_mesh(request: MeshRequest) -> Dict[str, Any]:
    """
    Create mesh for active study.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        mesh = study.Mesh

        if mesh:
            # Set mesh parameters
            mesh.Quality = request.quality

            if request.element_size:
                mesh.ElementSize = request.element_size

            if request.tolerance:
                mesh.Tolerance = request.tolerance

            if request.curvature_based:
                mesh.MeshType = 2  # Curvature-based

            # Create mesh
            result = mesh.Create()

            if result == 0:  # Success
                return {
                    "success": True,
                    "quality": MeshQuality(request.quality).name,
                    "element_count": mesh.ElementCount if hasattr(mesh, 'ElementCount') else "Unknown",
                    "node_count": mesh.NodeCount if hasattr(mesh, 'NodeCount') else "Unknown",
                }

        return {"success": False, "error": "Failed to create mesh"}

    except Exception as e:
        logger.error(f"Create mesh error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mesh/info")
async def get_mesh_info() -> Dict[str, Any]:
    """
    Get mesh information for active study.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        mesh = study.Mesh

        if mesh and study.IsMeshed():
            return {
                "success": True,
                "is_meshed": True,
                "element_count": mesh.ElementCount if hasattr(mesh, 'ElementCount') else 0,
                "node_count": mesh.NodeCount if hasattr(mesh, 'NodeCount') else 0,
                "element_size": mesh.ElementSize if hasattr(mesh, 'ElementSize') else 0,
                "quality": mesh.Quality if hasattr(mesh, 'Quality') else 0,
            }

        return {"success": True, "is_meshed": False}

    except Exception as e:
        logger.error(f"Mesh info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Run Analysis
# =============================================================================

@router.post("/run")
async def run_analysis(request: RunAnalysisRequest) -> Dict[str, Any]:
    """
    Run the simulation analysis.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()

        if request.study_name:
            study = doc.Study.Item(request.study_name)
        else:
            study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No study found"}

        # Check if meshed
        if not study.IsMeshed():
            return {"success": False, "error": "Study not meshed - create mesh first"}

        # Run analysis
        result = study.RunAnalysis()

        if result == 0:  # Success
            return {
                "success": True,
                "study_name": study.Name,
                "message": "Analysis completed successfully",
            }

        error_messages = {
            1: "Analysis failed",
            2: "Analysis cancelled by user",
            3: "Model not meshed",
            4: "Insufficient boundary conditions",
        }

        return {
            "success": False,
            "error_code": result,
            "error": error_messages.get(result, f"Unknown error: {result}"),
        }

    except Exception as e:
        logger.error(f"Run analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Results
# =============================================================================

@router.get("/results/summary")
async def get_results_summary() -> Dict[str, Any]:
    """
    Get summary of analysis results.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study:
            return {"success": False, "error": "No active study"}

        if not study.ResultsAvailable():
            return {"success": False, "error": "No results available - run analysis first"}

        # Get results
        results = study.Results

        summary = {
            "success": True,
            "study_name": study.Name,
            "stress": {},
            "displacement": {},
            "strain": {},
        }

        # Try to get result values
        try:
            # Von Mises stress
            summary["stress"]["max_von_mises_Pa"] = results.GetMinMaxStress(0, 0)[1]  # Max
            summary["stress"]["min_von_mises_Pa"] = results.GetMinMaxStress(0, 0)[0]  # Min
        except Exception:
            pass

        try:
            # Displacement
            summary["displacement"]["max_resultant_m"] = results.GetMinMaxDisplacement(0)[1]
        except Exception:
            pass

        try:
            # Factor of safety
            summary["factor_of_safety"] = {
                "minimum": results.GetMinFOS() if hasattr(results, 'GetMinFOS') else None,
            }
        except Exception:
            pass

        return summary

    except Exception as e:
        logger.error(f"Results summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/results/plot")
async def create_result_plot(request: ResultPlotRequest) -> Dict[str, Any]:
    """
    Create a result plot (stress, displacement, etc.).
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study or not study.ResultsAvailable():
            return {"success": False, "error": "No results available"}

        results = study.Results

        # Map result type to plot type
        plot_type_map = {
            "stress": 0,
            "displacement": 1,
            "strain": 2,
            "fos": 3,
            "reaction": 4,
        }

        plot_type = plot_type_map.get(request.result_type.lower(), 0)

        # Create plot
        plot = results.CreatePlot(plot_type, None)

        if plot:
            # Set deformation scale
            if request.deformation_scale != 1.0:
                plot.DeformationScale = request.deformation_scale

            return {
                "success": True,
                "plot_type": request.result_type,
                "deformation_scale": request.deformation_scale,
            }

        return {"success": False, "error": "Failed to create plot"}

    except Exception as e:
        logger.error(f"Create plot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/probe")
async def probe_result(x: float, y: float, z: float, result_type: str = "stress") -> Dict[str, Any]:
    """
    Probe result value at a specific location.
    """
    try:
        cosmos = get_cosmos()
        if not cosmos:
            return {"success": False, "error": "Simulation not available"}

        doc = cosmos.ActiveDoc()
        study = doc.Study.ActiveStudy

        if not study or not study.ResultsAvailable():
            return {"success": False, "error": "No results available"}

        results = study.Results

        # Probe at location
        value = results.ProbeResultAtLocation(x, y, z, 0)  # 0 = stress

        return {
            "success": True,
            "location": {"x": x, "y": y, "z": z},
            "result_type": result_type,
            "value": value,
        }

    except Exception as e:
        logger.error(f"Probe result error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Export
# =============================================================================

SIMULATION_AVAILABLE = COM_AVAILABLE

__all__ = [
    "router",
    "SIMULATION_AVAILABLE",
    "StudyType",
    "LoadType",
    "FixtureType",
    "MeshQuality",
    "ResultType",
]
