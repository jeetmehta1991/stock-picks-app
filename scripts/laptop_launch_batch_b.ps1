# Batch B Laptop Launch (Path Y: pool=1 keep all Quiver feeds; 1787 remaining tickers)
# Owner directive 2026-07-01: NO AWS, laptop only, ~80-100 hr Batch B wall-clock (~3.5-4 days)
# Council 224 verdict: pool=1 + --tickers-file (Batch B = 8051 chars, needs file input)
#
# PRE-CONDITION: Batch A must have completed successfully + merge dry-run PASSED
#
# Usage: Right-click PowerShell -> Run as Administrator, then:
#   cd C:\Users\jeetm\Github\stock-picks-app
#   .\scripts\laptop_launch_batch_b.ps1

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
$BATCH_A_DIR = "output_batch_A_150"
$BATCH_B_DIR = "output_batch_B_1787"
$TICKERS_FILE = "$BATCH_B_DIR\tickers.txt"
$LOG_FILE = "$BATCH_B_DIR\launch.log"

Set-Location $PROJECT_ROOT

# Pre-flight: verify Batch A results exist
if (-not (Test-Path "$BATCH_A_DIR\backtest_results.json")) {
    Write-Host "ERROR: Batch A results not found at $BATCH_A_DIR\backtest_results.json" -ForegroundColor Red
    Write-Host "Run Batch A first: .\scripts\laptop_launch_batch_a.ps1" -ForegroundColor Red
    exit 1
}

# Pre-flight: verify merge dry-run was run
Write-Host "PRE-FLIGHT: Did the merge dry-run PASS on Batch A output? (y/n)" -ForegroundColor Yellow
$mergeOK = Read-Host
if ($mergeOK -ne "y") {
    Write-Host "STOP: run .\scripts\laptop_merge_dryrun.ps1 first" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $TICKERS_FILE)) {
    Write-Host "ERROR: $TICKERS_FILE not found." -ForegroundColor Red
    exit 1
}

$FREE_MB = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
Write-Host "Free memory: $FREE_MB MB" -ForegroundColor Yellow
if ($FREE_MB -lt 6500) {
    Write-Host "WARNING: Free memory below 6500 MB. Consider freeing more before 3-4 day run." -ForegroundColor Yellow
    Write-Host "Continue? (y/n)" -ForegroundColor Yellow
    $confirm = Read-Host
    if ($confirm -ne "y") { exit 0 }
}

# Power plan + prevent sleep
try {
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>&1 | Out-Null
} catch { }
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 30

# Launch info
Write-Host ""
Write-Host "=== Launching Batch B ===" -ForegroundColor Cyan
Write-Host "Tickers: 1787 remaining (Master 1937 - Batch A 150)"
Write-Host "Pool workers: 1"
Write-Host "Window: 2022-05-05 to 2026-05-05 (4y)"
Write-Host "Output: $BATCH_B_DIR"
Write-Host "Expected wall-clock: 80-100 hr (3.5-4 days)"
Write-Host ""
Write-Host "IMPORTANT: This run takes 3-4 days. Consider:" -ForegroundColor Yellow
Write-Host "  - Plugging in laptop (don't unplug)"
Write-Host "  - Not using laptop for other heavy work during run"
Write-Host "  - Running health check every 6-12 hours:" -ForegroundColor Yellow
Write-Host "      .\scripts\laptop_health_check.ps1 -BatchDir $BATCH_B_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
Write-Host ""

# Arm B1019 runtime monitor as background job (Council 224 gap-fix 2026-07-01)
Write-Host "Arming B1019 runtime monitor as background job..." -ForegroundColor Cyan
$monitorLog = "$BATCH_B_DIR\b1019_monitor.log"
$engineStatePath = "$BATCH_B_DIR\engine_state.json"
$tradeLogPath = "$BATCH_B_DIR\trade_log_checkpoint.csv"

Start-Job -Name "B1019Monitor" -ScriptBlock {
    param($EngState, $TradeLog, $Log, $ProjectRoot)
    Set-Location $ProjectRoot
    python -u scripts/b1019_phase_1_runtime_monitor.py `
        --engine-state $EngState `
        --trade-log $TradeLog `
        --baseline output_audit/fire_count_measured_b660_full_universe.json `
        --poll-seconds 60 `
        --total-days 1044 `
        --total-cells 5694 `
        --total-tickers-active 1787 `
        --baseline-universe-size 503 `
        --baseline-window-start 2020-01-01 `
        --baseline-window-end 2026-01-01 `
        --phase-window-start 2022-05-05 `
        --phase-window-end 2026-05-05 `
        *> $Log
} -ArgumentList $engineStatePath, $tradeLogPath, $monitorLog, $PROJECT_ROOT | Out-Null

Start-Sleep -Seconds 2
$monitorJob = Get-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
if ($monitorJob -and $monitorJob.State -eq "Running") {
    Write-Host "  [OK] B1019 monitor armed (JobId $($monitorJob.Id)); log: $monitorLog" -ForegroundColor Green
} else {
    Write-Host "  [WARN] B1019 monitor job did not start; check manually" -ForegroundColor Yellow
}
Write-Host ""

# Run engine
# Batch 394 guard: raised 6.0 -> 120.0 hr for laptop mode (was killing Batch A at 68.9%);
# owner-approved recovery 2026-07-02 after Batch A B1076 resume.
python -m backtest.run_phase1a `
    --phase 1a-beta `
    --tickers-file $TICKERS_FILE `
    --start 2022-05-05 `
    --end 2026-05-05 `
    --output-dir $BATCH_B_DIR `
    --max-run-hours 120.0 `
    --warn-run-hours 100.0 `
    --screen-pool-workers 1 `
    --no-news `
    --no-git `
    --no-walk-forward `
    --no-agents `
    --no-portfolio-cap `
    --no-dd-halt `
    2>&1 | Tee-Object -FilePath $LOG_FILE

# Batch 1093 Q1 fix (Council 227 2026-07-02): exit-code aware cleanup
$ENGINE_EXIT = $LASTEXITCODE
Write-Host ""
Write-Host "Ended: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

if ($ENGINE_EXIT -eq 0) {
    Write-Host "=== Batch B Complete (exit 0 - clean) ===" -ForegroundColor Green
} elseif ($ENGINE_EXIT -eq 1) {
    $tailStr = (Get-Content $LOG_FILE -Tail 15 -ErrorAction SilentlyContinue) -join "`n"
    if ($tailStr -match "WALL-TIME KILL") {
        Write-Host "=== Batch B HALTED: wall-time guard (exit 1). Raise --max-run-hours + resume via engine_state.json checkpoint. ===" -ForegroundColor Red
    } elseif ($tailStr -match "MemoryError|OutOfMemory") {
        Write-Host "=== Batch B HALTED: OOM (exit 1) ===" -ForegroundColor Red
    } elseif ($tailStr -match "Traceback") {
        Write-Host "=== Batch B HALTED: unhandled exception (exit 1); see $LOG_FILE ===" -ForegroundColor Red
    } else {
        Write-Host "=== Batch B FAILED (exit 1, unknown cause); see $LOG_FILE ===" -ForegroundColor Red
    }
} else {
    Write-Host "=== Batch B UNEXPECTED EXIT: $ENGINE_EXIT ===" -ForegroundColor Red
}

# Stop B1019 monitor cleanly
$monitorJob = Get-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
if ($monitorJob) {
    Write-Host "Stopping B1019 monitor job..." -ForegroundColor Cyan
    Stop-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
    Remove-Job -Name "B1019Monitor" -Force -ErrorAction SilentlyContinue
    Write-Host "  B1019 monitor log: $BATCH_B_DIR\b1019_monitor.log" -ForegroundColor Green
}
Write-Host ""
Write-Host "Next: Run final merge Batch A + Batch B into unified log" -ForegroundColor Cyan
Write-Host "  .\scripts\laptop_final_merge.ps1"
