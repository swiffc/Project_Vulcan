"""
End-to-End Workflow Tests

Tests complete workflows through the orchestrator:
- Trading: Chat → Analyze → Journal
- CAD: Chat → Parse → Build
- Inspector: Audit → Report

Run with: pytest tests/test_workflows.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
import importlib.util

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def import_from_hyphenated(module_path, module_name):
    """Import module from folder with hyphens."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestOrchestratorRouting:
    """Test orchestrator agent routing."""

    def test_detect_trading_agent(self):
        """Trading keywords should route to trading agent."""
        from agents.core.orchestrator_adapter import OrchestratorAdapter, AgentType

        orch = OrchestratorAdapter()

        # Trading keywords
        assert orch.detect_agent("Analyze EURUSD for a setup") == AgentType.TRADING
        assert orch.detect_agent("What's the bias for GBP today?") == AgentType.TRADING
        assert orch.detect_agent("Show me ICT order blocks") == AgentType.TRADING
        assert orch.detect_agent("Log this trade in my journal") == AgentType.TRADING

    def test_detect_cad_agent(self):
        """CAD keywords should route to CAD agent."""
        from agents.core.orchestrator_adapter import OrchestratorAdapter, AgentType

        orch = OrchestratorAdapter()

        assert orch.detect_agent("Create a 3D model of a flange") == AgentType.CAD
        assert orch.detect_agent("Open SolidWorks and sketch a circle") == AgentType.CAD
        assert orch.detect_agent("Build assembly from this PDF") == AgentType.CAD
        assert orch.detect_agent("Apply ECN revision 5") == AgentType.CAD

    def test_detect_inspector_agent(self):
        """Inspector keywords should route to inspector."""
        from agents.core.orchestrator_adapter import OrchestratorAdapter, AgentType

        orch = OrchestratorAdapter()

        assert orch.detect_agent("Audit my trades this week") == AgentType.INSPECTOR
        assert orch.detect_agent("Generate performance report") == AgentType.INSPECTOR
        assert orch.detect_agent("Grade this setup") == AgentType.INSPECTOR

    def test_detect_system_agent(self):
        """System keywords should route to system manager."""
        from agents.core.orchestrator_adapter import OrchestratorAdapter, AgentType

        orch = OrchestratorAdapter()

        assert orch.detect_agent("Check system health") == AgentType.SYSTEM
        assert orch.detect_agent("Run backup now") == AgentType.SYSTEM
        assert orch.detect_agent("Show me uptime metrics") == AgentType.SYSTEM

    def test_detect_general_fallback(self):
        """Unknown queries should fall back to general."""
        from agents.core.orchestrator_adapter import OrchestratorAdapter, AgentType

        orch = OrchestratorAdapter()

        assert orch.detect_agent("What's the weather?") == AgentType.GENERAL
        assert orch.detect_agent("Hello") == AgentType.GENERAL
        assert orch.detect_agent("Tell me a joke") == AgentType.GENERAL


class TestTradingWorkflow:
    """Test trading agent workflow."""

    @pytest.mark.asyncio
    async def test_trading_analysis_flow(self):
        """Test: User asks for analysis → Strategy adapter processes."""
        from agents.core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        # Mock trading agent
        mock_trading = AsyncMock()
        mock_trading.process = AsyncMock(return_value={
            "bias": "bullish",
            "setup": "Q2 manipulation complete",
            "confidence": 0.8
        })
        orch.register_agent(AgentType.TRADING, mock_trading)

        # Execute workflow
        request = TaskRequest(message="Analyze EURUSD for ICT setup")
        result = await orch.route(request)

        assert result.success
        assert result.agent == AgentType.TRADING
        mock_trading.process.assert_called_once()

    @pytest.mark.asyncio
    async def test_trading_journal_flow(self):
        """Test: User logs trade → Journal adapter stores."""
        from agents.trading_agent.adapters import JournalAdapter

        # Mock memory client
        mock_memory = AsyncMock()
        mock_memory.store = AsyncMock(return_value=True)

        journal = JournalAdapter(memory_client=mock_memory)

        trade = {
            "pair": "EURUSD",
            "bias": "short",
            "result": "win",
            "r_multiple": 2.0,
            "lesson": "Waited for displacement"
        }

        result = await journal.log_trade(trade)
        assert result is not None


class TestCADWorkflow:
    """Test CAD agent workflow."""

    @pytest.mark.asyncio
    async def test_cad_pdf_to_part_flow(self):
        """Test: PDF upload → Parse → Build part."""
        from agents.core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        # Mock CAD agent
        mock_cad = AsyncMock()
        mock_cad.process = AsyncMock(return_value={
            "parts_created": ["Flange_01"],
            "status": "complete"
        })
        orch.register_agent(AgentType.CAD, mock_cad)

        request = TaskRequest(
            message="Build a flange from the uploaded PDF",
            context={"pdf_path": "/uploads/flange.pdf"}
        )
        result = await orch.route(request)

        assert result.success
        assert result.agent == AgentType.CAD


class TestInspectorWorkflow:
    """Test inspector workflow with Producer-Reviewer pattern."""

    @pytest.mark.asyncio
    async def test_audit_with_review(self):
        """Test: Task with require_review triggers inspector."""
        from agents.core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        # Mock trading agent (producer)
        mock_trading = AsyncMock()
        mock_trading.process = AsyncMock(return_value={"analysis": "bullish setup"})
        orch.register_agent(AgentType.TRADING, mock_trading)

        # Mock inspector (reviewer)
        mock_inspector = AsyncMock()
        mock_inspector.audit = AsyncMock(return_value={
            "grade": "B",
            "score": 85,
            "feedback": "Good analysis, consider more confluence"
        })
        orch.register_agent(AgentType.INSPECTOR, mock_inspector)

        request = TaskRequest(
            message="Analyze EURUSD setup",
            require_review=True
        )
        result = await orch.route(request)

        assert result.success
        assert result.metadata.get("reviewed") == True
        mock_inspector.audit.assert_called_once()


class TestHealthDashboard:
    """Test health dashboard endpoints."""

    def test_agent_status(self):
        """Test agent registration status."""
        from agents.core.orchestrator_adapter import OrchestratorAdapter, AgentType

        orch = OrchestratorAdapter()
        orch.register_agent(AgentType.TRADING, MagicMock())

        status = orch.get_agent_status()

        assert status["trading"] == "registered"
        assert status["cad"] == "not_registered"

    def test_task_history(self):
        """Test task history retrieval."""
        from agents.core.orchestrator_adapter import (
            OrchestratorAdapter, TaskResult, AgentType
        )

        orch = OrchestratorAdapter()

        # Add mock history
        orch.task_history = [
            TaskResult(AgentType.TRADING, True, "output1"),
            TaskResult(AgentType.CAD, False, None, error="timeout"),
        ]

        history = orch.get_task_history(limit=5)

        assert len(history) == 2
        assert history[0]["agent"] == "trading"
        assert history[1]["success"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
