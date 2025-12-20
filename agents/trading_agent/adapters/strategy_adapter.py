"""
Strategy Adapter
Thin wrapper around trading strategy logic.
Uses knowledge files from knowledge/ directory.

No external packages needed - pure Python logic.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger("trading.strategy")


class SessionPhase(Enum):
    Q1_ACCUMULATION = "Q1"   # Structure forming
    Q2_MANIPULATION = "Q2"   # Judas swing
    Q3_DISTRIBUTION = "Q3"   # Main move
    Q4_CONTINUATION = "Q4"   # Manage/exit


class Bias(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class TradeSetup:
    pair: str
    timeframe: str
    setup_type: str
    bias: Bias
    confidence: float
    confluence: List[str]


class StrategyAdapter:
    """
    Adapter for trading strategy logic.
    Reads rules from knowledge/ markdown files.
    """
    
    def __init__(self, knowledge_dir: str = "agents/trading_agent/knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self._strategies = ["ict", "btmm", "quarterly", "stacey-burke"]
        
    def get_current_phase(self) -> SessionPhase:
        """
        Determine current market phase based on Quarterly Theory.
        London Open (8:00 UTC) = True Open.
        """
        now = datetime.now(timezone.utc)
        minutes_since_midnight = now.hour * 60 + now.minute
        london_open = 8 * 60  # 8:00 UTC
        
        minutes_since_open = (minutes_since_midnight - london_open + 1440) % 1440
        quarter = 360  # 6 hours per quarter
        
        if minutes_since_open < quarter:
            return SessionPhase.Q1_ACCUMULATION
        elif minutes_since_open < quarter * 2:
            return SessionPhase.Q2_MANIPULATION
        elif minutes_since_open < quarter * 3:
            return SessionPhase.Q3_DISTRIBUTION
        else:
            return SessionPhase.Q4_CONTINUATION
            
    def get_phase_action(self, phase: SessionPhase) -> str:
        """Get recommended action for current phase."""
        actions = {
            SessionPhase.Q1_ACCUMULATION: "Wait for structure. Identify key levels.",
            SessionPhase.Q2_MANIPULATION: "Watch for stop hunts. Prepare for reversal.",
            SessionPhase.Q3_DISTRIBUTION: "Main move phase. Execute with confluence.",
            SessionPhase.Q4_CONTINUATION: "Manage trades. Look for exits."
        }
        return actions.get(phase, "")
        
    def load_strategy_rules(self, strategy: str) -> str:
        """Load strategy rules from knowledge file."""
        filepath = self.knowledge_dir / f"{strategy}.md"
        if filepath.exists():
            return filepath.read_text()
        return ""
        
    def get_all_rules(self) -> Dict[str, str]:
        """Load all strategy rules."""
        return {
            name: self.load_strategy_rules(name.replace('-', '_'))
            for name in self._strategies
        }
