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
| 3 | 13F holdings (institutional_new_positions and siblings) | backtest/data/smart_money.py:413 (per-ticker) and the bulk path both use ReportPeriod + 45 days | **LOOKAHEAD** (late filers; verified B3139q-r29) | `Date` is the SEC filing timestamp: 13 of 13 sampled rows that resolved on SEC match the 13F-HR filing (11 to the second, 2 by calendar date), 0 contradict; 15 of 28 sampled rows did not resolve (output_audit/b3139ay_13f_date_verification.json, S6-B3139ay). So the live ReportPeriod + 45 rule uses a late filing before it was public: in 60 non-empty per-ticker files (248,660 rows) 11.35% are filed after day 45 (median 43, p99 1321, max 6305 days), and filtering by filing date instead changes 894 of 1192 IS and 233 of 430 holdout bollinger values (measured B3139q-r22). DEC-325 (2026-05-11) already ruled the filing-date filter; the engine reconciliation is the owner's, S6-B3139bh |
| 4 | Axis TYPE: institutional_new_positions (B6) | producer_variant_table.py:2087 registers "require TRUE"; breadth_step1_grid._cell_mask reads eq_true as `== 1.0` | **MIS-SPECIFIED** | The signal is a COUNT (signal_loader.py:436), so the registered cell selects exactly-one-new-position fires, not any (S6-B3139az) |
| 5 | AAII sentiment | sentiment.py:92-100, `survey_date <= as_of - lag` | AVAILABILITY-LAGGED | Wednesday survey usable from Thursday (read, not measured) |
| 6 | CNN Fear and Greed | sentiment.py:244, `reading_date <= as_of` | same-day | Not audited further |
| 7 | defensive_leadership | backtest/signals/cross_asset.py:262-282, sector-ETF closes | PRICE-DERIVED | No publication lag |
| 8 | adx, bb_10_20_pctb, bb_20_15_pctb, below_ema_9/20/21/50, dc20_new_high, macd_12_26_9_line, pct_from_vwap | OHLCV bars | PRICE-DERIVED | Out of this class (no publication lag); the same-bar convention every gate shares is not audited here |
| 9 | Insider filings | smart_money.py:507-510 dates rows by fileDate (or Date) | FILING-DATED | Read, not measured |

## Formerly 'not yet classified' - every member below is classified in slice 2 (S6-B3139ba)

FRED / ALFRED macro series (backtest/data/macro.py), SEC fundamentals and earnings dates (the PEAD
family), congressional trading (disclosure lag up to 45 days), short interest's own
settlement-to-publication lag (S6-B3139d covers only its shares denominator), Wikipedia pageviews
(sentiment.py:402), news sentiment, Google Trends.

## What it means for bollinger_lower's Step 3

Two of its 13 axes are LOOKAHEAD (rows 1 and 3 - row 3 was DISPUTED until S6-B3139ay verified it at
B3139q-r29) and one is mis-specified (row 4). The holdout read (S6-B3139am) waits on the owner's choice for all three (S6-B3139ar).

## Slice 2 (S6-B3139ba, B3139q-r30, 2026-10-05)

**Method.** Each remaining producer's date filter was READ at its function; where a vintage record
exists (ALFRED), the gap between observation date and publication was MEASURED over
2022-05-05..2026-05-05 (scratchpad measure_fred_pit.py -> output_audit/b3139ba_fred_pit_measure.json).
Consumers were traced to the engine call site, not inferred from the producer.

| # | Producer (signal) | Date rule, READ | Class | Evidence / effect |
|---|---|---|---|---|
| 10 | FRED macro signals hy_oas / financial_stress / recession_probability / jobless_claims / fed_balance_sheet (macro.py macro_snapshot -> macro_score) | macro.py _fred_value_at: observations filtered `date <= as_of` over data_prefetch/fred/observations - the LATEST-REVISED values, never the ALFRED vintage path, although vintage caches exist for 4 of the 5 series | **LOOKAHEAD** (publication lag AND revision) | MEASURED from the ALFRED vintages: RECPROUSM156N is published 58-119 days after its observation date (median 61) and 97.8% of its 46 dates are later revised (up to 40 vintages); ICSA 4-54 days (median 5), 95.7% of 208 revised; WALCL 1-2 days, 0.0% revised; BAMLH0A0HYM2 same-day on 99.0% of 793 dates, none revised. Consumer: macro_score gates entry for 5 strategies via STRATEGY_REQUIRED_MACRO_REGIME (bollinger_tight, monthly_bias_momentum_long, xs_quality_top_quintile_long, pead_long, adx_initiation; backtest.py the _req_macro block) - 0 of 15 admitted Phase 1B lines are among them (grep of phase_1b_step2_admissions.json). Engine fix is the owner's: S6-B3139bi |
| 11 | yield_curve_regime (T10Y2Y) | macro.py get_yield_curve -> _fred_series(as_of=as_of) -> the ALFRED vintage filter `realtime_start <= as_of <= realtime_end` | VINTAGE-CORRECT | 5.0% of 955 dates published after their date and 72.7% revised - both handled by the vintage filter. Its fallback (FRED observations, no vintage) runs only on an ALFRED cache miss |
| 12 | financial_stress_signal (STLFSI4) | same _fred_value_at as row 10 | **LOOKAHEAD + VINTAGE CACHE GAP** | its ALFRED cache holds exactly 100,000 rows ending 2005-01-21, so the vintage path could not serve it either; NFCI's ends 2020-12-25 - 2 of 80 vintage caches end before the window, cause UNKNOWN - RCA NEEDED (S6-B3139bl). Lag unmeasurable from the cache |
| 13 | PEAD eps (compute_pead_signals, the yoy sleeves) | pead.py compute_pead_signals: `eps_df["filing_date"] <= as_of`, filing_date taken from each Polygon financials row | FILING-DATED | Read, not measured |
| 14 | earnings dates (fetcher.fetch_earnings_dates / days_to_next_earnings) | fetcher.py: earnings_date = fiscal end_date + 30 days, a PROXY (B998: the cache carries no announcement date) | PROXY, no publication question | an estimate knowable in advance; its error against the true announcement is the recorded B998 caveat, not an availability defect |
| 15 | congressional trading | smart_money.py congressional_signal: `disclosure_dt <= as_of` (DEC-324) | DISCLOSURE-DATED | Read, not measured |
| 16 | short interest - publication side (the shares denominator is S6-B3139bd) | short_interest.py compute_short_interest_signals: `settlement_date <= as_of`; the FINRA cache's columns are settlement_date, short_interest, shares_outstanding, avg_daily_volume - no dissemination date | **LOOKAHEAD** (lag unmeasured) | FINRA disseminates a settlement's figures days after the settlement date and the cache cannot say when. Consumer: strat_squeeze_setup_long layer 1. S6-B3139bj |
| 17 | Wikipedia pageviews | sentiment.py get_wikipedia_pageviews: `date <= as_of` | NOT CONSUMED by the engine | sentiment_snapshot is called without a ticker at backtest.py (the `sent = sentiment_snapshot(as_of)` line), so its ticker branch never runs |
| 18 | Apewisdom mentions | sentiment.py get_apewisdom_mentions takes no as_of - it reads the latest snapshot | NOT CONSUMED; NOT POINT-IN-TIME by construction | same branch as row 17; must gain an as_of before any consumer is wired. S6-B3139bk |
| 19 | news sentiment | news_sentiment.py compute_news_sentiment_signals: `published_date <= as_of` | PUBLICATION-DATED | Read, not measured |
| 20 | Google Trends (search_volume) | search_volume.py compute_search_volume_signals: `d <= as_of` on week-START dates (1,417 cached tickers; every date is a Sunday) - a week's index is readable from its first day | LOOKAHEAD-IF-CONSUMED (up to 6 days plus Google's own delay) | 0 strategy gates read its keys: the only screener hits are the injector call (inject_search_volume_signals) |

**What it means.** Of the 11 producers in this slice, 3 carry a live look-ahead in an engine path
(rows 10, 12 and 16), 1 is a look-ahead with no consumer (row 20), 2 are not consumed (rows 17-18, one
of them not point-in-time at all), and 5 are sound or proxies by design (rows 11, 13, 14, 15, 19).
No admitted Phase 1B line gates on any of the three live look-aheads.
