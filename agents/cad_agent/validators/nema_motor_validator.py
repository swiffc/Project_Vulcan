"""
NEMA Motor Frame Validator
==========================
Validates motor frame dimensions per NEMA MG-1.

Phase 25 - ACHE Standards Compliance
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.nema_motor")


# NEMA MG-1 Frame Dimensions (inches)
# Frame -> (D, 2E, 2F, H, N-W, U, BA)
# D = shaft height, 2E = base width, 2F = mounting hole spacing length
# H = mounting hole width, N-W = shaft length, U = shaft diameter, BA = foot hole dia
NEMA_FRAME_DIMS = {
    # T-Frame motors (foot-mounted)
    "143T": {"D": 3.50, "2E": 4.50, "2F": 4.00, "H": 2.75, "NW": 1.50, "U": 0.875, "BA": 0.34},
    "145T": {"D": 3.50, "2E": 5.00, "2F": 5.00, "H": 2.75, "NW": 1.50, "U": 0.875, "BA": 0.34},
    "182T": {"D": 4.50, "2E": 4.50, "2F": 4.50, "H": 3.75, "NW": 1.75, "U": 1.125, "BA": 0.41},
    "184T": {"D": 4.50, "2E": 5.50, "2F": 5.50, "H": 3.75, "NW": 1.75, "U": 1.125, "BA": 0.41},
    "213T": {"D": 5.25, "2E": 5.50, "2F": 5.50, "H": 4.25, "NW": 2.00, "U": 1.375, "BA": 0.41},
    "215T": {"D": 5.25, "2E": 7.00, "2F": 7.00, "H": 4.25, "NW": 2.00, "U": 1.375, "BA": 0.41},
    "254T": {"D": 6.25, "2E": 8.25, "2F": 8.25, "H": 5.00, "NW": 2.50, "U": 1.625, "BA": 0.53},
    "256T": {"D": 6.25, "2E": 10.00, "2F": 10.00, "H": 5.00, "NW": 2.50, "U": 1.625, "BA": 0.53},
    "284T": {"D": 7.00, "2E": 9.50, "2F": 9.50, "H": 5.50, "NW": 2.75, "U": 1.875, "BA": 0.53},
    "286T": {"D": 7.00, "2E": 11.00, "2F": 11.00, "H": 5.50, "NW": 2.75, "U": 1.875, "BA": 0.53},
    "324T": {"D": 8.00, "2E": 10.50, "2F": 10.50, "H": 6.25, "NW": 3.00, "U": 2.125, "BA": 0.66},
    "326T": {"D": 8.00, "2E": 12.50, "2F": 12.50, "H": 6.25, "NW": 3.00, "U": 2.125, "BA": 0.66},
    "364T": {"D": 9.00, "2E": 11.25, "2F": 11.25, "H": 7.00, "NW": 3.25, "U": 2.375, "BA": 0.66},
    "365T": {"D": 9.00, "2E": 12.25, "2F": 12.25, "H": 7.00, "NW": 3.25, "U": 2.375, "BA": 0.66},
    "404T": {"D": 10.00, "2E": 12.25, "2F": 12.25, "H": 8.00, "NW": 3.50, "U": 2.875, "BA": 0.81},
    "405T": {"D": 10.00, "2E": 13.75, "2F": 13.75, "H": 8.00, "NW": 3.50, "U": 2.875, "BA": 0.81},
    "444T": {"D": 11.00, "2E": 14.50, "2F": 14.50, "H": 9.00, "NW": 4.00, "U": 3.375, "BA": 0.81},
    "445T": {"D": 11.00, "2E": 16.50, "2F": 16.50, "H": 9.00, "NW": 4.00, "U": 3.375, "BA": 0.81},
    # C-Face frames
    "143TC": {"D": 3.50, "2E": 4.50, "2F": 4.00, "H": 2.75, "NW": 1.50, "U": 0.875, "AJ": 5.875},
    "145TC": {"D": 3.50, "2E": 5.00, "2F": 5.00, "H": 2.75, "NW": 1.50, "U": 0.875, "AJ": 5.875},
    "182TC": {"D": 4.50, "2E": 4.50, "2F": 4.50, "H": 3.75, "NW": 1.75, "U": 1.125, "AJ": 7.25},
    "184TC": {"D": 4.50, "2E": 5.50, "2F": 5.50, "H": 3.75, "NW": 1.75, "U": 1.125, "AJ": 7.25},
}

# Typical HP ranges for frame sizes
FRAME_HP_RANGE = {
    "143T": (0.75, 2),
    "145T": (1, 3),
    "182T": (2, 5),
    "184T": (3, 7.5),
    "213T": (5, 10),
    "215T": (7.5, 15),
    "254T": (10, 25),
    "256T": (15, 30),
    "284T": (20, 40),
    "286T": (25, 50),
    "324T": (30, 75),
    "326T": (40, 100),
    "364T": (50, 100),
    "365T": (60, 125),
    "404T": (75, 150),
    "405T": (100, 200),
    "444T": (125, 250),
    "445T": (150, 300),
}

# Minimum service factors
MIN_SERVICE_FACTOR = 1.0
CONTINUOUS_DUTY_SF = 1.15  # Recommended for continuous duty


@dataclass
class MotorData:
    """Data for motor validation."""
    frame_size: Optional[str] = None
    horsepower: Optional[float] = None
    shaft_diameter: Optional[float] = None
    shaft_length: Optional[float] = None
    mounting_hole_spacing_f: Optional[float] = None  # 2F dimension
    mounting_hole_spacing_h: Optional[float] = None  # H dimension
    shaft_height_d: Optional[float] = None
    service_factor: Optional[float] = None
    base_plate_length: Optional[float] = None
    base_plate_width: Optional[float] = None


@dataclass
class NEMAMotorValidationResult:
    """NEMA motor validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Statistics
    frame_validated: bool = False
    shaft_validated: bool = False
    mounting_validated: bool = False


class NEMAMotorValidator:
    """
    Validates motor frame dimensions per NEMA MG-1.

    Checks:
    1. Frame size vs HP compatibility
    2. Shaft diameter matches frame
    3. Shaft extension length
    4. Mounting bolt pattern (F, H dimensions)
    5. Service factor adequacy
    """

    def __init__(self):
        pass

    def validate_motor(self, motor: MotorData) -> NEMAMotorValidationResult:
        """
        Validate motor against NEMA MG-1.

        Args:
            motor: Motor data

        Returns:
            Validation result
        """
        result = NEMAMotorValidationResult()

        self._check_frame_hp_compatibility(motor, result)
        self._check_shaft_diameter(motor, result)
        self._check_shaft_length(motor, result)
        self._check_mounting_pattern(motor, result)
        self._check_service_factor(motor, result)

        return result

    def _check_frame_hp_compatibility(self, motor: MotorData, result: NEMAMotorValidationResult):
        """Check if frame size is appropriate for HP rating."""
        result.total_checks += 1

        if not motor.frame_size or not motor.horsepower:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="frame_hp_not_specified",
                message="Motor frame size or HP not specified",
                suggestion="Specify NEMA frame size and horsepower",
                standard_reference="NEMA MG-1",
            ))
            return

        # Normalize frame size (strip suffix letters for lookup)
        frame_base = motor.frame_size.upper().rstrip("TC")
        if frame_base.endswith("C"):
            frame_base = frame_base[:-1]

        if frame_base in FRAME_HP_RANGE:
            hp_min, hp_max = FRAME_HP_RANGE[frame_base]

            if motor.horsepower < hp_min:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="frame_oversized",
                    message=f"Frame {motor.frame_size} may be oversized for {motor.horsepower} HP (typical: {hp_min}-{hp_max} HP)",
                    suggestion="Consider smaller frame for cost savings",
                    standard_reference="NEMA MG-1",
                ))
            elif motor.horsepower > hp_max:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="frame_undersized",
                    message=f"Frame {motor.frame_size} undersized for {motor.horsepower} HP (max typical: {hp_max} HP)",
                    suggestion=f"Use larger frame size",
                    standard_reference="NEMA MG-1",
                ))
                return
            else:
                result.passed += 1
                result.frame_validated = True
        else:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="frame_unknown",
                message=f"Frame size {motor.frame_size} not in standard NEMA T-frame table",
                suggestion="Verify frame size is correct",
            ))

    def _check_shaft_diameter(self, motor: MotorData, result: NEMAMotorValidationResult):
        """Check shaft diameter matches frame size."""
        result.total_checks += 1

        if not motor.frame_size or not motor.shaft_diameter:
            return

        frame = motor.frame_size.upper()
        # Handle C-face variants
        if frame.endswith("C"):
            frame_lookup = frame + "C" if frame + "C" in NEMA_FRAME_DIMS else frame[:-1]
        else:
            frame_lookup = frame

        if frame_lookup not in NEMA_FRAME_DIMS:
            # Try base frame
            frame_lookup = frame.rstrip("TCJP")

        if frame_lookup in NEMA_FRAME_DIMS:
            expected_u = NEMA_FRAME_DIMS[frame_lookup]["U"]
            tolerance = 0.002  # ±0.002" for shaft diameter

            if abs(motor.shaft_diameter - expected_u) > tolerance:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="shaft_diameter",
                    message=f"Shaft diameter {motor.shaft_diameter}\" doesn't match {frame_lookup} (expected {expected_u}\")",
                    suggestion=f"Use shaft diameter {expected_u}\" per NEMA MG-1 for {frame_lookup}",
                    standard_reference="NEMA MG-1 Table 11-2",
                ))
            else:
                result.passed += 1
                result.shaft_validated = True

    def _check_shaft_length(self, motor: MotorData, result: NEMAMotorValidationResult):
        """Check shaft extension length."""
        result.total_checks += 1

        if not motor.frame_size or not motor.shaft_length:
            return

        frame = motor.frame_size.upper().rstrip("TCJP")

        if frame in NEMA_FRAME_DIMS:
            expected_nw = NEMA_FRAME_DIMS[frame]["NW"]
            tolerance = 0.03  # ±1/32" for shaft length

            if motor.shaft_length < expected_nw - tolerance:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="shaft_length_short",
                    message=f"Shaft extension {motor.shaft_length}\" shorter than standard {expected_nw}\"",
                    suggestion=f"Standard N-W dimension for {frame} is {expected_nw}\"",
                    standard_reference="NEMA MG-1 Table 11-2",
                ))
            else:
                result.passed += 1

    def _check_mounting_pattern(self, motor: MotorData, result: NEMAMotorValidationResult):
        """Check mounting bolt pattern matches frame."""
        result.total_checks += 1

        if not motor.frame_size:
            return

        frame = motor.frame_size.upper().rstrip("TCJP")

        if frame in NEMA_FRAME_DIMS:
            frame_dims = NEMA_FRAME_DIMS[frame]

            # Check 2F dimension
            if motor.mounting_hole_spacing_f is not None:
                expected_2f = frame_dims["2F"]
                tolerance = 0.03  # ±1/32"

                if abs(motor.mounting_hole_spacing_f - expected_2f) > tolerance:
                    result.failed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="mounting_f_dim",
                        message=f"Mounting hole spacing (2F) {motor.mounting_hole_spacing_f}\" doesn't match {frame} (expected {expected_2f}\")",
                        suggestion=f"Use 2F = {expected_2f}\" per NEMA MG-1",
                        standard_reference="NEMA MG-1 Table 11-1",
                    ))
                    return

            # Check H dimension
            if motor.mounting_hole_spacing_h is not None:
                expected_h = frame_dims["H"]
                tolerance = 0.03

                if abs(motor.mounting_hole_spacing_h - expected_h) > tolerance:
                    result.failed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="mounting_h_dim",
                        message=f"Mounting hole width (H) {motor.mounting_hole_spacing_h}\" doesn't match {frame} (expected {expected_h}\")",
                        suggestion=f"Use H = {expected_h}\" per NEMA MG-1",
                        standard_reference="NEMA MG-1 Table 11-1",
                    ))
                    return

            result.passed += 1
            result.mounting_validated = True

    def _check_service_factor(self, motor: MotorData, result: NEMAMotorValidationResult):
        """Check motor service factor."""
        result.total_checks += 1

        if motor.service_factor is None:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="service_factor_missing",
                message="Motor service factor not specified",
                suggestion=f"Specify service factor (min {MIN_SERVICE_FACTOR}, recommend {CONTINUOUS_DUTY_SF} for continuous duty)",
                standard_reference="NEMA MG-1",
            ))
            return

        if motor.service_factor < MIN_SERVICE_FACTOR:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="service_factor_low",
                message=f"Service factor {motor.service_factor} below minimum {MIN_SERVICE_FACTOR}",
                standard_reference="NEMA MG-1",
            ))
        elif motor.service_factor < CONTINUOUS_DUTY_SF:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="service_factor_marginal",
                message=f"Service factor {motor.service_factor} adequate but {CONTINUOUS_DUTY_SF} recommended for continuous duty",
                standard_reference="NEMA MG-1",
            ))
        else:
            result.passed += 1

    def get_frame_dimensions(self, frame_size: str) -> Optional[Dict[str, float]]:
        """
        Get NEMA frame dimensions.

        Args:
            frame_size: NEMA frame designation

        Returns:
            Dictionary of frame dimensions or None if not found
        """
        frame = frame_size.upper()
        if frame in NEMA_FRAME_DIMS:
            return NEMA_FRAME_DIMS[frame].copy()

        # Try base frame
        frame_base = frame.rstrip("TCJP")
        if frame_base in NEMA_FRAME_DIMS:
            return NEMA_FRAME_DIMS[frame_base].copy()

        return None

    def to_dict(self, result: NEMAMotorValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "nema_motor",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "statistics": {
                "frame_validated": result.frame_validated,
                "shaft_validated": result.shaft_validated,
                "mounting_validated": result.mounting_validated,
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
