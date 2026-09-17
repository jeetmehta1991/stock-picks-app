# Table A - stochrsi_overbought_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:05:47 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** momentum | **status:** NOT-STARTED | **R5 fires:** 4287 | **surviving fires (T1):** 4287 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  stochrsi_cross_dn  <- backtest/signals/screener.py +1
       DEFN: k crosses below d while k > 20 (technical.py:600)
       knobs P1.1-P1.1 (band rows in Table A)
P2  stochrsi_overbought  <- backtest/signals/screener.py +1
       DEFN: stochastic-RSI overbought = k > 80 (technical.py:598)
       knobs P2.1-P2.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  rsi_14 > 45   [EXISTING-THRESHOLD]
P4  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_stochrsi_overbought_short (docstring and return dropped):

```python
fires = s.get('stochrsi_overbought') and s.get('stochrsi_cross_dn') and (s.get('rsi_14', 50) > 45) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | stochrsi_cross_dn - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | k crosses below d while k > 20 (technical.py:600) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | cross guard band (k > 20 on cross_dn) - backtest/signals/technical.py:600 | BRACKET production guard | 20 | 20, 30 | TIGHTER (k > 30) on persisted k/d | none needed - k and d both persisted | T3 review before any grid |
| P2 | PRODUCER | stochrsi_overbought - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | stochastic-RSI overbought = k > 80 (technical.py:598) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | overbought threshold on k - backtest/signals/technical.py:598 | BRACKET canon 80; stochrsi_k IS persisted | 80 | 75, 80, 85, 90 | TIGHTER (k > 85, k > 90) - subset on persisted stochrsi_k | LOOSER (k > 75); DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2.2 | BAND | period (rsi+stoch length) - technical.py:574 | BRACKET production | 14 | 10, 14, 21 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | rsi_14 `> 45` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 45` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `> 45` | 100.0% | TIGHTER = RAISE the floor: 51.72 -> 3430 (80%); 56.94 -> 2573 (60%); 62.132 -> 1715 (40%); 68.178 -> 858 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.97, 20.514, 24.18, 29.3 | 16.97: 3431 (80%); 20.514: 2572 (60%); 24.18: 1717 (40%); 29.3: 859 (20%) | 16.97: 859 (20%); 20.514: 1715 (40%); 24.18: 2573 (60%); 29.3: 3432 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 13.05, 16.344, 19.27, 22.59 | 13.05: 3430 (80%); 16.344: 2572 (60%); 19.27: 1717 (40%); 22.59: 859 (20%) | 13.05: 860 (20%); 16.344: 1715 (40%); 19.27: 2576 (60%); 22.59: 3430 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 23.29, 27.004, 30.75, 35.42 | 23.29: 3430 (80%); 27.004: 2572 (60%); 30.75: 1716 (40%); 35.42: 861 (20%) | 23.29: 859 (20%); 27.004: 1715 (40%); 30.75: 2574 (60%); 35.42: 3430 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -0.6297, 1.1346, 3.4179, 8.5259 | -0.6297: 3429 (80%); 1.1346: 2572 (60%); 3.4179: 1715 (40%); 8.5259: 858 (20%) | -0.6297: 858 (20%); 1.1346: 1715 (40%); 3.4179: 2572 (60%); 8.5259: 3429 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2314, 2.0943, 3.5164, 5.9455 | 1.2314: 3429 (80%); 2.0943: 2572 (60%); 3.5164: 1715 (40%); 5.9455: 858 (20%) | 1.2314: 858 (20%); 2.0943: 1715 (40%); 3.5164: 2572 (60%); 5.9455: 3429 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2314, 2.0943, 3.5164, 5.9455 | 1.2314: 3429 (80%); 2.0943: 2572 (60%); 3.5164: 1715 (40%); 5.9455: 858 (20%) | 1.2314: 858 (20%); 2.0943: 1715 (40%); 3.5164: 2572 (60%); 5.9455: 3429 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.89, 2.311, 2.7376, 3.4416 | 1.89: 3430 (80%); 2.311: 2573 (60%); 2.7376: 1715 (40%); 3.4416: 858 (20%) | 1.89: 859 (20%); 2.311: 1717 (40%); 2.7376: 2572 (60%); 3.4416: 3429 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0608, 0.0879, 0.1206, 0.1709 | 0.0608: 3431 (80%); 0.0879: 2575 (60%); 0.1206: 1716 (40%); 0.1709: 858 (20%) | 0.0608: 862 (20%); 0.0879: 1717 (40%); 0.1206: 2575 (60%); 0.1709: 3430 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.6443, 0.7335, 0.7902, 0.8412 | 0.6443: 3430 (80%); 0.7335: 2574 (60%); 0.7902: 1718 (40%); 0.8412: 861 (20%) | 0.6443: 861 (20%); 0.7335: 1718 (40%); 0.7902: 2574 (60%); 0.8412: 3430 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0626, 0.0869, 0.1136, 0.1543 | 0.0626: 3432 (80%); 0.0869: 2576 (60%); 0.1136: 1717 (40%); 0.1543: 859 (20%) | 0.0626: 860 (20%); 0.0869: 1717 (40%); 0.1136: 2575 (60%); 0.1543: 3430 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.7572, 0.9035, 1.0036, 1.098 | 0.7572: 3430 (80%); 0.9035: 2572 (60%); 1.0036: 1715 (40%); 1.098: 859 (20%) | 0.7572: 858 (20%); 0.9035: 1715 (40%); 1.0036: 2572 (60%); 1.098: 3430 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0834, 0.1159, 0.1515, 0.2058 | 0.0834: 3432 (80%); 0.1159: 2575 (60%); 0.1515: 1715 (40%); 0.2058: 858 (20%) | 0.0834: 859 (20%); 0.1159: 1717 (40%); 0.1515: 2575 (60%); 0.2058: 3430 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.6929, 0.8026, 0.8778, 0.9485 | 0.6929: 3430 (80%); 0.8026: 2572 (60%); 0.8778: 1715 (40%); 0.9485: 860 (20%) | 0.6929: 858 (20%); 0.8026: 1715 (40%); 0.8778: 2574 (60%); 0.9485: 3430 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0503, -0.0269, -0.0089, 0.0124 | -0.0503: 3430 (80%); -0.0269: 2578 (60%); -0.0089: 1724 (40%); 0.0124: 868 (20%) | -0.0503: 861 (20%); -0.0269: 1717 (40%); -0.0089: 2573 (60%); 0.0124: 3432 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1379, 0.1654, 0.1992, 0.2607 | 0.1379: 3427 (80%); 0.1654: 2561 (60%); 0.1992: 1708 (40%); 0.2607: 844 (20%) | 0.1379: 860 (20%); 0.1654: 1726 (40%); 0.1992: 2579 (60%); 0.2607: 3443 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 4287 (100%) | 0: 4070 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.046, 0.0377, 0.1019, 0.1836 | -0.046: 3431 (80%); 0.0377: 2574 (60%); 0.1019: 1718 (40%); 0.1836: 859 (20%) | -0.046: 858 (20%); 0.0377: 1715 (40%); 0.1019: 2573 (60%); 0.1836: 3430 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 4287 (100%); 1: 1700 (40%) | 0: 2587 (60%); 1: 3458 (81%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2461, -0.2011, -0.1572, -0.1285 | -0.2461: 3464 (81%); -0.2011: 2580 (60%); -0.1572: 1718 (40%); -0.1285: 900 (21%) | -0.2461: 869 (20%); -0.2011: 1726 (40%); -0.1572: 2585 (60%); -0.1285: 3438 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.359, 0.5833, 0.6667, 0.7885 | 0.359: 3446 (80%); 0.5833: 2617 (61%); 0.6667: 1764 (41%); 0.7885: 861 (20%) | 0.359: 879 (21%); 0.5833: 1758 (41%); 0.6667: 2645 (62%); 0.7885: 3450 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.4231, 0.6538, 0.8846 | 0.2628: 3474 (81%); 0.4231: 2578 (60%); 0.6538: 1760 (41%); 0.8846: 862 (20%) | 0.2628: 946 (22%); 0.4231: 1752 (41%); 0.6538: 2580 (60%); 0.8846: 3526 (82%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1158, -0.0361, 0.0498, 0.2047 | -0.1158: 3436 (80%); -0.0361: 2582 (60%); 0.0498: 1735 (40%); 0.2047: 878 (20%) | -0.1158: 878 (20%); -0.0361: 1719 (40%); 0.0498: 2602 (61%); 0.2047: 3454 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2436, 0.3974, 0.5897, 0.7949 | 0.2436: 3501 (82%); 0.3974: 2602 (61%); 0.5897: 1777 (41%); 0.7949: 864 (20%) | 0.2436: 869 (20%); 0.3974: 1749 (41%); 0.5897: 2579 (60%); 0.7949: 3446 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.2564, 0.4551, 0.6474 | 0.109: 3447 (80%); 0.2564: 2590 (60%); 0.4551: 1750 (41%); 0.6474: 915 (21%) | 0.109: 881 (21%); 0.2564: 1757 (41%); 0.4551: 2589 (60%); 0.6474: 3436 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4904, -0.3438, -0.1616, 0.0939 | -0.4904: 3433 (80%); -0.3438: 2601 (61%); -0.1616: 1746 (41%); 0.0939: 862 (20%) | -0.4904: 874 (20%); -0.3438: 1732 (40%); -0.1616: 2581 (60%); 0.0939: 3439 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5192, 0.7436, 0.9487 | 0.3397: 3471 (81%); 0.5192: 2608 (61%); 0.7436: 1754 (41%); 0.9487: 931 (22%) | 0.3397: 871 (20%); 0.5192: 1800 (42%); 0.7436: 2577 (60%); 0.9487: 3449 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.3141, 0.5449, 0.7692 | 0.109: 3442 (80%); 0.3141: 2626 (61%); 0.5449: 1734 (40%); 0.7692: 893 (21%) | 0.109: 879 (21%); 0.3141: 1722 (40%); 0.5449: 2581 (60%); 0.7692: 3433 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0693, -0.06, -0.0399, 0 | -0.0693: 3468 (81%); -0.06: 2600 (61%); -0.0399: 1731 (40%); 0: 1230 (29%) | -0.0693: 865 (20%); -0.06: 1717 (40%); -0.0399: 2606 (61%); 0: 4145 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.641, 0.8846, 1 | 0.3526: 3434 (80%); 0.641: 2576 (60%); 0.8846: 1726 (40%); 1: 927 (22%) | 0.3526: 911 (21%); 0.641: 1729 (40%); 0.8846: 2630 (61%); 1: 4287 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.2628, 0.5833, 0.9038 | 0.1282: 3444 (80%); 0.2628: 2614 (61%); 0.5833: 1738 (41%); 0.9038: 886 (21%) | 0.1282: 926 (22%); 0.2628: 1720 (40%); 0.5833: 2604 (61%); 0.9038: 3471 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0192, 0.0324, 0.0829, 0.1591 | -0.0192: 3430 (80%); 0.0324: 2573 (60%); 0.0829: 1715 (40%); 0.1591: 873 (20%) | -0.0192: 875 (20%); 0.0324: 1718 (40%); 0.0829: 2572 (60%); 0.1591: 3441 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4167, 0.7788, 0.9186, 0.9744 | 0.4167: 3441 (80%); 0.7788: 2580 (60%); 0.9186: 1750 (41%); 0.9744: 911 (21%) | 0.4167: 874 (20%); 0.7788: 1748 (41%); 0.9186: 2601 (61%); 0.9744: 3520 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1026, 0.391, 0.6282, 0.8357 | 0.1026: 3445 (80%); 0.391: 2586 (60%); 0.6282: 1717 (40%); 0.8357: 870 (20%) | 0.1026: 863 (20%); 0.391: 1729 (40%); 0.6282: 2581 (60%); 0.8357: 3447 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0189, 0.0917, 0.1876 | -0.0812: 3763 (88%); -0.0189: 2574 (60%); 0.0917: 1722 (40%); 0.1876: 892 (21%) | -0.0812: 949 (22%); -0.0189: 1735 (40%); 0.0917: 2574 (60%); 0.1876: 3528 (82%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1761, -0.0268, 0.0321, 0.0772 | -0.1761: 3442 (80%); -0.0268: 2577 (60%); 0.0321: 1730 (40%); 0.0772: 870 (20%) | -0.1761: 862 (20%); -0.0268: 1730 (40%); 0.0321: 2573 (60%); 0.0772: 3434 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3269, 0.5449, 0.7179, 0.859 | 0.3269: 3439 (80%); 0.5449: 2592 (60%); 0.7179: 1736 (40%); 0.859: 888 (21%) | 0.3269: 877 (20%); 0.5449: 1744 (41%); 0.7179: 2642 (62%); 0.859: 3451 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.141, 0.3846, 0.6538, 0.8269 | 0.141: 3443 (80%); 0.3846: 2621 (61%); 0.6538: 1727 (40%); 0.8269: 909 (21%) | 0.141: 864 (20%); 0.3846: 1726 (40%); 0.6538: 2612 (61%); 0.8269: 3454 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.06, 0.1375, 0.2717, 0.5433 | 0.06: 3448 (80%); 0.1375: 2575 (60%); 0.2717: 1722 (40%); 0.5433: 859 (20%) | 0.06: 865 (20%); 0.1375: 1719 (40%); 0.2717: 2573 (60%); 0.5433: 3431 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.7% | 24, 57, 78, 125 | 24: 3400 (79%); 57: 2546 (59%); 78: 1727 (40%); 125: 847 (20%) | 24: 848 (20%); 57: 1701 (40%); 78: 2549 (59%); 125: 3397 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.5% | 1.7333, 2.2225, 2.7428, 3.5107 | 1.7333: 3411 (80%); 2.2225: 2558 (60%); 2.7428: 1707 (40%); 3.5107: 853 (20%) | 1.7333: 853 (20%); 2.2225: 1706 (40%); 2.7428: 2559 (60%); 3.5107: 3411 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 16, 23, 35 | 8: 3545 (83%); 16: 2594 (61%); 23: 1885 (44%); 35: 949 (22%) | 8: 878 (20%); 16: 1812 (42%); 23: 2587 (60%); 35: 3473 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 2, 4 | 0: 4287 (100%); 1: 3389 (79%); 2: 2514 (59%); 4: 882 (21%) | 0: 898 (21%); 1: 1773 (41%); 2: 2593 (60%); 4: 4287 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0159, -0.0064, 0.0054, 0.0207 | -0.0159: 3432 (80%); -0.0064: 2578 (60%); 0.0054: 1722 (40%); 0.0207: 860 (20%) | -0.0159: 875 (20%); -0.0064: 1719 (40%); 0.0054: 2576 (60%); 0.0207: 3466 (81%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5526, 25.9154, 26.4951, 27.2 | 24.5526: 3457 (81%); 25.9154: 2584 (60%); 26.4951: 1723 (40%); 27.2: 863 (20%) | 24.5526: 872 (20%); 25.9154: 1726 (40%); 26.4951: 2574 (60%); 27.2: 3430 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.5498, -0.189, 0.0806, 0.465 | -0.5498: 3429 (80%); -0.189: 2574 (60%); 0.0806: 1715 (40%); 0.465: 859 (20%) | -0.5498: 858 (20%); -0.189: 1721 (40%); 0.0806: 2572 (60%); 0.465: 3430 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.465, -0.0806, 0.189, 0.5498 | -0.465: 3430 (80%); -0.0806: 2572 (60%); 0.189: 1721 (40%); 0.5498: 858 (20%) | -0.465: 859 (20%); -0.0806: 1715 (40%); 0.189: 2574 (60%); 0.5498: 3429 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0454, -0.0123, 0.0149, 0.0405 | -0.0454: 3430 (80%); -0.0123: 2573 (60%); 0.0149: 1719 (40%); 0.0405: 858 (20%) | -0.0454: 865 (20%); -0.0123: 1716 (40%); 0.0149: 2577 (60%); 0.0405: 3442 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0686, 8.4607, 8.701, 9.0283 | 8.0686: 3430 (80%); 8.4607: 2570 (60%); 8.701: 1715 (40%); 9.0283: 847 (20%) | 8.0686: 857 (20%); 8.4607: 1717 (40%); 8.701: 2572 (60%); 9.0283: 3440 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 4252 (99%); 1: 1372 (32%) | 0: 2880 (67%); 1: 3814 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0 | 0: 3425 (80%) | 0: 3527 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.2% | 0, 1 | 0: 4252 (99%); 1: 1428 (33%) | 0: 2824 (66%); 1: 3778 (88%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 5, 70.6, 268 | 2: 3663 (85%); 5: 2793 (65%); 70.6: 1715 (40%); 268: 859 (20%) | 2: 891 (21%); 5: 1772 (41%); 70.6: 2572 (60%); 268: 3434 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 79, 138 | 1: 3472 (81%); 4: 2600 (61%); 79: 1718 (40%); 138: 859 (20%) | 1: 1174 (27%); 4: 1848 (43%); 79: 2581 (60%); 138: 3442 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | 0.2369, 0.5024, 0.9295, 1.7868 | 0.2369: 3430 (80%); 0.5024: 2572 (60%); 0.9295: 1715 (40%); 1.7868: 858 (20%) | 0.2369: 858 (20%); 0.5024: 1715 (40%); 0.9295: 2572 (60%); 1.7868: 3429 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -0.4026, 0.3288, 1.1536, 3.0856 | -0.4026: 3429 (80%); 0.3288: 2572 (60%); 1.1536: 1715 (40%); 3.0856: 858 (20%) | -0.4026: 858 (20%); 0.3288: 1715 (40%); 1.1536: 2572 (60%); 3.0856: 3429 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.2015, -0.1797, 0.471, 1.841 | -1.2015: 3429 (80%); -0.1797: 2572 (60%); 0.471: 1715 (40%); 1.841: 858 (20%) | -1.2015: 858 (20%); -0.1797: 1715 (40%); 0.471: 2572 (60%); 1.841: 3429 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | 0.1627, 0.3513, 0.67, 1.3279 | 0.1627: 3429 (80%); 0.3513: 2573 (60%); 0.67: 1715 (40%); 1.3279: 858 (20%) | 0.1627: 858 (20%); 0.3513: 1715 (40%); 0.67: 2572 (60%); 1.3279: 3429 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.0127, 0.776, 1.8314, 4.1636 | 0.0127: 3430 (80%); 0.776: 2572 (60%); 1.8314: 1715 (40%); 4.1636: 858 (20%) | 0.0127: 858 (20%); 0.776: 1715 (40%); 1.8314: 2572 (60%); 4.1636: 3429 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -0.3662, 0.3703, 1.2186, 3.2204 | -0.3662: 3430 (80%); 0.3703: 2572 (60%); 1.2186: 1715 (40%); 3.2204: 858 (20%) | -0.3662: 858 (20%); 0.3703: 1715 (40%); 1.2186: 2572 (60%); 3.2204: 3429 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 54.71, 61.944, 68.736, 76.18 | 54.71: 3431 (80%); 61.944: 2572 (60%); 68.736: 1715 (40%); 76.18: 859 (20%) | 54.71: 859 (20%); 61.944: 1715 (40%); 68.736: 2572 (60%); 76.18: 3430 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 98.6% | -0.092, 0.0142, 0.1005, 0.2171 | -0.092: 3382 (79%); 0.0142: 2538 (59%); 0.1005: 1691 (39%); 0.2171: 846 (20%) | -0.092: 846 (20%); 0.0142: 1691 (39%); 0.1005: 2536 (59%); 0.2171: 3381 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.5% | 0.0061, 0.0152, 0.0302, 0.0594 | 0.0061: 3403 (79%); 0.0152: 2554 (60%); 0.0302: 1708 (40%); 0.0594: 855 (20%) | 0.0061: 863 (20%); 0.0152: 1712 (40%); 0.0302: 2558 (60%); 0.0594: 3411 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 9 | 0: 4287 (100%); 2: 2673 (62%); 4: 1863 (43%); 9: 938 (22%) | 0: 990 (23%); 2: 2055 (48%); 4: 2665 (62%); 9: 3446 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1111 | 0: 4287 (100%); 0.1111: 870 (20%) | 0: 3043 (71%); 0.1111: 3462 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5, 0.6667 | 0: 4287 (100%); 0.25: 2576 (60%); 0.5: 1749 (41%); 0.6667: 1023 (24%) | 0: 1518 (35%); 0.25: 1808 (42%); 0.5: 2941 (69%); 0.6667: 3447 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 7 | 0: 4287 (100%); 1: 3042 (71%); 3: 1873 (44%); 7: 887 (21%) | 0: 1245 (29%); 1: 1937 (45%); 3: 2775 (65%); 7: 3532 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 4287 (100%); 2: 2673 (62%); 4: 1863 (43%); 9: 938 (22%) | 0: 990 (23%); 2: 2055 (48%); 4: 2665 (62%); 9: 3446 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 4287 (100%); 1: 3101 (72%); 3: 2014 (47%); 8: 899 (21%) | 0: 1186 (28%); 1: 1828 (43%); 3: 2603 (61%); 8: 3505 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0185, 0.2624, 0.4, 0.6 | 0.0185: 3429 (80%); 0.2624: 2572 (60%); 0.4: 1745 (41%); 0.6: 872 (20%) | 0.0185: 858 (20%); 0.2624: 1715 (40%); 0.4: 2590 (60%); 0.6: 3461 (81%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2779, 0.6316 | 0: 3996 (93%); 0.2779: 1715 (40%); 0.6316: 859 (20%) | 0: 2135 (50%); 0.2779: 2573 (60%); 0.6316: 3430 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3623, 0.6369 | 0: 4035 (94%); 0.3623: 1715 (40%); 0.6369: 858 (20%) | 0: 1718 (40%); 0.3623: 2572 (60%); 0.6369: 3429 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3623, 0.6369 | 0: 4035 (94%); 0.3623: 1715 (40%); 0.6369: 858 (20%) | 0: 1718 (40%); 0.3623: 2572 (60%); 0.6369: 3429 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1522, 0, 0.1847 | -0.1522: 3430 (80%); 0: 3110 (73%); 0.1847: 858 (20%) | -0.1522: 858 (20%); 0: 2975 (69%); 0.1847: 3430 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6928, -0.2079, 0.239, 1.5492 | -0.6928: 3434 (80%); -0.2079: 2572 (60%); 0.239: 1740 (41%); 1.5492: 862 (20%) | -0.6928: 868 (20%); -0.2079: 1715 (40%); 0.239: 2593 (60%); 1.5492: 3430 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 3609 (84%); 4: 2727 (64%); 7: 1834 (43%); 11: 919 (21%) | 2: 1135 (26%); 4: 1867 (44%); 7: 2722 (63%); 11: 3508 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0237, 0.0452, 0.0691, 0.105 | 0.0237: 3430 (80%); 0.0452: 2572 (60%); 0.0691: 1715 (40%); 0.105: 859 (20%) | 0.0237: 857 (20%); 0.0452: 1715 (40%); 0.0691: 2572 (60%); 0.105: 3429 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0094, 0.0249, 0.0607, 0.1098 | -0.0094: 3431 (80%); 0.0249: 2572 (60%); 0.0607: 1715 (40%); 0.1098: 858 (20%) | -0.0094: 856 (20%); 0.0249: 1715 (40%); 0.0607: 2572 (60%); 0.1098: 3429 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | 0.0088, 0.0253, 0.0427, 0.0691 | 0.0088: 3428 (80%); 0.0253: 2570 (60%); 0.0427: 1715 (40%); 0.0691: 857 (20%) | 0.0088: 859 (20%); 0.0253: 1717 (40%); 0.0427: 2572 (60%); 0.0691: 3430 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 1.895, 3.265, 4.729, 6.89 | 1.895: 3429 (80%); 3.265: 2572 (60%); 4.729: 1715 (40%); 6.89: 858 (20%) | 1.895: 858 (20%); 3.265: 1715 (40%); 4.729: 2572 (60%); 6.89: 3429 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 98.6% | 2.4704, 6.3078, 10.935, 18.5662 | 2.4704: 3383 (79%); 6.3078: 2537 (59%); 10.935: 1692 (39%); 18.5662: 846 (20%) | 2.4704: 846 (20%); 6.3078: 1692 (39%); 10.935: 2537 (59%); 18.5662: 3383 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 2.1334, 3.9324, 6.08, 9.2436 | 2.1334: 3429 (80%); 3.9324: 2572 (60%); 6.08: 1716 (40%); 9.2436: 858 (20%) | 2.1334: 858 (20%); 3.9324: 1715 (40%); 6.08: 2573 (60%); 9.2436: 3429 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -10.5826, 1.8226, 14.6408, 35.37 | -10.5826: 3429 (80%); 1.8226: 2572 (60%); 14.6408: 1715 (40%); 35.37: 858 (20%) | -10.5826: 858 (20%); 1.8226: 1715 (40%); 14.6408: 2572 (60%); 35.37: 3429 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0431, 0.059, 0.0776, 0.1087 | 0.0431: 3430 (80%); 0.059: 2574 (60%); 0.0776: 1718 (40%); 0.1087: 859 (20%) | 0.0431: 863 (20%); 0.059: 1721 (40%); 0.0776: 2573 (60%); 0.1087: 3431 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1429, 0.2667, 0.4144, 0.5953 | 0.1429: 3431 (80%); 0.2667: 2573 (60%); 0.4144: 1715 (40%); 0.5953: 858 (20%) | 0.1429: 864 (20%); 0.2667: 1715 (40%); 0.4144: 2573 (60%); 0.5953: 3429 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -0.5412, 0.4552, 1.3297, 2.4246 | -0.5412: 3429 (80%); 0.4552: 2572 (60%); 1.3297: 1715 (40%); 2.4246: 858 (20%) | -0.5412: 858 (20%); 0.4552: 1715 (40%); 1.3297: 2572 (60%); 2.4246: 3429 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | 0.3302, 0.5939, 0.8805, 1.2915 | 0.3302: 3429 (80%); 0.5939: 2572 (60%); 0.8805: 1715 (40%); 1.2915: 859 (20%) | 0.3302: 858 (20%); 0.5939: 1715 (40%); 0.8805: 2573 (60%); 1.2915: 3431 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.2654, -0.2395, 0.6141, 1.5972 | -1.2654: 3429 (80%); -0.2395: 2572 (60%); 0.6141: 1715 (40%); 1.5972: 858 (20%) | -1.2654: 858 (20%); -0.2395: 1715 (40%); 0.6141: 2572 (60%); 1.5972: 3429 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 2.6232, 5.0444, 7.5858, 11.4658 | 2.6232: 3429 (80%); 5.0444: 2572 (60%); 7.5858: 1715 (40%); 11.4658: 858 (20%) | 2.6232: 858 (20%); 5.0444: 1715 (40%); 7.5858: 2572 (60%); 11.4658: 3429 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 40.804, 56.21, 69.556, 85.524 | 40.804: 3429 (80%); 56.21: 2573 (60%); 69.556: 1715 (40%); 85.524: 858 (20%) | 40.804: 858 (20%); 56.21: 1716 (40%); 69.556: 2572 (60%); 85.524: 3429 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 49.82, 54.234, 58.8, 64.086 | 49.82: 3430 (80%); 54.234: 2572 (60%); 58.8: 1716 (40%); 64.086: 858 (20%) | 49.82: 861 (20%); 54.234: 1715 (40%); 58.8: 2574 (60%); 64.086: 3429 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 54.864, 60.794, 66.776, 73.48 | 54.864: 3429 (80%); 60.794: 2572 (60%); 66.776: 1715 (40%); 73.48: 859 (20%) | 54.864: 858 (20%); 60.794: 1715 (40%); 66.776: 2572 (60%); 73.48: 3432 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 4279 (100%) | 0: 4285 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0298, 0.0434, 0.0568, 0.0792 | 0.0298: 3451 (80%); 0.0434: 2576 (60%); 0.0568: 1726 (40%); 0.0792: 861 (20%) | 0.0298: 860 (20%); 0.0434: 1719 (40%); 0.0568: 2581 (60%); 0.0792: 3433 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0833, -0.0591, -0.0447, -0.0344 | -0.0833: 3440 (80%); -0.0591: 2574 (60%); -0.0447: 1717 (40%); -0.0344: 862 (20%) | -0.0833: 860 (20%); -0.0591: 1716 (40%); -0.0447: 2578 (60%); -0.0344: 3431 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 4287 (100%); 2: 885 (21%) | 0: 2953 (69%); 2: 3635 (85%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.5% | 28, 44, 56, 69 | 28: 3459 (81%); 44: 2560 (60%); 56: 1862 (43%); 69: 892 (21%) | 28: 981 (23%); 44: 1730 (40%); 56: 2574 (60%); 69: 3450 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.4% | 0.011, 0.0158, 0.0224, 0.0352 | 0.011: 3369 (79%); 0.0158: 2541 (59%); 0.0224: 1686 (39%); 0.0352: 845 (20%) | 0.011: 851 (20%); 0.0158: 1679 (39%); 0.0224: 2534 (59%); 0.0352: 3375 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.4075, 0.6098, 0.8083, 0.9049 | 0.4075: 3428 (80%); 0.6098: 2572 (60%); 0.8083: 1716 (40%); 0.9049: 858 (20%) | 0.4075: 857 (20%); 0.6098: 1715 (40%); 0.8083: 2572 (60%); 0.9049: 3428 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 19.6, 45.36, 76.2, 126 | 19.6: 3429 (80%); 45.36: 2571 (60%); 76.2: 1717 (40%); 126: 858 (20%) | 19.6: 860 (20%); 45.36: 1714 (40%); 76.2: 2575 (60%); 126: 3429 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 1.0804, 2.5619, 4.9575, 9.619 | 1.0804: 3429 (80%); 2.5619: 2572 (60%); 4.9575: 1715 (40%); 9.619: 858 (20%) | 1.0804: 858 (20%); 2.5619: 1715 (40%); 4.9575: 2572 (60%); 9.619: 3429 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 72.59, 83.16, 88.866, 92.72 | 72.59: 3429 (80%); 83.16: 2573 (60%); 88.866: 1715 (40%); 92.72: 859 (20%) | 72.59: 858 (20%); 83.16: 1716 (40%); 88.866: 2572 (60%); 92.72: 3431 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 76.27, 84.72, 89.47, 93.058 | 76.27: 3430 (80%); 84.72: 2573 (60%); 89.47: 1716 (40%); 93.058: 858 (20%) | 76.27: 860 (20%); 84.72: 1717 (40%); 89.47: 2573 (60%); 93.058: 3429 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 92.4, 94.864, 96.606, 98.19 | 92.4: 3434 (80%); 94.864: 2572 (60%); 96.606: 1715 (40%); 98.19: 860 (20%) | 92.4: 859 (20%); 94.864: 1715 (40%); 96.606: 2572 (60%); 98.19: 3432 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 84.1, 87.87, 91.57, 95.3 | 84.1: 3431 (80%); 87.87: 2576 (60%); 91.57: 1716 (40%); 95.3: 859 (20%) | 84.1: 860 (20%); 87.87: 1716 (40%); 91.57: 2573 (60%); 95.3: 3430 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 12, 17 | 4: 3660 (85%); 9: 2595 (61%); 12: 1954 (46%); 17: 1017 (24%) | 4: 865 (20%); 9: 1907 (44%); 12: 2575 (60%); 17: 3454 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 18 | 5: 3443 (80%); 9: 2729 (64%); 13: 1899 (44%); 18: 859 (20%) | 5: 1053 (25%); 9: 1740 (41%); 13: 2645 (62%); 18: 3674 (86%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 52.862, 57.55, 61.3, 65.66 | 52.862: 3429 (80%); 57.55: 2573 (60%); 61.3: 1719 (40%); 65.66: 859 (20%) | 52.862: 858 (20%); 57.55: 1717 (40%); 61.3: 2573 (60%); 65.66: 3430 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1032, 0.3413, 0.5794, 0.7738 | 0.1032: 3468 (81%); 0.3413: 2581 (60%); 0.5794: 1730 (40%); 0.7738: 872 (20%) | 0.1032: 870 (20%); 0.3413: 1733 (40%); 0.5794: 2585 (60%); 0.7738: 3456 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.23, 16.35, 18.69, 23.03 | 14.23: 3432 (80%); 16.35: 2580 (60%); 18.69: 1719 (40%); 23.03: 892 (21%) | 14.23: 859 (20%); 16.35: 1739 (41%); 18.69: 2580 (60%); 23.03: 3433 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.23, 16.35, 18.69, 23.03 | 14.23: 3432 (80%); 16.35: 2580 (60%); 18.69: 1719 (40%); 23.03: 892 (21%) | 14.23: 859 (20%); 16.35: 1739 (41%); 18.69: 2580 (60%); 23.03: 3433 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8498, 0.8743, 0.9048, 0.9391 | 0.8498: 3429 (80%); 0.8743: 2581 (60%); 0.9048: 1721 (40%); 0.9391: 865 (20%) | 0.8498: 858 (20%); 0.8743: 1719 (40%); 0.9048: 2587 (60%); 0.9391: 3437 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.68, 0.81, 0.93, 1.12 | 0.68: 3457 (81%); 0.81: 2575 (60%); 0.93: 1733 (40%); 1.12: 859 (20%) | 0.68: 900 (21%); 0.81: 1794 (42%); 0.93: 2625 (61%); 1.12: 3459 (81%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.016, 0.0408, 0.0705, 0.117 | 0.016: 3431 (80%); 0.0408: 2574 (60%); 0.0705: 1715 (40%); 0.117: 859 (20%) | 0.016: 859 (20%); 0.0408: 1717 (40%); 0.0705: 2577 (60%); 0.117: 3430 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 46.5135, 79.0658, 123.9933, 208.3359 | 46.5135: 3429 (80%); 79.0658: 2572 (60%); 123.9933: 1715 (40%); 208.3359: 858 (20%) | 46.5135: 858 (20%); 79.0658: 1715 (40%); 123.9933: 2572 (60%); 208.3359: 3429 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 44.233, 75.7786, 119.1161, 201.177 | 44.233: 3429 (80%); 75.7786: 2572 (60%); 119.1161: 1715 (40%); 201.177: 858 (20%) | 44.233: 858 (20%); 75.7786: 1715 (40%); 119.1161: 2572 (60%); 201.177: 3429 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.9412, 72.715, 114.1723, 193.4097 | 41.9412: 3429 (80%); 72.715: 2572 (60%); 114.1723: 1715 (40%); 193.4097: 858 (20%) | 41.9412: 858 (20%); 72.715: 1715 (40%); 114.1723: 2572 (60%); 193.4097: 3429 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 48.5454, 81.5226, 128.6621, 216.2546 | 48.5454: 3429 (80%); 81.5226: 2572 (60%); 128.6621: 1715 (40%); 216.2546: 858 (20%) | 48.5454: 858 (20%); 81.5226: 1715 (40%); 128.6621: 2572 (60%); 216.2546: 3429 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 50.5948, 84.5462, 133.6258, 223.3106 | 50.5948: 3429 (80%); 84.5462: 2572 (60%); 133.6258: 1715 (40%); 223.3106: 858 (20%) | 50.5948: 858 (20%); 84.5462: 1715 (40%); 133.6258: 2572 (60%); 223.3106: 3429 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 4287 (100%) | 0: 3757 (88%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 4287 (100%) | 0: 3827 (89%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0143, 0.0466, 0.0778, 0.123 | 0.0143: 3429 (80%); 0.0466: 2571 (60%); 0.0778: 1716 (40%); 0.123: 858 (20%) | 0.0143: 859 (20%); 0.0466: 1716 (40%); 0.0778: 2575 (60%); 0.123: 3429 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -28.856, -20.476, -14.808, -9.97 | -28.856: 3429 (80%); -20.476: 2572 (60%); -14.808: 1715 (40%); -9.97: 861 (20%) | -28.856: 858 (20%); -20.476: 1715 (40%); -14.808: 2572 (60%); -9.97: 3430 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.3% | 0.5357, 0.8088, 1.0356, 1.3205 | 0.5357: 3405 (79%); 0.8088: 2554 (60%); 1.0356: 1703 (40%); 1.3205: 852 (20%) | 0.5357: 852 (20%); 0.8088: 1703 (40%); 1.0356: 2554 (60%); 1.3205: 3405 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 3517 (82%); 5: 2734 (64%); 7: 1927 (45%); 9: 1049 (24%) | 3: 1099 (26%); 5: 1933 (45%); 7: 2739 (64%); 9: 3679 (86%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.3% | 0.1823, 0.2221, 0.2723, 0.3499 | 0.1823: 3404 (79%); 0.2221: 2555 (60%); 0.2723: 1703 (40%); 0.3499: 853 (20%) | 0.1823: 853 (20%); 0.2221: 1703 (40%); 0.2723: 2553 (60%); 0.3499: 3405 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.3% | 3, 5, 7, 9 | 3: 3491 (81%); 5: 2749 (64%); 7: 1973 (46%); 9: 1107 (26%) | 3: 1141 (27%); 5: 1874 (44%); 7: 2702 (63%); 9: 3655 (85%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.3% | 0.0253, 0.0343, 0.0458, 0.0658 | 0.0253: 3409 (80%); 0.0343: 2560 (60%); 0.0458: 1706 (40%); 0.0658: 855 (20%) | 0.0253: 858 (20%); 0.0343: 1703 (40%); 0.0458: 2554 (60%); 0.0658: 3405 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 6, 8, 9 | 3: 3727 (87%); 6: 2673 (62%); 8: 1841 (43%); 9: 1338 (31%) | 3: 852 (20%); 6: 2014 (47%); 8: 2918 (68%); 9: 3494 (82%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.5% | -0.1604, -0.0213, 0.1019, 0.3 | -0.1604: 3411 (80%); -0.0213: 2559 (60%); 0.1019: 1706 (40%); 0.3: 853 (20%) | -0.1604: 853 (20%); -0.0213: 1707 (40%); 0.1019: 2560 (60%); 0.3: 3411 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.5% | 3, 5, 7, 9 | 3: 3466 (81%); 5: 2662 (62%); 7: 1828 (43%); 9: 973 (23%) | 3: 1170 (27%); 5: 2048 (48%); 7: 2857 (67%); 9: 3718 (87%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.6% |
| 8k_item_5_02_filed_within_7d | 3.2% |
| above_avwap_20high | 36.9% |
| above_avwap_20low | 98.4% |
| above_avwap_252low | 89.3% |
| above_avwap_50low | 96.7% |
| above_cam_r3 | 11.0% |
| above_cam_r4 | 4.3% |
| above_cpr | 47.0% |
| above_pivot | 40.2% |
| above_prev_high | 9.9% |
| above_prev_high_clearance_atr_05 | 0.7% |
| above_prev_low | 81.7% |
| above_r1 | 5.6% |
| above_r2 | 1.5% |
| above_vwap | 63.5% |
| above_wood_p | 54.2% |
| ad_rising | 73.7% |
| adx_cross_up | 3.0% |
| adx_cross_up_20 | 3.3% |
| adx_di_bear | 16.4% |
| adx_di_bull | 83.6% |
| adx_strong | 4.0% |
| adx_trending | 36.0% |
| ao_cross_dn | 0.1% |
| ao_cross_up | 5.9% |
| ao_positive | 73.5% |
| ao_twin_peaks_bull | 1.3% |
| at_key_fib | 16.9% |
| at_key_fib_wide | 37.7% |
| avwap_20high_loss_recent_3d | 33.6% |
| avwap_20high_reclaim_recent_3d | 19.8% |
| avwap_20low_loss_recent_3d | 1.5% |
| avwap_20low_reclaim_recent_3d | 6.4% |
| avwap_252low_loss_recent_3d | 2.2% |
| avwap_252low_reclaim_recent_3d | 6.1% |
| avwap_50low_loss_recent_3d | 2.0% |
| avwap_50low_reclaim_recent_3d | 6.9% |
| bb_10_20_above_mid | 93.7% |
| bb_10_20_expanding | 50.1% |
| bb_10_20_pctb_gt_75 | 54.7% |
| bb_10_20_pctb_gt_8 | 35.9% |
| bb_10_20_pctb_gt_85 | 17.1% |
| bb_10_20_pctb_gt_9 | 5.8% |
| bb_10_20_pctb_gt_95 | 1.7% |
| bb_10_20_pctb_lt_05 | 0.1% |
| bb_10_20_pctb_lt_1 | 0.1% |
| bb_10_20_pctb_lt_15 | 0.2% |
| bb_10_20_pctb_lt_2 | 0.4% |
| bb_10_20_pctb_lt_25 | 0.5% |
| bb_10_20_reclaim_from_lower_recent_3d | 0.3% |
| bb_10_20_reclaim_from_upper_recent_3d | 28.0% |
| bb_10_20_squeeze | 34.4% |
| bb_10_20_touch_lower | 0.3% |
| bb_10_20_touch_upper | 2.7% |
| bb_20_15_above_mid | 96.8% |
| bb_20_15_expanding | 68.6% |
| bb_20_15_pctb_gt_75 | 80.8% |
| bb_20_15_pctb_gt_8 | 75.0% |
| bb_20_15_pctb_gt_85 | 68.3% |
| bb_20_15_pctb_gt_9 | 60.5% |
| bb_20_15_pctb_gt_95 | 51.4% |
| bb_20_15_pctb_lt_25 | 0.0% |
| bb_20_15_reclaim_from_lower_recent_3d | 0.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 28.0% |
| bb_20_15_squeeze | 34.4% |
| bb_20_15_touch_lower | 0.0% |
| bb_20_15_touch_upper | 52.7% |
| bb_20_20_above_mid | 96.8% |
| bb_20_20_expanding | 68.6% |
| bb_20_20_pctb_gt_75 | 70.6% |
| bb_20_20_pctb_gt_8 | 60.5% |
| bb_20_20_pctb_gt_85 | 47.7% |
| bb_20_20_pctb_gt_9 | 33.2% |
| bb_20_20_pctb_gt_95 | 19.8% |
| bb_20_20_reclaim_from_lower_recent_3d | 0.1% |
| bb_20_20_reclaim_from_upper_recent_3d | 33.7% |
| bb_20_20_squeeze | 17.9% |
| bb_20_20_touch_lower | 0.0% |
| bb_20_20_touch_upper | 17.5% |
| bearish_engulfing | 7.2% |
| bearish_pin_bar | 7.3% |
| below_avwap_20high | 63.0% |
| below_avwap_20low | 1.6% |
| below_avwap_252low | 10.7% |
| below_avwap_50low | 3.3% |
| below_cam_s3 | 43.7% |
| below_cam_s4 | 19.3% |
| below_cpr | 59.8% |
| below_ema_20 | 8.1% |
| below_ema_200 | 32.3% |
| below_ema_200_break_recent_5d | 2.8% |
| below_ema_20_break_recent_5d | 6.0% |
| below_ema_21 | 9.0% |
| below_ema_21_break_recent_5d | 6.5% |
| below_ema_50 | 22.5% |
| below_ema_50_break_recent_5d | 4.4% |
| below_ema_9 | 6.3% |
| below_ema_9_break_recent_5d | 6.2% |
| below_prev_high | 89.8% |
| below_prev_low | 18.2% |
| below_prev_low_clearance_atr_05 | 2.9% |
| below_s1 | 20.0% |
| below_s2 | 4.5% |
| below_sma_20 | 3.2% |
| below_sma_200 | 34.3% |
| below_sma_21 | 4.0% |
| below_sma_50 | 28.7% |
| below_sma_9 | 7.9% |
| below_vwap | 36.5% |
| blowoff_recent_3d | 1.9% |
| break_52w_high | 0.9% |
| break_52w_high_clearance_atr_05 | 0.0% |
| break_52w_high_confirmed_today | 6.4% |
| bullish_engulfing | 0.9% |
| bullish_pin_bar | 7.2% |
| capitulation_recent_3d | 0.1% |
| ceo_buy | 0.8% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 94.6% |
| chandelier_long_flip_dn | 1.1% |
| chandelier_short_bearish | 25.8% |
| chandelier_short_flip_up | 1.6% |
| classification_change_from_tech | 91.7% |
| classification_change_to_defensive | 8.3% |
| close_above_open | 16.0% |
| close_below_open | 82.4% |
| close_in_bottom_40pct_of_range | 58.1% |
| close_in_top_40pct_of_range | 19.6% |
| cluster_buy | 0.4% |
| cmf_cross_dn | 3.8% |
| cmf_cross_up | 3.4% |
| cmf_negative | 29.0% |
| cmf_positive | 71.0% |
| concentrated_sell | 6.0% |
| cpr_narrow | 86.7% |
| cpr_narrow_tight | 23.5% |
| cup_handle_detected | 13.9% |
| cup_handle_neckline_break_retest_long | 13.6% |
| dc10_breakout_dn | 0.0% |
| dc10_breakout_dn_1pct | 0.4% |
| dc10_breakout_up | 8.2% |
| dc10_breakout_up_1pct | 30.7% |
| dc10_new_high | 36.8% |
| dc10_strong_breakout_up | 0.3% |
| dc20_breakout_up | 6.1% |
| dc20_new_high | 29.2% |
| dc20_resistance_break_retest_strong | 40.3% |
| dc20_support_break_retest_strong | 0.1% |
| defensive_leadership | 43.3% |
| director_only_buy | 3.6% |
| doji | 8.0% |
| double_bottom_detected | 15.7% |
| double_top_detected | 17.1% |
| dpi_elevated | 54.8% |
| drying_volume_on_down_turn | 56.7% |
| drying_volume_on_up_turn | 12.0% |
| ema_20_50_bearish | 42.9% |
| ema_20_50_bullish | 57.1% |
| ema_20_50_death_cross | 0.0% |
| ema_20_50_golden_cross | 2.2% |
| ema_50_200_bearish | 44.4% |
| ema_50_200_bullish | 55.6% |
| ema_50_200_death_cross | 0.1% |
| ema_50_200_golden_cross | 0.6% |
| ema_9_21_bearish | 21.3% |
| ema_9_21_bullish | 78.7% |
| ema_9_21_death_cross | 0.0% |
| ema_9_21_golden_cross | 3.8% |
| evening_star | 5.6% |
| flag_bear_break_retest_short | 0.0% |
| flag_bear_broke | 0.0% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 2.0% |
| flag_bull_broke | 2.1% |
| flag_bull_detected | 0.3% |
| force_index_cross_dn | 3.2% |
| force_index_cross_up | 1.6% |
| force_index_positive | 91.3% |
| gap_dn_1_5pct | 2.9% |
| gap_dn_2pct | 1.4% |
| gap_up_1_5pct | 4.5% |
| gap_up_2pct | 2.4% |
| hammer | 5.6% |
| head_shoulders_bottom_detected | 4.3% |
| head_shoulders_top_detected | 5.6% |
| house_cluster_buy | 3.9% |
| house_cluster_sell | 4.5% |
| htf_aligned_bear | 16.4% |
| htf_aligned_bull | 54.9% |
| htf_disagreement | 2.7% |
| hull_bearish | 4.0% |
| hull_bullish | 96.0% |
| hull_flip_dn | 1.4% |
| hull_flip_up | 1.0% |
| ichi_above_cloud | 55.7% |
| ichi_above_cloud_break_recent_5d | 16.9% |
| ichi_below_cloud | 29.2% |
| ichi_below_cloud_break_recent_5d | 3.2% |
| ichi_cloud_thick | 86.1% |
| ichi_tk_bearish | 28.6% |
| ichi_tk_bullish | 65.9% |
| ichi_tk_cross_dn | 0.1% |
| ichi_tk_cross_up | 4.6% |
| ichi_weekly_above_cloud | 52.3% |
| ichi_weekly_below_cloud | 22.8% |
| ichi_weekly_in_cloud | 24.9% |
| in_reversal_window | 0.7% |
| inside_bar | 19.2% |
| inside_cpr | 1.0% |
| inside_kc | 75.6% |
| insider_cluster_active | 18.3% |
| institutional_buy | 88.5% |
| institutional_negative | 5.1% |
| institutional_persistence_growing | 42.1% |
| institutional_persistence_strong | 58.3% |
| institutional_strong_buy | 78.8% |
| inverted_cup_handle_detected | 11.0% |
| is_friday | 20.6% |
| is_halloween_period | 50.2% |
| is_halloween_period_first_day | 0.6% |
| is_january | 11.8% |
| is_january_extended | 13.8% |
| is_monday | 20.9% |
| is_pre_holiday | 4.6% |
| is_summer_period | 49.8% |
| is_totm_window | 34.3% |
| is_totm_window_first_day | 10.7% |
| is_week_open | 23.6% |
| kc_touch_upper | 30.1% |
| large_dollar_buy | 0.9% |
| macd_12_26_9_bearish | 3.0% |
| macd_12_26_9_bullish | 97.0% |
| macd_12_26_9_crossover_dn | 0.3% |
| macd_12_26_9_crossover_up | 1.2% |
| macd_8_21_5_bearish | 4.0% |
| macd_8_21_5_bullish | 96.0% |
| macd_8_21_5_crossover_dn | 1.7% |
| macd_8_21_5_crossover_up | 0.6% |
| marubozu_bear | 0.5% |
| marubozu_bull | 0.1% |
| mfi_broad_overbought | 36.0% |
| mfi_broad_oversold | 0.2% |
| mfi_overbought | 11.9% |
| mfi_oversold | 0.1% |
| monthly_above_sma_12 | 64.7% |
| monthly_above_sma_6 | 66.1% |
| monthly_bias_bear | 26.2% |
| monthly_bias_bull | 56.9% |
| monthly_momentum_pos | 63.0% |
| morning_star | 0.8% |
| near_52w_high | 14.3% |
| near_52w_high_95pct | 28.8% |
| near_52w_high_retest_long | 0.1% |
| near_52w_low_105pct | 0.5% |
| near_52w_low_retest_short | 1.0% |
| near_avwap_20high_atr_05x | 69.0% |
| near_avwap_20high_atr_10x | 89.5% |
| near_avwap_20high_atr_15x | 96.8% |
| near_avwap_20high_atr_20x | 99.2% |
| near_avwap_20low_atr_05x | 10.1% |
| near_avwap_20low_atr_10x | 28.2% |
| near_avwap_20low_atr_15x | 47.7% |
| near_avwap_20low_atr_20x | 64.9% |
| near_avwap_252low_atr_05x | 6.8% |
| near_avwap_252low_atr_10x | 15.7% |
| near_avwap_252low_atr_15x | 24.8% |
| near_avwap_252low_atr_20x | 32.9% |
| near_avwap_50low_atr_05x | 8.6% |
| near_avwap_50low_atr_10x | 23.9% |
| near_avwap_50low_atr_15x | 39.3% |
| near_avwap_50low_atr_20x | 52.3% |
| near_cam_r3 | 11.8% |
| near_cam_s3 | 28.6% |
| near_cam_s4 | 17.8% |
| near_fib_236 | 6.5% |
| near_fib_382 | 5.9% |
| near_fib_500 | 5.9% |
| near_fib_618 | 5.3% |
| near_fib_786 | 2.1% |
| near_pivot | 26.1% |
| near_prev_close | 24.0% |
| near_prev_high | 11.6% |
| near_prev_low | 15.4% |
| near_r1 | 6.5% |
| near_r1_wide | 51.1% |
| near_r2 | 1.8% |
| near_r2_wide | 22.8% |
| near_s1 | 18.7% |
| near_s1_wide | 73.2% |
| near_s2 | 4.5% |
| near_s2_wide | 35.1% |
| near_s3 | 1.6% |
| near_wood_r1 | 17.8% |
| near_wood_s1 | 11.1% |
| news_uses_polygon_score | 24.1% |
| obv_bearish | 15.4% |
| obv_bullish | 84.6% |
| obv_diverge_bull | 4.6% |
| obv_falling | 21.5% |
| obv_rising | 78.5% |
| outside_bar | 9.4% |
| pead_negative_surprise | 13.0% |
| pead_positive_surprise | 27.4% |
| pin_bar | 14.5% |
| po3_accumulation_active | 28.8% |
| po3_bearish | 22.3% |
| po3_bullish | 3.0% |
| po3_manipulation_sweep_down | 2.2% |
| po3_manipulation_sweep_up | 9.5% |
| po3_mmbm_setup | 0.6% |
| po3_mmsm_setup | 5.8% |
| po3_sweep_above_prior_high | 55.3% |
| po3_sweep_below_prior_low | 44.2% |
| ppo_bullish | 96.7% |
| ppo_crossover_dn | 0.4% |
| ppo_crossover_up | 1.2% |
| pre_fomc_d0 | 2.6% |
| pre_fomc_d1 | 2.9% |
| pre_fomc_window | 5.5% |
| price_above_dema | 92.3% |
| price_above_ema_20 | 91.9% |
| price_above_ema_200 | 67.7% |
| price_above_ema_200_break_recent_5d | 14.7% |
| price_above_ema_20_break_recent_5d | 33.8% |
| price_above_ema_21 | 91.0% |
| price_above_ema_21_break_recent_5d | 33.5% |
| price_above_ema_50 | 77.5% |
| price_above_ema_50_break_recent_5d | 26.0% |
| price_above_ema_9 | 93.7% |
| price_above_ema_9_break_recent_5d | 33.5% |
| price_above_hull | 67.9% |
| price_above_sma_200 | 65.7% |
| price_above_sma_21 | 96.0% |
| price_above_sma_50 | 71.2% |
| price_above_tema | 78.4% |
| price_below_dema | 7.7% |
| price_below_hull | 32.1% |
| price_below_tema | 21.6% |
| psar_bullish | 95.4% |
| psar_flip_dn | 0.5% |
| psar_flip_up | 1.2% |
| r1_break_retest_long | 94.0% |
| recent_blowoff_at_r3 | 0.3% |
| resistance_break_retest | 53.1% |
| risk_off_regime_bond_signal | 14.2% |
| risk_off_regime_bond_signal_strong | 3.6% |
| risk_off_regime_gold_signal | 35.9% |
| risk_on_regime_bond_signal | 47.6% |
| risk_on_regime_bond_signal_strong | 20.1% |
| roc_positive | 95.0% |
| roc_turning_dn | 2.6% |
| roc_turning_up | 2.7% |
| rsi_14_bullish | 86.0% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 1.7% |
| rsi_14_cross_dn_overbought_recent_3d | 9.1% |
| rsi_14_cross_up_oversold_recent_3d | 0.1% |
| rsi_14_extreme_ob | 1.8% |
| rsi_14_overbought | 15.3% |
| rsi_14_rising | 26.5% |
| rsi_21_bullish | 79.4% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.4% |
| rsi_21_cross_dn_overbought_recent_3d | 3.8% |
| rsi_21_extreme_ob | 0.3% |
| rsi_21_overbought | 6.1% |
| rsi_21_rising | 26.5% |
| rsi_2_bullish | 68.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 64.1% |
| rsi_2_cross_dn_overbought_recent_3d | 56.8% |
| rsi_2_cross_up_extreme_os_recent_3d | 5.6% |
| rsi_2_cross_up_oversold_recent_3d | 10.8% |
| rsi_2_extreme_ob | 26.6% |
| rsi_2_extreme_os | 3.6% |
| rsi_2_overbought | 39.6% |
| rsi_2_oversold | 10.0% |
| rsi_2_rising | 26.4% |
| rsi_9_bullish | 93.9% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 9.4% |
| rsi_9_cross_dn_overbought_recent_3d | 18.8% |
| rsi_9_cross_up_oversold_recent_3d | 0.4% |
| rsi_9_extreme_ob | 6.9% |
| rsi_9_overbought | 29.7% |
| rsi_9_rising | 26.4% |
| s1_break_retest_short | 8.4% |
| sc_13d_filed_within_30d | 3.3% |
| sc_13g_filed_within_30d | 3.4% |
| sector_outperforming_spy | 45.4% |
| sector_underperforming_spy | 54.6% |
| shooting_star | 5.2% |
| sma_20_50_bullish | 42.3% |
| sma_20_50_golden_cross | 2.3% |
| sma_50_200_bullish | 55.7% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 83.2% |
| sma_9_21_golden_cross | 6.2% |
| smc_bos_bearish | 7.1% |
| smc_bos_bullish | 16.1% |
| smc_bos_retest_long | 4.6% |
| smc_bos_retest_short | 3.9% |
| smc_breaker_block_bearish | 11.9% |
| smc_breaker_block_bullish | 27.4% |
| smc_choch_bearish | 3.1% |
| smc_choch_bullish | 4.8% |
| smc_equal_highs_swept | 4.7% |
| smc_equal_lows_swept | 3.3% |
| smc_fvg_bearish_active | 6.6% |
| smc_fvg_bullish_active | 74.3% |
| smc_fvg_retest_long_zone | 18.6% |
| smc_fvg_retest_short_zone | 1.0% |
| smc_in_discount_zone | 39.0% |
| smc_in_premium_zone | 80.7% |
| smc_inverse_fvg_bearish | 58.6% |
| smc_inverse_fvg_bullish | 97.2% |
| smc_liquidity_swept_dn | 1.2% |
| smc_liquidity_swept_up | 1.6% |
| smc_mitigation_block_long | 0.1% |
| smc_mitigation_block_short | 3.9% |
| smc_ob_bearish_active | 30.7% |
| smc_ob_bullish_active | 36.8% |
| smc_ote_long_zone | 7.7% |
| smc_ote_short_zone | 5.5% |
| squeeze_fire_dn | 1.0% |
| squeeze_fire_up | 0.9% |
| squeeze_in | 17.3% |
| squeeze_positive | 93.5% |
| stoch_bearish_cross | 25.7% |
| stoch_broad_overbought | 81.9% |
| stoch_bullish_cross | 3.7% |
| stoch_overbought | 73.0% |
| supertrend_flip_recent_long_5d | 0.1% |
| supertrend_flip_recent_short_5d | 0.0% |
| support_break_retest | 0.1% |
| tema_above_dema | 87.5% |
| tema_cross_dn | 0.1% |
| tema_cross_up | 3.8% |
| three_black_crows | 0.8% |
| three_white_soldiers | 2.0% |
| triangle_apex_break_retest_long | 19.1% |
| triangle_ascending_detected | 11.5% |
| triangle_descending_detected | 10.8% |
| uo_overbought | 7.5% |
| usd_strengthening | 20.6% |
| usd_weakening | 11.6% |
| vix_band_high | 33.1% |
| vix_band_low | 38.6% |
| vix_band_mid | 28.3% |
| vix_term_backwardation | 2.3% |
| vix_term_contango | 97.7% |
| vol_above_avg | 30.2% |
| vol_below_avg | 69.8% |
| vol_spike_12x | 14.7% |
| vol_spike_15x | 6.4% |
| vol_spike_17x | 3.5% |
| vol_spike_2x | 1.9% |
| vol_spike_2x_on_down_day_recent_3d | 1.0% |
| vol_spike_2x_on_up_day_recent_3d | 6.7% |
| vol_spike_3x | 0.3% |
| vp_above_value_area | 40.5% |
| vp_below_value_area | 2.4% |
| vp_close_above_poc | 75.8% |
| vp_close_below_poc | 24.2% |
| vp_in_value_area | 57.1% |
| week_open_gap_down_15pct | 0.9% |
| week_open_gap_up_15pct | 1.0% |
| weekly_above_ema_10 | 78.1% |
| weekly_above_ema_20 | 70.7% |
| weekly_bias_bear | 20.4% |
| weekly_bias_bull | 69.3% |
| weekly_momentum_pos | 87.3% |
| williams_r_overbought | 58.5% |
| williams_r_rising | 17.5% |
| within_pead_window | 41.6% |
| within_post_deletion_window | 3.5% |
| within_post_inclusion_window | 2.2% |
| within_pre_rebalance_window | 1.1% |
| xs_avoid_high_ivol | 74.0% |
| xs_avoid_high_max | 68.6% |
| xs_high_beta_decile | 24.6% |
| xs_low_beta_bottom_quintile | 24.6% |
| xs_low_beta_decile | 17.4% |
| xs_low_beta_decile_entry_recent_5d | 0.5% |
| xs_low_beta_top_quintile | 17.4% |
| xs_momentum_bottom_decile | 9.9% |
| xs_momentum_bottom_quintile | 18.7% |
| xs_momentum_top_decile | 12.8% |
| xs_momentum_top_quintile | 22.8% |
| xs_quality_bottom_quintile | 20.5% |
| xs_quality_top_quintile | 20.8% |
| xs_quality_top_tercile | 41.2% |
| year_high_break_retest_long | 10.8% |
| yoy_surprise_high | 57.0% |
| yoy_surprise_negative | 33.0% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.0% |
| committed_growth_holders | 91.0% |
| corp_donations_1y | 9.1% |
| corp_donations_count_1y | 9.1% |
| corp_donations_unique_pacs | 9.1% |
| cot_rut_commercials_pctile_3y | 54.1% |
| cot_rut_mmoney_pctile_3y | 54.1% |
| cup_handle_depth_pct | 20.1% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 6.6% |
| days_since_inclusion | 13.0% |
| days_to_next_holiday | 65.7% |
| days_to_rebalance | 8.5% |
| dpi_30d_avg | 95.5% |
| dpi_recent | 95.5% |
| earnings_announcement_return | 92.1% |
| earnings_eps_yoy_growth | 95.0% |
| flag_bear_pole_move_pct | 0.2% |
| flag_bull_pole_move_pct | 0.3% |
| gov_contracts_4q_sum | 39.7% |
| gov_contracts_last_qtr_amount | 39.7% |
| gov_contracts_qoq_growth | 39.7% |
| head_shoulders_magnitude_pct | 9.5% |
| insider_director_buyers_30d | 5.0% |
| insider_officer_buyers_30d | 5.0% |
| insider_total_shares_bought_30d | 5.0% |
| insider_unique_buyers_30d | 5.0% |
| inverted_cup_handle_height_pct | 18.2% |
| lobbying_amount_1y | 70.6% |
| lobbying_amount_q | 70.6% |
| lobbying_amount_yoy | 70.6% |
| otc_short_ratio_recent | 95.5% |
| otc_volume_recent | 95.5% |
| pair_half_life | 92.0% |
| pair_max_abs_zscore | 92.0% |
| pair_zscore_signed | 92.0% |
| pct_from_avwap_20high | 69.9% |
| persistent_holders_4q | 91.0% |
| persistent_holders_8q | 91.0% |
| sc_13g_latest_percent_owned | 1.6% |
| search_volume_index_recent | 78.2% |
| search_volume_observations | 78.2% |
| search_volume_zscore_30d | 78.2% |
| sector_etf_return_20d | 2.3% |
| spy_return_20d | 2.3% |
| total_active_holders | 91.0% |
| triangle_breakdown_pct | 10.8% |
| triangle_breakout_pct | 11.5% |
| xs_quality_decile | 61.5% |
| xs_quality_gross_profitability | 61.5% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.995), `avwap_50low` (1.0), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (1.0), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.998), `double_top_peak` (0.997), `entry_stop_long` (0.999), `entry_stop_short` (0.999), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.994), `fib_ext_162` (0.992), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (0.991), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.993), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.986), `monthly_sma_6` (0.996), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.999), `r1` (0.999), `r2` (0.999), `r3` (0.998), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.999), `swing_high` (0.996), `swing_low` (0.997), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.997), `vp_value_area_low` (0.997), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.975), `year_low` (0.971)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | cross guard band (k > 20 on cross_dn) | 2 | subset-safe | no - derives offline |
| P2.1 | overbought threshold on k | 4 | subset-safe | no - derives offline |
| P2.2 | period (rsi+stoch length) | 3 | **FIRE-ADDING** | **YES** |
| P3 | rsi_14 > 45 | 5 | subset-safe | no - derives offline |
| P4 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     2 x 4 x 3 x 5 x 1 = 120
offline gradings   40 level-combinations x 24 exits = 960
ENGINE RUNS        3 (every fire-adding axis sits at production-only until its env actuator exists)
check              3 x 40 = 120
```

B-row candidates NOT in this factorial: 622 census axes join it only when REGISTERED at the T3 band review.
