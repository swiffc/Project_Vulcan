@echo off
REM Project Vulcan - Start Desktop Server (with Watchdog)
REM This is the recommended way to start the server for long-running sessions.

cd /d "%~dp0"

if not exist venv (
    echo Creating python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Starting Vulcan Watchdog...
python watchdog.py

pause
