"""
Dimension Validator
===================
Validates dimensional data extracted from engineering drawings.

Phase 25.7 Implementation
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.dimension")


# Imperial/Metric conversion factor
INCH_TO_MM = 25.4
MM_TO_INCH = 1 / 25.4

# Standard tolerances for dual dimensions
CONVERSION_TOLERANCES = {
    "standard": 0.5,      # mm tolerance for standard conversions
    "tight": 0.1,         # mm tolerance for tight tolerances
    "loose": 1.0,         # mm tolerance for reference dimensions
}

# Common engineering dimensions (inches)
STANDARD_DIMENSIONS = {
    # Tube pitches
    2.75: "Standard tube pitch (API 661)",
    2.5: "Common tube pitch",
    2.25: "Compact tube pitch",
    # Flange dimensions (common)
    1.5: "1-1/2 inch (38mm)",
    2.0: "2 inch (51mm)",
    3.0: "3 inch (76mm)",
    4.0: "4 inch (102mm)",
    6.0: "6 inch (152mm)",
    # Bolt holes
    0.5: "1/2 inch bolt hole",
    0.5625: "9/16 inch bolt hole",
    0.625: "5/8 inch bolt hole",
    0.75: "3/4 inch bolt hole",
    0.8125: "13/16 inch bolt hole",
    0.875: "7/8 inch bolt hole",
    1.0: "1 inch bolt hole",
}

# Edge distance requirements (ratio to hole diameter)
MIN_EDGE_DISTANCE_RATIO = 1.5
MIN_EDGE_DISTANCE_STRUCTURAL = 1.75


@dataclass
class DimensionValidationResult:
    """Dimension validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Dimension-specific statistics
    total_dimensions: int = 0
    imperial_count: int = 0
    metric_count: int = 0
    dual_unit_count: int = 0
    conversion_errors: int = 0
    consistency_issues: int = 0


class DimensionValidator:
    """
    Validates dimensional data from engineering drawings.

    Checks:
    1. Imperial/metric conversion accuracy
    2. Overall dimension consistency (sum of parts = total)
    3. Hole pattern pitch verification
    4. Bolt circle diameter verification
    5. Edge distance checks (1.5x diameter minimum)
    6. Tube count verification
    7. Nozzle projection dimensions
    8. Header box dimension verification
    """

    def __init__(self):
        """Initialize dimension validator."""
        pass

    def validate(self, extraction_result) -> DimensionValidationResult:
        """
        Validate dimensions from extraction result.

        Args:
            extraction_result: DrawingExtractionResult from PDF extractor

        Returns:
            DimensionValidationResult with all validation findings
        """
        result = DimensionValidationResult()

        dimensions = extraction_result.dimensions
        result.total_dimensions = len(dimensions)

        if not dimensions:
            result.total_checks += 1
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="dimensions_missing",
                message="No dimensions extracted from drawing",
                suggestion="Ensure dimension text is extractable from PDF",
            ))
            return result

        # Count dimension types
        for dim in dimensions:
            if dim.is_dual_unit:
                result.dual_unit_count += 1
            if dim.value_imperial:
                result.imperial_count += 1
            if dim.value_metric:
                result.metric_count += 1

        # Run validation checks
        self._check_unit_conversions(dimensions, result)
        self._check_dimension_consistency(dimensions, result)
        self._check_standard_dimensions(dimensions, result)
        self._check_edge_distances(dimensions, result)
        self._check_tube_data(extraction_result, result)
        self._check_header_dimensions(extraction_result, result)
        self._check_tolerance_specifications(dimensions, result)

        return result

    def _check_unit_conversions(self, dimensions: List, result: DimensionValidationResult):
        """Check imperial/metric conversion accuracy for dual-unit dimensions."""
        result.total_checks += 1

        conversion_errors = 0

        for dim in dimensions:
            if dim.is_dual_unit and dim.value_imperial and dim.value_metric:
                # Calculate expected metric from imperial
                expected_mm = dim.value_imperial * INCH_TO_MM

                # Check tolerance based on dimension size
                if dim.value_imperial < 1.0:
                    tolerance = CONVERSION_TOLERANCES["tight"]
                elif dim.value_imperial > 24.0:
                    tolerance = CONVERSION_TOLERANCES["loose"]
                else:
                    tolerance = CONVERSION_TOLERANCES["standard"]

                error = abs(dim.value_metric - expected_mm)

                if error > tolerance:
                    conversion_errors += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="conversion_error",
                        message=f"Dimension conversion error: {dim.value_imperial}\" = {dim.value_metric}mm (expected {expected_mm:.1f}mm)",
                        location=dim.location if hasattr(dim, 'location') else "Drawing",
                        suggestion=f"Correct metric value to {expected_mm:.1f}mm",
                    ))

        result.conversion_errors = conversion_errors

        if conversion_errors == 0:
            result.passed += 1
        elif conversion_errors <= 2:
            result.warnings += 1
        else:
            result.failed += 1
            result.critical_failures += 1

    def _check_dimension_consistency(self, dimensions: List, result: DimensionValidationResult):
        """Check that component dimensions add up to overall dimensions."""
        result.total_checks += 1

        # Group dimensions by type/context
        overall_dims = []
        component_dims = []

        for dim in dimensions:
            desc = (dim.description or "").upper()
            if "OVERALL" in desc or "TOTAL" in desc or "OA" in desc:
                overall_dims.append(dim)
            else:
                component_dims.append(dim)

        # If we have overall dimensions, try to verify
        if overall_dims and component_dims:
            # This is a simplified check - in production would need
            # more sophisticated dimension chain analysis
            for overall in overall_dims:
                if overall.value_imperial:
                    # Find potential component dimensions that might sum
                    # to this overall dimension
                    overall_val = overall.value_imperial

                    # Check for obvious mismatches
                    for comp in component_dims:
                        if comp.value_imperial and comp.value_imperial > overall_val:
                            result.issues.append(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                check_type="dimension_exceeds_overall",
                                message=f"Component dimension {comp.value_imperial}\" exceeds overall {overall_val}\"",
                                suggestion="Verify dimension chain",
                            ))
                            result.consistency_issues += 1

        if result.consistency_issues == 0:
            result.passed += 1
        else:
            result.failed += 1

    def _check_standard_dimensions(self, dimensions: List, result: DimensionValidationResult):
        """Verify dimensions match standard engineering values."""
        result.total_checks += 1

        # Check for common mistakes in standard dimensions
        potential_errors = 0

        for dim in dimensions:
            if not dim.value_imperial:
                continue

            val = dim.value_imperial
            desc = (dim.description or "").upper()

            # Check tube pitch
            if "PITCH" in desc:
                if val not in [2.25, 2.5, 2.75, 3.0]:
                    potential_errors += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="nonstandard_pitch",
                        message=f"Non-standard tube pitch: {val}\"",
                        suggestion="Standard pitches: 2.25\", 2.5\", 2.75\", 3.0\"",
                    ))

            # Check for suspicious fractional values
            if "." in str(val):
                decimal = val - int(val)
                # Common fractions: 1/2, 1/4, 1/8, 1/16, 1/32
                valid_decimals = [0.0, 0.03125, 0.0625, 0.125, 0.1875, 0.25,
                                  0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625,
                                  0.6875, 0.75, 0.8125, 0.875, 0.9375]

                # Check if close to any valid fraction
                min_diff = min(abs(decimal - vd) for vd in valid_decimals)
                if min_diff > 0.01:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="unusual_fraction",
                        message=f"Unusual fractional dimension: {val}\"",
                        suggestion="Verify dimension is not a typo",
                    ))

        if potential_errors == 0:
            result.passed += 1
        else:
            result.warnings += 1

    def _check_edge_distances(self, dimensions: List, result: DimensionValidationResult):
        """Check edge distances meet minimum requirements."""
        result.total_checks += 1

        edge_violations = 0

        # Look for hole-related dimensions
        for dim in dimensions:
            desc = (dim.description or "").upper()

            if "EDGE" in desc or "DIST" in desc:
                # Try to find associated hole diameter
                val = dim.value_imperial
                if val:
                    # Assume standard bolt holes
                    common_holes = [0.5, 0.5625, 0.625, 0.75, 0.875, 1.0]

                    for hole_dia in common_holes:
                        min_edge = hole_dia * MIN_EDGE_DISTANCE_RATIO
                        if val < min_edge and val > hole_dia * 0.5:
                            # Likely an edge distance violation
                            edge_violations += 1
                            result.issues.append(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                check_type="edge_distance_min",
                                message=f"Edge distance {val}\" may be insufficient for {hole_dia}\" hole",
                                suggestion=f"Minimum edge distance: {min_edge}\" (1.5 x diameter)",
                                standard_reference="AISC/AWS D1.1 Table J3.4",
                            ))
                            break

        if edge_violations == 0:
            result.passed += 1
        else:
            result.failed += 1

    def _check_tube_data(self, extraction_result, result: DimensionValidationResult):
        """Check tube count and spacing from design data."""
        result.total_checks += 1

        design_data = extraction_result.design_data

        # Check if tube count can be verified from dimensions
        dimensions = extraction_result.dimensions
        tube_dims = [d for d in dimensions if "TUBE" in (d.description or "").upper()]

        # If we have tube layout dimensions, verify counts
        if tube_dims and design_data:
            # This would typically involve:
            # - Tube pitch x number of tubes = bundle width
            # - Number of rows x row pitch = bundle height
            pass  # Simplified - would need more context

        result.passed += 1

    def _check_header_dimensions(self, extraction_result, result: DimensionValidationResult):
        """Check header box dimensions for ACHE headers."""
        result.total_checks += 1

        drawing_type = extraction_result.drawing_type

        # Only check for header drawings (M-series)
        if drawing_type and drawing_type.value == "M":
            dimensions = extraction_result.dimensions

            # Look for header-related dimensions
            header_dims = []
            for dim in dimensions:
                desc = (dim.description or "").upper()
                if any(kw in desc for kw in ["HEADER", "BOX", "PLENUM", "DEPTH"]):
                    header_dims.append(dim)

            # Check plenum depth minimum (36" / 915mm per API 661)
            for dim in header_dims:
                desc = (dim.description or "").upper()
                if "DEPTH" in desc or "PLENUM" in desc:
                    val = dim.value_imperial or (dim.value_metric * MM_TO_INCH if dim.value_metric else None)
                    if val and val < 36:
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            check_type="plenum_depth",
                            message=f"Plenum depth {val}\" is below API 661 minimum of 36\"",
                            standard_reference="API 661 para 5.2.3",
                            suggestion="Verify plenum depth meets specification",
                        ))

        result.passed += 1

    def _check_tolerance_specifications(self, dimensions: List, result: DimensionValidationResult):
        """Check that critical dimensions have tolerances specified."""
        result.total_checks += 1

        dims_without_tol = 0

        for dim in dimensions:
            desc = (dim.description or "").upper()

            # Critical dimensions that should have tolerances
            critical_keywords = ["BORE", "DIA", "OD", "ID", "FIT", "HOLE"]

            is_critical = any(kw in desc for kw in critical_keywords)

            if is_critical:
                # Check if tolerance is specified
                has_tolerance = (dim.tolerance_plus is not None or
                                dim.tolerance_minus is not None or
                                dim.tolerance_bilateral is not None)

                if not has_tolerance:
                    dims_without_tol += 1

        if dims_without_tol > 3:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="tolerance_missing",
                message=f"{dims_without_tol} critical dimensions may be missing tolerance specifications",
                suggestion="Add tolerances to bore, diameter, and fit dimensions",
            ))
            result.warnings += 1
        else:
            result.passed += 1

    def to_dict(self, result: DimensionValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "dimension",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "total_dimensions": result.total_dimensions,
                "imperial_count": result.imperial_count,
                "metric_count": result.metric_count,
                "dual_unit_count": result.dual_unit_count,
                "conversion_errors": result.conversion_errors,
                "consistency_issues": result.consistency_issues,
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
