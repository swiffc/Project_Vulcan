"""
Desktop Server Extractors
=========================
Extract data from SolidWorks models and PDF drawings.
Phase 25 - PDF Drawing Validation support.
"""

from .properties import PropertiesExtractor
from .holes import HolePatternExtractor
from .pdf_drawing_extractor import (
    PDFDrawingExtractor,
    DrawingExtractionResult,
    DrawingType,
    TitleBlockData,
    BOMItem,
    WeldSymbol,
    Dimension,
    DesignData,
    RevisionEntry,
    GeneralNotes,
)

__all__ = [
    # SolidWorks extractors
    "PropertiesExtractor",
    "HolePatternExtractor",
    # PDF extractors (Phase 25)
    "PDFDrawingExtractor",
    "DrawingExtractionResult",
    "DrawingType",
    "TitleBlockData",
    "BOMItem",
    "WeldSymbol",
    "Dimension",
    "DesignData",
    "RevisionEntry",
    "GeneralNotes",
]
