# Table A - dc20_break_retest

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 1a2cbcbec | commit 1a2cbcbec at 2026-10-26 23:50:03 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** breakout | **status:** NOT-STARTED | **R5 fires:** 2414 (closed fires in the exit cube: 2414 of 2414, S6-B3258) | **surviving fires (T1):** 1193 (survives_pct 0.4942)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  close_in_bottom_40pct_of_range  <- backtest/signals/technical.py
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P1.1-P1.1 (band rows in Table A)
P2  close_in_top_40pct_of_range  <- backtest/signals/technical.py
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P2.1-P2.1 (band rows in Table A)
P3  resistance_break_retest  <- backtest/signals/technical.py
       DEFN: a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals)
       knobs P3.1-P3.3 (band rows in Table A)
P4  support_break_retest  <- backtest/signals/technical.py
       DEFN: a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals)
       knobs P4.1-P4.1 (band rows in Table A)
P5  vol_below_avg  <- backtest/signals/technical.py
       DEFN: volume / 20d average < 1.0 (technical.py compute_volume)
       knobs P5.1-P5.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P6  ppo_hist >= -0.2513   [EXISTING-THRESHOLD]
P7  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_dc20_break_retest (docstring and return dropped):

```python
fl = s.get('resistance_break_retest') and s.get('vol_below_avg') and s.get('close_in_top_40pct_of_range')
fl = fl and s.get('ppo_hist', float('-inf')) >= -0.2513
fs = s.get('support_break_retest') and s.get('vol_below_avg') and s.get('close_in_bottom_40pct_of_range') and (not _short_borrow_trap_active(s))
fs = fs and s.get('ppo_hist', float('-inf')) >= -0.2513
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
| P1 | PRODUCER | close_in_bottom_40pct_of_range - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | mirror of top_40pct - backtest/signals/technical.py:1682 region | mirror | 0.4 | [0.25, 0.40, 0.50] | offline 0 of 3 levels - none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | close_in_top_40pct_of_range - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | range-position cutoff - backtest/signals/technical.py:1682 | BRACKET production 0.40 | 0.4 | [0.25, 0.40, 0.50] | offline 0 of 3 levels - none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | resistance_break_retest - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | breakout clearance - the breakout bar closed beyond the level by c x ATR(14) - backtest/signals/technical.py compute_break_retest_signals | BRACKET production; 0.5 is the shipped B594 strong variant | 0.0 | 0, 0.5, 1 | offline 1 of 3 levels - TIGHTER (0.5) - the persisted dc20_resistance_break_retest_strong, set only inside the same hold check, so a subset of the leg: True on 599 of 862 dc20_break_retest and 532 of 765 break_retest_volume R5 long fires | 1.0 - tighter but unpersisted, engine-only; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3.2 | BAND | retest tolerance - a later bar's low within t x ATR(14) of the level - backtest/signals/technical.py compute_break_retest_signals | BRACKET production | 1.5 | 1, 1.5, 2 | offline 0 of 3 levels - none - the post-break bars are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3.3 | BAND | breakout window - lag 2 to N bars ago, and the close-based lookback that sets the level - backtest/signals/technical.py compute_break_retest_signals | BRACKET production | lag 2-8 / lookback 20 | lag max [5, 8, 12]; lookback [10, 20, 50] | offline 0 of 3, 0 of 3 levels - none - the earlier bars are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | support_break_retest - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | mirror of resistance_break_retest (the close-based low; the same clearance, tolerance and window) - backtest/signals/technical.py compute_break_retest_signals | mirror | as resistance_break_retest | as long, mirrored | counted on the mirrored leg - TIGHTER clearance 0.5 - the persisted dc20_support_break_retest_strong: True on 1121 of 1552 dc20_break_retest and 1009 of 1399 break_retest_volume R5 short fires | the rest - mirrored; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | PRODUCER | vol_below_avg - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average < 1.0 (technical.py compute_volume) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | volume ratio ceiling (vol / avg, strict <) - backtest/signals/technical.py compute_volume | MEASURED - production 1.0 (B594, the retest dry-up); levels near the R5 fires' vol_ratio_20d (q20 0.65, q60 0.83 on both consumers); avg window is the second knob [10, 20, 50] | 1.0 | 0.6, 0.8, 1 | offline 2 of 3 levels - TIGHTER ceilings (0.8, 0.6) on the persisted vol_ratio_20d, which is rounded to 2 dp - a level is blurred by 0.005 either way (the rounding already reads 1.00 on 23 of 2414 and 22 of 2164 R5 fires the strict production gate admitted) | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | STRATEGY | ppo_hist `>= -0.2513` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= -0.2513` | production + 4 tighter measured levels | offline 4 of 5 levels - measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P7 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| ppo_hist | backtest/signals/technical.py | `>= -0.2513` | 100.0% | TIGHTER = RAISE the floor: -0.0537 -> 955 (80%); 0.3121 -> 716 (60%); 0.7076 -> 477 (40%); 1.1198 -> 239 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 17.408, 21.08, 25.104, 31.326 | 17.408: 954 (80%); 21.08: 717 (60%); 25.104: 477 (40%); 31.326: 239 (20%) | 17.408: 239 (20%); 21.08: 478 (40%); 25.104: 716 (60%); 31.326: 954 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 16.03, 19.18, 22.486, 26.266 | 16.03: 955 (80%); 19.18: 717 (60%); 22.486: 477 (40%); 26.266: 239 (20%) | 16.03: 242 (20%); 19.18: 479 (40%); 22.486: 716 (60%); 26.266: 954 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.088, 23.84, 27.34, 31.208 | 18.088: 954 (80%); 23.84: 717 (60%); 27.34: 478 (40%); 31.208: 239 (20%) | 18.088: 239 (20%); 23.84: 479 (40%); 27.34: 717 (60%); 31.208: 954 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -3.3441, 0.6098, 2.4709, 6.1518 | -3.3441: 954 (80%); 0.6098: 716 (60%); 2.4709: 477 (40%); 6.1518: 239 (20%) | -3.3441: 239 (20%); 0.6098: 477 (40%); 2.4709: 716 (60%); 6.1518: 954 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.0174, 1.7906, 3.029, 5.3686 | 1.0174: 954 (80%); 1.7906: 716 (60%); 3.029: 477 (40%); 5.3686: 239 (20%) | 1.0174: 239 (20%); 1.7906: 477 (40%); 3.029: 716 (60%); 5.3686: 954 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.0174, 1.7906, 3.029, 5.3686 | 1.0174: 954 (80%); 1.7906: 716 (60%); 3.029: 477 (40%); 5.3686: 239 (20%) | 1.0174: 239 (20%); 1.7906: 477 (40%); 3.029: 716 (60%); 5.3686: 954 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.9994, 2.4418, 2.872, 3.6568 | 1.9994: 954 (80%); 2.4418: 716 (60%); 2.872: 477 (40%); 3.6568: 239 (20%) | 1.9994: 239 (20%); 2.4418: 477 (40%); 2.872: 716 (60%); 3.6568: 954 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0521, 0.076, 0.1063, 0.1542 | 0.0521: 955 (80%); 0.076: 716 (60%); 0.1063: 479 (40%); 0.1542: 239 (20%) | 0.0521: 240 (20%); 0.076: 477 (40%); 0.1063: 716 (60%); 0.1542: 955 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.429, 0.597, 0.741, 0.847 | 0.429: 954 (80%); 0.597: 716 (60%); 0.741: 478 (40%); 0.847: 239 (20%) | 0.429: 239 (20%); 0.597: 478 (40%); 0.741: 716 (60%); 0.847: 954 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0659, 0.0881, 0.1154, 0.1524 | 0.0659: 955 (80%); 0.0881: 717 (60%); 0.1154: 478 (40%); 0.1524: 239 (20%) | 0.0659: 239 (20%); 0.0881: 479 (40%); 0.1154: 716 (60%); 0.1524: 954 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2528, 0.779, 0.9411, 1.0877 | 0.2528: 954 (80%); 0.779: 716 (60%); 0.9411: 477 (40%); 1.0877: 239 (20%) | 0.2528: 239 (20%); 0.779: 477 (40%); 0.9411: 716 (60%); 1.0877: 954 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0879, 0.1174, 0.1539, 0.2033 | 0.0879: 955 (80%); 0.1174: 717 (60%); 0.1539: 478 (40%); 0.2033: 239 (20%) | 0.0879: 239 (20%); 0.1174: 478 (40%); 0.1539: 716 (60%); 0.2033: 954 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.3146, 0.7093, 0.8309, 0.9408 | 0.3146: 954 (80%); 0.7093: 716 (60%); 0.8309: 477 (40%); 0.9408: 239 (20%) | 0.3146: 239 (20%); 0.7093: 477 (40%); 0.8309: 716 (60%); 0.9408: 954 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0549, -0.032, -0.0099, 0.0184 | -0.0549: 957 (80%); -0.032: 716 (60%); -0.0099: 479 (40%); 0.0184: 239 (20%) | -0.0549: 239 (20%); -0.032: 479 (40%); -0.0099: 717 (60%); 0.0184: 954 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.145, 0.1708, 0.2223, 0.2632 | 0.145: 955 (80%); 0.1708: 715 (60%); 0.2223: 479 (40%); 0.2632: 230 (19%) | 0.145: 238 (20%); 0.1708: 478 (40%); 0.2223: 714 (60%); 0.2632: 963 (81%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1193 (100%) | 0: 1120 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.07, 0.0294, 0.1017, 0.183 | -0.07: 954 (80%); 0.0294: 716 (60%); 0.1017: 478 (40%); 0.183: 239 (20%) | -0.07: 239 (20%); 0.0294: 477 (40%); 0.1017: 716 (60%); 0.183: 954 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1193 (100%); 1: 478 (40%) | 0: 715 (60%); 1: 981 (82%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2387, -0.1931, -0.1509, -0.1197 | -0.2387: 957 (80%); -0.1931: 724 (61%); -0.1509: 480 (40%); -0.1197: 244 (20%) | -0.2387: 245 (21%); -0.1931: 479 (40%); -0.1509: 736 (62%); -0.1197: 961 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4167, 0.6282, 0.7244, 0.7756 | 0.4167: 974 (82%); 0.6282: 721 (60%); 0.7244: 480 (40%); 0.7756: 242 (20%) | 0.4167: 240 (20%); 0.6282: 501 (42%); 0.7244: 745 (62%); 0.7756: 963 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.3846, 0.5897, 0.8333 | 0.2628: 968 (81%); 0.3846: 727 (61%); 0.5897: 492 (41%); 0.8333: 244 (20%) | 0.2628: 285 (24%); 0.3846: 483 (40%); 0.5897: 723 (61%); 0.8333: 974 (82%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0921, 0.0195, 0.1037, 0.254 | -0.0921: 957 (80%); 0.0195: 723 (61%); 0.1037: 485 (41%); 0.254: 250 (21%) | -0.0921: 246 (21%); 0.0195: 489 (41%); 0.1037: 726 (61%); 0.254: 957 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2692, 0.4872, 0.6603, 0.8462 | 0.2692: 955 (80%); 0.4872: 736 (62%); 0.6603: 485 (41%); 0.8462: 242 (20%) | 0.2692: 253 (21%); 0.4872: 479 (40%); 0.6603: 720 (60%); 0.8462: 965 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.109, 0.25, 0.4487, 0.6218 | 0.109: 961 (81%); 0.25: 732 (61%); 0.4487: 482 (40%); 0.6218: 242 (20%) | 0.109: 240 (20%); 0.25: 496 (42%); 0.4487: 725 (61%); 0.6218: 977 (82%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.531, -0.4339, -0.2179, 0.0432 | -0.531: 961 (81%); -0.4339: 720 (60%); -0.2179: 493 (41%); 0.0432: 245 (21%) | -0.531: 250 (21%); -0.4339: 478 (40%); -0.2179: 719 (60%); 0.0432: 957 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2847, 0.4679, 0.609, 0.9167 | 0.2847: 954 (80%); 0.4679: 729 (61%); 0.609: 487 (41%); 0.9167: 247 (21%) | 0.2847: 239 (20%); 0.4679: 501 (42%); 0.609: 720 (60%); 0.9167: 995 (83%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2115, 0.4295, 0.5897, 0.8782 | 0.2115: 957 (80%); 0.4295: 742 (62%); 0.5897: 493 (41%); 0.8782: 245 (21%) | 0.2115: 241 (20%); 0.4295: 484 (41%); 0.5897: 724 (61%); 0.8782: 966 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0655, -0.0593, -0.0412, 0 | -0.0655: 958 (80%); -0.0593: 725 (61%); -0.0412: 497 (42%); 0: 318 (27%) | -0.0655: 250 (21%); -0.0593: 480 (40%); -0.0412: 723 (61%); 0: 1157 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.7244, 0.8718, 1 | 0.391: 975 (82%); 0.7244: 721 (60%); 0.8718: 514 (43%); 1: 249 (21%) | 0.391: 258 (22%); 0.7244: 491 (41%); 0.8718: 718 (60%); 1: 1193 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1116, 0.2179, 0.5705, 0.9038 | 0.1116: 954 (80%); 0.2179: 720 (60%); 0.5705: 495 (41%); 0.9038: 244 (20%) | 0.1116: 239 (20%); 0.2179: 514 (43%); 0.5705: 729 (61%); 0.9038: 960 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0289, 0.0245, 0.0635, 0.1958 | -0.0289: 971 (81%); 0.0245: 722 (61%); 0.0635: 478 (40%); 0.1958: 239 (20%) | -0.0289: 240 (20%); 0.0245: 482 (40%); 0.0635: 720 (60%); 0.1958: 954 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3974, 0.7429, 0.9038, 0.9679 | 0.3974: 956 (80%); 0.7429: 745 (62%); 0.9038: 478 (40%); 0.9679: 280 (23%) | 0.3974: 249 (21%); 0.7429: 478 (40%); 0.9038: 721 (60%); 0.9679: 982 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0917, 0.3013, 0.6111, 0.8357 | 0.0917: 955 (80%); 0.3013: 720 (60%); 0.6111: 478 (40%); 0.8357: 240 (20%) | 0.0917: 241 (20%); 0.3013: 480 (40%); 0.6111: 721 (60%); 0.8357: 959 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0158, 0.1104, 0.1876 | -0.0812: 1014 (85%); -0.0158: 717 (60%); 0.1104: 479 (40%); 0.1876: 300 (25%) | -0.0812: 334 (28%); -0.0158: 483 (40%); 0.1104: 719 (60%); 0.1876: 975 (82%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1586, -0.0314, 0.0362, 0.0869 | -0.1586: 958 (80%); -0.0314: 718 (60%); 0.0362: 477 (40%); 0.0869: 242 (20%) | -0.1586: 241 (20%); -0.0314: 481 (40%); 0.0362: 716 (60%); 0.0869: 959 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.5321, 0.7179, 0.859 | 0.2628: 964 (81%); 0.5321: 726 (61%); 0.7179: 493 (41%); 0.859: 241 (20%) | 0.2628: 246 (21%); 0.5321: 484 (41%); 0.7179: 719 (60%); 0.859: 978 (82%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2115, 0.4103, 0.6026, 0.8346 | 0.2115: 962 (81%); 0.4103: 739 (62%); 0.6026: 482 (40%); 0.8346: 239 (20%) | 0.2115: 244 (20%); 0.4103: 486 (41%); 0.6026: 724 (61%); 0.8346: 954 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0433, 0.1067, 0.1952, 0.4133 | 0.0433: 960 (80%); 0.1067: 719 (60%); 0.1952: 477 (40%); 0.4133: 240 (20%) | 0.0433: 240 (20%); 0.1067: 480 (40%); 0.1952: 716 (60%); 0.4133: 957 (80%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.6% | 1.6587, 2.2214, 2.8377, 3.829 | 1.6587: 950 (80%); 2.2214: 713 (60%); 2.8377: 475 (40%); 3.829: 238 (20%) | 1.6587: 238 (20%); 2.2214: 475 (40%); 2.8377: 713 (60%); 3.829: 950 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 8, 20, 27, 34 | 8: 984 (82%); 20: 719 (60%); 27: 505 (42%); 34: 282 (24%) | 8: 248 (21%); 20: 519 (44%); 27: 747 (63%); 34: 955 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 0, 1, 2, 3 | 0: 1193 (100%); 1: 947 (79%); 2: 707 (59%); 3: 468 (39%) | 0: 246 (21%); 1: 486 (41%); 2: 725 (61%); 3: 1009 (85%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.02, -0.0089, 0.0046, 0.0192 | -0.02: 957 (80%); -0.0089: 716 (60%); 0.0046: 478 (40%); 0.0192: 239 (20%) | -0.02: 240 (20%); -0.0089: 482 (40%); 0.0046: 720 (60%); 0.0192: 956 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5095, 25.4036, 26.3791, 27.07 | 24.5095: 957 (80%); 25.4036: 717 (60%); 26.3791: 486 (41%); 27.07: 240 (20%) | 24.5095: 240 (20%); 25.4036: 483 (40%); 26.3791: 718 (60%); 27.07: 955 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.5456, -0.08, 0.2214, 0.7252 | -0.5456: 954 (80%); -0.08: 716 (60%); 0.2214: 477 (40%); 0.7252: 239 (20%) | -0.5456: 239 (20%); -0.08: 477 (40%); 0.2214: 716 (60%); 0.7252: 954 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.7252, -0.2214, 0.08, 0.5456 | -0.7252: 954 (80%); -0.2214: 716 (60%); 0.08: 477 (40%); 0.5456: 239 (20%) | -0.7252: 239 (20%); -0.2214: 477 (40%); 0.08: 716 (60%); 0.5456: 954 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0531, -0.0195, 0.0117, 0.0569 | -0.0531: 956 (80%); -0.0195: 716 (60%); 0.0117: 477 (40%); 0.0569: 239 (20%) | -0.0531: 247 (21%); -0.0195: 477 (40%); 0.0117: 716 (60%); 0.0569: 954 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0819, 8.4621, 8.702, 9.0865 | 8.0819: 954 (80%); 8.4621: 713 (60%); 8.702: 477 (40%); 9.0865: 237 (20%) | 8.0819: 239 (20%); 8.4621: 480 (40%); 8.702: 716 (60%); 9.0865: 956 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 1184 (99%); 1: 387 (32%) | 0: 797 (67%); 1: 1048 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.2% | -1, 0 | -1: 1118 (94%); 0: 926 (78%) | -1: 258 (22%); 0: 996 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 1184 (99%); 1: 436 (37%) | 0: 748 (63%); 1: 1028 (86%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 1, 5, 12, 237 | 1: 1024 (86%); 5: 737 (62%); 12: 480 (40%); 237: 240 (20%) | 1: 241 (20%); 5: 530 (44%); 12: 717 (60%); 237: 955 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 0, 3, 67.2, 122 | 0: 1193 (100%); 3: 726 (61%); 67.2: 477 (40%); 122: 244 (20%) | 0: 277 (23%); 3: 528 (44%); 67.2: 716 (60%); 122: 955 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.0162, 0.1958, 0.4549, 1.0524 | -0.0162: 954 (80%); 0.1958: 716 (60%); 0.4549: 477 (40%); 1.0524: 239 (20%) | -0.0162: 239 (20%); 0.1958: 478 (40%); 0.4549: 716 (60%); 1.0524: 954 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.5292, -0.0019, 0.5535, 1.7609 | -1.5292: 954 (80%); -0.0019: 716 (60%); 0.5535: 477 (40%); 1.7609: 239 (20%) | -1.5292: 239 (20%); -0.0019: 477 (40%); 0.5535: 716 (60%); 1.7609: 954 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.7941, -0.538, 0.0266, 0.9414 | -1.7941: 954 (80%); -0.538: 716 (60%); 0.0266: 477 (40%); 0.9414: 239 (20%) | -1.7941: 239 (20%); -0.538: 477 (40%); 0.0266: 716 (60%); 0.9414: 954 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.0034, 0.1113, 0.2795, 0.681 | -0.0034: 954 (80%); 0.1113: 716 (60%); 0.2795: 478 (40%); 0.681: 239 (20%) | -0.0034: 239 (20%); 0.1113: 477 (40%); 0.2795: 716 (60%); 0.681: 954 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.3421, 0.302, 1.068, 2.6376 | -1.3421: 954 (80%); 0.302: 716 (60%); 1.068: 477 (40%); 2.6376: 239 (20%) | -1.3421: 239 (20%); 0.302: 477 (40%); 1.068: 716 (60%); 2.6376: 954 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.4861, 0.1256, 0.7671, 2.1091 | -1.4861: 954 (80%); 0.1256: 716 (60%); 0.7671: 477 (40%); 2.1091: 239 (20%) | -1.4861: 239 (20%); 0.1256: 477 (40%); 0.7671: 716 (60%); 2.1091: 954 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 43.288, 54.446, 62.35, 70.218 | 43.288: 954 (80%); 54.446: 716 (60%); 62.35: 477 (40%); 70.218: 239 (20%) | 43.288: 239 (20%); 54.446: 477 (40%); 62.35: 716 (60%); 70.218: 954 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0078, 0.0163, 0.0291, 0.0503 | 0.0078: 945 (79%); 0.0163: 710 (60%); 0.0291: 470 (39%); 0.0503: 236 (20%) | 0.0078: 238 (20%); 0.0163: 473 (40%); 0.0291: 713 (60%); 0.0503: 947 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 1193 (100%); 2: 750 (63%); 4: 508 (43%); 9: 240 (20%) | 0: 261 (22%); 2: 591 (50%); 4: 765 (64%); 9: 976 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1477 | 0: 1193 (100%); 0.1477: 239 (20%) | 0: 815 (68%); 0.1477: 954 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.4286, 0.6667 | 0: 1193 (100%); 0.2: 724 (61%); 0.4286: 480 (40%); 0.6667: 261 (22%) | 0: 436 (37%); 0.2: 500 (42%); 0.4286: 727 (61%); 0.6667: 975 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 6 | 0: 1193 (100%); 1: 861 (72%); 3: 492 (41%); 6: 253 (21%) | 0: 332 (28%); 1: 559 (47%); 3: 799 (67%); 6: 980 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 1193 (100%); 2: 750 (63%); 4: 508 (43%); 9: 240 (20%) | 0: 261 (22%); 2: 591 (50%); 4: 765 (64%); 9: 976 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1193 (100%); 1: 870 (73%); 3: 548 (46%); 8: 260 (22%) | 0: 323 (27%); 1: 509 (43%); 3: 741 (62%); 8: 975 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2207, 0.345, 0.5714 | 0: 1100 (92%); 0.2207: 716 (60%); 0.345: 477 (40%); 0.5714: 243 (20%) | 0: 242 (20%); 0.2207: 477 (40%); 0.345: 716 (60%); 0.5714: 958 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667, 0.5964 | 0: 1088 (91%); 0.1667: 478 (40%); 0.5964: 239 (20%) | 0: 647 (54%); 0.1667: 720 (60%); 0.5964: 954 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3, 0.5823 | 0: 1092 (92%); 0.3: 479 (40%); 0.5823: 239 (20%) | 0: 512 (43%); 0.3: 717 (60%); 0.5823: 954 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3, 0.5823 | 0: 1092 (92%); 0.3: 479 (40%); 0.5823: 239 (20%) | 0: 512 (43%); 0.3: 717 (60%); 0.5823: 954 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1863, 0, 0.1667 | -0.1863: 954 (80%); 0: 840 (70%); 0.1667: 247 (21%) | -0.1863: 239 (20%); 0: 835 (70%); 0.1667: 961 (81%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7599, -0.3053, 0.1893, 1.2573 | -0.7599: 954 (80%); -0.3053: 717 (60%); 0.1893: 481 (40%); 1.2573: 239 (20%) | -0.7599: 239 (20%); -0.3053: 478 (40%); 0.1893: 717 (60%); 1.2573: 954 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 1028 (86%); 4: 808 (68%); 7: 526 (44%); 11: 261 (22%) | 2: 271 (23%); 4: 482 (40%); 7: 738 (62%); 11: 961 (81%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0214, 0.0236, 0.052, 0.0878 | -0.0214: 954 (80%); 0.0236: 716 (60%); 0.052: 477 (40%); 0.0878: 239 (20%) | -0.0214: 239 (20%); 0.0236: 477 (40%); 0.052: 716 (60%); 0.0878: 954 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0485, 0.0403, 0.0765, 0.1162 | -0.0485: 954 (80%); 0.0403: 717 (60%); 0.0765: 477 (40%); 0.1162: 239 (20%) | -0.0485: 239 (20%); 0.0403: 476 (40%); 0.0765: 716 (60%); 0.1162: 954 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0106, 0.0078, 0.0254, 0.0532 | -0.0106: 954 (80%); 0.0078: 715 (60%); 0.0254: 477 (40%); 0.0532: 239 (20%) | -0.0106: 239 (20%); 0.0078: 478 (40%); 0.0254: 716 (60%); 0.0532: 954 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/technical.py (f-string template) | 98.1% | 0.5846, 3.4126, 5.772, 8.3236 | 0.5846: 936 (78%); 3.4126: 702 (59%); 5.772: 468 (39%); 8.3236: 234 (20%) | 0.5846: 234 (20%); 3.4126: 468 (39%); 5.772: 702 (59%); 8.3236: 936 (78%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -21.5144, -10.1824, -1.6246, 11.617 | -21.5144: 954 (80%); -10.1824: 716 (60%); -1.6246: 477 (40%); 11.617: 239 (20%) | -21.5144: 239 (20%); -10.1824: 477 (40%); -1.6246: 716 (60%); 11.617: 954 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0392, 0.0527, 0.0696, 0.0948 | 0.0392: 957 (80%); 0.0527: 717 (60%); 0.0696: 480 (40%); 0.0948: 239 (20%) | 0.0392: 240 (20%); 0.0527: 478 (40%); 0.0696: 717 (60%); 0.0948: 955 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.2536, 0.6787, 0.8085, 0.9111 | 0.2536: 954 (80%); 0.6787: 716 (60%); 0.8085: 478 (40%); 0.9111: 240 (20%) | 0.2536: 239 (20%); 0.6787: 477 (40%); 0.8085: 717 (60%); 0.9111: 955 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.6385, -0.0112, 0.8887, 1.8886 | -1.6385: 954 (80%); -0.0112: 716 (60%); 0.8887: 477 (40%); 1.8886: 239 (20%) | -1.6385: 239 (20%); -0.0112: 477 (40%); 0.8887: 716 (60%); 1.8886: 954 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -1.917, -0.7497, 0.0648, 1.2578 | -1.917: 954 (80%); -0.7497: 716 (60%); 0.0648: 477 (40%); 1.2578: 239 (20%) | -1.917: 239 (20%); -0.7497: 477 (40%); 0.0648: 716 (60%); 1.2578: 954 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -2.5392, 2.8566, 5.9286, 9.4076 | -2.5392: 954 (80%); 2.8566: 716 (60%); 5.9286: 477 (40%); 9.4076: 239 (20%) | -2.5392: 239 (20%); 2.8566: 477 (40%); 5.9286: 716 (60%); 9.4076: 954 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.954, 54.316, 59.266, 63.772 | 41.954: 954 (80%); 54.316: 716 (60%); 59.266: 477 (40%); 63.772: 239 (20%) | 41.954: 239 (20%); 54.316: 477 (40%); 59.266: 716 (60%); 63.772: 954 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 33.828, 55.738, 74.084, 88.84 | 33.828: 954 (80%); 55.738: 716 (60%); 74.084: 477 (40%); 88.84: 239 (20%) | 33.828: 239 (20%); 55.738: 477 (40%); 74.084: 716 (60%); 88.84: 954 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 42.792, 50.888, 55.232, 59.25 | 42.792: 954 (80%); 50.888: 716 (60%); 55.232: 477 (40%); 59.25: 239 (20%) | 42.792: 239 (20%); 50.888: 477 (40%); 55.232: 716 (60%); 59.25: 954 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 42.242, 57.246, 63.764, 69.802 | 42.242: 954 (80%); 57.246: 716 (60%); 63.764: 477 (40%); 69.802: 239 (20%) | 42.242: 239 (20%); 57.246: 477 (40%); 63.764: 716 (60%); 69.802: 954 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1189 (100%) | 0: 1193 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0323, 0.0468, 0.0595, 0.0835 | 0.0323: 954 (80%); 0.0468: 716 (60%); 0.0595: 481 (40%); 0.0835: 240 (20%) | 0.0323: 239 (20%); 0.0468: 482 (40%); 0.0595: 718 (60%); 0.0835: 958 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0905, -0.0663, -0.0515, -0.0364 | -0.0905: 955 (80%); -0.0663: 716 (60%); -0.0515: 478 (40%); -0.0364: 240 (20%) | -0.0905: 242 (20%); -0.0663: 479 (40%); -0.0515: 717 (60%); -0.0364: 956 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1193 (100%); 1: 310 (26%) | 0: 883 (74%); 1: 993 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 25, 37, 53, 67 | 25: 972 (81%); 37: 729 (61%); 53: 495 (41%); 67: 248 (21%) | 25: 248 (21%); 37: 497 (42%); 53: 716 (60%); 67: 959 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.2% | 0.0114, 0.0168, 0.0247, 0.0399 | 0.0114: 934 (78%); 0.0168: 700 (59%); 0.0247: 469 (39%); 0.0399: 234 (20%) | 0.0114: 237 (20%); 0.0168: 471 (39%); 0.0247: 702 (59%); 0.0399: 937 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 99.8% | 0.208, 0.4533, 0.6315, 0.8556 | 0.208: 953 (80%); 0.4533: 715 (60%); 0.6315: 477 (40%); 0.8556: 239 (20%) | 0.208: 239 (20%); 0.4533: 477 (40%); 0.6315: 715 (60%); 0.8556: 953 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 99.8% | 30.9, 52.4, 74.5, 108.2 | 30.9: 953 (80%); 52.4: 716 (60%); 74.5: 477 (40%); 108.2: 239 (20%) | 30.9: 239 (20%); 52.4: 477 (40%); 74.5: 716 (60%); 108.2: 953 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -1.62, 1.1575, 2.982, 6.7629 | -1.62: 955 (80%); 1.1575: 716 (60%); 2.982: 477 (40%); 6.7629: 239 (20%) | -1.62: 241 (20%); 1.1575: 477 (40%); 2.982: 716 (60%); 6.7629: 954 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 37.66, 66.362, 81.254, 88.206 | 37.66: 954 (80%); 66.362: 716 (60%); 81.254: 477 (40%); 88.206: 239 (20%) | 37.66: 239 (20%); 66.362: 477 (40%); 81.254: 716 (60%); 88.206: 954 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 40.148, 63.914, 81.276, 90.256 | 40.148: 954 (80%); 63.914: 716 (60%); 81.276: 477 (40%); 90.256: 239 (20%) | 40.148: 239 (20%); 63.914: 477 (40%); 81.276: 716 (60%); 90.256: 954 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 40.472, 65.224, 82.412, 94.712 | 40.472: 954 (80%); 65.224: 716 (60%); 82.412: 477 (40%); 94.712: 239 (20%) | 40.472: 239 (20%); 65.224: 477 (40%); 82.412: 716 (60%); 94.712: 954 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 36.452, 64.168, 84.242, 100 | 36.452: 954 (80%); 64.168: 716 (60%); 84.242: 477 (40%); 100: 265 (22%) | 36.452: 239 (20%); 64.168: 477 (40%); 84.242: 716 (60%); 100: 1193 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 16 | 5: 961 (81%); 9: 751 (63%); 13: 489 (41%); 16: 304 (25%) | 5: 298 (25%); 9: 495 (41%); 13: 785 (66%); 16: 955 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 17 | 5: 990 (83%); 9: 771 (65%); 13: 482 (40%); 17: 296 (25%) | 5: 260 (22%); 9: 499 (42%); 13: 758 (64%); 17: 958 (80%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 47.89, 53.57, 58.52, 64.09 | 47.89: 955 (80%); 53.57: 717 (60%); 58.52: 477 (40%); 64.09: 239 (20%) | 47.89: 240 (20%); 53.57: 478 (40%); 58.52: 716 (60%); 64.09: 954 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0968, 0.3254, 0.5556, 0.7921 | 0.0968: 954 (80%); 0.3254: 719 (60%); 0.5556: 485 (41%); 0.7921: 239 (20%) | 0.0968: 239 (20%); 0.3254: 483 (40%); 0.5556: 718 (60%); 0.7921: 954 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.76, 17.17, 19.642, 24.17 | 14.76: 958 (80%); 17.17: 717 (60%); 19.642: 477 (40%); 24.17: 240 (20%) | 14.76: 240 (20%); 17.17: 479 (40%); 19.642: 716 (60%); 24.17: 958 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.76, 17.17, 19.642, 24.17 | 14.76: 958 (80%); 17.17: 717 (60%); 19.642: 477 (40%); 24.17: 240 (20%) | 14.76: 240 (20%); 17.17: 479 (40%); 19.642: 716 (60%); 24.17: 958 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8479, 0.8805, 0.9091, 0.9476 | 0.8479: 955 (80%); 0.8805: 719 (60%); 0.9091: 478 (40%); 0.9476: 245 (21%) | 0.8479: 239 (20%); 0.8805: 486 (41%); 0.9091: 716 (60%); 0.9476: 958 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.64, 0.73, 0.81, 0.9 | 0.64: 964 (81%); 0.73: 728 (61%); 0.81: 501 (42%); 0.9: 242 (20%) | 0.64: 247 (21%); 0.73: 486 (41%); 0.81: 726 (61%); 0.9: 971 (81%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 99.9% | 0.0234, 0.0465, 0.0756, 0.1144 | 0.0234: 954 (80%); 0.0465: 717 (60%); 0.0756: 478 (40%); 0.1144: 240 (20%) | 0.0234: 239 (20%); 0.0465: 477 (40%); 0.0756: 716 (60%); 0.1144: 954 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 45.2074, 78.5137, 122.3127, 209.8921 | 45.2074: 954 (80%); 78.5137: 716 (60%); 122.3127: 477 (40%); 209.8921: 239 (20%) | 45.2074: 239 (20%); 78.5137: 477 (40%); 122.3127: 716 (60%); 209.8921: 954 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.7132, 75.8912, 118.4521, 203.3981 | 43.7132: 954 (80%); 75.8912: 716 (60%); 118.4521: 477 (40%); 203.3981: 239 (20%) | 43.7132: 239 (20%); 75.8912: 477 (40%); 118.4521: 716 (60%); 203.3981: 954 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.8616, 72.6898, 114.1249, 195.4466 | 41.8616: 954 (80%); 72.6898: 716 (60%); 114.1249: 477 (40%); 195.4466: 239 (20%) | 41.8616: 239 (20%); 72.6898: 477 (40%); 114.1249: 716 (60%); 195.4466: 954 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 46.6603, 81.2806, 127.0225, 216.1544 | 46.6603: 954 (80%); 81.2806: 716 (60%); 127.0225: 477 (40%); 216.1544: 239 (20%) | 46.6603: 239 (20%); 81.2806: 477 (40%); 127.0225: 716 (60%); 216.1544: 954 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.0184, 83.1932, 131.094, 222.4821 | 48.0184: 954 (80%); 83.1932: 716 (60%); 131.094: 477 (40%); 222.4821: 239 (20%) | 48.0184: 239 (20%); 83.1932: 477 (40%); 131.094: 716 (60%); 222.4821: 954 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1193 (100%) | 0: 1051 (88%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1193 (100%) | 0: 1067 (89%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.8% | -0.0384, 0.0369, 0.0726, 0.1127 | -0.0384: 954 (80%); 0.0369: 715 (60%); 0.0726: 477 (40%); 0.1127: 239 (20%) | -0.0384: 239 (20%); 0.0369: 477 (40%); 0.0726: 716 (60%); 0.1127: 953 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -62.18, -35.074, -16.31, -5.518 | -62.18: 954 (80%); -35.074: 716 (60%); -16.31: 477 (40%); -5.518: 239 (20%) | -62.18: 239 (20%); -35.074: 477 (40%); -16.31: 716 (60%); -5.518: 954 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.8% | 0.5419, 0.7935, 1.0261, 1.3038 | 0.5419: 943 (79%); 0.7935: 707 (59%); 1.0261: 472 (40%); 1.3038: 236 (20%) | 0.5419: 236 (20%); 0.7935: 472 (40%); 1.0261: 707 (59%); 1.3038: 943 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.8% | 3, 5, 7, 9 | 3: 965 (81%); 5: 755 (63%); 7: 518 (43%); 9: 282 (24%) | 3: 320 (27%); 5: 546 (46%); 7: 767 (64%); 9: 1039 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 98.7% | 0.1919, 0.2288, 0.2778, 0.3644 | 0.1919: 943 (79%); 0.2288: 707 (59%); 0.2778: 471 (39%); 0.3644: 236 (20%) | 0.1919: 237 (20%); 0.2288: 472 (40%); 0.2778: 707 (59%); 0.3644: 942 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 98.7% | 3, 5, 7, 9 | 3: 995 (83%); 5: 799 (67%); 7: 561 (47%); 9: 319 (27%) | 3: 292 (24%); 5: 495 (41%); 7: 715 (60%); 9: 977 (82%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 98.8% | 0.0242, 0.034, 0.0457, 0.0698 | 0.0242: 945 (79%); 0.034: 711 (60%); 0.0457: 474 (40%); 0.0698: 237 (20%) | 0.0242: 237 (20%); 0.034: 473 (40%); 0.0457: 708 (59%); 0.0698: 943 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 98.8% | 3, 5, 7, 9 | 3: 985 (83%); 5: 784 (66%); 7: 581 (49%); 9: 327 (27%) | 3: 291 (24%); 5: 496 (42%); 7: 709 (59%); 9: 969 (81%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 98.9% | -0.2961, -0.1601, -0.0453, 0.1044 | -0.2961: 945 (79%); -0.1601: 708 (59%); -0.0453: 473 (40%); 0.1044: 236 (20%) | -0.2961: 237 (20%); -0.1601: 472 (40%); -0.0453: 709 (59%); 0.1044: 944 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 98.9% | 1, 3, 5, 7 | 1: 1180 (99%); 3: 778 (65%); 5: 476 (40%); 7: 283 (24%) | 1: 237 (20%); 3: 573 (48%); 5: 796 (67%); 7: 992 (83%) | OFFLINE |
| year_high | backtest/signals/technical.py | 100.0% | 55.11, 93.3072, 151.6573, 257.384 | 55.11: 955 (80%); 93.3072: 716 (60%); 151.6573: 477 (40%); 257.384: 239 (20%) | 55.11: 240 (20%); 93.3072: 477 (40%); 151.6573: 716 (60%); 257.384: 954 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.9% |
| 8k_item_5_02_filed_within_7d | 3.3% |
| above_avwap_20high | 50.5% |
| above_avwap_20low | 84.8% |
| above_avwap_252low | 75.8% |
| above_avwap_50low | 83.9% |
| above_cam_r3 | 43.1% |
| above_cam_r4 | 23.8% |
| above_cpr | 61.3% |
| above_pivot | 62.3% |
| above_prev_high | 28.3% |
| above_prev_high_clearance_atr_05 | 7.5% |
| above_prev_low | 85.8% |
| above_r1 | 25.1% |
| above_r2 | 10.1% |
| above_vwap | 36.8% |
| above_wood_p | 61.0% |
| ad_rising | 66.6% |
| adx_cross_up | 1.3% |
| adx_cross_up_20 | 1.5% |
| adx_di_bear | 35.5% |
| adx_di_bull | 64.5% |
| adx_strong | 7.0% |
| adx_trending | 40.4% |
| ao_cross_up | 3.2% |
| ao_positive | 66.6% |
| ao_twin_peaks_bull | 2.5% |
| at_key_fib | 14.8% |
| at_key_fib_wide | 36.5% |
| avwap_20high_loss_recent_3d | 18.9% |
| avwap_20high_reclaim_recent_3d | 30.4% |
| avwap_20low_loss_recent_3d | 11.6% |
| avwap_20low_reclaim_recent_3d | 9.6% |
| avwap_252low_loss_recent_3d | 4.7% |
| avwap_252low_reclaim_recent_3d | 5.6% |
| avwap_50low_loss_recent_3d | 9.3% |
| avwap_50low_reclaim_recent_3d | 6.5% |
| bb_10_20_above_mid | 73.5% |
| bb_10_20_expanding | 38.1% |
| bb_10_20_pctb_gt_75 | 37.6% |
| bb_10_20_pctb_gt_8 | 28.9% |
| bb_10_20_pctb_gt_85 | 19.5% |
| bb_10_20_pctb_gt_9 | 10.8% |
| bb_10_20_pctb_gt_95 | 5.4% |
| bb_10_20_pctb_lt_05 | 0.7% |
| bb_10_20_pctb_lt_1 | 1.3% |
| bb_10_20_pctb_lt_15 | 2.4% |
| bb_10_20_pctb_lt_2 | 4.6% |
| bb_10_20_pctb_lt_25 | 7.0% |
| bb_10_20_reclaim_from_lower_recent_3d | 1.5% |
| bb_10_20_reclaim_from_upper_recent_3d | 12.2% |
| bb_10_20_squeeze | 43.0% |
| bb_10_20_touch_lower | 1.8% |
| bb_10_20_touch_upper | 6.2% |
| bb_20_15_above_mid | 70.2% |
| bb_20_15_expanding | 56.7% |
| bb_20_15_pctb_gt_75 | 63.5% |
| bb_20_15_pctb_gt_8 | 57.8% |
| bb_20_15_pctb_gt_85 | 52.4% |
| bb_20_15_pctb_gt_9 | 45.8% |
| bb_20_15_pctb_gt_95 | 39.1% |
| bb_20_15_pctb_lt_05 | 4.4% |
| bb_20_15_pctb_lt_1 | 7.2% |
| bb_20_15_pctb_lt_15 | 10.6% |
| bb_20_15_pctb_lt_2 | 14.2% |
| bb_20_15_pctb_lt_25 | 19.8% |
| bb_20_15_reclaim_from_lower_recent_3d | 6.1% |
| bb_20_15_reclaim_from_upper_recent_3d | 19.3% |
| bb_20_15_squeeze | 32.4% |
| bb_20_15_touch_lower | 6.0% |
| bb_20_15_touch_upper | 39.3% |
| bb_20_20_above_mid | 70.2% |
| bb_20_20_expanding | 56.7% |
| bb_20_20_pctb_gt_75 | 54.1% |
| bb_20_20_pctb_gt_8 | 45.8% |
| bb_20_20_pctb_gt_85 | 36.8% |
| bb_20_20_pctb_gt_9 | 27.4% |
| bb_20_20_pctb_gt_95 | 18.5% |
| bb_20_20_pctb_lt_05 | 0.9% |
| bb_20_20_pctb_lt_1 | 1.8% |
| bb_20_20_pctb_lt_15 | 3.6% |
| bb_20_20_pctb_lt_2 | 7.2% |
| bb_20_20_pctb_lt_25 | 11.3% |
| bb_20_20_reclaim_from_lower_recent_3d | 2.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 15.0% |
| bb_20_20_squeeze | 15.3% |
| bb_20_20_touch_lower | 1.2% |
| bb_20_20_touch_upper | 17.5% |
| bearish_engulfing | 3.1% |
| bearish_pin_bar | 2.0% |
| below_avwap_20high | 49.5% |
| below_avwap_20low | 15.2% |
| below_avwap_252low | 24.2% |
| below_avwap_50low | 16.1% |
| below_cam_s3 | 21.5% |
| below_cam_s4 | 12.5% |
| below_cpr | 37.6% |
| below_ema_20 | 30.3% |
| below_ema_200 | 67.8% |
| below_ema_200_break_recent_5d | 4.6% |
| below_ema_20_break_recent_5d | 6.5% |
| below_ema_21 | 30.3% |
| below_ema_21_break_recent_5d | 5.7% |
| below_ema_50 | 42.8% |
| below_ema_50_break_recent_5d | 6.6% |
| below_ema_9 | 28.8% |
| below_ema_9_break_recent_5d | 21.0% |
| below_prev_high | 71.2% |
| below_prev_low | 14.2% |
| below_prev_low_clearance_atr_05 | 2.8% |
| below_s1 | 12.8% |
| below_s2 | 4.6% |
| below_sma_20 | 29.8% |
| below_sma_200 | 69.5% |
| below_sma_21 | 29.7% |
| below_sma_50 | 39.8% |
| below_sma_9 | 27.3% |
| below_vwap | 63.2% |
| blowoff_recent_3d | 0.4% |
| break_52w_high | 0.5% |
| break_52w_high_confirmed_today | 0.3% |
| break_52w_low | 0.1% |
| bullish_engulfing | 7.0% |
| bullish_pin_bar | 6.2% |
| capitulation_recent_3d | 0.8% |
| ceo_buy | 1.5% |
| cfo_buy | 0.5% |
| chandelier_long_bullish | 77.3% |
| chandelier_long_flip_dn | 3.9% |
| chandelier_short_bearish | 37.2% |
| chandelier_short_flip_up | 6.5% |
| classification_change_from_tech | 50.0% |
| classification_change_to_defensive | 50.0% |
| close_above_open | 70.3% |
| close_below_open | 29.7% |
| close_in_bottom_40pct_of_range | 29.7% |
| close_in_top_40pct_of_range | 70.3% |
| cluster_buy | 0.9% |
| cmf_cross_dn | 2.7% |
| cmf_cross_up | 7.0% |
| cmf_negative | 32.8% |
| cmf_positive | 66.9% |
| concentrated_sell | 3.4% |
| cpr_narrow | 89.2% |
| cpr_narrow_tight | 25.9% |
| cup_handle_detected | 11.9% |
| cup_handle_neckline_break_retest_long | 9.1% |
| dc10_breakout_dn | 1.8% |
| dc10_breakout_dn_1pct | 4.9% |
| dc10_breakout_up | 17.5% |
| dc10_breakout_up_1pct | 30.7% |
| dc10_new_high | 20.4% |
| dc10_strong_breakout_dn | 0.2% |
| dc10_strong_breakout_up | 3.7% |
| dc20_breakout_dn | 1.6% |
| dc20_breakout_up | 17.0% |
| dc20_new_high | 19.4% |
| dc20_resistance_break_retest_strong | 48.6% |
| dc20_support_break_retest_strong | 21.2% |
| defensive_leadership | 42.0% |
| director_only_buy | 3.8% |
| doji | 3.1% |
| double_bottom_detected | 13.6% |
| double_top_detected | 14.5% |
| dpi_elevated | 57.8% |
| drying_volume_on_down_turn | 29.7% |
| drying_volume_on_up_turn | 70.3% |
| ema_20_50_bearish | 69.7% |
| ema_20_50_bullish | 30.3% |
| ema_20_50_death_cross | 0.1% |
| ema_20_50_golden_cross | 1.6% |
| ema_50_200_bearish | 74.8% |
| ema_50_200_bullish | 25.2% |
| ema_50_200_death_cross | 0.3% |
| ema_50_200_golden_cross | 0.3% |
| ema_9_21_bearish | 31.6% |
| ema_9_21_bullish | 68.4% |
| ema_9_21_death_cross | 0.1% |
| ema_9_21_golden_cross | 3.3% |
| evening_star | 3.6% |
| flag_bear_break_retest_short | 1.3% |
| flag_bear_broke | 1.5% |
| flag_bear_detected | 0.4% |
| flag_bull_break_retest_long | 1.8% |
| flag_bull_broke | 1.8% |
| flag_bull_detected | 0.8% |
| force_index_cross_dn | 3.3% |
| force_index_cross_up | 2.6% |
| force_index_positive | 70.0% |
| gap_dn_1_5pct | 5.9% |
| gap_dn_2pct | 3.4% |
| gap_up_1_5pct | 4.9% |
| gap_up_2pct | 2.8% |
| hammer | 4.2% |
| head_shoulders_bottom_detected | 6.3% |
| head_shoulders_top_detected | 3.0% |
| house_cluster_buy | 4.5% |
| house_cluster_sell | 5.0% |
| htf_aligned_bear | 32.2% |
| htf_aligned_bull | 18.2% |
| htf_disagreement | 5.0% |
| hull_bearish | 24.5% |
| hull_bullish | 75.5% |
| hull_flip_dn | 5.0% |
| hull_flip_up | 4.6% |
| ichi_above_cloud | 33.9% |
| ichi_above_cloud_break_recent_5d | 13.2% |
| ichi_below_cloud | 46.4% |
| ichi_below_cloud_break_recent_5d | 4.9% |
| ichi_cloud_thick | 87.6% |
| ichi_tk_bearish | 32.7% |
| ichi_tk_bullish | 63.1% |
| ichi_tk_cross_dn | 0.4% |
| ichi_tk_cross_up | 2.8% |
| ichi_weekly_above_cloud | 22.3% |
| ichi_weekly_below_cloud | 47.6% |
| ichi_weekly_in_cloud | 30.0% |
| in_reversal_window | 2.0% |
| inside_bar | 14.9% |
| inside_cpr | 3.6% |
| inside_kc | 84.7% |
| insider_cluster_active | 25.0% |
| institutional_buy | 84.2% |
| institutional_negative | 7.7% |
| institutional_persistence_growing | 41.2% |
| institutional_persistence_strong | 57.3% |
| institutional_strong_buy | 73.7% |
| inverted_cup_handle_detected | 13.3% |
| is_friday | 15.4% |
| is_halloween_period | 54.4% |
| is_halloween_period_first_day | 0.2% |
| is_january | 8.4% |
| is_january_extended | 11.2% |
| is_monday | 20.6% |
| is_pre_holiday | 4.1% |
| is_summer_period | 45.6% |
| is_totm_window | 31.3% |
| is_totm_window_first_day | 8.5% |
| is_week_open | 23.1% |
| kc_touch_lower | 2.3% |
| kc_touch_upper | 18.1% |
| large_dollar_buy | 2.0% |
| macd_12_26_9_bearish | 21.3% |
| macd_12_26_9_bullish | 78.7% |
| macd_12_26_9_crossover_dn | 1.9% |
| macd_12_26_9_crossover_up | 3.2% |
| macd_8_21_5_bearish | 20.8% |
| macd_8_21_5_bullish | 79.2% |
| macd_8_21_5_crossover_dn | 4.3% |
| macd_8_21_5_crossover_up | 2.0% |
| marubozu_bear | 0.4% |
| marubozu_bull | 1.4% |
| mfi_broad_overbought | 20.4% |
| mfi_broad_oversold | 4.8% |
| mfi_overbought | 4.8% |
| mfi_oversold | 0.9% |
| monthly_above_sma_12 | 29.0% |
| monthly_above_sma_6 | 35.3% |
| monthly_bias_bear | 56.1% |
| monthly_bias_bull | 20.3% |
| monthly_momentum_pos | 32.9% |
| morning_star | 5.5% |
| near_52w_high | 2.3% |
| near_52w_high_95pct | 5.5% |
| near_52w_high_retest_long | 0.5% |
| near_52w_low | 1.6% |
| near_52w_low_105pct | 5.0% |
| near_52w_low_retest_short | 1.9% |
| near_avwap_20high_atr_05x | 61.3% |
| near_avwap_20high_atr_10x | 83.3% |
| near_avwap_20high_atr_15x | 95.3% |
| near_avwap_20high_atr_20x | 98.9% |
| near_avwap_20low_atr_05x | 25.1% |
| near_avwap_20low_atr_10x | 41.9% |
| near_avwap_20low_atr_15x | 59.3% |
| near_avwap_20low_atr_20x | 74.9% |
| near_avwap_252low_atr_05x | 11.2% |
| near_avwap_252low_atr_10x | 23.3% |
| near_avwap_252low_atr_15x | 34.6% |
| near_avwap_252low_atr_20x | 47.3% |
| near_avwap_50low_atr_05x | 19.8% |
| near_avwap_50low_atr_10x | 32.7% |
| near_avwap_50low_atr_15x | 44.0% |
| near_avwap_50low_atr_20x | 57.6% |
| near_cam_r3 | 20.8% |
| near_cam_s3 | 14.4% |
| near_cam_s4 | 7.0% |
| near_fib_236 | 4.3% |
| near_fib_382 | 5.5% |
| near_fib_500 | 5.4% |
| near_fib_618 | 4.1% |
| near_fib_786 | 4.0% |
| near_pivot | 17.7% |
| near_prev_close | 18.6% |
| near_prev_high | 16.6% |
| near_prev_low | 10.1% |
| near_r1 | 17.1% |
| near_r1_wide | 65.9% |
| near_r2 | 5.7% |
| near_r2_wide | 41.6% |
| near_s1 | 8.1% |
| near_s1_wide | 47.2% |
| near_s2 | 3.4% |
| near_s2_wide | 24.1% |
| near_s3 | 1.3% |
| near_wood_r1 | 13.0% |
| near_wood_s1 | 9.8% |
| news_uses_polygon_score | 21.0% |
| obv_bearish | 32.8% |
| obv_bullish | 67.2% |
| obv_diverge_bull | 7.8% |
| obv_falling | 38.1% |
| obv_rising | 61.9% |
| outside_bar | 9.6% |
| pead_negative_surprise | 19.7% |
| pead_positive_surprise | 16.6% |
| pin_bar | 8.2% |
| po3_accumulation_active | 36.5% |
| po3_bearish | 10.6% |
| po3_bullish | 22.1% |
| po3_manipulation_sweep_down | 6.4% |
| po3_manipulation_sweep_up | 9.3% |
| po3_mmbm_setup | 3.7% |
| po3_mmsm_setup | 1.7% |
| po3_sweep_above_prior_high | 55.7% |
| po3_sweep_below_prior_low | 46.5% |
| ppo_bullish | 76.1% |
| ppo_crossover_dn | 2.2% |
| ppo_crossover_up | 2.8% |
| pre_fomc_d0 | 3.2% |
| pre_fomc_d1 | 2.3% |
| pre_fomc_window | 5.4% |
| price_above_dema | 79.2% |
| price_above_ema_20 | 69.7% |
| price_above_ema_200 | 32.2% |
| price_above_ema_200_break_recent_5d | 11.6% |
| price_above_ema_20_break_recent_5d | 18.6% |
| price_above_ema_21 | 69.7% |
| price_above_ema_21_break_recent_5d | 19.3% |
| price_above_ema_50 | 57.2% |
| price_above_ema_50_break_recent_5d | 24.2% |
| price_above_ema_9 | 71.2% |
| price_above_ema_9_break_recent_5d | 29.3% |
| price_above_hull | 62.8% |
| price_above_sma_200 | 30.5% |
| price_above_sma_21 | 70.3% |
| price_above_sma_50 | 60.2% |
| price_above_tema | 64.8% |
| price_below_dema | 20.8% |
| price_below_hull | 37.2% |
| price_below_tema | 35.2% |
| psar_bullish | 69.7% |
| psar_flip_dn | 4.4% |
| psar_flip_up | 2.7% |
| r1_break_retest_long | 79.4% |
| recent_blowoff_at_r3 | 0.1% |
| resistance_break_retest | 70.3% |
| risk_off_regime_bond_signal | 18.6% |
| risk_off_regime_bond_signal_strong | 4.4% |
| risk_off_regime_gold_signal | 35.1% |
| risk_on_regime_bond_signal | 50.7% |
| risk_on_regime_bond_signal_strong | 24.0% |
| roc_positive | 70.3% |
| roc_turning_dn | 1.9% |
| roc_turning_up | 1.2% |
| rsi_14_bullish | 69.0% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_14_cross_dn_overbought_recent_3d | 4.2% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_14_cross_up_oversold_recent_3d | 3.4% |
| rsi_14_extreme_ob | 0.2% |
| rsi_14_extreme_os | 0.2% |
| rsi_14_overbought | 5.7% |
| rsi_14_oversold | 1.5% |
| rsi_14_rising | 61.7% |
| rsi_21_bullish | 64.0% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_21_cross_dn_overbought_recent_3d | 0.9% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 1.3% |
| rsi_21_extreme_ob | 0.1% |
| rsi_21_extreme_os | 0.3% |
| rsi_21_overbought | 1.3% |
| rsi_21_oversold | 0.8% |
| rsi_21_rising | 61.5% |
| rsi_2_bullish | 65.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 35.5% |
| rsi_2_cross_dn_overbought_recent_3d | 37.7% |
| rsi_2_cross_up_extreme_os_recent_3d | 21.5% |
| rsi_2_cross_up_oversold_recent_3d | 28.9% |
| rsi_2_extreme_ob | 33.6% |
| rsi_2_extreme_os | 8.5% |
| rsi_2_overbought | 45.2% |
| rsi_2_oversold | 16.9% |
| rsi_2_rising | 61.4% |
| rsi_9_bullish | 69.8% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 2.2% |
| rsi_9_cross_dn_overbought_recent_3d | 11.2% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.6% |
| rsi_9_cross_up_oversold_recent_3d | 6.5% |
| rsi_9_extreme_ob | 3.1% |
| rsi_9_extreme_os | 0.1% |
| rsi_9_overbought | 19.2% |
| rsi_9_oversold | 1.9% |
| rsi_9_rising | 61.5% |
| s1_break_retest_short | 36.6% |
| sc_13d_filed_within_30d | 1.5% |
| sc_13g_filed_within_30d | 2.2% |
| sector_outperforming_spy | 58.1% |
| sector_underperforming_spy | 41.9% |
| shooting_star | 2.0% |
| sma_20_50_bullish | 30.6% |
| sma_20_50_golden_cross | 2.4% |
| sma_50_200_bullish | 27.6% |
| sma_50_200_golden_cross | 0.2% |
| sma_9_21_bullish | 69.8% |
| sma_9_21_golden_cross | 1.7% |
| smc_bos_bearish | 16.8% |
| smc_bos_bullish | 5.8% |
| smc_bos_retest_long | 4.2% |
| smc_bos_retest_short | 5.2% |
| smc_breaker_block_bearish | 20.6% |
| smc_breaker_block_bullish | 14.6% |
| smc_choch_bearish | 6.5% |
| smc_choch_bullish | 3.6% |
| smc_equal_highs_swept | 1.7% |
| smc_equal_lows_swept | 7.3% |
| smc_fvg_bearish_active | 24.7% |
| smc_fvg_bullish_active | 49.5% |
| smc_fvg_retest_long_zone | 5.3% |
| smc_fvg_retest_short_zone | 7.5% |
| smc_in_discount_zone | 56.5% |
| smc_in_premium_zone | 64.6% |
| smc_inverse_fvg_bearish | 79.4% |
| smc_inverse_fvg_bullish | 81.1% |
| smc_liquidity_swept_dn | 1.1% |
| smc_liquidity_swept_up | 1.8% |
| smc_mitigation_block_long | 1.4% |
| smc_mitigation_block_short | 2.9% |
| smc_ob_bearish_active | 53.1% |
| smc_ob_bullish_active | 15.7% |
| smc_ote_long_zone | 9.6% |
| smc_ote_short_zone | 9.5% |
| squeeze_fire_dn | 1.5% |
| squeeze_fire_up | 0.6% |
| squeeze_in | 20.8% |
| squeeze_positive | 70.7% |
| stoch_bearish_cross | 9.3% |
| stoch_broad_overbought | 50.0% |
| stoch_broad_oversold | 8.9% |
| stoch_bullish_cross | 12.7% |
| stoch_overbought | 42.3% |
| stoch_oversold | 6.1% |
| stochrsi_cross_dn | 37.3% |
| stochrsi_cross_up | 19.4% |
| stochrsi_overbought | 43.3% |
| stochrsi_oversold | 10.1% |
| supertrend_flip_recent_long_5d | 1.3% |
| support_break_retest | 29.7% |
| tema_above_dema | 74.2% |
| tema_cross_dn | 0.2% |
| tema_cross_up | 0.8% |
| three_black_crows | 1.4% |
| three_white_soldiers | 8.0% |
| triangle_apex_break_retest_long | 19.6% |
| triangle_ascending_detected | 12.3% |
| triangle_descending_detected | 8.4% |
| uo_overbought | 5.3% |
| uo_oversold | 0.5% |
| usd_strengthening | 19.7% |
| usd_weakening | 20.1% |
| vix_band_high | 32.1% |
| vix_band_low | 40.5% |
| vix_band_mid | 27.4% |
| vix_term_backwardation | 7.4% |
| vix_term_contango | 92.6% |
| vol_spike_2x_on_down_day_recent_3d | 1.3% |
| vol_spike_2x_on_up_day_recent_3d | 2.0% |
| vp_above_value_area | 30.2% |
| vp_below_value_area | 16.4% |
| vp_close_above_poc | 62.7% |
| vp_close_below_poc | 37.3% |
| vp_in_value_area | 53.4% |
| week_open_gap_down_15pct | 1.1% |
| week_open_gap_up_15pct | 1.8% |
| weekly_above_ema_10 | 58.8% |
| weekly_above_ema_20 | 40.7% |
| weekly_bias_bear | 39.2% |
| weekly_bias_bull | 38.7% |
| weekly_momentum_pos | 70.3% |
| williams_r_overbought | 45.0% |
| williams_r_oversold | 8.0% |
| williams_r_rising | 57.8% |
| within_pead_window | 38.9% |
| within_post_deletion_window | 7.3% |
| within_post_inclusion_window | 0.7% |
| within_pre_rebalance_window | 0.8% |
| xs_avoid_high_ivol | 72.9% |
| xs_avoid_high_max | 72.3% |
| xs_high_beta_decile | 23.9% |
| xs_low_beta_bottom_quintile | 23.9% |
| xs_low_beta_decile | 18.2% |
| xs_low_beta_decile_entry_recent_5d | 0.3% |
| xs_low_beta_top_quintile | 18.2% |
| xs_momentum_bottom_decile | 20.1% |
| xs_momentum_bottom_quintile | 34.1% |
| xs_momentum_top_decile | 3.7% |
| xs_momentum_top_quintile | 8.3% |
| xs_quality_bottom_quintile | 23.2% |
| xs_quality_top_quintile | 20.0% |
| xs_quality_top_tercile | 38.5% |
| year_high_break_retest_long | 1.4% |
| year_low_break_retest_short | 1.8% |
| yoy_surprise_high | 44.3% |
| yoy_surprise_negative | 45.8% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 89.6% |
| committed_growth_holders | 89.6% |
| corp_donations_1y | 6.7% |
| corp_donations_count_1y | 6.7% |
| corp_donations_unique_pacs | 6.7% |
| cot_rut_commercials_pctile_3y | 46.1% |
| cot_rut_mmoney_pctile_3y | 46.1% |
| cup_handle_depth_pct | 18.4% |
| days_since_deletion | 8.0% |
| days_since_inclusion | 12.6% |
| days_since_last_earnings | 97.0% |
| days_to_next_holiday | 64.7% |
| days_to_rebalance | 10.0% |
| dpi_30d_avg | 95.6% |
| dpi_recent | 95.6% |
| earnings_announcement_return | 90.8% |
| earnings_eps_yoy_growth | 92.9% |
| flag_bear_pole_move_pct | 0.4% |
| flag_bull_pole_move_pct | 0.8% |
| gov_contracts_4q_sum | 41.5% |
| gov_contracts_last_qtr_amount | 41.5% |
| gov_contracts_qoq_growth | 41.5% |
| head_shoulders_magnitude_pct | 9.2% |
| insider_director_buyers_30d | 6.4% |
| insider_officer_buyers_30d | 6.4% |
| insider_total_shares_bought_30d | 6.4% |
| insider_unique_buyers_30d | 6.4% |
| inverted_cup_handle_height_pct | 19.7% |
| lobbying_amount_1y | 70.8% |
| lobbying_amount_q | 70.8% |
| lobbying_amount_yoy | 70.8% |
| monthly_momentum_6m | 97.7% |
| otc_short_ratio_recent | 95.6% |
| otc_volume_recent | 95.6% |
| pair_half_life | 93.5% |
| pair_max_abs_zscore | 93.5% |
| pair_zscore_signed | 93.5% |
| pct_from_avwap_20high | 80.6% |
| pct_from_avwap_20low | 97.9% |
| pct_from_avwap_252low | 97.7% |
| persistent_holders_4q | 89.6% |
| persistent_holders_8q | 89.6% |
| sc_13g_latest_percent_owned | 1.2% |
| search_volume_index_recent | 78.4% |
| search_volume_observations | 78.4% |
| search_volume_zscore_30d | 78.4% |
| sector_etf_return_20d | 2.6% |
| spy_return_20d | 2.6% |
| total_active_holders | 89.6% |
| triangle_breakdown_pct | 8.4% |
| triangle_breakout_pct | 12.3% |
| xs_quality_decile | 62.4% |
| xs_quality_gross_profitability | 62.4% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.998), `avwap_50low` (1.0), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (1.0), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `days_since_classification_change` (-1.0), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.997), `double_top_peak` (0.998), `entry_stop_long` (0.998), `entry_stop_short` (0.998), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.999), `fib_ext_127` (0.993), `fib_ext_162` (0.99), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.984), `monthly_sma_6` (0.996), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.998), `swing_high` (0.995), `swing_low` (0.998), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.997), `vp_value_area_low` (0.998), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_low` (0.99)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | mirror of top_40pct | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P2.1 | range-position cutoff | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P3.1 | breakout clearance - the breakout bar cl | 3 | MIXED - offline AND pending levels | no - production only; 1 offline; 1 pending (DEFINED-NO-ACTUATOR) | 1 | 1 | 1 |
| P3.2 | retest tolerance - a later bar's low wit | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P3.3.1 | breakout window - lag 2 to N bars ago, a | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P3.3.2 | breakout window - lag 2 to N bars ago, a | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P5.1 | volume ratio ceiling (vol / avg, strict  | 3 | subset-safe | no - derives offline | 1 | 2 | 0 |
| P6 | ppo_hist >= -0.2513 | 5 | subset-safe | no - derives offline | 1 | 4 | 0 |
| P7 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     3 x 3 x 3 x 3 x 3 x 3 x 3 x 5 x 1 = 10935
offline gradings   29 level-combinations x 24 exits = 696 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  10905 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 29 + 10905 = 10935 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 642 census axes join it only when REGISTERED at the T3 band review.
