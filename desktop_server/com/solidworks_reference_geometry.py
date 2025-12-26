"""
SolidWorks Reference Geometry API
=================================
Reference geometry creation and management including:
- Reference planes
- Reference axes
- Reference points
- Coordinate systems
- Centerlines
"""

import logging
import math
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


# Pydantic models
class PlaneOffsetRequest(BaseModel):
    reference_plane: str = "Front Plane"  # Front, Top, Right, or feature name
    offset: float  # mm


class PlaneAngleRequest(BaseModel):
    reference_plane: str
    reference_edge: str
    angle: float  # degrees


class Plane3PointsRequest(BaseModel):
    point1: List[float]  # [X, Y, Z] in mm
    point2: List[float]
    point3: List[float]


class AxisRequest(BaseModel):
    axis_type: str  # two_planes, two_points, cylindrical, point_edge
    reference1: str
    reference2: Optional[str] = None


class PointRequest(BaseModel):
    point_type: str  # coordinates, arc_center, face_center, edge_vertex
    coordinates: Optional[List[float]] = None  # [X, Y, Z] for coordinate type
    reference: Optional[str] = None


class CoordinateSystemRequest(BaseModel):
    origin: List[float]  # [X, Y, Z] in mm
    x_direction: Optional[List[float]] = None
    y_direction: Optional[List[float]] = None
    name: Optional[str] = None


router = APIRouter(prefix="/solidworks-reference", tags=["solidworks-reference"])


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
# Reference Planes
# =============================================================================

@router.post("/plane/offset")
async def create_offset_plane(request: PlaneOffsetRequest):
    """
    Create a plane offset from a reference plane.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Select reference plane
        doc.Extension.SelectByID2(request.reference_plane, "PLANE", 0, 0, 0, False, 0, None, 0)

        fm = doc.FeatureManager

        # Create offset plane (convert mm to m)
        plane = fm.InsertRefPlane(
            1 | 4,  # Constraint: offset from plane
            request.offset / 1000.0,  # Offset in meters
            0, 0,  # Second constraint
            0, 0   # Third constraint
        )

        doc.ClearSelection2(True)

        return {
            "success": plane is not None,
            "reference": request.reference_plane,
            "offset_mm": request.offset,
            "message": f"Plane created at {request.offset}mm offset"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create offset plane failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/plane/angle")
async def create_angle_plane(request: PlaneAngleRequest):
    """
    Create a plane at an angle to a reference plane about an edge.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Select reference plane and edge
        doc.Extension.SelectByID2(request.reference_plane, "PLANE", 0, 0, 0, False, 0, None, 0)
        doc.Extension.SelectByID2(request.reference_edge, "EDGE", 0, 0, 0, True, 0, None, 0)

        fm = doc.FeatureManager

        # Create angled plane
        angle_rad = math.radians(request.angle)
        plane = fm.InsertRefPlane(
            1 | 8,  # At angle to plane
            0,
            2 | 16,  # Parallel to edge
            angle_rad,
            0, 0
        )

        doc.ClearSelection2(True)

        return {
            "success": plane is not None,
            "reference_plane": request.reference_plane,
            "reference_edge": request.reference_edge,
            "angle_deg": request.angle,
            "message": f"Plane created at {request.angle}° angle"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create angle plane failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/plane/three-points")
async def create_plane_from_points(request: Plane3PointsRequest):
    """
    Create a plane through three points.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Convert mm to m
        p1 = [v / 1000.0 for v in request.point1]
        p2 = [v / 1000.0 for v in request.point2]
        p3 = [v / 1000.0 for v in request.point3]

        # Create reference points first
        sm = doc.SketchManager

        # Create plane through 3 points
        plane = fm.InsertRefPlane3(
            p1[0], p1[1], p1[2],
            p2[0], p2[1], p2[2],
            p3[0], p3[1], p3[2]
        )

        return {
            "success": plane is not None,
            "point1_mm": request.point1,
            "point2_mm": request.point2,
            "point3_mm": request.point3,
            "message": "Plane created through 3 points"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create 3-point plane failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/plane/midplane")
async def create_midplane(face1: str, face2: str):
    """
    Create a midplane between two parallel faces.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Select two faces
        doc.Extension.SelectByID2(face1, "FACE", 0, 0, 0, False, 0, None, 0)
        doc.Extension.SelectByID2(face2, "FACE", 0, 0, 0, True, 0, None, 0)

        fm = doc.FeatureManager

        # Create midplane
        plane = fm.InsertRefPlane(
            1 | 256,  # Midplane constraint
            0, 0, 0, 0, 0
        )

        doc.ClearSelection2(True)

        return {
            "success": plane is not None,
            "face1": face1,
            "face2": face2,
            "message": "Midplane created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create midplane failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Reference Axes
# =============================================================================

@router.post("/axis/create")
async def create_axis(request: AxisRequest):
    """
    Create a reference axis.

    axis_type options:
    - two_planes: Intersection of two planes
    - two_points: Through two points
    - cylindrical: Through cylindrical face
    - point_edge: Through point parallel to edge
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Select references
        if request.axis_type == "two_planes":
            doc.Extension.SelectByID2(request.reference1, "PLANE", 0, 0, 0, False, 0, None, 0)
            doc.Extension.SelectByID2(request.reference2, "PLANE", 0, 0, 0, True, 0, None, 0)
            axis = fm.InsertRefAxis(0)  # Two planes

        elif request.axis_type == "cylindrical":
            doc.Extension.SelectByID2(request.reference1, "FACE", 0, 0, 0, False, 0, None, 0)
            axis = fm.InsertRefAxis(1)  # Cylindrical/conical face

        elif request.axis_type == "two_points":
            doc.Extension.SelectByID2(request.reference1, "VERTEX", 0, 0, 0, False, 0, None, 0)
            doc.Extension.SelectByID2(request.reference2, "VERTEX", 0, 0, 0, True, 0, None, 0)
            axis = fm.InsertRefAxis(2)  # Two points

        else:
            raise HTTPException(status_code=400, detail=f"Unknown axis type: {request.axis_type}")

        doc.ClearSelection2(True)

        return {
            "success": axis is not None,
            "axis_type": request.axis_type,
            "reference1": request.reference1,
            "reference2": request.reference2,
            "message": "Reference axis created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create axis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Reference Points
# =============================================================================

@router.post("/point/create")
async def create_point(request: PointRequest):
    """
    Create a reference point.

    point_type options:
    - coordinates: At specific X, Y, Z location
    - arc_center: At center of arc/circle
    - face_center: At center of face
    - edge_vertex: At edge endpoint
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        if request.point_type == "coordinates":
            if not request.coordinates:
                raise HTTPException(status_code=400, detail="Coordinates required")

            # Convert mm to m
            x, y, z = [v / 1000.0 for v in request.coordinates]

            point = fm.InsertReferencePoint(
                0,  # Point type: coordinates
                0, 0, 0,
                x, y, z
            )

        elif request.point_type == "arc_center":
            if not request.reference:
                raise HTTPException(status_code=400, detail="Reference edge required")

            doc.Extension.SelectByID2(request.reference, "EDGE", 0, 0, 0, False, 0, None, 0)
            point = fm.InsertReferencePoint(1, 0, 0, 0, 0, 0, 0)  # Arc center

        elif request.point_type == "face_center":
            if not request.reference:
                raise HTTPException(status_code=400, detail="Reference face required")

            doc.Extension.SelectByID2(request.reference, "FACE", 0, 0, 0, False, 0, None, 0)
            point = fm.InsertReferencePoint(2, 0, 0, 0, 0, 0, 0)  # Face center

        else:
            raise HTTPException(status_code=400, detail=f"Unknown point type: {request.point_type}")

        doc.ClearSelection2(True)

        return {
            "success": point is not None,
            "point_type": request.point_type,
            "coordinates_mm": request.coordinates,
            "message": "Reference point created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create point failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Coordinate Systems
# =============================================================================

@router.post("/coordinate-system/create")
async def create_coordinate_system(request: CoordinateSystemRequest):
    """
    Create a coordinate system at specified origin and orientation.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fm = doc.FeatureManager

        # Convert mm to m
        origin = [v / 1000.0 for v in request.origin]

        # Default directions if not specified
        x_dir = request.x_direction or [1, 0, 0]
        y_dir = request.y_direction or [0, 1, 0]

        cs = fm.InsertCoordinateSystem(
            False,  # Use selection for origin
            False,  # Use selection for X axis
            False,  # Use selection for Y axis
            origin[0], origin[1], origin[2],
            x_dir[0], x_dir[1], x_dir[2],
            y_dir[0], y_dir[1], y_dir[2]
        )

        if cs and request.name:
            cs.Name = request.name

        return {
            "success": cs is not None,
            "origin_mm": request.origin,
            "x_direction": x_dir,
            "y_direction": y_dir,
            "name": request.name,
            "message": "Coordinate system created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create coordinate system failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/coordinate-systems")
async def list_coordinate_systems():
    """
    List all coordinate systems in the document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        coord_systems = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "CoordSys":
                coord_systems.append({
                    "name": feature.Name,
                    "suppressed": feature.IsSuppressed2(1)[0]
                })
            feature = feature.GetNextFeature()

        return {
            "count": len(coord_systems),
            "coordinate_systems": coord_systems
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List coordinate systems failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Reference Geometry Listing
# =============================================================================

@router.get("/planes")
async def list_planes():
    """
    List all planes in the document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        planes = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "RefPlane":
                planes.append({
                    "name": feature.Name,
                    "suppressed": feature.IsSuppressed2(1)[0]
                })
            feature = feature.GetNextFeature()

        return {
            "count": len(planes),
            "planes": planes
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List planes failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/axes")
async def list_axes():
    """
    List all reference axes in the document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        axes = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "RefAxis":
                axes.append({
                    "name": feature.Name,
                    "suppressed": feature.IsSuppressed2(1)[0]
                })
            feature = feature.GetNextFeature()

        return {
            "count": len(axes),
            "axes": axes
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List axes failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/points")
async def list_reference_points():
    """
    List all reference points in the document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        points = []
        feature = doc.FirstFeature()

        while feature:
            if feature.GetTypeName2() == "RefPoint":
                points.append({
                    "name": feature.Name,
                    "suppressed": feature.IsSuppressed2(1)[0]
                })
            feature = feature.GetNextFeature()

        return {
            "count": len(points),
            "points": points
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List points failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
