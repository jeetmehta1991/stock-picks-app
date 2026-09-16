# Table A - hull_rsi

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit a8a3061da at 2026-09-16 16:05:40 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** momentum | **status:** STALLED-CAMPAIGN | **R5 fires:** 1270 | **surviving fires (T1):** 1270 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Table A - parameter inventory (the SS6 canonical shape, pre-R1)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close). The
R1 SPECS entry absorbs and supersedes this pre-R1 inventory - producer
knob rows below are placeholders it must fill.

| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|
| P1 | PRODUCER | adx_trending - emitted by backtest/signals/screener.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P2 | PRODUCER | below_ema_200_break_recent_5d - emitted by backtest/signals/screener.py; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P3 | PRODUCER | hull_bearish - emitted by backtest/signals/screener.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P4 | PRODUCER | hull_bullish - emitted by backtest/signals/screener.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P5 | PRODUCER | price_above_ema_200_break_recent_5d - emitted by backtest/signals/screener.py; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P6 | PRODUCER | price_above_hull - emitted by backtest/signals/screener.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P7 | PRODUCER | price_below_hull - emitted by backtest/signals/screener.py +1; its tunables live inside that producer | leg required True | - (a boolean leg has no offline tighter level) | producer knobs - INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P8 | STRATEGY | adx `> 20` [EXISTING-THRESHOLD] | `> 20` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P9 | STRATEGY-HELPER | _short_borrow_trap_active(s) - a helper gate; its internals are outside the source pattern (lower bound) | required | - | inspect at R1 | INVENTORY-PENDING-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | `> 20` | 100.0% | 21.878 -> 1016 (80%); 24.15 -> 764 (60%); 26.67 -> 509 (40%); 30.174 -> 254 (20%) | looser (lower the threshold): RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx_di_minus | backtest/signals/technical.py | 100.0% | 19.148, 24.706, 29.972, 35.826 | 19.148: 1016 (80%); 24.706: 762 (60%); 29.972: 508 (40%); 35.826: 254 (20%) | 19.148: 254 (20%); 24.706: 508 (40%); 29.972: 762 (60%); 35.826: 1016 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.488, 17.676, 23.142, 29.636 | 13.488: 1016 (80%); 17.676: 762 (60%); 23.142: 508 (40%); 29.636: 254 (20%) | 13.488: 254 (20%); 17.676: 508 (40%); 23.142: 762 (60%); 29.636: 1016 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -7.5872, -2.8446, -0.0813, 3.3069 | -7.5872: 1016 (80%); -2.8446: 762 (60%); -0.0813: 508 (40%); 3.3069: 254 (20%) | -7.5872: 254 (20%); -2.8446: 508 (40%); -0.0813: 762 (60%); 3.3069: 1016 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2824, 2.2969, 3.8717, 6.6397 | 1.2824: 1016 (80%); 2.2969: 762 (60%); 3.8717: 508 (40%); 6.6397: 254 (20%) | 1.2824: 254 (20%); 2.2969: 508 (40%); 3.8717: 762 (60%); 6.6397: 1016 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2824, 2.2969, 3.8717, 6.6397 | 1.2824: 1016 (80%); 2.2969: 762 (60%); 3.8717: 508 (40%); 6.6397: 254 (20%) | 1.2824: 254 (20%); 2.2969: 508 (40%); 3.8717: 762 (60%); 6.6397: 1016 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.1758, 2.6434, 3.1078, 3.8594 | 2.1758: 1016 (80%); 2.6434: 762 (60%); 3.1078: 508 (40%); 3.8594: 254 (20%) | 2.1758: 254 (20%); 2.6434: 508 (40%); 3.1078: 762 (60%); 3.8594: 1016 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0729, 0.1051, 0.1425, 0.1983 | 0.0729: 1016 (80%); 0.1051: 762 (60%); 0.1425: 508 (40%); 0.1983: 254 (20%) | 0.0729: 255 (20%); 0.1051: 508 (40%); 0.1425: 762 (60%); 0.1983: 1016 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.0459, 0.1468, 0.3152, 0.8757 | 0.0459: 1016 (80%); 0.1468: 762 (60%); 0.3152: 509 (40%); 0.8757: 254 (20%) | 0.0459: 254 (20%); 0.1468: 508 (40%); 0.3152: 763 (60%); 0.8757: 1016 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0744, 0.1014, 0.1241, 0.1565 | 0.0744: 1016 (80%); 0.1014: 763 (60%); 0.1241: 510 (40%); 0.1565: 254 (20%) | 0.0744: 255 (20%); 0.1014: 509 (40%); 0.1241: 762 (60%); 0.1565: 1016 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.1935, -0.0207, 0.4434, 1.0241 | -0.1935: 1016 (80%); -0.0207: 762 (60%); 0.4434: 508 (40%); 1.0241: 254 (20%) | -0.1935: 254 (20%); -0.0207: 508 (40%); 0.4434: 762 (60%); 1.0241: 1016 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0992, 0.1352, 0.1655, 0.2087 | 0.0992: 1016 (80%); 0.1352: 762 (60%); 0.1655: 509 (40%); 0.2087: 254 (20%) | 0.0992: 255 (20%); 0.1352: 509 (40%); 0.1655: 763 (60%); 0.2087: 1016 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | -0.0201, 0.1094, 0.4575, 0.8931 | -0.0201: 1016 (80%); 0.1094: 762 (60%); 0.4575: 508 (40%); 0.8931: 254 (20%) | -0.0201: 254 (20%); 0.1094: 508 (40%); 0.4575: 762 (60%); 0.8931: 1016 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0478, -0.022, -0.0006, 0.0296 | -0.0478: 1021 (80%); -0.022: 762 (60%); -0.0006: 511 (40%); 0.0296: 262 (21%) | -0.0478: 256 (20%); -0.022: 508 (40%); -0.0006: 765 (60%); 0.0296: 1016 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1373, 0.1647, 0.2006, 0.26 | 0.1373: 1016 (80%); 0.1647: 770 (61%); 0.2006: 508 (40%); 0.26: 254 (20%) | 0.1373: 254 (20%); 0.1647: 500 (39%); 0.2006: 762 (60%); 0.26: 1016 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1270 (100%) | 0: 1217 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1346, -0.038, 0.0344, 0.1147 | -0.1346: 1016 (80%); -0.038: 762 (60%); 0.0344: 509 (40%); 0.1147: 255 (20%) | -0.1346: 254 (20%); -0.038: 508 (40%); 0.0344: 763 (60%); 0.1147: 1016 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1270 (100%); 1: 479 (38%) | 0: 791 (62%); 1: 1073 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.242, -0.2013, -0.1536, -0.1141 | -0.242: 1017 (80%); -0.2013: 762 (60%); -0.1536: 508 (40%); -0.1141: 269 (21%) | -0.242: 259 (20%); -0.2013: 508 (40%); -0.1536: 762 (60%); -0.1141: 1053 (83%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.6026, 0.6987, 0.7692 | 0.3013: 1019 (80%); 0.6026: 765 (60%); 0.6987: 512 (40%); 0.7692: 303 (24%) | 0.3013: 258 (20%); 0.6026: 521 (41%); 0.6987: 765 (60%); 0.7692: 1029 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.3974, 0.6218, 0.8718 | 0.2628: 1018 (80%); 0.3974: 777 (61%); 0.6218: 510 (40%); 0.8718: 261 (21%) | 0.2628: 278 (22%); 0.3974: 512 (40%); 0.6218: 767 (60%); 0.8718: 1017 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0908, -0.0047, 0.0722, 0.1902 | -0.0908: 1021 (80%); -0.0047: 763 (60%); 0.0722: 511 (40%); 0.1902: 259 (20%) | -0.0908: 255 (20%); -0.0047: 515 (41%); 0.0722: 764 (60%); 0.1902: 1017 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2821, 0.4679, 0.5923, 0.7628 | 0.2821: 1021 (80%); 0.4679: 766 (60%); 0.5923: 508 (40%); 0.7628: 259 (20%) | 0.2821: 257 (20%); 0.4679: 527 (41%); 0.5923: 762 (60%); 0.7628: 1018 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.3077, 0.4551, 0.6667 | 0.1282: 1022 (80%); 0.3077: 766 (60%); 0.4551: 576 (45%); 0.6667: 255 (20%) | 0.1282: 262 (21%); 0.3077: 509 (40%); 0.4551: 772 (61%); 0.6667: 1029 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5101, -0.352, -0.169, 0.0839 | -0.5101: 1018 (80%); -0.352: 784 (62%); -0.169: 521 (41%); 0.0839: 256 (20%) | -0.5101: 256 (20%); -0.352: 509 (40%); -0.169: 769 (61%); 0.0839: 1031 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3205, 0.5192, 0.7244, 0.9167 | 0.3205: 1018 (80%); 0.5192: 770 (61%); 0.7244: 514 (40%); 0.9167: 293 (23%) | 0.3205: 258 (20%); 0.5192: 525 (41%); 0.7244: 764 (60%); 0.9167: 1032 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.3718, 0.5897, 0.8526 | 0.1538: 1024 (81%); 0.3718: 763 (60%); 0.5897: 519 (41%); 0.8526: 274 (22%) | 0.1538: 265 (21%); 0.3718: 512 (40%); 0.5897: 769 (61%); 0.8526: 1048 (83%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0649, -0.0564, -0.0356, 0 | -0.0649: 1017 (80%); -0.0564: 767 (60%); -0.0356: 509 (40%); 0: 393 (31%) | -0.0649: 256 (20%); -0.0564: 510 (40%); -0.0356: 790 (62%); 0: 1243 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4423, 0.7051, 0.8846, 1 | 0.4423: 1025 (81%); 0.7051: 769 (61%); 0.8846: 536 (42%); 1: 322 (25%) | 0.4423: 263 (21%); 0.7051: 519 (41%); 0.8846: 779 (61%); 1: 1270 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.2436, 0.5449, 0.8462 | 0.1346: 1020 (80%); 0.2436: 764 (60%); 0.5449: 511 (40%); 0.8462: 258 (20%) | 0.1346: 255 (20%); 0.2436: 510 (40%); 0.5449: 770 (61%); 0.8462: 1017 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0011, 0.0375, 0.1026, 0.2489 | -0.0011: 1018 (80%); 0.0375: 762 (60%); 0.1026: 508 (40%); 0.2489: 275 (22%) | -0.0011: 255 (20%); 0.0375: 508 (40%); 0.1026: 762 (60%); 0.2489: 1047 (82%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5155, 0.7826, 0.9368, 0.9744 | 0.5155: 1023 (81%); 0.7826: 762 (60%); 0.9368: 508 (40%); 0.9744: 300 (24%) | 0.5155: 255 (20%); 0.7826: 508 (40%); 0.9368: 762 (60%); 0.9744: 1062 (84%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0897, 0.2248, 0.5109, 0.7692 | 0.0897: 1031 (81%); 0.2248: 762 (60%); 0.5109: 513 (40%); 0.7692: 267 (21%) | 0.0897: 258 (20%); 0.2248: 508 (40%); 0.5109: 765 (60%); 0.7692: 1036 (82%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0095, 0.1093, 0.1876 | -0.0812: 1094 (86%); -0.0095: 769 (61%); 0.1093: 510 (40%); 0.1876: 285 (22%) | -0.0812: 301 (24%); -0.0095: 512 (40%); 0.1093: 764 (60%); 0.1876: 1018 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1912, -0.0278, 0.0387, 0.1 | -0.1912: 1016 (80%); -0.0278: 762 (60%); 0.0387: 509 (40%); 0.1: 255 (20%) | -0.1912: 254 (20%); -0.0278: 508 (40%); 0.0387: 765 (60%); 0.1: 1019 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2821, 0.5256, 0.7436, 0.891 | 0.2821: 1017 (80%); 0.5256: 774 (61%); 0.7436: 520 (41%); 0.891: 274 (22%) | 0.2821: 261 (21%); 0.5256: 524 (41%); 0.7436: 767 (60%); 0.891: 1018 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.391, 0.6026, 0.8269 | 0.1474: 1020 (80%); 0.391: 763 (60%); 0.6026: 511 (40%); 0.8269: 264 (21%) | 0.1474: 260 (20%); 0.391: 513 (40%); 0.6026: 770 (61%); 0.8269: 1044 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0642, 0.1625, 0.31, 0.7219 | 0.0642: 1019 (80%); 0.1625: 763 (60%); 0.31: 511 (40%); 0.7219: 254 (20%) | 0.0642: 255 (20%); 0.1625: 509 (40%); 0.31: 764 (60%); 0.7219: 1016 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.7% | 21, 60, 87.2, 140 | 21: 1003 (79%); 60: 754 (59%); 87.2: 501 (39%); 140: 252 (20%) | 21: 262 (21%); 60: 506 (40%); 87.2: 752 (59%); 140: 1005 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.7734, 2.2798, 2.8356, 3.6212 | 1.7734: 1012 (80%); 2.2798: 759 (60%); 2.8356: 506 (40%); 3.6212: 253 (20%) | 1.7734: 253 (20%); 2.2798: 506 (40%); 2.8356: 759 (60%); 3.6212: 1012 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 19, 28, 36 | 8: 1054 (83%); 19: 779 (61%); 28: 521 (41%); 36: 275 (22%) | 8: 258 (20%); 19: 526 (41%); 28: 802 (63%); 36: 1022 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 1072 (84%); 2: 790 (62%); 3: 541 (43%) | 1: 480 (38%); 2: 729 (57%); 3: 1020 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0148, -0.003, 0.0117, 0.0238 | -0.0148: 1020 (80%); -0.003: 762 (60%); 0.0117: 513 (40%); 0.0238: 258 (20%) | -0.0148: 256 (20%); -0.003: 511 (40%); 0.0117: 762 (60%); 0.0238: 1016 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6035, 25.8538, 26.6142, 27.3171 | 24.6035: 1017 (80%); 25.8538: 762 (60%); 26.6142: 508 (40%); 27.3171: 266 (21%) | 24.6035: 258 (20%); 25.8538: 508 (40%); 26.6142: 762 (60%); 27.3171: 1036 (82%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.7564, -0.193, 0.1732, 0.8056 | -0.7564: 1016 (80%); -0.193: 763 (60%); 0.1732: 508 (40%); 0.8056: 254 (20%) | -0.7564: 254 (20%); -0.193: 510 (40%); 0.1732: 762 (60%); 0.8056: 1016 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.8056, -0.1732, 0.193, 0.7564 | -0.8056: 1016 (80%); -0.1732: 762 (60%); 0.193: 510 (40%); 0.7564: 254 (20%) | -0.8056: 254 (20%); -0.1732: 508 (40%); 0.193: 763 (60%); 0.7564: 1016 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0407, -0.0036, 0.0266, 0.0659 | -0.0407: 1017 (80%); -0.0036: 762 (60%); 0.0266: 510 (40%); 0.0659: 255 (20%) | -0.0407: 256 (20%); -0.0036: 508 (40%); 0.0266: 764 (60%); 0.0659: 1020 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.036, 8.5012, 8.8038, 9.1005 | 8.036: 1016 (80%); 8.5012: 764 (60%); 8.8038: 508 (40%); 9.1005: 255 (20%) | 8.036: 254 (20%); 8.5012: 506 (40%); 8.8038: 762 (60%); 9.1005: 1015 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1259 (99%); 1: 433 (34%) | 0: 826 (65%); 1: 1118 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0 | 0: 1041 (82%) | 0: 1021 (80%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1259 (99%); 1: 387 (30%) | 0: 872 (69%); 1: 1115 (88%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 6, 120, 270.4 | 2: 1090 (86%); 6: 767 (60%); 120: 510 (40%); 270.4: 254 (20%) | 2: 266 (21%); 6: 563 (44%); 120: 763 (60%); 270.4: 1016 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 5, 85, 143 | 0: 1270 (100%); 5: 765 (60%); 85: 514 (40%); 143: 262 (21%) | 0: 255 (20%); 5: 530 (42%); 85: 763 (60%); 143: 1017 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.3172, -0.4894, -0.0418, 0.6789 | -1.3172: 1016 (80%); -0.4894: 762 (60%); -0.0418: 508 (40%); 0.6789: 254 (20%) | -1.3172: 254 (20%); -0.4894: 508 (40%); -0.0418: 762 (60%); 0.6789: 1016 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.6968, -1.051, -0.0358, 1.0887 | -2.6968: 1016 (80%); -1.051: 762 (60%); -0.0358: 508 (40%); 1.0887: 254 (20%) | -2.6968: 254 (20%); -1.051: 508 (40%); -0.0358: 762 (60%); 1.0887: 1016 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.3225, -0.8042, 0.0671, 1.0671 | -2.3225: 1016 (80%); -0.8042: 762 (60%); 0.0671: 508 (40%); 1.0671: 254 (20%) | -2.3225: 254 (20%); -0.8042: 508 (40%); 0.0671: 762 (60%); 1.0671: 1016 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -1.1812, -0.4584, -0.0807, 0.7085 | -1.1812: 1016 (80%); -0.4584: 762 (60%); -0.0807: 508 (40%); 0.7085: 254 (20%) | -1.1812: 254 (20%); -0.4584: 508 (40%); -0.0807: 762 (60%); 0.7085: 1016 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -3.6042, -1.2594, -0.097, 1.3157 | -3.6042: 1016 (80%); -1.2594: 762 (60%); -0.097: 508 (40%); 1.3157: 254 (20%) | -3.6042: 254 (20%); -1.2594: 508 (40%); -0.097: 762 (60%); 1.3157: 1016 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.782, -1.0699, -0.0294, 1.2743 | -2.782: 1016 (80%); -1.0699: 762 (60%); -0.0294: 509 (40%); 1.2743: 254 (20%) | -2.782: 254 (20%); -1.0699: 508 (40%); -0.0294: 763 (60%); 1.2743: 1016 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 31.06, 40.888, 50.18, 62.838 | 31.06: 1016 (80%); 40.888: 762 (60%); 50.18: 508 (40%); 62.838: 254 (20%) | 31.06: 254 (20%); 40.888: 508 (40%); 50.18: 762 (60%); 62.838: 1016 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.8% | 0.0049, 0.0113, 0.021, 0.0359 | 0.0049: 1015 (80%); 0.0113: 762 (60%); 0.021: 507 (40%); 0.0359: 254 (20%) | 0.0049: 252 (20%); 0.0113: 505 (40%); 0.021: 760 (60%); 0.0359: 1013 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 10 | 0: 1270 (100%); 2: 811 (64%); 4: 564 (44%); 10: 260 (20%) | 0: 272 (21%); 2: 608 (48%); 4: 787 (62%); 10: 1042 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 1270 (100%); 0.1667: 264 (21%) | 0: 839 (66%); 0.1667: 1028 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.4667, 0.6667 | 0: 1270 (100%); 0.25: 765 (60%); 0.4667: 509 (40%); 0.6667: 288 (23%) | 0: 451 (36%); 0.25: 529 (42%); 0.4667: 763 (60%); 0.6667: 1032 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 7 | 0: 1270 (100%); 1: 914 (72%); 3: 553 (44%); 7: 271 (21%) | 0: 356 (28%); 1: 575 (45%); 3: 819 (64%); 7: 1040 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 10 | 0: 1270 (100%); 2: 811 (64%); 4: 564 (44%); 10: 260 (20%) | 0: 272 (21%); 2: 608 (48%); 4: 787 (62%); 10: 1042 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1270 (100%); 1: 897 (71%); 3: 564 (44%); 7: 281 (22%) | 0: 373 (29%); 1: 559 (44%); 3: 789 (62%); 7: 1029 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0329, 0.25, 0.3926, 0.5968 | 0.0329: 1016 (80%); 0.25: 779 (61%); 0.3926: 508 (40%); 0.5968: 254 (20%) | 0.0329: 254 (20%); 0.25: 510 (40%); 0.3926: 762 (60%); 0.5968: 1016 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2222, 0.6402 | 0: 1139 (90%); 0.2222: 509 (40%); 0.6402: 254 (20%) | 0: 661 (52%); 0.2222: 765 (60%); 0.6402: 1016 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3333, 0.6 | 0: 1166 (92%); 0.3333: 533 (42%); 0.6: 258 (20%) | 0: 525 (41%); 0.3333: 782 (62%); 0.6: 1021 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.6 | 0: 1166 (92%); 0.3333: 533 (42%); 0.6: 258 (20%) | 0: 525 (41%); 0.3333: 782 (62%); 0.6: 1021 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1864, 0, 0.1464 | -0.1864: 1016 (80%); 0: 895 (70%); 0.1464: 255 (20%) | -0.1864: 254 (20%); 0: 922 (73%); 0.1464: 1016 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6928, -0.1711, 0.2807, 1.7889 | -0.6928: 1018 (80%); -0.1711: 766 (60%); 0.2807: 508 (40%); 1.7889: 267 (21%) | -0.6928: 257 (20%); -0.1711: 511 (40%); 0.2807: 762 (60%); 1.7889: 1043 (82%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 12 | 2: 1069 (84%); 4: 823 (65%); 7: 531 (42%); 12: 255 (20%) | 2: 324 (26%); 4: 563 (44%); 7: 808 (64%); 12: 1054 (83%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0988, -0.0531, -0.008, 0.064 | -0.0988: 1016 (80%); -0.0531: 762 (60%); -0.008: 508 (40%); 0.064: 254 (20%) | -0.0988: 254 (20%); -0.0531: 508 (40%); -0.008: 762 (60%); 0.064: 1016 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1075, -0.0603, -0.0045, 0.0614 | -0.1075: 1016 (80%); -0.0603: 763 (60%); -0.0045: 508 (40%); 0.0614: 254 (20%) | -0.1075: 254 (20%); -0.0603: 507 (40%); -0.0045: 762 (60%); 0.0614: 1016 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0854, -0.0465, -0.0159, 0.0574 | -0.0854: 1016 (80%); -0.0465: 762 (60%); -0.0159: 508 (40%); 0.0574: 254 (20%) | -0.0854: 254 (20%); -0.0465: 508 (40%); -0.0159: 762 (60%); 0.0574: 1016 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -10.6558, -2.2146, 5.533, 20.3282 | -10.6558: 1016 (80%); -2.2146: 762 (60%); 5.533: 508 (40%); 20.3282: 254 (20%) | -10.6558: 254 (20%); -2.2146: 508 (40%); 5.533: 762 (60%); 20.3282: 1016 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0478, 0.0659, 0.0857, 0.12 | 0.0478: 1016 (80%); 0.0659: 764 (60%); 0.0857: 509 (40%); 0.12: 255 (20%) | 0.0478: 257 (20%); 0.0659: 509 (40%); 0.0857: 763 (60%); 0.12: 1017 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1447, 0.312, 0.5061, 0.7775 | 0.1447: 1017 (80%); 0.312: 762 (60%); 0.5061: 508 (40%); 0.7775: 254 (20%) | 0.1447: 255 (20%); 0.312: 509 (40%); 0.5061: 762 (60%); 0.7775: 1016 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.1501, -1.2173, -0.0462, 1.3873 | -2.1501: 1016 (80%); -1.2173: 762 (60%); -0.0462: 508 (40%); 1.3873: 254 (20%) | -2.1501: 254 (20%); -1.2173: 508 (40%); -0.0462: 762 (60%); 1.3873: 1016 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.1881, -0.6485, -0.0817, 0.7653 | -1.1881: 1016 (80%); -0.6485: 762 (60%); -0.0817: 508 (40%); 0.7653: 254 (20%) | -1.1881: 254 (20%); -0.6485: 508 (40%); -0.0817: 762 (60%); 0.7653: 1016 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.7176, -0.9706, 0.0849, 1.3903 | -1.7176: 1016 (80%); -0.9706: 762 (60%); 0.0849: 508 (40%); 1.3903: 254 (20%) | -1.7176: 254 (20%); -0.9706: 508 (40%); 0.0849: 762 (60%); 1.3903: 1016 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -10.5572, -5.6658, -0.505, 6.557 | -10.5572: 1016 (80%); -5.6658: 762 (60%); -0.505: 508 (40%); 6.557: 255 (20%) | -10.5572: 254 (20%); -5.6658: 508 (40%); -0.505: 762 (60%); 6.557: 1017 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 30.9, 38.358, 48.992, 59.44 | 30.9: 1017 (80%); 38.358: 762 (60%); 48.992: 508 (40%); 59.44: 255 (20%) | 30.9: 255 (20%); 38.358: 508 (40%); 48.992: 762 (60%); 59.44: 1017 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 3.268, 10.398, 38.118, 92.56 | 3.268: 1016 (80%); 10.398: 762 (60%); 38.118: 508 (40%); 92.56: 255 (20%) | 3.268: 254 (20%); 10.398: 508 (40%); 38.118: 762 (60%); 92.56: 1017 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 36.638, 42.512, 49.384, 55.7 | 36.638: 1016 (80%); 42.512: 762 (60%); 49.384: 508 (40%); 55.7: 255 (20%) | 36.638: 254 (20%); 42.512: 508 (40%); 49.384: 762 (60%); 55.7: 1017 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 23.998, 33.038, 47.638, 65.63 | 23.998: 1016 (80%); 33.038: 762 (60%); 47.638: 508 (40%); 65.63: 255 (20%) | 23.998: 254 (20%); 33.038: 508 (40%); 47.638: 762 (60%); 65.63: 1017 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 1267 (100%) | 0: 1270 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0322, 0.0471, 0.0607, 0.0895 | 0.0322: 1016 (80%); 0.0471: 762 (60%); 0.0607: 508 (40%); 0.0895: 254 (20%) | 0.0322: 258 (20%); 0.0471: 510 (40%); 0.0607: 762 (60%); 0.0895: 1016 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0793, -0.0587, -0.0435, -0.0334 | -0.0793: 1016 (80%); -0.0587: 764 (60%); -0.0435: 510 (40%); -0.0334: 256 (20%) | -0.0793: 260 (20%); -0.0587: 510 (40%); -0.0435: 764 (60%); -0.0334: 1017 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1270 (100%); 1: 380 (30%) | 0: 890 (70%); 1: 1038 (82%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 28, 43, 60, 70 | 28: 1024 (81%); 43: 771 (61%); 60: 517 (41%); 70: 263 (21%) | 28: 263 (21%); 43: 509 (40%); 60: 773 (61%); 70: 1015 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.7% | 0.0115, 0.0163, 0.0229, 0.0352 | 0.0115: 1001 (79%); 0.0163: 746 (59%); 0.0229: 503 (40%); 0.0352: 255 (20%) | 0.0115: 253 (20%); 0.0163: 508 (40%); 0.0229: 751 (59%); 0.0352: 999 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.0835, 0.2721, 0.4875, 0.6915 | 0.0835: 1016 (80%); 0.2721: 762 (60%); 0.4875: 508 (40%); 0.6915: 254 (20%) | 0.0835: 255 (20%); 0.2721: 508 (40%); 0.4875: 762 (60%); 0.6915: 1016 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 41.2, 57.2, 72.34, 102.42 | 41.2: 1017 (80%); 57.2: 764 (60%); 72.34: 508 (40%); 102.42: 254 (20%) | 41.2: 258 (20%); 57.2: 509 (40%); 72.34: 762 (60%); 102.42: 1016 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -8.6485, -3.1846, -0.386, 3.8405 | -8.6485: 1016 (80%); -3.1846: 762 (60%); -0.386: 508 (40%); 3.8405: 254 (20%) | -8.6485: 254 (20%); -3.1846: 508 (40%); -0.386: 762 (60%); 3.8405: 1016 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 14.51, 26.924, 51.52, 76.874 | 14.51: 1017 (80%); 26.924: 762 (60%); 51.52: 509 (40%); 76.874: 254 (20%) | 14.51: 255 (20%); 26.924: 508 (40%); 51.52: 763 (60%); 76.874: 1016 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 10.548, 21.926, 47.014, 81.258 | 10.548: 1016 (80%); 21.926: 762 (60%); 47.014: 508 (40%); 81.258: 254 (20%) | 10.548: 254 (20%); 21.926: 508 (40%); 47.014: 762 (60%); 81.258: 1016 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 2.414, 17.504, 51.794, 91.892 | 2.414: 1016 (80%); 17.504: 762 (60%); 51.794: 508 (40%); 91.892: 254 (20%) | 2.414: 254 (20%); 17.504: 508 (40%); 51.794: 762 (60%); 91.892: 1016 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 6.674, 48.842, 100 | 0: 1270 (100%); 6.674: 762 (60%); 48.842: 508 (40%); 100: 276 (22%) | 0: 414 (33%); 6.674: 508 (40%); 48.842: 762 (60%); 100: 1270 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 12, 17 | 4: 1079 (85%); 8: 788 (62%); 12: 548 (43%); 17: 270 (21%) | 4: 278 (22%); 8: 558 (44%); 12: 779 (61%); 17: 1051 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 18 | 5: 1046 (82%); 10: 779 (61%); 14: 553 (44%); 18: 279 (22%) | 5: 270 (21%); 10: 537 (42%); 14: 787 (62%); 18: 1075 (85%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 36.322, 42.672, 49.982, 59.504 | 36.322: 1016 (80%); 42.672: 762 (60%); 49.982: 508 (40%); 59.504: 254 (20%) | 36.322: 254 (20%); 42.672: 508 (40%); 49.982: 762 (60%); 59.504: 1016 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1897, 0.4325, 0.6865, 0.9056 | 0.1897: 1016 (80%); 0.4325: 766 (60%); 0.6865: 510 (40%); 0.9056: 254 (20%) | 0.1897: 254 (20%); 0.4325: 510 (40%); 0.6865: 777 (61%); 0.9056: 1016 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.228, 17.83, 20.902, 25.87 | 15.228: 1016 (80%); 17.83: 764 (60%); 20.902: 508 (40%); 25.87: 255 (20%) | 15.228: 254 (20%); 17.83: 509 (40%); 20.902: 762 (60%); 25.87: 1020 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.228, 17.83, 20.902, 25.87 | 15.228: 1016 (80%); 17.83: 764 (60%); 20.902: 508 (40%); 25.87: 255 (20%) | 15.228: 254 (20%); 17.83: 509 (40%); 20.902: 762 (60%); 25.87: 1020 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8614, 0.895, 0.9331, 0.9744 | 0.8614: 1018 (80%); 0.895: 762 (60%); 0.9331: 510 (40%); 0.9744: 254 (20%) | 0.8614: 255 (20%); 0.895: 508 (40%); 0.9331: 763 (60%); 0.9744: 1016 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.79, 0.96, 1.17, 1.532 | 0.79: 1026 (81%); 0.96: 770 (61%); 1.17: 519 (41%); 1.532: 254 (20%) | 0.79: 258 (20%); 0.96: 521 (41%); 1.17: 763 (60%); 1.532: 1016 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0254, 0.0542, 0.0878, 0.1251 | 0.0254: 1017 (80%); 0.0542: 762 (60%); 0.0878: 508 (40%); 0.1251: 255 (20%) | 0.0254: 255 (20%); 0.0542: 509 (40%); 0.0878: 762 (60%); 0.1251: 1018 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.372, 73.2162, 112.2082, 196.342 | 41.372: 1016 (80%); 73.2162: 762 (60%); 112.2082: 508 (40%); 196.342: 254 (20%) | 41.372: 254 (20%); 73.2162: 508 (40%); 112.2082: 762 (60%); 196.342: 1016 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1270 (100%) | 0: 1145 (90%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1270 (100%) | 0: 1168 (92%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1065, -0.0583, -0.0039, 0.0639 | -0.1065: 1016 (80%); -0.0583: 762 (60%); -0.0039: 509 (40%); 0.0639: 254 (20%) | -0.1065: 256 (20%); -0.0583: 508 (40%); -0.0039: 762 (60%); 0.0639: 1016 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -94.702, -86.612, -57.476, -10.516 | -94.702: 1016 (80%); -86.612: 762 (60%); -57.476: 508 (40%); -10.516: 254 (20%) | -94.702: 254 (20%); -86.612: 508 (40%); -57.476: 762 (60%); -10.516: 1016 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.4% | 0.5274, 0.8181, 1.0274, 1.2956 | 0.5274: 1010 (80%); 0.8181: 758 (60%); 1.0274: 505 (40%); 1.2956: 253 (20%) | 0.5274: 253 (20%); 0.8181: 505 (40%); 1.0274: 758 (60%); 1.2956: 1010 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.4% | 3, 5, 7, 9 | 3: 1041 (82%); 5: 803 (63%); 7: 570 (45%); 9: 306 (24%) | 3: 326 (26%); 5: 584 (46%); 7: 815 (64%); 9: 1107 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.3% | 0.1963, 0.2327, 0.2771, 0.3492 | 0.1963: 1009 (79%); 0.2327: 757 (60%); 0.2771: 505 (40%); 0.3492: 253 (20%) | 0.1963: 253 (20%); 0.2327: 505 (40%); 0.2771: 758 (60%); 0.3492: 1009 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.3% | 3, 5, 7, 9 | 3: 1079 (85%); 5: 862 (68%); 7: 599 (47%); 9: 330 (26%) | 3: 288 (23%); 5: 548 (43%); 7: 794 (63%); 9: 1107 (87%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.4% | 0.022, 0.031, 0.0415, 0.0612 | 0.022: 1013 (80%); 0.031: 758 (60%); 0.0415: 508 (40%); 0.0612: 256 (20%) | 0.022: 254 (20%); 0.031: 507 (40%); 0.0415: 759 (60%); 0.0612: 1011 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.4% | 3, 5, 7, 9 | 3: 1039 (82%); 5: 797 (63%); 7: 571 (45%); 9: 327 (26%) | 3: 331 (26%); 5: 582 (46%); 7: 806 (63%); 9: 1088 (86%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.6% | -0.1285, 0.0026, 0.118, 0.2638 | -0.1285: 1012 (80%); 0.0026: 759 (60%); 0.118: 506 (40%); 0.2638: 253 (20%) | -0.1285: 253 (20%); 0.0026: 506 (40%); 0.118: 759 (60%); 0.2638: 1012 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 1058 (83%); 5: 819 (64%); 7: 582 (46%); 9: 277 (22%) | 3: 322 (25%); 5: 566 (45%); 7: 826 (65%); 9: 1127 (89%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.6% |
| 8k_item_5_02_filed_within_7d | 4.9% |
| above_avwap_20high | 28.9% |
| above_avwap_20low | 51.3% |
| above_avwap_252low | 64.1% |
| above_avwap_50low | 56.6% |
| above_cam_r3 | 28.7% |
| above_cam_r4 | 17.7% |
| above_cpr | 41.9% |
| above_pivot | 40.5% |
| above_prev_high | 25.4% |
| above_prev_high_clearance_atr_05 | 12.5% |
| above_prev_low | 62.8% |
| above_r1 | 21.0% |
| above_r2 | 12.6% |
| above_vwap | 54.2% |
| above_wood_p | 42.5% |
| ad_rising | 42.9% |
| adx_cross_up | 6.5% |
| adx_cross_up_20 | 8.3% |
| adx_di_bear | 62.7% |
| adx_di_bull | 37.3% |
| adx_strong | 2.5% |
| adx_trending | 53.1% |
| ao_cross_dn | 4.0% |
| ao_cross_up | 3.1% |
| ao_positive | 39.0% |
| ao_twin_peaks_bull | 1.9% |
| at_key_fib | 14.6% |
| at_key_fib_wide | 35.0% |
| avwap_20high_loss_recent_3d | 15.1% |
| avwap_20high_reclaim_recent_3d | 13.4% |
| avwap_20low_loss_recent_3d | 25.9% |
| avwap_20low_reclaim_recent_3d | 11.1% |
| avwap_252low_loss_recent_3d | 23.7% |
| avwap_252low_reclaim_recent_3d | 14.6% |
| avwap_50low_loss_recent_3d | 20.3% |
| avwap_50low_reclaim_recent_3d | 8.0% |
| bb_10_20_above_mid | 36.5% |
| bb_10_20_expanding | 77.5% |
| bb_10_20_pctb_gt_75 | 32.4% |
| bb_10_20_pctb_gt_8 | 28.7% |
| bb_10_20_pctb_gt_85 | 23.7% |
| bb_10_20_pctb_gt_9 | 18.1% |
| bb_10_20_pctb_gt_95 | 12.2% |
| bb_10_20_pctb_lt_05 | 20.4% |
| bb_10_20_pctb_lt_1 | 29.8% |
| bb_10_20_pctb_lt_15 | 41.2% |
| bb_10_20_pctb_lt_2 | 50.6% |
| bb_10_20_pctb_lt_25 | 56.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 18.1% |
| bb_10_20_reclaim_from_upper_recent_3d | 9.3% |
| bb_10_20_squeeze | 24.3% |
| bb_10_20_touch_lower | 20.5% |
| bb_10_20_touch_upper | 12.1% |
| bb_20_15_above_mid | 36.8% |
| bb_20_15_expanding | 67.4% |
| bb_20_15_pctb_gt_75 | 26.7% |
| bb_20_15_pctb_gt_8 | 25.6% |
| bb_20_15_pctb_gt_85 | 24.7% |
| bb_20_15_pctb_gt_9 | 24.1% |
| bb_20_15_pctb_gt_95 | 22.6% |
| bb_20_15_pctb_lt_05 | 45.3% |
| bb_20_15_pctb_lt_1 | 47.8% |
| bb_20_15_pctb_lt_15 | 49.1% |
| bb_20_15_pctb_lt_2 | 50.4% |
| bb_20_15_pctb_lt_25 | 52.0% |
| bb_20_15_reclaim_from_lower_recent_3d | 4.3% |
| bb_20_15_reclaim_from_upper_recent_3d | 3.3% |
| bb_20_15_squeeze | 23.5% |
| bb_20_15_touch_lower | 46.2% |
| bb_20_15_touch_upper | 22.9% |
| bb_20_20_above_mid | 36.8% |
| bb_20_20_expanding | 67.4% |
| bb_20_20_pctb_gt_75 | 25.1% |
| bb_20_20_pctb_gt_8 | 24.1% |
| bb_20_20_pctb_gt_85 | 22.0% |
| bb_20_20_pctb_gt_9 | 19.6% |
| bb_20_20_pctb_gt_95 | 15.7% |
| bb_20_20_pctb_lt_05 | 31.3% |
| bb_20_20_pctb_lt_1 | 38.7% |
| bb_20_20_pctb_lt_15 | 44.8% |
| bb_20_20_pctb_lt_2 | 47.8% |
| bb_20_20_pctb_lt_25 | 49.7% |
| bb_20_20_reclaim_from_lower_recent_3d | 9.8% |
| bb_20_20_reclaim_from_upper_recent_3d | 4.3% |
| bb_20_20_squeeze | 11.5% |
| bb_20_20_touch_lower | 29.8% |
| bb_20_20_touch_upper | 15.2% |
| bearish_engulfing | 3.9% |
| bearish_pin_bar | 4.5% |
| below_avwap_20high | 71.1% |
| below_avwap_20low | 48.6% |
| below_avwap_252low | 35.9% |
| below_avwap_50low | 43.4% |
| below_cam_s3 | 43.6% |
| below_cam_s4 | 27.4% |
| below_cpr | 59.5% |
| below_ema_20 | 63.4% |
| below_ema_200 | 63.5% |
| below_ema_200_break_recent_5d | 63.5% |
| below_ema_20_break_recent_5d | 28.1% |
| below_ema_21 | 63.4% |
| below_ema_21_break_recent_5d | 27.8% |
| below_ema_50 | 61.8% |
| below_ema_50_break_recent_5d | 22.8% |
| below_ema_9 | 63.3% |
| below_ema_9_break_recent_5d | 35.7% |
| below_prev_high | 74.5% |
| below_prev_low | 36.8% |
| below_prev_low_clearance_atr_05 | 18.7% |
| below_s1 | 31.9% |
| below_s2 | 17.0% |
| below_sma_20 | 63.2% |
| below_sma_200 | 58.6% |
| below_sma_21 | 63.0% |
| below_sma_50 | 61.3% |
| below_sma_9 | 63.2% |
| below_vwap | 45.8% |
| blowoff_recent_3d | 0.2% |
| break_52w_high | 0.2% |
| break_52w_high_confirmed_today | 0.1% |
| break_52w_low | 0.2% |
| bullish_engulfing | 2.0% |
| bullish_pin_bar | 4.7% |
| capitulation_recent_3d | 0.2% |
| ceo_buy | 0.5% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 43.4% |
| chandelier_long_flip_dn | 7.5% |
| chandelier_short_bearish | 65.4% |
| chandelier_short_flip_up | 5.3% |
| close_above_open | 36.5% |
| close_below_open | 63.5% |
| close_in_bottom_40pct_of_range | 49.5% |
| close_in_top_40pct_of_range | 33.0% |
| cluster_buy | 0.2% |
| cmf_cross_dn | 8.1% |
| cmf_cross_up | 4.7% |
| cmf_negative | 50.4% |
| cmf_positive | 49.6% |
| concentrated_sell | 5.3% |
| cpr_narrow | 86.9% |
| cpr_narrow_tight | 22.3% |
| cup_handle_detected | 17.5% |
| cup_handle_neckline_break_retest_long | 3.1% |
| dc10_breakout_dn | 31.1% |
| dc10_breakout_dn_1pct | 40.8% |
| dc10_breakout_up | 19.0% |
| dc10_breakout_up_1pct | 25.4% |
| dc10_new_high | 21.8% |
| dc10_strong_breakout_dn | 12.8% |
| dc10_strong_breakout_up | 8.4% |
| dc20_breakout_dn | 24.6% |
| dc20_breakout_up | 13.3% |
| dc20_new_high | 15.5% |
| dc20_resistance_break_retest_strong | 11.5% |
| dc20_support_break_retest_strong | 24.5% |
| defensive_leadership | 58.2% |
| director_only_buy | 2.6% |
| doji | 4.8% |
| double_bottom_detected | 11.0% |
| double_top_detected | 15.3% |
| dpi_elevated | 53.9% |
| drying_volume_on_down_turn | 25.0% |
| drying_volume_on_up_turn | 20.9% |
| ema_20_50_bearish | 57.6% |
| ema_20_50_bullish | 42.4% |
| ema_20_50_death_cross | 3.8% |
| ema_20_50_golden_cross | 1.6% |
| ema_50_200_bearish | 40.4% |
| ema_50_200_bullish | 59.6% |
| ema_50_200_death_cross | 0.2% |
| ema_50_200_golden_cross | 0.1% |
| ema_9_21_bearish | 61.0% |
| ema_9_21_bullish | 39.0% |
| ema_9_21_death_cross | 4.3% |
| ema_9_21_golden_cross | 3.7% |
| evening_star | 6.0% |
| flag_bear_break_retest_short | 0.6% |
| flag_bear_broke | 0.9% |
| flag_bear_detected | 0.1% |
| flag_bull_break_retest_long | 0.3% |
| flag_bull_broke | 0.6% |
| flag_bull_detected | 0.6% |
| force_index_cross_dn | 6.0% |
| force_index_cross_up | 3.9% |
| force_index_positive | 36.9% |
| gap_dn_1_5pct | 10.2% |
| gap_dn_2pct | 7.1% |
| gap_up_1_5pct | 10.7% |
| gap_up_2pct | 8.1% |
| hammer | 3.9% |
| head_shoulders_bottom_detected | 3.4% |
| head_shoulders_top_detected | 3.9% |
| house_cluster_buy | 3.5% |
| house_cluster_sell | 5.6% |
| htf_aligned_bear | 31.3% |
| htf_aligned_bull | 14.4% |
| htf_disagreement | 4.6% |
| hull_bearish | 63.5% |
| hull_bullish | 36.5% |
| hull_flip_dn | 8.1% |
| hull_flip_up | 5.5% |
| ichi_above_cloud | 30.6% |
| ichi_above_cloud_break_recent_5d | 10.2% |
| ichi_below_cloud | 53.9% |
| ichi_below_cloud_break_recent_5d | 22.7% |
| ichi_cloud_thick | 85.7% |
| ichi_tk_bearish | 54.3% |
| ichi_tk_bullish | 35.8% |
| ichi_tk_cross_dn | 2.3% |
| ichi_tk_cross_up | 2.6% |
| ichi_weekly_above_cloud | 35.9% |
| ichi_weekly_below_cloud | 30.7% |
| ichi_weekly_in_cloud | 33.4% |
| in_reversal_window | 2.3% |
| inside_bar | 10.5% |
| inside_cpr | 1.2% |
| inside_kc | 55.4% |
| insider_cluster_active | 26.2% |
| institutional_buy | 88.1% |
| institutional_negative | 5.4% |
| institutional_persistence_growing | 46.2% |
| institutional_persistence_strong | 62.3% |
| institutional_strong_buy | 78.5% |
| inverted_cup_handle_detected | 11.6% |
| is_friday | 19.7% |
| is_halloween_period | 55.4% |
| is_halloween_period_first_day | 0.4% |
| is_january | 8.7% |
| is_january_extended | 10.2% |
| is_monday | 15.6% |
| is_pre_holiday | 3.8% |
| is_summer_period | 44.6% |
| is_totm_window | 32.7% |
| is_totm_window_first_day | 9.4% |
| is_week_open | 18.3% |
| kc_touch_lower | 35.2% |
| kc_touch_upper | 15.0% |
| large_dollar_buy | 0.7% |
| macd_12_26_9_bearish | 61.9% |
| macd_12_26_9_bullish | 38.1% |
| macd_12_26_9_crossover_dn | 4.3% |
| macd_12_26_9_crossover_up | 2.7% |
| macd_8_21_5_bearish | 63.3% |
| macd_8_21_5_bullish | 36.7% |
| macd_8_21_5_crossover_dn | 4.7% |
| macd_8_21_5_crossover_up | 2.2% |
| marubozu_bear | 1.3% |
| marubozu_bull | 0.3% |
| mfi_broad_overbought | 11.3% |
| mfi_broad_oversold | 18.3% |
| mfi_overbought | 2.6% |
| mfi_oversold | 5.2% |
| monthly_above_sma_12 | 44.0% |
| monthly_above_sma_6 | 37.0% |
| monthly_bias_bear | 37.1% |
| monthly_bias_bull | 18.2% |
| monthly_momentum_pos | 47.9% |
| morning_star | 2.8% |
| near_52w_high | 0.2% |
| near_52w_high_95pct | 0.6% |
| near_52w_high_retest_long | 0.1% |
| near_52w_low | 0.6% |
| near_52w_low_105pct | 1.8% |
| near_avwap_20high_atr_05x | 14.7% |
| near_avwap_20high_atr_10x | 28.9% |
| near_avwap_20high_atr_15x | 47.3% |
| near_avwap_20high_atr_20x | 64.8% |
| near_avwap_20low_atr_05x | 30.5% |
| near_avwap_20low_atr_10x | 46.9% |
| near_avwap_20low_atr_15x | 60.2% |
| near_avwap_20low_atr_20x | 70.4% |
| near_avwap_252low_atr_05x | 21.3% |
| near_avwap_252low_atr_10x | 39.9% |
| near_avwap_252low_atr_15x | 56.0% |
| near_avwap_252low_atr_20x | 67.6% |
| near_avwap_50low_atr_05x | 19.9% |
| near_avwap_50low_atr_10x | 34.8% |
| near_avwap_50low_atr_15x | 48.9% |
| near_avwap_50low_atr_20x | 61.8% |
| near_cam_r3 | 9.8% |
| near_cam_s3 | 12.7% |
| near_cam_s4 | 9.6% |
| near_fib_236 | 2.4% |
| near_fib_382 | 5.4% |
| near_fib_500 | 4.4% |
| near_fib_618 | 4.8% |
| near_fib_786 | 4.3% |
| near_pivot | 7.7% |
| near_prev_close | 10.0% |
| near_prev_high | 7.3% |
| near_prev_low | 10.2% |
| near_r1 | 8.3% |
| near_r1_wide | 35.9% |
| near_r2 | 3.8% |
| near_r2_wide | 21.7% |
| near_s1 | 12.4% |
| near_s1_wide | 43.2% |
| near_s2 | 4.8% |
| near_s2_wide | 29.1% |
| near_s3 | 2.1% |
| near_wood_r1 | 6.1% |
| near_wood_s1 | 7.6% |
| news_uses_polygon_score | 26.5% |
| obv_bearish | 60.3% |
| obv_bullish | 39.7% |
| obv_diverge_bull | 4.9% |
| obv_falling | 60.6% |
| obv_rising | 39.4% |
| outside_bar | 6.8% |
| pead_negative_surprise | 14.1% |
| pead_positive_surprise | 23.7% |
| pin_bar | 9.2% |
| po3_accumulation_active | 22.9% |
| po3_bearish | 9.8% |
| po3_bullish | 4.0% |
| po3_manipulation_sweep_down | 12.7% |
| po3_manipulation_sweep_up | 6.6% |
| po3_mmbm_setup | 0.1% |
| po3_mmsm_setup | 0.2% |
| po3_sweep_above_prior_high | 45.0% |
| po3_sweep_below_prior_low | 54.6% |
| ppo_bullish | 37.1% |
| ppo_crossover_dn | 4.2% |
| ppo_crossover_up | 2.4% |
| pre_fomc_d0 | 3.0% |
| pre_fomc_d1 | 2.5% |
| pre_fomc_window | 5.5% |
| price_above_dema | 36.9% |
| price_above_ema_20 | 36.6% |
| price_above_ema_200 | 36.5% |
| price_above_ema_200_break_recent_5d | 36.5% |
| price_above_ema_20_break_recent_5d | 20.0% |
| price_above_ema_21 | 36.6% |
| price_above_ema_21_break_recent_5d | 19.8% |
| price_above_ema_50 | 38.2% |
| price_above_ema_50_break_recent_5d | 18.5% |
| price_above_ema_9 | 36.7% |
| price_above_ema_9_break_recent_5d | 22.9% |
| price_above_hull | 36.5% |
| price_above_sma_200 | 41.4% |
| price_above_sma_21 | 37.0% |
| price_above_sma_50 | 38.7% |
| price_above_tema | 37.9% |
| price_below_dema | 63.1% |
| price_below_hull | 63.5% |
| price_below_tema | 62.1% |
| psar_bullish | 38.1% |
| psar_flip_dn | 5.7% |
| psar_flip_up | 3.5% |
| r1_break_retest_long | 36.7% |
| recent_blowoff_at_r3 | 0.2% |
| recent_capitulation_at_s3 | 0.2% |
| resistance_break_retest | 15.5% |
| risk_off_regime_bond_signal | 25.2% |
| risk_off_regime_bond_signal_strong | 12.4% |
| risk_off_regime_gold_signal | 43.3% |
| risk_on_regime_bond_signal | 41.8% |
| risk_on_regime_bond_signal_strong | 18.0% |
| roc_positive | 38.3% |
| roc_turning_dn | 7.0% |
| roc_turning_up | 5.4% |
| rsi_14_bullish | 37.6% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_14_cross_dn_overbought_recent_3d | 2.6% |
| rsi_14_cross_up_oversold_recent_3d | 3.5% |
| rsi_14_extreme_ob | 0.4% |
| rsi_14_extreme_os | 1.1% |
| rsi_14_overbought | 5.4% |
| rsi_14_oversold | 17.2% |
| rsi_14_rising | 39.8% |
| rsi_21_bullish | 38.3% |
| rsi_21_cross_dn_overbought_recent_3d | 0.5% |
| rsi_21_cross_up_oversold_recent_3d | 0.3% |
| rsi_21_extreme_os | 0.2% |
| rsi_21_overbought | 1.0% |
| rsi_21_oversold | 3.0% |
| rsi_21_rising | 39.7% |
| rsi_2_bullish | 37.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 14.4% |
| rsi_2_cross_dn_overbought_recent_3d | 17.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 13.5% |
| rsi_2_cross_up_oversold_recent_3d | 13.7% |
| rsi_2_extreme_ob | 30.9% |
| rsi_2_extreme_os | 51.9% |
| rsi_2_overbought | 34.0% |
| rsi_2_oversold | 56.6% |
| rsi_2_rising | 39.7% |
| rsi_9_bullish | 36.5% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.4% |
| rsi_9_cross_dn_overbought_recent_3d | 5.5% |
| rsi_9_cross_up_extreme_os_recent_3d | 2.0% |
| rsi_9_cross_up_oversold_recent_3d | 5.9% |
| rsi_9_extreme_ob | 3.9% |
| rsi_9_extreme_os | 8.9% |
| rsi_9_overbought | 15.2% |
| rsi_9_oversold | 33.5% |
| rsi_9_rising | 39.7% |
| s1_break_retest_short | 60.7% |
| sc_13d_filed_within_30d | 2.8% |
| sc_13g_filed_within_30d | 3.1% |
| sector_outperforming_spy | 31.0% |
| sector_underperforming_spy | 69.0% |
| shooting_star | 4.2% |
| sma_20_50_bullish | 44.6% |
| sma_20_50_golden_cross | 1.0% |
| sma_50_200_bullish | 60.8% |
| sma_50_200_golden_cross | 0.2% |
| sma_9_21_bullish | 40.0% |
| sma_9_21_golden_cross | 2.6% |
| smc_bos_bearish | 7.0% |
| smc_bos_bullish | 9.8% |
| smc_bos_retest_long | 6.2% |
| smc_bos_retest_short | 4.9% |
| smc_breaker_block_bearish | 15.6% |
| smc_breaker_block_bullish | 21.3% |
| smc_choch_bearish | 9.6% |
| smc_choch_bullish | 3.1% |
| smc_equal_highs_swept | 2.3% |
| smc_equal_lows_swept | 3.4% |
| smc_fvg_bearish_active | 53.6% |
| smc_fvg_bullish_active | 35.1% |
| smc_fvg_retest_long_zone | 6.0% |
| smc_fvg_retest_short_zone | 6.5% |
| smc_in_discount_zone | 70.2% |
| smc_in_premium_zone | 48.7% |
| smc_inverse_fvg_bearish | 89.6% |
| smc_inverse_fvg_bullish | 71.7% |
| smc_liquidity_swept_dn | 2.0% |
| smc_liquidity_swept_up | 2.0% |
| smc_mitigation_block_long | 3.0% |
| smc_mitigation_block_short | 1.8% |
| smc_ob_bearish_active | 35.0% |
| smc_ob_bullish_active | 27.0% |
| smc_ote_long_zone | 13.0% |
| smc_ote_short_zone | 10.6% |
| squeeze_fire_dn | 4.8% |
| squeeze_fire_up | 2.8% |
| squeeze_in | 12.9% |
| squeeze_positive | 37.6% |
| stoch_bearish_cross | 9.8% |
| stoch_broad_overbought | 23.6% |
| stoch_broad_oversold | 42.9% |
| stoch_bullish_cross | 8.7% |
| stoch_overbought | 21.5% |
| stoch_oversold | 37.6% |
| stochrsi_cross_dn | 15.5% |
| stochrsi_cross_up | 17.5% |
| stochrsi_overbought | 29.9% |
| stochrsi_oversold | 47.5% |
| supertrend_bearish | 7.8% |
| supertrend_bullish | 92.2% |
| supertrend_flip_dn | 3.1% |
| supertrend_flip_recent_long_5d | 3.6% |
| supertrend_flip_recent_short_5d | 9.3% |
| supertrend_flip_up | 1.2% |
| support_break_retest | 34.8% |
| tema_above_dema | 37.9% |
| tema_cross_dn | 3.6% |
| tema_cross_up | 2.5% |
| three_black_crows | 16.2% |
| three_white_soldiers | 9.8% |
| triangle_apex_break_retest_long | 8.1% |
| triangle_ascending_detected | 5.0% |
| triangle_descending_detected | 9.4% |
| uo_overbought | 4.4% |
| uo_oversold | 7.6% |
| usd_strengthening | 25.7% |
| usd_weakening | 11.0% |
| vix_band_high | 42.4% |
| vix_band_low | 31.1% |
| vix_band_mid | 26.5% |
| vix_term_backwardation | 11.9% |
| vix_term_contango | 88.1% |
| vol_above_avg | 54.2% |
| vol_below_avg | 45.8% |
| vol_spike_12x | 38.4% |
| vol_spike_15x | 21.3% |
| vol_spike_17x | 15.0% |
| vol_spike_2x | 10.3% |
| vol_spike_2x_on_down_day_recent_3d | 9.4% |
| vol_spike_2x_on_up_day_recent_3d | 5.7% |
| vol_spike_3x | 3.5% |
| vp_above_value_area | 18.3% |
| vp_below_value_area | 33.9% |
| vp_close_above_poc | 41.7% |
| vp_close_below_poc | 58.3% |
| vp_in_value_area | 47.8% |
| week_open_gap_down_15pct | 1.9% |
| week_open_gap_up_15pct | 1.1% |
| weekly_above_ema_10 | 38.6% |
| weekly_above_ema_20 | 38.0% |
| weekly_bias_bear | 58.1% |
| weekly_bias_bull | 34.7% |
| weekly_momentum_pos | 38.7% |
| williams_r_overbought | 27.4% |
| williams_r_oversold | 48.0% |
| williams_r_rising | 43.5% |
| within_pead_window | 40.4% |
| within_post_inclusion_window | 0.6% |
| xs_avoid_high_ivol | 73.8% |
| xs_avoid_high_max | 74.1% |
| xs_high_beta_decile | 24.2% |
| xs_low_beta_bottom_quintile | 24.2% |
| xs_low_beta_decile | 17.6% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 17.6% |
| xs_momentum_bottom_decile | 6.5% |
| xs_momentum_bottom_quintile | 16.4% |
| xs_momentum_top_decile | 10.9% |
| xs_momentum_top_quintile | 21.9% |
| xs_quality_bottom_quintile | 20.6% |
| xs_quality_top_quintile | 21.4% |
| xs_quality_top_tercile | 39.8% |
| year_low_break_retest_short | 0.1% |
| yoy_surprise_high | 54.2% |
| yoy_surprise_negative | 35.2% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 89.9% |
| committed_growth_holders | 89.9% |
| corp_donations_1y | 9.9% |
| corp_donations_count_1y | 9.9% |
| corp_donations_unique_pacs | 9.9% |
| cot_rut_commercials_pctile_3y | 54.7% |
| cot_rut_mmoney_pctile_3y | 54.7% |
| cup_handle_depth_pct | 28.7% |
| days_since_deletion | 7.5% |
| days_since_inclusion | 13.9% |
| days_to_next_holiday | 67.1% |
| days_to_rebalance | 8.1% |
| dpi_30d_avg | 96.8% |
| dpi_recent | 96.8% |
| earnings_announcement_return | 90.1% |
| earnings_eps_yoy_growth | 95.1% |
| flag_bull_pole_move_pct | 0.6% |
| gov_contracts_4q_sum | 43.2% |
| gov_contracts_last_qtr_amount | 43.2% |
| gov_contracts_qoq_growth | 43.2% |
| head_shoulders_magnitude_pct | 7.3% |
| insider_director_buyers_30d | 4.8% |
| insider_officer_buyers_30d | 4.8% |
| insider_total_shares_bought_30d | 4.8% |
| insider_unique_buyers_30d | 4.8% |
| inverted_cup_handle_height_pct | 25.4% |
| lobbying_amount_1y | 71.1% |
| lobbying_amount_q | 71.1% |
| lobbying_amount_yoy | 71.1% |
| monthly_momentum_6m | 97.2% |
| otc_short_ratio_recent | 96.8% |
| otc_volume_recent | 96.8% |
| pair_half_life | 91.1% |
| pair_max_abs_zscore | 91.1% |
| pair_zscore_signed | 91.1% |
| pct_from_avwap_20high | 83.9% |
| pct_from_avwap_20low | 69.2% |
| pct_from_avwap_252low | 96.9% |
| pct_from_avwap_50low | 82.2% |
| persistent_holders_4q | 89.9% |
| persistent_holders_8q | 89.9% |
| sc_13g_latest_percent_owned | 1.4% |
| search_volume_index_recent | 78.7% |
| search_volume_observations | 78.7% |
| search_volume_zscore_30d | 78.7% |
| sector_etf_return_20d | 2.3% |
| spy_return_20d | 2.3% |
| total_active_holders | 89.9% |
| triangle_breakdown_pct | 9.4% |
| triangle_breakout_pct | 5.0% |
| xs_quality_decile | 59.4% |
| xs_quality_gross_profitability | 59.4% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.998), `avwap_252low` (0.997), `avwap_50low` (0.998), `bb_10_20_lower` (0.997), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.997), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.997), `cam_s2` (0.997), `cam_s3` (0.997), `cam_s4` (0.997), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.997), `cpr_top` (0.997), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.998), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.994), `entry_stop_short` (0.996), `fib_236` (0.998), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.996), `fib_ext_162` (0.995), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.996), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.995), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.995), `monthly_sma_12` (0.996), `monthly_sma_6` (0.997), `pivot` (0.997), `prev_close` (0.997), `prev_high` (0.998), `prev_low` (0.997), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.997), `s1` (0.997), `s2` (0.996), `s3` (0.995), `supertrend_value` (0.995), `swing_high` (0.997), `swing_low` (0.997), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.997), `vp_value_area_low` (0.996), `vwap` (0.964), `vwap_lower_1` (0.957), `vwap_upper_1` (0.968), `vwap_upper_2` (0.971), `weekly_close` (0.995), `weekly_ema_10` (0.999), `weekly_ema_20` (0.999), `wood_p` (0.997), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.997), `wood_s2` (0.996), `year_high` (0.992), `year_low` (0.985)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
