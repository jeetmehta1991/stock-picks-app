# Batch A Laptop Launch (Path Y: pool=1 keep all Quiver feeds; 150 stratified tickers)
# Owner directive 2026-07-01: NO AWS, laptop only, ~15-18 hr Batch A wall-clock
# Council 224 verdict: pool=1 + --tickers-file + local monitoring
#
# Usage: Right-click PowerShell -> Run as Administrator, then:
#   cd C:\Users\jeetm\Github\stock-picks-app
#   .\scripts\laptop_launch_batch_a.ps1

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
$BATCH_A_DIR = "output_batch_A_150"
$TICKERS_FILE = "$BATCH_A_DIR\tickers.txt"
$LOG_FILE = "$BATCH_A_DIR\launch.log"

Set-Location $PROJECT_ROOT

# Pre-flight checks
if (-not (Test-Path $TICKERS_FILE)) {
    Write-Host "ERROR: $TICKERS_FILE not found. Run ticker prep first." -ForegroundColor Red
    exit 1
}

$FREE_MB = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
Write-Host "Free memory: $FREE_MB MB" -ForegroundColor Yellow
if ($FREE_MB -lt 6500) {
    Write-Host "WARNING: Free memory below 6500 MB. Engine may swap or crash." -ForegroundColor Yellow
    Write-Host "Continue? (y/n)" -ForegroundColor Yellow
    $confirm = Read-Host
    if ($confirm -ne "y") { exit 0 }
}

# Set high performance power plan
try {
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>&1 | Out-Null
    Write-Host "Power plan: High performance active" -ForegroundColor Green
} catch { }

# Prevent sleep during run
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 30
Write-Host "Sleep/hibernate disabled" -ForegroundColor Green

# Launch info
Write-Host ""
Write-Host "=== Launching Batch A ===" -ForegroundColor Cyan
Write-Host "Tickers: 150 stratified (50 T1a + 50 T3 + 30 T2 + 15 T1c + 5 T1ETF)"
Write-Host "Pool workers: 1 (safe for 7-10 GB free RAM)"
Write-Host "Window: 2022-05-05 to 2026-05-05 (4y)"
Write-Host "Output: $BATCH_A_DIR"
Write-Host "Expected wall-clock: 15-18 hr"
Write-Host ""
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
Write-Host ""
Write-Host "TIP: Open a second PowerShell window and run every 30 min:" -ForegroundColor Cyan
Write-Host "  .\scripts\laptop_health_check.ps1 -BatchDir $BATCH_A_DIR" -ForegroundColor Cyan
Write-Host ""

# Arm B1019 runtime monitor as background job (Council 224 gap-fix 2026-07-01)
# Watches engine_state.json + trade_log_checkpoint.csv; emits WARN/HALT tiers
# on fire-rate anomaly (A1), schema violation (B2), progress stall (D1),
# silent-strategy floor (E-NEW), regime coverage gap (F-NEW).
Write-Host "Arming B1019 runtime monitor as background job..." -ForegroundColor Cyan
$monitorLog = "$BATCH_A_DIR\b1019_monitor.log"
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
        --total-days 1006 `
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
    Write-Host "  [OK] B1019 monitor armed (JobId $($monitorJob.Id)); log: $monitorLog" -ForegroundColor Green
} else {
    Write-Host "  [WARN] B1019 monitor job did not start; check manually" -ForegroundColor Yellow
}
Write-Host ""

# Run engine with --tickers-file (Council 224: bypasses 8191-char cmd limit)
# Batch 394 guard: raised 6.0 -> 24.0 hr for laptop mode (owner-approved 2026-07-02
# after original 6.0 killed Batch A at day=720/1044).
python -m backtest.run_phase1a `
    --phase 1a-beta `
    --tickers-file $TICKERS_FILE `
    --start 2022-05-05 `
    --end 2026-05-05 `
    --output-dir $BATCH_A_DIR `
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

# Batch 1093 Q1 fix (Council 227 2026-07-02): exit-code aware cleanup
$ENGINE_EXIT = $LASTEXITCODE
Write-Host ""
Write-Host "Ended: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

if ($ENGINE_EXIT -eq 0) {
    Write-Host "=== Batch A Complete (exit 0 - clean) ===" -ForegroundColor Green
} elseif ($ENGINE_EXIT -eq 1) {
    $tailStr = (Get-Content $LOG_FILE -Tail 15 -ErrorAction SilentlyContinue) -join "`n"
    if ($tailStr -match "WALL-TIME KILL") {
        Write-Host "=== Batch A HALTED: wall-time guard (exit 1). Resume: .\scripts\laptop_resume_batch_a.ps1 ===" -ForegroundColor Red
    } elseif ($tailStr -match "MemoryError|OutOfMemory") {
        Write-Host "=== Batch A HALTED: OOM (exit 1) ===" -ForegroundColor Red
    } elseif ($tailStr -match "Traceback") {
        Write-Host "=== Batch A HALTED: unhandled exception (exit 1); see $LOG_FILE ===" -ForegroundColor Red
    } else {
        Write-Host "=== Batch A FAILED (exit 1, unknown cause); see $LOG_FILE ===" -ForegroundColor Red
    }
} else {
    Write-Host "=== Batch A UNEXPECTED EXIT: $ENGINE_EXIT ===" -ForegroundColor Red
}

# Stop B1019 monitor cleanly
$monitorJob = Get-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
if ($monitorJob) {
    Write-Host "Stopping B1019 monitor job..." -ForegroundColor Cyan
    Stop-Job -Name "B1019Monitor" -ErrorAction SilentlyContinue
    Remove-Job -Name "B1019Monitor" -Force -ErrorAction SilentlyContinue
    Write-Host "  B1019 monitor log: $BATCH_A_DIR\b1019_monitor.log" -ForegroundColor Green
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Verify $BATCH_A_DIR\engine.log tail shows day=2026-05-04 or 2026-05-05"
Write-Host "  2. Verify $BATCH_A_DIR\trade_log.parquet OR trade_log.csv exists with rows"
Write-Host "  3. Verify $BATCH_A_DIR\backtest_results.json exists"
Write-Host "  4. Run merge dry-run: .\scripts\laptop_merge_dryrun.ps1"
Write-Host "  5. If merge dry-run PASSES, launch Batch B: .\scripts\laptop_launch_batch_b.ps1"
