# Table A - smc_mitigation_block_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** smc | **status:** NOT-STARTED | **R5 fires:** 15 | **surviving fires (T1):** 15 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       knobs P1.1-P1.1 (band rows in Table A)
P2  smc_mitigation_block_long  <- backtest/signals/screener.py +2
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  rsi_14 < 50   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_smc_mitigation_block_long (docstring and return dropped):

```python
fires = s.get('smc_mitigation_block_long', False) and s.get('price_above_ema_200', False) and (s.get('rsi_14', 50) < 50)
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
| P1 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | 200 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production; 150/250 are the adjacent canon spans; T3 review before any grid |
| P2 | PRODUCER | smc_mitigation_block_long - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | smc family knobs (swing_length, event_recency_bars) - backtest/signals/smc_ict.py mitigation block | (20, 90) | none - other-knob values unpersisted | the whole band; env SMC_SWING_LENGTH / SMC_EVENT_RECENCY_BARS | the smc SPECS family bands (producer_variant_table); T3 review before any grid |
| P3 | STRATEGY | rsi_14 `< 50` [EXISTING-THRESHOLD] | `< 50` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3.1 | BAND | rsi span - backtest/signals/technical.py rsi block | 14 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 50` | 100.0% | TIGHTER = LOWER the ceiling: 32.88 -> 3 (20%); 34.776 -> 6 (40%); 38.162 -> 9 (60%); 39.63 -> 12 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 18.684, 21.992, 23.252, 25.158 | 18.684: 12 (80%); 21.992: 9 (60%); 23.252: 6 (40%); 25.158: 3 (20%) | 18.684: 3 (20%); 21.992: 6 (40%); 23.252: 9 (60%); 25.158: 12 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 30.914, 32.332, 34.428, 37.902 | 30.914: 12 (80%); 32.332: 9 (60%); 34.428: 6 (40%); 37.902: 3 (20%) | 30.914: 3 (20%); 32.332: 6 (40%); 34.428: 9 (60%); 37.902: 12 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 12.196, 14.4, 15.118, 16.22 | 12.196: 12 (80%); 14.4: 9 (60%); 15.118: 6 (40%); 16.22: 3 (20%) | 12.196: 3 (20%); 14.4: 6 (40%); 15.118: 9 (60%); 16.22: 12 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -18.7579, -9.043, -7.4459, -6.4229 | -18.7579: 12 (80%); -9.043: 9 (60%); -7.4459: 6 (40%); -6.4229: 3 (20%) | -18.7579: 3 (20%); -9.043: 6 (40%); -7.4459: 9 (60%); -6.4229: 12 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 3.1398, 4.5015, 6.7234, 9.842 | 3.1398: 12 (80%); 4.5015: 9 (60%); 6.7234: 6 (40%); 9.842: 3 (20%) | 3.1398: 3 (20%); 4.5015: 6 (40%); 6.7234: 9 (60%); 9.842: 12 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 3.1398, 4.5015, 6.7234, 9.842 | 3.1398: 12 (80%); 4.5015: 9 (60%); 6.7234: 6 (40%); 9.842: 3 (20%) | 3.1398: 3 (20%); 4.5015: 6 (40%); 6.7234: 9 (60%); 9.842: 12 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.279, 3.0402, 4.0894, 4.9854 | 2.279: 12 (80%); 3.0402: 9 (60%); 4.0894: 6 (40%); 4.9854: 3 (20%) | 2.279: 3 (20%); 3.0402: 6 (40%); 4.0894: 9 (60%); 4.9854: 12 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0779, 0.0871, 0.1854, 0.2119 | 0.0779: 12 (80%); 0.0871: 9 (60%); 0.1854: 6 (40%); 0.2119: 3 (20%) | 0.0779: 3 (20%); 0.0871: 6 (40%); 0.1854: 9 (60%); 0.2119: 12 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.1211, 0.1515, 0.234, 0.2676 | 0.1211: 12 (80%); 0.1515: 9 (60%); 0.234: 6 (40%); 0.2676: 3 (20%) | 0.1211: 3 (20%); 0.1515: 6 (40%); 0.234: 9 (60%); 0.2676: 12 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0936, 0.1059, 0.1285, 0.1624 | 0.0936: 12 (80%); 0.1059: 9 (60%); 0.1285: 6 (40%); 0.1624: 3 (20%) | 0.0936: 3 (20%); 0.1059: 6 (40%); 0.1285: 9 (60%); 0.1624: 12 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.1599, -0.0738, -0.0056, 0.066 | -0.1599: 12 (80%); -0.0738: 9 (60%); -0.0056: 6 (40%); 0.066: 3 (20%) | -0.1599: 3 (20%); -0.0738: 6 (40%); -0.0056: 9 (60%); 0.066: 12 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1248, 0.1411, 0.1713, 0.2166 | 0.1248: 12 (80%); 0.1411: 9 (60%); 0.1713: 6 (40%); 0.2166: 3 (20%) | 0.1248: 3 (20%); 0.1411: 6 (40%); 0.1713: 9 (60%); 0.2166: 12 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0051, 0.0697, 0.1208, 0.1745 | 0.0051: 12 (80%); 0.0697: 9 (60%); 0.1208: 6 (40%); 0.1745: 3 (20%) | 0.0051: 3 (20%); 0.0697: 6 (40%); 0.1208: 9 (60%); 0.1745: 12 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0242, 0.0038, 0.0204, 0.0357 | -0.0242: 12 (80%); 0.0038: 9 (60%); 0.0204: 6 (40%); 0.0357: 3 (20%) | -0.0242: 3 (20%); 0.0038: 6 (40%); 0.0204: 9 (60%); 0.0357: 12 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1357, 0.1451, 0.1662, 0.2662 | 0.1357: 12 (80%); 0.1451: 9 (60%); 0.1662: 6 (40%); 0.2662: 3 (20%) | 0.1357: 3 (20%); 0.1451: 6 (40%); 0.1662: 9 (60%); 0.2662: 12 (80%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.138, -0.1138, -0.0389, 0.0026 | -0.138: 12 (80%); -0.1138: 9 (60%); -0.0389: 6 (40%); 0.0026: 3 (20%) | -0.138: 3 (20%); -0.1138: 6 (40%); -0.0389: 9 (60%); 0.0026: 12 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 15 (100%); 1: 8 (53%) | 0: 7 (47%); 1: 13 (87%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2388, -0.2157, -0.1775, -0.1508 | -0.2388: 12 (80%); -0.2157: 9 (60%); -0.1775: 6 (40%); -0.1508: 3 (20%) | -0.2388: 3 (20%); -0.2157: 6 (40%); -0.1775: 9 (60%); -0.1508: 12 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1462, 0.4436, 0.5667, 0.7372 | 0.1462: 12 (80%); 0.4436: 9 (60%); 0.5667: 6 (40%); 0.7372: 4 (27%) | 0.1462: 3 (20%); 0.4436: 6 (40%); 0.5667: 9 (60%); 0.7372: 13 (87%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3077, 0.718, 0.8461, 0.941 | 0.3077: 12 (80%); 0.718: 9 (60%); 0.8461: 6 (40%); 0.941: 3 (20%) | 0.3077: 3 (20%); 0.718: 6 (40%); 0.8461: 9 (60%); 0.941: 12 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1214, -0.0353, 0.0214, 0.1124 | -0.1214: 12 (80%); -0.0353: 9 (60%); 0.0214: 6 (40%); 0.1124: 3 (20%) | -0.1214: 3 (20%); -0.0353: 6 (40%); 0.0214: 9 (60%); 0.1124: 12 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2526, 0.3795, 0.55, 0.7128 | 0.2526: 12 (80%); 0.3795: 9 (60%); 0.55: 6 (40%); 0.7128: 3 (20%) | 0.2526: 3 (20%); 0.3795: 6 (40%); 0.55: 9 (60%); 0.7128: 12 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1372, 0.3321, 0.3974, 0.6654 | 0.1372: 12 (80%); 0.3321: 9 (60%); 0.3974: 6 (40%); 0.6654: 3 (20%) | 0.1372: 3 (20%); 0.3321: 6 (40%); 0.3974: 9 (60%); 0.6654: 12 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3529, -0.1509, 0.0105, 0.1382 | -0.3529: 12 (80%); -0.1509: 9 (60%); 0.0105: 6 (40%); 0.1382: 3 (20%) | -0.3529: 3 (20%); -0.1509: 6 (40%); 0.0105: 9 (60%); 0.1382: 12 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5103, 0.7346, 0.8615, 0.9615 | 0.5103: 12 (80%); 0.7346: 9 (60%); 0.8615: 6 (40%); 0.9615: 3 (20%) | 0.5103: 3 (20%); 0.7346: 6 (40%); 0.8615: 9 (60%); 0.9615: 12 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0128, 0.1705, 0.4808, 0.6179 | 0.0128: 14 (93%); 0.1705: 9 (60%); 0.4808: 7 (47%); 0.6179: 3 (20%) | 0.0128: 4 (27%); 0.1705: 6 (40%); 0.4808: 10 (67%); 0.6179: 12 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0738, -0.0667, -0.0557, -0.0394 | -0.0738: 12 (80%); -0.0667: 9 (60%); -0.0557: 6 (40%); -0.0394: 3 (20%) | -0.0738: 3 (20%); -0.0667: 6 (40%); -0.0557: 9 (60%); -0.0394: 12 (80%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2782, 0.4525, 0.6474, 0.8654 | 0.2782: 12 (80%); 0.4525: 9 (60%); 0.6474: 6 (40%); 0.8654: 4 (27%) | 0.2782: 3 (20%); 0.4525: 6 (40%); 0.6474: 9 (60%); 0.8654: 13 (87%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.509, 0.5949, 0.8667 | 0.1538: 13 (87%); 0.509: 9 (60%); 0.5949: 6 (40%); 0.8667: 3 (20%) | 0.1538: 4 (27%); 0.509: 6 (40%); 0.5949: 9 (60%); 0.8667: 12 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0362, 0.0848, 0.1942, 0.3199 | 0.0362: 12 (80%); 0.0848: 9 (60%); 0.1942: 6 (40%); 0.3199: 3 (20%) | 0.0362: 3 (20%); 0.0848: 6 (40%); 0.1942: 9 (60%); 0.3199: 12 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.8195, 0.9149, 0.9641, 0.9949 | 0.8195: 12 (80%); 0.9149: 9 (60%); 0.9641: 6 (40%); 0.9949: 3 (20%) | 0.8195: 3 (20%); 0.9149: 6 (40%); 0.9641: 9 (60%); 0.9949: 12 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1637, 0.18, 0.3449, 0.7561 | 0.1637: 12 (80%); 0.18: 9 (60%); 0.3449: 6 (40%); 0.7561: 3 (20%) | 0.1637: 3 (20%); 0.18: 6 (40%); 0.3449: 9 (60%); 0.7561: 12 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.04, 0.0562, 0.1236, 0.1805 | -0.04: 12 (80%); 0.0562: 9 (60%); 0.1236: 6 (40%); 0.1805: 3 (20%) | -0.04: 3 (20%); 0.0562: 6 (40%); 0.1236: 9 (60%); 0.1805: 12 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3206, -0.0085, 0.0249, 0.0597 | -0.3206: 12 (80%); -0.0085: 9 (60%); 0.0249: 6 (40%); 0.0597: 3 (20%) | -0.3206: 3 (20%); -0.0085: 6 (40%); 0.0249: 9 (60%); 0.0597: 12 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3577, 0.5628, 0.7308, 0.8577 | 0.3577: 12 (80%); 0.5628: 9 (60%); 0.7308: 7 (47%); 0.8577: 3 (20%) | 0.3577: 3 (20%); 0.5628: 6 (40%); 0.7308: 11 (73%); 0.8577: 12 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1154, 0.3423, 0.6359, 0.7962 | 0.1154: 13 (87%); 0.3423: 9 (60%); 0.6359: 6 (40%); 0.7962: 3 (20%) | 0.1154: 4 (27%); 0.3423: 6 (40%); 0.6359: 9 (60%); 0.7962: 12 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.1845, 0.3557, 0.5337, 0.9174 | 0.1845: 12 (80%); 0.3557: 9 (60%); 0.5337: 6 (40%); 0.9174: 3 (20%) | 0.1845: 3 (20%); 0.3557: 6 (40%); 0.5337: 9 (60%); 0.9174: 12 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 48, 79, 103.2, 139.2 | 48: 13 (87%); 79: 9 (60%); 103.2: 6 (40%); 139.2: 3 (20%) | 48: 4 (27%); 79: 6 (40%); 103.2: 9 (60%); 139.2: 12 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7.6, 14.4, 23.8, 34.2 | 7.6: 12 (80%); 14.4: 9 (60%); 23.8: 6 (40%); 34.2: 3 (20%) | 7.6: 3 (20%); 14.4: 6 (40%); 23.8: 9 (60%); 34.2: 12 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 2.4, 3.2 | 1: 14 (93%); 2: 11 (73%); 2.4: 6 (40%); 3.2: 3 (20%) | 1: 4 (27%); 2: 9 (60%); 2.4: 9 (60%); 3.2: 12 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0103, -0.008, 0.006, 0.0191 | -0.0103: 12 (80%); -0.008: 9 (60%); 0.006: 6 (40%); 0.0191: 4 (27%) | -0.0103: 3 (20%); -0.008: 6 (40%); 0.006: 9 (60%); 0.0191: 14 (93%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.4157, 26.4789, 26.8834, 27.2784 | 24.4157: 12 (80%); 26.4789: 9 (60%); 26.8834: 6 (40%); 27.2784: 3 (20%) | 24.4157: 3 (20%); 26.4789: 6 (40%); 26.8834: 9 (60%); 27.2784: 12 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.3894, -0.0594, 0.067, 4.207 | -0.3894: 12 (80%); -0.0594: 9 (60%); 0.067: 6 (40%); 4.207: 3 (20%) | -0.3894: 3 (20%); -0.0594: 6 (40%); 0.067: 9 (60%); 4.207: 12 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -4.207, -0.067, 0.0594, 0.3894 | -4.207: 12 (80%); -0.067: 9 (60%); 0.0594: 6 (40%); 0.3894: 3 (20%) | -4.207: 3 (20%); -0.067: 6 (40%); 0.0594: 9 (60%); 0.3894: 12 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0461, 0.0074, 0.0131, 0.0362 | -0.0461: 12 (80%); 0.0074: 9 (60%); 0.0131: 6 (40%); 0.0362: 3 (20%) | -0.0461: 3 (20%); 0.0074: 6 (40%); 0.0131: 9 (60%); 0.0362: 12 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.8487, 8.5925, 8.7579, 9.1651 | 7.8487: 12 (80%); 8.5925: 9 (60%); 8.7579: 6 (40%); 9.1651: 3 (20%) | 7.8487: 3 (20%); 8.5925: 6 (40%); 8.7579: 9 (60%); 9.1651: 12 (80%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 5.4, 231.4, 297.2 | 2: 13 (87%); 5.4: 9 (60%); 231.4: 6 (40%); 297.2: 3 (20%) | 2: 4 (27%); 5.4: 6 (40%); 231.4: 9 (60%); 297.2: 12 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 8.8, 134, 176 | 0: 15 (100%); 8.8: 9 (60%); 134: 6 (40%); 176: 3 (20%) | 0: 4 (27%); 8.8: 6 (40%); 134: 9 (60%); 176: 12 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -3.1686, -1.9315, -1.4479, -0.699 | -3.1686: 12 (80%); -1.9315: 9 (60%); -1.4479: 6 (40%); -0.699: 3 (20%) | -3.1686: 3 (20%); -1.9315: 6 (40%); -1.4479: 9 (60%); -0.699: 12 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -6.3712, -2.653, -2.3509, -1.8747 | -6.3712: 12 (80%); -2.653: 9 (60%); -2.3509: 6 (40%); -1.8747: 3 (20%) | -6.3712: 3 (20%); -2.653: 6 (40%); -2.3509: 9 (60%); -1.8747: 12 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.7861, -1.6194, -0.6045, -0.3199 | -2.7861: 12 (80%); -1.6194: 9 (60%); -0.6045: 6 (40%); -0.3199: 3 (20%) | -2.7861: 3 (20%); -1.6194: 6 (40%); -0.6045: 9 (60%); -0.3199: 12 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -2.0179, -0.9543, -0.8466, -0.5056 | -2.0179: 12 (80%); -0.9543: 9 (60%); -0.8466: 6 (40%); -0.5056: 3 (20%) | -2.0179: 3 (20%); -0.9543: 6 (40%); -0.8466: 9 (60%); -0.5056: 12 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -7.7241, -4.0644, -3.5232, -3.0456 | -7.7241: 12 (80%); -4.0644: 9 (60%); -3.5232: 6 (40%); -3.0456: 3 (20%) | -7.7241: 3 (20%); -4.0644: 6 (40%); -3.5232: 9 (60%); -3.0456: 12 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -6.6611, -2.9966, -2.539, -1.9221 | -6.6611: 12 (80%); -2.9966: 9 (60%); -2.539: 6 (40%); -1.9221: 3 (20%) | -6.6611: 3 (20%); -2.9966: 6 (40%); -2.539: 9 (60%); -1.9221: 12 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 26.086, 33.682, 37.75, 41.444 | 26.086: 12 (80%); 33.682: 9 (60%); 37.75: 6 (40%); 41.444: 3 (20%) | 26.086: 3 (20%); 33.682: 6 (40%); 37.75: 9 (60%); 41.444: 12 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1.2, 5.8, 7.4 | 0: 15 (100%); 1.2: 9 (60%); 5.8: 6 (40%); 7.4: 3 (20%) | 0: 6 (40%); 1.2: 6 (40%); 5.8: 9 (60%); 7.4: 12 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0222 | 0: 15 (100%); 0.0222: 3 (20%) | 0: 12 (80%); 0.0222: 12 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.38, 0.4444 | 0: 15 (100%); 0.38: 6 (40%); 0.4444: 4 (27%) | 0: 7 (47%); 0.38: 9 (60%); 0.4444: 13 (87%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1.2, 3.8, 5.4 | 0: 15 (100%); 1.2: 9 (60%); 3.8: 6 (40%); 5.4: 3 (20%) | 0: 6 (40%); 1.2: 6 (40%); 3.8: 9 (60%); 5.4: 12 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1.2, 5.8, 7.4 | 0: 15 (100%); 1.2: 9 (60%); 5.8: 6 (40%); 7.4: 3 (20%) | 0: 6 (40%); 1.2: 6 (40%); 5.8: 9 (60%); 7.4: 12 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4.6, 9.8 | 0: 15 (100%); 1: 11 (73%); 4.6: 6 (40%); 9.8: 3 (20%) | 0: 4 (27%); 1: 7 (47%); 4.6: 9 (60%); 9.8: 12 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.2325, 0.3451, 0.44, 1 | 0.2325: 12 (80%); 0.3451: 9 (60%); 0.44: 6 (40%); 1: 4 (27%) | 0.2325: 3 (20%); 0.3451: 6 (40%); 0.44: 9 (60%); 1: 15 (100%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.05, 0.3189 | 0: 14 (93%); 0.05: 6 (40%); 0.3189: 3 (20%) | 0: 9 (60%); 0.05: 9 (60%); 0.3189: 12 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2013, 0.4116 | 0: 15 (100%); 0.2013: 6 (40%); 0.4116: 3 (20%) | 0: 7 (47%); 0.2013: 9 (60%); 0.4116: 12 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2013, 0.4116 | 0: 15 (100%); 0.2013: 6 (40%); 0.4116: 3 (20%) | 0: 7 (47%); 0.2013: 9 (60%); 0.4116: 12 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0138, 0, 0.1107 | -0.0138: 12 (80%); 0: 12 (80%); 0.1107: 3 (20%) | -0.0138: 3 (20%); 0: 11 (73%); 0.1107: 12 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7885, -0.5455, -0.2683, 1.3833 | -0.7885: 12 (80%); -0.5455: 9 (60%); -0.2683: 6 (40%); 1.3833: 3 (20%) | -0.7885: 3 (20%); -0.5455: 6 (40%); -0.2683: 9 (60%); 1.3833: 12 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2.6, 5.2, 7.8, 10.6 | 2.6: 12 (80%); 5.2: 9 (60%); 7.8: 6 (40%); 10.6: 3 (20%) | 2.6: 3 (20%); 5.2: 6 (40%); 7.8: 9 (60%); 10.6: 12 (80%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.1124, -0.0789, -0.068, -0.0477 | -0.1124: 12 (80%); -0.0789: 9 (60%); -0.068: 6 (40%); -0.0477: 3 (20%) | -0.1124: 3 (20%); -0.0789: 6 (40%); -0.068: 9 (60%); -0.0477: 12 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1395, -0.1214, -0.1017, -0.0664 | -0.1395: 12 (80%); -0.1214: 9 (60%); -0.1017: 6 (40%); -0.0664: 3 (20%) | -0.1395: 3 (20%); -0.1214: 6 (40%); -0.1017: 9 (60%); -0.0664: 12 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.1172, -0.0636, -0.0299, -0.0215 | -0.1172: 12 (80%); -0.0636: 9 (60%); -0.0299: 6 (40%); -0.0215: 3 (20%) | -0.1172: 3 (20%); -0.0636: 6 (40%); -0.0299: 9 (60%); -0.0215: 12 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -8.1678, -5.8786, -5.0068, -4.2734 | -8.1678: 12 (80%); -5.8786: 9 (60%); -5.0068: 6 (40%); -4.2734: 3 (20%) | -8.1678: 3 (20%); -5.8786: 6 (40%); -5.0068: 9 (60%); -4.2734: 12 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | 16.8028, 22.8604, 30.5678, 94.6714 | 16.8028: 12 (80%); 22.8604: 9 (60%); 30.5678: 6 (40%); 94.6714: 3 (20%) | 16.8028: 3 (20%); 22.8604: 6 (40%); 30.5678: 9 (60%); 94.6714: 12 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0491, 0.0752, 0.108, 0.1932 | 0.0491: 12 (80%); 0.0752: 9 (60%); 0.108: 6 (40%); 0.1932: 3 (20%) | 0.0491: 3 (20%); 0.0752: 6 (40%); 0.108: 9 (60%); 0.1932: 12 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.4416, 0.5983, 0.7421, 0.8098 | 0.4416: 12 (80%); 0.5983: 9 (60%); 0.7421: 6 (40%); 0.8098: 3 (20%) | 0.4416: 3 (20%); 0.5983: 6 (40%); 0.7421: 9 (60%); 0.8098: 12 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.3073, -2.0843, -1.7115, -1.2464 | -2.3073: 12 (80%); -2.0843: 9 (60%); -1.7115: 6 (40%); -1.2464: 3 (20%) | -2.3073: 3 (20%); -2.0843: 6 (40%); -1.7115: 9 (60%); -1.2464: 12 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.4952, -1.0909, -0.7749, -0.5161 | -1.4952: 12 (80%); -1.0909: 9 (60%); -0.7749: 6 (40%); -0.5161: 3 (20%) | -1.4952: 3 (20%); -1.0909: 6 (40%); -0.7749: 9 (60%); -0.5161: 12 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.4308, -1.1527, -0.6642, -0.1789 | -1.4308: 12 (80%); -1.1527: 9 (60%); -0.6642: 6 (40%); -0.1789: 3 (20%) | -1.4308: 3 (20%); -1.1527: 6 (40%); -0.6642: 9 (60%); -0.1789: 12 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -15.3712, -8.6488, -7.4332, -4.7346 | -15.3712: 12 (80%); -8.6488: 9 (60%); -7.4332: 6 (40%); -4.7346: 3 (20%) | -15.3712: 3 (20%); -8.6488: 6 (40%); -7.4332: 9 (60%); -4.7346: 12 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 16.596, 29.508, 40.84, 50.816 | 16.596: 12 (80%); 29.508: 9 (60%); 40.84: 6 (40%); 50.816: 3 (20%) | 16.596: 3 (20%); 29.508: 6 (40%); 40.84: 9 (60%); 50.816: 12 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 37.24, 39.136, 41.212, 43.856 | 37.24: 12 (80%); 39.136: 9 (60%); 41.212: 6 (40%); 43.856: 3 (20%) | 37.24: 3 (20%); 39.136: 6 (40%); 41.212: 9 (60%); 43.856: 12 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 27.098, 30.788, 34.416, 36.618 | 27.098: 12 (80%); 30.788: 9 (60%); 34.416: 6 (40%); 36.618: 3 (20%) | 27.098: 3 (20%); 30.788: 6 (40%); 34.416: 9 (60%); 36.618: 12 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0328, 0.0418, 0.0466, 0.0625 | 0.0328: 12 (80%); 0.0418: 9 (60%); 0.0466: 6 (40%); 0.0625: 3 (20%) | 0.0328: 3 (20%); 0.0418: 6 (40%); 0.0466: 9 (60%); 0.0625: 12 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0644, -0.057, -0.0479, -0.0364 | -0.0644: 12 (80%); -0.057: 9 (60%); -0.0479: 6 (40%); -0.0364: 3 (20%) | -0.0644: 3 (20%); -0.057: 6 (40%); -0.0479: 9 (60%); -0.0364: 12 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 8.6 | 0: 15 (100%); 8.6: 3 (20%) | 0: 10 (67%); 8.6: 12 (80%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.1176, 0.1434, 0.1655, 0.2444 | 0.1176: 12 (80%); 0.1434: 9 (60%); 0.1655: 6 (40%); 0.2444: 3 (20%) | 0.1176: 3 (20%); 0.1434: 6 (40%); 0.1655: 9 (60%); 0.2444: 12 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 70.12, 80.06, 90.5, 93.24 | 70.12: 12 (80%); 80.06: 9 (60%); 90.5: 6 (40%); 93.24: 3 (20%) | 70.12: 3 (20%); 80.06: 6 (40%); 90.5: 9 (60%); 93.24: 12 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -20.3895, -11.5718, -7.3965, -6.3155 | -20.3895: 12 (80%); -11.5718: 9 (60%); -7.3965: 6 (40%); -6.3155: 3 (20%) | -20.3895: 3 (20%); -11.5718: 6 (40%); -7.3965: 9 (60%); -6.3155: 12 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 10.692, 12.986, 16.4, 20.202 | 10.692: 12 (80%); 12.986: 9 (60%); 16.4: 6 (40%); 20.202: 3 (20%) | 10.692: 3 (20%); 12.986: 6 (40%); 16.4: 9 (60%); 20.202: 12 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 10.28, 12.994, 15.694, 19.27 | 10.28: 12 (80%); 12.994: 9 (60%); 15.694: 6 (40%); 19.27: 3 (20%) | 10.28: 3 (20%); 12.994: 6 (40%); 15.694: 9 (60%); 19.27: 12 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 12.884, 15.536, 23.26, 32.312 | 12.884: 12 (80%); 15.536: 9 (60%); 23.26: 6 (40%); 32.312: 3 (20%) | 12.884: 3 (20%); 15.536: 6 (40%); 23.26: 9 (60%); 32.312: 12 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 12.002, 19.078, 29.37, 34.144 | 12.002: 12 (80%); 19.078: 9 (60%); 29.37: 6 (40%); 34.144: 3 (20%) | 12.002: 3 (20%); 19.078: 6 (40%); 29.37: 9 (60%); 34.144: 12 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4.8, 9.2, 12.4, 15.4 | 4.8: 12 (80%); 9.2: 9 (60%); 12.4: 6 (40%); 15.4: 3 (20%) | 4.8: 3 (20%); 9.2: 6 (40%); 12.4: 9 (60%); 15.4: 12 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 7, 9.6, 14, 16 | 7: 13 (87%); 9.6: 9 (60%); 14: 7 (47%); 16: 5 (33%) | 7: 5 (33%); 9.6: 6 (40%); 14: 10 (67%); 16: 13 (87%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 36.368, 41.84, 43.612, 46.978 | 36.368: 12 (80%); 41.84: 9 (60%); 43.612: 6 (40%); 46.978: 3 (20%) | 36.368: 3 (20%); 41.84: 6 (40%); 43.612: 9 (60%); 46.978: 12 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.3207, 0.5278, 0.75, 0.8334 | 0.3207: 12 (80%); 0.5278: 9 (60%); 0.75: 6 (40%); 0.8334: 3 (20%) | 0.3207: 3 (20%); 0.5278: 6 (40%); 0.75: 9 (60%); 0.8334: 12 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.372, 18.434, 19.738, 22.354 | 16.372: 12 (80%); 18.434: 9 (60%); 19.738: 6 (40%); 22.354: 3 (20%) | 16.372: 3 (20%); 18.434: 6 (40%); 19.738: 9 (60%); 22.354: 12 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 16.372, 18.434, 19.738, 22.354 | 16.372: 12 (80%); 18.434: 9 (60%); 19.738: 6 (40%); 22.354: 3 (20%) | 16.372: 3 (20%); 18.434: 6 (40%); 19.738: 9 (60%); 22.354: 12 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8598, 0.92, 0.9398, 0.9558 | 0.8598: 12 (80%); 0.92: 9 (60%); 0.9398: 6 (40%); 0.9558: 3 (20%) | 0.8598: 3 (20%); 0.92: 6 (40%); 0.9398: 9 (60%); 0.9558: 12 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.824, 1.026, 1.382, 1.668 | 0.824: 12 (80%); 1.026: 9 (60%); 1.382: 6 (40%); 1.668: 3 (20%) | 0.824: 3 (20%); 1.026: 6 (40%); 1.382: 9 (60%); 1.668: 12 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.006, 0.0385, 0.0649, 0.0863 | 0.006: 12 (80%); 0.0385: 9 (60%); 0.0649: 6 (40%); 0.0863: 3 (20%) | 0.006: 3 (20%); 0.0385: 6 (40%); 0.0649: 9 (60%); 0.0863: 12 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 63.409, 100.1967, 130.5336, 212.3508 | 63.409: 12 (80%); 100.1967: 9 (60%); 130.5336: 6 (40%); 212.3508: 3 (20%) | 63.409: 3 (20%); 100.1967: 6 (40%); 130.5336: 9 (60%); 212.3508: 12 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 60.3538, 92.8199, 121.6253, 194.7575 | 60.3538: 12 (80%); 92.8199: 9 (60%); 121.6253: 6 (40%); 194.7575: 3 (20%) | 60.3538: 3 (20%); 92.8199: 6 (40%); 121.6253: 9 (60%); 194.7575: 12 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 56.3937, 75.5479, 115.8708, 177.1642 | 56.3937: 12 (80%); 75.5479: 9 (60%); 115.8708: 6 (40%); 177.1642: 3 (20%) | 56.3937: 3 (20%); 75.5479: 6 (40%); 115.8708: 9 (60%); 177.1642: 12 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 66.4641, 106.1769, 136.5009, 229.9442 | 66.4641: 12 (80%); 106.1769: 9 (60%); 136.5009: 6 (40%); 229.9442: 3 (20%) | 66.4641: 3 (20%); 106.1769: 6 (40%); 136.5009: 9 (60%); 229.9442: 12 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 69.5193, 112.1571, 142.4171, 247.5374 | 69.5193: 12 (80%); 112.1571: 9 (60%); 142.4171: 6 (40%); 247.5374: 3 (20%) | 69.5193: 3 (20%); 112.1571: 6 (40%); 142.4171: 9 (60%); 247.5374: 12 (80%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 15 (100%) | 0: 14 (93%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1221, -0.0807, -0.0707, -0.0573 | -0.1221: 12 (80%); -0.0807: 9 (60%); -0.0707: 6 (40%); -0.0573: 3 (20%) | -0.1221: 3 (20%); -0.0807: 6 (40%); -0.0707: 9 (60%); -0.0573: 12 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -87.254, -83.732, -77.2, -75.686 | -87.254: 12 (80%); -83.732: 9 (60%); -77.2: 6 (40%); -75.686: 3 (20%) | -87.254: 3 (20%); -83.732: 6 (40%); -77.2: 9 (60%); -75.686: 12 (80%) | OFFLINE |
| year_low | backtest/signals/technical.py | 100.0% | 46.212, 99.072, 122.732, 155.44 | 46.212: 12 (80%); 99.072: 9 (60%); 122.732: 6 (40%); 155.44: 3 (20%) | 46.212: 3 (20%); 99.072: 6 (40%); 122.732: 9 (60%); 155.44: 12 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 7.1% |
| 8k_item_5_02_filed_within_7d | 7.1% |
| above_avwap_20low | 73.3% |
| above_avwap_50low | 46.7% |
| above_cam_r3 | 40.0% |
| above_cam_r4 | 13.3% |
| above_cpr | 33.3% |
| above_pivot | 53.3% |
| above_prev_high | 13.3% |
| above_prev_low | 73.3% |
| above_r1 | 13.3% |
| above_wood_p | 26.7% |
| ad_rising | 40.0% |
| adx_cross_up_20 | 6.7% |
| adx_trending | 20.0% |
| ao_positive | 6.7% |
| at_key_fib | 13.3% |
| at_key_fib_wide | 20.0% |
| avwap_20high_loss_recent_3d | 13.3% |
| avwap_20low_loss_recent_3d | 18.2% |
| avwap_20low_reclaim_recent_3d | 45.5% |
| avwap_50low_loss_recent_3d | 8.3% |
| avwap_50low_reclaim_recent_3d | 25.0% |
| bb_10_20_above_mid | 6.7% |
| bb_10_20_expanding | 60.0% |
| bb_10_20_pctb_lt_05 | 6.7% |
| bb_10_20_pctb_lt_1 | 13.3% |
| bb_10_20_pctb_lt_15 | 40.0% |
| bb_10_20_pctb_lt_2 | 53.3% |
| bb_10_20_pctb_lt_25 | 66.7% |
| bb_10_20_reclaim_from_lower_recent_3d | 53.3% |
| bb_10_20_squeeze | 26.7% |
| bb_10_20_touch_lower | 13.3% |
| bb_20_15_expanding | 73.3% |
| bb_20_15_pctb_lt_05 | 73.3% |
| bb_20_15_pctb_lt_1 | 93.3% |
| bb_20_15_pctb_lt_15 | 93.3% |
| bb_20_15_pctb_lt_2 | 93.3% |
| bb_20_15_pctb_lt_25 | 93.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 20.0% |
| bb_20_15_squeeze | 6.7% |
| bb_20_15_touch_lower | 66.7% |
| bb_20_20_expanding | 73.3% |
| bb_20_20_pctb_lt_05 | 40.0% |
| bb_20_20_pctb_lt_1 | 46.7% |
| bb_20_20_pctb_lt_15 | 66.7% |
| bb_20_20_pctb_lt_2 | 93.3% |
| bb_20_20_pctb_lt_25 | 93.3% |
| bb_20_20_reclaim_from_lower_recent_3d | 40.0% |
| bb_20_20_squeeze | 6.7% |
| bb_20_20_touch_lower | 33.3% |
| below_avwap_20low | 26.7% |
| below_avwap_50low | 53.3% |
| below_cam_s3 | 26.7% |
| below_cam_s4 | 26.7% |
| below_cpr | 46.7% |
| below_ema_20_break_recent_5d | 13.3% |
| below_ema_21_break_recent_5d | 13.3% |
| below_ema_50_break_recent_5d | 33.3% |
| below_ema_9_break_recent_5d | 20.0% |
| below_prev_high | 86.7% |
| below_prev_low | 26.7% |
| below_prev_low_clearance_atr_05 | 13.3% |
| below_s1 | 26.7% |
| below_s2 | 13.3% |
| below_sma_200 | 6.7% |
| below_sma_9 | 93.3% |
| bullish_engulfing | 6.7% |
| chandelier_long_bullish | 6.7% |
| chandelier_long_flip_dn | 6.7% |
| close_in_bottom_40pct_of_range | 13.3% |
| close_in_top_40pct_of_range | 60.0% |
| cmf_cross_dn | 6.7% |
| cmf_cross_up | 6.7% |
| cmf_negative | 80.0% |
| cmf_positive | 20.0% |
| cpr_narrow | 93.3% |
| cpr_narrow_tight | 33.3% |
| dc10_breakout_dn | 13.3% |
| dc10_breakout_dn_1pct | 20.0% |
| dc10_strong_breakout_dn | 6.7% |
| dc20_breakout_dn | 13.3% |
| dc20_support_break_retest_strong | 53.3% |
| defensive_leadership | 66.7% |
| doji | 6.7% |
| double_bottom_detected | 20.0% |
| dpi_elevated | 38.5% |
| drying_volume_on_up_turn | 40.0% |
| ema_20_50_bearish | 53.3% |
| ema_20_50_bullish | 46.7% |
| ema_9_21_death_cross | 6.7% |
| gap_dn_1_5pct | 26.7% |
| gap_dn_2pct | 26.7% |
| head_shoulders_top_detected | 20.0% |
| house_cluster_buy | 7.1% |
| house_cluster_sell | 7.1% |
| hull_bearish | 93.3% |
| hull_bullish | 6.7% |
| ichi_below_cloud | 93.3% |
| ichi_below_cloud_break_recent_5d | 60.0% |
| ichi_cloud_thick | 80.0% |
| ichi_tk_bearish | 93.3% |
| ichi_tk_bullish | 6.7% |
| ichi_tk_cross_dn | 6.7% |
| ichi_weekly_above_cloud | 85.7% |
| ichi_weekly_in_cloud | 14.3% |
| inside_bar | 33.3% |
| inside_cpr | 20.0% |
| inside_kc | 66.7% |
| institutional_buy | 86.7% |
| institutional_persistence_growing | 53.8% |
| institutional_persistence_strong | 53.8% |
| institutional_strong_buy | 73.3% |
| is_friday | 20.0% |
| is_halloween_period | 60.0% |
| is_january | 13.3% |
| is_january_extended | 13.3% |
| is_monday | 6.7% |
| is_pre_holiday | 6.7% |
| is_summer_period | 40.0% |
| is_totm_window | 13.3% |
| is_week_open | 6.7% |
| kc_touch_lower | 46.7% |
| macd_8_21_5_bearish | 93.3% |
| macd_8_21_5_bullish | 6.7% |
| mfi_broad_oversold | 33.3% |
| mfi_oversold | 20.0% |
| monthly_above_sma_6 | 21.4% |
| monthly_bias_bull | 21.4% |
| monthly_momentum_pos | 78.6% |
| morning_star | 6.7% |
| near_avwap_20high_atr_05x | 13.3% |
| near_avwap_20high_atr_10x | 13.3% |
| near_avwap_20high_atr_15x | 26.7% |
| near_avwap_20high_atr_20x | 60.0% |
| near_avwap_20low_atr_05x | 72.7% |
| near_avwap_20low_atr_10x | 90.9% |
| near_avwap_20low_atr_15x | 90.9% |
| near_avwap_252low_atr_15x | 7.1% |
| near_avwap_252low_atr_20x | 28.6% |
| near_avwap_50low_atr_05x | 33.3% |
| near_avwap_50low_atr_10x | 41.7% |
| near_avwap_50low_atr_15x | 58.3% |
| near_avwap_50low_atr_20x | 83.3% |
| near_cam_r3 | 33.3% |
| near_fib_618 | 13.3% |
| near_fib_786 | 6.7% |
| near_pivot | 26.7% |
| near_prev_close | 13.3% |
| near_prev_high | 6.7% |
| near_r1 | 6.7% |
| near_r1_wide | 40.0% |
| near_r2 | 6.7% |
| near_r2_wide | 20.0% |
| near_s1_wide | 20.0% |
| near_s2 | 6.7% |
| near_s2_wide | 20.0% |
| near_wood_r1 | 6.7% |
| near_wood_s1 | 33.3% |
| news_uses_polygon_score | 13.3% |
| obv_diverge_bull | 6.7% |
| obv_falling | 93.3% |
| obv_rising | 6.7% |
| pead_negative_surprise | 8.3% |
| pead_positive_surprise | 58.3% |
| po3_accumulation_active | 20.0% |
| po3_bullish | 20.0% |
| po3_manipulation_sweep_down | 6.7% |
| po3_sweep_above_prior_high | 33.3% |
| po3_sweep_below_prior_low | 40.0% |
| pre_fomc_d0 | 6.7% |
| pre_fomc_window | 6.7% |
| price_above_dema | 6.7% |
| price_above_ema_200_break_recent_5d | 13.3% |
| price_above_hull | 26.7% |
| price_above_sma_200 | 93.3% |
| price_above_tema | 26.7% |
| price_below_dema | 93.3% |
| price_below_hull | 73.3% |
| price_below_tema | 73.3% |
| psar_bullish | 6.7% |
| r1_break_retest_long | 6.7% |
| risk_off_regime_bond_signal | 40.0% |
| risk_off_regime_bond_signal_strong | 20.0% |
| risk_off_regime_gold_signal | 40.0% |
| risk_on_regime_bond_signal | 33.3% |
| risk_on_regime_bond_signal_strong | 6.7% |
| rsi_14_cross_up_oversold_recent_3d | 20.0% |
| rsi_14_oversold | 20.0% |
| rsi_14_rising | 73.3% |
| rsi_21_rising | 73.3% |
| rsi_2_bullish | 20.0% |
| rsi_2_cross_dn_overbought_recent_3d | 13.3% |
| rsi_2_cross_up_extreme_os_recent_3d | 66.7% |
| rsi_2_cross_up_oversold_recent_3d | 60.0% |
| rsi_2_extreme_os | 26.7% |
| rsi_2_oversold | 40.0% |
| rsi_2_rising | 73.3% |
| rsi_9_cross_up_extreme_os_recent_3d | 13.3% |
| rsi_9_cross_up_oversold_recent_3d | 40.0% |
| rsi_9_oversold | 33.3% |
| rsi_9_rising | 73.3% |
| s1_break_retest_short | 86.7% |
| sma_20_50_bullish | 46.7% |
| sma_9_21_bullish | 6.7% |
| smc_bos_bullish | 46.7% |
| smc_bos_retest_long | 6.7% |
| smc_breaker_block_bullish | 53.3% |
| smc_choch_bullish | 6.7% |
| smc_fvg_bearish_active | 80.0% |
| smc_fvg_retest_short_zone | 13.3% |
| smc_inverse_fvg_bullish | 13.3% |
| smc_ob_bullish_active | 93.3% |
| smc_ote_long_zone | 20.0% |
| smc_ote_short_zone | 20.0% |
| squeeze_in | 13.3% |
| stoch_bearish_cross | 6.7% |
| stoch_broad_oversold | 86.7% |
| stoch_bullish_cross | 26.7% |
| stoch_oversold | 80.0% |
| stochrsi_cross_dn | 6.7% |
| stochrsi_cross_up | 60.0% |
| stochrsi_overbought | 6.7% |
| stochrsi_oversold | 40.0% |
| support_break_retest | 86.7% |
| triangle_ascending_detected | 6.7% |
| triangle_descending_detected | 20.0% |
| usd_strengthening | 6.7% |
| usd_weakening | 13.3% |
| vix_band_high | 53.3% |
| vix_band_low | 20.0% |
| vix_band_mid | 26.7% |
| vol_above_avg | 60.0% |
| vol_below_avg | 40.0% |
| vol_spike_12x | 53.3% |
| vol_spike_15x | 33.3% |
| vol_spike_17x | 13.3% |
| vol_spike_2x | 13.3% |
| vol_spike_2x_on_down_day_recent_3d | 26.7% |
| vol_spike_3x | 6.7% |
| vp_below_value_area | 53.3% |
| vp_close_above_poc | 13.3% |
| vp_close_below_poc | 86.7% |
| vp_in_value_area | 46.7% |
| weekly_above_ema_20 | 20.0% |
| weekly_bias_bear | 80.0% |
| weekly_momentum_pos | 6.7% |
| williams_r_oversold | 53.3% |
| williams_r_rising | 80.0% |
| within_pead_window | 33.3% |
| xs_avoid_high_ivol | 50.0% |
| xs_avoid_high_max | 57.1% |
| xs_high_beta_decile | 21.4% |
| xs_low_beta_bottom_quintile | 21.4% |
| xs_momentum_top_decile | 64.3% |
| xs_quality_bottom_quintile | 25.0% |
| xs_quality_top_quintile | 37.5% |
| xs_quality_top_tercile | 75.0% |
| yoy_surprise_high | 78.6% |
| yoy_surprise_negative | 14.3% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 86.7% |
| committed_growth_holders | 86.7% |
| cot_rut_commercials_pctile_3y | 73.3% |
| cot_rut_mmoney_pctile_3y | 73.3% |
| days_to_cover | 93.3% |
| days_to_next_holiday | 73.3% |
| dpi_30d_avg | 86.7% |
| dpi_recent | 86.7% |
| earnings_announcement_return | 80.0% |
| earnings_eps_yoy_growth | 93.3% |
| gov_contracts_4q_sum | 26.7% |
| gov_contracts_last_qtr_amount | 26.7% |
| gov_contracts_qoq_growth | 26.7% |
| house_buy_count_90d | 93.3% |
| house_net_buy_90d | 93.3% |
| house_sell_count_90d | 93.3% |
| lobbying_amount_1y | 73.3% |
| lobbying_amount_q | 73.3% |
| lobbying_amount_yoy | 73.3% |
| monthly_momentum_6m | 93.3% |
| naked_poc_nearest_distance_pct | 93.3% |
| otc_short_ratio_recent | 86.7% |
| otc_volume_recent | 86.7% |
| pair_half_life | 86.7% |
| pair_max_abs_zscore | 86.7% |
| pair_zscore_signed | 86.7% |
| pct_from_avwap_20low | 73.3% |
| pct_from_avwap_252low | 93.3% |
| pct_from_avwap_50low | 80.0% |
| persistent_holders_4q | 86.7% |
| persistent_holders_8q | 86.7% |
| search_volume_index_recent | 66.7% |
| search_volume_observations | 66.7% |
| search_volume_zscore_30d | 66.7% |
| short_interest_observations | 93.3% |
| short_interest_pct | 86.7% |
| total_active_holders | 86.7% |
| triangle_breakdown_pct | 20.0% |
| xs_beta | 93.3% |
| xs_beta_decile | 93.3% |
| xs_ivol | 93.3% |
| xs_ivol_decile | 93.3% |
| xs_max_anomaly | 93.3% |
| xs_max_anomaly_decile | 93.3% |
| xs_momentum_12_1 | 93.3% |
| xs_momentum_decile | 93.3% |
| xs_quality_decile | 53.3% |
| xs_quality_gross_profitability | 53.3% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (1.0), `avwap_20low` (0.996), `avwap_252low` (0.991), `avwap_50low` (0.989), `bb_10_20_lower` (0.996), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.996), `bb_20_15_lower` (1.0), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.996), `bb_20_20_lower` (1.0), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.996), `cam_r1` (1.0), `cam_r2` (1.0), `cam_r3` (1.0), `cam_r4` (1.0), `cam_s1` (1.0), `cam_s2` (1.0), `cam_s3` (1.0), `cam_s4` (1.0), `chandelier_long_value` (0.996), `chandelier_short_value` (0.996), `cpr_bottom` (1.0), `cpr_top` (1.0), `days_since_inclusion` (1.0), `days_to_rebalance` (1.0), `dc10_lower` (0.996), `dc10_mid` (0.996), `dc10_upper` (0.996), `dc20_lower` (0.996), `dc20_mid` (0.996), `dc20_upper` (0.996), `dema` (1.0), `double_bottom_neckline` (1.0), `double_bottom_trough` (1.0), `entry_stop_long` (0.996), `entry_stop_short` (1.0), `fib_236` (0.996), `fib_382` (0.996), `fib_500` (0.996), `fib_618` (1.0), `fib_786` (1.0), `fib_ext_127` (0.993), `fib_ext_162` (0.993), `head_shoulders_magnitude_pct` (-1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (1.0), `ichi_kijun` (0.996), `ichi_senkou_a` (0.996), `ichi_senkou_b` (1.0), `ichi_tenkan` (0.996), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_height_pct` (1.0), `inverted_cup_handle_rim_low` (1.0), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.996), `monthly_sma_12` (0.991), `monthly_sma_6` (1.0), `pivot` (1.0), `prev_close` (1.0), `prev_high` (1.0), `prev_low` (1.0), `psar_value` (0.993), `r1` (1.0), `r2` (1.0), `r3` (1.0), `s1` (1.0), `s2` (1.0), `s3` (1.0), `supertrend_value` (0.996), `swing_high` (0.993), `swing_low` (0.996), `tema` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (1.0), `vp_value_area_low` (0.996), `weekly_close` (0.996), `weekly_ema_10` (1.0), `weekly_ema_20` (1.0), `wood_p` (1.0), `wood_r1` (0.996), `wood_r2` (0.996), `wood_s1` (1.0), `wood_s2` (1.0), `year_high` (0.993)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
