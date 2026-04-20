# Stock Picks & Automated Trading System
**Stage:** 2 — Strategy Validation | **Phase:** 1A v3 pending run
**Repo:** jeetmehta1991/stock-picks-app
**Docs:** `PROJECT_PLAN.md` (full detail) | `PROGRESS.md` (daily status)

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

---

## Key Files
- `backtest/config.py` — universe, position sizing, thresholds
- `backtest/run_phase1a.py` — entry point
- `backtest/signals/screener.py` — 60 strategies
- `backtest/engine/backtest.py` — main loop, all approved rules
- `backtest/data/cache/` — Parquet cache (561 tickers committed)
- `backtest/data/sp500_tickers.csv` — S&P 500 list (no web fetch needed)
- `scripts/download_cache.sh` — run to download/refresh cache
- `output_v2/` — Phase 1A results

---

## Current Phase: 1A v3

**Blocked on two owner decisions:**
1. Multiple strategies on same ticker — separate positions or one combined?
2. Review + confirm PROJECT_PLAN.md sections 18 & 19 (strategies + rules)

**Run command (after decisions confirmed):**
```bash
git fetch origin ; git reset --hard origin/main
python -m backtest.run_phase1a --no-agents --output-dir output_v2
git add output_v2/ ; git commit -m "Phase 1A v3 results" ; git push origin main
```

---

## Approved Rules (Phase 1A v3)
No position cap | No daily loss limit | No correlation filter | No regime sizing |
No direction hard block (crisis flagged) | No one-trade-per-ticker limit |
Max candidates 10 | Mean reversion ATR 1.0× | Liquidity filter once at load |
Position sizing: EXCEPTIONAL 5% / VERY HIGH 4% / HIGH 3% / MEDIUM-HIGH 1.5% |
Short RSI threshold 68 | Short candle conditions original strict | Pyramiding Stage 4

---

## Next Steps
1. Owner confirms two decisions above
2. Run Phase 1A v3 → analyse results
3. Phase 1B (~$116 CAD, ~509 instruments) → 1C → 1D
4. Stage 3 paper trading
