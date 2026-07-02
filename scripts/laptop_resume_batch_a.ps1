# Batch A RESUME (B1076 recovery from Batch 394 6-hr guard kill 2026-07-01)
# Owner directive 2026-07-02: resume from checkpoint after wall-time guard fired at day=720/1044
# Pre-condition: engine_state.json manually corrected to simulated_day=719 (matches CSV max_exit=2025-02-05)
#
# Usage: Right-click PowerShell -> Run as Administrator, then:
#   cd C:\Users\jeetm\Github\stock-picks-app
#   .\scripts\laptop_resume_batch_a.ps1

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
$BATCH_A_DIR = "output_batch_A_150"
$TICKERS_FILE = "$BATCH_A_DIR\tickers.txt"
$LOG_FILE = "$BATCH_A_DIR\launch_resume.log"

Set-Location $PROJECT_ROOT

# Pre-flight: verify state.json was corrected
$state = Get-Content "$BATCH_A_DIR\engine_state.json" -Raw | ConvertFrom-Json
if ($state.simulated_day -ne 719) {
    Write-Host "ERROR: engine_state.json simulated_day is $($state.simulated_day), expected 719." -ForegroundColor Red
    Write-Host "Run recovery patch first (see 2026-07-02 recovery notes)." -ForegroundColor Red
    exit 1
}
if ($state.trades_so_far -ne 5081) {
    Write-Host "ERROR: engine_state.json trades_so_far is $($state.trades_so_far), expected 5081." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] state.json corrected: simulated_day=719 trades_so_far=5081" -ForegroundColor Green

# Pre-flight: verify checkpoint CSV present
if (-not (Test-Path "$BATCH_A_DIR\trade_log_checkpoint.csv")) {
    Write-Host "ERROR: trade_log_checkpoint.csv missing at $BATCH_A_DIR" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] trade_log_checkpoint.csv present" -ForegroundColor Green

# Pre-flight: verify tickers file present
if (-not (Test-Path $TICKERS_FILE)) {
    Write-Host "ERROR: $TICKERS_FILE not found" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] tickers file present" -ForegroundColor Green

$FREE_MB = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
Write-Host "Free memory: $FREE_MB MB" -ForegroundColor Yellow
if ($FREE_MB -lt 5000) {
    Write-Host "WARNING: Free memory below 5000 MB. Continue? (y/n)" -ForegroundColor Yellow
    $confirm = Read-Host
    if ($confirm -ne "y") { exit 0 }
}

# Power plan
try {
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>&1 | Out-Null
} catch { }
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0

Write-Host ""
Write-Host "=== RESUMING Batch A from day=720 ===" -ForegroundColor Cyan
Write-Host "Prior progress: 719/1044 fully processed (5081 trades captured)"
Write-Host "Remaining: ~325 sim_days (720 -> 1044)"
Write-Host "Wall-clock guard: 24.0 hr (was 6.0 default; caused prior kill)"
Write-Host "Expected wall-clock: ~2.5 hr at 2.1 sim_days/min"
Write-Host ""
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
Write-Host ""

# Arm B1019 runtime monitor (same as original launch script)
Write-Host "Arming B1019 runtime monitor..." -ForegroundColor Cyan
$monitorLog = "$BATCH_A_DIR\b1019_monitor_resume.log"
$engineStatePath = "$BATCH_A_DIR\engine_state.json"
$tradeLogPath = "$BATCH_A_DIR\trade_log_checkpoint.csv"

Start-Job -Name "B1019Monitor" -ScriptBlock {
    param($EngState, $TradeLog, $Log, $ProjectRoot, $BatchDir)
    Set-Location $ProjectRoot
    python -u scripts/b1019_phase_1_runtime_monitor.py `
        --engine-state $EngState `
        --trade-log $TradeLog `
        --baseline output_audit/fire_count_measured_b660_full_universe.json `
        --poll-seconds 60 `
        --total-days 1044 `
        --total-cells 850 `
        --total-tickers-active 150 `
        --baseline-universe-size 503 `
        --baseline-window-start 2020-01-01 `
        --baseline-window-end 2026-01-01 `
        --phase-window-start 2022-05-05 `
        --phase-window-end 2026-05-05 `
        *> $Log
} -ArgumentList $engineStatePath, $tradeLogPath, $monitorLog, $PROJECT_ROOT, $BATCH_A_DIR | Out-Null

Start-Sleep -Seconds 2
$monitorJob = Get-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
if ($monitorJob -and $monitorJob.State -eq "Running") {
    Write-Host "  [OK] B1019 monitor armed (JobId $($monitorJob.Id))" -ForegroundColor Green
} else {
    Write-Host "  [WARN] B1019 monitor job did not start; engine will still proceed" -ForegroundColor Yellow
}
Write-Host ""

# Run engine with --resume-from-checkpoint + --max-run-hours 24.0
# B1076 resume: reads engine_state.json (simulated_day=719) + trade_log_checkpoint.csv (5081 trades)
# Batch 394 guard: raised from 6.0 -> 24.0 to prevent recurrence
python -m backtest.run_phase1a `
    --phase 1a-beta `
    --tickers-file $TICKERS_FILE `
    --start 2022-05-05 `
    --end 2026-05-05 `
    --output-dir $BATCH_A_DIR `
    --resume-from-checkpoint $BATCH_A_DIR `
    --max-run-hours 24.0 `
    --warn-run-hours 20.0 `
    --screen-pool-workers 1 `
    --no-news `
    --no-git `
    --no-walk-forward `
    --no-agents `
    --no-portfolio-cap `
    --no-dd-halt `
    2>&1 | Tee-Object -FilePath $LOG_FILE

# Batch 1093 Q1 fix (Council 227 2026-07-02): check engine exit code.
# Previously the launch script's post-engine cleanup treated guard-kill (exit 1)
# identically to clean-complete (exit 0), leaving owner unaware.
$ENGINE_EXIT = $LASTEXITCODE
Write-Host ""
Write-Host "Ended: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

if ($ENGINE_EXIT -eq 0) {
    Write-Host "=== Batch A Resume Complete (exit 0 - clean) ===" -ForegroundColor Green
} elseif ($ENGINE_EXIT -eq 1) {
    # Investigate cause via log tail
    $tailStr = ($LOG_FILE | ForEach-Object { Get-Content $_ -Tail 15 -ErrorAction SilentlyContinue }) -join "`n"
    if ($tailStr -match "WALL-TIME KILL") {
        Write-Host "=== Batch A Resume HALTED: engine wall-time guard fired (exit 1) ===" -ForegroundColor Red
        Write-Host "Root cause: --max-run-hours threshold hit." -ForegroundColor Red
        Write-Host "Recovery: raise --max-run-hours + re-run this script." -ForegroundColor Yellow
    } elseif ($tailStr -match "MemoryError|OutOfMemory") {
        Write-Host "=== Batch A Resume HALTED: OOM (exit 1) ===" -ForegroundColor Red
    } elseif ($tailStr -match "Traceback") {
        Write-Host "=== Batch A Resume HALTED: unhandled exception (exit 1) ===" -ForegroundColor Red
        Write-Host "See $LOG_FILE for traceback." -ForegroundColor Yellow
    } else {
        Write-Host "=== Batch A Resume FAILED (exit 1, unknown cause) ===" -ForegroundColor Red
        Write-Host "See $LOG_FILE tail for details." -ForegroundColor Yellow
    }
} else {
    Write-Host "=== Batch A Resume UNEXPECTED EXIT CODE: $ENGINE_EXIT ===" -ForegroundColor Red
}

# Stop B1019 monitor
$monitorJob = Get-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
if ($monitorJob) {
    Stop-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
    Remove-Job -Name "B1019Monitor" -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Verify $BATCH_A_DIR\backtest_results.json exists"
Write-Host "  2. Verify $BATCH_A_DIR\launch_resume.log tail shows 'Backtest complete' or day=2026-05-0X"
Write-Host "  3. Run merge dry-run: .\scripts\laptop_merge_dryrun.ps1"
Write-Host "  4. If PASS, launch Batch B: .\scripts\laptop_launch_batch_b.ps1"
