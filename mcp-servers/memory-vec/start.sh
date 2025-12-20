#!/bin/bash
# Start Memory Brain MCP Server

set -e

echo "🧠 Starting Vulcan Memory Brain..."

# Ensure data directory exists
mkdir -p ./data/vulcan-memory

# Install dependencies if needed
if [ ! -d "venv" ]; then
    python -m venv venv
    source venv/bin/activate
    pip install chromadb mcp anthropic
else
    source venv/bin/activate
fi

# Start the server
python -m mcp_memory_server --config config.json --port 8770

echo "✅ Memory Brain running on port 8770"
