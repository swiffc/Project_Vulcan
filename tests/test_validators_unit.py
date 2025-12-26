"""
Unit Tests for Phase 25 Validators
===================================
Comprehensive unit tests for all validator modules.

Run with: python -m pytest tests/test_validators_unit.py -v
"""

import pytest
import sys
from pathlib import Path

# Add validators to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "cad_agent"))

from validators.aisc_structural_validator import (
    AISCStructuralValidator, BeamData, ColumnData, ConnectionData,
    BasePlateData, ConnectionType
)
from validators.asme_b31_3_validator import (
    ASMEB313Validator, PipeDesignData, FlexibilityData, BranchConnectionData
)
from validators.api661_thermal_validator import (
    API661ThermalValidator, ThermalDesignData, HeaderDesignData, VibrationData
)
from validators.bom_exporter import BOMExporter, BOMItem, BOMMetadata
from validators.drawing_markup import DrawingMarkupGenerator, MarkupType, MarkupSeverity
from validators.report_generator import ReportGenerator, ReportLevel


class TestAISCStructuralValidator:
    """Test AISC structural steel validator."""

    def setup_method(self):
        self.validator = AISCStructuralValidator()

    def test_beam_valid_design(self):
        """Test valid beam design passes all checks."""
        beam = BeamData(
            shape="W16X77",
            span_ft=20,
            unbraced_length_ft=5,
            moment_kip_ft=100,
            shear_kips=30,
            material="A992"
        )
        result = self.validator.validate_beam(beam)
        assert result.valid
        assert result.passed >= 4
        assert "flexure" in result.calculations

    def test_beam_overstressed(self):
        """Test overstressed beam fails."""
        beam = BeamData(
            shape="W8X31",  # Small beam
            span_ft=30,
            unbraced_length_ft=30,
            moment_kip_ft=200,  # High moment
            shear_kips=50,
            material="A992"
        )
        result = self.validator.validate_beam(beam)
        assert not result.valid
        assert result.critical_failures > 0

    def test_column_valid_design(self):
        """Test valid column design."""
        column = ColumnData(
            shape="W14X68",
            height_ft=12,
            axial_load_kips=200,
            k_factor=1.0,
            material="A992"
        )
        result = self.validator.validate_column(column)
        assert result.valid
        assert result.passed >= 2
        assert "compression" in result.calculations

    def test_column_slenderness_limit(self):
        """Test column slenderness check."""
        column = ColumnData(
            shape="W8X31",  # Small column
            height_ft=40,  # Very tall
            axial_load_kips=50,
            k_factor=2.0,  # Cantilever
            material="A992"
        )
        result = self.validator.validate_column(column)
        # Should flag slenderness issue
        slenderness = result.calculations.get("slenderness", {})
        assert slenderness.get("governing", 0) > 0

    def test_bolted_connection(self):
        """Test bolted connection validation."""
        conn = ConnectionData(
            connection_type=ConnectionType.BOLTED_SHEAR,
            load_kips=30,
            bolt_diameter=0.75,
            bolt_grade="A325",
            num_bolts=4,
            plate_thickness=0.5,
            plate_material="A36"
        )
        result = self.validator.validate_connection(conn)
        assert result.total_checks >= 2
        assert "bolt_shear" in result.calculations

    def test_welded_connection(self):
        """Test welded connection validation."""
        conn = ConnectionData(
            connection_type=ConnectionType.WELDED_SHEAR,
            load_kips=20,
            weld_size=0.25,
            weld_length=12,
            electrode="E70XX",
            plate_thickness=0.5,
            plate_material="A36"
        )
        result = self.validator.validate_connection(conn)
        assert "weld" in result.calculations
        assert result.calculations["weld"]["capacity_per_inch_kips"] > 0

    def test_base_plate(self):
        """Test base plate validation."""
        bp = BasePlateData(
            plate_length=14,
            plate_width=14,
            plate_thickness=1.0,
            column_depth=8,
            column_bf=8,
            axial_load_kips=150,
            concrete_fc_psi=3000,
            material="A36",
            anchor_diameter=0.75,
            anchor_embedment=12
        )
        result = self.validator.validate_base_plate(bp)
        assert result.total_checks == 3
        assert "bearing" in result.calculations
        assert "plate_bending" in result.calculations


class TestASMEB313Validator:
    """Test ASME B31.3 piping validator."""

    def setup_method(self):
        self.validator = ASMEB313Validator()

    def test_pipe_design_valid(self):
        """Test valid pipe design."""
        pipe = PipeDesignData(
            nominal_size_in=4.0,
            pipe_od_in=4.5,
            wall_thickness_in=0.237,
            material="A106-B",
            pipe_type="seamless",
            design_pressure_psig=150,
            design_temp_f=300,
            corrosion_allowance_in=0.0625
        )
        result = self.validator.validate_pipe_design(pipe)
        assert result.passed >= 2
        assert "pressure_wall" in result.calculations
        assert "required_wall" in result.calculations

    def test_pipe_wall_inadequate(self):
        """Test inadequate pipe wall fails."""
        pipe = PipeDesignData(
            nominal_size_in=4.0,
            pipe_od_in=4.5,
            wall_thickness_in=0.1,  # Too thin
            material="A106-B",
            pipe_type="seamless",
            design_pressure_psig=500,  # High pressure
            design_temp_f=300,
            corrosion_allowance_in=0.0625
        )
        result = self.validator.validate_pipe_design(pipe)
        assert result.critical_failures > 0

    def test_flexibility_cold_line(self):
        """Test flexibility for cold piping."""
        flex = FlexibilityData(
            pipe_size_in=4.0,
            pipe_material="A106-B",
            design_temp_f=100,  # Near ambient
            ambient_temp_f=70,
            pipe_length_ft=50,
            num_direction_changes=2
        )
        result = self.validator.validate_flexibility(flex)
        assert result.passed >= 3
        assert result.calculations["thermal"]["expansion_in"] < 1.0

    def test_flexibility_hot_line(self):
        """Test flexibility for hot piping."""
        flex = FlexibilityData(
            pipe_size_in=6.0,
            pipe_material="A106-B",
            design_temp_f=600,  # Hot
            ambient_temp_f=70,
            pipe_length_ft=200,
            num_direction_changes=0,  # Straight run
            expansion_loop=False
        )
        result = self.validator.validate_flexibility(flex)
        # Should have expansion concerns
        assert result.calculations["thermal"]["expansion_in"] > 1.0

    def test_branch_reinforcement(self):
        """Test branch connection reinforcement."""
        branch = BranchConnectionData(
            header_od_in=8.625,
            header_wall_in=0.322,
            branch_od_in=4.5,
            branch_wall_in=0.237,
            design_pressure_psig=150,
            reinforcing_pad_thickness_in=0.25,
            weld_size_in=0.25
        )
        result = self.validator.validate_branch_reinforcement(branch)
        assert result.total_checks == 3
        assert "reinforcement" in result.calculations

    def test_support_spacing(self):
        """Test pipe support spacing."""
        result = self.validator.check_support_spacing(
            pipe_size_in=4.0,
            actual_spacing_ft=12,
            insulated=False
        )
        assert result.total_checks == 1
        # 4" pipe has 14 ft recommended, 12 ft should pass
        assert result.passed == 1


class TestAPI661ThermalValidator:
    """Test API 661 thermal validator."""

    def setup_method(self):
        self.validator = API661ThermalValidator()

    def test_thermal_design_valid(self):
        """Test valid thermal design."""
        data = ThermalDesignData(
            process_fluid="hydrocarbon_liquid",
            inlet_temp_f=200,
            outlet_temp_f=120,
            design_temp_f=250,
            design_pressure_psig=150,
            flow_rate_lb_hr=100000,
            tube_od_in=1.0,
            tube_wall_in=0.083,
            tube_length_ft=30,
            num_tubes=200,
            num_passes=4,
            tube_pitch_in=2.5,
            tube_material="carbon_steel"
        )
        result = self.validator.validate_thermal_design(data)
        assert result.total_checks >= 6
        assert "velocity" in result.calculations

    def test_tube_velocity_high(self):
        """Test high tube velocity detection."""
        data = ThermalDesignData(
            process_fluid="water",
            flow_rate_lb_hr=500000,  # High flow
            tube_od_in=0.75,
            tube_wall_in=0.065,
            num_tubes=50,  # Few tubes
            num_passes=2,
            density_lb_ft3=62.4
        )
        result = self.validator.validate_thermal_design(data)
        velocity = result.calculations.get("velocity", {})
        assert velocity.get("velocity_fps", 0) > 0

    def test_header_design(self):
        """Test header box design."""
        header = HeaderDesignData(
            length_in=120,
            width_in=8,
            depth_in=6,
            wall_thickness_in=0.5,
            material="carbon_steel",
            design_pressure_psig=150,
            num_plugs=200,
            plug_type="shoulder",
            nozzle_size_in=6
        )
        result = self.validator.validate_header_design(header)
        assert result.total_checks >= 3
        assert "header_wall" in result.calculations

    def test_vibration_analysis(self):
        """Test tube vibration analysis."""
        vib = VibrationData(
            tube_od_in=1.0,
            tube_wall_in=0.065,
            unsupported_span_in=48,
            tube_material="carbon_steel",
            crossflow_velocity_fps=20,
            fluid_density_lb_ft3=0.07
        )
        result = self.validator.validate_vibration(vib)
        assert result.total_checks >= 3
        assert "natural_freq" in result.calculations
        assert "vortex" in result.calculations


class TestBOMExporter:
    """Test BOM export functionality."""

    def setup_method(self):
        self.exporter = BOMExporter()
        self.exporter.set_metadata(BOMMetadata(
            assembly_number="ASSY-001",
            assembly_name="Test Assembly",
            revision="A"
        ))

    def test_add_items(self):
        """Test adding BOM items."""
        item = BOMItem(
            item_number=1,
            part_number="PART-001",
            description="Test Part",
            quantity=2,
            material="A36",
            weight_lbs=10.5,
            unit_cost=25.00
        )
        self.exporter.add_item(item)
        assert len(self.exporter.items) == 1

    def test_from_dict_list(self):
        """Test loading from dict list."""
        items = [
            {"part_number": "P001", "description": "Part 1", "qty": 1, "material": "Steel"},
            {"part_number": "P002", "description": "Part 2", "qty": 4, "material": "Aluminum"},
        ]
        self.exporter.from_dict_list(items)
        assert len(self.exporter.items) == 2

    def test_csv_export(self):
        """Test CSV export."""
        self.exporter.from_dict_list([
            {"part_number": "P001", "description": "Part 1", "qty": 2, "weight": 5.0, "cost": 10.00},
        ])
        result = self.exporter.export_csv()
        assert result.success
        assert result.format == "csv"
        assert result.size_bytes > 0
        assert b"P001" in result.content

    def test_excel_export(self):
        """Test Excel export."""
        self.exporter.from_dict_list([
            {"part_number": "P001", "description": "Part 1", "qty": 2, "material": "Steel"},
            {"part_number": "P002", "description": "Part 2", "qty": 1, "material": "Steel"},
        ])
        result = self.exporter.export_excel(include_charts=False)
        assert result.success
        assert result.format == "excel"
        assert result.size_bytes > 0

    def test_get_summary(self):
        """Test summary statistics."""
        self.exporter.from_dict_list([
            {"part_number": "P001", "qty": 2, "weight": 5.0, "cost": 10.00, "material": "Steel"},
            {"part_number": "P002", "qty": 3, "weight": 2.0, "cost": 5.00, "material": "Aluminum"},
        ])
        summary = self.exporter.get_summary()
        assert summary["total_line_items"] == 2
        assert summary["total_quantity"] == 5
        assert summary["total_weight_lbs"] == 16.0  # 2*5 + 3*2
        assert summary["total_cost"] == 35.0  # 2*10 + 3*5


class TestDrawingMarkup:
    """Test drawing markup generation."""

    def setup_method(self):
        self.generator = DrawingMarkupGenerator()
        self.generator.set_drawing_info("DWG-001", "A", 1100, 850)

    def test_add_markup(self):
        """Test adding markup items."""
        markup_id = self.generator.add_markup(
            markup_type=MarkupType.BALLOON,
            severity=MarkupSeverity.WARNING,
            x=100,
            y=100,
            message="Test issue"
        )
        assert markup_id == "M001"
        assert len(self.generator.markup.markups) == 1

    def test_add_from_issues(self):
        """Test adding from validation issues."""
        issues = [
            {"severity": "critical", "message": "Critical issue", "check_type": "test"},
            {"severity": "warning", "message": "Warning issue", "check_type": "test"},
        ]
        self.generator.add_from_validation_issues(issues)
        assert len(self.generator.markup.markups) == 2

    def test_generate_svg(self):
        """Test SVG generation."""
        self.generator.add_markup(
            MarkupType.BALLOON, MarkupSeverity.ERROR,
            x=200, y=150, message="Error here"
        )
        svg = self.generator.generate_svg()
        assert "<svg" in svg
        assert "DWG-001" in svg
        assert "Error here" not in svg  # Balloon only shows number

    def test_issue_table(self):
        """Test issue table generation."""
        self.generator.add_markup(
            MarkupType.BALLOON, MarkupSeverity.WARNING,
            x=100, y=100, message="Test", check_type="dimension"
        )
        table = self.generator.get_issue_table()
        assert len(table) == 1
        assert table[0]["check_type"] == "dimension"


class TestReportGenerator:
    """Test report generation."""

    def setup_method(self):
        self.generator = ReportGenerator()

    def test_add_results(self):
        """Test adding validator results."""
        self.generator.add_result("fabrication", {
            "total_checks": 10,
            "passed": 8,
            "failed": 1,
            "warnings": 1,
            "issues": []
        })
        assert "fabrication" in self.generator.results

    def test_generate_report(self):
        """Test report generation."""
        self.generator.add_result("test_validator", {
            "total_checks": 5,
            "passed": 4,
            "failed": 0,
            "warnings": 1,
            "issues": [
                {"severity": "warning", "message": "Minor issue", "check_type": "test"}
            ]
        })
        report = self.generator.generate_report(
            drawing_number="DWG-001",
            level=ReportLevel.STANDARD
        )
        assert report.total_checks == 5
        assert report.total_passed == 4
        assert report.overall_pass_rate == 80.0

    def test_export_json(self):
        """Test JSON export."""
        self.generator.add_result("validator", {"total_checks": 5, "passed": 5, "issues": []})
        self.generator.generate_report()
        json_str = self.generator.export_json()
        assert "overall_status" in json_str
        assert "statistics" in json_str

    def test_export_html(self):
        """Test HTML export."""
        self.generator.add_result("validator", {"total_checks": 5, "passed": 5, "issues": []})
        self.generator.generate_report()
        html = self.generator.export_html()
        assert "<html>" in html
        assert "Validation Report" in html

    def test_export_markdown(self):
        """Test Markdown export."""
        self.generator.add_result("validator", {"total_checks": 5, "passed": 5, "issues": []})
        self.generator.generate_report()
        md = self.generator.export_markdown()
        assert "# Validation Report" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
