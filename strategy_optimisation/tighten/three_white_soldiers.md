# Table A - three_white_soldiers

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:05:47 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** candle | **status:** NOT-STARTED | **R5 fires:** 1596 | **surviving fires (T1):** 1596 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  three_white_soldiers  <- backtest/signals/screener.py +2
       DEFN: 3 consecutive bullish bodies, each close AND open above the prior bar's (strict; technical.py:2104-2107)
       knobs P1.1-P1.4 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  rsi_14 < 60   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_three_white_soldiers (docstring and return dropped):

```python
fires = s.get('three_white_soldiers') and s.get('rsi_14', 50) < 60
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
| P1 | PRODUCER | three_white_soldiers - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | 3 consecutive bullish bodies, each close AND open above the prior bar's (strict; technical.py:2104-2107) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P1.1 | BAND | n_bars (pattern length) - backtest/signals/technical.py:2104-2107 | CANON (Nison 1991: three); 4 as the strict extension | 3 | 3, 4 | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P1.2 | BAND | min_body_pct_of_range per candle - technical.py:2105 (c>o only - no magnitude) | CANON (Nison long-body soldiers); production accepts ANY body | 0.0 | 0, 0.3, 0.5 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P1.3 | BAND | min_step_up_pct (close[i] above close[i-1] by) - technical.py:2106 | BRACKET zero upward; strict > today | 0.0 | 0, 0.1, 0.25 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P1.4 | BAND | max_upper_wick_pct (close near high) - technical.py:2104-2107 (absent today) | CANON (soldiers close at/near highs); production unenforced | None | None, 0.3, 0.2 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | STRATEGY | rsi_14 `< 60` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 60` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P2.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 60` | 100.0% | TIGHTER = LOWER the ceiling: 41.97 -> 320 (20%); 46.31 -> 641 (40%); 50.16 -> 960 (60%); 54.42 -> 1277 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 17.2, 21.56, 26.55, 34.2 | 17.2: 1277 (80%); 21.56: 958 (60%); 26.55: 639 (40%); 34.2: 320 (20%) | 17.2: 320 (20%); 21.56: 639 (40%); 26.55: 958 (60%); 34.2: 1277 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 21.8, 24.51, 27.18, 30.91 | 21.8: 1278 (80%); 24.51: 960 (60%); 27.18: 640 (40%); 30.91: 320 (20%) | 21.8: 320 (20%); 24.51: 640 (40%); 27.18: 958 (60%); 30.91: 1277 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 17.24, 20.5, 23.19, 26.4 | 17.24: 1279 (80%); 20.5: 958 (60%); 23.19: 640 (40%); 26.4: 325 (20%) | 17.24: 320 (20%); 20.5: 639 (40%); 23.19: 959 (60%); 26.4: 1277 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -8.9458, -4.5814, -2.2881, -0.7075 | -8.9458: 1277 (80%); -4.5814: 958 (60%); -2.2881: 639 (40%); -0.7075: 320 (20%) | -8.9458: 320 (20%); -4.5814: 639 (40%); -2.2881: 958 (60%); -0.7075: 1277 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.1086, 1.9174, 3.1125, 5.2045 | 1.1086: 1277 (80%); 1.9174: 958 (60%); 3.1125: 639 (40%); 5.2045: 320 (20%) | 1.1086: 320 (20%); 1.9174: 639 (40%); 3.1125: 958 (60%); 5.2045: 1277 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.1086, 1.9174, 3.1125, 5.2045 | 1.1086: 1277 (80%); 1.9174: 958 (60%); 3.1125: 639 (40%); 5.2045: 320 (20%) | 1.1086: 320 (20%); 1.9174: 639 (40%); 3.1125: 958 (60%); 5.2045: 1277 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.185, 2.643, 3.18, 4.042 | 2.185: 1277 (80%); 2.643: 959 (60%); 3.18: 639 (40%); 4.042: 320 (20%) | 2.185: 321 (20%); 2.643: 639 (40%); 3.18: 958 (60%); 4.042: 1278 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0582, 0.08, 0.1085, 0.1526 | 0.0582: 1278 (80%); 0.08: 959 (60%); 0.1085: 639 (40%); 0.1526: 320 (20%) | 0.0582: 320 (20%); 0.08: 640 (40%); 0.1085: 958 (60%); 0.1526: 1277 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.5115, 0.7109, 0.8342, 0.9257 | 0.5115: 1277 (80%); 0.7109: 958 (60%); 0.8342: 639 (40%); 0.9257: 320 (20%) | 0.5115: 320 (20%); 0.7109: 639 (40%); 0.8342: 958 (60%); 0.9257: 1277 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0647, 0.0923, 0.1237, 0.1726 | 0.0647: 1278 (80%); 0.0923: 959 (60%); 0.1237: 640 (40%); 0.1726: 321 (20%) | 0.0647: 321 (20%); 0.0923: 639 (40%); 0.1237: 960 (60%); 0.1726: 1277 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.2998, 0.4228, 0.5976, 0.8742 | 0.2998: 1277 (80%); 0.4228: 958 (60%); 0.5976: 639 (40%); 0.8742: 320 (20%) | 0.2998: 320 (20%); 0.4228: 639 (40%); 0.5976: 958 (60%); 0.8742: 1278 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0862, 0.1231, 0.1649, 0.2301 | 0.0862: 1278 (80%); 0.1231: 958 (60%); 0.1649: 640 (40%); 0.2301: 321 (20%) | 0.0862: 320 (20%); 0.1231: 639 (40%); 0.1649: 960 (60%); 0.2301: 1277 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.3498, 0.4421, 0.5732, 0.7806 | 0.3498: 1277 (80%); 0.4421: 958 (60%); 0.5732: 639 (40%); 0.7806: 321 (20%) | 0.3498: 320 (20%); 0.4421: 639 (40%); 0.5732: 958 (60%); 0.7806: 1277 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0472, -0.0224, -0.0048, 0.0242 | -0.0472: 1282 (80%); -0.0224: 960 (60%); -0.0048: 641 (40%); 0.0242: 327 (20%) | -0.0472: 323 (20%); -0.0224: 639 (40%); -0.0048: 958 (60%); 0.0242: 1277 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1451, 0.1736, 0.2439, 0.272 | 0.1451: 1276 (80%); 0.1736: 958 (60%); 0.2439: 636 (40%); 0.272: 319 (20%) | 0.1451: 320 (20%); 0.1736: 638 (40%); 0.2439: 960 (60%); 0.272: 1277 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1596 (100%) | 0: 1486 (93%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1079, -0.0286, 0.042, 0.11 | -0.1079: 1277 (80%); -0.0286: 959 (60%); 0.042: 639 (40%); 0.11: 320 (20%) | -0.1079: 320 (20%); -0.0286: 639 (40%); 0.042: 958 (60%); 0.11: 1277 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1596 (100%); 1: 626 (39%) | 0: 970 (61%); 1: 1338 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2368, -0.1753, -0.1388, -0.1063 | -0.2368: 1278 (80%); -0.1753: 960 (60%); -0.1388: 645 (40%); -0.1063: 337 (21%) | -0.2368: 320 (20%); -0.1753: 641 (40%); -0.1388: 965 (60%); -0.1063: 1290 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4231, 0.641, 0.7372, 0.8013 | 0.4231: 1283 (80%); 0.641: 959 (60%); 0.7372: 667 (42%); 0.8013: 340 (21%) | 0.4231: 331 (21%); 0.641: 657 (41%); 0.7372: 1002 (63%); 0.8013: 1296 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.25, 0.3077, 0.5192, 0.7949 | 0.25: 1293 (81%); 0.3077: 991 (62%); 0.5192: 646 (40%); 0.7949: 333 (21%) | 0.25: 326 (20%); 0.3077: 678 (42%); 0.5192: 968 (61%); 0.7949: 1277 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0556, 0.0195, 0.1092, 0.3218 | -0.0556: 1278 (80%); 0.0195: 959 (60%); 0.1092: 639 (40%); 0.3218: 375 (23%) | -0.0556: 326 (20%); 0.0195: 649 (41%); 0.1092: 970 (61%); 0.3218: 1283 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5, 0.6923, 0.9295 | 0.3397: 1281 (80%); 0.5: 965 (60%); 0.6923: 645 (40%); 0.9295: 333 (21%) | 0.3397: 322 (20%); 0.5: 649 (41%); 0.6923: 959 (60%); 0.9295: 1278 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.2949, 0.4679, 0.5897 | 0.109: 1294 (81%); 0.2949: 987 (62%); 0.4679: 641 (40%); 0.5897: 321 (20%) | 0.109: 329 (21%); 0.2949: 643 (40%); 0.4679: 965 (60%); 0.5897: 1279 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5724, -0.4529, -0.2595, 0.0045 | -0.5724: 1285 (81%); -0.4529: 961 (60%); -0.2595: 644 (40%); 0.0045: 330 (21%) | -0.5724: 321 (20%); -0.4529: 681 (43%); -0.2595: 958 (60%); 0.0045: 1280 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4679, 0.5897, 0.9167 | 0.2692: 1324 (83%); 0.4679: 987 (62%); 0.5897: 649 (41%); 0.9167: 335 (21%) | 0.2692: 324 (20%); 0.4679: 672 (42%); 0.5897: 963 (60%); 0.9167: 1322 (83%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3205, 0.5513, 0.7628 | 0.1218: 1278 (80%); 0.3205: 966 (61%); 0.5513: 643 (40%); 0.7628: 326 (20%) | 0.1218: 341 (21%); 0.3205: 639 (40%); 0.5513: 964 (60%); 0.7628: 1295 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0681, -0.0605, -0.0419, 0 | -0.0681: 1285 (81%); -0.0605: 972 (61%); -0.0419: 646 (40%); 0: 411 (26%) | -0.0681: 373 (23%); -0.0605: 649 (41%); -0.0419: 961 (60%); 0: 1555 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4423, 0.7308, 0.8846, 0.9936 | 0.4423: 1279 (80%); 0.7308: 959 (60%); 0.8846: 737 (46%); 0.9936: 393 (25%) | 0.4423: 325 (20%); 0.7308: 648 (41%); 0.8846: 980 (61%); 0.9936: 1287 (81%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0833, 0.1923, 0.4744, 0.7885 | 0.0833: 1325 (83%); 0.1923: 983 (62%); 0.4744: 650 (41%); 0.7885: 321 (20%) | 0.0833: 353 (22%); 0.1923: 703 (44%); 0.4744: 961 (60%); 0.7885: 1283 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0092, 0.0383, 0.0706, 0.1835 | 0.0092: 1294 (81%); 0.0383: 985 (62%); 0.0706: 655 (41%); 0.1835: 329 (21%) | 0.0092: 348 (22%); 0.0383: 679 (43%); 0.0706: 969 (61%); 0.1835: 1281 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.6144, 0.7821, 0.9359, 0.9744 | 0.6144: 1289 (81%); 0.7821: 961 (60%); 0.9359: 641 (40%); 0.9744: 373 (23%) | 0.6144: 322 (20%); 0.7821: 644 (40%); 0.9359: 960 (60%); 0.9744: 1296 (81%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0947, 0.2278, 0.6346, 0.8372 | 0.0947: 1288 (81%); 0.2278: 972 (61%); 0.6346: 641 (40%); 0.8372: 347 (22%) | 0.0947: 363 (23%); 0.2278: 639 (40%); 0.6346: 958 (60%); 0.8372: 1297 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0651, 0.0566, 0.1225, 0.3175 | -0.0651: 1278 (80%); 0.0566: 1014 (64%); 0.1225: 711 (45%); 0.3175: 369 (23%) | -0.0651: 322 (20%); 0.0566: 674 (42%); 0.1225: 990 (62%); 0.3175: 1542 (97%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1523, 0.0073, 0.0457, 0.0916 | -0.1523: 1282 (80%); 0.0073: 961 (60%); 0.0457: 640 (40%); 0.0916: 329 (21%) | -0.1523: 325 (20%); 0.0073: 649 (41%); 0.0457: 963 (60%); 0.0916: 1281 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5897, 0.7372, 0.8782 | 0.3397: 1277 (80%); 0.5897: 967 (61%); 0.7372: 691 (43%); 0.8782: 334 (21%) | 0.3397: 337 (21%); 0.5897: 645 (40%); 0.7372: 974 (61%); 0.8782: 1287 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3333, 0.5577, 0.7821 | 0.1218: 1309 (82%); 0.3333: 963 (60%); 0.5577: 641 (40%); 0.7821: 332 (21%) | 0.1218: 335 (21%); 0.3333: 642 (40%); 0.5577: 982 (62%); 0.7821: 1294 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.055, 0.1242, 0.2317, 0.4417 | 0.055: 1281 (80%); 0.1242: 959 (60%); 0.2317: 640 (40%); 0.4417: 321 (20%) | 0.055: 324 (20%); 0.1242: 643 (40%); 0.2317: 961 (60%); 0.4417: 1278 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.6% | 29, 62, 81, 137.4 | 29: 1272 (80%); 62: 961 (60%); 81: 638 (40%); 137.4: 315 (20%) | 29: 316 (20%); 62: 649 (41%); 81: 949 (59%); 137.4: 1259 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.7094, 2.2642, 2.8795, 4.0135 | 1.7094: 1272 (80%); 2.2642: 954 (60%); 2.8795: 636 (40%); 4.0135: 318 (20%) | 1.7094: 318 (20%); 2.2642: 636 (40%); 2.8795: 954 (60%); 4.0135: 1272 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 9, 19, 26, 33 | 9: 1311 (82%); 19: 1015 (64%); 26: 664 (42%); 33: 381 (24%) | 9: 351 (22%); 19: 657 (41%); 26: 964 (60%); 33: 1286 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 4 | 1: 1291 (81%); 2: 903 (57%); 4: 336 (21%) | 1: 693 (43%); 2: 967 (61%); 4: 1596 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0149, -0.0021, 0.0138, 0.0227 | -0.0149: 1277 (80%); -0.0021: 961 (60%); 0.0138: 639 (40%); 0.0227: 322 (20%) | -0.0149: 364 (23%); -0.0021: 645 (40%); 0.0138: 964 (60%); 0.0227: 1284 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.3774, 25.3862, 26.3225, 27.1043 | 24.3774: 1279 (80%); 25.3862: 962 (60%); 26.3225: 640 (40%); 27.1043: 320 (20%) | 24.3774: 322 (20%); 25.3862: 639 (40%); 26.3225: 958 (60%); 27.1043: 1278 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.687, -0.271, 0, 0.323 | -0.687: 1278 (80%); -0.271: 958 (60%); 0: 682 (43%); 0.323: 321 (20%) | -0.687: 320 (20%); -0.271: 639 (40%); 0: 975 (61%); 0.323: 1278 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.323, 0, 0.271, 0.687 | -0.323: 1278 (80%); 0: 975 (61%); 0.271: 639 (40%); 0.687: 320 (20%) | -0.323: 321 (20%); 0: 682 (43%); 0.271: 958 (60%); 0.687: 1278 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0383, 0.0029, 0.0248, 0.0607 | -0.0383: 1277 (80%); 0.0029: 958 (60%); 0.0248: 643 (40%); 0.0607: 321 (20%) | -0.0383: 320 (20%); 0.0029: 640 (40%); 0.0248: 976 (61%); 0.0607: 1282 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.074, 8.5182, 8.76, 9.1063 | 8.074: 1277 (80%); 8.5182: 960 (60%); 8.76: 636 (40%); 9.1063: 315 (20%) | 8.074: 319 (20%); 8.5182: 636 (40%); 8.76: 960 (60%); 9.1063: 1281 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 98.9% | 0, 1 | 0: 1579 (99%); 1: 471 (30%) | 0: 1108 (69%); 1: 1438 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 98.9% | -1, 0 | -1: 1494 (94%); 0: 1254 (79%) | -1: 325 (20%); 0: 1341 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 98.9% | 0, 1 | 0: 1579 (99%); 1: 543 (34%) | 0: 1036 (65%); 1: 1393 (87%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 6, 116, 257 | 3: 1298 (81%); 6: 973 (61%); 116: 642 (40%); 257: 321 (20%) | 3: 413 (26%); 6: 707 (44%); 116: 958 (60%); 257: 1277 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 3, 76, 126 | 0: 1596 (100%); 3: 1020 (64%); 76: 641 (40%); 126: 324 (20%) | 0: 331 (21%); 3: 650 (41%); 76: 966 (61%); 126: 1278 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.281, 0.0134, 0.2136, 0.6173 | -0.281: 1277 (80%); 0.0134: 959 (60%); 0.2136: 639 (40%); 0.6173: 320 (20%) | -0.281: 320 (20%); 0.0134: 639 (40%); 0.2136: 958 (60%); 0.6173: 1277 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -3.3793, -1.7882, -0.9003, -0.3575 | -3.3793: 1277 (80%); -1.7882: 958 (60%); -0.9003: 639 (40%); -0.3575: 320 (20%) | -3.3793: 320 (20%); -1.7882: 639 (40%); -0.9003: 958 (60%); -0.3575: 1277 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -3.7268, -1.9025, -1.0554, -0.464 | -3.7268: 1277 (80%); -1.9025: 958 (60%); -1.0554: 639 (40%); -0.464: 320 (20%) | -3.7268: 320 (20%); -1.9025: 639 (40%); -1.0554: 958 (60%); -0.464: 1277 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | 0.0298, 0.2039, 0.4403, 0.8926 | 0.0298: 1278 (80%); 0.2039: 958 (60%); 0.4403: 639 (40%); 0.8926: 320 (20%) | 0.0298: 320 (20%); 0.2039: 639 (40%); 0.4403: 958 (60%); 0.8926: 1277 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -3.1067, -1.5184, -0.6744, -0.1539 | -3.1067: 1277 (80%); -1.5184: 958 (60%); -0.6744: 639 (40%); -0.1539: 320 (20%) | -3.1067: 320 (20%); -1.5184: 639 (40%); -0.6744: 958 (60%); -0.1539: 1277 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -3.7329, -1.9469, -1.0137, -0.3827 | -3.7329: 1277 (80%); -1.9469: 958 (60%); -1.0137: 639 (40%); -0.3827: 320 (20%) | -3.7329: 320 (20%); -1.9469: 639 (40%); -1.0137: 958 (60%); -0.3827: 1277 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 35.88, 44.24, 50.72, 58.95 | 35.88: 1277 (80%); 44.24: 958 (60%); 50.72: 639 (40%); 58.95: 320 (20%) | 35.88: 320 (20%); 44.24: 639 (40%); 50.72: 958 (60%); 58.95: 1277 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 98.5% | -0.2257, -0.1462, -0.0741, 0.0021 | -0.2257: 1259 (79%); -0.1462: 943 (59%); -0.0741: 629 (39%); 0.0021: 315 (20%) | -0.2257: 315 (20%); -0.1462: 629 (39%); -0.0741: 943 (59%); 0.0021: 1257 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.1% | 0.0058, 0.0133, 0.0256, 0.0472 | 0.0058: 1266 (79%); 0.0133: 946 (59%); 0.0256: 632 (40%); 0.0472: 315 (20%) | 0.0058: 315 (20%); 0.0133: 635 (40%); 0.0256: 949 (59%); 0.0472: 1266 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 8 | 0: 1596 (100%); 2: 979 (61%); 4: 672 (42%); 8: 361 (23%) | 0: 390 (24%); 2: 795 (50%); 4: 1036 (65%); 8: 1286 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2 | 0: 1596 (100%); 0.2: 342 (21%) | 0: 1037 (65%); 0.2: 1293 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.5 | 0: 1596 (100%); 0.3333: 716 (45%); 0.5: 456 (29%) | 0: 647 (41%); 0.3333: 974 (61%); 0.5: 1282 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 6 | 0: 1596 (100%); 1: 1101 (69%); 2: 838 (53%); 6: 342 (21%) | 0: 495 (31%); 1: 758 (47%); 2: 958 (60%); 6: 1316 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 8 | 0: 1596 (100%); 2: 979 (61%); 4: 672 (42%); 8: 361 (23%) | 0: 390 (24%); 2: 795 (50%); 4: 1036 (65%); 8: 1286 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1596 (100%); 1: 1154 (72%); 3: 702 (44%); 7: 330 (21%) | 0: 442 (28%); 1: 707 (44%); 3: 1028 (64%); 7: 1312 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1562, 0.3, 0.5 | 0: 1424 (89%); 0.1562: 959 (60%); 0.3: 641 (40%); 0.5: 334 (21%) | 0: 413 (26%); 0.1562: 640 (40%); 0.3: 963 (60%); 0.5: 1316 (82%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.0969, 0.4615 | 0: 1428 (89%); 0.0969: 639 (40%); 0.4615: 320 (20%) | 0: 918 (58%); 0.0969: 958 (60%); 0.4615: 1278 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2, 0.5 | 0: 1409 (88%); 0.2: 651 (41%); 0.5: 333 (21%) | 0: 790 (49%); 0.2: 963 (60%); 0.5: 1342 (84%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.5 | 0: 1409 (88%); 0.2: 651 (41%); 0.5: 333 (21%) | 0: 790 (49%); 0.2: 963 (60%); 0.5: 1342 (84%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1667, 0, 0.1667 | -0.1667: 1279 (80%); 0: 1125 (70%); 0.1667: 336 (21%) | -0.1667: 340 (21%); 0: 1145 (72%); 0.1667: 1278 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7746, -0.369, 0, 1.0528 | -0.7746: 1279 (80%); -0.369: 959 (60%); 0: 830 (52%); 1.0528: 320 (20%) | -0.7746: 321 (20%); -0.369: 639 (40%); 0: 975 (61%); 1.0528: 1277 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 1346 (84%); 4: 1021 (64%); 7: 648 (41%); 11: 324 (20%) | 2: 415 (26%); 4: 708 (44%); 7: 1052 (66%); 11: 1313 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0391, -0.011, 0.0133, 0.0422 | -0.0391: 1277 (80%); -0.011: 958 (60%); 0.0133: 639 (40%); 0.0422: 320 (20%) | -0.0391: 319 (20%); -0.011: 638 (40%); 0.0133: 957 (60%); 0.0422: 1276 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0886, -0.0483, -0.0187, 0.0156 | -0.0886: 1278 (80%); -0.0483: 956 (60%); -0.0187: 639 (40%); 0.0156: 319 (20%) | -0.0886: 318 (20%); -0.0483: 640 (40%); -0.0187: 957 (60%); 0.0156: 1277 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | 0.0029, 0.0201, 0.0372, 0.0619 | 0.0029: 1277 (80%); 0.0201: 957 (60%); 0.0372: 640 (40%); 0.0619: 319 (20%) | 0.0029: 319 (20%); 0.0201: 639 (40%); 0.0372: 956 (60%); 0.0619: 1277 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 99.8% | 1.5964, 2.424, 3.4096, 5.1438 | 1.5964: 1274 (80%); 2.424: 957 (60%); 3.4096: 637 (40%); 5.1438: 319 (20%) | 1.5964: 319 (20%); 2.424: 638 (40%); 3.4096: 956 (60%); 5.1438: 1274 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 98.8% | -3.3826, 0.7072, 2.625, 4.924 | -3.3826: 1261 (79%); 0.7072: 946 (59%); 2.625: 631 (40%); 4.924: 316 (20%) | -3.3826: 316 (20%); 0.7072: 631 (40%); 2.625: 946 (59%); 4.924: 1261 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 99.7% | 1.375, 2.2894, 3.375, 5.1296 | 1.375: 1274 (80%); 2.2894: 955 (60%); 3.375: 637 (40%); 5.1296: 319 (20%) | 1.375: 320 (20%); 2.2894: 637 (40%); 3.375: 955 (60%); 5.1296: 1273 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -27.165, -15.267, -6.781, 2.882 | -27.165: 1277 (80%); -15.267: 958 (60%); -6.781: 639 (40%); 2.882: 320 (20%) | -27.165: 320 (20%); -15.267: 639 (40%); -6.781: 958 (60%); 2.882: 1277 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0437, 0.0571, 0.0747, 0.1002 | 0.0437: 1282 (80%); 0.0571: 959 (60%); 0.0747: 639 (40%); 0.1002: 320 (20%) | 0.0437: 320 (20%); 0.0571: 639 (40%); 0.0747: 959 (60%); 0.1002: 1277 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5263, 0.6967, 0.8208, 0.9194 | 0.5263: 1278 (80%); 0.6967: 958 (60%); 0.8208: 640 (40%); 0.9194: 320 (20%) | 0.5263: 320 (20%); 0.6967: 639 (40%); 0.8208: 958 (60%); 0.9194: 1277 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -3.2842, -2.114, -1.3269, -0.611 | -3.2842: 1277 (80%); -2.114: 958 (60%); -1.3269: 639 (40%); -0.611: 320 (20%) | -3.2842: 320 (20%); -2.114: 639 (40%); -1.3269: 958 (60%); -0.611: 1277 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.3966, -0.0179, 0.3103, 0.673 | -0.3966: 1277 (80%); -0.0179: 958 (60%); 0.3103: 639 (40%); 0.673: 320 (20%) | -0.3966: 320 (20%); -0.0179: 639 (40%); 0.3103: 958 (60%); 0.673: 1277 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -3.3729, -2.2265, -1.586, -0.7916 | -3.3729: 1277 (80%); -2.2265: 958 (60%); -1.586: 639 (40%); -0.7916: 320 (20%) | -3.3729: 320 (20%); -2.2265: 639 (40%); -1.586: 958 (60%); -0.7916: 1277 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -5.397, -2.014, 0.839, 3.618 | -5.397: 1277 (80%); -2.014: 958 (60%); 0.839: 639 (40%); 3.618: 320 (20%) | -5.397: 320 (20%); -2.014: 639 (40%); 0.839: 958 (60%); 3.618: 1277 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 80.98, 87.73, 91.92, 95.22 | 80.98: 1277 (80%); 87.73: 958 (60%); 91.92: 639 (40%); 95.22: 320 (20%) | 80.98: 320 (20%); 87.73: 640 (40%); 91.92: 959 (60%); 95.22: 1278 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 41.47, 45.11, 48.01, 51.09 | 41.47: 1277 (80%); 45.11: 958 (60%); 48.01: 639 (40%); 51.09: 322 (20%) | 41.47: 321 (20%); 45.11: 643 (40%); 48.01: 958 (60%); 51.09: 1277 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 43.95, 49.51, 54.72, 60.08 | 43.95: 1277 (80%); 49.51: 959 (60%); 54.72: 639 (40%); 60.08: 321 (20%) | 43.95: 320 (20%); 49.51: 640 (40%); 54.72: 959 (60%); 60.08: 1277 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0321, 0.0514, 0.0617, 0.0873 | 0.0321: 1282 (80%); 0.0514: 964 (60%); 0.0617: 640 (40%); 0.0873: 324 (20%) | 0.0321: 322 (20%); 0.0514: 654 (41%); 0.0617: 958 (60%); 0.0873: 1283 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0957, -0.064, -0.0504, -0.0365 | -0.0957: 1290 (81%); -0.064: 958 (60%); -0.0504: 639 (40%); -0.0365: 321 (20%) | -0.0957: 320 (20%); -0.064: 639 (40%); -0.0504: 958 (60%); -0.0365: 1277 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1596 (100%); 1: 322 (20%) | 0: 1274 (80%); 1: 1398 (88%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 21, 33, 53, 66 | 21: 1287 (81%); 33: 980 (61%); 53: 656 (41%); 66: 360 (23%) | 21: 319 (20%); 33: 652 (41%); 53: 984 (62%); 66: 1274 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.6% | 0.0122, 0.0186, 0.0274, 0.0453 | 0.0122: 1255 (79%); 0.0186: 946 (59%); 0.0274: 630 (39%); 0.0453: 315 (20%) | 0.0122: 318 (20%); 0.0186: 627 (39%); 0.0274: 944 (59%); 0.0453: 1258 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 99.9% | 0.2078, 0.2837, 0.3797, 0.501 | 0.2078: 1275 (80%); 0.2837: 957 (60%); 0.3797: 638 (40%); 0.501: 320 (20%) | 0.2078: 319 (20%); 0.2837: 638 (40%); 0.3797: 956 (60%); 0.501: 1275 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 99.9% | 25.86, 61.62, 96.8, 142.36 | 25.86: 1275 (80%); 61.62: 956 (60%); 96.8: 639 (40%); 142.36: 319 (20%) | 25.86: 319 (20%); 61.62: 638 (40%); 96.8: 957 (60%); 142.36: 1275 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -2.81, -0.665, 0.385, 2.14 | -2.81: 1277 (80%); -0.665: 959 (60%); 0.385: 640 (40%); 2.14: 320 (20%) | -2.81: 320 (20%); -0.665: 640 (40%); 0.385: 958 (60%); 2.14: 1277 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 20.11, 28.47, 40.38, 56.51 | 20.11: 1277 (80%); 28.47: 958 (60%); 40.38: 639 (40%); 56.51: 320 (20%) | 20.11: 320 (20%); 28.47: 639 (40%); 40.38: 959 (60%); 56.51: 1277 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 28.08, 39.62, 53.25, 70.99 | 28.08: 1278 (80%); 39.62: 958 (60%); 53.25: 639 (40%); 70.99: 320 (20%) | 28.08: 320 (20%); 39.62: 639 (40%); 53.25: 958 (60%); 70.99: 1277 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 25.61, 49.59, 77.18, 94.89 | 25.61: 1277 (80%); 49.59: 958 (60%); 77.18: 639 (40%); 94.89: 320 (20%) | 25.61: 320 (20%); 49.59: 639 (40%); 77.18: 958 (60%); 94.89: 1277 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 35.94, 66.11, 95.05, 100 | 35.94: 1277 (80%); 66.11: 958 (60%); 95.05: 639 (40%); 100: 570 (36%) | 35.94: 320 (20%); 66.11: 639 (40%); 95.05: 958 (60%); 100: 1596 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 15, 18 | 5: 1295 (81%); 10: 982 (62%); 15: 652 (41%); 18: 364 (23%) | 5: 370 (23%); 10: 677 (42%); 15: 1031 (65%); 18: 1340 (84%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 12, 17 | 4: 1349 (85%); 7: 998 (63%); 12: 670 (42%); 17: 351 (22%) | 4: 351 (22%); 7: 673 (42%); 12: 970 (61%); 17: 1312 (82%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 45.61, 51.01, 55.07, 59.72 | 45.61: 1277 (80%); 51.01: 959 (60%); 55.07: 639 (40%); 59.72: 320 (20%) | 45.61: 321 (20%); 51.01: 639 (40%); 55.07: 958 (60%); 59.72: 1277 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1786, 0.4444, 0.6548, 0.7857 | 0.1786: 1281 (80%); 0.4444: 979 (61%); 0.6548: 648 (41%); 0.7857: 332 (21%) | 0.1786: 321 (20%); 0.4444: 676 (42%); 0.6548: 969 (61%); 0.7857: 1277 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.22, 17.79, 21.4, 25.72 | 15.22: 1277 (80%); 17.79: 961 (60%); 21.4: 639 (40%); 25.72: 351 (22%) | 15.22: 321 (20%); 17.79: 639 (40%); 21.4: 960 (60%); 25.72: 1290 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.22, 17.79, 21.4, 25.72 | 15.22: 1277 (80%); 17.79: 961 (60%); 21.4: 639 (40%); 25.72: 351 (22%) | 15.22: 321 (20%); 17.79: 639 (40%); 21.4: 960 (60%); 25.72: 1290 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8606, 0.8939, 0.9204, 0.9554 | 0.8606: 1278 (80%); 0.8939: 959 (60%); 0.9204: 639 (40%); 0.9554: 324 (20%) | 0.8606: 323 (20%); 0.8939: 644 (40%); 0.9204: 960 (60%); 0.9554: 1277 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.66, 0.78, 0.9, 1.07 | 0.66: 1279 (80%); 0.78: 988 (62%); 0.9: 649 (41%); 1.07: 327 (20%) | 0.66: 340 (21%); 0.78: 639 (40%); 0.9: 967 (61%); 1.07: 1280 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 99.9% | 0.0159, 0.0336, 0.0553, 0.0971 | 0.0159: 1279 (80%); 0.0336: 957 (60%); 0.0553: 640 (40%); 0.0971: 319 (20%) | 0.0159: 320 (20%); 0.0336: 639 (40%); 0.0553: 958 (60%); 0.0971: 1276 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 46.3126, 77.8525, 117.3022, 197.0087 | 46.3126: 1277 (80%); 77.8525: 958 (60%); 117.3022: 639 (40%); 197.0087: 320 (20%) | 46.3126: 320 (20%); 77.8525: 639 (40%); 117.3022: 958 (60%); 197.0087: 1277 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 44.6156, 75.2759, 112.6416, 189.9376 | 44.6156: 1277 (80%); 75.2759: 958 (60%); 112.6416: 639 (40%); 189.9376: 320 (20%) | 44.6156: 320 (20%); 75.2759: 639 (40%); 112.6416: 958 (60%); 189.9376: 1277 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 42.6353, 72.3435, 109.1262, 183.1349 | 42.6353: 1277 (80%); 72.3435: 958 (60%); 109.1262: 639 (40%); 183.1349: 320 (20%) | 42.6353: 320 (20%); 72.3435: 639 (40%); 109.1262: 958 (60%); 183.1349: 1277 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.6636, 80.1023, 123.0376, 203.0272 | 47.6636: 1278 (80%); 80.1023: 958 (60%); 123.0376: 639 (40%); 203.0272: 320 (20%) | 47.6636: 320 (20%); 80.1023: 639 (40%); 123.0376: 958 (60%); 203.0272: 1277 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 49.6358, 82.8911, 127.3073, 209.2304 | 49.6358: 1277 (80%); 82.8911: 958 (60%); 127.3073: 639 (40%); 209.2304: 320 (20%) | 49.6358: 320 (20%); 82.8911: 639 (40%); 127.3073: 958 (60%); 209.2304: 1277 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1596 (100%) | 0: 1442 (90%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1596 (100%) | 0: 1409 (88%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.9% | -0.0806, -0.0402, -0.0115, 0.0201 | -0.0806: 1275 (80%); -0.0402: 957 (60%); -0.0115: 638 (40%); 0.0201: 319 (20%) | -0.0806: 320 (20%); -0.0402: 639 (40%); -0.0115: 959 (60%); 0.0201: 1275 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -62.56, -47.59, -30.2, -12.46 | -62.56: 1277 (80%); -47.59: 958 (60%); -30.2: 639 (40%); -12.46: 320 (20%) | -62.56: 320 (20%); -47.59: 639 (40%); -30.2: 958 (60%); -12.46: 1277 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.5387, 0.7956, 1.0052, 1.3069 | 0.5387: 1265 (79%); 0.7956: 949 (59%); 1.0052: 633 (40%); 1.3069: 317 (20%) | 0.5387: 317 (20%); 0.7956: 633 (40%); 1.0052: 949 (59%); 1.3069: 1265 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 1287 (81%); 5: 990 (62%); 7: 691 (43%); 9: 385 (24%) | 3: 458 (29%); 5: 732 (46%); 7: 1041 (65%); 9: 1378 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 98.8% | 0.2005, 0.2396, 0.2919, 0.3734 | 0.2005: 1262 (79%); 0.2396: 948 (59%); 0.2919: 631 (40%); 0.3734: 317 (20%) | 0.2005: 318 (20%); 0.2396: 632 (40%); 0.2919: 947 (59%); 0.3734: 1262 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 98.8% | 4, 6, 8, 9 | 4: 1274 (80%); 6: 972 (61%); 8: 664 (42%); 9: 486 (30%) | 4: 444 (28%); 6: 742 (46%); 8: 1091 (68%); 9: 1308 (82%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0228, 0.0307, 0.0399, 0.0566 | 0.0228: 1266 (79%); 0.0307: 949 (59%); 0.0399: 639 (40%); 0.0566: 318 (20%) | 0.0228: 321 (20%); 0.0307: 634 (40%); 0.0399: 949 (59%); 0.0566: 1265 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 1288 (81%); 5: 990 (62%); 7: 678 (42%); 9: 353 (22%) | 3: 434 (27%); 5: 752 (47%); 7: 1062 (67%); 9: 1384 (87%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 98.9% | -0.2683, -0.1373, -0.0331, 0.0814 | -0.2683: 1264 (79%); -0.1373: 947 (59%); -0.0331: 631 (40%); 0.0814: 316 (20%) | -0.2683: 316 (20%); -0.1373: 631 (40%); -0.0331: 947 (59%); 0.0814: 1263 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 98.9% | 1, 3, 4, 7 | 1: 1578 (99%); 3: 1025 (64%); 4: 825 (52%); 7: 325 (20%) | 1: 332 (21%); 3: 753 (47%); 4: 968 (61%); 7: 1358 (85%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 1.9% |
| 8k_item_5_02_filed_within_7d | 3.1% |
| above_avwap_20high | 57.8% |
| above_avwap_20low | 97.6% |
| above_avwap_252low | 63.3% |
| above_avwap_50low | 92.6% |
| above_cam_r3 | 68.1% |
| above_cam_r4 | 36.5% |
| above_cpr | 99.1% |
| above_pivot | 99.6% |
| above_prev_high | 75.1% |
| above_prev_high_clearance_atr_05 | 18.5% |
| above_r1 | 51.1% |
| above_r2 | 21.6% |
| above_vwap | 24.8% |
| ad_rising | 89.2% |
| adx_cross_up | 0.4% |
| adx_cross_up_20 | 0.3% |
| adx_di_bear | 66.7% |
| adx_di_bull | 33.3% |
| adx_strong | 9.3% |
| adx_trending | 46.6% |
| ao_cross_dn | 0.8% |
| ao_cross_up | 2.5% |
| ao_positive | 9.5% |
| ao_twin_peaks_bull | 15.2% |
| at_key_fib | 20.9% |
| at_key_fib_wide | 48.1% |
| avwap_20high_loss_recent_3d | 0.1% |
| avwap_20high_reclaim_recent_3d | 48.9% |
| avwap_20low_reclaim_recent_3d | 37.2% |
| avwap_252low_loss_recent_3d | 0.1% |
| avwap_252low_reclaim_recent_3d | 28.6% |
| avwap_50low_reclaim_recent_3d | 38.8% |
| bb_10_20_above_mid | 81.8% |
| bb_10_20_expanding | 46.6% |
| bb_10_20_pctb_gt_75 | 54.5% |
| bb_10_20_pctb_gt_8 | 47.1% |
| bb_10_20_pctb_gt_85 | 37.4% |
| bb_10_20_pctb_gt_9 | 26.4% |
| bb_10_20_pctb_gt_95 | 14.4% |
| bb_10_20_pctb_lt_25 | 0.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 7.2% |
| bb_10_20_reclaim_from_upper_recent_3d | 5.8% |
| bb_10_20_squeeze | 40.1% |
| bb_10_20_touch_upper | 17.7% |
| bb_20_15_above_mid | 50.1% |
| bb_20_15_expanding | 35.8% |
| bb_20_15_pctb_gt_75 | 27.4% |
| bb_20_15_pctb_gt_8 | 24.1% |
| bb_20_15_pctb_gt_85 | 21.1% |
| bb_20_15_pctb_gt_9 | 17.6% |
| bb_20_15_pctb_gt_95 | 14.4% |
| bb_20_15_pctb_lt_05 | 1.1% |
| bb_20_15_pctb_lt_1 | 2.8% |
| bb_20_15_pctb_lt_15 | 5.3% |
| bb_20_15_pctb_lt_2 | 9.2% |
| bb_20_15_pctb_lt_25 | 14.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 34.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 0.2% |
| bb_20_15_squeeze | 31.0% |
| bb_20_15_touch_lower | 0.8% |
| bb_20_15_touch_upper | 16.4% |
| bb_20_20_above_mid | 50.1% |
| bb_20_20_expanding | 35.8% |
| bb_20_20_pctb_gt_75 | 22.1% |
| bb_20_20_pctb_gt_8 | 17.6% |
| bb_20_20_pctb_gt_85 | 13.5% |
| bb_20_20_pctb_gt_9 | 10.0% |
| bb_20_20_pctb_gt_95 | 6.1% |
| bb_20_20_pctb_lt_1 | 0.3% |
| bb_20_20_pctb_lt_15 | 0.9% |
| bb_20_20_pctb_lt_2 | 2.8% |
| bb_20_20_pctb_lt_25 | 6.3% |
| bb_20_20_reclaim_from_lower_recent_3d | 13.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 0.5% |
| bb_20_20_squeeze | 16.8% |
| bb_20_20_touch_upper | 6.5% |
| bearish_pin_bar | 5.3% |
| below_avwap_20high | 42.2% |
| below_avwap_20low | 2.4% |
| below_avwap_252low | 36.7% |
| below_avwap_50low | 7.4% |
| below_cpr | 0.4% |
| below_ema_20 | 48.9% |
| below_ema_200 | 89.9% |
| below_ema_200_break_recent_5d | 1.6% |
| below_ema_20_break_recent_5d | 2.9% |
| below_ema_21 | 50.6% |
| below_ema_21_break_recent_5d | 2.9% |
| below_ema_50 | 79.2% |
| below_ema_50_break_recent_5d | 2.1% |
| below_ema_9 | 16.7% |
| below_ema_9_break_recent_5d | 2.1% |
| below_prev_high | 24.2% |
| below_sma_20 | 49.8% |
| below_sma_200 | 87.4% |
| below_sma_21 | 52.3% |
| below_sma_50 | 78.7% |
| below_sma_9 | 14.4% |
| below_vwap | 75.2% |
| bullish_pin_bar | 4.8% |
| capitulation_recent_3d | 0.9% |
| ceo_buy | 1.1% |
| cfo_buy | 0.8% |
| chandelier_long_bullish | 56.5% |
| chandelier_short_bearish | 73.4% |
| chandelier_short_flip_up | 11.8% |
| classification_change_from_tech | 50.0% |
| classification_change_to_defensive | 50.0% |
| close_in_bottom_40pct_of_range | 8.4% |
| close_in_top_40pct_of_range | 72.8% |
| cluster_buy | 0.9% |
| cmf_cross_dn | 1.9% |
| cmf_cross_up | 7.6% |
| cmf_negative | 48.4% |
| cmf_positive | 51.6% |
| concentrated_sell | 3.5% |
| cpr_narrow | 86.8% |
| cpr_narrow_tight | 20.1% |
| cup_handle_detected | 9.6% |
| cup_handle_neckline_break_retest_long | 0.3% |
| dc10_breakout_dn_1pct | 0.1% |
| dc10_breakout_up | 22.7% |
| dc10_breakout_up_1pct | 34.8% |
| dc10_new_high | 28.4% |
| dc10_strong_breakout_up | 3.7% |
| dc20_breakout_up | 4.9% |
| dc20_new_high | 7.1% |
| dc20_resistance_break_retest_strong | 1.1% |
| dc20_support_break_retest_strong | 20.5% |
| defensive_leadership | 56.0% |
| director_only_buy | 5.4% |
| doji | 3.9% |
| double_bottom_detected | 13.4% |
| double_top_detected | 15.0% |
| dpi_elevated | 59.1% |
| drying_volume_on_up_turn | 74.6% |
| ema_20_50_bearish | 92.8% |
| ema_20_50_bullish | 7.2% |
| ema_20_50_death_cross | 0.1% |
| ema_20_50_golden_cross | 0.6% |
| ema_50_200_bearish | 83.6% |
| ema_50_200_bullish | 16.4% |
| ema_50_200_death_cross | 0.4% |
| ema_9_21_bearish | 86.7% |
| ema_9_21_bullish | 13.3% |
| ema_9_21_golden_cross | 5.8% |
| flag_bear_break_retest_short | 1.1% |
| flag_bear_broke | 1.2% |
| flag_bear_detected | 0.8% |
| force_index_cross_up | 13.4% |
| force_index_positive | 56.0% |
| gap_dn_1_5pct | 2.7% |
| gap_dn_2pct | 0.9% |
| gap_up_1_5pct | 5.8% |
| gap_up_2pct | 3.2% |
| hammer | 4.3% |
| head_shoulders_bottom_detected | 3.2% |
| head_shoulders_top_detected | 4.7% |
| house_cluster_buy | 3.5% |
| house_cluster_sell | 4.1% |
| htf_aligned_bear | 66.9% |
| htf_aligned_bull | 3.5% |
| htf_disagreement | 1.8% |
| hull_bearish | 31.2% |
| hull_bullish | 68.8% |
| hull_flip_up | 20.9% |
| ichi_above_cloud | 8.8% |
| ichi_above_cloud_break_recent_5d | 6.3% |
| ichi_below_cloud | 78.9% |
| ichi_below_cloud_break_recent_5d | 2.9% |
| ichi_cloud_thick | 84.6% |
| ichi_tk_bearish | 84.2% |
| ichi_tk_bullish | 12.5% |
| ichi_tk_cross_dn | 1.7% |
| ichi_tk_cross_up | 1.8% |
| ichi_weekly_above_cloud | 11.4% |
| ichi_weekly_below_cloud | 51.4% |
| ichi_weekly_in_cloud | 37.2% |
| in_reversal_window | 1.0% |
| inside_bar | 5.8% |
| inside_cpr | 0.4% |
| inside_kc | 97.5% |
| insider_cluster_active | 30.0% |
| institutional_buy | 88.8% |
| institutional_negative | 4.7% |
| institutional_persistence_growing | 43.4% |
| institutional_persistence_strong | 58.1% |
| institutional_strong_buy | 77.3% |
| inverted_cup_handle_detected | 12.2% |
| is_friday | 21.1% |
| is_halloween_period | 45.4% |
| is_halloween_period_first_day | 0.6% |
| is_january | 6.4% |
| is_january_extended | 9.1% |
| is_monday | 19.1% |
| is_pre_holiday | 6.8% |
| is_summer_period | 54.6% |
| is_totm_window | 36.1% |
| is_totm_window_first_day | 10.5% |
| is_week_open | 22.3% |
| kc_touch_lower | 2.8% |
| kc_touch_upper | 0.4% |
| large_dollar_buy | 1.4% |
| macd_12_26_9_bearish | 38.5% |
| macd_12_26_9_bullish | 61.5% |
| macd_12_26_9_crossover_up | 12.5% |
| macd_8_21_5_bearish | 17.6% |
| macd_8_21_5_bullish | 82.4% |
| macd_8_21_5_crossover_up | 12.4% |
| marubozu_bull | 1.6% |
| mfi_broad_overbought | 4.9% |
| mfi_broad_oversold | 9.5% |
| mfi_overbought | 0.4% |
| mfi_oversold | 1.7% |
| monthly_above_sma_12 | 13.1% |
| monthly_above_sma_6 | 12.3% |
| monthly_bias_bear | 79.3% |
| monthly_bias_bull | 4.8% |
| monthly_momentum_pos | 20.5% |
| near_52w_high | 0.1% |
| near_52w_high_95pct | 0.3% |
| near_52w_high_retest_long | 0.4% |
| near_52w_low_105pct | 6.2% |
| near_avwap_20high_atr_05x | 44.6% |
| near_avwap_20high_atr_10x | 74.0% |
| near_avwap_20high_atr_15x | 90.0% |
| near_avwap_20high_atr_20x | 96.9% |
| near_avwap_20low_atr_05x | 14.2% |
| near_avwap_20low_atr_10x | 50.4% |
| near_avwap_20low_atr_15x | 78.8% |
| near_avwap_20low_atr_20x | 92.7% |
| near_avwap_252low_atr_05x | 16.6% |
| near_avwap_252low_atr_10x | 42.0% |
| near_avwap_252low_atr_15x | 63.3% |
| near_avwap_252low_atr_20x | 77.7% |
| near_avwap_50low_atr_05x | 16.4% |
| near_avwap_50low_atr_10x | 50.8% |
| near_avwap_50low_atr_15x | 77.5% |
| near_avwap_50low_atr_20x | 91.5% |
| near_cam_r3 | 32.5% |
| near_cam_s3 | 0.3% |
| near_cam_s4 | 0.1% |
| near_fib_236 | 1.3% |
| near_fib_382 | 4.1% |
| near_fib_500 | 7.4% |
| near_fib_618 | 9.4% |
| near_fib_786 | 9.2% |
| near_pivot | 3.3% |
| near_prev_close | 13.9% |
| near_prev_high | 27.1% |
| near_r1 | 29.4% |
| near_r1_wide | 83.8% |
| near_r2 | 12.0% |
| near_r2_wide | 68.5% |
| near_s1_wide | 14.3% |
| near_s2_wide | 1.9% |
| near_wood_r1 | 14.2% |
| news_uses_polygon_score | 17.7% |
| obv_bearish | 37.1% |
| obv_bullish | 62.9% |
| obv_diverge_bull | 7.8% |
| obv_falling | 8.5% |
| obv_rising | 91.5% |
| outside_bar | 3.4% |
| pead_negative_surprise | 26.8% |
| pead_positive_surprise | 13.2% |
| pin_bar | 10.0% |
| po3_accumulation_active | 28.8% |
| po3_bullish | 5.2% |
| po3_manipulation_sweep_down | 0.1% |
| po3_manipulation_sweep_up | 20.7% |
| po3_mmbm_setup | 0.1% |
| po3_sweep_above_prior_high | 93.5% |
| po3_sweep_below_prior_low | 7.1% |
| ppo_bullish | 58.9% |
| ppo_crossover_up | 12.0% |
| pre_fomc_d0 | 1.8% |
| pre_fomc_d1 | 2.8% |
| pre_fomc_window | 4.6% |
| price_above_dema | 90.0% |
| price_above_ema_20 | 51.1% |
| price_above_ema_200 | 10.1% |
| price_above_ema_200_break_recent_5d | 8.1% |
| price_above_ema_20_break_recent_5d | 48.8% |
| price_above_ema_21 | 49.4% |
| price_above_ema_21_break_recent_5d | 47.2% |
| price_above_ema_50 | 20.8% |
| price_above_ema_50_break_recent_5d | 19.6% |
| price_above_ema_9 | 83.3% |
| price_above_ema_9_break_recent_5d | 78.1% |
| price_above_hull | 96.2% |
| price_above_sma_200 | 12.6% |
| price_above_sma_21 | 47.7% |
| price_above_sma_50 | 21.3% |
| price_above_tema | 95.3% |
| price_below_dema | 10.0% |
| price_below_hull | 3.8% |
| price_below_tema | 4.7% |
| psar_bullish | 57.1% |
| psar_flip_dn | 0.1% |
| psar_flip_up | 16.6% |
| r1_break_retest_long | 69.2% |
| recent_capitulation_at_s3 | 0.1% |
| resistance_break_retest | 3.3% |
| risk_off_regime_bond_signal | 21.6% |
| risk_off_regime_bond_signal_strong | 7.2% |
| risk_off_regime_gold_signal | 43.4% |
| risk_on_regime_bond_signal | 43.9% |
| risk_on_regime_bond_signal_strong | 17.8% |
| roc_positive | 46.2% |
| roc_turning_dn | 2.5% |
| roc_turning_up | 14.7% |
| rsi_14_bullish | 40.7% |
| rsi_14_cross_up_extreme_os_recent_3d | 2.0% |
| rsi_14_cross_up_oversold_recent_3d | 18.1% |
| rsi_14_extreme_os | 0.3% |
| rsi_14_oversold | 1.4% |
| rsi_21_bullish | 26.9% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_21_cross_up_oversold_recent_3d | 7.4% |
| rsi_21_extreme_os | 0.2% |
| rsi_21_overbought | 0.1% |
| rsi_21_oversold | 1.1% |
| rsi_2_bullish | 99.1% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 0.4% |
| rsi_2_cross_dn_overbought_recent_3d | 0.4% |
| rsi_2_cross_up_extreme_os_recent_3d | 44.9% |
| rsi_2_cross_up_oversold_recent_3d | 56.9% |
| rsi_2_extreme_ob | 82.0% |
| rsi_2_overbought | 93.5% |
| rsi_2_oversold | 0.1% |
| rsi_9_bullish | 57.3% |
| rsi_9_cross_up_extreme_os_recent_3d | 7.7% |
| rsi_9_cross_up_oversold_recent_3d | 31.8% |
| rsi_9_extreme_os | 0.4% |
| rsi_9_overbought | 0.4% |
| rsi_9_oversold | 1.8% |
| s1_break_retest_short | 35.9% |
| sc_13d_filed_within_30d | 0.4% |
| sc_13g_filed_within_30d | 2.1% |
| sector_outperforming_spy | 34.9% |
| sector_underperforming_spy | 65.1% |
| shooting_star | 4.8% |
| sma_20_50_bullish | 14.0% |
| sma_20_50_golden_cross | 0.4% |
| sma_50_200_bullish | 24.1% |
| sma_9_21_bullish | 16.9% |
| sma_9_21_golden_cross | 3.0% |
| smc_bos_bearish | 25.6% |
| smc_bos_bullish | 2.0% |
| smc_bos_retest_long | 3.5% |
| smc_bos_retest_short | 6.5% |
| smc_breaker_block_bearish | 26.2% |
| smc_breaker_block_bullish | 9.8% |
| smc_choch_bearish | 6.8% |
| smc_choch_bullish | 1.2% |
| smc_equal_highs_swept | 1.1% |
| smc_equal_lows_swept | 6.0% |
| smc_fvg_bearish_active | 28.2% |
| smc_fvg_bullish_active | 73.9% |
| smc_fvg_retest_long_zone | 1.4% |
| smc_fvg_retest_short_zone | 13.2% |
| smc_in_discount_zone | 89.7% |
| smc_in_premium_zone | 35.8% |
| smc_inverse_fvg_bearish | 97.5% |
| smc_inverse_fvg_bullish | 81.2% |
| smc_liquidity_swept_dn | 0.3% |
| smc_liquidity_swept_up | 1.9% |
| smc_mitigation_block_long | 0.6% |
| smc_mitigation_block_short | 0.4% |
| smc_ob_bearish_active | 64.1% |
| smc_ob_bullish_active | 6.8% |
| smc_ote_long_zone | 12.2% |
| smc_ote_short_zone | 1.4% |
| squeeze_fire_up | 9.3% |
| squeeze_in | 24.1% |
| squeeze_positive | 46.7% |
| stoch_bearish_cross | 0.2% |
| stoch_broad_overbought | 16.4% |
| stoch_broad_oversold | 15.3% |
| stoch_bullish_cross | 11.4% |
| stoch_overbought | 12.5% |
| stoch_oversold | 7.5% |
| stochrsi_cross_dn | 9.7% |
| stochrsi_cross_up | 39.1% |
| stochrsi_overbought | 51.3% |
| stochrsi_oversold | 9.2% |
| supertrend_bearish | 0.8% |
| supertrend_bullish | 99.2% |
| supertrend_flip_recent_long_5d | 5.7% |
| supertrend_flip_recent_short_5d | 2.0% |
| supertrend_flip_up | 2.1% |
| support_break_retest | 23.4% |
| tema_above_dema | 42.4% |
| tema_cross_dn | 0.2% |
| tema_cross_up | 8.5% |
| triangle_apex_break_retest_long | 3.3% |
| triangle_ascending_detected | 3.3% |
| triangle_descending_detected | 11.8% |
| uo_overbought | 1.0% |
| uo_oversold | 0.3% |
| usd_strengthening | 23.0% |
| usd_weakening | 12.2% |
| vix_band_high | 39.2% |
| vix_band_low | 30.4% |
| vix_band_mid | 30.5% |
| vix_term_backwardation | 4.5% |
| vix_term_contango | 95.5% |
| vol_above_avg | 25.4% |
| vol_below_avg | 74.6% |
| vol_spike_12x | 12.1% |
| vol_spike_15x | 4.6% |
| vol_spike_17x | 2.4% |
| vol_spike_2x | 1.6% |
| vol_spike_2x_on_down_day_recent_3d | 1.8% |
| vol_spike_2x_on_up_day_recent_3d | 4.6% |
| vol_spike_3x | 0.2% |
| vp_above_value_area | 2.7% |
| vp_below_value_area | 25.8% |
| vp_close_above_poc | 37.3% |
| vp_close_below_poc | 62.7% |
| vp_in_value_area | 71.5% |
| week_open_gap_down_15pct | 0.8% |
| week_open_gap_up_15pct | 1.0% |
| weekly_above_ema_10 | 22.6% |
| weekly_above_ema_20 | 10.9% |
| weekly_bias_bear | 76.4% |
| weekly_bias_bull | 9.9% |
| weekly_momentum_pos | 31.7% |
| williams_r_overbought | 28.5% |
| williams_r_oversold | 2.4% |
| williams_r_rising | 92.7% |
| within_pead_window | 37.2% |
| within_post_deletion_window | 13.5% |
| within_pre_rebalance_window | 0.5% |
| xs_avoid_high_ivol | 69.2% |
| xs_avoid_high_max | 77.7% |
| xs_high_beta_decile | 24.4% |
| xs_low_beta_bottom_quintile | 24.4% |
| xs_low_beta_decile | 18.6% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 18.6% |
| xs_momentum_bottom_decile | 21.0% |
| xs_momentum_bottom_quintile | 35.0% |
| xs_momentum_top_decile | 3.9% |
| xs_momentum_top_quintile | 8.2% |
| xs_quality_bottom_quintile | 24.2% |
| xs_quality_top_quintile | 21.5% |
| xs_quality_top_tercile | 38.7% |
| year_low_break_retest_short | 3.3% |
| yoy_surprise_high | 37.8% |
| yoy_surprise_negative | 51.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.3% |
| committed_growth_holders | 91.3% |
| corp_donations_1y | 5.7% |
| corp_donations_count_1y | 5.7% |
| corp_donations_unique_pacs | 5.7% |
| cot_rut_commercials_pctile_3y | 45.2% |
| cot_rut_mmoney_pctile_3y | 45.2% |
| cup_handle_depth_pct | 15.3% |
| days_since_deletion | 8.8% |
| days_since_inclusion | 12.8% |
| days_to_next_holiday | 61.8% |
| days_to_rebalance | 13.6% |
| dpi_30d_avg | 95.9% |
| dpi_recent | 95.9% |
| earnings_announcement_return | 90.2% |
| earnings_eps_yoy_growth | 92.7% |
| flag_bear_pole_move_pct | 0.8% |
| gov_contracts_4q_sum | 39.9% |
| gov_contracts_last_qtr_amount | 39.9% |
| gov_contracts_qoq_growth | 39.9% |
| head_shoulders_magnitude_pct | 7.7% |
| insider_director_buyers_30d | 8.1% |
| insider_officer_buyers_30d | 8.1% |
| insider_total_shares_bought_30d | 8.1% |
| insider_unique_buyers_30d | 8.1% |
| inverted_cup_handle_height_pct | 18.7% |
| lobbying_amount_1y | 68.1% |
| lobbying_amount_q | 68.1% |
| lobbying_amount_yoy | 68.1% |
| otc_short_ratio_recent | 95.9% |
| otc_volume_recent | 95.9% |
| pair_half_life | 92.4% |
| pair_max_abs_zscore | 92.4% |
| pair_zscore_signed | 92.4% |
| pct_from_avwap_20high | 91.9% |
| persistent_holders_4q | 91.3% |
| persistent_holders_8q | 91.3% |
| sc_13g_latest_percent_owned | 1.2% |
| search_volume_index_recent | 77.3% |
| search_volume_observations | 77.3% |
| search_volume_zscore_30d | 77.3% |
| sector_etf_return_20d | 2.7% |
| spy_return_20d | 2.7% |
| total_active_holders | 91.3% |
| triangle_breakdown_pct | 11.8% |
| triangle_breakout_pct | 3.3% |
| xs_quality_decile | 64.3% |
| xs_quality_gross_profitability | 64.3% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.997), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.998), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.996), `days_since_classification_change` (-1.0), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.998), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.998), `double_top_neckline` (0.997), `double_top_peak` (0.998), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.993), `fib_382` (0.995), `fib_500` (0.996), `fib_618` (0.997), `fib_786` (0.998), `fib_ext_127` (0.985), `fib_ext_162` (0.98), `flag_bear_breakdown_level` (0.989), `head_shoulders_bottom_neckline` (0.996), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.994), `ichi_senkou_b` (0.991), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.982), `monthly_sma_6` (0.994), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.998), `supertrend_value` (0.998), `swing_high` (0.989), `swing_low` (0.998), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.996), `vp_value_area_low` (0.998), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.956), `year_low` (0.988)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | n_bars (pattern length) | 2 | **FIRE-ADDING** | **YES** |
| P1.2 | min_body_pct_of_range per candle | 3 | **FIRE-ADDING** | **YES** |
| P1.3 | min_step_up_pct (close[i] above close[i- | 3 | **FIRE-ADDING** | **YES** |
| P1.4 | max_upper_wick_pct (close near high) | 3 | **FIRE-ADDING** | **YES** |
| P2 | rsi_14 < 60 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     2 x 3 x 3 x 3 x 5 = 270
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        54 (every fire-adding axis sits at production-only until its env actuator exists)
check              54 x 5 = 270
```

B-row candidates NOT in this factorial: 583 census axes join it only when REGISTERED at the T3 band review.
