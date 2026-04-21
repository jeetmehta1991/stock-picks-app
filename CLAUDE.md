# Stock Picks & Automated Trading System
**Stage:** 2 — Strategy Validation | **Phase:** 1A v3 pending run
**Repo:** jeetmehta1991/stock-picks-app
**Docs:** `PROJECT_PLAN.md` (full detail) | `PROGRESS.md` (daily status) | `CHECKLIST.md` (pre-action)

---

## Critical Rules

- **ALL decisions need explicit owner approval before implementation. No exceptions.**
- Never change rules, filters, thresholds, or parameters without approval. Recommend only.
- Think through every action completely before suggesting it. Anticipate edge cases.
- Never jump ahead of the current phase. One instruction at a time.
- If something can go wrong, flag it proactively.
- Point-in-time data enforcement is non-negotiable.
- Push to `claude-updates` branch only — never directly to `main`.
- **Update PROGRESS.md at end of every working session.**
- **Never use `git pull` — always: `git fetch origin ; git reset --hard origin/main`**
- **CLAUDE.md is the owner's document. Never modify it without showing the exact before/after diff and receiving explicit written approval.**
- **Run CHECKLIST.md before every suggestion or execution.**
- For every proposed change, always provide a recommendation with clear reasoning and tradeoffs before waiting for approval. Never stay silent on something that could be improved.

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
│   │   ├── sp500_tickers.csv  # S&P 500 static list — no web fetch needed
│   │   ├── fetcher.py         # yfinance OHLCV + fundamentals
│   │   ├── macro.py           # FRED yield curve, VIX, DXY
│   │   ├── sentiment.py       # AAII, CNN Fear & Greed
│   │   └── smart_money.py     # congressional, insider, 13F, analyst
│   ├── signals/
│   │   ├── technical.py       # 274 signal fields
│   │   └── screener.py        # 60 strategies, 7 categories
│   ├── engine/
│   │   ├── backtest.py        # main loop, all approved rules applied
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
├── scripts/
│   └── download_cache.sh      # run to download/refresh full cache
├── PROJECT_PLAN.md            # full project plan — read for all context
├── PROGRESS.md                # daily status log — update end of every session
├── CHECKLIST.md               # pre-action checklist
├── analysis_dashboard.html    # 9-tab interactive dashboard
├── launcher.html              # navigation page
└── index.html                 # daily top stocks webpage
```

---

## Current Phase: 1A v3

**Blocked on two owner decisions:**
1. Multiple strategies on same ticker — separate positions or one combined?
2. Review + confirm PROJECT_PLAN.md sections 18 & 19 (strategies + rules)

**Sync Codespace before anything:**
```bash
git fetch origin ; git reset --hard origin/main
```

**Run command (after decisions confirmed):**
```bash
pip install -r requirements.txt --break-system-packages -q
find backtest -name "*.pyc" -delete ; find backtest -name "__pycache__" -type d -exec rm -rf {} +
python -m backtest.run_phase1a --no-agents --output-dir output_v2
```

**After run completes — commit and push together:**
```bash
git add output_v2/ ; git commit -m "Phase 1A v3 results" ; git push origin main
```

**Never use `git pull` — always use `git fetch origin ; git reset --hard origin/main`**

**Phase 1A v1 results (previous — superseded):**
198 trades, 17 strategies fired, 0 short trades, 0 passing. Pipeline confirmed clean.

---

## Approved Rules (Phase 1A v3)

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

- 60 strategies, 7 categories — see PROJECT_PLAN.md section 18
- 12 exit methods via composite score (40% ROI + 30% PF + 30% DD)
- Trailing stop primary exit: 10% below highest close, never reverses
- Risk profile: medium-high risk, high return. Buy dips including in crisis.
- Email (not Telegram) for all trade approvals in Stage 4
- Intraday trading: completely separate future project — out of scope
- TradingAgents 6-agent pipeline is core to the product — runs Phase 1B+ (Haiku) and Phase 1C+ (Sonnet). See PROJECT_PLAN.md section 20.

---

## Next Steps

1. Owner confirms two decisions above
2. Run Phase 1A v3 → push results → Claude analyses
3. Review results → confirm before Phase 1B spend (~$116 CAD)
4. Phase 1B → 1C → 1D before any paper trading begins
