# Table A - break_retest_volume

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build adafdd452 | commit adafdd452 at 2026-10-25 20:59:24 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** breakout | **status:** NOT-STARTED | **R5 fires:** 2164 (closed fires in the exit cube: 2164 of 2164, S6-B3258) | **surviving fires (T1):** 1073 (survives_pct 0.4958)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  close_above_open  <- backtest/signals/technical.py
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  close_below_open  <- backtest/signals/technical.py
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P2.1-P2.1 (band rows in Table A)
P3  close_in_bottom_40pct_of_range  <- backtest/signals/technical.py
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P3.1-P3.1 (band rows in Table A)
P4  close_in_top_40pct_of_range  <- backtest/signals/technical.py
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P4.1-P4.1 (band rows in Table A)
P5  obv_bearish  <- backtest/signals/technical.py
       DEFN: OBV vs its moving average (technical.py:1570)
       knobs P5.1-P5.1 (band rows in Table A)
P6  obv_bullish  <- backtest/signals/technical.py
       DEFN: OBV vs its moving average (technical.py:1570)
       knobs P6.1-P6.2 (band rows in Table A)
P7  resistance_break_retest  <- backtest/signals/technical.py
       DEFN: a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals)
       knobs P7.1-P7.3 (band rows in Table A)
P8  support_break_retest  <- backtest/signals/technical.py
       DEFN: a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals)
       knobs P8.1-P8.1 (band rows in Table A)
P9  vol_below_avg  <- backtest/signals/technical.py
       DEFN: volume / 20d average < 1.0 (technical.py compute_volume)
       knobs P9.1-P9.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P10  ppo_hist >= -0.2823   [EXISTING-THRESHOLD]
P11  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_break_retest_volume (docstring and return dropped):

```python
fl = s.get('resistance_break_retest') and s.get('obv_bullish') and s.get('close_above_open') and s.get('close_in_top_40pct_of_range') and s.get('vol_below_avg')
fl = fl and s.get('ppo_hist', float('-inf')) >= -0.2823
fs = s.get('support_break_retest') and s.get('obv_bearish') and s.get('close_below_open') and s.get('close_in_bottom_40pct_of_range') and s.get('vol_below_avg') and (not _short_borrow_trap_active(s))
fs = fs and s.get('ppo_hist', float('-inf')) >= -0.2823
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
| P1 | PRODUCER | close_above_open - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | (structural) c > o - optional min body pct - backtest/signals/technical.py bar-anatomy block | BRACKET zero | 0.0 | [0, 0.2, 0.5] pct | offline 0 of 3 levels - none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | close_below_open - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | mirror of close_above_open - technical.py bar-anatomy block | mirror | 0.0 | [0, 0.2, 0.5] pct | offline 0 of 3 levels - none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | close_in_bottom_40pct_of_range - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | mirror of top_40pct - backtest/signals/technical.py:1682 region | mirror | 0.4 | [0.25, 0.40, 0.50] | offline 0 of 3 levels - none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | close_in_top_40pct_of_range - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | range-position cutoff - backtest/signals/technical.py:1682 | BRACKET production 0.40 | 0.4 | [0.25, 0.40, 0.50] | offline 0 of 3 levels - none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | PRODUCER | obv_bearish - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | OBV vs its moving average (technical.py:1570) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | mirror of obv_bullish - backtest/signals/technical.py obv block | mirror | obv < obv_ma | as obv_bullish, mirrored | counted on the mirrored leg - tighter margins on persisted obv/obv_ma | looser; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | PRODUCER | obv_bullish - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | OBV vs its moving average (technical.py:1570) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P6.x) | BANDS-DEFINED |
| P6.1 | BAND | obv vs its moving average - backtest/signals/technical.py:1570 | BRACKET the shipped span | obv > obv_ma | MA span [10, 20, 50] | offline 0 of 3 levels - none - obv_ma at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6.2 | BAND | margin pct over the MA - technical.py:1570 | BRACKET zero | 0.0 | [0, 1, 2] pct | offline 2 of 3 levels - TIGHTER margins where obv and obv_ma are persisted | LOOSER; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | PRODUCER | resistance_break_retest - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P7.x) | BANDS-DEFINED |
| P7.1 | BAND | breakout clearance - the breakout bar closed beyond the level by c x ATR(14) - backtest/signals/technical.py compute_break_retest_signals | BRACKET production; 0.5 is the shipped B594 strong variant | 0.0 | 0, 0.5, 1 | offline 1 of 3 levels - TIGHTER (0.5) - the persisted dc20_resistance_break_retest_strong, set only inside the same hold check, so a subset of the leg: True on 599 of 862 dc20_break_retest and 532 of 765 break_retest_volume R5 long fires | 1.0 - tighter but unpersisted, engine-only; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7.2 | BAND | retest tolerance - a later bar's low within t x ATR(14) of the level - backtest/signals/technical.py compute_break_retest_signals | BRACKET production | 1.5 | 1, 1.5, 2 | offline 0 of 3 levels - none - the post-break bars are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7.3 | BAND | breakout window - lag 2 to N bars ago, and the close-based lookback that sets the level - backtest/signals/technical.py compute_break_retest_signals | BRACKET production | lag 2-8 / lookback 20 | lag max [5, 8, 12]; lookback [10, 20, 50] | offline 0 of 3, 0 of 3 levels - none - the earlier bars are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P8 | PRODUCER | support_break_retest - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | a close-based 20-bar high / low broken 2-8 bars ago, a later bar retesting it within 1.5 x ATR(14), today's close still beyond it (technical.py compute_break_retest_signals) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P8.x) | BANDS-DEFINED |
| P8.1 | BAND | mirror of resistance_break_retest (the close-based low; the same clearance, tolerance and window) - backtest/signals/technical.py compute_break_retest_signals | mirror | as resistance_break_retest | as long, mirrored | counted on the mirrored leg - TIGHTER clearance 0.5 - the persisted dc20_support_break_retest_strong: True on 1121 of 1552 dc20_break_retest and 1009 of 1399 break_retest_volume R5 short fires | the rest - mirrored; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P9 | PRODUCER | vol_below_avg - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average < 1.0 (technical.py compute_volume) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P9.x) | BANDS-DEFINED |
| P9.1 | BAND | volume ratio ceiling (vol / avg, strict <) - backtest/signals/technical.py compute_volume | MEASURED - production 1.0 (B594, the retest dry-up); levels near the R5 fires' vol_ratio_20d (q20 0.65, q60 0.83 on both consumers); avg window is the second knob [10, 20, 50] | 1.0 | 0.6, 0.8, 1 | offline 2 of 3 levels - TIGHTER ceilings (0.8, 0.6) on the persisted vol_ratio_20d, which is rounded to 2 dp - a level is blurred by 0.005 either way (the rounding already reads 1.00 on 23 of 2414 and 22 of 2164 R5 fires the strict production gate admitted) | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P10 | STRATEGY | ppo_hist `>= -0.2823` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= -0.2823` | production + 4 tighter measured levels | offline 4 of 5 levels - measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P11 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| ppo_hist | backtest/signals/technical.py | `>= -0.2823` | 100.0% | TIGHTER = RAISE the floor: -0.0865 -> 858 (80%); 0.3046 -> 644 (60%); 0.7281 -> 429 (40%); 1.1451 -> 215 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 17.454, 21.186, 25.52, 31.824 | 17.454: 858 (80%); 21.186: 644 (60%); 25.52: 430 (40%); 31.824: 215 (20%) | 17.454: 215 (20%); 21.186: 429 (40%); 25.52: 646 (60%); 31.824: 858 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 15.744, 18.92, 22.23, 26.192 | 15.744: 858 (80%); 18.92: 645 (60%); 22.23: 430 (40%); 26.192: 215 (20%) | 15.744: 215 (20%); 18.92: 430 (40%); 22.23: 645 (60%); 26.192: 858 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 17.746, 23.972, 27.404, 31.416 | 17.746: 858 (80%); 23.972: 644 (60%); 27.404: 429 (40%); 31.416: 215 (20%) | 17.746: 215 (20%); 23.972: 429 (40%); 27.404: 644 (60%); 31.416: 858 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -3.5953, 0.6175, 2.4709, 6.3037 | -3.5953: 858 (80%); 0.6175: 644 (60%); 2.4709: 429 (40%); 6.3037: 215 (20%) | -3.5953: 215 (20%); 0.6175: 429 (40%); 2.4709: 644 (60%); 6.3037: 858 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.0189, 1.7795, 3.0237, 5.4843 | 1.0189: 858 (80%); 1.7795: 644 (60%); 3.0237: 429 (40%); 5.4843: 215 (20%) | 1.0189: 215 (20%); 1.7795: 429 (40%); 3.0237: 644 (60%); 5.4843: 858 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.0189, 1.7795, 3.0237, 5.4843 | 1.0189: 858 (80%); 1.7795: 644 (60%); 3.0237: 429 (40%); 5.4843: 215 (20%) | 1.0189: 215 (20%); 1.7795: 429 (40%); 3.0237: 644 (60%); 5.4843: 858 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.9894, 2.4218, 2.8342, 3.599 | 1.9894: 858 (80%); 2.4218: 644 (60%); 2.8342: 429 (40%); 3.599: 216 (20%) | 1.9894: 215 (20%); 2.4218: 429 (40%); 2.8342: 644 (60%); 3.599: 859 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0522, 0.076, 0.1062, 0.1557 | 0.0522: 859 (80%); 0.076: 644 (60%); 0.1062: 430 (40%); 0.1557: 216 (20%) | 0.0522: 218 (20%); 0.076: 429 (40%); 0.1062: 645 (60%); 0.1557: 859 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.4264, 0.6039, 0.7489, 0.8544 | 0.4264: 858 (80%); 0.6039: 644 (60%); 0.7489: 429 (40%); 0.8544: 215 (20%) | 0.4264: 215 (20%); 0.6039: 429 (40%); 0.7489: 644 (60%); 0.8544: 858 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0664, 0.0891, 0.1156, 0.1532 | 0.0664: 859 (80%); 0.0891: 644 (60%); 0.1156: 429 (40%); 0.1532: 215 (20%) | 0.0664: 217 (20%); 0.0891: 430 (40%); 0.1156: 644 (60%); 0.1532: 859 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2341, 0.795, 0.9601, 1.0963 | 0.2341: 859 (80%); 0.795: 644 (60%); 0.9601: 429 (40%); 1.0963: 215 (20%) | 0.2341: 215 (20%); 0.795: 429 (40%); 0.9601: 644 (60%); 1.0963: 858 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0885, 0.1188, 0.1542, 0.2042 | 0.0885: 859 (80%); 0.1188: 644 (60%); 0.1542: 429 (40%); 0.2042: 215 (20%) | 0.0885: 217 (20%); 0.1188: 430 (40%); 0.1542: 644 (60%); 0.2042: 859 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.3006, 0.7213, 0.8451, 0.9472 | 0.3006: 859 (80%); 0.7213: 644 (60%); 0.8451: 429 (40%); 0.9472: 215 (20%) | 0.3006: 215 (20%); 0.7213: 429 (40%); 0.8451: 644 (60%); 0.9472: 858 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0553, -0.0319, -0.0099, 0.0175 | -0.0553: 859 (80%); -0.0319: 644 (60%); -0.0099: 430 (40%); 0.0175: 216 (20%) | -0.0553: 217 (20%); -0.0319: 432 (40%); -0.0099: 646 (60%); 0.0175: 860 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1447, 0.1708, 0.2223, 0.2621 | 0.1447: 856 (80%); 0.1708: 642 (60%); 0.2223: 431 (40%); 0.2621: 220 (21%) | 0.1447: 217 (20%); 0.1708: 431 (40%); 0.2223: 642 (60%); 0.2621: 853 (79%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1073 (100%) | 0: 1002 (93%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0686, 0.0319, 0.1059, 0.1898 | -0.0686: 858 (80%); 0.0319: 644 (60%); 0.1059: 429 (40%); 0.1898: 215 (20%) | -0.0686: 215 (20%); 0.0319: 430 (40%); 0.1059: 644 (60%); 0.1898: 858 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1073 (100%); 1: 428 (40%) | 0: 645 (60%); 1: 881 (82%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2396, -0.1944, -0.1509, -0.1197 | -0.2396: 861 (80%); -0.1944: 644 (60%); -0.1509: 430 (40%); -0.1197: 217 (20%) | -0.2396: 221 (21%); -0.1944: 429 (40%); -0.1509: 664 (62%); -0.1197: 867 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4167, 0.6269, 0.7244, 0.7756 | 0.4167: 869 (81%); 0.6269: 644 (60%); 0.7244: 435 (41%); 0.7756: 218 (20%) | 0.4167: 224 (21%); 0.6269: 429 (40%); 0.7244: 667 (62%); 0.7756: 866 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.3846, 0.5897, 0.8333 | 0.2628: 867 (81%); 0.3846: 654 (61%); 0.5897: 445 (41%); 0.8333: 225 (21%) | 0.2628: 259 (24%); 0.3846: 434 (40%); 0.5897: 646 (60%); 0.8333: 870 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0929, 0.0195, 0.0997, 0.254 | -0.0929: 860 (80%); 0.0195: 649 (60%); 0.0997: 431 (40%); 0.254: 222 (21%) | -0.0929: 215 (20%); 0.0195: 442 (41%); 0.0997: 646 (60%); 0.254: 864 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.4872, 0.6538, 0.8397 | 0.2628: 865 (81%); 0.4872: 662 (62%); 0.6538: 434 (40%); 0.8397: 223 (21%) | 0.2628: 218 (20%); 0.4872: 430 (40%); 0.6538: 645 (60%); 0.8397: 861 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.109, 0.25, 0.4487, 0.6218 | 0.109: 859 (80%); 0.25: 646 (60%); 0.4487: 432 (40%); 0.6218: 218 (20%) | 0.109: 221 (21%); 0.25: 460 (43%); 0.4487: 654 (61%); 0.6218: 878 (82%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.531, -0.4146, -0.2179, 0.0586 | -0.531: 865 (81%); -0.4146: 646 (60%); -0.2179: 446 (42%); 0.0586: 215 (20%) | -0.531: 223 (21%); -0.4146: 439 (41%); -0.2179: 645 (60%); 0.0586: 858 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2885, 0.4679, 0.609, 0.9167 | 0.2885: 861 (80%); 0.4679: 666 (62%); 0.609: 441 (41%); 0.9167: 230 (21%) | 0.2885: 221 (21%); 0.4679: 442 (41%); 0.609: 645 (60%); 0.9167: 890 (83%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2051, 0.4295, 0.5897, 0.8782 | 0.2051: 875 (82%); 0.4295: 659 (61%); 0.5897: 442 (41%); 0.8782: 218 (20%) | 0.2051: 216 (20%); 0.4295: 442 (41%); 0.5897: 654 (61%); 0.8782: 870 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0655, -0.0588, -0.0412, 0 | -0.0655: 870 (81%); -0.0588: 647 (60%); -0.0412: 443 (41%); 0: 284 (26%) | -0.0655: 215 (20%); -0.0588: 455 (42%); -0.0412: 656 (61%); 0: 1038 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.7051, 0.8718, 1 | 0.391: 877 (82%); 0.7051: 662 (62%); 0.8718: 460 (43%); 1: 218 (20%) | 0.391: 233 (22%); 0.7051: 431 (40%); 0.8718: 649 (60%); 1: 1073 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1218, 0.2179, 0.5705, 0.9077 | 0.1218: 859 (80%); 0.2179: 658 (61%); 0.5705: 456 (42%); 0.9077: 215 (20%) | 0.1218: 221 (21%); 0.2179: 449 (42%); 0.5705: 646 (60%); 0.9077: 858 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0289, 0.0229, 0.0608, 0.1869 | -0.0289: 865 (81%); 0.0229: 650 (61%); 0.0608: 430 (40%); 0.1869: 217 (20%) | -0.0289: 223 (21%); 0.0229: 434 (40%); 0.0608: 647 (60%); 0.1869: 859 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3846, 0.7429, 0.8966, 0.9679 | 0.3846: 859 (80%); 0.7429: 653 (61%); 0.8966: 431 (40%); 0.9679: 246 (23%) | 0.3846: 218 (20%); 0.7429: 445 (41%); 0.8966: 648 (60%); 0.9679: 891 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0952, 0.3077, 0.6154, 0.8372 | 0.0952: 859 (80%); 0.3077: 646 (60%); 0.6154: 431 (40%); 0.8372: 219 (20%) | 0.0952: 239 (22%); 0.3077: 432 (40%); 0.6154: 647 (60%); 0.8372: 860 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0184, 0.0917, 0.1876 | -0.0812: 909 (85%); -0.0184: 644 (60%); 0.0917: 430 (40%); 0.1876: 268 (25%) | -0.0812: 308 (29%); -0.0184: 429 (40%); 0.0917: 645 (60%); 0.1876: 875 (82%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1695, -0.0343, 0.0356, 0.0869 | -0.1695: 859 (80%); -0.0343: 650 (61%); 0.0356: 433 (40%); 0.0869: 216 (20%) | -0.1695: 218 (20%); -0.0343: 433 (40%); 0.0356: 645 (60%); 0.0869: 864 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.5321, 0.7179, 0.859 | 0.2628: 864 (81%); 0.5321: 647 (60%); 0.7179: 435 (41%); 0.859: 218 (20%) | 0.2628: 223 (21%); 0.5321: 441 (41%); 0.7179: 653 (61%); 0.859: 879 (82%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2115, 0.4103, 0.6026, 0.8462 | 0.2115: 865 (81%); 0.4103: 660 (62%); 0.6026: 432 (40%); 0.8462: 221 (21%) | 0.2115: 219 (20%); 0.4103: 441 (41%); 0.6026: 653 (61%); 0.8462: 861 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0467, 0.1102, 0.1994, 0.4172 | 0.0467: 859 (80%); 0.1102: 644 (60%); 0.1994: 429 (40%); 0.4172: 215 (20%) | 0.0467: 221 (21%); 0.1102: 430 (40%); 0.1994: 644 (60%); 0.4172: 858 (80%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.4% | 1.6673, 2.2602, 2.8348, 3.7966 | 1.6673: 853 (79%); 2.2602: 640 (60%); 2.8348: 427 (40%); 3.7966: 214 (20%) | 1.6673: 214 (20%); 2.2602: 427 (40%); 2.8348: 640 (60%); 3.7966: 853 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 8, 20, 27, 34 | 8: 881 (82%); 20: 645 (60%); 27: 454 (42%); 34: 250 (23%) | 8: 227 (21%); 20: 467 (44%); 27: 671 (63%); 34: 867 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 0, 1, 2, 3 | 0: 1073 (100%); 1: 844 (79%); 2: 633 (59%); 3: 417 (39%) | 0: 229 (21%); 1: 440 (41%); 2: 656 (61%); 3: 903 (84%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0193, -0.0086, 0.0047, 0.0193 | -0.0193: 859 (80%); -0.0086: 644 (60%); 0.0047: 430 (40%); 0.0193: 215 (20%) | -0.0193: 219 (20%); -0.0086: 435 (41%); 0.0047: 645 (60%); 0.0193: 859 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5095, 25.4036, 26.3791, 27.0536 | 24.5095: 859 (80%); 25.4036: 646 (60%); 26.3791: 437 (41%); 27.0536: 215 (20%) | 24.5095: 217 (20%); 25.4036: 432 (40%); 26.3791: 646 (60%); 27.0536: 858 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.5456, -0.094, 0.2152, 0.7006 | -0.5456: 858 (80%); -0.094: 645 (60%); 0.2152: 429 (40%); 0.7006: 215 (20%) | -0.5456: 215 (20%); -0.094: 430 (40%); 0.2152: 644 (60%); 0.7006: 858 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.7006, -0.2152, 0.094, 0.5456 | -0.7006: 858 (80%); -0.2152: 644 (60%); 0.094: 430 (40%); 0.5456: 215 (20%) | -0.7006: 215 (20%); -0.2152: 429 (40%); 0.094: 645 (60%); 0.5456: 858 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0553, -0.0214, 0.011, 0.0565 | -0.0553: 859 (80%); -0.0214: 645 (60%); 0.011: 430 (40%); 0.0565: 216 (20%) | -0.0553: 217 (20%); -0.0214: 430 (40%); 0.011: 644 (60%); 0.0565: 861 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0696, 8.4446, 8.6916, 9.0853 | 8.0696: 858 (80%); 8.4446: 642 (60%); 8.6916: 428 (40%); 9.0853: 214 (20%) | 8.0696: 215 (20%); 8.4446: 431 (40%); 8.6916: 645 (60%); 9.0853: 859 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1063 (99%); 1: 351 (33%) | 0: 712 (66%); 1: 937 (87%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | -1, 0 | -1: 1005 (94%); 0: 837 (78%) | -1: 226 (21%); 0: 890 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1063 (99%); 1: 388 (36%) | 0: 675 (63%); 1: 920 (86%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 1, 5, 12, 235.6 | 1: 921 (86%); 5: 656 (61%); 12: 430 (40%); 235.6: 215 (20%) | 1: 219 (20%); 5: 483 (45%); 12: 647 (60%); 235.6: 858 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 0, 3, 67, 124 | 0: 1073 (100%); 3: 650 (61%); 67: 430 (40%); 124: 216 (20%) | 0: 250 (23%); 3: 479 (45%); 67: 645 (60%); 124: 863 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.0369, 0.1942, 0.4517, 1.0847 | -0.0369: 858 (80%); 0.1942: 644 (60%); 0.4517: 429 (40%); 1.0847: 215 (20%) | -0.0369: 215 (20%); 0.1942: 429 (40%); 0.4517: 644 (60%); 1.0847: 858 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.5699, 0.0063, 0.5682, 1.8269 | -1.5699: 858 (80%); 0.0063: 644 (60%); 0.5682: 429 (40%); 1.8269: 215 (20%) | -1.5699: 215 (20%); 0.0063: 429 (40%); 0.5682: 644 (60%); 1.8269: 858 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.8752, -0.5514, 0.0266, 0.9826 | -1.8752: 858 (80%); -0.5514: 644 (60%); 0.0266: 429 (40%); 0.9826: 215 (20%) | -1.8752: 215 (20%); -0.5514: 429 (40%); 0.0266: 644 (60%); 0.9826: 858 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.0018, 0.1147, 0.2795, 0.7031 | -0.0018: 858 (80%); 0.1147: 644 (60%); 0.2795: 430 (40%); 0.7031: 215 (20%) | -0.0018: 215 (20%); 0.1147: 430 (40%); 0.2795: 644 (60%); 0.7031: 858 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.4519, 0.3032, 1.0777, 2.7073 | -1.4519: 858 (80%); 0.3032: 644 (60%); 1.0777: 429 (40%); 2.7073: 215 (20%) | -1.4519: 215 (20%); 0.3032: 429 (40%); 1.0777: 644 (60%); 2.7073: 858 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.5872, 0.1226, 0.7865, 2.1648 | -1.5872: 858 (80%); 0.1226: 644 (60%); 0.7865: 429 (40%); 2.1648: 215 (20%) | -1.5872: 215 (20%); 0.1226: 429 (40%); 0.7865: 644 (60%); 2.1648: 858 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 43.074, 54.798, 63.182, 71.114 | 43.074: 858 (80%); 54.798: 644 (60%); 63.182: 429 (40%); 71.114: 215 (20%) | 43.074: 215 (20%); 54.798: 429 (40%); 63.182: 644 (60%); 71.114: 858 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 98.0% | -0.1707, -0.0894, -0.0192, 0.0588 | -0.1707: 842 (78%); -0.0894: 631 (59%); -0.0192: 421 (39%); 0.0588: 211 (20%) | -0.1707: 211 (20%); -0.0894: 421 (39%); -0.0192: 632 (59%); 0.0588: 841 (78%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.3% | 0.0076, 0.0163, 0.0291, 0.0506 | 0.0076: 855 (80%); 0.0163: 637 (59%); 0.0291: 423 (39%); 0.0506: 213 (20%) | 0.0076: 210 (20%); 0.0163: 428 (40%); 0.0291: 642 (60%); 0.0506: 852 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 1073 (100%); 2: 673 (63%); 4: 450 (42%); 9: 218 (20%) | 0: 238 (22%); 2: 537 (50%); 4: 696 (65%); 9: 877 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1492 | 0: 1073 (100%); 0.1492: 215 (20%) | 0: 734 (68%); 0.1492: 858 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.197, 0.4225, 0.6667 | 0: 1073 (100%); 0.197: 644 (60%); 0.4225: 429 (40%); 0.6667: 232 (22%) | 0: 398 (37%); 0.197: 429 (40%); 0.4225: 644 (60%); 0.6667: 880 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 6 | 0: 1073 (100%); 1: 775 (72%); 3: 442 (41%); 6: 232 (22%) | 0: 298 (28%); 1: 502 (47%); 3: 718 (67%); 6: 879 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 1073 (100%); 2: 673 (63%); 4: 450 (42%); 9: 218 (20%) | 0: 238 (22%); 2: 537 (50%); 4: 696 (65%); 9: 877 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1073 (100%); 1: 786 (73%); 3: 496 (46%); 8: 233 (22%) | 0: 287 (27%); 1: 459 (43%); 3: 663 (62%); 8: 882 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2222, 0.3505, 0.578 | 0: 987 (92%); 0.2222: 647 (60%); 0.3505: 429 (40%); 0.578: 215 (20%) | 0: 219 (20%); 0.2222: 431 (40%); 0.3505: 644 (60%); 0.578: 858 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1568, 0.5833 | 0: 980 (91%); 0.1568: 429 (40%); 0.5833: 218 (20%) | 0: 583 (54%); 0.1568: 644 (60%); 0.5833: 860 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2883, 0.5714 | 0: 983 (92%); 0.2883: 429 (40%); 0.5714: 218 (20%) | 0: 467 (44%); 0.2883: 644 (60%); 0.5714: 859 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2883, 0.5714 | 0: 983 (92%); 0.2883: 429 (40%); 0.5714: 218 (20%) | 0: 467 (44%); 0.2883: 644 (60%); 0.5714: 859 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1882, 0, 0.1667 | -0.1882: 858 (80%); 0: 755 (70%); 0.1667: 217 (20%) | -0.1882: 215 (20%); 0: 749 (70%); 0.1667: 869 (81%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.757, -0.3053, 0.1893, 1.2596 | -0.757: 858 (80%); -0.3053: 645 (60%); 0.1893: 432 (40%); 1.2596: 215 (20%) | -0.757: 215 (20%); -0.3053: 430 (40%); 0.1893: 645 (60%); 1.2596: 858 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 5, 7, 12 | 2: 928 (86%); 5: 654 (61%); 7: 484 (45%); 12: 217 (20%) | 2: 240 (22%); 5: 513 (48%); 7: 657 (61%); 12: 887 (83%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0235, 0.0247, 0.0558, 0.092 | -0.0235: 859 (80%); 0.0247: 644 (60%); 0.0558: 428 (40%); 0.092: 215 (20%) | -0.0235: 214 (20%); 0.0247: 429 (40%); 0.0558: 645 (60%); 0.092: 858 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0501, 0.0409, 0.0779, 0.12 | -0.0501: 858 (80%); 0.0409: 644 (60%); 0.0779: 429 (40%); 0.12: 215 (20%) | -0.0501: 215 (20%); 0.0409: 429 (40%); 0.0779: 644 (60%); 0.12: 858 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0098, 0.0087, 0.026, 0.0549 | -0.0098: 858 (80%); 0.0087: 642 (60%); 0.026: 429 (40%); 0.0549: 215 (20%) | -0.0098: 215 (20%); 0.0087: 431 (40%); 0.026: 644 (60%); 0.0549: 858 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -20.9654, -9.556, -1.1652, 11.7152 | -20.9654: 858 (80%); -9.556: 644 (60%); -1.1652: 429 (40%); 11.7152: 215 (20%) | -20.9654: 215 (20%); -9.556: 429 (40%); -1.1652: 644 (60%); 11.7152: 858 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0381, 0.052, 0.0687, 0.0939 | 0.0381: 862 (80%); 0.052: 646 (60%); 0.0687: 430 (40%); 0.0939: 217 (20%) | 0.0381: 216 (20%); 0.052: 430 (40%); 0.0687: 644 (60%); 0.0939: 859 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.2437, 0.6746, 0.8043, 0.9111 | 0.2437: 858 (80%); 0.6746: 644 (60%); 0.8043: 429 (40%); 0.9111: 216 (20%) | 0.2437: 215 (20%); 0.6746: 429 (40%); 0.8043: 644 (60%); 0.9111: 859 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.6484, 0.0079, 0.9199, 1.949 | -1.6484: 858 (80%); 0.0079: 644 (60%); 0.9199: 429 (40%); 1.949: 215 (20%) | -1.6484: 215 (20%); 0.0079: 429 (40%); 0.9199: 644 (60%); 1.949: 859 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -1.9149, -0.7543, 0.0674, 1.2853 | -1.9149: 858 (80%); -0.7543: 644 (60%); 0.0674: 429 (40%); 1.2853: 215 (20%) | -1.9149: 215 (20%); -0.7543: 429 (40%); 0.0674: 644 (60%); 1.2853: 858 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -2.8958, 3.0048, 6.1412, 9.7512 | -2.8958: 858 (80%); 3.0048: 644 (60%); 6.1412: 429 (40%); 9.7512: 215 (20%) | -2.8958: 215 (20%); 3.0048: 429 (40%); 6.1412: 644 (60%); 9.7512: 858 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.282, 54.916, 59.874, 64.398 | 41.282: 858 (80%); 54.916: 644 (60%); 59.874: 429 (40%); 64.398: 215 (20%) | 41.282: 215 (20%); 54.916: 429 (40%); 59.874: 644 (60%); 64.398: 858 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 35.252, 57.354, 76.26, 90.082 | 35.252: 858 (80%); 57.354: 644 (60%); 76.26: 429 (40%); 90.082: 215 (20%) | 35.252: 215 (20%); 57.354: 429 (40%); 76.26: 644 (60%); 90.082: 858 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 42.288, 51.118, 55.622, 59.646 | 42.288: 858 (80%); 51.118: 644 (60%); 55.622: 429 (40%); 59.646: 215 (20%) | 42.288: 215 (20%); 51.118: 429 (40%); 55.622: 644 (60%); 59.646: 858 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.504, 57.99, 64.51, 70.16 | 41.504: 858 (80%); 57.99: 644 (60%); 64.51: 430 (40%); 70.16: 217 (20%) | 41.504: 215 (20%); 57.99: 429 (40%); 64.51: 646 (60%); 70.16: 859 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1069 (100%) | 0: 1073 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.032, 0.0467, 0.0588, 0.0804 | 0.032: 859 (80%); 0.0467: 644 (60%); 0.0588: 432 (40%); 0.0804: 215 (20%) | 0.032: 215 (20%); 0.0467: 429 (40%); 0.0588: 646 (60%); 0.0804: 858 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0914, -0.0682, -0.0516, -0.0363 | -0.0914: 860 (80%); -0.0682: 644 (60%); -0.0516: 430 (40%); -0.0363: 216 (20%) | -0.0914: 217 (20%); -0.0682: 430 (40%); -0.0516: 646 (60%); -0.0363: 861 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1073 (100%); 1: 287 (27%) | 0: 786 (73%); 1: 891 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.4% | 25.2, 37, 53, 67.8 | 25.2: 853 (79%); 37: 656 (61%); 53: 446 (42%); 67.8: 214 (20%) | 25.2: 214 (20%); 37: 443 (41%); 53: 643 (60%); 67.8: 853 (79%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.3% | 0.0113, 0.0166, 0.0245, 0.0398 | 0.0113: 846 (79%); 0.0166: 632 (59%); 0.0245: 422 (39%); 0.0398: 212 (20%) | 0.0113: 209 (19%); 0.0166: 423 (39%); 0.0245: 633 (59%); 0.0398: 843 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 99.8% | 0.2038, 0.4612, 0.6409, 0.8681 | 0.2038: 857 (80%); 0.4612: 643 (60%); 0.6409: 429 (40%); 0.8681: 215 (20%) | 0.2038: 215 (20%); 0.4612: 429 (40%); 0.6409: 643 (60%); 0.8681: 857 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 99.8% | 31, 54.1, 74.9, 108.3 | 31: 857 (80%); 54.1: 643 (60%); 74.9: 429 (40%); 108.3: 215 (20%) | 31: 216 (20%); 54.1: 429 (40%); 74.9: 643 (60%); 108.3: 857 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -1.931, 1.21, 3.113, 6.947 | -1.931: 858 (80%); 1.21: 644 (60%); 3.113: 429 (40%); 6.947: 215 (20%) | -1.931: 215 (20%); 1.21: 429 (40%); 3.113: 644 (60%); 6.947: 858 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 35.288, 68.142, 82.03, 88.716 | 35.288: 858 (80%); 68.142: 644 (60%); 82.03: 430 (40%); 88.716: 215 (20%) | 35.288: 215 (20%); 68.142: 429 (40%); 82.03: 646 (60%); 88.716: 858 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 37.642, 65.68, 82.39, 90.78 | 37.642: 858 (80%); 65.68: 644 (60%); 82.39: 429 (40%); 90.78: 215 (20%) | 37.642: 215 (20%); 65.68: 429 (40%); 82.39: 644 (60%); 90.78: 858 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 38.454, 65.27, 83.224, 95 | 38.454: 858 (80%); 65.27: 645 (60%); 83.224: 429 (40%); 95: 215 (20%) | 38.454: 215 (20%); 65.27: 430 (40%); 83.224: 644 (60%); 95: 858 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 35.698, 65.856, 85.098, 100 | 35.698: 858 (80%); 65.856: 644 (60%); 85.098: 429 (40%); 100: 252 (23%) | 35.698: 215 (20%); 65.856: 429 (40%); 85.098: 644 (60%); 100: 1073 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 17 | 5: 869 (81%); 9: 676 (63%); 13: 432 (40%); 17: 218 (20%) | 5: 265 (25%); 9: 445 (41%); 13: 711 (66%); 17: 907 (85%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 17 | 5: 888 (83%); 9: 698 (65%); 13: 430 (40%); 17: 260 (24%) | 5: 234 (22%); 9: 441 (41%); 13: 687 (64%); 17: 868 (81%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 47.87, 53.922, 58.864, 64.328 | 47.87: 859 (80%); 53.922: 644 (60%); 58.864: 429 (40%); 64.328: 215 (20%) | 47.87: 216 (20%); 53.922: 429 (40%); 58.864: 644 (60%); 64.328: 858 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0913, 0.3135, 0.5437, 0.7817 | 0.0913: 861 (80%); 0.3135: 645 (60%); 0.5437: 444 (41%); 0.7817: 218 (20%) | 0.0913: 216 (20%); 0.3135: 432 (40%); 0.5437: 650 (61%); 0.7817: 861 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.75, 17.03, 19.5, 23.93 | 14.75: 859 (80%); 17.03: 647 (60%); 19.5: 430 (40%); 23.93: 226 (21%) | 14.75: 216 (20%); 17.03: 430 (40%); 19.5: 645 (60%); 23.93: 860 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.75, 17.03, 19.5, 23.93 | 14.75: 859 (80%); 17.03: 647 (60%); 19.5: 430 (40%); 23.93: 226 (21%) | 14.75: 216 (20%); 17.03: 430 (40%); 19.5: 645 (60%); 23.93: 860 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8473, 0.8786, 0.9067, 0.9465 | 0.8473: 858 (80%); 0.8786: 650 (61%); 0.9067: 431 (40%); 0.9465: 219 (20%) | 0.8473: 215 (20%); 0.8786: 433 (40%); 0.9067: 644 (60%); 0.9465: 859 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.64, 0.73, 0.81, 0.9 | 0.64: 866 (81%); 0.73: 655 (61%); 0.81: 457 (43%); 0.9: 219 (20%) | 0.64: 224 (21%); 0.73: 435 (41%); 0.81: 645 (60%); 0.9: 869 (81%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 99.9% | 0.0237, 0.0481, 0.0769, 0.1183 | 0.0237: 857 (80%); 0.0481: 644 (60%); 0.0769: 430 (40%); 0.1183: 215 (20%) | 0.0237: 215 (20%); 0.0481: 430 (40%); 0.0769: 644 (60%); 0.1183: 857 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 45.8018, 78.9229, 122.6507, 210.9691 | 45.8018: 858 (80%); 78.9229: 644 (60%); 122.6507: 429 (40%); 210.9691: 215 (20%) | 45.8018: 215 (20%); 78.9229: 429 (40%); 122.6507: 644 (60%); 210.9691: 858 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 44.1458, 75.9872, 118.6462, 203.3981 | 44.1458: 858 (80%); 75.9872: 644 (60%); 118.6462: 429 (40%); 203.3981: 215 (20%) | 44.1458: 215 (20%); 75.9872: 429 (40%); 118.6462: 644 (60%); 203.3981: 858 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 42.5764, 73.2262, 114.0797, 196.2919 | 42.5764: 858 (80%); 73.2262: 644 (60%); 114.0797: 429 (40%); 196.2919: 215 (20%) | 42.5764: 215 (20%); 73.2262: 429 (40%); 114.0797: 644 (60%); 196.2919: 858 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.3626, 81.5598, 127.1623, 218.1248 | 47.3626: 858 (80%); 81.5598: 644 (60%); 127.1623: 429 (40%); 218.1248: 215 (20%) | 47.3626: 215 (20%); 81.5598: 429 (40%); 127.1623: 644 (60%); 218.1248: 858 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.8473, 83.6618, 131.7465, 224.0839 | 48.8473: 858 (80%); 83.6618: 644 (60%); 131.7465: 429 (40%); 224.0839: 215 (20%) | 48.8473: 215 (20%); 83.6618: 429 (40%); 131.7465: 644 (60%); 224.0839: 858 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1073 (100%) | 0: 941 (88%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1073 (100%) | 0: 954 (89%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.8% | -0.0421, 0.0399, 0.0749, 0.1157 | -0.0421: 857 (80%); 0.0399: 643 (60%); 0.0749: 429 (40%); 0.1157: 217 (20%) | -0.0421: 215 (20%); 0.0399: 429 (40%); 0.0749: 643 (60%); 0.1157: 857 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -64.638, -32.69, -14.718, -5.224 | -64.638: 858 (80%); -32.69: 644 (60%); -14.718: 429 (40%); -5.224: 215 (20%) | -64.638: 215 (20%); -32.69: 429 (40%); -14.718: 644 (60%); -5.224: 858 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.9% | 0.5373, 0.7864, 1.0235, 1.2999 | 0.5373: 849 (79%); 0.7864: 637 (59%); 1.0235: 425 (40%); 1.2999: 213 (20%) | 0.5373: 213 (20%); 0.7864: 425 (40%); 1.0235: 637 (59%); 1.2999: 849 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.9% | 3, 5, 7, 9 | 3: 862 (80%); 5: 665 (62%); 7: 457 (43%); 9: 247 (23%) | 3: 294 (27%); 5: 500 (47%); 7: 701 (65%); 9: 935 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 98.8% | 0.1897, 0.2275, 0.2751, 0.3632 | 0.1897: 848 (79%); 0.2275: 636 (59%); 0.2751: 425 (40%); 0.3632: 212 (20%) | 0.1897: 213 (20%); 0.2275: 424 (40%); 0.2751: 637 (59%); 0.3632: 848 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 98.8% | 3, 5, 7, 9 | 3: 881 (82%); 5: 713 (66%); 7: 498 (46%); 9: 284 (26%) | 3: 268 (25%); 5: 454 (42%); 7: 652 (61%); 9: 883 (82%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 98.9% | 0.024, 0.0338, 0.0446, 0.0691 | 0.024: 849 (79%); 0.0338: 638 (59%); 0.0446: 425 (40%); 0.0691: 213 (20%) | 0.024: 217 (20%); 0.0338: 425 (40%); 0.0446: 637 (59%); 0.0691: 849 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 98.9% | 3, 5, 7, 9 | 3: 882 (82%); 5: 702 (65%); 7: 505 (47%); 9: 286 (27%) | 3: 266 (25%); 5: 456 (42%); 7: 655 (61%); 9: 876 (82%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.1% | -0.2878, -0.1574, -0.0396, 0.1008 | -0.2878: 850 (79%); -0.1574: 638 (59%); -0.0396: 425 (40%); 0.1008: 213 (20%) | -0.2878: 213 (20%); -0.1574: 425 (40%); -0.0396: 638 (59%); 0.1008: 850 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.1% | 2, 3, 5, 7 | 2: 860 (80%); 3: 709 (66%); 5: 434 (40%); 7: 253 (24%) | 2: 354 (33%); 3: 504 (47%); 5: 718 (67%); 7: 899 (84%) | OFFLINE |
| year_high | backtest/signals/technical.py | 100.0% | 55.857, 93.6216, 153.5, 259.614 | 55.857: 858 (80%); 93.6216: 644 (60%); 153.5: 429 (40%); 259.614: 215 (20%) | 55.857: 215 (20%); 93.6216: 429 (40%); 153.5: 644 (60%); 259.614: 858 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.0% |
| 8k_item_5_02_filed_within_7d | 3.2% |
| above_avwap_20high | 51.8% |
| above_avwap_20low | 84.5% |
| above_avwap_252low | 75.3% |
| above_avwap_50low | 83.0% |
| above_cam_r3 | 43.9% |
| above_cam_r4 | 24.2% |
| above_cpr | 62.7% |
| above_pivot | 63.7% |
| above_prev_high | 29.1% |
| above_prev_high_clearance_atr_05 | 7.9% |
| above_prev_low | 87.0% |
| above_r1 | 25.6% |
| above_r2 | 10.3% |
| above_vwap | 37.6% |
| above_wood_p | 62.6% |
| ad_rising | 67.8% |
| adx_cross_up | 1.3% |
| adx_cross_up_20 | 1.6% |
| adx_di_bear | 34.9% |
| adx_di_bull | 65.1% |
| adx_strong | 7.4% |
| adx_trending | 42.1% |
| ao_cross_up | 3.2% |
| ao_positive | 66.2% |
| ao_twin_peaks_bull | 3.1% |
| at_key_fib | 14.2% |
| at_key_fib_wide | 35.7% |
| avwap_20high_loss_recent_3d | 17.6% |
| avwap_20high_reclaim_recent_3d | 30.7% |
| avwap_20low_loss_recent_3d | 11.7% |
| avwap_20low_reclaim_recent_3d | 9.3% |
| avwap_252low_loss_recent_3d | 4.6% |
| avwap_252low_reclaim_recent_3d | 5.6% |
| avwap_50low_loss_recent_3d | 9.4% |
| avwap_50low_reclaim_recent_3d | 6.1% |
| bb_10_20_above_mid | 73.3% |
| bb_10_20_expanding | 39.0% |
| bb_10_20_pctb_gt_75 | 39.6% |
| bb_10_20_pctb_gt_8 | 30.8% |
| bb_10_20_pctb_gt_85 | 20.6% |
| bb_10_20_pctb_gt_9 | 11.6% |
| bb_10_20_pctb_gt_95 | 5.6% |
| bb_10_20_pctb_lt_05 | 0.7% |
| bb_10_20_pctb_lt_1 | 1.4% |
| bb_10_20_pctb_lt_15 | 2.8% |
| bb_10_20_pctb_lt_2 | 5.3% |
| bb_10_20_pctb_lt_25 | 7.5% |
| bb_10_20_reclaim_from_lower_recent_3d | 1.5% |
| bb_10_20_reclaim_from_upper_recent_3d | 12.5% |
| bb_10_20_squeeze | 43.1% |
| bb_10_20_touch_lower | 2.1% |
| bb_10_20_touch_upper | 6.6% |
| bb_20_15_above_mid | 69.8% |
| bb_20_15_expanding | 59.0% |
| bb_20_15_pctb_gt_75 | 64.9% |
| bb_20_15_pctb_gt_8 | 59.4% |
| bb_20_15_pctb_gt_85 | 54.2% |
| bb_20_15_pctb_gt_9 | 47.9% |
| bb_20_15_pctb_gt_95 | 41.0% |
| bb_20_15_pctb_lt_05 | 4.6% |
| bb_20_15_pctb_lt_1 | 7.8% |
| bb_20_15_pctb_lt_15 | 11.6% |
| bb_20_15_pctb_lt_2 | 15.5% |
| bb_20_15_pctb_lt_25 | 21.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 6.8% |
| bb_20_15_reclaim_from_upper_recent_3d | 17.8% |
| bb_20_15_squeeze | 31.7% |
| bb_20_15_touch_lower | 6.3% |
| bb_20_15_touch_upper | 41.3% |
| bb_20_20_above_mid | 69.8% |
| bb_20_20_expanding | 59.0% |
| bb_20_20_pctb_gt_75 | 55.9% |
| bb_20_20_pctb_gt_8 | 47.9% |
| bb_20_20_pctb_gt_85 | 38.8% |
| bb_20_20_pctb_gt_9 | 29.2% |
| bb_20_20_pctb_gt_95 | 19.8% |
| bb_20_20_pctb_lt_05 | 0.8% |
| bb_20_20_pctb_lt_1 | 1.9% |
| bb_20_20_pctb_lt_15 | 3.8% |
| bb_20_20_pctb_lt_2 | 7.8% |
| bb_20_20_pctb_lt_25 | 12.8% |
| bb_20_20_reclaim_from_lower_recent_3d | 2.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 14.6% |
| bb_20_20_squeeze | 14.0% |
| bb_20_20_touch_lower | 1.2% |
| bb_20_20_touch_upper | 18.6% |
| bearish_engulfing | 3.3% |
| bearish_pin_bar | 2.1% |
| below_avwap_20high | 48.2% |
| below_avwap_20low | 15.5% |
| below_avwap_252low | 24.7% |
| below_avwap_50low | 17.0% |
| below_cam_s3 | 21.1% |
| below_cam_s4 | 11.5% |
| below_cpr | 36.2% |
| below_ema_20 | 30.5% |
| below_ema_200 | 66.6% |
| below_ema_200_break_recent_5d | 4.3% |
| below_ema_20_break_recent_5d | 5.6% |
| below_ema_21 | 30.5% |
| below_ema_21_break_recent_5d | 5.0% |
| below_ema_50 | 41.8% |
| below_ema_50_break_recent_5d | 5.8% |
| below_ema_9 | 28.6% |
| below_ema_9_break_recent_5d | 19.3% |
| below_prev_high | 70.4% |
| below_prev_low | 13.0% |
| below_prev_low_clearance_atr_05 | 2.2% |
| below_s1 | 11.6% |
| below_s2 | 3.8% |
| below_sma_20 | 30.2% |
| below_sma_200 | 68.2% |
| below_sma_21 | 30.2% |
| below_sma_50 | 39.0% |
| below_sma_9 | 27.1% |
| below_vwap | 62.4% |
| blowoff_recent_3d | 0.3% |
| break_52w_high | 0.6% |
| break_52w_high_confirmed_today | 0.3% |
| break_52w_low | 0.1% |
| bullish_engulfing | 7.3% |
| bullish_pin_bar | 5.7% |
| capitulation_recent_3d | 0.7% |
| ceo_buy | 1.4% |
| cfo_buy | 0.6% |
| chandelier_long_bullish | 76.3% |
| chandelier_long_flip_dn | 3.5% |
| chandelier_short_bearish | 36.4% |
| chandelier_short_flip_up | 6.1% |
| close_above_open | 69.8% |
| close_below_open | 30.2% |
| close_in_bottom_40pct_of_range | 30.2% |
| close_in_top_40pct_of_range | 69.8% |
| cluster_buy | 1.0% |
| cmf_cross_dn | 2.7% |
| cmf_cross_up | 7.0% |
| cmf_negative | 32.5% |
| cmf_positive | 67.2% |
| concentrated_sell | 3.8% |
| cpr_narrow | 88.7% |
| cpr_narrow_tight | 25.3% |
| cup_handle_detected | 12.1% |
| cup_handle_neckline_break_retest_long | 9.3% |
| dc10_breakout_dn | 1.9% |
| dc10_breakout_dn_1pct | 5.4% |
| dc10_breakout_up | 18.7% |
| dc10_breakout_up_1pct | 32.5% |
| dc10_new_high | 21.6% |
| dc10_strong_breakout_dn | 0.2% |
| dc10_strong_breakout_up | 4.0% |
| dc20_breakout_dn | 1.7% |
| dc20_breakout_up | 18.3% |
| dc20_new_high | 20.9% |
| dc20_resistance_break_retest_strong | 48.4% |
| dc20_support_break_retest_strong | 20.9% |
| defensive_leadership | 42.3% |
| director_only_buy | 4.2% |
| doji | 3.0% |
| double_bottom_detected | 13.7% |
| double_top_detected | 14.2% |
| dpi_elevated | 57.5% |
| drying_volume_on_down_turn | 30.2% |
| drying_volume_on_up_turn | 69.8% |
| ema_20_50_bearish | 68.9% |
| ema_20_50_bullish | 31.1% |
| ema_20_50_death_cross | 0.1% |
| ema_20_50_golden_cross | 1.8% |
| ema_50_200_bearish | 74.4% |
| ema_50_200_bullish | 25.6% |
| ema_50_200_death_cross | 0.3% |
| ema_50_200_golden_cross | 0.4% |
| ema_9_21_bearish | 31.9% |
| ema_9_21_bullish | 68.1% |
| ema_9_21_death_cross | 0.1% |
| ema_9_21_golden_cross | 3.3% |
| evening_star | 3.0% |
| flag_bear_break_retest_short | 1.4% |
| flag_bear_broke | 1.6% |
| flag_bear_detected | 0.5% |
| flag_bull_break_retest_long | 1.9% |
| flag_bull_broke | 2.0% |
| flag_bull_detected | 0.7% |
| force_index_cross_dn | 2.6% |
| force_index_cross_up | 2.3% |
| force_index_positive | 70.1% |
| gap_dn_1_5pct | 5.3% |
| gap_dn_2pct | 3.0% |
| gap_up_1_5pct | 4.8% |
| gap_up_2pct | 2.6% |
| hammer | 4.0% |
| head_shoulders_bottom_detected | 6.2% |
| head_shoulders_top_detected | 3.0% |
| house_cluster_buy | 4.5% |
| house_cluster_sell | 5.0% |
| htf_aligned_bear | 31.1% |
| htf_aligned_bull | 18.7% |
| htf_disagreement | 5.0% |
| hull_bearish | 24.5% |
| hull_bullish | 75.5% |
| hull_flip_dn | 4.8% |
| hull_flip_up | 5.3% |
| ichi_above_cloud | 34.9% |
| ichi_above_cloud_break_recent_5d | 13.7% |
| ichi_below_cloud | 45.9% |
| ichi_below_cloud_break_recent_5d | 4.3% |
| ichi_cloud_thick | 87.2% |
| ichi_tk_bearish | 33.4% |
| ichi_tk_bullish | 62.7% |
| ichi_tk_cross_dn | 0.4% |
| ichi_tk_cross_up | 2.8% |
| ichi_weekly_above_cloud | 23.3% |
| ichi_weekly_below_cloud | 47.0% |
| ichi_weekly_in_cloud | 29.8% |
| in_reversal_window | 2.1% |
| inside_bar | 15.0% |
| inside_cpr | 3.5% |
| inside_kc | 83.5% |
| insider_cluster_active | 25.0% |
| institutional_buy | 84.0% |
| institutional_negative | 8.1% |
| institutional_persistence_growing | 40.5% |
| institutional_persistence_strong | 56.8% |
| institutional_strong_buy | 73.5% |
| inverted_cup_handle_detected | 13.6% |
| is_friday | 15.8% |
| is_halloween_period | 54.8% |
| is_halloween_period_first_day | 0.2% |
| is_january | 8.5% |
| is_january_extended | 11.6% |
| is_monday | 21.3% |
| is_pre_holiday | 3.9% |
| is_summer_period | 45.2% |
| is_totm_window | 31.1% |
| is_totm_window_first_day | 8.9% |
| is_week_open | 24.0% |
| kc_touch_lower | 2.4% |
| kc_touch_upper | 19.7% |
| large_dollar_buy | 2.2% |
| macd_12_26_9_bearish | 22.9% |
| macd_12_26_9_bullish | 77.1% |
| macd_12_26_9_crossover_dn | 1.8% |
| macd_12_26_9_crossover_up | 3.1% |
| macd_8_21_5_bearish | 20.4% |
| macd_8_21_5_bullish | 79.6% |
| macd_8_21_5_crossover_dn | 4.0% |
| macd_8_21_5_crossover_up | 2.7% |
| marubozu_bear | 0.5% |
| marubozu_bull | 1.4% |
| mfi_broad_overbought | 22.3% |
| mfi_broad_oversold | 5.6% |
| mfi_overbought | 5.3% |
| mfi_oversold | 1.0% |
| monthly_above_sma_12 | 30.2% |
| monthly_above_sma_6 | 35.8% |
| monthly_bias_bear | 54.7% |
| monthly_bias_bull | 20.7% |
| monthly_momentum_pos | 34.1% |
| morning_star | 5.6% |
| near_52w_high | 2.5% |
| near_52w_high_95pct | 5.6% |
| near_52w_high_retest_long | 0.6% |
| near_52w_low | 1.4% |
| near_52w_low_105pct | 5.1% |
| near_52w_low_retest_short | 2.1% |
| near_avwap_20high_atr_05x | 59.6% |
| near_avwap_20high_atr_10x | 80.8% |
| near_avwap_20high_atr_15x | 94.3% |
| near_avwap_20high_atr_20x | 98.7% |
| near_avwap_20low_atr_05x | 24.0% |
| near_avwap_20low_atr_10x | 39.5% |
| near_avwap_20low_atr_15x | 56.8% |
| near_avwap_20low_atr_20x | 72.6% |
| near_avwap_252low_atr_05x | 10.8% |
| near_avwap_252low_atr_10x | 22.0% |
| near_avwap_252low_atr_15x | 33.0% |
| near_avwap_252low_atr_20x | 45.6% |
| near_avwap_50low_atr_05x | 19.1% |
| near_avwap_50low_atr_10x | 30.9% |
| near_avwap_50low_atr_15x | 41.4% |
| near_avwap_50low_atr_20x | 54.6% |
| near_cam_r3 | 21.3% |
| near_cam_s3 | 14.4% |
| near_cam_s4 | 7.5% |
| near_fib_236 | 4.3% |
| near_fib_382 | 5.3% |
| near_fib_500 | 5.3% |
| near_fib_618 | 3.6% |
| near_fib_786 | 4.0% |
| near_pivot | 18.3% |
| near_prev_close | 18.8% |
| near_prev_high | 17.2% |
| near_prev_low | 9.7% |
| near_r1 | 18.0% |
| near_r1_wide | 67.0% |
| near_r2 | 5.4% |
| near_r2_wide | 43.6% |
| near_s1 | 8.3% |
| near_s1_wide | 47.0% |
| near_s2 | 3.2% |
| near_s2_wide | 23.6% |
| near_s3 | 1.2% |
| near_wood_r1 | 13.3% |
| near_wood_s1 | 9.9% |
| news_uses_polygon_score | 21.2% |
| obv_bearish | 30.2% |
| obv_bullish | 69.8% |
| obv_diverge_bull | 7.7% |
| obv_falling | 36.8% |
| obv_rising | 63.2% |
| outside_bar | 10.0% |
| pead_negative_surprise | 18.5% |
| pead_positive_surprise | 16.8% |
| pin_bar | 7.7% |
| po3_accumulation_active | 37.7% |
| po3_bearish | 11.1% |
| po3_bullish | 21.7% |
| po3_manipulation_sweep_down | 6.1% |
| po3_manipulation_sweep_up | 9.7% |
| po3_mmbm_setup | 3.5% |
| po3_mmsm_setup | 1.5% |
| po3_sweep_above_prior_high | 57.2% |
| po3_sweep_below_prior_low | 45.7% |
| ppo_bullish | 74.6% |
| ppo_crossover_dn | 2.0% |
| ppo_crossover_up | 2.8% |
| pre_fomc_d0 | 3.4% |
| pre_fomc_d1 | 2.2% |
| pre_fomc_window | 5.6% |
| price_above_dema | 79.1% |
| price_above_ema_20 | 69.5% |
| price_above_ema_200 | 33.4% |
| price_above_ema_200_break_recent_5d | 11.9% |
| price_above_ema_20_break_recent_5d | 17.4% |
| price_above_ema_21 | 69.5% |
| price_above_ema_21_break_recent_5d | 18.2% |
| price_above_ema_50 | 58.2% |
| price_above_ema_50_break_recent_5d | 24.4% |
| price_above_ema_9 | 71.4% |
| price_above_ema_9_break_recent_5d | 28.1% |
| price_above_hull | 64.3% |
| price_above_sma_200 | 31.8% |
| price_above_sma_21 | 69.8% |
| price_above_sma_50 | 61.0% |
| price_above_tema | 66.5% |
| price_below_dema | 20.9% |
| price_below_hull | 35.7% |
| price_below_tema | 33.5% |
| psar_bullish | 70.0% |
| psar_flip_dn | 3.9% |
| psar_flip_up | 2.6% |
| r1_break_retest_long | 78.9% |
| recent_blowoff_at_r3 | 0.1% |
| resistance_break_retest | 69.8% |
| risk_off_regime_bond_signal | 18.0% |
| risk_off_regime_bond_signal_strong | 3.8% |
| risk_off_regime_gold_signal | 34.8% |
| risk_on_regime_bond_signal | 50.6% |
| risk_on_regime_bond_signal_strong | 24.2% |
| roc_positive | 69.8% |
| roc_turning_dn | 1.7% |
| roc_turning_up | 1.0% |
| rsi_14_bullish | 69.2% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_14_cross_dn_overbought_recent_3d | 4.1% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_14_cross_up_oversold_recent_3d | 4.1% |
| rsi_14_extreme_ob | 0.2% |
| rsi_14_extreme_os | 0.2% |
| rsi_14_overbought | 6.3% |
| rsi_14_oversold | 1.6% |
| rsi_14_rising | 62.8% |
| rsi_21_bullish | 64.7% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_21_cross_dn_overbought_recent_3d | 0.9% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 1.4% |
| rsi_21_extreme_ob | 0.1% |
| rsi_21_extreme_os | 0.3% |
| rsi_21_overbought | 1.5% |
| rsi_21_oversold | 0.8% |
| rsi_21_rising | 62.6% |
| rsi_2_bullish | 66.5% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 34.1% |
| rsi_2_cross_dn_overbought_recent_3d | 35.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 21.0% |
| rsi_2_cross_up_oversold_recent_3d | 28.2% |
| rsi_2_extreme_ob | 35.3% |
| rsi_2_extreme_os | 7.8% |
| rsi_2_overbought | 47.2% |
| rsi_2_oversold | 15.9% |
| rsi_2_rising | 62.5% |
| rsi_9_bullish | 69.7% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 2.3% |
| rsi_9_cross_dn_overbought_recent_3d | 10.9% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.7% |
| rsi_9_cross_up_oversold_recent_3d | 7.2% |
| rsi_9_extreme_ob | 3.4% |
| rsi_9_extreme_os | 0.1% |
| rsi_9_overbought | 21.0% |
| rsi_9_oversold | 2.3% |
| rsi_9_rising | 62.6% |
| s1_break_retest_short | 36.3% |
| sc_13d_filed_within_30d | 1.7% |
| sc_13g_filed_within_30d | 2.1% |
| sector_outperforming_spy | 55.6% |
| sector_underperforming_spy | 44.4% |
| shooting_star | 2.1% |
| sma_20_50_bullish | 30.6% |
| sma_20_50_golden_cross | 2.4% |
| sma_50_200_bullish | 28.2% |
| sma_50_200_golden_cross | 0.3% |
| sma_9_21_bullish | 69.2% |
| sma_9_21_golden_cross | 1.7% |
| smc_bos_bearish | 16.3% |
| smc_bos_bullish | 6.0% |
| smc_bos_retest_long | 4.1% |
| smc_bos_retest_short | 5.3% |
| smc_breaker_block_bearish | 20.4% |
| smc_breaker_block_bullish | 14.5% |
| smc_choch_bearish | 6.6% |
| smc_choch_bullish | 3.9% |
| smc_equal_highs_swept | 2.0% |
| smc_equal_lows_swept | 6.7% |
| smc_fvg_bearish_active | 23.2% |
| smc_fvg_bullish_active | 49.7% |
| smc_fvg_retest_long_zone | 5.2% |
| smc_fvg_retest_short_zone | 6.6% |
| smc_in_discount_zone | 55.6% |
| smc_in_premium_zone | 64.8% |
| smc_inverse_fvg_bearish | 78.7% |
| smc_inverse_fvg_bullish | 81.1% |
| smc_liquidity_swept_dn | 1.1% |
| smc_liquidity_swept_up | 2.1% |
| smc_mitigation_block_long | 1.6% |
| smc_mitigation_block_short | 3.0% |
| smc_ob_bearish_active | 51.9% |
| smc_ob_bullish_active | 16.5% |
| smc_ote_long_zone | 9.9% |
| smc_ote_short_zone | 9.6% |
| squeeze_fire_dn | 1.0% |
| squeeze_fire_up | 0.5% |
| squeeze_in | 19.2% |
| squeeze_positive | 70.6% |
| stoch_bearish_cross | 9.2% |
| stoch_broad_overbought | 51.7% |
| stoch_broad_oversold | 10.3% |
| stoch_bullish_cross | 13.1% |
| stoch_overbought | 44.3% |
| stoch_oversold | 7.1% |
| stochrsi_cross_dn | 35.2% |
| stochrsi_cross_up | 19.4% |
| stochrsi_overbought | 45.0% |
| stochrsi_oversold | 10.5% |
| supertrend_flip_recent_long_5d | 1.3% |
| support_break_retest | 30.2% |
| tema_above_dema | 73.3% |
| tema_cross_dn | 0.2% |
| tema_cross_up | 0.7% |
| three_black_crows | 1.7% |
| three_white_soldiers | 8.7% |
| triangle_apex_break_retest_long | 19.1% |
| triangle_ascending_detected | 11.9% |
| triangle_descending_detected | 8.6% |
| uo_overbought | 5.7% |
| uo_oversold | 0.6% |
| usd_strengthening | 19.9% |
| usd_weakening | 19.6% |
| vix_band_high | 30.8% |
| vix_band_low | 41.5% |
| vix_band_mid | 27.7% |
| vix_term_backwardation | 7.2% |
| vix_term_contango | 92.8% |
| vol_spike_2x_on_down_day_recent_3d | 1.3% |
| vol_spike_2x_on_up_day_recent_3d | 2.1% |
| vp_above_value_area | 31.4% |
| vp_below_value_area | 16.6% |
| vp_close_above_poc | 61.4% |
| vp_close_below_poc | 38.6% |
| vp_in_value_area | 52.0% |
| week_open_gap_down_15pct | 1.0% |
| week_open_gap_up_15pct | 1.7% |
| weekly_above_ema_10 | 59.7% |
| weekly_above_ema_20 | 41.9% |
| weekly_bias_bear | 38.2% |
| weekly_bias_bull | 39.8% |
| weekly_momentum_pos | 69.7% |
| williams_r_overbought | 47.0% |
| williams_r_oversold | 9.0% |
| williams_r_rising | 58.6% |
| within_pead_window | 38.3% |
| within_post_deletion_window | 5.7% |
| within_post_inclusion_window | 0.7% |
| within_pre_rebalance_window | 1.0% |
| xs_avoid_high_ivol | 73.2% |
| xs_avoid_high_max | 73.0% |
| xs_high_beta_decile | 23.3% |
| xs_low_beta_bottom_quintile | 23.3% |
| xs_low_beta_decile | 18.8% |
| xs_low_beta_decile_entry_recent_5d | 0.5% |
| xs_low_beta_top_quintile | 18.8% |
| xs_momentum_bottom_decile | 19.1% |
| xs_momentum_bottom_quintile | 33.3% |
| xs_momentum_top_decile | 3.5% |
| xs_momentum_top_quintile | 8.1% |
| xs_quality_bottom_quintile | 22.5% |
| xs_quality_top_quintile | 20.4% |
| xs_quality_top_tercile | 39.0% |
| year_high_break_retest_long | 1.5% |
| year_low_break_retest_short | 2.1% |
| yoy_surprise_high | 44.5% |
| yoy_surprise_negative | 45.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 89.7% |
| committed_growth_holders | 89.7% |
| corp_donations_1y | 6.7% |
| corp_donations_count_1y | 6.7% |
| corp_donations_unique_pacs | 6.7% |
| cot_rut_commercials_pctile_3y | 46.2% |
| cot_rut_mmoney_pctile_3y | 46.2% |
| cup_handle_depth_pct | 19.3% |
| days_since_deletion | 8.1% |
| days_since_inclusion | 13.0% |
| days_since_last_earnings | 97.1% |
| days_to_next_holiday | 65.3% |
| days_to_rebalance | 9.3% |
| dpi_30d_avg | 95.6% |
| dpi_recent | 95.6% |
| earnings_announcement_return | 90.7% |
| earnings_eps_yoy_growth | 93.0% |
| flag_bear_pole_move_pct | 0.5% |
| flag_bull_pole_move_pct | 0.7% |
| gov_contracts_4q_sum | 41.1% |
| gov_contracts_last_qtr_amount | 41.1% |
| gov_contracts_qoq_growth | 41.1% |
| head_shoulders_magnitude_pct | 9.1% |
| insider_director_buyers_30d | 6.7% |
| insider_officer_buyers_30d | 6.7% |
| insider_total_shares_bought_30d | 6.7% |
| insider_unique_buyers_30d | 6.7% |
| inverted_cup_handle_height_pct | 20.9% |
| lobbying_amount_1y | 70.5% |
| lobbying_amount_q | 70.5% |
| lobbying_amount_yoy | 70.5% |
| otc_short_ratio_recent | 95.6% |
| otc_volume_recent | 95.6% |
| pair_half_life | 93.6% |
| pair_max_abs_zscore | 93.6% |
| pair_zscore_signed | 93.6% |
| pct_from_avwap_20high | 79.1% |
| pct_from_avwap_20low | 97.7% |
| pct_from_avwap_252low | 97.9% |
| pct_from_avwap_50low | 97.9% |
| persistent_holders_4q | 89.7% |
| persistent_holders_8q | 89.7% |
| sc_13g_latest_percent_owned | 1.0% |
| search_volume_index_recent | 77.7% |
| search_volume_observations | 77.7% |
| search_volume_zscore_30d | 77.7% |
| sector_etf_return_20d | 2.5% |
| spy_return_20d | 2.5% |
| total_active_holders | 89.7% |
| triangle_breakdown_pct | 8.6% |
| triangle_breakout_pct | 11.9% |
| xs_quality_decile | 62.1% |
| xs_quality_gross_profitability | 62.1% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.998), `avwap_50low` (1.0), `bb_10_20_lower` (0.999), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (1.0), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.997), `double_top_peak` (0.998), `entry_stop_long` (0.998), `entry_stop_short` (0.998), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.999), `fib_786` (0.999), `fib_ext_127` (0.993), `fib_ext_162` (0.991), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.998), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.985), `monthly_sma_6` (0.996), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.998), `swing_high` (0.995), `swing_low` (0.998), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.997), `vp_value_area_low` (0.998), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_low` (0.99)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | (structural) c > o - optional min body p | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P2.1 | mirror of close_above_open | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P3.1 | mirror of top_40pct | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P4.1 | range-position cutoff | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P6.1 | obv vs its moving average | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P6.2 | margin pct over the MA | 3 | subset-safe | no - derives offline | 1 | 2 | 0 |
| P7.1 | breakout clearance - the breakout bar cl | 3 | MIXED - offline AND pending levels | no - production only; 1 offline; 1 pending (DEFINED-NO-ACTUATOR) | 1 | 1 | 1 |
| P7.2 | retest tolerance - a later bar's low wit | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P7.3.1 | breakout window - lag 2 to N bars ago, a | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P7.3.2 | breakout window - lag 2 to N bars ago, a | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P9.1 | volume ratio ceiling (vol / avg, strict  | 3 | subset-safe | no - derives offline | 1 | 2 | 0 |
| P10 | ppo_hist >= -0.2823 | 5 | subset-safe | no - derives offline | 1 | 4 | 0 |
| P11 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     3 x 3 x 3 x 3 x 3 x 3 x 3 x 3 x 3 x 3 x 3 x 5 x 1 = 885735
offline gradings   89 level-combinations x 24 exits = 2136 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  885645 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 89 + 885645 = 885735 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 640 census axes join it only when REGISTERED at the T3 band review.
