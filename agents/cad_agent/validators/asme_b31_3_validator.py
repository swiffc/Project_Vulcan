"""
ASME B31.3 Process Piping Validator
=====================================
Validation for process piping design per ASME B31.3.

Phase 25.7 - ASME B31.3 Piping Checks

Covers:
- Pipe wall thickness calculation
- Pressure design
- Allowable stresses
- Flexibility analysis requirements
- Branch connection reinforcement
- Support spacing
"""

import math
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .validation_models import ValidationIssue, ValidationSeverity

logger = logging.getLogger("vulcan.validator.b31_3")


# =============================================================================
# CONSTANTS - ASME B31.3 Requirements
# =============================================================================

# Allowable stresses (psi) at room temperature
ALLOWABLE_STRESS = {
    "A106-B": 20000,
    "A312-304": 20000,
    "A312-316": 16700,
    "A333-6": 17100,
    "A335-P11": 17800,
    "A335-P22": 15000,
    "A312-304L": 16700,
    "A312-316L": 16700,
}

# Mill tolerances
MILL_TOLERANCE = {
    "seamless": 0.125,  # 12.5%
    "erw": 0.10,  # 10%
    "saw": 0.10,
}

# Weld joint factors (E)
WELD_JOINT_FACTOR = {
    "seamless": 1.0,
    "erw": 0.85,
    "saw": 0.80,
    "furnace_butt_weld": 0.60,
}

# Y coefficient for pressure design (per Table 304.1.1)
Y_COEFFICIENTS = {
    "ferritic_below_900": 0.4,
    "ferritic_above_900": 0.7,
    "austenitic": 0.4,
}

# Support spacing (ft) for Schedule 40 pipe
SUPPORT_SPACING = {
    0.5: 5,   # 1/2"
    0.75: 5,  # 3/4"
    1.0: 7,   # 1"
    1.5: 9,   # 1-1/2"
    2.0: 10,  # 2"
    3.0: 12,  # 3"
    4.0: 14,  # 4"
    6.0: 17,  # 6"
    8.0: 19,  # 8"
    10.0: 22, # 10"
    12.0: 23, # 12"
    14.0: 25, # 14"
    16.0: 27, # 16"
    18.0: 28, # 18"
    20.0: 30, # 20"
    24.0: 32, # 24"
}

# Standard pipe dimensions (OD, wall for Sch 40)
PIPE_DIMENSIONS = {
    0.5: (0.840, 0.109),
    0.75: (1.050, 0.113),
    1.0: (1.315, 0.133),
    1.5: (1.900, 0.145),
    2.0: (2.375, 0.154),
    3.0: (3.500, 0.216),
    4.0: (4.500, 0.237),
    6.0: (6.625, 0.280),
    8.0: (8.625, 0.322),
    10.0: (10.750, 0.365),
    12.0: (12.750, 0.406),
    14.0: (14.0, 0.438),
    16.0: (16.0, 0.500),
    18.0: (18.0, 0.562),
    20.0: (20.0, 0.594),
    24.0: (24.0, 0.688),
}


# =============================================================================
# DATA CLASSES
# =============================================================================

class PipeType(Enum):
    """Pipe manufacturing type."""
    SEAMLESS = "seamless"
    ERW = "erw"
    SAW = "saw"
    FURNACE_BUTT_WELD = "furnace_butt_weld"


@dataclass
class PipeDesignData:
    """Pipe design parameters."""
    nominal_size_in: float = 4.0
    schedule: str = "40"
    pipe_od_in: float = 4.5
    wall_thickness_in: float = 0.237
    material: str = "A106-B"
    pipe_type: str = "seamless"
    design_pressure_psig: float = 150
    design_temp_f: float = 300
    corrosion_allowance_in: float = 0.0625
    fluid: str = "process"


@dataclass
class FlexibilityData:
    """Pipe flexibility analysis data."""
    pipe_size_in: float = 4.0
    pipe_material: str = "A106-B"
    design_temp_f: float = 300
    ambient_temp_f: float = 70
    pipe_length_ft: float = 100
    num_direction_changes: int = 0
    anchored_ends: bool = True
    expansion_loop: bool = False


@dataclass
class BranchConnectionData:
    """Branch connection reinforcement data."""
    header_od_in: float = 8.625
    header_wall_in: float = 0.322
    branch_od_in: float = 4.5
    branch_wall_in: float = 0.237
    design_pressure_psig: float = 150
    reinforcing_pad_thickness_in: float = 0
    weld_size_in: float = 0.25
    connection_angle_deg: float = 90


@dataclass
class ASMEB313Result:
    """Result from ASME B31.3 validation."""
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
# ASME B31.3 VALIDATOR
# =============================================================================

class ASMEB313Validator:
    """
    Validate piping design against ASME B31.3 Process Piping Code.

    Checks:
    - Minimum wall thickness (304.1.2)
    - Pressure design (304.1.1)
    - Branch reinforcement (304.3.3)
    - Support spacing
    - Flexibility requirements (319.4)
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
        standard_ref: str = "ASME B31.3"
    ):
        """Add a validation issue."""
        self.issues.append({
            "severity": severity,
            "check_type": check_type,
            "message": message,
            "suggestion": suggestion,
            "standard_reference": standard_ref,
        })

    def validate_pipe_design(self, data: PipeDesignData) -> ASMEB313Result:
        """
        Validate pipe wall thickness and pressure design.

        Checks:
        - Minimum wall per 304.1.2
        - Pressure wall per 304.1.1
        - Mill tolerance
        - Corrosion allowance
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        # Get material properties
        S = ALLOWABLE_STRESS.get(data.material, 20000)
        E = WELD_JOINT_FACTOR.get(data.pipe_type, 1.0)
        Y = Y_COEFFICIENTS.get("ferritic_below_900", 0.4)
        if data.design_temp_f > 900:
            Y = Y_COEFFICIENTS.get("ferritic_above_900", 0.7)

        # Mill tolerance
        mill_tol = MILL_TOLERANCE.get(data.pipe_type, 0.125)

        # Check 1: Pressure wall thickness per 304.1.1
        checks += 1
        P = data.design_pressure_psig
        D = data.pipe_od_in

        # t = PD / (2(SE + PY))
        t_pressure = (P * D) / (2 * (S * E + P * Y))

        self.calculations["pressure_wall"] = {
            "P_psig": P,
            "D_in": D,
            "S_psi": S,
            "E": E,
            "Y": Y,
            "t_pressure_in": round(t_pressure, 4),
        }

        # Check 2: Total required thickness
        checks += 1
        # t_m = t_pressure + corrosion + mill tolerance
        t_min = t_pressure + data.corrosion_allowance_in
        t_required = t_min / (1 - mill_tol)  # Account for mill tolerance

        self.calculations["required_wall"] = {
            "t_pressure_in": round(t_pressure, 4),
            "corrosion_in": data.corrosion_allowance_in,
            "t_min_in": round(t_min, 4),
            "mill_tolerance": mill_tol,
            "t_required_in": round(t_required, 4),
            "t_provided_in": data.wall_thickness_in,
        }

        if data.wall_thickness_in >= t_required:
            passed += 2  # Both pressure and total thickness OK
        else:
            self._add_issue(
                "critical",
                "wall_thickness",
                f"Wall thickness {data.wall_thickness_in:.3f}\" less than required {t_required:.3f}\"",
                f"Use minimum {math.ceil(t_required * 1000) / 1000:.3f}\" wall or next heavier schedule",
                "ASME B31.3 304.1.2"
            )

        # Check 3: Standard schedule adequacy
        checks += 1
        std_dims = PIPE_DIMENSIONS.get(data.nominal_size_in)
        if std_dims:
            std_od, std_wall = std_dims
            if abs(data.pipe_od_in - std_od) < 0.01 and data.wall_thickness_in >= t_required:
                passed += 1
                self.calculations["schedule_check"] = {
                    "nominal_size_in": data.nominal_size_in,
                    "schedule": data.schedule,
                    "standard_od_in": std_od,
                    "standard_wall_in": std_wall,
                    "adequate": True,
                }
            else:
                self._add_issue("info", "schedule",
                    f"Using non-standard dimensions for {data.nominal_size_in}\" pipe",
                    "Verify with standard pipe schedules")

        # Check 4: Minimum wall absolute
        checks += 1
        # B31.3 recommends minimum 0.065" for carbon steel
        abs_min_wall = 0.065

        if data.wall_thickness_in >= abs_min_wall:
            passed += 1
        else:
            self._add_issue("warning", "min_wall",
                f"Wall thickness {data.wall_thickness_in}\" below practical minimum {abs_min_wall}\"",
                "Consider heavier schedule for handling and corrosion",
                "ASME B31.3")

        return self._build_result(checks, passed)

    def validate_flexibility(self, data: FlexibilityData) -> ASMEB313Result:
        """
        Check piping flexibility requirements per B31.3 319.4.

        Checks:
        - Thermal expansion calculation
        - Flexibility requirement
        - Need for expansion loops
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        # Thermal expansion coefficient (in/100ft/100F for carbon steel)
        alpha = 0.0063  # approximate

        # Check 1: Thermal expansion
        checks += 1
        delta_t = data.design_temp_f - data.ambient_temp_f
        expansion = alpha * (delta_t / 100) * data.pipe_length_ft

        self.calculations["thermal"] = {
            "delta_t_f": delta_t,
            "expansion_in": round(expansion, 3),
            "pipe_length_ft": data.pipe_length_ft,
        }

        if expansion < 1.0:
            passed += 1
        else:
            self._add_issue("info", "thermal_expansion",
                f"Thermal expansion {expansion:.2f}\" - ensure adequate flexibility",
                "Consider expansion loops, offsets, or expansion joints")

        # Check 2: Flexibility criterion (simplified)
        checks += 1
        # B31.3 319.4.1: Formal analysis not required if:
        # D*y/(L-U)^2 <= 0.03 for steel
        # where D = nominal pipe size (in), y = expansion (in), L = developed length (ft), U = anchor distance (ft)
        # Simplified check:
        flexibility_ratio = (data.pipe_size_in * expansion) / (data.pipe_length_ft**2) if data.pipe_length_ft > 0 else 0

        self.calculations["flexibility"] = {
            "ratio": round(flexibility_ratio, 6),
            "limit": 0.03,
            "formal_analysis_required": flexibility_ratio > 0.03,
        }

        if flexibility_ratio <= 0.03:
            passed += 1
        else:
            self._add_issue("warning", "flexibility_analysis",
                f"Flexibility ratio {flexibility_ratio:.4f} > 0.03 - formal analysis required",
                "Perform flexibility analysis per B31.3 319.4",
                "ASME B31.3 319.4.1")

        # Check 3: Direction changes
        checks += 1
        # Rule of thumb: need direction change every 50-100 ft for hot lines
        effective_length = data.pipe_length_ft / max(data.num_direction_changes, 1)

        self.calculations["direction_changes"] = {
            "num_changes": data.num_direction_changes,
            "effective_straight_ft": round(effective_length, 1),
        }

        if delta_t > 100:  # Significant temperature change
            if data.num_direction_changes >= data.pipe_length_ft / 75:
                passed += 1
            else:
                self._add_issue("warning", "direction_changes",
                    f"Long straight runs with {delta_t}F temperature change",
                    "Add elbows or offsets for flexibility",
                    "ASME B31.3 319.4")
        else:
            passed += 1

        # Check 4: Expansion loop recommendation
        checks += 1
        if data.expansion_loop or expansion < 2.0:
            passed += 1
        else:
            self._add_issue("info", "expansion_loop",
                f"Consider expansion loop for {expansion:.2f}\" expansion",
                "Add U-bend or Z-bend expansion loop")

        return self._build_result(checks, passed)

    def validate_branch_reinforcement(self, data: BranchConnectionData) -> ASMEB313Result:
        """
        Validate branch connection reinforcement per B31.3 304.3.

        Checks:
        - Area replacement method
        - Reinforcing pad sizing
        - Weld requirements
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 0
        passed = 0

        # Calculate required and available reinforcement areas

        # Required area (simplified)
        # A1 = t_h * d_b (header wall required × branch opening)
        P = data.design_pressure_psig
        S = 20000  # Assume standard allowable
        E = 1.0

        # Required header wall for pressure
        t_h_req = (P * data.header_od_in) / (2 * (S * E + P * 0.4))
        # Required branch wall for pressure
        t_b_req = (P * data.branch_od_in) / (2 * (S * E + P * 0.4))

        # Branch opening (ID)
        d_b = data.branch_od_in - 2 * data.branch_wall_in

        # Required reinforcement area
        A_required = t_h_req * d_b * math.sin(math.radians(data.connection_angle_deg))

        # Check 1: Area calculation
        checks += 1

        # Available areas
        # A1 = excess header wall
        A1 = (data.header_wall_in - t_h_req) * d_b

        # A2 = excess branch wall (within reinforcement zone)
        reinforcement_height = 2.5 * data.header_wall_in  # Typical
        A2 = 2 * (data.branch_wall_in - t_b_req) * reinforcement_height

        # A3 = reinforcing pad
        A3 = 2 * data.reinforcing_pad_thickness_in * (d_b + 2 * data.header_wall_in)

        # A4 = fillet welds
        A4 = 2 * (0.5 * data.weld_size_in**2) * 2  # Two welds, each triangular

        A_available = A1 + A2 + A3 + A4

        self.calculations["reinforcement"] = {
            "t_h_req_in": round(t_h_req, 4),
            "t_b_req_in": round(t_b_req, 4),
            "d_b_in": round(d_b, 3),
            "A_required_sq_in": round(A_required, 3),
            "A1_excess_header": round(A1, 3),
            "A2_excess_branch": round(A2, 3),
            "A3_pad": round(A3, 3),
            "A4_welds": round(A4, 3),
            "A_available_sq_in": round(A_available, 3),
            "ratio": round(A_available / A_required, 3) if A_required > 0 else 999,
        }

        if A_available >= A_required:
            passed += 1
        else:
            deficit = A_required - A_available
            self._add_issue("critical", "branch_reinforcement",
                f"Reinforcement area deficit: need {A_required:.3f} sq.in, have {A_available:.3f} sq.in",
                f"Add reinforcing pad with area >= {deficit:.3f} sq.in",
                "ASME B31.3 304.3.3")

        # Check 2: Branch/header ratio
        checks += 1
        d_ratio = data.branch_od_in / data.header_od_in

        self.calculations["branch_ratio"] = {
            "branch_od": data.branch_od_in,
            "header_od": data.header_od_in,
            "ratio": round(d_ratio, 3),
        }

        if d_ratio <= 0.5:
            passed += 1  # Small branch, inherently adequate
        else:
            if A_available >= A_required:
                passed += 1
            else:
                self._add_issue("warning", "large_branch",
                    f"Branch/header ratio {d_ratio:.2f} > 0.5 requires careful reinforcement analysis",
                    "Consider full penetration weld or heavier branch")

        # Check 3: Weld size
        checks += 1
        min_weld = min(data.header_wall_in, data.branch_wall_in) * 0.7  # Typical minimum

        if data.weld_size_in >= min_weld:
            passed += 1
        else:
            self._add_issue("error", "weld_size",
                f"Weld size {data.weld_size_in}\" below recommended {min_weld:.3f}\"",
                f"Increase weld to minimum {min_weld:.3f}\"",
                "ASME B31.3 328.5")

        return self._build_result(checks, passed)

    def check_support_spacing(
        self,
        pipe_size_in: float,
        actual_spacing_ft: float,
        insulated: bool = False
    ) -> ASMEB313Result:
        """
        Check support spacing against MSS SP-69/B31.3 guidelines.
        """
        self.issues.clear()
        self.calculations.clear()
        checks = 1
        passed = 0

        # Get recommended spacing
        recommended = SUPPORT_SPACING.get(pipe_size_in, 14)

        # Reduce for insulated pipe
        if insulated:
            recommended = recommended * 0.8

        self.calculations["support_spacing"] = {
            "pipe_size_in": pipe_size_in,
            "recommended_ft": recommended,
            "actual_ft": actual_spacing_ft,
            "insulated": insulated,
        }

        if actual_spacing_ft <= recommended:
            passed += 1
        else:
            self._add_issue("warning", "support_spacing",
                f"Support spacing {actual_spacing_ft} ft exceeds recommended {recommended} ft for {pipe_size_in}\" pipe",
                "Add intermediate supports",
                "MSS SP-69")

        return self._build_result(checks, passed)

    def _build_result(self, total: int, passed: int) -> ASMEB313Result:
        """Build validation result."""
        failed = total - passed
        critical = sum(1 for i in self.issues if i["severity"] == "critical")
        warnings = sum(1 for i in self.issues if i["severity"] == "warning")

        return ASMEB313Result(
            valid=(failed == 0 and critical == 0),
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            critical_failures=critical,
            issues=self.issues.copy(),
            calculations=self.calculations.copy(),
        )
