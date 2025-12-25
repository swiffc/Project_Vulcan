"""
Thermal & Pressure Analyzer
===========================
Analyze thermal expansion and pressure-related calculations.

Phase 24.14 Implementation
"""

import logging
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.analyzer.thermal")


# Thermal expansion coefficients (in/in/°F × 10^-6)
THERMAL_EXPANSION_COEFFICIENTS = {
    "carbon_steel": 6.5,
    "stainless_304": 9.6,
    "stainless_316": 8.9,
    "aluminum": 12.8,
    "copper": 9.3,
    "brass": 10.4,
    "inconel_600": 7.4,
    "monel_400": 7.7,
    "titanium": 4.8,
}


@dataclass
class ThermalExpansionResult:
    """Thermal expansion calculation result."""
    material: str = ""
    initial_temp_f: float = 70.0
    design_temp_f: float = 300.0
    original_length_in: float = 0.0
    expansion_in: float = 0.0
    final_length_in: float = 0.0
    coefficient: float = 0.0


@dataclass
class ThermalAnalysisResult:
    """Complete thermal analysis results."""
    tube_expansion: Optional[ThermalExpansionResult] = None
    shell_expansion: Optional[ThermalExpansionResult] = None
    differential_expansion_in: float = 0.0
    pwht_required: bool = False
    pwht_reason: str = ""
    thermal_stress_notes: List[str] = field(default_factory=list)
    sliding_support_required: bool = False


class ThermalAnalyzer:
    """
    Analyze thermal expansion and related calculations.
    """

    # ASME VIII PWHT requirements (simplified)
    PWHT_THICKNESS_THRESHOLD_IN = {
        "P-1": 1.25,  # Carbon steel
        "P-3": 0.625,  # Alloy steel
        "P-4": 0.5,   # Cr-Mo
    }

    def __init__(self):
        pass

    def get_expansion_coefficient(self, material: str) -> float:
        """Get thermal expansion coefficient for material."""
        mat_lower = material.lower()

        if "stainless" in mat_lower and "316" in mat_lower:
            return THERMAL_EXPANSION_COEFFICIENTS["stainless_316"]
        elif "stainless" in mat_lower:
            return THERMAL_EXPANSION_COEFFICIENTS["stainless_304"]
        elif "aluminum" in mat_lower:
            return THERMAL_EXPANSION_COEFFICIENTS["aluminum"]
        elif "inconel" in mat_lower:
            return THERMAL_EXPANSION_COEFFICIENTS["inconel_600"]
        elif "monel" in mat_lower:
            return THERMAL_EXPANSION_COEFFICIENTS["monel_400"]
        elif "titanium" in mat_lower:
            return THERMAL_EXPANSION_COEFFICIENTS["titanium"]
        elif "copper" in mat_lower:
            return THERMAL_EXPANSION_COEFFICIENTS["copper"]
        else:
            return THERMAL_EXPANSION_COEFFICIENTS["carbon_steel"]

    def calc_thermal_expansion(
        self,
        material: str,
        length_in: float,
        initial_temp_f: float = 70.0,
        design_temp_f: float = 300.0,
    ) -> ThermalExpansionResult:
        """
        Calculate thermal expansion.

        ΔL = L × α × ΔT
        """
        result = ThermalExpansionResult()
        result.material = material
        result.initial_temp_f = initial_temp_f
        result.design_temp_f = design_temp_f
        result.original_length_in = length_in

        # Get coefficient (in/in/°F × 10^-6)
        alpha = self.get_expansion_coefficient(material)
        result.coefficient = alpha

        # Calculate expansion
        delta_t = design_temp_f - initial_temp_f
        result.expansion_in = length_in * (alpha * 1e-6) * delta_t
        result.final_length_in = length_in + result.expansion_in

        return result

    def check_pwht_required(
        self,
        material_pnum: str,
        thickness_in: float,
    ) -> tuple:
        """
        Check if PWHT is required per ASME VIII.

        Returns (required: bool, reason: str)
        """
        threshold = self.PWHT_THICKNESS_THRESHOLD_IN.get(material_pnum, 1.25)

        if thickness_in > threshold:
            return True, f"Thickness {thickness_in}\" exceeds {material_pnum} threshold of {threshold}\""

        return False, ""

    def analyze(
        self,
        tube_material: str = "carbon_steel",
        tube_length_in: float = 240.0,
        shell_material: str = "carbon_steel",
        shell_length_in: float = 240.0,
        design_temp_f: float = 300.0,
        ambient_temp_f: float = 70.0,
        material_pnum: str = "P-1",
        max_thickness_in: float = 1.0,
    ) -> ThermalAnalysisResult:
        """Perform complete thermal analysis."""
        result = ThermalAnalysisResult()

        # Calculate tube expansion
        result.tube_expansion = self.calc_thermal_expansion(
            tube_material, tube_length_in, ambient_temp_f, design_temp_f
        )

        # Calculate shell expansion
        result.shell_expansion = self.calc_thermal_expansion(
            shell_material, shell_length_in, ambient_temp_f, design_temp_f
        )

        # Calculate differential expansion
        result.differential_expansion_in = abs(
            result.tube_expansion.expansion_in - result.shell_expansion.expansion_in
        )

        # Check if sliding support needed (differential > 0.25")
        if result.differential_expansion_in > 0.25:
            result.sliding_support_required = True
            result.thermal_stress_notes.append(
                f"Differential expansion of {result.differential_expansion_in:.3f}\" "
                f"requires sliding support or expansion allowance"
            )

        # Check PWHT requirement
        result.pwht_required, result.pwht_reason = self.check_pwht_required(
            material_pnum, max_thickness_in
        )
        if result.pwht_required:
            result.thermal_stress_notes.append(f"PWHT required: {result.pwht_reason}")

        # Add thermal cycling note if high temperature
        if design_temp_f > 500:
            result.thermal_stress_notes.append(
                "High temperature service - consider thermal cycling fatigue"
            )

        return result

    def to_dict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and return results as dictionary."""
        result = self.analyze(
            tube_material=inputs.get("tube_material", "carbon_steel"),
            tube_length_in=inputs.get("tube_length_in", 240.0),
            shell_material=inputs.get("shell_material", "carbon_steel"),
            shell_length_in=inputs.get("shell_length_in", 240.0),
            design_temp_f=inputs.get("design_temp_f", 300.0),
            ambient_temp_f=inputs.get("ambient_temp_f", 70.0),
            material_pnum=inputs.get("material_pnum", "P-1"),
            max_thickness_in=inputs.get("max_thickness_in", 1.0),
        )

        return {
            "tube_expansion": {
                "material": result.tube_expansion.material,
                "original_length_in": result.tube_expansion.original_length_in,
                "expansion_in": round(result.tube_expansion.expansion_in, 4),
                "final_length_in": round(result.tube_expansion.final_length_in, 4),
                "coefficient": result.tube_expansion.coefficient,
            } if result.tube_expansion else None,
            "shell_expansion": {
                "material": result.shell_expansion.material,
                "original_length_in": result.shell_expansion.original_length_in,
                "expansion_in": round(result.shell_expansion.expansion_in, 4),
                "final_length_in": round(result.shell_expansion.final_length_in, 4),
            } if result.shell_expansion else None,
            "differential_expansion_in": round(result.differential_expansion_in, 4),
            "sliding_support_required": result.sliding_support_required,
            "pwht_required": result.pwht_required,
            "pwht_reason": result.pwht_reason,
            "thermal_stress_notes": result.thermal_stress_notes,
        }
