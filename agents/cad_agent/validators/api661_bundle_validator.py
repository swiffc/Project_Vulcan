"""
API 661 Bundle Assembly Validator
=================================
Validates tube bundle assembly requirements per API 661 Section 7.1.

Phase 25 - ACHE Standards Compliance
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.api661_bundle")


# API 661 Constants
MAX_TUBE_SUPPORT_SPACING_MM = 1830  # 6 ft
MAX_TUBE_SUPPORT_SPACING_IN = 72  # 6 ft
MIN_LATERAL_MOVEMENT_MM = 6.0  # 1/4" both directions
MIN_LATERAL_MOVEMENT_ONE_DIR_MM = 12.7  # 1/2" one direction
CONDENSER_SLOPE_MM_PER_M = 10  # 1/8 in/ft

# Prohibited nozzle sizes (DN)
PROHIBITED_NOZZLE_SIZES_DN = [32, 65, 90, 125]  # 1-1/4", 2-1/2", 3-1/2", 5"
MIN_FLANGED_SIZE_DN = 40  # 1-1/2"

# Header type pressure limits
PLUG_HEADER_REQUIRED_PRESSURE_PSI = 435  # 3 MPa

# Fan tip clearance (mm) per Table 6
FAN_TIP_CLEARANCE = {
    # fan_dia_mm: (min_clearance, max_clearance)
    3000: (6.35, 12.70),   # ≤3m: 1/4" to 1/2"
    3500: (6.35, 15.90),   # 3-3.5m: 1/4" to 5/8"
    9999: (6.35, 19.05),   # >3.5m: 1/4" to 3/4"
}

# Belt drive limits
VBELT_MAX_KW = 30  # 40 HP
HTD_MAX_KW = 45  # 60 HP
VBELT_SERVICE_FACTOR = 1.4
HTD_SERVICE_FACTOR_MIN = 1.8
HTD_SERVICE_FACTOR_MAX = 2.0

# Bearing L10 life requirements (hours)
MOTOR_BEARING_L10 = 40000
SHAFT_BEARING_L10 = 50000


class HeaderType(str, Enum):
    PLUG = "plug"
    COVER_PLATE = "cover_plate"
    BONNET = "bonnet"


@dataclass
class BundleData:
    """Data for tube bundle validation."""
    # Tube support
    tube_support_spacing_in: Optional[float] = None
    has_tube_keepers: bool = False
    tube_keepers_bolted: bool = False  # vs welded
    num_tube_supports: int = 0

    # Air seals
    has_air_seals: bool = False
    has_p_strips: bool = False

    # Lateral movement
    lateral_movement_both_dir_mm: Optional[float] = None
    lateral_movement_one_dir_mm: Optional[float] = None

    # Condenser slope
    is_condenser: bool = False
    tube_slope_mm_per_m: Optional[float] = None

    # Header
    header_type: Optional[str] = None
    design_pressure_psi: Optional[float] = None
    is_h2_service: bool = False

    # Plugs
    plug_type: Optional[str] = None  # "shoulder", "hollow", etc.
    plug_head_type: Optional[str] = None  # "hex", "square", etc.

    # Nozzles
    nozzle_sizes_dn: List[int] = field(default_factory=list)
    nozzles_flanged: Dict[int, bool] = field(default_factory=dict)

    # Instruments
    has_vent: bool = False
    vent_at_high_point: bool = False
    has_drain: bool = False
    drain_at_low_point: bool = False
    has_thermowell: bool = False
    has_pressure_gauge: bool = False


@dataclass
class FanData:
    """Data for fan validation."""
    diameter_mm: float = 0.0
    tip_clearance_mm: Optional[float] = None


@dataclass
class DriveData:
    """Data for drive system validation."""
    drive_type: str = "gear"  # "vbelt", "htd", "gear"
    motor_power_kw: float = 0.0
    service_factor: Optional[float] = None
    motor_bearing_l10: Optional[int] = None
    shaft_bearing_l10: Optional[int] = None


@dataclass
class API661BundleValidationResult:
    """API 661 bundle validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)


class API661BundleValidator:
    """
    Validates tube bundle assembly per API 661 Section 7.1.

    Checks:
    1. Tube support spacing ≤ 6 ft
    2. Tube keepers at each support (bolted, not welded)
    3. Air seals / P-strips specified
    4. Lateral movement provision
    5. Condenser tube slope
    6. Header type vs pressure
    7. Plug type and configuration
    8. Nozzle sizes (prohibited sizes, flanged requirement)
    9. Vent/drain locations
    10. Fan tip clearance
    11. Drive system requirements
    12. Bearing L10 life
    """

    def __init__(self):
        pass

    def validate_bundle(self, bundle: BundleData) -> API661BundleValidationResult:
        """
        Validate tube bundle assembly.

        Args:
            bundle: Bundle data

        Returns:
            Validation result
        """
        result = API661BundleValidationResult()

        self._check_tube_support_spacing(bundle, result)
        self._check_tube_keepers(bundle, result)
        self._check_air_seals(bundle, result)
        self._check_lateral_movement(bundle, result)
        self._check_condenser_slope(bundle, result)
        self._check_header_type(bundle, result)
        self._check_plug_type(bundle, result)
        self._check_nozzle_sizes(bundle, result)
        self._check_vent_drain(bundle, result)

        return result

    def _check_tube_support_spacing(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check tube support spacing ≤ 6 ft per 7.1.1.4."""
        result.total_checks += 1

        if bundle.tube_support_spacing_in is None:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="tube_support_spacing",
                message="Tube support spacing not specified",
                suggestion=f"Specify tube support spacing (max {MAX_TUBE_SUPPORT_SPACING_IN}\" / 6 ft)",
                standard_reference="API 661 7.1.1.4",
            ))
        elif bundle.tube_support_spacing_in > MAX_TUBE_SUPPORT_SPACING_IN:
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="tube_support_spacing",
                message=f"Tube support spacing {bundle.tube_support_spacing_in}\" exceeds max {MAX_TUBE_SUPPORT_SPACING_IN}\" (6 ft)",
                suggestion="Reduce tube support spacing to ≤ 6 ft center-to-center",
                standard_reference="API 661 7.1.1.4",
            ))
        else:
            result.passed += 1

    def _check_tube_keepers(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check tube keepers at each support, bolted per 7.1.1.5."""
        result.total_checks += 1

        if not bundle.has_tube_keepers:
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="tube_keepers_missing",
                message="Tube keepers not shown at tube supports",
                suggestion="Add tube keepers at each tube support location",
                standard_reference="API 661 7.1.1.5",
            ))
        elif not bundle.tube_keepers_bolted:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="tube_keepers_welded",
                message="Tube keepers must be bolted to side frames, not welded",
                suggestion="Change tube keeper attachment to bolted connection",
                standard_reference="API 661 7.1.1.5",
            ))
        else:
            result.passed += 1

    def _check_air_seals(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check air seals / P-strips per 7.1.1.8."""
        result.total_checks += 1

        if not bundle.has_air_seals and not bundle.has_p_strips:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="air_seals_missing",
                message="Air seals / P-strips not specified",
                suggestion="Add air seals throughout bundle and bay to minimize air leakage/bypassing",
                standard_reference="API 661 7.1.1.8",
            ))
        else:
            result.passed += 1

    def _check_lateral_movement(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check lateral movement provision per 7.1.1.2."""
        result.total_checks += 1

        has_movement = False

        if bundle.lateral_movement_both_dir_mm is not None:
            if bundle.lateral_movement_both_dir_mm >= MIN_LATERAL_MOVEMENT_MM:
                has_movement = True

        if bundle.lateral_movement_one_dir_mm is not None:
            if bundle.lateral_movement_one_dir_mm >= MIN_LATERAL_MOVEMENT_ONE_DIR_MM:
                has_movement = True

        if not has_movement and bundle.lateral_movement_both_dir_mm is None and bundle.lateral_movement_one_dir_mm is None:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="lateral_movement_not_specified",
                message="Bundle lateral movement provision not specified",
                suggestion="Specify lateral movement (≥6mm both directions OR ≥12.7mm one direction)",
                standard_reference="API 661 7.1.1.2",
            ))
        elif not has_movement:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="lateral_movement_insufficient",
                message="Bundle lateral movement insufficient",
                suggestion="Provide ≥6mm (1/4\") both directions OR ≥12.7mm (1/2\") one direction",
                standard_reference="API 661 7.1.1.2",
            ))
        else:
            result.passed += 1

    def _check_condenser_slope(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check condenser tube slope per 7.1.1.6."""
        if not bundle.is_condenser:
            return

        result.total_checks += 1

        if bundle.tube_slope_mm_per_m is None:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="condenser_slope_not_specified",
                message="Condenser tube slope not specified",
                suggestion=f"Specify tube slope ≥{CONDENSER_SLOPE_MM_PER_M} mm/m (1/8 in/ft) toward outlet",
                standard_reference="API 661 7.1.1.6",
            ))
        elif bundle.tube_slope_mm_per_m < CONDENSER_SLOPE_MM_PER_M:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="condenser_slope_insufficient",
                message=f"Tube slope {bundle.tube_slope_mm_per_m} mm/m < required {CONDENSER_SLOPE_MM_PER_M} mm/m",
                suggestion="Increase tube slope to ≥10 mm/m (1/8 in/ft) toward outlet",
                standard_reference="API 661 7.1.1.6",
            ))
        else:
            result.passed += 1

    def _check_header_type(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check header type vs pressure per 7.1.6."""
        result.total_checks += 1

        if bundle.header_type is None:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="header_type_not_specified",
                message="Header type not specified",
                standard_reference="API 661 7.1.6",
            ))
            return

        requires_plug = (
            (bundle.design_pressure_psi and bundle.design_pressure_psi >= PLUG_HEADER_REQUIRED_PRESSURE_PSI) or
            bundle.is_h2_service
        )

        if requires_plug and bundle.header_type != HeaderType.PLUG.value:
            result.failed += 1
            result.critical_failures += 1
            reason = "H2 service" if bundle.is_h2_service else f"pressure ≥{PLUG_HEADER_REQUIRED_PRESSURE_PSI} psi"
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="header_type_wrong",
                message=f"Plug header required for {reason}, but {bundle.header_type} specified",
                suggestion="Change to plug-type header",
                standard_reference="API 661 7.1.6",
            ))
        else:
            result.passed += 1

    def _check_plug_type(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check plug requirements per 7.1.7."""
        if bundle.header_type != HeaderType.PLUG.value:
            return

        result.total_checks += 1

        if bundle.plug_type == "hollow":
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="hollow_plugs_prohibited",
                message="Hollow plugs are NOT allowed per API 661",
                suggestion="Use shoulder-type plugs with solid hex head",
                standard_reference="API 661 7.1.7.2",
            ))
        elif bundle.plug_type != "shoulder":
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="plug_type_not_shoulder",
                message=f"Plug type '{bundle.plug_type}' - should be shoulder type",
                suggestion="Use shoulder-type plugs with straight-threaded shank",
                standard_reference="API 661 7.1.7",
            ))
        else:
            result.passed += 1

        # Check hex head
        result.total_checks += 1
        if bundle.plug_head_type and bundle.plug_head_type != "hex":
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="plug_head_not_hex",
                message=f"Plug head type '{bundle.plug_head_type}' - should be hexagonal",
                standard_reference="API 661 7.1.7",
            ))
        else:
            result.passed += 1

    def _check_nozzle_sizes(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check nozzle sizes per 7.1.9.5."""
        if not bundle.nozzle_sizes_dn:
            return

        # Check for prohibited sizes
        for dn in bundle.nozzle_sizes_dn:
            result.total_checks += 1

            if dn in PROHIBITED_NOZZLE_SIZES_DN:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="nozzle_size_prohibited",
                    message=f"DN{dn} nozzle size is prohibited",
                    suggestion=f"Use next standard size (DN{dn} → DN{dn + 10 if dn < 100 else dn + 25})",
                    standard_reference="API 661 7.1.9.5",
                ))
            else:
                result.passed += 1

        # Check flanged requirement for DN40+
        for dn, is_flanged in bundle.nozzles_flanged.items():
            if dn >= MIN_FLANGED_SIZE_DN:
                result.total_checks += 1
                if not is_flanged:
                    result.failed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        check_type="nozzle_not_flanged",
                        message=f"DN{dn} nozzle must be flanged (≥DN40 requirement)",
                        suggestion="Add flange to nozzle",
                        standard_reference="API 661 7.1.9.5",
                    ))
                else:
                    result.passed += 1

    def _check_vent_drain(self, bundle: BundleData, result: API661BundleValidationResult):
        """Check vent and drain locations per 7.1.9."""
        # Vent check
        result.total_checks += 1
        if not bundle.has_vent:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="vent_missing",
                message="Vent connection not shown",
                suggestion="Add vent at header high point",
                standard_reference="API 661 7.1.9",
            ))
        elif not bundle.vent_at_high_point:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="vent_location",
                message="Vent should be at header high point",
                standard_reference="API 661 7.1.9",
            ))
        else:
            result.passed += 1

        # Drain check
        result.total_checks += 1
        if not bundle.has_drain:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="drain_missing",
                message="Drain connection not shown",
                suggestion="Add drain at header low point",
                standard_reference="API 661 7.1.9",
            ))
        elif not bundle.drain_at_low_point:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="drain_location",
                message="Drain should be at header low point",
                standard_reference="API 661 7.1.9",
            ))
        else:
            result.passed += 1

    def validate_fan(self, fan: FanData) -> API661BundleValidationResult:
        """Validate fan tip clearance per Table 6."""
        result = API661BundleValidationResult()
        result.total_checks += 1

        if fan.tip_clearance_mm is None:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="fan_tip_clearance_not_specified",
                message="Fan tip clearance not specified",
                standard_reference="API 661 Table 6",
            ))
            return result

        # Find applicable clearance range
        min_clear, max_clear = 6.35, 19.05  # Default
        for max_dia, (min_c, max_c) in FAN_TIP_CLEARANCE.items():
            if fan.diameter_mm <= max_dia:
                min_clear, max_clear = min_c, max_c
                break

        if fan.tip_clearance_mm < min_clear:
            result.failed += 1
            result.critical_failures += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                check_type="fan_tip_clearance_too_small",
                message=f"Fan tip clearance {fan.tip_clearance_mm}mm < min {min_clear}mm",
                suggestion=f"Increase tip clearance to ≥{min_clear}mm",
                standard_reference="API 661 Table 6",
            ))
        elif fan.tip_clearance_mm > max_clear:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="fan_tip_clearance_large",
                message=f"Fan tip clearance {fan.tip_clearance_mm}mm > recommended max {max_clear}mm",
                suggestion=f"Consider reducing to ≤{max_clear}mm for efficiency",
                standard_reference="API 661 Table 6",
            ))
        else:
            result.passed += 1

        return result

    def validate_drive(self, drive: DriveData) -> API661BundleValidationResult:
        """Validate drive system per 7.2.4."""
        result = API661BundleValidationResult()

        # Check drive type vs power
        result.total_checks += 1
        if drive.drive_type == "vbelt" and drive.motor_power_kw > VBELT_MAX_KW:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="vbelt_over_limit",
                message=f"V-belt drive max {VBELT_MAX_KW}kW, motor is {drive.motor_power_kw}kW",
                suggestion="Use HTD belt or gear drive for higher power",
                standard_reference="API 661 7.2.4.5",
            ))
        elif drive.drive_type == "htd" and drive.motor_power_kw > HTD_MAX_KW:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="htd_over_limit",
                message=f"HTD belt drive max {HTD_MAX_KW}kW, motor is {drive.motor_power_kw}kW",
                suggestion="Use gear drive for power >45kW",
                standard_reference="API 661 7.2.4.5",
            ))
        else:
            result.passed += 1

        # Check service factor
        if drive.service_factor is not None:
            result.total_checks += 1
            if drive.drive_type == "vbelt" and drive.service_factor < VBELT_SERVICE_FACTOR:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="vbelt_sf_low",
                    message=f"V-belt SF {drive.service_factor} < required {VBELT_SERVICE_FACTOR}",
                    standard_reference="API 661 7.2.4.5",
                ))
            elif drive.drive_type == "htd" and drive.service_factor < HTD_SERVICE_FACTOR_MIN:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="htd_sf_low",
                    message=f"HTD belt SF {drive.service_factor} < required {HTD_SERVICE_FACTOR_MIN}",
                    standard_reference="API 661 7.2.4.5",
                ))
            else:
                result.passed += 1

        # Check bearing L10 life
        if drive.motor_bearing_l10 is not None:
            result.total_checks += 1
            if drive.motor_bearing_l10 < MOTOR_BEARING_L10:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="motor_bearing_l10",
                    message=f"Motor bearing L10 {drive.motor_bearing_l10}hrs < required {MOTOR_BEARING_L10}hrs",
                    standard_reference="API 661 7.2.4.1",
                ))
            else:
                result.passed += 1

        if drive.shaft_bearing_l10 is not None:
            result.total_checks += 1
            if drive.shaft_bearing_l10 < SHAFT_BEARING_L10:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="shaft_bearing_l10",
                    message=f"Shaft bearing L10 {drive.shaft_bearing_l10}hrs < required {SHAFT_BEARING_L10}hrs",
                    standard_reference="API 661 7.2.5",
                ))
            else:
                result.passed += 1

        return result

    def to_dict(self, result: API661BundleValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "api661_bundle",
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
                    "standard_reference": issue.standard_reference,
                }
                for issue in result.issues
            ],
        }
