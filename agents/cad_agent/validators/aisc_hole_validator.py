"""
AISC Hole & Edge Distance Validator
====================================
Validates hole patterns against AISC Steel Construction Manual requirements.

Phase 25.1 - Geometry & Dimensions
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.aisc_hole")


# AISC Table J3.4 - Minimum Edge Distance (inches)
# Based on bolt diameter and edge type
AISC_MIN_EDGE_DISTANCE = {
    # bolt_dia: (sheared_edge, rolled_edge)
    0.5: (0.875, 0.75),      # 1/2"
    0.625: (1.125, 0.875),   # 5/8"
    0.75: (1.25, 1.0),       # 3/4"
    0.875: (1.5, 1.125),     # 7/8"
    1.0: (1.75, 1.25),       # 1"
    1.125: (2.0, 1.5),       # 1-1/8"
    1.25: (2.25, 1.625),     # 1-1/4"
    1.375: (2.375, 1.75),    # 1-3/8"
    1.5: (2.625, 1.875),     # 1-1/2"
}

# Minimum hole spacing per AISC J3.3 (2.67 × bolt diameter)
MIN_SPACING_FACTOR = 2.67

# Preferred hole spacing (3 × bolt diameter typical)
PREFERRED_SPACING_FACTOR = 3.0

# Standard hole sizes per AISC Table J3.3
STANDARD_HOLE_SIZES = {
    # bolt_dia: standard_hole_dia
    0.5: 0.5625,      # 1/2" bolt = 9/16" hole
    0.625: 0.6875,    # 5/8" bolt = 11/16" hole
    0.75: 0.8125,     # 3/4" bolt = 13/16" hole
    0.875: 0.9375,    # 7/8" bolt = 15/16" hole
    1.0: 1.0625,      # 1" bolt = 1-1/16" hole
    1.125: 1.1875,    # 1-1/8" bolt = 1-3/16" hole
    1.25: 1.3125,     # 1-1/4" bolt = 1-5/16" hole
    1.375: 1.4375,    # 1-3/8" bolt = 1-7/16" hole
    1.5: 1.5625,      # 1-1/2" bolt = 1-9/16" hole
}

# Common drill sizes (fractional inches)
STANDARD_DRILL_SIZES = [
    0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5,
    0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375,
    1.0, 1.0625, 1.125, 1.1875, 1.25, 1.3125, 1.375,
    1.4375, 1.5, 1.5625, 1.625, 1.75, 1.875, 2.0
]

# Oversized hole dimensions per AISC Table J3.3 (inches)
OVERSIZED_HOLE_SIZES = {
    # bolt_dia: oversized_hole_dia
    0.5: 0.625,       # 1/2" bolt = 5/8" hole
    0.625: 0.8125,    # 5/8" bolt = 13/16" hole
    0.75: 0.9375,     # 3/4" bolt = 15/16" hole
    0.875: 1.0625,    # 7/8" bolt = 1-1/16" hole
    1.0: 1.25,        # 1" bolt = 1-1/4" hole
    1.125: 1.4375,    # ≥1-1/8" bolt: d + 5/16"
    1.25: 1.5625,
    1.375: 1.6875,
    1.5: 1.8125,
}

# Short-slotted hole dimensions per AISC Table J3.3
# (width × length)
SHORT_SLOT_SIZES = {
    # bolt_dia: (width, length)
    0.5: (0.5625, 0.6875),      # 9/16 × 11/16
    0.625: (0.6875, 0.875),     # 11/16 × 7/8
    0.75: (0.8125, 1.0),        # 13/16 × 1
    0.875: (0.9375, 1.125),     # 15/16 × 1-1/8
    1.0: (1.0625, 1.3125),      # 1-1/16 × 1-5/16
    1.125: (1.1875, 1.5625),    # ≥1-1/8": d+1/16 × d+7/16
}

# Long-slotted hole dimensions per AISC Table J3.3
LONG_SLOT_SIZES = {
    # bolt_dia: (width, length)
    0.5: (0.5625, 1.25),        # 9/16 × 1-1/4
    0.625: (0.6875, 1.5625),    # 11/16 × 1-9/16
    0.75: (0.8125, 1.875),      # 13/16 × 1-7/8
    0.875: (0.9375, 2.1875),    # 15/16 × 2-3/16
    1.0: (1.0625, 2.5),         # 1-1/16 × 2-1/2
    # ≥1-1/8": width=d+1/16, length=2.5d
}

# Bolt shear capacity (kips) - A325/A490 bolts
# Values per AISC Table J3.2 (threads excluded from shear plane)
BOLT_SHEAR_CAPACITY = {
    # (bolt_dia, grade): shear_capacity_per_plane
    (0.5, "A325"): 6.01,
    (0.625, "A325"): 9.39,
    (0.75, "A325"): 13.5,
    (0.875, "A325"): 18.4,
    (1.0, "A325"): 24.1,
    (1.125, "A325"): 30.5,
    (1.25, "A325"): 37.6,
    (0.5, "A490"): 7.51,
    (0.625, "A490"): 11.7,
    (0.75, "A490"): 16.9,
    (0.875, "A490"): 23.0,
    (1.0, "A490"): 30.1,
    (1.125, "A490"): 38.1,
    (1.25, "A490"): 47.0,
}

# Minimum pretension (kips) per AISC Table J3.1
MIN_PRETENSION = {
    # bolt_dia: (A325, A490)
    0.5: (12, 15),
    0.625: (19, 24),
    0.75: (28, 35),
    0.875: (39, 49),
    1.0: (51, 64),
    1.125: (64, 80),
    1.25: (81, 102),
    1.375: (97, 121),
    1.5: (118, 148),
}


@dataclass
class HoleData:
    """Data for a single hole."""
    diameter: float  # inches
    x: float = 0.0   # x coordinate
    y: float = 0.0   # y coordinate
    edge_distance_x: Optional[float] = None
    edge_distance_y: Optional[float] = None
    hole_type: str = "standard"  # standard, oversized, short_slot, long_slot
    slot_width: Optional[float] = None  # For slotted holes
    slot_length: Optional[float] = None  # For slotted holes
    slot_orientation: Optional[str] = None  # "parallel" or "perpendicular" to load
    bolt_diameter: Optional[float] = None
    bolt_grade: str = "A325"  # A325 or A490
    connection_type: str = "bearing"  # bearing or slip_critical


@dataclass
class AISCHoleValidationResult:
    """AISC hole validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    holes_checked: int = 0
    edge_distance_violations: int = 0
    spacing_violations: int = 0
    non_standard_holes: int = 0
    oversized_holes: int = 0
    slotted_holes: int = 0
    slip_critical_connections: int = 0


class AISCHoleValidator:
    """
    Validates hole patterns against AISC requirements.

    Checks:
    1. Edge distance vs AISC J3.4 minimum
    2. Edge distance vs material thickness rules
    3. Hole spacing/pitch (min 2.67d per AISC)
    4. Hole-to-hole alignment (same part)
    5. Standard hole sizes for bolt diameters
    6. Slot length-to-width ratio
    7. Oversized hole requirements
    """

    def __init__(self):
        pass

    def validate_holes(
        self,
        holes: List[HoleData],
        material_thickness: Optional[float] = None,
        edge_type: str = "sheared"
    ) -> AISCHoleValidationResult:
        """
        Validate a list of holes against AISC requirements.

        Args:
            holes: List of HoleData objects
            material_thickness: Material thickness in inches
            edge_type: "sheared" or "rolled" edge

        Returns:
            AISCHoleValidationResult
        """
        result = AISCHoleValidationResult()
        result.holes_checked = len(holes)

        if not holes:
            return result

        # Check each hole
        for i, hole in enumerate(holes):
            self._check_standard_size(hole, i, result)
            self._check_edge_distance(hole, i, edge_type, result)
            if material_thickness:
                self._check_edge_vs_thickness(hole, i, material_thickness, result)
            # New checks
            self._check_oversized_hole(hole, i, result)
            self._check_slotted_hole(hole, i, result)
            self._check_slip_critical(hole, i, result)

        # Check hole spacing between pairs
        self._check_hole_spacing(holes, result)

        # Check alignment
        self._check_hole_alignment(holes, result)

        # Check bearing capacity if thickness provided
        if material_thickness:
            self._check_bearing_capacity(holes, material_thickness, result)

        return result

    def _check_standard_size(self, hole: HoleData, index: int, result: AISCHoleValidationResult):
        """Check if hole size is a standard drill size."""
        result.total_checks += 1

        # Find closest standard size
        closest = min(STANDARD_DRILL_SIZES, key=lambda x: abs(x - hole.diameter))
        diff = abs(hole.diameter - closest)

        if diff < 0.001:  # Essentially equal
            result.passed += 1
        elif diff <= 0.03:  # Within 1/32"
            result.passed += 1
        else:
            result.non_standard_holes += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="non_standard_hole",
                message=f"Hole #{index+1}: {hole.diameter}\" is non-standard size",
                location=f"Hole {index+1}",
                suggestion=f"Consider standard size: {closest}\"",
                standard_reference="AISC Table J3.3",
            ))
            result.warnings += 1

    def _check_edge_distance(
        self,
        hole: HoleData,
        index: int,
        edge_type: str,
        result: AISCHoleValidationResult
    ):
        """Check edge distance against AISC J3.4."""
        result.total_checks += 1

        # Determine bolt size from hole size
        bolt_dia = self._get_bolt_from_hole(hole.diameter)

        if bolt_dia not in AISC_MIN_EDGE_DISTANCE:
            # Interpolate or use closest
            bolt_dia = min(AISC_MIN_EDGE_DISTANCE.keys(), key=lambda x: abs(x - bolt_dia))

        min_edge = AISC_MIN_EDGE_DISTANCE[bolt_dia]
        min_dist = min_edge[0] if edge_type == "sheared" else min_edge[1]

        # Check both x and y edge distances if provided
        violations = []
        if hole.edge_distance_x is not None and hole.edge_distance_x < min_dist:
            violations.append(("X", hole.edge_distance_x))
        if hole.edge_distance_y is not None and hole.edge_distance_y < min_dist:
            violations.append(("Y", hole.edge_distance_y))

        if violations:
            result.edge_distance_violations += 1
            result.failed += 1
            result.critical_failures += 1
            for direction, actual in violations:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="edge_distance_aisc",
                    message=f"Hole #{index+1}: {direction} edge distance {actual}\" < min {min_dist}\"",
                    location=f"Hole {index+1}",
                    suggestion=f"Increase edge distance to min {min_dist}\" per AISC J3.4",
                    standard_reference="AISC Table J3.4",
                ))
        else:
            result.passed += 1

    def _check_edge_vs_thickness(
        self,
        hole: HoleData,
        index: int,
        thickness: float,
        result: AISCHoleValidationResult
    ):
        """Check edge distance vs material thickness rule."""
        result.total_checks += 1

        # Rule of thumb: min edge = 1.5 × hole diameter or 2 × thickness, whichever larger
        min_by_hole = 1.5 * hole.diameter
        min_by_thickness = 2.0 * thickness
        min_edge = max(min_by_hole, min_by_thickness)

        actual_edge = None
        if hole.edge_distance_x is not None and hole.edge_distance_y is not None:
            actual_edge = min(hole.edge_distance_x, hole.edge_distance_y)
        elif hole.edge_distance_x is not None:
            actual_edge = hole.edge_distance_x
        elif hole.edge_distance_y is not None:
            actual_edge = hole.edge_distance_y

        if actual_edge is not None and actual_edge < min_edge:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="edge_distance_thickness",
                message=f"Hole #{index+1}: Edge {actual_edge}\" tight for {thickness}\" material",
                location=f"Hole {index+1}",
                suggestion=f"Recommended min edge: {min_edge:.3f}\"",
            ))
            result.warnings += 1
        else:
            result.passed += 1

    def _check_hole_spacing(self, holes: List[HoleData], result: AISCHoleValidationResult):
        """Check spacing between all hole pairs."""
        if len(holes) < 2:
            return

        result.total_checks += 1

        for i in range(len(holes)):
            for j in range(i + 1, len(holes)):
                h1, h2 = holes[i], holes[j]

                # Calculate center-to-center distance
                dx = h2.x - h1.x
                dy = h2.y - h1.y
                distance = (dx**2 + dy**2) ** 0.5

                # Use larger bolt diameter for spacing check
                max_hole = max(h1.diameter, h2.diameter)
                bolt_dia = self._get_bolt_from_hole(max_hole)

                min_spacing = MIN_SPACING_FACTOR * bolt_dia
                preferred_spacing = PREFERRED_SPACING_FACTOR * bolt_dia

                if distance < min_spacing:
                    result.spacing_violations += 1
                    result.failed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        check_type="hole_spacing_min",
                        message=f"Holes {i+1}-{j+1}: Spacing {distance:.3f}\" < min {min_spacing:.3f}\"",
                        suggestion=f"Increase spacing to min {min_spacing:.3f}\" (2.67d per AISC J3.3)",
                        standard_reference="AISC J3.3",
                    ))
                elif distance < preferred_spacing:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="hole_spacing_preferred",
                        message=f"Holes {i+1}-{j+1}: Spacing {distance:.3f}\" is tight (prefer {preferred_spacing:.3f}\")",
                        suggestion=f"Consider increasing to {preferred_spacing:.3f}\" (3d preferred)",
                    ))

        if result.spacing_violations == 0:
            result.passed += 1

    def _check_hole_alignment(self, holes: List[HoleData], result: AISCHoleValidationResult):
        """Check if holes are aligned in rows/columns."""
        if len(holes) < 2:
            return

        result.total_checks += 1

        # Group by approximate X and Y coordinates
        x_groups: Dict[float, List[int]] = {}
        y_groups: Dict[float, List[int]] = {}
        tolerance = 0.0625  # 1/16" alignment tolerance

        for i, hole in enumerate(holes):
            # Find or create X group
            found_x = False
            for key in x_groups:
                if abs(hole.x - key) < tolerance:
                    x_groups[key].append(i)
                    found_x = True
                    break
            if not found_x:
                x_groups[hole.x] = [i]

            # Find or create Y group
            found_y = False
            for key in y_groups:
                if abs(hole.y - key) < tolerance:
                    y_groups[key].append(i)
                    found_y = True
                    break
            if not found_y:
                y_groups[hole.y] = [i]

        # Check for misaligned holes (not in any row/column with others)
        aligned_holes = set()
        for group in x_groups.values():
            if len(group) > 1:
                aligned_holes.update(group)
        for group in y_groups.values():
            if len(group) > 1:
                aligned_holes.update(group)

        misaligned = set(range(len(holes))) - aligned_holes
        if misaligned and len(holes) > 2:
            for i in misaligned:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="hole_alignment",
                    message=f"Hole #{i+1} not aligned with other holes",
                    location=f"Hole {i+1}",
                    suggestion="Verify intentional placement",
                ))

        result.passed += 1

    def _get_bolt_from_hole(self, hole_dia: float) -> float:
        """Estimate bolt diameter from hole diameter."""
        # Standard hole is 1/16" larger than bolt
        bolt_dia = hole_dia - 0.0625

        # Round to nearest standard bolt size
        standard_bolts = [0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25, 1.375, 1.5]
        return min(standard_bolts, key=lambda x: abs(x - bolt_dia))

    def validate_cross_part_alignment(
        self,
        part_a_holes: List[HoleData],
        part_b_holes: List[HoleData],
        tolerance: float = 0.0625
    ) -> AISCHoleValidationResult:
        """
        Check hole alignment between mating parts.

        Args:
            part_a_holes: Holes from first part
            part_b_holes: Holes from mating part
            tolerance: Alignment tolerance (default 1/16")

        Returns:
            Validation result with alignment findings
        """
        result = AISCHoleValidationResult()
        result.total_checks += 1

        matched = []
        unmatched_a = list(range(len(part_a_holes)))
        unmatched_b = list(range(len(part_b_holes)))

        for i, h_a in enumerate(part_a_holes):
            for j, h_b in enumerate(part_b_holes):
                if j not in unmatched_b:
                    continue

                # Check position alignment
                dx = abs(h_a.x - h_b.x)
                dy = abs(h_a.y - h_b.y)

                if dx <= tolerance and dy <= tolerance:
                    # Check diameter compatibility
                    dia_diff = abs(h_a.diameter - h_b.diameter)

                    if dia_diff <= 0.0625:  # Same size within 1/16"
                        matched.append((i, j, "PASS"))
                        if i in unmatched_a:
                            unmatched_a.remove(i)
                        unmatched_b.remove(j)
                    else:
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            check_type="cross_part_hole_size",
                            message=f"Mating holes size mismatch: {h_a.diameter}\" vs {h_b.diameter}\"",
                            suggestion="Verify hole sizes match for bolted connection",
                        ))
                        result.warnings += 1

        # Report unmatched holes
        if unmatched_a or unmatched_b:
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="cross_part_alignment",
                message=f"Hole alignment issue: {len(unmatched_a)} holes in Part A, {len(unmatched_b)} in Part B unmatched",
                suggestion="Verify hole patterns align between mating parts",
            ))
        else:
            result.passed += 1

        return result

    def _check_oversized_hole(self, hole: HoleData, index: int, result: AISCHoleValidationResult):
        """Check oversized hole dimensions per AISC J3.3."""
        if hole.hole_type != "oversized":
            return

        result.total_checks += 1
        result.oversized_holes += 1

        bolt_dia = hole.bolt_diameter or self._get_bolt_from_hole(hole.diameter)

        if bolt_dia in OVERSIZED_HOLE_SIZES:
            expected = OVERSIZED_HOLE_SIZES[bolt_dia]
            tolerance = 0.03  # 1/32"

            if abs(hole.diameter - expected) > tolerance:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="oversized_hole_wrong",
                    message=f"Hole #{index+1}: Oversized hole {hole.diameter}\" doesn't match Table J3.3 ({expected}\")",
                    location=f"Hole {index+1}",
                    suggestion=f"Use {expected}\" dia for {bolt_dia}\" bolt oversized hole",
                    standard_reference="AISC Table J3.3",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

    def _check_slotted_hole(self, hole: HoleData, index: int, result: AISCHoleValidationResult):
        """Check slotted hole dimensions per AISC J3.3."""
        if hole.hole_type not in ["short_slot", "long_slot"]:
            return

        result.total_checks += 1
        result.slotted_holes += 1

        bolt_dia = hole.bolt_diameter or self._get_bolt_from_hole(hole.slot_width or hole.diameter)
        slot_table = SHORT_SLOT_SIZES if hole.hole_type == "short_slot" else LONG_SLOT_SIZES

        if bolt_dia in slot_table and hole.slot_width and hole.slot_length:
            expected_w, expected_l = slot_table[bolt_dia]
            tolerance = 0.03

            issues_found = []
            if abs(hole.slot_width - expected_w) > tolerance:
                issues_found.append(f"width {hole.slot_width}\" vs {expected_w}\"")
            if abs(hole.slot_length - expected_l) > tolerance:
                issues_found.append(f"length {hole.slot_length}\" vs {expected_l}\"")

            if issues_found:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="slot_dimensions",
                    message=f"Hole #{index+1}: Slot size incorrect: {', '.join(issues_found)}",
                    location=f"Hole {index+1}",
                    suggestion=f"Use {expected_w}\" × {expected_l}\" for {bolt_dia}\" bolt {hole.hole_type.replace('_', ' ')}",
                    standard_reference="AISC Table J3.3",
                ))
            else:
                result.passed += 1

        # Check slot orientation for long slots
        if hole.hole_type == "long_slot" and hole.slot_orientation:
            result.total_checks += 1
            if hole.slot_orientation == "parallel" and hole.connection_type == "bearing":
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="long_slot_orientation",
                    message=f"Hole #{index+1}: Long slot parallel to load in bearing connection",
                    location=f"Hole {index+1}",
                    suggestion="Consider perpendicular orientation or slip-critical connection",
                    standard_reference="AISC J3.3",
                ))
                result.warnings += 1
            else:
                result.passed += 1

    def _check_slip_critical(self, hole: HoleData, index: int, result: AISCHoleValidationResult):
        """Check slip-critical connection requirements."""
        if hole.connection_type != "slip_critical":
            return

        result.total_checks += 1
        result.slip_critical_connections += 1

        bolt_dia = hole.bolt_diameter or self._get_bolt_from_hole(hole.diameter)
        grade = hole.bolt_grade.upper()

        # Slip-critical requires pretension
        if bolt_dia in MIN_PRETENSION:
            pretension = MIN_PRETENSION[bolt_dia]
            grade_idx = 0 if grade == "A325" else 1

            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="slip_critical_pretension",
                message=f"Hole #{index+1}: Slip-critical connection requires min pretension {pretension[grade_idx]} kips for {grade} bolt",
                location=f"Hole {index+1}",
                suggestion="Verify bolt pretension specification in notes",
                standard_reference="AISC Table J3.1",
            ))

        # Slip-critical with oversized/slotted requires washer
        if hole.hole_type in ["oversized", "short_slot", "long_slot"]:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="slip_critical_washer",
                message=f"Hole #{index+1}: {hole.hole_type.replace('_', ' ')} in slip-critical requires hardened washer",
                location=f"Hole {index+1}",
                suggestion="Add F436 hardened washer callout",
                standard_reference="AISC J3.8",
            ))
            result.warnings += 1

        result.passed += 1

    def _check_bearing_capacity(
        self,
        holes: List[HoleData],
        thickness: float,
        result: AISCHoleValidationResult
    ):
        """Check bolt bearing capacity."""
        result.total_checks += 1

        # Group holes by bolt size
        bolt_groups: Dict[float, int] = {}
        for hole in holes:
            bolt_dia = hole.bolt_diameter or self._get_bolt_from_hole(hole.diameter)
            bolt_groups[bolt_dia] = bolt_groups.get(bolt_dia, 0) + 1

        # Provide bearing capacity info
        for bolt_dia, count in bolt_groups.items():
            # Nominal bearing capacity = 2.4 × d × t × Fu
            # Assume Fu = 58 ksi for A36, 65 ksi for A572 Gr 50
            fu = 58  # ksi, conservative
            bearing_per_bolt = 2.4 * bolt_dia * thickness * fu  # kips

            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="bearing_capacity",
                message=f"{count}× {bolt_dia}\" bolts: Bearing capacity ~{bearing_per_bolt:.1f} kips/bolt (2.4dtFu, Fu=58ksi)",
                suggestion="Verify applied loads vs capacity",
                standard_reference="AISC J3.10",
            ))

        result.passed += 1

    def validate_net_section(
        self,
        gross_area: float,
        holes: List[HoleData],
        material_fy: float = 50  # ksi
    ) -> AISCHoleValidationResult:
        """
        Check net section area reduction.

        Args:
            gross_area: Gross cross-sectional area (sq in)
            holes: Holes in the section
            material_fy: Yield strength (ksi)

        Returns:
            Validation result
        """
        result = AISCHoleValidationResult()
        result.total_checks += 1

        # Calculate net area (simplified - assumes all holes in same plane)
        total_hole_area = 0
        for hole in holes:
            if hole.hole_type in ["short_slot", "long_slot"]:
                # Use slot width for net area
                width = hole.slot_width or hole.diameter
            else:
                width = hole.diameter

            # Net area deduction per AISC D3.2 (add 1/16" to hole dia)
            effective_width = width + 0.0625
            # Assume same thickness for all holes
            total_hole_area += effective_width

        # Need thickness to compute actual area - use estimate
        if holes:
            # Estimate based on ratio
            reduction_ratio = total_hole_area / (gross_area ** 0.5)  # Rough estimate

            if reduction_ratio > 0.15:  # >15% reduction
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="net_section_reduction",
                    message=f"Significant net section reduction from {len(holes)} holes",
                    suggestion="Verify An/Ag ratio and tension member capacity per AISC D3",
                    standard_reference="AISC D3.2",
                ))
                result.warnings += 1
            else:
                result.passed += 1
        else:
            result.passed += 1

        return result

    def to_dict(self, result: AISCHoleValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "aisc_hole",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "holes_checked": result.holes_checked,
                "edge_distance_violations": result.edge_distance_violations,
                "spacing_violations": result.spacing_violations,
                "non_standard_holes": result.non_standard_holes,
                "oversized_holes": result.oversized_holes,
                "slotted_holes": result.slotted_holes,
                "slip_critical_connections": result.slip_critical_connections,
            },
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
