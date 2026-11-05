# Table A - rsi_oversold_with_smart_money_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 55a39e45e | commit 55a39e45e at 2026-11-05 11:51:33 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** smart_money_sleeve | **status:** NOT-STARTED | **R5 fires:** 2753 (closed fires in the exit cube: 2753 of 2753, S6-B3258) | **surviving fires (T1):** 143 (survives_pct 0.0519)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/technical.py (f-string template) +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  rsi_14 < 35   [EXISTING-THRESHOLD]
P3  _has_smart_money_buy(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_rsi_oversold_with_smart_money_long (docstring and return dropped):

```python
base_fires = s.get('rsi_14', 50) < 35 and s.get('price_above_ema_200', False)
fires = base_fires and _has_smart_money_buy(s)
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
| P1 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/technical.py (f-string template) +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - producer_variant_table.SPECS['bollinger_lower'] P3/P4; backtest/signals/technical.py compute_ema_sma | SPECS bollinger_lower P3/P4 (T3/Q2-APPROVED 2026-09-27): production 200 + resim spans [9, 20, 21, 50, 100, 150, 250] | 200 | 9, 20, 21, 50, 100, 150, 200, 250 | offline 0 of 8 levels - canon-span FLAGS (above/below ema 9/20/21/50/200) ARE persisted - measured 200-of-200 bollinger fires, S6-B3117b; offline as ADD-A-CONDITION legs only. The SWAP of the gate span, and non-canon spans, are RESIM | the whole band except production (resim_band [9, 20, 21, 50, 100, 150, 250]); env STRAT_EMA_SPAN does not reach this gate - it reads the literal key - DEFINED-NO-ACTUATOR here (S6-B3253) | T3 review before any grid |
| P2 | STRATEGY | rsi_14 `< 35` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 35` | production + 4 tighter measured levels | offline 4 of 5 levels - measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P2.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | offline 0 of 3 levels - none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY-HELPER | _has_smart_money_buy(s) - underlying condition: insider_cluster_active OR cfo_buy OR large_dollar_buy OR institutional_strong_buy OR institutional_buy | requires one smart-money buy flag on the fire bar | any of 5 | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = a NARROWER union of the persisted flags (an EVENT-only subset, say) - OFFLINE subset | a wider union admits fires the engine never recorded - RESIM; a helper shared by the smart-money sleeves, so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | `< 35` | 100.0% | TIGHTER = LOWER the ceiling: 30.574 -> 29 (20%); 32.428 -> 57 (40%); 33.514 -> 86 (60%); 34.246 -> 114 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 22.358, 26.384, 29.394, 33.924 | 22.358: 114 (80%); 26.384: 86 (60%); 29.394: 57 (40%); 33.924: 29 (20%) | 22.358: 29 (20%); 26.384: 57 (40%); 29.394: 86 (60%); 33.924: 114 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 32.922, 35.178, 37.026, 40.466 | 32.922: 114 (80%); 35.178: 86 (60%); 37.026: 57 (40%); 40.466: 29 (20%) | 32.922: 29 (20%); 35.178: 57 (40%); 37.026: 86 (60%); 40.466: 114 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 11.32, 13.036, 14.69, 16.086 | 11.32: 114 (80%); 13.036: 86 (60%); 14.69: 58 (41%); 16.086: 29 (20%) | 11.32: 29 (20%); 13.036: 57 (40%); 14.69: 87 (61%); 16.086: 114 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -18.1483, -9.2698, -5.4663, -2.8575 | -18.1483: 114 (80%); -9.2698: 86 (60%); -5.4663: 57 (40%); -2.8575: 29 (20%) | -18.1483: 29 (20%); -9.2698: 57 (40%); -5.4663: 86 (60%); -2.8575: 114 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.556, 3.0003, 4.6742, 6.8365 | 1.556: 114 (80%); 3.0003: 86 (60%); 4.6742: 57 (40%); 6.8365: 29 (20%) | 1.556: 29 (20%); 3.0003: 57 (40%); 4.6742: 86 (60%); 6.8365: 114 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.556, 3.0003, 4.6742, 6.8365 | 1.556: 114 (80%); 3.0003: 86 (60%); 4.6742: 57 (40%); 6.8365: 29 (20%) | 1.556: 29 (20%); 3.0003: 57 (40%); 4.6742: 86 (60%); 6.8365: 114 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.5756, 2.9894, 3.5194, 4.376 | 2.5756: 114 (80%); 2.9894: 86 (60%); 3.5194: 57 (40%); 4.376: 29 (20%) | 2.5756: 29 (20%); 2.9894: 57 (40%); 3.5194: 86 (60%); 4.376: 114 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.1008, 0.1437, 0.1894, 0.2288 | 0.1008: 114 (80%); 0.1437: 86 (60%); 0.1894: 57 (40%); 0.2288: 29 (20%) | 0.1008: 29 (20%); 0.1437: 57 (40%); 0.1894: 86 (60%); 0.2288: 114 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.0692, 0.1303, 0.1871, 0.2492 | 0.0692: 114 (80%); 0.1303: 86 (60%); 0.1871: 57 (40%); 0.2492: 29 (20%) | 0.0692: 29 (20%); 0.1303: 57 (40%); 0.1871: 86 (60%); 0.2492: 114 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0976, 0.1217, 0.1428, 0.183 | 0.0976: 114 (80%); 0.1217: 86 (60%); 0.1428: 57 (40%); 0.183: 29 (20%) | 0.0976: 29 (20%); 0.1217: 57 (40%); 0.1428: 86 (60%); 0.183: 114 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | -0.2571, -0.1598, -0.1, 0.002 | -0.2571: 114 (80%); -0.1598: 86 (60%); -0.1: 57 (40%); 0.002: 30 (21%) | -0.2571: 29 (20%); -0.1598: 57 (40%); -0.1: 86 (60%); 0.002: 115 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.1302, 0.1623, 0.1904, 0.244 | 0.1302: 114 (80%); 0.1623: 86 (60%); 0.1904: 57 (40%); 0.244: 29 (20%) | 0.1302: 29 (20%); 0.1623: 57 (40%); 0.1904: 86 (60%); 0.244: 114 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | -0.0679, 0.0052, 0.0501, 0.1265 | -0.0679: 114 (80%); 0.0052: 86 (60%); 0.0501: 57 (40%); 0.1265: 30 (21%) | -0.0679: 29 (20%); 0.0052: 57 (40%); 0.0501: 86 (60%); 0.1265: 115 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.038, -0.0145, 0.0105, 0.0586 | -0.038: 114 (80%); -0.0145: 86 (60%); 0.0105: 57 (40%); 0.0586: 30 (21%) | -0.038: 29 (20%); -0.0145: 59 (41%); 0.0105: 86 (60%); 0.0586: 119 (83%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1366, 0.1556, 0.1743, 0.2145 | 0.1366: 113 (79%); 0.1556: 82 (57%); 0.1743: 61 (43%); 0.2145: 29 (20%) | 0.1366: 30 (21%); 0.1556: 61 (43%); 0.1743: 82 (57%); 0.2145: 114 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 143 (100%) | 0: 139 (97%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.192, -0.1109, -0.0512, 0.0331 | -0.192: 114 (80%); -0.1109: 86 (60%); -0.0512: 57 (40%); 0.0331: 29 (20%) | -0.192: 29 (20%); -0.1109: 57 (40%); -0.0512: 86 (60%); 0.0331: 114 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 143 (100%); 1: 54 (38%) | 0: 89 (62%); 1: 119 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2406, -0.197, -0.1585, -0.1375 | -0.2406: 114 (80%); -0.197: 91 (64%); -0.1585: 59 (41%); -0.1375: 31 (22%) | -0.2406: 29 (20%); -0.197: 58 (41%); -0.1585: 87 (61%); -0.1375: 117 (82%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1833, 0.55, 0.632, 0.7641 | 0.1833: 114 (80%); 0.55: 86 (60%); 0.632: 57 (40%); 0.7641: 29 (20%) | 0.1833: 29 (20%); 0.55: 57 (40%); 0.632: 86 (60%); 0.7641: 114 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.4423, 0.7064, 0.8846 | 0.2564: 118 (83%); 0.4423: 91 (64%); 0.7064: 57 (40%); 0.8846: 36 (25%) | 0.2564: 30 (21%); 0.4423: 59 (41%); 0.7064: 86 (60%); 0.8846: 119 (83%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1503, -0.0474, -0.0046, 0.1195 | -0.1503: 114 (80%); -0.0474: 87 (61%); -0.0046: 57 (40%); 0.1195: 29 (20%) | -0.1503: 29 (20%); -0.0474: 60 (42%); -0.0046: 86 (60%); 0.1195: 114 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1923, 0.3654, 0.4525, 0.6705 | 0.1923: 115 (80%); 0.3654: 89 (62%); 0.4525: 57 (40%); 0.6705: 29 (20%) | 0.1923: 31 (22%); 0.3654: 60 (42%); 0.4525: 86 (60%); 0.6705: 114 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1949, 0.3526, 0.4551, 0.6448 | 0.1949: 114 (80%); 0.3526: 89 (62%); 0.4551: 60 (42%); 0.6448: 29 (20%) | 0.1949: 29 (20%); 0.3526: 61 (43%); 0.4551: 87 (61%); 0.6448: 114 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.5046, -0.2796, -0.1772, 0.0839 | -0.5046: 119 (83%); -0.2796: 87 (61%); -0.1772: 57 (40%); 0.0839: 32 (22%) | -0.5046: 32 (22%); -0.2796: 63 (44%); -0.1772: 86 (60%); 0.0839: 119 (83%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3039, 0.5564, 0.6987, 0.9589 | 0.3039: 114 (80%); 0.5564: 86 (60%); 0.6987: 63 (44%); 0.9589: 29 (20%) | 0.3039: 29 (20%); 0.5564: 57 (40%); 0.6987: 93 (65%); 0.9589: 114 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0705, 0.3192, 0.4525, 0.7821 | 0.0705: 120 (84%); 0.3192: 86 (60%); 0.4525: 57 (40%); 0.7821: 30 (21%) | 0.0705: 30 (21%); 0.3192: 57 (40%); 0.4525: 86 (60%); 0.7821: 115 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0694, -0.0521, -0.0354, 0 | -0.0694: 116 (81%); -0.0521: 87 (61%); -0.0354: 59 (41%); 0: 46 (32%) | -0.0694: 31 (22%); -0.0521: 58 (41%); -0.0354: 90 (63%); 0: 142 (99%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3705, 0.6154, 0.8397, 1 | 0.3705: 114 (80%); 0.6154: 87 (61%); 0.8397: 61 (43%); 1: 36 (25%) | 0.3705: 29 (20%); 0.6154: 61 (43%); 0.8397: 88 (62%); 1: 143 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1821, 0.3141, 0.609, 0.9231 | 0.1821: 114 (80%); 0.3141: 88 (62%); 0.609: 64 (45%); 0.9231: 33 (23%) | 0.1821: 29 (20%); 0.3141: 61 (43%); 0.609: 91 (64%); 0.9231: 116 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0324, 0.0847, 0.1451, 0.3264 | 0.0324: 115 (80%); 0.0847: 86 (60%); 0.1451: 60 (42%); 0.3264: 29 (20%) | 0.0324: 30 (21%); 0.0847: 57 (40%); 0.1451: 90 (63%); 0.3264: 114 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.7692, 0.9231, 0.9615, 0.9872 | 0.7692: 115 (80%); 0.9231: 88 (62%); 0.9615: 66 (46%); 0.9872: 33 (23%) | 0.7692: 33 (23%); 0.9231: 58 (41%); 0.9615: 92 (64%); 0.9872: 120 (84%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1045, 0.3304, 0.4744, 0.6141 | 0.1045: 114 (80%); 0.3304: 86 (60%); 0.4744: 61 (43%); 0.6141: 29 (20%) | 0.1045: 29 (20%); 0.3304: 57 (40%); 0.4744: 89 (62%); 0.6141: 114 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0249, 0.0564, 0.1225, 0.1603 | -0.0249: 114 (80%); 0.0564: 86 (60%); 0.1225: 61 (43%); 0.1603: 34 (24%) | -0.0249: 29 (20%); 0.0564: 57 (40%); 0.1225: 89 (62%); 0.1603: 117 (82%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.3185, 0.0036, 0.0489, 0.1115 | -0.3185: 114 (80%); 0.0036: 86 (60%); 0.0489: 57 (40%); 0.1115: 29 (20%) | -0.3185: 29 (20%); 0.0036: 57 (40%); 0.0489: 86 (60%); 0.1115: 114 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1654, 0.582, 0.8475, 0.9808 | 0.1654: 114 (80%); 0.582: 86 (60%); 0.8475: 57 (40%); 0.9808: 33 (23%) | 0.1654: 29 (20%); 0.582: 57 (40%); 0.8475: 86 (60%); 0.9808: 122 (85%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1154, 0.2936, 0.5449, 0.8269 | 0.1154: 119 (83%); 0.2936: 86 (60%); 0.5449: 59 (41%); 0.8269: 32 (22%) | 0.1154: 36 (25%); 0.2936: 57 (40%); 0.5449: 90 (63%); 0.8269: 120 (84%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0997, 0.2488, 0.4536, 0.8272 | 0.0997: 114 (80%); 0.2488: 86 (60%); 0.4536: 57 (40%); 0.8272: 29 (20%) | 0.0997: 29 (20%); 0.2488: 57 (40%); 0.4536: 86 (60%); 0.8272: 114 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.6% | 23, 56, 90, 148 | 23: 113 (79%); 56: 85 (59%); 90: 57 (40%); 148: 29 (20%) | 23: 29 (20%); 56: 59 (41%); 90: 85 (59%); 148: 114 (80%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 100.0% | 1.973, 2.4486, 3.0569, 3.9199 | 1.973: 114 (80%); 2.4486: 86 (60%); 3.0569: 57 (40%); 3.9199: 29 (20%) | 1.973: 29 (20%); 2.4486: 57 (40%); 3.0569: 86 (60%); 3.9199: 114 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 16, 33, 37 | 9: 115 (80%); 16: 90 (63%); 33: 59 (41%); 37: 31 (22%) | 9: 36 (25%); 16: 62 (43%); 33: 92 (64%); 37: 118 (83%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 0, 1, 3, 4 | 0: 143 (100%); 1: 100 (70%); 3: 58 (41%); 4: 30 (21%) | 0: 43 (30%); 1: 65 (45%); 3: 113 (79%); 4: 143 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0073, 0.0099, 0.017, 0.0281 | -0.0073: 115 (80%); 0.0099: 86 (60%); 0.017: 59 (41%); 0.0281: 30 (21%) | -0.0073: 29 (20%); 0.0099: 57 (40%); 0.017: 86 (60%); 0.0281: 115 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 25.0209, 26.6094, 27.2552, 27.58 | 25.0209: 119 (83%); 26.6094: 89 (62%); 27.2552: 57 (40%); 27.58: 30 (21%) | 25.0209: 30 (21%); 26.6094: 59 (41%); 27.2552: 86 (60%); 27.58: 115 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.4058, 0.421, 1.1618, 3.042 | -0.4058: 114 (80%); 0.421: 86 (60%); 1.1618: 57 (40%); 3.042: 29 (20%) | -0.4058: 29 (20%); 0.421: 57 (40%); 1.1618: 86 (60%); 3.042: 114 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -3.042, -1.1618, -0.421, 0.4058 | -3.042: 114 (80%); -1.1618: 86 (60%); -0.421: 57 (40%); 0.4058: 29 (20%) | -3.042: 29 (20%); -1.1618: 57 (40%); -0.421: 86 (60%); 0.4058: 114 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0368, 0.007, 0.0293, 0.0585 | -0.0368: 114 (80%); 0.007: 86 (60%); 0.0293: 57 (40%); 0.0585: 29 (20%) | -0.0368: 29 (20%); 0.007: 57 (40%); 0.0293: 86 (60%); 0.0585: 114 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9956, 8.5464, 8.7726, 9.0242 | 7.9956: 114 (80%); 8.5464: 86 (60%); 8.7726: 57 (40%); 9.0242: 29 (20%) | 7.9956: 29 (20%); 8.5464: 57 (40%); 8.7726: 86 (60%); 9.0242: 114 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 143 (100%); 1: 40 (28%) | 0: 103 (72%); 1: 132 (92%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0 | 0: 128 (90%) | 0: 115 (80%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 143 (100%); 1: 31 (22%) | 0: 112 (78%); 1: 137 (96%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 4, 7, 207.4, 286.8 | 4: 116 (81%); 7: 91 (64%); 207.4: 57 (40%); 286.8: 29 (20%) | 4: 38 (27%); 7: 58 (41%); 207.4: 86 (60%); 286.8: 114 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 3, 23.4, 114.2, 162.8 | 3: 116 (81%); 23.4: 86 (60%); 114.2: 57 (40%); 162.8: 29 (20%) | 3: 31 (22%); 23.4: 57 (40%); 114.2: 86 (60%); 162.8: 114 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -3.1009, -1.8564, -1.0983, -0.5365 | -3.1009: 114 (80%); -1.8564: 86 (60%); -1.0983: 57 (40%); -0.5365: 29 (20%) | -3.1009: 29 (20%); -1.8564: 57 (40%); -1.0983: 86 (60%); -0.5365: 114 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -5.5857, -2.9573, -1.5418, -0.8527 | -5.5857: 114 (80%); -2.9573: 86 (60%); -1.5418: 57 (40%); -0.8527: 29 (20%) | -5.5857: 29 (20%); -2.9573: 57 (40%); -1.5418: 86 (60%); -0.8527: 114 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.5836, -1.0708, -0.3123, 0.1308 | -2.5836: 114 (80%); -1.0708: 86 (60%); -0.3123: 57 (40%); 0.1308: 29 (20%) | -2.5836: 29 (20%); -1.0708: 57 (40%); -0.3123: 86 (60%); 0.1308: 114 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -2.0351, -1.2176, -0.6785, -0.3637 | -2.0351: 114 (80%); -1.2176: 86 (60%); -0.6785: 57 (40%); -0.3637: 29 (20%) | -2.0351: 29 (20%); -1.2176: 57 (40%); -0.6785: 86 (60%); -0.3637: 114 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -7.8534, -4.4782, -2.5214, -1.4295 | -7.8534: 114 (80%); -4.4782: 86 (60%); -2.5214: 57 (40%); -1.4295: 29 (20%) | -7.8534: 29 (20%); -4.4782: 57 (40%); -2.5214: 86 (60%); -1.4295: 114 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -6.0842, -3.0009, -1.663, -0.8608 | -6.0842: 114 (80%); -3.0009: 86 (60%); -1.663: 57 (40%); -0.8608: 29 (20%) | -6.0842: 29 (20%); -3.0009: 57 (40%); -1.663: 86 (60%); -0.8608: 114 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 23.43, 29.872, 33.858, 41.19 | 23.43: 114 (80%); 29.872: 86 (60%); 33.858: 57 (40%); 41.19: 29 (20%) | 23.43: 29 (20%); 29.872: 57 (40%); 33.858: 86 (60%); 41.19: 114 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.3% | 0.0106, 0.0224, 0.0427, 0.0653 | 0.0106: 113 (79%); 0.0224: 85 (59%); 0.0427: 57 (40%); 0.0653: 29 (20%) | 0.0106: 29 (20%); 0.0224: 57 (40%); 0.0427: 85 (59%); 0.0653: 113 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 1, 5, 12 | 1: 115 (80%); 5: 58 (41%); 12: 30 (21%) | 1: 62 (43%); 5: 90 (63%); 12: 115 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1758 | 0: 143 (100%); 0.1758: 29 (20%) | 0: 88 (62%); 0.1758: 114 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2327, 0.4478, 0.6667 | 0: 143 (100%); 0.2327: 86 (60%); 0.4478: 57 (40%); 0.6667: 30 (21%) | 0: 51 (36%); 0.2327: 57 (40%); 0.4478: 86 (60%); 0.6667: 115 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 143 (100%); 1: 104 (73%); 3: 64 (45%); 8: 38 (27%) | 0: 39 (27%); 1: 69 (48%); 3: 87 (61%); 8: 115 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1, 5, 12 | 1: 115 (80%); 5: 58 (41%); 12: 30 (21%) | 1: 62 (43%); 5: 90 (63%); 12: 115 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3.2, 9 | 0: 143 (100%); 1: 89 (62%); 3.2: 57 (40%); 9: 34 (24%) | 0: 54 (38%); 1: 69 (48%); 3.2: 86 (60%); 9: 115 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0933, 0.2799, 0.4422, 0.6326 | 0.0933: 114 (80%); 0.2799: 86 (60%); 0.4422: 57 (40%); 0.6326: 29 (20%) | 0.0933: 29 (20%); 0.2799: 57 (40%); 0.4422: 86 (60%); 0.6326: 114 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1871, 0.7409 | 0: 125 (87%); 0.1871: 57 (40%); 0.7409: 29 (20%) | 0: 76 (53%); 0.1871: 86 (60%); 0.7409: 114 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2986, 0.5582 | 0: 131 (92%); 0.2986: 57 (40%); 0.5582: 29 (20%) | 0: 60 (42%); 0.2986: 86 (60%); 0.5582: 114 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2986, 0.5582 | 0: 131 (92%); 0.2986: 57 (40%); 0.5582: 29 (20%) | 0: 60 (42%); 0.2986: 86 (60%); 0.5582: 114 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.2247, 0, 0.0505 | -0.2247: 114 (80%); 0: 101 (71%); 0.0505: 29 (20%) | -0.2247: 29 (20%); 0: 109 (76%); 0.0505: 114 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.5593, 0, 0.1893, 1.0961 | -0.5593: 114 (80%); 0: 88 (62%); 0.1893: 58 (41%); 1.0961: 29 (20%) | -0.5593: 29 (20%); 0: 80 (56%); 0.1893: 87 (61%); 1.0961: 114 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 6, 10 | 2: 120 (84%); 4: 90 (63%); 6: 64 (45%); 10: 30 (21%) | 2: 36 (25%); 4: 66 (46%); 6: 92 (64%); 10: 119 (83%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1389, -0.1085, -0.0912, -0.0691 | -0.1389: 114 (80%); -0.1085: 86 (60%); -0.0912: 57 (40%); -0.0691: 29 (20%) | -0.1389: 29 (20%); -0.1085: 57 (40%); -0.0912: 86 (60%); -0.0691: 114 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1482, -0.1312, -0.1107, -0.0827 | -0.1482: 114 (80%); -0.1312: 86 (60%); -0.1107: 57 (40%); -0.0827: 29 (20%) | -0.1482: 29 (20%); -0.1312: 57 (40%); -0.1107: 86 (60%); -0.0827: 114 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1105, -0.0774, -0.0574, -0.0327 | -0.1105: 114 (80%); -0.0774: 86 (60%); -0.0574: 57 (40%); -0.0327: 29 (20%) | -0.1105: 29 (20%); -0.0774: 57 (40%); -0.0574: 86 (60%); -0.0327: 114 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/technical.py (f-string template) | 100.0% | -8.952, -7.2872, -6.296, -5.0318 | -8.952: 114 (80%); -7.2872: 86 (60%); -6.296: 57 (40%); -5.0318: 29 (20%) | -8.952: 29 (20%); -7.2872: 57 (40%); -6.296: 86 (60%); -5.0318: 114 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | 6.2946, 16.5938, 30.148, 42.6508 | 6.2946: 114 (80%); 16.5938: 86 (60%); 30.148: 57 (40%); 42.6508: 29 (20%) | 6.2946: 29 (20%); 16.5938: 57 (40%); 30.148: 86 (60%); 42.6508: 114 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.059, 0.0861, 0.1126, 0.1499 | 0.059: 115 (80%); 0.0861: 86 (60%); 0.1126: 58 (41%); 0.1499: 30 (21%) | 0.059: 29 (20%); 0.0861: 57 (40%); 0.1126: 86 (60%); 0.1499: 115 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.4908, 0.6834, 0.7948, 0.8852 | 0.4908: 114 (80%); 0.6834: 86 (60%); 0.7948: 57 (40%); 0.8852: 29 (20%) | 0.4908: 29 (20%); 0.6834: 57 (40%); 0.7948: 86 (60%); 0.8852: 114 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.8636, -2.1968, -1.8201, -1.316 | -2.8636: 114 (80%); -2.1968: 86 (60%); -1.8201: 57 (40%); -1.316: 29 (20%) | -2.8636: 29 (20%); -2.1968: 57 (40%); -1.8201: 86 (60%); -1.316: 114 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -1.8336, -1.3958, -1.1179, -0.7994 | -1.8336: 114 (80%); -1.3958: 86 (60%); -1.1179: 57 (40%); -0.7994: 29 (20%) | -1.8336: 29 (20%); -1.3958: 57 (40%); -1.1179: 86 (60%); -0.7994: 114 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -1.8061, -0.9396, -0.5591, 0.1564 | -1.8061: 114 (80%); -0.9396: 86 (60%); -0.5591: 57 (40%); 0.1564: 29 (20%) | -1.8061: 29 (20%); -0.9396: 57 (40%); -0.5591: 86 (60%); 0.1564: 114 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -14.394, -11.1902, -9.3654, -6.9194 | -14.394: 114 (80%); -11.1902: 86 (60%); -9.3654: 57 (40%); -6.9194: 29 (20%) | -14.394: 29 (20%); -11.1902: 57 (40%); -9.3654: 86 (60%); -6.9194: 114 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 4.564, 10.96, 27.332, 42.032 | 4.564: 114 (80%); 10.96: 86 (60%); 27.332: 57 (40%); 42.032: 29 (20%) | 4.564: 29 (20%); 10.96: 57 (40%); 27.332: 86 (60%); 42.032: 114 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 36.446, 37.898, 39.044, 39.68 | 36.446: 114 (80%); 37.898: 86 (60%); 39.044: 57 (40%); 39.68: 30 (21%) | 36.446: 29 (20%); 37.898: 57 (40%); 39.044: 86 (60%); 39.68: 115 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 23.356, 26.01, 27.476, 28.868 | 23.356: 114 (80%); 26.01: 86 (60%); 27.476: 57 (40%); 28.868: 29 (20%) | 23.356: 29 (20%); 26.01: 57 (40%); 27.476: 86 (60%); 28.868: 114 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0385, 0.0533, 0.0758, 0.0926 | 0.0385: 114 (80%); 0.0533: 86 (60%); 0.0758: 58 (41%); 0.0926: 29 (20%) | 0.0385: 29 (20%); 0.0533: 57 (40%); 0.0758: 87 (61%); 0.0926: 114 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0705, -0.0552, -0.0425, -0.0311 | -0.0705: 114 (80%); -0.0552: 86 (60%); -0.0425: 57 (40%); -0.0311: 29 (20%) | -0.0705: 29 (20%); -0.0552: 57 (40%); -0.0425: 86 (60%); -0.0311: 114 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1, 2.6 | 0: 143 (100%); 1: 60 (42%); 2.6: 29 (20%) | 0: 83 (58%); 1: 103 (72%); 2.6: 114 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 39, 52, 61, 71.6 | 39: 116 (81%); 52: 87 (61%); 61: 60 (42%); 71.6: 29 (20%) | 39: 33 (23%); 52: 58 (41%); 61: 91 (64%); 71.6: 114 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 99.3% | 0.0153, 0.021, 0.0274, 0.0401 | 0.0153: 113 (79%); 0.021: 85 (59%); 0.0274: 57 (40%); 0.0401: 29 (20%) | 0.0153: 29 (20%); 0.021: 57 (40%); 0.0274: 85 (59%); 0.0401: 113 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.0925, 0.1303, 0.1669, 0.251 | 0.0925: 114 (80%); 0.1303: 86 (60%); 0.1669: 57 (40%); 0.251: 29 (20%) | 0.0925: 29 (20%); 0.1303: 58 (41%); 0.1669: 86 (60%); 0.251: 114 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 42.04, 53.56, 76.48, 127.56 | 42.04: 114 (80%); 53.56: 86 (60%); 76.48: 57 (40%); 127.56: 29 (20%) | 42.04: 29 (20%); 53.56: 57 (40%); 76.48: 86 (60%); 127.56: 114 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -16.1748, -10.504, -5.884, -3.4255 | -16.1748: 114 (80%); -10.504: 86 (60%); -5.884: 57 (40%); -3.4255: 29 (20%) | -16.1748: 29 (20%); -10.504: 57 (40%); -5.884: 86 (60%); -3.4255: 114 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 6.642, 9.564, 13.196, 19.46 | 6.642: 114 (80%); 9.564: 86 (60%); 13.196: 57 (40%); 19.46: 29 (20%) | 6.642: 29 (20%); 9.564: 57 (40%); 13.196: 86 (60%); 19.46: 114 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 6.5, 8.784, 12.75, 17.588 | 6.5: 114 (80%); 8.784: 86 (60%); 12.75: 57 (40%); 17.588: 29 (20%) | 6.5: 29 (20%); 8.784: 57 (40%); 12.75: 86 (60%); 17.588: 114 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 1.358, 4.694, 13.74, 22.456 | 1.358: 114 (80%); 4.694: 86 (60%); 13.74: 57 (40%); 22.456: 29 (20%) | 1.358: 29 (20%); 4.694: 57 (40%); 13.74: 86 (60%); 22.456: 114 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 2.386, 10.188, 25.304 | 0: 143 (100%); 2.386: 86 (60%); 10.188: 57 (40%); 25.304: 29 (20%) | 0: 49 (34%); 2.386: 57 (40%); 10.188: 86 (60%); 25.304: 114 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 14, 17 | 5: 119 (83%); 8: 92 (64%); 14: 61 (43%); 17: 30 (21%) | 5: 36 (25%); 8: 61 (43%); 14: 93 (65%); 17: 115 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 17 | 5: 116 (81%); 10: 87 (61%); 14: 64 (45%); 17: 41 (29%) | 5: 31 (22%); 10: 62 (43%); 14: 93 (65%); 17: 118 (83%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 33.486, 35.956, 39.444, 44.806 | 33.486: 114 (80%); 35.956: 86 (60%); 39.444: 57 (40%); 44.806: 29 (20%) | 33.486: 29 (20%); 35.956: 57 (40%); 39.444: 86 (60%); 44.806: 114 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.4357, 0.7381, 0.8571, 0.9349 | 0.4357: 114 (80%); 0.7381: 86 (60%); 0.8571: 61 (43%); 0.9349: 29 (20%) | 0.4357: 29 (20%); 0.7381: 57 (40%); 0.8571: 87 (61%); 0.9349: 114 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.442, 18.36, 20.964, 25.5 | 16.442: 114 (80%); 18.36: 87 (61%); 20.964: 57 (40%); 25.5: 33 (23%) | 16.442: 29 (20%); 18.36: 60 (42%); 20.964: 86 (60%); 25.5: 116 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 16.442, 18.36, 20.964, 25.5 | 16.442: 114 (80%); 18.36: 87 (61%); 20.964: 57 (40%); 25.5: 33 (23%) | 16.442: 29 (20%); 18.36: 60 (42%); 20.964: 86 (60%); 25.5: 116 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8992, 0.9362, 0.9573, 0.9982 | 0.8992: 115 (80%); 0.9362: 86 (60%); 0.9573: 60 (42%); 0.9982: 29 (20%) | 0.8992: 34 (24%); 0.9362: 58 (41%); 0.9573: 87 (61%); 0.9982: 114 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.834, 1.028, 1.232, 1.602 | 0.834: 114 (80%); 1.028: 86 (60%); 1.232: 57 (40%); 1.602: 29 (20%) | 0.834: 29 (20%); 1.028: 57 (40%); 1.232: 86 (60%); 1.602: 114 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0449, 0.076, 0.0977, 0.1208 | 0.0449: 114 (80%); 0.076: 86 (60%); 0.0977: 57 (40%); 0.1208: 29 (20%) | 0.0449: 29 (20%); 0.076: 57 (40%); 0.0977: 86 (60%); 0.1208: 114 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 33.6595, 61.398, 94.9217, 155.9175 | 33.6595: 114 (80%); 61.398: 86 (60%); 94.9217: 57 (40%); 155.9175: 29 (20%) | 33.6595: 29 (20%); 61.398: 57 (40%); 94.9217: 86 (60%); 155.9175: 114 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0, 0.3296 | 0: 143 (100%); 0.3296: 29 (20%) | 0: 111 (78%); 0.3296: 114 (80%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 143 (100%) | 0: 133 (93%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1465, -0.1215, -0.0992, -0.0748 | -0.1465: 114 (80%); -0.1215: 86 (60%); -0.0992: 57 (40%); -0.0748: 29 (20%) | -0.1465: 29 (20%); -0.1215: 57 (40%); -0.0992: 86 (60%); -0.0748: 114 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -90.598, -87.206, -83.356, -78.874 | -90.598: 114 (80%); -87.206: 86 (60%); -83.356: 57 (40%); -78.874: 29 (20%) | -90.598: 29 (20%); -87.206: 57 (40%); -83.356: 86 (60%); -78.874: 114 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.3% | 0.6038, 0.8495, 1.112, 1.3223 | 0.6038: 113 (79%); 0.8495: 85 (59%); 1.112: 57 (40%); 1.3223: 29 (20%) | 0.6038: 29 (20%); 0.8495: 57 (40%); 1.112: 85 (59%); 1.3223: 113 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.3% | 4, 6, 8, 9 | 4: 116 (81%); 6: 87 (61%); 8: 60 (42%); 9: 40 (28%) | 4: 42 (29%); 6: 67 (47%); 8: 102 (71%); 9: 120 (84%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.3% | 0.2194, 0.2561, 0.3003, 0.388 | 0.2194: 114 (80%); 0.2561: 85 (59%); 0.3003: 57 (40%); 0.388: 29 (20%) | 0.2194: 29 (20%); 0.2561: 57 (40%); 0.3003: 85 (59%); 0.388: 113 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.3% | 4, 6, 8, 9 | 4: 122 (85%); 6: 96 (67%); 8: 62 (43%); 9: 47 (33%) | 4: 30 (21%); 6: 64 (45%); 8: 95 (66%); 9: 117 (82%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.3% | 0.0196, 0.023, 0.0294, 0.039 | 0.0196: 114 (80%); 0.023: 85 (59%); 0.0294: 57 (40%); 0.039: 30 (21%) | 0.0196: 30 (21%); 0.023: 57 (40%); 0.0294: 85 (59%); 0.039: 114 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.3% | 2, 4, 6, 7.8 | 2: 128 (90%); 4: 93 (65%); 6: 59 (41%); 7.8: 29 (20%) | 2: 37 (26%); 4: 68 (48%); 6: 102 (71%); 7.8: 113 (79%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.3% | 0.2406, 0.371, 0.5046, 0.7063 | 0.2406: 113 (79%); 0.371: 85 (59%); 0.5046: 57 (40%); 0.7063: 29 (20%) | 0.2406: 29 (20%); 0.371: 57 (40%); 0.5046: 85 (59%); 0.7063: 113 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.3% | 8, 9, 10 | 8: 119 (83%); 9: 102 (71%); 10: 68 (48%) | 8: 40 (28%); 9: 74 (52%); 10: 142 (99%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.7% |
| above_avwap_20low | 79.0% |
| above_avwap_252low | 95.7% |
| above_avwap_50low | 59.4% |
| above_cam_r3 | 25.9% |
| above_cam_r4 | 11.2% |
| above_cpr | 35.7% |
| above_pivot | 40.6% |
| above_prev_high | 7.7% |
| above_prev_low | 69.2% |
| above_r1 | 10.5% |
| above_r2 | 2.1% |
| above_vwap | 89.5% |
| above_wood_p | 25.9% |
| ad_rising | 36.4% |
| adx_cross_up | 11.2% |
| adx_cross_up_20 | 7.0% |
| adx_strong | 3.5% |
| adx_trending | 68.5% |
| ao_cross_dn | 3.5% |
| ao_positive | 1.4% |
| ao_twin_peaks_bull | 3.5% |
| at_key_fib | 1.4% |
| at_key_fib_wide | 7.7% |
| avwap_20high_loss_recent_3d | 6.3% |
| avwap_20low_loss_recent_3d | 12.5% |
| avwap_20low_reclaim_recent_3d | 44.6% |
| avwap_252low_loss_recent_3d | 2.9% |
| avwap_252low_reclaim_recent_3d | 4.3% |
| avwap_50low_loss_recent_3d | 16.9% |
| avwap_50low_reclaim_recent_3d | 22.9% |
| bb_10_20_above_mid | 1.4% |
| bb_10_20_expanding | 69.9% |
| bb_10_20_pctb_lt_05 | 16.8% |
| bb_10_20_pctb_lt_1 | 30.1% |
| bb_10_20_pctb_lt_15 | 48.3% |
| bb_10_20_pctb_lt_2 | 65.7% |
| bb_10_20_pctb_lt_25 | 80.4% |
| bb_10_20_reclaim_from_lower_recent_3d | 45.5% |
| bb_10_20_squeeze | 9.1% |
| bb_10_20_touch_lower | 15.4% |
| bb_20_15_expanding | 90.2% |
| bb_20_15_pctb_lt_05 | 85.3% |
| bb_20_15_pctb_lt_1 | 91.6% |
| bb_20_15_pctb_lt_15 | 97.2% |
| bb_20_15_pctb_lt_2 | 98.6% |
| bb_20_15_reclaim_from_lower_recent_3d | 16.8% |
| bb_20_15_squeeze | 9.1% |
| bb_20_15_touch_lower | 84.6% |
| bb_20_20_expanding | 90.2% |
| bb_20_20_pctb_lt_05 | 60.1% |
| bb_20_20_pctb_lt_1 | 71.3% |
| bb_20_20_pctb_lt_15 | 83.9% |
| bb_20_20_pctb_lt_2 | 91.6% |
| bb_20_20_pctb_lt_25 | 97.9% |
| bb_20_20_reclaim_from_lower_recent_3d | 36.4% |
| bb_20_20_squeeze | 2.8% |
| bb_20_20_touch_lower | 49.0% |
| bearish_pin_bar | 2.8% |
| below_avwap_20low | 21.0% |
| below_avwap_252low | 4.3% |
| below_avwap_50low | 40.6% |
| below_cam_s3 | 25.9% |
| below_cam_s4 | 16.8% |
| below_cpr | 59.4% |
| below_ema_20_break_recent_5d | 16.1% |
| below_ema_21_break_recent_5d | 16.8% |
| below_ema_50_break_recent_5d | 42.0% |
| below_ema_9_break_recent_5d | 19.6% |
| below_prev_high | 92.3% |
| below_prev_low | 29.4% |
| below_prev_low_clearance_atr_05 | 14.0% |
| below_s1 | 21.7% |
| below_s2 | 12.6% |
| below_sma_9 | 98.6% |
| below_vwap | 10.5% |
| bullish_engulfing | 3.5% |
| bullish_pin_bar | 9.8% |
| capitulation_recent_3d | 1.4% |
| chandelier_long_flip_dn | 5.6% |
| close_in_bottom_40pct_of_range | 7.0% |
| close_in_top_40pct_of_range | 73.4% |
| cmf_cross_dn | 1.4% |
| cmf_cross_up | 9.8% |
| cmf_negative | 72.7% |
| cmf_positive | 27.3% |
| concentrated_sell | 11.3% |
| cpr_narrow | 85.3% |
| cpr_narrow_tight | 21.0% |
| cup_handle_detected | 0.7% |
| dc10_breakout_dn | 28.7% |
| dc10_breakout_dn_1pct | 45.5% |
| dc10_strong_breakout_dn | 13.3% |
| dc20_breakout_dn | 28.7% |
| dc20_support_break_retest_strong | 60.1% |
| defensive_leadership | 69.2% |
| director_only_buy | 2.8% |
| doji | 7.0% |
| double_bottom_detected | 11.2% |
| double_top_detected | 16.8% |
| dpi_elevated | 46.0% |
| drying_volume_on_up_turn | 37.8% |
| ema_20_50_bearish | 44.8% |
| ema_20_50_bullish | 55.2% |
| ema_20_50_death_cross | 5.6% |
| ema_9_21_bearish | 99.3% |
| ema_9_21_bullish | 0.7% |
| ema_9_21_death_cross | 2.1% |
| flag_bear_break_retest_short | 1.4% |
| flag_bear_broke | 2.1% |
| force_index_cross_dn | 2.8% |
| force_index_positive | 1.4% |
| gap_dn_1_5pct | 35.7% |
| gap_dn_2pct | 28.0% |
| gap_up_1_5pct | 2.8% |
| gap_up_2pct | 0.7% |
| hammer | 7.7% |
| head_shoulders_bottom_detected | 0.7% |
| head_shoulders_top_detected | 8.4% |
| house_cluster_buy | 2.8% |
| house_cluster_sell | 0.7% |
| htf_disagreement | 16.8% |
| hull_bearish | 99.3% |
| hull_bullish | 0.7% |
| hull_flip_dn | 3.5% |
| ichi_above_cloud | 0.7% |
| ichi_below_cloud | 78.3% |
| ichi_below_cloud_break_recent_5d | 51.7% |
| ichi_cloud_thick | 94.4% |
| ichi_tk_bearish | 88.8% |
| ichi_tk_cross_dn | 4.2% |
| ichi_weekly_above_cloud | 87.7% |
| ichi_weekly_below_cloud | 0.7% |
| ichi_weekly_in_cloud | 11.6% |
| inside_bar | 20.3% |
| inside_cpr | 6.3% |
| inside_kc | 24.5% |
| institutional_persistence_growing | 49.3% |
| institutional_persistence_strong | 63.0% |
| institutional_strong_buy | 93.7% |
| inverted_cup_handle_detected | 1.4% |
| is_friday | 21.0% |
| is_halloween_period | 58.7% |
| is_halloween_period_first_day | 0.7% |
| is_january | 6.3% |
| is_january_extended | 8.4% |
| is_monday | 30.1% |
| is_pre_holiday | 2.1% |
| is_summer_period | 41.3% |
| is_totm_window | 31.5% |
| is_totm_window_first_day | 9.8% |
| is_week_open | 30.8% |
| kc_touch_lower | 88.8% |
| macd_12_26_9_crossover_dn | 1.4% |
| macd_8_21_5_bearish | 97.9% |
| macd_8_21_5_bullish | 2.1% |
| macd_8_21_5_crossover_dn | 4.2% |
| macd_8_21_5_crossover_up | 0.7% |
| mfi_broad_overbought | 1.4% |
| mfi_broad_oversold | 41.3% |
| mfi_oversold | 12.6% |
| monthly_above_sma_12 | 98.6% |
| monthly_above_sma_6 | 26.1% |
| monthly_bias_bull | 24.6% |
| monthly_momentum_pos | 91.3% |
| morning_star | 2.8% |
| near_52w_high_retest_long | 4.2% |
| near_avwap_20high_atr_10x | 3.5% |
| near_avwap_20high_atr_15x | 12.6% |
| near_avwap_20high_atr_20x | 43.4% |
| near_avwap_20low_atr_05x | 85.7% |
| near_avwap_252low_atr_05x | 9.3% |
| near_avwap_252low_atr_10x | 16.4% |
| near_avwap_252low_atr_15x | 26.4% |
| near_avwap_252low_atr_20x | 42.9% |
| near_avwap_50low_atr_05x | 41.0% |
| near_avwap_50low_atr_10x | 51.8% |
| near_avwap_50low_atr_15x | 54.2% |
| near_avwap_50low_atr_20x | 68.7% |
| near_cam_r3 | 17.5% |
| near_cam_s3 | 9.1% |
| near_cam_s4 | 1.4% |
| near_fib_500 | 0.7% |
| near_fib_618 | 0.7% |
| near_fib_786 | 10.5% |
| near_pivot | 14.7% |
| near_prev_close | 18.2% |
| near_prev_high | 4.9% |
| near_prev_low | 8.4% |
| near_r1 | 7.7% |
| near_r1_wide | 37.8% |
| near_r2 | 2.8% |
| near_r2_wide | 12.6% |
| near_s1 | 4.9% |
| near_s1_wide | 37.8% |
| near_s2 | 4.2% |
| near_s2_wide | 16.8% |
| near_wood_r1 | 1.4% |
| near_wood_s1 | 10.5% |
| news_uses_polygon_score | 33.6% |
| obv_bearish | 97.2% |
| obv_bullish | 2.8% |
| obv_diverge_bull | 9.1% |
| obv_falling | 87.4% |
| obv_rising | 12.6% |
| outside_bar | 3.5% |
| pead_negative_surprise | 8.0% |
| pead_positive_surprise | 32.0% |
| pin_bar | 12.6% |
| po3_accumulation_active | 12.6% |
| po3_bullish | 35.0% |
| po3_manipulation_sweep_down | 7.0% |
| po3_manipulation_sweep_up | 0.7% |
| po3_mmbm_setup | 2.1% |
| po3_sweep_above_prior_high | 17.5% |
| po3_sweep_below_prior_low | 67.8% |
| ppo_crossover_dn | 1.4% |
| pre_fomc_d1 | 0.7% |
| pre_fomc_window | 0.7% |
| price_above_dema | 2.1% |
| price_above_ema_200_break_recent_5d | 14.7% |
| price_above_hull | 19.6% |
| price_above_tema | 18.2% |
| price_below_dema | 97.9% |
| price_below_hull | 80.4% |
| price_below_tema | 81.8% |
| psar_flip_dn | 2.8% |
| r1_break_retest_long | 2.1% |
| risk_off_regime_bond_signal | 32.9% |
| risk_off_regime_bond_signal_strong | 22.4% |
| risk_off_regime_gold_signal | 46.2% |
| risk_on_regime_bond_signal | 34.3% |
| risk_on_regime_bond_signal_strong | 8.4% |
| roc_turning_dn | 1.4% |
| rsi_14_cross_dn_overbought_recent_3d | 0.7% |
| rsi_14_cross_up_oversold_recent_3d | 28.0% |
| rsi_14_oversold | 15.4% |
| rsi_14_rising | 53.1% |
| rsi_21_cross_up_oversold_recent_3d | 3.5% |
| rsi_21_rising | 53.1% |
| rsi_2_bullish | 11.9% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 9.8% |
| rsi_2_cross_dn_overbought_recent_3d | 13.3% |
| rsi_2_cross_up_extreme_os_recent_3d | 45.5% |
| rsi_2_cross_up_oversold_recent_3d | 34.3% |
| rsi_2_extreme_ob | 1.4% |
| rsi_2_extreme_os | 51.7% |
| rsi_2_overbought | 2.8% |
| rsi_2_oversold | 65.0% |
| rsi_2_rising | 53.1% |
| rsi_9_cross_dn_overbought_recent_3d | 1.4% |
| rsi_9_cross_up_extreme_os_recent_3d | 23.1% |
| rsi_9_cross_up_oversold_recent_3d | 11.9% |
| rsi_9_extreme_os | 2.8% |
| rsi_9_oversold | 86.7% |
| rsi_9_rising | 53.1% |
| s1_break_retest_short | 95.1% |
| sc_13d_filed_within_30d | 3.9% |
| sc_13g_filed_within_30d | 0.7% |
| sector_outperforming_spy | 25.0% |
| sector_underperforming_spy | 75.0% |
| shooting_star | 4.2% |
| sma_20_50_bullish | 50.3% |
| sma_9_21_bullish | 4.2% |
| smc_bos_bearish | 1.4% |
| smc_bos_bullish | 12.6% |
| smc_bos_retest_long | 4.9% |
| smc_bos_retest_short | 1.4% |
| smc_breaker_block_bearish | 7.7% |
| smc_breaker_block_bullish | 42.0% |
| smc_choch_bearish | 4.2% |
| smc_choch_bullish | 0.7% |
| smc_equal_highs_swept | 4.2% |
| smc_fvg_bearish_active | 88.1% |
| smc_fvg_bullish_active | 5.6% |
| smc_fvg_retest_long_zone | 5.6% |
| smc_fvg_retest_short_zone | 29.4% |
| smc_in_premium_zone | 3.5% |
| smc_inverse_fvg_bullish | 50.3% |
| smc_liquidity_swept_dn | 0.7% |
| smc_liquidity_swept_up | 0.7% |
| smc_mitigation_block_long | 4.2% |
| smc_ob_bearish_active | 13.3% |
| smc_ob_bullish_active | 39.2% |
| smc_ote_long_zone | 11.2% |
| smc_ote_short_zone | 5.6% |
| squeeze_fire_dn | 0.7% |
| squeeze_in | 4.2% |
| stoch_bearish_cross | 8.4% |
| stoch_broad_oversold | 90.2% |
| stoch_bullish_cross | 29.4% |
| stoch_oversold | 86.7% |
| stochrsi_cross_dn | 7.7% |
| stochrsi_cross_up | 44.1% |
| stochrsi_overbought | 0.7% |
| stochrsi_oversold | 72.0% |
| supertrend_bearish | 16.8% |
| supertrend_bullish | 83.2% |
| supertrend_flip_dn | 4.9% |
| supertrend_flip_recent_long_5d | 4.9% |
| supertrend_flip_recent_short_5d | 17.5% |
| supertrend_flip_up | 2.1% |
| support_break_retest | 85.3% |
| tema_cross_dn | 0.7% |
| three_white_soldiers | 0.7% |
| triangle_ascending_detected | 2.1% |
| triangle_descending_detected | 11.2% |
| uo_oversold | 10.5% |
| usd_strengthening | 32.2% |
| usd_weakening | 9.8% |
| vix_band_high | 67.1% |
| vix_band_low | 16.1% |
| vix_band_mid | 16.8% |
| vix_term_backwardation | 19.6% |
| vix_term_contango | 80.4% |
| vol_above_avg | 62.2% |
| vol_below_avg | 37.8% |
| vol_spike_12x | 43.4% |
| vol_spike_15x | 24.5% |
| vol_spike_17x | 16.8% |
| vol_spike_2x | 14.0% |
| vol_spike_2x_on_down_day_recent_3d | 18.2% |
| vol_spike_2x_on_up_day_recent_3d | 4.2% |
| vol_spike_3x | 7.7% |
| vp_below_value_area | 67.1% |
| vp_close_above_poc | 4.2% |
| vp_close_below_poc | 95.8% |
| vp_in_value_area | 32.9% |
| week_open_gap_down_15pct | 11.9% |
| week_open_gap_up_15pct | 1.4% |
| weekly_above_ema_20 | 7.0% |
| weekly_bias_bear | 93.0% |
| williams_r_oversold | 76.2% |
| williams_r_rising | 83.9% |
| within_pead_window | 44.7% |
| within_post_inclusion_window | 9.5% |
| xs_avoid_high_ivol | 66.9% |
| xs_avoid_high_max | 86.6% |
| xs_high_beta_decile | 28.2% |
| xs_low_beta_bottom_quintile | 28.2% |
| xs_low_beta_decile | 9.9% |
| xs_low_beta_decile_entry_recent_5d | 0.7% |
| xs_low_beta_top_quintile | 9.9% |
| xs_momentum_top_decile | 47.9% |
| xs_momentum_top_quintile | 71.8% |
| xs_quality_bottom_quintile | 13.9% |
| xs_quality_top_quintile | 21.5% |
| xs_quality_top_tercile | 48.1% |
| yoy_surprise_high | 61.5% |
| yoy_surprise_negative | 28.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 96.5% |
| committed_growth_holders | 96.5% |
| corp_donations_1y | 9.8% |
| corp_donations_count_1y | 9.8% |
| corp_donations_unique_pacs | 9.8% |
| cot_rut_commercials_pctile_3y | 72.7% |
| cot_rut_mmoney_pctile_3y | 72.7% |
| days_since_deletion | 10.5% |
| days_since_inclusion | 14.7% |
| days_to_next_holiday | 68.5% |
| days_to_rebalance | 7.7% |
| dpi_30d_avg | 95.8% |
| dpi_recent | 95.8% |
| earnings_announcement_return | 87.4% |
| earnings_eps_yoy_growth | 94.4% |
| gov_contracts_4q_sum | 40.6% |
| gov_contracts_last_qtr_amount | 40.6% |
| gov_contracts_qoq_growth | 40.6% |
| head_shoulders_magnitude_pct | 8.4% |
| insider_total_shares_bought_30d | 4.2% |
| inverted_cup_handle_height_pct | 4.9% |
| lobbying_amount_1y | 74.8% |
| lobbying_amount_q | 74.8% |
| lobbying_amount_yoy | 74.8% |
| monthly_momentum_6m | 96.5% |
| otc_short_ratio_recent | 95.8% |
| otc_volume_recent | 95.8% |
| pair_half_life | 93.0% |
| pair_max_abs_zscore | 93.0% |
| pair_zscore_signed | 93.0% |
| pct_from_avwap_20low | 39.2% |
| pct_from_avwap_252low | 97.9% |
| pct_from_avwap_50low | 58.0% |
| persistent_holders_4q | 96.5% |
| persistent_holders_8q | 96.5% |
| search_volume_index_recent | 74.1% |
| search_volume_observations | 74.1% |
| search_volume_zscore_30d | 74.1% |
| sector_etf_return_20d | 2.8% |
| total_active_holders | 96.5% |
| triangle_breakdown_pct | 11.2% |
| triangle_breakout_pct | 2.1% |
| xs_quality_decile | 55.2% |
| xs_quality_gross_profitability | 55.2% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.998), `avwap_252low` (0.995), `avwap_50low` (0.997), `bb_10_20_lower` (0.996), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.998), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.997), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.998), `cam_s1` (0.997), `cam_s2` (0.997), `cam_s3` (0.997), `cam_s4` (0.997), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (1.0), `cup_handle_depth_pct` (-1.0), `cup_handle_rim` (1.0), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (0.999), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.994), `double_bottom_trough` (0.997), `double_top_neckline` (1.0), `double_top_peak` (0.997), `entry_stop_long` (0.997), `entry_stop_short` (0.999), `fib_236` (0.999), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.998), `fib_ext_127` (0.998), `fib_ext_162` (0.996), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.998), `ichi_senkou_b` (0.996), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_rim_low` (1.0), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.998), `monthly_sma_12` (0.995), `monthly_sma_6` (0.998), `pivot` (0.998), `prev_close` (0.997), `prev_high` (0.998), `prev_low` (0.997), `psar_value` (0.999), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.997), `s2` (0.997), `s3` (0.996), `spy_return_20d` (-1.0), `supertrend_value` (0.99), `swing_high` (0.998), `swing_low` (0.997), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.999), `vp_value_area_low` (0.996), `vwap` (0.963), `vwap_lower_1` (0.956), `vwap_upper_1` (0.968), `vwap_upper_2` (0.971), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.997), `wood_s2` (0.997), `year_high` (0.998), `year_low` (0.976)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 8 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 7 |
| P2 | rsi_14 < 35 | 5 | subset-safe | no - derives offline | 1 | 4 | 0 |
| P2.1 | rsi span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P3 | smart-money union (5 flags) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     8 x 5 x 3 x 1 = 120
offline gradings   4 level-combinations x 24 exits = 96 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  115 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 4 + 115 = 120 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 472 census axes join it only when REGISTERED at the T3 band review.
