@echo off
set "PYTHON_PATH=C:\Users\DCornealius\AppData\Local\Programs\Python\Python311\python.exe"

echo "Installing ALL dependencies from requirements.txt..."
"%PYTHON_PATH%" -m pip install -r requirements.txt

echo "Ensuring MCP specific packages are present..."
"%PYTHON_PATH%" -m pip install mcp google-auth-oauthlib google-api-python-client chromadb sentence-transformers duckduckgo_search tavily-python

echo "Dependencies installed successfully."
pause
