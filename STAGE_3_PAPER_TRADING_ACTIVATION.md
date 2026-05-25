# Stage 3 — Paper Trading Activation Runbook (G22)

**Created:** Batch 345 2026-05-25 (owner directive "Implement D and G now").

## Status

| Component | State |
|---|---|
| `backtest/paper_trading/paper_portfolio.py` (Portfolio class) | ✅ DONE |
| `backtest/paper_trading/daily_picks.py` (generate_picks helpers) | ✅ DONE |
| `backtest/paper_trading/email_digest.py` (formatter + SMTP) | ✅ DONE |
| `scripts/run_paper_morning.py` (morning orchestrator) | ✅ DONE — runs cleanly + graceful when winners.parquet missing |
| `scripts/run_paper_end_of_day.py` (EOD update) | ✅ DONE |
| `backtest/tests/test_paper_trading.py` | ✅ 19/19 passing |
| **Activation** | ❌ NOT ACTIVATED — owner action required |

## Activation prerequisites (sequence)

### 1. winners.parquet from Phase 1A-β

The morning orchestrator filters today's screen output against the Phase 1A-β winning (strategy × exit × regime) cells. Without this file, the warning fires:
```
[WARN] No winners at <path>/winners.parquet; nothing to pick
```

**Source:** after Phase 1A-β full re-run + `scripts/extract_phase_1a_beta_winners.py`.

### 2. SMTP credentials in env (for email digest)

```powershell
$env:EMAIL_SMTP_HOST = "smtp.gmail.com"
$env:EMAIL_SMTP_PORT = "587"
$env:EMAIL_SMTP_USER = "you@example.com"
$env:EMAIL_SMTP_PASS = "<app-password>"
$env:EMAIL_SMTP_FROM = "you@example.com"
$env:EMAIL_SMTP_TO   = "you@example.com"
```

Without these, `--send-email` will error; `--dry-run` runs without SMTP.

### 3. OHLCV daily refresh (most-recent close needed for picks)

The morning orchestrator reads `data_prefetch/polygon/ohlcv_daily/{TICKER}.parquet` for current-day close prices. After Stage 2 closes, set up a daily refresh job:
```bash
# Daily 5pm ET (after market close):
python scripts/prefetch_polygon_ohlcv.py --tickers <winners_universe> --latest-only
```
Requires `POLYGON_API_KEY` set.

## Activation commands

### Smoke (dry-run; no positions opened, no email sent)
```bash
python scripts/run_paper_morning.py \
    --winners-source output_phase_1a_beta_merged_local \
    --max-picks 5 \
    --dry-run
```

### Live (opens positions in paper portfolio + sends email)
```bash
python scripts/run_paper_morning.py \
    --winners-source output_phase_1a_beta_merged_local \
    --max-picks 5 \
    --send-email
```

### End-of-day (update position marks + journal)
```bash
python scripts/run_paper_end_of_day.py
```

## Schedule (Windows Task Scheduler or AWS Lightsail crontab)

```cron
# 9:00 ET Mon-Fri: morning orchestrator
0 13 * * 1-5  cd /path/to/stock-picks-app && .venv/bin/python scripts/run_paper_morning.py --send-email

# 17:00 ET Mon-Fri: end-of-day
0 21 * * 1-5  cd /path/to/stock-picks-app && .venv/bin/python scripts/run_paper_end_of_day.py
```

Times in UTC (Hetzner default). Adjust for ET (UTC-5 standard / UTC-4 daylight).

## Gates before flipping to live (Stage 4)

Per PROJECT_PLAN §3.13:
- Paper-trading 90+ days of clean daily runs
- Tracked equity curve matches backtest expectations within ±10% (drawdown profile)
- No errors in the journal for 30+ consecutive days
- Owner sign-off
- Then Stage 4 IBKR connection via `scripts/run_live_morning.py` (already built; same architecture)
