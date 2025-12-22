from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid

router = APIRouter()

class Trade(BaseModel):
    id: Optional[str] = None
    pair: str
    bias: str
    setup: str
    entry: float
    target: float
    stop: float
    rr: float
    result: Optional[str] = None

# In-memory database
db: Dict[str, Trade] = {}

@router.post("/trading/journal", response_model=Trade)
async def create_trade(trade: Trade):
    trade.id = str(uuid.uuid4())
    db[trade.id] = trade
    return trade

@router.get("/trading/journal", response_model=List[Trade])
async def get_trades():
    return list(db.values())

@router.get("/trading/journal/{trade_id}", response_model=Trade)
async def get_trade(trade_id: str):
    if trade_id not in db:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db[trade_id]

@router.put("/trading/journal/{trade_id}", response_model=Trade)
async def update_trade(trade_id: str, trade: Trade):
    if trade_id not in db:
        raise HTTPException(status_code=404, detail="Trade not found")
    trade.id = trade_id
    db[trade_id] = trade
    return trade

@router.delete("/trading/journal/{trade_id}")
async def delete_trade(trade_id: str):
    if trade_id not in db:
        raise HTTPException(status_code=404, detail="Trade not found")
    del db[trade_id]
    return {"status": "success", "message": "Trade deleted"}
