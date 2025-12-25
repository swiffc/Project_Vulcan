"""
Sheet Metal Validator
=====================
Validates sheet metal: bend allowance, grain direction, springback.

Phase 25 - Drawing Checker Standards Completion
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.sheet_metal")


# K-factors for bend allowance calculation
# K = distance of neutral axis from inside of bend / material thickness
K_FACTORS = {
    "air_bend": 0.33,      # Air bending (most common)
    "bottom_bend": 0.42,   # Bottoming
    "coining": 0.50,       # Coining (neutral axis at center)
    "soft_material": 0.35, # Soft materials (aluminum, copper)
    "hard_material": 0.45, # Hard materials (stainless, spring steel)
}

# Minimum bend radius as multiple of thickness
MIN_BEND_RADIUS_FACTOR = {
    "mild_steel": 1.0,
    "aluminum_3003": 0.0,   # Can bend flat
    "aluminum_5052": 1.0,
    "aluminum_6061": 1.5,
    "stainless_304": 1.5,
    "stainless_316": 1.5,
    "copper": 0.0,
    "brass": 0.5,
    "spring_steel": 3.0,
}

# Springback angles (approximate degrees to overbend)
SPRINGBACK_COMPENSATION = {
    "mild_steel": 2.0,      # 2° overbend
    "aluminum": 3.0,        # 3° overbend
    "stainless": 4.0,       # 4° overbend
    "spring_steel": 8.0,    # 8° overbend
}

# Grain direction impact on bend quality
GRAIN_DIRECTION_NOTES = {
    "parallel": "Bending parallel to grain may cause cracking - use caution",
    "perpendicular": "Perpendicular to grain is preferred for bending",
    "diagonal": "45° to grain provides good bendability",
}


@dataclass
class BendData:
    """Bend specification data."""
    material_thickness_in: float = 0.0
    inside_bend_radius_in: float = 0.0
    bend_angle_deg: float = 90.0
    bend_length_in: float = 0.0
    material_type: str = "mild_steel"
    bend_method: str = "air_bend"
    grain_direction: str = "perpendicular"  # relative to bend line
    location: str = ""


@dataclass
class SheetMetalValidationResult:
    """Sheet metal validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    bend_allowance_in: Optional[float] = None
    bend_deduction_in: Optional[float] = None
    min_bend_radius_in: Optional[float] = None
    springback_deg: Optional[float] = None
    k_factor: Optional[float] = None


class SheetMetalValidator:
    """
    Validates sheet metal fabrication requirements.

    Checks:
    1. Bend allowance and K-factor
    2. Grain direction relative to bend
    3. Springback compensation
    4. Minimum bend radius
    """

    def __init__(self):
        pass

    def calculate_bend_allowance(
        self,
        thickness: float,
        bend_radius: float,
        bend_angle_deg: float,
        k_factor: float,
    ) -> float:
        """
        Calculate bend allowance using standard formula.

        BA = π × (R + K × T) × (A / 180)

        Args:
            thickness: Material thickness
            bend_radius: Inside bend radius
            bend_angle_deg: Bend angle in degrees
            k_factor: K-factor for neutral axis

        Returns:
            Bend allowance in same units as inputs
        """
        return math.pi * (bend_radius + k_factor * thickness) * (bend_angle_deg / 180.0)

    def calculate_bend_deduction(
        self,
        thickness: float,
        bend_radius: float,
        bend_angle_deg: float,
        k_factor: float,
    ) -> float:
        """
        Calculate bend deduction (setback - bend allowance).

        Args:
            thickness: Material thickness
            bend_radius: Inside bend radius
            bend_angle_deg: Bend angle in degrees
            k_factor: K-factor for neutral axis

        Returns:
            Bend deduction
        """
        # Outside setback
        half_angle = bend_angle_deg / 2.0
        ossb = (bend_radius + thickness) * math.tan(math.radians(half_angle))

        # Bend allowance
        ba = self.calculate_bend_allowance(thickness, bend_radius, bend_angle_deg, k_factor)

        # Bend deduction = 2 × OSSB - BA
        return 2 * ossb - ba

    def validate_bend_radius(
        self,
        bend: BendData,
    ) -> SheetMetalValidationResult:
        """
        Validate minimum bend radius.

        Args:
            bend: Bend specification data

        Returns:
            Validation result
        """
        result = SheetMetalValidationResult()
        result.total_checks += 1

        material = bend.material_type.lower().replace(" ", "_")
        factor = MIN_BEND_RADIUS_FACTOR.get(material, 1.0)
        min_radius = factor * bend.material_thickness_in
        result.min_bend_radius_in = min_radius

        if bend.inside_bend_radius_in < min_radius:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="bend_radius",
                message=f"Bend radius {bend.inside_bend_radius_in}\" < min {min_radius}\" for {bend.material_type}",
                location=bend.location,
                suggestion=f"Increase bend radius to ≥{min_radius}\" ({factor}× thickness)",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="bend_radius",
                message=f"Bend radius {bend.inside_bend_radius_in}\" ≥ min {min_radius}\" OK",
                location=bend.location,
            ))

        return result

    def validate_bend_allowance(
        self,
        bend: BendData,
    ) -> SheetMetalValidationResult:
        """
        Calculate and validate bend allowance.

        Args:
            bend: Bend specification data

        Returns:
            Validation result with calculations
        """
        result = SheetMetalValidationResult()
        result.total_checks += 1

        # Determine K-factor
        method = bend.bend_method.lower().replace(" ", "_")
        k_factor = K_FACTORS.get(method, 0.33)

        # Adjust for material
        if "aluminum" in bend.material_type.lower():
            k_factor = K_FACTORS.get("soft_material", 0.35)
        elif "stainless" in bend.material_type.lower() or "spring" in bend.material_type.lower():
            k_factor = K_FACTORS.get("hard_material", 0.45)

        result.k_factor = k_factor

        # Calculate bend allowance
        ba = self.calculate_bend_allowance(
            bend.material_thickness_in,
            bend.inside_bend_radius_in,
            bend.bend_angle_deg,
            k_factor,
        )
        result.bend_allowance_in = ba

        # Calculate bend deduction
        bd = self.calculate_bend_deduction(
            bend.material_thickness_in,
            bend.inside_bend_radius_in,
            bend.bend_angle_deg,
            k_factor,
        )
        result.bend_deduction_in = bd

        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="bend_allowance",
            message=f"Bend allowance = {ba:.4f}\", K-factor = {k_factor}",
            location=bend.location,
            suggestion=f"Bend deduction = {bd:.4f}\"",
        ))

        return result

    def validate_grain_direction(
        self,
        bend: BendData,
    ) -> SheetMetalValidationResult:
        """
        Validate grain direction relative to bend.

        Args:
            bend: Bend specification data

        Returns:
            Validation result
        """
        result = SheetMetalValidationResult()
        result.total_checks += 1

        direction = bend.grain_direction.lower()

        if direction == "parallel":
            # Bending parallel to grain is problematic
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="grain_direction",
                message="Bend line parallel to grain direction",
                location=bend.location,
                suggestion=GRAIN_DIRECTION_NOTES["parallel"],
            ))

            # Especially bad for tight radii
            if bend.inside_bend_radius_in < bend.material_thickness_in:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="grain_direction_tight",
                    message="Tight bend parallel to grain will likely crack",
                    location=bend.location,
                    suggestion="Rotate part 90° or increase bend radius",
                ))
        elif direction == "perpendicular":
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="grain_direction",
                message="Bend perpendicular to grain (preferred)",
                location=bend.location,
            ))
        else:  # diagonal or unknown
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="grain_direction",
                message=f"Grain direction: {direction}",
                location=bend.location,
            ))

        return result

    def validate_springback(
        self,
        bend: BendData,
    ) -> SheetMetalValidationResult:
        """
        Calculate springback compensation.

        Args:
            bend: Bend specification data

        Returns:
            Validation result with springback info
        """
        result = SheetMetalValidationResult()
        result.total_checks += 1

        # Determine springback based on material
        material = bend.material_type.lower()
        if "aluminum" in material:
            springback = SPRINGBACK_COMPENSATION["aluminum"]
        elif "stainless" in material:
            springback = SPRINGBACK_COMPENSATION["stainless"]
        elif "spring" in material:
            springback = SPRINGBACK_COMPENSATION["spring_steel"]
        else:
            springback = SPRINGBACK_COMPENSATION["mild_steel"]

        # Springback increases with R/t ratio
        if bend.material_thickness_in > 0:
            rt_ratio = bend.inside_bend_radius_in / bend.material_thickness_in
            if rt_ratio > 3:
                springback *= 1.5  # More springback for larger radii
            elif rt_ratio < 1:
                springback *= 0.7  # Less springback for tight bends

        result.springback_deg = springback

        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="springback",
            message=f"Estimated springback: {springback:.1f}°",
            location=bend.location,
            suggestion=f"Overbend to {bend.bend_angle_deg + springback:.1f}° for {bend.bend_angle_deg}° final angle",
        ))

        # Warn about high springback materials
        if springback > 5:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="springback_high",
                message=f"High springback material ({springback:.1f}°)",
                suggestion="Consider trial bends to verify compensation",
            ))

        return result

    def validate_bend(
        self,
        bend: BendData,
    ) -> SheetMetalValidationResult:
        """
        Run all bend validations.

        Args:
            bend: Bend specification data

        Returns:
            Combined validation result
        """
        result = SheetMetalValidationResult()

        # Run all checks
        for check_result in [
            self.validate_bend_radius(bend),
            self.validate_bend_allowance(bend),
            self.validate_grain_direction(bend),
            self.validate_springback(bend),
        ]:
            result.total_checks += check_result.total_checks
            result.passed += check_result.passed
            result.failed += check_result.failed
            result.warnings += check_result.warnings
            result.issues.extend(check_result.issues)

            # Capture calculated values
            if check_result.bend_allowance_in:
                result.bend_allowance_in = check_result.bend_allowance_in
            if check_result.bend_deduction_in:
                result.bend_deduction_in = check_result.bend_deduction_in
            if check_result.min_bend_radius_in:
                result.min_bend_radius_in = check_result.min_bend_radius_in
            if check_result.springback_deg:
                result.springback_deg = check_result.springback_deg
            if check_result.k_factor:
                result.k_factor = check_result.k_factor

        return result

    def validate_all(
        self,
        bends: List[BendData],
    ) -> SheetMetalValidationResult:
        """
        Validate all bends.

        Args:
            bends: List of bend specifications

        Returns:
            Combined validation result
        """
        result = SheetMetalValidationResult()

        for bend in bends:
            r = self.validate_bend(bend)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        return result

    def to_dict(self, result: SheetMetalValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "sheet_metal",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "calculations": {
                "bend_allowance_in": result.bend_allowance_in,
                "bend_deduction_in": result.bend_deduction_in,
                "min_bend_radius_in": result.min_bend_radius_in,
                "springback_deg": result.springback_deg,
                "k_factor": result.k_factor,
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
