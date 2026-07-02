# Per-2hr Strategy Health Check (Batch 1093 Q5 fix 2026-07-02)
# Reads trade_log_checkpoint.csv and emits per-strategy diagnostics:
#   - Top 10 firing strategies + fire count
#   - Silent strategies (0 fires) list
#   - Regime x strategy sparsity
#   - Fire-rate trend last 2hr vs cumulative
#
# Runs in loop; append snapshot every -CadenceMinutes to logs/strategy_health.log.
# Council 227 Q5: address "we should ideally know the status of strategies during
# the run itself so we know if its logical".
#
# Usage:
#   .\scripts\laptop_strategy_health_check.ps1 -BatchDir output_batch_A_150 -CadenceMinutes 120

param(
    [string]$BatchDir = "output_batch_A_150",
    [int]$CadenceMinutes = 120
)

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
Set-Location $PROJECT_ROOT

$logFile = "$BatchDir\strategy_health.log"
$snapshotJson = "$BatchDir\strategy_health_latest.json"

Write-Host "=== Strategy Health Check ===" -ForegroundColor Cyan
Write-Host "Batch dir: $BatchDir"
Write-Host "Cadence: every $CadenceMinutes min"
Write-Host "Log: $logFile"
Write-Host "Ctrl+C to stop"
Write-Host ""

# Track last snapshot's trade count for rate-of-change
$lastCount = 0
$lastTimestamp = Get-Date

while ($true) {
    $now = Get-Date
    $tradeLog = "$BatchDir\trade_log_checkpoint.csv"

    if (-not (Test-Path $tradeLog)) {
        $msg = "[$now] SKIP: trade_log_checkpoint.csv not yet present"
        Write-Host $msg -ForegroundColor Yellow
        Add-Content -Path $logFile -Value $msg
        Start-Sleep -Seconds ($CadenceMinutes * 60)
        continue
    }

    # Run Python analytics
    $py = @"
import pandas as pd
import json
import sys
from datetime import datetime

BATCH_DIR = r'$BatchDir'
tradeLog = BATCH_DIR + '/trade_log_checkpoint.csv'

try:
    df = pd.read_csv(tradeLog)
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)

total = len(df)
tickers_active = df.ticker.nunique() if 'ticker' in df.columns else 0
strats_fired = df.strategy.nunique() if 'strategy' in df.columns else 0
date_range = f"{df.entry_date.min()} -> {df.exit_date.max()}" if 'entry_date' in df.columns else '?'

# Registered strategies
try:
    from backtest.signals.screener import ALL_STRATEGIES
    registered = len(ALL_STRATEGIES)
    # Extract names
    names = []
    for s in ALL_STRATEGIES:
        if hasattr(s, '__name__'):
            names.append(s.__name__)
        elif hasattr(s, 'name'):
            names.append(s.name)
        else:
            names.append(str(s))
    silent_names = sorted(set(names) - set(df.strategy.unique()))
    silent_count = len(silent_names)
except Exception as e:
    registered = -1
    silent_names = []
    silent_count = -1

# Top 10 firing
top10 = df.strategy.value_counts().head(10).to_dict()

# Regime x strategy matrix
regime_strat = None
if 'regime' in df.columns and 'strategy' in df.columns:
    regime_strat = df.groupby(['regime', 'strategy']).size().unstack(fill_value=0)
    # Sparsity per regime
    regime_sparsity = {}
    for regime in regime_strat.index:
        fired_in_regime = (regime_strat.loc[regime] > 0).sum()
        regime_sparsity[str(regime)] = f"{fired_in_regime}/{len(regime_strat.columns)}"
else:
    regime_sparsity = {}

# Win rate + PnL summary
if 'win' in df.columns and 'pnl_pct' in df.columns:
    win_rate = float(df.win.mean()) if len(df) > 0 else 0.0
    mean_pnl = float(df.pnl_pct.mean()) if len(df) > 0 else 0.0
else:
    win_rate = 0.0
    mean_pnl = 0.0

snapshot = {
    'timestamp': datetime.now().isoformat(),
    'total_trades': total,
    'tickers_active': int(tickers_active),
    'strategies_fired': int(strats_fired),
    'strategies_registered': int(registered),
    'silent_count': int(silent_count),
    'silent_pct': (silent_count / registered * 100 if registered > 0 else -1),
    'date_range': date_range,
    'win_rate': win_rate,
    'mean_pnl_pct': mean_pnl,
    'top10_firing': top10,
    'regime_sparsity': regime_sparsity,
    'silent_names_sample': silent_names[:20],
}
print(json.dumps(snapshot, indent=2))
"@

    $result = $py | python
    if ($LASTEXITCODE -ne 0) {
        $msg = "[$now] ERROR: analytics failed: $result"
        Write-Host $msg -ForegroundColor Red
        Add-Content -Path $logFile -Value $msg
    } else {
        # Save latest JSON
        $result | Out-File -FilePath $snapshotJson -Encoding utf8

        # Parse for rate-of-change
        try {
            $snap = $result | ConvertFrom-Json
            $currCount = $snap.total_trades
            $elapsedMin = ($now - $lastTimestamp).TotalMinutes
            if ($elapsedMin -gt 0 -and $lastCount -gt 0) {
                $rate = ($currCount - $lastCount) / $elapsedMin
                $rateStr = " | rate={0:F1} trades/min ({1} in {2:F0} min)" -f $rate, ($currCount - $lastCount), $elapsedMin
            } else {
                $rateStr = " | rate=baseline"
            }
            $lastCount = $currCount
            $lastTimestamp = $now

            $topStrat = ($snap.top10_firing.PSObject.Properties | Select-Object -First 3 | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ", "

            $summary = @"

===============================================================================
[$now] STRATEGY HEALTH SNAPSHOT
===============================================================================
Total trades: $($snap.total_trades)$rateStr
Tickers active: $($snap.tickers_active)
Strategies fired: $($snap.strategies_fired) / $($snap.strategies_registered) (silent: $($snap.silent_count), $([math]::Round($snap.silent_pct,1))%)
Date range: $($snap.date_range)
Win rate: $([math]::Round($snap.win_rate * 100, 1))% | Mean PnL: $([math]::Round($snap.mean_pnl_pct, 3))%
Top 3 firing: $topStrat
Regime sparsity: $(($snap.regime_sparsity.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ", ")
Silent (sample): $($snap.silent_names_sample -join ", ")

Full snapshot JSON: $snapshotJson
"@
            Write-Host $summary
            Add-Content -Path $logFile -Value $summary
        } catch {
            $msg = "[$now] PARSE-ERROR: $_"
            Write-Host $msg -ForegroundColor Yellow
            Add-Content -Path $logFile -Value $msg
        }
    }

    # Sleep until next cadence
    $nextCheck = $now.AddMinutes($CadenceMinutes)
    Write-Host "Next check: $nextCheck" -ForegroundColor Gray
    Start-Sleep -Seconds ($CadenceMinutes * 60)
}
