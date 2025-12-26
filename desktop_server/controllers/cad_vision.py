"""
CAD Vision Analysis Controller
==============================
Advanced vision analysis tools specifically for CAD screenshots.
Includes dimension extraction, GD&T detection, annotation analysis, etc.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import re
import base64
import io
from PIL import Image

router = APIRouter(prefix="/cad/vision", tags=["cad", "vision"])
logger = logging.getLogger(__name__)


def base64_to_image(b64: str) -> Image.Image:
    """Convert base64 string to PIL Image."""
    data = base64.b64decode(b64)
    return Image.open(io.BytesIO(data))


def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode()


class ScreenshotRequest(BaseModel):
    image_base64: str


class DimensionExtractionResult(BaseModel):
    dimensions: List[Dict[str, Any]]
    total_count: int
    units_detected: List[str]


@router.post("/extract-dimensions")
async def extract_dimensions_screenshot(req: ScreenshotRequest):
    """Extract dimensions from CAD screenshot using OCR and pattern matching."""
    try:
        import pytesseract
    except ImportError:
        raise HTTPException(status_code=500, detail="pytesseract not available")
    
    logger.info("Extracting dimensions from screenshot")
    
    # Load image
    img = base64_to_image(req.image_base64)
    
    # OCR
    text = pytesseract.image_to_string(img)
    
    # Extract dimensions using regex patterns
    dimensions = []
    units_detected = set()
    
    # Pattern: decimal numbers with units (e.g., "50.5mm", "2.5in", "1/2\"")
    patterns = [
        (r'(\d+\.?\d*)\s*(mm|cm|m|in|inch|inches|"|\')', 'decimal'),
        (r'(\d+)\s*-\s*(\d+)/(\d+)\s*"', 'fractional'),
        (r'(\d+)\s*/\s*(\d+)\s*"', 'fraction'),
        (r'Ø\s*(\d+\.?\d*)\s*(mm|in)', 'diameter'),
        (r'R\s*(\d+\.?\d*)\s*(mm|in)', 'radius'),
    ]
    
    for pattern, dim_type in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if dim_type == 'fractional':
                whole = int(match.group(1))
                num = int(match.group(2))
                den = int(match.group(3))
                value = whole + (num / den)
                unit = "in"
            elif dim_type == 'fraction':
                num = int(match.group(1))
                den = int(match.group(2))
                value = num / den
                unit = "in"
            else:
                value = float(match.group(1))
                unit = match.group(2).lower() if len(match.groups()) > 1 else "mm"
                if unit in ['"', "'", 'inch', 'inches']:
                    unit = "in"
            
            dimensions.append({
                "value": value,
                "unit": unit,
                "type": dim_type,
                "text": match.group(0)
            })
            units_detected.add(unit)
    
    return DimensionExtractionResult(
        dimensions=dimensions,
        total_count=len(dimensions),
        units_detected=list(units_detected)
    ).dict()


@router.post("/detect-gdt-symbols")
async def detect_gdt_symbols(req: ScreenshotRequest):
    """Detect GD&T symbols in drawing screenshot."""
    logger.info("Detecting GD&T symbols")
    
    # GD&T symbol patterns (Unicode and text)
    gdt_symbols = {
        "⏥": "parallelism",
        "⊥": "perpendicularity",
        "∥": "parallelism_alt",
        "⊕": "position",
        "○": "circularity",
        "⌭": "cylindricity",
        "⌓": "flatness",
        "↗": "surface_profile",
    }
    
    # Load image and do OCR
    try:
        import pytesseract
        img = base64_to_image(req.image_base64)
        text = pytesseract.image_to_string(img)
    except ImportError:
        raise HTTPException(status_code=500, detail="pytesseract not available")
    
    detected = []
    for symbol, name in gdt_symbols.items():
        if symbol in text:
            detected.append({
                "symbol": symbol,
                "name": name,
                "unicode": ord(symbol)
            })
    
    # Also check for text-based GD&T (e.g., "PERP", "PAR", "POS")
    text_patterns = {
        r'\bPERP\b': "perpendicularity",
        r'\bPAR\b': "parallelism",
        r'\bPOS\b': "position",
        r'\bFLAT\b': "flatness",
        r'\bCIRC\b': "circularity",
    }
    
    for pattern, name in text_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            detected.append({
                "symbol": None,
                "name": name,
                "text_match": True
            })
    
    return {
        "status": "ok",
        "symbols_detected": detected,
        "total_count": len(detected)
    }


@router.post("/detect-annotations")
async def detect_annotations(req: ScreenshotRequest):
    """Detect and extract annotations from drawing screenshot."""
    try:
        import pytesseract
    except ImportError:
        raise HTTPException(status_code=500, detail="pytesseract not available")
    
    logger.info("Detecting annotations")
    
    img = base64_to_image(req.image_base64)
    text = pytesseract.image_to_string(img)
    
    annotations = []
    
    # Detect numbered notes (e.g., "1. Weld all around", "2. Remove burrs")
    note_pattern = r'(\d+)[\.\)]\s*(.+?)(?=\d+[\.\)]|$)'
    notes = re.findall(note_pattern, text, re.MULTILINE | re.DOTALL)
    for num, content in notes:
        annotations.append({
            "type": "note",
            "number": int(num),
            "text": content.strip()
        })
    
    # Detect balloons (circles with numbers)
    balloon_pattern = r'[\(\[{](\d+)[\)\]}]'
    balloons = re.findall(balloon_pattern, text)
    for num in balloons:
        annotations.append({
            "type": "balloon",
            "number": int(num)
        })
    
    # Detect dimensions (already handled by extract-dimensions, but count here)
    dim_pattern = r'(\d+\.?\d*)\s*(mm|cm|m|in|"|\')'
    dim_count = len(re.findall(dim_pattern, text, re.IGNORECASE))
    
    return {
        "status": "ok",
        "annotations": annotations,
        "total_annotations": len(annotations),
        "notes_count": len([a for a in annotations if a["type"] == "note"]),
        "balloons_count": len([a for a in annotations if a["type"] == "balloon"]),
        "dimensions_count": dim_count
    }


@router.post("/extract-bom")
async def extract_bom_screenshot(req: ScreenshotRequest):
    """Extract BOM table from drawing screenshot."""
    try:
        import pytesseract
    except ImportError:
        raise HTTPException(status_code=500, detail="pytesseract not available")
    
    logger.info("Extracting BOM from screenshot")
    
    img = base64_to_image(req.image_base64)
    text = pytesseract.image_to_string(img)
    
    # Look for BOM table patterns
    bom_items = []
    
    # Pattern: Part number, Description, Qty (tab or space separated)
    # Example: "12345-001  Flange  2"
    bom_pattern = r'([A-Z0-9\-]+)\s+([A-Za-z\s]+?)\s+(\d+)'
    matches = re.finditer(bom_pattern, text)
    
    for match in matches:
        bom_items.append({
            "part_number": match.group(1).strip(),
            "description": match.group(2).strip(),
            "quantity": int(match.group(3))
        })
    
    return {
        "status": "ok",
        "bom_items": bom_items,
        "total_items": len(bom_items),
        "total_quantity": sum(item["quantity"] for item in bom_items)
    }


@router.post("/analyze-drawing-sheet")
async def analyze_drawing_sheet(req: ScreenshotRequest):
    """Comprehensive analysis of entire drawing sheet."""
    logger.info("Analyzing drawing sheet")
    
    # Run all analyses
    dim_result = await extract_dimensions_screenshot(req)
    gdt_result = await detect_gdt_symbols(req)
    annot_result = await detect_annotations(req)
    bom_result = await extract_bom_screenshot(req)
    
    return {
        "status": "ok",
        "dimensions": dim_result,
        "gdt_symbols": gdt_result,
        "annotations": annot_result,
        "bom": bom_result,
        "summary": {
            "total_dimensions": dim_result["total_count"],
            "total_gdt_symbols": gdt_result["total_count"],
            "total_annotations": annot_result["total_annotations"],
            "total_bom_items": bom_result["total_items"]
        }
    }


class MultiViewRequest(BaseModel):
    views: Optional[List[str]] = None


@router.post("/multi-view")
async def capture_multi_view(req: MultiViewRequest):
    """Capture multiple standard views (requires SolidWorks COM)."""
    try:
        import win32com.client
    except ImportError:
        raise HTTPException(status_code=500, detail="win32com not available")
    
    views_to_capture = req.views or ["front", "top", "right", "isometric"]
    logger.info(f"Capturing multi-view: {views_to_capture}")
    
    try:
        sw_app = win32com.client.GetActiveObject("SldWorks.Application")
        model = sw_app.ActiveDoc
        
        if not model:
            raise HTTPException(status_code=400, detail="No active SolidWorks document")
        
        views = {}
        view_map = {
            "front": 1,  # swStandardViewsFront
            "back": 2,
            "top": 3,
            "bottom": 4,
            "left": 5,
            "right": 6,
            "isometric": 7,
            "trimetric": 8
        }
        
        for view_name in views_to_capture:
            if view_name.lower() not in view_map:
                continue
            
            view_const = view_map[view_name.lower()]
            model.ShowNamedView2("", view_const)
            model.ViewZoomtofit2()
            
            # Take screenshot (would need to integrate with screen controller)
            # For now, return placeholder
            views[view_name] = {
                "status": "captured",
                "view_type": view_name
            }
        
        return {
            "status": "ok",
            "views": views,
            "total_views": len(views)
        }
    except Exception as e:
        logger.error(f"Multi-view capture failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

