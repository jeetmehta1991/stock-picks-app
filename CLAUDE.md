# Stock Picks & Automated Trading System
**Stage:** 2 — Strategy Validation | **Phase:** 1B — Full backtest in progress
**Repo:** jeetmehta1991/stock-picks-app
**Docs:** `PROJECT_PLAN.md` (full detail) | `CHECKLIST.md` (pre-action) | `LEARNINGS.md` (lessons)

---

## Critical Rules

- **ALL decisions need explicit owner approval before implementation. No exceptions.**
- Never change rules, filters, thresholds, or parameters without approval. Recommend only.
- Think through every action completely before suggesting it. Anticipate edge cases.
- Never jump ahead of the current phase. One instruction at a time.
- If something can go wrong, flag it proactively.
- Point-in-time data enforcement is non-negotiable.
- **Never use `git reset --hard` without running `git status` first. This has destroyed data twice (L49, L77).**
- **Run CHECKLIST.md before every suggestion or execution.**
- For every proposed change, always provide a recommendation with clear reasoning and tradeoffs before waiting for approval.
- After every audit, validate by RUNNING CODE — not reading it.
- Run `backtest/tests/test_integration.py` and `backtest/tests/test_unit.py` before every phase run and after every significant code change (36/36 must pass).

---

## Current Status (April 2026)

**Phase 1B with-news batch test: COMPLETE**
- 5 tickers (MMM, AOS, ABT, ABBV, ACN), Jan–Oct 2022, 577 trades, committed to main
- Agent reasoning: coherent and specific ✅
- News sentiment: `not_available` for all trades — Alpha Vantage free tier insufficient
- **Decision: proceed Phase 1B without news.** News adds no value at free tier. Revisit in Phase 1C with Unusual Whales.

**No-news batch test: NOT NEEDED** — news_sentiment = 'not_available' in both runs. A/B comparison would show identical results. Decision already made.

**Next actions (priority order):**
1. Sync laptop: `git pull --rebase origin main`
2. Run quarterly S&P 500 universe refresh (CHECKLIST item 19) — CSV is stale
3. Run 1-ticker-per-batch test (5 terminals, Jan 2022) before full Phase 1B
4. Owner approves test outputs → scale to full 509-ticker Phase 1B

---

## Phase 1B Parallel Batch Architecture

Full Phase 1B runs 5 parallel batches on LAPTOP (not Codespaces — no timeout risk).
- **Laptop required.** Disable sleep before starting. Set 3 API keys in each terminal.
- **5 terminals simultaneously.** Each batch ~101 tickers, ~3 hours, ~15 hours total.
- **Cost:** ~$116 CAD total.

**Before starting:**
```bash
python scripts/prepopulate_cache_index.py
python scripts/generate_batch_splits.py   # prints exact commands
```

**Test run first (1 ticker per batch, Jan 2022):**
See `scripts/generate_batch_splits.py` output for exact commands.

**After all batches complete — commit sequence (CHECKLIST item 18):**
```
git status → git add → git commit → git pull --rebase → git push → verify → merge
```

**NEVER run git reset --hard at any point.**

---

## Repo Structure

```
backtest/
  config.py              # universe, regimes, thresholds, position sizing
  run_phase1a.py         # entry point — --phase, --tickers, --no-news, --no-git flags
  data/
    cache.py             # Parquet cache + filelock for parallel writes
    universe.py          # 3-tier universe: get_sp500_constituents, get_extended_universe, get_full_live_universe
    sp500_tickers.csv    # Tier 1 — quarterly refresh via scripts/refresh_sp500_universe.py
    extended_universe.csv # Tier 2 — monthly refresh (Stage 3+)
    momentum_watchlist.csv # Tier 3 — monthly refresh (Stage 3+)
    fetcher.py           # yfinance OHLCV + fundamentals (Wikipedia REMOVED — L88)
    macro.py             # FRED yield curve, VIX (from OHLCV cache), DXY (UUP proxy)
    sentiment.py         # AAII, CNN Fear & Greed
    smart_money.py       # congressional, insider, 13F
  signals/
    technical.py         # 274 signal fields
    screener.py          # 60 strategies, 7 categories
  engine/
    backtest.py          # main loop, incremental checkpoints every 100 days
    exit_manager.py      # trailing stop + 5 circuit breakers
    exit_strategies.py   # 12 exit methods
    regime_filter.py     # classify_regime: bull/neutral/bear/crisis
    improvements.py      # walk-forward, transaction costs, slippage, survivorship
  agents/pipeline.py     # 6-agent pipeline (Haiku Phase 1B, Sonnet Phase 1C+)
  results/
    metrics.py           # 9 passing criteria + per-regime verdict matrix
    writer.py            # trade_log, backtest_results, strategy_regime_matrix.json
    site_generator.py    # daily site_picks JSON
scripts/
  generate_batch_splits.py     # prints 5-batch commands + 1-ticker test commands
  merge_batch_outputs.py       # merge 5 outputs, re-compute metrics, validate
  prepopulate_cache_index.py   # pre-fill index.json before parallel runs
  refresh_sp500_universe.py    # quarterly S&P 500 refresh (laptop only, slickcharts.com)
  refresh_extended_universe.py # monthly Tier 2 refresh (laptop only)
  build_momentum_watchlist.py  # monthly Tier 3 refresh (laptop only)
  validate_phase1b_data.py     # pre-run data completeness check
PROJECT_PLAN.md   # comprehensive reference — read first
CHECKLIST.md      # pre-action checklist — 21 items including universe refresh
LEARNINGS.md      # 89 lessons — L88: no Wikipedia, L89: universe staleness
```

---

## Passing Criteria (9 overall + per-regime verdict)

All 9 must pass overall for a strategy to advance. Additionally, each strategy gets a per-regime verdict (PASS/FAIL/INSUFFICIENT_DATA) for each of the 7 historical regimes. A strategy valid in crisis but not bull is deployed only during crisis — this is intentional.

| # | Criterion | Threshold |
|---|---|---|
| 1 | Win rate | ≥55% (high-vol sectors: ≥50%) |
| 2 | Profit factor | >1.3 (high-vol: >1.2) |
| 3 | Expected value | >0 |
| 4 | Win/loss ratio | >1.0 |
| 5 | Max drawdown | <20 pct-points (high-vol: <25) |
| 6 | Total ROI | >0% |
| 7 | Smart money lift | ≥3pp win rate improvement |
| 8 | Macro correlation | ≥5pp win rate diff |
| 9 | Min trades | ≥100 overall, ≥30 per regime |
| 10 | Per-regime verdict | PASS in ≥1 regime (not universal pass required) |

---

## Key Design Decisions

- **Risk profile:** medium-high risk, high return. Buy dips including in crisis.
- **Regime classification (real-time):** bull/neutral/bear/crisis via 20-day realised vol + SPY vs 200 EMA
- **Per-regime strategy library:** different strategies for different regimes — not universal strategies
- **Position sizing:** EXCEPTIONAL 5%, VERY HIGH 4%, HIGH 3%, MEDIUM-HIGH 1.5%, MEDIUM 0.75%, LOW skip
- **Exit:** atr_trail_1x (1× ATR trailing stop, checked against intraday low) — won 20/29 in Phase 1A
- **Email** (not Telegram) for all trade approvals in Stage 4
- **Intraday trading:** completely separate future project — out of scope
- **Agent pipeline:** 6 agents (Technical, Fundamental, Sentiment, Risk, Bull/Bear Debate, Decision) at temperature=0. Haiku for Phase 1B (~$116 CAD). Sonnet for Phase 1C+.
- **News sentiment:** not_available at free tier. Proceed Phase 1B without news. Add Unusual Whales in Phase 1C instead.

---

## Approved Rules

| Rule | Value |
|---|---|
| Open position cap | Removed from backtest |
| Daily loss limit | Removed from backtest |
| Correlation filter | Removed from backtest |
| Regime hard blocks | Removed — crisis flagged but longs allowed (buy-the-dip) |
| One trade per ticker | Removed — all strategies fire independently |
| Crisis regime longs | Allowed at 50% size — flagged as `regime=crisis_CRISIS_FLAG` |
| Max candidates/day | 10 |
| Position sizing | Tiered: 5/4/3/1.5/0.75% by confidence tier |
| Agent tier upgrade | score ≥75 upgrades one tier |
| Agent tier downgrade | score ≤40 downgrades one tier |

---

## HARD RULES — Never Violate

### Git Safety
- **NEVER run `git reset --hard` without `git status` first.** Has destroyed data twice (L49, L77).
- **NEVER run any git destructive command during or after parallel batch runs without checking status.**
- All code goes to `claude-updates` branch, merged to main via push.

### Data Sources
- **NEVER use Wikipedia.** Blocked in Codespaces, not point-in-time, fragile (L88).
  - S&P 500 → `backtest/data/sp500_tickers.csv` refreshed quarterly via `scripts/refresh_sp500_universe.py` on LAPTOP using slickcharts.com
  - Never propose `pd.read_html('https://en.wikipedia.org/...')` for any purpose.

### Universe Management
- `sp500_tickers.csv` must be refreshed quarterly (CHECKLIST item 19). If last commit >90 days old, flag before any run.
- New spinoffs above $10B market cap → add to Tier 2 immediately, don't wait for S&P 500 inclusion (SNDK waited 9 months — L89).
- Tier 2 (extended universe): monthly refresh in live trading.
- Tier 3 (momentum watchlist): monthly refresh in live trading, static for backtesting.

### Strategy Changes
- No strategy or rule changes without explicit owner approval. Every threshold, filter, and parameter change requires sign-off.
- The per-regime verdict system means a strategy that fails in one regime is NOT discarded — it is tagged for the regimes where it passes.
