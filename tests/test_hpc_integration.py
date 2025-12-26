"""
HPC Standards Integration Tests
================================
Tests for HPC standards validators integration.

Phase 26 Implementation
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestHPCValidatorsExist:
    """Test that HPC validators can be imported."""

    def test_hpc_mechanical_validator_import(self):
        """Test HPCMechanicalValidator can be imported."""
        from agents.cad_agent.validators import HPCMechanicalValidator
        assert HPCMechanicalValidator is not None

    def test_hpc_walkway_validator_import(self):
        """Test HPCWalkwayValidator can be imported."""
        from agents.cad_agent.validators import HPCWalkwayValidator
        assert HPCWalkwayValidator is not None

    def test_hpc_header_validator_import(self):
        """Test HPCHeaderValidator can be imported."""
        from agents.cad_agent.validators import HPCHeaderValidator
        assert HPCHeaderValidator is not None


class TestHPCMechanicalValidator:
    """Tests for HPC mechanical standards validator."""

    @pytest.fixture
    def validator(self):
        from agents.cad_agent.validators import HPCMechanicalValidator
        return HPCMechanicalValidator()

    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None

    def test_validate_vibration_switch_correct(self, validator):
        """Test vibration switch validation with correct mounting."""
        from agents.cad_agent.validators.hpc_mechanical_validator import MachineryMountData
        data = MachineryMountData(
            mount_type="forced_draft",
            has_vibration_switch=True,
            vibration_switch_location={"from_centerline_ft": 1.0, "from_top_in": 6.0}
        )
        result = validator.validate_vibration_switch(data)
        assert result.passed >= result.failed

    def test_validate_diagonal_brace_spacing_valid(self, validator):
        """Test diagonal brace spacing within valid range."""
        from agents.cad_agent.validators.hpc_mechanical_validator import MachineryMountData
        data = MachineryMountData(
            mount_type="induced_draft",
            diagonal_brace_spacing_in=3.25  # Valid: between 1" and 6.25"
        )
        result = validator.validate_diagonal_brace_spacing(data)
        assert result.passed >= result.failed


class TestHPCWalkwayValidator:
    """Tests for HPC walkway standards validator."""

    @pytest.fixture
    def validator(self):
        from agents.cad_agent.validators import HPCWalkwayValidator
        return HPCWalkwayValidator()

    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None

    def test_validate_ladder_rung_material_correct(self, validator):
        """Test ladder rung material validation with correct material."""
        from agents.cad_agent.validators.hpc_walkway_validator import WalkwayData
        data = WalkwayData(
            has_ladder=True,
            ladder_rung_material="#6 rebar"
        )
        result = validator.validate_ladder(data)
        assert result.passed >= result.failed

    def test_validate_toe_plate_spec_correct(self, validator):
        """Test toe plate specification validation."""
        from agents.cad_agent.validators.hpc_walkway_validator import WalkwayData
        data = WalkwayData(
            has_toe_plate=True,
            toe_plate_spec="PRL 4-1/2\" x 2\" x 1/4\" welded component"
        )
        result = validator.validate_toe_plate(data)
        assert result.passed >= result.failed


class TestHPCHeaderValidator:
    """Tests for HPC header design standards validator."""

    @pytest.fixture
    def validator(self):
        from agents.cad_agent.validators import HPCHeaderValidator
        return HPCHeaderValidator()

    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None

    def test_validate_nameplate_thickness_current(self, validator):
        """Test nameplate thickness with current standard."""
        from agents.cad_agent.validators.hpc_header_validator import HeaderData
        data = HeaderData(
            nameplate_thickness_in=0.105  # Current standard
        )
        result = validator.validate_nameplate_thickness(data)
        assert result.passed >= result.failed

    def test_validate_nameplate_thickness_previous(self, validator):
        """Test nameplate thickness with previous standard (should warn)."""
        from agents.cad_agent.validators.hpc_header_validator import HeaderData
        data = HeaderData(
            nameplate_thickness_in=0.125  # Previous standard
        )
        result = validator.validate_nameplate_thickness(data)
        # Should pass but may have warnings
        assert result.total_checks > 0


class TestOrchestratorHPCIntegration:
    """Test HPC validators integration in orchestrator."""

    def test_orchestrator_has_hpc_validators(self):
        """Test orchestrator initializes with HPC validators."""
        from agents.cad_agent.validators.orchestrator import ValidationOrchestrator
        orchestrator = ValidationOrchestrator()

        assert hasattr(orchestrator, 'hpc_mechanical_validator')
        assert hasattr(orchestrator, 'hpc_walkway_validator')
        assert hasattr(orchestrator, 'hpc_header_validator')

    def test_orchestrator_hpc_validators_initialized(self):
        """Test HPC validators are properly initialized."""
        from agents.cad_agent.validators.orchestrator import ValidationOrchestrator
        orchestrator = ValidationOrchestrator()

        # Should be initialized (not None)
        assert orchestrator.hpc_mechanical_validator is not None
        assert orchestrator.hpc_walkway_validator is not None
        assert orchestrator.hpc_header_validator is not None


class TestPDFEngineHPCIntegration:
    """Test HPC validators integration in PDF validation engine."""

    def test_pdf_engine_has_hpc_validators(self):
        """Test PDF engine initializes with HPC validators."""
        from agents.cad_agent.validators.pdf_validation_engine import PDFValidationEngine
        engine = PDFValidationEngine()

        assert hasattr(engine, 'hpc_mechanical')
        assert hasattr(engine, 'hpc_walkway')
        assert hasattr(engine, 'hpc_header')

    def test_pdf_engine_hpc_validators_initialized(self):
        """Test HPC validators are properly initialized in PDF engine."""
        from agents.cad_agent.validators.pdf_validation_engine import PDFValidationEngine
        engine = PDFValidationEngine()

        assert engine.hpc_mechanical is not None
        assert engine.hpc_walkway is not None
        assert engine.hpc_header is not None

    def test_pdf_validation_result_has_hpc_fields(self):
        """Test PDFValidationResult has HPC result fields."""
        from agents.cad_agent.validators.pdf_validation_engine import PDFValidationResult
        result = PDFValidationResult()

        assert hasattr(result, 'hpc_mechanical_results')
        assert hasattr(result, 'hpc_walkway_results')
        assert hasattr(result, 'hpc_header_results')


class TestHPCStandardsData:
    """Test HPC standards data availability."""

    def test_hpc_vibration_switch_standards(self):
        """Test vibration switch mounting standards are defined."""
        from agents.cad_agent.validators.hpc_mechanical_validator import HPC_VIBRATION_SWITCH_MOUNTING

        assert "distance_from_fan_centerline_ft" in HPC_VIBRATION_SWITCH_MOUNTING
        assert "distance_from_top_in" in HPC_VIBRATION_SWITCH_MOUNTING
        assert HPC_VIBRATION_SWITCH_MOUNTING["distance_from_fan_centerline_ft"] == 1.0
        assert HPC_VIBRATION_SWITCH_MOUNTING["distance_from_top_in"] == 6.0

    def test_hpc_diagonal_brace_spacing(self):
        """Test diagonal brace spacing standards are defined."""
        from agents.cad_agent.validators.hpc_mechanical_validator import HPC_DIAGONAL_BRACE_SPACING

        assert "min_in" in HPC_DIAGONAL_BRACE_SPACING
        assert "max_in" in HPC_DIAGONAL_BRACE_SPACING
        assert HPC_DIAGONAL_BRACE_SPACING["min_in"] == 1.0
        assert HPC_DIAGONAL_BRACE_SPACING["max_in"] == 6.25

    def test_hpc_ladder_rung_material(self):
        """Test ladder rung material standard is defined."""
        from agents.cad_agent.validators.hpc_walkway_validator import HPC_LADDER_RUNG_MATERIAL

        assert HPC_LADDER_RUNG_MATERIAL == "#6 rebar"

    def test_hpc_nameplate_thickness(self):
        """Test nameplate thickness standards are defined."""
        from agents.cad_agent.validators.hpc_header_validator import (
            HPC_NAMEPLATE_THICKNESS_CURRENT_IN,
            HPC_NAMEPLATE_THICKNESS_PREVIOUS_IN
        )

        assert HPC_NAMEPLATE_THICKNESS_CURRENT_IN == 0.105
        assert HPC_NAMEPLATE_THICKNESS_PREVIOUS_IN == 0.125


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
