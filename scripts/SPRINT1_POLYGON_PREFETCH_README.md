# Sprint 1 — Polygon Prefetch (Phase 0.A)

**Pass 53 turn — hybrid path (Path A tonight + Path B tomorrow).**

## Honest scope flag

This prefetch operates on `backtest/data/sp500_tickers.csv` (484 current-state S&P 500 tickers), NOT the full DEC-483 universe (T1a + T1b + T1c = ~1015 tickers).

The proper universe build (DEC-477 historical_membership.csv B++ format — single static CSV with `added_date`/`removed_date` columns + R1000 + NDX same format with year-grain dates) is deferred to a separate work session per Pass 53 turn discussion. **This is acknowledged survivorship bias for the data cache built tonight** — addressed in tomorrow's universe-build session.

When the proper universe files are built, an additional ~531 tickers (T1b R1000-non-S&P + T1c NDX-non-S&P + historical-S&P-delisted) will need supplementary prefetch.

## Decisions covered

Per Sprint 1 ENGINEERING_REGISTER scope:

| DEC | Description | Status post-prefetch |
|---|---|---|
| DEC-441 | Polygon Stocks Starter $29/mo | ✅ Subscribed; key in `.env` |
| DEC-256 | Polygon earnings prefetch | Earnings dates available via news endpoint metadata; explicit earnings calendar prefetch deferred (Polygon Stocks Starter doesn't include `/vX/reference/financials`) |
| DEC-257 | Polygon→yfinance fundamentals | Reference-only; full financials deferred to Sprint 4 SEC EDGAR (DEC-484) |
| DEC-440 | Polygon news endpoint | ✅ Covered by `prefetch_polygon_news.py` |
| DEC-260 | Cache freshness assertion | Cache populated; assertion logic in code (separate ticket) |
| DEC-261 | ICT/SMC PIT N+1 lag rule | Not consumed by prefetch; consumed by strategy code |
| DEC-040 | PointInTimeLoader structural framework | Not consumed by prefetch; depends on this cache as input |
| DEC-477 | historical_membership.csv canonical | **DEFERRED to tomorrow** — using sp500_tickers.csv tonight |
| DEC-478 | Polygon Stocks Starter $29/mo | ✅ |
| DEC-479 | Cost correction $30→$29 | ✅ Documentation only |
| DEC-483 | T1a/T1b/T1c sub-tiers | **DEFERRED to tomorrow** — T1a only tonight |

## Pre-requisites

- ✅ Polygon Stocks Starter $29/mo subscription active
- ✅ `POLYGON_API_KEY` in `.env` at repo root
- ✅ Python 3.11+ with `pandas`, `requests`, `python-dotenv`, `pyarrow` installed

If pyarrow is missing:
```bash
pip install pyarrow python-dotenv requests pandas
```

## How to run

### Step 1 — Smoke test (5 minutes)

```bash
python scripts/smoke_test_polygon.py
```

Verifies all 5 endpoints respond HTTP 200. Required first step.

### Step 2 — Small-scale 5-ticker test (10-15 minutes) **[REQUIRED before full prefetch]**

Per CHECKLIST #64 (artifact-state verification): test the full prefetch+write+checkpoint pipeline on 5 real tickers (AAPL, MSFT, GOOGL, JPM, XOM) before scaling to 484.

```bash
bash scripts/run_polygon_5ticker_test.sh
```

Then verify the output:

```bash
python scripts/verify_polygon_test_output.py
```

The verification script runs ~30 checks (file counts, schema integrity, content sanity, pagination evidence, checkpoint validity). Exits 0 only if all pass.

**Do NOT run full prefetch until the verification script returns ✅ ALL CHECKS PASSED and owner reviews the output.**

### Step 3 — Full prefetch (4-7 hours) — only after Step 2 passes

#### Option 3a — Orchestrator (recommended)

```bash
bash scripts/run_polygon_prefetch_all.sh
```

#### Option 3b — Individual scripts

```bash
# Daily OHLCV — main backbone (~30-60 min)
python scripts/prefetch_polygon_ohlcv_daily.py

# Reference details (~5-10 min)
python scripts/prefetch_polygon_reference.py

# Corporate actions (~5-10 min)
python scripts/prefetch_polygon_corp_actions.py

# News (~3-5 hours)
python scripts/prefetch_polygon_news.py
```

All scripts are checkpointed — safe to interrupt and resume. Note: if you've already run the small-scale test, the OHLCV + News scripts will skip the 5 test tickers (already in checkpoint). Only the remaining 479 will be fetched.

## Output structure

After successful prefetch:

```
backtest/data/cache/polygon/
├── ohlcv_daily/
│   ├── AAPL.parquet
│   ├── MSFT.parquet
│   └── ... (484 files)
├── reference/
│   ├── AAPL.parquet
│   ├── MSFT.parquet
│   └── ... (484 files)
├── reference_index.parquet     ← combined index of all 484 ticker references
├── splits/
│   └── all_splits.parquet
├── dividends/
│   └── all_dividends.parquet
├── news/
│   ├── AAPL.parquet
│   ├── MSFT.parquet
│   └── ... (484 files)
├── _checkpoint_ohlcv.json
└── _checkpoint_news.json
```

Estimated total size: ~7-12 GB (mostly news; OHLCV is small ~2-3 GB).

## Schema details

### OHLCV daily

```
ticker         str        AAPL
date           date       2021-05-04
open           float      131.65
high           float      132.65
low            float      131.40
close          float      132.54
volume         int        56,415,400
vwap           float      132.012
transactions   int        524,123
```

### Reference

```
ticker, name, market_cap, share_class_shares_outstanding, weighted_shares_outstanding,
sic_code, sic_description, primary_exchange, type, active, currency_name, cik,
list_date, delisted_utc, homepage_url, fetched_at
```

### Splits

```
ticker, execution_date, split_from, split_to
```

### Dividends

```
ticker, ex_dividend_date, declaration_date, pay_date, record_date, cash_amount,
currency, dividend_type, frequency
```

### News

```
ticker, id, published_utc, title, description, article_url, amp_url,
publisher_name, publisher_homepage_url, sentiment, sentiment_reasoning, all_tickers
```

## After prefetch — commit to main

```bash
# Verify cache size
du -sh backtest/data/cache/polygon/

# Stage + commit + push
git add backtest/data/cache/polygon/
git commit -m "Sprint 1: Polygon prefetch (484 tickers × 5y daily OHLCV + ref + corp actions + news)"
git push origin main
```

GitHub note: cache is ~7-12 GB total. GitHub allows 100 GB per repo, individual files up to 100 MB (>100 MB triggers warning, >2 GB blocks). Per-ticker Parquet files are typically 50-500 KB each, well within limits.

## What's NOT in this prefetch (deferred)

| Data | Why deferred | Where it goes |
|---|---|---|
| Full universe (T1b R1000 + T1c NDX) | Universe build is separate work | Tomorrow + supplementary prefetch |
| Polygon 1-min OHLCV | ~50-100 GB; not needed for daily-resolution Phase 1A | Post-Phase-1A-α if needed |
| Polygon financials (`/vX/reference/financials`) | Not in Stocks Starter tier | Sprint 4 SEC EDGAR per DEC-484 |
| Polygon options data | Not in scope (Stage 3+ per DEC-454/Unusual-Whales-deferred) | Stage 3+ |
| Quiver paid endpoints | Tomorrow per owner directive | Tomorrow |
| FRED macro | Already exists per `prefetch_macro.py` | (already cached) |
| AAII + CNN F&G sentiment | Already exists | (already cached) |

## Troubleshooting

**`401 Unauthorized`** — `POLYGON_API_KEY` is wrong or `.env` not being loaded. Verify with `cat .env` and re-run smoke test.

**`429 Too Many Requests`** — Should not happen on Stocks Starter (unlimited). If it does, increase `RATE_LIMIT_SLEEP` constant in scripts.

**`403 Forbidden`** — Subscription tier doesn't cover endpoint. For news/aggregates/reference/splits/dividends this should not happen on Stocks Starter. If you see 403 on these endpoints, your subscription may not be active — check polygon.io dashboard.

**Script interrupted** — Re-run; checkpoint files (`_checkpoint_*.json`) skip already-completed tickers.

**Pyarrow installation issue on Windows** — try `pip install pyarrow --upgrade --no-cache-dir`. If still fails, fastparquet is alternative: `pip install fastparquet` and replace `compression="snappy"` with `compression="gzip"` in scripts (Snappy may need Visual Studio C++ build tools on Windows).

## Tomorrow's work

After Polygon prefetch is committed to main, next session:

1. **Build universe files (DEC-477 + DEC-483 — B++ format Pass 53):**
   - `data/universe/historical_membership.csv` (S&P 500 — single CSV, columns `Symbol, Company, Sector, added_date, removed_date`; PIT loader filters by `(added_date IS NULL OR added_date ≤ as_of) AND (removed_date IS NULL OR removed_date > as_of)`)
     - **Primary source:** S&P Dow Jones Indices press releases (`spglobal.com/spdji` — authoritative for every S&P 500 add/remove with effective dates)
     - **Fallback source (Pass 53 one-time L88 exception, owner-granted):** Wikipedia "List of S&P 500 companies" Selected-changes table + general internet browse — used only if S&P DJI archives have gaps; manual verification before commit
     - **Mapping timeframe:** 2020-01-01 → today + ongoing for Stage 3 (Polygon Stocks Starter cache window is 5y backward = 2021-05; 1-year buffer ensures every ticker active in cache window has a verifiable `added_date`)
     - **Pre-2020 active tickers** (e.g., MMM/JNJ/KO): leave `added_date` NULL — meaning "in S&P prior to mapping window"; PIT loader handles null via the filter expression above (Pass 53 option-β)
   - `data/universe/russell_1000_membership.csv` (T1b — same B++ format with year-grain dates from FTSE Russell)
   - `data/universe/nasdaq_100_membership.csv` (T1c — same B++ format with year-grain dates from Nasdaq)
   - `data/universe/index_rebalance_events.parquet` (day-grain via SEC EDGAR for DEC-368 — separate file since rebalance events strategy needs effective-date grain)

2. **Supplementary Polygon prefetch** for T1b + T1c + historical-S&P-delisted (~531 net new tickers)

3. **Quiver paid endpoint prefetch** (all 13 endpoints; ~14-18 GB)

4. **Sprint 1 verification:** end-to-end smoke test that reads cache + universe + runs DEC-040 PIT loader sample query

After all 4: Sprint 1 RESOLVED-IMPLEMENTED → Sprint 2 (engine bug fixes) begins.
