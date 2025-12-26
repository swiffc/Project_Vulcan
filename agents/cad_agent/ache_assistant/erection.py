"""
ACHE Field Erection Module
Phase 24.8 - Field Erection Support for Air Cooled Heat Exchangers

Provides erection planning and support:
- Lifting lug design
- Rigging calculations
- Erection sequence planning
- Shipping split analysis
- Field assembly procedures
"""

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger("vulcan.ache.erection")


class LiftType(Enum):
    """Types of lifting operations."""
    SINGLE_CRANE = "single_crane"
    DUAL_CRANE = "dual_crane"
    TANDEM_LIFT = "tandem_lift"
    JACKING = "jacking"
    SLIDING = "sliding"


class LugType(Enum):
    """Lifting lug types."""
    PAD_EYE = "pad_eye"
    TRUNNION = "trunnion"
    LIFTING_BRACKET = "lifting_bracket"
    BAIL = "bail"


class ShipmentType(Enum):
    """Shipment configuration types."""
    COMPLETE_UNIT = "complete"
    MODULAR = "modular"
    KNOCKED_DOWN = "knocked_down"
    SUPER_MODULE = "super_module"


@dataclass
class LiftingLugDesign:
    """Lifting lug design results."""
    lug_type: LugType
    location: str  # Description of lug location
    position_mm: Tuple[float, float, float]  # X, Y, Z from reference

    # Loads
    design_load_kn: float = 0.0
    dynamic_factor: float = 2.0  # Impact/dynamic factor
    angle_factor: float = 1.0  # Sling angle factor
    total_design_load_kn: float = 0.0

    # Geometry
    hole_diameter_mm: float = 0.0
    plate_thickness_mm: float = 0.0
    plate_width_mm: float = 0.0
    plate_height_mm: float = 0.0
    weld_size_mm: float = 0.0

    # Capacities
    bearing_capacity_kn: float = 0.0
    tearout_capacity_kn: float = 0.0
    tension_capacity_kn: float = 0.0
    weld_capacity_kn: float = 0.0

    # Results
    utilization: float = 0.0
    is_adequate: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class RiggingPlan:
    """Rigging plan for lift operation."""
    lift_type: LiftType
    total_weight_kg: float
    center_of_gravity: Tuple[float, float, float]

    # Crane requirements
    num_cranes: int = 1
    crane_capacity_tonnes: float = 0.0
    boom_length_m: float = 0.0
    lift_radius_m: float = 0.0

    # Rigging
    num_slings: int = 4
    sling_type: str = "wire_rope"
    sling_diameter_mm: float = 0.0
    sling_length_m: float = 0.0
    sling_angle_deg: float = 60.0
    sling_wll_kn: float = 0.0

    # Spreader beam
    needs_spreader: bool = False
    spreader_length_m: float = 0.0
    spreader_capacity_kn: float = 0.0

    # Shackles
    shackle_size: str = ""
    shackle_wll_kn: float = 0.0
    num_shackles: int = 0

    # Checks
    ground_bearing_ok: bool = True
    swing_clearance_ok: bool = True
    is_adequate: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class ShippingSplit:
    """Shipping split point definition."""
    split_id: str
    location_mm: float  # Position along length
    description: str
    connection_type: str  # bolted, field_welded, slip_on

    # Pieces created
    piece_a_weight_kg: float = 0.0
    piece_b_weight_kg: float = 0.0
    piece_a_dims_m: Tuple[float, float, float] = (0, 0, 0)
    piece_b_dims_m: Tuple[float, float, float] = (0, 0, 0)

    # Transportation
    requires_permit: bool = False
    permit_type: str = ""


@dataclass
class ErectionSequence:
    """Erection sequence step."""
    step_number: int
    description: str
    module: str
    weight_kg: float
    crane_required: str
    duration_hours: float
    prerequisites: List[int] = field(default_factory=list)
    safety_notes: List[str] = field(default_factory=list)


@dataclass
class ErectionPlan:
    """Complete erection plan."""
    project_name: str
    equipment_tag: str
    total_weight_kg: float
    shipment_type: ShipmentType

    # Components
    lifting_lugs: List[LiftingLugDesign] = field(default_factory=list)
    rigging_plan: Optional[RiggingPlan] = None
    shipping_splits: List[ShippingSplit] = field(default_factory=list)
    erection_sequence: List[ErectionSequence] = field(default_factory=list)

    # Summary
    total_lift_hours: float = 0.0
    crane_days: float = 0.0
    is_feasible: bool = True
    warnings: List[str] = field(default_factory=list)


class ErectionPlanner:
    """
    Field erection planner for ACHE units.

    Implements Phase 24.8: Field Erection Support

    Capabilities:
    - Lifting lug design per AISC/AWS
    - Rigging calculations
    - Shipping split optimization
    - Erection sequence planning
    - Crane selection guidance
    """

    # Transportation limits (US typical)
    TRANSPORT_LIMITS = {
        "standard": {
            "length_m": 19.8,  # 65 ft
            "width_m": 2.6,  # 8.5 ft
            "height_m": 4.1,  # 13.5 ft
            "weight_kg": 22680,  # 50,000 lb
        },
        "overwidth": {
            "length_m": 19.8,
            "width_m": 3.7,  # 12 ft
            "height_m": 4.4,  # 14.5 ft
            "weight_kg": 36287,  # 80,000 lb
        },
        "superload": {
            "length_m": 36.6,  # 120 ft
            "width_m": 4.9,  # 16 ft
            "height_m": 5.5,  # 18 ft
            "weight_kg": 90720,  # 200,000 lb
        },
    }

    # Wire rope sling capacities (6x19 IWRC, vertical hitch)
    SLING_CAPACITIES_KN = {
        12.7: 53.4,  # 1/2"
        15.9: 80.1,  # 5/8"
        19.1: 115.6,  # 3/4"
        22.2: 155.7,  # 7/8"
        25.4: 200.2,  # 1"
        28.6: 253.5,  # 1-1/8"
        31.8: 311.4,  # 1-1/4"
        35.0: 377.8,  # 1-3/8"
        38.1: 444.8,  # 1-1/2"
    }

    def __init__(self):
        """Initialize erection planner."""
        self._steel_fy = 250  # A36 yield MPa
        self._safety_factor = 5.0  # Rigging safety factor

    def design_lifting_lug(
        self,
        design_load_kn: float,
        sling_angle_deg: float = 60.0,
        lug_type: LugType = LugType.PAD_EYE,
        material_fy_mpa: float = 250,
    ) -> LiftingLugDesign:
        """
        Design lifting lug for specified load.

        Args:
            design_load_kn: Static design load per lug
            sling_angle_deg: Sling angle from horizontal
            lug_type: Type of lifting lug
            material_fy_mpa: Lug material yield strength

        Returns:
            LiftingLugDesign
        """
        design = LiftingLugDesign(
            lug_type=lug_type,
            location="",
            position_mm=(0, 0, 0),
            design_load_kn=design_load_kn,
        )

        try:
            # Apply factors
            design.dynamic_factor = 2.0  # Per AISC/ASME BTH-1

            # Sling angle factor (load increases as angle decreases)
            angle_rad = math.radians(sling_angle_deg)
            design.angle_factor = 1.0 / math.sin(angle_rad) if angle_rad > 0 else 2.0

            # Total factored load
            design.total_design_load_kn = (
                design_load_kn * design.dynamic_factor * design.angle_factor
            )

            # Determine hole size based on shackle
            # Select shackle for design load
            shackle_wll = design_load_kn * design.dynamic_factor / 9.81  # tonnes
            if shackle_wll <= 4.75:
                design.hole_diameter_mm = 25.4  # 1"
            elif shackle_wll <= 8.5:
                design.hole_diameter_mm = 31.75  # 1-1/4"
            elif shackle_wll <= 12:
                design.hole_diameter_mm = 38.1  # 1-1/2"
            elif shackle_wll <= 17:
                design.hole_diameter_mm = 44.5  # 1-3/4"
            else:
                design.hole_diameter_mm = 50.8  # 2"

            # Plate geometry per ASME BTH-1
            d_h = design.hole_diameter_mm

            # Minimum plate thickness: t >= P / (Fy * d * 0.45)
            # Where P = total load, d = hole diameter
            min_thickness = (
                design.total_design_load_kn * 1000 / (material_fy_mpa * d_h * 0.45)
            )
            # Round up to standard plate
            std_plates = [12.7, 15.9, 19.1, 22.2, 25.4, 31.75, 38.1, 44.5, 50.8]
            design.plate_thickness_mm = next(
                (t for t in std_plates if t >= min_thickness), 50.8
            )

            # Plate width: 2 * (hole radius + edge distance)
            # Edge distance >= 1.5 * hole diameter per ASME BTH-1
            edge_dist = 1.5 * d_h
            design.plate_width_mm = 2 * (d_h / 2 + edge_dist)

            # Plate height: hole center to base
            # Top edge distance >= 0.875 * hole diameter
            top_edge = 0.875 * d_h
            bottom_edge = edge_dist
            design.plate_height_mm = d_h / 2 + top_edge + bottom_edge

            # Weld size (all around fillet weld)
            # Weld length = 2 * plate width + 2 * plate height
            weld_length = 2 * (design.plate_width_mm + design.plate_height_mm)

            # Required weld throat: a = P / (0.6 * Fw * L)
            Fw = 0.6 * 480  # E70 electrode
            req_throat = design.total_design_load_kn * 1000 / (Fw * weld_length)
            design.weld_size_mm = max(6, req_throat / 0.707)  # Fillet weld

            # Calculate capacities
            phi = 0.9  # LRFD factor

            # Bearing capacity on pin
            design.bearing_capacity_kn = (
                phi * 2.4 * material_fy_mpa * d_h * design.plate_thickness_mm / 1000
            )

            # Tearout capacity (shear along two planes)
            edge_clear = edge_dist - d_h / 2
            tearout_area = 2 * edge_clear * design.plate_thickness_mm
            design.tearout_capacity_kn = phi * 0.6 * material_fy_mpa * tearout_area / 1000

            # Tension capacity (net section)
            net_width = design.plate_width_mm - d_h
            net_area = net_width * design.plate_thickness_mm
            design.tension_capacity_kn = phi * 0.75 * material_fy_mpa * net_area / 1000

            # Weld capacity
            actual_throat = 0.707 * design.weld_size_mm
            design.weld_capacity_kn = phi * 0.6 * 480 * actual_throat * weld_length / 1000

            # Governing capacity
            min_capacity = min(
                design.bearing_capacity_kn,
                design.tearout_capacity_kn,
                design.tension_capacity_kn,
                design.weld_capacity_kn,
            )

            design.utilization = design.total_design_load_kn / min_capacity
            design.is_adequate = design.utilization <= 1.0

            if design.utilization > 1.0:
                design.warnings.append(f"Utilization {design.utilization:.2f} > 1.0")

            logger.info(
                f"Lifting lug: {design_load_kn:.1f} kN, "
                f"plate {design.plate_thickness_mm}x{design.plate_width_mm}mm, "
                f"util={design.utilization:.2f}"
            )

        except Exception as e:
            logger.error(f"Lifting lug design error: {e}")
            design.warnings.append(f"Design error: {e}")
            design.is_adequate = False

        return design

    def plan_rigging(
        self,
        total_weight_kg: float,
        cg_location: Tuple[float, float, float],
        lift_points: List[Tuple[float, float, float]],
        lift_height_m: float = 3.0,
        lift_radius_m: float = 15.0,
    ) -> RiggingPlan:
        """
        Plan rigging for lift operation.

        Args:
            total_weight_kg: Total lift weight
            cg_location: Center of gravity (x, y, z) in mm
            lift_points: List of lift point locations in mm
            lift_height_m: Required lift height
            lift_radius_m: Crane operating radius

        Returns:
            RiggingPlan
        """
        plan = RiggingPlan(
            lift_type=LiftType.SINGLE_CRANE,
            total_weight_kg=total_weight_kg,
            center_of_gravity=cg_location,
        )

        try:
            # Number of slings
            plan.num_slings = len(lift_points)
            if plan.num_slings < 2:
                plan.num_slings = 4

            # Load per sling (assume equal distribution)
            weight_kn = total_weight_kg * 9.81 / 1000
            load_per_sling_kn = weight_kn / plan.num_slings

            # Calculate sling geometry
            # Assume lift points form a rectangle
            if len(lift_points) >= 4:
                # Calculate spread
                x_coords = [p[0] for p in lift_points]
                y_coords = [p[1] for p in lift_points]
                spread_x = (max(x_coords) - min(x_coords)) / 1000  # m
                spread_y = (max(y_coords) - min(y_coords)) / 1000  # m

                # Diagonal spread
                diagonal = math.sqrt(spread_x ** 2 + spread_y ** 2)

                # Sling length for desired angle
                plan.sling_angle_deg = 60  # Target angle
                angle_rad = math.radians(plan.sling_angle_deg)
                plan.sling_length_m = (diagonal / 2) / math.cos(angle_rad)
            else:
                plan.sling_length_m = 3.0  # Default

            # Select sling size
            # Factored load per sling with angle
            angle_factor = 1 / math.sin(math.radians(plan.sling_angle_deg))
            design_load = load_per_sling_kn * angle_factor * self._safety_factor

            for diameter, wll in sorted(self.SLING_CAPACITIES_KN.items()):
                if wll >= design_load:
                    plan.sling_diameter_mm = diameter
                    plan.sling_wll_kn = wll
                    break
            else:
                plan.sling_diameter_mm = 38.1
                plan.sling_wll_kn = self.SLING_CAPACITIES_KN[38.1]
                plan.warnings.append("Maximum sling size selected - verify capacity")

            # Spreader beam check
            # Needed if sling angle would be too shallow
            if plan.sling_angle_deg < 45:
                plan.needs_spreader = True
                plan.spreader_length_m = diagonal * 0.8
                plan.spreader_capacity_kn = weight_kn * 1.5

            # Shackle selection
            shackle_load = load_per_sling_kn * angle_factor
            plan.num_shackles = plan.num_slings * 2  # At each end
            if shackle_load <= 47:
                plan.shackle_size = "3/4\""
                plan.shackle_wll_kn = 47
            elif shackle_load <= 85:
                plan.shackle_size = "1\""
                plan.shackle_wll_kn = 85
            elif shackle_load <= 133:
                plan.shackle_size = "1-1/4\""
                plan.shackle_wll_kn = 133
            else:
                plan.shackle_size = "1-1/2\""
                plan.shackle_wll_kn = 187

            # Crane requirements
            plan.lift_radius_m = lift_radius_m

            # Required crane capacity (with contingency)
            crane_capacity_kg = total_weight_kg * 1.25  # 25% contingency
            rigging_weight_kg = plan.num_slings * plan.sling_length_m * 5  # Estimate
            hook_block_kg = 500  # Typical

            total_crane_load = crane_capacity_kg + rigging_weight_kg + hook_block_kg
            plan.crane_capacity_tonnes = total_crane_load / 1000

            # Boom length estimate
            plan.boom_length_m = math.sqrt(
                lift_radius_m ** 2 + (lift_height_m + 5) ** 2
            ) * 1.1

            # Check if dual crane needed
            if total_weight_kg > 100000:  # > 100 tonnes
                plan.lift_type = LiftType.DUAL_CRANE
                plan.num_cranes = 2
                plan.crane_capacity_tonnes /= 2

            plan.is_adequate = True

            logger.info(
                f"Rigging plan: {total_weight_kg:.0f} kg, "
                f"{plan.num_slings} slings @ {plan.sling_diameter_mm}mm, "
                f"crane {plan.crane_capacity_tonnes:.1f}T"
            )

        except Exception as e:
            logger.error(f"Rigging plan error: {e}")
            plan.warnings.append(f"Planning error: {e}")
            plan.is_adequate = False

        return plan

    def analyze_shipping_splits(
        self,
        unit_length_m: float,
        unit_width_m: float,
        unit_height_m: float,
        unit_weight_kg: float,
        max_transport_category: str = "overwidth",
    ) -> List[ShippingSplit]:
        """
        Analyze shipping splits for transportation.

        Args:
            unit_length_m: Total unit length
            unit_width_m: Total unit width
            unit_height_m: Total unit height
            unit_weight_kg: Total unit weight
            max_transport_category: Maximum transport category allowed

        Returns:
            List of ShippingSplit recommendations
        """
        splits = []
        limits = self.TRANSPORT_LIMITS[max_transport_category]

        try:
            # Check if unit fits without splitting
            fits_length = unit_length_m <= limits["length_m"]
            fits_width = unit_width_m <= limits["width_m"]
            fits_height = unit_height_m <= limits["height_m"]
            fits_weight = unit_weight_kg <= limits["weight_kg"]

            if fits_length and fits_width and fits_height and fits_weight:
                logger.info("Unit ships complete - no splits required")
                return splits

            # Determine split locations
            split_count = 0

            # Length splits
            if not fits_length:
                num_length_splits = math.ceil(unit_length_m / limits["length_m"]) - 1
                segment_length = unit_length_m / (num_length_splits + 1)

                for i in range(num_length_splits):
                    split_count += 1
                    split_location = segment_length * (i + 1) * 1000  # mm

                    split = ShippingSplit(
                        split_id=f"L{split_count}",
                        location_mm=split_location,
                        description=f"Length split at {split_location/1000:.1f}m",
                        connection_type="bolted",
                        piece_a_weight_kg=unit_weight_kg / (num_length_splits + 1),
                        piece_b_weight_kg=unit_weight_kg / (num_length_splits + 1),
                        piece_a_dims_m=(segment_length, unit_width_m, unit_height_m),
                        piece_b_dims_m=(unit_length_m - split_location/1000, unit_width_m, unit_height_m),
                    )

                    # Check if permit needed
                    if segment_length > self.TRANSPORT_LIMITS["standard"]["length_m"]:
                        split.requires_permit = True
                        split.permit_type = "overlength"

                    splits.append(split)

            # Width splits (typically at bay boundaries)
            if not fits_width:
                num_width_splits = math.ceil(unit_width_m / limits["width_m"]) - 1

                for i in range(num_width_splits):
                    split_count += 1
                    split_location = (unit_width_m / (num_width_splits + 1)) * (i + 1) * 1000

                    split = ShippingSplit(
                        split_id=f"W{split_count}",
                        location_mm=split_location,
                        description=f"Width split at {split_location/1000:.1f}m (bay split)",
                        connection_type="bolted",
                        requires_permit=True,
                        permit_type="overwidth",
                    )
                    splits.append(split)

            # Weight-based splits
            if not fits_weight and len(splits) == 0:
                num_weight_splits = math.ceil(unit_weight_kg / limits["weight_kg"]) - 1
                segment_length = unit_length_m / (num_weight_splits + 1)

                for i in range(num_weight_splits):
                    split_count += 1
                    split = ShippingSplit(
                        split_id=f"WT{split_count}",
                        location_mm=segment_length * (i + 1) * 1000,
                        description=f"Weight split for transport",
                        connection_type="bolted",
                        piece_a_weight_kg=unit_weight_kg / (num_weight_splits + 1),
                        piece_b_weight_kg=unit_weight_kg / (num_weight_splits + 1),
                    )
                    splits.append(split)

            logger.info(f"Shipping analysis: {len(splits)} splits required")

        except Exception as e:
            logger.error(f"Shipping analysis error: {e}")

        return splits

    def create_erection_sequence(
        self,
        modules: List[Dict[str, Any]],
        site_constraints: Optional[Dict[str, Any]] = None,
    ) -> List[ErectionSequence]:
        """
        Create erection sequence for ACHE modules.

        Args:
            modules: List of modules with weight, dimensions, type
            site_constraints: Site-specific constraints

        Returns:
            List of ErectionSequence steps
        """
        sequence = []
        step_num = 0

        try:
            # Sort modules by erection priority
            # Priority: foundation -> columns -> beams -> bundle -> fans -> accessories
            priority_order = {
                "foundation": 1,
                "column": 2,
                "beam": 3,
                "structure": 3,
                "bundle": 4,
                "header": 5,
                "fan": 6,
                "motor": 7,
                "platform": 8,
                "ladder": 8,
                "handrail": 9,
                "piping": 10,
            }

            sorted_modules = sorted(
                modules,
                key=lambda m: priority_order.get(m.get("type", "").lower(), 99)
            )

            crane_sizes = {
                "light": "50T mobile",
                "medium": "100T mobile",
                "heavy": "200T crawler",
                "super_heavy": "500T+ crawler",
            }

            for module in sorted_modules:
                step_num += 1
                weight = module.get("weight_kg", 0)

                # Determine crane size
                if weight < 10000:
                    crane = crane_sizes["light"]
                elif weight < 30000:
                    crane = crane_sizes["medium"]
                elif weight < 80000:
                    crane = crane_sizes["heavy"]
                else:
                    crane = crane_sizes["super_heavy"]

                # Estimate duration
                base_hours = 2.0
                if weight > 50000:
                    base_hours = 4.0
                elif weight > 20000:
                    base_hours = 3.0

                # Build sequence step
                step = ErectionSequence(
                    step_number=step_num,
                    description=f"Erect {module.get('name', f'Module {step_num}')}",
                    module=module.get("name", ""),
                    weight_kg=weight,
                    crane_required=crane,
                    duration_hours=base_hours,
                    prerequisites=[s.step_number for s in sequence if s.step_number < step_num],
                    safety_notes=self._get_safety_notes(module.get("type", "")),
                )
                sequence.append(step)

            logger.info(f"Erection sequence: {len(sequence)} steps")

        except Exception as e:
            logger.error(f"Erection sequence error: {e}")

        return sequence

    def _get_safety_notes(self, module_type: str) -> List[str]:
        """Get safety notes for module type."""
        notes = ["Verify rigging before lift", "Maintain exclusion zone"]

        type_lower = module_type.lower()

        if "column" in type_lower or "structure" in type_lower:
            notes.extend([
                "Check anchor bolt alignment before setting",
                "Use tag lines to control rotation",
            ])
        elif "bundle" in type_lower:
            notes.extend([
                "Support tubes during lift - prevent sagging",
                "Verify CG location matches rigging plan",
            ])
        elif "fan" in type_lower:
            notes.extend([
                "Protect blade tips during handling",
                "Verify motor rotation before final connection",
            ])
        elif "platform" in type_lower or "ladder" in type_lower:
            notes.append("Install fall protection before releasing crane")

        return notes

    def create_erection_plan(
        self,
        project_name: str,
        equipment_tag: str,
        ache_properties: Dict[str, Any],
    ) -> ErectionPlan:
        """
        Create complete erection plan for ACHE unit.

        Args:
            project_name: Project name
            equipment_tag: Equipment tag number
            ache_properties: ACHE properties from extractor

        Returns:
            Complete ErectionPlan
        """
        plan = ErectionPlan(
            project_name=project_name,
            equipment_tag=equipment_tag,
            total_weight_kg=0,
            shipment_type=ShipmentType.MODULAR,
        )

        try:
            # Get total weight
            mass_props = ache_properties.get("mass_properties", {})
            plan.total_weight_kg = mass_props.get("mass_kg", 0) or ache_properties.get("total_weight_kg", 0)

            # Get dimensions
            bbox = ache_properties.get("bounding_box", {})
            length_m = bbox.get("length_mm", 0) / 1000
            width_m = bbox.get("width_mm", 0) / 1000
            height_m = bbox.get("height_mm", 0) / 1000

            # Analyze shipping
            plan.shipping_splits = self.analyze_shipping_splits(
                length_m, width_m, height_m, plan.total_weight_kg
            )

            if len(plan.shipping_splits) == 0:
                plan.shipment_type = ShipmentType.COMPLETE_UNIT
            elif len(plan.shipping_splits) <= 2:
                plan.shipment_type = ShipmentType.MODULAR
            else:
                plan.shipment_type = ShipmentType.KNOCKED_DOWN

            # Design lifting lugs
            # Assume 4-point lift
            lift_load = plan.total_weight_kg * 9.81 / 4000  # kN per lug

            for i, corner in enumerate(["NE", "NW", "SE", "SW"]):
                lug = self.design_lifting_lug(
                    design_load_kn=lift_load,
                    sling_angle_deg=60,
                )
                lug.location = f"Lug {corner}"
                plan.lifting_lugs.append(lug)

            # Create rigging plan
            cg = mass_props.get("center_of_mass", (0, 0, 0))
            lift_points = [
                (0, 0, 0),
                (length_m * 1000, 0, 0),
                (0, width_m * 1000, 0),
                (length_m * 1000, width_m * 1000, 0),
            ]
            plan.rigging_plan = self.plan_rigging(
                plan.total_weight_kg,
                cg,
                lift_points,
            )

            # Build erection sequence
            modules = []

            # Structure
            modules.append({
                "name": "Support Structure",
                "type": "structure",
                "weight_kg": plan.total_weight_kg * 0.15,
            })

            # Bundle
            modules.append({
                "name": "Tube Bundle",
                "type": "bundle",
                "weight_kg": plan.total_weight_kg * 0.60,
            })

            # Fans
            fan_data = ache_properties.get("fan_system", {})
            num_fans = fan_data.get("num_fans", 1)
            for i in range(num_fans):
                modules.append({
                    "name": f"Fan Assembly {i+1}",
                    "type": "fan",
                    "weight_kg": plan.total_weight_kg * 0.05 / num_fans,
                })

            # Accessories
            modules.append({
                "name": "Platforms and Handrails",
                "type": "platform",
                "weight_kg": plan.total_weight_kg * 0.08,
            })

            plan.erection_sequence = self.create_erection_sequence(modules)

            # Calculate totals
            plan.total_lift_hours = sum(s.duration_hours for s in plan.erection_sequence)
            plan.crane_days = plan.total_lift_hours / 8

            plan.is_feasible = all(lug.is_adequate for lug in plan.lifting_lugs)
            if plan.rigging_plan:
                plan.is_feasible = plan.is_feasible and plan.rigging_plan.is_adequate

            logger.info(
                f"Erection plan: {plan.total_weight_kg:.0f} kg, "
                f"{len(plan.shipping_splits)} splits, "
                f"{plan.total_lift_hours:.1f} hrs"
            )

        except Exception as e:
            logger.error(f"Erection plan error: {e}")
            plan.warnings.append(f"Planning error: {e}")
            plan.is_feasible = False

        return plan
