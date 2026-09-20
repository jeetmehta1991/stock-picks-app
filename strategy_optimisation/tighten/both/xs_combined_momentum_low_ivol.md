# Table A - xs_combined_momentum_low_ivol

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:26:39 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** factor | **status:** STALLED-CAMPAIGN | **R5 fires:** 212 | **surviving fires (T1):** 212 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)
P2  xs_momentum_top_quintile  <- backtest/signals/cross_sectional.py +1
       DEFN: cross-sectional 12-1 momentum in the top quintile (factor block)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  xs_ivol_decile <= 4   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_xs_combined_momentum_low_ivol (docstring and return dropped):

```python
fires = s.get('xs_momentum_top_quintile', False) and s.get('xs_ivol_decile', 5) <= 4 and s.get('price_above_ema_200', False)
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
| P2 | PRODUCER | xs_momentum_top_quintile - emitted by backtest/signals/cross_sectional.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | cross-sectional 12-1 momentum in the top quintile (factor block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | quantile cut (quintile) - backtest/signals cross-sectional factor block | BRACKET the cut; the underlying 12-1 momentum and decile keys are persisted | top 20pct | [decile, quintile, tercile] | re-cuts via persisted xs decile/raw keys - OFFLINE | recompute at other formation windows; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | xs_ivol_decile `<= 4` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `<= 4` | production + 3 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | `<= 4` | 100.0% | TIGHTER = LOWER the ceiling: 1 -> 48 (23%); 2 -> 96 (45%); 3 -> 152 (72%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 19.12, 23.342, 26.934, 32.638 | 19.12: 169 (80%); 23.342: 127 (60%); 26.934: 85 (40%); 32.638: 43 (20%) | 19.12: 43 (20%); 23.342: 85 (40%); 26.934: 127 (60%); 32.638: 169 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 19.682, 24.7, 28.93, 32.468 | 19.682: 169 (80%); 24.7: 127 (60%); 28.93: 86 (41%); 32.468: 43 (20%) | 19.682: 43 (20%); 24.7: 85 (40%); 28.93: 128 (60%); 32.468: 169 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 14.226, 16.89, 20.858, 24.828 | 14.226: 169 (80%); 16.89: 128 (60%); 20.858: 85 (40%); 24.828: 43 (20%) | 14.226: 43 (20%); 16.89: 86 (41%); 20.858: 127 (60%); 24.828: 169 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -8.4609, -3.6034, -0.7991, 1.3194 | -8.4609: 169 (80%); -3.6034: 127 (60%); -0.7991: 85 (40%); 1.3194: 43 (20%) | -8.4609: 43 (20%); -3.6034: 85 (40%); -0.7991: 127 (60%); 1.3194: 169 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.5786, 2.3746, 3.5625, 6.32 | 1.5786: 169 (80%); 2.3746: 127 (60%); 3.5625: 85 (40%); 6.32: 43 (20%) | 1.5786: 43 (20%); 2.3746: 85 (40%); 3.5625: 127 (60%); 6.32: 169 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.5786, 2.3746, 3.5625, 6.32 | 1.5786: 169 (80%); 2.3746: 127 (60%); 3.5625: 85 (40%); 6.32: 43 (20%) | 1.5786: 43 (20%); 2.3746: 85 (40%); 3.5625: 127 (60%); 6.32: 169 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.0424, 2.3052, 2.617, 3.0096 | 2.0424: 169 (80%); 2.3052: 127 (60%); 2.617: 85 (40%); 3.0096: 43 (20%) | 2.0424: 43 (20%); 2.3052: 85 (40%); 2.617: 127 (60%); 3.0096: 169 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0533, 0.0742, 0.1018, 0.1351 | 0.0533: 169 (80%); 0.0742: 127 (60%); 0.1018: 85 (40%); 0.1351: 43 (20%) | 0.0533: 43 (20%); 0.0742: 85 (40%); 0.1018: 127 (60%); 0.1351: 169 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.237, 0.3945, 0.6105, 0.8211 | 0.237: 169 (80%); 0.3945: 127 (60%); 0.6105: 85 (40%); 0.8211: 43 (20%) | 0.237: 43 (20%); 0.3945: 85 (40%); 0.6105: 127 (60%); 0.8211: 169 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0539, 0.0782, 0.0942, 0.1213 | 0.0539: 169 (80%); 0.0782: 128 (60%); 0.0942: 85 (40%); 0.1213: 43 (20%) | 0.0539: 43 (20%); 0.0782: 86 (41%); 0.0942: 127 (60%); 0.1213: 169 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.0191, 0.2337, 0.5048, 0.8255 | 0.0191: 169 (80%); 0.2337: 127 (60%); 0.5048: 85 (40%); 0.8255: 43 (20%) | 0.0191: 43 (20%); 0.2337: 85 (40%); 0.5048: 127 (60%); 0.8255: 169 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0719, 0.1042, 0.1256, 0.1617 | 0.0719: 169 (80%); 0.1042: 128 (60%); 0.1256: 85 (40%); 0.1617: 43 (20%) | 0.0719: 43 (20%); 0.1042: 85 (40%); 0.1256: 127 (60%); 0.1617: 169 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.1394, 0.3002, 0.5036, 0.7442 | 0.1394: 169 (80%); 0.3002: 127 (60%); 0.5036: 85 (40%); 0.7442: 43 (20%) | 0.1394: 43 (20%); 0.3002: 85 (40%); 0.5036: 127 (60%); 0.7442: 169 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0329, -0.0042, 0.0142, 0.0463 | -0.0329: 169 (80%); -0.0042: 128 (60%); 0.0142: 85 (40%); 0.0463: 43 (20%) | -0.0329: 43 (20%); -0.0042: 86 (41%); 0.0142: 128 (60%); 0.0463: 170 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1469, 0.162, 0.201, 0.2641 | 0.1469: 171 (81%); 0.162: 122 (58%); 0.201: 85 (40%); 0.2641: 43 (20%) | 0.1469: 41 (19%); 0.162: 90 (42%); 0.201: 127 (60%); 0.2641: 169 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 212 (100%) | 0: 201 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0874, -0.0131, 0.0555, 0.1306 | -0.0874: 169 (80%); -0.0131: 127 (60%); 0.0555: 85 (40%); 0.1306: 43 (20%) | -0.0874: 43 (20%); -0.0131: 85 (40%); 0.0555: 127 (60%); 0.1306: 169 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 212 (100%); 1: 69 (33%) | 0: 143 (67%); 1: 190 (90%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2312, -0.1597, -0.1376, -0.1141 | -0.2312: 170 (80%); -0.1597: 127 (60%); -0.1376: 85 (40%); -0.1141: 61 (29%) | -0.2312: 44 (21%); -0.1597: 85 (40%); -0.1376: 127 (60%); -0.1141: 183 (86%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5513, 0.6667, 0.7308, 0.7692 | 0.5513: 170 (80%); 0.6667: 128 (60%); 0.7308: 86 (41%); 0.7692: 70 (33%) | 0.5513: 44 (21%); 0.6667: 96 (45%); 0.7308: 128 (60%); 0.7692: 180 (85%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4321, 0.5897, 0.7936 | 0.2692: 173 (82%); 0.4321: 127 (60%); 0.5897: 108 (51%); 0.7936: 43 (20%) | 0.2692: 45 (21%); 0.4321: 85 (40%); 0.5897: 136 (64%); 0.7936: 169 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0462, 0.0136, 0.0357, 0.2414 | -0.0462: 170 (80%); 0.0136: 129 (61%); 0.0357: 86 (41%); 0.2414: 43 (20%) | -0.0462: 50 (24%); 0.0136: 86 (41%); 0.0357: 129 (61%); 0.2414: 169 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3846, 0.4872, 0.5385, 0.809 | 0.3846: 174 (82%); 0.4872: 132 (62%); 0.5385: 91 (43%); 0.809: 43 (20%) | 0.3846: 44 (21%); 0.4872: 113 (53%); 0.5385: 128 (60%); 0.809: 169 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2372, 0.3603, 0.4551, 0.5884 | 0.2372: 172 (81%); 0.3603: 127 (60%); 0.4551: 104 (49%); 0.5884: 43 (20%) | 0.2372: 45 (21%); 0.3603: 85 (40%); 0.4551: 145 (68%); 0.5884: 169 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.521, -0.3469, -0.0978, -0.023 | -0.521: 172 (81%); -0.3469: 127 (60%); -0.0978: 91 (43%); -0.023: 43 (20%) | -0.521: 45 (21%); -0.3469: 85 (40%); -0.0978: 131 (62%); -0.023: 169 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3077, 0.4936, 0.8205, 0.8269 | 0.3077: 170 (80%); 0.4936: 132 (62%); 0.8205: 86 (41%); 0.8269: 44 (21%) | 0.3077: 45 (21%); 0.4936: 87 (41%); 0.8205: 168 (79%); 0.8269: 173 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.4487, 0.7167, 0.8526 | 0.2628: 172 (81%); 0.4487: 130 (61%); 0.7167: 85 (40%); 0.8526: 67 (32%) | 0.2628: 46 (22%); 0.4487: 86 (41%); 0.7167: 127 (60%); 0.8526: 177 (83%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0643, -0.0448, 0 | -0.0643: 169 (80%); -0.0448: 127 (60%); 0: 100 (47%) | -0.0643: 43 (20%); -0.0448: 85 (40%); 0: 207 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4834, 0.8654, 1 | 0.4834: 169 (80%); 0.8654: 130 (61%); 1: 88 (42%) | 0.4834: 43 (20%); 0.8654: 89 (42%); 1: 212 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.2308, 0.3205, 0.75 | 0.109: 171 (81%); 0.2308: 128 (60%); 0.3205: 111 (52%); 0.75: 44 (21%) | 0.109: 46 (22%); 0.2308: 86 (41%); 0.3205: 135 (64%); 0.75: 170 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0182, 0.0428, 0.1408, 0.2489 | 0.0182: 170 (80%); 0.0428: 127 (60%); 0.1408: 85 (40%); 0.2489: 62 (29%) | 0.0182: 45 (21%); 0.0428: 85 (40%); 0.1408: 127 (60%); 0.2489: 182 (86%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.6449, 0.8764, 0.9615, 0.9744 | 0.6449: 169 (80%); 0.8764: 128 (60%); 0.9615: 88 (42%); 0.9744: 70 (33%) | 0.6449: 43 (20%); 0.8764: 86 (41%); 0.9615: 138 (65%); 0.9744: 180 (85%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0948, 0.2949, 0.4154, 0.7686 | 0.0948: 169 (80%); 0.2949: 130 (61%); 0.4154: 85 (40%); 0.7686: 43 (20%) | 0.0948: 43 (20%); 0.2949: 114 (54%); 0.4154: 127 (60%); 0.7686: 169 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3493, -0.0003, 0.1225, 0.1876 | -0.3493: 196 (92%); -0.0003: 129 (61%); 0.1225: 86 (41%); 0.1876: 46 (22%) | -0.3493: 48 (23%); -0.0003: 86 (41%); 0.1225: 142 (67%); 0.1876: 175 (83%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3459, -0.0412, 0.0292, 0.0968 | -0.3459: 198 (93%); -0.0412: 127 (60%); 0.0292: 85 (40%); 0.0968: 44 (21%) | -0.3459: 46 (22%); -0.0412: 85 (40%); 0.0292: 127 (60%); 0.0968: 170 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5321, 0.7372, 0.8833 | 0.2628: 182 (86%); 0.5321: 128 (60%); 0.7372: 88 (42%); 0.8833: 43 (20%) | 0.2628: 62 (29%); 0.5321: 88 (42%); 0.7372: 134 (63%); 0.8833: 169 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.3872, 0.5641, 0.75 | 0.1538: 169 (80%); 0.3872: 127 (60%); 0.5641: 104 (49%); 0.75: 44 (21%) | 0.1538: 43 (20%); 0.3872: 85 (40%); 0.5641: 142 (67%); 0.75: 170 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0724, 0.176, 0.352, 0.723 | 0.0724: 169 (80%); 0.176: 127 (60%); 0.352: 85 (40%); 0.723: 43 (20%) | 0.0724: 43 (20%); 0.176: 85 (40%); 0.352: 127 (60%); 0.723: 169 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.1% | 26, 66.6, 117, 159.6 | 26: 168 (79%); 66.6: 125 (59%); 117: 83 (39%); 159.6: 42 (20%) | 26: 43 (20%); 66.6: 83 (39%); 117: 125 (59%); 159.6: 166 (78%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.1% | 1.92, 2.3049, 2.8129, 3.6166 | 1.92: 168 (79%); 2.3049: 126 (59%); 2.8129: 84 (40%); 3.6166: 42 (20%) | 1.92: 42 (20%); 2.3049: 84 (40%); 2.8129: 126 (59%); 3.6166: 168 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 12, 23, 28, 34 | 12: 176 (83%); 23: 129 (61%); 28: 101 (48%); 34: 44 (21%) | 12: 44 (21%); 23: 89 (42%); 28: 143 (67%); 34: 176 (83%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 173 (82%); 2: 133 (63%); 3: 75 (35%) | 1: 79 (37%); 2: 137 (65%); 3: 172 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0193, -0.002, 0.0036, 0.0199 | -0.0193: 170 (80%); -0.002: 127 (60%); 0.0036: 85 (40%); 0.0199: 45 (21%) | -0.0193: 44 (21%); -0.002: 85 (40%); 0.0036: 127 (60%); 0.0199: 170 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5714, 26.0848, 26.7852, 27.4428 | 24.5714: 169 (80%); 26.0848: 127 (60%); 26.7852: 88 (42%); 27.4428: 47 (22%) | 24.5714: 43 (20%); 26.0848: 85 (40%); 26.7852: 128 (60%); 27.4428: 174 (82%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.522, -0.0624, 0.3624, 0.948 | -0.522: 169 (80%); -0.0624: 127 (60%); 0.3624: 85 (40%); 0.948: 43 (20%) | -0.522: 43 (20%); -0.0624: 85 (40%); 0.3624: 127 (60%); 0.948: 169 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.948, -0.3624, 0.0624, 0.522 | -0.948: 169 (80%); -0.3624: 127 (60%); 0.0624: 85 (40%); 0.522: 43 (20%) | -0.948: 43 (20%); -0.3624: 85 (40%); 0.0624: 127 (60%); 0.522: 169 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0258, 0.0125, 0.0608, 0.1162 | -0.0258: 169 (80%); 0.0125: 128 (60%); 0.0608: 85 (40%); 0.1162: 43 (20%) | -0.0258: 43 (20%); 0.0125: 86 (41%); 0.0608: 127 (60%); 0.1162: 169 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.3282, 8.6677, 9.031, 10.0851 | 8.3282: 169 (80%); 8.6677: 127 (60%); 9.031: 85 (40%); 10.0851: 46 (22%) | 8.3282: 43 (20%); 8.6677: 85 (40%); 9.031: 127 (60%); 10.0851: 166 (78%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 210 (99%); 1: 65 (31%) | 0: 145 (68%); 1: 182 (86%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0 | 0: 174 (82%) | 0: 170 (80%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 210 (99%); 1: 70 (33%) | 0: 140 (66%); 1: 187 (88%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 1, 4, 9.6, 270 | 1: 181 (85%); 4: 129 (61%); 9.6: 85 (40%); 270: 43 (20%) | 1: 44 (21%); 4: 100 (47%); 9.6: 127 (60%); 270: 169 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 2, 83.6, 142 | 0: 212 (100%); 2: 134 (63%); 83.6: 85 (40%); 142: 43 (20%) | 0: 55 (26%); 2: 95 (45%); 83.6: 127 (60%); 142: 169 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.0545, -0.4826, -0.123, 0.3542 | -1.0545: 169 (80%); -0.4826: 127 (60%); -0.123: 85 (40%); 0.3542: 43 (20%) | -1.0545: 43 (20%); -0.4826: 85 (40%); -0.123: 127 (60%); 0.3542: 169 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.9556, -1.0042, -0.2377, 0.7012 | -2.9556: 169 (80%); -1.0042: 127 (60%); -0.2377: 85 (40%); 0.7012: 43 (20%) | -2.9556: 43 (20%); -1.0042: 85 (40%); -0.2377: 127 (60%); 0.7012: 169 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.2575, -0.5574, 0.1009, 0.8689 | -2.2575: 169 (80%); -0.5574: 127 (60%); 0.1009: 85 (40%); 0.8689: 43 (20%) | -2.2575: 43 (20%); -0.5574: 85 (40%); 0.1009: 127 (60%); 0.8689: 169 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.6864, -0.2337, 0.0596, 0.4386 | -0.6864: 170 (80%); -0.2337: 127 (60%); 0.0596: 85 (40%); 0.4386: 43 (20%) | -0.6864: 43 (20%); -0.2337: 85 (40%); 0.0596: 127 (60%); 0.4386: 169 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -3.0669, -1.1468, -0.3667, 0.6538 | -3.0669: 169 (80%); -1.1468: 127 (60%); -0.3667: 85 (40%); 0.6538: 43 (20%) | -3.0669: 43 (20%); -1.1468: 85 (40%); -0.3667: 127 (60%); 0.6538: 169 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -3.4269, -1.0959, -0.2878, 0.757 | -3.4269: 169 (80%); -1.0959: 127 (60%); -0.2878: 85 (40%); 0.757: 43 (20%) | -3.4269: 43 (20%); -1.0959: 85 (40%); -0.2878: 127 (60%); 0.757: 169 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 36.462, 44.974, 52.734, 61.856 | 36.462: 169 (80%); 44.974: 127 (60%); 52.734: 85 (40%); 61.856: 43 (20%) | 36.462: 43 (20%); 44.974: 85 (40%); 52.734: 127 (60%); 61.856: 169 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.006, 0.0146, 0.0231, 0.0375 | 0.006: 169 (80%); 0.0146: 127 (60%); 0.0231: 85 (40%); 0.0375: 43 (20%) | 0.006: 43 (20%); 0.0146: 85 (40%); 0.0231: 127 (60%); 0.0375: 169 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 9 | 0: 212 (100%); 1: 157 (74%); 3: 101 (48%); 9: 45 (21%) | 0: 55 (26%); 1: 92 (43%); 3: 131 (62%); 9: 180 (85%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1111 | 0: 212 (100%); 0.1111: 46 (22%) | 0: 155 (73%); 0.1111: 175 (83%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.4286, 0.7106 | 0: 212 (100%); 0.2: 130 (61%); 0.4286: 86 (41%); 0.7106: 43 (20%) | 0: 78 (37%); 0.2: 86 (41%); 0.4286: 128 (60%); 0.7106: 169 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 6 | 0: 212 (100%); 1: 146 (69%); 2: 106 (50%); 6: 46 (22%) | 0: 66 (31%); 1: 106 (50%); 2: 130 (61%); 6: 172 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 9 | 0: 212 (100%); 1: 157 (74%); 3: 101 (48%); 9: 45 (21%) | 0: 55 (26%); 1: 92 (43%); 3: 131 (62%); 9: 180 (85%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 212 (100%); 1: 137 (65%); 3: 93 (44%); 7: 48 (23%) | 0: 75 (35%); 1: 98 (46%); 3: 137 (65%); 7: 174 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3035, 0.4256, 0.6623 | 0: 208 (98%); 0.3035: 127 (60%); 0.4256: 85 (40%); 0.6623: 43 (20%) | 0: 44 (21%); 0.3035: 85 (40%); 0.4256: 127 (60%); 0.6623: 169 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1925, 0.665 | 0: 197 (93%); 0.1925: 85 (40%); 0.665: 43 (20%) | 0: 113 (53%); 0.1925: 127 (60%); 0.665: 169 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3046, 0.64 | 0: 203 (96%); 0.3046: 85 (40%); 0.64: 43 (20%) | 0: 86 (41%); 0.3046: 127 (60%); 0.64: 169 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3046, 0.64 | 0: 203 (96%); 0.3046: 85 (40%); 0.64: 43 (20%) | 0: 86 (41%); 0.3046: 127 (60%); 0.64: 169 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1316, 0, 0.0398 | -0.1316: 169 (80%); 0: 154 (73%); 0.0398: 43 (20%) | -0.1316: 43 (20%); 0: 163 (77%); 0.0398: 169 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6494, -0.2128, 0, 1.2929 | -0.6494: 169 (80%); -0.2128: 127 (60%); 0: 121 (57%); 1.2929: 43 (20%) | -0.6494: 43 (20%); -0.2128: 85 (40%); 0: 135 (64%); 1.2929: 169 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 3, 5, 9, 13 | 3: 171 (81%); 5: 141 (67%); 9: 89 (42%); 13: 45 (21%) | 3: 64 (30%); 5: 97 (46%); 9: 141 (67%); 13: 176 (83%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0523, -0.025, 0.003, 0.0313 | -0.0523: 169 (80%); -0.025: 127 (60%); 0.003: 84 (40%); 0.0313: 43 (20%) | -0.0523: 43 (20%); -0.025: 85 (40%); 0.003: 128 (60%); 0.0313: 169 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0678, -0.038, -0.012, 0.0395 | -0.0678: 169 (80%); -0.038: 127 (60%); -0.012: 85 (40%); 0.0395: 43 (20%) | -0.0678: 43 (20%); -0.038: 85 (40%); -0.012: 127 (60%); 0.0395: 169 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0403, -0.0164, 0.0072, 0.0311 | -0.0403: 168 (79%); -0.0164: 127 (60%); 0.0072: 85 (40%); 0.0311: 43 (20%) | -0.0403: 44 (21%); -0.0164: 85 (40%); 0.0072: 127 (60%); 0.0311: 169 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 98.6% | 3.4488, 6.1662, 9.0086, 13.6416 | 3.4488: 167 (79%); 6.1662: 125 (59%); 9.0086: 84 (40%); 13.6416: 42 (20%) | 3.4488: 42 (20%); 6.1662: 84 (40%); 9.0086: 125 (59%); 13.6416: 167 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | 6.4846, 14.3118, 28.607, 47.9266 | 6.4846: 169 (80%); 14.3118: 127 (60%); 28.607: 85 (40%); 47.9266: 43 (20%) | 6.4846: 43 (20%); 14.3118: 85 (40%); 28.607: 127 (60%); 47.9266: 169 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0413, 0.0548, 0.0725, 0.0986 | 0.0413: 169 (80%); 0.0548: 129 (61%); 0.0725: 86 (41%); 0.0986: 43 (20%) | 0.0413: 43 (20%); 0.0548: 85 (40%); 0.0725: 128 (60%); 0.0986: 170 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5864, 0.7232, 0.8205, 0.9157 | 0.5864: 169 (80%); 0.7232: 127 (60%); 0.8205: 85 (40%); 0.9157: 43 (20%) | 0.5864: 43 (20%); 0.7232: 85 (40%); 0.8205: 127 (60%); 0.9157: 169 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.7351, -0.9218, -0.3113, 0.8257 | -1.7351: 169 (80%); -0.9218: 127 (60%); -0.3113: 85 (40%); 0.8257: 43 (20%) | -1.7351: 43 (20%); -0.9218: 85 (40%); -0.3113: 127 (60%); 0.8257: 169 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.736, -0.4505, -0.1602, 0.3737 | -0.736: 169 (80%); -0.4505: 127 (60%); -0.1602: 85 (40%); 0.3737: 43 (20%) | -0.736: 43 (20%); -0.4505: 85 (40%); -0.1602: 127 (60%); 0.3737: 169 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.5535, -0.635, 0.1055, 0.9176 | -1.5535: 169 (80%); -0.635: 127 (60%); 0.1055: 85 (40%); 0.9176: 43 (20%) | -1.5535: 43 (20%); -0.635: 85 (40%); 0.1055: 127 (60%); 0.9176: 169 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -5.925, -2.8296, 0.08, 3.4772 | -5.925: 169 (80%); -2.8296: 127 (60%); 0.08: 85 (40%); 3.4772: 43 (20%) | -5.925: 43 (20%); -2.8296: 85 (40%); 0.08: 127 (60%); 3.4772: 169 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 38.772, 44.74, 49.316, 57.81 | 38.772: 169 (80%); 44.74: 128 (60%); 49.316: 85 (40%); 57.81: 43 (20%) | 38.772: 43 (20%); 44.74: 86 (41%); 49.316: 127 (60%); 57.81: 169 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 32.48, 58.546, 74.682, 88.634 | 32.48: 169 (80%); 58.546: 127 (60%); 74.682: 85 (40%); 88.634: 43 (20%) | 32.48: 43 (20%); 58.546: 85 (40%); 74.682: 127 (60%); 88.634: 169 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 42.384, 46.516, 49.522, 55.78 | 42.384: 169 (80%); 46.516: 127 (60%); 49.522: 85 (40%); 55.78: 43 (20%) | 42.384: 43 (20%); 46.516: 85 (40%); 49.522: 127 (60%); 55.78: 169 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 36.126, 44.04, 51.794, 61.086 | 36.126: 169 (80%); 44.04: 127 (60%); 51.794: 85 (40%); 61.086: 43 (20%) | 36.126: 43 (20%); 44.04: 85 (40%); 51.794: 127 (60%); 61.086: 169 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0293, 0.0489, 0.0653, 0.0927 | 0.0293: 169 (80%); 0.0489: 130 (61%); 0.0653: 85 (40%); 0.0927: 43 (20%) | 0.0293: 43 (20%); 0.0489: 86 (41%); 0.0653: 127 (60%); 0.0927: 169 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0839, -0.0597, -0.0434, -0.0348 | -0.0839: 170 (80%); -0.0597: 127 (60%); -0.0434: 88 (42%); -0.0348: 44 (21%) | -0.0839: 44 (21%); -0.0597: 85 (40%); -0.0434: 147 (69%); -0.0348: 170 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 212 (100%); 2: 50 (24%) | 0: 140 (66%); 2: 172 (81%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.1% | 26, 45, 64.4, 66 | 26: 169 (80%); 45: 127 (60%); 64.4: 84 (40%); 66: 43 (20%) | 26: 48 (23%); 45: 87 (41%); 64.4: 126 (59%); 66: 174 (82%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 99.1% | 0.0097, 0.0134, 0.0176, 0.0258 | 0.0097: 168 (79%); 0.0134: 126 (59%); 0.0176: 84 (40%); 0.0258: 42 (20%) | 0.0097: 42 (20%); 0.0134: 84 (40%); 0.0176: 126 (59%); 0.0258: 168 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.2585, 0.393, 0.4991, 0.7305 | 0.2585: 169 (80%); 0.393: 128 (60%); 0.4991: 85 (40%); 0.7305: 43 (20%) | 0.2585: 43 (20%); 0.393: 86 (41%); 0.4991: 127 (60%); 0.7305: 169 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 41.56, 60.68, 85.14, 121.4 | 41.56: 169 (80%); 60.68: 127 (60%); 85.14: 85 (40%); 121.4: 43 (20%) | 41.56: 43 (20%); 60.68: 85 (40%); 85.14: 127 (60%); 121.4: 169 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -4.357, -1.4518, 0.2515, 3.1529 | -4.357: 169 (80%); -1.4518: 127 (60%); 0.2515: 85 (40%); 3.1529: 43 (20%) | -4.357: 43 (20%); -1.4518: 85 (40%); 0.2515: 127 (60%); 3.1529: 169 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 18.326, 29.424, 48.322, 70.504 | 18.326: 169 (80%); 29.424: 127 (60%); 48.322: 85 (40%); 70.504: 43 (20%) | 18.326: 43 (20%); 29.424: 85 (40%); 48.322: 127 (60%); 70.504: 169 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 18.732, 33.194, 50.06, 76.088 | 18.732: 169 (80%); 33.194: 127 (60%); 50.06: 85 (40%); 76.088: 43 (20%) | 18.732: 43 (20%); 33.194: 85 (40%); 50.06: 127 (60%); 76.088: 169 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 9.888, 23.756, 50.022, 83.242 | 9.888: 169 (80%); 23.756: 127 (60%); 50.022: 85 (40%); 83.242: 43 (20%) | 9.888: 43 (20%); 23.756: 85 (40%); 50.022: 127 (60%); 83.242: 169 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 12.016, 32.316, 61.074, 95.768 | 12.016: 169 (80%); 32.316: 127 (60%); 61.074: 85 (40%); 95.768: 43 (20%) | 12.016: 43 (20%); 32.316: 85 (40%); 61.074: 127 (60%); 95.768: 169 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 7, 10, 15.8 | 5: 170 (80%); 7: 144 (68%); 10: 99 (47%); 15.8: 43 (20%) | 5: 60 (28%); 7: 98 (46%); 10: 129 (61%); 15.8: 169 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 6, 12, 15, 17 | 6: 174 (82%); 12: 129 (61%); 15: 96 (45%); 17: 62 (29%) | 6: 47 (22%); 12: 97 (46%); 15: 142 (67%); 17: 173 (82%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 41.956, 47.932, 52.184, 57.978 | 41.956: 169 (80%); 47.932: 127 (60%); 52.184: 85 (40%); 57.978: 43 (20%) | 41.956: 43 (20%); 47.932: 85 (40%); 52.184: 127 (60%); 57.978: 169 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2445, 0.6659, 0.873, 0.9722 | 0.2445: 169 (80%); 0.6659: 127 (60%); 0.873: 88 (42%); 0.9722: 45 (21%) | 0.2445: 43 (20%); 0.6659: 85 (40%); 0.873: 133 (63%); 0.9722: 170 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.95, 21.138, 25.5, 30.76 | 16.95: 170 (80%); 21.138: 127 (60%); 25.5: 86 (41%); 30.76: 44 (21%) | 16.95: 44 (21%); 21.138: 85 (40%); 25.5: 131 (62%); 30.76: 170 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 16.95, 21.138, 25.5, 30.76 | 16.95: 170 (80%); 21.138: 127 (60%); 25.5: 86 (41%); 30.76: 44 (21%) | 16.95: 44 (21%); 21.138: 85 (40%); 25.5: 131 (62%); 30.76: 170 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.871, 0.9262, 0.966, 1.0416 | 0.871: 169 (80%); 0.9262: 128 (60%); 0.966: 85 (40%); 1.0416: 43 (20%) | 0.871: 43 (20%); 0.9262: 86 (41%); 0.966: 127 (60%); 1.0416: 169 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.73, 0.894, 1.116, 1.428 | 0.73: 174 (82%); 0.894: 127 (60%); 1.116: 85 (40%); 1.428: 43 (20%) | 0.73: 44 (21%); 0.894: 85 (40%); 1.116: 127 (60%); 1.428: 169 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0132, 0.0329, 0.0519, 0.0791 | 0.0132: 169 (80%); 0.0329: 128 (60%); 0.0519: 85 (40%); 0.0791: 43 (20%) | 0.0132: 43 (20%); 0.0329: 85 (40%); 0.0519: 127 (60%); 0.0791: 169 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 212 (100%) | 0: 182 (86%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 212 (100%) | 0: 200 (94%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0635, -0.0334, -0.0122, 0.0311 | -0.0635: 169 (80%); -0.0334: 128 (60%); -0.0122: 85 (40%); 0.0311: 43 (20%) | -0.0635: 43 (20%); -0.0334: 85 (40%); -0.0122: 127 (60%); 0.0311: 169 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -73.576, -59.042, -42.872, -19.788 | -73.576: 169 (80%); -59.042: 127 (60%); -42.872: 85 (40%); -19.788: 43 (20%) | -73.576: 43 (20%); -59.042: 85 (40%); -42.872: 127 (60%); -19.788: 169 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.3265, 0.5783, 0.8347, 1.0769 | 0.3265: 169 (80%); 0.5783: 127 (60%); 0.8347: 85 (40%); 1.0769: 43 (20%) | 0.3265: 43 (20%); 0.5783: 85 (40%); 0.8347: 127 (60%); 1.0769: 169 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 3, 5.6, 8 | 2: 175 (83%); 3: 138 (65%); 5.6: 85 (40%); 8: 45 (21%) | 2: 74 (35%); 3: 90 (42%); 5.6: 127 (60%); 8: 183 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.1703, 0.1844, 0.202, 0.2186 | 0.1703: 169 (80%); 0.1844: 128 (60%); 0.202: 85 (40%); 0.2186: 43 (20%) | 0.1703: 43 (20%); 0.1844: 85 (40%); 0.202: 127 (60%); 0.2186: 169 (80%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0203, 0.0244, 0.0309, 0.0406 | 0.0203: 171 (81%); 0.0244: 128 (60%); 0.0309: 85 (40%); 0.0406: 43 (20%) | 0.0203: 43 (20%); 0.0244: 85 (40%); 0.0309: 130 (61%); 0.0406: 169 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 1, 2, 4, 6 | 1: 212 (100%); 2: 165 (78%); 4: 98 (46%); 6: 52 (25%) | 1: 47 (22%); 2: 92 (43%); 4: 138 (65%); 6: 176 (83%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | 0.1883, 0.2559, 0.3399, 0.4825 | 0.1883: 169 (80%); 0.2559: 127 (60%); 0.3399: 85 (40%); 0.4825: 43 (20%) | 0.1883: 43 (20%); 0.2559: 85 (40%); 0.3399: 127 (60%); 0.4825: 169 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 9, 10 | 9: 212 (100%); 10: 76 (36%) | 9: 136 (64%); 10: 212 (100%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.7% |
| 8k_item_5_02_filed_within_7d | 2.8% |
| above_avwap_20high | 42.9% |
| above_avwap_20low | 91.5% |
| above_avwap_252low | 98.1% |
| above_avwap_50low | 75.9% |
| above_cam_r3 | 54.7% |
| above_cam_r4 | 30.7% |
| above_cpr | 75.5% |
| above_pivot | 79.2% |
| above_prev_high | 35.8% |
| above_prev_high_clearance_atr_05 | 12.7% |
| above_prev_low | 93.4% |
| above_r1 | 34.9% |
| above_r2 | 13.2% |
| above_vwap | 98.6% |
| above_wood_p | 67.5% |
| ad_rising | 58.0% |
| adx_cross_up | 2.4% |
| adx_cross_up_20 | 2.8% |
| adx_di_bear | 69.8% |
| adx_di_bull | 30.2% |
| adx_strong | 4.7% |
| adx_trending | 50.0% |
| ao_cross_dn | 5.2% |
| ao_cross_up | 0.9% |
| ao_positive | 27.8% |
| ao_twin_peaks_bull | 7.1% |
| at_key_fib | 26.9% |
| at_key_fib_wide | 52.4% |
| avwap_20high_loss_recent_3d | 9.7% |
| avwap_20high_reclaim_recent_3d | 30.1% |
| avwap_20low_loss_recent_3d | 5.4% |
| avwap_20low_reclaim_recent_3d | 38.1% |
| avwap_252low_loss_recent_3d | 1.0% |
| avwap_252low_reclaim_recent_3d | 12.9% |
| avwap_50low_loss_recent_3d | 11.7% |
| avwap_50low_reclaim_recent_3d | 28.2% |
| bb_10_20_above_mid | 50.0% |
| bb_10_20_expanding | 56.1% |
| bb_10_20_pctb_gt_75 | 27.4% |
| bb_10_20_pctb_gt_8 | 21.7% |
| bb_10_20_pctb_gt_85 | 17.9% |
| bb_10_20_pctb_gt_9 | 10.4% |
| bb_10_20_pctb_gt_95 | 7.5% |
| bb_10_20_pctb_lt_05 | 2.8% |
| bb_10_20_pctb_lt_1 | 6.6% |
| bb_10_20_pctb_lt_15 | 13.2% |
| bb_10_20_pctb_lt_2 | 15.1% |
| bb_10_20_pctb_lt_25 | 22.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 18.4% |
| bb_10_20_reclaim_from_upper_recent_3d | 4.2% |
| bb_10_20_squeeze | 46.7% |
| bb_10_20_touch_lower | 3.8% |
| bb_10_20_touch_upper | 9.4% |
| bb_20_15_above_mid | 40.1% |
| bb_20_15_expanding | 54.2% |
| bb_20_15_pctb_gt_75 | 25.9% |
| bb_20_15_pctb_gt_8 | 23.1% |
| bb_20_15_pctb_gt_85 | 18.4% |
| bb_20_15_pctb_gt_9 | 16.5% |
| bb_20_15_pctb_gt_95 | 12.7% |
| bb_20_15_pctb_lt_05 | 22.6% |
| bb_20_15_pctb_lt_1 | 25.5% |
| bb_20_15_pctb_lt_15 | 29.7% |
| bb_20_15_pctb_lt_2 | 35.8% |
| bb_20_15_pctb_lt_25 | 41.5% |
| bb_20_15_reclaim_from_lower_recent_3d | 28.8% |
| bb_20_15_reclaim_from_upper_recent_3d | 4.2% |
| bb_20_15_squeeze | 43.9% |
| bb_20_15_touch_lower | 23.6% |
| bb_20_15_touch_upper | 13.2% |
| bb_20_20_above_mid | 40.1% |
| bb_20_20_expanding | 54.2% |
| bb_20_20_pctb_gt_75 | 19.8% |
| bb_20_20_pctb_gt_8 | 16.5% |
| bb_20_20_pctb_gt_85 | 11.8% |
| bb_20_20_pctb_gt_9 | 9.0% |
| bb_20_20_pctb_gt_95 | 5.7% |
| bb_20_20_pctb_lt_05 | 11.8% |
| bb_20_20_pctb_lt_1 | 15.1% |
| bb_20_20_pctb_lt_15 | 21.7% |
| bb_20_20_pctb_lt_2 | 25.5% |
| bb_20_20_pctb_lt_25 | 31.1% |
| bb_20_20_reclaim_from_lower_recent_3d | 24.5% |
| bb_20_20_reclaim_from_upper_recent_3d | 2.4% |
| bb_20_20_squeeze | 26.9% |
| bb_20_20_touch_lower | 10.4% |
| bb_20_20_touch_upper | 6.1% |
| bearish_pin_bar | 5.7% |
| below_avwap_20high | 57.1% |
| below_avwap_20low | 8.5% |
| below_avwap_252low | 1.9% |
| below_avwap_50low | 24.1% |
| below_cam_s3 | 4.7% |
| below_cam_s4 | 1.9% |
| below_cpr | 20.8% |
| below_ema_20 | 59.9% |
| below_ema_20_break_recent_5d | 25.5% |
| below_ema_21 | 59.9% |
| below_ema_21_break_recent_5d | 25.5% |
| below_ema_50 | 62.3% |
| below_ema_50_break_recent_5d | 26.4% |
| below_ema_9 | 49.5% |
| below_ema_9_break_recent_5d | 26.4% |
| below_prev_high | 64.2% |
| below_prev_low | 6.1% |
| below_prev_low_clearance_atr_05 | 1.4% |
| below_s1 | 2.8% |
| below_s2 | 0.9% |
| below_sma_20 | 59.9% |
| below_sma_200 | 7.5% |
| below_sma_21 | 59.9% |
| below_sma_50 | 65.1% |
| below_sma_9 | 49.5% |
| below_vwap | 1.4% |
| break_52w_high | 0.5% |
| bullish_engulfing | 12.3% |
| bullish_pin_bar | 4.7% |
| capitulation_recent_3d | 0.5% |
| ceo_buy | 1.5% |
| cfo_buy | 0.5% |
| chandelier_long_bullish | 52.4% |
| chandelier_long_flip_dn | 0.9% |
| chandelier_short_bearish | 66.0% |
| chandelier_short_flip_up | 9.0% |
| close_in_bottom_40pct_of_range | 8.0% |
| close_in_top_40pct_of_range | 77.8% |
| cluster_buy | 0.5% |
| cmf_cross_dn | 1.4% |
| cmf_cross_up | 10.4% |
| cmf_negative | 43.4% |
| cmf_positive | 56.6% |
| concentrated_sell | 6.3% |
| cpr_narrow | 92.0% |
| cpr_narrow_tight | 25.5% |
| cup_handle_detected | 21.7% |
| cup_handle_neckline_break_retest_long | 6.6% |
| dc10_breakout_dn | 6.1% |
| dc10_breakout_dn_1pct | 10.4% |
| dc10_breakout_up | 12.3% |
| dc10_breakout_up_1pct | 20.8% |
| dc10_new_high | 15.1% |
| dc10_strong_breakout_dn | 1.4% |
| dc10_strong_breakout_up | 4.2% |
| dc20_breakout_dn | 6.1% |
| dc20_breakout_up | 6.1% |
| dc20_new_high | 6.6% |
| dc20_resistance_break_retest_strong | 9.9% |
| dc20_support_break_retest_strong | 24.5% |
| defensive_leadership | 66.0% |
| director_only_buy | 3.9% |
| doji | 6.1% |
| double_bottom_detected | 15.6% |
| double_top_detected | 24.1% |
| dpi_elevated | 49.8% |
| drying_volume_on_up_turn | 52.8% |
| ema_20_50_bearish | 45.3% |
| ema_20_50_bullish | 54.7% |
| ema_20_50_death_cross | 2.8% |
| ema_20_50_golden_cross | 1.4% |
| ema_50_200_bearish | 4.2% |
| ema_50_200_bullish | 95.8% |
| ema_9_21_bearish | 72.2% |
| ema_9_21_bullish | 27.8% |
| ema_9_21_death_cross | 2.4% |
| ema_9_21_golden_cross | 1.9% |
| flag_bear_break_retest_short | 0.5% |
| flag_bear_broke | 0.5% |
| flag_bull_break_retest_long | 1.9% |
| flag_bull_broke | 2.4% |
| flag_bull_detected | 2.8% |
| force_index_cross_dn | 0.5% |
| force_index_cross_up | 11.8% |
| force_index_positive | 44.3% |
| gap_dn_1_5pct | 11.3% |
| gap_dn_2pct | 8.0% |
| gap_up_1_5pct | 3.3% |
| gap_up_2pct | 1.9% |
| hammer | 3.3% |
| head_shoulders_bottom_detected | 3.8% |
| head_shoulders_top_detected | 4.7% |
| house_cluster_buy | 5.7% |
| house_cluster_sell | 3.8% |
| htf_aligned_bear | 1.4% |
| htf_aligned_bull | 32.1% |
| htf_disagreement | 4.2% |
| hull_bearish | 58.0% |
| hull_bullish | 42.0% |
| hull_flip_dn | 3.3% |
| hull_flip_up | 9.9% |
| ichi_above_cloud | 35.4% |
| ichi_above_cloud_break_recent_5d | 11.3% |
| ichi_below_cloud | 43.4% |
| ichi_below_cloud_break_recent_5d | 13.7% |
| ichi_cloud_thick | 88.2% |
| ichi_tk_bearish | 58.0% |
| ichi_tk_bullish | 26.4% |
| ichi_tk_cross_dn | 2.4% |
| ichi_tk_cross_up | 2.4% |
| ichi_weekly_above_cloud | 82.0% |
| ichi_weekly_in_cloud | 18.0% |
| inside_bar | 17.0% |
| inside_cpr | 4.2% |
| inside_kc | 85.8% |
| insider_cluster_active | 9.1% |
| institutional_buy | 83.5% |
| institutional_negative | 5.2% |
| institutional_persistence_growing | 34.8% |
| institutional_persistence_strong | 54.5% |
| institutional_strong_buy | 72.2% |
| inverted_cup_handle_detected | 17.9% |
| is_friday | 18.9% |
| is_halloween_period | 63.2% |
| is_halloween_period_first_day | 0.5% |
| is_january | 6.6% |
| is_january_extended | 9.4% |
| is_monday | 18.4% |
| is_pre_holiday | 4.7% |
| is_summer_period | 36.8% |
| is_totm_window | 31.1% |
| is_totm_window_first_day | 9.0% |
| is_week_open | 19.8% |
| kc_touch_lower | 10.4% |
| kc_touch_upper | 6.1% |
| macd_12_26_9_bearish | 66.0% |
| macd_12_26_9_bullish | 34.0% |
| macd_12_26_9_crossover_dn | 1.4% |
| macd_12_26_9_crossover_up | 2.8% |
| macd_8_21_5_bearish | 56.6% |
| macd_8_21_5_bullish | 43.4% |
| macd_8_21_5_crossover_dn | 3.3% |
| macd_8_21_5_crossover_up | 9.4% |
| marubozu_bull | 1.9% |
| mfi_broad_overbought | 10.4% |
| mfi_broad_oversold | 11.8% |
| mfi_overbought | 1.4% |
| mfi_oversold | 1.9% |
| monthly_above_sma_12 | 97.6% |
| monthly_above_sma_6 | 51.0% |
| monthly_bias_bear | 2.4% |
| monthly_bias_bull | 51.0% |
| monthly_momentum_pos | 82.5% |
| morning_star | 5.7% |
| near_52w_high | 5.7% |
| near_52w_high_95pct | 18.9% |
| near_52w_high_retest_long | 6.1% |
| near_avwap_20high_atr_05x | 39.3% |
| near_avwap_20high_atr_10x | 64.8% |
| near_avwap_20high_atr_15x | 83.2% |
| near_avwap_20high_atr_20x | 90.3% |
| near_avwap_20low_atr_05x | 26.2% |
| near_avwap_20low_atr_10x | 54.8% |
| near_avwap_20low_atr_15x | 76.2% |
| near_avwap_20low_atr_20x | 90.5% |
| near_avwap_252low_atr_05x | 6.2% |
| near_avwap_252low_atr_10x | 12.0% |
| near_avwap_252low_atr_15x | 23.9% |
| near_avwap_252low_atr_20x | 32.5% |
| near_avwap_50low_atr_05x | 21.3% |
| near_avwap_50low_atr_10x | 49.5% |
| near_avwap_50low_atr_15x | 66.0% |
| near_avwap_50low_atr_20x | 77.7% |
| near_cam_r3 | 25.0% |
| near_cam_s3 | 7.5% |
| near_cam_s4 | 1.4% |
| near_fib_236 | 2.8% |
| near_fib_382 | 5.2% |
| near_fib_500 | 9.4% |
| near_fib_618 | 12.3% |
| near_fib_786 | 6.6% |
| near_pivot | 17.9% |
| near_prev_close | 18.9% |
| near_prev_high | 18.9% |
| near_prev_low | 5.2% |
| near_r1 | 19.3% |
| near_r1_wide | 70.3% |
| near_r2 | 6.1% |
| near_r2_wide | 47.2% |
| near_s1 | 1.9% |
| near_s1_wide | 33.0% |
| near_s2 | 1.4% |
| near_s2_wide | 8.0% |
| near_wood_r1 | 14.2% |
| near_wood_s1 | 9.4% |
| news_uses_polygon_score | 27.4% |
| obv_bearish | 51.9% |
| obv_bullish | 48.1% |
| obv_diverge_bull | 7.1% |
| obv_falling | 46.7% |
| obv_rising | 53.3% |
| outside_bar | 11.3% |
| pead_negative_surprise | 6.8% |
| pead_positive_surprise | 37.0% |
| pin_bar | 10.4% |
| po3_accumulation_active | 32.1% |
| po3_bullish | 25.9% |
| po3_manipulation_sweep_down | 6.1% |
| po3_manipulation_sweep_up | 11.3% |
| po3_mmbm_setup | 4.2% |
| po3_sweep_above_prior_high | 58.0% |
| po3_sweep_below_prior_low | 42.9% |
| ppo_bullish | 33.5% |
| ppo_crossover_dn | 0.9% |
| ppo_crossover_up | 2.4% |
| pre_fomc_d0 | 0.9% |
| pre_fomc_d1 | 2.8% |
| pre_fomc_window | 3.8% |
| price_above_dema | 50.5% |
| price_above_ema_20 | 40.1% |
| price_above_ema_200_break_recent_5d | 28.3% |
| price_above_ema_20_break_recent_5d | 23.6% |
| price_above_ema_21 | 40.1% |
| price_above_ema_21_break_recent_5d | 23.6% |
| price_above_ema_50 | 37.7% |
| price_above_ema_50_break_recent_5d | 16.0% |
| price_above_ema_9 | 50.5% |
| price_above_ema_9_break_recent_5d | 38.7% |
| price_above_hull | 55.2% |
| price_above_sma_200 | 92.5% |
| price_above_sma_21 | 40.1% |
| price_above_sma_50 | 34.9% |
| price_above_tema | 60.8% |
| price_below_dema | 49.5% |
| price_below_hull | 44.8% |
| price_below_tema | 39.2% |
| psar_bullish | 39.2% |
| psar_flip_dn | 2.4% |
| psar_flip_up | 5.2% |
| r1_break_retest_long | 50.5% |
| recent_blowoff_at_r3 | 0.5% |
| resistance_break_retest | 15.6% |
| risk_off_regime_bond_signal | 33.0% |
| risk_off_regime_bond_signal_strong | 15.6% |
| risk_off_regime_gold_signal | 57.1% |
| risk_on_regime_bond_signal | 30.7% |
| risk_on_regime_bond_signal_strong | 12.7% |
| roc_positive | 40.1% |
| roc_turning_dn | 1.4% |
| roc_turning_up | 8.0% |
| rsi_14_bullish | 38.7% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.5% |
| rsi_14_cross_dn_overbought_recent_3d | 1.4% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.5% |
| rsi_14_cross_up_oversold_recent_3d | 11.8% |
| rsi_14_overbought | 3.3% |
| rsi_14_oversold | 2.4% |
| rsi_14_rising | 78.8% |
| rsi_21_bullish | 38.2% |
| rsi_21_cross_up_oversold_recent_3d | 2.8% |
| rsi_21_overbought | 0.9% |
| rsi_21_rising | 79.2% |
| rsi_2_bullish | 71.2% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 18.9% |
| rsi_2_cross_dn_overbought_recent_3d | 18.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 47.6% |
| rsi_2_cross_up_oversold_recent_3d | 49.1% |
| rsi_2_extreme_ob | 32.1% |
| rsi_2_extreme_os | 15.1% |
| rsi_2_overbought | 48.6% |
| rsi_2_oversold | 19.3% |
| rsi_2_rising | 78.8% |
| rsi_9_bullish | 43.4% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.9% |
| rsi_9_cross_dn_overbought_recent_3d | 2.8% |
| rsi_9_cross_up_extreme_os_recent_3d | 9.0% |
| rsi_9_cross_up_oversold_recent_3d | 24.5% |
| rsi_9_extreme_ob | 0.9% |
| rsi_9_extreme_os | 0.5% |
| rsi_9_overbought | 6.1% |
| rsi_9_oversold | 11.3% |
| rsi_9_rising | 78.8% |
| s1_break_retest_short | 56.1% |
| sc_13d_filed_within_30d | 1.8% |
| sc_13g_filed_within_30d | 0.5% |
| sector_outperforming_spy | 28.6% |
| sector_underperforming_spy | 71.4% |
| shooting_star | 3.8% |
| sma_20_50_bullish | 47.6% |
| sma_50_200_bullish | 92.9% |
| sma_50_200_golden_cross | 0.5% |
| sma_9_21_bullish | 35.4% |
| sma_9_21_golden_cross | 3.3% |
| smc_bos_bearish | 4.2% |
| smc_bos_bullish | 20.8% |
| smc_bos_retest_long | 7.1% |
| smc_breaker_block_bearish | 3.8% |
| smc_breaker_block_bullish | 46.2% |
| smc_choch_bearish | 6.1% |
| smc_choch_bullish | 5.7% |
| smc_equal_highs_swept | 2.8% |
| smc_equal_lows_swept | 0.9% |
| smc_fvg_bearish_active | 46.7% |
| smc_fvg_bullish_active | 32.1% |
| smc_fvg_retest_long_zone | 1.4% |
| smc_fvg_retest_short_zone | 13.2% |
| smc_in_discount_zone | 71.2% |
| smc_in_premium_zone | 58.5% |
| smc_inverse_fvg_bearish | 85.8% |
| smc_inverse_fvg_bullish | 89.2% |
| smc_liquidity_swept_up | 0.5% |
| smc_mitigation_block_long | 1.4% |
| smc_mitigation_block_short | 0.9% |
| smc_ob_bearish_active | 19.3% |
| smc_ob_bullish_active | 45.3% |
| smc_ote_long_zone | 14.2% |
| smc_ote_short_zone | 5.2% |
| squeeze_fire_dn | 0.5% |
| squeeze_fire_up | 4.7% |
| squeeze_in | 25.9% |
| squeeze_positive | 42.0% |
| stoch_bearish_cross | 7.1% |
| stoch_broad_overbought | 20.8% |
| stoch_broad_oversold | 29.2% |
| stoch_bullish_cross | 21.7% |
| stoch_overbought | 15.1% |
| stoch_oversold | 22.6% |
| stochrsi_cross_dn | 12.3% |
| stochrsi_cross_up | 45.8% |
| stochrsi_overbought | 28.8% |
| stochrsi_oversold | 29.2% |
| supertrend_bearish | 3.8% |
| supertrend_bullish | 96.2% |
| supertrend_flip_recent_long_5d | 10.4% |
| supertrend_flip_recent_short_5d | 11.3% |
| supertrend_flip_up | 4.7% |
| support_break_retest | 32.1% |
| tema_above_dema | 29.2% |
| tema_cross_dn | 0.9% |
| tema_cross_up | 2.4% |
| three_white_soldiers | 8.5% |
| triangle_apex_break_retest_long | 8.0% |
| triangle_ascending_detected | 7.1% |
| triangle_descending_detected | 10.4% |
| uo_overbought | 1.4% |
| uo_oversold | 1.4% |
| usd_strengthening | 19.8% |
| usd_weakening | 18.9% |
| vix_band_high | 59.9% |
| vix_band_low | 23.1% |
| vix_band_mid | 17.0% |
| vix_term_backwardation | 29.7% |
| vix_term_contango | 70.3% |
| vol_above_avg | 47.2% |
| vol_below_avg | 52.8% |
| vol_spike_12x | 33.0% |
| vol_spike_15x | 17.5% |
| vol_spike_17x | 9.4% |
| vol_spike_2x | 5.2% |
| vol_spike_2x_on_down_day_recent_3d | 8.0% |
| vol_spike_2x_on_up_day_recent_3d | 3.3% |
| vol_spike_3x | 0.5% |
| vp_above_value_area | 10.8% |
| vp_below_value_area | 25.0% |
| vp_close_above_poc | 39.2% |
| vp_close_below_poc | 60.8% |
| vp_in_value_area | 64.2% |
| week_open_gap_down_15pct | 6.6% |
| weekly_above_ema_10 | 40.1% |
| weekly_above_ema_20 | 56.1% |
| weekly_bias_bear | 41.0% |
| weekly_bias_bull | 37.3% |
| weekly_momentum_pos | 34.4% |
| williams_r_overbought | 20.8% |
| williams_r_oversold | 11.3% |
| williams_r_rising | 83.5% |
| within_pead_window | 31.7% |
| within_post_inclusion_window | 5.6% |
| xs_avoid_high_max | 93.4% |
| xs_high_beta_decile | 13.7% |
| xs_low_beta_bottom_quintile | 13.7% |
| xs_low_beta_decile | 34.9% |
| xs_low_beta_decile_entry_recent_5d | 1.4% |
| xs_low_beta_top_quintile | 34.9% |
| xs_momentum_top_decile | 35.8% |
| xs_quality_bottom_quintile | 17.1% |
| xs_quality_top_quintile | 19.7% |
| xs_quality_top_tercile | 40.2% |
| year_high_break_retest_long | 2.8% |
| yoy_surprise_high | 67.8% |
| yoy_surprise_negative | 23.8% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 88.2% |
| committed_growth_holders | 88.2% |
| corp_donations_1y | 4.7% |
| corp_donations_count_1y | 4.7% |
| corp_donations_unique_pacs | 4.7% |
| cot_rut_commercials_pctile_3y | 59.0% |
| cot_rut_mmoney_pctile_3y | 59.0% |
| cup_handle_depth_pct | 24.5% |
| days_since_deletion | 4.7% |
| days_since_inclusion | 8.5% |
| days_to_next_holiday | 77.4% |
| days_to_rebalance | 2.4% |
| dpi_30d_avg | 94.8% |
| dpi_recent | 94.8% |
| earnings_announcement_return | 90.6% |
| earnings_eps_yoy_growth | 95.3% |
| flag_bull_pole_move_pct | 2.8% |
| gov_contracts_4q_sum | 44.3% |
| gov_contracts_last_qtr_amount | 44.3% |
| gov_contracts_qoq_growth | 44.3% |
| head_shoulders_magnitude_pct | 8.5% |
| insider_director_buyers_30d | 5.2% |
| insider_officer_buyers_30d | 5.2% |
| insider_total_shares_bought_30d | 5.2% |
| insider_unique_buyers_30d | 5.2% |
| inverted_cup_handle_height_pct | 27.4% |
| lobbying_amount_1y | 71.7% |
| lobbying_amount_q | 71.7% |
| lobbying_amount_yoy | 71.7% |
| monthly_momentum_6m | 97.2% |
| otc_short_ratio_recent | 94.8% |
| otc_volume_recent | 94.8% |
| pair_half_life | 96.7% |
| pair_max_abs_zscore | 96.7% |
| pair_zscore_signed | 96.7% |
| pct_from_avwap_20high | 92.5% |
| pct_from_avwap_20low | 79.2% |
| pct_from_avwap_50low | 88.7% |
| persistent_holders_4q | 88.2% |
| persistent_holders_8q | 88.2% |
| search_volume_index_recent | 77.4% |
| search_volume_observations | 77.4% |
| search_volume_zscore_30d | 77.4% |
| sector_etf_return_20d | 3.3% |
| spy_return_20d | 3.3% |
| total_active_holders | 88.2% |
| triangle_breakdown_pct | 10.4% |
| triangle_breakout_pct | 7.1% |
| xs_quality_decile | 55.2% |
| xs_quality_gross_profitability | 55.2% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.995), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.994), `double_bottom_trough` (0.995), `double_top_neckline` (0.998), `double_top_peak` (0.997), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.999), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.998), `fib_ext_127` (0.998), `fib_ext_162` (0.997), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.976), `head_shoulders_top_neckline` (0.988), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.996), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.995), `monthly_sma_6` (0.998), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.998), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.998), `s2` (0.998), `s3` (0.997), `supertrend_value` (0.996), `swing_high` (0.998), `swing_low` (0.997), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (0.994), `vp_poc` (0.997), `vp_value_area_high` (0.998), `vp_value_area_low` (0.996), `vwap` (0.97), `vwap_lower_1` (0.966), `vwap_lower_2` (0.963), `vwap_upper_1` (0.974), `vwap_upper_2` (0.976), `weekly_close` (0.999), `weekly_ema_10` (1.0), `weekly_ema_20` (0.999), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.998), `year_high` (0.998), `year_low` (0.981)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | quantile cut (quintile) | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3 | xs_ivol_decile <= 4 | 4 | subset-safe | no - derives offline |

```
FULL FACTORIAL     3 x 3 x 4 = 36
offline gradings   4 level-combinations x 24 exits = 96
ENGINE RUNS        1 (actuated fire-adding axes only)
PENDING ACTUATION  9 level-combinations are DEFINED but have no env knob - they are a FEATURE REQUEST, not a runnable band (plan 11.0b state 1; B2866)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 602 census axes join it only when REGISTERED at the T3 band review.
