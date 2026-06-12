# B737 Decision 4 Confronting-Tests Report (2026-06-12)

# Source: scripts/run_b737_confronting_tests.py per CHECKLIST #77

Universe: 30 alphabetical T1a PIT-active tickers (['A', 'AAPL', 'ABBV', 'ABNB', 'ABT'] ...).
Train through 2023-12-31; test from 2024-01-01. Barrier race: +2x ATR target, -1x ATR stop, 10-bar horizon.
OOS-watchdog (B734) thresholds: REJECT_OVERFIT fires when |train_ft - test_ft| > 0.10 AND test_lift < 0.03.

## Sequenced verdict summary

| Test | Verdict | base_test_ft | with_test_ft | lift | train_test_gap | with_test_n |
|---|---|---:|---:|---:|---:|---:|
| A1_PEAD_LONG_gap_conditioning | **REJECT_REDUNDANT** | 0.3318 | 0.3301 | -0.0017 | 0.0212 | 5565 |
| A2_PEAD_SHORT_gap_conditioning | **REJECT_REDUNDANT** | 0.3018 | 0.3053 | 0.0035 | -0.0161 | 6616 |
| C1_week_gap_size_band_long | **REJECT_REDUNDANT** | 0.3484 | 0.3607 | 0.0123 | -0.0398 | 122 |
| C2_week_gap_earnings_filter_long | **ADD** | 0.3484 | 0.3814 | 0.033 | -0.0499 | 118 |
| C3_week_gap_trend_context_long | **REJECT_REDUNDANT** | 0.3484 | 0.3651 | 0.0167 | -0.0664 | 63 |

## A1: PEAD LONG gap-conditioning

**Verdict: REJECT_REDUNDANT**
  - no FT lift (0.332->0.330, -0.002); gate doesn't earn its slot

## A2: PEAD SHORT gap-conditioning (mirror)

**Verdict: REJECT_REDUNDANT**
  - no FT lift (0.302->0.305, +0.004); gate doesn't earn its slot

## B1: FOMC SPY Lucca-Moench survival (2022-2026)

**Verdict: FAIL**
  - SPY mean pre-FOMC return +5.7bp; p_one_sided=0.401; on n=35 FOMC dates 2022-2026 -- effect does NOT clearly survive (Mueller-Tahbaz-Salehi 2017 weakening era confirmed)
  - n FOMC dates measured: 35
  - SPY mean pre-FOMC return: 5.73 bp (Lucca-Moench baseline +50 bp)
  - One-sided p-value: 0.4012

## B2: FOMC single-stock beta-decile

**SKIPPED** -- gated on B1 PASS; B1 did not pass.

## C1: Week-gap size band (gap_pct > -0.03 on gap-down-fade-long)

**Verdict: REJECT_REDUNDANT**
  - no FT lift (0.348->0.361, +0.012); gate doesn't earn its slot

## C2: Week-gap earnings filter (NOT earnings_last_2d)

**Verdict: ADD**
  - lifts FT 0.348->0.381 (+0.033); train gap -0.050; n_test=118

## C3: Week-gap trend context (price_above_ema200 AND-required)

**Verdict: REJECT_REDUNDANT**
  - no FT lift (0.348->0.365, +0.017); gate doesn't earn its slot

---

## Proxy disclosures (each test states its assumption)

- **A1/A2 PEAD ANN-day proxy**: |daily_return| > 5% bar; positive sign = up; PEAD window = bars 1-60 after ANN. Production producer uses real EPS data + SUE; this proxy uses price-move-based detection. The confronting test asks 'does gap-conditioning lift FT given the existing entry mechanism?' -- the answer transfers if the production producer's FT curve has the same monotonicity in gap_pct.
- **B1/B2 FOMC**: real FOMC_DATES from backtest/data/macro.py (40 dates 2022-2026); SPY OHLCV from polygon prefetch. No proxy.
- **C1/C2/C3 Week-gap proxy**: ICT-11/12 production uses ict_producers.compute_week_opening_gap_signals with week_open_gap_up_15pct / week_open_gap_dn_15pct (gap_pct >= 1.5%). Our proxy uses gap-pct ratio at first trading day of ISO week + same 1.5% threshold. Equivalent on regular Monday opens; differs on Monday-holiday weeks where production uses Tuesday open.
- **C2 earnings proxy**: |daily_return|>5% in last 2 trading days. Production uses real earnings calendar.
- **C3 trend proxy**: EMA-200 from close-only EMA. Production uses identical EMA-200.

## Owner action by verdict

| Verdict | Action |
|---|---|
| ADD | wire the gate to the named production strategy |
| REJECT_HARMFUL | do NOT wire; gate hurts |
| REJECT_REDUNDANT | do NOT wire; gate doesn't earn its slot |
| REJECT_OVERFIT | do NOT wire; train edge does not persist OOS |
| DEFER | insufficient sample; revisit post-B660 fire-count run |
