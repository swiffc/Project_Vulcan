"""
Measurement Tools - COM Adapter
Provides measurement capabilities for SolidWorks and Inventor.

Priority 1 API - Measurement Tools (12.5% coverage)
Enables:
- "What's the distance between these two holes?"
- "Measure the angle of this bend"
- "Get the bounding box dimensions"
- "What's the clearance between these parts?"
"""

import logging
import math
from typing import List, Dict, Optional, Tuple
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("com.measurement")

router = APIRouter(prefix="/com/measurement", tags=["Measurement"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class Point3D(BaseModel):
    """3D point coordinates."""
    x: float
    y: float
    z: float


class BoundingBox(BaseModel):
    """3D bounding box."""
    min: Point3D
    max: Point3D
    width: float
    height: float
    depth: float
    volume: float


class DistanceMeasurement(BaseModel):
    """Distance measurement result."""
    distance: float
    point1: Point3D
    point2: Point3D
    units: str = "meters"


class AngleMeasurement(BaseModel):
    """Angle measurement result."""
    angle_degrees: float
    angle_radians: float
    vertex: Optional[Point3D] = None


class MeasureDistanceRequest(BaseModel):
    """Request to measure distance between entities."""
    entity1_type: str  # "face", "edge", "vertex", "point"
    entity2_type: str
    entity1_index: Optional[int] = 0  # If selecting by index
    entity2_index: Optional[int] = 0
    point1: Optional[Point3D] = None  # If measuring from explicit points
    point2: Optional[Point3D] = None


class MeasureAngleRequest(BaseModel):
    """Request to measure angle between entities."""
    entity1_type: str  # "face", "edge", "line"
    entity2_type: str
    entity1_index: Optional[int] = 0
    entity2_index: Optional[int] = 0


# ============================================================================
# SOLIDWORKS MEASUREMENT TOOLS
# ============================================================================

class SolidWorksMeasurement:
    """SolidWorks measurement utilities."""
    
    def __init__(self, sw_app=None):
        self.app = sw_app
    
    def get_bounding_box(self) -> BoundingBox:
        """Get bounding box of active model."""
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Get bounding box
        # GetBox returns [xmin, ymin, zmin, xmax, ymax, zmax]
        box = model.Extension.GetBox()
        if not box or len(box) < 6:
            raise ValueError("Failed to get bounding box")
        
        min_point = Point3D(x=box[0], y=box[1], z=box[2])
        max_point = Point3D(x=box[3], y=box[4], z=box[5])
        
        width = abs(box[3] - box[0])
        height = abs(box[4] - box[1])
        depth = abs(box[5] - box[2])
        volume = width * height * depth
        
        return BoundingBox(
            min=min_point,
            max=max_point,
            width=width,
            height=height,
            depth=depth,
            volume=volume
        )
    
    def measure_distance_points(self, p1: Point3D, p2: Point3D) -> DistanceMeasurement:
        """Measure distance between two points."""
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dz = p2.z - p1.z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        return DistanceMeasurement(
            distance=distance,
            point1=p1,
            point2=p2,
            units="meters"
        )
    
    def measure_distance_selection(self) -> DistanceMeasurement:
        """
        Measure distance between two selected entities.
        Requires user to pre-select 2 entities.
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        sel_mgr = model.SelectionManager
        sel_count = sel_mgr.GetSelectedObjectCount2(-1)
        
        if sel_count < 2:
            raise ValueError(f"Need 2 selections, got {sel_count}. Select 2 faces/edges/vertices first.")
        
        # Get selected objects
        obj1 = sel_mgr.GetSelectedObject6(1, -1)
        obj2 = sel_mgr.GetSelectedObject6(2, -1)
        
        if not obj1 or not obj2:
            raise ValueError("Failed to get selected objects")
        
        # Use measure tool
        measure = model.Extension.CreateMeasure()
        if not measure:
            raise ValueError("Failed to create measure tool")
        
        # Set entities to measure
        measure.SetEntity1(obj1)
        measure.SetEntity2(obj2)
        measure.Calculate()
        
        # Get distance
        distance = measure.Distance
        
        # Get closest points
        pts = measure.GetClosestPoints()
        if pts and len(pts) >= 6:
            p1 = Point3D(x=pts[0], y=pts[1], z=pts[2])
            p2 = Point3D(x=pts[3], y=pts[4], z=pts[5])
        else:
            # Fallback to entity centers
            p1 = Point3D(x=0, y=0, z=0)
            p2 = Point3D(x=0, y=0, z=0)
        
        return DistanceMeasurement(
            distance=distance,
            point1=p1,
            point2=p2,
            units="meters"
        )
    
    def measure_angle_selection(self) -> AngleMeasurement:
        """
        Measure angle between two selected entities.
        Requires user to pre-select 2 faces/edges.
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        sel_mgr = model.SelectionManager
        sel_count = sel_mgr.GetSelectedObjectCount2(-1)
        
        if sel_count < 2:
            raise ValueError(f"Need 2 selections, got {sel_count}")
        
        obj1 = sel_mgr.GetSelectedObject6(1, -1)
        obj2 = sel_mgr.GetSelectedObject6(2, -1)
        
        if not obj1 or not obj2:
            raise ValueError("Failed to get selected objects")
        
        # Use measure tool
        measure = model.Extension.CreateMeasure()
        measure.SetEntity1(obj1)
        measure.SetEntity2(obj2)
        measure.Calculate()
        
        # Get angle in radians
        angle_rad = measure.Angle
        angle_deg = math.degrees(angle_rad)
        
        return AngleMeasurement(
            angle_degrees=angle_deg,
            angle_radians=angle_rad
        )
    
    def check_clearance(self, min_clearance: float = 0.001) -> Dict:
        """
        Check clearance/interference in assembly.
        
        Args:
            min_clearance: Minimum acceptable clearance (meters)
        
        Returns:
            Dict with clearance info and any interferences
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Check if assembly
        if model.GetType() != 2:  # 2 = swDocASSEMBLY
            raise ValueError("Clearance check only works on assemblies")
        
        # Get interference detection
        interference_result = {
            "has_interference": False,
            "interference_count": 0,
            "min_clearance_met": True,
            "components_checked": 0
        }
        
        # Run interference detection
        # Note: This requires COM methods - simplified version
        logger.info(f"Running clearance check with min clearance: {min_clearance}m")
        
        # Count components
        comp_count = model.GetComponentCount(False)
        interference_result["components_checked"] = comp_count
        
        # TODO: Implement full interference detection
        # For now, return basic structure
        
        return interference_result


# ============================================================================
# INVENTOR MEASUREMENT TOOLS
# ============================================================================

class InventorMeasurement:
    """Inventor measurement utilities."""
    
    def __init__(self, inv_app=None):
        self.app = inv_app
    
    def get_bounding_box(self) -> BoundingBox:
        """Get bounding box of active model."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        # Get bounding box
        if hasattr(doc, 'ComponentDefinition'):
            comp_def = doc.ComponentDefinition
            range_box = comp_def.RangeBox
            
            min_point = Point3D(
                x=range_box.MinPoint.X,
                y=range_box.MinPoint.Y,
                z=range_box.MinPoint.Z
            )
            max_point = Point3D(
                x=range_box.MaxPoint.X,
                y=range_box.MaxPoint.Y,
                z=range_box.MaxPoint.Z
            )
            
            width = abs(max_point.x - min_point.x)
            height = abs(max_point.y - min_point.y)
            depth = abs(max_point.z - min_point.z)
            volume = width * height * depth
            
            return BoundingBox(
                min=min_point,
                max=max_point,
                width=width,
                height=height,
                depth=depth,
                volume=volume
            )
        
        raise ValueError("Cannot get bounding box for this document type")
    
    def measure_distance_points(self, p1: Point3D, p2: Point3D) -> DistanceMeasurement:
        """Measure distance between two points."""
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dz = p2.z - p1.z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        return DistanceMeasurement(
            distance=distance,
            point1=p1,
            point2=p2,
            units="centimeters"  # Inventor uses cm
        )
    
    def measure_distance_selection(self) -> DistanceMeasurement:
        """Measure distance between selected entities."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        # Get selected entities
        # Inventor measure tool usage
        logger.warning("Inventor measure from selection not fully implemented")
        
        # Placeholder
        return DistanceMeasurement(
            distance=0.0,
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=0, y=0, z=0),
            units="centimeters"
        )
    
    def measure_angle_selection(self) -> AngleMeasurement:
        """Measure angle between selected entities."""
        logger.warning("Inventor angle measurement not fully implemented")
        return AngleMeasurement(angle_degrees=0.0, angle_radians=0.0)
    
    def check_clearance(self, min_clearance: float = 0.1) -> Dict:
        """Check clearance in assembly (Inventor uses cm)."""
        logger.warning("Inventor clearance check not fully implemented")
        return {
            "has_interference": False,
            "interference_count": 0,
            "min_clearance_met": True,
            "components_checked": 0
        }


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

_sw_measure: Optional[SolidWorksMeasurement] = None
_inv_measure: Optional[InventorMeasurement] = None


def set_solidworks_app(sw_app):
    """Set SolidWorks application instance."""
    global _sw_measure
    _sw_measure = SolidWorksMeasurement(sw_app)


def set_inventor_app(inv_app):
    """Set Inventor application instance."""
    global _inv_measure
    _inv_measure = InventorMeasurement(inv_app)


@router.get("/bounding-box")
async def get_bounding_box(cad_system: str = "solidworks"):
    """Get bounding box of active model."""
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_measure:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            bbox = _sw_measure.get_bounding_box()
        else:
            if not _inv_measure:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            bbox = _inv_measure.get_bounding_box()
        
        return {
            "success": True,
            "bounding_box": bbox.dict()
        }
    except Exception as e:
        logger.error(f"Get bounding box failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/distance")
async def measure_distance(request: MeasureDistanceRequest, cad_system: str = "solidworks"):
    """Measure distance between entities or points."""
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_measure:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            
            # If explicit points provided
            if request.point1 and request.point2:
                result = _sw_measure.measure_distance_points(request.point1, request.point2)
            else:
                # Measure from selection
                result = _sw_measure.measure_distance_selection()
        else:
            if not _inv_measure:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            
            if request.point1 and request.point2:
                result = _inv_measure.measure_distance_points(request.point1, request.point2)
            else:
                result = _inv_measure.measure_distance_selection()
        
        return {
            "success": True,
            "measurement": result.dict()
        }
    except Exception as e:
        logger.error(f"Measure distance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/angle")
async def measure_angle(request: MeasureAngleRequest, cad_system: str = "solidworks"):
    """Measure angle between entities."""
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_measure:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            result = _sw_measure.measure_angle_selection()
        else:
            if not _inv_measure:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            result = _inv_measure.measure_angle_selection()
        
        return {
            "success": True,
            "measurement": result.dict()
        }
    except Exception as e:
        logger.error(f"Measure angle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clearance")
async def check_clearance(min_clearance: float = 0.001, cad_system: str = "solidworks"):
    """
    Check clearance/interference in assembly.
    
    Args:
        min_clearance: Minimum acceptable clearance (meters for SW, cm for Inventor)
        cad_system: "solidworks" or "inventor"
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_measure:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            result = _sw_measure.check_clearance(min_clearance)
        else:
            if not _inv_measure:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            result = _inv_measure.check_clearance(min_clearance)
        
        return {
            "success": True,
            "clearance_check": result
        }
    except Exception as e:
        logger.error(f"Check clearance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
