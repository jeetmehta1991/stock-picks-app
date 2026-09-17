# Table A - morning_star

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** candle | **status:** NOT-STARTED | **R5 fires:** 2280 | **surviving fires (T1):** 1053 (survives_pct 0.4618)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  evening_star  <- backtest/signals/screener.py +1
       knobs P1.1-P1.1 (band rows in Table A)
P2  morning_star  <- backtest/signals/screener.py +1
       knobs P2.1-P2.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  rsi_14 < 45   [EXISTING-THRESHOLD]
P4  rsi_14 > 55   [EXISTING-THRESHOLD]
P5  squeeze_momentum <= 0.0096   [EXISTING-THRESHOLD]
P6  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_morning_star (docstring and return dropped):

```python
fl = s.get('morning_star') and s.get('rsi_14', 50) < 45
fl = fl and s.get('squeeze_momentum', float('inf')) <= 0.0096
fs = (s.get('evening_star') and s.get('rsi_14', 50) > 55) and (not _short_borrow_trap_active(s))
fs = fs and s.get('squeeze_momentum', float('inf')) <= 0.0096
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
| P1 | PRODUCER | evening_star - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | mirror of morning_star's two knobs - backtest/signals/technical.py:2095-2100 | 0.3 / midpoint | none | the whole band; DEFINED-NO-ACTUATOR | mirror; T3 review before any grid |
| P2 | PRODUCER | morning_star - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | mid-candle small-body ratio (body < X * range) - backtest/signals/technical.py:2088 | 0.3 | none - the mid bar's body/range unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production (the one EXPLICIT candle knob); T3 review before any grid |
| P2.2 | BAND | recovery rule (close above midpoint of bar-3) - technical.py:2093 | structural | none | the whole band; DEFINED-NO-ACTUATOR | BRACKET the midpoint rule; T3 review before any grid |
| P3 | STRATEGY | rsi_14 `< 45` [EXISTING-THRESHOLD] | `< 45` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3.1 | BAND | rsi span - backtest/signals/technical.py rsi block | 14 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P4 | STRATEGY | rsi_14 `> 55` [EXISTING-THRESHOLD] | `> 55` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4.1 | BAND | rsi span - backtest/signals/technical.py rsi block | 14 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P5 | STRATEGY | squeeze_momentum `<= 0.0096` [EXISTING-THRESHOLD] | `<= 0.0096` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 45` | 100.0% | TIGHTER = LOWER the ceiling: 34.832 -> 211 (20%); 38.416 -> 421 (40%); 40.68 -> 634 (60%); 43.012 -> 842 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `> 55` | 100.0% | TIGHTER = RAISE the floor: (no QUANTS level sits tighter than production - band at T3) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| squeeze_momentum | backtest/signals/screener.py +1 | `<= 0.0096` | 100.0% | TIGHTER = LOWER the ceiling: -7.707 -> 211 (20%); -4.0938 -> 421 (40%); -2.3375 -> 632 (60%); -1.0855 -> 842 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 19.512, 25.13, 29.924, 36.632 | 19.512: 842 (80%); 25.13: 633 (60%); 29.924: 421 (40%); 36.632: 211 (20%) | 19.512: 211 (20%); 25.13: 423 (40%); 29.924: 632 (60%); 36.632: 842 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 26.028, 28.96, 31.324, 34.472 | 26.028: 842 (80%); 28.96: 633 (60%); 31.324: 421 (40%); 34.472: 211 (20%) | 26.028: 211 (20%); 28.96: 423 (40%); 31.324: 632 (60%); 34.472: 842 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.224, 15.688, 17.522, 20.026 | 13.224: 842 (80%); 15.688: 632 (60%); 17.522: 421 (40%); 20.026: 211 (20%) | 13.224: 211 (20%); 15.688: 421 (40%); 17.522: 632 (60%); 20.026: 842 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -12.6324, -7.1178, -4.1266, -2.0844 | -12.6324: 842 (80%); -7.1178: 632 (60%); -4.1266: 421 (40%); -2.0844: 211 (20%) | -12.6324: 211 (20%); -7.1178: 421 (40%); -4.1266: 632 (60%); -2.0844: 842 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.0296, 1.8587, 2.9816, 5.4082 | 1.0296: 842 (80%); 1.8587: 633 (60%); 2.9816: 421 (40%); 5.4082: 211 (20%) | 1.0296: 211 (20%); 1.8587: 422 (40%); 2.9816: 632 (60%); 5.4082: 842 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.0296, 1.8587, 2.9816, 5.4082 | 1.0296: 842 (80%); 1.8587: 633 (60%); 2.9816: 421 (40%); 5.4082: 211 (20%) | 1.0296: 211 (20%); 1.8587: 422 (40%); 2.9816: 632 (60%); 5.4082: 842 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.1998, 2.7782, 3.3422, 4.263 | 2.1998: 842 (80%); 2.7782: 632 (60%); 3.3422: 421 (40%); 4.263: 211 (20%) | 2.1998: 211 (20%); 2.7782: 421 (40%); 3.3422: 632 (60%); 4.263: 842 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0608, 0.0896, 0.1257, 0.1776 | 0.0608: 843 (80%); 0.0896: 632 (60%); 0.1257: 423 (40%); 0.1776: 211 (20%) | 0.0608: 212 (20%); 0.0896: 422 (40%); 0.1257: 633 (60%); 0.1776: 842 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.3026, 0.3598, 0.4279, 0.5595 | 0.3026: 843 (80%); 0.3598: 632 (60%); 0.4279: 421 (40%); 0.5595: 211 (20%) | 0.3026: 211 (20%); 0.3598: 422 (40%); 0.4279: 632 (60%); 0.5595: 842 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0762, 0.1101, 0.1436, 0.1941 | 0.0762: 843 (80%); 0.1101: 632 (60%); 0.1436: 422 (40%); 0.1941: 211 (20%) | 0.0762: 211 (20%); 0.1101: 422 (40%); 0.1436: 633 (60%); 0.1941: 842 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.0808, 0.1472, 0.217, 0.3112 | 0.0808: 842 (80%); 0.1472: 632 (60%); 0.217: 422 (40%); 0.3112: 211 (20%) | 0.0808: 211 (20%); 0.1472: 422 (40%); 0.217: 633 (60%); 0.3112: 842 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1017, 0.1468, 0.1914, 0.2587 | 0.1017: 843 (80%); 0.1468: 632 (60%); 0.1914: 422 (40%); 0.2587: 211 (20%) | 0.1017: 212 (20%); 0.1468: 422 (40%); 0.1914: 633 (60%); 0.2587: 842 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.1856, 0.2354, 0.2878, 0.3584 | 0.1856: 842 (80%); 0.2354: 633 (60%); 0.2878: 422 (40%); 0.3584: 211 (20%) | 0.1856: 211 (20%); 0.2354: 422 (40%); 0.2878: 634 (60%); 0.3584: 842 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0403, -0.0134, 0.0049, 0.0361 | -0.0403: 843 (80%); -0.0134: 634 (60%); 0.0049: 422 (40%); 0.0361: 212 (20%) | -0.0403: 212 (20%); -0.0134: 424 (40%); 0.0049: 634 (60%); 0.0361: 844 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.145, 0.1743, 0.2168, 0.2762 | 0.145: 843 (80%); 0.1743: 632 (60%); 0.2168: 421 (40%); 0.2762: 214 (20%) | 0.145: 210 (20%); 0.1743: 421 (40%); 0.2168: 632 (60%); 0.2762: 839 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1053 (100%) | 0: 982 (93%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1879, -0.1103, -0.0456, 0.0258 | -0.1879: 842 (80%); -0.1103: 632 (60%); -0.0456: 422 (40%); 0.0258: 211 (20%) | -0.1879: 211 (20%); -0.1103: 422 (40%); -0.0456: 632 (60%); 0.0258: 842 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1053 (100%); 1: 437 (42%) | 0: 616 (58%); 1: 868 (82%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2296, -0.1736, -0.1433, -0.0994 | -0.2296: 843 (80%); -0.1736: 635 (60%); -0.1433: 423 (40%); -0.0994: 214 (20%) | -0.2296: 211 (20%); -0.1736: 427 (41%); -0.1433: 633 (60%); -0.0994: 852 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4167, 0.6474, 0.7385, 0.8218 | 0.4167: 851 (81%); 0.6474: 636 (60%); 0.7385: 421 (40%); 0.8218: 211 (20%) | 0.4167: 213 (20%); 0.6474: 459 (44%); 0.7385: 632 (60%); 0.8218: 842 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2115, 0.2987, 0.5897, 0.8141 | 0.2115: 853 (81%); 0.2987: 632 (60%); 0.5897: 436 (41%); 0.8141: 217 (21%) | 0.2115: 228 (22%); 0.2987: 421 (40%); 0.5897: 635 (60%); 0.8141: 850 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0824, 0.0158, 0.1292, 0.2516 | -0.0824: 848 (81%); 0.0158: 636 (60%); 0.1292: 421 (40%); 0.2516: 213 (20%) | -0.0824: 218 (21%); 0.0158: 423 (40%); 0.1292: 632 (60%); 0.2516: 849 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3039, 0.5, 0.6731, 0.8654 | 0.3039: 842 (80%); 0.5: 637 (60%); 0.6731: 457 (43%); 0.8654: 214 (20%) | 0.3039: 211 (20%); 0.5: 428 (41%); 0.6731: 658 (62%); 0.8654: 861 (82%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0705, 0.3462, 0.4936, 0.6538 | 0.0705: 844 (80%); 0.3462: 633 (60%); 0.4936: 425 (40%); 0.6538: 246 (23%) | 0.0705: 214 (20%); 0.3462: 422 (40%); 0.4936: 647 (61%); 0.6538: 853 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5326, -0.388, -0.2241, -0.0228 | -0.5326: 860 (82%); -0.388: 647 (61%); -0.2241: 421 (40%); -0.0228: 214 (20%) | -0.5326: 213 (20%); -0.388: 452 (43%); -0.2241: 632 (60%); -0.0228: 845 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2949, 0.4872, 0.609, 0.9167 | 0.2949: 847 (80%); 0.4872: 643 (61%); 0.609: 426 (40%); 0.9167: 232 (22%) | 0.2949: 219 (21%); 0.4872: 425 (40%); 0.609: 653 (62%); 0.9167: 853 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.2628, 0.4872, 0.7526 | 0.0962: 843 (80%); 0.2628: 644 (61%); 0.4872: 425 (40%); 0.7526: 211 (20%) | 0.0962: 213 (20%); 0.2628: 431 (41%); 0.4872: 651 (62%); 0.7526: 842 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0681, -0.0572, -0.0397, 0 | -0.0681: 845 (80%); -0.0572: 640 (61%); -0.0397: 421 (40%); 0: 278 (26%) | -0.0681: 223 (21%); -0.0572: 423 (40%); -0.0397: 632 (60%); 0: 998 (95%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4385, 0.7372, 0.8846, 1 | 0.4385: 842 (80%); 0.7372: 634 (60%); 0.8846: 445 (42%); 1: 215 (20%) | 0.4385: 211 (20%); 0.7372: 423 (40%); 0.8846: 651 (62%); 1: 1053 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0769, 0.1923, 0.4936, 0.8397 | 0.0769: 855 (81%); 0.1923: 641 (61%); 0.4936: 425 (40%); 0.8397: 212 (20%) | 0.0769: 231 (22%); 0.1923: 437 (42%); 0.4936: 633 (60%); 0.8397: 852 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0099, 0.0383, 0.0848, 0.2042 | -0.0099: 845 (80%); 0.0383: 655 (62%); 0.0848: 422 (40%); 0.2042: 211 (20%) | -0.0099: 212 (20%); 0.0383: 425 (40%); 0.0848: 642 (61%); 0.2042: 842 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4966, 0.7829, 0.9462, 0.9744 | 0.4966: 846 (80%); 0.7829: 637 (60%); 0.9462: 426 (40%); 0.9744: 262 (25%) | 0.4966: 223 (21%); 0.7829: 423 (40%); 0.9462: 639 (61%); 0.9744: 844 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0843, 0.2051, 0.4932, 0.7821 | 0.0843: 857 (81%); 0.2051: 639 (61%); 0.4932: 424 (40%); 0.7821: 214 (20%) | 0.0843: 218 (21%); 0.2051: 447 (42%); 0.4932: 634 (60%); 0.7821: 849 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, 0.0566, 0.1225, 0.3175 | -0.0812: 961 (91%); 0.0566: 657 (62%); 0.1225: 465 (44%); 0.3175: 248 (24%) | -0.0812: 212 (20%); 0.0566: 452 (43%); 0.1225: 654 (62%); 0.3175: 1017 (97%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0935, 0.0214, 0.0551, 0.0978 | -0.0935: 842 (80%); 0.0214: 639 (61%); 0.0551: 434 (41%); 0.0978: 216 (21%) | -0.0935: 211 (20%); 0.0214: 433 (41%); 0.0551: 665 (63%); 0.0978: 846 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3718, 0.6603, 0.7564, 0.891 | 0.3718: 849 (81%); 0.6603: 633 (60%); 0.7564: 465 (44%); 0.891: 228 (22%) | 0.3718: 213 (20%); 0.6603: 423 (40%); 0.7564: 634 (60%); 0.891: 845 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.3013, 0.5449, 0.7821 | 0.109: 851 (81%); 0.3013: 636 (60%); 0.5449: 424 (40%); 0.7821: 236 (22%) | 0.109: 231 (22%); 0.3013: 434 (41%); 0.5449: 635 (60%); 0.7821: 847 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0233, 0.0583, 0.12, 0.248 | 0.0233: 851 (81%); 0.0583: 635 (60%); 0.12: 423 (40%); 0.248: 211 (20%) | 0.0233: 214 (20%); 0.0583: 424 (40%); 0.12: 635 (60%); 0.248: 842 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.5% | 28.2, 56, 76.6, 134.8 | 28.2: 829 (79%); 56: 626 (59%); 76.6: 415 (39%); 134.8: 208 (20%) | 28.2: 208 (20%); 56: 423 (40%); 76.6: 622 (59%); 134.8: 829 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.6939, 2.2268, 2.9263, 4.0174 | 1.6939: 839 (80%); 2.2268: 629 (60%); 2.9263: 420 (40%); 4.0174: 210 (20%) | 1.6939: 210 (20%); 2.2268: 420 (40%); 2.9263: 629 (60%); 4.0174: 839 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 20, 28, 35 | 8: 861 (82%); 20: 640 (61%); 28: 439 (42%); 35: 252 (24%) | 8: 226 (21%); 20: 447 (42%); 28: 640 (61%); 35: 862 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 2, 3 | 0: 1053 (100%); 1: 828 (79%); 2: 576 (55%); 3: 358 (34%) | 0: 225 (21%); 1: 477 (45%); 2: 695 (66%); 3: 878 (83%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0102, 0.004, 0.0179, 0.0288 | -0.0102: 850 (81%); 0.004: 634 (60%); 0.0179: 422 (40%); 0.0288: 218 (21%) | -0.0102: 212 (20%); 0.004: 428 (41%); 0.0179: 639 (61%); 0.0288: 849 (81%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.4417, 25.7776, 26.3984, 27.08 | 24.4417: 842 (80%); 25.7776: 634 (60%); 26.3984: 426 (40%); 27.08: 214 (20%) | 24.4417: 211 (20%); 25.7776: 423 (40%); 26.3984: 638 (61%); 27.08: 845 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -1.0012, -0.397, -0.03, 0.4786 | -1.0012: 842 (80%); -0.397: 632 (60%); -0.03: 422 (40%); 0.4786: 211 (20%) | -1.0012: 211 (20%); -0.397: 421 (40%); -0.03: 633 (60%); 0.4786: 842 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.4786, 0.03, 0.397, 1.0012 | -0.4786: 842 (80%); 0.03: 633 (60%); 0.397: 421 (40%); 1.0012: 211 (20%) | -0.4786: 211 (20%); 0.03: 422 (40%); 0.397: 632 (60%); 1.0012: 842 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0428, -0.0037, 0.0203, 0.0611 | -0.0428: 842 (80%); -0.0037: 644 (61%); 0.0203: 426 (40%); 0.0611: 212 (20%) | -0.0428: 211 (20%); -0.0037: 423 (40%); 0.0203: 634 (60%); 0.0611: 844 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.096, 8.5205, 8.7704, 9.013 | 8.096: 843 (80%); 8.5205: 627 (60%); 8.7704: 418 (40%); 9.013: 211 (20%) | 8.096: 210 (20%); 8.5205: 426 (40%); 8.7704: 635 (60%); 9.013: 842 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1046 (99%); 1: 301 (29%) | 0: 745 (71%); 1: 955 (91%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0 | 0: 838 (80%) | 0: 878 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1046 (99%); 1: 325 (31%) | 0: 721 (68%); 1: 949 (90%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 6, 136, 251 | 3: 862 (82%); 6: 653 (62%); 136: 422 (40%); 251: 213 (20%) | 3: 272 (26%); 6: 451 (43%); 136: 633 (60%); 251: 845 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 78, 129 | 1: 849 (81%); 4: 648 (62%); 78: 423 (40%); 129: 213 (20%) | 1: 292 (28%); 4: 442 (42%); 78: 634 (60%); 129: 844 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.9344, -0.4018, -0.1738, 0.0253 | -0.9344: 842 (80%); -0.4018: 632 (60%); -0.1738: 421 (40%); 0.0253: 211 (20%) | -0.9344: 211 (20%); -0.4018: 421 (40%); -0.1738: 632 (60%); 0.0253: 842 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -4.7838, -2.6602, -1.5711, -0.7829 | -4.7838: 842 (80%); -2.6602: 632 (60%); -1.5711: 422 (40%); -0.7829: 211 (20%) | -4.7838: 211 (20%); -2.6602: 421 (40%); -1.5711: 632 (60%); -0.7829: 842 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -4.2532, -2.1448, -1.1073, -0.505 | -4.2532: 842 (80%); -2.1448: 632 (60%); -1.1073: 421 (40%); -0.505: 211 (20%) | -4.2532: 211 (20%); -2.1448: 421 (40%); -1.1073: 632 (60%); -0.505: 842 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.4454, -0.1323, -0.0108, 0.2006 | -0.4454: 842 (80%); -0.1323: 632 (60%); -0.0108: 421 (40%); 0.2006: 211 (20%) | -0.4454: 211 (20%); -0.1323: 421 (40%); -0.0108: 632 (60%); 0.2006: 842 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -5.3502, -2.9105, -1.7397, -0.9422 | -5.3502: 842 (80%); -2.9105: 632 (60%); -1.7397: 421 (40%); -0.9422: 211 (20%) | -5.3502: 211 (20%); -2.9105: 421 (40%); -1.7397: 632 (60%); -0.9422: 842 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -4.985, -2.8036, -1.6153, -0.8156 | -4.985: 842 (80%); -2.8036: 632 (60%); -1.6153: 421 (40%); -0.8156: 211 (20%) | -4.985: 211 (20%); -2.8036: 421 (40%); -1.6153: 632 (60%); -0.8156: 842 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 26.546, 33.414, 40.062, 47.884 | 26.546: 842 (80%); 33.414: 632 (60%); 40.062: 421 (40%); 47.884: 211 (20%) | 26.546: 211 (20%); 33.414: 421 (40%); 40.062: 632 (60%); 47.884: 842 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0063, 0.019, 0.0368, 0.0736 | 0.0063: 834 (79%); 0.019: 626 (59%); 0.0368: 418 (40%); 0.0736: 209 (20%) | 0.0063: 211 (20%); 0.019: 419 (40%); 0.0368: 627 (60%); 0.0736: 836 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 9 | 0: 1053 (100%); 1: 810 (77%); 3: 487 (46%); 9: 215 (20%) | 0: 243 (23%); 1: 432 (41%); 3: 640 (61%); 9: 871 (83%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.219 | 0: 1053 (100%); 0.219: 211 (20%) | 0: 661 (63%); 0.219: 842 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.5714 | 0: 1053 (100%); 0.3333: 467 (44%); 0.5714: 213 (20%) | 0: 446 (42%); 0.3333: 640 (61%); 0.5714: 847 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 6 | 0: 1053 (100%); 1: 748 (71%); 2: 533 (51%); 6: 230 (22%) | 0: 305 (29%); 1: 520 (49%); 2: 649 (62%); 6: 862 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 9 | 0: 1053 (100%); 1: 810 (77%); 3: 487 (46%); 9: 215 (20%) | 0: 243 (23%); 1: 432 (41%); 3: 640 (61%); 9: 871 (83%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1053 (100%); 1: 745 (71%); 3: 458 (43%); 7: 235 (22%) | 0: 308 (29%); 1: 484 (46%); 3: 690 (66%); 7: 854 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1574, 0.3005, 0.5 | 0: 931 (88%); 0.1574: 632 (60%); 0.3005: 421 (40%); 0.5: 229 (22%) | 0: 286 (27%); 0.1574: 421 (40%); 0.3005: 632 (60%); 0.5: 854 (81%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.0771, 0.4859 | 0: 931 (88%); 0.0771: 421 (40%); 0.4859: 211 (20%) | 0: 623 (59%); 0.0771: 632 (60%); 0.4859: 842 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2, 0.5 | 0: 916 (87%); 0.2: 424 (40%); 0.5: 232 (22%) | 0: 539 (51%); 0.2: 642 (61%); 0.5: 873 (83%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.5 | 0: 916 (87%); 0.2: 424 (40%); 0.5: 232 (22%) | 0: 539 (51%); 0.2: 642 (61%); 0.5: 873 (83%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1783, 0, 0.1733 | -0.1783: 842 (80%); 0: 739 (70%); 0.1733: 211 (20%) | -0.1783: 211 (20%); 0: 770 (73%); 0.1733: 842 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7571, -0.3034, 0, 0.9986 | -0.7571: 845 (80%); -0.3034: 632 (60%); 0: 552 (52%); 0.9986: 211 (20%) | -0.7571: 212 (20%); -0.3034: 421 (40%); 0: 648 (62%); 0.9986: 842 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 881 (84%); 4: 678 (64%); 7: 431 (41%); 11: 217 (21%) | 2: 278 (26%); 4: 448 (43%); 7: 679 (64%); 11: 862 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0883, -0.0542, -0.0333, -0.0117 | -0.0883: 842 (80%); -0.0542: 632 (60%); -0.0333: 421 (40%); -0.0117: 212 (20%) | -0.0883: 211 (20%); -0.0542: 421 (40%); -0.0333: 632 (60%); -0.0117: 841 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1339, -0.0952, -0.0696, -0.0405 | -0.1339: 843 (80%); -0.0952: 631 (60%); -0.0696: 421 (40%); -0.0405: 211 (20%) | -0.1339: 210 (20%); -0.0952: 422 (40%); -0.0696: 632 (60%); -0.0405: 842 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0408, -0.0196, -0.0052, 0.0107 | -0.0408: 843 (80%); -0.0196: 632 (60%); -0.0052: 421 (40%); 0.0107: 210 (20%) | -0.0408: 210 (20%); -0.0196: 421 (40%); -0.0052: 632 (60%); 0.0107: 843 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -5.3902, -3.4634, -2.3026, -1.2474 | -5.3902: 842 (80%); -3.4634: 632 (60%); -2.3026: 421 (40%); -1.2474: 211 (20%) | -5.3902: 211 (20%); -3.4634: 421 (40%); -2.3026: 632 (60%); -1.2474: 842 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -30.3732, -18.3272, -8.9148, 2.393 | -30.3732: 842 (80%); -18.3272: 632 (60%); -8.9148: 421 (40%); 2.393: 211 (20%) | -30.3732: 211 (20%); -18.3272: 421 (40%); -8.9148: 632 (60%); 2.393: 842 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0454, 0.0616, 0.0811, 0.1138 | 0.0454: 843 (80%); 0.0616: 633 (60%); 0.0811: 422 (40%); 0.1138: 211 (20%) | 0.0454: 212 (20%); 0.0616: 422 (40%); 0.0811: 632 (60%); 0.1138: 843 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.537, 0.7169, 0.8265, 0.9156 | 0.537: 843 (80%); 0.7169: 632 (60%); 0.8265: 421 (40%); 0.9156: 211 (20%) | 0.537: 212 (20%); 0.7169: 422 (40%); 0.8265: 632 (60%); 0.9156: 842 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -4.2742, -3.0313, -2.2113, -1.4636 | -4.2742: 842 (80%); -3.0313: 632 (60%); -2.2113: 421 (40%); -1.4636: 211 (20%) | -4.2742: 211 (20%); -3.0313: 421 (40%); -2.2113: 632 (60%); -1.4636: 842 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.0007, -0.6064, -0.3127, -0.0104 | -1.0007: 842 (80%); -0.6064: 632 (60%); -0.3127: 421 (40%); -0.0104: 211 (20%) | -1.0007: 211 (20%); -0.6064: 421 (40%); -0.3127: 632 (60%); -0.0104: 842 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -3.8075, -2.5583, -1.7454, -0.906 | -3.8075: 842 (80%); -2.5583: 632 (60%); -1.7454: 421 (40%); -0.906: 211 (20%) | -3.8075: 211 (20%); -2.5583: 421 (40%); -1.7454: 632 (60%); -0.906: 842 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -9.8766, -6.5258, -4.1264, -1.8628 | -9.8766: 842 (80%); -6.5258: 632 (60%); -4.1264: 421 (40%); -1.8628: 211 (20%) | -9.8766: 211 (20%); -6.5258: 421 (40%); -4.1264: 632 (60%); -1.8628: 842 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 56.948, 65.472, 72.26, 80.042 | 56.948: 842 (80%); 65.472: 632 (60%); 72.26: 422 (40%); 80.042: 211 (20%) | 56.948: 211 (20%); 65.472: 421 (40%); 72.26: 634 (60%); 80.042: 842 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 36.698, 39.49, 41.75, 43.706 | 36.698: 842 (80%); 39.49: 633 (60%); 41.75: 422 (40%); 43.706: 211 (20%) | 36.698: 211 (20%); 39.49: 422 (40%); 41.75: 633 (60%); 43.706: 842 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 33.3, 37.77, 40.83, 44.03 | 33.3: 843 (80%); 37.77: 633 (60%); 40.83: 422 (40%); 44.03: 213 (20%) | 33.3: 212 (20%); 37.77: 422 (40%); 40.83: 633 (60%); 44.03: 843 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 1053 (100%) | 0: 1051 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0323, 0.0515, 0.0609, 0.0865 | 0.0323: 844 (80%); 0.0515: 635 (60%); 0.0609: 423 (40%); 0.0865: 221 (21%) | 0.0323: 211 (20%); 0.0515: 422 (40%); 0.0609: 632 (60%); 0.0865: 844 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0824, -0.0586, -0.0446, -0.0329 | -0.0824: 848 (81%); -0.0586: 635 (60%); -0.0446: 422 (40%); -0.0329: 215 (20%) | -0.0824: 221 (21%); -0.0586: 425 (40%); -0.0446: 632 (60%); -0.0329: 843 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1053 (100%); 1: 227 (22%) | 0: 826 (78%); 1: 913 (87%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 23, 35, 53, 66 | 23: 853 (81%); 35: 640 (61%); 53: 423 (40%); 66: 230 (22%) | 23: 232 (22%); 35: 422 (40%); 53: 653 (62%); 66: 840 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.5% | 0.0126, 0.0199, 0.028, 0.0449 | 0.0126: 828 (79%); 0.0199: 622 (59%); 0.028: 415 (39%); 0.0449: 208 (20%) | 0.0126: 209 (20%); 0.0199: 415 (39%); 0.028: 622 (59%); 0.0449: 829 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.1104, 0.1505, 0.1957, 0.2688 | 0.1104: 842 (80%); 0.1505: 632 (60%); 0.1957: 422 (40%); 0.2688: 212 (20%) | 0.1104: 211 (20%); 0.1505: 423 (40%); 0.1957: 632 (60%); 0.2688: 843 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 11.66, 67.84, 107.7, 158.84 | 11.66: 842 (80%); 67.84: 632 (60%); 107.7: 422 (40%); 158.84: 211 (20%) | 11.66: 211 (20%); 67.84: 421 (40%); 107.7: 633 (60%); 158.84: 842 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 8.362, 11.55, 16.342, 26.396 | 8.362: 842 (80%); 11.55: 633 (60%); 16.342: 421 (40%); 26.396: 211 (20%) | 8.362: 211 (20%); 11.55: 422 (40%); 16.342: 632 (60%); 26.396: 842 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 10.734, 14.254, 19.268, 28.396 | 10.734: 842 (80%); 14.254: 632 (60%); 19.268: 421 (40%); 28.396: 211 (20%) | 10.734: 211 (20%); 14.254: 421 (40%); 19.268: 632 (60%); 28.396: 842 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 7.628, 16.632, 34.87, 65.312 | 7.628: 842 (80%); 16.632: 632 (60%); 34.87: 421 (40%); 65.312: 211 (20%) | 7.628: 211 (20%); 16.632: 421 (40%); 34.87: 632 (60%); 65.312: 842 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 13.784, 27.836, 52.17, 87.426 | 13.784: 842 (80%); 27.836: 632 (60%); 52.17: 421 (40%); 87.426: 211 (20%) | 13.784: 211 (20%); 27.836: 421 (40%); 52.17: 632 (60%); 87.426: 842 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 6, 10, 14, 18 | 6: 854 (81%); 10: 691 (66%); 14: 446 (42%); 18: 220 (21%) | 6: 237 (23%); 10: 442 (42%); 14: 667 (63%); 18: 863 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 12, 16 | 4: 878 (83%); 9: 633 (60%); 12: 442 (42%); 16: 232 (22%) | 4: 216 (21%); 9: 472 (45%); 12: 681 (65%); 16: 854 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 37.056, 41.276, 44.72, 50.036 | 37.056: 842 (80%); 41.276: 632 (60%); 44.72: 421 (40%); 50.036: 211 (20%) | 37.056: 211 (20%); 41.276: 421 (40%); 44.72: 632 (60%); 50.036: 842 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1905, 0.4881, 0.7619, 0.873 | 0.1905: 843 (80%); 0.4881: 643 (61%); 0.7619: 422 (40%); 0.873: 214 (20%) | 0.1905: 212 (20%); 0.4881: 426 (40%); 0.7619: 635 (60%); 0.873: 886 (84%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.78, 18, 21.424, 27.732 | 15.78: 844 (80%); 18: 638 (61%); 21.424: 421 (40%); 27.732: 211 (20%) | 15.78: 212 (20%); 18: 422 (40%); 21.424: 632 (60%); 27.732: 842 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.78, 18, 21.424, 27.732 | 15.78: 844 (80%); 18: 638 (61%); 21.424: 421 (40%); 27.732: 211 (20%) | 15.78: 212 (20%); 18: 422 (40%); 21.424: 632 (60%); 27.732: 842 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8682, 0.9043, 0.9404, 0.9704 | 0.8682: 842 (80%); 0.9043: 632 (60%); 0.9404: 432 (41%); 0.9704: 212 (20%) | 0.8682: 211 (20%); 0.9043: 421 (40%); 0.9404: 637 (60%); 0.9704: 843 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.7, 0.83, 0.93, 1.09 | 0.7: 853 (81%); 0.83: 641 (61%); 0.93: 444 (42%); 1.09: 219 (21%) | 0.7: 214 (20%); 0.83: 438 (42%); 0.93: 634 (60%); 1.09: 846 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0239, 0.0527, 0.0901, 0.1326 | 0.0239: 844 (80%); 0.0527: 632 (60%); 0.0901: 422 (40%); 0.1326: 211 (20%) | 0.0239: 211 (20%); 0.0527: 422 (40%); 0.0901: 633 (60%); 0.1326: 842 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 43.5499, 73.9829, 113.2258, 194.2329 | 43.5499: 842 (80%); 73.9829: 632 (60%); 113.2258: 421 (40%); 194.2329: 211 (20%) | 43.5499: 211 (20%); 73.9829: 421 (40%); 113.2258: 632 (60%); 194.2329: 842 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 42.0739, 71.4328, 108.4501, 188.9275 | 42.0739: 842 (80%); 71.4328: 632 (60%); 108.4501: 421 (40%); 188.9275: 211 (20%) | 42.0739: 211 (20%); 71.4328: 421 (40%); 108.4501: 632 (60%); 188.9275: 842 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 40.1557, 67.885, 103.8235, 181.1992 | 40.1557: 842 (80%); 67.885: 632 (60%); 103.8235: 421 (40%); 181.1992: 211 (20%) | 40.1557: 211 (20%); 67.885: 421 (40%); 103.8235: 632 (60%); 181.1992: 842 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1053 (100%) | 0: 977 (93%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1053 (100%) | 0: 885 (84%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1234, -0.0874, -0.0589, -0.0346 | -0.1234: 843 (80%); -0.0874: 632 (60%); -0.0589: 421 (40%); -0.0346: 211 (20%) | -0.1234: 211 (20%); -0.0874: 422 (40%); -0.0589: 632 (60%); -0.0346: 842 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -81.164, -75.658, -68.366, -59.032 | -81.164: 842 (80%); -75.658: 632 (60%); -68.366: 421 (40%); -59.032: 211 (20%) | -81.164: 211 (20%); -75.658: 421 (40%); -68.366: 632 (60%); -59.032: 842 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.5827, 0.8493, 1.0454, 1.3341 | 0.5827: 834 (79%); 0.8493: 626 (59%); 1.0454: 418 (40%); 1.3341: 209 (20%) | 0.5827: 209 (20%); 0.8493: 417 (40%); 1.0454: 626 (59%); 1.3341: 834 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 875 (83%); 5: 694 (66%); 7: 484 (46%); 9: 257 (24%) | 3: 253 (24%); 5: 451 (43%); 7: 666 (63%); 9: 908 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 98.8% | 0.1987, 0.2414, 0.2914, 0.365 | 0.1987: 832 (79%); 0.2414: 624 (59%); 0.2914: 416 (40%); 0.365: 209 (20%) | 0.1987: 209 (20%); 0.2414: 416 (40%); 0.2914: 624 (59%); 0.365: 832 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 98.8% | 4, 6, 8, 9 | 4: 852 (81%); 6: 661 (63%); 8: 451 (43%); 9: 320 (30%) | 4: 290 (28%); 6: 475 (45%); 8: 720 (68%); 9: 884 (84%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0201, 0.0272, 0.0355, 0.0491 | 0.0201: 835 (79%); 0.0272: 627 (60%); 0.0355: 420 (40%); 0.0491: 210 (20%) | 0.0201: 211 (20%); 0.0272: 418 (40%); 0.0355: 627 (60%); 0.0491: 836 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 2, 4, 6, 8 | 2: 908 (86%); 4: 699 (66%); 6: 505 (48%); 8: 289 (27%) | 2: 239 (23%); 4: 440 (42%); 6: 650 (62%); 8: 863 (82%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.1% | -0.2582, -0.121, -0.0098, 0.1151 | -0.2582: 835 (79%); -0.121: 626 (59%); -0.0098: 418 (40%); 0.1151: 209 (20%) | -0.2582: 210 (20%); -0.121: 418 (40%); -0.0098: 627 (60%); 0.1151: 835 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.1% | 1.6, 3, 5, 7 | 1.6: 835 (79%); 3: 681 (65%); 5: 445 (42%); 7: 260 (25%) | 1.6: 209 (20%); 3: 467 (44%); 5: 693 (66%); 7: 867 (82%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.6% |
| 8k_item_5_02_filed_within_7d | 4.1% |
| above_avwap_20high | 3.4% |
| above_avwap_20low | 91.6% |
| above_avwap_252low | 50.9% |
| above_avwap_50low | 75.1% |
| above_cam_r3 | 80.2% |
| above_cam_r4 | 58.3% |
| above_cpr | 90.8% |
| above_pivot | 92.1% |
| above_prev_high | 61.7% |
| above_prev_high_clearance_atr_05 | 16.0% |
| above_prev_low | 98.6% |
| above_r1 | 62.6% |
| above_r2 | 25.6% |
| above_vwap | 23.5% |
| above_wood_p | 92.1% |
| ad_rising | 43.1% |
| adx_cross_up | 1.4% |
| adx_cross_up_20 | 0.9% |
| adx_di_bear | 96.9% |
| adx_di_bull | 3.1% |
| adx_strong | 13.2% |
| adx_trending | 60.4% |
| ao_cross_dn | 1.2% |
| ao_positive | 3.0% |
| ao_twin_peaks_bull | 14.1% |
| at_key_fib | 4.8% |
| at_key_fib_wide | 13.9% |
| avwap_20high_loss_recent_3d | 2.9% |
| avwap_20high_reclaim_recent_3d | 3.1% |
| avwap_20low_loss_recent_3d | 3.8% |
| avwap_20low_reclaim_recent_3d | 51.2% |
| avwap_252low_loss_recent_3d | 3.1% |
| avwap_252low_reclaim_recent_3d | 24.8% |
| avwap_50low_loss_recent_3d | 2.1% |
| avwap_50low_reclaim_recent_3d | 40.6% |
| bb_10_20_above_mid | 25.5% |
| bb_10_20_expanding | 25.7% |
| bb_10_20_pctb_gt_75 | 6.0% |
| bb_10_20_pctb_gt_8 | 3.5% |
| bb_10_20_pctb_gt_85 | 1.8% |
| bb_10_20_pctb_gt_9 | 0.7% |
| bb_10_20_pctb_gt_95 | 0.5% |
| bb_10_20_pctb_lt_2 | 0.3% |
| bb_10_20_pctb_lt_25 | 4.7% |
| bb_10_20_reclaim_from_lower_recent_3d | 15.4% |
| bb_10_20_reclaim_from_upper_recent_3d | 0.3% |
| bb_10_20_squeeze | 33.8% |
| bb_10_20_touch_upper | 1.1% |
| bb_20_15_above_mid | 2.8% |
| bb_20_15_expanding | 50.1% |
| bb_20_15_pctb_gt_75 | 0.1% |
| bb_20_15_pctb_gt_8 | 0.1% |
| bb_20_15_pctb_lt_05 | 12.7% |
| bb_20_15_pctb_lt_1 | 25.1% |
| bb_20_15_pctb_lt_15 | 41.1% |
| bb_20_15_pctb_lt_2 | 54.9% |
| bb_20_15_pctb_lt_25 | 69.0% |
| bb_20_15_reclaim_from_lower_recent_3d | 57.6% |
| bb_20_15_reclaim_from_upper_recent_3d | 0.3% |
| bb_20_15_squeeze | 21.9% |
| bb_20_15_touch_lower | 12.3% |
| bb_20_20_above_mid | 2.8% |
| bb_20_20_expanding | 50.1% |
| bb_20_20_pctb_gt_75 | 0.1% |
| bb_20_20_pctb_lt_1 | 1.9% |
| bb_20_20_pctb_lt_15 | 9.7% |
| bb_20_20_pctb_lt_2 | 25.1% |
| bb_20_20_pctb_lt_25 | 45.2% |
| bb_20_20_reclaim_from_lower_recent_3d | 31.6% |
| bb_20_20_reclaim_from_upper_recent_3d | 0.2% |
| bb_20_20_squeeze | 10.4% |
| bearish_engulfing | 0.6% |
| bearish_pin_bar | 4.2% |
| below_avwap_20high | 96.6% |
| below_avwap_20low | 8.4% |
| below_avwap_252low | 49.1% |
| below_avwap_50low | 24.9% |
| below_cam_s3 | 2.8% |
| below_cam_s4 | 1.2% |
| below_cpr | 7.9% |
| below_ema_20 | 97.5% |
| below_ema_200 | 92.5% |
| below_ema_200_break_recent_5d | 7.6% |
| below_ema_20_break_recent_5d | 9.8% |
| below_ema_21 | 97.5% |
| below_ema_21_break_recent_5d | 9.2% |
| below_ema_50 | 97.3% |
| below_ema_50_break_recent_5d | 8.8% |
| below_ema_9 | 77.4% |
| below_ema_9_break_recent_5d | 17.1% |
| below_prev_high | 37.3% |
| below_prev_low | 1.3% |
| below_prev_low_clearance_atr_05 | 0.4% |
| below_s1 | 1.3% |
| below_s2 | 0.5% |
| below_sma_20 | 97.2% |
| below_sma_200 | 87.6% |
| below_sma_21 | 98.1% |
| below_sma_50 | 97.0% |
| below_sma_9 | 68.2% |
| below_vwap | 76.5% |
| bullish_engulfing | 13.9% |
| bullish_pin_bar | 4.1% |
| capitulation_recent_3d | 3.3% |
| ceo_buy | 1.6% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 17.8% |
| chandelier_long_flip_dn | 0.3% |
| chandelier_short_bearish | 99.1% |
| chandelier_short_flip_up | 0.3% |
| close_above_open | 97.5% |
| close_below_open | 2.5% |
| close_in_bottom_40pct_of_range | 9.2% |
| close_in_top_40pct_of_range | 73.8% |
| cluster_buy | 0.5% |
| cmf_cross_dn | 2.8% |
| cmf_cross_up | 6.6% |
| cmf_negative | 73.9% |
| cmf_positive | 25.9% |
| concentrated_sell | 4.9% |
| cpr_narrow | 96.4% |
| cpr_narrow_tight | 43.9% |
| cup_handle_detected | 11.2% |
| dc10_breakout_dn_1pct | 1.5% |
| dc10_breakout_up | 0.4% |
| dc10_breakout_up_1pct | 1.5% |
| dc10_new_high | 0.9% |
| dc20_resistance_break_retest_strong | 0.1% |
| dc20_support_break_retest_strong | 57.1% |
| defensive_leadership | 63.8% |
| director_only_buy | 4.1% |
| doji | 4.0% |
| double_bottom_detected | 11.8% |
| double_top_detected | 16.7% |
| dpi_elevated | 43.6% |
| drying_volume_on_down_turn | 1.7% |
| drying_volume_on_up_turn | 70.5% |
| ema_20_50_bearish | 91.4% |
| ema_20_50_bullish | 8.6% |
| ema_20_50_death_cross | 0.7% |
| ema_50_200_bearish | 74.3% |
| ema_50_200_bullish | 25.7% |
| ema_50_200_death_cross | 1.0% |
| ema_9_21_bearish | 97.5% |
| ema_9_21_bullish | 2.5% |
| ema_9_21_death_cross | 0.1% |
| evening_star | 2.5% |
| flag_bear_break_retest_short | 2.0% |
| flag_bear_broke | 2.2% |
| flag_bear_detected | 1.5% |
| flag_bull_detected | 0.3% |
| force_index_cross_dn | 0.4% |
| force_index_cross_up | 4.7% |
| force_index_positive | 8.1% |
| gap_dn_1_5pct | 3.7% |
| gap_dn_2pct | 1.6% |
| gap_up_1_5pct | 10.7% |
| gap_up_2pct | 5.5% |
| hammer | 4.3% |
| head_shoulders_bottom_detected | 1.8% |
| head_shoulders_top_detected | 7.2% |
| house_cluster_buy | 3.0% |
| house_cluster_sell | 3.7% |
| htf_aligned_bear | 81.9% |
| htf_aligned_bull | 2.3% |
| htf_disagreement | 1.8% |
| hull_bearish | 79.0% |
| hull_bullish | 21.0% |
| hull_flip_dn | 0.3% |
| hull_flip_up | 8.6% |
| ichi_above_cloud | 3.9% |
| ichi_above_cloud_break_recent_5d | 1.0% |
| ichi_below_cloud | 89.9% |
| ichi_below_cloud_break_recent_5d | 10.7% |
| ichi_cloud_thick | 85.2% |
| ichi_tk_bearish | 90.7% |
| ichi_tk_bullish | 5.9% |
| ichi_tk_cross_dn | 1.4% |
| ichi_tk_cross_up | 0.2% |
| ichi_weekly_above_cloud | 12.2% |
| ichi_weekly_below_cloud | 53.0% |
| ichi_weekly_in_cloud | 34.7% |
| in_reversal_window | 0.7% |
| inside_bar | 6.0% |
| inside_cpr | 1.7% |
| inside_kc | 90.6% |
| insider_cluster_active | 25.4% |
| institutional_buy | 89.7% |
| institutional_negative | 4.3% |
| institutional_persistence_growing | 45.6% |
| institutional_persistence_strong | 58.9% |
| institutional_strong_buy | 78.3% |
| inverted_cup_handle_detected | 12.0% |
| is_friday | 16.6% |
| is_halloween_period | 41.9% |
| is_halloween_period_first_day | 0.5% |
| is_january | 4.3% |
| is_january_extended | 5.9% |
| is_monday | 21.4% |
| is_pre_holiday | 2.8% |
| is_summer_period | 58.1% |
| is_totm_window | 30.9% |
| is_totm_window_first_day | 8.3% |
| is_week_open | 23.6% |
| kc_touch_lower | 12.8% |
| large_dollar_buy | 1.3% |
| macd_12_26_9_bearish | 77.2% |
| macd_12_26_9_bullish | 22.8% |
| macd_12_26_9_crossover_dn | 0.1% |
| macd_12_26_9_crossover_up | 6.0% |
| macd_8_21_5_bearish | 62.6% |
| macd_8_21_5_bullish | 37.4% |
| macd_8_21_5_crossover_dn | 0.3% |
| macd_8_21_5_crossover_up | 11.4% |
| marubozu_bull | 1.9% |
| mfi_broad_overbought | 0.3% |
| mfi_broad_oversold | 29.2% |
| mfi_overbought | 0.1% |
| mfi_oversold | 7.3% |
| monthly_above_sma_12 | 13.4% |
| monthly_above_sma_6 | 8.1% |
| monthly_bias_bear | 84.3% |
| monthly_bias_bull | 5.9% |
| monthly_momentum_pos | 19.2% |
| morning_star | 97.5% |
| near_52w_high_95pct | 0.9% |
| near_52w_high_retest_long | 0.4% |
| near_52w_low | 2.5% |
| near_52w_low_105pct | 25.9% |
| near_avwap_20high_atr_05x | 23.8% |
| near_avwap_20high_atr_10x | 54.3% |
| near_avwap_20high_atr_15x | 77.5% |
| near_avwap_20high_atr_20x | 93.0% |
| near_avwap_20low_atr_05x | 59.1% |
| near_avwap_20low_atr_10x | 95.4% |
| near_avwap_20low_atr_15x | 99.7% |
| near_avwap_252low_atr_05x | 28.1% |
| near_avwap_252low_atr_10x | 55.5% |
| near_avwap_252low_atr_15x | 66.6% |
| near_avwap_252low_atr_20x | 76.4% |
| near_avwap_50low_atr_05x | 46.0% |
| near_avwap_50low_atr_10x | 82.6% |
| near_avwap_50low_atr_15x | 92.1% |
| near_avwap_50low_atr_20x | 96.7% |
| near_cam_r3 | 19.3% |
| near_cam_s3 | 3.3% |
| near_cam_s4 | 1.0% |
| near_fib_236 | 0.8% |
| near_fib_382 | 0.2% |
| near_fib_500 | 1.1% |
| near_fib_618 | 3.5% |
| near_fib_786 | 13.9% |
| near_pivot | 8.2% |
| near_prev_close | 8.5% |
| near_prev_high | 21.2% |
| near_prev_low | 1.6% |
| near_r1 | 22.0% |
| near_r1_wide | 78.1% |
| near_r2 | 15.2% |
| near_r2_wide | 70.2% |
| near_s1 | 1.4% |
| near_s1_wide | 19.8% |
| near_s2 | 0.3% |
| near_s2_wide | 5.8% |
| near_s3 | 0.3% |
| near_wood_r1 | 23.8% |
| near_wood_s1 | 1.8% |
| news_uses_polygon_score | 19.3% |
| obv_bearish | 79.3% |
| obv_bullish | 20.7% |
| obv_diverge_bull | 15.2% |
| obv_falling | 55.3% |
| obv_rising | 44.7% |
| outside_bar | 12.7% |
| pead_negative_surprise | 27.8% |
| pead_positive_surprise | 12.6% |
| pin_bar | 8.3% |
| po3_accumulation_active | 25.6% |
| po3_bearish | 0.7% |
| po3_bullish | 18.3% |
| po3_manipulation_sweep_down | 2.8% |
| po3_manipulation_sweep_up | 5.4% |
| po3_mmbm_setup | 2.4% |
| po3_mmsm_setup | 0.1% |
| po3_sweep_above_prior_high | 82.7% |
| po3_sweep_below_prior_low | 29.1% |
| ppo_bullish | 19.3% |
| ppo_crossover_dn | 0.3% |
| ppo_crossover_up | 6.0% |
| pre_fomc_d0 | 3.3% |
| pre_fomc_d1 | 3.1% |
| pre_fomc_window | 6.5% |
| price_above_dema | 53.0% |
| price_above_ema_20 | 2.5% |
| price_above_ema_200 | 7.5% |
| price_above_ema_200_break_recent_5d | 1.8% |
| price_above_ema_20_break_recent_5d | 0.5% |
| price_above_ema_21 | 2.5% |
| price_above_ema_21_break_recent_5d | 0.3% |
| price_above_ema_50 | 2.7% |
| price_above_ema_50_break_recent_5d | 0.3% |
| price_above_ema_9 | 22.6% |
| price_above_ema_9_break_recent_5d | 22.3% |
| price_above_hull | 79.5% |
| price_above_sma_200 | 12.4% |
| price_above_sma_21 | 1.9% |
| price_above_sma_50 | 3.0% |
| price_above_tema | 80.5% |
| price_below_dema | 47.0% |
| price_below_hull | 20.5% |
| price_below_tema | 19.5% |
| psar_bullish | 16.1% |
| psar_flip_dn | 0.5% |
| psar_flip_up | 6.3% |
| r1_break_retest_long | 22.0% |
| recent_capitulation_at_s3 | 0.3% |
| resistance_break_retest | 0.1% |
| risk_off_regime_bond_signal | 28.0% |
| risk_off_regime_bond_signal_strong | 8.9% |
| risk_off_regime_gold_signal | 40.6% |
| risk_on_regime_bond_signal | 35.0% |
| risk_on_regime_bond_signal_strong | 13.2% |
| roc_positive | 8.7% |
| roc_turning_dn | 1.3% |
| roc_turning_up | 4.7% |
| rsi_14_bullish | 2.5% |
| rsi_14_cross_up_extreme_os_recent_3d | 2.2% |
| rsi_14_cross_up_oversold_recent_3d | 24.3% |
| rsi_14_extreme_os | 0.8% |
| rsi_14_oversold | 6.5% |
| rsi_14_rising | 92.8% |
| rsi_21_bullish | 2.5% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.4% |
| rsi_21_cross_up_oversold_recent_3d | 8.0% |
| rsi_21_extreme_os | 0.5% |
| rsi_21_oversold | 2.8% |
| rsi_21_rising | 92.8% |
| rsi_2_bullish | 87.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 4.5% |
| rsi_2_cross_dn_overbought_recent_3d | 5.4% |
| rsi_2_cross_up_extreme_os_recent_3d | 75.1% |
| rsi_2_cross_up_oversold_recent_3d | 84.0% |
| rsi_2_extreme_ob | 20.1% |
| rsi_2_extreme_os | 0.9% |
| rsi_2_overbought | 47.0% |
| rsi_2_oversold | 2.1% |
| rsi_2_rising | 92.8% |
| rsi_9_bullish | 2.6% |
| rsi_9_cross_dn_overbought_recent_3d | 0.1% |
| rsi_9_cross_up_extreme_os_recent_3d | 12.7% |
| rsi_9_cross_up_oversold_recent_3d | 48.4% |
| rsi_9_extreme_os | 1.1% |
| rsi_9_oversold | 9.1% |
| rsi_9_rising | 92.8% |
| s1_break_retest_short | 82.8% |
| sc_13d_filed_within_30d | 1.0% |
| sc_13g_filed_within_30d | 2.5% |
| sector_outperforming_spy | 19.0% |
| sector_underperforming_spy | 81.0% |
| shooting_star | 4.5% |
| sma_20_50_bullish | 17.3% |
| sma_20_50_golden_cross | 0.4% |
| sma_50_200_bullish | 32.8% |
| sma_50_200_golden_cross | 0.1% |
| sma_9_21_bullish | 4.7% |
| sma_9_21_golden_cross | 0.2% |
| smc_bos_bearish | 31.8% |
| smc_bos_bullish | 4.3% |
| smc_bos_retest_long | 3.4% |
| smc_bos_retest_short | 4.3% |
| smc_breaker_block_bearish | 28.9% |
| smc_breaker_block_bullish | 11.2% |
| smc_choch_bearish | 7.7% |
| smc_choch_bullish | 1.8% |
| smc_equal_highs_swept | 1.8% |
| smc_equal_lows_swept | 8.5% |
| smc_fvg_bearish_active | 57.5% |
| smc_fvg_bullish_active | 8.3% |
| smc_fvg_retest_long_zone | 0.4% |
| smc_fvg_retest_short_zone | 25.2% |
| smc_in_discount_zone | 97.6% |
| smc_in_premium_zone | 8.5% |
| smc_inverse_fvg_bearish | 99.1% |
| smc_inverse_fvg_bullish | 38.0% |
| smc_liquidity_swept_dn | 2.3% |
| smc_liquidity_swept_up | 1.5% |
| smc_mitigation_block_long | 2.3% |
| smc_mitigation_block_short | 0.2% |
| smc_ob_bearish_active | 61.0% |
| smc_ob_bullish_active | 13.4% |
| smc_ote_long_zone | 9.7% |
| smc_ote_short_zone | 0.9% |
| squeeze_fire_dn | 0.6% |
| squeeze_in | 14.1% |
| stoch_bearish_cross | 2.5% |
| stoch_broad_overbought | 0.3% |
| stoch_broad_oversold | 75.0% |
| stoch_bullish_cross | 36.0% |
| stoch_overbought | 0.2% |
| stoch_oversold | 61.5% |
| stochrsi_cross_dn | 6.8% |
| stochrsi_cross_up | 60.3% |
| stochrsi_overbought | 23.3% |
| stochrsi_oversold | 28.5% |
| supertrend_bearish | 2.4% |
| supertrend_bullish | 97.6% |
| supertrend_flip_recent_long_5d | 4.8% |
| supertrend_flip_recent_short_5d | 2.7% |
| supertrend_flip_up | 1.4% |
| support_break_retest | 67.7% |
| tema_above_dema | 13.6% |
| tema_cross_dn | 0.6% |
| tema_cross_up | 3.6% |
| triangle_apex_break_retest_long | 0.4% |
| triangle_ascending_detected | 2.5% |
| triangle_descending_detected | 11.5% |
| uo_oversold | 2.1% |
| usd_strengthening | 35.3% |
| usd_weakening | 9.8% |
| vix_band_high | 48.5% |
| vix_band_low | 27.9% |
| vix_band_mid | 23.6% |
| vix_term_backwardation | 6.4% |
| vix_term_contango | 93.6% |
| vol_above_avg | 27.8% |
| vol_below_avg | 72.2% |
| vol_spike_12x | 13.3% |
| vol_spike_15x | 5.0% |
| vol_spike_17x | 3.2% |
| vol_spike_2x | 1.8% |
| vol_spike_2x_on_down_day_recent_3d | 5.6% |
| vol_spike_2x_on_up_day_recent_3d | 1.8% |
| vol_spike_3x | 0.9% |
| vp_above_value_area | 0.7% |
| vp_below_value_area | 53.6% |
| vp_close_above_poc | 13.9% |
| vp_close_below_poc | 86.1% |
| vp_in_value_area | 45.8% |
| week_open_gap_down_15pct | 0.7% |
| week_open_gap_up_15pct | 3.2% |
| weekly_above_ema_10 | 2.7% |
| weekly_above_ema_20 | 4.8% |
| weekly_bias_bear | 95.1% |
| weekly_bias_bull | 2.6% |
| weekly_momentum_pos | 4.1% |
| williams_r_overbought | 0.4% |
| williams_r_oversold | 24.8% |
| williams_r_rising | 93.8% |
| within_pead_window | 43.5% |
| within_post_deletion_window | 9.2% |
| within_pre_rebalance_window | 1.4% |
| xs_avoid_high_ivol | 69.2% |
| xs_avoid_high_max | 82.7% |
| xs_high_beta_decile | 24.6% |
| xs_low_beta_bottom_quintile | 24.6% |
| xs_low_beta_decile | 16.1% |
| xs_low_beta_decile_entry_recent_5d | 0.5% |
| xs_low_beta_top_quintile | 16.1% |
| xs_momentum_bottom_decile | 20.0% |
| xs_momentum_bottom_quintile | 34.8% |
| xs_momentum_top_decile | 5.6% |
| xs_momentum_top_quintile | 9.9% |
| xs_quality_bottom_quintile | 23.2% |
| xs_quality_top_quintile | 19.5% |
| xs_quality_top_tercile | 37.3% |
| year_high_break_retest_long | 0.1% |
| year_low_break_retest_short | 12.9% |
| yoy_surprise_high | 37.1% |
| yoy_surprise_negative | 50.9% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.0% |
| committed_growth_holders | 91.0% |
| corp_donations_1y | 6.6% |
| corp_donations_count_1y | 6.6% |
| corp_donations_unique_pacs | 6.6% |
| cot_rut_commercials_pctile_3y | 46.2% |
| cot_rut_mmoney_pctile_3y | 46.2% |
| cup_handle_depth_pct | 20.5% |
| days_since_deletion | 8.3% |
| days_since_inclusion | 13.2% |
| days_to_next_holiday | 59.6% |
| days_to_rebalance | 13.5% |
| dpi_30d_avg | 95.8% |
| dpi_recent | 95.8% |
| earnings_announcement_return | 91.8% |
| earnings_eps_yoy_growth | 93.6% |
| flag_bear_pole_move_pct | 1.5% |
| flag_bull_pole_move_pct | 0.3% |
| gov_contracts_4q_sum | 39.1% |
| gov_contracts_last_qtr_amount | 39.1% |
| gov_contracts_qoq_growth | 39.1% |
| head_shoulders_magnitude_pct | 8.7% |
| insider_director_buyers_30d | 6.7% |
| insider_officer_buyers_30d | 6.7% |
| insider_total_shares_bought_30d | 6.7% |
| insider_unique_buyers_30d | 6.7% |
| inverted_cup_handle_height_pct | 19.7% |
| lobbying_amount_1y | 69.7% |
| lobbying_amount_q | 69.7% |
| lobbying_amount_yoy | 69.7% |
| monthly_momentum_6m | 97.1% |
| otc_short_ratio_recent | 95.8% |
| otc_volume_recent | 95.8% |
| pair_half_life | 91.9% |
| pair_max_abs_zscore | 91.9% |
| pair_zscore_signed | 91.9% |
| pct_from_avwap_20low | 92.4% |
| pct_from_avwap_252low | 96.5% |
| pct_from_avwap_50low | 94.0% |
| persistent_holders_4q | 91.0% |
| persistent_holders_8q | 91.0% |
| sc_13g_latest_percent_owned | 1.3% |
| search_volume_index_recent | 77.6% |
| search_volume_observations | 77.6% |
| search_volume_zscore_30d | 77.6% |
| sector_etf_return_20d | 2.0% |
| spy_return_20d | 2.0% |
| total_active_holders | 91.0% |
| triangle_breakdown_pct | 11.5% |
| triangle_breakout_pct | 2.5% |
| xs_quality_decile | 61.9% |
| xs_quality_gross_profitability | 61.9% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.999), `avwap_252low` (0.997), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.997), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.997), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (0.999), `dc20_upper` (0.997), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.997), `double_top_neckline` (0.996), `double_top_peak` (0.996), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.993), `fib_382` (0.995), `fib_500` (0.996), `fib_618` (0.997), `fib_786` (0.998), `fib_ext_127` (0.986), `fib_ext_162` (0.982), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.999), `ichi_kijun` (0.999), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.989), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.982), `monthly_sma_6` (0.994), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.998), `s3` (0.998), `supertrend_value` (0.996), `swing_high` (0.99), `swing_low` (0.998), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.994), `vp_value_area_low` (0.996), `vwap_upper_1` (0.952), `vwap_upper_2` (0.954), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.995), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.998), `year_high` (0.956), `year_low` (0.987)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
