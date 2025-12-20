@echo off
REM Project Vulcan - Run Judge Agent
REM Audits recent logs using LLM

cd /d "%~dp0..\.."
set PYTHONPATH=%CD%

echo Running Judge Agent (LLM-as-a-Judge)...
python agents/review-agent/src/judge.py

if errorlevel 1 (
    echo Error running judge
    pause
    exit /b 1
)

echo Done.
pause
