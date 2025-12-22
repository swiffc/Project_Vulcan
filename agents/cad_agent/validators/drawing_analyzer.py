"""
Drawing Analyzer

Extracts text, images, and metadata from PDF/DXF drawings.
Uses OCR (pytesseract) and PDF processing (pdf2image, PyPDF2).
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    from pdf2image import convert_from_path

    PDF2IMAGE_AVAILABLE = True
except ImportError:
    logger.warning("pdf2image not available - PDF image conversion disabled")
    PDF2IMAGE_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image

    PYTESSERACT_AVAILABLE = True
except ImportError:
    logger.warning("pytesseract not available - OCR disabled")
    PYTESSERACT_AVAILABLE = False

try:
    from PyPDF2 import PdfReader

    PYPDF2_AVAILABLE = True
except ImportError:
    logger.warning("PyPDF2 not available - PDF text extraction disabled")
    PYPDF2_AVAILABLE = False


@dataclass
class DrawingAnalysis:
    """Results from analyzing a drawing."""

    file_path: str
    file_type: str  # "pdf", "dxf", etc.

    # Extracted content
    extracted_text: str = ""
    raw_text: str = ""  # Direct PDF text extraction
    ocr_text: str = ""  # OCR from images

    # Metadata
    title: Optional[str] = None
    drawing_number: Optional[str] = None
    revision: Optional[str] = None
    sheet_count: int = 0

    # Engineering data
    datums: List[str] = field(default_factory=list)
    weld_callouts: List[Dict[str, Any]] = field(default_factory=list)
    materials: List[Dict[str, Any]] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Images
    page_images: List[Any] = field(default_factory=list)  # PIL Images

    # Analysis metadata
    analysis_duration_ms: int = 0
    ocr_used: bool = False
    errors: List[str] = field(default_factory=list)


class DrawingAnalyzer:
    """
    Analyzes CAD drawings to extract text, metadata, and engineering data.

    Supports PDF drawings with both direct text extraction and OCR.

    Example:
        >>> analyzer = DrawingAnalyzer()
        >>> analysis = analyzer.analyze_pdf("drawing.pdf")
        >>> print(f"Found {len(analysis.datums)} datums")
        >>> print(f"Extracted {len(analysis.extracted_text)} characters")
    """

    def __init__(self, enable_ocr: bool = True):
        """
        Initialize analyzer.

        Args:
            enable_ocr: Whether to use OCR for scanned PDFs
        """
        self.enable_ocr = enable_ocr and PYTESSERACT_AVAILABLE

        logger.info("DrawingAnalyzer initialized")
        logger.info(f"  PDF text extraction: {'✓' if PYPDF2_AVAILABLE else '✗'}")
        logger.info(f"  PDF to image: {'✓' if PDF2IMAGE_AVAILABLE else '✗'}")
        logger.info(f"  OCR: {'✓' if self.enable_ocr else '✗'}")

    def analyze_pdf(self, file_path: str) -> DrawingAnalysis:
        """
        Analyze a PDF drawing.

        Args:
            file_path: Path to PDF file

        Returns:
            Complete drawing analysis
        """
        import time

        start_time = time.time()

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Drawing not found: {file_path}")

        logger.info(f"Analyzing PDF: {file_path}")

        analysis = DrawingAnalysis(
            file_path=file_path,
            file_type="pdf",
        )

        try:
            # Extract text directly from PDF
            if PYPDF2_AVAILABLE:
                analysis.raw_text = self._extract_pdf_text(file_path)
                analysis.extracted_text = analysis.raw_text
                logger.info(f"  Extracted {len(analysis.raw_text)} chars from PDF")

            # Convert to images for OCR if needed
            if self.enable_ocr and PDF2IMAGE_AVAILABLE:
                analysis.page_images = self._convert_pdf_to_images(file_path)
                logger.info(f"  Converted to {len(analysis.page_images)} images")

                # Run OCR if text extraction yielded little content
                if len(analysis.raw_text) < 100:
                    analysis.ocr_text = self._run_ocr(analysis.page_images)
                    analysis.extracted_text = analysis.ocr_text
                    analysis.ocr_used = True
                    logger.info(f"  OCR extracted {len(analysis.ocr_text)} chars")

            # Parse engineering data
            self._parse_engineering_data(analysis)

            # Extract metadata
            self._extract_metadata(analysis)

            duration_ms = int((time.time() - start_time) * 1000)
            analysis.analysis_duration_ms = duration_ms

            logger.info(f"Analysis complete in {duration_ms}ms:")
            logger.info(f"  Text: {len(analysis.extracted_text)} chars")
            logger.info(f"  Datums: {len(analysis.datums)}")
            logger.info(f"  Welds: {len(analysis.weld_callouts)}")
            logger.info(f"  Materials: {len(analysis.materials)}")

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            analysis.errors.append(str(e))

        return analysis

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text directly from PDF."""
        if not PYPDF2_AVAILABLE:
            return ""

        try:
            reader = PdfReader(file_path)
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""

    def _convert_pdf_to_images(self, file_path: str) -> List[Any]:
        """Convert PDF pages to images."""
        if not PDF2IMAGE_AVAILABLE:
            return []

        try:
            images = convert_from_path(file_path, dpi=300)
            return images

        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            return []

    def _run_ocr(self, images: List[Any]) -> str:
        """Run OCR on images."""
        if not PYTESSERACT_AVAILABLE or not images:
            return ""

        try:
            text_parts = []

            for i, image in enumerate(images):
                logger.debug(f"  Running OCR on page {i + 1}...")
                text = pytesseract.image_to_string(image)
                if text:
                    text_parts.append(text)

            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""

    def _parse_engineering_data(self, analysis: DrawingAnalysis) -> None:
        """Parse engineering data from extracted text."""
        text = analysis.extracted_text

        # Find datums (A, B, C, etc.)
        datum_pattern = r"\b([A-Z])\b(?:\s*(?:DATUM|DAT))?"
        datums = re.findall(datum_pattern, text)
        analysis.datums = sorted(list(set(datums)))[:10]  # Limit to reasonable count

        # Find weld callouts
        # Pattern: fillet welds, groove welds, etc.
        weld_patterns = [
            r"(\d+/\d+)\s*(?:FILLET|FILL|F)",  # e.g., "1/4 FILLET"
            r"(CJP|PJP)",  # Complete/Partial Joint Penetration
            r"AWS\s+D1\.1",  # AWS reference
        ]

        for pattern in weld_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                analysis.weld_callouts.append(
                    {
                        "symbol": match.group(0),
                        "location": f"Character {match.start()}",
                        "type": (
                            "fillet"
                            if "FILLET" in match.group(0).upper()
                            else "unknown"
                        ),
                    }
                )

        # Find material callouts
        # Pattern: ASTM specs, grade callouts
        material_patterns = [
            r"(ASTM\s+[A-Z]\d+[A-Z]?)",  # e.g., "ASTM A36"
            r"(SA-\d+[A-Z]?)",  # e.g., "SA-516"
            r"(GRADE\s+\d+)",  # e.g., "GRADE 70"
        ]

        for pattern in material_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                analysis.materials.append(
                    {
                        "spec": match.group(0),
                        "location": f"Character {match.start()}",
                    }
                )

        # Find dimensions (basic pattern)
        dimension_pattern = r'(\d+(?:\.\d+)?)\s*(?:IN|"|MM|\')'
        dimensions = re.findall(dimension_pattern, text, re.IGNORECASE)
        analysis.dimensions = dimensions[:50]  # Limit to reasonable count

        # Find notes
        note_patterns = [
            r"NOTE\s*\d*\s*[:-]\s*(.+?)(?:\n|$)",
            r"GENERAL\s+NOTES?\s*[:-]\s*(.+?)(?:\n|$)",
        ]

        for pattern in note_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            analysis.notes.extend(matches[:20])  # Limit to reasonable count

    def _extract_metadata(self, analysis: DrawingAnalysis) -> None:
        """Extract drawing metadata."""
        text = analysis.extracted_text

        # Drawing number pattern
        dwg_patterns = [
            r"DWG\s*(?:NO\.?|#|NUM)?\s*[:-]?\s*([A-Z0-9-]+)",
            r"DRAWING\s*(?:NO\.?|#|NUM)?\s*[:-]?\s*([A-Z0-9-]+)",
        ]

        for pattern in dwg_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                analysis.drawing_number = match.group(1)
                break

        # Revision pattern
        rev_patterns = [
            r"REV\.?\s*[:-]?\s*([A-Z0-9]+)",
            r"REVISION\s*[:-]?\s*([A-Z0-9]+)",
        ]

        for pattern in rev_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                analysis.revision = match.group(1)
                break

        # Title (usually in uppercase near top)
        title_match = re.search(r"^([A-Z\s]{10,60})$", text[:500], re.MULTILINE)
        if title_match:
            analysis.title = title_match.group(1).strip()

        # Sheet count
        sheet_match = re.search(r"SHEET\s+\d+\s+OF\s+(\d+)", text, re.IGNORECASE)
        if sheet_match:
            analysis.sheet_count = int(sheet_match.group(1))
        else:
            analysis.sheet_count = (
                len(analysis.page_images) if analysis.page_images else 1
            )

    def analyze_dxf(self, file_path: str) -> DrawingAnalysis:
        """
        Analyze a DXF drawing.

        Args:
            file_path: Path to DXF file

        Returns:
            Drawing analysis with extracted geometric data
        """
        import time

        start_time = time.time()

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"DXF file not found: {file_path}")

        logger.info(f"Analyzing DXF: {file_path}")

        analysis = DrawingAnalysis(
            file_path=file_path,
            file_type="dxf",
        )

        try:
            import ezdxf

            # Read DXF file
            doc = ezdxf.readfile(file_path)
            modelspace = doc.modelspace()

            logger.info(f"  DXF version: {doc.dxfversion}")
            logger.info(f"  Entities: {len(list(modelspace))}")

            # Extract dimensions from DIMENSION entities
            dimensions = []
            for entity in modelspace.query("DIMENSION"):
                try:
                    # Get dimension measurement
                    measurement = entity.dxf.get("text", "")
                    if not measurement:
                        # Try to get actual measurement value
                        measurement = str(round(entity.get_measurement(), 3))
                    dimensions.append(measurement)
                except Exception as e:
                    logger.debug(f"Could not extract dimension: {e}")

            analysis.dimensions = dimensions
            logger.info(f"  Extracted {len(dimensions)} dimensions")

            # Extract hole patterns from CIRCLE entities
            holes = []
            for circle in modelspace.query("CIRCLE"):
                try:
                    center = circle.dxf.center
                    radius = circle.dxf.radius
                    diameter = round(radius * 2, 3)

                    holes.append(
                        {
                            "type": "circle",
                            "center_x": round(center[0], 3),
                            "center_y": round(center[1], 3),
                            "diameter": diameter,
                            "radius": round(radius, 3),
                        }
                    )
                except Exception as e:
                    logger.debug(f"Could not extract circle: {e}")

            # Store holes in materials field (repurposing for geometric data)
            analysis.materials = holes
            logger.info(f"  Extracted {len(holes)} holes/circles")

            # Extract bend lines from LINE and ARC entities
            bend_lines = []

            # Extract lines
            for line in modelspace.query("LINE"):
                try:
                    start = line.dxf.start
                    end = line.dxf.end
                    length = (
                        (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
                    ) ** 0.5

                    bend_lines.append(
                        {
                            "type": "line",
                            "start_x": round(start[0], 3),
                            "start_y": round(start[1], 3),
                            "end_x": round(end[0], 3),
                            "end_y": round(end[1], 3),
                            "length": round(length, 3),
                        }
                    )
                except Exception as e:
                    logger.debug(f"Could not extract line: {e}")

            # Extract arcs
            for arc in modelspace.query("ARC"):
                try:
                    center = arc.dxf.center
                    radius = arc.dxf.radius
                    start_angle = arc.dxf.start_angle
                    end_angle = arc.dxf.end_angle

                    bend_lines.append(
                        {
                            "type": "arc",
                            "center_x": round(center[0], 3),
                            "center_y": round(center[1], 3),
                            "radius": round(radius, 3),
                            "start_angle": round(start_angle, 2),
                            "end_angle": round(end_angle, 2),
                        }
                    )
                except Exception as e:
                    logger.debug(f"Could not extract arc: {e}")

            # Store bend lines in weld_callouts field (repurposing for geometric data)
            analysis.weld_callouts = bend_lines
            logger.info(f"  Extracted {len(bend_lines)} lines/arcs")

            # Extract text entities
            text_parts = []
            for text_entity in modelspace.query("TEXT"):
                try:
                    text = text_entity.dxf.text
                    if text:
                        text_parts.append(text)
                except Exception as e:
                    logger.debug(f"Could not extract text: {e}")

            for mtext_entity in modelspace.query("MTEXT"):
                try:
                    text = mtext_entity.text
                    if text:
                        text_parts.append(text)
                except Exception as e:
                    logger.debug(f"Could not extract mtext: {e}")

            analysis.extracted_text = "\n".join(text_parts)
            logger.info(f"  Extracted {len(text_parts)} text entities")

            # Try to extract metadata from text
            if analysis.extracted_text:
                self._extract_metadata(analysis)

            # Extract layer information
            layers = list(doc.layers)
            analysis.notes = [f"Layer: {layer.dxf.name}" for layer in layers[:20]]
            logger.info(f"  Found {len(layers)} layers")

            duration_ms = int((time.time() - start_time) * 1000)
            analysis.analysis_duration_ms = duration_ms

            logger.info(f"DXF analysis complete in {duration_ms}ms:")
            logger.info(f"  Dimensions: {len(analysis.dimensions)}")
            logger.info(f"  Holes: {len(analysis.materials)}")
            logger.info(f"  Lines/Arcs: {len(analysis.weld_callouts)}")
            logger.info(f"  Text entities: {len(text_parts)}")

        except ImportError:
            error_msg = "ezdxf library not installed - run: pip install ezdxf"
            logger.error(error_msg)
            analysis.errors.append(error_msg)

        except Exception as e:
            error_msg = f"DXF analysis failed: {e}"
            logger.error(error_msg, exc_info=True)
            analysis.errors.append(error_msg)

        return analysis
