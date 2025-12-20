"""
PDF Bridge
Thin wrapper around pytesseract + pdf2image for drawing OCR.

Packages Used (via pip - NOT in project):
- pytesseract: OCR engine wrapper
- pdf2image: PDF to image conversion
- Pillow: Image processing

External Requirement:
- Tesseract OCR installed on system (see REFERENCES.md)
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("cad_agent.pdf-bridge")


@dataclass
class ExtractedDimension:
    value: float
    unit: str = "mm"
    tolerance: Optional[float] = None


@dataclass
class DrawingData:
    part_number: str
    revision: str
    material: str
    dimensions: List[ExtractedDimension]
    notes: List[str]
    raw_text: str


class PDFBridge:
    """
    Bridge to OCR packages for extracting drawing data.
    Keeps all heavy imports lazy-loaded.
    """
    
    def __init__(self, dpi: int = 300):
        self.dpi = dpi
        self._patterns = {
            "dimension": re.compile(r'(\d+\.?\d*)\s*(mm|in|")?'),
            "part_number": re.compile(r'P/?N[:\s]*([A-Z0-9\-]+)', re.I),
            "revision": re.compile(r'REV[:\s]*([A-Z0-9]+)', re.I),
            "material": re.compile(r'MATERIAL[:\s]*(.+?)(?:\n|$)', re.I),
        }
    
    def extract_from_pdf(self, pdf_path: str) -> List[DrawingData]:
        """Extract data from all pages of a PDF."""
        # Lazy imports
        from pdf2image import convert_from_path
        import pytesseract
        
        logger.info(f"📄 Processing: {pdf_path}")
        images = convert_from_path(pdf_path, dpi=self.dpi)
        
        results = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img)
            data = self._parse_text(text)
            results.append(data)
            logger.info(f"  Page {i+1}: {len(data.dimensions)} dimensions found")
            
        return results
    
    def _parse_text(self, text: str) -> DrawingData:
        """Parse OCR text into structured data."""
        # Extract part number
        pn_match = self._patterns["part_number"].search(text)
        part_number = pn_match.group(1) if pn_match else ""
        
        # Extract revision
        rev_match = self._patterns["revision"].search(text)
        revision = rev_match.group(1) if rev_match else "A"
        
        # Extract material
        mat_match = self._patterns["material"].search(text)
        material = mat_match.group(1).strip() if mat_match else ""
        
        # Extract dimensions
        dimensions = [
            ExtractedDimension(value=float(m.group(1)), unit=m.group(2) or "mm")
            for m in self._patterns["dimension"].finditer(text)
        ]
        
        # Extract notes (lines starting with numbers)
        notes = re.findall(r'^\d+[.\)]\s*(.+)$', text, re.MULTILINE)
        
        return DrawingData(
            part_number=part_number,
            revision=revision,
            material=material,
            dimensions=dimensions,
            notes=notes,
            raw_text=text
        )
