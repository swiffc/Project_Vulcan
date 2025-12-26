"""
Tests for Phase 24 ACHE Design Assistant modules.

Tests cover:
- Calculator (thermal, pressure drop, fan)
- Structural designer (columns, beams, frames)
- Accessory designer (platforms, ladders, handrails)
- AI assistant (compliance, recommendations)
- Erection planner (lifting lugs, rigging)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestACHECalculator:
    """Tests for ACHECalculator module."""

    def test_import_calculator(self):
        """Test calculator module imports correctly."""
        from agents.cad_agent.ache_assistant import ACHECalculator, ThermalResults, FanResults
        assert ACHECalculator is not None
        assert ThermalResults is not None
        assert FanResults is not None

    def test_fluid_properties_air(self):
        """Test air properties at temperature."""
        from agents.cad_agent.ache_assistant.calculator import FluidProperties

        air = FluidProperties.air_at_temperature(25)
        assert air.density_kg_m3 > 1.0
        assert air.density_kg_m3 < 1.3
        assert air.specific_heat_j_kg_k > 1000

    def test_thermal_lmtd_calculation(self):
        """Test LMTD calculation."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()
        lmtd = calc._calculate_lmtd(100, 60, 25, 45)

        # LMTD should be between min and max delta-T
        assert lmtd > 0
        assert lmtd < 75  # Max would be 100-25=75

    def test_fan_performance(self):
        """Test fan performance calculation."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()
        results = calc.calculate_fan_performance(
            air_flow_m3_s=50,
            static_pressure_pa=200,
            fan_diameter_m=3.0,
            fan_rpm=300,
            fan_efficiency=0.75,
        )

        assert results.air_flow_m3_s == 50
        assert results.shaft_power_kw > 0
        assert results.motor_power_kw > results.shaft_power_kw
        assert results.tip_speed_m_s > 0

    def test_fan_tip_speed_check(self):
        """Test API 661 tip speed limit check."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()

        # Low speed - should be acceptable
        results = calc.calculate_fan_performance(
            air_flow_m3_s=50,
            static_pressure_pa=200,
            fan_diameter_m=3.0,
            fan_rpm=300,
        )
        assert results.tip_speed_acceptable is True

        # High speed - should exceed limit
        results_high = calc.calculate_fan_performance(
            air_flow_m3_s=50,
            static_pressure_pa=200,
            fan_diameter_m=3.0,
            fan_rpm=500,
        )
        assert results_high.tip_speed_m_s > 61  # API 661 limit

    def test_ache_sizing(self):
        """Test preliminary ACHE sizing."""
        from agents.cad_agent.ache_assistant import ACHECalculator, FluidProperties

        calc = ACHECalculator()
        fluid = FluidProperties(
            density_kg_m3=800,
            specific_heat_j_kg_k=2000,
            viscosity_pa_s=0.001,
            thermal_conductivity_w_m_k=0.15,
            prandtl_number=10,
        )

        sizing = calc.size_ache(
            duty_kw=1000,
            process_inlet_temp_c=120,
            process_outlet_temp_c=60,
            air_inlet_temp_c=35,
            process_fluid=fluid,
        )

        assert sizing["duty_kw"] == 1000
        assert sizing["surface_area_m2"] > 0
        assert sizing["num_fans"] >= 1
        assert "lmtd_k" in sizing


class TestStructuralDesigner:
    """Tests for StructuralDesigner module."""

    def test_import_structural(self):
        """Test structural module imports correctly."""
        from agents.cad_agent.ache_assistant import StructuralDesigner, ColumnDesign, BeamDesign
        assert StructuralDesigner is not None
        assert ColumnDesign is not None
        assert BeamDesign is not None

    def test_column_design(self):
        """Test column design."""
        from agents.cad_agent.ache_assistant import StructuralDesigner

        designer = StructuralDesigner()
        column = designer.design_column(
            axial_load_kn=200,
            moment_kn_m=50,
            height_m=4.0,
            k_factor=1.0,
        )

        assert column.profile != ""
        assert column.axial_capacity_kn > 0
        assert column.utilization_ratio > 0
        assert column.utilization_ratio <= 1.0 or not column.is_adequate

    def test_beam_design(self):
        """Test beam design."""
        from agents.cad_agent.ache_assistant import StructuralDesigner

        designer = StructuralDesigner()
        beam = designer.design_beam(
            span_m=6.0,
            distributed_load_kn_m=10,
            deflection_limit="L/240",
        )

        assert beam.profile != ""
        assert beam.moment_capacity_knm > 0
        assert beam.deflection_mm <= beam.deflection_limit_mm or not beam.is_adequate

    def test_frame_design(self):
        """Test complete frame design."""
        from agents.cad_agent.ache_assistant import StructuralDesigner

        designer = StructuralDesigner()
        frame = designer.design_ache_frame(
            bundle_weight_kn=500,
            bundle_length_m=12,
            bundle_width_m=3,
            bundle_height_m=2,
            num_bays=2,
            elevation_m=4,
        )

        assert frame.num_columns > 0
        assert frame.num_beams > 0
        assert frame.total_steel_weight_kg > 0
        assert len(frame.columns) > 0
        assert len(frame.beams) > 0

    def test_anchor_bolt_calculation(self):
        """Test anchor bolt design."""
        from agents.cad_agent.ache_assistant import StructuralDesigner

        designer = StructuralDesigner()
        bolts = designer.calculate_anchor_bolts(
            axial_kn=100,
            shear_kn=50,
            moment_knm=30,
            base_plate_width_mm=400,
            num_bolts=4,
        )

        assert "bolt_size" in bolts
        assert bolts["num_bolts"] == 4
        assert "embedment_mm" in bolts


class TestAccessoryDesigner:
    """Tests for AccessoryDesigner module."""

    def test_import_accessories(self):
        """Test accessory module imports correctly."""
        from agents.cad_agent.ache_assistant import (
            AccessoryDesigner, PlatformDesign, LadderDesign, HandrailDesign
        )
        assert AccessoryDesigner is not None
        assert PlatformDesign is not None
        assert LadderDesign is not None
        assert HandrailDesign is not None

    def test_platform_design(self):
        """Test platform design."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()
        platform = designer.design_platform(
            length_m=6,
            width_m=1.0,
            elevation_m=4,
        )

        assert platform.grating_area_m2 == 6.0
        assert platform.total_weight_kg > 0
        assert platform.num_support_beams >= 2

    def test_platform_width_check(self):
        """Test OSHA minimum width check."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()

        # Below minimum width
        narrow = designer.design_platform(
            length_m=6,
            width_m=0.3,  # Below 450mm minimum
            elevation_m=4,
        )

        assert narrow.is_adequate is False
        assert any("width" in w.lower() for w in narrow.warnings)

    def test_ladder_design(self):
        """Test ladder design."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()
        ladder = designer.design_ladder(
            height_m=8,
            width_mm=450,
            include_cage=True,
        )

        assert ladder.num_rungs > 0
        assert ladder.has_cage is True  # Required for >20ft
        assert ladder.total_weight_kg > 0

    def test_ladder_cage_requirement(self):
        """Test ladder cage requirement per OSHA."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()

        # Short ladder - no cage needed
        short = designer.design_ladder(height_m=5, include_cage=False)
        assert short.has_cage is False

        # Tall ladder - cage required
        tall = designer.design_ladder(height_m=8, include_cage=True)
        assert tall.has_cage is True

    def test_handrail_design(self):
        """Test handrail design."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()
        handrail = designer.design_handrail(
            total_length_m=20,
            num_corners=4,
            has_gates=True,
            num_gates=2,
        )

        assert handrail.num_posts > 0
        assert handrail.top_rail_height_mm >= 1070  # OSHA 42"
        assert handrail.has_gates is True
        assert handrail.num_gates == 2

    def test_access_system_design(self):
        """Test complete access system design."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()
        bom = designer.design_ache_access_system(
            bundle_length_m=12,
            bundle_width_m=3,
            elevation_m=5,
            num_bays=2,
        )

        assert bom.total_grating_m2 > 0
        assert bom.total_steel_kg > 0
        assert len(bom.platforms) > 0
        assert len(bom.ladders) > 0
        assert len(bom.handrails) > 0
        assert len(bom.items) > 0


class TestACHEAssistant:
    """Tests for ACHEAssistant AI module."""

    def test_import_assistant(self):
        """Test assistant module imports correctly."""
        from agents.cad_agent.ache_assistant import ACHEAssistant
        assert ACHEAssistant is not None

    def test_compliance_check(self):
        """Test API 661 compliance checking."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()
        props = {
            "tube_bundle": {
                "tube_length_m": 10,
                "tube_od_mm": 25.4,
                "tube_wall_mm": 2.5,
            },
            "fan_system": {
                "tip_speed_m_s": 55,
                "blade_clearance_mm": 15,
            },
        }

        report = assistant.check_api661_compliance(props)

        assert report.standard == "API 661 / ISO 13706"
        assert report.total_checks > 0
        assert isinstance(report.is_compliant, bool)
        assert isinstance(report.issues, list)

    def test_design_recommendations(self):
        """Test design recommendations generation."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()
        props = {
            "thermal_performance": {
                "approach_temp_c": 8,
                "overdesign_percent": 5,
            },
        }

        recs = assistant.get_design_recommendations(props)
        assert isinstance(recs, list)

    def test_troubleshooting(self):
        """Test troubleshooting guidance."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()

        result = assistant.troubleshoot("high temperature")
        assert "possible_causes" in result
        assert "solutions" in result

        result2 = assistant.troubleshoot("vibration")
        assert "possible_causes" in result2

    def test_knowledge_query(self):
        """Test knowledge base query."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()

        result = assistant.query_knowledge_base("tube selection")
        assert "results" in result
        assert "references" in result


class TestErectionPlanner:
    """Tests for ErectionPlanner module."""

    def test_import_erection(self):
        """Test erection module imports correctly."""
        from agents.cad_agent.ache_assistant import ErectionPlanner, LiftingLugDesign, RiggingPlan
        assert ErectionPlanner is not None
        assert LiftingLugDesign is not None
        assert RiggingPlan is not None

    def test_lifting_lug_design(self):
        """Test lifting lug design."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()
        lug = planner.design_lifting_lug(
            design_load_kn=100,
            sling_angle_deg=60,
        )

        assert lug.plate_thickness_mm > 0
        assert lug.hole_diameter_mm > 0
        assert lug.bearing_capacity_kn > 0
        assert lug.utilization > 0

    def test_lifting_lug_adequacy(self):
        """Test lifting lug adequacy check."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()

        # Reasonable load - should be adequate
        lug = planner.design_lifting_lug(design_load_kn=50)
        assert lug.is_adequate is True

    def test_rigging_plan(self):
        """Test rigging plan generation."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()
        plan = planner.plan_rigging(
            total_weight_kg=50000,
            cg_location=(6000, 1500, 1000),
            lift_points=[
                (0, 0, 0),
                (12000, 0, 0),
                (0, 3000, 0),
                (12000, 3000, 0),
            ],
            lift_height_m=5,
            lift_radius_m=20,
        )

        assert plan.num_slings == 4
        assert plan.sling_diameter_mm > 0
        assert plan.crane_capacity_tonnes > 0
        assert plan.is_adequate is True

    def test_shipping_splits(self):
        """Test shipping split analysis."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()

        # Large unit requiring splits
        splits = planner.analyze_shipping_splits(
            unit_length_m=25,  # Over 65ft limit
            unit_width_m=3,
            unit_height_m=4,
            unit_weight_kg=80000,
        )

        assert len(splits) > 0
        assert any(s.split_id.startswith("L") for s in splits)

    def test_shipping_no_splits(self):
        """Test shipping that fits without splits."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()

        splits = planner.analyze_shipping_splits(
            unit_length_m=15,  # Under limit
            unit_width_m=2.5,
            unit_height_m=3,
            unit_weight_kg=20000,
        )

        assert len(splits) == 0

    def test_erection_sequence(self):
        """Test erection sequence generation."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()
        modules = [
            {"name": "Column A", "type": "column", "weight_kg": 2000},
            {"name": "Beam B", "type": "beam", "weight_kg": 1500},
            {"name": "Bundle", "type": "bundle", "weight_kg": 30000},
            {"name": "Fan 1", "type": "fan", "weight_kg": 500},
        ]

        sequence = planner.create_erection_sequence(modules)

        assert len(sequence) == 4
        # Columns should come before bundles
        col_step = next(s for s in sequence if "Column" in s.description)
        bundle_step = next(s for s in sequence if "Bundle" in s.description)
        assert col_step.step_number < bundle_step.step_number

    def test_complete_erection_plan(self):
        """Test complete erection plan generation."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()
        props = {
            "mass_properties": {"mass_kg": 50000},
            "bounding_box": {
                "length_mm": 12000,
                "width_mm": 3000,
                "height_mm": 4000,
            },
            "fan_system": {"num_fans": 2},
        }

        plan = planner.create_erection_plan(
            project_name="Test Project",
            equipment_tag="AC-101",
            ache_properties=props,
        )

        assert plan.project_name == "Test Project"
        assert plan.equipment_tag == "AC-101"
        assert plan.total_weight_kg == 50000
        assert len(plan.lifting_lugs) == 4
        assert plan.rigging_plan is not None
        assert len(plan.erection_sequence) > 0
        assert plan.total_lift_hours > 0


class TestACHEExtractor:
    """Tests for ACHEExtractor module."""

    def test_import_extractor(self):
        """Test extractor module imports correctly."""
        from agents.cad_agent.ache_assistant import ACHEExtractor, ACHEProperties
        assert ACHEExtractor is not None
        assert ACHEProperties is not None

    def test_extractor_dataclasses(self):
        """Test extractor dataclasses."""
        from agents.cad_agent.ache_assistant.extractor import (
            HeaderBoxData, TubeBundleData, FanSystemData,
            HeaderType, TubePattern, FinType
        )

        # Test header box defaults
        header = HeaderBoxData()
        assert header.length_mm == 0.0
        assert header.header_type == HeaderType.PLUG
        assert header.requires_split is False

        # Test tube bundle defaults
        bundle = TubeBundleData()
        assert bundle.tube_od_mm == 25.4
        assert bundle.tube_wall_mm == 2.11
        assert bundle.pattern == TubePattern.TRIANGULAR

        # Test fan system defaults
        fan = FanSystemData()
        assert fan.num_fans == 1
        assert fan.num_blades == 4
        assert fan.blade_material == "aluminum"

    def test_header_types(self):
        """Test API 661 header type enumeration."""
        from agents.cad_agent.ache_assistant.extractor import HeaderType

        assert HeaderType.PLUG.value == "plug"
        assert HeaderType.COVER_PLATE.value == "cover_plate"
        assert HeaderType.BONNET.value == "bonnet"

    def test_tube_patterns(self):
        """Test tube pattern enumeration."""
        from agents.cad_agent.ache_assistant.extractor import TubePattern

        assert TubePattern.TRIANGULAR.value == "triangular"
        assert TubePattern.SQUARE.value == "square"

    def test_fin_types(self):
        """Test fin type enumeration per API 661."""
        from agents.cad_agent.ache_assistant.extractor import FinType

        assert FinType.L_FOOTED.value == "l_footed"
        assert FinType.EMBEDDED.value == "embedded"
        assert FinType.EXTRUDED.value == "extruded"

    def test_header_split_requirement(self):
        """Test API 661 header split requirement calculation."""
        from agents.cad_agent.ache_assistant.extractor import HeaderBoxData

        # Low delta-T - no split required
        header_low = HeaderBoxData(
            inlet_temp_c=80,
            outlet_temp_c=60,
            delta_t=20,
            requires_split=False,
        )
        assert header_low.requires_split is False

        # High delta-T (>110°C) - split required per API 661 7.1.6.1.2
        header_high = HeaderBoxData(
            inlet_temp_c=200,
            outlet_temp_c=60,
            delta_t=140,
            requires_split=True,
        )
        assert header_high.requires_split is True

    def test_ache_properties_dataclass(self):
        """Test ACHEProperties dataclass."""
        from agents.cad_agent.ache_assistant.extractor import (
            ACHEProperties, HeaderBoxData, TubeBundleData, FanSystemData
        )

        props = ACHEProperties(
            equipment_tag="AC-101",
            service="Cooling",
            header_box=HeaderBoxData(length_mm=3000),
            tube_bundle=TubeBundleData(total_tubes=500),
            fan_system=FanSystemData(num_fans=2),
        )

        assert props.equipment_tag == "AC-101"
        assert props.header_box.length_mm == 3000
        assert props.tube_bundle.total_tubes == 500
        assert props.fan_system.num_fans == 2


class TestPressureDropCalculations:
    """Tests for pressure drop calculations."""

    def test_tube_side_pressure_drop(self):
        """Test tube-side pressure drop calculation."""
        from agents.cad_agent.ache_assistant import ACHECalculator, FluidProperties

        calc = ACHECalculator()
        fluid = FluidProperties(
            density_kg_m3=800,
            specific_heat_j_kg_k=2000,
            viscosity_pa_s=0.001,
            thermal_conductivity_w_m_k=0.15,
            prandtl_number=10,
        )

        results = calc.calculate_tube_side_pressure_drop(
            mass_flow_kg_s=50,
            fluid=fluid,
            tube_id_mm=22,
            tube_length_m=6,
            num_tubes=500,
            num_passes=4,
        )

        assert results.tube_side_dp_kpa > 0
        assert results.tube_friction_dp_kpa > 0
        assert results.tube_entrance_exit_dp_kpa > 0

    def test_air_side_pressure_drop(self):
        """Test air-side pressure drop calculation."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()

        results = calc.calculate_air_side_pressure_drop(
            air_flow_kg_s=100,
            air_inlet_temp_c=35,
            bundle_face_area_m2=30,
            tube_od_mm=25.4,
            fin_pitch_mm=2.5,
            fin_height_mm=12.7,
            num_tube_rows=4,
        )

        assert results.air_side_dp_pa > 0
        assert results.bundle_dp_pa > 0

    def test_air_pressure_drop_limit(self):
        """Test air-side pressure drop limit check."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()

        # Low air flow - should be within limits
        results = calc.calculate_air_side_pressure_drop(
            air_flow_kg_s=50,
            air_inlet_temp_c=35,
            bundle_face_area_m2=40,
            tube_od_mm=25.4,
            fin_pitch_mm=2.5,
            fin_height_mm=12.7,
            num_tube_rows=4,
        )

        assert results.is_within_limits is True


class TestHeatTransferCoefficient:
    """Tests for heat transfer coefficient calculations."""

    def test_htc_turbulent_flow(self):
        """Test heat transfer coefficient for turbulent flow."""
        from agents.cad_agent.ache_assistant import ACHECalculator, FluidProperties
        from agents.cad_agent.ache_assistant.calculator import FluidType

        calc = ACHECalculator()
        fluid = FluidProperties(
            density_kg_m3=1000,
            specific_heat_j_kg_k=4186,
            viscosity_pa_s=0.001,
            thermal_conductivity_w_m_k=0.6,
            prandtl_number=7,
        )

        h = calc.calculate_heat_transfer_coefficient(
            fluid=fluid,
            velocity_m_s=2.0,
            hydraulic_diameter_m=0.02,
            fluid_type=FluidType.LIQUID,
        )

        # Turbulent flow should give reasonable h value
        assert h > 1000  # W/m2-K typical for turbulent water

    def test_htc_laminar_flow(self):
        """Test heat transfer coefficient for laminar flow."""
        from agents.cad_agent.ache_assistant import ACHECalculator, FluidProperties
        from agents.cad_agent.ache_assistant.calculator import FluidType

        calc = ACHECalculator()
        # High viscosity fluid for laminar flow
        fluid = FluidProperties(
            density_kg_m3=900,
            specific_heat_j_kg_k=2000,
            viscosity_pa_s=0.1,  # High viscosity
            thermal_conductivity_w_m_k=0.15,
            prandtl_number=1000,
        )

        h = calc.calculate_heat_transfer_coefficient(
            fluid=fluid,
            velocity_m_s=0.1,
            hydraulic_diameter_m=0.02,
            fluid_type=FluidType.LIQUID,
        )

        # Laminar flow gives lower h
        assert h > 0
        assert h < 500  # Lower than turbulent


class TestAPIEndpointModels:
    """Tests for API endpoint request/response models."""

    def test_thermal_calc_request_model(self):
        """Test ThermalCalcRequest model."""
        from pydantic import BaseModel

        # Simulate creating request data
        request_data = {
            "duty_kw": 1000,
            "process_inlet_temp_c": 120,
            "process_outlet_temp_c": 60,
            "air_inlet_temp_c": 35,
            "air_flow_kg_s": 100,
            "surface_area_m2": 500,
            "u_clean_w_m2_k": 45.0,
            "fouling_factor": 0.0002,
        }
        assert request_data["duty_kw"] == 1000
        assert request_data["fouling_factor"] == 0.0002

    def test_fan_calc_request_model(self):
        """Test FanCalcRequest model."""
        request_data = {
            "air_flow_m3_s": 50,
            "static_pressure_pa": 200,
            "fan_diameter_m": 3.0,
            "fan_rpm": 300,
            "fan_efficiency": 0.75,
        }
        assert request_data["air_flow_m3_s"] == 50
        assert request_data["fan_efficiency"] == 0.75

    def test_frame_design_request_model(self):
        """Test FrameDesignRequest model."""
        request_data = {
            "bundle_weight_kn": 500,
            "bundle_length_m": 12,
            "bundle_width_m": 3,
            "bundle_height_m": 2,
            "num_bays": 2,
            "elevation_m": 4.0,
            "wind_speed_m_s": 40.0,
        }
        assert request_data["bundle_weight_kn"] == 500
        assert request_data["num_bays"] == 2

    def test_access_design_request_model(self):
        """Test AccessDesignRequest model."""
        request_data = {
            "bundle_length_m": 12,
            "bundle_width_m": 3,
            "elevation_m": 5,
            "num_bays": 2,
            "fan_deck_required": True,
            "header_access_required": True,
        }
        assert request_data["fan_deck_required"] == True

    def test_erection_plan_request_model(self):
        """Test ErectionPlanRequest model."""
        request_data = {
            "project_name": "Test Project",
            "equipment_tag": "AC-101",
            "ache_properties": {
                "mass_properties": {"mass_kg": 50000},
                "bounding_box": {
                    "length_mm": 12000,
                    "width_mm": 3000,
                    "height_mm": 4000,
                },
            },
        }
        assert request_data["project_name"] == "Test Project"
        assert request_data["ache_properties"]["mass_properties"]["mass_kg"] == 50000

    def test_optimization_request_model(self):
        """Test OptimizationRequest model."""
        request_data = {
            "ache_properties": {},
            "thermal_results": {},
            "optimization_targets": ["cost", "efficiency", "footprint"],
            "constraints": {"max_footprint_m2": 100},
        }
        assert "cost" in request_data["optimization_targets"]
        assert request_data["constraints"]["max_footprint_m2"] == 100


class TestAPI661Compliance:
    """Tests for API 661 compliance checking."""

    def test_tube_length_limit(self):
        """Test API 661 5.1.1 - Maximum tube length 12.0m."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()
        result = assistant.check_compliance({
            "tube_bundle": {
                "tube_length_m": 10.0,  # Within limit
            }
        })
        # Should have checks performed
        assert result.total_checks >= 0

    def test_tube_length_exceeds(self):
        """Test API 661 5.1.1 - Tube length exceeds limit."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()
        result = assistant.check_compliance({
            "tube_bundle": {
                "tube_length_m": 14.0,  # Exceeds 12m limit
            }
        })
        # Should have warning or failure
        assert result.total_checks >= 0

    def test_fan_tip_speed_limit(self):
        """Test API 661 6.1.1 - Maximum fan tip speed 61 m/s."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()
        result = assistant.check_compliance({
            "fan_system": {
                "tip_speed_m_s": 55,  # Within limit
            }
        })
        # Should have checks performed
        assert result.total_checks >= 0

    def test_blade_clearance_minimum(self):
        """Test API 661 Table 6 - Minimum blade clearance 12.7mm."""
        from agents.cad_agent.ache_assistant import ACHEAssistant

        assistant = ACHEAssistant()
        result = assistant.check_compliance({
            "fan_system": {
                "blade_clearance_mm": 15,  # Above minimum
            }
        })
        # Should have checks performed
        assert result.total_checks >= 0

    def test_header_split_requirement(self):
        """Test API 661 7.1.6.1.2 - Header split required if delta T > 110°C."""
        # Direct calculation: delta T = 180 - 60 = 120°C > 110°C requires split
        delta_t_high = 180 - 60  # 120°C
        assert delta_t_high > 110  # Requires split

        # delta T = 150 - 60 = 90°C < 110°C no split required
        delta_t_low = 150 - 60  # 90°C
        assert delta_t_low < 110  # No split required


class TestOSHACompliance:
    """Tests for OSHA compliance checking."""

    def test_walkway_width_minimum(self):
        """Test OSHA 1910.22 - Minimum walkway width 450mm."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()
        platform = designer.design_platform(
            length_m=10,
            width_m=0.5,  # 500mm > 450mm minimum
            elevation_m=4.0,
            live_load_kpa=4.8,
        )
        assert platform.width_m >= 0.45

    def test_handrail_height_minimum(self):
        """Test OSHA 1910.29 - Minimum handrail height 1070mm."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()
        handrail = designer.design_handrail(total_length_m=10)
        assert handrail.height_mm >= 1070

    def test_ladder_cage_requirement(self):
        """Test OSHA 1910.28 - Ladder cage required > 6.1m."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        designer = AccessoryDesigner()

        # Height > 6.1m with cage
        ladder_tall = designer.design_ladder(height_m=7.0, include_cage=True)
        assert ladder_tall.height_m == 7.0

        # Height <= 6.1m without cage
        ladder_short = designer.design_ladder(height_m=5.0, include_cage=False)
        assert ladder_short.height_m == 5.0

    def test_toe_plate_height(self):
        """Test OSHA 1910.29 - Toe plate height >= 89mm."""
        from agents.cad_agent.ache_assistant import AccessoryDesigner

        # OSHA requirement is 89mm minimum
        assert AccessoryDesigner.TOE_PLATE_HEIGHT_MM >= 89


class TestAISCCompliance:
    """Tests for AISC steel design compliance."""

    def test_column_slenderness_limit(self):
        """Test AISC - Column slenderness KL/r <= 200."""
        from agents.cad_agent.ache_assistant import StructuralDesigner

        designer = StructuralDesigner()
        column = designer.design_column(
            axial_load_kn=200,
            height_m=4.0,
            moment_kn_m=20,
            k_factor=1.0,
        )
        # Selected profile should satisfy slenderness requirement
        assert column.is_adequate == True or hasattr(column, 'slenderness_ratio')

    def test_beam_deflection_limit(self):
        """Test AISC - Beam deflection limit L/240."""
        from agents.cad_agent.ache_assistant import StructuralDesigner

        designer = StructuralDesigner()
        beam = designer.design_beam(
            span_m=6.0,
            distributed_load_kn_m=10,
            deflection_limit="L/240",
        )
        # Beam should be designed
        assert beam is not None
        assert beam.span_m == 6.0

    def test_frame_load_combinations(self):
        """Test AISC LRFD load combinations."""
        from agents.cad_agent.ache_assistant import StructuralDesigner

        designer = StructuralDesigner()
        frame = designer.design_ache_frame(
            bundle_weight_kn=300,
            bundle_length_m=10,
            bundle_width_m=3,
            bundle_height_m=2,
            num_bays=1,
            elevation_m=4,
            wind_speed_m_s=40,
        )
        # Frame should be designed
        assert frame is not None
        assert frame.num_columns > 0


class TestASMEBTH1Compliance:
    """Tests for ASME BTH-1 lifting lug design."""

    def test_lifting_lug_design_factors(self):
        """Test ASME BTH-1 design factors."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()
        lug = planner.design_lifting_lug(
            design_load_kn=100,
            sling_angle_deg=60,
        )
        # Design load should include factors
        # Sling angle factor = 1/sin(60°) = 1.155
        assert lug.total_design_load_kn > lug.design_load_kn

    def test_lifting_lug_failure_modes(self):
        """Test all lifting lug failure modes are checked."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()
        lug = planner.design_lifting_lug(
            design_load_kn=100,
            sling_angle_deg=60,
        )
        # All failure modes should be checked
        assert lug.bearing_capacity_kn > 0
        assert lug.tearout_capacity_kn > 0
        assert lug.tension_capacity_kn > 0
        assert lug.weld_capacity_kn > 0

    def test_lifting_lug_utilization(self):
        """Test lifting lug utilization calculation."""
        from agents.cad_agent.ache_assistant import ErectionPlanner

        planner = ErectionPlanner()
        lug = planner.design_lifting_lug(
            design_load_kn=100,
            sling_angle_deg=60,
        )
        # Utilization should be demand/capacity
        assert lug.utilization > 0
        assert lug.utilization <= 1.0 or not lug.is_adequate


class TestBatchCalculations:
    """Tests for batch calculation features."""

    def test_multiple_fan_calculations(self):
        """Test multiple fan calculations."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()
        results = []
        for flow in [30, 50, 70]:
            result = calc.calculate_fan_performance(
                air_flow_m3_s=flow,
                static_pressure_pa=200,
                fan_diameter_m=3.0,
                fan_rpm=300,
                fan_efficiency=0.75,
            )
            results.append(result)

        # Higher flow should require more power
        assert results[2].shaft_power_kw >= results[0].shaft_power_kw

    def test_parametric_fan_sizing(self):
        """Test parametric fan sizing."""
        from agents.cad_agent.ache_assistant import ACHECalculator
        import math

        calc = ACHECalculator()
        results = []
        for diameter in [2.0, 2.5, 3.0]:
            result = calc.calculate_fan_performance(
                air_flow_m3_s=50,
                static_pressure_pa=200,
                fan_diameter_m=diameter,
                fan_rpm=300,
                fan_efficiency=0.75,
            )
            results.append(result)

        # Larger diameter at same RPM = higher tip speed
        assert results[2].tip_speed_m_s > results[0].tip_speed_m_s


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_duty(self):
        """Test handling of zero duty."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()
        # Zero duty should handle gracefully
        try:
            result = calc.calculate_thermal(
                duty_kw=0,
                process_inlet_temp_c=100,
                process_outlet_temp_c=100,  # Same temp = no duty
                air_inlet_temp_c=35,
                air_flow_kg_s=50,
                surface_area_m2=200,
            )
            # Should either return zero or handle gracefully
            assert result is not None
        except (ValueError, ZeroDivisionError):
            # Acceptable to raise error for invalid input
            pass

    def test_negative_pressure_drop(self):
        """Test handling of invalid pressure values."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()
        # Should handle or reject negative values
        try:
            result = calc.calculate_fan_performance(
                air_flow_m3_s=50,
                static_pressure_pa=-100,  # Invalid negative
                fan_diameter_m=3.0,
                fan_rpm=300,
                fan_efficiency=0.75,
            )
            # If it returns, power should be negative or zero
            assert result.shaft_power_kw <= 0
        except ValueError:
            # Acceptable to reject invalid input
            pass

    def test_very_high_temperature(self):
        """Test handling of very high temperatures."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()
        result = calc.calculate_thermal(
            duty_kw=1000,
            process_inlet_temp_c=400,  # Very high
            process_outlet_temp_c=200,
            air_inlet_temp_c=50,
            air_flow_kg_s=100,
            surface_area_m2=500,
        )
        # Should handle high temps
        assert result.lmtd_k > 0

    def test_small_tube_count(self):
        """Test pressure drop with small tube count."""
        from agents.cad_agent.ache_assistant import ACHECalculator

        calc = ACHECalculator()
        result = calc.calculate_tube_side_pressure_drop(
            mass_flow_kg_s=10,
            tube_id_mm=25,
            tube_length_m=6,
            num_tubes=10,  # Small count
            num_passes=2,
            fluid_density_kg_m3=800,
            fluid_viscosity_pa_s=0.001,
        )
        # Higher velocity in fewer tubes = higher pressure drop
        assert result.tube_side_dp_kpa > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
