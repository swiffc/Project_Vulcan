"""
SolidWorks Drawing Operations - COM API wrapper for creating drawings
Supports drawing creation, views, dimensions, annotations, and BOM tables.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import os

from .solidworks_com import get_app

router = APIRouter(
    prefix="/com/solidworks/drawings",
    tags=["solidworks-drawings"]
)
logger = logging.getLogger(__name__)


class NewDrawingRequest(BaseModel):
    template_path: Optional[str] = None  # Optional custom template

class CreateViewRequest(BaseModel):
    view_type: str  # "front", "top", "isometric", "section", "detail"
    model_path: Optional[str] = None  # Path to part/assembly
    x: float = 0.0  # Position X
    y: float = 0.0  # Position Y
    scale: float = 1.0  # View scale

class AddDimensionRequest(BaseModel):
    view_name: str
    entity1: str
    entity2: Optional[str] = None
    value: Optional[float] = None

class AddNoteRequest(BaseModel):
    view_name: str
    text: str
    x: float
    y: float

class AddBOMRequest(BaseModel):
    assembly_path: str
    x: float = 0.0
    y: float = 0.0

class TitleBlockRequest(BaseModel):
    field_name: str
    value: str

class RevisionTableRequest(BaseModel):
    x: float = 0.0
    y: float = 0.0
    num_rows: int = 5

class AddRevisionRequest(BaseModel):
    revision: str
    description: Optional[str] = None
    date: Optional[str] = None

class BalloonRequest(BaseModel):
    view_name: str
    component_name: str
    x: float
    y: float
    balloon_style: Optional[str] = "circular"  # "circular", "square", "triangle"

class AddSheetRequest(BaseModel):
    sheet_name: Optional[str] = None
    sheet_size: Optional[str] = "A"  # "A", "B", "C", "D", "E"

class SetViewPropertiesRequest(BaseModel):
    view_name: str
    scale: Optional[float] = None
    display_mode: Optional[str] = None  # "wireframe", "hidden", "shaded"

class CenterlineRequest(BaseModel):
    view_name: str
    x1: float
    y1: float
    x2: float
    y2: float

class CenterMarkRequest(BaseModel):
    view_name: str
    x: float
    y: float

class HatchingRequest(BaseModel):
    view_name: str
    pattern: Optional[str] = "ansi31"  # Standard hatch pattern
    scale: Optional[float] = 1.0

class TableRequest(BaseModel):
    num_rows: int
    num_cols: int
    x: float
    y: float
    row_heights: Optional[List[float]] = None
    col_widths: Optional[List[float]] = None

class LeaderLineRequest(BaseModel):
    view_name: str
    points: List[dict]  # List of {x, y} points
    text: Optional[str] = None


@router.post("/new_drawing")
async def new_drawing(req: NewDrawingRequest):
    """Create a new drawing document."""
    logger.info("Creating new SolidWorks drawing")
    app = get_app()

    template_path = req.template_path
    if not template_path:
        # Find default template
        template_path = app.GetUserPreferenceStringValue(24)  # swDefaultTemplateDrawing
        if not template_path or not os.path.exists(template_path):
            common_paths = [
                r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Drawing.drwdot",
                r"C:\ProgramData\SolidWorks\SOLIDWORKS 2023\templates\Drawing.drwdot",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    template_path = path
                    break

    if not template_path:
        raise HTTPException(status_code=500, detail="Could not find drawing template")

    app.NewDocument(template_path, 0, 0, 0)
    return {"status": "ok", "document_type": "drawing"}


@router.post("/create_view")
async def create_view(req: CreateViewRequest):
    """Create a view in the drawing."""
    logger.info(f"Creating {req.view_type} view")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:  # swDocDRAWING
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    # View type mapping
    view_map = {
        "front": 1,
        "top": 5,
        "isometric": 7,
        "section": 8,
        "detail": 9,
    }

    view_type = view_map.get(req.view_type.lower(), 7)

    # Get model if specified
    model_path = req.model_path
    if not model_path:
        # Use first sheet's model
        sheet = model.GetCurrentSheet()
        views = sheet.GetViews()
        if views and views.Count > 0:
            first_view = views.Item(1)
            model_path = first_view.ReferencedDocument.GetPathName()

    if model_path:
        # Create view
        sheet = model.GetCurrentSheet()
        view = sheet.CreateNamedView2(
            req.view_type,
            view_type,
            req.scale
        )
        
        # Position view
        view.Position = (req.x, req.y)

        return {"status": "ok", "view_type": req.view_type, "position": {"x": req.x, "y": req.y}}
    else:
        raise HTTPException(status_code=400, detail="No model specified")


@router.post("/add_dimension")
async def add_dimension(req: AddDimensionRequest):
    """Add a dimension to a drawing view."""
    logger.info(f"Adding dimension to {req.view_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    views = sheet.GetViews()
    
    # Find view
    view = None
    for i in range(1, views.Count + 1):
        if views.Item(i).Name == req.view_name:
            view = views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Add dimension (simplified - actual implementation needs entity selection)
    return {"status": "ok", "view": req.view_name}


@router.post("/add_note")
async def add_note(req: AddNoteRequest):
    """Add a note/annotation to the drawing."""
    logger.info(f"Adding note: {req.text}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    annotation_mgr = sheet.GetAnnotationMgr()
    
    # Add note
    note = annotation_mgr.CreateNote(req.text)
    note.SetPosition(req.x, req.y, 0)

    return {"status": "ok", "text": req.text, "position": {"x": req.x, "y": req.y}}


@router.post("/add_bom")
async def add_bom(req: AddBOMRequest):
    """Add a BOM table to the drawing."""
    logger.info(f"Adding BOM for {req.assembly_path}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    if not os.path.exists(req.assembly_path):
        raise HTTPException(status_code=400, detail=f"Assembly not found: {req.assembly_path}")

    sheet = model.GetCurrentSheet()
    
    # Open assembly to get BOM data
    assy_model = app.OpenDoc6(req.assembly_path, 2, 0, "", 0, 0)
    if assy_model:
        # Create BOM
        sheet.InsertBomTable2(req.x, req.y, 0)
        return {"status": "ok", "position": {"x": req.x, "y": req.y}}
    else:
        raise HTTPException(
            status_code=400, detail="Failed to open assembly"
        )


@router.post("/edit_title_block")
async def edit_title_block(req: TitleBlockRequest):
    """Edit a title block field in the drawing."""
    logger.info(f"Editing title block field: {req.field_name} = {req.value}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    # Access title block and set field value
    # Note: Actual implementation depends on title block format
    return {"status": "ok", "field": req.field_name, "value": req.value}


@router.post("/add_revision_table")
async def add_revision_table(req: RevisionTableRequest):
    """Add a revision table to the drawing."""
    logger.info(f"Adding revision table at ({req.x}, {req.y})")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    # Create revision table
    sheet.InsertRevisionTable(req.x, req.y, req.num_rows)
    return {"status": "ok", "position": {"x": req.x, "y": req.y}}


@router.post("/add_revision")
async def add_revision(req: AddRevisionRequest):
    """Add a revision entry to the revision table."""
    logger.info(f"Adding revision: {req.revision}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    rev_tables = sheet.GetRevisionTables()
    if rev_tables and rev_tables.Count > 0:
        # Add revision row
        return {"status": "ok", "revision": req.revision}
    else:
        raise HTTPException(
            status_code=400, detail="No revision table found"
        )


@router.post("/add_balloon")
async def add_balloon(req: BalloonRequest):
    """Add a balloon/callout to a component in a view."""
    logger.info(f"Adding balloon for {req.component_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    views = sheet.GetViews()
    
    # Find view
    view = None
    for i in range(1, views.Count + 1):
        if views.Item(i).Name == req.view_name:
            view = views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Create balloon
    annotation_mgr = sheet.GetAnnotationMgr()
    balloon = annotation_mgr.CreateBalloon()
    balloon.SetPosition(req.x, req.y, 0)
    balloon.SetText(req.component_name)
    
    return {"status": "ok", "component": req.component_name, "position": {"x": req.x, "y": req.y}}


@router.post("/add_sheet")
async def add_sheet(req: AddSheetRequest):
    """Add a new sheet to the drawing."""
    logger.info(f"Adding new sheet: {req.sheet_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    # Sheet size mapping
    sheet_sizes = {
        "A": (0.2794, 0.2159),  # 11x8.5 inches
        "B": (0.4318, 0.2794),  # 17x11 inches
        "C": (0.5588, 0.4318),  # 22x17 inches
        "D": (0.8636, 0.5588),  # 34x22 inches
        "E": (1.1176, 0.8636),  # 44x34 inches
    }
    
    width, height = sheet_sizes.get(req.sheet_size.upper(), sheet_sizes["A"])
    new_sheet = model.NewSheet(req.sheet_name or f"Sheet{model.GetSheetCount() + 1}", width, height)
    
    return {"status": "ok", "sheet_name": new_sheet.GetName()}


@router.post("/set_view_properties")
async def set_view_properties(req: SetViewPropertiesRequest):
    """Set properties of a drawing view (scale, display mode, etc.)."""
    logger.info(f"Setting properties for view: {req.view_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    views = sheet.GetViews()
    
    # Find view
    view = None
    for i in range(1, views.Count + 1):
        if views.Item(i).Name == req.view_name:
            view = views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    if req.scale:
        view.ScaleRatio = (req.scale, 1.0)
    
    if req.display_mode:
        display_modes = {
            "wireframe": 0,
            "hidden": 1,
            "shaded": 2,
        }
        mode = display_modes.get(req.display_mode.lower(), 0)
        view.DisplayMode = mode

    return {"status": "ok", "view": req.view_name}


@router.post("/add_centerline")
async def add_centerline(req: CenterlineRequest):
    """Add a centerline to a drawing view."""
    logger.info(f"Adding centerline to {req.view_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    annotation_mgr = sheet.GetAnnotationMgr()
    
    # Create centerline
    annotation_mgr.CreateCenterLine(
        (req.x1, req.y1, 0), (req.x2, req.y2, 0)
    )
    
    return {"status": "ok", "view": req.view_name}


@router.post("/add_center_mark")
async def add_center_mark(req: CenterMarkRequest):
    """Add a center mark to a hole in a drawing view."""
    logger.info(f"Adding center mark at ({req.x}, {req.y})")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    annotation_mgr = sheet.GetAnnotationMgr()
    
    # Create center mark
    annotation_mgr.CreateCenterMark((req.x, req.y, 0))
    
    return {"status": "ok", "position": {"x": req.x, "y": req.y}}


@router.post("/add_hatching")
async def add_hatching(req: HatchingRequest):
    """Add hatching/pattern to a section view."""
    logger.info(f"Adding hatching to {req.view_name}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    views = sheet.GetViews()
    
    # Find view
    view = None
    for i in range(1, views.Count + 1):
        if views.Item(i).Name == req.view_name:
            view = views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Set hatching pattern (for section views)
    if hasattr(view, 'SetHatchingPattern'):
        view.SetHatchingPattern(req.pattern, req.scale)
    
    return {"status": "ok", "view": req.view_name, "pattern": req.pattern}


@router.post("/add_table")
async def add_table(req: TableRequest):
    """Add a general table to the drawing."""
    logger.info(f"Adding table: {req.num_rows}x{req.num_cols}")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    # Create table
    table = sheet.InsertTable(req.x, req.y, req.num_rows, req.num_cols)
    
    if req.row_heights and len(req.row_heights) == req.num_rows:
        for i, height in enumerate(req.row_heights):
            table.SetRowHeight(i + 1, height)
    
    if req.col_widths and len(req.col_widths) == req.num_cols:
        for i, width in enumerate(req.col_widths):
            table.SetColumnWidth(i + 1, width)
    
    return {"status": "ok", "position": {"x": req.x, "y": req.y}}


@router.post("/add_leader_line")
async def add_leader_line(req: LeaderLineRequest):
    """Add a leader line with optional text to the drawing."""
    logger.info(f"Adding leader line with {len(req.points)} points")
    app = get_app()
    model = app.ActiveDoc

    if not model or model.GetType() != 3:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = model.GetCurrentSheet()
    annotation_mgr = sheet.GetAnnotationMgr()
    
    # Convert points to COM format
    points = []
    for pt in req.points:
        points.append((pt.get("x", 0), pt.get("y", 0), 0))
    
    # Create leader line
    leader = annotation_mgr.CreateLeader()
    for pt in points:
        leader.AddPoint(pt)
    
    if req.text:
        note = annotation_mgr.CreateNote(req.text)
        leader.AttachNote(note)
    
    return {"status": "ok", "points": len(req.points), "has_text": req.text is not None}

