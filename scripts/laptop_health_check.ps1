# Local Health Check for Laptop Batch Run (adapted 7 sentinels; no S3)
# Run every 30 min during batch execution to detect problems early.
#
# Usage:
#   .\scripts\laptop_health_check.ps1 -BatchDir output_batch_A_150
#
# Exit codes:
#   0 = healthy (batch progressing)
#   1 = TERMINATE (fatal error detected)
#   2 = WARN (attention needed but not fatal)

param(
    [string]$BatchDir = "output_batch_A_150"
)

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
Set-Location $PROJECT_ROOT

Write-Host "=== Laptop Health Check ($(Get-Date -Format 'HH:mm:ss')) ===" -ForegroundColor Cyan
Write-Host "Batch dir: $BatchDir"

$WARN = 0
$FATAL = 0

# Check 1: Python engine process alive
$engineProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*run_phase1a*" -or $_.Path -like "*python*"} | Select-Object -First 1
if (-not $engineProcess) {
    # Check if any python running
    $anyPy = Get-Process python -ErrorAction SilentlyContinue
    if (-not $anyPy) {
        Write-Host "  [FATAL] No python process running" -ForegroundColor Red
        $FATAL++
    } else {
        Write-Host "  [WARN] Cannot identify engine process; found $($anyPy.Count) python instances" -ForegroundColor Yellow
        $WARN++
    }
} else {
    Write-Host "  [OK] Engine process alive (PID $($engineProcess.Id))" -ForegroundColor Green
}

# Check 2: engine.log activity (last write within 15 min)
$engineLog = "$BatchDir\engine.log"
if (Test-Path $engineLog) {
    $lastWrite = (Get-Item $engineLog).LastWriteTime
    $minsAgo = ((Get-Date) - $lastWrite).TotalMinutes
    if ($minsAgo -gt 15) {
        Write-Host "  [FATAL] engine.log last updated $([math]::Round($minsAgo,1)) min ago (>15 min = stuck)" -ForegroundColor Red
        $FATAL++
    } else {
        Write-Host "  [OK] engine.log active (last write $([math]::Round($minsAgo,1)) min ago)" -ForegroundColor Green
    }
} else {
    Write-Host "  [WARN] engine.log not yet created" -ForegroundColor Yellow
    $WARN++
}

# Check 3: engine.log size > 0 bytes (B1019 PIVOT #34 regression check)
if (Test-Path $engineLog) {
    $size = (Get-Item $engineLog).Length
    if ($size -eq 0) {
        Write-Host "  [FATAL] engine.log is 0 bytes (B1019 PIVOT #34 buffering regression)" -ForegroundColor Red
        $FATAL++
    } else {
        Write-Host "  [OK] engine.log size: $([math]::Round($size/1KB,1)) KB" -ForegroundColor Green
    }
}

# Check 4: engine_state.json progress
$stateFile = "$BatchDir\engine_state.json"
if (Test-Path $stateFile) {
    $state = Get-Content $stateFile -Raw | ConvertFrom-Json
    Write-Host "  [OK] sim_day=$($state.simulated_day) trades=$($state.trades_so_far) status=$($state.status)" -ForegroundColor Green
    if ($state.status -eq "failed" -or $state.status -eq "crashed") {
        Write-Host "  [FATAL] engine_state.status = $($state.status)" -ForegroundColor Red
        $FATAL++
    }
} else {
    Write-Host "  [INFO] engine_state.json not yet emitted (engine still bootstrapping)" -ForegroundColor Gray
}

# Check 5: Free RAM > 2 GB (headroom for spikes)
$freeMB = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
if ($freeMB -lt 1000) {
    Write-Host "  [FATAL] Free RAM $freeMB MB (< 1 GB = imminent swap disaster)" -ForegroundColor Red
    $FATAL++
} elseif ($freeMB -lt 2000) {
    Write-Host "  [WARN] Free RAM $freeMB MB (< 2 GB headroom)" -ForegroundColor Yellow
    $WARN++
} else {
    Write-Host "  [OK] Free RAM: $freeMB MB" -ForegroundColor Green
}

# Check 6: Recent engine.log content contains PHASE_TIMING (not stuck in bootstrap)
if (Test-Path $engineLog) {
    $recent = Get-Content $engineLog -Tail 20 -ErrorAction SilentlyContinue
    if ($recent -match "PHASE_TIMING day=") {
        Write-Host "  [OK] Engine actively processing sim_days" -ForegroundColor Green
    } elseif ($recent -match "Loaded Quiver bulk feed") {
        # Count Quiver load repetitions - if >5, engine may be in load loop (PIVOT #48)
        $loadCount = ($recent | Select-String "Loaded Quiver bulk feed").Count
        if ($loadCount -gt 10) {
            Write-Host "  [FATAL] Engine stuck in Quiver load loop ($loadCount repetitions - PIVOT #48 pattern)" -ForegroundColor Red
            $FATAL++
        } else {
            Write-Host "  [INFO] Engine loading Quiver bulk feeds (normal bootstrap phase)" -ForegroundColor Gray
        }
    } elseif ($recent -match "MemoryError|OutOfMemory") {
        Write-Host "  [FATAL] Memory error detected in engine.log" -ForegroundColor Red
        $FATAL++
    } elseif ($recent -match "Traceback") {
        Write-Host "  [FATAL] Traceback detected in engine.log" -ForegroundColor Red
        $FATAL++
    }
}

# Check 7: exit_method schema drift (B1062 PIVOT #37 regression check)
$tradeLog = "$BatchDir\trade_log.csv"
if (Test-Path $tradeLog) {
    $header = Get-Content $tradeLog -TotalCount 1
    if ($header -notmatch "exit_reason") {
        Write-Host "  [FATAL] trade_log missing 'exit_reason' column (B1062 PIVOT #37 regression)" -ForegroundColor Red
        $FATAL++
    } else {
        Write-Host "  [OK] trade_log schema OK" -ForegroundColor Green
    }
}

# Summary
Write-Host ""
if ($FATAL -gt 0) {
    Write-Host "TERMINATE - $FATAL fatal error(s). Kill engine process:" -ForegroundColor Red
    Write-Host "  Get-Process python | Stop-Process -Force" -ForegroundColor Red
    exit 1
} elseif ($WARN -gt 0) {
    Write-Host "WARN - $WARN warning(s). Monitor closely." -ForegroundColor Yellow
    exit 2
} else {
    Write-Host "HEALTHY - all checks passed." -ForegroundColor Green
    exit 0
}
