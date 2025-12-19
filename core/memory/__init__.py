"""
Project Vulcan - Memory & RAG Module

Provides semantic search and context retrieval for agents.
Uses Chroma for local vector storage (no API costs, data stays local).
"""

from .chroma_store import VulcanMemory
from .rag_engine import RAGEngine
from .embeddings import get_embedding_function
from .ingest import TradeIngestor, LessonIngestor, AnalysisIngestor, CADIngestor

__all__ = [
    "VulcanMemory",
    "RAGEngine",
    "get_embedding_function",
    "TradeIngestor",
    "LessonIngestor",
    "AnalysisIngestor",
    "CADIngestor",
]
