"""
Standards Database for CAD Drawing Verification
================================================
Pre-loaded engineering standards for instant lookup during drawing analysis.

References:
- AISC Steel Manual v15
- AWS D1.1 Structural Welding
- ASME Y14.5 Dimensioning & Tolerancing
- API 661 Air-Cooled Heat Exchangers
- OSHA 1910 Platform/Ladder/Handrail Requirements

Usage:
    from agents.cad_agent.adapters.standards_db import (
        get_beam_properties,
        get_edge_distance,
        get_bend_factor,
        calculate_weight,
        validate_hole_size,
    )
"""

from typing import Optional
from dataclasses import dataclass


# =============================================================================
# AISC W-SHAPES (Wide Flange Beams)
# =============================================================================

W_SHAPES: dict[str, dict] = {
    # Shape: {d: depth, bf: flange width, tw: web thickness, tf: flange thickness, wt: weight/ft}
    "W4x13": {"d": 4.16, "bf": 4.060, "tw": 0.280, "tf": 0.345, "wt": 13},
    "W5x16": {"d": 5.01, "bf": 5.000, "tw": 0.240, "tf": 0.360, "wt": 16},
    "W5x19": {"d": 5.15, "bf": 5.030, "tw": 0.270, "tf": 0.430, "wt": 19},
    "W6x9": {"d": 5.90, "bf": 3.940, "tw": 0.170, "tf": 0.215, "wt": 9},
    "W6x12": {"d": 6.03, "bf": 4.000, "tw": 0.230, "tf": 0.280, "wt": 12},
    "W6x15": {"d": 5.99, "bf": 5.990, "tw": 0.230, "tf": 0.260, "wt": 15},
    "W6x16": {"d": 6.28, "bf": 4.030, "tw": 0.260, "tf": 0.405, "wt": 16},
    "W6x20": {"d": 6.20, "bf": 6.020, "tw": 0.260, "tf": 0.365, "wt": 20},
    "W6x25": {"d": 6.38, "bf": 6.080, "tw": 0.320, "tf": 0.455, "wt": 25},
    "W8x10": {"d": 7.89, "bf": 3.940, "tw": 0.170, "tf": 0.205, "wt": 10},
    "W8x13": {"d": 7.99, "bf": 4.000, "tw": 0.230, "tf": 0.255, "wt": 13},
    "W8x15": {"d": 8.11, "bf": 4.015, "tw": 0.245, "tf": 0.315, "wt": 15},
    "W8x18": {"d": 8.14, "bf": 5.250, "tw": 0.230, "tf": 0.330, "wt": 18},
    "W8x21": {"d": 8.28, "bf": 5.270, "tw": 0.250, "tf": 0.400, "wt": 21},
    "W8x24": {"d": 7.93, "bf": 6.495, "tw": 0.245, "tf": 0.400, "wt": 24},
    "W8x28": {"d": 8.06, "bf": 6.535, "tw": 0.285, "tf": 0.465, "wt": 28},
    "W8x31": {"d": 8.00, "bf": 7.995, "tw": 0.285, "tf": 0.435, "wt": 31},
    "W8x35": {"d": 8.12, "bf": 8.020, "tw": 0.310, "tf": 0.495, "wt": 35},
    "W8x40": {"d": 8.25, "bf": 8.070, "tw": 0.360, "tf": 0.560, "wt": 40},
    "W8x48": {"d": 8.50, "bf": 8.110, "tw": 0.400, "tf": 0.685, "wt": 48},
    "W8x58": {"d": 8.75, "bf": 8.220, "tw": 0.510, "tf": 0.810, "wt": 58},
    "W8x67": {"d": 9.00, "bf": 8.280, "tw": 0.570, "tf": 0.935, "wt": 67},
    "W10x12": {"d": 9.87, "bf": 3.960, "tw": 0.190, "tf": 0.210, "wt": 12},
    "W10x15": {"d": 9.99, "bf": 4.000, "tw": 0.230, "tf": 0.270, "wt": 15},
    "W10x17": {"d": 10.11, "bf": 4.010, "tw": 0.240, "tf": 0.330, "wt": 17},
    "W10x19": {"d": 10.24, "bf": 4.020, "tw": 0.250, "tf": 0.395, "wt": 19},
    "W10x22": {"d": 10.17, "bf": 5.750, "tw": 0.240, "tf": 0.360, "wt": 22},
    "W10x26": {"d": 10.33, "bf": 5.770, "tw": 0.260, "tf": 0.440, "wt": 26},
    "W10x30": {"d": 10.47, "bf": 5.810, "tw": 0.300, "tf": 0.510, "wt": 30},
    "W10x33": {"d": 9.73, "bf": 7.960, "tw": 0.290, "tf": 0.435, "wt": 33},
    "W10x39": {"d": 9.92, "bf": 7.985, "tw": 0.315, "tf": 0.530, "wt": 39},
    "W10x45": {"d": 10.10, "bf": 8.020, "tw": 0.350, "tf": 0.620, "wt": 45},
    "W10x49": {"d": 9.98, "bf": 10.000, "tw": 0.340, "tf": 0.560, "wt": 49},
    "W10x54": {"d": 10.09, "bf": 10.030, "tw": 0.370, "tf": 0.615, "wt": 54},
    "W10x60": {"d": 10.22, "bf": 10.080, "tw": 0.420, "tf": 0.680, "wt": 60},
    "W12x14": {"d": 11.91, "bf": 3.970, "tw": 0.200, "tf": 0.225, "wt": 14},
    "W12x16": {"d": 11.99, "bf": 3.990, "tw": 0.220, "tf": 0.265, "wt": 16},
    "W12x19": {"d": 12.16, "bf": 4.005, "tw": 0.235, "tf": 0.350, "wt": 19},
    "W12x22": {"d": 12.31, "bf": 4.030, "tw": 0.260, "tf": 0.425, "wt": 22},
    "W12x26": {"d": 12.22, "bf": 6.490, "tw": 0.230, "tf": 0.380, "wt": 26},
    "W12x30": {"d": 12.34, "bf": 6.520, "tw": 0.260, "tf": 0.440, "wt": 30},
    "W12x35": {"d": 12.50, "bf": 6.560, "tw": 0.300, "tf": 0.520, "wt": 35},
    "W12x40": {"d": 11.94, "bf": 8.005, "tw": 0.295, "tf": 0.515, "wt": 40},
    "W12x45": {"d": 12.06, "bf": 8.045, "tw": 0.335, "tf": 0.575, "wt": 45},
    "W12x50": {"d": 12.19, "bf": 8.080, "tw": 0.370, "tf": 0.640, "wt": 50},
    "W12x53": {"d": 12.06, "bf": 9.995, "tw": 0.345, "tf": 0.575, "wt": 53},
    "W12x58": {"d": 12.19, "bf": 10.010, "tw": 0.360, "tf": 0.640, "wt": 58},
    "W12x65": {"d": 12.12, "bf": 12.000, "tw": 0.390, "tf": 0.605, "wt": 65},
    "W12x72": {"d": 12.25, "bf": 12.040, "tw": 0.430, "tf": 0.670, "wt": 72},
    "W12x79": {"d": 12.38, "bf": 12.080, "tw": 0.470, "tf": 0.735, "wt": 79},
    "W12x87": {"d": 12.53, "bf": 12.125, "tw": 0.515, "tf": 0.810, "wt": 87},
    "W12x96": {"d": 12.71, "bf": 12.160, "tw": 0.550, "tf": 0.900, "wt": 96},
    "W12x106": {"d": 12.89, "bf": 12.220, "tw": 0.610, "tf": 0.990, "wt": 106},
}


# =============================================================================
# AISC ANGLES (Equal Leg)
# =============================================================================

ANGLES: dict[str, dict] = {
    # L{leg}x{leg}x{t}: {leg, t, wt}
    "L2x2x1/8": {"leg": 2.0, "t": 0.125, "wt": 0.98},
    "L2x2x3/16": {"leg": 2.0, "t": 0.1875, "wt": 1.44},
    "L2x2x1/4": {"leg": 2.0, "t": 0.250, "wt": 1.88},
    "L2x2x5/16": {"leg": 2.0, "t": 0.3125, "wt": 2.31},
    "L2-1/2x2-1/2x3/16": {"leg": 2.5, "t": 0.1875, "wt": 1.83},
    "L2-1/2x2-1/2x1/4": {"leg": 2.5, "t": 0.250, "wt": 2.38},
    "L2-1/2x2-1/2x5/16": {"leg": 2.5, "t": 0.3125, "wt": 2.93},
    "L3x3x3/16": {"leg": 3.0, "t": 0.1875, "wt": 3.71},
    "L3x3x1/4": {"leg": 3.0, "t": 0.250, "wt": 4.90},
    "L3x3x5/16": {"leg": 3.0, "t": 0.3125, "wt": 6.10},
    "L3x3x3/8": {"leg": 3.0, "t": 0.375, "wt": 7.20},
    "L3x3x1/2": {"leg": 3.0, "t": 0.500, "wt": 9.40},
    "L3-1/2x3-1/2x1/4": {"leg": 3.5, "t": 0.250, "wt": 5.80},
    "L3-1/2x3-1/2x5/16": {"leg": 3.5, "t": 0.3125, "wt": 7.20},
    "L3-1/2x3-1/2x3/8": {"leg": 3.5, "t": 0.375, "wt": 8.50},
    "L3-1/2x3-1/2x1/2": {"leg": 3.5, "t": 0.500, "wt": 11.10},
    "L4x4x1/4": {"leg": 4.0, "t": 0.250, "wt": 6.60},
    "L4x4x5/16": {"leg": 4.0, "t": 0.3125, "wt": 8.20},
    "L4x4x3/8": {"leg": 4.0, "t": 0.375, "wt": 9.80},
    "L4x4x1/2": {"leg": 4.0, "t": 0.500, "wt": 12.80},
    "L4x4x5/8": {"leg": 4.0, "t": 0.625, "wt": 15.70},
    "L5x5x5/16": {"leg": 5.0, "t": 0.3125, "wt": 10.30},
    "L5x5x3/8": {"leg": 5.0, "t": 0.375, "wt": 12.30},
    "L5x5x1/2": {"leg": 5.0, "t": 0.500, "wt": 16.20},
    "L5x5x5/8": {"leg": 5.0, "t": 0.625, "wt": 20.00},
    "L5x5x3/4": {"leg": 5.0, "t": 0.750, "wt": 23.60},
    "L6x6x3/8": {"leg": 6.0, "t": 0.375, "wt": 14.90},
    "L6x6x1/2": {"leg": 6.0, "t": 0.500, "wt": 19.60},
    "L6x6x5/8": {"leg": 6.0, "t": 0.625, "wt": 24.20},
    "L6x6x3/4": {"leg": 6.0, "t": 0.750, "wt": 28.70},
    "L8x8x1/2": {"leg": 8.0, "t": 0.500, "wt": 26.40},
    "L8x8x5/8": {"leg": 8.0, "t": 0.625, "wt": 32.70},
    "L8x8x3/4": {"leg": 8.0, "t": 0.750, "wt": 38.90},
    "L8x8x1": {"leg": 8.0, "t": 1.000, "wt": 51.00},
}


# =============================================================================
# SHEET METAL GAUGES
# =============================================================================

SHEET_GAUGES: dict[str, dict] = {
    # Gauge: {t: thickness in inches, wt_sqft: weight per sq ft for steel}
    "7GA": {"t": 0.1793, "wt_sqft": 7.50},
    "8GA": {"t": 0.1644, "wt_sqft": 6.875},
    "9GA": {"t": 0.1495, "wt_sqft": 6.25},
    "10GA": {"t": 0.1345, "wt_sqft": 5.625},
    "11GA": {"t": 0.1196, "wt_sqft": 5.00},
    "12GA": {"t": 0.1046, "wt_sqft": 4.375},
    "13GA": {"t": 0.0897, "wt_sqft": 3.75},
    "14GA": {"t": 0.0747, "wt_sqft": 3.125},
    "15GA": {"t": 0.0673, "wt_sqft": 2.8125},
    "16GA": {"t": 0.0598, "wt_sqft": 2.50},
    "17GA": {"t": 0.0538, "wt_sqft": 2.25},
    "18GA": {"t": 0.0478, "wt_sqft": 2.00},
    "19GA": {"t": 0.0418, "wt_sqft": 1.75},
    "20GA": {"t": 0.0359, "wt_sqft": 1.50},
    "22GA": {"t": 0.0299, "wt_sqft": 1.25},
    "24GA": {"t": 0.0239, "wt_sqft": 1.00},
    "26GA": {"t": 0.0179, "wt_sqft": 0.75},
}


# =============================================================================
# PLATE THICKNESSES
# =============================================================================

PLATE_THICKNESSES: dict[str, dict] = {
    # Fraction: {t: thickness in inches, wt_sqft: weight per sq ft for steel}
    "1/16": {"t": 0.0625, "wt_sqft": 2.55},
    "3/32": {"t": 0.09375, "wt_sqft": 3.83},
    "1/8": {"t": 0.125, "wt_sqft": 5.10},
    "5/32": {"t": 0.15625, "wt_sqft": 6.38},
    "3/16": {"t": 0.1875, "wt_sqft": 7.65},
    "1/4": {"t": 0.250, "wt_sqft": 10.20},
    "5/16": {"t": 0.3125, "wt_sqft": 12.75},
    "3/8": {"t": 0.375, "wt_sqft": 15.30},
    "7/16": {"t": 0.4375, "wt_sqft": 17.85},
    "1/2": {"t": 0.500, "wt_sqft": 20.40},
    "9/16": {"t": 0.5625, "wt_sqft": 22.95},
    "5/8": {"t": 0.625, "wt_sqft": 25.50},
    "11/16": {"t": 0.6875, "wt_sqft": 28.05},
    "3/4": {"t": 0.750, "wt_sqft": 30.60},
    "13/16": {"t": 0.8125, "wt_sqft": 33.15},
    "7/8": {"t": 0.875, "wt_sqft": 35.70},
    "15/16": {"t": 0.9375, "wt_sqft": 38.25},
    "1": {"t": 1.000, "wt_sqft": 40.80},
    "1-1/8": {"t": 1.125, "wt_sqft": 45.90},
    "1-1/4": {"t": 1.250, "wt_sqft": 51.00},
    "1-1/2": {"t": 1.500, "wt_sqft": 61.20},
    "2": {"t": 2.000, "wt_sqft": 81.60},
}


# =============================================================================
# EDGE DISTANCES (AISC Table J3.4)
# =============================================================================

EDGE_DISTANCES: dict[str, dict] = {
    # Bolt size: {hole: standard hole diameter, min_sheared, min_rolled}
    "1/2": {"hole": 0.5625, "min_sheared": 0.875, "min_rolled": 0.75},
    "5/8": {"hole": 0.6875, "min_sheared": 1.125, "min_rolled": 0.875},
    "3/4": {"hole": 0.8125, "min_sheared": 1.25, "min_rolled": 1.00},
    "7/8": {"hole": 0.9375, "min_sheared": 1.50, "min_rolled": 1.125},
    "1": {"hole": 1.0625, "min_sheared": 1.75, "min_rolled": 1.25},
    "1-1/8": {"hole": 1.25, "min_sheared": 2.00, "min_rolled": 1.50},
    "1-1/4": {"hole": 1.375, "min_sheared": 2.25, "min_rolled": 1.625},
}


# =============================================================================
# STANDARD HOLE SIZES (AISC)
# =============================================================================

HOLE_SIZES: dict[str, dict] = {
    # Bolt size: {standard, oversize, short_slot, long_slot}
    "1/2": {"std": 0.5625, "over": 0.625, "short": "9/16x11/16", "long": "9/16x1-1/4"},
    "5/8": {"std": 0.6875, "over": 0.8125, "short": "11/16x7/8", "long": "11/16x1-9/16"},
    "3/4": {"std": 0.8125, "over": 0.9375, "short": "13/16x1", "long": "13/16x1-7/8"},
    "7/8": {"std": 0.9375, "over": 1.0625, "short": "15/16x1-1/8", "long": "15/16x2-3/16"},
    "1": {"std": 1.0625, "over": 1.25, "short": "1-1/16x1-5/16", "long": "1-1/16x2-1/2"},
    "1-1/8": {"std": 1.1875, "over": 1.4375, "short": "1-3/16x1-1/2", "long": "1-3/16x2-13/16"},
    "1-1/4": {"std": 1.3125, "over": 1.5625, "short": "1-5/16x1-11/16", "long": "1-5/16x3-1/8"},
}


# =============================================================================
# MINIMUM WELD SIZES (AWS D1.1)
# =============================================================================

MIN_FILLET_WELDS: dict[str, float] = {
    # Base metal thickness range: minimum fillet weld size
    "<=1/4": 0.125,       # 1/8"
    ">1/4 to 1/2": 0.1875,  # 3/16"
    ">1/2 to 3/4": 0.25,    # 1/4"
    ">3/4 to 1-1/2": 0.3125,  # 5/16"
    ">1-1/2 to 2-1/4": 0.375,  # 3/8"
    ">2-1/4 to 6": 0.50,     # 1/2"
    ">6": 0.625,            # 5/8"
}


# =============================================================================
# BEND RADII (by material)
# =============================================================================

BEND_FACTORS: dict[str, float] = {
    # Material: factor (multiply by thickness for min inside radius)
    "1010": 0.5,      # Soft steel
    "1018": 0.75,     # Low carbon
    "A36": 1.0,       # Mild steel
    "A572-50": 1.5,   # High strength low alloy
    "A514": 2.0,      # Quenched & tempered
    "SS304": 1.5,     # Stainless steel
    "SS316": 1.5,
    "AL5052": 1.0,    # Aluminum alloys
    "AL6061-T6": 1.5,
    "AL3003": 0.5,
}


# =============================================================================
# MATERIAL DENSITIES (lb/in³)
# =============================================================================

DENSITIES: dict[str, float] = {
    "steel": 0.284,
    "carbon_steel": 0.284,
    "stainless": 0.289,
    "ss304": 0.289,
    "ss316": 0.289,
    "aluminum": 0.098,
    "brass": 0.307,
    "bronze": 0.320,
    "copper": 0.323,
    "cast_iron": 0.260,
}


# =============================================================================
# API 661 FAN TIP CLEARANCES
# =============================================================================

FAN_TIP_CLEARANCES: dict[str, float] = {
    # Fan diameter range: max radial clearance (inches)
    "4-5ft": 0.375,    # 3/8"
    "6-8ft": 0.50,     # 1/2"
    "9-12ft": 0.625,   # 5/8"
    "13-18ft": 0.75,   # 3/4"
    "19-28ft": 1.00,   # 1"
    ">28ft": 1.25,     # 1-1/4"
}


# =============================================================================
# OSHA PLATFORM REQUIREMENTS
# =============================================================================

@dataclass
class PlatformRequirements:
    min_width_in: float
    load_psf: float
    handrail_height_in: float = 42.0
    midrail_height_in: float = 21.0
    toeboard_height_in: float = 4.0


PLATFORM_REQUIREMENTS: dict[str, PlatformRequirements] = {
    "header_walkway": PlatformRequirements(min_width_in=30, load_psf=50),
    "motor_platform": PlatformRequirements(min_width_in=36, load_psf=75),
    "ballroom_walkway": PlatformRequirements(min_width_in=60, load_psf=100),
    "interconnecting": PlatformRequirements(min_width_in=24, load_psf=50),
}


# =============================================================================
# OSHA LADDER REQUIREMENTS (1910.23)
# =============================================================================

LADDER_REQUIREMENTS: dict[str, float] = {
    "rung_spacing_in": 12.0,
    "min_rung_diameter_in": 0.75,
    "min_width_clear_in": 16.0,
    "cage_required_height_ft": 20.0,
    "landing_max_height_ft": 30.0,
    "extension_above_landing_in": 42.0,
    "clearance_behind_rungs_in": 7.0,
}


# =============================================================================
# OSHA STAIR REQUIREMENTS (1910.25)
# =============================================================================

STAIR_REQUIREMENTS: dict[str, float] = {
    "min_width_in": 22.0,
    "min_riser_in": 6.0,
    "max_riser_in": 7.5,
    "min_tread_depth_in": 9.5,
    "min_handrail_height_in": 30.0,
    "max_handrail_height_in": 37.0,
    "min_angle_deg": 30.0,
    "max_angle_deg": 50.0,
    "landing_max_rise_ft": 12.0,
}


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================

def get_beam_properties(shape: str) -> Optional[dict]:
    """Get properties for a W-shape beam."""
    # Normalize input (W8x31 -> W8x31, W8X31 -> W8x31)
    normalized = shape.upper().replace("X", "x")
    return W_SHAPES.get(normalized)


def get_angle_properties(shape: str) -> Optional[dict]:
    """Get properties for an angle shape."""
    normalized = shape.upper().replace("X", "x")
    return ANGLES.get(normalized)


def get_gauge_thickness(gauge: str) -> Optional[float]:
    """Get thickness for a sheet metal gauge."""
    # Handle various formats: 10GA, 10 GA, 10 GAUGE
    clean = gauge.upper().replace(" ", "").replace("GAUGE", "GA")
    if clean in SHEET_GAUGES:
        return SHEET_GAUGES[clean]["t"]
    return None


def get_plate_thickness(fraction: str) -> Optional[float]:
    """Get thickness for a plate specified as a fraction."""
    # Handle various formats: 1/4", 1/4, 0.250
    clean = fraction.replace('"', '').replace("'", '').strip()
    if clean in PLATE_THICKNESSES:
        return PLATE_THICKNESSES[clean]["t"]
    return None


def get_edge_distance(bolt_size: str, edge_type: str = "rolled") -> Optional[float]:
    """
    Get minimum edge distance for a bolt size.

    Args:
        bolt_size: Bolt diameter as fraction (e.g., "3/4", "1/2")
        edge_type: "rolled" or "sheared"

    Returns:
        Minimum edge distance in inches
    """
    clean = bolt_size.replace('"', '').strip()
    if clean in EDGE_DISTANCES:
        key = f"min_{edge_type}"
        return EDGE_DISTANCES[clean].get(key)
    return None


def get_standard_hole(bolt_size: str) -> Optional[float]:
    """Get standard hole diameter for a bolt size."""
    clean = bolt_size.replace('"', '').strip()
    if clean in HOLE_SIZES:
        return HOLE_SIZES[clean]["std"]
    return None


def get_bend_factor(material: str) -> float:
    """
    Get bend radius factor for a material.
    Returns factor to multiply by thickness for minimum inside radius.
    """
    # Try exact match first
    if material.upper() in BEND_FACTORS:
        return BEND_FACTORS[material.upper()]

    # Try partial matches
    material_upper = material.upper()
    if "A572" in material_upper or "HSLA" in material_upper:
        return BEND_FACTORS["A572-50"]
    if "A36" in material_upper:
        return BEND_FACTORS["A36"]
    if "304" in material_upper:
        return BEND_FACTORS["SS304"]
    if "316" in material_upper:
        return BEND_FACTORS["SS316"]

    # Default to mild steel
    return 1.0


def get_density(material: str) -> float:
    """Get density for a material in lb/in³."""
    material_lower = material.lower()

    # Try exact match
    if material_lower in DENSITIES:
        return DENSITIES[material_lower]

    # Try partial matches
    if "stainless" in material_lower or "ss" in material_lower:
        return DENSITIES["stainless"]
    if "aluminum" in material_lower or "al" in material_lower:
        return DENSITIES["aluminum"]
    if "brass" in material_lower:
        return DENSITIES["brass"]
    if "bronze" in material_lower:
        return DENSITIES["bronze"]

    # Default to carbon steel
    return DENSITIES["steel"]


def get_min_fillet_weld(base_metal_thickness: float) -> float:
    """Get minimum fillet weld size for a given base metal thickness."""
    if base_metal_thickness <= 0.25:
        return 0.125
    elif base_metal_thickness <= 0.50:
        return 0.1875
    elif base_metal_thickness <= 0.75:
        return 0.25
    elif base_metal_thickness <= 1.50:
        return 0.3125
    elif base_metal_thickness <= 2.25:
        return 0.375
    elif base_metal_thickness <= 6.0:
        return 0.50
    else:
        return 0.625


def get_fan_tip_clearance(fan_diameter_ft: float) -> float:
    """Get maximum tip clearance for a fan diameter per API 661."""
    if fan_diameter_ft <= 5:
        return 0.375
    elif fan_diameter_ft <= 8:
        return 0.50
    elif fan_diameter_ft <= 12:
        return 0.625
    elif fan_diameter_ft <= 18:
        return 0.75
    elif fan_diameter_ft <= 28:
        return 1.00
    else:
        return 1.25


# =============================================================================
# CALCULATION FUNCTIONS
# =============================================================================

def calculate_beam_weight(shape: str, length_ft: float) -> Optional[float]:
    """Calculate weight of a beam given shape and length."""
    props = get_beam_properties(shape)
    if props:
        return props["wt"] * length_ft
    return None


def calculate_plate_weight(
    length_in: float,
    width_in: float,
    thickness_in: float,
    material: str = "steel"
) -> float:
    """Calculate weight of a plate in pounds."""
    volume = length_in * width_in * thickness_in
    density = get_density(material)
    return volume * density


def calculate_angle_weight(shape: str, length_ft: float) -> Optional[float]:
    """Calculate weight of an angle given shape and length."""
    props = get_angle_properties(shape)
    if props:
        return props["wt"] * length_ft
    return None


def calculate_min_bend_radius(thickness: float, material: str) -> float:
    """Calculate minimum inside bend radius for a given thickness and material."""
    factor = get_bend_factor(material)
    return thickness * factor


def validate_edge_distance(
    actual_distance: float,
    bolt_size: str,
    edge_type: str = "rolled"
) -> tuple[bool, str]:
    """
    Validate an edge distance against AISC requirements.

    Returns:
        Tuple of (is_valid, message)
    """
    min_dist = get_edge_distance(bolt_size, edge_type)
    if min_dist is None:
        return False, f"Unknown bolt size: {bolt_size}"

    if actual_distance < min_dist:
        return False, f"Edge distance {actual_distance}\" < min {min_dist}\" for {bolt_size}\" bolt"

    return True, f"Edge distance {actual_distance}\" OK (min {min_dist}\")"


def validate_bend_radius(
    actual_radius: float,
    thickness: float,
    material: str
) -> tuple[bool, str]:
    """
    Validate a bend radius against material requirements.

    Returns:
        Tuple of (is_valid, message)
    """
    min_radius = calculate_min_bend_radius(thickness, material)

    if actual_radius < min_radius:
        return False, f"Bend radius R{actual_radius}\" < min R{min_radius}\" for {material}"

    return True, f"Bend radius R{actual_radius}\" OK (min R{min_radius}\")"


def validate_hole_size(
    hole_diameter: float,
    bolt_size: str
) -> tuple[bool, str]:
    """
    Validate a hole size is standard for the bolt.

    Returns:
        Tuple of (is_valid, message)
    """
    hole_data = HOLE_SIZES.get(bolt_size.replace('"', '').strip())
    if hole_data is None:
        return False, f"Unknown bolt size: {bolt_size}"

    if abs(hole_diameter - hole_data["std"]) < 0.01:
        return True, f"Standard hole Ø{hole_diameter}\" for {bolt_size}\" bolt"

    if abs(hole_diameter - hole_data["over"]) < 0.01:
        return True, f"Oversize hole Ø{hole_diameter}\" for {bolt_size}\" bolt"

    return False, f"Non-standard hole Ø{hole_diameter}\" for {bolt_size}\" bolt (std={hole_data['std']}\")"


def validate_weight(
    stated_weight: float,
    calculated_weight: float,
    tolerance: float = 0.10
) -> tuple[bool, str]:
    """
    Validate stated weight against calculated weight.

    Args:
        stated_weight: Weight shown on drawing
        calculated_weight: Calculated weight
        tolerance: Acceptable difference (default 10%)

    Returns:
        Tuple of (is_valid, message)
    """
    if stated_weight == 0:
        return False, "Stated weight is zero"

    diff = abs(stated_weight - calculated_weight)
    diff_pct = diff / stated_weight

    if diff_pct <= tolerance:
        return True, f"Weight OK: {stated_weight:.1f} lb (calc {calculated_weight:.1f} lb, diff {diff_pct*100:.1f}%)"

    return False, f"Weight mismatch: {stated_weight:.1f} lb vs calc {calculated_weight:.1f} lb ({diff_pct*100:.1f}% diff)"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data tables
    "W_SHAPES",
    "ANGLES",
    "SHEET_GAUGES",
    "PLATE_THICKNESSES",
    "EDGE_DISTANCES",
    "HOLE_SIZES",
    "MIN_FILLET_WELDS",
    "BEND_FACTORS",
    "DENSITIES",
    "FAN_TIP_CLEARANCES",
    "PLATFORM_REQUIREMENTS",
    "LADDER_REQUIREMENTS",
    "STAIR_REQUIREMENTS",
    # Lookup functions
    "get_beam_properties",
    "get_angle_properties",
    "get_gauge_thickness",
    "get_plate_thickness",
    "get_edge_distance",
    "get_standard_hole",
    "get_bend_factor",
    "get_density",
    "get_min_fillet_weld",
    "get_fan_tip_clearance",
    # Calculation functions
    "calculate_beam_weight",
    "calculate_plate_weight",
    "calculate_angle_weight",
    "calculate_min_bend_radius",
    # Validation functions
    "validate_edge_distance",
    "validate_bend_radius",
    "validate_hole_size",
    "validate_weight",
]
