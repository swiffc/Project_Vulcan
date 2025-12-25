import json
import logging
import os
import chromadb
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from chromadb.utils import embedding_functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vulcan-memory-brain")

# Initialize FastMCP Server
mcp = FastMCP("vulcan-memory-brain")

# ChromaDB Setup
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/vulcan-memory")
client = chromadb.PersistentClient(path=DATA_PATH)

# Use a default embedding function (e.g., Sentence Transformers if available locally, or rely on OpenAI if configured)
# For elite local performance without API keys effectively, we use 'all-MiniLM-L6-v2' via sentence-transformers
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="vulcan_knowledge", embedding_function=ef
)


@mcp.tool()
async def memory_store(key: str, content: str, metadata: Dict[str, Any] = {}) -> str:
    """Store a memory item."""
    try:
        collection.upsert(documents=[content], metadatas=[metadata], ids=[key])
        return f"Stored memory: {key}"
    except Exception as e:
        return f"Error storing memory: {str(e)}"


@mcp.tool()
async def memory_search(query: str, limit: int = 5) -> str:
    """Search for relevant memories."""
    try:
        results = collection.query(query_texts=[query], n_results=limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching memory: {str(e)}"


@mcp.tool()
async def memory_delete(key: str) -> str:
    """Delete a memory item."""
    try:
        collection.delete(ids=[key])
        return f"Deleted memory: {key}"
    except Exception as e:
        return f"Error deleting memory: {str(e)}"


@mcp.resource("vulcan://memory/stats")
async def get_stats() -> str:
    """Return memory statistics."""
    count = collection.count()
    return json.dumps({"total_memories": count})


if __name__ == "__main__":
    mcp.run()
