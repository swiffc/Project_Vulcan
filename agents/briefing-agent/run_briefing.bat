@echo off
REM Project Vulcan - Run Daily Briefing
REM Generates Good Morning report

cd /d "%~dp0..\.."
set PYTHONPATH=%CD%

echo Generating Daily Briefing...
python agents/briefing-agent/src/daily.py

if errorlevel 1 (
    echo Error generating briefing
    pause
    exit /b 1
)

echo Done. Report saved to storage/briefings/latest.md
pause
