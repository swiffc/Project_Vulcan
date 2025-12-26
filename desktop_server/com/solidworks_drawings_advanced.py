"""
SolidWorks Advanced Drawing API
===============================
Complete drawing creation and modification including:
- Section/Detail/Projected/Auxiliary views
- Smart dimensions with full control
- Ordinate and baseline dimensions
- GD&T symbols and datum features
- Hole callouts and surface finish
- Weld symbols and annotations
- Auto-dimensioning and auto-balloon
- Break views and exploded views
"""

import logging
import math
from typing import Optional, Dict, Any, List, Tuple
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


# =============================================================================
# SolidWorks Drawing Constants
# =============================================================================

class swDrawingViewTypes(IntEnum):
    """Drawing view types."""
    STANDARD = 0
    SECTION = 1
    DETAIL = 2
    AUXILIARY = 3
    PROJECTED = 4
    RELATIVE = 5
    BROKEN = 6
    CROP = 7
    EXPLODED = 8
    ALTERNATE_POSITION = 9


class swDimensionType(IntEnum):
    """Dimension types."""
    LINEAR = 0
    ANGULAR = 1
    RADIAL = 2
    DIAMETER = 3
    ORDINATE = 4
    ARC_LENGTH = 5
    CHAMFER = 6


class swGTolType(IntEnum):
    """Geometric tolerance types."""
    STRAIGHTNESS = 0
    FLATNESS = 1
    CIRCULARITY = 2
    CYLINDRICITY = 3
    LINE_PROFILE = 4
    SURFACE_PROFILE = 5
    ANGULARITY = 6
    PERPENDICULARITY = 7
    PARALLELISM = 8
    POSITION = 9
    CONCENTRICITY = 10
    SYMMETRY = 11
    CIRCULAR_RUNOUT = 12
    TOTAL_RUNOUT = 13


class swSurfaceFinishSymbol(IntEnum):
    """Surface finish symbol types."""
    BASIC = 0
    MACHINED = 1
    PROHIBITED = 2
    REMOVAL_REQUIRED = 3
    REMOVAL_PROHIBITED = 4


class swWeldSymbolType(IntEnum):
    """Weld symbol types."""
    FILLET = 0
    PLUG = 1
    SPOT = 2
    SEAM = 3
    BACK = 4
    SURFACING = 5
    FLANGE_EDGE = 6
    FLANGE_CORNER = 7
    SQUARE = 8
    V_GROOVE = 9
    BEVEL = 10
    U_GROOVE = 11
    J_GROOVE = 12
    FLARE_V = 13
    FLARE_BEVEL = 14


# =============================================================================
# Pydantic Request Models
# =============================================================================

class SectionViewRequest(BaseModel):
    parent_view_name: str
    section_line_start: List[float]  # [x, y]
    section_line_end: List[float]  # [x, y]
    position_x: float
    position_y: float
    label: Optional[str] = "A"
    scale: Optional[float] = None
    aligned: bool = False  # Aligned or offset section
    partial: bool = False  # Partial section


class DetailViewRequest(BaseModel):
    parent_view_name: str
    center_x: float
    center_y: float
    radius: float
    position_x: float
    position_y: float
    label: Optional[str] = "A"
    scale: float = 2.0
    circle_style: str = "circle"  # circle, profile, connected, no_outline


class ProjectedViewRequest(BaseModel):
    parent_view_name: str
    direction: str  # up, down, left, right
    position_x: float
    position_y: float
    scale: Optional[float] = None


class AuxiliaryViewRequest(BaseModel):
    parent_view_name: str
    edge_name: str  # Edge to project from
    position_x: float
    position_y: float
    scale: Optional[float] = None


class BreakViewRequest(BaseModel):
    view_name: str
    break_line_style: str = "straight"  # straight, curved, zigzag
    gap_size: float = 10.0  # mm
    break_positions: List[float]  # Y positions for horizontal breaks


class ExplodedViewRequest(BaseModel):
    view_name: str
    configuration_name: Optional[str] = None


class SmartDimensionRequest(BaseModel):
    view_name: str
    entity1_type: str  # edge, vertex, face, silhouette
    entity1_coords: List[float]  # [x, y, z] or selection point
    entity2_type: Optional[str] = None
    entity2_coords: Optional[List[float]] = None
    dimension_position: List[float]  # [x, y] for dimension text
    dimension_type: str = "linear"  # linear, angular, radial, diameter
    value: Optional[float] = None  # Override value
    tolerance_type: Optional[str] = None  # none, bilateral, limit, fit
    upper_tolerance: Optional[float] = None
    lower_tolerance: Optional[float] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None


class OrdinateDimensionRequest(BaseModel):
    view_name: str
    origin_point: List[float]  # [x, y] datum origin
    points: List[List[float]]  # List of [x, y] points to dimension
    direction: str = "horizontal"  # horizontal or vertical
    jog_positions: Optional[List[float]] = None


class BaselineDimensionRequest(BaseModel):
    view_name: str
    baseline_edge: List[float]  # [x, y] baseline reference
    dimension_points: List[List[float]]  # Points to dimension from baseline
    direction: str = "horizontal"


class ChainDimensionRequest(BaseModel):
    view_name: str
    points: List[List[float]]  # Sequential points for chain
    direction: str = "horizontal"


class GDTRequest(BaseModel):
    view_name: str
    position: List[float]  # [x, y]
    tolerance_type: str  # position, flatness, perpendicularity, etc.
    tolerance_value: float
    material_condition: Optional[str] = None  # MMC, LMC, RFS
    datum_references: Optional[List[str]] = None  # ["A", "B", "C"]
    composite: bool = False
    secondary_tolerance: Optional[float] = None


class DatumFeatureRequest(BaseModel):
    view_name: str
    position: List[float]  # [x, y]
    datum_letter: str  # A, B, C, etc.
    triangle_filled: bool = True


class DatumTargetRequest(BaseModel):
    view_name: str
    position: List[float]
    datum_letter: str
    target_number: int  # A1, A2, etc.
    target_type: str = "point"  # point, line, area
    target_size: Optional[float] = None


class HoleCalloutRequest(BaseModel):
    view_name: str
    hole_edge_position: List[float]  # [x, y] on hole edge
    callout_position: List[float]  # [x, y] for text
    show_depth: bool = True
    show_thread: bool = True
    custom_text: Optional[str] = None


class SurfaceFinishRequest(BaseModel):
    view_name: str
    position: List[float]  # [x, y]
    symbol_type: str = "machined"  # basic, machined, prohibited
    roughness_value: Optional[float] = None  # Ra value
    production_method: Optional[str] = None
    lay_direction: Optional[str] = None
    sampling_length: Optional[float] = None


class WeldSymbolRequest(BaseModel):
    view_name: str
    position: List[float]  # [x, y]
    arrow_side_weld: str  # fillet, v_groove, etc.
    other_side_weld: Optional[str] = None
    arrow_side_size: Optional[float] = None
    other_side_size: Optional[float] = None
    arrow_side_length: Optional[float] = None
    field_weld: bool = False
    all_around: bool = False
    tail_text: Optional[str] = None


class AutoDimensionRequest(BaseModel):
    view_name: str
    horizontal: bool = True
    vertical: bool = True
    radial: bool = True
    diameter: bool = True
    chamfer: bool = True
    slot: bool = True
    hole_callout: bool = True
    ordinate: bool = False


class AutoBalloonRequest(BaseModel):
    view_name: str
    layout: str = "square"  # square, circular, top, bottom, left, right
    balloon_style: str = "circular"  # circular, triangle, hexagon, etc.
    include_sub_assemblies: bool = True
    resequence: bool = True


class CenterMarkPatternRequest(BaseModel):
    view_name: str
    center_point: List[float]  # [x, y]
    pattern_type: str = "circular"  # circular or linear
    count: int = 4
    spacing: Optional[float] = None
    angle_start: Optional[float] = 0
    connect_lines: bool = True


class DimensionStyleRequest(BaseModel):
    dimension_name: str
    text_height: Optional[float] = None
    arrow_style: Optional[str] = None  # solid, open, dot, tick
    arrow_size: Optional[float] = None
    dual_dimension: bool = False
    second_unit: Optional[str] = None  # mm, in
    precision: Optional[int] = None
    font_name: Optional[str] = None


class SketchOnDrawingRequest(BaseModel):
    view_name: Optional[str] = None  # None for sheet sketch
    sketch_entities: List[Dict[str, Any]]  # List of sketch entities to create


class BlockInsertRequest(BaseModel):
    block_path: str  # Path to block file
    position: List[float]  # [x, y]
    scale: float = 1.0
    angle: float = 0.0


router = APIRouter(prefix="/solidworks-drawings-advanced", tags=["solidworks-drawings-advanced"])


def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


def get_drawing_doc(sw):
    """Get active drawing document."""
    doc = sw.ActiveDoc
    if not doc:
        raise HTTPException(status_code=404, detail="No document open")
    if doc.GetType() != 3:  # swDocDRAWING
        raise HTTPException(status_code=400, detail="Active document is not a drawing")
    return doc


def get_view(drawing, view_name: str):
    """Get a drawing view by name."""
    sheet = drawing.GetCurrentSheet()
    views = sheet.GetViews()
    if views:
        for i in range(views.Count):
            view = views.Item(i)
            if view and view.Name == view_name:
                return view
    raise HTTPException(status_code=404, detail=f"View '{view_name}' not found")


# =============================================================================
# Section/Detail/Projected Views
# =============================================================================

@router.post("/view/section")
async def create_section_view(request: SectionViewRequest):
    """
    Create a section view from a parent view.

    Supports:
    - Full section (straight cut)
    - Aligned section (follows geometry)
    - Partial/broken-out section
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        # Activate parent view
        drawing.ActivateView(request.parent_view_name)

        # Create section line
        sm = drawing.SketchManager
        sm.InsertSketch(True)

        # Draw section line
        x1, y1 = request.section_line_start
        x2, y2 = request.section_line_end
        sm.CreateLine(x1/1000, y1/1000, 0, x2/1000, y2/1000, 0)

        sm.InsertSketch(False)

        # Create section view
        # swSectionViewStyle: 0=Default, 1=Aligned, 2=Half
        section_style = 1 if request.aligned else 0

        view = drawing.CreateSectionView(
            request.position_x / 1000,
            request.position_y / 1000,
            section_style
        )

        if view and request.label:
            view.SetName2(f"SECTION {request.label}-{request.label}")

        if view and request.scale:
            view.ScaleRatio = (1.0, request.scale)

        drawing.ClearSelection2(True)

        return {
            "success": view is not None,
            "parent_view": request.parent_view_name,
            "section_label": request.label,
            "aligned": request.aligned,
            "message": f"Section view {request.label}-{request.label} created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create section view failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/view/detail")
async def create_detail_view(request: DetailViewRequest):
    """
    Create a detail view (magnified circular area).

    circle_style options:
    - circle: Standard circle outline
    - profile: Follows part profile
    - connected: Connected to parent
    - no_outline: No circle shown on parent
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        # Activate parent view
        drawing.ActivateView(request.parent_view_name)

        # Create detail circle
        sm = drawing.SketchManager
        sm.InsertSketch(True)

        # Draw circle for detail area
        sm.CreateCircle(
            request.center_x / 1000,
            request.center_y / 1000,
            0,
            (request.center_x + request.radius) / 1000,
            request.center_y / 1000,
            0
        )

        sm.InsertSketch(False)

        # Create detail view
        # Circle style mapping
        style_map = {
            "circle": 0,
            "profile": 1,
            "connected": 2,
            "no_outline": 3
        }
        circle_style = style_map.get(request.circle_style, 0)

        view = drawing.CreateDetailView(
            request.position_x / 1000,
            request.position_y / 1000,
            circle_style
        )

        if view:
            view.SetName2(f"DETAIL {request.label}")
            view.ScaleRatio = (request.scale, 1.0)

        drawing.ClearSelection2(True)

        return {
            "success": view is not None,
            "parent_view": request.parent_view_name,
            "detail_label": request.label,
            "scale": f"{request.scale}:1",
            "message": f"Detail view {request.label} created at {request.scale}:1 scale"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create detail view failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/view/projected")
async def create_projected_view(request: ProjectedViewRequest):
    """
    Create an orthographic projected view from parent view.

    direction: up, down, left, right
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        # Activate parent view
        parent_view = get_view(drawing, request.parent_view_name)
        drawing.ActivateView(request.parent_view_name)

        # Select the view
        drawing.Extension.SelectByID2(
            request.parent_view_name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0
        )

        # Direction offsets
        directions = {
            "up": (0, 0.1),
            "down": (0, -0.1),
            "left": (-0.1, 0),
            "right": (0.1, 0)
        }
        dx, dy = directions.get(request.direction.lower(), (0.1, 0))

        # Create projected view using InsertProjectedView
        view = drawing.CreateUnfoldedViewAt3(
            request.position_x / 1000,
            request.position_y / 1000,
            0,  # Angle
            True  # Hide bend lines
        )

        if not view:
            # Try alternative method
            drawing.ActivateView(request.parent_view_name)
            # Create view manually at offset position
            parent_pos = parent_view.Position
            view = drawing.CreateDrawViewFromModelView3(
                parent_view.ReferencedDocument.GetPathName(),
                parent_view.GetOrientationName(),
                request.position_x / 1000,
                request.position_y / 1000
            )

        if view and request.scale:
            view.ScaleRatio = (1.0, request.scale)

        drawing.ClearSelection2(True)

        return {
            "success": view is not None,
            "parent_view": request.parent_view_name,
            "direction": request.direction,
            "message": f"Projected view created {request.direction} of parent"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create projected view failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/view/auxiliary")
async def create_auxiliary_view(request: AuxiliaryViewRequest):
    """Create an auxiliary view projected from an angled edge."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        # Activate parent view
        drawing.ActivateView(request.parent_view_name)

        # Select edge
        drawing.Extension.SelectByID2(
            request.edge_name, "EDGE", 0, 0, 0, False, 0, None, 0
        )

        # Create auxiliary view
        view = drawing.CreateAuxiliaryView(
            request.position_x / 1000,
            request.position_y / 1000
        )

        if view and request.scale:
            view.ScaleRatio = (1.0, request.scale)

        drawing.ClearSelection2(True)

        return {
            "success": view is not None,
            "parent_view": request.parent_view_name,
            "message": "Auxiliary view created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create auxiliary view failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/view/break")
async def create_break_view(request: BreakViewRequest):
    """Add break lines to a view to shorten long parts."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        view = get_view(drawing, request.view_name)
        drawing.ActivateView(request.view_name)

        # Break line style mapping
        style_map = {
            "straight": 0,
            "curved": 1,
            "zigzag": 2
        }
        style = style_map.get(request.break_line_style.lower(), 0)

        # Insert break lines at each position
        for pos in request.break_positions:
            drawing.InsertBreakHorizontal(
                pos / 1000,
                request.gap_size / 1000,
                style
            )

        return {
            "success": True,
            "view": request.view_name,
            "breaks": len(request.break_positions),
            "style": request.break_line_style,
            "message": f"Added {len(request.break_positions)} break lines"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create break view failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Smart Dimensions
# =============================================================================

@router.post("/dimension/smart")
async def add_smart_dimension(request: SmartDimensionRequest):
    """
    Add a smart dimension between entities.

    Supports linear, angular, radial, and diameter dimensions
    with full tolerance and text control.
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select first entity
        drawing.Extension.SelectByID2(
            "", request.entity1_type.upper(),
            request.entity1_coords[0] / 1000,
            request.entity1_coords[1] / 1000,
            request.entity1_coords[2] / 1000 if len(request.entity1_coords) > 2 else 0,
            False, 0, None, 0
        )

        # Select second entity if provided
        if request.entity2_type and request.entity2_coords:
            drawing.Extension.SelectByID2(
                "", request.entity2_type.upper(),
                request.entity2_coords[0] / 1000,
                request.entity2_coords[1] / 1000,
                request.entity2_coords[2] / 1000 if len(request.entity2_coords) > 2 else 0,
                True, 0, None, 0
            )

        # Add dimension at position
        dim = drawing.AddDimension2(
            request.dimension_position[0] / 1000,
            request.dimension_position[1] / 1000,
            0
        )

        if dim:
            # Get dimension object
            dim_obj = dim.GetDimension2(0)

            # Set value if provided
            if request.value is not None:
                dim_obj.SystemValue = request.value / 1000  # Convert mm to m

            # Set tolerances
            if request.tolerance_type:
                tol_map = {
                    "none": 0,
                    "bilateral": 1,
                    "limit": 2,
                    "symmetric": 3,
                    "fit": 4
                }
                tol_type = tol_map.get(request.tolerance_type.lower(), 0)
                dim_obj.ToleranceType = tol_type

                if request.upper_tolerance is not None:
                    dim_obj.SetTolerance(0, request.upper_tolerance / 1000)
                if request.lower_tolerance is not None:
                    dim_obj.SetTolerance(1, request.lower_tolerance / 1000)

            # Set prefix/suffix
            if request.prefix:
                dim_obj.Prefix = request.prefix
            if request.suffix:
                dim_obj.Suffix = request.suffix

        drawing.ClearSelection2(True)

        return {
            "success": dim is not None,
            "view": request.view_name,
            "dimension_type": request.dimension_type,
            "value": request.value,
            "message": "Smart dimension added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add smart dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/ordinate")
async def add_ordinate_dimensions(request: OrdinateDimensionRequest):
    """
    Add ordinate dimensions from a datum origin.

    Creates a series of dimensions measured from a single datum point,
    commonly used for hole patterns and precision features.
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select origin point
        drawing.Extension.SelectByID2(
            "", "VERTEX",
            request.origin_point[0] / 1000,
            request.origin_point[1] / 1000,
            0, False, 0, None, 0
        )

        # Create ordinate dimension at origin (this becomes 0 reference)
        is_horizontal = request.direction.lower() == "horizontal"

        origin_dim = drawing.AddOrdinateDimension(
            request.origin_point[0] / 1000,
            request.origin_point[1] / 1000,
            0
        )

        dims_created = 1 if origin_dim else 0

        # Add dimensions for each point
        for point in request.points:
            drawing.Extension.SelectByID2(
                "", "VERTEX",
                point[0] / 1000,
                point[1] / 1000,
                0, False, 0, None, 0
            )

            dim = drawing.AddOrdinateDimension(
                point[0] / 1000,
                point[1] / 1000,
                0
            )

            if dim:
                dims_created += 1

        drawing.ClearSelection2(True)

        return {
            "success": dims_created > 0,
            "view": request.view_name,
            "dimensions_created": dims_created,
            "direction": request.direction,
            "message": f"Created {dims_created} ordinate dimensions"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add ordinate dimensions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/baseline")
async def add_baseline_dimensions(request: BaselineDimensionRequest):
    """Add baseline (parallel) dimensions from a common baseline."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        dims_created = 0

        for point in request.dimension_points:
            # Select baseline
            drawing.Extension.SelectByID2(
                "", "EDGE",
                request.baseline_edge[0] / 1000,
                request.baseline_edge[1] / 1000,
                0, False, 0, None, 0
            )

            # Select target point
            drawing.Extension.SelectByID2(
                "", "VERTEX",
                point[0] / 1000,
                point[1] / 1000,
                0, True, 0, None, 0
            )

            # Calculate dimension position
            if request.direction.lower() == "horizontal":
                dim_pos_x = (request.baseline_edge[0] + point[0]) / 2
                dim_pos_y = point[1] + 10 + (dims_created * 8)
            else:
                dim_pos_x = point[0] + 10 + (dims_created * 8)
                dim_pos_y = (request.baseline_edge[1] + point[1]) / 2

            dim = drawing.AddDimension2(dim_pos_x / 1000, dim_pos_y / 1000, 0)
            if dim:
                dims_created += 1

        drawing.ClearSelection2(True)

        return {
            "success": dims_created > 0,
            "view": request.view_name,
            "dimensions_created": dims_created,
            "message": f"Created {dims_created} baseline dimensions"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add baseline dimensions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/chain")
async def add_chain_dimensions(request: ChainDimensionRequest):
    """Add chain dimensions (sequential point-to-point)."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        dims_created = 0

        for i in range(len(request.points) - 1):
            pt1 = request.points[i]
            pt2 = request.points[i + 1]

            # Select first point
            drawing.Extension.SelectByID2(
                "", "VERTEX",
                pt1[0] / 1000, pt1[1] / 1000, 0,
                False, 0, None, 0
            )

            # Select second point
            drawing.Extension.SelectByID2(
                "", "VERTEX",
                pt2[0] / 1000, pt2[1] / 1000, 0,
                True, 0, None, 0
            )

            # Calculate dimension position
            if request.direction.lower() == "horizontal":
                dim_pos_x = (pt1[0] + pt2[0]) / 2
                dim_pos_y = pt1[1] + 15
            else:
                dim_pos_x = pt1[0] + 15
                dim_pos_y = (pt1[1] + pt2[1]) / 2

            dim = drawing.AddDimension2(dim_pos_x / 1000, dim_pos_y / 1000, 0)
            if dim:
                dims_created += 1

        drawing.ClearSelection2(True)

        return {
            "success": dims_created > 0,
            "view": request.view_name,
            "dimensions_created": dims_created,
            "message": f"Created {dims_created} chain dimensions"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add chain dimensions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# GD&T and Annotations
# =============================================================================

@router.post("/annotation/gdt")
async def add_geometric_tolerance(request: GDTRequest):
    """
    Add a geometric tolerance (GD&T) symbol.

    tolerance_type options:
    - position, flatness, perpendicularity, parallelism
    - circularity, cylindricity, straightness
    - profile_line, profile_surface
    - angularity, concentricity, symmetry
    - circular_runout, total_runout
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Map tolerance type
        type_map = {
            "position": 9,
            "flatness": 1,
            "perpendicularity": 7,
            "parallelism": 8,
            "circularity": 2,
            "cylindricity": 3,
            "straightness": 0,
            "profile_line": 4,
            "profile_surface": 5,
            "angularity": 6,
            "concentricity": 10,
            "symmetry": 11,
            "circular_runout": 12,
            "total_runout": 13
        }
        gtol_type = type_map.get(request.tolerance_type.lower(), 9)

        # Material condition
        mc_map = {
            "MMC": 0,  # Maximum Material Condition
            "LMC": 1,  # Least Material Condition
            "RFS": 2   # Regardless of Feature Size
        }

        # Create GD&T frame
        gtol = drawing.InsertGtol()

        if gtol:
            # Set tolerance type and value
            gtol.SetFrameSymbol(0, gtol_type)
            gtol.SetFrameValue(0, 0, request.tolerance_value)

            # Set material condition
            if request.material_condition:
                mc = mc_map.get(request.material_condition.upper(), 2)
                gtol.SetFrameModifier(0, 0, mc)

            # Set datum references
            if request.datum_references:
                for i, datum in enumerate(request.datum_references[:3]):
                    gtol.SetFrameDatumRef(0, i, datum)

            # Position the symbol
            gtol.SetPosition(
                request.position[0] / 1000,
                request.position[1] / 1000,
                0
            )

        drawing.ClearSelection2(True)

        return {
            "success": gtol is not None,
            "view": request.view_name,
            "tolerance_type": request.tolerance_type,
            "value": request.tolerance_value,
            "datums": request.datum_references,
            "message": f"GD&T symbol ({request.tolerance_type}) added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add GD&T failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/annotation/datum-feature")
async def add_datum_feature(request: DatumFeatureRequest):
    """Add a datum feature symbol (datum identifier)."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Insert datum feature symbol
        datum = drawing.InsertDatumFeatureSymbol()

        if datum:
            datum.SetText(request.datum_letter)
            datum.SetPosition(
                request.position[0] / 1000,
                request.position[1] / 1000,
                0
            )
            # Set filled vs open triangle
            if hasattr(datum, 'SetFilledTriangle'):
                datum.SetFilledTriangle(request.triangle_filled)

        drawing.ClearSelection2(True)

        return {
            "success": datum is not None,
            "view": request.view_name,
            "datum": request.datum_letter,
            "message": f"Datum feature {request.datum_letter} added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add datum feature failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/annotation/datum-target")
async def add_datum_target(request: DatumTargetRequest):
    """Add a datum target symbol."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Target type mapping
        type_map = {
            "point": 0,
            "line": 1,
            "area": 2
        }
        target_type = type_map.get(request.target_type.lower(), 0)

        # Insert datum target
        target = drawing.InsertDatumTargetSymbol(
            target_type,
            request.target_size / 1000 if request.target_size else 0
        )

        if target:
            target.SetDatumLetter(request.datum_letter)
            target.SetTargetNumber(request.target_number)
            target.SetPosition(
                request.position[0] / 1000,
                request.position[1] / 1000,
                0
            )

        drawing.ClearSelection2(True)

        return {
            "success": target is not None,
            "view": request.view_name,
            "datum_target": f"{request.datum_letter}{request.target_number}",
            "type": request.target_type,
            "message": f"Datum target {request.datum_letter}{request.target_number} added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add datum target failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/annotation/hole-callout")
async def add_hole_callout(request: HoleCalloutRequest):
    """
    Add a hole callout annotation.

    Automatically detects hole type (simple, counterbore, countersink, tapped)
    and creates appropriate callout text.
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select hole edge
        drawing.Extension.SelectByID2(
            "", "EDGE",
            request.hole_edge_position[0] / 1000,
            request.hole_edge_position[1] / 1000,
            0, False, 0, None, 0
        )

        # Insert hole callout
        callout = drawing.InsertHoleCallout()

        if callout:
            # Position the callout
            callout.SetPosition(
                request.callout_position[0] / 1000,
                request.callout_position[1] / 1000,
                0
            )

            # Custom text override
            if request.custom_text:
                callout.SetText(request.custom_text)

        drawing.ClearSelection2(True)

        return {
            "success": callout is not None,
            "view": request.view_name,
            "show_depth": request.show_depth,
            "show_thread": request.show_thread,
            "message": "Hole callout added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add hole callout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/annotation/surface-finish")
async def add_surface_finish(request: SurfaceFinishRequest):
    """
    Add a surface finish symbol.

    symbol_type options:
    - basic: Basic symbol (any process)
    - machined: Material removal required
    - prohibited: Material removal prohibited
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Symbol type mapping
        symbol_map = {
            "basic": 0,
            "machined": 1,
            "prohibited": 2,
            "removal_required": 3,
            "removal_prohibited": 4
        }
        symbol_type = symbol_map.get(request.symbol_type.lower(), 0)

        # Insert surface finish symbol
        sf = drawing.InsertSurfaceFinishSymbol(symbol_type)

        if sf:
            sf.SetPosition(
                request.position[0] / 1000,
                request.position[1] / 1000,
                0
            )

            if request.roughness_value is not None:
                sf.SetRoughnessValue(request.roughness_value)

            if request.production_method:
                sf.SetProductionMethod(request.production_method)

            if request.lay_direction:
                sf.SetLayDirection(request.lay_direction)

        drawing.ClearSelection2(True)

        return {
            "success": sf is not None,
            "view": request.view_name,
            "symbol_type": request.symbol_type,
            "roughness": request.roughness_value,
            "message": "Surface finish symbol added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add surface finish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/annotation/weld-symbol")
async def add_weld_symbol(request: WeldSymbolRequest):
    """
    Add a weld symbol.

    Supports all standard weld types with arrow/other side,
    field weld, and all-around indicators.
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Weld type mapping
        weld_map = {
            "fillet": 0,
            "plug": 1,
            "spot": 2,
            "seam": 3,
            "back": 4,
            "surfacing": 5,
            "square": 8,
            "v_groove": 9,
            "bevel": 10,
            "u_groove": 11,
            "j_groove": 12
        }

        arrow_weld = weld_map.get(request.arrow_side_weld.lower(), 0)
        other_weld = weld_map.get(request.other_side_weld.lower(), -1) if request.other_side_weld else -1

        # Insert weld symbol
        weld = drawing.InsertWeldSymbol()

        if weld:
            weld.SetArrowSideWeld(arrow_weld)
            if other_weld >= 0:
                weld.SetOtherSideWeld(other_weld)

            if request.arrow_side_size:
                weld.SetArrowSideSize(request.arrow_side_size)
            if request.other_side_size:
                weld.SetOtherSideSize(request.other_side_size)
            if request.arrow_side_length:
                weld.SetArrowSideLength(request.arrow_side_length)

            weld.SetFieldWeld(request.field_weld)
            weld.SetAllAround(request.all_around)

            if request.tail_text:
                weld.SetTailText(request.tail_text)

            weld.SetPosition(
                request.position[0] / 1000,
                request.position[1] / 1000,
                0
            )

        drawing.ClearSelection2(True)

        return {
            "success": weld is not None,
            "view": request.view_name,
            "arrow_weld": request.arrow_side_weld,
            "other_weld": request.other_side_weld,
            "field_weld": request.field_weld,
            "all_around": request.all_around,
            "message": "Weld symbol added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add weld symbol failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Auto Dimensioning and Auto Balloon
# =============================================================================

@router.post("/auto-dimension")
async def auto_dimension_view(request: AutoDimensionRequest):
    """
    Automatically add dimensions to a view.

    Uses SolidWorks' DimXpert/Auto Dimension feature
    to intelligently place dimensions.
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        view = get_view(drawing, request.view_name)
        drawing.ActivateView(request.view_name)

        # Select the view
        drawing.Extension.SelectByID2(
            request.view_name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0
        )

        # Build options flags
        options = 0
        if request.horizontal:
            options |= 1
        if request.vertical:
            options |= 2
        if request.radial:
            options |= 4
        if request.diameter:
            options |= 8
        if request.chamfer:
            options |= 16
        if request.slot:
            options |= 32
        if request.hole_callout:
            options |= 64
        if request.ordinate:
            options |= 128

        # Auto-dimension the view
        dims_added = drawing.AutoDimension(options)

        drawing.ClearSelection2(True)

        return {
            "success": True,
            "view": request.view_name,
            "dimensions_added": dims_added if dims_added else "Auto-dimension applied",
            "options": {
                "horizontal": request.horizontal,
                "vertical": request.vertical,
                "radial": request.radial,
                "diameter": request.diameter,
                "chamfer": request.chamfer,
                "hole_callout": request.hole_callout,
                "ordinate": request.ordinate
            },
            "message": "Auto-dimensioning complete"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/auto-balloon")
async def auto_balloon_view(request: AutoBalloonRequest):
    """
    Automatically add balloons to an assembly view.

    layout options:
    - square: Square layout around view
    - circular: Radial layout
    - top, bottom, left, right: Single side layout
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        view = get_view(drawing, request.view_name)
        drawing.ActivateView(request.view_name)

        # Select the view
        drawing.Extension.SelectByID2(
            request.view_name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0
        )

        # Layout mapping
        layout_map = {
            "square": 0,
            "circular": 1,
            "top": 2,
            "bottom": 3,
            "left": 4,
            "right": 5
        }
        layout = layout_map.get(request.layout.lower(), 0)

        # Balloon style mapping
        style_map = {
            "circular": 0,
            "triangle": 1,
            "hexagon": 2,
            "box": 3,
            "diamond": 4,
            "flag": 5
        }
        style = style_map.get(request.balloon_style.lower(), 0)

        # Auto-balloon
        balloons = drawing.AutoBalloon(
            layout,
            style,
            request.include_sub_assemblies
        )

        # Resequence if requested
        if request.resequence:
            drawing.ResequenceBalloons()

        drawing.ClearSelection2(True)

        return {
            "success": True,
            "view": request.view_name,
            "balloons_added": balloons if balloons else "Auto-balloon applied",
            "layout": request.layout,
            "style": request.balloon_style,
            "resequenced": request.resequence,
            "message": "Auto-ballooning complete"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-balloon failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Center Marks and Centerlines
# =============================================================================

@router.post("/centermark/pattern")
async def add_centermark_pattern(request: CenterMarkPatternRequest):
    """Add center marks to a hole pattern (circular or linear)."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        marks_created = 0

        if request.pattern_type.lower() == "circular":
            # Create circular pattern of center marks
            angle_step = 360.0 / request.count
            radius = request.spacing or 50

            for i in range(request.count):
                angle = math.radians(request.angle_start + i * angle_step)
                x = request.center_point[0] + radius * math.cos(angle)
                y = request.center_point[1] + radius * math.sin(angle)

                # Insert center mark
                mark = drawing.InsertCenterMark2(x / 1000, y / 1000, 0)
                if mark:
                    marks_created += 1

            # Add connecting lines if requested
            if request.connect_lines and marks_created > 1:
                drawing.InsertCenterLinePattern()

        else:  # Linear pattern
            spacing = request.spacing or 25
            for i in range(request.count):
                x = request.center_point[0] + i * spacing
                y = request.center_point[1]

                mark = drawing.InsertCenterMark2(x / 1000, y / 1000, 0)
                if mark:
                    marks_created += 1

        drawing.ClearSelection2(True)

        return {
            "success": marks_created > 0,
            "view": request.view_name,
            "marks_created": marks_created,
            "pattern_type": request.pattern_type,
            "message": f"Created {marks_created} center marks"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add centermark pattern failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Drawing Utilities
# =============================================================================

@router.get("/views")
async def list_drawing_views():
    """List all views in the current drawing."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        sheet = drawing.GetCurrentSheet()
        views_list = []

        views = sheet.GetViews()
        if views:
            for i in range(views.Count):
                view = views.Item(i)
                if view:
                    view_info = {
                        "name": view.Name,
                        "type": view.GetType2(),
                        "scale": view.ScaleRatio,
                        "position": list(view.Position) if view.Position else None,
                    }
                    # Get referenced document if available
                    try:
                        ref_doc = view.ReferencedDocument
                        if ref_doc:
                            view_info["referenced_model"] = ref_doc.GetPathName()
                    except:
                        pass

                    views_list.append(view_info)

        return {
            "sheet": sheet.GetName(),
            "view_count": len(views_list),
            "views": views_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List views failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/dimensions")
async def list_drawing_dimensions(view_name: Optional[str] = None):
    """List all dimensions in the drawing or specific view."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        dims_list = []

        # Get all annotations
        if view_name:
            drawing.ActivateView(view_name)

        # Traverse features looking for dimensions
        feature = drawing.FirstFeature()
        while feature:
            if "Dimension" in feature.GetTypeName2():
                dim_display = feature.GetDisplayDimension()
                if dim_display:
                    dim = dim_display.GetDimension2(0)
                    if dim:
                        dims_list.append({
                            "name": dim.FullName,
                            "value": dim.SystemValue * 1000,  # Convert to mm
                            "type": dim.Type,
                            "tolerance_type": dim.ToleranceType
                        })
            feature = feature.GetNextFeature()

        return {
            "view": view_name or "all",
            "dimension_count": len(dims_list),
            "dimensions": dims_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List dimensions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/modify")
async def modify_dimension(dimension_name: str, new_value: Optional[float] = None,
                          prefix: Optional[str] = None, suffix: Optional[str] = None,
                          tolerance_type: Optional[str] = None,
                          upper_tol: Optional[float] = None,
                          lower_tol: Optional[float] = None):
    """Modify an existing dimension's value, text, or tolerances."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        # Find and select dimension
        drawing.Extension.SelectByID2(
            dimension_name, "DIMENSION", 0, 0, 0, False, 0, None, 0
        )

        sel_mgr = drawing.SelectionManager
        if sel_mgr.GetSelectedObjectCount2(-1) == 0:
            raise HTTPException(status_code=404, detail=f"Dimension '{dimension_name}' not found")

        dim_display = sel_mgr.GetSelectedObject6(1, -1)
        dim = dim_display.GetDimension2(0)

        if new_value is not None:
            dim.SystemValue = new_value / 1000

        if prefix is not None:
            dim.Prefix = prefix

        if suffix is not None:
            dim.Suffix = suffix

        if tolerance_type:
            tol_map = {
                "none": 0,
                "bilateral": 1,
                "limit": 2,
                "symmetric": 3,
                "fit": 4
            }
            dim.ToleranceType = tol_map.get(tolerance_type.lower(), 0)

        if upper_tol is not None:
            dim.SetTolerance(0, upper_tol / 1000)
        if lower_tol is not None:
            dim.SetTolerance(1, lower_tol / 1000)

        drawing.EditRebuild3()
        drawing.ClearSelection2(True)

        return {
            "success": True,
            "dimension": dimension_name,
            "new_value": new_value,
            "message": "Dimension modified"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Modify dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/dimension/{dimension_name}")
async def delete_dimension(dimension_name: str):
    """Delete a dimension from the drawing."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.Extension.SelectByID2(
            dimension_name, "DIMENSION", 0, 0, 0, False, 0, None, 0
        )

        drawing.EditDelete()

        return {
            "success": True,
            "deleted": dimension_name,
            "message": f"Dimension '{dimension_name}' deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Additional View Types
# =============================================================================

class BrokenOutSectionRequest(BaseModel):
    view_name: str
    spline_points: List[List[float]]  # Points defining the boundary
    depth: float  # Depth of break-out in mm


class CropViewRequest(BaseModel):
    view_name: str
    crop_points: List[List[float]]  # Points defining crop boundary


class AlternatePositionRequest(BaseModel):
    view_name: str
    configuration_name: str
    show_original: bool = True


@router.post("/view/broken-out-section")
async def create_broken_out_section(request: BrokenOutSectionRequest):
    """
    Create a broken-out section in a view.
    Shows internal details without creating a separate section view.
    """
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Create spline sketch for boundary
        sm = drawing.SketchManager
        sm.InsertSketch(True)

        # Create closed spline from points
        points = []
        for pt in request.spline_points:
            points.extend([pt[0] / 1000, pt[1] / 1000, 0])

        sm.CreateSpline(points)
        sm.InsertSketch(False)

        # Create broken-out section
        section = drawing.InsertBrokenOutSection(
            request.depth / 1000  # Depth in meters
        )

        drawing.ClearSelection2(True)

        return {
            "success": section is not None,
            "view": request.view_name,
            "depth_mm": request.depth,
            "message": "Broken-out section created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create broken-out section failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/view/crop")
async def crop_view(request: CropViewRequest):
    """Crop a view to show only a specific region."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Create sketch for crop boundary
        sm = drawing.SketchManager
        sm.InsertSketch(True)

        # Create closed polygon
        for i in range(len(request.crop_points)):
            pt1 = request.crop_points[i]
            pt2 = request.crop_points[(i + 1) % len(request.crop_points)]
            sm.CreateLine(
                pt1[0] / 1000, pt1[1] / 1000, 0,
                pt2[0] / 1000, pt2[1] / 1000, 0
            )

        sm.InsertSketch(False)

        # Apply crop
        drawing.CropView()

        drawing.ClearSelection2(True)

        return {
            "success": True,
            "view": request.view_name,
            "message": "View cropped"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Crop view failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/view/alternate-position")
async def create_alternate_position_view(request: AlternatePositionRequest):
    """Create an alternate position view showing different configuration."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        view = get_view(drawing, request.view_name)
        drawing.ActivateView(request.view_name)

        # Create alternate position
        alt_view = drawing.CreateAlternatePositionView(
            request.configuration_name,
            request.show_original
        )

        drawing.ClearSelection2(True)

        return {
            "success": alt_view is not None,
            "view": request.view_name,
            "configuration": request.configuration_name,
            "message": "Alternate position view created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create alternate position failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Additional Dimension Types
# =============================================================================

class AngularDimensionRequest(BaseModel):
    view_name: str
    line1_start: List[float]
    line1_end: List[float]
    line2_start: List[float]
    line2_end: List[float]
    dimension_position: List[float]


class ArcLengthDimensionRequest(BaseModel):
    view_name: str
    arc_position: List[float]  # Point on the arc
    dimension_position: List[float]


class ChamferDimensionRequest(BaseModel):
    view_name: str
    chamfer_edge_position: List[float]
    dimension_position: List[float]
    format: str = "distance_x_angle"  # distance_x_angle, distance_x_distance


@router.post("/dimension/angular")
async def add_angular_dimension(request: AngularDimensionRequest):
    """Add an angular dimension between two lines."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select first line
        drawing.Extension.SelectByID2(
            "", "EDGE",
            request.line1_start[0] / 1000,
            request.line1_start[1] / 1000,
            0, False, 0, None, 0
        )

        # Select second line
        drawing.Extension.SelectByID2(
            "", "EDGE",
            request.line2_start[0] / 1000,
            request.line2_start[1] / 1000,
            0, True, 0, None, 0
        )

        # Add angular dimension
        dim = drawing.AddDimension2(
            request.dimension_position[0] / 1000,
            request.dimension_position[1] / 1000,
            0
        )

        drawing.ClearSelection2(True)

        return {
            "success": dim is not None,
            "view": request.view_name,
            "type": "angular",
            "message": "Angular dimension added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add angular dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/arc-length")
async def add_arc_length_dimension(request: ArcLengthDimensionRequest):
    """Add an arc length dimension."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select arc
        drawing.Extension.SelectByID2(
            "", "EDGE",
            request.arc_position[0] / 1000,
            request.arc_position[1] / 1000,
            0, False, 0, None, 0
        )

        # Add arc length dimension
        dim = drawing.AddArcLengthDimension(
            request.dimension_position[0] / 1000,
            request.dimension_position[1] / 1000,
            0
        )

        drawing.ClearSelection2(True)

        return {
            "success": dim is not None,
            "view": request.view_name,
            "type": "arc_length",
            "message": "Arc length dimension added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add arc length dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/dimension/chamfer")
async def add_chamfer_dimension(request: ChamferDimensionRequest):
    """Add a chamfer dimension."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select chamfer edge
        drawing.Extension.SelectByID2(
            "", "EDGE",
            request.chamfer_edge_position[0] / 1000,
            request.chamfer_edge_position[1] / 1000,
            0, False, 0, None, 0
        )

        # Add chamfer dimension
        format_map = {
            "distance_x_angle": 0,
            "distance_x_distance": 1
        }
        fmt = format_map.get(request.format, 0)

        dim = drawing.AddChamferDimension(
            request.dimension_position[0] / 1000,
            request.dimension_position[1] / 1000,
            0,
            fmt
        )

        drawing.ClearSelection2(True)

        return {
            "success": dim is not None,
            "view": request.view_name,
            "type": "chamfer",
            "format": request.format,
            "message": "Chamfer dimension added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add chamfer dimension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Tables
# =============================================================================

class HoleTableRequest(BaseModel):
    view_name: str
    origin_position: List[float]  # Datum origin
    table_position: List[float]  # Where to place table
    tag_holes: bool = True


class BendTableRequest(BaseModel):
    view_name: str
    table_position: List[float]


class WeldmentCutListRequest(BaseModel):
    view_name: str
    table_position: List[float]


@router.post("/table/hole")
async def insert_hole_table(request: HoleTableRequest):
    """Insert a hole table showing hole positions from a datum."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select origin point
        drawing.Extension.SelectByID2(
            "", "VERTEX",
            request.origin_position[0] / 1000,
            request.origin_position[1] / 1000,
            0, False, 0, None, 0
        )

        # Insert hole table
        table = drawing.InsertHoleTable2(
            True,  # Use origin
            request.table_position[0] / 1000,
            request.table_position[1] / 1000,
            1,  # Anchor type
            request.tag_holes
        )

        drawing.ClearSelection2(True)

        return {
            "success": table is not None,
            "view": request.view_name,
            "table_type": "hole",
            "message": "Hole table inserted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Insert hole table failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/table/bend")
async def insert_bend_table(request: BendTableRequest):
    """Insert a bend table for sheet metal parts."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select the view
        drawing.Extension.SelectByID2(
            request.view_name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0
        )

        # Insert bend table
        table = drawing.InsertBendTable(
            True,
            request.table_position[0] / 1000,
            request.table_position[1] / 1000,
            1,  # Anchor type
            ""  # Template
        )

        drawing.ClearSelection2(True)

        return {
            "success": table is not None,
            "view": request.view_name,
            "table_type": "bend",
            "message": "Bend table inserted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Insert bend table failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/table/weldment-cutlist")
async def insert_weldment_cutlist(request: WeldmentCutListRequest):
    """Insert a weldment cut list table."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select the view
        drawing.Extension.SelectByID2(
            request.view_name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0
        )

        # Insert weldment cut list
        table = drawing.InsertWeldmentTable(
            True,
            request.table_position[0] / 1000,
            request.table_position[1] / 1000,
            1,  # Anchor type
            ""  # Template
        )

        drawing.ClearSelection2(True)

        return {
            "success": table is not None,
            "view": request.view_name,
            "table_type": "weldment_cutlist",
            "message": "Weldment cut list inserted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Insert weldment cut list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Additional Annotations
# =============================================================================

class CosmeticThreadRequest(BaseModel):
    view_name: str
    edge_position: List[float]  # Point on hole edge
    thread_standard: str = "ANSI Inch"  # ANSI Inch, ANSI Metric, ISO, etc.
    thread_size: Optional[str] = None  # e.g., "1/4-20", "M6x1"


class DowelPinSymbolRequest(BaseModel):
    view_name: str
    position: List[float]
    diameter: float


class MultiJogLeaderRequest(BaseModel):
    view_name: str
    points: List[List[float]]  # Leader line points
    text: str
    arrow_style: str = "solid"


@router.post("/annotation/cosmetic-thread")
async def add_cosmetic_thread(request: CosmeticThreadRequest):
    """Add a cosmetic thread annotation to a hole."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Select hole edge
        drawing.Extension.SelectByID2(
            "", "EDGE",
            request.edge_position[0] / 1000,
            request.edge_position[1] / 1000,
            0, False, 0, None, 0
        )

        # Insert cosmetic thread
        thread = drawing.InsertCosmeticThread(
            request.thread_standard,
            request.thread_size or ""
        )

        drawing.ClearSelection2(True)

        return {
            "success": thread is not None,
            "view": request.view_name,
            "standard": request.thread_standard,
            "size": request.thread_size,
            "message": "Cosmetic thread added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add cosmetic thread failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/annotation/dowel-pin")
async def add_dowel_pin_symbol(request: DowelPinSymbolRequest):
    """Add a dowel pin symbol."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Insert dowel pin symbol
        symbol = drawing.InsertDowelSymbol(
            request.position[0] / 1000,
            request.position[1] / 1000,
            0,
            request.diameter / 1000
        )

        drawing.ClearSelection2(True)

        return {
            "success": symbol is not None,
            "view": request.view_name,
            "diameter_mm": request.diameter,
            "message": "Dowel pin symbol added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add dowel pin symbol failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/annotation/multi-jog-leader")
async def add_multi_jog_leader(request: MultiJogLeaderRequest):
    """Add a leader line with multiple jogs/bends."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateView(request.view_name)

        # Create note first
        note = drawing.InsertNote(request.text)

        if note:
            # Position note at last point
            last_pt = request.points[-1]
            note.SetPosition(last_pt[0] / 1000, last_pt[1] / 1000, 0)

            # Add leader points
            for i, pt in enumerate(request.points[:-1]):
                note.AddLeaderPoint(pt[0] / 1000, pt[1] / 1000, 0)

        drawing.ClearSelection2(True)

        return {
            "success": note is not None,
            "view": request.view_name,
            "jog_count": len(request.points) - 1,
            "message": "Multi-jog leader added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add multi-jog leader failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Layer Management
# =============================================================================

class LayerRequest(BaseModel):
    layer_name: str
    description: Optional[str] = None
    color: Optional[int] = None  # RGB as integer
    line_style: Optional[str] = None
    line_weight: Optional[float] = None


@router.get("/layers")
async def list_layers():
    """List all layers in the drawing."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        layer_mgr = drawing.GetLayerManager()
        layers = []

        layer_count = layer_mgr.GetLayerCount()
        for i in range(layer_count):
            layer = layer_mgr.GetLayerAt(i)
            if layer:
                layers.append({
                    "name": layer.Name,
                    "description": layer.Description,
                    "visible": layer.Visible,
                    "color": layer.Color
                })

        return {
            "layer_count": len(layers),
            "layers": layers
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List layers failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/layer/create")
async def create_layer(request: LayerRequest):
    """Create a new layer."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        layer_mgr = drawing.GetLayerManager()

        # Create layer
        layer = layer_mgr.AddLayer(
            request.layer_name,
            request.description or "",
            request.color or 0,
            request.line_style or "Continuous",
            request.line_weight or 0.25
        )

        return {
            "success": layer is not None,
            "layer_name": request.layer_name,
            "message": f"Layer '{request.layer_name}' created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create layer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/layer/set-current")
async def set_current_layer(layer_name: str):
    """Set the current/active layer."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        layer_mgr = drawing.GetLayerManager()
        result = layer_mgr.SetCurrentLayer(layer_name)

        return {
            "success": result,
            "current_layer": layer_name,
            "message": f"Current layer set to '{layer_name}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set current layer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Drawing Sheets
# =============================================================================

@router.get("/sheets")
async def list_sheets():
    """List all sheets in the drawing."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        sheets = []
        sheet_names = drawing.GetSheetNames()

        if sheet_names:
            for name in sheet_names:
                sheet = drawing.Sheet(name)
                if sheet:
                    sheets.append({
                        "name": name,
                        "scale": sheet.GetScale2(),
                        "template": sheet.GetTemplateName(),
                        "paper_size": sheet.GetSize()
                    })

        return {
            "sheet_count": len(sheets),
            "current_sheet": drawing.GetCurrentSheet().GetName() if drawing.GetCurrentSheet() else None,
            "sheets": sheets
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List sheets failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/sheet/activate")
async def activate_sheet(sheet_name: str):
    """Activate a sheet by name."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        result = drawing.ActivateSheet(sheet_name)

        return {
            "success": result,
            "active_sheet": sheet_name,
            "message": f"Sheet '{sheet_name}' activated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Activate sheet failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/sheet/set-scale")
async def set_sheet_scale(sheet_name: str, scale_numerator: float, scale_denominator: float):
    """Set the scale of a sheet."""
    try:
        sw = get_solidworks()
        drawing = get_drawing_doc(sw)

        drawing.ActivateSheet(sheet_name)
        sheet = drawing.GetCurrentSheet()

        if sheet:
            sheet.SetScale2(scale_numerator, scale_denominator)
            drawing.EditRebuild3()

        return {
            "success": True,
            "sheet": sheet_name,
            "scale": f"{scale_numerator}:{scale_denominator}",
            "message": f"Sheet scale set to {scale_numerator}:{scale_denominator}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set sheet scale failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
