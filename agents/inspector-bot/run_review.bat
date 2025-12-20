@echo off
REM Project Vulcan - Run Weekly Review
REM This script is called by the Task Scheduler

cd /d "%~dp0..\.."
set PYTHONPATH=%CD%

echo Running Weekly Review...
echo Project Root: %CD%

python agents/review-agent/src/weekly_review.py

if errorlevel 1 (
    echo Error running review
    exit /b 1
)

echo Done.
