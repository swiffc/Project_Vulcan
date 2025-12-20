"""
Memory Controller - API endpoints for RAG and memory operations.

Exposes the core/memory module via REST API.
"""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

router = APIRouter(prefix="/memory", tags=["memory"])

# Lazy load memory components
_memory = None
_rag_engine = None
_trade_ingestor = None
_lesson_ingestor = None


def get_memory():
    """Lazy load VulcanMemory."""
    global _memory
    if _memory is None:
        from core.memory import VulcanMemory
        _memory = VulcanMemory(persist_dir=str(PROJECT_ROOT / "storage" / "chroma"))
    return _memory


def get_rag_engine():
    """Lazy load RAGEngine."""
    global _rag_engine
    if _rag_engine is None:
        from core.memory import RAGEngine
        _rag_engine = RAGEngine(get_memory())
    return _rag_engine


def get_trade_ingestor():
    """Lazy load TradeIngestor."""
    global _trade_ingestor
    if _trade_ingestor is None:
        from core.memory import TradeIngestor
        _trade_ingestor = TradeIngestor(get_memory())
    return _trade_ingestor


def get_lesson_ingestor():
    """Lazy load LessonIngestor."""
    global _lesson_ingestor
    if _lesson_ingestor is None:
        from core.memory import LessonIngestor
        _lesson_ingestor = LessonIngestor(get_memory())
    return _lesson_ingestor


# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    n_results: int = 5


class TradeRequest(BaseModel):
    pair: str
    setup_type: str
    rationale: str
    result: str  # "win" or "loss"
    r_multiple: float
    lesson: str
    day: Optional[str] = None
    session: Optional[str] = None


class LessonRequest(BaseModel):
    content: str
    category: str = "general"
    source_trade: Optional[str] = None


class AugmentRequest(BaseModel):
    query: str
    context_type: str = "all"


# Search Endpoints
@router.post("/search/trades")
async def search_trades(req: SearchRequest):
    """Search trades by semantic similarity."""
    try:
        memory = get_memory()
        results = memory.search_trades(req.query, n_results=req.n_results)

        formatted = []
        if results["documents"][0]:
            for i, (doc, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0] if "distances" in results else [0] * len(results["documents"][0])
            )):
                formatted.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": meta,
                    "distance": dist
                })

        return {"results": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/lessons")
async def search_lessons(req: SearchRequest):
    """Search lessons by semantic similarity."""
    try:
        memory = get_memory()
        results = memory.search_lessons(req.query, n_results=req.n_results)

        formatted = []
        if results["documents"][0]:
            for i, (doc, meta) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0]
            )):
                formatted.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": meta
                })

        return {"results": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# RAG Endpoint
@router.post("/rag/augment")
async def augment_prompt(req: AugmentRequest):
    """Augment a query with relevant context from memory."""
    try:
        rag = get_rag_engine()
        augmented = rag.augment_prompt(req.query, context_type=req.context_type)
        return {"augmented_prompt": augmented}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ingest Endpoints
@router.post("/trades/add")
async def add_trade(req: TradeRequest):
    """Add a trade to memory."""
    try:
        ingestor = get_trade_ingestor()
        trade_id = ingestor.ingest_trade(
            pair=req.pair,
            setup_type=req.setup_type,
            rationale=req.rationale,
            result=req.result,
            r_multiple=req.r_multiple,
            lesson=req.lesson,
            day=req.day,
            session=req.session
        )
        return {"trade_id": trade_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lessons/add")
async def add_lesson(req: LessonRequest):
    """Add a lesson to memory."""
    try:
        ingestor = get_lesson_ingestor()
        lesson_id = ingestor.ingest_lesson(
            content=req.content,
            category=req.category,
            source_trade=req.source_trade
        )
        return {"lesson_id": lesson_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Review Endpoint
@router.get("/review/weekly")
async def get_weekly_review():
    """Generate weekly trading review."""
    try:
        from agents.review_agent.src import WeeklyReviewAgent, get_last_week_dates

        memory = get_memory()
        agent = WeeklyReviewAgent(memory)

        week_start, week_end = get_last_week_dates()
        review = agent.generate_review(week_start, week_end)

        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Stats Endpoint
@router.get("/stats")
async def get_memory_stats():
    """Get memory statistics."""
    try:
        memory = get_memory()
        return {
            "trade_count": memory.get_trade_count(),
            "lesson_count": memory.get_lesson_count(),
            "status": "ok"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
