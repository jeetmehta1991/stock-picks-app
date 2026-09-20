# Table A - naked_poc_retest_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:25:29 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** volume_profile | **status:** NOT-STARTED | **R5 fires:** 1788 | **surviving fires (T1):** 1788 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  naked_poc_count > 0   [EXISTING-THRESHOLD]
P3  naked_poc_nearest_distance_pct < 0.02   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_naked_poc_retest_long (docstring and return dropped):

```python
fires = s.get('naked_poc_count', 0) > 0 and s.get('naked_poc_nearest_distance_pct', 1.0) < 0.02 and s.get('price_above_ema_200', False)
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
| P1 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | STRATEGY | naked_poc_count `> 0` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> 0` | production + 1 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P2.1 | BAND | period_lookback (bars) - backtest/signals/volume_profile.py:152-168 | BRACKET production (1y; half-year alt) | 252 | 126, 252 | none - POC set at other windows unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2.2 | BAND | n_periods (POC chunks) - volume_profile.py:155 | BRACKET production | 6 | 4, 6, 8 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2.3 | BAND | n_bins (price bins) - volume_profile.py:156 | BRACKET production | 40 | 30, 40, 50 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2.4 | BAND | count floor (> N naked POCs) - backtest/signals/screener.py:7004 | BRACKET production; naked_poc_count IS persisted | 0 | 0, 1, 2 | TIGHTER floors (> 1, > 2) - subset on the persisted count | none on this knob | T3 review before any grid |
| P3 | STRATEGY | naked_poc_nearest_distance_pct `< 0.02` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `< 0.02` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| naked_poc_count | backtest/signals/screener.py | `> 0` | 100.0% | TIGHTER = RAISE the floor: 6 -> 1788 (100%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | `< 0.02` | 100.0% | TIGHTER = LOWER the ceiling: 0.0028 -> 364 (20%); 0.0059 -> 719 (40%); 0.0096 -> 1069 (60%); 0.0141 -> 1428 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.174, 19.768, 23.66, 28.586 | 16.174: 1430 (80%); 19.768: 1073 (60%); 23.66: 716 (40%); 28.586: 358 (20%) | 16.174: 358 (20%); 19.768: 715 (40%); 23.66: 1074 (60%); 28.586: 1430 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 17.294, 20.888, 24.312, 28.662 | 17.294: 1430 (80%); 20.888: 1073 (60%); 24.312: 715 (40%); 28.662: 358 (20%) | 17.294: 358 (20%); 20.888: 715 (40%); 24.312: 1073 (60%); 28.662: 1430 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.01, 21.87, 25.454, 30.56 | 18.01: 1431 (80%); 21.87: 1074 (60%); 25.454: 715 (40%); 30.56: 359 (20%) | 18.01: 359 (20%); 21.87: 717 (40%); 25.454: 1073 (60%); 30.56: 1431 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -4.1645, -0.9915, 0.9179, 3.8823 | -4.1645: 1430 (80%); -0.9915: 1073 (60%); 0.9179: 715 (40%); 3.8823: 358 (20%) | -4.1645: 358 (20%); -0.9915: 715 (40%); 0.9179: 1073 (60%); 3.8823: 1430 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2647, 2.1321, 3.551, 6.1069 | 1.2647: 1430 (80%); 2.1321: 1073 (60%); 3.551: 715 (40%); 6.1069: 358 (20%) | 1.2647: 358 (20%); 2.1321: 715 (40%); 3.551: 1073 (60%); 6.1069: 1430 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2647, 2.1321, 3.551, 6.1069 | 1.2647: 1430 (80%); 2.1321: 1073 (60%); 3.551: 715 (40%); 6.1069: 358 (20%) | 1.2647: 358 (20%); 2.1321: 715 (40%); 3.551: 1073 (60%); 6.1069: 1430 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.968, 2.3434, 2.8132, 3.541 | 1.968: 1431 (80%); 2.3434: 1073 (60%); 2.8132: 715 (40%); 3.541: 359 (20%) | 1.968: 359 (20%); 2.3434: 715 (40%); 2.8132: 1073 (60%); 3.541: 1433 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0522, 0.0743, 0.1041, 0.1529 | 0.0522: 1431 (80%); 0.0743: 1075 (60%); 0.1041: 718 (40%); 0.1529: 358 (20%) | 0.0522: 361 (20%); 0.0743: 716 (40%); 0.1041: 1073 (60%); 0.1529: 1431 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.3048, 0.5074, 0.7155, 0.869 | 0.3048: 1430 (80%); 0.5074: 1073 (60%); 0.7155: 715 (40%); 0.869: 358 (20%) | 0.3048: 358 (20%); 0.5074: 717 (40%); 0.7155: 1073 (60%); 0.869: 1430 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0572, 0.0809, 0.1041, 0.1368 | 0.0572: 1432 (80%); 0.0809: 1073 (60%); 0.1041: 716 (40%); 0.1368: 360 (20%) | 0.0572: 358 (20%); 0.0809: 717 (40%); 0.1041: 1075 (60%); 0.1368: 1432 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.1927, 0.4641, 0.7468, 1.0001 | 0.1927: 1431 (80%); 0.4641: 1073 (60%); 0.7468: 715 (40%); 1.0001: 358 (20%) | 0.1927: 358 (20%); 0.4641: 715 (40%); 0.7468: 1073 (60%); 1.0001: 1430 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0763, 0.1078, 0.1388, 0.1824 | 0.0763: 1430 (80%); 0.1078: 1073 (60%); 0.1388: 716 (40%); 0.1824: 358 (20%) | 0.0763: 358 (20%); 0.1078: 716 (40%); 0.1388: 1075 (60%); 0.1824: 1432 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.2695, 0.473, 0.6851, 0.875 | 0.2695: 1431 (80%); 0.473: 1073 (60%); 0.6851: 715 (40%); 0.875: 358 (20%) | 0.2695: 358 (20%); 0.473: 715 (40%); 0.6851: 1073 (60%); 0.875: 1430 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0478, -0.0211, 0.0002, 0.0269 | -0.0478: 1431 (80%); -0.0211: 1076 (60%); 0.0002: 717 (40%); 0.0269: 363 (20%) | -0.0478: 361 (20%); -0.0211: 717 (40%); 0.0002: 1075 (60%); 0.0269: 1438 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1428, 0.164, 0.2038, 0.2598 | 0.1428: 1430 (80%); 0.164: 1077 (60%); 0.2038: 714 (40%); 0.2598: 359 (20%) | 0.1428: 358 (20%); 0.164: 711 (40%); 0.2038: 1074 (60%); 0.2598: 1429 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1788 (100%) | 0: 1709 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.068, 0.0079, 0.0719, 0.1519 | -0.068: 1430 (80%); 0.0079: 1073 (60%); 0.0719: 715 (40%); 0.1519: 358 (20%) | -0.068: 358 (20%); 0.0079: 716 (40%); 0.0719: 1073 (60%); 0.1519: 1431 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1788 (100%); 1: 725 (41%) | 0: 1063 (59%); 1: 1482 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2408, -0.2038, -0.1583, -0.1258 | -0.2408: 1431 (80%); -0.2038: 1073 (60%); -0.1583: 720 (40%); -0.1258: 363 (20%) | -0.2408: 360 (20%); -0.2038: 720 (40%); -0.1583: 1074 (60%); -0.1258: 1431 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3846, 0.6026, 0.6757, 0.7692 | 0.3846: 1438 (80%); 0.6026: 1106 (62%); 0.6757: 715 (40%); 0.7692: 395 (22%) | 0.3846: 360 (20%); 0.6026: 717 (40%); 0.6757: 1073 (60%); 0.7692: 1489 (83%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4167, 0.5962, 0.8462 | 0.2692: 1431 (80%); 0.4167: 1075 (60%); 0.5962: 735 (41%); 0.8462: 359 (20%) | 0.2692: 381 (21%); 0.4167: 721 (40%); 0.5962: 1075 (60%); 0.8462: 1436 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0928, -0.0124, 0.0628, 0.1902 | -0.0928: 1433 (80%); -0.0124: 1073 (60%); 0.0628: 716 (40%); 0.1902: 379 (21%) | -0.0928: 361 (20%); -0.0124: 715 (40%); 0.0628: 1092 (61%); 0.1902: 1431 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.4551, 0.5833, 0.7885 | 0.2628: 1431 (80%); 0.4551: 1075 (60%); 0.5833: 727 (41%); 0.7885: 359 (20%) | 0.2628: 375 (21%); 0.4551: 759 (42%); 0.5833: 1084 (61%); 0.7885: 1438 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.3077, 0.4551, 0.6603 | 0.1346: 1432 (80%); 0.3077: 1074 (60%); 0.4551: 799 (45%); 0.6603: 362 (20%) | 0.1346: 367 (21%); 0.3077: 718 (40%); 0.4551: 1093 (61%); 0.6603: 1432 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5017, -0.3421, -0.171, 0.0648 | -0.5017: 1433 (80%); -0.3421: 1077 (60%); -0.171: 748 (42%); 0.0648: 366 (20%) | -0.5017: 370 (21%); -0.3421: 727 (41%); -0.171: 1074 (60%); 0.0648: 1434 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3269, 0.5192, 0.7436, 0.9167 | 0.3269: 1443 (81%); 0.5192: 1092 (61%); 0.7436: 729 (41%); 0.9167: 427 (24%) | 0.3269: 362 (20%); 0.5192: 742 (41%); 0.7436: 1081 (60%); 0.9167: 1445 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.141, 0.3654, 0.5962, 0.8526 | 0.141: 1434 (80%); 0.3654: 1077 (60%); 0.5962: 720 (40%); 0.8526: 434 (24%) | 0.141: 370 (21%); 0.3654: 720 (40%); 0.5962: 1081 (60%); 0.8526: 1434 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0666, -0.0593, -0.0412, 0 | -0.0666: 1430 (80%); -0.0593: 1093 (61%); -0.0412: 725 (41%); 0: 533 (30%) | -0.0666: 358 (20%); -0.0593: 729 (41%); -0.0412: 1077 (60%); 0: 1742 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4038, 0.6667, 0.8718, 1 | 0.4038: 1435 (80%); 0.6667: 1105 (62%); 0.8718: 736 (41%); 1: 420 (23%) | 0.4038: 359 (20%); 0.6667: 717 (40%); 0.8718: 1076 (60%); 1: 1788 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1603, 0.3141, 0.5769, 0.9038 | 0.1603: 1441 (81%); 0.3141: 1075 (60%); 0.5769: 725 (41%); 0.9038: 366 (20%) | 0.1603: 369 (21%); 0.3141: 754 (42%); 0.5769: 1085 (61%); 0.9038: 1433 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0099, 0.0364, 0.0985, 0.2489 | -0.0099: 1433 (80%); 0.0364: 1076 (60%); 0.0985: 716 (40%); 0.2489: 373 (21%) | -0.0099: 363 (20%); 0.0364: 724 (40%); 0.0985: 1075 (60%); 0.2489: 1495 (84%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4583, 0.782, 0.9353, 0.9744 | 0.4583: 1434 (80%); 0.782: 1073 (60%); 0.9353: 715 (40%); 0.9744: 454 (25%) | 0.4583: 364 (20%); 0.782: 715 (40%); 0.9353: 1073 (60%); 0.9744: 1483 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.2949, 0.5577, 0.7882 | 0.0962: 1433 (80%); 0.2949: 1082 (61%); 0.5577: 726 (41%); 0.7882: 367 (21%) | 0.0962: 379 (21%); 0.2949: 786 (44%); 0.5577: 1083 (61%); 0.7882: 1431 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0202, 0.0621, 0.1463 | -0.0812: 1525 (85%); -0.0202: 1074 (60%); 0.0621: 736 (41%); 0.1463: 365 (20%) | -0.0812: 444 (25%); -0.0202: 717 (40%); 0.0621: 1076 (60%); 0.1463: 1441 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2669, -0.0425, 0.0281, 0.0916 | -0.2669: 1457 (81%); -0.0425: 1077 (60%); 0.0281: 723 (40%); 0.0916: 365 (20%) | -0.2669: 365 (20%); -0.0425: 720 (40%); 0.0281: 1073 (60%); 0.0916: 1437 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2526, 0.5192, 0.7128, 0.8654 | 0.2526: 1430 (80%); 0.5192: 1087 (61%); 0.7128: 715 (40%); 0.8654: 372 (21%) | 0.2526: 358 (20%); 0.5192: 716 (40%); 0.7128: 1073 (60%); 0.8654: 1440 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.391, 0.5833, 0.8269 | 0.1538: 1438 (80%); 0.391: 1079 (60%); 0.5833: 727 (41%); 0.8269: 383 (21%) | 0.1538: 364 (20%); 0.391: 722 (40%); 0.5833: 1080 (60%); 0.8269: 1448 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0621, 0.1474, 0.2794, 0.586 | 0.0621: 1430 (80%); 0.1474: 1073 (60%); 0.2794: 715 (40%); 0.586: 358 (20%) | 0.0621: 358 (20%); 0.1474: 715 (40%); 0.2794: 1073 (60%); 0.586: 1430 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.6% | 21, 61, 82, 140 | 21: 1419 (79%); 61: 1059 (59%); 82: 711 (40%); 140: 361 (20%) | 21: 358 (20%); 61: 738 (41%); 82: 1066 (60%); 140: 1412 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.708, 2.2542, 2.8739, 3.9402 | 1.708: 1425 (80%); 2.2542: 1069 (60%); 2.8739: 713 (40%); 3.9402: 357 (20%) | 1.708: 357 (20%); 2.2542: 713 (40%); 2.8739: 1069 (60%); 3.9402: 1426 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 10.2, 21, 28, 36 | 10.2: 1430 (80%); 21: 1074 (60%); 28: 790 (44%); 36: 368 (21%) | 10.2: 358 (20%); 21: 774 (43%); 28: 1120 (63%); 36: 1474 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 2, 3 | 0: 1788 (100%); 2: 1080 (60%); 3: 688 (38%) | 0: 366 (20%); 2: 1100 (62%); 3: 1440 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0156, -0.0052, 0.0061, 0.0214 | -0.0156: 1431 (80%); -0.0052: 1076 (60%); 0.0061: 717 (40%); 0.0214: 359 (20%) | -0.0156: 358 (20%); -0.0052: 716 (40%); 0.0061: 1074 (60%); 0.0214: 1434 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5181, 25.6734, 26.5261, 27.28 | 24.5181: 1433 (80%); 25.6734: 1074 (60%); 26.5261: 718 (40%); 27.28: 362 (20%) | 24.5181: 361 (20%); 25.6734: 717 (40%); 26.5261: 1077 (60%); 27.28: 1431 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.5876, -0.1082, 0.2372, 0.7112 | -0.5876: 1430 (80%); -0.1082: 1073 (60%); 0.2372: 715 (40%); 0.7112: 358 (20%) | -0.5876: 358 (20%); -0.1082: 715 (40%); 0.2372: 1073 (60%); 0.7112: 1430 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.7112, -0.2372, 0.1082, 0.5876 | -0.7112: 1430 (80%); -0.2372: 1073 (60%); 0.1082: 715 (40%); 0.5876: 358 (20%) | -0.7112: 358 (20%); -0.2372: 715 (40%); 0.1082: 1073 (60%); 0.5876: 1430 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.045, -0.0051, 0.0248, 0.0688 | -0.045: 1431 (80%); -0.0051: 1074 (60%); 0.0248: 720 (40%); 0.0688: 381 (21%) | -0.045: 359 (20%); -0.0051: 716 (40%); 0.0248: 1074 (60%); 0.0688: 1438 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9906, 8.481, 8.7501, 9.0568 | 7.9906: 1430 (80%); 8.481: 1076 (60%); 8.7501: 715 (40%); 9.0568: 356 (20%) | 7.9906: 358 (20%); 8.481: 712 (40%); 8.7501: 1073 (60%); 9.0568: 1432 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0, 1 | 0: 1779 (99%); 1: 565 (32%) | 0: 1214 (68%); 1: 1590 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0 | 0: 1431 (80%) | 0: 1469 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0, 1 | 0: 1779 (99%); 1: 597 (33%) | 0: 1182 (66%); 1: 1569 (88%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 5, 12.2, 259 | 2: 1460 (82%); 5: 1084 (61%); 12.2: 715 (40%); 259: 361 (20%) | 2: 464 (26%); 5: 815 (46%); 12.2: 1073 (60%); 259: 1431 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 3, 69.2, 138 | 0: 1788 (100%); 3: 1091 (61%); 69.2: 715 (40%); 138: 362 (20%) | 0: 378 (21%); 3: 778 (44%); 69.2: 1073 (60%); 138: 1437 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.711, -0.1962, 0.1266, 0.6259 | -0.711: 1430 (80%); -0.1962: 1073 (60%); 0.1266: 715 (40%); 0.6259: 358 (20%) | -0.711: 358 (20%); -0.1962: 715 (40%); 0.1266: 1073 (60%); 0.6259: 1430 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.2241, -0.2361, 0.3593, 1.4747 | -1.2241: 1431 (80%); -0.2361: 1073 (60%); 0.3593: 715 (40%); 1.4747: 358 (20%) | -1.2241: 358 (20%); -0.2361: 715 (40%); 0.3593: 1073 (60%); 1.4747: 1430 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.1418, -0.1962, 0.3836, 1.3961 | -1.1418: 1430 (80%); -0.1962: 1073 (60%); 0.3836: 716 (40%); 1.3961: 358 (20%) | -1.1418: 358 (20%); -0.1962: 715 (40%); 0.3836: 1074 (60%); 1.3961: 1430 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.4934, -0.1077, 0.1287, 0.6042 | -0.4934: 1430 (80%); -0.1077: 1073 (60%); 0.1287: 715 (40%); 0.6042: 358 (20%) | -0.4934: 358 (20%); -0.1077: 715 (40%); 0.1287: 1073 (60%); 0.6042: 1430 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.5095, -0.2913, 0.4922, 1.7193 | -1.5095: 1430 (80%); -0.2913: 1073 (60%); 0.4922: 715 (40%); 1.7193: 358 (20%) | -1.5095: 358 (20%); -0.2913: 715 (40%); 0.4922: 1073 (60%); 1.7193: 1430 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.5318, -0.3102, 0.3796, 1.5162 | -1.5318: 1430 (80%); -0.3102: 1073 (60%); 0.3796: 715 (40%); 1.5162: 358 (20%) | -1.5318: 358 (20%); -0.3102: 716 (40%); 0.3796: 1073 (60%); 1.5162: 1430 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 38.892, 47.996, 56.58, 66.604 | 38.892: 1430 (80%); 47.996: 1073 (60%); 56.58: 718 (40%); 66.604: 358 (20%) | 38.892: 358 (20%); 47.996: 715 (40%); 56.58: 1074 (60%); 66.604: 1430 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 9 | 0: 1788 (100%); 2: 1098 (61%); 4: 765 (43%); 9: 388 (22%) | 0: 429 (24%); 2: 876 (49%); 4: 1112 (62%); 9: 1438 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1429 | 0: 1788 (100%); 0.1429: 365 (20%) | 0: 1229 (69%); 0.1429: 1449 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.4351, 0.6667 | 0: 1788 (100%); 0.2: 1087 (61%); 0.4351: 715 (40%); 0.6667: 417 (23%) | 0: 648 (36%); 0.2: 735 (41%); 0.4351: 1073 (60%); 0.6667: 1448 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 7 | 0: 1788 (100%); 1: 1252 (70%); 3: 753 (42%); 7: 370 (21%) | 0: 536 (30%); 1: 833 (47%); 3: 1163 (65%); 7: 1472 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 1788 (100%); 2: 1098 (61%); 4: 765 (43%); 9: 388 (22%) | 0: 429 (24%); 2: 876 (49%); 4: 1112 (62%); 9: 1438 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1788 (100%); 1: 1272 (71%); 3: 838 (47%); 8: 362 (20%) | 0: 516 (29%); 1: 782 (44%); 3: 1108 (62%); 8: 1470 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0741, 0.269, 0.4094, 0.6137 | 0.0741: 1430 (80%); 0.269: 1073 (60%); 0.4094: 716 (40%); 0.6137: 358 (20%) | 0.0741: 358 (20%); 0.269: 716 (40%); 0.4094: 1073 (60%); 0.6137: 1430 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1741, 0.5841 | 0: 1649 (92%); 0.1741: 715 (40%); 0.5841: 358 (20%) | 0: 954 (53%); 0.1741: 1073 (60%); 0.5841: 1430 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3333, 0.625 | 0: 1668 (93%); 0.3333: 719 (40%); 0.625: 359 (20%) | 0: 758 (42%); 0.3333: 1131 (63%); 0.625: 1434 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.625 | 0: 1668 (93%); 0.3333: 719 (40%); 0.625: 359 (20%) | 0: 758 (42%); 0.3333: 1131 (63%); 0.625: 1434 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1667, 0, 0.1316 | -0.1667: 1431 (80%); 0: 1261 (71%); 0.1316: 358 (20%) | -0.1667: 374 (21%); 0: 1310 (73%); 0.1316: 1430 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7571, -0.3599, 0.1281, 1.3993 | -0.7571: 1432 (80%); -0.3599: 1073 (60%); 0.1281: 715 (40%); 1.3993: 358 (20%) | -0.7571: 366 (20%); -0.3599: 715 (40%); 0.1281: 1073 (60%); 1.3993: 1430 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 12 | 2: 1533 (86%); 4: 1198 (67%); 7: 803 (45%); 12: 371 (21%) | 2: 417 (23%); 4: 731 (41%); 7: 1092 (61%); 12: 1465 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0342, -0.0068, 0.02, 0.062 | -0.0342: 1430 (80%); -0.0068: 1072 (60%); 0.02: 715 (40%); 0.062: 358 (20%) | -0.0342: 358 (20%); -0.0068: 716 (40%); 0.02: 1073 (60%); 0.062: 1430 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0469, -0.0068, 0.0294, 0.0784 | -0.0469: 1430 (80%); -0.0068: 1073 (60%); 0.0294: 714 (40%); 0.0784: 358 (20%) | -0.0469: 358 (20%); -0.0068: 715 (40%); 0.0294: 1074 (60%); 0.0784: 1430 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0278, -0.0026, 0.0169, 0.0477 | -0.0278: 1430 (80%); -0.0026: 1076 (60%); 0.0169: 716 (40%); 0.0477: 358 (20%) | -0.0278: 358 (20%); -0.0026: 713 (40%); 0.0169: 1072 (60%); 0.0477: 1430 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -2.4734, 4.266, 11.8354, 29.1444 | -2.4734: 1430 (80%); 4.266: 1073 (60%); 11.8354: 715 (40%); 29.1444: 358 (20%) | -2.4734: 358 (20%); 4.266: 715 (40%); 11.8354: 1073 (60%); 29.1444: 1430 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.039, 0.053, 0.071, 0.101 | 0.039: 1432 (80%); 0.053: 1074 (60%); 0.071: 716 (40%); 0.101: 358 (20%) | 0.039: 360 (20%); 0.053: 716 (40%); 0.071: 1073 (60%); 0.101: 1430 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5235, 0.7009, 0.8104, 0.9086 | 0.5235: 1430 (80%); 0.7009: 1073 (60%); 0.8104: 716 (40%); 0.9086: 358 (20%) | 0.5235: 358 (20%); 0.7009: 715 (40%); 0.8104: 1075 (60%); 0.9086: 1430 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.1293, -0.2822, 0.4757, 1.4517 | -1.1293: 1430 (80%); -0.2822: 1073 (60%); 0.4757: 715 (40%); 1.4517: 358 (20%) | -1.1293: 358 (20%); -0.2822: 715 (40%); 0.4757: 1073 (60%); 1.4517: 1430 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.6389, -0.2607, 0.1594, 0.6555 | -0.6389: 1430 (80%); -0.2607: 1073 (60%); 0.1594: 715 (40%); 0.6555: 358 (20%) | -0.6389: 358 (20%); -0.2607: 715 (40%); 0.1594: 1073 (60%); 0.6555: 1430 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.0829, -0.2804, 0.5011, 1.399 | -1.0829: 1430 (80%); -0.2804: 1073 (60%); 0.5011: 715 (40%); 1.399: 358 (20%) | -1.0829: 358 (20%); -0.2804: 715 (40%); 0.5011: 1073 (60%); 1.399: 1430 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.2478, -0.792, 2.2752, 6.7 | -4.2478: 1430 (80%); -0.792: 1073 (60%); 2.2752: 715 (40%); 6.7: 359 (20%) | -4.2478: 358 (20%); -0.792: 715 (40%); 2.2752: 1073 (60%); 6.7: 1431 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 44.42, 50.396, 55.862, 62.184 | 44.42: 1431 (80%); 50.396: 1073 (60%); 55.862: 715 (40%); 62.184: 358 (20%) | 44.42: 359 (20%); 50.396: 715 (40%); 55.862: 1073 (60%); 62.184: 1430 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 41.628, 62.56, 79.78, 91.886 | 41.628: 1430 (80%); 62.56: 1074 (60%); 79.78: 716 (40%); 91.886: 358 (20%) | 41.628: 358 (20%); 62.56: 716 (40%); 79.78: 1074 (60%); 91.886: 1430 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 46.678, 50.374, 54.222, 58.794 | 46.678: 1430 (80%); 50.374: 1073 (60%); 54.222: 715 (40%); 58.794: 358 (20%) | 46.678: 358 (20%); 50.374: 715 (40%); 54.222: 1073 (60%); 58.794: 1430 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 42.174, 50.638, 57.932, 66.54 | 42.174: 1430 (80%); 50.638: 1073 (60%); 57.932: 715 (40%); 66.54: 359 (20%) | 42.174: 358 (20%); 50.638: 715 (40%); 57.932: 1073 (60%); 66.54: 1431 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 1786 (100%) | 0: 1788 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0292, 0.0438, 0.0586, 0.0865 | 0.0292: 1431 (80%); 0.0438: 1076 (60%); 0.0586: 716 (40%); 0.0865: 358 (20%) | 0.0292: 361 (20%); 0.0438: 718 (40%); 0.0586: 1075 (60%); 0.0865: 1436 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0811, -0.0586, -0.0438, -0.0349 | -0.0811: 1434 (80%); -0.0586: 1076 (60%); -0.0438: 719 (40%); -0.0349: 359 (20%) | -0.0811: 359 (20%); -0.0586: 716 (40%); -0.0438: 1073 (60%); -0.0349: 1432 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 1788 (100%); 2: 428 (24%) | 0: 1162 (65%); 2: 1460 (82%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 28, 43, 57, 68 | 28: 1448 (81%); 43: 1079 (60%); 57: 719 (40%); 68: 372 (21%) | 28: 404 (23%); 43: 724 (40%); 57: 1079 (60%); 68: 1446 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.7% | 0.0108, 0.0156, 0.0222, 0.0348 | 0.0108: 1413 (79%); 0.0156: 1057 (59%); 0.0222: 706 (39%); 0.0348: 353 (20%) | 0.0108: 352 (20%); 0.0156: 708 (40%); 0.0222: 1059 (59%); 0.0348: 1412 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.3482, 0.509, 0.6568, 0.8337 | 0.3482: 1431 (80%); 0.509: 1073 (60%); 0.6568: 716 (40%); 0.8337: 358 (20%) | 0.3482: 358 (20%); 0.509: 715 (40%); 0.6568: 1073 (60%); 0.8337: 1430 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 40.6, 57.68, 72.82, 98.6 | 40.6: 1432 (80%); 57.68: 1073 (60%); 72.82: 715 (40%); 98.6: 360 (20%) | 40.6: 359 (20%); 57.68: 715 (40%); 72.82: 1073 (60%); 98.6: 1431 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -2.508, -0.1392, 1.7605, 5.414 | -2.508: 1430 (80%); -0.1392: 1073 (60%); 1.7605: 715 (40%); 5.414: 358 (20%) | -2.508: 358 (20%); -0.1392: 715 (40%); 1.7605: 1073 (60%); 5.414: 1430 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 23.116, 40.172, 61.738, 81.826 | 23.116: 1430 (80%); 40.172: 1073 (60%); 61.738: 715 (40%); 81.826: 358 (20%) | 23.116: 358 (20%); 40.172: 715 (40%); 61.738: 1073 (60%); 81.826: 1430 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 23.788, 41.426, 65.482, 84.168 | 23.788: 1430 (80%); 41.426: 1073 (60%); 65.482: 715 (40%); 84.168: 358 (20%) | 23.788: 358 (20%); 41.426: 715 (40%); 65.482: 1073 (60%); 84.168: 1430 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 11.528, 30.794, 64.392, 91.388 | 11.528: 1430 (80%); 30.794: 1073 (60%); 64.392: 715 (40%); 91.388: 358 (20%) | 11.528: 358 (20%); 30.794: 715 (40%); 64.392: 1073 (60%); 91.388: 1430 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 13.654, 37.86, 72.802, 100 | 13.654: 1430 (80%); 37.86: 1073 (60%); 72.802: 715 (40%); 100: 419 (23%) | 13.654: 358 (20%); 37.86: 715 (40%); 72.802: 1073 (60%); 100: 1788 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 12, 17 | 4: 1495 (84%); 7: 1188 (66%); 12: 768 (43%); 17: 401 (22%) | 4: 383 (21%); 7: 721 (40%); 12: 1106 (62%); 17: 1460 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 18 | 5: 1454 (81%); 10: 1082 (61%); 14: 783 (44%); 18: 378 (21%) | 5: 407 (23%); 10: 784 (44%); 14: 1084 (61%); 18: 1517 (85%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 44.774, 50.328, 55.392, 61.362 | 44.774: 1430 (80%); 50.328: 1073 (60%); 55.392: 715 (40%); 61.362: 358 (20%) | 44.774: 358 (20%); 50.328: 715 (40%); 55.392: 1073 (60%); 61.362: 1430 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.123, 0.3611, 0.6706, 0.877 | 0.123: 1434 (80%); 0.3611: 1078 (60%); 0.6706: 717 (40%); 0.877: 363 (20%) | 0.123: 369 (21%); 0.3611: 720 (40%); 0.6706: 1078 (60%); 0.877: 1438 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.77, 17.16, 20.28, 25.15 | 14.77: 1431 (80%); 17.16: 1076 (60%); 20.28: 716 (40%); 25.15: 361 (20%) | 14.77: 359 (20%); 17.16: 716 (40%); 20.28: 1074 (60%); 25.15: 1434 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.77, 17.16, 20.28, 25.15 | 14.77: 1431 (80%); 17.16: 1076 (60%); 20.28: 716 (40%); 25.15: 361 (20%) | 14.77: 359 (20%); 17.16: 716 (40%); 20.28: 1074 (60%); 25.15: 1434 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8542, 0.8872, 0.92, 0.9636 | 0.8542: 1432 (80%); 0.8872: 1074 (60%); 0.92: 721 (40%); 0.9636: 358 (20%) | 0.8542: 359 (20%); 0.8872: 716 (40%); 0.92: 1075 (60%); 0.9636: 1432 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.69, 0.85, 0.98, 1.27 | 0.69: 1455 (81%); 0.85: 1077 (60%); 0.98: 731 (41%); 1.27: 363 (20%) | 0.69: 359 (20%); 0.85: 743 (42%); 0.98: 1078 (60%); 1.27: 1435 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0093, 0.0229, 0.0478, 0.0891 | 0.0093: 1433 (80%); 0.0229: 1074 (60%); 0.0478: 716 (40%); 0.0891: 358 (20%) | 0.0093: 359 (20%); 0.0229: 717 (40%); 0.0478: 1074 (60%); 0.0891: 1432 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 44.988, 72.6386, 110.1781, 186.0186 | 44.988: 1430 (80%); 72.6386: 1073 (60%); 110.1781: 715 (40%); 186.0186: 358 (20%) | 44.988: 358 (20%); 72.6386: 715 (40%); 110.1781: 1073 (60%); 186.0186: 1430 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 42.4338, 69.4422, 105.8963, 179.7806 | 42.4338: 1430 (80%); 69.4422: 1073 (60%); 105.8963: 715 (40%); 179.7806: 358 (20%) | 42.4338: 358 (20%); 69.4422: 715 (40%); 105.8963: 1073 (60%); 179.7806: 1430 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1788 (100%) | 0: 1545 (86%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1788 (100%) | 0: 1616 (90%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0468, -0.0092, 0.0259, 0.0703 | -0.0468: 1431 (80%); -0.0092: 1073 (60%); 0.0259: 716 (40%); 0.0703: 358 (20%) | -0.0468: 359 (20%); -0.0092: 716 (40%); 0.0259: 1074 (60%); 0.0703: 1430 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -70.356, -50.536, -27.928, -9.88 | -70.356: 1430 (80%); -50.536: 1073 (60%); -27.928: 715 (40%); -9.88: 359 (20%) | -70.356: 358 (20%); -50.536: 715 (40%); -27.928: 1073 (60%); -9.88: 1431 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.9% | 0.4923, 0.761, 1.0009, 1.2744 | 0.4923: 1429 (80%); 0.761: 1072 (60%); 1.0009: 715 (40%); 1.2744: 358 (20%) | 0.4923: 358 (20%); 0.761: 715 (40%); 1.0009: 1072 (60%); 1.2744: 1429 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.9% | 2, 5, 7, 9 | 2: 1596 (89%); 5: 1077 (60%); 7: 734 (41%); 9: 390 (22%) | 2: 363 (20%); 5: 868 (49%); 7: 1194 (67%); 9: 1574 (88%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.9% | 0.187, 0.2184, 0.2563, 0.3306 | 0.187: 1429 (80%); 0.2184: 1072 (60%); 0.2563: 716 (40%); 0.3306: 358 (20%) | 0.187: 359 (20%); 0.2184: 715 (40%); 0.2563: 1072 (60%); 0.3306: 1429 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.9% | 3, 5, 7, 9 | 3: 1465 (82%); 5: 1110 (62%); 7: 716 (40%); 9: 377 (21%) | 3: 509 (28%); 5: 897 (50%); 7: 1251 (70%); 9: 1609 (90%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.9% | 0.0236, 0.0318, 0.0414, 0.0613 | 0.0236: 1429 (80%); 0.0318: 1075 (60%); 0.0414: 716 (40%); 0.0613: 359 (20%) | 0.0236: 360 (20%); 0.0318: 718 (40%); 0.0414: 1072 (60%); 0.0613: 1432 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.9% | 3, 5, 7, 9 | 3: 1478 (83%); 5: 1150 (64%); 7: 793 (44%); 9: 432 (24%) | 3: 470 (26%); 5: 822 (46%); 7: 1164 (65%); 9: 1551 (87%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.0784, 0.0186, 0.1323, 0.3053 | -0.0784: 1431 (80%); 0.0186: 1073 (60%); 0.1323: 715 (40%); 0.3053: 358 (20%) | -0.0784: 358 (20%); 0.0186: 715 (40%); 0.1323: 1073 (60%); 0.3053: 1430 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 4, 5, 7, 9 | 4: 1477 (83%); 5: 1287 (72%); 7: 893 (50%); 9: 471 (26%) | 4: 501 (28%); 5: 716 (40%); 7: 1092 (61%); 9: 1530 (86%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.1% |
| 8k_item_5_02_filed_within_7d | 3.1% |
| above_avwap_20high | 45.1% |
| above_avwap_20low | 89.4% |
| above_avwap_252low | 94.7% |
| above_avwap_50low | 80.6% |
| above_cam_r3 | 59.9% |
| above_cam_r4 | 33.8% |
| above_cpr | 75.3% |
| above_pivot | 78.9% |
| above_prev_high | 44.2% |
| above_prev_high_clearance_atr_05 | 17.1% |
| above_prev_low | 94.1% |
| above_r1 | 38.8% |
| above_r2 | 16.6% |
| above_vwap | 74.0% |
| above_wood_p | 72.0% |
| ad_rising | 63.1% |
| adx_cross_up | 1.6% |
| adx_cross_up_20 | 2.4% |
| adx_di_bear | 46.5% |
| adx_di_bull | 53.5% |
| adx_strong | 2.7% |
| adx_trending | 34.0% |
| ao_cross_dn | 2.8% |
| ao_cross_up | 3.1% |
| ao_positive | 50.1% |
| ao_twin_peaks_bull | 5.5% |
| at_key_fib | 21.0% |
| at_key_fib_wide | 49.8% |
| avwap_20high_loss_recent_3d | 12.1% |
| avwap_20high_reclaim_recent_3d | 29.0% |
| avwap_20low_loss_recent_3d | 7.1% |
| avwap_20low_reclaim_recent_3d | 27.7% |
| avwap_252low_loss_recent_3d | 1.2% |
| avwap_252low_reclaim_recent_3d | 18.8% |
| avwap_50low_loss_recent_3d | 7.4% |
| avwap_50low_reclaim_recent_3d | 17.9% |
| bb_10_20_above_mid | 60.6% |
| bb_10_20_expanding | 50.3% |
| bb_10_20_pctb_gt_75 | 36.2% |
| bb_10_20_pctb_gt_8 | 29.8% |
| bb_10_20_pctb_gt_85 | 22.8% |
| bb_10_20_pctb_gt_9 | 16.1% |
| bb_10_20_pctb_gt_95 | 11.1% |
| bb_10_20_pctb_lt_05 | 1.6% |
| bb_10_20_pctb_lt_1 | 2.9% |
| bb_10_20_pctb_lt_15 | 5.2% |
| bb_10_20_pctb_lt_2 | 9.0% |
| bb_10_20_pctb_lt_25 | 14.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 12.1% |
| bb_10_20_reclaim_from_upper_recent_3d | 7.4% |
| bb_10_20_squeeze | 43.8% |
| bb_10_20_touch_lower | 1.8% |
| bb_10_20_touch_upper | 12.5% |
| bb_20_15_above_mid | 57.5% |
| bb_20_15_expanding | 49.3% |
| bb_20_15_pctb_gt_75 | 39.7% |
| bb_20_15_pctb_gt_8 | 34.8% |
| bb_20_15_pctb_gt_85 | 31.4% |
| bb_20_15_pctb_gt_9 | 27.8% |
| bb_20_15_pctb_gt_95 | 24.1% |
| bb_20_15_pctb_lt_05 | 10.9% |
| bb_20_15_pctb_lt_1 | 13.8% |
| bb_20_15_pctb_lt_15 | 16.9% |
| bb_20_15_pctb_lt_2 | 20.9% |
| bb_20_15_pctb_lt_25 | 24.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 18.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 7.7% |
| bb_20_15_squeeze | 39.1% |
| bb_20_15_touch_lower | 11.7% |
| bb_20_15_touch_upper | 25.2% |
| bb_20_20_above_mid | 57.5% |
| bb_20_20_expanding | 49.3% |
| bb_20_20_pctb_gt_75 | 32.7% |
| bb_20_20_pctb_gt_8 | 27.8% |
| bb_20_20_pctb_gt_85 | 22.7% |
| bb_20_20_pctb_gt_9 | 17.7% |
| bb_20_20_pctb_gt_95 | 13.0% |
| bb_20_20_pctb_lt_05 | 3.9% |
| bb_20_20_pctb_lt_1 | 6.5% |
| bb_20_20_pctb_lt_15 | 9.5% |
| bb_20_20_pctb_lt_2 | 13.8% |
| bb_20_20_pctb_lt_25 | 18.2% |
| bb_20_20_reclaim_from_lower_recent_3d | 13.1% |
| bb_20_20_reclaim_from_upper_recent_3d | 4.8% |
| bb_20_20_squeeze | 22.4% |
| bb_20_20_touch_lower | 3.4% |
| bb_20_20_touch_upper | 13.0% |
| bearish_pin_bar | 5.4% |
| below_avwap_20high | 54.9% |
| below_avwap_20low | 10.6% |
| below_avwap_252low | 5.3% |
| below_avwap_50low | 19.4% |
| below_cam_s3 | 6.6% |
| below_cam_s4 | 2.9% |
| below_cpr | 21.1% |
| below_ema_20 | 39.0% |
| below_ema_20_break_recent_5d | 17.3% |
| below_ema_21 | 39.0% |
| below_ema_21_break_recent_5d | 17.3% |
| below_ema_50 | 37.5% |
| below_ema_50_break_recent_5d | 18.2% |
| below_ema_9 | 36.2% |
| below_ema_9_break_recent_5d | 21.0% |
| below_prev_high | 55.5% |
| below_prev_low | 5.8% |
| below_prev_low_clearance_atr_05 | 1.5% |
| below_s1 | 3.9% |
| below_s2 | 1.7% |
| below_sma_20 | 42.5% |
| below_sma_200 | 13.9% |
| below_sma_21 | 42.7% |
| below_sma_50 | 41.7% |
| below_sma_9 | 38.8% |
| below_vwap | 26.0% |
| break_52w_high | 0.1% |
| bullish_engulfing | 10.4% |
| bullish_pin_bar | 5.5% |
| capitulation_recent_3d | 1.2% |
| ceo_buy | 1.0% |
| cfo_buy | 0.3% |
| chandelier_long_bullish | 70.5% |
| chandelier_long_flip_dn | 1.0% |
| chandelier_short_bearish | 52.8% |
| chandelier_short_flip_up | 9.3% |
| classification_change_from_tech | 66.7% |
| classification_change_to_defensive | 33.3% |
| close_in_bottom_40pct_of_range | 8.7% |
| close_in_top_40pct_of_range | 72.9% |
| cluster_buy | 0.4% |
| cmf_cross_dn | 2.3% |
| cmf_cross_up | 8.7% |
| cmf_negative | 37.8% |
| cmf_positive | 62.2% |
| concentrated_sell | 6.8% |
| cpr_narrow | 87.5% |
| cpr_narrow_tight | 23.8% |
| cup_handle_detected | 22.9% |
| cup_handle_neckline_break_retest_long | 6.5% |
| dc10_breakout_dn | 3.1% |
| dc10_breakout_dn_1pct | 6.8% |
| dc10_breakout_up | 18.5% |
| dc10_breakout_up_1pct | 29.3% |
| dc10_new_high | 23.4% |
| dc10_strong_breakout_dn | 0.8% |
| dc10_strong_breakout_up | 7.2% |
| dc20_breakout_dn | 2.1% |
| dc20_breakout_up | 12.7% |
| dc20_new_high | 15.9% |
| dc20_resistance_break_retest_strong | 16.0% |
| dc20_support_break_retest_strong | 11.9% |
| defensive_leadership | 54.4% |
| director_only_buy | 2.8% |
| doji | 4.6% |
| double_bottom_detected | 14.1% |
| double_top_detected | 15.8% |
| dpi_elevated | 57.5% |
| drying_volume_on_up_turn | 62.6% |
| ema_20_50_bearish | 40.0% |
| ema_20_50_bullish | 60.0% |
| ema_20_50_death_cross | 1.0% |
| ema_20_50_golden_cross | 2.7% |
| ema_50_200_bearish | 30.4% |
| ema_50_200_bullish | 69.6% |
| ema_50_200_golden_cross | 0.5% |
| ema_9_21_bearish | 47.8% |
| ema_9_21_bullish | 52.2% |
| ema_9_21_death_cross | 2.0% |
| ema_9_21_golden_cross | 5.0% |
| flag_bear_break_retest_short | 0.1% |
| flag_bear_broke | 0.2% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 0.8% |
| flag_bull_broke | 1.2% |
| flag_bull_detected | 2.0% |
| force_index_cross_dn | 1.4% |
| force_index_cross_up | 9.8% |
| force_index_positive | 59.4% |
| gap_dn_1_5pct | 7.8% |
| gap_dn_2pct | 4.9% |
| gap_up_1_5pct | 7.2% |
| gap_up_2pct | 4.8% |
| hammer | 4.2% |
| head_shoulders_bottom_detected | 4.6% |
| head_shoulders_top_detected | 4.9% |
| house_cluster_buy | 4.3% |
| house_cluster_sell | 4.4% |
| htf_aligned_bear | 1.4% |
| htf_aligned_bull | 40.9% |
| htf_disagreement | 5.7% |
| hull_bearish | 48.1% |
| hull_bullish | 51.9% |
| hull_flip_dn | 3.0% |
| hull_flip_up | 6.6% |
| ichi_above_cloud | 51.3% |
| ichi_above_cloud_break_recent_5d | 18.1% |
| ichi_below_cloud | 28.0% |
| ichi_below_cloud_break_recent_5d | 7.6% |
| ichi_cloud_thick | 86.1% |
| ichi_tk_bearish | 45.6% |
| ichi_tk_bullish | 47.8% |
| ichi_tk_cross_dn | 1.7% |
| ichi_tk_cross_up | 3.0% |
| ichi_weekly_above_cloud | 57.0% |
| ichi_weekly_below_cloud | 11.5% |
| ichi_weekly_in_cloud | 31.5% |
| in_reversal_window | 2.2% |
| inside_bar | 13.5% |
| inside_cpr | 4.6% |
| inside_kc | 85.2% |
| insider_cluster_active | 20.3% |
| institutional_buy | 86.0% |
| institutional_negative | 6.7% |
| institutional_persistence_growing | 39.7% |
| institutional_persistence_strong | 56.6% |
| institutional_strong_buy | 75.9% |
| inverted_cup_handle_detected | 17.2% |
| is_friday | 19.5% |
| is_halloween_period | 57.1% |
| is_halloween_period_first_day | 0.1% |
| is_january | 10.5% |
| is_january_extended | 13.0% |
| is_monday | 20.5% |
| is_pre_holiday | 4.3% |
| is_summer_period | 42.9% |
| is_totm_window | 35.1% |
| is_totm_window_first_day | 10.8% |
| is_week_open | 23.7% |
| kc_touch_lower | 4.2% |
| kc_touch_upper | 14.6% |
| large_dollar_buy | 1.0% |
| macd_12_26_9_bearish | 53.5% |
| macd_12_26_9_bullish | 46.5% |
| macd_12_26_9_crossover_dn | 2.0% |
| macd_12_26_9_crossover_up | 3.5% |
| macd_8_21_5_bearish | 49.9% |
| macd_8_21_5_bullish | 50.1% |
| macd_8_21_5_crossover_dn | 2.3% |
| macd_8_21_5_crossover_up | 5.8% |
| marubozu_bull | 1.7% |
| mfi_broad_overbought | 13.8% |
| mfi_broad_oversold | 6.9% |
| mfi_overbought | 3.4% |
| mfi_oversold | 1.5% |
| monthly_above_sma_12 | 85.3% |
| monthly_above_sma_6 | 66.9% |
| monthly_bias_bear | 5.3% |
| monthly_bias_bull | 57.5% |
| monthly_momentum_pos | 71.6% |
| morning_star | 8.6% |
| near_52w_high | 0.6% |
| near_52w_high_95pct | 5.5% |
| near_52w_high_retest_long | 2.5% |
| near_avwap_20high_atr_05x | 44.8% |
| near_avwap_20high_atr_10x | 70.6% |
| near_avwap_20high_atr_15x | 86.9% |
| near_avwap_20high_atr_20x | 94.8% |
| near_avwap_20low_atr_05x | 27.3% |
| near_avwap_20low_atr_10x | 50.9% |
| near_avwap_20low_atr_15x | 66.9% |
| near_avwap_20low_atr_20x | 79.4% |
| near_avwap_252low_atr_05x | 9.6% |
| near_avwap_252low_atr_10x | 21.0% |
| near_avwap_252low_atr_15x | 32.7% |
| near_avwap_252low_atr_20x | 44.5% |
| near_avwap_50low_atr_05x | 18.6% |
| near_avwap_50low_atr_10x | 37.2% |
| near_avwap_50low_atr_15x | 52.3% |
| near_avwap_50low_atr_20x | 64.5% |
| near_cam_r3 | 24.0% |
| near_cam_s3 | 7.2% |
| near_cam_s4 | 2.5% |
| near_fib_236 | 6.6% |
| near_fib_382 | 7.6% |
| near_fib_500 | 6.9% |
| near_fib_618 | 6.6% |
| near_fib_786 | 3.4% |
| near_pivot | 16.9% |
| near_prev_close | 16.7% |
| near_prev_high | 17.9% |
| near_prev_low | 4.6% |
| near_r1 | 20.7% |
| near_r1_wide | 71.3% |
| near_r2 | 7.7% |
| near_r2_wide | 48.3% |
| near_s1 | 3.8% |
| near_s1_wide | 30.3% |
| near_s2 | 0.7% |
| near_s2_wide | 11.7% |
| near_s3 | 0.2% |
| near_wood_r1 | 12.4% |
| near_wood_s1 | 8.2% |
| news_uses_polygon_score | 23.9% |
| obv_bearish | 41.7% |
| obv_bullish | 58.3% |
| obv_diverge_bull | 8.9% |
| obv_falling | 42.1% |
| obv_rising | 57.9% |
| outside_bar | 9.4% |
| pead_negative_surprise | 14.0% |
| pead_positive_surprise | 24.4% |
| pin_bar | 11.0% |
| po3_accumulation_active | 35.5% |
| po3_bullish | 21.6% |
| po3_manipulation_sweep_down | 6.0% |
| po3_manipulation_sweep_up | 12.4% |
| po3_mmbm_setup | 4.8% |
| po3_sweep_above_prior_high | 64.1% |
| po3_sweep_below_prior_low | 36.5% |
| ppo_bullish | 46.0% |
| ppo_crossover_dn | 1.7% |
| ppo_crossover_up | 3.3% |
| pre_fomc_d0 | 2.0% |
| pre_fomc_d1 | 1.8% |
| pre_fomc_window | 3.9% |
| price_above_dema | 55.8% |
| price_above_ema_20 | 61.0% |
| price_above_ema_200_break_recent_5d | 46.9% |
| price_above_ema_20_break_recent_5d | 32.0% |
| price_above_ema_21 | 61.0% |
| price_above_ema_21_break_recent_5d | 31.4% |
| price_above_ema_50 | 62.5% |
| price_above_ema_50_break_recent_5d | 29.5% |
| price_above_ema_9 | 63.8% |
| price_above_ema_9_break_recent_5d | 41.0% |
| price_above_hull | 62.0% |
| price_above_sma_200 | 86.1% |
| price_above_sma_21 | 57.3% |
| price_above_sma_50 | 58.3% |
| price_above_tema | 60.9% |
| price_below_dema | 44.2% |
| price_below_hull | 38.0% |
| price_below_tema | 39.1% |
| psar_bullish | 50.0% |
| psar_flip_dn | 2.1% |
| psar_flip_up | 4.5% |
| r1_break_retest_long | 59.5% |
| recent_blowoff_at_r3 | 0.1% |
| recent_capitulation_at_s3 | 0.1% |
| resistance_break_retest | 23.5% |
| risk_off_regime_bond_signal | 22.8% |
| risk_off_regime_bond_signal_strong | 9.2% |
| risk_off_regime_gold_signal | 41.9% |
| risk_on_regime_bond_signal | 40.6% |
| risk_on_regime_bond_signal_strong | 18.5% |
| roc_positive | 54.4% |
| roc_turning_dn | 3.0% |
| roc_turning_up | 8.3% |
| rsi_14_bullish | 60.8% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_14_cross_dn_overbought_recent_3d | 2.3% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_14_cross_up_oversold_recent_3d | 3.3% |
| rsi_14_extreme_ob | 0.1% |
| rsi_14_overbought | 5.2% |
| rsi_14_oversold | 0.5% |
| rsi_14_rising | 82.0% |
| rsi_21_bullish | 61.8% |
| rsi_21_cross_dn_overbought_recent_3d | 0.8% |
| rsi_21_cross_up_oversold_recent_3d | 0.3% |
| rsi_21_overbought | 1.1% |
| rsi_21_rising | 82.0% |
| rsi_2_bullish | 72.8% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 17.9% |
| rsi_2_cross_dn_overbought_recent_3d | 19.6% |
| rsi_2_cross_up_extreme_os_recent_3d | 40.9% |
| rsi_2_cross_up_oversold_recent_3d | 48.4% |
| rsi_2_extreme_ob | 39.7% |
| rsi_2_extreme_os | 7.8% |
| rsi_2_overbought | 52.0% |
| rsi_2_oversold | 13.3% |
| rsi_2_rising | 82.0% |
| rsi_9_bullish | 61.5% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.4% |
| rsi_9_cross_dn_overbought_recent_3d | 5.8% |
| rsi_9_cross_up_extreme_os_recent_3d | 1.8% |
| rsi_9_cross_up_oversold_recent_3d | 12.6% |
| rsi_9_extreme_ob | 2.5% |
| rsi_9_overbought | 14.1% |
| rsi_9_oversold | 4.0% |
| rsi_9_rising | 82.0% |
| s1_break_retest_short | 46.8% |
| sc_13d_filed_within_30d | 2.0% |
| sc_13g_filed_within_30d | 3.2% |
| sector_outperforming_spy | 41.5% |
| sector_underperforming_spy | 58.5% |
| shooting_star | 4.7% |
| sma_20_50_bullish | 54.6% |
| sma_20_50_golden_cross | 1.7% |
| sma_50_200_bullish | 65.7% |
| sma_50_200_golden_cross | 0.6% |
| sma_9_21_bullish | 51.2% |
| sma_9_21_golden_cross | 3.5% |
| smc_bos_bearish | 7.5% |
| smc_bos_bullish | 12.0% |
| smc_bos_retest_long | 6.9% |
| smc_bos_retest_short | 5.0% |
| smc_breaker_block_bearish | 6.9% |
| smc_breaker_block_bullish | 25.8% |
| smc_choch_bearish | 5.4% |
| smc_choch_bullish | 5.1% |
| smc_equal_highs_swept | 3.8% |
| smc_equal_lows_swept | 2.9% |
| smc_fvg_bearish_active | 37.2% |
| smc_fvg_bullish_active | 40.4% |
| smc_fvg_retest_long_zone | 2.1% |
| smc_fvg_retest_short_zone | 13.9% |
| smc_in_discount_zone | 52.6% |
| smc_in_premium_zone | 73.5% |
| smc_inverse_fvg_bearish | 81.1% |
| smc_inverse_fvg_bullish | 94.6% |
| smc_liquidity_swept_dn | 1.3% |
| smc_liquidity_swept_up | 1.6% |
| smc_mitigation_block_long | 0.5% |
| smc_mitigation_block_short | 3.2% |
| smc_ob_bearish_active | 24.4% |
| smc_ob_bullish_active | 38.3% |
| smc_ote_long_zone | 11.2% |
| smc_ote_short_zone | 13.7% |
| squeeze_fire_dn | 0.4% |
| squeeze_fire_up | 5.6% |
| squeeze_in | 24.5% |
| squeeze_positive | 58.7% |
| stoch_bearish_cross | 5.9% |
| stoch_broad_overbought | 30.1% |
| stoch_broad_oversold | 21.8% |
| stoch_bullish_cross | 17.2% |
| stoch_overbought | 25.4% |
| stoch_oversold | 15.7% |
| stochrsi_cross_dn | 16.2% |
| stochrsi_cross_up | 36.0% |
| stochrsi_overbought | 35.4% |
| stochrsi_oversold | 26.0% |
| supertrend_bearish | 1.7% |
| supertrend_bullish | 98.3% |
| supertrend_flip_dn | 0.2% |
| supertrend_flip_recent_long_5d | 2.6% |
| supertrend_flip_recent_short_5d | 3.0% |
| supertrend_flip_up | 0.9% |
| support_break_retest | 17.0% |
| tema_above_dema | 47.8% |
| tema_cross_dn | 1.6% |
| tema_cross_up | 2.9% |
| three_white_soldiers | 12.0% |
| triangle_apex_break_retest_long | 14.2% |
| triangle_ascending_detected | 11.0% |
| triangle_descending_detected | 9.5% |
| uo_overbought | 3.6% |
| uo_oversold | 0.8% |
| usd_strengthening | 20.9% |
| usd_weakening | 13.0% |
| vix_band_high | 40.4% |
| vix_band_low | 38.0% |
| vix_band_mid | 21.6% |
| vix_term_backwardation | 9.7% |
| vix_term_contango | 90.3% |
| vol_above_avg | 37.4% |
| vol_below_avg | 62.6% |
| vol_spike_12x | 23.7% |
| vol_spike_15x | 12.4% |
| vol_spike_17x | 7.0% |
| vol_spike_2x | 3.7% |
| vol_spike_2x_on_down_day_recent_3d | 4.9% |
| vol_spike_2x_on_up_day_recent_3d | 4.1% |
| vol_spike_3x | 0.9% |
| vp_above_value_area | 24.8% |
| vp_below_value_area | 7.5% |
| vp_close_above_poc | 61.4% |
| vp_close_below_poc | 38.6% |
| vp_in_value_area | 67.7% |
| week_open_gap_down_15pct | 2.6% |
| week_open_gap_up_15pct | 2.0% |
| weekly_above_ema_10 | 63.0% |
| weekly_above_ema_20 | 75.0% |
| weekly_bias_bear | 22.0% |
| weekly_bias_bull | 60.1% |
| weekly_momentum_pos | 55.5% |
| williams_r_overbought | 32.6% |
| williams_r_oversold | 9.6% |
| williams_r_rising | 76.2% |
| within_pead_window | 39.9% |
| within_post_deletion_window | 1.1% |
| within_post_inclusion_window | 3.1% |
| xs_avoid_high_ivol | 78.9% |
| xs_avoid_high_max | 75.8% |
| xs_high_beta_decile | 21.8% |
| xs_low_beta_bottom_quintile | 21.8% |
| xs_low_beta_decile | 20.3% |
| xs_low_beta_decile_entry_recent_5d | 0.6% |
| xs_low_beta_top_quintile | 20.3% |
| xs_momentum_bottom_decile | 2.6% |
| xs_momentum_bottom_quintile | 8.3% |
| xs_momentum_top_decile | 14.4% |
| xs_momentum_top_quintile | 26.3% |
| xs_quality_bottom_quintile | 19.6% |
| xs_quality_top_quintile | 21.5% |
| xs_quality_top_tercile | 41.9% |
| year_high_break_retest_long | 0.2% |
| yoy_surprise_high | 53.2% |
| yoy_surprise_negative | 36.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.3% |
| committed_growth_holders | 91.3% |
| corp_donations_1y | 8.7% |
| corp_donations_count_1y | 8.7% |
| corp_donations_unique_pacs | 8.7% |
| cot_rut_commercials_pctile_3y | 53.5% |
| cot_rut_mmoney_pctile_3y | 53.5% |
| cup_handle_depth_pct | 30.8% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 5.0% |
| days_since_inclusion | 12.8% |
| days_to_next_holiday | 70.0% |
| days_to_rebalance | 5.8% |
| dpi_30d_avg | 96.0% |
| dpi_recent | 96.0% |
| earnings_announcement_return | 91.0% |
| earnings_eps_yoy_growth | 95.1% |
| flag_bear_pole_move_pct | 0.2% |
| flag_bull_pole_move_pct | 2.0% |
| gov_contracts_4q_sum | 42.9% |
| gov_contracts_last_qtr_amount | 42.9% |
| gov_contracts_qoq_growth | 42.9% |
| head_shoulders_magnitude_pct | 9.3% |
| insider_director_buyers_30d | 4.1% |
| insider_officer_buyers_30d | 4.1% |
| insider_total_shares_bought_30d | 4.1% |
| insider_unique_buyers_30d | 4.1% |
| inverted_cup_handle_height_pct | 28.2% |
| lobbying_amount_1y | 72.9% |
| lobbying_amount_q | 72.9% |
| lobbying_amount_yoy | 72.9% |
| monthly_momentum_6m | 96.2% |
| otc_short_ratio_recent | 96.0% |
| otc_volume_recent | 96.0% |
| pair_half_life | 94.0% |
| pair_max_abs_zscore | 94.0% |
| pair_zscore_signed | 94.0% |
| pct_from_avwap_20high | 83.4% |
| pct_from_avwap_20low | 91.1% |
| pct_from_avwap_252low | 97.0% |
| pct_from_avwap_50low | 96.4% |
| persistent_holders_4q | 91.3% |
| persistent_holders_8q | 91.3% |
| sc_13g_latest_percent_owned | 1.7% |
| search_volume_index_recent | 77.7% |
| search_volume_observations | 77.7% |
| search_volume_zscore_30d | 77.7% |
| sector_etf_return_20d | 2.3% |
| spy_return_20d | 2.3% |
| total_active_holders | 91.3% |
| triangle_breakdown_pct | 9.5% |
| triangle_breakout_pct | 11.0% |
| xs_quality_decile | 58.7% |
| xs_quality_gross_profitability | 58.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.995), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.999), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.998), `entry_stop_short` (0.998), `fib_236` (0.998), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.997), `fib_ext_162` (0.995), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.995), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.998), `monthly_sma_12` (0.994), `monthly_sma_6` (0.997), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.999), `prev_low` (0.998), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.998), `s2` (0.998), `s3` (0.997), `supertrend_value` (0.996), `swing_high` (0.998), `swing_low` (0.997), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.998), `vp_value_area_low` (0.996), `vwap` (0.954), `vwap_upper_1` (0.96), `vwap_upper_2` (0.965), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.999), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.994), `year_low` (0.971)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2 | naked_poc_count > 0 | 2 | subset-safe | no - derives offline |
| P2.1 | period_lookback (bars) | 2 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.2 | n_periods (POC chunks) | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.3 | n_bins (price bins) | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.4 | count floor (> N naked POCs) | 3 | subset-safe | no - derives offline |
| P3 | naked_poc_nearest_distance_pct < 0.02 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     3 x 2 x 2 x 3 x 3 x 3 x 5 = 1620
offline gradings   30 level-combinations x 24 exits = 720
ENGINE RUNS        1 (actuated fire-adding axes only)
PENDING ACTUATION  54 level-combinations are DEFINED but have no env knob - they are a FEATURE REQUEST, not a runnable band (plan 11.0b state 1; B2866)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 624 census axes join it only when REGISTERED at the T3 band review.
