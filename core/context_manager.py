"""
Context Manager - Unified Cross-Domain Context

Manages context across Trading, CAD, and Work domains.
Provides unified recall and context injection for all agents.
"""

import logging
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger("core.context_manager")


@dataclass
class ContextItem:
    """A single context item."""
    id: str
    domain: str  # trading, cad, work, general
    type: str  # trade, validation, strategy, task, conversation
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance: float = 1.0  # 0-1 scale
    ttl_hours: int = 24  # Time to live

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.timestamp + timedelta(hours=self.ttl_hours)


class ContextManager:
    """
    Unified context management across all domains.

    Provides:
    - Short-term working memory (current session)
    - Cross-domain context retrieval
    - Context prioritization and filtering
    - RAG integration for long-term memory
    """

    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self._context: List[ContextItem] = []
        self._rag_engine = None
        self._knowledge_graph = None

    def _get_rag(self):
        """Lazy load RAG engine."""
        if self._rag_engine is None:
            try:
                from core.memory.rag_engine import RAGEngine
                from core.memory.chroma_store import VulcanMemory
                memory = VulcanMemory()
                self._rag_engine = RAGEngine(memory)
            except Exception as e:
                logger.warning(f"RAG engine not available: {e}")
        return self._rag_engine

    def _get_knowledge_graph(self):
        """Lazy load knowledge graph."""
        if self._knowledge_graph is None:
            try:
                from core.memory.knowledge_graph import get_knowledge_graph
                self._knowledge_graph = get_knowledge_graph()
            except Exception as e:
                logger.warning(f"Knowledge graph not available: {e}")
        return self._knowledge_graph

    def add(
        self,
        content: str,
        domain: Literal["trading", "cad", "work", "general"],
        type: str,
        metadata: Dict = None,
        importance: float = 1.0,
        ttl_hours: int = 24
    ) -> ContextItem:
        """Add a context item to working memory."""
        item = ContextItem(
            id=f"{domain}_{type}_{datetime.utcnow().timestamp()}",
            domain=domain,
            type=type,
            content=content,
            metadata=metadata or {},
            importance=importance,
            ttl_hours=ttl_hours
        )

        self._context.append(item)
        self._prune()

        return item

    def _prune(self):
        """Remove expired items and enforce max size."""
        # Remove expired
        self._context = [c for c in self._context if not c.is_expired]

        # Sort by importance and recency
        self._context.sort(
            key=lambda x: (x.importance, x.timestamp.timestamp()),
            reverse=True
        )

        # Enforce max size
        if len(self._context) > self.max_items:
            self._context = self._context[:self.max_items]

    def get_context(
        self,
        domain: str = None,
        type: str = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[ContextItem]:
        """Get context items with optional filters."""
        items = self._context

        if domain:
            items = [c for c in items if c.domain == domain]
        if type:
            items = [c for c in items if c.type == type]
        if min_importance > 0:
            items = [c for c in items if c.importance >= min_importance]

        return items[:limit]

    def get_for_prompt(
        self,
        query: str,
        domain: str = None,
        max_tokens: int = 2000
    ) -> str:
        """
        Get formatted context for inclusion in a prompt.

        Combines:
        - Recent working memory
        - RAG-retrieved relevant context
        - Knowledge graph connections
        """
        parts = []
        char_count = 0
        max_chars = max_tokens * 4  # Rough token-to-char conversion

        # 1. Recent working memory
        recent = self.get_context(domain=domain, limit=5)
        if recent:
            parts.append("## Recent Context")
            for item in recent:
                summary = item.content[:200]
                if char_count + len(summary) > max_chars:
                    break
                parts.append(f"- [{item.domain}/{item.type}] {summary}")
                char_count += len(summary)
            parts.append("")

        # 2. RAG retrieval for query
        rag = self._get_rag()
        if rag and query:
            try:
                context_type = domain if domain else "all"
                augmented = rag.augment_prompt(query, context_type=context_type)
                if augmented and char_count + len(augmented) < max_chars:
                    parts.append("## Relevant Memory")
                    parts.append(augmented[:max_chars - char_count])
                    char_count += len(augmented)
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

        # 3. Knowledge graph relationships (if query mentions known entities)
        kg = self._get_knowledge_graph()
        if kg and query:
            try:
                # Search for matching nodes
                matches = kg.search(query)[:3]
                if matches:
                    parts.append("## Related Knowledge")
                    for node in matches:
                        neighbors = kg.get_neighbors(node.id, depth=1)[:3]
                        if neighbors:
                            rels = ", ".join([n["relation"] for n in neighbors])
                            parts.append(f"- {node.label}: {rels}")
            except Exception as e:
                logger.warning(f"Knowledge graph lookup failed: {e}")

        return "\n".join(parts)

    def add_trade(self, trade_data: Dict):
        """Add trading context."""
        self.add(
            content=f"Trade: {trade_data.get('symbol')} {trade_data.get('direction')} "
                   f"@ {trade_data.get('entry_price')} - {trade_data.get('setup', 'N/A')}",
            domain="trading",
            type="trade",
            metadata=trade_data,
            importance=0.8,
            ttl_hours=48
        )

    def add_validation(self, validation_data: Dict):
        """Add CAD validation context."""
        status = "PASSED" if validation_data.get("passed") else "FAILED"
        errors = validation_data.get("errors", [])
        self.add(
            content=f"Validation {status}: {validation_data.get('file_path', 'Unknown')} "
                   f"- {len(errors)} issues",
            domain="cad",
            type="validation",
            metadata=validation_data,
            importance=0.9 if errors else 0.5,
            ttl_hours=72
        )

    def add_strategy_result(self, strategy_name: str, passed: bool, details: Dict = None):
        """Add strategy execution context."""
        self.add(
            content=f"Strategy '{strategy_name}' {'PASSED' if passed else 'FAILED'}",
            domain="cad",
            type="strategy",
            metadata={"name": strategy_name, "passed": passed, **(details or {})},
            importance=0.9,
            ttl_hours=168  # Keep for a week
        )

    def add_work_task(self, task_data: Dict):
        """Add work task context."""
        self.add(
            content=f"Task: {task_data.get('title', 'Unknown')} - {task_data.get('status', 'pending')}",
            domain="work",
            type="task",
            metadata=task_data,
            importance=0.7,
            ttl_hours=24
        )

    def add_conversation(self, message: str, role: str = "user"):
        """Add conversation context."""
        self.add(
            content=f"[{role}] {message[:500]}",
            domain="general",
            type="conversation",
            metadata={"role": role},
            importance=0.6,
            ttl_hours=4
        )

    def clear_domain(self, domain: str):
        """Clear all context for a domain."""
        self._context = [c for c in self._context if c.domain != domain]

    def clear_all(self):
        """Clear all context."""
        self._context.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics."""
        by_domain = {}
        by_type = {}

        for item in self._context:
            by_domain[item.domain] = by_domain.get(item.domain, 0) + 1
            by_type[item.type] = by_type.get(item.type, 0) + 1

        return {
            "total_items": len(self._context),
            "by_domain": by_domain,
            "by_type": by_type,
            "oldest": min((c.timestamp for c in self._context), default=None),
            "newest": max((c.timestamp for c in self._context), default=None)
        }


# Singleton
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get or create context manager singleton."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
