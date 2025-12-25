# Project Vulcan - Git Pull Script
# Pull latest changes from GitHub

$folder = "C:\Users\D&E Cornealius\Documents\GitHub\Project_Vulcan"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   VULCAN GIT PULL" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $folder

# Show current status
Write-Host "Current branch: " -NoNewline
git branch --show-current
Write-Host ""

# Check for local changes
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️  Local changes detected:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    Write-Host "Stashing local changes..." -ForegroundColor Yellow
    git stash
    $stashed = $true
} else {
    $stashed = $false
}

# Fetch and pull
Write-Host "Fetching from origin..." -ForegroundColor Gray
git fetch origin

Write-Host "Pulling latest..." -ForegroundColor Gray
$result = git pull origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully pulled latest changes!" -ForegroundColor Green
    Write-Host ""
    
    # Show what changed
    Write-Host "Recent commits:" -ForegroundColor Cyan
    git log --oneline -5
} else {
    Write-Host ""
    Write-Host "❌ Pull failed:" -ForegroundColor Red
    Write-Host $result
}

# Restore stashed changes if any
if ($stashed) {
    Write-Host ""
    Write-Host "Restoring stashed changes..." -ForegroundColor Yellow
    git stash pop
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DONE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
