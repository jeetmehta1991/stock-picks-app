# Project Learnings & Optimizations
**Project:** Stock Picks & Automated Trading System
**Updated:** April 24, 2026

This document tracks mistakes made, lessons learned, and optimizations integrated.
Maintained to prevent repeating the same errors and to document why decisions were made.

---

## Infrastructure & Environment

### L1 — Codespace network restrictions
**Mistake:** Assumed all external APIs accessible from Codespaces. Spent time debugging Wikipedia, Quiver, Finnhub failures.
**Learning:** Codespaces has an allowlist. Only specific domains (yfinance, pypi, GitHub, FRED) are allowed. Test every new API endpoint from Codespaces before building integrations.
**Fix:** Pre-fetch scripts run from laptop or GitHub Actions. Codespaces only used for computation on cached data.

### L2 — pyarrow not installed on Codespace restart
**Mistake:** Cache layer built but pyarrow missing — multiple runs produced no cache files.
**Learning:** Codespace loses all pip installs on restart unless in devcontainer.json.
**Fix:** Added pyarrow + all dependencies to devcontainer.json. Auto-installs on every start.

### L3 — Cache not committed = lost on restart
**Mistake:** Downloaded 67 instruments, Codespace restarted, lost everything. Repeated 3+ times.
**Learning:** Any file not committed to git is lost when Codespace restarts.
**Fix:** Immediate commit after every download. Chunk-commit every 50 tickers during long downloads.

### L4 — git pull causing divergent branch conflicts
**Mistake:** Used `git pull` repeatedly causing merge conflicts, especially on Windows PowerShell.
**Learning:** `git pull` merges. Always use `git fetch origin ; git reset --hard origin/main` to sync.
**Fix:** Standard sync command documented in CLAUDE.md and CHECKLIST.md.

### L5 — Direct pushes to main causing laptop conflicts
**Mistake:** Pushed directly to main from sandbox environment, causing conflicts on laptop and Codespace.
**Learning:** All changes should go through claude-updates branch → sync workflow → main.
**Fix:** Rule enforced in CLAUDE.md. Sync workflow updated to remove archive bloat.

---

## Data & APIs

### L6 — Wikipedia as S&P 500 source
**Mistake:** Used Wikipedia for S&P 500 list — blocked by Codespaces network allowlist.
**Learning:** Never rely on web scraping for core data. Use committed static files.
**Fix:** `sp500_tickers.csv` committed to repo. No network calls needed for universe.

### L7 — AAII sentiment — only 15 hardcoded data points
**Mistake:** Built sentiment agent with 15 hardcoded AAII readings for 782 trading days. Sentiment agent was nearly blind.
**Learning:** Always verify data coverage before building around it. 15 points for 3 years is not a dataset — it's a placeholder.
**Fix:** Full 325 weekly readings downloaded from AAII, committed as CSV. Covers 2020-2026.

### L8 — CNN Fear & Greed — same problem
**Mistake:** 16 hardcoded points for 782 days.
**Fix:** 1,630 daily readings built from CNN archives and interpolated. Covers 2020-March 2026.

### L9 — Quiver API tier not verified before building
**Mistake:** Built full pre-fetch script for 7 Quiver data types. Ran 509 tickers through insider endpoint. All returned 0 records. Discovered Hobbyist tier doesn't include insider data only after the full run.
**Learning:** Before building any API integration, verify exact endpoint access per tier. Test one call per endpoint before writing any code. (CHECKLIST item 12)
**Fix:** Upgraded to Trader tier ($75/month). Verified all endpoints before re-running. Cost: $45 extra.

### L10 — Wrong Quiver endpoint URLs
**Mistake:** Used `/historical/insidertrading/` — returned 404. Correct endpoint is `/live/insiders?ticker=`.
**Learning:** Always find endpoint URLs from the official Python package source, not assumed paths.
**Fix:** Installed quiverquant package, extracted URLs from source code. Verified before building.

### L11 — Agents calling live APIs during backtest loop
**Mistake:** Started Phase 1B with agents calling Quiver, FRED, sentiment live on every candidate every day. Each agent call took 35 seconds. Estimated 40-60 hours runtime.
**Learning:** Never call external APIs inside a backtest loop. Pre-fetch all data first, read from disk during backtest.
**Fix:** Built complete pre-fetch architecture. Agents now read from Parquet cache — ~2 seconds per candidate.

### L12 — Backtest period too short
**Mistake:** Set BACKTEST_END = 2024-12-31. Phase 1B would have excluded all 2025 data — the most recent and relevant period.
**Learning:** Always use the most recent data available. OOS period should extend to near-present.
**Fix:** Extended to March 2026. IS = 2022-2024, OOS = 2025-March 2026.

### L13 — Finnhub parallel batch push conflicts
**Mistake:** Ran 5 Finnhub batches simultaneously on GitHub Actions. Each batch tried to push to main independently — push conflicts. Only batch 1 data committed.
**Learning:** Parallel git pushes to same branch always conflict. Each parallel job needs rebase before push.
**Fix:** Added `git pull --rebase origin main` before push. Per-batch checkpoint keys prevent duplicate work.

---

## Engine & Strategy

### L14 — Aggregate exit comparison, no per-trade detail
**Mistake:** Exit comparison only saved strategy-level aggregates. Impossible to see how different exits performed on a specific trade.
**Learning:** Always capture granular data. Aggregates can be recomputed; raw data cannot be recovered. (CHECKLIST item 11)
**Fix:** Added `trade_exit_detail.csv` — one row per trade × exit method. Full trade-level exit analysis now possible.

### L15 — Raw smart money signals not in trade log
**Mistake:** Only saved composite smart money score per trade. Couldn't audit why a trade got EXCEPTIONAL vs HIGH tier.
**Fix:** Added congressional_signal, insider_signal, institutional_signal, aaii_bullish, aaii_bearish, cnn_fg_score to ClosedTrade dataclass and trade_log.csv.

### L16 — Phase 1B universe not switching from 67 instruments
**Mistake:** `--phase 1b` flag existed but didn't change the universe from 67 to 509 instruments. Would have run Phase 1B on Phase 1A universe.
**Fix:** `run_phase1a.py` now loads full 509-instrument universe when `--phase 1b` is passed.

### L17 — Stop simulation described incorrectly
**Mistake:** Claimed results were pessimistic due to stop simulation. Actually slightly optimistic — gap-down opens fill at open price, not stop price.
**Learning:** Think through simulation logic before documenting it. Don't assume direction of bias.
**Fix:** Corrected in PROJECT_PLAN.md section 19.

### L18 — No batch testing before full Phase 1B run
**Mistake:** Attempted to run full Phase 1B on 509 instruments without first testing on 25 tickers for 1 month.
**Learning:** Always validate the full pipeline on a small sample before scaling. Catch bugs and bad agent outputs cheaply.
**Fix:** Added to CHECKLIST item 13. Phase 1B will run 25-ticker test first.

---

## Process & Workflow

### L19 — Commands not chained
**Mistake:** Gave separate commands for run, commit, push. Codespace timed out between commands, losing results.
**Learning:** Chain dependent commands. Commit+push always together. Long runs always use nohup.
**Fix:** CHECKLIST items 9 and 10. All run commands now include nohup and chained commit+push.

### L20 — CLAUDE.md modified without approval
**Mistake:** Rewrote CLAUDE.md from 128 to 62 lines without showing diff or getting approval. Removed useful context.
**Learning:** CLAUDE.md is the owner's document. Never modify without showing exact before/after diff.
**Fix:** Added explicit rule to CLAUDE.md and CHECKLIST item 6.

### L21 — Jumped ahead to Phase 1B download without approval
**Mistake:** Downloaded full S&P 500 cache for Phase 1B before Phase 1A results were reviewed.
**Learning:** Never jump ahead of the current phase. Each phase requires explicit owner approval.
**Fix:** Reinforced in CHECKLIST item 3 and CLAUDE.md standard of work.

---

## Optimizations Integrated

| # | Optimization | Impact |
|---|---|---|
| O1 | Parquet cache layer | OHLCV never re-downloaded — saves hours per session |
| O2 | devcontainer.json auto-install | pyarrow always available on Codespace start |
| O3 | Static sp500_tickers.csv | No Wikipedia dependency, works in all environments |
| O4 | Agent JSON cache | Agents never re-run — saves ~$116 CAD on reruns |
| O5 | Pre-fetch architecture | Agent runtime 35s → 2s per candidate |
| O6 | Chunk-commit pattern | Partial downloads safe — resume from checkpoint |
| O7 | nohup for all long runs | Terminal timeout never kills a running job |
| O8 | GitHub Actions for Finnhub/Quiver | No laptop needed for data downloads |
| O9 | Per-trade exit detail | Full audit trail for exit strategy decisions |
| O10 | Raw signals in trade log | Full audit trail for confidence tier decisions |
| O11 | IS/OOS trade log splits | Granular walk-forward analysis |
| O12 | Backtest extended to March 2026 | More data, better OOS validation |
| O13 | AAII/CNN full CSVs | Sentiment agent has real data not placeholders |
