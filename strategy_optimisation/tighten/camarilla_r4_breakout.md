# Table A - camarilla_r4_breakout

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 06a7ff8bb | commit 06a7ff8bb at 2026-10-27 11:24:05 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** pivot | **status:** IN-CAMPAIGN | **R5 fires:** 5774 (closed fires in the exit cube: 5774 of 5774, S6-B3258) | **surviving fires (T1):** 3073 (survives_pct 0.5322)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  above_cam_r4  <- backtest/signals/technical.py
       DEFN: today's close above Camarilla R4 = prior close + 1.1/2 x prior range (technical.py compute_pivots)
       knobs P1.1-P1.1 (band rows in Table A)
P2  below_cam_s4  <- backtest/signals/technical.py
       DEFN: today's close below Camarilla S4 = prior close - 1.1/2 x prior range (technical.py compute_pivots)
       knobs P2.1-P2.1 (band rows in Table A)
P3  vol_above_avg  <- backtest/signals/technical.py
       DEFN: volume / 20d average >= 1.0 (technical.py:1600)
       knobs P3.1-P3.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P4  xs_ivol >= 0.2598   [EXISTING-THRESHOLD]
P5  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_camarilla_r4_breakout (docstring and return dropped):

```python
fl = s.get('above_cam_r4') and s.get('vol_above_avg')
fl = fl and s.get('xs_ivol', float('-inf')) >= 0.2598
fs = (s.get('below_cam_s4') and s.get('vol_above_avg')) and (not _short_borrow_trap_active(s))
fs = fs and s.get('xs_ivol', float('-inf')) >= 0.2598
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
| P1 | PRODUCER | above_cam_r4 - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | today's close above Camarilla R4 = prior close + 1.1/2 x prior range (technical.py compute_pivots) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P1.1 | BAND | R4 distance from the prior close, in prior ranges (R4 = C + 1.1/2 x range) - backtest/signals/technical.py compute_pivots (Camarilla block) | MEASURED - production is the Camarilla 1.1 / 2; the tighter levels sit near the R5 fires' distance quantiles (q20 0.72, q40 0.94, q60 1.24 prior ranges); 0.45 the one looser bracket | 0.55 | 0.45, 0.55, 0.75, 1, 1.25 | offline 3 of 5 levels - TIGHTER (0.75, 1.0, 1.25) - derivable from the persisted prev_close / prev_high / prev_low and a close recovered as vwap x (1 + pct_from_vwap / 100); both legs reproduce on 5774 of 5774 R5 fires (output_audit/b3304_camarilla_distance_derivability.json); the derive module, the S6-B3290b pattern, is not built | LOOSER (0.45) - adds fires the cube never recorded; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | below_cam_s4 - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | today's close below Camarilla S4 = prior close - 1.1/2 x prior range (technical.py compute_pivots) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P2.1 | BAND | mirror of above_cam_r4 (S4 = C - 1.1/2 x range) - backtest/signals/technical.py compute_pivots (Camarilla block) | mirror | 0.55 | as long, mirrored | counted on the mirrored leg - TIGHTER - mirrored, on the same persisted keys | LOOSER - mirrored; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | vol_above_avg - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average >= 1.0 (technical.py:1600) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P3.1 | BAND | volume ratio floor (vol / avg) - backtest/signals/technical.py:1600 | BRACKET production 1.0; avg window is the second knob [10, 20, 50] | 1.0 | [1.0, 1.2, 1.5, 2.0] | offline 3 of 4 levels - TIGHTER floors where the vol ratio key is persisted on the fires; else none | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | STRATEGY | xs_ivol `>= 0.2598` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 0.2598` | production + 4 tighter measured levels | offline 4 of 5 levels - measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| xs_ivol | backtest/signals/cross_sectional.py | `>= 0.2598` | 100.0% | TIGHTER = RAISE the floor: 0.2918 -> 2459 (80%); 0.3301 -> 1845 (60%); 0.3814 -> 1230 (40%); 0.4621 -> 615 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 17.034, 20.94, 25.212, 31.584 | 17.034: 2458 (80%); 20.94: 1845 (60%); 25.212: 1229 (40%); 31.584: 615 (20%) | 17.034: 615 (20%); 20.94: 1232 (40%); 25.212: 1844 (60%); 31.584: 2458 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 19.628, 24.19, 28.46, 33.296 | 19.628: 2458 (80%); 24.19: 1846 (60%); 28.46: 1232 (40%); 33.296: 615 (20%) | 19.628: 615 (20%); 24.19: 1230 (40%); 28.46: 1845 (60%); 33.296: 2458 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 16.14, 20.08, 24.532, 30.078 | 16.14: 2460 (80%); 20.08: 1845 (60%); 24.532: 1229 (40%); 30.078: 615 (20%) | 16.14: 616 (20%); 20.08: 1231 (40%); 24.532: 1844 (60%); 30.078: 2458 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -7.943, -2.6261, -0.1266, 3.7438 | -7.943: 2458 (80%); -2.6261: 1844 (60%); -0.1266: 1229 (40%); 3.7438: 615 (20%) | -7.943: 615 (20%); -2.6261: 1229 (40%); -0.1266: 1844 (60%); 3.7438: 2458 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.3081, 2.4856, 4.1368, 7.3575 | 1.3081: 2458 (80%); 2.4856: 1844 (60%); 4.1368: 1229 (40%); 7.3575: 615 (20%) | 1.3081: 615 (20%); 2.4856: 1229 (40%); 4.1368: 1844 (60%); 7.3575: 2458 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.3081, 2.4856, 4.1368, 7.3575 | 1.3081: 2458 (80%); 2.4856: 1844 (60%); 4.1368: 1229 (40%); 7.3575: 615 (20%) | 1.3081: 615 (20%); 2.4856: 1229 (40%); 4.1368: 1844 (60%); 7.3575: 2458 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.925, 3.519, 4.1444, 5.1556 | 2.925: 2459 (80%); 3.519: 1845 (60%); 4.1444: 1229 (40%); 5.1556: 615 (20%) | 2.925: 617 (20%); 3.519: 1230 (40%); 4.1444: 1844 (60%); 5.1556: 2458 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0888, 0.1251, 0.1671, 0.2308 | 0.0888: 2459 (80%); 0.1251: 1844 (60%); 0.1671: 1231 (40%); 0.2308: 615 (20%) | 0.0888: 616 (20%); 0.1251: 1231 (40%); 0.1671: 1846 (60%); 0.2308: 2459 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1499, 0.3491, 0.5418, 0.8114 | 0.1499: 2458 (80%); 0.3491: 1844 (60%); 0.5418: 1229 (40%); 0.8114: 615 (20%) | 0.1499: 615 (20%); 0.3491: 1229 (40%); 0.5418: 1844 (60%); 0.8114: 2458 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0915, 0.119, 0.148, 0.2028 | 0.0915: 2461 (80%); 0.119: 1845 (60%); 0.148: 1231 (40%); 0.2028: 615 (20%) | 0.0915: 616 (20%); 0.119: 1230 (40%); 0.148: 1845 (60%); 0.2028: 2458 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0, 0.2386, 0.5384, 0.8783 | 0: 2458 (80%); 0.2386: 1844 (60%); 0.5384: 1229 (40%); 0.8783: 616 (20%) | 0: 615 (20%); 0.2386: 1229 (40%); 0.5384: 1844 (60%); 0.8783: 2459 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.122, 0.1586, 0.1973, 0.2705 | 0.122: 2461 (80%); 0.1586: 1846 (60%); 0.1973: 1231 (40%); 0.2705: 615 (20%) | 0.122: 616 (20%); 0.1586: 1230 (40%); 0.1973: 1845 (60%); 0.2705: 2458 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.125, 0.304, 0.5287, 0.7837 | 0.125: 2459 (80%); 0.304: 1844 (60%); 0.5287: 1230 (40%); 0.7837: 616 (20%) | 0.125: 615 (20%); 0.304: 1229 (40%); 0.5287: 1844 (60%); 0.7837: 2459 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0431, -0.019, 0.0021, 0.0204 | -0.0431: 2458 (80%); -0.019: 1850 (60%); 0.0021: 1232 (40%); 0.0204: 620 (20%) | -0.0431: 615 (20%); -0.019: 1231 (40%); 0.0021: 1873 (61%); 0.0204: 2463 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1371, 0.162, 0.1871, 0.2649 | 0.1371: 2458 (80%); 0.162: 1702 (55%); 0.1871: 1226 (40%); 0.2649: 616 (20%) | 0.1371: 615 (20%); 0.162: 1371 (45%); 0.1871: 1847 (60%); 0.2649: 2457 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 3073 (100%) | 0: 2897 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1231, -0.0369, 0.0382, 0.121 | -0.1231: 2459 (80%); -0.0369: 1844 (60%); 0.0382: 1229 (40%); 0.121: 615 (20%) | -0.1231: 616 (20%); -0.0369: 1230 (40%); 0.0382: 1844 (60%); 0.121: 2458 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 3073 (100%); 1: 1167 (38%) | 0: 1906 (62%); 1: 2558 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2452, -0.1931, -0.1541, -0.1141 | -0.2452: 2474 (81%); -0.1931: 1845 (60%); -0.1541: 1236 (40%); -0.1141: 677 (22%) | -0.2452: 620 (20%); -0.1931: 1240 (40%); -0.1541: 1849 (60%); -0.1141: 2654 (86%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2064, 0.5897, 0.6731, 0.7692 | 0.2064: 2458 (80%); 0.5897: 1890 (62%); 0.6731: 1332 (43%); 0.7692: 767 (25%) | 0.2064: 615 (20%); 0.5897: 1238 (40%); 0.6731: 1875 (61%); 0.7692: 2594 (84%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2821, 0.4295, 0.6346, 0.8795 | 0.2821: 2468 (80%); 0.4295: 1899 (62%); 0.6346: 1231 (40%); 0.8795: 615 (20%) | 0.2821: 643 (21%); 0.4295: 1231 (40%); 0.6346: 1857 (60%); 0.8795: 2458 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0831, -0.0047, 0.0498, 0.1946 | -0.0831: 2459 (80%); -0.0047: 1859 (60%); 0.0498: 1263 (41%); 0.1946: 617 (20%) | -0.0831: 629 (20%); -0.0047: 1232 (40%); 0.0498: 1846 (60%); 0.1946: 2463 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3013, 0.4808, 0.5897, 0.7628 | 0.3013: 2486 (81%); 0.4808: 1866 (61%); 0.5897: 1269 (41%); 0.7628: 627 (20%) | 0.3013: 619 (20%); 0.4808: 1243 (40%); 0.5897: 1858 (60%); 0.7628: 2463 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3205, 0.4551, 0.6154 | 0.1474: 2462 (80%); 0.3205: 1858 (60%); 0.4551: 1414 (46%); 0.6154: 629 (20%) | 0.1474: 666 (22%); 0.3205: 1237 (40%); 0.4551: 1946 (63%); 0.6154: 2471 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.497, -0.3214, -0.0978, 0.0839 | -0.497: 2512 (82%); -0.3214: 1845 (60%); -0.0978: 1269 (41%); 0.0839: 645 (21%) | -0.497: 662 (22%); -0.3214: 1256 (41%); -0.0978: 1863 (61%); 0.0839: 2467 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3397, 0.5192, 0.7564, 0.9167 | 0.3397: 2491 (81%); 0.5192: 1859 (60%); 0.7564: 1233 (40%); 0.9167: 685 (22%) | 0.3397: 634 (21%); 0.5192: 1248 (41%); 0.7564: 1850 (60%); 0.9167: 2503 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3718, 0.5962, 0.8526 | 0.1474: 2473 (80%); 0.3718: 1845 (60%); 0.5962: 1254 (41%); 0.8526: 725 (24%) | 0.1474: 636 (21%); 0.3718: 1235 (40%); 0.5962: 1854 (60%); 0.8526: 2606 (85%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0665, -0.0547, -0.0356, 0 | -0.0665: 2464 (80%); -0.0547: 1846 (60%); -0.0356: 1255 (41%); 0: 1043 (34%) | -0.0665: 626 (20%); -0.0547: 1235 (40%); -0.0356: 1854 (60%); 0: 2970 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4359, 0.7244, 0.9038, 1 | 0.4359: 2466 (80%); 0.7244: 1849 (60%); 0.9038: 1275 (41%); 1: 809 (26%) | 0.4359: 625 (20%); 0.7244: 1239 (40%); 0.9038: 1877 (61%); 1: 3073 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1218, 0.2756, 0.5128, 0.7949 | 0.1218: 2477 (81%); 0.2756: 1846 (60%); 0.5128: 1251 (41%); 0.7949: 629 (20%) | 0.1218: 624 (20%); 0.2756: 1234 (40%); 0.5128: 1863 (61%); 0.7949: 2470 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0078, 0.0443, 0.1206, 0.2489 | 0.0078: 2470 (80%); 0.0443: 1844 (60%); 0.1206: 1236 (40%); 0.2489: 816 (27%) | 0.0078: 617 (20%); 0.0443: 1229 (40%); 0.1206: 1865 (61%); 0.2489: 2515 (82%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.5974, 0.8482, 0.9487, 0.9744 | 0.5974: 2460 (80%); 0.8482: 1877 (61%); 0.9487: 1289 (42%); 0.9744: 875 (28%) | 0.5974: 617 (20%); 0.8482: 1232 (40%); 0.9487: 1878 (61%); 0.9744: 2547 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0947, 0.2179, 0.4295, 0.7188 | 0.0947: 2476 (81%); 0.2179: 1855 (60%); 0.4295: 1257 (41%); 0.7188: 639 (21%) | 0.0947: 618 (20%); 0.2179: 1241 (40%); 0.4295: 1875 (61%); 0.7188: 2462 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0141, 0.1093, 0.1876 | -0.0812: 2490 (81%); -0.0141: 1845 (60%); 0.1093: 1232 (40%); 0.1876: 620 (20%) | -0.0812: 835 (27%); -0.0141: 1250 (41%); 0.1093: 1853 (60%); 0.1876: 2515 (82%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.3109, -0.0425, 0.0345, 0.0916 | -0.3109: 2469 (80%); -0.0425: 1845 (60%); 0.0345: 1231 (40%); 0.0916: 628 (20%) | -0.3109: 618 (20%); -0.0425: 1235 (40%); 0.0345: 1856 (60%); 0.0916: 2470 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.5256, 0.7436, 0.8782 | 0.2628: 2626 (85%); 0.5256: 1902 (62%); 0.7436: 1239 (40%); 0.8782: 640 (21%) | 0.2628: 705 (23%); 0.5256: 1249 (41%); 0.7436: 1888 (61%); 0.8782: 2500 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1218, 0.3782, 0.5641, 0.8205 | 0.1218: 2484 (81%); 0.3782: 1861 (61%); 0.5641: 1395 (45%); 0.8205: 625 (20%) | 0.1218: 622 (20%); 0.3782: 1272 (41%); 0.5641: 1960 (64%); 0.8205: 2484 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0542, 0.1433, 0.3133, 0.69 | 0.0542: 2460 (80%); 0.1433: 1846 (60%); 0.3133: 1233 (40%); 0.69: 616 (20%) | 0.0542: 617 (20%); 0.1433: 1233 (40%); 0.3133: 1846 (60%); 0.69: 2459 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.5% | 27, 60, 85, 150 | 27: 2446 (80%); 60: 1830 (60%); 85: 1220 (40%); 150: 612 (20%) | 27: 608 (20%); 60: 1213 (39%); 85: 1833 (60%); 150: 2424 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.7% | 1.78, 2.3611, 2.962, 3.9449 | 1.78: 2450 (80%); 2.3611: 1840 (60%); 2.962: 1225 (40%); 3.9449: 613 (20%) | 1.78: 613 (20%); 2.3611: 1226 (40%); 2.962: 1838 (60%); 3.9449: 2450 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 8, 19, 28, 36 | 8: 2534 (82%); 19: 1882 (61%); 28: 1381 (45%); 36: 656 (21%) | 8: 636 (21%); 19: 1258 (41%); 28: 1991 (65%); 36: 2482 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3 | 1: 2589 (84%); 2: 2008 (65%); 3: 1269 (41%) | 1: 1065 (35%); 2: 1804 (59%); 3: 2466 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.012, -0.0029, 0.0086, 0.0215 | -0.012: 2462 (80%); -0.0029: 1851 (60%); 0.0086: 1231 (40%); 0.0215: 615 (20%) | -0.012: 615 (20%); -0.0029: 1234 (40%); 0.0086: 1844 (60%); 0.0215: 2461 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5861, 26.0298, 26.7852, 27.3557 | 24.5861: 2459 (80%); 26.0298: 1845 (60%); 26.7852: 1259 (41%); 27.3557: 755 (25%) | 24.5861: 627 (20%); 26.0298: 1233 (40%); 26.7852: 1853 (60%); 27.3557: 2523 (82%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -1.2386, -0.2612, 0.4042, 1.5114 | -1.2386: 2458 (80%); -0.2612: 1844 (60%); 0.4042: 1229 (40%); 1.5114: 615 (20%) | -1.2386: 615 (20%); -0.2612: 1229 (40%); 0.4042: 1844 (60%); 1.5114: 2458 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -1.5114, -0.4042, 0.2612, 1.2386 | -1.5114: 2458 (80%); -0.4042: 1844 (60%); 0.2612: 1229 (40%); 1.2386: 615 (20%) | -1.5114: 615 (20%); -0.4042: 1229 (40%); 0.2612: 1844 (60%); 1.2386: 2458 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0429, -0.0033, 0.0265, 0.0747 | -0.0429: 2464 (80%); -0.0033: 1846 (60%); 0.0265: 1230 (40%); 0.0747: 616 (20%) | -0.0429: 621 (20%); -0.0033: 1239 (40%); 0.0265: 1845 (60%); 0.0747: 2462 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9793, 8.4681, 8.8011, 9.2351 | 7.9793: 2463 (80%); 8.4681: 1843 (60%); 8.8011: 1227 (40%); 9.2351: 615 (20%) | 7.9793: 610 (20%); 8.4681: 1230 (40%); 8.8011: 1846 (60%); 9.2351: 2458 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 3046 (99%); 1: 1020 (33%) | 0: 2026 (66%); 1: 2685 (87%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | -1, 0 | -1: 2893 (94%); 0: 2408 (78%) | -1: 638 (21%); 0: 2574 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 3046 (99%); 1: 1123 (37%) | 0: 1923 (63%); 1: 2637 (86%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 8, 181, 285 | 3: 2579 (84%); 8: 1889 (61%); 181: 1230 (40%); 285: 621 (20%) | 3: 651 (21%); 8: 1238 (40%); 181: 1846 (60%); 285: 2459 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 2, 20, 96.2, 151 | 2: 2467 (80%); 20: 1847 (60%); 96.2: 1229 (40%); 151: 620 (20%) | 2: 772 (25%); 20: 1231 (40%); 96.2: 1844 (60%); 151: 2467 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.878, -0.2394, 0.0721, 0.6423 | -0.878: 2458 (80%); -0.2394: 1845 (60%); 0.0721: 1229 (40%); 0.6423: 615 (20%) | -0.878: 615 (20%); -0.2394: 1230 (40%); 0.0721: 1844 (60%); 0.6423: 2458 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.9491, -1.0023, -0.0789, 1.29 | -2.9491: 2458 (80%); -1.0023: 1844 (60%); -0.0789: 1229 (40%); 1.29: 615 (20%) | -2.9491: 615 (20%); -1.0023: 1229 (40%); -0.0789: 1844 (60%); 1.29: 2458 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.5805, -0.8618, -0.0642, 1.1867 | -2.5805: 2458 (80%); -0.8618: 1844 (60%); -0.0642: 1229 (40%); 1.1867: 615 (20%) | -2.5805: 615 (20%); -0.8618: 1229 (40%); -0.0642: 1844 (60%); 1.1867: 2458 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.7144, -0.189, 0.0767, 0.511 | -0.7144: 2458 (80%); -0.189: 1844 (60%); 0.0767: 1229 (40%); 0.511: 615 (20%) | -0.7144: 615 (20%); -0.189: 1229 (40%); 0.0767: 1844 (60%); 0.511: 2458 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -3.3174, -1.0917, -0.0169, 1.5665 | -3.3174: 2458 (80%); -1.0917: 1844 (60%); -0.0169: 1229 (40%); 1.5665: 615 (20%) | -3.3174: 615 (20%); -1.0917: 1229 (40%); -0.0169: 1844 (60%); 1.5665: 2458 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.9739, -1.0123, -0.053, 1.4326 | -2.9739: 2458 (80%); -1.0123: 1844 (60%); -0.053: 1229 (40%); 1.4326: 615 (20%) | -2.9739: 615 (20%); -1.0123: 1229 (40%); -0.053: 1844 (60%); 1.4326: 2458 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 34.238, 43.314, 52.35, 62.438 | 34.238: 2458 (80%); 43.314: 1844 (60%); 52.35: 1231 (40%); 62.438: 615 (20%) | 34.238: 615 (20%); 43.314: 1229 (40%); 52.35: 1845 (60%); 62.438: 2458 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0093, 0.0219, 0.0425, 0.081 | 0.0093: 2459 (80%); 0.0219: 1845 (60%); 0.0425: 1231 (40%); 0.081: 614 (20%) | 0.0093: 614 (20%); 0.0219: 1228 (40%); 0.0425: 1842 (60%); 0.081: 2459 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 10 | 0: 3073 (100%); 2: 1922 (63%); 4: 1342 (44%); 10: 661 (22%) | 0: 646 (21%); 2: 1485 (48%); 4: 1895 (62%); 10: 2486 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2143 | 0: 3073 (100%); 0.2143: 621 (20%) | 0: 1895 (62%); 0.2143: 2463 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.4375, 0.6667 | 0: 3073 (100%); 0.2: 1873 (61%); 0.4375: 1230 (40%); 0.6667: 688 (22%) | 0: 1097 (36%); 0.2: 1252 (41%); 0.4375: 1847 (60%); 0.6667: 2484 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 3073 (100%); 1: 2260 (74%); 3: 1347 (44%); 7: 707 (23%) | 0: 813 (26%); 1: 1388 (45%); 3: 1954 (64%); 7: 2466 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 10 | 0: 3073 (100%); 2: 1922 (63%); 4: 1342 (44%); 10: 661 (22%) | 0: 646 (21%); 2: 1485 (48%); 4: 1895 (62%); 10: 2486 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 3073 (100%); 1: 2139 (70%); 3: 1340 (44%); 7: 694 (23%) | 0: 934 (30%); 1: 1434 (47%); 3: 1981 (64%); 7: 2478 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.3502, 0.5714 | 0: 2739 (89%); 0.2: 1845 (60%); 0.3502: 1229 (40%); 0.5714: 626 (20%) | 0: 785 (26%); 0.2: 1257 (41%); 0.3502: 1844 (60%); 0.5714: 2461 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1881, 0.6 | 0: 2698 (88%); 0.1881: 1229 (40%); 0.6: 620 (20%) | 0: 1624 (53%); 0.1881: 1844 (60%); 0.6: 2463 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3, 0.6 | 0: 2694 (88%); 0.3: 1233 (40%); 0.6: 632 (21%) | 0: 1352 (44%); 0.3: 1849 (60%); 0.6: 2467 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3, 0.6 | 0: 2694 (88%); 0.3: 1233 (40%); 0.6: 632 (21%) | 0: 1352 (44%); 0.3: 1849 (60%); 0.6: 2467 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1667, 0, 0.1632 | -0.1667: 2470 (80%); 0: 2209 (72%); 0.1632: 615 (20%) | -0.1667: 618 (20%); 0: 2201 (72%); 0.1632: 2458 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.6461, 0, 0.4843, 1.7889 | -0.6461: 2529 (82%); 0: 1899 (62%); 0.4843: 1229 (40%); 1.7889: 707 (23%) | -0.6461: 618 (20%); 0: 1575 (51%); 0.4843: 1844 (60%); 1.7889: 2463 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 2508 (82%); 4: 1961 (64%); 7: 1256 (41%); 11: 655 (21%) | 2: 846 (28%); 4: 1388 (45%); 7: 1967 (64%); 11: 2523 (82%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0962, -0.0431, 0.0036, 0.0648 | -0.0962: 2458 (80%); -0.0431: 1845 (60%); 0.0036: 1229 (40%); 0.0648: 616 (20%) | -0.0962: 615 (20%); -0.0431: 1228 (40%); 0.0036: 1844 (60%); 0.0648: 2457 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1086, -0.0485, 0.0067, 0.0763 | -0.1086: 2458 (80%); -0.0485: 1843 (60%); 0.0067: 1229 (40%); 0.0763: 614 (20%) | -0.1086: 615 (20%); -0.0485: 1230 (40%); 0.0067: 1844 (60%); 0.0763: 2459 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0689, -0.0292, 0.0055, 0.053 | -0.0689: 2458 (80%); -0.0292: 1844 (60%); 0.0055: 1228 (40%); 0.053: 615 (20%) | -0.0689: 615 (20%); -0.0292: 1229 (40%); 0.0055: 1845 (60%); 0.053: 2458 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -31.8064, -16.4866, 0.7654, 29.1934 | -31.8064: 2458 (80%); -16.4866: 1844 (60%); 0.7654: 1229 (40%); 29.1934: 615 (20%) | -31.8064: 615 (20%); -16.4866: 1229 (40%); 0.7654: 1844 (60%); 29.1934: 2458 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0555, 0.0775, 0.1033, 0.1515 | 0.0555: 2459 (80%); 0.0775: 1846 (60%); 0.1033: 1230 (40%); 0.1515: 615 (20%) | 0.0555: 617 (20%); 0.0775: 1230 (40%); 0.1033: 1845 (60%); 0.1515: 2459 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1384, 0.3553, 0.7237, 0.8979 | 0.1384: 2458 (80%); 0.3553: 1844 (60%); 0.7237: 1230 (40%); 0.8979: 615 (20%) | 0.1384: 615 (20%); 0.3553: 1230 (40%); 0.7237: 1844 (60%); 0.8979: 2458 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -3.3461, -1.6491, -0.199, 1.5823 | -3.3461: 2458 (80%); -1.6491: 1844 (60%); -0.199: 1230 (40%); 1.5823: 615 (20%) | -3.3461: 615 (20%); -1.6491: 1229 (40%); -0.199: 1844 (60%); 1.5823: 2458 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -1.0575, -0.4554, 0.1201, 0.7946 | -1.0575: 2458 (80%); -0.4554: 1844 (60%); 0.1201: 1229 (40%); 0.7946: 616 (20%) | -1.0575: 615 (20%); -0.4554: 1229 (40%); 0.1201: 1844 (60%); 0.7946: 2459 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -2.9344, -1.4099, -0.1362, 1.538 | -2.9344: 2458 (80%); -1.4099: 1844 (60%); -0.1362: 1229 (40%); 1.538: 615 (20%) | -2.9344: 615 (20%); -1.4099: 1229 (40%); -0.1362: 1844 (60%); 1.538: 2458 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -10.5398, -4.8164, 0.4796, 6.7408 | -10.5398: 2458 (80%); -4.8164: 1844 (60%); 0.4796: 1229 (40%); 6.7408: 615 (20%) | -10.5398: 615 (20%); -4.8164: 1229 (40%); 0.4796: 1844 (60%); 6.7408: 2458 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 37.368, 43.718, 50.26, 57.93 | 37.368: 2458 (80%); 43.718: 1844 (60%); 50.26: 1230 (40%); 57.93: 616 (20%) | 37.368: 615 (20%); 43.718: 1229 (40%); 50.26: 1846 (60%); 57.93: 2459 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 11.82, 36.346, 66.946, 87.2 | 11.82: 2460 (80%); 36.346: 1844 (60%); 66.946: 1229 (40%); 87.2: 615 (20%) | 11.82: 616 (20%); 36.346: 1229 (40%); 66.946: 1844 (60%); 87.2: 2458 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 39.68, 44.45, 49.824, 55.55 | 39.68: 2461 (80%); 44.45: 1845 (60%); 49.824: 1229 (40%); 55.55: 616 (20%) | 39.68: 617 (20%); 44.45: 1230 (40%); 49.824: 1844 (60%); 55.55: 2460 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 34.42, 42.942, 50.85, 60.896 | 34.42: 2459 (80%); 42.942: 1844 (60%); 50.85: 1230 (40%); 60.896: 615 (20%) | 34.42: 616 (20%); 42.942: 1229 (40%); 50.85: 1845 (60%); 60.896: 2458 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0285, 0.0448, 0.0597, 0.0922 | 0.0285: 2461 (80%); 0.0448: 1844 (60%); 0.0597: 1231 (40%); 0.0922: 622 (20%) | 0.0285: 617 (20%); 0.0448: 1233 (40%); 0.0597: 1846 (60%); 0.0922: 2460 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.075, -0.0529, -0.0433, -0.0337 | -0.075: 2464 (80%); -0.0529: 1850 (60%); -0.0433: 1237 (40%); -0.0337: 616 (20%) | -0.075: 615 (20%); -0.0529: 1233 (40%); -0.0433: 1847 (60%); -0.0337: 2468 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 3073 (100%); 1: 901 (29%) | 0: 2172 (71%); 1: 2493 (81%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.7% | 27, 45, 63, 71 | 27: 2454 (80%); 45: 1877 (61%); 63: 1263 (41%); 71: 627 (20%) | 27: 638 (21%); 45: 1258 (41%); 63: 1853 (60%); 71: 2466 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.1% | 0.0168, 0.025, 0.0361, 0.0561 | 0.0168: 2407 (78%); 0.025: 1805 (59%); 0.0361: 1208 (39%); 0.0561: 602 (20%) | 0.0168: 609 (20%); 0.025: 1212 (39%); 0.0361: 1808 (59%); 0.0561: 2414 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.1563, 0.299, 0.477, 0.713 | 0.1563: 2459 (80%); 0.299: 1844 (60%); 0.477: 1229 (40%); 0.713: 615 (20%) | 0.1563: 616 (20%); 0.299: 1230 (40%); 0.477: 1844 (60%); 0.713: 2458 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 22.6, 54.08, 90.1, 148.06 | 22.6: 2459 (80%); 54.08: 1844 (60%); 90.1: 1230 (40%); 148.06: 615 (20%) | 22.6: 617 (20%); 54.08: 1229 (40%); 90.1: 1845 (60%); 148.06: 2458 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -5.508, -1.6562, 0.3205, 3.781 | -5.508: 2458 (80%); -1.6562: 1844 (60%); 0.3205: 1229 (40%); 3.781: 615 (20%) | -5.508: 615 (20%); -1.6562: 1229 (40%); 0.3205: 1844 (60%); 3.781: 2458 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 15.274, 26.864, 52.772, 78.644 | 15.274: 2458 (80%); 26.864: 1844 (60%); 52.772: 1229 (40%); 78.644: 615 (20%) | 15.274: 615 (20%); 26.864: 1229 (40%); 52.772: 1844 (60%); 78.644: 2458 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 16.4, 29.334, 52.726, 77.032 | 16.4: 2458 (80%); 29.334: 1844 (60%); 52.726: 1229 (40%); 77.032: 615 (20%) | 16.4: 615 (20%); 29.334: 1229 (40%); 52.726: 1844 (60%); 77.032: 2458 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 11.11, 28.898, 59.134, 85.356 | 11.11: 2458 (80%); 28.898: 1844 (60%); 59.134: 1229 (40%); 85.356: 615 (20%) | 11.11: 615 (20%); 28.898: 1229 (40%); 59.134: 1844 (60%); 85.356: 2458 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 4.562, 33.55, 59.704, 92.502 | 4.562: 2458 (80%); 33.55: 1844 (60%); 59.704: 1229 (40%); 92.502: 615 (20%) | 4.562: 615 (20%); 33.55: 1229 (40%); 59.704: 1844 (60%); 92.502: 2458 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 11, 16 | 4: 2620 (85%); 7: 2073 (67%); 11: 1338 (44%); 16: 718 (23%) | 4: 713 (23%); 7: 1304 (42%); 11: 1862 (61%); 16: 2463 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 6, 11, 15, 18 | 6: 2462 (80%); 11: 1849 (60%); 15: 1286 (42%); 18: 685 (22%) | 6: 723 (24%); 11: 1349 (44%); 15: 2077 (68%); 18: 2626 (85%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 39.922, 46.43, 51.722, 57.67 | 39.922: 2458 (80%); 46.43: 1845 (60%); 51.722: 1229 (40%); 57.67: 617 (20%) | 39.922: 615 (20%); 46.43: 1230 (40%); 51.722: 1844 (60%); 57.67: 2459 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2262, 0.5429, 0.754, 0.9365 | 0.2262: 2460 (80%); 0.5429: 1844 (60%); 0.754: 1238 (40%); 0.9365: 616 (20%) | 0.2262: 616 (20%); 0.5429: 1229 (40%); 0.754: 1865 (61%); 0.9365: 2475 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.78, 18.21, 21.74, 28.46 | 15.78: 2459 (80%); 18.21: 1845 (60%); 21.74: 1230 (40%); 28.46: 617 (20%) | 15.78: 634 (21%); 18.21: 1238 (40%); 21.74: 1845 (60%); 28.46: 2459 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 15.78, 18.21, 21.74, 28.46 | 15.78: 2459 (80%); 18.21: 1845 (60%); 21.74: 1230 (40%); 28.46: 617 (20%) | 15.78: 634 (21%); 18.21: 1238 (40%); 21.74: 1845 (60%); 28.46: 2459 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8626, 0.899, 0.9398, 0.9842 | 0.8626: 2465 (80%); 0.899: 1844 (60%); 0.9398: 1230 (40%); 0.9842: 616 (20%) | 0.8626: 621 (20%); 0.899: 1233 (40%); 0.9398: 1845 (60%); 0.9842: 2466 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 1.1, 1.22, 1.43, 1.8 | 1.1: 2468 (80%); 1.22: 1865 (61%); 1.43: 1236 (40%); 1.8: 621 (20%) | 1.1: 672 (22%); 1.22: 1247 (41%); 1.43: 1864 (61%); 1.8: 2466 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0252, 0.0568, 0.0936, 0.1497 | 0.0252: 2459 (80%); 0.0568: 1847 (60%); 0.0936: 1230 (40%); 0.1497: 615 (20%) | 0.0252: 616 (20%); 0.0568: 1230 (40%); 0.0936: 1844 (60%); 0.1497: 2459 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 41.1839, 72.0657, 110.3202, 186.6977 | 41.1839: 2458 (80%); 72.0657: 1844 (60%); 110.3202: 1229 (40%); 186.6977: 615 (20%) | 41.1839: 615 (20%); 72.0657: 1229 (40%); 110.3202: 1844 (60%); 186.6977: 2458 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 38.9251, 68.2428, 103.1641, 178.304 | 38.9251: 2458 (80%); 68.2428: 1844 (60%); 103.1641: 1229 (40%); 178.304: 615 (20%) | 38.9251: 615 (20%); 68.2428: 1229 (40%); 103.1641: 1844 (60%); 178.304: 2458 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 36.6619, 63.4709, 97.3912, 169.5274 | 36.6619: 2458 (80%); 63.4709: 1844 (60%); 97.3912: 1229 (40%); 169.5274: 615 (20%) | 36.6619: 615 (20%); 63.4709: 1229 (40%); 97.3912: 1844 (60%); 169.5274: 2458 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 43.4219, 75.6703, 116.0496, 196.2101 | 43.4219: 2458 (80%); 75.6703: 1844 (60%); 116.0496: 1229 (40%); 196.2101: 615 (20%) | 43.4219: 615 (20%); 75.6703: 1229 (40%); 116.0496: 1844 (60%); 196.2101: 2458 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 45.4055, 79.1095, 121.2178, 204.3523 | 45.4055: 2458 (80%); 79.1095: 1844 (60%); 121.2178: 1229 (40%); 204.3523: 615 (20%) | 45.4055: 615 (20%); 79.1095: 1229 (40%); 121.2178: 1844 (60%); 204.3523: 2458 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 3073 (100%) | 0: 2768 (90%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 3073 (100%) | 0: 2806 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1064, -0.0498, 0.0035, 0.0746 | -0.1064: 2458 (80%); -0.0498: 1846 (60%); 0.0035: 1231 (40%); 0.0746: 615 (20%) | -0.1064: 615 (20%); -0.0498: 1231 (40%); 0.0035: 1844 (60%); 0.0746: 2458 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -85.076, -65.408, -45.428, -22.352 | -85.076: 2458 (80%); -65.408: 1844 (60%); -45.428: 1229 (40%); -22.352: 615 (20%) | -85.076: 615 (20%); -65.408: 1229 (40%); -45.428: 1844 (60%); -22.352: 2458 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.7388, 1.0462, 1.3193, 1.6244 | 0.7388: 2458 (80%); 1.0462: 1844 (60%); 1.3193: 1229 (40%); 1.6244: 615 (20%) | 0.7388: 615 (20%); 1.0462: 1229 (40%); 1.3193: 1844 (60%); 1.6244: 2458 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 5, 7, 9, 10 | 5: 2476 (81%); 7: 2042 (66%); 9: 1395 (45%); 10: 866 (28%) | 5: 797 (26%); 7: 1314 (43%); 9: 2207 (72%); 10: 3073 (100%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 100.0% | 8, 9, 10 | 8: 2487 (81%); 9: 1885 (61%); 10: 1047 (34%) | 8: 1188 (39%); 9: 2026 (66%); 10: 3073 (100%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0338, 0.0456, 0.0601, 0.0867 | 0.0338: 2461 (80%); 0.0456: 1846 (60%); 0.0601: 1231 (40%); 0.0867: 615 (20%) | 0.0338: 619 (20%); 0.0456: 1234 (40%); 0.0601: 1848 (60%); 0.0867: 2462 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 5, 8, 9, 10 | 5: 2667 (87%); 8: 1891 (62%); 9: 1461 (48%); 10: 890 (29%) | 5: 621 (20%); 8: 1612 (52%); 9: 2183 (71%); 10: 3073 (100%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.3109, -0.1486, 0.0212, 0.3036 | -0.3109: 2458 (80%); -0.1486: 1844 (60%); 0.0212: 1230 (40%); 0.3036: 615 (20%) | -0.3109: 615 (20%); -0.1486: 1229 (40%); 0.0212: 1844 (60%); 0.3036: 2458 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 1, 3, 5, 9 | 1: 3072 (100%); 3: 1910 (62%); 5: 1365 (44%); 9: 688 (22%) | 1: 743 (24%); 3: 1463 (48%); 5: 1899 (62%); 9: 2592 (84%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 7.0% |
| 8k_item_5_02_filed_within_7d | 4.4% |
| above_avwap_20high | 28.1% |
| above_avwap_20low | 71.1% |
| above_avwap_252low | 70.0% |
| above_avwap_50low | 71.4% |
| above_cam_r3 | 52.7% |
| above_cam_r4 | 52.7% |
| above_cpr | 52.7% |
| above_pivot | 52.7% |
| above_prev_high | 44.7% |
| above_prev_high_clearance_atr_05 | 27.3% |
| above_prev_low | 59.7% |
| above_r1 | 50.9% |
| above_r2 | 29.4% |
| above_vwap | 40.8% |
| above_wood_p | 53.2% |
| ad_rising | 49.5% |
| adx_cross_up | 2.6% |
| adx_cross_up_20 | 2.6% |
| adx_di_bear | 59.6% |
| adx_di_bull | 40.4% |
| adx_strong | 7.0% |
| adx_trending | 40.9% |
| ao_cross_dn | 2.4% |
| ao_cross_up | 1.9% |
| ao_positive | 38.6% |
| ao_twin_peaks_bull | 6.8% |
| at_key_fib | 11.2% |
| at_key_fib_wide | 29.7% |
| avwap_20high_loss_recent_3d | 23.5% |
| avwap_20high_reclaim_recent_3d | 19.3% |
| avwap_20low_loss_recent_3d | 17.8% |
| avwap_20low_reclaim_recent_3d | 30.5% |
| avwap_252low_loss_recent_3d | 9.1% |
| avwap_252low_reclaim_recent_3d | 18.4% |
| avwap_50low_loss_recent_3d | 14.5% |
| avwap_50low_reclaim_recent_3d | 25.0% |
| bb_10_20_above_mid | 44.4% |
| bb_10_20_expanding | 54.7% |
| bb_10_20_pctb_gt_75 | 24.0% |
| bb_10_20_pctb_gt_8 | 21.1% |
| bb_10_20_pctb_gt_85 | 18.1% |
| bb_10_20_pctb_gt_9 | 15.7% |
| bb_10_20_pctb_gt_95 | 13.1% |
| bb_10_20_pctb_lt_05 | 13.4% |
| bb_10_20_pctb_lt_1 | 17.0% |
| bb_10_20_pctb_lt_15 | 20.0% |
| bb_10_20_pctb_lt_2 | 23.8% |
| bb_10_20_pctb_lt_25 | 28.8% |
| bb_10_20_reclaim_from_lower_recent_3d | 14.2% |
| bb_10_20_reclaim_from_upper_recent_3d | 7.4% |
| bb_10_20_squeeze | 15.2% |
| bb_10_20_touch_lower | 12.9% |
| bb_10_20_touch_upper | 12.6% |
| bb_20_15_above_mid | 42.4% |
| bb_20_15_expanding | 59.2% |
| bb_20_15_pctb_gt_75 | 27.2% |
| bb_20_15_pctb_gt_8 | 24.5% |
| bb_20_15_pctb_gt_85 | 21.5% |
| bb_20_15_pctb_gt_9 | 19.0% |
| bb_20_15_pctb_gt_95 | 17.2% |
| bb_20_15_pctb_lt_05 | 23.7% |
| bb_20_15_pctb_lt_1 | 27.3% |
| bb_20_15_pctb_lt_15 | 32.3% |
| bb_20_15_pctb_lt_2 | 36.6% |
| bb_20_15_pctb_lt_25 | 41.2% |
| bb_20_15_reclaim_from_lower_recent_3d | 23.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 14.8% |
| bb_20_15_squeeze | 14.2% |
| bb_20_15_touch_lower | 22.5% |
| bb_20_15_touch_upper | 17.1% |
| bb_20_20_above_mid | 42.4% |
| bb_20_20_expanding | 59.2% |
| bb_20_20_pctb_gt_75 | 22.3% |
| bb_20_20_pctb_gt_8 | 19.0% |
| bb_20_20_pctb_gt_85 | 16.4% |
| bb_20_20_pctb_gt_9 | 13.6% |
| bb_20_20_pctb_gt_95 | 10.8% |
| bb_20_20_pctb_lt_05 | 13.9% |
| bb_20_20_pctb_lt_1 | 17.5% |
| bb_20_20_pctb_lt_15 | 22.4% |
| bb_20_20_pctb_lt_2 | 27.3% |
| bb_20_20_pctb_lt_25 | 33.4% |
| bb_20_20_reclaim_from_lower_recent_3d | 19.4% |
| bb_20_20_reclaim_from_upper_recent_3d | 10.2% |
| bb_20_20_squeeze | 5.1% |
| bb_20_20_touch_lower | 12.5% |
| bb_20_20_touch_upper | 10.1% |
| bearish_engulfing | 6.3% |
| bearish_pin_bar | 1.8% |
| below_avwap_20high | 71.9% |
| below_avwap_20low | 28.8% |
| below_avwap_252low | 30.0% |
| below_avwap_50low | 28.6% |
| below_cam_s3 | 47.3% |
| below_cam_s4 | 47.3% |
| below_cpr | 47.3% |
| below_ema_20 | 58.2% |
| below_ema_200 | 65.6% |
| below_ema_200_break_recent_5d | 10.3% |
| below_ema_20_break_recent_5d | 24.1% |
| below_ema_21 | 58.3% |
| below_ema_21_break_recent_5d | 23.6% |
| below_ema_50 | 62.2% |
| below_ema_50_break_recent_5d | 17.5% |
| below_ema_9 | 55.3% |
| below_ema_9_break_recent_5d | 32.7% |
| below_prev_high | 55.2% |
| below_prev_low | 40.2% |
| below_prev_low_clearance_atr_05 | 25.7% |
| below_s1 | 44.9% |
| below_s2 | 27.2% |
| below_sma_20 | 57.6% |
| below_sma_200 | 64.2% |
| below_sma_21 | 57.6% |
| below_sma_50 | 61.2% |
| below_sma_9 | 54.4% |
| below_vwap | 59.2% |
| break_52w_high | 0.5% |
| break_52w_high_clearance_atr_05 | 0.2% |
| break_52w_high_confirmed_today | 0.5% |
| break_52w_low | 1.7% |
| bullish_engulfing | 10.7% |
| bullish_pin_bar | 1.7% |
| ceo_buy | 1.2% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 55.1% |
| chandelier_long_flip_dn | 9.5% |
| chandelier_short_bearish | 67.8% |
| chandelier_short_flip_up | 10.0% |
| classification_change_from_tech | 80.0% |
| classification_change_to_defensive | 20.0% |
| close_above_open | 52.7% |
| close_below_open | 47.3% |
| close_in_bottom_40pct_of_range | 42.5% |
| close_in_top_40pct_of_range | 48.2% |
| cluster_buy | 0.6% |
| cmf_cross_dn | 6.5% |
| cmf_cross_up | 6.9% |
| cmf_negative | 50.3% |
| cmf_positive | 49.5% |
| concentrated_sell | 4.8% |
| cpr_narrow | 87.5% |
| cpr_narrow_tight | 25.2% |
| cup_handle_detected | 6.5% |
| cup_handle_neckline_break_retest_long | 2.2% |
| dc10_breakout_dn | 17.1% |
| dc10_breakout_dn_1pct | 19.4% |
| dc10_breakout_up | 14.3% |
| dc10_breakout_up_1pct | 16.4% |
| dc10_new_high | 20.0% |
| dc10_strong_breakout_dn | 10.6% |
| dc10_strong_breakout_up | 8.9% |
| dc20_breakout_dn | 12.5% |
| dc20_breakout_up | 8.8% |
| dc20_new_high | 13.5% |
| dc20_resistance_break_retest_strong | 11.7% |
| dc20_support_break_retest_strong | 23.5% |
| defensive_leadership | 58.8% |
| director_only_buy | 4.0% |
| doji | 0.9% |
| double_bottom_detected | 11.2% |
| double_top_detected | 12.1% |
| dpi_elevated | 49.1% |
| ema_20_50_bearish | 63.9% |
| ema_20_50_bullish | 36.1% |
| ema_20_50_death_cross | 1.6% |
| ema_20_50_golden_cross | 0.7% |
| ema_50_200_bearish | 61.3% |
| ema_50_200_bullish | 38.7% |
| ema_50_200_death_cross | 0.1% |
| ema_50_200_golden_cross | 0.2% |
| ema_9_21_bearish | 60.7% |
| ema_9_21_bullish | 39.3% |
| ema_9_21_death_cross | 2.6% |
| ema_9_21_golden_cross | 3.7% |
| evening_star | 7.7% |
| flag_bear_break_retest_short | 0.8% |
| flag_bear_broke | 1.0% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 0.5% |
| flag_bull_broke | 0.6% |
| flag_bull_detected | 0.4% |
| force_index_cross_dn | 15.1% |
| force_index_cross_up | 16.7% |
| force_index_positive | 44.0% |
| gap_dn_1_5pct | 20.2% |
| gap_dn_2pct | 14.6% |
| gap_up_1_5pct | 16.8% |
| gap_up_2pct | 11.9% |
| hammer | 1.7% |
| head_shoulders_bottom_detected | 4.7% |
| head_shoulders_top_detected | 5.2% |
| house_cluster_buy | 5.1% |
| house_cluster_sell | 5.4% |
| htf_aligned_bear | 46.3% |
| htf_aligned_bull | 21.5% |
| htf_disagreement | 3.1% |
| hull_bearish | 56.7% |
| hull_bullish | 43.3% |
| hull_flip_dn | 7.4% |
| hull_flip_up | 6.4% |
| ichi_above_cloud | 29.0% |
| ichi_above_cloud_break_recent_5d | 8.3% |
| ichi_below_cloud | 56.1% |
| ichi_below_cloud_break_recent_5d | 13.4% |
| ichi_cloud_thick | 89.6% |
| ichi_tk_bearish | 55.7% |
| ichi_tk_bullish | 36.7% |
| ichi_tk_cross_dn | 3.0% |
| ichi_tk_cross_up | 3.4% |
| ichi_weekly_above_cloud | 29.2% |
| ichi_weekly_below_cloud | 46.4% |
| ichi_weekly_in_cloud | 24.4% |
| in_reversal_window | 3.0% |
| inside_bar | 3.2% |
| inside_kc | 77.4% |
| insider_cluster_active | 20.3% |
| institutional_buy | 90.7% |
| institutional_negative | 4.5% |
| institutional_persistence_growing | 54.7% |
| institutional_persistence_strong | 67.1% |
| institutional_strong_buy | 84.6% |
| inverted_cup_handle_detected | 3.8% |
| is_friday | 19.8% |
| is_halloween_period | 55.4% |
| is_halloween_period_first_day | 0.1% |
| is_january | 9.5% |
| is_january_extended | 10.3% |
| is_monday | 15.8% |
| is_pre_holiday | 2.1% |
| is_summer_period | 44.6% |
| is_totm_window | 30.7% |
| is_totm_window_first_day | 8.2% |
| is_week_open | 18.7% |
| kc_touch_lower | 16.1% |
| kc_touch_upper | 9.3% |
| large_dollar_buy | 1.4% |
| macd_12_26_9_bearish | 54.9% |
| macd_12_26_9_bullish | 45.1% |
| macd_12_26_9_crossover_dn | 5.5% |
| macd_12_26_9_crossover_up | 4.6% |
| macd_8_21_5_bearish | 54.0% |
| macd_8_21_5_bullish | 46.0% |
| macd_8_21_5_crossover_dn | 8.4% |
| macd_8_21_5_crossover_up | 7.7% |
| marubozu_bear | 1.8% |
| marubozu_bull | 2.1% |
| mfi_broad_overbought | 9.3% |
| mfi_broad_oversold | 12.9% |
| mfi_overbought | 2.1% |
| mfi_oversold | 2.8% |
| monthly_above_sma_12 | 35.8% |
| monthly_above_sma_6 | 34.9% |
| monthly_bias_bear | 56.5% |
| monthly_bias_bull | 27.2% |
| monthly_momentum_pos | 38.0% |
| morning_star | 6.8% |
| near_52w_high | 0.8% |
| near_52w_high_95pct | 5.0% |
| near_52w_low | 2.7% |
| near_52w_low_105pct | 8.1% |
| near_avwap_20high_atr_05x | 25.3% |
| near_avwap_20high_atr_10x | 54.8% |
| near_avwap_20high_atr_15x | 74.3% |
| near_avwap_20high_atr_20x | 86.8% |
| near_avwap_20low_atr_05x | 28.3% |
| near_avwap_20low_atr_10x | 55.6% |
| near_avwap_20low_atr_15x | 72.7% |
| near_avwap_20low_atr_20x | 83.2% |
| near_avwap_252low_atr_05x | 14.3% |
| near_avwap_252low_atr_10x | 31.2% |
| near_avwap_252low_atr_15x | 43.6% |
| near_avwap_252low_atr_20x | 54.2% |
| near_avwap_50low_atr_05x | 20.3% |
| near_avwap_50low_atr_10x | 42.0% |
| near_avwap_50low_atr_15x | 59.4% |
| near_avwap_50low_atr_20x | 72.4% |
| near_cam_r3 | 0.1% |
| near_cam_s4 | 4.7% |
| near_fib_236 | 3.7% |
| near_fib_382 | 2.9% |
| near_fib_500 | 4.0% |
| near_fib_618 | 4.2% |
| near_fib_786 | 4.7% |
| near_pivot | 0.1% |
| near_prev_close | 0.0% |
| near_prev_high | 4.5% |
| near_prev_low | 4.1% |
| near_r1 | 4.5% |
| near_r1_wide | 19.8% |
| near_r2 | 6.4% |
| near_r2_wide | 26.9% |
| near_s1 | 3.7% |
| near_s1_wide | 19.4% |
| near_s2 | 6.1% |
| near_s2_wide | 24.7% |
| near_s3 | 4.2% |
| near_wood_r1 | 3.8% |
| near_wood_s1 | 3.9% |
| news_uses_polygon_score | 31.9% |
| obv_bearish | 55.1% |
| obv_bullish | 44.9% |
| obv_diverge_bull | 8.8% |
| obv_falling | 52.5% |
| obv_rising | 47.5% |
| outside_bar | 16.8% |
| pead_negative_surprise | 21.7% |
| pead_positive_surprise | 20.3% |
| pin_bar | 3.5% |
| po3_accumulation_active | 14.5% |
| po3_bearish | 7.8% |
| po3_bullish | 11.0% |
| po3_manipulation_sweep_down | 7.7% |
| po3_manipulation_sweep_up | 5.2% |
| po3_mmbm_setup | 0.4% |
| po3_mmsm_setup | 0.6% |
| po3_sweep_above_prior_high | 59.4% |
| po3_sweep_below_prior_low | 56.9% |
| ppo_bullish | 43.5% |
| ppo_crossover_dn | 5.9% |
| ppo_crossover_up | 4.7% |
| pre_fomc_d0 | 3.4% |
| pre_fomc_d1 | 2.5% |
| pre_fomc_window | 6.0% |
| price_above_dema | 48.3% |
| price_above_ema_20 | 41.8% |
| price_above_ema_200 | 34.4% |
| price_above_ema_200_break_recent_5d | 6.7% |
| price_above_ema_20_break_recent_5d | 22.4% |
| price_above_ema_21 | 41.7% |
| price_above_ema_21_break_recent_5d | 21.9% |
| price_above_ema_50 | 37.8% |
| price_above_ema_50_break_recent_5d | 16.1% |
| price_above_ema_9 | 44.7% |
| price_above_ema_9_break_recent_5d | 31.2% |
| price_above_hull | 51.0% |
| price_above_sma_200 | 35.8% |
| price_above_sma_21 | 42.4% |
| price_above_sma_50 | 38.8% |
| price_above_tema | 50.8% |
| price_below_dema | 51.7% |
| price_below_hull | 49.0% |
| price_below_tema | 49.2% |
| psar_bullish | 42.5% |
| psar_flip_dn | 8.2% |
| psar_flip_up | 7.8% |
| r1_break_retest_long | 44.1% |
| recent_blowoff_at_r3 | 0.1% |
| recent_capitulation_at_s3 | 0.3% |
| resistance_break_retest | 16.6% |
| risk_off_regime_bond_signal | 20.5% |
| risk_off_regime_bond_signal_strong | 8.8% |
| risk_off_regime_gold_signal | 44.0% |
| risk_on_regime_bond_signal | 38.6% |
| risk_on_regime_bond_signal_strong | 16.4% |
| roc_positive | 41.7% |
| roc_turning_dn | 8.6% |
| roc_turning_up | 8.4% |
| rsi_14_bullish | 40.9% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 1.4% |
| rsi_14_cross_dn_overbought_recent_3d | 7.2% |
| rsi_14_cross_up_extreme_os_recent_3d | 2.2% |
| rsi_14_cross_up_oversold_recent_3d | 13.2% |
| rsi_14_extreme_ob | 0.3% |
| rsi_14_extreme_os | 0.7% |
| rsi_14_overbought | 3.3% |
| rsi_14_oversold | 6.0% |
| rsi_14_rising | 52.7% |
| rsi_21_bullish | 39.4% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_21_cross_dn_overbought_recent_3d | 3.1% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.2% |
| rsi_21_cross_up_oversold_recent_3d | 7.2% |
| rsi_21_extreme_ob | 0.1% |
| rsi_21_extreme_os | 0.1% |
| rsi_21_overbought | 1.1% |
| rsi_21_oversold | 2.2% |
| rsi_21_rising | 52.7% |
| rsi_2_bullish | 51.2% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 28.3% |
| rsi_2_cross_dn_overbought_recent_3d | 34.1% |
| rsi_2_cross_up_extreme_os_recent_3d | 37.5% |
| rsi_2_cross_up_oversold_recent_3d | 41.4% |
| rsi_2_extreme_ob | 27.6% |
| rsi_2_extreme_os | 28.6% |
| rsi_2_overbought | 37.0% |
| rsi_2_oversold | 35.9% |
| rsi_2_rising | 52.7% |
| rsi_9_bullish | 42.2% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 4.4% |
| rsi_9_cross_dn_overbought_recent_3d | 13.6% |
| rsi_9_cross_up_extreme_os_recent_3d | 8.7% |
| rsi_9_cross_up_oversold_recent_3d | 22.4% |
| rsi_9_extreme_ob | 1.5% |
| rsi_9_extreme_os | 2.6% |
| rsi_9_overbought | 8.7% |
| rsi_9_oversold | 13.0% |
| rsi_9_rising | 52.7% |
| s1_break_retest_short | 56.0% |
| sc_13d_filed_within_30d | 2.0% |
| sc_13g_filed_within_30d | 2.4% |
| sector_outperforming_spy | 38.0% |
| sector_underperforming_spy | 62.0% |
| shooting_star | 1.9% |
| sma_20_50_bullish | 40.2% |
| sma_20_50_golden_cross | 1.3% |
| sma_50_200_bullish | 40.0% |
| sma_50_200_golden_cross | 0.2% |
| sma_9_21_bullish | 41.7% |
| sma_9_21_golden_cross | 2.7% |
| smc_bos_bearish | 15.9% |
| smc_bos_bullish | 11.1% |
| smc_bos_retest_long | 3.1% |
| smc_bos_retest_short | 3.2% |
| smc_breaker_block_bearish | 22.6% |
| smc_breaker_block_bullish | 18.7% |
| smc_choch_bearish | 7.6% |
| smc_choch_bullish | 3.1% |
| smc_equal_highs_swept | 2.7% |
| smc_equal_lows_swept | 6.0% |
| smc_fvg_bearish_active | 45.1% |
| smc_fvg_bullish_active | 35.4% |
| smc_fvg_retest_long_zone | 11.4% |
| smc_fvg_retest_short_zone | 15.3% |
| smc_in_discount_zone | 71.2% |
| smc_in_premium_zone | 46.9% |
| smc_inverse_fvg_bearish | 86.0% |
| smc_inverse_fvg_bullish | 69.8% |
| smc_liquidity_swept_dn | 2.1% |
| smc_liquidity_swept_up | 1.4% |
| smc_mitigation_block_long | 1.7% |
| smc_mitigation_block_short | 1.1% |
| smc_ob_bearish_active | 45.8% |
| smc_ob_bullish_active | 24.7% |
| smc_ote_long_zone | 7.7% |
| smc_ote_short_zone | 4.4% |
| squeeze_fire_dn | 6.3% |
| squeeze_fire_up | 7.6% |
| squeeze_in | 23.1% |
| squeeze_positive | 43.4% |
| stoch_bearish_cross | 14.2% |
| stoch_broad_overbought | 22.0% |
| stoch_broad_oversold | 34.4% |
| stoch_bullish_cross | 20.6% |
| stoch_overbought | 16.8% |
| stoch_oversold | 25.9% |
| stochrsi_cross_dn | 22.7% |
| stochrsi_cross_up | 31.3% |
| stochrsi_overbought | 26.4% |
| stochrsi_oversold | 29.0% |
| supertrend_bearish | 6.2% |
| supertrend_bullish | 93.8% |
| supertrend_flip_dn | 3.5% |
| supertrend_flip_recent_long_5d | 5.0% |
| supertrend_flip_recent_short_5d | 9.0% |
| supertrend_flip_up | 1.8% |
| support_break_retest | 30.6% |
| tema_above_dema | 46.1% |
| tema_cross_dn | 3.3% |
| tema_cross_up | 2.9% |
| three_black_crows | 6.3% |
| three_white_soldiers | 5.8% |
| triangle_apex_break_retest_long | 9.4% |
| triangle_ascending_detected | 5.6% |
| triangle_descending_detected | 7.0% |
| uo_overbought | 2.2% |
| uo_oversold | 2.7% |
| usd_strengthening | 22.0% |
| usd_weakening | 8.8% |
| vix_band_high | 49.6% |
| vix_band_low | 26.1% |
| vix_band_mid | 24.3% |
| vix_term_backwardation | 15.9% |
| vix_term_contango | 84.1% |
| vol_spike_12x | 62.8% |
| vol_spike_15x | 34.0% |
| vol_spike_17x | 24.1% |
| vol_spike_2x | 14.5% |
| vol_spike_2x_on_down_day_recent_3d | 6.7% |
| vol_spike_2x_on_up_day_recent_3d | 6.4% |
| vol_spike_3x | 5.0% |
| vp_above_value_area | 17.8% |
| vp_below_value_area | 26.9% |
| vp_close_above_poc | 44.6% |
| vp_close_below_poc | 55.4% |
| vp_in_value_area | 55.3% |
| week_open_gap_down_15pct | 3.9% |
| week_open_gap_up_15pct | 3.4% |
| weekly_above_ema_10 | 38.3% |
| weekly_above_ema_20 | 34.8% |
| weekly_bias_bear | 57.4% |
| weekly_bias_bull | 30.6% |
| weekly_momentum_pos | 41.3% |
| williams_r_overbought | 18.2% |
| williams_r_oversold | 24.9% |
| williams_r_rising | 52.7% |
| within_pead_window | 40.1% |
| within_post_deletion_window | 3.0% |
| within_post_inclusion_window | 1.4% |
| within_pre_rebalance_window | 1.7% |
| xs_avoid_high_ivol | 38.7% |
| xs_avoid_high_max | 52.5% |
| xs_high_beta_decile | 45.4% |
| xs_low_beta_bottom_quintile | 45.4% |
| xs_low_beta_decile | 7.6% |
| xs_low_beta_decile_entry_recent_5d | 0.3% |
| xs_low_beta_top_quintile | 7.6% |
| xs_momentum_bottom_decile | 24.2% |
| xs_momentum_bottom_quintile | 37.8% |
| xs_momentum_top_decile | 15.6% |
| xs_momentum_top_quintile | 22.4% |
| xs_quality_bottom_quintile | 24.2% |
| xs_quality_top_quintile | 22.6% |
| xs_quality_top_tercile | 42.5% |
| year_high_break_retest_long | 2.4% |
| year_low_break_retest_short | 6.9% |
| yoy_surprise_high | 48.5% |
| yoy_surprise_negative | 43.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.0% |
| committed_growth_holders | 90.0% |
| corp_donations_1y | 8.0% |
| corp_donations_count_1y | 8.0% |
| corp_donations_unique_pacs | 8.0% |
| cot_rut_commercials_pctile_3y | 59.5% |
| cot_rut_mmoney_pctile_3y | 59.5% |
| cup_handle_depth_pct | 16.6% |
| days_since_classification_change | 0.2% |
| days_since_deletion | 13.2% |
| days_since_inclusion | 20.4% |
| days_to_next_holiday | 68.2% |
| days_to_rebalance | 17.0% |
| dpi_30d_avg | 95.7% |
| dpi_recent | 95.7% |
| earnings_announcement_return | 89.7% |
| earnings_eps_yoy_growth | 94.1% |
| flag_bear_pole_move_pct | 0.2% |
| flag_bull_pole_move_pct | 0.4% |
| gov_contracts_4q_sum | 38.9% |
| gov_contracts_last_qtr_amount | 38.9% |
| gov_contracts_qoq_growth | 38.9% |
| head_shoulders_magnitude_pct | 9.5% |
| insider_director_buyers_30d | 6.6% |
| insider_officer_buyers_30d | 6.6% |
| insider_total_shares_bought_30d | 6.6% |
| insider_unique_buyers_30d | 6.6% |
| inverted_cup_handle_height_pct | 11.0% |
| lobbying_amount_1y | 71.6% |
| lobbying_amount_q | 71.6% |
| lobbying_amount_yoy | 71.6% |
| monthly_momentum_6m | 96.2% |
| otc_short_ratio_recent | 95.7% |
| otc_volume_recent | 95.7% |
| pair_half_life | 90.1% |
| pair_max_abs_zscore | 90.1% |
| pair_zscore_signed | 90.1% |
| pct_from_avwap_20high | 86.2% |
| pct_from_avwap_20low | 78.2% |
| pct_from_avwap_252low | 91.1% |
| pct_from_avwap_50low | 87.3% |
| persistent_holders_4q | 90.0% |
| persistent_holders_8q | 90.0% |
| sc_13g_latest_percent_owned | 1.4% |
| search_volume_index_recent | 77.0% |
| search_volume_observations | 77.0% |
| search_volume_zscore_30d | 77.0% |
| sector_etf_return_20d | 2.3% |
| spy_return_20d | 2.3% |
| total_active_holders | 90.0% |
| triangle_breakdown_pct | 7.0% |
| triangle_breakout_pct | 5.6% |
| xs_quality_decile | 67.6% |
| xs_quality_gross_profitability | 67.6% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.997), `avwap_252low` (0.992), `avwap_50low` (0.997), `bb_10_20_lower` (0.996), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.998), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.996), `cam_r2` (0.996), `cam_r3` (0.996), `cam_r4` (0.996), `cam_s1` (0.995), `cam_s2` (0.995), `cam_s3` (0.995), `cam_s4` (0.995), `chandelier_long_value` (0.999), `chandelier_short_value` (0.998), `cpr_bottom` (0.996), `cpr_top` (0.996), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.997), `dc10_lower` (0.996), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.997), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.998), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.997), `double_top_peak` (0.998), `entry_stop_long` (0.994), `entry_stop_short` (0.997), `fib_236` (0.995), `fib_382` (0.996), `fib_500` (0.997), `fib_618` (0.997), `fib_786` (0.997), `fib_ext_127` (0.99), `fib_ext_162` (0.987), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.997), `ichi_kijun` (0.999), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.988), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.996), `monthly_sma_12` (0.974), `monthly_sma_6` (0.992), `pivot` (0.996), `prev_close` (0.996), `prev_high` (0.997), `prev_low` (0.995), `psar_value` (0.997), `r1` (0.996), `r2` (0.997), `r3` (0.997), `s1` (0.995), `s2` (0.994), `s3` (0.993), `supertrend_value` (0.991), `swing_high` (0.993), `swing_low` (0.995), `tema` (0.997), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.995), `vp_value_area_low` (0.994), `weekly_close` (0.996), `weekly_ema_10` (0.999), `weekly_ema_20` (0.995), `wood_p` (0.996), `wood_r1` (0.997), `wood_r2` (0.997), `wood_s1` (0.996), `wood_s2` (0.995), `year_high` (0.953), `year_low` (0.954)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | R4 distance from the prior close, in pri | 5 | MIXED - offline AND pending levels | no - production only; 3 offline; 1 pending (DEFINED-NO-ACTUATOR) | 1 | 3 | 1 |
| P3.1 | volume ratio floor (vol / avg) | 4 | subset-safe | no - derives offline | 1 | 3 | 0 |
| P4 | xs_ivol >= 0.2598 | 5 | subset-safe | no - derives offline | 1 | 4 | 0 |
| P5 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     5 x 4 x 5 x 1 = 100
offline gradings   79 level-combinations x 24 exits = 1896 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  20 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 79 + 20 = 100 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 645 census axes join it only when REGISTERED at the T3 band review.
