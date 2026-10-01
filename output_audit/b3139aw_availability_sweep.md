# S6-B3139aw - availability sweep, slice 1 (B3139q-r22, 2026-10-01)

**Question.** Which signal producers date their data by when it was OBSERVED rather than when it
was PUBLISHED - so a backtest reads it before it was knowable? Slice 1 covers the producers behind
bollinger_lower's 13 Step-3 breadth axes, plus the non-price producers read on the way. The
remainder is S6-B3139ba.

**Method.** Each producer's date filter was READ at file:line. Where a value feeds bollinger's
grid, the effect was MEASURED on bollinger's own 1622 R5 fires after first reproducing the stored
values with the live function (1622 of 1622 in both measured cases). Scripts: scratchpad
measure_cot_pit.py, regrade_cot_lagged.py, measure_13f_filing_lag.py, measure_13f_pit_bollinger.py.

## Classification

| # | Producer (signal) | Date rule, READ | Class | Evidence / effect |
|---|---|---|---|---|
| 1 | COT positioning (cot_rut_commercials_net_pct and siblings) | backtest/signals/cot_positioning.py:134 filters on the Tuesday positions date; screener.py:9093 passes as_of through | **LOOKAHEAD** | Friday release (the module's own docstring, line 7). 366 of 1192 IS and 269 of 430 holdout bollinger values change under a 3-day lag; the long leg's rank-1 cell moves 120 -> 44 members (S6-B3139ar/as) |
| 2 | COT report in the engine's sentiment snapshot | backtest/data/sentiment.py:454 filters `report_date <= as_of`; reached from backtest/engine/backtest.py:2716 via sentiment_snapshot (sentiment.py:540) | **LOOKAHEAD** (same rule) | The file's own comment, line 295: "released every Friday for prior Tuesday positioning". Whether this value reaches an entry decision is NOT traced (S6-B3139as now covers both producers) |
| 3 | 13F holdings (institutional_new_positions and siblings) | backtest/data/smart_money.py:413 (per-ticker) and the bulk path both use ReportPeriod + 45 days | **DISPUTED** | scripts/build_13f_depth_precompute.py:29/:70 dates the same rows by their own `Date` column as the filing date. In 60 non-empty per-ticker files (248,660 rows) 11.35% are dated after day 45 (median 43, p99 1321, max 6305 days). Re-run with "filed by as_of" added, 894 of 1192 IS and 233 of 430 holdout bollinger values change. What `Date` holds is UNVERIFIED - the multi-year gaps fit amendments or vendor dates as well as filings (S6-B3139ay) |
| 4 | Axis TYPE: institutional_new_positions (B6) | producer_variant_table.py:2087 registers "require TRUE"; breadth_step1_grid._cell_mask reads eq_true as `== 1.0` | **MIS-SPECIFIED** | The signal is a COUNT (signal_loader.py:436), so the registered cell selects exactly-one-new-position fires, not any (S6-B3139az) |
| 5 | AAII sentiment | sentiment.py:92-100, `survey_date <= as_of - lag` | AVAILABILITY-LAGGED | Wednesday survey usable from Thursday (read, not measured) |
| 6 | CNN Fear and Greed | sentiment.py:244, `reading_date <= as_of` | same-day | Not audited further |
| 7 | defensive_leadership | backtest/signals/cross_asset.py:262-282, sector-ETF closes | PRICE-DERIVED | No publication lag |
| 8 | adx, bb_10_20_pctb, bb_20_15_pctb, below_ema_9/20/21/50, dc20_new_high, macd_12_26_9_line, pct_from_vwap | OHLCV bars | PRICE-DERIVED | Out of this class (no publication lag); the same-bar convention every gate shares is not audited here |
| 9 | Insider filings | smart_money.py:507-510 dates rows by fileDate (or Date) | FILING-DATED | Read, not measured |

## Not yet classified (S6-B3139ba)

FRED / ALFRED macro series (backtest/data/macro.py), SEC fundamentals and earnings dates (the PEAD
family), congressional trading (disclosure lag up to 45 days), short interest's own
settlement-to-publication lag (S6-B3139d covers only its shares denominator), Wikipedia pageviews
(sentiment.py:402), news sentiment, Google Trends.

## What it means for bollinger_lower's Step 3

Two of its 13 axes carry an open availability question (rows 1 and 3) and one is mis-specified
(row 4). The holdout read (S6-B3139am) waits on the owner's choice for all three (S6-B3139ar).
