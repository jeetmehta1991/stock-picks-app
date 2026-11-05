# Table A - r1_break_retest

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build ff10274b7 | commit 352770ae3 at 2026-11-05 00:52:21 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** pivot | **status:** NOT-STARTED | **R5 fires:** 3371 (closed fires in the exit cube: 3371 of 3371, S6-B3258) | **surviving fires (T1):** 3371 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  above_avwap_20low  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define
P2  above_r1  <- backtest/signals/technical.py
       DEFN: read the producer source (evidence column)
       knobs bands to define
P3  below_avwap_20high  <- backtest/signals/technical.py (f-string template)
       DEFN: close below the anchored-VWAP from the 20d high (avwap block)
       knobs P3.1-P3.1 (band rows in Table A)
P4  below_s1  <- backtest/signals/technical.py
       DEFN: read the producer source (evidence column)
       knobs bands to define
P5  close_above_open  <- backtest/signals/technical.py
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P5.1-P5.1 (band rows in Table A)
P6  close_below_open  <- backtest/signals/technical.py
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P6.1-P6.1 (band rows in Table A)
P7  close_in_bottom_40pct_of_range  <- backtest/signals/technical.py
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P7.1-P7.1 (band rows in Table A)
P8  close_in_top_40pct_of_range  <- backtest/signals/technical.py
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P8.1-P8.1 (band rows in Table A)
P9  macd_12_26_9_bearish  <- backtest/signals/technical.py (f-string template)
       DEFN: MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)
       knobs P9.1-P9.1 (band rows in Table A)
P10  macd_12_26_9_bullish  <- backtest/signals/technical.py (f-string template)
       DEFN: MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)
       knobs P10.1-P10.1 (band rows in Table A)
P11  r1_break_retest_long  <- backtest/signals/technical.py
       DEFN: read the producer source (evidence column)
       knobs bands to define
P12  s1_break_retest_short  <- backtest/signals/technical.py
       DEFN: read the producer source (evidence column)
       knobs bands to define
P13  vol_below_avg  <- backtest/signals/technical.py
       DEFN: volume / 20d average < 1.0 (technical.py compute_volume)
       knobs P13.1-P13.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P14  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_r1_break_retest (docstring and return dropped):

```python
fl = s.get('r1_break_retest_long') and s.get('above_r1') and s.get('macd_12_26_9_bullish') and s.get('close_above_open') and s.get('close_in_top_40pct_of_range') and s.get('vol_below_avg') and s.get('above_avwap_20low')
fs = s.get('s1_break_retest_short') and s.get('below_s1') and s.get('macd_12_26_9_bearish') and s.get('close_below_open') and s.get('close_in_bottom_40pct_of_range') and s.get('vol_below_avg') and s.get('below_avwap_20high') and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | above_avwap_20low - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs to define | BANDS-TO-DEFINE |
| P2 | PRODUCER | above_r1 - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs to define | BANDS-TO-DEFINE |
| P3 | PRODUCER | below_avwap_20high - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | close below the anchored-VWAP from the 20d high (avwap block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | buffer pct (price vs avwap anchored at 20d high) + anchor choice [20high, 50high, 252high] - backtest/signals/technical.py avwap block | BRACKET zero; strict inequality today | 0.0 | [0, 0.25, 0.5] | offline 0 of 3 levels - none - today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | below_s1 - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs to define | BANDS-TO-DEFINE |
| P5 | PRODUCER | close_above_open - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | (structural) c > o - optional min body pct - backtest/signals/technical.py bar-anatomy block | BRACKET zero | 0.0 | [0, 0.2, 0.5] pct | offline 0 of 3 levels - none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | PRODUCER | close_below_open - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P6.x) | BANDS-DEFINED |
| P6.1 | BAND | mirror of close_above_open - technical.py bar-anatomy block | mirror | 0.0 | [0, 0.2, 0.5] pct | offline 0 of 3 levels - none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | PRODUCER | close_in_bottom_40pct_of_range - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P7.x) | BANDS-DEFINED |
| P7.1 | BAND | mirror of top_40pct - backtest/signals/technical.py:1682 region | mirror | 0.4 | [0.25, 0.40, 0.50] | offline 0 of 3 levels - none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P8 | PRODUCER | close_in_top_40pct_of_range - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P8.x) | BANDS-DEFINED |
| P8.1 | BAND | range-position cutoff - backtest/signals/technical.py:1682 | BRACKET production 0.40 | 0.4 | [0.25, 0.40, 0.50] | offline 0 of 3 levels - none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P9 | PRODUCER | macd_12_26_9_bearish - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P9.x) | BANDS-DEFINED |
| P9.1 | BAND | span triple (fast, slow, signal) - backtest/signals/technical.py:634-648 | MEASURED availability - both triples are emitted and macd_8_21_5_* IS persisted | (12,26,9) | [(8,21,5), (12,26,9)] both computed in production; other triples are new | offline 0 of 2 levels - none - the (8,21,5) SWAP changes which bars fire: the persisted macd_8_21_5 keys re-grade only fires the (12,26,9) cube holds, and the fires the swap adds are engine work | any third triple; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P10 | PRODUCER | macd_12_26_9_bullish - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P10.x) | BANDS-DEFINED |
| P10.1 | BAND | span triple (mirror of the bearish entry) - backtest/signals/technical.py:634-648 | MEASURED availability (both persisted) | (12,26,9) | [(8,21,5), (12,26,9)] both computed; others new | offline 0 of 2 levels - none - the (8,21,5) swap changes which bars fire; the persisted keys re-grade only fires the (12,26,9) cube holds (mirror of the bearish row) | any third triple; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P11 | PRODUCER | r1_break_retest_long - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs to define | BANDS-TO-DEFINE |
| P12 | PRODUCER | s1_break_retest_short - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs to define | BANDS-TO-DEFINE |
| P13 | PRODUCER | vol_below_avg - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average < 1.0 (technical.py compute_volume) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P13.x) | BANDS-DEFINED |
| P13.1 | BAND | volume ratio ceiling (vol / avg, strict <) - backtest/signals/technical.py compute_volume | MEASURED - production 1.0 (B594, the retest dry-up); levels near the R5 fires' vol_ratio_20d (q20 0.65, q60 0.83 on both consumers); avg window is the second knob [10, 20, 50] | 1.0 | 0.6, 0.8, 1 | offline 2 of 3 levels - TIGHTER ceilings (0.8, 0.6) on the persisted vol_ratio_20d, which is rounded to 2 dp - a level is blurred by 0.005 either way (the rounding already reads 1.00 on 23 of 2414 and 22 of 2164 R5 fires the strict production gate admitted) | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P14 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
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
| adx | backtest/signals/technical.py | 100.0% | 16.75, 21.38, 26.02, 32.99 | 16.75: 2698 (80%); 21.38: 2024 (60%); 26.02: 1350 (40%); 32.99: 676 (20%) | 16.75: 675 (20%); 21.38: 1349 (40%); 26.02: 2023 (60%); 32.99: 2697 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 19.51, 22.74, 25.59, 29.16 | 19.51: 2698 (80%); 22.74: 2024 (60%); 25.59: 1349 (40%); 29.16: 676 (20%) | 19.51: 676 (20%); 22.74: 1350 (40%); 25.59: 2026 (60%); 29.16: 2698 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 17.31, 20.62, 23.62, 27.18 | 17.31: 2697 (80%); 20.62: 2025 (60%); 23.62: 1351 (40%); 27.18: 677 (20%) | 17.31: 676 (20%); 20.62: 1349 (40%); 23.62: 2023 (60%); 27.18: 2697 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -5.2591, -1.7789, 0.0105, 2.8866 | -5.2591: 2697 (80%); -1.7789: 2023 (60%); 0.0105: 1349 (40%); 2.8866: 675 (20%) | -5.2591: 675 (20%); -1.7789: 1349 (40%); 0.0105: 2023 (60%); 2.8866: 2697 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.1443, 1.9764, 3.2799, 5.7282 | 1.1443: 2697 (80%); 1.9764: 2023 (60%); 3.2799: 1349 (40%); 5.7282: 675 (20%) | 1.1443: 675 (20%); 1.9764: 1349 (40%); 3.2799: 2023 (60%); 5.7282: 2697 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.1443, 1.9764, 3.2799, 5.7282 | 1.1443: 2697 (80%); 1.9764: 2023 (60%); 3.2799: 1349 (40%); 5.7282: 675 (20%) | 1.1443: 675 (20%); 1.9764: 1349 (40%); 3.2799: 2023 (60%); 5.7282: 2697 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.041, 2.531, 3.058, 3.869 | 2.041: 2698 (80%); 2.531: 2023 (60%); 3.058: 1349 (40%); 3.869: 675 (20%) | 2.041: 675 (20%); 2.531: 1349 (40%); 3.058: 2024 (60%); 3.869: 2697 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0487, 0.0684, 0.0914, 0.1281 | 0.0487: 2700 (80%); 0.0684: 2024 (60%); 0.0914: 1349 (40%); 0.1281: 678 (20%) | 0.0487: 675 (20%); 0.0684: 1349 (40%); 0.0914: 2026 (60%); 0.1281: 2697 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1401, 0.3378, 0.7035, 0.8767 | 0.1401: 2697 (80%); 0.3378: 2024 (60%); 0.7035: 1349 (40%); 0.8767: 675 (20%) | 0.1401: 675 (20%); 0.3378: 1349 (40%); 0.7035: 2023 (60%); 0.8767: 2698 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0581, 0.0803, 0.1078, 0.1465 | 0.0581: 2701 (80%); 0.0803: 2024 (60%); 0.1078: 1350 (40%); 0.1465: 675 (20%) | 0.0581: 675 (20%); 0.0803: 1349 (40%); 0.1078: 2024 (60%); 0.1465: 2699 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1034, 0.3887, 0.5645, 0.8295 | 0.1034: 2697 (80%); 0.3887: 2024 (60%); 0.5645: 1349 (40%); 0.8295: 675 (20%) | 0.1034: 676 (20%); 0.3887: 1349 (40%); 0.5645: 2023 (60%); 0.8295: 2697 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0775, 0.1071, 0.1437, 0.1953 | 0.0775: 2700 (80%); 0.1071: 2023 (60%); 0.1437: 1350 (40%); 0.1953: 676 (20%) | 0.0775: 675 (20%); 0.1071: 1350 (40%); 0.1437: 2023 (60%); 0.1953: 2698 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2025, 0.4166, 0.5484, 0.7471 | 0.2025: 2697 (80%); 0.4166: 2024 (60%); 0.5484: 1349 (40%); 0.7471: 675 (20%) | 0.2025: 675 (20%); 0.4166: 1349 (40%); 0.5484: 2023 (60%); 0.7471: 2697 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0478, -0.0232, -0.0036, 0.0292 | -0.0478: 2715 (81%); -0.0232: 2060 (61%); -0.0036: 1350 (40%); 0.0292: 693 (21%) | -0.0478: 677 (20%); -0.0232: 1360 (40%); -0.0036: 2025 (60%); 0.0292: 2699 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1444, 0.1691, 0.2134, 0.268 | 0.1444: 2695 (80%); 0.1691: 2019 (60%); 0.2134: 1350 (40%); 0.268: 685 (20%) | 0.1444: 676 (20%); 0.1691: 1352 (40%); 0.2134: 2021 (60%); 0.268: 2686 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 3371 (100%) | 0: 3156 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1076, -0.0282, 0.0402, 0.1225 | -0.1076: 2697 (80%); -0.0282: 2025 (60%); 0.0402: 1349 (40%); 0.1225: 675 (20%) | -0.1076: 676 (20%); -0.0282: 1349 (40%); 0.0402: 2025 (60%); 0.1225: 2697 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 3371 (100%); 1: 1274 (38%) | 0: 2097 (62%); 1: 2799 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.242, -0.1931, -0.1531, -0.1189 | -0.242: 2710 (80%); -0.1931: 2024 (60%); -0.1531: 1349 (40%); -0.1189: 680 (20%) | -0.242: 679 (20%); -0.1931: 1356 (40%); -0.1531: 2028 (60%); -0.1189: 2712 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.6026, 0.6987, 0.7756 | 0.391: 2721 (81%); 0.6026: 2091 (62%); 0.6987: 1379 (41%); 0.7756: 678 (20%) | 0.391: 685 (20%); 0.6026: 1392 (41%); 0.6987: 2031 (60%); 0.7756: 2728 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.3526, 0.6026, 0.8205 | 0.2628: 2710 (80%); 0.3526: 2023 (60%); 0.6026: 1367 (41%); 0.8205: 700 (21%) | 0.2628: 798 (24%); 0.3526: 1359 (40%); 0.6026: 2023 (60%); 0.8205: 2700 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1043, -0.0222, 0.0857, 0.2506 | -0.1043: 2711 (80%); -0.0222: 2024 (60%); 0.0857: 1359 (40%); 0.2506: 695 (21%) | -0.1043: 685 (20%); -0.0222: 1359 (40%); 0.0857: 2031 (60%); 0.2506: 2728 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.25, 0.4487, 0.5962, 0.8462 | 0.25: 2748 (82%); 0.4487: 2027 (60%); 0.5962: 1356 (40%); 0.8462: 678 (20%) | 0.25: 676 (20%); 0.4487: 1394 (41%); 0.5962: 2035 (60%); 0.8462: 2711 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1346, 0.3462, 0.4808, 0.6731 | 0.1346: 2723 (81%); 0.3462: 2028 (60%); 0.4808: 1402 (42%); 0.6731: 699 (21%) | 0.1346: 695 (21%); 0.3462: 1389 (41%); 0.4808: 2033 (60%); 0.6731: 2732 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.4997, -0.352, -0.171, 0.0666 | -0.4997: 2697 (80%); -0.352: 2024 (60%); -0.171: 1355 (40%); 0.0666: 688 (20%) | -0.4997: 687 (20%); -0.352: 1374 (41%); -0.171: 2054 (61%); 0.0666: 2698 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3397, 0.5192, 0.7244, 0.9231 | 0.3397: 2700 (80%); 0.5192: 2030 (60%); 0.7244: 1353 (40%); 0.9231: 706 (21%) | 0.3397: 696 (21%); 0.5192: 1445 (43%); 0.7244: 2036 (60%); 0.9231: 2712 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1154, 0.2885, 0.5321, 0.7821 | 0.1154: 2740 (81%); 0.2885: 2046 (61%); 0.5321: 1356 (40%); 0.7821: 688 (20%) | 0.1154: 709 (21%); 0.2885: 1386 (41%); 0.5321: 2040 (61%); 0.7821: 2702 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0691, -0.0593, -0.0412, 0 | -0.0691: 2714 (81%); -0.0593: 2044 (61%); -0.0412: 1368 (41%); 0: 903 (27%) | -0.0691: 678 (20%); -0.0593: 1365 (40%); -0.0412: 2028 (60%); 0: 3296 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4038, 0.6923, 0.8846, 1 | 0.4038: 2700 (80%); 0.6923: 2046 (61%); 0.8846: 1390 (41%); 1: 702 (21%) | 0.4038: 681 (20%); 0.6923: 1349 (40%); 0.8846: 2131 (63%); 1: 3371 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1026, 0.2179, 0.5449, 0.8718 | 0.1026: 2708 (80%); 0.2179: 2047 (61%); 0.5449: 1360 (40%); 0.8718: 675 (20%) | 0.1026: 684 (20%); 0.2179: 1364 (40%); 0.5449: 2031 (60%); 0.8718: 2703 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0, 0.0373, 0.0706, 0.1955 | 0: 2699 (80%); 0.0373: 2031 (60%); 0.0706: 1381 (41%); 0.1955: 675 (20%) | 0: 685 (20%); 0.0373: 1355 (40%); 0.0706: 2025 (60%); 0.1955: 2702 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4583, 0.7821, 0.9351, 0.9744 | 0.4583: 2715 (81%); 0.7821: 2035 (60%); 0.9351: 1379 (41%); 0.9744: 696 (21%) | 0.4583: 689 (20%); 0.7821: 1351 (40%); 0.9351: 2044 (61%); 0.9744: 2796 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0816, 0.2278, 0.5577, 0.7882 | 0.0816: 2699 (80%); 0.2278: 2033 (60%); 0.5577: 1365 (40%); 0.7882: 710 (21%) | 0.0816: 683 (20%); 0.2278: 1377 (41%); 0.5577: 2037 (60%); 0.7882: 2704 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0003, 0.1182, 0.2381 | -0.0812: 2946 (87%); -0.0003: 2030 (60%); 0.1182: 1350 (40%); 0.2381: 679 (20%) | -0.0812: 770 (23%); -0.0003: 1374 (41%); 0.1182: 2040 (61%); 0.2381: 2722 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0954, 0.0073, 0.0492, 0.0916 | -0.0954: 2702 (80%); 0.0073: 2029 (60%); 0.0492: 1355 (40%); 0.0916: 677 (20%) | -0.0954: 689 (20%); 0.0073: 1354 (40%); 0.0492: 2033 (60%); 0.0916: 2719 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.5962, 0.7628, 0.8782 | 0.391: 2698 (80%); 0.5962: 2029 (60%); 0.7628: 1355 (40%); 0.8782: 732 (22%) | 0.391: 687 (20%); 0.5962: 1361 (40%); 0.7628: 2098 (62%); 0.8782: 2703 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3718, 0.5833, 0.8205 | 0.1474: 2723 (81%); 0.3718: 2027 (60%); 0.5833: 1360 (40%); 0.8205: 675 (20%) | 0.1474: 711 (21%); 0.3718: 1354 (40%); 0.5833: 2032 (60%); 0.8205: 2729 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0392, 0.0975, 0.1842, 0.385 | 0.0392: 2697 (80%); 0.0975: 2025 (60%); 0.1842: 1349 (40%); 0.385: 676 (20%) | 0.0392: 677 (20%); 0.0975: 1350 (40%); 0.1842: 2023 (60%); 0.385: 2698 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.6% | 25, 61, 78, 137 | 25: 2665 (79%); 61: 2008 (60%); 78: 1338 (40%); 137: 666 (20%) | 25: 684 (20%); 61: 1370 (41%); 78: 2009 (60%); 137: 2662 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.6% | 1.6737, 2.1867, 2.7515, 3.603 | 1.6737: 2686 (80%); 2.1867: 2015 (60%); 2.7515: 1344 (40%); 3.603: 672 (20%) | 1.6737: 672 (20%); 2.1867: 1343 (40%); 2.7515: 2015 (60%); 3.603: 2686 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 19, 26, 34 | 9: 2726 (81%); 19: 2115 (63%); 26: 1483 (44%); 34: 708 (21%) | 9: 720 (21%); 19: 1374 (41%); 26: 2032 (60%); 34: 2758 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3 | 1: 2810 (83%); 2: 2052 (61%); 3: 1360 (40%) | 1: 1319 (39%); 2: 2011 (60%); 3: 2718 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0152, -0.0045, 0.0126, 0.0249 | -0.0152: 2700 (80%); -0.0045: 2025 (60%); 0.0126: 1353 (40%); 0.0249: 681 (20%) | -0.0152: 696 (21%); -0.0045: 1351 (40%); 0.0126: 2028 (60%); 0.0249: 2699 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5078, 25.6194, 26.3984, 27.09 | 24.5078: 2713 (80%); 25.6194: 2024 (60%); 26.3984: 1362 (40%); 27.09: 681 (20%) | 24.5078: 679 (20%); 25.6194: 1357 (40%); 26.3984: 2028 (60%); 27.09: 2701 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.759, -0.222, 0.1, 0.591 | -0.759: 2698 (80%); -0.222: 2023 (60%); 0.1: 1349 (40%); 0.591: 675 (20%) | -0.759: 675 (20%); -0.222: 1351 (40%); 0.1: 2025 (60%); 0.591: 2697 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.591, -0.1, 0.222, 0.759 | -0.591: 2697 (80%); -0.1: 2025 (60%); 0.222: 1351 (40%); 0.759: 675 (20%) | -0.591: 675 (20%); -0.1: 1349 (40%); 0.222: 2023 (60%); 0.759: 2698 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0449, -0.0109, 0.0231, 0.0618 | -0.0449: 2702 (80%); -0.0109: 2025 (60%); 0.0231: 1351 (40%); 0.0618: 676 (20%) | -0.0449: 677 (20%); -0.0109: 1349 (40%); 0.0231: 2024 (60%); 0.0618: 2716 (81%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0718, 8.4764, 8.7144, 9.1133 | 8.0718: 2696 (80%); 8.4764: 2021 (60%); 8.7144: 1346 (40%); 9.1133: 673 (20%) | 8.0718: 675 (20%); 8.4764: 1350 (40%); 8.7144: 2025 (60%); 9.1133: 2698 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 3347 (99%); 1: 1060 (31%) | 0: 2287 (68%); 1: 3009 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0 | 0: 2685 (80%) | 0: 2786 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 3347 (99%); 1: 1132 (34%) | 0: 2215 (66%); 1: 2972 (88%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 2, 5, 100, 261 | 2: 2893 (86%); 5: 2203 (65%); 100: 1352 (40%); 261: 675 (20%) | 2: 702 (21%); 5: 1368 (41%); 100: 2024 (60%); 261: 2697 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 4, 78, 132 | 1: 2710 (80%); 4: 2038 (60%); 78: 1358 (40%); 132: 682 (20%) | 1: 955 (28%); 4: 1448 (43%); 78: 2034 (60%); 132: 2698 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.5284, -0.1213, 0.13, 0.5311 | -0.5284: 2697 (80%); -0.1213: 2023 (60%); 0.13: 1349 (40%); 0.5311: 675 (20%) | -0.5284: 675 (20%); -0.1213: 1349 (40%); 0.13: 2023 (60%); 0.5311: 2697 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.2122, -0.7405, -0.0025, 1.2549 | -2.2122: 2697 (80%); -0.7405: 2023 (60%); -0.0025: 1349 (40%); 1.2549: 675 (20%) | -2.2122: 675 (20%); -0.7405: 1349 (40%); -0.0025: 2023 (60%); 1.2549: 2697 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.6358, -0.8751, 0.0026, 1.4501 | -2.6358: 2697 (80%); -0.8751: 2023 (60%); 0.0026: 1349 (40%); 1.4501: 675 (20%) | -2.6358: 675 (20%); -0.8751: 1349 (40%); 0.0026: 2023 (60%); 1.4501: 2697 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.4829, -0.1107, 0.2008, 0.5979 | -0.4829: 2697 (80%); -0.1107: 2024 (60%); 0.2008: 1349 (40%); 0.5979: 675 (20%) | -0.4829: 675 (20%); -0.1107: 1349 (40%); 0.2008: 2024 (60%); 0.5979: 2697 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -1.9507, -0.6427, 0.0354, 1.0938 | -1.9507: 2697 (80%); -0.6427: 2023 (60%); 0.0354: 1349 (40%); 1.0938: 675 (20%) | -1.9507: 675 (20%); -0.6427: 1349 (40%); 0.0354: 2023 (60%); 1.0938: 2697 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.3031, -0.78, -0.0128, 1.2952 | -2.3031: 2697 (80%); -0.78: 2023 (60%); -0.0128: 1349 (40%); 1.2952: 675 (20%) | -2.3031: 675 (20%); -0.78: 1350 (40%); -0.0128: 2023 (60%); 1.2952: 2697 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 37.23, 46.06, 53.25, 61.39 | 37.23: 2697 (80%); 46.06: 2023 (60%); 53.25: 1349 (40%); 61.39: 675 (20%) | 37.23: 676 (20%); 46.06: 1350 (40%); 53.25: 2023 (60%); 61.39: 2699 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.4% | 0.0066, 0.014, 0.0248, 0.0446 | 0.0066: 2679 (79%); 0.014: 2006 (60%); 0.0248: 1341 (40%); 0.0446: 670 (20%) | 0.0066: 671 (20%); 0.014: 1344 (40%); 0.0248: 2009 (60%); 0.0446: 2680 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 3371 (100%); 1: 2548 (76%); 3: 1613 (48%); 8: 709 (21%) | 0: 823 (24%); 1: 1358 (40%); 3: 2029 (60%); 8: 2730 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1429 | 0: 3371 (100%); 0.1429: 697 (21%) | 0: 2350 (70%); 0.1429: 2719 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1111, 0.4, 0.6667 | 0: 3371 (100%); 0.1111: 2027 (60%); 0.4: 1369 (41%); 0.6667: 696 (21%) | 0: 1327 (39%); 0.1111: 1351 (40%); 0.4: 2080 (62%); 0.6667: 2790 (83%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 3371 (100%); 1: 2321 (69%); 2: 1695 (50%); 6: 685 (20%) | 0: 1050 (31%); 1: 1676 (50%); 2: 2082 (62%); 6: 2797 (83%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 3371 (100%); 1: 2548 (76%); 3: 1613 (48%); 8: 709 (21%) | 0: 823 (24%); 1: 1358 (40%); 3: 2029 (60%); 8: 2730 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 3371 (100%); 1: 2471 (73%); 3: 1552 (46%); 8: 698 (21%) | 0: 900 (27%); 1: 1451 (43%); 3: 2084 (62%); 8: 2756 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2235, 0.3636, 0.5623 | 0: 3107 (92%); 0.2235: 2023 (60%); 0.3636: 1355 (40%); 0.5623: 675 (20%) | 0: 713 (21%); 0.2235: 1349 (40%); 0.3636: 2024 (60%); 0.5623: 2697 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1538, 0.5556 | 0: 3064 (91%); 0.1538: 1349 (40%); 0.5556: 686 (20%) | 0: 1888 (56%); 0.1538: 2028 (60%); 0.5556: 2699 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2857, 0.5442 | 0: 3079 (91%); 0.2857: 1351 (40%); 0.5442: 675 (20%) | 0: 1517 (45%); 0.2857: 2040 (61%); 0.5442: 2698 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2857, 0.5442 | 0: 3079 (91%); 0.2857: 1351 (40%); 0.5442: 675 (20%) | 0: 1517 (45%); 0.2857: 2040 (61%); 0.5442: 2698 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1667, 0, 0.1659 | -0.1667: 2698 (80%); 0: 2375 (70%); 0.1659: 675 (20%) | -0.1667: 702 (21%); 0: 2432 (72%); 0.1659: 2697 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.809, -0.4472, 0, 0.9254 | -0.809: 2710 (80%); -0.4472: 2142 (64%); 0: 1635 (49%); 0.9254: 675 (20%) | -0.809: 740 (22%); -0.4472: 1428 (42%); 0: 2165 (64%); 0.9254: 2697 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 2850 (85%); 4: 2212 (66%); 7: 1421 (42%); 11: 726 (22%) | 2: 844 (25%); 4: 1430 (42%); 7: 2173 (64%); 11: 2744 (81%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0416, -0.0107, 0.0151, 0.0489 | -0.0416: 2695 (80%); -0.0107: 2020 (60%); 0.0151: 1350 (40%); 0.0489: 673 (20%) | -0.0416: 676 (20%); -0.0107: 1351 (40%); 0.0151: 2021 (60%); 0.0489: 2698 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0778, -0.0317, 0.0057, 0.0509 | -0.0778: 2697 (80%); -0.0317: 2021 (60%); 0.0057: 1347 (40%); 0.0509: 674 (20%) | -0.0778: 674 (20%); -0.0317: 1350 (40%); 0.0057: 2024 (60%); 0.0509: 2697 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0308, -0.0094, 0.0143, 0.0421 | -0.0308: 2696 (80%); -0.0094: 2022 (60%); 0.0143: 1346 (40%); 0.0421: 672 (20%) | -0.0308: 675 (20%); -0.0094: 1349 (40%); 0.0143: 2025 (60%); 0.0421: 2699 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -21.274, -8.262, 3.018, 22.386 | -21.274: 2697 (80%); -8.262: 2023 (60%); 3.018: 1349 (40%); 22.386: 675 (20%) | -21.274: 675 (20%); -8.262: 1349 (40%); 3.018: 2023 (60%); 22.386: 2697 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.036, 0.0482, 0.063, 0.0845 | 0.036: 2697 (80%); 0.0482: 2026 (60%); 0.063: 1350 (40%); 0.0845: 675 (20%) | 0.036: 685 (20%); 0.0482: 1356 (40%); 0.063: 2025 (60%); 0.0845: 2697 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1092, 0.2786, 0.7571, 0.9014 | 0.1092: 2698 (80%); 0.2786: 2024 (60%); 0.7571: 1349 (40%); 0.9014: 675 (20%) | 0.1092: 675 (20%); 0.2786: 1349 (40%); 0.7571: 2023 (60%); 0.9014: 2697 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.4374, -1.1329, -0.0056, 1.3059 | -2.4374: 2697 (80%); -1.1329: 2023 (60%); -0.0056: 1349 (40%); 1.3059: 675 (20%) | -2.4374: 675 (20%); -1.1329: 1349 (40%); -0.0056: 2023 (60%); 1.3059: 2697 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.5075, -0.1853, 0.2057, 0.626 | -0.5075: 2697 (80%); -0.1853: 2023 (60%); 0.2057: 1349 (40%); 0.626: 675 (20%) | -0.5075: 675 (20%); -0.1853: 1349 (40%); 0.2057: 2023 (60%); 0.626: 2697 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -2.7369, -1.3912, 0.0034, 1.5378 | -2.7369: 2697 (80%); -1.3912: 2023 (60%); 0.0034: 1349 (40%); 1.5378: 675 (20%) | -2.7369: 675 (20%); -1.3912: 1349 (40%); 0.0034: 2023 (60%); 1.5378: 2697 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.487, -1.302, 1.164, 4.545 | -4.487: 2697 (80%); -1.302: 2023 (60%); 1.164: 1349 (40%); 4.545: 675 (20%) | -4.487: 675 (20%); -1.302: 1349 (40%); 1.164: 2023 (60%); 4.545: 2697 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.5, 46.65, 51.16, 55.85 | 41.5: 2699 (80%); 46.65: 2024 (60%); 51.16: 1352 (40%); 55.85: 676 (20%) | 41.5: 675 (20%); 46.65: 1349 (40%); 51.16: 2023 (60%); 55.85: 2697 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 12.41, 28.35, 76.07, 89.47 | 12.41: 2697 (80%); 28.35: 2024 (60%); 76.07: 1349 (40%); 89.47: 675 (20%) | 12.41: 675 (20%); 28.35: 1349 (40%); 76.07: 2023 (60%); 89.47: 2697 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 42.53, 46.62, 50.45, 54.85 | 42.53: 2697 (80%); 46.62: 2024 (60%); 50.45: 1350 (40%); 54.85: 676 (20%) | 42.53: 677 (20%); 46.62: 1350 (40%); 50.45: 2023 (60%); 54.85: 2697 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 39.27, 46.67, 52.09, 58.86 | 39.27: 2697 (80%); 46.67: 2023 (60%); 52.09: 1349 (40%); 58.86: 675 (20%) | 39.27: 676 (20%); 46.67: 1350 (40%); 52.09: 2025 (60%); 58.86: 2697 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 3371 (100%) | 0: 3368 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0315, 0.0478, 0.061, 0.0925 | 0.0315: 2698 (80%); 0.0478: 2025 (60%); 0.061: 1379 (41%); 0.0925: 686 (20%) | 0.0315: 676 (20%); 0.0478: 1350 (40%); 0.061: 2044 (61%); 0.0925: 2697 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0899, -0.0608, -0.0447, -0.0341 | -0.0899: 2700 (80%); -0.0608: 2023 (60%); -0.0447: 1365 (40%); -0.0341: 676 (20%) | -0.0899: 681 (20%); -0.0608: 1350 (40%); -0.0447: 2026 (60%); -0.0341: 2705 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 3371 (100%); 2: 714 (21%) | 0: 2318 (69%); 2: 2848 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 24, 38, 55, 68 | 24: 2755 (82%); 38: 2036 (60%); 55: 1344 (40%); 68: 679 (20%) | 24: 747 (22%); 38: 1349 (40%); 55: 2033 (60%); 68: 2757 (82%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.5% | 0.0115, 0.017, 0.0248, 0.0395 | 0.0115: 2656 (79%); 0.017: 1996 (59%); 0.0248: 1330 (39%); 0.0395: 665 (20%) | 0.0115: 666 (20%); 0.017: 1326 (39%); 0.0248: 1992 (59%); 0.0395: 2657 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 99.9% | 0.2101, 0.3459, 0.5202, 0.7161 | 0.2101: 2694 (80%); 0.3459: 2020 (60%); 0.5202: 1347 (40%); 0.7161: 674 (20%) | 0.2101: 675 (20%); 0.3459: 1347 (40%); 0.5202: 2020 (60%); 0.7161: 2694 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 99.9% | 35.32, 68.6, 103.06, 155.2 | 35.32: 2693 (80%); 68.6: 2021 (60%); 103.06: 1347 (40%); 155.2: 676 (20%) | 35.32: 674 (20%); 68.6: 1349 (40%); 103.06: 2020 (60%); 155.2: 2694 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -3.76, -0.9625, 0.43, 2.7188 | -3.76: 2698 (80%); -0.9625: 2023 (60%); 0.43: 1350 (40%); 2.7188: 675 (20%) | -3.76: 675 (20%); -0.9625: 1350 (40%); 0.43: 2024 (60%); 2.7188: 2697 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 25.94, 39.69, 54.68, 70.93 | 25.94: 2697 (80%); 39.69: 2023 (60%); 54.68: 1349 (40%); 70.93: 675 (20%) | 25.94: 675 (20%); 39.69: 1349 (40%); 54.68: 2023 (60%); 70.93: 2697 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 25.74, 41.75, 55.78, 72.81 | 25.74: 2698 (80%); 41.75: 2023 (60%); 55.78: 1350 (40%); 72.81: 676 (20%) | 25.74: 675 (20%); 41.75: 1349 (40%); 55.78: 2025 (60%); 72.81: 2697 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 12.22, 37.22, 67.27, 91.25 | 12.22: 2698 (80%); 37.22: 2023 (60%); 67.27: 1349 (40%); 91.25: 675 (20%) | 12.22: 675 (20%); 37.22: 1349 (40%); 67.27: 2023 (60%); 91.25: 2698 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 32.65, 77.66, 100 | 0: 3371 (100%); 32.65: 2024 (60%); 77.66: 1349 (40%); 100: 909 (27%) | 0: 764 (23%); 32.65: 1350 (40%); 77.66: 2023 (60%); 100: 3371 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 13, 17 | 4: 2847 (84%); 9: 2083 (62%); 13: 1485 (44%); 17: 857 (25%) | 4: 734 (22%); 9: 1410 (42%); 13: 2049 (61%); 17: 2713 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 13, 18 | 4: 2827 (84%); 9: 2029 (60%); 13: 1428 (42%); 18: 706 (21%) | 4: 695 (21%); 9: 1513 (45%); 13: 2104 (62%); 18: 2834 (84%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 42.46, 48.53, 53.11, 58.35 | 42.46: 2697 (80%); 48.53: 2025 (60%); 53.11: 1350 (40%); 58.35: 675 (20%) | 42.46: 675 (20%); 48.53: 1351 (40%); 53.11: 2024 (60%); 58.35: 2697 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1706, 0.4127, 0.6865, 0.8452 | 0.1706: 2710 (80%); 0.4127: 2028 (60%); 0.6865: 1350 (40%); 0.8452: 680 (20%) | 0.1706: 683 (20%); 0.4127: 1364 (40%); 0.6865: 2077 (62%); 0.8452: 2705 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.99, 17.7, 21.01, 25.72 | 14.99: 2698 (80%); 17.7: 2024 (60%); 21.01: 1355 (40%); 25.72: 700 (21%) | 14.99: 678 (20%); 17.7: 1355 (40%); 21.01: 2023 (60%); 25.72: 2697 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.99, 17.7, 21.01, 25.72 | 14.99: 2698 (80%); 17.7: 2024 (60%); 21.01: 1355 (40%); 25.72: 700 (21%) | 14.99: 678 (20%); 17.7: 1355 (40%); 21.01: 2023 (60%); 25.72: 2697 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8595, 0.8921, 0.9264, 0.9623 | 0.8595: 2697 (80%); 0.8921: 2024 (60%); 0.9264: 1351 (40%); 0.9623: 677 (20%) | 0.8595: 675 (20%); 0.8921: 1349 (40%); 0.9264: 2026 (60%); 0.9623: 2715 (81%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.65, 0.75, 0.84, 0.92 | 0.65: 2712 (80%); 0.75: 2095 (62%); 0.84: 1357 (40%); 0.92: 680 (20%) | 0.65: 711 (21%); 0.75: 1352 (40%); 0.84: 2083 (62%); 0.92: 2776 (82%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 99.9% | 0.0159, 0.0347, 0.0642, 0.1101 | 0.0159: 2697 (80%); 0.0347: 2023 (60%); 0.0642: 1348 (40%); 0.1101: 680 (20%) | 0.0159: 677 (20%); 0.0347: 1352 (40%); 0.0642: 2025 (60%); 0.1101: 2695 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 44.8806, 76.4011, 118.7898, 200.7241 | 44.8806: 2697 (80%); 76.4011: 2023 (60%); 118.7898: 1349 (40%); 200.7241: 675 (20%) | 44.8806: 675 (20%); 76.4011: 1349 (40%); 118.7898: 2023 (60%); 200.7241: 2697 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.2197, 73.2501, 114.3705, 194.8336 | 43.2197: 2697 (80%); 73.2501: 2023 (60%); 114.3705: 1349 (40%); 194.8336: 675 (20%) | 43.2197: 675 (20%); 73.2501: 1349 (40%); 114.3705: 2023 (60%); 194.8336: 2697 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.1497, 71.0567, 109.8141, 186.9425 | 41.1497: 2697 (80%); 71.0567: 2023 (60%); 109.8141: 1349 (40%); 186.9425: 675 (20%) | 41.1497: 675 (20%); 71.0567: 1349 (40%); 109.8141: 2023 (60%); 186.9425: 2697 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 46.603, 78.6191, 123.1565, 205.7049 | 46.603: 2697 (80%); 78.6191: 2023 (60%); 123.1565: 1349 (40%); 205.7049: 675 (20%) | 46.603: 675 (20%); 78.6191: 1349 (40%); 123.1565: 2023 (60%); 205.7049: 2697 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.086, 80.9412, 127.6345, 212.8324 | 48.086: 2697 (80%); 80.9412: 2023 (60%); 127.6345: 1349 (40%); 212.8324: 675 (20%) | 48.086: 675 (20%); 80.9412: 1349 (40%); 127.6345: 2023 (60%); 212.8324: 2697 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 3371 (100%) | 0: 3049 (90%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 3371 (100%) | 0: 3060 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.9% | -0.0638, -0.0259, 0.0047, 0.0459 | -0.0638: 2694 (80%); -0.0259: 2023 (60%); 0.0047: 1348 (40%); 0.0459: 675 (20%) | -0.0638: 675 (20%); -0.0259: 1350 (40%); 0.0047: 2021 (60%); 0.0459: 2697 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -86.94, -60.45, -39.81, -13.05 | -86.94: 2697 (80%); -60.45: 2023 (60%); -39.81: 1349 (40%); -13.05: 675 (20%) | -86.94: 676 (20%); -60.45: 1349 (40%); -39.81: 2023 (60%); -13.05: 2697 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.3% | 0.5712, 0.8355, 1.0538, 1.3326 | 0.5712: 2677 (79%); 0.8355: 2008 (60%); 1.0538: 1339 (40%); 1.3326: 670 (20%) | 0.5712: 670 (20%); 0.8355: 1339 (40%); 1.0538: 2008 (60%); 1.3326: 2677 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 2811 (83%); 5: 2206 (65%); 7: 1577 (47%); 9: 875 (26%) | 3: 829 (25%); 5: 1445 (43%); 7: 2111 (63%); 9: 2877 (85%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.2% | 0.1926, 0.2331, 0.2819, 0.3631 | 0.1926: 2675 (79%); 0.2331: 2010 (60%); 0.2819: 1338 (40%); 0.3631: 669 (20%) | 0.1926: 672 (20%); 0.2331: 1338 (40%); 0.2819: 2007 (60%); 0.3631: 2675 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 2868 (85%); 5: 2291 (68%); 7: 1659 (49%); 9: 917 (27%) | 3: 759 (23%); 5: 1365 (40%); 7: 2026 (60%); 9: 2848 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.3% | 0.024, 0.0325, 0.0431, 0.0611 | 0.024: 2679 (79%); 0.0325: 2013 (60%); 0.0431: 1341 (40%); 0.0611: 671 (20%) | 0.024: 676 (20%); 0.0325: 1342 (40%); 0.0431: 2017 (60%); 0.0611: 2679 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 2837 (84%); 5: 2265 (67%); 7: 1593 (47%); 9: 843 (25%) | 3: 786 (23%); 5: 1422 (42%); 7: 2094 (62%); 9: 2901 (86%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.3% | -0.2175, -0.075, 0.0581, 0.2462 | -0.2175: 2678 (79%); -0.075: 2009 (60%); 0.0581: 1339 (40%); 0.2462: 670 (20%) | -0.2175: 670 (20%); -0.075: 1339 (40%); 0.0581: 2008 (60%); 0.2462: 2677 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.3% | 2, 4, 6, 8 | 2: 2882 (85%); 4: 2157 (64%); 6: 1506 (45%); 8: 942 (28%) | 2: 850 (25%); 4: 1545 (46%); 6: 2122 (63%); 8: 2722 (81%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.0% |
| 8k_item_5_02_filed_within_7d | 3.2% |
| above_avwap_20high | 41.0% |
| above_avwap_20low | 61.9% |
| above_avwap_252low | 76.0% |
| above_avwap_50low | 76.1% |
| above_cam_r3 | 51.2% |
| above_cam_r4 | 45.3% |
| above_cpr | 51.2% |
| above_pivot | 51.2% |
| above_prev_high | 45.9% |
| above_prev_high_clearance_atr_05 | 14.8% |
| above_prev_low | 58.3% |
| above_r1 | 51.2% |
| above_r2 | 21.1% |
| above_vwap | 44.9% |
| above_wood_p | 51.3% |
| ad_rising | 56.7% |
| adx_cross_up | 0.8% |
| adx_cross_up_20 | 1.1% |
| adx_di_bear | 58.1% |
| adx_di_bull | 41.9% |
| adx_strong | 8.5% |
| adx_trending | 44.3% |
| ao_cross_dn | 1.6% |
| ao_cross_up | 2.2% |
| ao_positive | 40.1% |
| ao_twin_peaks_bull | 5.3% |
| at_key_fib | 16.6% |
| at_key_fib_wide | 41.1% |
| avwap_20high_loss_recent_3d | 20.1% |
| avwap_20high_reclaim_recent_3d | 27.7% |
| avwap_20low_loss_recent_3d | 26.6% |
| avwap_20low_reclaim_recent_3d | 20.8% |
| avwap_252low_loss_recent_3d | 4.5% |
| avwap_252low_reclaim_recent_3d | 15.2% |
| avwap_50low_loss_recent_3d | 12.4% |
| avwap_50low_reclaim_recent_3d | 19.6% |
| bb_10_20_above_mid | 51.6% |
| bb_10_20_expanding | 57.8% |
| bb_10_20_pctb_gt_75 | 36.2% |
| bb_10_20_pctb_gt_8 | 30.6% |
| bb_10_20_pctb_gt_85 | 23.9% |
| bb_10_20_pctb_gt_9 | 16.6% |
| bb_10_20_pctb_gt_95 | 11.2% |
| bb_10_20_pctb_lt_05 | 9.2% |
| bb_10_20_pctb_lt_1 | 14.9% |
| bb_10_20_pctb_lt_15 | 21.2% |
| bb_10_20_pctb_lt_2 | 27.2% |
| bb_10_20_pctb_lt_25 | 32.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 2.3% |
| bb_10_20_reclaim_from_upper_recent_3d | 3.1% |
| bb_10_20_squeeze | 50.8% |
| bb_10_20_touch_lower | 12.7% |
| bb_10_20_touch_upper | 12.6% |
| bb_20_15_above_mid | 48.0% |
| bb_20_15_expanding | 38.9% |
| bb_20_15_pctb_gt_75 | 24.4% |
| bb_20_15_pctb_gt_8 | 21.2% |
| bb_20_15_pctb_gt_85 | 19.1% |
| bb_20_15_pctb_gt_9 | 16.7% |
| bb_20_15_pctb_gt_95 | 14.2% |
| bb_20_15_pctb_lt_05 | 16.4% |
| bb_20_15_pctb_lt_1 | 19.8% |
| bb_20_15_pctb_lt_15 | 22.8% |
| bb_20_15_pctb_lt_2 | 25.7% |
| bb_20_15_pctb_lt_25 | 28.8% |
| bb_20_15_reclaim_from_lower_recent_3d | 6.2% |
| bb_20_15_reclaim_from_upper_recent_3d | 3.6% |
| bb_20_15_squeeze | 39.8% |
| bb_20_15_touch_lower | 17.7% |
| bb_20_15_touch_upper | 15.0% |
| bb_20_20_above_mid | 48.0% |
| bb_20_20_expanding | 38.9% |
| bb_20_20_pctb_gt_75 | 19.9% |
| bb_20_20_pctb_gt_8 | 16.7% |
| bb_20_20_pctb_gt_85 | 13.6% |
| bb_20_20_pctb_gt_9 | 10.6% |
| bb_20_20_pctb_gt_95 | 7.3% |
| bb_20_20_pctb_lt_05 | 7.3% |
| bb_20_20_pctb_lt_1 | 11.1% |
| bb_20_20_pctb_lt_15 | 15.2% |
| bb_20_20_pctb_lt_2 | 19.8% |
| bb_20_20_pctb_lt_25 | 23.8% |
| bb_20_20_reclaim_from_lower_recent_3d | 2.6% |
| bb_20_20_reclaim_from_upper_recent_3d | 1.1% |
| bb_20_20_squeeze | 21.8% |
| bb_20_20_touch_lower | 7.4% |
| bb_20_20_touch_upper | 7.6% |
| bearish_engulfing | 7.8% |
| bearish_pin_bar | 1.0% |
| below_avwap_20high | 59.0% |
| below_avwap_20low | 38.1% |
| below_avwap_252low | 24.0% |
| below_avwap_50low | 23.9% |
| below_cam_s3 | 48.8% |
| below_cam_s4 | 43.5% |
| below_cpr | 48.8% |
| below_ema_20 | 53.5% |
| below_ema_200 | 59.4% |
| below_ema_200_break_recent_5d | 5.8% |
| below_ema_20_break_recent_5d | 23.0% |
| below_ema_21 | 53.5% |
| below_ema_21_break_recent_5d | 21.9% |
| below_ema_50 | 58.2% |
| below_ema_50_break_recent_5d | 10.4% |
| below_ema_9 | 49.1% |
| below_ema_9_break_recent_5d | 35.2% |
| below_prev_high | 53.8% |
| below_prev_low | 41.5% |
| below_prev_low_clearance_atr_05 | 13.9% |
| below_s1 | 48.8% |
| below_s2 | 19.8% |
| below_sma_20 | 52.0% |
| below_sma_200 | 58.2% |
| below_sma_21 | 52.8% |
| below_sma_50 | 58.1% |
| below_sma_9 | 48.4% |
| below_vwap | 55.1% |
| blowoff_recent_3d | 0.3% |
| break_52w_high | 0.1% |
| break_52w_high_confirmed_today | 0.1% |
| break_52w_low | 0.5% |
| bullish_engulfing | 6.3% |
| bullish_pin_bar | 1.1% |
| capitulation_recent_3d | 0.8% |
| ceo_buy | 1.4% |
| cfo_buy | 0.6% |
| chandelier_long_bullish | 59.5% |
| chandelier_long_flip_dn | 8.6% |
| chandelier_short_bearish | 68.7% |
| chandelier_short_flip_up | 8.5% |
| classification_change_from_tech | 42.9% |
| classification_change_to_defensive | 57.1% |
| close_above_open | 51.2% |
| close_below_open | 48.8% |
| close_in_bottom_40pct_of_range | 48.8% |
| close_in_top_40pct_of_range | 51.2% |
| cluster_buy | 0.7% |
| cmf_cross_dn | 5.5% |
| cmf_cross_up | 5.7% |
| cmf_negative | 48.5% |
| cmf_positive | 51.4% |
| concentrated_sell | 5.9% |
| cpr_narrow | 89.3% |
| cpr_narrow_tight | 28.1% |
| cup_handle_detected | 13.1% |
| cup_handle_neckline_break_retest_long | 2.2% |
| dc10_breakout_dn | 16.0% |
| dc10_breakout_dn_1pct | 24.1% |
| dc10_breakout_up | 18.4% |
| dc10_breakout_up_1pct | 26.0% |
| dc10_new_high | 19.6% |
| dc10_strong_breakout_dn | 3.6% |
| dc10_strong_breakout_up | 4.7% |
| dc20_breakout_dn | 8.7% |
| dc20_breakout_up | 7.5% |
| dc20_new_high | 8.0% |
| dc20_resistance_break_retest_strong | 6.6% |
| dc20_support_break_retest_strong | 10.0% |
| defensive_leadership | 55.8% |
| director_only_buy | 4.4% |
| doji | 0.5% |
| double_bottom_detected | 11.0% |
| double_top_detected | 13.4% |
| dpi_elevated | 54.3% |
| drying_volume_on_down_turn | 48.8% |
| drying_volume_on_up_turn | 51.2% |
| ema_20_50_bearish | 59.6% |
| ema_20_50_bullish | 40.4% |
| ema_20_50_death_cross | 1.0% |
| ema_20_50_golden_cross | 0.6% |
| ema_50_200_bearish | 56.7% |
| ema_50_200_bullish | 43.3% |
| ema_50_200_death_cross | 0.2% |
| ema_50_200_golden_cross | 0.1% |
| ema_9_21_bearish | 59.4% |
| ema_9_21_bullish | 40.6% |
| ema_9_21_death_cross | 2.8% |
| ema_9_21_golden_cross | 3.7% |
| evening_star | 8.3% |
| flag_bear_break_retest_short | 0.4% |
| flag_bear_broke | 0.6% |
| flag_bear_detected | 0.9% |
| flag_bull_break_retest_long | 0.7% |
| flag_bull_broke | 0.8% |
| flag_bull_detected | 2.3% |
| force_index_cross_dn | 9.5% |
| force_index_cross_up | 11.2% |
| force_index_positive | 48.2% |
| gap_dn_1_5pct | 4.5% |
| gap_dn_2pct | 1.9% |
| gap_up_1_5pct | 6.6% |
| gap_up_2pct | 2.8% |
| hammer | 1.0% |
| head_shoulders_bottom_detected | 3.6% |
| head_shoulders_top_detected | 4.6% |
| house_cluster_buy | 4.1% |
| house_cluster_sell | 4.3% |
| htf_aligned_bear | 42.4% |
| htf_aligned_bull | 26.2% |
| htf_disagreement | 2.6% |
| hull_bearish | 46.6% |
| hull_bullish | 53.4% |
| hull_flip_dn | 6.9% |
| hull_flip_up | 8.1% |
| ichi_above_cloud | 35.3% |
| ichi_above_cloud_break_recent_5d | 4.9% |
| ichi_below_cloud | 52.7% |
| ichi_below_cloud_break_recent_5d | 6.9% |
| ichi_cloud_thick | 85.7% |
| ichi_tk_bearish | 58.0% |
| ichi_tk_bullish | 39.6% |
| ichi_tk_cross_dn | 2.3% |
| ichi_tk_cross_up | 2.4% |
| ichi_weekly_above_cloud | 34.4% |
| ichi_weekly_below_cloud | 34.8% |
| ichi_weekly_in_cloud | 30.7% |
| in_reversal_window | 2.5% |
| inside_bar | 2.8% |
| inside_kc | 90.9% |
| insider_cluster_active | 24.5% |
| institutional_buy | 88.9% |
| institutional_negative | 5.0% |
| institutional_persistence_growing | 42.4% |
| institutional_persistence_strong | 57.8% |
| institutional_strong_buy | 78.4% |
| inverted_cup_handle_detected | 10.2% |
| is_friday | 19.4% |
| is_halloween_period | 50.0% |
| is_halloween_period_first_day | 0.3% |
| is_january | 8.6% |
| is_january_extended | 12.4% |
| is_monday | 16.6% |
| is_pre_holiday | 5.6% |
| is_summer_period | 50.0% |
| is_totm_window | 36.2% |
| is_totm_window_first_day | 10.0% |
| is_week_open | 19.4% |
| kc_touch_lower | 7.6% |
| kc_touch_upper | 4.4% |
| large_dollar_buy | 1.3% |
| macd_12_26_9_bearish | 48.8% |
| macd_12_26_9_bullish | 51.2% |
| macd_12_26_9_crossover_dn | 7.9% |
| macd_12_26_9_crossover_up | 9.0% |
| macd_8_21_5_bearish | 45.4% |
| macd_8_21_5_bullish | 54.6% |
| macd_8_21_5_crossover_dn | 2.2% |
| macd_8_21_5_crossover_up | 2.6% |
| marubozu_bear | 1.7% |
| marubozu_bull | 1.9% |
| mfi_broad_overbought | 7.1% |
| mfi_broad_oversold | 8.4% |
| mfi_overbought | 1.2% |
| mfi_oversold | 1.7% |
| monthly_above_sma_12 | 41.7% |
| monthly_above_sma_6 | 40.0% |
| monthly_bias_bear | 51.4% |
| monthly_bias_bull | 33.1% |
| monthly_momentum_pos | 43.3% |
| morning_star | 6.7% |
| near_52w_high | 0.7% |
| near_52w_high_95pct | 9.5% |
| near_52w_high_retest_long | 0.3% |
| near_52w_low | 1.0% |
| near_52w_low_105pct | 4.5% |
| near_52w_low_retest_short | 0.4% |
| near_avwap_20high_atr_05x | 30.3% |
| near_avwap_20high_atr_10x | 60.5% |
| near_avwap_20high_atr_15x | 80.9% |
| near_avwap_20high_atr_20x | 91.8% |
| near_avwap_20low_atr_05x | 31.9% |
| near_avwap_20low_atr_10x | 61.6% |
| near_avwap_20low_atr_15x | 81.0% |
| near_avwap_20low_atr_20x | 90.8% |
| near_avwap_252low_atr_05x | 12.1% |
| near_avwap_252low_atr_10x | 29.4% |
| near_avwap_252low_atr_15x | 43.5% |
| near_avwap_252low_atr_20x | 53.7% |
| near_avwap_50low_atr_05x | 19.8% |
| near_avwap_50low_atr_10x | 44.8% |
| near_avwap_50low_atr_15x | 64.8% |
| near_avwap_50low_atr_20x | 78.2% |
| near_cam_r3 | 1.3% |
| near_cam_s3 | 1.5% |
| near_cam_s4 | 12.8% |
| near_fib_236 | 5.5% |
| near_fib_382 | 5.5% |
| near_fib_500 | 5.1% |
| near_fib_618 | 6.0% |
| near_fib_786 | 6.2% |
| near_pivot | 0.1% |
| near_prev_close | 0.1% |
| near_prev_high | 8.4% |
| near_prev_low | 10.2% |
| near_r1 | 9.6% |
| near_r1_wide | 41.4% |
| near_r2 | 12.5% |
| near_r2_wide | 45.3% |
| near_s1 | 11.8% |
| near_s1_wide | 40.7% |
| near_s2 | 13.1% |
| near_s2_wide | 43.3% |
| near_s3 | 5.8% |
| near_wood_r1 | 7.7% |
| near_wood_s1 | 8.3% |
| news_uses_polygon_score | 20.2% |
| obv_bearish | 50.2% |
| obv_bullish | 49.8% |
| obv_diverge_bull | 9.3% |
| obv_falling | 47.9% |
| obv_rising | 52.1% |
| outside_bar | 15.7% |
| pead_negative_surprise | 18.6% |
| pead_positive_surprise | 22.7% |
| pin_bar | 2.1% |
| po3_accumulation_active | 42.7% |
| po3_bearish | 11.0% |
| po3_bullish | 8.2% |
| po3_manipulation_sweep_down | 16.3% |
| po3_manipulation_sweep_up | 12.2% |
| po3_mmbm_setup | 0.6% |
| po3_mmsm_setup | 1.5% |
| po3_sweep_above_prior_high | 62.3% |
| po3_sweep_below_prior_low | 55.9% |
| ppo_bullish | 49.4% |
| ppo_crossover_dn | 6.7% |
| ppo_crossover_up | 9.2% |
| pre_fomc_d0 | 2.8% |
| pre_fomc_d1 | 2.0% |
| pre_fomc_window | 4.8% |
| price_above_dema | 51.8% |
| price_above_ema_20 | 46.5% |
| price_above_ema_200 | 40.6% |
| price_above_ema_200_break_recent_5d | 5.3% |
| price_above_ema_20_break_recent_5d | 28.0% |
| price_above_ema_21 | 46.5% |
| price_above_ema_21_break_recent_5d | 27.1% |
| price_above_ema_50 | 41.8% |
| price_above_ema_50_break_recent_5d | 12.8% |
| price_above_ema_9 | 50.9% |
| price_above_ema_9_break_recent_5d | 40.6% |
| price_above_hull | 54.9% |
| price_above_sma_200 | 41.8% |
| price_above_sma_21 | 47.2% |
| price_above_sma_50 | 41.9% |
| price_above_tema | 55.1% |
| price_below_dema | 48.2% |
| price_below_hull | 45.1% |
| price_below_tema | 44.9% |
| psar_bullish | 50.0% |
| psar_flip_dn | 5.3% |
| psar_flip_up | 7.5% |
| r1_break_retest_long | 58.6% |
| resistance_break_retest | 9.6% |
| risk_off_regime_bond_signal | 25.4% |
| risk_off_regime_bond_signal_strong | 7.2% |
| risk_off_regime_gold_signal | 41.6% |
| risk_on_regime_bond_signal | 43.8% |
| risk_on_regime_bond_signal_strong | 17.1% |
| roc_positive | 49.3% |
| roc_turning_dn | 10.2% |
| roc_turning_up | 13.7% |
| rsi_14_bullish | 44.9% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_14_cross_dn_overbought_recent_3d | 3.0% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.2% |
| rsi_14_cross_up_oversold_recent_3d | 3.5% |
| rsi_14_extreme_os | 0.1% |
| rsi_14_overbought | 1.2% |
| rsi_14_oversold | 2.2% |
| rsi_14_rising | 51.2% |
| rsi_21_bullish | 42.1% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_21_cross_dn_overbought_recent_3d | 1.6% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 1.6% |
| rsi_21_extreme_os | 0.1% |
| rsi_21_overbought | 0.3% |
| rsi_21_oversold | 0.6% |
| rsi_21_rising | 51.2% |
| rsi_2_bullish | 51.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 20.2% |
| rsi_2_cross_dn_overbought_recent_3d | 26.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 21.0% |
| rsi_2_cross_up_oversold_recent_3d | 26.1% |
| rsi_2_extreme_ob | 35.6% |
| rsi_2_extreme_os | 31.2% |
| rsi_2_overbought | 45.5% |
| rsi_2_oversold | 41.6% |
| rsi_2_rising | 51.2% |
| rsi_9_bullish | 47.8% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.4% |
| rsi_9_cross_dn_overbought_recent_3d | 4.2% |
| rsi_9_cross_up_extreme_os_recent_3d | 1.0% |
| rsi_9_cross_up_oversold_recent_3d | 5.5% |
| rsi_9_extreme_ob | 0.7% |
| rsi_9_extreme_os | 0.9% |
| rsi_9_overbought | 4.4% |
| rsi_9_oversold | 7.2% |
| rsi_9_rising | 51.2% |
| s1_break_retest_short | 56.8% |
| sc_13d_filed_within_30d | 3.1% |
| sc_13g_filed_within_30d | 3.0% |
| sector_outperforming_spy | 38.1% |
| sector_underperforming_spy | 61.9% |
| shooting_star | 1.2% |
| sma_20_50_bullish | 42.0% |
| sma_20_50_golden_cross | 0.5% |
| sma_50_200_bullish | 45.1% |
| sma_50_200_golden_cross | 0.3% |
| sma_9_21_bullish | 42.5% |
| sma_9_21_golden_cross | 3.3% |
| smc_bos_bearish | 16.4% |
| smc_bos_bullish | 11.7% |
| smc_bos_retest_long | 4.2% |
| smc_bos_retest_short | 4.3% |
| smc_breaker_block_bearish | 17.6% |
| smc_breaker_block_bullish | 19.7% |
| smc_choch_bearish | 5.5% |
| smc_choch_bullish | 3.3% |
| smc_equal_highs_swept | 3.3% |
| smc_equal_lows_swept | 4.5% |
| smc_fvg_bearish_active | 31.2% |
| smc_fvg_bullish_active | 35.6% |
| smc_fvg_retest_long_zone | 4.9% |
| smc_fvg_retest_short_zone | 5.3% |
| smc_in_discount_zone | 67.4% |
| smc_in_premium_zone | 53.1% |
| smc_inverse_fvg_bearish | 89.3% |
| smc_inverse_fvg_bullish | 82.2% |
| smc_liquidity_swept_dn | 1.5% |
| smc_liquidity_swept_up | 1.0% |
| smc_mitigation_block_long | 1.3% |
| smc_mitigation_block_short | 1.0% |
| smc_ob_bearish_active | 43.0% |
| smc_ob_bullish_active | 28.6% |
| smc_ote_long_zone | 7.9% |
| smc_ote_short_zone | 5.5% |
| squeeze_fire_dn | 5.1% |
| squeeze_fire_up | 5.7% |
| squeeze_in | 29.0% |
| squeeze_positive | 46.0% |
| stoch_bearish_cross | 10.7% |
| stoch_broad_overbought | 17.8% |
| stoch_broad_oversold | 19.4% |
| stoch_bullish_cross | 10.9% |
| stoch_overbought | 13.7% |
| stoch_oversold | 14.3% |
| stochrsi_cross_dn | 16.3% |
| stochrsi_cross_up | 16.8% |
| stochrsi_overbought | 38.7% |
| stochrsi_oversold | 34.0% |
| supertrend_bearish | 0.1% |
| supertrend_bullish | 99.9% |
| supertrend_flip_recent_long_5d | 1.4% |
| supertrend_flip_recent_short_5d | 0.2% |
| supertrend_flip_up | 0.1% |
| support_break_retest | 15.0% |
| tema_above_dema | 47.3% |
| tema_cross_dn | 4.3% |
| tema_cross_up | 5.2% |
| three_black_crows | 6.6% |
| three_white_soldiers | 8.2% |
| triangle_apex_break_retest_long | 8.2% |
| triangle_ascending_detected | 6.5% |
| triangle_descending_detected | 9.3% |
| uo_overbought | 1.3% |
| uo_oversold | 1.2% |
| usd_strengthening | 28.3% |
| usd_weakening | 12.2% |
| vix_band_high | 42.3% |
| vix_band_low | 33.8% |
| vix_band_mid | 23.8% |
| vix_term_backwardation | 7.4% |
| vix_term_contango | 92.6% |
| vol_spike_2x_on_down_day_recent_3d | 1.2% |
| vol_spike_2x_on_up_day_recent_3d | 0.9% |
| vp_above_value_area | 16.0% |
| vp_below_value_area | 19.4% |
| vp_close_above_poc | 48.9% |
| vp_close_below_poc | 51.1% |
| vp_in_value_area | 64.6% |
| week_open_gap_down_15pct | 1.0% |
| week_open_gap_up_15pct | 1.3% |
| weekly_above_ema_10 | 41.8% |
| weekly_above_ema_20 | 40.0% |
| weekly_bias_bear | 52.1% |
| weekly_bias_bull | 33.9% |
| weekly_momentum_pos | 43.3% |
| williams_r_overbought | 24.6% |
| williams_r_oversold | 24.6% |
| williams_r_rising | 51.6% |
| within_pead_window | 39.6% |
| within_post_deletion_window | 8.8% |
| within_post_inclusion_window | 2.7% |
| within_pre_rebalance_window | 0.3% |
| xs_avoid_high_ivol | 72.6% |
| xs_avoid_high_max | 74.8% |
| xs_high_beta_decile | 26.1% |
| xs_low_beta_bottom_quintile | 26.1% |
| xs_low_beta_decile | 16.0% |
| xs_low_beta_decile_entry_recent_5d | 0.3% |
| xs_low_beta_top_quintile | 16.0% |
| xs_momentum_bottom_decile | 13.9% |
| xs_momentum_bottom_quintile | 25.4% |
| xs_momentum_top_decile | 10.3% |
| xs_momentum_top_quintile | 18.7% |
| xs_quality_bottom_quintile | 21.1% |
| xs_quality_top_quintile | 20.3% |
| xs_quality_top_tercile | 40.8% |
| year_high_break_retest_long | 0.7% |
| year_low_break_retest_short | 1.2% |
| yoy_surprise_high | 49.4% |
| yoy_surprise_negative | 40.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.0% |
| committed_growth_holders | 91.0% |
| corp_donations_1y | 6.9% |
| corp_donations_count_1y | 6.9% |
| corp_donations_unique_pacs | 6.9% |
| cot_rut_commercials_pctile_3y | 49.5% |
| cot_rut_mmoney_pctile_3y | 49.5% |
| cup_handle_depth_pct | 18.2% |
| days_since_classification_change | 0.2% |
| days_since_deletion | 8.1% |
| days_since_inclusion | 13.1% |
| days_to_next_holiday | 63.7% |
| days_to_rebalance | 10.3% |
| dpi_30d_avg | 95.5% |
| dpi_recent | 95.5% |
| earnings_announcement_return | 92.2% |
| earnings_eps_yoy_growth | 94.4% |
| flag_bear_pole_move_pct | 0.9% |
| flag_bull_pole_move_pct | 2.3% |
| gov_contracts_4q_sum | 40.3% |
| gov_contracts_last_qtr_amount | 40.3% |
| gov_contracts_qoq_growth | 40.3% |
| head_shoulders_magnitude_pct | 8.0% |
| insider_director_buyers_30d | 7.1% |
| insider_officer_buyers_30d | 7.1% |
| insider_total_shares_bought_30d | 7.1% |
| insider_unique_buyers_30d | 7.1% |
| inverted_cup_handle_height_pct | 15.6% |
| lobbying_amount_1y | 70.3% |
| lobbying_amount_q | 70.3% |
| lobbying_amount_yoy | 70.3% |
| monthly_momentum_6m | 97.6% |
| otc_short_ratio_recent | 95.5% |
| otc_volume_recent | 95.5% |
| pair_half_life | 92.3% |
| pair_max_abs_zscore | 92.3% |
| pair_zscore_signed | 92.3% |
| pct_from_avwap_20high | 91.5% |
| pct_from_avwap_20low | 89.8% |
| pct_from_avwap_252low | 97.2% |
| pct_from_avwap_50low | 96.0% |
| persistent_holders_4q | 91.0% |
| persistent_holders_8q | 91.0% |
| sc_13g_latest_percent_owned | 1.4% |
| search_volume_index_recent | 77.4% |
| search_volume_observations | 77.4% |
| search_volume_zscore_30d | 77.4% |
| sector_etf_return_20d | 2.5% |
| spy_return_20d | 2.5% |
| total_active_holders | 91.0% |
| triangle_breakdown_pct | 9.3% |
| triangle_breakout_pct | 6.5% |
| xs_quality_decile | 61.9% |
| xs_quality_gross_profitability | 61.9% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.994), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.997), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.998), `double_top_neckline` (0.996), `double_top_peak` (0.996), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.995), `fib_382` (0.996), `fib_500` (0.997), `fib_618` (0.997), `fib_786` (0.997), `fib_ext_127` (0.99), `fib_ext_162` (0.987), `flag_bear_breakdown_level` (0.999), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.999), `ichi_kijun` (0.999), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.988), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.98), `monthly_sma_6` (0.993), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.998), `swing_high` (0.993), `swing_low` (0.997), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.995), `vp_value_area_low` (0.996), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.995), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.966), `year_low` (0.972)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P3.1 | buffer pct (price vs avwap anchored at 2 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P5.1 | (structural) c > o - optional min body p | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P6.1 | mirror of close_above_open | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P7.1 | mirror of top_40pct | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P8.1 | range-position cutoff | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P9.1 | span triple (fast, slow, signal) | 2 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 1 |
| P10.1 | span triple (mirror of the bearish entry | 2 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 1 |
| P13.1 | volume ratio ceiling (vol / avg, strict  | 3 | subset-safe | no - derives offline | 1 | 2 | 0 |
| P14 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     3 x 3 x 3 x 3 x 3 x 2 x 2 x 3 x 1 = 2916
offline gradings   2 level-combinations x 24 exits = 48 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  2913 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 2 + 2913 = 2916 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 643 census axes join it only when REGISTERED at the T3 band review.
