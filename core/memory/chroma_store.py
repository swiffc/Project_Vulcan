"""
Chroma Vector Store

Local vector database for semantic search over trades, lessons, and analyses.
Data stays on your machine - no API costs, full privacy.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None
    Settings = None

from .embeddings import get_embedding_function


class VulcanMemory:
    """Vector memory store using Chroma.

    Collections:
        - trades: Trade journal entries with setup type, rationale, lessons
        - lessons: Extracted lessons learned from trading
        - analyses: Daily/weekly market analyses
        - cad_jobs: CAD work logs with commands, parameters, outcomes
    """

    def __init__(self, persist_dir: str = "./storage/chroma"):
        """Initialize the memory store.

        Args:
            persist_dir: Directory to persist the vector database.
        """
        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_fn = get_embedding_function()

        # Initialize collections
        self.trades = self.client.get_or_create_collection(
            name="trades",
            embedding_function=self.embedding_fn,
            metadata={"description": "Trade journal entries"}
        )
        self.lessons = self.client.get_or_create_collection(
            name="lessons",
            embedding_function=self.embedding_fn,
            metadata={"description": "Lessons learned from trading"}
        )
        self.analyses = self.client.get_or_create_collection(
            name="analyses",
            embedding_function=self.embedding_fn,
            metadata={"description": "Market analyses"}
        )
        self.cad_jobs = self.client.get_or_create_collection(
            name="cad_jobs",
            embedding_function=self.embedding_fn,
            metadata={"description": "CAD work logs"}
        )

    def add_trade(self, trade_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Add a trade to memory.

        Args:
            trade_id: Unique identifier for the trade
            content: Full trade description (setup, rationale, result, lesson)
            metadata: Structured data (pair, setup_type, result, day, session, r_multiple)
        """
        metadata["timestamp"] = datetime.now().isoformat()
        self.trades.add(
            ids=[trade_id],
            documents=[content],
            metadatas=[metadata]
        )

    def search_trades(self, query: str, n_results: int = 5,
                      where: Optional[Dict] = None) -> Dict[str, Any]:
        """Semantic search over trades.

        Args:
            query: Natural language query
            n_results: Number of results to return
            where: Optional metadata filter (e.g., {"result": "win"})

        Returns:
            Dict with ids, documents, metadatas, distances
        """
        return self.trades.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

    def add_lesson(self, lesson_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Add a lesson learned.

        Args:
            lesson_id: Unique identifier for the lesson
            content: The lesson text
            metadata: Context (source_trade, category, severity)
        """
        metadata["timestamp"] = datetime.now().isoformat()
        self.lessons.add(
            ids=[lesson_id],
            documents=[content],
            metadatas=[metadata]
        )

    def search_lessons(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Find relevant lessons."""
        return self.lessons.query(
            query_texts=[query],
            n_results=n_results
        )

    def add_analysis(self, analysis_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Add a market analysis."""
        metadata["timestamp"] = datetime.now().isoformat()
        self.analyses.add(
            ids=[analysis_id],
            documents=[content],
            metadatas=[metadata]
        )

    def search_analyses(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search market analyses."""
        return self.analyses.query(
            query_texts=[query],
            n_results=n_results
        )

    def add_cad_job(self, job_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Add a CAD job log."""
        metadata["timestamp"] = datetime.now().isoformat()
        self.cad_jobs.add(
            ids=[job_id],
            documents=[content],
            metadatas=[metadata]
        )

    def search_cad_jobs(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search CAD job history."""
        return self.cad_jobs.query(
            query_texts=[query],
            n_results=n_results
        )

    def get_trade_count(self) -> int:
        """Get total number of trades stored."""
        return self.trades.count()

    def get_lesson_count(self) -> int:
        """Get total number of lessons stored."""
        return self.lessons.count()

    def get_trades_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get all trades within a date range.

        Args:
            start_date: ISO format date string (YYYY-MM-DD)
            end_date: ISO format date string (YYYY-MM-DD)

        Returns:
            List of trade documents with metadata
        """
        results = self.trades.get(
            where={
                "$and": [
                    {"timestamp": {"$gte": start_date}},
                    {"timestamp": {"$lte": end_date}}
                ]
            }
        )
        return [
            {"id": id, "content": doc, "metadata": meta}
            for id, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ] if results["ids"] else []
