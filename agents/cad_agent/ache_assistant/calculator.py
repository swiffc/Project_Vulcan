"""
ACHE Calculator Module
Phase 24.4 - Engineering Calculations for Air Cooled Heat Exchangers

Implements API 661 / ISO 13706 calculations:
- Thermal performance (LMTD, NTU-effectiveness)
- Pressure drop (tube-side and air-side)
- Fan power requirements
- Heat transfer coefficients
"""

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger("vulcan.ache.calculator")


class FluidType(Enum):
    """Process fluid types."""
    LIQUID = "liquid"
    GAS = "gas"
    TWO_PHASE = "two_phase"
    CONDENSING = "condensing"
    BOILING = "boiling"


class FlowArrangement(Enum):
    """Heat exchanger flow arrangements."""
    COUNTERFLOW = "counterflow"
    PARALLEL = "parallel"
    CROSSFLOW = "crossflow"
    CROSSFLOW_MIXED = "crossflow_mixed"
    CROSSFLOW_UNMIXED = "crossflow_unmixed"


@dataclass
class FluidProperties:
    """Thermophysical properties of a fluid."""
    density_kg_m3: float = 1.0
    specific_heat_j_kg_k: float = 1000.0
    viscosity_pa_s: float = 0.001
    thermal_conductivity_w_m_k: float = 0.6
    prandtl_number: float = 7.0

    @classmethod
    def air_at_temperature(cls, temp_c: float) -> "FluidProperties":
        """Get air properties at given temperature."""
        # Simplified correlations for air
        temp_k = temp_c + 273.15
        density = 101325 / (287.05 * temp_k)  # Ideal gas
        cp = 1006.0  # J/kg-K (nearly constant)
        # Sutherland's formula for viscosity
        mu = 1.458e-6 * (temp_k ** 1.5) / (temp_k + 110.4)
        k = 0.0241 * (temp_k / 273.15) ** 0.81  # W/m-K
        pr = mu * cp / k

        return cls(
            density_kg_m3=density,
            specific_heat_j_kg_k=cp,
            viscosity_pa_s=mu,
            thermal_conductivity_w_m_k=k,
            prandtl_number=pr,
        )


@dataclass
class ThermalResults:
    """Results of thermal performance calculations."""
    duty_kw: float = 0.0
    lmtd_k: float = 0.0
    lmtd_correction_factor: float = 1.0
    overall_u_w_m2_k: float = 0.0
    effectiveness: float = 0.0
    ntu: float = 0.0
    air_outlet_temp_c: float = 0.0
    process_outlet_temp_c: float = 0.0
    surface_area_m2: float = 0.0

    # Per API 661 requirements
    overdesign_percent: float = 0.0
    min_approach_temp_c: float = 0.0
    is_acceptable: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class PressureDropResults:
    """Results of pressure drop calculations."""
    # Tube-side
    tube_side_dp_kpa: float = 0.0
    tube_friction_dp_kpa: float = 0.0
    tube_entrance_exit_dp_kpa: float = 0.0
    tube_return_bend_dp_kpa: float = 0.0
    nozzle_dp_kpa: float = 0.0

    # Air-side
    air_side_dp_pa: float = 0.0
    bundle_dp_pa: float = 0.0
    plenum_dp_pa: float = 0.0

    # Validation
    is_within_limits: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class FanResults:
    """Fan performance calculation results."""
    air_flow_m3_s: float = 0.0
    air_flow_acfm: float = 0.0
    static_pressure_pa: float = 0.0
    static_pressure_inwg: float = 0.0
    shaft_power_kw: float = 0.0
    motor_power_kw: float = 0.0
    tip_speed_m_s: float = 0.0
    fan_efficiency: float = 0.75

    # API 661 checks
    tip_speed_acceptable: bool = True
    noise_db_a: float = 0.0
    warnings: List[str] = field(default_factory=list)


class ACHECalculator:
    """
    Engineering calculator for Air Cooled Heat Exchangers.

    Implements Phase 24.4: Analysis & Calculations

    Calculation Methods:
    - Thermal: LMTD and NTU-effectiveness methods
    - Pressure drop: Tube-side and air-side correlations
    - Fan: Power and performance per API 661

    Standards:
    - API 661 / ISO 13706
    - ASME PTC 30
    - HTRI methods (simplified)
    """

    # API 661 limits
    MAX_TIP_SPEED_M_S = 61.0  # ~200 ft/s
    MAX_AIR_SIDE_DP_PA = 250  # Typical limit
    MIN_APPROACH_TEMP_C = 5.0  # Minimum approach temperature

    def __init__(self):
        """Initialize calculator."""
        self._fouling_factors = {
            "clean": 0.0,
            "light": 0.0001,
            "moderate": 0.0002,
            "heavy": 0.0004,
            "severe": 0.0006,
        }

    def calculate_thermal_performance(
        self,
        duty_kw: float,
        process_inlet_temp_c: float,
        process_outlet_temp_c: float,
        air_inlet_temp_c: float,
        air_flow_kg_s: float,
        surface_area_m2: float,
        process_fluid: FluidProperties,
        u_clean_w_m2_k: float,
        fouling_factor: float = 0.0002,
        flow_arrangement: FlowArrangement = FlowArrangement.CROSSFLOW_UNMIXED,
    ) -> ThermalResults:
        """
        Calculate thermal performance of ACHE.

        Args:
            duty_kw: Heat duty in kW
            process_inlet_temp_c: Process fluid inlet temperature
            process_outlet_temp_c: Process fluid outlet temperature
            air_inlet_temp_c: Air inlet temperature
            air_flow_kg_s: Air mass flow rate
            surface_area_m2: Heat transfer surface area
            process_fluid: Process fluid properties
            u_clean_w_m2_k: Clean overall heat transfer coefficient
            fouling_factor: Total fouling resistance (m2-K/W)
            flow_arrangement: Heat exchanger flow arrangement

        Returns:
            ThermalResults with calculated values
        """
        results = ThermalResults()
        results.surface_area_m2 = surface_area_m2

        try:
            # Air properties at average temperature
            air_avg_temp = air_inlet_temp_c + 10  # Initial estimate
            air_props = FluidProperties.air_at_temperature(air_avg_temp)

            # Calculate air outlet temperature from energy balance
            duty_w = duty_kw * 1000
            air_cp = air_props.specific_heat_j_kg_k
            delta_t_air = duty_w / (air_flow_kg_s * air_cp)
            air_outlet_temp = air_inlet_temp_c + delta_t_air

            results.air_outlet_temp_c = air_outlet_temp
            results.process_outlet_temp_c = process_outlet_temp_c
            results.duty_kw = duty_kw

            # LMTD calculation
            lmtd = self._calculate_lmtd(
                process_inlet_temp_c,
                process_outlet_temp_c,
                air_inlet_temp_c,
                air_outlet_temp,
            )
            results.lmtd_k = lmtd

            # LMTD correction factor for crossflow
            F = self._calculate_lmtd_correction(
                process_inlet_temp_c,
                process_outlet_temp_c,
                air_inlet_temp_c,
                air_outlet_temp,
                flow_arrangement,
            )
            results.lmtd_correction_factor = F

            # Overall U with fouling
            u_fouled = 1.0 / (1.0 / u_clean_w_m2_k + fouling_factor)
            results.overall_u_w_m2_k = u_fouled

            # Required surface area
            required_area = duty_w / (u_fouled * lmtd * F)

            # Overdesign calculation
            overdesign = ((surface_area_m2 - required_area) / required_area) * 100
            results.overdesign_percent = overdesign

            # NTU-effectiveness
            c_min = min(
                air_flow_kg_s * air_cp,
                duty_w / abs(process_inlet_temp_c - process_outlet_temp_c)
            )
            c_max = max(
                air_flow_kg_s * air_cp,
                duty_w / abs(process_inlet_temp_c - process_outlet_temp_c)
            )
            c_ratio = c_min / c_max if c_max > 0 else 0

            ntu = u_fouled * surface_area_m2 / c_min if c_min > 0 else 0
            results.ntu = ntu

            # Effectiveness for crossflow
            effectiveness = self._calculate_effectiveness(ntu, c_ratio, flow_arrangement)
            results.effectiveness = effectiveness

            # Minimum approach temperature
            min_approach = min(
                process_outlet_temp_c - air_inlet_temp_c,
                process_inlet_temp_c - air_outlet_temp,
            )
            results.min_approach_temp_c = min_approach

            # Validation
            if min_approach < self.MIN_APPROACH_TEMP_C:
                results.warnings.append(
                    f"Approach temperature {min_approach:.1f}°C below minimum {self.MIN_APPROACH_TEMP_C}°C"
                )
                results.is_acceptable = False

            if overdesign < 0:
                results.warnings.append(
                    f"Insufficient surface area: {overdesign:.1f}% overdesign"
                )
                results.is_acceptable = False
            elif overdesign < 5:
                results.warnings.append(
                    f"Low overdesign margin: {overdesign:.1f}%"
                )

            if F < 0.75:
                results.warnings.append(
                    f"Low LMTD correction factor: {F:.3f}"
                )

            logger.info(f"Thermal calc complete: {duty_kw:.1f} kW, LMTD={lmtd:.1f}K")

        except Exception as e:
            logger.error(f"Thermal calculation error: {e}")
            results.warnings.append(f"Calculation error: {e}")
            results.is_acceptable = False

        return results

    def _calculate_lmtd(
        self,
        t1_in: float,
        t1_out: float,
        t2_in: float,
        t2_out: float,
    ) -> float:
        """Calculate Log Mean Temperature Difference."""
        dt1 = t1_in - t2_out  # Hot end
        dt2 = t1_out - t2_in  # Cold end

        if dt1 <= 0 or dt2 <= 0:
            return 0.0

        if abs(dt1 - dt2) < 0.1:
            return (dt1 + dt2) / 2

        return (dt1 - dt2) / math.log(dt1 / dt2)

    def _calculate_lmtd_correction(
        self,
        t1_in: float,
        t1_out: float,
        t2_in: float,
        t2_out: float,
        arrangement: FlowArrangement,
    ) -> float:
        """Calculate LMTD correction factor F."""
        if arrangement == FlowArrangement.COUNTERFLOW:
            return 1.0

        # P and R parameters
        denom = t1_in - t2_in
        if abs(denom) < 0.1:
            return 0.9  # Conservative estimate

        P = (t2_out - t2_in) / denom
        R = (t1_in - t1_out) / (t2_out - t2_in) if abs(t2_out - t2_in) > 0.1 else 1.0

        # Simplified F factor for crossflow
        if arrangement in [FlowArrangement.CROSSFLOW, FlowArrangement.CROSSFLOW_UNMIXED]:
            # Approximation for single-pass crossflow
            if R < 0.1:
                return 0.98
            elif R < 1.0:
                return 0.95 - 0.1 * P
            else:
                return 0.90 - 0.15 * P

        return 0.9  # Default conservative value

    def _calculate_effectiveness(
        self,
        ntu: float,
        c_ratio: float,
        arrangement: FlowArrangement,
    ) -> float:
        """Calculate heat exchanger effectiveness."""
        if ntu <= 0:
            return 0.0

        if arrangement == FlowArrangement.COUNTERFLOW:
            if abs(c_ratio - 1.0) < 0.01:
                return ntu / (1 + ntu)
            exp_term = math.exp(-ntu * (1 - c_ratio))
            return (1 - exp_term) / (1 - c_ratio * exp_term)

        elif arrangement == FlowArrangement.PARALLEL:
            exp_term = math.exp(-ntu * (1 + c_ratio))
            return (1 - exp_term) / (1 + c_ratio)

        elif arrangement in [FlowArrangement.CROSSFLOW, FlowArrangement.CROSSFLOW_UNMIXED]:
            # Approximation for crossflow, both fluids unmixed
            exp_ntu = 1 - math.exp(-ntu)
            return 1 - math.exp(-exp_ntu * (1 - math.exp(-c_ratio * ntu)) / c_ratio) if c_ratio > 0 else exp_ntu

        return 1 - math.exp(-ntu)  # Default single-stream

    def calculate_tube_side_pressure_drop(
        self,
        mass_flow_kg_s: float,
        fluid: FluidProperties,
        tube_id_mm: float,
        tube_length_m: float,
        num_tubes: int,
        num_passes: int,
        roughness_mm: float = 0.045,
    ) -> PressureDropResults:
        """
        Calculate tube-side pressure drop.

        Args:
            mass_flow_kg_s: Total mass flow rate
            fluid: Fluid properties
            tube_id_mm: Tube inside diameter in mm
            tube_length_m: Tube length in meters
            num_tubes: Number of tubes
            num_passes: Number of tube passes
            roughness_mm: Tube roughness in mm

        Returns:
            PressureDropResults
        """
        results = PressureDropResults()

        try:
            tube_id_m = tube_id_mm / 1000
            tubes_per_pass = num_tubes / num_passes

            # Flow velocity
            flow_area = (math.pi * tube_id_m ** 2 / 4) * tubes_per_pass
            velocity = mass_flow_kg_s / (fluid.density_kg_m3 * flow_area)

            # Reynolds number
            Re = fluid.density_kg_m3 * velocity * tube_id_m / fluid.viscosity_pa_s

            # Friction factor (Colebrook-White approximation)
            rel_roughness = roughness_mm / tube_id_mm
            if Re < 2300:
                f = 64 / Re
            else:
                # Swamee-Jain equation
                f = 0.25 / (math.log10(rel_roughness / 3.7 + 5.74 / Re ** 0.9)) ** 2

            # Friction pressure drop (all passes)
            dp_friction = f * (tube_length_m * num_passes / tube_id_m) * \
                         (fluid.density_kg_m3 * velocity ** 2 / 2)
            results.tube_friction_dp_kpa = dp_friction / 1000

            # Entrance/exit losses (K = 1.0 per pass)
            dp_entrance_exit = num_passes * 1.0 * (fluid.density_kg_m3 * velocity ** 2 / 2)
            results.tube_entrance_exit_dp_kpa = dp_entrance_exit / 1000

            # Return bend losses (K = 0.5 per bend)
            num_bends = num_passes - 1
            dp_bends = num_bends * 0.5 * (fluid.density_kg_m3 * velocity ** 2 / 2)
            results.tube_return_bend_dp_kpa = dp_bends / 1000

            # Total
            results.tube_side_dp_kpa = (dp_friction + dp_entrance_exit + dp_bends) / 1000

            logger.info(f"Tube-side DP: {results.tube_side_dp_kpa:.2f} kPa, Re={Re:.0f}")

        except Exception as e:
            logger.error(f"Tube-side pressure drop error: {e}")
            results.warnings.append(f"Calculation error: {e}")

        return results

    def calculate_air_side_pressure_drop(
        self,
        air_flow_kg_s: float,
        air_inlet_temp_c: float,
        bundle_face_area_m2: float,
        tube_od_mm: float,
        fin_pitch_mm: float,
        fin_height_mm: float,
        num_tube_rows: int,
    ) -> PressureDropResults:
        """
        Calculate air-side pressure drop across tube bundle.

        Uses simplified ESDU correlation for finned tube banks.

        Args:
            air_flow_kg_s: Air mass flow rate
            air_inlet_temp_c: Air inlet temperature
            bundle_face_area_m2: Bundle face area
            tube_od_mm: Tube outside diameter
            fin_pitch_mm: Fin pitch (fins per length)
            fin_height_mm: Fin height
            num_tube_rows: Number of tube rows deep

        Returns:
            PressureDropResults
        """
        results = PressureDropResults()

        try:
            air_props = FluidProperties.air_at_temperature(air_inlet_temp_c)

            # Face velocity
            face_velocity = air_flow_kg_s / (air_props.density_kg_m3 * bundle_face_area_m2)

            # Minimum free flow area ratio (sigma)
            tube_od_m = tube_od_mm / 1000
            fin_od_m = tube_od_m + 2 * fin_height_mm / 1000
            # Simplified: assume triangular pitch with 2.5 * tube OD spacing
            pitch = 2.5 * tube_od_m
            sigma = 1 - fin_od_m / pitch  # Approximate

            # Maximum velocity
            max_velocity = face_velocity / sigma

            # Reynolds number based on tube OD
            Re = air_props.density_kg_m3 * max_velocity * tube_od_m / air_props.viscosity_pa_s

            # Friction factor (simplified correlation for finned tubes)
            # Based on Robinson & Briggs correlation
            f = 0.5 * Re ** (-0.25) * (fin_pitch_mm / fin_height_mm) ** 0.14

            # Pressure drop across bundle
            dp_bundle = f * num_tube_rows * (air_props.density_kg_m3 * max_velocity ** 2 / 2)
            results.bundle_dp_pa = dp_bundle

            # Plenum losses (estimated at 20% of bundle)
            dp_plenum = 0.2 * dp_bundle
            results.plenum_dp_pa = dp_plenum

            # Total air-side pressure drop
            results.air_side_dp_pa = dp_bundle + dp_plenum

            # Validation
            if results.air_side_dp_pa > self.MAX_AIR_SIDE_DP_PA:
                results.warnings.append(
                    f"Air-side DP {results.air_side_dp_pa:.0f} Pa exceeds limit {self.MAX_AIR_SIDE_DP_PA} Pa"
                )
                results.is_within_limits = False

            logger.info(f"Air-side DP: {results.air_side_dp_pa:.0f} Pa, Re={Re:.0f}")

        except Exception as e:
            logger.error(f"Air-side pressure drop error: {e}")
            results.warnings.append(f"Calculation error: {e}")

        return results

    def calculate_fan_performance(
        self,
        air_flow_m3_s: float,
        static_pressure_pa: float,
        fan_diameter_m: float,
        fan_rpm: float,
        fan_efficiency: float = 0.75,
        motor_efficiency: float = 0.92,
        air_density_kg_m3: float = 1.2,
    ) -> FanResults:
        """
        Calculate fan performance and power requirements.

        Per API 661 Section 6 requirements.

        Args:
            air_flow_m3_s: Volumetric air flow rate
            static_pressure_pa: Static pressure rise required
            fan_diameter_m: Fan diameter
            fan_rpm: Fan rotational speed
            fan_efficiency: Fan static efficiency
            motor_efficiency: Motor efficiency
            air_density_kg_m3: Air density

        Returns:
            FanResults
        """
        results = FanResults()

        try:
            results.air_flow_m3_s = air_flow_m3_s
            results.air_flow_acfm = air_flow_m3_s * 2118.88  # Convert to ACFM
            results.static_pressure_pa = static_pressure_pa
            results.static_pressure_inwg = static_pressure_pa / 249.09  # Convert to inwg
            results.fan_efficiency = fan_efficiency

            # Fan tip speed
            tip_speed = math.pi * fan_diameter_m * fan_rpm / 60
            results.tip_speed_m_s = tip_speed

            # API 661 tip speed check
            if tip_speed > self.MAX_TIP_SPEED_M_S:
                results.tip_speed_acceptable = False
                results.warnings.append(
                    f"Tip speed {tip_speed:.1f} m/s exceeds API 661 limit of {self.MAX_TIP_SPEED_M_S} m/s"
                )

            # Air power
            air_power_w = air_flow_m3_s * static_pressure_pa

            # Shaft power
            shaft_power_w = air_power_w / fan_efficiency
            results.shaft_power_kw = shaft_power_w / 1000

            # Motor power (with margin)
            motor_power_w = shaft_power_w / motor_efficiency
            # Add 10% margin per API 661
            results.motor_power_kw = (motor_power_w / 1000) * 1.10

            # Noise estimate (simplified)
            # Based on specific sound power level correlation
            Lw = 56 + 10 * math.log10(shaft_power_w) + 30 * math.log10(tip_speed / 50)
            results.noise_db_a = Lw

            if results.noise_db_a > 90:
                results.warnings.append(
                    f"Estimated noise level {results.noise_db_a:.0f} dBA may require attenuation"
                )

            logger.info(
                f"Fan calc: {air_flow_m3_s:.1f} m3/s, {static_pressure_pa:.0f} Pa, "
                f"Shaft power: {results.shaft_power_kw:.2f} kW"
            )

        except Exception as e:
            logger.error(f"Fan calculation error: {e}")
            results.warnings.append(f"Calculation error: {e}")

        return results

    def calculate_heat_transfer_coefficient(
        self,
        fluid: FluidProperties,
        velocity_m_s: float,
        hydraulic_diameter_m: float,
        fluid_type: FluidType = FluidType.LIQUID,
    ) -> float:
        """
        Calculate convective heat transfer coefficient.

        Uses appropriate correlation based on fluid type:
        - Dittus-Boelter for turbulent liquid/gas
        - Simplified correlations for two-phase

        Args:
            fluid: Fluid properties
            velocity_m_s: Fluid velocity
            hydraulic_diameter_m: Hydraulic diameter
            fluid_type: Type of fluid flow

        Returns:
            Heat transfer coefficient in W/m2-K
        """
        # Reynolds number
        Re = fluid.density_kg_m3 * velocity_m_s * hydraulic_diameter_m / fluid.viscosity_pa_s
        Pr = fluid.prandtl_number

        if Re < 2300:
            # Laminar flow - constant wall temperature
            Nu = 3.66
        elif Re < 10000:
            # Transition region
            Nu_lam = 3.66
            Nu_turb = 0.023 * Re ** 0.8 * Pr ** 0.4
            # Linear interpolation
            x = (Re - 2300) / 7700
            Nu = Nu_lam * (1 - x) + Nu_turb * x
        else:
            # Turbulent - Dittus-Boelter
            if fluid_type in [FluidType.CONDENSING]:
                # Cooling - exponent 0.3
                Nu = 0.023 * Re ** 0.8 * Pr ** 0.3
            else:
                # Heating - exponent 0.4
                Nu = 0.023 * Re ** 0.8 * Pr ** 0.4

        # Heat transfer coefficient
        h = Nu * fluid.thermal_conductivity_w_m_k / hydraulic_diameter_m

        # Enhancement for two-phase
        if fluid_type == FluidType.CONDENSING:
            h *= 1.5  # Simplified enhancement
        elif fluid_type == FluidType.BOILING:
            h *= 2.0

        return h

    def size_ache(
        self,
        duty_kw: float,
        process_inlet_temp_c: float,
        process_outlet_temp_c: float,
        air_inlet_temp_c: float,
        process_fluid: FluidProperties,
        max_air_outlet_temp_c: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Preliminary ACHE sizing calculation.

        Provides initial estimates for:
        - Surface area required
        - Number of tube rows
        - Face area
        - Air flow rate
        - Number of fans

        Args:
            duty_kw: Heat duty
            process_inlet_temp_c: Process inlet temperature
            process_outlet_temp_c: Process outlet temperature
            air_inlet_temp_c: Ambient air temperature
            process_fluid: Process fluid properties
            max_air_outlet_temp_c: Maximum air outlet (default: process_out - 10°C)

        Returns:
            Dictionary with sizing estimates
        """
        results = {
            "duty_kw": duty_kw,
            "air_inlet_temp_c": air_inlet_temp_c,
            "warnings": [],
        }

        try:
            # Air outlet temperature limit
            if max_air_outlet_temp_c is None:
                max_air_outlet_temp_c = process_outlet_temp_c - 10

            # Air temperature rise
            air_temp_rise = max_air_outlet_temp_c - air_inlet_temp_c
            if air_temp_rise < 5:
                results["warnings"].append("Air temperature rise too low")
                air_temp_rise = 10

            results["air_outlet_temp_c"] = air_inlet_temp_c + air_temp_rise

            # Air properties at average temperature
            air_avg_temp = air_inlet_temp_c + air_temp_rise / 2
            air_props = FluidProperties.air_at_temperature(air_avg_temp)

            # Air mass flow required
            duty_w = duty_kw * 1000
            air_mass_flow = duty_w / (air_props.specific_heat_j_kg_k * air_temp_rise)
            air_vol_flow = air_mass_flow / air_props.density_kg_m3

            results["air_mass_flow_kg_s"] = air_mass_flow
            results["air_volume_flow_m3_s"] = air_vol_flow

            # Typical face velocity for ACHEs: 2.5-3.5 m/s
            face_velocity = 3.0  # m/s
            face_area = air_vol_flow / face_velocity

            results["face_area_m2"] = face_area
            results["face_velocity_m_s"] = face_velocity

            # LMTD estimate
            lmtd = self._calculate_lmtd(
                process_inlet_temp_c,
                process_outlet_temp_c,
                air_inlet_temp_c,
                air_inlet_temp_c + air_temp_rise,
            )
            results["lmtd_k"] = lmtd

            # Typical U values for finned tubes
            # Air-side limited: 30-60 W/m2-K
            u_estimated = 45  # W/m2-K typical
            results["estimated_u_w_m2_k"] = u_estimated

            # Surface area (with F factor ~0.9 for crossflow)
            F = 0.9
            surface_area = duty_w / (u_estimated * lmtd * F)

            # Add 15% overdesign margin
            surface_area *= 1.15
            results["surface_area_m2"] = surface_area

            # Typical extended surface ratios: 15-25
            extended_ratio = 20
            bare_tube_area = surface_area / extended_ratio
            results["bare_tube_area_m2"] = bare_tube_area

            # Estimate number of tubes (assume 25mm OD x 6m length)
            tube_od = 0.025  # m
            tube_length = 6.0  # m
            tube_surface = math.pi * tube_od * tube_length
            num_tubes = int(bare_tube_area / tube_surface) + 1

            results["estimated_tubes"] = num_tubes
            results["tube_length_m"] = tube_length

            # Bay width (typically 2.5-3.5m per bay)
            bay_width = 3.0  # m
            bundle_width = face_area / tube_length
            num_bays = max(1, int(bundle_width / bay_width) + 1)

            results["estimated_bays"] = num_bays
            results["bundle_width_m"] = bundle_width

            # Fan sizing (typical: 1-2 fans per bay)
            fans_per_bay = 1 if air_vol_flow / num_bays < 30 else 2
            num_fans = num_bays * fans_per_bay

            results["num_fans"] = num_fans
            results["air_flow_per_fan_m3_s"] = air_vol_flow / num_fans

            # Fan diameter (fit within bay)
            fan_diameter = min(bay_width * 0.9, 4.5)  # Max ~14 ft
            results["fan_diameter_m"] = fan_diameter

            logger.info(
                f"ACHE sizing: {duty_kw:.0f} kW, "
                f"Area: {surface_area:.0f} m2, "
                f"{num_bays} bays, {num_fans} fans"
            )

        except Exception as e:
            logger.error(f"ACHE sizing error: {e}")
            results["warnings"].append(f"Sizing error: {e}")

        return results
