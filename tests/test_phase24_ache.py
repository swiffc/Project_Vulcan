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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
