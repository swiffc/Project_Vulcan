"""
Trading Agent Adapters
Thin wrappers for trading functionality.
"""

from .strategy_adapter import StrategyAdapter
from .journal_adapter import JournalAdapter
from .tradingview_bridge import TradingViewBridge

__all__ = ["StrategyAdapter", "JournalAdapter", "TradingViewBridge"]
