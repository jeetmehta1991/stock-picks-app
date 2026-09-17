# Table A - stochrsi_oversold

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:05:47 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** momentum | **status:** NOT-STARTED | **R5 fires:** 2433 | **surviving fires (T1):** 2433 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_ema_200  <- backtest/signals/screener.py
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)
P2  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P2.1-P2.1 (band rows in Table A)
P3  rsi_2  <- backtest/signals/screener.py
       DEFN: Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540)
       knobs P3.1-P3.1 (band rows in Table A)
P4  stochrsi_cross_dn  <- backtest/signals/screener.py +1
       DEFN: k crosses below d while k > 20 (technical.py:600)
       knobs P4.1-P4.1 (band rows in Table A)
P5  stochrsi_cross_up  <- backtest/signals/screener.py +1
       DEFN: k crosses above d while k < 80 (technical.py:599)
       knobs P5.1-P5.1 (band rows in Table A)
P6  stochrsi_overbought  <- backtest/signals/screener.py +1
       DEFN: stochastic-RSI overbought = k > 80 (technical.py:598)
       knobs P6.1-P6.2 (band rows in Table A)
P7  stochrsi_oversold  <- backtest/signals/screener.py +2
       DEFN: stochastic-RSI k over period 14; oversold = k < 20 (technical.py:597)
       knobs P7.1-P7.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P8  rsi_14 < 55   [EXISTING-THRESHOLD]
P9  rsi_14 > 45   [EXISTING-THRESHOLD]
P10  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_stochrsi_oversold (docstring and return dropped):

```python
rsi_2 = s.get('rsi_2', 50)
above_200 = s.get('price_above_ema_200', False)
below_200 = s.get('below_ema_200', False)
fl = s.get('stochrsi_oversold') and s.get('stochrsi_cross_up') and (s.get('rsi_14', 50) < 55) and above_200
fs = s.get('stochrsi_overbought') and s.get('stochrsi_cross_dn') and (s.get('rsi_14', 50) > 45) and below_200 and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | below_ema_200 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | rsi_2 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | rsi (fast escape-hatch) span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 2 | [2, 3, 5] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | stochrsi_cross_dn - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | k crosses below d while k > 20 (technical.py:600) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | cross guard band (k > 20 on cross_dn) - backtest/signals/technical.py:600 | BRACKET production guard | 20 | 20, 30 | TIGHTER (k > 30) on persisted k/d | none needed - k and d both persisted | T3 review before any grid |
| P5 | PRODUCER | stochrsi_cross_up - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | k crosses above d while k < 80 (technical.py:599) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | cross guard band (k < 80 on cross_up) - backtest/signals/technical.py:599 | BRACKET production guard | 80 | 70, 80 | TIGHTER (k < 70) on persisted k/d | freshness itself (k vs d needs both persisted - both ARE); DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | PRODUCER | stochrsi_overbought - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | stochastic-RSI overbought = k > 80 (technical.py:598) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P6.x) | BANDS-DEFINED |
| P6.1 | BAND | overbought threshold on k - backtest/signals/technical.py:598 | BRACKET canon 80; stochrsi_k IS persisted | 80 | 75, 80, 85, 90 | TIGHTER (k > 85, k > 90) - subset on persisted stochrsi_k | LOOSER (k > 75); DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6.2 | BAND | period (rsi+stoch length) - technical.py:574 | BRACKET production | 14 | 10, 14, 21 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | PRODUCER | stochrsi_oversold - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | stochastic-RSI k over period 14; oversold = k < 20 (technical.py:597) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P7.x) | BANDS-DEFINED |
| P7.1 | BAND | period (rsi+stoch length) - backtest/signals/technical.py:574-600 | BRACKET production with the adjacent canon spans | 14 | 10, 14, 21 | none - k/d at other periods unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7.2 | BAND | oversold threshold on k - technical.py:597 | BRACKET canon 20; stochrsi_k IS persisted | 20 | 10, 15, 20, 25 | TIGHTER (k < 15, k < 10) - subset on persisted stochrsi_k | LOOSER (k < 25); DEFINED-NO-ACTUATOR | T3 review before any grid |
| P8 | STRATEGY | rsi_14 `< 55` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 55` | production + 3 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P8.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P9 | STRATEGY | rsi_14 `> 45` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 45` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
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
| rsi_14 | backtest/signals/screener.py | `< 55` | 100.0% | TIGHTER = LOWER the ceiling: 45.288 -> 487 (20%); 48.708 -> 973 (40%); 51.9 -> 1462 (60%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `> 45` | 100.0% | TIGHTER = RAISE the floor: 45.288 -> 1946 (80%); 48.708 -> 1460 (60%); 51.9 -> 974 (40%); 55.71 -> 488 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.874, 20.33, 24.072, 28.81 | 16.874: 1946 (80%); 20.33: 1461 (60%); 24.072: 973 (40%); 28.81: 488 (20%) | 16.874: 487 (20%); 20.33: 975 (40%); 24.072: 1460 (60%); 28.81: 1947 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 18.21, 21.298, 24.14, 27.336 | 18.21: 1949 (80%); 21.298: 1460 (60%); 24.14: 974 (40%); 27.336: 487 (20%) | 18.21: 488 (20%); 21.298: 973 (40%); 24.14: 1461 (60%); 27.336: 1946 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.39, 21.528, 24.33, 28.282 | 18.39: 1947 (80%); 21.528: 1460 (60%); 24.33: 975 (40%); 28.282: 487 (20%) | 18.39: 488 (20%); 21.528: 973 (40%); 24.33: 1461 (60%); 28.282: 1946 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -3.2966, -0.7814, 0.5217, 2.4996 | -3.2966: 1946 (80%); -0.7814: 1460 (60%); 0.5217: 973 (40%); 2.4996: 487 (20%) | -3.2966: 487 (20%); -0.7814: 973 (40%); 0.5217: 1460 (60%); 2.4996: 1946 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.1648, 2.0621, 3.492, 5.992 | 1.1648: 1947 (80%); 2.0621: 1460 (60%); 3.492: 973 (40%); 5.992: 487 (20%) | 1.1648: 487 (20%); 2.0621: 973 (40%); 3.492: 1460 (60%); 5.992: 1946 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.1648, 2.0621, 3.492, 5.992 | 1.1648: 1947 (80%); 2.0621: 1460 (60%); 3.492: 973 (40%); 5.992: 487 (20%) | 1.1648: 487 (20%); 2.0621: 973 (40%); 3.492: 1460 (60%); 5.992: 1946 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.057, 2.512, 3.0382, 3.803 | 2.057: 1948 (80%); 2.512: 1462 (60%); 3.0382: 973 (40%); 3.803: 488 (20%) | 2.057: 489 (20%); 2.512: 974 (40%); 3.0382: 1460 (60%); 3.803: 1948 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0546, 0.0795, 0.1098, 0.1569 | 0.0546: 1948 (80%); 0.0795: 1461 (60%); 0.1098: 975 (40%); 0.1569: 487 (20%) | 0.0546: 490 (20%); 0.0795: 976 (40%); 0.1098: 1462 (60%); 0.1569: 1946 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.254, 0.4476, 0.68, 0.7968 | 0.254: 1946 (80%); 0.4476: 1460 (60%); 0.68: 973 (40%); 0.7968: 487 (20%) | 0.254: 487 (20%); 0.4476: 973 (40%); 0.68: 1460 (60%); 0.7968: 1946 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0549, 0.0758, 0.1014, 0.138 | 0.0549: 1948 (80%); 0.0758: 1461 (60%); 0.1014: 974 (40%); 0.138: 488 (20%) | 0.0549: 488 (20%); 0.0758: 976 (40%); 0.1014: 1462 (60%); 0.138: 1947 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.0948, 0.4328, 0.7483, 0.9673 | 0.0948: 1946 (80%); 0.4328: 1460 (60%); 0.7483: 973 (40%); 0.9673: 487 (20%) | 0.0948: 487 (20%); 0.4328: 973 (40%); 0.7483: 1460 (60%); 0.9673: 1946 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0732, 0.1011, 0.1351, 0.184 | 0.0732: 1948 (80%); 0.1011: 1460 (60%); 0.1351: 974 (40%); 0.184: 488 (20%) | 0.0732: 488 (20%); 0.1011: 976 (40%); 0.1351: 1460 (60%); 0.184: 1947 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.196, 0.4496, 0.6862, 0.8504 | 0.196: 1946 (80%); 0.4496: 1460 (60%); 0.6862: 973 (40%); 0.8504: 487 (20%) | 0.196: 487 (20%); 0.4496: 973 (40%); 0.6862: 1460 (60%); 0.8504: 1946 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0491, -0.0243, -0.0058, 0.0155 | -0.0491: 1948 (80%); -0.0243: 1460 (60%); -0.0058: 974 (40%); 0.0155: 491 (20%) | -0.0491: 494 (20%); -0.0243: 975 (40%); -0.0058: 1462 (60%); 0.0155: 1953 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1388, 0.167, 0.2083, 0.2663 | 0.1388: 1940 (80%); 0.167: 1460 (60%); 0.2083: 973 (40%); 0.2663: 487 (20%) | 0.1388: 493 (20%); 0.167: 973 (40%); 0.2083: 1460 (60%); 0.2663: 1946 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 2433 (100%) | 0: 2299 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.091, -0.0149, 0.0511, 0.1297 | -0.091: 1946 (80%); -0.0149: 1460 (60%); 0.0511: 973 (40%); 0.1297: 489 (20%) | -0.091: 487 (20%); -0.0149: 973 (40%); 0.0511: 1460 (60%); 0.1297: 1947 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 2433 (100%); 1: 949 (39%) | 0: 1484 (61%); 1: 2046 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2423, -0.1936, -0.1542, -0.1109 | -0.2423: 1956 (80%); -0.1936: 1461 (60%); -0.1542: 981 (40%); -0.1109: 488 (20%) | -0.2423: 491 (20%); -0.1936: 977 (40%); -0.1542: 1461 (60%); -0.1109: 1953 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3782, 0.5962, 0.6731, 0.7949 | 0.3782: 1955 (80%); 0.5962: 1463 (60%); 0.6731: 1025 (42%); 0.7949: 496 (20%) | 0.3782: 507 (21%); 0.5962: 996 (41%); 0.6731: 1480 (61%); 0.7949: 1965 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2564, 0.3846, 0.6346, 0.8462 | 0.2564: 1959 (81%); 0.3846: 1467 (60%); 0.6346: 979 (40%); 0.8462: 495 (20%) | 0.2564: 493 (20%); 0.3846: 983 (40%); 0.6346: 1461 (60%); 0.8462: 1949 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0929, -0.0184, 0.0823, 0.2246 | -0.0929: 1952 (80%); -0.0184: 1461 (60%); 0.0823: 984 (40%); 0.2246: 493 (20%) | -0.0929: 495 (20%); -0.0184: 985 (40%); 0.0823: 1461 (60%); 0.2246: 1952 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2564, 0.4487, 0.6154, 0.8205 | 0.2564: 1980 (81%); 0.4487: 1474 (61%); 0.6154: 983 (40%); 0.8205: 490 (20%) | 0.2564: 508 (21%); 0.4487: 1017 (42%); 0.6154: 1470 (60%); 0.8205: 1953 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3077, 0.4744, 0.6667 | 0.1218: 1948 (80%); 0.3077: 1466 (60%); 0.4744: 1002 (41%); 0.6667: 504 (21%) | 0.1218: 488 (20%); 0.3077: 977 (40%); 0.4744: 1461 (60%); 0.6667: 1988 (82%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5017, -0.3562, -0.1909, 0.0839 | -0.5017: 1956 (80%); -0.3562: 1470 (60%); -0.1909: 990 (41%); 0.0839: 505 (21%) | -0.5017: 494 (20%); -0.3562: 984 (40%); -0.1909: 1465 (60%); 0.0839: 1960 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5064, 0.6987, 0.9231 | 0.3397: 1947 (80%); 0.5064: 1462 (60%); 0.6987: 984 (40%); 0.9231: 520 (21%) | 0.3397: 512 (21%); 0.5064: 1002 (41%); 0.6987: 1472 (61%); 0.9231: 1947 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3436, 0.5513, 0.7692 | 0.1218: 1956 (80%); 0.3436: 1460 (60%); 0.5513: 974 (40%); 0.7692: 492 (20%) | 0.1218: 533 (22%); 0.3436: 973 (40%); 0.5513: 1487 (61%); 0.7692: 1960 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0671, -0.0587, -0.0399, 0 | -0.0671: 1952 (80%); -0.0587: 1466 (60%); -0.0399: 985 (40%); 0: 617 (25%) | -0.0671: 490 (20%); -0.0587: 977 (40%); -0.0399: 1468 (60%); 0: 2363 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3718, 0.6987, 0.8846, 0.9936 | 0.3718: 1950 (80%); 0.6987: 1469 (60%); 0.8846: 974 (40%); 0.9936: 576 (24%) | 0.3718: 492 (20%); 0.6987: 984 (40%); 0.8846: 1499 (62%); 0.9936: 1963 (81%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1026, 0.2244, 0.5577, 0.859 | 0.1026: 1968 (81%); 0.2244: 1461 (60%); 0.5577: 983 (40%); 0.859: 497 (20%) | 0.1026: 489 (20%); 0.2244: 977 (40%); 0.5577: 1474 (61%); 0.859: 1954 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0, 0.0373, 0.084, 0.196 | 0: 1956 (80%); 0.0373: 1471 (60%); 0.084: 993 (41%); 0.196: 493 (20%) | 0: 496 (20%); 0.0373: 977 (40%); 0.084: 1502 (62%); 0.196: 1949 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4583, 0.7949, 0.9351, 0.9744 | 0.4583: 1952 (80%); 0.7949: 1466 (60%); 0.9351: 1001 (41%); 0.9744: 563 (23%) | 0.4583: 495 (20%); 0.7949: 976 (40%); 0.9351: 1475 (61%); 0.9744: 1972 (81%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0897, 0.2756, 0.5897, 0.7804 | 0.0897: 1963 (81%); 0.2756: 1466 (60%); 0.5897: 977 (40%); 0.7804: 487 (20%) | 0.0897: 493 (20%); 0.2756: 976 (40%); 0.5897: 1502 (62%); 0.7804: 1946 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0003, 0.1185, 0.2415 | -0.0812: 2134 (88%); -0.0003: 1472 (61%); 0.1185: 980 (40%); 0.2415: 488 (20%) | -0.0812: 552 (23%); -0.0003: 983 (40%); 0.1185: 1462 (60%); 0.2415: 1966 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1695, -0.0157, 0.0442, 0.0905 | -0.1695: 1948 (80%); -0.0157: 1461 (60%); 0.0442: 979 (40%); 0.0905: 487 (20%) | -0.1695: 498 (20%); -0.0157: 988 (41%); 0.0442: 1460 (60%); 0.0905: 1946 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.5513, 0.7436, 0.8782 | 0.3526: 1949 (80%); 0.5513: 1473 (61%); 0.7436: 980 (40%); 0.8782: 500 (21%) | 0.3526: 515 (21%); 0.5513: 997 (41%); 0.7436: 1514 (62%); 0.8782: 2000 (82%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.3782, 0.6026, 0.8269 | 0.1346: 1950 (80%); 0.3782: 1466 (60%); 0.6026: 978 (40%); 0.8269: 496 (20%) | 0.1346: 498 (20%); 0.3782: 1043 (43%); 0.6026: 1471 (60%); 0.8269: 2004 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.055, 0.125, 0.26, 0.5361 | 0.055: 1948 (80%); 0.125: 1463 (60%); 0.26: 978 (40%); 0.5361: 487 (20%) | 0.055: 497 (20%); 0.125: 979 (40%); 0.26: 1464 (60%); 0.5361: 1946 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.8% | 28, 58, 81, 133 | 28: 1934 (79%); 58: 1452 (60%); 81: 963 (40%); 133: 490 (20%) | 28: 488 (20%); 58: 963 (40%); 81: 1457 (60%); 133: 1929 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.5% | 1.7559, 2.2903, 2.87, 3.849 | 1.7559: 1937 (80%); 2.2903: 1453 (60%); 2.87: 969 (40%); 3.849: 485 (20%) | 1.7559: 485 (20%); 2.2903: 969 (40%); 2.87: 1453 (60%); 3.849: 1937 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 15, 23, 35 | 8: 1992 (82%); 15: 1509 (62%); 23: 1023 (42%); 35: 515 (21%) | 8: 543 (22%); 15: 1052 (43%); 23: 1504 (62%); 35: 1980 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 2, 3 | 0: 2433 (100%); 1: 1889 (78%); 2: 1360 (56%); 3: 899 (37%) | 0: 544 (22%); 1: 1073 (44%); 2: 1534 (63%); 3: 1977 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0135, -0.0032, 0.0123, 0.0237 | -0.0135: 1948 (80%); -0.0032: 1473 (61%); 0.0123: 977 (40%); 0.0237: 490 (20%) | -0.0135: 490 (20%); -0.0032: 979 (40%); 0.0123: 1462 (60%); 0.0237: 1948 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5526, 25.8414, 26.4951, 27.2687 | 24.5526: 1962 (81%); 25.8414: 1461 (60%); 26.4951: 976 (40%); 27.2687: 488 (20%) | 24.5526: 507 (21%); 25.8414: 976 (40%); 26.4951: 1469 (60%); 27.2687: 1948 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.7002, -0.224, 0.1354, 0.6206 | -0.7002: 1946 (80%); -0.224: 1461 (60%); 0.1354: 973 (40%); 0.6206: 487 (20%) | -0.7002: 487 (20%); -0.224: 974 (40%); 0.1354: 1460 (60%); 0.6206: 1946 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.6206, -0.1354, 0.224, 0.7002 | -0.6206: 1946 (80%); -0.1354: 1460 (60%); 0.224: 974 (40%); 0.7002: 487 (20%) | -0.6206: 487 (20%); -0.1354: 973 (40%); 0.224: 1461 (60%); 0.7002: 1946 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0456, -0.0097, 0.0203, 0.0588 | -0.0456: 1946 (80%); -0.0097: 1466 (60%); 0.0203: 980 (40%); 0.0588: 490 (20%) | -0.0456: 487 (20%); -0.0097: 974 (40%); 0.0203: 1489 (61%); 0.0588: 1981 (81%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0431, 8.4621, 8.767, 9.1005 | 8.0431: 1946 (80%); 8.4621: 1461 (60%); 8.767: 974 (40%); 9.1005: 488 (20%) | 8.0431: 487 (20%); 8.4621: 972 (40%); 8.767: 1459 (60%); 9.1005: 1945 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 2414 (99%); 1: 736 (30%) | 0: 1678 (69%); 1: 2198 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0 | 0: 1933 (79%) | 0: 2031 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 2414 (99%); 1: 811 (33%) | 0: 1603 (66%); 1: 2162 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 6, 126, 266 | 2: 2093 (86%); 6: 1469 (60%); 126: 974 (40%); 266: 491 (20%) | 2: 492 (20%); 6: 1088 (45%); 126: 1461 (60%); 266: 1951 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 82, 134 | 1: 2002 (82%); 4: 1500 (62%); 82: 977 (40%); 134: 488 (20%) | 1: 636 (26%); 4: 1017 (42%); 82: 1463 (60%); 134: 1952 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.8529, -0.1392, 0.3646, 1.0703 | -0.8529: 1946 (80%); -0.1392: 1460 (60%); 0.3646: 973 (40%); 1.0703: 487 (20%) | -0.8529: 487 (20%); -0.1392: 973 (40%); 0.3646: 1460 (60%); 1.0703: 1946 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.3317, -0.3179, 0.1655, 0.9757 | -1.3317: 1946 (80%); -0.3179: 1460 (60%); 0.1655: 974 (40%); 0.9757: 487 (20%) | -1.3317: 487 (20%); -0.3179: 973 (40%); 0.1655: 1460 (60%); 0.9757: 1946 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.757, -0.51, 0.1669, 1.224 | -1.757: 1946 (80%); -0.51: 1460 (60%); 0.1669: 975 (40%); 1.224: 487 (20%) | -1.757: 487 (20%); -0.51: 974 (40%); 0.1669: 1460 (60%); 1.224: 1946 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.5722, -0.0698, 0.2624, 0.7618 | -0.5722: 1946 (80%); -0.0698: 1460 (60%); 0.2624: 974 (40%); 0.7618: 487 (20%) | -0.5722: 487 (20%); -0.0698: 974 (40%); 0.2624: 1461 (60%); 0.7618: 1946 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.1493, -0.247, 0.2334, 1.004 | -1.1493: 1946 (80%); -0.247: 1460 (60%); 0.2334: 973 (40%); 1.004: 487 (20%) | -1.1493: 487 (20%); -0.247: 974 (40%); 0.2334: 1460 (60%); 1.004: 1946 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.3199, -0.3174, 0.202, 0.9815 | -1.3199: 1946 (80%); -0.3174: 1460 (60%); 0.202: 973 (40%); 0.9815: 487 (20%) | -1.3199: 487 (20%); -0.3174: 973 (40%); 0.202: 1460 (60%); 0.9815: 1946 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 38.582, 48.3, 56.71, 66.322 | 38.582: 1946 (80%); 48.3: 1461 (60%); 56.71: 974 (40%); 66.322: 487 (20%) | 38.582: 487 (20%); 48.3: 974 (40%); 56.71: 1461 (60%); 66.322: 1946 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.7% | 0.0046, 0.0121, 0.0216, 0.0426 | 0.0046: 1936 (80%); 0.0121: 1452 (60%); 0.0216: 972 (40%); 0.0426: 484 (20%) | 0.0046: 489 (20%); 0.0121: 973 (40%); 0.0216: 1453 (60%); 0.0426: 1941 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 8 | 0: 2433 (100%); 2: 1503 (62%); 4: 1033 (42%); 8: 564 (23%) | 0: 569 (23%); 2: 1191 (49%); 4: 1545 (64%); 8: 1950 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1617 | 0: 2433 (100%); 0.1617: 487 (20%) | 0: 1664 (68%); 0.1617: 1946 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667, 0.4091, 0.6667 | 0: 2433 (100%); 0.1667: 1467 (60%); 0.4091: 974 (40%); 0.6667: 506 (21%) | 0: 913 (38%); 0.1667: 984 (40%); 0.4091: 1461 (60%); 0.6667: 2017 (83%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 6 | 0: 2433 (100%); 1: 1725 (71%); 3: 1018 (42%); 6: 551 (23%) | 0: 708 (29%); 1: 1127 (46%); 3: 1610 (66%); 6: 1966 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 8 | 0: 2433 (100%); 2: 1503 (62%); 4: 1033 (42%); 8: 564 (23%) | 0: 569 (23%); 2: 1191 (49%); 4: 1545 (64%); 8: 1950 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 2433 (100%); 1: 1732 (71%); 3: 1101 (45%); 7: 542 (22%) | 0: 701 (29%); 1: 1086 (45%); 3: 1536 (63%); 7: 1972 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.223, 0.3769, 0.5714 | 0: 2238 (92%); 0.223: 1460 (60%); 0.3769: 973 (40%); 0.5714: 491 (20%) | 0: 525 (22%); 0.223: 974 (40%); 0.3769: 1460 (60%); 0.5714: 1953 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1875, 0.5833 | 0: 2203 (91%); 0.1875: 974 (40%); 0.5833: 488 (20%) | 0: 1306 (54%); 0.1875: 1461 (60%); 0.5833: 1948 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3007, 0.5538 | 0: 2227 (92%); 0.3007: 973 (40%); 0.5538: 487 (20%) | 0: 1077 (44%); 0.3007: 1460 (60%); 0.5538: 1946 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3007, 0.5538 | 0: 2227 (92%); 0.3007: 973 (40%); 0.5538: 487 (20%) | 0: 1077 (44%); 0.3007: 1460 (60%); 0.5538: 1946 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1676, 0, 0.1777 | -0.1676: 1946 (80%); 0: 1733 (71%); 0.1777: 488 (20%) | -0.1676: 487 (20%); 0: 1745 (72%); 0.1777: 1947 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7571, -0.2583, 0.1826, 1.4239 | -0.7571: 1953 (80%); -0.2583: 1460 (60%); 0.1826: 975 (40%); 1.4239: 488 (20%) | -0.7571: 489 (20%); -0.2583: 973 (40%); 0.1826: 1462 (60%); 1.4239: 1951 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 2052 (84%); 4: 1574 (65%); 7: 1015 (42%); 11: 491 (20%) | 2: 618 (25%); 4: 1052 (43%); 7: 1565 (64%); 11: 2021 (83%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0402, -0.0067, 0.0286, 0.0672 | -0.0402: 1946 (80%); -0.0067: 1461 (60%); 0.0286: 972 (40%); 0.0672: 487 (20%) | -0.0402: 487 (20%); -0.0067: 972 (40%); 0.0286: 1461 (60%); 0.0672: 1946 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0434, -0.0133, 0.0113, 0.0538 | -0.0434: 1944 (80%); -0.0133: 1456 (60%); 0.0113: 975 (40%); 0.0538: 487 (20%) | -0.0434: 489 (20%); -0.0133: 977 (40%); 0.0113: 1458 (60%); 0.0538: 1946 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.028, -0.0046, 0.0176, 0.0467 | -0.028: 1948 (80%); -0.0046: 1460 (60%); 0.0176: 976 (40%); 0.0467: 487 (20%) | -0.028: 485 (20%); -0.0046: 973 (40%); 0.0176: 1457 (60%); 0.0467: 1946 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 98.4% | 0.0578, 1.8186, 3.2692, 5.5338 | 0.0578: 1914 (79%); 1.8186: 1436 (59%); 3.2692: 957 (39%); 5.5338: 479 (20%) | 0.0578: 479 (20%); 1.8186: 957 (39%); 3.2692: 1436 (59%); 5.5338: 1914 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -18.2198, -6.3516, 4.2774, 22.1874 | -18.2198: 1946 (80%); -6.3516: 1460 (60%); 4.2774: 973 (40%); 22.1874: 487 (20%) | -18.2198: 487 (20%); -6.3516: 973 (40%); 4.2774: 1460 (60%); 22.1874: 1946 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0421, 0.0581, 0.0764, 0.1093 | 0.0421: 1948 (80%); 0.0581: 1462 (60%); 0.0764: 974 (40%); 0.1093: 487 (20%) | 0.0421: 488 (20%); 0.0581: 979 (40%); 0.0764: 1461 (60%); 0.1093: 1948 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1786, 0.342, 0.5117, 0.717 | 0.1786: 1946 (80%); 0.342: 1460 (60%); 0.5117: 974 (40%); 0.717: 487 (20%) | 0.1786: 487 (20%); 0.342: 973 (40%); 0.5117: 1460 (60%); 0.717: 1946 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.3205, -0.4725, 0.2369, 0.9975 | -1.3205: 1946 (80%); -0.4725: 1460 (60%); 0.2369: 973 (40%); 0.9975: 487 (20%) | -1.3205: 487 (20%); -0.4725: 973 (40%); 0.2369: 1460 (60%); 0.9975: 1946 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.7161, -0.2211, 0.6199, 1.1405 | -0.7161: 1947 (80%); -0.2211: 1460 (60%); 0.6199: 973 (40%); 1.1405: 487 (20%) | -0.7161: 487 (20%); -0.2211: 974 (40%); 0.6199: 1460 (60%); 1.1405: 1946 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.8648, -0.7821, 0.2212, 1.207 | -1.8648: 1946 (80%); -0.7821: 1460 (60%); 0.2212: 974 (40%); 1.207: 487 (20%) | -1.8648: 487 (20%); -0.7821: 973 (40%); 0.2212: 1460 (60%); 1.207: 1946 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.1702, -0.7278, 2.8422, 7.0968 | -4.1702: 1946 (80%); -0.7278: 1460 (60%); 2.8422: 973 (40%); 7.0968: 487 (20%) | -4.1702: 487 (20%); -0.7278: 973 (40%); 2.8422: 1460 (60%); 7.0968: 1946 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 26.738, 43.538, 58.412, 76.246 | 26.738: 1946 (80%); 43.538: 1460 (60%); 58.412: 973 (40%); 76.246: 487 (20%) | 26.738: 487 (20%); 43.538: 973 (40%); 58.412: 1460 (60%); 76.246: 1946 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 45.534, 48.178, 51.24, 54.39 | 45.534: 1946 (80%); 48.178: 1460 (60%); 51.24: 975 (40%); 54.39: 488 (20%) | 45.534: 487 (20%); 48.178: 973 (40%); 51.24: 1461 (60%); 54.39: 1947 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 41.042, 48.88, 54.04, 61.248 | 41.042: 1946 (80%); 48.88: 1461 (60%); 54.04: 975 (40%); 61.248: 487 (20%) | 41.042: 487 (20%); 48.88: 974 (40%); 54.04: 1461 (60%); 61.248: 1946 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 2433 (100%) | 0: 2431 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0304, 0.0476, 0.0596, 0.0877 | 0.0304: 1949 (80%); 0.0476: 1464 (60%); 0.0596: 976 (40%); 0.0877: 487 (20%) | 0.0304: 488 (20%); 0.0476: 974 (40%); 0.0596: 1460 (60%); 0.0877: 1946 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0866, -0.0584, -0.044, -0.0346 | -0.0866: 1947 (80%); -0.0584: 1460 (60%); -0.044: 978 (40%); -0.0346: 490 (20%) | -0.0866: 488 (20%); -0.0584: 977 (40%); -0.044: 1464 (60%); -0.0346: 1948 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 2433 (100%); 1: 737 (30%) | 0: 1696 (70%); 1: 1950 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.5% | 25, 40, 56, 69 | 25: 1957 (80%); 40: 1467 (60%); 56: 1016 (42%); 69: 487 (20%) | 25: 516 (21%); 40: 971 (40%); 56: 1467 (60%); 69: 1964 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.6% | 0.0122, 0.0179, 0.0262, 0.0411 | 0.0122: 1920 (79%); 0.0179: 1436 (59%); 0.0262: 959 (39%); 0.0411: 480 (20%) | 0.0122: 480 (20%); 0.0179: 963 (40%); 0.0262: 1440 (59%); 0.0411: 1919 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.29, 0.4105, 0.546, 0.7016 | 0.29: 1946 (80%); 0.4105: 1460 (60%); 0.546: 973 (40%); 0.7016: 488 (20%) | 0.29: 487 (20%); 0.4105: 973 (40%); 0.546: 1460 (60%); 0.7016: 1947 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 38.84, 63, 88.4, 129.16 | 38.84: 1946 (80%); 63: 1461 (60%); 88.4: 975 (40%); 129.16: 487 (20%) | 38.84: 487 (20%); 63: 975 (40%); 88.4: 1462 (60%); 129.16: 1946 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -3.007, -0.3755, 1.076, 3.693 | -3.007: 1946 (80%); -0.3755: 1460 (60%); 1.076: 973 (40%); 3.693: 487 (20%) | -3.007: 487 (20%); -0.3755: 973 (40%); 1.076: 1460 (60%); 3.693: 1946 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 22.548, 43.14, 69.956, 85.748 | 22.548: 1946 (80%); 43.14: 1461 (60%); 69.956: 973 (40%); 85.748: 487 (20%) | 22.548: 487 (20%); 43.14: 974 (40%); 69.956: 1460 (60%); 85.748: 1946 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 20.034, 43.798, 74.412, 87.372 | 20.034: 1946 (80%); 43.798: 1460 (60%); 74.412: 973 (40%); 87.372: 487 (20%) | 20.034: 487 (20%); 43.798: 973 (40%); 74.412: 1460 (60%); 87.372: 1946 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 4.67, 14.19, 93.53, 96.83 | 4.67: 1947 (80%); 14.19: 1461 (60%); 93.53: 974 (40%); 96.83: 488 (20%) | 4.67: 489 (20%); 14.19: 974 (40%); 93.53: 1463 (60%); 96.83: 1947 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 10.056, 18.584, 85.962, 92.26 | 10.056: 1946 (80%); 18.584: 1460 (60%); 85.962: 973 (40%); 92.26: 488 (20%) | 10.056: 487 (20%); 18.584: 973 (40%); 85.962: 1460 (60%); 92.26: 1947 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 17 | 4: 2056 (85%); 8: 1485 (61%); 13: 986 (41%); 17: 497 (20%) | 4: 557 (23%); 8: 1052 (43%); 13: 1557 (64%); 17: 2038 (84%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 18 | 5: 2028 (83%); 9: 1559 (64%); 14: 1033 (42%); 18: 541 (22%) | 5: 514 (21%); 9: 993 (41%); 14: 1493 (61%); 18: 2046 (84%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 43.27, 49.468, 54.432, 60.03 | 43.27: 1947 (80%); 49.468: 1460 (60%); 54.432: 973 (40%); 60.03: 488 (20%) | 43.27: 488 (20%); 49.468: 973 (40%); 54.432: 1460 (60%); 60.03: 1947 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1429, 0.4325, 0.6706, 0.8413 | 0.1429: 1953 (80%); 0.4325: 1463 (60%); 0.6706: 985 (40%); 0.8413: 523 (21%) | 0.1429: 491 (20%); 0.4325: 980 (40%); 0.6706: 1468 (60%); 0.8413: 1950 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.02, 17.21, 20.03, 24.93 | 15.02: 1955 (80%); 17.21: 1465 (60%); 20.03: 977 (40%); 24.93: 489 (20%) | 15.02: 488 (20%); 17.21: 974 (40%); 20.03: 1461 (60%); 24.93: 1952 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.02, 17.21, 20.03, 24.93 | 15.02: 1955 (80%); 17.21: 1465 (60%); 20.03: 977 (40%); 24.93: 489 (20%) | 15.02: 488 (20%); 17.21: 974 (40%); 20.03: 1461 (60%); 24.93: 1952 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8547, 0.8868, 0.921, 0.962 | 0.8547: 1948 (80%); 0.8868: 1494 (61%); 0.921: 982 (40%); 0.962: 491 (20%) | 0.8547: 490 (20%); 0.8868: 975 (40%); 0.921: 1463 (60%); 0.962: 1947 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.67, 0.798, 0.92, 1.12 | 0.67: 1954 (80%); 0.798: 1460 (60%); 0.92: 1000 (41%); 1.12: 506 (21%) | 0.67: 513 (21%); 0.798: 973 (40%); 0.92: 1468 (60%); 1.12: 1948 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0119, 0.03, 0.0554, 0.0921 | 0.0119: 1947 (80%); 0.03: 1462 (60%); 0.0554: 975 (40%); 0.0921: 488 (20%) | 0.0119: 490 (20%); 0.03: 976 (40%); 0.0554: 1461 (60%); 0.0921: 1947 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 46.0286, 77.4882, 120.5161, 209.2934 | 46.0286: 1946 (80%); 77.4882: 1460 (60%); 120.5161: 973 (40%); 209.2934: 487 (20%) | 46.0286: 487 (20%); 77.4882: 973 (40%); 120.5161: 1460 (60%); 209.2934: 1946 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.9496, 75.5043, 116.0824, 203.0044 | 43.9496: 1946 (80%); 75.5043: 1460 (60%); 116.0824: 973 (40%); 203.0044: 487 (20%) | 43.9496: 487 (20%); 75.5043: 973 (40%); 116.0824: 1460 (60%); 203.0044: 1946 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.9583, 72.8544, 112.4708, 194.3603 | 41.9583: 1946 (80%); 72.8544: 1460 (60%); 112.4708: 973 (40%); 194.3603: 487 (20%) | 41.9583: 487 (20%); 72.8544: 973 (40%); 112.4708: 1460 (60%); 194.3603: 1946 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.3602, 80.0754, 123.9748, 214.652 | 47.3602: 1946 (80%); 80.0754: 1460 (60%); 123.9748: 973 (40%); 214.652: 487 (20%) | 47.3602: 487 (20%); 80.0754: 973 (40%); 123.9748: 1460 (60%); 214.652: 1946 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.9021, 82.4254, 127.7654, 220.4011 | 48.9021: 1946 (80%); 82.4254: 1460 (60%); 127.7654: 973 (40%); 220.4011: 487 (20%) | 48.9021: 487 (20%); 82.4254: 973 (40%); 127.7654: 1460 (60%); 220.4011: 1946 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2433 (100%) | 0: 2120 (87%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2433 (100%) | 0: 2150 (88%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0422, -0.0103, 0.0248, 0.0739 | -0.0422: 1947 (80%); -0.0103: 1463 (60%); 0.0248: 974 (40%); 0.0739: 487 (20%) | -0.0422: 487 (20%); -0.0103: 976 (40%); 0.0248: 1460 (60%); 0.0739: 1946 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -77.598, -55.176, -28.306, -16.834 | -77.598: 1946 (80%); -55.176: 1460 (60%); -28.306: 973 (40%); -16.834: 487 (20%) | -77.598: 487 (20%); -55.176: 973 (40%); -28.306: 1460 (60%); -16.834: 1946 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.6% | 0.5644, 0.8347, 1.0571, 1.3391 | 0.5644: 1939 (80%); 0.8347: 1454 (60%); 1.0571: 970 (40%); 1.3391: 485 (20%) | 0.5644: 485 (20%); 0.8347: 969 (40%); 1.0571: 1454 (60%); 1.3391: 1938 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 2017 (83%); 5: 1597 (66%); 7: 1140 (47%); 9: 630 (26%) | 3: 598 (25%); 5: 1050 (43%); 7: 1512 (62%); 9: 2074 (85%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.5% | 0.1911, 0.2313, 0.286, 0.3733 | 0.1911: 1937 (80%); 0.2313: 1455 (60%); 0.286: 969 (40%); 0.3733: 486 (20%) | 0.1911: 485 (20%); 0.2313: 970 (40%); 0.286: 1455 (60%); 0.3733: 1938 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.5% | 3, 5, 8, 9 | 3: 2057 (85%); 5: 1638 (67%); 8: 978 (40%); 9: 705 (29%) | 3: 586 (24%); 5: 988 (41%); 8: 1717 (71%); 9: 2034 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.6% | 0.0233, 0.0327, 0.0433, 0.0604 | 0.0233: 1940 (80%); 0.0327: 1455 (60%); 0.0433: 972 (40%); 0.0604: 485 (20%) | 0.0233: 489 (20%); 0.0327: 970 (40%); 0.0433: 1455 (60%); 0.0604: 1939 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 2026 (83%); 5: 1625 (67%); 7: 1194 (49%); 9: 653 (27%) | 3: 595 (24%); 5: 1006 (41%); 7: 1468 (60%); 9: 2060 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.6% | -0.2222, -0.0691, 0.0596, 0.2506 | -0.2222: 1939 (80%); -0.0691: 1454 (60%); 0.0596: 969 (40%); 0.2506: 485 (20%) | -0.2222: 485 (20%); -0.0691: 970 (40%); 0.0596: 1454 (60%); 0.2506: 1938 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.6% | 2, 4, 6, 9 | 2: 2076 (85%); 4: 1572 (65%); 6: 1090 (45%); 9: 495 (20%) | 2: 612 (25%); 4: 1096 (45%); 6: 1537 (63%); 9: 2160 (89%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.2% |
| 8k_item_5_02_filed_within_7d | 3.3% |
| above_avwap_20high | 31.0% |
| above_avwap_20low | 76.7% |
| above_avwap_252low | 81.8% |
| above_avwap_50low | 80.6% |
| above_cam_r3 | 20.8% |
| above_cam_r4 | 9.0% |
| above_cpr | 48.7% |
| above_pivot | 46.8% |
| above_prev_high | 13.4% |
| above_prev_high_clearance_atr_05 | 1.3% |
| above_prev_low | 83.2% |
| above_r1 | 10.4% |
| above_r2 | 3.1% |
| above_vwap | 47.3% |
| above_wood_p | 51.8% |
| ad_rising | 56.1% |
| adx_cross_up | 1.3% |
| adx_cross_up_20 | 1.8% |
| adx_di_bear | 50.2% |
| adx_di_bull | 49.8% |
| adx_strong | 1.7% |
| adx_trending | 35.5% |
| ao_cross_dn | 2.6% |
| ao_cross_up | 4.3% |
| ao_positive | 48.4% |
| ao_twin_peaks_bull | 3.4% |
| at_key_fib | 22.9% |
| at_key_fib_wide | 53.3% |
| avwap_20high_loss_recent_3d | 19.4% |
| avwap_20high_reclaim_recent_3d | 17.6% |
| avwap_20low_loss_recent_3d | 13.7% |
| avwap_20low_reclaim_recent_3d | 16.8% |
| avwap_252low_loss_recent_3d | 3.4% |
| avwap_252low_reclaim_recent_3d | 6.5% |
| avwap_50low_loss_recent_3d | 9.3% |
| avwap_50low_reclaim_recent_3d | 11.9% |
| bb_10_20_above_mid | 56.6% |
| bb_10_20_expanding | 51.4% |
| bb_10_20_pctb_gt_75 | 29.0% |
| bb_10_20_pctb_gt_8 | 19.3% |
| bb_10_20_pctb_gt_85 | 10.1% |
| bb_10_20_pctb_gt_9 | 3.7% |
| bb_10_20_pctb_gt_95 | 1.3% |
| bb_10_20_pctb_lt_05 | 1.3% |
| bb_10_20_pctb_lt_1 | 3.4% |
| bb_10_20_pctb_lt_15 | 7.6% |
| bb_10_20_pctb_lt_2 | 13.1% |
| bb_10_20_pctb_lt_25 | 19.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 9.9% |
| bb_10_20_reclaim_from_upper_recent_3d | 14.2% |
| bb_10_20_squeeze | 40.7% |
| bb_10_20_touch_lower | 2.5% |
| bb_10_20_touch_upper | 2.2% |
| bb_20_15_above_mid | 56.3% |
| bb_20_15_expanding | 56.3% |
| bb_20_15_pctb_gt_75 | 39.9% |
| bb_20_15_pctb_gt_8 | 36.0% |
| bb_20_15_pctb_gt_85 | 30.9% |
| bb_20_15_pctb_gt_9 | 26.1% |
| bb_20_15_pctb_gt_95 | 21.7% |
| bb_20_15_pctb_lt_05 | 16.4% |
| bb_20_15_pctb_lt_1 | 20.3% |
| bb_20_15_pctb_lt_15 | 24.0% |
| bb_20_15_pctb_lt_2 | 27.0% |
| bb_20_15_pctb_lt_25 | 29.6% |
| bb_20_15_reclaim_from_lower_recent_3d | 10.8% |
| bb_20_15_reclaim_from_upper_recent_3d | 14.3% |
| bb_20_15_squeeze | 43.4% |
| bb_20_15_touch_lower | 18.5% |
| bb_20_15_touch_upper | 22.6% |
| bb_20_20_above_mid | 56.3% |
| bb_20_20_expanding | 56.3% |
| bb_20_20_pctb_gt_75 | 32.5% |
| bb_20_20_pctb_gt_8 | 26.1% |
| bb_20_20_pctb_gt_85 | 20.1% |
| bb_20_20_pctb_gt_9 | 13.3% |
| bb_20_20_pctb_gt_95 | 7.8% |
| bb_20_20_pctb_lt_05 | 6.2% |
| bb_20_20_pctb_lt_1 | 10.4% |
| bb_20_20_pctb_lt_15 | 15.6% |
| bb_20_20_pctb_lt_2 | 20.3% |
| bb_20_20_pctb_lt_25 | 24.8% |
| bb_20_20_reclaim_from_lower_recent_3d | 9.7% |
| bb_20_20_reclaim_from_upper_recent_3d | 13.4% |
| bb_20_20_squeeze | 24.6% |
| bb_20_20_touch_lower | 6.0% |
| bb_20_20_touch_upper | 7.2% |
| bearish_engulfing | 5.2% |
| bearish_pin_bar | 6.8% |
| below_avwap_20high | 69.0% |
| below_avwap_20low | 23.3% |
| below_avwap_252low | 18.2% |
| below_avwap_50low | 19.4% |
| below_cam_s3 | 33.0% |
| below_cam_s4 | 14.9% |
| below_cpr | 53.2% |
| below_ema_20 | 45.6% |
| below_ema_200 | 56.8% |
| below_ema_200_break_recent_5d | 4.9% |
| below_ema_20_break_recent_5d | 28.0% |
| below_ema_21 | 45.7% |
| below_ema_21_break_recent_5d | 28.4% |
| below_ema_50 | 52.0% |
| below_ema_50_break_recent_5d | 17.5% |
| below_ema_9 | 43.8% |
| below_ema_9_break_recent_5d | 25.7% |
| below_prev_high | 86.3% |
| below_prev_low | 16.6% |
| below_prev_low_clearance_atr_05 | 2.0% |
| below_s1 | 15.9% |
| below_s2 | 3.4% |
| below_sma_20 | 43.7% |
| below_sma_200 | 56.4% |
| below_sma_21 | 44.3% |
| below_sma_50 | 52.9% |
| below_sma_9 | 43.6% |
| below_vwap | 52.7% |
| blowoff_recent_3d | 1.1% |
| bullish_engulfing | 2.3% |
| bullish_pin_bar | 7.2% |
| capitulation_recent_3d | 0.4% |
| ceo_buy | 1.0% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 70.2% |
| chandelier_long_flip_dn | 2.6% |
| chandelier_short_bearish | 64.0% |
| chandelier_short_flip_up | 2.7% |
| classification_change_from_tech | 50.0% |
| classification_change_to_defensive | 50.0% |
| close_above_open | 33.6% |
| close_below_open | 64.6% |
| close_in_bottom_40pct_of_range | 46.6% |
| close_in_top_40pct_of_range | 31.0% |
| cluster_buy | 0.6% |
| cmf_cross_dn | 6.0% |
| cmf_cross_up | 4.4% |
| cmf_negative | 44.6% |
| cmf_positive | 55.4% |
| concentrated_sell | 5.3% |
| cpr_narrow | 86.6% |
| cpr_narrow_tight | 25.6% |
| cup_handle_detected | 13.6% |
| cup_handle_neckline_break_retest_long | 1.2% |
| dc10_breakout_dn | 3.8% |
| dc10_breakout_dn_1pct | 11.3% |
| dc10_breakout_up | 4.8% |
| dc10_breakout_up_1pct | 14.5% |
| dc10_new_high | 18.8% |
| dc10_strong_breakout_dn | 0.2% |
| dc10_strong_breakout_up | 0.3% |
| dc20_breakout_dn | 2.3% |
| dc20_breakout_up | 2.8% |
| dc20_new_high | 11.5% |
| dc20_resistance_break_retest_strong | 11.9% |
| dc20_support_break_retest_strong | 8.9% |
| defensive_leadership | 50.4% |
| director_only_buy | 4.0% |
| doji | 8.0% |
| double_bottom_detected | 11.9% |
| double_top_detected | 12.6% |
| dpi_elevated | 55.6% |
| drying_volume_on_down_turn | 45.0% |
| drying_volume_on_up_turn | 23.4% |
| ema_20_50_bearish | 55.9% |
| ema_20_50_bullish | 44.1% |
| ema_20_50_death_cross | 0.8% |
| ema_20_50_golden_cross | 0.9% |
| ema_50_200_bearish | 55.8% |
| ema_50_200_bullish | 44.2% |
| ema_50_200_death_cross | 0.2% |
| ema_9_21_bearish | 50.3% |
| ema_9_21_bullish | 49.7% |
| ema_9_21_death_cross | 2.7% |
| ema_9_21_golden_cross | 3.7% |
| evening_star | 3.7% |
| flag_bear_break_retest_short | 0.1% |
| flag_bear_broke | 0.1% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 0.0% |
| flag_bull_broke | 0.0% |
| flag_bull_detected | 0.5% |
| force_index_cross_dn | 4.3% |
| force_index_cross_up | 2.8% |
| force_index_positive | 54.5% |
| gap_dn_1_5pct | 5.2% |
| gap_dn_2pct | 2.6% |
| gap_up_1_5pct | 7.6% |
| gap_up_2pct | 4.5% |
| hammer | 5.3% |
| head_shoulders_bottom_detected | 3.7% |
| head_shoulders_top_detected | 3.7% |
| house_cluster_buy | 3.6% |
| house_cluster_sell | 3.9% |
| htf_aligned_bear | 28.7% |
| htf_aligned_bull | 20.5% |
| htf_disagreement | 4.6% |
| hull_bearish | 41.6% |
| hull_bullish | 58.4% |
| hull_flip_dn | 1.8% |
| hull_flip_up | 2.7% |
| ichi_above_cloud | 36.3% |
| ichi_above_cloud_break_recent_5d | 8.1% |
| ichi_below_cloud | 45.8% |
| ichi_below_cloud_break_recent_5d | 7.4% |
| ichi_cloud_thick | 86.6% |
| ichi_tk_bearish | 48.4% |
| ichi_tk_bullish | 45.8% |
| ichi_tk_cross_dn | 2.4% |
| ichi_tk_cross_up | 3.3% |
| ichi_weekly_above_cloud | 34.9% |
| ichi_weekly_below_cloud | 35.9% |
| ichi_weekly_in_cloud | 29.2% |
| in_reversal_window | 0.6% |
| inside_bar | 17.6% |
| inside_cpr | 3.0% |
| inside_kc | 93.0% |
| insider_cluster_active | 21.5% |
| institutional_buy | 89.8% |
| institutional_negative | 4.4% |
| institutional_persistence_growing | 44.2% |
| institutional_persistence_strong | 59.7% |
| institutional_strong_buy | 79.6% |
| inverted_cup_handle_detected | 10.6% |
| is_friday | 18.7% |
| is_halloween_period | 50.1% |
| is_halloween_period_first_day | 0.5% |
| is_january | 9.1% |
| is_january_extended | 11.0% |
| is_monday | 22.4% |
| is_pre_holiday | 4.1% |
| is_summer_period | 49.9% |
| is_totm_window | 32.1% |
| is_totm_window_first_day | 8.7% |
| is_week_open | 25.1% |
| kc_touch_lower | 4.2% |
| kc_touch_upper | 5.5% |
| large_dollar_buy | 1.0% |
| macd_12_26_9_bearish | 43.6% |
| macd_12_26_9_bullish | 56.4% |
| macd_12_26_9_crossover_dn | 0.4% |
| macd_12_26_9_crossover_up | 0.5% |
| macd_8_21_5_bearish | 42.3% |
| macd_8_21_5_bullish | 57.7% |
| macd_8_21_5_crossover_dn | 0.6% |
| macd_8_21_5_crossover_up | 1.5% |
| marubozu_bear | 0.2% |
| marubozu_bull | 0.2% |
| mfi_broad_overbought | 13.6% |
| mfi_broad_oversold | 7.4% |
| mfi_overbought | 3.3% |
| mfi_oversold | 1.5% |
| monthly_above_sma_12 | 43.5% |
| monthly_above_sma_6 | 44.0% |
| monthly_bias_bear | 44.7% |
| monthly_bias_bull | 32.2% |
| monthly_momentum_pos | 44.6% |
| morning_star | 2.3% |
| near_52w_high | 0.1% |
| near_52w_high_95pct | 5.5% |
| near_52w_high_retest_long | 0.8% |
| near_52w_low_105pct | 0.9% |
| near_52w_low_retest_short | 1.8% |
| near_avwap_20high_atr_05x | 43.1% |
| near_avwap_20high_atr_10x | 69.3% |
| near_avwap_20high_atr_15x | 86.5% |
| near_avwap_20high_atr_20x | 95.3% |
| near_avwap_20low_atr_05x | 36.6% |
| near_avwap_20low_atr_10x | 60.6% |
| near_avwap_20low_atr_15x | 77.9% |
| near_avwap_20low_atr_20x | 89.1% |
| near_avwap_252low_atr_05x | 10.2% |
| near_avwap_252low_atr_10x | 24.2% |
| near_avwap_252low_atr_15x | 39.2% |
| near_avwap_252low_atr_20x | 51.6% |
| near_avwap_50low_atr_05x | 22.1% |
| near_avwap_50low_atr_10x | 46.3% |
| near_avwap_50low_atr_15x | 68.1% |
| near_avwap_50low_atr_20x | 82.3% |
| near_cam_r3 | 15.8% |
| near_cam_s3 | 21.9% |
| near_cam_s4 | 12.7% |
| near_fib_236 | 6.0% |
| near_fib_382 | 7.6% |
| near_fib_500 | 7.2% |
| near_fib_618 | 8.2% |
| near_fib_786 | 4.5% |
| near_pivot | 22.3% |
| near_prev_close | 22.9% |
| near_prev_high | 11.1% |
| near_prev_low | 13.4% |
| near_r1 | 9.1% |
| near_r1_wide | 55.2% |
| near_r2 | 2.7% |
| near_r2_wide | 24.3% |
| near_s1 | 13.4% |
| near_s1_wide | 62.8% |
| near_s2 | 3.3% |
| near_s2_wide | 28.7% |
| near_s3 | 1.0% |
| near_wood_r1 | 14.3% |
| near_wood_s1 | 11.5% |
| news_uses_polygon_score | 22.7% |
| obv_bearish | 45.2% |
| obv_bullish | 54.8% |
| obv_diverge_bull | 9.7% |
| obv_falling | 44.2% |
| obv_rising | 55.8% |
| outside_bar | 10.4% |
| pead_negative_surprise | 15.6% |
| pead_positive_surprise | 24.5% |
| pin_bar | 14.0% |
| po3_accumulation_active | 30.8% |
| po3_bearish | 17.0% |
| po3_bullish | 8.0% |
| po3_manipulation_sweep_down | 6.8% |
| po3_manipulation_sweep_up | 5.8% |
| po3_mmbm_setup | 1.1% |
| po3_mmsm_setup | 2.3% |
| po3_sweep_above_prior_high | 52.2% |
| po3_sweep_below_prior_low | 47.6% |
| ppo_bullish | 56.3% |
| ppo_crossover_dn | 0.4% |
| ppo_crossover_up | 0.7% |
| pre_fomc_d0 | 2.6% |
| pre_fomc_d1 | 2.9% |
| pre_fomc_window | 5.5% |
| price_above_dema | 56.7% |
| price_above_ema_20 | 54.4% |
| price_above_ema_200 | 43.2% |
| price_above_ema_200_break_recent_5d | 4.6% |
| price_above_ema_20_break_recent_5d | 33.2% |
| price_above_ema_21 | 54.3% |
| price_above_ema_21_break_recent_5d | 33.3% |
| price_above_ema_50 | 48.0% |
| price_above_ema_50_break_recent_5d | 21.2% |
| price_above_ema_9 | 56.2% |
| price_above_ema_9_break_recent_5d | 31.6% |
| price_above_hull | 53.1% |
| price_above_sma_200 | 43.6% |
| price_above_sma_21 | 55.7% |
| price_above_sma_50 | 47.1% |
| price_above_tema | 55.6% |
| price_below_dema | 43.3% |
| price_below_hull | 46.9% |
| price_below_tema | 44.4% |
| psar_bullish | 55.4% |
| psar_flip_dn | 1.2% |
| psar_flip_up | 1.9% |
| r1_break_retest_long | 59.1% |
| resistance_break_retest | 17.3% |
| risk_off_regime_bond_signal | 17.8% |
| risk_off_regime_bond_signal_strong | 6.7% |
| risk_off_regime_gold_signal | 40.4% |
| risk_on_regime_bond_signal | 44.8% |
| risk_on_regime_bond_signal_strong | 19.8% |
| roc_positive | 55.7% |
| roc_turning_dn | 4.5% |
| roc_turning_up | 4.7% |
| rsi_14_bullish | 51.3% |
| rsi_14_cross_dn_overbought_recent_3d | 2.1% |
| rsi_14_cross_up_oversold_recent_3d | 1.4% |
| rsi_14_overbought | 0.8% |
| rsi_14_oversold | 0.5% |
| rsi_14_rising | 41.4% |
| rsi_21_bullish | 48.4% |
| rsi_21_cross_dn_overbought_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 0.1% |
| rsi_21_rising | 41.4% |
| rsi_2_bullish | 50.9% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 40.3% |
| rsi_2_cross_dn_overbought_recent_3d | 40.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 28.4% |
| rsi_2_cross_up_oversold_recent_3d | 30.9% |
| rsi_2_extreme_ob | 16.3% |
| rsi_2_extreme_os | 14.3% |
| rsi_2_overbought | 26.4% |
| rsi_2_oversold | 23.4% |
| rsi_2_rising | 41.3% |
| rsi_9_bullish | 55.4% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.6% |
| rsi_9_cross_dn_overbought_recent_3d | 8.2% |
| rsi_9_cross_up_extreme_os_recent_3d | 1.2% |
| rsi_9_cross_up_oversold_recent_3d | 6.8% |
| rsi_9_extreme_ob | 0.4% |
| rsi_9_extreme_os | 0.2% |
| rsi_9_overbought | 6.2% |
| rsi_9_oversold | 4.8% |
| rsi_9_rising | 41.3% |
| s1_break_retest_short | 45.8% |
| sc_13d_filed_within_30d | 2.7% |
| sc_13g_filed_within_30d | 2.6% |
| sector_outperforming_spy | 37.1% |
| sector_underperforming_spy | 62.9% |
| shooting_star | 4.7% |
| sma_20_50_bullish | 45.1% |
| sma_20_50_golden_cross | 1.0% |
| sma_50_200_bullish | 45.5% |
| sma_50_200_golden_cross | 0.3% |
| sma_9_21_bullish | 52.5% |
| sma_9_21_golden_cross | 5.1% |
| smc_bos_bearish | 9.8% |
| smc_bos_bullish | 10.6% |
| smc_bos_retest_long | 4.2% |
| smc_bos_retest_short | 4.6% |
| smc_breaker_block_bearish | 16.2% |
| smc_breaker_block_bullish | 19.9% |
| smc_choch_bearish | 3.5% |
| smc_choch_bullish | 3.0% |
| smc_equal_highs_swept | 3.2% |
| smc_equal_lows_swept | 4.6% |
| smc_fvg_bearish_active | 32.0% |
| smc_fvg_bullish_active | 43.5% |
| smc_fvg_retest_long_zone | 9.5% |
| smc_fvg_retest_short_zone | 6.2% |
| smc_in_discount_zone | 67.2% |
| smc_in_premium_zone | 61.5% |
| smc_inverse_fvg_bearish | 91.8% |
| smc_inverse_fvg_bullish | 91.8% |
| smc_liquidity_swept_dn | 1.3% |
| smc_liquidity_swept_up | 0.9% |
| smc_mitigation_block_long | 0.5% |
| smc_mitigation_block_short | 0.9% |
| smc_ob_bearish_active | 39.8% |
| smc_ob_bullish_active | 28.9% |
| smc_ote_long_zone | 9.9% |
| smc_ote_short_zone | 7.6% |
| squeeze_fire_dn | 2.0% |
| squeeze_fire_up | 1.6% |
| squeeze_in | 24.7% |
| squeeze_positive | 54.7% |
| stoch_bearish_cross | 14.4% |
| stoch_broad_overbought | 39.4% |
| stoch_broad_oversold | 25.2% |
| stoch_bullish_cross | 10.4% |
| stoch_overbought | 32.8% |
| stoch_oversold | 19.9% |
| stochrsi_cross_dn | 56.8% |
| stochrsi_cross_up | 43.2% |
| stochrsi_overbought | 56.8% |
| stochrsi_oversold | 43.2% |
| supertrend_bearish | 1.0% |
| supertrend_bullish | 99.0% |
| supertrend_flip_recent_long_5d | 1.5% |
| supertrend_flip_recent_short_5d | 1.8% |
| supertrend_flip_up | 0.6% |
| support_break_retest | 14.0% |
| tema_above_dema | 55.6% |
| tema_cross_dn | 1.4% |
| tema_cross_up | 2.3% |
| three_black_crows | 3.2% |
| three_white_soldiers | 3.0% |
| triangle_apex_break_retest_long | 7.6% |
| triangle_ascending_detected | 11.4% |
| triangle_descending_detected | 11.7% |
| uo_overbought | 1.2% |
| uo_oversold | 0.9% |
| usd_strengthening | 26.4% |
| usd_weakening | 10.1% |
| vix_band_high | 40.7% |
| vix_band_low | 33.8% |
| vix_band_mid | 25.4% |
| vix_term_backwardation | 5.2% |
| vix_term_contango | 94.8% |
| vol_above_avg | 30.2% |
| vol_below_avg | 69.8% |
| vol_spike_12x | 15.2% |
| vol_spike_15x | 6.3% |
| vol_spike_17x | 3.2% |
| vol_spike_2x | 1.4% |
| vol_spike_2x_on_down_day_recent_3d | 3.7% |
| vol_spike_2x_on_up_day_recent_3d | 3.2% |
| vol_spike_3x | 0.1% |
| vp_above_value_area | 12.4% |
| vp_below_value_area | 7.9% |
| vp_close_above_poc | 53.7% |
| vp_close_below_poc | 46.3% |
| vp_in_value_area | 79.7% |
| week_open_gap_down_15pct | 1.7% |
| week_open_gap_up_15pct | 1.5% |
| weekly_above_ema_10 | 48.1% |
| weekly_above_ema_20 | 44.6% |
| weekly_bias_bear | 41.1% |
| weekly_bias_bull | 33.8% |
| weekly_momentum_pos | 53.6% |
| williams_r_overbought | 25.4% |
| williams_r_oversold | 17.1% |
| williams_r_rising | 41.1% |
| within_pead_window | 41.0% |
| within_post_deletion_window | 3.0% |
| within_post_inclusion_window | 1.6% |
| within_pre_rebalance_window | 0.8% |
| xs_avoid_high_ivol | 70.9% |
| xs_avoid_high_max | 73.0% |
| xs_high_beta_decile | 26.0% |
| xs_low_beta_bottom_quintile | 26.0% |
| xs_low_beta_decile | 16.8% |
| xs_low_beta_decile_entry_recent_5d | 0.7% |
| xs_low_beta_top_quintile | 16.8% |
| xs_momentum_bottom_decile | 14.3% |
| xs_momentum_bottom_quintile | 25.3% |
| xs_momentum_top_decile | 10.9% |
| xs_momentum_top_quintile | 20.4% |
| xs_quality_bottom_quintile | 21.4% |
| xs_quality_top_quintile | 21.7% |
| xs_quality_top_tercile | 40.8% |
| yoy_surprise_high | 53.7% |
| yoy_surprise_negative | 35.6% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.3% |
| committed_growth_holders | 91.3% |
| corp_donations_1y | 8.4% |
| corp_donations_count_1y | 8.4% |
| corp_donations_unique_pacs | 8.4% |
| cot_rut_commercials_pctile_3y | 51.7% |
| cot_rut_mmoney_pctile_3y | 51.7% |
| cup_handle_depth_pct | 17.2% |
| days_since_deletion | 8.1% |
| days_since_inclusion | 12.7% |
| days_to_next_holiday | 62.6% |
| days_to_rebalance | 10.8% |
| dpi_30d_avg | 96.1% |
| dpi_recent | 96.1% |
| earnings_announcement_return | 92.1% |
| earnings_eps_yoy_growth | 95.0% |
| flag_bear_pole_move_pct | 0.2% |
| flag_bull_pole_move_pct | 0.5% |
| gov_contracts_4q_sum | 39.7% |
| gov_contracts_last_qtr_amount | 39.7% |
| gov_contracts_qoq_growth | 39.7% |
| head_shoulders_magnitude_pct | 7.1% |
| insider_director_buyers_30d | 5.9% |
| insider_officer_buyers_30d | 5.9% |
| insider_total_shares_bought_30d | 5.9% |
| insider_unique_buyers_30d | 5.9% |
| inverted_cup_handle_height_pct | 14.0% |
| lobbying_amount_1y | 69.8% |
| lobbying_amount_q | 69.8% |
| lobbying_amount_yoy | 69.8% |
| monthly_momentum_6m | 97.5% |
| otc_short_ratio_recent | 96.1% |
| otc_volume_recent | 96.1% |
| pair_half_life | 92.1% |
| pair_max_abs_zscore | 92.1% |
| pair_zscore_signed | 92.1% |
| pct_from_avwap_20high | 87.9% |
| pct_from_avwap_20low | 92.4% |
| pct_from_avwap_252low | 97.8% |
| persistent_holders_4q | 91.3% |
| persistent_holders_8q | 91.3% |
| sc_13g_latest_percent_owned | 1.1% |
| search_volume_index_recent | 76.1% |
| search_volume_observations | 76.1% |
| search_volume_zscore_30d | 76.1% |
| sector_etf_return_20d | 2.5% |
| spy_return_20d | 2.5% |
| total_active_holders | 91.3% |
| triangle_breakdown_pct | 11.7% |
| triangle_breakout_pct | 11.4% |
| xs_quality_decile | 62.2% |
| xs_quality_gross_profitability | 62.2% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (1.0), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.997), `days_since_classification_change` (1.0), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (1.0), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.999), `double_top_neckline` (0.996), `double_top_peak` (0.996), `entry_stop_long` (0.998), `entry_stop_short` (0.998), `fib_236` (0.996), `fib_382` (0.997), `fib_500` (0.997), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.992), `fib_ext_162` (0.99), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.994), `ichi_senkou_b` (0.989), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.999), `monthly_sma_12` (0.979), `monthly_sma_6` (0.993), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.999), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.998), `s2` (0.998), `s3` (0.998), `supertrend_value` (0.997), `swing_high` (0.995), `swing_low` (0.997), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.996), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.995), `wood_p` (0.998), `wood_r1` (0.999), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.965), `year_low` (0.967)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | **YES** |
| P2.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | **YES** |
| P3.1 | rsi (fast escape-hatch) span | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | cross guard band (k > 20 on cross_dn) | 2 | subset-safe | no - derives offline |
| P5.1 | cross guard band (k < 80 on cross_up) | 2 | subset-safe | no - derives offline |
| P6.1 | overbought threshold on k | 4 | subset-safe | no - derives offline |
| P6.2 | period (rsi+stoch length) | 3 | **FIRE-ADDING** | **YES** |
| P7.1 | period (rsi+stoch length) | 3 | **FIRE-ADDING** | **YES** |
| P7.2 | oversold threshold on k | 4 | subset-safe | no - derives offline |
| P8 | rsi_14 < 55 | 4 | subset-safe | no - derives offline |
| P9 | rsi_14 > 45 | 5 | subset-safe | no - derives offline |
| P10 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     3 x 3 x 1 x 2 x 2 x 4 x 3 x 3 x 4 x 4 x 5 x 1 = 103680
offline gradings   1280 level-combinations x 24 exits = 30720
ENGINE RUNS        81 (every fire-adding axis sits at production-only until its env actuator exists)
check              81 x 1280 = 103680
```

B-row candidates NOT in this factorial: 636 census axes join it only when REGISTERED at the T3 band review.
