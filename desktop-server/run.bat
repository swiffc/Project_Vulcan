@echo off
REM Project Vulcan - Desktop Control Server Startup Script
REM Run this to start the server on your Windows PC

echo ============================================
echo Project Vulcan - Desktop Control Server
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Navigate to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo Dependencies installed.
echo.

REM Check for Tailscale
echo Checking Tailscale connection...
tailscale status >nul 2>&1
if errorlevel 1 (
    echo WARNING: Tailscale is not running or not installed
    echo Server will run on localhost only
    echo.
    echo To enable remote access:
    echo 1. Install Tailscale from https://tailscale.com
    echo 2. Run 'tailscale up' to connect
    echo.
) else (
    echo Tailscale is connected.
    for /f "tokens=*" %%i in ('tailscale ip -4 2^>nul') do set TAILSCALE_IP=%%i
    if defined TAILSCALE_IP (
        echo Tailscale IP: %TAILSCALE_IP%
    )
)

echo.
echo ============================================
echo Starting Desktop Control Server...
echo ============================================
echo.
echo KILL SWITCH: Move mouse to top-left corner to stop
echo Press Ctrl+C to shut down
echo.

REM Start the server
python server.py

REM If we get here, server stopped
echo.
echo Server stopped.
pause
