# Table A - mmbm_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build ff10274b7 | commit 352770ae3 at 2026-11-05 02:40:55 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** ict | **status:** NOT-STARTED | **R5 fires:** 1337 (closed fires in the exit cube: 1337 of 1337, S6-B3258) | **surviving fires (T1):** 1337 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  po3_mmbm_setup  <- backtest/signals/ict_producers.py
       DEFN: read the producer source (evidence column)
       knobs bands to define

============================== STRATEGY LAYER ==============================


Gate body, VERBATIM from backtest/signals/screener.py strat_mmbm_long (docstring and return dropped):

```python
fires = bool(s.get('po3_mmbm_setup', False))
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
| P1 | PRODUCER | po3_mmbm_setup - emitted by backtest/signals/ict_producers.py; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
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
| adx | backtest/signals/technical.py | 100.0% | 15.828, 19.374, 24.406, 31.874 | 15.828: 1069 (80%); 19.374: 802 (60%); 24.406: 535 (40%); 31.874: 268 (20%) | 15.828: 268 (20%); 19.374: 535 (40%); 24.406: 802 (60%); 31.874: 1069 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 22.454, 25.604, 27.936, 31.444 | 22.454: 1069 (80%); 25.604: 802 (60%); 27.936: 535 (40%); 31.444: 268 (20%) | 22.454: 268 (20%); 25.604: 535 (40%); 27.936: 802 (60%); 31.444: 1069 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.344, 15.852, 18.38, 21.652 | 13.344: 1069 (80%); 15.852: 802 (60%); 18.38: 535 (40%); 21.652: 268 (20%) | 13.344: 268 (20%); 15.852: 535 (40%); 18.38: 802 (60%); 21.652: 1069 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -5.5879, -2.4175, -0.7967, 0.5818 | -5.5879: 1069 (80%); -2.4175: 802 (60%); -0.7967: 535 (40%); 0.5818: 268 (20%) | -5.5879: 268 (20%); -2.4175: 535 (40%); -0.7967: 802 (60%); 0.5818: 1069 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.894, 2.148, 2.4276, 2.7946 | 1.894: 1070 (80%); 2.148: 803 (60%); 2.4276: 535 (40%); 2.7946: 268 (20%) | 1.894: 271 (20%); 2.148: 536 (40%); 2.4276: 802 (60%); 2.7946: 1069 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0374, 0.0484, 0.0601, 0.0781 | 0.0374: 1070 (80%); 0.0484: 803 (60%); 0.0601: 537 (40%); 0.0781: 269 (20%) | 0.0374: 268 (20%); 0.0484: 538 (40%); 0.0601: 803 (60%); 0.0781: 1072 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2033, 0.2754, 0.3604, 0.4978 | 0.2033: 1069 (80%); 0.2754: 803 (60%); 0.3604: 536 (40%); 0.4978: 268 (20%) | 0.2033: 268 (20%); 0.2754: 535 (40%); 0.3604: 803 (60%); 0.4978: 1069 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0467, 0.0603, 0.0794, 0.1082 | 0.0467: 1070 (80%); 0.0603: 805 (60%); 0.0794: 535 (40%); 0.1082: 268 (20%) | 0.0467: 268 (20%); 0.0603: 535 (40%); 0.0794: 802 (60%); 0.1082: 1070 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.0639, 0.1816, 0.3464, 0.5896 | 0.0639: 1069 (80%); 0.1816: 802 (60%); 0.3464: 535 (40%); 0.5896: 268 (20%) | 0.0639: 268 (20%); 0.1816: 535 (40%); 0.3464: 803 (60%); 0.5896: 1069 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0623, 0.0805, 0.1059, 0.1442 | 0.0623: 1070 (80%); 0.0805: 803 (60%); 0.1059: 535 (40%); 0.1442: 268 (20%) | 0.0623: 268 (20%); 0.0805: 536 (40%); 0.1059: 802 (60%); 0.1442: 1069 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1729, 0.2612, 0.3848, 0.5672 | 0.1729: 1069 (80%); 0.2612: 802 (60%); 0.3848: 535 (40%); 0.5672: 268 (20%) | 0.1729: 268 (20%); 0.2612: 535 (40%); 0.3848: 803 (60%); 0.5672: 1069 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.051, -0.0324, -0.0131, 0.0127 | -0.051: 1072 (80%); -0.0324: 805 (60%); -0.0131: 541 (40%); 0.0127: 278 (21%) | -0.051: 271 (20%); -0.0324: 536 (40%); -0.0131: 807 (60%); 0.0127: 1071 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1387, 0.165, 0.2063, 0.2583 | 0.1387: 1067 (80%); 0.165: 803 (60%); 0.2063: 544 (41%); 0.2583: 263 (20%) | 0.1387: 270 (20%); 0.165: 534 (40%); 0.2063: 793 (59%); 0.2583: 1074 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1337 (100%) | 0: 1239 (93%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1249, -0.0471, 0.0328, 0.119 | -0.1249: 1070 (80%); -0.0471: 802 (60%); 0.0328: 535 (40%); 0.119: 268 (20%) | -0.1249: 268 (20%); -0.0471: 535 (40%); 0.0328: 805 (60%); 0.119: 1069 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1337 (100%); 1: 639 (48%) | 0: 698 (52%); 1: 1097 (82%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2406, -0.2132, -0.1531, -0.1057 | -0.2406: 1069 (80%); -0.2132: 810 (61%); -0.1531: 541 (40%); -0.1057: 268 (20%) | -0.2406: 268 (20%); -0.2132: 539 (40%); -0.1531: 810 (61%); -0.1057: 1069 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3782, 0.5962, 0.6987, 0.8013 | 0.3782: 1070 (80%); 0.5962: 810 (61%); 0.6987: 538 (40%); 0.8013: 323 (24%) | 0.3782: 279 (21%); 0.5962: 544 (41%); 0.6987: 806 (60%); 0.8013: 1102 (82%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2115, 0.3526, 0.6512, 0.8846 | 0.2115: 1141 (85%); 0.3526: 808 (60%); 0.6512: 535 (40%); 0.8846: 282 (21%) | 0.2115: 295 (22%); 0.3526: 541 (40%); 0.6512: 802 (60%); 0.8846: 1079 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1008, -0.0184, 0.0849, 0.2047 | -0.1008: 1071 (80%); -0.0184: 807 (60%); 0.0849: 535 (40%); 0.2047: 276 (21%) | -0.1008: 270 (20%); -0.0184: 539 (40%); 0.0849: 802 (60%); 0.2047: 1073 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.4487, 0.5897, 0.8013 | 0.2564: 1095 (82%); 0.4487: 817 (61%); 0.5897: 538 (40%); 0.8013: 286 (21%) | 0.2564: 277 (21%); 0.4487: 554 (41%); 0.5897: 822 (61%); 0.8013: 1073 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0833, 0.2564, 0.4628, 0.641 | 0.0833: 1071 (80%); 0.2564: 806 (60%); 0.4628: 535 (40%); 0.641: 288 (22%) | 0.0833: 279 (21%); 0.2564: 562 (42%); 0.4628: 802 (60%); 0.641: 1070 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.5212, -0.3421, -0.171, 0.0936 | -0.5212: 1073 (80%); -0.3421: 821 (61%); -0.171: 545 (41%); 0.0936: 269 (20%) | -0.5212: 278 (21%); -0.3421: 538 (40%); -0.171: 812 (61%); 0.0936: 1072 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2898, 0.5321, 0.7244, 0.9359 | 0.2898: 1069 (80%); 0.5321: 818 (61%); 0.7244: 546 (41%); 0.9359: 271 (20%) | 0.2898: 268 (20%); 0.5321: 567 (42%); 0.7244: 807 (60%); 0.9359: 1078 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1231, 0.359, 0.5449, 0.7308 | 0.1231: 1069 (80%); 0.359: 813 (61%); 0.5449: 548 (41%); 0.7308: 276 (21%) | 0.1231: 268 (20%); 0.359: 538 (40%); 0.5449: 806 (60%); 0.7308: 1080 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0657, -0.057, -0.0419, 0 | -0.0657: 1072 (80%); -0.057: 815 (61%); -0.0419: 587 (44%); 0: 376 (28%) | -0.0657: 278 (21%); -0.057: 537 (40%); -0.0419: 826 (62%); 0: 1311 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3936, 0.7308, 0.8718, 1 | 0.3936: 1069 (80%); 0.7308: 804 (60%); 0.8718: 537 (40%); 1: 275 (21%) | 0.3936: 268 (20%); 0.7308: 557 (42%); 0.8718: 813 (61%); 1: 1337 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0833, 0.2372, 0.5513, 0.8526 | 0.0833: 1091 (82%); 0.2372: 812 (61%); 0.5513: 540 (40%); 0.8526: 272 (20%) | 0.0833: 269 (20%); 0.2372: 536 (40%); 0.5513: 807 (60%); 0.8526: 1072 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0191, 0.0193, 0.0456, 0.1462 | -0.0191: 1076 (80%); 0.0193: 803 (60%); 0.0456: 595 (45%); 0.1462: 274 (20%) | -0.0191: 272 (20%); 0.0193: 536 (40%); 0.0456: 824 (62%); 0.1462: 1081 (81%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3692, 0.6731, 0.8966, 0.9615 | 0.3692: 1069 (80%); 0.6731: 806 (60%); 0.8966: 540 (40%); 0.9615: 275 (21%) | 0.3692: 268 (20%); 0.6731: 545 (41%); 0.8966: 873 (65%); 0.9615: 1100 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1169, 0.359, 0.6026, 0.8372 | 0.1169: 1070 (80%); 0.359: 806 (60%); 0.6026: 563 (42%); 0.8372: 271 (20%) | 0.1169: 269 (20%); 0.359: 542 (41%); 0.6026: 808 (60%); 0.8372: 1075 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0158, 0.0689, 0.2068 | -0.0812: 1175 (88%); -0.0158: 808 (60%); 0.0689: 537 (40%); 0.2068: 275 (21%) | -0.0812: 328 (25%); -0.0158: 536 (40%); 0.0689: 806 (60%); 0.2068: 1077 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1527, -0.0245, 0.0442, 0.0659 | -0.1527: 1070 (80%); -0.0245: 802 (60%); 0.0442: 540 (40%); 0.0659: 277 (21%) | -0.1527: 271 (20%); -0.0245: 535 (40%); 0.0442: 803 (60%); 0.0659: 1073 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3397, 0.5321, 0.7179, 0.859 | 0.3397: 1073 (80%); 0.5321: 805 (60%); 0.7179: 539 (40%); 0.859: 270 (20%) | 0.3397: 286 (21%); 0.5321: 540 (40%); 0.7179: 804 (60%); 0.859: 1097 (82%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1859, 0.4423, 0.6603, 0.8269 | 0.1859: 1073 (80%); 0.4423: 827 (62%); 0.6603: 540 (40%); 0.8269: 330 (25%) | 0.1859: 281 (21%); 0.4423: 547 (41%); 0.6603: 804 (60%); 0.8269: 1070 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0517, 0.1117, 0.2163, 0.4048 | 0.0517: 1071 (80%); 0.1117: 804 (60%); 0.2163: 535 (40%); 0.4048: 268 (20%) | 0.0517: 270 (20%); 0.1117: 536 (40%); 0.2163: 802 (60%); 0.4048: 1069 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.4% | 34, 63, 77, 126 | 34: 1063 (80%); 63: 808 (60%); 77: 537 (40%); 126: 267 (20%) | 34: 264 (20%); 63: 536 (40%); 77: 795 (59%); 126: 1056 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.4% | 1.797, 2.3431, 2.9498, 4.0516 | 1.797: 1063 (80%); 2.3431: 797 (60%); 2.9498: 532 (40%); 4.0516: 266 (20%) | 1.797: 266 (20%); 2.3431: 532 (40%); 2.9498: 797 (60%); 4.0516: 1063 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 13, 19.4, 26, 35 | 13: 1079 (81%); 19.4: 802 (60%); 26: 625 (47%); 35: 280 (21%) | 13: 324 (24%); 19.4: 535 (40%); 26: 804 (60%); 35: 1094 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3, 4 | 1: 1105 (83%); 2: 846 (63%); 3: 564 (42%); 4: 273 (20%) | 1: 491 (37%); 2: 773 (58%); 3: 1064 (80%); 4: 1337 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0095, -0.0005, 0.0146, 0.026 | -0.0095: 1073 (80%); -0.0005: 810 (61%); 0.0146: 540 (40%); 0.026: 290 (22%) | -0.0095: 271 (20%); -0.0005: 549 (41%); 0.0146: 806 (60%); 0.026: 1086 (81%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.7166, 25.6656, 26.5048, 27.121 | 24.7166: 1083 (81%); 25.6656: 803 (60%); 26.5048: 545 (41%); 27.121: 268 (20%) | 24.7166: 269 (20%); 25.6656: 536 (40%); 26.5048: 805 (60%); 27.121: 1069 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | 0.0122, 0.2738, 0.602, 1.0784 | 0.0122: 1069 (80%); 0.2738: 802 (60%); 0.602: 536 (40%); 1.0784: 268 (20%) | 0.0122: 268 (20%); 0.2738: 535 (40%); 0.602: 803 (60%); 1.0784: 1069 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -1.0784, -0.602, -0.2738, -0.0122 | -1.0784: 1069 (80%); -0.602: 803 (60%); -0.2738: 535 (40%); -0.0122: 268 (20%) | -1.0784: 268 (20%); -0.602: 536 (40%); -0.2738: 802 (60%); -0.0122: 1069 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.052, -0.0051, 0.0238, 0.053 | -0.052: 1072 (80%); -0.0051: 803 (60%); 0.0238: 535 (40%); 0.053: 268 (20%) | -0.052: 268 (20%); -0.0051: 539 (40%); 0.0238: 802 (60%); 0.053: 1069 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0325, 8.4621, 8.8092, 9.1351 | 8.0325: 1069 (80%); 8.4621: 802 (60%); 8.8092: 537 (40%); 9.1351: 292 (22%) | 8.0325: 268 (20%); 8.4621: 535 (40%); 8.8092: 800 (60%); 9.1351: 1045 (78%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1327 (99%); 1: 396 (30%) | 0: 931 (70%); 1: 1207 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | -1, 0 | -1: 1234 (92%); 0: 1019 (76%) | -1: 308 (23%); 0: 1143 (85%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1327 (99%); 1: 478 (36%) | 0: 849 (64%); 1: 1144 (86%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 148.6, 285.8 | 3: 1077 (81%); 6: 835 (62%); 148.6: 535 (40%); 285.8: 268 (20%) | 3: 352 (26%); 6: 560 (42%); 148.6: 802 (60%); 285.8: 1069 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 3, 82, 128 | 1: 1078 (81%); 3: 853 (64%); 82: 540 (40%); 128: 271 (20%) | 1: 381 (28%); 3: 539 (40%); 82: 804 (60%); 128: 1070 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.3994, -0.1117, 0.0581, 0.3272 | -0.3994: 1070 (80%); -0.1117: 802 (60%); 0.0581: 535 (40%); 0.3272: 268 (20%) | -0.3994: 269 (20%); -0.1117: 535 (40%); 0.0581: 802 (60%); 0.3272: 1069 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.4293, -1.0926, -0.4262, 0.0894 | -2.4293: 1069 (80%); -1.0926: 802 (60%); -0.4262: 535 (40%); 0.0894: 268 (20%) | -2.4293: 268 (20%); -1.0926: 535 (40%); -0.4262: 802 (60%); 0.0894: 1069 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.4452, -1.0894, -0.3861, 0.1574 | -2.4452: 1069 (80%); -1.0894: 802 (60%); -0.3861: 535 (40%); 0.1574: 268 (20%) | -2.4452: 268 (20%); -1.0894: 535 (40%); -0.3861: 802 (60%); 0.1574: 1069 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.2738, -0.1, -0.0013, 0.1456 | -0.2738: 1069 (80%); -0.1: 802 (60%); -0.0013: 535 (40%); 0.1456: 270 (20%) | -0.2738: 268 (20%); -0.1: 535 (40%); -0.0013: 802 (60%); 0.1456: 1070 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.3555, -1.0666, -0.4091, 0.1542 | -2.3555: 1069 (80%); -1.0666: 802 (60%); -0.4091: 535 (40%); 0.1542: 268 (20%) | -2.3555: 268 (20%); -1.0666: 535 (40%); -0.4091: 802 (60%); 0.1542: 1069 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.3365, -1.0466, -0.347, 0.1976 | -2.3365: 1069 (80%); -1.0466: 802 (60%); -0.347: 535 (40%); 0.1976: 268 (20%) | -2.3365: 268 (20%); -1.0466: 535 (40%); -0.347: 802 (60%); 0.1976: 1069 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 30.152, 39.478, 46.9, 55.34 | 30.152: 1069 (80%); 39.478: 802 (60%); 46.9: 535 (40%); 55.34: 269 (20%) | 30.152: 268 (20%); 39.478: 535 (40%); 46.9: 802 (60%); 55.34: 1070 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.2% | -0.1716, -0.1094, -0.0533, 0.0078 | -0.1716: 1061 (79%); -0.1094: 796 (60%); -0.0533: 531 (40%); 0.0078: 266 (20%) | -0.1716: 266 (20%); -0.1094: 532 (40%); -0.0533: 797 (60%); 0.0078: 1061 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.5% | 0.0037, 0.0086, 0.0159, 0.0294 | 0.0037: 1062 (79%); 0.0086: 800 (60%); 0.0159: 533 (40%); 0.0294: 265 (20%) | 0.0037: 268 (20%); 0.0086: 530 (40%); 0.0159: 797 (60%); 0.0294: 1065 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 6 | 0: 1337 (100%); 1: 967 (72%); 3: 563 (42%); 6: 301 (23%) | 0: 370 (28%); 1: 610 (46%); 3: 889 (66%); 6: 1083 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1111 | 0: 1337 (100%); 0.1111: 278 (21%) | 0: 1001 (75%); 0.1111: 1072 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.6473 | 0: 1337 (100%); 0.3333: 589 (44%); 0.6473: 268 (20%) | 0: 603 (45%); 0.3333: 822 (61%); 0.6473: 1069 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 5 | 0: 1337 (100%); 1: 878 (66%); 2: 621 (46%); 5: 269 (20%) | 0: 459 (34%); 1: 716 (54%); 2: 892 (67%); 5: 1119 (84%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 6 | 0: 1337 (100%); 1: 967 (72%); 3: 563 (42%); 6: 301 (23%) | 0: 370 (28%); 1: 610 (46%); 3: 889 (66%); 6: 1083 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 1337 (100%); 1: 914 (68%); 2: 672 (50%); 6: 280 (21%) | 0: 423 (32%); 1: 665 (50%); 2: 810 (61%); 6: 1107 (83%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2049, 0.3463, 0.5556 | 0: 1223 (91%); 0.2049: 802 (60%); 0.3463: 535 (40%); 0.5556: 270 (20%) | 0: 327 (24%); 0.2049: 535 (40%); 0.3463: 802 (60%); 0.5556: 1070 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0447, 0.529 | 0: 1232 (92%); 0.0447: 535 (40%); 0.529: 268 (20%) | 0: 796 (60%); 0.0447: 802 (60%); 0.529: 1069 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5 | 0: 1226 (92%); 0.25: 540 (40%); 0.5: 350 (26%) | 0: 665 (50%); 0.25: 818 (61%); 0.5: 1070 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5 | 0: 1226 (92%); 0.25: 540 (40%); 0.5: 350 (26%) | 0: 665 (50%); 0.25: 818 (61%); 0.5: 1070 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1664, 0, 0.1581 | -0.1664: 1069 (80%); 0: 995 (74%); 0.1581: 268 (20%) | -0.1664: 268 (20%); 0: 975 (73%); 0.1581: 1069 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7881, -0.4472, 0, 0.9691 | -0.7881: 1069 (80%); -0.4472: 889 (66%); 0: 666 (50%); 0.9691: 269 (20%) | -0.7881: 268 (20%); -0.4472: 551 (41%); 0: 862 (64%); 0.9691: 1092 (82%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 6, 10 | 2: 1121 (84%); 4: 848 (63%); 6: 624 (47%); 10: 314 (23%) | 2: 351 (26%); 4: 599 (45%); 6: 806 (60%); 10: 1077 (81%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0421, -0.0226, -0.0058, 0.0153 | -0.0421: 1069 (80%); -0.0226: 802 (60%); -0.0058: 537 (40%); 0.0153: 269 (20%) | -0.0421: 268 (20%); -0.0226: 535 (40%); -0.0058: 800 (60%); 0.0153: 1068 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0702, -0.0417, -0.0138, 0.023 | -0.0702: 1071 (80%); -0.0417: 801 (60%); -0.0138: 535 (40%); 0.023: 268 (20%) | -0.0702: 266 (20%); -0.0417: 536 (40%); -0.0138: 802 (60%); 0.023: 1069 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0234, -0.0153, -0.0088, -0.0017 | -0.0234: 1070 (80%); -0.0153: 802 (60%); -0.0088: 534 (40%); -0.0017: 267 (20%) | -0.0234: 267 (20%); -0.0153: 535 (40%); -0.0088: 803 (60%); -0.0017: 1070 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/technical.py (f-string template) | 99.5% | -3.0054, -1.9356, -1.1898, -0.4334 | -3.0054: 1064 (80%); -1.9356: 798 (60%); -1.1898: 532 (40%); -0.4334: 266 (20%) | -3.0054: 266 (20%); -1.9356: 532 (40%); -1.1898: 798 (60%); -0.4334: 1064 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -19.2808, -10.6314, -3.127, 6.3476 | -19.2808: 1069 (80%); -10.6314: 802 (60%); -3.127: 535 (40%); 6.3476: 268 (20%) | -19.2808: 268 (20%); -10.6314: 535 (40%); -3.127: 802 (60%); 6.3476: 1069 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0308, 0.0368, 0.0419, 0.046 | 0.0308: 1073 (80%); 0.0368: 805 (60%); 0.0419: 535 (40%); 0.046: 269 (20%) | 0.0308: 269 (20%); 0.0368: 535 (40%); 0.0419: 808 (60%); 0.046: 1076 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.6176, 0.7506, 0.8477, 0.9245 | 0.6176: 1069 (80%); 0.7506: 802 (60%); 0.8477: 535 (40%); 0.9245: 269 (20%) | 0.6176: 268 (20%); 0.7506: 535 (40%); 0.8477: 802 (60%); 0.9245: 1070 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.0919, -1.3081, -0.6014, 0.1505 | -2.0919: 1069 (80%); -1.3081: 802 (60%); -0.6014: 535 (40%); 0.1505: 268 (20%) | -2.0919: 268 (20%); -1.3081: 535 (40%); -0.6014: 802 (60%); 0.1505: 1069 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.4255, -0.1732, 0.0744, 0.3454 | -0.4255: 1069 (80%); -0.1732: 802 (60%); 0.0744: 535 (40%); 0.3454: 268 (20%) | -0.4255: 268 (20%); -0.1732: 535 (40%); 0.0744: 802 (60%); 0.3454: 1069 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -2.0972, -1.2836, -0.557, 0.2119 | -2.0972: 1069 (80%); -1.2836: 802 (60%); -0.557: 535 (40%); 0.2119: 268 (20%) | -2.0972: 268 (20%); -1.2836: 535 (40%); -0.557: 802 (60%); 0.2119: 1069 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.9542, -2.7618, -0.7746, 1.4962 | -4.9542: 1069 (80%); -2.7618: 802 (60%); -0.7746: 535 (40%); 1.4962: 268 (20%) | -4.9542: 268 (20%); -2.7618: 535 (40%); -0.7746: 802 (60%); 1.4962: 1069 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 36.4, 41.07, 44.786, 49.32 | 36.4: 1070 (80%); 41.07: 804 (60%); 44.786: 535 (40%); 49.32: 269 (20%) | 36.4: 269 (20%); 41.07: 536 (40%); 44.786: 802 (60%); 49.32: 1070 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 16.33, 28.174, 42.328, 57.03 | 16.33: 1070 (80%); 28.174: 802 (60%); 42.328: 535 (40%); 57.03: 268 (20%) | 16.33: 270 (20%); 28.174: 535 (40%); 42.328: 802 (60%); 57.03: 1069 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 38.642, 42.098, 45.686, 48.886 | 38.642: 1069 (80%); 42.098: 802 (60%); 45.686: 535 (40%); 48.886: 268 (20%) | 38.642: 268 (20%); 42.098: 535 (40%); 45.686: 802 (60%); 48.886: 1069 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 34.232, 39.172, 44.26, 50.022 | 34.232: 1069 (80%); 39.172: 802 (60%); 44.26: 535 (40%); 50.022: 268 (20%) | 34.232: 268 (20%); 39.172: 535 (40%); 44.26: 802 (60%); 50.022: 1069 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1335 (100%) | 0: 1337 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0281, 0.0391, 0.0498, 0.0741 | 0.0281: 1076 (80%); 0.0391: 808 (60%); 0.0498: 536 (40%); 0.0741: 271 (20%) | 0.0281: 269 (20%); 0.0391: 536 (40%); 0.0498: 808 (60%); 0.0741: 1073 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0918, -0.0612, -0.0443, -0.0334 | -0.0918: 1070 (80%); -0.0612: 806 (60%); -0.0443: 538 (40%); -0.0334: 271 (20%) | -0.0918: 271 (20%); -0.0612: 537 (40%); -0.0443: 804 (60%); -0.0334: 1076 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1337 (100%); 1: 366 (27%) | 0: 971 (73%); 1: 1139 (85%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.4% | 29, 41, 53, 68 | 29: 1065 (80%); 41: 812 (61%); 53: 586 (44%); 68: 321 (24%) | 29: 280 (21%); 41: 577 (43%); 53: 799 (60%); 68: 1065 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.6% | 0.0114, 0.0162, 0.0225, 0.0347 | 0.0114: 1055 (79%); 0.0162: 789 (59%); 0.0225: 529 (40%); 0.0347: 264 (20%) | 0.0114: 263 (20%); 0.0162: 529 (40%); 0.0225: 789 (59%); 0.0347: 1054 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.0994, 0.1945, 0.3321, 0.5208 | 0.0994: 1069 (80%); 0.1945: 802 (60%); 0.3321: 535 (40%); 0.5208: 268 (20%) | 0.0994: 268 (20%); 0.1945: 535 (40%); 0.3321: 802 (60%); 0.5208: 1069 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 28, 52.9, 79.16, 122.1 | 28: 1071 (80%); 52.9: 803 (60%); 79.16: 535 (40%); 122.1: 269 (20%) | 28: 269 (20%); 52.9: 537 (40%); 79.16: 802 (60%); 122.1: 1070 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -4.6125, -1.8335, -0.63, 0.672 | -4.6125: 1069 (80%); -1.8335: 802 (60%); -0.63: 535 (40%); 0.672: 268 (20%) | -4.6125: 268 (20%); -1.8335: 535 (40%); -0.63: 802 (60%); 0.672: 1069 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 13.992, 26.308, 45.06, 66.224 | 13.992: 1069 (80%); 26.308: 802 (60%); 45.06: 536 (40%); 66.224: 268 (20%) | 13.992: 268 (20%); 26.308: 535 (40%); 45.06: 803 (60%); 66.224: 1069 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 12.99, 22.524, 40.342, 61.024 | 12.99: 1070 (80%); 22.524: 802 (60%); 40.342: 535 (40%); 61.024: 268 (20%) | 12.99: 269 (20%); 22.524: 535 (40%); 40.342: 802 (60%); 61.024: 1069 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 8.496, 27.872, 59.23, 81.764 | 8.496: 1069 (80%); 27.872: 802 (60%); 59.23: 536 (40%); 81.764: 268 (20%) | 8.496: 268 (20%); 27.872: 535 (40%); 59.23: 803 (60%); 81.764: 1069 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 5.212, 27.372, 56.018, 84.37 | 5.212: 1069 (80%); 27.372: 802 (60%); 56.018: 535 (40%); 84.37: 268 (20%) | 5.212: 268 (20%); 27.372: 535 (40%); 56.018: 802 (60%); 84.37: 1069 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 17 | 4: 1074 (80%); 8: 847 (63%); 13: 542 (41%); 17: 289 (22%) | 4: 311 (23%); 8: 593 (44%); 13: 857 (64%); 17: 1111 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 18 | 5: 1098 (82%); 9: 840 (63%); 14: 548 (41%); 18: 322 (24%) | 5: 290 (22%); 9: 544 (41%); 14: 863 (65%); 18: 1083 (81%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 41.662, 46.448, 50.576, 55.452 | 41.662: 1069 (80%); 46.448: 802 (60%); 50.576: 535 (40%); 55.452: 268 (20%) | 41.662: 268 (20%); 46.448: 535 (40%); 50.576: 802 (60%); 55.452: 1069 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1071, 0.3016, 0.5619, 0.7262 | 0.1071: 1070 (80%); 0.3016: 817 (61%); 0.5619: 535 (40%); 0.7262: 275 (21%) | 0.1071: 276 (21%); 0.3016: 548 (41%); 0.5619: 802 (60%); 0.7262: 1070 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.51, 16.774, 19.08, 22.792 | 14.51: 1070 (80%); 16.774: 802 (60%); 19.08: 540 (40%); 22.792: 268 (20%) | 14.51: 289 (22%); 16.774: 535 (40%); 19.08: 805 (60%); 22.792: 1069 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.51, 16.774, 19.08, 22.792 | 14.51: 1070 (80%); 16.774: 802 (60%); 19.08: 540 (40%); 22.792: 268 (20%) | 14.51: 289 (22%); 16.774: 535 (40%); 19.08: 805 (60%); 22.792: 1069 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8532, 0.8812, 0.9139, 0.9446 | 0.8532: 1073 (80%); 0.8812: 802 (60%); 0.9139: 539 (40%); 0.9446: 270 (20%) | 0.8532: 272 (20%); 0.8812: 535 (40%); 0.9139: 803 (60%); 0.9446: 1071 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.7, 0.82, 0.94, 1.14 | 0.7: 1074 (80%); 0.82: 820 (61%); 0.94: 544 (41%); 1.14: 276 (21%) | 0.7: 282 (21%); 0.82: 540 (40%); 0.94: 808 (60%); 1.14: 1070 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0083, 0.021, 0.0451, 0.0849 | 0.0083: 1070 (80%); 0.021: 803 (60%); 0.0451: 535 (40%); 0.0849: 268 (20%) | 0.0083: 271 (20%); 0.021: 535 (40%); 0.0451: 802 (60%); 0.0849: 1070 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1337 (100%) | 0: 1107 (83%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1337 (100%) | 0: 1304 (98%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.064, -0.0353, -0.0105, 0.0255 | -0.064: 1071 (80%); -0.0353: 803 (60%); -0.0105: 535 (40%); 0.0255: 268 (20%) | -0.064: 268 (20%); -0.0353: 536 (40%); -0.0105: 802 (60%); 0.0255: 1070 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -84.084, -75.22, -60.814, -41.33 | -84.084: 1069 (80%); -75.22: 803 (60%); -60.814: 535 (40%); -41.33: 268 (20%) | -84.084: 268 (20%); -75.22: 536 (40%); -60.814: 802 (60%); -41.33: 1069 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.3% | 0.4273, 0.632, 0.8511, 1.0574 | 0.4273: 1062 (79%); 0.632: 797 (60%); 0.8511: 531 (40%); 1.0574: 266 (20%) | 0.4273: 266 (20%); 0.632: 531 (40%); 0.8511: 797 (60%); 1.0574: 1062 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.3% | 2, 4, 5, 7 | 2: 1123 (84%); 4: 813 (61%); 5: 641 (48%); 7: 367 (27%) | 2: 355 (27%); 4: 687 (51%); 5: 830 (62%); 7: 1088 (81%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.2% | 0.1824, 0.2088, 0.2375, 0.2841 | 0.1824: 1061 (79%); 0.2088: 796 (60%); 0.2375: 531 (40%); 0.2841: 267 (20%) | 0.1824: 266 (20%); 0.2088: 533 (40%); 0.2375: 797 (60%); 0.2841: 1061 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 4, 6, 8 | 3: 1080 (81%); 4: 928 (69%); 6: 583 (44%); 8: 296 (22%) | 3: 398 (30%); 4: 570 (43%); 6: 882 (66%); 8: 1147 (86%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.3% | 0.0178, 0.0237, 0.0293, 0.039 | 0.0178: 1068 (80%); 0.0237: 801 (60%); 0.0293: 533 (40%); 0.039: 266 (20%) | 0.0178: 267 (20%); 0.0237: 532 (40%); 0.0293: 798 (60%); 0.039: 1064 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.3% | 2, 3, 5, 7 | 2: 1107 (83%); 3: 915 (68%); 5: 623 (47%); 7: 349 (26%) | 2: 413 (31%); 3: 571 (43%); 5: 857 (64%); 7: 1105 (83%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.3% | -0.1969, -0.098, -0.0083, 0.0933 | -0.1969: 1062 (79%); -0.098: 797 (60%); -0.0083: 532 (40%); 0.0933: 266 (20%) | -0.1969: 266 (20%); -0.098: 531 (40%); -0.0083: 797 (60%); 0.0933: 1062 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.3% | 2, 4, 5, 7 | 2: 1181 (88%); 4: 798 (60%); 5: 615 (46%); 7: 295 (22%) | 2: 342 (26%); 4: 713 (53%); 5: 893 (67%); 7: 1140 (85%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 3.7% |
| 8k_item_5_02_filed_within_7d | 2.7% |
| above_avwap_20high | 10.9% |
| above_avwap_20low | 69.9% |
| above_avwap_252low | 46.5% |
| above_avwap_50low | 63.6% |
| above_cam_r3 | 33.5% |
| above_cam_r4 | 13.0% |
| above_cpr | 34.5% |
| above_pivot | 43.2% |
| above_prev_high | 8.5% |
| above_prev_high_clearance_atr_05 | 1.2% |
| above_prev_low | 92.1% |
| above_r1 | 11.7% |
| above_r2 | 2.5% |
| above_vwap | 32.0% |
| above_wood_p | 31.0% |
| ad_rising | 44.9% |
| adx_cross_up | 2.2% |
| adx_cross_up_20 | 1.0% |
| adx_di_bear | 84.4% |
| adx_di_bull | 15.6% |
| adx_strong | 7.1% |
| adx_trending | 38.1% |
| ao_cross_dn | 2.7% |
| ao_cross_up | 0.2% |
| ao_positive | 27.8% |
| ao_twin_peaks_bull | 4.3% |
| at_key_fib | 16.5% |
| at_key_fib_wide | 36.6% |
| avwap_20high_loss_recent_3d | 21.7% |
| avwap_20high_reclaim_recent_3d | 6.3% |
| avwap_20low_loss_recent_3d | 32.9% |
| avwap_20low_reclaim_recent_3d | 14.4% |
| avwap_252low_loss_recent_3d | 15.1% |
| avwap_252low_reclaim_recent_3d | 5.0% |
| avwap_50low_loss_recent_3d | 24.7% |
| avwap_50low_reclaim_recent_3d | 9.8% |
| bb_10_20_above_mid | 19.7% |
| bb_10_20_expanding | 35.0% |
| bb_10_20_pctb_gt_75 | 2.2% |
| bb_10_20_pctb_gt_8 | 1.3% |
| bb_10_20_pctb_gt_85 | 0.8% |
| bb_10_20_pctb_gt_9 | 0.7% |
| bb_10_20_pctb_gt_95 | 0.4% |
| bb_10_20_pctb_lt_05 | 0.8% |
| bb_10_20_pctb_lt_1 | 4.0% |
| bb_10_20_pctb_lt_15 | 9.6% |
| bb_10_20_pctb_lt_2 | 19.1% |
| bb_10_20_pctb_lt_25 | 32.7% |
| bb_10_20_reclaim_from_lower_recent_3d | 7.8% |
| bb_10_20_reclaim_from_upper_recent_3d | 0.4% |
| bb_10_20_squeeze | 82.1% |
| bb_10_20_touch_lower | 5.2% |
| bb_10_20_touch_upper | 0.9% |
| bb_20_15_above_mid | 27.4% |
| bb_20_15_expanding | 38.1% |
| bb_20_15_pctb_gt_75 | 7.9% |
| bb_20_15_pctb_gt_8 | 4.3% |
| bb_20_15_pctb_gt_85 | 2.5% |
| bb_20_15_pctb_gt_9 | 1.2% |
| bb_20_15_pctb_gt_95 | 0.6% |
| bb_20_15_pctb_lt_05 | 17.1% |
| bb_20_15_pctb_lt_1 | 26.3% |
| bb_20_15_pctb_lt_15 | 35.8% |
| bb_20_15_pctb_lt_2 | 42.7% |
| bb_20_15_pctb_lt_25 | 49.7% |
| bb_20_15_reclaim_from_lower_recent_3d | 15.5% |
| bb_20_15_reclaim_from_upper_recent_3d | 6.9% |
| bb_20_15_squeeze | 60.4% |
| bb_20_15_touch_lower | 20.6% |
| bb_20_15_touch_upper | 1.0% |
| bb_20_20_above_mid | 27.4% |
| bb_20_20_expanding | 38.1% |
| bb_20_20_pctb_gt_75 | 3.0% |
| bb_20_20_pctb_gt_8 | 1.2% |
| bb_20_20_pctb_gt_85 | 0.5% |
| bb_20_20_pctb_gt_9 | 0.4% |
| bb_20_20_pctb_gt_95 | 0.2% |
| bb_20_20_pctb_lt_05 | 2.8% |
| bb_20_20_pctb_lt_1 | 7.9% |
| bb_20_20_pctb_lt_15 | 15.2% |
| bb_20_20_pctb_lt_2 | 26.3% |
| bb_20_20_pctb_lt_25 | 38.1% |
| bb_20_20_reclaim_from_lower_recent_3d | 7.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 1.0% |
| bb_20_20_squeeze | 39.6% |
| bb_20_20_touch_lower | 4.8% |
| bb_20_20_touch_upper | 0.2% |
| bearish_pin_bar | 1.9% |
| below_avwap_20high | 89.1% |
| below_avwap_20low | 29.9% |
| below_avwap_252low | 53.5% |
| below_avwap_50low | 36.2% |
| below_cam_s3 | 11.9% |
| below_cam_s4 | 3.4% |
| below_cpr | 56.6% |
| below_ema_20 | 80.3% |
| below_ema_200 | 90.3% |
| below_ema_200_break_recent_5d | 14.5% |
| below_ema_20_break_recent_5d | 26.4% |
| below_ema_21 | 80.6% |
| below_ema_21_break_recent_5d | 26.0% |
| below_ema_50 | 88.0% |
| below_ema_50_break_recent_5d | 20.0% |
| below_ema_9 | 80.5% |
| below_ema_9_break_recent_5d | 43.8% |
| below_prev_high | 91.3% |
| below_prev_low | 7.6% |
| below_prev_low_clearance_atr_05 | 0.5% |
| below_s1 | 4.0% |
| below_s2 | 1.0% |
| below_sma_20 | 72.6% |
| below_sma_200 | 84.9% |
| below_sma_21 | 72.7% |
| below_sma_50 | 80.0% |
| below_sma_9 | 82.5% |
| below_vwap | 68.0% |
| bullish_engulfing | 10.7% |
| bullish_pin_bar | 12.6% |
| capitulation_recent_3d | 0.7% |
| ceo_buy | 1.2% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 51.0% |
| chandelier_long_flip_dn | 1.3% |
| chandelier_short_bearish | 84.1% |
| chandelier_short_flip_up | 1.7% |
| classification_change_from_tech | 60.0% |
| classification_change_to_defensive | 40.0% |
| close_in_bottom_40pct_of_range | 4.0% |
| close_in_top_40pct_of_range | 82.0% |
| cluster_buy | 0.7% |
| cmf_cross_dn | 2.0% |
| cmf_cross_up | 6.9% |
| cmf_negative | 52.6% |
| cmf_positive | 47.4% |
| concentrated_sell | 5.0% |
| cpr_narrow | 85.2% |
| cpr_narrow_tight | 21.2% |
| cup_handle_detected | 19.9% |
| cup_handle_neckline_break_retest_long | 1.0% |
| dc10_breakout_dn | 4.7% |
| dc10_breakout_dn_1pct | 31.1% |
| dc10_breakout_up | 0.7% |
| dc10_breakout_up_1pct | 1.8% |
| dc10_new_high | 1.0% |
| dc10_strong_breakout_up | 0.2% |
| dc20_breakout_dn | 3.1% |
| dc20_breakout_up | 0.3% |
| dc20_new_high | 0.4% |
| dc20_resistance_break_retest_strong | 4.6% |
| dc20_support_break_retest_strong | 19.2% |
| defensive_leadership | 48.8% |
| director_only_buy | 4.8% |
| doji | 6.5% |
| double_bottom_detected | 16.3% |
| double_top_detected | 15.4% |
| dpi_elevated | 48.7% |
| drying_volume_on_up_turn | 66.4% |
| ema_20_50_bearish | 80.1% |
| ema_20_50_bullish | 19.9% |
| ema_20_50_death_cross | 1.2% |
| ema_20_50_golden_cross | 0.2% |
| ema_50_200_bearish | 73.2% |
| ema_50_200_bullish | 26.8% |
| ema_50_200_death_cross | 0.5% |
| ema_9_21_bearish | 75.4% |
| ema_9_21_bullish | 24.6% |
| ema_9_21_death_cross | 2.2% |
| ema_9_21_golden_cross | 0.6% |
| flag_bear_break_retest_short | 2.2% |
| flag_bear_broke | 2.5% |
| flag_bear_detected | 3.0% |
| flag_bull_break_retest_long | 0.3% |
| flag_bull_broke | 0.3% |
| flag_bull_detected | 1.5% |
| force_index_cross_dn | 3.3% |
| force_index_cross_up | 4.9% |
| force_index_positive | 22.6% |
| gap_dn_1_5pct | 11.1% |
| gap_dn_2pct | 4.3% |
| gap_up_1_5pct | 0.1% |
| gap_up_2pct | 0.1% |
| hammer | 9.3% |
| head_shoulders_bottom_detected | 4.7% |
| head_shoulders_top_detected | 5.8% |
| house_cluster_buy | 3.0% |
| house_cluster_sell | 5.4% |
| htf_aligned_bear | 72.6% |
| htf_aligned_bull | 4.9% |
| htf_disagreement | 1.3% |
| hull_bearish | 72.3% |
| hull_bullish | 27.7% |
| hull_flip_dn | 8.8% |
| hull_flip_up | 2.8% |
| ichi_above_cloud | 13.7% |
| ichi_above_cloud_break_recent_5d | 2.2% |
| ichi_below_cloud | 71.1% |
| ichi_below_cloud_break_recent_5d | 10.5% |
| ichi_cloud_thick | 82.6% |
| ichi_tk_bearish | 67.7% |
| ichi_tk_bullish | 30.6% |
| ichi_tk_cross_dn | 3.4% |
| ichi_tk_cross_up | 1.8% |
| ichi_weekly_above_cloud | 15.6% |
| ichi_weekly_below_cloud | 54.5% |
| ichi_weekly_in_cloud | 29.9% |
| inside_cpr | 9.5% |
| inside_kc | 95.1% |
| insider_cluster_active | 20.0% |
| institutional_buy | 88.7% |
| institutional_negative | 4.9% |
| institutional_persistence_growing | 45.6% |
| institutional_persistence_strong | 62.9% |
| institutional_strong_buy | 78.5% |
| inverted_cup_handle_detected | 23.1% |
| is_friday | 20.4% |
| is_halloween_period | 49.7% |
| is_halloween_period_first_day | 0.4% |
| is_january | 11.8% |
| is_january_extended | 14.7% |
| is_monday | 17.4% |
| is_pre_holiday | 4.3% |
| is_summer_period | 50.3% |
| is_totm_window | 37.5% |
| is_totm_window_first_day | 9.9% |
| is_week_open | 20.0% |
| kc_touch_lower | 8.5% |
| kc_touch_upper | 0.2% |
| large_dollar_buy | 1.7% |
| macd_12_26_9_bearish | 53.0% |
| macd_12_26_9_bullish | 47.0% |
| macd_12_26_9_crossover_dn | 3.1% |
| macd_12_26_9_crossover_up | 1.1% |
| macd_8_21_5_bearish | 60.4% |
| macd_8_21_5_bullish | 39.6% |
| macd_8_21_5_crossover_dn | 6.2% |
| macd_8_21_5_crossover_up | 3.2% |
| marubozu_bull | 0.7% |
| mfi_broad_overbought | 2.5% |
| mfi_broad_oversold | 19.7% |
| mfi_overbought | 0.1% |
| mfi_oversold | 4.6% |
| monthly_above_sma_12 | 14.7% |
| monthly_above_sma_6 | 16.1% |
| monthly_bias_bear | 76.7% |
| monthly_bias_bull | 7.5% |
| monthly_momentum_pos | 21.7% |
| morning_star | 3.4% |
| near_52w_high | 0.1% |
| near_52w_high_95pct | 1.3% |
| near_52w_high_retest_long | 0.8% |
| near_52w_low | 7.1% |
| near_52w_low_105pct | 18.3% |
| near_avwap_20high_atr_05x | 36.5% |
| near_avwap_20high_atr_10x | 68.0% |
| near_avwap_20high_atr_15x | 84.4% |
| near_avwap_20high_atr_20x | 95.0% |
| near_avwap_20low_atr_05x | 61.5% |
| near_avwap_20low_atr_10x | 88.2% |
| near_avwap_20low_atr_15x | 97.1% |
| near_avwap_20low_atr_20x | 99.4% |
| near_avwap_252low_atr_05x | 24.9% |
| near_avwap_252low_atr_10x | 44.5% |
| near_avwap_252low_atr_15x | 58.8% |
| near_avwap_252low_atr_20x | 70.7% |
| near_avwap_50low_atr_05x | 44.7% |
| near_avwap_50low_atr_10x | 70.8% |
| near_avwap_50low_atr_15x | 83.3% |
| near_avwap_50low_atr_20x | 90.6% |
| near_cam_r3 | 31.2% |
| near_cam_s3 | 17.1% |
| near_cam_s4 | 6.0% |
| near_fib_236 | 2.3% |
| near_fib_382 | 3.6% |
| near_fib_500 | 6.4% |
| near_fib_618 | 6.7% |
| near_fib_786 | 9.1% |
| near_pivot | 36.5% |
| near_prev_close | 35.2% |
| near_prev_high | 9.9% |
| near_prev_low | 20.1% |
| near_r1 | 14.4% |
| near_r1_wide | 78.8% |
| near_r2 | 2.6% |
| near_r2_wide | 33.1% |
| near_s1 | 9.3% |
| near_s1_wide | 70.5% |
| near_s2 | 1.0% |
| near_s2_wide | 29.9% |
| near_s3 | 0.2% |
| near_wood_r1 | 8.5% |
| near_wood_s1 | 27.7% |
| news_uses_polygon_score | 17.9% |
| obv_bearish | 63.8% |
| obv_bullish | 36.2% |
| obv_diverge_bull | 21.2% |
| obv_falling | 67.7% |
| obv_rising | 32.3% |
| outside_bar | 18.5% |
| pead_negative_surprise | 23.3% |
| pead_positive_surprise | 14.5% |
| pin_bar | 14.4% |
| po3_bullish | 60.4% |
| po3_manipulation_sweep_up | 2.3% |
| po3_sweep_above_prior_high | 21.7% |
| ppo_bullish | 45.7% |
| ppo_crossover_dn | 3.1% |
| ppo_crossover_up | 0.8% |
| pre_fomc_d0 | 1.9% |
| pre_fomc_d1 | 2.2% |
| pre_fomc_window | 4.1% |
| price_above_dema | 42.1% |
| price_above_ema_20 | 19.7% |
| price_above_ema_200 | 9.7% |
| price_above_ema_200_break_recent_5d | 1.3% |
| price_above_ema_20_break_recent_5d | 5.2% |
| price_above_ema_21 | 19.4% |
| price_above_ema_21_break_recent_5d | 4.6% |
| price_above_ema_50 | 12.0% |
| price_above_ema_50_break_recent_5d | 1.9% |
| price_above_ema_9 | 19.5% |
| price_above_ema_9_break_recent_5d | 11.1% |
| price_above_hull | 31.9% |
| price_above_sma_200 | 15.1% |
| price_above_sma_21 | 27.3% |
| price_above_sma_50 | 20.0% |
| price_above_tema | 44.8% |
| price_below_dema | 57.9% |
| price_below_hull | 68.1% |
| price_below_tema | 55.2% |
| psar_bullish | 26.3% |
| psar_flip_dn | 11.5% |
| psar_flip_up | 0.6% |
| r1_break_retest_long | 29.8% |
| resistance_break_retest | 6.2% |
| risk_off_regime_bond_signal | 17.8% |
| risk_off_regime_bond_signal_strong | 8.2% |
| risk_off_regime_gold_signal | 41.1% |
| risk_on_regime_bond_signal | 52.8% |
| risk_on_regime_bond_signal_strong | 21.6% |
| roc_positive | 32.8% |
| roc_turning_dn | 6.0% |
| roc_turning_up | 7.3% |
| rsi_14_bullish | 17.9% |
| rsi_14_cross_dn_overbought_recent_3d | 0.7% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_14_cross_up_oversold_recent_3d | 3.7% |
| rsi_14_extreme_os | 0.1% |
| rsi_14_overbought | 0.1% |
| rsi_14_oversold | 5.0% |
| rsi_14_rising | 67.0% |
| rsi_21_bullish | 14.7% |
| rsi_21_cross_dn_overbought_recent_3d | 0.3% |
| rsi_21_cross_up_oversold_recent_3d | 1.5% |
| rsi_21_oversold | 1.4% |
| rsi_21_rising | 67.0% |
| rsi_2_bullish | 27.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 19.0% |
| rsi_2_cross_dn_overbought_recent_3d | 31.6% |
| rsi_2_cross_up_extreme_os_recent_3d | 50.0% |
| rsi_2_cross_up_oversold_recent_3d | 51.4% |
| rsi_2_extreme_ob | 2.8% |
| rsi_2_extreme_os | 26.1% |
| rsi_2_overbought | 7.3% |
| rsi_2_oversold | 42.3% |
| rsi_2_rising | 67.0% |
| rsi_9_bullish | 20.0% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_9_cross_dn_overbought_recent_3d | 2.3% |
| rsi_9_cross_up_extreme_os_recent_3d | 2.1% |
| rsi_9_cross_up_oversold_recent_3d | 9.6% |
| rsi_9_extreme_os | 0.9% |
| rsi_9_overbought | 0.1% |
| rsi_9_oversold | 10.2% |
| rsi_9_rising | 67.0% |
| s1_break_retest_short | 75.5% |
| sc_13d_filed_within_30d | 1.6% |
| sc_13g_filed_within_30d | 3.5% |
| sector_outperforming_spy | 35.7% |
| sector_underperforming_spy | 64.3% |
| shooting_star | 1.4% |
| sma_20_50_bullish | 27.7% |
| sma_20_50_golden_cross | 0.8% |
| sma_50_200_bullish | 31.2% |
| sma_9_21_bullish | 37.8% |
| sma_9_21_golden_cross | 2.7% |
| smc_bos_bearish | 22.1% |
| smc_bos_bullish | 2.8% |
| smc_bos_retest_long | 3.2% |
| smc_bos_retest_short | 6.3% |
| smc_breaker_block_bearish | 23.8% |
| smc_breaker_block_bullish | 12.7% |
| smc_choch_bearish | 7.5% |
| smc_choch_bullish | 2.0% |
| smc_equal_highs_swept | 1.2% |
| smc_equal_lows_swept | 7.9% |
| smc_fvg_bearish_active | 50.0% |
| smc_fvg_bullish_active | 8.2% |
| smc_fvg_retest_long_zone | 0.4% |
| smc_fvg_retest_short_zone | 8.8% |
| smc_in_discount_zone | 87.4% |
| smc_in_premium_zone | 33.0% |
| smc_inverse_fvg_bearish | 97.2% |
| smc_inverse_fvg_bullish | 58.8% |
| smc_liquidity_swept_dn | 1.2% |
| smc_liquidity_swept_up | 1.2% |
| smc_mitigation_block_long | 2.8% |
| smc_mitigation_block_short | 0.3% |
| smc_ob_bearish_active | 53.4% |
| smc_ob_bullish_active | 12.6% |
| smc_ote_long_zone | 11.4% |
| smc_ote_short_zone | 3.9% |
| squeeze_fire_dn | 0.4% |
| squeeze_fire_up | 1.7% |
| squeeze_in | 35.9% |
| squeeze_positive | 29.0% |
| stoch_bearish_cross | 8.0% |
| stoch_broad_overbought | 8.2% |
| stoch_broad_oversold | 43.5% |
| stoch_bullish_cross | 13.2% |
| stoch_overbought | 4.0% |
| stoch_oversold | 34.9% |
| stochrsi_cross_dn | 27.0% |
| stochrsi_cross_up | 30.9% |
| stochrsi_overbought | 23.6% |
| stochrsi_oversold | 35.4% |
| supertrend_bearish | 0.3% |
| supertrend_bullish | 99.7% |
| supertrend_flip_recent_long_5d | 1.0% |
| support_break_retest | 31.2% |
| tema_above_dema | 48.6% |
| tema_cross_dn | 1.6% |
| tema_cross_up | 1.2% |
| three_white_soldiers | 0.1% |
| triangle_apex_break_retest_long | 6.5% |
| triangle_ascending_detected | 9.3% |
| triangle_descending_detected | 15.7% |
| uo_overbought | 0.2% |
| uo_oversold | 0.7% |
| usd_strengthening | 32.3% |
| usd_weakening | 6.9% |
| vix_band_high | 34.3% |
| vix_band_low | 43.1% |
| vix_band_mid | 22.7% |
| vix_term_backwardation | 4.3% |
| vix_term_contango | 95.7% |
| vol_above_avg | 33.6% |
| vol_below_avg | 66.4% |
| vol_spike_12x | 16.5% |
| vol_spike_15x | 7.2% |
| vol_spike_17x | 4.8% |
| vol_spike_2x | 2.8% |
| vol_spike_2x_on_down_day_recent_3d | 1.8% |
| vol_spike_2x_on_up_day_recent_3d | 0.4% |
| vol_spike_3x | 0.2% |
| vp_above_value_area | 4.9% |
| vp_below_value_area | 29.0% |
| vp_close_above_poc | 26.9% |
| vp_close_below_poc | 73.1% |
| vp_in_value_area | 66.0% |
| week_open_gap_down_15pct | 2.1% |
| weekly_above_ema_10 | 13.0% |
| weekly_above_ema_20 | 11.7% |
| weekly_bias_bear | 84.4% |
| weekly_bias_bull | 9.1% |
| weekly_momentum_pos | 34.1% |
| williams_r_overbought | 3.7% |
| williams_r_oversold | 30.3% |
| williams_r_rising | 73.0% |
| within_pead_window | 35.6% |
| within_post_deletion_window | 5.6% |
| within_post_inclusion_window | 1.6% |
| within_pre_rebalance_window | 1.0% |
| xs_avoid_high_ivol | 86.5% |
| xs_avoid_high_max | 90.8% |
| xs_high_beta_decile | 9.8% |
| xs_low_beta_bottom_quintile | 9.8% |
| xs_low_beta_decile | 26.7% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 26.7% |
| xs_momentum_bottom_decile | 11.1% |
| xs_momentum_bottom_quintile | 25.8% |
| xs_momentum_top_decile | 2.4% |
| xs_momentum_top_quintile | 6.7% |
| xs_quality_bottom_quintile | 20.9% |
| xs_quality_top_quintile | 20.1% |
| xs_quality_top_tercile | 36.9% |
| year_low_break_retest_short | 3.4% |
| yoy_surprise_high | 41.1% |
| yoy_surprise_negative | 46.2% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 92.6% |
| committed_growth_holders | 92.6% |
| corp_donations_1y | 8.2% |
| corp_donations_count_1y | 8.2% |
| corp_donations_unique_pacs | 8.2% |
| cot_rut_commercials_pctile_3y | 49.7% |
| cot_rut_mmoney_pctile_3y | 49.7% |
| cup_handle_depth_pct | 23.1% |
| days_since_classification_change | 0.4% |
| days_since_deletion | 4.0% |
| days_since_inclusion | 9.3% |
| days_to_next_holiday | 62.9% |
| days_to_rebalance | 7.6% |
| dpi_30d_avg | 95.8% |
| dpi_recent | 95.8% |
| earnings_announcement_return | 91.0% |
| earnings_eps_yoy_growth | 94.0% |
| flag_bear_pole_move_pct | 3.0% |
| flag_bull_pole_move_pct | 1.5% |
| gov_contracts_4q_sum | 38.7% |
| gov_contracts_last_qtr_amount | 38.7% |
| gov_contracts_qoq_growth | 38.7% |
| head_shoulders_magnitude_pct | 10.1% |
| insider_director_buyers_30d | 7.1% |
| insider_officer_buyers_30d | 7.1% |
| insider_total_shares_bought_30d | 7.1% |
| insider_unique_buyers_30d | 7.1% |
| inverted_cup_handle_height_pct | 26.4% |
| lobbying_amount_1y | 69.9% |
| lobbying_amount_q | 69.9% |
| lobbying_amount_yoy | 69.9% |
| otc_short_ratio_recent | 95.8% |
| otc_volume_recent | 95.8% |
| pair_half_life | 92.7% |
| pair_max_abs_zscore | 92.7% |
| pair_zscore_signed | 92.7% |
| pct_from_avwap_20low | 59.8% |
| pct_from_avwap_252low | 91.8% |
| pct_from_avwap_50low | 75.6% |
| persistent_holders_4q | 92.6% |
| persistent_holders_8q | 92.6% |
| sc_13g_latest_percent_owned | 1.5% |
| search_volume_index_recent | 76.6% |
| search_volume_observations | 76.6% |
| search_volume_zscore_30d | 76.6% |
| sector_etf_return_20d | 3.1% |
| spy_return_20d | 3.1% |
| total_active_holders | 92.6% |
| triangle_breakdown_pct | 15.7% |
| triangle_breakout_pct | 9.3% |
| xs_quality_decile | 61.6% |
| xs_quality_gross_profitability | 61.6% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`atr` (0.961), `atr_14` (0.961), `avwap_20high` (1.0), `avwap_20low` (1.0), `avwap_252low` (0.998), `avwap_50low` (1.0), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (1.0), `bb_20_15_lower` (1.0), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (1.0), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (1.0), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (1.0), `dema` (1.0), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.999), `entry_stop_short` (0.999), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.995), `fib_ext_162` (0.993), `flag_bear_breakdown_level` (0.999), `flag_bull_breakout_level` (0.998), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.995), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.993), `monthly_sma_6` (0.997), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.999), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.999), `swing_high` (0.996), `swing_low` (0.998), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.997), `vp_value_area_low` (0.998), `vwap` (0.969), `vwap_lower_1` (0.966), `vwap_lower_2` (0.963), `vwap_upper_1` (0.97), `vwap_upper_2` (0.971), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.984), `year_low` (0.992)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|

```
FULL FACTORIAL     0 = 0
offline gradings   0 level-combinations x 24 exits = 0 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        0 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  0 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             0 + 0 + 0 = 0 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 0 x 3.66 h = 0 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 613 census axes join it only when REGISTERED at the T3 band review.
