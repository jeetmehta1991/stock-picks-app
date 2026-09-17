# Table A - weekly_bias_pullback_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:07:43 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** multi_timeframe | **status:** NOT-STARTED | **R5 fires:** 27 | **surviving fires (T1):** 27 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  weekly_bias_bull  <- backtest/signals/multi_timeframe.py +1
       DEFN: weekly close above weekly EMA(10) AND EMA(20) (multi_timeframe.py:45-90)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  rsi_14 < 45   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_weekly_bias_pullback_long (docstring and return dropped):

```python
fires = s.get('weekly_bias_bull', False) and s.get('rsi_14', 50) < 45
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
| P1 | PRODUCER | weekly_bias_bull - emitted by backtest/signals/multi_timeframe.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | weekly close above weekly EMA(10) AND EMA(20) (multi_timeframe.py:45-90) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | weekly ema pair - backtest/signals/multi_timeframe.py:45-90 | BRACKET production | (10, 20) | [(5,10), (10,20), (20,40)] | none - weekly emas unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | STRATEGY | rsi_14 `< 45` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 45` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P2.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 45` | 100.0% | TIGHTER = LOWER the ceiling: 42.938 -> 6 (22%); 44.222 -> 11 (41%); 44.51 -> 16 (59%); 44.712 -> 21 (78%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 21.772, 24.374, 27.29, 29.846 | 21.772: 21 (78%); 24.374: 16 (59%); 27.29: 11 (41%); 29.846: 6 (22%) | 21.772: 6 (22%); 24.374: 11 (41%); 27.29: 16 (59%); 29.846: 21 (78%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 24.43, 26.95, 29.366, 32.81 | 24.43: 21 (78%); 26.95: 16 (59%); 29.366: 11 (41%); 32.81: 6 (22%) | 24.43: 6 (22%); 26.95: 11 (41%); 29.366: 16 (59%); 32.81: 21 (78%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 15.838, 20.024, 21.254, 23.38 | 15.838: 21 (78%); 20.024: 16 (59%); 21.254: 11 (41%); 23.38: 6 (22%) | 15.838: 6 (22%); 20.024: 11 (41%); 21.254: 16 (59%); 23.38: 21 (78%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -2.0882, -1.1776, -0.1376, 0.5597 | -2.0882: 21 (78%); -1.1776: 16 (59%); -0.1376: 11 (41%); 0.5597: 6 (22%) | -2.0882: 6 (22%); -1.1776: 11 (41%); -0.1376: 16 (59%); 0.5597: 21 (78%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 0.9491, 1.8063, 3.2111, 7.3406 | 0.9491: 21 (78%); 1.8063: 16 (59%); 3.2111: 11 (41%); 7.3406: 6 (22%) | 0.9491: 6 (22%); 1.8063: 11 (41%); 3.2111: 16 (59%); 7.3406: 21 (78%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 0.9491, 1.8063, 3.2111, 7.3406 | 0.9491: 21 (78%); 1.8063: 16 (59%); 3.2111: 11 (41%); 7.3406: 6 (22%) | 0.9491: 6 (22%); 1.8063: 11 (41%); 3.2111: 16 (59%); 7.3406: 21 (78%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.9864, 2.8694, 4.2546, 4.9834 | 1.9864: 21 (78%); 2.8694: 16 (59%); 4.2546: 11 (41%); 4.9834: 6 (22%) | 1.9864: 6 (22%); 2.8694: 11 (41%); 4.2546: 16 (59%); 4.9834: 21 (78%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0744, 0.103, 0.1335, 0.2004 | 0.0744: 21 (78%); 0.103: 16 (59%); 0.1335: 11 (41%); 0.2004: 6 (22%) | 0.0744: 6 (22%); 0.103: 11 (41%); 0.1335: 16 (59%); 0.2004: 21 (78%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.1032, 0.1823, 0.2438, 0.3232 | 0.1032: 21 (78%); 0.1823: 16 (59%); 0.2438: 11 (41%); 0.3232: 6 (22%) | 0.1032: 6 (22%); 0.1823: 11 (41%); 0.2438: 16 (59%); 0.3232: 21 (78%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0621, 0.091, 0.1253, 0.1546 | 0.0621: 21 (78%); 0.091: 16 (59%); 0.1253: 11 (41%); 0.1546: 6 (22%) | 0.0621: 6 (22%); 0.091: 11 (41%); 0.1253: 16 (59%); 0.1546: 21 (78%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.0977, -0.0055, 0.044, 0.1025 | -0.0977: 21 (78%); -0.0055: 16 (59%); 0.044: 11 (41%); 0.1025: 6 (22%) | -0.0977: 6 (22%); -0.0055: 11 (41%); 0.044: 16 (59%); 0.1025: 21 (78%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0827, 0.1214, 0.1672, 0.2061 | 0.0827: 21 (78%); 0.1214: 16 (59%); 0.1672: 11 (41%); 0.2061: 6 (22%) | 0.0827: 6 (22%); 0.1214: 11 (41%); 0.1672: 16 (59%); 0.2061: 21 (78%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0517, 0.1209, 0.158, 0.2018 | 0.0517: 21 (78%); 0.1209: 16 (59%); 0.158: 11 (41%); 0.2018: 6 (22%) | 0.0517: 6 (22%); 0.1209: 11 (41%); 0.158: 16 (59%); 0.2018: 21 (78%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0596, -0.0305, -0.0139, 0.0156 | -0.0596: 21 (78%); -0.0305: 16 (59%); -0.0139: 11 (41%); 0.0156: 6 (22%) | -0.0596: 6 (22%); -0.0305: 11 (41%); -0.0139: 16 (59%); 0.0156: 21 (78%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1344, 0.1639, 0.2047, 0.2716 | 0.1344: 21 (78%); 0.1639: 16 (59%); 0.2047: 11 (41%); 0.2716: 6 (22%) | 0.1344: 6 (22%); 0.1639: 11 (41%); 0.2047: 16 (59%); 0.2716: 21 (78%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 27 (100%) | 0: 26 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1257, 0.0019, 0.0607, 0.1291 | -0.1257: 21 (78%); 0.0019: 16 (59%); 0.0607: 11 (41%); 0.1291: 6 (22%) | -0.1257: 6 (22%); 0.0019: 11 (41%); 0.0607: 16 (59%); 0.1291: 21 (78%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 27 (100%); 1: 10 (37%) | 0: 17 (63%); 1: 24 (89%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2641, -0.2257, -0.1816, -0.123 | -0.2641: 21 (78%); -0.2257: 16 (59%); -0.1816: 11 (41%); -0.123: 6 (22%) | -0.2641: 6 (22%); -0.2257: 11 (41%); -0.1816: 16 (59%); -0.123: 21 (78%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.0423, 0.4795, 0.6731, 0.7526 | 0.0423: 21 (78%); 0.4795: 16 (59%); 0.6731: 12 (44%); 0.7526: 6 (22%) | 0.0423: 6 (22%); 0.4795: 11 (41%); 0.6731: 17 (63%); 0.7526: 21 (78%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3141, 0.4257, 0.7897, 0.9025 | 0.3141: 22 (81%); 0.4257: 16 (59%); 0.7897: 11 (41%); 0.9025: 6 (22%) | 0.3141: 9 (33%); 0.4257: 11 (41%); 0.7897: 16 (59%); 0.9025: 21 (78%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0197, 0.0178, 0.0752, 0.0996 | -0.0197: 21 (78%); 0.0178: 16 (59%); 0.0752: 11 (41%); 0.0996: 6 (22%) | -0.0197: 6 (22%); 0.0178: 11 (41%); 0.0752: 16 (59%); 0.0996: 21 (78%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4282, 0.5038, 0.609, 0.7153 | 0.4282: 21 (78%); 0.5038: 16 (59%); 0.609: 11 (41%); 0.7153: 6 (22%) | 0.4282: 6 (22%); 0.5038: 11 (41%); 0.609: 16 (59%); 0.7153: 21 (78%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.118, 0.2769, 0.4705, 0.6577 | 0.118: 21 (78%); 0.2769: 16 (59%); 0.4705: 11 (41%); 0.6577: 6 (22%) | 0.118: 6 (22%); 0.2769: 11 (41%); 0.4705: 16 (59%); 0.6577: 21 (78%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.497, -0.3186, -0.1694, 0.106 | -0.497: 22 (81%); -0.3186: 16 (59%); -0.1694: 11 (41%); 0.106: 6 (22%) | -0.497: 7 (26%); -0.3186: 11 (41%); -0.1694: 16 (59%); 0.106: 21 (78%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3423, 0.4846, 0.7167, 0.9538 | 0.3423: 21 (78%); 0.4846: 16 (59%); 0.7167: 11 (41%); 0.9538: 6 (22%) | 0.3423: 6 (22%); 0.4846: 11 (41%); 0.7167: 16 (59%); 0.9538: 21 (78%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1116, 0.3295, 0.4423, 0.7846 | 0.1116: 21 (78%); 0.3295: 16 (59%); 0.4423: 11 (41%); 0.7846: 6 (22%) | 0.1116: 6 (22%); 0.3295: 11 (41%); 0.4423: 16 (59%); 0.7846: 21 (78%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0565, -0.0494, 0 | -0.0565: 22 (81%); -0.0494: 16 (59%); 0: 12 (44%) | -0.0565: 7 (26%); -0.0494: 11 (41%); 0: 24 (89%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.7321, 0.8692, 0.9782, 1 | 0.7321: 21 (78%); 0.8692: 16 (59%); 0.9782: 11 (41%); 1: 8 (30%) | 0.7321: 6 (22%); 0.8692: 11 (41%); 0.9782: 16 (59%); 1: 27 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1244, 0.1923, 0.3205, 0.5038 | 0.1244: 21 (78%); 0.1923: 16 (59%); 0.3205: 12 (44%); 0.5038: 6 (22%) | 0.1244: 6 (22%); 0.1923: 11 (41%); 0.3205: 18 (67%); 0.5038: 21 (78%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0004, 0.0255, 0.0854, 0.356 | 0.0004: 21 (78%); 0.0255: 16 (59%); 0.0854: 11 (41%); 0.356: 6 (22%) | 0.0004: 6 (22%); 0.0255: 11 (41%); 0.0854: 16 (59%); 0.356: 21 (78%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5335, 0.7538, 0.9718, 0.9859 | 0.5335: 21 (78%); 0.7538: 16 (59%); 0.9718: 11 (41%); 0.9859: 6 (22%) | 0.5335: 6 (22%); 0.7538: 11 (41%); 0.9718: 16 (59%); 0.9859: 21 (78%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.192, 0.3666, 0.7116 | 0.0962: 22 (81%); 0.192: 16 (59%); 0.3666: 11 (41%); 0.7116: 6 (22%) | 0.0962: 7 (26%); 0.192: 11 (41%); 0.3666: 16 (59%); 0.7116: 21 (78%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0336, 0.0566, 0.1225 | -0.0812: 22 (81%); -0.0336: 16 (59%); 0.0566: 12 (44%); 0.1225: 8 (30%) | -0.0812: 8 (30%); -0.0336: 11 (41%); 0.0566: 18 (67%); 0.1225: 22 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.126, -0.0217, 0.0071, 0.0472 | -0.126: 21 (78%); -0.0217: 17 (63%); 0.0071: 11 (41%); 0.0472: 6 (22%) | -0.126: 6 (22%); -0.0217: 11 (41%); 0.0071: 16 (59%); 0.0472: 21 (78%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4205, 0.5218, 0.6359, 0.791 | 0.4205: 21 (78%); 0.5218: 16 (59%); 0.6359: 11 (41%); 0.791: 6 (22%) | 0.4205: 6 (22%); 0.5218: 11 (41%); 0.6359: 16 (59%); 0.791: 21 (78%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1859, 0.5641, 0.8705, 0.9744 | 0.1859: 22 (81%); 0.5641: 17 (63%); 0.8705: 11 (41%); 0.9744: 6 (22%) | 0.1859: 7 (26%); 0.5641: 13 (48%); 0.8705: 16 (59%); 0.9744: 21 (78%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.035, 0.0827, 0.1973, 0.4036 | 0.035: 21 (78%); 0.0827: 16 (59%); 0.1973: 11 (41%); 0.4036: 6 (22%) | 0.035: 6 (22%); 0.0827: 11 (41%); 0.1973: 16 (59%); 0.4036: 21 (78%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 20, 49.8, 79.8, 164.4 | 20: 21 (78%); 49.8: 16 (59%); 79.8: 11 (41%); 164.4: 6 (22%) | 20: 6 (22%); 49.8: 11 (41%); 79.8: 16 (59%); 164.4: 21 (78%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 1.2593, 2.0802, 2.6775, 3.5474 | 1.2593: 21 (78%); 2.0802: 16 (59%); 2.6775: 11 (41%); 3.5474: 6 (22%) | 1.2593: 6 (22%); 2.0802: 11 (41%); 2.6775: 16 (59%); 3.5474: 21 (78%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 9.8, 26.4, 33.6, 40.8 | 9.8: 21 (78%); 26.4: 16 (59%); 33.6: 11 (41%); 40.8: 6 (22%) | 9.8: 6 (22%); 26.4: 11 (41%); 33.6: 16 (59%); 40.8: 21 (78%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 3, 3.8 | 0: 27 (100%); 1: 19 (70%); 3: 13 (48%); 3.8: 6 (22%) | 0: 8 (30%); 1: 12 (44%); 3: 21 (78%); 3.8: 21 (78%) | OFFLINE |
| dpi_30d_avg | backtest/signals/congressional_alt_data.py | 100.0% | 0.4028, 0.4601, 0.4965, 0.5272 | 0.4028: 21 (78%); 0.4601: 16 (59%); 0.4965: 11 (41%); 0.5272: 6 (22%) | 0.4028: 6 (22%); 0.4601: 11 (41%); 0.4965: 16 (59%); 0.5272: 21 (78%) | OFFLINE |
| dpi_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3408, 0.4361, 0.4884, 0.569 | 0.3408: 21 (78%); 0.4361: 16 (59%); 0.4884: 11 (41%); 0.569: 6 (22%) | 0.3408: 6 (22%); 0.4361: 11 (41%); 0.4884: 16 (59%); 0.569: 21 (78%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.004, 0.008, 0.0171, 0.0327 | -0.004: 21 (78%); 0.008: 16 (59%); 0.0171: 11 (41%); 0.0327: 6 (22%) | -0.004: 6 (22%); 0.008: 11 (41%); 0.0171: 16 (59%); 0.0327: 21 (78%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.4491, 25.8771, 26.7677, 27.32 | 24.4491: 21 (78%); 25.8771: 16 (59%); 26.7677: 11 (41%); 27.32: 7 (26%) | 24.4491: 6 (22%); 25.8771: 11 (41%); 26.7677: 16 (59%); 27.32: 22 (81%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.129, 0.2862, 0.736, 1.5572 | -0.129: 21 (78%); 0.2862: 16 (59%); 0.736: 11 (41%); 1.5572: 6 (22%) | -0.129: 6 (22%); 0.2862: 11 (41%); 0.736: 16 (59%); 1.5572: 21 (78%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -1.5572, -0.736, -0.2862, 0.129 | -1.5572: 21 (78%); -0.736: 16 (59%); -0.2862: 11 (41%); 0.129: 6 (22%) | -1.5572: 6 (22%); -0.736: 11 (41%); -0.2862: 16 (59%); 0.129: 21 (78%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0672, -0.0185, 0.0131, 0.0735 | -0.0672: 21 (78%); -0.0185: 16 (59%); 0.0131: 11 (41%); 0.0735: 6 (22%) | -0.0672: 6 (22%); -0.0185: 11 (41%); 0.0131: 16 (59%); 0.0735: 21 (78%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.7941, 8.3779, 8.5674, 8.9287 | 7.7941: 21 (78%); 8.3779: 16 (59%); 8.5674: 11 (41%); 8.9287: 6 (22%) | 7.7941: 6 (22%); 8.3779: 11 (41%); 8.5674: 16 (59%); 8.9287: 21 (78%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 27 (100%); 1: 7 (26%) | 0: 20 (74%); 1: 23 (85%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 0.8 | 0: 22 (81%); 0.8: 6 (22%) | 0: 21 (78%); 0.8: 21 (78%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 27 (100%); 1: 8 (30%) | 0: 19 (70%); 1: 26 (96%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 0, 5.4, 13.8, 163 | 0: 27 (100%); 5.4: 16 (59%); 13.8: 11 (41%); 163: 6 (22%) | 0: 7 (26%); 5.4: 11 (41%); 13.8: 16 (59%); 163: 21 (78%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 2.4, 69, 132.6 | 0: 27 (100%); 2.4: 16 (59%); 69: 11 (41%); 132.6: 6 (22%) | 0: 8 (30%); 2.4: 11 (41%); 69: 16 (59%); 132.6: 21 (78%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -2.9501, -1.5205, -0.685, -0.355 | -2.9501: 21 (78%); -1.5205: 16 (59%); -0.685: 11 (41%); -0.355: 6 (22%) | -2.9501: 6 (22%); -1.5205: 11 (41%); -0.685: 16 (59%); -0.355: 21 (78%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -0.1311, 0.039, 0.3493, 1.1886 | -0.1311: 21 (78%); 0.039: 16 (59%); 0.3493: 11 (41%); 1.1886: 6 (22%) | -0.1311: 6 (22%); 0.039: 11 (41%); 0.3493: 16 (59%); 1.1886: 21 (78%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | 0.6383, 0.9297, 1.4942, 3.3727 | 0.6383: 21 (78%); 0.9297: 16 (59%); 1.4942: 11 (41%); 3.3727: 6 (22%) | 0.6383: 6 (22%); 0.9297: 11 (41%); 1.4942: 16 (59%); 3.3727: 21 (78%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -1.5413, -0.8184, -0.454, -0.2589 | -1.5413: 21 (78%); -0.8184: 16 (59%); -0.454: 11 (41%); -0.2589: 6 (22%) | -1.5413: 6 (22%); -0.8184: 11 (41%); -0.454: 16 (59%); -0.2589: 21 (78%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.4602, -0.5962, -0.3655, -0.1579 | -1.4602: 21 (78%); -0.5962: 16 (59%); -0.3655: 11 (41%); -0.1579: 6 (22%) | -1.4602: 6 (22%); -0.5962: 11 (41%); -0.3655: 16 (59%); -0.1579: 21 (78%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -0.4078, -0.133, 0.2377, 0.7259 | -0.4078: 21 (78%); -0.133: 16 (59%); 0.2377: 11 (41%); 0.7259: 6 (22%) | -0.4078: 6 (22%); -0.133: 11 (41%); 0.2377: 16 (59%); 0.7259: 21 (78%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 28.774, 33.594, 37.616, 42.874 | 28.774: 21 (78%); 33.594: 16 (59%); 37.616: 11 (41%); 42.874: 6 (22%) | 28.774: 6 (22%); 33.594: 11 (41%); 37.616: 16 (59%); 42.874: 21 (78%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0133, 0.0297, 0.0508, 0.0694 | 0.0133: 21 (78%); 0.0297: 16 (59%); 0.0508: 11 (41%); 0.0694: 6 (22%) | 0.0133: 6 (22%); 0.0297: 11 (41%); 0.0508: 16 (59%); 0.0694: 21 (78%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1.2, 3.4, 6, 11.4 | 1.2: 21 (78%); 3.4: 16 (59%); 6: 12 (44%); 11.4: 6 (22%) | 1.2: 6 (22%); 3.4: 11 (41%); 6: 17 (63%); 11.4: 21 (78%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1053, 0.3166 | 0: 27 (100%); 0.1053: 12 (44%); 0.3166: 6 (22%) | 0: 13 (48%); 0.1053: 17 (63%); 0.3166: 21 (78%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2833, 0.4381, 0.5631 | 0: 27 (100%); 0.2833: 16 (59%); 0.4381: 11 (41%); 0.5631: 6 (22%) | 0: 8 (30%); 0.2833: 11 (41%); 0.4381: 16 (59%); 0.5631: 21 (78%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 5, 8 | 1: 23 (85%); 2: 19 (70%); 5: 14 (52%); 8: 7 (26%) | 1: 8 (30%); 2: 12 (44%); 5: 17 (63%); 8: 22 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1.2, 3.4, 6, 11.4 | 1.2: 21 (78%); 3.4: 16 (59%); 6: 12 (44%); 11.4: 6 (22%) | 1.2: 6 (22%); 3.4: 11 (41%); 6: 17 (63%); 11.4: 21 (78%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 4, 8 | 1: 23 (85%); 2: 18 (67%); 4: 12 (44%); 8: 7 (26%) | 1: 9 (33%); 2: 12 (44%); 4: 17 (63%); 8: 22 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.1636, 0.297, 0.4228, 0.5599 | 0.1636: 21 (78%); 0.297: 16 (59%); 0.4228: 11 (41%); 0.5599: 6 (22%) | 0.1636: 6 (22%); 0.297: 11 (41%); 0.4228: 16 (59%); 0.5599: 21 (78%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2478, 0.5105 | 0: 23 (85%); 0.2478: 11 (41%); 0.5105: 6 (22%) | 0: 12 (44%); 0.2478: 16 (59%); 0.5105: 21 (78%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.0822, 0.2495, 0.4236 | 0: 24 (89%); 0.0822: 16 (59%); 0.2495: 11 (41%); 0.4236: 6 (22%) | 0: 10 (37%); 0.0822: 11 (41%); 0.2495: 16 (59%); 0.4236: 21 (78%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0822, 0.2495, 0.4236 | 0: 24 (89%); 0.0822: 16 (59%); 0.2495: 11 (41%); 0.4236: 6 (22%) | 0: 10 (37%); 0.0822: 11 (41%); 0.2495: 16 (59%); 0.4236: 21 (78%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.3738, -0.0133, 0, 0.2388 | -0.3738: 21 (78%); -0.0133: 16 (59%); 0: 16 (59%); 0.2388: 6 (22%) | -0.3738: 6 (22%); -0.0133: 11 (41%); 0: 20 (74%); 0.2388: 21 (78%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.5262, -0.3188, 0.2141, 1.0053 | -0.5262: 21 (78%); -0.3188: 16 (59%); 0.2141: 11 (41%); 1.0053: 6 (22%) | -0.5262: 6 (22%); -0.3188: 11 (41%); 0.2141: 16 (59%); 1.0053: 21 (78%) | OFFLINE |
| otc_short_ratio_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3408, 0.4361, 0.4884, 0.569 | 0.3408: 21 (78%); 0.4361: 16 (59%); 0.4884: 11 (41%); 0.569: 6 (22%) | 0.3408: 6 (22%); 0.4361: 11 (41%); 0.4884: 16 (59%); 0.569: 21 (78%) | OFFLINE |
| otc_volume_recent | backtest/signals/congressional_alt_data.py | 100.0% | 482024.6, 1189553.6, 1738632.6, 3961661 | 482024.6: 21 (78%); 1189553.6: 16 (59%); 1738632.6: 11 (41%); 3961661: 6 (22%) | 482024.6: 6 (22%); 1189553.6: 11 (41%); 1738632.6: 16 (59%); 3961661: 21 (78%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 3, 6, 10, 11.8 | 3: 23 (85%); 6: 17 (63%); 10: 12 (44%); 11.8: 6 (22%) | 3: 8 (30%); 6: 13 (48%); 10: 19 (70%); 11.8: 21 (78%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.1099, -0.0783, -0.0682, -0.0427 | -0.1099: 21 (78%); -0.0783: 16 (59%); -0.0682: 12 (44%); -0.0427: 6 (22%) | -0.1099: 6 (22%); -0.0783: 11 (41%); -0.0682: 15 (56%); -0.0427: 21 (78%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0672, -0.0524, -0.0413, -0.0107 | -0.0672: 21 (78%); -0.0524: 17 (63%); -0.0413: 11 (41%); -0.0107: 6 (22%) | -0.0672: 6 (22%); -0.0524: 10 (37%); -0.0413: 16 (59%); -0.0107: 21 (78%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.09, -0.0629, -0.0324, -0.017 | -0.09: 21 (78%); -0.0629: 16 (59%); -0.0324: 11 (41%); -0.017: 6 (22%) | -0.09: 6 (22%); -0.0629: 11 (41%); -0.0324: 16 (59%); -0.017: 21 (78%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -8.5186, -5.0106, -3.4304, -1.8574 | -8.5186: 21 (78%); -5.0106: 16 (59%); -3.4304: 11 (41%); -1.8574: 6 (22%) | -8.5186: 6 (22%); -5.0106: 11 (41%); -3.4304: 16 (59%); -1.8574: 21 (78%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | -1.8172, -0.8276, -0.0672, 0.143 | -1.8172: 21 (78%); -0.8276: 16 (59%); -0.0672: 11 (41%); 0.143: 6 (22%) | -1.8172: 6 (22%); -0.8276: 11 (41%); -0.0672: 16 (59%); 0.143: 21 (78%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -6.7054, 6.3054, 12.6542, 26.9806 | -6.7054: 21 (78%); 6.3054: 16 (59%); 12.6542: 11 (41%); 26.9806: 6 (22%) | -6.7054: 6 (22%); 6.3054: 11 (41%); 12.6542: 16 (59%); 26.9806: 21 (78%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0603, 0.0708, 0.114, 0.1424 | 0.0603: 21 (78%); 0.0708: 16 (59%); 0.114: 11 (41%); 0.1424: 6 (22%) | 0.0603: 6 (22%); 0.0708: 11 (41%); 0.114: 16 (59%); 0.1424: 21 (78%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5143, 0.6441, 0.7856, 0.8696 | 0.5143: 21 (78%); 0.6441: 16 (59%); 0.7856: 11 (41%); 0.8696: 6 (22%) | 0.5143: 6 (22%); 0.6441: 11 (41%); 0.7856: 16 (59%); 0.8696: 21 (78%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -0.1909, 0.0726, 0.6733, 1.1553 | -0.1909: 21 (78%); 0.0726: 16 (59%); 0.6733: 11 (41%); 1.1553: 6 (22%) | -0.1909: 6 (22%); 0.0726: 11 (41%); 0.6733: 16 (59%); 1.1553: 21 (78%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -2.2634, -1.436, -1.1906, -0.7725 | -2.2634: 21 (78%); -1.436: 16 (59%); -1.1906: 11 (41%); -0.7725: 6 (22%) | -2.2634: 6 (22%); -1.436: 11 (41%); -1.1906: 16 (59%); -0.7725: 21 (78%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | 0.6963, 1.1505, 1.9364, 3.4213 | 0.6963: 21 (78%); 1.1505: 16 (59%); 1.9364: 11 (41%); 3.4213: 6 (22%) | 0.6963: 6 (22%); 1.1505: 11 (41%); 1.9364: 16 (59%); 3.4213: 21 (78%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -10.1538, -8.4598, -6.5772, -3.6874 | -10.1538: 21 (78%); -8.4598: 16 (59%); -6.5772: 11 (41%); -3.6874: 6 (22%) | -10.1538: 6 (22%); -8.4598: 11 (41%); -6.5772: 16 (59%); -3.6874: 21 (78%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 4.332, 24.252, 33.746, 50.88 | 4.332: 21 (78%); 24.252: 16 (59%); 33.746: 11 (41%); 50.88: 6 (22%) | 4.332: 6 (22%); 24.252: 11 (41%); 33.746: 16 (59%); 50.88: 21 (78%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 48.008, 48.748, 48.88, 49.406 | 48.008: 21 (78%); 48.748: 16 (59%); 48.88: 11 (41%); 49.406: 6 (22%) | 48.008: 6 (22%); 48.748: 11 (41%); 48.88: 16 (59%); 49.406: 21 (78%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 34.084, 37.186, 38.918, 39.624 | 34.084: 21 (78%); 37.186: 16 (59%); 38.918: 11 (41%); 39.624: 6 (22%) | 34.084: 6 (22%); 37.186: 11 (41%); 38.918: 16 (59%); 39.624: 21 (78%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.036, 0.0487, 0.0578, 0.0958 | 0.036: 21 (78%); 0.0487: 16 (59%); 0.0578: 11 (41%); 0.0958: 6 (22%) | 0.036: 6 (22%); 0.0487: 11 (41%); 0.0578: 16 (59%); 0.0958: 21 (78%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0843, -0.0665, -0.0454, -0.0423 | -0.0843: 21 (78%); -0.0665: 16 (59%); -0.0454: 11 (41%); -0.0423: 6 (22%) | -0.0843: 6 (22%); -0.0665: 11 (41%); -0.0454: 16 (59%); -0.0423: 22 (81%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1, 3.8 | 0: 27 (100%); 1: 12 (44%); 3.8: 6 (22%) | 0: 15 (56%); 1: 18 (67%); 3.8: 21 (78%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 28.2, 41.4, 61.8, 75.8 | 28.2: 21 (78%); 41.4: 16 (59%); 61.8: 11 (41%); 75.8: 6 (22%) | 28.2: 6 (22%); 41.4: 11 (41%); 61.8: 16 (59%); 75.8: 21 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.4663, 0.5036, 0.5323, 0.6118 | 0.4663: 21 (78%); 0.5036: 16 (59%); 0.5323: 11 (41%); 0.6118: 6 (22%) | 0.4663: 6 (22%); 0.5036: 11 (41%); 0.5323: 16 (59%); 0.6118: 21 (78%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 53.82, 119.2, 145.52, 160.1 | 53.82: 21 (78%); 119.2: 16 (59%); 145.52: 11 (41%); 160.1: 6 (22%) | 53.82: 6 (22%); 119.2: 11 (41%); 145.52: 16 (59%); 160.1: 21 (78%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -10.114, -4.822, -2.557, -1.3368 | -10.114: 21 (78%); -4.822: 16 (59%); -2.557: 11 (41%); -1.3368: 6 (22%) | -10.114: 6 (22%); -4.822: 11 (41%); -2.557: 16 (59%); -1.3368: 21 (78%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 11.788, 17.682, 20.678, 27.162 | 11.788: 21 (78%); 17.682: 16 (59%); 20.678: 11 (41%); 27.162: 6 (22%) | 11.788: 6 (22%); 17.682: 11 (41%); 20.678: 16 (59%); 27.162: 21 (78%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 10.542, 14.63, 18.824, 27.77 | 10.542: 21 (78%); 14.63: 16 (59%); 18.824: 11 (41%); 27.77: 6 (22%) | 10.542: 6 (22%); 14.63: 11 (41%); 18.824: 16 (59%); 27.77: 21 (78%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 1.132, 2.568, 7.956, 13.71 | 1.132: 21 (78%); 2.568: 16 (59%); 7.956: 11 (41%); 13.71: 6 (22%) | 1.132: 6 (22%); 2.568: 11 (41%); 7.956: 16 (59%); 13.71: 21 (78%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 4.32, 9.064, 15.038 | 0: 27 (100%); 4.32: 16 (59%); 9.064: 11 (41%); 15.038: 6 (22%) | 0: 7 (26%); 4.32: 11 (41%); 9.064: 16 (59%); 15.038: 21 (78%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9.4, 13, 15.8 | 5: 22 (81%); 9.4: 16 (59%); 13: 12 (44%); 15.8: 6 (22%) | 5: 7 (26%); 9.4: 11 (41%); 13: 18 (67%); 15.8: 21 (78%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 6.2, 9, 11, 17.8 | 6.2: 21 (78%); 9: 18 (67%); 11: 12 (44%); 17.8: 6 (22%) | 6.2: 6 (22%); 9: 12 (44%); 11: 17 (63%); 17.8: 21 (78%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 38.948, 42.872, 46.172, 48.346 | 38.948: 21 (78%); 42.872: 16 (59%); 46.172: 11 (41%); 48.346: 6 (22%) | 38.948: 6 (22%); 42.872: 11 (41%); 46.172: 16 (59%); 48.346: 21 (78%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2, 0.6151, 0.7413, 0.9119 | 0.2: 21 (78%); 0.6151: 16 (59%); 0.7413: 11 (41%); 0.9119: 6 (22%) | 0.2: 6 (22%); 0.6151: 11 (41%); 0.7413: 16 (59%); 0.9119: 21 (78%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.96, 18.886, 20.448, 29.43 | 15.96: 21 (78%); 18.886: 16 (59%); 20.448: 11 (41%); 29.43: 6 (22%) | 15.96: 6 (22%); 18.886: 11 (41%); 20.448: 16 (59%); 29.43: 21 (78%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.96, 18.886, 20.448, 29.43 | 15.96: 21 (78%); 18.886: 16 (59%); 20.448: 11 (41%); 29.43: 6 (22%) | 15.96: 6 (22%); 18.886: 11 (41%); 20.448: 16 (59%); 29.43: 21 (78%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8884, 0.9023, 0.9295, 0.9646 | 0.8884: 22 (81%); 0.9023: 16 (59%); 0.9295: 11 (41%); 0.9646: 6 (22%) | 0.8884: 7 (26%); 0.9023: 11 (41%); 0.9295: 16 (59%); 0.9646: 21 (78%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.686, 0.844, 0.952, 1.396 | 0.686: 21 (78%); 0.844: 16 (59%); 0.952: 11 (41%); 1.396: 6 (22%) | 0.686: 6 (22%); 0.844: 11 (41%); 0.952: 16 (59%); 1.396: 21 (78%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.026, 0.0465, 0.0928, 0.163 | 0.026: 21 (78%); 0.0465: 17 (63%); 0.0928: 11 (41%); 0.163: 6 (22%) | 0.026: 6 (22%); 0.0465: 11 (41%); 0.0928: 16 (59%); 0.163: 21 (78%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 30.7292, 61.7586, 101.075, 129.698 | 30.7292: 21 (78%); 61.7586: 16 (59%); 101.075: 11 (41%); 129.698: 6 (22%) | 30.7292: 6 (22%); 61.7586: 11 (41%); 101.075: 16 (59%); 129.698: 21 (78%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 30.0028, 60.6161, 97.7149, 126.5817 | 30.0028: 21 (78%); 60.6161: 16 (59%); 97.7149: 11 (41%); 126.5817: 6 (22%) | 30.0028: 6 (22%); 60.6161: 11 (41%); 97.7149: 16 (59%); 126.5817: 21 (78%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 28.2675, 59.4737, 86.6801, 123.4654 | 28.2675: 21 (78%); 59.4737: 16 (59%); 86.6801: 11 (41%); 123.4654: 6 (22%) | 28.2675: 6 (22%); 59.4737: 11 (41%); 86.6801: 16 (59%); 123.4654: 21 (78%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 32.982, 64.8353, 104.4352, 136.6228 | 32.982: 21 (78%); 64.8353: 16 (59%); 104.4352: 11 (41%); 136.6228: 6 (22%) | 32.982: 6 (22%); 64.8353: 11 (41%); 104.4352: 16 (59%); 136.6228: 21 (78%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 34.9233, 73.2486, 107.7953, 151.9736 | 34.9233: 21 (78%); 73.2486: 16 (59%); 107.7953: 11 (41%); 151.9736: 6 (22%) | 34.9233: 6 (22%); 73.2486: 11 (41%); 107.7953: 16 (59%); 151.9736: 21 (78%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 27 (100%) | 0: 24 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 27 (100%) | 0: 22 (81%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1223, -0.0589, -0.0452, -0.0266 | -0.1223: 21 (78%); -0.0589: 16 (59%); -0.0452: 11 (41%); -0.0266: 6 (22%) | -0.1223: 6 (22%); -0.0589: 11 (41%); -0.0452: 16 (59%); -0.0266: 21 (78%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -86.098, -80.778, -77.008, -72.756 | -86.098: 21 (78%); -80.778: 16 (59%); -77.008: 11 (41%); -72.756: 6 (22%) | -86.098: 6 (22%); -80.778: 11 (41%); -77.008: 16 (59%); -72.756: 21 (78%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.316, 0.6768, 1.2341, 1.6279 | 0.316: 21 (78%); 0.6768: 16 (59%); 1.2341: 11 (41%); 1.6279: 6 (22%) | 0.316: 6 (22%); 0.6768: 11 (41%); 1.2341: 16 (59%); 1.6279: 21 (78%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 3.4, 8.6, 10 | 2: 22 (81%); 3.4: 16 (59%); 8.6: 11 (41%); 10: 9 (33%) | 2: 7 (26%); 3.4: 11 (41%); 8.6: 16 (59%); 10: 27 (100%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.1917, 0.2971, 0.4029, 0.5518 | 0.1917: 21 (78%); 0.2971: 16 (59%); 0.4029: 11 (41%); 0.5518: 6 (22%) | 0.1917: 6 (22%); 0.2971: 11 (41%); 0.4029: 16 (59%); 0.5518: 21 (78%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 2, 7.4, 10 | 2: 24 (89%); 7.4: 16 (59%); 10: 12 (44%) | 2: 7 (26%); 7.4: 11 (41%); 10: 27 (100%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0204, 0.0321, 0.0441, 0.0609 | 0.0204: 21 (78%); 0.0321: 16 (59%); 0.0441: 11 (41%); 0.0609: 6 (22%) | 0.0204: 6 (22%); 0.0321: 11 (41%); 0.0441: 16 (59%); 0.0609: 21 (78%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 1.2, 5.4, 7, 8.8 | 1.2: 21 (78%); 5.4: 16 (59%); 7: 13 (48%); 8.8: 6 (22%) | 1.2: 6 (22%); 5.4: 11 (41%); 7: 17 (63%); 8.8: 21 (78%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.1046, 0.0805, 0.1778, 0.7758 | -0.1046: 21 (78%); 0.0805: 16 (59%); 0.1778: 11 (41%); 0.7758: 6 (22%) | -0.1046: 6 (22%); 0.0805: 11 (41%); 0.1778: 16 (59%); 0.7758: 21 (78%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 4, 6, 6.6, 10 | 4: 24 (89%); 6: 17 (63%); 6.6: 11 (41%); 10: 8 (30%) | 4: 7 (26%); 6: 16 (59%); 6.6: 16 (59%); 10: 27 (100%) | OFFLINE |
| year_low | backtest/signals/technical.py | 100.0% | 19.287, 41.1202, 63.666, 111.97 | 19.287: 21 (78%); 41.1202: 16 (59%); 63.666: 11 (41%); 111.97: 6 (22%) | 19.287: 6 (22%); 41.1202: 11 (41%); 63.666: 16 (59%); 111.97: 21 (78%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.0% |
| 8k_item_5_02_filed_within_7d | 4.0% |
| above_avwap_20low | 74.1% |
| above_avwap_252low | 96.0% |
| above_avwap_50low | 37.0% |
| above_cam_r3 | 22.2% |
| above_cam_r4 | 18.5% |
| above_cpr | 44.4% |
| above_pivot | 44.4% |
| above_prev_high | 22.2% |
| above_prev_low | 81.5% |
| above_r1 | 18.5% |
| above_r2 | 7.4% |
| above_vwap | 70.4% |
| above_wood_p | 37.0% |
| ad_rising | 37.0% |
| adx_di_bear | 92.6% |
| adx_di_bull | 7.4% |
| adx_strong | 3.7% |
| adx_trending | 48.1% |
| ao_cross_dn | 3.7% |
| ao_positive | 40.7% |
| at_key_fib | 48.1% |
| at_key_fib_wide | 70.4% |
| avwap_20low_loss_recent_3d | 31.2% |
| avwap_20low_reclaim_recent_3d | 37.5% |
| avwap_252low_loss_recent_3d | 4.0% |
| avwap_252low_reclaim_recent_3d | 4.0% |
| avwap_50low_loss_recent_3d | 37.0% |
| avwap_50low_reclaim_recent_3d | 18.5% |
| bb_10_20_expanding | 59.3% |
| bb_10_20_pctb_lt_05 | 11.1% |
| bb_10_20_pctb_lt_1 | 22.2% |
| bb_10_20_pctb_lt_15 | 29.6% |
| bb_10_20_pctb_lt_2 | 48.1% |
| bb_10_20_pctb_lt_25 | 63.0% |
| bb_10_20_reclaim_from_lower_recent_3d | 29.6% |
| bb_10_20_squeeze | 22.2% |
| bb_10_20_touch_lower | 7.4% |
| bb_20_15_expanding | 81.5% |
| bb_20_15_pctb_lt_05 | 63.0% |
| bb_20_15_pctb_lt_1 | 77.8% |
| bb_20_15_pctb_lt_15 | 92.6% |
| bb_20_15_pctb_lt_2 | 96.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 37.0% |
| bb_20_15_squeeze | 33.3% |
| bb_20_15_touch_lower | 59.3% |
| bb_20_20_expanding | 81.5% |
| bb_20_20_pctb_lt_05 | 22.2% |
| bb_20_20_pctb_lt_1 | 29.6% |
| bb_20_20_pctb_lt_15 | 51.9% |
| bb_20_20_pctb_lt_2 | 77.8% |
| bb_20_20_pctb_lt_25 | 92.6% |
| bb_20_20_reclaim_from_lower_recent_3d | 25.9% |
| bb_20_20_squeeze | 14.8% |
| bb_20_20_touch_lower | 14.8% |
| bearish_pin_bar | 7.4% |
| below_avwap_20low | 25.9% |
| below_avwap_252low | 4.0% |
| below_avwap_50low | 63.0% |
| below_cam_s3 | 18.5% |
| below_cam_s4 | 7.4% |
| below_cpr | 51.9% |
| below_ema_200 | 7.4% |
| below_ema_200_break_recent_5d | 7.4% |
| below_ema_20_break_recent_5d | 63.0% |
| below_ema_21_break_recent_5d | 66.7% |
| below_ema_50 | 22.2% |
| below_ema_50_break_recent_5d | 22.2% |
| below_ema_9_break_recent_5d | 48.1% |
| below_prev_high | 77.8% |
| below_prev_low | 18.5% |
| below_prev_low_clearance_atr_05 | 3.7% |
| below_s1 | 7.4% |
| below_s2 | 3.7% |
| below_sma_200 | 3.7% |
| below_sma_50 | 33.3% |
| below_vwap | 29.6% |
| bullish_pin_bar | 7.4% |
| chandelier_long_bullish | 7.4% |
| chandelier_long_flip_dn | 7.4% |
| close_in_bottom_40pct_of_range | 18.5% |
| close_in_top_40pct_of_range | 66.7% |
| cmf_cross_up | 3.7% |
| cmf_negative | 40.7% |
| cmf_positive | 59.3% |
| concentrated_sell | 18.5% |
| cpr_narrow_tight | 44.4% |
| cup_handle_detected | 3.7% |
| dc10_breakout_dn | 29.6% |
| dc10_breakout_dn_1pct | 33.3% |
| dc10_strong_breakout_dn | 3.7% |
| dc20_breakout_dn | 18.5% |
| dc20_support_break_retest_strong | 25.9% |
| defensive_leadership | 66.7% |
| director_only_buy | 3.7% |
| doji | 14.8% |
| double_bottom_detected | 18.5% |
| double_top_detected | 11.1% |
| dpi_elevated | 37.0% |
| drying_volume_on_up_turn | 63.0% |
| ema_50_200_bearish | 11.1% |
| ema_50_200_bullish | 88.9% |
| ema_9_21_bearish | 81.5% |
| ema_9_21_bullish | 18.5% |
| ema_9_21_death_cross | 22.2% |
| force_index_cross_dn | 3.7% |
| force_index_positive | 3.7% |
| gap_dn_1_5pct | 22.2% |
| gap_dn_2pct | 11.1% |
| gap_up_1_5pct | 3.7% |
| hammer | 7.4% |
| head_shoulders_top_detected | 3.7% |
| house_cluster_buy | 3.7% |
| htf_aligned_bull | 88.9% |
| hull_bearish | 92.6% |
| hull_bullish | 7.4% |
| ichi_above_cloud | 96.3% |
| ichi_above_cloud_break_recent_5d | 7.4% |
| ichi_tk_bearish | 59.3% |
| ichi_tk_bullish | 33.3% |
| ichi_tk_cross_dn | 11.1% |
| ichi_weekly_above_cloud | 56.0% |
| ichi_weekly_below_cloud | 12.0% |
| ichi_weekly_in_cloud | 32.0% |
| inside_bar | 14.8% |
| inside_cpr | 3.7% |
| institutional_buy | 70.4% |
| institutional_negative | 14.8% |
| institutional_persistence_growing | 50.0% |
| institutional_persistence_strong | 70.0% |
| institutional_strong_buy | 70.4% |
| inverted_cup_handle_detected | 3.7% |
| is_friday | 22.2% |
| is_halloween_period | 44.4% |
| is_january | 3.7% |
| is_january_extended | 3.7% |
| is_monday | 29.6% |
| is_summer_period | 55.6% |
| is_totm_window | 22.2% |
| is_totm_window_first_day | 7.4% |
| is_week_open | 29.6% |
| macd_8_21_5_crossover_dn | 3.7% |
| mfi_broad_oversold | 25.9% |
| mfi_oversold | 3.7% |
| monthly_above_sma_12 | 96.0% |
| monthly_bias_bull | 96.0% |
| monthly_momentum_pos | 96.0% |
| morning_star | 7.4% |
| near_52w_high_95pct | 3.7% |
| near_52w_high_retest_long | 14.8% |
| near_avwap_20high_atr_05x | 7.4% |
| near_avwap_20high_atr_10x | 29.6% |
| near_avwap_20high_atr_15x | 66.7% |
| near_avwap_20high_atr_20x | 88.9% |
| near_avwap_20low_atr_05x | 62.5% |
| near_avwap_20low_atr_10x | 81.2% |
| near_avwap_20low_atr_15x | 87.5% |
| near_avwap_252low_atr_05x | 12.0% |
| near_avwap_252low_atr_10x | 16.0% |
| near_avwap_252low_atr_15x | 16.0% |
| near_avwap_252low_atr_20x | 20.0% |
| near_avwap_50low_atr_05x | 74.1% |
| near_avwap_50low_atr_10x | 96.3% |
| near_cam_r3 | 7.4% |
| near_cam_s3 | 18.5% |
| near_cam_s4 | 7.4% |
| near_fib_236 | 3.7% |
| near_fib_382 | 7.4% |
| near_fib_500 | 37.0% |
| near_fib_618 | 3.7% |
| near_pivot | 18.5% |
| near_prev_close | 11.1% |
| near_prev_high | 7.4% |
| near_prev_low | 22.2% |
| near_r1 | 3.7% |
| near_r1_wide | 37.0% |
| near_r2 | 7.4% |
| near_r2_wide | 29.6% |
| near_s1 | 7.4% |
| near_s1_wide | 51.9% |
| near_s2_wide | 18.5% |
| near_wood_r1 | 7.4% |
| near_wood_s1 | 14.8% |
| news_uses_polygon_score | 40.7% |
| obv_bearish | 96.3% |
| obv_bullish | 3.7% |
| obv_diverge_bull | 11.1% |
| obv_falling | 85.2% |
| obv_rising | 14.8% |
| outside_bar | 18.5% |
| pead_negative_surprise | 8.3% |
| pead_positive_surprise | 25.0% |
| pin_bar | 14.8% |
| po3_accumulation_active | 14.8% |
| po3_bullish | 37.0% |
| po3_manipulation_sweep_down | 7.4% |
| po3_manipulation_sweep_up | 3.7% |
| po3_mmbm_setup | 3.7% |
| po3_sweep_above_prior_high | 40.7% |
| po3_sweep_below_prior_low | 66.7% |
| price_above_ema_200 | 92.6% |
| price_above_ema_200_break_recent_5d | 7.4% |
| price_above_ema_50 | 77.8% |
| price_above_ema_50_break_recent_5d | 33.3% |
| price_above_hull | 29.6% |
| price_above_sma_200 | 96.3% |
| price_above_sma_50 | 66.7% |
| price_above_tema | 14.8% |
| price_below_hull | 70.4% |
| price_below_tema | 85.2% |
| psar_bullish | 3.7% |
| risk_off_regime_bond_signal | 18.5% |
| risk_off_regime_bond_signal_strong | 14.8% |
| risk_off_regime_gold_signal | 37.0% |
| risk_on_regime_bond_signal | 55.6% |
| risk_on_regime_bond_signal_strong | 29.6% |
| rsi_14_rising | 51.9% |
| rsi_21_bullish | 11.1% |
| rsi_21_rising | 51.9% |
| rsi_2_bullish | 22.2% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 7.4% |
| rsi_2_cross_dn_overbought_recent_3d | 22.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 59.3% |
| rsi_2_cross_up_oversold_recent_3d | 48.1% |
| rsi_2_extreme_os | 37.0% |
| rsi_2_overbought | 3.7% |
| rsi_2_oversold | 51.9% |
| rsi_2_rising | 51.9% |
| rsi_9_cross_up_oversold_recent_3d | 14.8% |
| rsi_9_oversold | 3.7% |
| rsi_9_rising | 51.9% |
| s1_break_retest_short | 96.3% |
| sc_13g_filed_within_30d | 8.0% |
| shooting_star | 3.7% |
| sma_50_200_bullish | 96.3% |
| sma_9_21_bullish | 11.1% |
| smc_bos_bullish | 37.0% |
| smc_bos_retest_long | 3.7% |
| smc_breaker_block_bearish | 11.1% |
| smc_breaker_block_bullish | 37.0% |
| smc_choch_bullish | 11.1% |
| smc_equal_highs_swept | 22.2% |
| smc_equal_lows_swept | 3.7% |
| smc_fvg_bearish_active | 81.5% |
| smc_fvg_bullish_active | 14.8% |
| smc_fvg_retest_long_zone | 11.1% |
| smc_fvg_retest_short_zone | 14.8% |
| smc_in_discount_zone | 77.8% |
| smc_inverse_fvg_bullish | 96.3% |
| smc_ob_bullish_active | 88.9% |
| smc_ote_short_zone | 3.7% |
| squeeze_in | 7.4% |
| stoch_bearish_cross | 3.7% |
| stoch_broad_oversold | 74.1% |
| stoch_bullish_cross | 25.9% |
| stoch_oversold | 63.0% |
| stochrsi_cross_up | 55.6% |
| stochrsi_oversold | 81.5% |
| supertrend_flip_recent_long_5d | 3.7% |
| supertrend_flip_recent_short_5d | 3.7% |
| supertrend_flip_up | 3.7% |
| support_break_retest | 44.4% |
| tema_cross_dn | 3.7% |
| three_white_soldiers | 3.7% |
| triangle_ascending_detected | 14.8% |
| triangle_descending_detected | 11.1% |
| usd_strengthening | 33.3% |
| vix_band_high | 51.9% |
| vix_band_low | 33.3% |
| vix_band_mid | 14.8% |
| vix_term_backwardation | 14.8% |
| vix_term_contango | 85.2% |
| vol_above_avg | 37.0% |
| vol_below_avg | 63.0% |
| vol_spike_12x | 22.2% |
| vol_spike_15x | 18.5% |
| vol_spike_17x | 7.4% |
| vp_close_above_poc | 55.6% |
| vp_close_below_poc | 44.4% |
| week_open_gap_down_15pct | 7.4% |
| week_open_gap_up_15pct | 3.7% |
| williams_r_oversold | 48.1% |
| williams_r_rising | 81.5% |
| within_pead_window | 44.4% |
| xs_avoid_high_ivol | 51.9% |
| xs_avoid_high_max | 77.8% |
| xs_high_beta_decile | 40.7% |
| xs_low_beta_bottom_quintile | 40.7% |
| xs_low_beta_decile | 25.9% |
| xs_low_beta_decile_entry_recent_5d | 7.4% |
| xs_low_beta_top_quintile | 25.9% |
| xs_momentum_bottom_decile | 3.7% |
| xs_momentum_bottom_quintile | 7.4% |
| xs_momentum_top_decile | 29.6% |
| xs_momentum_top_quintile | 37.0% |
| xs_quality_bottom_quintile | 26.3% |
| xs_quality_top_quintile | 21.1% |
| xs_quality_top_tercile | 42.1% |
| yoy_surprise_high | 53.8% |
| yoy_surprise_negative | 38.5% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 74.1% |
| committed_growth_holders | 74.1% |
| cot_rut_commercials_pctile_3y | 55.6% |
| cot_rut_mmoney_pctile_3y | 55.6% |
| days_since_deletion | 18.5% |
| days_since_inclusion | 14.8% |
| days_to_next_holiday | 70.4% |
| days_to_rebalance | 11.1% |
| earnings_announcement_return | 88.9% |
| earnings_eps_yoy_growth | 96.3% |
| gov_contracts_4q_sum | 59.3% |
| gov_contracts_last_qtr_amount | 59.3% |
| gov_contracts_qoq_growth | 59.3% |
| lobbying_amount_1y | 81.5% |
| lobbying_amount_q | 81.5% |
| lobbying_amount_yoy | 81.5% |
| monthly_momentum_6m | 92.6% |
| pair_half_life | 92.6% |
| pair_max_abs_zscore | 92.6% |
| pair_zscore_signed | 92.6% |
| pct_from_avwap_20low | 59.3% |
| pct_from_avwap_252low | 92.6% |
| persistent_holders_4q | 74.1% |
| persistent_holders_8q | 74.1% |
| search_volume_index_recent | 81.5% |
| search_volume_observations | 81.5% |
| search_volume_zscore_30d | 81.5% |
| short_interest_pct | 92.6% |
| total_active_holders | 74.1% |
| triangle_breakdown_pct | 11.1% |
| xs_quality_decile | 70.4% |
| xs_quality_gross_profitability | 70.4% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.996), `avwap_252low` (0.986), `avwap_50low` (0.997), `bb_10_20_lower` (0.996), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.996), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.996), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.997), `cam_r2` (0.996), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.997), `cam_s2` (0.996), `cam_s3` (0.996), `cam_s4` (0.996), `chandelier_long_value` (0.998), `chandelier_short_value` (0.998), `corp_donations_1y` (1.0), `corp_donations_count_1y` (1.0), `corp_donations_unique_pacs` (1.0), `cpr_bottom` (0.996), `cpr_top` (0.996), `dc10_lower` (0.996), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.995), `dc20_mid` (0.998), `dc20_upper` (0.998), `dema` (0.999), `double_bottom_neckline` (1.0), `double_bottom_trough` (1.0), `double_top_neckline` (1.0), `double_top_peak` (1.0), `entry_stop_long` (0.995), `entry_stop_short` (0.999), `fib_236` (0.997), `fib_382` (0.996), `fib_500` (0.995), `fib_618` (0.993), `fib_786` (0.987), `fib_ext_127` (0.995), `fib_ext_162` (0.991), `hull_ma` (0.997), `ichi_kijun` (0.998), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.99), `ichi_tenkan` (0.999), `kc_lower` (0.996), `kc_mid` (0.999), `kc_upper` (0.999), `monthly_close` (0.997), `monthly_sma_12` (0.987), `monthly_sma_6` (0.989), `pivot` (0.996), `prev_close` (0.997), `prev_high` (0.996), `prev_low` (0.996), `psar_value` (0.997), `r1` (0.996), `r2` (0.996), `r3` (0.998), `s1` (0.997), `s2` (0.996), `s3` (0.992), `supertrend_value` (0.99), `swing_high` (0.998), `swing_low` (0.981), `tema` (0.996), `triangle_breakout_pct` (1.0), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.985), `vp_value_area_high` (0.997), `vp_value_area_low` (0.987), `weekly_close` (0.997), `weekly_ema_10` (0.997), `weekly_ema_20` (0.996), `wood_p` (0.996), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.996), `wood_s2` (0.995), `year_high` (0.995)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | weekly ema pair | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2 | rsi_14 < 45 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     1 x 5 = 5
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 5 = 5
```

B-row candidates NOT in this factorial: 432 census axes join it only when REGISTERED at the T3 band review.
