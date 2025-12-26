"""
Fabrication Feasibility Validator
==================================
Validates design for manufacturability and fabrication constraints.

Phase 25.3 - Fabrication Feasibility
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.fabrication")


class FabricationProcess(str, Enum):
    """Fabrication process types."""
    PLASMA_CUT = "plasma_cut"
    LASER_CUT = "laser_cut"
    WATER_JET = "water_jet"
    OXY_FUEL = "oxy_fuel"
    SHEAR = "shear"
    PUNCH = "punch"
    DRILL = "drill"
    SAW = "saw"
    BRAKE_FORM = "brake_form"
    ROLL_FORM = "roll_form"


# Minimum hole diameter by cutting process (inches)
MIN_HOLE_DIAMETER = {
    FabricationProcess.PLASMA_CUT: 0.5,      # Typically thickness or 1/2" min
    FabricationProcess.LASER_CUT: 0.125,     # Can do very small holes
    FabricationProcess.WATER_JET: 0.125,     # Good for small holes
    FabricationProcess.OXY_FUEL: 0.75,       # Larger holes only
    FabricationProcess.PUNCH: 0.1875,        # 3/16" typical min
    FabricationProcess.DRILL: 0.0625,        # 1/16" bit minimum
}

# Minimum edge distance for cutting (factor of thickness)
MIN_EDGE_DISTANCE_FACTOR = {
    FabricationProcess.PLASMA_CUT: 1.5,
    FabricationProcess.LASER_CUT: 1.0,
    FabricationProcess.WATER_JET: 1.0,
    FabricationProcess.OXY_FUEL: 2.0,
    FabricationProcess.PUNCH: 1.5,
}

# Sheet metal bend radius minimums (factor of thickness)
MIN_BEND_RADIUS_FACTOR = {
    "mild_steel": 1.0,
    "stainless_steel": 1.5,
    "aluminum_soft": 0.5,
    "aluminum_hard": 2.0,
    "galvanized": 1.0,
}

# Standard plate thicknesses (inches)
STANDARD_PLATE_THICKNESSES = [
    0.0625, 0.075, 0.09375, 0.125, 0.1875, 0.25, 0.3125, 0.375,
    0.4375, 0.5, 0.5625, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25,
    1.375, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 4.0
]

# Standard sheet metal gauges
SHEET_METAL_GAUGES = {
    # Gauge: (thickness_in, weight_psf for steel)
    10: (0.1345, 5.625),
    11: (0.1196, 5.0),
    12: (0.1046, 4.375),
    14: (0.0747, 3.125),
    16: (0.0598, 2.5),
    18: (0.0478, 2.0),
    20: (0.0359, 1.5),
    22: (0.0299, 1.25),
    24: (0.0239, 1.0),
}

# Minimum cut widths for internal features (inches)
MIN_SLOT_WIDTH = {
    FabricationProcess.PLASMA_CUT: 0.375,
    FabricationProcess.LASER_CUT: 0.125,
    FabricationProcess.WATER_JET: 0.125,
    FabricationProcess.OXY_FUEL: 0.5,
}

# Maximum aspect ratio for slots
MAX_SLOT_ASPECT_RATIO = 10  # Length / Width

# Minimum distance between cuts (factor of thickness)
MIN_CUT_SPACING_FACTOR = 1.5

# Maximum plate sizes commonly available (ft)
MAX_PLATE_SIZES = {
    "standard": (48, 120),   # 4' x 10'
    "wide": (60, 240),       # 5' x 20'
    "extra_wide": (96, 480), # 8' x 40'
}


@dataclass
class PartGeometry:
    """Part geometry data for fabrication analysis."""
    length: float  # inches
    width: float  # inches
    thickness: float  # inches
    material: str = "mild_steel"

    # Features
    holes: List[Dict] = field(default_factory=list)  # {diameter, x, y}
    slots: List[Dict] = field(default_factory=list)  # {width, length, x, y}
    bends: List[Dict] = field(default_factory=list)  # {radius, angle, length}
    cutouts: List[Dict] = field(default_factory=list)  # {width, height, x, y}
    notches: List[Dict] = field(default_factory=list)  # {width, depth}

    # Process specification
    cutting_process: Optional[FabricationProcess] = None
    forming_process: Optional[str] = None


@dataclass
class FabricationValidationResult:
    """Fabrication feasibility validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    parts_checked: int = 0
    non_standard_thicknesses: int = 0
    tight_tolerances: int = 0
    difficult_features: int = 0
    nesting_efficiency: Optional[float] = None

    # Recommendations
    suggested_processes: List[str] = field(default_factory=list)
    material_substitutions: List[str] = field(default_factory=list)


class FabricationFeasibilityValidator:
    """
    Validates design for fabrication feasibility.

    Checks:
    1. Standard vs non-standard plate/sheet sizes
    2. Minimum hole sizes for cutting process
    3. Edge distances for cutting
    4. Slot width and aspect ratio
    5. Bend radius feasibility
    6. Cut spacing (between features)
    7. Weld access clearance
    8. Nesting feasibility (plate utilization)
    """

    def __init__(self):
        pass

    def validate_part(
        self,
        part: PartGeometry,
        process: Optional[FabricationProcess] = None
    ) -> FabricationValidationResult:
        """
        Validate a single part for fabrication feasibility.

        Args:
            part: Part geometry data
            process: Optional cutting process override

        Returns:
            FabricationValidationResult
        """
        result = FabricationValidationResult()
        result.parts_checked = 1

        # Determine cutting process
        cutting_process = process or part.cutting_process or self._suggest_cutting_process(part)
        result.suggested_processes.append(cutting_process.value)

        # Run checks
        self._check_standard_thickness(part, result)
        self._check_plate_size(part, result)
        self._check_hole_feasibility(part, cutting_process, result)
        self._check_slot_feasibility(part, cutting_process, result)
        self._check_edge_distances(part, cutting_process, result)
        self._check_feature_spacing(part, cutting_process, result)
        self._check_bend_feasibility(part, result)
        self._check_notch_feasibility(part, result)
        self._check_weld_access(part, result)

        return result

    def validate_assembly(
        self,
        parts: List[PartGeometry]
    ) -> FabricationValidationResult:
        """
        Validate multiple parts and check assembly feasibility.

        Args:
            parts: List of part geometries

        Returns:
            Combined validation result
        """
        result = FabricationValidationResult()
        result.parts_checked = len(parts)

        for i, part in enumerate(parts):
            part_result = self.validate_part(part)

            # Combine results
            result.total_checks += part_result.total_checks
            result.passed += part_result.passed
            result.failed += part_result.failed
            result.warnings += part_result.warnings
            result.critical_failures += part_result.critical_failures

            # Add part identifier to issues
            for issue in part_result.issues:
                issue.location = f"Part {i+1}: {issue.location or ''}"
                result.issues.append(issue)

            result.non_standard_thicknesses += part_result.non_standard_thicknesses
            result.tight_tolerances += part_result.tight_tolerances
            result.difficult_features += part_result.difficult_features

        # Check nesting efficiency
        self._check_nesting_efficiency(parts, result)

        return result

    def _suggest_cutting_process(self, part: PartGeometry) -> FabricationProcess:
        """Suggest appropriate cutting process based on part characteristics."""
        thickness = part.thickness
        has_small_holes = any(h.get("diameter", 1) < 0.5 for h in part.holes)
        has_tight_corners = any(c.get("radius", 1) < 0.25 for c in part.cutouts)

        # Decision tree for process selection
        if thickness <= 0.25:
            if has_small_holes or has_tight_corners:
                return FabricationProcess.LASER_CUT
            else:
                return FabricationProcess.PLASMA_CUT
        elif thickness <= 0.5:
            if has_small_holes:
                return FabricationProcess.WATER_JET
            else:
                return FabricationProcess.PLASMA_CUT
        elif thickness <= 1.0:
            return FabricationProcess.PLASMA_CUT
        else:
            return FabricationProcess.OXY_FUEL

    def _check_standard_thickness(self, part: PartGeometry, result: FabricationValidationResult):
        """Check if thickness is a standard size."""
        result.total_checks += 1

        # Find closest standard thickness
        closest = min(STANDARD_PLATE_THICKNESSES, key=lambda x: abs(x - part.thickness))
        diff = abs(part.thickness - closest)

        if diff < 0.001:  # Match
            result.passed += 1
        elif diff <= 0.03:  # Within 1/32"
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="thickness_standard",
                message=f"Thickness {part.thickness}\" close to standard {closest}\"",
                suggestion=f"Consider using standard {closest}\" for cost savings",
            ))
        else:
            result.non_standard_thicknesses += 1
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="thickness_non_standard",
                message=f"Non-standard thickness: {part.thickness}\"",
                location="Material specification",
                suggestion=f"Standard thicknesses: {closest}\" may reduce cost and lead time",
            ))

    def _check_plate_size(self, part: PartGeometry, result: FabricationValidationResult):
        """Check if part fits on standard plate sizes."""
        result.total_checks += 1

        length_ft = part.length / 12
        width_ft = part.width / 12

        # Check against standard sizes
        fits_standard = False
        recommended_size = None

        for size_name, (max_w, max_l) in MAX_PLATE_SIZES.items():
            max_w_ft = max_w / 12
            max_l_ft = max_l / 12
            if length_ft <= max_l_ft and width_ft <= max_w_ft:
                fits_standard = True
                recommended_size = size_name
                break
            # Check rotated
            if length_ft <= max_w_ft and width_ft <= max_l_ft:
                fits_standard = True
                recommended_size = size_name
                break

        if fits_standard:
            result.passed += 1
            if recommended_size != "standard":
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="plate_size",
                    message=f"Part requires {recommended_size} plate ({length_ft:.1f}' x {width_ft:.1f}')",
                    suggestion="Verify plate availability with supplier",
                ))
        else:
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="plate_size_exceeded",
                message=f"Part size {length_ft:.1f}' x {width_ft:.1f}' exceeds standard plate sizes",
                location="Overall dimensions",
                suggestion="Consider splitting into multiple pieces or sourcing special plate",
            ))

    def _check_hole_feasibility(
        self,
        part: PartGeometry,
        process: FabricationProcess,
        result: FabricationValidationResult
    ):
        """Check if holes are feasible for the cutting process."""
        if not part.holes:
            return

        result.total_checks += 1
        min_hole = MIN_HOLE_DIAMETER.get(process, 0.25)
        violations = []

        for i, hole in enumerate(part.holes):
            diameter = hole.get("diameter", 0)

            # Check minimum diameter
            if diameter < min_hole:
                violations.append((i, diameter, min_hole))

            # Check diameter vs thickness ratio
            if diameter < part.thickness:
                result.difficult_features += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="hole_thickness_ratio",
                    message=f"Hole #{i+1}: Dia {diameter}\" < thickness {part.thickness}\"",
                    location=f"Hole {i+1}",
                    suggestion="May require drilling after cutting or secondary operation",
                ))

        if violations:
            result.failed += 1
            for i, dia, min_d in violations:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="hole_too_small",
                    message=f"Hole #{i+1}: {dia}\" too small for {process.value} (min {min_d}\")",
                    location=f"Hole {i+1}",
                    suggestion=f"Use drilling or switch to laser/water jet cutting",
                ))
        else:
            result.passed += 1

    def _check_slot_feasibility(
        self,
        part: PartGeometry,
        process: FabricationProcess,
        result: FabricationValidationResult
    ):
        """Check if slots are feasible for the cutting process."""
        if not part.slots:
            return

        result.total_checks += 1
        min_width = MIN_SLOT_WIDTH.get(process, 0.25)
        violations = []

        for i, slot in enumerate(part.slots):
            width = slot.get("width", 0)
            length = slot.get("length", 0)

            # Check minimum width
            if width < min_width:
                violations.append((i, "width", width, min_width))

            # Check aspect ratio
            if length > 0 and width > 0:
                aspect = length / width
                if aspect > MAX_SLOT_ASPECT_RATIO:
                    result.difficult_features += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="slot_aspect_ratio",
                        message=f"Slot #{i+1}: Aspect ratio {aspect:.1f}:1 exceeds {MAX_SLOT_ASPECT_RATIO}:1",
                        location=f"Slot {i+1}",
                        suggestion="May cause distortion during cutting; consider multiple passes",
                    ))

        if violations:
            result.failed += 1
            for i, param, actual, min_val in violations:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="slot_too_narrow",
                    message=f"Slot #{i+1}: {param} {actual}\" < min {min_val}\" for {process.value}",
                    location=f"Slot {i+1}",
                    suggestion=f"Increase slot width or use water jet/laser",
                ))
        else:
            result.passed += 1

    def _check_edge_distances(
        self,
        part: PartGeometry,
        process: FabricationProcess,
        result: FabricationValidationResult
    ):
        """Check edge distances for cutting feasibility."""
        result.total_checks += 1

        min_factor = MIN_EDGE_DISTANCE_FACTOR.get(process, 1.5)
        min_edge = min_factor * part.thickness
        violations = []

        for i, hole in enumerate(part.holes):
            x = hole.get("x", 0)
            y = hole.get("y", 0)
            radius = hole.get("diameter", 0) / 2

            # Distance to each edge
            dist_left = x - radius
            dist_right = part.width - x - radius
            dist_bottom = y - radius
            dist_top = part.length - y - radius

            min_dist = min(dist_left, dist_right, dist_bottom, dist_top)
            if min_dist < min_edge and min_dist >= 0:
                violations.append((i, min_dist, min_edge))

        if violations:
            result.warnings += 1
            for i, actual, required in violations:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="edge_distance_fabrication",
                    message=f"Hole #{i+1}: Edge distance {actual:.3f}\" tight for {process.value}",
                    location=f"Hole {i+1}",
                    suggestion=f"Recommend min {required:.3f}\" ({min_factor}× thickness) for clean cut",
                ))
        else:
            result.passed += 1

    def _check_feature_spacing(
        self,
        part: PartGeometry,
        process: FabricationProcess,
        result: FabricationValidationResult
    ):
        """Check spacing between cut features."""
        all_features = part.holes + part.slots + part.cutouts
        if len(all_features) < 2:
            return

        result.total_checks += 1
        min_spacing = MIN_CUT_SPACING_FACTOR * part.thickness
        violations = []

        for i in range(len(all_features)):
            for j in range(i + 1, len(all_features)):
                f1 = all_features[i]
                f2 = all_features[j]

                # Calculate center-to-center distance
                dx = f2.get("x", 0) - f1.get("x", 0)
                dy = f2.get("y", 0) - f1.get("y", 0)
                distance = (dx**2 + dy**2) ** 0.5

                # Subtract radii/half-widths for edge-to-edge distance
                r1 = f1.get("diameter", f1.get("width", 0)) / 2
                r2 = f2.get("diameter", f2.get("width", 0)) / 2
                edge_distance = distance - r1 - r2

                if edge_distance > 0 and edge_distance < min_spacing:
                    violations.append((i, j, edge_distance, min_spacing))

        if violations:
            result.warnings += 1
            for i, j, actual, required in violations[:3]:  # Limit to first 3
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="feature_spacing",
                    message=f"Features {i+1} & {j+1}: Spacing {actual:.3f}\" < {required:.3f}\"",
                    suggestion=f"Tight spacing may cause heat distortion during cutting",
                ))
        else:
            result.passed += 1

    def _check_bend_feasibility(self, part: PartGeometry, result: FabricationValidationResult):
        """Check if bends are feasible for the material."""
        if not part.bends:
            return

        result.total_checks += 1

        # Get minimum bend radius factor for material
        material_key = part.material.lower().replace(" ", "_")
        min_factor = MIN_BEND_RADIUS_FACTOR.get(material_key, 1.0)
        min_radius = min_factor * part.thickness

        violations = []
        for i, bend in enumerate(part.bends):
            radius = bend.get("radius", 0)
            angle = bend.get("angle", 90)

            if radius < min_radius:
                violations.append((i, radius, min_radius))

            # Check for acute angles (< 90 degrees)
            if angle < 90:
                result.difficult_features += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="acute_bend",
                    message=f"Bend #{i+1}: {angle}° acute bend requires special tooling",
                    location=f"Bend {i+1}",
                    suggestion="Verify brake press capability for acute bends",
                ))

        if violations:
            result.failed += 1
            for i, actual, required in violations:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="bend_radius_too_small",
                    message=f"Bend #{i+1}: Radius {actual}\" < min {required:.3f}\" for {part.material}",
                    location=f"Bend {i+1}",
                    suggestion=f"Increase bend radius to {required:.3f}\" ({min_factor}× thickness) or use softer material",
                    standard_reference="Sheet metal bend radius tables",
                ))
        else:
            result.passed += 1

    def _check_notch_feasibility(self, part: PartGeometry, result: FabricationValidationResult):
        """Check notch dimensions for fabrication."""
        if not part.notches:
            return

        result.total_checks += 1
        min_notch_width = part.thickness  # Minimum notch width = thickness

        violations = []
        for i, notch in enumerate(part.notches):
            width = notch.get("width", 0)
            depth = notch.get("depth", 0)

            if width < min_notch_width:
                violations.append((i, "width", width, min_notch_width))

            # Check aspect ratio
            if depth > 0 and width > 0 and depth / width > 5:
                result.difficult_features += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="notch_aspect_ratio",
                    message=f"Notch #{i+1}: Deep/narrow notch may cause stress concentration",
                    location=f"Notch {i+1}",
                    suggestion="Consider adding radius at notch corners",
                ))

        if violations:
            result.warnings += 1
            for i, param, actual, min_val in violations:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="notch_too_narrow",
                    message=f"Notch #{i+1}: {param} {actual}\" < min {min_val:.3f}\"",
                    location=f"Notch {i+1}",
                    suggestion="Increase notch width for proper cut quality",
                ))
        else:
            result.passed += 1

    def _check_weld_access(self, part: PartGeometry, result: FabricationValidationResult):
        """Check for adequate weld access (placeholder for geometry analysis)."""
        result.total_checks += 1

        # This would typically analyze 3D geometry for weld torch access
        # For now, check for tight corners in cutouts

        tight_corners = 0
        for cutout in part.cutouts:
            radius = cutout.get("corner_radius", 0)
            if radius < 0.25:  # Less than 1/4" corner radius
                tight_corners += 1

        if tight_corners > 0:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="weld_access",
                message=f"{tight_corners} cutouts with tight corners may limit weld access",
                suggestion="Verify welder can access all required weld locations",
            ))

        result.passed += 1

    def _check_nesting_efficiency(
        self,
        parts: List[PartGeometry],
        result: FabricationValidationResult
    ):
        """Estimate nesting efficiency for batch of parts."""
        if not parts:
            return

        result.total_checks += 1

        # Group by thickness
        thickness_groups: Dict[float, List[PartGeometry]] = {}
        for part in parts:
            key = round(part.thickness, 4)
            if key not in thickness_groups:
                thickness_groups[key] = []
            thickness_groups[key].append(part)

        total_part_area = sum(p.length * p.width for p in parts)

        # Estimate plate usage (simple bounding box approach)
        total_plate_area = 0
        for thickness, group_parts in thickness_groups.items():
            # Estimate plate size needed
            max_length = max(p.length for p in group_parts)
            max_width = max(p.width for p in group_parts)

            # Find suitable plate
            plate_w, plate_l = 48, 120  # Default 4x10
            for size_name, (pw, pl) in MAX_PLATE_SIZES.items():
                if max_length <= pl and max_width <= pw:
                    plate_l, plate_w = pl, pw
                    break

            # Rough estimate: parts need ~1.2x their area due to nesting gaps
            group_area = sum(p.length * p.width * 1.2 for p in group_parts)
            plates_needed = max(1, int(group_area / (plate_w * plate_l)) + 1)
            total_plate_area += plates_needed * plate_w * plate_l

        if total_plate_area > 0:
            efficiency = (total_part_area / total_plate_area) * 100
            result.nesting_efficiency = efficiency

            if efficiency < 50:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="nesting_efficiency",
                    message=f"Estimated nesting efficiency: {efficiency:.0f}%",
                    suggestion="Consider optimizing part sizes or adding filler parts to reduce scrap",
                ))
                result.warnings += 1
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="nesting_efficiency",
                    message=f"Estimated nesting efficiency: {efficiency:.0f}%",
                    suggestion="Good material utilization",
                ))
        else:
            result.passed += 1

    def to_dict(self, result: FabricationValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "fabrication_feasibility",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "parts_checked": result.parts_checked,
                "non_standard_thicknesses": result.non_standard_thicknesses,
                "tight_tolerances": result.tight_tolerances,
                "difficult_features": result.difficult_features,
                "nesting_efficiency": result.nesting_efficiency,
            },
            "suggested_processes": result.suggested_processes,
            "material_substitutions": result.material_substitutions,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "check_type": issue.check_type,
                    "message": issue.message,
                    "location": issue.location,
                    "suggestion": issue.suggestion,
                    "standard_reference": issue.standard_reference,
                }
                for issue in result.issues
            ],
        }
