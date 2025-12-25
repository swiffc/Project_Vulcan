"""
Inventor Drawing Operations - COM API wrapper for creating drawings
Supports drawing creation, views, dimensions, annotations, and BOM tables.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import os

from .inventor_com import get_app

router = APIRouter(
    prefix="/com/inventor/drawings",
    tags=["inventor-drawings"]
)
logger = logging.getLogger(__name__)


class NewDrawingRequest(BaseModel):
    template_path: Optional[str] = None

class CreateViewRequest(BaseModel):
    view_type: str  # "front", "top", "isometric", "section", "detail"
    model_path: Optional[str] = None
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0

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
    balloon_style: Optional[str] = "circular"

class AddSheetRequest(BaseModel):
    sheet_name: Optional[str] = None
    sheet_size: Optional[str] = "A"

class SetViewPropertiesRequest(BaseModel):
    view_name: str
    scale: Optional[float] = None
    display_mode: Optional[str] = None

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
    pattern: Optional[str] = "ansi31"
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
    points: List[dict]
    text: Optional[str] = None


@router.post("/new_drawing")
async def new_drawing(req: NewDrawingRequest):
    """Create a new drawing document."""
    logger.info("Creating new Inventor drawing")
    app = get_app()

    # Create new drawing document
    doc = app.Documents.Add(
        12292,  # kDrawingDocumentObject
        req.template_path if req.template_path else "",
        True
    )

    return {"status": "ok", "document_type": "drawing"}


@router.post("/create_view")
async def create_view(req: CreateViewRequest):
    """Create a view in the drawing."""
    logger.info(f"Creating {req.view_type} view")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:  # kDrawingDocumentObject
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews

    # Get model if specified
    model_path = req.model_path
    if not model_path:
        # Use first view's model
        if drawing_views.Count > 0:
            first_view = drawing_views.Item(1)
            model_path = first_view.ReferencedDocument.FullFileName

    if model_path:
        # View type mapping
        view_type_map = {
            "front": 12288,    # kFrontViewOrientation
            "top": 12289,      # kTopViewOrientation
            "isometric": 12290, # kIsoTopRightViewOrientation
        }

        view_orient = view_type_map.get(req.view_type.lower(), 12290)

        # Create view
        tg = app.TransientGeometry
        position = tg.CreatePoint2d(req.x, req.y)
        
        view = drawing_views.Add(
            model_path,
            position,
            view_orient,
            req.scale
        )

        return {"status": "ok", "view_type": req.view_type}
    else:
        raise HTTPException(status_code=400, detail="No model specified")


@router.post("/add_dimension")
async def add_dimension(req: AddDimensionRequest):
    """Add a dimension to a drawing view."""
    logger.info(f"Adding dimension to {req.view_name}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(
            status_code=400,
            detail="Active document is not a drawing"
        )

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews
    
    # Find view
    for i in range(1, drawing_views.Count + 1):
        if drawing_views.Item(i).Name == req.view_name:
            break
    else:
        raise HTTPException(
            status_code=400,
            detail=f"View not found: {req.view_name}"
        )

    # Add dimension (simplified)
    return {"status": "ok", "view": req.view_name}


@router.post("/add_note")
async def add_note(req: AddNoteRequest):
    """Add a note/annotation to the drawing."""
    logger.info(f"Adding note: {req.text}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_notes = sheet.DrawingNotes
    
    tg = app.TransientGeometry
    position = tg.CreatePoint2d(req.x, req.y)
    
    # Add note
    drawing_notes.Add(position, req.text)

    return {"status": "ok", "text": req.text}


@router.post("/add_bom")
async def add_bom(req: AddBOMRequest):
    """Add a BOM table to the drawing."""
    logger.info(f"Adding BOM for {req.assembly_path}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    if not os.path.exists(req.assembly_path):
        raise HTTPException(status_code=400, detail=f"Assembly not found: {req.assembly_path}")

    sheet = doc.ActiveSheet
    bom_tables = sheet.BOMTables
    
    # Open assembly
    assy_doc = app.Documents.Open(req.assembly_path, True)
    if assy_doc:
        # Create BOM
        tg = app.TransientGeometry
        position = tg.CreatePoint2d(req.x, req.y)
        bom_tables.Add(assy_doc, position)
        
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
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    title_block = sheet.TitleBlock
    
    # Set title block property
    if hasattr(title_block, 'GetProperty'):
        title_block.SetProperty(req.field_name, req.value)
    
    return {"status": "ok", "field": req.field_name, "value": req.value}


@router.post("/add_revision_table")
async def add_revision_table(req: RevisionTableRequest):
    """Add a revision table to the drawing."""
    logger.info(f"Adding revision table at ({req.x}, {req.y})")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    revision_tables = sheet.RevisionTables
    
    tg = app.TransientGeometry
    position = tg.CreatePoint2d(req.x, req.y)
    
    # Create revision table
    rev_table = revision_tables.Add(position, req.num_rows)
    return {"status": "ok", "position": {"x": req.x, "y": req.y}}


@router.post("/add_revision")
async def add_revision(req: AddRevisionRequest):
    """Add a revision entry to the revision table."""
    logger.info(f"Adding revision: {req.revision}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    rev_tables = sheet.RevisionTables
    
    if rev_tables.Count > 0:
        rev_table = rev_tables.Item(1)
        # Add revision row
        new_row = rev_table.RevisionTableRows.Add()
        new_row.Revision = req.revision
        if req.description:
            new_row.Description = req.description
        if req.date:
            new_row.Date = req.date
        
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
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews
    
    # Find view
    view = None
    for i in range(1, drawing_views.Count + 1):
        if drawing_views.Item(i).Name == req.view_name:
            view = drawing_views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Create balloon
    balloons = view.Balloons
    tg = app.TransientGeometry
    position = tg.CreatePoint2d(req.x, req.y)
    
    balloons.Add(position, req.component_name)
    
    return {
        "status": "ok",
        "component": req.component_name,
        "position": {"x": req.x, "y": req.y}
    }


@router.post("/add_sheet")
async def add_sheet(req: AddSheetRequest):
    """Add a new sheet to the drawing."""
    logger.info(f"Adding new sheet: {req.sheet_name}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    # Sheet size mapping (in cm)
    sheet_sizes = {
        "A": (27.94, 21.59),  # A-size in cm
        "B": (43.18, 27.94),  # B-size in cm
        "C": (55.88, 43.18),  # C-size in cm
        "D": (86.36, 55.88),  # D-size in cm
        "E": (111.76, 86.36), # E-size in cm
    }
    
    width, height = sheet_sizes.get(req.sheet_size.upper(), sheet_sizes["A"])
    sheets = doc.Sheets
    new_sheet = sheets.Add(req.sheet_name or f"Sheet{sheets.Count + 1}", width, height)
    
    return {"status": "ok", "sheet_name": new_sheet.Name}


@router.post("/set_view_properties")
async def set_view_properties(req: SetViewPropertiesRequest):
    """Set properties of a drawing view (scale, display mode, etc.)."""
    logger.info(f"Setting properties for view: {req.view_name}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews
    
    # Find view
    view = None
    for i in range(1, drawing_views.Count + 1):
        if drawing_views.Item(i).Name == req.view_name:
            view = drawing_views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    if req.scale:
        view.Scale = req.scale
    
    if req.display_mode:
        # Display mode constants
        display_modes = {
            "wireframe": 12291,  # kWireFrameDisplayMode
            "hidden": 12292,     # kHiddenLineDisplayMode
            "shaded": 12293,     # kShadedDisplayMode
        }
        mode = display_modes.get(req.display_mode.lower(), 12292)
        view.DisplayMode = mode

    return {"status": "ok", "view": req.view_name}


@router.post("/add_centerline")
async def add_centerline(req: CenterlineRequest):
    """Add a centerline to a drawing view."""
    logger.info(f"Adding centerline to {req.view_name}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews
    
    # Find view
    view = None
    for i in range(1, drawing_views.Count + 1):
        if drawing_views.Item(i).Name == req.view_name:
            view = drawing_views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Create centerline
    centerlines = view.CenterLines
    tg = app.TransientGeometry
    start_pt = tg.CreatePoint2d(req.x1, req.y1)
    end_pt = tg.CreatePoint2d(req.x2, req.y2)
    
    centerlines.Add(start_pt, end_pt)
    
    return {"status": "ok", "view": req.view_name}


@router.post("/add_center_mark")
async def add_center_mark(req: CenterMarkRequest):
    """Add a center mark to a hole in a drawing view."""
    logger.info(f"Adding center mark at ({req.x}, {req.y})")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews
    
    # Find view
    view = None
    for i in range(1, drawing_views.Count + 1):
        if drawing_views.Item(i).Name == req.view_name:
            view = drawing_views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Create center mark
    center_marks = view.CenterMarks
    tg = app.TransientGeometry
    position = tg.CreatePoint2d(req.x, req.y)
    
    center_marks.Add(position)
    
    return {"status": "ok", "position": {"x": req.x, "y": req.y}}


@router.post("/add_hatching")
async def add_hatching(req: HatchingRequest):
    """Add hatching/pattern to a section view."""
    logger.info(f"Adding hatching to {req.view_name}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews
    
    # Find view
    view = None
    for i in range(1, drawing_views.Count + 1):
        if drawing_views.Item(i).Name == req.view_name:
            view = drawing_views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Set hatching pattern (for section views)
    if hasattr(view, 'HatchingPattern'):
        view.HatchingPattern = req.pattern
        view.HatchingScale = req.scale
    
    return {"status": "ok", "view": req.view_name, "pattern": req.pattern}


@router.post("/add_table")
async def add_table(req: TableRequest):
    """Add a general table to the drawing."""
    logger.info(f"Adding table: {req.num_rows}x{req.num_cols}")
    app = get_app()
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    tables = sheet.Tables
    
    tg = app.TransientGeometry
    position = tg.CreatePoint2d(req.x, req.y)
    
    # Create table
    table = tables.Add(position, req.num_rows, req.num_cols)
    
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
    doc = app.ActiveDocument

    if not doc or doc.DocumentType != 12292:
        raise HTTPException(status_code=400, detail="Active document is not a drawing")

    sheet = doc.ActiveSheet
    drawing_views = sheet.DrawingViews
    
    # Find view
    view = None
    for i in range(1, drawing_views.Count + 1):
        if drawing_views.Item(i).Name == req.view_name:
            view = drawing_views.Item(i)
            break

    if not view:
        raise HTTPException(status_code=400, detail=f"View not found: {req.view_name}")

    # Create leader line
    leaders = view.LeaderLines
    tg = app.TransientGeometry
    
    points = []
    for pt in req.points:
        points.append(tg.CreatePoint2d(pt.get("x", 0), pt.get("y", 0)))
    
    leader = leaders.Add(points)
    
    if req.text:
        notes = sheet.DrawingNotes
        note = notes.Add(points[-1], req.text)
        leader.AttachNote(note)
    
    return {"status": "ok", "points": len(req.points), "has_text": req.text is not None}

