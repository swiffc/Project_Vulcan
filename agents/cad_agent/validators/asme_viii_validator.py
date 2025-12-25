"""
ASME VIII Pressure Vessel Validator
====================================
Validates pressure vessel components per ASME Section VIII Division 1.

Phase 25 - ACHE Standards Compliance (Header boxes, nozzles)
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.asme_viii")


class WeldJointType(str, Enum):
    """Weld joint categories per UW-12."""
    TYPE_1 = "1"  # Full radiography, E=1.0
    TYPE_2 = "2"  # Spot radiography, E=0.85
    TYPE_3 = "3"  # No radiography, E=0.70


# Material allowable stresses (ksi) at temperature - simplified table
# Full tables in ASME II Part D
MATERIAL_ALLOWABLE_STRESS = {
    # Material: {temp_F: stress_ksi}
    "SA-516-70": {100: 20.0, 200: 20.0, 300: 20.0, 400: 20.0, 500: 19.4, 600: 18.0},
    "SA-516-60": {100: 17.1, 200: 17.1, 300: 17.1, 400: 17.1, 500: 16.6, 600: 15.4},
    "SA-240-304": {100: 20.0, 200: 18.9, 300: 17.5, 400: 16.3, 500: 15.5, 600: 14.8},
    "SA-240-316": {100: 20.0, 200: 18.5, 300: 17.0, 400: 15.9, 500: 15.0, 600: 14.4},
    "SA-106-B": {100: 17.1, 200: 17.1, 300: 17.1, 400: 17.1, 500: 16.6, 600: 15.4},
}

# Weld joint efficiency per UW-12
JOINT_EFFICIENCY = {
    WeldJointType.TYPE_1: 1.0,   # Full RT
    WeldJointType.TYPE_2: 0.85,  # Spot RT
    WeldJointType.TYPE_3: 0.70,  # No RT
}

# Hydrostatic test factors
HYDRO_TEST_FACTOR = 1.3  # Per UG-99(b)

# Flange ratings per ASME B16.5 (psi at ambient)
FLANGE_RATINGS = {
    150: {"ambient": 285, "100F": 275, "200F": 230, "300F": 200},
    300: {"ambient": 740, "100F": 720, "200F": 600, "300F": 535},
    600: {"ambient": 1480, "100F": 1440, "200F": 1200, "300F": 1070},
    900: {"ambient": 2220, "100F": 2160, "200F": 1795, "300F": 1600},
    1500: {"ambient": 3705, "100F": 3600, "200F": 2995, "300F": 2670},
    2500: {"ambient": 6170, "100F": 6000, "200F": 4990, "300F": 4450},
}


@dataclass
class VesselData:
    """Pressure vessel design data."""
    # Geometry
    inside_diameter_in: Optional[float] = None
    wall_thickness_in: Optional[float] = None
    corrosion_allowance_in: float = 0.0625  # 1/16" default

    # Design conditions
    design_pressure_psi: Optional[float] = None
    design_temp_f: float = 100

    # Material
    material: str = "SA-516-70"

    # Weld
    joint_type: WeldJointType = WeldJointType.TYPE_2

    # Nozzle (if checking reinforcement)
    nozzle_od_in: Optional[float] = None
    nozzle_thickness_in: Optional[float] = None

    # Flange
    flange_class: Optional[int] = None  # 150, 300, 600, etc.

    # Testing
    hydro_test_pressure_psi: Optional[float] = None

    # Traceability
    has_mtr: bool = False  # Material Test Report


@dataclass
class ASMEVIIIValidationResult:
    """ASME VIII validation result."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    # Calculated values
    min_wall_thickness: Optional[float] = None
    mawp: Optional[float] = None
    required_hydro_pressure: Optional[float] = None
    nozzle_reinforcement_ok: Optional[bool] = None


class ASMEVIIIValidator:
    """
    Validates pressure vessel components per ASME VIII Div 1.

    Checks:
    1. Minimum wall thickness (UG-27)
    2. Nozzle reinforcement (UG-37)
    3. Flange rating verification (B16.5)
    4. Weld joint efficiency (UW-12)
    5. Hydrostatic test pressure (UG-99)
    6. MAWP calculation (UG-98)
    7. Corrosion allowance (UG-25)
    8. Material traceability (UG-93)
    """

    def __init__(self):
        pass

    def validate_vessel(self, vessel: VesselData) -> ASMEVIIIValidationResult:
        """
        Validate vessel against ASME VIII Div 1.

        Args:
            vessel: Vessel design data

        Returns:
            Validation result
        """
        result = ASMEVIIIValidationResult()

        self._check_wall_thickness(vessel, result)
        self._check_nozzle_reinforcement(vessel, result)
        self._check_flange_rating(vessel, result)
        self._check_joint_efficiency(vessel, result)
        self._check_hydro_test(vessel, result)
        self._check_mawp(vessel, result)
        self._check_corrosion_allowance(vessel, result)
        self._check_material_traceability(vessel, result)

        return result

    def _get_allowable_stress(self, material: str, temp_f: float) -> Optional[float]:
        """Get allowable stress for material at temperature."""
        if material not in MATERIAL_ALLOWABLE_STRESS:
            return None

        temps = MATERIAL_ALLOWABLE_STRESS[material]
        # Find closest temperature
        temp_keys = sorted(temps.keys())

        for i, t in enumerate(temp_keys):
            if temp_f <= t:
                return temps[t]

        return temps[temp_keys[-1]]  # Use highest if above range

    def _check_wall_thickness(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Check minimum wall thickness per UG-27."""
        result.total_checks += 1

        if not vessel.inside_diameter_in or not vessel.design_pressure_psi:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="wall_thickness_data",
                message="Insufficient data for wall thickness calculation",
                suggestion="Provide inside diameter and design pressure",
                standard_reference="ASME VIII UG-27",
            ))
            return

        S = self._get_allowable_stress(vessel.material, vessel.design_temp_f)
        if not S:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="material_unknown",
                message=f"Material {vessel.material} not in database",
                suggestion="Verify material allowable stress",
            ))
            return

        E = JOINT_EFFICIENCY[vessel.joint_type]
        P = vessel.design_pressure_psi
        R = vessel.inside_diameter_in / 2
        CA = vessel.corrosion_allowance_in

        # UG-27(c)(1) - Circumferential stress (governs for cylinders)
        t_min = (P * R) / (S * E - 0.6 * P) + CA

        result.min_wall_thickness = t_min

        if vessel.wall_thickness_in:
            if vessel.wall_thickness_in >= t_min:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="wall_thickness",
                    message=f"Wall thickness {vessel.wall_thickness_in:.3f}\" ≥ min {t_min:.3f}\"",
                    standard_reference="ASME VIII UG-27",
                ))
            else:
                result.failed += 1
                result.critical_failures += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    check_type="wall_thickness",
                    message=f"Wall thickness {vessel.wall_thickness_in:.3f}\" < min {t_min:.3f}\"",
                    suggestion=f"Increase wall thickness to ≥{t_min:.3f}\"",
                    standard_reference="ASME VIII UG-27",
                ))
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="wall_thickness_calc",
                message=f"Minimum wall thickness = {t_min:.3f}\" (P={P} psi, R={R}\", S={S} ksi, E={E})",
                standard_reference="ASME VIII UG-27",
            ))
            result.passed += 1

    def _check_nozzle_reinforcement(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Check nozzle reinforcement per UG-37."""
        result.total_checks += 1

        if not vessel.nozzle_od_in or not vessel.wall_thickness_in:
            result.passed += 1  # No nozzle to check
            return

        # Simplified check - area replacement method
        # Required reinforcement area = d × tr
        # where d = nozzle diameter, tr = required shell thickness

        if result.min_wall_thickness:
            d = vessel.nozzle_od_in - 2 * (vessel.nozzle_thickness_in or 0)
            A_required = d * result.min_wall_thickness

            # Available area from excess shell thickness
            t_actual = vessel.wall_thickness_in
            t_req = result.min_wall_thickness
            A_shell = d * (t_actual - t_req)

            # Available area from nozzle wall
            if vessel.nozzle_thickness_in:
                A_nozzle = 2 * vessel.nozzle_thickness_in * min(2.5 * t_actual, 2.5 * vessel.nozzle_thickness_in)
            else:
                A_nozzle = 0

            A_available = A_shell + A_nozzle

            result.nozzle_reinforcement_ok = A_available >= A_required

            if A_available >= A_required:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="nozzle_reinforcement",
                    message=f"Nozzle reinforcement OK: Available {A_available:.3f} sq.in ≥ Required {A_required:.3f} sq.in",
                    standard_reference="ASME VIII UG-37",
                ))
            else:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="nozzle_reinforcement",
                    message=f"Nozzle reinforcement insufficient: {A_available:.3f} < {A_required:.3f} sq.in",
                    suggestion="Add reinforcing pad or increase nozzle/shell thickness",
                    standard_reference="ASME VIII UG-37",
                ))
        else:
            result.passed += 1

    def _check_flange_rating(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Check flange rating per ASME B16.5."""
        result.total_checks += 1

        if not vessel.flange_class or not vessel.design_pressure_psi:
            result.passed += 1
            return

        if vessel.flange_class not in FLANGE_RATINGS:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="flange_class",
                message=f"Flange class {vessel.flange_class} not standard",
                suggestion="Use standard class: 150, 300, 600, 900, 1500, 2500",
                standard_reference="ASME B16.5",
            ))
            return

        ratings = FLANGE_RATINGS[vessel.flange_class]

        # Get rating at temperature
        if vessel.design_temp_f <= 100:
            rating = ratings["100F"]
        elif vessel.design_temp_f <= 200:
            rating = ratings["200F"]
        elif vessel.design_temp_f <= 300:
            rating = ratings["300F"]
        else:
            rating = ratings["300F"] * 0.8  # Conservative derating

        if vessel.design_pressure_psi <= rating:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="flange_rating",
                message=f"Class {vessel.flange_class} flange OK: {vessel.design_pressure_psi} psi ≤ {rating} psi at {vessel.design_temp_f}°F",
                standard_reference="ASME B16.5",
            ))
        else:
            result.failed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                check_type="flange_rating",
                message=f"Class {vessel.flange_class} insufficient: {vessel.design_pressure_psi} psi > {rating} psi at {vessel.design_temp_f}°F",
                suggestion=f"Use higher flange class",
                standard_reference="ASME B16.5",
            ))

    def _check_joint_efficiency(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Check weld joint efficiency per UW-12."""
        result.total_checks += 1

        E = JOINT_EFFICIENCY[vessel.joint_type]

        result.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            check_type="joint_efficiency",
            message=f"Joint Type {vessel.joint_type.value}: E = {E} ({'Full RT' if E == 1.0 else 'Spot RT' if E == 0.85 else 'No RT'})",
            standard_reference="ASME VIII UW-12",
        ))

        # Warning if using low efficiency
        if E < 0.85:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="joint_efficiency_low",
                message="Joint efficiency < 0.85 increases required wall thickness",
                suggestion="Consider radiographic examination for E = 1.0",
                standard_reference="ASME VIII UW-12",
            ))

        result.passed += 1

    def _check_hydro_test(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Check hydrostatic test pressure per UG-99."""
        result.total_checks += 1

        if not vessel.design_pressure_psi:
            result.passed += 1
            return

        # UG-99(b): Test pressure = 1.3 × MAWP × (stress ratio)
        # Simplified: 1.3 × design pressure (assuming stress ratio ≈ 1)
        required_hydro = vessel.design_pressure_psi * HYDRO_TEST_FACTOR
        result.required_hydro_pressure = required_hydro

        if vessel.hydro_test_pressure_psi:
            if vessel.hydro_test_pressure_psi >= required_hydro:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="hydro_test",
                    message=f"Hydro test {vessel.hydro_test_pressure_psi} psi ≥ required {required_hydro:.0f} psi",
                    standard_reference="ASME VIII UG-99",
                ))
            else:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="hydro_test",
                    message=f"Hydro test {vessel.hydro_test_pressure_psi} psi < required {required_hydro:.0f} psi",
                    suggestion=f"Increase test pressure to ≥{required_hydro:.0f} psi",
                    standard_reference="ASME VIII UG-99",
                ))
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="hydro_test_calc",
                message=f"Required hydro test pressure = {required_hydro:.0f} psi (1.3 × {vessel.design_pressure_psi} psi)",
                standard_reference="ASME VIII UG-99",
            ))
            result.passed += 1

    def _check_mawp(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Calculate MAWP per UG-98."""
        result.total_checks += 1

        if not vessel.inside_diameter_in or not vessel.wall_thickness_in:
            result.passed += 1
            return

        S = self._get_allowable_stress(vessel.material, vessel.design_temp_f)
        if not S:
            result.passed += 1
            return

        E = JOINT_EFFICIENCY[vessel.joint_type]
        t = vessel.wall_thickness_in - vessel.corrosion_allowance_in
        R = vessel.inside_diameter_in / 2

        # UG-27 rearranged for P
        mawp = (S * E * t) / (R + 0.6 * t)
        result.mawp = mawp

        if vessel.design_pressure_psi:
            if mawp >= vessel.design_pressure_psi:
                result.passed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    check_type="mawp",
                    message=f"MAWP = {mawp:.0f} psi ≥ Design P = {vessel.design_pressure_psi} psi",
                    standard_reference="ASME VIII UG-98",
                ))
            else:
                result.failed += 1
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    check_type="mawp",
                    message=f"MAWP = {mawp:.0f} psi < Design P = {vessel.design_pressure_psi} psi",
                    suggestion="Increase wall thickness or use higher strength material",
                    standard_reference="ASME VIII UG-98",
                ))
        else:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="mawp_calc",
                message=f"Calculated MAWP = {mawp:.0f} psi",
                standard_reference="ASME VIII UG-98",
            ))
            result.passed += 1

    def _check_corrosion_allowance(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Check corrosion allowance per UG-25."""
        result.total_checks += 1

        if vessel.corrosion_allowance_in <= 0:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="corrosion_allowance",
                message="No corrosion allowance specified",
                suggestion="Add corrosion allowance (typical 1/16\" to 1/8\")",
                standard_reference="ASME VIII UG-25",
            ))
        elif vessel.corrosion_allowance_in < 0.0625:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="corrosion_allowance_low",
                message=f"Corrosion allowance {vessel.corrosion_allowance_in}\" may be low",
                suggestion="Typical CA is 1/16\" (0.0625\") minimum",
                standard_reference="ASME VIII UG-25",
            ))
        else:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="corrosion_allowance",
                message=f"Corrosion allowance = {vessel.corrosion_allowance_in}\"",
                standard_reference="ASME VIII UG-25",
            ))

    def _check_material_traceability(self, vessel: VesselData, result: ASMEVIIIValidationResult):
        """Check material traceability per UG-93."""
        result.total_checks += 1

        if vessel.has_mtr:
            result.passed += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                check_type="material_traceability",
                message="Material Test Report (MTR) available",
                standard_reference="ASME VIII UG-93",
            ))
        else:
            result.warnings += 1
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                check_type="material_traceability",
                message="Material Test Report (MTR) not confirmed",
                suggestion="Ensure MTR available per UG-93",
                standard_reference="ASME VIII UG-93",
            ))

    def to_dict(self, result: ASMEVIIIValidationResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "validator": "asme_viii",
            "total_checks": result.total_checks,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "critical_failures": result.critical_failures,
            "calculations": {
                "min_wall_thickness_in": result.min_wall_thickness,
                "mawp_psi": result.mawp,
                "required_hydro_psi": result.required_hydro_pressure,
                "nozzle_reinforcement_ok": result.nozzle_reinforcement_ok,
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
