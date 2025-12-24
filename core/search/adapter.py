"""
Web Search Adapter - Unified search interface

Wraps multiple search providers:
1. Tavily API (best quality, requires key)
2. DuckDuckGo (free, no key needed)
3. Claude web_search tool (API-native)

Based on patterns from:
- anthropics/claude-agent-sdk-demos/research-agent
- NirDiamant/RAG_Techniques
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
import json
import asyncio


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    source: str  # tavily, duckduckgo, claude
    score: float = 0.0
    published_date: Optional[str] = None
    raw_content: Optional[str] = None

    def to_context(self) -> str:
        """Format result for LLM context."""
        return f"**{self.title}**\nSource: {self.url}\n{self.snippet}"


@dataclass
class SearchResponse:
    """Response from a search query."""

    query: str
    results: List[SearchResult]
    provider: str
    total_results: int = 0
    search_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_context(self, max_results: int = 5) -> str:
        """Format all results for LLM context."""
        parts = [f"## Search Results for: {self.query}\n"]
        for i, result in enumerate(self.results[:max_results], 1):
            parts.append(f"### Result {i}")
            parts.append(result.to_context())
            parts.append("")
        return "\n".join(parts)


class WebSearchAdapter:
    """
    Unified web search adapter.

    Priority order:
    1. Tavily (if TAVILY_API_KEY set)
    2. DuckDuckGo (free fallback)

    Usage:
        adapter = WebSearchAdapter()
        results = await adapter.search("ASME B16.5 flange dimensions")
    """

    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        prefer_provider: Literal["tavily", "duckduckgo", "auto"] = "auto"
    ):
        """Initialize search adapter."""
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.prefer_provider = prefer_provider

        # Initialize providers
        self._tavily_client = None
        self._ddg_available = False

        self._init_providers()

    def _init_providers(self) -> None:
        """Initialize available search providers."""
        # Try Tavily
        if self.tavily_api_key:
            try:
                from tavily import TavilyClient
                self._tavily_client = TavilyClient(api_key=self.tavily_api_key)
            except ImportError:
                pass
            except Exception:
                pass

        # Try DuckDuckGo
        try:
            from duckduckgo_search import DDGS
            self._ddg_available = True
        except ImportError:
            pass

    @property
    def available_providers(self) -> List[str]:
        """List available search providers."""
        providers = []
        if self._tavily_client:
            providers.append("tavily")
        if self._ddg_available:
            providers.append("duckduckgo")
        return providers

    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: Literal["basic", "advanced"] = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> SearchResponse:
        """
        Search the web.

        Args:
            query: Search query
            max_results: Maximum results to return
            search_depth: basic (fast) or advanced (thorough)
            include_domains: Only search these domains
            exclude_domains: Exclude these domains

        Returns:
            SearchResponse with results
        """
        # Determine provider
        provider = self._select_provider()

        if provider == "tavily":
            return await self._search_tavily(
                query, max_results, search_depth, include_domains, exclude_domains
            )
        elif provider == "duckduckgo":
            return await self._search_duckduckgo(query, max_results)
        else:
            raise RuntimeError("No search providers available. Install tavily-python or duckduckgo_search.")

    def _select_provider(self) -> str:
        """Select the best available provider."""
        if self.prefer_provider == "tavily" and self._tavily_client:
            return "tavily"
        elif self.prefer_provider == "duckduckgo" and self._ddg_available:
            return "duckduckgo"
        elif self.prefer_provider == "auto":
            if self._tavily_client:
                return "tavily"
            elif self._ddg_available:
                return "duckduckgo"
        raise RuntimeError("No search provider available")

    async def _search_tavily(
        self,
        query: str,
        max_results: int,
        search_depth: str,
        include_domains: Optional[List[str]],
        exclude_domains: Optional[List[str]]
    ) -> SearchResponse:
        """Search using Tavily API."""
        import time
        start = time.time()

        try:
            # Tavily search
            response = self._tavily_client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains or [],
                exclude_domains=exclude_domains or []
            )

            results = []
            for item in response.get("results", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    source="tavily",
                    score=item.get("score", 0.0),
                    raw_content=item.get("raw_content")
                ))

            elapsed = int((time.time() - start) * 1000)

            return SearchResponse(
                query=query,
                results=results,
                provider="tavily",
                total_results=len(results),
                search_time_ms=elapsed
            )

        except Exception as e:
            # Fallback to DuckDuckGo on error
            if self._ddg_available:
                return await self._search_duckduckgo(query, max_results)
            raise

    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int
    ) -> SearchResponse:
        """Search using DuckDuckGo."""
        import time
        from duckduckgo_search import DDGS

        start = time.time()

        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source="duckduckgo"
                    ))
        except Exception as e:
            # Return empty results on error
            pass

        elapsed = int((time.time() - start) * 1000)

        return SearchResponse(
            query=query,
            results=results,
            provider="duckduckgo",
            total_results=len(results),
            search_time_ms=elapsed
        )

    def search_sync(
        self,
        query: str,
        max_results: int = 5
    ) -> SearchResponse:
        """Synchronous search wrapper."""
        return asyncio.get_event_loop().run_until_complete(
            self.search(query, max_results)
        )


# Convenience functions
_adapter_instance: Optional[WebSearchAdapter] = None


def get_search_adapter() -> WebSearchAdapter:
    """Get singleton search adapter."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = WebSearchAdapter()
    return _adapter_instance


async def search(query: str, max_results: int = 5) -> SearchResponse:
    """Quick search function."""
    adapter = get_search_adapter()
    return await adapter.search(query, max_results)


def search_sync(query: str, max_results: int = 5) -> SearchResponse:
    """Synchronous search function."""
    adapter = get_search_adapter()
    return adapter.search_sync(query, max_results)
