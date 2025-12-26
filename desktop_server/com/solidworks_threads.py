"""
SolidWorks Cosmetic Thread & Helix API
======================================
Thread representation and helix features including:
- Cosmetic threads (visual representation)
- Helix/spiral features
- Thread callouts and standards
- Tap/die hole specifications
"""

import logging
from typing import Optional, Dict, Any, List
from enum import IntEnum
from dataclasses import dataclass
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


class ThreadStandard(IntEnum):
    """Thread standards."""
    ANSI_INCH = 0
    ANSI_METRIC = 1
    ISO = 2
    BSP = 3  # British Standard Pipe
    NPT = 4  # National Pipe Thread
    ACME = 5
    CUSTOM = 99


class ThreadType(IntEnum):
    """Thread types."""
    EXTERNAL = 0  # Male thread (bolt)
    INTERNAL = 1  # Female thread (nut/hole)


class HelixType(IntEnum):
    """Helix definition types."""
    HEIGHT_PITCH = 0
    HEIGHT_REVOLUTIONS = 1
    PITCH_REVOLUTIONS = 2
    SPIRAL = 3


@dataclass
class ThreadSpec:
    """Thread specification data."""
    standard: str
    designation: str
    major_diameter: float
    minor_diameter: float
    pitch: float  # or TPI for inch
    thread_class: str  # 2A, 2B, 6g, 6H, etc.
    thread_type: str  # internal/external


# Common thread database
METRIC_THREADS = {
    "M3": {"major": 3.0, "pitch": 0.5, "minor_ext": 2.39, "minor_int": 2.459},
    "M4": {"major": 4.0, "pitch": 0.7, "minor_ext": 3.14, "minor_int": 3.242},
    "M5": {"major": 5.0, "pitch": 0.8, "minor_ext": 4.02, "minor_int": 4.134},
    "M6": {"major": 6.0, "pitch": 1.0, "minor_ext": 4.77, "minor_int": 4.917},
    "M8": {"major": 8.0, "pitch": 1.25, "minor_ext": 6.47, "minor_int": 6.647},
    "M10": {"major": 10.0, "pitch": 1.5, "minor_ext": 8.16, "minor_int": 8.376},
    "M12": {"major": 12.0, "pitch": 1.75, "minor_ext": 9.85, "minor_int": 10.106},
    "M16": {"major": 16.0, "pitch": 2.0, "minor_ext": 13.55, "minor_int": 13.835},
    "M20": {"major": 20.0, "pitch": 2.5, "minor_ext": 16.93, "minor_int": 17.294},
    "M24": {"major": 24.0, "pitch": 3.0, "minor_ext": 20.32, "minor_int": 20.752},
}

INCH_THREADS = {
    "#4-40": {"major": 2.845, "tpi": 40, "minor_ext": 2.157, "minor_int": 2.261},
    "#6-32": {"major": 3.505, "tpi": 32, "minor_ext": 2.642, "minor_int": 2.771},
    "#8-32": {"major": 4.166, "tpi": 32, "minor_ext": 3.302, "minor_int": 3.432},
    "#10-24": {"major": 4.826, "tpi": 24, "minor_ext": 3.683, "minor_int": 3.861},
    "1/4-20": {"major": 6.350, "tpi": 20, "minor_ext": 4.976, "minor_int": 5.190},
    "5/16-18": {"major": 7.938, "tpi": 18, "minor_ext": 6.401, "minor_int": 6.629},
    "3/8-16": {"major": 9.525, "tpi": 16, "minor_ext": 7.798, "minor_int": 8.051},
    "1/2-13": {"major": 12.700, "tpi": 13, "minor_ext": 10.592, "minor_int": 10.881},
    "5/8-11": {"major": 15.875, "tpi": 11, "minor_ext": 13.386, "minor_int": 13.716},
    "3/4-10": {"major": 19.050, "tpi": 10, "minor_ext": 16.307, "minor_int": 16.662},
}


# Pydantic models
class CosmeticThreadRequest(BaseModel):
    edge_name: Optional[str] = None  # Circular edge to thread
    thread_designation: str  # e.g., "M10x1.5", "1/4-20"
    thread_type: str = "internal"  # internal/external
    depth: Optional[float] = None  # Thread depth in mm (None = full depth)
    thread_class: str = "6H"  # 6H, 6g, 2A, 2B, etc.


class HelixRequest(BaseModel):
    definition_type: str = "height_pitch"  # height_pitch, height_revolutions, pitch_revolutions
    height: float = 20.0  # Total height in mm
    pitch: float = 2.0  # Pitch in mm
    revolutions: float = 10.0  # Number of revolutions
    start_angle: float = 0.0  # Start angle in degrees
    clockwise: bool = True
    taper_angle: float = 0.0  # Taper angle in degrees (0 = cylindrical)
    variable_pitch: bool = False


class SpiralRequest(BaseModel):
    start_radius: float  # Starting radius in mm
    end_radius: float  # Ending radius in mm
    revolutions: float  # Number of turns
    height: float = 0.0  # Height (0 = flat spiral)
    clockwise: bool = True


class ThreadCalloutRequest(BaseModel):
    thread_designation: str
    depth: Optional[float] = None
    include_class: bool = True
    include_depth: bool = True


router = APIRouter(prefix="/solidworks-threads", tags=["solidworks-threads"])


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
# Cosmetic Threads
# =============================================================================

@router.post("/cosmetic/add")
async def add_cosmetic_thread(request: CosmeticThreadRequest):
    """
    Add cosmetic thread to a circular edge or face.

    This creates a visual thread representation without modeling actual helical geometry.
    Used for internal threads in holes and external threads on shafts.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Parse thread designation
        thread_data = None
        if request.thread_designation.startswith("M"):
            # Metric thread
            base = request.thread_designation.split("x")[0]
            thread_data = METRIC_THREADS.get(base)
            if thread_data:
                thread_data["standard"] = "ISO"
        else:
            # Inch thread
            thread_data = INCH_THREADS.get(request.thread_designation)
            if thread_data:
                thread_data["standard"] = "ANSI"

        if not thread_data:
            raise HTTPException(status_code=400, detail=f"Unknown thread: {request.thread_designation}")

        # Select edge if specified
        if request.edge_name:
            doc.Extension.SelectByID2(
                request.edge_name, "EDGE", 0, 0, 0, False, 0, None, 0
            )

        # Verify selection is circular edge
        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) == 0:
            raise HTTPException(status_code=400, detail="Select a circular edge first")

        fm = doc.FeatureManager

        # Determine diameters based on thread type
        if request.thread_type.lower() == "internal":
            # Internal thread: major = tap drill, minor = thread major
            major_dia = thread_data["major"] / 1000.0
            minor_dia = thread_data.get("minor_int", thread_data["major"] * 0.85) / 1000.0
        else:
            # External thread: major = thread major, minor = thread minor
            major_dia = thread_data["major"] / 1000.0
            minor_dia = thread_data.get("minor_ext", thread_data["major"] * 0.85) / 1000.0

        # Calculate depth
        depth = (request.depth / 1000.0) if request.depth else 0.02  # Default 20mm

        # Insert cosmetic thread
        # Parameters: blind_type, diameter, depth, diameter_type
        thread = fm.InsertCosmeticThread4(
            0,  # Blind type (0 = blind, 1 = through)
            minor_dia,  # Minor diameter
            depth,
            1,  # Diameter type
            major_dia,  # Major diameter
            request.thread_designation,  # Callout
            True  # Show in drawing
        )

        return {
            "success": thread is not None,
            "thread_designation": request.thread_designation,
            "thread_type": request.thread_type,
            "major_diameter_mm": thread_data["major"],
            "minor_diameter_mm": minor_dia * 1000,
            "pitch_mm": thread_data.get("pitch", 25.4 / thread_data.get("tpi", 20)),
            "depth_mm": depth * 1000,
            "standard": thread_data["standard"],
            "message": f"Cosmetic thread {request.thread_designation} added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add cosmetic thread failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/cosmetic/list")
async def list_cosmetic_threads():
    """
    List all cosmetic threads in active document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        threads = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "CosmeticThread":
                try:
                    ct_data = feature.GetDefinition()
                    threads.append({
                        "name": feature.Name,
                        "suppressed": feature.IsSuppressed2(1)[0],
                        # "callout": ct_data.GetCallout() if ct_data else None
                    })
                except Exception:
                    threads.append({"name": feature.Name})

            feature = feature.GetNextFeature()

        return {
            "count": len(threads),
            "threads": threads
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List threads failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/cosmetic/{thread_name}")
async def delete_cosmetic_thread(thread_name: str):
    """
    Delete a cosmetic thread by name.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.Extension.SelectByID2(thread_name, "COSMETIC_THREAD", 0, 0, 0, False, 0, None, 0)
        result = doc.EditDelete()

        return {
            "success": result,
            "deleted": thread_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete thread failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Helix Features
# =============================================================================

@router.post("/helix/create")
async def create_helix(request: HelixRequest):
    """
    Create a helix/spiral curve.

    Used as a path for sweep features (like actual threads, springs, coils).

    definition_type options:
    - height_pitch: Define by total height and pitch
    - height_revolutions: Define by height and number of turns
    - pitch_revolutions: Define by pitch and number of turns
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Need to select a circular sketch or edge first
        sel_mgr = doc.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) == 0:
            raise HTTPException(status_code=400, detail="Select a circular sketch or edge first")

        fm = doc.FeatureManager

        # Definition type mapping
        type_map = {
            "height_pitch": 0,
            "height_revolutions": 1,
            "pitch_revolutions": 2,
            "spiral": 3
        }
        def_type = type_map.get(request.definition_type.lower(), 0)

        # Convert to meters
        height = request.height / 1000.0
        pitch = request.pitch / 1000.0

        # Create helix
        helix = fm.InsertHelixSpiral(
            def_type,
            True,  # Constant pitch (not variable)
            request.clockwise,
            False,  # Not CCW (use clockwise param)
            request.revolutions if def_type in [1, 2] else 0,
            height if def_type in [0, 1] else 0,
            pitch if def_type in [0, 2] else 0,
            request.start_angle,
            request.taper_angle,
            False  # Taper outward
        )

        return {
            "success": helix is not None,
            "definition_type": request.definition_type,
            "height_mm": request.height,
            "pitch_mm": request.pitch,
            "revolutions": request.revolutions,
            "clockwise": request.clockwise,
            "taper_angle": request.taper_angle,
            "message": "Helix created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create helix failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/spiral/create")
async def create_spiral(request: SpiralRequest):
    """
    Create a flat or conical spiral.

    Used for springs, scroll patterns, cam profiles.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Convert to meters
        start_r = request.start_radius / 1000.0
        end_r = request.end_radius / 1000.0
        height = request.height / 1000.0

        # Calculate pitch from radius change
        radius_change = abs(end_r - start_r)
        pitch = radius_change / request.revolutions if request.revolutions > 0 else 0.001

        # For spiral, use pitch_revolutions type
        spiral = fm.InsertHelixSpiral(
            3,  # Spiral type
            True,  # Constant
            request.clockwise,
            False,
            request.revolutions,
            height,
            pitch,
            0,  # Start angle
            0,  # No taper
            end_r > start_r  # Taper outward if expanding
        )

        return {
            "success": spiral is not None,
            "start_radius_mm": request.start_radius,
            "end_radius_mm": request.end_radius,
            "revolutions": request.revolutions,
            "height_mm": request.height,
            "message": "Spiral created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create spiral failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Thread Database & Callouts
# =============================================================================

@router.get("/database/metric")
async def get_metric_threads():
    """
    Get metric thread database.
    """
    threads = []
    for designation, data in METRIC_THREADS.items():
        threads.append({
            "designation": designation,
            "major_diameter_mm": data["major"],
            "pitch_mm": data["pitch"],
            "minor_external_mm": data["minor_ext"],
            "minor_internal_mm": data["minor_int"],
            "tap_drill_mm": round(data["major"] - data["pitch"], 2),
            "tpi": round(25.4 / data["pitch"], 1)
        })

    return {
        "standard": "ISO Metric",
        "count": len(threads),
        "threads": threads
    }


@router.get("/database/inch")
async def get_inch_threads():
    """
    Get inch (unified) thread database.
    """
    threads = []
    for designation, data in INCH_THREADS.items():
        pitch_mm = 25.4 / data["tpi"]
        threads.append({
            "designation": designation,
            "major_diameter_mm": data["major"],
            "major_diameter_inch": round(data["major"] / 25.4, 4),
            "tpi": data["tpi"],
            "pitch_mm": round(pitch_mm, 3),
            "minor_external_mm": data["minor_ext"],
            "minor_internal_mm": data["minor_int"],
            "tap_drill_mm": round(data["major"] - pitch_mm, 2)
        })

    return {
        "standard": "Unified Inch (UNC/UNF)",
        "count": len(threads),
        "threads": threads
    }


@router.get("/thread/{designation}")
async def get_thread_info(designation: str):
    """
    Get detailed information for a specific thread designation.
    """
    # Check metric
    if designation.startswith("M"):
        base = designation.split("x")[0]
        data = METRIC_THREADS.get(base)
        if data:
            return {
                "designation": designation,
                "standard": "ISO Metric",
                "major_diameter_mm": data["major"],
                "pitch_mm": data["pitch"],
                "minor_external_mm": data["minor_ext"],
                "minor_internal_mm": data["minor_int"],
                "tap_drill_mm": round(data["major"] - data["pitch"], 2),
                "clearance_drill_mm": round(data["major"] + 0.5, 1),
                "thread_depth_mm": round(data["pitch"] * 0.6134, 3),
                "thread_classes": ["6g", "6H", "4g6g", "4H5H"],
                "applications": {
                    "6g/6H": "General purpose",
                    "4g6g/4H5H": "Close fit"
                }
            }

    # Check inch
    data = INCH_THREADS.get(designation)
    if data:
        pitch_mm = 25.4 / data["tpi"]
        return {
            "designation": designation,
            "standard": "Unified Inch",
            "major_diameter_mm": data["major"],
            "major_diameter_inch": round(data["major"] / 25.4, 4),
            "tpi": data["tpi"],
            "pitch_mm": round(pitch_mm, 3),
            "minor_external_mm": data["minor_ext"],
            "minor_internal_mm": data["minor_int"],
            "tap_drill_mm": round(data["major"] - pitch_mm, 2),
            "tap_drill_inch": round((data["major"] - pitch_mm) / 25.4, 4),
            "thread_classes": ["2A", "2B", "3A", "3B"],
            "applications": {
                "2A/2B": "General purpose",
                "3A/3B": "Close fit"
            }
        }

    raise HTTPException(status_code=404, detail=f"Thread {designation} not found")


@router.post("/callout/format")
async def format_thread_callout(request: ThreadCalloutRequest):
    """
    Format a proper thread callout string per drawing standards.
    """
    designation = request.thread_designation
    depth = request.depth

    # Determine if metric or inch
    if designation.startswith("M"):
        # Metric format: M10x1.5-6H
        base = designation.split("x")[0]
        data = METRIC_THREADS.get(base)
        if not data:
            raise HTTPException(status_code=404, detail=f"Unknown thread: {designation}")

        callout = designation
        if "x" not in designation:
            callout = f"{base}x{data['pitch']}"

        if request.include_class:
            callout += "-6H"  # Default internal class

        if request.include_depth and depth:
            callout += f" x {depth}"

    else:
        # Inch format: 1/4-20 UNC-2B
        data = INCH_THREADS.get(designation)
        if not data:
            raise HTTPException(status_code=404, detail=f"Unknown thread: {designation}")

        callout = f"{designation} UNC"

        if request.include_class:
            callout += "-2B"

        if request.include_depth and depth:
            callout += f" x {depth}"

    return {
        "callout": callout,
        "designation": designation,
        "standard": "ISO" if designation.startswith("M") else "ANSI",
        "depth": depth
    }


@router.get("/tap-drill/{designation}")
async def get_tap_drill(designation: str, thread_percent: float = 75.0):
    """
    Calculate tap drill size for a thread designation.

    thread_percent: Percentage of thread engagement (typically 50-75%)
    """
    # Get thread data
    data = None
    is_metric = designation.startswith("M")

    if is_metric:
        base = designation.split("x")[0]
        data = METRIC_THREADS.get(base)
        if data:
            pitch = data["pitch"]
    else:
        data = INCH_THREADS.get(designation)
        if data:
            pitch = 25.4 / data["tpi"]

    if not data:
        raise HTTPException(status_code=404, detail=f"Unknown thread: {designation}")

    major = data["major"]

    # Calculate tap drill for desired thread percentage
    # Formula: Tap drill = Major diameter - (pitch * thread% / 76.98)
    tap_drill = major - (pitch * thread_percent / 76.98)

    # Find closest standard drill
    standard_metric_drills = [2.0, 2.5, 3.0, 3.3, 3.5, 4.0, 4.2, 4.5, 5.0, 5.5, 6.0, 6.5, 6.8, 7.0, 8.0, 8.5, 9.0, 10.0, 10.5, 11.0, 12.0]
    closest = min(standard_metric_drills, key=lambda x: abs(x - tap_drill))

    return {
        "thread": designation,
        "major_diameter_mm": major,
        "pitch_mm": round(pitch, 3),
        "thread_percent": thread_percent,
        "calculated_tap_drill_mm": round(tap_drill, 2),
        "recommended_drill_mm": closest,
        "actual_thread_percent": round((major - closest) / pitch * 76.98, 1),
        "clearance_drill_mm": round(major + 0.5, 1)
    }


__all__ = ["router"]
