"""
Tests for Strategy Management System (Phase 20)

Tests:
- Strategy CRUD operations
- Strategy scoring
- Strategy performance tracking
- Strategy API endpoints
"""

import pytest
import os
from fastapi.testclient import TestClient

# Set up test environment
os.environ["API_KEY"] = "test-api-key"
os.environ["DATABASE_URL"] = "sqlite:///./test_vulcan.db"


class TestStrategyScoring:
    """Tests for strategy scoring formula."""

    def test_calculate_accuracy_score(self):
        """Test accuracy calculation (60% weight)."""
        from core.metrics.strategy_scoring import StrategyScorer

        scorer = StrategyScorer()

        # Mock performance data
        performance = [
            {"validation_passed": True},
            {"validation_passed": True},
            {"validation_passed": False},
            {"validation_passed": True},
            {"validation_passed": True},
        ]

        accuracy = scorer._calculate_accuracy(performance)
        assert accuracy == 80.0  # 4/5 = 80%

    def test_calculate_accuracy_empty(self):
        """Test accuracy with no data."""
        from core.metrics.strategy_scoring import StrategyScorer

        scorer = StrategyScorer()
        accuracy = scorer._calculate_accuracy([])
        assert accuracy == 0

    def test_calculate_speed_score_fast(self):
        """Test speed score for fast execution."""
        from core.metrics.strategy_scoring import StrategyScorer

        scorer = StrategyScorer()

        # Fast execution (< 10 seconds)
        performance = [
            {"execution_time": 5.0},
            {"execution_time": 8.0},
            {"execution_time": 7.0},
        ]

        speed = scorer._calculate_speed_score(performance)
        assert speed == 100  # < 10 seconds = 100

    def test_calculate_speed_score_slow(self):
        """Test speed score for slow execution."""
        from core.metrics.strategy_scoring import StrategyScorer

        scorer = StrategyScorer()

        # Slow execution (> 60 seconds)
        performance = [
            {"execution_time": 90.0},
            {"execution_time": 100.0},
        ]

        speed = scorer._calculate_speed_score(performance)
        assert speed < 50  # > 60 seconds = < 50

    def test_calculate_quality_score_perfect(self):
        """Test quality score with no errors."""
        from core.metrics.strategy_scoring import StrategyScorer

        scorer = StrategyScorer()

        performance = [
            {"errors_json": []},
            {"errors_json": []},
        ]

        quality = scorer._calculate_quality_score(performance)
        assert quality == 100  # No errors = 100

    def test_calculate_quality_score_with_errors(self):
        """Test quality score with errors."""
        from core.metrics.strategy_scoring import StrategyScorer

        scorer = StrategyScorer()

        performance = [
            {"errors_json": [{"type": "tolerance_error"}]},
            {"errors_json": [{"type": "gdt_error"}, {"type": "material_error"}]},
        ]

        quality = scorer._calculate_quality_score(performance)
        assert quality < 100  # Has errors = less than 100

    def test_count_error_types(self):
        """Test error type counting."""
        from core.metrics.strategy_scoring import StrategyScorer

        scorer = StrategyScorer()

        performance = [
            {"errors_json": [{"type": "tolerance"}, {"type": "gdt"}]},
            {"errors_json": [{"type": "tolerance"}]},
        ]

        counts = scorer._count_error_types(performance)
        assert counts["tolerance"] == 2
        assert counts["gdt"] == 1


class TestStrategyProductModels:
    """Tests for Digital Twin product models."""

    def test_product_type_enum(self):
        """Test ProductType enum values."""
        from core.strategies.product_models import ProductType

        assert ProductType.WELDMENT.value == "weldment"
        assert ProductType.SHEET_METAL.value == "sheet_metal"
        assert ProductType.MACHINING.value == "machining"
        assert ProductType.ASSEMBLY.value == "assembly"
        assert ProductType.SOLID.value == "solid"

    def test_material_spec_defaults(self):
        """Test MaterialSpec default values."""
        from core.strategies.product_models import MaterialSpec

        spec = MaterialSpec()
        assert spec.name == "AISI 304"  # Default material
        assert spec.grade is None
        assert spec.density == 7850.0

    def test_feature_dataclass(self):
        """Test Feature dataclass."""
        from core.strategies.product_models import Feature

        feature = Feature(
            name="hole_pattern", type="hole", parameters={"diameter": 0.5, "count": 4}
        )
        assert feature.name == "hole_pattern"
        assert feature.parameters["diameter"] == 0.5

    def test_base_product_creation(self):
        """Test BaseProduct creation."""
        from core.strategies.product_models import BaseProduct, ProductType

        product = BaseProduct(
            name="Test Weldment",
            product_type=ProductType.WELDMENT,
            description="A test weldment product",
        )
        assert product.name == "Test Weldment"
        assert product.product_type == ProductType.WELDMENT
        assert product.version == 1
        assert product.is_experimental is False


class TestStrategyTemplates:
    """Tests for strategy templates."""

    def test_ibeam_template_exists(self):
        """Test I-beam template file exists."""
        import json
        from pathlib import Path

        template_path = Path("core/strategies/templates/ibeam_weldment.json")
        assert template_path.exists()

        with open(template_path) as f:
            data = json.load(f)

        assert data["name"] == "I-Beam Weldment Frame"
        assert data["product_type"] == "weldment"

    def test_sheetmetal_template_exists(self):
        """Test sheet metal template file exists."""
        import json
        from pathlib import Path

        template_path = Path("core/strategies/templates/sheetmetal_enclosure.json")
        assert template_path.exists()

        with open(template_path) as f:
            data = json.load(f)

        assert data["product_type"] == "sheet_metal"

    def test_machined_template_exists(self):
        """Test machined adapter template file exists."""
        import json
        from pathlib import Path

        template_path = Path("core/strategies/templates/machined_adapter.json")
        assert template_path.exists()


class TestStrategyAPI:
    """Tests for Strategy API endpoints."""

    def test_list_strategies(self):
        """Test GET /api/strategies endpoint."""
        from core.api import app

        client = TestClient(app)
        response = client.get("/api/strategies", headers={"X-API-Key": "test-api-key"})
        assert response.status_code == 200
        assert "strategies" in response.json()
        assert "count" in response.json()

    def test_create_strategy(self):
        """Test POST /api/strategies endpoint."""
        from core.api import app

        client = TestClient(app)

        strategy_data = {
            "name": "Test Strategy",
            "product_type": "weldment",
            "schema_json": {"material": "SA-516-70", "features": []},
            "is_experimental": True,
        }

        response = client.post(
            "/api/strategies", json=strategy_data, headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_strategy_not_found(self):
        """Test GET /api/strategies/{id} for non-existent strategy."""
        from core.api import app

        client = TestClient(app)
        response = client.get(
            "/api/strategies/99999", headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 404

    def test_get_strategy_rankings(self):
        """Test GET /api/strategies/rankings endpoint."""
        from core.api import app

        client = TestClient(app)
        response = client.get(
            "/api/strategies/rankings", headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200
        assert "rankings" in response.json()


class TestFeedbackLoop:
    """Tests for autonomous feedback loop."""

    def test_feedback_loop_initialization(self):
        """Test FeedbackLoop class initialization."""
        from core.feedback_loop import FeedbackLoop

        loop = FeedbackLoop()
        assert loop is not None

    def test_feedback_loop_singleton(self):
        """Test feedback loop singleton pattern."""
        from core.feedback_loop import get_feedback_loop

        loop1 = get_feedback_loop()
        loop2 = get_feedback_loop()
        assert loop1 is loop2


class TestAuditLogger:
    """Tests for audit logging system."""

    def test_audit_logger_initialization(self):
        """Test AuditLogger class initialization."""
        from core.audit_logger import AuditLogger

        logger = AuditLogger()
        assert logger is not None

    def test_audit_logger_singleton(self):
        """Test audit logger singleton pattern."""
        from core.audit_logger import get_audit_logger

        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        assert logger1 is logger2

    def test_log_api_call(self):
        """Test logging API calls."""
        from core.audit_logger import get_audit_logger

        logger = get_audit_logger()
        # Should not raise
        logger.log_api_call("/api/test", "GET", "test_user", 200)

    def test_log_strategy_action(self):
        """Test logging strategy actions."""
        from core.audit_logger import get_audit_logger

        logger = get_audit_logger()
        # Should not raise
        logger.log_strategy_action("create", strategy_id=1, strategy_name="Test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
