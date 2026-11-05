# Table A - macd_crossover

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build ff10274b7 | commit 352770ae3 at 2026-11-05 02:37:24 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** momentum | **status:** NOT-STARTED | **R5 fires:** 2910 (closed fires in the exit cube: 2910 of 2910, S6-B3258) | **surviving fires (T1):** 2910 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  macd_12_26_9_crossover_dn  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define
P2  macd_12_26_9_crossover_up  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define

============================== STRATEGY LAYER ==============================

P3  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_macd_crossover (docstring and return dropped):

```python
fl = s.get('macd_12_26_9_crossover_up')
fs = s.get('macd_12_26_9_crossover_dn') and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | macd_12_26_9_crossover_dn - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P2 | PRODUCER | macd_12_26_9_crossover_up - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P3 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
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
| adx | backtest/signals/technical.py | 100.0% | 17.386, 22.866, 28.92, 36.738 | 17.386: 2328 (80%); 22.866: 1746 (60%); 28.92: 1165 (40%); 36.738: 582 (20%) | 17.386: 582 (20%); 22.866: 1164 (40%); 28.92: 1747 (60%); 36.738: 2328 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 17.956, 22.302, 25.61, 29.54 | 17.956: 2328 (80%); 22.302: 1746 (60%); 25.61: 1165 (40%); 29.54: 583 (20%) | 17.956: 582 (20%); 22.302: 1164 (40%); 25.61: 1748 (60%); 29.54: 2330 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 17.38, 20.98, 24.48, 28.49 | 17.38: 2329 (80%); 20.98: 1749 (60%); 24.48: 1168 (40%); 28.49: 583 (20%) | 17.38: 583 (20%); 20.98: 1165 (40%); 24.48: 1748 (60%); 28.49: 2331 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -6.0769, -1.8041, 1.5774, 6.4116 | -6.0769: 2328 (80%); -1.8041: 1746 (60%); 1.5774: 1164 (40%); 6.4116: 582 (20%) | -6.0769: 582 (20%); -1.8041: 1164 (40%); 1.5774: 1746 (60%); 6.4116: 2328 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.2034, 2.0471, 3.4455, 5.906 | 1.2034: 2328 (80%); 2.0471: 1746 (60%); 3.4455: 1164 (40%); 5.906: 582 (20%) | 1.2034: 582 (20%); 2.0471: 1164 (40%); 3.4455: 1746 (60%); 5.906: 2328 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.2034, 2.0471, 3.4455, 5.906 | 1.2034: 2328 (80%); 2.0471: 1746 (60%); 3.4455: 1164 (40%); 5.906: 582 (20%) | 1.2034: 582 (20%); 2.0471: 1164 (40%); 3.4455: 1746 (60%); 5.906: 2328 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.026, 2.5026, 3.0296, 3.9786 | 2.026: 2329 (80%); 2.5026: 1746 (60%); 3.0296: 1164 (40%); 3.9786: 582 (20%) | 2.026: 583 (20%); 2.5026: 1164 (40%); 3.0296: 1746 (60%); 3.9786: 2328 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0444, 0.0628, 0.0843, 0.12 | 0.0444: 2333 (80%); 0.0628: 1746 (60%); 0.0843: 1166 (40%); 0.12: 583 (20%) | 0.0444: 583 (20%); 0.0628: 1167 (40%); 0.0843: 1747 (60%); 0.12: 2328 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.191, 0.397, 0.5737, 0.7675 | 0.191: 2328 (80%); 0.397: 1746 (60%); 0.5737: 1165 (40%); 0.7675: 583 (20%) | 0.191: 582 (20%); 0.397: 1165 (40%); 0.5737: 1746 (60%); 0.7675: 2329 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0645, 0.089, 0.1174, 0.1633 | 0.0645: 2330 (80%); 0.089: 1749 (60%); 0.1174: 1168 (40%); 0.1633: 583 (20%) | 0.0645: 584 (20%); 0.089: 1165 (40%); 0.1174: 1747 (60%); 0.1633: 2329 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2878, 0.4116, 0.5434, 0.6789 | 0.2878: 2328 (80%); 0.4116: 1747 (60%); 0.5434: 1165 (40%); 0.6789: 583 (20%) | 0.2878: 583 (20%); 0.4116: 1165 (40%); 0.5434: 1746 (60%); 0.6789: 2329 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.086, 0.1187, 0.1565, 0.2177 | 0.086: 2329 (80%); 0.1187: 1748 (60%); 0.1565: 1168 (40%); 0.2177: 583 (20%) | 0.086: 584 (20%); 0.1187: 1165 (40%); 0.1565: 1746 (60%); 0.2177: 2328 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.3408, 0.4337, 0.5325, 0.6342 | 0.3408: 2330 (80%); 0.4337: 1747 (60%); 0.5325: 1165 (40%); 0.6342: 583 (20%) | 0.3408: 583 (20%); 0.4337: 1165 (40%); 0.5325: 1746 (60%); 0.6342: 2329 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0468, -0.0218, -0.0019, 0.0278 | -0.0468: 2328 (80%); -0.0218: 1753 (60%); -0.0019: 1165 (40%); 0.0278: 587 (20%) | -0.0468: 583 (20%); -0.0218: 1167 (40%); -0.0019: 1747 (60%); 0.0278: 2330 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1412, 0.167, 0.2021, 0.2674 | 0.1412: 2326 (80%); 0.167: 1750 (60%); 0.2021: 1160 (40%); 0.2674: 586 (20%) | 0.1412: 584 (20%); 0.167: 1160 (40%); 0.2021: 1750 (60%); 0.2674: 2324 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 2910 (100%) | 0: 2753 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1041, -0.0223, 0.0529, 0.1382 | -0.1041: 2329 (80%); -0.0223: 1746 (60%); 0.0529: 1165 (40%); 0.1382: 583 (20%) | -0.1041: 583 (20%); -0.0223: 1164 (40%); 0.0529: 1748 (60%); 0.1382: 2328 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 2910 (100%); 1: 1183 (41%) | 0: 1727 (59%); 1: 2401 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2354, -0.1909, -0.1541, -0.1236 | -0.2354: 2335 (80%); -0.1909: 1758 (60%); -0.1541: 1186 (41%); -0.1236: 592 (20%) | -0.2354: 599 (21%); -0.1909: 1188 (41%); -0.1541: 1755 (60%); -0.1236: 2341 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3897, 0.6026, 0.6923, 0.7628 | 0.3897: 2328 (80%); 0.6026: 1781 (61%); 0.6923: 1196 (41%); 0.7628: 610 (21%) | 0.3897: 582 (20%); 0.6026: 1171 (40%); 0.6923: 1773 (61%); 0.7628: 2345 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.391, 0.6282, 0.8333 | 0.2628: 2376 (82%); 0.391: 1755 (60%); 0.6282: 1208 (42%); 0.8333: 610 (21%) | 0.2628: 604 (21%); 0.391: 1179 (41%); 0.6282: 1759 (60%); 0.8333: 2337 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1089, -0.0139, 0.0827, 0.1972 | -0.1089: 2343 (81%); -0.0139: 1749 (60%); 0.0827: 1164 (40%); 0.1972: 584 (20%) | -0.1089: 584 (20%); -0.0139: 1167 (40%); 0.0827: 1746 (60%); 0.1972: 2338 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.25, 0.4551, 0.5897, 0.7898 | 0.25: 2360 (81%); 0.4551: 1755 (60%); 0.5897: 1208 (42%); 0.7898: 582 (20%) | 0.25: 589 (20%); 0.4551: 1198 (41%); 0.5897: 1804 (62%); 0.7898: 2328 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1218, 0.3013, 0.4679, 0.641 | 0.1218: 2337 (80%); 0.3013: 1752 (60%); 0.4679: 1191 (41%); 0.641: 604 (21%) | 0.1218: 592 (20%); 0.3013: 1175 (40%); 0.4679: 1753 (60%); 0.641: 2329 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.497, -0.3483, -0.1203, 0.0936 | -0.497: 2346 (81%); -0.3483: 1748 (60%); -0.1203: 1170 (40%); 0.0936: 589 (20%) | -0.497: 598 (21%); -0.3483: 1165 (40%); -0.1203: 1754 (60%); 0.0936: 2331 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3526, 0.5128, 0.7821, 0.9487 | 0.3526: 2332 (80%); 0.5128: 1780 (61%); 0.7821: 1165 (40%); 0.9487: 590 (20%) | 0.3526: 598 (21%); 0.5128: 1173 (40%); 0.7821: 1754 (60%); 0.9487: 2385 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1154, 0.2885, 0.5641, 0.8013 | 0.1154: 2354 (81%); 0.2885: 1783 (61%); 0.5641: 1176 (40%); 0.8013: 614 (21%) | 0.1154: 613 (21%); 0.2885: 1173 (40%); 0.5641: 1759 (60%); 0.8013: 2332 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0681, -0.0588, -0.0388, 0 | -0.0681: 2353 (81%); -0.0588: 1761 (61%); -0.0388: 1180 (41%); 0: 883 (30%) | -0.0681: 607 (21%); -0.0588: 1198 (41%); -0.0388: 1812 (62%); 0: 2826 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.6859, 0.8846, 1 | 0.391: 2349 (81%); 0.6859: 1764 (61%); 0.8846: 1232 (42%); 1: 686 (24%) | 0.391: 613 (21%); 0.6859: 1181 (41%); 0.8846: 1846 (63%); 1: 2910 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1026, 0.2244, 0.5705, 0.8718 | 0.1026: 2343 (81%); 0.2244: 1747 (60%); 0.5705: 1169 (40%); 0.8718: 590 (20%) | 0.1026: 587 (20%); 0.2244: 1190 (41%); 0.5705: 1790 (62%); 0.8718: 2334 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0027, 0.0366, 0.0848, 0.1955 | 0.0027: 2329 (80%); 0.0366: 1750 (60%); 0.0848: 1168 (40%); 0.1955: 583 (20%) | 0.0027: 595 (20%); 0.0366: 1170 (40%); 0.0848: 1756 (60%); 0.1955: 2332 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.5, 0.7788, 0.9295, 0.9744 | 0.5: 2330 (80%); 0.7788: 1750 (60%); 0.9295: 1171 (40%); 0.9744: 613 (21%) | 0.5: 589 (20%); 0.7788: 1179 (41%); 0.9295: 1784 (61%); 0.9744: 2404 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.101, 0.2949, 0.5769, 0.7971 | 0.101: 2331 (80%); 0.2949: 1762 (61%); 0.5769: 1169 (40%); 0.7971: 597 (21%) | 0.101: 661 (23%); 0.2949: 1186 (41%); 0.5769: 1748 (60%); 0.7971: 2336 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0132, 0.1131, 0.2068 | -0.0812: 2548 (88%); -0.0132: 1751 (60%); 0.1131: 1165 (40%); 0.2068: 591 (20%) | -0.0812: 627 (22%); -0.0132: 1173 (40%); 0.1131: 1766 (61%); 0.2068: 2335 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1523, 0.0067, 0.0465, 0.0968 | -0.1523: 2331 (80%); 0.0067: 1748 (60%); 0.0465: 1167 (40%); 0.0968: 583 (20%) | -0.1523: 602 (21%); 0.0067: 1168 (40%); 0.0465: 1753 (60%); 0.0968: 2345 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3526, 0.5897, 0.7628, 0.8846 | 0.3526: 2336 (80%); 0.5897: 1756 (60%); 0.7628: 1178 (40%); 0.8846: 594 (20%) | 0.3526: 593 (20%); 0.5897: 1199 (41%); 0.7628: 1783 (61%); 0.8846: 2341 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3846, 0.5833, 0.8205 | 0.1474: 2347 (81%); 0.3846: 1764 (61%); 0.5833: 1166 (40%); 0.8205: 588 (20%) | 0.1474: 610 (21%); 0.3846: 1277 (44%); 0.5833: 1767 (61%); 0.8205: 2345 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0512, 0.1249, 0.2445, 0.5053 | 0.0512: 2328 (80%); 0.1249: 1746 (60%); 0.2445: 1164 (40%); 0.5053: 582 (20%) | 0.0512: 583 (20%); 0.1249: 1164 (40%); 0.2445: 1746 (60%); 0.5053: 2328 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.8% | 27, 62, 82, 139 | 27: 2304 (79%); 62: 1734 (60%); 82: 1153 (40%); 139: 576 (20%) | 27: 596 (20%); 62: 1189 (41%); 82: 1743 (60%); 139: 2311 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.7% | 1.6974, 2.2114, 2.8239, 3.7422 | 1.6974: 2321 (80%); 2.2114: 1741 (60%); 2.8239: 1161 (40%); 3.7422: 581 (20%) | 1.6974: 581 (20%); 2.2114: 1161 (40%); 2.8239: 1741 (60%); 3.7422: 2321 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 12, 20, 27, 34 | 12: 2354 (81%); 20: 1796 (62%); 27: 1254 (43%); 34: 594 (20%) | 12: 633 (22%); 20: 1235 (42%); 27: 1752 (60%); 34: 2392 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 4 | 1: 2419 (83%); 2: 1764 (61%); 4: 589 (20%) | 1: 1146 (39%); 2: 1761 (61%); 4: 2910 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.012, -0.0029, 0.0117, 0.0228 | -0.012: 2328 (80%); -0.0029: 1747 (60%); 0.0117: 1192 (41%); 0.0228: 589 (20%) | -0.012: 587 (20%); -0.0029: 1173 (40%); 0.0117: 1746 (60%); 0.0228: 2328 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5871, 25.8507, 26.4855, 27.12 | 24.5871: 2334 (80%); 25.8507: 1747 (60%); 26.4855: 1174 (40%); 27.12: 585 (20%) | 24.5871: 586 (20%); 25.8507: 1167 (40%); 26.4855: 1747 (60%); 27.12: 2332 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.6964, -0.148, 0.1814, 0.7602 | -0.6964: 2328 (80%); -0.148: 1747 (60%); 0.1814: 1164 (40%); 0.7602: 582 (20%) | -0.6964: 582 (20%); -0.148: 1166 (40%); 0.1814: 1746 (60%); 0.7602: 2328 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.7602, -0.1814, 0.148, 0.6964 | -0.7602: 2328 (80%); -0.1814: 1746 (60%); 0.148: 1166 (40%); 0.6964: 582 (20%) | -0.7602: 582 (20%); -0.1814: 1164 (40%); 0.148: 1747 (60%); 0.6964: 2328 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0429, -0.0084, 0.0198, 0.0615 | -0.0429: 2330 (80%); -0.0084: 1754 (60%); 0.0198: 1165 (40%); 0.0615: 586 (20%) | -0.0429: 584 (20%); -0.0084: 1165 (40%); 0.0198: 1748 (60%); 0.0615: 2329 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0737, 8.5005, 8.7717, 9.1005 | 8.0737: 2328 (80%); 8.5005: 1758 (60%); 8.7717: 1163 (40%); 9.1005: 585 (20%) | 8.0737: 582 (20%); 8.5005: 1152 (40%); 8.7717: 1747 (60%); 9.1005: 2325 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 2890 (99%); 1: 902 (31%) | 0: 1988 (68%); 1: 2570 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | -1, 0 | -1: 2757 (95%); 0: 2297 (79%) | -1: 593 (20%); 0: 2396 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 2890 (99%); 1: 983 (34%) | 0: 1907 (66%); 1: 2569 (88%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 115.4, 263.2 | 3: 2352 (81%); 6: 1792 (62%); 115.4: 1164 (40%); 263.2: 582 (20%) | 3: 754 (26%); 6: 1275 (44%); 115.4: 1746 (60%); 263.2: 2328 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 4, 82.4, 135 | 1: 2387 (82%); 4: 1839 (63%); 82.4: 1164 (40%); 135: 591 (20%) | 1: 773 (27%); 4: 1165 (40%); 82.4: 1746 (60%); 135: 2331 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.121, -0.0295, 0.0146, 0.0914 | -0.121: 2328 (80%); -0.0295: 1746 (60%); 0.0146: 1165 (40%); 0.0914: 583 (20%) | -0.121: 582 (20%); -0.0295: 1165 (40%); 0.0146: 1748 (60%); 0.0914: 2328 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.5152, -0.7171, 0.6304, 2.6261 | -2.5152: 2328 (80%); -0.7171: 1746 (60%); 0.6304: 1164 (40%); 2.6261: 582 (20%) | -2.5152: 582 (20%); -0.7171: 1164 (40%); 0.6304: 1746 (60%); 2.6261: 2328 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.5832, -0.7436, 0.6723, 2.759 | -2.5832: 2328 (80%); -0.7436: 1746 (60%); 0.6723: 1164 (40%); 2.759: 583 (20%) | -2.5832: 582 (20%); -0.7436: 1164 (40%); 0.6723: 1746 (60%); 2.759: 2329 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.469, -0.143, 0.1029, 0.4179 | -0.469: 2328 (80%); -0.143: 1747 (60%); 0.1029: 1164 (40%); 0.4179: 583 (20%) | -0.469: 583 (20%); -0.143: 1166 (40%); 0.1029: 1746 (60%); 0.4179: 2329 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.2753, -0.6533, 0.531, 2.3681 | -2.2753: 2328 (80%); -0.6533: 1746 (60%); 0.531: 1164 (40%); 2.3681: 582 (20%) | -2.2753: 582 (20%); -0.6533: 1164 (40%); 0.531: 1746 (60%); 2.3681: 2328 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.6005, -0.7746, 0.6919, 2.7977 | -2.6005: 2328 (80%); -0.7746: 1746 (60%); 0.6919: 1164 (40%); 2.7977: 582 (20%) | -2.6005: 583 (20%); -0.7746: 1164 (40%); 0.6919: 1746 (60%); 2.7977: 2328 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 38.452, 46.696, 53.758, 62.014 | 38.452: 2328 (80%); 46.696: 1746 (60%); 53.758: 1164 (40%); 62.014: 582 (20%) | 38.452: 582 (20%); 46.696: 1164 (40%); 53.758: 1746 (60%); 62.014: 2328 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0064, 0.0155, 0.0318, 0.0628 | 0.0064: 2310 (79%); 0.0155: 1737 (60%); 0.0318: 1154 (40%); 0.0628: 577 (20%) | 0.0064: 578 (20%); 0.0155: 1151 (40%); 0.0318: 1734 (60%); 0.0628: 2311 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 8 | 0: 2910 (100%); 1: 2206 (76%); 4: 1165 (40%); 8: 646 (22%) | 0: 704 (24%); 1: 1169 (40%); 4: 1926 (66%); 8: 2342 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1528 | 0: 2910 (100%); 0.1528: 582 (20%) | 0: 1993 (68%); 0.1528: 2328 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1563, 0.4286, 0.6667 | 0: 2910 (100%); 0.1563: 1746 (60%); 0.4286: 1181 (41%); 0.6667: 643 (22%) | 0: 1123 (39%); 0.1563: 1164 (40%); 0.4286: 1767 (61%); 0.6667: 2369 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 2910 (100%); 1: 2046 (70%); 2: 1490 (51%); 6: 616 (21%) | 0: 864 (30%); 1: 1420 (49%); 2: 1764 (61%); 6: 2386 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 8 | 0: 2910 (100%); 1: 2206 (76%); 4: 1165 (40%); 8: 646 (22%) | 0: 704 (24%); 1: 1169 (40%); 4: 1926 (66%); 8: 2342 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 2910 (100%); 1: 2019 (69%); 3: 1267 (44%); 7: 632 (22%) | 0: 891 (31%); 1: 1339 (46%); 3: 1876 (64%); 7: 2357 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2197, 0.3703, 0.5984 | 0: 2692 (93%); 0.2197: 1746 (60%); 0.3703: 1164 (40%); 0.5984: 582 (20%) | 0: 659 (23%); 0.2197: 1165 (40%); 0.3703: 1746 (60%); 0.5984: 2328 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667, 0.6 | 0: 2633 (90%); 0.1667: 1168 (40%); 0.6: 592 (20%) | 0: 1575 (54%); 0.1667: 1759 (60%); 0.6: 2330 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3096, 0.6 | 0: 2654 (91%); 0.3096: 1164 (40%); 0.6: 591 (20%) | 0: 1301 (45%); 0.3096: 1746 (60%); 0.6: 2344 (81%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3096, 0.6 | 0: 2654 (91%); 0.3096: 1164 (40%); 0.6: 591 (20%) | 0: 1301 (45%); 0.3096: 1746 (60%); 0.6: 2344 (81%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1578, 0, 0.155 | -0.1578: 2328 (80%); 0: 2095 (72%); 0.155: 582 (20%) | -0.1578: 582 (20%); 0: 2115 (73%); 0.155: 2328 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7571, -0.3262, 0, 1.1356 | -0.7571: 2337 (80%); -0.3262: 1748 (60%); 0: 1570 (54%); 1.1356: 584 (20%) | -0.7571: 594 (20%); -0.3262: 1165 (40%); 0: 1748 (60%); 1.1356: 2339 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 2467 (85%); 4: 1857 (64%); 7: 1192 (41%); 11: 590 (20%) | 2: 757 (26%); 4: 1290 (44%); 7: 1887 (65%); 11: 2408 (83%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0257, -0.0072, 0.0064, 0.0228 | -0.0257: 2327 (80%); -0.0072: 1741 (60%); 0.0064: 1166 (40%); 0.0228: 583 (20%) | -0.0257: 583 (20%); -0.0072: 1169 (40%); 0.0064: 1744 (60%); 0.0228: 2327 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0799, -0.0306, 0.0194, 0.0675 | -0.0799: 2327 (80%); -0.0306: 1746 (60%); 0.0194: 1163 (40%); 0.0675: 582 (20%) | -0.0799: 583 (20%); -0.0306: 1164 (40%); 0.0194: 1747 (60%); 0.0675: 2328 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0299, -0.0102, 0.0056, 0.0304 | -0.0299: 2328 (80%); -0.0102: 1746 (60%); 0.0056: 1166 (40%); 0.0304: 584 (20%) | -0.0299: 582 (20%); -0.0102: 1165 (40%); 0.0056: 1744 (60%); 0.0304: 2326 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -20.7898, -7.029, 7.0294, 27.0102 | -20.7898: 2328 (80%); -7.029: 1746 (60%); 7.0294: 1164 (40%); 27.0102: 582 (20%) | -20.7898: 582 (20%); -7.029: 1164 (40%); 7.0294: 1746 (60%); 27.0102: 2328 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0358, 0.0483, 0.063, 0.0846 | 0.0358: 2331 (80%); 0.0483: 1749 (60%); 0.063: 1168 (40%); 0.0846: 583 (20%) | 0.0358: 585 (20%); 0.0483: 1166 (40%); 0.063: 1749 (60%); 0.0846: 2330 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1577, 0.3536, 0.6017, 0.8317 | 0.1577: 2328 (80%); 0.3536: 1746 (60%); 0.6017: 1166 (40%); 0.8317: 583 (20%) | 0.1577: 582 (20%); 0.3536: 1164 (40%); 0.6017: 1746 (60%); 0.8317: 2328 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.7954, -1.295, 0.886, 2.1281 | -2.7954: 2328 (80%); -1.295: 1746 (60%); 0.886: 1164 (40%); 2.1281: 582 (20%) | -2.7954: 582 (20%); -1.295: 1164 (40%); 0.886: 1746 (60%); 2.1281: 2328 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.1483, -0.067, -0.0112, 0.0713 | -0.1483: 2328 (80%); -0.067: 1747 (60%); -0.0112: 1166 (40%); 0.0713: 583 (20%) | -0.1483: 583 (20%); -0.067: 1165 (40%); -0.0112: 1747 (60%); 0.0713: 2329 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -2.8773, -1.3548, 0.9632, 2.2491 | -2.8773: 2328 (80%); -1.3548: 1746 (60%); 0.9632: 1164 (40%); 2.2491: 582 (20%) | -2.8773: 583 (20%); -1.3548: 1164 (40%); 0.9632: 1746 (60%); 2.2491: 2328 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -3.7222, -1.2286, 0.692, 2.764 | -3.7222: 2328 (80%); -1.2286: 1746 (60%); 0.692: 1165 (40%); 2.764: 582 (20%) | -3.7222: 582 (20%); -1.2286: 1164 (40%); 0.692: 1747 (60%); 2.764: 2328 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.49, 46.726, 51.9, 57.422 | 41.49: 2329 (80%); 46.726: 1746 (60%); 51.9: 1165 (40%); 57.422: 582 (20%) | 41.49: 583 (20%); 46.726: 1164 (40%); 51.9: 1747 (60%); 57.422: 2328 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 11.734, 27.212, 65.528, 86.056 | 11.734: 2328 (80%); 27.212: 1746 (60%); 65.528: 1164 (40%); 86.056: 582 (20%) | 11.734: 582 (20%); 27.212: 1164 (40%); 65.528: 1746 (60%); 86.056: 2328 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.76, 46.39, 51.88, 57.832 | 41.76: 2330 (80%); 46.39: 1748 (60%); 51.88: 1165 (40%); 57.832: 582 (20%) | 41.76: 584 (20%); 46.39: 1166 (40%); 51.88: 1747 (60%); 57.832: 2328 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 42.184, 47.406, 51.51, 56.64 | 42.184: 2328 (80%); 47.406: 1746 (60%); 51.51: 1166 (40%); 56.64: 583 (20%) | 42.184: 582 (20%); 47.406: 1164 (40%); 51.51: 1747 (60%); 56.64: 2330 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 2908 (100%) | 0: 2909 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0317, 0.0458, 0.0608, 0.0908 | 0.0317: 2337 (80%); 0.0458: 1749 (60%); 0.0608: 1164 (40%); 0.0908: 583 (20%) | 0.0317: 583 (20%); 0.0458: 1169 (40%); 0.0608: 1746 (60%); 0.0908: 2329 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0815, -0.0569, -0.0435, -0.0344 | -0.0815: 2331 (80%); -0.0569: 1748 (60%); -0.0435: 1173 (40%); -0.0344: 585 (20%) | -0.0815: 584 (20%); -0.0569: 1166 (40%); -0.0435: 1746 (60%); -0.0344: 2337 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 2910 (100%); 2: 623 (21%) | 0: 1978 (68%); 2: 2445 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.7% | 24, 42, 57, 68 | 24: 2451 (84%); 42: 1742 (60%); 57: 1178 (40%); 68: 631 (22%) | 24: 582 (20%); 42: 1191 (41%); 57: 1753 (60%); 68: 2344 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.6% | 0.0118, 0.0171, 0.025, 0.0405 | 0.0118: 2300 (79%); 0.0171: 1724 (59%); 0.025: 1149 (39%); 0.0405: 575 (20%) | 0.0118: 570 (20%); 0.0171: 1147 (39%); 0.025: 1721 (59%); 0.0405: 2295 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.1939, 0.3369, 0.6171, 0.7921 | 0.1939: 2327 (80%); 0.3369: 1745 (60%); 0.6171: 1164 (40%); 0.7921: 582 (20%) | 0.1939: 582 (20%); 0.3369: 1164 (40%); 0.6171: 1745 (60%); 0.7921: 2327 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 39.06, 76.42, 112.1, 162.5 | 39.06: 2327 (80%); 76.42: 1745 (60%); 112.1: 1166 (40%); 162.5: 583 (20%) | 39.06: 582 (20%); 76.42: 1164 (40%); 112.1: 1747 (60%); 162.5: 2328 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -2.94, -0.7425, 0.431, 2.651 | -2.94: 2329 (80%); -0.7425: 1747 (60%); 0.431: 1164 (40%); 2.651: 582 (20%) | -2.94: 583 (20%); -0.7425: 1165 (40%); 0.431: 1746 (60%); 2.651: 2328 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 26.326, 39.318, 60.764, 75.072 | 26.326: 2328 (80%); 39.318: 1746 (60%); 60.764: 1164 (40%); 75.072: 582 (20%) | 26.326: 582 (20%); 39.318: 1164 (40%); 60.764: 1746 (60%); 75.072: 2328 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 32, 43.876, 55.48, 67.494 | 32: 2329 (80%); 43.876: 1746 (60%); 55.48: 1165 (40%); 67.494: 582 (20%) | 32: 584 (20%); 43.876: 1164 (40%); 55.48: 1747 (60%); 67.494: 2328 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 20.638, 39.808, 58.288, 75.962 | 20.638: 2328 (80%); 39.808: 1746 (60%); 58.288: 1164 (40%); 75.962: 582 (20%) | 20.638: 582 (20%); 39.808: 1164 (40%); 58.288: 1746 (60%); 75.962: 2328 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 32.094, 59.61, 95.474 | 0: 2910 (100%); 32.094: 1746 (60%); 59.61: 1165 (40%); 95.474: 582 (20%) | 0: 647 (22%); 32.094: 1164 (40%); 59.61: 1747 (60%); 95.474: 2328 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 17 | 4: 2382 (82%); 8: 1794 (62%); 13: 1209 (42%); 17: 679 (23%) | 4: 716 (25%); 8: 1227 (42%); 13: 1836 (63%); 17: 2405 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 18 | 5: 2398 (82%); 9: 1823 (63%); 14: 1215 (42%); 18: 687 (24%) | 5: 650 (22%); 9: 1227 (42%); 14: 1819 (63%); 18: 2381 (82%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 44.206, 48.546, 52.074, 55.73 | 44.206: 2328 (80%); 48.546: 1746 (60%); 52.074: 1164 (40%); 55.73: 584 (20%) | 44.206: 582 (20%); 48.546: 1164 (40%); 52.074: 1746 (60%); 55.73: 2330 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1746, 0.4444, 0.7063, 0.8651 | 0.1746: 2329 (80%); 0.4444: 1749 (60%); 0.7063: 1167 (40%); 0.8651: 587 (20%) | 0.1746: 598 (21%); 0.4444: 1179 (41%); 0.7063: 1755 (60%); 0.8651: 2329 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.91, 17.31, 20.6, 26.1 | 14.91: 2329 (80%); 17.31: 1748 (60%); 20.6: 1166 (40%); 26.1: 603 (21%) | 14.91: 594 (20%); 17.31: 1167 (40%); 20.6: 1751 (60%); 26.1: 2331 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.91, 17.31, 20.6, 26.1 | 14.91: 2329 (80%); 17.31: 1748 (60%); 20.6: 1166 (40%); 26.1: 603 (21%) | 14.91: 594 (20%); 17.31: 1167 (40%); 20.6: 1751 (60%); 26.1: 2331 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8582, 0.8923, 0.9283, 0.9671 | 0.8582: 2331 (80%); 0.8923: 1748 (60%); 0.9283: 1170 (40%); 0.9671: 583 (20%) | 0.8582: 583 (20%); 0.8923: 1174 (40%); 0.9283: 1747 (60%); 0.9671: 2332 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.68, 0.82, 0.95, 1.18 | 0.68: 2361 (81%); 0.82: 1751 (60%); 0.95: 1166 (40%); 1.18: 585 (20%) | 0.68: 591 (20%); 0.82: 1206 (41%); 0.95: 1781 (61%); 1.18: 2340 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0194, 0.0493, 0.0827, 0.1341 | 0.0194: 2329 (80%); 0.0493: 1748 (60%); 0.0827: 1166 (40%); 0.1341: 584 (20%) | 0.0194: 584 (20%); 0.0493: 1165 (40%); 0.0827: 1746 (60%); 0.1341: 2328 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 45.9219, 77.3548, 121.595, 201.731 | 45.9219: 2328 (80%); 77.3548: 1746 (60%); 121.595: 1164 (40%); 201.731: 582 (20%) | 45.9219: 582 (20%); 77.3548: 1164 (40%); 121.595: 1746 (60%); 201.731: 2328 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.7908, 73.9563, 116.3094, 191.7057 | 43.7908: 2328 (80%); 73.9563: 1746 (60%); 116.3094: 1164 (40%); 191.7057: 582 (20%) | 43.7908: 582 (20%); 73.9563: 1164 (40%); 116.3094: 1746 (60%); 191.7057: 2328 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.5173, 70.6757, 110.8553, 184.7191 | 41.5173: 2328 (80%); 70.6757: 1746 (60%); 110.8553: 1164 (40%); 184.7191: 582 (20%) | 41.5173: 582 (20%); 70.6757: 1164 (40%); 110.8553: 1746 (60%); 184.7191: 2328 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.6609, 80.6691, 126.5009, 208.8697 | 47.6609: 2328 (80%); 80.6691: 1746 (60%); 126.5009: 1164 (40%); 208.8697: 582 (20%) | 47.6609: 582 (20%); 80.6691: 1164 (40%); 126.5009: 1746 (60%); 208.8697: 2328 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 49.8031, 82.9948, 131.8928, 216.6484 | 49.8031: 2328 (80%); 82.9948: 1746 (60%); 131.8928: 1164 (40%); 216.6484: 582 (20%) | 49.8031: 582 (20%); 82.9948: 1164 (40%); 131.8928: 1746 (60%); 216.6484: 2328 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2910 (100%) | 0: 2600 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2910 (100%) | 0: 2669 (92%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0674, -0.0261, 0.0128, 0.0526 | -0.0674: 2328 (80%); -0.0261: 1746 (60%); 0.0128: 1165 (40%); 0.0526: 583 (20%) | -0.0674: 583 (20%); -0.0261: 1164 (40%); 0.0128: 1747 (60%); 0.0526: 2328 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -69.6, -55.83, -46.056, -34.016 | -69.6: 2329 (80%); -55.83: 1747 (60%); -46.056: 1164 (40%); -34.016: 582 (20%) | -69.6: 583 (20%); -55.83: 1166 (40%); -46.056: 1746 (60%); -34.016: 2328 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.5556, 0.8324, 1.0561, 1.3305 | 0.5556: 2308 (79%); 0.8324: 1731 (59%); 1.0561: 1154 (40%); 1.3305: 577 (20%) | 0.5556: 577 (20%); 0.8324: 1154 (40%); 1.0561: 1731 (59%); 1.3305: 2308 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 2429 (83%); 5: 1911 (66%); 7: 1362 (47%); 9: 762 (26%) | 3: 700 (24%); 5: 1255 (43%); 7: 1816 (62%); 9: 2464 (85%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.0% | 0.1922, 0.2324, 0.2835, 0.3651 | 0.1922: 2306 (79%); 0.2324: 1729 (59%); 0.2835: 1153 (40%); 0.3651: 578 (20%) | 0.1922: 578 (20%); 0.2324: 1153 (40%); 0.2835: 1730 (59%); 0.3651: 2306 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.0% | 3, 5, 8, 9 | 3: 2414 (83%); 5: 1971 (68%); 8: 1154 (40%); 9: 812 (28%) | 3: 661 (23%); 5: 1157 (40%); 8: 2070 (71%); 9: 2439 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0239, 0.0329, 0.0436, 0.0633 | 0.0239: 2313 (79%); 0.0329: 1734 (60%); 0.0436: 1159 (40%); 0.0633: 580 (20%) | 0.0239: 583 (20%); 0.0329: 1157 (40%); 0.0436: 1733 (60%); 0.0633: 2309 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 6, 8, 9 | 3: 2457 (84%); 6: 1736 (60%); 8: 1155 (40%); 9: 807 (28%) | 3: 644 (22%); 6: 1444 (50%); 8: 2078 (71%); 9: 2456 (84%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.2% | -0.2023, -0.0598, 0.0652, 0.2542 | -0.2023: 2309 (79%); -0.0598: 1732 (60%); 0.0652: 1155 (40%); 0.2542: 578 (20%) | -0.2023: 578 (20%); -0.0598: 1156 (40%); 0.0652: 1733 (60%); 0.2542: 2309 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.2% | 2, 4, 6, 8 | 2: 2501 (86%); 4: 1879 (65%); 6: 1294 (44%); 8: 824 (28%) | 2: 718 (25%); 4: 1307 (45%); 6: 1832 (63%); 8: 2310 (79%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.3% |
| 8k_item_5_02_filed_within_7d | 3.1% |
| above_avwap_20high | 24.5% |
| above_avwap_20low | 75.3% |
| above_avwap_252low | 75.5% |
| above_avwap_50low | 84.4% |
| above_cam_r3 | 34.9% |
| above_cam_r4 | 23.7% |
| above_cpr | 47.6% |
| above_pivot | 46.9% |
| above_prev_high | 30.4% |
| above_prev_high_clearance_atr_05 | 11.8% |
| above_prev_low | 66.3% |
| above_r1 | 27.0% |
| above_r2 | 13.4% |
| above_vwap | 49.6% |
| above_wood_p | 47.5% |
| ad_rising | 50.8% |
| adx_cross_up | 0.4% |
| adx_cross_up_20 | 0.5% |
| adx_di_bear | 53.9% |
| adx_di_bull | 46.1% |
| adx_strong | 13.7% |
| adx_trending | 53.0% |
| ao_cross_dn | 0.7% |
| ao_cross_up | 0.4% |
| ao_positive | 48.2% |
| ao_twin_peaks_bull | 7.7% |
| at_key_fib | 13.1% |
| at_key_fib_wide | 30.7% |
| avwap_20high_loss_recent_3d | 27.3% |
| avwap_20high_reclaim_recent_3d | 20.8% |
| avwap_20low_loss_recent_3d | 19.7% |
| avwap_20low_reclaim_recent_3d | 24.1% |
| avwap_252low_loss_recent_3d | 4.7% |
| avwap_252low_reclaim_recent_3d | 15.7% |
| avwap_50low_loss_recent_3d | 9.5% |
| avwap_50low_reclaim_recent_3d | 23.4% |
| bb_10_20_above_mid | 48.7% |
| bb_10_20_expanding | 42.3% |
| bb_10_20_pctb_gt_75 | 21.6% |
| bb_10_20_pctb_gt_8 | 17.3% |
| bb_10_20_pctb_gt_85 | 12.6% |
| bb_10_20_pctb_gt_9 | 9.1% |
| bb_10_20_pctb_gt_95 | 6.3% |
| bb_10_20_pctb_lt_05 | 8.9% |
| bb_10_20_pctb_lt_1 | 12.3% |
| bb_10_20_pctb_lt_15 | 15.9% |
| bb_10_20_pctb_lt_2 | 20.7% |
| bb_10_20_pctb_lt_25 | 25.1% |
| bb_10_20_reclaim_from_lower_recent_3d | 3.2% |
| bb_10_20_reclaim_from_upper_recent_3d | 3.3% |
| bb_10_20_squeeze | 56.7% |
| bb_10_20_touch_lower | 11.2% |
| bb_10_20_touch_upper | 7.5% |
| bb_20_15_above_mid | 46.5% |
| bb_20_15_expanding | 20.1% |
| bb_20_15_pctb_gt_75 | 11.0% |
| bb_20_15_pctb_gt_8 | 6.8% |
| bb_20_15_pctb_gt_85 | 4.4% |
| bb_20_15_pctb_gt_9 | 3.2% |
| bb_20_15_pctb_gt_95 | 2.3% |
| bb_20_15_pctb_lt_05 | 5.7% |
| bb_20_15_pctb_lt_1 | 6.9% |
| bb_20_15_pctb_lt_15 | 8.9% |
| bb_20_15_pctb_lt_2 | 11.3% |
| bb_20_15_pctb_lt_25 | 15.5% |
| bb_20_15_reclaim_from_lower_recent_3d | 12.1% |
| bb_20_15_reclaim_from_upper_recent_3d | 13.2% |
| bb_20_15_squeeze | 32.1% |
| bb_20_15_touch_lower | 6.1% |
| bb_20_15_touch_upper | 2.8% |
| bb_20_20_above_mid | 46.5% |
| bb_20_20_expanding | 20.1% |
| bb_20_20_pctb_gt_75 | 5.0% |
| bb_20_20_pctb_gt_8 | 3.2% |
| bb_20_20_pctb_gt_85 | 2.1% |
| bb_20_20_pctb_gt_9 | 1.5% |
| bb_20_20_pctb_gt_95 | 1.1% |
| bb_20_20_pctb_lt_05 | 3.3% |
| bb_20_20_pctb_lt_1 | 4.1% |
| bb_20_20_pctb_lt_15 | 5.4% |
| bb_20_20_pctb_lt_2 | 6.9% |
| bb_20_20_pctb_lt_25 | 9.4% |
| bb_20_20_reclaim_from_lower_recent_3d | 3.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 2.5% |
| bb_20_20_squeeze | 16.1% |
| bb_20_20_touch_lower | 3.3% |
| bb_20_20_touch_upper | 1.1% |
| bearish_engulfing | 4.8% |
| bearish_pin_bar | 4.2% |
| below_avwap_20high | 75.5% |
| below_avwap_20low | 24.7% |
| below_avwap_252low | 24.5% |
| below_avwap_50low | 15.6% |
| below_cam_s3 | 40.5% |
| below_cam_s4 | 27.3% |
| below_cpr | 53.0% |
| below_ema_20 | 52.9% |
| below_ema_200 | 54.1% |
| below_ema_200_break_recent_5d | 5.0% |
| below_ema_20_break_recent_5d | 20.4% |
| below_ema_21 | 52.9% |
| below_ema_21_break_recent_5d | 19.3% |
| below_ema_50 | 52.6% |
| below_ema_50_break_recent_5d | 8.1% |
| below_ema_9 | 52.5% |
| below_ema_9_break_recent_5d | 44.8% |
| below_prev_high | 69.4% |
| below_prev_low | 33.6% |
| below_prev_low_clearance_atr_05 | 15.2% |
| below_s1 | 30.7% |
| below_s2 | 16.6% |
| below_sma_20 | 53.5% |
| below_sma_200 | 53.4% |
| below_sma_21 | 53.3% |
| below_sma_50 | 52.5% |
| below_sma_9 | 52.0% |
| below_vwap | 50.4% |
| blowoff_recent_3d | 0.6% |
| break_52w_high | 0.2% |
| break_52w_high_clearance_atr_05 | 0.1% |
| break_52w_high_confirmed_today | 0.1% |
| break_52w_low | 0.7% |
| bullish_engulfing | 3.8% |
| bullish_pin_bar | 3.8% |
| capitulation_recent_3d | 0.5% |
| ceo_buy | 1.1% |
| cfo_buy | 0.6% |
| chandelier_long_bullish | 62.2% |
| chandelier_long_flip_dn | 6.9% |
| chandelier_short_bearish | 65.5% |
| chandelier_short_flip_up | 4.8% |
| classification_change_from_tech | 66.7% |
| classification_change_to_defensive | 33.3% |
| close_above_open | 47.6% |
| close_below_open | 52.4% |
| close_in_bottom_40pct_of_range | 43.5% |
| close_in_top_40pct_of_range | 40.2% |
| cluster_buy | 0.7% |
| cmf_cross_dn | 4.9% |
| cmf_cross_up | 4.0% |
| cmf_negative | 46.9% |
| cmf_positive | 53.1% |
| concentrated_sell | 5.8% |
| cpr_narrow | 87.9% |
| cpr_narrow_tight | 26.1% |
| cup_handle_detected | 14.3% |
| cup_handle_neckline_break_retest_long | 4.2% |
| dc10_breakout_dn | 9.2% |
| dc10_breakout_dn_1pct | 14.0% |
| dc10_breakout_up | 5.7% |
| dc10_breakout_up_1pct | 9.8% |
| dc10_new_high | 8.7% |
| dc10_strong_breakout_dn | 3.9% |
| dc10_strong_breakout_up | 1.9% |
| dc20_breakout_dn | 3.1% |
| dc20_breakout_up | 1.1% |
| dc20_new_high | 2.6% |
| dc20_resistance_break_retest_strong | 9.7% |
| dc20_support_break_retest_strong | 8.5% |
| defensive_leadership | 56.8% |
| director_only_buy | 3.7% |
| doji | 3.1% |
| double_bottom_detected | 11.6% |
| double_top_detected | 13.5% |
| dpi_elevated | 49.6% |
| drying_volume_on_down_turn | 33.8% |
| drying_volume_on_up_turn | 33.5% |
| ema_20_50_bearish | 51.5% |
| ema_20_50_bullish | 48.5% |
| ema_20_50_death_cross | 0.2% |
| ema_20_50_golden_cross | 0.5% |
| ema_50_200_bearish | 51.9% |
| ema_50_200_bullish | 48.1% |
| ema_50_200_death_cross | 0.3% |
| ema_50_200_golden_cross | 0.3% |
| ema_9_21_bearish | 52.2% |
| ema_9_21_bullish | 47.8% |
| ema_9_21_death_cross | 1.4% |
| ema_9_21_golden_cross | 0.9% |
| evening_star | 6.3% |
| flag_bear_break_retest_short | 0.7% |
| flag_bear_broke | 0.9% |
| flag_bear_detected | 0.8% |
| flag_bull_break_retest_long | 2.3% |
| flag_bull_broke | 2.5% |
| flag_bull_detected | 3.3% |
| force_index_cross_dn | 13.4% |
| force_index_cross_up | 10.9% |
| force_index_positive | 47.2% |
| gap_dn_1_5pct | 8.3% |
| gap_dn_2pct | 5.1% |
| gap_up_1_5pct | 8.1% |
| gap_up_2pct | 4.4% |
| hammer | 3.5% |
| head_shoulders_bottom_detected | 3.6% |
| head_shoulders_top_detected | 4.6% |
| house_cluster_buy | 4.4% |
| house_cluster_sell | 4.9% |
| htf_aligned_bear | 41.8% |
| htf_aligned_bull | 36.8% |
| htf_disagreement | 1.3% |
| hull_bearish | 50.6% |
| hull_bullish | 49.4% |
| hull_flip_dn | 17.3% |
| hull_flip_up | 13.6% |
| ichi_above_cloud | 42.8% |
| ichi_above_cloud_break_recent_5d | 3.1% |
| ichi_below_cloud | 47.6% |
| ichi_below_cloud_break_recent_5d | 4.3% |
| ichi_cloud_thick | 85.9% |
| ichi_tk_bearish | 51.3% |
| ichi_tk_bullish | 46.4% |
| ichi_tk_cross_dn | 1.1% |
| ichi_tk_cross_up | 0.7% |
| ichi_weekly_above_cloud | 39.1% |
| ichi_weekly_below_cloud | 32.9% |
| ichi_weekly_in_cloud | 28.0% |
| in_reversal_window | 1.7% |
| inside_bar | 9.3% |
| inside_cpr | 1.1% |
| inside_kc | 95.5% |
| insider_cluster_active | 24.6% |
| institutional_buy | 89.7% |
| institutional_negative | 4.6% |
| institutional_persistence_growing | 43.2% |
| institutional_persistence_strong | 58.9% |
| institutional_strong_buy | 80.1% |
| inverted_cup_handle_detected | 10.2% |
| is_friday | 20.2% |
| is_halloween_period | 49.4% |
| is_halloween_period_first_day | 0.3% |
| is_january | 8.3% |
| is_january_extended | 10.7% |
| is_monday | 16.9% |
| is_pre_holiday | 5.3% |
| is_summer_period | 50.6% |
| is_totm_window | 35.7% |
| is_totm_window_first_day | 8.9% |
| is_week_open | 19.5% |
| kc_touch_lower | 3.9% |
| kc_touch_upper | 2.3% |
| large_dollar_buy | 1.2% |
| macd_12_26_9_bearish | 52.4% |
| macd_12_26_9_bullish | 47.6% |
| macd_12_26_9_crossover_dn | 52.4% |
| macd_12_26_9_crossover_up | 47.6% |
| macd_8_21_5_bearish | 51.1% |
| macd_8_21_5_bullish | 48.9% |
| macd_8_21_5_crossover_dn | 8.2% |
| macd_8_21_5_crossover_up | 6.5% |
| marubozu_bear | 1.1% |
| marubozu_bull | 1.4% |
| mfi_broad_overbought | 7.5% |
| mfi_broad_oversold | 6.2% |
| mfi_overbought | 0.8% |
| mfi_oversold | 0.5% |
| monthly_above_sma_12 | 46.7% |
| monthly_above_sma_6 | 46.6% |
| monthly_bias_bear | 46.9% |
| monthly_bias_bull | 40.2% |
| monthly_momentum_pos | 47.4% |
| morning_star | 4.7% |
| near_52w_high | 3.8% |
| near_52w_high_95pct | 17.4% |
| near_52w_high_retest_long | 0.2% |
| near_52w_low | 1.6% |
| near_52w_low_105pct | 8.0% |
| near_52w_low_retest_short | 0.1% |
| near_avwap_20high_atr_05x | 42.0% |
| near_avwap_20high_atr_10x | 76.5% |
| near_avwap_20high_atr_15x | 92.3% |
| near_avwap_20high_atr_20x | 98.1% |
| near_avwap_20low_atr_05x | 38.9% |
| near_avwap_20low_atr_10x | 72.3% |
| near_avwap_20low_atr_15x | 89.1% |
| near_avwap_20low_atr_20x | 96.4% |
| near_avwap_252low_atr_05x | 15.2% |
| near_avwap_252low_atr_10x | 30.6% |
| near_avwap_252low_atr_15x | 40.9% |
| near_avwap_252low_atr_20x | 49.1% |
| near_avwap_50low_atr_05x | 24.1% |
| near_avwap_50low_atr_10x | 49.7% |
| near_avwap_50low_atr_15x | 64.9% |
| near_avwap_50low_atr_20x | 75.0% |
| near_cam_r3 | 10.1% |
| near_cam_s3 | 13.5% |
| near_cam_s4 | 11.2% |
| near_fib_236 | 7.5% |
| near_fib_382 | 4.7% |
| near_fib_500 | 4.2% |
| near_fib_618 | 4.3% |
| near_fib_786 | 6.2% |
| near_pivot | 10.4% |
| near_prev_close | 11.2% |
| near_prev_high | 9.0% |
| near_prev_low | 11.5% |
| near_r1 | 8.9% |
| near_r1_wide | 44.1% |
| near_r2 | 5.6% |
| near_r2_wide | 29.1% |
| near_s1 | 12.4% |
| near_s1_wide | 46.1% |
| near_s2 | 6.7% |
| near_s2_wide | 33.3% |
| near_s3 | 3.7% |
| near_wood_r1 | 7.7% |
| near_wood_s1 | 9.2% |
| news_uses_polygon_score | 23.1% |
| obv_bearish | 51.0% |
| obv_bullish | 49.0% |
| obv_diverge_bull | 9.7% |
| obv_falling | 52.1% |
| obv_rising | 47.9% |
| outside_bar | 9.1% |
| pead_negative_surprise | 17.9% |
| pead_positive_surprise | 23.1% |
| pin_bar | 8.1% |
| po3_accumulation_active | 42.5% |
| po3_bearish | 8.1% |
| po3_bullish | 7.1% |
| po3_manipulation_sweep_down | 15.7% |
| po3_manipulation_sweep_up | 9.3% |
| po3_mmbm_setup | 0.5% |
| po3_mmsm_setup | 1.6% |
| po3_sweep_above_prior_high | 51.3% |
| po3_sweep_below_prior_low | 53.9% |
| ppo_bullish | 36.2% |
| ppo_crossover_dn | 42.2% |
| ppo_crossover_up | 36.1% |
| pre_fomc_d0 | 2.1% |
| pre_fomc_d1 | 2.5% |
| pre_fomc_window | 4.6% |
| price_above_dema | 47.6% |
| price_above_ema_20 | 47.1% |
| price_above_ema_200 | 45.9% |
| price_above_ema_200_break_recent_5d | 3.0% |
| price_above_ema_20_break_recent_5d | 17.2% |
| price_above_ema_21 | 47.1% |
| price_above_ema_21_break_recent_5d | 16.1% |
| price_above_ema_50 | 47.4% |
| price_above_ema_50_break_recent_5d | 6.9% |
| price_above_ema_9 | 47.5% |
| price_above_ema_9_break_recent_5d | 40.7% |
| price_above_hull | 47.8% |
| price_above_sma_200 | 46.6% |
| price_above_sma_21 | 46.7% |
| price_above_sma_50 | 47.5% |
| price_above_tema | 48.1% |
| price_below_dema | 52.4% |
| price_below_hull | 52.2% |
| price_below_tema | 51.9% |
| psar_bullish | 47.0% |
| psar_flip_dn | 12.0% |
| psar_flip_up | 11.4% |
| r1_break_retest_long | 52.9% |
| recent_blowoff_at_r3 | 0.0% |
| recent_capitulation_at_s3 | 0.1% |
| resistance_break_retest | 13.6% |
| risk_off_regime_bond_signal | 23.6% |
| risk_off_regime_bond_signal_strong | 7.3% |
| risk_off_regime_gold_signal | 39.8% |
| risk_on_regime_bond_signal | 42.2% |
| risk_on_regime_bond_signal_strong | 17.8% |
| roc_positive | 47.4% |
| roc_turning_dn | 12.3% |
| roc_turning_up | 10.0% |
| rsi_14_bullish | 46.7% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 1.4% |
| rsi_14_cross_dn_overbought_recent_3d | 11.9% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.4% |
| rsi_14_cross_up_oversold_recent_3d | 7.9% |
| rsi_14_extreme_os | 0.2% |
| rsi_14_overbought | 1.4% |
| rsi_14_oversold | 1.4% |
| rsi_14_rising | 46.3% |
| rsi_21_bullish | 47.8% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_21_cross_dn_overbought_recent_3d | 6.3% |
| rsi_21_cross_up_oversold_recent_3d | 4.0% |
| rsi_21_extreme_os | 0.1% |
| rsi_21_overbought | 1.0% |
| rsi_21_oversold | 0.6% |
| rsi_21_rising | 46.2% |
| rsi_2_bullish | 47.6% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 31.4% |
| rsi_2_cross_dn_overbought_recent_3d | 39.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 27.1% |
| rsi_2_cross_up_oversold_recent_3d | 34.3% |
| rsi_2_extreme_ob | 27.5% |
| rsi_2_extreme_os | 32.4% |
| rsi_2_overbought | 36.5% |
| rsi_2_oversold | 41.8% |
| rsi_2_rising | 46.2% |
| rsi_9_bullish | 47.0% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 3.6% |
| rsi_9_cross_dn_overbought_recent_3d | 17.9% |
| rsi_9_cross_up_extreme_os_recent_3d | 2.0% |
| rsi_9_cross_up_oversold_recent_3d | 14.1% |
| rsi_9_extreme_os | 0.2% |
| rsi_9_overbought | 1.7% |
| rsi_9_oversold | 3.0% |
| rsi_9_rising | 46.2% |
| s1_break_retest_short | 52.5% |
| sc_13d_filed_within_30d | 1.5% |
| sc_13g_filed_within_30d | 3.5% |
| sector_outperforming_spy | 41.4% |
| sector_underperforming_spy | 58.6% |
| shooting_star | 3.5% |
| sma_20_50_bullish | 48.7% |
| sma_20_50_golden_cross | 0.3% |
| sma_50_200_bullish | 48.4% |
| sma_50_200_golden_cross | 0.3% |
| sma_9_21_bullish | 49.2% |
| sma_9_21_golden_cross | 0.8% |
| smc_bos_bearish | 15.5% |
| smc_bos_bullish | 14.1% |
| smc_bos_retest_long | 3.7% |
| smc_bos_retest_short | 3.3% |
| smc_breaker_block_bearish | 16.7% |
| smc_breaker_block_bullish | 22.6% |
| smc_choch_bearish | 6.2% |
| smc_choch_bullish | 4.5% |
| smc_equal_highs_swept | 3.5% |
| smc_equal_lows_swept | 3.9% |
| smc_fvg_bearish_active | 35.8% |
| smc_fvg_bullish_active | 35.8% |
| smc_fvg_retest_long_zone | 5.5% |
| smc_fvg_retest_short_zone | 5.5% |
| smc_in_discount_zone | 58.7% |
| smc_in_premium_zone | 54.6% |
| smc_inverse_fvg_bearish | 81.0% |
| smc_inverse_fvg_bullish | 77.7% |
| smc_liquidity_swept_dn | 1.3% |
| smc_liquidity_swept_up | 0.9% |
| smc_mitigation_block_long | 1.2% |
| smc_mitigation_block_short | 1.1% |
| smc_ob_bearish_active | 38.9% |
| smc_ob_bullish_active | 33.0% |
| smc_ote_long_zone | 7.4% |
| smc_ote_short_zone | 6.1% |
| squeeze_fire_dn | 5.8% |
| squeeze_fire_up | 4.7% |
| squeeze_in | 26.5% |
| squeeze_positive | 47.3% |
| stoch_bearish_cross | 11.5% |
| stoch_broad_overbought | 10.5% |
| stoch_broad_oversold | 10.6% |
| stoch_bullish_cross | 9.8% |
| stoch_overbought | 5.7% |
| stoch_oversold | 5.2% |
| stochrsi_cross_dn | 21.4% |
| stochrsi_cross_up | 21.5% |
| stochrsi_overbought | 28.0% |
| stochrsi_oversold | 32.9% |
| supertrend_bearish | 2.6% |
| supertrend_bullish | 97.4% |
| supertrend_flip_dn | 2.3% |
| supertrend_flip_recent_long_5d | 0.7% |
| supertrend_flip_recent_short_5d | 2.7% |
| supertrend_flip_up | 0.1% |
| support_break_retest | 12.2% |
| tema_above_dema | 48.6% |
| tema_cross_dn | 4.2% |
| tema_cross_up | 3.1% |
| three_black_crows | 8.3% |
| three_white_soldiers | 7.3% |
| triangle_apex_break_retest_long | 13.0% |
| triangle_ascending_detected | 5.3% |
| triangle_descending_detected | 4.9% |
| uo_overbought | 0.2% |
| uo_oversold | 0.3% |
| usd_strengthening | 23.2% |
| usd_weakening | 10.6% |
| vix_band_high | 44.5% |
| vix_band_low | 32.2% |
| vix_band_mid | 23.4% |
| vix_term_backwardation | 9.1% |
| vix_term_contango | 90.9% |
| vol_above_avg | 32.7% |
| vol_below_avg | 67.3% |
| vol_spike_12x | 18.7% |
| vol_spike_15x | 9.7% |
| vol_spike_17x | 7.0% |
| vol_spike_2x | 4.3% |
| vol_spike_2x_on_down_day_recent_3d | 2.6% |
| vol_spike_2x_on_up_day_recent_3d | 2.4% |
| vol_spike_3x | 1.8% |
| vp_above_value_area | 25.5% |
| vp_below_value_area | 24.3% |
| vp_close_above_poc | 50.7% |
| vp_close_below_poc | 49.3% |
| vp_in_value_area | 50.3% |
| week_open_gap_down_15pct | 2.0% |
| week_open_gap_up_15pct | 1.2% |
| weekly_above_ema_10 | 48.1% |
| weekly_above_ema_20 | 46.5% |
| weekly_bias_bear | 49.1% |
| weekly_bias_bull | 43.7% |
| weekly_momentum_pos | 46.6% |
| williams_r_overbought | 6.7% |
| williams_r_oversold | 11.1% |
| williams_r_rising | 47.4% |
| within_pead_window | 38.3% |
| within_post_deletion_window | 7.9% |
| within_post_inclusion_window | 1.2% |
| within_pre_rebalance_window | 1.0% |
| xs_avoid_high_ivol | 71.8% |
| xs_avoid_high_max | 72.0% |
| xs_high_beta_decile | 26.4% |
| xs_low_beta_bottom_quintile | 26.4% |
| xs_low_beta_decile | 15.8% |
| xs_low_beta_decile_entry_recent_5d | 0.1% |
| xs_low_beta_top_quintile | 15.8% |
| xs_momentum_bottom_decile | 13.3% |
| xs_momentum_bottom_quintile | 24.9% |
| xs_momentum_top_decile | 11.1% |
| xs_momentum_top_quintile | 20.0% |
| xs_quality_bottom_quintile | 21.8% |
| xs_quality_top_quintile | 21.2% |
| xs_quality_top_tercile | 40.5% |
| year_high_break_retest_long | 4.4% |
| year_low_break_retest_short | 3.0% |
| yoy_surprise_high | 50.5% |
| yoy_surprise_negative | 38.9% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.6% |
| committed_growth_holders | 91.6% |
| corp_donations_1y | 7.5% |
| corp_donations_count_1y | 7.5% |
| corp_donations_unique_pacs | 7.5% |
| cot_rut_commercials_pctile_3y | 53.5% |
| cot_rut_mmoney_pctile_3y | 53.5% |
| cup_handle_depth_pct | 20.0% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 7.9% |
| days_since_inclusion | 14.1% |
| days_to_next_holiday | 63.2% |
| days_to_rebalance | 10.8% |
| dpi_30d_avg | 95.8% |
| dpi_recent | 95.8% |
| earnings_announcement_return | 91.0% |
| earnings_eps_yoy_growth | 94.3% |
| flag_bear_pole_move_pct | 0.8% |
| flag_bull_pole_move_pct | 3.3% |
| gov_contracts_4q_sum | 40.8% |
| gov_contracts_last_qtr_amount | 40.8% |
| gov_contracts_qoq_growth | 40.8% |
| head_shoulders_magnitude_pct | 8.1% |
| insider_director_buyers_30d | 5.7% |
| insider_officer_buyers_30d | 5.7% |
| insider_total_shares_bought_30d | 5.7% |
| insider_unique_buyers_30d | 5.7% |
| inverted_cup_handle_height_pct | 16.2% |
| lobbying_amount_1y | 71.1% |
| lobbying_amount_q | 71.1% |
| lobbying_amount_yoy | 71.1% |
| monthly_momentum_6m | 97.6% |
| otc_short_ratio_recent | 95.8% |
| otc_volume_recent | 95.8% |
| pair_half_life | 92.6% |
| pair_max_abs_zscore | 92.6% |
| pair_zscore_signed | 92.6% |
| pct_from_avwap_20high | 97.4% |
| pct_from_avwap_20low | 95.2% |
| pct_from_avwap_252low | 96.7% |
| pct_from_avwap_50low | 96.7% |
| persistent_holders_4q | 91.6% |
| persistent_holders_8q | 91.6% |
| sc_13g_latest_percent_owned | 1.7% |
| search_volume_index_recent | 77.4% |
| search_volume_observations | 77.4% |
| search_volume_zscore_30d | 77.4% |
| sector_etf_return_20d | 2.4% |
| spy_return_20d | 2.4% |
| total_active_holders | 91.6% |
| triangle_breakdown_pct | 4.9% |
| triangle_breakout_pct | 5.3% |
| xs_quality_decile | 61.4% |
| xs_quality_gross_profitability | 61.4% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (1.0), `avwap_20low` (0.999), `avwap_252low` (0.994), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.997), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.998), `dema` (0.999), `double_bottom_neckline` (0.995), `double_bottom_trough` (0.997), `double_top_neckline` (0.996), `double_top_peak` (0.997), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.996), `fib_382` (0.997), `fib_500` (0.997), `fib_618` (0.998), `fib_786` (0.997), `fib_ext_127` (0.992), `fib_ext_162` (0.989), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.992), `ichi_senkou_b` (0.989), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.983), `monthly_sma_6` (0.994), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.997), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.998), `supertrend_value` (0.997), `swing_high` (0.995), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.995), `vp_value_area_low` (0.995), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.97), `year_low` (0.971)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P3 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     1 = 1
offline gradings   0 level-combinations x 24 exits = 0 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  0 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 0 + 0 = 1 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 653 census axes join it only when REGISTERED at the T3 band review.
