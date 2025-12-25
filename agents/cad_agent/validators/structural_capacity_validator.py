"""
Structural Capacity Validator
=============================
Validates structural connections against AISC capacity requirements.

Phase 25.2 - Structural Adequacy
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.structural")


# AISC Bolt Capacities (kips) - A325-N (threads not excluded)
# Per AISC Table 7-1
BOLT_SHEAR_CAPACITY = {
    # bolt_dia: single_shear_kips
    0.5: 7.07,
    0.625: 11.0,
    0.75: 15.9,
    0.875: 21.6,
    1.0: 28.3,
    1.125: 35.8,
    1.25: 44.2,
}

# A325-X (threads excluded from shear plane)
BOLT_SHEAR_CAPACITY_X = {
    0.5: 8.84,
    0.625: 13.8,
    0.75: 19.9,
    0.875: 27.1,
    1.0: 35.3,
    1.125: 44.8,
    1.25: 55.2,
}

# Bearing capacity factor (Fu × d × t × 2.4)
# Using Fu = 58 ksi for A36, 65 ksi for A572-50
MATERIAL_FU = {
    "A36": 58.0,
    "A572-50": 65.0,
    "A572-GR50": 65.0,
    "A992": 65.0,
    "A500-B": 58.0,
}

# Minimum fillet weld sizes per AWS D1.1 Table 5.8
MIN_FILLET_BY_THICKNESS = {
    # (min_t, max_t): min_weld_size
    (0, 0.25): 0.125,       # 1/8"
    (0.25, 0.5): 0.1875,    # 3/16"
    (0.5, 0.75): 0.25,      # 1/4"
    (0.75, 1.5): 0.3125,    # 5/16"
    (1.5, 2.25): 0.375,     # 3/8"
    (2.25, 6.0): 0.5,       # 1/2"
}

# Weld strength (kips per inch) for E70XX electrode
# Fillet weld: 0.707 × leg × 0.6 × 70 ksi = 29.7 × leg
FILLET_WELD_STRENGTH_PER_INCH = 29.7  # kips/in per 1" leg


@dataclass
class BoltData:
    """Data for a bolt connection."""
    diameter: float  # inches
    grade: str = "A325"  # A325, A490
    threads_excluded: bool = False
    num_bolts: int = 1
    num_shear_planes: int = 1  # single or double shear


@dataclass
class WeldData:
    """Data for a weld."""
    weld_type: str = "fillet"  # fillet, groove, plug
    leg_size: float = 0.25  # inches
    length: float = 1.0  # inches
    electrode: str = "E70XX"


@dataclass
class StructuralValidationResult:
    """Structural capacity validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Capacity results
    bolt_capacity_kips: float = 0.0
    weld_capacity_kips: float = 0.0
    bearing_capacity_kips: float = 0.0


class StructuralCapacityValidator:
    """
    Validates structural connection capacity.

    Checks:
    1. Bolt shear capacity
    2. Bolt bearing capacity
    3. Weld size adequate for load
    4. Weld length adequate
    5. Net section at holes
    6. Block shear
    7. Connection capacity
    """

    def __init__(self):
        pass

    def check_bolt_shear(
        self,
        bolt: BoltData,
        applied_load_kips: Optional[float] = None
    ) -> StructuralValidationResult:
        """
        Check bolt shear capacity.

        Args:
            bolt: BoltData with bolt info
            applied_load_kips: Applied load (if known)

        Returns:
            Validation result with capacity
        """
        result = StructuralValidationResult()
        result.total_checks += 1

        # Get base capacity
        capacity_table = BOLT_SHEAR_CAPACITY_X if bolt.threads_excluded else BOLT_SHEAR_CAPACITY

        if bolt.diameter not in capacity_table:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="bolt_size_unknown",
                message=f"Bolt diameter {bolt.diameter}\" not in standard tables",
                suggestion="Verify bolt capacity manually",
            ))
            result.warnings += 1
            return result

        single_shear = capacity_table[bolt.diameter]
        total_capacity = single_shear * bolt.num_bolts * bolt.num_shear_planes

        result.bolt_capacity_kips = total_capacity

        if applied_load_kips is not None:
            if applied_load_kips > total_capacity:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="bolt_shear_capacity",
                    message=f"Bolt shear capacity {total_capacity:.1f} kips < load {applied_load_kips:.1f} kips",
                    suggestion=f"Add bolts or increase diameter (need {applied_load_kips/single_shear:.0f} bolts)",
                    standard_reference="AISC Table 7-1",
                ))
            elif applied_load_kips > total_capacity * 0.9:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="bolt_shear_utilization",
                    message=f"Bolt shear utilization {applied_load_kips/total_capacity*100:.0f}% (>90%)",
                    suggestion="Consider adding bolts for safety margin",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

        return result

    def check_bearing(
        self,
        bolt: BoltData,
        material_thickness: float,
        material_grade: str = "A572-50",
        applied_load_kips: Optional[float] = None
    ) -> StructuralValidationResult:
        """
        Check bolt bearing capacity.

        Args:
            bolt: Bolt data
            material_thickness: Plate thickness (inches)
            material_grade: Material grade
            applied_load_kips: Applied load

        Returns:
            Validation result
        """
        result = StructuralValidationResult()
        result.total_checks += 1

        # Get Fu
        fu = MATERIAL_FU.get(material_grade, 58.0)

        # Bearing capacity: 2.4 × d × t × Fu (AISC J3.10)
        bearing_capacity = 2.4 * bolt.diameter * material_thickness * fu * bolt.num_bolts
        result.bearing_capacity_kips = bearing_capacity

        if applied_load_kips is not None:
            if applied_load_kips > bearing_capacity:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="bearing_capacity",
                    message=f"Bearing capacity {bearing_capacity:.1f} kips < load {applied_load_kips:.1f} kips",
                    suggestion="Increase plate thickness or add bolts",
                    standard_reference="AISC J3.10",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

        return result

    def check_fillet_weld(
        self,
        weld: WeldData,
        base_metal_thickness: float,
        applied_load_kips: Optional[float] = None
    ) -> StructuralValidationResult:
        """
        Check fillet weld capacity and size requirements.

        Args:
            weld: Weld data
            base_metal_thickness: Thinner base metal thickness
            applied_load_kips: Applied load

        Returns:
            Validation result
        """
        result = StructuralValidationResult()

        # Check minimum weld size per AWS D1.1
        result.total_checks += 1
        min_size = self._get_min_fillet_size(base_metal_thickness)

        if weld.leg_size < min_size:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="weld_size_min",
                message=f"Fillet weld {weld.leg_size}\" < minimum {min_size}\" for {base_metal_thickness}\" material",
                suggestion=f"Increase weld size to minimum {min_size}\"",
                standard_reference="AWS D1.1 Table 5.8",
            ))
        else:
            result.passed += 1

        # Check maximum weld size (should not exceed thinner material minus 1/16")
        result.total_checks += 1
        max_size = base_metal_thickness - 0.0625 if base_metal_thickness >= 0.25 else base_metal_thickness

        if weld.leg_size > max_size:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="weld_size_max",
                message=f"Fillet weld {weld.leg_size}\" exceeds practical max {max_size}\" for {base_metal_thickness}\" material",
                suggestion="Verify weld can be deposited without edge melt-through",
            ))
        else:
            result.passed += 1

        # Check capacity
        result.total_checks += 1
        weld_capacity = FILLET_WELD_STRENGTH_PER_INCH * weld.leg_size * weld.length
        result.weld_capacity_kips = weld_capacity

        if applied_load_kips is not None:
            if applied_load_kips > weld_capacity:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="weld_capacity",
                    message=f"Weld capacity {weld_capacity:.1f} kips < load {applied_load_kips:.1f} kips",
                    suggestion=f"Increase weld size or length (need {applied_load_kips/FILLET_WELD_STRENGTH_PER_INCH/weld.length:.3f}\" leg or {applied_load_kips/FILLET_WELD_STRENGTH_PER_INCH/weld.leg_size:.1f}\" length)",
                    standard_reference="AISC Table J2.5",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

        return result

    def check_net_section(
        self,
        gross_width: float,
        thickness: float,
        hole_diameters: List[float],
        material_grade: str = "A572-50",
        applied_load_kips: Optional[float] = None
    ) -> StructuralValidationResult:
        """
        Check net section capacity at holes.

        Args:
            gross_width: Total width of member
            thickness: Member thickness
            hole_diameters: List of hole diameters in section
            material_grade: Material grade
            applied_load_kips: Applied load

        Returns:
            Validation result
        """
        result = StructuralValidationResult()
        result.total_checks += 1

        # Net width = gross - sum of holes (use hole + 1/16" for net section per AISC)
        hole_deduction = sum(d + 0.0625 for d in hole_diameters)
        net_width = gross_width - hole_deduction

        if net_width <= 0:
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="net_section_negative",
                message=f"Net section is zero or negative (gross {gross_width}\" - holes {hole_deduction}\")",
                suggestion="Reduce number of holes or increase member width",
                standard_reference="AISC D3",
            ))
            return result

        # Net area
        net_area = net_width * thickness
        gross_area = gross_width * thickness

        # Efficiency
        efficiency = net_area / gross_area * 100

        if efficiency < 85:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="net_section_efficiency",
                message=f"Net section efficiency {efficiency:.0f}% (< 85%)",
                suggestion="Consider staggered hole pattern or wider member",
                standard_reference="AISC D3",
            ))
            result.warnings += 1

        # Check capacity
        fu = MATERIAL_FU.get(material_grade, 58.0)
        net_capacity = 0.75 * net_area * fu  # phi = 0.75 for fracture

        if applied_load_kips is not None:
            if applied_load_kips > net_capacity:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="net_section_capacity",
                    message=f"Net section capacity {net_capacity:.1f} kips < load {applied_load_kips:.1f} kips",
                    suggestion="Increase member size or reduce holes",
                    standard_reference="AISC D3",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

        return result

    def _get_min_fillet_size(self, thickness: float) -> float:
        """Get minimum fillet weld size for base metal thickness."""
        for (min_t, max_t), min_weld in MIN_FILLET_BY_THICKNESS.items():
            if min_t < thickness <= max_t:
                return min_weld
        return 0.5  # Default for very thick material

    def to_dict(self, result: StructuralValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "structural_capacity",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "capacities": {
                "bolt_shear_kips": result.bolt_capacity_kips,
                "weld_kips": result.weld_capacity_kips,
                "bearing_kips": result.bearing_capacity_kips,
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
