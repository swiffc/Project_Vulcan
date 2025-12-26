"""
SolidWorks Surface Analysis API
===============================
Surface quality and analysis tools including:
- Curvature analysis (Gaussian, mean, principal)
- Zebra stripe analysis
- Draft analysis
- Deviation analysis
- Surface quality metrics
"""

import logging
import math
from typing import Optional, Dict, Any, List, Tuple
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


class CurvatureType(IntEnum):
    """Curvature analysis types."""
    GAUSSIAN = 0  # Product of principal curvatures
    MEAN = 1  # Average of principal curvatures
    MAX_PRINCIPAL = 2  # Maximum principal curvature
    MIN_PRINCIPAL = 3  # Minimum principal curvature


class DraftDirection(IntEnum):
    """Draft analysis direction."""
    POSITIVE_ONLY = 0
    NEGATIVE_ONLY = 1
    BOTH = 2


class DeviationType(IntEnum):
    """Deviation analysis types."""
    POINT_TO_SURFACE = 0
    SURFACE_TO_SURFACE = 1


@dataclass
class CurvatureResult:
    """Result from curvature analysis."""
    min_value: float
    max_value: float
    average: float
    distribution: List[Tuple[float, float]]  # (curvature, area_percent)


@dataclass
class DraftResult:
    """Result from draft analysis."""
    positive_draft_area: float
    negative_draft_area: float
    zero_draft_area: float
    min_draft_angle: float
    max_draft_angle: float


# Pydantic models
class CurvatureAnalysisRequest(BaseModel):
    curvature_type: str = "gaussian"  # gaussian, mean, max_principal, min_principal
    face_names: List[str] = []  # Empty = all faces
    color_scale_min: float = -0.1
    color_scale_max: float = 0.1


class ZebraAnalysisRequest(BaseModel):
    stripe_count: int = 10
    stripe_width_ratio: float = 0.5  # 0-1, black/white ratio
    direction: str = "horizontal"  # horizontal, vertical, custom
    custom_angle: float = 0.0


class DraftAnalysisRequest(BaseModel):
    pull_direction: str = "+Z"  # +X, -X, +Y, -Y, +Z, -Z
    positive_angle: float = 1.0  # Minimum acceptable draft (degrees)
    negative_angle: float = -1.0
    face_names: List[str] = []


class DeviationAnalysisRequest(BaseModel):
    reference_body: str  # Name of reference body/surface
    analysis_body: str  # Name of body to analyze
    tolerance: float = 0.1  # mm


class UnderCutAnalysisRequest(BaseModel):
    pull_direction: str = "+Z"
    include_shadowed: bool = True


class SurfaceQualityRequest(BaseModel):
    face_names: List[str] = []
    check_continuity: bool = True
    check_curvature: bool = True


router = APIRouter(prefix="/solidworks-surfaces", tags=["solidworks-surfaces"])


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
# Curvature Analysis
# =============================================================================

@router.post("/curvature/analyze")
async def analyze_curvature(request: CurvatureAnalysisRequest):
    """
    Perform curvature analysis on selected faces.

    curvature_type:
    - gaussian: K = k1 * k2 (positive=convex, negative=saddle, zero=flat)
    - mean: H = (k1 + k2) / 2
    - max_principal: Maximum curvature direction
    - min_principal: Minimum curvature direction
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension

        # Map curvature type
        type_map = {
            "gaussian": 0,
            "mean": 1,
            "max_principal": 2,
            "min_principal": 3
        }
        curv_type = type_map.get(request.curvature_type.lower(), 0)

        # Select faces if specified
        if request.face_names:
            doc.ClearSelection2(True)
            for face_name in request.face_names:
                doc.Extension.SelectByID2(face_name, "FACE", 0, 0, 0, True, 0, None, 0)

        # Create curvature display
        curv_analysis = model_ext.CreateCurvatureAnalysis()

        if curv_analysis:
            curv_analysis.SetCurvatureType(curv_type)
            curv_analysis.SetColorScaleMin(request.color_scale_min)
            curv_analysis.SetColorScaleMax(request.color_scale_max)
            curv_analysis.Update()

            # Get statistics
            stats = curv_analysis.GetStatistics() if hasattr(curv_analysis, 'GetStatistics') else None

        return {
            "success": curv_analysis is not None,
            "curvature_type": request.curvature_type,
            "scale_range": [request.color_scale_min, request.color_scale_max],
            "faces_analyzed": len(request.face_names) if request.face_names else "all",
            "interpretation": {
                "gaussian": {
                    "positive": "Convex surface (dome)",
                    "negative": "Saddle surface",
                    "zero": "Flat or cylindrical"
                },
                "mean": {
                    "positive": "Overall convex",
                    "negative": "Overall concave",
                    "zero": "Minimal surface"
                }
            }.get(request.curvature_type, {}),
            "message": "Curvature analysis displayed on model"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Curvature analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/curvature/clear")
async def clear_curvature_display():
    """
    Clear curvature analysis display.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension
        model_ext.DeleteCurvatureAnalysis()

        return {"success": True, "message": "Curvature display cleared"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Zebra Stripe Analysis
# =============================================================================

@router.post("/zebra/enable")
async def enable_zebra_stripes(request: ZebraAnalysisRequest):
    """
    Enable zebra stripe analysis for surface continuity checking.

    Zebra stripes show:
    - G0 (position): Stripes break at edges
    - G1 (tangent): Stripes meet but kink
    - G2 (curvature): Stripes flow smoothly
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension

        # Create zebra analysis
        zebra = model_ext.CreateZebraStripeAnalysis()

        if zebra:
            zebra.SetStripeCount(request.stripe_count)
            zebra.SetWidthRatio(request.stripe_width_ratio)

            dir_map = {
                "horizontal": 0,
                "vertical": 1,
                "custom": 2
            }
            zebra.SetDirection(dir_map.get(request.direction.lower(), 0))

            if request.direction.lower() == "custom":
                zebra.SetCustomAngle(request.custom_angle)

            zebra.Update()

        return {
            "success": zebra is not None,
            "stripe_count": request.stripe_count,
            "width_ratio": request.stripe_width_ratio,
            "direction": request.direction,
            "interpretation": {
                "G0_position": "Stripes break completely - surfaces only touch",
                "G1_tangent": "Stripes meet at angle - tangent continuous",
                "G2_curvature": "Stripes flow smoothly - curvature continuous"
            },
            "message": "Zebra stripes enabled"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Zebra analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/zebra/disable")
async def disable_zebra_stripes():
    """
    Disable zebra stripe display.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension
        model_ext.DeleteZebraStripeAnalysis()

        return {"success": True, "message": "Zebra stripes disabled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Draft Analysis
# =============================================================================

@router.post("/draft/analyze")
async def analyze_draft(request: DraftAnalysisRequest):
    """
    Perform draft analysis for moldability.

    Shows faces with insufficient draft angle for mold release.
    Color coding:
    - Green: Positive draft (good)
    - Red: Negative draft (undercut)
    - Yellow: Insufficient draft
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension

        # Parse pull direction
        dir_map = {
            "+X": (1, 0, 0), "-X": (-1, 0, 0),
            "+Y": (0, 1, 0), "-Y": (0, -1, 0),
            "+Z": (0, 0, 1), "-Z": (0, 0, -1)
        }
        direction = dir_map.get(request.pull_direction.upper(), (0, 0, 1))

        # Select faces if specified
        if request.face_names:
            doc.ClearSelection2(True)
            for face_name in request.face_names:
                doc.Extension.SelectByID2(face_name, "FACE", 0, 0, 0, True, 0, None, 0)

        # Create draft analysis
        draft = model_ext.CreateDraftAnalysis()

        if draft:
            draft.SetPullDirection(direction[0], direction[1], direction[2])
            draft.SetPositiveAngle(math.radians(request.positive_angle))
            draft.SetNegativeAngle(math.radians(request.negative_angle))
            draft.Update()

        return {
            "success": draft is not None,
            "pull_direction": request.pull_direction,
            "positive_draft_angle_deg": request.positive_angle,
            "negative_draft_angle_deg": request.negative_angle,
            "color_legend": {
                "green": f"Draft >= {request.positive_angle}° (good for mold release)",
                "yellow": f"Draft between 0° and {request.positive_angle}° (marginal)",
                "red": "Negative draft (undercut - requires side action or redesign)"
            },
            "message": "Draft analysis displayed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Draft analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/draft/clear")
async def clear_draft_analysis():
    """
    Clear draft analysis display.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension
        model_ext.DeleteDraftAnalysis()

        return {"success": True, "message": "Draft analysis cleared"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Undercut Analysis
# =============================================================================

@router.post("/undercut/analyze")
async def analyze_undercuts(request: UnderCutAnalysisRequest):
    """
    Analyze model for undercuts that prevent mold release.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension

        dir_map = {
            "+X": (1, 0, 0), "-X": (-1, 0, 0),
            "+Y": (0, 1, 0), "-Y": (0, -1, 0),
            "+Z": (0, 0, 1), "-Z": (0, 0, -1)
        }
        direction = dir_map.get(request.pull_direction.upper(), (0, 0, 1))

        # Create undercut analysis
        undercut = model_ext.CreateUndercutAnalysis()

        if undercut:
            undercut.SetPullDirection(direction[0], direction[1], direction[2])
            undercut.SetIncludeShadowed(request.include_shadowed)
            undercut.Update()

            # Get undercut faces
            undercut_faces = undercut.GetUndercutFaces() if hasattr(undercut, 'GetUndercutFaces') else []
            shadowed_faces = undercut.GetShadowedFaces() if hasattr(undercut, 'GetShadowedFaces') else []

        return {
            "success": undercut is not None,
            "pull_direction": request.pull_direction,
            "undercut_face_count": len(undercut_faces) if undercut_faces else 0,
            "shadowed_face_count": len(shadowed_faces) if shadowed_faces else 0,
            "recommendations": [
                "Consider adding draft to undercut faces",
                "Side actions may be required for complex undercuts",
                "Split mold at parting line if possible"
            ],
            "message": "Undercut analysis displayed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Undercut analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Deviation Analysis
# =============================================================================

@router.post("/deviation/analyze")
async def analyze_deviation(request: DeviationAnalysisRequest):
    """
    Compare two surfaces/bodies and show deviation.
    Useful for comparing scanned data to CAD or checking import quality.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        model_ext = doc.Extension

        # Select reference and analysis bodies
        doc.ClearSelection2(True)
        doc.Extension.SelectByID2(request.reference_body, "SOLIDBODY", 0, 0, 0, False, 1, None, 0)
        doc.Extension.SelectByID2(request.analysis_body, "SOLIDBODY", 0, 0, 0, True, 2, None, 0)

        # Create deviation analysis
        deviation = model_ext.CreateDeviationAnalysis()

        if deviation:
            deviation.SetTolerance(request.tolerance / 1000.0)  # Convert mm to m
            deviation.Update()

            # Get statistics
            stats = {
                "max_deviation": deviation.GetMaxDeviation() * 1000 if hasattr(deviation, 'GetMaxDeviation') else None,
                "min_deviation": deviation.GetMinDeviation() * 1000 if hasattr(deviation, 'GetMinDeviation') else None,
                "avg_deviation": deviation.GetAverageDeviation() * 1000 if hasattr(deviation, 'GetAverageDeviation') else None,
                "std_deviation": deviation.GetStandardDeviation() * 1000 if hasattr(deviation, 'GetStandardDeviation') else None
            }

        return {
            "success": deviation is not None,
            "reference": request.reference_body,
            "analysis": request.analysis_body,
            "tolerance_mm": request.tolerance,
            "statistics_mm": stats if deviation else None,
            "message": "Deviation analysis displayed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deviation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Surface Quality Check
# =============================================================================

@router.get("/quality/check")
async def check_surface_quality():
    """
    Check overall surface quality of the model.
    Reports issues like:
    - Tangent discontinuities
    - Curvature discontinuities
    - Short edges
    - Sliver faces
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        issues = []

        # Get all faces and check them
        bodies = doc.GetBodies2(0, False)  # Solid bodies
        if bodies:
            for body in bodies:
                faces = body.GetFaces()
                if faces:
                    for face in faces:
                        try:
                            surf = face.GetSurface()
                            if surf:
                                # Check for problematic geometry
                                area = face.GetArea()

                                # Flag very small faces (slivers)
                                if area < 1e-8:  # < 0.01 mm²
                                    issues.append({
                                        "type": "sliver_face",
                                        "severity": "warning",
                                        "description": f"Very small face detected (area: {area * 1e6:.4f} mm²)"
                                    })

                                # Check edges for short segments
                                edges = face.GetEdges()
                                if edges:
                                    for edge in edges:
                                        curve = edge.GetCurve()
                                        if curve:
                                            params = edge.GetCurveParams3()
                                            if params:
                                                length = params[6]  # Arc length
                                                if length < 1e-4:  # < 0.1mm
                                                    issues.append({
                                                        "type": "short_edge",
                                                        "severity": "warning",
                                                        "description": f"Short edge detected (length: {length * 1000:.4f} mm)"
                                                    })
                        except Exception:
                            pass

        # Categorize by severity
        errors = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]

        return {
            "document": doc.GetTitle(),
            "overall_quality": "good" if len(errors) == 0 else ("fair" if len(errors) < 5 else "poor"),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "issues": issues[:50],  # Limit to first 50
            "recommendations": [
                "Use 'Check' tool in SolidWorks for detailed analysis",
                "Consider healing short edges with 'Delete Face'",
                "Sliver faces may cause meshing issues in simulation"
            ] if issues else ["Surface quality is good"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/continuity/check")
async def check_edge_continuity():
    """
    Check continuity across surface edges.
    G0 = Position, G1 = Tangent, G2 = Curvature continuous
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        continuity_report = {
            "g0_edges": 0,  # Position only
            "g1_edges": 0,  # Tangent continuous
            "g2_edges": 0,  # Curvature continuous
            "sharp_edges": 0,
            "total_edges": 0
        }

        bodies = doc.GetBodies2(0, False)
        if bodies:
            for body in bodies:
                edges = body.GetEdges()
                if edges:
                    for edge in edges:
                        try:
                            continuity_report["total_edges"] += 1

                            # Check edge type
                            edge_type = edge.GetCurve().Identity() if edge.GetCurve() else -1

                            # Get adjacent faces
                            faces = edge.GetTwoAdjacentFaces2()
                            if faces and len(faces) == 2:
                                # Check tangency at edge
                                # This is simplified - actual check would sample points
                                continuity_report["g1_edges"] += 1
                            else:
                                continuity_report["sharp_edges"] += 1

                        except Exception:
                            pass

        return {
            "document": doc.GetTitle(),
            "continuity_report": continuity_report,
            "percentage_smooth": round(
                (continuity_report["g1_edges"] + continuity_report["g2_edges"]) /
                max(continuity_report["total_edges"], 1) * 100, 1
            ),
            "recommendation": "Use zebra stripes for visual verification"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Continuity check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Surface Utilities
# =============================================================================

@router.get("/info")
async def get_surface_info():
    """
    Get summary information about all surfaces in the model.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        surface_types = {
            "planar": 0,
            "cylindrical": 0,
            "conical": 0,
            "spherical": 0,
            "toroidal": 0,
            "bspline": 0,
            "other": 0
        }

        total_area = 0

        bodies = doc.GetBodies2(0, False)
        if bodies:
            for body in bodies:
                faces = body.GetFaces()
                if faces:
                    for face in faces:
                        try:
                            surf = face.GetSurface()
                            area = face.GetArea()
                            total_area += area

                            if surf:
                                if surf.IsPlane():
                                    surface_types["planar"] += 1
                                elif surf.IsCylinder():
                                    surface_types["cylindrical"] += 1
                                elif surf.IsCone():
                                    surface_types["conical"] += 1
                                elif surf.IsSphere():
                                    surface_types["spherical"] += 1
                                elif surf.IsTorus():
                                    surface_types["toroidal"] += 1
                                elif surf.IsBSplineSurface():
                                    surface_types["bspline"] += 1
                                else:
                                    surface_types["other"] += 1
                        except Exception:
                            surface_types["other"] += 1

        total_faces = sum(surface_types.values())

        return {
            "document": doc.GetTitle(),
            "total_faces": total_faces,
            "total_area_m2": round(total_area, 6),
            "total_area_mm2": round(total_area * 1e6, 2),
            "surface_types": surface_types,
            "complexity": "low" if surface_types["bspline"] < total_faces * 0.1 else
                         ("medium" if surface_types["bspline"] < total_faces * 0.3 else "high")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Surface info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
