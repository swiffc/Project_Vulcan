"""
Web Search Module for Project Vulcan

Provides unified web search capabilities using:
- Tavily API (preferred, requires API key)
- DuckDuckGo (free fallback)
- Claude API web_search tool (when available)
"""

from .adapter import WebSearchAdapter, SearchResult, search
from .research_agent import ResearchAgent, ResearchResult

__all__ = [
    "WebSearchAdapter",
    "SearchResult",
    "search",
    "ResearchAgent",
    "ResearchResult",
]
