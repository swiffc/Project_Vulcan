from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import logging
from core.database_adapter import get_db_adapter

logger = logging.getLogger("core.trading")
router = APIRouter()


class Trade(BaseModel):
    id: Optional[str] = None
    pair: str
    direction: Optional[str] = "long"
    setup: str
    entry: float
    target: float
    stop: float
    rr: Optional[float] = None
    result: Optional[str] = None
    notes: Optional[str] = None


@router.post("/trading/journal", response_model=Trade)
async def create_trade(trade: Trade):
    db = get_db_adapter()
    try:
        trade_id = db.add_trade(trade.dict())
        trade.id = trade_id
        return trade
    except Exception as e:
        logger.error(f"API Error creating trade: {e}")
        raise HTTPException(status_code=500, detail="Failed to save trade to database")


@router.get("/trading/journal", response_model=List[Trade])
async def get_trades():
    db = get_db_adapter()
    try:
        raw_trades = db.get_recent_trades()
        # Map DB fields to API model
        trades = []
        for t in raw_trades:
            trades.append(
                Trade(
                    id=t["id"],
                    pair=t["symbol"],
                    direction=t["direction"],
                    setup=t["setup"],
                    entry=t["entry_price"],
                    target=t["target"],
                    stop=t["stop"],
                    rr=t["rr"],
                    result=t["result"],
                    notes=t["notes"],
                )
            )
        return trades
    except Exception as e:
        logger.error(f"API Error fetching trades: {e}")
        return []


@router.get("/trading/journal/{trade_id}", response_model=Trade)
async def get_trade(trade_id: str):
    # For now, searching in recent trades
    db = get_db_adapter()
    trades = db.get_recent_trades(limit=100)
    for t in trades:
        if t["id"] == trade_id:
            return Trade(
                id=t["id"],
                pair=t["symbol"],
                direction=t["direction"],
                setup=t["setup"],
                entry=t["entry_price"],
                target=t["target"],
                stop=t["stop"],
                rr=t["rr"],
                result=t["result"],
                notes=t["notes"],
            )
    raise HTTPException(status_code=404, detail="Trade not found")
