"""
HPC Walkway Standards Validator
================================
Validates walkways, ladders, and handrails per HPC standards.

References:
- HPC Standards Book II Vol. II - Structural, Frames, Walkways
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.hpc_walkway")

# HPC Walkway Standards
HPC_LADDER_RUNG_MATERIAL = "#6 rebar"
HPC_TOE_PLATE_SPEC = "PRL 4-1/2\" x 2\" x 1/4\" welded component"
HPC_HANDRAIL_DETAILING_METHOD = "plan-view, single line method"


@dataclass
class WalkwayData:
    """Data for walkway validation."""
    has_ladder: bool = False
    ladder_rung_material: Optional[str] = None
    has_toe_plate: bool = False
    toe_plate_spec: Optional[str] = None
    has_handrail: bool = False
    handrail_detailing_method: Optional[str] = None


@dataclass
class HPCWalkwayValidationResult:
    """HPC walkway validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)


class HPCWalkwayValidator:
    """
    Validates HPC walkway standards.

    Checks:
    1. Ladder rung material (#6 rebar)
    2. Toe-plate design (PRL 4-1/2\" x 2\" x 1/4\")
    3. Handrail detailing method (plan-view, single line)
    """

    def __init__(self):
        pass

    def validate_walkway(
        self,
        walkway: WalkwayData
    ) -> HPCWalkwayValidationResult:
        """
        Validate walkway per HPC standards.

        Args:
            walkway: Walkway data

        Returns:
            Validation result
        """
        result = HPCWalkwayValidationResult()

        # Check 1: Ladder rung material
        if walkway.has_ladder:
            result.total_checks += 1
            if walkway.ladder_rung_material:
                if walkway.ladder_rung_material.upper() != HPC_LADDER_RUNG_MATERIAL.upper():
                    result.warnings += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="ladder_rung_material",
                        message=f"Ladder rung material '{walkway.ladder_rung_material}' doesn't match HPC standard",
                        suggestion=f"Use {HPC_LADDER_RUNG_MATERIAL} per HPC standards",
                        standard_reference="HPC Standards Book II Vol. II",
                    ))
                else:
                    result.passed += 1
            else:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="ladder_rung_material_unspecified",
                    message="Ladder present but rung material not specified",
                    suggestion=f"Specify {HPC_LADDER_RUNG_MATERIAL} per HPC standards",
                ))

        # Check 2: Toe-plate design
        if walkway.has_toe_plate:
            result.total_checks += 1
            if walkway.toe_plate_spec:
                if walkway.toe_plate_spec.upper() != HPC_TOE_PLATE_SPEC.upper():
                    result.warnings += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="toe_plate_spec",
                        message=f"Toe-plate specification '{walkway.toe_plate_spec}' doesn't match HPC standard",
                        suggestion=f"Use {HPC_TOE_PLATE_SPEC} per HPC standards",
                        standard_reference="HPC Standards Book II Vol. II",
                    ))
                else:
                    result.passed += 1
            else:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="toe_plate_spec_unspecified",
                    message="Toe-plate present but specification not provided",
                    suggestion=f"Specify {HPC_TOE_PLATE_SPEC} per HPC standards",
                ))

        # Check 3: Handrail detailing method
        if walkway.has_handrail:
            result.total_checks += 1
            if walkway.handrail_detailing_method:
                if HPC_HANDRAIL_DETAILING_METHOD.lower() not in walkway.handrail_detailing_method.lower():
                    result.warnings += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="handrail_detailing_method",
                        message=f"Handrail detailing method may not match HPC standard",
                        suggestion=f"Use {HPC_HANDRAIL_DETAILING_METHOD} per HPC standards",
                        standard_reference="HPC Standards Book II Vol. II",
                    ))
                else:
                    result.passed += 1
            else:
                result.passed += 1  # Method not specified is acceptable

        return result

    def to_dict(self, result: HPCWalkwayValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "hpc_walkway",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "check_type": issue.check_type,
                    "message": issue.message,
                    "location": issue.location,
                    "suggestion": issue.suggestion,
                    "standard_reference": getattr(issue, "standard_reference", None),
                }
                for issue in result.issues
            ],
        }

