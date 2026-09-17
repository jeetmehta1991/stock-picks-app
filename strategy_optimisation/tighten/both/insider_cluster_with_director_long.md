# Table A - insider_cluster_with_director_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** event_driven | **status:** NOT-STARTED | **R5 fires:** 24 | **surviving fires (T1):** 24 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  insider_cluster_active  <- backtest/signals/insider_buying.py +1
       knobs P1.1-P1.1 (band rows in Table A)
P2  insider_unique_buyers_30d  <- backtest/signals/insider_buying.py +1
       knobs P2.1-P2.1 (band rows in Table A)
P3  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       knobs P3.1-P3.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P4  insider_director_buyers_30d >= 1   [EXISTING-THRESHOLD]
P5  insider_officer_buyers_30d >= 1   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_insider_cluster_with_director_long (docstring and return dropped):

```python
fires = s.get('insider_cluster_active', False) and (s.get('insider_director_buyers_30d', 0) >= 1 or s.get('insider_officer_buyers_30d', 0) >= 1) and s.get('price_above_ema_200', False)
n = s.get('insider_unique_buyers_30d', 0)
n_dir = s.get('insider_director_buyers_30d', 0)
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
| P1 | PRODUCER | insider_cluster_active - emitted by backtest/signals/insider_buying.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | cluster rule (unique buyers >= N in window) - backtest/data/smart_money.py cluster block | N in 30d | N-side TIGHTER via persisted insider_unique_buyers_30d | window changes; DEFINED-NO-ACTUATOR | BRACKET the shipped cluster rule; T3 review before any grid |
| P2 | PRODUCER | insider_unique_buyers_30d - emitted by backtest/signals/insider_buying.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | count window (days) - backtest/data/smart_money.py:433-439 region | 30 | count floors via the persisted count | window changes; DEFINED-NO-ACTUATOR | BRACKET production; T3 review before any grid |
| P3 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | 200 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production; 150/250 are the adjacent canon spans; T3 review before any grid |
| P4 | STRATEGY | insider_director_buyers_30d `>= 1` [EXISTING-THRESHOLD] | `>= 1` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5 | STRATEGY | insider_officer_buyers_30d `>= 1` [EXISTING-THRESHOLD] | `>= 1` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| insider_director_buyers_30d | backtest/signals/insider_buying.py +1 | `>= 1` | 100.0% | TIGHTER = RAISE the floor: 2 -> 13 (54%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| insider_officer_buyers_30d | backtest/signals/insider_buying.py +1 | `>= 1` | 100.0% | TIGHTER = RAISE the floor: 3.4 -> 5 (21%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 18.728, 21.446, 23.862, 29.186 | 18.728: 19 (79%); 21.446: 14 (58%); 23.862: 10 (42%); 29.186: 5 (21%) | 18.728: 5 (21%); 21.446: 10 (42%); 23.862: 14 (58%); 29.186: 19 (79%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 13.592, 15.358, 19.942, 23.65 | 13.592: 19 (79%); 15.358: 14 (58%); 19.942: 10 (42%); 23.65: 5 (21%) | 13.592: 5 (21%); 15.358: 10 (42%); 19.942: 14 (58%); 23.65: 19 (79%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 23.612, 26.288, 30.784, 34.71 | 23.612: 19 (79%); 26.288: 14 (58%); 30.784: 10 (42%); 34.71: 5 (21%) | 23.612: 5 (21%); 26.288: 10 (42%); 30.784: 14 (58%); 34.71: 19 (79%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 0.3966, 1.1604, 1.946, 3.8895 | 0.3966: 19 (79%); 1.1604: 14 (58%); 1.946: 10 (42%); 3.8895: 5 (21%) | 0.3966: 5 (21%); 1.1604: 10 (42%); 1.946: 14 (58%); 3.8895: 19 (79%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.0584, 1.7279, 3.1177, 5.5938 | 1.0584: 19 (79%); 1.7279: 14 (58%); 3.1177: 10 (42%); 5.5938: 5 (21%) | 1.0584: 5 (21%); 1.7279: 10 (42%); 3.1177: 14 (58%); 5.5938: 19 (79%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.0584, 1.7279, 3.1177, 5.5938 | 1.0584: 19 (79%); 1.7279: 14 (58%); 3.1177: 10 (42%); 5.5938: 5 (21%) | 1.0584: 5 (21%); 1.7279: 10 (42%); 3.1177: 14 (58%); 5.5938: 19 (79%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.9278, 2.5002, 3.2128, 3.5206 | 1.9278: 19 (79%); 2.5002: 14 (58%); 3.2128: 10 (42%); 3.5206: 5 (21%) | 1.9278: 5 (21%); 2.5002: 10 (42%); 3.2128: 14 (58%); 3.5206: 19 (79%) | OFFLINE |
| avg_position_age_quarters | backtest/signals/institutional_persistence_consumer.py | 100.0% | 4.32, 6.446, 7.396, 8.958 | 4.32: 19 (79%); 6.446: 14 (58%); 7.396: 10 (42%); 8.958: 5 (21%) | 4.32: 5 (21%); 6.446: 10 (42%); 7.396: 14 (58%); 8.958: 19 (79%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0562, 0.0711, 0.1227, 0.1797 | 0.0562: 19 (79%); 0.0711: 14 (58%); 0.1227: 10 (42%); 0.1797: 5 (21%) | 0.0562: 5 (21%); 0.0711: 10 (42%); 0.1227: 14 (58%); 0.1797: 19 (79%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.4665, 0.7743, 0.9153, 0.9805 | 0.4665: 19 (79%); 0.7743: 14 (58%); 0.9153: 10 (42%); 0.9805: 5 (21%) | 0.4665: 5 (21%); 0.7743: 10 (42%); 0.9153: 14 (58%); 0.9805: 19 (79%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0631, 0.0742, 0.1175, 0.1482 | 0.0631: 19 (79%); 0.0742: 14 (58%); 0.1175: 10 (42%); 0.1482: 5 (21%) | 0.0631: 5 (21%); 0.0742: 10 (42%); 0.1175: 14 (58%); 0.1482: 19 (79%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.7174, 0.9306, 1.1227, 1.3183 | 0.7174: 19 (79%); 0.9306: 14 (58%); 1.1227: 10 (42%); 1.3183: 5 (21%) | 0.7174: 5 (21%); 0.9306: 10 (42%); 1.1227: 14 (58%); 1.3183: 19 (79%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0842, 0.099, 0.1567, 0.1976 | 0.0842: 19 (79%); 0.099: 14 (58%); 0.1567: 10 (42%); 0.1976: 5 (21%) | 0.0842: 5 (21%); 0.099: 10 (42%); 0.1567: 14 (58%); 0.1976: 19 (79%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.6631, 0.8229, 0.967, 1.1138 | 0.6631: 19 (79%); 0.8229: 14 (58%); 0.967: 10 (42%); 1.1138: 5 (21%) | 0.6631: 5 (21%); 0.8229: 10 (42%); 0.967: 14 (58%); 1.1138: 19 (79%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0406, -0.019, 0.0028, 0.0226 | -0.0406: 19 (79%); -0.019: 14 (58%); 0.0028: 10 (42%); 0.0226: 5 (21%) | -0.0406: 5 (21%); -0.019: 10 (42%); 0.0028: 14 (58%); 0.0226: 19 (79%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.131, 0.1491, 0.1656, 0.2548 | 0.131: 19 (79%); 0.1491: 14 (58%); 0.1656: 10 (42%); 0.2548: 5 (21%) | 0.131: 5 (21%); 0.1491: 10 (42%); 0.1656: 14 (58%); 0.2548: 19 (79%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 2, 2.2, 4, 8.4 | 2: 21 (88%); 2.2: 14 (58%); 4: 11 (46%); 8.4: 5 (21%) | 2: 10 (42%); 2.2: 10 (42%); 4: 17 (71%); 8.4: 19 (79%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | 0.0028, 0.0578, 0.1243, 0.2171 | 0.0028: 19 (79%); 0.0578: 14 (58%); 0.1243: 10 (42%); 0.2171: 5 (21%) | 0.0028: 5 (21%); 0.0578: 10 (42%); 0.1243: 14 (58%); 0.2171: 19 (79%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 0.8, 1 | 0: 24 (100%); 0.8: 10 (42%); 1: 10 (42%) | 0: 14 (58%); 0.8: 14 (58%); 1: 21 (88%) | OFFLINE |
| committed_growth_holders | backtest/signals/institutional_persistence_consumer.py +1 | 100.0% | 2, 3.4, 5, 142.8 | 2: 21 (88%); 3.4: 14 (58%); 5: 14 (58%); 142.8: 5 (21%) | 2: 8 (33%); 3.4: 10 (42%); 5: 15 (62%); 142.8: 19 (79%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2706, -0.2365, -0.2166, -0.1668 | -0.2706: 19 (79%); -0.2365: 15 (62%); -0.2166: 10 (42%); -0.1668: 5 (21%) | -0.2706: 5 (21%); -0.2365: 11 (46%); -0.2166: 14 (58%); -0.1668: 19 (79%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.0321, 0.4, 0.5897, 0.659 | 0.0321: 20 (83%); 0.4: 14 (58%); 0.5897: 11 (46%); 0.659: 5 (21%) | 0.0321: 6 (25%); 0.4: 10 (42%); 0.5897: 15 (62%); 0.659: 19 (79%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.4705, 0.6833, 0.8179, 0.9282 | 0.4705: 19 (79%); 0.6833: 14 (58%); 0.8179: 10 (42%); 0.9282: 5 (21%) | 0.4705: 5 (21%); 0.6833: 10 (42%); 0.8179: 14 (58%); 0.9282: 19 (79%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0481, 0.016, 0.0811, 0.1255 | -0.0481: 19 (79%); 0.016: 14 (58%); 0.0811: 10 (42%); 0.1255: 5 (21%) | -0.0481: 5 (21%); 0.016: 10 (42%); 0.0811: 14 (58%); 0.1255: 19 (79%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4, 0.4821, 0.6961, 0.7244 | 0.4: 19 (79%); 0.4821: 14 (58%); 0.6961: 10 (42%); 0.7244: 7 (29%) | 0.4: 5 (21%); 0.4821: 10 (42%); 0.6961: 14 (58%); 0.7244: 20 (83%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0807, 0.2334, 0.3077, 0.4436 | 0.0807: 19 (79%); 0.2334: 14 (58%); 0.3077: 10 (42%); 0.4436: 5 (21%) | 0.0807: 5 (21%); 0.2334: 10 (42%); 0.3077: 14 (58%); 0.4436: 19 (79%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4922, -0.2789, -0.0802, 0.099 | -0.4922: 19 (79%); -0.2789: 14 (58%); -0.0802: 10 (42%); 0.099: 5 (21%) | -0.4922: 5 (21%); -0.2789: 10 (42%); -0.0802: 14 (58%); 0.099: 19 (79%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.359, 0.5423, 0.7757, 0.9295 | 0.359: 19 (79%); 0.5423: 14 (58%); 0.7757: 10 (42%); 0.9295: 5 (21%) | 0.359: 5 (21%); 0.5423: 10 (42%); 0.7757: 14 (58%); 0.9295: 19 (79%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2244, 0.4423, 0.5603, 0.7757 | 0.2244: 19 (79%); 0.4423: 14 (58%); 0.5603: 10 (42%); 0.7757: 5 (21%) | 0.2244: 5 (21%); 0.4423: 10 (42%); 0.5603: 14 (58%); 0.7757: 19 (79%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0649, -0.0618, -0.0421, 0 | -0.0649: 19 (79%); -0.0618: 14 (58%); -0.0421: 10 (42%); 0: 6 (25%) | -0.0649: 5 (21%); -0.0618: 10 (42%); -0.0421: 14 (58%); 0: 24 (100%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3961, 0.4885, 0.7257, 0.9936 | 0.3961: 19 (79%); 0.4885: 14 (58%); 0.7257: 10 (42%); 0.9936: 6 (25%) | 0.3961: 5 (21%); 0.4885: 10 (42%); 0.7257: 14 (58%); 0.9936: 20 (83%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2603, 0.4, 0.5705, 0.791 | 0.2603: 19 (79%); 0.4: 14 (58%); 0.5705: 10 (42%); 0.791: 5 (21%) | 0.2603: 5 (21%); 0.4: 10 (42%); 0.5705: 14 (58%); 0.791: 19 (79%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0028, 0.041, 0.1677, 0.3623 | 0.0028: 19 (79%); 0.041: 14 (58%); 0.1677: 10 (42%); 0.3623: 5 (21%) | 0.0028: 5 (21%); 0.041: 10 (42%); 0.1677: 14 (58%); 0.3623: 19 (79%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5156, 0.7717, 0.921, 0.9744 | 0.5156: 19 (79%); 0.7717: 14 (58%); 0.921: 10 (42%); 0.9744: 6 (25%) | 0.5156: 5 (21%); 0.7717: 10 (42%); 0.921: 14 (58%); 0.9744: 20 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0952, 0.1372, 0.2908, 0.8526 | 0.0952: 20 (83%); 0.1372: 14 (58%); 0.2908: 10 (42%); 0.8526: 5 (21%) | 0.0952: 6 (25%); 0.1372: 10 (42%); 0.2908: 14 (58%); 0.8526: 19 (79%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0565, 0.0123, 0.0606, 0.1474 | -0.0565: 19 (79%); 0.0123: 15 (62%); 0.0606: 10 (42%); 0.1474: 5 (21%) | -0.0565: 5 (21%); 0.0123: 11 (46%); 0.0606: 14 (58%); 0.1474: 19 (79%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2436, -0.058, 0.0274, 0.1051 | -0.2436: 19 (79%); -0.058: 15 (62%); 0.0274: 10 (42%); 0.1051: 5 (21%) | -0.2436: 5 (21%); -0.058: 11 (46%); 0.0274: 14 (58%); 0.1051: 19 (79%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2744, 0.5539, 0.6603, 0.8385 | 0.2744: 19 (79%); 0.5539: 14 (58%); 0.6603: 10 (42%); 0.8385: 5 (21%) | 0.2744: 5 (21%); 0.5539: 10 (42%); 0.6603: 14 (58%); 0.8385: 19 (79%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.4731, 0.6, 0.8192, 0.9423 | 0.4731: 19 (79%); 0.6: 14 (58%); 0.8192: 10 (42%); 0.9423: 6 (25%) | 0.4731: 5 (21%); 0.6: 10 (42%); 0.8192: 14 (58%); 0.9423: 20 (83%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0513, 0.0943, 0.3273, 0.4367 | 0.0513: 19 (79%); 0.0943: 14 (58%); 0.3273: 10 (42%); 0.4367: 5 (21%) | 0.0513: 5 (21%); 0.0943: 10 (42%); 0.3273: 14 (58%); 0.4367: 19 (79%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 18.8, 43, 106.2, 148.2 | 18.8: 19 (79%); 43: 14 (58%); 106.2: 10 (42%); 148.2: 5 (21%) | 18.8: 5 (21%); 43: 10 (42%); 106.2: 14 (58%); 148.2: 19 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 1.6201, 2.2531, 3.0456, 4.3566 | 1.6201: 19 (79%); 2.2531: 14 (58%); 3.0456: 10 (42%); 4.3566: 5 (21%) | 1.6201: 5 (21%); 2.2531: 10 (42%); 3.0456: 14 (58%); 4.3566: 19 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 18, 22.8, 28, 29.4 | 18: 19 (79%); 22.8: 14 (58%); 28: 11 (46%); 29.4: 5 (21%) | 18: 5 (21%); 22.8: 10 (42%); 28: 18 (75%); 29.4: 19 (79%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 20 (83%); 2: 16 (67%); 3: 8 (33%) | 1: 8 (33%); 2: 16 (67%); 3: 22 (92%) | OFFLINE |
| dpi_30d_avg | backtest/signals/congressional_alt_data.py | 100.0% | 0.4338, 0.4899, 0.5263, 0.5767 | 0.4338: 19 (79%); 0.4899: 14 (58%); 0.5263: 10 (42%); 0.5767: 5 (21%) | 0.4338: 5 (21%); 0.4899: 10 (42%); 0.5263: 14 (58%); 0.5767: 19 (79%) | OFFLINE |
| dpi_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3678, 0.529, 0.6113, 0.7323 | 0.3678: 19 (79%); 0.529: 14 (58%); 0.6113: 10 (42%); 0.7323: 5 (21%) | 0.3678: 5 (21%); 0.529: 10 (42%); 0.6113: 14 (58%); 0.7323: 19 (79%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0249, -0.0093, -0.0028, 0.0021 | -0.0249: 19 (79%); -0.0093: 14 (58%); -0.0028: 10 (42%); 0.0021: 5 (21%) | -0.0249: 5 (21%); -0.0093: 10 (42%); -0.0028: 14 (58%); 0.0021: 19 (79%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.7302, 26.4578, 27.088, 27.3712 | 24.7302: 19 (79%); 26.4578: 14 (58%); 27.088: 10 (42%); 27.3712: 5 (21%) | 24.7302: 5 (21%); 26.4578: 10 (42%); 27.088: 14 (58%); 27.3712: 19 (79%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.5654, -0.1258, 0.2748, 0.6194 | -0.5654: 19 (79%); -0.1258: 14 (58%); 0.2748: 10 (42%); 0.6194: 5 (21%) | -0.5654: 5 (21%); -0.1258: 10 (42%); 0.2748: 14 (58%); 0.6194: 19 (79%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.6194, -0.2748, 0.1258, 0.5654 | -0.6194: 19 (79%); -0.2748: 14 (58%); 0.1258: 10 (42%); 0.5654: 5 (21%) | -0.6194: 5 (21%); -0.2748: 10 (42%); 0.1258: 14 (58%); 0.5654: 19 (79%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0592, -0.034, 0.0103, 0.0475 | -0.0592: 19 (79%); -0.034: 14 (58%); 0.0103: 10 (42%); 0.0475: 6 (25%) | -0.0592: 5 (21%); -0.034: 10 (42%); 0.0103: 14 (58%); 0.0475: 20 (83%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.3116, 8.1331, 8.3646, 9.2065 | 7.3116: 19 (79%); 8.1331: 14 (58%); 8.3646: 10 (42%); 9.2065: 5 (21%) | 7.3116: 5 (21%); 8.1331: 10 (42%); 8.3646: 14 (58%); 9.2065: 19 (79%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 24 (100%); 1: 11 (46%) | 0: 13 (54%); 1: 23 (96%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 0.4 | 0: 21 (88%); 0.4: 5 (21%) | 0: 19 (79%); 0.4: 19 (79%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 24 (100%); 1: 7 (29%) | 0: 17 (71%); 1: 22 (92%) | OFFLINE |
| insider_total_shares_bought_30d | backtest/signals/insider_buying.py | 100.0% | 401.4, 3781, 11826.8, 84174.4 | 401.4: 19 (79%); 3781: 14 (58%); 11826.8: 10 (42%); 84174.4: 5 (21%) | 401.4: 5 (21%); 3781: 10 (42%); 11826.8: 14 (58%); 84174.4: 19 (79%) | OFFLINE |
| insider_unique_buyers_30d | backtest/signals/insider_buying.py +1 | 100.0% | 2, 3, 7 | 2: 24 (100%); 3: 11 (46%); 7: 6 (25%) | 2: 13 (54%); 3: 15 (62%); 7: 20 (83%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2.6, 5, 203.6, 270.8 | 2.6: 19 (79%); 5: 15 (62%); 203.6: 10 (42%); 270.8: 5 (21%) | 2.6: 5 (21%); 5: 12 (50%); 203.6: 14 (58%); 270.8: 19 (79%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4.4, 83.4, 119.6 | 1: 20 (83%); 4.4: 14 (58%); 83.4: 10 (42%); 119.6: 5 (21%) | 1: 7 (29%); 4.4: 10 (42%); 83.4: 14 (58%); 119.6: 19 (79%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.1115, 0.1569, 0.5385, 1.0196 | -0.1115: 19 (79%); 0.1569: 14 (58%); 0.5385: 10 (42%); 1.0196: 5 (21%) | -0.1115: 5 (21%); 0.1569: 10 (42%); 0.5385: 14 (58%); 1.0196: 19 (79%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.072, 0.3223, 0.6353, 2.0801 | 0.072: 19 (79%); 0.3223: 14 (58%); 0.6353: 10 (42%); 2.0801: 5 (21%) | 0.072: 5 (21%); 0.3223: 10 (42%); 0.6353: 14 (58%); 2.0801: 19 (79%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -0.4474, -0.0545, 0.4264, 2.0586 | -0.4474: 19 (79%); -0.0545: 14 (58%); 0.4264: 10 (42%); 2.0586: 5 (21%) | -0.4474: 5 (21%); -0.0545: 10 (42%); 0.4264: 14 (58%); 2.0586: 19 (79%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.2324, 0.0922, 0.3666, 1.1024 | -0.2324: 19 (79%); 0.0922: 14 (58%); 0.3666: 10 (42%); 1.1024: 5 (21%) | -0.2324: 5 (21%); 0.0922: 10 (42%); 0.3666: 14 (58%); 1.1024: 19 (79%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.2357, 0.6898, 1.1573, 2.798 | 0.2357: 19 (79%); 0.6898: 14 (58%); 1.1573: 10 (42%); 2.798: 5 (21%) | 0.2357: 5 (21%); 0.6898: 10 (42%); 1.1573: 14 (58%); 2.798: 19 (79%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.0882, 0.3368, 0.716, 1.975 | 0.0882: 19 (79%); 0.3368: 14 (58%); 0.716: 10 (42%); 1.975: 5 (21%) | 0.0882: 5 (21%); 0.3368: 10 (42%); 0.716: 14 (58%); 1.975: 19 (79%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 55.016, 58.428, 60.82, 72.42 | 55.016: 19 (79%); 58.428: 14 (58%); 60.82: 10 (42%); 72.42: 5 (21%) | 55.016: 5 (21%); 58.428: 10 (42%); 60.82: 14 (58%); 72.42: 19 (79%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 100.0% | -0.065, -0.0289, 0.0168, 0.1449 | -0.065: 19 (79%); -0.0289: 14 (58%); 0.0168: 10 (42%); 0.1449: 5 (21%) | -0.065: 5 (21%); -0.0289: 10 (42%); 0.0168: 14 (58%); 0.1449: 19 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0057, 0.0134, 0.0196, 0.0436 | 0.0057: 19 (79%); 0.0134: 14 (58%); 0.0196: 10 (42%); 0.0436: 5 (21%) | 0.0057: 5 (21%); 0.0134: 10 (42%); 0.0196: 14 (58%); 0.0436: 19 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1.2, 3, 6.4 | 0: 24 (100%); 1.2: 14 (58%); 3: 11 (46%); 6.4: 5 (21%) | 0: 7 (29%); 1.2: 10 (42%); 3: 15 (62%); 6.4: 19 (79%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1417 | 0: 24 (100%); 0.1417: 5 (21%) | 0: 16 (67%); 0.1417: 19 (79%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.5, 0.6417 | 0: 24 (100%); 0.5: 11 (46%); 0.6417: 5 (21%) | 0: 12 (50%); 0.5: 17 (71%); 0.6417: 19 (79%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 1.8, 5.4 | 0: 24 (100%); 1: 15 (62%); 1.8: 10 (42%); 5.4: 5 (21%) | 0: 9 (38%); 1: 14 (58%); 1.8: 14 (58%); 5.4: 19 (79%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1.2, 3, 6.4 | 0: 24 (100%); 1.2: 14 (58%); 3: 11 (46%); 6.4: 5 (21%) | 0: 7 (29%); 1.2: 10 (42%); 3: 15 (62%); 6.4: 19 (79%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 3.8 | 0: 24 (100%); 1: 15 (62%); 2: 11 (46%); 3.8: 5 (21%) | 0: 9 (38%); 1: 13 (54%); 2: 17 (71%); 3.8: 19 (79%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0232, 0.2475, 0.3798, 0.7 | 0.0232: 19 (79%); 0.2475: 14 (58%); 0.3798: 10 (42%); 0.7: 5 (21%) | 0.0232: 5 (21%); 0.2475: 10 (42%); 0.3798: 14 (58%); 0.7: 19 (79%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.4709 | 0: 22 (92%); 0.4709: 5 (21%) | 0: 16 (67%); 0.4709: 19 (79%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3138, 0.55 | 0: 20 (83%); 0.3138: 10 (42%); 0.55: 5 (21%) | 0: 13 (54%); 0.3138: 14 (58%); 0.55: 19 (79%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3138, 0.55 | 0: 20 (83%); 0.3138: 10 (42%); 0.55: 5 (21%) | 0: 13 (54%); 0.3138: 14 (58%); 0.55: 19 (79%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0645, 0, 0.0806 | -0.0645: 19 (79%); 0: 18 (75%); 0.0806: 5 (21%) | -0.0645: 5 (21%); 0: 18 (75%); 0.0806: 19 (79%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.8679, -0.4789, -0.0781, 0.3965 | -0.8679: 19 (79%); -0.4789: 14 (58%); -0.0781: 10 (42%); 0.3965: 5 (21%) | -0.8679: 5 (21%); -0.4789: 10 (42%); -0.0781: 14 (58%); 0.3965: 19 (79%) | OFFLINE |
| otc_short_ratio_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3678, 0.529, 0.6113, 0.7323 | 0.3678: 19 (79%); 0.529: 14 (58%); 0.6113: 10 (42%); 0.7323: 5 (21%) | 0.3678: 5 (21%); 0.529: 10 (42%); 0.6113: 14 (58%); 0.7323: 19 (79%) | OFFLINE |
| otc_volume_recent | backtest/signals/congressional_alt_data.py | 100.0% | 592109.4, 1464757.4, 2288049, 4299517.6 | 592109.4: 19 (79%); 1464757.4: 14 (58%); 2288049: 10 (42%); 4299517.6: 5 (21%) | 592109.4: 5 (21%); 1464757.4: 10 (42%); 2288049: 14 (58%); 4299517.6: 19 (79%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 3, 5.2, 7, 10.4 | 3: 21 (88%); 5.2: 14 (58%); 7: 11 (46%); 10.4: 5 (21%) | 3: 6 (25%); 5.2: 10 (42%); 7: 17 (71%); 10.4: 19 (79%) | OFFLINE |
| pair_half_life | backtest/signals/pairs_trading.py +1 | 100.0% | 7.464, 9.52, 10.534, 12.486 | 7.464: 19 (79%); 9.52: 14 (58%); 10.534: 10 (42%); 12.486: 5 (21%) | 7.464: 5 (21%); 9.52: 10 (42%); 10.534: 14 (58%); 12.486: 19 (79%) | OFFLINE |
| pair_max_abs_zscore | backtest/signals/pairs_trading.py | 100.0% | 1.071, 1.6431, 1.7958, 1.9626 | 1.071: 19 (79%); 1.6431: 14 (58%); 1.7958: 10 (42%); 1.9626: 5 (21%) | 1.071: 5 (21%); 1.6431: 10 (42%); 1.7958: 14 (58%); 1.9626: 19 (79%) | OFFLINE |
| pair_zscore_signed | backtest/signals/pairs_trading.py +1 | 100.0% | -1.3851, 0.7669, 1.6073, 1.8085 | -1.3851: 19 (79%); 0.7669: 14 (58%); 1.6073: 10 (42%); 1.8085: 5 (21%) | -1.3851: 5 (21%); 0.7669: 10 (42%); 1.6073: 14 (58%); 1.8085: 19 (79%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0132, 0.0341, 0.054, 0.0962 | 0.0132: 19 (79%); 0.0341: 14 (58%); 0.054: 10 (42%); 0.0962: 5 (21%) | 0.0132: 5 (21%); 0.0341: 10 (42%); 0.054: 14 (58%); 0.0962: 19 (79%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0464, 0.0588, 0.1046, 0.1724 | 0.0464: 19 (79%); 0.0588: 14 (58%); 0.1046: 10 (42%); 0.1724: 5 (21%) | 0.0464: 5 (21%); 0.0588: 10 (42%); 0.1046: 14 (58%); 0.1724: 19 (79%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0165, 0.014, 0.0432, 0.079 | -0.0165: 19 (79%); 0.014: 14 (58%); 0.0432: 10 (42%); 0.079: 5 (21%) | -0.0165: 5 (21%); 0.014: 10 (42%); 0.0432: 14 (58%); 0.079: 19 (79%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 2.3272, 4.0916, 4.7542, 7.3626 | 2.3272: 19 (79%); 4.0916: 14 (58%); 4.7542: 10 (42%); 7.3626: 5 (21%) | 2.3272: 5 (21%); 4.0916: 10 (42%); 4.7542: 14 (58%); 7.3626: 19 (79%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 100.0% | 1.8718, 4.8082, 7.5868, 12.4496 | 1.8718: 19 (79%); 4.8082: 14 (58%); 7.5868: 10 (42%); 12.4496: 5 (21%) | 1.8718: 5 (21%); 4.8082: 10 (42%); 7.5868: 14 (58%); 12.4496: 19 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 3.7408, 4.6788, 6.7004, 11.6536 | 3.7408: 19 (79%); 4.6788: 14 (58%); 6.7004: 10 (42%); 11.6536: 5 (21%) | 3.7408: 5 (21%); 4.6788: 10 (42%); 6.7004: 14 (58%); 11.6536: 19 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -6.3916, 2.9526, 13.0974, 25.1796 | -6.3916: 19 (79%); 2.9526: 14 (58%); 13.0974: 10 (42%); 25.1796: 5 (21%) | -6.3916: 5 (21%); 2.9526: 10 (42%); 13.0974: 14 (58%); 25.1796: 19 (79%) | OFFLINE |
| persistent_holders_4q | backtest/signals/institutional_persistence_consumer.py +1 | 100.0% | 7, 9.6, 16.6, 502.8 | 7: 21 (88%); 9.6: 14 (58%); 16.6: 10 (42%); 502.8: 5 (21%) | 7: 6 (25%); 9.6: 10 (42%); 16.6: 14 (58%); 502.8: 19 (79%) | OFFLINE |
| persistent_holders_8q | backtest/signals/institutional_persistence_consumer.py | 100.0% | 5, 6, 7, 114.4 | 5: 20 (83%); 6: 16 (67%); 7: 12 (50%); 114.4: 5 (21%) | 5: 8 (33%); 6: 12 (50%); 7: 15 (62%); 114.4: 19 (79%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0406, 0.0499, 0.0782, 0.123 | 0.0406: 19 (79%); 0.0499: 14 (58%); 0.0782: 10 (42%); 0.123: 5 (21%) | 0.0406: 5 (21%); 0.0499: 10 (42%); 0.0782: 14 (58%); 0.123: 19 (79%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.4968, 0.7353, 0.8438, 0.9037 | 0.4968: 19 (79%); 0.7353: 14 (58%); 0.8438: 10 (42%); 0.9037: 5 (21%) | 0.4968: 5 (21%); 0.7353: 10 (42%); 0.8438: 14 (58%); 0.9037: 19 (79%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 0.0948, 0.5969, 1.3882, 1.9617 | 0.0948: 19 (79%); 0.5969: 14 (58%); 1.3882: 10 (42%); 1.9617: 5 (21%) | 0.0948: 5 (21%); 0.5969: 10 (42%); 1.3882: 14 (58%); 1.9617: 19 (79%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.2107, 0.4646, 0.6362, 1.3937 | -0.2107: 19 (79%); 0.4646: 14 (58%); 0.6362: 10 (42%); 1.3937: 5 (21%) | -0.2107: 5 (21%); 0.4646: 10 (42%); 0.6362: 14 (58%); 1.3937: 19 (79%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -0.6188, -0.0512, 1.0385, 1.9011 | -0.6188: 19 (79%); -0.0512: 14 (58%); 1.0385: 10 (42%); 1.9011: 5 (21%) | -0.6188: 5 (21%); -0.0512: 10 (42%); 1.0385: 14 (58%); 1.9011: 19 (79%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -0.0484, 3, 5.5938, 10.1052 | -0.0484: 19 (79%); 3: 14 (58%); 5.5938: 10 (42%); 10.1052: 5 (21%) | -0.0484: 5 (21%); 3: 10 (42%); 5.5938: 14 (58%); 10.1052: 19 (79%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 52.738, 59.92, 63.62, 66.16 | 52.738: 19 (79%); 59.92: 14 (58%); 63.62: 10 (42%); 66.16: 5 (21%) | 52.738: 5 (21%); 59.92: 10 (42%); 63.62: 14 (58%); 66.16: 19 (79%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 60.468, 79.846, 92.8, 96.44 | 60.468: 19 (79%); 79.846: 14 (58%); 92.8: 10 (42%); 96.44: 5 (21%) | 60.468: 5 (21%); 79.846: 10 (42%); 92.8: 14 (58%); 96.44: 19 (79%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 53.3, 56.126, 59.228, 61.236 | 53.3: 20 (83%); 56.126: 14 (58%); 59.228: 10 (42%); 61.236: 5 (21%) | 53.3: 6 (25%); 56.126: 10 (42%); 59.228: 14 (58%); 61.236: 19 (79%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 54.962, 63.614, 69.604, 72.968 | 54.962: 19 (79%); 63.614: 14 (58%); 69.604: 10 (42%); 72.968: 5 (21%) | 54.962: 5 (21%); 63.614: 10 (42%); 69.604: 14 (58%); 72.968: 19 (79%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0294, 0.0366, 0.0519, 0.066 | 0.0294: 19 (79%); 0.0366: 14 (58%); 0.0519: 10 (42%); 0.066: 5 (21%) | 0.0294: 5 (21%); 0.0366: 10 (42%); 0.0519: 14 (58%); 0.066: 19 (79%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0656, -0.0568, -0.0474, -0.0296 | -0.0656: 19 (79%); -0.0568: 14 (58%); -0.0474: 10 (42%); -0.0296: 5 (21%) | -0.0656: 5 (21%); -0.0568: 10 (42%); -0.0474: 14 (58%); -0.0296: 19 (79%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 24 (100%); 1: 6 (25%) | 0: 18 (75%); 1: 20 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 31.8, 55, 66.6, 76.4 | 31.8: 19 (79%); 55: 14 (58%); 66.6: 10 (42%); 76.4: 5 (21%) | 31.8: 5 (21%); 55: 10 (42%); 66.6: 14 (58%); 76.4: 19 (79%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 100.0% | 0.0162, 0.018, 0.0295, 0.0576 | 0.0162: 19 (79%); 0.018: 14 (58%); 0.0295: 10 (42%); 0.0576: 5 (21%) | 0.0162: 5 (21%); 0.018: 10 (42%); 0.0295: 14 (58%); 0.0576: 19 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.5432, 0.6767, 0.7596, 0.915 | 0.5432: 19 (79%); 0.6767: 14 (58%); 0.7596: 10 (42%); 0.915: 5 (21%) | 0.5432: 5 (21%); 0.6767: 10 (42%); 0.7596: 14 (58%); 0.915: 19 (79%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 43.68, 56.12, 74.26, 110.08 | 43.68: 19 (79%); 56.12: 14 (58%); 74.26: 10 (42%); 110.08: 5 (21%) | 43.68: 5 (21%); 56.12: 10 (42%); 74.26: 14 (58%); 110.08: 19 (79%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 0.9095, 2.3405, 3.686, 8.508 | 0.9095: 19 (79%); 2.3405: 14 (58%); 3.686: 10 (42%); 8.508: 5 (21%) | 0.9095: 5 (21%); 2.3405: 10 (42%); 3.686: 14 (58%); 8.508: 19 (79%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 70.178, 76.774, 83.754, 86.11 | 70.178: 19 (79%); 76.774: 14 (58%); 83.754: 10 (42%); 86.11: 5 (21%) | 70.178: 5 (21%); 76.774: 10 (42%); 83.754: 14 (58%); 86.11: 19 (79%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 69.34, 79.502, 86.71, 92.836 | 69.34: 19 (79%); 79.502: 14 (58%); 86.71: 10 (42%); 92.836: 5 (21%) | 69.34: 5 (21%); 79.502: 10 (42%); 86.71: 14 (58%); 92.836: 19 (79%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 15.648, 70.314, 94.506, 97.864 | 15.648: 19 (79%); 70.314: 14 (58%); 94.506: 10 (42%); 97.864: 5 (21%) | 15.648: 5 (21%); 70.314: 10 (42%); 94.506: 14 (58%); 97.864: 19 (79%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 21.94, 51.906, 99.234, 100 | 21.94: 19 (79%); 51.906: 14 (58%); 99.234: 10 (42%); 100: 10 (42%) | 21.94: 5 (21%); 51.906: 10 (42%); 99.234: 14 (58%); 100: 24 (100%) | OFFLINE |
| total_active_holders | backtest/signals/institutional_persistence_consumer.py +1 | 100.0% | 11, 17.4, 574, 803 | 11: 20 (83%); 17.4: 14 (58%); 574: 10 (42%); 803: 6 (25%) | 11: 6 (25%); 17.4: 10 (42%); 574: 14 (58%); 803: 20 (83%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 2.6, 6.2, 12, 13.4 | 2.6: 19 (79%); 6.2: 14 (58%); 12: 11 (46%); 13.4: 5 (21%) | 2.6: 5 (21%); 6.2: 10 (42%); 12: 16 (67%); 13.4: 19 (79%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 7.6, 10, 14.8, 18.4 | 7.6: 19 (79%); 10: 15 (62%); 14.8: 10 (42%); 18.4: 5 (21%) | 7.6: 5 (21%); 10: 11 (46%); 14.8: 14 (58%); 18.4: 19 (79%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 50.74, 56.936, 60.298, 64.25 | 50.74: 19 (79%); 56.936: 14 (58%); 60.298: 10 (42%); 64.25: 5 (21%) | 50.74: 5 (21%); 56.936: 10 (42%); 60.298: 14 (58%); 64.25: 19 (79%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0484, 0.3389, 0.6135, 0.8349 | 0.0484: 19 (79%); 0.3389: 14 (58%); 0.6135: 10 (42%); 0.8349: 5 (21%) | 0.0484: 5 (21%); 0.3389: 10 (42%); 0.6135: 14 (58%); 0.8349: 19 (79%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.49, 18.864, 19.594, 21.818 | 15.49: 19 (79%); 18.864: 14 (58%); 19.594: 10 (42%); 21.818: 5 (21%) | 15.49: 5 (21%); 18.864: 10 (42%); 19.594: 14 (58%); 21.818: 19 (79%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.49, 18.864, 19.594, 21.818 | 15.49: 19 (79%); 18.864: 14 (58%); 19.594: 10 (42%); 21.818: 5 (21%) | 15.49: 5 (21%); 18.864: 10 (42%); 19.594: 14 (58%); 21.818: 19 (79%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8613, 0.8885, 0.9157, 0.9698 | 0.8613: 19 (79%); 0.8885: 14 (58%); 0.9157: 10 (42%); 0.9698: 5 (21%) | 0.8613: 5 (21%); 0.8885: 10 (42%); 0.9157: 14 (58%); 0.9698: 19 (79%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.64, 0.774, 0.99, 1.296 | 0.64: 21 (88%); 0.774: 14 (58%); 0.99: 10 (42%); 1.296: 5 (21%) | 0.64: 6 (25%); 0.774: 10 (42%); 0.99: 14 (58%); 1.296: 19 (79%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0344, 0.0502, 0.0782, 0.1331 | 0.0344: 19 (79%); 0.0502: 14 (58%); 0.0782: 10 (42%); 0.1331: 5 (21%) | 0.0344: 5 (21%); 0.0502: 10 (42%); 0.0782: 14 (58%); 0.1331: 19 (79%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 35.6714, 62.0885, 83.905, 146.6797 | 35.6714: 19 (79%); 62.0885: 14 (58%); 83.905: 10 (42%); 146.6797: 5 (21%) | 35.6714: 5 (21%); 62.0885: 10 (42%); 83.905: 14 (58%); 146.6797: 19 (79%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 24 (100%) | 0: 22 (92%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 24 (100%) | 0: 22 (92%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0251, 0.0587, 0.075, 0.1301 | 0.0251: 19 (79%); 0.0587: 14 (58%); 0.075: 10 (42%); 0.1301: 5 (21%) | 0.0251: 5 (21%); 0.0587: 10 (42%); 0.075: 14 (58%); 0.1301: 19 (79%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -32.212, -19.236, -9.384, -4.144 | -32.212: 19 (79%); -19.236: 14 (58%); -9.384: 10 (42%); -4.144: 5 (21%) | -32.212: 5 (21%); -19.236: 10 (42%); -9.384: 14 (58%); -4.144: 19 (79%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.5746, 0.7709, 1.0161, 1.2484 | 0.5746: 19 (79%); 0.7709: 14 (58%); 1.0161: 10 (42%); 1.2484: 5 (21%) | 0.5746: 5 (21%); 0.7709: 10 (42%); 1.0161: 14 (58%); 1.2484: 19 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 4, 6, 9 | 4: 20 (83%); 6: 15 (62%); 9: 8 (33%) | 4: 6 (25%); 6: 15 (62%); 9: 22 (92%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.1891, 0.2352, 0.3093, 0.3659 | 0.1891: 19 (79%); 0.2352: 14 (58%); 0.3093: 10 (42%); 0.3659: 5 (21%) | 0.1891: 5 (21%); 0.2352: 10 (42%); 0.3093: 14 (58%); 0.3659: 19 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 3, 4, 7, 9 | 3: 21 (88%); 4: 15 (62%); 7: 11 (46%); 9: 6 (25%) | 3: 9 (38%); 4: 11 (46%); 7: 16 (67%); 9: 22 (92%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0334, 0.0447, 0.0565, 0.0676 | 0.0334: 19 (79%); 0.0447: 14 (58%); 0.0565: 10 (42%); 0.0676: 5 (21%) | 0.0334: 5 (21%); 0.0447: 10 (42%); 0.0565: 14 (58%); 0.0676: 19 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 4.6, 7, 8.8, 9.4 | 4.6: 19 (79%); 7: 15 (62%); 8.8: 10 (42%); 9.4: 5 (21%) | 4.6: 5 (21%); 7: 12 (50%); 8.8: 14 (58%); 9.4: 19 (79%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.1711, -0.0489, 0.0481, 0.1007 | -0.1711: 19 (79%); -0.0489: 14 (58%); 0.0481: 10 (42%); 0.1007: 5 (21%) | -0.1711: 5 (21%); -0.0489: 10 (42%); 0.0481: 14 (58%); 0.1007: 19 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 2.6, 5, 6, 7 | 2.6: 19 (79%); 5: 16 (67%); 6: 12 (50%); 7: 8 (33%) | 2.6: 5 (21%); 5: 12 (50%); 6: 16 (67%); 7: 20 (83%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.2% |
| 8k_item_5_02_filed_within_7d | 8.3% |
| above_avwap_20high | 75.0% |
| above_avwap_20low | 91.7% |
| above_avwap_252low | 87.5% |
| above_cam_r3 | 58.3% |
| above_cam_r4 | 45.8% |
| above_cpr | 87.5% |
| above_pivot | 83.3% |
| above_prev_high | 58.3% |
| above_prev_high_clearance_atr_05 | 33.3% |
| above_prev_low | 91.7% |
| above_r1 | 45.8% |
| above_r2 | 33.3% |
| above_vwap | 62.5% |
| above_wood_p | 91.7% |
| ad_rising | 62.5% |
| adx_di_bear | 16.7% |
| adx_di_bull | 83.3% |
| adx_strong | 8.3% |
| adx_trending | 33.3% |
| ao_cross_dn | 4.2% |
| ao_cross_up | 12.5% |
| ao_positive | 87.5% |
| at_key_fib | 16.7% |
| at_key_fib_wide | 41.7% |
| avwap_20high_reclaim_recent_3d | 41.7% |
| avwap_20low_loss_recent_3d | 4.2% |
| avwap_20low_reclaim_recent_3d | 12.5% |
| avwap_252low_loss_recent_3d | 4.2% |
| avwap_252low_reclaim_recent_3d | 20.8% |
| avwap_50low_reclaim_recent_3d | 12.5% |
| bb_10_20_above_mid | 75.0% |
| bb_10_20_expanding | 75.0% |
| bb_10_20_pctb_gt_75 | 66.7% |
| bb_10_20_pctb_gt_8 | 54.2% |
| bb_10_20_pctb_gt_85 | 50.0% |
| bb_10_20_pctb_gt_9 | 45.8% |
| bb_10_20_pctb_gt_95 | 29.2% |
| bb_10_20_pctb_lt_2 | 4.2% |
| bb_10_20_pctb_lt_25 | 8.3% |
| bb_10_20_reclaim_from_lower_recent_3d | 8.3% |
| bb_10_20_reclaim_from_upper_recent_3d | 20.8% |
| bb_10_20_squeeze | 50.0% |
| bb_10_20_touch_upper | 29.2% |
| bb_20_15_above_mid | 83.3% |
| bb_20_15_expanding | 54.2% |
| bb_20_15_pctb_gt_75 | 75.0% |
| bb_20_15_pctb_gt_8 | 70.8% |
| bb_20_15_pctb_gt_85 | 62.5% |
| bb_20_15_pctb_gt_9 | 62.5% |
| bb_20_15_pctb_gt_95 | 50.0% |
| bb_20_15_reclaim_from_lower_recent_3d | 8.3% |
| bb_20_15_reclaim_from_upper_recent_3d | 12.5% |
| bb_20_15_squeeze | 41.7% |
| bb_20_15_touch_upper | 62.5% |
| bb_20_20_above_mid | 83.3% |
| bb_20_20_expanding | 54.2% |
| bb_20_20_pctb_gt_75 | 66.7% |
| bb_20_20_pctb_gt_8 | 62.5% |
| bb_20_20_pctb_gt_85 | 50.0% |
| bb_20_20_pctb_gt_9 | 45.8% |
| bb_20_20_pctb_gt_95 | 41.7% |
| bb_20_20_reclaim_from_lower_recent_3d | 4.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 8.3% |
| bb_20_20_squeeze | 16.7% |
| bb_20_20_touch_upper | 41.7% |
| bearish_pin_bar | 4.2% |
| below_avwap_20high | 25.0% |
| below_avwap_20low | 8.3% |
| below_avwap_252low | 12.5% |
| below_cam_s3 | 4.2% |
| below_cpr | 16.7% |
| below_ema_20 | 4.2% |
| below_ema_20_break_recent_5d | 4.2% |
| below_ema_50 | 4.2% |
| below_ema_9 | 12.5% |
| below_ema_9_break_recent_5d | 12.5% |
| below_prev_high | 41.7% |
| below_prev_low | 8.3% |
| below_sma_20 | 16.7% |
| below_sma_200 | 29.2% |
| below_sma_21 | 16.7% |
| below_sma_50 | 16.7% |
| below_sma_9 | 25.0% |
| below_vwap | 37.5% |
| bullish_engulfing | 16.7% |
| bullish_pin_bar | 12.5% |
| ceo_buy | 45.8% |
| cfo_buy | 29.2% |
| chandelier_long_bullish | 91.7% |
| chandelier_short_bearish | 16.7% |
| chandelier_short_flip_up | 4.2% |
| close_in_bottom_40pct_of_range | 12.5% |
| close_in_top_40pct_of_range | 70.8% |
| cluster_buy | 41.7% |
| cmf_cross_dn | 4.2% |
| cmf_cross_up | 16.7% |
| cmf_negative | 20.8% |
| cmf_positive | 79.2% |
| concentrated_sell | 12.5% |
| cpr_narrow | 79.2% |
| cpr_narrow_tight | 33.3% |
| cup_handle_detected | 16.7% |
| cup_handle_neckline_break_retest_long | 20.8% |
| dc10_breakout_up | 50.0% |
| dc10_breakout_up_1pct | 54.2% |
| dc10_new_high | 54.2% |
| dc10_strong_breakout_up | 20.8% |
| dc20_breakout_up | 45.8% |
| dc20_new_high | 50.0% |
| dc20_resistance_break_retest_strong | 29.2% |
| defensive_leadership | 37.5% |
| director_only_buy | 58.3% |
| doji | 4.2% |
| double_bottom_detected | 8.3% |
| double_top_detected | 4.2% |
| dpi_elevated | 62.5% |
| drying_volume_on_up_turn | 62.5% |
| ema_20_50_bearish | 50.0% |
| ema_20_50_bullish | 50.0% |
| ema_50_200_bearish | 58.3% |
| ema_50_200_bullish | 41.7% |
| ema_50_200_golden_cross | 4.2% |
| ema_9_21_bearish | 12.5% |
| ema_9_21_bullish | 87.5% |
| ema_9_21_golden_cross | 4.2% |
| force_index_cross_up | 8.3% |
| force_index_positive | 95.8% |
| gap_up_1_5pct | 8.3% |
| gap_up_2pct | 4.2% |
| head_shoulders_top_detected | 4.2% |
| htf_aligned_bull | 41.7% |
| htf_disagreement | 12.5% |
| hull_bearish | 29.2% |
| hull_bullish | 70.8% |
| hull_flip_dn | 4.2% |
| ichi_above_cloud | 70.8% |
| ichi_above_cloud_break_recent_5d | 41.7% |
| ichi_below_cloud | 25.0% |
| ichi_below_cloud_break_recent_5d | 4.2% |
| ichi_cloud_thick | 87.5% |
| ichi_tk_bearish | 16.7% |
| ichi_tk_bullish | 62.5% |
| ichi_weekly_above_cloud | 50.0% |
| ichi_weekly_below_cloud | 25.0% |
| ichi_weekly_in_cloud | 25.0% |
| in_reversal_window | 50.0% |
| inside_bar | 12.5% |
| inside_kc | 75.0% |
| institutional_buy | 91.7% |
| institutional_negative | 8.3% |
| institutional_persistence_growing | 58.3% |
| institutional_persistence_strong | 58.3% |
| institutional_strong_buy | 83.3% |
| inverted_cup_handle_detected | 12.5% |
| is_friday | 8.3% |
| is_halloween_period | 75.0% |
| is_january | 4.2% |
| is_january_extended | 8.3% |
| is_monday | 16.7% |
| is_pre_holiday | 4.2% |
| is_summer_period | 25.0% |
| is_totm_window | 41.7% |
| is_totm_window_first_day | 8.3% |
| is_week_open | 16.7% |
| kc_touch_upper | 29.2% |
| large_dollar_buy | 37.5% |
| macd_12_26_9_bearish | 25.0% |
| macd_12_26_9_bullish | 75.0% |
| macd_12_26_9_crossover_up | 4.2% |
| macd_8_21_5_bearish | 25.0% |
| macd_8_21_5_bullish | 75.0% |
| marubozu_bull | 8.3% |
| mfi_broad_overbought | 25.0% |
| mfi_overbought | 8.3% |
| monthly_above_sma_12 | 62.5% |
| monthly_above_sma_6 | 66.7% |
| monthly_bias_bear | 16.7% |
| monthly_bias_bull | 45.8% |
| monthly_momentum_pos | 50.0% |
| morning_star | 4.2% |
| near_52w_high | 4.2% |
| near_52w_high_95pct | 12.5% |
| near_avwap_20high_atr_05x | 50.0% |
| near_avwap_20high_atr_10x | 75.0% |
| near_avwap_20high_atr_15x | 91.7% |
| near_avwap_20high_atr_20x | 91.7% |
| near_avwap_20low_atr_05x | 4.2% |
| near_avwap_20low_atr_10x | 16.7% |
| near_avwap_20low_atr_15x | 37.5% |
| near_avwap_20low_atr_20x | 62.5% |
| near_avwap_252low_atr_05x | 12.5% |
| near_avwap_252low_atr_10x | 25.0% |
| near_avwap_252low_atr_15x | 33.3% |
| near_avwap_252low_atr_20x | 37.5% |
| near_avwap_50low_atr_10x | 12.5% |
| near_avwap_50low_atr_15x | 20.8% |
| near_avwap_50low_atr_20x | 37.5% |
| near_cam_r3 | 25.0% |
| near_cam_s3 | 12.5% |
| near_fib_236 | 12.5% |
| near_fib_382 | 8.3% |
| near_fib_618 | 8.3% |
| near_pivot | 16.7% |
| near_prev_close | 20.8% |
| near_prev_high | 16.7% |
| near_prev_low | 8.3% |
| near_r1 | 16.7% |
| near_r1_wide | 58.3% |
| near_r2 | 8.3% |
| near_r2_wide | 58.3% |
| near_s1 | 4.2% |
| near_s1_wide | 25.0% |
| near_s2_wide | 16.7% |
| near_wood_r1 | 12.5% |
| news_uses_polygon_score | 25.0% |
| obv_bearish | 20.8% |
| obv_bullish | 79.2% |
| obv_diverge_bull | 4.2% |
| obv_falling | 29.2% |
| obv_rising | 70.8% |
| outside_bar | 12.5% |
| pead_negative_surprise | 17.4% |
| pead_positive_surprise | 17.4% |
| pin_bar | 16.7% |
| po3_accumulation_active | 41.7% |
| po3_bullish | 16.7% |
| po3_manipulation_sweep_down | 4.2% |
| po3_manipulation_sweep_up | 20.8% |
| po3_sweep_above_prior_high | 70.8% |
| po3_sweep_below_prior_low | 29.2% |
| ppo_bullish | 75.0% |
| ppo_crossover_up | 4.2% |
| pre_fomc_d0 | 4.2% |
| pre_fomc_window | 4.2% |
| price_above_dema | 75.0% |
| price_above_ema_20 | 95.8% |
| price_above_ema_200_break_recent_5d | 54.2% |
| price_above_ema_20_break_recent_5d | 50.0% |
| price_above_ema_21_break_recent_5d | 50.0% |
| price_above_ema_50 | 95.8% |
| price_above_ema_50_break_recent_5d | 54.2% |
| price_above_ema_9 | 87.5% |
| price_above_ema_9_break_recent_5d | 45.8% |
| price_above_hull | 75.0% |
| price_above_sma_200 | 70.8% |
| price_above_sma_21 | 83.3% |
| price_above_sma_50 | 83.3% |
| price_above_tema | 66.7% |
| price_below_dema | 25.0% |
| price_below_hull | 25.0% |
| price_below_tema | 33.3% |
| psar_bullish | 75.0% |
| r1_break_retest_long | 83.3% |
| resistance_break_retest | 45.8% |
| risk_off_regime_bond_signal | 25.0% |
| risk_off_regime_bond_signal_strong | 4.2% |
| risk_off_regime_gold_signal | 37.5% |
| risk_on_regime_bond_signal | 37.5% |
| risk_on_regime_bond_signal_strong | 8.3% |
| roc_positive | 79.2% |
| roc_turning_dn | 8.3% |
| rsi_14_cross_dn_overbought_recent_3d | 4.2% |
| rsi_14_overbought | 8.3% |
| rsi_14_rising | 83.3% |
| rsi_21_bullish | 95.8% |
| rsi_21_overbought | 4.2% |
| rsi_21_rising | 83.3% |
| rsi_2_bullish | 83.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 12.5% |
| rsi_2_cross_dn_overbought_recent_3d | 12.5% |
| rsi_2_cross_up_extreme_os_recent_3d | 29.2% |
| rsi_2_cross_up_oversold_recent_3d | 33.3% |
| rsi_2_extreme_ob | 58.3% |
| rsi_2_extreme_os | 4.2% |
| rsi_2_overbought | 70.8% |
| rsi_2_oversold | 8.3% |
| rsi_2_rising | 83.3% |
| rsi_9_bullish | 91.7% |
| rsi_9_cross_dn_overbought_recent_3d | 8.3% |
| rsi_9_cross_up_oversold_recent_3d | 8.3% |
| rsi_9_extreme_ob | 8.3% |
| rsi_9_overbought | 37.5% |
| rsi_9_rising | 83.3% |
| s1_break_retest_short | 20.8% |
| shooting_star | 4.2% |
| sma_20_50_bullish | 45.8% |
| sma_20_50_golden_cross | 4.2% |
| sma_50_200_bullish | 50.0% |
| sma_9_21_bullish | 87.5% |
| sma_9_21_golden_cross | 8.3% |
| smc_bos_bearish | 12.5% |
| smc_bos_bullish | 16.7% |
| smc_bos_retest_long | 8.3% |
| smc_bos_retest_short | 12.5% |
| smc_breaker_block_bearish | 12.5% |
| smc_breaker_block_bullish | 37.5% |
| smc_choch_bearish | 8.3% |
| smc_equal_highs_swept | 8.3% |
| smc_equal_lows_swept | 4.2% |
| smc_fvg_bearish_active | 20.8% |
| smc_fvg_bullish_active | 54.2% |
| smc_fvg_retest_short_zone | 8.3% |
| smc_in_discount_zone | 25.0% |
| smc_in_premium_zone | 91.7% |
| smc_inverse_fvg_bearish | 66.7% |
| smc_liquidity_swept_up | 4.2% |
| smc_mitigation_block_short | 4.2% |
| smc_ob_bearish_active | 37.5% |
| smc_ob_bullish_active | 41.7% |
| smc_ote_long_zone | 8.3% |
| smc_ote_short_zone | 8.3% |
| squeeze_fire_up | 8.3% |
| squeeze_in | 12.5% |
| squeeze_positive | 95.8% |
| stoch_bearish_cross | 4.2% |
| stoch_broad_overbought | 66.7% |
| stoch_broad_oversold | 4.2% |
| stoch_bullish_cross | 12.5% |
| stoch_overbought | 54.2% |
| stoch_oversold | 4.2% |
| stochrsi_cross_dn | 16.7% |
| stochrsi_cross_up | 16.7% |
| stochrsi_overbought | 54.2% |
| stochrsi_oversold | 20.8% |
| supertrend_flip_recent_long_5d | 8.3% |
| supertrend_flip_recent_short_5d | 8.3% |
| supertrend_flip_up | 4.2% |
| tema_above_dema | 83.3% |
| three_white_soldiers | 25.0% |
| triangle_apex_break_retest_long | 8.3% |
| triangle_ascending_detected | 4.2% |
| triangle_descending_detected | 8.3% |
| uo_overbought | 8.3% |
| usd_strengthening | 8.3% |
| usd_weakening | 25.0% |
| vix_band_high | 37.5% |
| vix_band_low | 37.5% |
| vix_band_mid | 25.0% |
| vix_term_backwardation | 12.5% |
| vix_term_contango | 87.5% |
| vol_above_avg | 37.5% |
| vol_below_avg | 62.5% |
| vol_spike_12x | 29.2% |
| vol_spike_15x | 12.5% |
| vol_spike_17x | 8.3% |
| vol_spike_2x | 4.2% |
| vol_spike_2x_on_up_day_recent_3d | 4.2% |
| vp_above_value_area | 50.0% |
| vp_close_above_poc | 87.5% |
| vp_close_below_poc | 12.5% |
| vp_in_value_area | 50.0% |
| week_open_gap_up_15pct | 4.2% |
| weekly_above_ema_10 | 91.7% |
| weekly_above_ema_20 | 87.5% |
| weekly_bias_bear | 4.2% |
| weekly_bias_bull | 83.3% |
| weekly_momentum_pos | 91.7% |
| williams_r_overbought | 62.5% |
| williams_r_oversold | 8.3% |
| williams_r_rising | 66.7% |
| within_pead_window | 45.8% |
| xs_avoid_high_ivol | 75.0% |
| xs_avoid_high_max | 58.3% |
| xs_high_beta_decile | 33.3% |
| xs_low_beta_bottom_quintile | 33.3% |
| xs_low_beta_decile | 12.5% |
| xs_low_beta_top_quintile | 12.5% |
| xs_momentum_bottom_decile | 12.5% |
| xs_momentum_bottom_quintile | 20.8% |
| xs_momentum_top_decile | 4.2% |
| xs_momentum_top_quintile | 8.3% |
| xs_quality_bottom_quintile | 18.2% |
| xs_quality_top_tercile | 45.5% |
| yoy_surprise_high | 43.5% |
| yoy_surprise_negative | 52.2% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| cot_rut_commercials_pctile_3y | 66.7% |
| cot_rut_mmoney_pctile_3y | 66.7% |
| cup_handle_breakout_level | 25.0% |
| cup_handle_depth_pct | 25.0% |
| days_to_next_holiday | 70.8% |
| earnings_announcement_return | 95.8% |
| earnings_eps_yoy_growth | 95.8% |
| gov_contracts_4q_sum | 33.3% |
| gov_contracts_last_qtr_amount | 33.3% |
| gov_contracts_qoq_growth | 33.3% |
| inverted_cup_handle_height_pct | 20.8% |
| lobbying_amount_1y | 66.7% |
| lobbying_amount_q | 66.7% |
| lobbying_amount_yoy | 66.7% |
| pct_from_avwap_20high | 50.0% |
| search_volume_index_recent | 83.3% |
| search_volume_observations | 83.3% |
| search_volume_zscore_30d | 83.3% |
| xs_quality_decile | 45.8% |
| xs_quality_gross_profitability | 45.8% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.988), `avwap_20low` (0.998), `avwap_252low` (0.972), `avwap_50low` (0.991), `bb_10_20_lower` (0.999), `bb_10_20_mid` (0.998), `bb_10_20_upper` (0.991), `bb_20_15_lower` (0.997), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.997), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.995), `cam_r1` (0.991), `cam_r2` (0.991), `cam_r3` (0.991), `cam_r4` (0.988), `cam_s1` (0.991), `cam_s2` (0.991), `cam_s3` (0.991), `cam_s4` (0.991), `chandelier_long_value` (0.993), `chandelier_short_value` (0.991), `cpr_bottom` (0.994), `cpr_top` (0.994), `cup_handle_rim` (1.0), `days_since_inclusion` (1.0), `days_to_rebalance` (-1.0), `dc10_lower` (0.991), `dc10_mid` (0.997), `dc10_upper` (0.991), `dc20_lower` (0.993), `dc20_mid` (0.993), `dc20_upper` (0.99), `dema` (0.997), `double_bottom_neckline` (1.0), `double_bottom_trough` (1.0), `entry_stop_long` (0.988), `entry_stop_short` (0.988), `fib_236` (0.988), `fib_382` (0.99), `fib_500` (0.989), `fib_618` (0.989), `fib_786` (0.984), `fib_ext_127` (0.986), `fib_ext_162` (0.988), `hull_ma` (0.997), `ichi_kijun` (0.99), `ichi_senkou_a` (0.981), `ichi_senkou_b` (0.976), `ichi_tenkan` (0.997), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_rim_low` (1.0), `kc_lower` (0.998), `kc_mid` (0.997), `kc_upper` (0.998), `monthly_close` (0.99), `monthly_sma_12` (0.975), `monthly_sma_6` (0.979), `pivot` (0.994), `prev_close` (0.991), `prev_high` (0.995), `prev_low` (0.996), `psar_value` (0.999), `r1` (0.992), `r2` (0.99), `r3` (0.986), `s1` (0.994), `s2` (0.996), `s3` (0.997), `supertrend_value` (0.986), `swing_high` (0.989), `swing_low` (0.985), `tema` (0.997), `triangle_breakdown_pct` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.985), `vp_value_area_high` (0.989), `vp_value_area_low` (0.982), `vwap` (0.957), `vwap_lower_1` (0.955), `vwap_upper_1` (0.957), `vwap_upper_2` (0.956), `weekly_close` (0.99), `weekly_ema_10` (0.993), `weekly_ema_20` (0.985), `wood_p` (0.996), `wood_r1` (0.997), `wood_r2` (0.995), `wood_s1` (0.997), `wood_s2` (0.997), `year_high` (0.985), `year_low` (0.965)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
