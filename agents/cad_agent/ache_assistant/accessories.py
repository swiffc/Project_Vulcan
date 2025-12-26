"""
ACHE Accessory Designer Module
Phase 24.6 - Walkways, Handrails, and Ladders for Air Cooled Heat Exchangers

Implements accessory design per:
- OSHA 1910 Subpart D (Walking-Working Surfaces)
- API 661 / ISO 13706 access requirements
- ANSI A1264.1 (Safety Requirements for Workplace Walking/Working Surfaces)
"""

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger("vulcan.ache.accessories")


class PlatformType(Enum):
    """Platform types for ACHE access."""
    FAN_DECK = "fan_deck"
    HEADER_ACCESS = "header_access"
    VALVE_ACCESS = "valve_access"
    MAINTENANCE = "maintenance"
    INTERMEDIATE = "intermediate"


class GratingType(Enum):
    """Grating specifications."""
    BAR_19_4 = "19-4"  # 19mm bearing bar, 4mm cross bar
    BAR_25_5 = "25-5"
    BAR_32_5 = "32-5"
    BAR_40_5 = "40-5"
    EXPANDED = "expanded"
    PLANK = "plank"


class LadderType(Enum):
    """Ladder types."""
    VERTICAL_FIXED = "vertical_fixed"
    INCLINED = "inclined"
    SHIP_STAIR = "ship_stair"
    STAIR = "stair"


class HandrailType(Enum):
    """Handrail types."""
    PIPE = "pipe"
    TUBE = "tube"
    CHANNEL = "channel"


@dataclass
class GratingSpec:
    """Grating specification and load capacity."""
    type: GratingType
    bearing_bar_mm: float
    bearing_bar_spacing_mm: float
    cross_bar_spacing_mm: float
    load_capacity_kpa: float
    weight_kg_m2: float
    deflection_limit: str = "L/200"


@dataclass
class PlatformDesign:
    """Platform/walkway design results."""
    platform_type: PlatformType
    length_m: float
    width_m: float
    elevation_m: float

    # Grating
    grating: GratingSpec
    grating_area_m2: float = 0.0

    # Structure
    support_beam_profile: str = ""
    support_beam_spacing_m: float = 0.0
    num_support_beams: int = 0

    # Loads
    live_load_kpa: float = 4.8  # 100 psf default
    dead_load_kpa: float = 0.5
    total_load_kpa: float = 5.3

    # Toe plate
    toe_plate_height_mm: float = 100
    has_toe_plate: bool = True

    # Results
    total_weight_kg: float = 0.0
    is_adequate: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class LadderDesign:
    """Ladder design results."""
    ladder_type: LadderType
    height_m: float
    width_mm: float = 450  # Min 16" per OSHA

    # Rungs
    rung_spacing_mm: float = 300  # 12" nominal
    rung_diameter_mm: float = 25
    num_rungs: int = 0

    # Side rails
    side_rail_profile: str = ""
    side_rail_size_mm: Tuple[float, float] = (75, 10)  # Typical channel

    # Safety
    has_cage: bool = False
    cage_start_height_m: float = 2.1  # 7 ft
    has_safety_climb: bool = False
    has_rest_platforms: bool = False
    rest_platform_interval_m: float = 9.0  # 30 ft max climb

    # Landing
    landing_length_mm: float = 600
    landing_width_mm: float = 600

    # Results
    total_weight_kg: float = 0.0
    is_osha_compliant: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class HandrailDesign:
    """Handrail design results."""
    handrail_type: HandrailType
    total_length_m: float

    # Dimensions
    top_rail_height_mm: float = 1070  # 42" per OSHA
    mid_rail_height_mm: float = 535  # 21"
    post_spacing_m: float = 2.4  # 8 ft max

    # Members
    top_rail_profile: str = ""
    top_rail_od_mm: float = 42  # 1.5" pipe typical
    mid_rail_profile: str = ""
    mid_rail_od_mm: float = 42
    post_profile: str = ""
    post_od_mm: float = 48  # 1.5" pipe typical

    # Load capacity
    top_rail_load_kn_m: float = 0.89  # 200 lbf/ft
    concentrated_load_kn: float = 0.89  # 200 lbf

    # Gates
    has_gates: bool = False
    num_gates: int = 0
    gate_width_mm: float = 600

    # Results
    num_posts: int = 0
    total_weight_kg: float = 0.0
    is_osha_compliant: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class AccessoryBOM:
    """Bill of materials for accessories."""
    platforms: List[Dict[str, Any]] = field(default_factory=list)
    ladders: List[Dict[str, Any]] = field(default_factory=list)
    handrails: List[Dict[str, Any]] = field(default_factory=list)
    total_grating_m2: float = 0.0
    total_steel_kg: float = 0.0
    items: List[Dict[str, Any]] = field(default_factory=list)


class AccessoryDesigner:
    """
    Designer for ACHE access platforms, ladders, and handrails.

    Implements Phase 24.6: Walkways/Handrails/Ladders

    Standards:
    - OSHA 1910.23 (Ladders)
    - OSHA 1910.25-29 (Walking-Working Surfaces)
    - API 661 Section 7 (Access provisions)
    - ANSI A1264.1
    """

    # Standard grating specifications
    GRATING_SPECS = {
        GratingType.BAR_19_4: GratingSpec(
            type=GratingType.BAR_19_4,
            bearing_bar_mm=19,
            bearing_bar_spacing_mm=30,
            cross_bar_spacing_mm=100,
            load_capacity_kpa=7.2,  # ~150 psf
            weight_kg_m2=22,
        ),
        GratingType.BAR_25_5: GratingSpec(
            type=GratingType.BAR_25_5,
            bearing_bar_mm=25,
            bearing_bar_spacing_mm=30,
            cross_bar_spacing_mm=100,
            load_capacity_kpa=9.6,  # ~200 psf
            weight_kg_m2=30,
        ),
        GratingType.BAR_32_5: GratingSpec(
            type=GratingType.BAR_32_5,
            bearing_bar_mm=32,
            bearing_bar_spacing_mm=30,
            cross_bar_spacing_mm=100,
            load_capacity_kpa=14.4,  # ~300 psf
            weight_kg_m2=40,
        ),
    }

    # OSHA requirements
    MIN_WALKWAY_WIDTH_MM = 450  # 18"
    MIN_PLATFORM_WIDTH_MM = 508  # 20" for workstations
    MAX_RUNG_SPACING_MM = 305  # 12"
    HANDRAIL_HEIGHT_MM = 1070  # 42"
    TOE_PLATE_HEIGHT_MM = 89  # 3.5"

    def __init__(self):
        """Initialize accessory designer."""
        self._steel_density = 7850  # kg/m3

    def design_platform(
        self,
        length_m: float,
        width_m: float,
        elevation_m: float,
        platform_type: PlatformType = PlatformType.MAINTENANCE,
        live_load_kpa: float = 4.8,
        grating_type: GratingType = GratingType.BAR_25_5,
    ) -> PlatformDesign:
        """
        Design access platform/walkway.

        Args:
            length_m: Platform length
            width_m: Platform width
            elevation_m: Platform elevation above grade
            platform_type: Type of platform
            live_load_kpa: Design live load (default 100 psf)
            grating_type: Grating specification

        Returns:
            PlatformDesign
        """
        design = PlatformDesign(
            platform_type=platform_type,
            length_m=length_m,
            width_m=width_m,
            elevation_m=elevation_m,
            grating=self.GRATING_SPECS.get(grating_type, self.GRATING_SPECS[GratingType.BAR_25_5]),
            live_load_kpa=live_load_kpa,
        )

        try:
            # Check minimum width
            if width_m * 1000 < self.MIN_WALKWAY_WIDTH_MM:
                design.warnings.append(
                    f"Width {width_m*1000:.0f}mm below OSHA minimum {self.MIN_WALKWAY_WIDTH_MM}mm"
                )
                design.is_adequate = False

            # Grating area
            design.grating_area_m2 = length_m * width_m

            # Total load
            design.dead_load_kpa = design.grating.weight_kg_m2 * 9.81 / 1000
            design.total_load_kpa = design.live_load_kpa + design.dead_load_kpa

            # Check grating capacity
            if design.total_load_kpa > design.grating.load_capacity_kpa:
                design.warnings.append(
                    f"Load {design.total_load_kpa:.1f} kPa exceeds grating capacity "
                    f"{design.grating.load_capacity_kpa:.1f} kPa"
                )
                design.is_adequate = False

            # Support beam design
            # Typical span for grating: 1.2-1.5m depending on load
            max_span = self._get_grating_span(design.grating, design.total_load_kpa)
            design.support_beam_spacing_m = min(max_span, length_m)
            design.num_support_beams = max(2, int(length_m / design.support_beam_spacing_m) + 1)

            # Select support beam (C-channel typical)
            beam_load = design.total_load_kpa * width_m * design.support_beam_spacing_m
            design.support_beam_profile = self._select_channel(beam_load, width_m)

            # Toe plate
            if platform_type in [PlatformType.FAN_DECK, PlatformType.HEADER_ACCESS]:
                design.has_toe_plate = True
                design.toe_plate_height_mm = max(100, self.TOE_PLATE_HEIGHT_MM)

            # Calculate weight
            grating_weight = design.grating_area_m2 * design.grating.weight_kg_m2

            # Support beam weight (estimate)
            beam_weight_per_m = 10  # kg/m typical for C6x8.2
            beam_weight = design.num_support_beams * width_m * beam_weight_per_m

            # Toe plate weight
            toe_plate_weight = 0
            if design.has_toe_plate:
                toe_plate_perimeter = 2 * (length_m + width_m)
                toe_plate_weight = toe_plate_perimeter * (design.toe_plate_height_mm / 1000) * 0.005 * self._steel_density

            design.total_weight_kg = grating_weight + beam_weight + toe_plate_weight

            logger.info(
                f"Platform design: {length_m:.1f}x{width_m:.1f}m, "
                f"{design.grating.type.value}, {design.total_weight_kg:.0f} kg"
            )

        except Exception as e:
            logger.error(f"Platform design error: {e}")
            design.warnings.append(f"Design error: {e}")
            design.is_adequate = False

        return design

    def _get_grating_span(self, grating: GratingSpec, load_kpa: float) -> float:
        """Get maximum grating span for given load."""
        # Simplified span table based on bearing bar size
        base_span = {
            GratingType.BAR_19_4: 0.9,
            GratingType.BAR_25_5: 1.2,
            GratingType.BAR_32_5: 1.5,
        }
        span = base_span.get(grating.type, 1.0)

        # Adjust for load (reduce for higher loads)
        if load_kpa > 7.2:
            span *= 0.8
        elif load_kpa < 3.0:
            span *= 1.2

        return span

    def _select_channel(self, load_kn: float, span_m: float) -> str:
        """Select channel size for support beam."""
        # Required section modulus (simplified)
        M = load_kn * span_m / 8  # Simple beam moment
        fy = 250  # A36 yield
        S_req = M * 1e6 / (0.66 * fy)  # mm3

        # Channel selection
        channels = {
            "C4x5.4": 22.8e3,
            "C5x6.7": 34.4e3,
            "C6x8.2": 50.1e3,
            "C8x11.5": 88.5e3,
            "C10x15.3": 143e3,
        }

        for name, Sx in channels.items():
            if Sx >= S_req:
                return name

        return "C10x15.3"  # Default to largest

    def design_ladder(
        self,
        height_m: float,
        ladder_type: LadderType = LadderType.VERTICAL_FIXED,
        width_mm: float = 450,
        include_cage: bool = True,
        include_safety_climb: bool = False,
    ) -> LadderDesign:
        """
        Design fixed ladder per OSHA 1910.23.

        Args:
            height_m: Total climb height
            ladder_type: Type of ladder
            width_mm: Clear width between side rails
            include_cage: Include safety cage (required > 20ft)
            include_safety_climb: Include fall arrest system

        Returns:
            LadderDesign
        """
        design = LadderDesign(
            ladder_type=ladder_type,
            height_m=height_m,
            width_mm=width_mm,
        )

        try:
            # OSHA compliance checks
            if width_mm < 400:  # 16" minimum
                design.warnings.append(f"Width {width_mm}mm below OSHA minimum 400mm")
                design.is_osha_compliant = False

            # Rung spacing
            design.rung_spacing_mm = 300  # 12" nominal (OSHA: max 12")
            design.num_rungs = int(height_m * 1000 / design.rung_spacing_mm) + 1

            # Side rail sizing
            if ladder_type == LadderType.VERTICAL_FIXED:
                design.side_rail_profile = "C3x4.1"
                design.side_rail_size_mm = (76, 35)  # Approximate dimensions
            else:
                design.side_rail_profile = "C4x5.4"
                design.side_rail_size_mm = (102, 41)

            # Rung sizing - must support 250 lbf concentrated load
            design.rung_diameter_mm = 25  # 1" min, round or square acceptable

            # Safety cage requirements (OSHA 1910.28)
            if height_m > 6.1:  # 20 ft
                if include_cage or not include_safety_climb:
                    design.has_cage = True
                    design.cage_start_height_m = 2.1  # Start at 7 ft

                if include_safety_climb:
                    design.has_safety_climb = True
                    design.has_cage = False  # Safety climb can replace cage

            # Rest platforms required every 150 ft (45.7m), recommended every 30 ft
            if height_m > 9.0:
                design.has_rest_platforms = True
                design.rest_platform_interval_m = 9.0

            # Landing at top
            design.landing_length_mm = max(600, width_mm)
            design.landing_width_mm = max(600, width_mm)

            # Calculate weight
            # Side rails
            rail_weight_per_m = 6  # kg/m typical for C3
            rail_weight = 2 * height_m * rail_weight_per_m

            # Rungs (25mm round bar)
            rung_area = math.pi * (design.rung_diameter_mm / 2) ** 2 / 1e6  # m2
            rung_weight = design.num_rungs * (width_mm / 1000) * rung_area * self._steel_density

            # Cage weight (if applicable)
            cage_weight = 0
            if design.has_cage:
                cage_height = height_m - design.cage_start_height_m
                # Cage hoops every 600mm + vertical bars
                num_hoops = int(cage_height / 0.6) + 1
                hoop_length = math.pi * 0.75  # ~750mm diameter cage
                cage_weight = num_hoops * hoop_length * 2 + cage_height * 4 * 2  # Approximate

            design.total_weight_kg = rail_weight + rung_weight + cage_weight

            logger.info(
                f"Ladder design: {height_m:.1f}m, {design.num_rungs} rungs, "
                f"cage={design.has_cage}, {design.total_weight_kg:.0f} kg"
            )

        except Exception as e:
            logger.error(f"Ladder design error: {e}")
            design.warnings.append(f"Design error: {e}")
            design.is_osha_compliant = False

        return design

    def design_handrail(
        self,
        total_length_m: float,
        num_corners: int = 0,
        has_gates: bool = False,
        num_gates: int = 0,
        handrail_type: HandrailType = HandrailType.PIPE,
    ) -> HandrailDesign:
        """
        Design handrail system per OSHA 1910.29.

        Args:
            total_length_m: Total handrail length
            num_corners: Number of corners
            has_gates: Include self-closing gates
            num_gates: Number of gates
            handrail_type: Type of handrail construction

        Returns:
            HandrailDesign
        """
        design = HandrailDesign(
            handrail_type=handrail_type,
            total_length_m=total_length_m,
            has_gates=has_gates,
            num_gates=num_gates,
        )

        try:
            # Standard heights per OSHA
            design.top_rail_height_mm = self.HANDRAIL_HEIGHT_MM
            design.mid_rail_height_mm = self.HANDRAIL_HEIGHT_MM // 2

            # Post spacing (8 ft max typical)
            design.post_spacing_m = 2.4
            design.num_posts = max(2, int(total_length_m / design.post_spacing_m) + 1)
            design.num_posts += num_corners  # Extra posts at corners

            # Member sizing
            if handrail_type == HandrailType.PIPE:
                design.top_rail_profile = "1-1/2\" SCH 40 PIPE"
                design.top_rail_od_mm = 48.3
                design.mid_rail_profile = "1-1/4\" SCH 40 PIPE"
                design.mid_rail_od_mm = 42.2
                design.post_profile = "1-1/2\" SCH 40 PIPE"
                design.post_od_mm = 48.3
            elif handrail_type == HandrailType.TUBE:
                design.top_rail_profile = "1-1/2\" SQ TUBE"
                design.top_rail_od_mm = 38.1
                design.mid_rail_profile = "1-1/4\" SQ TUBE"
                design.mid_rail_od_mm = 31.75
                design.post_profile = "1-1/2\" SQ TUBE"
                design.post_od_mm = 38.1

            # Gate dimensions
            if has_gates:
                design.gate_width_mm = 600  # 24" typical

            # Load capacity check
            # Top rail must support 200 lbf/ft (2.92 kN/m) and 200 lbf concentrated
            design.top_rail_load_kn_m = 0.89  # 200 lbf/ft
            design.concentrated_load_kn = 0.89  # 200 lbf

            # Calculate weight
            # Top rail weight
            top_rail_area = math.pi * (design.top_rail_od_mm / 2) ** 2 / 1e6
            wall_thickness = 3.68  # mm for SCH 40
            top_rail_weight = total_length_m * top_rail_area * 0.2 * self._steel_density  # Hollow

            # Mid rail weight (similar)
            mid_rail_weight = top_rail_weight * 0.8  # Slightly lighter

            # Post weight
            post_height = design.top_rail_height_mm / 1000 + 0.1  # Include base
            post_area = math.pi * (design.post_od_mm / 2) ** 2 / 1e6
            post_weight = design.num_posts * post_height * post_area * 0.2 * self._steel_density

            # Gate weight
            gate_weight = 0
            if has_gates:
                gate_weight = num_gates * 15  # ~15 kg per gate typical

            design.total_weight_kg = top_rail_weight + mid_rail_weight + post_weight + gate_weight

            logger.info(
                f"Handrail design: {total_length_m:.1f}m, {design.num_posts} posts, "
                f"{num_gates} gates, {design.total_weight_kg:.0f} kg"
            )

        except Exception as e:
            logger.error(f"Handrail design error: {e}")
            design.warnings.append(f"Design error: {e}")
            design.is_osha_compliant = False

        return design

    def design_ache_access_system(
        self,
        bundle_length_m: float,
        bundle_width_m: float,
        elevation_m: float,
        num_bays: int = 1,
        fan_deck_required: bool = True,
        header_access_required: bool = True,
    ) -> AccessoryBOM:
        """
        Design complete access system for ACHE.

        Args:
            bundle_length_m: ACHE bundle length
            bundle_width_m: ACHE bundle width
            elevation_m: Elevation to fan deck
            num_bays: Number of bays
            fan_deck_required: Include fan deck walkway
            header_access_required: Include header access platforms

        Returns:
            AccessoryBOM with complete bill of materials
        """
        bom = AccessoryBOM()

        try:
            platforms = []
            ladders = []
            handrails = []

            # Fan deck walkway (along length of unit)
            if fan_deck_required:
                fan_deck = self.design_platform(
                    length_m=bundle_length_m,
                    width_m=0.9,  # 3 ft typical walkway
                    elevation_m=elevation_m,
                    platform_type=PlatformType.FAN_DECK,
                    live_load_kpa=4.8,
                )
                platforms.append({
                    "type": "Fan Deck Walkway",
                    "quantity": 2,  # Both sides
                    "design": fan_deck,
                    "length_m": fan_deck.length_m,
                    "width_m": fan_deck.width_m,
                })
                bom.total_grating_m2 += 2 * fan_deck.grating_area_m2
                bom.total_steel_kg += 2 * fan_deck.total_weight_kg

            # Header access platforms (at ends)
            if header_access_required:
                header_platform = self.design_platform(
                    length_m=bundle_width_m,
                    width_m=1.2,  # 4 ft for header access
                    elevation_m=elevation_m,
                    platform_type=PlatformType.HEADER_ACCESS,
                    live_load_kpa=4.8,
                )
                platforms.append({
                    "type": "Header Access Platform",
                    "quantity": 2,  # Both ends
                    "design": header_platform,
                    "length_m": header_platform.length_m,
                    "width_m": header_platform.width_m,
                })
                bom.total_grating_m2 += 2 * header_platform.grating_area_m2
                bom.total_steel_kg += 2 * header_platform.total_weight_kg

            # Access ladder
            ladder = self.design_ladder(
                height_m=elevation_m,
                ladder_type=LadderType.VERTICAL_FIXED,
                width_mm=450,
                include_cage=elevation_m > 6.1,
            )
            ladders.append({
                "type": "Access Ladder",
                "quantity": 1,
                "design": ladder,
                "height_m": ladder.height_m,
            })
            bom.total_steel_kg += ladder.total_weight_kg

            # Handrails for all platforms
            # Fan deck handrails (both sides of walkway)
            if fan_deck_required:
                handrail_length = bundle_length_m * 2  # Both walkways
                fan_handrail = self.design_handrail(
                    total_length_m=handrail_length,
                    num_corners=4,
                    has_gates=True,
                    num_gates=2,  # Gate at each end
                )
                handrails.append({
                    "type": "Fan Deck Handrail",
                    "quantity": 1,
                    "design": fan_handrail,
                    "length_m": fan_handrail.total_length_m,
                })
                bom.total_steel_kg += fan_handrail.total_weight_kg

            # Header platform handrails
            if header_access_required:
                header_handrail_length = (bundle_width_m + 1.2) * 2  # Perimeter
                header_handrail = self.design_handrail(
                    total_length_m=header_handrail_length,
                    num_corners=8,  # Two platforms
                )
                handrails.append({
                    "type": "Header Platform Handrail",
                    "quantity": 2,
                    "design": header_handrail,
                    "length_m": header_handrail.total_length_m,
                })
                bom.total_steel_kg += 2 * header_handrail.total_weight_kg

            bom.platforms = platforms
            bom.ladders = ladders
            bom.handrails = handrails

            # Generate BOM items
            bom.items = self._generate_bom_items(platforms, ladders, handrails)

            logger.info(
                f"ACHE access system: {len(platforms)} platforms, "
                f"{len(ladders)} ladders, {len(handrails)} handrail runs, "
                f"Total: {bom.total_steel_kg:.0f} kg"
            )

        except Exception as e:
            logger.error(f"Access system design error: {e}")

        return bom

    def _generate_bom_items(
        self,
        platforms: List[Dict],
        ladders: List[Dict],
        handrails: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Generate detailed BOM items from designs."""
        items = []

        # Grating items
        for p in platforms:
            design = p["design"]
            qty = p["quantity"]
            items.append({
                "item": f"Grating - {design.grating.type.value}",
                "description": f"{design.length_m:.1f}m x {design.width_m:.1f}m",
                "quantity": qty,
                "unit": "ea",
                "area_m2": design.grating_area_m2 * qty,
                "weight_kg": design.grating_area_m2 * design.grating.weight_kg_m2 * qty,
            })

            # Support beams
            items.append({
                "item": f"Channel {design.support_beam_profile}",
                "description": f"Platform support beam",
                "quantity": design.num_support_beams * qty,
                "unit": "ea",
                "length_m": design.width_m,
                "weight_kg": design.num_support_beams * design.width_m * 10 * qty,  # Estimate
            })

            # Toe plate
            if design.has_toe_plate:
                perimeter = 2 * (design.length_m + design.width_m)
                items.append({
                    "item": f"Toe Plate - {design.toe_plate_height_mm}mm",
                    "description": f"Platform toe plate",
                    "quantity": qty,
                    "unit": "ea",
                    "length_m": perimeter,
                })

        # Ladder items
        for l in ladders:
            design = l["design"]
            qty = l["quantity"]
            items.append({
                "item": f"Fixed Ladder - {design.side_rail_profile}",
                "description": f"{design.height_m:.1f}m height, {design.width_mm}mm width",
                "quantity": qty,
                "unit": "ea",
                "weight_kg": design.total_weight_kg * qty,
            })

            if design.has_cage:
                items.append({
                    "item": "Ladder Cage Assembly",
                    "description": f"Safety cage from {design.cage_start_height_m}m to top",
                    "quantity": qty,
                    "unit": "ea",
                })

        # Handrail items
        for h in handrails:
            design = h["design"]
            qty = h["quantity"]
            items.append({
                "item": f"Handrail - {design.top_rail_profile}",
                "description": f"{design.total_length_m:.1f}m total, {design.num_posts} posts",
                "quantity": qty,
                "unit": "ea",
                "weight_kg": design.total_weight_kg * qty,
            })

            if design.has_gates:
                items.append({
                    "item": "Self-Closing Gate",
                    "description": f"{design.gate_width_mm}mm width",
                    "quantity": design.num_gates * qty,
                    "unit": "ea",
                })

        return items
