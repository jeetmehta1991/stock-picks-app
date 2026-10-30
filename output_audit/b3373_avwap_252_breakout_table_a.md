# Table A - avwap_252_breakout

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build ff10274b7 | commit ff10274b7 at 2026-10-30 10:37:35 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** vwap | **status:** NOT-STARTED | **R5 fires:** 2294 (closed fires in the exit cube: 2294 of 2294, S6-B3258) | **surviving fires (T1):** 2294 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  avwap_252low_loss_recent_3d  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define
P2  avwap_252low_reclaim_recent_3d  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define
P3  vol_above_avg  <- backtest/signals/technical.py
       DEFN: volume / 20d average >= 1.0 (technical.py:1600)
       knobs P3.1-P3.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P4  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_avwap_252_breakout (docstring and return dropped):

```python
reclaim_252_long = s.get('avwap_252low_reclaim_recent_3d', False)
loss_252_short = s.get('avwap_252low_loss_recent_3d', False)
vol_ok = s.get('vol_above_avg', False)
rsi_14 = s.get('rsi_14', 50)
fl = reclaim_252_long and vol_ok
fs = loss_252_short and vol_ok and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | avwap_252low_loss_recent_3d - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs to define | BANDS-TO-DEFINE |
| P2 | PRODUCER | avwap_252low_reclaim_recent_3d - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs to define | BANDS-TO-DEFINE |
| P3 | PRODUCER | vol_above_avg - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average >= 1.0 (technical.py:1600) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | volume ratio floor (vol / avg) - backtest/signals/technical.py:1600 | BRACKET production 1.0; avg window is the second knob [10, 20, 50] | 1.0 | [1.0, 1.2, 1.5, 2.0] | offline 3 of 4 levels - TIGHTER floors where the vol ratio key is persisted on the fires; else none | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 17.19, 21.202, 25.528, 32.362 | 17.19: 1836 (80%); 21.202: 1376 (60%); 25.528: 918 (40%); 32.362: 459 (20%) | 17.19: 460 (20%); 21.202: 918 (40%); 25.528: 1376 (60%); 32.362: 1835 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 22.566, 27.082, 30.908, 35.748 | 22.566: 1835 (80%); 27.082: 1376 (60%); 30.908: 918 (40%); 35.748: 459 (20%) | 22.566: 459 (20%); 27.082: 918 (40%); 30.908: 1376 (60%); 35.748: 1835 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.246, 16.43, 20.04, 24.862 | 13.246: 1835 (80%); 16.43: 1378 (60%); 20.04: 919 (40%); 24.862: 459 (20%) | 13.246: 459 (20%); 16.43: 919 (40%); 20.04: 1378 (60%); 24.862: 1835 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -10.0503, -4.344, -1.6847, -0.0906 | -10.0503: 1835 (80%); -4.344: 1376 (60%); -1.6847: 918 (40%); -0.0906: 459 (20%) | -10.0503: 459 (20%); -4.344: 918 (40%); -1.6847: 1376 (60%); -0.0906: 1835 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.1903, 2.1835, 3.6629, 6.4834 | 1.1903: 1835 (80%); 2.1835: 1376 (60%); 3.6629: 918 (40%); 6.4834: 459 (20%) | 1.1903: 459 (20%); 2.1835: 918 (40%); 3.6629: 1376 (60%); 6.4834: 1835 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.1903, 2.1835, 3.6629, 6.4834 | 1.1903: 1835 (80%); 2.1835: 1376 (60%); 3.6629: 918 (40%); 6.4834: 459 (20%) | 1.1903: 459 (20%); 2.1835: 918 (40%); 3.6629: 1376 (60%); 6.4834: 1835 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.474, 3.0564, 3.7634, 4.8914 | 2.474: 1836 (80%); 3.0564: 1376 (60%); 3.7634: 918 (40%); 4.8914: 459 (20%) | 2.474: 460 (20%); 3.0564: 918 (40%); 3.7634: 1376 (60%); 4.8914: 1835 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0759, 0.114, 0.1617, 0.2331 | 0.0759: 1836 (80%); 0.114: 1376 (60%); 0.1617: 918 (40%); 0.2331: 459 (20%) | 0.0759: 460 (20%); 0.114: 918 (40%); 0.1617: 1377 (60%); 0.2331: 1835 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1357, 0.2833, 0.4709, 0.7823 | 0.1357: 1835 (80%); 0.2833: 1378 (60%); 0.4709: 918 (40%); 0.7823: 460 (20%) | 0.1357: 459 (20%); 0.2833: 918 (40%); 0.4709: 1377 (60%); 0.7823: 1835 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0729, 0.1032, 0.1346, 0.184 | 0.0729: 1837 (80%); 0.1032: 1381 (60%); 0.1346: 920 (40%); 0.184: 461 (20%) | 0.0729: 460 (20%); 0.1032: 918 (40%); 0.1346: 1378 (60%); 0.184: 1836 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | -0.1137, 0.1019, 0.3189, 0.6511 | -0.1137: 1835 (80%); 0.1019: 1376 (60%); 0.3189: 918 (40%); 0.6511: 459 (20%) | -0.1137: 459 (20%); 0.1019: 918 (40%); 0.3189: 1376 (60%); 0.6511: 1835 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0973, 0.1377, 0.1795, 0.2454 | 0.0973: 1835 (80%); 0.1377: 1377 (60%); 0.1795: 919 (40%); 0.2454: 460 (20%) | 0.0973: 460 (20%); 0.1377: 919 (40%); 0.1795: 1378 (60%); 0.2454: 1837 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.0397, 0.2014, 0.3642, 0.6133 | 0.0397: 1835 (80%); 0.2014: 1376 (60%); 0.3642: 918 (40%); 0.6133: 459 (20%) | 0.0397: 459 (20%); 0.2014: 918 (40%); 0.3642: 1376 (60%); 0.6133: 1835 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0423, -0.0128, 0.0049, 0.0266 | -0.0423: 1836 (80%); -0.0128: 1384 (60%); 0.0049: 918 (40%); 0.0266: 460 (20%) | -0.0423: 470 (20%); -0.0128: 918 (40%); 0.0049: 1382 (60%); 0.0266: 1837 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1457, 0.1647, 0.2021, 0.2712 | 0.1457: 1835 (80%); 0.1647: 1381 (60%); 0.2021: 916 (40%); 0.2712: 459 (20%) | 0.1457: 459 (20%); 0.1647: 913 (40%); 0.2021: 1378 (60%); 0.2712: 1835 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 2294 (100%) | 0: 2166 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1427, -0.0637, -0, 0.0852 | -0.1427: 1835 (80%); -0.0637: 1377 (60%); -0: 918 (40%); 0.0852: 461 (20%) | -0.1427: 459 (20%); -0.0637: 918 (40%); -0: 1381 (60%); 0.0852: 1835 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 2294 (100%); 1: 830 (36%) | 0: 1464 (64%); 1: 1919 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2289, -0.1642, -0.1375, -0.1141 | -0.2289: 1843 (80%); -0.1642: 1378 (60%); -0.1375: 952 (41%); -0.1141: 726 (32%) | -0.2289: 462 (20%); -0.1642: 920 (40%); -0.1375: 1383 (60%); -0.1141: 1863 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4615, 0.6603, 0.7564, 0.7911 | 0.4615: 1841 (80%); 0.6603: 1381 (60%); 0.7564: 930 (41%); 0.7911: 459 (20%) | 0.4615: 488 (21%); 0.6603: 935 (41%); 0.7564: 1449 (63%); 0.7911: 1835 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.3526, 0.5897, 0.8269 | 0.2564: 1845 (80%); 0.3526: 1394 (61%); 0.5897: 1091 (48%); 0.8269: 468 (20%) | 0.2564: 510 (22%); 0.3526: 922 (40%); 0.5897: 1502 (65%); 0.8269: 1862 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0546, 0.0167, 0.0842, 0.2047 | -0.0546: 1844 (80%); 0.0167: 1461 (64%); 0.0842: 919 (40%); 0.2047: 464 (20%) | -0.0546: 463 (20%); 0.0167: 1128 (49%); 0.0842: 1389 (61%); 0.2047: 1852 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3718, 0.4872, 0.6154, 0.7885 | 0.3718: 1846 (80%); 0.4872: 1492 (65%); 0.6154: 935 (41%); 0.7885: 465 (20%) | 0.3718: 498 (22%); 0.4872: 1104 (48%); 0.6154: 1389 (61%); 0.7885: 1838 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3526, 0.4551, 0.6026 | 0.1474: 1841 (80%); 0.3526: 1407 (61%); 0.4551: 1122 (49%); 0.6026: 469 (20%) | 0.1474: 492 (21%); 0.3526: 984 (43%); 0.4551: 1486 (65%); 0.6026: 1836 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.521, -0.352, -0.1224, 0.0029 | -0.521: 1836 (80%); -0.352: 1378 (60%); -0.1224: 922 (40%); 0.0029: 469 (20%) | -0.521: 462 (20%); -0.352: 920 (40%); -0.1224: 1378 (60%); 0.0029: 1849 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3013, 0.5128, 0.7436, 0.8846 | 0.3013: 1846 (80%); 0.5128: 1392 (61%); 0.7436: 932 (41%); 0.8846: 474 (21%) | 0.3013: 472 (21%); 0.5128: 922 (40%); 0.7436: 1380 (60%); 0.8846: 1838 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.141, 0.4103, 0.6603, 0.8526 | 0.141: 1844 (80%); 0.4103: 1379 (60%); 0.6603: 933 (41%); 0.8526: 601 (26%) | 0.141: 470 (20%); 0.4103: 921 (40%); 0.6603: 1381 (60%); 0.8526: 1988 (87%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0645, -0.0478, -0.022, 0 | -0.0645: 1837 (80%); -0.0478: 1383 (60%); -0.022: 972 (42%); 0: 862 (38%) | -0.0645: 469 (20%); -0.0478: 920 (40%); -0.022: 1379 (60%); 0: 2244 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4846, 0.8141, 0.9038, 1 | 0.4846: 1835 (80%); 0.8141: 1383 (60%); 0.9038: 1022 (45%); 1: 730 (32%) | 0.4846: 459 (20%); 0.8141: 929 (40%); 0.9038: 1382 (60%); 1: 2294 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0833, 0.2179, 0.3205, 0.7179 | 0.0833: 1910 (83%); 0.2179: 1381 (60%); 0.3205: 1222 (53%); 0.7179: 460 (20%) | 0.0833: 482 (21%); 0.2179: 920 (40%); 0.3205: 1385 (60%); 0.7179: 1854 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0027, 0.0402, 0.1133, 0.2489 | 0.0027: 1844 (80%); 0.0402: 1390 (61%); 0.1133: 918 (40%); 0.2489: 614 (27%) | 0.0027: 472 (21%); 0.0402: 921 (40%); 0.1133: 1376 (60%); 0.2489: 1975 (86%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.5625, 0.7979, 0.9545, 0.9744 | 0.5625: 1850 (81%); 0.7979: 1389 (61%); 0.9545: 940 (41%); 0.9744: 697 (30%) | 0.5625: 463 (20%); 0.7979: 919 (40%); 0.9545: 1377 (60%); 0.9744: 1961 (85%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0843, 0.2436, 0.4282, 0.7266 | 0.0843: 1864 (81%); 0.2436: 1378 (60%); 0.4282: 918 (40%); 0.7266: 460 (20%) | 0.0843: 481 (21%); 0.2436: 924 (40%); 0.4282: 1376 (60%); 0.7266: 1840 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1386, -0.0183, 0.1131, 0.3175 | -0.1386: 1844 (80%); -0.0183: 1380 (60%); 0.1131: 920 (40%); 0.3175: 473 (21%) | -0.1386: 468 (20%); -0.0183: 920 (40%); 0.1131: 1380 (60%); 0.3175: 2214 (97%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.3207, -0.0294, 0.0444, 0.0848 | -0.3207: 1844 (80%); -0.0294: 1382 (60%); 0.0444: 937 (41%); 0.0848: 474 (21%) | -0.3207: 461 (20%); -0.0294: 920 (40%); 0.0444: 1386 (60%); 0.0848: 1845 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.5321, 0.7372, 0.859 | 0.2628: 1991 (87%); 0.5321: 1387 (60%); 0.7372: 930 (41%); 0.859: 465 (20%) | 0.2628: 598 (26%); 0.5321: 924 (40%); 0.7372: 1400 (61%); 0.859: 1849 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.141, 0.3846, 0.5641, 0.7885 | 0.141: 1841 (80%); 0.3846: 1398 (61%); 0.5641: 1104 (48%); 0.7885: 477 (21%) | 0.141: 461 (20%); 0.3846: 937 (41%); 0.5641: 1495 (65%); 0.7885: 1842 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0675, 0.1767, 0.3715, 0.7828 | 0.0675: 1836 (80%); 0.1767: 1382 (60%); 0.3715: 918 (40%); 0.7828: 459 (20%) | 0.0675: 461 (20%); 0.1767: 919 (40%); 0.3715: 1376 (60%); 0.7828: 1835 (80%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.4% | 1.8424, 2.3747, 2.9639, 4.0229 | 1.8424: 1825 (80%); 2.3747: 1370 (60%); 2.9639: 913 (40%); 4.0229: 457 (20%) | 1.8424: 457 (20%); 2.3747: 913 (40%); 2.9639: 1369 (60%); 4.0229: 1825 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 8, 19, 28, 35 | 8: 1862 (81%); 19: 1407 (61%); 28: 1000 (44%); 35: 463 (20%) | 8: 510 (22%); 19: 946 (41%); 28: 1530 (67%); 35: 1899 (83%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3, 4 | 1: 1952 (85%); 2: 1520 (66%); 3: 942 (41%); 4: 470 (20%) | 1: 774 (34%); 2: 1352 (59%); 3: 1824 (80%); 4: 2294 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0133, -0.0011, 0.0103, 0.0217 | -0.0133: 1840 (80%); -0.0011: 1399 (61%); 0.0103: 918 (40%); 0.0217: 460 (20%) | -0.0133: 460 (20%); -0.0011: 1081 (47%); 0.0103: 1383 (60%); 0.0217: 1837 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6437, 25.9689, 26.6498, 27.3557 | 24.6437: 1835 (80%); 25.9689: 1378 (60%); 26.6498: 925 (40%); 27.3557: 493 (21%) | 24.6437: 459 (20%); 25.9689: 920 (40%); 26.6498: 1379 (60%); 27.3557: 1966 (86%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -1.0766, -0.3524, 0.1456, 0.9308 | -1.0766: 1835 (80%); -0.3524: 1376 (60%); 0.1456: 918 (40%); 0.9308: 459 (20%) | -1.0766: 459 (20%); -0.3524: 918 (40%); 0.1456: 1376 (60%); 0.9308: 1835 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.9308, -0.1456, 0.3524, 1.0766 | -0.9308: 1835 (80%); -0.1456: 1376 (60%); 0.3524: 918 (40%); 1.0766: 459 (20%) | -0.9308: 459 (20%); -0.1456: 918 (40%); 0.3524: 1376 (60%); 1.0766: 1835 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0413, 0.0021, 0.0326, 0.09 | -0.0413: 1836 (80%); 0.0021: 1379 (60%); 0.0326: 924 (40%); 0.09: 459 (20%) | -0.0413: 461 (20%); 0.0021: 918 (40%); 0.0326: 1377 (60%); 0.09: 1835 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.1601, 8.5721, 8.9108, 9.3704 | 8.1601: 1836 (80%); 8.5721: 1373 (60%); 8.9108: 918 (40%); 9.3704: 459 (20%) | 8.1601: 458 (20%); 8.5721: 921 (40%); 8.9108: 1376 (60%); 9.3704: 1835 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 98.9% | 0, 1 | 0: 2269 (99%); 1: 795 (35%) | 0: 1474 (64%); 1: 2020 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 98.9% | -1, 0 | -1: 2142 (93%); 0: 1758 (77%) | -1: 511 (22%); 0: 1907 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 98.9% | 0, 1 | 0: 2269 (99%); 1: 869 (38%) | 0: 1400 (61%); 1: 1957 (85%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 7, 172, 277 | 3: 1904 (83%); 7: 1421 (62%); 172: 919 (40%); 277: 463 (20%) | 3: 525 (23%); 7: 969 (42%); 172: 1377 (60%); 277: 1839 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 8, 89, 141 | 1: 1885 (82%); 8: 1377 (60%); 89: 921 (40%); 141: 460 (20%) | 1: 583 (25%); 8: 924 (40%); 89: 1378 (60%); 141: 1838 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -1.1667, -0.4016, -0.0595, 0.2709 | -1.1667: 1835 (80%); -0.4016: 1376 (60%); -0.0595: 918 (40%); 0.2709: 459 (20%) | -1.1667: 459 (20%); -0.4016: 918 (40%); -0.0595: 1376 (60%); 0.2709: 1835 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -3.9604, -1.7439, -0.7023, -0.1175 | -3.9604: 1835 (80%); -1.7439: 1376 (60%); -0.7023: 918 (40%); -0.1175: 459 (20%) | -3.9604: 459 (20%); -1.7439: 918 (40%); -0.7023: 1376 (60%); -0.1175: 1835 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -3.1538, -1.4035, -0.6018, -0.0433 | -3.1538: 1835 (80%); -1.4035: 1376 (60%); -0.6018: 918 (40%); -0.0433: 459 (20%) | -3.1538: 459 (20%); -1.4035: 918 (40%); -0.6018: 1376 (60%); -0.0433: 1835 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.8859, -0.2778, -0.0003, 0.3333 | -0.8859: 1835 (80%); -0.2778: 1377 (60%); -0.0003: 918 (40%); 0.3333: 459 (20%) | -0.8859: 459 (20%); -0.2778: 918 (40%); -0.0003: 1377 (60%); 0.3333: 1835 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -4.5199, -1.9766, -0.8087, -0.0627 | -4.5199: 1835 (80%); -1.9766: 1376 (60%); -0.8087: 918 (40%); -0.0627: 459 (20%) | -4.5199: 460 (20%); -1.9766: 918 (40%); -0.8087: 1377 (60%); -0.0627: 1835 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -3.8935, -1.7143, -0.6805, -0.0895 | -3.8935: 1835 (80%); -1.7143: 1376 (60%); -0.6805: 918 (40%); -0.0895: 459 (20%) | -3.8935: 459 (20%); -1.7143: 918 (40%); -0.6805: 1376 (60%); -0.0895: 1835 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 30.916, 39.03, 46.02, 55.436 | 30.916: 1835 (80%); 39.03: 1377 (60%); 46.02: 920 (40%); 55.436: 459 (20%) | 30.916: 459 (20%); 39.03: 920 (40%); 46.02: 1377 (60%); 55.436: 1835 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.3% | -0.2454, -0.1486, -0.0677, 0.0079 | -0.2454: 1822 (79%); -0.1486: 1366 (60%); -0.0677: 912 (40%); 0.0079: 457 (20%) | -0.2454: 456 (20%); -0.1486: 911 (40%); -0.0677: 1367 (60%); 0.0079: 1822 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0073, 0.0179, 0.0354, 0.0794 | 0.0073: 1831 (80%); 0.0179: 1375 (60%); 0.0354: 920 (40%); 0.0794: 459 (20%) | 0.0073: 463 (20%); 0.0179: 919 (40%); 0.0354: 1374 (60%); 0.0794: 1835 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 9 | 0: 2294 (100%); 1: 1753 (76%); 4: 939 (41%); 9: 473 (21%) | 0: 541 (24%); 1: 933 (41%); 4: 1496 (65%); 9: 1888 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2143 | 0: 2294 (100%); 0.2143: 463 (20%) | 0: 1471 (64%); 0.2143: 1840 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1439, 0.4, 0.6667 | 0: 2294 (100%); 0.1439: 1376 (60%); 0.4: 946 (41%); 0.6667: 495 (22%) | 0: 887 (39%); 0.1439: 918 (40%); 0.4: 1393 (61%); 0.6667: 1872 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 2294 (100%); 1: 1602 (70%); 3: 944 (41%); 7: 465 (20%) | 0: 692 (30%); 1: 1107 (48%); 3: 1516 (66%); 7: 1895 (83%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 9 | 0: 2294 (100%); 1: 1753 (76%); 4: 939 (41%); 9: 473 (21%) | 0: 541 (24%); 1: 933 (41%); 4: 1496 (65%); 9: 1888 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 2294 (100%); 1: 1547 (67%); 2: 1151 (50%); 6: 465 (20%) | 0: 747 (33%); 1: 1143 (50%); 2: 1408 (61%); 6: 1895 (83%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667, 0.3333, 0.5903 | 0: 2031 (89%); 0.1667: 1383 (60%); 0.3333: 947 (41%); 0.5903: 459 (20%) | 0: 644 (28%); 0.1667: 923 (40%); 0.3333: 1393 (61%); 0.5903: 1835 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.125, 0.5455 | 0: 2021 (88%); 0.125: 921 (40%); 0.5455: 460 (20%) | 0: 1275 (56%); 0.125: 1377 (60%); 0.5455: 1837 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5714 | 0: 2014 (88%); 0.25: 942 (41%); 0.5714: 462 (20%) | 0: 1078 (47%); 0.25: 1383 (60%); 0.5714: 1836 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5714 | 0: 2014 (88%); 0.25: 942 (41%); 0.5714: 462 (20%) | 0: 1078 (47%); 0.25: 1383 (60%); 0.5714: 1836 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1738, 0, 0.1288 | -0.1738: 1835 (80%); 0: 1665 (73%); 0.1288: 459 (20%) | -0.1738: 459 (20%); 0: 1686 (73%); 0.1288: 1835 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.6098, 0, 0.4725, 1.891 | -0.6098: 1835 (80%); 0: 1471 (64%); 0.4725: 919 (40%); 1.891: 459 (20%) | -0.6098: 459 (20%); 0: 1199 (52%); 0.4725: 1378 (60%); 1.891: 1835 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 1919 (84%); 4: 1532 (67%); 7: 985 (43%); 11: 512 (22%) | 2: 552 (24%); 4: 973 (42%); 7: 1454 (63%); 11: 1836 (80%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1085, -0.0609, -0.0216, 0.0221 | -0.1085: 1835 (80%); -0.0609: 1376 (60%); -0.0216: 918 (40%); 0.0221: 458 (20%) | -0.1085: 459 (20%); -0.0609: 918 (40%); -0.0216: 1376 (60%); 0.0221: 1836 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1202, -0.0736, -0.0335, 0.0139 | -0.1202: 1835 (80%); -0.0736: 1376 (60%); -0.0335: 918 (40%); 0.0139: 458 (20%) | -0.1202: 459 (20%); -0.0736: 918 (40%); -0.0335: 1376 (60%); 0.0139: 1836 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0806, -0.0396, -0.0074, 0.033 | -0.0806: 1835 (80%); -0.0396: 1377 (60%); -0.0074: 918 (40%); 0.033: 459 (20%) | -0.0806: 459 (20%); -0.0396: 917 (40%); -0.0074: 1376 (60%); 0.033: 1835 (80%) | OFFLINE |
| pct_from_avwap_252low | backtest/signals/technical.py (f-string template) | 100.0% | -1.3788, 0.2684, 1.1638, 3.3122 | -1.3788: 1835 (80%); 0.2684: 1376 (60%); 1.1638: 918 (40%); 3.3122: 459 (20%) | -1.3788: 459 (20%); 0.2684: 918 (40%); 1.1638: 1376 (60%); 3.3122: 1835 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -29.4784, -17.2406, -5.8516, 8.7726 | -29.4784: 1835 (80%); -17.2406: 1376 (60%); -5.8516: 918 (40%); 8.7726: 459 (20%) | -29.4784: 459 (20%); -17.2406: 918 (40%); -5.8516: 1376 (60%); 8.7726: 1835 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0521, 0.0754, 0.1057, 0.1605 | 0.0521: 1836 (80%); 0.0754: 1377 (60%); 0.1057: 918 (40%); 0.1605: 461 (20%) | 0.0521: 463 (20%); 0.0754: 920 (40%); 0.1057: 1376 (60%); 0.1605: 1835 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.2541, 0.5303, 0.7494, 0.8984 | 0.2541: 1835 (80%); 0.5303: 1376 (60%); 0.7494: 918 (40%); 0.8984: 459 (20%) | 0.2541: 460 (20%); 0.5303: 918 (40%); 0.7494: 1376 (60%); 0.8984: 1835 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -3.7297, -2.2266, -1.1414, -0.2207 | -3.7297: 1835 (80%); -2.2266: 1376 (60%); -1.1414: 918 (40%); -0.2207: 459 (20%) | -3.7297: 459 (20%); -2.2266: 918 (40%); -1.1414: 1376 (60%); -0.2207: 1835 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -1.1398, -0.605, -0.1378, 0.3988 | -1.1398: 1835 (80%); -0.605: 1376 (60%); -0.1378: 918 (40%); 0.3988: 459 (20%) | -1.1398: 459 (20%); -0.605: 918 (40%); -0.1378: 1376 (60%); 0.3988: 1835 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -3.1499, -1.8427, -0.9701, -0.0711 | -3.1499: 1835 (80%); -1.8427: 1376 (60%); -0.9701: 918 (40%); -0.0711: 459 (20%) | -3.1499: 459 (20%); -1.8427: 918 (40%); -0.9701: 1376 (60%); -0.0711: 1835 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -11.5212, -6.7034, -2.6882, 1.9404 | -11.5212: 1835 (80%); -6.7034: 1376 (60%); -2.6882: 918 (40%); 1.9404: 459 (20%) | -11.5212: 459 (20%); -6.7034: 918 (40%); -2.6882: 1376 (60%); 1.9404: 1835 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 32.884, 38.762, 44.728, 51.244 | 32.884: 1835 (80%); 38.762: 1376 (60%); 44.728: 918 (40%); 51.244: 459 (20%) | 32.884: 459 (20%); 38.762: 918 (40%); 44.728: 1376 (60%); 51.244: 1835 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 12.736, 43.072, 68.528, 86.046 | 12.736: 1835 (80%); 43.072: 1376 (60%); 68.528: 918 (40%); 86.046: 459 (20%) | 12.736: 459 (20%); 43.072: 918 (40%); 68.528: 1376 (60%); 86.046: 1835 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 36.14, 40.614, 44.778, 49.7 | 36.14: 1837 (80%); 40.614: 1376 (60%); 44.778: 918 (40%); 49.7: 460 (20%) | 36.14: 460 (20%); 40.614: 918 (40%); 44.778: 1376 (60%); 49.7: 1836 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 28.812, 37.382, 45.266, 54.87 | 28.812: 1835 (80%); 37.382: 1376 (60%); 45.266: 918 (40%); 54.87: 460 (20%) | 28.812: 459 (20%); 37.382: 918 (40%); 45.266: 1376 (60%); 54.87: 1836 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 2293 (100%) | 0: 2293 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0291, 0.0444, 0.0569, 0.0857 | 0.0291: 1837 (80%); 0.0444: 1377 (60%); 0.0569: 918 (40%); 0.0857: 463 (20%) | 0.0291: 464 (20%); 0.0444: 922 (40%); 0.0569: 1378 (60%); 0.0857: 1837 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0778, -0.0567, -0.0434, -0.0345 | -0.0778: 1839 (80%); -0.0567: 1377 (60%); -0.0434: 990 (43%); -0.0345: 459 (20%) | -0.0778: 461 (20%); -0.0567: 918 (40%); -0.0434: 1469 (64%); -0.0345: 1835 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 2294 (100%); 1: 499 (22%) | 0: 1795 (78%); 1: 1987 (87%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.4% | 24, 41, 62, 66 | 24: 1907 (83%); 41: 1403 (61%); 62: 932 (41%); 66: 490 (21%) | 24: 492 (21%); 41: 942 (41%); 62: 1374 (60%); 66: 1828 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.0% | 0.0128, 0.0193, 0.0279, 0.0458 | 0.0128: 1796 (78%); 0.0193: 1348 (59%); 0.0279: 900 (39%); 0.0458: 452 (20%) | 0.0128: 453 (20%); 0.0193: 901 (39%); 0.0279: 1349 (59%); 0.0458: 1797 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.1054, 0.1856, 0.3117, 0.4874 | 0.1054: 1835 (80%); 0.1856: 1377 (60%); 0.3117: 918 (40%); 0.4874: 459 (20%) | 0.1054: 460 (20%); 0.1856: 920 (40%); 0.3117: 1377 (60%); 0.4874: 1835 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 26.62, 53.8, 89.04, 145.24 | 26.62: 1835 (80%); 53.8: 1379 (60%); 89.04: 918 (40%); 145.24: 459 (20%) | 26.62: 459 (20%); 53.8: 921 (40%); 89.04: 1376 (60%); 145.24: 1835 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -7.315, -2.8545, -0.801, 1.165 | -7.315: 1836 (80%); -2.8545: 1376 (60%); -0.801: 918 (40%); 1.165: 460 (20%) | -7.315: 460 (20%); -2.8545: 918 (40%); -0.801: 1376 (60%); 1.165: 1836 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 13.116, 21.032, 32.688, 54.48 | 13.116: 1835 (80%); 21.032: 1376 (60%); 32.688: 918 (40%); 54.48: 459 (20%) | 13.116: 459 (20%); 21.032: 918 (40%); 32.688: 1376 (60%); 54.48: 1835 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 12.736, 22.684, 34.698, 55.27 | 12.736: 1835 (80%); 22.684: 1376 (60%); 34.698: 918 (40%); 55.27: 459 (20%) | 12.736: 459 (20%); 22.684: 918 (40%); 34.698: 1376 (60%); 55.27: 1835 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 8.6, 21.93, 44.682, 75.068 | 8.6: 1835 (80%); 21.93: 1377 (60%); 44.682: 918 (40%); 75.068: 459 (20%) | 8.6: 459 (20%); 21.93: 919 (40%); 44.682: 1376 (60%); 75.068: 1835 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 5.782, 28.592, 54.896, 91.926 | 5.782: 1835 (80%); 28.592: 1376 (60%); 54.896: 918 (40%); 91.926: 459 (20%) | 5.782: 459 (20%); 28.592: 918 (40%); 54.896: 1376 (60%); 91.926: 1835 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 12, 17 | 5: 1844 (80%); 8: 1399 (61%); 12: 928 (40%); 17: 478 (21%) | 5: 566 (25%); 8: 1057 (46%); 12: 1475 (64%); 17: 1923 (84%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 17 | 5: 1896 (83%); 10: 1447 (63%); 14: 1059 (46%); 17: 538 (23%) | 5: 492 (21%); 10: 922 (40%); 14: 1408 (61%); 17: 1856 (81%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 36.84, 42.96, 48.028, 54.47 | 36.84: 1836 (80%); 42.96: 1377 (60%); 48.028: 918 (40%); 54.47: 460 (20%) | 36.84: 460 (20%); 42.96: 920 (40%); 48.028: 1376 (60%); 54.47: 1837 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2643, 0.5794, 0.7976, 0.9484 | 0.2643: 1835 (80%); 0.5794: 1384 (60%); 0.7976: 920 (40%); 0.9484: 472 (21%) | 0.2643: 459 (20%); 0.5794: 925 (40%); 0.7976: 1378 (60%); 0.9484: 1837 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.28, 19.1, 24.23, 30.18 | 16.28: 1837 (80%); 19.1: 1379 (60%); 24.23: 920 (40%); 30.18: 479 (21%) | 16.28: 461 (20%); 19.1: 920 (40%); 24.23: 1382 (60%); 30.18: 1836 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 16.28, 19.1, 24.23, 30.18 | 16.28: 1837 (80%); 19.1: 1379 (60%); 24.23: 920 (40%); 30.18: 479 (21%) | 16.28: 461 (20%); 19.1: 920 (40%); 24.23: 1382 (60%); 30.18: 1836 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.871, 0.9127, 0.9542, 1.0011 | 0.871: 1843 (80%); 0.9127: 1376 (60%); 0.9542: 924 (40%); 1.0011: 465 (20%) | 0.871: 460 (20%); 0.9127: 918 (40%); 0.9542: 1377 (60%); 1.0011: 1836 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 1.1, 1.22, 1.4, 1.75 | 1.1: 1854 (81%); 1.22: 1394 (61%); 1.4: 922 (40%); 1.75: 467 (20%) | 1.1: 496 (22%); 1.22: 934 (41%); 1.4: 1382 (60%); 1.75: 1836 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0201, 0.0483, 0.0839, 0.1332 | 0.0201: 1837 (80%); 0.0483: 1377 (60%); 0.0839: 918 (40%); 0.1332: 459 (20%) | 0.0201: 460 (20%); 0.0483: 918 (40%); 0.0839: 1376 (60%); 0.1332: 1835 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 44.608, 77.1202, 116.8681, 202.4191 | 44.608: 1835 (80%); 77.1202: 1376 (60%); 116.8681: 918 (40%); 202.4191: 459 (20%) | 44.608: 459 (20%); 77.1202: 918 (40%); 116.8681: 1376 (60%); 202.4191: 1835 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 42.8059, 73.5858, 112.643, 193.6532 | 42.8059: 1835 (80%); 73.5858: 1376 (60%); 112.643: 918 (40%); 193.6532: 459 (20%) | 42.8059: 459 (20%); 73.5858: 918 (40%); 112.643: 1376 (60%); 193.6532: 1835 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 40.5566, 70.1703, 108.8814, 187.7733 | 40.5566: 1835 (80%); 70.1703: 1376 (60%); 108.8814: 918 (40%); 187.7733: 459 (20%) | 40.5566: 459 (20%); 70.1703: 918 (40%); 108.8814: 1376 (60%); 187.7733: 1835 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 46.4279, 80.3439, 123.0382, 209.491 | 46.4279: 1835 (80%); 80.3439: 1376 (60%); 123.0382: 918 (40%); 209.491: 459 (20%) | 46.4279: 459 (20%); 80.3439: 918 (40%); 123.0382: 1376 (60%); 209.491: 1835 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.1394, 82.9711, 128.7882, 216.3947 | 48.1394: 1835 (80%); 82.9711: 1376 (60%); 128.7882: 918 (40%); 216.3947: 459 (20%) | 48.1394: 459 (20%); 82.9711: 918 (40%); 128.7882: 1376 (60%); 216.3947: 1835 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2294 (100%) | 0: 2133 (93%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2294 (100%) | 0: 2072 (90%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.12, -0.0708, -0.0339, 0.0156 | -0.12: 1835 (80%); -0.0708: 1378 (60%); -0.0339: 918 (40%); 0.0156: 461 (20%) | -0.12: 461 (20%); -0.0708: 920 (40%); -0.0339: 1377 (60%); 0.0156: 1836 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -87.574, -75.74, -56.726, -30.762 | -87.574: 1835 (80%); -75.74: 1376 (60%); -56.726: 918 (40%); -30.762: 459 (20%) | -87.574: 459 (20%); -75.74: 918 (40%); -56.726: 1376 (60%); -30.762: 1835 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.9% | 0.5868, 0.8602, 1.0773, 1.3845 | 0.5868: 1833 (80%); 0.8602: 1375 (60%); 1.0773: 917 (40%); 1.3845: 459 (20%) | 0.5868: 459 (20%); 0.8602: 917 (40%); 1.0773: 1375 (60%); 1.3845: 1833 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.9% | 3, 5, 8, 9 | 3: 1986 (87%); 5: 1580 (69%); 8: 921 (40%); 9: 658 (29%) | 3: 502 (22%); 5: 919 (40%); 8: 1633 (71%); 9: 1914 (83%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.8% | 0.2064, 0.2539, 0.3097, 0.3962 | 0.2064: 1832 (80%); 0.2539: 1374 (60%); 0.3097: 918 (40%); 0.3962: 458 (20%) | 0.2064: 459 (20%); 0.2539: 917 (40%); 0.3097: 1375 (60%); 0.3962: 1831 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.8% | 4, 6, 8, 9 | 4: 1886 (82%); 6: 1534 (67%); 8: 1066 (46%); 9: 789 (34%) | 4: 559 (24%); 6: 953 (42%); 8: 1500 (65%); 9: 1835 (80%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.9% | 0.0244, 0.0353, 0.0479, 0.0755 | 0.0244: 1836 (80%); 0.0353: 1375 (60%); 0.0479: 917 (40%); 0.0755: 460 (20%) | 0.0244: 459 (20%); 0.0353: 920 (40%); 0.0479: 1376 (60%); 0.0755: 1833 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.9% | 3, 6, 8, 9 | 3: 1963 (86%); 6: 1405 (61%); 8: 946 (41%); 9: 671 (29%) | 3: 501 (22%); 6: 1106 (48%); 8: 1620 (71%); 9: 1906 (83%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.8% | -0.2769, -0.1497, -0.0377, 0.1058 | -0.2769: 1831 (80%); -0.1497: 1373 (60%); -0.0377: 916 (40%); 0.1058: 459 (20%) | -0.2769: 458 (20%); -0.1497: 916 (40%); -0.0377: 1374 (60%); 0.1058: 1831 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.8% | 1, 3, 4, 7 | 1: 2289 (100%); 3: 1443 (63%); 4: 1165 (51%); 7: 532 (23%) | 1: 473 (21%); 3: 1124 (49%); 4: 1380 (60%); 7: 1916 (84%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.3% |
| 8k_item_5_02_filed_within_7d | 4.3% |
| above_avwap_20high | 28.9% |
| above_avwap_20low | 70.8% |
| above_avwap_252low | 66.4% |
| above_avwap_50low | 68.3% |
| above_cam_r3 | 54.7% |
| above_cam_r4 | 35.1% |
| above_cpr | 64.3% |
| above_pivot | 65.3% |
| above_prev_high | 39.1% |
| above_prev_high_clearance_atr_05 | 20.4% |
| above_prev_low | 80.3% |
| above_r1 | 38.6% |
| above_r2 | 20.2% |
| above_vwap | 30.9% |
| above_wood_p | 61.4% |
| ad_rising | 44.5% |
| adx_cross_up | 3.1% |
| adx_cross_up_20 | 3.2% |
| adx_di_bear | 78.7% |
| adx_di_bull | 21.3% |
| adx_strong | 7.3% |
| adx_trending | 42.6% |
| ao_cross_dn | 3.8% |
| ao_cross_up | 1.9% |
| ao_positive | 18.8% |
| ao_twin_peaks_bull | 8.3% |
| at_key_fib | 13.6% |
| at_key_fib_wide | 32.1% |
| avwap_20high_loss_recent_3d | 13.9% |
| avwap_20high_reclaim_recent_3d | 22.3% |
| avwap_20low_loss_recent_3d | 17.6% |
| avwap_20low_reclaim_recent_3d | 59.3% |
| avwap_252low_loss_recent_3d | 33.6% |
| avwap_252low_reclaim_recent_3d | 66.4% |
| avwap_50low_loss_recent_3d | 21.2% |
| avwap_50low_reclaim_recent_3d | 56.8% |
| bb_10_20_above_mid | 37.4% |
| bb_10_20_expanding | 59.6% |
| bb_10_20_pctb_gt_75 | 21.6% |
| bb_10_20_pctb_gt_8 | 19.3% |
| bb_10_20_pctb_gt_85 | 16.2% |
| bb_10_20_pctb_gt_9 | 13.6% |
| bb_10_20_pctb_gt_95 | 10.5% |
| bb_10_20_pctb_lt_05 | 11.2% |
| bb_10_20_pctb_lt_1 | 16.2% |
| bb_10_20_pctb_lt_15 | 21.7% |
| bb_10_20_pctb_lt_2 | 28.2% |
| bb_10_20_pctb_lt_25 | 35.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 25.7% |
| bb_10_20_reclaim_from_upper_recent_3d | 4.6% |
| bb_10_20_squeeze | 21.7% |
| bb_10_20_touch_lower | 10.2% |
| bb_10_20_touch_upper | 10.7% |
| bb_20_15_above_mid | 28.1% |
| bb_20_15_expanding | 65.0% |
| bb_20_15_pctb_gt_75 | 17.3% |
| bb_20_15_pctb_gt_8 | 15.9% |
| bb_20_15_pctb_gt_85 | 14.7% |
| bb_20_15_pctb_gt_9 | 13.3% |
| bb_20_15_pctb_gt_95 | 12.1% |
| bb_20_15_pctb_lt_05 | 34.9% |
| bb_20_15_pctb_lt_1 | 39.8% |
| bb_20_15_pctb_lt_15 | 44.2% |
| bb_20_15_pctb_lt_2 | 48.6% |
| bb_20_15_pctb_lt_25 | 53.6% |
| bb_20_15_reclaim_from_lower_recent_3d | 29.4% |
| bb_20_15_reclaim_from_upper_recent_3d | 4.0% |
| bb_20_15_squeeze | 23.8% |
| bb_20_15_touch_lower | 34.0% |
| bb_20_15_touch_upper | 12.6% |
| bb_20_20_above_mid | 28.1% |
| bb_20_20_expanding | 65.0% |
| bb_20_20_pctb_gt_75 | 15.2% |
| bb_20_20_pctb_gt_8 | 13.3% |
| bb_20_20_pctb_gt_85 | 11.6% |
| bb_20_20_pctb_gt_9 | 10.5% |
| bb_20_20_pctb_gt_95 | 8.7% |
| bb_20_20_pctb_lt_05 | 20.9% |
| bb_20_20_pctb_lt_1 | 26.4% |
| bb_20_20_pctb_lt_15 | 33.3% |
| bb_20_20_pctb_lt_2 | 39.8% |
| bb_20_20_pctb_lt_25 | 45.2% |
| bb_20_20_reclaim_from_lower_recent_3d | 27.5% |
| bb_20_20_reclaim_from_upper_recent_3d | 2.7% |
| bb_20_20_squeeze | 11.8% |
| bb_20_20_touch_lower | 18.9% |
| bb_20_20_touch_upper | 8.6% |
| bearish_engulfing | 2.1% |
| bearish_pin_bar | 4.1% |
| below_avwap_20high | 71.1% |
| below_avwap_20low | 29.1% |
| below_avwap_252low | 33.6% |
| below_avwap_50low | 31.7% |
| below_cam_s3 | 25.3% |
| below_cam_s4 | 15.4% |
| below_cpr | 34.7% |
| below_ema_20 | 73.5% |
| below_ema_200 | 87.4% |
| below_ema_200_break_recent_5d | 21.8% |
| below_ema_20_break_recent_5d | 27.1% |
| below_ema_21 | 73.8% |
| below_ema_21_break_recent_5d | 26.4% |
| below_ema_50 | 82.7% |
| below_ema_50_break_recent_5d | 21.6% |
| below_ema_9 | 61.5% |
| below_ema_9_break_recent_5d | 29.9% |
| below_prev_high | 60.7% |
| below_prev_low | 19.6% |
| below_prev_low_clearance_atr_05 | 12.4% |
| below_s1 | 16.8% |
| below_s2 | 10.5% |
| below_sma_20 | 71.9% |
| below_sma_200 | 85.2% |
| below_sma_21 | 72.5% |
| below_sma_50 | 80.6% |
| below_sma_9 | 60.0% |
| below_vwap | 69.1% |
| break_52w_high | 0.0% |
| break_52w_high_confirmed_today | 0.0% |
| bullish_engulfing | 9.8% |
| bullish_pin_bar | 3.7% |
| ceo_buy | 1.6% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 41.4% |
| chandelier_long_flip_dn | 6.6% |
| chandelier_short_bearish | 82.2% |
| chandelier_short_flip_up | 9.3% |
| classification_change_from_tech | 66.7% |
| classification_change_to_defensive | 33.3% |
| close_above_open | 66.4% |
| close_below_open | 33.6% |
| close_in_bottom_40pct_of_range | 29.5% |
| close_in_top_40pct_of_range | 54.6% |
| cluster_buy | 0.6% |
| cmf_cross_dn | 5.1% |
| cmf_cross_up | 7.7% |
| cmf_negative | 60.0% |
| cmf_positive | 39.8% |
| concentrated_sell | 3.1% |
| cpr_narrow | 86.4% |
| cpr_narrow_tight | 21.0% |
| cup_handle_detected | 12.3% |
| cup_handle_neckline_break_retest_long | 1.1% |
| dc10_breakout_dn | 14.3% |
| dc10_breakout_dn_1pct | 17.9% |
| dc10_breakout_up | 11.6% |
| dc10_breakout_up_1pct | 15.1% |
| dc10_new_high | 14.9% |
| dc10_strong_breakout_dn | 7.8% |
| dc10_strong_breakout_up | 5.4% |
| dc20_breakout_dn | 11.4% |
| dc20_breakout_up | 6.8% |
| dc20_new_high | 8.5% |
| dc20_resistance_break_retest_strong | 3.1% |
| dc20_support_break_retest_strong | 33.7% |
| defensive_leadership | 61.4% |
| director_only_buy | 3.7% |
| doji | 2.4% |
| double_bottom_detected | 14.2% |
| double_top_detected | 15.6% |
| dpi_elevated | 49.0% |
| ema_20_50_bearish | 84.0% |
| ema_20_50_bullish | 16.0% |
| ema_20_50_death_cross | 2.0% |
| ema_20_50_golden_cross | 0.9% |
| ema_50_200_bearish | 71.6% |
| ema_50_200_bullish | 28.4% |
| ema_50_200_death_cross | 0.4% |
| ema_50_200_golden_cross | 0.1% |
| ema_9_21_bearish | 82.5% |
| ema_9_21_bullish | 17.5% |
| ema_9_21_death_cross | 3.9% |
| ema_9_21_golden_cross | 4.2% |
| evening_star | 3.1% |
| flag_bear_break_retest_short | 1.8% |
| flag_bear_broke | 1.9% |
| flag_bear_detected | 0.5% |
| flag_bull_broke | 0.1% |
| force_index_cross_dn | 5.5% |
| force_index_cross_up | 15.9% |
| force_index_positive | 35.0% |
| gap_dn_1_5pct | 12.8% |
| gap_dn_2pct | 9.1% |
| gap_up_1_5pct | 13.9% |
| gap_up_2pct | 9.2% |
| hammer | 2.5% |
| head_shoulders_bottom_detected | 3.3% |
| head_shoulders_top_detected | 6.8% |
| house_cluster_buy | 4.7% |
| house_cluster_sell | 5.9% |
| htf_aligned_bear | 68.9% |
| htf_aligned_bull | 4.2% |
| htf_disagreement | 2.5% |
| hull_bearish | 68.4% |
| hull_bullish | 31.6% |
| hull_flip_dn | 4.1% |
| hull_flip_up | 8.1% |
| ichi_above_cloud | 9.9% |
| ichi_above_cloud_break_recent_5d | 7.2% |
| ichi_below_cloud | 75.5% |
| ichi_below_cloud_break_recent_5d | 18.3% |
| ichi_cloud_thick | 86.2% |
| ichi_tk_bearish | 73.2% |
| ichi_tk_bullish | 18.2% |
| ichi_tk_cross_dn | 3.5% |
| ichi_tk_cross_up | 2.5% |
| ichi_weekly_above_cloud | 17.0% |
| ichi_weekly_below_cloud | 51.5% |
| ichi_weekly_in_cloud | 31.4% |
| in_reversal_window | 0.9% |
| inside_bar | 18.2% |
| inside_cpr | 3.4% |
| inside_kc | 71.4% |
| insider_cluster_active | 20.9% |
| institutional_buy | 90.5% |
| institutional_negative | 3.4% |
| institutional_persistence_growing | 50.7% |
| institutional_persistence_strong | 64.9% |
| institutional_strong_buy | 80.6% |
| inverted_cup_handle_detected | 11.2% |
| is_friday | 20.5% |
| is_halloween_period | 53.8% |
| is_halloween_period_first_day | 0.6% |
| is_january | 7.7% |
| is_january_extended | 8.3% |
| is_monday | 14.9% |
| is_pre_holiday | 2.4% |
| is_summer_period | 46.2% |
| is_totm_window | 31.6% |
| is_totm_window_first_day | 7.7% |
| is_week_open | 16.9% |
| kc_touch_lower | 27.3% |
| kc_touch_upper | 4.9% |
| large_dollar_buy | 1.1% |
| macd_12_26_9_bearish | 64.6% |
| macd_12_26_9_bullish | 35.4% |
| macd_12_26_9_crossover_dn | 3.4% |
| macd_12_26_9_crossover_up | 5.9% |
| macd_8_21_5_bearish | 60.1% |
| macd_8_21_5_bullish | 39.9% |
| macd_8_21_5_crossover_dn | 3.8% |
| macd_8_21_5_crossover_up | 7.8% |
| marubozu_bear | 0.8% |
| marubozu_bull | 2.4% |
| mfi_broad_overbought | 4.2% |
| mfi_broad_oversold | 17.7% |
| mfi_overbought | 1.0% |
| mfi_oversold | 4.4% |
| monthly_above_sma_12 | 16.8% |
| monthly_above_sma_6 | 13.9% |
| monthly_bias_bear | 75.0% |
| monthly_bias_bull | 5.7% |
| monthly_momentum_pos | 21.9% |
| morning_star | 5.2% |
| near_52w_high | 0.0% |
| near_52w_high_95pct | 0.3% |
| near_52w_low | 3.2% |
| near_52w_low_105pct | 19.5% |
| near_avwap_20high_atr_05x | 25.6% |
| near_avwap_20high_atr_10x | 47.1% |
| near_avwap_20high_atr_15x | 66.4% |
| near_avwap_20high_atr_20x | 80.8% |
| near_avwap_20low_atr_05x | 44.1% |
| near_avwap_20low_atr_10x | 66.7% |
| near_avwap_20low_atr_15x | 81.1% |
| near_avwap_20low_atr_20x | 89.7% |
| near_avwap_252low_atr_05x | 48.5% |
| near_avwap_252low_atr_10x | 71.9% |
| near_avwap_252low_atr_15x | 85.2% |
| near_avwap_252low_atr_20x | 92.6% |
| near_avwap_50low_atr_05x | 42.2% |
| near_avwap_50low_atr_10x | 63.0% |
| near_avwap_50low_atr_15x | 77.1% |
| near_avwap_50low_atr_20x | 86.8% |
| near_cam_r3 | 10.8% |
| near_cam_s3 | 5.9% |
| near_cam_s4 | 3.5% |
| near_fib_236 | 0.9% |
| near_fib_382 | 3.4% |
| near_fib_500 | 4.8% |
| near_fib_618 | 5.4% |
| near_fib_786 | 7.2% |
| near_pivot | 7.3% |
| near_prev_close | 5.8% |
| near_prev_high | 8.6% |
| near_prev_low | 3.4% |
| near_r1 | 10.6% |
| near_r1_wide | 39.9% |
| near_r2 | 4.7% |
| near_r2_wide | 28.2% |
| near_s1 | 5.1% |
| near_s1_wide | 21.4% |
| near_s2 | 1.7% |
| near_s2_wide | 11.8% |
| near_s3 | 1.6% |
| near_wood_r1 | 6.7% |
| near_wood_s1 | 3.7% |
| news_uses_polygon_score | 26.5% |
| obv_bearish | 69.0% |
| obv_bullish | 31.0% |
| obv_diverge_bull | 8.8% |
| obv_falling | 56.5% |
| obv_rising | 43.5% |
| outside_bar | 9.5% |
| pead_negative_surprise | 21.7% |
| pead_positive_surprise | 16.6% |
| pin_bar | 7.8% |
| po3_accumulation_active | 18.2% |
| po3_bearish | 4.4% |
| po3_bullish | 11.2% |
| po3_manipulation_sweep_down | 5.7% |
| po3_manipulation_sweep_up | 6.3% |
| po3_mmbm_setup | 0.6% |
| po3_mmsm_setup | 0.1% |
| po3_sweep_above_prior_high | 56.7% |
| po3_sweep_below_prior_low | 39.1% |
| ppo_bullish | 34.0% |
| ppo_crossover_dn | 3.5% |
| ppo_crossover_up | 6.0% |
| pre_fomc_d0 | 4.3% |
| pre_fomc_d1 | 2.9% |
| pre_fomc_window | 7.1% |
| price_above_dema | 48.1% |
| price_above_ema_20 | 26.5% |
| price_above_ema_200 | 12.6% |
| price_above_ema_200_break_recent_5d | 10.8% |
| price_above_ema_20_break_recent_5d | 22.6% |
| price_above_ema_21 | 26.2% |
| price_above_ema_21_break_recent_5d | 22.4% |
| price_above_ema_50 | 17.3% |
| price_above_ema_50_break_recent_5d | 15.6% |
| price_above_ema_9 | 38.5% |
| price_above_ema_9_break_recent_5d | 34.4% |
| price_above_hull | 52.7% |
| price_above_sma_200 | 14.8% |
| price_above_sma_21 | 27.5% |
| price_above_sma_50 | 19.4% |
| price_above_tema | 53.8% |
| price_below_dema | 51.9% |
| price_below_hull | 47.3% |
| price_below_tema | 46.2% |
| psar_bullish | 32.0% |
| psar_flip_dn | 4.2% |
| psar_flip_up | 8.6% |
| r1_break_retest_long | 33.7% |
| recent_capitulation_at_s3 | 0.6% |
| resistance_break_retest | 5.4% |
| risk_off_regime_bond_signal | 22.1% |
| risk_off_regime_bond_signal_strong | 11.1% |
| risk_off_regime_gold_signal | 46.3% |
| risk_on_regime_bond_signal | 34.2% |
| risk_on_regime_bond_signal_strong | 16.1% |
| roc_positive | 27.5% |
| roc_turning_dn | 4.6% |
| roc_turning_up | 8.6% |
| rsi_14_bullish | 22.9% |
| rsi_14_cross_dn_overbought_recent_3d | 0.7% |
| rsi_14_cross_up_extreme_os_recent_3d | 3.5% |
| rsi_14_cross_up_oversold_recent_3d | 20.2% |
| rsi_14_extreme_ob | 0.1% |
| rsi_14_extreme_os | 0.9% |
| rsi_14_overbought | 1.1% |
| rsi_14_oversold | 12.7% |
| rsi_14_rising | 65.8% |
| rsi_21_bullish | 19.0% |
| rsi_21_cross_dn_overbought_recent_3d | 0.0% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.5% |
| rsi_21_cross_up_oversold_recent_3d | 11.5% |
| rsi_21_extreme_os | 0.3% |
| rsi_21_overbought | 0.2% |
| rsi_21_oversold | 4.7% |
| rsi_21_rising | 65.6% |
| rsi_2_bullish | 54.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 15.4% |
| rsi_2_cross_dn_overbought_recent_3d | 22.0% |
| rsi_2_cross_up_extreme_os_recent_3d | 52.2% |
| rsi_2_cross_up_oversold_recent_3d | 56.3% |
| rsi_2_extreme_ob | 27.7% |
| rsi_2_extreme_os | 24.1% |
| rsi_2_overbought | 38.1% |
| rsi_2_oversold | 29.0% |
| rsi_2_rising | 65.6% |
| rsi_9_bullish | 28.6% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_9_cross_dn_overbought_recent_3d | 3.1% |
| rsi_9_cross_up_extreme_os_recent_3d | 14.5% |
| rsi_9_cross_up_oversold_recent_3d | 28.9% |
| rsi_9_extreme_ob | 0.6% |
| rsi_9_extreme_os | 5.0% |
| rsi_9_overbought | 4.8% |
| rsi_9_oversold | 23.0% |
| rsi_9_rising | 65.6% |
| s1_break_retest_short | 68.0% |
| sc_13d_filed_within_30d | 2.3% |
| sc_13g_filed_within_30d | 1.8% |
| sector_outperforming_spy | 49.3% |
| sector_underperforming_spy | 50.7% |
| shooting_star | 4.0% |
| sma_20_50_bullish | 23.9% |
| sma_20_50_golden_cross | 0.7% |
| sma_50_200_bullish | 30.8% |
| sma_50_200_golden_cross | 0.1% |
| sma_9_21_bullish | 24.6% |
| sma_9_21_golden_cross | 2.1% |
| smc_bos_bearish | 22.1% |
| smc_bos_bullish | 5.8% |
| smc_bos_retest_long | 3.3% |
| smc_bos_retest_short | 3.6% |
| smc_breaker_block_bearish | 27.7% |
| smc_breaker_block_bullish | 12.6% |
| smc_choch_bearish | 11.2% |
| smc_choch_bullish | 1.7% |
| smc_equal_highs_swept | 1.3% |
| smc_equal_lows_swept | 9.6% |
| smc_fvg_bearish_active | 59.2% |
| smc_fvg_bullish_active | 26.8% |
| smc_fvg_retest_long_zone | 3.8% |
| smc_fvg_retest_short_zone | 17.1% |
| smc_in_discount_zone | 89.3% |
| smc_in_premium_zone | 29.0% |
| smc_inverse_fvg_bearish | 97.2% |
| smc_inverse_fvg_bullish | 54.9% |
| smc_liquidity_swept_dn | 1.8% |
| smc_liquidity_swept_up | 1.9% |
| smc_mitigation_block_long | 2.2% |
| smc_mitigation_block_short | 0.8% |
| smc_ob_bearish_active | 61.1% |
| smc_ob_bullish_active | 10.8% |
| smc_ote_long_zone | 9.9% |
| smc_ote_short_zone | 3.2% |
| squeeze_fire_dn | 4.0% |
| squeeze_fire_up | 8.3% |
| squeeze_in | 22.9% |
| squeeze_positive | 29.6% |
| stoch_bearish_cross | 7.2% |
| stoch_broad_overbought | 8.8% |
| stoch_broad_oversold | 44.7% |
| stoch_bullish_cross | 21.4% |
| stoch_overbought | 6.7% |
| stoch_oversold | 35.6% |
| stochrsi_cross_dn | 12.7% |
| stochrsi_cross_up | 41.5% |
| stochrsi_overbought | 25.5% |
| stochrsi_oversold | 32.8% |
| supertrend_bearish | 9.2% |
| supertrend_bullish | 90.8% |
| supertrend_flip_dn | 2.4% |
| supertrend_flip_recent_long_5d | 6.7% |
| supertrend_flip_recent_short_5d | 12.2% |
| supertrend_flip_up | 2.0% |
| support_break_retest | 42.8% |
| tema_above_dema | 33.7% |
| tema_cross_dn | 3.0% |
| tema_cross_up | 3.0% |
| three_black_crows | 8.0% |
| three_white_soldiers | 6.7% |
| triangle_apex_break_retest_long | 4.9% |
| triangle_ascending_detected | 4.2% |
| triangle_descending_detected | 10.9% |
| uo_overbought | 1.0% |
| uo_oversold | 5.1% |
| usd_strengthening | 22.9% |
| usd_weakening | 12.6% |
| vix_band_high | 52.9% |
| vix_band_low | 23.1% |
| vix_band_mid | 24.0% |
| vix_term_backwardation | 20.3% |
| vix_term_contango | 79.7% |
| vol_spike_12x | 63.3% |
| vol_spike_15x | 32.7% |
| vol_spike_17x | 22.5% |
| vol_spike_2x | 12.9% |
| vol_spike_2x_on_down_day_recent_3d | 14.3% |
| vol_spike_2x_on_up_day_recent_3d | 8.5% |
| vol_spike_3x | 3.7% |
| vp_above_value_area | 4.9% |
| vp_below_value_area | 42.4% |
| vp_close_above_poc | 27.8% |
| vp_close_below_poc | 72.2% |
| vp_in_value_area | 52.7% |
| week_open_gap_down_15pct | 1.5% |
| week_open_gap_up_15pct | 2.7% |
| weekly_above_ema_10 | 18.0% |
| weekly_above_ema_20 | 12.7% |
| weekly_bias_bear | 81.0% |
| weekly_bias_bull | 11.7% |
| weekly_momentum_pos | 25.5% |
| williams_r_overbought | 14.9% |
| williams_r_oversold | 33.2% |
| williams_r_rising | 67.7% |
| within_pead_window | 38.5% |
| within_post_deletion_window | 2.7% |
| within_post_inclusion_window | 0.3% |
| within_pre_rebalance_window | 2.7% |
| xs_avoid_high_ivol | 65.5% |
| xs_avoid_high_max | 70.7% |
| xs_high_beta_decile | 28.7% |
| xs_low_beta_bottom_quintile | 28.7% |
| xs_low_beta_decile | 13.3% |
| xs_low_beta_decile_entry_recent_5d | 0.5% |
| xs_low_beta_top_quintile | 13.3% |
| xs_momentum_bottom_decile | 20.7% |
| xs_momentum_bottom_quintile | 37.0% |
| xs_momentum_top_decile | 5.3% |
| xs_momentum_top_quintile | 10.4% |
| xs_quality_bottom_quintile | 23.1% |
| xs_quality_top_quintile | 20.4% |
| xs_quality_top_tercile | 38.5% |
| year_low_break_retest_short | 15.2% |
| yoy_surprise_high | 45.2% |
| yoy_surprise_negative | 44.3% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.9% |
| committed_growth_holders | 90.9% |
| corp_donations_1y | 6.1% |
| corp_donations_count_1y | 6.1% |
| corp_donations_unique_pacs | 6.1% |
| cot_rut_commercials_pctile_3y | 54.0% |
| cot_rut_mmoney_pctile_3y | 54.0% |
| cup_handle_depth_pct | 23.2% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 9.5% |
| days_since_inclusion | 14.4% |
| days_since_last_earnings | 98.0% |
| days_to_next_holiday | 67.5% |
| days_to_rebalance | 13.1% |
| dpi_30d_avg | 95.6% |
| dpi_recent | 95.6% |
| earnings_announcement_return | 90.5% |
| earnings_eps_yoy_growth | 94.5% |
| flag_bear_pole_move_pct | 0.5% |
| gov_contracts_4q_sum | 39.5% |
| gov_contracts_last_qtr_amount | 39.5% |
| gov_contracts_qoq_growth | 39.5% |
| head_shoulders_magnitude_pct | 9.9% |
| insider_director_buyers_30d | 6.9% |
| insider_officer_buyers_30d | 6.9% |
| insider_total_shares_bought_30d | 6.9% |
| insider_unique_buyers_30d | 6.9% |
| inverted_cup_handle_height_pct | 19.1% |
| lobbying_amount_1y | 68.9% |
| lobbying_amount_q | 68.9% |
| lobbying_amount_yoy | 68.9% |
| otc_short_ratio_recent | 95.6% |
| otc_volume_recent | 95.6% |
| pair_half_life | 91.6% |
| pair_max_abs_zscore | 91.6% |
| pair_zscore_signed | 91.6% |
| pct_from_avwap_20high | 91.1% |
| pct_from_avwap_20low | 83.3% |
| pct_from_avwap_50low | 91.4% |
| persistent_holders_4q | 90.9% |
| persistent_holders_8q | 90.9% |
| sc_13g_latest_percent_owned | 0.9% |
| search_volume_index_recent | 77.4% |
| search_volume_observations | 77.4% |
| search_volume_zscore_30d | 77.4% |
| sector_etf_return_20d | 3.3% |
| spy_return_20d | 3.3% |
| total_active_holders | 90.9% |
| triangle_breakdown_pct | 10.9% |
| triangle_breakout_pct | 4.2% |
| xs_quality_decile | 64.3% |
| xs_quality_gross_profitability | 64.3% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.997), `avwap_252low` (0.997), `avwap_50low` (0.997), `bb_10_20_lower` (0.995), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.998), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.996), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.996), `cam_s2` (0.996), `cam_s3` (0.996), `cam_s4` (0.995), `chandelier_long_value` (0.999), `chandelier_short_value` (0.998), `cpr_bottom` (0.997), `cpr_top` (0.997), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.997), `dc10_lower` (0.996), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.996), `dc20_mid` (0.999), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.999), `double_top_neckline` (0.998), `double_top_peak` (0.998), `entry_stop_long` (0.994), `entry_stop_short` (0.997), `fib_236` (0.995), `fib_382` (0.997), `fib_500` (0.997), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.99), `fib_ext_162` (0.986), `flag_bear_breakdown_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.993), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.998), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.996), `monthly_sma_12` (0.984), `monthly_sma_6` (0.995), `pivot` (0.997), `prev_close` (0.996), `prev_high` (0.997), `prev_low` (0.996), `psar_value` (0.998), `r1` (0.997), `r2` (0.997), `r3` (0.997), `s1` (0.995), `s2` (0.994), `s3` (0.992), `supertrend_value` (0.99), `swing_high` (0.993), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.997), `weekly_close` (0.996), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.997), `wood_r1` (0.997), `wood_r2` (0.998), `wood_s1` (0.995), `wood_s2` (0.994), `year_high` (0.955), `year_low` (0.988)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P3.1 | volume ratio floor (vol / avg) | 4 | subset-safe | no - derives offline | 1 | 3 | 0 |
| P4 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     4 x 1 = 4
offline gradings   3 level-combinations x 24 exits = 72 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  0 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 3 + 0 = 4 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 641 census axes join it only when REGISTERED at the T3 band review.
