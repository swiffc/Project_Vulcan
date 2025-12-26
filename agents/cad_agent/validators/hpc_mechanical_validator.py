"""
HPC Mechanical Standards Validator
===================================
Validates machinery mounts, fans, vibration switches per HPC standards.

References:
- HPC Standards Book II Vol. I - GA & Assembly, Mechanicals
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

logger = logging.getLogger("vulcan.validator.hpc_mechanical")

# HPC Mechanical Standards
HPC_VIBRATION_SWITCH_MOUNTING = {
    "distance_from_fan_centerline_ft": 1.0,
    "distance_from_top_in": 6.0,
    "description": "Vibration switch mounting: 1' from fan centerline, 6\" from top"
}

HPC_DIAGONAL_BRACE_SPACING = {
    "min_in": 1.0,
    "max_in": 6.25,
    "increment_in": 0.25,
    "description": "Spacing from c-channel stiffener to plan brace in even 1/4\" increments, between 1\" and 6-1/4\""
}


@dataclass
class MachineryMountData:
    """Data for machinery mount validation."""
    mount_type: str  # "forced_draft" or "induced_draft"
    length_ft: Optional[float] = None
    has_vibration_switch: bool = False
    vibration_switch_location: Optional[Dict[str, float]] = None  # {"from_centerline_ft": x, "from_top_in": y}
    diagonal_brace_spacing_in: Optional[float] = None


@dataclass
class FanData:
    """Data for fan validation."""
    fan_diameter_ft: Optional[float] = None
    fan_type: Optional[str] = None  # "forced_draft" or "induced_draft"
    num_fans: int = 1


@dataclass
class HPCMechanicalValidationResult:
    """HPC mechanical validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)


class HPCMechanicalValidator:
    """
    Validates HPC mechanical standards.

    Checks:
    1. Vibration switch mounting location (1' from centerline, 6" from top)
    2. Diagonal brace spacing (1" to 6-1/4" in 1/4" increments)
    3. Machinery mount configuration
    4. Fan specifications
    """

    def __init__(self):
        pass

    def validate_machinery_mount(
        self,
        mount: MachineryMountData
    ) -> HPCMechanicalValidationResult:
        """
        Validate machinery mount per HPC standards.

        Args:
            mount: Machinery mount data

        Returns:
            Validation result
        """
        result = HPCMechanicalValidationResult()

        # Check 1: Vibration switch mounting location
        if mount.has_vibration_switch:
            result.total_checks += 1
            if mount.vibration_switch_location:
                from_cl = mount.vibration_switch_location.get("from_centerline_ft", 0)
                from_top = mount.vibration_switch_location.get("from_top_in", 0)
                
                required_cl = HPC_VIBRATION_SWITCH_MOUNTING["distance_from_fan_centerline_ft"]
                required_top = HPC_VIBRATION_SWITCH_MOUNTING["distance_from_top_in"]
                
                if abs(from_cl - required_cl) > 0.1 or abs(from_top - required_top) > 0.5:
                    result.failed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        check_type="vibration_switch_location",
                        message=f"Vibration switch location ({from_cl}' from CL, {from_top}\" from top) doesn't match HPC standard",
                        suggestion=f"Mount vibration switch {required_cl}' from fan centerline, {required_top}\" from top per HPC standards",
                        standard_reference="HPC Standards Book II Vol. I",
                    ))
                else:
                    result.passed += 1
            else:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="vibration_switch_location_unknown",
                    message="Vibration switch present but location not specified",
                    suggestion=f"Verify location: {HPC_VIBRATION_SWITCH_MOUNTING['distance_from_fan_centerline_ft']}' from centerline, {HPC_VIBRATION_SWITCH_MOUNTING['distance_from_top_in']}\" from top",
                ))

        # Check 2: Diagonal brace spacing
        if mount.diagonal_brace_spacing_in is not None:
            result.total_checks += 1
            spacing = mount.diagonal_brace_spacing_in
            min_spacing = HPC_DIAGONAL_BRACE_SPACING["min_in"]
            max_spacing = HPC_DIAGONAL_BRACE_SPACING["max_in"]
            increment = HPC_DIAGONAL_BRACE_SPACING["increment_in"]
            
            # Check if within range
            if spacing < min_spacing or spacing > max_spacing:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="brace_spacing_out_of_range",
                    message=f"Diagonal brace spacing {spacing}\" outside HPC range ({min_spacing}\" to {max_spacing}\")",
                    suggestion=f"Adjust spacing to between {min_spacing}\" and {max_spacing}\" per HPC standards",
                    standard_reference="HPC Standards Book II Vol. I",
                ))
            # Check if in 1/4" increments
            elif (spacing * 4) % 1 != 0:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="brace_spacing_not_increment",
                    message=f"Diagonal brace spacing {spacing}\" not in 1/4\" increments",
                    suggestion=f"Round to nearest 1/4\" increment (e.g., {round(spacing * 4) / 4}\")",
                    standard_reference="HPC Standards Book II Vol. I",
                ))
            else:
                result.passed += 1

        return result

    def validate_fan_configuration(
        self,
        fan: FanData
    ) -> HPCMechanicalValidationResult:
        """
        Validate fan configuration per HPC standards.

        Args:
            fan: Fan data

        Returns:
            Validation result
        """
        result = HPCMechanicalValidationResult()

        # Check fan type is specified
        result.total_checks += 1
        if not fan.fan_type or fan.fan_type not in ["forced_draft", "induced_draft"]:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="fan_type_unspecified",
                message="Fan type not specified (forced_draft or induced_draft)",
                suggestion="Specify fan type for proper configuration validation",
            ))
        else:
            result.passed += 1

        return result

    def to_dict(self, result: HPCMechanicalValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "hpc_mechanical",
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

