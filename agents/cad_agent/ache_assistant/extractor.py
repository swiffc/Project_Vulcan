"""
ACHE-Specific Property Extractor
Phase 24.3 - Properties Extraction

Extracts ACHE-specific properties:
- Header box dimensions
- Tube bundle parameters
- Fan system parameters
- Structural frame dimensions
- Nozzle schedule
- Material takeoff (MTO)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger("vulcan.ache.extractor")


class HeaderType(str, Enum):
    """API 661 header types."""
    PLUG = "plug"
    COVER_PLATE = "cover_plate"
    BONNET = "bonnet"  # Not allowed per IOGP S-710


class TubePattern(str, Enum):
    """Tube arrangement patterns."""
    TRIANGULAR = "triangular"
    SQUARE = "square"
    ROTATED_TRIANGULAR = "rotated_triangular"
    ROTATED_SQUARE = "rotated_square"


class FinType(str, Enum):
    """Fin types per API 661."""
    L_FOOTED = "l_footed"
    LL_OVERLAPPED = "ll_overlapped"
    KL_KNURLED = "kl_knurled"
    EMBEDDED = "embedded"
    EXTRUDED = "extruded"


@dataclass
class HeaderBoxData:
    """Header box dimensions and parameters."""
    length_mm: float = 0.0
    width_mm: float = 0.0
    height_mm: float = 0.0
    wall_thickness_mm: float = 0.0
    header_type: HeaderType = HeaderType.PLUG
    num_passes: int = 1
    has_partition: bool = False
    partition_thickness_mm: float = 0.0
    design_pressure_bar: float = 0.0
    design_temp_c: float = 0.0
    material: str = ""
    inlet_temp_c: float = 0.0
    outlet_temp_c: float = 0.0
    delta_t: float = 0.0  # Temperature differential
    requires_split: bool = False  # Per API 661 7.1.6.1.2


@dataclass
class TubeBundleData:
    """Tube bundle parameters."""
    num_rows: int = 0
    tubes_per_row: int = 0
    total_tubes: int = 0
    tube_od_mm: float = 25.4
    tube_wall_mm: float = 2.11
    tube_length_mm: float = 0.0
    tube_pitch_mm: float = 0.0
    pattern: TubePattern = TubePattern.TRIANGULAR
    fin_type: FinType = FinType.L_FOOTED
    fin_height_mm: float = 0.0
    fin_pitch_mm: float = 0.0  # Fins per meter
    fin_thickness_mm: float = 0.0
    tube_material: str = ""
    fin_material: str = ""
    tubesheet_thickness_mm: float = 0.0
    tube_projection_mm: float = 0.0
    support_spacing_mm: float = 0.0
    num_supports: int = 0


@dataclass
class FanSystemData:
    """Fan system parameters."""
    fan_diameter_mm: float = 0.0
    num_fans: int = 1
    num_blades: int = 4
    blade_material: str = "aluminum"
    hub_diameter_mm: float = 0.0
    tip_clearance_mm: float = 0.0
    motor_power_kw: float = 0.0
    motor_voltage: int = 460
    motor_phase: int = 3
    motor_rpm: int = 1800
    fan_rpm: int = 0
    airflow_m3_hr: float = 0.0
    static_pressure_pa: float = 0.0
    drive_type: str = "belt"  # belt, direct, gear
    belt_type: str = ""
    gear_ratio: float = 1.0


@dataclass
class StructuralFrameData:
    """Structural frame dimensions."""
    overall_length_mm: float = 0.0
    overall_width_mm: float = 0.0
    overall_height_mm: float = 0.0
    num_bays: int = 1
    bay_spacing_mm: float = 0.0
    column_size: str = ""  # e.g., "W8x31"
    beam_size: str = ""
    bracing_type: str = ""
    base_elevation_mm: float = 0.0
    platform_elevation_mm: float = 0.0
    steel_grade: str = "A36"


@dataclass
class NozzleData:
    """Nozzle information."""
    tag: str = ""
    service: str = ""  # inlet, outlet, vent, drain
    size_dn: int = 0
    rating_class: int = 150
    facing: str = "RF"  # RF, RTJ, FF
    flange_type: str = "WN"  # WN, SO, SW
    projection_mm: float = 0.0
    orientation_deg: float = 0.0
    elevation_mm: float = 0.0


@dataclass
class MTOItem:
    """Material takeoff item."""
    item_no: int = 0
    description: str = ""
    material: str = ""
    size: str = ""
    quantity: float = 0.0
    unit: str = "EA"
    weight_kg: float = 0.0
    total_weight_kg: float = 0.0
    category: str = ""  # structural, piping, mechanical, electrical


@dataclass
class ACHEProperties:
    """Complete ACHE properties."""
    project_name: str = ""
    equipment_tag: str = ""
    service: str = ""
    design_code: str = "API 661"

    header_box: Optional[HeaderBoxData] = None
    tube_bundle: Optional[TubeBundleData] = None
    fan_system: Optional[FanSystemData] = None
    structural_frame: Optional[StructuralFrameData] = None
    nozzles: List[NozzleData] = field(default_factory=list)
    mto: List[MTOItem] = field(default_factory=list)

    # Calculated values
    dry_weight_kg: float = 0.0
    operating_weight_kg: float = 0.0
    test_weight_kg: float = 0.0
    bundle_weight_kg: float = 0.0

    # Validation flags
    api_661_compliant: bool = False
    validation_issues: List[str] = field(default_factory=list)


class ACHEExtractor:
    """
    Extracts ACHE-specific properties from model data.

    Phase 24.3 Implementation:
    - 24.3.1 Header box dimensions
    - 24.3.2 Tube bundle parameters
    - 24.3.3 Fan system parameters
    - 24.3.4 Structural frame dimensions
    - 24.3.5 Nozzle schedule extraction
    - 24.3.6 Material takeoff (MTO)
    """

    # Property name mappings
    HEADER_PROPS = {
        "Header Length": "length_mm",
        "Header Width": "width_mm",
        "Header Height": "height_mm",
        "Header Wall": "wall_thickness_mm",
        "Header Type": "header_type",
        "Number of Passes": "num_passes",
        "Design Pressure": "design_pressure_bar",
        "Design Temperature": "design_temp_c",
        "Inlet Temperature": "inlet_temp_c",
        "Outlet Temperature": "outlet_temp_c",
    }

    BUNDLE_PROPS = {
        "Number of Rows": "num_rows",
        "Tubes per Row": "tubes_per_row",
        "Tube OD": "tube_od_mm",
        "Tube Wall": "tube_wall_mm",
        "Tube Length": "tube_length_mm",
        "Tube Pitch": "tube_pitch_mm",
        "Fin Height": "fin_height_mm",
        "Fin Pitch": "fin_pitch_mm",
        "Fin Thickness": "fin_thickness_mm",
    }

    FAN_PROPS = {
        "Fan Diameter": "fan_diameter_mm",
        "Number of Fans": "num_fans",
        "Number of Blades": "num_blades",
        "Motor Power": "motor_power_kw",
        "Motor RPM": "motor_rpm",
        "Fan RPM": "fan_rpm",
        "Airflow": "airflow_m3_hr",
    }

    def __init__(self):
        """Initialize the extractor."""
        pass

    def extract(
        self,
        custom_properties: Dict[str, Any],
        components: List[Dict[str, Any]],
        mass_kg: float = 0.0
    ) -> ACHEProperties:
        """
        Extract ACHE properties from model data.

        Args:
            custom_properties: Custom properties from model
            components: List of assembly components
            mass_kg: Total mass from mass properties

        Returns:
            ACHEProperties with all extracted data
        """
        props = ACHEProperties()

        # Extract basic info
        props.project_name = custom_properties.get("Project", "")
        props.equipment_tag = custom_properties.get("Tag",
                              custom_properties.get("Equipment Tag", ""))
        props.service = custom_properties.get("Service", "")

        # Extract specific data
        props.header_box = self._extract_header(custom_properties, components)
        props.tube_bundle = self._extract_bundle(custom_properties, components)
        props.fan_system = self._extract_fan(custom_properties, components)
        props.structural_frame = self._extract_structure(custom_properties, components)
        props.nozzles = self._extract_nozzles(components)
        props.mto = self._generate_mto(props, components)

        # Calculate weights
        props.dry_weight_kg = mass_kg
        props.bundle_weight_kg = self._calc_bundle_weight(props.tube_bundle)
        props.operating_weight_kg = props.dry_weight_kg * 1.1  # Estimate
        props.test_weight_kg = props.dry_weight_kg * 1.3  # Water-filled estimate

        # Validate
        props.validation_issues = self._validate(props)
        props.api_661_compliant = len(props.validation_issues) == 0

        return props

    def _extract_header(
        self,
        props: Dict[str, Any],
        components: List[Dict[str, Any]]
    ) -> HeaderBoxData:
        """Extract header box data."""
        header = HeaderBoxData()

        # Map properties
        for prop_name, attr_name in self.HEADER_PROPS.items():
            if prop_name in props:
                value = props[prop_name]
                if attr_name == "header_type":
                    header.header_type = self._parse_header_type(value)
                elif hasattr(header, attr_name):
                    try:
                        setattr(header, attr_name, float(value))
                    except (ValueError, TypeError):
                        pass

        # Calculate delta T
        if header.inlet_temp_c and header.outlet_temp_c:
            header.delta_t = abs(header.inlet_temp_c - header.outlet_temp_c)
            # Per API 661 7.1.6.1.2: Split header required if ΔT > 110°C
            header.requires_split = header.delta_t > 110

        # Look for header in components
        for comp in components:
            name = comp.get("name", "").lower()
            if "header" in name:
                header.material = comp.get("material", header.material)

        return header

    def _extract_bundle(
        self,
        props: Dict[str, Any],
        components: List[Dict[str, Any]]
    ) -> TubeBundleData:
        """Extract tube bundle data."""
        bundle = TubeBundleData()

        # Map properties
        for prop_name, attr_name in self.BUNDLE_PROPS.items():
            if prop_name in props:
                try:
                    setattr(bundle, attr_name, float(props[prop_name]))
                except (ValueError, TypeError):
                    pass

        # Calculate total tubes
        if bundle.num_rows and bundle.tubes_per_row:
            bundle.total_tubes = bundle.num_rows * bundle.tubes_per_row

        # Parse pattern
        pattern_str = props.get("Tube Pattern", "").lower()
        if "square" in pattern_str:
            bundle.pattern = TubePattern.SQUARE
        elif "rotated" in pattern_str:
            bundle.pattern = TubePattern.ROTATED_TRIANGULAR

        # Parse fin type
        fin_str = props.get("Fin Type", "").lower()
        if "embed" in fin_str:
            bundle.fin_type = FinType.EMBEDDED
        elif "extrud" in fin_str:
            bundle.fin_type = FinType.EXTRUDED
        elif "knurl" in fin_str or "kl" in fin_str:
            bundle.fin_type = FinType.KL_KNURLED
        elif "ll" in fin_str or "overlap" in fin_str:
            bundle.fin_type = FinType.LL_OVERLAPPED

        return bundle

    def _extract_fan(
        self,
        props: Dict[str, Any],
        components: List[Dict[str, Any]]
    ) -> FanSystemData:
        """Extract fan system data."""
        fan = FanSystemData()

        # Map properties
        for prop_name, attr_name in self.FAN_PROPS.items():
            if prop_name in props:
                try:
                    setattr(fan, attr_name, float(props[prop_name]))
                except (ValueError, TypeError):
                    pass

        # Parse drive type
        drive_str = props.get("Drive Type", "belt").lower()
        if "direct" in drive_str:
            fan.drive_type = "direct"
        elif "gear" in drive_str:
            fan.drive_type = "gear"
        else:
            fan.drive_type = "belt"

        # Calculate tip clearance if not specified
        if not fan.tip_clearance_mm and fan.fan_diameter_mm:
            # API 661 Table 6 minimums
            if fan.fan_diameter_mm <= 3000:
                fan.tip_clearance_mm = 6.35  # Min 1/4"
            elif fan.fan_diameter_mm <= 3500:
                fan.tip_clearance_mm = 9.5
            else:
                fan.tip_clearance_mm = 12.7

        return fan

    def _extract_structure(
        self,
        props: Dict[str, Any],
        components: List[Dict[str, Any]]
    ) -> StructuralFrameData:
        """Extract structural frame data."""
        struct = StructuralFrameData()

        struct.overall_length_mm = float(props.get("Overall Length", 0))
        struct.overall_width_mm = float(props.get("Overall Width", 0))
        struct.overall_height_mm = float(props.get("Overall Height", 0))
        struct.num_bays = int(props.get("Number of Bays", 1))
        struct.base_elevation_mm = float(props.get("Base Elevation", 0))
        struct.platform_elevation_mm = float(props.get("Platform Elevation", 0))

        # Look for structural members in components
        for comp in components:
            name = comp.get("name", "").lower()
            if "column" in name and not struct.column_size:
                struct.column_size = self._extract_section_size(name)
            elif "beam" in name and not struct.beam_size:
                struct.beam_size = self._extract_section_size(name)

        return struct

    def _extract_nozzles(self, components: List[Dict[str, Any]]) -> List[NozzleData]:
        """Extract nozzle schedule from components."""
        nozzles = []
        nozzle_keywords = ["nozzle", "inlet", "outlet", "vent", "drain", "connection"]

        for comp in components:
            name = comp.get("name", "").lower()
            if any(kw in name for kw in nozzle_keywords):
                nozzle = NozzleData()
                nozzle.tag = comp.get("name", "")

                # Parse service from name
                if "inlet" in name:
                    nozzle.service = "inlet"
                elif "outlet" in name:
                    nozzle.service = "outlet"
                elif "vent" in name:
                    nozzle.service = "vent"
                elif "drain" in name:
                    nozzle.service = "drain"

                # Try to parse size from name (e.g., "4in Inlet Nozzle")
                import re
                size_match = re.search(r'(\d+)["\s]*(in|inch|dn|mm)', name, re.I)
                if size_match:
                    size_val = int(size_match.group(1))
                    unit = size_match.group(2).lower()
                    if "dn" in unit or "mm" in unit:
                        nozzle.size_dn = size_val
                    else:
                        # Convert inches to DN
                        nozzle.size_dn = int(size_val * 25)

                nozzles.append(nozzle)

        return nozzles

    def _generate_mto(
        self,
        props: ACHEProperties,
        components: List[Dict[str, Any]]
    ) -> List[MTOItem]:
        """Generate material takeoff from properties and components."""
        mto = []
        item_no = 1

        # Add tube bundle
        if props.tube_bundle and props.tube_bundle.total_tubes:
            tb = props.tube_bundle
            mto.append(MTOItem(
                item_no=item_no,
                description=f"Finned Tube {tb.tube_od_mm}mm OD x {tb.tube_length_mm}mm",
                material=tb.tube_material or "Carbon Steel",
                size=f"{tb.tube_od_mm}mm OD x {tb.tube_wall_mm}mm wall",
                quantity=tb.total_tubes,
                unit="EA",
                category="mechanical"
            ))
            item_no += 1

        # Add header
        if props.header_box:
            hb = props.header_box
            mto.append(MTOItem(
                item_no=item_no,
                description=f"Header Box {hb.header_type.value}",
                material=hb.material or "SA-516-70",
                size=f"{hb.length_mm}x{hb.width_mm}x{hb.height_mm}mm",
                quantity=2 if hb.requires_split else 1,
                unit="EA",
                category="mechanical"
            ))
            item_no += 1

        # Add fan
        if props.fan_system:
            fs = props.fan_system
            mto.append(MTOItem(
                item_no=item_no,
                description=f"Fan Assembly {fs.fan_diameter_mm}mm",
                material=fs.blade_material,
                size=f"{fs.fan_diameter_mm}mm, {fs.num_blades} blades",
                quantity=fs.num_fans,
                unit="EA",
                category="mechanical"
            ))
            item_no += 1

            mto.append(MTOItem(
                item_no=item_no,
                description=f"Motor {fs.motor_power_kw}kW",
                material="",
                size=f"{fs.motor_power_kw}kW, {fs.motor_voltage}V, {fs.motor_phase}ph",
                quantity=fs.num_fans,
                unit="EA",
                category="electrical"
            ))
            item_no += 1

        # Add nozzles
        for nozzle in props.nozzles:
            mto.append(MTOItem(
                item_no=item_no,
                description=f"Nozzle {nozzle.tag}",
                material="",
                size=f"DN{nozzle.size_dn} {nozzle.rating_class}# {nozzle.flange_type}",
                quantity=1,
                unit="EA",
                category="piping"
            ))
            item_no += 1

        return mto

    def _validate(self, props: ACHEProperties) -> List[str]:
        """Validate ACHE properties against API 661."""
        issues = []

        # Check header split requirement
        if props.header_box:
            hb = props.header_box
            if hb.delta_t > 110 and not hb.requires_split:
                issues.append(
                    f"API 661 7.1.6.1.2: Split header required for ΔT > 110°C "
                    f"(current ΔT = {hb.delta_t}°C)"
                )

            # Check header type
            if hb.header_type == HeaderType.BONNET:
                issues.append("IOGP S-710: Bonnet-type headers not allowed")

        # Check tube bundle
        if props.tube_bundle:
            tb = props.tube_bundle
            if tb.tube_od_mm < 25.4:
                issues.append(f"API 661: Min tube OD is 25.4mm (1\"), got {tb.tube_od_mm}mm")

            if tb.support_spacing_mm > 1830:
                issues.append(
                    f"API 661: Max tube support spacing is 1830mm (6ft), "
                    f"got {tb.support_spacing_mm}mm"
                )

        # Check fan
        if props.fan_system:
            fs = props.fan_system
            # Check tip clearance per Table 6
            if fs.fan_diameter_mm <= 3000 and fs.tip_clearance_mm < 6.35:
                issues.append(
                    f"API 661 Table 6: Min tip clearance is 6.35mm, "
                    f"got {fs.tip_clearance_mm}mm"
                )

        # Check prohibited nozzle sizes
        prohibited_dn = [32, 65, 90, 125]
        for nozzle in props.nozzles:
            if nozzle.size_dn in prohibited_dn:
                issues.append(
                    f"API 661 7.1.9.5: DN{nozzle.size_dn} is prohibited "
                    f"(nozzle {nozzle.tag})"
                )
            if nozzle.size_dn < 20:
                issues.append(
                    f"API 661: Min nozzle size is DN20, got DN{nozzle.size_dn} "
                    f"(nozzle {nozzle.tag})"
                )

        return issues

    def _parse_header_type(self, value: str) -> HeaderType:
        """Parse header type from string."""
        value_lower = value.lower()
        if "cover" in value_lower:
            return HeaderType.COVER_PLATE
        elif "bonnet" in value_lower:
            return HeaderType.BONNET
        return HeaderType.PLUG

    def _extract_section_size(self, name: str) -> str:
        """Extract structural section size from component name."""
        import re
        # Match patterns like W8x31, HSS6x6x1/4, L4x4x1/4
        match = re.search(r'([WCHSL][\d]+[xX][\d\.\/]+)', name, re.I)
        if match:
            return match.group(1).upper()
        return ""

    def _calc_bundle_weight(self, bundle: Optional[TubeBundleData]) -> float:
        """Estimate tube bundle weight."""
        if not bundle or not bundle.total_tubes:
            return 0.0

        # Steel density ~7850 kg/m³
        # Tube volume = π/4 * (OD² - ID²) * Length
        import math
        od_m = bundle.tube_od_mm / 1000
        id_m = (bundle.tube_od_mm - 2 * bundle.tube_wall_mm) / 1000
        length_m = bundle.tube_length_mm / 1000

        tube_volume = math.pi / 4 * (od_m**2 - id_m**2) * length_m
        tube_weight = tube_volume * 7850  # kg

        # Add ~30% for fins
        total_weight = bundle.total_tubes * tube_weight * 1.3

        return round(total_weight, 1)

    def to_dict(self, props: ACHEProperties) -> Dict[str, Any]:
        """Convert ACHEProperties to dictionary."""
        return {
            "project_name": props.project_name,
            "equipment_tag": props.equipment_tag,
            "service": props.service,
            "design_code": props.design_code,
            "header_box": {
                "length_mm": props.header_box.length_mm,
                "width_mm": props.header_box.width_mm,
                "height_mm": props.header_box.height_mm,
                "wall_thickness_mm": props.header_box.wall_thickness_mm,
                "header_type": props.header_box.header_type.value,
                "num_passes": props.header_box.num_passes,
                "design_pressure_bar": props.header_box.design_pressure_bar,
                "design_temp_c": props.header_box.design_temp_c,
                "delta_t": props.header_box.delta_t,
                "requires_split": props.header_box.requires_split,
                "material": props.header_box.material,
            } if props.header_box else None,
            "tube_bundle": {
                "num_rows": props.tube_bundle.num_rows,
                "tubes_per_row": props.tube_bundle.tubes_per_row,
                "total_tubes": props.tube_bundle.total_tubes,
                "tube_od_mm": props.tube_bundle.tube_od_mm,
                "tube_wall_mm": props.tube_bundle.tube_wall_mm,
                "tube_length_mm": props.tube_bundle.tube_length_mm,
                "pattern": props.tube_bundle.pattern.value,
                "fin_type": props.tube_bundle.fin_type.value,
                "bundle_weight_kg": props.bundle_weight_kg,
            } if props.tube_bundle else None,
            "fan_system": {
                "fan_diameter_mm": props.fan_system.fan_diameter_mm,
                "num_fans": props.fan_system.num_fans,
                "num_blades": props.fan_system.num_blades,
                "motor_power_kw": props.fan_system.motor_power_kw,
                "airflow_m3_hr": props.fan_system.airflow_m3_hr,
                "drive_type": props.fan_system.drive_type,
                "tip_clearance_mm": props.fan_system.tip_clearance_mm,
            } if props.fan_system else None,
            "structural_frame": {
                "overall_length_mm": props.structural_frame.overall_length_mm,
                "overall_width_mm": props.structural_frame.overall_width_mm,
                "overall_height_mm": props.structural_frame.overall_height_mm,
                "num_bays": props.structural_frame.num_bays,
                "column_size": props.structural_frame.column_size,
                "beam_size": props.structural_frame.beam_size,
            } if props.structural_frame else None,
            "nozzles": [
                {
                    "tag": n.tag,
                    "service": n.service,
                    "size_dn": n.size_dn,
                    "rating_class": n.rating_class,
                    "flange_type": n.flange_type,
                }
                for n in props.nozzles
            ],
            "mto_items": len(props.mto),
            "weights": {
                "dry_weight_kg": props.dry_weight_kg,
                "operating_weight_kg": props.operating_weight_kg,
                "test_weight_kg": props.test_weight_kg,
                "bundle_weight_kg": props.bundle_weight_kg,
            },
            "api_661_compliant": props.api_661_compliant,
            "validation_issues": props.validation_issues,
        }
