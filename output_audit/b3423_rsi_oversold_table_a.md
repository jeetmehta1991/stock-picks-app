# Table A - rsi_oversold

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 37ba09e03 | commit 5ac63c461 at 2026-11-09 22:18:43 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** mean_reversion | **status:** NOT-STARTED | **R5 fires:** 1945 (closed fires in the exit cube: 1945 of 1945, S6-B3258) | **surviving fires (T1):** 1945 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_ema_200  <- backtest/signals/technical.py (f-string template)
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)
P2  below_sma_50  <- backtest/signals/technical.py (f-string template)
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P2.1-P2.1 (band rows in Table A)
P3  price_above_ema_200  <- backtest/signals/technical.py (f-string template) +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P3.1-P3.1 (band rows in Table A)
P4  price_above_sma_50  <- backtest/signals/technical.py (f-string template) +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P4.1-P4.1 (band rows in Table A)
P5  rsi_14  <- backtest/signals/polars_panel.py (f-string template) +2
       DEFN: Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540)
       knobs P5.1-P5.1 (band rows in Table A)
P6  rsi_2  <- backtest/signals/polars_panel.py (f-string template) +2
       DEFN: Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540)
       knobs P6.1-P6.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P7  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_rsi_oversold (docstring and return dropped):

```python
rsi_2 = s.get('rsi_2', 50)
rsi_14 = s.get('rsi_14', 50)
above_200 = s.get('price_above_ema_200', False)
below_200 = s.get('below_ema_200', False)
fl = (rsi_2 < 7 or rsi_14 < 40) and s.get('price_above_sma_50') and above_200
fs = (rsi_2 > 93 or rsi_14 > 60) and s.get('below_sma_50') and below_200 and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | below_ema_200 - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - producer_variant_table.SPECS['bollinger_lower'] P3/P4; backtest/signals/technical.py compute_ema_sma | SPECS bollinger_lower P3/P4 (T3/Q2-APPROVED 2026-09-27): production 200 + resim spans [9, 20, 21, 50, 100, 150, 250] | 200 | 9, 20, 21, 50, 100, 150, 200, 250 | offline 0 of 8 levels - canon-span FLAGS (above/below ema 9/20/21/50/200) ARE persisted - measured 200-of-200 bollinger fires, S6-B3117b; offline as ADD-A-CONDITION legs only. The SWAP of the gate span, and non-canon spans, are RESIM | the whole band except production (resim_band [9, 20, 21, 50, 100, 150, 250]); env STRAT_EMA_SPAN does not reach this gate - it reads the literal key - DEFINED-NO-ACTUATOR here (S6-B3253) | T3 review before any grid |
| P2 | PRODUCER | below_sma_50 - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P2.1 | BAND | sma span - backtest/signals/technical.py sma block | BRACKET production with adjacent canon spans | 50 | [20, 50, 100] | offline 0 of 3 levels - none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/technical.py (f-string template) +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P3.1 | BAND | ema span (the 200 in above/below_ema_200) - producer_variant_table.SPECS['bollinger_lower'] P3/P4; backtest/signals/technical.py compute_ema_sma | SPECS bollinger_lower P3/P4 (T3/Q2-APPROVED 2026-09-27): production 200 + resim spans [9, 20, 21, 50, 100, 150, 250] | 200 | 9, 20, 21, 50, 100, 150, 200, 250 | offline 0 of 8 levels - canon-span FLAGS (above/below ema 9/20/21/50/200) ARE persisted - measured 200-of-200 bollinger fires, S6-B3117b; offline as ADD-A-CONDITION legs only. The SWAP of the gate span, and non-canon spans, are RESIM | the whole band except production (resim_band [9, 20, 21, 50, 100, 150, 250]); env STRAT_EMA_SPAN does not reach this gate - it reads the literal key - DEFINED-NO-ACTUATOR here (S6-B3253) | T3 review before any grid |
| P4 | PRODUCER | price_above_sma_50 - emitted by backtest/signals/technical.py (f-string template) +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P4.1 | BAND | sma span - backtest/signals/technical.py sma block | BRACKET production with adjacent canon spans | 50 | [20, 50, 100] | offline 0 of 3 levels - none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | PRODUCER | rsi_14 - emitted by backtest/signals/polars_panel.py (f-string template) +2; the boolean's UNDERLYING condition is bandable through its producer's internals | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P5.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | offline 0 of 3 levels - none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | PRODUCER | rsi_2 - emitted by backtest/signals/polars_panel.py (f-string template) +2; the boolean's UNDERLYING condition is bandable through its producer's internals | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P6.1 | BAND | rsi (fast escape-hatch) span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 2 | [2, 3, 5] | offline 0 of 3 levels - none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | STRATEGY | OR-composite `(rsi_2 < 7 OR rsi_14 < 40)` [EXISTING-THRESHOLD, OR-composite - S6-B3429] | an `or` of numeric cuts: tightening either arm keeps a subset of the recorded fires, and per-arm retention needs the gate's arm | `rsi_2 < 7 or rsi_14 < 40` | production arms as written | offline 0 of 1 levels - arm-conditioned tighter levels are measured at grid time - the sweep takes the arms as @group axes (S6-B3290, the williams_r_oversold precedent) | - (the arms' magnitudes are persisted on the fires) | OR-COMPOSITE-REGISTERED |
| P8 | STRATEGY | OR-composite `(rsi_2 > 93 OR rsi_14 > 60)` [EXISTING-THRESHOLD, OR-composite - S6-B3429] | an `or` of numeric cuts: tightening either arm keeps a subset of the recorded fires, and per-arm retention needs the gate's arm | `rsi_2 > 93 or rsi_14 > 60` | production arms as written | offline 0 of 1 levels - arm-conditioned tighter levels are measured at grid time - the sweep takes the arms as @group axes (S6-B3290, the williams_r_oversold precedent) | - (the arms' magnitudes are persisted on the fires) | OR-COMPOSITE-REGISTERED |
| P9 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
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
| adx | backtest/signals/technical.py | 100.0% | 20.208, 25.206, 30.188, 36.912 | 20.208: 1556 (80%); 25.206: 1167 (60%); 30.188: 778 (40%); 36.912: 389 (20%) | 20.208: 389 (20%); 25.206: 778 (40%); 30.188: 1167 (60%); 36.912: 1556 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 19.95, 22.456, 24.57, 27.41 | 19.95: 1557 (80%); 22.456: 1167 (60%); 24.57: 779 (40%); 27.41: 390 (20%) | 19.95: 390 (20%); 22.456: 778 (40%); 24.57: 1168 (60%); 27.41: 1557 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 20.05, 22.516, 24.93, 27.552 | 20.05: 1558 (80%); 22.516: 1167 (60%); 24.93: 779 (40%); 27.552: 389 (20%) | 20.05: 390 (20%); 22.516: 778 (40%); 24.93: 1169 (60%); 27.552: 1556 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -4.5822, -1.1677, 1.4533, 5.2522 | -4.5822: 1556 (80%); -1.1677: 1167 (60%); 1.4533: 778 (40%); 5.2522: 389 (20%) | -4.5822: 389 (20%); -1.1677: 778 (40%); 1.4533: 1167 (60%); 5.2522: 1556 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.1128, 1.9503, 3.1328, 5.5554 | 1.1128: 1556 (80%); 1.9503: 1167 (60%); 3.1328: 778 (40%); 5.5554: 389 (20%) | 1.1128: 389 (20%); 1.9503: 778 (40%); 3.1328: 1167 (60%); 5.5554: 1556 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.1128, 1.9503, 3.1328, 5.5554 | 1.1128: 1556 (80%); 1.9503: 1167 (60%); 3.1328: 778 (40%); 5.5554: 389 (20%) | 1.1128: 389 (20%); 1.9503: 778 (40%); 3.1328: 1167 (60%); 5.5554: 1556 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.922, 2.3642, 2.865, 3.7278 | 1.922: 1557 (80%); 2.3642: 1167 (60%); 2.865: 779 (40%); 3.7278: 389 (20%) | 1.922: 390 (20%); 2.3642: 778 (40%); 2.865: 1170 (60%); 3.7278: 1556 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0496, 0.0667, 0.0891, 0.1246 | 0.0496: 1558 (80%); 0.0667: 1167 (60%); 0.0891: 779 (40%); 0.1246: 390 (20%) | 0.0496: 391 (20%); 0.0667: 782 (40%); 0.0891: 1167 (60%); 0.1246: 1556 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.0647, 0.1981, 0.8111, 0.9322 | 0.0647: 1556 (80%); 0.1981: 1167 (60%); 0.8111: 778 (40%); 0.9322: 390 (20%) | 0.0647: 391 (20%); 0.1981: 778 (40%); 0.8111: 1167 (60%); 0.9322: 1557 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.056, 0.0799, 0.1122, 0.1627 | 0.056: 1557 (80%); 0.0799: 1167 (60%); 0.1122: 782 (40%); 0.1627: 390 (20%) | 0.056: 391 (20%); 0.0799: 778 (40%); 0.1122: 1167 (60%); 0.1627: 1557 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2413, 0.4349, 0.5732, 0.7536 | 0.2413: 1556 (80%); 0.4349: 1168 (60%); 0.5732: 778 (40%); 0.7536: 389 (20%) | 0.2413: 389 (20%); 0.4349: 779 (40%); 0.5732: 1167 (60%); 0.7536: 1556 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0746, 0.1065, 0.1497, 0.2169 | 0.0746: 1557 (80%); 0.1065: 1167 (60%); 0.1497: 779 (40%); 0.2169: 390 (20%) | 0.0746: 390 (20%); 0.1065: 778 (40%); 0.1497: 1167 (60%); 0.2169: 1556 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.306, 0.4512, 0.5549, 0.6902 | 0.306: 1556 (80%); 0.4512: 1167 (60%); 0.5549: 778 (40%); 0.6902: 389 (20%) | 0.306: 389 (20%); 0.4512: 779 (40%); 0.5549: 1167 (60%); 0.6902: 1556 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0488, -0.025, -0.0061, 0.0255 | -0.0488: 1558 (80%); -0.025: 1171 (60%); -0.0061: 783 (40%); 0.0255: 390 (20%) | -0.0488: 396 (20%); -0.025: 781 (40%); -0.0061: 1170 (60%); 0.0255: 1557 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1422, 0.1663, 0.2043, 0.2598 | 0.1422: 1556 (80%); 0.1663: 1163 (60%); 0.2043: 778 (40%); 0.2598: 399 (21%) | 0.1422: 389 (20%); 0.1663: 782 (40%); 0.2043: 1167 (60%); 0.2598: 1546 (79%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1945 (100%) | 0: 1842 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0797, -0.004, 0.0607, 0.1386 | -0.0797: 1556 (80%); -0.004: 1167 (60%); 0.0607: 779 (40%); 0.1386: 390 (20%) | -0.0797: 392 (20%); -0.004: 778 (40%); 0.0607: 1169 (60%); 0.1386: 1556 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1945 (100%); 1: 723 (37%) | 0: 1222 (63%); 1: 1636 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2389, -0.1909, -0.1539, -0.1204 | -0.2389: 1556 (80%); -0.1909: 1184 (61%); -0.1539: 786 (40%); -0.1204: 411 (21%) | -0.2389: 389 (20%); -0.1909: 838 (43%); -0.1539: 1177 (61%); -0.1204: 1557 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.6026, 0.6859, 0.7628 | 0.391: 1559 (80%); 0.6026: 1189 (61%); 0.6859: 785 (40%); 0.7628: 396 (20%) | 0.391: 397 (20%); 0.6026: 825 (42%); 0.6859: 1178 (61%); 0.7628: 1569 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.391, 0.6603, 0.8333 | 0.2628: 1560 (80%); 0.391: 1170 (60%); 0.6603: 792 (41%); 0.8333: 418 (21%) | 0.2628: 494 (25%); 0.391: 786 (40%); 0.6603: 1173 (60%); 0.8333: 1568 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1288, -0.0361, 0.0823, 0.1961 | -0.1288: 1558 (80%); -0.0361: 1195 (61%); 0.0823: 782 (40%); 0.1961: 398 (20%) | -0.1288: 392 (20%); -0.0361: 779 (40%); 0.0823: 1170 (60%); 0.1961: 1557 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2372, 0.3974, 0.5897, 0.7949 | 0.2372: 1562 (80%); 0.3974: 1246 (64%); 0.5897: 827 (43%); 0.7949: 406 (21%) | 0.2372: 407 (21%); 0.3974: 779 (40%); 0.5897: 1174 (60%); 0.7949: 1565 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.109, 0.2949, 0.4551, 0.6923 | 0.109: 1589 (82%); 0.2949: 1169 (60%); 0.4551: 781 (40%); 0.6923: 390 (20%) | 0.109: 419 (22%); 0.2949: 812 (42%); 0.4551: 1184 (61%); 0.6923: 1561 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.5017, -0.3354, -0.1216, 0.0936 | -0.5017: 1561 (80%); -0.3354: 1180 (61%); -0.1216: 778 (40%); 0.0936: 396 (20%) | -0.5017: 391 (20%); -0.3354: 780 (40%); -0.1216: 1167 (60%); 0.0936: 1562 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3269, 0.523, 0.8269, 0.9487 | 0.3269: 1559 (80%); 0.523: 1167 (60%); 0.8269: 793 (41%); 0.9487: 406 (21%) | 0.3269: 393 (20%); 0.523: 778 (40%); 0.8269: 1173 (60%); 0.9487: 1584 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1154, 0.359, 0.5641, 0.8462 | 0.1154: 1578 (81%); 0.359: 1180 (61%); 0.5641: 782 (40%); 0.8462: 393 (20%) | 0.1154: 400 (21%); 0.359: 793 (41%); 0.5641: 1179 (61%); 0.8462: 1571 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0681, -0.0577, -0.0395, 0 | -0.0681: 1557 (80%); -0.0577: 1170 (60%); -0.0395: 778 (40%); 0: 564 (29%) | -0.0681: 411 (21%); -0.0577: 790 (41%); -0.0395: 1167 (60%); 0: 1909 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4359, 0.641, 0.8846, 1 | 0.4359: 1567 (81%); 0.641: 1171 (60%); 0.8846: 788 (41%); 1: 443 (23%) | 0.4359: 392 (20%); 0.641: 784 (40%); 0.8846: 1245 (64%); 1: 1945 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1282, 0.2756, 0.5923, 0.9295 | 0.1282: 1565 (80%); 0.2756: 1184 (61%); 0.5923: 778 (40%); 0.9295: 394 (20%) | 0.1282: 425 (22%); 0.2756: 781 (40%); 0.5923: 1167 (60%); 0.9295: 1557 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0013, 0.0366, 0.084, 0.1869 | 0.0013: 1574 (81%); 0.0366: 1172 (60%); 0.084: 785 (40%); 0.1869: 394 (20%) | 0.0013: 448 (23%); 0.0366: 789 (41%); 0.084: 1172 (60%); 0.1869: 1558 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.483, 0.7789, 0.9354, 0.9679 | 0.483: 1559 (80%); 0.7789: 1180 (61%); 0.9354: 778 (40%); 0.9679: 431 (22%) | 0.483: 390 (20%); 0.7789: 787 (40%); 0.9354: 1167 (60%); 0.9679: 1559 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0917, 0.3526, 0.6026, 0.7692 | 0.0917: 1571 (81%); 0.3526: 1175 (60%); 0.6026: 818 (42%); 0.7692: 400 (21%) | 0.0917: 390 (20%); 0.3526: 790 (41%); 0.6026: 1206 (62%); 0.7692: 1580 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0203, 0.0787, 0.2205 | -0.0812: 1681 (86%); -0.0203: 1292 (66%); 0.0787: 782 (40%); 0.2205: 390 (20%) | -0.0812: 474 (24%); -0.0203: 786 (40%); 0.0787: 1178 (61%); 0.2205: 1561 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1475, -0.0039, 0.0504, 0.1 | -0.1475: 1557 (80%); -0.0039: 1189 (61%); 0.0504: 780 (40%); 0.1: 390 (20%) | -0.1475: 409 (21%); -0.0039: 793 (41%); 0.0504: 1188 (61%); 0.1: 1564 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3654, 0.5705, 0.7821, 0.9038 | 0.3654: 1563 (80%); 0.5705: 1194 (61%); 0.7821: 804 (41%); 0.9038: 390 (20%) | 0.3654: 404 (21%); 0.5705: 816 (42%); 0.7821: 1169 (60%); 0.9038: 1558 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1987, 0.3846, 0.6538, 0.8205 | 0.1987: 1563 (80%); 0.3846: 1205 (62%); 0.6538: 795 (41%); 0.8205: 402 (21%) | 0.1987: 419 (22%); 0.3846: 843 (43%); 0.6538: 1180 (61%); 0.8205: 1560 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.045, 0.11, 0.2151, 0.4467 | 0.045: 1562 (80%); 0.11: 1175 (60%); 0.2151: 778 (40%); 0.4467: 391 (20%) | 0.045: 394 (20%); 0.11: 779 (40%); 0.2151: 1167 (60%); 0.4467: 1559 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.7% | 28, 61, 82, 140 | 28: 1554 (80%); 61: 1175 (60%); 82: 778 (40%); 140: 387 (20%) | 28: 388 (20%); 61: 773 (40%); 82: 1160 (60%); 140: 1539 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.6% | 1.6786, 2.2589, 2.8966, 3.8976 | 1.6786: 1549 (80%); 2.2589: 1162 (60%); 2.8966: 775 (40%); 3.8976: 388 (20%) | 1.6786: 388 (20%); 2.2589: 775 (40%); 2.8966: 1162 (60%); 3.8976: 1549 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 16, 27, 33 | 9: 1581 (81%); 16: 1184 (61%); 27: 795 (41%); 33: 418 (21%) | 9: 431 (22%); 16: 802 (41%); 27: 1214 (62%); 33: 1598 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3, 4 | 1: 1618 (83%); 2: 1240 (64%); 3: 809 (42%); 4: 406 (21%) | 1: 705 (36%); 2: 1136 (58%); 3: 1539 (79%); 4: 1945 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0139, -0.0039, 0.0131, 0.0232 | -0.0139: 1557 (80%); -0.0039: 1167 (60%); 0.0131: 784 (40%); 0.0232: 391 (20%) | -0.0139: 395 (20%); -0.0039: 778 (40%); 0.0131: 1177 (61%); 0.0232: 1559 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6557, 25.6703, 26.4855, 27.0901 | 24.6557: 1558 (80%); 25.6703: 1167 (60%); 26.4855: 792 (41%); 27.0901: 389 (20%) | 24.6557: 393 (20%); 25.6703: 778 (40%); 26.4855: 1182 (61%); 27.0901: 1556 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.7778, -0.2142, 0.1238, 0.607 | -0.7778: 1556 (80%); -0.2142: 1167 (60%); 0.1238: 778 (40%); 0.607: 391 (20%) | -0.7778: 389 (20%); -0.2142: 778 (40%); 0.1238: 1167 (60%); 0.607: 1557 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.607, -0.1238, 0.2142, 0.7778 | -0.607: 1557 (80%); -0.1238: 1167 (60%); 0.2142: 778 (40%); 0.7778: 389 (20%) | -0.607: 391 (20%); -0.1238: 778 (40%); 0.2142: 1167 (60%); 0.7778: 1556 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.044, -0.0095, 0.0218, 0.0609 | -0.044: 1556 (80%); -0.0095: 1183 (61%); 0.0218: 782 (40%); 0.0609: 391 (20%) | -0.044: 389 (20%); -0.0095: 786 (40%); 0.0218: 1170 (60%); 0.0609: 1557 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.1598, 8.5135, 8.7773, 9.1118 | 8.1598: 1556 (80%); 8.5135: 1179 (61%); 8.7773: 779 (40%); 9.1118: 389 (20%) | 8.1598: 389 (20%); 8.5135: 766 (39%); 8.7773: 1166 (60%); 9.1118: 1556 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1931 (99%); 1: 596 (31%) | 0: 1335 (69%); 1: 1755 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | -1, 0 | -1: 1825 (94%); 0: 1539 (79%) | -1: 392 (20%); 0: 1628 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1931 (99%); 1: 644 (33%) | 0: 1287 (66%); 1: 1706 (88%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 147, 265.2 | 3: 1605 (83%); 6: 1237 (64%); 147: 779 (40%); 265.2: 389 (20%) | 3: 474 (24%); 6: 806 (41%); 147: 1170 (60%); 265.2: 1556 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 4, 85, 136 | 1: 1614 (83%); 4: 1222 (63%); 85: 785 (40%); 136: 396 (20%) | 1: 493 (25%); 4: 781 (40%); 85: 1170 (60%); 136: 1559 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.5625, -0.1326, 0.1511, 0.652 | -0.5625: 1556 (80%); -0.1326: 1167 (60%); 0.1511: 778 (40%); 0.652: 389 (20%) | -0.5625: 389 (20%); -0.1326: 778 (40%); 0.1511: 1167 (60%); 0.652: 1556 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.0662, -0.6338, 0.741, 2.3922 | -2.0662: 1556 (80%); -0.6338: 1167 (60%); 0.741: 779 (40%); 2.3922: 389 (20%) | -2.0662: 389 (20%); -0.6338: 778 (40%); 0.741: 1167 (60%); 2.3922: 1556 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.7786, -0.8861, 0.9927, 2.9259 | -2.7786: 1556 (80%); -0.8861: 1167 (60%); 0.9927: 778 (40%); 2.9259: 389 (20%) | -2.7786: 389 (20%); -0.8861: 778 (40%); 0.9927: 1167 (60%); 2.9259: 1556 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.7681, -0.2657, 0.2541, 0.7913 | -0.7681: 1556 (80%); -0.2657: 1167 (60%); 0.2541: 778 (40%); 0.7913: 390 (20%) | -0.7681: 389 (20%); -0.2657: 778 (40%); 0.2541: 1167 (60%); 0.7913: 1556 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.3808, -0.2838, 0.4708, 1.7101 | -1.3808: 1556 (80%); -0.2838: 1167 (60%); 0.4708: 778 (40%); 1.7101: 389 (20%) | -1.3808: 389 (20%); -0.2838: 778 (40%); 0.4708: 1167 (60%); 1.7101: 1556 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.2143, -0.6574, 0.7479, 2.4949 | -2.2143: 1556 (80%); -0.6574: 1167 (60%); 0.7479: 778 (40%); 2.4949: 389 (20%) | -2.2143: 390 (20%); -0.6574: 780 (40%); 0.7479: 1167 (60%); 2.4949: 1556 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 41.042, 48.5, 54.61, 62.246 | 41.042: 1556 (80%); 48.5: 1168 (60%); 54.61: 779 (40%); 62.246: 389 (20%) | 41.042: 389 (20%); 48.5: 779 (40%); 54.61: 1168 (60%); 62.246: 1556 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.5% | -0.1434, -0.0386, 0.0411, 0.1541 | -0.1434: 1550 (80%); -0.0386: 1162 (60%); 0.0411: 775 (40%); 0.1541: 388 (20%) | -0.1434: 388 (20%); -0.0386: 777 (40%); 0.0411: 1162 (60%); 0.1541: 1549 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.7% | 0.0068, 0.0145, 0.0271, 0.0488 | 0.0068: 1550 (80%); 0.0145: 1166 (60%); 0.0271: 777 (40%); 0.0488: 388 (20%) | 0.0068: 390 (20%); 0.0145: 774 (40%); 0.0271: 1163 (60%); 0.0488: 1552 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 8 | 0: 1945 (100%); 1: 1428 (73%); 4: 791 (41%); 8: 430 (22%) | 0: 517 (27%); 1: 829 (43%); 4: 1275 (66%); 8: 1560 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 1945 (100%); 0.1667: 391 (20%) | 0: 1326 (68%); 0.1667: 1584 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.087, 0.4, 0.6667 | 0: 1945 (100%); 0.087: 1167 (60%); 0.4: 801 (41%); 0.6667: 405 (21%) | 0: 773 (40%); 0.087: 778 (40%); 0.4: 1189 (61%); 0.6667: 1603 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 1945 (100%); 1: 1333 (69%); 2: 986 (51%); 6: 418 (21%) | 0: 612 (31%); 1: 959 (49%); 2: 1172 (60%); 6: 1586 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 8 | 0: 1945 (100%); 1: 1428 (73%); 4: 791 (41%); 8: 430 (22%) | 0: 517 (27%); 1: 829 (43%); 4: 1275 (66%); 8: 1560 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1945 (100%); 1: 1399 (72%); 3: 830 (43%); 7: 418 (21%) | 0: 546 (28%); 1: 905 (47%); 3: 1258 (65%); 7: 1583 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2158, 0.3618, 0.5615 | 0: 1805 (93%); 0.2158: 1167 (60%); 0.3618: 779 (40%); 0.5615: 389 (20%) | 0: 439 (23%); 0.2158: 778 (40%); 0.3618: 1167 (60%); 0.5615: 1556 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1613, 0.5789 | 0: 1756 (90%); 0.1613: 779 (40%); 0.5789: 390 (20%) | 0: 1072 (55%); 0.1613: 1168 (60%); 0.5789: 1557 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2775, 0.557 | 0: 1788 (92%); 0.2775: 778 (40%); 0.557: 389 (20%) | 0: 890 (46%); 0.2775: 1167 (60%); 0.557: 1556 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2775, 0.557 | 0: 1788 (92%); 0.2775: 778 (40%); 0.557: 389 (20%) | 0: 890 (46%); 0.2775: 1167 (60%); 0.557: 1556 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1667, 0, 0.1847 | -0.1667: 1566 (81%); 0: 1406 (72%); 0.1847: 389 (20%) | -0.1667: 392 (20%); 0: 1381 (71%); 0.1847: 1556 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7107, -0.3101, 0, 1.1169 | -0.7107: 1556 (80%); -0.3101: 1167 (60%); 0: 1035 (53%); 1.1169: 389 (20%) | -0.7107: 390 (20%); -0.3101: 778 (40%); 0: 1205 (62%); 1.1169: 1556 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 1644 (85%); 4: 1284 (66%); 7: 833 (43%); 11: 428 (22%) | 2: 481 (25%); 4: 820 (42%); 7: 1234 (63%); 11: 1582 (81%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0292, -0.0077, 0.0123, 0.044 | -0.0292: 1557 (80%); -0.0077: 1166 (60%); 0.0123: 778 (40%); 0.044: 391 (20%) | -0.0292: 388 (20%); -0.0077: 779 (40%); 0.0123: 1167 (60%); 0.044: 1554 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0519, -0.0114, 0.0162, 0.0539 | -0.0519: 1556 (80%); -0.0114: 1168 (60%); 0.0162: 777 (40%); 0.0539: 390 (20%) | -0.0519: 389 (20%); -0.0114: 777 (40%); 0.0162: 1168 (60%); 0.0539: 1555 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0381, -0.0221, 0.0307, 0.0603 | -0.0381: 1556 (80%); -0.0221: 1167 (60%); 0.0307: 777 (40%); 0.0603: 388 (20%) | -0.0381: 389 (20%); -0.0221: 778 (40%); 0.0307: 1168 (60%); 0.0603: 1557 (80%) | OFFLINE |
| pct_from_avwap_252low | backtest/signals/technical.py (f-string template) | 99.7% | -0.2984, 3.9194, 7.2836, 12.7752 | -0.2984: 1551 (80%); 3.9194: 1163 (60%); 7.2836: 776 (40%); 12.7752: 388 (20%) | -0.2984: 388 (20%); 3.9194: 776 (40%); 7.2836: 1163 (60%); 12.7752: 1551 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/technical.py (f-string template) | 100.0% | 1.5466, 2.8948, 4.3164, 6.3126 | 1.5466: 1556 (80%); 2.8948: 1167 (60%); 4.3164: 778 (40%); 6.3126: 389 (20%) | 1.5466: 389 (20%); 2.8948: 778 (40%); 4.3164: 1167 (60%); 6.3126: 1556 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -18.7568, -4.3588, 5.9464, 23.0512 | -18.7568: 1556 (80%); -4.3588: 1167 (60%); 5.9464: 778 (40%); 23.0512: 389 (20%) | -18.7568: 389 (20%); -4.3588: 778 (40%); 5.9464: 1167 (60%); 23.0512: 1556 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0346, 0.0456, 0.0602, 0.0846 | 0.0346: 1558 (80%); 0.0456: 1174 (60%); 0.0602: 779 (40%); 0.0846: 391 (20%) | 0.0346: 392 (20%); 0.0456: 779 (40%); 0.0602: 1170 (60%); 0.0846: 1556 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1457, 0.3333, 0.5768, 0.8029 | 0.1457: 1556 (80%); 0.3333: 1172 (60%); 0.5768: 778 (40%); 0.8029: 389 (20%) | 0.1457: 390 (20%); 0.3333: 779 (40%); 0.5768: 1167 (60%); 0.8029: 1556 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.4866, -1.1601, 1.023, 1.9936 | -2.4866: 1556 (80%); -1.1601: 1167 (60%); 1.023: 778 (40%); 1.9936: 389 (20%) | -2.4866: 389 (20%); -1.1601: 778 (40%); 1.023: 1167 (60%); 1.9936: 1556 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.5207, -0.2297, 0.1947, 0.7355 | -0.5207: 1556 (80%); -0.2297: 1167 (60%); 0.1947: 778 (40%); 0.7355: 389 (20%) | -0.5207: 389 (20%); -0.2297: 778 (40%); 0.1947: 1167 (60%); 0.7355: 1556 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -3.0761, -1.6949, 1.3745, 2.4556 | -3.0761: 1556 (80%); -1.6949: 1167 (60%); 1.3745: 778 (40%); 2.4556: 389 (20%) | -3.0761: 389 (20%); -1.6949: 778 (40%); 1.3745: 1167 (60%); 2.4556: 1556 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -3.0994, -0.927, 1.2846, 4.4424 | -3.0994: 1556 (80%); -0.927: 1167 (60%); 1.2846: 778 (40%); 4.4424: 389 (20%) | -3.0994: 389 (20%); -0.927: 778 (40%); 1.2846: 1167 (60%); 4.4424: 1556 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 45.556, 48.88, 51.754, 54.772 | 45.556: 1556 (80%); 48.88: 1169 (60%); 51.754: 778 (40%); 54.772: 389 (20%) | 45.556: 389 (20%); 48.88: 779 (40%); 51.754: 1167 (60%); 54.772: 1556 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 4.068, 6.09, 93.844, 95.942 | 4.068: 1556 (80%); 6.09: 1168 (60%); 93.844: 778 (40%); 95.942: 389 (20%) | 4.068: 389 (20%); 6.09: 779 (40%); 93.844: 1167 (60%); 95.942: 1556 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 46.148, 49.07, 51.354, 54.61 | 46.148: 1556 (80%); 49.07: 1169 (60%); 51.354: 778 (40%); 54.61: 390 (20%) | 46.148: 389 (20%); 49.07: 779 (40%); 51.354: 1167 (60%); 54.61: 1558 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.222, 47.516, 52.794, 58.866 | 41.222: 1556 (80%); 47.516: 1167 (60%); 52.794: 778 (40%); 58.866: 389 (20%) | 41.222: 389 (20%); 47.516: 778 (40%); 52.794: 1167 (60%); 58.866: 1556 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1943 (100%) | 0: 1944 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0298, 0.0431, 0.0561, 0.0765 | 0.0298: 1557 (80%); 0.0431: 1170 (60%); 0.0561: 783 (40%); 0.0765: 396 (20%) | 0.0298: 398 (20%); 0.0431: 781 (40%); 0.0561: 1177 (61%); 0.0765: 1556 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0878, -0.059, -0.0434, -0.0326 | -0.0878: 1557 (80%); -0.059: 1172 (60%); -0.0434: 779 (40%); -0.0326: 392 (20%) | -0.0878: 390 (20%); -0.059: 784 (40%); -0.0434: 1167 (60%); -0.0326: 1567 (81%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 1945 (100%); 2: 434 (22%) | 0: 1299 (67%); 2: 1629 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 28, 42, 56, 68 | 28: 1568 (81%); 42: 1187 (61%); 56: 823 (42%); 68: 420 (22%) | 28: 409 (21%); 42: 782 (40%); 56: 1164 (60%); 68: 1568 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.7% | 0.0123, 0.0178, 0.026, 0.0407 | 0.0123: 1539 (79%); 0.0178: 1150 (59%); 0.026: 767 (39%); 0.0407: 384 (20%) | 0.0123: 380 (20%); 0.0178: 769 (40%); 0.026: 1152 (59%); 0.0407: 1535 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.3033, 0.4266, 0.5939, 0.7285 | 0.3033: 1556 (80%); 0.4266: 1169 (60%); 0.5939: 778 (40%); 0.7285: 390 (20%) | 0.3033: 390 (20%); 0.4266: 779 (40%); 0.5939: 1167 (60%); 0.7285: 1556 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 53.78, 87.96, 118.2, 164.72 | 53.78: 1556 (80%); 87.96: 1167 (60%); 118.2: 779 (40%); 164.72: 389 (20%) | 53.78: 389 (20%); 87.96: 778 (40%); 118.2: 1168 (60%); 164.72: 1556 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -2.0655, -0.4445, 0.6585, 2.7804 | -2.0655: 1556 (80%); -0.4445: 1167 (60%); 0.6585: 778 (40%); 2.7804: 389 (20%) | -2.0655: 389 (20%); -0.4445: 778 (40%); 0.6585: 1167 (60%); 2.7804: 1556 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 31.326, 46.966, 60.946, 74.876 | 31.326: 1556 (80%); 46.966: 1167 (60%); 60.946: 778 (40%); 74.876: 389 (20%) | 31.326: 389 (20%); 46.966: 778 (40%); 60.946: 1167 (60%); 74.876: 1556 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 31.262, 45.88, 59.568, 74.03 | 31.262: 1556 (80%); 45.88: 1168 (60%); 59.568: 778 (40%); 74.03: 390 (20%) | 31.262: 389 (20%); 45.88: 779 (40%); 59.568: 1167 (60%); 74.03: 1557 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 7.116, 33.536, 65.578, 93.554 | 7.116: 1556 (80%); 33.536: 1167 (60%); 65.578: 778 (40%); 93.554: 389 (20%) | 7.116: 389 (20%); 33.536: 778 (40%); 65.578: 1167 (60%); 93.554: 1556 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 16.358, 74.65, 100 | 0: 1945 (100%); 16.358: 1167 (60%); 74.65: 778 (40%); 100: 563 (29%) | 0: 630 (32%); 16.358: 778 (40%); 74.65: 1167 (60%); 100: 1945 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 14, 17 | 4: 1579 (81%); 9: 1200 (62%); 14: 785 (40%); 17: 540 (28%) | 4: 446 (23%); 9: 820 (42%); 14: 1225 (63%); 17: 1564 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 13, 18 | 5: 1568 (81%); 8: 1216 (63%); 13: 815 (42%); 18: 457 (23%) | 5: 510 (26%); 8: 811 (42%); 13: 1197 (62%); 18: 1566 (81%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 44.074, 48.952, 53.13, 58.112 | 44.074: 1556 (80%); 48.952: 1167 (60%); 53.13: 779 (40%); 58.112: 389 (20%) | 44.074: 389 (20%); 48.952: 778 (40%); 53.13: 1168 (60%); 58.112: 1556 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1587, 0.369, 0.6429, 0.8294 | 0.1587: 1558 (80%); 0.369: 1170 (60%); 0.6429: 782 (40%); 0.8294: 390 (20%) | 0.1587: 397 (20%); 0.369: 784 (40%); 0.6429: 1173 (60%); 0.8294: 1567 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.79, 17.03, 19.49, 24.17 | 14.79: 1557 (80%); 17.03: 1173 (60%); 19.49: 780 (40%); 24.17: 393 (20%) | 14.79: 397 (20%); 17.03: 780 (40%); 19.49: 1170 (60%); 24.17: 1565 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.79, 17.03, 19.49, 24.17 | 14.79: 1557 (80%); 17.03: 1173 (60%); 19.49: 780 (40%); 24.17: 393 (20%) | 14.79: 397 (20%); 17.03: 780 (40%); 19.49: 1170 (60%); 24.17: 1565 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8536, 0.8867, 0.9181, 0.962 | 0.8536: 1556 (80%); 0.8867: 1179 (61%); 0.9181: 786 (40%); 0.962: 389 (20%) | 0.8536: 390 (20%); 0.8867: 785 (40%); 0.9181: 1167 (60%); 0.962: 1556 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.69, 0.85, 0.98, 1.192 | 0.69: 1581 (81%); 0.85: 1179 (61%); 0.98: 796 (41%); 1.192: 389 (20%) | 0.69: 397 (20%); 0.85: 800 (41%); 0.98: 1178 (61%); 1.192: 1556 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0205, 0.0433, 0.0725, 0.1197 | 0.0205: 1556 (80%); 0.0433: 1167 (60%); 0.0725: 779 (40%); 0.1197: 390 (20%) | 0.0205: 391 (20%); 0.0433: 780 (40%); 0.0725: 1167 (60%); 0.1197: 1557 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 44.2569, 76.0304, 118.2228, 201.5213 | 44.2569: 1556 (80%); 76.0304: 1167 (60%); 118.2228: 778 (40%); 201.5213: 389 (20%) | 44.2569: 389 (20%); 76.0304: 778 (40%); 118.2228: 1167 (60%); 201.5213: 1556 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 42.3457, 72.7634, 114.5795, 195.0128 | 42.3457: 1556 (80%); 72.7634: 1167 (60%); 114.5795: 778 (40%); 195.0128: 389 (20%) | 42.3457: 389 (20%); 72.7634: 778 (40%); 114.5795: 1167 (60%); 195.0128: 1556 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.0205, 69.5921, 110.686, 186.8445 | 41.0205: 1556 (80%); 69.5921: 1167 (60%); 110.686: 778 (40%); 186.8445: 389 (20%) | 41.0205: 389 (20%); 69.5921: 778 (40%); 110.686: 1167 (60%); 186.8445: 1556 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 45.8013, 78.8845, 122.2474, 206.4765 | 45.8013: 1556 (80%); 78.8845: 1167 (60%); 122.2474: 778 (40%); 206.4765: 389 (20%) | 45.8013: 389 (20%); 78.8845: 778 (40%); 122.2474: 1167 (60%); 206.4765: 1556 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 47.8099, 81.0891, 127.0544, 215.4886 | 47.8099: 1556 (80%); 81.0891: 1167 (60%); 127.0544: 778 (40%); 215.4886: 389 (20%) | 47.8099: 389 (20%); 81.0891: 778 (40%); 127.0544: 1167 (60%); 215.4886: 1556 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1945 (100%) | 0: 1739 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1945 (100%) | 0: 1769 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0462, -0.0125, 0.0134, 0.0484 | -0.0462: 1556 (80%); -0.0125: 1168 (60%); 0.0134: 778 (40%); 0.0484: 391 (20%) | -0.0462: 390 (20%); -0.0125: 779 (40%); 0.0134: 1167 (60%); 0.0484: 1556 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -82.962, -58.59, -40.468, -14.548 | -82.962: 1556 (80%); -58.59: 1167 (60%); -40.468: 778 (40%); -14.548: 389 (20%) | -82.962: 389 (20%); -58.59: 778 (40%); -40.468: 1167 (60%); -14.548: 1556 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.5% | 0.5659, 0.8514, 1.0552, 1.3392 | 0.5659: 1549 (80%); 0.8514: 1162 (60%); 1.0552: 776 (40%); 1.3392: 388 (20%) | 0.5659: 388 (20%); 0.8514: 775 (40%); 1.0552: 1162 (60%); 1.3392: 1549 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.5% | 3, 5, 7, 9 | 3: 1627 (84%); 5: 1298 (67%); 7: 932 (48%); 9: 508 (26%) | 3: 467 (24%); 5: 817 (42%); 7: 1194 (61%); 9: 1675 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.3% | 0.187, 0.225, 0.2774, 0.3656 | 0.187: 1547 (80%); 0.225: 1159 (60%); 0.2774: 773 (40%); 0.3656: 387 (20%) | 0.187: 387 (20%); 0.225: 773 (40%); 0.2774: 1159 (60%); 0.3656: 1546 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 1603 (82%); 5: 1297 (67%); 7: 928 (48%); 9: 524 (27%) | 3: 492 (25%); 5: 802 (41%); 7: 1200 (62%); 9: 1627 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.6% | 0.0225, 0.031, 0.0424, 0.063 | 0.0225: 1555 (80%); 0.031: 1163 (60%); 0.0424: 775 (40%); 0.063: 390 (20%) | 0.0225: 389 (20%); 0.031: 780 (40%); 0.0424: 1163 (60%); 0.063: 1550 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 1600 (82%); 5: 1279 (66%); 7: 919 (47%); 9: 531 (27%) | 3: 481 (25%); 5: 846 (43%); 7: 1206 (62%); 9: 1646 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.7% | -0.1813, -0.0451, 0.0587, 0.2191 | -0.1813: 1551 (80%); -0.0451: 1164 (60%); 0.0587: 776 (40%); 0.2191: 388 (20%) | -0.1813: 388 (20%); -0.0451: 776 (40%); 0.0587: 1163 (60%); 0.2191: 1551 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.7% | 2, 4, 6, 8 | 2: 1704 (88%); 4: 1307 (67%); 6: 884 (45%); 8: 524 (27%) | 2: 426 (22%); 4: 857 (44%); 6: 1242 (64%); 8: 1601 (82%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.4% |
| 8k_item_5_02_filed_within_7d | 3.0% |
| above_avwap_20high | 37.9% |
| above_avwap_20low | 64.3% |
| above_avwap_252low | 79.2% |
| above_avwap_50low | 93.0% |
| above_cam_r3 | 36.9% |
| above_cam_r4 | 24.2% |
| above_cpr | 49.4% |
| above_pivot | 49.5% |
| above_prev_high | 36.0% |
| above_prev_high_clearance_atr_05 | 13.1% |
| above_prev_low | 61.6% |
| above_r1 | 28.2% |
| above_r2 | 15.6% |
| above_vwap | 51.1% |
| above_wood_p | 49.2% |
| ad_rising | 51.0% |
| adx_cross_up_20 | 0.1% |
| adx_di_bear | 48.9% |
| adx_di_bull | 51.1% |
| adx_strong | 12.8% |
| adx_trending | 61.0% |
| ao_cross_dn | 0.8% |
| ao_cross_up | 1.7% |
| ao_positive | 51.4% |
| ao_twin_peaks_bull | 2.0% |
| at_key_fib | 19.6% |
| at_key_fib_wide | 48.3% |
| avwap_20high_loss_recent_3d | 15.7% |
| avwap_20high_reclaim_recent_3d | 28.0% |
| avwap_20low_loss_recent_3d | 29.3% |
| avwap_20low_reclaim_recent_3d | 10.0% |
| avwap_252low_loss_recent_3d | 0.6% |
| avwap_252low_reclaim_recent_3d | 8.8% |
| avwap_50low_loss_recent_3d | 5.0% |
| avwap_50low_reclaim_recent_3d | 9.0% |
| bb_10_20_above_mid | 49.3% |
| bb_10_20_expanding | 70.2% |
| bb_10_20_pctb_gt_75 | 45.0% |
| bb_10_20_pctb_gt_8 | 41.5% |
| bb_10_20_pctb_gt_85 | 34.9% |
| bb_10_20_pctb_gt_9 | 26.2% |
| bb_10_20_pctb_gt_95 | 16.7% |
| bb_10_20_pctb_lt_05 | 17.3% |
| bb_10_20_pctb_lt_1 | 26.1% |
| bb_10_20_pctb_lt_15 | 34.3% |
| bb_10_20_pctb_lt_2 | 40.1% |
| bb_10_20_pctb_lt_25 | 42.9% |
| bb_10_20_reclaim_from_lower_recent_3d | 3.8% |
| bb_10_20_reclaim_from_upper_recent_3d | 6.2% |
| bb_10_20_squeeze | 52.9% |
| bb_10_20_touch_lower | 23.9% |
| bb_10_20_touch_upper | 18.6% |
| bb_20_15_above_mid | 50.3% |
| bb_20_15_expanding | 25.9% |
| bb_20_15_pctb_gt_75 | 20.3% |
| bb_20_15_pctb_gt_8 | 18.0% |
| bb_20_15_pctb_gt_85 | 16.0% |
| bb_20_15_pctb_gt_9 | 13.5% |
| bb_20_15_pctb_gt_95 | 11.5% |
| bb_20_15_pctb_lt_05 | 11.6% |
| bb_20_15_pctb_lt_1 | 13.4% |
| bb_20_15_pctb_lt_15 | 15.7% |
| bb_20_15_pctb_lt_2 | 17.9% |
| bb_20_15_pctb_lt_25 | 20.5% |
| bb_20_15_reclaim_from_lower_recent_3d | 3.9% |
| bb_20_15_reclaim_from_upper_recent_3d | 6.8% |
| bb_20_15_squeeze | 40.1% |
| bb_20_15_touch_lower | 13.3% |
| bb_20_15_touch_upper | 12.4% |
| bb_20_20_above_mid | 50.3% |
| bb_20_20_expanding | 25.9% |
| bb_20_20_pctb_gt_75 | 16.9% |
| bb_20_20_pctb_gt_8 | 13.5% |
| bb_20_20_pctb_gt_85 | 11.1% |
| bb_20_20_pctb_gt_9 | 8.7% |
| bb_20_20_pctb_gt_95 | 6.4% |
| bb_20_20_pctb_lt_05 | 5.9% |
| bb_20_20_pctb_lt_1 | 8.6% |
| bb_20_20_pctb_lt_15 | 11.1% |
| bb_20_20_pctb_lt_2 | 13.4% |
| bb_20_20_pctb_lt_25 | 16.6% |
| bb_20_20_reclaim_from_lower_recent_3d | 0.5% |
| bb_20_20_reclaim_from_upper_recent_3d | 0.8% |
| bb_20_20_squeeze | 23.9% |
| bb_20_20_touch_lower | 7.4% |
| bb_20_20_touch_upper | 6.5% |
| bearish_engulfing | 2.5% |
| bearish_pin_bar | 4.3% |
| below_avwap_20high | 62.1% |
| below_avwap_20low | 35.7% |
| below_avwap_252low | 20.8% |
| below_avwap_50low | 7.0% |
| below_cam_s3 | 41.1% |
| below_cam_s4 | 28.5% |
| below_cpr | 50.5% |
| below_ema_20 | 49.3% |
| below_ema_200 | 49.3% |
| below_ema_20_break_recent_5d | 34.4% |
| below_ema_21 | 49.1% |
| below_ema_21_break_recent_5d | 33.1% |
| below_ema_50 | 48.6% |
| below_ema_50_break_recent_5d | 4.4% |
| below_ema_9 | 51.0% |
| below_ema_9_break_recent_5d | 47.2% |
| below_prev_high | 63.9% |
| below_prev_low | 38.3% |
| below_prev_low_clearance_atr_05 | 17.7% |
| below_s1 | 32.7% |
| below_s2 | 18.5% |
| below_sma_20 | 49.7% |
| below_sma_200 | 49.4% |
| below_sma_21 | 49.5% |
| below_sma_50 | 49.3% |
| below_sma_9 | 50.7% |
| below_vwap | 48.9% |
| blowoff_recent_3d | 0.1% |
| bullish_engulfing | 1.9% |
| bullish_pin_bar | 4.1% |
| capitulation_recent_3d | 0.1% |
| ceo_buy | 1.2% |
| cfo_buy | 0.6% |
| chandelier_long_bullish | 65.6% |
| chandelier_long_flip_dn | 8.8% |
| chandelier_short_bearish | 60.9% |
| chandelier_short_flip_up | 8.6% |
| classification_change_from_tech | 57.1% |
| classification_change_to_defensive | 42.9% |
| close_above_open | 42.9% |
| close_below_open | 56.3% |
| close_in_bottom_40pct_of_range | 45.5% |
| close_in_top_40pct_of_range | 38.6% |
| cluster_buy | 0.6% |
| cmf_cross_dn | 6.5% |
| cmf_cross_up | 5.6% |
| cmf_negative | 41.4% |
| cmf_positive | 58.5% |
| concentrated_sell | 5.7% |
| cpr_narrow | 89.1% |
| cpr_narrow_tight | 27.2% |
| cup_handle_detected | 15.7% |
| cup_handle_neckline_break_retest_long | 2.7% |
| dc10_breakout_dn | 20.8% |
| dc10_breakout_dn_1pct | 31.0% |
| dc10_breakout_up | 21.1% |
| dc10_breakout_up_1pct | 29.9% |
| dc10_new_high | 26.9% |
| dc10_strong_breakout_dn | 5.3% |
| dc10_strong_breakout_up | 4.3% |
| dc20_breakout_dn | 3.2% |
| dc20_breakout_up | 3.8% |
| dc20_new_high | 6.0% |
| dc20_resistance_break_retest_strong | 4.9% |
| dc20_support_break_retest_strong | 4.0% |
| defensive_leadership | 55.9% |
| director_only_buy | 3.3% |
| doji | 4.4% |
| double_bottom_detected | 8.9% |
| double_top_detected | 11.7% |
| dpi_elevated | 54.6% |
| drying_volume_on_down_turn | 32.3% |
| drying_volume_on_up_turn | 29.4% |
| ema_20_50_bearish | 49.3% |
| ema_20_50_bullish | 50.7% |
| ema_50_200_bearish | 49.5% |
| ema_50_200_bullish | 50.5% |
| ema_50_200_death_cross | 0.1% |
| ema_50_200_golden_cross | 0.2% |
| ema_9_21_bearish | 48.4% |
| ema_9_21_bullish | 51.6% |
| ema_9_21_death_cross | 1.9% |
| ema_9_21_golden_cross | 2.5% |
| evening_star | 5.1% |
| flag_bear_break_retest_short | 0.2% |
| flag_bear_broke | 0.3% |
| flag_bear_detected | 0.9% |
| flag_bull_break_retest_long | 0.7% |
| flag_bull_broke | 0.7% |
| flag_bull_detected | 2.9% |
| force_index_cross_dn | 14.9% |
| force_index_cross_up | 9.6% |
| force_index_positive | 50.0% |
| gap_dn_1_5pct | 5.4% |
| gap_dn_2pct | 2.9% |
| gap_up_1_5pct | 9.8% |
| gap_up_2pct | 6.5% |
| hammer | 3.7% |
| head_shoulders_bottom_detected | 2.3% |
| head_shoulders_top_detected | 2.4% |
| house_cluster_buy | 3.9% |
| house_cluster_sell | 4.6% |
| htf_aligned_bear | 39.1% |
| htf_aligned_bull | 40.5% |
| htf_disagreement | 0.8% |
| hull_bearish | 49.3% |
| hull_bullish | 50.7% |
| hull_flip_dn | 13.0% |
| hull_flip_up | 8.8% |
| ichi_above_cloud | 48.5% |
| ichi_above_cloud_break_recent_5d | 0.1% |
| ichi_below_cloud | 47.2% |
| ichi_below_cloud_break_recent_5d | 0.3% |
| ichi_cloud_thick | 86.1% |
| ichi_tk_bearish | 46.9% |
| ichi_tk_bullish | 51.5% |
| ichi_tk_cross_dn | 1.6% |
| ichi_tk_cross_up | 2.2% |
| ichi_weekly_above_cloud | 38.8% |
| ichi_weekly_below_cloud | 31.9% |
| ichi_weekly_in_cloud | 29.2% |
| in_reversal_window | 1.2% |
| inside_bar | 5.4% |
| inside_cpr | 0.5% |
| inside_kc | 99.3% |
| insider_cluster_active | 29.1% |
| institutional_buy | 90.8% |
| institutional_negative | 3.7% |
| institutional_persistence_growing | 45.6% |
| institutional_persistence_strong | 62.2% |
| institutional_strong_buy | 81.1% |
| inverted_cup_handle_detected | 9.8% |
| is_friday | 20.9% |
| is_halloween_period | 51.7% |
| is_halloween_period_first_day | 0.4% |
| is_january | 11.1% |
| is_january_extended | 13.1% |
| is_monday | 16.8% |
| is_pre_holiday | 4.7% |
| is_summer_period | 48.3% |
| is_totm_window | 38.2% |
| is_totm_window_first_day | 11.6% |
| is_week_open | 19.9% |
| kc_touch_lower | 0.7% |
| kc_touch_upper | 0.6% |
| large_dollar_buy | 1.3% |
| macd_12_26_9_bearish | 49.7% |
| macd_12_26_9_bullish | 50.3% |
| macd_12_26_9_crossover_dn | 7.3% |
| macd_12_26_9_crossover_up | 6.3% |
| macd_8_21_5_bearish | 50.6% |
| macd_8_21_5_bullish | 49.4% |
| macd_8_21_5_crossover_dn | 3.8% |
| macd_8_21_5_crossover_up | 2.3% |
| marubozu_bear | 1.2% |
| marubozu_bull | 1.0% |
| mfi_broad_overbought | 7.6% |
| mfi_broad_oversold | 4.3% |
| mfi_overbought | 1.0% |
| mfi_oversold | 0.6% |
| monthly_above_sma_12 | 50.2% |
| monthly_above_sma_6 | 49.9% |
| monthly_bias_bear | 44.9% |
| monthly_bias_bull | 45.0% |
| monthly_momentum_pos | 50.0% |
| morning_star | 3.4% |
| near_52w_high | 0.4% |
| near_52w_high_95pct | 10.4% |
| near_52w_high_retest_long | 0.1% |
| near_52w_low_105pct | 1.1% |
| near_52w_low_retest_short | 0.4% |
| near_avwap_20high_atr_05x | 19.0% |
| near_avwap_20high_atr_10x | 52.5% |
| near_avwap_20high_atr_15x | 83.0% |
| near_avwap_20high_atr_20x | 96.3% |
| near_avwap_20low_atr_05x | 22.2% |
| near_avwap_20low_atr_10x | 50.0% |
| near_avwap_20low_atr_15x | 78.4% |
| near_avwap_20low_atr_20x | 93.1% |
| near_avwap_252low_atr_05x | 8.3% |
| near_avwap_252low_atr_10x | 18.9% |
| near_avwap_252low_atr_15x | 35.1% |
| near_avwap_252low_atr_20x | 47.7% |
| near_avwap_50low_atr_05x | 14.4% |
| near_avwap_50low_atr_10x | 33.6% |
| near_avwap_50low_atr_15x | 59.9% |
| near_avwap_50low_atr_20x | 77.7% |
| near_cam_r3 | 12.9% |
| near_cam_s3 | 12.3% |
| near_cam_s4 | 11.7% |
| near_fib_236 | 8.3% |
| near_fib_382 | 7.0% |
| near_fib_500 | 5.6% |
| near_fib_618 | 7.0% |
| near_fib_786 | 3.8% |
| near_pivot | 4.5% |
| near_prev_close | 9.6% |
| near_prev_high | 10.5% |
| near_prev_low | 11.4% |
| near_r1 | 11.8% |
| near_r1_wide | 45.0% |
| near_r2 | 6.2% |
| near_r2_wide | 31.2% |
| near_s1 | 12.7% |
| near_s1_wide | 44.3% |
| near_s2 | 7.8% |
| near_s2_wide | 37.0% |
| near_s3 | 4.7% |
| near_wood_r1 | 6.0% |
| near_wood_s1 | 6.4% |
| news_uses_polygon_score | 21.0% |
| obv_bearish | 46.1% |
| obv_bullish | 53.9% |
| obv_diverge_bull | 1.4% |
| obv_falling | 50.5% |
| obv_rising | 49.5% |
| outside_bar | 5.9% |
| pead_negative_surprise | 16.9% |
| pead_positive_surprise | 24.8% |
| pin_bar | 8.4% |
| po3_accumulation_active | 46.1% |
| po3_bearish | 7.8% |
| po3_bullish | 4.8% |
| po3_manipulation_sweep_down | 30.2% |
| po3_manipulation_sweep_up | 13.1% |
| po3_mmbm_setup | 0.3% |
| po3_mmsm_setup | 0.7% |
| po3_sweep_above_prior_high | 51.5% |
| po3_sweep_below_prior_low | 52.3% |
| ppo_bullish | 48.7% |
| ppo_crossover_dn | 6.6% |
| ppo_crossover_up | 6.6% |
| pre_fomc_d0 | 2.0% |
| pre_fomc_d1 | 1.4% |
| pre_fomc_window | 3.4% |
| price_above_dema | 49.4% |
| price_above_ema_20 | 50.7% |
| price_above_ema_200 | 50.7% |
| price_above_ema_20_break_recent_5d | 34.1% |
| price_above_ema_21 | 50.9% |
| price_above_ema_21_break_recent_5d | 32.9% |
| price_above_ema_50 | 51.4% |
| price_above_ema_50_break_recent_5d | 5.1% |
| price_above_ema_9 | 49.0% |
| price_above_ema_9_break_recent_5d | 43.4% |
| price_above_hull | 49.3% |
| price_above_sma_200 | 50.6% |
| price_above_sma_21 | 50.5% |
| price_above_sma_50 | 50.7% |
| price_above_tema | 49.2% |
| price_below_dema | 50.6% |
| price_below_hull | 50.7% |
| price_below_tema | 50.8% |
| psar_bullish | 51.2% |
| psar_flip_dn | 10.8% |
| psar_flip_up | 8.5% |
| r1_break_retest_long | 48.1% |
| resistance_break_retest | 6.9% |
| risk_off_regime_bond_signal | 22.8% |
| risk_off_regime_bond_signal_strong | 4.6% |
| risk_off_regime_gold_signal | 41.1% |
| risk_on_regime_bond_signal | 45.3% |
| risk_on_regime_bond_signal_strong | 19.5% |
| roc_positive | 51.1% |
| roc_turning_dn | 13.7% |
| roc_turning_up | 9.6% |
| rsi_14_bullish | 52.0% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.9% |
| rsi_14_cross_dn_overbought_recent_3d | 11.0% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_14_cross_up_oversold_recent_3d | 4.9% |
| rsi_14_extreme_os | 0.2% |
| rsi_14_overbought | 0.1% |
| rsi_14_oversold | 0.3% |
| rsi_14_rising | 49.0% |
| rsi_21_bullish | 52.5% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_21_cross_dn_overbought_recent_3d | 5.1% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 2.1% |
| rsi_21_extreme_os | 0.2% |
| rsi_21_overbought | 0.1% |
| rsi_21_oversold | 0.3% |
| rsi_21_rising | 49.0% |
| rsi_2_bullish | 49.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 12.2% |
| rsi_2_cross_dn_overbought_recent_3d | 16.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 5.9% |
| rsi_2_cross_up_oversold_recent_3d | 9.0% |
| rsi_2_extreme_ob | 49.3% |
| rsi_2_extreme_os | 50.6% |
| rsi_2_overbought | 49.3% |
| rsi_2_oversold | 50.6% |
| rsi_2_rising | 49.0% |
| rsi_9_bullish | 50.6% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 3.1% |
| rsi_9_cross_dn_overbought_recent_3d | 15.3% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.8% |
| rsi_9_cross_up_oversold_recent_3d | 8.1% |
| rsi_9_extreme_os | 0.2% |
| rsi_9_overbought | 1.1% |
| rsi_9_oversold | 1.2% |
| rsi_9_rising | 49.0% |
| s1_break_retest_short | 43.5% |
| sc_13d_filed_within_30d | 2.7% |
| sc_13g_filed_within_30d | 3.3% |
| sector_outperforming_spy | 42.3% |
| sector_underperforming_spy | 57.7% |
| shooting_star | 3.1% |
| sma_20_50_bullish | 51.0% |
| sma_20_50_golden_cross | 0.2% |
| sma_50_200_bullish | 49.8% |
| sma_50_200_golden_cross | 0.5% |
| sma_9_21_bullish | 52.1% |
| sma_9_21_golden_cross | 2.8% |
| smc_bos_bearish | 14.7% |
| smc_bos_bullish | 14.7% |
| smc_bos_retest_long | 4.7% |
| smc_bos_retest_short | 5.4% |
| smc_breaker_block_bearish | 17.7% |
| smc_breaker_block_bullish | 19.7% |
| smc_choch_bearish | 5.7% |
| smc_choch_bullish | 5.4% |
| smc_equal_highs_swept | 4.8% |
| smc_equal_lows_swept | 4.4% |
| smc_fvg_bearish_active | 36.6% |
| smc_fvg_bullish_active | 42.3% |
| smc_fvg_retest_long_zone | 9.1% |
| smc_fvg_retest_short_zone | 7.0% |
| smc_in_discount_zone | 61.1% |
| smc_in_premium_zone | 64.4% |
| smc_inverse_fvg_bearish | 93.4% |
| smc_inverse_fvg_bullish | 93.4% |
| smc_liquidity_swept_dn | 1.1% |
| smc_liquidity_swept_up | 1.0% |
| smc_mitigation_block_long | 0.3% |
| smc_mitigation_block_short | 0.6% |
| smc_ob_bearish_active | 39.6% |
| smc_ob_bullish_active | 36.4% |
| smc_ote_long_zone | 6.6% |
| smc_ote_short_zone | 6.5% |
| squeeze_fire_dn | 9.0% |
| squeeze_fire_up | 7.9% |
| squeeze_in | 22.0% |
| squeeze_positive | 51.5% |
| stoch_bearish_cross | 1.9% |
| stoch_broad_overbought | 19.0% |
| stoch_broad_oversold | 13.0% |
| stoch_bullish_cross | 1.5% |
| stoch_overbought | 13.7% |
| stoch_oversold | 8.2% |
| stochrsi_cross_dn | 12.2% |
| stochrsi_cross_up | 13.5% |
| stochrsi_overbought | 38.4% |
| stochrsi_oversold | 41.4% |
| supertrend_bearish | 1.0% |
| supertrend_bullish | 99.0% |
| supertrend_flip_dn | 0.8% |
| supertrend_flip_recent_long_5d | 1.2% |
| supertrend_flip_recent_short_5d | 0.9% |
| supertrend_flip_up | 0.3% |
| support_break_retest | 5.1% |
| tema_above_dema | 51.5% |
| tema_cross_dn | 6.5% |
| tema_cross_up | 6.4% |
| three_black_crows | 18.4% |
| three_white_soldiers | 14.9% |
| triangle_apex_break_retest_long | 7.8% |
| triangle_ascending_detected | 7.1% |
| triangle_descending_detected | 5.1% |
| uo_overbought | 0.6% |
| uo_oversold | 0.7% |
| usd_strengthening | 24.7% |
| usd_weakening | 11.0% |
| vix_band_high | 38.0% |
| vix_band_low | 35.4% |
| vix_band_mid | 26.6% |
| vix_term_backwardation | 5.4% |
| vix_term_contango | 94.6% |
| vol_above_avg | 37.7% |
| vol_below_avg | 62.3% |
| vol_spike_12x | 19.8% |
| vol_spike_15x | 7.7% |
| vol_spike_17x | 4.5% |
| vol_spike_2x | 3.2% |
| vol_spike_2x_on_down_day_recent_3d | 2.4% |
| vol_spike_2x_on_up_day_recent_3d | 2.0% |
| vol_spike_3x | 0.5% |
| vp_above_value_area | 19.2% |
| vp_below_value_area | 9.5% |
| vp_close_above_poc | 56.3% |
| vp_close_below_poc | 43.7% |
| vp_in_value_area | 71.3% |
| week_open_gap_down_15pct | 1.5% |
| week_open_gap_up_15pct | 1.8% |
| weekly_above_ema_10 | 51.8% |
| weekly_above_ema_20 | 51.1% |
| weekly_bias_bear | 43.0% |
| weekly_bias_bull | 45.9% |
| weekly_momentum_pos | 50.2% |
| williams_r_overbought | 24.4% |
| williams_r_oversold | 22.9% |
| williams_r_rising | 46.9% |
| within_pead_window | 38.8% |
| within_post_deletion_window | 5.1% |
| within_post_inclusion_window | 2.3% |
| within_pre_rebalance_window | 1.5% |
| xs_avoid_high_ivol | 72.9% |
| xs_avoid_high_max | 72.6% |
| xs_high_beta_decile | 26.2% |
| xs_low_beta_bottom_quintile | 26.2% |
| xs_low_beta_decile | 16.0% |
| xs_low_beta_decile_entry_recent_5d | 0.3% |
| xs_low_beta_top_quintile | 16.0% |
| xs_momentum_bottom_decile | 12.1% |
| xs_momentum_bottom_quintile | 22.0% |
| xs_momentum_top_decile | 8.5% |
| xs_momentum_top_quintile | 17.4% |
| xs_quality_bottom_quintile | 22.3% |
| xs_quality_top_quintile | 21.4% |
| xs_quality_top_tercile | 40.4% |
| year_high_break_retest_long | 0.6% |
| year_low_break_retest_short | 0.5% |
| yoy_surprise_high | 51.4% |
| yoy_surprise_negative | 38.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.8% |
| committed_growth_holders | 91.8% |
| corp_donations_1y | 7.6% |
| corp_donations_count_1y | 7.6% |
| corp_donations_unique_pacs | 7.6% |
| cot_rut_commercials_pctile_3y | 52.2% |
| cot_rut_mmoney_pctile_3y | 52.2% |
| cup_handle_depth_pct | 21.5% |
| days_since_classification_change | 0.4% |
| days_since_deletion | 7.1% |
| days_since_inclusion | 13.3% |
| days_to_next_holiday | 62.0% |
| days_to_rebalance | 10.4% |
| dpi_30d_avg | 96.1% |
| dpi_recent | 96.1% |
| earnings_announcement_return | 91.7% |
| earnings_eps_yoy_growth | 95.0% |
| flag_bear_pole_move_pct | 0.9% |
| flag_bull_pole_move_pct | 2.9% |
| gov_contracts_4q_sum | 39.8% |
| gov_contracts_last_qtr_amount | 39.8% |
| gov_contracts_qoq_growth | 39.8% |
| head_shoulders_magnitude_pct | 4.7% |
| insider_director_buyers_30d | 5.7% |
| insider_officer_buyers_30d | 5.7% |
| insider_total_shares_bought_30d | 5.7% |
| insider_unique_buyers_30d | 5.7% |
| inverted_cup_handle_height_pct | 14.7% |
| lobbying_amount_1y | 68.9% |
| lobbying_amount_q | 68.9% |
| lobbying_amount_yoy | 68.9% |
| otc_short_ratio_recent | 96.1% |
| otc_volume_recent | 96.1% |
| pair_half_life | 93.1% |
| pair_max_abs_zscore | 93.1% |
| pair_zscore_signed | 93.1% |
| pct_from_avwap_20high | 93.0% |
| pct_from_avwap_20low | 93.5% |
| persistent_holders_4q | 91.8% |
| persistent_holders_8q | 91.8% |
| sc_13g_latest_percent_owned | 1.7% |
| search_volume_index_recent | 77.3% |
| search_volume_observations | 77.3% |
| search_volume_zscore_30d | 77.3% |
| sector_etf_return_20d | 2.7% |
| spy_return_20d | 2.7% |
| total_active_holders | 91.8% |
| triangle_breakdown_pct | 5.1% |
| triangle_breakout_pct | 7.1% |
| xs_quality_decile | 60.8% |
| xs_quality_gross_profitability | 60.8% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.996), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.997), `double_top_neckline` (0.995), `double_top_peak` (0.995), `entry_stop_long` (0.999), `entry_stop_short` (0.999), `fib_236` (0.992), `fib_382` (0.994), `fib_500` (0.995), `fib_618` (0.996), `fib_786` (0.996), `fib_ext_127` (0.986), `fib_ext_162` (0.982), `flag_bear_breakdown_level` (0.998), `flag_bull_breakout_level` (0.999), `head_shoulders_bottom_neckline` (0.996), `head_shoulders_top_neckline` (0.996), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.989), `ichi_senkou_b` (0.983), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.999), `monthly_sma_12` (0.977), `monthly_sma_6` (0.991), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.997), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.999), `swing_high` (0.989), `swing_low` (0.995), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.993), `vp_value_area_high` (0.993), `vp_value_area_low` (0.993), `weekly_close` (0.999), `weekly_ema_10` (0.998), `weekly_ema_20` (0.993), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.961), `year_low` (0.974)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 8 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 7 |
| P2.1 | sma span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P3.1 | ema span (the 200 in above/below_ema_200 | 8 | **FIRE-ADDING** | shares env STRAT_EMA_SPAN with P1.1 - ONE knob, counted once | - | - | - |
| P4.1 | sma span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P5.1 | rsi span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P6.1 | rsi (fast escape-hatch) span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P7 | OR-composite (rsi_2 < 7 OR rsi_14 < 40) | 1 | **FIRE-ADDING** | **YES** | 1 | 0 | 0 |
| P8 | OR-composite (rsi_2 > 93 OR rsi_14 > 60) | 1 | **FIRE-ADDING** | **YES** | 1 | 0 | 0 |
| P9 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     8 x 3 x 3 x 3 x 3 x 1 x 1 x 1 = 648
offline gradings   0 level-combinations x 24 exits = 0 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  647 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 0 + 647 = 648 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 645 census axes join it only when REGISTERED at the T3 band review.
