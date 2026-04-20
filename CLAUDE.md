# Stock Picks & Automated Trading System
**Stage:** 2 — Strategy Validation | **Phase:** 1A rerun in progress
**Repo:** jeetmehta1991/stock-picks-app | **Full plan:** `PROJECT_PLAN.md`

---

## Critical Rules — Read First

- **ALL decisions require explicit owner approval before implementation. No exceptions.** Rules, filters, thresholds, strategies, architecture, infrastructure — everything. Claude presents recommendations with reasoning. Owner decides. Claude builds only what is explicitly approved.
- **NEVER change any rule, filter, threshold, or strategy parameter without explicit owner approval.** Present recommendations only. Owner decides. Then build.
- Point-in-time data enforcement is non-negotiable — no future data ever used in backtest
- All strategy/rule decisions are logged in `PROJECT_PLAN.md` section 8 with approval status
- Push all changes to `claude-updates` branch only — never directly to `main`
- Sync to main via GitHub Actions → Sync from Claude workflow

---

## Repo Structure

```
stock-picks-app/
├── backtest/
│   ├── config.py              # universe, regimes, thresholds, position sizing
│   ├── run_phase1a.py         # entry point — python -m backtest.run_phase1a
│   ├── data/
│   │   ├── cache.py           # Parquet cache — fetch once, load from disk
│   │   ├── universe.py        # S&P 500 universe + liquidity filter
│   │   ├── fetcher.py         # yfinance OHLCV + fundamentals
│   │   ├── macro.py           # FRED yield curve, VIX, DXY
│   │   ├── sentiment.py       # AAII, CNN Fear & Greed
│   │   └── smart_money.py     # congressional, insider, 13F, analyst
│   ├── signals/
│   │   ├── technical.py       # 274 signal fields
│   │   └── screener.py        # 60 strategies, 7 categories
│   ├── engine/
│   │   ├── backtest.py        # main loop
│   │   ├── exit_manager.py    # trailing stop + 5 circuit breakers
│   │   ├── exit_strategies.py # 12 exit methods, composite scoring
│   │   ├── regime_filter.py   # VIX + SPY 200 EMA classification
│   │   └── improvements.py    # transaction costs, walk-forward, slippage
│   ├── agents/pipeline.py     # 6 TradingAgents (Haiku/Sonnet)
│   └── results/
│       ├── metrics.py         # 10 passing criteria per strategy
│       ├── writer.py          # 13 output files
│       └── site_generator.py  # daily site_picks JSON
├── output_v2/                 # Phase 1A results
├── PROJECT_PLAN.md            # full project plan — read for all context
├── analysis_dashboard.html    # 9-tab interactive dashboard
├── launcher.html              # navigation page
└── index.html                 # daily top stocks webpage
```

---

## Current Phase Status

**Phase 1A v3 — running with approved rule changes**

**Sync Codespace before anything:**
```bash
git fetch origin ; git reset --hard origin/main
```

Run command:
```bash
pip install -r requirements.txt --break-system-packages -q
find backtest -name "*.pyc" -delete ; find backtest -name "__pycache__" -type d -exec rm -rf {} +
python -m backtest.run_phase1a --no-agents --output-dir output_v2
```

After run completes:
```bash
git add output_v2/ backtest/data/cache/ ; git commit -m "Phase 1A v3 results" ; git push origin main
```

**Never use `git pull` — always use `git fetch origin ; git reset --hard origin/main`**

**Phase 1A v1 results (previous — superseded):**
198 trades, 17 strategies fired, 0 short trades, 0 passing. Pipeline confirmed clean.

---

## Approved Rule Changes (Phase 1A v3)

All owner-approved. Do not revert without approval.

| Rule | Value |
|---|---|
| Open position cap | Removed from backtest |
| Daily loss limit | Removed from backtest |
| Correlation filter | Removed from backtest |
| Regime position sizing | Removed from backtest |
| Regime direction hard block | Removed — all directions allowed, crisis flagged |
| One trade per ticker per day | Removed — all strategies fire independently |
| Crisis regime longs | Allowed — flagged as `regime=crisis_CRISIS_FLAG` |
| Max candidates per day | 10 |
| Mean reversion ATR multiplier | 1.0× |
| Liquidity filter | Once at load time only |
| Position sizing | EXCEPTIONAL 5%, VERY HIGH 4%, HIGH 3%, MEDIUM-HIGH 1.5% |
| Short RSI (rsi_overbought_short) | 68 |
| Short candle conditions | Original strict — wait for Phase 1B volume |
| Pyramiding | Out of scope — flagged for Stage 4 + backtest later |

---

## Key Design Decisions

- 60 strategies, 7 categories — see PROJECT_PLAN.md section 5
- 12 exit methods via composite score (40% ROI + 30% PF + 30% DD)
- Trailing stop primary exit: 10% below highest close, never reverses
- Risk profile: medium-high risk, high return. Buy dips including in crisis.
- Email (not Telegram) for all trade approvals in Stage 4
- Intraday trading: completely separate future project — out of scope

---

## Next Steps

1. Phase 1A v3 completes → push results + cache → Claude analyses
2. Review results → confirm before Phase 1B spend (~$116 CAD)
3. Phase 1B → 1C → 1D before any paper trading begins
