# Table A - rsi21_slow

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** mean_reversion | **status:** NOT-STARTED | **R5 fires:** 9 | **surviving fires (T1):** 9 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_sma_50  <- backtest/signals/screener.py
       knobs P1.1-P1.1 (band rows in Table A)
P2  price_above_sma_50  <- backtest/signals/screener.py
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  rsi_21 < 40   [EXISTING-THRESHOLD]
P4  rsi_21 > 60   [EXISTING-THRESHOLD]
P5  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_rsi21_slow (docstring and return dropped):

```python
fl = s.get('rsi_21', 50) < 40 and s.get('price_above_sma_50')
fs = (s.get('rsi_21', 50) > 60 and s.get('below_sma_50')) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | below_sma_50 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | sma span - backtest/signals/technical.py sma block | 50 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P2 | PRODUCER | price_above_sma_50 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | sma span - backtest/signals/technical.py sma block | 50 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P3 | STRATEGY | rsi_21 `< 40` [EXISTING-THRESHOLD] | `< 40` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4 | STRATEGY | rsi_21 `> 60` [EXISTING-THRESHOLD] | `> 60` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_21 | backtest/signals/screener.py | `< 40` | 100.0% | TIGHTER = LOWER the ceiling: 14.78 -> 2 (22%); 24.448 -> 4 (44%); 37.264 -> 5 (56%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_21 | backtest/signals/screener.py | `> 60` | 100.0% | TIGHTER = RAISE the floor: (no QUANTS level sits tighter than production - band at T3) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 28.742, 34.926, 58.022, 72.736 | 28.742: 7 (78%); 34.926: 5 (56%); 58.022: 4 (44%); 72.736: 2 (22%) | 28.742: 2 (22%); 34.926: 4 (44%); 58.022: 5 (56%); 72.736: 7 (78%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 12.424, 20.33, 51.602, 55.846 | 12.424: 7 (78%); 20.33: 5 (56%); 51.602: 4 (44%); 55.846: 2 (22%) | 12.424: 2 (22%); 20.33: 4 (44%); 51.602: 5 (56%); 55.846: 7 (78%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 14.51, 16.148, 24.308, 27.758 | 14.51: 7 (78%); 16.148: 5 (56%); 24.308: 4 (44%); 27.758: 2 (22%) | 14.51: 2 (22%); 16.148: 4 (44%); 24.308: 5 (56%); 27.758: 7 (78%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -0.0002, 0.0193, 0.06, 0.1612 | -0.0002: 7 (78%); 0.0193: 5 (56%); 0.06: 4 (44%); 0.1612: 2 (22%) | -0.0002: 2 (22%); 0.0193: 4 (44%); 0.06: 5 (56%); 0.1612: 7 (78%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 0.0652, 0.1441, 0.2107, 0.2522 | 0.0652: 7 (78%); 0.1441: 5 (56%); 0.2107: 4 (44%); 0.2522: 2 (22%) | 0.0652: 2 (22%); 0.1441: 4 (44%); 0.2107: 5 (56%); 0.2522: 7 (78%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 0.0652, 0.1441, 0.2107, 0.2522 | 0.0652: 7 (78%); 0.1441: 5 (56%); 0.2107: 4 (44%); 0.2522: 2 (22%) | 0.0652: 2 (22%); 0.1441: 4 (44%); 0.2107: 5 (56%); 0.2522: 7 (78%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 0.8328, 10.8314, 59.0602, 71.8762 | 0.8328: 7 (78%); 10.8314: 5 (56%); 59.0602: 4 (44%); 71.8762: 2 (22%) | 0.8328: 2 (22%); 10.8314: 4 (44%); 59.0602: 5 (56%); 71.8762: 7 (78%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0198, 0.0822, 0.6761, 1.0677 | 0.0198: 7 (78%); 0.0822: 5 (56%); 0.6761: 4 (44%); 1.0677: 2 (22%) | 0.0198: 2 (22%); 0.0822: 4 (44%); 0.6761: 5 (56%); 1.0677: 7 (78%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.4941, 0.5945, 0.6332, 0.7893 | 0.4941: 7 (78%); 0.5945: 5 (56%); 0.6332: 4 (44%); 0.7893: 2 (22%) | 0.4941: 2 (22%); 0.5945: 4 (44%); 0.6332: 5 (56%); 0.7893: 7 (78%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0277, 0.0759, 0.637, 0.8702 | 0.0277: 7 (78%); 0.0759: 5 (56%); 0.637: 4 (44%); 0.8702: 2 (22%) | 0.0277: 2 (22%); 0.0759: 4 (44%); 0.637: 5 (56%); 0.8702: 7 (78%) | OFFLINE |
| bb_20_15_lower | (not found by literal grep) | 100.0% | 0.055, 0.1019, 16.4081, 28.9113 | 0.055: 7 (78%); 0.1019: 5 (56%); 16.4081: 4 (44%); 28.9113: 2 (22%) | 0.055: 2 (22%); 0.1019: 4 (44%); 16.4081: 5 (56%); 28.9113: 7 (78%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.5954, 0.6984, 0.86, 0.9094 | 0.5954: 7 (78%); 0.6984: 5 (56%); 0.86: 4 (44%); 0.9094: 2 (22%) | 0.5954: 2 (22%); 0.6984: 4 (44%); 0.86: 5 (56%); 0.9094: 7 (78%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.037, 0.1012, 0.8493, 1.1603 | 0.037: 7 (78%); 0.1012: 5 (56%); 0.8493: 4 (44%); 1.1603: 2 (22%) | 0.037: 2 (22%); 0.1012: 4 (44%); 0.8493: 5 (56%); 1.1603: 7 (78%) | OFFLINE |
| bb_20_20_lower | backtest/signals/technical.py | 100.0% | 0.0431, 0.0854, 16.2791, 28.7992 | 0.0431: 7 (78%); 0.0854: 5 (56%); 16.2791: 4 (44%); 28.7992: 2 (22%) | 0.0431: 2 (22%); 0.0854: 4 (44%); 16.2791: 5 (56%); 28.7992: 7 (78%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.5716, 0.6488, 0.77, 0.807 | 0.5716: 7 (78%); 0.6488: 5 (56%); 0.77: 4 (44%); 0.807: 2 (22%) | 0.5716: 2 (22%); 0.6488: 4 (44%); 0.77: 5 (56%); 0.807: 7 (78%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0543, -0.0435, -0.0255, -0.018 | -0.0543: 7 (78%); -0.0435: 5 (56%); -0.0255: 4 (44%); -0.018: 2 (22%) | -0.0543: 2 (22%); -0.0435: 4 (44%); -0.0255: 5 (56%); -0.018: 7 (78%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1459, 0.1667, 0.201, 0.2284 | 0.1459: 7 (78%); 0.1667: 5 (56%); 0.201: 4 (44%); 0.2284: 2 (22%) | 0.1459: 2 (22%); 0.1667: 4 (44%); 0.201: 5 (56%); 0.2284: 7 (78%) | OFFLINE |
| chandelier_long_value | backtest/signals/technical.py | 100.0% | -1.1041, -0.0311, 15.5796, 28.5908 | -1.1041: 7 (78%); -0.0311: 5 (56%); 15.5796: 4 (44%); 28.5908: 2 (22%) | -1.1041: 2 (22%); -0.0311: 4 (44%); 15.5796: 5 (56%); 28.5908: 7 (78%) | OFFLINE |
| chandelier_short_value | backtest/signals/technical.py | 100.0% | 0.864, 1.8066, 17.6365, 30.2759 | 0.864: 7 (78%); 1.8066: 5 (56%); 17.6365: 4 (44%); 30.2759: 2 (22%) | 0.864: 2 (22%); 1.8066: 4 (44%); 17.6365: 5 (56%); 30.2759: 7 (78%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1464, -0.06, -0.0079, 0 | -0.1464: 7 (78%); -0.06: 5 (56%); -0.0079: 4 (44%); 0: 4 (44%) | -0.1464: 2 (22%); -0.06: 4 (44%); -0.0079: 5 (56%); 0: 8 (89%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 0.2, 1, 2.8 | 0: 9 (100%); 0.2: 5 (56%); 1: 5 (56%); 2.8: 2 (22%) | 0: 4 (44%); 0.2: 4 (44%); 1: 6 (67%); 2.8: 7 (78%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2302, -0.1876, -0.153, -0.142 | -0.2302: 7 (78%); -0.1876: 5 (56%); -0.153: 4 (44%); -0.142: 2 (22%) | -0.2302: 2 (22%); -0.1876: 4 (44%); -0.153: 5 (56%); -0.142: 7 (78%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5654, 0.6718, 0.7538, 0.7667 | 0.5654: 7 (78%); 0.6718: 5 (56%); 0.7538: 4 (44%); 0.7667: 2 (22%) | 0.5654: 2 (22%); 0.6718: 4 (44%); 0.7538: 5 (56%); 0.7667: 7 (78%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3115, 0.3961, 0.4269, 0.5885 | 0.3115: 7 (78%); 0.3961: 5 (56%); 0.4269: 4 (44%); 0.5885: 2 (22%) | 0.3115: 2 (22%); 0.3961: 4 (44%); 0.4269: 5 (56%); 0.5885: 7 (78%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1133, 0.0798, 0.0997, 0.2135 | -0.1133: 7 (78%); 0.0798: 5 (56%); 0.0997: 4 (44%); 0.2135: 2 (22%) | -0.1133: 2 (22%); 0.0798: 4 (44%); 0.0997: 5 (56%); 0.2135: 7 (78%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.5, 0.6436, 0.782 | 0.2692: 7 (78%); 0.5: 5 (56%); 0.6436: 4 (44%); 0.782: 2 (22%) | 0.2692: 2 (22%); 0.5: 4 (44%); 0.6436: 5 (56%); 0.782: 7 (78%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0641, 0.1154, 0.2385, 0.4359 | 0.0641: 7 (78%); 0.1154: 5 (56%); 0.2385: 4 (44%); 0.4359: 2 (22%) | 0.0641: 2 (22%); 0.1154: 4 (44%); 0.2385: 5 (56%); 0.4359: 7 (78%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5653, -0.5042, -0.3729, -0.1211 | -0.5653: 7 (78%); -0.5042: 5 (56%); -0.3729: 4 (44%); -0.1211: 2 (22%) | -0.5653: 2 (22%); -0.5042: 4 (44%); -0.3729: 5 (56%); -0.1211: 7 (78%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2513, 0.3141, 0.5039, 0.7231 | 0.2513: 7 (78%); 0.3141: 5 (56%); 0.5039: 4 (44%); 0.7231: 2 (22%) | 0.2513: 2 (22%); 0.3141: 4 (44%); 0.5039: 5 (56%); 0.7231: 7 (78%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3731, 0.5692, 0.8256, 0.9141 | 0.3731: 7 (78%); 0.5692: 5 (56%); 0.8256: 4 (44%); 0.9141: 2 (22%) | 0.3731: 2 (22%); 0.5692: 4 (44%); 0.8256: 5 (56%); 0.9141: 7 (78%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.054, -0.0449, -0.0137, 0 | -0.054: 7 (78%); -0.0449: 5 (56%); -0.0137: 4 (44%); 0: 3 (33%) | -0.054: 2 (22%); -0.0449: 4 (44%); -0.0137: 5 (56%); 0: 9 (100%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5308, 0.7898, 0.8, 0.9962 | 0.5308: 7 (78%); 0.7898: 5 (56%); 0.8: 4 (44%); 0.9962: 2 (22%) | 0.5308: 2 (22%); 0.7898: 4 (44%); 0.8: 5 (56%); 0.9962: 7 (78%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1961, 0.3193, 0.7038, 0.8436 | 0.1961: 7 (78%); 0.3193: 5 (56%); 0.7038: 4 (44%); 0.8436: 2 (22%) | 0.1961: 2 (22%); 0.3193: 4 (44%); 0.7038: 5 (56%); 0.8436: 7 (78%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0512, -0.0274, -0.0214, 0.0528 | -0.0512: 7 (78%); -0.0274: 5 (56%); -0.0214: 4 (44%); 0.0528: 2 (22%) | -0.0512: 2 (22%); -0.0274: 4 (44%); -0.0214: 5 (56%); 0.0528: 7 (78%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2321, 0.3402, 0.4157, 0.6295 | 0.2321: 7 (78%); 0.3402: 5 (56%); 0.4157: 4 (44%); 0.6295: 2 (22%) | 0.2321: 2 (22%); 0.3402: 4 (44%); 0.4157: 5 (56%); 0.6295: 7 (78%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.6064, 0.6918, 0.791, 0.9084 | 0.6064: 7 (78%); 0.6918: 5 (56%); 0.791: 4 (44%); 0.9084: 2 (22%) | 0.6064: 2 (22%); 0.6918: 4 (44%); 0.791: 5 (56%); 0.9084: 7 (78%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0109, 0.0737, 0.1199 | -0.0812: 9 (100%); -0.0109: 5 (56%); 0.0737: 4 (44%); 0.1199: 2 (22%) | -0.0812: 3 (33%); -0.0109: 4 (44%); 0.0737: 5 (56%); 0.1199: 7 (78%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1671, -0.0646, 0.0294, 0.0701 | -0.1671: 7 (78%); -0.0646: 5 (56%); 0.0294: 4 (44%); 0.0701: 2 (22%) | -0.1671: 2 (22%); -0.0646: 4 (44%); 0.0294: 5 (56%); 0.0701: 7 (78%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1115, 0.1859, 0.5808, 0.8795 | 0.1115: 7 (78%); 0.1859: 5 (56%); 0.5808: 4 (44%); 0.8795: 2 (22%) | 0.1115: 2 (22%); 0.1859: 4 (44%); 0.5808: 5 (56%); 0.8795: 7 (78%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.5551, 0.6141, 0.7679, 0.859 | 0.5551: 7 (78%); 0.6141: 5 (56%); 0.7679: 4 (44%); 0.859: 2 (22%) | 0.5551: 2 (22%); 0.6141: 4 (44%); 0.7679: 5 (56%); 0.859: 7 (78%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0009, 0.0014, 0.0044, 0.006 | 0.0009: 7 (78%); 0.0014: 5 (56%); 0.0044: 4 (44%); 0.006: 2 (22%) | 0.0009: 2 (22%); 0.0014: 4 (44%); 0.0044: 5 (56%); 0.006: 7 (78%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 0.2726, 0.9164, 2.8647, 11.1721 | 0.2726: 8 (89%); 0.9164: 5 (56%); 2.8647: 4 (44%); 11.1721: 3 (33%) | 0.2726: 3 (33%); 0.9164: 4 (44%); 2.8647: 5 (56%); 11.1721: 8 (89%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 15.6, 19.8, 25.4, 42.8 | 15.6: 7 (78%); 19.8: 5 (56%); 25.4: 4 (44%); 42.8: 2 (22%) | 15.6: 2 (22%); 19.8: 4 (44%); 25.4: 5 (56%); 42.8: 7 (78%) | OFFLINE |
| dema | backtest/signals/technical.py | 100.0% | -0.4767, 0.0135, 15.8303, 29.325 | -0.4767: 7 (78%); 0.0135: 5 (56%); 15.8303: 4 (44%); 29.325: 2 (22%) | -0.4767: 2 (22%); 0.0135: 4 (44%); 15.8303: 5 (56%); 29.325: 7 (78%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0.6, 1.4, 3.8, 4 | 0.6: 7 (78%); 1.4: 5 (56%); 3.8: 4 (44%); 4: 4 (44%) | 0.6: 2 (22%); 1.4: 4 (44%); 3.8: 5 (56%); 4: 9 (100%) | OFFLINE |
| dpi_30d_avg | backtest/signals/congressional_alt_data.py | 100.0% | 0.2303, 0.3354, 0.4203, 0.551 | 0.2303: 7 (78%); 0.3354: 5 (56%); 0.4203: 4 (44%); 0.551: 2 (22%) | 0.2303: 2 (22%); 0.3354: 4 (44%); 0.4203: 5 (56%); 0.551: 7 (78%) | OFFLINE |
| dpi_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.2287, 0.3113, 0.395, 0.6422 | 0.2287: 7 (78%); 0.3113: 5 (56%); 0.395: 4 (44%); 0.6422: 2 (22%) | 0.2287: 2 (22%); 0.3113: 4 (44%); 0.395: 5 (56%); 0.6422: 7 (78%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0209, -0.0123, 0.0011, 0.0139 | -0.0209: 7 (78%); -0.0123: 5 (56%); 0.0011: 4 (44%); 0.0139: 2 (22%) | -0.0209: 2 (22%); -0.0123: 4 (44%); 0.0011: 5 (56%); 0.0139: 7 (78%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6296, 25.2819, 26.3423, 27.6276 | 24.6296: 7 (78%); 25.2819: 5 (56%); 26.3423: 4 (44%); 27.6276: 2 (22%) | 24.6296: 2 (22%); 25.2819: 4 (44%); 26.3423: 5 (56%); 27.6276: 7 (78%) | OFFLINE |
| entry_stop_long | backtest/signals/technical.py | 100.0% | -0.0241, -0.0047, 16.2981, 29.0074 | -0.0241: 7 (78%); -0.0047: 5 (56%); 16.2981: 4 (44%); 29.0074: 2 (22%) | -0.0241: 2 (22%); -0.0047: 4 (44%); 16.2981: 5 (56%); 29.0074: 7 (78%) | OFFLINE |
| entry_stop_short | backtest/signals/technical.py | 100.0% | 0.2614, 0.4873, 17.3443, 29.8723 | 0.2614: 7 (78%); 0.4873: 5 (56%); 17.3443: 4 (44%); 29.8723: 2 (22%) | 0.2614: 2 (22%); 0.4873: 4 (44%); 17.3443: 5 (56%); 29.8723: 7 (78%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -5.2096, -0.8024, -0.2008, 0 | -5.2096: 7 (78%); -0.8024: 5 (56%); -0.2008: 4 (44%); 0: 3 (33%) | -5.2096: 2 (22%); -0.8024: 4 (44%); -0.2008: 5 (56%); 0: 8 (89%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | 0, 0.2008, 0.8024, 5.2096 | 0: 8 (89%); 0.2008: 5 (56%); 0.8024: 4 (44%); 5.2096: 2 (22%) | 0: 3 (33%); 0.2008: 4 (44%); 0.8024: 5 (56%); 5.2096: 7 (78%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0536, -0.0442, -0.0169, 0.012 | -0.0536: 7 (78%); -0.0442: 5 (56%); -0.0169: 4 (44%); 0.012: 2 (22%) | -0.0536: 2 (22%); -0.0442: 4 (44%); -0.0169: 5 (56%); 0.012: 7 (78%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.1767, 8.2617, 8.4033, 8.6913 | 8.1767: 7 (78%); 8.2617: 5 (56%); 8.4033: 4 (44%); 8.6913: 2 (22%) | 8.1767: 2 (22%); 8.2617: 4 (44%); 8.4033: 5 (56%); 8.6913: 7 (78%) | OFFLINE |
| ichi_senkou_a | backtest/signals/technical.py | 100.0% | 0.082, 0.1636, 16.5085, 29.4234 | 0.082: 7 (78%); 0.1636: 5 (56%); 16.5085: 4 (44%); 29.4234: 2 (22%) | 0.082: 2 (22%); 0.1636: 4 (44%); 16.5085: 5 (56%); 29.4234: 7 (78%) | OFFLINE |
| ichi_senkou_b | backtest/signals/technical.py | 100.0% | 23.074, 57.7779, 63.5451, 68.666 | 23.074: 7 (78%); 57.7779: 5 (56%); 63.5451: 4 (44%); 68.666: 2 (22%) | 23.074: 2 (22%); 57.7779: 4 (44%); 63.5451: 5 (56%); 68.666: 7 (78%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 0, 2.2, 11, 60.6 | 0: 9 (100%); 2.2: 5 (56%); 11: 5 (56%); 60.6: 2 (22%) | 0: 4 (44%); 2.2: 4 (44%); 11: 7 (78%); 60.6: 7 (78%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0.6, 3.2, 12, 26.8 | 0.6: 7 (78%); 3.2: 5 (56%); 12: 5 (56%); 26.8: 2 (22%) | 0.6: 2 (22%); 3.2: 4 (44%); 12: 7 (78%); 26.8: 7 (78%) | OFFLINE |
| kc_lower | backtest/signals/technical.py | 100.0% | -0.4354, -0.015, 16.0351, 28.7072 | -0.4354: 7 (78%); -0.015: 5 (56%); 16.0351: 4 (44%); 28.7072: 2 (22%) | -0.4354: 2 (22%); -0.015: 4 (44%); 16.0351: 5 (56%); 28.7072: 7 (78%) | OFFLINE |
| kc_mid | backtest/signals/technical.py | 100.0% | 0.1669, 0.34, 16.9718, 29.3428 | 0.1669: 7 (78%); 0.34: 5 (56%); 16.9718: 4 (44%); 29.3428: 2 (22%) | 0.1669: 2 (22%); 0.34: 4 (44%); 16.9718: 5 (56%); 29.3428: 7 (78%) | OFFLINE |
| kc_upper | backtest/signals/technical.py | 100.0% | 0.5747, 1.2281, 17.7589, 30.1991 | 0.5747: 7 (78%); 1.2281: 5 (56%); 17.7589: 4 (44%); 30.1991: 2 (22%) | 0.5747: 2 (22%); 1.2281: 4 (44%); 17.7589: 5 (56%); 30.1991: 7 (78%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.0055, 0.0283, 0.2245, 0.355 | -0.0055: 7 (78%); 0.0283: 5 (56%); 0.2245: 4 (44%); 0.355: 2 (22%) | -0.0055: 2 (22%); 0.0283: 4 (44%); 0.2245: 5 (56%); 0.355: 7 (78%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -0.7814, -0.4225, -0.0284, 0.0637 | -0.7814: 7 (78%); -0.4225: 5 (56%); -0.0284: 4 (44%); 0.0637: 2 (22%) | -0.7814: 2 (22%); -0.4225: 4 (44%); -0.0284: 5 (56%); 0.0637: 7 (78%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.1365, -0.647, -0.0566, 0.0691 | -1.1365: 7 (78%); -0.647: 5 (56%); -0.0566: 4 (44%); 0.0691: 2 (22%) | -1.1365: 2 (22%); -0.647: 4 (44%); -0.0566: 5 (56%); 0.0691: 7 (78%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.0002, 0.0027, 0.03, 0.0677 | -0.0002: 7 (78%); 0.0027: 5 (56%); 0.03: 4 (44%); 0.0677: 2 (22%) | -0.0002: 2 (22%); 0.0027: 4 (44%); 0.03: 5 (56%); 0.0677: 7 (78%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -0.249, -0.0916, 0.0002, 0.0796 | -0.249: 7 (78%); -0.0916: 5 (56%); 0.0002: 4 (44%); 0.0796: 2 (22%) | -0.249: 2 (22%); -0.0916: 4 (44%); 0.0002: 5 (56%); 0.0796: 7 (78%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -0.3167, -0.1202, 0.0004, 0.0814 | -0.3167: 7 (78%); -0.1202: 5 (56%); 0.0004: 5 (56%); 0.0814: 2 (22%) | -0.3167: 2 (22%); -0.1202: 4 (44%); 0.0004: 6 (67%); 0.0814: 7 (78%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 49.894, 64.364, 65.468, 72.396 | 49.894: 7 (78%); 64.364: 5 (56%); 65.468: 4 (44%); 72.396: 2 (22%) | 49.894: 2 (22%); 64.364: 4 (44%); 65.468: 5 (56%); 72.396: 7 (78%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 100.0% | -0.9983, -0.8599, -0.8456, -0.3475 | -0.9983: 7 (78%); -0.8599: 5 (56%); -0.8456: 4 (44%); -0.3475: 2 (22%) | -0.9983: 2 (22%); -0.8599: 4 (44%); -0.8456: 5 (56%); -0.3475: 7 (78%) | OFFLINE |
| monthly_sma_12 | backtest/signals/multi_timeframe.py | 100.0% | 32.5356, 66.495, 86.6113, 91.6327 | 32.5356: 7 (78%); 66.495: 5 (56%); 86.6113: 4 (44%); 91.6327: 2 (22%) | 32.5356: 2 (22%); 66.495: 4 (44%); 86.6113: 5 (56%); 91.6327: 7 (78%) | OFFLINE |
| monthly_sma_6 | backtest/signals/multi_timeframe.py | 100.0% | 11.611, 38.495, 40.7652, 51.3124 | 11.611: 7 (78%); 38.495: 5 (56%); 40.7652: 4 (44%); 51.3124: 2 (22%) | 11.611: 2 (22%); 38.495: 4 (44%); 40.7652: 5 (56%); 51.3124: 7 (78%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0047, 0.0239, 0.2836, 0.3651 | 0.0047: 7 (78%); 0.0239: 5 (56%); 0.2836: 4 (44%); 0.3651: 2 (22%) | 0.0047: 2 (22%); 0.0239: 4 (44%); 0.2836: 5 (56%); 0.3651: 7 (78%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.4 | 0: 9 (100%); 0.4: 2 (22%) | 0: 7 (78%); 0.4: 7 (78%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0 | 0: 9 (100%) | 0: 8 (89%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0 | 0: 9 (100%) | 0: 8 (89%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.4 | 0: 9 (100%); 0.4: 2 (22%) | 0: 7 (78%); 0.4: 7 (78%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4 | 0: 9 (100%); 0.4: 2 (22%) | 0: 7 (78%); 0.4: 7 (78%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4 | 0: 9 (100%); 0.4: 2 (22%) | 0: 7 (78%); 0.4: 7 (78%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0 | 0: 8 (89%) | 0: 8 (89%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0 | 0: 8 (89%) | 0: 8 (89%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0 | 0: 8 (89%) | 0: 8 (89%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0 | 0: 8 (89%) | 0: 8 (89%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | 0 | 0: 9 (100%) | 0: 8 (89%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.0956 | 0: 9 (100%); 0.0956: 2 (22%) | 0: 7 (78%); 0.0956: 7 (78%) | OFFLINE |
| otc_short_ratio_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.2287, 0.3113, 0.395, 0.6422 | 0.2287: 7 (78%); 0.3113: 5 (56%); 0.395: 4 (44%); 0.6422: 2 (22%) | 0.2287: 2 (22%); 0.3113: 4 (44%); 0.395: 5 (56%); 0.6422: 7 (78%) | OFFLINE |
| otc_volume_recent | backtest/signals/congressional_alt_data.py | 100.0% | 28006.2, 246056.2, 818334.6, 1180843 | 28006.2: 7 (78%); 246056.2: 5 (56%); 818334.6: 4 (44%); 1180843: 2 (22%) | 28006.2: 2 (22%); 246056.2: 4 (44%); 818334.6: 5 (56%); 1180843: 7 (78%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 0, 5.6, 12 | 0: 9 (100%); 5.6: 5 (56%); 12: 5 (56%) | 0: 3 (33%); 5.6: 4 (44%); 12: 9 (100%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0011, 0.0157, 0.1584, 0.3578 | -0.0011: 7 (78%); 0.0157: 5 (56%); 0.1584: 4 (44%); 0.3578: 2 (22%) | -0.0011: 2 (22%); 0.0157: 4 (44%); 0.1584: 5 (56%); 0.3578: 7 (78%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0061, 0.0125, 0.566, 0.7292 | -0.0061: 7 (78%); 0.0125: 5 (56%); 0.566: 4 (44%); 0.7292: 2 (22%) | -0.0061: 2 (22%); 0.0125: 4 (44%); 0.566: 5 (56%); 0.7292: 7 (78%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0069, 0.0003, 0.0031, 0.0408 | -0.0069: 7 (78%); 0.0003: 5 (56%); 0.0031: 4 (44%); 0.0408: 2 (22%) | -0.0069: 2 (22%); 0.0003: 4 (44%); 0.0031: 5 (56%); 0.0408: 7 (78%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 100.0% | -15.6294, 3.931, 18.3358, 34.8464 | -15.6294: 7 (78%); 3.931: 5 (56%); 18.3358: 4 (44%); 34.8464: 2 (22%) | -15.6294: 2 (22%); 3.931: 4 (44%); 18.3358: 5 (56%); 34.8464: 7 (78%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 0.4256, 4.636, 36.6656, 44.1986 | 0.4256: 7 (78%); 4.636: 5 (56%); 36.6656: 4 (44%); 44.1986: 2 (22%) | 0.4256: 2 (22%); 4.636: 4 (44%); 36.6656: 5 (56%); 44.1986: 7 (78%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0169, 0.0586, 0.4721, 1.0684 | 0.0169: 7 (78%); 0.0586: 5 (56%); 0.4721: 4 (44%); 1.0684: 2 (22%) | 0.0169: 2 (22%); 0.0586: 4 (44%); 0.4721: 5 (56%); 1.0684: 7 (78%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -75.7007, -4.3493, -2.919, -0.2447 | -75.7007: 7 (78%); -4.3493: 5 (56%); -2.919: 4 (44%); -0.2447: 2 (22%) | -75.7007: 2 (22%); -4.3493: 4 (44%); -2.919: 5 (56%); -0.2447: 7 (78%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | 0.3726, 1.5561, 1.9259, 4.0906 | 0.3726: 7 (78%); 1.5561: 5 (56%); 1.9259: 4 (44%); 4.0906: 2 (22%) | 0.3726: 2 (22%); 1.5561: 4 (44%); 1.9259: 5 (56%); 4.0906: 7 (78%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -81.9585, -6.2744, -5.6655, -0.6132 | -81.9585: 7 (78%); -6.2744: 5 (56%); -5.6655: 4 (44%); -0.6132: 2 (22%) | -81.9585: 2 (22%); -6.2744: 4 (44%); -5.6655: 5 (56%); -0.6132: 7 (78%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 0.385, 4.9618, 44.1442, 68.0002 | 0.385: 7 (78%); 4.9618: 5 (56%); 44.1442: 4 (44%); 68.0002: 2 (22%) | 0.385: 2 (22%); 4.9618: 4 (44%); 44.1442: 5 (56%); 68.0002: 7 (78%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 17.396, 36.714, 50.394, 52.278 | 17.396: 7 (78%); 36.714: 5 (56%); 50.394: 4 (44%); 52.278: 2 (22%) | 17.396: 2 (22%); 36.714: 4 (44%); 50.394: 5 (56%); 52.278: 7 (78%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 44.234, 58.004, 66.42, 78.372 | 44.234: 7 (78%); 58.004: 5 (56%); 66.42: 4 (44%); 78.372: 2 (22%) | 44.234: 2 (22%); 58.004: 4 (44%); 66.42: 5 (56%); 78.372: 7 (78%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 45.796, 51.814, 52.47, 53.642 | 45.796: 7 (78%); 51.814: 5 (56%); 52.47: 4 (44%); 53.642: 2 (22%) | 45.796: 2 (22%); 51.814: 4 (44%); 52.47: 5 (56%); 53.642: 7 (78%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0372, 0.04, 0.043, 0.053 | 0.0372: 7 (78%); 0.04: 5 (56%); 0.043: 4 (44%); 0.053: 2 (22%) | 0.0372: 2 (22%); 0.04: 4 (44%); 0.043: 5 (56%); 0.053: 7 (78%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0775, -0.0526, -0.0448, -0.0381 | -0.0775: 7 (78%); -0.0526: 5 (56%); -0.0448: 4 (44%); -0.0381: 2 (22%) | -0.0775: 2 (22%); -0.0526: 4 (44%); -0.0448: 5 (56%); -0.0381: 7 (78%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 9 (100%) | 0: 8 (89%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 29.6, 37, 41.8, 49 | 29.6: 7 (78%); 37: 6 (67%); 41.8: 4 (44%); 49: 2 (22%) | 29.6: 2 (22%); 37: 5 (56%); 41.8: 5 (56%); 49: 7 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.3317, 0.5194, 0.6123, 0.6792 | 0.3317: 7 (78%); 0.5194: 5 (56%); 0.6123: 4 (44%); 0.6792: 2 (22%) | 0.3317: 2 (22%); 0.5194: 4 (44%); 0.6123: 5 (56%); 0.6792: 7 (78%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 0.16, 0.94, 7.58, 51.42 | 0.16: 7 (78%); 0.94: 5 (56%); 7.58: 4 (44%); 51.42: 2 (22%) | 0.16: 2 (22%); 0.94: 4 (44%); 7.58: 5 (56%); 51.42: 7 (78%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 0.004, 0.0059, 0.0097, 0.1311 | 0.004: 7 (78%); 0.0059: 5 (56%); 0.0097: 4 (44%); 0.1311: 2 (22%) | 0.004: 2 (22%); 0.0059: 4 (44%); 0.0097: 5 (56%); 0.1311: 7 (78%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 43.848, 53.018, 61.818, 75.312 | 43.848: 7 (78%); 53.018: 5 (56%); 61.818: 4 (44%); 75.312: 2 (22%) | 43.848: 2 (22%); 53.018: 4 (44%); 61.818: 5 (56%); 75.312: 7 (78%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 42.368, 54.788, 57.596, 73.746 | 42.368: 7 (78%); 54.788: 5 (56%); 57.596: 4 (44%); 73.746: 2 (22%) | 42.368: 2 (22%); 54.788: 4 (44%); 57.596: 5 (56%); 73.746: 7 (78%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 24.414, 46.802, 59.826, 77.788 | 24.414: 7 (78%); 46.802: 5 (56%); 59.826: 4 (44%); 77.788: 2 (22%) | 24.414: 2 (22%); 46.802: 4 (44%); 59.826: 5 (56%); 77.788: 7 (78%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 38.086, 43.14, 63.38, 81.85 | 38.086: 7 (78%); 43.14: 5 (56%); 63.38: 4 (44%); 81.85: 2 (22%) | 38.086: 2 (22%); 43.14: 4 (44%); 63.38: 5 (56%); 81.85: 7 (78%) | OFFLINE |
| tema | backtest/signals/technical.py | 100.0% | 0.7731, 1.6474, 17.8863, 30.0107 | 0.7731: 7 (78%); 1.6474: 5 (56%); 17.8863: 4 (44%); 30.0107: 2 (22%) | 0.7731: 2 (22%); 1.6474: 4 (44%); 17.8863: 5 (56%); 30.0107: 7 (78%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 8.8, 18.2, 19, 21 | 8.8: 7 (78%); 18.2: 5 (56%); 19: 5 (56%); 21: 3 (33%) | 8.8: 2 (22%); 18.2: 4 (44%); 19: 6 (67%); 21: 9 (100%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 1.6, 3, 3.8, 12.8 | 1.6: 7 (78%); 3: 6 (67%); 3.8: 4 (44%); 12.8: 2 (22%) | 1.6: 2 (22%); 3: 5 (56%); 3.8: 5 (56%); 12.8: 7 (78%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 42.326, 47.524, 48.3, 61.486 | 42.326: 7 (78%); 47.524: 5 (56%); 48.3: 4 (44%); 61.486: 2 (22%) | 42.326: 2 (22%); 47.524: 4 (44%); 48.3: 5 (56%); 61.486: 7 (78%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0103, 0.0413, 0.3937, 0.6715 | 0.0103: 7 (78%); 0.0413: 5 (56%); 0.3937: 4 (44%); 0.6715: 2 (22%) | 0.0103: 2 (22%); 0.0413: 4 (44%); 0.3937: 5 (56%); 0.6715: 7 (78%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8305, 0.8503, 0.8598, 0.8904 | 0.8305: 7 (78%); 0.8503: 5 (56%); 0.8598: 4 (44%); 0.8904: 2 (22%) | 0.8305: 2 (22%); 0.8503: 4 (44%); 0.8598: 5 (56%); 0.8904: 7 (78%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.028, 0.802, 1.106, 1.544 | 0.028: 7 (78%); 0.802: 5 (56%); 1.106: 4 (44%); 1.544: 2 (22%) | 0.028: 2 (22%); 0.802: 4 (44%); 1.106: 5 (56%); 1.544: 7 (78%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0071, 0.0672, 0.3855, 0.5772 | 0.0071: 7 (78%); 0.0672: 5 (56%); 0.3855: 4 (44%); 0.5772: 2 (22%) | 0.0071: 2 (22%); 0.0672: 4 (44%); 0.3855: 5 (56%); 0.5772: 7 (78%) | OFFLINE |
| vp_poc | backtest/signals/volume_profile.py | 100.0% | 0.0798, 0.4038, 17.042, 29.1782 | 0.0798: 7 (78%); 0.4038: 5 (56%); 17.042: 4 (44%); 29.1782: 2 (22%) | 0.0798: 2 (22%); 0.4038: 4 (44%); 17.042: 5 (56%); 29.1782: 7 (78%) | OFFLINE |
| vp_value_area_high | backtest/signals/volume_profile.py | 100.0% | 0.1187, 0.6844, 17.3526, 29.503 | 0.1187: 7 (78%); 0.6844: 5 (56%); 17.3526: 4 (44%); 29.503: 2 (22%) | 0.1187: 2 (22%); 0.6844: 4 (44%); 17.3526: 5 (56%); 29.503: 7 (78%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 87.0661, 102.0184, 103.6575, 110.706 | 87.0661: 7 (78%); 102.0184: 5 (56%); 103.6575: 4 (44%); 110.706: 2 (22%) | 87.0661: 2 (22%); 102.0184: 4 (44%); 103.6575: 5 (56%); 110.706: 7 (78%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 86.9851, 102.008, 103.6202, 110.5716 | 86.9851: 7 (78%); 102.008: 5 (56%); 103.6202: 4 (44%); 110.5716: 2 (22%) | 86.9851: 2 (22%); 102.008: 4 (44%); 103.6202: 5 (56%); 110.5716: 7 (78%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 86.9041, 101.9977, 103.5829, 110.4372 | 86.9041: 7 (78%); 101.9977: 5 (56%); 103.5829: 4 (44%); 110.4372: 2 (22%) | 86.9041: 2 (22%); 101.9977: 4 (44%); 103.5829: 5 (56%); 110.4372: 7 (78%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 87.147, 102.0288, 103.6947, 110.8403 | 87.147: 7 (78%); 102.0288: 5 (56%); 103.6947: 4 (44%); 110.8403: 2 (22%) | 87.147: 2 (22%); 102.0288: 4 (44%); 103.6947: 5 (56%); 110.8403: 7 (78%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 87.2279, 102.0392, 103.732, 110.9549 | 87.2279: 7 (78%); 102.0392: 5 (56%); 103.732: 4 (44%); 110.9549: 2 (22%) | 87.2279: 2 (22%); 102.0392: 4 (44%); 103.732: 5 (56%); 110.9549: 7 (78%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0, 0.2864 | 0: 9 (100%); 0.2864: 2 (22%) | 0: 7 (78%); 0.2864: 7 (78%) | OFFLINE |
| weekly_ema_10 | backtest/signals/multi_timeframe.py | 100.0% | 3.4912, 7.6557, 21.3483, 32.4007 | 3.4912: 7 (78%); 7.6557: 5 (56%); 21.3483: 4 (44%); 32.4007: 2 (22%) | 3.4912: 2 (22%); 7.6557: 4 (44%); 21.3483: 5 (56%); 32.4007: 7 (78%) | OFFLINE |
| weekly_ema_20 | backtest/signals/multi_timeframe.py | 100.0% | 18.4383, 32.7533, 38.7128, 41.6042 | 18.4383: 7 (78%); 32.7533: 5 (56%); 38.7128: 4 (44%); 41.6042: 2 (22%) | 18.4383: 2 (22%); 32.7533: 4 (44%); 38.7128: 5 (56%); 41.6042: 7 (78%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0041, 0.01, 0.0993, 0.3169 | -0.0041: 7 (78%); 0.01: 5 (56%); 0.0993: 4 (44%); 0.3169: 2 (22%) | -0.0041: 2 (22%); 0.01: 4 (44%); 0.0993: 5 (56%); 0.3169: 7 (78%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -50.574, -35.362, -26.538, -22.528 | -50.574: 7 (78%); -35.362: 5 (56%); -26.538: 4 (44%); -22.528: 2 (22%) | -50.574: 2 (22%); -35.362: 4 (44%); -26.538: 5 (56%); -22.528: 7 (78%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.9743, 1.2439, 2.0031, 2.5075 | 0.9743: 7 (78%); 1.2439: 5 (56%); 2.0031: 4 (44%); 2.5075: 2 (22%) | 0.9743: 2 (22%); 1.2439: 4 (44%); 2.0031: 5 (56%); 2.5075: 7 (78%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 7, 8.4, 10 | 7: 8 (89%); 8.4: 5 (56%); 10: 5 (56%) | 7: 3 (33%); 8.4: 4 (44%); 10: 9 (100%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0105, 0.0341, 0.5127, 2.1643 | 0.0105: 7 (78%); 0.0341: 5 (56%); 0.5127: 4 (44%); 2.1643: 2 (22%) | 0.0105: 2 (22%); 0.0341: 4 (44%); 0.5127: 5 (56%); 2.1643: 7 (78%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 1.6, 4.4, 10 | 1.6: 7 (78%); 4.4: 5 (56%); 10: 5 (56%) | 1.6: 2 (22%); 4.4: 4 (44%); 10: 9 (100%) | OFFLINE |
| year_high | backtest/signals/screener.py +1 | 100.0% | 113.996, 140.137, 157.4051, 208.48 | 113.996: 7 (78%); 140.137: 5 (56%); 157.4051: 5 (56%); 208.48: 3 (33%) | 113.996: 2 (22%); 140.137: 4 (44%); 157.4051: 6 (67%); 208.48: 8 (89%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| above_avwap_20high | 33.3% |
| above_avwap_20low | 88.9% |
| above_avwap_252low | 66.7% |
| above_avwap_50low | 77.8% |
| above_cam_r3 | 33.3% |
| above_cam_r4 | 33.3% |
| above_cpr | 55.6% |
| above_pivot | 55.6% |
| above_prev_high | 33.3% |
| above_prev_high_clearance_atr_05 | 11.1% |
| above_prev_low | 66.7% |
| above_r1 | 33.3% |
| above_r2 | 33.3% |
| above_vwap | 22.2% |
| above_wood_p | 55.6% |
| ad_rising | 33.3% |
| adx_cross_up | 11.1% |
| adx_di_bear | 55.6% |
| adx_di_bull | 44.4% |
| adx_strong | 55.6% |
| ao_cross_dn | 11.1% |
| ao_positive | 66.7% |
| ao_twin_peaks_bull | 22.2% |
| at_key_fib | 11.1% |
| at_key_fib_wide | 55.6% |
| avwap_20high_loss_recent_3d | 25.0% |
| avwap_20high_reclaim_recent_3d | 37.5% |
| avwap_20low_loss_recent_3d | 11.1% |
| avwap_20low_reclaim_recent_3d | 22.2% |
| avwap_50low_loss_recent_3d | 11.1% |
| avwap_50low_reclaim_recent_3d | 22.2% |
| bb_10_20_above_mid | 77.8% |
| bb_10_20_expanding | 33.3% |
| bb_10_20_pctb_gt_75 | 33.3% |
| bb_10_20_pctb_gt_8 | 11.1% |
| bb_10_20_pctb_gt_85 | 11.1% |
| bb_10_20_pctb_lt_05 | 11.1% |
| bb_10_20_pctb_lt_1 | 11.1% |
| bb_10_20_pctb_lt_15 | 11.1% |
| bb_10_20_pctb_lt_2 | 11.1% |
| bb_10_20_pctb_lt_25 | 11.1% |
| bb_10_20_reclaim_from_lower_recent_3d | 33.3% |
| bb_10_20_reclaim_from_upper_recent_3d | 11.1% |
| bb_10_20_squeeze | 44.4% |
| bb_10_20_touch_lower | 22.2% |
| bb_10_20_touch_upper | 11.1% |
| bb_20_15_above_mid | 77.8% |
| bb_20_15_expanding | 33.3% |
| bb_20_15_pctb_gt_75 | 44.4% |
| bb_20_15_pctb_gt_8 | 44.4% |
| bb_20_15_pctb_gt_85 | 44.4% |
| bb_20_15_pctb_gt_9 | 44.4% |
| bb_20_15_pctb_gt_95 | 11.1% |
| bb_20_15_pctb_lt_2 | 11.1% |
| bb_20_15_pctb_lt_25 | 11.1% |
| bb_20_15_reclaim_from_lower_recent_3d | 33.3% |
| bb_20_15_reclaim_from_upper_recent_3d | 11.1% |
| bb_20_15_squeeze | 44.4% |
| bb_20_15_touch_lower | 11.1% |
| bb_20_15_touch_upper | 22.2% |
| bb_20_20_above_mid | 77.8% |
| bb_20_20_expanding | 33.3% |
| bb_20_20_pctb_gt_75 | 44.4% |
| bb_20_20_pctb_gt_8 | 44.4% |
| bb_20_20_pctb_gt_85 | 11.1% |
| bb_20_20_pctb_gt_9 | 11.1% |
| bb_20_20_pctb_gt_95 | 11.1% |
| bb_20_20_reclaim_from_upper_recent_3d | 11.1% |
| bb_20_20_squeeze | 44.4% |
| bb_20_20_touch_lower | 11.1% |
| bb_20_20_touch_upper | 11.1% |
| bearish_pin_bar | 11.1% |
| below_avwap_20high | 66.7% |
| below_avwap_20low | 11.1% |
| below_avwap_252low | 33.3% |
| below_avwap_50low | 22.2% |
| below_cam_s3 | 22.2% |
| below_cam_s4 | 11.1% |
| below_cpr | 44.4% |
| below_ema_20 | 55.6% |
| below_ema_200 | 77.8% |
| below_ema_20_break_recent_5d | 11.1% |
| below_ema_21 | 55.6% |
| below_ema_21_break_recent_5d | 11.1% |
| below_ema_50 | 77.8% |
| below_ema_9 | 22.2% |
| below_ema_9_break_recent_5d | 22.2% |
| below_prev_high | 66.7% |
| below_prev_low | 33.3% |
| below_s1 | 11.1% |
| below_sma_20 | 22.2% |
| below_sma_200 | 77.8% |
| below_sma_21 | 22.2% |
| below_sma_50 | 22.2% |
| below_sma_9 | 22.2% |
| below_vwap | 77.8% |
| bullish_pin_bar | 11.1% |
| close_above_open | 22.2% |
| close_below_open | 55.6% |
| close_in_bottom_40pct_of_range | 55.6% |
| close_in_top_40pct_of_range | 33.3% |
| cmf_cross_up | 11.1% |
| cmf_negative | 55.6% |
| cmf_positive | 11.1% |
| cpr_narrow | 55.6% |
| cpr_narrow_tight | 11.1% |
| dc10_breakout_dn | 11.1% |
| dc10_breakout_dn_1pct | 22.2% |
| dc10_breakout_up_1pct | 33.3% |
| dc10_new_high | 22.2% |
| dc20_breakout_dn | 11.1% |
| dc20_new_high | 11.1% |
| dc20_resistance_break_retest_strong | 11.1% |
| defensive_leadership | 11.1% |
| doji | 11.1% |
| double_bottom_detected | 33.3% |
| double_top_detected | 33.3% |
| dpi_elevated | 44.4% |
| drying_volume_on_down_turn | 22.2% |
| drying_volume_on_up_turn | 11.1% |
| ema_20_50_bearish | 77.8% |
| ema_20_50_bullish | 22.2% |
| ema_50_200_bearish | 77.8% |
| ema_50_200_bullish | 22.2% |
| ema_9_21_bearish | 44.4% |
| ema_9_21_bullish | 55.6% |
| ema_9_21_golden_cross | 11.1% |
| force_index_positive | 77.8% |
| gap_dn_1_5pct | 11.1% |
| gap_dn_2pct | 11.1% |
| gap_up_1_5pct | 33.3% |
| gap_up_2pct | 33.3% |
| htf_aligned_bear | 77.8% |
| htf_aligned_bull | 22.2% |
| hull_bearish | 44.4% |
| hull_bullish | 55.6% |
| hull_flip_dn | 11.1% |
| hull_flip_up | 11.1% |
| ichi_above_cloud | 11.1% |
| ichi_below_cloud | 33.3% |
| ichi_tk_bearish | 44.4% |
| ichi_tk_bullish | 55.6% |
| ichi_weekly_above_cloud | 22.2% |
| ichi_weekly_below_cloud | 55.6% |
| ichi_weekly_in_cloud | 22.2% |
| inside_bar | 11.1% |
| institutional_buy | 77.8% |
| institutional_strong_buy | 55.6% |
| is_friday | 44.4% |
| is_halloween_period | 55.6% |
| is_january | 33.3% |
| is_january_extended | 33.3% |
| is_monday | 22.2% |
| is_pre_holiday | 11.1% |
| is_summer_period | 44.4% |
| is_totm_window | 77.8% |
| is_totm_window_first_day | 11.1% |
| is_week_open | 22.2% |
| macd_12_26_9_bearish | 22.2% |
| macd_12_26_9_bullish | 77.8% |
| macd_8_21_5_bearish | 33.3% |
| macd_8_21_5_bullish | 66.7% |
| marubozu_bear | 11.1% |
| marubozu_bull | 11.1% |
| mfi_broad_overbought | 22.2% |
| mfi_overbought | 11.1% |
| monthly_above_sma_12 | 22.2% |
| monthly_above_sma_6 | 22.2% |
| monthly_bias_bear | 77.8% |
| monthly_bias_bull | 22.2% |
| monthly_momentum_pos | 22.2% |
| near_52w_high | 11.1% |
| near_52w_high_95pct | 11.1% |
| near_avwap_20high_atr_05x | 87.5% |
| near_avwap_20low_atr_05x | 55.6% |
| near_avwap_252low_atr_05x | 66.7% |
| near_avwap_252low_atr_10x | 77.8% |
| near_avwap_252low_atr_15x | 77.8% |
| near_avwap_252low_atr_20x | 77.8% |
| near_avwap_50low_atr_05x | 66.7% |
| near_avwap_50low_atr_10x | 88.9% |
| near_cam_r3 | 22.2% |
| near_cam_s3 | 22.2% |
| near_cam_s4 | 33.3% |
| near_fib_236 | 33.3% |
| near_fib_382 | 11.1% |
| near_fib_500 | 11.1% |
| near_fib_618 | 11.1% |
| near_fib_786 | 11.1% |
| near_pivot | 22.2% |
| near_prev_close | 22.2% |
| near_prev_high | 11.1% |
| near_prev_low | 44.4% |
| near_r1 | 11.1% |
| near_r1_wide | 44.4% |
| near_r2_wide | 55.6% |
| near_s1 | 33.3% |
| near_s1_wide | 44.4% |
| near_s2 | 22.2% |
| near_s2_wide | 44.4% |
| near_s3 | 11.1% |
| near_wood_r1 | 11.1% |
| near_wood_s1 | 22.2% |
| news_uses_polygon_score | 22.2% |
| obv_bearish | 22.2% |
| obv_bullish | 77.8% |
| obv_falling | 44.4% |
| obv_rising | 55.6% |
| outside_bar | 11.1% |
| pead_positive_surprise | 50.0% |
| pin_bar | 22.2% |
| po3_accumulation_active | 44.4% |
| po3_bearish | 37.5% |
| po3_bullish | 12.5% |
| po3_manipulation_sweep_down | 11.1% |
| po3_manipulation_sweep_up | 22.2% |
| po3_mmsm_setup | 11.1% |
| po3_sweep_above_prior_high | 62.5% |
| po3_sweep_below_prior_low | 62.5% |
| ppo_bullish | 77.8% |
| price_above_dema | 77.8% |
| price_above_ema_20 | 44.4% |
| price_above_ema_200 | 22.2% |
| price_above_ema_20_break_recent_5d | 33.3% |
| price_above_ema_21 | 44.4% |
| price_above_ema_21_break_recent_5d | 33.3% |
| price_above_ema_50 | 22.2% |
| price_above_ema_9 | 77.8% |
| price_above_ema_9_break_recent_5d | 55.6% |
| price_above_hull | 55.6% |
| price_above_sma_200 | 22.2% |
| price_above_sma_21 | 77.8% |
| price_above_sma_50 | 77.8% |
| price_above_tema | 33.3% |
| price_below_dema | 22.2% |
| price_below_hull | 44.4% |
| price_below_tema | 66.7% |
| psar_bullish | 77.8% |
| r1_break_retest_long | 55.6% |
| resistance_break_retest | 44.4% |
| risk_off_regime_gold_signal | 11.1% |
| risk_on_regime_bond_signal | 77.8% |
| risk_on_regime_bond_signal_strong | 33.3% |
| roc_positive | 88.9% |
| roc_turning_up | 22.2% |
| rsi_14_bullish | 44.4% |
| rsi_14_cross_up_oversold_recent_3d | 11.1% |
| rsi_14_extreme_os | 33.3% |
| rsi_14_oversold | 33.3% |
| rsi_14_rising | 44.4% |
| rsi_21_bullish | 22.2% |
| rsi_21_cross_dn_overbought_recent_3d | 11.1% |
| rsi_21_cross_up_extreme_os_recent_3d | 11.1% |
| rsi_21_extreme_os | 33.3% |
| rsi_21_oversold | 44.4% |
| rsi_21_rising | 44.4% |
| rsi_2_bullish | 77.8% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 22.2% |
| rsi_2_cross_dn_overbought_recent_3d | 22.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 33.3% |
| rsi_2_cross_up_oversold_recent_3d | 44.4% |
| rsi_2_extreme_ob | 22.2% |
| rsi_2_extreme_os | 11.1% |
| rsi_2_overbought | 33.3% |
| rsi_2_oversold | 11.1% |
| rsi_2_rising | 44.4% |
| rsi_9_bullish | 77.8% |
| rsi_9_cross_up_oversold_recent_3d | 11.1% |
| rsi_9_extreme_os | 11.1% |
| rsi_9_oversold | 11.1% |
| rsi_9_rising | 44.4% |
| s1_break_retest_short | 33.3% |
| shooting_star | 11.1% |
| sma_20_50_bullish | 55.6% |
| sma_20_50_golden_cross | 11.1% |
| sma_50_200_bullish | 22.2% |
| sma_9_21_bullish | 77.8% |
| smc_bos_bullish | 11.1% |
| smc_bos_retest_short | 11.1% |
| smc_breaker_block_bearish | 77.8% |
| smc_breaker_block_bullish | 11.1% |
| smc_fvg_bearish_active | 33.3% |
| smc_fvg_bullish_active | 55.6% |
| smc_fvg_retest_long_zone | 22.2% |
| smc_in_discount_zone | 55.6% |
| smc_in_premium_zone | 66.7% |
| smc_inverse_fvg_bearish | 88.9% |
| smc_ob_bearish_active | 11.1% |
| smc_ob_bullish_active | 33.3% |
| squeeze_in | 88.9% |
| squeeze_positive | 88.9% |
| stoch_bearish_cross | 11.1% |
| stoch_broad_overbought | 22.2% |
| stoch_broad_oversold | 11.1% |
| stoch_overbought | 11.1% |
| stochrsi_cross_dn | 44.4% |
| stochrsi_cross_up | 33.3% |
| stochrsi_overbought | 22.2% |
| tema_above_dema | 77.8% |
| triangle_apex_break_retest_long | 33.3% |
| triangle_ascending_detected | 11.1% |
| uo_overbought | 22.2% |
| usd_strengthening | 22.2% |
| usd_weakening | 22.2% |
| vix_band_high | 33.3% |
| vix_band_low | 55.6% |
| vix_band_mid | 11.1% |
| vol_above_avg | 44.4% |
| vol_below_avg | 55.6% |
| vol_spike_12x | 33.3% |
| vol_spike_15x | 22.2% |
| vol_spike_17x | 22.2% |
| vol_spike_2x | 11.1% |
| vol_spike_2x_on_up_day_recent_3d | 11.1% |
| vp_above_value_area | 33.3% |
| vp_close_above_poc | 77.8% |
| vp_close_below_poc | 22.2% |
| vp_in_value_area | 66.7% |
| week_open_gap_up_15pct | 11.1% |
| weekly_above_ema_10 | 22.2% |
| weekly_above_ema_20 | 22.2% |
| weekly_bias_bear | 77.8% |
| weekly_bias_bull | 22.2% |
| weekly_momentum_pos | 66.7% |
| williams_r_overbought | 22.2% |
| williams_r_oversold | 11.1% |
| williams_r_rising | 44.4% |
| xs_avoid_high_ivol | 28.6% |
| xs_avoid_high_max | 44.4% |
| xs_high_beta_decile | 55.6% |
| xs_low_beta_bottom_quintile | 55.6% |
| xs_low_beta_decile | 11.1% |
| xs_low_beta_top_quintile | 11.1% |
| xs_momentum_bottom_decile | 71.4% |
| xs_momentum_bottom_quintile | 71.4% |
| xs_momentum_top_quintile | 14.3% |
| xs_quality_top_tercile | 50.0% |
| yoy_surprise_high | 50.0% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 66.7% |
| committed_growth_holders | 66.7% |
| cot_rut_commercials_pctile_3y | 44.4% |
| cot_rut_mmoney_pctile_3y | 44.4% |
| days_since_deletion | 88.9% |
| days_to_next_holiday | 88.9% |
| lobbying_amount_1y | 33.3% |
| lobbying_amount_q | 33.3% |
| lobbying_amount_yoy | 33.3% |
| pair_half_life | 66.7% |
| pair_max_abs_zscore | 66.7% |
| pair_zscore_signed | 66.7% |
| pct_from_avwap_20high | 88.9% |
| persistent_holders_4q | 66.7% |
| persistent_holders_8q | 66.7% |
| po3_close_position | 88.9% |
| search_volume_observations | 33.3% |
| search_volume_zscore_30d | 33.3% |
| short_interest_pct | 77.8% |
| total_active_holders | 66.7% |
| xs_ivol | 77.8% |
| xs_ivol_decile | 77.8% |
| xs_momentum_12_1 | 77.8% |
| xs_momentum_decile | 77.8% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.967), `avwap_20low` (1.0), `avwap_252low` (0.967), `avwap_50low` (0.979), `bb_10_20_lower` (0.979), `bb_10_20_mid` (0.983), `bb_10_20_upper` (0.983), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.983), `cam_r1` (0.983), `cam_r2` (0.983), `cam_r3` (0.983), `cam_r4` (0.983), `cam_s1` (0.983), `cam_s2` (0.983), `cam_s3` (0.983), `cam_s4` (0.983), `cpr_bottom` (0.983), `cpr_top` (0.983), `days_since_last_earnings` (1.0), `dc10_lower` (0.996), `dc10_mid` (0.996), `dc10_upper` (0.992), `dc20_lower` (0.975), `dc20_mid` (0.996), `dc20_upper` (0.992), `double_bottom_neckline` (1.0), `double_bottom_trough` (1.0), `double_top_neckline` (1.0), `double_top_peak` (1.0), `earnings_announcement_return` (1.0), `earnings_eps_yoy_growth` (-1.0), `fib_236` (0.992), `fib_382` (0.992), `fib_500` (0.992), `fib_618` (0.992), `fib_786` (0.992), `fib_ext_127` (0.992), `fib_ext_162` (0.975), `hull_ma` (0.983), `ichi_kijun` (0.992), `ichi_tenkan` (0.996), `monthly_close` (0.967), `pct_from_avwap_20low` (-0.983), `pct_from_vwap` (0.979), `pivot` (0.983), `prev_close` (0.983), `prev_high` (0.983), `prev_low` (0.979), `psar_value` (0.983), `r1` (0.983), `r2` (0.983), `r3` (0.983), `s1` (0.983), `s2` (0.983), `s3` (0.996), `search_volume_index_recent` (1.0), `supertrend_value` (0.983), `swing_high` (0.992), `swing_low` (0.979), `vix_today` (0.996), `vix_value` (0.996), `vp_value_area_low` (0.967), `weekly_close` (0.967), `wood_p` (0.983), `wood_r1` (0.983), `wood_r2` (0.983), `wood_s1` (0.983), `wood_s2` (0.983), `xs_quality_decile` (1.0), `xs_quality_gross_profitability` (1.0), `year_low` (0.975)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
