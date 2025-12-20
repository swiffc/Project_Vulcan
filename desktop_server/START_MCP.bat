@echo off
REM Project Vulcan - Desktop Control MCP Server Startup
REM Use this to start the MCP-compliant server

echo ============================================
echo Project Vulcan - MCP Desktop Server
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    pause
    exit /b 1
)

cd /d "%~dp0"

REM Config Venv
if not exist "venv" (
    echo Creating venv...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.

echo Starting MCP Server...
echo Press Ctrl+C to stop
echo.

python mcp_server.py

pause
