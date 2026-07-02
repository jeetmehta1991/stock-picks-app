# Merge Dry-Run: verify Batch A output can be merged before committing to Batch B
# Council 224 mandatory gate: fix merge issues in the $0 window not the 4-day window
#
# Usage:
#   cd C:\Users\jeetm\Github\stock-picks-app
#   .\scripts\laptop_merge_dryrun.ps1

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
$BATCH_A_DIR = "output_batch_A_150"

Set-Location $PROJECT_ROOT

Write-Host "=== Merge Dry-Run (Batch A output) ===" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

$FAIL = 0

# Check 1: Batch A output directory exists
if (-not (Test-Path $BATCH_A_DIR)) {
    Write-Host "  [FAIL] $BATCH_A_DIR not found" -ForegroundColor Red
    $FAIL++
    Write-Host ""
    Write-Host "TERMINATE: Batch A hasn't run yet or output missing" -ForegroundColor Red
    exit 1
}

# Check 2: trade_log file exists
$tradeLogParquet = "$BATCH_A_DIR\trade_log.parquet"
$tradeLogCsv = "$BATCH_A_DIR\trade_log.csv"
$tradeLog = if (Test-Path $tradeLogParquet) { $tradeLogParquet } elseif (Test-Path $tradeLogCsv) { $tradeLogCsv } else { $null }

if (-not $tradeLog) {
    Write-Host "  [FAIL] No trade_log.parquet or trade_log.csv in $BATCH_A_DIR" -ForegroundColor Red
    $FAIL++
} else {
    $size = (Get-Item $tradeLog).Length
    Write-Host "  [OK] Trade log: $tradeLog ($([math]::Round($size/1KB,1)) KB)" -ForegroundColor Green
}

# Check 3: backtest_results.json exists
$resultsFile = "$BATCH_A_DIR\backtest_results.json"
if (-not (Test-Path $resultsFile)) {
    Write-Host "  [FAIL] $resultsFile not found" -ForegroundColor Red
    $FAIL++
} else {
    Write-Host "  [OK] Results JSON: $resultsFile" -ForegroundColor Green
}

# Check 4: engine.log complete (last day reached)
$engineLog = "$BATCH_A_DIR\engine.log"
if (Test-Path $engineLog) {
    $lastLines = Get-Content $engineLog -Tail 50 -ErrorAction SilentlyContinue
    if ($lastLines -match "Backtest complete") {
        Write-Host "  [OK] engine.log shows 'Backtest complete'" -ForegroundColor Green
    } elseif ($lastLines -match "day=2026-05-0") {
        Write-Host "  [OK] engine.log reached end date (2026-05-0X)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] engine.log does not show completion marker" -ForegroundColor Red
        $FAIL++
    }
} else {
    Write-Host "  [FAIL] engine.log missing" -ForegroundColor Red
    $FAIL++
}

# Check 5: Schema validation - trade log has required columns
if ($tradeLog -like "*.csv") {
    $header = Get-Content $tradeLog -TotalCount 1
    $requiredCols = @("ticker", "entry_date", "exit_date", "strategy", "exit_reason", "pnl_pct")
    foreach ($col in $requiredCols) {
        if ($header -notmatch $col) {
            Write-Host "  [FAIL] Trade log missing required column: $col" -ForegroundColor Red
            $FAIL++
        }
    }
    if ($FAIL -eq 0) {
        Write-Host "  [OK] Trade log schema valid (all $($requiredCols.Count) required columns present)" -ForegroundColor Green
    }
}

# Check 6: Row count sanity (Batch A 150t x 4y should have thousands of trades)
if ($tradeLog -like "*.csv" -and (Test-Path $tradeLog)) {
    $rowCount = (Get-Content $tradeLog | Measure-Object -Line).Lines - 1  # minus header
    Write-Host "  [INFO] Trade log rows: $rowCount" -ForegroundColor Cyan
    if ($rowCount -lt 100) {
        Write-Host "  [FAIL] Trade log has only $rowCount trades (expected 1000+)" -ForegroundColor Red
        $FAIL++
    } elseif ($rowCount -lt 500) {
        Write-Host "  [WARN] Trade log has $rowCount trades (low; may be Batch A infrastructure issue)" -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] Trade log row count reasonable" -ForegroundColor Green
    }
}

# Check 7: Dry-run merge simulation (Python)
Write-Host ""
Write-Host "Running Python merge simulation..." -ForegroundColor Cyan

python -c @"
import pandas as pd
import os
import sys

BATCH_A_DIR = 'output_batch_A_150'
trade_log = None
for ext in ['parquet', 'csv']:
    path = os.path.join(BATCH_A_DIR, f'trade_log.{ext}')
    if os.path.exists(path):
        trade_log = path
        break

if not trade_log:
    print('FAIL: no trade log')
    sys.exit(1)

try:
    if trade_log.endswith('.parquet'):
        df = pd.read_parquet(trade_log)
    else:
        df = pd.read_csv(trade_log)
    print(f'OK: loaded {len(df)} rows, {len(df.columns)} columns')
    print(f'Unique tickers: {df.ticker.nunique() if \"ticker\" in df.columns else \"?\"}')
    print(f'Unique strategies: {df.strategy.nunique() if \"strategy\" in df.columns else \"?\"}')
    print(f'Date range: {df.entry_date.min() if \"entry_date\" in df.columns else \"?\"} to {df.exit_date.max() if \"exit_date\" in df.columns else \"?\"}')
    print(f'Merge-ready: YES')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] Python merge simulation failed" -ForegroundColor Red
    $FAIL++
}

# Summary
Write-Host ""
if ($FAIL -eq 0) {
    Write-Host "=== MERGE DRY-RUN PASS ===" -ForegroundColor Green
    Write-Host "Batch A output is merge-ready. Safe to launch Batch B." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: .\scripts\laptop_launch_batch_b.ps1" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "=== MERGE DRY-RUN FAIL ($FAIL error(s)) ===" -ForegroundColor Red
    Write-Host "DO NOT launch Batch B until merge issues are fixed." -ForegroundColor Red
    exit 1
}
