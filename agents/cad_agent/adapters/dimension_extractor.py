"""
Dimension Extractor Adapter
===========================
Enhanced OCR for extracting dimensions from engineering drawings.
Uses zone detection and pattern matching for accurate extraction.

Key Features:
- Title block zone detection
- Dimension zone isolation
- Multi-format dimension parsing (feet-inches, fractions, decimals, metric)
- Tolerance extraction
- Reference dimension detection
- GD&T symbol recognition

Uses:
- pytesseract: OCR engine
- Pillow: Image processing
- OpenCV: Zone detection (optional)

References:
- VERIFICATION_REQUIREMENTS.md Section 2.2

Usage:
    from agents.cad_agent.adapters.dimension_extractor import DimensionExtractor

    extractor = DimensionExtractor()
    dims = extractor.extract_from_image(image)
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

logger = logging.getLogger("cad_agent.dimension-extractor")


# =============================================================================
# CONSTANTS
# =============================================================================

# Common engineering drawing zones
ZONE_RATIOS = {
    # Zone: (x_start, y_start, x_end, y_end) as ratio of image dimensions
    "title_block": (0.6, 0.85, 1.0, 1.0),  # Bottom right
    "revision_block": (0.8, 0.0, 1.0, 0.15),  # Top right
    "parts_list": (0.0, 0.0, 0.4, 0.25),  # Top left
    "main_view": (0.1, 0.15, 0.85, 0.85),  # Center
    "notes": (0.0, 0.7, 0.3, 1.0),  # Bottom left
}


# =============================================================================
# ENUMS & DATA MODELS
# =============================================================================

class DimensionType(Enum):
    """Type of dimension."""
    LINEAR = "linear"
    ANGULAR = "angular"
    RADIAL = "radial"
    DIAMETER = "diameter"
    REFERENCE = "reference"
    BASIC = "basic"
    ORDINATE = "ordinate"


class Unit(Enum):
    """Dimension unit."""
    INCH = "in"
    FEET = "ft"
    FEET_INCHES = "ft-in"
    MILLIMETER = "mm"
    CENTIMETER = "cm"
    METER = "m"
    DEGREE = "deg"


@dataclass
class Tolerance:
    """Dimension tolerance."""
    upper: float = 0.0
    lower: float = 0.0
    bilateral: bool = True  # True if ± style, False if +/- separate

    @property
    def is_symmetric(self) -> bool:
        return abs(self.upper + self.lower) < 0.0001

    def __str__(self) -> str:
        if self.bilateral and self.is_symmetric:
            return f"±{abs(self.upper)}"
        return f"+{self.upper}/-{abs(self.lower)}"


@dataclass
class ExtractedDimension:
    """A single extracted dimension."""
    value: float
    unit: Unit = Unit.INCH
    dim_type: DimensionType = DimensionType.LINEAR
    tolerance: Optional[Tolerance] = None
    raw_text: str = ""
    confidence: float = 0.0
    zone: str = ""
    position: tuple[int, int] = (0, 0)  # x, y in image
    is_reference: bool = False

    @property
    def formatted(self) -> str:
        """Return formatted dimension string."""
        if self.unit == Unit.FEET_INCHES:
            feet = int(self.value // 12)
            inches = self.value % 12
            return f"{feet}'-{inches:.4g}\""
        elif self.unit == Unit.INCH:
            return f"{self.value:.4g}\""
        elif self.unit == Unit.MILLIMETER:
            return f"{self.value:.2f}mm"
        elif self.unit == Unit.DEGREE:
            return f"{self.value:.1f}°"
        return f"{self.value:.4g}"


@dataclass
class TitleBlockData:
    """Data extracted from title block zone."""
    part_number: str = ""
    description: str = ""
    material: str = ""
    revision: str = ""
    drawn_by: str = ""
    checked_by: str = ""
    date: str = ""
    scale: str = ""
    weight: Optional[float] = None
    sheet: str = ""
    finish: str = ""


@dataclass
class ExtractionResult:
    """Complete extraction result."""
    dimensions: list[ExtractedDimension] = field(default_factory=list)
    title_block: Optional[TitleBlockData] = None
    notes: list[str] = field(default_factory=list)
    zones_detected: list[str] = field(default_factory=list)
    raw_text: str = ""
    processing_time_ms: float = 0.0
    confidence_score: float = 0.0


# =============================================================================
# REGEX PATTERNS
# =============================================================================

DIMENSION_PATTERNS = {
    # Feet and inches: 6'-8 3/16", 12'-0"
    "feet_inches": re.compile(
        r"(\d+)['\u2032]\s*-?\s*(\d+)\s*(?:(\d+)\s*/\s*(\d+))?\s*[\"″\u2033]?",
        re.UNICODE
    ),

    # Fractional inches: 1-1/4", 3/8", 15/16
    "fraction": re.compile(
        r"(\d+)?\s*-?\s*(\d+)\s*/\s*(\d+)\s*[\"″]?"
    ),

    # Decimal inches with tolerance: 1.250 ±.005, 2.000 +.010/-.005
    "decimal_tolerance": re.compile(
        r"(\d+\.?\d*)\s*[\"″]?\s*(?:[±]\s*([\d.]+)|(?:\+\s*([\d.]+)\s*[/-]\s*-?\s*([\d.]+)))"
    ),

    # Plain decimal inches: 1.250", 0.375
    "decimal": re.compile(
        r"(\d+\.\d+)\s*[\"″]?"
    ),

    # Metric: 25.4mm, 100 mm
    "metric": re.compile(
        r"(\d+\.?\d*)\s*(?:mm|MM)"
    ),

    # Angular: 45°, 90 DEG, 30°30'
    "angular": re.compile(
        r"(\d+\.?\d*)\s*(?:°|DEG|DEGREES?)(?:\s*(\d+)['\u2032])?"
    ),

    # Diameter: Ø1.250, DIA 1.5
    "diameter": re.compile(
        r"(?:[ØΦ∅]|DIA\.?)\s*(\d+\.?\d*)\s*[\"″]?"
    ),

    # Radius: R.500, RAD 1.0
    "radius": re.compile(
        r"(?:R|RAD\.?)\s*(\d+\.?\d*)\s*[\"″]?"
    ),

    # Reference dimension: (1.250), [1.250]
    "reference": re.compile(
        r"[\(\[](\d+\.?\d*)[\)\]]\s*[\"″]?"
    ),

    # Basic dimension: ⬜1.250 or boxed
    "basic": re.compile(
        r"[⬜□▢]\s*(\d+\.?\d*)\s*[\"″]?"
    ),
}

TITLE_BLOCK_PATTERNS = {
    "part_number": re.compile(
        r"(?:P/?N|PART\s*(?:NO|NUMBER|#)|DWG\s*(?:NO)?)[:\s]*([A-Z0-9]+-[A-Z0-9]+(?:-[A-Z0-9]+)?)",
        re.IGNORECASE
    ),
    "description": re.compile(
        r"(?:DESC(?:RIPTION)?|TITLE)[:\s]*([A-Z0-9\s\-_,]+?)(?:\n|$)",
        re.IGNORECASE
    ),
    "material": re.compile(
        r"(?:MATERIAL|MTL|MATL)[:\s]*([A-Z0-9\s\-_/]+?)(?:\n|$)",
        re.IGNORECASE
    ),
    "weight": re.compile(
        r"(?:WT|WEIGHT)[:\s]*([\d.]+)\s*(LBS?|KG)?",
        re.IGNORECASE
    ),
    "revision": re.compile(
        r"(?:REV(?:ISION)?)[:\s]*([A-Z0-9]+)",
        re.IGNORECASE
    ),
    "scale": re.compile(
        r"SCALE[:\s]*([\d]+\s*[:/]\s*[\d]+|FULL|NTS|NONE)",
        re.IGNORECASE
    ),
    "drawn_by": re.compile(
        r"(?:DRAWN|DR)[:\s]*([A-Z]{2,4})",
        re.IGNORECASE
    ),
    "checked_by": re.compile(
        r"(?:CHECKED|CHK|CK)[:\s]*([A-Z]{2,4})",
        re.IGNORECASE
    ),
    "date": re.compile(
        r"DATE[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        re.IGNORECASE
    ),
    "sheet": re.compile(
        r"SHEET[:\s]*(\d+)\s*(?:OF\s*(\d+))?",
        re.IGNORECASE
    ),
    "finish": re.compile(
        r"FINISH[:\s]*(GALV(?:ANIZED)?|HDG|PAINTED|BARE|MECH\s*GALV)",
        re.IGNORECASE
    ),
}


# =============================================================================
# DIMENSION EXTRACTOR
# =============================================================================

class DimensionExtractor:
    """
    Extract dimensions from engineering drawings using OCR.

    Features:
    - Zone-based extraction (title block, main view, notes)
    - Multi-format dimension parsing
    - Tolerance extraction
    - GD&T symbol recognition
    """

    def __init__(
        self,
        dpi: int = 300,
        default_unit: Unit = Unit.INCH,
        use_zones: bool = True,
    ):
        self.dpi = dpi
        self.default_unit = default_unit
        self.use_zones = use_zones

    def extract_from_image(self, image) -> ExtractionResult:
        """
        Extract dimensions from a PIL image.

        Args:
            image: PIL Image object

        Returns:
            ExtractionResult with all extracted data
        """
        import time
        import pytesseract

        start_time = time.perf_counter()

        # Get full text
        raw_text = pytesseract.image_to_string(image)

        dimensions = []
        title_block = None
        notes = []
        zones_detected = []

        if self.use_zones:
            # Extract from zones
            zones = self._detect_zones(image)
            zones_detected = list(zones.keys())

            # Process title block
            if "title_block" in zones:
                tb_image = zones["title_block"]
                tb_text = pytesseract.image_to_string(tb_image)
                title_block = self._extract_title_block(tb_text)

            # Process main view for dimensions
            if "main_view" in zones:
                mv_image = zones["main_view"]
                mv_text = pytesseract.image_to_string(mv_image)
                dimensions = self._extract_dimensions(mv_text, zone="main_view")

            # Process notes
            if "notes" in zones:
                notes_image = zones["notes"]
                notes_text = pytesseract.image_to_string(notes_image)
                notes = self._extract_notes(notes_text)

        else:
            # Process entire image
            title_block = self._extract_title_block(raw_text)
            dimensions = self._extract_dimensions(raw_text, zone="full")
            notes = self._extract_notes(raw_text)

        # Add any dimensions from full text not already found
        full_dims = self._extract_dimensions(raw_text, zone="full")
        for dim in full_dims:
            if not any(self._dims_match(dim, d) for d in dimensions):
                dimensions.append(dim)

        # Calculate confidence
        confidence = self._calculate_confidence(dimensions, title_block)

        elapsed = (time.perf_counter() - start_time) * 1000

        return ExtractionResult(
            dimensions=dimensions,
            title_block=title_block,
            notes=notes,
            zones_detected=zones_detected,
            raw_text=raw_text,
            processing_time_ms=elapsed,
            confidence_score=confidence,
        )

    def extract_from_pdf(self, pdf_path: str, page: int = 0) -> ExtractionResult:
        """
        Extract dimensions from a PDF page.

        Args:
            pdf_path: Path to PDF file
            page: Page number (0-indexed)

        Returns:
            ExtractionResult with all extracted data
        """
        from pdf2image import convert_from_path

        images = convert_from_path(pdf_path, dpi=self.dpi, first_page=page + 1, last_page=page + 1)

        if not images:
            return ExtractionResult()

        return self.extract_from_image(images[0])

    # -------------------------------------------------------------------------
    # ZONE DETECTION
    # -------------------------------------------------------------------------

    def _detect_zones(self, image) -> dict:
        """
        Detect standard zones in an engineering drawing.

        Returns dict of zone_name -> cropped PIL image
        """
        width, height = image.size
        zones = {}

        for zone_name, (x1_ratio, y1_ratio, x2_ratio, y2_ratio) in ZONE_RATIOS.items():
            x1 = int(width * x1_ratio)
            y1 = int(height * y1_ratio)
            x2 = int(width * x2_ratio)
            y2 = int(height * y2_ratio)

            cropped = image.crop((x1, y1, x2, y2))
            zones[zone_name] = cropped

        return zones

    # -------------------------------------------------------------------------
    # DIMENSION EXTRACTION
    # -------------------------------------------------------------------------

    def _extract_dimensions(self, text: str, zone: str = "") -> list[ExtractedDimension]:
        """Extract all dimensions from text."""
        dimensions = []

        # Feet and inches
        for match in DIMENSION_PATTERNS["feet_inches"].finditer(text):
            feet = int(match.group(1))
            inches = int(match.group(2))
            frac_num = int(match.group(3)) if match.group(3) else 0
            frac_den = int(match.group(4)) if match.group(4) else 1

            total_inches = feet * 12 + inches + (frac_num / frac_den if frac_den else 0)

            dimensions.append(ExtractedDimension(
                value=total_inches,
                unit=Unit.FEET_INCHES,
                dim_type=DimensionType.LINEAR,
                raw_text=match.group(0),
                confidence=0.9,
                zone=zone,
            ))

        # Diameter
        for match in DIMENSION_PATTERNS["diameter"].finditer(text):
            value = float(match.group(1))
            dimensions.append(ExtractedDimension(
                value=value,
                unit=self.default_unit,
                dim_type=DimensionType.DIAMETER,
                raw_text=match.group(0),
                confidence=0.9,
                zone=zone,
            ))

        # Radius
        for match in DIMENSION_PATTERNS["radius"].finditer(text):
            value = float(match.group(1))
            dimensions.append(ExtractedDimension(
                value=value,
                unit=self.default_unit,
                dim_type=DimensionType.RADIAL,
                raw_text=match.group(0),
                confidence=0.9,
                zone=zone,
            ))

        # Angular
        for match in DIMENSION_PATTERNS["angular"].finditer(text):
            degrees = float(match.group(1))
            minutes = int(match.group(2)) if match.group(2) else 0
            value = degrees + minutes / 60

            dimensions.append(ExtractedDimension(
                value=value,
                unit=Unit.DEGREE,
                dim_type=DimensionType.ANGULAR,
                raw_text=match.group(0),
                confidence=0.85,
                zone=zone,
            ))

        # Decimal with tolerance
        for match in DIMENSION_PATTERNS["decimal_tolerance"].finditer(text):
            value = float(match.group(1))
            if match.group(2):
                # Bilateral: ±.005
                tol = float(match.group(2))
                tolerance = Tolerance(upper=tol, lower=-tol, bilateral=True)
            else:
                # Asymmetric: +.010/-.005
                upper = float(match.group(3))
                lower = -float(match.group(4))
                tolerance = Tolerance(upper=upper, lower=lower, bilateral=False)

            dimensions.append(ExtractedDimension(
                value=value,
                unit=self.default_unit,
                dim_type=DimensionType.LINEAR,
                tolerance=tolerance,
                raw_text=match.group(0),
                confidence=0.95,
                zone=zone,
            ))

        # Reference dimensions
        for match in DIMENSION_PATTERNS["reference"].finditer(text):
            value = float(match.group(1))
            dimensions.append(ExtractedDimension(
                value=value,
                unit=self.default_unit,
                dim_type=DimensionType.REFERENCE,
                raw_text=match.group(0),
                confidence=0.85,
                zone=zone,
                is_reference=True,
            ))

        # Basic dimensions
        for match in DIMENSION_PATTERNS["basic"].finditer(text):
            value = float(match.group(1))
            dimensions.append(ExtractedDimension(
                value=value,
                unit=self.default_unit,
                dim_type=DimensionType.BASIC,
                raw_text=match.group(0),
                confidence=0.85,
                zone=zone,
            ))

        # Metric
        for match in DIMENSION_PATTERNS["metric"].finditer(text):
            value = float(match.group(1))
            dimensions.append(ExtractedDimension(
                value=value,
                unit=Unit.MILLIMETER,
                dim_type=DimensionType.LINEAR,
                raw_text=match.group(0),
                confidence=0.9,
                zone=zone,
            ))

        # Fractions (if not already captured as feet-inches)
        for match in DIMENSION_PATTERNS["fraction"].finditer(text):
            whole = int(match.group(1)) if match.group(1) else 0
            num = int(match.group(2))
            den = int(match.group(3))

            if den == 0:
                continue

            value = whole + num / den

            # Skip if this matches a feet-inches pattern
            raw = match.group(0)
            if any(raw in d.raw_text for d in dimensions):
                continue

            dimensions.append(ExtractedDimension(
                value=value,
                unit=self.default_unit,
                dim_type=DimensionType.LINEAR,
                raw_text=raw,
                confidence=0.8,
                zone=zone,
            ))

        # Plain decimals (lowest priority - many false positives)
        for match in DIMENSION_PATTERNS["decimal"].finditer(text):
            value = float(match.group(1))

            # Skip if already captured
            raw = match.group(0)
            if any(raw in d.raw_text for d in dimensions):
                continue

            # Skip very small values (likely tolerances or revisions)
            if value < 0.01:
                continue

            dimensions.append(ExtractedDimension(
                value=value,
                unit=self.default_unit,
                dim_type=DimensionType.LINEAR,
                raw_text=raw,
                confidence=0.7,
                zone=zone,
            ))

        return dimensions

    # -------------------------------------------------------------------------
    # TITLE BLOCK EXTRACTION
    # -------------------------------------------------------------------------

    def _extract_title_block(self, text: str) -> TitleBlockData:
        """Extract title block information."""
        data = TitleBlockData()

        for field_name, pattern in TITLE_BLOCK_PATTERNS.items():
            match = pattern.search(text)
            if match:
                if field_name == "weight":
                    try:
                        data.weight = float(match.group(1))
                    except ValueError:
                        pass
                elif field_name == "sheet" and match.group(2):
                    data.sheet = f"{match.group(1)} of {match.group(2)}"
                elif hasattr(data, field_name):
                    setattr(data, field_name, match.group(1).strip())

        return data

    # -------------------------------------------------------------------------
    # NOTES EXTRACTION
    # -------------------------------------------------------------------------

    def _extract_notes(self, text: str) -> list[str]:
        """Extract numbered notes from text."""
        notes = []

        # Pattern for numbered notes: 1. Note text, 1) Note text, NOTE 1: text
        note_pattern = re.compile(
            r'(?:(?:NOTE\s*)?(\d+)[.\):\s]+(.+?)(?=(?:\d+[.\)])|$))',
            re.IGNORECASE | re.DOTALL
        )

        for match in note_pattern.finditer(text):
            note_num = match.group(1)
            note_text = match.group(2).strip()

            if note_text and len(note_text) > 5:
                notes.append(f"{note_num}. {note_text}")

        return notes

    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------

    def _dims_match(self, dim1: ExtractedDimension, dim2: ExtractedDimension) -> bool:
        """Check if two dimensions are essentially the same."""
        return (
            abs(dim1.value - dim2.value) < 0.001 and
            dim1.unit == dim2.unit and
            dim1.dim_type == dim2.dim_type
        )

    def _calculate_confidence(
        self,
        dimensions: list[ExtractedDimension],
        title_block: Optional[TitleBlockData],
    ) -> float:
        """Calculate overall extraction confidence."""
        scores = []

        # Dimension confidence
        if dimensions:
            dim_conf = sum(d.confidence for d in dimensions) / len(dimensions)
            scores.append(dim_conf * 0.5)

        # Title block completeness
        if title_block:
            tb_fields = [
                title_block.part_number,
                title_block.material,
                title_block.revision,
            ]
            tb_score = sum(1 for f in tb_fields if f) / len(tb_fields)
            scores.append(tb_score * 0.5)

        return sum(scores) if scores else 0.0

    # -------------------------------------------------------------------------
    # CONVENIENCE METHODS
    # -------------------------------------------------------------------------

    def quick_extract(self, text: str) -> list[ExtractedDimension]:
        """
        Quick extraction from raw text without zone processing.

        Args:
            text: Raw OCR text

        Returns:
            List of extracted dimensions
        """
        return self._extract_dimensions(text, zone="quick")

    def parse_dimension_string(self, dim_str: str) -> Optional[ExtractedDimension]:
        """
        Parse a single dimension string.

        Args:
            dim_str: Dimension string like "1'-6 3/8\"" or "25.4mm"

        Returns:
            ExtractedDimension or None
        """
        dims = self._extract_dimensions(dim_str)
        return dims[0] if dims else None

    def convert_to_inches(self, dim: ExtractedDimension) -> float:
        """Convert a dimension to inches."""
        if dim.unit == Unit.INCH:
            return dim.value
        elif dim.unit == Unit.FEET_INCHES:
            return dim.value  # Already stored as total inches
        elif dim.unit == Unit.FEET:
            return dim.value * 12
        elif dim.unit == Unit.MILLIMETER:
            return dim.value / 25.4
        elif dim.unit == Unit.CENTIMETER:
            return dim.value / 2.54
        elif dim.unit == Unit.METER:
            return dim.value / 0.0254
        return dim.value


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "DimensionExtractor",
    "ExtractedDimension",
    "ExtractionResult",
    "TitleBlockData",
    "Tolerance",
    "DimensionType",
    "Unit",
]
