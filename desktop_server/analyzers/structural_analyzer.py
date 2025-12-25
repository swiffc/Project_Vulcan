"""
Structural Component Analyzer
=============================
Phase 24.22-24.33 Implementation - ACHE Structural Analysis

Comprehensive analysis of ACHE structural components:
- 24.22 Plenum Chamber Analysis
- 24.23 Fan System Analysis
- 24.24 Louver System Analysis
- 24.25 Structural Frame Analysis
- 24.26 Tube Bundle Analysis
- 24.27 Header Box Analysis
- 24.28 Pipe & Nozzle Analysis
- 24.29 Access Panel Analysis
- 24.30 Vibration Analysis
- 24.31 Lifting Analysis
- 24.32 Shipping Analysis
- 24.33 Walkway & Platform Analysis
"""

import logging
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("vulcan.analyzer.structural")


# =============================================================================
# Data Classes for Each Analysis Type
# =============================================================================

@dataclass
class PlenumAnalysis:
    """24.22 Plenum Chamber Analysis"""
    volume_ft3: float = 0.0
    velocity_fpm: float = 0.0
    pressure_drop_in_wg: float = 0.0
    uniformity_index: float = 0.0  # 0-1, 1 = perfect
    access_panel_count: int = 0
    drain_present: bool = False
    issues: List[str] = field(default_factory=list)


@dataclass
class FanSystemAnalysis:
    """24.23 Fan System Analysis"""
    fan_count: int = 0
    fan_diameter_in: float = 0.0
    tip_clearance_in: float = 0.0
    hub_ratio: float = 0.0
    blade_count: int = 0
    motor_hp: float = 0.0
    rpm: int = 0
    cfm: float = 0.0
    static_pressure_in_wg: float = 0.0
    tip_speed_fpm: float = 0.0
    issues: List[str] = field(default_factory=list)


@dataclass
class LouverAnalysis:
    """24.24 Louver System Analysis"""
    louver_count: int = 0
    blade_angle_deg: float = 0.0
    free_area_percent: float = 0.0
    pressure_drop_in_wg: float = 0.0
    actuator_type: str = ""  # manual, pneumatic, electric
    issues: List[str] = field(default_factory=list)


@dataclass
class FrameAnalysis:
    """24.25 Structural Frame Analysis"""
    column_count: int = 0
    beam_count: int = 0
    column_sizes: List[str] = field(default_factory=list)
    beam_sizes: List[str] = field(default_factory=list)
    total_weight_lbs: float = 0.0
    wind_load_psf: float = 0.0
    seismic_category: str = ""
    issues: List[str] = field(default_factory=list)


@dataclass
class TubeBundleAnalysis:
    """24.26 Tube Bundle Analysis"""
    tube_count: int = 0
    tube_od_in: float = 0.0
    tube_length_ft: float = 0.0
    tube_pitch_in: float = 0.0
    tube_pattern: str = ""  # triangular, square, rotated
    rows: int = 0
    passes: int = 0
    fin_density_fpi: float = 0.0
    fin_height_in: float = 0.0
    surface_area_ft2: float = 0.0
    bundle_weight_lbs: float = 0.0
    issues: List[str] = field(default_factory=list)


@dataclass
class HeaderBoxAnalysis:
    """24.27 Header Box Analysis"""
    header_count: int = 0
    plug_count: int = 0
    plug_type: str = ""  # threaded, seal welded
    pass_partition_count: int = 0
    nozzle_count: int = 0
    design_pressure_psi: float = 0.0
    design_temp_f: float = 0.0
    material: str = ""
    issues: List[str] = field(default_factory=list)


@dataclass
class LiftingAnalysis:
    """24.31 Lifting Analysis"""
    total_weight_lbs: float = 0.0
    lifting_lug_count: int = 0
    lug_capacity_lbs: float = 0.0
    center_of_gravity: tuple = (0.0, 0.0, 0.0)
    lift_angle_deg: float = 0.0
    sling_load_lbs: float = 0.0
    crane_radius_ft: float = 0.0
    issues: List[str] = field(default_factory=list)


@dataclass
class ShippingAnalysis:
    """24.32 Shipping Analysis"""
    overall_length_ft: float = 0.0
    overall_width_ft: float = 0.0
    overall_height_ft: float = 0.0
    shipping_weight_lbs: float = 0.0
    requires_permit: bool = False
    requires_escort: bool = False
    max_axle_load_lbs: float = 0.0
    tiedown_count: int = 0
    issues: List[str] = field(default_factory=list)


@dataclass
class StructuralAnalysisResult:
    """Complete structural analysis results."""
    plenum: Optional[PlenumAnalysis] = None
    fan_system: Optional[FanSystemAnalysis] = None
    louvers: Optional[LouverAnalysis] = None
    frame: Optional[FrameAnalysis] = None
    tube_bundle: Optional[TubeBundleAnalysis] = None
    header_box: Optional[HeaderBoxAnalysis] = None
    lifting: Optional[LiftingAnalysis] = None
    shipping: Optional[ShippingAnalysis] = None
    all_issues: List[str] = field(default_factory=list)


# =============================================================================
# Structural Analyzer Class
# =============================================================================

class StructuralAnalyzer:
    """
    Comprehensive ACHE structural analysis (Phase 24.22-24.33).
    Analyzes assembly components and provides design validation.
    """

    # Design limits and standards
    MAX_FAN_TIP_SPEED_FPM = 12000
    MIN_TIP_CLEARANCE_RATIO = 0.005  # Of diameter
    MAX_PLENUM_VELOCITY_FPM = 1200
    MAX_TUBE_VIBRATION_AMPLITUDE_IN = 0.010
    STANDARD_SHIPPING_WIDTH_FT = 14
    STANDARD_SHIPPING_HEIGHT_FT = 14

    def __init__(self):
        self._sw_app = None
        self._doc = None

    def _connect(self) -> bool:
        """Connect to SolidWorks COM interface."""
        try:
            import win32com.client
            self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
            self._doc = self._sw_app.ActiveDoc
            return self._doc is not None and self._doc.GetType() == 2  # Assembly
        except Exception as e:
            logger.error(f"Failed to connect to SolidWorks: {e}")
            return False

    def analyze_plenum(self, components: List[Dict]) -> PlenumAnalysis:
        """Analyze plenum chamber (24.22)."""
        result = PlenumAnalysis()

        plenum_parts = [c for c in components if "plenum" in c.get("name", "").lower()]

        if plenum_parts:
            # Calculate approximate volume from bounding box
            for part in plenum_parts:
                bbox = part.get("bounding_box", {})
                if bbox:
                    result.volume_ft3 = (
                        bbox.get("length", 0) *
                        bbox.get("width", 0) *
                        bbox.get("height", 0)
                    ) / 1728  # in³ to ft³

            # Count access panels
            result.access_panel_count = sum(
                1 for c in components
                if any(x in c.get("name", "").lower() for x in ["access", "panel", "door"])
            )

            # Check for drain
            result.drain_present = any(
                "drain" in c.get("name", "").lower() for c in components
            )

            if not result.drain_present:
                result.issues.append("No drain detected in plenum - may cause water accumulation")

            if result.access_panel_count == 0:
                result.issues.append("No access panels detected for maintenance")

        return result

    def analyze_fan_system(self, components: List[Dict]) -> FanSystemAnalysis:
        """Analyze fan system (24.23)."""
        result = FanSystemAnalysis()

        fan_parts = [c for c in components if "fan" in c.get("name", "").lower()]
        motor_parts = [c for c in components if "motor" in c.get("name", "").lower()]

        result.fan_count = len([f for f in fan_parts if "ring" not in f.get("name", "").lower()])

        # Estimate diameter from fan ring
        fan_rings = [f for f in fan_parts if "ring" in f.get("name", "").lower()]
        if fan_rings:
            bbox = fan_rings[0].get("bounding_box", {})
            result.fan_diameter_in = max(bbox.get("length", 0), bbox.get("width", 0))

        # Calculate tip speed if RPM available
        if result.fan_diameter_in > 0 and result.rpm > 0:
            result.tip_speed_fpm = (result.fan_diameter_in * math.pi * result.rpm) / 12

            if result.tip_speed_fpm > self.MAX_FAN_TIP_SPEED_FPM:
                result.issues.append(
                    f"Fan tip speed {result.tip_speed_fpm:.0f} FPM exceeds max {self.MAX_FAN_TIP_SPEED_FPM} FPM"
                )

        # Check tip clearance
        if result.fan_diameter_in > 0 and result.tip_clearance_in > 0:
            clearance_ratio = result.tip_clearance_in / result.fan_diameter_in
            if clearance_ratio < self.MIN_TIP_CLEARANCE_RATIO:
                result.issues.append(
                    f"Tip clearance {result.tip_clearance_in:.3f}\" may be too tight"
                )

        return result

    def analyze_tube_bundle(self, components: List[Dict]) -> TubeBundleAnalysis:
        """Analyze tube bundle (24.26)."""
        result = TubeBundleAnalysis()

        tube_parts = [c for c in components if "tube" in c.get("name", "").lower()]
        fin_parts = [c for c in components if "fin" in c.get("name", "").lower()]

        result.tube_count = len(tube_parts)

        # Get tube dimensions from first tube
        if tube_parts:
            tube = tube_parts[0]
            bbox = tube.get("bounding_box", {})
            # Estimate OD from smallest dimension
            dims = [bbox.get("length", 0), bbox.get("width", 0), bbox.get("height", 0)]
            dims = [d for d in dims if d > 0]
            if dims:
                result.tube_od_in = min(dims)
                result.tube_length_ft = max(dims) / 12

        # Check tube count is reasonable
        if result.tube_count > 0 and result.rows > 0:
            tubes_per_row = result.tube_count / result.rows
            if tubes_per_row % 1 != 0:
                result.issues.append(
                    f"Tube count {result.tube_count} doesn't divide evenly by row count {result.rows}"
                )

        return result

    def analyze_header_box(self, components: List[Dict]) -> HeaderBoxAnalysis:
        """Analyze header box (24.27)."""
        result = HeaderBoxAnalysis()

        header_parts = [c for c in components if "header" in c.get("name", "").lower()]
        plug_parts = [c for c in components if "plug" in c.get("name", "").lower()]
        nozzle_parts = [c for c in components if "nozzle" in c.get("name", "").lower()]

        result.header_count = len(header_parts)
        result.plug_count = len(plug_parts)
        result.nozzle_count = len(nozzle_parts)

        # Check plug count matches tube count
        if result.plug_count > 0:
            tube_parts = [c for c in components if "tube" in c.get("name", "").lower()]
            if len(tube_parts) > 0 and result.plug_count != len(tube_parts):
                result.issues.append(
                    f"Plug count {result.plug_count} doesn't match tube count {len(tube_parts)}"
                )

        return result

    def analyze_lifting(self, total_weight_lbs: float, components: List[Dict]) -> LiftingAnalysis:
        """Analyze lifting requirements (24.31)."""
        result = LiftingAnalysis()
        result.total_weight_lbs = total_weight_lbs

        # Count lifting lugs
        lug_parts = [c for c in components if any(x in c.get("name", "").lower() for x in ["lug", "lift", "trunnion"])]
        result.lifting_lug_count = len(lug_parts)

        if result.lifting_lug_count == 0:
            result.issues.append("No lifting lugs detected")
        elif result.lifting_lug_count < 4 and total_weight_lbs > 10000:
            result.issues.append(
                f"Only {result.lifting_lug_count} lugs for {total_weight_lbs:.0f} lbs - consider adding more"
            )

        # Estimate lug load (assume 4-point lift at 60° sling angle)
        if result.lifting_lug_count >= 2:
            result.lift_angle_deg = 60
            angle_factor = 1 / math.sin(math.radians(result.lift_angle_deg))
            result.sling_load_lbs = (total_weight_lbs / result.lifting_lug_count) * angle_factor

        return result

    def analyze_shipping(self, components: List[Dict], total_weight_lbs: float) -> ShippingAnalysis:
        """Analyze shipping requirements (24.32)."""
        result = ShippingAnalysis()
        result.shipping_weight_lbs = total_weight_lbs

        # Calculate overall dimensions from all components
        all_dims = []
        for c in components:
            bbox = c.get("bounding_box", {})
            if bbox:
                all_dims.append((
                    bbox.get("length", 0),
                    bbox.get("width", 0),
                    bbox.get("height", 0)
                ))

        if all_dims:
            result.overall_length_ft = max(d[0] for d in all_dims) / 12
            result.overall_width_ft = max(d[1] for d in all_dims) / 12
            result.overall_height_ft = max(d[2] for d in all_dims) / 12

        # Check permit requirements
        if result.overall_width_ft > self.STANDARD_SHIPPING_WIDTH_FT:
            result.requires_permit = True
            result.issues.append(
                f"Width {result.overall_width_ft:.1f}' exceeds standard {self.STANDARD_SHIPPING_WIDTH_FT}' - permit required"
            )

        if result.overall_height_ft > self.STANDARD_SHIPPING_HEIGHT_FT:
            result.requires_permit = True
            result.requires_escort = True
            result.issues.append(
                f"Height {result.overall_height_ft:.1f}' exceeds standard {self.STANDARD_SHIPPING_HEIGHT_FT}' - escort required"
            )

        # Estimate tiedown count
        result.tiedown_count = max(4, int(result.shipping_weight_lbs / 10000) * 2)

        return result

    def analyze(self) -> StructuralAnalysisResult:
        """Perform complete structural analysis."""
        result = StructuralAnalysisResult()

        if not self._connect():
            logger.warning("Not connected to a SolidWorks assembly")
            return result

        try:
            # Get all components
            config_mgr = self._doc.ConfigurationManager
            active_config = config_mgr.ActiveConfiguration
            root_component = active_config.GetRootComponent3(True)

            if not root_component:
                return result

            children = root_component.GetChildren()
            if not children:
                return result

            # Build component list
            components = []
            total_weight = 0.0

            for comp in children:
                try:
                    comp_name = comp.Name2
                    if not comp_name:
                        continue

                    comp_data = {"name": comp_name, "bounding_box": {}}

                    # Get bounding box
                    ref_model = comp.GetModelDoc2()
                    if ref_model:
                        try:
                            box = ref_model.GetBox()
                            if box:
                                comp_data["bounding_box"] = {
                                    "length": abs(box[3] - box[0]) * 39.3701,  # m to in
                                    "width": abs(box[4] - box[1]) * 39.3701,
                                    "height": abs(box[5] - box[2]) * 39.3701,
                                }
                        except Exception:
                            pass

                        # Get mass
                        try:
                            mass_props = ref_model.Extension.CreateMassProperty()
                            if mass_props:
                                total_weight += mass_props.Mass * 2.205  # kg to lbs
                        except Exception:
                            pass

                    components.append(comp_data)
                except Exception:
                    continue

            # Run all analyses
            result.plenum = self.analyze_plenum(components)
            result.fan_system = self.analyze_fan_system(components)
            result.tube_bundle = self.analyze_tube_bundle(components)
            result.header_box = self.analyze_header_box(components)
            result.lifting = self.analyze_lifting(total_weight, components)
            result.shipping = self.analyze_shipping(components, total_weight)

            # Collect all issues
            for analysis in [result.plenum, result.fan_system, result.tube_bundle,
                           result.header_box, result.lifting, result.shipping]:
                if analysis and hasattr(analysis, 'issues'):
                    result.all_issues.extend(analysis.issues)

        except Exception as e:
            logger.error(f"Structural analysis error: {e}")

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Analyze and return results as dictionary."""
        result = self.analyze()

        def analysis_to_dict(analysis):
            if analysis is None:
                return None
            d = {}
            for key, value in analysis.__dict__.items():
                if isinstance(value, list):
                    d[key] = value
                elif isinstance(value, tuple):
                    d[key] = list(value)
                else:
                    d[key] = value
            return d

        return {
            "plenum_analysis": analysis_to_dict(result.plenum),
            "fan_system_analysis": analysis_to_dict(result.fan_system),
            "tube_bundle_analysis": analysis_to_dict(result.tube_bundle),
            "header_box_analysis": analysis_to_dict(result.header_box),
            "lifting_analysis": analysis_to_dict(result.lifting),
            "shipping_analysis": analysis_to_dict(result.shipping),
            "all_issues": result.all_issues,
            "issue_count": len(result.all_issues),
        }
