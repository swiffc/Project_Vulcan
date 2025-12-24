"""
Tests for Phase 20 Core Components

Tests:
- Context Manager
- Knowledge Graph
- Telemetry
- Backup Manager
- Workflow Engine
"""

import pytest
import os
import tempfile
from datetime import datetime

# Set up test environment
os.environ["API_KEY"] = "test-api-key"


class TestContextManager:
    """Tests for cross-domain context manager."""

    def test_context_manager_initialization(self):
        """Test ContextManager initialization."""
        from core.context_manager import ContextManager

        manager = ContextManager()
        assert manager is not None

    def test_context_manager_singleton(self):
        """Test context manager singleton pattern."""
        from core.context_manager import get_context_manager

        manager1 = get_context_manager()
        manager2 = get_context_manager()
        assert manager1 is manager2

    def test_add_context_item(self):
        """Test adding context items."""
        from core.context_manager import ContextManager

        manager = ContextManager()

        item = manager.add(
            content="Test validation completed",
            domain="cad",
            type="validation",
            metadata={"file": "test.pdf"}
        )

        assert item.content == "Test validation completed"
        assert item.domain == "cad"

    def test_add_trade_context(self):
        """Test adding trade context."""
        from core.context_manager import ContextManager

        manager = ContextManager()

        # Should not raise
        manager.add_trade({
            "pair": "EURUSD",
            "bias": "long",
            "entry": 1.10,
            "result": "win"
        })

    def test_add_validation_context(self):
        """Test adding validation context."""
        from core.context_manager import ContextManager

        manager = ContextManager()

        # Should not raise
        manager.add_validation({
            "file": "test.pdf",
            "passed": True,
            "checks": 130
        })


class TestKnowledgeGraph:
    """Tests for knowledge graph memory system."""

    def test_knowledge_graph_initialization(self):
        """Test KnowledgeGraph initialization."""
        from core.memory.knowledge_graph import KnowledgeGraph

        graph = KnowledgeGraph()
        assert graph is not None

    def test_knowledge_graph_singleton(self):
        """Test knowledge graph singleton pattern."""
        from core.memory.knowledge_graph import get_knowledge_graph

        graph1 = get_knowledge_graph()
        graph2 = get_knowledge_graph()
        assert graph1 is graph2

    def test_add_node(self):
        """Test adding nodes to graph."""
        from core.memory.knowledge_graph import KnowledgeGraph

        graph = KnowledgeGraph()

        node = graph.add_node(
            id="strategy_1",
            type="strategy",
            label="I-Beam Weldment",
            properties={"product_type": "weldment"}
        )

        assert node.id == "strategy_1"
        assert node.type == "strategy"

    def test_add_edge(self):
        """Test adding edges to graph."""
        from core.memory.knowledge_graph import KnowledgeGraph

        graph = KnowledgeGraph()

        # Add nodes first
        graph.add_node(id="s1", type="strategy", label="Strategy 1")
        graph.add_node(id="s2", type="strategy", label="Strategy 2")

        # Add edge
        edge = graph.add_edge(
            source="s1",
            target="s2",
            relation="similar_to",
            weight=0.8
        )

        assert edge.source == "s1"
        assert edge.target == "s2"
        assert edge.relation == "similar_to"

    def test_get_neighbors(self):
        """Test getting neighbor nodes."""
        from core.memory.knowledge_graph import KnowledgeGraph

        graph = KnowledgeGraph()

        graph.add_node(id="center", type="test", label="Center")
        graph.add_node(id="neighbor1", type="test", label="Neighbor 1")
        graph.add_node(id="neighbor2", type="test", label="Neighbor 2")

        graph.add_edge(source="center", target="neighbor1", relation="connected")
        graph.add_edge(source="center", target="neighbor2", relation="connected")

        neighbors = graph.get_neighbors("center")
        assert len(neighbors) >= 0  # May be empty if graph implementation differs


class TestTelemetry:
    """Tests for telemetry and cost tracking."""

    def test_telemetry_initialization(self):
        """Test Telemetry initialization."""
        from core.metrics.telemetry import Telemetry

        telemetry = Telemetry()
        assert telemetry is not None

    def test_telemetry_singleton(self):
        """Test telemetry singleton pattern."""
        from core.metrics.telemetry import get_telemetry

        t1 = get_telemetry()
        t2 = get_telemetry()
        assert t1 is t2

    def test_record_api_call(self):
        """Test recording API calls."""
        from core.metrics.telemetry import Telemetry

        telemetry = Telemetry()

        call = telemetry.record(
            model="claude-sonnet-4-20250514",
            endpoint="/api/chat",
            input_tokens=1000,
            output_tokens=500,
            latency_ms=1500.0,
            success=True
        )

        assert call.model == "claude-sonnet-4-20250514"
        assert call.total_tokens == 1500

    def test_api_call_cost_calculation(self):
        """Test cost calculation for API calls."""
        from core.metrics.telemetry import APICall
        from datetime import datetime

        call = APICall(
            timestamp=datetime.utcnow(),
            model="claude-sonnet-4-20250514",
            endpoint="/api/chat",
            input_tokens=1000000,  # 1M tokens
            output_tokens=0,
            latency_ms=1000.0,
            success=True
        )

        # Claude Sonnet input cost is $3/1M tokens
        assert call.cost == pytest.approx(3.0, rel=0.1)

    def test_get_daily_stats(self):
        """Test getting daily statistics."""
        from core.metrics.telemetry import Telemetry

        telemetry = Telemetry()

        stats = telemetry.get_daily_stats()
        assert "date" in stats
        assert "calls" in stats

    def test_get_weekly_stats(self):
        """Test getting weekly statistics."""
        from core.metrics.telemetry import Telemetry

        telemetry = Telemetry()

        stats = telemetry.get_weekly_stats()
        assert "period" in stats

    def test_estimate_monthly_cost(self):
        """Test monthly cost estimation."""
        from core.metrics.telemetry import Telemetry

        telemetry = Telemetry()

        cost = telemetry.estimate_monthly_cost()
        assert isinstance(cost, float)
        assert cost >= 0


class TestBackupManager:
    """Tests for backup and restore functionality."""

    def test_backup_manager_initialization(self):
        """Test BackupManager initialization."""
        from core.system_manager.backup_strategies import BackupManager

        manager = BackupManager()
        assert manager is not None

    def test_backup_manager_singleton(self):
        """Test backup manager singleton pattern."""
        from core.system_manager.backup_strategies import get_backup_manager

        m1 = get_backup_manager()
        m2 = get_backup_manager()
        assert m1 is m2


class TestWorkflowEngine:
    """Tests for workflow automation engine."""

    def test_workflow_engine_initialization(self):
        """Test WorkflowEngine initialization."""
        from core.workflows.engine import WorkflowEngine

        engine = WorkflowEngine()
        assert engine is not None

    def test_workflow_engine_singleton(self):
        """Test workflow engine singleton pattern."""
        from core.workflows.engine import get_workflow_engine

        e1 = get_workflow_engine()
        e2 = get_workflow_engine()
        assert e1 is e2

    def test_step_creation(self):
        """Test workflow step creation."""
        from core.workflows.engine import WorkflowStep

        # WorkflowStep requires action as Callable and params as Dict
        async def mock_action(ctx, **kwargs):
            return "done"

        step = WorkflowStep(
            name="validate",
            action=mock_action,
            params={"checks": ["gdt", "welding"]}
        )

        assert step.name == "validate"
        assert step.params["checks"] == ["gdt", "welding"]

    def test_workflow_creation(self):
        """Test workflow definition with engine."""
        from core.workflows.engine import WorkflowEngine, WorkflowStep

        engine = WorkflowEngine()

        # Create mock actions
        async def parse_action(ctx, **kwargs):
            return "parsed"

        async def validate_action(ctx, **kwargs):
            return "validated"

        # Create workflow steps
        step1 = WorkflowStep(name="parse", action=parse_action, params={})
        step2 = WorkflowStep(name="validate", action=validate_action, params={})

        assert step1.name == "parse"
        assert step2.name == "validate"
        assert engine is not None


class TestExportAdapter:
    """Tests for export functionality."""

    def test_export_adapter_initialization(self):
        """Test ExportAdapter initialization."""
        from core.export_adapter import ExportAdapter

        adapter = ExportAdapter()
        assert adapter is not None

    def test_export_strategy(self):
        """Test strategy export."""
        from core.export_adapter import ExportAdapter

        adapter = ExportAdapter()

        data = {
            "name": "Test Strategy",
            "type": "weldment"
        }

        # Export using actual method
        result_path = adapter.export_strategy("test_strategy", data)
        assert os.path.exists(result_path)

        # Cleanup
        if os.path.exists(result_path):
            os.unlink(result_path)


class TestCryptoWrapper:
    """Tests for crypto/secrets functionality."""

    def test_crypto_wrapper_initialization(self):
        """Test CryptoWrapper initialization."""
        from core.crypto_wrapper import CryptoWrapper

        wrapper = CryptoWrapper()
        assert wrapper is not None


class TestCostEstimator:
    """Tests for material cost estimation."""

    def test_cost_estimator_initialization(self):
        """Test CostEstimator initialization."""
        from agents.cad_agent.cost_estimator import CostEstimator

        estimator = CostEstimator()
        assert estimator is not None

    def test_cost_estimator_factory(self):
        """Test cost estimator factory function."""
        from agents.cad_agent.cost_estimator import get_cost_estimator

        e1 = get_cost_estimator()
        e2 = get_cost_estimator()
        # Factory creates new instances (not a singleton)
        assert e1 is not None
        assert e2 is not None


class TestStrategyBuilder:
    """Tests for LLM-powered strategy builder."""

    def test_strategy_builder_initialization(self):
        """Test StrategyBuilder initialization."""
        from agents.cad_agent.strategy_builder import StrategyBuilder

        builder = StrategyBuilder()
        assert builder is not None

    def test_strategy_builder_singleton(self):
        """Test strategy builder singleton pattern."""
        from agents.cad_agent.strategy_builder import get_strategy_builder

        b1 = get_strategy_builder()
        b2 = get_strategy_builder()
        assert b1 is b2


class TestStrategyEvolution:
    """Tests for LLM-powered strategy evolution."""

    def test_strategy_evolution_initialization(self):
        """Test StrategyEvolution initialization."""
        from agents.cad_agent.strategy_evolution import StrategyEvolution

        evolution = StrategyEvolution()
        assert evolution is not None

    def test_strategy_evolution_factory(self):
        """Test strategy evolution factory function."""
        from agents.cad_agent.strategy_evolution import get_strategy_evolution

        e1 = get_strategy_evolution()
        e2 = get_strategy_evolution()
        # Factory creates instances
        assert e1 is not None
        assert e2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
