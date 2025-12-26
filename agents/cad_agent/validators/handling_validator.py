"""
Handling & Lifting Validator
============================
Validates lifting, rigging, and handling requirements.

Phase 25.8 - Handling & Erection
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

# Import HPC standards database
try:
    from ..adapters.standards_db_v2 import get_standards_db
    _hpc_db = get_standards_db()
except ImportError:
    _hpc_db = None
    logging.warning("HPC standards database not available")

logger = logging.getLogger("vulcan.validator.handling")


# Weight thresholds requiring lifting provisions
LIFTING_LUG_REQUIRED_LBS = 500  # Require lugs for assemblies > 500 lbs
CG_REQUIRED_LBS = 1000  # Require CG marking for assemblies > 1000 lbs
RIGGING_DIAGRAM_LBS = 2000  # Require rigging diagram > 2000 lbs

# Standard lifting lug capacities (per lug, SWL) - fallback if HPC data unavailable
LIFTING_LUG_CAPACITIES_FALLBACK = {
    # lug_thickness: capacity_lbs (approx, for standard plate lug)
    0.375: 2000,
    0.5: 4000,
    0.625: 6000,
    0.75: 9000,
    1.0: 15000,
    1.25: 25000,
    1.5: 35000,
}

# HPC-specific requirements
HPC_LIFTING_LUG_QUANTITY_RULE = {
    "min_tube_length_ft": 50.0,
    "required_quantity": 4,
    "description": "4 lifting lugs for units with 50' or 60' long tubes or greater"
}
HPC_MAX_CENTERLINE_SPACING_FT = 23.0

# Maximum shipping dimensions (typical flatbed truck)
MAX_SHIPPING = {
    "length_ft": 48,
    "width_ft": 8.5,
    "height_ft": 8.5,  # Low-boy can go higher
    "weight_lbs": 44000,  # Single trailer
}


@dataclass
class HandlingData:
    """Data for handling/lifting validation."""
    total_weight_lbs: float
    length_in: Optional[float] = None
    width_in: Optional[float] = None
    height_in: Optional[float] = None
    has_lifting_lugs: bool = False
    num_lifting_lugs: int = 0
    lug_capacity_lbs: Optional[float] = None
    lug_part_number: Optional[str] = None  # HPC part number (e.g., "W708")
    tube_length_ft: Optional[float] = None  # For HPC quantity rule check
    lug_spacing_ft: Optional[float] = None  # Centerline to centerline spacing
    cg_marked: bool = False
    cg_location: Optional[str] = None  # e.g., "12\" from left end"
    has_rigging_diagram: bool = False


@dataclass
class HandlingValidationResult:
    """Handling validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    weight_lbs: float = 0.0
    requires_lifting_lugs: bool = False
    requires_cg: bool = False
    shippable_standard: bool = True


class HandlingValidator:
    """
    Validates handling and lifting requirements.

    Checks:
    1. Lifting lugs required for heavy assemblies
    2. Lifting lug capacity adequate
    3. Center of gravity marked
    4. Rigging diagram provided
    5. Shipping dimensions within limits
    6. Tie-down points shown
    7. Shop vs field assembly scope
    8. Shimming/grouting requirements
    """

    def __init__(self):
        pass

    def validate(self, handling: HandlingData) -> HandlingValidationResult:
        """
        Validate handling requirements.

        Args:
            handling: Handling data

        Returns:
            Validation result
        """
        result = HandlingValidationResult()
        result.weight_lbs = handling.total_weight_lbs

        # Determine what's required
        result.requires_lifting_lugs = handling.total_weight_lbs > LIFTING_LUG_REQUIRED_LBS
        result.requires_cg = handling.total_weight_lbs > CG_REQUIRED_LBS

        # Run checks
        self._check_lifting_lugs(handling, result)
        self._check_lug_capacity(handling, result)
        self._check_cg_marking(handling, result)
        self._check_rigging_diagram(handling, result)
        self._check_shipping_dimensions(handling, result)

        return result

    def _check_lifting_lugs(self, handling: HandlingData, result: HandlingValidationResult):
        """Check if lifting lugs are provided when required."""
        result.total_checks += 1

        if result.requires_lifting_lugs:
            if not handling.has_lifting_lugs:
                result.critical_failures += 1
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="lifting_lugs_missing",
                    message=f"Assembly weighs {handling.total_weight_lbs:,.0f} lbs but no lifting lugs shown",
                    suggestion="Add lifting lugs sized for assembly weight",
                ))
            else:
                # Check HPC quantity rule if tube length provided
                if handling.tube_length_ft and handling.tube_length_ft >= HPC_LIFTING_LUG_QUANTITY_RULE["min_tube_length_ft"]:
                    required_qty = HPC_LIFTING_LUG_QUANTITY_RULE["required_quantity"]
                    if handling.num_lifting_lugs < required_qty:
                        result.failed += 1
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.CRITICAL,
                            check_type="hpc_lug_quantity",
                            message=f"HPC standard requires {required_qty} lifting lugs for {handling.tube_length_ft}' tubes (found {handling.num_lifting_lugs})",
                            suggestion=f"Add {required_qty - handling.num_lifting_lugs} more lifting lug(s) per HPC standards",
                        ))
                    else:
                        result.passed += 1
                elif handling.num_lifting_lugs < 2:
                    result.warnings += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="lifting_lugs_count",
                        message=f"Only {handling.num_lifting_lugs} lifting lug(s) shown - minimum 2 recommended",
                        suggestion="Add second lifting lug for balanced lift",
                    ))
                else:
                    result.passed += 1
                
                # Check HPC spacing requirement
                if handling.lug_spacing_ft and handling.lug_spacing_ft > HPC_MAX_CENTERLINE_SPACING_FT:
                    result.failed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        check_type="hpc_lug_spacing",
                        message=f"Lifting lug spacing {handling.lug_spacing_ft:.1f}' exceeds HPC maximum of {HPC_MAX_CENTERLINE_SPACING_FT}'",
                        suggestion=f"Reduce spacing to {HPC_MAX_CENTERLINE_SPACING_FT}' or less per HPC standards",
                    ))
        else:
            result.passed += 1

    def _check_lug_capacity(self, handling: HandlingData, result: HandlingValidationResult):
        """Check lifting lug capacity is adequate."""
        if not handling.has_lifting_lugs or not result.requires_lifting_lugs:
            return

        result.total_checks += 1

        # Try to get capacity from HPC standards if part number provided
        lug_capacity = handling.lug_capacity_lbs
        if handling.lug_part_number and _hpc_db:
            hpc_lug = _hpc_db.get_hpc_lifting_lug(handling.lug_part_number)
            if hpc_lug:
                # Estimate capacity based on thickness (fallback method)
                # HPC lugs are typically A36, use conservative estimate
                thickness = hpc_lug.thickness_in
                if thickness in LIFTING_LUG_CAPACITIES_FALLBACK:
                    lug_capacity = LIFTING_LUG_CAPACITIES_FALLBACK[thickness]
                    # Add note about HPC part
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="hpc_lug_identified",
                        message=f"Identified HPC standard lifting lug {handling.lug_part_number} ({hpc_lug.description})",
                        suggestion="Verify capacity meets load requirements",
                    ))

        if lug_capacity is None:
            result.warnings += 1
            suggestion = f"Add lug SWL rating (min {handling.total_weight_lbs/handling.num_lifting_lugs*2:,.0f} lbs per lug with 2:1 SF)"
            if handling.lug_part_number:
                suggestion += f" or verify HPC part {handling.lug_part_number} capacity"
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="lug_capacity_unknown",
                message="Lifting lug capacity not specified on drawing",
                suggestion=suggestion,
            ))
        else:
            # Check with 2:1 safety factor per lug
            required_per_lug = handling.total_weight_lbs / handling.num_lifting_lugs * 2

            if lug_capacity < required_per_lug:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="lug_capacity_low",
                    message=f"Lug capacity {lug_capacity:,.0f} lbs < required {required_per_lug:,.0f} lbs (2:1 SF)",
                    suggestion="Increase lug size or add more lugs",
                ))
            else:
                result.passed += 1

    def _check_cg_marking(self, handling: HandlingData, result: HandlingValidationResult):
        """Check center of gravity is marked."""
        result.total_checks += 1

        if result.requires_cg:
            if not handling.cg_marked:
                result.critical_failures += 1
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="cg_missing",
                    message=f"Assembly weighs {handling.total_weight_lbs:,.0f} lbs but CG not marked",
                    suggestion="Add center of gravity location symbol",
                ))
            elif not handling.cg_location:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="cg_dimension_missing",
                    message="CG symbol shown but location not dimensioned",
                    suggestion="Add dimension from reference point to CG",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

    def _check_rigging_diagram(self, handling: HandlingData, result: HandlingValidationResult):
        """Check if rigging diagram is provided for heavy lifts."""
        result.total_checks += 1

        if handling.total_weight_lbs > RIGGING_DIAGRAM_LBS:
            if not handling.has_rigging_diagram:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="rigging_diagram_missing",
                    message=f"Assembly weighs {handling.total_weight_lbs:,.0f} lbs - consider rigging diagram",
                    suggestion="Add rigging diagram showing sling angles and spreader beam if required",
                ))
            else:
                result.passed += 1
        else:
            result.passed += 1

    def _check_shipping_dimensions(self, handling: HandlingData, result: HandlingValidationResult):
        """Check if assembly can be shipped on standard transport."""
        result.total_checks += 1

        issues_found = []

        if handling.length_in and handling.length_in > MAX_SHIPPING["length_ft"] * 12:
            issues_found.append(f"Length {handling.length_in/12:.1f}' > max {MAX_SHIPPING['length_ft']}'")

        if handling.width_in and handling.width_in > MAX_SHIPPING["width_ft"] * 12:
            issues_found.append(f"Width {handling.width_in/12:.1f}' > max {MAX_SHIPPING['width_ft']}'")

        if handling.height_in and handling.height_in > MAX_SHIPPING["height_ft"] * 12:
            issues_found.append(f"Height {handling.height_in/12:.1f}' > max {MAX_SHIPPING['height_ft']}'")

        if handling.total_weight_lbs > MAX_SHIPPING["weight_lbs"]:
            issues_found.append(f"Weight {handling.total_weight_lbs:,.0f} lbs > max {MAX_SHIPPING['weight_lbs']:,} lbs")

        if issues_found:
            result.shippable_standard = False
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="shipping_oversize",
                message=f"Assembly exceeds standard shipping: {'; '.join(issues_found)}",
                suggestion="Consider shipping splits, permits, or escort required",
            ))
        else:
            result.passed += 1

    def check_tie_downs(
        self,
        has_tie_down_points: bool,
        weight_lbs: float
    ) -> HandlingValidationResult:
        """Check tie-down provisions for shipping."""
        result = HandlingValidationResult()
        result.total_checks += 1

        if weight_lbs > 2000 and not has_tie_down_points:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="tie_downs_not_shown",
                message="Tie-down points not shown for shipping",
                suggestion="Identify tie-down locations for transport",
            ))

        result.passed += 1
        return result

    def check_field_assembly(
        self,
        shop_vs_field_noted: bool,
        has_match_marks: bool
    ) -> HandlingValidationResult:
        """Check shop vs field assembly scope is clear."""
        result = HandlingValidationResult()
        result.total_checks += 1

        if not shop_vs_field_noted:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="assembly_scope_unclear",
                message="Shop vs field assembly scope not noted",
                suggestion="Clarify what is shop-assembled vs field-assembled",
            ))

        if not has_match_marks:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="match_marks_missing",
                message="Match marks not shown for field assembly",
                suggestion="Add match marks for components assembled in field",
            ))

        result.passed += 1
        return result

    def to_dict(self, result: HandlingValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "handling",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "weight_lbs": result.weight_lbs,
                "requires_lifting_lugs": result.requires_lifting_lugs,
                "requires_cg": result.requires_cg,
                "shippable_standard": result.shippable_standard,
            },
            "issues": [
                {
                    "severity": issue.severity.value,
                    "check_type": issue.check_type,
                    "message": issue.message,
                    "location": issue.location,
                    "suggestion": issue.suggestion,
                }
                for issue in result.issues
            ],
        }
