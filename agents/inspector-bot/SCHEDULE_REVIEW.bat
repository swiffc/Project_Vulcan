@echo off
echo Scheduling Vulcan Weekly Review...
echo Job: VulcanWeeklyReview
echo Schedule: Every Friday at 17:00
echo Script: %~dp0run_review.bat

schtasks /create /tn "VulcanWeeklyReview" /tr "%~dp0run_review.bat" /sc weekly /d FRI /st 17:00 /f

if errorlevel 1 (
    echo Error scheduling task. Try running as Administrator.
    pause
    exit /b 1
)

echo Task scheduled successfully!
pause
