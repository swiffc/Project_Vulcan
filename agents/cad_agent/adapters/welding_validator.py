"""
Welding Validator - AWS D1.1 & ASME IX Compliance
=================================================
Validates welding symbols, procedures, and quality requirements.

Key Features:
- Weld symbol interpretation (fillet, groove, plug, spot, etc.)
- Minimum weld size per AWS D1.1 Table 2.3
- Joint preparation validation
- WPS/PQR verification
- NDE requirements per ASME VIII

References:
- AWS D1.1-2020 Structural Welding Code - Steel
- ASME Section IX Welding and Brazing Qualifications
- AWS A2.4 Standard Symbols for Welding, Brazing, and Nondestructive Examination

Usage:
    from agents.cad_agent.adapters.welding_validator import WeldingValidator

    validator = WeldingValidator()
    result = validator.validate_weld_callout("1/4\" FILLET WELD ALL AROUND")
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import re
import logging

# Import from standards_db_v2 for enhanced lookups
try:
    from .standards_db_v2 import StandardsDB

    _db = StandardsDB()
except ImportError:
    _db = None
    logging.warning("standards_db_v2 not available, using fallback data")

logger = logging.getLogger("cad_agent.welding-validator")


# =============================================================================
# WELD TYPES & SYMBOLS
# =============================================================================


class WeldType(Enum):
    """Weld types per AWS A2.4."""

    FILLET = "fillet"
    SQUARE_GROOVE = "square_groove"
    V_GROOVE = "v_groove"
    BEVEL_GROOVE = "bevel_groove"
    U_GROOVE = "u_groove"
    J_GROOVE = "j_groove"
    FLARE_V = "flare_v"
    FLARE_BEVEL = "flare_bevel"
    PLUG = "plug"
    SLOT = "slot"
    SPOT = "spot"
    SEAM = "seam"
    SURFACING = "surfacing"
    EDGE = "edge"


class WeldLocation(Enum):
    """Weld location relative to arrow."""

    ARROW_SIDE = "arrow_side"
    OTHER_SIDE = "other_side"
    BOTH_SIDES = "both_sides"


class ContourSymbol(Enum):
    """Weld contour."""

    FLAT = "flat"
    CONVEX = "convex"
    CONCAVE = "concave"


class FinishMethod(Enum):
    """Weld finish method."""

    CHIPPING = "C"
    GRINDING = "G"
    MACHINING = "M"
    ROLLING = "R"
    HAMMERING = "H"


class NDEMethod(Enum):
    """Non-Destructive Examination methods."""

    RT = "radiographic"  # X-ray
    UT = "ultrasonic"  # Sound waves
    MT = "magnetic_particle"  # Ferromagnetic
    PT = "liquid_penetrant"  # Surface defects
    VT = "visual"  # Visual inspection
    ET = "eddy_current"  # Electromagnetic


@dataclass
class WeldSymbol:
    r"""
    Weld symbol per AWS A2.4.

    Example: ___/\\___ (fillet weld symbol on reference line)
    """

    weld_type: WeldType
    location: WeldLocation
    size: Optional[float] = None  # Weld leg size or groove depth
    length: Optional[float] = None  # Length of weld
    pitch: Optional[float] = None  # Spacing for intermittent welds
    contour: Optional[ContourSymbol] = None
    finish: Optional[FinishMethod] = None
    weld_all_around: bool = False  # Circle symbol
    field_weld: bool = False  # Flag symbol
    root_opening: Optional[float] = None  # For groove welds
    groove_angle: Optional[float] = None  # For V, bevel welds

    @property
    def is_intermittent(self) -> bool:
        """Check if intermittent weld."""
        return self.pitch is not None and self.length is not None

    @property
    def effective_throat(self) -> Optional[float]:
        """Calculate effective throat for fillet weld."""
        if self.weld_type == WeldType.FILLET and self.size:
            # For equal leg fillet: throat = 0.707 × leg size
            return 0.707 * self.size
        return None


@dataclass
class WeldProcedure:
    """Welding Procedure Specification (WPS)."""

    wps_number: str
    base_metal_p_number: str  # ASME IX material grouping
    filler_metal_f_number: str  # ASME IX filler grouping
    process: str  # SMAW, GMAW, GTAW, SAW, FCAW
    position: str  # 1G, 2G, 3G, 4G (groove), 1F, 2F, 3F, 4F (fillet)
    preheat_temp: Optional[int] = None  # °F
    interpass_temp_max: Optional[int] = None  # °F
    pwht_required: bool = False  # Post-Weld Heat Treatment
    pwht_temp: Optional[int] = None  # °F
    pwht_time: Optional[float] = None  # hours
    pqr_number: Optional[str] = None  # Supporting Procedure Qualification Record


@dataclass
class NDERequirement:
    """Non-Destructive Examination requirement."""

    method: NDEMethod
    extent: str  # "100%", "25%", "Spot", etc.
    acceptance_standard: str  # AWS D1.1, ASME VIII, etc.
    location: str = "All welds"
    timing: str = "After welding"


@dataclass
class WeldValidationResult:
    """Result of weld validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    weld_symbols_found: int = 0
    min_size_met: bool = True


# =============================================================================
# AWS D1.1 MINIMUM FILLET WELD SIZES
# =============================================================================

# Table 2.3 from AWS D1.1
AWS_MIN_FILLET_WELD_SIZE = {
    # Base metal thickness range (inches): minimum fillet size (inches)
    (0, 0.25): 0.125,  # Up to 1/4": 1/8" fillet
    (0.25, 0.50): 0.1875,  # >1/4" to 1/2": 3/16" fillet
    (0.50, 0.75): 0.25,  # >1/2" to 3/4": 1/4" fillet
    (0.75, 1.50): 0.3125,  # >3/4" to 1-1/2": 5/16" fillet
    (1.50, 2.25): 0.375,  # >1-1/2" to 2-1/4": 3/8" fillet
    (2.25, 6.0): 0.50,  # >2-1/4" to 6": 1/2" fillet
    (6.0, 999): 0.625,  # >6": 5/8" fillet
}


# Maximum fillet weld size
# AWS D1.1 Clause 2.3.2.2
def get_max_fillet_size(plate_thickness: float) -> float:
    """
    Get maximum fillet weld size per AWS D1.1.

    For material < 1/4": Max = thickness
    For material >= 1/4": Max = thickness - 1/16"
    """
    if plate_thickness < 0.25:
        return plate_thickness
    else:
        return plate_thickness - 0.0625


# =============================================================================
# WELDING VALIDATOR
# =============================================================================


class WeldingValidator:
    """
    Validate welding symbols and specifications per AWS D1.1.

    Features:
    - Weld symbol parsing from text
    - Minimum size validation
    - WPS/PQR checking
    - NDE requirements
    """

    def __init__(self):
        self.weld_symbols: list[WeldSymbol] = []
        self.procedures: list[WeldProcedure] = []
        self.nde_requirements: list[NDERequirement] = []

    def validate_weld_callout(
        self, callout: str, base_metal_thickness: float = 0.25
    ) -> WeldValidationResult:
        """
        Validate a weld callout string.

        Args:
            callout: Weld callout text (e.g., "1/4\" FILLET WELD BOTH SIDES")
            base_metal_thickness: Thickness of base metal (inches)

        Returns:
            WeldValidationResult
        """
        result = WeldValidationResult(is_valid=True)

        # Parse weld symbol
        symbol = self._parse_weld_callout(callout)
        if symbol:
            self.weld_symbols.append(symbol)
            result.weld_symbols_found = 1

            # Validate minimum size
            if symbol.weld_type == WeldType.FILLET and symbol.size:
                min_size = get_min_fillet_weld_size(base_metal_thickness)
                max_size = get_max_fillet_size(base_metal_thickness)

                if symbol.size < min_size:
                    result.errors.append(
                        f'Fillet weld size {symbol.size:.4f}" is below AWS D1.1 minimum of {min_size:.4f}" '
                        f'for {base_metal_thickness}" base metal'
                    )
                    result.min_size_met = False

                if symbol.size > max_size:
                    result.warnings.append(
                        f'Fillet weld size {symbol.size:.4f}" exceeds recommended maximum of {max_size:.4f}"'
                    )

                result.info.append(f'Effective throat: {symbol.effective_throat:.4f}"')

            # Check for intermittent weld issues
            if symbol.is_intermittent:
                if symbol.pitch and symbol.length:
                    if symbol.pitch < symbol.length * 1.5:
                        result.warnings.append(
                            f'Intermittent weld pitch ({symbol.pitch}") should be >= 1.5× length ({symbol.length}")'
                        )
        else:
            result.warnings.append(f"Could not parse weld callout: {callout}")

        result.is_valid = len(result.errors) == 0

        return result

    def _parse_weld_callout(self, callout: str) -> Optional[WeldSymbol]:
        """Parse weld callout text into WeldSymbol."""
        callout_upper = callout.upper()

        # Determine weld type
        weld_type = None
        if "FILLET" in callout_upper:
            weld_type = WeldType.FILLET
        elif "V-GROOVE" in callout_upper or "V GROOVE" in callout_upper:
            weld_type = WeldType.V_GROOVE
        elif "BEVEL" in callout_upper:
            weld_type = WeldType.BEVEL_GROOVE
        elif "PLUG" in callout_upper:
            weld_type = WeldType.PLUG
        elif "SPOT" in callout_upper:
            weld_type = WeldType.SPOT
        else:
            return None

        # Extract weld size (e.g., "1/4\"", "0.25")
        size = None
        size_match = re.search(
            r'(\d+/\d+|[0-9.]+)\s*["\']?\s*(?:FILLET|WELD)', callout_upper
        )
        if size_match:
            size_str = size_match.group(1)
            if "/" in size_str:
                # Fraction
                num, denom = size_str.split("/")
                size = float(num) / float(denom)
            else:
                size = float(size_str)

        # Determine location
        location = WeldLocation.ARROW_SIDE
        if "BOTH SIDES" in callout_upper or "BOTH" in callout_upper:
            location = WeldLocation.BOTH_SIDES
        elif "OTHER SIDE" in callout_upper:
            location = WeldLocation.OTHER_SIDE

        # Check for special symbols
        weld_all_around = "ALL AROUND" in callout_upper
        field_weld = "FIELD" in callout_upper

        # Extract intermittent weld info (e.g., "3\" - 6\"" = 3" weld, 6" pitch)
        length = None
        pitch = None
        intermittent_match = re.search(r'(\d+)\s*["\']?\s*-\s*(\d+)\s*["\']?', callout)
        if intermittent_match:
            length = float(intermittent_match.group(1))
            pitch = float(intermittent_match.group(2))

        return WeldSymbol(
            weld_type=weld_type,
            location=location,
            size=size,
            length=length,
            pitch=pitch,
            weld_all_around=weld_all_around,
            field_weld=field_weld,
        )

    def validate_wps(
        self, wps: WeldProcedure, base_metal_spec: str
    ) -> WeldValidationResult:
        """
        Validate Welding Procedure Specification.

        Args:
            wps: WeldProcedure to validate
            base_metal_spec: Base metal specification (e.g., "A36", "A516-70")

        Returns:
            WeldValidationResult
        """
        result = WeldValidationResult(is_valid=True)

        # Check P-number compatibility
        # (Simplified - real implementation would have full P-number table)
        valid_p_numbers = ["1", "3", "4", "5A", "5B", "8"]
        if wps.base_metal_p_number not in valid_p_numbers:
            result.warnings.append(f"Unusual P-number: {wps.base_metal_p_number}")

        # Check for PQR
        if not wps.pqr_number:
            result.warnings.append("No PQR number specified for WPS")

        # Preheat requirements (simplified)
        if "A514" in base_metal_spec or "A517" in base_metal_spec:
            if not wps.preheat_temp or wps.preheat_temp < 200:
                result.warnings.append(
                    "High-strength steel typically requires ≥200°F preheat"
                )

        # PWHT requirements
        if wps.pwht_required and not wps.pwht_temp:
            result.errors.append("PWHT required but temperature not specified")

        result.is_valid = len(result.errors) == 0

        return result

    def check_nde_requirements(
        self, joint_type: str, code: str = "AWS D1.1"
    ) -> list[NDERequirement]:
        """
        Determine NDE requirements based on joint type and code.

        Args:
            joint_type: "butt", "fillet", "corner", etc.
            code: Applicable code ("AWS D1.1", "ASME VIII", etc.)

        Returns:
            List of required NDE methods
        """
        nde_requirements = []

        # Visual testing is always required
        nde_requirements.append(
            NDERequirement(
                method=NDEMethod.VT,
                extent="100%",
                acceptance_standard=code,
                location="All welds",
            )
        )

        if code == "ASME VIII":
            # Pressure vessel requirements
            if joint_type.lower() in ["butt", "full penetration"]:
                nde_requirements.append(
                    NDERequirement(
                        method=NDEMethod.RT,
                        extent="100% or spot per UW-11",
                        acceptance_standard="ASME VIII UW-51",
                        location="Full penetration welds",
                    )
                )

        elif code == "AWS D1.1":
            # Structural welding
            if "critical" in joint_type.lower():
                nde_requirements.append(
                    NDERequirement(
                        method=NDEMethod.UT,
                        extent="100%",
                        acceptance_standard="AWS D1.1 Table 6.1",
                        location="Critical welds",
                    )
                )

        return nde_requirements

    def validate_weld_prep(
        self, joint_type: WeldType, angle_deg: float, root_gap: float
    ) -> WeldValidationResult:
        """
        Validate weld preparation geometry (Rule 33 / ASME B16.25).

        Args:
            joint_type: Type of weld (V_GROOVE, BEVEL_GROOVE)
            angle_deg: Measured bevel angle
            root_gap: Measured root opening

        Returns:
            Validation result
        """
        result = WeldValidationResult(is_valid=True)

        # ASME B16.25 Standard Bevel (for wall thickness < 0.88")
        STD_BEVEL = 37.5
        TOLERANCE = 2.5

        if joint_type in [WeldType.V_GROOVE, WeldType.BEVEL_GROOVE]:
            # Check Angle
            if not (STD_BEVEL - TOLERANCE <= angle_deg <= STD_BEVEL + TOLERANCE):
                result.errors.append(
                    f"Invalid Bevel Angle: {angle_deg}°. Required: {STD_BEVEL}° ±{TOLERANCE}° (ASME B16.25)"
                )

            # Check Root Gap (Rule 33 requires physical gap)
            if root_gap <= 0.001:
                result.errors.append(
                    'Missing Root Gap: Parts are touching (0 gap). Rule 33 requires physical weld gap (e.g., 1/16" or 1/8").'
                )
            elif root_gap > 0.25:
                result.warnings.append(
                    f'Excessive Root Gap: {root_gap}". Standard is typically 1/16" to 1/8".'
                )

        else:
            result.info.append(
                f"Weld prep check skipped for {joint_type.name} (not a groove weld)"
            )

        result.is_valid = len(result.errors) == 0
        return result


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_min_fillet_weld_size(base_metal_thickness: float) -> float:
    """
    Get minimum fillet weld size per AWS D1.1 Table 2.3.

    Args:
        base_metal_thickness: Thickness of thicker part joined (inches)

    Returns:
        Minimum fillet weld leg size (inches)
    """
    for (min_t, max_t), min_size in AWS_MIN_FILLET_WELD_SIZE.items():
        if min_t < base_metal_thickness <= max_t:
            return min_size

    # Default to largest
    return 0.625


def calculate_fillet_weld_strength(
    leg_size: float, length: float, electrode: str = "E70"
) -> dict:
    """
    Calculate fillet weld strength per AISC/AWS.

    Args:
        leg_size: Fillet weld leg size (inches)
        length: Total weld length (inches)
        electrode: Electrode classification (E60, E70, E80, E100)

    Returns:
        Dictionary with capacity calculations
    """
    # Electrode tensile strength (ksi)
    electrode_strength = {
        "E60": 60,
        "E70": 70,
        "E80": 80,
        "E100": 100,
        "E110": 110,
    }

    fexx = electrode_strength.get(electrode, 70)

    # Effective throat = 0.707 × leg size (for equal leg fillet)
    throat = 0.707 * leg_size

    # Nominal weld strength (AISC J2-4)
    fnw = 0.60 * fexx  # Nominal stress (ksi)

    # Weld area
    area = throat * length  # in²

    # Design strength (LRFD)
    phi = 0.75  # Resistance factor for welds
    rn = fnw * area  # Nominal strength (kips)
    design_strength = phi * rn  # Design strength (kips)

    return {
        "effective_throat_in": throat,
        "weld_area_in2": area,
        "nominal_stress_ksi": fnw,
        "nominal_strength_kips": rn,
        "design_strength_kips": design_strength,
        "electrode": electrode,
        "fexx_ksi": fexx,
    }


# =============================================================================
# AWS D1.1 WELD ACCESS & CLEARANCE REQUIREMENTS (Phase 25.4)
# =============================================================================

# Minimum clearances for weld access per AWS D1.1 & fabrication practice
WELD_ACCESS_REQUIREMENTS = {
    # Process: (min_electrode_angle_deg, min_nozzle_clearance_in, min_work_space_in)
    "SMAW": (15, 0.5, 3.0),      # Stick welding
    "GMAW": (15, 0.75, 4.0),     # MIG welding
    "FCAW": (15, 0.75, 4.0),     # Flux-cored
    "GTAW": (15, 0.5, 4.0),      # TIG welding
    "SAW": (0, 2.0, 6.0),        # Submerged arc (vertical down only)
}

# Minimum access dimensions for different joint configurations
JOINT_ACCESS_DIMENSIONS = {
    # Joint type: (min_side_clearance_in, min_overhead_clearance_in)
    "fillet_tee": (1.5, 3.0),
    "fillet_lap": (1.0, 3.0),
    "fillet_corner": (2.0, 3.0),
    "groove_butt": (1.0, 3.0),
    "groove_corner": (2.0, 4.0),
    "plug_slot": (2.0, 4.0),
}

# Minimum torch/electrode work angles by position
POSITION_ANGLE_REQUIREMENTS = {
    # Position: (min_work_angle_deg, max_travel_angle_deg)
    "1F": (45, 15),     # Flat fillet
    "1G": (90, 15),     # Flat groove
    "2F": (45, 15),     # Horizontal fillet
    "2G": (90, 15),     # Horizontal groove
    "3F": (45, 15),     # Vertical fillet
    "3G": (90, 15),     # Vertical groove
    "4F": (45, 15),     # Overhead fillet
    "4G": (90, 15),     # Overhead groove
}


@dataclass
class WeldAccessData:
    """Data for weld access analysis."""
    joint_type: str  # fillet_tee, fillet_lap, groove_butt, etc.
    position: str  # 1F, 2F, 3F, 4F, 1G, 2G, 3G, 4G
    side_clearance: float  # inches
    overhead_clearance: float  # inches
    electrode_angle_available: float  # degrees
    process: str = "SMAW"  # SMAW, GMAW, FCAW, GTAW, SAW
    backing_accessible: bool = True
    back_gouge_possible: bool = True


@dataclass
class WeldAccessResult:
    """Result of weld access validation."""
    access_adequate: bool = True
    electrode_access_ok: bool = True
    clearance_ok: bool = True
    position_feasible: bool = True
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)


def validate_weld_access(access_data: WeldAccessData) -> WeldAccessResult:
    """
    Validate weld access per AWS D1.1 requirements.

    Checks:
    1. Minimum electrode/nozzle clearance for process
    2. Side and overhead clearances for joint type
    3. Work angle feasibility for position
    4. Back gouge and backing accessibility

    Args:
        access_data: WeldAccessData with geometry information

    Returns:
        WeldAccessResult with pass/fail status and issues
    """
    result = WeldAccessResult()

    # Get requirements for process
    process_req = WELD_ACCESS_REQUIREMENTS.get(access_data.process)
    if not process_req:
        result.warnings.append(f"Unknown welding process: {access_data.process}")
        process_req = WELD_ACCESS_REQUIREMENTS["SMAW"]  # Default to SMAW

    min_electrode_angle, min_nozzle_clearance, min_work_space = process_req

    # Check electrode angle
    if access_data.electrode_angle_available < min_electrode_angle:
        result.electrode_access_ok = False
        result.issues.append(
            f"Insufficient electrode angle: {access_data.electrode_angle_available}° available, "
            f"{min_electrode_angle}° minimum required for {access_data.process}"
        )
        result.suggestions.append(
            "Consider: (1) Modify joint design, (2) Use different weld sequence, "
            "(3) Pre-position parts for better access"
        )

    # Check joint type clearances
    joint_req = JOINT_ACCESS_DIMENSIONS.get(access_data.joint_type)
    if joint_req:
        req_side, req_overhead = joint_req

        if access_data.side_clearance < req_side:
            result.clearance_ok = False
            result.issues.append(
                f"Insufficient side clearance: {access_data.side_clearance}\" available, "
                f"{req_side}\" minimum required for {access_data.joint_type}"
            )
            result.suggestions.append(
                "Consider: (1) Relocate adjacent members, (2) Modify weld sequence, "
                "(3) Use shorter electrode/nozzle"
            )

        if access_data.overhead_clearance < req_overhead:
            result.clearance_ok = False
            result.issues.append(
                f"Insufficient overhead clearance: {access_data.overhead_clearance}\" available, "
                f"{req_overhead}\" minimum required for {access_data.joint_type}"
            )

    # Check position feasibility
    position_req = POSITION_ANGLE_REQUIREMENTS.get(access_data.position)
    if position_req:
        min_work_angle, max_travel_angle = position_req
        if access_data.electrode_angle_available < min_work_angle:
            result.position_feasible = False
            result.warnings.append(
                f"Position {access_data.position} may be difficult with "
                f"{access_data.electrode_angle_available}° work angle"
            )

    # Check backing and back gouge access for CJP welds
    if "groove" in access_data.joint_type.lower():
        if not access_data.backing_accessible:
            result.warnings.append(
                "Backing not accessible - may need single-sided CJP with special WPS"
            )
        if not access_data.back_gouge_possible:
            result.warnings.append(
                "Back gouge not possible - verify WPS allows single-sided welding"
            )

    # Set overall access status
    result.access_adequate = result.electrode_access_ok and result.clearance_ok

    return result


def check_weld_sequence_access(
    welds: list,
    assembly_sequence: list
) -> list:
    """
    Check if weld sequence allows adequate access at each step.

    Args:
        welds: List of weld definitions with access requirements
        assembly_sequence: Order of assembly/welding operations

    Returns:
        List of sequence issues and recommendations
    """
    issues = []

    for i, step in enumerate(assembly_sequence):
        weld = next((w for w in welds if w.get("id") == step.get("weld_id")), None)
        if not weld:
            continue

        # Check if previous welds block access
        blocking_welds = [
            w for w in welds
            if w.get("blocks_access_to") == weld.get("id")
            and any(s.get("weld_id") == w.get("id") for s in assembly_sequence[:i])
        ]

        if blocking_welds:
            issues.append({
                "step": i + 1,
                "weld_id": weld.get("id"),
                "issue": f"Access blocked by previous welds: {[w.get('id') for w in blocking_welds]}",
                "suggestion": "Resequence to weld internal joints before closing assemblies"
            })

    return issues


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "WeldingValidator",
    "WeldType",
    "WeldLocation",
    "WeldSymbol",
    "WeldProcedure",
    "NDEMethod",
    "NDERequirement",
    "WeldValidationResult",
    "get_min_fillet_weld_size",
    "get_max_fillet_size",
    "calculate_fillet_weld_strength",
    # Phase 25.4 - Weld Access
    "WeldAccessData",
    "WeldAccessResult",
    "validate_weld_access",
    "check_weld_sequence_access",
    "WELD_ACCESS_REQUIREMENTS",
    "JOINT_ACCESS_DIMENSIONS",
    "POSITION_ANGLE_REQUIREMENTS",
]
