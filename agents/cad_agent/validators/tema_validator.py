"""
TEMA Heat Exchanger Validator
==============================
Validates heat exchanger design per TEMA standards (Class R/B/C).

Phase 25 - ACHE Standards Compliance
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.tema")


class TEMAClass(str, Enum):
    """TEMA class designations."""
    R = "R"  # Petroleum/severe service
    C = "C"  # Commercial/general
    B = "B"  # Chemical process


# Minimum tubesheet thickness factors per TEMA
# Thickness = factor × tube OD
TUBESHEET_THICKNESS_FACTOR = {
    TEMAClass.R: 0.75,  # Most conservative
    TEMAClass.C: 0.625,
    TEMAClass.B: 0.50,  # Least conservative
}

# Minimum baffle spacing as fraction of shell ID
MIN_BAFFLE_SPACING_FACTOR = {
    TEMAClass.R: 0.20,  # 20% of shell ID or 2"
    TEMAClass.C: 0.20,
    TEMAClass.B: 0.20,
}

# Maximum unsupported tube span (inches)
MAX_UNSUPPORTED_SPAN = {
    # tube_od: max_span
    0.625: 52,   # 5/8"
    0.750: 60,   # 3/4"
    1.000: 74,   # 1"
    1.250: 88,   # 1-1/4"
    1.500: 100,  # 1-1/2"
    2.000: 120,  # 2"
}

# Standard tube pitches (tube pitch / tube OD ratio)
TUBE_PITCH_RATIOS = {
    "triangular": 1.25,      # 30° triangular
    "rotated_triangular": 1.25,  # 60° triangular
    "square": 1.25,          # 90° square
    "rotated_square": 1.25,  # 45° square
}

# Minimum tube pitch ratios per TEMA
MIN_PITCH_RATIO = {
    TEMAClass.R: 1.25,
    TEMAClass.C: 1.25,
    TEMAClass.B: 1.20,  # Allows tighter pitch
}

# Tube-to-tubesheet joint types
class TubeJointType(str, Enum):
    EXPANDED = "expanded"
    WELDED = "welded"
    EXPANDED_WELDED = "expanded_welded"
    STRENGTH_WELDED = "strength_welded"


# Max velocities (ft/s) per TEMA
MAX_VELOCITY = {
    "tube_side_liquid": 10.0,
    "tube_side_gas": 100.0,
    "shell_side_liquid": 5.0,
    "shell_side_gas": 50.0,
}


@dataclass
class HeatExchangerData:
    """Heat exchanger design data."""
    tema_class: TEMAClass = TEMAClass.R

    # Shell
    shell_id_in: Optional[float] = None

    # Tubes
    tube_od_in: Optional[float] = None
    tube_pitch_in: Optional[float] = None
    tube_layout: str = "triangular"  # triangular, square, rotated
    num_tubes: int = 0

    # Tubesheet
    tubesheet_thickness_in: Optional[float] = None

    # Tube-to-tubesheet joint
    tube_joint_type: TubeJointType = TubeJointType.EXPANDED

    # Baffles
    num_baffles: int = 0
    baffle_spacing_in: Optional[float] = None
    baffle_cut_percent: float = 25.0  # % of shell ID

    # Flow data
    tube_side_velocity_fps: Optional[float] = None
    shell_side_velocity_fps: Optional[float] = None
    tube_side_fluid: str = "liquid"  # liquid or gas
    shell_side_fluid: str = "liquid"


@dataclass
class TEMAValidationResult:
    """TEMA validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    min_tubesheet_thickness: Optional[float] = None
    max_baffle_spacing: Optional[float] = None
    pitch_ratio: Optional[float] = None


class TEMAValidator:
    """
    Validates heat exchanger design per TEMA standards.

    Checks:
    1. Tubesheet thickness (RCB-7)
    2. Tube-to-tubesheet joint (RCB-7.4)
    3. Baffle spacing (RCB-4.5)
    4. Tube pitch (RCB-2.2)
    5. Shell-side velocity
    6. Tube-side velocity
    """

    def __init__(self):
        pass

    def validate_exchanger(self, hx: HeatExchangerData) -> TEMAValidationResult:
        """
        Validate heat exchanger against TEMA.

        Args:
            hx: Heat exchanger data

        Returns:
            Validation result
        """
        result = TEMAValidationResult()

        self._check_tubesheet_thickness(hx, result)
        self._check_tube_joint(hx, result)
        self._check_baffle_spacing(hx, result)
        self._check_tube_pitch(hx, result)
        self._check_shell_velocity(hx, result)
        self._check_tube_velocity(hx, result)

        return result

    def _check_tubesheet_thickness(self, hx: HeatExchangerData, result: TEMAValidationResult):
        """Check tubesheet thickness per RCB-7."""
        result.total_checks += 1

        if not hx.tube_od_in:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="tubesheet_data",
                message="Tube OD not specified for tubesheet check",
                suggestion="Provide tube OD",
            ))
            return

        factor = TUBESHEET_THICKNESS_FACTOR[hx.tema_class]
        min_thickness = factor * hx.tube_od_in
        result.min_tubesheet_thickness = min_thickness

        if hx.tubesheet_thickness_in:
            if hx.tubesheet_thickness_in >= min_thickness:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="tubesheet_thickness",
                    message=f"Tubesheet {hx.tubesheet_thickness_in}\" ≥ min {min_thickness:.3f}\" (TEMA {hx.tema_class.value})",
                    standard_reference=f"TEMA {hx.tema_class.value}CB-7",
                ))
            else:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="tubesheet_thickness",
                    message=f"Tubesheet {hx.tubesheet_thickness_in}\" < min {min_thickness:.3f}\"",
                    suggestion=f"Increase tubesheet thickness to ≥{min_thickness:.3f}\"",
                    standard_reference=f"TEMA {hx.tema_class.value}CB-7",
                ))
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="tubesheet_thickness_calc",
                message=f"Min tubesheet thickness = {min_thickness:.3f}\" for {hx.tube_od_in}\" tubes (TEMA {hx.tema_class.value})",
                standard_reference=f"TEMA {hx.tema_class.value}CB-7",
            ))
            result.passed += 1

    def _check_tube_joint(self, hx: HeatExchangerData, result: TEMAValidationResult):
        """Check tube-to-tubesheet joint per RCB-7.4."""
        result.total_checks += 1

        joint_descriptions = {
            TubeJointType.EXPANDED: "Roller expanded (standard)",
            TubeJointType.WELDED: "Seal welded only",
            TubeJointType.EXPANDED_WELDED: "Expanded and seal welded",
            TubeJointType.STRENGTH_WELDED: "Strength welded (full)",
        }

        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="tube_joint",
            message=f"Tube joint: {joint_descriptions.get(hx.tube_joint_type, hx.tube_joint_type.value)}",
            standard_reference=f"TEMA {hx.tema_class.value}CB-7.4",
        ))

        # Class R typically requires expanded + welded for severe service
        if hx.tema_class == TEMAClass.R and hx.tube_joint_type == TubeJointType.EXPANDED:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="tube_joint_class_r",
                message="TEMA R service may require expanded + welded joint",
                suggestion="Consider expanded and seal welded for severe service",
                standard_reference="TEMA RCB-7.4",
            ))
        else:
            result.passed += 1

    def _check_baffle_spacing(self, hx: HeatExchangerData, result: TEMAValidationResult):
        """Check baffle spacing per RCB-4.5."""
        result.total_checks += 1

        if not hx.shell_id_in or not hx.baffle_spacing_in:
            if hx.tube_od_in and hx.tube_od_in in MAX_UNSUPPORTED_SPAN:
                max_span = MAX_UNSUPPORTED_SPAN[hx.tube_od_in]
                result.max_baffle_spacing = max_span
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="baffle_spacing_max",
                    message=f"Max unsupported span for {hx.tube_od_in}\" tubes = {max_span}\"",
                    standard_reference=f"TEMA {hx.tema_class.value}CB-4.5",
                ))
            result.passed += 1
            return

        # Minimum baffle spacing
        min_factor = MIN_BAFFLE_SPACING_FACTOR[hx.tema_class]
        min_spacing = max(min_factor * hx.shell_id_in, 2.0)  # Min 2"

        # Maximum baffle spacing (unsupported span)
        max_spacing = MAX_UNSUPPORTED_SPAN.get(hx.tube_od_in, 74)  # Default 74" for 1" tubes
        result.max_baffle_spacing = max_spacing

        if hx.baffle_spacing_in < min_spacing:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="baffle_spacing_min",
                message=f"Baffle spacing {hx.baffle_spacing_in}\" < min {min_spacing:.1f}\"",
                suggestion=f"Increase baffle spacing to ≥{min_spacing:.1f}\"",
                standard_reference=f"TEMA {hx.tema_class.value}CB-4.5",
            ))
        elif hx.baffle_spacing_in > max_spacing:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="baffle_spacing_max",
                message=f"Baffle spacing {hx.baffle_spacing_in}\" > max {max_spacing}\" (tube vibration risk)",
                suggestion=f"Reduce baffle spacing to ≤{max_spacing}\"",
                standard_reference=f"TEMA {hx.tema_class.value}CB-4.5",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="baffle_spacing",
                message=f"Baffle spacing {hx.baffle_spacing_in}\" within limits ({min_spacing:.1f}\" - {max_spacing}\")",
                standard_reference=f"TEMA {hx.tema_class.value}CB-4.5",
            ))

    def _check_tube_pitch(self, hx: HeatExchangerData, result: TEMAValidationResult):
        """Check tube pitch per RCB-2.2."""
        result.total_checks += 1

        if not hx.tube_od_in or not hx.tube_pitch_in:
            result.passed += 1
            return

        pitch_ratio = hx.tube_pitch_in / hx.tube_od_in
        result.pitch_ratio = pitch_ratio

        min_ratio = MIN_PITCH_RATIO[hx.tema_class]

        if pitch_ratio < min_ratio:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="tube_pitch",
                message=f"Pitch ratio {pitch_ratio:.2f} < min {min_ratio} for TEMA {hx.tema_class.value}",
                suggestion=f"Increase tube pitch to ≥{min_ratio * hx.tube_od_in:.3f}\"",
                standard_reference=f"TEMA {hx.tema_class.value}CB-2.2",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="tube_pitch",
                message=f"Tube pitch {hx.tube_pitch_in}\" (ratio {pitch_ratio:.2f}) OK for TEMA {hx.tema_class.value}",
                standard_reference=f"TEMA {hx.tema_class.value}CB-2.2",
            ))

        # Check ligament (space between tubes)
        ligament = hx.tube_pitch_in - hx.tube_od_in
        min_ligament = 0.25 if hx.tema_class == TEMAClass.R else 0.1875  # 1/4" or 3/16"

        if ligament < min_ligament:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="tube_ligament",
                message=f"Tube ligament {ligament:.3f}\" may be narrow (min ~{min_ligament}\")",
                suggestion="Verify cleaning lane access",
            ))

    def _check_shell_velocity(self, hx: HeatExchangerData, result: TEMAValidationResult):
        """Check shell-side velocity."""
        result.total_checks += 1

        if not hx.shell_side_velocity_fps:
            result.passed += 1
            return

        fluid_type = hx.shell_side_fluid.lower()
        max_vel = MAX_VELOCITY.get(f"shell_side_{fluid_type}", 5.0)

        if hx.shell_side_velocity_fps > max_vel:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="shell_velocity",
                message=f"Shell-side velocity {hx.shell_side_velocity_fps} fps > typical max {max_vel} fps",
                suggestion="High velocity may cause erosion/vibration",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="shell_velocity",
                message=f"Shell-side velocity {hx.shell_side_velocity_fps} fps ≤ {max_vel} fps",
            ))

    def _check_tube_velocity(self, hx: HeatExchangerData, result: TEMAValidationResult):
        """Check tube-side velocity."""
        result.total_checks += 1

        if not hx.tube_side_velocity_fps:
            result.passed += 1
            return

        fluid_type = hx.tube_side_fluid.lower()
        max_vel = MAX_VELOCITY.get(f"tube_side_{fluid_type}", 10.0)

        if hx.tube_side_velocity_fps > max_vel:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="tube_velocity",
                message=f"Tube-side velocity {hx.tube_side_velocity_fps} fps > typical max {max_vel} fps",
                suggestion="High velocity may cause erosion",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="tube_velocity",
                message=f"Tube-side velocity {hx.tube_side_velocity_fps} fps ≤ {max_vel} fps",
            ))

    def to_dict(self, result: TEMAValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "tema",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "calculations": {
                "min_tubesheet_thickness_in": result.min_tubesheet_thickness,
                "max_baffle_spacing_in": result.max_baffle_spacing,
                "pitch_ratio": result.pitch_ratio,
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
