# Table A - rsi_oversold_with_smart_money_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build ff10274b7 | commit 352770ae3 at 2026-11-05 00:53:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** smart_money_sleeve | **status:** NOT-STARTED | **R5 fires:** 2753 (closed fires in the exit cube: 2753 of 2753, S6-B3258) | **surviving fires (T1):** 2753 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/technical.py (f-string template) +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)
P2  rsi_14  <- backtest/signals/polars_panel.py (f-string template) +2
       DEFN: Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  _has_smart_money_buy(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_rsi_oversold_with_smart_money_long (docstring and return dropped):

```python
base_fires = s.get('rsi_14', False) and s.get('price_above_ema_200', False)
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
| P1 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/technical.py (f-string template) +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - producer_variant_table.SPECS['bollinger_lower'] P3/P4; backtest/signals/technical.py compute_ema_sma | SPECS bollinger_lower P3/P4 (T3/Q2-APPROVED 2026-09-27): production 200 + resim spans [9, 20, 21, 50, 100, 150, 250] | 200 | 9, 20, 21, 50, 100, 150, 200, 250 | offline 0 of 8 levels - canon-span FLAGS (above/below ema 9/20/21/50/200) ARE persisted - measured 200-of-200 bollinger fires, S6-B3117b; offline as ADD-A-CONDITION legs only. The SWAP of the gate span, and non-canon spans, are RESIM | the whole band except production (resim_band [9, 20, 21, 50, 100, 150, 250]); env STRAT_EMA_SPAN does not reach this gate - it reads the literal key - DEFINED-NO-ACTUATOR here (S6-B3253) | T3 review before any grid |
| P2 | PRODUCER | rsi_14 - emitted by backtest/signals/polars_panel.py (f-string template) +2; the boolean's UNDERLYING condition is bandable through its producer's internals | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | offline 0 of 3 levels - none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY-HELPER | _has_smart_money_buy(s) - a helper gate; its internals are outside the source pattern (lower bound) | see the helper's own source | required | - | - | inspect before any engine leg | BANDS-TO-DEFINE |
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
| adx | backtest/signals/technical.py | 100.0% | 16.854, 20.696, 24.84, 29.86 | 16.854: 2202 (80%); 20.696: 1652 (60%); 24.84: 1102 (40%); 29.86: 552 (20%) | 16.854: 551 (20%); 20.696: 1101 (40%); 24.84: 1654 (60%); 29.86: 2203 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 17.374, 21.39, 25.57, 30.13 | 17.374: 2202 (80%); 21.39: 1654 (60%); 25.57: 1103 (40%); 30.13: 552 (20%) | 17.374: 551 (20%); 21.39: 1102 (40%); 25.57: 1653 (60%); 30.13: 2203 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 17.068, 21.298, 25.342, 30.752 | 17.068: 2202 (80%); 21.298: 1652 (60%); 25.342: 1101 (40%); 30.752: 551 (20%) | 17.068: 551 (20%); 21.298: 1101 (40%); 25.342: 1652 (60%); 30.752: 2202 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -5.4395, -1.3426, 0.7769, 4.0514 | -5.4395: 2202 (80%); -1.3426: 1652 (60%); 0.7769: 1101 (40%); 4.0514: 551 (20%) | -5.4395: 551 (20%); -1.3426: 1101 (40%); 0.7769: 1652 (60%); 4.0514: 2202 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.3141, 2.2431, 3.7359, 6.8781 | 1.3141: 2202 (80%); 2.2431: 1652 (60%); 3.7359: 1101 (40%); 6.8781: 551 (20%) | 1.3141: 551 (20%); 2.2431: 1101 (40%); 3.7359: 1652 (60%); 6.8781: 2202 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.3141, 2.2431, 3.7359, 6.8781 | 1.3141: 2202 (80%); 2.2431: 1652 (60%); 3.7359: 1101 (40%); 6.8781: 551 (20%) | 1.3141: 551 (20%); 2.2431: 1101 (40%); 3.7359: 1652 (60%); 6.8781: 2202 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.088, 2.564, 3.1182, 4.0224 | 2.088: 2203 (80%); 2.564: 1654 (60%); 3.1182: 1101 (40%); 4.0224: 551 (20%) | 2.088: 553 (20%); 2.564: 1102 (40%); 3.1182: 1652 (60%); 4.0224: 2202 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0597, 0.0864, 0.1231, 0.1745 | 0.0597: 2202 (80%); 0.0864: 1652 (60%); 0.1231: 1104 (40%); 0.1745: 552 (20%) | 0.0597: 551 (20%); 0.0864: 1102 (40%); 0.1231: 1652 (60%); 0.1745: 2203 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2615, 0.4494, 0.6903, 0.8737 | 0.2615: 2202 (80%); 0.4494: 1652 (60%); 0.6903: 1102 (40%); 0.8737: 551 (20%) | 0.2615: 551 (20%); 0.4494: 1101 (40%); 0.6903: 1652 (60%); 0.8737: 2202 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0655, 0.0909, 0.1169, 0.1517 | 0.0655: 2205 (80%); 0.0909: 1654 (60%); 0.1169: 1102 (40%); 0.1517: 551 (20%) | 0.0655: 551 (20%); 0.0909: 1103 (40%); 0.1169: 1654 (60%); 0.1517: 2202 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1038, 0.3848, 0.7208, 1.0138 | 0.1038: 2203 (80%); 0.3848: 1652 (60%); 0.7208: 1101 (40%); 1.0138: 551 (20%) | 0.1038: 552 (20%); 0.3848: 1102 (40%); 0.7208: 1652 (60%); 1.0138: 2202 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0874, 0.1212, 0.1558, 0.2023 | 0.0874: 2203 (80%); 0.1212: 1654 (60%); 0.1558: 1102 (40%); 0.2023: 551 (20%) | 0.0874: 553 (20%); 0.1212: 1103 (40%); 0.1558: 1653 (60%); 0.2023: 2202 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2028, 0.4136, 0.6655, 0.8854 | 0.2028: 2203 (80%); 0.4136: 1652 (60%); 0.6655: 1101 (40%); 0.8854: 551 (20%) | 0.2028: 551 (20%); 0.4136: 1102 (40%); 0.6655: 1652 (60%); 0.8854: 2202 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0467, -0.0196, 0.0023, 0.0297 | -0.0467: 2204 (80%); -0.0196: 1679 (61%); 0.0023: 1116 (41%); 0.0297: 554 (20%) | -0.0467: 555 (20%); -0.0196: 1120 (41%); 0.0023: 1656 (60%); 0.0297: 2209 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1428, 0.1627, 0.2009, 0.2594 | 0.1428: 2202 (80%); 0.1627: 1675 (61%); 0.2009: 1098 (40%); 0.2594: 544 (20%) | 0.1428: 551 (20%); 0.1627: 1078 (39%); 0.2009: 1655 (60%); 0.2594: 2209 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 2753 (100%) | 0: 2634 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0843, 0.0019, 0.0713, 0.1523 | -0.0843: 2202 (80%); 0.0019: 1653 (60%); 0.0713: 1102 (40%); 0.1523: 551 (20%) | -0.0843: 551 (20%); 0.0019: 1102 (40%); 0.0713: 1652 (60%); 0.1523: 2202 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 2753 (100%); 1: 1055 (38%) | 0: 1698 (62%); 1: 2327 (85%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2408, -0.2011, -0.1572, -0.1236 | -0.2408: 2203 (80%); -0.2011: 1658 (60%); -0.1572: 1105 (40%); -0.1236: 558 (20%) | -0.2408: 558 (20%); -0.2011: 1102 (40%); -0.1572: 1663 (60%); -0.1236: 2208 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3782, 0.6026, 0.6731, 0.7692 | 0.3782: 2224 (81%); 0.6026: 1683 (61%); 0.6731: 1191 (43%); 0.7692: 600 (22%) | 0.3782: 561 (20%); 0.6026: 1120 (41%); 0.6731: 1681 (61%); 0.7692: 2309 (84%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2692, 0.4295, 0.6026, 0.8397 | 0.2692: 2219 (81%); 0.4295: 1674 (61%); 0.6026: 1113 (40%); 0.8397: 553 (20%) | 0.2692: 573 (21%); 0.4295: 1183 (43%); 0.6026: 1653 (60%); 0.8397: 2218 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0929, -0.0184, 0.0401, 0.1806 | -0.0929: 2207 (80%); -0.0184: 1664 (60%); 0.0401: 1116 (41%); 0.1806: 558 (20%) | -0.0929: 559 (20%); -0.0184: 1108 (40%); 0.0401: 1653 (60%); 0.1806: 2205 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.4487, 0.5564, 0.7436 | 0.2564: 2232 (81%); 0.4487: 1701 (62%); 0.5564: 1101 (40%); 0.7436: 556 (20%) | 0.2564: 572 (21%); 0.4487: 1125 (41%); 0.5564: 1652 (60%); 0.7436: 2210 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3462, 0.4551, 0.6667 | 0.1474: 2230 (81%); 0.3462: 1654 (60%); 0.4551: 1265 (46%); 0.6667: 559 (20%) | 0.1474: 572 (21%); 0.3462: 1149 (42%); 0.4551: 1657 (60%); 0.6667: 2220 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.5046, -0.3448, -0.171, 0.0639 | -0.5046: 2224 (81%); -0.3448: 1659 (60%); -0.171: 1135 (41%); 0.0639: 555 (20%) | -0.5046: 552 (20%); -0.3448: 1102 (40%); -0.171: 1672 (61%); 0.0639: 2212 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3269, 0.5128, 0.7372, 0.9167 | 0.3269: 2224 (81%); 0.5128: 1660 (60%); 0.7372: 1111 (40%); 0.9167: 612 (22%) | 0.3269: 567 (21%); 0.5128: 1107 (40%); 0.7372: 1669 (61%); 0.9167: 2256 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.359, 0.5962, 0.8526 | 0.1474: 2220 (81%); 0.359: 1668 (61%); 0.5962: 1106 (40%); 0.8526: 665 (24%) | 0.1474: 552 (20%); 0.359: 1120 (41%); 0.5962: 1674 (61%); 0.8526: 2216 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0664, -0.0577, -0.0372, 0 | -0.0664: 2202 (80%); -0.0577: 1665 (60%); -0.0372: 1119 (41%); 0: 870 (32%) | -0.0664: 551 (20%); -0.0577: 1105 (40%); -0.0372: 1669 (61%); 0: 2660 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4103, 0.6667, 0.8846, 1 | 0.4103: 2206 (80%); 0.6667: 1687 (61%); 0.8846: 1136 (41%); 1: 679 (25%) | 0.4103: 553 (20%); 0.6667: 1103 (40%); 0.8846: 1676 (61%); 1: 2753 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1538, 0.3077, 0.5769, 0.8974 | 0.1538: 2219 (81%); 0.3077: 1659 (60%); 0.5769: 1107 (40%); 0.8974: 554 (20%) | 0.1538: 557 (20%); 0.3077: 1110 (40%); 0.5769: 1674 (61%); 0.8974: 2206 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0013, 0.0378, 0.1079, 0.2489 | 0.0013: 2225 (81%); 0.0378: 1652 (60%); 0.1079: 1118 (41%); 0.2489: 604 (22%) | 0.0013: 582 (21%); 0.0378: 1116 (41%); 0.1079: 1660 (60%); 0.2489: 2277 (83%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.5211, 0.7949, 0.9467, 0.9744 | 0.5211: 2214 (80%); 0.7949: 1656 (60%); 0.9467: 1101 (40%); 0.9744: 745 (27%) | 0.5211: 553 (20%); 0.7949: 1110 (40%); 0.9467: 1652 (60%); 0.9744: 2248 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0962, 0.2753, 0.5128, 0.7692 | 0.0962: 2217 (81%); 0.2753: 1652 (60%); 0.5128: 1105 (40%); 0.7692: 596 (22%) | 0.0962: 575 (21%); 0.2753: 1101 (40%); 0.5128: 1653 (60%); 0.7692: 2204 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0141, 0.0791, 0.1491 | -0.0812: 2371 (86%); -0.0141: 1658 (60%); 0.0791: 1120 (41%); 0.1491: 558 (20%) | -0.0812: 633 (23%); -0.0141: 1122 (41%); 0.0791: 1665 (60%); 0.1491: 2211 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2669, -0.0345, 0.0281, 0.0941 | -0.2669: 2245 (82%); -0.0345: 1654 (60%); 0.0281: 1103 (40%); 0.0941: 569 (21%) | -0.2669: 562 (20%); -0.0345: 1115 (41%); 0.0281: 1662 (60%); 0.0941: 2212 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.25, 0.5256, 0.7192, 0.8782 | 0.25: 2211 (80%); 0.5256: 1659 (60%); 0.7192: 1101 (40%); 0.8782: 587 (21%) | 0.25: 554 (20%); 0.5256: 1121 (41%); 0.7192: 1652 (60%); 0.8782: 2221 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1603, 0.3897, 0.5833, 0.8269 | 0.1603: 2208 (80%); 0.3897: 1652 (60%); 0.5833: 1117 (41%); 0.8269: 585 (21%) | 0.1603: 558 (20%); 0.3897: 1101 (40%); 0.5833: 1659 (60%); 0.8269: 2244 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0667, 0.1617, 0.316, 0.6961 | 0.0667: 2205 (80%); 0.1617: 1658 (60%); 0.316: 1101 (40%); 0.6961: 551 (20%) | 0.0667: 555 (20%); 0.1617: 1103 (40%); 0.316: 1652 (60%); 0.6961: 2202 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.9% | 23, 61, 84, 140 | 23: 2182 (79%); 61: 1662 (60%); 84: 1107 (40%); 140: 557 (20%) | 23: 555 (20%); 61: 1119 (41%); 84: 1651 (60%); 140: 2181 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 100.0% | 1.725, 2.2995, 2.9399, 4.0669 | 1.725: 2202 (80%); 2.2995: 1653 (60%); 2.9399: 1101 (40%); 4.0669: 551 (20%) | 1.725: 551 (20%); 2.2995: 1102 (40%); 2.9399: 1652 (60%); 4.0669: 2202 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 21, 28, 36 | 9: 2284 (83%); 21: 1673 (61%); 28: 1247 (45%); 36: 596 (22%) | 9: 563 (20%); 21: 1154 (42%); 28: 1704 (62%); 36: 2248 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 0, 1, 2, 3 | 0: 2753 (100%); 1: 2170 (79%); 2: 1625 (59%); 3: 1044 (38%) | 0: 583 (21%); 1: 1128 (41%); 2: 1709 (62%); 3: 2214 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0155, -0.0046, 0.009, 0.0218 | -0.0155: 2204 (80%); -0.0046: 1657 (60%); 0.009: 1103 (40%); 0.0218: 552 (20%) | -0.0155: 554 (20%); -0.0046: 1120 (41%); 0.009: 1652 (60%); 0.0218: 2203 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5699, 25.8225, 26.6094, 27.3557 | 24.5699: 2205 (80%); 25.8225: 1652 (60%); 26.6094: 1105 (40%); 27.3557: 582 (21%) | 24.5699: 555 (20%); 25.8225: 1101 (40%); 26.6094: 1659 (60%); 27.3557: 2265 (82%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.6736, -0.131, 0.2764, 0.8686 | -0.6736: 2202 (80%); -0.131: 1653 (60%); 0.2764: 1101 (40%); 0.8686: 551 (20%) | -0.6736: 551 (20%); -0.131: 1103 (40%); 0.2764: 1652 (60%); 0.8686: 2202 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.8686, -0.2764, 0.131, 0.6736 | -0.8686: 2202 (80%); -0.2764: 1652 (60%); 0.131: 1103 (40%); 0.6736: 551 (20%) | -0.8686: 551 (20%); -0.2764: 1101 (40%); 0.131: 1653 (60%); 0.6736: 2202 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0422, -0.0012, 0.0293, 0.0703 | -0.0422: 2207 (80%); -0.0012: 1654 (60%); 0.0293: 1105 (40%); 0.0703: 552 (20%) | -0.0422: 556 (20%); -0.0012: 1102 (40%); 0.0293: 1655 (60%); 0.0703: 2207 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9922, 8.4883, 8.7492, 9.0634 | 7.9922: 2204 (80%); 8.4883: 1652 (60%); 8.7492: 1100 (40%); 9.0634: 551 (20%) | 7.9922: 549 (20%); 8.4883: 1101 (40%); 8.7492: 1653 (60%); 9.0634: 2202 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.9% | 0, 1 | 0: 2749 (100%); 1: 824 (30%) | 0: 1925 (70%); 1: 2469 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.9% | 0 | 0: 2273 (83%) | 0: 2278 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.9% | 0, 1 | 0: 2749 (100%); 1: 814 (30%) | 0: 1935 (70%); 1: 2461 (89%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 141, 285 | 3: 2375 (86%); 6: 1768 (64%); 141: 1104 (40%); 285: 552 (20%) | 3: 594 (22%); 6: 1129 (41%); 141: 1654 (60%); 285: 2205 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 2, 6, 95, 153 | 2: 2251 (82%); 6: 1667 (61%); 95: 1106 (40%); 153: 558 (20%) | 2: 748 (27%); 6: 1127 (41%); 95: 1661 (60%); 153: 2204 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -1.0073, -0.2995, 0.0528, 0.5859 | -1.0073: 2202 (80%); -0.2995: 1652 (60%); 0.0528: 1101 (40%); 0.5859: 551 (20%) | -1.0073: 551 (20%); -0.2995: 1101 (40%); 0.0528: 1652 (60%); 0.5859: 2203 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.5145, -0.3033, 0.3769, 1.6427 | -1.5145: 2202 (80%); -0.3033: 1652 (60%); 0.3769: 1102 (40%); 1.6427: 551 (20%) | -1.5145: 551 (20%); -0.3033: 1101 (40%); 0.3769: 1652 (60%); 1.6427: 2202 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.2261, -0.1695, 0.4516, 1.6579 | -1.2261: 2202 (80%); -0.1695: 1652 (60%); 0.4516: 1103 (40%); 1.6579: 551 (20%) | -1.2261: 551 (20%); -0.1695: 1101 (40%); 0.4516: 1652 (60%); 1.6579: 2202 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.685, -0.1786, 0.0906, 0.565 | -0.685: 2202 (80%); -0.1786: 1652 (60%); 0.0906: 1101 (40%); 0.565: 551 (20%) | -0.685: 551 (20%); -0.1786: 1102 (40%); 0.0906: 1652 (60%); 0.565: 2202 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.0414, -0.47, 0.4708, 1.7885 | -2.0414: 2202 (80%); -0.47: 1652 (60%); 0.4708: 1101 (40%); 1.7885: 551 (20%) | -2.0414: 551 (20%); -0.47: 1101 (40%); 0.4708: 1652 (60%); 1.7885: 2202 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.8032, -0.4107, 0.3486, 1.6609 | -1.8032: 2202 (80%); -0.4107: 1652 (60%); 0.3486: 1101 (40%); 1.6609: 551 (20%) | -1.8032: 551 (20%); -0.4107: 1101 (40%); 0.3486: 1652 (60%); 1.6609: 2202 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 36.908, 46.46, 55.574, 66.03 | 36.908: 2202 (80%); 46.46: 1653 (60%); 55.574: 1101 (40%); 66.03: 552 (20%) | 36.908: 551 (20%); 46.46: 1102 (40%); 55.574: 1652 (60%); 66.03: 2203 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.3% | 0.0051, 0.0121, 0.0225, 0.0412 | 0.0051: 2188 (79%); 0.0121: 1645 (60%); 0.0225: 1098 (40%); 0.0412: 549 (20%) | 0.0051: 547 (20%); 0.0121: 1090 (40%); 0.0225: 1637 (59%); 0.0412: 2186 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 10 | 0: 2753 (100%); 2: 1691 (61%); 4: 1186 (43%); 10: 552 (20%) | 0: 642 (23%); 2: 1355 (49%); 4: 1714 (62%); 10: 2262 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.148 | 0: 2753 (100%); 0.148: 551 (20%) | 0: 1867 (68%); 0.148: 2202 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.4545, 0.6667 | 0: 2753 (100%); 0.2: 1695 (62%); 0.4545: 1106 (40%); 0.6667: 625 (23%) | 0: 988 (36%); 0.2: 1103 (40%); 0.4545: 1656 (60%); 0.6667: 2232 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 2753 (100%); 1: 1954 (71%); 3: 1179 (43%); 7: 577 (21%) | 0: 799 (29%); 1: 1285 (47%); 3: 1778 (65%); 7: 2258 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 10 | 0: 2753 (100%); 2: 1691 (61%); 4: 1186 (43%); 10: 552 (20%) | 0: 642 (23%); 2: 1355 (49%); 4: 1714 (62%); 10: 2262 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 2753 (100%); 1: 1952 (71%); 3: 1289 (47%); 8: 568 (21%) | 0: 801 (29%); 1: 1204 (44%); 3: 1676 (61%); 8: 2267 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0623, 0.2722, 0.4, 0.6062 | 0.0623: 2202 (80%); 0.2722: 1652 (60%); 0.4: 1133 (41%); 0.6062: 551 (20%) | 0.0623: 551 (20%); 0.2722: 1101 (40%); 0.4: 1656 (60%); 0.6062: 2203 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.231, 0.625 | 0: 2519 (92%); 0.231: 1101 (40%); 0.625: 556 (20%) | 0: 1423 (52%); 0.231: 1652 (60%); 0.625: 2204 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.6025 | 0: 2547 (93%); 0.3333: 1119 (41%); 0.6025: 551 (20%) | 0: 1152 (42%); 0.3333: 1727 (63%); 0.6025: 2202 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.6025 | 0: 2547 (93%); 0.3333: 1119 (41%); 0.6025: 551 (20%) | 0: 1152 (42%); 0.3333: 1727 (63%); 0.6025: 2202 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1751, 0, 0.15 | -0.1751: 2203 (80%); 0: 1947 (71%); 0.15: 552 (20%) | -0.1751: 551 (20%); 0: 1995 (72%); 0.15: 2203 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7322, -0.2924, 0.1496, 1.4343 | -0.7322: 2202 (80%); -0.2924: 1652 (60%); 0.1496: 1101 (40%); 1.4343: 555 (20%) | -0.7322: 551 (20%); -0.2924: 1101 (40%); 0.1496: 1652 (60%); 1.4343: 2216 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 12 | 2: 2334 (85%); 4: 1832 (67%); 7: 1240 (45%); 12: 562 (20%) | 2: 675 (25%); 4: 1126 (41%); 7: 1686 (61%); 12: 2267 (82%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.056, -0.0144, 0.0188, 0.063 | -0.056: 2201 (80%); -0.0144: 1651 (60%); 0.0188: 1101 (40%); 0.063: 551 (20%) | -0.056: 552 (20%); -0.0144: 1102 (40%); 0.0188: 1652 (60%); 0.063: 2202 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0624, -0.0157, 0.0312, 0.0861 | -0.0624: 2202 (80%); -0.0157: 1652 (60%); 0.0312: 1100 (40%); 0.0861: 551 (20%) | -0.0624: 551 (20%); -0.0157: 1101 (40%); 0.0312: 1653 (60%); 0.0861: 2202 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0398, -0.0086, 0.0152, 0.0501 | -0.0398: 2202 (80%); -0.0086: 1652 (60%); 0.0152: 1100 (40%); 0.0501: 551 (20%) | -0.0398: 551 (20%); -0.0086: 1101 (40%); 0.0152: 1653 (60%); 0.0501: 2202 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -2.5174, 6.0314, 15.828, 36.9834 | -2.5174: 2202 (80%); 6.0314: 1652 (60%); 15.828: 1101 (40%); 36.9834: 551 (20%) | -2.5174: 551 (20%); 6.0314: 1101 (40%); 15.828: 1652 (60%); 36.9834: 2202 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0434, 0.0599, 0.0827, 0.1181 | 0.0434: 2209 (80%); 0.0599: 1652 (60%); 0.0827: 1104 (40%); 0.1181: 551 (20%) | 0.0434: 551 (20%); 0.0599: 1105 (40%); 0.0827: 1654 (60%); 0.1181: 2205 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5409, 0.712, 0.8216, 0.9161 | 0.5409: 2202 (80%); 0.712: 1652 (60%); 0.8216: 1103 (40%); 0.9161: 552 (20%) | 0.5409: 551 (20%); 0.712: 1102 (40%); 0.8216: 1652 (60%); 0.9161: 2203 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.3675, -0.3703, 0.4963, 1.6897 | -1.3675: 2202 (80%); -0.3703: 1652 (60%); 0.4963: 1101 (40%); 1.6897: 551 (20%) | -1.3675: 551 (20%); -0.3703: 1101 (40%); 0.4963: 1652 (60%); 1.6897: 2202 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.8793, -0.3934, 0.0519, 0.6464 | -0.8793: 2202 (80%); -0.3934: 1652 (60%); 0.0519: 1101 (40%); 0.6464: 551 (20%) | -0.8793: 551 (20%); -0.3934: 1101 (40%); 0.0519: 1652 (60%); 0.6464: 2202 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -1.1596, -0.2373, 0.6112, 1.6669 | -1.1596: 2202 (80%); -0.2373: 1652 (60%); 0.6112: 1101 (40%); 1.6669: 551 (20%) | -1.1596: 551 (20%); -0.2373: 1101 (40%); 0.6112: 1652 (60%); 1.6669: 2202 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -6.1184, -1.8168, 2.1382, 6.7784 | -6.1184: 2202 (80%); -1.8168: 1652 (60%); 2.1382: 1101 (40%); 6.7784: 551 (20%) | -6.1184: 551 (20%); -1.8168: 1101 (40%); 2.1382: 1652 (60%); 6.7784: 2202 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 42.212, 48.748, 55.69, 62.46 | 42.212: 2202 (80%); 48.748: 1652 (60%); 55.69: 1103 (40%); 62.46: 552 (20%) | 42.212: 551 (20%); 48.748: 1101 (40%); 55.69: 1654 (60%); 62.46: 2203 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 36.064, 60.944, 79.042, 91.826 | 36.064: 2202 (80%); 60.944: 1652 (60%); 79.042: 1101 (40%); 91.826: 551 (20%) | 36.064: 551 (20%); 60.944: 1101 (40%); 79.042: 1652 (60%); 91.826: 2202 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 45.38, 49.296, 54.14, 59.23 | 45.38: 2206 (80%); 49.296: 1652 (60%); 54.14: 1104 (40%); 59.23: 552 (20%) | 45.38: 552 (20%); 49.296: 1101 (40%); 54.14: 1654 (60%); 59.23: 2204 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 39.154, 48.438, 57.49, 66.702 | 39.154: 2202 (80%); 48.438: 1652 (60%); 57.49: 1103 (40%); 66.702: 551 (20%) | 39.154: 551 (20%); 48.438: 1101 (40%); 57.49: 1653 (60%); 66.702: 2202 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 2751 (100%) | 0: 2752 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0299, 0.0452, 0.06, 0.0895 | 0.0299: 2203 (80%); 0.0452: 1657 (60%); 0.06: 1112 (40%); 0.0895: 551 (20%) | 0.0299: 555 (20%); 0.0452: 1102 (40%); 0.06: 1652 (60%); 0.0895: 2202 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0813, -0.0586, -0.0438, -0.0341 | -0.0813: 2210 (80%); -0.0586: 1656 (60%); -0.0438: 1102 (40%); -0.0341: 557 (20%) | -0.0813: 553 (20%); -0.0586: 1102 (40%); -0.0438: 1658 (60%); -0.0341: 2217 (81%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 2753 (100%); 2: 701 (25%) | 0: 1731 (63%); 2: 2210 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 28, 44, 58, 68 | 28: 2242 (81%); 44: 1680 (61%); 58: 1116 (41%); 68: 573 (21%) | 28: 607 (22%); 44: 1104 (40%); 58: 1656 (60%); 68: 2224 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.9% | 0.012, 0.0174, 0.0254, 0.0402 | 0.012: 2177 (79%); 0.0174: 1638 (59%); 0.0254: 1088 (40%); 0.0402: 542 (20%) | 0.012: 546 (20%); 0.0174: 1085 (39%); 0.0254: 1635 (59%); 0.0402: 2181 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.3201, 0.4863, 0.6443, 0.8389 | 0.3201: 2202 (80%); 0.4863: 1652 (60%); 0.6443: 1101 (40%); 0.8389: 551 (20%) | 0.3201: 551 (20%); 0.4863: 1102 (40%); 0.6443: 1652 (60%); 0.8389: 2202 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 39.34, 56.9, 75.42, 110.66 | 39.34: 2202 (80%); 56.9: 1654 (60%); 75.42: 1101 (40%); 110.66: 551 (20%) | 39.34: 551 (20%); 56.9: 1103 (40%); 75.42: 1652 (60%); 110.66: 2202 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -3.808, -0.6455, 1.6851, 5.64 | -3.808: 2202 (80%); -0.6455: 1652 (60%); 1.6851: 1101 (40%); 5.64: 551 (20%) | -3.808: 551 (20%); -0.6455: 1101 (40%); 1.6851: 1652 (60%); 5.64: 2202 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 19.178, 34.296, 59.658, 80.592 | 19.178: 2202 (80%); 34.296: 1652 (60%); 59.658: 1101 (40%); 80.592: 551 (20%) | 19.178: 551 (20%); 34.296: 1101 (40%); 59.658: 1652 (60%); 80.592: 2202 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 19.684, 36.454, 62.088, 83.656 | 19.684: 2202 (80%); 36.454: 1652 (60%); 62.088: 1101 (40%); 83.656: 551 (20%) | 19.684: 551 (20%); 36.454: 1101 (40%); 62.088: 1652 (60%); 83.656: 2202 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 9.448, 26.258, 56.536, 89.252 | 9.448: 2202 (80%); 26.258: 1652 (60%); 56.536: 1101 (40%); 89.252: 551 (20%) | 9.448: 551 (20%); 26.258: 1101 (40%); 56.536: 1652 (60%); 89.252: 2202 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 9.96, 33.222, 65.444, 100 | 9.96: 2203 (80%); 33.222: 1652 (60%); 65.444: 1101 (40%); 100: 577 (21%) | 9.96: 552 (20%); 33.222: 1101 (40%); 65.444: 1652 (60%); 100: 2753 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 12, 17 | 4: 2306 (84%); 7: 1833 (67%); 12: 1163 (42%); 17: 588 (21%) | 4: 576 (21%); 7: 1106 (40%); 12: 1715 (62%); 17: 2275 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 18 | 5: 2262 (82%); 10: 1682 (61%); 14: 1228 (45%); 18: 566 (21%) | 5: 600 (22%); 10: 1190 (43%); 14: 1655 (60%); 18: 2324 (84%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 43.53, 49.42, 54.562, 60.596 | 43.53: 2203 (80%); 49.42: 1654 (60%); 54.562: 1101 (40%); 60.596: 551 (20%) | 43.53: 553 (20%); 49.42: 1103 (40%); 54.562: 1652 (60%); 60.596: 2202 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1429, 0.4246, 0.7024, 0.9048 | 0.1429: 2211 (80%); 0.4246: 1660 (60%); 0.7024: 1110 (40%); 0.9048: 571 (21%) | 0.1429: 575 (21%); 0.4246: 1103 (40%); 0.7024: 1659 (60%); 0.9048: 2208 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.84, 17.48, 20.58, 25.5 | 14.84: 2210 (80%); 17.48: 1660 (60%); 20.58: 1103 (40%); 25.5: 555 (20%) | 14.84: 555 (20%); 17.48: 1113 (40%); 20.58: 1659 (60%); 25.5: 2221 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.84, 17.48, 20.58, 25.5 | 14.84: 2210 (80%); 17.48: 1660 (60%); 20.58: 1103 (40%); 25.5: 555 (20%) | 14.84: 555 (20%); 17.48: 1113 (40%); 20.58: 1659 (60%); 25.5: 2221 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8606, 0.8923, 0.9277, 0.971 | 0.8606: 2204 (80%); 0.8923: 1652 (60%); 0.9277: 1115 (41%); 0.971: 552 (20%) | 0.8606: 561 (20%); 0.8923: 1102 (40%); 0.9277: 1652 (60%); 0.971: 2205 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.71, 0.86, 1.01, 1.31 | 0.71: 2228 (81%); 0.86: 1685 (61%); 1.01: 1107 (40%); 1.31: 559 (20%) | 0.71: 552 (20%); 0.86: 1107 (40%); 1.01: 1677 (61%); 1.31: 2203 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0163, 0.0382, 0.064, 0.1089 | 0.0163: 2203 (80%); 0.0382: 1652 (60%); 0.064: 1103 (40%); 0.1089: 551 (20%) | 0.0163: 551 (20%); 0.0382: 1103 (40%); 0.064: 1652 (60%); 0.1089: 2204 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 43.5241, 73.6289, 111.3644, 195.0572 | 43.5241: 2202 (80%); 73.6289: 1652 (60%); 111.3644: 1101 (40%); 195.0572: 551 (20%) | 43.5241: 551 (20%); 73.6289: 1101 (40%); 111.3644: 1652 (60%); 195.0572: 2202 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 41.3741, 70.4717, 105.2582, 186.2457 | 41.3741: 2202 (80%); 70.4717: 1652 (60%); 105.2582: 1101 (40%); 186.2457: 551 (20%) | 41.3741: 551 (20%); 70.4717: 1101 (40%); 105.2582: 1652 (60%); 186.2457: 2202 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 39.423, 66.875, 99.793, 174.9142 | 39.423: 2202 (80%); 66.875: 1652 (60%); 99.793: 1101 (40%); 174.9142: 551 (20%) | 39.423: 551 (20%); 66.875: 1101 (40%); 99.793: 1652 (60%); 174.9142: 2202 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2753 (100%) | 0: 2367 (86%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2753 (100%) | 0: 2492 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.063, -0.0177, 0.028, 0.0768 | -0.063: 2205 (80%); -0.0177: 1652 (60%); 0.028: 1103 (40%); 0.0768: 552 (20%) | -0.063: 551 (20%); -0.0177: 1101 (40%); 0.028: 1652 (60%); 0.0768: 2203 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -74.816, -55.76, -30.968, -9.714 | -74.816: 2202 (80%); -55.76: 1652 (60%); -30.968: 1101 (40%); -9.714: 551 (20%) | -74.816: 551 (20%); -55.76: 1101 (40%); -30.968: 1652 (60%); -9.714: 2202 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.2% | 0.5455, 0.8425, 1.0745, 1.3733 | 0.5455: 2185 (79%); 0.8425: 1639 (60%); 1.0745: 1093 (40%); 1.3733: 547 (20%) | 0.5455: 547 (20%); 0.8425: 1093 (40%); 1.0745: 1639 (60%); 1.3733: 2185 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 2280 (83%); 5: 1835 (67%); 7: 1312 (48%); 9: 752 (27%) | 3: 674 (24%); 5: 1149 (42%); 7: 1669 (61%); 9: 2308 (84%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.2% | 0.1951, 0.2359, 0.2878, 0.3712 | 0.1951: 2185 (79%); 0.2359: 1639 (60%); 0.2878: 1093 (40%); 0.3712: 547 (20%) | 0.1951: 548 (20%); 0.2359: 1094 (40%); 0.2878: 1639 (60%); 0.3712: 2185 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 2332 (85%); 5: 1878 (68%); 7: 1333 (48%); 9: 803 (29%) | 3: 630 (23%); 5: 1145 (42%); 7: 1648 (60%); 9: 2296 (83%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.2% | 0.0247, 0.034, 0.0451, 0.0669 | 0.0247: 2191 (80%); 0.034: 1640 (60%); 0.0451: 1096 (40%); 0.0669: 547 (20%) | 0.0247: 552 (20%); 0.034: 1097 (40%); 0.0451: 1640 (60%); 0.0669: 2187 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 8, 9 | 3: 2329 (85%); 5: 1881 (68%); 8: 1106 (40%); 9: 800 (29%) | 3: 619 (22%); 5: 1115 (41%); 8: 1932 (70%); 9: 2287 (83%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.3% | -0.0681, 0.057, 0.1835, 0.4237 | -0.0681: 2189 (80%); 0.057: 1641 (60%); 0.1835: 1094 (40%); 0.4237: 548 (20%) | -0.0681: 548 (20%); 0.057: 1094 (40%); 0.1835: 1641 (60%); 0.4237: 2188 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.3% | 4, 6, 8, 10 | 4: 2300 (84%); 6: 1779 (65%); 8: 1244 (45%); 10: 582 (21%) | 4: 693 (25%); 6: 1218 (44%); 8: 1816 (66%); 10: 2735 (99%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.5% |
| 8k_item_5_02_filed_within_7d | 2.9% |
| above_avwap_20high | 43.0% |
| above_avwap_20low | 88.8% |
| above_avwap_252low | 95.4% |
| above_avwap_50low | 77.7% |
| above_cam_r3 | 60.0% |
| above_cam_r4 | 35.5% |
| above_cpr | 73.7% |
| above_pivot | 77.7% |
| above_prev_high | 44.9% |
| above_prev_high_clearance_atr_05 | 17.6% |
| above_prev_low | 92.5% |
| above_r1 | 40.5% |
| above_r2 | 17.9% |
| above_vwap | 75.1% |
| above_wood_p | 69.6% |
| ad_rising | 60.7% |
| adx_cross_up | 2.1% |
| adx_cross_up_20 | 3.0% |
| adx_di_bear | 50.1% |
| adx_di_bull | 49.9% |
| adx_strong | 3.9% |
| adx_trending | 39.0% |
| ao_cross_dn | 2.9% |
| ao_cross_up | 3.1% |
| ao_positive | 47.8% |
| ao_twin_peaks_bull | 5.1% |
| at_key_fib | 18.6% |
| at_key_fib_wide | 44.8% |
| avwap_20high_loss_recent_3d | 11.0% |
| avwap_20high_reclaim_recent_3d | 27.6% |
| avwap_20low_loss_recent_3d | 7.2% |
| avwap_20low_reclaim_recent_3d | 28.2% |
| avwap_252low_loss_recent_3d | 1.3% |
| avwap_252low_reclaim_recent_3d | 16.7% |
| avwap_50low_loss_recent_3d | 9.0% |
| avwap_50low_reclaim_recent_3d | 18.1% |
| bb_10_20_above_mid | 55.6% |
| bb_10_20_expanding | 52.9% |
| bb_10_20_pctb_gt_75 | 35.0% |
| bb_10_20_pctb_gt_8 | 29.5% |
| bb_10_20_pctb_gt_85 | 23.1% |
| bb_10_20_pctb_gt_9 | 17.1% |
| bb_10_20_pctb_gt_95 | 11.2% |
| bb_10_20_pctb_lt_05 | 2.0% |
| bb_10_20_pctb_lt_1 | 4.7% |
| bb_10_20_pctb_lt_15 | 8.2% |
| bb_10_20_pctb_lt_2 | 13.3% |
| bb_10_20_pctb_lt_25 | 18.7% |
| bb_10_20_reclaim_from_lower_recent_3d | 15.4% |
| bb_10_20_reclaim_from_upper_recent_3d | 7.4% |
| bb_10_20_squeeze | 35.4% |
| bb_10_20_touch_lower | 2.1% |
| bb_10_20_touch_upper | 12.0% |
| bb_20_15_above_mid | 53.6% |
| bb_20_15_expanding | 54.1% |
| bb_20_15_pctb_gt_75 | 37.8% |
| bb_20_15_pctb_gt_8 | 33.7% |
| bb_20_15_pctb_gt_85 | 30.6% |
| bb_20_15_pctb_gt_9 | 27.6% |
| bb_20_15_pctb_gt_95 | 24.8% |
| bb_20_15_pctb_lt_05 | 16.3% |
| bb_20_15_pctb_lt_1 | 19.8% |
| bb_20_15_pctb_lt_15 | 23.2% |
| bb_20_15_pctb_lt_2 | 27.4% |
| bb_20_15_pctb_lt_25 | 30.7% |
| bb_20_15_reclaim_from_lower_recent_3d | 20.3% |
| bb_20_15_reclaim_from_upper_recent_3d | 6.6% |
| bb_20_15_squeeze | 30.5% |
| bb_20_15_touch_lower | 16.5% |
| bb_20_15_touch_upper | 25.5% |
| bb_20_20_above_mid | 53.6% |
| bb_20_20_expanding | 54.1% |
| bb_20_20_pctb_gt_75 | 31.8% |
| bb_20_20_pctb_gt_8 | 27.6% |
| bb_20_20_pctb_gt_85 | 23.5% |
| bb_20_20_pctb_gt_9 | 19.0% |
| bb_20_20_pctb_gt_95 | 14.3% |
| bb_20_20_pctb_lt_05 | 6.9% |
| bb_20_20_pctb_lt_1 | 10.5% |
| bb_20_20_pctb_lt_15 | 14.9% |
| bb_20_20_pctb_lt_2 | 19.8% |
| bb_20_20_pctb_lt_25 | 24.6% |
| bb_20_20_reclaim_from_lower_recent_3d | 16.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 4.6% |
| bb_20_20_squeeze | 16.0% |
| bb_20_20_touch_lower | 5.8% |
| bb_20_20_touch_upper | 14.0% |
| bearish_pin_bar | 5.2% |
| below_avwap_20high | 57.0% |
| below_avwap_20low | 11.2% |
| below_avwap_252low | 4.6% |
| below_avwap_50low | 22.3% |
| below_cam_s3 | 7.3% |
| below_cam_s4 | 3.6% |
| below_cpr | 22.3% |
| below_ema_20 | 43.8% |
| below_ema_20_break_recent_5d | 18.7% |
| below_ema_21 | 43.8% |
| below_ema_21_break_recent_5d | 18.7% |
| below_ema_50 | 41.5% |
| below_ema_50_break_recent_5d | 20.8% |
| below_ema_9 | 41.0% |
| below_ema_9_break_recent_5d | 21.7% |
| below_prev_high | 54.8% |
| below_prev_low | 7.2% |
| below_prev_low_clearance_atr_05 | 2.0% |
| below_s1 | 4.5% |
| below_s2 | 2.2% |
| below_sma_20 | 46.4% |
| below_sma_200 | 11.6% |
| below_sma_21 | 46.4% |
| below_sma_50 | 44.2% |
| below_sma_9 | 43.6% |
| below_vwap | 24.9% |
| break_52w_high | 0.8% |
| break_52w_high_clearance_atr_05 | 0.2% |
| break_52w_high_confirmed_today | 0.3% |
| bullish_engulfing | 9.8% |
| bullish_pin_bar | 5.8% |
| capitulation_recent_3d | 1.4% |
| ceo_buy | 0.8% |
| cfo_buy | 0.3% |
| chandelier_long_bullish | 64.1% |
| chandelier_long_flip_dn | 1.3% |
| chandelier_short_bearish | 54.7% |
| chandelier_short_flip_up | 8.9% |
| classification_change_from_tech | 60.0% |
| classification_change_to_defensive | 40.0% |
| close_in_bottom_40pct_of_range | 8.2% |
| close_in_top_40pct_of_range | 74.7% |
| cluster_buy | 0.4% |
| cmf_cross_dn | 2.3% |
| cmf_cross_up | 8.6% |
| cmf_negative | 39.4% |
| cmf_positive | 60.6% |
| concentrated_sell | 7.8% |
| cpr_narrow | 86.7% |
| cpr_narrow_tight | 23.1% |
| cup_handle_detected | 18.2% |
| cup_handle_neckline_break_retest_long | 6.6% |
| dc10_breakout_dn | 4.5% |
| dc10_breakout_dn_1pct | 8.4% |
| dc10_breakout_up | 19.3% |
| dc10_breakout_up_1pct | 27.8% |
| dc10_new_high | 23.1% |
| dc10_strong_breakout_dn | 1.3% |
| dc10_strong_breakout_up | 7.3% |
| dc20_breakout_dn | 3.2% |
| dc20_breakout_up | 14.1% |
| dc20_new_high | 16.8% |
| dc20_resistance_break_retest_strong | 16.3% |
| dc20_support_break_retest_strong | 15.7% |
| defensive_leadership | 55.7% |
| director_only_buy | 2.9% |
| doji | 4.3% |
| double_bottom_detected | 12.8% |
| double_top_detected | 15.4% |
| dpi_elevated | 56.2% |
| drying_volume_on_up_turn | 59.5% |
| ema_20_50_bearish | 37.4% |
| ema_20_50_bullish | 62.6% |
| ema_20_50_death_cross | 1.1% |
| ema_20_50_golden_cross | 2.4% |
| ema_50_200_bearish | 25.4% |
| ema_50_200_bullish | 74.6% |
| ema_50_200_golden_cross | 0.6% |
| ema_9_21_bearish | 50.1% |
| ema_9_21_bullish | 49.9% |
| ema_9_21_death_cross | 2.2% |
| ema_9_21_golden_cross | 4.5% |
| flag_bear_break_retest_short | 0.1% |
| flag_bear_broke | 0.2% |
| flag_bear_detected | 0.1% |
| flag_bull_break_retest_long | 1.2% |
| flag_bull_broke | 1.6% |
| flag_bull_detected | 1.8% |
| force_index_cross_dn | 1.3% |
| force_index_cross_up | 9.0% |
| force_index_positive | 54.7% |
| gap_dn_1_5pct | 11.0% |
| gap_dn_2pct | 7.8% |
| gap_up_1_5pct | 8.8% |
| gap_up_2pct | 5.8% |
| hammer | 4.1% |
| head_shoulders_bottom_detected | 4.3% |
| head_shoulders_top_detected | 5.0% |
| house_cluster_buy | 3.9% |
| house_cluster_sell | 3.9% |
| htf_aligned_bear | 0.9% |
| htf_aligned_bull | 39.0% |
| htf_disagreement | 5.6% |
| hull_bearish | 52.5% |
| hull_bullish | 47.5% |
| hull_flip_dn | 3.1% |
| hull_flip_up | 6.3% |
| ichi_above_cloud | 50.6% |
| ichi_above_cloud_break_recent_5d | 16.9% |
| ichi_below_cloud | 28.8% |
| ichi_below_cloud_break_recent_5d | 9.4% |
| ichi_cloud_thick | 88.1% |
| ichi_tk_bearish | 47.5% |
| ichi_tk_bullish | 44.9% |
| ichi_tk_cross_dn | 2.5% |
| ichi_tk_cross_up | 2.5% |
| ichi_weekly_above_cloud | 61.8% |
| ichi_weekly_below_cloud | 9.4% |
| ichi_weekly_in_cloud | 28.7% |
| in_reversal_window | 5.1% |
| inside_bar | 12.7% |
| inside_cpr | 4.6% |
| inside_kc | 82.3% |
| insider_cluster_active | 20.3% |
| institutional_buy | 99.9% |
| institutional_negative | 0.1% |
| institutional_persistence_growing | 42.0% |
| institutional_persistence_strong | 57.7% |
| institutional_strong_buy | 89.0% |
| inverted_cup_handle_detected | 12.7% |
| is_friday | 19.6% |
| is_halloween_period | 57.9% |
| is_halloween_period_first_day | 0.2% |
| is_january | 10.0% |
| is_january_extended | 12.4% |
| is_monday | 21.2% |
| is_pre_holiday | 4.0% |
| is_summer_period | 42.1% |
| is_totm_window | 34.1% |
| is_totm_window_first_day | 10.6% |
| is_week_open | 24.2% |
| kc_touch_lower | 6.7% |
| kc_touch_upper | 15.3% |
| large_dollar_buy | 1.0% |
| macd_12_26_9_bearish | 57.8% |
| macd_12_26_9_bullish | 42.2% |
| macd_12_26_9_crossover_dn | 2.2% |
| macd_12_26_9_crossover_up | 3.4% |
| macd_8_21_5_bearish | 54.0% |
| macd_8_21_5_bullish | 46.0% |
| macd_8_21_5_crossover_dn | 2.3% |
| macd_8_21_5_crossover_up | 6.0% |
| marubozu_bull | 2.0% |
| mfi_broad_overbought | 13.4% |
| mfi_broad_oversold | 8.9% |
| mfi_overbought | 3.1% |
| mfi_oversold | 1.9% |
| monthly_above_sma_12 | 88.0% |
| monthly_above_sma_6 | 67.0% |
| monthly_bias_bear | 3.9% |
| monthly_bias_bull | 59.0% |
| monthly_momentum_pos | 75.6% |
| morning_star | 8.7% |
| near_52w_high | 2.4% |
| near_52w_high_95pct | 7.8% |
| near_52w_high_retest_long | 4.2% |
| near_avwap_20high_atr_05x | 38.5% |
| near_avwap_20high_atr_10x | 63.7% |
| near_avwap_20high_atr_15x | 82.6% |
| near_avwap_20high_atr_20x | 92.4% |
| near_avwap_20low_atr_05x | 26.9% |
| near_avwap_20low_atr_10x | 49.8% |
| near_avwap_20low_atr_15x | 65.8% |
| near_avwap_20low_atr_20x | 78.6% |
| near_avwap_252low_atr_05x | 8.7% |
| near_avwap_252low_atr_10x | 17.7% |
| near_avwap_252low_atr_15x | 28.9% |
| near_avwap_252low_atr_20x | 39.5% |
| near_avwap_50low_atr_05x | 17.5% |
| near_avwap_50low_atr_10x | 36.0% |
| near_avwap_50low_atr_15x | 51.3% |
| near_avwap_50low_atr_20x | 64.1% |
| near_cam_r3 | 20.7% |
| near_cam_s3 | 6.2% |
| near_cam_s4 | 2.1% |
| near_fib_236 | 5.2% |
| near_fib_382 | 5.9% |
| near_fib_500 | 6.7% |
| near_fib_618 | 6.1% |
| near_fib_786 | 3.7% |
| near_pivot | 13.9% |
| near_prev_close | 14.3% |
| near_prev_high | 15.8% |
| near_prev_low | 4.8% |
| near_r1 | 18.2% |
| near_r1_wide | 64.6% |
| near_r2 | 7.4% |
| near_r2_wide | 44.3% |
| near_s1 | 3.1% |
| near_s1_wide | 27.0% |
| near_s2 | 0.7% |
| near_s2_wide | 10.1% |
| near_s3 | 0.3% |
| near_wood_r1 | 10.4% |
| near_wood_s1 | 7.3% |
| news_uses_polygon_score | 24.9% |
| obv_bearish | 45.7% |
| obv_bullish | 54.3% |
| obv_diverge_bull | 8.3% |
| obv_falling | 45.2% |
| obv_rising | 54.8% |
| outside_bar | 9.4% |
| pead_negative_surprise | 13.1% |
| pead_positive_surprise | 26.5% |
| pin_bar | 10.9% |
| po3_accumulation_active | 28.4% |
| po3_bullish | 22.7% |
| po3_manipulation_sweep_down | 5.3% |
| po3_manipulation_sweep_up | 10.5% |
| po3_mmbm_setup | 4.0% |
| po3_sweep_above_prior_high | 62.6% |
| po3_sweep_below_prior_low | 38.5% |
| ppo_bullish | 41.7% |
| ppo_crossover_dn | 1.8% |
| ppo_crossover_up | 3.3% |
| pre_fomc_d0 | 1.9% |
| pre_fomc_d1 | 2.1% |
| pre_fomc_window | 3.9% |
| price_above_dema | 51.1% |
| price_above_ema_20 | 56.2% |
| price_above_ema_200_break_recent_5d | 41.5% |
| price_above_ema_20_break_recent_5d | 28.4% |
| price_above_ema_21 | 56.2% |
| price_above_ema_21_break_recent_5d | 28.0% |
| price_above_ema_50 | 58.5% |
| price_above_ema_50_break_recent_5d | 26.6% |
| price_above_ema_9 | 59.0% |
| price_above_ema_9_break_recent_5d | 38.4% |
| price_above_hull | 59.6% |
| price_above_sma_200 | 88.4% |
| price_above_sma_21 | 53.6% |
| price_above_sma_50 | 55.8% |
| price_above_tema | 58.6% |
| price_below_dema | 48.9% |
| price_below_hull | 40.4% |
| price_below_tema | 41.4% |
| psar_bullish | 45.9% |
| psar_flip_dn | 2.4% |
| psar_flip_up | 5.0% |
| r1_break_retest_long | 54.7% |
| recent_blowoff_at_r3 | 0.0% |
| recent_capitulation_at_s3 | 0.0% |
| resistance_break_retest | 23.4% |
| risk_off_regime_bond_signal | 24.7% |
| risk_off_regime_bond_signal_strong | 10.6% |
| risk_off_regime_gold_signal | 44.0% |
| risk_on_regime_bond_signal | 38.6% |
| risk_on_regime_bond_signal_strong | 17.6% |
| roc_positive | 51.0% |
| roc_turning_dn | 2.6% |
| roc_turning_up | 7.7% |
| rsi_14_bullish | 56.7% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_14_cross_dn_overbought_recent_3d | 3.3% |
| rsi_14_cross_up_oversold_recent_3d | 4.9% |
| rsi_14_extreme_ob | 0.2% |
| rsi_14_overbought | 5.4% |
| rsi_14_oversold | 0.8% |
| rsi_14_rising | 81.3% |
| rsi_21_bullish | 57.5% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.0% |
| rsi_21_cross_dn_overbought_recent_3d | 1.1% |
| rsi_21_cross_up_oversold_recent_3d | 0.4% |
| rsi_21_overbought | 1.3% |
| rsi_21_rising | 81.4% |
| rsi_2_bullish | 69.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 16.2% |
| rsi_2_cross_dn_overbought_recent_3d | 17.8% |
| rsi_2_cross_up_extreme_os_recent_3d | 42.4% |
| rsi_2_cross_up_oversold_recent_3d | 47.3% |
| rsi_2_extreme_ob | 38.6% |
| rsi_2_extreme_os | 10.8% |
| rsi_2_overbought | 50.4% |
| rsi_2_oversold | 16.6% |
| rsi_2_rising | 81.3% |
| rsi_9_bullish | 56.5% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.4% |
| rsi_9_cross_dn_overbought_recent_3d | 5.8% |
| rsi_9_cross_up_extreme_os_recent_3d | 3.1% |
| rsi_9_cross_up_oversold_recent_3d | 15.3% |
| rsi_9_extreme_ob | 2.8% |
| rsi_9_extreme_os | 0.1% |
| rsi_9_overbought | 14.3% |
| rsi_9_oversold | 6.5% |
| rsi_9_rising | 81.4% |
| s1_break_retest_short | 50.9% |
| sc_13d_filed_within_30d | 2.6% |
| sc_13g_filed_within_30d | 3.2% |
| sector_outperforming_spy | 46.6% |
| sector_underperforming_spy | 53.4% |
| shooting_star | 4.6% |
| sma_20_50_bullish | 57.6% |
| sma_20_50_golden_cross | 1.4% |
| sma_50_200_bullish | 71.4% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 48.5% |
| sma_9_21_golden_cross | 2.9% |
| smc_bos_bearish | 6.8% |
| smc_bos_bullish | 13.9% |
| smc_bos_retest_long | 6.2% |
| smc_bos_retest_short | 4.1% |
| smc_breaker_block_bearish | 8.0% |
| smc_breaker_block_bullish | 28.6% |
| smc_choch_bearish | 5.4% |
| smc_choch_bullish | 6.0% |
| smc_equal_highs_swept | 4.7% |
| smc_equal_lows_swept | 2.2% |
| smc_fvg_bearish_active | 42.4% |
| smc_fvg_bullish_active | 38.1% |
| smc_fvg_retest_long_zone | 2.3% |
| smc_fvg_retest_short_zone | 15.7% |
| smc_in_discount_zone | 55.0% |
| smc_in_premium_zone | 70.7% |
| smc_inverse_fvg_bearish | 78.8% |
| smc_inverse_fvg_bullish | 91.2% |
| smc_liquidity_swept_dn | 1.2% |
| smc_liquidity_swept_up | 1.5% |
| smc_mitigation_block_long | 0.5% |
| smc_mitigation_block_short | 3.1% |
| smc_ob_bearish_active | 22.6% |
| smc_ob_bullish_active | 41.1% |
| smc_ote_long_zone | 9.8% |
| smc_ote_short_zone | 11.4% |
| squeeze_fire_dn | 0.5% |
| squeeze_fire_up | 5.4% |
| squeeze_in | 21.4% |
| squeeze_positive | 54.7% |
| stoch_bearish_cross | 5.9% |
| stoch_broad_overbought | 29.1% |
| stoch_broad_oversold | 27.5% |
| stoch_bullish_cross | 19.0% |
| stoch_overbought | 24.5% |
| stoch_oversold | 20.5% |
| stochrsi_cross_dn | 15.7% |
| stochrsi_cross_up | 38.1% |
| stochrsi_overbought | 32.7% |
| stochrsi_oversold | 28.5% |
| supertrend_bearish | 2.7% |
| supertrend_bullish | 97.3% |
| supertrend_flip_dn | 0.4% |
| supertrend_flip_recent_long_5d | 3.2% |
| supertrend_flip_recent_short_5d | 4.2% |
| supertrend_flip_up | 1.3% |
| support_break_retest | 22.5% |
| tema_above_dema | 43.9% |
| tema_cross_dn | 1.4% |
| tema_cross_up | 2.9% |
| three_white_soldiers | 11.4% |
| triangle_apex_break_retest_long | 13.1% |
| triangle_ascending_detected | 9.3% |
| triangle_descending_detected | 9.0% |
| uo_overbought | 3.6% |
| uo_oversold | 1.0% |
| usd_strengthening | 21.9% |
| usd_weakening | 13.2% |
| vix_band_high | 44.0% |
| vix_band_low | 34.4% |
| vix_band_mid | 21.6% |
| vix_term_backwardation | 11.7% |
| vix_term_contango | 88.3% |
| vol_above_avg | 40.5% |
| vol_below_avg | 59.5% |
| vol_spike_12x | 25.8% |
| vol_spike_15x | 13.6% |
| vol_spike_17x | 9.0% |
| vol_spike_2x | 4.9% |
| vol_spike_2x_on_down_day_recent_3d | 6.1% |
| vol_spike_2x_on_up_day_recent_3d | 4.2% |
| vol_spike_3x | 1.3% |
| vp_above_value_area | 26.6% |
| vp_below_value_area | 11.6% |
| vp_close_above_poc | 60.1% |
| vp_close_below_poc | 39.9% |
| vp_in_value_area | 61.8% |
| week_open_gap_down_15pct | 3.6% |
| week_open_gap_up_15pct | 1.9% |
| weekly_above_ema_10 | 59.2% |
| weekly_above_ema_20 | 73.6% |
| weekly_bias_bear | 23.9% |
| weekly_bias_bull | 56.6% |
| weekly_momentum_pos | 52.5% |
| williams_r_overbought | 31.8% |
| williams_r_oversold | 13.0% |
| williams_r_rising | 78.2% |
| within_pead_window | 39.0% |
| within_post_deletion_window | 0.5% |
| within_post_inclusion_window | 5.4% |
| xs_avoid_high_ivol | 70.6% |
| xs_avoid_high_max | 70.7% |
| xs_high_beta_decile | 27.5% |
| xs_low_beta_bottom_quintile | 27.5% |
| xs_low_beta_decile | 16.5% |
| xs_low_beta_decile_entry_recent_5d | 0.7% |
| xs_low_beta_top_quintile | 16.5% |
| xs_momentum_bottom_decile | 2.6% |
| xs_momentum_bottom_quintile | 8.5% |
| xs_momentum_top_decile | 21.3% |
| xs_momentum_top_quintile | 33.6% |
| xs_quality_bottom_quintile | 20.0% |
| xs_quality_top_quintile | 21.8% |
| xs_quality_top_tercile | 42.1% |
| year_high_break_retest_long | 0.8% |
| yoy_surprise_high | 55.2% |
| yoy_surprise_negative | 35.5% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 96.9% |
| committed_growth_holders | 96.9% |
| corp_donations_1y | 7.6% |
| corp_donations_count_1y | 7.6% |
| corp_donations_unique_pacs | 7.6% |
| cot_rut_commercials_pctile_3y | 55.4% |
| cot_rut_mmoney_pctile_3y | 55.4% |
| cup_handle_depth_pct | 25.8% |
| days_since_classification_change | 0.2% |
| days_since_deletion | 6.6% |
| days_since_inclusion | 16.3% |
| days_to_next_holiday | 69.9% |
| days_to_rebalance | 7.4% |
| dpi_30d_avg | 96.5% |
| dpi_recent | 96.5% |
| earnings_announcement_return | 90.7% |
| earnings_eps_yoy_growth | 94.8% |
| flag_bear_pole_move_pct | 0.1% |
| flag_bull_pole_move_pct | 1.8% |
| gov_contracts_4q_sum | 39.5% |
| gov_contracts_last_qtr_amount | 39.5% |
| gov_contracts_qoq_growth | 39.5% |
| head_shoulders_magnitude_pct | 9.0% |
| insider_director_buyers_30d | 4.3% |
| insider_officer_buyers_30d | 4.3% |
| insider_total_shares_bought_30d | 4.3% |
| insider_unique_buyers_30d | 4.3% |
| inverted_cup_handle_height_pct | 22.3% |
| lobbying_amount_1y | 72.2% |
| lobbying_amount_q | 72.2% |
| lobbying_amount_yoy | 72.2% |
| monthly_momentum_6m | 95.4% |
| otc_short_ratio_recent | 96.5% |
| otc_volume_recent | 96.5% |
| pair_half_life | 92.8% |
| pair_max_abs_zscore | 92.8% |
| pair_zscore_signed | 92.8% |
| pct_from_avwap_20high | 82.7% |
| pct_from_avwap_20low | 87.5% |
| pct_from_avwap_252low | 96.4% |
| pct_from_avwap_50low | 95.3% |
| persistent_holders_4q | 96.9% |
| persistent_holders_8q | 96.9% |
| sc_13g_latest_percent_owned | 1.7% |
| search_volume_index_recent | 75.7% |
| search_volume_observations | 75.7% |
| search_volume_zscore_30d | 75.7% |
| sector_etf_return_20d | 2.1% |
| spy_return_20d | 2.1% |
| total_active_holders | 96.9% |
| triangle_breakdown_pct | 9.0% |
| triangle_breakout_pct | 9.3% |
| xs_quality_decile | 60.2% |
| xs_quality_gross_profitability | 60.2% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.999), `double_top_neckline` (0.999), `double_top_peak` (0.999), `entry_stop_long` (0.997), `entry_stop_short` (0.998), `fib_236` (0.998), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.997), `fib_ext_162` (0.995), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.998), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.995), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.998), `monthly_sma_12` (0.992), `monthly_sma_6` (0.997), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.998), `s2` (0.997), `s3` (0.997), `supertrend_value` (0.996), `swing_high` (0.998), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.998), `vp_value_area_low` (0.996), `vwap_upper_1` (0.954), `vwap_upper_2` (0.96), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.994), `year_low` (0.955)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 8 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 7 |
| P2.1 | rsi span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |

```
FULL FACTORIAL     8 x 3 = 24
offline gradings   0 level-combinations x 24 exits = 0 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  23 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 0 + 23 = 24 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 629 census axes join it only when REGISTERED at the T3 band review.
