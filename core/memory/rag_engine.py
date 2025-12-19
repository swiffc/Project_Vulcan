"""
RAG Engine - Retrieval-Augmented Generation

Retrieves relevant context from memory before answering queries.
Augments prompts with past trades, lessons, and analyses.
"""

from typing import List, Dict, Any, Optional, Literal

from .chroma_store import VulcanMemory


ContextType = Literal["all", "trades", "lessons", "analyses", "cad"]


class RAGEngine:
    """Retrieval-Augmented Generation for Vulcan.

    Workflow:
        1. User asks a question
        2. RAG retrieves relevant past context
        3. Context is added to the prompt
        4. AI answers with full context awareness
    """

    def __init__(self, memory: VulcanMemory, context_window: int = 3):
        """Initialize RAG engine.

        Args:
            memory: VulcanMemory instance
            context_window: Number of similar documents to retrieve
        """
        self.memory = memory
        self.context_window = context_window

    def augment_prompt(
        self,
        user_query: str,
        context_type: ContextType = "all",
        include_metadata: bool = True
    ) -> str:
        """Retrieve relevant context and augment the prompt.

        Args:
            user_query: The user's question
            context_type: Which collections to search ("all", "trades", "lessons", etc.)
            include_metadata: Whether to include metadata in context

        Returns:
            Augmented prompt with retrieved context
        """
        context_parts = []

        if context_type in ["all", "trades"]:
            trades_context = self._get_trades_context(user_query, include_metadata)
            if trades_context:
                context_parts.append(trades_context)

        if context_type in ["all", "lessons"]:
            lessons_context = self._get_lessons_context(user_query, include_metadata)
            if lessons_context:
                context_parts.append(lessons_context)

        if context_type in ["all", "analyses"]:
            analyses_context = self._get_analyses_context(user_query, include_metadata)
            if analyses_context:
                context_parts.append(analyses_context)

        if context_type in ["cad"]:
            cad_context = self._get_cad_context(user_query, include_metadata)
            if cad_context:
                context_parts.append(cad_context)

        if context_parts:
            return f"""## Retrieved Context

{chr(10).join(context_parts)}

---

## User Query
{user_query}"""

        return user_query

    def _get_trades_context(self, query: str, include_metadata: bool) -> Optional[str]:
        """Retrieve relevant trades."""
        results = self.memory.search_trades(query, n_results=self.context_window)

        if not results["documents"][0]:
            return None

        lines = ["### Relevant Past Trades"]
        for i, (doc, meta) in enumerate(
            zip(results["documents"][0], results["metadatas"][0]), 1
        ):
            lines.append(f"\n**Trade {i}:**")
            if include_metadata and meta:
                meta_str = ", ".join(f"{k}: {v}" for k, v in meta.items() if k != "timestamp")
                lines.append(f"*({meta_str})*")
            lines.append(doc)

        return "\n".join(lines)

    def _get_lessons_context(self, query: str, include_metadata: bool) -> Optional[str]:
        """Retrieve relevant lessons."""
        results = self.memory.search_lessons(query, n_results=self.context_window)

        if not results["documents"][0]:
            return None

        lines = ["### Relevant Lessons Learned"]
        for i, (doc, meta) in enumerate(
            zip(results["documents"][0], results["metadatas"][0]), 1
        ):
            lines.append(f"\n**Lesson {i}:**")
            if include_metadata and meta:
                category = meta.get("category", "general")
                lines.append(f"*Category: {category}*")
            lines.append(doc)

        return "\n".join(lines)

    def _get_analyses_context(self, query: str, include_metadata: bool) -> Optional[str]:
        """Retrieve relevant market analyses."""
        results = self.memory.search_analyses(query, n_results=self.context_window)

        if not results["documents"][0]:
            return None

        lines = ["### Relevant Market Analyses"]
        for i, (doc, meta) in enumerate(
            zip(results["documents"][0], results["metadatas"][0]), 1
        ):
            lines.append(f"\n**Analysis {i}:**")
            if include_metadata and meta:
                date = meta.get("date", meta.get("timestamp", "unknown"))
                lines.append(f"*Date: {date}*")
            lines.append(doc)

        return "\n".join(lines)

    def _get_cad_context(self, query: str, include_metadata: bool) -> Optional[str]:
        """Retrieve relevant CAD job logs."""
        results = self.memory.search_cad_jobs(query, n_results=self.context_window)

        if not results["documents"][0]:
            return None

        lines = ["### Relevant CAD Jobs"]
        for i, (doc, meta) in enumerate(
            zip(results["documents"][0], results["metadatas"][0]), 1
        ):
            lines.append(f"\n**CAD Job {i}:**")
            if include_metadata and meta:
                software = meta.get("software", "unknown")
                lines.append(f"*Software: {software}*")
            lines.append(doc)

        return "\n".join(lines)

    def get_context_only(
        self,
        query: str,
        context_type: ContextType = "all"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get raw context without prompt augmentation.

        Useful for displaying context separately or custom formatting.

        Returns:
            Dict with context by type
        """
        context = {}

        if context_type in ["all", "trades"]:
            results = self.memory.search_trades(query, n_results=self.context_window)
            if results["documents"][0]:
                context["trades"] = [
                    {"content": doc, "metadata": meta}
                    for doc, meta in zip(results["documents"][0], results["metadatas"][0])
                ]

        if context_type in ["all", "lessons"]:
            results = self.memory.search_lessons(query, n_results=self.context_window)
            if results["documents"][0]:
                context["lessons"] = [
                    {"content": doc, "metadata": meta}
                    for doc, meta in zip(results["documents"][0], results["metadatas"][0])
                ]

        return context
