@echo off
echo.
echo ========================================
echo    PULLING LATEST FROM GITHUB
echo ========================================
echo.

cd /d "C:\Users\D&E Cornealius\Documents\GitHub\Project_Vulcan"

echo Current branch:
git branch --show-current
echo.

echo Fetching updates...
git fetch origin

echo.
echo Pulling latest...
git pull origin main

echo.
echo ========================================
echo    DONE!
echo ========================================
echo.
pause
