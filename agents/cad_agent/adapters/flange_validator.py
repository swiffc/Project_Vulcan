"""
ASME B16.5 Flange Validator
===========================
Validates pipe flanges against ASME B16.5 standard for pressure piping.

References:
- ASME B16.5-2020 Pipe Flanges and Flanged Fittings
- ASME B16.47 Large Diameter Steel Flanges (NPS 26-60)
- API 661 Section 7.1 - Nozzle connections

Common ACHE Applications:
- Inlet/outlet nozzles
- Drain connections
- Vent connections
- Steam/hot oil headers

Usage:
    from agents.cad_agent.adapters.flange_validator import (
        get_flange_dimensions,
        validate_flange,
        validate_flange_pair,
        get_pressure_rating,
    )
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class FlangeClass(Enum):
    """ASME B16.5 pressure classes."""
    CLASS_150 = 150
    CLASS_300 = 300
    CLASS_400 = 400
    CLASS_600 = 600
    CLASS_900 = 900
    CLASS_1500 = 1500
    CLASS_2500 = 2500


class FacingType(Enum):
    """Flange facing types per ASME B16.5."""
    RAISED_FACE = "RF"           # Most common
    FLAT_FACE = "FF"             # Cast iron mating
    RING_JOINT = "RTJ"           # High pressure
    LAP_JOINT = "LJ"             # Lined pipe
    MALE_FEMALE = "MF"           # Legacy
    TONGUE_GROOVE = "TG"         # Legacy


@dataclass
class FlangeDimensions:
    """Dimensional data for a flange per ASME B16.5."""
    nps: str                      # Nominal pipe size (e.g., "4", "6")
    rating_class: int             # 150, 300, 600, etc.
    od: float                     # Outside diameter (inches)
    thickness: float              # Flange thickness (inches)
    raised_face_od: float         # Raised face OD (inches)
    raised_face_height: float     # RF height (inches) - 0.06 for Class 150/300
    bolt_circle: float            # Bolt circle diameter (inches)
    num_bolts: int                # Number of bolts
    bolt_diameter: str            # Bolt diameter (e.g., "3/4")
    bolt_hole_diameter: float     # Bolt hole diameter (inches)
    hub_diameter: float           # Hub diameter at base (inches)
    hub_length: float             # Length through hub (inches)
    weight_approx: float          # Approximate weight (lbs)


@dataclass
class PressureRating:
    """Pressure-temperature rating per ASME B16.5 Table 2."""
    class_rating: int
    material_group: str           # e.g., "1.1" (carbon steel)
    temp_f: float
    max_pressure_psi: float


@dataclass
class FlangeValidationResult:
    """Result of flange validation."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    details: dict


# =============================================================================
# ASME B16.5 FLANGE DIMENSIONS
# =============================================================================
# Source: ASME B16.5-2020 Tables
# Format: (NPS, Class) -> FlangeDimensions

FLANGE_DIMENSIONS: dict[tuple[str, int], FlangeDimensions] = {
    # =========================================================================
    # CLASS 150 FLANGES
    # =========================================================================
    ("1/2", 150): FlangeDimensions(
        nps="1/2", rating_class=150, od=3.50, thickness=0.44,
        raised_face_od=1.38, raised_face_height=0.06, bolt_circle=2.38,
        num_bolts=4, bolt_diameter="1/2", bolt_hole_diameter=0.62,
        hub_diameter=1.19, hub_length=0.62, weight_approx=1.0
    ),
    ("3/4", 150): FlangeDimensions(
        nps="3/4", rating_class=150, od=3.88, thickness=0.50,
        raised_face_od=1.69, raised_face_height=0.06, bolt_circle=2.75,
        num_bolts=4, bolt_diameter="1/2", bolt_hole_diameter=0.62,
        hub_diameter=1.50, hub_length=0.62, weight_approx=2.0
    ),
    ("1", 150): FlangeDimensions(
        nps="1", rating_class=150, od=4.25, thickness=0.56,
        raised_face_od=2.00, raised_face_height=0.06, bolt_circle=3.12,
        num_bolts=4, bolt_diameter="1/2", bolt_hole_diameter=0.62,
        hub_diameter=1.94, hub_length=0.69, weight_approx=2.5
    ),
    ("1-1/4", 150): FlangeDimensions(
        nps="1-1/4", rating_class=150, od=4.62, thickness=0.62,
        raised_face_od=2.50, raised_face_height=0.06, bolt_circle=3.50,
        num_bolts=4, bolt_diameter="1/2", bolt_hole_diameter=0.62,
        hub_diameter=2.31, hub_length=0.75, weight_approx=3.0
    ),
    ("1-1/2", 150): FlangeDimensions(
        nps="1-1/2", rating_class=150, od=5.00, thickness=0.69,
        raised_face_od=2.88, raised_face_height=0.06, bolt_circle=3.88,
        num_bolts=4, bolt_diameter="1/2", bolt_hole_diameter=0.62,
        hub_diameter=2.56, hub_length=0.81, weight_approx=4.0
    ),
    ("2", 150): FlangeDimensions(
        nps="2", rating_class=150, od=6.00, thickness=0.75,
        raised_face_od=3.62, raised_face_height=0.06, bolt_circle=4.75,
        num_bolts=4, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=3.06, hub_length=0.88, weight_approx=5.5
    ),
    ("2-1/2", 150): FlangeDimensions(
        nps="2-1/2", rating_class=150, od=7.00, thickness=0.88,
        raised_face_od=4.12, raised_face_height=0.06, bolt_circle=5.50,
        num_bolts=4, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=3.56, hub_length=1.00, weight_approx=8.0
    ),
    ("3", 150): FlangeDimensions(
        nps="3", rating_class=150, od=7.50, thickness=0.94,
        raised_face_od=5.00, raised_face_height=0.06, bolt_circle=6.00,
        num_bolts=4, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=4.25, hub_length=1.06, weight_approx=10.0
    ),
    ("4", 150): FlangeDimensions(
        nps="4", rating_class=150, od=9.00, thickness=0.94,
        raised_face_od=6.19, raised_face_height=0.06, bolt_circle=7.50,
        num_bolts=8, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=5.31, hub_length=1.06, weight_approx=14.0
    ),
    ("5", 150): FlangeDimensions(
        nps="5", rating_class=150, od=10.00, thickness=0.94,
        raised_face_od=7.31, raised_face_height=0.06, bolt_circle=8.50,
        num_bolts=8, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=6.44, hub_length=1.06, weight_approx=17.0
    ),
    ("6", 150): FlangeDimensions(
        nps="6", rating_class=150, od=11.00, thickness=1.00,
        raised_face_od=8.50, raised_face_height=0.06, bolt_circle=9.50,
        num_bolts=8, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=7.56, hub_length=1.12, weight_approx=22.0
    ),
    ("8", 150): FlangeDimensions(
        nps="8", rating_class=150, od=13.50, thickness=1.12,
        raised_face_od=10.62, raised_face_height=0.06, bolt_circle=11.75,
        num_bolts=8, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=9.69, hub_length=1.25, weight_approx=36.0
    ),
    ("10", 150): FlangeDimensions(
        nps="10", rating_class=150, od=16.00, thickness=1.19,
        raised_face_od=12.75, raised_face_height=0.06, bolt_circle=14.25,
        num_bolts=12, bolt_diameter="7/8", bolt_hole_diameter=1.00,
        hub_diameter=12.00, hub_length=1.31, weight_approx=50.0
    ),
    ("12", 150): FlangeDimensions(
        nps="12", rating_class=150, od=19.00, thickness=1.25,
        raised_face_od=15.00, raised_face_height=0.06, bolt_circle=17.00,
        num_bolts=12, bolt_diameter="7/8", bolt_hole_diameter=1.00,
        hub_diameter=14.38, hub_length=1.38, weight_approx=70.0
    ),
    ("14", 150): FlangeDimensions(
        nps="14", rating_class=150, od=21.00, thickness=1.38,
        raised_face_od=16.25, raised_face_height=0.06, bolt_circle=18.75,
        num_bolts=12, bolt_diameter="1", bolt_hole_diameter=1.12,
        hub_diameter=15.75, hub_length=1.50, weight_approx=90.0
    ),
    ("16", 150): FlangeDimensions(
        nps="16", rating_class=150, od=23.50, thickness=1.44,
        raised_face_od=18.50, raised_face_height=0.06, bolt_circle=21.25,
        num_bolts=16, bolt_diameter="1", bolt_hole_diameter=1.12,
        hub_diameter=18.00, hub_length=1.56, weight_approx=115.0
    ),
    ("18", 150): FlangeDimensions(
        nps="18", rating_class=150, od=25.00, thickness=1.56,
        raised_face_od=21.00, raised_face_height=0.06, bolt_circle=22.75,
        num_bolts=16, bolt_diameter="1-1/8", bolt_hole_diameter=1.25,
        hub_diameter=19.88, hub_length=1.69, weight_approx=140.0
    ),
    ("20", 150): FlangeDimensions(
        nps="20", rating_class=150, od=27.50, thickness=1.69,
        raised_face_od=23.00, raised_face_height=0.06, bolt_circle=25.00,
        num_bolts=20, bolt_diameter="1-1/8", bolt_hole_diameter=1.25,
        hub_diameter=22.00, hub_length=1.81, weight_approx=175.0
    ),
    ("24", 150): FlangeDimensions(
        nps="24", rating_class=150, od=32.00, thickness=1.88,
        raised_face_od=27.25, raised_face_height=0.06, bolt_circle=29.50,
        num_bolts=20, bolt_diameter="1-1/4", bolt_hole_diameter=1.38,
        hub_diameter=26.12, hub_length=2.00, weight_approx=260.0
    ),

    # =========================================================================
    # CLASS 300 FLANGES
    # =========================================================================
    ("1/2", 300): FlangeDimensions(
        nps="1/2", rating_class=300, od=3.75, thickness=0.56,
        raised_face_od=1.38, raised_face_height=0.06, bolt_circle=2.62,
        num_bolts=4, bolt_diameter="1/2", bolt_hole_diameter=0.62,
        hub_diameter=1.19, hub_length=0.88, weight_approx=2.0
    ),
    ("3/4", 300): FlangeDimensions(
        nps="3/4", rating_class=300, od=4.62, thickness=0.62,
        raised_face_od=1.69, raised_face_height=0.06, bolt_circle=3.25,
        num_bolts=4, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=1.50, hub_length=0.94, weight_approx=3.0
    ),
    ("1", 300): FlangeDimensions(
        nps="1", rating_class=300, od=4.88, thickness=0.69,
        raised_face_od=2.00, raised_face_height=0.06, bolt_circle=3.50,
        num_bolts=4, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=1.94, hub_length=1.00, weight_approx=4.0
    ),
    ("1-1/2", 300): FlangeDimensions(
        nps="1-1/2", rating_class=300, od=6.12, thickness=0.81,
        raised_face_od=2.88, raised_face_height=0.06, bolt_circle=4.50,
        num_bolts=4, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=2.56, hub_length=1.12, weight_approx=7.0
    ),
    ("2", 300): FlangeDimensions(
        nps="2", rating_class=300, od=6.50, thickness=0.88,
        raised_face_od=3.62, raised_face_height=0.06, bolt_circle=5.00,
        num_bolts=8, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=3.06, hub_length=1.19, weight_approx=9.0
    ),
    ("3", 300): FlangeDimensions(
        nps="3", rating_class=300, od=8.25, thickness=1.12,
        raised_face_od=5.00, raised_face_height=0.06, bolt_circle=6.62,
        num_bolts=8, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=4.25, hub_length=1.50, weight_approx=17.0
    ),
    ("4", 300): FlangeDimensions(
        nps="4", rating_class=300, od=10.00, thickness=1.25,
        raised_face_od=6.19, raised_face_height=0.06, bolt_circle=7.88,
        num_bolts=8, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=5.31, hub_length=1.62, weight_approx=26.0
    ),
    ("6", 300): FlangeDimensions(
        nps="6", rating_class=300, od=12.50, thickness=1.44,
        raised_face_od=8.50, raised_face_height=0.06, bolt_circle=10.62,
        num_bolts=12, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=7.56, hub_length=1.81, weight_approx=46.0
    ),
    ("8", 300): FlangeDimensions(
        nps="8", rating_class=300, od=15.00, thickness=1.62,
        raised_face_od=10.62, raised_face_height=0.06, bolt_circle=13.00,
        num_bolts=12, bolt_diameter="7/8", bolt_hole_diameter=1.00,
        hub_diameter=9.69, hub_length=2.00, weight_approx=73.0
    ),
    ("10", 300): FlangeDimensions(
        nps="10", rating_class=300, od=17.50, thickness=1.88,
        raised_face_od=12.75, raised_face_height=0.06, bolt_circle=15.25,
        num_bolts=16, bolt_diameter="1", bolt_hole_diameter=1.12,
        hub_diameter=12.00, hub_length=2.25, weight_approx=105.0
    ),
    ("12", 300): FlangeDimensions(
        nps="12", rating_class=300, od=20.50, thickness=2.00,
        raised_face_od=15.00, raised_face_height=0.06, bolt_circle=17.75,
        num_bolts=16, bolt_diameter="1-1/8", bolt_hole_diameter=1.25,
        hub_diameter=14.38, hub_length=2.38, weight_approx=150.0
    ),
    ("14", 300): FlangeDimensions(
        nps="14", rating_class=300, od=23.00, thickness=2.12,
        raised_face_od=16.25, raised_face_height=0.06, bolt_circle=20.25,
        num_bolts=20, bolt_diameter="1-1/8", bolt_hole_diameter=1.25,
        hub_diameter=15.75, hub_length=2.50, weight_approx=195.0
    ),
    ("16", 300): FlangeDimensions(
        nps="16", rating_class=300, od=25.50, thickness=2.25,
        raised_face_od=18.50, raised_face_height=0.06, bolt_circle=22.50,
        num_bolts=20, bolt_diameter="1-1/4", bolt_hole_diameter=1.38,
        hub_diameter=18.00, hub_length=2.62, weight_approx=255.0
    ),
    ("18", 300): FlangeDimensions(
        nps="18", rating_class=300, od=28.00, thickness=2.38,
        raised_face_od=21.00, raised_face_height=0.06, bolt_circle=24.75,
        num_bolts=24, bolt_diameter="1-1/4", bolt_hole_diameter=1.38,
        hub_diameter=19.88, hub_length=2.75, weight_approx=320.0
    ),
    ("20", 300): FlangeDimensions(
        nps="20", rating_class=300, od=30.50, thickness=2.50,
        raised_face_od=23.00, raised_face_height=0.06, bolt_circle=27.00,
        num_bolts=24, bolt_diameter="1-1/4", bolt_hole_diameter=1.38,
        hub_diameter=22.00, hub_length=2.88, weight_approx=400.0
    ),
    ("24", 300): FlangeDimensions(
        nps="24", rating_class=300, od=36.00, thickness=2.75,
        raised_face_od=27.25, raised_face_height=0.06, bolt_circle=32.00,
        num_bolts=24, bolt_diameter="1-1/2", bolt_hole_diameter=1.62,
        hub_diameter=26.12, hub_length=3.12, weight_approx=575.0
    ),

    # =========================================================================
    # CLASS 600 FLANGES (Common in high-pressure ACHE)
    # =========================================================================
    ("1", 600): FlangeDimensions(
        nps="1", rating_class=600, od=4.88, thickness=0.81,
        raised_face_od=2.00, raised_face_height=0.25, bolt_circle=3.50,
        num_bolts=4, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=1.94, hub_length=1.12, weight_approx=5.0
    ),
    ("2", 600): FlangeDimensions(
        nps="2", rating_class=600, od=6.50, thickness=1.00,
        raised_face_od=3.62, raised_face_height=0.25, bolt_circle=5.00,
        num_bolts=8, bolt_diameter="5/8", bolt_hole_diameter=0.75,
        hub_diameter=3.06, hub_length=1.38, weight_approx=11.0
    ),
    ("3", 600): FlangeDimensions(
        nps="3", rating_class=600, od=8.25, thickness=1.25,
        raised_face_od=5.00, raised_face_height=0.25, bolt_circle=6.62,
        num_bolts=8, bolt_diameter="3/4", bolt_hole_diameter=0.88,
        hub_diameter=4.25, hub_length=1.62, weight_approx=21.0
    ),
    ("4", 600): FlangeDimensions(
        nps="4", rating_class=600, od=10.75, thickness=1.50,
        raised_face_od=6.19, raised_face_height=0.25, bolt_circle=8.50,
        num_bolts=8, bolt_diameter="7/8", bolt_hole_diameter=1.00,
        hub_diameter=5.31, hub_length=1.88, weight_approx=36.0
    ),
    ("6", 600): FlangeDimensions(
        nps="6", rating_class=600, od=14.00, thickness=1.88,
        raised_face_od=8.50, raised_face_height=0.25, bolt_circle=11.50,
        num_bolts=12, bolt_diameter="1", bolt_hole_diameter=1.12,
        hub_diameter=7.56, hub_length=2.25, weight_approx=72.0
    ),
    ("8", 600): FlangeDimensions(
        nps="8", rating_class=600, od=16.50, thickness=2.19,
        raised_face_od=10.62, raised_face_height=0.25, bolt_circle=13.75,
        num_bolts=12, bolt_diameter="1-1/8", bolt_hole_diameter=1.25,
        hub_diameter=9.69, hub_length=2.56, weight_approx=115.0
    ),
    ("10", 600): FlangeDimensions(
        nps="10", rating_class=600, od=20.00, thickness=2.50,
        raised_face_od=12.75, raised_face_height=0.25, bolt_circle=17.00,
        num_bolts=16, bolt_diameter="1-1/4", bolt_hole_diameter=1.38,
        hub_diameter=12.00, hub_length=2.88, weight_approx=180.0
    ),
    ("12", 600): FlangeDimensions(
        nps="12", rating_class=600, od=22.00, thickness=2.62,
        raised_face_od=15.00, raised_face_height=0.25, bolt_circle=19.25,
        num_bolts=20, bolt_diameter="1-1/4", bolt_hole_diameter=1.38,
        hub_diameter=14.38, hub_length=3.00, weight_approx=240.0
    ),
    ("16", 600): FlangeDimensions(
        nps="16", rating_class=600, od=27.75, thickness=3.00,
        raised_face_od=18.50, raised_face_height=0.25, bolt_circle=24.25,
        num_bolts=20, bolt_diameter="1-1/2", bolt_hole_diameter=1.62,
        hub_diameter=18.00, hub_length=3.38, weight_approx=420.0
    ),

    # =========================================================================
    # CLASS 900 FLANGES (High pressure)
    # =========================================================================
    ("2", 900): FlangeDimensions(
        nps="2", rating_class=900, od=8.50, thickness=1.50,
        raised_face_od=3.62, raised_face_height=0.25, bolt_circle=6.50,
        num_bolts=8, bolt_diameter="1", bolt_hole_diameter=1.12,
        hub_diameter=3.06, hub_length=1.88, weight_approx=24.0
    ),
    ("3", 900): FlangeDimensions(
        nps="3", rating_class=900, od=9.50, thickness=1.50,
        raised_face_od=5.00, raised_face_height=0.25, bolt_circle=7.50,
        num_bolts=8, bolt_diameter="7/8", bolt_hole_diameter=1.00,
        hub_diameter=4.25, hub_length=1.88, weight_approx=32.0
    ),
    ("4", 900): FlangeDimensions(
        nps="4", rating_class=900, od=11.50, thickness=1.75,
        raised_face_od=6.19, raised_face_height=0.25, bolt_circle=9.25,
        num_bolts=8, bolt_diameter="1-1/8", bolt_hole_diameter=1.25,
        hub_diameter=5.31, hub_length=2.12, weight_approx=52.0
    ),
    ("6", 900): FlangeDimensions(
        nps="6", rating_class=900, od=15.00, thickness=2.19,
        raised_face_od=8.50, raised_face_height=0.25, bolt_circle=12.50,
        num_bolts=12, bolt_diameter="1-1/8", bolt_hole_diameter=1.25,
        hub_diameter=7.56, hub_length=2.56, weight_approx=100.0
    ),
    ("8", 900): FlangeDimensions(
        nps="8", rating_class=900, od=18.50, thickness=2.50,
        raised_face_od=10.62, raised_face_height=0.25, bolt_circle=15.50,
        num_bolts=12, bolt_diameter="1-3/8", bolt_hole_diameter=1.50,
        hub_diameter=9.69, hub_length=2.88, weight_approx=165.0
    ),
}


# =============================================================================
# PRESSURE-TEMPERATURE RATINGS (ASME B16.5 Table 2)
# =============================================================================
# Material Group 1.1 = Carbon Steel (A105, A350 LF2, A516 Gr.70)

PRESSURE_RATINGS: dict[tuple[int, float], float] = {
    # (Class, Temp °F) -> Max Working Pressure (psig)
    # Class 150
    (150, -20): 285, (150, 100): 285, (150, 200): 260, (150, 300): 230,
    (150, 400): 200, (150, 500): 170, (150, 600): 140, (150, 650): 125,
    (150, 700): 110, (150, 750): 95, (150, 800): 80, (150, 850): 65,
    (150, 900): 50, (150, 950): 35, (150, 1000): 20,

    # Class 300
    (300, -20): 740, (300, 100): 740, (300, 200): 675, (300, 300): 655,
    (300, 400): 635, (300, 500): 600, (300, 600): 550, (300, 650): 535,
    (300, 700): 535, (300, 750): 505, (300, 800): 410, (300, 850): 270,
    (300, 900): 170, (300, 950): 105, (300, 1000): 50,

    # Class 600
    (600, -20): 1480, (600, 100): 1480, (600, 200): 1350, (600, 300): 1310,
    (600, 400): 1270, (600, 500): 1200, (600, 600): 1095, (600, 650): 1075,
    (600, 700): 1065, (600, 750): 1010, (600, 800): 825, (600, 850): 535,
    (600, 900): 345, (600, 950): 205, (600, 1000): 105,

    # Class 900
    (900, -20): 2220, (900, 100): 2220, (900, 200): 2025, (900, 300): 1970,
    (900, 400): 1900, (900, 500): 1795, (900, 600): 1640, (900, 650): 1610,
    (900, 700): 1600, (900, 750): 1510, (900, 800): 1235, (900, 850): 805,
    (900, 900): 515, (900, 950): 310, (900, 1000): 155,

    # Class 1500
    (1500, -20): 3705, (1500, 100): 3705, (1500, 200): 3375, (1500, 300): 3280,
    (1500, 400): 3170, (1500, 500): 2995, (1500, 600): 2735, (1500, 650): 2685,
    (1500, 700): 2665, (1500, 750): 2520, (1500, 800): 2060, (1500, 850): 1340,
    (1500, 900): 860, (1500, 950): 515, (1500, 1000): 260,

    # Class 2500
    (2500, -20): 6170, (2500, 100): 6170, (2500, 200): 5625, (2500, 300): 5465,
    (2500, 400): 5280, (2500, 500): 4990, (2500, 600): 4560, (2500, 650): 4475,
    (2500, 700): 4440, (2500, 750): 4195, (2500, 800): 3430, (2500, 850): 2235,
    (2500, 900): 1430, (2500, 950): 860, (2500, 1000): 430,
}


# =============================================================================
# BOLT TORQUE VALUES (ft-lbs, lubricated)
# =============================================================================
# For reference - actual torque depends on gasket, stud material, etc.

BOLT_TORQUE_REFERENCE: dict[str, dict[str, float]] = {
    # Bolt size: {grade: torque ft-lbs}
    "1/2": {"B7": 30, "B8": 25},
    "5/8": {"B7": 60, "B8": 50},
    "3/4": {"B7": 100, "B8": 85},
    "7/8": {"B7": 160, "B8": 135},
    "1": {"B7": 240, "B8": 200},
    "1-1/8": {"B7": 350, "B8": 290},
    "1-1/4": {"B7": 480, "B8": 400},
    "1-3/8": {"B7": 650, "B8": 540},
    "1-1/2": {"B7": 850, "B8": 710},
}


# =============================================================================
# GASKET DIMENSIONS (for RF flanges)
# =============================================================================

GASKET_ID_OD: dict[str, tuple[float, float]] = {
    # NPS: (ID, OD) for spiral wound gaskets
    "1/2": (0.84, 1.38),
    "3/4": (1.05, 1.69),
    "1": (1.32, 2.00),
    "1-1/4": (1.66, 2.50),
    "1-1/2": (1.90, 2.88),
    "2": (2.38, 3.62),
    "2-1/2": (2.88, 4.12),
    "3": (3.50, 5.00),
    "4": (4.50, 6.19),
    "5": (5.56, 7.31),
    "6": (6.62, 8.50),
    "8": (8.62, 10.62),
    "10": (10.75, 12.75),
    "12": (12.75, 15.00),
    "14": (14.00, 16.25),
    "16": (16.00, 18.50),
    "18": (18.00, 21.00),
    "20": (20.00, 23.00),
    "24": (24.00, 27.25),
}


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================

def get_flange_dimensions(nps: str, rating_class: int) -> Optional[FlangeDimensions]:
    """
    Get ASME B16.5 flange dimensions.

    Args:
        nps: Nominal pipe size (e.g., "4", "6", "2-1/2")
        rating_class: 150, 300, 600, 900, 1500, or 2500

    Returns:
        FlangeDimensions or None if not found
    """
    return FLANGE_DIMENSIONS.get((nps, rating_class))


def get_pressure_rating(rating_class: int, temp_f: float) -> Optional[float]:
    """
    Get maximum working pressure for a flange class at temperature.

    Args:
        rating_class: 150, 300, 600, etc.
        temp_f: Temperature in Fahrenheit

    Returns:
        Maximum pressure in psig, or None if not found
    """
    # Find the nearest temperature in the table
    temps = sorted(set(t for (c, t) in PRESSURE_RATINGS.keys() if c == rating_class))

    if not temps:
        return None

    # Use the next higher temperature for conservatism
    for t in temps:
        if t >= temp_f:
            return PRESSURE_RATINGS.get((rating_class, t))

    # If temp exceeds all table values, return the highest temp rating
    return PRESSURE_RATINGS.get((rating_class, temps[-1]))


def get_all_classes() -> list[int]:
    """Get all available pressure classes."""
    return [150, 300, 400, 600, 900, 1500, 2500]


def get_all_sizes(rating_class: int) -> list[str]:
    """Get all available sizes for a pressure class."""
    sizes = []
    for (nps, cls) in FLANGE_DIMENSIONS.keys():
        if cls == rating_class and nps not in sizes:
            sizes.append(nps)
    return sizes


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_flange(
    nps: str,
    rating_class: int,
    od: Optional[float] = None,
    bolt_circle: Optional[float] = None,
    num_bolts: Optional[int] = None,
    bolt_diameter: Optional[str] = None,
    thickness: Optional[float] = None,
    tolerance: float = 0.03
) -> FlangeValidationResult:
    """
    Validate flange dimensions against ASME B16.5.

    Args:
        nps: Nominal pipe size
        rating_class: Pressure class
        od: Measured OD (optional)
        bolt_circle: Measured bolt circle (optional)
        num_bolts: Number of bolts (optional)
        bolt_diameter: Bolt size (optional)
        thickness: Measured thickness (optional)
        tolerance: Acceptable tolerance (default 3%)

    Returns:
        FlangeValidationResult with errors and warnings
    """
    errors = []
    warnings = []
    details = {}

    # Get standard dimensions
    std = get_flange_dimensions(nps, rating_class)
    if std is None:
        return FlangeValidationResult(
            is_valid=False,
            errors=[f"No ASME B16.5 data for {nps}\" Class {rating_class}"],
            warnings=[],
            details={}
        )

    details["standard"] = {
        "nps": std.nps,
        "class": std.rating_class,
        "od": std.od,
        "bolt_circle": std.bolt_circle,
        "num_bolts": std.num_bolts,
        "bolt_diameter": std.bolt_diameter,
        "thickness": std.thickness,
    }

    # Validate OD
    if od is not None:
        diff = abs(od - std.od)
        diff_pct = diff / std.od
        details["od_check"] = {"measured": od, "standard": std.od, "diff": diff}
        if diff_pct > tolerance:
            errors.append(f"OD {od}\" differs from std {std.od}\" by {diff_pct*100:.1f}%")
        elif diff_pct > tolerance / 2:
            warnings.append(f"OD {od}\" is close to tolerance (std {std.od}\")")

    # Validate bolt circle
    if bolt_circle is not None:
        diff = abs(bolt_circle - std.bolt_circle)
        diff_pct = diff / std.bolt_circle
        details["bc_check"] = {"measured": bolt_circle, "standard": std.bolt_circle, "diff": diff}
        if diff_pct > tolerance:
            errors.append(f"Bolt circle {bolt_circle}\" differs from std {std.bolt_circle}\"")

    # Validate number of bolts
    if num_bolts is not None:
        details["bolt_count"] = {"measured": num_bolts, "standard": std.num_bolts}
        if num_bolts != std.num_bolts:
            errors.append(f"Bolt count {num_bolts} differs from std {std.num_bolts}")

    # Validate bolt diameter
    if bolt_diameter is not None:
        details["bolt_size"] = {"measured": bolt_diameter, "standard": std.bolt_diameter}
        if bolt_diameter != std.bolt_diameter:
            errors.append(f"Bolt size {bolt_diameter}\" differs from std {std.bolt_diameter}\"")

    # Validate thickness (min check)
    if thickness is not None:
        details["thickness_check"] = {"measured": thickness, "standard": std.thickness}
        if thickness < std.thickness * 0.95:  # Allow 5% under for machining
            errors.append(f"Thickness {thickness}\" below min {std.thickness}\"")

    return FlangeValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details
    )


def validate_flange_pair(
    flange_a: FlangeDimensions,
    flange_b: FlangeDimensions,
    tolerance: float = 0.03
) -> FlangeValidationResult:
    """
    Validate that two flanges can mate properly.

    Args:
        flange_a: First flange dimensions
        flange_b: Second flange dimensions
        tolerance: Acceptable difference

    Returns:
        FlangeValidationResult
    """
    errors = []
    warnings = []
    details = {"flange_a": flange_a.nps, "flange_b": flange_b.nps}

    # Must be same size
    if flange_a.nps != flange_b.nps:
        errors.append(f"Size mismatch: {flange_a.nps}\" vs {flange_b.nps}\"")

    # Bolt patterns must match
    if flange_a.bolt_circle != flange_b.bolt_circle:
        diff = abs(flange_a.bolt_circle - flange_b.bolt_circle)
        if diff > tolerance:
            errors.append(f"Bolt circle mismatch: {flange_a.bolt_circle}\" vs {flange_b.bolt_circle}\"")
        else:
            warnings.append(f"Bolt circles slightly different but within tolerance")

    if flange_a.num_bolts != flange_b.num_bolts:
        errors.append(f"Bolt count mismatch: {flange_a.num_bolts} vs {flange_b.num_bolts}")

    if flange_a.bolt_diameter != flange_b.bolt_diameter:
        # Check if bolt holes are compatible (larger holes can accept smaller bolts)
        errors.append(f"Bolt size mismatch: {flange_a.bolt_diameter}\" vs {flange_b.bolt_diameter}\"")

    # Raised face OD should match for gasket
    if flange_a.raised_face_od != flange_b.raised_face_od:
        diff = abs(flange_a.raised_face_od - flange_b.raised_face_od)
        if diff > 0.06:  # 1/16" tolerance
            warnings.append(f"RF OD differs: {flange_a.raised_face_od}\" vs {flange_b.raised_face_od}\"")

    details["compatible"] = len(errors) == 0

    return FlangeValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details
    )


def check_class_for_conditions(
    design_pressure_psi: float,
    design_temp_f: float,
    min_class: int = 150
) -> tuple[int, str]:
    """
    Determine minimum flange class for given conditions.

    Args:
        design_pressure_psi: Design pressure
        design_temp_f: Design temperature
        min_class: Minimum acceptable class

    Returns:
        Tuple of (recommended_class, message)
    """
    for cls in [150, 300, 600, 900, 1500, 2500]:
        if cls < min_class:
            continue

        rating = get_pressure_rating(cls, design_temp_f)
        if rating and rating >= design_pressure_psi:
            margin = (rating - design_pressure_psi) / rating * 100
            return cls, f"Class {cls} rated {rating} psig at {design_temp_f}°F (margin: {margin:.1f}%)"

    return 2500, f"Class 2500 required or conditions exceed ASME B16.5 limits"


def validate_nozzle_projection(
    flange_dims: FlangeDimensions,
    projection: float,
    min_projection: float = 1.0
) -> tuple[bool, str]:
    """
    Validate nozzle projection per API 661 recommendations.

    Args:
        flange_dims: Flange dimensions
        projection: Distance from vessel to flange face (inches)
        min_projection: Minimum required projection

    Returns:
        Tuple of (is_valid, message)
    """
    # Minimum projection should allow for gasket installation
    min_req = max(min_projection, flange_dims.hub_length * 0.5)

    if projection < min_req:
        return False, f"Projection {projection}\" below min {min_req}\" for assembly access"

    return True, f"Projection {projection}\" OK (min {min_req}\")"


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_flange_report(
    nps: str,
    rating_class: int,
    design_pressure: float,
    design_temp: float
) -> dict:
    """
    Generate a comprehensive flange specification report.

    Returns:
        Dictionary with all relevant specifications
    """
    dims = get_flange_dimensions(nps, rating_class)
    rating = get_pressure_rating(rating_class, design_temp)
    gasket = GASKET_ID_OD.get(nps)

    report = {
        "specification": f"{nps}\" Class {rating_class} ASME B16.5",
        "design_conditions": {
            "pressure_psi": design_pressure,
            "temperature_f": design_temp,
        },
        "dimensions": None,
        "pressure_rating": None,
        "gasket": None,
        "bolt_info": None,
        "is_adequate": False,
    }

    if dims:
        report["dimensions"] = {
            "od_in": dims.od,
            "thickness_in": dims.thickness,
            "bolt_circle_in": dims.bolt_circle,
            "num_bolts": dims.num_bolts,
            "bolt_size": dims.bolt_diameter,
            "bolt_hole_dia_in": dims.bolt_hole_diameter,
            "raised_face_od_in": dims.raised_face_od,
            "hub_diameter_in": dims.hub_diameter,
            "hub_length_in": dims.hub_length,
            "weight_lbs": dims.weight_approx,
        }

        if dims.bolt_diameter in BOLT_TORQUE_REFERENCE:
            report["bolt_info"] = {
                "size": dims.bolt_diameter,
                "quantity": dims.num_bolts,
                "material": "ASTM A193 B7",
                "nut_material": "ASTM A194 2H",
                "torque_ft_lbs": BOLT_TORQUE_REFERENCE[dims.bolt_diameter]["B7"],
            }

    if rating:
        report["pressure_rating"] = {
            "max_working_pressure_psi": rating,
            "at_temperature_f": design_temp,
            "margin_pct": (rating - design_pressure) / rating * 100 if rating > 0 else 0,
        }
        report["is_adequate"] = rating >= design_pressure

    if gasket:
        report["gasket"] = {
            "type": "Spiral Wound (316L/Graphite)",
            "id_in": gasket[0],
            "od_in": gasket[1],
            "thickness_in": 0.175,
        }

    return report


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "FlangeClass",
    "FacingType",
    # Data classes
    "FlangeDimensions",
    "PressureRating",
    "FlangeValidationResult",
    # Data tables
    "FLANGE_DIMENSIONS",
    "PRESSURE_RATINGS",
    "BOLT_TORQUE_REFERENCE",
    "GASKET_ID_OD",
    # Lookup functions
    "get_flange_dimensions",
    "get_pressure_rating",
    "get_all_classes",
    "get_all_sizes",
    # Validation functions
    "validate_flange",
    "validate_flange_pair",
    "check_class_for_conditions",
    "validate_nozzle_projection",
    # Report generation
    "generate_flange_report",
]
