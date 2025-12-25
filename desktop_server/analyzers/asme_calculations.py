"""
ASME VIII Div 1 Calculations
============================
Pressure vessel calculations per ASME VIII Division 1.

Phase 24.13 Implementation
"""

import math
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("vulcan.analyzer.asme")


@dataclass
class MaterialAllowable:
    """Material allowable stress data."""
    spec: str = ""
    grade: str = ""
    allowable_stress_psi: float = 0.0
    yield_strength_psi: float = 0.0
    tensile_strength_psi: float = 0.0


# Common materials for ACHE (simplified table)
MATERIAL_ALLOWABLES = {
    "SA-516-70": MaterialAllowable("SA-516", "70", 20000, 38000, 70000),
    "SA-516-60": MaterialAllowable("SA-516", "60", 17100, 32000, 60000),
    "SA-240-304": MaterialAllowable("SA-240", "304", 20000, 30000, 75000),
    "SA-240-316": MaterialAllowable("SA-240", "316", 20000, 30000, 75000),
    "SA-106-B": MaterialAllowable("SA-106", "B", 17100, 35000, 60000),
    "SA-105": MaterialAllowable("SA-105", "N/A", 17100, 36000, 70000),
}


class ASMECalculator:
    """
    ASME VIII Division 1 pressure vessel calculations.
    Implements UG-27, UG-32, UG-34, UG-37, UG-40.
    """

    def __init__(self):
        pass

    def get_allowable_stress(self, material: str) -> float:
        """Get allowable stress for material (psi)."""
        mat = MATERIAL_ALLOWABLES.get(material.upper())
        if mat:
            return mat.allowable_stress_psi
        logger.warning(f"Material {material} not in database, using default 17100 psi")
        return 17100.0

    def calc_shell_thickness_ug27(
        self,
        pressure_psi: float,
        inside_radius_in: float,
        allowable_stress_psi: float,
        joint_efficiency: float = 1.0,
        corrosion_allowance_in: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculate shell thickness per UG-27 (Cylindrical Shells).

        t = (P * R) / (S * E - 0.6 * P) + CA

        Args:
            pressure_psi: Design pressure (psi)
            inside_radius_in: Inside radius (inches)
            allowable_stress_psi: Allowable stress (psi)
            joint_efficiency: Weld joint efficiency (0.0-1.0)
            corrosion_allowance_in: Corrosion allowance (inches)

        Returns:
            Dict with calculated and required thicknesses
        """
        S = allowable_stress_psi
        E = joint_efficiency
        P = pressure_psi
        R = inside_radius_in
        CA = corrosion_allowance_in

        # UG-27(c)(1) - Circumferential stress formula
        t_calc = (P * R) / (S * E - 0.6 * P)
        t_required = t_calc + CA

        return {
            "formula": "UG-27(c)(1)",
            "calculated_thickness_in": round(t_calc, 4),
            "required_thickness_in": round(t_required, 4),
            "corrosion_allowance_in": CA,
        }

    def calc_head_thickness_ug32(
        self,
        pressure_psi: float,
        inside_diameter_in: float,
        allowable_stress_psi: float,
        joint_efficiency: float = 1.0,
        corrosion_allowance_in: float = 0.0,
        head_type: str = "2:1_ellipsoidal",
    ) -> Dict[str, float]:
        """
        Calculate head thickness per UG-32 (Formed Heads).

        For 2:1 Ellipsoidal (UG-32(d)):
            t = (P * D) / (2 * S * E - 0.2 * P) + CA

        Args:
            head_type: "2:1_ellipsoidal", "hemispherical", "torispherical"
        """
        S = allowable_stress_psi
        E = joint_efficiency
        P = pressure_psi
        D = inside_diameter_in
        CA = corrosion_allowance_in

        if head_type == "2:1_ellipsoidal":
            # UG-32(d)
            t_calc = (P * D) / (2 * S * E - 0.2 * P)
            formula = "UG-32(d)"
        elif head_type == "hemispherical":
            # UG-32(f)
            t_calc = (P * D) / (4 * S * E - 0.4 * P)
            formula = "UG-32(f)"
        else:
            # Torispherical (simplified)
            L = D  # Crown radius = diameter for standard
            t_calc = (0.885 * P * L) / (S * E - 0.1 * P)
            formula = "UG-32(e)"

        t_required = t_calc + CA

        return {
            "formula": formula,
            "head_type": head_type,
            "calculated_thickness_in": round(t_calc, 4),
            "required_thickness_in": round(t_required, 4),
        }

    def calc_tubesheet_thickness_ug34(
        self,
        pressure_psi: float,
        diameter_in: float,
        allowable_stress_psi: float,
        attachment_factor: float = 0.5,
        ligament_efficiency: float = 0.5,
    ) -> Dict[str, float]:
        """
        Calculate tubesheet thickness per UG-34 (Unstayed Flat Heads).

        t = d * sqrt(C * P / (S * E))

        Args:
            attachment_factor: C value (0.17 to 0.50 per table)
            ligament_efficiency: E for perforated plate
        """
        S = allowable_stress_psi
        E = ligament_efficiency
        P = pressure_psi
        d = diameter_in
        C = attachment_factor

        t_calc = d * math.sqrt(C * P / (S * E))

        return {
            "formula": "UG-34(c)(2)",
            "calculated_thickness_in": round(t_calc, 4),
            "attachment_factor_C": C,
            "ligament_efficiency": E,
        }

    def calc_nozzle_reinforcement_ug37(
        self,
        shell_thickness_in: float,
        nozzle_od_in: float,
        nozzle_thickness_in: float,
        nozzle_projection_in: float,
        pressure_psi: float,
        allowable_stress_psi: float,
        corrosion_allowance_in: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculate nozzle reinforcement per UG-37/UG-40.

        A (required) = d * tr * F
        A (available) = A1 + A2 + A3 + A4 + A5
        """
        CA = corrosion_allowance_in
        S = allowable_stress_psi
        P = pressure_psi

        # Required thickness of shell (simplified)
        R = (nozzle_od_in - 2 * nozzle_thickness_in) / 2
        tr = (P * R) / (S - 0.6 * P)

        # Finished opening diameter
        d = nozzle_od_in - 2 * (nozzle_thickness_in - CA)

        # Area required (UG-37)
        F = 1.0  # Correction factor
        A_required = d * tr * F

        # Available areas (simplified)
        # A1 = Excess shell metal
        t_shell = shell_thickness_in - CA
        A1 = (t_shell - tr) * d

        # A2 = Excess nozzle metal (outward)
        t_nozzle = nozzle_thickness_in - CA
        trn = (P * R) / (S - 0.6 * P)
        h = min(nozzle_projection_in, 2.5 * t_shell)
        A2 = 2 * h * (t_nozzle - trn)

        # Total available
        A_available = A1 + A2

        # Pad required?
        reinforcement_adequate = A_available >= A_required
        pad_area_needed = max(0, A_required - A_available)

        return {
            "formula": "UG-37/UG-40",
            "area_required_in2": round(A_required, 4),
            "area_available_in2": round(A_available, 4),
            "A1_shell_excess_in2": round(A1, 4),
            "A2_nozzle_excess_in2": round(A2, 4),
            "reinforcement_adequate": reinforcement_adequate,
            "pad_area_needed_in2": round(pad_area_needed, 4),
        }

    def calc_mawp(
        self,
        actual_thickness_in: float,
        inside_radius_in: float,
        allowable_stress_psi: float,
        joint_efficiency: float = 1.0,
        corrosion_allowance_in: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculate Maximum Allowable Working Pressure per UG-27.

        P = (S * E * t) / (R + 0.6 * t)
        """
        S = allowable_stress_psi
        E = joint_efficiency
        t = actual_thickness_in - corrosion_allowance_in
        R = inside_radius_in

        mawp = (S * E * t) / (R + 0.6 * t)

        return {
            "mawp_psi": round(mawp, 1),
            "mawp_bar": round(mawp / 14.5038, 2),
            "corroded_thickness_in": round(t, 4),
        }

    def calc_hydro_test_pressure(
        self,
        mawp_psi: float,
        test_type: str = "standard",
    ) -> Dict[str, float]:
        """
        Calculate hydrostatic test pressure.

        Standard: 1.3 × MAWP (per UG-99)
        Pneumatic: 1.1 × MAWP (per UG-100)
        """
        if test_type == "pneumatic":
            factor = 1.1
        else:
            factor = 1.3

        test_pressure = mawp_psi * factor

        return {
            "test_type": test_type,
            "factor": factor,
            "test_pressure_psi": round(test_pressure, 1),
            "test_pressure_bar": round(test_pressure / 14.5038, 2),
        }

    def to_dict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run calculations based on inputs and return all results."""
        results = {}

        # Get material allowable
        material = inputs.get("material", "SA-516-70")
        S = self.get_allowable_stress(material)
        results["material"] = material
        results["allowable_stress_psi"] = S

        # Shell calculation if applicable
        if "shell_inside_radius_in" in inputs:
            results["shell"] = self.calc_shell_thickness_ug27(
                pressure_psi=inputs.get("design_pressure_psi", 150),
                inside_radius_in=inputs["shell_inside_radius_in"],
                allowable_stress_psi=S,
                joint_efficiency=inputs.get("joint_efficiency", 0.85),
                corrosion_allowance_in=inputs.get("corrosion_allowance_in", 0.0625),
            )

        # Head calculation if applicable
        if "head_inside_diameter_in" in inputs:
            results["head"] = self.calc_head_thickness_ug32(
                pressure_psi=inputs.get("design_pressure_psi", 150),
                inside_diameter_in=inputs["head_inside_diameter_in"],
                allowable_stress_psi=S,
                joint_efficiency=inputs.get("joint_efficiency", 0.85),
                head_type=inputs.get("head_type", "2:1_ellipsoidal"),
            )

        # Tubesheet calculation if applicable
        if "tubesheet_diameter_in" in inputs:
            results["tubesheet"] = self.calc_tubesheet_thickness_ug34(
                pressure_psi=inputs.get("design_pressure_psi", 150),
                diameter_in=inputs["tubesheet_diameter_in"],
                allowable_stress_psi=S,
                ligament_efficiency=inputs.get("ligament_efficiency", 0.5),
            )

        return results
