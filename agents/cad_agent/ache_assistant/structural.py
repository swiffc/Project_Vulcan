"""
ACHE Structural Designer Module
Phase 24.5 - Structural Component Design for Air Cooled Heat Exchangers

Implements structural design per:
- API 661 / ISO 13706 structural requirements
- AISC Steel Construction Manual
- ASCE 7 load combinations
"""

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger("vulcan.ache.structural")


class SteelGrade(Enum):
    """Common structural steel grades."""
    A36 = "A36"
    A572_50 = "A572-50"
    A992 = "A992"
    A500B = "A500B"  # HSS
    A500C = "A500C"  # HSS


class ProfileType(Enum):
    """Structural profile types."""
    W_SHAPE = "W"
    HSS_RECT = "HSS_RECT"
    HSS_ROUND = "HSS_ROUND"
    PIPE = "PIPE"
    CHANNEL = "C"
    ANGLE = "L"


@dataclass
class SteelProperties:
    """Steel material properties."""
    grade: SteelGrade
    fy_mpa: float  # Yield strength
    fu_mpa: float  # Tensile strength
    E_mpa: float = 200000  # Elastic modulus
    density_kg_m3: float = 7850

    @classmethod
    def from_grade(cls, grade: SteelGrade) -> "SteelProperties":
        """Get properties for standard steel grade."""
        props = {
            SteelGrade.A36: (250, 400),
            SteelGrade.A572_50: (345, 450),
            SteelGrade.A992: (345, 450),
            SteelGrade.A500B: (290, 400),
            SteelGrade.A500C: (317, 427),
        }
        fy, fu = props.get(grade, (250, 400))
        return cls(grade=grade, fy_mpa=fy, fu_mpa=fu)


@dataclass
class LoadCase:
    """Structural load case definition."""
    name: str
    dead_kn: float = 0.0
    live_kn: float = 0.0
    wind_kn: float = 0.0
    seismic_kn: float = 0.0
    thermal_kn: float = 0.0
    nozzle_kn: float = 0.0

    def get_factored_load(self, combination: str = "D+L") -> float:
        """Get factored load for LRFD combination."""
        combos = {
            "D": 1.4 * self.dead_kn,
            "D+L": 1.2 * self.dead_kn + 1.6 * self.live_kn,
            "D+W": 1.2 * self.dead_kn + 1.0 * self.wind_kn,
            "D+L+W": 1.2 * self.dead_kn + 1.0 * self.live_kn + 0.5 * self.wind_kn,
            "D+E": 1.2 * self.dead_kn + 1.0 * self.seismic_kn,
            "D+L+E": 1.2 * self.dead_kn + 0.5 * self.live_kn + 1.0 * self.seismic_kn,
        }
        return combos.get(combination, self.dead_kn + self.live_kn)


@dataclass
class ColumnDesign:
    """Column design results."""
    profile: str
    profile_type: ProfileType
    steel_grade: SteelGrade
    height_m: float

    # Section properties
    area_mm2: float = 0.0
    ix_mm4: float = 0.0
    iy_mm4: float = 0.0
    rx_mm: float = 0.0
    ry_mm: float = 0.0
    zx_mm3: float = 0.0

    # Design values
    axial_capacity_kn: float = 0.0
    moment_capacity_knm: float = 0.0
    applied_axial_kn: float = 0.0
    applied_moment_knm: float = 0.0
    utilization_ratio: float = 0.0

    # Slenderness
    kl_r: float = 0.0
    is_slender: bool = False

    is_adequate: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class BeamDesign:
    """Beam design results."""
    profile: str
    profile_type: ProfileType
    steel_grade: SteelGrade
    span_m: float

    # Section properties
    area_mm2: float = 0.0
    ix_mm4: float = 0.0
    sx_mm3: float = 0.0
    zx_mm3: float = 0.0

    # Design values
    moment_capacity_knm: float = 0.0
    shear_capacity_kn: float = 0.0
    applied_moment_knm: float = 0.0
    applied_shear_kn: float = 0.0
    deflection_mm: float = 0.0
    deflection_limit_mm: float = 0.0
    utilization_ratio: float = 0.0

    is_adequate: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class ConnectionDesign:
    """Connection design results."""
    connection_type: str
    num_bolts: int = 0
    bolt_diameter_mm: float = 0.0
    bolt_grade: str = "A325"
    weld_size_mm: float = 0.0
    weld_length_mm: float = 0.0

    bolt_capacity_kn: float = 0.0
    weld_capacity_kn: float = 0.0
    applied_force_kn: float = 0.0
    utilization_ratio: float = 0.0

    is_adequate: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class FrameDesign:
    """Complete frame design summary."""
    num_columns: int
    num_beams: int
    columns: List[ColumnDesign]
    beams: List[BeamDesign]
    connections: List[ConnectionDesign]

    total_steel_weight_kg: float = 0.0
    max_utilization: float = 0.0

    is_adequate: bool = True
    governing_case: str = ""
    warnings: List[str] = field(default_factory=list)


class StructuralDesigner:
    """
    Structural designer for ACHE support frames.

    Implements Phase 24.5: Structural Components

    Capabilities:
    - Column design (axial + bending)
    - Beam design (flexure + shear)
    - Connection design (bolted/welded)
    - Frame analysis and optimization
    - Code compliance checks (AISC/API 661)
    """

    # Standard W-shape database (simplified)
    W_SHAPES = {
        "W6x15": {"d": 152, "bf": 152, "A": 2850, "Ix": 12.1e6, "Iy": 3.8e6, "Zx": 175e3},
        "W8x21": {"d": 210, "bf": 134, "A": 4000, "Ix": 32.6e6, "Iy": 3.0e6, "Zx": 346e3},
        "W8x31": {"d": 203, "bf": 203, "A": 5900, "Ix": 48.5e6, "Iy": 15.7e6, "Zx": 522e3},
        "W10x33": {"d": 247, "bf": 202, "A": 6290, "Ix": 71.3e6, "Iy": 15.9e6, "Zx": 617e3},
        "W10x49": {"d": 253, "bf": 254, "A": 9290, "Ix": 113e6, "Iy": 38.9e6, "Zx": 978e3},
        "W12x40": {"d": 304, "bf": 203, "A": 7610, "Ix": 135e6, "Iy": 16.3e6, "Zx": 978e3},
        "W12x58": {"d": 310, "bf": 254, "A": 11000, "Ix": 199e6, "Iy": 42.0e6, "Zx": 1410e3},
        "W14x48": {"d": 351, "bf": 203, "A": 9100, "Ix": 201e6, "Iy": 17.3e6, "Zx": 1260e3},
        "W14x68": {"d": 357, "bf": 254, "A": 12900, "Ix": 301e6, "Iy": 45.0e6, "Zx": 1850e3},
        "W14x90": {"d": 356, "bf": 368, "A": 17100, "Ix": 416e6, "Iy": 131e6, "Zx": 2540e3},
    }

    # HSS shapes database (simplified)
    HSS_SHAPES = {
        "HSS6x6x1/4": {"b": 152, "t": 6.35, "A": 3480, "I": 9.17e6, "Z": 141e3},
        "HSS6x6x3/8": {"b": 152, "t": 9.53, "A": 5030, "I": 12.6e6, "Z": 199e3},
        "HSS8x8x1/4": {"b": 203, "t": 6.35, "A": 4710, "I": 22.4e6, "Z": 254e3},
        "HSS8x8x3/8": {"b": 203, "t": 9.53, "A": 6900, "I": 31.3e6, "Z": 361e3},
        "HSS8x8x1/2": {"b": 203, "t": 12.7, "A": 8970, "I": 38.7e6, "Z": 453e3},
        "HSS10x10x3/8": {"b": 254, "t": 9.53, "A": 8770, "I": 63.0e6, "Z": 578e3},
        "HSS10x10x1/2": {"b": 254, "t": 12.7, "A": 11500, "I": 79.5e6, "Z": 738e3},
        "HSS12x12x3/8": {"b": 305, "t": 9.53, "A": 10600, "I": 111e6, "Z": 841e3},
        "HSS12x12x1/2": {"b": 305, "t": 12.7, "A": 14000, "I": 142e6, "Z": 1090e3},
    }

    def __init__(self, steel_grade: SteelGrade = SteelGrade.A992):
        """Initialize structural designer."""
        self.default_grade = steel_grade
        self.steel_props = SteelProperties.from_grade(steel_grade)

    def design_column(
        self,
        axial_load_kn: float,
        moment_kn_m: float,
        height_m: float,
        k_factor: float = 1.0,
        profile_type: ProfileType = ProfileType.HSS_RECT,
        braced_axis: str = "both",
    ) -> ColumnDesign:
        """
        Design column for axial load and moment.

        Args:
            axial_load_kn: Factored axial load
            moment_kn_m: Factored moment
            height_m: Column height
            k_factor: Effective length factor
            profile_type: Type of profile to use
            braced_axis: Bracing condition ("x", "y", "both", "none")

        Returns:
            ColumnDesign with selected profile and checks
        """
        design = ColumnDesign(
            profile="",
            profile_type=profile_type,
            steel_grade=self.default_grade,
            height_m=height_m,
            applied_axial_kn=axial_load_kn,
            applied_moment_knm=moment_kn_m,
        )

        try:
            # Select shape database
            shapes = self.HSS_SHAPES if profile_type == ProfileType.HSS_RECT else self.W_SHAPES

            best_profile = None
            best_weight = float('inf')

            for name, props in shapes.items():
                # Get section properties
                A = props["A"]
                I = props.get("I", props.get("Ix", 0))
                Z = props.get("Z", props.get("Zx", 0))

                # Radius of gyration
                r = math.sqrt(I / A) if A > 0 else 1

                # Slenderness ratio
                kl = k_factor * height_m * 1000  # mm
                kl_r = kl / r

                # Critical stress (AISC E3)
                Fe = math.pi ** 2 * self.steel_props.E_mpa / kl_r ** 2 if kl_r > 0 else float('inf')
                fy = self.steel_props.fy_mpa

                if kl_r <= 4.71 * math.sqrt(self.steel_props.E_mpa / fy):
                    Fcr = 0.658 ** (fy / Fe) * fy
                else:
                    Fcr = 0.877 * Fe

                # Axial capacity (phi = 0.9)
                Pn = 0.9 * Fcr * A / 1000  # kN

                # Moment capacity (phi = 0.9)
                Mn = 0.9 * fy * Z / 1e6  # kN-m

                # Interaction check (AISC H1)
                if Pn > 0 and Mn > 0:
                    Pr_Pc = axial_load_kn / Pn
                    Mr_Mc = moment_kn_m / Mn

                    if Pr_Pc >= 0.2:
                        utilization = Pr_Pc + (8/9) * Mr_Mc
                    else:
                        utilization = Pr_Pc / 2 + Mr_Mc

                    # Check if adequate
                    if utilization <= 1.0:
                        # Estimate weight
                        weight = A * height_m * self.steel_props.density_kg_m3 / 1e6

                        if weight < best_weight:
                            best_weight = weight
                            best_profile = {
                                "name": name,
                                "A": A,
                                "I": I,
                                "Z": Z,
                                "r": r,
                                "kl_r": kl_r,
                                "Pn": Pn,
                                "Mn": Mn,
                                "util": utilization,
                            }

            if best_profile:
                design.profile = best_profile["name"]
                design.area_mm2 = best_profile["A"]
                design.ix_mm4 = best_profile["I"]
                design.zx_mm3 = best_profile["Z"]
                design.rx_mm = best_profile["r"]
                design.kl_r = best_profile["kl_r"]
                design.axial_capacity_kn = best_profile["Pn"]
                design.moment_capacity_knm = best_profile["Mn"]
                design.utilization_ratio = best_profile["util"]
                design.is_adequate = True

                if best_profile["kl_r"] > 200:
                    design.is_slender = True
                    design.warnings.append(f"Slenderness ratio {best_profile['kl_r']:.0f} exceeds 200")
            else:
                design.is_adequate = False
                design.warnings.append("No adequate profile found - increase section size")

            logger.info(f"Column design: {design.profile}, utilization={design.utilization_ratio:.2f}")

        except Exception as e:
            logger.error(f"Column design error: {e}")
            design.warnings.append(f"Design error: {e}")
            design.is_adequate = False

        return design

    def design_beam(
        self,
        span_m: float,
        distributed_load_kn_m: float,
        point_loads: Optional[List[Tuple[float, float]]] = None,
        deflection_limit: str = "L/240",
        profile_type: ProfileType = ProfileType.W_SHAPE,
        unbraced_length_m: Optional[float] = None,
    ) -> BeamDesign:
        """
        Design beam for flexure and deflection.

        Args:
            span_m: Beam span
            distributed_load_kn_m: Uniformly distributed load
            point_loads: List of (position_m, load_kn) tuples
            deflection_limit: Deflection criterion (L/240, L/360, etc.)
            profile_type: Type of profile
            unbraced_length_m: Unbraced length for LTB

        Returns:
            BeamDesign with selected profile and checks
        """
        design = BeamDesign(
            profile="",
            profile_type=profile_type,
            steel_grade=self.default_grade,
            span_m=span_m,
        )

        try:
            # Calculate maximum moment and shear from distributed load
            w = distributed_load_kn_m
            L = span_m

            M_dist = w * L ** 2 / 8  # kN-m
            V_dist = w * L / 2  # kN

            # Add point loads
            M_point = 0
            V_point = 0
            if point_loads:
                for pos, P in point_loads:
                    # Simple beam moment
                    a = pos
                    b = L - pos
                    M_point += P * a * b / L
                    V_point += P / 2  # Simplified

            M_total = M_dist + M_point
            V_total = V_dist + V_point

            design.applied_moment_knm = M_total
            design.applied_shear_kn = V_total

            # Parse deflection limit
            if "/" in deflection_limit:
                divisor = float(deflection_limit.split("/")[1])
            else:
                divisor = 240
            design.deflection_limit_mm = span_m * 1000 / divisor

            # Select shape database
            shapes = self.W_SHAPES if profile_type == ProfileType.W_SHAPE else self.HSS_SHAPES

            best_profile = None
            best_weight = float('inf')

            for name, props in shapes.items():
                A = props["A"]
                I = props.get("I", props.get("Ix", 0))
                Z = props.get("Z", props.get("Zx", 0))

                # Moment capacity (assuming adequate bracing)
                fy = self.steel_props.fy_mpa
                Mn = 0.9 * fy * Z / 1e6  # kN-m

                # Shear capacity (simplified)
                d = props.get("d", props.get("b", 200))
                tw = props.get("tw", props.get("t", 10))
                Aw = d * tw  # Approximate web area
                Vn = 0.6 * 0.9 * fy * Aw / 1000  # kN

                # Deflection check
                E = self.steel_props.E_mpa
                deflection = (5 * w * (L * 1000) ** 4) / (384 * E * I)  # mm

                # Check adequacy
                if Mn >= M_total and Vn >= V_total and deflection <= design.deflection_limit_mm:
                    weight = A * span_m * self.steel_props.density_kg_m3 / 1e6

                    if weight < best_weight:
                        best_weight = weight
                        util = max(M_total / Mn, V_total / Vn)
                        best_profile = {
                            "name": name,
                            "A": A,
                            "I": I,
                            "Z": Z,
                            "Mn": Mn,
                            "Vn": Vn,
                            "defl": deflection,
                            "util": util,
                        }

            if best_profile:
                design.profile = best_profile["name"]
                design.area_mm2 = best_profile["A"]
                design.ix_mm4 = best_profile["I"]
                design.zx_mm3 = best_profile["Z"]
                design.moment_capacity_knm = best_profile["Mn"]
                design.shear_capacity_kn = best_profile["Vn"]
                design.deflection_mm = best_profile["defl"]
                design.utilization_ratio = best_profile["util"]
                design.is_adequate = True
            else:
                design.is_adequate = False
                design.warnings.append("No adequate profile found")

            logger.info(f"Beam design: {design.profile}, utilization={design.utilization_ratio:.2f}")

        except Exception as e:
            logger.error(f"Beam design error: {e}")
            design.warnings.append(f"Design error: {e}")
            design.is_adequate = False

        return design

    def design_connection(
        self,
        force_kn: float,
        moment_knm: float = 0,
        connection_type: str = "bolted",
        bolt_size_mm: float = 20,
        bolt_grade: str = "A325",
    ) -> ConnectionDesign:
        """
        Design bolted or welded connection.

        Args:
            force_kn: Applied force
            moment_knm: Applied moment
            connection_type: "bolted" or "welded"
            bolt_size_mm: Bolt diameter
            bolt_grade: Bolt grade (A325, A490)

        Returns:
            ConnectionDesign
        """
        design = ConnectionDesign(
            connection_type=connection_type,
            bolt_diameter_mm=bolt_size_mm,
            bolt_grade=bolt_grade,
            applied_force_kn=force_kn,
        )

        try:
            if connection_type == "bolted":
                # Bolt capacities (single shear, threads excluded)
                bolt_fu = 830 if bolt_grade == "A325" else 1040  # MPa for A490
                Ab = math.pi * (bolt_size_mm / 2) ** 2

                # Shear capacity per bolt (phi = 0.75)
                Rn_shear = 0.75 * 0.5 * bolt_fu * Ab / 1000  # kN

                # Number of bolts required
                num_bolts = max(2, int(force_kn / Rn_shear) + 1)

                design.num_bolts = num_bolts
                design.bolt_capacity_kn = num_bolts * Rn_shear
                design.utilization_ratio = force_kn / design.bolt_capacity_kn
                design.is_adequate = design.utilization_ratio <= 1.0

            else:  # welded
                # Fillet weld capacity
                # Assume E70 electrode, Fexx = 480 MPa
                Fexx = 480

                # Required weld size (minimum 5mm for structural)
                weld_size = max(5, bolt_size_mm / 4)

                # Effective throat
                throat = 0.707 * weld_size

                # Weld capacity per mm length (phi = 0.75)
                Rn_per_mm = 0.75 * 0.6 * Fexx * throat / 1000  # kN/mm

                # Required length
                weld_length = force_kn / Rn_per_mm + 2 * weld_size  # Add returns

                design.weld_size_mm = weld_size
                design.weld_length_mm = weld_length
                design.weld_capacity_kn = Rn_per_mm * weld_length
                design.utilization_ratio = force_kn / design.weld_capacity_kn
                design.is_adequate = design.utilization_ratio <= 1.0

            logger.info(f"Connection design: {connection_type}, util={design.utilization_ratio:.2f}")

        except Exception as e:
            logger.error(f"Connection design error: {e}")
            design.warnings.append(f"Design error: {e}")
            design.is_adequate = False

        return design

    def design_ache_frame(
        self,
        bundle_weight_kn: float,
        bundle_length_m: float,
        bundle_width_m: float,
        bundle_height_m: float,
        num_bays: int = 1,
        elevation_m: float = 3.0,
        wind_speed_m_s: float = 40,
        seismic_factor: float = 0.0,
    ) -> FrameDesign:
        """
        Design complete ACHE support frame.

        Args:
            bundle_weight_kn: Total bundle weight
            bundle_length_m: Bundle length (tube direction)
            bundle_width_m: Bundle width (perpendicular to tubes)
            bundle_height_m: Bundle height
            num_bays: Number of bays
            elevation_m: Height to bottom of bundle
            wind_speed_m_s: Design wind speed
            seismic_factor: Seismic acceleration factor (g)

        Returns:
            FrameDesign with complete frame design
        """
        columns = []
        beams = []
        connections = []
        warnings = []

        try:
            # Frame geometry
            col_spacing_length = bundle_length_m / 2  # Columns at ends and middle
            col_spacing_width = bundle_width_m / num_bays

            num_cols_length = 3  # End + middle columns
            num_cols_width = num_bays + 1
            total_columns = num_cols_length * num_cols_width

            # Loads
            dead_per_col = bundle_weight_kn / total_columns

            # Live load (maintenance access)
            live_psf = 50  # psf typical
            live_kpa = live_psf * 0.0479
            live_per_col = live_kpa * (col_spacing_length * col_spacing_width) / 4

            # Wind load
            wind_pressure_pa = 0.5 * 1.2 * wind_speed_m_s ** 2  # Dynamic pressure
            wind_area = bundle_length_m * bundle_height_m / total_columns
            wind_per_col = wind_pressure_pa * wind_area / 1000  # kN

            # Seismic
            seismic_per_col = seismic_factor * (dead_per_col + 0.25 * live_per_col)

            # Create load case
            load_case = LoadCase(
                name="Operating",
                dead_kn=dead_per_col,
                live_kn=live_per_col,
                wind_kn=wind_per_col,
                seismic_kn=seismic_per_col,
            )

            # Design columns
            # Check multiple load combinations
            combinations = ["D+L", "D+W", "D+L+W"]
            if seismic_factor > 0:
                combinations.extend(["D+E", "D+L+E"])

            max_util = 0
            governing = ""

            for combo in combinations:
                axial = load_case.get_factored_load(combo)
                # Moment from wind/seismic eccentricity
                moment = wind_per_col * elevation_m / 2 if "W" in combo else 0
                moment += seismic_per_col * elevation_m / 2 if "E" in combo else 0

                col_design = self.design_column(
                    axial_load_kn=axial,
                    moment_kn_m=moment,
                    height_m=elevation_m,
                    k_factor=1.2,  # Partially braced
                    profile_type=ProfileType.HSS_RECT,
                )

                if col_design.utilization_ratio > max_util:
                    max_util = col_design.utilization_ratio
                    governing = combo
                    final_col_design = col_design

            # Add column designs (same profile for all)
            for i in range(total_columns):
                col_copy = ColumnDesign(
                    profile=final_col_design.profile,
                    profile_type=final_col_design.profile_type,
                    steel_grade=final_col_design.steel_grade,
                    height_m=final_col_design.height_m,
                    area_mm2=final_col_design.area_mm2,
                    ix_mm4=final_col_design.ix_mm4,
                    zx_mm3=final_col_design.zx_mm3,
                    axial_capacity_kn=final_col_design.axial_capacity_kn,
                    moment_capacity_knm=final_col_design.moment_capacity_knm,
                    utilization_ratio=final_col_design.utilization_ratio,
                    is_adequate=final_col_design.is_adequate,
                )
                columns.append(col_copy)

            # Design beams (header beams at top)
            beam_load = bundle_weight_kn / (2 * num_bays)  # Two beams per bay
            beam_load_per_m = beam_load / bundle_length_m

            beam_design = self.design_beam(
                span_m=col_spacing_length,
                distributed_load_kn_m=beam_load_per_m * 1.4,  # Factored
                deflection_limit="L/240",
                profile_type=ProfileType.W_SHAPE,
            )

            num_beams = 2 * num_bays * 2  # Header beams both directions
            for i in range(num_beams):
                beams.append(BeamDesign(
                    profile=beam_design.profile,
                    profile_type=beam_design.profile_type,
                    steel_grade=beam_design.steel_grade,
                    span_m=beam_design.span_m,
                    moment_capacity_knm=beam_design.moment_capacity_knm,
                    shear_capacity_kn=beam_design.shear_capacity_kn,
                    utilization_ratio=beam_design.utilization_ratio,
                    is_adequate=beam_design.is_adequate,
                ))

            # Design connections
            conn_force = dead_per_col * 1.4  # Factored reaction
            conn_design = self.design_connection(
                force_kn=conn_force,
                connection_type="bolted",
                bolt_size_mm=20,
            )
            connections.append(conn_design)

            # Calculate total weight
            col_weight = sum(c.area_mm2 * c.height_m * 7850 / 1e9 for c in columns)
            beam_weight = sum(b.area_mm2 * b.span_m * 7850 / 1e9 for b in beams)
            total_weight = col_weight + beam_weight

            # Build frame design
            frame = FrameDesign(
                num_columns=total_columns,
                num_beams=num_beams,
                columns=columns,
                beams=beams,
                connections=connections,
                total_steel_weight_kg=total_weight,
                max_utilization=max_util,
                governing_case=governing,
                is_adequate=all(c.is_adequate for c in columns) and all(b.is_adequate for b in beams),
                warnings=warnings,
            )

            logger.info(
                f"Frame design complete: {total_columns} columns, {num_beams} beams, "
                f"{total_weight:.0f} kg, max util={max_util:.2f}"
            )

            return frame

        except Exception as e:
            logger.error(f"Frame design error: {e}")
            return FrameDesign(
                num_columns=0,
                num_beams=0,
                columns=[],
                beams=[],
                connections=[],
                is_adequate=False,
                warnings=[f"Design error: {e}"],
            )

    def calculate_anchor_bolts(
        self,
        axial_kn: float,
        shear_kn: float,
        moment_knm: float,
        base_plate_width_mm: float,
        num_bolts: int = 4,
    ) -> Dict[str, Any]:
        """
        Calculate anchor bolt requirements.

        Args:
            axial_kn: Axial load (tension positive)
            shear_kn: Shear load
            moment_knm: Overturning moment
            base_plate_width_mm: Base plate width
            num_bolts: Number of anchor bolts

        Returns:
            Dictionary with anchor bolt design
        """
        result = {
            "num_bolts": num_bolts,
            "warnings": [],
        }

        try:
            # Bolt tension from moment
            lever_arm = base_plate_width_mm * 0.8 / 1000  # Effective lever arm
            tension_from_moment = moment_knm / lever_arm if lever_arm > 0 else 0

            # Total tension per bolt
            tension_per_bolt = (max(0, axial_kn) + tension_from_moment) / (num_bolts / 2)

            # Shear per bolt
            shear_per_bolt = shear_kn / num_bolts

            # Select bolt size (F1554 Grade 55)
            # Capacities for F1554-55 anchors
            bolt_data = {
                "3/4": {"area": 285, "tensile": 65, "shear": 39},
                "1": {"area": 507, "tensile": 115, "shear": 69},
                "1-1/4": {"area": 792, "tensile": 180, "shear": 108},
                "1-1/2": {"area": 1140, "tensile": 259, "shear": 155},
            }

            selected_bolt = None
            for size, data in bolt_data.items():
                # Combined check
                util_tension = tension_per_bolt / data["tensile"]
                util_shear = shear_per_bolt / data["shear"]

                # Interaction (tension + shear)
                interaction = (util_tension ** 2 + util_shear ** 2) ** 0.5

                if interaction <= 1.0:
                    selected_bolt = size
                    result["bolt_size"] = size
                    result["bolt_area_mm2"] = data["area"]
                    result["tension_capacity_kn"] = data["tensile"]
                    result["shear_capacity_kn"] = data["shear"]
                    result["tension_demand_kn"] = tension_per_bolt
                    result["shear_demand_kn"] = shear_per_bolt
                    result["utilization"] = interaction
                    result["is_adequate"] = True
                    break

            if not selected_bolt:
                result["is_adequate"] = False
                result["warnings"].append("No adequate bolt size - increase quantity or size")

            # Embedment length (minimum 12 diameters)
            if selected_bolt:
                bolt_dia_mm = float(selected_bolt.replace("-", ".").split("/")[0]) * 25.4
                result["embedment_mm"] = 12 * bolt_dia_mm

            logger.info(f"Anchor bolts: {num_bolts}x {result.get('bolt_size', 'N/A')}")

        except Exception as e:
            logger.error(f"Anchor bolt calculation error: {e}")
            result["warnings"].append(f"Calculation error: {e}")
            result["is_adequate"] = False

        return result
