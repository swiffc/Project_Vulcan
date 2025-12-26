"""
HPC Header Design Standards Validator
======================================
Validates header design per HPC standards.

References:
- HPC Standards Book III - Header Design
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.hpc_header")

# HPC Header Standards
HPC_NAMEPLATE_THICKNESS_CURRENT_IN = 0.105
HPC_NAMEPLATE_THICKNESS_PREVIOUS_IN = 0.125
HPC_NAMEPLATE_THICKNESS_TOLERANCE_IN = 0.005


@dataclass
class HeaderData:
    """Data for header validation."""
    nameplate_thickness_in: Optional[float] = None
    has_plug: bool = False
    plug_part_number: Optional[str] = None  # e.g., "P430"
    has_weld_joint_prep: bool = False
    has_weld_procedure_spec: bool = False


@dataclass
class HPCHeaderValidationResult:
    """HPC header validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)


class HPCHeaderValidator:
    """
    Validates HPC header design standards.

    Checks:
    1. Nameplate thickness (0.105\" current standard, reduced from 0.125\")
    2. Plug specifications
    3. Welding requirements
    """

    def __init__(self):
        pass

    def validate_header(
        self,
        header: HeaderData
    ) -> HPCHeaderValidationResult:
        """
        Validate header per HPC standards.

        Args:
            header: Header data

        Returns:
            Validation result
        """
        result = HPCHeaderValidationResult()

        # Check 1: Nameplate thickness
        if header.nameplate_thickness_in is not None:
            result.total_checks += 1
            thickness = header.nameplate_thickness_in
            
            # Check if matches current standard (0.105")
            if abs(thickness - HPC_NAMEPLATE_THICKNESS_CURRENT_IN) <= HPC_NAMEPLATE_THICKNESS_TOLERANCE_IN:
                result.passed += 1
            # Check if matches old standard (0.125")
            elif abs(thickness - HPC_NAMEPLATE_THICKNESS_PREVIOUS_IN) <= HPC_NAMEPLATE_THICKNESS_TOLERANCE_IN:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="nameplate_thickness_old_standard",
                    message=f"Nameplate thickness {thickness}\" matches old HPC standard (0.125\")",
                    suggestion=f"Consider updating to current HPC standard {HPC_NAMEPLATE_THICKNESS_CURRENT_IN}\" for cost reduction (ASME compliant)",
                    standard_reference="HPC Standards Book III",
                ))
            else:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="nameplate_thickness_non_standard",
                    message=f"Nameplate thickness {thickness}\" doesn't match HPC standard ({HPC_NAMEPLATE_THICKNESS_CURRENT_IN}\")",
                    suggestion=f"Verify thickness - HPC standard is {HPC_NAMEPLATE_THICKNESS_CURRENT_IN}\" (reduced from 0.125\" for cost)",
                    standard_reference="HPC Standards Book III",
                ))

        # Check 2: Plug specifications
        if header.has_plug:
            result.total_checks += 1
            if header.plug_part_number:
                # HPC standard plugs include P430 and others
                if header.plug_part_number.upper().startswith("P"):
                    result.passed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="plug_identified",
                        message=f"Plug part number {header.plug_part_number} identified",
                        suggestion="Verify plug specification matches HPC standard",
                        standard_reference="HPC Standards Book III",
                    ))
                else:
                    result.warnings += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        check_type="plug_part_number_format",
                        message=f"Plug part number '{header.plug_part_number}' doesn't match HPC format (should start with 'P')",
                        suggestion="Verify plug part number format (e.g., P430)",
                    ))
            else:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="plug_part_number_missing",
                    message="Plug present but part number not specified",
                    suggestion="Specify plug part number (e.g., P430) per HPC standards",
                ))

        # Check 3: Welding requirements
        result.total_checks += 1
        if not header.has_weld_joint_prep:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="weld_joint_prep_not_shown",
                message="Welding joint preparation details not shown",
                suggestion="Include welding joint preparation details per HPC standards",
                standard_reference="HPC Standards Book III",
            ))
        else:
            result.passed += 1

        result.total_checks += 1
        if not header.has_weld_procedure_spec:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="weld_procedure_spec_not_shown",
                message="Weld procedure specifications not shown",
                suggestion="Include weld procedure specifications per HPC standards",
                standard_reference="HPC Standards Book III",
            ))
        else:
            result.passed += 1

        return result

    def to_dict(self, result: HPCHeaderValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "hpc_header",
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

