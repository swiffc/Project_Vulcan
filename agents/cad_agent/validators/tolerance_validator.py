"""
Tolerance Validator
===================
Validates GD&T tolerances: flatness, squareness, parallelism.

Phase 25 - Drawing Checker Standards Completion
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.tolerance")


# Standard flatness tolerances per surface size (inches per inch)
# Based on ASME Y14.5 and industry practice
FLATNESS_TOLERANCES = {
    "precision": 0.001,    # Precision machined surfaces
    "standard": 0.005,     # Standard machined surfaces
    "commercial": 0.015,   # Commercial grade
    "rough": 0.030,        # As-cut/as-welded
}

# Flatness per foot for large surfaces
FLATNESS_PER_FOOT = {
    "precision": 0.002,
    "standard": 0.010,
    "commercial": 0.030,
    "rough": 0.060,
}

# Squareness (perpendicularity) tolerances per length
SQUARENESS_TOLERANCES = {
    "precision": 0.001,    # Per inch of length
    "standard": 0.003,
    "commercial": 0.005,
    "rough": 0.010,
}

# Parallelism tolerances per length
PARALLELISM_TOLERANCES = {
    "precision": 0.001,
    "standard": 0.003,
    "commercial": 0.005,
    "rough": 0.010,
}

# Standard surface grades
SURFACE_GRADES = ["precision", "standard", "commercial", "rough"]


@dataclass
class FlatnessData:
    """Flatness specification data."""
    surface_length_in: float = 0.0
    surface_width_in: float = 0.0
    specified_tolerance_in: Optional[float] = None
    surface_grade: str = "standard"
    is_datum: bool = False
    location: str = ""


@dataclass
class SquarenessData:
    """Squareness (perpendicularity) data."""
    feature_length_in: float = 0.0
    specified_tolerance_in: Optional[float] = None
    surface_grade: str = "standard"
    datum_reference: str = ""
    location: str = ""


@dataclass
class ParallelismData:
    """Parallelism data."""
    feature_length_in: float = 0.0
    separation_distance_in: float = 0.0
    specified_tolerance_in: Optional[float] = None
    surface_grade: str = "standard"
    datum_reference: str = ""
    location: str = ""


@dataclass
class ToleranceValidationResult:
    """Tolerance validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    recommended_flatness: Optional[float] = None
    recommended_squareness: Optional[float] = None
    recommended_parallelism: Optional[float] = None


class ToleranceValidator:
    """
    Validates GD&T form and orientation tolerances.

    Checks:
    1. Flatness per surface size and grade
    2. Squareness (perpendicularity) per length
    3. Parallelism per length and separation
    """

    def __init__(self):
        pass

    def validate_flatness(
        self,
        flatness: FlatnessData,
    ) -> ToleranceValidationResult:
        """
        Validate flatness tolerance.

        Args:
            flatness: Flatness specification data

        Returns:
            Validation result
        """
        result = ToleranceValidationResult()
        result.total_checks += 1

        grade = flatness.surface_grade.lower()
        if grade not in SURFACE_GRADES:
            grade = "standard"

        # Calculate recommended flatness based on surface size
        diagonal = math.sqrt(flatness.surface_length_in**2 + flatness.surface_width_in**2)
        feet = diagonal / 12.0

        # Use per-foot tolerance for larger surfaces
        if feet > 1.0:
            recommended = FLATNESS_PER_FOOT[grade] * feet
        else:
            recommended = FLATNESS_TOLERANCES[grade]

        result.recommended_flatness = recommended

        if flatness.specified_tolerance_in is not None:
            if flatness.specified_tolerance_in < recommended * 0.5:
                # Tolerance is very tight
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="flatness_tight",
                    message=f"Flatness {flatness.specified_tolerance_in}\" is very tight for {grade} grade",
                    location=flatness.location,
                    suggestion=f"Typical tolerance for this surface: {recommended:.4f}\"",
                    standard_reference="ASME Y14.5",
                ))
            elif flatness.specified_tolerance_in > recommended * 3.0:
                # Tolerance is very loose
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="flatness_loose",
                    message=f"Flatness {flatness.specified_tolerance_in}\" is generous (typical: {recommended:.4f}\")",
                    location=flatness.location,
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="flatness",
                    message=f"Flatness {flatness.specified_tolerance_in}\" appropriate for {grade} grade",
                    location=flatness.location,
                    standard_reference="ASME Y14.5",
                ))

            # Datum surfaces need tighter control
            if flatness.is_datum and flatness.specified_tolerance_in > recommended:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="flatness_datum",
                    message="Datum surface flatness may need tighter control",
                    location=flatness.location,
                    suggestion=f"Consider flatness ≤{recommended:.4f}\" for datum",
                ))
        else:
            # No tolerance specified - provide recommendation
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="flatness_recommend",
                message=f"Recommended flatness for {grade} grade: {recommended:.4f}\"",
                location=flatness.location,
                standard_reference="ASME Y14.5",
            ))

        return result

    def validate_squareness(
        self,
        squareness: SquarenessData,
    ) -> ToleranceValidationResult:
        """
        Validate squareness (perpendicularity) tolerance.

        Args:
            squareness: Squareness specification data

        Returns:
            Validation result
        """
        result = ToleranceValidationResult()
        result.total_checks += 1

        grade = squareness.surface_grade.lower()
        if grade not in SURFACE_GRADES:
            grade = "standard"

        # Calculate recommended squareness based on length
        tol_per_inch = SQUARENESS_TOLERANCES[grade]
        recommended = tol_per_inch * squareness.feature_length_in

        # Minimum practical tolerance
        recommended = max(recommended, 0.005)

        result.recommended_squareness = recommended

        if squareness.specified_tolerance_in is not None:
            if squareness.specified_tolerance_in < recommended * 0.5:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="squareness_tight",
                    message=f"Squareness {squareness.specified_tolerance_in}\" very tight for {squareness.feature_length_in}\" length",
                    location=squareness.location,
                    suggestion=f"Typical: {recommended:.4f}\" for {grade} grade",
                    standard_reference="ASME Y14.5",
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="squareness",
                    message=f"Squareness {squareness.specified_tolerance_in}\" to datum {squareness.datum_reference}",
                    location=squareness.location,
                    standard_reference="ASME Y14.5",
                ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="squareness_recommend",
                message=f"Recommended squareness for {squareness.feature_length_in}\" length: {recommended:.4f}\"",
                location=squareness.location,
            ))

        return result

    def validate_parallelism(
        self,
        parallelism: ParallelismData,
    ) -> ToleranceValidationResult:
        """
        Validate parallelism tolerance.

        Args:
            parallelism: Parallelism specification data

        Returns:
            Validation result
        """
        result = ToleranceValidationResult()
        result.total_checks += 1

        grade = parallelism.surface_grade.lower()
        if grade not in SURFACE_GRADES:
            grade = "standard"

        # Calculate recommended parallelism based on length
        tol_per_inch = PARALLELISM_TOLERANCES[grade]
        recommended = tol_per_inch * parallelism.feature_length_in

        # Minimum practical tolerance
        recommended = max(recommended, 0.005)

        result.recommended_parallelism = recommended

        if parallelism.specified_tolerance_in is not None:
            if parallelism.specified_tolerance_in < recommended * 0.5:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="parallelism_tight",
                    message=f"Parallelism {parallelism.specified_tolerance_in}\" very tight for {parallelism.feature_length_in}\" length",
                    location=parallelism.location,
                    suggestion=f"Typical: {recommended:.4f}\" for {grade} grade",
                    standard_reference="ASME Y14.5",
                ))
            else:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="parallelism",
                    message=f"Parallelism {parallelism.specified_tolerance_in}\" to datum {parallelism.datum_reference}",
                    location=parallelism.location,
                    standard_reference="ASME Y14.5",
                ))

            # Check if separation distance affects achievability
            if parallelism.separation_distance_in > 0:
                angle_error = parallelism.specified_tolerance_in / parallelism.separation_distance_in
                if angle_error < 0.0001:  # Very tight angular relationship
                    result.warnings += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="parallelism_angle",
                        message="Parallelism implies very tight angular control",
                        suggestion="Verify measurement capability exists",
                    ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="parallelism_recommend",
                message=f"Recommended parallelism for {parallelism.feature_length_in}\" length: {recommended:.4f}\"",
                location=parallelism.location,
            ))

        return result

    def validate_all(
        self,
        flatness_specs: List[FlatnessData] = None,
        squareness_specs: List[SquarenessData] = None,
        parallelism_specs: List[ParallelismData] = None,
    ) -> ToleranceValidationResult:
        """
        Run all tolerance validations.

        Args:
            flatness_specs: List of flatness specifications
            squareness_specs: List of squareness specifications
            parallelism_specs: List of parallelism specifications

        Returns:
            Combined validation result
        """
        result = ToleranceValidationResult()

        for spec in (flatness_specs or []):
            r = self.validate_flatness(spec)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        for spec in (squareness_specs or []):
            r = self.validate_squareness(spec)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        for spec in (parallelism_specs or []):
            r = self.validate_parallelism(spec)
            result.total_checks += r.total_checks
            result.passed += r.passed
            result.failed += r.failed
            result.warnings += r.warnings
            result.issues.extend(r.issues)

        return result

    def to_dict(self, result: ToleranceValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "tolerance",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "recommendations": {
                "flatness_in": result.recommended_flatness,
                "squareness_in": result.recommended_squareness,
                "parallelism_in": result.recommended_parallelism,
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
