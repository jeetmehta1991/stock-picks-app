# Table A - three_black_crows_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:24:46 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** candle | **status:** NOT-STARTED | **R5 fires:** 1674 | **surviving fires (T1):** 1674 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  three_black_crows  <- backtest/signals/screener.py +1
       knobs P1.1-P1.4 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  rsi_14 > 40   [EXISTING-THRESHOLD]
P3  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_three_black_crows_short (docstring and return dropped):

```python
fires = s.get('three_black_crows') and s.get('rsi_14', 50) > 40 and (not _short_borrow_trap_active(s))
```

## Table A - parameter inventory (canonical shape - READY FOR OWNER BAND REVIEW)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close).
Every producer row carries its DEFINED BANDS in the P<n>.x rows beneath
it (B2845, owner-corrected: a ready and FINAL Table A per strategy);
the engine-spec (SPECS) entry is built from these before any engine
leg runs.

| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|
| P1 | PRODUCER | three_black_crows - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | n_bars (pattern length) - backtest/signals/technical.py:2108-2111 | 3 | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | CANON (Nison 1991: three); 4 as the strict extension; T3 review before any grid |
| P1.2 | BAND | min_body_pct_of_range per candle - technical.py:2109 (c<o only - no magnitude) | 0.0 | none | the whole band; DEFINED-NO-ACTUATOR | CANON (Nison long-body crows); production accepts ANY body; T3 review before any grid |
| P1.3 | BAND | min_step_down_pct (close[i] below close[i-1] by) - technical.py:2110 | 0.0 | none | the whole band; DEFINED-NO-ACTUATOR | BRACKET zero upward; strict < today; T3 review before any grid |
| P1.4 | BAND | max_lower_wick_pct (close near low) - technical.py:2108-2111 (absent today) | None | none | the whole band; DEFINED-NO-ACTUATOR | CANON (crows close at/near lows); production unenforced; T3 review before any grid |
| P2 | STRATEGY | rsi_14 `> 40` [EXISTING-THRESHOLD] | `> 40` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P2.1 | BAND | rsi span - backtest/signals/technical.py rsi block | 14 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P3 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `> 40` | 100.0% | TIGHTER = RAISE the floor: 45.094 -> 1339 (80%); 50.132 -> 1004 (60%); 54.066 -> 670 (40%); 58.812 -> 335 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 17.416, 21.8, 26.728, 34.248 | 17.416: 1339 (80%); 21.8: 1005 (60%); 26.728: 670 (40%); 34.248: 335 (20%) | 17.416: 335 (20%); 21.8: 673 (40%); 26.728: 1004 (60%); 34.248: 1339 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 17.75, 20.68, 23.548, 26.75 | 17.75: 1340 (80%); 20.68: 1006 (60%); 23.548: 670 (40%); 26.75: 336 (20%) | 17.75: 337 (20%); 20.68: 671 (40%); 23.548: 1004 (60%); 26.75: 1340 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 20.602, 23.68, 26.61, 30.654 | 20.602: 1339 (80%); 23.68: 1006 (60%); 26.61: 671 (40%); 30.654: 335 (20%) | 20.602: 335 (20%); 23.68: 672 (40%); 26.61: 1005 (60%); 30.654: 1339 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 0.7211, 2.5099, 4.9563, 11.0771 | 0.7211: 1339 (80%); 2.5099: 1004 (60%); 4.9563: 670 (40%); 11.0771: 335 (20%) | 0.7211: 335 (20%); 2.5099: 670 (40%); 4.9563: 1004 (60%); 11.0771: 1339 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2247, 2.0888, 3.5995, 6.2589 | 1.2247: 1339 (80%); 2.0888: 1004 (60%); 3.5995: 670 (40%); 6.2589: 335 (20%) | 1.2247: 335 (20%); 2.0888: 670 (40%); 3.5995: 1004 (60%); 6.2589: 1339 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2247, 2.0888, 3.5995, 6.2589 | 1.2247: 1339 (80%); 2.0888: 1004 (60%); 3.5995: 670 (40%); 6.2589: 335 (20%) | 1.2247: 335 (20%); 2.0888: 670 (40%); 3.5995: 1004 (60%); 6.2589: 1339 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.795, 2.125, 2.5198, 3.1914 | 1.795: 1341 (80%); 2.125: 1006 (60%); 2.5198: 670 (40%); 3.1914: 335 (20%) | 1.795: 336 (20%); 2.125: 671 (40%); 2.5198: 1004 (60%); 3.1914: 1339 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0442, 0.0607, 0.0796, 0.1152 | 0.0442: 1340 (80%); 0.0607: 1005 (60%); 0.0796: 671 (40%); 0.1152: 336 (20%) | 0.0442: 338 (20%); 0.0607: 670 (40%); 0.0796: 1005 (60%); 0.1152: 1339 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.0875, 0.1987, 0.3493, 0.5039 | 0.0875: 1340 (80%); 0.1987: 1006 (60%); 0.3493: 670 (40%); 0.5039: 335 (20%) | 0.0875: 336 (20%); 0.1987: 670 (40%); 0.3493: 1005 (60%); 0.5039: 1339 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0503, 0.0709, 0.0952, 0.1304 | 0.0503: 1339 (80%); 0.0709: 1007 (60%); 0.0952: 670 (40%); 0.1304: 335 (20%) | 0.0503: 335 (20%); 0.0709: 670 (40%); 0.0952: 1005 (60%); 0.1304: 1339 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.1641, 0.4102, 0.5882, 0.7202 | 0.1641: 1339 (80%); 0.4102: 1006 (60%); 0.5882: 670 (40%); 0.7202: 336 (20%) | 0.1641: 335 (20%); 0.4102: 670 (40%); 0.5882: 1006 (60%); 0.7202: 1339 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0671, 0.0945, 0.1269, 0.1739 | 0.0671: 1339 (80%); 0.0945: 1007 (60%); 0.1269: 671 (40%); 0.1739: 335 (20%) | 0.0671: 337 (20%); 0.0945: 670 (40%); 0.1269: 1005 (60%); 0.1739: 1339 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.2481, 0.4326, 0.5661, 0.6651 | 0.2481: 1339 (80%); 0.4326: 1006 (60%); 0.5661: 670 (40%); 0.6651: 336 (20%) | 0.2481: 335 (20%); 0.4326: 670 (40%); 0.5661: 1005 (60%); 0.6651: 1339 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0547, -0.0302, -0.0105, 0.0138 | -0.0547: 1339 (80%); -0.0302: 1010 (60%); -0.0105: 670 (40%); 0.0138: 335 (20%) | -0.0547: 338 (20%); -0.0302: 671 (40%); -0.0105: 1005 (60%); 0.0138: 1339 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1369, 0.1605, 0.1836, 0.2515 | 0.1369: 1341 (80%); 0.1605: 1004 (60%); 0.1836: 668 (40%); 0.2515: 337 (20%) | 0.1369: 333 (20%); 0.1605: 670 (40%); 0.1836: 1006 (60%); 0.2515: 1337 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1674 (100%) | 0: 1621 (97%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0726, 0.0044, 0.0768, 0.146 | -0.0726: 1339 (80%); 0.0044: 1004 (60%); 0.0768: 670 (40%); 0.146: 336 (20%) | -0.0726: 335 (20%); 0.0044: 670 (40%); 0.0768: 1004 (60%); 0.146: 1339 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1674 (100%); 1: 732 (44%) | 0: 942 (56%); 1: 1366 (82%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2396, -0.2118, -0.1644, -0.1405 | -0.2396: 1343 (80%); -0.2118: 1008 (60%); -0.1644: 670 (40%); -0.1405: 336 (20%) | -0.2396: 337 (20%); -0.2118: 672 (40%); -0.1644: 1004 (60%); -0.1405: 1348 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5449, 0.6474, 0.75 | 0.2628: 1342 (80%); 0.5449: 1007 (60%); 0.6474: 685 (41%); 0.75: 341 (20%) | 0.2628: 338 (20%); 0.5449: 697 (42%); 0.6474: 1009 (60%); 0.75: 1368 (82%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3141, 0.4808, 0.6987, 0.891 | 0.3141: 1349 (81%); 0.4808: 1011 (60%); 0.6987: 680 (41%); 0.891: 340 (20%) | 0.3141: 392 (23%); 0.4808: 672 (40%); 0.6987: 1008 (60%); 0.891: 1353 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1781, -0.0664, 0.0223, 0.1461 | -0.1781: 1340 (80%); -0.0664: 1013 (61%); 0.0223: 672 (40%); 0.1461: 338 (20%) | -0.1781: 338 (20%); -0.0664: 672 (40%); 0.0223: 1015 (61%); 0.1461: 1348 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.3269, 0.5192, 0.7179 | 0.1538: 1366 (82%); 0.3269: 1020 (61%); 0.5192: 675 (40%); 0.7179: 343 (20%) | 0.1538: 339 (20%); 0.3269: 690 (41%); 0.5192: 1026 (61%); 0.7179: 1358 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1154, 0.2692, 0.4423, 0.6987 | 0.1154: 1363 (81%); 0.2692: 1007 (60%); 0.4423: 673 (40%); 0.6987: 367 (22%) | 0.1154: 341 (20%); 0.2692: 684 (41%); 0.4423: 1012 (60%); 0.6987: 1340 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4859, -0.2257, -0.0279, 0.1047 | -0.4859: 1339 (80%); -0.2257: 1009 (60%); -0.0279: 674 (40%); 0.1047: 342 (20%) | -0.4859: 335 (20%); -0.2257: 676 (40%); -0.0279: 1009 (60%); 0.1047: 1347 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.6193, 0.9038, 0.9679 | 0.3397: 1356 (81%); 0.6193: 1004 (60%); 0.9038: 682 (41%); 0.9679: 371 (22%) | 0.3397: 338 (20%); 0.6193: 670 (40%); 0.9038: 1021 (61%); 0.9679: 1343 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0705, 0.359, 0.5641, 0.8013 | 0.0705: 1378 (82%); 0.359: 1015 (61%); 0.5641: 691 (41%); 0.8013: 352 (21%) | 0.0705: 344 (21%); 0.359: 676 (40%); 0.5641: 1012 (60%); 0.8013: 1358 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0668, -0.0588, -0.0408, 0 | -0.0668: 1357 (81%); -0.0588: 1011 (60%); -0.0408: 673 (40%); 0: 560 (33%) | -0.0668: 339 (20%); -0.0588: 676 (40%); -0.0408: 1008 (60%); 0: 1638 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.6436, 0.8718, 1 | 0.3397: 1344 (80%); 0.6436: 1004 (60%); 0.8718: 691 (41%); 1: 448 (27%) | 0.3397: 343 (20%); 0.6436: 670 (40%); 0.8718: 1011 (60%); 1: 1674 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1603, 0.2756, 0.5962, 0.9423 | 0.1603: 1342 (80%); 0.2756: 1006 (60%); 0.5962: 671 (40%); 0.9423: 357 (21%) | 0.1603: 365 (22%); 0.2756: 690 (41%); 0.5962: 1033 (62%); 0.9423: 1357 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0135, 0.0312, 0.0812, 0.1591 | -0.0135: 1344 (80%); 0.0312: 1006 (60%); 0.0812: 672 (40%); 0.1591: 346 (21%) | -0.0135: 338 (20%); 0.0312: 674 (40%); 0.0812: 1024 (61%); 0.1591: 1340 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4167, 0.7586, 0.9167, 0.9679 | 0.4167: 1355 (81%); 0.7586: 1007 (60%); 0.9167: 705 (42%); 0.9679: 372 (22%) | 0.4167: 341 (20%); 0.7586: 673 (40%); 0.9167: 1010 (60%); 0.9679: 1354 (81%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1383, 0.4167, 0.6026, 0.8013 | 0.1383: 1343 (80%); 0.4167: 1016 (61%); 0.6026: 711 (42%); 0.8013: 343 (20%) | 0.1383: 336 (20%); 0.4167: 672 (40%); 0.6026: 1008 (60%); 0.8013: 1357 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0203, 0.0689, 0.167 | -0.0812: 1463 (87%); -0.0203: 1110 (66%); 0.0689: 675 (40%); 0.167: 336 (20%) | -0.0812: 356 (21%); -0.0203: 676 (40%); 0.0689: 1009 (60%); 0.167: 1341 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1699, -0.0216, 0.0445, 0.0982 | -0.1699: 1342 (80%); -0.0216: 1011 (60%); 0.0445: 687 (41%); 0.0982: 335 (20%) | -0.1699: 347 (21%); -0.0216: 673 (40%); 0.0445: 1009 (60%); 0.0982: 1339 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3333, 0.5449, 0.7628, 0.891 | 0.3333: 1347 (80%); 0.5449: 1007 (60%); 0.7628: 677 (40%); 0.891: 350 (21%) | 0.3333: 337 (20%); 0.5449: 686 (41%); 0.7628: 1029 (61%); 0.891: 1355 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2564, 0.4679, 0.7372, 0.8269 | 0.2564: 1344 (80%); 0.4679: 1006 (60%); 0.7372: 676 (40%); 0.8269: 408 (24%) | 0.2564: 346 (21%); 0.4679: 675 (40%); 0.7372: 1041 (62%); 0.8269: 1347 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0597, 0.1377, 0.2673, 0.5119 | 0.0597: 1339 (80%); 0.1377: 1004 (60%); 0.2673: 670 (40%); 0.5119: 335 (20%) | 0.0597: 335 (20%); 0.1377: 670 (40%); 0.2673: 1004 (60%); 0.5119: 1339 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.6% | 28, 57, 79, 127 | 28: 1323 (79%); 57: 993 (59%); 79: 668 (40%); 127: 333 (20%) | 28: 343 (20%); 57: 668 (40%); 79: 999 (60%); 127: 1322 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.7% | 1.8071, 2.3218, 2.882, 3.6838 | 1.8071: 1335 (80%); 2.3218: 1001 (60%); 2.882: 668 (40%); 3.6838: 334 (20%) | 1.8071: 334 (20%); 2.3218: 668 (40%); 2.882: 1001 (60%); 3.6838: 1335 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 16, 27, 35 | 8: 1371 (82%); 16: 1012 (60%); 27: 715 (43%); 35: 348 (21%) | 8: 354 (21%); 16: 715 (43%); 27: 1016 (61%); 35: 1368 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 2.8, 3 | 1: 1387 (83%); 2: 1037 (62%); 2.8: 670 (40%); 3: 670 (40%) | 1: 637 (38%); 2: 1004 (60%); 2.8: 1004 (60%); 3: 1370 (82%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0112, -0.0046, 0.0093, 0.0226 | -0.0112: 1344 (80%); -0.0046: 1016 (61%); 0.0093: 685 (41%); 0.0226: 337 (20%) | -0.0112: 336 (20%); -0.0046: 675 (40%); 0.0093: 1014 (61%); 0.0226: 1343 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 25.0088, 26.0727, 26.5531, 27.0997 | 25.0088: 1339 (80%); 26.0727: 1007 (60%); 26.5531: 678 (41%); 27.0997: 338 (20%) | 25.0088: 335 (20%); 26.0727: 680 (41%); 26.5531: 1006 (60%); 27.0997: 1341 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.2834, 0, 0.1678, 0.5756 | -0.2834: 1339 (80%); 0: 1006 (60%); 0.1678: 670 (40%); 0.5756: 335 (20%) | -0.2834: 335 (20%); 0: 727 (43%); 0.1678: 1004 (60%); 0.5756: 1339 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.5756, -0.1678, 0, 0.2834 | -0.5756: 1339 (80%); -0.1678: 1004 (60%); 0: 727 (43%); 0.2834: 335 (20%) | -0.5756: 335 (20%); -0.1678: 670 (40%); 0: 1006 (60%); 0.2834: 1339 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.048, -0.0179, 0.0066, 0.0402 | -0.048: 1340 (80%); -0.0179: 1006 (60%); 0.0066: 670 (40%); 0.0402: 343 (20%) | -0.048: 336 (20%); -0.0179: 675 (40%); 0.0066: 1006 (60%); 0.0402: 1344 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0439, 8.4977, 8.7418, 9.0083 | 8.0439: 1338 (80%); 8.4977: 997 (60%); 8.7418: 670 (40%); 9.0083: 335 (20%) | 8.0439: 336 (20%); 8.4977: 677 (40%); 8.7418: 1004 (60%); 9.0083: 1339 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.4% | 0, 1 | 0: 1664 (99%); 1: 527 (31%) | 0: 1137 (68%); 1: 1471 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.4% | 0 | 0: 1358 (81%) | 0: 1347 (80%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.4% | 0, 1 | 0: 1664 (99%); 1: 537 (32%) | 0: 1127 (67%); 1: 1487 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 6, 140.8, 283.4 | 3: 1357 (81%); 6: 1028 (61%); 140.8: 670 (40%); 283.4: 335 (20%) | 3: 436 (26%); 6: 713 (43%); 140.8: 1004 (60%); 283.4: 1339 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 5, 90, 146 | 1: 1380 (82%); 5: 1031 (62%); 90: 673 (40%); 146: 336 (20%) | 1: 420 (25%); 5: 678 (41%); 90: 1007 (60%); 146: 1342 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.6224, -0.1957, 0.0336, 0.3379 | -0.6224: 1339 (80%); -0.1957: 1004 (60%); 0.0336: 670 (40%); 0.3379: 335 (20%) | -0.6224: 335 (20%); -0.1957: 670 (40%); 0.0336: 1005 (60%); 0.3379: 1339 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.2983, 0.9876, 1.8892, 4.2164 | 0.2983: 1339 (80%); 0.9876: 1004 (60%); 1.8892: 670 (40%); 4.2164: 335 (20%) | 0.2983: 335 (20%); 0.9876: 670 (40%); 1.8892: 1004 (60%); 4.2164: 1339 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | 0.3362, 1.036, 2.1118, 4.4085 | 0.3362: 1339 (80%); 1.036: 1004 (60%); 2.1118: 670 (40%); 4.4085: 335 (20%) | 0.3362: 336 (20%); 1.036: 670 (40%); 2.1118: 1004 (60%); 4.4085: 1339 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.9297, -0.4033, -0.1728, 0.0325 | -0.9297: 1339 (80%); -0.4033: 1004 (60%); -0.1728: 670 (40%); 0.0325: 335 (20%) | -0.9297: 336 (20%); -0.4033: 670 (40%); -0.1728: 1004 (60%); 0.0325: 1339 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.0916, 0.7609, 1.6762, 3.8092 | 0.0916: 1339 (80%); 0.7609: 1005 (60%); 1.6762: 670 (40%); 3.8092: 335 (20%) | 0.0916: 335 (20%); 0.7609: 670 (40%); 1.6762: 1004 (60%); 3.8092: 1339 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.3292, 1.0469, 2.0724, 4.5368 | 0.3292: 1339 (80%); 1.0469: 1004 (60%); 2.0724: 670 (40%); 4.5368: 335 (20%) | 0.3292: 335 (20%); 1.0469: 670 (40%); 2.0724: 1004 (60%); 4.5368: 1339 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 43.67, 51.07, 57.332, 64.268 | 43.67: 1340 (80%); 51.07: 1005 (60%); 57.332: 670 (40%); 64.268: 335 (20%) | 43.67: 336 (20%); 51.07: 671 (40%); 57.332: 1004 (60%); 64.268: 1339 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.2% | -0.0283, 0.0625, 0.1448, 0.2582 | -0.0283: 1329 (79%); 0.0625: 997 (60%); 0.1448: 666 (40%); 0.2582: 333 (20%) | -0.0283: 333 (20%); 0.0625: 665 (40%); 0.1448: 997 (60%); 0.2582: 1329 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.5% | 0.0056, 0.0131, 0.0244, 0.0468 | 0.0056: 1331 (80%); 0.0131: 997 (60%); 0.0244: 666 (40%); 0.0468: 334 (20%) | 0.0056: 334 (20%); 0.0131: 668 (40%); 0.0244: 999 (60%); 0.0468: 1331 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 4, 9 | 0: 1674 (100%); 1: 1220 (73%); 4: 672 (40%); 9: 355 (21%) | 0: 454 (27%); 1: 716 (43%); 4: 1085 (65%); 9: 1365 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0909 | 0: 1674 (100%); 0.0909: 341 (20%) | 0: 1238 (74%); 0.0909: 1343 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667, 0.4489, 0.6667 | 0: 1674 (100%); 0.1667: 1013 (61%); 0.4489: 670 (40%); 0.6667: 407 (24%) | 0: 644 (38%); 0.1667: 672 (40%); 0.4489: 1004 (60%); 0.6667: 1340 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 6 | 0: 1674 (100%); 1: 1134 (68%); 2: 847 (51%); 6: 392 (23%) | 0: 540 (32%); 1: 827 (49%); 2: 1006 (60%); 6: 1348 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 9 | 0: 1674 (100%); 1: 1220 (73%); 4: 672 (40%); 9: 355 (21%) | 0: 454 (27%); 1: 716 (43%); 4: 1085 (65%); 9: 1365 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1674 (100%); 1: 1190 (71%); 3: 755 (45%); 8: 338 (20%) | 0: 484 (29%); 1: 762 (46%); 3: 1042 (62%); 8: 1383 (83%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.296, 0.4467, 0.6667 | 0: 1604 (96%); 0.296: 1004 (60%); 0.4467: 670 (40%); 0.6667: 357 (21%) | 0: 336 (20%); 0.296: 670 (40%); 0.4467: 1004 (60%); 0.6667: 1353 (81%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2301, 0.6264 | 0: 1564 (93%); 0.2301: 670 (40%); 0.6264: 335 (20%) | 0: 881 (53%); 0.2301: 1004 (60%); 0.6264: 1339 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3333, 0.6667 | 0: 1591 (95%); 0.3333: 718 (43%); 0.6667: 338 (20%) | 0: 704 (42%); 0.3333: 1018 (61%); 0.6667: 1381 (82%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.6667 | 0: 1591 (95%); 0.3333: 718 (43%); 0.6667: 338 (20%) | 0: 704 (42%); 0.3333: 1018 (61%); 0.6667: 1381 (82%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1429, 0, 0.1429 | -0.1429: 1341 (80%); 0: 1200 (72%); 0.1429: 336 (20%) | -0.1429: 341 (20%); 0: 1222 (73%); 0.1429: 1343 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7444, -0.3303, 0, 1.1356 | -0.7444: 1339 (80%); -0.3303: 1006 (60%); 0: 899 (54%); 1.1356: 337 (20%) | -0.7444: 335 (20%); -0.3303: 676 (40%); 0: 1021 (61%); 1.1356: 1342 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 6, 10 | 2: 1408 (84%); 4: 1038 (62%); 6: 772 (46%); 10: 382 (23%) | 2: 450 (27%); 4: 768 (46%); 6: 1019 (61%); 10: 1354 (81%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0275, -0.0064, 0.0106, 0.0343 | -0.0275: 1339 (80%); -0.0064: 1004 (60%); 0.0106: 671 (40%); 0.0343: 335 (20%) | -0.0275: 335 (20%); -0.0064: 670 (40%); 0.0106: 1003 (60%); 0.0343: 1339 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0156, 0.0157, 0.0424, 0.0795 | -0.0156: 1338 (80%); 0.0157: 1005 (60%); 0.0424: 669 (40%); 0.0795: 335 (20%) | -0.0156: 336 (20%); 0.0157: 669 (40%); 0.0424: 1005 (60%); 0.0795: 1339 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0389, -0.0238, -0.0131, -0 | -0.0389: 1342 (80%); -0.0238: 1004 (60%); -0.0131: 668 (40%); -0: 335 (20%) | -0.0389: 333 (20%); -0.0238: 670 (40%); -0.0131: 1006 (60%); -0: 1346 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 99.9% | -3.3524, -2.2982, -1.5918, -0.9784 | -3.3524: 1338 (80%); -2.2982: 1004 (60%); -1.5918: 669 (40%); -0.9784: 335 (20%) | -3.3524: 335 (20%); -2.2982: 669 (40%); -1.5918: 1004 (60%); -0.9784: 1338 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 99.3% | 2.9202, 7.3162, 12.2786, 19.8214 | 2.9202: 1329 (79%); 7.3162: 997 (60%); 12.2786: 665 (40%); 19.8214: 333 (20%) | 2.9202: 333 (20%); 7.3162: 665 (40%); 12.2786: 997 (60%); 19.8214: 1329 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 99.9% | 0.0184, 1.855, 3.6218, 6.0564 | 0.0184: 1337 (80%); 1.855: 1004 (60%); 3.6218: 669 (40%); 6.0564: 335 (20%) | 0.0184: 335 (20%); 1.855: 670 (40%); 3.6218: 1003 (60%); 6.0564: 1337 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -5.4144, 7.715, 19.9254, 40.6542 | -5.4144: 1339 (80%); 7.715: 1004 (60%); 19.9254: 670 (40%); 40.6542: 335 (20%) | -5.4144: 335 (20%); 7.715: 670 (40%); 19.9254: 1004 (60%); 40.6542: 1339 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0329, 0.0428, 0.0551, 0.0751 | 0.0329: 1342 (80%); 0.0428: 1007 (60%); 0.0551: 670 (40%); 0.0751: 336 (20%) | 0.0329: 336 (20%); 0.0428: 671 (40%); 0.0551: 1006 (60%); 0.0751: 1339 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1225, 0.2267, 0.3351, 0.4785 | 0.1225: 1339 (80%); 0.2267: 1005 (60%); 0.3351: 670 (40%); 0.4785: 335 (20%) | 0.1225: 336 (20%); 0.2267: 671 (40%); 0.3351: 1005 (60%); 0.4785: 1339 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 0.4274, 1.1001, 1.7002, 2.557 | 0.4274: 1339 (80%); 1.1001: 1004 (60%); 1.7002: 670 (40%); 2.557: 335 (20%) | 0.4274: 335 (20%); 1.1001: 670 (40%); 1.7002: 1004 (60%); 2.557: 1339 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.4797, -0.2328, 0.0211, 0.3121 | -0.4797: 1339 (80%); -0.2328: 1005 (60%); 0.0211: 670 (40%); 0.3121: 335 (20%) | -0.4797: 335 (20%); -0.2328: 670 (40%); 0.0211: 1004 (60%); 0.3121: 1339 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | 0.4684, 1.211, 1.831, 2.6882 | 0.4684: 1339 (80%); 1.211: 1004 (60%); 1.831: 670 (40%); 2.6882: 335 (20%) | 0.4684: 335 (20%); 1.211: 670 (40%); 1.831: 1004 (60%); 2.6882: 1339 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -2.4016, -0.244, 1.7726, 4.536 | -2.4016: 1339 (80%); -0.244: 1004 (60%); 1.7726: 670 (40%); 4.536: 335 (20%) | -2.4016: 335 (20%); -0.244: 670 (40%); 1.7726: 1004 (60%); 4.536: 1339 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 5.546, 8.732, 12.568, 19.314 | 5.546: 1339 (80%); 8.732: 1004 (60%); 12.568: 670 (40%); 19.314: 335 (20%) | 5.546: 335 (20%); 8.732: 670 (40%); 12.568: 1004 (60%); 19.314: 1339 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 48.65, 51.912, 55.308, 59.128 | 48.65: 1340 (80%); 51.912: 1004 (60%); 55.308: 670 (40%); 59.128: 335 (20%) | 48.65: 336 (20%); 51.912: 670 (40%); 55.308: 1004 (60%); 59.128: 1339 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 40.236, 45.666, 50.736, 56.566 | 40.236: 1339 (80%); 45.666: 1004 (60%); 50.736: 670 (40%); 56.566: 335 (20%) | 40.236: 335 (20%); 45.666: 670 (40%); 50.736: 1004 (60%); 56.566: 1339 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 1670 (100%) | 0: 1674 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0295, 0.0395, 0.0538, 0.0736 | 0.0295: 1339 (80%); 0.0395: 1006 (60%); 0.0538: 673 (40%); 0.0736: 335 (20%) | 0.0295: 335 (20%); 0.0395: 673 (40%); 0.0538: 1005 (60%); 0.0736: 1339 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0698, -0.0548, -0.0421, -0.0316 | -0.0698: 1343 (80%); -0.0548: 1006 (60%); -0.0421: 671 (40%); -0.0316: 339 (20%) | -0.0698: 337 (20%); -0.0548: 676 (40%); -0.0421: 1007 (60%); -0.0316: 1351 (81%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1, 3 | 0: 1674 (100%); 1: 741 (44%); 3: 389 (23%) | 0: 933 (56%); 1: 1154 (69%); 3: 1355 (81%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.7% | 33, 48, 59, 71 | 33: 1361 (81%); 48: 1006 (60%); 59: 669 (40%); 71: 339 (20%) | 33: 363 (22%); 48: 687 (41%); 59: 1027 (61%); 71: 1347 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 99.0% | 0.0107, 0.0156, 0.0216, 0.0339 | 0.0107: 1329 (79%); 0.0156: 993 (59%); 0.0216: 663 (40%); 0.0339: 333 (20%) | 0.0107: 330 (20%); 0.0156: 665 (40%); 0.0216: 995 (59%); 0.0339: 1325 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.4808, 0.6238, 0.7235, 0.803 | 0.4808: 1339 (80%); 0.6238: 1005 (60%); 0.7235: 670 (40%); 0.803: 336 (20%) | 0.4808: 336 (20%); 0.6238: 670 (40%); 0.7235: 1005 (60%); 0.803: 1339 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 31.52, 69.04, 103.56, 164.04 | 31.52: 1339 (80%); 69.04: 1004 (60%); 103.56: 670 (40%); 164.04: 335 (20%) | 31.52: 335 (20%); 69.04: 670 (40%); 103.56: 1004 (60%); 164.04: 1339 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -2.379, -0.396, 0.835, 3.1798 | -2.379: 1339 (80%); -0.396: 1004 (60%); 0.835: 671 (40%); 3.1798: 335 (20%) | -2.379: 335 (20%); -0.396: 670 (40%); 0.835: 1005 (60%); 3.1798: 1339 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 47.098, 62.698, 73.83, 81.572 | 47.098: 1339 (80%); 62.698: 1004 (60%); 73.83: 671 (40%); 81.572: 335 (20%) | 47.098: 335 (20%); 62.698: 670 (40%); 73.83: 1005 (60%); 81.572: 1339 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 32.74, 50.696, 63.29, 73.154 | 32.74: 1340 (80%); 50.696: 1004 (60%); 63.29: 670 (40%); 73.154: 335 (20%) | 32.74: 336 (20%); 50.696: 670 (40%); 63.29: 1004 (60%); 73.154: 1339 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 5.646, 23.982, 52.618, 75.614 | 5.646: 1339 (80%); 23.982: 1004 (60%); 52.618: 670 (40%); 75.614: 335 (20%) | 5.646: 335 (20%); 23.982: 670 (40%); 52.618: 1004 (60%); 75.614: 1339 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 3.944, 35.848, 67.146 | 0: 1674 (100%); 3.944: 1004 (60%); 35.848: 670 (40%); 67.146: 335 (20%) | 0: 618 (37%); 3.944: 670 (40%); 35.848: 1004 (60%); 67.146: 1339 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 13, 17 | 4: 1384 (83%); 9: 1034 (62%); 13: 739 (44%); 17: 399 (24%) | 4: 359 (21%); 9: 692 (41%); 13: 1020 (61%); 17: 1371 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 18 | 5: 1358 (81%); 9: 1018 (61%); 13: 681 (41%); 18: 359 (21%) | 5: 373 (22%); 9: 758 (45%); 13: 1045 (62%); 18: 1383 (83%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 42.692, 47.51, 51.33, 55.6 | 42.692: 1339 (80%); 47.51: 1005 (60%); 51.33: 672 (40%); 55.6: 335 (20%) | 42.692: 335 (20%); 47.51: 671 (40%); 51.33: 1005 (60%); 55.6: 1339 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1349, 0.3413, 0.5794, 0.8016 | 0.1349: 1340 (80%); 0.3413: 1025 (61%); 0.5794: 678 (41%); 0.8016: 337 (20%) | 0.1349: 339 (20%); 0.3413: 677 (40%); 0.5794: 1019 (61%); 0.8016: 1345 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.238, 16.36, 18.48, 21.71 | 14.238: 1339 (80%); 16.36: 1007 (60%); 18.48: 673 (40%); 21.71: 341 (20%) | 14.238: 335 (20%); 16.36: 672 (40%); 18.48: 1008 (60%); 21.71: 1342 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.238, 16.36, 18.48, 21.71 | 14.238: 1339 (80%); 16.36: 1007 (60%); 18.48: 673 (40%); 21.71: 341 (20%) | 14.238: 335 (20%); 16.36: 672 (40%); 18.48: 1008 (60%); 21.71: 1342 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8477, 0.8753, 0.9086, 0.9469 | 0.8477: 1342 (80%); 0.8753: 1013 (61%); 0.9086: 673 (40%); 0.9469: 338 (20%) | 0.8477: 336 (20%); 0.8753: 680 (41%); 0.9086: 1007 (60%); 0.9469: 1340 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.68, 0.8, 0.93, 1.1 | 0.68: 1343 (80%); 0.8: 1006 (60%); 0.93: 678 (41%); 1.1: 336 (20%) | 0.68: 360 (22%); 0.8: 696 (42%); 0.93: 1015 (61%); 1.1: 1352 (81%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0135, 0.0321, 0.063, 0.1162 | 0.0135: 1341 (80%); 0.0321: 1005 (60%); 0.063: 670 (40%); 0.1162: 335 (20%) | 0.0135: 337 (20%); 0.0321: 671 (40%); 0.063: 1005 (60%); 0.1162: 1339 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 47.9199, 81.1457, 130.0013, 212.5719 | 47.9199: 1339 (80%); 81.1457: 1004 (60%); 130.0013: 670 (40%); 212.5719: 335 (20%) | 47.9199: 335 (20%); 81.1457: 670 (40%); 130.0013: 1004 (60%); 212.5719: 1339 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 45.3729, 78.2665, 125.3079, 205.4401 | 45.3729: 1339 (80%); 78.2665: 1004 (60%); 125.3079: 670 (40%); 205.4401: 335 (20%) | 45.3729: 335 (20%); 78.2665: 670 (40%); 125.3079: 1004 (60%); 205.4401: 1339 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 43.7381, 74.9824, 120.6759, 195.5192 | 43.7381: 1339 (80%); 74.9824: 1004 (60%); 120.6759: 670 (40%); 195.5192: 335 (20%) | 43.7381: 335 (20%); 74.9824: 670 (40%); 120.6759: 1004 (60%); 195.5192: 1339 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1674 (100%) | 0: 1470 (88%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1674 (100%) | 0: 1554 (93%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0185, 0.0072, 0.034, 0.0677 | -0.0185: 1339 (80%); 0.0072: 1005 (60%); 0.034: 672 (40%); 0.0677: 336 (20%) | -0.0185: 336 (20%); 0.0072: 670 (40%); 0.034: 1005 (60%); 0.0677: 1340 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -83.338, -66.392, -49.41, -37.656 | -83.338: 1339 (80%); -66.392: 1004 (60%); -49.41: 671 (40%); -37.656: 335 (20%) | -83.338: 335 (20%); -66.392: 670 (40%); -49.41: 1005 (60%); -37.656: 1339 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.2% | 0.4953, 0.7743, 0.9875, 1.2862 | 0.4953: 1329 (79%); 0.7743: 997 (60%); 0.9875: 665 (40%); 1.2862: 333 (20%) | 0.4953: 333 (20%); 0.7743: 665 (40%); 0.9875: 997 (60%); 1.2862: 1329 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 1349 (81%); 5: 1036 (62%); 7: 709 (42%); 9: 380 (23%) | 3: 464 (28%); 5: 803 (48%); 7: 1126 (67%); 9: 1463 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.2% | 0.1788, 0.2143, 0.2565, 0.3295 | 0.1788: 1330 (79%); 0.2143: 996 (59%); 0.2565: 665 (40%); 0.3295: 333 (20%) | 0.1788: 334 (20%); 0.2143: 664 (40%); 0.2565: 996 (59%); 0.3295: 1329 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.2% | 3, 5, 7, 9 | 3: 1357 (81%); 5: 1020 (61%); 7: 695 (42%); 9: 363 (22%) | 3: 475 (28%); 5: 802 (48%); 7: 1114 (67%); 9: 1460 (87%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.2% | 0.0224, 0.0306, 0.0418, 0.0604 | 0.0224: 1331 (80%); 0.0306: 1002 (60%); 0.0418: 665 (40%); 0.0604: 333 (20%) | 0.0224: 333 (20%); 0.0306: 666 (40%); 0.0418: 999 (60%); 0.0604: 1329 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 1380 (82%); 5: 1123 (67%); 7: 814 (49%); 9: 470 (28%) | 3: 393 (23%); 5: 687 (41%); 7: 1010 (60%); 9: 1402 (84%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.5% | -0.0984, 0.0413, 0.17, 0.3592 | -0.0984: 1332 (80%); 0.0413: 999 (60%); 0.17: 666 (40%); 0.3592: 333 (20%) | -0.0984: 333 (20%); 0.0413: 666 (40%); 0.17: 999 (60%); 0.3592: 1332 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.5% | 3, 5, 7, 9 | 3: 1437 (86%); 5: 1148 (69%); 7: 814 (49%); 9: 465 (28%) | 3: 370 (22%); 5: 679 (41%); 7: 1015 (61%); 9: 1406 (84%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 8.0% |
| 8k_item_5_02_filed_within_7d | 3.8% |
| above_avwap_20high | 3.5% |
| above_avwap_20low | 50.4% |
| above_avwap_252low | 90.3% |
| above_avwap_50low | 80.1% |
| above_cpr | 1.4% |
| above_pivot | 0.9% |
| above_prev_low | 30.8% |
| above_vwap | 72.4% |
| above_wood_p | 0.1% |
| ad_rising | 15.9% |
| adx_cross_up | 0.2% |
| adx_cross_up_20 | 0.4% |
| adx_di_bear | 37.4% |
| adx_di_bull | 62.6% |
| adx_strong | 10.5% |
| adx_trending | 46.5% |
| ao_cross_dn | 1.9% |
| ao_cross_up | 0.3% |
| ao_positive | 87.5% |
| ao_twin_peaks_bull | 0.5% |
| at_key_fib | 20.7% |
| at_key_fib_wide | 45.3% |
| avwap_20high_loss_recent_3d | 42.9% |
| avwap_20high_reclaim_recent_3d | 0.1% |
| avwap_20low_loss_recent_3d | 44.1% |
| avwap_20low_reclaim_recent_3d | 0.1% |
| avwap_252low_loss_recent_3d | 5.8% |
| avwap_50low_loss_recent_3d | 18.4% |
| avwap_50low_reclaim_recent_3d | 0.1% |
| bb_10_20_above_mid | 20.2% |
| bb_10_20_expanding | 43.1% |
| bb_10_20_pctb_lt_05 | 12.5% |
| bb_10_20_pctb_lt_1 | 22.8% |
| bb_10_20_pctb_lt_15 | 31.4% |
| bb_10_20_pctb_lt_2 | 40.3% |
| bb_10_20_pctb_lt_25 | 46.8% |
| bb_10_20_reclaim_from_lower_recent_3d | 4.5% |
| bb_10_20_reclaim_from_upper_recent_3d | 7.8% |
| bb_10_20_squeeze | 60.3% |
| bb_10_20_touch_lower | 19.5% |
| bb_20_15_above_mid | 51.1% |
| bb_20_15_expanding | 30.3% |
| bb_20_15_pctb_gt_75 | 16.1% |
| bb_20_15_pctb_gt_8 | 8.9% |
| bb_20_15_pctb_gt_85 | 4.8% |
| bb_20_15_pctb_gt_9 | 2.2% |
| bb_20_15_pctb_gt_95 | 0.8% |
| bb_20_15_pctb_lt_05 | 13.4% |
| bb_20_15_pctb_lt_1 | 15.7% |
| bb_20_15_pctb_lt_15 | 18.8% |
| bb_20_15_pctb_lt_2 | 22.5% |
| bb_20_15_pctb_lt_25 | 26.9% |
| bb_20_15_reclaim_from_lower_recent_3d | 0.1% |
| bb_20_15_reclaim_from_upper_recent_3d | 38.4% |
| bb_20_15_squeeze | 48.5% |
| bb_20_15_touch_lower | 15.4% |
| bb_20_15_touch_upper | 1.0% |
| bb_20_20_above_mid | 51.1% |
| bb_20_20_expanding | 30.3% |
| bb_20_20_pctb_gt_75 | 5.7% |
| bb_20_20_pctb_gt_8 | 2.2% |
| bb_20_20_pctb_gt_85 | 0.7% |
| bb_20_20_pctb_gt_9 | 0.1% |
| bb_20_20_pctb_lt_05 | 5.1% |
| bb_20_20_pctb_lt_1 | 8.8% |
| bb_20_20_pctb_lt_15 | 12.1% |
| bb_20_20_pctb_lt_2 | 15.7% |
| bb_20_20_pctb_lt_25 | 20.4% |
| bb_20_20_reclaim_from_lower_recent_3d | 0.4% |
| bb_20_20_reclaim_from_upper_recent_3d | 15.4% |
| bb_20_20_squeeze | 29.5% |
| bb_20_20_touch_lower | 6.8% |
| bearish_pin_bar | 4.2% |
| below_avwap_20high | 96.5% |
| below_avwap_20low | 49.6% |
| below_avwap_252low | 9.7% |
| below_avwap_50low | 19.9% |
| below_cam_s3 | 64.0% |
| below_cam_s4 | 33.6% |
| below_cpr | 99.1% |
| below_ema_20 | 49.3% |
| below_ema_200 | 19.7% |
| below_ema_200_break_recent_5d | 9.0% |
| below_ema_20_break_recent_5d | 45.3% |
| below_ema_21 | 47.8% |
| below_ema_21_break_recent_5d | 43.9% |
| below_ema_50 | 23.1% |
| below_ema_50_break_recent_5d | 15.4% |
| below_ema_9 | 83.6% |
| below_ema_9_break_recent_5d | 79.6% |
| below_prev_low | 68.4% |
| below_prev_low_clearance_atr_05 | 18.0% |
| below_s1 | 45.9% |
| below_s2 | 18.5% |
| below_sma_20 | 48.9% |
| below_sma_200 | 20.4% |
| below_sma_21 | 47.3% |
| below_sma_50 | 22.3% |
| below_sma_9 | 84.1% |
| below_vwap | 27.6% |
| blowoff_recent_3d | 0.4% |
| bullish_pin_bar | 6.3% |
| ceo_buy | 0.6% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 76.2% |
| chandelier_long_flip_dn | 10.2% |
| chandelier_short_bearish | 56.0% |
| classification_change_from_tech | 66.7% |
| classification_change_to_defensive | 33.3% |
| close_in_bottom_40pct_of_range | 69.1% |
| close_in_top_40pct_of_range | 9.7% |
| cluster_buy | 0.4% |
| cmf_cross_dn | 5.9% |
| cmf_cross_up | 1.7% |
| cmf_negative | 38.7% |
| cmf_positive | 61.3% |
| concentrated_sell | 8.9% |
| cpr_narrow | 86.9% |
| cpr_narrow_tight | 25.7% |
| cup_handle_detected | 15.5% |
| cup_handle_neckline_break_retest_long | 6.1% |
| dc10_breakout_dn | 19.3% |
| dc10_breakout_dn_1pct | 32.3% |
| dc10_breakout_up_1pct | 0.2% |
| dc10_new_high | 0.2% |
| dc10_strong_breakout_dn | 3.0% |
| dc20_breakout_dn | 3.5% |
| dc20_new_high | 0.1% |
| dc20_resistance_break_retest_strong | 22.2% |
| dc20_support_break_retest_strong | 0.8% |
| defensive_leadership | 46.4% |
| director_only_buy | 2.1% |
| doji | 4.3% |
| double_bottom_detected | 14.0% |
| double_top_detected | 14.3% |
| dpi_elevated | 44.1% |
| drying_volume_on_down_turn | 70.0% |
| ema_20_50_bearish | 13.7% |
| ema_20_50_bullish | 86.3% |
| ema_20_50_death_cross | 0.4% |
| ema_20_50_golden_cross | 0.1% |
| ema_50_200_bearish | 24.0% |
| ema_50_200_bullish | 76.0% |
| ema_50_200_golden_cross | 0.4% |
| ema_9_21_bearish | 14.9% |
| ema_9_21_bullish | 85.1% |
| ema_9_21_death_cross | 4.2% |
| ema_9_21_golden_cross | 0.2% |
| flag_bear_detected | 0.1% |
| flag_bull_break_retest_long | 2.9% |
| flag_bull_broke | 2.9% |
| flag_bull_detected | 3.6% |
| force_index_cross_dn | 14.8% |
| force_index_positive | 43.7% |
| gap_dn_1_5pct | 5.1% |
| gap_dn_2pct | 2.6% |
| gap_up_1_5pct | 0.3% |
| gap_up_2pct | 0.1% |
| hammer | 6.0% |
| head_shoulders_bottom_detected | 3.8% |
| head_shoulders_top_detected | 2.9% |
| house_cluster_buy | 4.9% |
| house_cluster_sell | 4.7% |
| htf_aligned_bear | 10.3% |
| htf_aligned_bull | 64.0% |
| htf_disagreement | 1.4% |
| hull_bearish | 63.4% |
| hull_bullish | 36.6% |
| hull_flip_dn | 23.4% |
| hull_flip_up | 0.1% |
| ichi_above_cloud | 73.8% |
| ichi_above_cloud_break_recent_5d | 2.2% |
| ichi_below_cloud | 13.3% |
| ichi_below_cloud_break_recent_5d | 5.3% |
| ichi_cloud_thick | 85.3% |
| ichi_tk_bearish | 15.1% |
| ichi_tk_bullish | 82.5% |
| ichi_tk_cross_dn | 1.6% |
| ichi_tk_cross_up | 1.3% |
| ichi_weekly_above_cloud | 63.2% |
| ichi_weekly_below_cloud | 15.9% |
| ichi_weekly_in_cloud | 21.0% |
| in_reversal_window | 1.4% |
| inside_bar | 8.5% |
| inside_kc | 98.7% |
| insider_cluster_active | 25.4% |
| institutional_buy | 89.7% |
| institutional_negative | 4.6% |
| institutional_persistence_growing | 42.4% |
| institutional_persistence_strong | 60.3% |
| institutional_strong_buy | 80.5% |
| inverted_cup_handle_detected | 9.1% |
| is_friday | 18.2% |
| is_halloween_period | 52.4% |
| is_halloween_period_first_day | 0.2% |
| is_january | 9.9% |
| is_january_extended | 12.7% |
| is_monday | 17.1% |
| is_pre_holiday | 3.8% |
| is_summer_period | 47.6% |
| is_totm_window | 36.2% |
| is_totm_window_first_day | 9.4% |
| is_week_open | 19.7% |
| kc_touch_lower | 0.2% |
| kc_touch_upper | 2.1% |
| large_dollar_buy | 0.4% |
| macd_12_26_9_bearish | 56.2% |
| macd_12_26_9_bullish | 43.8% |
| macd_12_26_9_crossover_dn | 11.6% |
| macd_12_26_9_crossover_up | 0.1% |
| macd_8_21_5_bearish | 77.0% |
| macd_8_21_5_bullish | 23.0% |
| macd_8_21_5_crossover_dn | 12.7% |
| marubozu_bear | 0.4% |
| mfi_broad_overbought | 8.9% |
| mfi_broad_oversold | 2.8% |
| mfi_overbought | 1.0% |
| mfi_oversold | 0.4% |
| monthly_above_sma_12 | 78.7% |
| monthly_above_sma_6 | 79.8% |
| monthly_bias_bear | 14.1% |
| monthly_bias_bull | 72.6% |
| monthly_momentum_pos | 74.4% |
| near_52w_high | 2.3% |
| near_52w_high_95pct | 26.7% |
| near_52w_low | 0.1% |
| near_52w_low_105pct | 0.6% |
| near_52w_low_retest_short | 0.9% |
| near_avwap_20high_atr_05x | 19.7% |
| near_avwap_20high_atr_10x | 63.1% |
| near_avwap_20high_atr_15x | 89.2% |
| near_avwap_20high_atr_20x | 98.1% |
| near_avwap_20low_atr_05x | 43.8% |
| near_avwap_20low_atr_10x | 75.3% |
| near_avwap_20low_atr_15x | 92.5% |
| near_avwap_20low_atr_20x | 97.9% |
| near_avwap_252low_atr_05x | 6.4% |
| near_avwap_252low_atr_10x | 13.5% |
| near_avwap_252low_atr_15x | 20.1% |
| near_avwap_252low_atr_20x | 26.7% |
| near_avwap_50low_atr_05x | 24.6% |
| near_avwap_50low_atr_10x | 42.7% |
| near_avwap_50low_atr_15x | 57.1% |
| near_avwap_50low_atr_20x | 68.8% |
| near_cam_r3 | 0.3% |
| near_cam_s3 | 37.8% |
| near_cam_s4 | 23.8% |
| near_fib_236 | 14.3% |
| near_fib_382 | 10.9% |
| near_fib_500 | 6.2% |
| near_fib_618 | 3.7% |
| near_fib_786 | 2.4% |
| near_pivot | 5.5% |
| near_prev_close | 18.5% |
| near_prev_high | 0.1% |
| near_prev_low | 32.0% |
| near_r1 | 0.1% |
| near_r1_wide | 26.0% |
| near_r2 | 0.1% |
| near_r2_wide | 4.1% |
| near_s1 | 32.0% |
| near_s1_wide | 88.1% |
| near_s2 | 14.9% |
| near_s2_wide | 70.7% |
| near_s3 | 4.4% |
| near_wood_r1 | 0.1% |
| near_wood_s1 | 16.5% |
| news_uses_polygon_score | 24.6% |
| obv_bearish | 60.7% |
| obv_bullish | 39.3% |
| obv_diverge_bull | 4.0% |
| obv_falling | 92.4% |
| obv_rising | 7.6% |
| outside_bar | 3.9% |
| pead_negative_surprise | 9.3% |
| pead_positive_surprise | 31.7% |
| pin_bar | 10.5% |
| po3_accumulation_active | 52.2% |
| po3_bearish | 5.4% |
| po3_manipulation_sweep_down | 35.9% |
| po3_manipulation_sweep_up | 0.2% |
| po3_mmsm_setup | 0.2% |
| po3_sweep_above_prior_high | 8.3% |
| po3_sweep_below_prior_low | 91.9% |
| ppo_bullish | 42.0% |
| ppo_crossover_dn | 11.7% |
| ppo_crossover_up | 0.1% |
| pre_fomc_d0 | 2.6% |
| pre_fomc_d1 | 2.7% |
| pre_fomc_window | 5.4% |
| price_above_dema | 11.8% |
| price_above_ema_20 | 50.7% |
| price_above_ema_200 | 80.3% |
| price_above_ema_200_break_recent_5d | 1.1% |
| price_above_ema_20_break_recent_5d | 2.7% |
| price_above_ema_21 | 52.2% |
| price_above_ema_21_break_recent_5d | 2.6% |
| price_above_ema_50 | 76.9% |
| price_above_ema_50_break_recent_5d | 2.0% |
| price_above_ema_9 | 16.4% |
| price_above_ema_9_break_recent_5d | 2.3% |
| price_above_hull | 4.8% |
| price_above_sma_200 | 79.6% |
| price_above_sma_21 | 52.7% |
| price_above_sma_50 | 77.7% |
| price_above_tema | 6.2% |
| price_below_dema | 88.2% |
| price_below_hull | 95.2% |
| price_below_tema | 93.8% |
| psar_bullish | 46.5% |
| psar_flip_dn | 15.1% |
| r1_break_retest_long | 41.6% |
| recent_blowoff_at_r3 | 0.2% |
| resistance_break_retest | 26.9% |
| risk_off_regime_bond_signal | 15.7% |
| risk_off_regime_bond_signal_strong | 3.5% |
| risk_off_regime_gold_signal | 29.7% |
| risk_on_regime_bond_signal | 52.0% |
| risk_on_regime_bond_signal_strong | 22.4% |
| roc_positive | 57.8% |
| roc_turning_dn | 13.3% |
| roc_turning_up | 2.2% |
| rsi_14_bullish | 60.9% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 3.3% |
| rsi_14_cross_dn_overbought_recent_3d | 24.2% |
| rsi_14_overbought | 0.9% |
| rsi_21_bullish | 72.3% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.5% |
| rsi_21_cross_dn_overbought_recent_3d | 11.9% |
| rsi_21_overbought | 0.5% |
| rsi_2_bullish | 0.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 53.8% |
| rsi_2_cross_dn_overbought_recent_3d | 66.5% |
| rsi_2_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_2_cross_up_oversold_recent_3d | 0.4% |
| rsi_2_extreme_os | 81.1% |
| rsi_2_oversold | 93.8% |
| rsi_9_bullish | 44.0% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 10.1% |
| rsi_9_cross_dn_overbought_recent_3d | 39.4% |
| rsi_9_extreme_ob | 0.1% |
| rsi_9_overbought | 0.7% |
| rsi_9_oversold | 0.1% |
| s1_break_retest_short | 64.0% |
| sc_13d_filed_within_30d | 4.0% |
| sc_13g_filed_within_30d | 4.0% |
| sector_outperforming_spy | 37.8% |
| sector_underperforming_spy | 62.2% |
| shooting_star | 3.1% |
| sma_20_50_bullish | 80.8% |
| sma_20_50_golden_cross | 1.0% |
| sma_50_200_bullish | 71.0% |
| sma_50_200_golden_cross | 0.3% |
| sma_9_21_bullish | 82.6% |
| sma_9_21_golden_cross | 1.3% |
| smc_bos_bearish | 1.6% |
| smc_bos_bullish | 22.6% |
| smc_bos_retest_long | 5.5% |
| smc_bos_retest_short | 3.0% |
| smc_breaker_block_bearish | 6.6% |
| smc_breaker_block_bullish | 33.8% |
| smc_choch_bearish | 2.0% |
| smc_choch_bullish | 6.3% |
| smc_equal_highs_swept | 5.0% |
| smc_equal_lows_swept | 1.4% |
| smc_fvg_bearish_active | 68.5% |
| smc_fvg_bullish_active | 32.8% |
| smc_fvg_retest_long_zone | 12.2% |
| smc_fvg_retest_short_zone | 1.3% |
| smc_in_discount_zone | 34.7% |
| smc_in_premium_zone | 86.1% |
| smc_inverse_fvg_bearish | 81.5% |
| smc_inverse_fvg_bullish | 94.8% |
| smc_liquidity_swept_dn | 1.9% |
| smc_liquidity_swept_up | 0.5% |
| smc_mitigation_block_long | 0.4% |
| smc_mitigation_block_short | 1.4% |
| smc_ob_bearish_active | 12.1% |
| smc_ob_bullish_active | 56.0% |
| smc_ote_long_zone | 3.0% |
| smc_ote_short_zone | 10.5% |
| squeeze_fire_dn | 8.9% |
| squeeze_fire_up | 0.1% |
| squeeze_in | 26.9% |
| squeeze_positive | 54.2% |
| stoch_bearish_cross | 13.7% |
| stoch_broad_overbought | 15.9% |
| stoch_broad_oversold | 12.2% |
| stoch_bullish_cross | 0.1% |
| stoch_overbought | 7.4% |
| stoch_oversold | 8.4% |
| stochrsi_cross_dn | 36.0% |
| stochrsi_cross_up | 8.7% |
| stochrsi_overbought | 10.4% |
| stochrsi_oversold | 51.0% |
| supertrend_bearish | 0.2% |
| supertrend_bullish | 99.8% |
| supertrend_flip_dn | 0.1% |
| supertrend_flip_recent_long_5d | 0.2% |
| supertrend_flip_recent_short_5d | 0.2% |
| support_break_retest | 2.6% |
| tema_above_dema | 59.4% |
| tema_cross_dn | 6.5% |
| tema_cross_up | 0.3% |
| triangle_apex_break_retest_long | 21.3% |
| triangle_ascending_detected | 14.0% |
| triangle_descending_detected | 3.6% |
| uo_overbought | 0.1% |
| uo_oversold | 0.4% |
| usd_strengthening | 22.2% |
| usd_weakening | 10.0% |
| vix_band_high | 32.6% |
| vix_band_low | 37.8% |
| vix_band_mid | 29.6% |
| vix_term_backwardation | 4.3% |
| vix_term_contango | 95.7% |
| vol_above_avg | 30.0% |
| vol_below_avg | 70.0% |
| vol_spike_12x | 13.4% |
| vol_spike_15x | 4.8% |
| vol_spike_17x | 2.4% |
| vol_spike_2x | 0.9% |
| vol_spike_2x_on_down_day_recent_3d | 2.4% |
| vol_spike_2x_on_up_day_recent_3d | 1.4% |
| vol_spike_3x | 0.2% |
| vp_above_value_area | 35.2% |
| vp_below_value_area | 4.0% |
| vp_close_above_poc | 70.1% |
| vp_close_below_poc | 29.9% |
| vp_in_value_area | 60.8% |
| week_open_gap_down_15pct | 1.6% |
| week_open_gap_up_15pct | 0.1% |
| weekly_above_ema_10 | 75.7% |
| weekly_above_ema_20 | 80.6% |
| weekly_bias_bear | 15.7% |
| weekly_bias_bull | 72.0% |
| weekly_momentum_pos | 65.6% |
| williams_r_overbought | 2.0% |
| williams_r_oversold | 24.5% |
| williams_r_rising | 6.5% |
| within_pead_window | 41.2% |
| within_post_inclusion_window | 1.8% |
| within_pre_rebalance_window | 0.8% |
| xs_avoid_high_ivol | 78.1% |
| xs_avoid_high_max | 71.7% |
| xs_high_beta_decile | 22.9% |
| xs_low_beta_bottom_quintile | 22.9% |
| xs_low_beta_decile | 18.8% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 18.8% |
| xs_momentum_bottom_decile | 4.4% |
| xs_momentum_bottom_quintile | 13.7% |
| xs_momentum_top_decile | 15.6% |
| xs_momentum_top_quintile | 27.9% |
| xs_quality_bottom_quintile | 19.5% |
| xs_quality_top_quintile | 20.2% |
| xs_quality_top_tercile | 41.3% |
| year_high_break_retest_long | 5.9% |
| yoy_surprise_high | 62.6% |
| yoy_surprise_negative | 27.0% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.6% |
| committed_growth_holders | 91.6% |
| corp_donations_1y | 11.6% |
| corp_donations_count_1y | 11.6% |
| corp_donations_unique_pacs | 11.6% |
| cot_rut_commercials_pctile_3y | 60.8% |
| cot_rut_mmoney_pctile_3y | 60.8% |
| cup_handle_depth_pct | 19.6% |
| days_since_classification_change | 0.4% |
| days_since_deletion | 6.5% |
| days_since_inclusion | 13.1% |
| days_to_next_holiday | 62.2% |
| days_to_rebalance | 7.5% |
| dpi_30d_avg | 95.4% |
| dpi_recent | 95.4% |
| earnings_announcement_return | 93.1% |
| earnings_eps_yoy_growth | 95.3% |
| flag_bull_pole_move_pct | 3.6% |
| gov_contracts_4q_sum | 41.3% |
| gov_contracts_last_qtr_amount | 41.3% |
| gov_contracts_qoq_growth | 41.3% |
| head_shoulders_magnitude_pct | 6.5% |
| insider_director_buyers_30d | 3.5% |
| insider_officer_buyers_30d | 3.5% |
| insider_total_shares_bought_30d | 3.5% |
| insider_unique_buyers_30d | 3.5% |
| inverted_cup_handle_height_pct | 15.4% |
| lobbying_amount_1y | 71.3% |
| lobbying_amount_q | 71.3% |
| lobbying_amount_yoy | 71.3% |
| otc_short_ratio_recent | 95.4% |
| otc_volume_recent | 95.4% |
| pair_half_life | 92.2% |
| pair_max_abs_zscore | 92.2% |
| pair_zscore_signed | 92.2% |
| pct_from_avwap_20low | 93.2% |
| persistent_holders_4q | 91.6% |
| persistent_holders_8q | 91.6% |
| sc_13g_latest_percent_owned | 2.1% |
| search_volume_index_recent | 78.4% |
| search_volume_observations | 78.4% |
| search_volume_zscore_30d | 78.4% |
| sector_etf_return_20d | 2.2% |
| spy_return_20d | 2.2% |
| total_active_holders | 91.6% |
| triangle_breakdown_pct | 3.6% |
| triangle_breakout_pct | 14.0% |
| xs_quality_decile | 61.4% |
| xs_quality_gross_profitability | 61.4% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.994), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (1.0), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (1.0), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.998), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.999), `entry_stop_short` (0.999), `fib_236` (0.999), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.998), `fib_786` (0.997), `fib_ext_127` (0.997), `fib_ext_162` (0.996), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.994), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.99), `monthly_sma_6` (0.997), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.999), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.999), `swing_high` (0.998), `swing_low` (0.995), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.998), `vp_value_area_low` (0.995), `vwap_upper_1` (0.951), `vwap_upper_2` (0.954), `weekly_close` (0.999), `weekly_ema_10` (1.0), `weekly_ema_20` (0.998), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.988), `year_low` (0.967)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
