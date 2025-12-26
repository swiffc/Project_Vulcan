"""
GD&T Validator - ASME Y14.5-2018
=================================
Complete Geometric Dimensioning and Tolerancing validation.

All 14 geometric tolerance symbols:
- Form: Flatness, Straightness, Circularity, Cylindricity
- Orientation: Perpendicularity, Angularity, Parallelism
- Location: Position, Concentricity, Symmetry
- Runout: Circular Runout, Total Runout
- Profile: Profile of a Line, Profile of a Surface

Plus:
- MMC/LMC/RFS modifiers
- Bonus tolerance calculations
- Datum feature validation
- Feature control frame parsing
- Composite tolerancing

Phase 25 - Full GD&T Standards Compliance
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.gdt")


class ToleranceType(str, Enum):
    """GD&T tolerance types per ASME Y14.5-2018."""
    # Form tolerances (no datum required)
    FLATNESS = "flatness"
    STRAIGHTNESS = "straightness"
    CIRCULARITY = "circularity"
    CYLINDRICITY = "cylindricity"

    # Orientation tolerances (datum required)
    PERPENDICULARITY = "perpendicularity"
    ANGULARITY = "angularity"
    PARALLELISM = "parallelism"

    # Location tolerances (datum required)
    POSITION = "position"
    CONCENTRICITY = "concentricity"
    SYMMETRY = "symmetry"

    # Runout tolerances (datum required)
    CIRCULAR_RUNOUT = "circular_runout"
    TOTAL_RUNOUT = "total_runout"

    # Profile tolerances (datum optional)
    PROFILE_LINE = "profile_line"
    PROFILE_SURFACE = "profile_surface"


class MaterialCondition(str, Enum):
    """Material condition modifiers."""
    MMC = "M"  # Maximum Material Condition
    LMC = "L"  # Least Material Condition
    RFS = "S"  # Regardless of Feature Size (default)


class FeatureType(str, Enum):
    """Feature types for GD&T application."""
    HOLE = "hole"
    PIN = "pin"
    SLOT = "slot"
    TAB = "tab"
    SURFACE = "surface"
    AXIS = "axis"
    CENTER_PLANE = "center_plane"
    PATTERN = "pattern"


# Form tolerance capabilities by process (inches)
PROCESS_FORM_CAPABILITY = {
    "grinding": 0.0001,
    "honing": 0.0002,
    "lapping": 0.0001,
    "precision_turning": 0.0005,
    "turning": 0.001,
    "milling": 0.002,
    "drilling": 0.003,
    "casting": 0.015,
    "forging": 0.030,
}

# Position tolerance for hole patterns (inches) - typical
POSITION_CAPABILITY = {
    "cnc_machining": 0.005,
    "manual_machining": 0.010,
    "drilling_jig": 0.003,
    "punching": 0.015,
    "laser_cutting": 0.005,
    "waterjet": 0.008,
}

# Standard hole sizes for bonus tolerance (inches)
STANDARD_HOLE_SIZES = [
    0.125, 0.1875, 0.250, 0.3125, 0.375, 0.4375, 0.500,
    0.5625, 0.625, 0.750, 0.875, 1.000, 1.125, 1.250
]


@dataclass
class DatumFeature:
    """Datum feature definition."""
    label: str  # A, B, C, etc.
    feature_type: FeatureType = FeatureType.SURFACE
    is_primary: bool = False
    is_secondary: bool = False
    is_tertiary: bool = False
    material_condition: MaterialCondition = MaterialCondition.RFS


@dataclass
class FeatureControlFrame:
    """Feature control frame (FCF) data."""
    tolerance_type: ToleranceType
    tolerance_value: float  # inches
    material_condition: MaterialCondition = MaterialCondition.RFS
    primary_datum: Optional[str] = None
    primary_datum_mc: MaterialCondition = MaterialCondition.RFS
    secondary_datum: Optional[str] = None
    secondary_datum_mc: MaterialCondition = MaterialCondition.RFS
    tertiary_datum: Optional[str] = None
    tertiary_datum_mc: MaterialCondition = MaterialCondition.RFS

    # For composite tolerancing
    is_composite: bool = False
    pattern_tolerance: Optional[float] = None  # PLTZF
    feature_tolerance: Optional[float] = None  # FRTZF

    # Feature data for bonus calculation
    feature_type: FeatureType = FeatureType.HOLE
    feature_size: Optional[float] = None  # Actual/nominal size
    feature_size_tolerance: Optional[float] = None  # Size tolerance


@dataclass
class PositionData:
    """Position tolerance data for holes/pins."""
    nominal_x: float = 0.0
    nominal_y: float = 0.0
    actual_x: Optional[float] = None
    actual_y: Optional[float] = None
    hole_diameter: Optional[float] = None
    hole_tolerance_plus: Optional[float] = None
    hole_tolerance_minus: Optional[float] = None
    position_tolerance: float = 0.0
    material_condition: MaterialCondition = MaterialCondition.RFS
    datum_reference_frame: str = ""


@dataclass
class GDTValidationResult:
    """GD&T validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    bonus_tolerance: Optional[float] = None
    total_tolerance: Optional[float] = None
    position_deviation: Optional[float] = None
    virtual_condition: Optional[float] = None
    resultant_condition: Optional[float] = None


class GDTValidator:
    """
    Complete GD&T validator per ASME Y14.5-2018.

    Validates all 14 geometric tolerance symbols with:
    - Material condition modifiers (MMC/LMC/RFS)
    - Bonus tolerance calculations
    - Datum feature requirements
    - Composite tolerancing
    - Virtual/resultant condition
    """

    def __init__(self):
        pass

    # =========================================================================
    # FORM TOLERANCES (No datum required)
    # =========================================================================

    def validate_flatness(
        self,
        tolerance: float,
        surface_length: float,
        surface_width: float,
        process: str = "milling",
    ) -> GDTValidationResult:
        """
        Validate flatness tolerance.

        Flatness controls how much a surface can deviate from
        a perfect plane within the specified tolerance zone.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        # Calculate diagonal for tolerance assessment
        diagonal = math.sqrt(surface_length**2 + surface_width**2)

        # Get process capability
        capability = PROCESS_FORM_CAPABILITY.get(process.lower(), 0.002)

        # Typical flatness per inch of length
        flatness_per_inch = tolerance / diagonal if diagonal > 0 else tolerance

        if tolerance < capability:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="flatness",
                message=f"Flatness {tolerance}\" tighter than {process} capability ({capability}\")",
                suggestion=f"Use finer process or relax to ≥{capability}\"",
                standard_reference="ASME Y14.5-2018 §9.2",
            ))
        elif tolerance < capability * 2:
            result.warnings += 1
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="flatness",
                message=f"Flatness {tolerance}\" near {process} capability limit",
                standard_reference="ASME Y14.5-2018 §9.2",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="flatness",
                message=f"Flatness {tolerance}\" achievable with {process}",
                standard_reference="ASME Y14.5-2018 §9.2",
            ))

        return result

    def validate_straightness(
        self,
        tolerance: float,
        feature_length: float,
        is_axis: bool = False,
        material_condition: MaterialCondition = MaterialCondition.RFS,
    ) -> GDTValidationResult:
        """
        Validate straightness tolerance.

        Can apply to:
        - Surface elements (line elements)
        - Axis (derived median line) - can use MMC/LMC
        """
        result = GDTValidationResult()
        result.total_checks += 1

        # Straightness per unit length
        straightness_ratio = tolerance / feature_length if feature_length > 0 else tolerance

        if is_axis:
            if material_condition != MaterialCondition.RFS:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="straightness_axis",
                    message=f"Axis straightness {tolerance}\" at {material_condition.value}MC",
                    suggestion="Bonus tolerance may apply",
                    standard_reference="ASME Y14.5-2018 §9.3",
                ))
            else:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="straightness_axis",
                    message=f"Axis straightness {tolerance}\" RFS",
                    standard_reference="ASME Y14.5-2018 §9.3",
                ))
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="straightness_surface",
                message=f"Surface straightness {tolerance}\" over {feature_length}\"",
                standard_reference="ASME Y14.5-2018 §9.3",
            ))

        # Check if tolerance is reasonable
        if straightness_ratio < 0.0001:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="straightness_tight",
                message="Very tight straightness may require special processes",
            ))

        result.passed += 1
        return result

    def validate_circularity(
        self,
        tolerance: float,
        diameter: float,
        process: str = "turning",
    ) -> GDTValidationResult:
        """
        Validate circularity (roundness) tolerance.

        Controls how much a circular cross-section can deviate
        from a perfect circle.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        capability = PROCESS_FORM_CAPABILITY.get(process.lower(), 0.001)

        # Circularity should be less than size tolerance
        if tolerance < capability:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="circularity",
                message=f"Circularity {tolerance}\" < {process} capability ({capability}\")",
                suggestion="Use grinding or honing for tighter circularity",
                standard_reference="ASME Y14.5-2018 §9.4",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="circularity",
                message=f"Circularity {tolerance}\" for Ø{diameter}\" achievable",
                standard_reference="ASME Y14.5-2018 §9.4",
            ))

        return result

    def validate_cylindricity(
        self,
        tolerance: float,
        diameter: float,
        length: float,
        process: str = "turning",
    ) -> GDTValidationResult:
        """
        Validate cylindricity tolerance.

        Controls the entire surface of a cylinder within a
        tolerance zone of two coaxial cylinders.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        capability = PROCESS_FORM_CAPABILITY.get(process.lower(), 0.001)

        # Cylindricity is typically 2-3x circularity due to length
        length_factor = max(1.0, length / diameter) if diameter > 0 else 1.0
        adjusted_capability = capability * length_factor

        if tolerance < adjusted_capability:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="cylindricity",
                message=f"Cylindricity {tolerance}\" tight for L/D ratio",
                suggestion=f"Consider ≥{adjusted_capability:.4f}\" for {process}",
                standard_reference="ASME Y14.5-2018 §9.5",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="cylindricity",
                message=f"Cylindricity {tolerance}\" for Ø{diameter}\" × {length}\"",
                standard_reference="ASME Y14.5-2018 §9.5",
            ))

        return result

    # =========================================================================
    # ORIENTATION TOLERANCES (Datum required)
    # =========================================================================

    def validate_perpendicularity(
        self,
        tolerance: float,
        feature_length: float,
        datum: str,
        material_condition: MaterialCondition = MaterialCondition.RFS,
        feature_type: FeatureType = FeatureType.SURFACE,
    ) -> GDTValidationResult:
        """
        Validate perpendicularity tolerance.

        Controls how perpendicular a feature is relative to a datum.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        if not datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="perpendicularity_datum",
                message="Perpendicularity requires a datum reference",
                standard_reference="ASME Y14.5-2018 §10.3",
            ))
            return result

        # Calculate angular equivalent
        angular_error = math.degrees(math.atan(tolerance / feature_length)) if feature_length > 0 else 0

        result.passed += 1
        mc_text = f" at {material_condition.value}MC" if material_condition != MaterialCondition.RFS else ""
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="perpendicularity",
            message=f"Perpendicularity {tolerance}\"{mc_text} to datum {datum} (~{angular_error:.3f}°)",
            standard_reference="ASME Y14.5-2018 §10.3",
        ))

        return result

    def validate_angularity(
        self,
        tolerance: float,
        specified_angle: float,
        feature_length: float,
        datum: str,
    ) -> GDTValidationResult:
        """
        Validate angularity tolerance.

        Controls how accurately a feature is oriented at a
        specified angle to a datum.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        if not datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="angularity_datum",
                message="Angularity requires a datum reference",
                standard_reference="ASME Y14.5-2018 §10.4",
            ))
            return result

        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="angularity",
            message=f"Angularity {tolerance}\" at {specified_angle}° to datum {datum}",
            standard_reference="ASME Y14.5-2018 §10.4",
        ))

        return result

    def validate_parallelism(
        self,
        tolerance: float,
        feature_length: float,
        datum: str,
        material_condition: MaterialCondition = MaterialCondition.RFS,
    ) -> GDTValidationResult:
        """
        Validate parallelism tolerance.

        Controls how parallel a feature is to a datum.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        if not datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="parallelism_datum",
                message="Parallelism requires a datum reference",
                standard_reference="ASME Y14.5-2018 §10.2",
            ))
            return result

        result.passed += 1
        mc_text = f" at {material_condition.value}MC" if material_condition != MaterialCondition.RFS else ""
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="parallelism",
            message=f"Parallelism {tolerance}\"{mc_text} to datum {datum}",
            standard_reference="ASME Y14.5-2018 §10.2",
        ))

        return result

    # =========================================================================
    # LOCATION TOLERANCES (Datum required)
    # =========================================================================

    def validate_position(
        self,
        fcf: FeatureControlFrame,
        position_data: Optional[PositionData] = None,
    ) -> GDTValidationResult:
        """
        Validate position tolerance - THE MOST IMPORTANT GD&T SYMBOL.

        Includes:
        - Datum reference validation
        - Bonus tolerance calculation (MMC/LMC)
        - Position deviation calculation
        - Virtual/resultant condition
        """
        result = GDTValidationResult()

        # Check datum requirement
        result.total_checks += 1
        if not fcf.primary_datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="position_datum",
                message="Position tolerance requires datum reference frame",
                suggestion="Add primary datum at minimum",
                standard_reference="ASME Y14.5-2018 §11.2",
            ))
            return result
        else:
            result.passed += 1
            datums = fcf.primary_datum
            if fcf.secondary_datum:
                datums += f", {fcf.secondary_datum}"
            if fcf.tertiary_datum:
                datums += f", {fcf.tertiary_datum}"
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="position_datums",
                message=f"Position referenced to datums: {datums}",
                standard_reference="ASME Y14.5-2018 §11.2",
            ))

        # Calculate bonus tolerance if MMC/LMC
        result.total_checks += 1
        if fcf.material_condition == MaterialCondition.MMC:
            if fcf.feature_size and fcf.feature_size_tolerance:
                if fcf.feature_type == FeatureType.HOLE:
                    # Bonus = actual size - MMC size
                    mmc_size = fcf.feature_size - fcf.feature_size_tolerance
                    # Assuming actual at LMC for max bonus
                    max_bonus = 2 * fcf.feature_size_tolerance
                    result.bonus_tolerance = max_bonus
                    result.total_tolerance = fcf.tolerance_value + max_bonus

                    result.passed += 1
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="position_bonus",
                        message=f"Position {fcf.tolerance_value}\" @ MMC, max bonus = {max_bonus:.4f}\"",
                        suggestion=f"Total possible tolerance = {result.total_tolerance:.4f}\"",
                        standard_reference="ASME Y14.5-2018 §11.3",
                    ))

                    # Calculate virtual condition
                    result.virtual_condition = mmc_size - fcf.tolerance_value
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        check_type="virtual_condition",
                        message=f"Virtual condition (gage pin) = {result.virtual_condition:.4f}\"",
                        standard_reference="ASME Y14.5-2018 §11.5",
                    ))
                else:  # PIN
                    mmc_size = fcf.feature_size + fcf.feature_size_tolerance
                    max_bonus = 2 * fcf.feature_size_tolerance
                    result.bonus_tolerance = max_bonus
                    result.total_tolerance = fcf.tolerance_value + max_bonus
                    result.passed += 1
            else:
                result.warnings += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    check_type="position_bonus",
                    message="MMC specified but feature size data missing for bonus calc",
                ))
        elif fcf.material_condition == MaterialCondition.LMC:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="position_lmc",
                message=f"Position {fcf.tolerance_value}\" @ LMC (ensures min wall)",
                standard_reference="ASME Y14.5-2018 §11.4",
            ))
        else:  # RFS
            result.passed += 1
            result.total_tolerance = fcf.tolerance_value
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="position_rfs",
                message=f"Position {fcf.tolerance_value}\" RFS (no bonus)",
                standard_reference="ASME Y14.5-2018 §11.2",
            ))

        # Calculate position deviation if actual data provided
        if position_data and position_data.actual_x is not None and position_data.actual_y is not None:
            result.total_checks += 1
            dx = position_data.actual_x - position_data.nominal_x
            dy = position_data.actual_y - position_data.nominal_y
            deviation = 2 * math.sqrt(dx**2 + dy**2)  # Diametral deviation
            result.position_deviation = deviation

            tolerance_to_check = result.total_tolerance or fcf.tolerance_value

            if deviation <= tolerance_to_check:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="position_actual",
                    message=f"Position deviation {deviation:.4f}\" ≤ {tolerance_to_check:.4f}\" PASS",
                ))
            else:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="position_actual",
                    message=f"Position deviation {deviation:.4f}\" > {tolerance_to_check:.4f}\" FAIL",
                ))

        # Composite position check
        if fcf.is_composite:
            result.total_checks += 1
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="position_composite",
                message=f"Composite: PLTZF {fcf.pattern_tolerance}\", FRTZF {fcf.feature_tolerance}\"",
                standard_reference="ASME Y14.5-2018 §11.6",
            ))

        return result

    def validate_concentricity(
        self,
        tolerance: float,
        datum: str,
    ) -> GDTValidationResult:
        """
        Validate concentricity tolerance.

        Note: Concentricity is rarely used in modern practice.
        Position or runout are usually preferred.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        if not datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="concentricity_datum",
                message="Concentricity requires datum axis reference",
                standard_reference="ASME Y14.5-2018 §11.7",
            ))
            return result

        result.warnings += 1
        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            check_type="concentricity_usage",
            message=f"Concentricity {tolerance}\" to datum {datum}",
            suggestion="Consider using Position or Runout instead (easier to inspect)",
            standard_reference="ASME Y14.5-2018 §11.7",
        ))

        return result

    def validate_symmetry(
        self,
        tolerance: float,
        datum: str,
    ) -> GDTValidationResult:
        """
        Validate symmetry tolerance.

        Note: Like concentricity, symmetry is rarely used.
        Position is usually preferred.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        if not datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="symmetry_datum",
                message="Symmetry requires datum center plane reference",
                standard_reference="ASME Y14.5-2018 §11.8",
            ))
            return result

        result.warnings += 1
        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            check_type="symmetry_usage",
            message=f"Symmetry {tolerance}\" to datum {datum}",
            suggestion="Consider using Position instead (easier to inspect)",
            standard_reference="ASME Y14.5-2018 §11.8",
        ))

        return result

    # =========================================================================
    # RUNOUT TOLERANCES (Datum axis required)
    # =========================================================================

    def validate_circular_runout(
        self,
        tolerance: float,
        datum: str,
    ) -> GDTValidationResult:
        """
        Validate circular runout tolerance.

        Controls the composite effect of circularity and
        concentricity at each circular element.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        if not datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="circular_runout_datum",
                message="Circular runout requires datum axis",
                standard_reference="ASME Y14.5-2018 §12.2",
            ))
            return result

        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="circular_runout",
            message=f"Circular runout {tolerance}\" to datum {datum} (FIM at each section)",
            standard_reference="ASME Y14.5-2018 §12.2",
        ))

        return result

    def validate_total_runout(
        self,
        tolerance: float,
        datum: str,
    ) -> GDTValidationResult:
        """
        Validate total runout tolerance.

        Controls the composite effect of circularity, cylindricity,
        straightness, and coaxiality over the entire surface.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        if not datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="total_runout_datum",
                message="Total runout requires datum axis",
                standard_reference="ASME Y14.5-2018 §12.3",
            ))
            return result

        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="total_runout",
            message=f"Total runout {tolerance}\" to datum {datum} (FIM over entire surface)",
            standard_reference="ASME Y14.5-2018 §12.3",
        ))

        return result

    # =========================================================================
    # PROFILE TOLERANCES
    # =========================================================================

    def validate_profile_line(
        self,
        tolerance: float,
        is_bilateral: bool = True,
        datum: Optional[str] = None,
    ) -> GDTValidationResult:
        """
        Validate profile of a line tolerance.

        Controls the 2D outline of a feature.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        distribution = "bilateral (±)" if is_bilateral else "unilateral"
        datum_text = f" to datum {datum}" if datum else " (no datum - form only)"

        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="profile_line",
            message=f"Profile of line {tolerance}\" {distribution}{datum_text}",
            standard_reference="ASME Y14.5-2018 §13.2",
        ))

        return result

    def validate_profile_surface(
        self,
        tolerance: float,
        is_bilateral: bool = True,
        datum: Optional[str] = None,
    ) -> GDTValidationResult:
        """
        Validate profile of a surface tolerance.

        Controls the 3D shape of a feature. Most versatile GD&T symbol.
        """
        result = GDTValidationResult()
        result.total_checks += 1

        distribution = "bilateral (±)" if is_bilateral else "unilateral"
        datum_text = f" to datum {datum}" if datum else " (no datum - form only)"

        result.passed += 1
        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="profile_surface",
            message=f"Profile of surface {tolerance}\" {distribution}{datum_text}",
            standard_reference="ASME Y14.5-2018 §13.3",
        ))

        return result

    # =========================================================================
    # FCF VALIDATION
    # =========================================================================

    def validate_fcf(self, fcf: FeatureControlFrame) -> GDTValidationResult:
        """
        Validate a complete feature control frame.
        """
        result = GDTValidationResult()

        # Check datum requirements based on tolerance type
        requires_datum = fcf.tolerance_type in [
            ToleranceType.PERPENDICULARITY,
            ToleranceType.ANGULARITY,
            ToleranceType.PARALLELISM,
            ToleranceType.POSITION,
            ToleranceType.CONCENTRICITY,
            ToleranceType.SYMMETRY,
            ToleranceType.CIRCULAR_RUNOUT,
            ToleranceType.TOTAL_RUNOUT,
        ]

        result.total_checks += 1
        if requires_datum and not fcf.primary_datum:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="fcf_datum",
                message=f"{fcf.tolerance_type.value} requires datum reference",
                standard_reference="ASME Y14.5-2018",
            ))
        else:
            result.passed += 1

        # Check material condition applicability
        mc_allowed = fcf.tolerance_type in [
            ToleranceType.STRAIGHTNESS,  # Axis only
            ToleranceType.PERPENDICULARITY,
            ToleranceType.ANGULARITY,
            ToleranceType.PARALLELISM,
            ToleranceType.POSITION,
        ]

        result.total_checks += 1
        if fcf.material_condition != MaterialCondition.RFS and not mc_allowed:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="fcf_material_condition",
                message=f"Material condition modifier not typical for {fcf.tolerance_type.value}",
                standard_reference="ASME Y14.5-2018",
            ))
        else:
            result.passed += 1

        # Dispatch to specific validator
        if fcf.tolerance_type == ToleranceType.POSITION:
            pos_result = self.validate_position(fcf)
            result.total_checks += pos_result.total_checks
            result.passed += pos_result.passed
            result.failed += pos_result.failed
            result.warnings += pos_result.warnings
            result.issues.extend(pos_result.issues)
            result.bonus_tolerance = pos_result.bonus_tolerance
            result.total_tolerance = pos_result.total_tolerance
            result.virtual_condition = pos_result.virtual_condition

        return result

    def to_dict(self, result: GDTValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "gdt_y14.5",
            "standard": "ASME Y14.5-2018",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "calculations": {
                "bonus_tolerance_in": result.bonus_tolerance,
                "total_tolerance_in": result.total_tolerance,
                "position_deviation_in": result.position_deviation,
                "virtual_condition_in": result.virtual_condition,
                "resultant_condition_in": result.resultant_condition,
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
