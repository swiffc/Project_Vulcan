"""
Weight Calculator Adapter
=========================
Automatic weight calculation from dimensions and material for engineering drawings.
Validates stated weights against calculated values with tolerance checking.

Uses: standards_db.py for material densities and standard shapes

References:
- AISC Steel Manual for W-shapes, angles
- VERIFICATION_REQUIREMENTS.md Section 1.2

Usage:
    from agents.cad_agent.adapters.weight_calculator import WeightCalculator

    calc = WeightCalculator()
    result = calc.calculate_part_weight(part_data)
    validation = calc.validate_stated_weight(stated=150, calculated=145.5)
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from .standards_db import (
    W_SHAPES,
    ANGLES,
    SHEET_GAUGES,
    PLATE_THICKNESSES,
    DENSITIES,
    get_beam_properties,
    get_angle_properties,
    get_gauge_thickness,
    get_plate_thickness,
    get_density,
    calculate_beam_weight,
    calculate_plate_weight,
    calculate_angle_weight,
)

logger = logging.getLogger("cad_agent.weight-calculator")


# =============================================================================
# ENUMS & DATA MODELS
# =============================================================================

class PartType(Enum):
    """Type of part for weight calculation."""
    PLATE = "plate"
    SHEET = "sheet"
    BEAM = "beam"
    ANGLE = "angle"
    TUBE = "tube"
    PIPE = "pipe"
    BAR = "bar"
    CHANNEL = "channel"
    UNKNOWN = "unknown"


class WeightStatus(Enum):
    """Weight validation status."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    MISSING = "missing"


@dataclass
class PartDimensions:
    """Dimensions needed for weight calculation."""
    length: Optional[float] = None  # inches
    width: Optional[float] = None   # inches
    thickness: Optional[float] = None  # inches
    height: Optional[float] = None  # inches (for beams)
    wall_thickness: Optional[float] = None  # for tubes/pipes
    od: Optional[float] = None  # outer diameter for pipes/tubes
    id: Optional[float] = None  # inner diameter for pipes/tubes
    shape: Optional[str] = None  # W8x31, L3x3x1/4, etc.
    gauge: Optional[str] = None  # 10GA, 12GA, etc.


@dataclass
class WeightResult:
    """Result of weight calculation."""
    calculated_weight: float
    weight_unit: str = "lb"
    part_type: PartType = PartType.UNKNOWN
    method: str = ""
    breakdown: dict = None

    def __post_init__(self):
        if self.breakdown is None:
            self.breakdown = {}


@dataclass
class WeightValidation:
    """Result of weight validation."""
    status: WeightStatus
    stated_weight: float
    calculated_weight: float
    difference: float
    difference_percent: float
    message: str
    tolerance_used: float


# =============================================================================
# WEIGHT CALCULATOR
# =============================================================================

class WeightCalculator:
    """
    Calculate and validate weights for engineering parts.

    Supports:
    - Plates and sheets (flat stock)
    - W-beams and angles
    - Round tubes and pipes
    - Square/rectangular tubes
    - Bars (round, square, flat)
    """

    # Default tolerances by part type
    DEFAULT_TOLERANCES = {
        PartType.PLATE: 0.05,      # 5% for simple parts
        PartType.SHEET: 0.05,
        PartType.BEAM: 0.03,       # 3% for standard shapes
        PartType.ANGLE: 0.03,
        PartType.TUBE: 0.08,       # 8% for tubes (wall variation)
        PartType.PIPE: 0.08,
        PartType.BAR: 0.05,
        PartType.UNKNOWN: 0.10,    # 10% for assemblies
    }

    def __init__(self, default_material: str = "steel"):
        self.default_material = default_material

    # -------------------------------------------------------------------------
    # MAIN CALCULATION METHODS
    # -------------------------------------------------------------------------

    def calculate_part_weight(
        self,
        dims: PartDimensions,
        material: Optional[str] = None,
        part_type: Optional[PartType] = None,
    ) -> WeightResult:
        """
        Calculate weight for a part given its dimensions.

        Args:
            dims: Part dimensions
            material: Material type (default: steel)
            part_type: Type of part (auto-detected if not provided)

        Returns:
            WeightResult with calculated weight and method used
        """
        material = material or self.default_material

        # Auto-detect part type if not provided
        if part_type is None:
            part_type = self._detect_part_type(dims)

        logger.debug(f"Calculating weight for {part_type.value}, material={material}")

        # Route to appropriate calculation method
        if part_type == PartType.BEAM:
            return self._calc_beam_weight(dims)

        if part_type == PartType.ANGLE:
            return self._calc_angle_weight(dims)

        if part_type in (PartType.PLATE, PartType.SHEET):
            return self._calc_plate_weight(dims, material)

        if part_type in (PartType.TUBE, PartType.PIPE):
            return self._calc_tube_weight(dims, material)

        if part_type == PartType.BAR:
            return self._calc_bar_weight(dims, material)

        # Fallback to volume-based calculation
        return self._calc_generic_weight(dims, material)

    def validate_stated_weight(
        self,
        stated: float,
        calculated: float,
        part_type: PartType = PartType.UNKNOWN,
        tolerance: Optional[float] = None,
    ) -> WeightValidation:
        """
        Validate a stated weight against calculated weight.

        Args:
            stated: Weight shown on drawing
            calculated: Calculated weight
            part_type: Type of part (for tolerance selection)
            tolerance: Override tolerance (default: based on part type)

        Returns:
            WeightValidation with status and details
        """
        if tolerance is None:
            tolerance = self.DEFAULT_TOLERANCES.get(part_type, 0.10)

        if stated == 0 or stated is None:
            return WeightValidation(
                status=WeightStatus.MISSING,
                stated_weight=0,
                calculated_weight=calculated,
                difference=calculated,
                difference_percent=100.0,
                message="No weight specified on drawing",
                tolerance_used=tolerance,
            )

        difference = abs(stated - calculated)
        diff_percent = (difference / stated) * 100

        if diff_percent <= tolerance * 100:
            status = WeightStatus.OK
            message = f"Weight OK: {stated:.1f} lb (calc {calculated:.1f} lb, diff {diff_percent:.1f}%)"
        elif diff_percent <= (tolerance * 2) * 100:
            status = WeightStatus.WARNING
            message = f"Weight warning: {stated:.1f} lb vs calc {calculated:.1f} lb ({diff_percent:.1f}% diff)"
        else:
            status = WeightStatus.ERROR
            message = f"Weight mismatch: {stated:.1f} lb vs calc {calculated:.1f} lb ({diff_percent:.1f}% diff)"

        return WeightValidation(
            status=status,
            stated_weight=stated,
            calculated_weight=calculated,
            difference=difference,
            difference_percent=diff_percent,
            message=message,
            tolerance_used=tolerance,
        )

    # -------------------------------------------------------------------------
    # SPECIFIC CALCULATION METHODS
    # -------------------------------------------------------------------------

    def _calc_beam_weight(self, dims: PartDimensions) -> WeightResult:
        """Calculate weight for W-beam or similar structural shape."""
        if not dims.shape:
            return WeightResult(
                calculated_weight=0,
                part_type=PartType.BEAM,
                method="beam_lookup",
                breakdown={"error": "No shape specified"},
            )

        # Get beam properties from AISC data
        props = get_beam_properties(dims.shape)
        if not props:
            return WeightResult(
                calculated_weight=0,
                part_type=PartType.BEAM,
                method="beam_lookup",
                breakdown={"error": f"Shape {dims.shape} not found in database"},
            )

        # Calculate length in feet
        length_ft = (dims.length or 0) / 12.0

        weight = calculate_beam_weight(dims.shape, length_ft) or 0

        return WeightResult(
            calculated_weight=weight,
            part_type=PartType.BEAM,
            method="beam_lookup",
            breakdown={
                "shape": dims.shape,
                "weight_per_ft": props["wt"],
                "length_ft": length_ft,
                "formula": f"{length_ft:.2f} ft × {props['wt']} lb/ft",
            },
        )

    def _calc_angle_weight(self, dims: PartDimensions) -> WeightResult:
        """Calculate weight for angle iron."""
        if not dims.shape:
            return WeightResult(
                calculated_weight=0,
                part_type=PartType.ANGLE,
                method="angle_lookup",
                breakdown={"error": "No shape specified"},
            )

        props = get_angle_properties(dims.shape)
        if not props:
            return WeightResult(
                calculated_weight=0,
                part_type=PartType.ANGLE,
                method="angle_lookup",
                breakdown={"error": f"Shape {dims.shape} not found in database"},
            )

        length_ft = (dims.length or 0) / 12.0
        weight = calculate_angle_weight(dims.shape, length_ft) or 0

        return WeightResult(
            calculated_weight=weight,
            part_type=PartType.ANGLE,
            method="angle_lookup",
            breakdown={
                "shape": dims.shape,
                "weight_per_ft": props["wt"],
                "length_ft": length_ft,
                "formula": f"{length_ft:.2f} ft × {props['wt']} lb/ft",
            },
        )

    def _calc_plate_weight(self, dims: PartDimensions, material: str) -> WeightResult:
        """Calculate weight for flat plate or sheet metal."""
        # Determine thickness
        thickness = dims.thickness

        # Try gauge if thickness not provided
        if thickness is None and dims.gauge:
            thickness = get_gauge_thickness(dims.gauge)

        if thickness is None:
            return WeightResult(
                calculated_weight=0,
                part_type=PartType.PLATE,
                method="plate_volume",
                breakdown={"error": "No thickness specified"},
            )

        length = dims.length or 0
        width = dims.width or 0

        weight = calculate_plate_weight(length, width, thickness, material)

        return WeightResult(
            calculated_weight=weight,
            part_type=PartType.PLATE,
            method="plate_volume",
            breakdown={
                "length_in": length,
                "width_in": width,
                "thickness_in": thickness,
                "material": material,
                "density": get_density(material),
                "formula": f"{length} × {width} × {thickness} × {get_density(material):.3f}",
            },
        )

    def _calc_tube_weight(self, dims: PartDimensions, material: str) -> WeightResult:
        """Calculate weight for round tube or pipe."""
        import math

        if dims.od is None:
            return WeightResult(
                calculated_weight=0,
                part_type=PartType.TUBE,
                method="tube_annulus",
                breakdown={"error": "No OD specified"},
            )

        od = dims.od
        wall = dims.wall_thickness or 0
        id_val = dims.id or (od - 2 * wall)
        length = dims.length or 0

        # Calculate annular area
        outer_area = math.pi * (od / 2) ** 2
        inner_area = math.pi * (id_val / 2) ** 2
        cross_section = outer_area - inner_area

        # Volume in cubic inches
        volume = cross_section * length

        # Weight
        density = get_density(material)
        weight = volume * density

        return WeightResult(
            calculated_weight=weight,
            part_type=PartType.TUBE,
            method="tube_annulus",
            breakdown={
                "od": od,
                "id": id_val,
                "wall": wall,
                "length": length,
                "cross_section": cross_section,
                "volume": volume,
                "density": density,
            },
        )

    def _calc_bar_weight(self, dims: PartDimensions, material: str) -> WeightResult:
        """Calculate weight for bar stock (round, square, flat)."""
        import math

        length = dims.length or 0
        density = get_density(material)

        # Round bar (diameter = width)
        if dims.width and not dims.thickness:
            diameter = dims.width
            area = math.pi * (diameter / 2) ** 2
            volume = area * length
        # Square bar
        elif dims.width and dims.width == dims.thickness:
            area = dims.width ** 2
            volume = area * length
        # Flat bar
        elif dims.width and dims.thickness:
            area = dims.width * dims.thickness
            volume = area * length
        else:
            return WeightResult(
                calculated_weight=0,
                part_type=PartType.BAR,
                method="bar_volume",
                breakdown={"error": "Insufficient dimensions"},
            )

        weight = volume * density

        return WeightResult(
            calculated_weight=weight,
            part_type=PartType.BAR,
            method="bar_volume",
            breakdown={
                "length": length,
                "cross_section_area": area,
                "volume": volume,
                "density": density,
            },
        )

    def _calc_generic_weight(self, dims: PartDimensions, material: str) -> WeightResult:
        """Fallback generic volume-based calculation."""
        length = dims.length or 0
        width = dims.width or 0
        thickness = dims.thickness or 0

        if dims.gauge:
            thickness = get_gauge_thickness(dims.gauge) or thickness

        volume = length * width * thickness
        density = get_density(material)
        weight = volume * density

        return WeightResult(
            calculated_weight=weight,
            part_type=PartType.UNKNOWN,
            method="generic_volume",
            breakdown={
                "length": length,
                "width": width,
                "thickness": thickness,
                "volume": volume,
                "density": density,
            },
        )

    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------

    def _detect_part_type(self, dims: PartDimensions) -> PartType:
        """Auto-detect part type from dimensions and shape."""
        if dims.shape:
            shape_upper = dims.shape.upper()

            if shape_upper.startswith("W"):
                return PartType.BEAM

            if shape_upper.startswith("L"):
                return PartType.ANGLE

            if "C" in shape_upper or "MC" in shape_upper:
                return PartType.CHANNEL

            if "TUBE" in shape_upper or "HSS" in shape_upper:
                return PartType.TUBE

            if "PIPE" in shape_upper:
                return PartType.PIPE

        if dims.od or dims.id:
            return PartType.TUBE if dims.wall_thickness else PartType.PIPE

        if dims.gauge:
            return PartType.SHEET

        if dims.length and dims.width and dims.thickness:
            # Distinguish plate from bar
            if dims.thickness <= 0.5 and dims.width > dims.thickness * 2:
                return PartType.PLATE
            if dims.width == dims.thickness:
                return PartType.BAR

            return PartType.PLATE

        return PartType.UNKNOWN

    def parse_description(self, description: str) -> tuple[PartDimensions, Optional[str]]:
        """
        Parse a material description into dimensions.

        Examples:
            "PLATE_1/4_A36" -> (PartDimensions(thickness=0.25), "A36")
            "W8X31" -> (PartDimensions(shape="W8x31"), None)
            "L3X3X1/4" -> (PartDimensions(shape="L3x3x1/4"), None)
            "10GA_A36" -> (PartDimensions(gauge="10GA"), "A36")
        """
        dims = PartDimensions()
        material = None

        desc_upper = description.upper().strip()

        # W-beam pattern
        beam_match = re.match(r'W(\d+)[X×](\d+)', desc_upper)
        if beam_match:
            dims.shape = f"W{beam_match.group(1)}x{beam_match.group(2)}"
            return dims, None

        # Angle pattern
        angle_match = re.match(r'L(\d+(?:-\d+/\d+)?)[X×](\d+(?:-\d+/\d+)?)[X×](\d+/\d+|\d+)', desc_upper)
        if angle_match:
            dims.shape = f"L{angle_match.group(1)}x{angle_match.group(2)}x{angle_match.group(3)}"
            return dims, None

        # Gauge pattern
        gauge_match = re.search(r'(\d+GA)', desc_upper)
        if gauge_match:
            dims.gauge = gauge_match.group(1)

        # Plate thickness pattern
        plate_match = re.search(r'PLATE[_\s]*(\d+/\d+|\d+\.?\d*)', desc_upper)
        if plate_match:
            thickness_str = plate_match.group(1)
            dims.thickness = self._parse_fraction(thickness_str)

        # Material extraction
        for mat in ["A36", "A572", "A514", "SS304", "SS316", "AL6061", "AL5052"]:
            if mat in desc_upper:
                material = mat
                break

        return dims, material

    def _parse_fraction(self, frac_str: str) -> float:
        """Parse a fraction string like '1/4' or '1-1/2' to float."""
        if "/" not in frac_str:
            try:
                return float(frac_str)
            except ValueError:
                return 0.0

        if "-" in frac_str:
            # Mixed number: 1-1/2
            parts = frac_str.split("-")
            whole = int(parts[0])
            frac_parts = parts[1].split("/")
            return whole + int(frac_parts[0]) / int(frac_parts[1])
        else:
            # Simple fraction: 1/4
            parts = frac_str.split("/")
            return int(parts[0]) / int(parts[1])


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "WeightCalculator",
    "WeightResult",
    "WeightValidation",
    "WeightStatus",
    "PartType",
    "PartDimensions",
]
