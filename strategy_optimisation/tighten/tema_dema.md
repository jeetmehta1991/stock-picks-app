# Table A - tema_dema

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6d884d139 | commit 6d884d139 at 2026-10-27 10:10:00 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** trend | **status:** NOT-STARTED | **R5 fires:** 1876 (closed fires in the exit cube: 1876 of 1876, S6-B3258) | **surviving fires (T1):** 1351 (survives_pct 0.7201)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_tema  <- backtest/signals/technical.py
       DEFN: close above / below TEMA(20) (technical.py compute_dema_tema)
       knobs P1.1-P1.1 (band rows in Table A)
P2  price_below_tema  <- backtest/signals/technical.py
       DEFN: close above / below TEMA(20) (technical.py compute_dema_tema)
       knobs P2.1-P2.1 (band rows in Table A)
P3  tema_cross_dn  <- backtest/signals/technical.py
       DEFN: TEMA(20) crosses above / below DEMA(20) against the prior bar (technical.py compute_dema_tema)
       knobs P3.1-P3.1 (band rows in Table A)
P4  tema_cross_up  <- backtest/signals/technical.py
       DEFN: TEMA(20) crosses above / below DEMA(20) against the prior bar (technical.py compute_dema_tema)
       knobs P4.1-P4.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P5  ao <= 2.866   [EXISTING-THRESHOLD]
P6  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_tema_dema (docstring and return dropped):

```python
fl = s.get('tema_cross_up') and s.get('price_above_tema')
fl = fl and s.get('ao', float('inf')) <= 2.866
fs = (s.get('tema_cross_dn') and s.get('price_below_tema')) and (not _short_borrow_trap_active(s))
fs = fs and s.get('ao', float('inf')) <= 2.866
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
| P1 | PRODUCER | price_above_tema - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close above / below TEMA(20) (technical.py compute_dema_tema) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | buffer above TEMA (close > tema x (1 + b)); the period is tema_cross_up's knob - backtest/signals/technical.py compute_dema_tema | MEASURED - production strict close > tema; 1-pct steps through the R5 fires' price-over-tema margin (q20 1.40pct, q40 2.09pct, q60 3.13pct of tema) | 0.0 | 0, 0.01, 0.02, 0.03 | offline 3 of 4 levels - TIGHTER (0.01, 0.02, 0.03) - subset on the persisted tema and a close recovered as vwap x (1 + pct_from_vwap / 100); the price-vs-tema legs reproduce on 1876 of 1876 R5 fires | LOOSER (a negative buffer) - adds fires; outside the band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | price_below_tema - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close above / below TEMA(20) (technical.py compute_dema_tema) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | mirror of price_above_tema (close < tema x (1 - b)) - backtest/signals/technical.py compute_dema_tema | mirror | 0.0 | as long, mirrored | counted on the mirrored leg - TIGHTER - mirrored, on the same persisted keys | LOOSER - mirrored; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | tema_cross_dn - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | TEMA(20) crosses above / below DEMA(20) against the prior bar (technical.py compute_dema_tema) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | mirror of tema_cross_up (the same period) - backtest/signals/technical.py compute_dema_tema | mirror | 20 | as long, mirrored | counted on the mirrored leg - none - mirrored | the whole band, mirrored; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | tema_cross_up - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | TEMA(20) crosses above / below DEMA(20) against the prior bar (technical.py compute_dema_tema) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | TEMA / DEMA EMA period (one period drives both averages) - backtest/signals/technical.py compute_dema_tema | BRACKET production - compute_dema_tema's default; its call site passes no period | 20 | 10, 20, 30 | offline 0 of 3 levels - none - the averages at other periods are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY | ao `<= 2.866` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `<= 2.866` | production + 4 tighter measured levels | offline 4 of 5 levels - measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| ao | backtest/signals/technical.py | `<= 2.866` | 100.0% | TIGHTER = LOWER the ceiling: -6.71 -> 271 (20%); -3.0256 -> 541 (40%); -1.1582 -> 811 (60%); 0.7541 -> 1081 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 16.83, 20.98, 26.4, 33.58 | 16.83: 1081 (80%); 20.98: 811 (60%); 26.4: 542 (40%); 33.58: 272 (20%) | 16.83: 271 (20%); 20.98: 541 (40%); 26.4: 811 (60%); 33.58: 1081 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 20.98, 23.86, 26.23, 29.56 | 20.98: 1081 (80%); 23.86: 811 (60%); 26.23: 542 (40%); 29.56: 271 (20%) | 20.98: 273 (20%); 23.86: 542 (40%); 26.23: 811 (60%); 29.56: 1081 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 16.64, 19.68, 22.31, 25.77 | 16.64: 1083 (80%); 19.68: 811 (60%); 22.31: 542 (40%); 25.77: 271 (20%) | 16.64: 271 (20%); 19.68: 542 (40%); 22.31: 811 (60%); 25.77: 1082 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 0.9805, 1.6734, 2.6875, 4.8673 | 0.9805: 1081 (80%); 1.6734: 811 (60%); 2.6875: 541 (40%); 4.8673: 271 (20%) | 0.9805: 271 (20%); 1.6734: 541 (40%); 2.6875: 811 (60%); 4.8673: 1081 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 0.9805, 1.6734, 2.6875, 4.8673 | 0.9805: 1081 (80%); 1.6734: 811 (60%); 2.6875: 541 (40%); 4.8673: 271 (20%) | 0.9805: 271 (20%); 1.6734: 541 (40%); 2.6875: 811 (60%); 4.8673: 1081 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.087, 2.616, 3.182, 4.077 | 2.087: 1081 (80%); 2.616: 811 (60%); 3.182: 541 (40%); 4.077: 272 (20%) | 2.087: 272 (20%); 2.616: 543 (40%); 3.182: 811 (60%); 4.077: 1081 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0478, 0.067, 0.0917, 0.1378 | 0.0478: 1081 (80%); 0.067: 812 (60%); 0.0917: 541 (40%); 0.1378: 272 (20%) | 0.0478: 271 (20%); 0.067: 541 (40%); 0.0917: 811 (60%); 0.1378: 1081 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2197, 0.5352, 0.7268, 0.8882 | 0.2197: 1081 (80%); 0.5352: 811 (60%); 0.7268: 541 (40%); 0.8882: 273 (20%) | 0.2197: 271 (20%); 0.5352: 542 (40%); 0.7268: 811 (60%); 0.8882: 1081 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0548, 0.0755, 0.1014, 0.1402 | 0.0548: 1081 (80%); 0.0755: 811 (60%); 0.1014: 542 (40%); 0.1402: 271 (20%) | 0.0548: 271 (20%); 0.0755: 542 (40%); 0.1014: 811 (60%); 0.1402: 1082 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2668, 0.4297, 0.554, 0.7052 | 0.2668: 1081 (80%); 0.4297: 811 (60%); 0.554: 542 (40%); 0.7052: 271 (20%) | 0.2668: 271 (20%); 0.4297: 541 (40%); 0.554: 811 (60%); 0.7052: 1081 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.073, 0.1006, 0.1353, 0.1869 | 0.073: 1081 (80%); 0.1006: 812 (60%); 0.1353: 541 (40%); 0.1869: 271 (20%) | 0.073: 271 (20%); 0.1006: 542 (40%); 0.1353: 812 (60%); 0.1869: 1081 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.3251, 0.4473, 0.5405, 0.6539 | 0.3251: 1081 (80%); 0.4473: 811 (60%); 0.5405: 542 (40%); 0.6539: 271 (20%) | 0.3251: 271 (20%); 0.4473: 541 (40%); 0.5405: 811 (60%); 0.6539: 1081 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0454, -0.0196, -0.0006, 0.0296 | -0.0454: 1081 (80%); -0.0196: 812 (60%); -0.0006: 549 (41%); 0.0296: 275 (20%) | -0.0454: 275 (20%); -0.0196: 547 (40%); -0.0006: 811 (60%); 0.0296: 1088 (81%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1447, 0.167, 0.211, 0.27 | 0.1447: 1080 (80%); 0.167: 813 (60%); 0.211: 537 (40%); 0.27: 269 (20%) | 0.1447: 271 (20%); 0.167: 538 (40%); 0.211: 814 (60%); 0.27: 1082 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1351 (100%) | 0: 1259 (93%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1179, -0.0404, 0.0291, 0.1001 | -0.1179: 1081 (80%); -0.0404: 811 (60%); 0.0291: 541 (40%); 0.1001: 271 (20%) | -0.1179: 271 (20%); -0.0404: 542 (40%); 0.0291: 812 (60%); 0.1001: 1081 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1351 (100%); 1: 508 (38%) | 0: 843 (62%); 1: 1128 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2399, -0.1872, -0.1463, -0.1141 | -0.2399: 1082 (80%); -0.1872: 817 (60%); -0.1463: 541 (40%); -0.1141: 276 (20%) | -0.2399: 273 (20%); -0.1872: 542 (40%); -0.1463: 817 (60%); -0.1141: 1096 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4167, 0.6154, 0.7244, 0.7949 | 0.4167: 1086 (80%); 0.6154: 814 (60%); 0.7244: 550 (41%); 0.7949: 273 (20%) | 0.4167: 281 (21%); 0.6154: 546 (40%); 0.7244: 862 (64%); 0.7949: 1083 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.3141, 0.6282, 0.8269 | 0.2564: 1081 (80%); 0.3141: 881 (65%); 0.6282: 541 (40%); 0.8269: 271 (20%) | 0.2564: 289 (21%); 0.3141: 546 (40%); 0.6282: 833 (62%); 0.8269: 1096 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0892, -0.0065, 0.0961, 0.2798 | -0.0892: 1082 (80%); -0.0065: 820 (61%); 0.0961: 549 (41%); 0.2798: 276 (20%) | -0.0892: 272 (20%); -0.0065: 546 (40%); 0.0961: 826 (61%); 0.2798: 1084 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2821, 0.4679, 0.6538, 0.8974 | 0.2821: 1082 (80%); 0.4679: 815 (60%); 0.6538: 551 (41%); 0.8974: 276 (20%) | 0.2821: 280 (21%); 0.4679: 556 (41%); 0.6538: 823 (61%); 0.8974: 1096 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.109, 0.3462, 0.4744, 0.641 | 0.109: 1099 (81%); 0.3462: 825 (61%); 0.4744: 542 (40%); 0.641: 279 (21%) | 0.109: 278 (21%); 0.3462: 544 (40%); 0.4744: 821 (61%); 0.641: 1081 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.4997, -0.3562, -0.1909, 0.056 | -0.4997: 1087 (80%); -0.3562: 829 (61%); -0.1909: 550 (41%); 0.056: 272 (20%) | -0.4997: 271 (20%); -0.3562: 555 (41%); -0.1909: 816 (60%); 0.056: 1084 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3333, 0.5, 0.7051, 0.9167 | 0.3333: 1086 (80%); 0.5: 823 (61%); 0.7051: 549 (41%); 0.9167: 342 (25%) | 0.3333: 272 (20%); 0.5: 552 (41%); 0.7051: 815 (60%); 0.9167: 1082 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1154, 0.2885, 0.5577, 0.8013 | 0.1154: 1117 (83%); 0.2885: 813 (60%); 0.5577: 541 (40%); 0.8013: 275 (20%) | 0.1154: 274 (20%); 0.2885: 560 (41%); 0.5577: 818 (61%); 0.8013: 1089 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0681, -0.0599, -0.0399, 0 | -0.0681: 1086 (80%); -0.0599: 812 (60%); -0.0399: 550 (41%); 0: 377 (28%) | -0.0681: 296 (22%); -0.0599: 543 (40%); -0.0399: 823 (61%); 0: 1320 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4103, 0.7051, 0.8846, 1 | 0.4103: 1085 (80%); 0.7051: 824 (61%); 0.8846: 587 (43%); 1: 294 (22%) | 0.4103: 272 (20%); 0.7051: 544 (40%); 0.8846: 835 (62%); 1: 1351 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0962, 0.2244, 0.5385, 0.8462 | 0.0962: 1086 (80%); 0.2244: 812 (60%); 0.5385: 542 (40%); 0.8462: 276 (20%) | 0.0962: 273 (20%); 0.2244: 545 (40%); 0.5385: 821 (61%); 0.8462: 1083 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0078, 0.04, 0.0911, 0.2309 | 0.0078: 1082 (80%); 0.04: 813 (60%); 0.0911: 541 (40%); 0.2309: 279 (21%) | 0.0078: 278 (21%); 0.04: 549 (41%); 0.0911: 826 (61%); 0.2309: 1122 (83%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.5974, 0.7979, 0.9423, 0.9744 | 0.5974: 1081 (80%); 0.7979: 813 (60%); 0.9423: 542 (40%); 0.9744: 301 (22%) | 0.5974: 279 (21%); 0.7979: 544 (40%); 0.9423: 819 (61%); 0.9744: 1110 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0897, 0.2278, 0.5385, 0.7821 | 0.0897: 1082 (80%); 0.2278: 813 (60%); 0.5385: 550 (41%); 0.7821: 271 (20%) | 0.0897: 271 (20%); 0.2278: 552 (41%); 0.5385: 814 (60%); 0.7821: 1091 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, 0.0098, 0.1218, 0.2205 | -0.0812: 1173 (87%); 0.0098: 814 (60%); 0.1218: 543 (40%); 0.2205: 274 (20%) | -0.0812: 317 (23%); 0.0098: 541 (40%); 0.1218: 812 (60%); 0.2205: 1083 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1544, 0.0073, 0.0492, 0.0968 | -0.1544: 1082 (80%); 0.0073: 813 (60%); 0.0492: 545 (40%); 0.0968: 283 (21%) | -0.1544: 274 (20%); 0.0073: 545 (40%); 0.0492: 815 (60%); 0.0968: 1087 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3654, 0.5897, 0.7628, 0.8846 | 0.3654: 1082 (80%); 0.5897: 817 (60%); 0.7628: 561 (42%); 0.8846: 277 (21%) | 0.3654: 281 (21%); 0.5897: 549 (41%); 0.7628: 815 (60%); 0.8846: 1083 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1346, 0.3782, 0.5705, 0.7885 | 0.1346: 1084 (80%); 0.3782: 817 (60%); 0.5705: 546 (40%); 0.7885: 280 (21%) | 0.1346: 271 (20%); 0.3782: 579 (43%); 0.5705: 822 (61%); 0.7885: 1086 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.045, 0.1017, 0.195, 0.4133 | 0.045: 1089 (81%); 0.1017: 813 (60%); 0.195: 541 (40%); 0.4133: 271 (20%) | 0.045: 272 (20%); 0.1017: 541 (40%); 0.195: 812 (60%); 0.4133: 1081 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.4% | 28, 64, 84, 149 | 28: 1075 (80%); 64: 807 (60%); 84: 534 (40%); 149: 271 (20%) | 28: 267 (20%); 64: 539 (40%); 84: 812 (60%); 149: 1070 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.6% | 1.6974, 2.2123, 2.7879, 3.7564 | 1.6974: 1077 (80%); 2.2123: 808 (60%); 2.7879: 539 (40%); 3.7564: 270 (20%) | 1.6974: 270 (20%); 2.2123: 539 (40%); 2.7879: 808 (60%); 3.7564: 1077 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 10, 19, 26, 33 | 10: 1081 (80%); 19: 821 (61%); 26: 542 (40%); 33: 321 (24%) | 10: 271 (20%); 19: 582 (43%); 26: 847 (63%); 33: 1084 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3, 4 | 1: 1117 (83%); 2: 831 (62%); 3: 575 (43%); 4: 273 (20%) | 1: 520 (38%); 2: 776 (57%); 3: 1078 (80%); 4: 1351 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0149, -0.0042, 0.0117, 0.0233 | -0.0149: 1084 (80%); -0.0042: 812 (60%); 0.0117: 548 (41%); 0.0233: 278 (21%) | -0.0149: 281 (21%); -0.0042: 541 (40%); 0.0117: 811 (60%); 0.0233: 1084 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.4904, 25.7515, 26.4178, 27.201 | 24.4904: 1081 (80%); 25.7515: 813 (60%); 26.4178: 557 (41%); 27.201: 272 (20%) | 24.4904: 272 (20%); 25.7515: 544 (40%); 26.4178: 817 (60%); 27.201: 1081 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.696, -0.196, 0.16, 0.784 | -0.696: 1081 (80%); -0.196: 811 (60%); 0.16: 543 (40%); 0.784: 271 (20%) | -0.696: 273 (20%); -0.196: 541 (40%); 0.16: 811 (60%); 0.784: 1081 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.784, -0.16, 0.196, 0.696 | -0.784: 1081 (80%); -0.16: 811 (60%); 0.196: 541 (40%); 0.696: 273 (20%) | -0.784: 271 (20%); -0.16: 543 (40%); 0.196: 811 (60%); 0.696: 1081 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0383, 0.0018, 0.0284, 0.0668 | -0.0383: 1085 (80%); 0.0018: 811 (60%); 0.0284: 541 (40%); 0.0668: 271 (20%) | -0.0383: 272 (20%); 0.0018: 541 (40%); 0.0284: 812 (60%); 0.0668: 1081 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.144, 8.5005, 8.776, 9.1755 | 8.144: 1078 (80%); 8.5005: 814 (60%); 8.776: 540 (40%); 9.1755: 270 (20%) | 8.144: 273 (20%); 8.5005: 537 (40%); 8.776: 811 (60%); 9.1755: 1081 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.0% | 0, 1 | 0: 1338 (99%); 1: 391 (29%) | 0: 947 (70%); 1: 1210 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.0% | -1, 0 | -1: 1271 (94%); 0: 1059 (78%) | -1: 279 (21%); 0: 1140 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.0% | 0, 1 | 0: 1338 (99%); 1: 446 (33%) | 0: 892 (66%); 1: 1184 (88%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 5, 134, 260 | 3: 1086 (80%); 5: 888 (66%); 134: 542 (40%); 260: 273 (20%) | 3: 374 (28%); 5: 546 (40%); 134: 811 (60%); 260: 1081 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 0, 4, 81, 134 | 0: 1351 (100%); 4: 819 (61%); 81: 544 (40%); 134: 271 (20%) | 0: 272 (20%); 4: 567 (42%); 81: 813 (60%); 134: 1084 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.1362, 0.0682, 0.2666, 0.6236 | -0.1362: 1082 (80%); 0.0682: 811 (60%); 0.2666: 541 (40%); 0.6236: 271 (20%) | -0.1362: 271 (20%); 0.0682: 541 (40%); 0.2666: 811 (60%); 0.6236: 1081 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -3.0473, -1.3777, -0.5213, 0.3256 | -3.0473: 1081 (80%); -1.3777: 811 (60%); -0.5213: 541 (40%); 0.3256: 271 (20%) | -3.0473: 271 (20%); -1.3777: 541 (40%); -0.5213: 811 (60%); 0.3256: 1081 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -3.7008, -1.6232, -0.6215, 0.4581 | -3.7008: 1081 (80%); -1.6232: 811 (60%); -0.6215: 541 (40%); 0.4581: 271 (20%) | -3.7008: 271 (20%); -1.6232: 541 (40%); -0.6215: 811 (60%); 0.4581: 1081 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.1755, 0.1012, 0.3273, 0.79 | -0.1755: 1081 (80%); 0.1012: 812 (60%); 0.3273: 541 (40%); 0.79: 271 (20%) | -0.1755: 271 (20%); 0.1012: 541 (40%); 0.3273: 811 (60%); 0.79: 1081 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.3446, -1.0526, -0.3677, 0.2204 | -2.3446: 1081 (80%); -1.0526: 811 (60%); -0.3677: 541 (40%); 0.2204: 271 (20%) | -2.3446: 271 (20%); -1.0526: 541 (40%); -0.3677: 811 (60%); 0.2204: 1081 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -3.1401, -1.3762, -0.5285, 0.3655 | -3.1401: 1081 (80%); -1.3762: 811 (60%); -0.5285: 541 (40%); 0.3655: 271 (20%) | -3.1401: 271 (20%); -1.3762: 541 (40%); -0.5285: 811 (60%); 0.3655: 1081 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 40.11, 46.89, 52.61, 58.49 | 40.11: 1081 (80%); 46.89: 811 (60%); 52.61: 541 (40%); 58.49: 272 (20%) | 40.11: 271 (20%); 46.89: 541 (40%); 52.61: 811 (60%); 58.49: 1081 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0044, 0.0108, 0.0214, 0.0448 | 0.0044: 1068 (79%); 0.0108: 804 (60%); 0.0214: 535 (40%); 0.0448: 270 (20%) | 0.0044: 272 (20%); 0.0108: 536 (40%); 0.0214: 805 (60%); 0.0448: 1070 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 8 | 0: 1351 (100%); 1: 1011 (75%); 4: 541 (40%); 8: 305 (23%) | 0: 340 (25%); 1: 557 (41%); 4: 873 (65%); 8: 1085 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 1351 (100%); 0.1667: 285 (21%) | 0: 916 (68%); 0.1667: 1090 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0714, 0.375, 0.6667 | 0: 1351 (100%); 0.0714: 811 (60%); 0.375: 547 (40%); 0.6667: 285 (21%) | 0: 538 (40%); 0.0714: 541 (40%); 0.375: 819 (61%); 0.6667: 1116 (83%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 1351 (100%); 1: 931 (69%); 2: 688 (51%); 6: 301 (22%) | 0: 420 (31%); 1: 663 (49%); 2: 814 (60%); 6: 1102 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 8 | 0: 1351 (100%); 1: 1011 (75%); 4: 541 (40%); 8: 305 (23%) | 0: 340 (25%); 1: 557 (41%); 4: 873 (65%); 8: 1085 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1351 (100%); 1: 955 (71%); 3: 579 (43%); 7: 291 (22%) | 0: 396 (29%); 1: 642 (48%); 3: 886 (66%); 7: 1101 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1778, 0.3333, 0.5276 | 0: 1214 (90%); 0.1778: 811 (60%); 0.3333: 553 (41%); 0.5276: 271 (20%) | 0: 347 (26%); 0.1778: 541 (40%); 0.3333: 836 (62%); 0.5276: 1081 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1395, 0.5 | 0: 1208 (89%); 0.1395: 541 (40%); 0.5: 286 (21%) | 0: 757 (56%); 0.1395: 811 (60%); 0.5: 1084 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5364 | 0: 1204 (89%); 0.25: 555 (41%); 0.5364: 271 (20%) | 0: 628 (46%); 0.25: 812 (60%); 0.5364: 1081 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5364 | 0: 1204 (89%); 0.25: 555 (41%); 0.5364: 271 (20%) | 0: 628 (46%); 0.25: 812 (60%); 0.5364: 1081 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.125, 0, 0.1481 | -0.125: 1081 (80%); 0: 987 (73%); 0.1481: 271 (20%) | -0.125: 271 (20%); 0: 979 (72%); 0.1481: 1081 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7328, -0.2627, 0.1133, 1.3212 | -0.7328: 1081 (80%); -0.2627: 811 (60%); 0.1133: 541 (40%); 1.3212: 271 (20%) | -0.7328: 273 (20%); -0.2627: 541 (40%); 0.1133: 811 (60%); 1.3212: 1084 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 10 | 2: 1134 (84%); 4: 861 (64%); 7: 555 (41%); 10: 313 (23%) | 2: 337 (25%); 4: 576 (43%); 7: 895 (66%); 10: 1092 (81%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0289, -0.0053, 0.0128, 0.0376 | -0.0289: 1080 (80%); -0.0053: 810 (60%); 0.0128: 539 (40%); 0.0376: 270 (20%) | -0.0289: 271 (20%); -0.0053: 541 (40%); 0.0128: 812 (60%); 0.0376: 1081 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0749, -0.0395, -0.0113, 0.0203 | -0.0749: 1080 (80%); -0.0395: 811 (60%); -0.0113: 540 (40%); 0.0203: 270 (20%) | -0.0749: 271 (20%); -0.0395: 540 (40%); -0.0113: 811 (60%); 0.0203: 1081 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0238, -0.0009, 0.0201, 0.0505 | -0.0238: 1079 (80%); -0.0009: 810 (60%); 0.0201: 541 (40%); 0.0505: 270 (20%) | -0.0238: 272 (20%); -0.0009: 541 (40%); 0.0201: 810 (60%); 0.0505: 1081 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -23.742, -11.541, -1.279, 13.102 | -23.742: 1082 (80%); -11.541: 811 (60%); -1.279: 541 (40%); 13.102: 271 (20%) | -23.742: 271 (20%); -11.541: 541 (40%); -1.279: 811 (60%); 13.102: 1081 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.039, 0.0528, 0.0702, 0.0958 | 0.039: 1086 (80%); 0.0528: 815 (60%); 0.0702: 541 (40%); 0.0958: 272 (20%) | 0.039: 271 (20%); 0.0528: 541 (40%); 0.0702: 811 (60%); 0.0958: 1082 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.2646, 0.5313, 0.7343, 0.8912 | 0.2646: 1081 (80%); 0.5313: 811 (60%); 0.7343: 541 (40%); 0.8912: 271 (20%) | 0.2646: 271 (20%); 0.5313: 541 (40%); 0.7343: 811 (60%); 0.8912: 1081 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.884, -1.7885, -0.9282, 0.6052 | -2.884: 1081 (80%); -1.7885: 811 (60%); -0.9282: 541 (40%); 0.6052: 271 (20%) | -2.884: 271 (20%); -1.7885: 541 (40%); -0.9282: 811 (60%); 0.6052: 1081 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.2526, 0.1149, 0.3317, 0.5958 | -0.2526: 1081 (80%); 0.1149: 811 (60%); 0.3317: 541 (40%); 0.5958: 271 (20%) | -0.2526: 271 (20%); 0.1149: 542 (40%); 0.3317: 812 (60%); 0.5958: 1081 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -3.396, -2.1338, -1.1454, 0.7657 | -3.396: 1081 (80%); -2.1338: 811 (60%); -1.1454: 541 (40%); 0.7657: 271 (20%) | -3.396: 271 (20%); -2.1338: 541 (40%); -1.1454: 811 (60%); 0.7657: 1081 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -3.37, -0.993, 0.841, 3.494 | -3.37: 1081 (80%); -0.993: 811 (60%); 0.841: 541 (40%); 3.494: 271 (20%) | -3.37: 272 (20%); -0.993: 541 (40%); 0.841: 811 (60%); 3.494: 1081 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.79, 45.85, 49.39, 53.16 | 41.79: 1081 (80%); 45.85: 811 (60%); 49.39: 541 (40%); 53.16: 271 (20%) | 41.79: 271 (20%); 45.85: 541 (40%); 49.39: 811 (60%); 53.16: 1081 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 18.17, 56.96, 80.4, 91.32 | 18.17: 1081 (80%); 56.96: 811 (60%); 80.4: 541 (40%); 91.32: 271 (20%) | 18.17: 271 (20%); 56.96: 541 (40%); 80.4: 811 (60%); 91.32: 1083 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.35, 44.91, 48.29, 52.34 | 41.35: 1081 (80%); 44.91: 811 (60%); 48.29: 543 (40%); 52.34: 271 (20%) | 41.35: 271 (20%); 44.91: 542 (40%); 48.29: 811 (60%); 52.34: 1081 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.66, 47.46, 51.94, 56.81 | 41.66: 1081 (80%); 47.46: 813 (60%); 51.94: 541 (40%); 56.81: 271 (20%) | 41.66: 272 (20%); 47.46: 541 (40%); 51.94: 811 (60%); 56.81: 1082 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1350 (100%) | 0: 1351 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0321, 0.0484, 0.0629, 0.095 | 0.0321: 1085 (80%); 0.0484: 812 (60%); 0.0629: 542 (40%); 0.095: 271 (20%) | 0.0321: 273 (20%); 0.0484: 541 (40%); 0.0629: 811 (60%); 0.095: 1081 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0899, -0.0629, -0.0453, -0.0349 | -0.0899: 1081 (80%); -0.0629: 811 (60%); -0.0453: 541 (40%); -0.0349: 277 (21%) | -0.0899: 271 (20%); -0.0629: 541 (40%); -0.0453: 813 (60%); -0.0349: 1082 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1351 (100%); 1: 321 (24%) | 0: 1030 (76%); 1: 1153 (85%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 24, 38, 56, 67 | 24: 1099 (81%); 38: 815 (60%); 56: 557 (41%); 67: 273 (20%) | 24: 320 (24%); 38: 544 (40%); 56: 820 (61%); 67: 1081 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.5% | 0.012, 0.017, 0.0256, 0.0428 | 0.012: 1065 (79%); 0.017: 799 (59%); 0.0256: 532 (39%); 0.0428: 266 (20%) | 0.012: 267 (20%); 0.017: 532 (39%); 0.0256: 799 (59%); 0.0428: 1066 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 99.9% | 0.1779, 0.2714, 0.408, 0.6274 | 0.1779: 1081 (80%); 0.2714: 810 (60%); 0.408: 540 (40%); 0.6274: 270 (20%) | 0.1779: 272 (20%); 0.2714: 540 (40%); 0.408: 810 (60%); 0.6274: 1080 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 99.9% | 33.26, 71.1, 102.22, 143.14 | 33.26: 1080 (80%); 71.1: 811 (60%); 102.22: 540 (40%); 143.14: 270 (20%) | 33.26: 270 (20%); 71.1: 541 (40%); 102.22: 810 (60%); 143.14: 1080 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -2.5225, -0.665, 0.155, 1.245 | -2.5225: 1081 (80%); -0.665: 811 (60%); 0.155: 541 (40%); 1.245: 271 (20%) | -2.5225: 271 (20%); -0.665: 543 (40%); 0.155: 812 (60%); 1.245: 1081 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 30.35, 41.18, 50.95, 61.98 | 30.35: 1081 (80%); 41.18: 812 (60%); 50.95: 541 (40%); 61.98: 271 (20%) | 30.35: 271 (20%); 41.18: 541 (40%); 50.95: 811 (60%); 61.98: 1081 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 31.45, 44.63, 56.07, 67.52 | 31.45: 1081 (80%); 44.63: 811 (60%); 56.07: 541 (40%); 67.52: 271 (20%) | 31.45: 271 (20%); 44.63: 541 (40%); 56.07: 811 (60%); 67.52: 1082 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 23.31, 54.33, 80.08, 94.72 | 23.31: 1081 (80%); 54.33: 811 (60%); 80.08: 541 (40%); 94.72: 271 (20%) | 23.31: 271 (20%); 54.33: 541 (40%); 80.08: 811 (60%); 94.72: 1081 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 13.29, 60.57, 94.48, 100 | 13.29: 1081 (80%); 60.57: 811 (60%); 94.48: 541 (40%); 100: 479 (35%) | 13.29: 271 (20%); 60.57: 541 (40%); 94.48: 811 (60%); 100: 1351 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 17 | 4: 1118 (83%); 8: 823 (61%); 13: 554 (41%); 17: 349 (26%) | 4: 324 (24%); 8: 582 (43%); 13: 847 (63%); 17: 1088 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 18 | 5: 1085 (80%); 9: 837 (62%); 14: 571 (42%); 18: 302 (22%) | 5: 342 (25%); 9: 557 (41%); 14: 834 (62%); 18: 1121 (83%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 44.21, 49.35, 53.46, 57.79 | 44.21: 1081 (80%); 49.35: 812 (60%); 53.46: 541 (40%); 57.79: 271 (20%) | 44.21: 271 (20%); 49.35: 544 (40%); 53.46: 811 (60%); 57.79: 1081 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1746, 0.4921, 0.7222, 0.873 | 0.1746: 1083 (80%); 0.4921: 811 (60%); 0.7222: 547 (40%); 0.873: 293 (22%) | 0.1746: 276 (20%); 0.4921: 541 (40%); 0.7222: 814 (60%); 0.873: 1082 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.45, 18.21, 21.67, 26.7 | 15.45: 1081 (80%); 18.21: 811 (60%); 21.67: 545 (40%); 26.7: 278 (21%) | 15.45: 271 (20%); 18.21: 541 (40%); 21.67: 811 (60%); 26.7: 1081 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 15.45, 18.21, 21.67, 26.7 | 15.45: 1081 (80%); 18.21: 811 (60%); 21.67: 545 (40%); 26.7: 278 (21%) | 15.45: 271 (20%); 18.21: 541 (40%); 21.67: 811 (60%); 26.7: 1081 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8614, 0.8953, 0.9344, 0.9709 | 0.8614: 1086 (80%); 0.8953: 811 (60%); 0.9344: 543 (40%); 0.9709: 272 (20%) | 0.8614: 272 (20%); 0.8953: 544 (40%); 0.9344: 816 (60%); 0.9709: 1082 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.69, 0.81, 0.94, 1.19 | 0.69: 1091 (81%); 0.81: 831 (62%); 0.94: 550 (41%); 1.19: 272 (20%) | 0.69: 280 (21%); 0.81: 544 (40%); 0.94: 820 (61%); 1.19: 1086 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0129, 0.0338, 0.0668, 0.1066 | 0.0129: 1081 (80%); 0.0338: 812 (60%); 0.0668: 541 (40%); 0.1066: 271 (20%) | 0.0129: 272 (20%); 0.0338: 543 (40%); 0.0668: 812 (60%); 0.1066: 1081 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 39.5806, 65.7599, 101.1141, 166.7068 | 39.5806: 1081 (80%); 65.7599: 811 (60%); 101.1141: 541 (40%); 166.7068: 271 (20%) | 39.5806: 271 (20%); 65.7599: 541 (40%); 101.1141: 811 (60%); 166.7068: 1081 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 38.7194, 64.2132, 97.6789, 162.9372 | 38.7194: 1081 (80%); 64.2132: 811 (60%); 97.6789: 541 (40%); 162.9372: 271 (20%) | 38.7194: 271 (20%); 64.2132: 541 (40%); 97.6789: 811 (60%); 162.9372: 1081 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 37.0914, 62.3716, 94.4803, 159.6187 | 37.0914: 1081 (80%); 62.3716: 811 (60%); 94.4803: 541 (40%); 159.6187: 271 (20%) | 37.0914: 271 (20%); 62.3716: 541 (40%); 94.4803: 811 (60%); 159.6187: 1081 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 40.6008, 67.7767, 104.2646, 170.859 | 40.6008: 1081 (80%); 67.7767: 811 (60%); 104.2646: 541 (40%); 170.859: 271 (20%) | 40.6008: 271 (20%); 67.7767: 541 (40%); 104.2646: 811 (60%); 170.859: 1081 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 42.0319, 69.5225, 107.039, 175.8332 | 42.0319: 1081 (80%); 69.5225: 811 (60%); 107.039: 541 (40%); 175.8332: 271 (20%) | 42.0319: 271 (20%); 69.5225: 541 (40%); 107.039: 811 (60%); 175.8332: 1081 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1351 (100%) | 0: 1202 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1351 (100%) | 0: 1230 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.9% | -0.0544, -0.0255, -0.0044, 0.0201 | -0.0544: 1080 (80%); -0.0255: 810 (60%); -0.0044: 541 (40%); 0.0201: 270 (20%) | -0.0544: 272 (20%); -0.0255: 540 (40%); -0.0044: 811 (60%); 0.0201: 1080 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -72.68, -51.68, -35.43, -17.36 | -72.68: 1081 (80%); -51.68: 811 (60%); -35.43: 541 (40%); -17.36: 271 (20%) | -72.68: 271 (20%); -51.68: 541 (40%); -35.43: 811 (60%); -17.36: 1081 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.5606, 0.8201, 1.0369, 1.3091 | 0.5606: 1071 (79%); 0.8201: 803 (59%); 1.0369: 536 (40%); 1.3091: 268 (20%) | 0.5606: 268 (20%); 0.8201: 536 (40%); 1.0369: 805 (60%); 1.3091: 1071 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 1111 (82%); 5: 868 (64%); 7: 622 (46%); 9: 327 (24%) | 3: 343 (25%); 5: 574 (42%); 7: 861 (64%); 9: 1174 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.0% | 0.1934, 0.2347, 0.2841, 0.366 | 0.1934: 1071 (79%); 0.2347: 805 (60%); 0.2841: 537 (40%); 0.366: 268 (20%) | 0.1934: 269 (20%); 0.2347: 536 (40%); 0.2841: 803 (59%); 0.366: 1070 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.0% | 3, 5, 7.2, 9 | 3: 1140 (84%); 5: 905 (67%); 7.2: 535 (40%); 9: 363 (27%) | 3: 303 (22%); 5: 550 (41%); 7.2: 803 (59%); 9: 1153 (85%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0238, 0.0321, 0.0424, 0.0604 | 0.0238: 1071 (79%); 0.0321: 808 (60%); 0.0424: 536 (40%); 0.0604: 268 (20%) | 0.0238: 273 (20%); 0.0321: 539 (40%); 0.0424: 805 (60%); 0.0604: 1071 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 1136 (84%); 5: 878 (65%); 7: 632 (47%); 9: 325 (24%) | 3: 316 (23%); 5: 590 (44%); 7: 858 (64%); 9: 1163 (86%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.2% | -0.231, -0.0989, 0.0061, 0.1536 | -0.231: 1072 (79%); -0.0989: 804 (60%); 0.0061: 536 (40%); 0.1536: 268 (20%) | -0.231: 268 (20%); -0.0989: 536 (40%); 0.0061: 804 (60%); 0.1536: 1072 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.2% | 2, 3, 5, 8 | 2: 1126 (83%); 3: 923 (68%); 5: 621 (46%); 8: 283 (21%) | 2: 417 (31%); 3: 554 (41%); 5: 836 (62%); 8: 1173 (87%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 3.5% |
| 8k_item_5_02_filed_within_7d | 3.9% |
| above_avwap_20high | 48.2% |
| above_avwap_20low | 72.8% |
| above_avwap_252low | 65.2% |
| above_avwap_50low | 82.5% |
| above_cam_r3 | 45.9% |
| above_cam_r4 | 29.4% |
| above_cpr | 63.8% |
| above_pivot | 64.3% |
| above_prev_high | 38.2% |
| above_prev_high_clearance_atr_05 | 14.6% |
| above_prev_low | 80.6% |
| above_r1 | 33.1% |
| above_r2 | 16.5% |
| above_vwap | 37.4% |
| above_wood_p | 62.9% |
| ad_rising | 61.7% |
| adx_cross_up | 0.5% |
| adx_cross_up_20 | 0.7% |
| adx_di_bear | 68.4% |
| adx_di_bull | 31.6% |
| adx_strong | 8.7% |
| adx_trending | 44.8% |
| ao_cross_dn | 1.6% |
| ao_cross_up | 1.0% |
| ao_positive | 26.8% |
| ao_twin_peaks_bull | 6.6% |
| at_key_fib | 15.8% |
| at_key_fib_wide | 37.5% |
| avwap_20high_loss_recent_3d | 16.4% |
| avwap_20high_reclaim_recent_3d | 38.2% |
| avwap_20low_loss_recent_3d | 19.3% |
| avwap_20low_reclaim_recent_3d | 27.7% |
| avwap_252low_loss_recent_3d | 6.0% |
| avwap_252low_reclaim_recent_3d | 19.4% |
| avwap_50low_loss_recent_3d | 10.5% |
| avwap_50low_reclaim_recent_3d | 28.1% |
| bb_10_20_above_mid | 62.1% |
| bb_10_20_expanding | 61.1% |
| bb_10_20_pctb_gt_75 | 37.1% |
| bb_10_20_pctb_gt_8 | 31.8% |
| bb_10_20_pctb_gt_85 | 24.9% |
| bb_10_20_pctb_gt_9 | 18.3% |
| bb_10_20_pctb_gt_95 | 12.5% |
| bb_10_20_pctb_lt_05 | 8.2% |
| bb_10_20_pctb_lt_1 | 11.5% |
| bb_10_20_pctb_lt_15 | 15.1% |
| bb_10_20_pctb_lt_2 | 18.1% |
| bb_10_20_pctb_lt_25 | 22.4% |
| bb_10_20_reclaim_from_lower_recent_3d | 5.8% |
| bb_10_20_reclaim_from_upper_recent_3d | 5.0% |
| bb_10_20_squeeze | 52.3% |
| bb_10_20_touch_lower | 9.5% |
| bb_10_20_touch_upper | 14.0% |
| bb_20_15_above_mid | 48.9% |
| bb_20_15_expanding | 25.7% |
| bb_20_15_pctb_gt_75 | 16.3% |
| bb_20_15_pctb_gt_8 | 13.3% |
| bb_20_15_pctb_gt_85 | 11.0% |
| bb_20_15_pctb_gt_9 | 9.3% |
| bb_20_15_pctb_gt_95 | 7.3% |
| bb_20_15_pctb_lt_05 | 9.3% |
| bb_20_15_pctb_lt_1 | 10.9% |
| bb_20_15_pctb_lt_15 | 13.0% |
| bb_20_15_pctb_lt_2 | 15.5% |
| bb_20_15_pctb_lt_25 | 18.7% |
| bb_20_15_reclaim_from_lower_recent_3d | 10.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 3.5% |
| bb_20_15_squeeze | 43.7% |
| bb_20_15_touch_lower | 10.1% |
| bb_20_15_touch_upper | 8.5% |
| bb_20_20_above_mid | 48.9% |
| bb_20_20_expanding | 25.7% |
| bb_20_20_pctb_gt_75 | 11.8% |
| bb_20_20_pctb_gt_8 | 9.3% |
| bb_20_20_pctb_gt_85 | 6.7% |
| bb_20_20_pctb_gt_9 | 5.3% |
| bb_20_20_pctb_gt_95 | 3.6% |
| bb_20_20_pctb_lt_05 | 5.1% |
| bb_20_20_pctb_lt_1 | 6.4% |
| bb_20_20_pctb_lt_15 | 8.8% |
| bb_20_20_pctb_lt_2 | 10.9% |
| bb_20_20_pctb_lt_25 | 13.5% |
| bb_20_20_reclaim_from_lower_recent_3d | 4.0% |
| bb_20_20_reclaim_from_upper_recent_3d | 1.3% |
| bb_20_20_squeeze | 25.6% |
| bb_20_20_touch_lower | 5.6% |
| bb_20_20_touch_upper | 3.6% |
| bearish_engulfing | 3.1% |
| bearish_pin_bar | 5.0% |
| below_avwap_20high | 51.8% |
| below_avwap_20low | 27.2% |
| below_avwap_252low | 34.8% |
| below_avwap_50low | 17.5% |
| below_cam_s3 | 24.6% |
| below_cam_s4 | 15.9% |
| below_cpr | 35.6% |
| below_ema_20 | 56.7% |
| below_ema_200 | 73.2% |
| below_ema_200_break_recent_5d | 6.6% |
| below_ema_20_break_recent_5d | 25.1% |
| below_ema_21 | 57.7% |
| below_ema_21_break_recent_5d | 23.5% |
| below_ema_50 | 69.8% |
| below_ema_50_break_recent_5d | 9.6% |
| below_ema_9 | 39.4% |
| below_ema_9_break_recent_5d | 32.9% |
| below_prev_high | 61.5% |
| below_prev_low | 19.2% |
| below_prev_low_clearance_atr_05 | 9.5% |
| below_s1 | 18.1% |
| below_s2 | 9.6% |
| below_sma_20 | 51.1% |
| below_sma_200 | 71.5% |
| below_sma_21 | 54.1% |
| below_sma_50 | 70.3% |
| below_sma_9 | 37.2% |
| below_vwap | 62.6% |
| break_52w_high | 0.2% |
| break_52w_high_clearance_atr_05 | 0.1% |
| break_52w_low | 0.7% |
| bullish_engulfing | 4.6% |
| bullish_pin_bar | 4.2% |
| capitulation_recent_3d | 0.3% |
| ceo_buy | 1.7% |
| cfo_buy | 1.4% |
| chandelier_long_bullish | 61.9% |
| chandelier_long_flip_dn | 6.1% |
| chandelier_short_bearish | 77.5% |
| chandelier_short_flip_up | 9.5% |
| classification_change_from_tech | 50.0% |
| classification_change_to_defensive | 50.0% |
| close_above_open | 67.4% |
| close_below_open | 32.6% |
| close_in_bottom_40pct_of_range | 30.3% |
| close_in_top_40pct_of_range | 53.1% |
| cluster_buy | 1.5% |
| cmf_cross_dn | 4.4% |
| cmf_cross_up | 5.3% |
| cmf_negative | 52.6% |
| cmf_positive | 47.4% |
| concentrated_sell | 4.1% |
| cpr_narrow | 87.8% |
| cpr_narrow_tight | 24.8% |
| cup_handle_detected | 17.0% |
| cup_handle_neckline_break_retest_long | 0.4% |
| dc10_breakout_dn | 10.4% |
| dc10_breakout_dn_1pct | 16.5% |
| dc10_breakout_up | 16.4% |
| dc10_breakout_up_1pct | 25.4% |
| dc10_new_high | 20.9% |
| dc10_strong_breakout_dn | 4.4% |
| dc10_strong_breakout_up | 5.7% |
| dc20_breakout_dn | 4.3% |
| dc20_breakout_up | 2.7% |
| dc20_new_high | 3.8% |
| dc20_resistance_break_retest_strong | 1.1% |
| dc20_support_break_retest_strong | 3.9% |
| defensive_leadership | 59.7% |
| director_only_buy | 4.5% |
| doji | 3.3% |
| double_bottom_detected | 10.2% |
| double_top_detected | 12.8% |
| dpi_elevated | 55.3% |
| drying_volume_on_down_turn | 19.8% |
| drying_volume_on_up_turn | 48.3% |
| ema_20_50_bearish | 73.2% |
| ema_20_50_bullish | 26.8% |
| ema_20_50_death_cross | 0.7% |
| ema_20_50_golden_cross | 0.1% |
| ema_50_200_bearish | 68.5% |
| ema_50_200_bullish | 31.5% |
| ema_50_200_death_cross | 0.1% |
| ema_50_200_golden_cross | 0.1% |
| ema_9_21_bearish | 73.0% |
| ema_9_21_bullish | 27.0% |
| ema_9_21_death_cross | 2.5% |
| ema_9_21_golden_cross | 2.4% |
| evening_star | 4.8% |
| flag_bear_break_retest_short | 1.2% |
| flag_bear_broke | 1.3% |
| flag_bear_detected | 1.5% |
| flag_bull_break_retest_long | 0.8% |
| flag_bull_broke | 1.0% |
| flag_bull_detected | 1.0% |
| force_index_cross_dn | 8.5% |
| force_index_cross_up | 15.2% |
| force_index_positive | 48.7% |
| gap_dn_1_5pct | 8.4% |
| gap_dn_2pct | 5.3% |
| gap_up_1_5pct | 8.2% |
| gap_up_2pct | 5.8% |
| hammer | 3.2% |
| head_shoulders_bottom_detected | 2.9% |
| head_shoulders_top_detected | 3.6% |
| house_cluster_buy | 3.3% |
| house_cluster_sell | 4.1% |
| htf_aligned_bear | 58.0% |
| htf_aligned_bull | 18.1% |
| htf_disagreement | 1.2% |
| hull_bearish | 39.5% |
| hull_bullish | 60.5% |
| hull_flip_dn | 5.1% |
| hull_flip_up | 9.3% |
| ichi_above_cloud | 22.6% |
| ichi_above_cloud_break_recent_5d | 3.8% |
| ichi_below_cloud | 67.9% |
| ichi_below_cloud_break_recent_5d | 4.8% |
| ichi_cloud_thick | 83.8% |
| ichi_tk_bearish | 69.6% |
| ichi_tk_bullish | 26.6% |
| ichi_tk_cross_dn | 2.0% |
| ichi_tk_cross_up | 1.5% |
| ichi_weekly_above_cloud | 23.8% |
| ichi_weekly_below_cloud | 42.3% |
| ichi_weekly_in_cloud | 33.9% |
| in_reversal_window | 2.3% |
| inside_bar | 11.8% |
| inside_cpr | 2.4% |
| inside_kc | 93.9% |
| insider_cluster_active | 39.8% |
| institutional_buy | 89.3% |
| institutional_negative | 4.2% |
| institutional_persistence_growing | 42.9% |
| institutional_persistence_strong | 59.3% |
| institutional_strong_buy | 78.1% |
| inverted_cup_handle_detected | 15.2% |
| is_friday | 20.2% |
| is_halloween_period | 49.6% |
| is_halloween_period_first_day | 0.3% |
| is_january | 8.1% |
| is_january_extended | 9.8% |
| is_monday | 17.3% |
| is_pre_holiday | 5.8% |
| is_summer_period | 50.4% |
| is_totm_window | 36.9% |
| is_totm_window_first_day | 10.4% |
| is_week_open | 20.8% |
| kc_touch_lower | 4.7% |
| kc_touch_upper | 2.6% |
| large_dollar_buy | 1.3% |
| macd_12_26_9_bearish | 33.0% |
| macd_12_26_9_bullish | 67.0% |
| macd_12_26_9_crossover_dn | 5.3% |
| macd_12_26_9_crossover_up | 6.6% |
| macd_8_21_5_bearish | 32.3% |
| macd_8_21_5_bullish | 67.7% |
| macd_8_21_5_crossover_dn | 3.3% |
| macd_8_21_5_crossover_up | 4.9% |
| marubozu_bear | 0.9% |
| marubozu_bull | 1.8% |
| mfi_broad_overbought | 2.4% |
| mfi_broad_oversold | 5.0% |
| mfi_overbought | 0.4% |
| mfi_oversold | 0.2% |
| monthly_above_sma_12 | 28.3% |
| monthly_above_sma_6 | 26.8% |
| monthly_bias_bear | 65.9% |
| monthly_bias_bull | 21.0% |
| monthly_momentum_pos | 32.3% |
| morning_star | 6.7% |
| near_52w_high | 1.4% |
| near_52w_high_95pct | 7.0% |
| near_52w_high_retest_long | 0.1% |
| near_52w_low | 1.8% |
| near_52w_low_105pct | 9.7% |
| near_52w_low_retest_short | 0.2% |
| near_avwap_20high_atr_05x | 41.7% |
| near_avwap_20high_atr_10x | 71.7% |
| near_avwap_20high_atr_15x | 87.0% |
| near_avwap_20high_atr_20x | 95.6% |
| near_avwap_20low_atr_05x | 33.1% |
| near_avwap_20low_atr_10x | 64.9% |
| near_avwap_20low_atr_15x | 84.2% |
| near_avwap_20low_atr_20x | 92.9% |
| near_avwap_252low_atr_05x | 17.2% |
| near_avwap_252low_atr_10x | 38.0% |
| near_avwap_252low_atr_15x | 53.3% |
| near_avwap_252low_atr_20x | 63.8% |
| near_avwap_50low_atr_05x | 27.0% |
| near_avwap_50low_atr_10x | 57.6% |
| near_avwap_50low_atr_15x | 78.2% |
| near_avwap_50low_atr_20x | 87.8% |
| near_cam_r3 | 15.6% |
| near_cam_s3 | 10.7% |
| near_cam_s4 | 7.2% |
| near_fib_236 | 4.1% |
| near_fib_382 | 5.1% |
| near_fib_500 | 4.2% |
| near_fib_618 | 6.7% |
| near_fib_786 | 7.8% |
| near_pivot | 13.2% |
| near_prev_close | 14.3% |
| near_prev_high | 13.0% |
| near_prev_low | 7.5% |
| near_r1 | 13.0% |
| near_r1_wide | 56.2% |
| near_r2 | 6.2% |
| near_r2_wide | 37.7% |
| near_s1 | 7.5% |
| near_s1_wide | 36.9% |
| near_s2 | 2.8% |
| near_s2_wide | 21.6% |
| near_s3 | 2.3% |
| near_wood_r1 | 10.7% |
| near_wood_s1 | 7.1% |
| news_uses_polygon_score | 21.1% |
| obv_bearish | 49.4% |
| obv_bullish | 50.6% |
| obv_diverge_bull | 8.3% |
| obv_falling | 41.5% |
| obv_rising | 58.5% |
| outside_bar | 9.5% |
| pead_negative_surprise | 21.2% |
| pead_positive_surprise | 18.4% |
| pin_bar | 9.3% |
| po3_accumulation_active | 35.9% |
| po3_bearish | 5.6% |
| po3_bullish | 10.8% |
| po3_manipulation_sweep_down | 10.0% |
| po3_manipulation_sweep_up | 10.6% |
| po3_mmbm_setup | 1.2% |
| po3_mmsm_setup | 0.6% |
| po3_sweep_above_prior_high | 61.1% |
| po3_sweep_below_prior_low | 42.5% |
| ppo_bullish | 65.9% |
| ppo_crossover_dn | 5.0% |
| ppo_crossover_up | 7.5% |
| pre_fomc_d0 | 2.6% |
| pre_fomc_d1 | 2.1% |
| pre_fomc_window | 4.7% |
| price_above_dema | 67.4% |
| price_above_ema_20 | 43.3% |
| price_above_ema_200 | 26.8% |
| price_above_ema_200_break_recent_5d | 5.5% |
| price_above_ema_20_break_recent_5d | 36.2% |
| price_above_ema_21 | 42.3% |
| price_above_ema_21_break_recent_5d | 34.3% |
| price_above_ema_50 | 30.2% |
| price_above_ema_50_break_recent_5d | 12.8% |
| price_above_ema_9 | 60.6% |
| price_above_ema_9_break_recent_5d | 57.0% |
| price_above_hull | 65.7% |
| price_above_sma_200 | 28.5% |
| price_above_sma_21 | 45.9% |
| price_above_sma_50 | 29.7% |
| price_above_tema | 67.4% |
| price_below_dema | 32.6% |
| price_below_hull | 34.3% |
| price_below_tema | 32.6% |
| psar_bullish | 56.5% |
| psar_flip_dn | 4.5% |
| psar_flip_up | 9.2% |
| r1_break_retest_long | 60.0% |
| recent_capitulation_at_s3 | 0.1% |
| resistance_break_retest | 1.9% |
| risk_off_regime_bond_signal | 25.9% |
| risk_off_regime_bond_signal_strong | 9.0% |
| risk_off_regime_gold_signal | 45.4% |
| risk_on_regime_bond_signal | 39.8% |
| risk_on_regime_bond_signal_strong | 16.1% |
| roc_positive | 50.3% |
| roc_turning_dn | 11.3% |
| roc_turning_up | 17.8% |
| rsi_14_bullish | 36.3% |
| rsi_14_cross_dn_overbought_recent_3d | 1.3% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_14_cross_up_oversold_recent_3d | 4.7% |
| rsi_14_extreme_os | 0.2% |
| rsi_14_overbought | 0.4% |
| rsi_14_oversold | 1.5% |
| rsi_14_rising | 61.7% |
| rsi_21_bullish | 31.2% |
| rsi_21_cross_dn_overbought_recent_3d | 0.5% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 2.4% |
| rsi_21_extreme_os | 0.1% |
| rsi_21_overbought | 0.1% |
| rsi_21_oversold | 0.6% |
| rsi_21_rising | 61.7% |
| rsi_2_bullish | 63.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 21.3% |
| rsi_2_cross_dn_overbought_recent_3d | 25.5% |
| rsi_2_cross_up_extreme_os_recent_3d | 27.5% |
| rsi_2_cross_up_oversold_recent_3d | 36.0% |
| rsi_2_extreme_ob | 40.8% |
| rsi_2_extreme_os | 20.9% |
| rsi_2_overbought | 52.0% |
| rsi_2_oversold | 26.9% |
| rsi_2_rising | 61.7% |
| rsi_9_bullish | 49.2% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_9_cross_dn_overbought_recent_3d | 3.2% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.8% |
| rsi_9_cross_up_oversold_recent_3d | 8.1% |
| rsi_9_extreme_ob | 0.1% |
| rsi_9_extreme_os | 0.2% |
| rsi_9_overbought | 1.6% |
| rsi_9_oversold | 4.3% |
| rsi_9_rising | 61.7% |
| s1_break_retest_short | 43.3% |
| sc_13d_filed_within_30d | 3.0% |
| sc_13g_filed_within_30d | 2.9% |
| sector_outperforming_spy | 37.5% |
| sector_underperforming_spy | 62.5% |
| shooting_star | 4.3% |
| sma_20_50_bullish | 27.6% |
| sma_20_50_golden_cross | 0.1% |
| sma_50_200_bullish | 34.4% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 28.8% |
| sma_9_21_golden_cross | 2.1% |
| smc_bos_bearish | 20.4% |
| smc_bos_bullish | 7.0% |
| smc_bos_retest_long | 3.7% |
| smc_bos_retest_short | 5.1% |
| smc_breaker_block_bearish | 20.8% |
| smc_breaker_block_bullish | 14.6% |
| smc_choch_bearish | 7.7% |
| smc_choch_bullish | 2.1% |
| smc_equal_highs_swept | 1.8% |
| smc_equal_lows_swept | 5.6% |
| smc_fvg_bearish_active | 31.2% |
| smc_fvg_bullish_active | 40.7% |
| smc_fvg_retest_long_zone | 3.0% |
| smc_fvg_retest_short_zone | 6.7% |
| smc_in_discount_zone | 78.0% |
| smc_in_premium_zone | 41.0% |
| smc_inverse_fvg_bearish | 91.7% |
| smc_inverse_fvg_bullish | 74.9% |
| smc_liquidity_swept_dn | 1.0% |
| smc_liquidity_swept_up | 1.3% |
| smc_mitigation_block_long | 1.2% |
| smc_mitigation_block_short | 0.8% |
| smc_ob_bearish_active | 52.9% |
| smc_ob_bullish_active | 17.2% |
| smc_ote_long_zone | 8.6% |
| smc_ote_short_zone | 4.4% |
| squeeze_fire_dn | 4.6% |
| squeeze_fire_up | 9.5% |
| squeeze_in | 36.2% |
| squeeze_positive | 43.9% |
| stoch_bearish_cross | 7.4% |
| stoch_broad_overbought | 11.4% |
| stoch_broad_oversold | 12.7% |
| stoch_bullish_cross | 9.1% |
| stoch_overbought | 6.6% |
| stoch_oversold | 7.2% |
| stochrsi_cross_dn | 16.2% |
| stochrsi_cross_up | 17.6% |
| stochrsi_overbought | 49.5% |
| stochrsi_oversold | 23.1% |
| supertrend_bearish | 1.9% |
| supertrend_bullish | 98.1% |
| supertrend_flip_dn | 1.3% |
| supertrend_flip_recent_long_5d | 0.7% |
| supertrend_flip_recent_short_5d | 2.1% |
| supertrend_flip_up | 0.1% |
| support_break_retest | 6.8% |
| tema_above_dema | 67.4% |
| tema_cross_dn | 32.6% |
| tema_cross_up | 67.4% |
| three_black_crows | 5.9% |
| three_white_soldiers | 11.2% |
| triangle_apex_break_retest_long | 7.7% |
| triangle_ascending_detected | 6.5% |
| triangle_descending_detected | 7.9% |
| uo_overbought | 0.7% |
| uo_oversold | 0.8% |
| usd_strengthening | 25.7% |
| usd_weakening | 12.3% |
| vix_band_high | 47.9% |
| vix_band_low | 30.6% |
| vix_band_mid | 21.5% |
| vix_term_backwardation | 10.0% |
| vix_term_contango | 90.0% |
| vol_above_avg | 31.8% |
| vol_below_avg | 68.2% |
| vol_spike_12x | 19.5% |
| vol_spike_15x | 10.1% |
| vol_spike_17x | 7.0% |
| vol_spike_2x | 4.4% |
| vol_spike_2x_on_down_day_recent_3d | 2.0% |
| vol_spike_2x_on_up_day_recent_3d | 2.4% |
| vol_spike_3x | 1.5% |
| vp_above_value_area | 9.6% |
| vp_below_value_area | 24.1% |
| vp_close_above_poc | 37.6% |
| vp_close_below_poc | 62.4% |
| vp_in_value_area | 66.2% |
| week_open_gap_down_15pct | 2.4% |
| week_open_gap_up_15pct | 1.3% |
| weekly_above_ema_10 | 30.7% |
| weekly_above_ema_20 | 27.3% |
| weekly_bias_bear | 66.1% |
| weekly_bias_bull | 24.1% |
| weekly_momentum_pos | 35.8% |
| williams_r_overbought | 22.6% |
| williams_r_oversold | 14.9% |
| williams_r_rising | 62.7% |
| within_pead_window | 35.0% |
| within_post_deletion_window | 5.7% |
| xs_avoid_high_ivol | 72.9% |
| xs_avoid_high_max | 75.7% |
| xs_high_beta_decile | 24.4% |
| xs_low_beta_bottom_quintile | 24.4% |
| xs_low_beta_decile | 17.0% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 17.0% |
| xs_momentum_bottom_decile | 16.0% |
| xs_momentum_bottom_quintile | 31.1% |
| xs_momentum_top_decile | 6.3% |
| xs_momentum_top_quintile | 12.5% |
| xs_quality_bottom_quintile | 23.9% |
| xs_quality_top_quintile | 19.9% |
| xs_quality_top_tercile | 38.6% |
| year_high_break_retest_long | 0.4% |
| year_low_break_retest_short | 1.6% |
| yoy_surprise_high | 43.9% |
| yoy_surprise_negative | 45.8% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.8% |
| committed_growth_holders | 90.8% |
| corp_donations_1y | 7.4% |
| corp_donations_count_1y | 7.4% |
| corp_donations_unique_pacs | 7.4% |
| cot_rut_commercials_pctile_3y | 50.1% |
| cot_rut_mmoney_pctile_3y | 50.1% |
| cup_handle_depth_pct | 21.5% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 7.8% |
| days_since_inclusion | 12.7% |
| days_to_next_holiday | 61.1% |
| days_to_rebalance | 11.8% |
| dpi_30d_avg | 95.6% |
| dpi_recent | 95.6% |
| earnings_announcement_return | 89.9% |
| earnings_eps_yoy_growth | 93.6% |
| flag_bear_pole_move_pct | 1.5% |
| flag_bull_pole_move_pct | 1.0% |
| gov_contracts_4q_sum | 38.5% |
| gov_contracts_last_qtr_amount | 38.5% |
| gov_contracts_qoq_growth | 38.5% |
| head_shoulders_magnitude_pct | 6.4% |
| insider_director_buyers_30d | 7.3% |
| insider_officer_buyers_30d | 7.3% |
| insider_total_shares_bought_30d | 7.3% |
| insider_unique_buyers_30d | 7.3% |
| inverted_cup_handle_height_pct | 18.9% |
| lobbying_amount_1y | 70.4% |
| lobbying_amount_q | 70.4% |
| lobbying_amount_yoy | 70.4% |
| monthly_momentum_6m | 97.1% |
| otc_short_ratio_recent | 95.6% |
| otc_volume_recent | 95.6% |
| pair_half_life | 91.9% |
| pair_max_abs_zscore | 91.9% |
| pair_zscore_signed | 91.9% |
| pct_from_avwap_20high | 95.6% |
| pct_from_avwap_20low | 93.1% |
| pct_from_avwap_252low | 95.6% |
| pct_from_avwap_50low | 95.6% |
| persistent_holders_4q | 90.8% |
| persistent_holders_8q | 90.8% |
| sc_13g_latest_percent_owned | 1.5% |
| search_volume_index_recent | 77.9% |
| search_volume_observations | 77.9% |
| search_volume_zscore_30d | 77.9% |
| sector_etf_return_20d | 2.4% |
| spy_return_20d | 2.4% |
| total_active_holders | 90.8% |
| triangle_breakdown_pct | 7.9% |
| triangle_breakout_pct | 6.5% |
| xs_quality_decile | 59.7% |
| xs_quality_gross_profitability | 59.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (1.0), `avwap_252low` (0.996), `avwap_50low` (1.0), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.997), `chandelier_short_value` (0.999), `cpr_bottom` (1.0), `cpr_top` (0.999), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.995), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (1.0), `dc20_lower` (0.999), `dc20_mid` (0.999), `dc20_upper` (0.997), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.999), `double_top_neckline` (0.995), `double_top_peak` (0.997), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.993), `fib_382` (0.994), `fib_500` (0.996), `fib_618` (0.997), `fib_786` (0.998), `fib_ext_127` (0.986), `fib_ext_162` (0.982), `flag_bear_breakdown_level` (0.998), `flag_bull_breakout_level` (0.982), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.999), `ichi_kijun` (0.998), `ichi_senkou_a` (0.991), `ichi_senkou_b` (0.988), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.999), `monthly_sma_12` (0.982), `monthly_sma_6` (0.994), `pivot` (1.0), `prev_close` (0.999), `prev_high` (1.0), `prev_low` (0.999), `psar_value` (0.997), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.998), `swing_high` (0.99), `swing_low` (0.998), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.994), `vp_value_area_high` (0.993), `vp_value_area_low` (0.996), `weekly_close` (0.999), `weekly_ema_10` (0.998), `weekly_ema_20` (0.995), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.962), `year_low` (0.984)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | buffer above TEMA (close > tema x (1 + b | 4 | subset-safe | no - derives offline | 1 | 3 | 0 |
| P4.1 | TEMA / DEMA EMA period (one period drive | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P5 | ao <= 2.866 | 5 | subset-safe | no - derives offline | 1 | 4 | 0 |
| P6 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     4 x 3 x 5 x 1 = 60
offline gradings   19 level-combinations x 24 exits = 456 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  40 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 19 + 40 = 60 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 647 census axes join it only when REGISTERED at the T3 band review.
