# Project Learnings — Stock Picks & Automated Trading System
**Project:** jeetmehta1991/stock-picks-app
**Period:** March–April 2026
**Purpose:** Every mistake made in this project, with root cause and fix. Reference before making any change.

---

## Infrastructure & Environment

### L1 — Codespace network restrictions
**Mistake:** Assumed all external APIs accessible from Codespaces. Wikipedia, Quiver, Finnhub all failed silently.
**Fix:** Pre-fetch scripts run from laptop or GitHub Actions. Codespaces only used for computation on cached data. Test every new API endpoint from Codespaces before building integrations.

### L2 — pyarrow not installed on Codespace restart
**Mistake:** Cache layer built but pyarrow missing after restart — multiple runs produced no cache files.
**Fix:** Added pyarrow + all dependencies to devcontainer.json. Auto-installs on every start.

### L3 — Cache not committed = lost on restart
**Mistake:** Downloaded 67 instruments, Codespace restarted, lost everything. Repeated 3+ times.
**Fix:** Immediate commit after every download. Chunk-commit every 25-50 tickers during long downloads.

### L4 — git pull causing divergent branch conflicts
**Mistake:** Used `git pull` repeatedly causing merge conflicts on Windows PowerShell.
**Fix:** Always use `git fetch origin ; git reset --hard origin/main` to sync. Check for uncommitted changes first.

### L5 — Direct pushes to main causing conflicts
**Mistake:** Pushed directly to main from sandbox, causing conflicts on laptop and Codespace.
**Fix:** All changes go through claude-updates branch. Rule enforced in CLAUDE.md.

### L31 — git reset --hard wiped uncommitted Quiver data
**Mistake:** Instructed `git reset --hard origin/main` which wiped locally completed Quiver data not yet committed.
**Fix:** Before any `git reset --hard`, always run `git status` first. If uncommitted work exists, commit it before resetting.

### L33 — Used && in commands on Windows PowerShell
**Mistake:** Repeatedly gave commands using `&&` as separator. PowerShell uses `;` not `&&`.
**Fix:** All commands now use `;`. Always identify terminal environment before giving commands.

### L34 — Built solution for wrong environment
**Mistake:** Created a PowerShell script despite knowing the user worked in Git Bash. Made 3 consecutive errors.
**Fix:** The correct solution was always one Git Bash line: `export QUIVER_API_KEY="key" ; python scripts/prefetch_quiver.py`

---

## Data & APIs

### L6 — Wikipedia as S&P 500 source
**Mistake:** Used Wikipedia for S&P 500 list — blocked by Codespaces network allowlist.
**Fix:** `sp500_tickers.csv` committed to repo. No network calls needed for universe.

### L7 — AAII sentiment — only 15 hardcoded data points
**Mistake:** Built sentiment agent with 15 hardcoded AAII readings for 782 trading days.
**Fix:** Full 325 weekly readings downloaded from AAII, committed as CSV. Covers 2020-2026.

### L8 — CNN Fear & Greed — same problem as L7
**Mistake:** 16 hardcoded points for 782 days.
**Fix:** 1,630 daily readings built from CNN archives. Covers 2020-March 2026.

### L9 — Quiver API tier not verified before building
**Mistake:** Built full 509-ticker download for insider data on Hobbyist tier. All returned 0 records.
**Fix:** Verified all endpoints before re-running. Upgraded to Trader tier ($75/month). Cost: $45 extra + wasted time.

### L10 — Wrong Quiver endpoint URLs
**Mistake:** Used `/historical/insidertrading/` — returned 404. Correct is `/live/insiders?ticker=`.
**Fix:** Installed quiverquant package, extracted URLs from source code before building.

### L11 — Agents calling live APIs during backtest loop
**Mistake:** Started Phase 1B with agents calling Quiver/FRED live on every candidate. Estimated 40-60 hours runtime.
**Fix:** Built complete pre-fetch architecture. Agents now read from Parquet cache — ~2 seconds per candidate.

### L12 — Backtest period too short
**Mistake:** Set BACKTEST_END = 2024-12-31. Excluded all 2025 data — the most recent and relevant period.
**Fix:** Extended to March 2026. IS = 2022-2024, OOS = 2025-March 2026.

### L13 — Parallel GitHub Actions batches with git push conflicts
**Mistake:** Ran 5 Finnhub batches simultaneously. All tried to push to main — only one succeeded.
**Fix:** Never run parallel workflows that all push to the same branch. Sequential is slower but reliable.

### L22 — Parallel GitHub Actions batches (same lesson, repeated)
**Mistake:** Made the same parallel push mistake again despite L13 being documented.
**Fix:** git pull --rebase before push added as partial mitigation. Sequential batches enforced.

### L23 — Insider endpoint run against 509 tickers before verifying
**Mistake:** Built and ran full 509-ticker download before verifying the endpoint worked on our tier.
**Fix:** Test one call per endpoint before building any script. This is CHECKLIST item 12.

### L37 — Finnhub free tier 1-year lookback not verified before downloading
**Mistake:** Built and ran Finnhub pre-fetch for 2022-2024 data. Free tier only returns ~1 year. All 509 files empty.
**Fix:** Test the date range before building. `r = requests.get(url, params={..., "from": "2022-01-01"})` — check `len(data)` first.

### L43 — Alpha Vantage already provides news sentiment — Finnhub was unnecessary
**Mistake:** Added Finnhub for news sentiment without checking if Alpha Vantage (already in use) also provides it.
**Fix:** Always check existing API providers for additional endpoints before adding new ones. AV provides AI sentiment, free, full 2022-2026 coverage.

---

## Engine & Strategy Design

### L14 — Aggregate exit comparison, no per-trade detail
**Mistake:** Exit comparison only saved strategy-level aggregates. Impossible to audit individual trades.
**Fix:** Added `trade_exit_detail.csv` — one row per trade × exit method.

### L15 — Raw smart money signals not in trade log
**Mistake:** Only saved composite smart money score. Couldn't audit why a trade got EXCEPTIONAL vs HIGH tier.
**Fix:** Added congressional_signal, insider_signal, institutional_signal, aaii_bullish, cnn_fg_score to trade log.

### L16 — Phase 1B universe not switching from 67 instruments
**Mistake:** `--phase 1b` flag existed but didn't change the universe from 67 to 509 instruments.
**Fix:** `run_phase1a.py` now loads full 509-instrument universe when `--phase 1b` is passed.

### L17 — Stop simulation described incorrectly
**Mistake:** Claimed results were pessimistic. Actually slightly optimistic — gap-down opens fill at open price.
**Fix:** Corrected in PROJECT_PLAN.md. Think through simulation logic before documenting.

### L36 — Trailing stop used closing price not intraday low
**Mistake:** `check_trailing_stop_hit` checked `today_close <= trailing_stop`. Real stops trigger on intraday low.
**Fix:** Changed to `today_low <= trailing_stop` for longs, `today_high >= trailing_stop` for shorts. ~2-4pp lower win rates but realistic.

### L44 — smart_money_score returned wrong key names — all agent SM context was empty
**Mistake:** `smart_money_score()` returned `{composite_signal, score, details}`. Agent pipeline expected `{congressional_sig, insider_sig, institutional_sig, smart_money_composite}`. All agent SM context was empty dicts for the entire backtest.
**Fix:** Updated `smart_money_score()` to return all keys expected by both engine AND pipeline. Added integration test.

### L47 — Walk-forward documented as two-window but implemented as one
**Mistake:** PROJECT_PLAN.md said two walk-forward windows. Code had one with hardcoded dates.
**Fix:** Walk-forward now runs two windows. ROBUST = passes both.

### L48 — MAE/MFE computed for one day not full trade duration
**Mistake:** `max_adverse_excursion` was documented as "worst % during hold period" but computed from a single bar.
**Fix:** MAE/MFE now accumulated on OpenTrade across every day of the hold period.

---

## Agent Pipeline Design

### L38 — Decision Agent was given the tier rules it was supposed to derive
**Mistake:** Gave the Decision Agent the confidence tier matrix in its prompt. Agent pattern-matched rules instead of reasoning independently.
**Fix:** Removed tier rules from prompt. Agent returns `final_score` (0-100). Tier mapping happens in code.

### L39 — Agent temperature not set — non-deterministic backtest results
**Mistake:** API calls did not set `temperature`. Default is 1.0 (stochastic). Same inputs could produce different outputs on different runs.
**Fix:** Added `temperature=0.0` to all backtest agent calls. `temperature=0.3` for live trading.

---

## Process & Workflow

### L18 — No batch testing before full Phase 1B run
**Mistake:** Attempted to run full Phase 1B on 509 instruments without first testing on 25 tickers.
**Fix:** Added to CHECKLIST item 13. Phase 1B will run 25-ticker test first and review agent outputs.

### L19 — Commands not chained
**Mistake:** Gave separate commands for run, commit, push. Codespace timed out between commands, losing results.
**Fix:** Chain dependent commands. Commit+push always together. Long runs always use nohup.

### L20 — CLAUDE.md modified without approval
**Mistake:** Rewrote CLAUDE.md from 128 to 62 lines without showing diff or getting approval.
**Fix:** CLAUDE.md is the owner's document. Never modify without showing exact before/after diff.

### L21 — Jumped ahead to Phase 1B download without approval
**Mistake:** Downloaded full S&P 500 cache for Phase 1B before Phase 1A results were reviewed.
**Fix:** Never jump ahead of the current phase. Each phase requires explicit owner approval.

### L24 — Phase 1B partial run started without complete data
**Mistake:** Started Phase 1B agents with AAII at 15 hardcoded points, no news, no pre-fetched SM data. ~$3 CAD wasted.
**Fix:** Never start a paid agent run without verifying all data sources are complete. Pre-run checklist must be verified.

### L25 — input() prompt broke nohup execution
**Mistake:** Run script had an interactive `input()` prompt. nohup has no terminal attached — crashes.
**Fix:** Removed interactive prompt. Script now prints cost estimate and proceeds automatically.

### L26 — Checklist existed but wasn't being followed
**Mistake:** CHECKLIST.md was created but repeatedly not consulted before taking actions.
**Fix:** Behavioural discipline required. Checklist must be the first thing consulted, not an afterthought.

### L35 — Checklist not enforced in practice (same as L26, repeated)
**Mistake:** Made 33+ documented mistakes after the checklist existed.
**Fix:** Visibly state checklist compliance before every action. Owner prompt "Did you run the checklist?" enforces this.

---

## Cost & Estimation

### L29 — Wrong runtime and cost estimates
**Mistake:** Estimated Phase 1B at 3-4 hours and ~$16 USD. Actual: 40+ hours and ~$115 USD.
**Fix:** Never give cost/runtime estimates without measuring one actual call first. Always show the calculation.

### L30 — CLAUDE.md reduction claimed wrong token savings
**Mistake:** Recommended reducing CLAUDE.md claiming token savings. Claude Code loads it every session — removing content costs tokens not saves them.
**Fix:** Always identify which environment a change affects before claiming a benefit.

### L32 — Phase 1B cost formula was wrong
**Mistake:** Used `days × max_cands × $0.021 / 10` — the `/10` divisor was incorrect.
**Fix:** Corrected formula: `days × avg_passing × 6 agents × $0.00035`. Always validate cost formulas before presenting.

---

## Metrics & Analysis Design

### L40 — Smart money lift threshold was undefined
**Mistake:** Passing criterion "smart money lift" had no numeric threshold. Any lift, even 0.1pp, passed.
**Fix:** Smart money lift now requires ≥ 3pp win rate improvement with minimum 30 trades per bucket.

### L41 — No benchmark comparison or risk-adjusted metrics
**Mistake:** All strategy performance reported in absolute terms. No SPY comparison, no Sharpe, no Calmar.
**Fix:** Added SPY benchmark comparison, beats_benchmark flag, Calmar ratio, and 95% CIs to all strategy metrics.

---

## Testing

### L45 — Audits were conversational not executable — critical bugs survived three reviews
**Mistake:** Three comprehensive audits conducted by reading code. L44 (all SM context empty) survived all three. Would have been caught in 30 seconds by running a single print statement.
**Fix:** After every audit, every flagged item must be validated by running code. Integration tests created (7 tests). Unit tests created (29 tests). E2E smoke test created. Run `python backtest/tests/run_all_tests.py` before every Phase 1B.

### L46 — No systematic data flow tracing — producer/consumer key coherency never verified
**Mistake:** smart_money_score() and pipeline.py both looked correct when read independently. Never tested that output keys matched expected input keys.
**Fix:** Every inter-module data handoff gets an integration test. Pattern: `result = producer(); assert 'expected_key' in result`.

---

## Broker & Infrastructure (Stage 4+)

### L42 — Alpaca not available in Canada
**Mistake:** Listed Alpaca as Stage 4 broker throughout the project plan without checking Canadian availability.
**Fix:** Updated broker to IBKR Canada (Interactive Brokers Canada) — lowest commissions for active Canadian traders.

---

## Summary Statistics
- Total mistakes documented: 48
- Infrastructure mistakes: 8
- Data/API mistakes: 10
- Engine/strategy mistakes: 8
- Agent pipeline mistakes: 2
- Process/workflow mistakes: 8
- Cost/estimation mistakes: 3
- Metrics/analysis mistakes: 2
- Testing mistakes: 2
- Broker/infrastructure mistakes: 1
