@echo off
echo.
echo ========================================
echo    STARTING VULCAN AUTO-SYNC WATCHER
echo ========================================
echo.
echo This will run in the background and push changes to GitHub.
echo Claude Chat will be able to see CLI updates.
echo.
echo Press any key to start...
pause >nul

powershell -ExecutionPolicy Bypass -File "%~dp0watch_and_sync.ps1"
