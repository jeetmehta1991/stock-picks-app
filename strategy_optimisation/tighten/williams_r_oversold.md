# Table A - williams_r_oversold

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit a8a3061da at 2026-09-16 16:05:40 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** momentum | **status:** STALLED-CAMPAIGN | **R5 fires:** 2535 | **surviving fires (T1):** 2535 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Table A - parameter inventory (the SS6 canonical shape, pre-R1)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close). The
R1 SPECS entry absorbs and supersedes this pre-R1 inventory - producer
knob rows below are placeholders it must fill.

| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|
| P1 | PRODUCER | below_ema_200 - emitted by backtest/signals/screener.py; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P2 | PRODUCER | cmf_negative - emitted by backtest/signals/screener.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P3 | PRODUCER | cmf_positive - emitted by backtest/signals/screener.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P4 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P5 | PRODUCER | rsi_2 - emitted by backtest/signals/screener.py; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P6 | PRODUCER | williams_r_oversold - emitted by backtest/signals/screener.py +3; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P7 | STRATEGY | williams_r `> -20` [EXISTING-THRESHOLD] | `> -20` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P8 | STRATEGY-HELPER | _short_borrow_trap_active(s) - a helper gate; its internals are outside the source pattern (lower bound) | required | - | inspect at R1 | INVENTORY-PENDING-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| williams_r | backtest/signals/screener.py +1 | `> -20` | 100.0% | -19.89 -> 1014 (40%); -13.08 -> 508 (20%) | looser (lower the threshold): RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 17.71, 21.776, 26.496, 33.282 | 17.71: 2030 (80%); 21.776: 1521 (60%); 26.496: 1014 (40%); 33.282: 507 (20%) | 17.71: 510 (20%); 21.776: 1014 (40%); 26.496: 1521 (60%); 33.282: 2028 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 19.55, 22.37, 24.79, 27.962 | 19.55: 2029 (80%); 22.37: 1524 (60%); 24.79: 1018 (40%); 27.962: 507 (20%) | 19.55: 509 (20%); 22.37: 1015 (40%); 24.79: 1522 (60%); 27.962: 2028 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.62, 21.51, 24.304, 28.104 | 18.62: 2029 (80%); 21.51: 1522 (60%); 24.304: 1014 (40%); 28.104: 507 (20%) | 18.62: 508 (20%); 21.51: 1015 (40%); 24.304: 1521 (60%); 28.104: 2028 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -3.5548, -0.7617, 0.8445, 3.9855 | -3.5548: 2028 (80%); -0.7617: 1521 (60%); 0.8445: 1014 (40%); 3.9855: 507 (20%) | -3.5548: 507 (20%); -0.7617: 1015 (40%); 0.8445: 1521 (60%); 3.9855: 2028 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.1537, 2.0124, 3.3208, 5.8258 | 1.1537: 2028 (80%); 2.0124: 1521 (60%); 3.3208: 1014 (40%); 5.8258: 507 (20%) | 1.1537: 507 (20%); 2.0124: 1014 (40%); 3.3208: 1521 (60%); 5.8258: 2028 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.1537, 2.0124, 3.3208, 5.8258 | 1.1537: 2028 (80%); 2.0124: 1521 (60%); 3.3208: 1014 (40%); 5.8258: 507 (20%) | 1.1537: 507 (20%); 2.0124: 1014 (40%); 3.3208: 1521 (60%); 5.8258: 2028 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.9946, 2.4396, 2.939, 3.7442 | 1.9946: 2028 (80%); 2.4396: 1521 (60%); 2.939: 1015 (40%); 3.7442: 507 (20%) | 1.9946: 507 (20%); 2.4396: 1014 (40%); 2.939: 1522 (60%); 3.7442: 2028 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0524, 0.0722, 0.0967, 0.1366 | 0.0524: 2028 (80%); 0.0722: 1523 (60%); 0.0967: 1016 (40%); 0.1366: 508 (20%) | 0.0524: 509 (20%); 0.0722: 1015 (40%); 0.0967: 1522 (60%); 0.1366: 2028 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.0705, 0.1834, 0.7675, 0.8942 | 0.0705: 2028 (80%); 0.1834: 1521 (60%); 0.7675: 1015 (40%); 0.8942: 508 (20%) | 0.0705: 507 (20%); 0.1834: 1015 (40%); 0.7675: 1521 (60%); 0.8942: 2028 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0543, 0.0741, 0.0997, 0.1398 | 0.0543: 2030 (80%); 0.0741: 1524 (60%); 0.0997: 1015 (40%); 0.1398: 508 (20%) | 0.0543: 509 (20%); 0.0741: 1015 (40%); 0.0997: 1521 (60%); 0.1398: 2029 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.0376, 0.3281, 0.5952, 0.9142 | 0.0376: 2028 (80%); 0.3281: 1521 (60%); 0.5952: 1015 (40%); 0.9142: 508 (20%) | 0.0376: 507 (20%); 0.3281: 1014 (40%); 0.5952: 1521 (60%); 0.9142: 2029 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0724, 0.0988, 0.1329, 0.1864 | 0.0724: 2029 (80%); 0.0988: 1524 (60%); 0.1329: 1015 (40%); 0.1864: 508 (20%) | 0.0724: 509 (20%); 0.0988: 1015 (40%); 0.1329: 1521 (60%); 0.1864: 2029 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.1532, 0.3711, 0.5714, 0.8106 | 0.1532: 2028 (80%); 0.3711: 1521 (60%); 0.5714: 1015 (40%); 0.8106: 508 (20%) | 0.1532: 507 (20%); 0.3711: 1014 (40%); 0.5714: 1522 (60%); 0.8106: 2028 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0543, -0.027, -0.0078, 0.0213 | -0.0543: 2028 (80%); -0.027: 1527 (60%); -0.0078: 1020 (40%); 0.0213: 515 (20%) | -0.0543: 507 (20%); -0.027: 1015 (40%); -0.0078: 1523 (60%); 0.0213: 2031 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1366, 0.1635, 0.2018, 0.2568 | 0.1366: 2025 (80%); 0.1635: 1521 (60%); 0.2018: 1015 (40%); 0.2568: 508 (20%) | 0.1366: 510 (20%); 0.1635: 1014 (40%); 0.2018: 1525 (60%); 0.2568: 2027 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 2535 (100%) | 0: 2387 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0878, -0.0214, 0.0401, 0.1084 | -0.0878: 2028 (80%); -0.0214: 1522 (60%); 0.0401: 1015 (40%); 0.1084: 508 (20%) | -0.0878: 509 (20%); -0.0214: 1015 (40%); 0.0401: 1521 (60%); 0.1084: 2029 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 2535 (100%); 1: 973 (38%) | 0: 1562 (62%); 1: 2117 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2452, -0.2071, -0.1579, -0.1197 | -0.2452: 2036 (80%); -0.2071: 1527 (60%); -0.1579: 1025 (40%); -0.1197: 509 (20%) | -0.2452: 519 (20%); -0.2071: 1017 (40%); -0.1579: 1527 (60%); -0.1197: 2089 (82%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2564, 0.5897, 0.6667, 0.7756 | 0.2564: 2034 (80%); 0.5897: 1551 (61%); 0.6667: 1091 (43%); 0.7756: 516 (20%) | 0.2564: 509 (20%); 0.5897: 1056 (42%); 0.6667: 1556 (61%); 0.7756: 2082 (82%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.3974, 0.6795, 0.8654 | 0.2628: 2091 (82%); 0.3974: 1557 (61%); 0.6795: 1047 (41%); 0.8654: 520 (21%) | 0.2628: 524 (21%); 0.3974: 1017 (40%); 0.6795: 1536 (61%); 0.8654: 2032 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1119, -0.0184, 0.0646, 0.1789 | -0.1119: 2034 (80%); -0.0184: 1526 (60%); 0.0646: 1020 (40%); 0.1789: 516 (20%) | -0.1119: 535 (21%); -0.0184: 1029 (41%); 0.0646: 1532 (60%); 0.1789: 2029 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.25, 0.4487, 0.6026, 0.7436 | 0.25: 2046 (81%); 0.4487: 1536 (61%); 0.6026: 1025 (40%); 0.7436: 508 (20%) | 0.25: 530 (21%); 0.4487: 1042 (41%); 0.6026: 1524 (60%); 0.7436: 2056 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.2821, 0.4487, 0.6731 | 0.109: 2065 (81%); 0.2821: 1535 (61%); 0.4487: 1019 (40%); 0.6731: 552 (22%) | 0.109: 523 (21%); 0.2821: 1048 (41%); 0.4487: 1524 (60%); 0.6731: 2051 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4858, -0.3421, -0.169, 0.0892 | -0.4858: 2032 (80%); -0.3421: 1529 (60%); -0.169: 1018 (40%); 0.0892: 515 (20%) | -0.4858: 508 (20%); -0.3421: 1016 (40%); -0.169: 1540 (61%); 0.0892: 2036 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.5192, 0.7436, 0.9487 | 0.3526: 2061 (81%); 0.5192: 1556 (61%); 0.7436: 1015 (40%); 0.9487: 511 (20%) | 0.3526: 519 (20%); 0.5192: 1071 (42%); 0.7436: 1544 (61%); 0.9487: 2054 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.3141, 0.5513, 0.7885 | 0.1282: 2029 (80%); 0.3141: 1548 (61%); 0.5513: 1029 (41%); 0.7885: 523 (21%) | 0.1282: 512 (20%); 0.3141: 1033 (41%); 0.5513: 1544 (61%); 0.7885: 2037 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0671, -0.057, -0.0384, 0 | -0.0671: 2041 (81%); -0.057: 1537 (61%); -0.0384: 1021 (40%); 0: 711 (28%) | -0.0671: 511 (20%); -0.057: 1019 (40%); -0.0384: 1522 (60%); 0: 2461 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4167, 0.641, 0.8718, 1 | 0.4167: 2035 (80%); 0.641: 1529 (60%); 0.8718: 1036 (41%); 1: 536 (21%) | 0.4167: 514 (20%); 0.641: 1016 (40%); 0.8718: 1545 (61%); 1: 2535 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.2756, 0.5962, 0.8974 | 0.1218: 2036 (80%); 0.2756: 1529 (60%); 0.5962: 1019 (40%); 0.8974: 513 (20%) | 0.1218: 510 (20%); 0.2756: 1031 (41%); 0.5962: 1548 (61%); 0.8974: 2031 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0, 0.0361, 0.084, 0.2037 | 0: 2036 (80%); 0.0361: 1539 (61%); 0.084: 1025 (40%); 0.2037: 512 (20%) | 0: 513 (20%); 0.0361: 1015 (40%); 0.084: 1527 (60%); 0.2037: 2033 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4583, 0.7778, 0.9359, 0.9744 | 0.4583: 2036 (80%); 0.7778: 1530 (60%); 0.9359: 1016 (40%); 0.9744: 537 (21%) | 0.4583: 517 (20%); 0.7778: 1022 (40%); 0.9359: 1545 (61%); 0.9744: 2068 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.084, 0.2151, 0.5641, 0.7692 | 0.084: 2035 (80%); 0.2151: 1537 (61%); 0.5641: 1017 (40%); 0.7692: 526 (21%) | 0.084: 536 (21%); 0.2151: 1019 (40%); 0.5641: 1528 (60%); 0.7692: 2048 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.011, 0.0791, 0.1876 | -0.0812: 2221 (88%); -0.011: 1521 (60%); 0.0791: 1017 (40%); 0.1876: 602 (24%) | -0.0812: 560 (22%); -0.011: 1014 (40%); 0.0791: 1535 (61%); 0.1876: 2059 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1544, -0.0157, 0.0481, 0.0968 | -0.1544: 2030 (80%); -0.0157: 1524 (60%); 0.0481: 1017 (40%); 0.0968: 515 (20%) | -0.1544: 515 (20%); -0.0157: 1017 (40%); 0.0481: 1534 (61%); 0.0968: 2061 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.5513, 0.7628, 0.8846 | 0.3526: 2051 (81%); 0.5513: 1546 (61%); 0.7628: 1016 (40%); 0.8846: 511 (20%) | 0.3526: 526 (21%); 0.5513: 1027 (41%); 0.7628: 1556 (61%); 0.8846: 2036 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1859, 0.3846, 0.641, 0.8269 | 0.1859: 2052 (81%); 0.3846: 1525 (60%); 0.641: 1024 (40%); 0.8269: 561 (22%) | 0.1859: 529 (21%); 0.3846: 1084 (43%); 0.641: 1532 (60%); 0.8269: 2049 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0475, 0.1105, 0.2395, 0.5169 | 0.0475: 2030 (80%); 0.1105: 1521 (60%); 0.2395: 1014 (40%); 0.5169: 507 (20%) | 0.0475: 512 (20%); 0.1105: 1014 (40%); 0.2395: 1521 (60%); 0.5169: 2028 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.9% | 28, 62, 83, 140 | 28: 2009 (79%); 62: 1512 (60%); 83: 1026 (40%); 140: 509 (20%) | 28: 529 (21%); 62: 1030 (41%); 83: 1506 (59%); 140: 2007 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.7391, 2.3027, 2.8956, 3.9244 | 1.7391: 2019 (80%); 2.3027: 1514 (60%); 2.8956: 1010 (40%); 3.9244: 505 (20%) | 1.7391: 506 (20%); 2.3027: 1010 (40%); 2.8956: 1514 (60%); 3.9244: 2019 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 16, 26, 33 | 8: 2103 (83%); 16: 1543 (61%); 26: 1038 (41%); 33: 583 (23%) | 8: 518 (20%); 16: 1050 (41%); 26: 1560 (62%); 33: 2029 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 2071 (82%); 2: 1529 (60%); 3: 978 (39%) | 1: 1006 (40%); 2: 1557 (61%); 3: 2051 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0146, -0.0044, 0.0106, 0.0227 | -0.0146: 2034 (80%); -0.0044: 1542 (61%); 0.0106: 1016 (40%); 0.0227: 515 (20%) | -0.0146: 508 (20%); -0.0044: 1016 (40%); 0.0106: 1525 (60%); 0.0227: 2029 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.7079, 25.8599, 26.5104, 27.2494 | 24.7079: 2028 (80%); 25.8599: 1524 (60%); 26.5104: 1014 (40%); 27.2494: 513 (20%) | 24.7079: 508 (20%); 25.8599: 1015 (40%); 26.5104: 1521 (60%); 27.2494: 2030 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.7492, -0.2184, 0.1154, 0.6704 | -0.7492: 2028 (80%); -0.2184: 1521 (60%); 0.1154: 1014 (40%); 0.6704: 507 (20%) | -0.7492: 507 (20%); -0.2184: 1014 (40%); 0.1154: 1521 (60%); 0.6704: 2028 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.6704, -0.1154, 0.2184, 0.7492 | -0.6704: 2028 (80%); -0.1154: 1521 (60%); 0.2184: 1014 (40%); 0.7492: 507 (20%) | -0.6704: 507 (20%); -0.1154: 1014 (40%); 0.2184: 1521 (60%); 0.7492: 2028 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0519, -0.0138, 0.0156, 0.0498 | -0.0519: 2030 (80%); -0.0138: 1525 (60%); 0.0156: 1017 (40%); 0.0498: 513 (20%) | -0.0519: 512 (20%); -0.0138: 1015 (40%); 0.0156: 1521 (60%); 0.0498: 2029 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9912, 8.4716, 8.703, 9.013 | 7.9912: 2028 (80%); 8.4716: 1521 (60%); 8.703: 1014 (40%); 9.013: 505 (20%) | 7.9912: 507 (20%); 8.4716: 1014 (40%); 8.703: 1521 (60%); 9.013: 2030 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 2516 (99%); 1: 774 (31%) | 0: 1742 (69%); 1: 2270 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0 | 0: 2015 (79%) | 0: 2107 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 2516 (99%); 1: 837 (33%) | 0: 1679 (66%); 1: 2240 (88%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 6, 140.4, 271 | 3: 2035 (80%); 6: 1574 (62%); 140.4: 1014 (40%); 271: 510 (20%) | 3: 678 (27%); 6: 1086 (43%); 140.4: 1521 (60%); 271: 2029 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 84, 138 | 1: 2057 (81%); 4: 1573 (62%); 84: 1018 (40%); 138: 513 (20%) | 1: 681 (27%); 4: 1047 (41%); 84: 1529 (60%); 138: 2029 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.8161, -0.2475, 0.1819, 0.7141 | -0.8161: 2028 (80%); -0.2475: 1521 (60%); 0.1819: 1015 (40%); 0.7141: 507 (20%) | -0.8161: 508 (20%); -0.2475: 1015 (40%); 0.1819: 1521 (60%); 0.7141: 2028 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.4976, -0.3339, 0.389, 1.7551 | -1.4976: 2028 (80%); -0.3339: 1521 (60%); 0.389: 1014 (40%); 1.7551: 507 (20%) | -1.4976: 507 (20%); -0.3339: 1014 (40%); 0.389: 1521 (60%); 1.7551: 2028 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.0718, -0.4622, 0.6436, 2.3934 | -2.0718: 2028 (80%); -0.4622: 1521 (60%); 0.6436: 1014 (40%); 2.3934: 507 (20%) | -2.0718: 507 (20%); -0.4622: 1014 (40%); 0.6436: 1521 (60%); 2.3934: 2028 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.8919, -0.2993, 0.2, 0.7211 | -0.8919: 2028 (80%); -0.2993: 1521 (60%); 0.2: 1014 (40%); 0.7211: 508 (20%) | -0.8919: 507 (20%); -0.2993: 1014 (40%); 0.2: 1521 (60%); 0.7211: 2029 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.2051, -0.2614, 0.255, 1.248 | -1.2051: 2028 (80%); -0.2614: 1521 (60%); 0.255: 1015 (40%); 1.248: 507 (20%) | -1.2051: 507 (20%); -0.2614: 1014 (40%); 0.255: 1522 (60%); 1.248: 2028 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.5553, -0.3436, 0.3967, 1.8153 | -1.5553: 2028 (80%); -0.3436: 1521 (60%); 0.3967: 1014 (40%); 1.8153: 507 (20%) | -1.5553: 507 (20%); -0.3436: 1014 (40%); 0.3967: 1521 (60%); 1.8153: 2028 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 39.954, 47.87, 54.014, 61.784 | 39.954: 2028 (80%); 47.87: 1522 (60%); 54.014: 1014 (40%); 61.784: 507 (20%) | 39.954: 507 (20%); 47.87: 1016 (40%); 54.014: 1521 (60%); 61.784: 2028 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.3% | -0.1381, -0.0314, 0.0522, 0.1675 | -0.1381: 2013 (79%); -0.0314: 1510 (60%); 0.0522: 1007 (40%); 0.1675: 504 (20%) | -0.1381: 505 (20%); -0.0314: 1008 (40%); 0.0522: 1510 (60%); 0.1675: 2013 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.9% | 0.0059, 0.0134, 0.0246, 0.0446 | 0.0059: 2023 (80%); 0.0134: 1521 (60%); 0.0246: 1015 (40%); 0.0446: 506 (20%) | 0.0059: 509 (20%); 0.0134: 1011 (40%); 0.0246: 1517 (60%); 0.0446: 2026 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 9 | 0: 2535 (100%); 2: 1530 (60%); 4: 1086 (43%); 9: 554 (22%) | 0: 600 (24%); 2: 1273 (50%); 4: 1600 (63%); 9: 2041 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 2535 (100%); 0.1667: 513 (20%) | 0: 1697 (67%); 0.1667: 2062 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667, 0.4303, 0.6667 | 0: 2535 (100%); 0.1667: 1535 (61%); 0.4303: 1014 (40%); 0.6667: 570 (22%) | 0: 953 (38%); 0.1667: 1023 (40%); 0.4303: 1521 (60%); 0.6667: 2056 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 7 | 0: 2535 (100%); 1: 1785 (70%); 3: 1051 (41%); 7: 515 (20%) | 0: 750 (30%); 1: 1205 (48%); 3: 1662 (66%); 7: 2087 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 2535 (100%); 2: 1530 (60%); 4: 1086 (43%); 9: 554 (22%) | 0: 600 (24%); 2: 1273 (50%); 4: 1600 (63%); 9: 2041 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 2535 (100%); 1: 1828 (72%); 3: 1130 (45%); 8: 516 (20%) | 0: 707 (28%); 1: 1132 (45%); 3: 1583 (62%); 8: 2081 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2389, 0.381, 0.5714 | 0: 2343 (92%); 0.2389: 1521 (60%); 0.381: 1015 (40%); 0.5714: 517 (20%) | 0: 531 (21%); 0.2389: 1014 (40%); 0.381: 1522 (60%); 0.5714: 2029 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2085, 0.6154 | 0: 2295 (91%); 0.2085: 1014 (40%); 0.6154: 509 (20%) | 0: 1330 (52%); 0.2085: 1521 (60%); 0.6154: 2031 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3049, 0.6 | 0: 2322 (92%); 0.3049: 1014 (40%); 0.6: 522 (21%) | 0: 1105 (44%); 0.3049: 1521 (60%); 0.6: 2037 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3049, 0.6 | 0: 2322 (92%); 0.3049: 1014 (40%); 0.6: 522 (21%) | 0: 1105 (44%); 0.3049: 1521 (60%); 0.6: 2037 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1548, 0, 0.1667 | -0.1548: 2028 (80%); 0: 1817 (72%); 0.1667: 517 (20%) | -0.1548: 508 (20%); 0: 1795 (71%); 0.1667: 2040 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7311, -0.3303, 0, 1.125 | -0.7311: 2028 (80%); -0.3303: 1526 (60%); 0: 1333 (53%); 1.125: 507 (20%) | -0.7311: 507 (20%); -0.3303: 1018 (40%); 0: 1535 (61%); 1.125: 2028 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 2143 (85%); 4: 1671 (66%); 7: 1057 (42%); 11: 516 (20%) | 2: 626 (25%); 4: 1087 (43%); 7: 1621 (64%); 11: 2091 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0418, -0.0172, 0.016, 0.055 | -0.0418: 2027 (80%); -0.0172: 1522 (60%); 0.016: 1015 (40%); 0.055: 508 (20%) | -0.0418: 508 (20%); -0.0172: 1013 (40%); 0.016: 1520 (60%); 0.055: 2027 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0485, -0.0143, 0.0112, 0.0448 | -0.0485: 2026 (80%); -0.0143: 1522 (60%); 0.0112: 1017 (40%); 0.0448: 510 (20%) | -0.0485: 509 (20%); -0.0143: 1013 (40%); 0.0112: 1518 (60%); 0.0448: 2025 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0427, -0.0209, 0.0193, 0.0539 | -0.0427: 2027 (80%); -0.0209: 1519 (60%); 0.0193: 1015 (40%); 0.0539: 507 (20%) | -0.0427: 508 (20%); -0.0209: 1016 (40%); 0.0193: 1520 (60%); 0.0539: 2028 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 99.3% | 1.2292, 4.1424, 7.4218, 12.7886 | 1.2292: 2013 (79%); 4.1424: 1510 (60%); 7.4218: 1007 (40%); 12.7886: 504 (20%) | 1.2292: 504 (20%); 4.1424: 1007 (40%); 7.4218: 1510 (60%); 12.7886: 2013 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -18.3824, -3.3956, 6.9374, 24.6886 | -18.3824: 2028 (80%); -3.3956: 1521 (60%); 6.9374: 1014 (40%); 24.6886: 507 (20%) | -18.3824: 507 (20%); -3.3956: 1014 (40%); 6.9374: 1521 (60%); 24.6886: 2028 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.037, 0.0486, 0.0664, 0.092 | 0.037: 2030 (80%); 0.0486: 1529 (60%); 0.0664: 1015 (40%); 0.092: 508 (20%) | 0.037: 510 (20%); 0.0486: 1016 (40%); 0.0664: 1523 (60%); 0.092: 2028 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1488, 0.3216, 0.5137, 0.7559 | 0.1488: 2028 (80%); 0.3216: 1521 (60%); 0.5137: 1015 (40%); 0.7559: 507 (20%) | 0.1488: 507 (20%); 0.3216: 1014 (40%); 0.5137: 1521 (60%); 0.7559: 2028 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.694, -0.5315, 0.5376, 1.5156 | -1.694: 2028 (80%); -0.5315: 1521 (60%); 0.5376: 1015 (40%); 1.5156: 507 (20%) | -1.694: 507 (20%); -0.5315: 1014 (40%); 0.5376: 1521 (60%); 1.5156: 2028 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.6824, -0.3318, 0.3689, 0.8393 | -0.6824: 2028 (80%); -0.3318: 1521 (60%); 0.3689: 1014 (40%); 0.8393: 508 (20%) | -0.6824: 507 (20%); -0.3318: 1014 (40%); 0.3689: 1521 (60%); 0.8393: 2029 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.3101, -0.8777, 0.8547, 1.9655 | -2.3101: 2028 (80%); -0.8777: 1521 (60%); 0.8547: 1014 (40%); 1.9655: 507 (20%) | -2.3101: 507 (20%); -0.8777: 1014 (40%); 0.8547: 1521 (60%); 1.9655: 2028 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.2298, -1.578, 1.6274, 5.8648 | -4.2298: 2028 (80%); -1.578: 1521 (60%); 1.6274: 1014 (40%); 5.8648: 507 (20%) | -4.2298: 507 (20%); -1.578: 1014 (40%); 1.6274: 1521 (60%); 5.8648: 2028 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 43.638, 47.8, 51.074, 55.234 | 43.638: 2028 (80%); 47.8: 1522 (60%); 51.074: 1014 (40%); 55.234: 507 (20%) | 43.638: 507 (20%); 47.8: 1015 (40%); 51.074: 1521 (60%); 55.234: 2028 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 4.858, 15.76, 72.262, 92.718 | 4.858: 2028 (80%); 15.76: 1523 (60%); 72.262: 1014 (40%); 92.718: 507 (20%) | 4.858: 507 (20%); 15.76: 1015 (40%); 72.262: 1521 (60%); 92.718: 2028 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 45.38, 48.276, 51.15, 54.45 | 45.38: 2029 (80%); 48.276: 1521 (60%); 51.15: 1015 (40%); 54.45: 509 (20%) | 45.38: 510 (20%); 48.276: 1014 (40%); 51.15: 1524 (60%); 54.45: 2029 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 37.978, 43.936, 53.226, 60.45 | 37.978: 2028 (80%); 43.936: 1521 (60%); 53.226: 1014 (40%); 60.45: 508 (20%) | 37.978: 507 (20%); 43.936: 1014 (40%); 53.226: 1521 (60%); 60.45: 2029 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 2532 (100%) | 0: 2535 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0298, 0.0434, 0.0595, 0.0869 | 0.0298: 2033 (80%); 0.0434: 1524 (60%); 0.0595: 1015 (40%); 0.0869: 513 (20%) | 0.0298: 512 (20%); 0.0434: 1019 (40%); 0.0595: 1524 (60%); 0.0869: 2037 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0854, -0.0585, -0.0434, -0.0322 | -0.0854: 2029 (80%); -0.0585: 1522 (60%); -0.0434: 1022 (40%); -0.0322: 509 (20%) | -0.0854: 509 (20%); -0.0585: 1016 (40%); -0.0434: 1522 (60%); -0.0322: 2031 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 2535 (100%); 2: 588 (23%) | 0: 1666 (66%); 2: 2097 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 28, 42, 57, 71 | 28: 2056 (81%); 42: 1557 (61%); 57: 1041 (41%); 71: 522 (21%) | 28: 538 (21%); 42: 1011 (40%); 57: 1520 (60%); 71: 2020 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.4% | 0.0122, 0.0178, 0.0259, 0.0414 | 0.0122: 1999 (79%); 0.0178: 1498 (59%); 0.0259: 997 (39%); 0.0414: 499 (20%) | 0.0122: 496 (20%); 0.0178: 997 (39%); 0.0259: 1498 (59%); 0.0414: 1996 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.2913, 0.4283, 0.5695, 0.7081 | 0.2913: 2028 (80%); 0.4283: 1521 (60%); 0.5695: 1014 (40%); 0.7081: 508 (20%) | 0.2913: 509 (20%); 0.4283: 1014 (40%); 0.5695: 1521 (60%); 0.7081: 2029 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 37.28, 72, 102.74, 148.34 | 37.28: 2028 (80%); 72: 1522 (60%); 102.74: 1014 (40%); 148.34: 507 (20%) | 37.28: 507 (20%); 72: 1015 (40%); 102.74: 1521 (60%); 148.34: 2028 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -3.607, -0.866, 0.5435, 2.7804 | -3.607: 2028 (80%); -0.866: 1521 (60%); 0.5435: 1014 (40%); 2.7804: 507 (20%) | -3.607: 507 (20%); -0.866: 1014 (40%); 0.5435: 1521 (60%); 2.7804: 2028 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 29.978, 45.246, 59.614, 74.54 | 29.978: 2028 (80%); 45.246: 1521 (60%); 59.614: 1014 (40%); 74.54: 507 (20%) | 29.978: 507 (20%); 45.246: 1014 (40%); 59.614: 1521 (60%); 74.54: 2028 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 23.148, 39.62, 62.082, 79.424 | 23.148: 2028 (80%); 39.62: 1521 (60%); 62.082: 1014 (40%); 79.424: 507 (20%) | 23.148: 507 (20%); 39.62: 1014 (40%); 62.082: 1521 (60%); 79.424: 2028 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 4.25, 26.618, 71.748, 95.96 | 4.25: 2028 (80%); 26.618: 1521 (60%); 71.748: 1014 (40%); 95.96: 508 (20%) | 4.25: 507 (20%); 26.618: 1014 (40%); 71.748: 1521 (60%); 95.96: 2029 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 6.156, 84.572, 100 | 0: 2535 (100%); 6.156: 1521 (60%); 84.572: 1014 (40%); 100: 762 (30%) | 0: 882 (35%); 6.156: 1014 (40%); 84.572: 1521 (60%); 100: 2535 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 17 | 4: 2100 (83%); 8: 1607 (63%); 13: 1019 (40%); 17: 606 (24%) | 4: 569 (22%); 8: 1046 (41%); 13: 1629 (64%); 17: 2083 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 18 | 5: 2063 (81%); 9: 1626 (64%); 14: 1029 (41%); 18: 573 (23%) | 5: 603 (24%); 9: 1026 (40%); 14: 1614 (64%); 18: 2104 (83%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 44.13, 48.49, 52.534, 56.732 | 44.13: 2029 (80%); 48.49: 1522 (60%); 52.534: 1014 (40%); 56.732: 507 (20%) | 44.13: 508 (20%); 48.49: 1015 (40%); 52.534: 1521 (60%); 56.732: 2028 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1706, 0.369, 0.6349, 0.8373 | 0.1706: 2036 (80%); 0.369: 1522 (60%); 0.6349: 1032 (41%); 0.8373: 509 (20%) | 0.1706: 518 (20%); 0.369: 1019 (40%); 0.6349: 1523 (60%); 0.8373: 2041 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.91, 17.31, 19.63, 24.54 | 14.91: 2036 (80%); 17.31: 1526 (60%); 19.63: 1017 (40%); 24.54: 510 (20%) | 14.91: 520 (21%); 17.31: 1015 (40%); 19.63: 1528 (60%); 24.54: 2038 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.91, 17.31, 19.63, 24.54 | 14.91: 2036 (80%); 17.31: 1526 (60%); 19.63: 1017 (40%); 24.54: 510 (20%) | 14.91: 520 (21%); 17.31: 1015 (40%); 19.63: 1528 (60%); 24.54: 2038 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8579, 0.8867, 0.921, 0.9657 | 0.8579: 2028 (80%); 0.8867: 1524 (60%); 0.921: 1021 (40%); 0.9657: 507 (20%) | 0.8579: 508 (20%); 0.8867: 1025 (40%); 0.921: 1523 (60%); 0.9657: 2028 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.69, 0.84, 0.98, 1.22 | 0.69: 2055 (81%); 0.84: 1540 (61%); 0.98: 1039 (41%); 1.22: 508 (20%) | 0.69: 513 (20%); 0.84: 1029 (41%); 0.98: 1522 (60%); 1.22: 2038 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0156, 0.0333, 0.0587, 0.1041 | 0.0156: 2030 (80%); 0.0333: 1522 (60%); 0.0587: 1016 (40%); 0.1041: 509 (20%) | 0.0156: 510 (20%); 0.0333: 1016 (40%); 0.0587: 1524 (60%); 0.1041: 2028 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 45.2974, 77.4451, 118.8613, 207.7471 | 45.2974: 2028 (80%); 77.4451: 1521 (60%); 118.8613: 1014 (40%); 207.7471: 507 (20%) | 45.2974: 507 (20%); 77.4451: 1014 (40%); 118.8613: 1521 (60%); 207.7471: 2028 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.5604, 75.1494, 114.5466, 200.5802 | 43.5604: 2028 (80%); 75.1494: 1521 (60%); 114.5466: 1014 (40%); 200.5802: 507 (20%) | 43.5604: 507 (20%); 75.1494: 1014 (40%); 114.5466: 1521 (60%); 200.5802: 2028 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.669, 71.6961, 111.2293, 192.9361 | 41.669: 2028 (80%); 71.6961: 1521 (60%); 111.2293: 1014 (40%); 192.9361: 507 (20%) | 41.669: 507 (20%); 71.6961: 1014 (40%); 111.2293: 1521 (60%); 192.9361: 2028 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.0866, 79.5377, 122.9624, 215.0244 | 47.0866: 2028 (80%); 79.5377: 1521 (60%); 122.9624: 1014 (40%); 215.0244: 507 (20%) | 47.0866: 507 (20%); 79.5377: 1014 (40%); 122.9624: 1521 (60%); 215.0244: 2028 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.7624, 81.5489, 127.3154, 220.2284 | 48.7624: 2028 (80%); 81.5489: 1521 (60%); 127.3154: 1014 (40%); 220.2284: 507 (20%) | 48.7624: 507 (20%); 81.5489: 1014 (40%); 127.3154: 1521 (60%); 220.2284: 2028 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2535 (100%) | 0: 2257 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2535 (100%) | 0: 2284 (90%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0423, -0.0124, 0.0122, 0.0486 | -0.0423: 2028 (80%); -0.0124: 1521 (60%); 0.0122: 1015 (40%); 0.0486: 509 (20%) | -0.0423: 510 (20%); -0.0124: 1014 (40%); 0.0122: 1521 (60%); 0.0486: 2028 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.8% | 0.5471, 0.8102, 1.0391, 1.3204 | 0.5471: 2023 (80%); 0.8102: 1517 (60%); 1.0391: 1012 (40%); 1.3204: 506 (20%) | 0.5471: 506 (20%); 0.8102: 1012 (40%); 1.0391: 1517 (60%); 1.3204: 2023 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.8% | 3, 5, 7, 9 | 3: 2094 (83%); 5: 1634 (64%); 7: 1142 (45%); 9: 635 (25%) | 3: 653 (26%); 5: 1135 (45%); 7: 1615 (64%); 9: 2169 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.6% | 0.1895, 0.2294, 0.2811, 0.3695 | 0.1895: 2022 (80%); 0.2294: 1517 (60%); 0.2811: 1012 (40%); 0.3695: 506 (20%) | 0.1895: 506 (20%); 0.2294: 1011 (40%); 0.2811: 1517 (60%); 0.3695: 2021 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.6% | 3, 5, 8, 9 | 3: 2110 (83%); 5: 1704 (67%); 8: 1016 (40%); 9: 725 (29%) | 3: 625 (25%); 5: 1043 (41%); 8: 1801 (71%); 9: 2130 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.8% | 0.0232, 0.0318, 0.0428, 0.0613 | 0.0232: 2023 (80%); 0.0318: 1519 (60%); 0.0428: 1013 (40%); 0.0613: 510 (20%) | 0.0232: 511 (20%); 0.0318: 1013 (40%); 0.0428: 1519 (60%); 0.0613: 2023 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.8% | 3, 5, 7, 9 | 3: 2116 (83%); 5: 1691 (67%); 7: 1236 (49%); 9: 699 (28%) | 3: 602 (24%); 5: 1074 (42%); 7: 1543 (61%); 9: 2150 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.8% | -0.1974, -0.0453, 0.0752, 0.2504 | -0.1974: 2023 (80%); -0.0453: 1518 (60%); 0.0752: 1012 (40%); 0.2504: 506 (20%) | -0.1974: 508 (20%); -0.0453: 1012 (40%); 0.0752: 1517 (60%); 0.2504: 2023 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.8% | 2, 4, 6, 9 | 2: 2206 (87%); 4: 1698 (67%); 6: 1180 (47%); 9: 509 (20%) | 2: 591 (23%); 4: 1082 (43%); 6: 1565 (62%); 9: 2245 (89%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.0% |
| 8k_item_5_02_filed_within_7d | 3.0% |
| above_avwap_20high | 37.0% |
| above_avwap_20low | 57.2% |
| above_avwap_252low | 84.0% |
| above_avwap_50low | 79.3% |
| above_cam_r3 | 30.3% |
| above_cam_r4 | 19.5% |
| above_cpr | 45.4% |
| above_pivot | 44.5% |
| above_prev_high | 24.9% |
| above_prev_high_clearance_atr_05 | 10.2% |
| above_prev_low | 65.4% |
| above_r1 | 21.6% |
| above_r2 | 11.4% |
| above_vwap | 53.0% |
| above_wood_p | 46.2% |
| ad_rising | 49.0% |
| adx_cross_up | 0.9% |
| adx_cross_up_20 | 1.1% |
| adx_di_bear | 53.5% |
| adx_di_bull | 46.5% |
| adx_strong | 8.2% |
| adx_trending | 46.4% |
| ao_cross_dn | 3.1% |
| ao_cross_up | 3.4% |
| ao_positive | 50.6% |
| ao_twin_peaks_bull | 2.4% |
| at_key_fib | 21.3% |
| at_key_fib_wide | 51.0% |
| avwap_20high_loss_recent_3d | 18.0% |
| avwap_20high_reclaim_recent_3d | 24.6% |
| avwap_20low_loss_recent_3d | 32.3% |
| avwap_20low_reclaim_recent_3d | 12.1% |
| avwap_252low_loss_recent_3d | 1.2% |
| avwap_252low_reclaim_recent_3d | 9.6% |
| avwap_50low_loss_recent_3d | 15.5% |
| avwap_50low_reclaim_recent_3d | 10.9% |
| bb_10_20_above_mid | 47.7% |
| bb_10_20_expanding | 77.6% |
| bb_10_20_pctb_gt_75 | 41.7% |
| bb_10_20_pctb_gt_8 | 35.5% |
| bb_10_20_pctb_gt_85 | 27.2% |
| bb_10_20_pctb_gt_9 | 19.1% |
| bb_10_20_pctb_gt_95 | 11.8% |
| bb_10_20_pctb_lt_05 | 16.4% |
| bb_10_20_pctb_lt_1 | 24.7% |
| bb_10_20_pctb_lt_15 | 34.3% |
| bb_10_20_pctb_lt_2 | 42.6% |
| bb_10_20_pctb_lt_25 | 47.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 7.1% |
| bb_10_20_reclaim_from_upper_recent_3d | 7.3% |
| bb_10_20_squeeze | 47.3% |
| bb_10_20_touch_lower | 20.7% |
| bb_10_20_touch_upper | 13.8% |
| bb_20_15_above_mid | 47.3% |
| bb_20_15_expanding | 40.6% |
| bb_20_15_pctb_gt_75 | 29.8% |
| bb_20_15_pctb_gt_8 | 26.8% |
| bb_20_15_pctb_gt_85 | 23.9% |
| bb_20_15_pctb_gt_9 | 20.9% |
| bb_20_15_pctb_gt_95 | 17.8% |
| bb_20_15_pctb_lt_05 | 21.0% |
| bb_20_15_pctb_lt_1 | 24.7% |
| bb_20_15_pctb_lt_15 | 28.2% |
| bb_20_15_pctb_lt_2 | 31.9% |
| bb_20_15_pctb_lt_25 | 35.0% |
| bb_20_15_reclaim_from_lower_recent_3d | 3.3% |
| bb_20_15_reclaim_from_upper_recent_3d | 5.5% |
| bb_20_15_squeeze | 45.2% |
| bb_20_15_touch_lower | 23.3% |
| bb_20_15_touch_upper | 18.7% |
| bb_20_20_above_mid | 47.3% |
| bb_20_20_expanding | 40.6% |
| bb_20_20_pctb_gt_75 | 24.7% |
| bb_20_20_pctb_gt_8 | 20.9% |
| bb_20_20_pctb_gt_85 | 16.6% |
| bb_20_20_pctb_gt_9 | 12.6% |
| bb_20_20_pctb_gt_95 | 9.2% |
| bb_20_20_pctb_lt_05 | 10.3% |
| bb_20_20_pctb_lt_1 | 14.7% |
| bb_20_20_pctb_lt_15 | 19.6% |
| bb_20_20_pctb_lt_2 | 24.7% |
| bb_20_20_pctb_lt_25 | 29.7% |
| bb_20_20_reclaim_from_lower_recent_3d | 2.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 3.6% |
| bb_20_20_squeeze | 26.1% |
| bb_20_20_touch_lower | 11.5% |
| bb_20_20_touch_upper | 9.4% |
| bearish_engulfing | 4.5% |
| bearish_pin_bar | 4.7% |
| below_avwap_20high | 63.0% |
| below_avwap_20low | 42.8% |
| below_avwap_252low | 16.0% |
| below_avwap_50low | 20.7% |
| below_cam_s3 | 41.5% |
| below_cam_s4 | 27.1% |
| below_cpr | 55.4% |
| below_ema_20 | 54.2% |
| below_ema_200 | 47.7% |
| below_ema_200_break_recent_5d | 0.7% |
| below_ema_20_break_recent_5d | 39.7% |
| below_ema_21 | 54.5% |
| below_ema_21_break_recent_5d | 39.3% |
| below_ema_50 | 51.4% |
| below_ema_50_break_recent_5d | 16.5% |
| below_ema_9 | 52.5% |
| below_ema_9_break_recent_5d | 41.4% |
| below_prev_high | 74.8% |
| below_prev_low | 34.4% |
| below_prev_low_clearance_atr_05 | 15.3% |
| below_s1 | 29.9% |
| below_s2 | 16.5% |
| below_sma_20 | 52.7% |
| below_sma_200 | 47.7% |
| below_sma_21 | 52.9% |
| below_sma_50 | 51.1% |
| below_sma_9 | 52.4% |
| below_vwap | 47.0% |
| blowoff_recent_3d | 0.3% |
| bullish_engulfing | 2.4% |
| bullish_pin_bar | 5.8% |
| capitulation_recent_3d | 0.2% |
| ceo_buy | 1.7% |
| cfo_buy | 0.7% |
| chandelier_long_bullish | 61.5% |
| chandelier_long_flip_dn | 12.8% |
| chandelier_short_bearish | 64.7% |
| chandelier_short_flip_up | 8.2% |
| classification_change_from_tech | 50.0% |
| classification_change_to_defensive | 50.0% |
| close_above_open | 37.5% |
| close_below_open | 61.2% |
| close_in_bottom_40pct_of_range | 49.2% |
| close_in_top_40pct_of_range | 32.7% |
| cluster_buy | 0.8% |
| cmf_cross_dn | 4.4% |
| cmf_cross_up | 2.3% |
| cmf_negative | 47.7% |
| cmf_positive | 52.3% |
| concentrated_sell | 6.4% |
| cpr_narrow | 89.1% |
| cpr_narrow_tight | 27.6% |
| cup_handle_detected | 13.6% |
| cup_handle_neckline_break_retest_long | 1.3% |
| dc10_breakout_dn | 21.2% |
| dc10_breakout_dn_1pct | 36.7% |
| dc10_breakout_up | 16.0% |
| dc10_breakout_up_1pct | 27.9% |
| dc10_new_high | 26.0% |
| dc10_strong_breakout_dn | 6.2% |
| dc10_strong_breakout_up | 4.7% |
| dc20_breakout_dn | 5.5% |
| dc20_breakout_up | 4.9% |
| dc20_new_high | 9.7% |
| dc20_resistance_break_retest_strong | 4.2% |
| dc20_support_break_retest_strong | 4.4% |
| defensive_leadership | 53.4% |
| director_only_buy | 3.9% |
| doji | 6.0% |
| double_bottom_detected | 10.4% |
| double_top_detected | 12.7% |
| dpi_elevated | 52.7% |
| drying_volume_on_down_turn | 36.3% |
| drying_volume_on_up_turn | 24.7% |
| ema_20_50_bearish | 48.5% |
| ema_20_50_bullish | 51.5% |
| ema_20_50_death_cross | 0.7% |
| ema_20_50_golden_cross | 0.6% |
| ema_50_200_bearish | 48.1% |
| ema_50_200_bullish | 51.9% |
| ema_50_200_death_cross | 0.1% |
| ema_50_200_golden_cross | 0.0% |
| ema_9_21_bearish | 49.7% |
| ema_9_21_bullish | 50.3% |
| ema_9_21_death_cross | 4.7% |
| ema_9_21_golden_cross | 4.2% |
| evening_star | 6.5% |
| flag_bear_break_retest_short | 0.1% |
| flag_bear_broke | 0.2% |
| flag_bear_detected | 0.8% |
| flag_bull_break_retest_long | 0.4% |
| flag_bull_broke | 0.5% |
| flag_bull_detected | 2.1% |
| force_index_cross_dn | 12.1% |
| force_index_cross_up | 7.5% |
| force_index_positive | 46.8% |
| gap_dn_1_5pct | 8.2% |
| gap_dn_2pct | 4.8% |
| gap_up_1_5pct | 9.7% |
| gap_up_2pct | 6.7% |
| hammer | 4.4% |
| head_shoulders_bottom_detected | 3.4% |
| head_shoulders_top_detected | 3.2% |
| house_cluster_buy | 3.6% |
| house_cluster_sell | 4.0% |
| htf_aligned_bear | 28.8% |
| htf_aligned_bull | 28.9% |
| htf_disagreement | 4.0% |
| hull_bearish | 51.7% |
| hull_bullish | 48.3% |
| hull_flip_dn | 7.8% |
| hull_flip_up | 4.4% |
| ichi_above_cloud | 43.4% |
| ichi_above_cloud_break_recent_5d | 3.9% |
| ichi_below_cloud | 42.0% |
| ichi_below_cloud_break_recent_5d | 4.9% |
| ichi_cloud_thick | 86.9% |
| ichi_tk_bearish | 46.2% |
| ichi_tk_bullish | 48.8% |
| ichi_tk_cross_dn | 2.5% |
| ichi_tk_cross_up | 3.0% |
| ichi_weekly_above_cloud | 39.8% |
| ichi_weekly_below_cloud | 35.5% |
| ichi_weekly_in_cloud | 24.8% |
| in_reversal_window | 1.7% |
| inside_bar | 10.7% |
| inside_cpr | 1.4% |
| inside_kc | 93.6% |
| insider_cluster_active | 23.7% |
| institutional_buy | 89.4% |
| institutional_negative | 4.7% |
| institutional_persistence_growing | 45.7% |
| institutional_persistence_strong | 62.0% |
| institutional_strong_buy | 79.5% |
| inverted_cup_handle_detected | 10.5% |
| is_friday | 19.1% |
| is_halloween_period | 54.1% |
| is_halloween_period_first_day | 0.7% |
| is_january | 10.3% |
| is_january_extended | 12.7% |
| is_monday | 18.3% |
| is_pre_holiday | 3.9% |
| is_summer_period | 45.9% |
| is_totm_window | 35.8% |
| is_totm_window_first_day | 11.2% |
| is_week_open | 21.4% |
| kc_touch_lower | 4.5% |
| kc_touch_upper | 4.2% |
| large_dollar_buy | 1.4% |
| macd_12_26_9_bearish | 51.3% |
| macd_12_26_9_bullish | 48.7% |
| macd_12_26_9_crossover_dn | 5.3% |
| macd_12_26_9_crossover_up | 2.8% |
| macd_8_21_5_bearish | 52.3% |
| macd_8_21_5_bullish | 47.7% |
| macd_8_21_5_crossover_dn | 3.2% |
| macd_8_21_5_crossover_up | 1.1% |
| marubozu_bear | 0.9% |
| marubozu_bull | 0.8% |
| mfi_broad_overbought | 8.2% |
| mfi_broad_oversold | 5.4% |
| mfi_overbought | 1.3% |
| mfi_oversold | 0.6% |
| monthly_above_sma_12 | 51.3% |
| monthly_above_sma_6 | 50.2% |
| monthly_bias_bear | 40.3% |
| monthly_bias_bull | 41.9% |
| monthly_momentum_pos | 52.7% |
| morning_star | 3.5% |
| near_52w_high | 0.2% |
| near_52w_high_95pct | 6.9% |
| near_52w_high_retest_long | 0.2% |
| near_52w_low_105pct | 0.6% |
| near_52w_low_retest_short | 0.7% |
| near_avwap_20high_atr_05x | 15.8% |
| near_avwap_20high_atr_10x | 47.8% |
| near_avwap_20high_atr_15x | 79.6% |
| near_avwap_20high_atr_20x | 94.4% |
| near_avwap_20low_atr_05x | 17.8% |
| near_avwap_20low_atr_10x | 48.5% |
| near_avwap_20low_atr_15x | 76.5% |
| near_avwap_20low_atr_20x | 90.4% |
| near_avwap_252low_atr_05x | 7.3% |
| near_avwap_252low_atr_10x | 19.7% |
| near_avwap_252low_atr_15x | 34.3% |
| near_avwap_252low_atr_20x | 45.8% |
| near_avwap_50low_atr_05x | 15.7% |
| near_avwap_50low_atr_10x | 38.9% |
| near_avwap_50low_atr_15x | 64.0% |
| near_avwap_50low_atr_20x | 79.2% |
| near_cam_r3 | 10.6% |
| near_cam_s3 | 14.6% |
| near_cam_s4 | 11.7% |
| near_fib_236 | 6.2% |
| near_fib_382 | 7.8% |
| near_fib_500 | 7.3% |
| near_fib_618 | 6.4% |
| near_fib_786 | 4.2% |
| near_pivot | 11.1% |
| near_prev_close | 12.9% |
| near_prev_high | 9.0% |
| near_prev_low | 11.6% |
| near_r1 | 9.5% |
| near_r1_wide | 42.4% |
| near_r2 | 3.9% |
| near_r2_wide | 24.7% |
| near_s1 | 12.7% |
| near_s1_wide | 49.3% |
| near_s2 | 5.8% |
| near_s2_wide | 33.1% |
| near_s3 | 3.8% |
| near_wood_r1 | 8.2% |
| near_wood_s1 | 8.4% |
| news_uses_polygon_score | 23.2% |
| obv_bearish | 50.8% |
| obv_bullish | 49.2% |
| obv_diverge_bull | 5.0% |
| obv_falling | 53.1% |
| obv_rising | 46.9% |
| outside_bar | 7.2% |
| pead_negative_surprise | 16.7% |
| pead_positive_surprise | 25.0% |
| pin_bar | 10.6% |
| po3_accumulation_active | 41.7% |
| po3_bearish | 11.3% |
| po3_bullish | 5.8% |
| po3_manipulation_sweep_down | 22.2% |
| po3_manipulation_sweep_up | 9.3% |
| po3_mmbm_setup | 0.5% |
| po3_mmsm_setup | 1.2% |
| po3_sweep_above_prior_high | 48.2% |
| po3_sweep_below_prior_low | 53.1% |
| ppo_bullish | 48.1% |
| ppo_crossover_dn | 4.9% |
| ppo_crossover_up | 3.1% |
| pre_fomc_d0 | 2.5% |
| pre_fomc_d1 | 2.7% |
| pre_fomc_window | 5.2% |
| price_above_dema | 47.6% |
| price_above_ema_20 | 45.8% |
| price_above_ema_200 | 52.3% |
| price_above_ema_200_break_recent_5d | 0.6% |
| price_above_ema_20_break_recent_5d | 33.7% |
| price_above_ema_21 | 45.5% |
| price_above_ema_21_break_recent_5d | 32.9% |
| price_above_ema_50 | 48.6% |
| price_above_ema_50_break_recent_5d | 14.0% |
| price_above_ema_9 | 47.5% |
| price_above_ema_9_break_recent_5d | 35.3% |
| price_above_hull | 47.5% |
| price_above_sma_200 | 52.3% |
| price_above_sma_21 | 47.1% |
| price_above_sma_50 | 48.9% |
| price_above_tema | 47.5% |
| price_below_dema | 52.4% |
| price_below_hull | 52.5% |
| price_below_tema | 52.5% |
| psar_bullish | 47.3% |
| psar_flip_dn | 8.8% |
| psar_flip_up | 5.0% |
| r1_break_retest_long | 45.5% |
| recent_blowoff_at_r3 | 0.0% |
| resistance_break_retest | 7.2% |
| risk_off_regime_bond_signal | 20.6% |
| risk_off_regime_bond_signal_strong | 6.9% |
| risk_off_regime_gold_signal | 37.1% |
| risk_on_regime_bond_signal | 46.4% |
| risk_on_regime_bond_signal_strong | 22.1% |
| roc_positive | 48.1% |
| roc_turning_dn | 12.7% |
| roc_turning_up | 7.7% |
| rsi_14_bullish | 46.6% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.6% |
| rsi_14_cross_dn_overbought_recent_3d | 5.8% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_14_cross_up_oversold_recent_3d | 2.2% |
| rsi_14_extreme_ob | 0.1% |
| rsi_14_extreme_os | 0.1% |
| rsi_14_overbought | 0.5% |
| rsi_14_oversold | 0.2% |
| rsi_14_rising | 42.4% |
| rsi_21_bullish | 48.1% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_21_cross_dn_overbought_recent_3d | 2.8% |
| rsi_21_cross_up_oversold_recent_3d | 1.1% |
| rsi_21_extreme_ob | 0.0% |
| rsi_21_extreme_os | 0.1% |
| rsi_21_overbought | 0.2% |
| rsi_21_oversold | 0.1% |
| rsi_21_rising | 42.4% |
| rsi_2_bullish | 46.9% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 21.3% |
| rsi_2_cross_dn_overbought_recent_3d | 23.5% |
| rsi_2_cross_up_extreme_os_recent_3d | 13.3% |
| rsi_2_cross_up_oversold_recent_3d | 14.8% |
| rsi_2_extreme_ob | 35.7% |
| rsi_2_extreme_os | 43.9% |
| rsi_2_overbought | 40.9% |
| rsi_2_oversold | 49.3% |
| rsi_2_rising | 42.4% |
| rsi_9_bullish | 47.0% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.7% |
| rsi_9_cross_dn_overbought_recent_3d | 9.1% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.4% |
| rsi_9_cross_up_oversold_recent_3d | 4.3% |
| rsi_9_extreme_ob | 0.3% |
| rsi_9_extreme_os | 0.1% |
| rsi_9_overbought | 4.6% |
| rsi_9_oversold | 4.3% |
| rsi_9_rising | 42.4% |
| s1_break_retest_short | 47.4% |
| sc_13d_filed_within_30d | 2.1% |
| sc_13g_filed_within_30d | 3.1% |
| sector_outperforming_spy | 45.7% |
| sector_underperforming_spy | 54.3% |
| shooting_star | 4.1% |
| sma_20_50_bullish | 51.4% |
| sma_20_50_golden_cross | 0.6% |
| sma_50_200_bullish | 51.8% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 51.7% |
| sma_9_21_golden_cross | 4.5% |
| smc_bos_bearish | 10.8% |
| smc_bos_bullish | 12.0% |
| smc_bos_retest_long | 5.1% |
| smc_bos_retest_short | 4.4% |
| smc_breaker_block_bearish | 17.2% |
| smc_breaker_block_bullish | 23.5% |
| smc_choch_bearish | 4.5% |
| smc_choch_bullish | 4.4% |
| smc_equal_highs_swept | 4.3% |
| smc_equal_lows_swept | 4.6% |
| smc_fvg_bearish_active | 38.7% |
| smc_fvg_bullish_active | 39.1% |
| smc_fvg_retest_long_zone | 7.8% |
| smc_fvg_retest_short_zone | 5.1% |
| smc_in_discount_zone | 64.3% |
| smc_in_premium_zone | 64.7% |
| smc_inverse_fvg_bearish | 94.0% |
| smc_inverse_fvg_bullish | 92.2% |
| smc_liquidity_swept_dn | 0.9% |
| smc_liquidity_swept_up | 1.1% |
| smc_mitigation_block_long | 0.7% |
| smc_mitigation_block_short | 0.8% |
| smc_ob_bearish_active | 36.3% |
| smc_ob_bullish_active | 36.1% |
| smc_ote_long_zone | 7.1% |
| smc_ote_short_zone | 7.3% |
| squeeze_fire_dn | 8.6% |
| squeeze_fire_up | 5.9% |
| squeeze_in | 27.2% |
| squeeze_positive | 47.1% |
| stoch_bearish_cross | 6.6% |
| stoch_broad_overbought | 25.9% |
| stoch_broad_oversold | 22.2% |
| stoch_bullish_cross | 4.7% |
| stoch_overbought | 19.3% |
| stoch_oversold | 15.4% |
| stochrsi_cross_dn | 12.0% |
| stochrsi_cross_up | 9.9% |
| stochrsi_overbought | 41.4% |
| stochrsi_oversold | 45.6% |
| supertrend_bearish | 2.3% |
| supertrend_bullish | 97.7% |
| supertrend_flip_dn | 1.7% |
| supertrend_flip_recent_long_5d | 0.8% |
| supertrend_flip_recent_short_5d | 2.5% |
| supertrend_flip_up | 0.2% |
| support_break_retest | 8.1% |
| tema_above_dema | 50.0% |
| tema_cross_dn | 6.2% |
| tema_cross_up | 5.8% |
| three_black_crows | 11.2% |
| three_white_soldiers | 6.8% |
| triangle_apex_break_retest_long | 7.4% |
| triangle_ascending_detected | 9.4% |
| triangle_descending_detected | 7.8% |
| uo_overbought | 0.1% |
| uo_oversold | 0.2% |
| usd_strengthening | 23.9% |
| usd_weakening | 11.5% |
| vix_band_high | 37.4% |
| vix_band_low | 35.8% |
| vix_band_mid | 26.8% |
| vix_term_backwardation | 5.9% |
| vix_term_contango | 94.1% |
| vol_above_avg | 38.1% |
| vol_below_avg | 61.9% |
| vol_spike_12x | 20.8% |
| vol_spike_15x | 10.4% |
| vol_spike_17x | 7.1% |
| vol_spike_2x | 4.4% |
| vol_spike_2x_on_down_day_recent_3d | 2.3% |
| vol_spike_2x_on_up_day_recent_3d | 2.7% |
| vol_spike_3x | 1.1% |
| vp_above_value_area | 15.7% |
| vp_below_value_area | 9.3% |
| vp_close_above_poc | 53.6% |
| vp_close_below_poc | 46.4% |
| vp_in_value_area | 75.0% |
| week_open_gap_down_15pct | 2.4% |
| week_open_gap_up_15pct | 2.1% |
| weekly_above_ema_10 | 48.8% |
| weekly_above_ema_20 | 50.9% |
| weekly_bias_bear | 38.4% |
| weekly_bias_bull | 38.1% |
| weekly_momentum_pos | 49.5% |
| williams_r_overbought | 40.4% |
| williams_r_oversold | 43.3% |
| williams_r_rising | 43.6% |
| within_pead_window | 38.5% |
| within_post_deletion_window | 4.0% |
| within_post_inclusion_window | 1.5% |
| within_pre_rebalance_window | 1.1% |
| xs_avoid_high_ivol | 71.3% |
| xs_avoid_high_max | 72.4% |
| xs_high_beta_decile | 25.1% |
| xs_low_beta_bottom_quintile | 25.1% |
| xs_low_beta_decile | 17.2% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 17.2% |
| xs_momentum_bottom_decile | 12.8% |
| xs_momentum_bottom_quintile | 23.4% |
| xs_momentum_top_decile | 11.2% |
| xs_momentum_top_quintile | 20.1% |
| xs_quality_bottom_quintile | 22.3% |
| xs_quality_top_quintile | 20.8% |
| xs_quality_top_tercile | 41.5% |
| year_high_break_retest_long | 0.1% |
| year_low_break_retest_short | 0.2% |
| yoy_surprise_high | 52.5% |
| yoy_surprise_negative | 37.8% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.4% |
| committed_growth_holders | 91.4% |
| corp_donations_1y | 9.9% |
| corp_donations_count_1y | 9.9% |
| corp_donations_unique_pacs | 9.9% |
| cot_rut_commercials_pctile_3y | 54.0% |
| cot_rut_mmoney_pctile_3y | 54.0% |
| cup_handle_depth_pct | 17.8% |
| days_since_classification_change | 0.2% |
| days_since_deletion | 7.8% |
| days_since_inclusion | 13.6% |
| days_to_next_holiday | 63.6% |
| days_to_rebalance | 10.6% |
| dpi_30d_avg | 96.5% |
| dpi_recent | 96.5% |
| earnings_announcement_return | 91.0% |
| earnings_eps_yoy_growth | 94.4% |
| flag_bear_pole_move_pct | 0.8% |
| flag_bull_pole_move_pct | 2.1% |
| gov_contracts_4q_sum | 41.1% |
| gov_contracts_last_qtr_amount | 41.1% |
| gov_contracts_qoq_growth | 41.1% |
| head_shoulders_magnitude_pct | 6.4% |
| insider_director_buyers_30d | 6.7% |
| insider_officer_buyers_30d | 6.7% |
| insider_total_shares_bought_30d | 6.7% |
| insider_unique_buyers_30d | 6.7% |
| inverted_cup_handle_height_pct | 14.2% |
| lobbying_amount_1y | 72.5% |
| lobbying_amount_q | 72.5% |
| lobbying_amount_yoy | 72.5% |
| otc_short_ratio_recent | 96.5% |
| otc_volume_recent | 96.5% |
| pair_half_life | 92.7% |
| pair_max_abs_zscore | 92.7% |
| pair_zscore_signed | 92.7% |
| pct_from_avwap_20high | 89.6% |
| pct_from_avwap_20low | 88.4% |
| pct_from_avwap_50low | 98.0% |
| persistent_holders_4q | 91.4% |
| persistent_holders_8q | 91.4% |
| sc_13g_latest_percent_owned | 1.4% |
| search_volume_index_recent | 77.6% |
| search_volume_observations | 77.6% |
| search_volume_zscore_30d | 77.6% |
| sector_etf_return_20d | 2.8% |
| spy_return_20d | 2.8% |
| total_active_holders | 91.4% |
| triangle_breakdown_pct | 7.8% |
| triangle_breakout_pct | 9.4% |
| xs_quality_decile | 62.7% |
| xs_quality_gross_profitability | 62.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.997), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (1.0), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.996), `double_top_peak` (0.997), `entry_stop_long` (0.999), `entry_stop_short` (0.998), `fib_236` (0.995), `fib_382` (0.996), `fib_500` (0.996), `fib_618` (0.997), `fib_786` (0.997), `fib_ext_127` (0.991), `fib_ext_162` (0.988), `flag_bear_breakdown_level` (0.998), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.999), `ichi_kijun` (0.999), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.987), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.978), `monthly_sma_6` (0.992), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.998), `swing_high` (0.993), `swing_low` (0.996), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.996), `vp_value_area_low` (0.995), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.995), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.966), `year_low` (0.969)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
