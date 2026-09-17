# Table A - bollinger_lower

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 7be42d989 at 2026-09-16 23:53:21 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** mean_reversion | **status:** STALLED-CAMPAIGN | **R5 fires:** 1622 | **surviving fires (T1):** 1622 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  bb_20_20_reclaim_from_lower_recent_3d  <- backtest/signals/screener.py
       knobs P1.1-P1.2 (band rows in Table A)
P2  bb_20_20_reclaim_from_upper_recent_3d  <- backtest/signals/screener.py
       knobs INVENTORY-PENDING-R1 (SPECS)
P3  below_ema_200  <- backtest/signals/screener.py
       knobs P3.1-P3.1 (band rows in Table A)
P4  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       knobs P4.1-P4.1 (band rows in Table A)
P5  rsi_14  <- backtest/signals/screener.py
       knobs INVENTORY-PENDING-R1 (SPECS)
P6  rsi_2  <- backtest/signals/screener.py
       knobs INVENTORY-PENDING-R1 (SPECS)
P7  vix_band_high  <- backtest/signals/screener.py +2
       knobs P7.1-P7.1 (band rows in Table A)
P8  vix_band_low  <- backtest/signals/screener.py +2
       knobs P8.1-P8.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P9  adx < 35   [EXISTING-THRESHOLD]
P10  _short_borrow_trap_active(s)   [helper gate]
P11  VIX-conditional RSI thresholds (low 40/60, mid 45/55, high 50/50)   [local-variable gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_bollinger_lower (docstring and return dropped):

```python
rsi_2 = s.get('rsi_2', 50)
rsi_14 = s.get('rsi_14', 50)
above_200 = s.get('price_above_ema_200', False)
below_200 = s.get('below_ema_200', False)
adx_ok = s.get('adx', 30) < 35
if s.get('vix_band_low'):
    rsi_thr_long, rsi_thr_short = (40, 60)
elif s.get('vix_band_high'):
    rsi_thr_long, rsi_thr_short = (50, 50)
else:
    rsi_thr_long, rsi_thr_short = (45, 55)
rsi_long_ok = rsi_2 < 5 or rsi_14 < rsi_thr_long
fl = s.get('bb_20_20_reclaim_from_lower_recent_3d') and rsi_long_ok and above_200 and adx_ok
rsi_short_ok = rsi_2 > 95 or rsi_14 > rsi_thr_short
fs = (s.get('bb_20_20_reclaim_from_upper_recent_3d') and rsi_short_ok and below_200 and adx_ok) and (not _short_borrow_trap_active(s))
```

## Table A - parameter inventory (the SS6 canonical shape, pre-R1)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close). The
R1 SPECS entry absorbs and supersedes this pre-R1 inventory - producer
knob rows below are placeholders it must fill.

| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|
| P1 | PRODUCER | bb_20_20_reclaim_from_lower_recent_3d - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P1.1 | BAND | bb period / k - backtest/signals/technical.py bb block + :1402 | 20 / 2.0 | none - band values at other k unpersisted for the reclaim test | the whole band; DEFINED-NO-ACTUATOR | k BRACKETs canon 2.0; period held (the 20_20 identity); T3 review before any grid |
| P1.2 | BAND | reclaim recency (bars) - technical.py:1402 | 3 | none - reclaim history unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production (B800 EVENT conversion); T3 review before any grid |
| P2 | PRODUCER | bb_20_20_reclaim_from_upper_recent_3d - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P3 | PRODUCER | below_ema_200 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P3.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | 200 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production; 150/250 are the adjacent canon spans; T3 review before any grid |
| P4 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P4.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | 200 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production; 150/250 are the adjacent canon spans; T3 review before any grid |
| P5 | PRODUCER | rsi_14 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P6 | PRODUCER | rsi_2 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P7 | PRODUCER | vix_band_high - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P7.1 | BAND | as vix_band_low (upper edge) - technical.py:2700 | 2/3 | re-derive from persisted vix_percentile | none needed | as vix_band_low; T3 review before any grid |
| P8 | PRODUCER | vix_band_low - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P8.1 | BAND | tercile edges on vix_percentile - backtest/signals/technical.py:2690-2702 | 1/3, 2/3 | any re-banding - re-derive from persisted vix_percentile | none needed | BRACKET terciles vs quartile edges; vix_percentile IS persisted; T3 review before any grid |
| P9 | STRATEGY | adx `< 35` [EXISTING-THRESHOLD] | `< 35` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P10 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| P11 | STRATEGY | VIX-conditional RSI thresholds (low 40/60, mid 45/55, high 50/50) - backtest/signals/screener.py:1855-1863 | B1147 widened set | TIGHTER edges - subset on persisted rsi keys per band | LOOSER edges | BRACKET production (Connors canonical, B1147 history); rsi_2/rsi_14 and vix_percentile all persisted; T3 review |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | `< 35` | 100.0% | TIGHTER = LOWER the ceiling: 17.69 -> 326 (20%); 20.976 -> 649 (40%); 23.96 -> 974 (60%); 27.51 -> 1298 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx_di_minus | backtest/signals/technical.py | 100.0% | 16.176, 20.114, 25.52, 30.486 | 16.176: 1297 (80%); 20.114: 973 (60%); 25.52: 650 (40%); 30.486: 325 (20%) | 16.176: 325 (20%); 20.114: 649 (40%); 25.52: 974 (60%); 30.486: 1297 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 15.71, 19.694, 26.446, 31.69 | 15.71: 1298 (80%); 19.694: 973 (60%); 26.446: 649 (40%); 31.69: 326 (20%) | 15.71: 326 (20%); 19.694: 649 (40%); 26.446: 973 (60%); 31.69: 1298 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -5.7955, -1.4996, 1.0697, 4.6828 | -5.7955: 1297 (80%); -1.4996: 973 (60%); 1.0697: 649 (40%); 4.6828: 325 (20%) | -5.7955: 325 (20%); -1.4996: 649 (40%); 1.0697: 973 (60%); 4.6828: 1297 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.271, 2.2412, 3.7452, 6.3495 | 1.271: 1297 (80%); 2.2412: 973 (60%); 3.7452: 649 (40%); 6.3495: 325 (20%) | 1.271: 325 (20%); 2.2412: 649 (40%); 3.7452: 973 (60%); 6.3495: 1297 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.271, 2.2412, 3.7452, 6.3495 | 1.271: 1297 (80%); 2.2412: 973 (60%); 3.7452: 649 (40%); 6.3495: 325 (20%) | 1.271: 325 (20%); 2.2412: 649 (40%); 3.7452: 973 (60%); 6.3495: 1297 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.1702, 2.6368, 3.1356, 3.8646 | 2.1702: 1297 (80%); 2.6368: 973 (60%); 3.1356: 649 (40%); 3.8646: 325 (20%) | 2.1702: 325 (20%); 2.6368: 649 (40%); 3.1356: 973 (60%); 3.8646: 1297 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0848, 0.1126, 0.1446, 0.1915 | 0.0848: 1298 (80%); 0.1126: 974 (60%); 0.1446: 649 (40%); 0.1915: 325 (20%) | 0.0848: 325 (20%); 0.1126: 653 (40%); 0.1446: 973 (60%); 0.1915: 1299 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.2282, 0.3736, 0.669, 0.7825 | 0.2282: 1297 (80%); 0.3736: 973 (60%); 0.669: 649 (40%); 0.7825: 325 (20%) | 0.2282: 325 (20%); 0.3736: 649 (40%); 0.669: 974 (60%); 0.7825: 1299 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0668, 0.0906, 0.1155, 0.1489 | 0.0668: 1298 (80%); 0.0906: 974 (60%); 0.1155: 650 (40%); 0.1489: 325 (20%) | 0.0668: 325 (20%); 0.0906: 650 (40%); 0.1155: 975 (60%); 0.1489: 1298 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.0357, 0.1438, 0.9032, 1.0535 | -0.0357: 1297 (80%); 0.1438: 973 (60%); 0.9032: 649 (40%); 1.0535: 326 (20%) | -0.0357: 325 (20%); 0.1438: 649 (40%); 0.9032: 973 (60%); 1.0535: 1298 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0891, 0.1208, 0.154, 0.1985 | 0.0891: 1298 (80%); 0.1208: 974 (60%); 0.154: 650 (40%); 0.1985: 326 (20%) | 0.0891: 326 (20%); 0.1208: 650 (40%); 0.154: 975 (60%); 0.1985: 1298 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0983, 0.2328, 0.8024, 0.9151 | 0.0983: 1297 (80%); 0.2328: 974 (60%); 0.8024: 649 (40%); 0.9151: 326 (20%) | 0.0983: 325 (20%); 0.2328: 649 (40%); 0.8024: 973 (60%); 0.9151: 1298 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0508, -0.0232, -0.0036, 0.0155 | -0.0508: 1298 (80%); -0.0232: 1002 (62%); -0.0036: 649 (40%); 0.0155: 326 (20%) | -0.0508: 326 (20%); -0.0232: 666 (41%); -0.0036: 989 (61%); 0.0155: 1299 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1375, 0.162, 0.1968, 0.2679 | 0.1375: 1298 (80%); 0.162: 949 (59%); 0.1968: 650 (40%); 0.2679: 326 (20%) | 0.1375: 324 (20%); 0.162: 673 (41%); 0.1968: 972 (60%); 0.2679: 1296 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1622 (100%) | 0: 1551 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1111, -0.0288, 0.0503, 0.1399 | -0.1111: 1297 (80%); -0.0288: 974 (60%); 0.0503: 649 (40%); 0.1399: 325 (20%) | -0.1111: 325 (20%); -0.0288: 649 (40%); 0.0503: 973 (60%); 0.1399: 1297 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1622 (100%); 1: 546 (34%) | 0: 1076 (66%); 1: 1434 (88%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2381, -0.1896, -0.1572, -0.1141 | -0.2381: 1301 (80%); -0.1896: 1010 (62%); -0.1572: 651 (40%); -0.1141: 336 (21%) | -0.2381: 338 (21%); -0.1896: 663 (41%); -0.1572: 978 (60%); -0.1141: 1359 (84%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5705, 0.6731, 0.7692 | 0.3397: 1299 (80%); 0.5705: 1029 (63%); 0.6731: 654 (40%); 0.7692: 330 (20%) | 0.3397: 327 (20%); 0.5705: 676 (42%); 0.6731: 1035 (64%); 0.7692: 1377 (85%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2821, 0.4295, 0.6603, 0.8654 | 0.2821: 1303 (80%); 0.4295: 984 (61%); 0.6603: 653 (40%); 0.8654: 328 (20%) | 0.2821: 337 (21%); 0.4295: 652 (40%); 0.6603: 977 (60%); 0.8654: 1303 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0921, -0.0081, 0.0722, 0.206 | -0.0921: 1299 (80%); -0.0081: 974 (60%); 0.0722: 654 (40%); 0.206: 326 (20%) | -0.0921: 345 (21%); -0.0081: 654 (40%); 0.0722: 975 (60%); 0.206: 1304 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.4679, 0.641, 0.8013 | 0.2628: 1308 (81%); 0.4679: 987 (61%); 0.641: 653 (40%); 0.8013: 337 (21%) | 0.2628: 331 (20%); 0.4679: 668 (41%); 0.641: 1003 (62%); 0.8013: 1325 (82%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.3462, 0.4679, 0.6346 | 0.1795: 1301 (80%); 0.3462: 1009 (62%); 0.4679: 667 (41%); 0.6346: 331 (20%) | 0.1795: 331 (20%); 0.3462: 668 (41%); 0.4679: 986 (61%); 0.6346: 1300 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.521, -0.4263, -0.1909, 0.0839 | -0.521: 1300 (80%); -0.4263: 989 (61%); -0.1909: 650 (40%); 0.0839: 338 (21%) | -0.521: 344 (21%); -0.4263: 662 (41%); -0.1909: 985 (61%); 0.0839: 1303 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.4679, 0.6923, 0.9551 | 0.3013: 1320 (81%); 0.4679: 988 (61%); 0.6923: 661 (41%); 0.9551: 327 (20%) | 0.3013: 330 (20%); 0.4679: 661 (41%); 0.6923: 986 (61%); 0.9551: 1324 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3141, 0.5192, 0.8513 | 0.1218: 1312 (81%); 0.3141: 1020 (63%); 0.5192: 683 (42%); 0.8513: 325 (20%) | 0.1218: 327 (20%); 0.3141: 653 (40%); 0.5192: 998 (62%); 0.8513: 1297 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0657, -0.0521, -0.0356, 0 | -0.0657: 1299 (80%); -0.0521: 977 (60%); -0.0356: 666 (41%); 0: 498 (31%) | -0.0657: 327 (20%); -0.0521: 654 (40%); -0.0356: 981 (60%); 0: 1544 (95%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4231, 0.7372, 0.9038, 1 | 0.4231: 1299 (80%); 0.7372: 975 (60%); 0.9038: 708 (44%); 1: 385 (24%) | 0.4231: 330 (20%); 0.7372: 657 (41%); 0.9038: 1001 (62%); 1: 1622 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0833, 0.1987, 0.4744, 0.8526 | 0.0833: 1335 (82%); 0.1987: 993 (61%); 0.4744: 654 (40%); 0.8526: 333 (21%) | 0.0833: 337 (21%); 0.1987: 660 (41%); 0.4744: 974 (60%); 0.8526: 1322 (82%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0182, 0.0553, 0.1157, 0.2489 | 0.0182: 1321 (81%); 0.0553: 980 (60%); 0.1157: 650 (40%); 0.2489: 390 (24%) | 0.0182: 351 (22%); 0.0553: 650 (40%); 0.1157: 974 (60%); 0.2489: 1305 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.7049, 0.8974, 0.9551, 0.9808 | 0.7049: 1309 (81%); 0.8974: 975 (60%); 0.9551: 685 (42%); 0.9808: 348 (21%) | 0.7049: 329 (20%); 0.8974: 653 (40%); 0.9551: 1003 (62%); 0.9808: 1340 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0897, 0.2051, 0.3933, 0.6364 | 0.0897: 1318 (81%); 0.2051: 1001 (62%); 0.3933: 668 (41%); 0.6364: 380 (23%) | 0.0897: 326 (20%); 0.2051: 655 (40%); 0.3933: 979 (60%); 0.6364: 1301 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0599, 0.0566, 0.1225, 0.2205 | -0.0599: 1302 (80%); 0.0566: 982 (61%); 0.1225: 744 (46%); 0.2205: 334 (21%) | -0.0599: 337 (21%); 0.0566: 705 (43%); 0.1225: 991 (61%); 0.2205: 1316 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3109, -0.0268, 0.0444, 0.0897 | -0.3109: 1302 (80%); -0.0268: 977 (60%); 0.0444: 654 (40%); 0.0897: 374 (23%) | -0.3109: 329 (20%); -0.0268: 654 (40%); 0.0444: 979 (60%); 0.0897: 1299 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5513, 0.7436, 0.8782 | 0.2628: 1331 (82%); 0.5513: 976 (60%); 0.7436: 685 (42%); 0.8782: 366 (23%) | 0.2628: 364 (22%); 0.5513: 677 (42%); 0.7436: 974 (60%); 0.8782: 1309 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.3333, 0.5577, 0.8205 | 0.1282: 1304 (80%); 0.3333: 982 (61%); 0.5577: 659 (41%); 0.8205: 338 (21%) | 0.1282: 327 (20%); 0.3333: 662 (41%); 0.5577: 975 (60%); 0.8205: 1299 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.07, 0.1683, 0.328, 0.6793 | 0.07: 1298 (80%); 0.1683: 977 (60%); 0.328: 649 (40%); 0.6793: 325 (20%) | 0.07: 330 (20%); 0.1683: 650 (40%); 0.328: 973 (60%); 0.6793: 1297 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.6% | 26.8, 61, 84, 146 | 26.8: 1280 (79%); 61: 976 (60%); 84: 653 (40%); 146: 321 (20%) | 26.8: 320 (20%); 61: 643 (40%); 84: 967 (60%); 146: 1287 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.1% | 1.8514, 2.374, 2.9837, 3.9875 | 1.8514: 1286 (79%); 2.374: 966 (60%); 2.9837: 643 (40%); 3.9875: 322 (20%) | 1.8514: 322 (20%); 2.374: 645 (40%); 2.9837: 965 (59%); 3.9875: 1286 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7, 14, 27, 35 | 7: 1302 (80%); 14: 1010 (62%); 27: 665 (41%); 35: 369 (23%) | 7: 375 (23%); 14: 682 (42%); 27: 1013 (62%); 35: 1300 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 1315 (81%); 2: 964 (59%); 3: 604 (37%) | 1: 658 (41%); 2: 1018 (63%); 3: 1347 (83%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0126, -0.0015, 0.0131, 0.024 | -0.0126: 1298 (80%); -0.0015: 976 (60%); 0.0131: 649 (40%); 0.024: 329 (20%) | -0.0126: 333 (21%); -0.0015: 649 (40%); 0.0131: 980 (60%); 0.024: 1299 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5861, 25.9923, 26.7389, 27.3557 | 24.5861: 1298 (80%); 25.9923: 987 (61%); 26.7389: 664 (41%); 27.3557: 360 (22%) | 24.5861: 331 (20%); 25.9923: 651 (40%); 26.7389: 981 (60%); 27.3557: 1306 (81%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.769, -0.2334, 0.163, 0.774 | -0.769: 1298 (80%); -0.2334: 973 (60%); 0.163: 650 (40%); 0.774: 326 (20%) | -0.769: 327 (20%); -0.2334: 649 (40%); 0.163: 974 (60%); 0.774: 1298 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.774, -0.163, 0.2334, 0.769 | -0.774: 1298 (80%); -0.163: 974 (60%); 0.2334: 649 (40%); 0.769: 327 (20%) | -0.774: 326 (20%); -0.163: 650 (40%); 0.2334: 973 (60%); 0.769: 1298 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0446, -0.0136, 0.0189, 0.0601 | -0.0446: 1300 (80%); -0.0136: 974 (60%); 0.0189: 649 (40%); 0.0601: 325 (20%) | -0.0446: 328 (20%); -0.0136: 651 (40%); 0.0189: 973 (60%); 0.0601: 1297 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0713, 8.4924, 8.7489, 9.1471 | 8.0713: 1297 (80%); 8.4924: 973 (60%); 8.7489: 649 (40%); 9.1471: 325 (20%) | 8.0713: 325 (20%); 8.4924: 649 (40%); 8.7489: 973 (60%); 9.1471: 1297 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 98.7% | 0, 1 | 0: 1601 (99%); 1: 489 (30%) | 0: 1112 (69%); 1: 1443 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 98.7% | 0 | 0: 1315 (81%) | 0: 1335 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 98.7% | 0, 1 | 0: 1601 (99%); 1: 517 (32%) | 0: 1084 (67%); 1: 1450 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 6, 150.6, 272.8 | 2: 1391 (86%); 6: 1008 (62%); 150.6: 649 (40%); 272.8: 325 (20%) | 2: 333 (21%); 6: 691 (43%); 150.6: 973 (60%); 272.8: 1297 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 5, 86, 147 | 1: 1324 (82%); 5: 974 (60%); 86: 659 (41%); 147: 328 (20%) | 1: 413 (25%); 5: 680 (42%); 86: 974 (60%); 147: 1303 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.3614, -0.4339, 0.333, 1.1291 | -1.3614: 1297 (80%); -0.4339: 973 (60%); 0.333: 649 (40%); 1.1291: 325 (20%) | -1.3614: 325 (20%); -0.4339: 649 (40%); 0.333: 973 (60%); 1.1291: 1297 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.4693, -0.3406, 0.2726, 1.1643 | -1.4693: 1297 (80%); -0.3406: 973 (60%); 0.2726: 649 (40%); 1.1643: 325 (20%) | -1.4693: 325 (20%); -0.3406: 649 (40%); 0.2726: 973 (60%); 1.1643: 1297 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.0136, -0.2243, 0.1528, 0.8019 | -1.0136: 1297 (80%); -0.2243: 973 (60%); 0.1528: 650 (40%); 0.8019: 325 (20%) | -1.0136: 325 (20%); -0.2243: 649 (40%); 0.1528: 974 (60%); 0.8019: 1297 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.7976, -0.2172, 0.2035, 0.6802 | -0.7976: 1297 (80%); -0.2172: 974 (60%); 0.2035: 649 (40%); 0.6802: 326 (20%) | -0.7976: 325 (20%); -0.2172: 650 (40%); 0.2035: 973 (60%); 0.6802: 1298 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -2.6334, -0.7085, 0.5853, 2.0639 | -2.6334: 1297 (80%); -0.7085: 973 (60%); 0.5853: 649 (40%); 2.0639: 325 (20%) | -2.6334: 325 (20%); -0.7085: 649 (40%); 0.5853: 973 (60%); 2.0639: 1297 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.7562, -0.3881, 0.321, 1.3781 | -1.7562: 1297 (80%); -0.3881: 973 (60%); 0.321: 649 (40%); 1.3781: 325 (20%) | -1.7562: 325 (20%); -0.3881: 649 (40%); 0.321: 973 (60%); 1.3781: 1297 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 34.666, 45.964, 57.388, 67.948 | 34.666: 1297 (80%); 45.964: 973 (60%); 57.388: 649 (40%); 67.948: 325 (20%) | 34.666: 325 (20%); 45.964: 649 (40%); 57.388: 973 (60%); 67.948: 1297 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.9% | 0.0077, 0.0168, 0.03, 0.052 | 0.0077: 1294 (80%); 0.0168: 972 (60%); 0.03: 649 (40%); 0.052: 323 (20%) | 0.0077: 326 (20%); 0.0168: 648 (40%); 0.03: 971 (60%); 0.052: 1297 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 10 | 0: 1622 (100%); 2: 985 (61%); 4: 675 (42%); 10: 326 (20%) | 0: 376 (23%); 2: 811 (50%); 4: 1019 (63%); 10: 1333 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 1622 (100%); 0.1667: 358 (22%) | 0: 1058 (65%); 0.1667: 1299 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.4365, 0.6667 | 0: 1622 (100%); 0.2: 974 (60%); 0.4365: 649 (40%); 0.6667: 360 (22%) | 0: 596 (37%); 0.2: 667 (41%); 0.4365: 974 (60%); 0.6667: 1321 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 7 | 0: 1622 (100%); 1: 1137 (70%); 3: 672 (41%); 7: 340 (21%) | 0: 485 (30%); 1: 758 (47%); 3: 1075 (66%); 7: 1331 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 10 | 0: 1622 (100%); 2: 985 (61%); 4: 675 (42%); 10: 326 (20%) | 0: 376 (23%); 2: 811 (50%); 4: 1019 (63%); 10: 1333 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1622 (100%); 1: 1111 (68%); 3: 699 (43%); 7: 375 (23%) | 0: 511 (32%); 1: 774 (48%); 3: 1034 (64%); 7: 1300 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2258, 0.3797, 0.6109 | 0: 1512 (93%); 0.2258: 974 (60%); 0.3797: 649 (40%); 0.6109: 325 (20%) | 0: 364 (22%); 0.2258: 650 (40%); 0.3797: 974 (60%); 0.6109: 1297 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1775, 0.5601 | 0: 1456 (90%); 0.1775: 649 (40%); 0.5601: 325 (20%) | 0: 869 (54%); 0.1775: 973 (60%); 0.5601: 1297 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3137, 0.6 | 0: 1470 (91%); 0.3137: 650 (40%); 0.6: 337 (21%) | 0: 704 (43%); 0.3137: 974 (60%); 0.6: 1303 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3137, 0.6 | 0: 1470 (91%); 0.3137: 650 (40%); 0.6: 337 (21%) | 0: 704 (43%); 0.3137: 974 (60%); 0.6: 1303 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1814, 0, 0.1429 | -0.1814: 1297 (80%); 0: 1145 (71%); 0.1429: 327 (20%) | -0.1814: 325 (20%); 0: 1195 (74%); 0.1429: 1299 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6461, -0.0775, 0.3126, 1.6383 | -0.6461: 1312 (81%); -0.0775: 973 (60%); 0.3126: 649 (40%); 1.6383: 325 (20%) | -0.6461: 362 (22%); -0.0775: 649 (40%); 0.3126: 973 (60%); 1.6383: 1297 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 6, 10 | 2: 1340 (83%); 4: 1023 (63%); 6: 754 (46%); 10: 385 (24%) | 2: 437 (27%); 4: 737 (45%); 6: 980 (60%); 10: 1305 (80%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0647, -0.0314, 0.0409, 0.0819 | -0.0647: 1297 (80%); -0.0314: 973 (60%); 0.0409: 649 (40%); 0.0819: 325 (20%) | -0.0647: 325 (20%); -0.0314: 649 (40%); 0.0409: 973 (60%); 0.0819: 1297 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0629, -0.027, 0.0402, 0.0912 | -0.0629: 1298 (80%); -0.027: 973 (60%); 0.0402: 650 (40%); 0.0912: 325 (20%) | -0.0629: 324 (20%); -0.027: 649 (40%); 0.0402: 972 (60%); 0.0912: 1297 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0436, -0.0161, 0.0218, 0.0542 | -0.0436: 1298 (80%); -0.0161: 973 (60%); 0.0218: 649 (40%); 0.0542: 325 (20%) | -0.0436: 324 (20%); -0.0161: 649 (40%); 0.0218: 973 (60%); 0.0542: 1297 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -18.6832, -5.8756, 7.426, 28.3488 | -18.6832: 1297 (80%); -5.8756: 973 (60%); 7.426: 649 (40%); 28.3488: 325 (20%) | -18.6832: 325 (20%); -5.8756: 649 (40%); 7.426: 973 (60%); 28.3488: 1297 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0572, 0.0745, 0.0961, 0.1336 | 0.0572: 1299 (80%); 0.0745: 974 (60%); 0.0961: 650 (40%); 0.1336: 325 (20%) | 0.0572: 325 (20%); 0.0745: 649 (40%); 0.0961: 975 (60%); 0.1336: 1298 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1514, 0.3119, 0.5038, 0.7369 | 0.1514: 1297 (80%); 0.3119: 973 (60%); 0.5038: 649 (40%); 0.7369: 326 (20%) | 0.1514: 325 (20%); 0.3119: 649 (40%); 0.5038: 973 (60%); 0.7369: 1298 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.2615, -0.4405, 0.4235, 1.404 | -1.2615: 1297 (80%); -0.4405: 973 (60%); 0.4235: 649 (40%); 1.404: 325 (20%) | -1.2615: 325 (20%); -0.4405: 649 (40%); 0.4235: 973 (60%); 1.404: 1297 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.9689, -0.5393, 0.6797, 1.2145 | -0.9689: 1297 (80%); -0.5393: 973 (60%); 0.6797: 649 (40%); 1.2145: 325 (20%) | -0.9689: 325 (20%); -0.5393: 649 (40%); 0.6797: 973 (60%); 1.2145: 1297 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -0.9148, -0.3071, 0.2182, 0.8751 | -0.9148: 1297 (80%); -0.3071: 973 (60%); 0.2182: 649 (40%); 0.8751: 325 (20%) | -0.9148: 325 (20%); -0.3071: 649 (40%); 0.2182: 973 (60%); 0.8751: 1297 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -6.6824, -3.3306, 4.4142, 8.7148 | -6.6824: 1297 (80%); -3.3306: 973 (60%); 4.4142: 649 (40%); 8.7148: 325 (20%) | -6.6824: 325 (20%); -3.3306: 649 (40%); 4.4142: 973 (60%); 8.7148: 1297 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 39.002, 44.818, 56.16, 61.21 | 39.002: 1297 (80%); 44.818: 973 (60%); 56.16: 650 (40%); 61.21: 326 (20%) | 39.002: 325 (20%); 44.818: 649 (40%); 56.16: 975 (60%); 61.21: 1298 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 28.964, 43.888, 56.716, 72.018 | 28.964: 1297 (80%); 43.888: 973 (60%); 56.716: 649 (40%); 72.018: 325 (20%) | 28.964: 325 (20%); 43.888: 649 (40%); 56.716: 973 (60%); 72.018: 1297 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 43.162, 47.36, 52.4, 56.808 | 43.162: 1297 (80%); 47.36: 974 (60%); 52.4: 650 (40%); 56.808: 325 (20%) | 43.162: 325 (20%); 47.36: 650 (40%); 52.4: 974 (60%); 56.808: 1297 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 34.214, 42.466, 59.47, 66.348 | 34.214: 1297 (80%); 42.466: 973 (60%); 59.47: 649 (40%); 66.348: 325 (20%) | 34.214: 325 (20%); 42.466: 649 (40%); 59.47: 973 (60%); 66.348: 1297 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 1619 (100%) | 0: 1621 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0347, 0.0499, 0.0656, 0.095 | 0.0347: 1298 (80%); 0.0499: 976 (60%); 0.0656: 650 (40%); 0.095: 326 (20%) | 0.0347: 326 (20%); 0.0499: 654 (40%); 0.0656: 974 (60%); 0.095: 1306 (81%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0729, -0.0549, -0.0433, -0.0341 | -0.0729: 1298 (80%); -0.0549: 973 (60%); -0.0433: 649 (40%); -0.0341: 329 (20%) | -0.0729: 325 (20%); -0.0549: 649 (40%); -0.0433: 980 (60%); -0.0341: 1301 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1622 (100%); 1: 461 (28%) | 0: 1161 (72%); 1: 1339 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.1% | 24, 44, 60, 69 | 24: 1325 (82%); 44: 978 (60%); 60: 659 (41%); 69: 344 (21%) | 24: 327 (20%); 44: 644 (40%); 60: 986 (61%); 69: 1287 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.2831, 0.436, 0.5601, 0.7366 | 0.2831: 1298 (80%); 0.436: 973 (60%); 0.5601: 649 (40%); 0.7366: 326 (20%) | 0.2831: 326 (20%); 0.436: 649 (40%); 0.5601: 973 (60%); 0.7366: 1298 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 32.14, 49.74, 70.76, 104.64 | 32.14: 1297 (80%); 49.74: 973 (60%); 70.76: 649 (40%); 104.64: 325 (20%) | 32.14: 325 (20%); 49.74: 649 (40%); 70.76: 973 (60%); 104.64: 1297 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -4.9185, -1.285, 1.46, 4.614 | -4.9185: 1297 (80%); -1.285: 973 (60%); 1.46: 649 (40%); 4.614: 325 (20%) | -4.9185: 325 (20%); -1.285: 649 (40%); 1.46: 973 (60%); 4.614: 1297 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 13.516, 24.548, 78.474, 89.028 | 13.516: 1297 (80%); 24.548: 973 (60%); 78.474: 649 (40%); 89.028: 325 (20%) | 13.516: 325 (20%); 24.548: 649 (40%); 78.474: 973 (60%); 89.028: 1297 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 14.872, 28.342, 78.762, 88.69 | 14.872: 1297 (80%); 28.342: 973 (60%); 78.762: 649 (40%); 88.69: 326 (20%) | 14.872: 325 (20%); 28.342: 649 (40%); 78.762: 973 (60%); 88.69: 1298 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 8.43, 25.752, 76.052, 93.424 | 8.43: 1298 (80%); 25.752: 973 (60%); 76.052: 649 (40%); 93.424: 325 (20%) | 8.43: 326 (20%); 25.752: 649 (40%); 76.052: 973 (60%); 93.424: 1297 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 9.622, 32.844, 67.374, 90.42 | 9.622: 1297 (80%); 32.844: 973 (60%); 67.374: 649 (40%); 90.42: 325 (20%) | 9.622: 325 (20%); 32.844: 649 (40%); 67.374: 973 (60%); 90.42: 1297 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 13, 16 | 5: 1307 (81%); 8: 1046 (64%); 13: 672 (41%); 16: 387 (24%) | 5: 382 (24%); 8: 652 (40%); 13: 1038 (64%); 16: 1315 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 17 | 5: 1356 (84%); 9: 1060 (65%); 14: 659 (41%); 17: 398 (25%) | 5: 334 (21%); 9: 653 (40%); 14: 1039 (64%); 17: 1307 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 38.722, 46.224, 54.912, 62.018 | 38.722: 1297 (80%); 46.224: 973 (60%); 54.912: 649 (40%); 62.018: 325 (20%) | 38.722: 325 (20%); 46.224: 649 (40%); 54.912: 973 (60%); 62.018: 1297 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.3611, 0.5635, 0.754, 0.9167 | 0.3611: 1301 (80%); 0.5635: 982 (61%); 0.754: 651 (40%); 0.9167: 330 (20%) | 0.3611: 333 (21%); 0.5635: 654 (40%); 0.754: 976 (60%); 0.9167: 1302 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.43, 18.71, 21.97, 25.76 | 16.43: 1300 (80%); 18.71: 976 (60%); 21.97: 651 (40%); 25.76: 326 (20%) | 16.43: 326 (20%); 18.71: 653 (40%); 21.97: 977 (60%); 25.76: 1298 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 16.43, 18.71, 21.97, 25.76 | 16.43: 1300 (80%); 18.71: 976 (60%); 21.97: 651 (40%); 25.76: 326 (20%) | 16.43: 326 (20%); 18.71: 653 (40%); 21.97: 977 (60%); 25.76: 1298 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8729, 0.9075, 0.9446, 0.974 | 0.8729: 1299 (80%); 0.9075: 973 (60%); 0.9446: 655 (40%); 0.974: 325 (20%) | 0.8729: 326 (20%); 0.9075: 649 (40%); 0.9446: 975 (60%); 0.974: 1298 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.75, 0.87, 1, 1.248 | 0.75: 1302 (80%); 0.87: 998 (62%); 1: 672 (41%); 1.248: 325 (20%) | 0.75: 337 (21%); 0.87: 654 (40%); 1: 974 (60%); 1.248: 1297 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0219, 0.0413, 0.0625, 0.0927 | 0.0219: 1298 (80%); 0.0413: 974 (60%); 0.0625: 649 (40%); 0.0927: 325 (20%) | 0.0219: 325 (20%); 0.0413: 650 (40%); 0.0625: 975 (60%); 0.0927: 1298 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 46.0303, 79.6756, 123.2904, 205.4076 | 46.0303: 1297 (80%); 79.6756: 973 (60%); 123.2904: 649 (40%); 205.4076: 325 (20%) | 46.0303: 325 (20%); 79.6756: 649 (40%); 123.2904: 973 (60%); 205.4076: 1297 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.8128, 76.5198, 118.7561, 199.5864 | 43.8128: 1297 (80%); 76.5198: 973 (60%); 118.7561: 649 (40%); 199.5864: 325 (20%) | 43.8128: 325 (20%); 76.5198: 649 (40%); 118.7561: 973 (60%); 199.5864: 1297 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.8714, 73.3629, 114.073, 192.7142 | 41.8714: 1297 (80%); 73.3629: 973 (60%); 114.073: 649 (40%); 192.7142: 325 (20%) | 41.8714: 325 (20%); 73.3629: 649 (40%); 114.073: 973 (60%); 192.7142: 1297 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.8092, 82.3538, 129.0372, 211.1836 | 47.8092: 1297 (80%); 82.3538: 973 (60%); 129.0372: 649 (40%); 211.1836: 325 (20%) | 47.8092: 325 (20%); 82.3538: 649 (40%); 129.0372: 973 (60%); 211.1836: 1297 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 49.3474, 85.4315, 133.7398, 217.7273 | 49.3474: 1297 (80%); 85.4315: 973 (60%); 133.7398: 649 (40%); 217.7273: 325 (20%) | 49.3474: 325 (20%); 85.4315: 649 (40%); 133.7398: 973 (60%); 217.7273: 1297 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1622 (100%) | 0: 1445 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1622 (100%) | 0: 1469 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.066, -0.0316, 0.0444, 0.0949 | -0.066: 1298 (80%); -0.0316: 973 (60%); 0.0444: 649 (40%); 0.0949: 325 (20%) | -0.066: 325 (20%); -0.0316: 649 (40%); 0.0444: 975 (60%); 0.0949: 1297 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -81.868, -64.118, -30.044, -16.936 | -81.868: 1297 (80%); -64.118: 973 (60%); -30.044: 649 (40%); -16.936: 325 (20%) | -81.868: 325 (20%); -64.118: 649 (40%); -30.044: 973 (60%); -16.936: 1297 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.6% | 0.4966, 0.8027, 1.0438, 1.3458 | 0.4966: 1293 (80%); 0.8027: 970 (60%); 1.0438: 647 (40%); 1.3458: 324 (20%) | 0.4966: 324 (20%); 0.8027: 647 (40%); 1.0438: 970 (60%); 1.3458: 1293 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 1324 (82%); 5: 1051 (65%); 7: 751 (46%); 9: 434 (27%) | 3: 432 (27%); 5: 706 (44%); 7: 1023 (63%); 9: 1379 (85%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.6% | 0.1934, 0.2373, 0.2846, 0.3682 | 0.1934: 1293 (80%); 0.2373: 971 (60%); 0.2846: 647 (40%); 0.3682: 324 (20%) | 0.1934: 324 (20%); 0.2373: 647 (40%); 0.2846: 970 (60%); 0.3682: 1293 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.6% | 3, 5, 7, 9 | 3: 1360 (84%); 5: 1098 (68%); 7: 802 (49%); 9: 455 (28%) | 3: 391 (24%); 5: 666 (41%); 7: 985 (61%); 9: 1363 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.6% | 0.0222, 0.0318, 0.0423, 0.0583 | 0.0222: 1296 (80%); 0.0318: 970 (60%); 0.0423: 650 (40%); 0.0583: 324 (20%) | 0.0222: 327 (20%); 0.0318: 649 (40%); 0.0423: 970 (60%); 0.0583: 1293 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 1336 (82%); 5: 1068 (66%); 7: 754 (46%); 9: 397 (24%) | 3: 427 (26%); 5: 699 (43%); 7: 1030 (64%); 9: 1410 (87%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.8% | -0.2811, -0.0967, 0.1221, 0.3477 | -0.2811: 1295 (80%); -0.0967: 971 (60%); 0.1221: 648 (40%); 0.3477: 324 (20%) | -0.2811: 324 (20%); -0.0967: 648 (40%); 0.1221: 972 (60%); 0.3477: 1295 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.8% | 2, 4, 7, 9 | 2: 1331 (82%); 4: 999 (62%); 7: 667 (41%); 9: 409 (25%) | 2: 481 (30%); 4: 739 (46%); 7: 1069 (66%); 9: 1361 (84%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.5% |
| 8k_item_5_02_filed_within_7d | 3.0% |
| above_avwap_20high | 11.6% |
| above_avwap_20low | 86.0% |
| above_avwap_252low | 93.7% |
| above_avwap_50low | 70.2% |
| above_cam_r3 | 23.8% |
| above_cam_r4 | 11.3% |
| above_cpr | 47.4% |
| above_pivot | 46.9% |
| above_prev_high | 14.1% |
| above_prev_high_clearance_atr_05 | 3.5% |
| above_prev_low | 81.4% |
| above_r1 | 12.0% |
| above_r2 | 3.8% |
| above_vwap | 51.2% |
| above_wood_p | 48.3% |
| ad_rising | 49.1% |
| adx_cross_up | 3.9% |
| adx_cross_up_20 | 4.3% |
| adx_di_bear | 49.9% |
| adx_di_bull | 50.1% |
| adx_trending | 34.2% |
| ao_cross_dn | 2.3% |
| ao_cross_up | 2.5% |
| ao_positive | 49.3% |
| ao_twin_peaks_bull | 2.8% |
| at_key_fib | 21.3% |
| at_key_fib_wide | 51.6% |
| avwap_20high_loss_recent_3d | 24.2% |
| avwap_20high_reclaim_recent_3d | 7.8% |
| avwap_20low_loss_recent_3d | 8.8% |
| avwap_20low_reclaim_recent_3d | 23.9% |
| avwap_252low_loss_recent_3d | 1.7% |
| avwap_252low_reclaim_recent_3d | 7.9% |
| avwap_50low_loss_recent_3d | 9.5% |
| avwap_50low_reclaim_recent_3d | 13.0% |
| bb_10_20_above_mid | 51.0% |
| bb_10_20_expanding | 52.5% |
| bb_10_20_pctb_gt_75 | 26.7% |
| bb_10_20_pctb_gt_8 | 16.3% |
| bb_10_20_pctb_gt_85 | 6.1% |
| bb_10_20_pctb_gt_9 | 1.4% |
| bb_10_20_pctb_gt_95 | 0.2% |
| bb_10_20_pctb_lt_05 | 0.1% |
| bb_10_20_pctb_lt_1 | 1.2% |
| bb_10_20_pctb_lt_15 | 5.2% |
| bb_10_20_pctb_lt_2 | 14.1% |
| bb_10_20_pctb_lt_25 | 23.0% |
| bb_10_20_reclaim_from_lower_recent_3d | 20.8% |
| bb_10_20_reclaim_from_upper_recent_3d | 22.3% |
| bb_10_20_squeeze | 16.8% |
| bb_10_20_touch_lower | 0.5% |
| bb_10_20_touch_upper | 0.2% |
| bb_20_15_above_mid | 50.2% |
| bb_20_15_expanding | 86.0% |
| bb_20_15_pctb_gt_75 | 47.5% |
| bb_20_15_pctb_gt_8 | 46.3% |
| bb_20_15_pctb_gt_85 | 43.6% |
| bb_20_15_pctb_gt_9 | 40.5% |
| bb_20_15_pctb_gt_95 | 35.3% |
| bb_20_15_pctb_lt_05 | 31.0% |
| bb_20_15_pctb_lt_1 | 36.9% |
| bb_20_15_pctb_lt_15 | 40.4% |
| bb_20_15_pctb_lt_2 | 43.8% |
| bb_20_15_pctb_lt_25 | 45.4% |
| bb_20_15_reclaim_from_lower_recent_3d | 25.5% |
| bb_20_15_reclaim_from_upper_recent_3d | 21.5% |
| bb_20_15_squeeze | 31.3% |
| bb_20_15_touch_lower | 32.4% |
| bb_20_15_touch_upper | 35.0% |
| bb_20_20_above_mid | 50.2% |
| bb_20_20_expanding | 86.0% |
| bb_20_20_pctb_gt_75 | 44.7% |
| bb_20_20_pctb_gt_8 | 40.5% |
| bb_20_20_pctb_gt_85 | 33.7% |
| bb_20_20_pctb_gt_9 | 23.5% |
| bb_20_20_pctb_gt_95 | 11.8% |
| bb_20_20_pctb_lt_05 | 10.7% |
| bb_20_20_pctb_lt_1 | 20.4% |
| bb_20_20_pctb_lt_15 | 28.8% |
| bb_20_20_pctb_lt_2 | 36.9% |
| bb_20_20_pctb_lt_25 | 41.5% |
| bb_20_20_reclaim_from_lower_recent_3d | 50.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 49.9% |
| bb_20_20_squeeze | 14.4% |
| bb_20_20_touch_lower | 8.2% |
| bb_20_20_touch_upper | 9.7% |
| bearish_engulfing | 5.6% |
| bearish_pin_bar | 6.7% |
| below_avwap_20high | 88.4% |
| below_avwap_20low | 14.0% |
| below_avwap_252low | 6.3% |
| below_avwap_50low | 29.8% |
| below_cam_s3 | 35.8% |
| below_cam_s4 | 19.7% |
| below_cpr | 53.1% |
| below_ema_20 | 49.9% |
| below_ema_200 | 49.8% |
| below_ema_200_break_recent_5d | 7.8% |
| below_ema_20_break_recent_5d | 17.1% |
| below_ema_21 | 49.9% |
| below_ema_21_break_recent_5d | 17.4% |
| below_ema_50 | 51.0% |
| below_ema_50_break_recent_5d | 28.7% |
| below_ema_9 | 47.8% |
| below_ema_9_break_recent_5d | 16.5% |
| below_prev_high | 85.8% |
| below_prev_low | 18.4% |
| below_prev_low_clearance_atr_05 | 4.5% |
| below_s1 | 19.9% |
| below_s2 | 5.1% |
| below_sma_20 | 49.8% |
| below_sma_200 | 49.2% |
| below_sma_21 | 49.8% |
| below_sma_50 | 50.2% |
| below_sma_9 | 48.4% |
| below_vwap | 48.8% |
| blowoff_recent_3d | 1.1% |
| bullish_engulfing | 4.1% |
| bullish_pin_bar | 6.2% |
| capitulation_recent_3d | 0.6% |
| ceo_buy | 0.4% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 61.1% |
| chandelier_long_flip_dn | 2.1% |
| chandelier_short_bearish | 57.0% |
| chandelier_short_flip_up | 2.0% |
| close_above_open | 32.9% |
| close_below_open | 65.4% |
| close_in_bottom_40pct_of_range | 48.8% |
| close_in_top_40pct_of_range | 31.9% |
| cluster_buy | 0.2% |
| cmf_cross_dn | 6.0% |
| cmf_cross_up | 4.0% |
| cmf_negative | 48.0% |
| cmf_positive | 52.0% |
| concentrated_sell | 4.8% |
| cpr_narrow | 86.2% |
| cpr_narrow_tight | 22.8% |
| cup_handle_detected | 8.1% |
| cup_handle_neckline_break_retest_long | 2.8% |
| dc10_breakout_dn | 3.1% |
| dc10_breakout_dn_1pct | 9.7% |
| dc10_breakout_up | 3.1% |
| dc10_breakout_up_1pct | 10.6% |
| dc10_new_high | 17.0% |
| dc20_breakout_dn | 3.1% |
| dc20_breakout_up | 3.1% |
| dc20_new_high | 16.7% |
| dc20_resistance_break_retest_strong | 32.6% |
| dc20_support_break_retest_strong | 30.9% |
| defensive_leadership | 50.4% |
| director_only_buy | 3.0% |
| doji | 6.6% |
| double_bottom_detected | 17.3% |
| double_top_detected | 18.3% |
| dpi_elevated | 55.5% |
| drying_volume_on_down_turn | 39.8% |
| drying_volume_on_up_turn | 18.4% |
| ema_20_50_bearish | 50.7% |
| ema_20_50_bullish | 49.3% |
| ema_20_50_death_cross | 2.0% |
| ema_20_50_golden_cross | 2.0% |
| ema_50_200_bearish | 49.8% |
| ema_50_200_bullish | 50.2% |
| ema_9_21_bearish | 50.7% |
| ema_9_21_bullish | 49.3% |
| ema_9_21_death_cross | 1.6% |
| ema_9_21_golden_cross | 1.3% |
| evening_star | 5.5% |
| flag_bear_break_retest_short | 0.2% |
| flag_bear_broke | 0.2% |
| flag_bear_detected | 0.1% |
| flag_bull_break_retest_long | 0.4% |
| flag_bull_broke | 0.4% |
| force_index_cross_dn | 2.2% |
| force_index_cross_up | 1.6% |
| force_index_positive | 51.3% |
| gap_dn_1_5pct | 8.3% |
| gap_dn_2pct | 4.9% |
| gap_up_1_5pct | 7.9% |
| gap_up_2pct | 4.4% |
| hammer | 5.7% |
| head_shoulders_bottom_detected | 4.7% |
| head_shoulders_top_detected | 5.1% |
| house_cluster_buy | 4.2% |
| house_cluster_sell | 3.1% |
| htf_aligned_bear | 6.4% |
| htf_aligned_bull | 5.9% |
| htf_disagreement | 10.7% |
| hull_bearish | 49.9% |
| hull_bullish | 50.1% |
| hull_flip_dn | 0.1% |
| hull_flip_up | 0.3% |
| ichi_above_cloud | 31.8% |
| ichi_above_cloud_break_recent_5d | 15.2% |
| ichi_below_cloud | 35.1% |
| ichi_below_cloud_break_recent_5d | 16.5% |
| ichi_cloud_thick | 89.2% |
| ichi_tk_bearish | 44.6% |
| ichi_tk_bullish | 44.0% |
| ichi_tk_cross_dn | 2.7% |
| ichi_tk_cross_up | 1.7% |
| ichi_weekly_above_cloud | 40.8% |
| ichi_weekly_below_cloud | 35.7% |
| ichi_weekly_in_cloud | 23.6% |
| in_reversal_window | 1.0% |
| inside_bar | 21.0% |
| inside_cpr | 3.9% |
| inside_kc | 87.3% |
| insider_cluster_active | 11.2% |
| institutional_buy | 89.1% |
| institutional_negative | 4.4% |
| institutional_persistence_growing | 47.8% |
| institutional_persistence_strong | 63.0% |
| institutional_strong_buy | 79.3% |
| inverted_cup_handle_detected | 5.9% |
| is_friday | 17.0% |
| is_halloween_period | 50.7% |
| is_halloween_period_first_day | 0.9% |
| is_january | 7.7% |
| is_january_extended | 8.4% |
| is_monday | 18.9% |
| is_pre_holiday | 1.7% |
| is_summer_period | 49.3% |
| is_totm_window | 27.4% |
| is_totm_window_first_day | 8.3% |
| is_week_open | 20.8% |
| kc_touch_lower | 10.0% |
| kc_touch_upper | 9.7% |
| large_dollar_buy | 0.8% |
| macd_12_26_9_bearish | 50.1% |
| macd_12_26_9_bullish | 49.9% |
| macd_12_26_9_crossover_dn | 0.1% |
| macd_12_26_9_crossover_up | 0.2% |
| macd_8_21_5_bearish | 48.9% |
| macd_8_21_5_bullish | 51.1% |
| macd_8_21_5_crossover_dn | 0.6% |
| macd_8_21_5_crossover_up | 1.2% |
| marubozu_bear | 0.8% |
| marubozu_bull | 0.6% |
| mfi_broad_overbought | 16.8% |
| mfi_broad_oversold | 12.1% |
| mfi_overbought | 4.4% |
| mfi_oversold | 3.1% |
| monthly_above_sma_12 | 49.5% |
| monthly_above_sma_6 | 47.7% |
| monthly_bias_bear | 30.8% |
| monthly_bias_bull | 28.1% |
| monthly_momentum_pos | 51.2% |
| morning_star | 2.1% |
| near_52w_high_95pct | 1.7% |
| near_52w_high_retest_long | 1.2% |
| near_52w_low_105pct | 0.1% |
| near_52w_low_retest_short | 2.4% |
| near_avwap_20high_atr_05x | 37.4% |
| near_avwap_20high_atr_10x | 59.7% |
| near_avwap_20high_atr_15x | 78.1% |
| near_avwap_20high_atr_20x | 91.3% |
| near_avwap_20low_atr_05x | 35.6% |
| near_avwap_20low_atr_10x | 50.5% |
| near_avwap_20low_atr_15x | 67.3% |
| near_avwap_20low_atr_20x | 82.3% |
| near_avwap_252low_atr_05x | 5.9% |
| near_avwap_252low_atr_10x | 13.8% |
| near_avwap_252low_atr_15x | 26.6% |
| near_avwap_252low_atr_20x | 41.6% |
| near_avwap_50low_atr_05x | 18.5% |
| near_avwap_50low_atr_10x | 34.1% |
| near_avwap_50low_atr_15x | 52.2% |
| near_avwap_50low_atr_20x | 68.6% |
| near_cam_r3 | 11.7% |
| near_cam_s3 | 16.5% |
| near_cam_s4 | 11.5% |
| near_fib_236 | 5.0% |
| near_fib_382 | 5.8% |
| near_fib_500 | 8.1% |
| near_fib_618 | 7.6% |
| near_fib_786 | 5.1% |
| near_pivot | 18.5% |
| near_prev_close | 18.5% |
| near_prev_high | 9.9% |
| near_prev_low | 11.5% |
| near_r1 | 7.0% |
| near_r1_wide | 45.4% |
| near_r2 | 2.4% |
| near_r2_wide | 19.2% |
| near_s1 | 12.2% |
| near_s1_wide | 54.1% |
| near_s2 | 3.7% |
| near_s2_wide | 25.6% |
| near_s3 | 1.2% |
| near_wood_r1 | 12.3% |
| near_wood_s1 | 10.9% |
| news_uses_polygon_score | 26.9% |
| obv_bearish | 48.6% |
| obv_bullish | 51.4% |
| obv_diverge_bull | 9.6% |
| obv_falling | 46.2% |
| obv_rising | 53.8% |
| outside_bar | 10.7% |
| pead_negative_surprise | 17.1% |
| pead_positive_surprise | 24.1% |
| pin_bar | 12.9% |
| po3_accumulation_active | 12.7% |
| po3_bearish | 16.8% |
| po3_bullish | 10.0% |
| po3_manipulation_sweep_down | 2.8% |
| po3_manipulation_sweep_up | 1.7% |
| po3_mmbm_setup | 0.3% |
| po3_mmsm_setup | 0.9% |
| po3_sweep_above_prior_high | 49.3% |
| po3_sweep_below_prior_low | 46.3% |
| ppo_bullish | 49.8% |
| ppo_crossover_dn | 0.1% |
| ppo_crossover_up | 0.2% |
| pre_fomc_d0 | 2.7% |
| pre_fomc_d1 | 5.0% |
| pre_fomc_window | 7.6% |
| price_above_dema | 51.4% |
| price_above_ema_20 | 50.1% |
| price_above_ema_200 | 50.2% |
| price_above_ema_200_break_recent_5d | 11.1% |
| price_above_ema_20_break_recent_5d | 14.7% |
| price_above_ema_21 | 50.1% |
| price_above_ema_21_break_recent_5d | 15.0% |
| price_above_ema_50 | 49.0% |
| price_above_ema_50_break_recent_5d | 28.8% |
| price_above_ema_9 | 52.2% |
| price_above_ema_9_break_recent_5d | 17.7% |
| price_above_hull | 53.3% |
| price_above_sma_200 | 50.8% |
| price_above_sma_21 | 50.2% |
| price_above_sma_50 | 49.8% |
| price_above_tema | 52.3% |
| price_below_dema | 48.6% |
| price_below_hull | 46.7% |
| price_below_tema | 47.7% |
| psar_bullish | 50.1% |
| psar_flip_dn | 0.9% |
| psar_flip_up | 0.9% |
| r1_break_retest_long | 52.2% |
| recent_blowoff_at_r3 | 0.1% |
| recent_capitulation_at_s3 | 0.1% |
| resistance_break_retest | 40.0% |
| risk_off_regime_bond_signal | 17.6% |
| risk_off_regime_bond_signal_strong | 8.8% |
| risk_off_regime_gold_signal | 39.6% |
| risk_on_regime_bond_signal | 43.3% |
| risk_on_regime_bond_signal_strong | 20.3% |
| roc_positive | 50.0% |
| roc_turning_dn | 1.0% |
| roc_turning_up | 0.5% |
| rsi_14_bullish | 49.8% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_14_cross_dn_overbought_recent_3d | 6.7% |
| rsi_14_cross_up_oversold_recent_3d | 7.8% |
| rsi_14_overbought | 1.1% |
| rsi_14_oversold | 0.9% |
| rsi_14_rising | 42.8% |
| rsi_21_bullish | 49.8% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_21_cross_dn_overbought_recent_3d | 0.2% |
| rsi_21_cross_up_oversold_recent_3d | 0.3% |
| rsi_21_overbought | 0.2% |
| rsi_21_rising | 42.8% |
| rsi_2_bullish | 49.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 43.2% |
| rsi_2_cross_dn_overbought_recent_3d | 41.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 42.0% |
| rsi_2_cross_up_oversold_recent_3d | 38.5% |
| rsi_2_extreme_ob | 11.6% |
| rsi_2_extreme_os | 10.7% |
| rsi_2_overbought | 22.7% |
| rsi_2_oversold | 21.2% |
| rsi_2_rising | 42.8% |
| rsi_9_bullish | 50.2% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 4.5% |
| rsi_9_cross_dn_overbought_recent_3d | 24.0% |
| rsi_9_cross_up_extreme_os_recent_3d | 5.4% |
| rsi_9_cross_up_oversold_recent_3d | 26.4% |
| rsi_9_extreme_ob | 0.4% |
| rsi_9_extreme_os | 0.5% |
| rsi_9_overbought | 10.6% |
| rsi_9_oversold | 10.0% |
| rsi_9_rising | 42.8% |
| s1_break_retest_short | 50.4% |
| sc_13d_filed_within_30d | 1.8% |
| sc_13g_filed_within_30d | 2.4% |
| sector_outperforming_spy | 45.5% |
| sector_underperforming_spy | 54.5% |
| shooting_star | 5.4% |
| sma_20_50_bullish | 51.2% |
| sma_20_50_golden_cross | 2.0% |
| sma_50_200_bullish | 50.7% |
| sma_50_200_golden_cross | 0.1% |
| sma_9_21_bullish | 49.8% |
| sma_9_21_golden_cross | 1.9% |
| smc_bos_bearish | 8.8% |
| smc_bos_bullish | 13.0% |
| smc_bos_retest_long | 5.2% |
| smc_bos_retest_short | 3.7% |
| smc_breaker_block_bearish | 15.5% |
| smc_breaker_block_bullish | 24.1% |
| smc_choch_bearish | 3.0% |
| smc_choch_bullish | 2.7% |
| smc_equal_highs_swept | 3.3% |
| smc_equal_lows_swept | 3.8% |
| smc_fvg_bearish_active | 46.2% |
| smc_fvg_bullish_active | 46.9% |
| smc_fvg_retest_long_zone | 13.1% |
| smc_fvg_retest_short_zone | 9.0% |
| smc_in_discount_zone | 65.6% |
| smc_in_premium_zone | 65.1% |
| smc_inverse_fvg_bearish | 87.1% |
| smc_inverse_fvg_bullish | 89.0% |
| smc_liquidity_swept_dn | 1.8% |
| smc_liquidity_swept_up | 1.7% |
| smc_mitigation_block_long | 0.8% |
| smc_mitigation_block_short | 1.1% |
| smc_ob_bearish_active | 36.5% |
| smc_ob_bullish_active | 30.9% |
| smc_ote_long_zone | 9.6% |
| smc_ote_short_zone | 8.6% |
| squeeze_fire_dn | 1.0% |
| squeeze_fire_up | 1.9% |
| squeeze_in | 16.9% |
| squeeze_positive | 51.4% |
| stoch_bearish_cross | 17.1% |
| stoch_broad_overbought | 43.6% |
| stoch_broad_oversold | 35.9% |
| stoch_bullish_cross | 16.5% |
| stoch_overbought | 37.9% |
| stoch_oversold | 29.2% |
| stochrsi_cross_dn | 34.0% |
| stochrsi_cross_up | 31.2% |
| stochrsi_overbought | 30.2% |
| stochrsi_oversold | 28.2% |
| supertrend_bearish | 1.5% |
| supertrend_bullish | 98.5% |
| supertrend_flip_recent_long_5d | 4.5% |
| supertrend_flip_recent_short_5d | 4.9% |
| supertrend_flip_up | 2.2% |
| support_break_retest | 39.4% |
| tema_above_dema | 49.8% |
| tema_cross_dn | 0.2% |
| three_black_crows | 2.5% |
| three_white_soldiers | 1.3% |
| triangle_apex_break_retest_long | 12.7% |
| triangle_ascending_detected | 10.4% |
| triangle_descending_detected | 12.5% |
| uo_overbought | 2.5% |
| uo_oversold | 2.7% |
| usd_strengthening | 29.0% |
| usd_weakening | 9.8% |
| vix_band_high | 50.4% |
| vix_band_low | 16.8% |
| vix_band_mid | 32.8% |
| vix_term_backwardation | 11.0% |
| vix_term_contango | 89.0% |
| vol_above_avg | 40.4% |
| vol_below_avg | 59.6% |
| vol_spike_12x | 22.3% |
| vol_spike_15x | 9.8% |
| vol_spike_17x | 6.2% |
| vol_spike_2x | 2.5% |
| vol_spike_2x_on_down_day_recent_3d | 6.0% |
| vol_spike_2x_on_up_day_recent_3d | 5.4% |
| vol_spike_3x | 0.6% |
| vp_above_value_area | 20.0% |
| vp_below_value_area | 15.8% |
| vp_close_above_poc | 53.6% |
| vp_close_below_poc | 46.4% |
| vp_in_value_area | 64.2% |
| week_open_gap_down_15pct | 1.8% |
| week_open_gap_up_15pct | 1.7% |
| weekly_above_ema_10 | 49.3% |
| weekly_above_ema_20 | 48.0% |
| weekly_bias_bear | 31.6% |
| weekly_bias_bull | 28.8% |
| weekly_momentum_pos | 50.0% |
| williams_r_overbought | 25.7% |
| williams_r_oversold | 22.7% |
| williams_r_rising | 43.0% |
| within_pead_window | 39.0% |
| within_post_deletion_window | 7.4% |
| within_post_inclusion_window | 1.5% |
| within_pre_rebalance_window | 0.6% |
| xs_avoid_high_ivol | 71.8% |
| xs_avoid_high_max | 75.4% |
| xs_high_beta_decile | 26.9% |
| xs_low_beta_bottom_quintile | 26.9% |
| xs_low_beta_decile | 18.1% |
| xs_low_beta_decile_entry_recent_5d | 0.9% |
| xs_low_beta_top_quintile | 18.1% |
| xs_momentum_bottom_decile | 17.8% |
| xs_momentum_bottom_quintile | 29.7% |
| xs_momentum_top_decile | 15.9% |
| xs_momentum_top_quintile | 25.3% |
| xs_quality_bottom_quintile | 20.7% |
| xs_quality_top_quintile | 20.5% |
| xs_quality_top_tercile | 40.0% |
| yoy_surprise_high | 52.2% |
| yoy_surprise_negative | 38.0% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.2% |
| committed_growth_holders | 90.2% |
| corp_donations_1y | 9.2% |
| corp_donations_count_1y | 9.2% |
| corp_donations_unique_pacs | 9.2% |
| cot_rut_commercials_pctile_3y | 58.6% |
| cot_rut_mmoney_pctile_3y | 58.6% |
| cup_handle_depth_pct | 11.8% |
| days_since_classification_change | 0.2% |
| days_since_deletion | 8.4% |
| days_since_inclusion | 12.5% |
| days_to_next_holiday | 59.9% |
| days_to_rebalance | 10.3% |
| dpi_30d_avg | 95.3% |
| dpi_recent | 95.3% |
| earnings_announcement_return | 91.1% |
| earnings_eps_yoy_growth | 94.6% |
| gov_contracts_4q_sum | 39.6% |
| gov_contracts_last_qtr_amount | 39.6% |
| gov_contracts_qoq_growth | 39.6% |
| head_shoulders_magnitude_pct | 9.6% |
| insider_director_buyers_30d | 4.9% |
| insider_officer_buyers_30d | 4.9% |
| insider_total_shares_bought_30d | 4.9% |
| insider_unique_buyers_30d | 4.9% |
| inverted_cup_handle_height_pct | 11.5% |
| lobbying_amount_1y | 69.8% |
| lobbying_amount_q | 69.8% |
| lobbying_amount_yoy | 69.8% |
| monthly_momentum_6m | 96.5% |
| otc_short_ratio_recent | 95.3% |
| otc_volume_recent | 95.3% |
| pair_half_life | 91.7% |
| pair_max_abs_zscore | 91.7% |
| pair_zscore_signed | 91.7% |
| pct_from_avwap_20high | 83.2% |
| pct_from_avwap_20low | 88.7% |
| pct_from_avwap_252low | 96.7% |
| pct_from_avwap_50low | 96.5% |
| persistent_holders_4q | 90.2% |
| persistent_holders_8q | 90.2% |
| sc_13g_latest_percent_owned | 1.1% |
| search_volume_index_recent | 77.7% |
| search_volume_observations | 77.7% |
| search_volume_zscore_30d | 77.7% |
| sector_etf_return_20d | 2.7% |
| short_interest_pct | 98.0% |
| spy_return_20d | 2.7% |
| total_active_holders | 90.2% |
| triangle_breakdown_pct | 12.5% |
| triangle_breakout_pct | 10.4% |
| xs_quality_decile | 61.7% |
| xs_quality_gross_profitability | 61.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.994), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.997), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.997), `cam_s2` (0.997), `cam_s3` (0.996), `cam_s4` (0.996), `chandelier_long_value` (1.0), `chandelier_short_value` (1.0), `cpr_bottom` (0.997), `cpr_top` (0.997), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.997), `entry_stop_short` (0.997), `fib_236` (0.998), `fib_382` (0.998), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.999), `fib_ext_127` (0.995), `fib_ext_162` (0.993), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.998), `ichi_kijun` (1.0), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.998), `monthly_sma_12` (0.978), `monthly_sma_6` (0.995), `pivot` (0.997), `prev_close` (0.997), `prev_high` (0.997), `prev_low` (0.997), `psar_value` (0.999), `r1` (0.997), `r2` (0.997), `r3` (0.997), `s1` (0.996), `s2` (0.996), `s3` (0.995), `supertrend_value` (0.995), `swing_high` (0.997), `swing_low` (0.998), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.998), `vp_value_area_high` (0.998), `vp_value_area_low` (0.998), `weekly_close` (0.997), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.997), `wood_r1` (0.997), `wood_r2` (0.997), `wood_s1` (0.997), `wood_s2` (0.996), `year_high` (0.963), `year_low` (0.966)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
