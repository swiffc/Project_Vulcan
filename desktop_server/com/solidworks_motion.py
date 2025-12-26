"""
SolidWorks Advanced Motion Study API
====================================
Full motion simulation capabilities including:
- Motion study management
- Motors, springs, dampers, forces
- Contact and collision detection
- Sensors and results extraction
- Animation export
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


class MotionStudyType(IntEnum):
    """Motion study types."""
    ANIMATION = 1
    BASIC_MOTION = 2
    MOTION_ANALYSIS = 3  # Requires SolidWorks Motion add-in


class MotorType(IntEnum):
    """Motor types for motion."""
    ROTARY = 0
    LINEAR = 1


class MotorMotion(IntEnum):
    """Motor motion profiles."""
    CONSTANT_SPEED = 0
    DISTANCE = 1
    OSCILLATING = 2
    SEGMENTS = 3
    DATA_POINTS = 4
    EXPRESSION = 5


class ForceType(IntEnum):
    """Applied force types."""
    APPLIED_FORCE = 0
    GRAVITY = 1
    SPRING = 2
    DAMPER = 3
    BUSHING = 4


class ContactType(IntEnum):
    """Contact/collision types."""
    SOLID_BODIES = 0
    CONTACT_GROUPS = 1


class SensorType(IntEnum):
    """Sensor measurement types."""
    POSITION = 0
    VELOCITY = 1
    ACCELERATION = 2
    FORCE = 3
    TORQUE = 4


# Pydantic models
class CreateMotionStudyRequest(BaseModel):
    name: str
    study_type: str = "basic_motion"  # animation, basic_motion, motion_analysis


class AddMotorRequest(BaseModel):
    motor_type: str = "rotary"  # rotary, linear
    component_name: str
    motion_type: str = "constant_speed"  # constant_speed, distance, oscillating
    speed: float = 60.0  # RPM for rotary, mm/s for linear
    direction_reversed: bool = False


class AddSpringRequest(BaseModel):
    component1: str
    component2: str
    spring_constant: float  # N/mm
    free_length: float  # mm
    damping: float = 0.0  # N*s/mm


class AddDamperRequest(BaseModel):
    component1: str
    component2: str
    damping_coefficient: float  # N*s/mm


class AddGravityRequest(BaseModel):
    direction: str = "-Y"  # +X, -X, +Y, -Y, +Z, -Z
    magnitude: float = 9.81  # m/s^2


class AddContactRequest(BaseModel):
    component1: str
    component2: str
    friction: float = 0.3
    restitution: float = 0.5  # Coefficient of restitution (bounciness)


class AddSensorRequest(BaseModel):
    sensor_type: str  # position, velocity, acceleration, force, torque
    component_name: str
    reference_component: Optional[str] = None


class RunMotionRequest(BaseModel):
    duration: float = 5.0  # seconds
    frame_rate: int = 30  # frames per second
    start_time: float = 0.0


class ExportAnimationRequest(BaseModel):
    output_path: str
    format: str = "avi"  # avi, mp4
    duration: float = 5.0
    frame_rate: int = 30
    width: int = 1920
    height: int = 1080


router = APIRouter(prefix="/solidworks-motion", tags=["solidworks-motion"])


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


def get_motion_manager(doc):
    """Get motion study manager from document."""
    ext = doc.Extension
    if not ext:
        raise HTTPException(status_code=500, detail="Cannot get document extension")

    motion_mgr = ext.GetMotionStudyManager()
    if not motion_mgr:
        raise HTTPException(status_code=501, detail="Motion Study Manager not available")

    return motion_mgr


# =============================================================================
# Motion Study Management
# =============================================================================

@router.post("/study/create")
async def create_motion_study(request: CreateMotionStudyRequest):
    """
    Create a new motion study.

    study_type options:
    - animation: Simple key-frame animation
    - basic_motion: Physics-based with gravity, contact, motors
    - motion_analysis: Full dynamics (requires Motion add-in)
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if doc.GetType() != 2:  # Assembly
            raise HTTPException(status_code=400, detail="Motion studies require an assembly")

        motion_mgr = get_motion_manager(doc)

        type_map = {
            "animation": 1,
            "basic_motion": 2,
            "motion_analysis": 3
        }
        study_type = type_map.get(request.study_type.lower(), 2)

        # Create study
        study = motion_mgr.CreateMotionStudy(request.name, study_type)

        return {
            "success": study is not None,
            "name": request.name,
            "study_type": request.study_type,
            "message": f"Motion study '{request.name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create motion study failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/study/list")
async def list_motion_studies():
    """
    List all motion studies in active document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)

        count = motion_mgr.GetMotionStudyCount()
        studies = []

        for i in range(count):
            study = motion_mgr.GetMotionStudy(i)
            if study:
                studies.append({
                    "index": i,
                    "name": study.Name if hasattr(study, 'Name') else f"Study_{i}",
                    "active": motion_mgr.GetActiveMotionStudy() == study if hasattr(motion_mgr, 'GetActiveMotionStudy') else False
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


@router.post("/study/{name}/activate")
async def activate_motion_study(name: str):
    """
    Activate a motion study by name.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)

        count = motion_mgr.GetMotionStudyCount()
        for i in range(count):
            study = motion_mgr.GetMotionStudy(i)
            if study and hasattr(study, 'Name') and study.Name == name:
                motion_mgr.SetActiveMotionStudy(study)
                return {
                    "success": True,
                    "activated": name
                }

        raise HTTPException(status_code=404, detail=f"Study '{name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Activate study failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/study/{name}")
async def delete_motion_study(name: str):
    """
    Delete a motion study by name.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)

        result = motion_mgr.DeleteMotionStudy(name)

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
# Motors
# =============================================================================

@router.post("/motor/add")
async def add_motor(request: AddMotorRequest):
    """
    Add a motor to the active motion study.

    motor_type: rotary (for rotating components) or linear (for sliding)
    motion_type: constant_speed, distance, oscillating
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        # Select the component/mate to drive
        doc.Extension.SelectByID2(
            request.component_name, "COMPONENT", 0, 0, 0, False, 0, None, 0
        )

        motor_type = 0 if request.motor_type.lower() == "rotary" else 1

        motion_map = {
            "constant_speed": 0,
            "distance": 1,
            "oscillating": 2
        }
        motion_type = motion_map.get(request.motion_type.lower(), 0)

        # Add motor feature
        # Note: Actual API may vary by SW version
        motor = study.AddMotor(
            motor_type,
            motion_type,
            request.speed,
            request.direction_reversed
        )

        return {
            "success": motor is not None,
            "motor_type": request.motor_type,
            "motion_type": request.motion_type,
            "speed": request.speed,
            "unit": "RPM" if motor_type == 0 else "mm/s",
            "message": f"{request.motor_type.capitalize()} motor added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add motor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Springs and Dampers
# =============================================================================

@router.post("/spring/add")
async def add_spring(request: AddSpringRequest):
    """
    Add a spring between two components.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        # Select both components
        doc.ClearSelection2(True)
        doc.Extension.SelectByID2(request.component1, "COMPONENT", 0, 0, 0, False, 0, None, 0)
        doc.Extension.SelectByID2(request.component2, "COMPONENT", 0, 0, 0, True, 0, None, 0)

        # Add spring (linear spring-damper)
        spring = study.AddSpringDamper(
            request.spring_constant,  # N/mm
            request.free_length / 1000.0,  # Convert to meters
            request.damping
        )

        return {
            "success": spring is not None,
            "spring_constant_N_mm": request.spring_constant,
            "free_length_mm": request.free_length,
            "damping_Ns_mm": request.damping,
            "message": "Spring added between components"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add spring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/damper/add")
async def add_damper(request: AddDamperRequest):
    """
    Add a pure damper between two components.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        doc.ClearSelection2(True)
        doc.Extension.SelectByID2(request.component1, "COMPONENT", 0, 0, 0, False, 0, None, 0)
        doc.Extension.SelectByID2(request.component2, "COMPONENT", 0, 0, 0, True, 0, None, 0)

        # Add damper (spring with zero stiffness)
        damper = study.AddSpringDamper(
            0,  # No spring stiffness
            0,  # No free length
            request.damping_coefficient
        )

        return {
            "success": damper is not None,
            "damping_coefficient_Ns_mm": request.damping_coefficient,
            "message": "Damper added between components"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add damper failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Forces and Gravity
# =============================================================================

@router.post("/gravity/add")
async def add_gravity(request: AddGravityRequest):
    """
    Add gravity to the motion study.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        # Direction mapping
        dir_map = {
            "+X": (1, 0, 0), "-X": (-1, 0, 0),
            "+Y": (0, 1, 0), "-Y": (0, -1, 0),
            "+Z": (0, 0, 1), "-Z": (0, 0, -1)
        }
        direction = dir_map.get(request.direction.upper(), (0, -1, 0))

        # Add gravity
        gravity = study.AddGravity(
            direction[0] * request.magnitude,
            direction[1] * request.magnitude,
            direction[2] * request.magnitude
        )

        return {
            "success": gravity is not None,
            "direction": request.direction,
            "magnitude_m_s2": request.magnitude,
            "message": f"Gravity added in {request.direction} direction"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add gravity failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Contact and Collision
# =============================================================================

@router.post("/contact/add")
async def add_contact(request: AddContactRequest):
    """
    Add contact/collision detection between components.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        doc.ClearSelection2(True)
        doc.Extension.SelectByID2(request.component1, "COMPONENT", 0, 0, 0, False, 0, None, 0)
        doc.Extension.SelectByID2(request.component2, "COMPONENT", 0, 0, 0, True, 0, None, 0)

        # Add contact
        contact = study.AddContact(
            request.friction,
            request.restitution,
            0  # Contact type
        )

        return {
            "success": contact is not None,
            "component1": request.component1,
            "component2": request.component2,
            "friction": request.friction,
            "restitution": request.restitution,
            "message": "Contact defined between components"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add contact failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/contact/all-solid-bodies")
async def enable_all_contact():
    """
    Enable contact between all solid bodies (global setting).
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        # Enable global contact
        study.SetSolidBodyContactEnabled(True)

        return {
            "success": True,
            "message": "Contact enabled for all solid bodies"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enable contact failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Sensors
# =============================================================================

@router.post("/sensor/add")
async def add_sensor(request: AddSensorRequest):
    """
    Add a sensor to track motion data.

    sensor_type: position, velocity, acceleration, force, torque
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        doc.Extension.SelectByID2(
            request.component_name, "COMPONENT", 0, 0, 0, False, 0, None, 0
        )

        type_map = {
            "position": 0,
            "velocity": 1,
            "acceleration": 2,
            "force": 3,
            "torque": 4
        }
        sensor_type = type_map.get(request.sensor_type.lower(), 0)

        # Add sensor
        sensor = study.AddSensor(sensor_type)

        return {
            "success": sensor is not None,
            "sensor_type": request.sensor_type,
            "component": request.component_name,
            "message": f"{request.sensor_type.capitalize()} sensor added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add sensor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Run and Results
# =============================================================================

@router.post("/run")
async def run_motion_study(request: RunMotionRequest):
    """
    Run the active motion study.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        # Set study duration
        study.SetDuration(request.duration)
        study.SetFrameRate(request.frame_rate)

        # Calculate the study
        result = study.Calculate()

        return {
            "success": result,
            "duration_seconds": request.duration,
            "frame_rate": request.frame_rate,
            "total_frames": int(request.duration * request.frame_rate),
            "message": "Motion study calculated" if result else "Calculation failed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run motion study failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/results")
async def get_motion_results():
    """
    Get results from the last motion study run.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        # Get basic results info
        duration = study.GetDuration() if hasattr(study, 'GetDuration') else 0
        frame_rate = study.GetFrameRate() if hasattr(study, 'GetFrameRate') else 30

        return {
            "duration_seconds": duration,
            "frame_rate": frame_rate,
            "total_frames": int(duration * frame_rate),
            "message": "Use export endpoint for detailed data"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get results failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/export/animation")
async def export_animation(request: ExportAnimationRequest):
    """
    Export motion study as video animation.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        # Export video
        result = study.SaveAsVideo(
            request.output_path,
            request.frame_rate,
            request.width,
            request.height
        )

        return {
            "success": result,
            "output_path": request.output_path,
            "format": request.format,
            "duration": request.duration,
            "resolution": f"{request.width}x{request.height}",
            "message": f"Animation exported to {request.output_path}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export animation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/export/csv")
async def export_results_csv(output_path: str):
    """
    Export motion results to CSV file.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        result = study.ExportResultsToCSV(output_path)

        return {
            "success": result,
            "output_path": output_path,
            "message": f"Results exported to {output_path}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export CSV failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Playback Control
# =============================================================================

@router.post("/playback/play")
async def play_motion():
    """Start motion playback."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        study.Play()

        return {"success": True, "message": "Playback started"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/playback/stop")
async def stop_motion():
    """Stop motion playback."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        study.Stop()

        return {"success": True, "message": "Playback stopped"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/playback/goto/{time}")
async def goto_time(time: float):
    """
    Go to specific time in motion study.
    time: Time in seconds
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        motion_mgr = get_motion_manager(doc)
        study = motion_mgr.GetActiveMotionStudy()
        if not study:
            raise HTTPException(status_code=404, detail="No active motion study")

        study.GoToTime(time)

        return {"success": True, "time": time}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
