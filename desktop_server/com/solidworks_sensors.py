"""
SolidWorks Sensors API
======================
Model sensors for monitoring including:
- Mass property sensors
- Dimension sensors
- Measurement sensors
- Interference sensors
- Simulation data sensors
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


class SensorType(IntEnum):
    """Sensor types."""
    MASS_PROPERTY = 0
    DIMENSION = 1
    MEASUREMENT = 2
    INTERFERENCE = 3
    SIMULATION = 4


class AlertOperator(IntEnum):
    """Alert comparison operators."""
    GREATER_THAN = 0
    LESS_THAN = 1
    BETWEEN = 2
    NOT_BETWEEN = 3
    EQUAL = 4
    NOT_EQUAL = 5


# Pydantic models
class CreateMassSensorRequest(BaseModel):
    name: str
    property_type: str = "mass"  # mass, volume, surface_area, density, center_of_mass
    body_name: Optional[str] = None


class CreateDimensionSensorRequest(BaseModel):
    name: str
    dimension_name: str  # e.g., "D1@Sketch1"


class CreateMeasurementSensorRequest(BaseModel):
    name: str
    measurement_type: str  # distance, angle, radius, length
    entity1: str
    entity2: Optional[str] = None


class SetAlertRequest(BaseModel):
    sensor_name: str
    operator: str  # greater_than, less_than, between, equal
    value1: float
    value2: Optional[float] = None  # For between/not_between


router = APIRouter(prefix="/solidworks-sensors", tags=["solidworks-sensors"])


def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


# =============================================================================
# Sensor Management
# =============================================================================

@router.get("/list")
async def list_sensors():
    """
    List all sensors in the active document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        sensors = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "Sensor":
                try:
                    sensor_data = feature.GetDefinition()
                    value = sensor_data.Value if sensor_data and hasattr(sensor_data, 'Value') else None

                    sensors.append({
                        "name": feature.Name,
                        "type": "sensor",
                        "value": value,
                        "suppressed": feature.IsSuppressed2(1)[0]
                    })
                except Exception:
                    sensors.append({"name": feature.Name, "type": "sensor"})

            feature = feature.GetNextFeature()

        return {
            "count": len(sensors),
            "sensors": sensors
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List sensors failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/mass")
async def create_mass_sensor(request: CreateMassSensorRequest):
    """
    Create a mass property sensor.

    property_type options:
    - mass: Total mass (kg)
    - volume: Total volume (m³)
    - surface_area: Surface area (m²)
    - density: Material density
    - center_of_mass: Center of mass coordinates
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Property type mapping
        prop_map = {
            "mass": 0,
            "volume": 1,
            "surface_area": 2,
            "density": 3,
            "center_of_mass_x": 4,
            "center_of_mass_y": 5,
            "center_of_mass_z": 6
        }
        prop_type = prop_map.get(request.property_type.lower(), 0)

        # Create sensor
        sensor = fm.InsertSensor(
            0,  # Sensor type (0 = mass property)
            prop_type,
            None,  # Bodies to include
            None   # Alert settings
        )

        if sensor:
            sensor.Name = request.name

        doc.EditRebuild3()

        return {
            "success": sensor is not None,
            "name": request.name,
            "property_type": request.property_type,
            "message": f"Mass sensor '{request.name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create mass sensor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension")
async def create_dimension_sensor(request: CreateDimensionSensorRequest):
    """
    Create a dimension sensor to monitor a dimension value.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Select the dimension
        doc.Extension.SelectByID2(request.dimension_name, "DIMENSION", 0, 0, 0, False, 0, None, 0)

        # Create sensor
        sensor = fm.InsertSensor(
            1,  # Sensor type (1 = dimension)
            0,  # Sub-type
            None, None
        )

        if sensor:
            sensor.Name = request.name

        doc.ClearSelection2(True)
        doc.EditRebuild3()

        return {
            "success": sensor is not None,
            "name": request.name,
            "dimension": request.dimension_name,
            "message": f"Dimension sensor '{request.name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create dimension sensor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/measurement")
async def create_measurement_sensor(request: CreateMeasurementSensorRequest):
    """
    Create a measurement sensor between entities.

    measurement_type options:
    - distance: Point-to-point or minimum distance
    - angle: Angle between faces/edges
    - radius: Radius of arc/circle
    - length: Length of edge/curve
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Select entities
        doc.ClearSelection2(True)
        doc.Extension.SelectByID2(request.entity1, "", 0, 0, 0, False, 0, None, 0)
        if request.entity2:
            doc.Extension.SelectByID2(request.entity2, "", 0, 0, 0, True, 0, None, 0)

        # Measurement type mapping
        meas_map = {
            "distance": 0,
            "angle": 1,
            "radius": 2,
            "length": 3
        }
        meas_type = meas_map.get(request.measurement_type.lower(), 0)

        # Create sensor
        sensor = fm.InsertSensor(
            2,  # Sensor type (2 = measurement)
            meas_type,
            None, None
        )

        if sensor:
            sensor.Name = request.name

        doc.ClearSelection2(True)
        doc.EditRebuild3()

        return {
            "success": sensor is not None,
            "name": request.name,
            "measurement_type": request.measurement_type,
            "entity1": request.entity1,
            "entity2": request.entity2,
            "message": f"Measurement sensor '{request.name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create measurement sensor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/interference")
async def create_interference_sensor(name: str = "Interference Sensor"):
    """
    Create an interference detection sensor.
    Monitors for component interference in assemblies.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if doc.GetType() != 2:  # Assembly
            raise HTTPException(status_code=400, detail="Interference sensors require an assembly")

        fm = doc.FeatureManager

        # Create interference sensor
        sensor = fm.InsertSensor(
            3,  # Sensor type (3 = interference)
            0, None, None
        )

        if sensor:
            sensor.Name = name

        doc.EditRebuild3()

        return {
            "success": sensor is not None,
            "name": name,
            "message": f"Interference sensor '{name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create interference sensor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Sensor Values
# =============================================================================

@router.get("/value/{sensor_name}")
async def get_sensor_value(sensor_name: str):
    """
    Get the current value of a sensor.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Find sensor
        feature = doc.FirstFeature()
        while feature:
            if feature.GetTypeName2() == "Sensor" and feature.Name == sensor_name:
                sensor_def = feature.GetDefinition()
                if sensor_def:
                    value = sensor_def.Value if hasattr(sensor_def, 'Value') else None
                    alert_state = sensor_def.AlertState if hasattr(sensor_def, 'AlertState') else None

                    return {
                        "sensor": sensor_name,
                        "value": value,
                        "alert_triggered": alert_state == 1 if alert_state is not None else False
                    }

            feature = feature.GetNextFeature()

        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sensor value failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/values")
async def get_all_sensor_values():
    """
    Get values of all sensors.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        sensors = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "Sensor":
                try:
                    sensor_def = feature.GetDefinition()
                    value = sensor_def.Value if sensor_def and hasattr(sensor_def, 'Value') else None

                    sensors.append({
                        "name": feature.Name,
                        "value": value,
                        "suppressed": feature.IsSuppressed2(1)[0]
                    })
                except Exception:
                    sensors.append({"name": feature.Name, "value": None})

            feature = feature.GetNextFeature()

        return {
            "count": len(sensors),
            "sensors": sensors
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all sensor values failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Alerts
# =============================================================================

@router.post("/alert/set")
async def set_sensor_alert(request: SetAlertRequest):
    """
    Set an alert on a sensor.
    When the condition is met, the sensor flags an alert.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Find sensor
        feature = doc.FirstFeature()
        while feature:
            if feature.GetTypeName2() == "Sensor" and feature.Name == request.sensor_name:
                sensor_def = feature.GetDefinition()
                if sensor_def:
                    # Operator mapping
                    op_map = {
                        "greater_than": 0,
                        "less_than": 1,
                        "between": 2,
                        "not_between": 3,
                        "equal": 4,
                        "not_equal": 5
                    }
                    operator = op_map.get(request.operator.lower(), 0)

                    sensor_def.SetAlert(
                        True,  # Enable alert
                        operator,
                        request.value1,
                        request.value2 or 0
                    )

                    feature.ModifyDefinition(sensor_def, doc, None)
                    doc.EditRebuild3()

                    return {
                        "success": True,
                        "sensor": request.sensor_name,
                        "operator": request.operator,
                        "value1": request.value1,
                        "value2": request.value2,
                        "message": f"Alert set on sensor '{request.sensor_name}'"
                    }

            feature = feature.GetNextFeature()

        raise HTTPException(status_code=404, detail=f"Sensor '{request.sensor_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set sensor alert failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/alerts")
async def get_triggered_alerts():
    """
    Get all sensors with triggered alerts.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        triggered = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "Sensor":
                try:
                    sensor_def = feature.GetDefinition()
                    if sensor_def and hasattr(sensor_def, 'AlertState'):
                        if sensor_def.AlertState == 1:  # Alert triggered
                            triggered.append({
                                "name": feature.Name,
                                "value": sensor_def.Value if hasattr(sensor_def, 'Value') else None
                            })
                except Exception:
                    pass

            feature = feature.GetNextFeature()

        return {
            "triggered_count": len(triggered),
            "alerts": triggered,
            "has_alerts": len(triggered) > 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alerts failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Sensor Operations
# =============================================================================

@router.delete("/{sensor_name}")
async def delete_sensor(sensor_name: str):
    """
    Delete a sensor.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.Extension.SelectByID2(sensor_name, "SENSOR", 0, 0, 0, False, 0, None, 0)
        doc.EditDelete()

        return {"success": True, "deleted": sensor_name}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete sensor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/update-all")
async def update_all_sensors():
    """
    Force update of all sensor values.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        doc.EditRebuild3()

        return {"success": True, "message": "All sensors updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update sensors failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
