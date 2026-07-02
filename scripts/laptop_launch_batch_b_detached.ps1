# Batch B DETACHED LAUNCH (Council 227 Q2 pattern; Batch 1094-A I1 2026-07-02)
# Path Y: pool=1 keep all Quiver feeds; 1787 remaining tickers; ~80-100 hr wall-clock
# Launches engine + B1019 monitor + strategy health sidecar + watchdog
# all via Start-Process detached so all survive if invoking shell dies.
# NO interactive prompts.
#
# PRE-CONDITION: Batch A completed + merge dry-run PASSED
#
# Usage:
#   .\scripts\laptop_launch_batch_b_detached.ps1

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
$BATCH_B_DIR = "$PROJECT_ROOT\output_batch_B_1787"
$BATCH_A_DIR = "$PROJECT_ROOT\output_batch_A_150"
$VENV_PYTHON = "$PROJECT_ROOT\.venv\Scripts\python.exe"

Set-Location $PROJECT_ROOT

# Pre-flight: Batch A must have completed
if (-not (Test-Path "$BATCH_A_DIR\backtest_results.json")) {
    Write-Host "PRE-FLIGHT FAIL: Batch A backtest_results.json missing at $BATCH_A_DIR" -ForegroundColor Red
    Write-Host "Run: Test-Path $BATCH_A_DIR\backtest_results.json" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Batch A backtest_results.json present" -ForegroundColor Green

# Pre-flight: Batch B tickers file
if (-not (Test-Path "$BATCH_B_DIR\tickers.txt")) {
    Write-Host "PRE-FLIGHT FAIL: $BATCH_B_DIR\tickers.txt missing" -ForegroundColor Red
    exit 1
}
$tickerCount = ((Get-Content "$BATCH_B_DIR\tickers.txt") -split ',').Count
if ($tickerCount -lt 1700) {
    Write-Host "PRE-FLIGHT FAIL: tickers.txt has $tickerCount tickers, expected 1787" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Batch B tickers: $tickerCount" -ForegroundColor Green

# Pre-flight: venv python
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "PRE-FLIGHT FAIL: $VENV_PYTHON missing" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] venv python: $VENV_PYTHON" -ForegroundColor Green

# Pre-flight: RAM (need at least 6 GB for safety)
$FREE_MB = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
if ($FREE_MB -lt 5000) {
    Write-Host "PRE-FLIGHT FAIL: Free RAM $FREE_MB MB below 5000 MB minimum" -ForegroundColor Red
    Write-Host "Close browsers / VS Code windows / OneDrive; re-run" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Free RAM: $FREE_MB MB" -ForegroundColor Green

# Pre-flight: Batch A not still running (would compete for RAM)
$AProcs = Get-Content "$BATCH_A_DIR\process_pids.txt" -ErrorAction SilentlyContinue |
          Select-String -Pattern 'PID:\s*(\d+)' | ForEach-Object { $_.Matches[0].Groups[1].Value }
$stillAlive = @()
foreach ($p in $AProcs) {
    $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
    if ($proc) { $stillAlive += $p }
}
if ($stillAlive.Count -gt 0) {
    Write-Host "PRE-FLIGHT FAIL: Batch A processes still alive: $($stillAlive -join ', ')" -ForegroundColor Red
    Write-Host "Wait for Batch A completion OR kill: Get-Process -Id $($stillAlive -join ',') | Stop-Process -Force" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] No Batch A processes competing for RAM" -ForegroundColor Green

# Power plan
try { powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>&1 | Out-Null } catch { }
powercfg /change standby-timeout-ac 0 2>&1 | Out-Null
powercfg /change hibernate-timeout-ac 0 2>&1 | Out-Null
Write-Host "[OK] Sleep disabled" -ForegroundColor Green

# ============================================================================
# 1. Launch ENGINE detached with --max-run-hours 120.0
# ============================================================================
$engineLog = "$BATCH_B_DIR\launch.log"
$engineErr = "$BATCH_B_DIR\launch_err.log"
$engineArgs = @(
    "-u",
    "-m", "backtest.run_phase1a",
    "--phase", "1a-beta",
    "--tickers-file", "$BATCH_B_DIR\tickers.txt",
    "--start", "2022-05-05",
    "--end", "2026-05-05",
    "--output-dir", "$BATCH_B_DIR",
    "--max-run-hours", "120.0",
    "--warn-run-hours", "100.0",
    "--screen-pool-workers", "1",
    "--no-news",
    "--no-git",
    "--no-walk-forward",
    "--no-agents",
    "--no-portfolio-cap",
    "--no-dd-halt"
)

Write-Host ""
Write-Host "=== Launching ENGINE (detached, --max-run-hours 120.0) ===" -ForegroundColor Cyan
$engineProc = Start-Process -FilePath $VENV_PYTHON `
    -ArgumentList $engineArgs `
    -RedirectStandardOutput $engineLog `
    -RedirectStandardError $engineErr `
    -WindowStyle Hidden `
    -PassThru `
    -WorkingDirectory $PROJECT_ROOT
Write-Host "  Engine PID: $($engineProc.Id)" -ForegroundColor Green

# ============================================================================
# 2. Launch B1019 MONITOR detached
# ============================================================================
$monitorLog = "$BATCH_B_DIR\b1019_monitor.log"
$monitorErr = "$BATCH_B_DIR\b1019_monitor_err.log"
$monitorArgs = @(
    "-u",
    "scripts/b1019_phase_1_runtime_monitor.py",
    "--engine-state", "$BATCH_B_DIR\engine_state.json",
    "--trade-log", "$BATCH_B_DIR\trade_log_checkpoint.csv",
    "--baseline", "output_audit/fire_count_measured_b660_full_universe.json",
    "--poll-seconds", "60",
    "--total-days", "1044",
    "--total-cells", "5694",
    "--total-tickers-active", "1787",
    "--baseline-universe-size", "503",
    "--baseline-window-start", "2020-01-01",
    "--baseline-window-end", "2026-01-01",
    "--phase-window-start", "2022-05-05",
    "--phase-window-end", "2026-05-05"
)

Write-Host ""
Write-Host "=== Launching B1019 MONITOR (detached) ===" -ForegroundColor Cyan
$monitorProc = Start-Process -FilePath $VENV_PYTHON `
    -ArgumentList $monitorArgs `
    -RedirectStandardOutput $monitorLog `
    -RedirectStandardError $monitorErr `
    -WindowStyle Hidden `
    -PassThru `
    -WorkingDirectory $PROJECT_ROOT
Write-Host "  Monitor PID: $($monitorProc.Id)" -ForegroundColor Green

# ============================================================================
# 3. Launch STRATEGY HEALTH SIDECAR detached (2-hr cadence)
# ============================================================================
$healthLog = "$BATCH_B_DIR\strategy_health_run.log"
$healthErr = "$BATCH_B_DIR\strategy_health_run_err.log"
$healthArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "scripts\laptop_strategy_health_check.ps1",
    "-BatchDir", "$BATCH_B_DIR",
    "-CadenceMinutes", "120"
)

Write-Host ""
Write-Host "=== Launching STRATEGY HEALTH SIDECAR (detached, 2hr cadence) ===" -ForegroundColor Cyan
$healthProc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList $healthArgs `
    -RedirectStandardOutput $healthLog `
    -RedirectStandardError $healthErr `
    -WindowStyle Hidden `
    -PassThru `
    -WorkingDirectory $PROJECT_ROOT
Write-Host "  Sidecar PID: $($healthProc.Id)" -ForegroundColor Green

# ============================================================================
# 4. Launch WATCHDOG detached (Batch 1094-A I4)
# ============================================================================
$watchdogLog = "$BATCH_B_DIR\watchdog.log"
$watchdogErr = "$BATCH_B_DIR\watchdog_err.log"
$watchdogArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "scripts\laptop_watchdog.ps1",
    "-BatchDir", "$BATCH_B_DIR",
    "-EnginePid", "$($engineProc.Id)",
    "-MaxRetries", "2",
    "-PollSeconds", "60"
)

Write-Host ""
Write-Host "=== Launching WATCHDOG (detached, auto-resume on engine death) ===" -ForegroundColor Cyan
$watchdogProc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList $watchdogArgs `
    -RedirectStandardOutput $watchdogLog `
    -RedirectStandardError $watchdogErr `
    -WindowStyle Hidden `
    -PassThru `
    -WorkingDirectory $PROJECT_ROOT
Write-Host "  Watchdog PID: $($watchdogProc.Id)" -ForegroundColor Green

# Persist PIDs
$pidsFile = "$BATCH_B_DIR\process_pids.txt"
@"
Batch B Detached Launch - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Engine PID:   $($engineProc.Id)
Monitor PID:  $($monitorProc.Id)
Sidecar PID:  $($healthProc.Id)
Watchdog PID: $($watchdogProc.Id)

Kill all: Get-Process -Id $($engineProc.Id),$($monitorProc.Id),$($healthProc.Id),$($watchdogProc.Id) -EA SilentlyContinue | Stop-Process -Force
"@ | Out-File -FilePath $pidsFile -Encoding utf8

Write-Host ""
Write-Host "=== ALL 4 PROCESSES DETACHED ===" -ForegroundColor Green
Write-Host "PIDs: $pidsFile"
Write-Host ""
Write-Host "Expected wall-clock: 80-100 hr (3.5-4 days)"
Write-Host "Projected completion: $((Get-Date).AddHours(90).ToString('yyyy-MM-dd HH:mm:ss')) (~90 hr midpoint)"
Write-Host ""
Write-Host "Watchdog will auto-restart engine up to 2 times if it dies unexpectedly."
Write-Host "Health check any time: .\scripts\laptop_health_check.ps1 -BatchDir $BATCH_B_DIR"
