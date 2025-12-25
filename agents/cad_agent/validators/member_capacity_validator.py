"""
Member Capacity Validator
=========================
Validates structural member capacity and deflection limits.

Phase 25 - Drawing Checker Standards Completion
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.member_capacity")


# Common steel section properties (simplified for validation)
# Format: {section: (area_sqin, Ix_in4, Sx_in3, weight_plf)}
STEEL_SECTIONS = {
    # W-shapes (wide flange)
    "W8X31": (9.13, 110, 27.5, 31),
    "W10X33": (9.71, 171, 35.0, 33),
    "W12X40": (11.7, 310, 51.5, 40),
    "W14X48": (14.1, 485, 70.3, 48),
    "W16X57": (16.8, 758, 92.2, 57),
    "W18X76": (22.3, 1330, 146, 76),
    "W21X93": (27.3, 2070, 192, 93),
    "W24X104": (30.6, 3100, 258, 104),

    # Channels
    "C8X11.5": (3.38, 32.6, 8.14, 11.5),
    "C10X15.3": (4.49, 67.4, 13.5, 15.3),
    "C12X20.7": (6.09, 129, 21.5, 20.7),

    # Angles (single)
    "L4X4X1/4": (1.94, 3.0, 1.03, 6.6),
    "L4X4X3/8": (2.86, 4.32, 1.52, 9.8),
    "L6X6X3/8": (4.36, 15.4, 3.53, 14.9),
    "L6X6X1/2": (5.75, 19.9, 4.61, 19.6),
}

# Material yield strengths (ksi)
YIELD_STRENGTHS = {
    "A36": 36,
    "A572-50": 50,
    "A992": 50,
    "A500-B": 46,
    "A500-C": 50,
}

# Deflection limits per application (L/xxx)
DEFLECTION_LIMITS = {
    "floor_live": 360,        # L/360 for floor live load
    "floor_total": 240,       # L/240 for floor total load
    "roof_live": 240,         # L/240 for roof live load
    "roof_total": 180,        # L/180 for roof total load
    "cantilever": 180,        # L/180 for cantilevers
    "equipment": 600,         # L/600 for sensitive equipment
    "crane_runway": 600,      # L/600 for crane runways
    "industrial": 240,        # L/240 general industrial
    "walkway": 360,           # L/360 for walkways/platforms
}

# Modulus of elasticity (ksi)
E_STEEL = 29000


@dataclass
class MemberData:
    """Structural member data."""
    section: str = ""  # e.g., "W12X40"
    length_in: float = 0.0
    material: str = "A992"
    unbraced_length_in: Optional[float] = None

    # Loading
    applied_moment_kip_in: Optional[float] = None
    applied_shear_kips: Optional[float] = None
    applied_axial_kips: Optional[float] = None

    # For deflection check
    uniform_load_kip_per_in: Optional[float] = None
    application: str = "industrial"
    is_cantilever: bool = False

    location: str = ""


@dataclass
class MemberCapacityResult:
    """Member capacity validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    moment_capacity_kip_in: Optional[float] = None
    shear_capacity_kips: Optional[float] = None
    axial_capacity_kips: Optional[float] = None
    max_deflection_in: Optional[float] = None
    allowable_deflection_in: Optional[float] = None
    demand_capacity_ratio: Optional[float] = None


class MemberCapacityValidator:
    """
    Validates structural member capacity and deflection.

    Checks:
    1. Member capacity (flexure, shear, axial)
    2. Deflection limits per application
    """

    def __init__(self):
        pass

    def get_section_properties(self, section: str) -> Optional[tuple]:
        """Get section properties from database."""
        section_upper = section.upper().replace(" ", "")
        return STEEL_SECTIONS.get(section_upper)

    def validate_member_capacity(
        self,
        member: MemberData,
    ) -> MemberCapacityResult:
        """
        Validate member capacity for applied loads.

        Args:
            member: Member data

        Returns:
            Validation result
        """
        result = MemberCapacityResult()

        # Get section properties
        props = self.get_section_properties(member.section)
        if not props:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="section_lookup",
                message=f"Section {member.section} not in database",
                location=member.location,
                suggestion="Manually verify capacity or add section to database",
            ))
            return result

        area, Ix, Sx, weight = props

        # Get yield strength
        fy = YIELD_STRENGTHS.get(member.material.upper().replace("-", ""), 50)

        # Calculate capacities (simplified LRFD)
        phi_b = 0.90  # Flexure
        phi_v = 1.00  # Shear
        phi_c = 0.90  # Compression

        # Moment capacity (assuming compact section, full Fy)
        Mn = fy * Sx  # kip-in
        phi_Mn = phi_b * Mn
        result.moment_capacity_kip_in = phi_Mn

        # Shear capacity (simplified, assumes web yielding controls)
        # Approximate web area as 0.5 × total area
        Aw = area * 0.5
        Vn = 0.6 * fy * Aw
        phi_Vn = phi_v * Vn
        result.shear_capacity_kips = phi_Vn

        # Axial capacity (simplified, no buckling check)
        Pn = fy * area
        phi_Pn = phi_c * Pn
        result.axial_capacity_kips = phi_Pn

        # Check moment
        if member.applied_moment_kip_in is not None:
            result.total_checks += 1
            ratio = member.applied_moment_kip_in / phi_Mn
            result.demand_capacity_ratio = ratio

            if ratio > 1.0:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="moment_capacity",
                    message=f"Moment demand/capacity = {ratio:.2f} > 1.0 (FAILS)",
                    location=member.location,
                    suggestion=f"Increase section size. Need Sx ≥ {member.applied_moment_kip_in / (phi_b * fy):.1f} in³",
                    standard_reference="AISC 360 Chapter F",
                ))
            elif ratio > 0.9:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="moment_capacity",
                    message=f"Moment D/C = {ratio:.2f} (near limit)",
                    location=member.location,
                    standard_reference="AISC 360 Chapter F",
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="moment_capacity",
                    message=f"Moment D/C = {ratio:.2f} OK",
                    location=member.location,
                ))

        # Check shear
        if member.applied_shear_kips is not None:
            result.total_checks += 1
            ratio = member.applied_shear_kips / phi_Vn

            if ratio > 1.0:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="shear_capacity",
                    message=f"Shear demand/capacity = {ratio:.2f} > 1.0 (FAILS)",
                    location=member.location,
                    standard_reference="AISC 360 Chapter G",
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="shear_capacity",
                    message=f"Shear D/C = {ratio:.2f} OK",
                    location=member.location,
                ))

        # Check axial
        if member.applied_axial_kips is not None:
            result.total_checks += 1
            ratio = abs(member.applied_axial_kips) / phi_Pn

            if ratio > 1.0:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="axial_capacity",
                    message=f"Axial demand/capacity = {ratio:.2f} > 1.0 (FAILS)",
                    location=member.location,
                    suggestion="Note: Buckling not checked - actual capacity may be lower",
                    standard_reference="AISC 360 Chapter E",
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="axial_capacity",
                    message=f"Axial D/C = {ratio:.2f} (buckling not checked)",
                    location=member.location,
                ))

        return result

    def validate_deflection(
        self,
        member: MemberData,
    ) -> MemberCapacityResult:
        """
        Validate member deflection.

        Args:
            member: Member data

        Returns:
            Validation result
        """
        result = MemberCapacityResult()
        result.total_checks += 1

        # Get section properties
        props = self.get_section_properties(member.section)
        if not props:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="deflection_data",
                message=f"Cannot check deflection - section {member.section} not in database",
            ))
            return result

        area, Ix, Sx, weight = props

        # Get deflection limit
        application = member.application.lower().replace(" ", "_")
        if member.is_cantilever:
            limit_ratio = DEFLECTION_LIMITS.get("cantilever", 180)
        else:
            limit_ratio = DEFLECTION_LIMITS.get(application, 240)

        allowable = member.length_in / limit_ratio
        result.allowable_deflection_in = allowable

        # Calculate deflection if load provided
        if member.uniform_load_kip_per_in is not None:
            w = member.uniform_load_kip_per_in
            L = member.length_in

            if member.is_cantilever:
                # Cantilever: δ = wL⁴ / (8EI)
                delta = (w * L**4) / (8 * E_STEEL * Ix)
            else:
                # Simple span: δ = 5wL⁴ / (384EI)
                delta = (5 * w * L**4) / (384 * E_STEEL * Ix)

            result.max_deflection_in = delta

            if delta > allowable:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="deflection",
                    message=f"Deflection {delta:.3f}\" > L/{limit_ratio} = {allowable:.3f}\" (FAILS)",
                    location=member.location,
                    suggestion=f"Need Ix ≥ {Ix * (delta / allowable):.0f} in⁴",
                    standard_reference=f"Deflection limit L/{limit_ratio}",
                ))
            else:
                result.passed += 1
                actual_ratio = member.length_in / delta if delta > 0 else float('inf')
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="deflection",
                    message=f"Deflection {delta:.3f}\" = L/{actual_ratio:.0f} ≤ L/{limit_ratio} OK",
                    location=member.location,
                ))
        else:
            # No load - just report allowable
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="deflection_limit",
                message=f"Deflection limit for {application}: L/{limit_ratio} = {allowable:.3f}\"",
                location=member.location,
            ))

        return result

    def validate_member(
        self,
        member: MemberData,
    ) -> MemberCapacityResult:
        """
        Run all member validations.

        Args:
            member: Member data

        Returns:
            Combined validation result
        """
        result = MemberCapacityResult()

        # Capacity checks
        cap_result = self.validate_member_capacity(member)
        result.total_checks += cap_result.total_checks
        result.passed += cap_result.passed
        result.failed += cap_result.failed
        result.warnings += cap_result.warnings
        result.issues.extend(cap_result.issues)
        result.moment_capacity_kip_in = cap_result.moment_capacity_kip_in
        result.shear_capacity_kips = cap_result.shear_capacity_kips
        result.axial_capacity_kips = cap_result.axial_capacity_kips
        result.demand_capacity_ratio = cap_result.demand_capacity_ratio

        # Deflection check
        defl_result = self.validate_deflection(member)
        result.total_checks += defl_result.total_checks
        result.passed += defl_result.passed
        result.failed += defl_result.failed
        result.warnings += defl_result.warnings
        result.issues.extend(defl_result.issues)
        result.max_deflection_in = defl_result.max_deflection_in
        result.allowable_deflection_in = defl_result.allowable_deflection_in

        return result

    def validate_all(
        self,
        members: List[MemberData],
    ) -> MemberCapacityResult:
        """
        Validate all members.

        Args:
            members: List of member data

        Returns:
            Combined validation result
        """
        result = MemberCapacityResult()

        for member in members:
            r = self.validate_member(member)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        return result

    def to_dict(self, result: MemberCapacityResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "member_capacity",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "capacities": {
                "moment_capacity_kip_in": result.moment_capacity_kip_in,
                "shear_capacity_kips": result.shear_capacity_kips,
                "axial_capacity_kips": result.axial_capacity_kips,
                "demand_capacity_ratio": result.demand_capacity_ratio,
            },
            "deflection": {
                "max_deflection_in": result.max_deflection_in,
                "allowable_deflection_in": result.allowable_deflection_in,
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
