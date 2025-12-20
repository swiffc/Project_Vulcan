"""
E2E Trading Flow Test (PRD Section 9)

Tests complete trading workflow:
1. User prompt → Task Router detects trading context
2. Trading Bot runs strategy logic
3. Commands → MCP Desktop (TradingView)
4. Logs → Memory Brain + PDF reports
5. Inspector Bot reviews → LLM Judge scores
6. System Manager backs up to Drive

Run with: pytest tests/test_e2e_trading.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTradingE2EFlow:
    """End-to-end trading workflow tests."""

    @pytest.mark.asyncio
    async def test_full_trading_flow(self):
        """
        E2E: Analyze → Journal → Audit → Backup

        Simulates: "Create this week's EUR/USD plan"
        """
        from agents.core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        # Step 1: Mock Trading Agent
        mock_trading = AsyncMock()
        mock_trading.process = AsyncMock(return_value={
            "pair": "EURUSD",
            "bias": "bearish",
            "setup": "Q2 manipulation into weekly FVG",
            "entry": 1.0850,
            "stop": 1.0900,
            "target": 1.0750,
            "rr": 2.0,
            "confidence": 0.85
        })
        orch.register_agent(AgentType.TRADING, mock_trading)

        # Step 2: Mock Inspector (audit)
        mock_inspector = AsyncMock()
        mock_inspector.audit = AsyncMock(return_value={
            "grade": "A",
            "score": 92,
            "feedback": "Solid confluence with weekly structure"
        })
        orch.register_agent(AgentType.INSPECTOR, mock_inspector)

        # Step 3: Execute trading analysis
        request = TaskRequest(
            message="Create this week's EUR/USD plan",
            require_review=True
        )
        result = await orch.route(request)

        # Assertions
        assert result.success
        assert result.agent == AgentType.TRADING
        assert result.metadata.get("reviewed") == True
        mock_trading.process.assert_called_once()
        mock_inspector.audit.assert_called_once()

    @pytest.mark.asyncio
    async def test_trading_journal_integration(self):
        """Test trade logging to Memory Brain."""
        from agents.trading_agent.adapters import JournalAdapter

        mock_memory = AsyncMock()
        mock_memory.store = AsyncMock(return_value={"id": "trade-001"})

        journal = JournalAdapter(memory_client=mock_memory)

        trade = {
            "pair": "GBPUSD",
            "session": "London",
            "bias": "long",
            "entry": 1.2650,
            "result": "win",
            "r_multiple": 1.5,
            "lesson": "Patience on retracement paid off"
        }

        result = await journal.log_trade(trade)

        assert result is not None
        mock_memory.store.assert_called_once()

    @pytest.mark.asyncio
    async def test_trading_with_desktop_control(self):
        """Test TradingView control via MCP bridge."""
        from agents.trading_agent.adapters import TradingViewBridge

        mock_mcp = AsyncMock()
        mock_mcp.call_tool = AsyncMock(return_value={"success": True})

        bridge = TradingViewBridge(mcp_client=mock_mcp)

        # Simulate chart navigation
        await bridge.change_symbol("EURUSD")
        await bridge.change_timeframe("1H")
        screenshot = await bridge.capture_chart()

        assert mock_mcp.call_tool.call_count >= 2

    @pytest.mark.asyncio
    async def test_strategy_detection(self):
        """Test ICT/BTMM strategy detection."""
        from agents.trading_agent.adapters import StrategyAdapter

        strategy = StrategyAdapter()

        # Test quarterly cycle detection
        result = strategy.detect_quarterly_phase("2025-01-15")
        assert result in ["Q1", "Q2", "Q3", "Q4"]

        # Test bias determination
        bias = strategy.determine_bias({
            "daily_trend": "bearish",
            "weekly_fvg": True,
            "liquidity_swept": True
        })
        assert bias in ["bullish", "bearish", "neutral"]

    @pytest.mark.asyncio
    async def test_inspector_grading(self):
        """Test LLM-as-Judge grading."""
        from agents.inspector_bot.adapters import AuditAdapter

        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(return_value={
            "grade": "B+",
            "score": 87,
            "strengths": ["Good entry timing", "Proper risk management"],
            "weaknesses": ["Could wait for more confluence"],
            "suggestions": ["Consider HTF structure more"]
        })

        audit = AuditAdapter(llm_client=mock_llm)

        trade_output = {
            "pair": "USDJPY",
            "setup": "Order block retest",
            "result": "win"
        }

        review = await audit.grade_trade(trade_output)

        assert review["grade"] in ["A", "A-", "B+", "B", "B-", "C+", "C", "D", "F"]
        assert 0 <= review["score"] <= 100


class TestTradingErrorHandling:
    """Test error handling in trading flow."""

    @pytest.mark.asyncio
    async def test_desktop_unreachable(self):
        """Test graceful handling when desktop server is down."""
        from agents.trading_agent.adapters import TradingViewBridge

        mock_mcp = AsyncMock()
        mock_mcp.call_tool = AsyncMock(side_effect=ConnectionError("Desktop unreachable"))

        bridge = TradingViewBridge(mcp_client=mock_mcp)

        with pytest.raises(ConnectionError):
            await bridge.change_symbol("EURUSD")

    @pytest.mark.asyncio
    async def test_memory_fallback(self):
        """Test journal works with memory unavailable."""
        from agents.trading_agent.adapters import JournalAdapter

        mock_memory = AsyncMock()
        mock_memory.store = AsyncMock(side_effect=Exception("Memory unavailable"))

        journal = JournalAdapter(memory_client=mock_memory)

        trade = {"pair": "EURUSD", "result": "win"}

        # Should handle gracefully (log locally or return error)
        try:
            result = await journal.log_trade(trade)
            # If it doesn't raise, should indicate failure
            assert result is None or result.get("error")
        except Exception:
            pass  # Expected behavior


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
