# Table A - cup_and_handle_retest_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:26:39 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** chart_pattern | **status:** NOT-STARTED | **R5 fires:** 99 | **surviving fires (T1):** 99 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  cup_handle_detected  <- backtest/signals/chart_patterns.py +1
       DEFN: cup-and-handle geometry detected / neckline break-retest (chart_patterns.py)
       knobs P1.1-P1.1 (band rows in Table A)
P2  cup_handle_neckline_break_retest_long  <- backtest/signals/chart_patterns.py +1
       DEFN: cup-and-handle geometry detected / neckline break-retest (chart_patterns.py)
       knobs P2.1-P2.1 (band rows in Table A)
P3  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P3.1-P3.1 (band rows in Table A)
P4  price_above_ema_50  <- backtest/signals/screener.py
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P4.1-P4.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P5  rsi_14 < 70   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_cup_and_handle_retest_long (docstring and return dropped):

```python
fires = s.get('cup_handle_detected', False) and s.get('cup_handle_neckline_break_retest_long', False) and s.get('price_above_ema_200', False) and s.get('price_above_ema_50', False) and (s.get('rsi_14', 50) < 70)
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
| P1 | PRODUCER | cup_handle_detected - emitted by backtest/signals/chart_patterns.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | cup-and-handle geometry detected / neckline break-retest (chart_patterns.py) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | detector tolerances (rim match, depth, handle pullback) - backtest/signals/chart_patterns.py detect_cup_and_handle | BRACKET the detector's shipped tolerances | detect_cup_and_handle defaults | each tolerance bracketed [0.5x, 1x, 1.5x] of production | none - pattern geometry unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | cup_handle_neckline_break_retest_long - emitted by backtest/signals/chart_patterns.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | cup-and-handle geometry detected / neckline break-retest (chart_patterns.py) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | retest window + neckline tolerance - backtest/signals/chart_patterns.py compute_cup_handle_neckline_break_retest_signals | BRACKET production (B685 producer) | producer defaults | window [3, 5, 10]; tolerance [0, 0.2, 0.5] pct | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | price_above_ema_50 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | ema span - backtest/signals/technical.py compute_ema_sma | BRACKET production with adjacent canon spans | 50 | [20, 50, 100] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY | rsi_14 `< 70` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 70` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 70` | 100.0% | TIGHTER = LOWER the ceiling: 60.696 -> 20 (20%); 63.084 -> 40 (40%); 64.752 -> 59 (60%); 67.214 -> 79 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.266, 20.682, 24.49, 28.588 | 16.266: 79 (80%); 20.682: 59 (60%); 24.49: 40 (40%); 28.588: 20 (20%) | 16.266: 20 (20%); 20.682: 40 (40%); 24.49: 59 (60%); 28.588: 79 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 14.01, 15.75, 17.168, 19.5 | 14.01: 79 (80%); 15.75: 59 (60%); 17.168: 40 (40%); 19.5: 20 (20%) | 14.01: 20 (20%); 15.75: 40 (40%); 17.168: 59 (60%); 19.5: 79 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 25.754, 28.008, 30.232, 33.764 | 25.754: 79 (80%); 28.008: 59 (60%); 30.232: 40 (40%); 33.764: 20 (20%) | 25.754: 20 (20%); 28.008: 40 (40%); 30.232: 59 (60%); 33.764: 79 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 1.6859, 2.2939, 4.1485, 8.0426 | 1.6859: 79 (80%); 2.2939: 59 (60%); 4.1485: 40 (40%); 8.0426: 20 (20%) | 1.6859: 20 (20%); 2.2939: 40 (40%); 4.1485: 59 (60%); 8.0426: 79 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.712, 1.9892, 2.2198, 2.4674 | 1.712: 79 (80%); 1.9892: 59 (60%); 2.2198: 40 (40%); 2.4674: 20 (20%) | 1.712: 20 (20%); 1.9892: 40 (40%); 2.2198: 59 (60%); 2.4674: 79 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0467, 0.0616, 0.0756, 0.0997 | 0.0467: 79 (80%); 0.0616: 60 (61%); 0.0756: 40 (40%); 0.0997: 20 (20%) | 0.0467: 20 (20%); 0.0616: 40 (40%); 0.0756: 59 (60%); 0.0997: 79 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.6324, 0.751, 0.8277, 0.8937 | 0.6324: 79 (80%); 0.751: 60 (61%); 0.8277: 40 (40%); 0.8937: 20 (20%) | 0.6324: 20 (20%); 0.751: 40 (40%); 0.8277: 59 (60%); 0.8937: 79 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0638, 0.0762, 0.0925, 0.1056 | 0.0638: 79 (80%); 0.0762: 59 (60%); 0.0925: 40 (40%); 0.1056: 20 (20%) | 0.0638: 20 (20%); 0.0762: 40 (40%); 0.0925: 59 (60%); 0.1056: 79 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.8392, 0.9466, 1.0053, 1.0971 | 0.8392: 79 (80%); 0.9466: 59 (60%); 1.0053: 40 (40%); 1.0971: 20 (20%) | 0.8392: 20 (20%); 0.9466: 40 (40%); 1.0053: 59 (60%); 1.0971: 79 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0851, 0.1016, 0.1234, 0.1408 | 0.0851: 79 (80%); 0.1016: 59 (60%); 0.1234: 40 (40%); 0.1408: 20 (20%) | 0.0851: 20 (20%); 0.1016: 40 (40%); 0.1234: 59 (60%); 0.1408: 79 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.7544, 0.835, 0.879, 0.9479 | 0.7544: 79 (80%); 0.835: 59 (60%); 0.879: 40 (40%); 0.9479: 20 (20%) | 0.7544: 20 (20%); 0.835: 40 (40%); 0.879: 59 (60%); 0.9479: 79 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0652, -0.0343, -0.0097, 0.0201 | -0.0652: 79 (80%); -0.0343: 59 (60%); -0.0097: 41 (41%); 0.0201: 21 (21%) | -0.0652: 20 (20%); -0.0343: 40 (40%); -0.0097: 60 (61%); 0.0201: 80 (81%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1457, 0.1794, 0.2266, 0.2605 | 0.1457: 79 (80%); 0.1794: 59 (60%); 0.2266: 40 (40%); 0.2605: 20 (20%) | 0.1457: 20 (20%); 0.1794: 40 (40%); 0.2266: 59 (60%); 0.2605: 79 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 99 (100%) | 0: 94 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | 0.0546, 0.1122, 0.1626, 0.2212 | 0.0546: 79 (80%); 0.1122: 59 (60%); 0.1626: 41 (41%); 0.2212: 20 (20%) | 0.0546: 20 (20%); 0.1122: 40 (40%); 0.1626: 60 (61%); 0.2212: 79 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 99 (100%); 1: 41 (41%) | 0: 58 (59%); 1: 84 (85%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2396, -0.2132, -0.1784, -0.1197 | -0.2396: 80 (81%); -0.2132: 60 (61%); -0.1784: 40 (40%); -0.1197: 21 (21%) | -0.2396: 21 (21%); -0.2132: 45 (45%); -0.1784: 59 (60%); -0.1197: 80 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4064, 0.6026, 0.7231, 0.7756 | 0.4064: 79 (80%); 0.6026: 61 (62%); 0.7231: 40 (40%); 0.7756: 21 (21%) | 0.4064: 20 (20%); 0.6026: 41 (41%); 0.7231: 59 (60%); 0.7756: 80 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.391, 0.5128, 0.85 | 0.2628: 81 (82%); 0.391: 60 (61%); 0.5128: 40 (40%); 0.85: 20 (20%) | 0.2628: 21 (21%); 0.391: 41 (41%); 0.5128: 59 (60%); 0.85: 79 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1336, -0.0195, 0.0927, 0.1926 | -0.1336: 79 (80%); -0.0195: 59 (60%); 0.0927: 40 (40%); 0.1926: 20 (20%) | -0.1336: 20 (20%); -0.0195: 40 (40%); 0.0927: 59 (60%); 0.1926: 79 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2321, 0.4487, 0.5769, 0.727 | 0.2321: 79 (80%); 0.4487: 60 (61%); 0.5769: 43 (43%); 0.727: 20 (20%) | 0.2321: 20 (20%); 0.4487: 41 (41%); 0.5769: 61 (62%); 0.727: 79 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1667, 0.2654, 0.4513, 0.6398 | 0.1667: 80 (81%); 0.2654: 59 (60%); 0.4513: 40 (40%); 0.6398: 20 (20%) | 0.1667: 22 (22%); 0.2654: 40 (40%); 0.4513: 59 (60%); 0.6398: 79 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5401, -0.4168, -0.2195, 0.0965 | -0.5401: 80 (81%); -0.4168: 59 (60%); -0.2195: 40 (40%); 0.0965: 21 (21%) | -0.5401: 22 (22%); -0.4168: 40 (40%); -0.2195: 59 (60%); 0.0965: 80 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4743, 0.6974, 0.9513 | 0.2692: 83 (84%); 0.4743: 59 (60%); 0.6974: 40 (40%); 0.9513: 20 (20%) | 0.2692: 21 (21%); 0.4743: 40 (40%); 0.6974: 59 (60%); 0.9513: 79 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2397, 0.4872, 0.6205, 0.8577 | 0.2397: 79 (80%); 0.4872: 60 (61%); 0.6205: 40 (40%); 0.8577: 20 (20%) | 0.2397: 20 (20%); 0.4872: 41 (41%); 0.6205: 59 (60%); 0.8577: 79 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0667, -0.0599, -0.045, 0 | -0.0667: 80 (81%); -0.0599: 59 (60%); -0.045: 44 (44%); 0: 25 (25%) | -0.0667: 21 (21%); -0.0599: 40 (40%); -0.045: 60 (61%); 0: 96 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4872, 0.7308, 0.8384, 0.9962 | 0.4872: 80 (81%); 0.7308: 60 (61%); 0.8384: 40 (40%); 0.9962: 20 (20%) | 0.4872: 21 (21%); 0.7308: 45 (45%); 0.8384: 59 (60%); 0.9962: 79 (80%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1603, 0.2756, 0.5962, 0.859 | 0.1603: 80 (81%); 0.2756: 60 (61%); 0.5962: 41 (41%); 0.859: 21 (21%) | 0.1603: 24 (24%); 0.2756: 42 (42%); 0.5962: 60 (61%); 0.859: 81 (82%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0446, 0.0064, 0.0403, 0.0916 | -0.0446: 79 (80%); 0.0064: 60 (61%); 0.0403: 40 (40%); 0.0916: 20 (20%) | -0.0446: 20 (20%); 0.0064: 42 (42%); 0.0403: 59 (60%); 0.0916: 79 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3273, 0.5297, 0.8478, 0.9487 | 0.3273: 79 (80%); 0.5297: 59 (60%); 0.8478: 41 (41%); 0.9487: 21 (21%) | 0.3273: 20 (20%); 0.5297: 40 (40%); 0.8478: 62 (63%); 0.9487: 80 (81%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.4301, 0.7308, 0.8795 | 0.1795: 80 (81%); 0.4301: 59 (60%); 0.7308: 41 (41%); 0.8795: 20 (20%) | 0.1795: 21 (21%); 0.4301: 40 (40%); 0.7308: 60 (61%); 0.8795: 79 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0203, 0.0606, 0.1876 | -0.0812: 91 (92%); -0.0203: 63 (64%); 0.0606: 40 (40%); 0.1876: 23 (23%) | -0.0812: 26 (26%); -0.0203: 43 (43%); 0.0606: 59 (60%); 0.1876: 81 (82%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2009, -0.0676, -0.0047, 0.0595 | -0.2009: 79 (80%); -0.0676: 59 (60%); -0.0047: 40 (40%); 0.0595: 20 (20%) | -0.2009: 20 (20%); -0.0676: 40 (40%); -0.0047: 59 (60%); 0.0595: 79 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1038, 0.4551, 0.5962, 0.7949 | 0.1038: 79 (80%); 0.4551: 61 (62%); 0.5962: 40 (40%); 0.7949: 22 (22%) | 0.1038: 20 (20%); 0.4551: 43 (43%); 0.5962: 59 (60%); 0.7949: 80 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2615, 0.4116, 0.6231, 0.8488 | 0.2615: 79 (80%); 0.4116: 59 (60%); 0.6231: 40 (40%); 0.8488: 20 (20%) | 0.2615: 20 (20%); 0.4116: 40 (40%); 0.6231: 59 (60%); 0.8488: 79 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0387, 0.086, 0.1722, 0.361 | 0.0387: 79 (80%); 0.086: 59 (60%); 0.1722: 40 (40%); 0.361: 20 (20%) | 0.0387: 20 (20%); 0.086: 40 (40%); 0.1722: 59 (60%); 0.361: 79 (80%) | OFFLINE |
| cup_handle_depth_pct | backtest/signals/chart_patterns.py | 100.0% | 0.1313, 0.1463, 0.1634, 0.194 | 0.1313: 79 (80%); 0.1463: 59 (60%); 0.1634: 40 (40%); 0.194: 20 (20%) | 0.1313: 20 (20%); 0.1463: 40 (40%); 0.1634: 59 (60%); 0.194: 79 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 99.0% | 33.4, 60.4, 71, 88 | 33.4: 78 (79%); 60.4: 59 (60%); 71: 39 (39%); 88: 20 (20%) | 33.4: 20 (20%); 60.4: 39 (39%); 71: 59 (60%); 88: 78 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7.6, 20, 28, 35 | 7.6: 79 (80%); 20: 61 (62%); 28: 43 (43%); 35: 21 (21%) | 7.6: 20 (20%); 20: 43 (43%); 28: 65 (66%); 35: 82 (83%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 80 (81%); 2: 61 (62%); 3: 32 (32%) | 1: 38 (38%); 2: 67 (68%); 3: 85 (86%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.014, -0.0095, -0.0011, 0.0138 | -0.014: 80 (81%); -0.0095: 60 (61%); -0.0011: 41 (41%); 0.0138: 21 (21%) | -0.014: 22 (22%); -0.0095: 41 (41%); -0.0011: 61 (62%); 0.0138: 80 (81%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.473, 24.9049, 26.0125, 26.7444 | 24.473: 80 (81%); 24.9049: 59 (60%); 26.0125: 40 (40%); 26.7444: 20 (20%) | 24.473: 21 (21%); 24.9049: 40 (40%); 26.0125: 59 (60%); 26.7444: 79 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.289, -0.0552, 0.1336, 0.5196 | -0.289: 79 (80%); -0.0552: 59 (60%); 0.1336: 40 (40%); 0.5196: 20 (20%) | -0.289: 20 (20%); -0.0552: 40 (40%); 0.1336: 59 (60%); 0.5196: 79 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.5196, -0.1336, 0.0552, 0.289 | -0.5196: 79 (80%); -0.1336: 59 (60%); 0.0552: 40 (40%); 0.289: 20 (20%) | -0.5196: 20 (20%); -0.1336: 40 (40%); 0.0552: 59 (60%); 0.289: 79 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0564, -0.0274, 0.0002, 0.0417 | -0.0564: 79 (80%); -0.0274: 59 (60%); 0.0002: 40 (40%); 0.0417: 20 (20%) | -0.0564: 20 (20%); -0.0274: 40 (40%); 0.0002: 59 (60%); 0.0417: 79 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0483, 8.4292, 8.6022, 8.9732 | 8.0483: 79 (80%); 8.4292: 59 (60%); 8.6022: 40 (40%); 8.9732: 20 (20%) | 8.0483: 20 (20%); 8.4292: 40 (40%); 8.6022: 59 (60%); 8.9732: 79 (80%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 0, 2.2, 5, 138 | 0: 99 (100%); 2.2: 59 (60%); 5: 43 (43%); 138: 20 (20%) | 0: 25 (25%); 2.2: 40 (40%); 5: 62 (63%); 138: 79 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 1, 2.8, 78.8 | 0: 99 (100%); 1: 64 (65%); 2.8: 40 (40%); 78.8: 20 (20%) | 0: 35 (35%); 1: 51 (52%); 2.8: 59 (60%); 78.8: 79 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | 0.0093, 0.2056, 0.3424, 0.7317 | 0.0093: 79 (80%); 0.2056: 59 (60%); 0.3424: 40 (40%); 0.7317: 20 (20%) | 0.0093: 20 (20%); 0.2056: 40 (40%); 0.3424: 59 (60%); 0.7317: 79 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.5315, 0.9584, 1.5923, 3.1163 | 0.5315: 79 (80%); 0.9584: 59 (60%); 1.5923: 40 (40%); 3.1163: 20 (20%) | 0.5315: 20 (20%); 0.9584: 40 (40%); 1.5923: 59 (60%); 3.1163: 79 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | 0.2244, 0.7052, 1.1316, 2.5224 | 0.2244: 79 (80%); 0.7052: 59 (60%); 1.1316: 40 (40%); 2.5224: 20 (20%) | 0.2244: 20 (20%); 0.7052: 40 (40%); 1.1316: 59 (60%); 2.5224: 79 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.0838, 0.074, 0.2032, 0.3762 | -0.0838: 79 (80%); 0.074: 59 (60%); 0.2032: 40 (40%); 0.3762: 20 (20%) | -0.0838: 20 (20%); 0.074: 40 (40%); 0.2032: 59 (60%); 0.3762: 79 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.7637, 1.1205, 1.7088, 3.4712 | 0.7637: 79 (80%); 1.1205: 59 (60%); 1.7088: 40 (40%); 3.4712: 20 (20%) | 0.7637: 20 (20%); 1.1205: 40 (40%); 1.7088: 59 (60%); 3.4712: 79 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.6034, 1.0772, 1.6823, 3.1257 | 0.6034: 79 (80%); 1.0772: 60 (61%); 1.6823: 40 (40%); 3.1257: 20 (20%) | 0.6034: 20 (20%); 1.0772: 40 (40%); 1.6823: 59 (60%); 3.1257: 79 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 58.982, 63.634, 69.402, 73.716 | 58.982: 79 (80%); 63.634: 59 (60%); 69.402: 40 (40%); 73.716: 20 (20%) | 58.982: 20 (20%); 63.634: 40 (40%); 69.402: 59 (60%); 73.716: 79 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 100.0% | 0.0011, 0.0298, 0.0594, 0.1033 | 0.0011: 79 (80%); 0.0298: 59 (60%); 0.0594: 40 (40%); 0.1033: 20 (20%) | 0.0011: 21 (21%); 0.0298: 40 (40%); 0.0594: 59 (60%); 0.1033: 79 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0057, 0.0109, 0.0224, 0.0355 | 0.0057: 79 (80%); 0.0109: 59 (60%); 0.0224: 40 (40%); 0.0355: 20 (20%) | 0.0057: 20 (20%); 0.0109: 40 (40%); 0.0224: 59 (60%); 0.0355: 79 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1.2, 3, 9.4 | 0: 99 (100%); 1.2: 59 (60%); 3: 48 (48%); 9.4: 20 (20%) | 0: 30 (30%); 1.2: 40 (40%); 3: 62 (63%); 9.4: 79 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0844 | 0: 99 (100%); 0.0844: 20 (20%) | 0: 73 (74%); 0.0844: 79 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1882, 0.395, 0.54 | 0: 99 (100%); 0.1882: 59 (60%); 0.395: 40 (40%); 0.54: 20 (20%) | 0: 36 (36%); 0.1882: 40 (40%); 0.395: 59 (60%); 0.54: 79 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 6 | 0: 99 (100%); 1: 64 (65%); 3: 41 (41%); 6: 23 (23%) | 0: 35 (35%); 1: 44 (44%); 3: 69 (70%); 6: 80 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1.2, 3, 9.4 | 0: 99 (100%); 1.2: 59 (60%); 3: 48 (48%); 9.4: 20 (20%) | 0: 30 (30%); 1.2: 40 (40%); 3: 62 (63%); 9.4: 79 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 8 | 0: 99 (100%); 1: 65 (66%); 2: 48 (48%); 8: 21 (21%) | 0: 34 (34%); 1: 51 (52%); 2: 61 (62%); 8: 81 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.1203, 0.259, 0.4178, 0.6455 | 0.1203: 79 (80%); 0.259: 59 (60%); 0.4178: 40 (40%); 0.6455: 20 (20%) | 0.1203: 20 (20%); 0.259: 40 (40%); 0.4178: 59 (60%); 0.6455: 79 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1498, 0.48 | 0: 95 (96%); 0.1498: 40 (40%); 0.48: 20 (20%) | 0: 51 (52%); 0.1498: 59 (60%); 0.48: 79 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2288, 0.5 | 0: 97 (98%); 0.2288: 40 (40%); 0.5: 22 (22%) | 0: 41 (41%); 0.2288: 59 (60%); 0.5: 82 (83%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2288, 0.5 | 0: 97 (98%); 0.2288: 40 (40%); 0.5: 22 (22%) | 0: 41 (41%); 0.2288: 59 (60%); 0.5: 82 (83%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1561, 0, 0.0567 | -0.1561: 79 (80%); 0: 72 (73%); 0.0567: 20 (20%) | -0.1561: 20 (20%); 0: 77 (78%); 0.0567: 79 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6461, -0.2777, 0.2783, 1.161 | -0.6461: 80 (81%); -0.2777: 59 (60%); 0.2783: 40 (40%); 1.161: 20 (20%) | -0.6461: 23 (23%); -0.2777: 40 (40%); 0.2783: 59 (60%); 1.161: 79 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 3, 7, 11 | 2: 80 (81%); 3: 71 (72%); 7: 41 (41%); 11: 22 (22%) | 2: 28 (28%); 3: 45 (45%); 7: 63 (64%); 11: 80 (81%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0179, 0.0333, 0.0547, 0.0713 | 0.0179: 79 (80%); 0.0333: 59 (60%); 0.0547: 40 (40%); 0.0713: 20 (20%) | 0.0179: 20 (20%); 0.0333: 40 (40%); 0.0547: 59 (60%); 0.0713: 79 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0563, 0.0666, 0.0836, 0.1045 | 0.0563: 79 (80%); 0.0666: 59 (60%); 0.0836: 40 (40%); 0.1045: 20 (20%) | 0.0563: 20 (20%); 0.0666: 40 (40%); 0.0836: 59 (60%); 0.1045: 79 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | 0.0044, 0.0195, 0.0283, 0.0475 | 0.0044: 79 (80%); 0.0195: 60 (61%); 0.0283: 40 (40%); 0.0475: 20 (20%) | 0.0044: 20 (20%); 0.0195: 39 (39%); 0.0283: 59 (60%); 0.0475: 79 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 2.2764, 3.2074, 4.2398, 4.9852 | 2.2764: 79 (80%); 3.2074: 59 (60%); 4.2398: 40 (40%); 4.9852: 20 (20%) | 2.2764: 20 (20%); 3.2074: 40 (40%); 4.2398: 59 (60%); 4.9852: 79 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 100.0% | 5.2928, 6.678, 8.788, 10.4902 | 5.2928: 79 (80%); 6.678: 59 (60%); 8.788: 40 (40%); 10.4902: 20 (20%) | 5.2928: 20 (20%); 6.678: 40 (40%); 8.788: 59 (60%); 10.4902: 79 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 4.847, 5.8912, 6.8522, 8.2806 | 4.847: 79 (80%); 5.8912: 59 (60%); 6.8522: 40 (40%); 8.2806: 20 (20%) | 4.847: 20 (20%); 5.8912: 40 (40%); 6.8522: 59 (60%); 8.2806: 79 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -2.5836, 3.8308, 7.937, 19.791 | -2.5836: 79 (80%); 3.8308: 59 (60%); 7.937: 40 (40%); 19.791: 20 (20%) | -2.5836: 20 (20%); 3.8308: 40 (40%); 7.937: 59 (60%); 19.791: 79 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0315, 0.0391, 0.0521, 0.065 | 0.0315: 79 (80%); 0.0391: 59 (60%); 0.0521: 40 (40%); 0.065: 20 (20%) | 0.0315: 21 (21%); 0.0391: 40 (40%); 0.0521: 59 (60%); 0.065: 79 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.534, 0.7052, 0.7897, 0.8869 | 0.534: 79 (80%); 0.7052: 59 (60%); 0.7897: 40 (40%); 0.8869: 20 (20%) | 0.534: 20 (20%); 0.7052: 40 (40%); 0.7897: 59 (60%); 0.8869: 79 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 0.9249, 1.4595, 1.8536, 2.1791 | 0.9249: 79 (80%); 1.4595: 59 (60%); 1.8536: 40 (40%); 2.1791: 20 (20%) | 0.9249: 20 (20%); 1.4595: 40 (40%); 1.8536: 59 (60%); 2.1791: 79 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.0038, 0.2687, 0.4944, 0.772 | -0.0038: 79 (80%); 0.2687: 59 (60%); 0.4944: 40 (40%); 0.772: 20 (20%) | -0.0038: 20 (20%); 0.2687: 40 (40%); 0.4944: 59 (60%); 0.772: 79 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | 0.4039, 1.0779, 1.6311, 2.0576 | 0.4039: 79 (80%); 1.0779: 59 (60%); 1.6311: 40 (40%); 2.0576: 20 (20%) | 0.4039: 20 (20%); 1.0779: 40 (40%); 1.6311: 59 (60%); 2.0576: 79 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 2.4652, 4.2306, 5.5938, 7.4496 | 2.4652: 79 (80%); 4.2306: 59 (60%); 5.5938: 40 (40%); 7.4496: 20 (20%) | 2.4652: 20 (20%); 4.2306: 40 (40%); 5.5938: 59 (60%); 7.4496: 79 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 58.53, 76.312, 86.756, 92.206 | 58.53: 79 (80%); 76.312: 59 (60%); 86.756: 40 (40%); 92.206: 20 (20%) | 58.53: 20 (20%); 76.312: 40 (40%); 86.756: 59 (60%); 92.206: 79 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 57.248, 59.656, 62.044, 63.328 | 57.248: 79 (80%); 59.656: 59 (60%); 62.044: 40 (40%); 63.328: 20 (20%) | 57.248: 20 (20%); 59.656: 40 (40%); 62.044: 59 (60%); 63.328: 79 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 63.04, 66.332, 68.972, 71.298 | 63.04: 80 (81%); 66.332: 59 (60%); 68.972: 40 (40%); 71.298: 20 (20%) | 63.04: 21 (21%); 66.332: 40 (40%); 68.972: 59 (60%); 71.298: 79 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 98 (99%) | 0: 99 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0336, 0.0429, 0.0557, 0.0807 | 0.0336: 79 (80%); 0.0429: 59 (60%); 0.0557: 40 (40%); 0.0807: 20 (20%) | 0.0336: 20 (20%); 0.0429: 40 (40%); 0.0557: 59 (60%); 0.0807: 79 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0922, -0.0623, -0.0463, -0.0326 | -0.0922: 79 (80%); -0.0623: 60 (61%); -0.0463: 40 (40%); -0.0326: 20 (20%) | -0.0922: 20 (20%); -0.0623: 40 (40%); -0.0463: 59 (60%); -0.0326: 79 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 99 (100%); 1: 25 (25%) | 0: 74 (75%); 1: 86 (87%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.6688, 0.8401, 0.9227, 0.9527 | 0.6688: 79 (80%); 0.8401: 59 (60%); 0.9227: 40 (40%); 0.9527: 20 (20%) | 0.6688: 20 (20%); 0.8401: 40 (40%); 0.9227: 59 (60%); 0.9527: 79 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 46.06, 68.7, 86.36, 110.72 | 46.06: 79 (80%); 68.7: 59 (60%); 86.36: 40 (40%); 110.72: 20 (20%) | 46.06: 20 (20%); 68.7: 40 (40%); 86.36: 59 (60%); 110.72: 79 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 1.6105, 2.5909, 4.123, 7.597 | 1.6105: 79 (80%); 2.5909: 59 (60%); 4.123: 40 (40%); 7.597: 20 (20%) | 1.6105: 20 (20%); 2.5909: 40 (40%); 4.123: 59 (60%); 7.597: 79 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 73.704, 82.952, 86.098, 90.14 | 73.704: 79 (80%); 82.952: 59 (60%); 86.098: 40 (40%); 90.14: 20 (20%) | 73.704: 20 (20%); 82.952: 40 (40%); 86.098: 59 (60%); 90.14: 79 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 73.99, 83.448, 88.066, 91.862 | 73.99: 79 (80%); 83.448: 59 (60%); 88.066: 40 (40%); 91.862: 20 (20%) | 73.99: 20 (20%); 83.448: 40 (40%); 88.066: 59 (60%); 91.862: 79 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 40.942, 67.524, 82.962, 93.444 | 40.942: 79 (80%); 67.524: 59 (60%); 82.962: 40 (40%); 93.444: 20 (20%) | 40.942: 20 (20%); 67.524: 40 (40%); 82.962: 59 (60%); 93.444: 79 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 31.38, 63.472, 84.788, 100 | 31.38: 79 (80%); 63.472: 59 (60%); 84.788: 40 (40%); 100: 22 (22%) | 31.38: 20 (20%); 63.472: 40 (40%); 84.788: 59 (60%); 100: 99 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 13, 18 | 4: 81 (82%); 9: 61 (62%); 13: 48 (48%); 18: 22 (22%) | 4: 24 (24%); 9: 41 (41%); 13: 63 (64%); 18: 89 (90%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 18 | 4: 85 (86%); 8: 65 (66%); 13: 41 (41%); 18: 25 (25%) | 4: 22 (22%); 8: 41 (41%); 13: 61 (62%); 18: 80 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 54.392, 58.668, 61.576, 65.482 | 54.392: 79 (80%); 58.668: 59 (60%); 61.576: 40 (40%); 65.482: 20 (20%) | 54.392: 20 (20%); 58.668: 40 (40%); 61.576: 59 (60%); 65.482: 79 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0373, 0.1826, 0.4119, 0.6754 | 0.0373: 79 (80%); 0.1826: 59 (60%); 0.4119: 40 (40%); 0.6754: 20 (20%) | 0.0373: 20 (20%); 0.1826: 40 (40%); 0.4119: 59 (60%); 0.6754: 79 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 13.988, 16.4, 18.188, 21.326 | 13.988: 79 (80%); 16.4: 59 (60%); 18.188: 40 (40%); 21.326: 20 (20%) | 13.988: 20 (20%); 16.4: 40 (40%); 18.188: 59 (60%); 21.326: 79 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 13.988, 16.4, 18.188, 21.326 | 13.988: 79 (80%); 16.4: 59 (60%); 18.188: 40 (40%); 21.326: 20 (20%) | 13.988: 20 (20%); 16.4: 40 (40%); 18.188: 59 (60%); 21.326: 79 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8425, 0.867, 0.8904, 0.9192 | 0.8425: 79 (80%); 0.867: 59 (60%); 0.8904: 40 (40%); 0.9192: 20 (20%) | 0.8425: 20 (20%); 0.867: 40 (40%); 0.8904: 59 (60%); 0.9192: 79 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.696, 0.802, 0.89, 1.154 | 0.696: 79 (80%); 0.802: 59 (60%); 0.89: 42 (42%); 1.154: 20 (20%) | 0.696: 20 (20%); 0.802: 40 (40%); 0.89: 60 (61%); 1.154: 79 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0364, 0.0543, 0.0783, 0.0946 | 0.0364: 79 (80%); 0.0543: 59 (60%); 0.0783: 40 (40%); 0.0946: 20 (20%) | 0.0364: 20 (20%); 0.0543: 40 (40%); 0.0783: 60 (61%); 0.0946: 79 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 99 (100%) | 0: 85 (86%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 99 (100%) | 0: 93 (94%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.043, 0.0581, 0.0761, 0.0906 | 0.043: 79 (80%); 0.0581: 60 (61%); 0.0761: 40 (40%); 0.0906: 21 (21%) | 0.043: 20 (20%); 0.0581: 40 (40%); 0.0761: 59 (60%); 0.0906: 79 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -24.998, -15.308, -9.542, -4.178 | -24.998: 79 (80%); -15.308: 59 (60%); -9.542: 40 (40%); -4.178: 20 (20%) | -24.998: 20 (20%); -15.308: 40 (40%); -9.542: 59 (60%); -4.178: 79 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.0% | 0.5273, 0.7408, 0.944, 1.1309 | 0.5273: 78 (79%); 0.7408: 59 (60%); 0.944: 39 (39%); 1.1309: 20 (20%) | 0.5273: 20 (20%); 0.7408: 39 (39%); 0.944: 59 (60%); 1.1309: 78 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.0% | 2.4, 4, 6, 8 | 2.4: 78 (79%); 4: 66 (67%); 6: 47 (47%); 8: 26 (26%) | 2.4: 20 (20%); 4: 43 (43%); 6: 63 (64%); 8: 85 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.0% | 0.1654, 0.1924, 0.222, 0.269 | 0.1654: 78 (79%); 0.1924: 59 (60%); 0.222: 39 (39%); 0.269: 20 (20%) | 0.1654: 20 (20%); 0.1924: 39 (39%); 0.222: 59 (60%); 0.269: 78 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.0% | 2, 3.8, 5, 7 | 2: 85 (86%); 3.8: 59 (60%); 5: 49 (49%); 7: 26 (26%) | 2: 23 (23%); 3.8: 39 (39%); 5: 65 (66%); 7: 81 (82%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.0% | 0.0252, 0.0301, 0.0358, 0.0447 | 0.0252: 78 (79%); 0.0301: 59 (60%); 0.0358: 40 (40%); 0.0447: 20 (20%) | 0.0252: 20 (20%); 0.0301: 40 (40%); 0.0358: 59 (60%); 0.0447: 78 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.0% | 3, 5, 6, 8 | 3: 83 (84%); 5: 61 (62%); 6: 45 (45%); 8: 25 (25%) | 3: 28 (28%); 5: 53 (54%); 6: 64 (65%); 8: 84 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.1395, -0.0688, -0.0047, 0.111 | -0.1395: 79 (80%); -0.0688: 59 (60%); -0.0047: 40 (40%); 0.111: 20 (20%) | -0.1395: 20 (20%); -0.0688: 40 (40%); -0.0047: 59 (60%); 0.111: 79 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 3, 4, 5, 7 | 3: 85 (86%); 4: 66 (67%); 5: 50 (51%); 7: 29 (29%) | 3: 33 (33%); 4: 49 (49%); 5: 61 (62%); 7: 80 (81%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 2.0% |
| 8k_item_5_02_filed_within_7d | 3.1% |
| above_avwap_20high | 70.7% |
| above_cam_r3 | 58.6% |
| above_cam_r4 | 30.3% |
| above_cpr | 83.8% |
| above_pivot | 84.8% |
| above_prev_high | 41.4% |
| above_prev_high_clearance_atr_05 | 13.1% |
| above_prev_low | 97.0% |
| above_r1 | 38.4% |
| above_r2 | 16.2% |
| above_vwap | 71.7% |
| above_wood_p | 78.8% |
| ad_rising | 76.8% |
| adx_cross_up | 2.0% |
| adx_cross_up_20 | 3.0% |
| adx_di_bear | 2.0% |
| adx_di_bull | 98.0% |
| adx_strong | 4.0% |
| adx_trending | 37.4% |
| ao_cross_up | 2.0% |
| ao_positive | 99.0% |
| at_key_fib | 12.1% |
| at_key_fib_wide | 23.2% |
| avwap_20high_loss_recent_3d | 17.2% |
| avwap_20high_reclaim_recent_3d | 51.7% |
| avwap_20low_reclaim_recent_3d | 9.1% |
| avwap_252low_reclaim_recent_3d | 5.1% |
| avwap_50low_reclaim_recent_3d | 5.1% |
| bb_10_20_above_mid | 91.9% |
| bb_10_20_expanding | 44.4% |
| bb_10_20_pctb_gt_75 | 61.6% |
| bb_10_20_pctb_gt_8 | 46.5% |
| bb_10_20_pctb_gt_85 | 34.3% |
| bb_10_20_pctb_gt_9 | 19.2% |
| bb_10_20_pctb_gt_95 | 11.1% |
| bb_10_20_reclaim_from_upper_recent_3d | 14.1% |
| bb_10_20_squeeze | 65.7% |
| bb_10_20_touch_upper | 18.2% |
| bb_20_15_expanding | 56.6% |
| bb_20_15_pctb_gt_75 | 93.9% |
| bb_20_15_pctb_gt_8 | 84.8% |
| bb_20_15_pctb_gt_85 | 77.8% |
| bb_20_15_pctb_gt_9 | 71.7% |
| bb_20_15_pctb_gt_95 | 58.6% |
| bb_20_15_reclaim_from_upper_recent_3d | 25.3% |
| bb_20_15_squeeze | 45.5% |
| bb_20_15_touch_upper | 61.6% |
| bb_20_20_expanding | 56.6% |
| bb_20_20_pctb_gt_75 | 80.8% |
| bb_20_20_pctb_gt_8 | 71.7% |
| bb_20_20_pctb_gt_85 | 51.5% |
| bb_20_20_pctb_gt_9 | 37.4% |
| bb_20_20_pctb_gt_95 | 19.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 17.2% |
| bb_20_20_squeeze | 16.2% |
| bb_20_20_touch_upper | 20.2% |
| bearish_pin_bar | 5.1% |
| below_avwap_20high | 29.3% |
| below_cam_s3 | 6.1% |
| below_cam_s4 | 2.0% |
| below_cpr | 15.2% |
| below_ema_9 | 2.0% |
| below_ema_9_break_recent_5d | 2.0% |
| below_prev_high | 58.6% |
| below_prev_low | 3.0% |
| below_prev_low_clearance_atr_05 | 1.0% |
| below_s1 | 2.0% |
| below_s2 | 1.0% |
| below_sma_200 | 10.1% |
| below_sma_50 | 1.0% |
| below_sma_9 | 9.1% |
| below_vwap | 28.3% |
| break_52w_high | 2.0% |
| break_52w_high_clearance_atr_05 | 1.0% |
| break_52w_high_confirmed_today | 1.0% |
| bullish_engulfing | 5.1% |
| bullish_pin_bar | 6.1% |
| capitulation_recent_3d | 1.0% |
| ceo_buy | 2.2% |
| cfo_buy | 2.2% |
| chandelier_short_bearish | 5.1% |
| chandelier_short_flip_up | 5.1% |
| close_in_bottom_40pct_of_range | 8.1% |
| close_in_top_40pct_of_range | 71.7% |
| cluster_buy | 1.1% |
| cmf_cross_dn | 2.0% |
| cmf_cross_up | 4.0% |
| cmf_negative | 8.1% |
| cmf_positive | 91.9% |
| concentrated_sell | 2.2% |
| cpr_narrow | 93.9% |
| cpr_narrow_tight | 24.2% |
| dc10_breakout_up | 34.3% |
| dc10_breakout_up_1pct | 58.6% |
| dc10_new_high | 41.4% |
| dc10_strong_breakout_up | 7.1% |
| dc20_breakout_up | 34.3% |
| dc20_new_high | 41.4% |
| dc20_resistance_break_retest_strong | 59.6% |
| defensive_leadership | 31.3% |
| director_only_buy | 2.2% |
| doji | 4.0% |
| double_bottom_detected | 19.2% |
| double_top_detected | 12.1% |
| dpi_elevated | 53.3% |
| drying_volume_on_up_turn | 68.7% |
| ema_20_50_bearish | 14.1% |
| ema_20_50_bullish | 85.9% |
| ema_20_50_golden_cross | 5.1% |
| ema_50_200_bearish | 44.4% |
| ema_50_200_bullish | 55.6% |
| ema_50_200_golden_cross | 2.0% |
| flag_bull_break_retest_long | 4.0% |
| flag_bull_broke | 6.1% |
| flag_bull_detected | 8.1% |
| force_index_cross_dn | 1.0% |
| force_index_cross_up | 3.0% |
| force_index_positive | 98.0% |
| gap_dn_1_5pct | 2.0% |
| gap_dn_2pct | 1.0% |
| gap_up_1_5pct | 1.0% |
| hammer | 3.0% |
| head_shoulders_bottom_detected | 6.1% |
| head_shoulders_top_detected | 2.0% |
| house_cluster_buy | 3.1% |
| house_cluster_sell | 3.1% |
| htf_aligned_bull | 80.8% |
| htf_disagreement | 1.0% |
| hull_bearish | 16.2% |
| hull_bullish | 83.8% |
| hull_flip_dn | 2.0% |
| hull_flip_up | 3.0% |
| ichi_above_cloud | 91.9% |
| ichi_above_cloud_break_recent_5d | 23.2% |
| ichi_below_cloud | 1.0% |
| ichi_cloud_thick | 78.8% |
| ichi_tk_bullish | 93.9% |
| ichi_tk_cross_up | 4.0% |
| ichi_weekly_above_cloud | 47.5% |
| ichi_weekly_below_cloud | 20.2% |
| ichi_weekly_in_cloud | 32.3% |
| inside_bar | 18.2% |
| inside_cpr | 5.1% |
| inside_kc | 78.8% |
| insider_cluster_active | 20.0% |
| institutional_buy | 71.7% |
| institutional_negative | 8.1% |
| institutional_persistence_growing | 35.1% |
| institutional_persistence_strong | 47.3% |
| institutional_strong_buy | 62.6% |
| inverted_cup_handle_detected | 37.4% |
| is_friday | 14.1% |
| is_halloween_period | 47.5% |
| is_january | 8.1% |
| is_january_extended | 12.1% |
| is_monday | 19.2% |
| is_pre_holiday | 4.0% |
| is_summer_period | 52.5% |
| is_totm_window | 40.4% |
| is_totm_window_first_day | 17.2% |
| is_week_open | 21.2% |
| kc_touch_upper | 32.3% |
| macd_12_26_9_bearish | 20.2% |
| macd_12_26_9_bullish | 79.8% |
| macd_12_26_9_crossover_dn | 3.0% |
| macd_12_26_9_crossover_up | 1.0% |
| macd_8_21_5_bearish | 32.3% |
| macd_8_21_5_bullish | 67.7% |
| macd_8_21_5_crossover_dn | 4.0% |
| macd_8_21_5_crossover_up | 2.0% |
| mfi_broad_overbought | 37.4% |
| mfi_overbought | 4.0% |
| monthly_above_sma_12 | 82.8% |
| monthly_above_sma_6 | 97.0% |
| monthly_bias_bear | 1.0% |
| monthly_bias_bull | 80.8% |
| monthly_momentum_pos | 80.8% |
| morning_star | 10.1% |
| near_52w_high | 11.1% |
| near_52w_high_95pct | 28.3% |
| near_52w_high_retest_long | 1.0% |
| near_avwap_20high_atr_05x | 87.9% |
| near_avwap_20low_atr_05x | 2.0% |
| near_avwap_20low_atr_10x | 14.1% |
| near_avwap_20low_atr_15x | 34.3% |
| near_avwap_20low_atr_20x | 66.7% |
| near_avwap_252low_atr_10x | 1.0% |
| near_avwap_252low_atr_15x | 6.1% |
| near_avwap_252low_atr_20x | 10.1% |
| near_avwap_50low_atr_15x | 5.1% |
| near_avwap_50low_atr_20x | 9.1% |
| near_cam_r3 | 31.3% |
| near_cam_s3 | 12.1% |
| near_cam_s4 | 2.0% |
| near_fib_236 | 7.1% |
| near_fib_382 | 10.1% |
| near_fib_500 | 2.0% |
| near_pivot | 24.2% |
| near_prev_close | 28.3% |
| near_prev_high | 27.3% |
| near_prev_low | 2.0% |
| near_r1 | 28.3% |
| near_r1_wide | 88.9% |
| near_r2 | 11.1% |
| near_r2_wide | 64.6% |
| near_s1 | 3.0% |
| near_s1_wide | 42.4% |
| near_s2 | 1.0% |
| near_s2_wide | 18.2% |
| near_wood_r1 | 22.2% |
| near_wood_s1 | 8.1% |
| news_uses_polygon_score | 15.2% |
| obv_bearish | 7.1% |
| obv_bullish | 92.9% |
| obv_diverge_bull | 4.0% |
| obv_falling | 27.3% |
| obv_rising | 72.7% |
| outside_bar | 9.1% |
| pead_negative_surprise | 20.4% |
| pead_positive_surprise | 25.8% |
| pin_bar | 11.1% |
| po3_accumulation_active | 58.6% |
| po3_bullish | 19.2% |
| po3_manipulation_sweep_down | 5.1% |
| po3_manipulation_sweep_up | 26.3% |
| po3_mmbm_setup | 4.0% |
| po3_sweep_above_prior_high | 69.7% |
| po3_sweep_below_prior_low | 31.3% |
| ppo_bullish | 79.8% |
| ppo_crossover_up | 2.0% |
| pre_fomc_d0 | 5.1% |
| pre_fomc_d1 | 3.0% |
| pre_fomc_window | 8.1% |
| price_above_dema | 76.8% |
| price_above_ema_200_break_recent_5d | 30.3% |
| price_above_ema_20_break_recent_5d | 15.2% |
| price_above_ema_21_break_recent_5d | 16.2% |
| price_above_ema_50_break_recent_5d | 20.2% |
| price_above_ema_9 | 98.0% |
| price_above_ema_9_break_recent_5d | 41.4% |
| price_above_hull | 61.6% |
| price_above_sma_200 | 89.9% |
| price_above_sma_50 | 99.0% |
| price_above_tema | 54.5% |
| price_below_dema | 23.2% |
| price_below_hull | 38.4% |
| price_below_tema | 45.5% |
| psar_bullish | 85.9% |
| psar_flip_dn | 2.0% |
| r1_break_retest_long | 96.0% |
| resistance_break_retest | 84.8% |
| risk_off_regime_bond_signal | 21.2% |
| risk_off_regime_bond_signal_strong | 4.0% |
| risk_off_regime_gold_signal | 28.3% |
| risk_on_regime_bond_signal | 49.5% |
| risk_on_regime_bond_signal_strong | 29.3% |
| rsi_14_cross_dn_overbought_recent_3d | 15.2% |
| rsi_14_rising | 79.8% |
| rsi_21_cross_dn_overbought_recent_3d | 1.0% |
| rsi_21_rising | 79.8% |
| rsi_2_bullish | 89.9% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 35.4% |
| rsi_2_cross_dn_overbought_recent_3d | 28.3% |
| rsi_2_cross_up_extreme_os_recent_3d | 22.2% |
| rsi_2_cross_up_oversold_recent_3d | 36.4% |
| rsi_2_extreme_ob | 48.5% |
| rsi_2_extreme_os | 1.0% |
| rsi_2_overbought | 64.6% |
| rsi_2_oversold | 3.0% |
| rsi_2_rising | 79.8% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 5.1% |
| rsi_9_cross_dn_overbought_recent_3d | 24.2% |
| rsi_9_overbought | 31.3% |
| rsi_9_rising | 79.8% |
| s1_break_retest_short | 14.1% |
| sc_13g_filed_within_30d | 3.4% |
| sector_outperforming_spy | 33.3% |
| sector_underperforming_spy | 66.7% |
| shooting_star | 3.0% |
| sma_20_50_bullish | 77.8% |
| sma_20_50_golden_cross | 7.1% |
| sma_50_200_bullish | 40.4% |
| sma_50_200_golden_cross | 1.0% |
| sma_9_21_bullish | 97.0% |
| sma_9_21_golden_cross | 1.0% |
| smc_bos_bearish | 18.2% |
| smc_bos_bullish | 8.1% |
| smc_bos_retest_long | 3.0% |
| smc_bos_retest_short | 4.0% |
| smc_breaker_block_bearish | 7.1% |
| smc_breaker_block_bullish | 22.2% |
| smc_choch_bearish | 7.1% |
| smc_choch_bullish | 21.2% |
| smc_equal_highs_swept | 2.0% |
| smc_equal_lows_swept | 5.1% |
| smc_fvg_bearish_active | 17.2% |
| smc_fvg_bullish_active | 61.6% |
| smc_fvg_retest_short_zone | 4.0% |
| smc_in_discount_zone | 9.1% |
| smc_inverse_fvg_bearish | 36.4% |
| smc_liquidity_swept_dn | 3.0% |
| smc_liquidity_swept_up | 1.0% |
| smc_mitigation_block_short | 13.1% |
| smc_ob_bearish_active | 27.3% |
| smc_ob_bullish_active | 44.4% |
| smc_ote_long_zone | 4.0% |
| smc_ote_short_zone | 21.2% |
| squeeze_in | 15.2% |
| stoch_bearish_cross | 10.1% |
| stoch_broad_overbought | 78.8% |
| stoch_bullish_cross | 10.1% |
| stoch_overbought | 73.7% |
| stochrsi_cross_dn | 35.4% |
| stochrsi_cross_up | 19.2% |
| stochrsi_overbought | 47.5% |
| stochrsi_oversold | 13.1% |
| tema_above_dema | 94.9% |
| tema_cross_up | 2.0% |
| three_white_soldiers | 18.2% |
| triangle_apex_break_retest_long | 39.4% |
| triangle_ascending_detected | 17.2% |
| triangle_descending_detected | 4.0% |
| uo_overbought | 4.0% |
| usd_strengthening | 9.1% |
| usd_weakening | 12.1% |
| vix_band_high | 21.2% |
| vix_band_low | 54.5% |
| vix_band_mid | 24.2% |
| vix_term_backwardation | 4.0% |
| vix_term_contango | 96.0% |
| vol_above_avg | 31.3% |
| vol_below_avg | 68.7% |
| vol_spike_12x | 13.1% |
| vol_spike_15x | 6.1% |
| vol_spike_17x | 3.0% |
| vol_spike_2x | 2.0% |
| vol_spike_2x_on_down_day_recent_3d | 2.0% |
| vol_spike_2x_on_up_day_recent_3d | 3.0% |
| vp_above_value_area | 66.7% |
| vp_close_above_poc | 94.9% |
| vp_close_below_poc | 5.1% |
| vp_in_value_area | 33.3% |
| week_open_gap_down_15pct | 2.0% |
| williams_r_overbought | 67.7% |
| williams_r_rising | 60.6% |
| within_pead_window | 39.8% |
| within_post_deletion_window | 16.7% |
| xs_avoid_high_ivol | 90.8% |
| xs_avoid_high_max | 85.7% |
| xs_high_beta_decile | 13.3% |
| xs_low_beta_bottom_quintile | 13.3% |
| xs_low_beta_decile | 20.4% |
| xs_low_beta_top_quintile | 20.4% |
| xs_momentum_bottom_decile | 3.0% |
| xs_momentum_bottom_quintile | 14.1% |
| xs_momentum_top_decile | 2.0% |
| xs_momentum_top_quintile | 12.1% |
| xs_quality_bottom_quintile | 9.8% |
| xs_quality_top_quintile | 21.3% |
| xs_quality_top_tercile | 41.0% |
| year_high_break_retest_long | 3.0% |
| yoy_surprise_high | 47.9% |
| yoy_surprise_negative | 44.7% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 74.7% |
| committed_growth_holders | 74.7% |
| corp_donations_1y | 5.1% |
| corp_donations_count_1y | 5.1% |
| corp_donations_unique_pacs | 5.1% |
| cot_rut_commercials_pctile_3y | 40.4% |
| cot_rut_mmoney_pctile_3y | 40.4% |
| days_since_deletion | 6.1% |
| days_since_inclusion | 8.1% |
| days_to_cover | 97.0% |
| days_to_next_holiday | 64.6% |
| days_to_rebalance | 3.0% |
| dpi_30d_avg | 90.9% |
| dpi_recent | 90.9% |
| earnings_announcement_return | 93.9% |
| earnings_eps_yoy_growth | 94.9% |
| flag_bull_pole_move_pct | 8.1% |
| gov_contracts_4q_sum | 40.4% |
| gov_contracts_last_qtr_amount | 40.4% |
| gov_contracts_qoq_growth | 40.4% |
| head_shoulders_magnitude_pct | 7.1% |
| house_buy_count_90d | 97.0% |
| house_net_buy_90d | 97.0% |
| house_sell_count_90d | 97.0% |
| insider_officer_buyers_30d | 5.1% |
| insider_total_shares_bought_30d | 5.1% |
| insider_unique_buyers_30d | 5.1% |
| inverted_cup_handle_height_pct | 46.5% |
| lobbying_amount_1y | 69.7% |
| lobbying_amount_q | 69.7% |
| lobbying_amount_yoy | 69.7% |
| otc_short_ratio_recent | 90.9% |
| otc_volume_recent | 90.9% |
| pair_half_life | 93.9% |
| pair_max_abs_zscore | 93.9% |
| pair_zscore_signed | 93.9% |
| pct_from_avwap_20high | 58.6% |
| persistent_holders_4q | 74.7% |
| persistent_holders_8q | 74.7% |
| search_volume_index_recent | 78.8% |
| search_volume_observations | 78.8% |
| search_volume_zscore_30d | 78.8% |
| short_interest_observations | 97.0% |
| short_interest_pct | 96.0% |
| total_active_holders | 74.7% |
| triangle_breakdown_pct | 4.0% |
| triangle_breakout_pct | 17.2% |
| xs_quality_decile | 61.6% |
| xs_quality_gross_profitability | 61.6% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`atr` (0.956), `atr_14` (0.956), `avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.999), `avwap_50low` (1.0), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (1.0), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (1.0), `cam_s2` (1.0), `cam_s3` (1.0), `cam_s4` (1.0), `chandelier_long_value` (1.0), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (1.0), `double_bottom_neckline` (1.0), `double_bottom_trough` (1.0), `double_top_neckline` (1.0), `double_top_peak` (0.993), `entry_stop_long` (1.0), `entry_stop_short` (0.999), `fib_236` (0.999), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.999), `fib_ext_127` (0.999), `fib_ext_162` (0.998), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.997), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.997), `monthly_sma_6` (0.999), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (1.0), `psar_value` (0.999), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (1.0), `s2` (1.0), `s3` (0.999), `sector_etf_return_20d` (-1.0), `spy_return_20d` (-1.0), `supertrend_value` (1.0), `swing_high` (0.999), `swing_low` (0.998), `tema` (1.0), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.999), `vp_value_area_low` (0.998), `vwap` (0.987), `vwap_lower_1` (0.986), `vwap_lower_2` (0.985), `vwap_upper_1` (0.988), `vwap_upper_2` (0.988), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.999), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.995), `year_low` (0.992)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | detector tolerances (rim match, depth, h | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1.1 | retest window + neckline tolerance | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1.2 | retest window + neckline tolerance | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | ema span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P5 | rsi_14 < 70 | 5 | subset-safe | no - derives offline |
| P5.1 | rsi span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     3 x 3 x 3 x 3 x 3 x 5 x 3 = 3645
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (actuated fire-adding axes only)
PENDING ACTUATION  729 level-combinations are DEFINED but have no env knob - they are a FEATURE REQUEST, not a runnable band (plan 11.0b state 1; B2866)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 483 census axes join it only when REGISTERED at the T3 band review.
