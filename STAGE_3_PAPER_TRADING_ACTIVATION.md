<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1233 2026-07-07 doc-sync sweep -->

<!-- 🟢 COUNCIL 278-287 SYNC BANNER (B1233 2026-07-07) — READ FIRST BEFORE THIS DOC -->
> **Doc-sync status:** This document may contain references stale as of 2026-06-27 or earlier. The current state below overrides any stale references in the body until the next full-rewrite.
>
> **Current canonical values (as of 2026-07-07 B1231):**
> - `len(ALL_STRATEGIES) = 219` (was 220 pre-B1189 DELETE of dxy_headwind_multinational_short; was 221 pre-B874)
> - `STRATEGIES_DISABLED_MISSING_PRODUCER = set()` (was `{dxy_headwind_multinational_short}` pre-B1189)
> - Active strategies for Phase 1A-β cube: 219; cube cells 219×26 = 5,694
> - Test count: **880 passed, 2 skipped** on `test_unit.py + test_integration.py`
> - **CHECKLIST items:** #1–#157 (added #151-#157 in Councils 279-285)
> - **LEARNINGS lessons:** through L209 (added L197-L202 in Councils 279-285)
> - **Latest batch:** B1310 (Council 342)
>
> **Recent Council 278-287 milestones (chronological):**
> - Council 278 (B1188-B1204): 40 SKIP strategies loosened per CSV recommendations
> - Council 279 (B1205-B1210): 11 silent misses remediated + L197 + CHECKLIST #151-#153
> - Council 280 (B1211-B1213): News coverage refined (84.2%) + CHECKLIST #154 codified
> - Council 281 (B1214-B1216): short_interest_pct producer bug + institutional 30% gap surfaced
> - Council 282 (B1217-B1219): Cross-audit 192 strategies + CHECKLIST #155
> - Council 283 (B1220-B1223): 5 more producer audits + comprehensive report
> - Council 284 (B1224-B1228): All 25+ producers audited + historical 2020-2023 spot-check + L201 + CHECKLIST #156
> - Council 285 (B1229-B1231): 2 critical bugs FIXED with graceful degradation + L202 + CHECKLIST #157
> - Council 287 (B1232-B1236 in progress): Stage 4 walks archived + doc-sync sweep
>
> **Stage 4 walks: ARCHIVED 2026-07-07 to `archive/2026-07-07-stage-4-walks-complete/`** (Council 121+ 2026-06-27 owner-approved completion). Any `STAGE_4_*.md` reference in this doc now points to archived location.
>
> **Producer coverage (all 25+ producers audited Councils 280-284):**
> - news_sentiment 84.2% / short_interest_dtc 97.7% / **short_interest_pct 0%** (bug; graceful-degradation fix in B1229) / pead 85% / insider 18.8% (event-rarity) / **institutional_signal 85%** (B1230 corrected from B1216's 30% misattribution) / congressional 67.7% / sec_edgar 97.7% / search_volume 99.2% / index_rebalance 10.5% (event) / earnings_yoy 78.9% / cot_positioning 100% / cross_asset 100% (5 fns) / calendar_effects 100% / macro_events 100% / OHLCV-derived (chart_patterns/technical/dec513/multi_timeframe/cross_sectional/ict_producers/volume_profile/smc_ict/pairs_trading) all 100% (bounded by ~84% OHLCV cache)
> - **Critical historical finding (B1227):** news_sentiment 0% in 2020; short_interest_dtc 0% in 2020; institutional 0% in 2020-2021. Backtest interpretation must annotate producer coverage TIMELINE.
>
> **Sprint 5 tickets queued (post-Council 285 priorities):**
> - S5-B1214-SHARES-OUTSTANDING (HIGH; 1 strategy; 1d) - remove B1229 fallback when data ships
> - S5-B1216-INSTITUTIONAL-13F (MED after B1230 correction; 1 strategy; 1-2d) - expand T1a persistence file
> - S5-B1212-SECONDARY-NEWS (MED; 6 strategies; 2d) - Finnhub/AlphaVantage fallback
>
> **Comprehensive coverage report:** `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# Stage 3 — Paper Trading Activation Runbook (G22)

> **B1029 doc-sync 2026-06-27:** Prerequisite `winners.parquet` = **BLOCKED-PENDING-R5-COMPLETE**. R5 LAUNCHED 2026-06-27 B1028 on AWS i-0940a53c75d049381 (Master 1929 ops × 4y window). Activation gated on R5 cube completion + verdict. ETA per cube wall-clock estimate ~3-4 hr post-launch.

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
