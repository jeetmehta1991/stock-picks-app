# Run Quiver pre-fetch from VS Code terminal (PowerShell)
# Usage: .\scripts\run_quiver_vscode.ps1
#
# Runs from your laptop where Quiver API is accessible.
# Resumes from checkpoint — safe to interrupt and restart.

Write-Host "=== Quiver Pre-fetch Script ===" -ForegroundColor Cyan

# Check for uncommitted changes first
$status = git status --porcelain
if ($status) {
    Write-Host "WARNING: Uncommitted changes found. Committing before proceeding..." -ForegroundColor Yellow
    git add backtest/data/cache/quiver/
    git add backtest/data/cache/quiver_checkpoint.json
    git commit -m "Quiver cache: auto-commit before sync"
    git push origin main
}

# Sync with main
Write-Host "Syncing with main..." -ForegroundColor Cyan
git fetch origin
git reset --hard origin/main

# Check API key
if (-not $env:QUIVER_API_KEY) {
    Write-Host "ERROR: QUIVER_API_KEY not set. Run: `$env:QUIVER_API_KEY='your-key'" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Quiver pre-fetch (resumes from checkpoint)..." -ForegroundColor Green
python scripts/prefetch_quiver.py

# Commit everything after completion
Write-Host "Committing final results..." -ForegroundColor Cyan
git status --porcelain
git add backtest/data/cache/quiver/
git add backtest/data/cache/quiver_checkpoint.json
git commit -m "Quiver cache: all data types complete"
git push origin main

Write-Host "=== Complete ===" -ForegroundColor Green
