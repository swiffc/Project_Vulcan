#!/bin/bash
# Start Google Drive MCP Server

set -e

echo "📁 Starting Vulcan Google Drive Bridge..."

# Check for credentials
if [ ! -f "./secrets/gdrive-credentials.json" ]; then
    echo "❌ Error: Google Drive credentials not found"
    echo "Please place gdrive-credentials.json in ./secrets/"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    python -m venv venv
    source venv/bin/activate
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib mcp
else
    source venv/bin/activate
fi

# Start the server
python -m mcp_gdrive_server --config config.json --port 8771

echo "✅ Google Drive Bridge running on port 8771"
