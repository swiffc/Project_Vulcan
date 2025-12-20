# Project Vulcan - Auto Sync Watcher
# Runs in background and pushes changes to GitHub automatically
# This lets Claude Chat see what Claude CLI is building

$folder = "C:\Users\DCornealius\Documents\GitHub\Project_Vulcan"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   VULCAN AUTO-SYNC WATCHER" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Watching: $folder" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Track last sync time to avoid duplicate pushes
$lastSync = Get-Date
$syncCooldown = 30  # seconds between syncs

function Sync-ToGitHub {
    $now = Get-Date
    $elapsed = ($now - $script:lastSync).TotalSeconds
    
    # Only sync if cooldown passed
    if ($elapsed -lt $syncCooldown) {
        return
    }
    
    Set-Location $folder
    
    # Check if there are changes
    $status = git status --porcelain
    if ($status) {
        Write-Host "[$now] Changes detected..." -ForegroundColor Gray
        
        git add . 2>$null
        $msg = "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $msg 2>$null
        
        $result = git push origin main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$now] ✅ Pushed to GitHub" -ForegroundColor Green
        } else {
            Write-Host "[$now] ⚠️ Push failed (might need to pull first)" -ForegroundColor Yellow
        }
        
        $script:lastSync = $now
    }
}

# Set up file watcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folder
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, DirectoryName'

# Exclude patterns (don't trigger on these)
$excludePatterns = @('.git', 'node_modules', 'venv', '__pycache__', '.pyc')

$action = {
    $path = $Event.SourceEventArgs.FullPath
    
    # Skip excluded patterns
    foreach ($pattern in $excludePatterns) {
        if ($path -like "*$pattern*") { return }
    }
    
    # Wait a moment for file to finish writing
    Start-Sleep -Seconds 3
    Sync-ToGitHub
}

# Register events
Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
Register-ObjectEvent $watcher "Created" -Action $action | Out-Null
Register-ObjectEvent $watcher "Deleted" -Action $action | Out-Null
Register-ObjectEvent $watcher "Renamed" -Action $action | Out-Null

Write-Host "👀 Watcher is running..." -ForegroundColor Green
Write-Host ""

# Keep script running
try {
    while ($true) { 
        Start-Sleep -Seconds 10
        
        # Also do periodic sync check every 60 seconds
        Sync-ToGitHub
    }
} finally {
    # Cleanup on exit
    Get-EventSubscriber | Unregister-Event
    $watcher.Dispose()
    Write-Host ""
    Write-Host "Watcher stopped." -ForegroundColor Yellow
}
