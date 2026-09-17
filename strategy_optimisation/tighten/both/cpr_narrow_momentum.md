# Table A - cpr_narrow_momentum

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:07:43 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** confluence | **status:** NOT-STARTED | **R5 fires:** 1001 | **surviving fires (T1):** 1001 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  above_cpr  <- backtest/signals/screener.py +1
       DEFN: today's price above cpr_top / below cpr_bottom (technical.py:146 region)
       knobs P1.1-P1.1 (band rows in Table A)
P2  below_cpr  <- backtest/signals/screener.py +1
       DEFN: today's price below cpr_bottom (technical.py:146)
       knobs P2.1-P2.1 (band rows in Table A)
P3  below_ema_200  <- backtest/signals/screener.py
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P3.1-P3.1 (band rows in Table A)
P4  cpr_narrow_tight  <- backtest/signals/screener.py +1
       DEFN: CPR width < 0.05 x prior range - the B654 tight local variant (technical.py:103)
       knobs P4.1-P4.1 (band rows in Table A)
P5  macd_12_26_9_bearish  <- backtest/signals/screener.py
       DEFN: MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)
       knobs P5.1-P5.1 (band rows in Table A)
P6  macd_12_26_9_bullish  <- backtest/signals/screener.py
       DEFN: MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)
       knobs P6.1-P6.1 (band rows in Table A)
P7  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P7.1-P7.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P8  rsi_14 < 50   [EXISTING-THRESHOLD]
P9  rsi_14 > 50   [EXISTING-THRESHOLD]
P10  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_cpr_narrow_momentum (docstring and return dropped):

```python
above_200 = s.get('price_above_ema_200', False)
below_200 = s.get('below_ema_200', False)
fl = s.get('cpr_narrow_tight') and s.get('above_cpr') and (s.get('rsi_14', 50) > 50) and s.get('macd_12_26_9_bullish') and above_200
fs = s.get('cpr_narrow_tight') and s.get('below_cpr') and (s.get('rsi_14', 50) < 50) and s.get('macd_12_26_9_bearish') and below_200 and (not _short_borrow_trap_active(s))
```

## Table A - parameter inventory (canonical shape - READY FOR OWNER BAND REVIEW)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close).
Every producer row carries its DEFINED BANDS in the P<n>.x rows beneath
it (B2845, owner-corrected: a ready and FINAL Table A per strategy);
the engine-spec (SPECS) entry is built from these before any engine
leg runs.

| id | layer | producer / parameter | what it does | production | band VALUES | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|---|---|
| P1 | PRODUCER | above_cpr - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | today's price above cpr_top / below cpr_bottom (technical.py:146 region) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | buffer pct (price vs cpr_top) - backtest/signals/technical.py:146 region | BRACKET zero; strict inequality today | 0.0 | [0, 0.25, 0.5] | none - today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | below_cpr - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | today's price below cpr_bottom (technical.py:146) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | buffer pct (price below cpr_bottom by) - backtest/signals/technical.py:146 | BRACKET zero | 0.0 | 0, 0.25 | none - entry price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | below_ema_200 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | cpr_narrow_tight - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | CPR width < 0.05 x prior range - the B654 tight local variant (technical.py:103) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | width threshold (cpr_width < rng * X) - backtest/signals/technical.py:103 | BRACKET production (B654 local 0.05; the family's 0.15 stays with its own consumers) | 0.05 | 0.03, 0.05, 0.08 | none - cpr_width IS persisted but the denominator (prior-day range) is not | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | PRODUCER | macd_12_26_9_bearish - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | span triple (fast, slow, signal) - backtest/signals/technical.py:634-648 | MEASURED availability - both triples are emitted and macd_8_21_5_* IS persisted | (12,26,9) | [(8,21,5), (12,26,9)] both computed in production; other triples are new | the (8,21,5) SWAP - re-evaluate on persisted macd_8_21_5 keys | any third triple; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | PRODUCER | macd_12_26_9_bullish - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P6.x) | BANDS-DEFINED |
| P6.1 | BAND | span triple (mirror of the bearish entry) - backtest/signals/technical.py:634-648 | MEASURED availability (both persisted) | (12,26,9) | [(8,21,5), (12,26,9)] both computed; others new | the (8,21,5) swap on persisted keys | any third triple; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P7.x) | BANDS-DEFINED |
| P7.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P8 | STRATEGY | rsi_14 `< 50` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 50` | production + 3 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P8.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P9 | STRATEGY | rsi_14 `> 50` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 50` | production + 1 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P9.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P10 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 50` | 100.0% | TIGHTER = LOWER the ceiling: 31.39 -> 201 (20%); 37.86 -> 401 (40%); 43.49 -> 601 (60%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `> 50` | 100.0% | TIGHTER = RAISE the floor: 57.3 -> 201 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.92, 20.31, 23.98, 29.62 | 16.92: 801 (80%); 20.31: 602 (60%); 23.98: 402 (40%); 29.62: 201 (20%) | 16.92: 202 (20%); 20.31: 401 (40%); 23.98: 601 (60%); 29.62: 801 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 20.12, 25.55, 29.96, 34.74 | 20.12: 801 (80%); 25.55: 601 (60%); 29.96: 402 (40%); 34.74: 201 (20%) | 20.12: 201 (20%); 25.55: 401 (40%); 29.96: 601 (60%); 34.74: 801 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.87, 17.02, 20.64, 26.45 | 13.87: 801 (80%); 17.02: 601 (60%); 20.64: 401 (40%); 26.45: 201 (20%) | 13.87: 201 (20%); 17.02: 401 (40%); 20.64: 601 (60%); 26.45: 801 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -8.5271, -3.2516, -0.8387, 1.4153 | -8.5271: 801 (80%); -3.2516: 601 (60%); -0.8387: 401 (40%); 1.4153: 201 (20%) | -8.5271: 201 (20%); -3.2516: 401 (40%); -0.8387: 601 (60%); 1.4153: 801 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.1821, 2.1372, 3.5057, 6.0935 | 1.1821: 801 (80%); 2.1372: 601 (60%); 3.5057: 401 (40%); 6.0935: 201 (20%) | 1.1821: 201 (20%); 2.1372: 401 (40%); 3.5057: 601 (60%); 6.0935: 801 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.1821, 2.1372, 3.5057, 6.0935 | 1.1821: 801 (80%); 2.1372: 601 (60%); 3.5057: 401 (40%); 6.0935: 201 (20%) | 1.1821: 201 (20%); 2.1372: 401 (40%); 3.5057: 601 (60%); 6.0935: 801 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.21, 2.709, 3.24, 4.125 | 2.21: 801 (80%); 2.709: 601 (60%); 3.24: 401 (40%); 4.125: 201 (20%) | 2.21: 201 (20%); 2.709: 401 (40%); 3.24: 601 (60%); 4.125: 801 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0663, 0.0923, 0.129, 0.1829 | 0.0663: 801 (80%); 0.0923: 602 (60%); 0.129: 401 (40%); 0.1829: 201 (20%) | 0.0663: 202 (20%); 0.0923: 401 (40%); 0.129: 602 (60%); 0.1829: 801 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.0866, 0.1908, 0.3671, 0.7727 | 0.0866: 801 (80%); 0.1908: 601 (60%); 0.3671: 401 (40%); 0.7727: 201 (20%) | 0.0866: 201 (20%); 0.1908: 401 (40%); 0.3671: 601 (60%); 0.7727: 801 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.07, 0.0972, 0.1235, 0.1684 | 0.07: 801 (80%); 0.0972: 601 (60%); 0.1235: 401 (40%); 0.1684: 202 (20%) | 0.07: 202 (20%); 0.0972: 402 (40%); 0.1235: 601 (60%); 0.1684: 801 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.1594, 0.031, 0.1932, 0.9043 | -0.1594: 801 (80%); 0.031: 601 (60%); 0.1932: 401 (40%); 0.9043: 201 (20%) | -0.1594: 201 (20%); 0.031: 401 (40%); 0.1932: 601 (60%); 0.9043: 801 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0933, 0.1296, 0.1647, 0.2246 | 0.0933: 801 (80%); 0.1296: 601 (60%); 0.1647: 401 (40%); 0.2246: 201 (20%) | 0.0933: 201 (20%); 0.1296: 402 (40%); 0.1647: 601 (60%); 0.2246: 801 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0055, 0.1482, 0.2699, 0.8033 | 0.0055: 801 (80%); 0.1482: 601 (60%); 0.2699: 401 (40%); 0.8033: 201 (20%) | 0.0055: 201 (20%); 0.1482: 401 (40%); 0.2699: 601 (60%); 0.8033: 802 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0442, -0.0142, 0.0077, 0.0381 | -0.0442: 803 (80%); -0.0142: 602 (60%); 0.0077: 404 (40%); 0.0381: 201 (20%) | -0.0442: 201 (20%); -0.0142: 401 (40%); 0.0077: 601 (60%); 0.0381: 803 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1437, 0.1712, 0.2054, 0.2664 | 0.1437: 798 (80%); 0.1712: 600 (60%); 0.2054: 400 (40%); 0.2664: 205 (20%) | 0.1437: 203 (20%); 0.1712: 401 (40%); 0.2054: 601 (60%); 0.2664: 796 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1001 (100%) | 0: 950 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1267, -0.061, 0.0178, 0.1053 | -0.1267: 801 (80%); -0.061: 601 (60%); 0.0178: 401 (40%); 0.1053: 201 (20%) | -0.1267: 201 (20%); -0.061: 401 (40%); 0.0178: 601 (60%); 0.1053: 801 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1001 (100%); 1: 413 (41%) | 0: 588 (59%); 1: 838 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2365, -0.1896, -0.1481, -0.1141 | -0.2365: 807 (81%); -0.1896: 603 (60%); -0.1481: 410 (41%); -0.1141: 229 (23%) | -0.2365: 203 (20%); -0.1896: 404 (40%); -0.1481: 609 (61%); -0.1141: 830 (83%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.391, 0.6346, 0.7244, 0.7692 | 0.391: 805 (80%); 0.6346: 607 (61%); 0.7244: 412 (41%); 0.7692: 237 (24%) | 0.391: 203 (20%); 0.6346: 410 (41%); 0.7244: 613 (61%); 0.7692: 830 (83%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.3846, 0.6026, 0.8397 | 0.2628: 803 (80%); 0.3846: 602 (60%); 0.6026: 406 (41%); 0.8397: 202 (20%) | 0.2628: 226 (23%); 0.3846: 407 (41%); 0.6026: 601 (60%); 0.8397: 803 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0712, 0.0136, 0.0836, 0.1972 | -0.0712: 805 (80%); 0.0136: 603 (60%); 0.0836: 403 (40%); 0.1972: 201 (20%) | -0.0712: 201 (20%); 0.0136: 406 (41%); 0.0836: 608 (61%); 0.1972: 807 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3269, 0.4872, 0.5897, 0.7949 | 0.3269: 804 (80%); 0.4872: 602 (60%); 0.5897: 419 (42%); 0.7949: 203 (20%) | 0.3269: 201 (20%); 0.4872: 458 (46%); 0.5897: 614 (61%); 0.7949: 802 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.3013, 0.4551, 0.6282 | 0.1282: 802 (80%); 0.3013: 601 (60%); 0.4551: 461 (46%); 0.6282: 209 (21%) | 0.1282: 205 (20%); 0.3013: 403 (40%); 0.4551: 615 (61%); 0.6282: 801 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.497, -0.3426, -0.1283, 0.056 | -0.497: 802 (80%); -0.3426: 605 (60%); -0.1283: 406 (41%); 0.056: 206 (21%) | -0.497: 222 (22%); -0.3426: 405 (40%); -0.1283: 601 (60%); 0.056: 802 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5321, 0.7628, 0.9167 | 0.3397: 805 (80%); 0.5321: 604 (60%); 0.7628: 401 (40%); 0.9167: 224 (22%) | 0.3397: 206 (21%); 0.5321: 437 (44%); 0.7628: 605 (60%); 0.9167: 819 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.359, 0.5897, 0.8526 | 0.1538: 804 (80%); 0.359: 605 (60%); 0.5897: 409 (41%); 0.8526: 224 (22%) | 0.1538: 207 (21%); 0.359: 405 (40%); 0.5897: 603 (60%); 0.8526: 835 (83%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0654, -0.0572, -0.0372, 0 | -0.0654: 802 (80%); -0.0572: 604 (60%); -0.0372: 405 (40%); 0: 318 (32%) | -0.0654: 202 (20%); -0.0572: 402 (40%); -0.0372: 605 (60%); 0: 972 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4487, 0.7244, 0.8846, 1 | 0.4487: 802 (80%); 0.7244: 609 (61%); 0.8846: 431 (43%); 1: 254 (25%) | 0.4487: 206 (21%); 0.7244: 404 (40%); 0.8846: 612 (61%); 1: 1001 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.2436, 0.5128, 0.7949 | 0.109: 805 (80%); 0.2436: 604 (60%); 0.5128: 407 (41%); 0.7949: 205 (20%) | 0.109: 207 (21%); 0.2436: 404 (40%); 0.5128: 605 (60%); 0.7949: 806 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0063, 0.0366, 0.0875, 0.2489 | -0.0063: 803 (80%); 0.0366: 613 (61%); 0.0875: 403 (40%); 0.2489: 208 (21%) | -0.0063: 205 (20%); 0.0366: 405 (40%); 0.0875: 601 (60%); 0.2489: 851 (85%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5, 0.7815, 0.9359, 0.9744 | 0.5: 802 (80%); 0.7815: 607 (61%); 0.9359: 405 (40%); 0.9744: 244 (24%) | 0.5: 201 (20%); 0.7815: 409 (41%); 0.9359: 605 (60%); 0.9744: 854 (85%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.084, 0.2051, 0.4744, 0.7778 | 0.084: 815 (81%); 0.2051: 614 (61%); 0.4744: 403 (40%); 0.7778: 201 (20%) | 0.084: 201 (20%); 0.2051: 404 (40%); 0.4744: 601 (60%); 0.7778: 807 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0141, 0.1048, 0.2205 | -0.0812: 825 (82%); -0.0141: 602 (60%); 0.1048: 405 (40%); 0.2205: 205 (20%) | -0.0812: 276 (28%); -0.0141: 404 (40%); 0.1048: 601 (60%); 0.2205: 809 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1894, -0.0125, 0.0442, 0.0978 | -0.1894: 804 (80%); -0.0125: 605 (60%); 0.0442: 409 (41%); 0.0978: 202 (20%) | -0.1894: 201 (20%); -0.0125: 401 (40%); 0.0442: 601 (60%); 0.0978: 806 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3205, 0.5449, 0.7436, 0.891 | 0.3205: 801 (80%); 0.5449: 608 (61%); 0.7436: 407 (41%); 0.891: 204 (20%) | 0.3205: 211 (21%); 0.5449: 401 (40%); 0.7436: 609 (61%); 0.891: 802 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.3782, 0.5641, 0.8141 | 0.1282: 804 (80%); 0.3782: 616 (62%); 0.5641: 458 (46%); 0.8141: 201 (20%) | 0.1282: 212 (21%); 0.3782: 404 (40%); 0.5641: 611 (61%); 0.8141: 813 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0129, 0.03, 0.0617, 0.1425 | 0.0129: 801 (80%); 0.03: 612 (61%); 0.0617: 406 (41%); 0.1425: 201 (20%) | 0.0129: 201 (20%); 0.03: 403 (40%); 0.0617: 601 (60%); 0.1425: 802 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.8% | 26, 62, 85, 143.4 | 26: 794 (79%); 62: 599 (60%); 85: 400 (40%); 143.4: 198 (20%) | 26: 199 (20%); 62: 413 (41%); 85: 599 (60%); 143.4: 791 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.5% | 1.7404, 2.2301, 2.7675, 3.6213 | 1.7404: 798 (80%); 2.2301: 598 (60%); 2.7675: 399 (40%); 3.6213: 200 (20%) | 1.7404: 200 (20%); 2.2301: 399 (40%); 2.7675: 598 (60%); 3.6213: 797 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 12, 21, 29, 35 | 12: 812 (81%); 21: 602 (60%); 29: 420 (42%); 35: 222 (22%) | 12: 217 (22%); 21: 430 (43%); 29: 678 (68%); 35: 807 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 834 (83%); 2: 574 (57%); 3: 366 (37%) | 1: 427 (43%); 2: 635 (63%); 3: 832 (83%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0147, -0.0021, 0.0133, 0.0249 | -0.0147: 801 (80%); -0.0021: 603 (60%); 0.0133: 402 (40%); 0.0249: 204 (20%) | -0.0147: 203 (20%); -0.0021: 401 (40%); 0.0133: 601 (60%); 0.0249: 802 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5078, 25.7489, 26.5338, 27.3171 | 24.5078: 804 (80%); 25.7489: 602 (60%); 26.5338: 401 (40%); 27.3171: 203 (20%) | 24.5078: 202 (20%); 25.7489: 402 (40%); 26.5338: 603 (60%); 27.3171: 851 (85%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.698, -0.208, 0.133, 0.655 | -0.698: 801 (80%); -0.208: 603 (60%); 0.133: 401 (40%); 0.655: 201 (20%) | -0.698: 201 (20%); -0.208: 402 (40%); 0.133: 601 (60%); 0.655: 801 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.655, -0.133, 0.208, 0.698 | -0.655: 801 (80%); -0.133: 601 (60%); 0.208: 402 (40%); 0.698: 201 (20%) | -0.655: 201 (20%); -0.133: 401 (40%); 0.208: 603 (60%); 0.698: 801 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0422, -0.0049, 0.0265, 0.0697 | -0.0422: 802 (80%); -0.0049: 601 (60%); 0.0265: 401 (40%); 0.0697: 201 (20%) | -0.0422: 204 (20%); -0.0049: 401 (40%); 0.0265: 601 (60%); 0.0697: 804 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0628, 8.5012, 8.8383, 9.2024 | 8.0628: 806 (81%); 8.5012: 605 (60%); 8.8383: 399 (40%); 9.2024: 201 (20%) | 8.0628: 195 (19%); 8.5012: 396 (40%); 8.8383: 602 (60%); 9.2024: 800 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 993 (99%); 1: 317 (32%) | 0: 676 (68%); 1: 888 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.2% | -1, 0 | -1: 940 (94%); 0: 774 (77%) | -1: 219 (22%); 0: 826 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 993 (99%); 1: 343 (34%) | 0: 650 (65%); 1: 864 (86%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 5, 114, 252 | 2: 834 (83%); 5: 634 (63%); 114: 401 (40%); 252: 202 (20%) | 2: 221 (22%); 5: 430 (43%); 114: 601 (60%); 252: 803 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 4, 78, 140 | 0: 1001 (100%); 4: 603 (60%); 78: 408 (41%); 140: 201 (20%) | 0: 206 (21%); 4: 426 (43%); 78: 601 (60%); 140: 803 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.0946, -0.4334, -0.1519, 0.2642 | -1.0946: 801 (80%); -0.4334: 601 (60%); -0.1519: 401 (40%); 0.2642: 201 (20%) | -1.0946: 201 (20%); -0.4334: 401 (40%); -0.1519: 601 (60%); 0.2642: 801 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -3.1605, -1.1598, -0.3134, 0.4653 | -3.1605: 801 (80%); -1.1598: 601 (60%); -0.3134: 401 (40%); 0.4653: 201 (20%) | -3.1605: 201 (20%); -1.1598: 401 (40%); -0.3134: 601 (60%); 0.4653: 801 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.4403, -0.8482, -0.1375, 0.4951 | -2.4403: 801 (80%); -0.8482: 601 (60%); -0.1375: 401 (40%); 0.4951: 201 (20%) | -2.4403: 201 (20%); -0.8482: 401 (40%); -0.1375: 601 (60%); 0.4951: 801 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.8, -0.2539, -0.0255, 0.3419 | -0.8: 801 (80%); -0.2539: 601 (60%); -0.0255: 401 (40%); 0.3419: 201 (20%) | -0.8: 201 (20%); -0.2539: 401 (40%); -0.0255: 601 (60%); 0.3419: 801 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -4.0102, -1.4551, -0.4306, 0.6158 | -4.0102: 801 (80%); -1.4551: 601 (60%); -0.4306: 401 (40%); 0.6158: 201 (20%) | -4.0102: 201 (20%); -1.4551: 401 (40%); -0.4306: 601 (60%); 0.6158: 801 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -3.3324, -1.2377, -0.3013, 0.5245 | -3.3324: 801 (80%); -1.2377: 601 (60%); -0.3013: 401 (40%); 0.5245: 201 (20%) | -3.3324: 201 (20%); -1.2377: 401 (40%); -0.3013: 601 (60%); 0.5245: 801 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 28.79, 37.36, 46.68, 60.24 | 28.79: 801 (80%); 37.36: 601 (60%); 46.68: 401 (40%); 60.24: 201 (20%) | 28.79: 201 (20%); 37.36: 401 (40%); 46.68: 601 (60%); 60.24: 801 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.8% | 0.0058, 0.0139, 0.0242, 0.0486 | 0.0058: 799 (80%); 0.0139: 602 (60%); 0.0242: 401 (40%); 0.0486: 200 (20%) | 0.0058: 200 (20%); 0.0139: 397 (40%); 0.0242: 598 (60%); 0.0486: 799 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 8 | 0: 1001 (100%); 1: 751 (75%); 3: 473 (47%); 8: 215 (21%) | 0: 250 (25%); 1: 414 (41%); 3: 606 (61%); 8: 802 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 1001 (100%); 0.1667: 203 (20%) | 0: 688 (69%); 0.1667: 810 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4, 0.6667 | 0: 1001 (100%); 0.4: 415 (41%); 0.6667: 217 (22%) | 0: 401 (40%); 0.4: 604 (60%); 0.6667: 819 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 6 | 0: 1001 (100%); 1: 680 (68%); 2: 500 (50%); 6: 207 (21%) | 0: 321 (32%); 1: 501 (50%); 2: 604 (60%); 6: 825 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1001 (100%); 1: 751 (75%); 3: 473 (47%); 8: 215 (21%) | 0: 250 (25%); 1: 414 (41%); 3: 606 (61%); 8: 802 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1001 (100%); 1: 680 (68%); 3: 424 (42%); 7: 216 (22%) | 0: 321 (32%); 1: 472 (47%); 3: 651 (65%); 7: 816 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2308, 0.373, 0.5795 | 0: 923 (92%); 0.2308: 601 (60%); 0.373: 401 (40%); 0.5795: 201 (20%) | 0: 236 (24%); 0.2308: 401 (40%); 0.373: 601 (60%); 0.5795: 801 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.125, 0.5263 | 0: 904 (90%); 0.125: 401 (40%); 0.5263: 201 (20%) | 0: 563 (56%); 0.125: 601 (60%); 0.5263: 801 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3, 0.5714 | 0: 891 (89%); 0.3: 405 (40%); 0.5714: 201 (20%) | 0: 462 (46%); 0.3: 601 (60%); 0.5714: 801 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3, 0.5714 | 0: 891 (89%); 0.3: 405 (40%); 0.5714: 201 (20%) | 0: 462 (46%); 0.3: 601 (60%); 0.5714: 801 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1667, 0, 0.1259 | -0.1667: 807 (81%); 0: 728 (73%); 0.1259: 201 (20%) | -0.1667: 205 (20%); 0: 733 (73%); 0.1259: 801 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7108, -0.2899, 0.1994, 1.4343 | -0.7108: 801 (80%); -0.2899: 602 (60%); 0.1994: 401 (40%); 1.4343: 201 (20%) | -0.7108: 201 (20%); -0.2899: 401 (40%); 0.1994: 601 (60%); 1.4343: 805 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 12 | 2: 824 (82%); 4: 632 (63%); 7: 424 (42%); 12: 206 (21%) | 2: 276 (28%); 4: 446 (45%); 7: 630 (63%); 12: 817 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.101, -0.0584, -0.0267, 0.0397 | -0.101: 800 (80%); -0.0584: 600 (60%); -0.0267: 401 (40%); 0.0397: 201 (20%) | -0.101: 201 (20%); -0.0584: 401 (40%); -0.0267: 600 (60%); 0.0397: 800 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1177, -0.0705, -0.0262, 0.0399 | -0.1177: 801 (80%); -0.0705: 601 (60%); -0.0262: 401 (40%); 0.0399: 199 (20%) | -0.1177: 200 (20%); -0.0705: 400 (40%); -0.0262: 600 (60%); 0.0399: 802 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0649, -0.0312, -0.0057, 0.0297 | -0.0649: 800 (80%); -0.0312: 599 (60%); -0.0057: 401 (40%); 0.0297: 200 (20%) | -0.0649: 201 (20%); -0.0312: 402 (40%); -0.0057: 600 (60%); 0.0297: 801 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -18.912, -8.278, 0.371, 11.76 | -18.912: 801 (80%); -8.278: 601 (60%); 0.371: 401 (40%); 11.76: 201 (20%) | -18.912: 201 (20%); -8.278: 401 (40%); 0.371: 601 (60%); 11.76: 802 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.043, 0.0575, 0.0757, 0.1097 | 0.043: 801 (80%); 0.0575: 601 (60%); 0.0757: 401 (40%); 0.1097: 201 (20%) | 0.043: 202 (20%); 0.0575: 401 (40%); 0.0757: 601 (60%); 0.1097: 801 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1102, 0.2498, 0.4455, 0.7061 | 0.1102: 801 (80%); 0.2498: 601 (60%); 0.4455: 401 (40%); 0.7061: 201 (20%) | 0.1102: 201 (20%); 0.2498: 401 (40%); 0.4455: 601 (60%); 0.7061: 801 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.5717, -1.474, -0.4643, 0.7379 | -2.5717: 801 (80%); -1.474: 601 (60%); -0.4643: 401 (40%); 0.7379: 201 (20%) | -2.5717: 201 (20%); -1.474: 401 (40%); -0.4643: 601 (60%); 0.7379: 801 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.0301, -0.5767, -0.2376, 0.4103 | -1.0301: 801 (80%); -0.5767: 601 (60%); -0.2376: 401 (40%); 0.4103: 201 (20%) | -1.0301: 201 (20%); -0.5767: 401 (40%); -0.2376: 601 (60%); 0.4103: 801 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.0493, -1.1263, -0.244, 0.6644 | -2.0493: 801 (80%); -1.1263: 601 (60%); -0.244: 401 (40%); 0.6644: 201 (20%) | -2.0493: 201 (20%); -1.1263: 401 (40%); -0.244: 601 (60%); 0.6644: 801 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -11.117, -6.742, -3.189, 4.148 | -11.117: 801 (80%); -6.742: 601 (60%); -3.189: 401 (40%); 4.148: 201 (20%) | -11.117: 201 (20%); -6.742: 401 (40%); -3.189: 601 (60%); 4.148: 801 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 4.7, 13.7, 35.3, 79.66 | 4.7: 801 (80%); 13.7: 601 (60%); 35.3: 401 (40%); 79.66: 201 (20%) | 4.7: 201 (20%); 13.7: 401 (40%); 35.3: 601 (60%); 79.66: 801 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 36.35, 41.38, 45.8, 53.9 | 36.35: 801 (80%); 41.38: 602 (60%); 45.8: 401 (40%); 53.9: 201 (20%) | 36.35: 201 (20%); 41.38: 401 (40%); 45.8: 601 (60%); 53.9: 801 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 25.85, 33.61, 40.55, 61.82 | 25.85: 802 (80%); 33.61: 601 (60%); 40.55: 401 (40%); 61.82: 201 (20%) | 25.85: 201 (20%); 33.61: 402 (40%); 40.55: 601 (60%); 61.82: 801 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 1000 (100%) | 0: 1001 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0322, 0.05, 0.061, 0.0911 | 0.0322: 806 (81%); 0.05: 602 (60%); 0.061: 409 (41%); 0.0911: 206 (21%) | 0.0322: 201 (20%); 0.05: 405 (40%); 0.061: 602 (60%); 0.0911: 803 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.087, -0.058, -0.044, -0.0314 | -0.087: 802 (80%); -0.058: 601 (60%); -0.044: 401 (40%); -0.0314: 202 (20%) | -0.087: 202 (20%); -0.058: 401 (40%); -0.044: 604 (60%); -0.0314: 805 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1001 (100%); 1: 265 (26%) | 0: 736 (74%); 1: 828 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.5% | 26, 41, 60, 68 | 26: 799 (80%); 41: 602 (60%); 60: 406 (41%); 68: 205 (20%) | 26: 209 (21%); 41: 412 (41%); 60: 606 (61%); 68: 810 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.9% | 0.0115, 0.0169, 0.0246, 0.037 | 0.0115: 793 (79%); 0.0169: 593 (59%); 0.0246: 397 (40%); 0.037: 199 (20%) | 0.0115: 197 (20%); 0.0169: 397 (40%); 0.0246: 593 (59%); 0.037: 791 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.0687, 0.1908, 0.4081, 0.6409 | 0.0687: 801 (80%); 0.1908: 601 (60%); 0.4081: 401 (40%); 0.6409: 201 (20%) | 0.0687: 202 (20%); 0.1908: 401 (40%); 0.4081: 601 (60%); 0.6409: 801 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 30.1, 49.7, 71.1, 100 | 30.1: 802 (80%); 49.7: 601 (60%); 71.1: 402 (40%); 100: 201 (20%) | 30.1: 204 (20%); 49.7: 402 (40%); 71.1: 601 (60%); 100: 802 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -9.225, -3.98, -1.52, 2.32 | -9.225: 801 (80%); -3.98: 602 (60%); -1.52: 401 (40%); 2.32: 201 (20%) | -9.225: 201 (20%); -3.98: 401 (40%); -1.52: 601 (60%); 2.32: 801 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 12.9, 21.1, 36.78, 71.21 | 12.9: 801 (80%); 21.1: 601 (60%); 36.78: 401 (40%); 71.21: 201 (20%) | 12.9: 201 (20%); 21.1: 401 (40%); 36.78: 601 (60%); 71.21: 801 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 10.4, 18.27, 32.85, 74.11 | 10.4: 801 (80%); 18.27: 601 (60%); 32.85: 401 (40%); 74.11: 201 (20%) | 10.4: 201 (20%); 18.27: 401 (40%); 32.85: 601 (60%); 74.11: 801 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 3.24, 16.53, 43.1, 81.51 | 3.24: 801 (80%); 16.53: 601 (60%); 43.1: 401 (40%); 81.51: 201 (20%) | 3.24: 201 (20%); 16.53: 401 (40%); 43.1: 602 (60%); 81.51: 801 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 7.66, 41.08, 89.64 | 0: 1001 (100%); 7.66: 601 (60%); 41.08: 401 (40%); 89.64: 201 (20%) | 0: 299 (30%); 7.66: 401 (40%); 41.08: 601 (60%); 89.64: 801 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 12, 17 | 5: 806 (81%); 8: 609 (61%); 12: 432 (43%); 17: 210 (21%) | 5: 254 (25%); 8: 433 (43%); 12: 625 (62%); 17: 832 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 17 | 5: 821 (82%); 10: 629 (63%); 14: 433 (43%); 17: 249 (25%) | 5: 223 (22%); 10: 425 (42%); 14: 611 (61%); 17: 814 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 37.74, 41.9, 48.26, 57.26 | 37.74: 801 (80%); 41.9: 602 (60%); 48.26: 402 (40%); 57.26: 201 (20%) | 37.74: 201 (20%); 41.9: 401 (40%); 48.26: 601 (60%); 57.26: 802 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2143, 0.4643, 0.7341, 0.9286 | 0.2143: 803 (80%); 0.4643: 602 (60%); 0.7341: 401 (40%); 0.9286: 203 (20%) | 0.2143: 201 (20%); 0.4643: 401 (40%); 0.7341: 605 (60%); 0.9286: 806 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.81, 18.21, 22.36, 28.36 | 15.81: 801 (80%); 18.21: 607 (61%); 22.36: 403 (40%); 28.36: 205 (20%) | 15.81: 202 (20%); 18.21: 401 (40%); 22.36: 601 (60%); 28.36: 803 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.81, 18.21, 22.36, 28.36 | 15.81: 801 (80%); 18.21: 607 (61%); 22.36: 403 (40%); 28.36: 205 (20%) | 15.81: 202 (20%); 18.21: 401 (40%); 22.36: 601 (60%); 28.36: 803 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.864, 0.9026, 0.9407, 0.9871 | 0.864: 805 (80%); 0.9026: 602 (60%); 0.9407: 402 (40%); 0.9871: 201 (20%) | 0.864: 201 (20%); 0.9026: 402 (40%); 0.9407: 604 (60%); 0.9871: 801 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.72, 0.89, 1.07, 1.39 | 0.72: 803 (80%); 0.89: 610 (61%); 1.07: 401 (40%); 1.39: 201 (20%) | 0.72: 205 (20%); 0.89: 404 (40%); 1.07: 611 (61%); 1.39: 809 (81%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0227, 0.0472, 0.0822, 0.1302 | 0.0227: 802 (80%); 0.0472: 601 (60%); 0.0822: 401 (40%); 0.1302: 201 (20%) | 0.0227: 202 (20%); 0.0472: 401 (40%); 0.0822: 601 (60%); 0.1302: 801 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1001 (100%) | 0: 889 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1001 (100%) | 0: 923 (92%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1147, -0.0698, -0.0318, 0.0421 | -0.1147: 801 (80%); -0.0698: 601 (60%); -0.0318: 401 (40%); 0.0421: 201 (20%) | -0.1147: 201 (20%); -0.0698: 401 (40%); -0.0318: 601 (60%); 0.0421: 801 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -94.21, -87.9, -73.33, -16.66 | -94.21: 801 (80%); -87.9: 601 (60%); -73.33: 401 (40%); -16.66: 201 (20%) | -94.21: 201 (20%); -87.9: 401 (40%); -73.33: 601 (60%); -16.66: 801 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.7% | 0.5659, 0.8528, 1.0704, 1.3291 | 0.5659: 798 (80%); 0.8528: 599 (60%); 1.0704: 399 (40%); 1.3291: 200 (20%) | 0.5659: 200 (20%); 0.8528: 400 (40%); 1.0704: 599 (60%); 1.3291: 798 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.7% | 3, 5, 8, 9 | 3: 841 (84%); 5: 670 (67%); 8: 400 (40%); 9: 271 (27%) | 3: 234 (23%); 5: 408 (41%); 8: 727 (73%); 9: 861 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.4% | 0.1943, 0.2375, 0.2856, 0.3565 | 0.1943: 796 (80%); 0.2375: 597 (60%); 0.2856: 398 (40%); 0.3565: 199 (20%) | 0.1943: 199 (20%); 0.2375: 399 (40%); 0.2856: 597 (60%); 0.3565: 796 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.4% | 3, 5, 8, 9 | 3: 855 (85%); 5: 695 (69%); 8: 400 (40%); 9: 273 (27%) | 3: 219 (22%); 5: 399 (40%); 8: 722 (72%); 9: 871 (87%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.5% | 0.0227, 0.0312, 0.0401, 0.0586 | 0.0227: 797 (80%); 0.0312: 598 (60%); 0.0401: 399 (40%); 0.0586: 200 (20%) | 0.0227: 203 (20%); 0.0312: 401 (40%); 0.0401: 598 (60%); 0.0586: 797 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.5% | 3, 5, 7, 9 | 3: 823 (82%); 5: 666 (67%); 7: 461 (46%); 9: 242 (24%) | 3: 235 (23%); 5: 421 (42%); 7: 633 (63%); 9: 876 (88%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.8% | -0.162, -0.0687, 0.029, 0.1661 | -0.162: 799 (80%); -0.0687: 599 (60%); 0.029: 400 (40%); 0.1661: 200 (20%) | -0.162: 200 (20%); -0.0687: 400 (40%); 0.029: 600 (60%); 0.1661: 799 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.8% | 2, 4, 6, 8 | 2: 930 (93%); 4: 653 (65%); 6: 422 (42%); 8: 240 (24%) | 2: 218 (22%); 4: 463 (46%); 6: 676 (68%); 8: 856 (86%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 8.7% |
| 8k_item_5_02_filed_within_7d | 3.7% |
| above_avwap_20high | 24.6% |
| above_avwap_20low | 45.6% |
| above_avwap_252low | 47.6% |
| above_avwap_50low | 46.4% |
| above_cam_r3 | 22.2% |
| above_cam_r4 | 14.1% |
| above_cpr | 28.6% |
| above_pivot | 26.9% |
| above_prev_high | 16.3% |
| above_prev_high_clearance_atr_05 | 7.1% |
| above_prev_low | 65.9% |
| above_r1 | 15.4% |
| above_r2 | 8.2% |
| above_vwap | 40.8% |
| above_wood_p | 33.4% |
| ad_rising | 42.0% |
| adx_cross_up | 4.3% |
| adx_cross_up_20 | 3.3% |
| adx_di_bear | 71.4% |
| adx_di_bull | 28.6% |
| adx_strong | 4.3% |
| adx_trending | 36.5% |
| ao_cross_dn | 2.9% |
| ao_cross_up | 2.0% |
| ao_positive | 31.3% |
| ao_twin_peaks_bull | 4.8% |
| at_key_fib | 12.9% |
| at_key_fib_wide | 30.3% |
| avwap_20high_loss_recent_3d | 11.7% |
| avwap_20high_reclaim_recent_3d | 9.8% |
| avwap_20low_loss_recent_3d | 30.8% |
| avwap_20low_reclaim_recent_3d | 7.7% |
| avwap_252low_loss_recent_3d | 17.8% |
| avwap_252low_reclaim_recent_3d | 7.1% |
| avwap_50low_loss_recent_3d | 24.7% |
| avwap_50low_reclaim_recent_3d | 5.7% |
| bb_10_20_above_mid | 31.1% |
| bb_10_20_expanding | 61.5% |
| bb_10_20_pctb_gt_75 | 21.7% |
| bb_10_20_pctb_gt_8 | 17.6% |
| bb_10_20_pctb_gt_85 | 13.5% |
| bb_10_20_pctb_gt_9 | 9.7% |
| bb_10_20_pctb_gt_95 | 6.4% |
| bb_10_20_pctb_lt_05 | 14.6% |
| bb_10_20_pctb_lt_1 | 23.0% |
| bb_10_20_pctb_lt_15 | 32.6% |
| bb_10_20_pctb_lt_2 | 42.4% |
| bb_10_20_pctb_lt_25 | 49.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 11.9% |
| bb_10_20_reclaim_from_upper_recent_3d | 4.8% |
| bb_10_20_squeeze | 31.1% |
| bb_10_20_touch_lower | 15.6% |
| bb_10_20_touch_upper | 7.1% |
| bb_20_15_above_mid | 27.4% |
| bb_20_15_expanding | 71.6% |
| bb_20_15_pctb_gt_75 | 24.9% |
| bb_20_15_pctb_gt_8 | 23.4% |
| bb_20_15_pctb_gt_85 | 21.8% |
| bb_20_15_pctb_gt_9 | 20.1% |
| bb_20_15_pctb_gt_95 | 18.0% |
| bb_20_15_pctb_lt_05 | 43.0% |
| bb_20_15_pctb_lt_1 | 49.2% |
| bb_20_15_pctb_lt_15 | 54.6% |
| bb_20_15_pctb_lt_2 | 60.6% |
| bb_20_15_pctb_lt_25 | 65.1% |
| bb_20_15_reclaim_from_lower_recent_3d | 10.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 3.3% |
| bb_20_15_squeeze | 26.9% |
| bb_20_15_touch_lower | 43.1% |
| bb_20_15_touch_upper | 18.5% |
| bb_20_20_above_mid | 27.4% |
| bb_20_20_expanding | 71.6% |
| bb_20_20_pctb_gt_75 | 22.1% |
| bb_20_20_pctb_gt_8 | 20.1% |
| bb_20_20_pctb_gt_85 | 17.4% |
| bb_20_20_pctb_gt_9 | 13.7% |
| bb_20_20_pctb_gt_95 | 9.4% |
| bb_20_20_pctb_lt_05 | 26.2% |
| bb_20_20_pctb_lt_1 | 33.2% |
| bb_20_20_pctb_lt_15 | 40.6% |
| bb_20_20_pctb_lt_2 | 49.2% |
| bb_20_20_pctb_lt_25 | 56.3% |
| bb_20_20_reclaim_from_lower_recent_3d | 7.8% |
| bb_20_20_reclaim_from_upper_recent_3d | 3.2% |
| bb_20_20_squeeze | 13.0% |
| bb_20_20_touch_lower | 25.5% |
| bb_20_20_touch_upper | 9.7% |
| bearish_engulfing | 10.5% |
| bearish_pin_bar | 3.7% |
| below_avwap_20high | 75.4% |
| below_avwap_20low | 54.4% |
| below_avwap_252low | 52.4% |
| below_avwap_50low | 53.6% |
| below_cam_s3 | 50.7% |
| below_cam_s4 | 30.6% |
| below_cpr | 73.1% |
| below_ema_20 | 72.6% |
| below_ema_200 | 72.7% |
| below_ema_200_break_recent_5d | 24.4% |
| below_ema_20_break_recent_5d | 21.2% |
| below_ema_21 | 72.6% |
| below_ema_21_break_recent_5d | 21.5% |
| below_ema_50 | 71.5% |
| below_ema_50_break_recent_5d | 16.8% |
| below_ema_9 | 71.4% |
| below_ema_9_break_recent_5d | 29.9% |
| below_prev_high | 83.7% |
| below_prev_low | 33.7% |
| below_prev_low_clearance_atr_05 | 15.4% |
| below_s1 | 33.2% |
| below_s2 | 18.7% |
| below_sma_20 | 72.6% |
| below_sma_200 | 68.1% |
| below_sma_21 | 72.6% |
| below_sma_50 | 69.4% |
| below_sma_9 | 67.3% |
| below_vwap | 59.2% |
| blowoff_recent_3d | 0.3% |
| break_52w_high | 0.9% |
| break_52w_high_clearance_atr_05 | 0.1% |
| break_52w_high_confirmed_today | 0.2% |
| break_52w_low | 2.8% |
| bullish_engulfing | 4.3% |
| bullish_pin_bar | 5.1% |
| capitulation_recent_3d | 0.2% |
| ceo_buy | 0.7% |
| cfo_buy | 0.1% |
| chandelier_long_bullish | 37.7% |
| chandelier_long_flip_dn | 8.6% |
| chandelier_short_bearish | 73.8% |
| chandelier_short_flip_up | 4.9% |
| close_above_open | 27.3% |
| close_below_open | 72.7% |
| close_in_bottom_40pct_of_range | 55.9% |
| close_in_top_40pct_of_range | 26.6% |
| cluster_buy | 0.3% |
| cmf_cross_dn | 9.2% |
| cmf_cross_up | 3.8% |
| cmf_negative | 55.6% |
| cmf_positive | 44.4% |
| concentrated_sell | 3.8% |
| cup_handle_detected | 19.6% |
| cup_handle_neckline_break_retest_long | 4.7% |
| dc10_breakout_dn | 23.7% |
| dc10_breakout_dn_1pct | 37.7% |
| dc10_breakout_up | 12.5% |
| dc10_breakout_up_1pct | 19.1% |
| dc10_new_high | 16.1% |
| dc10_strong_breakout_dn | 9.8% |
| dc10_strong_breakout_up | 4.3% |
| dc20_breakout_dn | 19.5% |
| dc20_breakout_up | 9.8% |
| dc20_new_high | 12.1% |
| dc20_resistance_break_retest_strong | 9.9% |
| dc20_support_break_retest_strong | 32.8% |
| defensive_leadership | 63.1% |
| director_only_buy | 3.4% |
| doji | 2.7% |
| double_bottom_detected | 14.1% |
| double_top_detected | 17.2% |
| dpi_elevated | 50.8% |
| drying_volume_on_down_turn | 38.4% |
| drying_volume_on_up_turn | 15.2% |
| ema_20_50_bearish | 66.5% |
| ema_20_50_bullish | 33.5% |
| ema_20_50_death_cross | 3.1% |
| ema_20_50_golden_cross | 0.9% |
| ema_50_200_bearish | 58.8% |
| ema_50_200_bullish | 41.2% |
| ema_50_200_death_cross | 0.7% |
| ema_50_200_golden_cross | 0.1% |
| ema_9_21_bearish | 69.2% |
| ema_9_21_bullish | 30.8% |
| ema_9_21_death_cross | 3.2% |
| ema_9_21_golden_cross | 2.3% |
| evening_star | 10.6% |
| flag_bear_break_retest_short | 0.9% |
| flag_bear_broke | 1.0% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 0.2% |
| flag_bull_broke | 0.3% |
| force_index_cross_dn | 4.1% |
| force_index_cross_up | 1.3% |
| force_index_positive | 28.2% |
| gap_dn_1_5pct | 8.4% |
| gap_dn_2pct | 6.3% |
| gap_up_1_5pct | 10.2% |
| gap_up_2pct | 7.9% |
| hammer | 4.9% |
| head_shoulders_bottom_detected | 3.8% |
| head_shoulders_top_detected | 5.7% |
| house_cluster_buy | 3.5% |
| house_cluster_sell | 4.8% |
| htf_aligned_bear | 54.9% |
| htf_aligned_bull | 15.5% |
| htf_disagreement | 2.8% |
| hull_bearish | 66.2% |
| hull_bullish | 33.8% |
| hull_flip_dn | 3.8% |
| hull_flip_up | 4.1% |
| ichi_above_cloud | 25.0% |
| ichi_above_cloud_break_recent_5d | 8.2% |
| ichi_below_cloud | 60.3% |
| ichi_below_cloud_break_recent_5d | 17.3% |
| ichi_cloud_thick | 83.7% |
| ichi_tk_bearish | 63.6% |
| ichi_tk_bullish | 30.1% |
| ichi_tk_cross_dn | 4.1% |
| ichi_tk_cross_up | 2.6% |
| ichi_weekly_above_cloud | 23.3% |
| ichi_weekly_below_cloud | 42.9% |
| ichi_weekly_in_cloud | 33.9% |
| in_reversal_window | 2.1% |
| inside_bar | 15.4% |
| inside_kc | 66.1% |
| insider_cluster_active | 19.2% |
| institutional_buy | 86.7% |
| institutional_negative | 6.3% |
| institutional_persistence_growing | 44.8% |
| institutional_persistence_strong | 59.0% |
| institutional_strong_buy | 77.0% |
| inverted_cup_handle_detected | 14.7% |
| is_friday | 16.9% |
| is_halloween_period | 54.1% |
| is_halloween_period_first_day | 0.3% |
| is_january | 7.8% |
| is_january_extended | 10.1% |
| is_monday | 16.7% |
| is_pre_holiday | 3.3% |
| is_summer_period | 45.9% |
| is_totm_window | 33.0% |
| is_totm_window_first_day | 9.6% |
| is_week_open | 19.3% |
| kc_touch_lower | 30.0% |
| kc_touch_upper | 9.8% |
| large_dollar_buy | 0.9% |
| macd_12_26_9_bearish | 72.7% |
| macd_12_26_9_bullish | 27.3% |
| macd_12_26_9_crossover_dn | 3.8% |
| macd_12_26_9_crossover_up | 2.1% |
| macd_8_21_5_bearish | 62.5% |
| macd_8_21_5_bullish | 37.5% |
| macd_8_21_5_crossover_dn | 2.5% |
| macd_8_21_5_crossover_up | 2.5% |
| marubozu_bear | 1.2% |
| marubozu_bull | 0.7% |
| mfi_broad_overbought | 9.1% |
| mfi_broad_oversold | 22.1% |
| mfi_overbought | 2.3% |
| mfi_oversold | 7.1% |
| monthly_above_sma_12 | 30.5% |
| monthly_above_sma_6 | 28.2% |
| monthly_bias_bear | 59.4% |
| monthly_bias_bull | 18.1% |
| monthly_momentum_pos | 36.4% |
| morning_star | 3.6% |
| near_52w_high | 1.5% |
| near_52w_high_95pct | 3.6% |
| near_52w_high_retest_long | 0.2% |
| near_52w_low | 6.6% |
| near_52w_low_105pct | 13.4% |
| near_52w_low_retest_short | 1.4% |
| near_avwap_20high_atr_05x | 16.5% |
| near_avwap_20high_atr_10x | 32.8% |
| near_avwap_20high_atr_15x | 54.4% |
| near_avwap_20high_atr_20x | 74.5% |
| near_avwap_20low_atr_05x | 43.3% |
| near_avwap_20low_atr_10x | 58.9% |
| near_avwap_20low_atr_15x | 70.6% |
| near_avwap_20low_atr_20x | 81.3% |
| near_avwap_252low_atr_05x | 21.7% |
| near_avwap_252low_atr_10x | 40.1% |
| near_avwap_252low_atr_15x | 52.3% |
| near_avwap_252low_atr_20x | 64.0% |
| near_avwap_50low_atr_05x | 31.7% |
| near_avwap_50low_atr_10x | 48.6% |
| near_avwap_50low_atr_15x | 61.6% |
| near_avwap_50low_atr_20x | 71.7% |
| near_cam_r3 | 6.9% |
| near_cam_s3 | 20.8% |
| near_cam_s4 | 12.8% |
| near_fib_236 | 2.6% |
| near_fib_382 | 4.4% |
| near_fib_500 | 4.1% |
| near_fib_618 | 4.4% |
| near_fib_786 | 6.3% |
| near_pivot | 11.6% |
| near_prev_close | 10.8% |
| near_prev_high | 7.2% |
| near_prev_low | 14.3% |
| near_r1 | 7.3% |
| near_r1_wide | 34.5% |
| near_r2 | 2.5% |
| near_r2_wide | 19.7% |
| near_s1 | 14.3% |
| near_s1_wide | 56.4% |
| near_s2 | 6.1% |
| near_s2_wide | 37.9% |
| near_s3 | 3.9% |
| near_wood_r1 | 5.7% |
| near_wood_s1 | 11.7% |
| news_uses_polygon_score | 23.6% |
| obv_bearish | 68.1% |
| obv_bullish | 31.9% |
| obv_diverge_bull | 6.1% |
| obv_falling | 63.1% |
| obv_rising | 36.9% |
| outside_bar | 11.6% |
| pead_negative_surprise | 16.1% |
| pead_positive_surprise | 22.8% |
| pin_bar | 8.8% |
| po3_accumulation_active | 30.4% |
| po3_bearish | 13.9% |
| po3_bullish | 3.2% |
| po3_manipulation_sweep_down | 12.2% |
| po3_manipulation_sweep_up | 6.5% |
| po3_mmbm_setup | 0.5% |
| po3_mmsm_setup | 0.4% |
| po3_sweep_above_prior_high | 43.0% |
| po3_sweep_below_prior_low | 61.0% |
| ppo_bullish | 27.2% |
| ppo_crossover_dn | 3.5% |
| ppo_crossover_up | 2.1% |
| pre_fomc_d0 | 3.5% |
| pre_fomc_d1 | 2.5% |
| pre_fomc_window | 6.0% |
| price_above_dema | 33.8% |
| price_above_ema_20 | 27.4% |
| price_above_ema_200 | 27.3% |
| price_above_ema_200_break_recent_5d | 16.7% |
| price_above_ema_20_break_recent_5d | 11.4% |
| price_above_ema_21 | 27.4% |
| price_above_ema_21_break_recent_5d | 11.4% |
| price_above_ema_50 | 28.5% |
| price_above_ema_50_break_recent_5d | 13.2% |
| price_above_ema_9 | 28.6% |
| price_above_ema_9_break_recent_5d | 13.3% |
| price_above_hull | 44.3% |
| price_above_sma_200 | 31.9% |
| price_above_sma_21 | 27.4% |
| price_above_sma_50 | 30.6% |
| price_above_tema | 43.4% |
| price_below_dema | 66.2% |
| price_below_hull | 55.7% |
| price_below_tema | 56.6% |
| psar_bullish | 31.5% |
| psar_flip_dn | 2.9% |
| psar_flip_up | 1.8% |
| r1_break_retest_long | 36.6% |
| recent_blowoff_at_r3 | 0.1% |
| recent_capitulation_at_s3 | 0.5% |
| resistance_break_retest | 14.4% |
| risk_off_regime_bond_signal | 30.3% |
| risk_off_regime_bond_signal_strong | 13.8% |
| risk_off_regime_gold_signal | 43.8% |
| risk_on_regime_bond_signal | 33.3% |
| risk_on_regime_bond_signal_strong | 16.6% |
| roc_positive | 28.0% |
| roc_turning_dn | 5.7% |
| roc_turning_up | 3.7% |
| rsi_14_bullish | 27.3% |
| rsi_14_cross_dn_overbought_recent_3d | 1.2% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.4% |
| rsi_14_cross_up_oversold_recent_3d | 3.0% |
| rsi_14_extreme_ob | 0.2% |
| rsi_14_extreme_os | 1.6% |
| rsi_14_overbought | 3.3% |
| rsi_14_oversold | 16.1% |
| rsi_14_rising | 27.6% |
| rsi_21_bullish | 28.1% |
| rsi_21_cross_dn_overbought_recent_3d | 0.3% |
| rsi_21_cross_up_oversold_recent_3d | 1.5% |
| rsi_21_extreme_os | 0.4% |
| rsi_21_overbought | 0.7% |
| rsi_21_oversold | 5.7% |
| rsi_21_rising | 27.5% |
| rsi_2_bullish | 32.2% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 15.9% |
| rsi_2_cross_dn_overbought_recent_3d | 24.6% |
| rsi_2_cross_up_extreme_os_recent_3d | 15.1% |
| rsi_2_cross_up_oversold_recent_3d | 15.7% |
| rsi_2_extreme_ob | 19.8% |
| rsi_2_extreme_os | 48.0% |
| rsi_2_overbought | 23.9% |
| rsi_2_oversold | 57.2% |
| rsi_2_rising | 27.5% |
| rsi_9_bullish | 27.5% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.5% |
| rsi_9_cross_dn_overbought_recent_3d | 3.1% |
| rsi_9_cross_up_extreme_os_recent_3d | 2.2% |
| rsi_9_cross_up_oversold_recent_3d | 6.2% |
| rsi_9_extreme_ob | 1.8% |
| rsi_9_extreme_os | 7.8% |
| rsi_9_overbought | 9.7% |
| rsi_9_oversold | 30.0% |
| rsi_9_rising | 27.5% |
| s1_break_retest_short | 69.4% |
| sc_13d_filed_within_30d | 3.3% |
| sc_13g_filed_within_30d | 3.0% |
| sector_outperforming_spy | 30.8% |
| sector_underperforming_spy | 69.2% |
| shooting_star | 3.9% |
| sma_20_50_bullish | 39.5% |
| sma_20_50_golden_cross | 1.2% |
| sma_50_200_bullish | 45.7% |
| sma_50_200_golden_cross | 0.1% |
| sma_9_21_bullish | 30.0% |
| sma_9_21_golden_cross | 2.0% |
| smc_bos_bearish | 11.1% |
| smc_bos_bullish | 8.9% |
| smc_bos_retest_long | 4.8% |
| smc_bos_retest_short | 3.6% |
| smc_breaker_block_bearish | 13.6% |
| smc_breaker_block_bullish | 15.2% |
| smc_choch_bearish | 8.5% |
| smc_choch_bullish | 3.1% |
| smc_equal_highs_swept | 1.9% |
| smc_equal_lows_swept | 5.6% |
| smc_fvg_bearish_active | 46.3% |
| smc_fvg_bullish_active | 29.7% |
| smc_fvg_retest_long_zone | 3.1% |
| smc_fvg_retest_short_zone | 2.0% |
| smc_in_discount_zone | 76.4% |
| smc_in_premium_zone | 40.3% |
| smc_inverse_fvg_bearish | 88.8% |
| smc_inverse_fvg_bullish | 60.3% |
| smc_liquidity_swept_dn | 2.6% |
| smc_liquidity_swept_up | 1.3% |
| smc_mitigation_block_long | 4.0% |
| smc_mitigation_block_short | 1.4% |
| smc_ob_bearish_active | 41.1% |
| smc_ob_bullish_active | 22.8% |
| smc_ote_long_zone | 10.5% |
| smc_ote_short_zone | 7.5% |
| squeeze_fire_dn | 2.1% |
| squeeze_fire_up | 1.2% |
| squeeze_in | 18.7% |
| squeeze_positive | 28.5% |
| stoch_bearish_cross | 11.0% |
| stoch_broad_overbought | 19.8% |
| stoch_broad_oversold | 49.3% |
| stoch_bullish_cross | 10.3% |
| stoch_overbought | 17.6% |
| stoch_oversold | 43.0% |
| stochrsi_cross_dn | 17.7% |
| stochrsi_cross_up | 20.5% |
| stochrsi_overbought | 23.6% |
| stochrsi_oversold | 49.7% |
| supertrend_bearish | 4.2% |
| supertrend_bullish | 95.8% |
| supertrend_flip_dn | 1.9% |
| supertrend_flip_recent_long_5d | 4.9% |
| supertrend_flip_recent_short_5d | 5.8% |
| supertrend_flip_up | 1.6% |
| support_break_retest | 44.2% |
| tema_above_dema | 30.4% |
| tema_cross_dn | 3.6% |
| tema_cross_up | 1.6% |
| three_black_crows | 12.3% |
| three_white_soldiers | 4.3% |
| triangle_apex_break_retest_long | 7.7% |
| triangle_ascending_detected | 8.8% |
| triangle_descending_detected | 9.7% |
| uo_overbought | 1.9% |
| uo_oversold | 4.5% |
| usd_strengthening | 28.7% |
| usd_weakening | 13.2% |
| vix_band_high | 47.4% |
| vix_band_low | 29.4% |
| vix_band_mid | 23.3% |
| vix_term_backwardation | 16.3% |
| vix_term_contango | 83.7% |
| vol_above_avg | 46.5% |
| vol_below_avg | 53.5% |
| vol_spike_12x | 30.3% |
| vol_spike_15x | 15.1% |
| vol_spike_17x | 10.3% |
| vol_spike_2x | 6.8% |
| vol_spike_2x_on_down_day_recent_3d | 7.0% |
| vol_spike_2x_on_up_day_recent_3d | 3.6% |
| vol_spike_3x | 2.7% |
| vp_above_value_area | 13.0% |
| vp_below_value_area | 37.2% |
| vp_close_above_poc | 32.2% |
| vp_close_below_poc | 67.8% |
| vp_in_value_area | 49.9% |
| week_open_gap_down_15pct | 1.8% |
| week_open_gap_up_15pct | 1.0% |
| weekly_above_ema_10 | 28.1% |
| weekly_above_ema_20 | 27.9% |
| weekly_bias_bear | 69.6% |
| weekly_bias_bull | 25.6% |
| weekly_momentum_pos | 28.9% |
| williams_r_overbought | 21.5% |
| williams_r_oversold | 52.9% |
| williams_r_rising | 32.5% |
| within_pead_window | 37.2% |
| within_post_deletion_window | 6.2% |
| xs_avoid_high_ivol | 72.6% |
| xs_avoid_high_max | 75.7% |
| xs_high_beta_decile | 27.2% |
| xs_low_beta_bottom_quintile | 27.2% |
| xs_low_beta_decile | 15.7% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 15.7% |
| xs_momentum_bottom_decile | 6.9% |
| xs_momentum_bottom_quintile | 21.8% |
| xs_momentum_top_decile | 6.8% |
| xs_momentum_top_quintile | 14.3% |
| xs_quality_bottom_quintile | 20.2% |
| xs_quality_top_quintile | 18.3% |
| xs_quality_top_tercile | 37.0% |
| year_high_break_retest_long | 0.4% |
| year_low_break_retest_short | 4.5% |
| yoy_surprise_high | 51.6% |
| yoy_surprise_negative | 36.7% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 88.9% |
| committed_growth_holders | 88.9% |
| corp_donations_1y | 7.6% |
| corp_donations_count_1y | 7.6% |
| corp_donations_unique_pacs | 7.6% |
| cot_rut_commercials_pctile_3y | 52.6% |
| cot_rut_mmoney_pctile_3y | 52.6% |
| cup_handle_depth_pct | 29.2% |
| days_since_deletion | 9.6% |
| days_since_inclusion | 14.4% |
| days_to_next_holiday | 68.3% |
| days_to_rebalance | 9.4% |
| dpi_30d_avg | 96.6% |
| dpi_recent | 96.6% |
| earnings_announcement_return | 92.2% |
| earnings_eps_yoy_growth | 95.1% |
| gov_contracts_4q_sum | 41.2% |
| gov_contracts_last_qtr_amount | 41.2% |
| gov_contracts_qoq_growth | 41.2% |
| head_shoulders_magnitude_pct | 9.3% |
| insider_director_buyers_30d | 5.2% |
| insider_officer_buyers_30d | 5.2% |
| insider_total_shares_bought_30d | 5.2% |
| insider_unique_buyers_30d | 5.2% |
| inverted_cup_handle_height_pct | 24.9% |
| lobbying_amount_1y | 72.7% |
| lobbying_amount_q | 72.7% |
| lobbying_amount_yoy | 72.7% |
| monthly_momentum_6m | 96.5% |
| otc_short_ratio_recent | 96.6% |
| otc_volume_recent | 96.6% |
| pair_half_life | 89.7% |
| pair_max_abs_zscore | 89.7% |
| pair_zscore_signed | 89.7% |
| pct_from_avwap_20high | 87.6% |
| pct_from_avwap_20low | 71.7% |
| pct_from_avwap_252low | 92.7% |
| pct_from_avwap_50low | 84.0% |
| persistent_holders_4q | 88.9% |
| persistent_holders_8q | 88.9% |
| sc_13g_latest_percent_owned | 1.5% |
| search_volume_index_recent | 79.5% |
| search_volume_observations | 79.5% |
| search_volume_zscore_30d | 79.5% |
| sector_etf_return_20d | 2.6% |
| spy_return_20d | 2.6% |
| total_active_holders | 88.9% |
| triangle_breakdown_pct | 9.7% |
| triangle_breakout_pct | 8.8% |
| xs_quality_decile | 62.9% |
| xs_quality_gross_profitability | 62.9% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.997), `avwap_20low` (0.996), `avwap_252low` (0.996), `avwap_50low` (0.997), `bb_10_20_lower` (0.995), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.997), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.998), `bb_20_20_lower` (0.996), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.997), `cam_r1` (0.996), `cam_r2` (0.996), `cam_r3` (0.996), `cam_r4` (0.996), `cam_s1` (0.996), `cam_s2` (0.996), `cam_s3` (0.996), `cam_s4` (0.996), `chandelier_long_value` (0.999), `chandelier_short_value` (0.998), `cpr_bottom` (0.996), `cpr_top` (0.996), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `days_since_classification_change` (-1.0), `dc10_lower` (0.996), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.996), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.998), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.992), `entry_stop_short` (0.996), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.998), `fib_ext_127` (0.993), `fib_ext_162` (0.991), `flag_bear_breakdown_level` (1.0), `flag_bear_pole_move_pct` (-1.0), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.996), `ichi_kijun` (0.999), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.995), `ichi_tenkan` (0.998), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.994), `monthly_sma_12` (0.994), `monthly_sma_6` (0.998), `pivot` (0.996), `prev_close` (0.996), `prev_high` (0.996), `prev_low` (0.996), `psar_value` (0.998), `r1` (0.996), `r2` (0.997), `r3` (0.997), `s1` (0.996), `s2` (0.995), `s3` (0.994), `supertrend_value` (0.993), `swing_high` (0.996), `swing_low` (0.995), `tema` (0.996), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.995), `vp_value_area_low` (0.996), `vwap` (0.966), `vwap_lower_1` (0.962), `vwap_lower_2` (0.955), `vwap_upper_1` (0.967), `vwap_upper_2` (0.968), `weekly_close` (0.994), `weekly_ema_10` (1.0), `weekly_ema_20` (0.998), `wood_p` (0.996), `wood_r1` (0.996), `wood_r2` (0.997), `wood_s1` (0.995), `wood_s2` (0.995), `year_high` (0.983), `year_low` (0.984)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | buffer pct (price vs cpr_top) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | buffer pct (price below cpr_bottom by) | 2 | **FIRE-ADDING** | **YES** |
| P3.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | **YES** |
| P4.1 | width threshold (cpr_width < rng * X) | 3 | **FIRE-ADDING** | **YES** |
| P5.1 | span triple (fast, slow, signal) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P6.1 | span triple (mirror of the bearish entry | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P7.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | **YES** |
| P8 | rsi_14 < 50 | 4 | subset-safe | no - derives offline |
| P9 | rsi_14 > 50 | 2 | subset-safe | no - derives offline |
| P10 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 2 x 3 x 3 x 1 x 1 x 3 x 4 x 2 x 1 = 432
offline gradings   8 level-combinations x 24 exits = 192
ENGINE RUNS        54 (every fire-adding axis sits at production-only until its env actuator exists)
check              54 x 8 = 432
```

B-row candidates NOT in this factorial: 639 census axes join it only when REGISTERED at the T3 band review.
