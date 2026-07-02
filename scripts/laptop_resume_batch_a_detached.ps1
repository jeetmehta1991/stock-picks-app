# Batch A RESUME (detached / headless variant)
# Council 227 Q2 fix: launches engine + B1019 monitor + strategy health sidecar
# via detached Start-Process so all 3 survive if the invoking shell dies.
# NO interactive prompts (assumes owner-approved pre-flight).
#
# Usage:
#   .\scripts\laptop_resume_batch_a_detached.ps1
# Returns PIDs of all 3 background processes.

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
$BATCH_A_DIR = "$PROJECT_ROOT\output_batch_A_150"
$VENV_PYTHON = "$PROJECT_ROOT\.venv\Scripts\python.exe"

Set-Location $PROJECT_ROOT

# Pre-flight: state.json corrected
$state = Get-Content "$BATCH_A_DIR\engine_state.json" -Raw | ConvertFrom-Json
if ($state.simulated_day -ne 719 -or $state.trades_so_far -ne 5081) {
    Write-Host "PRE-FLIGHT FAIL: state.json not corrected (simulated_day=$($state.simulated_day) trades_so_far=$($state.trades_so_far))" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] state.json corrected: simulated_day=719 trades_so_far=5081" -ForegroundColor Green

# Pre-flight: files present
foreach ($f in @("$BATCH_A_DIR\trade_log_checkpoint.csv", "$BATCH_A_DIR\tickers.txt")) {
    if (-not (Test-Path $f)) {
        Write-Host "PRE-FLIGHT FAIL: $f missing" -ForegroundColor Red
        exit 1
    }
}
Write-Host "[OK] checkpoint CSV + tickers file present" -ForegroundColor Green

# Pre-flight: Python available
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "PRE-FLIGHT FAIL: $VENV_PYTHON missing" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] venv python: $VENV_PYTHON" -ForegroundColor Green

# Pre-flight: RAM
$FREE_MB = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
Write-Host "[OK] Free RAM: $FREE_MB MB" -ForegroundColor Green

# Power plan
try { powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>&1 | Out-Null } catch { }
powercfg /change standby-timeout-ac 0 2>&1 | Out-Null
powercfg /change hibernate-timeout-ac 0 2>&1 | Out-Null
Write-Host "[OK] Sleep disabled" -ForegroundColor Green

# ============================================================================
# 1. Launch ENGINE detached
# ============================================================================
$engineLog = "$BATCH_A_DIR\launch_resume.log"
$engineErr = "$BATCH_A_DIR\launch_resume_err.log"
$engineArgs = @(
    "-u",
    "-m", "backtest.run_phase1a",
    "--phase", "1a-beta",
    "--tickers-file", "$BATCH_A_DIR\tickers.txt",
    "--start", "2022-05-05",
    "--end", "2026-05-05",
    "--output-dir", "$BATCH_A_DIR",
    "--resume-from-checkpoint", "$BATCH_A_DIR",
    "--max-run-hours", "24.0",
    "--warn-run-hours", "20.0",
    "--screen-pool-workers", "1",
    "--no-news",
    "--no-git",
    "--no-walk-forward",
    "--no-agents",
    "--no-portfolio-cap",
    "--no-dd-halt"
)

Write-Host ""
Write-Host "=== Launching ENGINE (detached) ===" -ForegroundColor Cyan
$engineProc = Start-Process -FilePath $VENV_PYTHON `
    -ArgumentList $engineArgs `
    -RedirectStandardOutput $engineLog `
    -RedirectStandardError $engineErr `
    -WindowStyle Hidden `
    -PassThru `
    -WorkingDirectory $PROJECT_ROOT
Write-Host "  Engine PID: $($engineProc.Id)" -ForegroundColor Green
Write-Host "  Log: $engineLog" -ForegroundColor Gray
Write-Host "  Err: $engineErr" -ForegroundColor Gray

# ============================================================================
# 2. Launch B1019 MONITOR detached
# ============================================================================
$monitorLog = "$BATCH_A_DIR\b1019_monitor_resume.log"
$monitorErr = "$BATCH_A_DIR\b1019_monitor_resume_err.log"
$monitorArgs = @(
    "-u",
    "scripts/b1019_phase_1_runtime_monitor.py",
    "--engine-state", "$BATCH_A_DIR\engine_state.json",
    "--trade-log", "$BATCH_A_DIR\trade_log_checkpoint.csv",
    "--baseline", "output_audit/fire_count_measured_b660_full_universe.json",
    "--poll-seconds", "60",
    "--total-days", "1044",
    "--total-cells", "850",
    "--total-tickers-active", "150",
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
Write-Host "  Log: $monitorLog" -ForegroundColor Gray

# ============================================================================
# 3. Launch STRATEGY HEALTH SIDECAR detached (2-hr cadence per Council 227 Q5)
# ============================================================================
$healthLog = "$BATCH_A_DIR\strategy_health_run.log"
$healthErr = "$BATCH_A_DIR\strategy_health_run_err.log"
$healthArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "scripts\laptop_strategy_health_check.ps1",
    "-BatchDir", "$BATCH_A_DIR",
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
Write-Host "  Log: $healthLog" -ForegroundColor Gray

# ============================================================================
# Persist PIDs for later inspection
# ============================================================================
$pidsFile = "$BATCH_A_DIR\process_pids.txt"
@"
Batch A Resume - launched $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Engine PID:  $($engineProc.Id)
Monitor PID: $($monitorProc.Id)
Sidecar PID: $($healthProc.Id)

Kill all: Get-Process -Id $($engineProc.Id),$($monitorProc.Id),$($healthProc.Id) -EA SilentlyContinue | Stop-Process -Force
"@ | Out-File -FilePath $pidsFile -Encoding utf8

Write-Host ""
Write-Host "=== ALL 3 PROCESSES DETACHED ===" -ForegroundColor Green
Write-Host "PIDs written to: $pidsFile"
Write-Host ""
Write-Host "Expected wall-clock: ~2.5 hr (~325 remaining sim_days at 2.1 days/min)"
Write-Host "Projected completion: $((Get-Date).AddMinutes(150).ToString('yyyy-MM-dd HH:mm:ss'))"
Write-Host ""
Write-Host "Health check (any time): .\scripts\laptop_health_check.ps1 -BatchDir $BATCH_A_DIR" -ForegroundColor Cyan
Write-Host "Verify completion: Test-Path $BATCH_A_DIR\backtest_results.json" -ForegroundColor Cyan
