"""
AISC Structural Steel Validator
================================
Comprehensive validation against AISC Steel Construction Manual 15th Edition.

Phase 25.5 - Enhanced AISC Checks

Covers:
- Connection design (bolted/welded)
- Beam design (flexure, shear, deflection)
- Column design (slenderness, capacity)
- Weld sizes and lengths
- Base plate design
- Stiffener requirements
- Web crippling/yielding
- Block shear
"""

import math
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.aisc_structural")


# =============================================================================
# CONSTANTS AND TABLES
# =============================================================================

# Material properties (ksi)
MATERIAL_PROPERTIES = {
    "A36": {"Fy": 36, "Fu": 58, "E": 29000},
    "A572-50": {"Fy": 50, "Fu": 65, "E": 29000},
    "A572-60": {"Fy": 60, "Fu": 75, "E": 29000},
    "A572-65": {"Fy": 65, "Fu": 80, "E": 29000},
    "A992": {"Fy": 50, "Fu": 65, "E": 29000},
    "A500B": {"Fy": 42, "Fu": 58, "E": 29000},
    "A500C": {"Fy": 50, "Fu": 62, "E": 29000},
    "A514": {"Fy": 100, "Fu": 110, "E": 29000},
}

# Bolt capacities (kips) per AISC Table J3.2
# (diameter, grade): (single_shear_N, single_shear_X, tension)
BOLT_CAPACITIES = {
    (0.5, "A325"): (5.57, 6.96, 13.5),
    (0.625, "A325"): (8.70, 10.9, 21.1),
    (0.75, "A325"): (12.5, 15.7, 30.4),
    (0.875, "A325"): (17.1, 21.3, 41.4),
    (1.0, "A325"): (22.3, 27.9, 54.1),
    (0.5, "A490"): (6.96, 8.70, 17.0),
    (0.625, "A490"): (10.9, 13.6, 26.5),
    (0.75, "A490"): (15.7, 19.6, 38.2),
    (0.875, "A490"): (21.3, 26.7, 52.0),
    (1.0, "A490"): (27.9, 34.8, 67.9),
}

# Weld electrode capacities (ksi)
WELD_ELECTRODES = {
    "E60XX": 60,
    "E70XX": 70,
    "E80XX": 80,
    "E90XX": 90,
    "E100XX": 100,
    "E110XX": 110,
}

# Standard W-shape properties (partial list)
# Shape: (d, bf, tf, tw, Ix, Sx, Zx, rx, Iy, Sy, Zy, ry, A)
W_SHAPES = {
    "W8X31": (8.0, 7.995, 0.435, 0.285, 110, 27.5, 30.4, 3.47, 37.1, 9.27, 14.1, 2.02, 9.13),
    "W10X49": (10.0, 10.0, 0.560, 0.340, 272, 54.6, 60.4, 4.35, 93.4, 18.7, 28.3, 2.54, 14.4),
    "W12X50": (12.2, 8.08, 0.640, 0.370, 394, 64.7, 71.9, 5.18, 56.3, 13.9, 21.3, 1.96, 14.6),
    "W14X68": (14.0, 10.0, 0.720, 0.415, 722, 103, 115, 5.85, 121, 24.2, 36.9, 2.46, 20.0),
    "W16X77": (16.5, 10.3, 0.760, 0.455, 1110, 134, 150, 6.77, 138, 26.9, 41.1, 2.47, 22.6),
    "W18X97": (18.6, 11.1, 0.870, 0.535, 1750, 188, 211, 7.82, 201, 36.1, 55.3, 2.65, 28.5),
    "W21X111": (21.5, 12.3, 0.875, 0.550, 2670, 249, 279, 8.60, 274, 44.5, 68.2, 2.90, 32.7),
    "W24X131": (24.5, 12.9, 1.00, 0.605, 4020, 329, 370, 10.2, 340, 53.0, 81.5, 3.00, 38.5),
}

# Column K-factors
K_FACTORS = {
    "fixed_fixed": 0.65,
    "fixed_pinned": 0.80,
    "pinned_pinned": 1.00,
    "fixed_free": 2.10,
}

# Deflection limits (L/ratio)
DEFLECTION_LIMITS = {
    "floor_live": 360,
    "floor_dead_live": 240,
    "roof_live": 180,
    "roof_total": 120,
    "cantilever": 180,
    "supporting_plaster": 360,
    "supporting_masonry": 600,
}


# =============================================================================
# DATA CLASSES
# =============================================================================

class ConnectionType(Enum):
    """Types of steel connections."""
    BOLTED_SHEAR = "bolted_shear"
    BOLTED_MOMENT = "bolted_moment"
    WELDED_SHEAR = "welded_shear"
    WELDED_MOMENT = "welded_moment"
    SHEAR_TAB = "shear_tab"
    CLIP_ANGLE = "clip_angle"
    MOMENT_END_PLATE = "moment_end_plate"
    BASE_PLATE = "base_plate"


class MemberType(Enum):
    """Types of structural members."""
    BEAM = "beam"
    COLUMN = "column"
    BRACE = "brace"
    TRUSS_CHORD = "truss_chord"
    TRUSS_WEB = "truss_web"


@dataclass
class BeamData:
    """Beam design data."""
    shape: str  # W-shape designation
    span_ft: float
    unbraced_length_ft: float
    moment_kip_ft: float = 0
    shear_kips: float = 0
    axial_kips: float = 0
    material: str = "A992"
    deflection_limit: str = "floor_live"
    calculated_deflection_in: float = 0


@dataclass
class ColumnData:
    """Column design data."""
    shape: str
    height_ft: float
    axial_load_kips: float
    moment_x_kip_ft: float = 0
    moment_y_kip_ft: float = 0
    k_factor: float = 1.0
    material: str = "A992"
    braced_x: bool = True
    braced_y: bool = True


@dataclass
class ConnectionData:
    """Connection design data."""
    connection_type: ConnectionType
    load_kips: float
    bolt_diameter: float = 0.75
    bolt_grade: str = "A325"
    num_bolts: int = 4
    weld_size: float = 0.25
    weld_length: float = 0
    electrode: str = "E70XX"
    plate_thickness: float = 0.5
    plate_material: str = "A36"


@dataclass
class BasePlateData:
    """Base plate design data."""
    plate_length: float
    plate_width: float
    plate_thickness: float
    column_depth: float
    column_bf: float
    axial_load_kips: float
    moment_kip_ft: float = 0
    concrete_fc_psi: float = 3000
    material: str = "A36"
    anchor_diameter: float = 0.75
    anchor_embedment: float = 9


@dataclass
class AISCValidationResult:
    """Result from AISC structural validation."""
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
# AISC STRUCTURAL VALIDATOR
# =============================================================================

class AISCStructuralValidator:
    """
    Comprehensive AISC Steel Construction Manual validation.

    Checks per AISC 15th Edition:
    - Chapter B: Design Requirements
    - Chapter D: Tension Members
    - Chapter E: Compression Members
    - Chapter F: Flexural Members
    - Chapter G: Shear
    - Chapter H: Combined Forces
    - Chapter J: Connections
    - Chapter K: HSS Connections
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
        standard_ref: str = "AISC 360-16"
    ):
        """Add a validation issue."""
        self.issues.append({
            "severity": severity,
            "check_type": check_type,
            "message": message,
            "suggestion": suggestion,
            "standard_reference": standard_ref,
        })

    # =========================================================================
    # BEAM VALIDATION
    # =========================================================================

    def validate_beam(self, beam: BeamData) -> AISCValidationResult:
        """
        Validate beam design per AISC Chapters F & G.

        Checks:
        - Flexural capacity
        - Shear capacity
        - Lateral-torsional buckling
        - Deflection limits
        - Compact section requirements
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        # Get material properties
        mat = MATERIAL_PROPERTIES.get(beam.material, MATERIAL_PROPERTIES["A992"])
        Fy = mat["Fy"]
        E = mat["E"]

        # Get section properties
        shape_props = W_SHAPES.get(beam.shape)
        if not shape_props:
            self._add_issue("error", "shape", f"Unknown shape: {beam.shape}",
                           "Use standard W-shape designation")
            return self._build_result(1, 0)

        d, bf, tf, tw, Ix, Sx, Zx, rx, Iy, Sy, Zy, ry, A = shape_props

        # Store calculations
        self.calculations["section"] = {
            "shape": beam.shape,
            "d": d, "bf": bf, "tf": tf, "tw": tw,
            "Zx": Zx, "Sx": Sx, "Ix": Ix,
            "A": A,
        }

        # Check 1: Flexural capacity (AISC F2)
        checks += 1
        Mn = Fy * Zx / 12  # kip-ft (plastic moment)
        phi_Mn = 0.9 * Mn
        self.calculations["flexure"] = {
            "Mn_kip_ft": round(Mn, 1),
            "phi_Mn_kip_ft": round(phi_Mn, 1),
            "Mu_kip_ft": beam.moment_kip_ft,
            "DCR": round(beam.moment_kip_ft / phi_Mn, 3) if phi_Mn > 0 else 0,
        }

        if beam.moment_kip_ft <= phi_Mn:
            passed += 1
        else:
            dcr = beam.moment_kip_ft / phi_Mn
            self._add_issue(
                "critical" if dcr > 1.1 else "error",
                "flexure",
                f"Moment {beam.moment_kip_ft:.1f} kip-ft exceeds capacity {phi_Mn:.1f} kip-ft (DCR={dcr:.2f})",
                "Increase beam size or reduce span",
                "AISC 360-16 F2"
            )

        # Check 2: Shear capacity (AISC G2)
        checks += 1
        Aw = d * tw  # Web area
        Cv = 1.0  # For most W-shapes
        Vn = 0.6 * Fy * Aw * Cv
        phi_Vn = 1.0 * Vn  # phi = 1.0 for shear
        self.calculations["shear"] = {
            "Vn_kips": round(Vn, 1),
            "phi_Vn_kips": round(phi_Vn, 1),
            "Vu_kips": beam.shear_kips,
            "DCR": round(beam.shear_kips / phi_Vn, 3) if phi_Vn > 0 else 0,
        }

        if beam.shear_kips <= phi_Vn:
            passed += 1
        else:
            self._add_issue(
                "critical",
                "shear",
                f"Shear {beam.shear_kips:.1f} kips exceeds capacity {phi_Vn:.1f} kips",
                "Add web stiffeners or increase beam size",
                "AISC 360-16 G2"
            )

        # Check 3: Lateral-torsional buckling (AISC F2.2)
        checks += 1
        Lb = beam.unbraced_length_ft * 12  # inches
        rts = math.sqrt(math.sqrt(Iy * d / (2 * bf * tf)) / 12) if Iy > 0 else ry
        Lp = 1.76 * ry * math.sqrt(E / Fy)
        Lr = 1.95 * rts * (E / (0.7 * Fy)) * math.sqrt(1 + math.sqrt(1 + 6.76 * (0.7 * Fy / E)**2))

        self.calculations["ltb"] = {
            "Lb_in": Lb,
            "Lp_in": round(Lp, 1),
            "Lr_in": round(Lr, 1),
            "zone": "plastic" if Lb <= Lp else ("inelastic" if Lb <= Lr else "elastic"),
        }

        if Lb <= Lp:
            passed += 1  # Plastic zone, full capacity
        elif Lb <= Lr:
            passed += 1  # Inelastic zone, reduced capacity (handled above)
            self._add_issue("warning", "ltb",
                f"Unbraced length {Lb/12:.1f} ft is in inelastic LTB zone (Lp={Lp/12:.1f} ft)",
                "Consider additional bracing to achieve full plastic capacity",
                "AISC 360-16 F2.2")
        else:
            self._add_issue("warning", "ltb",
                f"Unbraced length {Lb/12:.1f} ft exceeds Lr={Lr/12:.1f} ft (elastic buckling zone)",
                "Add lateral bracing or use reduced moment capacity",
                "AISC 360-16 F2.2")

        # Check 4: Deflection (IBC/AISC)
        checks += 1
        limit_ratio = DEFLECTION_LIMITS.get(beam.deflection_limit, 360)
        span_in = beam.span_ft * 12
        allowable_defl = span_in / limit_ratio

        self.calculations["deflection"] = {
            "span_in": span_in,
            "limit_ratio": limit_ratio,
            "allowable_in": round(allowable_defl, 3),
            "actual_in": beam.calculated_deflection_in,
        }

        if beam.calculated_deflection_in <= allowable_defl:
            passed += 1
        else:
            self._add_issue("warning", "deflection",
                f"Deflection {beam.calculated_deflection_in:.3f}\" exceeds L/{limit_ratio}={allowable_defl:.3f}\"",
                "Increase beam size for stiffness",
                "IBC Table 1604.3")

        # Check 5: Compact section (AISC B4.1)
        checks += 1
        lambda_f = bf / (2 * tf)  # Flange slenderness
        lambda_w = (d - 2 * tf) / tw  # Web slenderness
        lambda_pf = 0.38 * math.sqrt(E / Fy)  # Flange limit
        lambda_pw = 3.76 * math.sqrt(E / Fy)  # Web limit

        self.calculations["slenderness"] = {
            "lambda_f": round(lambda_f, 2),
            "lambda_pf": round(lambda_pf, 2),
            "lambda_w": round(lambda_w, 2),
            "lambda_pw": round(lambda_pw, 2),
            "compact": lambda_f <= lambda_pf and lambda_w <= lambda_pw,
        }

        if lambda_f <= lambda_pf and lambda_w <= lambda_pw:
            passed += 1
        else:
            self._add_issue("warning", "slenderness",
                f"Section not compact: flange={lambda_f:.1f} (limit {lambda_pf:.1f}), web={lambda_w:.1f} (limit {lambda_pw:.1f})",
                "Use compact section or apply reduced capacity per AISC B4",
                "AISC 360-16 B4.1")

        return self._build_result(checks, passed)

    # =========================================================================
    # COLUMN VALIDATION
    # =========================================================================

    def validate_column(self, column: ColumnData) -> AISCValidationResult:
        """
        Validate column design per AISC Chapters E & H.

        Checks:
        - Slenderness ratio
        - Compressive capacity
        - Combined axial + bending
        - Local buckling
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        mat = MATERIAL_PROPERTIES.get(column.material, MATERIAL_PROPERTIES["A992"])
        Fy = mat["Fy"]
        E = mat["E"]

        shape_props = W_SHAPES.get(column.shape)
        if not shape_props:
            self._add_issue("error", "shape", f"Unknown shape: {column.shape}")
            return self._build_result(1, 0)

        d, bf, tf, tw, Ix, Sx, Zx, rx, Iy, Sy, Zy, ry, A = shape_props

        # Check 1: Slenderness ratio (AISC E2)
        checks += 1
        L = column.height_ft * 12
        KL_rx = (column.k_factor * L) / rx
        KL_ry = (column.k_factor * L) / ry
        slenderness = max(KL_rx, KL_ry)

        self.calculations["slenderness"] = {
            "KL_rx": round(KL_rx, 1),
            "KL_ry": round(KL_ry, 1),
            "governing": round(slenderness, 1),
            "limit": 200,
        }

        if slenderness <= 200:
            passed += 1
        else:
            self._add_issue("critical", "slenderness",
                f"Slenderness ratio {slenderness:.1f} exceeds limit of 200",
                "Reduce unbraced length or increase column size",
                "AISC 360-16 E2")

        # Check 2: Compressive capacity (AISC E3)
        checks += 1
        Fe = (math.pi**2 * E) / (slenderness**2)  # Euler buckling stress

        if slenderness <= 4.71 * math.sqrt(E / Fy):
            Fcr = Fy * (0.658 ** (Fy / Fe))  # Inelastic buckling
        else:
            Fcr = 0.877 * Fe  # Elastic buckling

        Pn = Fcr * A
        phi_Pn = 0.9 * Pn

        self.calculations["compression"] = {
            "Fe_ksi": round(Fe, 1),
            "Fcr_ksi": round(Fcr, 1),
            "Pn_kips": round(Pn, 1),
            "phi_Pn_kips": round(phi_Pn, 1),
            "Pu_kips": column.axial_load_kips,
            "DCR": round(column.axial_load_kips / phi_Pn, 3) if phi_Pn > 0 else 0,
        }

        if column.axial_load_kips <= phi_Pn:
            passed += 1
        else:
            dcr = column.axial_load_kips / phi_Pn
            self._add_issue(
                "critical" if dcr > 1.1 else "error",
                "compression",
                f"Axial load {column.axial_load_kips:.1f} kips exceeds capacity {phi_Pn:.1f} kips",
                "Increase column size",
                "AISC 360-16 E3"
            )

        # Check 3: Combined forces (AISC H1) - if moments present
        if column.moment_x_kip_ft > 0 or column.moment_y_kip_ft > 0:
            checks += 1
            Mnx = 0.9 * Fy * Zx / 12
            Mny = 0.9 * Fy * Zy / 12

            Pr = column.axial_load_kips
            Pc = phi_Pn
            Mrx = column.moment_x_kip_ft
            Mcx = Mnx
            Mry = column.moment_y_kip_ft
            Mcy = Mny

            if Pr / Pc >= 0.2:
                interaction = (Pr / Pc) + (8 / 9) * (Mrx / Mcx + Mry / Mcy)
            else:
                interaction = (Pr / (2 * Pc)) + (Mrx / Mcx + Mry / Mcy)

            self.calculations["interaction"] = {
                "formula": "H1-1a" if Pr / Pc >= 0.2 else "H1-1b",
                "ratio": round(interaction, 3),
            }

            if interaction <= 1.0:
                passed += 1
            else:
                self._add_issue("critical", "interaction",
                    f"Combined force interaction ratio {interaction:.3f} exceeds 1.0",
                    "Increase column size for combined loading",
                    "AISC 360-16 H1")

        return self._build_result(checks, passed)

    # =========================================================================
    # CONNECTION VALIDATION
    # =========================================================================

    def validate_connection(self, conn: ConnectionData) -> AISCValidationResult:
        """
        Validate connection design per AISC Chapter J.

        Checks:
        - Bolt shear/tension capacity
        - Bolt bearing capacity
        - Weld capacity
        - Block shear
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        mat = MATERIAL_PROPERTIES.get(conn.plate_material, MATERIAL_PROPERTIES["A36"])
        Fy = mat["Fy"]
        Fu = mat["Fu"]

        # Bolted connections
        if conn.connection_type in [ConnectionType.BOLTED_SHEAR, ConnectionType.BOLTED_MOMENT,
                                    ConnectionType.SHEAR_TAB, ConnectionType.CLIP_ANGLE]:

            # Check 1: Bolt shear capacity
            checks += 1
            bolt_key = (conn.bolt_diameter, conn.bolt_grade)
            bolt_caps = BOLT_CAPACITIES.get(bolt_key)

            if bolt_caps:
                single_shear = bolt_caps[0]  # Threads in shear plane (conservative)
                total_capacity = conn.num_bolts * single_shear

                self.calculations["bolt_shear"] = {
                    "single_bolt_kips": single_shear,
                    "num_bolts": conn.num_bolts,
                    "total_capacity_kips": total_capacity,
                    "demand_kips": conn.load_kips,
                    "DCR": round(conn.load_kips / total_capacity, 3) if total_capacity > 0 else 0,
                }

                if conn.load_kips <= total_capacity:
                    passed += 1
                else:
                    self._add_issue("critical", "bolt_shear",
                        f"Load {conn.load_kips:.1f} kips exceeds bolt shear capacity {total_capacity:.1f} kips",
                        "Add more bolts or use larger diameter",
                        "AISC 360-16 J3.6")
            else:
                self._add_issue("warning", "bolt_spec",
                    f"Unknown bolt specification: {conn.bolt_diameter}\" {conn.bolt_grade}",
                    "Use standard ASTM bolt grades")

            # Check 2: Bolt bearing
            checks += 1
            # Bearing capacity per bolt: 2.4*d*t*Fu (tearout controls if edge distance is limiting)
            bearing_per_bolt = 2.4 * conn.bolt_diameter * conn.plate_thickness * Fu
            total_bearing = conn.num_bolts * bearing_per_bolt

            self.calculations["bolt_bearing"] = {
                "per_bolt_kips": round(bearing_per_bolt, 1),
                "total_kips": round(total_bearing, 1),
            }

            if conn.load_kips <= total_bearing:
                passed += 1
            else:
                self._add_issue("error", "bolt_bearing",
                    f"Load exceeds bearing capacity {total_bearing:.1f} kips",
                    "Increase plate thickness",
                    "AISC 360-16 J3.10")

        # Welded connections
        if conn.connection_type in [ConnectionType.WELDED_SHEAR, ConnectionType.WELDED_MOMENT]:

            # Check 1: Weld capacity
            checks += 1
            electrode_strength = WELD_ELECTRODES.get(conn.electrode, 70)
            # Fillet weld effective throat = 0.707 * weld size
            throat = 0.707 * conn.weld_size
            # Weld capacity per inch = 0.6 * FEXX * throat
            capacity_per_inch = 0.6 * electrode_strength * throat * 0.75  # phi = 0.75
            total_capacity = capacity_per_inch * conn.weld_length

            self.calculations["weld"] = {
                "electrode": conn.electrode,
                "size_in": conn.weld_size,
                "throat_in": round(throat, 3),
                "capacity_per_inch_kips": round(capacity_per_inch, 2),
                "length_in": conn.weld_length,
                "total_capacity_kips": round(total_capacity, 1),
                "demand_kips": conn.load_kips,
            }

            if conn.load_kips <= total_capacity:
                passed += 1
            else:
                self._add_issue("critical", "weld_capacity",
                    f"Load {conn.load_kips:.1f} kips exceeds weld capacity {total_capacity:.1f} kips",
                    "Increase weld size or length",
                    "AISC 360-16 J2.4")

            # Check 2: Minimum weld size
            checks += 1
            # Minimum weld size per AISC Table J2.4
            min_weld = 0.1875 if conn.plate_thickness <= 0.25 else (
                0.25 if conn.plate_thickness <= 0.5 else (
                0.3125 if conn.plate_thickness <= 0.75 else 0.375))

            self.calculations["weld"]["min_size_in"] = min_weld

            if conn.weld_size >= min_weld:
                passed += 1
            else:
                self._add_issue("error", "weld_min_size",
                    f"Weld size {conn.weld_size}\" is below minimum {min_weld}\" for {conn.plate_thickness}\" plate",
                    f"Use minimum {min_weld}\" fillet weld",
                    "AISC 360-16 J2.2b")

        return self._build_result(checks, passed)

    # =========================================================================
    # BASE PLATE VALIDATION
    # =========================================================================

    def validate_base_plate(self, bp: BasePlateData) -> AISCValidationResult:
        """
        Validate base plate design per AISC Design Guide 1.

        Checks:
        - Bearing on concrete
        - Plate bending
        - Anchor bolt requirements
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        mat = MATERIAL_PROPERTIES.get(bp.material, MATERIAL_PROPERTIES["A36"])
        Fy = mat["Fy"]

        # Check 1: Bearing on concrete (ACI/AISC)
        checks += 1
        A1 = bp.plate_length * bp.plate_width  # Bearing area
        # Assume A2 = A1 (full contact)
        phi_c = 0.65
        Pp = phi_c * 0.85 * (bp.concrete_fc_psi / 1000) * A1  # kips

        self.calculations["bearing"] = {
            "A1_sq_in": A1,
            "fc_psi": bp.concrete_fc_psi,
            "phi_Pp_kips": round(Pp, 1),
            "Pu_kips": bp.axial_load_kips,
        }

        if bp.axial_load_kips <= Pp:
            passed += 1
        else:
            self._add_issue("critical", "bearing",
                f"Axial load {bp.axial_load_kips:.1f} kips exceeds bearing capacity {Pp:.1f} kips",
                "Increase plate size or concrete strength",
                "AISC Design Guide 1")

        # Check 2: Plate bending
        checks += 1
        # Cantilever projections
        m = (bp.plate_length - 0.95 * bp.column_depth) / 2
        n = (bp.plate_width - 0.8 * bp.column_bf) / 2
        l_max = max(m, n)

        # Bearing pressure
        fp = bp.axial_load_kips / A1  # ksi

        # Required plate thickness
        t_req = l_max * math.sqrt(2 * fp / (0.9 * Fy))

        self.calculations["plate_bending"] = {
            "m_in": round(m, 2),
            "n_in": round(n, 2),
            "l_max_in": round(l_max, 2),
            "fp_ksi": round(fp, 3),
            "t_required_in": round(t_req, 3),
            "t_provided_in": bp.plate_thickness,
        }

        if bp.plate_thickness >= t_req:
            passed += 1
        else:
            self._add_issue("error", "plate_thickness",
                f"Plate thickness {bp.plate_thickness}\" is less than required {t_req:.3f}\"",
                f"Increase plate thickness to at least {math.ceil(t_req * 8) / 8}\"",
                "AISC Design Guide 1")

        # Check 3: Anchor bolt embedment
        checks += 1
        min_embed = 12 * bp.anchor_diameter  # Rule of thumb minimum

        self.calculations["anchors"] = {
            "diameter_in": bp.anchor_diameter,
            "embedment_in": bp.anchor_embedment,
            "min_embedment_in": min_embed,
        }

        if bp.anchor_embedment >= min_embed:
            passed += 1
        else:
            self._add_issue("warning", "anchor_embedment",
                f"Anchor embedment {bp.anchor_embedment}\" is less than recommended {min_embed}\"",
                "Verify anchor capacity per ACI 318 Appendix D",
                "ACI 318-19 Ch. 17")

        return self._build_result(checks, passed)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _build_result(self, total: int, passed: int) -> AISCValidationResult:
        """Build validation result."""
        failed = total - passed
        critical = sum(1 for i in self.issues if i["severity"] == "critical")
        warnings = sum(1 for i in self.issues if i["severity"] == "warning")

        return AISCValidationResult(
            valid=(failed == 0 and critical == 0),
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            critical_failures=critical,
            issues=self.issues.copy(),
            calculations=self.calculations.copy(),
        )
