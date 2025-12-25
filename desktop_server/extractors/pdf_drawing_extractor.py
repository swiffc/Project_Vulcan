"""
PDF Drawing Extractor
=====================
Extract structured data from engineering drawing PDFs.
Supports E&C FINFANS drawing types: M-series (Headers), S-series (Structures), CS-series (Shipping).

Phase 25.1 Implementation
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum

logger = logging.getLogger("vulcan.extractor.pdf_drawing")


class DrawingType(Enum):
    """Types of E&C FINFANS engineering drawings."""
    HEADER = "M"  # M-series: Header Details
    STRUCTURE = "S"  # S-series: Structure/Shop Assemblies
    SHIPPING = "CS"  # CS-series: Certified Shipping/Lifting
    UNKNOWN = "UNKNOWN"


@dataclass
class TitleBlockData:
    """Extracted title block information."""
    part_number: str = ""
    revision: str = ""
    customer: str = ""
    project: str = ""
    job_number: str = ""
    drawing_date: str = ""
    drawn_by: str = ""
    checked_by: str = ""
    approved_by: str = ""
    sheet: str = ""
    scale: str = ""
    drawing_type: DrawingType = DrawingType.UNKNOWN
    title: str = ""
    description: str = ""


@dataclass
class BOMItem:
    """Single BOM (Bill of Materials) line item."""
    item_number: int = 0
    part_number: str = ""
    description: str = ""
    material: str = ""
    material_spec: str = ""  # e.g., SA-516-70, SA-350-LF2
    quantity: int = 1
    unit: str = "EA"
    size: str = ""
    weight_each: float = 0.0
    weight_total: float = 0.0
    raw_material_pn: str = ""  # RM part number


@dataclass
class WeldSymbol:
    """Extracted weld symbol data."""
    weld_type: str = ""  # Fillet, Groove, Plug, etc.
    size: str = ""  # Weld size (e.g., 1/4", 3/8")
    length: str = ""  # Weld length if specified
    pitch: str = ""  # Pitch for intermittent welds
    process: str = ""  # GMAW, GTAW, SMAW, etc.
    procedure: str = ""  # WPS number (e.g., P1A-4, P1TM-1)
    arrow_side: bool = True
    other_side: bool = False
    all_around: bool = False
    field_weld: bool = False
    nde_requirement: str = ""  # RT, UT, MT, PT
    joint_type: str = ""  # Butt, Lap, Tee, Corner
    penetration: str = ""  # Full, Partial


@dataclass
class Dimension:
    """Extracted dimension with units."""
    value_imperial: float = 0.0
    value_metric: float = 0.0
    unit_imperial: str = "in"
    unit_metric: str = "mm"
    tolerance_plus: Optional[float] = None
    tolerance_minus: Optional[float] = None
    dimension_type: str = ""  # Length, Diameter, Radius, Angle
    reference: str = ""  # Datum or feature reference
    is_basic: bool = False
    is_reference: bool = False


@dataclass
class RevisionEntry:
    """Single revision history entry."""
    revision: str = ""
    date: str = ""
    description: str = ""
    ecn_number: str = ""
    by: str = ""
    approved_by: str = ""


@dataclass
class DesignData:
    """Extracted design/pressure vessel data."""
    mawp_psi: float = 0.0
    mawp_bar: float = 0.0
    design_pressure_psi: float = 0.0
    design_temperature_f: float = 0.0
    design_temperature_c: float = 0.0
    mdmt_f: float = 0.0
    mdmt_c: float = 0.0
    test_pressure_psi: float = 0.0
    corrosion_allowance_in: float = 0.0
    design_code: str = ""  # ASME VIII Div 1, etc.
    joint_efficiency: float = 1.0
    stamp_required: bool = False
    pwht_required: bool = False
    radiography: str = ""  # Full, Spot, None
    service: str = ""


@dataclass
class GeneralNotes:
    """Extracted general and shop notes."""
    general_notes: List[str] = field(default_factory=list)
    shop_notes: List[str] = field(default_factory=list)
    welding_notes: List[str] = field(default_factory=list)
    material_notes: List[str] = field(default_factory=list)
    painting_notes: List[str] = field(default_factory=list)
    inspection_notes: List[str] = field(default_factory=list)


@dataclass
class DrawingExtractionResult:
    """Complete extraction result from a PDF drawing."""
    file_path: str = ""
    page_count: int = 0
    drawing_type: DrawingType = DrawingType.UNKNOWN
    title_block: TitleBlockData = field(default_factory=TitleBlockData)
    bom_items: List[BOMItem] = field(default_factory=list)
    weld_symbols: List[WeldSymbol] = field(default_factory=list)
    dimensions: List[Dimension] = field(default_factory=list)
    revisions: List[RevisionEntry] = field(default_factory=list)
    design_data: DesignData = field(default_factory=DesignData)
    notes: GeneralNotes = field(default_factory=GeneralNotes)
    raw_text: str = ""
    extraction_errors: List[str] = field(default_factory=list)
    extraction_warnings: List[str] = field(default_factory=list)


class PDFDrawingExtractor:
    """
    Extract structured data from E&C FINFANS engineering drawing PDFs.

    Supports:
    - M-series: Header Details (M169-6A, M180-10AF, etc.)
    - S-series: Structure/Shop Assemblies (S24400-10AS, etc.)
    - CS-series: Certified Shipping/Lifting (CS23456-7A-SWLA, etc.)
    """

    # Regex patterns for extraction
    PATTERNS = {
        # Part number patterns
        "part_number_m": re.compile(r'M(\d{3,5})-(\d+[A-Z]*)', re.I),
        "part_number_s": re.compile(r'S(\d{4,5})-(\d+[A-Z]*)', re.I),
        "part_number_cs": re.compile(r'CS(\d{4,5})-(\d+[A-Z]*)', re.I),
        "part_number_generic": re.compile(r'(?:PART\s*(?:NO|#|NUMBER)?[:\s]*)([A-Z0-9\-]+)', re.I),

        # Revision
        "revision": re.compile(r'REV(?:ISION)?[:\s]*([A-Z0-9]+)', re.I),

        # Customer/Project
        "customer": re.compile(r'CUSTOMER[:\s]*(.+?)(?:\n|$)', re.I),
        "project": re.compile(r'PROJECT[:\s]*(.+?)(?:\n|$)', re.I),
        "job_number": re.compile(r'(?:JOB|ORDER)\s*(?:NO|#|NUMBER)?[:\s]*([A-Z0-9\-]+)', re.I),

        # Drawing info
        "drawn_by": re.compile(r'(?:DRAWN|DRN)\s*(?:BY)?[:\s]*([A-Z]{2,4})', re.I),
        "checked_by": re.compile(r'(?:CHECKED|CHK|CK)\s*(?:BY)?[:\s]*([A-Z]{2,4})', re.I),
        "approved_by": re.compile(r'(?:APPROVED|APPR?|APP)\s*(?:BY)?[:\s]*([A-Z]{2,4})', re.I),
        "date": re.compile(r'DATE[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', re.I),
        "scale": re.compile(r'SCALE[:\s]*(\d+:\d+|FULL|NTS)', re.I),
        "sheet": re.compile(r'SHEET[:\s]*(\d+)\s*(?:OF|/)\s*(\d+)', re.I),

        # Material specifications (ASME/ASTM)
        "material_spec": re.compile(
            r'(SA|A|SB|B)-(\d{3,4})(?:-(\d+|[A-Z]+\d*))?(?:\s*(?:GR|GRADE)?\.?\s*([A-Z0-9]+))?',
            re.I
        ),

        # Dimensions (imperial and metric)
        "dimension_imperial": re.compile(
            r'(\d+(?:\.\d+)?)\s*(?:"|IN(?:CH)?(?:ES)?)?(?:\s*[±+\-]\s*(\d+(?:\.\d+)?))?',
            re.I
        ),
        "dimension_metric": re.compile(
            r'(\d+(?:\.\d+)?)\s*(?:MM|CM|M)(?:\s*[±+\-]\s*(\d+(?:\.\d+)?))?',
            re.I
        ),
        "dimension_dual": re.compile(
            r'(\d+(?:\.\d+)?)\s*(?:"|IN)?\s*[\[\(](\d+(?:\.\d+)?)\s*(?:MM)?\s*[\]\)]',
            re.I
        ),

        # Pressure/Temperature data
        "mawp": re.compile(r'MAWP[:\s]*(\d+(?:\.\d+)?)\s*(?:PSI|PSIG)?', re.I),
        "design_pressure": re.compile(r'DESIGN\s*(?:PRESS(?:URE)?)?[:\s]*(\d+(?:\.\d+)?)\s*(?:PSI|PSIG)?', re.I),
        "design_temp": re.compile(r'DESIGN\s*(?:TEMP(?:ERATURE)?)?[:\s]*(\d+(?:\.\d+)?)\s*[°]?F?', re.I),
        "mdmt": re.compile(r'MDMT[:\s]*([+-]?\d+(?:\.\d+)?)\s*[°]?F?', re.I),
        "test_pressure": re.compile(r'(?:HYDRO|TEST)\s*(?:PRESS(?:URE)?)?[:\s]*(\d+(?:\.\d+)?)\s*(?:PSI|PSIG)?', re.I),
        "corrosion_allowance": re.compile(r'(?:CORR(?:OSION)?|C\.?A\.?)\s*(?:ALL(?:OWANCE)?)?[:\s]*(\d+(?:\.\d+)?)\s*(?:"|IN)?', re.I),

        # Weld procedures
        "weld_procedure": re.compile(r'(P\d+[A-Z]*-\d+[A-Z]*)', re.I),
        "weld_size": re.compile(r'(\d+/\d+|\d+(?:\.\d+)?)\s*(?:"|IN)?\s*(?:FILLET|FIL)', re.I),

        # Design code
        "design_code": re.compile(r'(?:ASME|API|TEMA)\s*(?:SEC(?:TION)?|VIII|661|C|R)?(?:\s*DIV(?:ISION)?\s*\d)?', re.I),

        # Flange ratings
        "flange_rating": re.compile(r'(\d{3,4})\s*(?:#|LB|CLASS)', re.I),
        "flange_type": re.compile(r'(WN|SO|BL|LJ|SW|TH|LWN|BLD)\s*(?:FLG|FLANGE)?', re.I),

        # Notes patterns
        "numbered_note": re.compile(r'^(\d+)[.\)]\s*(.+)$', re.MULTILINE),
        "general_note": re.compile(r'GENERAL\s*NOTE[S]?[:\s]*', re.I),
        "shop_note": re.compile(r'SHOP\s*NOTE[S]?[:\s]*', re.I),
        "weld_note": re.compile(r'WELD(?:ING)?\s*NOTE[S]?[:\s]*', re.I),
    }

    def __init__(self, dpi: int = 300):
        """Initialize the PDF drawing extractor."""
        self.dpi = dpi
        self._ocr_available = False
        self._pypdf_available = False
        self._check_dependencies()

    def _check_dependencies(self):
        """Check available PDF processing libraries."""
        try:
            import pypdf
            self._pypdf_available = True
            logger.info("pypdf available for text extraction")
        except ImportError:
            logger.warning("pypdf not available")

        try:
            import pytesseract
            from pdf2image import convert_from_path
            self._ocr_available = True
            logger.info("OCR (pytesseract + pdf2image) available")
        except ImportError:
            logger.warning("OCR not available - install pytesseract and pdf2image")

    def extract(self, pdf_path: str) -> DrawingExtractionResult:
        """
        Extract all data from a PDF engineering drawing.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            DrawingExtractionResult with all extracted data
        """
        result = DrawingExtractionResult(file_path=pdf_path)

        if not Path(pdf_path).exists():
            result.extraction_errors.append(f"File not found: {pdf_path}")
            return result

        # Try pypdf first for text extraction
        raw_text = ""
        if self._pypdf_available:
            raw_text = self._extract_text_pypdf(pdf_path, result)

        # Fall back to OCR if text extraction fails or is insufficient
        if len(raw_text) < 100 and self._ocr_available:
            logger.info("Text extraction insufficient, trying OCR")
            raw_text = self._extract_text_ocr(pdf_path, result)

        result.raw_text = raw_text

        if not raw_text:
            result.extraction_errors.append("Failed to extract text from PDF")
            return result

        # Detect drawing type
        result.drawing_type = self._detect_drawing_type(raw_text)

        # Extract all components
        result.title_block = self._extract_title_block(raw_text)
        result.title_block.drawing_type = result.drawing_type

        result.bom_items = self._extract_bom(raw_text)
        result.weld_symbols = self._extract_weld_symbols(raw_text)
        result.dimensions = self._extract_dimensions(raw_text)
        result.revisions = self._extract_revisions(raw_text)
        result.design_data = self._extract_design_data(raw_text)
        result.notes = self._extract_notes(raw_text)

        return result

    def _extract_text_pypdf(self, pdf_path: str, result: DrawingExtractionResult) -> str:
        """Extract text using pypdf."""
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            result.page_count = len(reader.pages)

            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)

            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"pypdf extraction failed: {e}")
            result.extraction_errors.append(f"pypdf error: {str(e)}")
            return ""

    def _extract_text_ocr(self, pdf_path: str, result: DrawingExtractionResult) -> str:
        """Extract text using OCR (pytesseract + pdf2image)."""
        try:
            from pdf2image import convert_from_path
            import pytesseract

            images = convert_from_path(pdf_path, dpi=self.dpi)
            result.page_count = len(images)

            text_parts = []
            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img)
                text_parts.append(page_text)
                logger.debug(f"OCR page {i+1}: {len(page_text)} chars")

            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            result.extraction_errors.append(f"OCR error: {str(e)}")
            return ""

    def _detect_drawing_type(self, text: str) -> DrawingType:
        """Detect the drawing type from part number prefix."""
        if self.PATTERNS["part_number_cs"].search(text):
            return DrawingType.SHIPPING
        elif self.PATTERNS["part_number_m"].search(text):
            return DrawingType.HEADER
        elif self.PATTERNS["part_number_s"].search(text):
            return DrawingType.STRUCTURE
        return DrawingType.UNKNOWN

    def _extract_title_block(self, text: str) -> TitleBlockData:
        """Extract title block information."""
        tb = TitleBlockData()

        # Part number - try specific patterns first
        for pattern_name in ["part_number_cs", "part_number_m", "part_number_s", "part_number_generic"]:
            match = self.PATTERNS[pattern_name].search(text)
            if match:
                tb.part_number = match.group(0).upper()
                break

        # Revision
        match = self.PATTERNS["revision"].search(text)
        if match:
            tb.revision = match.group(1).upper()

        # Customer
        match = self.PATTERNS["customer"].search(text)
        if match:
            tb.customer = match.group(1).strip()

        # Project
        match = self.PATTERNS["project"].search(text)
        if match:
            tb.project = match.group(1).strip()

        # Job number
        match = self.PATTERNS["job_number"].search(text)
        if match:
            tb.job_number = match.group(1).strip()

        # Drawn by
        match = self.PATTERNS["drawn_by"].search(text)
        if match:
            tb.drawn_by = match.group(1).upper()

        # Checked by
        match = self.PATTERNS["checked_by"].search(text)
        if match:
            tb.checked_by = match.group(1).upper()

        # Approved by
        match = self.PATTERNS["approved_by"].search(text)
        if match:
            tb.approved_by = match.group(1).upper()

        # Date
        match = self.PATTERNS["date"].search(text)
        if match:
            tb.drawing_date = match.group(1)

        # Scale
        match = self.PATTERNS["scale"].search(text)
        if match:
            tb.scale = match.group(1).upper()

        # Sheet
        match = self.PATTERNS["sheet"].search(text)
        if match:
            tb.sheet = f"{match.group(1)} OF {match.group(2)}"

        return tb

    def _extract_bom(self, text: str) -> List[BOMItem]:
        """Extract BOM (Bill of Materials) items."""
        bom_items = []

        # Look for BOM table patterns
        # Typical format: ITEM | PART NO | DESCRIPTION | MATERIAL | QTY
        bom_pattern = re.compile(
            r'^\s*(\d+)\s+'  # Item number
            r'([A-Z0-9\-]+)\s+'  # Part number
            r'(.+?)\s+'  # Description
            r'((?:SA|A|SB)-\d{3}[^\s]*)\s+'  # Material spec
            r'(\d+)',  # Quantity
            re.MULTILINE | re.I
        )

        for match in bom_pattern.finditer(text):
            item = BOMItem()
            item.item_number = int(match.group(1))
            item.part_number = match.group(2).upper()
            item.description = match.group(3).strip()
            item.material_spec = match.group(4).upper()
            item.quantity = int(match.group(5))

            # Parse material spec to get base material
            item.material = self._parse_material_spec(item.material_spec)

            bom_items.append(item)

        # Also extract individual material specs from text
        for match in self.PATTERNS["material_spec"].finditer(text):
            spec = match.group(0).upper()
            # Check if this spec is already in a BOM item
            if not any(item.material_spec == spec for item in bom_items):
                # Create a "found material" entry
                item = BOMItem()
                item.material_spec = spec
                item.material = self._parse_material_spec(spec)
                bom_items.append(item)

        return bom_items

    def _parse_material_spec(self, spec: str) -> str:
        """Parse material specification to human-readable name."""
        spec_upper = spec.upper()

        material_names = {
            "SA-516-70": "Carbon Steel Plate (Gr 70)",
            "SA-516-65": "Carbon Steel Plate (Gr 65)",
            "SA-350-LF2": "Low-Temp Carbon Steel Forging",
            "SA-105": "Carbon Steel Forging",
            "SA-193-B7": "Alloy Steel Bolting",
            "SA-194-2H": "Carbon Steel Heavy Hex Nuts",
            "SA-240-304": "Stainless Steel 304 Plate",
            "SA-240-316": "Stainless Steel 316 Plate",
            "SA-312-304": "Stainless Steel 304 Pipe",
            "SA-312-316": "Stainless Steel 316 Pipe",
            "A36": "Structural Carbon Steel",
            "A572-50": "HSLA Structural Steel",
            "A325": "Structural Bolts",
            "A490": "High-Strength Structural Bolts",
        }

        for pattern, name in material_names.items():
            if pattern in spec_upper:
                return name

        return spec_upper

    def _extract_weld_symbols(self, text: str) -> List[WeldSymbol]:
        """Extract weld symbols and specifications."""
        welds = []

        # Find weld procedures
        for match in self.PATTERNS["weld_procedure"].finditer(text):
            weld = WeldSymbol()
            weld.procedure = match.group(1).upper()
            welds.append(weld)

        # Find weld sizes
        for match in self.PATTERNS["weld_size"].finditer(text):
            weld = WeldSymbol()
            weld.size = match.group(1)
            weld.weld_type = "FILLET"
            welds.append(weld)

        # Look for specific weld callouts
        weld_callout = re.compile(
            r'(\d+/\d+|\d+(?:\.\d+)?)\s*(?:"|IN)?\s*'  # Size
            r'(FILLET|FIL|GROOVE|GRV|PLUG|SLOT|BUTT)\s*'  # Type
            r'(?:WELD)?\s*'
            r'(?:(ALL\s*AROUND|FIELD))?\s*'  # Modifiers
            r'(?:WPS|PROC)?[:\s]*(P\d+[A-Z\-\d]+)?',  # Procedure
            re.I
        )

        for match in weld_callout.finditer(text):
            weld = WeldSymbol()
            weld.size = match.group(1)
            weld.weld_type = match.group(2).upper()
            if match.group(3):
                modifier = match.group(3).upper()
                weld.all_around = "ALL" in modifier
                weld.field_weld = "FIELD" in modifier
            if match.group(4):
                weld.procedure = match.group(4).upper()
            welds.append(weld)

        return welds

    def _extract_dimensions(self, text: str) -> List[Dimension]:
        """Extract dimensions with imperial and metric values."""
        dimensions = []

        # Dual dimension pattern (imperial [metric])
        for match in self.PATTERNS["dimension_dual"].finditer(text):
            dim = Dimension()
            dim.value_imperial = float(match.group(1))
            dim.value_metric = float(match.group(2))
            dim.unit_imperial = "in"
            dim.unit_metric = "mm"
            dimensions.append(dim)

        # Single imperial dimensions
        for match in self.PATTERNS["dimension_imperial"].finditer(text):
            dim = Dimension()
            dim.value_imperial = float(match.group(1))
            dim.value_metric = dim.value_imperial * 25.4  # Convert to mm
            if match.group(2):
                dim.tolerance_plus = float(match.group(2))
                dim.tolerance_minus = float(match.group(2))
            dimensions.append(dim)

        return dimensions

    def _extract_revisions(self, text: str) -> List[RevisionEntry]:
        """Extract revision history entries."""
        revisions = []

        # Look for revision table pattern
        # REV | DATE | DESCRIPTION | BY
        rev_pattern = re.compile(
            r'^\s*([A-Z]|NC|0)\s+'  # Revision letter/number
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s+'  # Date
            r'(.+?)\s+'  # Description
            r'([A-Z]{2,4})',  # By initials
            re.MULTILINE | re.I
        )

        for match in rev_pattern.finditer(text):
            rev = RevisionEntry()
            rev.revision = match.group(1).upper()
            rev.date = match.group(2)
            rev.description = match.group(3).strip()
            rev.by = match.group(4).upper()
            revisions.append(rev)

        # Look for ECN numbers
        ecn_pattern = re.compile(r'ECN[:\s#]*(\d+)', re.I)
        for i, match in enumerate(ecn_pattern.finditer(text)):
            if i < len(revisions):
                revisions[i].ecn_number = match.group(1)

        return revisions

    def _extract_design_data(self, text: str) -> DesignData:
        """Extract pressure vessel design data."""
        data = DesignData()

        # MAWP
        match = self.PATTERNS["mawp"].search(text)
        if match:
            data.mawp_psi = float(match.group(1))
            data.mawp_bar = data.mawp_psi * 0.0689476

        # Design pressure
        match = self.PATTERNS["design_pressure"].search(text)
        if match:
            data.design_pressure_psi = float(match.group(1))

        # Design temperature
        match = self.PATTERNS["design_temp"].search(text)
        if match:
            data.design_temperature_f = float(match.group(1))
            data.design_temperature_c = (data.design_temperature_f - 32) * 5/9

        # MDMT
        match = self.PATTERNS["mdmt"].search(text)
        if match:
            data.mdmt_f = float(match.group(1))
            data.mdmt_c = (data.mdmt_f - 32) * 5/9

        # Test pressure
        match = self.PATTERNS["test_pressure"].search(text)
        if match:
            data.test_pressure_psi = float(match.group(1))

        # Corrosion allowance
        match = self.PATTERNS["corrosion_allowance"].search(text)
        if match:
            data.corrosion_allowance_in = float(match.group(1))

        # Design code
        match = self.PATTERNS["design_code"].search(text)
        if match:
            data.design_code = match.group(0).upper()

        # Check for PWHT requirement
        if re.search(r'PWHT\s*(?:REQ|REQUIRED)', text, re.I):
            data.pwht_required = True

        # Check for radiography
        if re.search(r'FULL\s*(?:RT|RADIOGRAPHY)', text, re.I):
            data.radiography = "FULL"
        elif re.search(r'SPOT\s*(?:RT|RADIOGRAPHY)', text, re.I):
            data.radiography = "SPOT"

        return data

    def _extract_notes(self, text: str) -> GeneralNotes:
        """Extract general and shop notes."""
        notes = GeneralNotes()

        # Find all numbered notes
        for match in self.PATTERNS["numbered_note"].finditer(text):
            note_text = match.group(2).strip()
            note_lower = note_text.lower()

            # Categorize notes
            if any(kw in note_lower for kw in ["weld", "wps", "gtaw", "gmaw", "smaw"]):
                notes.welding_notes.append(note_text)
            elif any(kw in note_lower for kw in ["material", "spec", "grade", "astm", "asme"]):
                notes.material_notes.append(note_text)
            elif any(kw in note_lower for kw in ["paint", "coat", "primer", "finish"]):
                notes.painting_notes.append(note_text)
            elif any(kw in note_lower for kw in ["inspect", "nde", "test", "rt", "ut", "mt", "pt"]):
                notes.inspection_notes.append(note_text)
            else:
                notes.general_notes.append(note_text)

        # Look for specific note sections
        shop_match = self.PATTERNS["shop_note"].search(text)
        if shop_match:
            # Get text after "SHOP NOTES:" until next section
            start = shop_match.end()
            end = text.find("\n\n", start)
            if end == -1:
                end = len(text)
            shop_text = text[start:end]
            notes.shop_notes.extend(line.strip() for line in shop_text.split("\n") if line.strip())

        return notes

    def to_dict(self, result: DrawingExtractionResult) -> Dict[str, Any]:
        """Convert extraction result to dictionary for JSON serialization."""
        return {
            "file_path": result.file_path,
            "page_count": result.page_count,
            "drawing_type": result.drawing_type.value,
            "title_block": {
                "part_number": result.title_block.part_number,
                "revision": result.title_block.revision,
                "customer": result.title_block.customer,
                "project": result.title_block.project,
                "job_number": result.title_block.job_number,
                "drawing_date": result.title_block.drawing_date,
                "drawn_by": result.title_block.drawn_by,
                "checked_by": result.title_block.checked_by,
                "approved_by": result.title_block.approved_by,
                "sheet": result.title_block.sheet,
                "scale": result.title_block.scale,
            },
            "bom_items": [
                {
                    "item_number": item.item_number,
                    "part_number": item.part_number,
                    "description": item.description,
                    "material": item.material,
                    "material_spec": item.material_spec,
                    "quantity": item.quantity,
                }
                for item in result.bom_items
            ],
            "weld_symbols": [
                {
                    "weld_type": w.weld_type,
                    "size": w.size,
                    "procedure": w.procedure,
                    "all_around": w.all_around,
                    "field_weld": w.field_weld,
                }
                for w in result.weld_symbols
            ],
            "design_data": {
                "mawp_psi": result.design_data.mawp_psi,
                "design_pressure_psi": result.design_data.design_pressure_psi,
                "design_temperature_f": result.design_data.design_temperature_f,
                "mdmt_f": result.design_data.mdmt_f,
                "test_pressure_psi": result.design_data.test_pressure_psi,
                "corrosion_allowance_in": result.design_data.corrosion_allowance_in,
                "design_code": result.design_data.design_code,
                "pwht_required": result.design_data.pwht_required,
                "radiography": result.design_data.radiography,
            },
            "revisions": [
                {
                    "revision": r.revision,
                    "date": r.date,
                    "description": r.description,
                    "ecn_number": r.ecn_number,
                    "by": r.by,
                }
                for r in result.revisions
            ],
            "notes": {
                "general_notes": result.notes.general_notes,
                "shop_notes": result.notes.shop_notes,
                "welding_notes": result.notes.welding_notes,
                "material_notes": result.notes.material_notes,
                "painting_notes": result.notes.painting_notes,
                "inspection_notes": result.notes.inspection_notes,
            },
            "extraction_errors": result.extraction_errors,
            "extraction_warnings": result.extraction_warnings,
        }
