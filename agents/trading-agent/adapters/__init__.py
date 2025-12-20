"""
Trading Agent Adapters
Thin wrappers for trading functionality.
"""

from .strategy_adapter import StrategyAdapter
from .journal_adapter import JournalAdapter

__all__ = ["StrategyAdapter", "JournalAdapter"]
