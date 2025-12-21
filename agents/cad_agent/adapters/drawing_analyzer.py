"""
Drawing Analyzer Adapter
========================
AI-powered engineering drawing analysis for ACHE/Fin Fan verification.
Handles PDF/DXF extraction, parallel processing, and intelligent caching.

Uses:
- pdf2image: PDF to image conversion
- pytesseract: OCR engine
- Pillow: Image processing
- ezdxf: DXF file parsing (optional)
- concurrent.futures: Parallel processing

References:
- ACHE_CHECKLIST.md: Complete verification requirements
- VERIFICATION_REQUIREMENTS.md: Speed optimization strategies
- standards_db.py: Pre-loaded engineering standards

Usage:
    from agents.cad_agent.adapters.drawing_analyzer import DrawingAnalyzer

    analyzer = DrawingAnalyzer()
    results = analyzer.analyze_drawing_package("drawings.pdf")
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger("cad_agent.drawing-analyzer")


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class TitleBlock:
    """Extracted title block data."""
    part_number: str = ""
    description: str = ""
    revision: str = ""
    material: str = ""
    weight: Optional[float] = None
    weight_unit: str = "lb"
    finish: str = ""
    drawn_by: str = ""
    checked_by: str = ""
    date: str = ""
    scale: str = ""


@dataclass
class Dimension:
    """Extracted dimension with units and tolerance."""
    value: float
    unit: str = "in"
    tolerance_plus: Optional[float] = None
    tolerance_minus: Optional[float] = None
    is_reference: bool = False

    @property
    def tolerance(self) -> Optional[float]:
        if self.tolerance_plus and self.tolerance_minus:
            return max(abs(self.tolerance_plus), abs(self.tolerance_minus))
        return self.tolerance_plus or self.tolerance_minus


@dataclass
class HoleData:
    """Extracted hole information."""
    diameter: float
    x: Optional[float] = None
    y: Optional[float] = None
    quantity: int = 1
    hole_type: str = "standard"  # standard, oversize, slot, tap
    depth: Optional[float] = None


@dataclass
class BendData:
    """Extracted bend information."""
    angle: float
    radius: float
    k_factor: Optional[float] = None
    bend_line_location: Optional[float] = None


@dataclass
class RedFlag:
    """Issue identified during analysis."""
    severity: str  # critical, warning, info
    category: str  # edge_dist, bend_radius, weight, hole, material, etc.
    message: str
    location: str = ""
    standard_ref: str = ""
    suggested_fix: str = ""


@dataclass
class PageAnalysis:
    """Analysis results for a single page/drawing."""
    page_number: int
    title_block: TitleBlock
    dimensions: list[Dimension] = field(default_factory=list)
    holes: list[HoleData] = field(default_factory=list)
    bends: list[BendData] = field(default_factory=list)
    red_flags: list[RedFlag] = field(default_factory=list)
    raw_text: str = ""
    processing_time_ms: float = 0.0
    confidence_score: float = 0.0


@dataclass
class DrawingPackageAnalysis:
    """Complete analysis of a drawing package."""
    file_path: str
    total_pages: int
    pages: list[PageAnalysis] = field(default_factory=list)
    total_red_flags: int = 0
    critical_flags: int = 0
    processing_time_ms: float = 0.0
    analyzed_at: str = ""


# =============================================================================
# REGEX PATTERNS FOR TITLE BLOCK EXTRACTION
# =============================================================================

TITLE_BLOCK_PATTERNS = {
    "part_number": re.compile(
        r'(?:P/?N|PART\s*(?:NO|NUMBER|#))[:\s]*([A-Z0-9]+-[A-Z0-9]+(?:-[A-Z0-9]+)?)',
        re.IGNORECASE
    ),
    "description": re.compile(
        r'(?:DESC(?:RIPTION)?|TITLE)[:\s]*([A-Z0-9\s\-_]+?)(?:\n|$)',
        re.IGNORECASE
    ),
    "material": re.compile(
        r'(?:MATERIAL|MTL|MATL)[:\s]*([A-Z0-9\s\-_/]+?)(?:\n|$)',
        re.IGNORECASE
    ),
    "weight": re.compile(
        r'(?:WT|WEIGHT)[:\s]*([\d.]+)\s*(LBS?|KG|OZ)?',
        re.IGNORECASE
    ),
    "revision": re.compile(
        r'(?:REV(?:ISION)?)[:\s]*([A-Z0-9]+)',
        re.IGNORECASE
    ),
    "finish": re.compile(
        r'(?:FINISH|COATING)[:\s]*(GALV(?:ANIZED)?|HDG|PAINTED|BARE|MECH\s*GALV)',
        re.IGNORECASE
    ),
    "scale": re.compile(
        r'(?:SCALE)[:\s]*([\d]+\s*[:/]\s*[\d]+|FULL|NTS)',
        re.IGNORECASE
    ),
}

DIMENSION_PATTERNS = {
    # Fractional inches: 1-1/4", 3/8", etc.
    "fraction": re.compile(r'(\d+)?-?(\d+)/(\d+)"?'),
    # Decimal inches: 1.250", 0.375
    "decimal": re.compile(r'(\d+\.?\d*)"?(?:\s*[±]?\s*([\d.]+))?'),
    # Feet and inches: 6'-8 3/16"
    "feet_inches": re.compile(r"(\d+)['′]-(\d+)\s*(?:(\d+)/(\d+))?[\"″]?"),
    # Metric: 25.4mm
    "metric": re.compile(r'(\d+\.?\d*)\s*mm'),
}

HOLE_PATTERNS = {
    # Diameter symbols
    "diameter": re.compile(r'[ØΦ∅]\s*([\d.]+)(?:\s*(?:THRU|X\s*DP|DEEP))?', re.IGNORECASE),
    # Hole callout
    "callout": re.compile(r'(\d+)X?\s*[ØΦ∅]?\s*([\d./]+)\s*(?:HOLES?)?', re.IGNORECASE),
    # Tap holes
    "tap": re.compile(r'(\d+)/(\d+)-(\d+)\s*(?:UNC|UNF|TAP)', re.IGNORECASE),
}


# =============================================================================
# DRAWING ANALYZER
# =============================================================================

class DrawingAnalyzer:
    """
    AI-powered engineering drawing analyzer.

    Features:
    - PDF and DXF file support
    - Parallel page processing
    - Intelligent title block OCR
    - Red flag pre-scanning
    - Verification caching
    """

    def __init__(
        self,
        dpi: int = 300,
        max_workers: int = 8,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
    ):
        self.dpi = dpi
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache/drawings")

        if self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_cache()
        else:
            self._cache: dict = {}

    def _load_cache(self) -> None:
        """Load verification cache from disk."""
        cache_file = self.cache_dir / "verified_cache.json"
        try:
            with open(cache_file) as f:
                self._cache = json.load(f)
        except FileNotFoundError:
            self._cache = {}

    def _save_cache(self) -> None:
        """Save verification cache to disk."""
        if not self.use_cache:
            return
        cache_file = self.cache_dir / "verified_cache.json"
        with open(cache_file, "w") as f:
            json.dump(self._cache, f, indent=2)

    def _get_cached(self, key: str) -> Optional[dict]:
        """Get cached verification result."""
        return self._cache.get(key)

    def _set_cached(self, key: str, data: dict) -> None:
        """Cache a verification result."""
        self._cache[key] = {
            **data,
            "cached_at": datetime.now().isoformat(),
        }
        self._save_cache()

    # -------------------------------------------------------------------------
    # PDF PROCESSING
    # -------------------------------------------------------------------------

    def analyze_drawing_package(
        self,
        pdf_path: str,
        parallel: bool = True,
    ) -> DrawingPackageAnalysis:
        """
        Analyze an entire drawing package (multi-page PDF).

        Args:
            pdf_path: Path to PDF file
            parallel: Use parallel processing (default True)

        Returns:
            Complete analysis with all pages
        """
        import time
        start_time = time.perf_counter()

        logger.info(f"Analyzing drawing package: {pdf_path}")

        # Convert PDF to images
        images = self._pdf_to_images(pdf_path)
        total_pages = len(images)
        logger.info(f"  {total_pages} pages to process")

        # Process pages
        if parallel and total_pages > 1:
            page_results = self._process_pages_parallel(images)
        else:
            page_results = self._process_pages_sequential(images)

        # Aggregate results
        total_flags = sum(len(p.red_flags) for p in page_results)
        critical_flags = sum(
            len([f for f in p.red_flags if f.severity == "critical"])
            for p in page_results
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        result = DrawingPackageAnalysis(
            file_path=pdf_path,
            total_pages=total_pages,
            pages=page_results,
            total_red_flags=total_flags,
            critical_flags=critical_flags,
            processing_time_ms=elapsed_ms,
            analyzed_at=datetime.now().isoformat(),
        )

        logger.info(f"  Analysis complete: {total_flags} flags ({critical_flags} critical)")
        logger.info(f"  Processing time: {elapsed_ms:.0f}ms")

        # Cleanup temp images
        self._cleanup_temp_images(images)

        return result

    def _pdf_to_images(self, pdf_path: str) -> list:
        """Convert PDF to list of PIL images."""
        from pdf2image import convert_from_path

        logger.debug(f"Converting PDF to images at {self.dpi} DPI")
        return convert_from_path(pdf_path, dpi=self.dpi)

    def _process_pages_parallel(self, images: list) -> list[PageAnalysis]:
        """Process pages in parallel using thread pool."""
        results: list[Optional[PageAnalysis]] = [None] * len(images)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._analyze_page, i, img): i
                for i, img in enumerate(images)
            }

            for future in as_completed(futures):
                page_idx = futures[future]
                try:
                    results[page_idx] = future.result()
                except Exception as e:
                    logger.error(f"Page {page_idx + 1} failed: {e}")
                    results[page_idx] = PageAnalysis(
                        page_number=page_idx + 1,
                        title_block=TitleBlock(),
                        red_flags=[RedFlag(
                            severity="critical",
                            category="processing",
                            message=f"Page analysis failed: {str(e)}",
                        )],
                    )

        return [r for r in results if r is not None]

    def _process_pages_sequential(self, images: list) -> list[PageAnalysis]:
        """Process pages sequentially."""
        return [self._analyze_page(i, img) for i, img in enumerate(images)]

    def _cleanup_temp_images(self, images: list) -> None:
        """Clean up temporary image files."""
        # pdf2image returns PIL images, not file paths
        # Just clear references to allow garbage collection
        images.clear()

    # -------------------------------------------------------------------------
    # PAGE ANALYSIS
    # -------------------------------------------------------------------------

    def _analyze_page(self, page_idx: int, image) -> PageAnalysis:
        """Analyze a single page/drawing."""
        import time
        import pytesseract

        start_time = time.perf_counter()
        page_num = page_idx + 1

        logger.debug(f"Analyzing page {page_num}")

        # OCR the image
        raw_text = pytesseract.image_to_string(image)

        # Extract title block
        title_block = self._extract_title_block(raw_text)

        # Check cache for this part
        cache_key = f"{title_block.part_number}_{title_block.revision}"
        cached = self._get_cached(cache_key)
        if cached and title_block.part_number:
            logger.debug(f"  Using cached result for {cache_key}")
            return PageAnalysis(
                page_number=page_num,
                title_block=title_block,
                raw_text=raw_text,
                confidence_score=cached.get("confidence_score", 0.9),
                processing_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Extract dimensions
        dimensions = self._extract_dimensions(raw_text)

        # Extract holes
        holes = self._extract_holes(raw_text)

        # Extract bends
        bends = self._extract_bends(raw_text)

        # Run red flag scan
        red_flags = self._scan_for_red_flags(title_block, dimensions, holes, bends)

        # Calculate confidence
        confidence = self._calculate_confidence(title_block, dimensions)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        result = PageAnalysis(
            page_number=page_num,
            title_block=title_block,
            dimensions=dimensions,
            holes=holes,
            bends=bends,
            red_flags=red_flags,
            raw_text=raw_text,
            processing_time_ms=elapsed_ms,
            confidence_score=confidence,
        )

        # Cache result
        if title_block.part_number and confidence > 0.7:
            self._set_cached(cache_key, asdict(result))

        return result

    # -------------------------------------------------------------------------
    # EXTRACTION METHODS
    # -------------------------------------------------------------------------

    def _extract_title_block(self, text: str) -> TitleBlock:
        """Extract title block information from OCR text."""
        title_block = TitleBlock()

        # Part number
        match = TITLE_BLOCK_PATTERNS["part_number"].search(text)
        if match:
            title_block.part_number = match.group(1).strip()

        # Description
        match = TITLE_BLOCK_PATTERNS["description"].search(text)
        if match:
            title_block.description = match.group(1).strip()

        # Material
        match = TITLE_BLOCK_PATTERNS["material"].search(text)
        if match:
            title_block.material = match.group(1).strip()

        # Weight
        match = TITLE_BLOCK_PATTERNS["weight"].search(text)
        if match:
            try:
                title_block.weight = float(match.group(1))
                if match.group(2):
                    title_block.weight_unit = match.group(2).upper()
            except ValueError:
                pass

        # Revision
        match = TITLE_BLOCK_PATTERNS["revision"].search(text)
        if match:
            title_block.revision = match.group(1).strip()

        # Finish
        match = TITLE_BLOCK_PATTERNS["finish"].search(text)
        if match:
            title_block.finish = match.group(1).upper()

        # Scale
        match = TITLE_BLOCK_PATTERNS["scale"].search(text)
        if match:
            title_block.scale = match.group(1).strip()

        return title_block

    def _extract_dimensions(self, text: str) -> list[Dimension]:
        """Extract dimensions from OCR text."""
        dimensions = []

        # Feet and inches (e.g., 6'-8 3/16")
        for match in DIMENSION_PATTERNS["feet_inches"].finditer(text):
            feet = int(match.group(1))
            inches = int(match.group(2))
            frac_num = int(match.group(3)) if match.group(3) else 0
            frac_den = int(match.group(4)) if match.group(4) else 1
            total_inches = (feet * 12) + inches + (frac_num / frac_den if frac_den else 0)
            dimensions.append(Dimension(value=total_inches, unit="in"))

        # Fractional inches (e.g., 1-1/4")
        for match in DIMENSION_PATTERNS["fraction"].finditer(text):
            whole = int(match.group(1)) if match.group(1) else 0
            num = int(match.group(2))
            den = int(match.group(3))
            value = whole + (num / den if den else 0)
            dimensions.append(Dimension(value=value, unit="in"))

        # Decimal inches
        for match in DIMENSION_PATTERNS["decimal"].finditer(text):
            try:
                value = float(match.group(1))
                tolerance = float(match.group(2)) if match.group(2) else None
                dimensions.append(Dimension(
                    value=value,
                    unit="in",
                    tolerance_plus=tolerance,
                    tolerance_minus=-tolerance if tolerance else None,
                ))
            except ValueError:
                continue

        # Metric
        for match in DIMENSION_PATTERNS["metric"].finditer(text):
            try:
                value = float(match.group(1))
                dimensions.append(Dimension(value=value, unit="mm"))
            except ValueError:
                continue

        return dimensions

    def _extract_holes(self, text: str) -> list[HoleData]:
        """Extract hole information from OCR text."""
        holes = []

        # Diameter callouts
        for match in HOLE_PATTERNS["diameter"].finditer(text):
            try:
                diameter = float(match.group(1))
                holes.append(HoleData(diameter=diameter))
            except ValueError:
                continue

        # Quantity x diameter
        for match in HOLE_PATTERNS["callout"].finditer(text):
            try:
                qty = int(match.group(1))
                dia_str = match.group(2)

                # Handle fractions
                if "/" in dia_str:
                    parts = dia_str.split("/")
                    diameter = float(parts[0]) / float(parts[1])
                else:
                    diameter = float(dia_str)

                holes.append(HoleData(diameter=diameter, quantity=qty))
            except ValueError:
                continue

        # Tapped holes
        for match in HOLE_PATTERNS["tap"].finditer(text):
            try:
                major_num = int(match.group(1))
                major_den = int(match.group(2))
                major_dia = major_num / major_den
                holes.append(HoleData(
                    diameter=major_dia,
                    hole_type="tap",
                ))
            except ValueError:
                continue

        return holes

    def _extract_bends(self, text: str) -> list[BendData]:
        """Extract bend information from OCR text."""
        bends = []

        # Bend angle and radius patterns
        bend_pattern = re.compile(
            r'(?:BEND|BND)[:\s]*(\d+)[°]?\s*(?:R|RAD(?:IUS)?)[:\s]*([\d.]+)',
            re.IGNORECASE
        )

        for match in bend_pattern.finditer(text):
            try:
                angle = float(match.group(1))
                radius = float(match.group(2))
                bends.append(BendData(angle=angle, radius=radius))
            except ValueError:
                continue

        return bends

    # -------------------------------------------------------------------------
    # RED FLAG SCANNING
    # -------------------------------------------------------------------------

    def _scan_for_red_flags(
        self,
        title_block: TitleBlock,
        dimensions: list[Dimension],
        holes: list[HoleData],
        bends: list[BendData],
    ) -> list[RedFlag]:
        """Pre-scan for obvious issues."""
        from .standards_db import (
            get_edge_distance,
            validate_hole_size,
            get_bend_factor,
            HOLE_SIZES,
        )

        flags = []

        # Check weight is present
        if title_block.weight is None or title_block.weight == 0:
            flags.append(RedFlag(
                severity="warning",
                category="weight",
                message="No weight specified in title block",
                suggested_fix="Add weight to title block",
            ))

        # Check material is specified
        if not title_block.material:
            flags.append(RedFlag(
                severity="warning",
                category="material",
                message="No material specified in title block",
                suggested_fix="Add material specification",
            ))

        # Check for non-standard hole sizes
        std_holes = set(HOLE_SIZES.get(bs, {}).get("std", 0) for bs in HOLE_SIZES)
        for hole in holes:
            if hole.diameter not in std_holes and hole.hole_type == "standard":
                # Find closest standard
                closest = min(std_holes, key=lambda x: abs(x - hole.diameter)) if std_holes else 0
                flags.append(RedFlag(
                    severity="warning",
                    category="hole",
                    message=f"Non-standard hole diameter: {hole.diameter}\"",
                    suggested_fix=f"Use standard hole {closest}\" if possible",
                    standard_ref="AISC Table J3.3",
                ))

        # Check bend radii
        for bend in bends:
            if bend.radius < 0.125:  # Less than 1/8" is very tight
                flags.append(RedFlag(
                    severity="critical",
                    category="bend_radius",
                    message=f"Very tight bend radius: R{bend.radius}\"",
                    suggested_fix="Increase bend radius to minimum 1T",
                ))

        # Check part number format
        if title_block.part_number and not re.match(r'^[A-Z0-9]+-', title_block.part_number):
            flags.append(RedFlag(
                severity="info",
                category="part_number",
                message=f"Non-standard part number format: {title_block.part_number}",
            ))

        return flags

    def _calculate_confidence(
        self,
        title_block: TitleBlock,
        dimensions: list[Dimension],
    ) -> float:
        """Calculate confidence score for extraction quality."""
        score = 0.0
        max_score = 0.0

        # Part number (25%)
        max_score += 0.25
        if title_block.part_number:
            score += 0.25

        # Material (20%)
        max_score += 0.20
        if title_block.material:
            score += 0.20

        # Weight (15%)
        max_score += 0.15
        if title_block.weight:
            score += 0.15

        # Dimensions found (25%)
        max_score += 0.25
        if len(dimensions) >= 3:
            score += 0.25
        elif len(dimensions) >= 1:
            score += 0.15

        # Revision (10%)
        max_score += 0.10
        if title_block.revision:
            score += 0.10

        # Description (5%)
        max_score += 0.05
        if title_block.description:
            score += 0.05

        return score / max_score if max_score > 0 else 0.0

    # -------------------------------------------------------------------------
    # DXF SUPPORT
    # -------------------------------------------------------------------------

    def analyze_dxf(self, dxf_path: str) -> PageAnalysis:
        """
        Analyze a DXF file for circles, lines, and dimensions.

        Uses ezdxf library for parsing.
        """
        import ezdxf
        import time

        start_time = time.perf_counter()

        logger.info(f"Analyzing DXF: {dxf_path}")

        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        holes = []
        dimensions = []

        # Extract circles (potential holes)
        for circle in msp.query("CIRCLE"):
            radius = circle.dxf.radius
            diameter = radius * 2
            center = circle.dxf.center
            holes.append(HoleData(
                diameter=diameter,
                x=center.x,
                y=center.y,
            ))

        # Extract dimension entities
        for dim in msp.query("DIMENSION"):
            try:
                value = dim.dxf.actual_measurement
                dimensions.append(Dimension(value=value, unit="in"))
            except AttributeError:
                continue

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return PageAnalysis(
            page_number=1,
            title_block=TitleBlock(),
            dimensions=dimensions,
            holes=holes,
            processing_time_ms=elapsed_ms,
            confidence_score=0.8,  # DXF extraction is generally reliable
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "DrawingAnalyzer",
    "DrawingPackageAnalysis",
    "PageAnalysis",
    "TitleBlock",
    "Dimension",
    "HoleData",
    "BendData",
    "RedFlag",
]
