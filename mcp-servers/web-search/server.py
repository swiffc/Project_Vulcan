import json
import logging
import os
from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS

# Try importing Tavily, handle if missing
try:
    from tavily import TavilyClient

    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vulcan-web-search")

# Initialize FastMCP Server
mcp = FastMCP("vulcan-web-search")


def get_tavily_client():
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)


@mcp.tool()
async def web_search_duckduckgo(query: str, max_results: int = 5) -> str:
    """
    Perform a web search using DuckDuckGo (Free, no API key required).
    Good for quick lookups and general knowledge.
    """
    try:
        results = []
        with DDGS() as ddgs:
            # text() returns a generator, we take max_results
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error performing DuckDuckGo search: {str(e)}"


@mcp.tool()
async def web_search_tavily(
    query: str, search_depth: str = "basic", include_answer: bool = False
) -> str:
    """
    Perform a deep web search using Tavily (Requires TAVILY_API_KEY).
    Optimized for LLM context retrieval.

    Args:
        query: The search query
        search_depth: "basic" or "advanced"
        include_answer: Whether to include a generated answer
    """
    if not TAVILY_AVAILABLE:
        return "Error: 'tavily-python' library not installed."

    client = get_tavily_client()
    if not client:
        return "Error: TAVILY_API_KEY not found in environment variables."

    try:
        response = client.search(
            query=query,
            search_depth=search_depth,
            include_answer=include_answer,
            max_results=5,
        )
        return json.dumps(response, indent=2)
    except Exception as e:
        return f"Error performing Tavily search: {str(e)}"


@mcp.tool()
async def web_news_search(query: str, max_results: int = 5) -> str:
    """
    Search for latest news articles using DuckDuckGo.
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append(r)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error performing News search: {str(e)}"


if __name__ == "__main__":
    mcp.run()
