"""
Red Flag Scanner Adapter
========================
Pre-scan engineering drawings for obvious issues before detailed review.
Implements the automated red flag detection from VERIFICATION_REQUIREMENTS.md.

Checks:
- Edge distances < minimum (AISC J3.4)
- Bend radii too tight (< 1T for material)
- Non-standard hole sizes
- Weight mismatches > 10%
- Description vs dimension mismatches
- Missing critical information
- OSHA platform/ladder compliance
- API 661 fan clearances

References:
- VERIFICATION_REQUIREMENTS.md Section 2.5
- ACHE_CHECKLIST.md for ACHE-specific checks

Usage:
    from agents.cad_agent.adapters.red_flag_scanner import RedFlagScanner

    scanner = RedFlagScanner()
    flags = scanner.scan_drawing(drawing_data)
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from .standards_db import (
    get_edge_distance,
    get_bend_factor,
    get_standard_hole,
    get_gauge_thickness,
    get_plate_thickness,
    get_fan_tip_clearance,
    validate_edge_distance,
    validate_bend_radius,
    validate_hole_size,
    validate_weight,
    HOLE_SIZES,
    LADDER_REQUIREMENTS,
    STAIR_REQUIREMENTS,
    PLATFORM_REQUIREMENTS,
)

logger = logging.getLogger("cad_agent.red-flag-scanner")


# =============================================================================
# ENUMS & DATA MODELS
# =============================================================================

class Severity(Enum):
    """Flag severity level."""
    CRITICAL = "critical"  # Must fix before release
    WARNING = "warning"    # Should review
    INFO = "info"          # For awareness


class FlagCategory(Enum):
    """Category of red flag."""
    EDGE_DISTANCE = "edge_distance"
    BEND_RADIUS = "bend_radius"
    HOLE_SIZE = "hole_size"
    WEIGHT = "weight"
    DESCRIPTION = "description"
    MATERIAL = "material"
    DIMENSION = "dimension"
    OSHA = "osha"
    API_661 = "api_661"
    BOM = "bom"
    TITLE_BLOCK = "title_block"
    GENERAL = "general"


@dataclass
class RedFlag:
    """A single red flag issue."""
    severity: Severity
    category: FlagCategory
    message: str
    location: str = ""
    value: Optional[float] = None
    limit: Optional[float] = None
    standard_ref: str = ""
    suggested_fix: str = ""

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "location": self.location,
            "value": self.value,
            "limit": self.limit,
            "standard_ref": self.standard_ref,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class ScanResult:
    """Complete scan result."""
    flags: list[RedFlag] = field(default_factory=list)
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    scan_time_ms: float = 0.0
    part_number: str = ""

    @property
    def has_critical(self) -> bool:
        return self.critical_count > 0

    @property
    def total_flags(self) -> int:
        return len(self.flags)

    def to_dict(self) -> dict:
        return {
            "part_number": self.part_number,
            "total_flags": self.total_flags,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "has_critical": self.has_critical,
            "scan_time_ms": self.scan_time_ms,
            "flags": [f.to_dict() for f in self.flags],
        }


@dataclass
class PartData:
    """Data extracted from a drawing for scanning."""
    part_number: str = ""
    description: str = ""
    material: str = ""
    thickness: Optional[float] = None
    gauge: Optional[str] = None
    weight_stated: Optional[float] = None
    weight_calculated: Optional[float] = None

    # Holes
    holes: list[dict] = field(default_factory=list)
    # hole: {diameter, edge_dist, bolt_size}

    # Bends
    bends: list[dict] = field(default_factory=list)
    # bend: {radius, angle, material_thickness}

    # Dimensions
    dimensions: list[dict] = field(default_factory=list)
    # dim: {value, unit, description}

    # Platform/access (OSHA)
    platforms: list[dict] = field(default_factory=list)
    ladders: list[dict] = field(default_factory=list)
    stairs: list[dict] = field(default_factory=list)

    # Fan data (API 661)
    fan_diameter_ft: Optional[float] = None
    tip_clearance: Optional[float] = None


# =============================================================================
# RED FLAG SCANNER
# =============================================================================

class RedFlagScanner:
    """
    Pre-scan drawings for obvious issues.

    Fast first-pass analysis to identify problems before detailed review.
    """

    def __init__(self):
        self._checks = [
            self._check_title_block,
            self._check_weight,
            self._check_holes,
            self._check_bends,
            self._check_description,
            self._check_osha_platforms,
            self._check_osha_ladders,
            self._check_osha_stairs,
            self._check_api_661_fans,
        ]

    def scan_drawing(self, part: PartData) -> ScanResult:
        """
        Scan a drawing for red flags.

        Args:
            part: Extracted part data

        Returns:
            ScanResult with all flags found
        """
        import time
        start = time.perf_counter()

        flags = []
        for check in self._checks:
            try:
                new_flags = check(part)
                flags.extend(new_flags)
            except Exception as e:
                logger.error(f"Check failed: {check.__name__}: {e}")

        # Count by severity
        critical = sum(1 for f in flags if f.severity == Severity.CRITICAL)
        warning = sum(1 for f in flags if f.severity == Severity.WARNING)
        info = sum(1 for f in flags if f.severity == Severity.INFO)

        elapsed = (time.perf_counter() - start) * 1000

        return ScanResult(
            flags=flags,
            critical_count=critical,
            warning_count=warning,
            info_count=info,
            scan_time_ms=elapsed,
            part_number=part.part_number,
        )

    # -------------------------------------------------------------------------
    # INDIVIDUAL CHECKS
    # -------------------------------------------------------------------------

    def _check_title_block(self, part: PartData) -> list[RedFlag]:
        """Check for missing title block information."""
        flags = []

        if not part.part_number:
            flags.append(RedFlag(
                severity=Severity.CRITICAL,
                category=FlagCategory.TITLE_BLOCK,
                message="Missing part number",
                suggested_fix="Add part number to title block",
            ))

        if not part.material:
            flags.append(RedFlag(
                severity=Severity.WARNING,
                category=FlagCategory.MATERIAL,
                message="No material specified",
                suggested_fix="Add material specification",
            ))

        if part.weight_stated is None or part.weight_stated == 0:
            flags.append(RedFlag(
                severity=Severity.WARNING,
                category=FlagCategory.WEIGHT,
                message="No weight specified in title block",
                suggested_fix="Calculate and add weight",
            ))

        return flags

    def _check_weight(self, part: PartData) -> list[RedFlag]:
        """Check weight accuracy."""
        flags = []

        if part.weight_stated and part.weight_calculated:
            is_valid, msg = validate_weight(
                part.weight_stated,
                part.weight_calculated,
                tolerance=0.10
            )

            if not is_valid:
                diff_pct = abs(part.weight_stated - part.weight_calculated) / part.weight_stated * 100
                flags.append(RedFlag(
                    severity=Severity.CRITICAL if diff_pct > 20 else Severity.WARNING,
                    category=FlagCategory.WEIGHT,
                    message=f"Weight mismatch: stated {part.weight_stated:.1f} lb vs calculated {part.weight_calculated:.1f} lb",
                    value=diff_pct,
                    limit=10.0,
                    suggested_fix=f"Verify weight; calculated value is {part.weight_calculated:.1f} lb",
                ))

        return flags

    def _check_holes(self, part: PartData) -> list[RedFlag]:
        """Check hole sizes and edge distances."""
        flags = []

        # Standard hole diameters
        std_holes = set()
        for bolt_size, data in HOLE_SIZES.items():
            std_holes.add(data["std"])
            std_holes.add(data["over"])

        for i, hole in enumerate(part.holes):
            diameter = hole.get("diameter", 0)
            edge_dist = hole.get("edge_dist")
            bolt_size = hole.get("bolt_size")
            location = hole.get("location", f"Hole {i+1}")

            # Check standard size
            if diameter and diameter not in std_holes:
                flags.append(RedFlag(
                    severity=Severity.WARNING,
                    category=FlagCategory.HOLE_SIZE,
                    message=f"Non-standard hole diameter: Ø{diameter}\"",
                    location=location,
                    value=diameter,
                    standard_ref="AISC Table J3.3",
                    suggested_fix="Use standard hole size for bolt",
                ))

            # Check edge distance
            if edge_dist and bolt_size:
                is_valid, msg = validate_edge_distance(edge_dist, bolt_size, "rolled")
                if not is_valid:
                    min_edge = get_edge_distance(bolt_size, "rolled")
                    flags.append(RedFlag(
                        severity=Severity.CRITICAL,
                        category=FlagCategory.EDGE_DISTANCE,
                        message=f"Edge distance {edge_dist}\" < minimum {min_edge}\" for {bolt_size}\" bolt",
                        location=location,
                        value=edge_dist,
                        limit=min_edge,
                        standard_ref="AISC Table J3.4",
                        suggested_fix=f"Increase edge distance to at least {min_edge}\"",
                    ))

        return flags

    def _check_bends(self, part: PartData) -> list[RedFlag]:
        """Check bend radii against material limits."""
        flags = []

        # Get thickness
        thickness = part.thickness
        if not thickness and part.gauge:
            thickness = get_gauge_thickness(part.gauge)

        if not thickness:
            return flags

        # Get bend factor
        bend_factor = get_bend_factor(part.material or "A36")
        min_radius = thickness * bend_factor

        for i, bend in enumerate(part.bends):
            radius = bend.get("radius", 0)
            location = bend.get("location", f"Bend {i+1}")

            if radius < min_radius:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.BEND_RADIUS,
                    message=f"Bend radius R{radius}\" is too tight (min R{min_radius}\" for {part.material})",
                    location=location,
                    value=radius,
                    limit=min_radius,
                    suggested_fix=f"Increase bend radius to at least R{min_radius}\"",
                ))
            elif radius < min_radius * 1.5:
                flags.append(RedFlag(
                    severity=Severity.WARNING,
                    category=FlagCategory.BEND_RADIUS,
                    message=f"Bend radius R{radius}\" is near minimum (recommended R{min_radius * 1.5:.3f}\")",
                    location=location,
                    value=radius,
                    limit=min_radius * 1.5,
                ))

        return flags

    def _check_description(self, part: PartData) -> list[RedFlag]:
        """Check description matches actual dimensions."""
        flags = []

        if not part.description:
            return flags

        desc_upper = part.description.upper()

        # Check plate thickness
        plate_match = re.search(r'PLATE[_\s]*(\d+/\d+|\d+\.?\d*)', desc_upper)
        if plate_match:
            desc_thickness_str = plate_match.group(1)
            desc_thickness = get_plate_thickness(desc_thickness_str)

            if desc_thickness and part.thickness:
                if abs(desc_thickness - part.thickness) > 0.015:  # > 1/64"
                    flags.append(RedFlag(
                        severity=Severity.CRITICAL,
                        category=FlagCategory.DESCRIPTION,
                        message=f"Description says '{desc_thickness_str}' plate but drawing shows {part.thickness}\"",
                        value=part.thickness,
                        limit=desc_thickness,
                        suggested_fix="Correct description or drawing thickness",
                    ))

        # Check gauge
        gauge_match = re.search(r'(\d+GA)', desc_upper)
        if gauge_match:
            desc_gauge = gauge_match.group(1)
            desc_thickness = get_gauge_thickness(desc_gauge)

            if desc_thickness and part.thickness:
                if abs(desc_thickness - part.thickness) > 0.010:
                    flags.append(RedFlag(
                        severity=Severity.CRITICAL,
                        category=FlagCategory.DESCRIPTION,
                        message=f"Description says {desc_gauge} but actual thickness {part.thickness}\" doesn't match",
                        value=part.thickness,
                        limit=desc_thickness,
                        suggested_fix=f"Verify gauge; {desc_gauge} should be {desc_thickness}\"",
                    ))

        return flags

    def _check_osha_platforms(self, part: PartData) -> list[RedFlag]:
        """Check platform compliance with OSHA 1910.29."""
        flags = []

        for platform in part.platforms:
            width = platform.get("width_in", 0)
            platform_type = platform.get("type", "header_walkway")
            location = platform.get("location", "Platform")

            req = PLATFORM_REQUIREMENTS.get(platform_type)
            if req and width < req.min_width_in:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.OSHA,
                    message=f"Platform width {width}\" < minimum {req.min_width_in}\" for {platform_type}",
                    location=location,
                    value=width,
                    limit=req.min_width_in,
                    standard_ref="OSHA 1910.29",
                    suggested_fix=f"Increase width to at least {req.min_width_in}\"",
                ))

            # Check handrail height
            handrail = platform.get("handrail_height_in")
            if handrail and handrail < 42:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.OSHA,
                    message=f"Handrail height {handrail}\" < minimum 42\"",
                    location=location,
                    value=handrail,
                    limit=42,
                    standard_ref="OSHA 1910.29(f)",
                ))

            # Check toeboard
            toeboard = platform.get("toeboard_height_in")
            if toeboard is not None and toeboard < 4:
                flags.append(RedFlag(
                    severity=Severity.WARNING,
                    category=FlagCategory.OSHA,
                    message=f"Toeboard height {toeboard}\" < minimum 4\"",
                    location=location,
                    value=toeboard,
                    limit=4,
                    standard_ref="OSHA 1910.29(k)",
                ))

        return flags

    def _check_osha_ladders(self, part: PartData) -> list[RedFlag]:
        """Check ladder compliance with OSHA 1910.23."""
        flags = []

        for ladder in part.ladders:
            location = ladder.get("location", "Ladder")

            # Rung spacing
            rung_spacing = ladder.get("rung_spacing_in")
            if rung_spacing and abs(rung_spacing - 12) > 0.5:
                flags.append(RedFlag(
                    severity=Severity.WARNING if abs(rung_spacing - 12) < 1 else Severity.CRITICAL,
                    category=FlagCategory.OSHA,
                    message=f"Rung spacing {rung_spacing}\" differs from standard 12\"",
                    location=location,
                    value=rung_spacing,
                    limit=12,
                    standard_ref="OSHA 1910.23(b)(3)",
                ))

            # Clear width
            clear_width = ladder.get("clear_width_in")
            if clear_width and clear_width < 16:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.OSHA,
                    message=f"Ladder clear width {clear_width}\" < minimum 16\"",
                    location=location,
                    value=clear_width,
                    limit=16,
                    standard_ref="OSHA 1910.23(b)(2)",
                ))

            # Extension above landing
            extension = ladder.get("extension_above_landing_in")
            if extension is not None and extension < 42:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.OSHA,
                    message=f"Ladder extension {extension}\" < minimum 42\" above landing",
                    location=location,
                    value=extension,
                    limit=42,
                    standard_ref="OSHA 1910.23(d)(4)",
                ))

        return flags

    def _check_osha_stairs(self, part: PartData) -> list[RedFlag]:
        """Check stair compliance with OSHA 1910.25."""
        flags = []

        for stair in part.stairs:
            location = stair.get("location", "Stair")

            # Width
            width = stair.get("width_in")
            if width and width < 22:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.OSHA,
                    message=f"Stair width {width}\" < minimum 22\"",
                    location=location,
                    value=width,
                    limit=22,
                    standard_ref="OSHA 1910.25(c)(2)",
                ))

            # Riser height
            riser = stair.get("riser_in")
            if riser:
                if riser < 6:
                    flags.append(RedFlag(
                        severity=Severity.WARNING,
                        category=FlagCategory.OSHA,
                        message=f"Riser height {riser}\" < minimum 6\"",
                        location=location,
                        value=riser,
                        limit=6,
                        standard_ref="OSHA 1910.25(c)(3)",
                    ))
                elif riser > 7.5:
                    flags.append(RedFlag(
                        severity=Severity.CRITICAL,
                        category=FlagCategory.OSHA,
                        message=f"Riser height {riser}\" > maximum 7.5\"",
                        location=location,
                        value=riser,
                        limit=7.5,
                        standard_ref="OSHA 1910.25(c)(3)",
                    ))

            # Tread depth
            tread = stair.get("tread_depth_in")
            if tread and tread < 9.5:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.OSHA,
                    message=f"Tread depth {tread}\" < minimum 9.5\"",
                    location=location,
                    value=tread,
                    limit=9.5,
                    standard_ref="OSHA 1910.25(c)(3)",
                ))

            # Angle
            angle = stair.get("angle_deg")
            if angle:
                if angle < 30:
                    flags.append(RedFlag(
                        severity=Severity.WARNING,
                        category=FlagCategory.OSHA,
                        message=f"Stair angle {angle}° < minimum 30°",
                        location=location,
                        value=angle,
                        limit=30,
                    ))
                elif angle > 50:
                    flags.append(RedFlag(
                        severity=Severity.CRITICAL,
                        category=FlagCategory.OSHA,
                        message=f"Stair angle {angle}° > maximum 50° (use ladder)",
                        location=location,
                        value=angle,
                        limit=50,
                    ))

        return flags

    def _check_api_661_fans(self, part: PartData) -> list[RedFlag]:
        """Check fan tip clearance per API 661."""
        flags = []

        if part.fan_diameter_ft and part.tip_clearance is not None:
            max_clearance = get_fan_tip_clearance(part.fan_diameter_ft)

            if part.tip_clearance > max_clearance:
                flags.append(RedFlag(
                    severity=Severity.CRITICAL,
                    category=FlagCategory.API_661,
                    message=f"Fan tip clearance {part.tip_clearance}\" > maximum {max_clearance}\" for {part.fan_diameter_ft}' fan",
                    value=part.tip_clearance,
                    limit=max_clearance,
                    standard_ref="API 661",
                    suggested_fix=f"Reduce tip clearance to max {max_clearance}\"",
                ))
            elif part.tip_clearance > max_clearance * 0.8:
                flags.append(RedFlag(
                    severity=Severity.WARNING,
                    category=FlagCategory.API_661,
                    message=f"Fan tip clearance {part.tip_clearance}\" approaching limit of {max_clearance}\"",
                    value=part.tip_clearance,
                    limit=max_clearance,
                    standard_ref="API 661",
                ))

        return flags


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def quick_scan(
    part_number: str = "",
    material: str = "",
    weight_stated: Optional[float] = None,
    weight_calculated: Optional[float] = None,
    holes: Optional[list[dict]] = None,
    bends: Optional[list[dict]] = None,
    thickness: Optional[float] = None,
) -> ScanResult:
    """
    Quick scan with minimal data.

    Args:
        part_number: Part number
        material: Material type
        weight_stated: Weight from drawing
        weight_calculated: Calculated weight
        holes: List of hole dicts {diameter, edge_dist, bolt_size}
        bends: List of bend dicts {radius, angle}
        thickness: Material thickness

    Returns:
        ScanResult with flags
    """
    part = PartData(
        part_number=part_number,
        material=material,
        weight_stated=weight_stated,
        weight_calculated=weight_calculated,
        holes=holes or [],
        bends=bends or [],
        thickness=thickness,
    )

    scanner = RedFlagScanner()
    return scanner.scan_drawing(part)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RedFlagScanner",
    "RedFlag",
    "ScanResult",
    "PartData",
    "Severity",
    "FlagCategory",
    "quick_scan",
]
