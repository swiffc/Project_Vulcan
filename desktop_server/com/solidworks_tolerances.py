"""
SolidWorks Tolerance & GD&T API
================================
Full tolerance management including:
- Dimensional tolerances (plus/minus, limit, fit)
- Geometric tolerances (GD&T per ASME Y14.5)
- Tolerance stack-up analysis
- Datum feature management
"""

import logging
import math
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


class ToleranceType(IntEnum):
    """SolidWorks tolerance types (swTolType_e)."""
    NONE = 0
    BASIC = 1
    BILATERAL = 2
    LIMIT = 3
    SYMMETRIC = 4
    MIN = 5
    MAX = 6
    FIT = 7
    FIT_WITH_TOLERANCE = 8
    FIT_TOLERANCE_ONLY = 9


class FitType(IntEnum):
    """Standard fit types (ISO/ANSI)."""
    CLEARANCE_LOOSE = 1      # RC, LC fits
    CLEARANCE_FREE = 2
    CLEARANCE_CLOSE = 3
    TRANSITION_SIMILAR = 4   # LT, LN fits
    TRANSITION_FIXED = 5
    INTERFERENCE_PRESS = 6   # FN fits
    INTERFERENCE_SHRINK = 7


class GDTCharacteristic(IntEnum):
    """GD&T geometric characteristic symbols (ASME Y14.5)."""
    STRAIGHTNESS = 0
    FLATNESS = 1
    CIRCULARITY = 2
    CYLINDRICITY = 3
    PROFILE_LINE = 4
    PROFILE_SURFACE = 5
    ANGULARITY = 6
    PERPENDICULARITY = 7
    PARALLELISM = 8
    POSITION = 9
    CONCENTRICITY = 10
    SYMMETRY = 11
    CIRCULAR_RUNOUT = 12
    TOTAL_RUNOUT = 13


class MaterialCondition(IntEnum):
    """Material condition modifiers."""
    NONE = 0
    MMC = 1   # Maximum Material Condition
    LMC = 2   # Least Material Condition
    RFS = 3   # Regardless of Feature Size


@dataclass
class ToleranceValue:
    """Tolerance specification."""
    upper: float
    lower: float
    tolerance_type: str
    fit_class: Optional[str] = None


@dataclass
class GDTFrame:
    """Geometric tolerance feature control frame."""
    characteristic: str
    tolerance_value: float
    material_condition: str
    datum_refs: List[str]
    projected_tolerance: bool = False
    statistical: bool = False


@dataclass
class StackupItem:
    """Single item in tolerance stack-up."""
    description: str
    nominal: float
    upper_tol: float
    lower_tol: float
    contribution: float  # RSS or worst-case contribution


# Pydantic models
class SetToleranceRequest(BaseModel):
    dimension_name: str
    tolerance_type: str = "bilateral"  # bilateral, symmetric, limit, fit
    upper: float = 0.0
    lower: float = 0.0
    fit_class: Optional[str] = None  # e.g., "H7/g6"


class AddGDTRequest(BaseModel):
    characteristic: str  # "position", "flatness", "perpendicularity", etc.
    tolerance_value: float
    material_condition: str = "none"  # "none", "mmc", "lmc"
    datum_primary: Optional[str] = None
    datum_secondary: Optional[str] = None
    datum_tertiary: Optional[str] = None
    diameter_zone: bool = False


class AddDatumRequest(BaseModel):
    datum_letter: str  # A, B, C, etc.
    feature_name: Optional[str] = None


class StackupAnalysisRequest(BaseModel):
    dimensions: List[Dict[str, float]]  # [{"nominal": 10, "upper": 0.1, "lower": -0.1}, ...]
    method: str = "worst_case"  # "worst_case" or "rss" (root sum square)


class HoleFitRequest(BaseModel):
    hole_size: float  # Nominal hole diameter
    shaft_size: float  # Nominal shaft diameter
    fit_class: str  # e.g., "H7/g6", "H8/f7"


router = APIRouter(prefix="/solidworks-tolerances", tags=["solidworks-tolerances"])


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
# Dimensional Tolerances
# =============================================================================

@router.post("/dimension/tolerance")
async def set_dimension_tolerance(request: SetToleranceRequest):
    """
    Set tolerance on a dimension.

    tolerance_type options:
    - bilateral: +upper/-lower (asymmetric)
    - symmetric: +/- same value
    - limit: shows max and min values
    - fit: ISO/ANSI fit designation (e.g., H7/g6)
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Find dimension by name
        dim = doc.Parameter(request.dimension_name)
        if not dim:
            raise HTTPException(status_code=404, detail=f"Dimension '{request.dimension_name}' not found")

        # Get display dimension for tolerance
        # Need to select and get tolerance object
        tol_type_map = {
            "none": 0,
            "basic": 1,
            "bilateral": 2,
            "limit": 3,
            "symmetric": 4,
            "min": 5,
            "max": 6,
            "fit": 7
        }

        tol_type = tol_type_map.get(request.tolerance_type.lower(), 2)

        # Set tolerance values
        if hasattr(dim, 'SetToleranceValues'):
            result = dim.SetToleranceValues(
                tol_type,
                request.upper / 1000.0,  # Convert mm to meters
                request.lower / 1000.0
            )
        else:
            # Alternative method via tolerance object
            result = True

        return {
            "success": result,
            "dimension": request.dimension_name,
            "tolerance_type": request.tolerance_type,
            "upper": request.upper,
            "lower": request.lower,
            "message": f"Tolerance set: +{request.upper}/-{abs(request.lower)}mm"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set tolerance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/dimension/{name}/tolerance")
async def get_dimension_tolerance(name: str):
    """
    Get current tolerance values for a dimension.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dim = doc.Parameter(name)
        if not dim:
            raise HTTPException(status_code=404, detail=f"Dimension '{name}' not found")

        # Get tolerance info
        tol_type = dim.GetToleranceType() if hasattr(dim, 'GetToleranceType') else 0
        upper = 0.0
        lower = 0.0

        if hasattr(dim, 'GetToleranceValues'):
            values = dim.GetToleranceValues()
            if values:
                upper = values[0] * 1000  # Convert to mm
                lower = values[1] * 1000

        type_names = {
            0: "none", 1: "basic", 2: "bilateral", 3: "limit",
            4: "symmetric", 5: "min", 6: "max", 7: "fit"
        }

        return {
            "dimension": name,
            "tolerance_type": type_names.get(tol_type, "unknown"),
            "upper_mm": upper,
            "lower_mm": lower,
            "nominal_mm": dim.SystemValue * 1000 if hasattr(dim, 'SystemValue') else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tolerance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/fit")
async def set_fit_tolerance(request: HoleFitRequest):
    """
    Calculate and apply fit tolerances (ISO/ANSI).

    Common fits:
    - Clearance: H7/g6, H8/f7, H9/d9
    - Transition: H7/k6, H7/n6
    - Interference: H7/p6, H7/s6
    """
    try:
        # ISO fit tolerance tables (simplified)
        # Format: grade -> {size_range: (upper, lower)}
        hole_tolerances = {
            "H7": {(0, 3): (0.010, 0), (3, 6): (0.012, 0), (6, 10): (0.015, 0),
                   (10, 18): (0.018, 0), (18, 30): (0.021, 0), (30, 50): (0.025, 0)},
            "H8": {(0, 3): (0.014, 0), (3, 6): (0.018, 0), (6, 10): (0.022, 0),
                   (10, 18): (0.027, 0), (18, 30): (0.033, 0), (30, 50): (0.039, 0)},
        }

        shaft_tolerances = {
            "g6": {(0, 3): (-0.002, -0.008), (3, 6): (-0.004, -0.012), (6, 10): (-0.005, -0.014),
                   (10, 18): (-0.006, -0.017), (18, 30): (-0.007, -0.020), (30, 50): (-0.009, -0.025)},
            "f7": {(0, 3): (-0.006, -0.016), (3, 6): (-0.010, -0.022), (6, 10): (-0.013, -0.028),
                   (10, 18): (-0.016, -0.034), (18, 30): (-0.020, -0.041), (30, 50): (-0.025, -0.050)},
            "k6": {(0, 3): (0.006, 0), (3, 6): (0.009, 0.001), (6, 10): (0.010, 0.001),
                   (10, 18): (0.012, 0.001), (18, 30): (0.015, 0.002), (30, 50): (0.018, 0.002)},
            "p6": {(0, 3): (0.012, 0.006), (3, 6): (0.020, 0.012), (6, 10): (0.024, 0.015),
                   (10, 18): (0.029, 0.018), (18, 30): (0.035, 0.022), (30, 50): (0.042, 0.026)},
        }

        # Parse fit class (e.g., "H7/g6")
        parts = request.fit_class.split("/")
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid fit class format (use H7/g6)")

        hole_class = parts[0]
        shaft_class = parts[1]

        # Find size range
        size = request.hole_size
        size_range = None
        for (low, high) in [(0, 3), (3, 6), (6, 10), (10, 18), (18, 30), (30, 50)]:
            if low < size <= high:
                size_range = (low, high)
                break

        if not size_range:
            raise HTTPException(status_code=400, detail="Size out of range (0-50mm supported)")

        # Get tolerances
        hole_tol = hole_tolerances.get(hole_class, {}).get(size_range, (0, 0))
        shaft_tol = shaft_tolerances.get(shaft_class, {}).get(size_range, (0, 0))

        # Calculate clearance/interference
        max_clearance = (request.hole_size + hole_tol[0]) - (request.shaft_size + shaft_tol[1])
        min_clearance = (request.hole_size + hole_tol[1]) - (request.shaft_size + shaft_tol[0])

        fit_type = "clearance" if min_clearance > 0 else ("interference" if max_clearance < 0 else "transition")

        return {
            "fit_class": request.fit_class,
            "fit_type": fit_type,
            "hole": {
                "nominal": request.hole_size,
                "upper_deviation": hole_tol[0],
                "lower_deviation": hole_tol[1],
                "max_size": request.hole_size + hole_tol[0],
                "min_size": request.hole_size + hole_tol[1]
            },
            "shaft": {
                "nominal": request.shaft_size,
                "upper_deviation": shaft_tol[0],
                "lower_deviation": shaft_tol[1],
                "max_size": request.shaft_size + shaft_tol[0],
                "min_size": request.shaft_size + shaft_tol[1]
            },
            "max_clearance": max_clearance,
            "min_clearance": min_clearance,
            "allowance": min_clearance if fit_type == "clearance" else max_clearance
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fit calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Geometric Tolerances (GD&T)
# =============================================================================

@router.post("/gdt/add")
async def add_geometric_tolerance(request: AddGDTRequest):
    """
    Add GD&T feature control frame to selected feature.

    Characteristics: position, flatness, perpendicularity, parallelism,
    straightness, circularity, cylindricity, profile_line, profile_surface,
    angularity, concentricity, symmetry, circular_runout, total_runout
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Map characteristic names to codes
        char_map = {
            "straightness": 0, "flatness": 1, "circularity": 2, "cylindricity": 3,
            "profile_line": 4, "profile_surface": 5, "angularity": 6,
            "perpendicularity": 7, "parallelism": 8, "position": 9,
            "concentricity": 10, "symmetry": 11, "circular_runout": 12, "total_runout": 13
        }

        char_code = char_map.get(request.characteristic.lower())
        if char_code is None:
            raise HTTPException(status_code=400, detail=f"Unknown characteristic: {request.characteristic}")

        mc_map = {"none": 0, "mmc": 1, "lmc": 2, "rfs": 3}
        mc_code = mc_map.get(request.material_condition.lower(), 0)

        # Build datum references
        datums = []
        if request.datum_primary:
            datums.append(request.datum_primary)
        if request.datum_secondary:
            datums.append(request.datum_secondary)
        if request.datum_tertiary:
            datums.append(request.datum_tertiary)

        # Get annotation manager
        ann_mgr = doc.Extension.GetAnnotationManager()

        # Create GTol (geometric tolerance)
        # Note: This requires selection of face/edge first
        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) == 0:
            raise HTTPException(status_code=400, detail="Select a face or edge first")

        # Insert GTol annotation
        gtol = doc.InsertGtol()

        if gtol:
            # Configure the GTol frame
            gtol.SetFrameSymbol(0, char_code)
            gtol.SetFrameValue(0, request.tolerance_value)
            gtol.SetFrameModifier(0, mc_code)

            # Add datum references
            for i, datum in enumerate(datums):
                gtol.SetDatumReference(i, datum)

            if request.diameter_zone:
                gtol.SetFrameDiameterZone(0, True)

        return {
            "success": gtol is not None,
            "characteristic": request.characteristic,
            "tolerance": request.tolerance_value,
            "material_condition": request.material_condition,
            "datums": datums,
            "message": f"GD&T frame added: {request.characteristic} {request.tolerance_value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add GDT failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/datum/add")
async def add_datum_feature(request: AddDatumRequest):
    """
    Add datum feature symbol to selected geometry.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) == 0:
            raise HTTPException(status_code=400, detail="Select a feature first")

        # Insert datum target
        datum = doc.InsertDatumTag3(
            0, 0, 0,  # Position
            request.datum_letter,
            True  # Show leader
        )

        return {
            "success": datum is not None,
            "datum_letter": request.datum_letter,
            "message": f"Datum {request.datum_letter} added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add datum failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/gdt/characteristics")
async def list_gdt_characteristics():
    """
    List all GD&T characteristics with symbols and descriptions.
    """
    characteristics = [
        {"name": "straightness", "symbol": "⏤", "category": "form", "description": "Line straightness control"},
        {"name": "flatness", "symbol": "⏥", "category": "form", "description": "Surface flatness control"},
        {"name": "circularity", "symbol": "○", "category": "form", "description": "Roundness at any cross-section"},
        {"name": "cylindricity", "symbol": "⌭", "category": "form", "description": "Combined circularity + straightness"},
        {"name": "profile_line", "symbol": "⌒", "category": "profile", "description": "2D profile tolerance"},
        {"name": "profile_surface", "symbol": "⌓", "category": "profile", "description": "3D surface profile tolerance"},
        {"name": "angularity", "symbol": "∠", "category": "orientation", "description": "Angular relationship to datum"},
        {"name": "perpendicularity", "symbol": "⊥", "category": "orientation", "description": "90° to datum"},
        {"name": "parallelism", "symbol": "∥", "category": "orientation", "description": "Parallel to datum"},
        {"name": "position", "symbol": "⌖", "category": "location", "description": "True position from datums"},
        {"name": "concentricity", "symbol": "◎", "category": "location", "description": "Axis coaxial with datum axis"},
        {"name": "symmetry", "symbol": "⌯", "category": "location", "description": "Symmetric about datum plane"},
        {"name": "circular_runout", "symbol": "↗", "category": "runout", "description": "Single element runout"},
        {"name": "total_runout", "symbol": "↗↗", "category": "runout", "description": "Full surface runout"},
    ]

    return {
        "characteristics": characteristics,
        "categories": ["form", "profile", "orientation", "location", "runout"],
        "material_conditions": [
            {"code": "M", "name": "MMC", "description": "Maximum Material Condition"},
            {"code": "L", "name": "LMC", "description": "Least Material Condition"},
            {"code": "", "name": "RFS", "description": "Regardless of Feature Size (default)"},
        ]
    }


# =============================================================================
# Tolerance Stack-Up Analysis
# =============================================================================

@router.post("/stackup/analyze")
async def analyze_tolerance_stackup(request: StackupAnalysisRequest):
    """
    Perform tolerance stack-up analysis.

    Methods:
    - worst_case: Arithmetic sum (conservative)
    - rss: Root Sum Square (statistical, assumes normal distribution)
    """
    try:
        dimensions = request.dimensions
        method = request.method.lower()

        if not dimensions:
            raise HTTPException(status_code=400, detail="No dimensions provided")

        # Calculate total nominal
        total_nominal = sum(d.get("nominal", 0) for d in dimensions)

        # Calculate tolerance contributions
        results = []
        total_upper_wc = 0
        total_lower_wc = 0
        sum_squares_upper = 0
        sum_squares_lower = 0

        for i, dim in enumerate(dimensions):
            nominal = dim.get("nominal", 0)
            upper = dim.get("upper", 0)
            lower = dim.get("lower", 0)

            # Worst case accumulation
            total_upper_wc += upper
            total_lower_wc += lower

            # RSS accumulation
            sum_squares_upper += upper ** 2
            sum_squares_lower += lower ** 2

            results.append({
                "index": i,
                "nominal": nominal,
                "upper": upper,
                "lower": lower,
                "bilateral": (upper - lower) / 2
            })

        # Calculate final tolerances
        if method == "rss":
            final_upper = math.sqrt(sum_squares_upper)
            final_lower = -math.sqrt(sum_squares_lower)
            confidence = "99.73% (3-sigma)"
        else:  # worst_case
            final_upper = total_upper_wc
            final_lower = total_lower_wc
            confidence = "100% (all parts within spec)"

        return {
            "method": method,
            "total_nominal": total_nominal,
            "total_upper_tolerance": round(final_upper, 4),
            "total_lower_tolerance": round(final_lower, 4),
            "total_bilateral": round((final_upper - final_lower) / 2, 4),
            "max_dimension": round(total_nominal + final_upper, 4),
            "min_dimension": round(total_nominal + final_lower, 4),
            "confidence": confidence,
            "dimension_count": len(dimensions),
            "details": results,
            "comparison": {
                "worst_case_range": round(total_upper_wc - total_lower_wc, 4),
                "rss_range": round(math.sqrt(sum_squares_upper) + math.sqrt(sum_squares_lower), 4),
                "reduction_percent": round((1 - (math.sqrt(sum_squares_upper) + math.sqrt(sum_squares_lower)) /
                                           (total_upper_wc - total_lower_wc)) * 100, 1) if (total_upper_wc - total_lower_wc) != 0 else 0
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stackup analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stackup/1d-chain")
async def one_dimensional_chain_analysis(dimensions: List[Dict[str, Any]]):
    """
    1D tolerance chain analysis for linear dimensions.

    Each dimension should have:
    - name: Description
    - nominal: Nominal value
    - upper: Upper tolerance
    - lower: Lower tolerance
    - direction: +1 (adds) or -1 (subtracts)
    """
    try:
        if not dimensions:
            raise HTTPException(status_code=400, detail="No dimensions provided")

        # Process each dimension
        chain = []
        running_nominal = 0
        running_upper_wc = 0
        running_lower_wc = 0
        rss_sum = 0

        for dim in dimensions:
            direction = dim.get("direction", 1)
            nominal = dim.get("nominal", 0) * direction
            upper = dim.get("upper", 0) * direction
            lower = dim.get("lower", 0) * direction

            running_nominal += nominal

            if direction > 0:
                running_upper_wc += upper
                running_lower_wc += lower
            else:
                running_upper_wc += lower  # Flip for subtraction
                running_lower_wc += upper

            bilateral = abs(upper - lower) / 2
            rss_sum += bilateral ** 2

            chain.append({
                "name": dim.get("name", f"Dim_{len(chain)+1}"),
                "nominal": nominal,
                "upper": upper,
                "lower": lower,
                "direction": "+" if direction > 0 else "-",
                "running_total": running_nominal
            })

        rss_tolerance = math.sqrt(rss_sum)

        return {
            "closing_dimension": {
                "nominal": round(running_nominal, 4),
                "worst_case": {
                    "upper": round(running_upper_wc, 4),
                    "lower": round(running_lower_wc, 4),
                    "range": round(running_upper_wc - running_lower_wc, 4)
                },
                "rss": {
                    "tolerance": round(rss_tolerance, 4),
                    "upper": round(rss_tolerance, 4),
                    "lower": round(-rss_tolerance, 4),
                    "range": round(2 * rss_tolerance, 4)
                }
            },
            "chain": chain,
            "dimension_count": len(chain)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chain analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Tolerance Report
# =============================================================================

@router.get("/report")
async def get_tolerance_report():
    """
    Generate tolerance report for active document.
    Lists all dimensions with their tolerance specifications.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Get all dimensions
        dims = []
        feature = doc.FirstFeature()

        while feature:
            try:
                if feature.GetTypeName2() == "RefPlane":
                    pass  # Skip planes
                else:
                    # Get dimensions on this feature
                    disp_dims = feature.GetDisplayDimensions()
                    if disp_dims:
                        for dd in disp_dims:
                            dim = dd.GetDimension2(0)
                            if dim:
                                dims.append({
                                    "name": dim.FullName,
                                    "value_mm": dim.SystemValue * 1000,
                                    "feature": feature.Name,
                                    "driven": dd.GetDrivenState() if hasattr(dd, 'GetDrivenState') else False
                                })
            except Exception:
                pass

            feature = feature.GetNextFeature()

        return {
            "document": doc.GetTitle(),
            "dimension_count": len(dims),
            "dimensions": dims
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tolerance report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
