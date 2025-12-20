"""
Journal Adapter
Thin wrapper for trade journaling with Memory Brain integration.

Packages Used:
- chromadb (via Memory Brain)
- Already in requirements.txt
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("trading.journal")


@dataclass
class TradeRecord:
    id: str
    pair: str
    session: str
    bias: str
    setup_type: str
    entry: float
    stop_loss: float
    take_profit: float
    result: str  # win, loss, breakeven
    r_multiple: float
    lesson: str
    timestamp: str = ""
    screenshot_path: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.id:
            self.id = f"trade-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


class JournalAdapter:
    """
    Adapter for trade journaling with RAG memory.
    Stores trades for future recall and pattern analysis.
    """
    
    def __init__(self, memory_client=None):
        self.memory = memory_client
        self._local_cache: List[TradeRecord] = []
        
    async def log_trade(self, trade: TradeRecord) -> str:
        """Log a trade to memory."""
        # Build embedding text for semantic search
        embedding_text = f"""
        Trade: {trade.pair} {trade.bias} {trade.setup_type}
        Result: {trade.result} ({trade.r_multiple}R)
        Lesson: {trade.lesson}
        Session: {trade.session}
        """
        
        # Store in memory brain
        if self.memory:
            await self.memory.store(
                key=f"trade:{trade.id}",
                content=embedding_text,
                metadata=asdict(trade)
            )
        
        # Also cache locally
        self._local_cache.append(trade)
        logger.info(f"📝 Logged: {trade.id} - {trade.result}")
        
        return trade.id
        
    async def search_similar(self, query: str, limit: int = 5) -> List[TradeRecord]:
        """Search for similar past trades."""
        if not self.memory:
            return []
            
        results = await self.memory.search(query, limit=limit)
        return [TradeRecord(**r.metadata) for r in results]
        
    async def get_weekly_stats(self) -> Dict:
        """Calculate stats for current week."""
        # Filter to this week's trades
        week_trades = self._local_cache  # Would filter by date in production
        
        if not week_trades:
            return {"total": 0, "win_rate": 0, "total_r": 0}
            
        wins = sum(1 for t in week_trades if t.result == "win")
        total_r = sum(t.r_multiple for t in week_trades)
        
        return {
            "total": len(week_trades),
            "wins": wins,
            "losses": len(week_trades) - wins,
            "win_rate": wins / len(week_trades) if week_trades else 0,
            "total_r": total_r,
            "avg_r": total_r / len(week_trades) if week_trades else 0
        }
        
    async def recall_lessons(self, pair: str) -> List[str]:
        """Recall lessons learned from past trades on a pair."""
        if not self.memory:
            return []
            
        results = await self.memory.search(f"lessons from {pair} trades", limit=10)
        return [r.metadata.get("lesson", "") for r in results if r.metadata.get("lesson")]
