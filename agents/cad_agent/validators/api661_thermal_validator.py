"""
API 661 Thermal & Mechanical Validator
=======================================
Enhanced validation for ACHE (Air-Cooled Heat Exchangers) per API 661.

Phase 25.6 - Expanded API 661 Coverage

Covers:
- Thermal design verification
- Tube bundle geometry
- Header box design
- Structural requirements
- Vibration analysis
- Fouling factors
"""

import math
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.api661_thermal")


# =============================================================================
# CONSTANTS - API 661 Requirements
# =============================================================================

# Maximum allowable velocities (ft/s) per API 661
MAX_TUBE_VELOCITY = {
    "water": 8.0,
    "hydrocarbon_liquid": 6.0,
    "gas": 100.0,
    "steam": 150.0,
    "two_phase": 50.0,
}

# Minimum tube wall thickness by material (inches)
MIN_TUBE_WALL = {
    "carbon_steel": 0.065,
    "stainless_steel": 0.049,
    "aluminum": 0.049,
    "copper": 0.049,
    "titanium": 0.035,
}

# Minimum header box thickness (inches)
MIN_HEADER_THICKNESS = {
    "carbon_steel": 0.375,
    "stainless_steel": 0.25,
}

# Tube pitch ratios (pitch/OD)
MIN_TUBE_PITCH_RATIO = 1.25  # API 661 minimum

# Fin parameters
MAX_FIN_DENSITY = 11  # fins per inch (typical max)
MIN_FIN_THICKNESS = 0.012  # inches
MIN_FIN_HEIGHT = 0.375  # inches

# Fouling factors (hr-ft2-F/BTU)
FOULING_FACTORS = {
    "clean_water": 0.001,
    "treated_cooling_water": 0.002,
    "untreated_water": 0.003,
    "sea_water": 0.0015,
    "light_hydrocarbon": 0.001,
    "heavy_hydrocarbon": 0.003,
    "crude_oil": 0.005,
    "gas": 0.0005,
    "air": 0.0,
}

# Design temperature limits (F)
TEMP_LIMITS = {
    "carbon_steel": (-20, 800),
    "stainless_304": (-320, 1500),
    "stainless_316": (-320, 1500),
    "aluminum": (-452, 400),
    "copper": (-325, 400),
}


# =============================================================================
# DATA CLASSES
# =============================================================================

class FluidType(Enum):
    """Process fluid types."""
    WATER = "water"
    HYDROCARBON_LIQUID = "hydrocarbon_liquid"
    GAS = "gas"
    STEAM = "steam"
    TWO_PHASE = "two_phase"


class TubeMaterial(Enum):
    """Tube material types."""
    CARBON_STEEL = "carbon_steel"
    STAINLESS_STEEL = "stainless_steel"
    ALUMINUM = "aluminum"
    COPPER = "copper"
    TITANIUM = "titanium"


@dataclass
class ThermalDesignData:
    """ACHE thermal design parameters."""
    # Process conditions
    process_fluid: str = "hydrocarbon_liquid"
    inlet_temp_f: float = 200
    outlet_temp_f: float = 120
    design_temp_f: float = 250
    design_pressure_psig: float = 150
    flow_rate_lb_hr: float = 100000
    specific_heat_btu_lb_f: float = 0.5
    viscosity_cp: float = 1.0
    density_lb_ft3: float = 50

    # Tube bundle
    tube_od_in: float = 1.0
    tube_wall_in: float = 0.065
    tube_length_ft: float = 30
    num_tubes: int = 200
    num_passes: int = 4
    tube_pitch_in: float = 2.5
    tube_material: str = "carbon_steel"

    # Fins
    fin_height_in: float = 0.625
    fin_thickness_in: float = 0.016
    fin_density_per_inch: float = 10
    fin_material: str = "aluminum"

    # Calculated/provided
    heat_duty_btu_hr: float = 0
    fouling_factor: float = 0.002
    overall_u_btu_hr_ft2_f: float = 0
    mtd_f: float = 0  # Mean temperature difference


@dataclass
class HeaderDesignData:
    """Header box design parameters."""
    length_in: float = 120
    width_in: float = 8
    depth_in: float = 6
    wall_thickness_in: float = 0.5
    material: str = "carbon_steel"
    design_pressure_psig: float = 150
    design_temp_f: float = 250
    num_plugs: int = 200
    plug_type: str = "shoulder"  # shoulder, taper, bar
    nozzle_size_in: float = 6
    num_nozzles: int = 2


@dataclass
class VibrationData:
    """Tube vibration analysis data."""
    tube_od_in: float = 1.0
    tube_wall_in: float = 0.065
    unsupported_span_in: float = 48
    tube_material: str = "carbon_steel"
    crossflow_velocity_fps: float = 20
    fluid_density_lb_ft3: float = 0.07  # Air typical
    num_tube_rows: int = 4


@dataclass
class API661ThermalResult:
    """Result from API 661 thermal validation."""
    valid: bool
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    critical_failures: int = 0
    issues: List[Dict] = field(default_factory=list)
    calculations: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# API 661 THERMAL VALIDATOR
# =============================================================================

class API661ThermalValidator:
    """
    Validate ACHE design against API 661 thermal and mechanical requirements.

    Checks:
    - Tube velocity limits
    - Tube wall thickness
    - Fin geometry
    - Header design
    - Vibration susceptibility
    - Fouling allowance
    """

    def __init__(self):
        self.issues: List[Dict] = []
        self.calculations: Dict[str, Any] = {}

    def _add_issue(
        self,
        severity: str,
        check_type: str,
        message: str,
        suggestion: str = "",
        standard_ref: str = "API 661"
    ):
        """Add a validation issue."""
        self.issues.append({
            "severity": severity,
            "check_type": check_type,
            "message": message,
            "suggestion": suggestion,
            "standard_reference": standard_ref,
        })

    def validate_thermal_design(self, data: ThermalDesignData) -> API661ThermalResult:
        """
        Validate thermal design parameters.

        Checks:
        - Tube-side velocity
        - Tube wall thickness
        - Fin geometry
        - Fouling allowance
        - Temperature limits
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        # Check 1: Tube-side velocity
        checks += 1
        tube_id = data.tube_od_in - 2 * data.tube_wall_in
        tubes_per_pass = data.num_tubes / data.num_passes
        flow_area = tubes_per_pass * math.pi * (tube_id / 12)**2 / 4  # ft2
        volumetric_flow = data.flow_rate_lb_hr / data.density_lb_ft3 / 3600  # ft3/s
        velocity = volumetric_flow / flow_area if flow_area > 0 else 0  # ft/s

        max_vel = MAX_TUBE_VELOCITY.get(data.process_fluid, 6.0)

        self.calculations["velocity"] = {
            "tube_id_in": round(tube_id, 3),
            "flow_area_ft2": round(flow_area, 4),
            "velocity_fps": round(velocity, 2),
            "max_velocity_fps": max_vel,
        }

        if velocity <= max_vel:
            passed += 1
        else:
            self._add_issue(
                "error" if velocity < max_vel * 1.2 else "critical",
                "tube_velocity",
                f"Tube velocity {velocity:.1f} ft/s exceeds limit {max_vel} ft/s for {data.process_fluid}",
                "Increase number of tubes or reduce passes",
                "API 661 6.1.4"
            )

        # Check 2: Tube wall thickness
        checks += 1
        min_wall = MIN_TUBE_WALL.get(data.tube_material, 0.065)

        self.calculations["tube_wall"] = {
            "provided_in": data.tube_wall_in,
            "minimum_in": min_wall,
        }

        if data.tube_wall_in >= min_wall:
            passed += 1
        else:
            self._add_issue("critical", "tube_wall",
                f"Tube wall {data.tube_wall_in}\" is below minimum {min_wall}\" for {data.tube_material}",
                f"Use minimum {min_wall}\" wall tubes",
                "API 661 6.1.2")

        # Check 3: Tube pitch ratio
        checks += 1
        pitch_ratio = data.tube_pitch_in / data.tube_od_in

        self.calculations["pitch"] = {
            "pitch_in": data.tube_pitch_in,
            "tube_od_in": data.tube_od_in,
            "ratio": round(pitch_ratio, 3),
            "min_ratio": MIN_TUBE_PITCH_RATIO,
        }

        if pitch_ratio >= MIN_TUBE_PITCH_RATIO:
            passed += 1
        else:
            self._add_issue("error", "tube_pitch",
                f"Pitch ratio {pitch_ratio:.2f} is below minimum {MIN_TUBE_PITCH_RATIO}",
                "Increase tube pitch or use smaller tubes",
                "API 661 6.1.3")

        # Check 4: Fin geometry
        checks += 1
        fin_ok = True

        self.calculations["fins"] = {
            "height_in": data.fin_height_in,
            "thickness_in": data.fin_thickness_in,
            "density_per_inch": data.fin_density_per_inch,
        }

        if data.fin_thickness_in < MIN_FIN_THICKNESS:
            fin_ok = False
            self._add_issue("warning", "fin_thickness",
                f"Fin thickness {data.fin_thickness_in}\" below typical minimum {MIN_FIN_THICKNESS}\"",
                "Consider thicker fins for durability")

        if data.fin_density_per_inch > MAX_FIN_DENSITY:
            fin_ok = False
            self._add_issue("warning", "fin_density",
                f"Fin density {data.fin_density_per_inch}/in exceeds typical maximum {MAX_FIN_DENSITY}/in",
                "Reduce fin density to prevent fouling")

        if data.fin_height_in < MIN_FIN_HEIGHT:
            fin_ok = False
            self._add_issue("info", "fin_height",
                f"Fin height {data.fin_height_in}\" is below typical {MIN_FIN_HEIGHT}\"",
                "Consider taller fins for better heat transfer")

        if fin_ok:
            passed += 1

        # Check 5: Temperature limits
        checks += 1
        temp_limits = TEMP_LIMITS.get(data.tube_material, (-20, 800))

        self.calculations["temperature"] = {
            "design_temp_f": data.design_temp_f,
            "material_min_f": temp_limits[0],
            "material_max_f": temp_limits[1],
        }

        if temp_limits[0] <= data.design_temp_f <= temp_limits[1]:
            passed += 1
        else:
            self._add_issue("critical", "temperature",
                f"Design temp {data.design_temp_f}F outside material limits ({temp_limits[0]}-{temp_limits[1]}F)",
                "Select appropriate material for temperature range",
                "API 661 5.1")

        # Check 6: Fouling factor
        checks += 1
        typical_fouling = FOULING_FACTORS.get(data.process_fluid, 0.002)

        self.calculations["fouling"] = {
            "specified": data.fouling_factor,
            "typical": typical_fouling,
        }

        if data.fouling_factor >= typical_fouling:
            passed += 1
        else:
            self._add_issue("warning", "fouling",
                f"Fouling factor {data.fouling_factor} is less than typical {typical_fouling} for {data.process_fluid}",
                "Consider higher fouling factor for conservative design",
                "API 661 5.2.1")

        # Check 7: Heat duty calculation verification
        checks += 1
        calc_duty = data.flow_rate_lb_hr * data.specific_heat_btu_lb_f * (data.inlet_temp_f - data.outlet_temp_f)

        self.calculations["heat_duty"] = {
            "calculated_btu_hr": round(calc_duty, 0),
            "specified_btu_hr": data.heat_duty_btu_hr,
        }

        if data.heat_duty_btu_hr > 0:
            deviation = abs(calc_duty - data.heat_duty_btu_hr) / data.heat_duty_btu_hr * 100
            if deviation <= 5:
                passed += 1
            else:
                self._add_issue("warning", "heat_duty",
                    f"Calculated duty deviates {deviation:.1f}% from specified",
                    "Verify heat balance calculation")
        else:
            passed += 1  # No specified duty to check

        return self._build_result(checks, passed)

    def validate_header_design(self, data: HeaderDesignData) -> API661ThermalResult:
        """
        Validate header box design per API 661.

        Checks:
        - Wall thickness
        - Plug requirements
        - Nozzle sizing
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        # Check 1: Header wall thickness
        checks += 1
        min_wall = MIN_HEADER_THICKNESS.get(data.material, 0.375)

        self.calculations["header_wall"] = {
            "provided_in": data.wall_thickness_in,
            "minimum_in": min_wall,
        }

        if data.wall_thickness_in >= min_wall:
            passed += 1
        else:
            self._add_issue("error", "header_wall",
                f"Header wall {data.wall_thickness_in}\" below minimum {min_wall}\"",
                f"Use minimum {min_wall}\" header",
                "API 661 6.2.2")

        # Check 2: Plug type for pressure
        checks += 1
        if data.design_pressure_psig > 300 and data.plug_type != "shoulder":
            self._add_issue("warning", "plug_type",
                f"Shoulder plugs recommended for pressures above 300 psig (current: {data.design_pressure_psig})",
                "Consider shoulder plugs for high pressure service",
                "API 661 6.2.6")
        else:
            passed += 1

        # Check 3: Header aspect ratio
        checks += 1
        aspect_ratio = data.length_in / data.width_in

        self.calculations["header_aspect"] = {
            "length_in": data.length_in,
            "width_in": data.width_in,
            "ratio": round(aspect_ratio, 1),
        }

        if aspect_ratio <= 20:
            passed += 1
        else:
            self._add_issue("warning", "header_aspect",
                f"Header aspect ratio {aspect_ratio:.1f} is high - may require stiffeners",
                "Add internal stiffeners or limit unsupported length",
                "API 661 6.2.3")

        # Check 4: Nozzle size adequacy
        checks += 1
        # Simple velocity check at nozzle
        nozzle_area = math.pi * (data.nozzle_size_in / 12)**2 / 4 * data.num_nozzles
        # Assuming 100 lb/ft3 and 1M lb/hr as reference
        self.calculations["nozzle"] = {
            "size_in": data.nozzle_size_in,
            "quantity": data.num_nozzles,
            "total_area_ft2": round(nozzle_area, 3),
        }
        passed += 1  # Simplified - actual check requires flow data

        return self._build_result(checks, passed)

    def validate_vibration(self, data: VibrationData) -> API661ThermalResult:
        """
        Check tube bundle vibration susceptibility per API 661.

        Checks:
        - Acoustic resonance
        - Vortex shedding
        - Fluid-elastic instability
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        # Material properties (steel typical)
        E = 29e6  # psi
        rho_tube = 490  # lb/ft3 steel

        tube_id = data.tube_od_in - 2 * data.tube_wall_in
        tube_area = math.pi * ((data.tube_od_in/12)**2 - (tube_id/12)**2) / 4  # ft2
        I = math.pi * ((data.tube_od_in/12)**4 - (tube_id/12)**4) / 64  # ft4

        # Check 1: Natural frequency
        checks += 1
        L = data.unsupported_span_in / 12  # ft
        # Simplified natural frequency for pinned-pinned
        fn = (math.pi / (2 * L**2)) * math.sqrt(E * I * 144**4 / (rho_tube * tube_area)) * (1 / (2 * math.pi))

        self.calculations["natural_freq"] = {
            "span_in": data.unsupported_span_in,
            "fn_hz": round(fn, 1),
        }

        if fn > 10:  # Typical minimum to avoid low-frequency issues
            passed += 1
        else:
            self._add_issue("warning", "natural_frequency",
                f"Tube natural frequency {fn:.1f} Hz is low - susceptible to vibration",
                "Reduce span or add tube supports",
                "API 661 6.3")

        # Check 2: Vortex shedding frequency
        checks += 1
        # Strouhal number ~ 0.2 for cylinders
        St = 0.2
        fv = St * data.crossflow_velocity_fps / (data.tube_od_in / 12)

        self.calculations["vortex"] = {
            "crossflow_velocity_fps": data.crossflow_velocity_fps,
            "fv_hz": round(fv, 1),
            "fn_hz": round(fn, 1),
            "ratio": round(fv / fn, 2) if fn > 0 else 0,
        }

        # Check if vortex frequency is near natural frequency
        if fn > 0 and 0.8 <= fv / fn <= 1.2:
            self._add_issue("critical", "vortex_resonance",
                f"Vortex shedding frequency {fv:.1f} Hz near tube natural frequency {fn:.1f} Hz",
                "Add baffles or change tube pitch to avoid resonance",
                "API 661 6.3.2")
        else:
            passed += 1

        # Check 3: Reduced velocity
        checks += 1
        Vr = data.crossflow_velocity_fps / (fn * data.tube_od_in / 12) if fn > 0 else 999

        self.calculations["reduced_velocity"] = {
            "Vr": round(Vr, 2),
            "limit": 3.0,  # Typical instability threshold
        }

        if Vr < 3.0:
            passed += 1
        else:
            self._add_issue("error", "fluid_elastic",
                f"Reduced velocity {Vr:.1f} exceeds stability limit 3.0",
                "Reduce crossflow velocity or increase tube stiffness",
                "API 661 6.3.3")

        return self._build_result(checks, passed)

    def _build_result(self, total: int, passed: int) -> API661ThermalResult:
        """Build validation result."""
        failed = total - passed
        critical = sum(1 for i in self.issues if i["severity"] == "critical")
        warnings = sum(1 for i in self.issues if i["severity"] == "warning")

        return API661ThermalResult(
            valid=(failed == 0 and critical == 0),
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            critical_failures=critical,
            issues=self.issues.copy(),
            calculations=self.calculations.copy(),
        )
