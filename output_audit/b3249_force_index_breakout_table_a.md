# Table A - force_index_breakout

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build ff10274b7 | commit 352770ae3 at 2026-11-05 02:38:35 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** breakout | **status:** NOT-STARTED | **R5 fires:** 3013 (closed fires in the exit cube: 3013 of 3013, S6-B3258) | **surviving fires (T1):** 3013 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_ema_20  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define
P2  close_above_open  <- backtest/signals/technical.py
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P2.1-P2.1 (band rows in Table A)
P3  close_below_open  <- backtest/signals/technical.py
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P3.1-P3.1 (band rows in Table A)
P4  force_index_cross_dn  <- backtest/signals/technical.py
       DEFN: read the producer source (evidence column)
       knobs bands to define
P5  force_index_cross_up  <- backtest/signals/technical.py
       DEFN: read the producer source (evidence column)
       knobs bands to define
P6  price_above_ema_20  <- backtest/signals/technical.py (f-string template) +1
       DEFN: read the producer source (evidence column)
       knobs bands to define

============================== STRATEGY LAYER ==============================

P7  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_force_index_breakout (docstring and return dropped):

```python
fl = s.get('force_index_cross_up') and s.get('price_above_ema_20') and s.get('close_above_open')
fs = s.get('force_index_cross_dn') and s.get('below_ema_20') and s.get('close_below_open') and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | below_ema_20 - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P2 | PRODUCER | close_above_open - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P2.1 | BAND | (structural) c > o - optional min body pct - backtest/signals/technical.py bar-anatomy block | BRACKET zero | 0.0 | [0, 0.2, 0.5] pct | offline 0 of 3 levels - none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | close_below_open - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P3.1 | BAND | mirror of close_above_open - technical.py bar-anatomy block | mirror | 0.0 | [0, 0.2, 0.5] pct | offline 0 of 3 levels - none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | force_index_cross_dn - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P5 | PRODUCER | force_index_cross_up - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P6 | PRODUCER | price_above_ema_20 - emitted by backtest/signals/technical.py (f-string template) +1; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P7 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
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
| adx | backtest/signals/technical.py | 100.0% | 15.486, 18.978, 22.92, 28.37 | 15.486: 2410 (80%); 18.978: 1808 (60%); 22.92: 1206 (40%); 28.37: 605 (20%) | 15.486: 603 (20%); 18.978: 1205 (40%); 22.92: 1809 (60%); 28.37: 2411 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 20.6, 23.07, 25.23, 27.756 | 20.6: 2411 (80%); 23.07: 1812 (60%); 25.23: 1207 (40%); 27.756: 603 (20%) | 20.6: 605 (20%); 23.07: 1206 (40%); 25.23: 1809 (60%); 27.756: 2410 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.9, 21.378, 23.412, 26.06 | 18.9: 2411 (80%); 21.378: 1808 (60%); 23.412: 1205 (40%); 26.06: 605 (20%) | 18.9: 605 (20%); 21.378: 1205 (40%); 23.412: 1808 (60%); 26.06: 2412 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -4.3995, -1.2926, 0.2682, 2.8142 | -4.3995: 2410 (80%); -1.2926: 1808 (60%); 0.2682: 1206 (40%); 2.8142: 603 (20%) | -4.3995: 603 (20%); -1.2926: 1205 (40%); 0.2682: 1808 (60%); 2.8142: 2410 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.2141, 2.1028, 3.5707, 6.4351 | 1.2141: 2410 (80%); 2.1028: 1808 (60%); 3.5707: 1205 (40%); 6.4351: 603 (20%) | 1.2141: 603 (20%); 2.1028: 1205 (40%); 3.5707: 1808 (60%); 6.4351: 2410 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.2141, 2.1028, 3.5707, 6.4351 | 1.2141: 2410 (80%); 2.1028: 1808 (60%); 3.5707: 1205 (40%); 6.4351: 603 (20%) | 1.2141: 603 (20%); 2.1028: 1205 (40%); 3.5707: 1808 (60%); 6.4351: 2410 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.0762, 2.539, 3.1124, 4.0916 | 2.0762: 2410 (80%); 2.539: 1809 (60%); 3.1124: 1205 (40%); 4.0916: 603 (20%) | 2.0762: 603 (20%); 2.539: 1207 (40%); 3.1124: 1808 (60%); 4.0916: 2410 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0468, 0.0648, 0.0869, 0.127 | 0.0468: 2411 (80%); 0.0648: 1809 (60%); 0.0869: 1207 (40%); 0.127: 604 (20%) | 0.0468: 607 (20%); 0.0648: 1209 (40%); 0.0869: 1809 (60%); 0.127: 2411 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1579, 0.3687, 0.5648, 0.8061 | 0.1579: 2410 (80%); 0.3687: 1808 (60%); 0.5648: 1205 (40%); 0.8061: 603 (20%) | 0.1579: 603 (20%); 0.3687: 1205 (40%); 0.5648: 1808 (60%); 0.8061: 2410 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0516, 0.0702, 0.0951, 0.1346 | 0.0516: 2412 (80%); 0.0702: 1810 (60%); 0.0951: 1207 (40%); 0.1346: 603 (20%) | 0.0516: 608 (20%); 0.0702: 1208 (40%); 0.0951: 1811 (60%); 0.1346: 2411 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2157, 0.3886, 0.521, 0.6836 | 0.2157: 2410 (80%); 0.3886: 1808 (60%); 0.521: 1206 (40%); 0.6836: 603 (20%) | 0.2157: 603 (20%); 0.3886: 1205 (40%); 0.521: 1809 (60%); 0.6836: 2411 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0688, 0.0936, 0.1268, 0.1794 | 0.0688: 2412 (80%); 0.0936: 1808 (60%); 0.1268: 1207 (40%); 0.1794: 604 (20%) | 0.0688: 607 (20%); 0.0936: 1208 (40%); 0.1268: 1810 (60%); 0.1794: 2411 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2868, 0.4165, 0.5157, 0.6377 | 0.2868: 2410 (80%); 0.4165: 1808 (60%); 0.5157: 1206 (40%); 0.6377: 603 (20%) | 0.2868: 603 (20%); 0.4165: 1205 (40%); 0.5157: 1808 (60%); 0.6377: 2411 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0488, -0.0226, -0.0016, 0.0218 | -0.0488: 2424 (80%); -0.0226: 1816 (60%); -0.0016: 1206 (40%); 0.0218: 603 (20%) | -0.0488: 609 (20%); -0.0226: 1207 (40%); -0.0016: 1817 (60%); 0.0218: 2410 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1441, 0.1653, 0.208, 0.2688 | 0.1441: 2404 (80%); 0.1653: 1808 (60%); 0.208: 1200 (40%); 0.2688: 612 (20%) | 0.1441: 609 (20%); 0.1653: 1205 (40%); 0.208: 1813 (60%); 0.2688: 2401 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 3013 (100%) | 0: 2863 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0905, -0.0186, 0.0468, 0.1207 | -0.0905: 2410 (80%); -0.0186: 1810 (60%); 0.0468: 1206 (40%); 0.1207: 603 (20%) | -0.0905: 603 (20%); -0.0186: 1206 (40%); 0.0468: 1810 (60%); 0.1207: 2412 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 3013 (100%); 1: 1142 (38%) | 0: 1871 (62%); 1: 2498 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.236, -0.1872, -0.1508, -0.1141 | -0.236: 2421 (80%); -0.1872: 1815 (60%); -0.1508: 1205 (40%); -0.1141: 617 (20%) | -0.236: 605 (20%); -0.1872: 1209 (40%); -0.1508: 1808 (60%); -0.1141: 2557 (85%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4167, 0.6154, 0.6923, 0.7692 | 0.4167: 2416 (80%); 0.6154: 1811 (60%); 0.6923: 1254 (42%); 0.7692: 720 (24%) | 0.4167: 638 (21%); 0.6154: 1213 (40%); 0.6923: 1817 (60%); 0.7692: 2493 (83%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.3692, 0.5962, 0.8269 | 0.2628: 2485 (82%); 0.3692: 1808 (60%); 0.5962: 1217 (40%); 0.8269: 656 (22%) | 0.2628: 614 (20%); 0.3692: 1205 (40%); 0.5962: 1818 (60%); 0.8269: 2414 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0921, -0.0065, 0.0833, 0.2246 | -0.0921: 2431 (81%); -0.0065: 1818 (60%); 0.0833: 1213 (40%); 0.2246: 606 (20%) | -0.0921: 606 (20%); -0.0065: 1225 (41%); 0.0833: 1816 (60%); 0.2246: 2424 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2692, 0.4679, 0.5962, 0.8013 | 0.2692: 2413 (80%); 0.4679: 1853 (62%); 0.5962: 1208 (40%); 0.8013: 630 (21%) | 0.2692: 627 (21%); 0.4679: 1224 (41%); 0.5962: 1820 (60%); 0.8013: 2412 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.141, 0.3526, 0.4679, 0.641 | 0.141: 2413 (80%); 0.3526: 1819 (60%); 0.4679: 1213 (40%); 0.641: 614 (20%) | 0.141: 610 (20%); 0.3526: 1317 (44%); 0.4679: 1829 (61%); 0.641: 2413 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.497, -0.3438, -0.1616, 0.0612 | -0.497: 2477 (82%); -0.3438: 1813 (60%); -0.1616: 1213 (40%); 0.0612: 610 (20%) | -0.497: 663 (22%); -0.3438: 1217 (40%); -0.1616: 1814 (60%); 0.0612: 2416 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3846, 0.5179, 0.75, 0.9167 | 0.3846: 2437 (81%); 0.5179: 1808 (60%); 0.75: 1215 (40%); 0.9167: 666 (22%) | 0.3846: 633 (21%); 0.5179: 1205 (40%); 0.75: 1815 (60%); 0.9167: 2444 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3141, 0.5833, 0.8462 | 0.1474: 2427 (81%); 0.3141: 1829 (61%); 0.5833: 1216 (40%); 0.8462: 616 (20%) | 0.1474: 633 (21%); 0.3141: 1231 (41%); 0.5833: 1833 (61%); 0.8462: 2412 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0665, -0.0587, -0.0388, 0 | -0.0665: 2416 (80%); -0.0587: 1808 (60%); -0.0388: 1212 (40%); 0: 891 (30%) | -0.0665: 612 (20%); -0.0587: 1211 (40%); -0.0388: 1869 (62%); 0: 2943 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4359, 0.7179, 0.891, 1 | 0.4359: 2412 (80%); 0.7179: 1810 (60%); 0.891: 1217 (40%); 1: 719 (24%) | 0.4359: 620 (21%); 0.7179: 1217 (40%); 0.891: 1836 (61%); 1: 3013 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1218, 0.2372, 0.5128, 0.8526 | 0.1218: 2426 (81%); 0.2372: 1812 (60%); 0.5128: 1214 (40%); 0.8526: 614 (20%) | 0.1218: 607 (20%); 0.2372: 1209 (40%); 0.5128: 1824 (61%); 0.8526: 2415 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0064, 0.0324, 0.0842, 0.2309 | 0.0064: 2414 (80%); 0.0324: 1808 (60%); 0.0842: 1205 (40%); 0.2309: 622 (21%) | 0.0064: 620 (21%); 0.0324: 1208 (40%); 0.0842: 1808 (60%); 0.2309: 2421 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.5211, 0.7815, 0.9351, 0.9744 | 0.5211: 2417 (80%); 0.7815: 1825 (61%); 0.9351: 1288 (43%); 0.9744: 696 (23%) | 0.5211: 607 (20%); 0.7815: 1208 (40%); 0.9351: 1852 (61%); 0.9744: 2557 (85%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0962, 0.2436, 0.4966, 0.7664 | 0.0962: 2438 (81%); 0.2436: 1811 (60%); 0.4966: 1213 (40%); 0.7664: 605 (20%) | 0.0962: 605 (20%); 0.2436: 1207 (40%); 0.4966: 1809 (60%); 0.7664: 2414 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0132, 0.1131, 0.1876 | -0.0812: 2539 (84%); -0.0132: 1814 (60%); 0.1131: 1211 (40%); 0.1876: 648 (22%) | -0.0812: 748 (25%); -0.0132: 1208 (40%); 0.1131: 1809 (60%); 0.1876: 2443 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1856, -0.0125, 0.0444, 0.0869 | -0.1856: 2410 (80%); -0.0125: 1812 (60%); 0.0444: 1234 (41%); 0.0869: 604 (20%) | -0.1856: 603 (20%); -0.0125: 1215 (40%); 0.0444: 1826 (61%); 0.0869: 2437 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2821, 0.5705, 0.75, 0.8782 | 0.2821: 2422 (80%); 0.5705: 1852 (61%); 0.75: 1239 (41%); 0.8782: 608 (20%) | 0.2821: 604 (20%); 0.5705: 1251 (42%); 0.75: 1901 (63%); 0.8782: 2450 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3782, 0.5641, 0.8115 | 0.1474: 2412 (80%); 0.3782: 1843 (61%); 0.5641: 1313 (44%); 0.8115: 603 (20%) | 0.1474: 650 (22%); 0.3782: 1247 (41%); 0.5641: 1904 (63%); 0.8115: 2410 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0517, 0.1275, 0.2583, 0.5678 | 0.0517: 2413 (80%); 0.1275: 1809 (60%); 0.2583: 1206 (40%); 0.5678: 603 (20%) | 0.0517: 611 (20%); 0.1275: 1206 (40%); 0.2583: 1810 (60%); 0.5678: 2410 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.3% | 29, 62, 83, 149 | 29: 2374 (79%); 62: 1810 (60%); 83: 1197 (40%); 149: 597 (20%) | 29: 612 (20%); 62: 1206 (40%); 83: 1786 (59%); 149: 2374 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.5% | 1.7704, 2.2925, 2.851, 3.7482 | 1.7704: 2399 (80%); 2.2925: 1799 (60%); 2.851: 1200 (40%); 3.7482: 600 (20%) | 1.7704: 600 (20%); 2.2925: 1200 (40%); 2.851: 1799 (60%); 3.7482: 2399 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 20, 27, 34 | 9: 2448 (81%); 20: 1847 (61%); 27: 1352 (45%); 34: 643 (21%) | 9: 620 (21%); 20: 1274 (42%); 27: 1823 (61%); 34: 2452 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3 | 1: 2559 (85%); 2: 1959 (65%); 3: 1312 (44%) | 1: 1054 (35%); 2: 1701 (56%); 3: 2433 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0138, -0.0033, 0.0117, 0.0247 | -0.0138: 2413 (80%); -0.0033: 1809 (60%); 0.0117: 1208 (40%); 0.0247: 603 (20%) | -0.0138: 608 (20%); -0.0033: 1214 (40%); 0.0117: 1833 (61%); 0.0247: 2415 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5181, 25.751, 26.5341, 27.2416 | 24.5181: 2414 (80%); 25.751: 1808 (60%); 26.5341: 1205 (40%); 27.2416: 603 (20%) | 24.5181: 604 (20%); 25.751: 1205 (40%); 26.5341: 1808 (60%); 27.2416: 2410 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.705, -0.107, 0.3032, 1.035 | -0.705: 2411 (80%); -0.107: 1809 (60%); 0.3032: 1205 (40%); 1.035: 604 (20%) | -0.705: 604 (20%); -0.107: 1207 (40%); 0.3032: 1808 (60%); 1.035: 2411 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -1.035, -0.3032, 0.107, 0.705 | -1.035: 2411 (80%); -0.3032: 1808 (60%); 0.107: 1207 (40%); 0.705: 604 (20%) | -1.035: 604 (20%); -0.3032: 1205 (40%); 0.107: 1809 (60%); 0.705: 2411 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0449, -0.0041, 0.026, 0.0666 | -0.0449: 2415 (80%); -0.0041: 1808 (60%); 0.026: 1218 (40%); 0.0666: 605 (20%) | -0.0449: 606 (20%); -0.0041: 1211 (40%); 0.026: 1809 (60%); 0.0666: 2411 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0712, 8.4752, 8.7889, 9.2219 | 8.0712: 2418 (80%); 8.4752: 1808 (60%); 8.7889: 1200 (40%); 9.2219: 604 (20%) | 8.0712: 595 (20%); 8.4752: 1205 (40%); 8.7889: 1813 (60%); 9.2219: 2409 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 2990 (99%); 1: 958 (32%) | 0: 2032 (67%); 1: 2666 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.2% | -1, 0 | -1: 2839 (94%); 0: 2365 (78%) | -1: 625 (21%); 0: 2483 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 2990 (99%); 1: 1033 (34%) | 0: 1957 (65%); 1: 2620 (87%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 121, 274 | 3: 2416 (80%); 6: 1834 (61%); 121: 1206 (40%); 274: 604 (20%) | 3: 823 (27%); 6: 1321 (44%); 121: 1810 (60%); 274: 2416 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 4, 83, 139 | 1: 2452 (81%); 4: 1862 (62%); 83: 1213 (40%); 139: 610 (20%) | 1: 798 (26%); 4: 1247 (41%); 83: 1814 (60%); 139: 2415 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.3891, -0.0786, 0.1017, 0.4383 | -0.3891: 2410 (80%); -0.0786: 1808 (60%); 0.1017: 1205 (40%); 0.4383: 603 (20%) | -0.3891: 603 (20%); -0.0786: 1206 (40%); 0.1017: 1808 (60%); 0.4383: 2410 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.7602, -0.5451, 0.0817, 1.0642 | -1.7602: 2410 (80%); -0.5451: 1808 (60%); 0.0817: 1206 (40%); 1.0642: 603 (20%) | -1.7602: 603 (20%); -0.5451: 1205 (40%); 0.0817: 1808 (60%); 1.0642: 2410 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.0453, -0.6441, 0.0806, 1.264 | -2.0453: 2410 (80%); -0.6441: 1808 (60%); 0.0806: 1205 (40%); 1.264: 603 (20%) | -2.0453: 603 (20%); -0.6441: 1206 (40%); 0.0806: 1808 (60%); 1.264: 2410 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.3791, -0.0693, 0.1253, 0.4264 | -0.3791: 2410 (80%); -0.0693: 1808 (60%); 0.1253: 1206 (40%); 0.4264: 603 (20%) | -0.3791: 603 (20%); -0.0693: 1205 (40%); 0.1253: 1808 (60%); 0.4264: 2411 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.4619, -0.4294, 0.0802, 0.89 | -1.4619: 2410 (80%); -0.4294: 1808 (60%); 0.0802: 1205 (40%); 0.89: 603 (20%) | -1.4619: 603 (20%); -0.4294: 1206 (40%); 0.0802: 1808 (60%); 0.89: 2410 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.8198, -0.568, 0.0987, 1.194 | -1.8198: 2410 (80%); -0.568: 1808 (60%); 0.0987: 1205 (40%); 1.194: 603 (20%) | -1.8198: 603 (20%); -0.568: 1206 (40%); 0.0987: 1808 (60%); 1.194: 2410 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 40.06, 46.698, 52.792, 59.382 | 40.06: 2411 (80%); 46.698: 1808 (60%); 52.792: 1205 (40%); 59.382: 603 (20%) | 40.06: 604 (20%); 46.698: 1205 (40%); 52.792: 1808 (60%); 59.382: 2410 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.4% | 0.0049, 0.0111, 0.0206, 0.0375 | 0.0049: 2390 (79%); 0.0111: 1799 (60%); 0.0206: 1197 (40%); 0.0375: 600 (20%) | 0.0049: 606 (20%); 0.0111: 1197 (40%); 0.0206: 1799 (60%); 0.0375: 2396 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 3013 (100%); 1: 2224 (74%); 3: 1424 (47%); 8: 654 (22%) | 0: 789 (26%); 1: 1285 (43%); 3: 1826 (61%); 8: 2436 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1568 | 0: 3013 (100%); 0.1568: 603 (20%) | 0: 2067 (69%); 0.1568: 2410 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1053, 0.4055, 0.6667 | 0: 3013 (100%); 0.1053: 1809 (60%); 0.4055: 1205 (40%); 0.6667: 644 (21%) | 0: 1195 (40%); 0.1053: 1206 (40%); 0.4055: 1808 (60%); 0.6667: 2468 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 3013 (100%); 1: 2034 (68%); 2: 1516 (50%); 6: 653 (22%) | 0: 979 (32%); 1: 1497 (50%); 2: 1838 (61%); 6: 2468 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 3013 (100%); 1: 2224 (74%); 3: 1424 (47%); 8: 654 (22%) | 0: 789 (26%); 1: 1285 (43%); 3: 1826 (61%); 8: 2436 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 3013 (100%); 1: 2077 (69%); 3: 1293 (43%); 7: 652 (22%) | 0: 936 (31%); 1: 1399 (46%); 3: 1975 (66%); 7: 2453 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.221, 0.3744, 0.5899 | 0: 2813 (93%); 0.221: 1808 (60%); 0.3744: 1205 (40%); 0.5899: 603 (20%) | 0: 676 (22%); 0.221: 1205 (40%); 0.3744: 1808 (60%); 0.5899: 2410 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1304, 0.5556 | 0: 2724 (90%); 0.1304: 1206 (40%); 0.5556: 609 (20%) | 0: 1693 (56%); 0.1304: 1809 (60%); 0.5556: 2415 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2894, 0.5865 | 0: 2762 (92%); 0.2894: 1205 (40%); 0.5865: 603 (20%) | 0: 1363 (45%); 0.2894: 1808 (60%); 0.5865: 2410 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2894, 0.5865 | 0: 2762 (92%); 0.2894: 1205 (40%); 0.5865: 603 (20%) | 0: 1363 (45%); 0.2894: 1808 (60%); 0.5865: 2410 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1544, 0, 0.1333 | -0.1544: 2410 (80%); 0: 2191 (73%); 0.1333: 605 (20%) | -0.1544: 603 (20%); 0: 2196 (73%); 0.1333: 2414 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7345, -0.2781, 0.1028, 1.2781 | -0.7345: 2411 (80%); -0.2781: 1808 (60%); 0.1028: 1207 (40%); 1.2781: 603 (20%) | -0.7345: 604 (20%); -0.2781: 1205 (40%); 0.1028: 1809 (60%); 1.2781: 2410 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 2537 (84%); 4: 1981 (66%); 7: 1291 (43%); 11: 637 (21%) | 2: 754 (25%); 4: 1265 (42%); 7: 1910 (63%); 11: 2477 (82%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0317, -0.01, 0.0057, 0.0262 | -0.0317: 2411 (80%); -0.01: 1809 (60%); 0.0057: 1206 (40%); 0.0262: 603 (20%) | -0.0317: 602 (20%); -0.01: 1204 (40%); 0.0057: 1807 (60%); 0.0262: 2410 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0531, -0.0205, 0.0054, 0.0356 | -0.0531: 2410 (80%); -0.0205: 1806 (60%); 0.0054: 1205 (40%); 0.0356: 602 (20%) | -0.0531: 603 (20%); -0.0205: 1207 (40%); 0.0054: 1808 (60%); 0.0356: 2411 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0321, -0.0119, 0.0057, 0.0292 | -0.0321: 2410 (80%); -0.0119: 1809 (60%); 0.0057: 1204 (40%); 0.0292: 603 (20%) | -0.0321: 603 (20%); -0.0119: 1204 (40%); 0.0057: 1809 (60%); 0.0292: 2410 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/technical.py (f-string template) | 98.2% | -0.2664, 0.991, 2.2318, 4.2348 | -0.2664: 2367 (79%); 0.991: 1776 (59%); 2.2318: 1184 (39%); 4.2348: 592 (20%) | -0.2664: 592 (20%); 0.991: 1185 (39%); 2.2318: 1775 (59%); 4.2348: 2367 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -18.8766, -6.72, 5.112, 24.8908 | -18.8766: 2410 (80%); -6.72: 1809 (60%); 5.112: 1205 (40%); 24.8908: 603 (20%) | -18.8766: 603 (20%); -6.72: 1206 (40%); 5.112: 1808 (60%); 24.8908: 2410 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0369, 0.0484, 0.0618, 0.0888 | 0.0369: 2414 (80%); 0.0484: 1808 (60%); 0.0618: 1208 (40%); 0.0888: 603 (20%) | 0.0369: 605 (20%); 0.0484: 1206 (40%); 0.0618: 1812 (60%); 0.0888: 2412 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1183, 0.287, 0.5637, 0.8427 | 0.1183: 2411 (80%); 0.287: 1808 (60%); 0.5637: 1205 (40%); 0.8427: 603 (20%) | 0.1183: 603 (20%); 0.287: 1206 (40%); 0.5637: 1808 (60%); 0.8427: 2411 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.8464, -0.8238, 0.1105, 1.1102 | -1.8464: 2410 (80%); -0.8238: 1808 (60%); 0.1105: 1205 (40%); 1.1102: 603 (20%) | -1.8464: 603 (20%); -0.8238: 1205 (40%); 0.1105: 1808 (60%); 1.1102: 2410 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.3968, -0.1232, 0.1467, 0.4544 | -0.3968: 2410 (80%); -0.1232: 1808 (60%); 0.1467: 1205 (40%); 0.4544: 603 (20%) | -0.3968: 603 (20%); -0.1232: 1205 (40%); 0.1467: 1808 (60%); 0.4544: 2410 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -2.1669, -0.9763, 0.1245, 1.3259 | -2.1669: 2410 (80%); -0.9763: 1808 (60%); 0.1245: 1206 (40%); 1.3259: 603 (20%) | -2.1669: 603 (20%); -0.9763: 1205 (40%); 0.1245: 1808 (60%); 1.3259: 2410 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -3.5726, -1.2324, 0.485, 2.6462 | -3.5726: 2410 (80%); -1.2324: 1808 (60%); 0.485: 1206 (40%); 2.6462: 603 (20%) | -3.5726: 603 (20%); -1.2324: 1205 (40%); 0.485: 1809 (60%); 2.6462: 2410 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 44.44, 48.108, 49.99, 52.1 | 44.44: 2414 (80%); 48.108: 1808 (60%); 49.99: 1207 (40%); 52.1: 605 (20%) | 44.44: 605 (20%); 48.108: 1205 (40%); 49.99: 1809 (60%); 52.1: 2411 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 12.398, 26.422, 53.476, 85.676 | 12.398: 2410 (80%); 26.422: 1808 (60%); 53.476: 1205 (40%); 85.676: 603 (20%) | 12.398: 603 (20%); 26.422: 1205 (40%); 53.476: 1808 (60%); 85.676: 2410 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 44.784, 47.748, 50.052, 52.52 | 44.784: 2410 (80%); 47.748: 1808 (60%); 50.052: 1205 (40%); 52.52: 604 (20%) | 44.784: 603 (20%); 47.748: 1205 (40%); 50.052: 1808 (60%); 52.52: 2411 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 42.114, 46.02, 50.318, 55.038 | 42.114: 2410 (80%); 46.02: 1810 (60%); 50.318: 1205 (40%); 55.038: 603 (20%) | 42.114: 603 (20%); 46.02: 1207 (40%); 50.318: 1808 (60%); 55.038: 2410 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 3009 (100%) | 0: 3013 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0312, 0.0455, 0.0602, 0.0927 | 0.0312: 2417 (80%); 0.0455: 1809 (60%); 0.0602: 1208 (40%); 0.0927: 603 (20%) | 0.0312: 604 (20%); 0.0455: 1209 (40%); 0.0602: 1808 (60%); 0.0927: 2410 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0772, -0.0561, -0.0434, -0.0347 | -0.0772: 2411 (80%); -0.0561: 1813 (60%); -0.0434: 1280 (42%); -0.0347: 611 (20%) | -0.0772: 604 (20%); -0.0561: 1208 (40%); -0.0434: 1812 (60%); -0.0347: 2417 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 3013 (100%); 1: 909 (30%) | 0: 2104 (70%); 1: 2412 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.5% | 24, 40, 58, 68 | 24: 2476 (82%); 40: 1816 (60%); 58: 1213 (40%); 68: 618 (21%) | 24: 646 (21%); 40: 1201 (40%); 58: 1816 (60%); 68: 2462 (82%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.5% | 0.0118, 0.0173, 0.0249, 0.0395 | 0.0118: 2379 (79%); 0.0173: 1778 (59%); 0.0249: 1189 (39%); 0.0395: 592 (20%) | 0.0118: 588 (20%); 0.0173: 1189 (39%); 0.0249: 1778 (59%); 0.0395: 2375 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 99.9% | 0.2492, 0.366, 0.5179, 0.6699 | 0.2492: 2410 (80%); 0.366: 1807 (60%); 0.5179: 1205 (40%); 0.6699: 603 (20%) | 0.2492: 604 (20%); 0.366: 1205 (40%); 0.5179: 1807 (60%); 0.6699: 2409 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 99.9% | 30.1, 56.4, 85.9, 133.8 | 30.1: 2410 (80%); 56.4: 1809 (60%); 85.9: 1205 (40%); 133.8: 604 (20%) | 30.1: 606 (20%); 56.4: 1206 (40%); 85.9: 1807 (60%); 133.8: 2410 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -2.729, -0.76, 0.108, 1.405 | -2.729: 2410 (80%); -0.76: 1811 (60%); 0.108: 1205 (40%); 1.405: 604 (20%) | -2.729: 603 (20%); -0.76: 1208 (40%); 0.108: 1808 (60%); 1.405: 2411 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 30.122, 43.61, 55.75, 70.942 | 30.122: 2410 (80%); 43.61: 1810 (60%); 55.75: 1205 (40%); 70.942: 603 (20%) | 30.122: 603 (20%); 43.61: 1206 (40%); 55.75: 1808 (60%); 70.942: 2410 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 36.102, 45.548, 55.182, 65.73 | 36.102: 2410 (80%); 45.548: 1808 (60%); 55.182: 1205 (40%); 65.73: 604 (20%) | 36.102: 603 (20%); 45.548: 1205 (40%); 55.182: 1808 (60%); 65.73: 2411 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 19.68, 41.506, 64.392, 85.21 | 19.68: 2411 (80%); 41.506: 1808 (60%); 64.392: 1205 (40%); 85.21: 603 (20%) | 19.68: 604 (20%); 41.506: 1205 (40%); 64.392: 1808 (60%); 85.21: 2410 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 7.128, 38.126, 64.374, 93.356 | 7.128: 2410 (80%); 38.126: 1808 (60%); 64.374: 1205 (40%); 93.356: 603 (20%) | 7.128: 603 (20%); 38.126: 1205 (40%); 64.374: 1808 (60%); 93.356: 2410 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 11, 17 | 4: 2507 (83%); 7: 1942 (64%); 11: 1282 (43%); 17: 639 (21%) | 4: 784 (26%); 7: 1292 (43%); 11: 1834 (61%); 17: 2508 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 11, 15, 18 | 5: 2513 (83%); 11: 1809 (60%); 15: 1289 (43%); 18: 778 (26%) | 5: 639 (21%); 11: 1315 (44%); 15: 1930 (64%); 18: 2529 (84%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 44.554, 48.728, 52.06, 55.75 | 44.554: 2410 (80%); 48.728: 1808 (60%); 52.06: 1209 (40%); 55.75: 605 (20%) | 44.554: 603 (20%); 48.728: 1205 (40%); 52.06: 1809 (60%); 55.75: 2412 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1841, 0.4722, 0.7302, 0.9206 | 0.1841: 2410 (80%); 0.4722: 1817 (60%); 0.7302: 1229 (41%); 0.9206: 608 (20%) | 0.1841: 603 (20%); 0.4722: 1207 (40%); 0.7302: 1812 (60%); 0.9206: 2438 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.42, 18.21, 21.78, 27.44 | 15.42: 2412 (80%); 18.21: 1811 (60%); 21.78: 1207 (40%); 27.44: 605 (20%) | 15.42: 604 (20%); 18.21: 1208 (40%); 21.78: 1818 (60%); 27.44: 2415 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 15.42, 18.21, 21.78, 27.44 | 15.42: 2412 (80%); 18.21: 1811 (60%); 21.78: 1207 (40%); 27.44: 605 (20%) | 15.42: 604 (20%); 18.21: 1208 (40%); 21.78: 1818 (60%); 27.44: 2415 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8623, 0.8976, 0.9348, 0.9769 | 0.8623: 2411 (80%); 0.8976: 1809 (60%); 0.9348: 1211 (40%); 0.9769: 614 (20%) | 0.8623: 605 (20%); 0.8976: 1206 (40%); 0.9348: 1813 (60%); 0.9769: 2413 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.75, 0.89, 1.03, 1.35 | 0.75: 2436 (81%); 0.89: 1843 (61%); 1.03: 1239 (41%); 1.35: 615 (20%) | 0.75: 611 (20%); 0.89: 1222 (41%); 1.03: 1809 (60%); 1.35: 2412 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0103, 0.0241, 0.048, 0.0887 | 0.0103: 2413 (80%); 0.0241: 1809 (60%); 0.048: 1206 (40%); 0.0887: 603 (20%) | 0.0103: 607 (20%); 0.0241: 1206 (40%); 0.048: 1809 (60%); 0.0887: 2413 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 45.6662, 76.8377, 121.1674, 205.2399 | 45.6662: 2410 (80%); 76.8377: 1808 (60%); 121.1674: 1205 (40%); 205.2399: 603 (20%) | 45.6662: 603 (20%); 76.8377: 1205 (40%); 121.1674: 1808 (60%); 205.2399: 2410 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.918, 74.4138, 116.2791, 198.2608 | 43.918: 2410 (80%); 74.4138: 1808 (60%); 116.2791: 1205 (40%); 198.2608: 603 (20%) | 43.918: 603 (20%); 74.4138: 1205 (40%); 116.2791: 1808 (60%); 198.2608: 2410 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 42.1726, 71.8203, 112.8502, 191.5395 | 42.1726: 2410 (80%); 71.8203: 1808 (60%); 112.8502: 1205 (40%); 191.5395: 603 (20%) | 42.1726: 603 (20%); 71.8203: 1205 (40%); 112.8502: 1808 (60%); 191.5395: 2410 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.0395, 78.641, 124.5821, 211.2504 | 47.0395: 2410 (80%); 78.641: 1808 (60%); 124.5821: 1205 (40%); 211.2504: 603 (20%) | 47.0395: 603 (20%); 78.641: 1205 (40%); 124.5821: 1808 (60%); 211.2504: 2410 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.7393, 81.0486, 129.1042, 217.9189 | 48.7393: 2410 (80%); 81.0486: 1808 (60%); 129.1042: 1205 (40%); 217.9189: 603 (20%) | 48.7393: 603 (20%); 81.0486: 1205 (40%); 129.1042: 1808 (60%); 217.9189: 2410 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 3013 (100%) | 0: 2721 (90%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 3013 (100%) | 0: 2788 (93%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.9% | -0.0484, -0.0175, 0.0034, 0.0313 | -0.0484: 2409 (80%); -0.0175: 1811 (60%); 0.0034: 1208 (40%); 0.0313: 605 (20%) | -0.0484: 603 (20%); -0.0175: 1205 (40%); 0.0034: 1807 (60%); 0.0313: 2410 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -75.462, -59.294, -45.504, -29.364 | -75.462: 2410 (80%); -59.294: 1808 (60%); -45.504: 1205 (40%); -29.364: 603 (20%) | -75.462: 603 (20%); -59.294: 1205 (40%); -45.504: 1808 (60%); -29.364: 2410 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.3% | 0.5648, 0.8563, 1.0667, 1.3666 | 0.5648: 2393 (79%); 0.8563: 1796 (60%); 1.0667: 1197 (40%); 1.3666: 599 (20%) | 0.5648: 599 (20%); 0.8563: 1198 (40%); 1.0667: 1796 (60%); 1.3666: 2394 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 2516 (84%); 5: 2004 (67%); 7: 1451 (48%); 9: 826 (27%) | 3: 708 (23%); 5: 1244 (41%); 7: 1844 (61%); 9: 2536 (84%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.3% | 0.1924, 0.2347, 0.2839, 0.3679 | 0.1924: 2393 (79%); 0.2347: 1796 (60%); 0.2839: 1198 (40%); 0.3679: 600 (20%) | 0.1924: 599 (20%); 0.2347: 1198 (40%); 0.2839: 1795 (60%); 0.3679: 2393 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 2520 (84%); 5: 2009 (67%); 7: 1469 (49%); 9: 868 (29%) | 3: 711 (24%); 5: 1247 (41%); 7: 1812 (60%); 9: 2530 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.3% | 0.0237, 0.0326, 0.0435, 0.0659 | 0.0237: 2394 (79%); 0.0326: 1799 (60%); 0.0435: 1197 (40%); 0.0659: 601 (20%) | 0.0237: 603 (20%); 0.0326: 1199 (40%); 0.0435: 1797 (60%); 0.0659: 2394 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 2522 (84%); 5: 2000 (66%); 7: 1422 (47%); 9: 819 (27%) | 3: 724 (24%); 5: 1274 (42%); 7: 1863 (62%); 9: 2553 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.4% | -0.2115, -0.0724, 0.0621, 0.2525 | -0.2115: 2398 (80%); -0.0724: 1797 (60%); 0.0621: 1200 (40%); 0.2525: 600 (20%) | -0.2115: 600 (20%); -0.0724: 1198 (40%); 0.0621: 1797 (60%); 0.2525: 2396 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.4% | 2, 4, 6, 8 | 2: 2620 (87%); 4: 1960 (65%); 6: 1369 (45%); 8: 851 (28%) | 2: 730 (24%); 4: 1357 (45%); 6: 1895 (63%); 8: 2400 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.8% |
| 8k_item_5_02_filed_within_7d | 4.0% |
| above_avwap_20high | 36.7% |
| above_avwap_20low | 59.8% |
| above_avwap_252low | 74.2% |
| above_avwap_50low | 75.7% |
| above_cam_r3 | 38.4% |
| above_cam_r4 | 31.0% |
| above_cpr | 42.3% |
| above_pivot | 40.9% |
| above_prev_high | 32.0% |
| above_prev_high_clearance_atr_05 | 18.9% |
| above_prev_low | 56.9% |
| above_r1 | 32.2% |
| above_r2 | 20.7% |
| above_vwap | 48.5% |
| above_wood_p | 44.4% |
| ad_rising | 54.3% |
| adx_cross_up | 0.3% |
| adx_cross_up_20 | 0.4% |
| adx_di_bear | 61.7% |
| adx_di_bull | 38.3% |
| adx_strong | 3.4% |
| adx_trending | 31.4% |
| ao_cross_dn | 1.2% |
| ao_cross_up | 1.3% |
| ao_positive | 42.9% |
| ao_twin_peaks_bull | 7.2% |
| at_key_fib | 21.1% |
| at_key_fib_wide | 52.1% |
| avwap_20high_loss_recent_3d | 34.1% |
| avwap_20high_reclaim_recent_3d | 29.3% |
| avwap_20low_loss_recent_3d | 34.7% |
| avwap_20low_reclaim_recent_3d | 23.7% |
| avwap_252low_loss_recent_3d | 7.5% |
| avwap_252low_reclaim_recent_3d | 14.9% |
| avwap_50low_loss_recent_3d | 17.6% |
| avwap_50low_reclaim_recent_3d | 21.2% |
| bb_10_20_above_mid | 46.6% |
| bb_10_20_expanding | 50.3% |
| bb_10_20_pctb_gt_75 | 23.9% |
| bb_10_20_pctb_gt_8 | 20.4% |
| bb_10_20_pctb_gt_85 | 16.3% |
| bb_10_20_pctb_gt_9 | 12.9% |
| bb_10_20_pctb_gt_95 | 9.8% |
| bb_10_20_pctb_lt_05 | 11.2% |
| bb_10_20_pctb_lt_1 | 14.8% |
| bb_10_20_pctb_lt_15 | 19.1% |
| bb_10_20_pctb_lt_2 | 24.0% |
| bb_10_20_pctb_lt_25 | 27.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 4.0% |
| bb_10_20_reclaim_from_upper_recent_3d | 4.2% |
| bb_10_20_squeeze | 55.0% |
| bb_10_20_touch_lower | 14.0% |
| bb_10_20_touch_upper | 11.6% |
| bb_20_15_above_mid | 43.0% |
| bb_20_15_expanding | 30.2% |
| bb_20_15_pctb_gt_75 | 14.5% |
| bb_20_15_pctb_gt_8 | 11.3% |
| bb_20_15_pctb_gt_85 | 8.8% |
| bb_20_15_pctb_gt_9 | 7.1% |
| bb_20_15_pctb_gt_95 | 5.5% |
| bb_20_15_pctb_lt_05 | 9.3% |
| bb_20_15_pctb_lt_1 | 12.1% |
| bb_20_15_pctb_lt_15 | 15.4% |
| bb_20_15_pctb_lt_2 | 18.5% |
| bb_20_15_pctb_lt_25 | 23.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 11.0% |
| bb_20_15_reclaim_from_upper_recent_3d | 10.7% |
| bb_20_15_squeeze | 48.6% |
| bb_20_15_touch_lower | 11.0% |
| bb_20_15_touch_upper | 6.8% |
| bb_20_20_above_mid | 43.0% |
| bb_20_20_expanding | 30.2% |
| bb_20_20_pctb_gt_75 | 9.5% |
| bb_20_20_pctb_gt_8 | 7.1% |
| bb_20_20_pctb_gt_85 | 5.1% |
| bb_20_20_pctb_gt_9 | 3.9% |
| bb_20_20_pctb_gt_95 | 2.8% |
| bb_20_20_pctb_lt_05 | 3.8% |
| bb_20_20_pctb_lt_1 | 5.4% |
| bb_20_20_pctb_lt_15 | 8.2% |
| bb_20_20_pctb_lt_2 | 12.1% |
| bb_20_20_pctb_lt_25 | 16.4% |
| bb_20_20_reclaim_from_lower_recent_3d | 6.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 3.6% |
| bb_20_20_squeeze | 29.5% |
| bb_20_20_touch_lower | 4.3% |
| bb_20_20_touch_upper | 3.1% |
| bearish_engulfing | 5.7% |
| bearish_pin_bar | 1.5% |
| below_avwap_20high | 63.3% |
| below_avwap_20low | 40.2% |
| below_avwap_252low | 25.8% |
| below_avwap_50low | 24.3% |
| below_cam_s3 | 56.4% |
| below_cam_s4 | 45.0% |
| below_cpr | 59.1% |
| below_ema_20 | 59.8% |
| below_ema_200 | 58.5% |
| below_ema_200_break_recent_5d | 7.9% |
| below_ema_20_break_recent_5d | 50.0% |
| below_ema_21 | 59.8% |
| below_ema_21_break_recent_5d | 46.9% |
| below_ema_50 | 59.8% |
| below_ema_50_break_recent_5d | 16.8% |
| below_ema_9 | 57.2% |
| below_ema_9_break_recent_5d | 54.5% |
| below_prev_high | 67.8% |
| below_prev_low | 43.0% |
| below_prev_low_clearance_atr_05 | 25.3% |
| below_s1 | 45.7% |
| below_s2 | 28.0% |
| below_sma_20 | 57.0% |
| below_sma_200 | 57.4% |
| below_sma_21 | 57.3% |
| below_sma_50 | 59.4% |
| below_sma_9 | 53.5% |
| below_vwap | 51.5% |
| blowoff_recent_3d | 0.5% |
| break_52w_high | 0.1% |
| break_52w_high_clearance_atr_05 | 0.1% |
| break_52w_low | 0.3% |
| bullish_engulfing | 5.3% |
| bullish_pin_bar | 2.4% |
| capitulation_recent_3d | 0.5% |
| ceo_buy | 0.9% |
| cfo_buy | 0.3% |
| chandelier_long_bullish | 70.4% |
| chandelier_long_flip_dn | 14.7% |
| chandelier_short_bearish | 80.4% |
| chandelier_short_flip_up | 9.2% |
| classification_change_from_tech | 88.9% |
| classification_change_to_defensive | 11.1% |
| close_above_open | 40.2% |
| close_below_open | 59.8% |
| close_in_bottom_40pct_of_range | 50.0% |
| close_in_top_40pct_of_range | 37.9% |
| cluster_buy | 0.6% |
| cmf_cross_dn | 6.5% |
| cmf_cross_up | 5.6% |
| cmf_negative | 45.2% |
| cmf_positive | 54.8% |
| concentrated_sell | 5.6% |
| cpr_narrow | 87.3% |
| cpr_narrow_tight | 24.8% |
| cup_handle_detected | 16.1% |
| cup_handle_neckline_break_retest_long | 0.6% |
| dc10_breakout_dn | 11.8% |
| dc10_breakout_dn_1pct | 18.3% |
| dc10_breakout_up | 9.3% |
| dc10_breakout_up_1pct | 14.4% |
| dc10_new_high | 13.4% |
| dc10_strong_breakout_dn | 4.8% |
| dc10_strong_breakout_up | 3.3% |
| dc20_breakout_dn | 3.2% |
| dc20_breakout_up | 2.2% |
| dc20_new_high | 3.4% |
| dc20_resistance_break_retest_strong | 2.1% |
| dc20_support_break_retest_strong | 7.0% |
| defensive_leadership | 59.4% |
| director_only_buy | 3.4% |
| doji | 1.8% |
| double_bottom_detected | 13.3% |
| double_top_detected | 14.4% |
| dpi_elevated | 53.7% |
| drying_volume_on_down_turn | 34.0% |
| drying_volume_on_up_turn | 22.4% |
| ema_20_50_bearish | 57.7% |
| ema_20_50_bullish | 42.3% |
| ema_20_50_death_cross | 0.5% |
| ema_20_50_golden_cross | 0.3% |
| ema_50_200_bearish | 55.3% |
| ema_50_200_bullish | 44.7% |
| ema_50_200_death_cross | 0.3% |
| ema_50_200_golden_cross | 0.2% |
| ema_9_21_bearish | 56.8% |
| ema_9_21_bullish | 43.2% |
| ema_9_21_death_cross | 2.2% |
| ema_9_21_golden_cross | 2.5% |
| evening_star | 10.0% |
| flag_bear_break_retest_short | 0.2% |
| flag_bear_broke | 0.3% |
| flag_bear_detected | 0.5% |
| flag_bull_break_retest_long | 0.1% |
| flag_bull_broke | 0.2% |
| flag_bull_detected | 1.5% |
| force_index_cross_dn | 59.8% |
| force_index_cross_up | 40.2% |
| force_index_positive | 40.2% |
| gap_dn_1_5pct | 13.3% |
| gap_dn_2pct | 9.4% |
| gap_up_1_5pct | 9.8% |
| gap_up_2pct | 6.5% |
| hammer | 2.4% |
| head_shoulders_bottom_detected | 4.0% |
| head_shoulders_top_detected | 4.4% |
| house_cluster_buy | 4.2% |
| house_cluster_sell | 4.6% |
| htf_aligned_bear | 39.1% |
| htf_aligned_bull | 25.0% |
| htf_disagreement | 1.5% |
| hull_bearish | 47.7% |
| hull_bullish | 52.3% |
| hull_flip_dn | 12.4% |
| hull_flip_up | 10.2% |
| ichi_above_cloud | 33.5% |
| ichi_above_cloud_break_recent_5d | 5.4% |
| ichi_below_cloud | 50.1% |
| ichi_below_cloud_break_recent_5d | 7.7% |
| ichi_cloud_thick | 86.8% |
| ichi_tk_bearish | 55.5% |
| ichi_tk_bullish | 41.3% |
| ichi_tk_cross_dn | 2.2% |
| ichi_tk_cross_up | 2.3% |
| ichi_weekly_above_cloud | 35.5% |
| ichi_weekly_below_cloud | 35.6% |
| ichi_weekly_in_cloud | 28.9% |
| in_reversal_window | 3.2% |
| inside_bar | 8.5% |
| inside_cpr | 0.8% |
| inside_kc | 96.3% |
| insider_cluster_active | 21.4% |
| institutional_buy | 89.5% |
| institutional_negative | 4.5% |
| institutional_persistence_growing | 43.4% |
| institutional_persistence_strong | 59.7% |
| institutional_strong_buy | 79.3% |
| inverted_cup_handle_detected | 12.9% |
| is_friday | 19.2% |
| is_halloween_period | 51.4% |
| is_halloween_period_first_day | 0.2% |
| is_january | 10.1% |
| is_january_extended | 12.2% |
| is_monday | 15.1% |
| is_pre_holiday | 2.3% |
| is_summer_period | 48.6% |
| is_totm_window | 33.4% |
| is_totm_window_first_day | 9.5% |
| is_week_open | 17.7% |
| kc_touch_lower | 3.2% |
| kc_touch_upper | 1.0% |
| large_dollar_buy | 0.9% |
| macd_12_26_9_bearish | 48.1% |
| macd_12_26_9_bullish | 51.9% |
| macd_12_26_9_crossover_dn | 8.0% |
| macd_12_26_9_crossover_up | 6.0% |
| macd_8_21_5_bearish | 46.2% |
| macd_8_21_5_bullish | 53.8% |
| macd_8_21_5_crossover_dn | 9.9% |
| macd_8_21_5_crossover_up | 7.7% |
| marubozu_bear | 2.2% |
| marubozu_bull | 2.0% |
| mfi_broad_overbought | 4.4% |
| mfi_broad_oversold | 3.6% |
| mfi_overbought | 0.4% |
| mfi_oversold | 0.2% |
| monthly_above_sma_12 | 43.3% |
| monthly_above_sma_6 | 41.2% |
| monthly_bias_bear | 48.0% |
| monthly_bias_bull | 32.5% |
| monthly_momentum_pos | 44.5% |
| morning_star | 6.0% |
| near_52w_high | 0.2% |
| near_52w_high_95pct | 6.9% |
| near_52w_high_retest_long | 0.3% |
| near_52w_low | 0.9% |
| near_52w_low_105pct | 4.4% |
| near_52w_low_retest_short | 0.9% |
| near_avwap_20high_atr_05x | 38.7% |
| near_avwap_20high_atr_10x | 72.7% |
| near_avwap_20high_atr_15x | 91.2% |
| near_avwap_20high_atr_20x | 97.6% |
| near_avwap_20low_atr_05x | 44.6% |
| near_avwap_20low_atr_10x | 74.8% |
| near_avwap_20low_atr_15x | 90.2% |
| near_avwap_20low_atr_20x | 96.3% |
| near_avwap_252low_atr_05x | 17.7% |
| near_avwap_252low_atr_10x | 34.5% |
| near_avwap_252low_atr_15x | 47.6% |
| near_avwap_252low_atr_20x | 57.8% |
| near_avwap_50low_atr_05x | 36.4% |
| near_avwap_50low_atr_10x | 62.8% |
| near_avwap_50low_atr_15x | 80.2% |
| near_avwap_50low_atr_20x | 90.5% |
| near_cam_r3 | 4.4% |
| near_cam_s3 | 6.7% |
| near_cam_s4 | 10.1% |
| near_fib_236 | 5.3% |
| near_fib_382 | 7.0% |
| near_fib_500 | 6.5% |
| near_fib_618 | 7.9% |
| near_fib_786 | 5.7% |
| near_pivot | 4.2% |
| near_prev_close | 1.3% |
| near_prev_high | 5.0% |
| near_prev_low | 8.0% |
| near_r1 | 6.4% |
| near_r1_wide | 26.6% |
| near_r2 | 5.5% |
| near_r2_wide | 25.0% |
| near_s1 | 9.7% |
| near_s1_wide | 37.1% |
| near_s2 | 8.4% |
| near_s2_wide | 34.9% |
| near_s3 | 5.2% |
| near_wood_r1 | 5.4% |
| near_wood_s1 | 7.3% |
| news_uses_polygon_score | 22.6% |
| obv_bearish | 51.6% |
| obv_bullish | 48.4% |
| obv_diverge_bull | 11.0% |
| obv_falling | 51.1% |
| obv_rising | 48.9% |
| outside_bar | 9.8% |
| pead_negative_surprise | 17.1% |
| pead_positive_surprise | 22.7% |
| pin_bar | 3.9% |
| po3_accumulation_active | 42.7% |
| po3_bearish | 8.5% |
| po3_bullish | 5.4% |
| po3_manipulation_sweep_down | 17.8% |
| po3_manipulation_sweep_up | 10.4% |
| po3_mmbm_setup | 1.0% |
| po3_mmsm_setup | 1.7% |
| po3_sweep_above_prior_high | 47.3% |
| po3_sweep_below_prior_low | 58.2% |
| ppo_bullish | 51.3% |
| ppo_crossover_dn | 7.8% |
| ppo_crossover_up | 6.2% |
| pre_fomc_d0 | 2.4% |
| pre_fomc_d1 | 2.1% |
| pre_fomc_window | 4.5% |
| price_above_dema | 49.8% |
| price_above_ema_20 | 40.2% |
| price_above_ema_200 | 41.5% |
| price_above_ema_200_break_recent_5d | 5.8% |
| price_above_ema_20_break_recent_5d | 37.5% |
| price_above_ema_21 | 40.2% |
| price_above_ema_21_break_recent_5d | 35.3% |
| price_above_ema_50 | 40.2% |
| price_above_ema_50_break_recent_5d | 13.7% |
| price_above_ema_9 | 42.8% |
| price_above_ema_9_break_recent_5d | 40.2% |
| price_above_hull | 48.9% |
| price_above_sma_200 | 42.6% |
| price_above_sma_21 | 42.7% |
| price_above_sma_50 | 40.6% |
| price_above_tema | 50.7% |
| price_below_dema | 50.2% |
| price_below_hull | 51.1% |
| price_below_tema | 49.3% |
| psar_bullish | 50.8% |
| psar_flip_dn | 12.3% |
| psar_flip_up | 9.7% |
| r1_break_retest_long | 49.5% |
| recent_capitulation_at_s3 | 0.1% |
| resistance_break_retest | 3.4% |
| risk_off_regime_bond_signal | 20.3% |
| risk_off_regime_bond_signal_strong | 6.1% |
| risk_off_regime_gold_signal | 44.0% |
| risk_on_regime_bond_signal | 43.0% |
| risk_on_regime_bond_signal_strong | 19.0% |
| roc_positive | 45.1% |
| roc_turning_dn | 20.7% |
| roc_turning_up | 14.6% |
| rsi_14_bullish | 40.0% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_14_cross_dn_overbought_recent_3d | 2.6% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_14_cross_up_oversold_recent_3d | 4.2% |
| rsi_14_extreme_os | 0.1% |
| rsi_14_overbought | 0.2% |
| rsi_14_oversold | 0.4% |
| rsi_14_rising | 40.2% |
| rsi_21_bullish | 40.6% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.0% |
| rsi_21_cross_dn_overbought_recent_3d | 1.0% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.0% |
| rsi_21_cross_up_oversold_recent_3d | 2.2% |
| rsi_21_extreme_os | 0.0% |
| rsi_21_oversold | 0.2% |
| rsi_21_rising | 40.2% |
| rsi_2_bullish | 41.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 38.7% |
| rsi_2_cross_dn_overbought_recent_3d | 48.4% |
| rsi_2_cross_up_extreme_os_recent_3d | 28.4% |
| rsi_2_cross_up_oversold_recent_3d | 34.4% |
| rsi_2_extreme_ob | 27.1% |
| rsi_2_extreme_os | 32.4% |
| rsi_2_overbought | 33.9% |
| rsi_2_oversold | 43.8% |
| rsi_2_rising | 40.2% |
| rsi_9_bullish | 40.6% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.7% |
| rsi_9_cross_dn_overbought_recent_3d | 6.5% |
| rsi_9_cross_up_extreme_os_recent_3d | 1.7% |
| rsi_9_cross_up_oversold_recent_3d | 8.4% |
| rsi_9_extreme_ob | 0.0% |
| rsi_9_extreme_os | 0.1% |
| rsi_9_overbought | 0.9% |
| rsi_9_oversold | 1.8% |
| rsi_9_rising | 40.2% |
| s1_break_retest_short | 51.7% |
| sc_13d_filed_within_30d | 2.9% |
| sc_13g_filed_within_30d | 3.0% |
| sector_outperforming_spy | 41.9% |
| sector_underperforming_spy | 58.1% |
| shooting_star | 1.5% |
| sma_20_50_bullish | 43.3% |
| sma_20_50_golden_cross | 0.6% |
| sma_50_200_bullish | 45.5% |
| sma_50_200_golden_cross | 0.2% |
| sma_9_21_bullish | 45.5% |
| sma_9_21_golden_cross | 2.8% |
| smc_bos_bearish | 12.6% |
| smc_bos_bullish | 11.5% |
| smc_bos_retest_long | 4.3% |
| smc_bos_retest_short | 4.1% |
| smc_breaker_block_bearish | 15.9% |
| smc_breaker_block_bullish | 20.1% |
| smc_choch_bearish | 5.7% |
| smc_choch_bullish | 3.3% |
| smc_equal_highs_swept | 2.7% |
| smc_equal_lows_swept | 4.3% |
| smc_fvg_bearish_active | 31.8% |
| smc_fvg_bullish_active | 35.8% |
| smc_fvg_retest_long_zone | 8.7% |
| smc_fvg_retest_short_zone | 6.3% |
| smc_in_discount_zone | 70.7% |
| smc_in_premium_zone | 55.0% |
| smc_inverse_fvg_bearish | 93.9% |
| smc_inverse_fvg_bullish | 84.8% |
| smc_liquidity_swept_dn | 1.2% |
| smc_liquidity_swept_up | 0.9% |
| smc_mitigation_block_long | 1.0% |
| smc_mitigation_block_short | 0.5% |
| smc_ob_bearish_active | 39.5% |
| smc_ob_bullish_active | 26.8% |
| smc_ote_long_zone | 8.9% |
| smc_ote_short_zone | 5.9% |
| squeeze_fire_dn | 14.5% |
| squeeze_fire_up | 9.5% |
| squeeze_in | 41.4% |
| squeeze_positive | 42.9% |
| stoch_bearish_cross | 15.5% |
| stoch_broad_overbought | 7.9% |
| stoch_broad_oversold | 5.9% |
| stoch_bullish_cross | 11.7% |
| stoch_overbought | 3.3% |
| stoch_oversold | 2.3% |
| stochrsi_cross_dn | 28.0% |
| stochrsi_cross_up | 23.6% |
| stochrsi_overbought | 28.7% |
| stochrsi_oversold | 27.3% |
| supertrend_bearish | 3.1% |
| supertrend_bullish | 96.9% |
| supertrend_flip_dn | 3.1% |
| supertrend_flip_recent_long_5d | 1.2% |
| supertrend_flip_recent_short_5d | 3.4% |
| supertrend_flip_up | 0.2% |
| support_break_retest | 9.2% |
| tema_above_dema | 49.0% |
| tema_cross_dn | 4.8% |
| tema_cross_up | 4.4% |
| three_black_crows | 4.8% |
| three_white_soldiers | 3.6% |
| triangle_apex_break_retest_long | 11.0% |
| triangle_ascending_detected | 8.4% |
| triangle_descending_detected | 10.0% |
| uo_overbought | 0.2% |
| uo_oversold | 0.4% |
| usd_strengthening | 26.8% |
| usd_weakening | 12.0% |
| vix_band_high | 46.4% |
| vix_band_low | 30.9% |
| vix_band_mid | 22.8% |
| vix_term_backwardation | 12.3% |
| vix_term_contango | 87.7% |
| vol_above_avg | 43.6% |
| vol_below_avg | 56.4% |
| vol_spike_12x | 27.2% |
| vol_spike_15x | 15.1% |
| vol_spike_17x | 11.2% |
| vol_spike_2x | 6.8% |
| vol_spike_2x_on_down_day_recent_3d | 1.8% |
| vol_spike_2x_on_up_day_recent_3d | 2.7% |
| vol_spike_3x | 2.4% |
| vp_above_value_area | 8.9% |
| vp_below_value_area | 13.9% |
| vp_close_above_poc | 47.0% |
| vp_close_below_poc | 53.0% |
| vp_in_value_area | 77.3% |
| week_open_gap_down_15pct | 2.1% |
| week_open_gap_up_15pct | 1.4% |
| weekly_above_ema_10 | 40.7% |
| weekly_above_ema_20 | 40.7% |
| weekly_bias_bear | 52.2% |
| weekly_bias_bull | 33.7% |
| weekly_momentum_pos | 42.8% |
| williams_r_overbought | 12.2% |
| williams_r_oversold | 15.3% |
| williams_r_rising | 40.7% |
| within_pead_window | 37.2% |
| within_post_deletion_window | 3.9% |
| within_post_inclusion_window | 1.6% |
| within_pre_rebalance_window | 1.2% |
| xs_avoid_high_ivol | 71.0% |
| xs_avoid_high_max | 72.6% |
| xs_high_beta_decile | 27.6% |
| xs_low_beta_bottom_quintile | 27.6% |
| xs_low_beta_decile | 15.9% |
| xs_low_beta_decile_entry_recent_5d | 0.3% |
| xs_low_beta_top_quintile | 15.9% |
| xs_momentum_bottom_decile | 12.5% |
| xs_momentum_bottom_quintile | 24.4% |
| xs_momentum_top_decile | 11.6% |
| xs_momentum_top_quintile | 19.9% |
| xs_quality_bottom_quintile | 21.1% |
| xs_quality_top_quintile | 20.7% |
| xs_quality_top_tercile | 41.7% |
| year_high_break_retest_long | 0.1% |
| year_low_break_retest_short | 1.1% |
| yoy_surprise_high | 52.2% |
| yoy_surprise_negative | 38.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.3% |
| committed_growth_holders | 91.3% |
| corp_donations_1y | 6.8% |
| corp_donations_count_1y | 6.8% |
| corp_donations_unique_pacs | 6.8% |
| cot_rut_commercials_pctile_3y | 53.0% |
| cot_rut_mmoney_pctile_3y | 53.0% |
| cup_handle_depth_pct | 20.7% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 7.7% |
| days_since_inclusion | 14.6% |
| days_to_next_holiday | 65.3% |
| days_to_rebalance | 10.8% |
| dpi_30d_avg | 95.0% |
| dpi_recent | 95.0% |
| earnings_announcement_return | 89.8% |
| earnings_eps_yoy_growth | 94.3% |
| flag_bear_pole_move_pct | 0.5% |
| flag_bull_pole_move_pct | 1.5% |
| gov_contracts_4q_sum | 39.9% |
| gov_contracts_last_qtr_amount | 39.9% |
| gov_contracts_qoq_growth | 39.9% |
| head_shoulders_magnitude_pct | 8.2% |
| insider_director_buyers_30d | 5.3% |
| insider_officer_buyers_30d | 5.3% |
| insider_total_shares_bought_30d | 5.3% |
| insider_unique_buyers_30d | 5.3% |
| inverted_cup_handle_height_pct | 17.1% |
| lobbying_amount_1y | 69.4% |
| lobbying_amount_q | 69.4% |
| lobbying_amount_yoy | 69.4% |
| monthly_momentum_6m | 94.8% |
| otc_short_ratio_recent | 95.0% |
| otc_volume_recent | 95.0% |
| pair_half_life | 92.6% |
| pair_max_abs_zscore | 92.6% |
| pair_zscore_signed | 92.6% |
| pct_from_avwap_20high | 96.4% |
| pct_from_avwap_20low | 94.5% |
| pct_from_avwap_252low | 94.8% |
| persistent_holders_4q | 91.3% |
| persistent_holders_8q | 91.3% |
| sc_13g_latest_percent_owned | 1.4% |
| search_volume_index_recent | 76.2% |
| search_volume_observations | 76.2% |
| search_volume_zscore_30d | 76.2% |
| sector_etf_return_20d | 2.1% |
| spy_return_20d | 2.1% |
| total_active_holders | 91.3% |
| triangle_breakdown_pct | 10.0% |
| triangle_breakout_pct | 8.4% |
| xs_quality_decile | 61.5% |
| xs_quality_gross_profitability | 61.5% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (1.0), `avwap_20low` (0.999), `avwap_252low` (0.995), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.998), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (1.0), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.999), `double_top_neckline` (0.997), `double_top_peak` (0.998), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.996), `fib_382` (0.997), `fib_500` (0.997), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.992), `fib_ext_162` (0.99), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (0.999), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.991), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.983), `monthly_sma_6` (0.995), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.998), `s3` (0.998), `supertrend_value` (0.997), `swing_high` (0.995), `swing_low` (0.996), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.997), `vp_value_area_low` (0.997), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.998), `year_high` (0.969), `year_low` (0.97)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P2.1 | (structural) c > o - optional min body p | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P3.1 | mirror of close_above_open | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P7 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     3 x 3 x 1 = 9
offline gradings   0 level-combinations x 24 exits = 0 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  8 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 0 + 8 = 9 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 653 census axes join it only when REGISTERED at the T3 band review.
