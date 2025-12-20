@echo off
cd /d "%~dp0"
if exist ".next" rd /s /q ".next"
npm run dev
