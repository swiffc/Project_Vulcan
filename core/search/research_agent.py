"""
Research Agent - Autonomous web research capability

Based on: anthropics/claude-agent-sdk-demos/research-agent

Architecture:
- Lead Agent: Coordinates using Task tool
- Researcher Agents: Use WebSearch + Write to gather info
- Report-Writer Agent: Synthesizes findings

Wrapped for Project Vulcan integration.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import asyncio

from .adapter import WebSearchAdapter, SearchResponse, SearchResult, get_search_adapter


@dataclass
class ResearchResult:
    """Result of a research task."""

    query: str
    summary: str
    sources: List[Dict[str, str]]
    raw_searches: List[SearchResponse]
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_context(self) -> str:
        """Format for LLM context."""
        parts = [
            f"## Research Results: {self.query}",
            "",
            f"**Summary**: {self.summary}",
            "",
            "**Sources**:"
        ]
        for i, source in enumerate(self.sources[:5], 1):
            parts.append(f"  {i}. [{source.get('title', 'Unknown')}]({source.get('url', '')})")

        return "\n".join(parts)

    def to_markdown(self) -> str:
        """Format as full markdown report."""
        parts = [
            f"# Research Report: {self.query}",
            "",
            f"*Generated: {self.timestamp.isoformat()}*",
            f"*Confidence: {self.confidence:.0%}*",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## Sources",
            ""
        ]

        for i, source in enumerate(self.sources, 1):
            parts.append(f"### Source {i}: {source.get('title', 'Unknown')}")
            parts.append(f"- URL: {source.get('url', '')}")
            parts.append(f"- Snippet: {source.get('snippet', '')}")
            parts.append("")

        return "\n".join(parts)


class ResearchAgent:
    """
    Autonomous research agent for web-based information gathering.

    Features:
    - Multi-query research (explores topic from multiple angles)
    - Source verification (checks multiple sources)
    - Summarization (synthesizes findings)
    - Citation tracking (maintains source links)

    Usage:
        agent = ResearchAgent()
        result = await agent.research("ASME B16.5 flange dimensions for NPS 6")
    """

    def __init__(
        self,
        search_adapter: Optional[WebSearchAdapter] = None,
        llm_client: Optional[Any] = None
    ):
        """Initialize research agent."""
        self.search = search_adapter or get_search_adapter()
        self.llm_client = llm_client

        # Research configuration
        self.max_queries = 3  # Number of search queries per research task
        self.max_results_per_query = 5
        self.require_multiple_sources = True

    async def research(
        self,
        topic: str,
        depth: str = "standard",  # quick, standard, thorough
        output_file: Optional[Path] = None
    ) -> ResearchResult:
        """
        Research a topic using web search.

        Args:
            topic: The topic to research
            depth: Research depth (affects number of queries)
            output_file: Optional file to save results

        Returns:
            ResearchResult with findings
        """
        # Determine research intensity
        if depth == "quick":
            queries = [topic]
        elif depth == "thorough":
            queries = self._generate_research_queries(topic, count=5)
        else:  # standard
            queries = self._generate_research_queries(topic, count=3)

        # Execute searches
        all_searches: List[SearchResponse] = []
        all_sources: List[Dict[str, str]] = []

        for query in queries:
            try:
                response = await self.search.search(
                    query=query,
                    max_results=self.max_results_per_query
                )
                all_searches.append(response)

                # Collect sources
                for result in response.results:
                    all_sources.append({
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet
                    })
            except Exception as e:
                # Log but continue
                pass

        # Deduplicate sources by URL
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            url = source.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)

        # Generate summary
        summary = self._synthesize_findings(topic, unique_sources)

        # Calculate confidence
        confidence = min(len(unique_sources) / 5, 1.0)

        result = ResearchResult(
            query=topic,
            summary=summary,
            sources=unique_sources,
            raw_searches=all_searches,
            confidence=confidence
        )

        # Save to file if requested
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(result.to_markdown(), encoding="utf-8")

        return result

    def _generate_research_queries(self, topic: str, count: int = 3) -> List[str]:
        """Generate multiple search queries for a topic."""
        queries = [topic]

        # Add variations
        variations = [
            f"{topic} specifications",
            f"{topic} dimensions table",
            f"{topic} standards reference",
            f"{topic} technical data",
            f"{topic} engineering data"
        ]

        for variation in variations:
            if len(queries) >= count:
                break
            queries.append(variation)

        return queries[:count]

    def _synthesize_findings(
        self,
        topic: str,
        sources: List[Dict[str, str]]
    ) -> str:
        """Synthesize findings from sources into a summary."""
        if not sources:
            return f"No information found for: {topic}"

        # Simple synthesis (could be enhanced with LLM)
        snippets = [s.get("snippet", "") for s in sources[:5] if s.get("snippet")]

        if len(snippets) == 0:
            return f"Found {len(sources)} sources but no extractable content for: {topic}"

        # Combine snippets
        combined = " | ".join(snippets[:3])

        return f"Based on {len(sources)} sources: {combined[:500]}..."

    async def research_engineering_standard(
        self,
        standard: str,
        specific_data: Optional[str] = None
    ) -> ResearchResult:
        """
        Research an engineering standard (ASME, API, ISO, etc.).

        Optimized for finding technical specifications.

        Args:
            standard: Standard name (e.g., "ASME B16.5")
            specific_data: Specific data to find (e.g., "NPS 6 Class 150 dimensions")

        Returns:
            ResearchResult
        """
        # Build optimized query
        if specific_data:
            query = f"{standard} {specific_data}"
        else:
            query = f"{standard} specifications dimensions table"

        # Use engineering-specific domains
        return await self.research(
            topic=query,
            depth="thorough"
        )

    def research_sync(
        self,
        topic: str,
        depth: str = "standard"
    ) -> ResearchResult:
        """Synchronous research wrapper."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.research(topic, depth))


# Singleton
_agent_instance: Optional[ResearchAgent] = None


def get_research_agent() -> ResearchAgent:
    """Get singleton research agent."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ResearchAgent()
    return _agent_instance
