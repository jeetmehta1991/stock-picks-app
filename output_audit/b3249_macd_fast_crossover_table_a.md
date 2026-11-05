# Table A - macd_fast_crossover

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build ff10274b7 | commit 352770ae3 at 2026-11-05 02:36:06 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** momentum | **status:** NOT-STARTED | **R5 fires:** 4070 (closed fires in the exit cube: 4070 of 4070, S6-B3258) | **surviving fires (T1):** 4070 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  macd_8_21_5_crossover_dn  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define
P2  macd_8_21_5_crossover_up  <- backtest/signals/technical.py (f-string template)
       DEFN: read the producer source (evidence column)
       knobs bands to define

============================== STRATEGY LAYER ==============================

P3  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_macd_fast_crossover (docstring and return dropped):

```python
fl = s.get('macd_8_21_5_crossover_up')
fs = s.get('macd_8_21_5_crossover_dn') and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | macd_8_21_5_crossover_dn - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P2 | PRODUCER | macd_8_21_5_crossover_up - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | see evidence | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P3 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
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
| adx | backtest/signals/technical.py | 100.0% | 17.17, 22.01, 27.314, 34.084 | 17.17: 3257 (80%); 22.01: 2443 (60%); 27.314: 1628 (40%); 34.084: 814 (20%) | 17.17: 815 (20%); 22.01: 1631 (40%); 27.314: 2442 (60%); 34.084: 3256 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 17.346, 21.902, 25.94, 30.11 | 17.346: 3256 (80%); 21.902: 2442 (60%); 25.94: 1629 (40%); 30.11: 815 (20%) | 17.346: 814 (20%); 21.902: 1628 (40%); 25.94: 2446 (60%); 30.11: 3259 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 16.598, 20.76, 24.894, 29.272 | 16.598: 3256 (80%); 20.76: 2445 (60%); 24.894: 1628 (40%); 29.272: 814 (20%) | 16.598: 814 (20%); 20.76: 1629 (40%); 24.894: 2442 (60%); 29.272: 3256 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -6.3037, -1.6533, 1.6369, 6.6539 | -6.3037: 3256 (80%); -1.6533: 2442 (60%); 1.6369: 1628 (40%); 6.6539: 814 (20%) | -6.3037: 814 (20%); -1.6533: 1628 (40%); 1.6369: 2442 (60%); 6.6539: 3256 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.2067, 2.1118, 3.5286, 6.214 | 1.2067: 3256 (80%); 2.1118: 2442 (60%); 3.5286: 1628 (40%); 6.214: 814 (20%) | 1.2067: 814 (20%); 2.1118: 1628 (40%); 3.5286: 2442 (60%); 6.214: 3256 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.2067, 2.1118, 3.5286, 6.214 | 1.2067: 3256 (80%); 2.1118: 2442 (60%); 3.5286: 1628 (40%); 6.214: 814 (20%) | 1.2067: 814 (20%); 2.1118: 1628 (40%); 3.5286: 2442 (60%); 6.214: 3256 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.039, 2.5402, 3.0654, 4.0146 | 2.039: 3257 (80%); 2.5402: 2442 (60%); 3.0654: 1628 (40%); 4.0146: 814 (20%) | 2.039: 816 (20%); 2.5402: 1628 (40%); 3.0654: 2442 (60%); 4.0146: 3256 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0508, 0.0706, 0.0937, 0.133 | 0.0508: 3259 (80%); 0.0706: 2443 (60%); 0.0937: 1629 (40%); 0.133: 815 (20%) | 0.0508: 817 (20%); 0.0706: 1633 (40%); 0.0937: 2444 (60%); 0.133: 3258 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.3349, 0.4528, 0.5379, 0.6372 | 0.3349: 3256 (80%); 0.4528: 2442 (60%); 0.5379: 1628 (40%); 0.6372: 815 (20%) | 0.3349: 814 (20%); 0.4528: 1630 (40%); 0.5379: 2442 (60%); 0.6372: 3259 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0654, 0.093, 0.1239, 0.1692 | 0.0654: 3258 (80%); 0.093: 2444 (60%); 0.1239: 1631 (40%); 0.1692: 815 (20%) | 0.0654: 815 (20%); 0.093: 1631 (40%); 0.1239: 2446 (60%); 0.1692: 3257 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2219, 0.3605, 0.6011, 0.7625 | 0.2219: 3256 (80%); 0.3605: 2442 (60%); 0.6011: 1628 (40%); 0.7625: 816 (20%) | 0.2219: 815 (20%); 0.3605: 1628 (40%); 0.6011: 2442 (60%); 0.7625: 3256 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0873, 0.124, 0.1652, 0.2255 | 0.0873: 3256 (80%); 0.124: 2443 (60%); 0.1652: 1631 (40%); 0.2255: 815 (20%) | 0.0873: 816 (20%); 0.124: 1631 (40%); 0.1652: 2446 (60%); 0.2255: 3256 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.2914, 0.3954, 0.5758, 0.6969 | 0.2914: 3256 (80%); 0.3954: 2442 (60%); 0.5758: 1628 (40%); 0.6969: 816 (20%) | 0.2914: 815 (20%); 0.3954: 1628 (40%); 0.5758: 2442 (60%); 0.6969: 3256 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0484, -0.0232, -0.0027, 0.0239 | -0.0484: 3263 (80%); -0.0232: 2478 (61%); -0.0027: 1632 (40%); 0.0239: 814 (20%) | -0.0484: 825 (20%); -0.0232: 1630 (40%); -0.0027: 2448 (60%); 0.0239: 3256 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1424, 0.167, 0.2045, 0.2664 | 0.1424: 3264 (80%); 0.167: 2443 (60%); 0.2045: 1628 (40%); 0.2664: 821 (20%) | 0.1424: 806 (20%); 0.167: 1627 (40%); 0.2045: 2442 (60%); 0.2664: 3249 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 4070 (100%) | 0: 3878 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1064, -0.0168, 0.0589, 0.1432 | -0.1064: 3258 (80%); -0.0168: 2442 (60%); 0.0589: 1630 (40%); 0.1432: 815 (20%) | -0.1064: 815 (20%); -0.0168: 1629 (40%); 0.0589: 2442 (60%); 0.1432: 3256 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 4070 (100%); 1: 1633 (40%) | 0: 2437 (60%); 1: 3330 (82%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2396, -0.197, -0.1544, -0.1207 | -0.2396: 3263 (80%); -0.197: 2445 (60%); -0.1544: 1637 (40%); -0.1207: 855 (21%) | -0.2396: 828 (20%); -0.197: 1635 (40%); -0.1544: 2450 (60%); -0.1207: 3271 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.6026, 0.6923, 0.7692 | 0.391: 3265 (80%); 0.6026: 2454 (60%); 0.6923: 1658 (41%); 0.7692: 903 (22%) | 0.391: 849 (21%); 0.6026: 1687 (41%); 0.6923: 2494 (61%); 0.7692: 3321 (82%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.391, 0.6154, 0.8333 | 0.2564: 3329 (82%); 0.391: 2474 (61%); 0.6154: 1635 (40%); 0.8333: 874 (21%) | 0.2564: 857 (21%); 0.391: 1631 (40%); 0.6154: 2447 (60%); 0.8333: 3257 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.093, -0.0139, 0.0789, 0.1961 | -0.093: 3262 (80%); -0.0139: 2443 (60%); 0.0789: 1629 (40%); 0.1961: 827 (20%) | -0.093: 829 (20%); -0.0139: 1641 (40%); 0.0789: 2444 (60%); 0.1961: 3264 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.4551, 0.5897, 0.7628 | 0.2564: 3303 (81%); 0.4551: 2475 (61%); 0.5897: 1647 (40%); 0.7628: 841 (21%) | 0.2564: 846 (21%); 0.4551: 1663 (41%); 0.5897: 2482 (61%); 0.7628: 3261 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.141, 0.3051, 0.4679, 0.6487 | 0.141: 3258 (80%); 0.3051: 2442 (60%); 0.4679: 1641 (40%); 0.6487: 814 (20%) | 0.141: 822 (20%); 0.3051: 1628 (40%); 0.4679: 2473 (61%); 0.6487: 3256 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.497, -0.3438, -0.1503, 0.0881 | -0.497: 3257 (80%); -0.3438: 2445 (60%); -0.1503: 1628 (40%); 0.0881: 819 (20%) | -0.497: 873 (21%); -0.3438: 1630 (40%); -0.1503: 2442 (60%); 0.0881: 3268 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3333, 0.5192, 0.75, 0.9295 | 0.3333: 3274 (80%); 0.5192: 2456 (60%); 0.75: 1629 (40%); 0.9295: 822 (20%) | 0.3333: 824 (20%); 0.5192: 1686 (41%); 0.75: 2466 (61%); 0.9295: 3265 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1154, 0.3141, 0.5833, 0.8205 | 0.1154: 3277 (81%); 0.3141: 2492 (61%); 0.5833: 1646 (40%); 0.8205: 820 (20%) | 0.1154: 837 (21%); 0.3141: 1637 (40%); 0.5833: 2476 (61%); 0.8205: 3257 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0681, -0.0588, -0.0384, 0 | -0.0681: 3275 (80%); -0.0588: 2468 (61%); -0.0384: 1634 (40%); 0: 1273 (31%) | -0.0681: 827 (20%); -0.0588: 1658 (41%); -0.0384: 2459 (60%); 0: 3949 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.7179, 0.8846, 1 | 0.391: 3280 (81%); 0.7179: 2449 (60%); 0.8846: 1724 (42%); 1: 995 (24%) | 0.391: 855 (21%); 0.7179: 1634 (40%); 0.8846: 2448 (60%); 1: 4070 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1026, 0.2179, 0.5321, 0.8462 | 0.1026: 3304 (81%); 0.2179: 2458 (60%); 0.5321: 1650 (41%); 0.8462: 837 (21%) | 0.1026: 822 (20%); 0.2179: 1657 (41%); 0.5321: 2443 (60%); 0.8462: 3262 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0011, 0.0364, 0.0812, 0.1955 | -0.0011: 3259 (80%); 0.0364: 2446 (60%); 0.0812: 1648 (40%); 0.1955: 823 (20%) | -0.0011: 829 (20%); 0.0364: 1634 (40%); 0.0812: 2463 (61%); 0.1955: 3260 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.446, 0.7788, 0.9231, 0.9744 | 0.446: 3262 (80%); 0.7788: 2464 (61%); 0.9231: 1649 (41%); 0.9744: 917 (23%) | 0.446: 819 (20%); 0.7788: 1636 (40%); 0.9231: 2458 (60%); 0.9744: 3388 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0913, 0.2872, 0.5449, 0.8013 | 0.0913: 3256 (80%); 0.2872: 2442 (60%); 0.5449: 1640 (40%); 0.8013: 819 (20%) | 0.0913: 814 (20%); 0.2872: 1628 (40%); 0.5449: 2453 (60%); 0.8013: 3270 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0132, 0.1104, 0.1876 | -0.0812: 3505 (86%); -0.0132: 2453 (60%); 0.1104: 1634 (40%); 0.1876: 910 (22%) | -0.0812: 935 (23%); -0.0132: 1649 (41%); 0.1104: 2451 (60%); 0.1876: 3275 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1699, -0.0157, 0.0442, 0.0848 | -0.1699: 3258 (80%); -0.0157: 2449 (60%); 0.0442: 1632 (40%); 0.0848: 818 (20%) | -0.1699: 825 (20%); -0.0157: 1636 (40%); 0.0442: 2444 (60%); 0.0848: 3279 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3205, 0.559, 0.7372, 0.8654 | 0.3205: 3272 (80%); 0.559: 2442 (60%); 0.7372: 1698 (42%); 0.8654: 831 (20%) | 0.3205: 824 (20%); 0.559: 1628 (40%); 0.7372: 2483 (61%); 0.8654: 3269 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.141, 0.3718, 0.5641, 0.8141 | 0.141: 3260 (80%); 0.3718: 2448 (60%); 0.5641: 1756 (43%); 0.8141: 830 (20%) | 0.141: 827 (20%); 0.3718: 1643 (40%); 0.5641: 2450 (60%); 0.8141: 3304 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0483, 0.1183, 0.2425, 0.5083 | 0.0483: 3268 (80%); 0.1183: 2457 (60%); 0.2425: 1631 (40%); 0.5083: 815 (20%) | 0.0483: 822 (20%); 0.1183: 1630 (40%); 0.2425: 2443 (60%); 0.5083: 3257 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.5% | 27.4, 62, 82, 141 | 27.4: 3206 (79%); 62: 2407 (59%); 82: 1624 (40%); 141: 811 (20%) | 27.4: 802 (20%); 62: 1671 (41%); 82: 2409 (59%); 141: 3211 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.6% | 1.7688, 2.2861, 2.8588, 3.8198 | 1.7688: 3241 (80%); 2.2861: 2431 (60%); 2.8588: 1621 (40%); 3.8198: 811 (20%) | 1.7688: 811 (20%); 2.2861: 1621 (40%); 2.8588: 2432 (60%); 3.8198: 3241 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 20, 28, 34 | 9: 3337 (82%); 20: 2532 (62%); 28: 1772 (44%); 34: 967 (24%) | 9: 833 (20%); 20: 1687 (41%); 28: 2530 (62%); 34: 3257 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3, 4 | 1: 3339 (82%); 2: 2480 (61%); 3: 1635 (40%); 4: 818 (20%) | 1: 1590 (39%); 2: 2435 (60%); 3: 3252 (80%); 4: 4070 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0139, -0.0042, 0.0099, 0.0224 | -0.0139: 3257 (80%); -0.0042: 2444 (60%); 0.0099: 1636 (40%); 0.0224: 818 (20%) | -0.0139: 816 (20%); -0.0042: 1631 (40%); 0.0099: 2443 (60%); 0.0224: 3257 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5339, 25.8645, 26.4758, 27.11 | 24.5339: 3265 (80%); 25.8645: 2447 (60%); 26.4758: 1630 (40%); 27.11: 821 (20%) | 24.5339: 816 (20%); 25.8645: 1631 (40%); 26.4758: 2445 (60%); 27.11: 3264 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.703, -0.1824, 0.178, 0.724 | -0.703: 3257 (80%); -0.1824: 2442 (60%); 0.178: 1629 (40%); 0.724: 815 (20%) | -0.703: 815 (20%); -0.1824: 1628 (40%); 0.178: 2445 (60%); 0.724: 3257 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.724, -0.178, 0.1824, 0.703 | -0.724: 3257 (80%); -0.178: 2445 (60%); 0.1824: 1628 (40%); 0.703: 815 (20%) | -0.724: 815 (20%); -0.178: 1629 (40%); 0.1824: 2442 (60%); 0.703: 3257 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0459, -0.0114, 0.0187, 0.0616 | -0.0459: 3256 (80%); -0.0114: 2454 (60%); 0.0187: 1630 (40%); 0.0616: 815 (20%) | -0.0459: 814 (20%); -0.0114: 1632 (40%); 0.0187: 2450 (60%); 0.0616: 3257 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0426, 8.4897, 8.7688, 9.0997 | 8.0426: 3251 (80%); 8.4897: 2441 (60%); 8.7688: 1626 (40%); 9.0997: 807 (20%) | 8.0426: 819 (20%); 8.4897: 1629 (40%); 8.7688: 2444 (60%); 9.0997: 3263 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 4040 (99%); 1: 1199 (29%) | 0: 2841 (70%); 1: 3623 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | -1, 0 | -1: 3823 (94%); 0: 3219 (79%) | -1: 821 (20%); 0: 3399 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 4040 (99%); 1: 1338 (33%) | 0: 2702 (66%); 1: 3580 (88%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 132, 272 | 3: 3282 (81%); 6: 2503 (61%); 132: 1629 (40%); 272: 818 (20%) | 3: 1066 (26%); 6: 1761 (43%); 132: 2445 (60%); 272: 3260 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 4, 83, 137 | 1: 3348 (82%); 4: 2568 (63%); 83: 1631 (40%); 137: 819 (20%) | 1: 1050 (26%); 4: 1652 (41%); 83: 2460 (60%); 137: 3263 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.3049, -0.0742, 0.0622, 0.3087 | -0.3049: 3256 (80%); -0.0742: 2442 (60%); 0.0622: 1629 (40%); 0.3087: 815 (20%) | -0.3049: 815 (20%); -0.0742: 1628 (40%); 0.0622: 2443 (60%); 0.3087: 3256 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.4038, -0.6494, 0.6014, 2.5787 | -2.4038: 3256 (80%); -0.6494: 2442 (60%); 0.6014: 1628 (40%); 2.5787: 814 (20%) | -2.4038: 814 (20%); -0.6494: 1628 (40%); 0.6014: 2442 (60%); 2.5787: 3256 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.128, -0.5762, 0.5481, 2.3856 | -2.128: 3256 (80%); -0.5762: 2442 (60%); 0.5481: 1628 (40%); 2.3856: 814 (20%) | -2.128: 814 (20%); -0.5762: 1628 (40%); 0.5481: 2442 (60%); 2.3856: 3256 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.1528, -0.0353, 0.0163, 0.1117 | -0.1528: 3256 (80%); -0.0353: 2442 (60%); 0.0163: 1631 (40%); 0.1117: 815 (20%) | -0.1528: 815 (20%); -0.0353: 1629 (40%); 0.0163: 2442 (60%); 0.1117: 3256 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.4753, -0.6569, 0.6111, 2.5685 | -2.4753: 3256 (80%); -0.6569: 2442 (60%); 0.6111: 1628 (40%); 2.5685: 814 (20%) | -2.4753: 814 (20%); -0.6569: 1628 (40%); 0.6111: 2442 (60%); 2.5685: 3256 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -2.5648, -0.6877, 0.6625, 2.7379 | -2.5648: 3256 (80%); -0.6877: 2442 (60%); 0.6625: 1628 (40%); 2.7379: 814 (20%) | -2.5648: 814 (20%); -0.6877: 1628 (40%); 0.6625: 2442 (60%); 2.7379: 3256 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 36.016, 45.47, 54.864, 64.76 | 36.016: 3256 (80%); 45.47: 2445 (60%); 54.864: 1628 (40%); 64.76: 815 (20%) | 36.016: 814 (20%); 45.47: 1629 (40%); 54.864: 2442 (60%); 64.76: 3257 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0065, 0.016, 0.0322, 0.0621 | 0.0065: 3235 (79%); 0.016: 2426 (60%); 0.0322: 1616 (40%); 0.0621: 809 (20%) | 0.0065: 804 (20%); 0.016: 1613 (40%); 0.0322: 2423 (60%); 0.0621: 3230 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 4070 (100%); 1: 3070 (75%); 3: 1932 (47%); 8: 883 (22%) | 0: 1000 (25%); 1: 1670 (41%); 3: 2473 (61%); 8: 3297 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1429 | 0: 4070 (100%); 0.1429: 861 (21%) | 0: 2845 (70%); 0.1429: 3266 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4, 0.6667 | 0: 4070 (100%); 0.4: 1679 (41%); 0.6667: 869 (21%) | 0: 1629 (40%); 0.4: 2477 (61%); 0.6667: 3346 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 4070 (100%); 1: 2806 (69%); 2: 2080 (51%); 6: 838 (21%) | 0: 1264 (31%); 1: 1990 (49%); 2: 2495 (61%); 6: 3347 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 4070 (100%); 1: 3070 (75%); 3: 1932 (47%); 8: 883 (22%) | 0: 1000 (25%); 1: 1670 (41%); 3: 2473 (61%); 8: 3297 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 4070 (100%); 1: 2889 (71%); 3: 1794 (44%); 7: 902 (22%) | 0: 1181 (29%); 1: 1850 (45%); 3: 2584 (63%); 7: 3301 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2235, 0.375, 0.576 | 0: 3760 (92%); 0.2235: 2442 (60%); 0.375: 1633 (40%); 0.576: 814 (20%) | 0: 932 (23%); 0.2235: 1629 (40%); 0.375: 2453 (60%); 0.576: 3256 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1581, 0.5556 | 0: 3698 (91%); 0.1581: 1628 (40%); 0.5556: 818 (20%) | 0: 2268 (56%); 0.1581: 2442 (60%); 0.5556: 3262 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2894, 0.5721 | 0: 3725 (92%); 0.2894: 1628 (40%); 0.5721: 814 (20%) | 0: 1862 (46%); 0.2894: 2442 (60%); 0.5721: 3256 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2894, 0.5721 | 0: 3725 (92%); 0.2894: 1628 (40%); 0.5721: 814 (20%) | 0: 1862 (46%); 0.2894: 2442 (60%); 0.5721: 3256 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1667, 0, 0.15 | -0.1667: 3259 (80%); 0: 2915 (72%); 0.15: 816 (20%) | -0.1667: 831 (20%); 0: 2938 (72%); 0.15: 3258 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7571, -0.3345, 0, 1.1356 | -0.7571: 3286 (81%); -0.3345: 2443 (60%); 0: 2184 (54%); 1.1356: 824 (20%) | -0.7571: 818 (20%); -0.3345: 1629 (40%); 0: 2454 (60%); 1.1356: 3262 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 3411 (84%); 4: 2631 (65%); 7: 1687 (41%); 11: 829 (20%) | 2: 1060 (26%); 4: 1776 (44%); 7: 2641 (65%); 11: 3364 (83%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0431, -0.0136, 0.0093, 0.0324 | -0.0431: 3255 (80%); -0.0136: 2440 (60%); 0.0093: 1628 (40%); 0.0324: 816 (20%) | -0.0431: 815 (20%); -0.0136: 1630 (40%); 0.0093: 2442 (60%); 0.0324: 3254 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0834, -0.0297, 0.0222, 0.0741 | -0.0834: 3256 (80%); -0.0297: 2442 (60%); 0.0222: 1628 (40%); 0.0741: 815 (20%) | -0.0834: 814 (20%); -0.0297: 1628 (40%); 0.0222: 2442 (60%); 0.0741: 3255 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0217, -0.0069, 0.0051, 0.0217 | -0.0217: 3256 (80%); -0.0069: 2442 (60%); 0.0051: 1629 (40%); 0.0217: 815 (20%) | -0.0217: 814 (20%); -0.0069: 1629 (40%); 0.0051: 2441 (60%); 0.0217: 3255 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -21.418, -6.5948, 7.3928, 28.4078 | -21.418: 3256 (80%); -6.5948: 2442 (60%); 7.3928: 1628 (40%); 28.4078: 814 (20%) | -21.418: 814 (20%); -6.5948: 1628 (40%); 7.3928: 2442 (60%); 28.4078: 3256 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0364, 0.0479, 0.062, 0.0866 | 0.0364: 3259 (80%); 0.0479: 2442 (60%); 0.062: 1634 (40%); 0.0866: 815 (20%) | 0.0364: 815 (20%); 0.0479: 1633 (40%); 0.062: 2442 (60%); 0.0866: 3259 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1499, 0.343, 0.6328, 0.8586 | 0.1499: 3256 (80%); 0.343: 2442 (60%); 0.6328: 1628 (40%); 0.8586: 815 (20%) | 0.1499: 814 (20%); 0.343: 1628 (40%); 0.6328: 2442 (60%); 0.8586: 3257 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.7401, -1.111, 0.9084, 2.1817 | -2.7401: 3256 (80%); -1.111: 2442 (60%); 0.9084: 1628 (40%); 2.1817: 814 (20%) | -2.7401: 814 (20%); -1.111: 1628 (40%); 0.9084: 2442 (60%); 2.1817: 3256 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.3831, -0.1308, 0.0627, 0.2547 | -0.3831: 3256 (80%); -0.1308: 2442 (60%); 0.0627: 1628 (40%); 0.2547: 815 (20%) | -0.3831: 816 (20%); -0.1308: 1628 (40%); 0.0627: 2442 (60%); 0.2547: 3256 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -2.4375, -0.9736, 0.791, 2.0228 | -2.4375: 3256 (80%); -0.9736: 2442 (60%); 0.791: 1628 (40%); 2.0228: 814 (20%) | -2.4375: 814 (20%); -0.9736: 1628 (40%); 0.791: 2442 (60%); 2.0228: 3256 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -5.669, -2.0172, 1.2674, 4.5314 | -5.669: 3257 (80%); -2.0172: 2442 (60%); 1.2674: 1628 (40%); 4.5314: 814 (20%) | -5.669: 815 (20%); -2.0172: 1628 (40%); 1.2674: 2442 (60%); 4.5314: 3256 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 40.598, 46.41, 52.37, 58.972 | 40.598: 3256 (80%); 46.41: 2443 (60%); 52.37: 1629 (40%); 58.972: 814 (20%) | 40.598: 814 (20%); 46.41: 1631 (40%); 52.37: 2445 (60%); 58.972: 3256 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 14.97, 28.932, 64.128, 81.864 | 14.97: 3257 (80%); 28.932: 2442 (60%); 64.128: 1628 (40%); 81.864: 814 (20%) | 14.97: 815 (20%); 28.932: 1628 (40%); 64.128: 2442 (60%); 81.864: 3256 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.48, 46.526, 52.134, 58.6 | 41.48: 3259 (80%); 46.526: 2442 (60%); 52.134: 1628 (40%); 58.6: 815 (20%) | 41.48: 815 (20%); 46.526: 1628 (40%); 52.134: 2442 (60%); 58.6: 3257 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 40.616, 46.88, 52.11, 58.372 | 40.616: 3256 (80%); 46.88: 2446 (60%); 52.11: 1630 (40%); 58.372: 814 (20%) | 40.616: 814 (20%); 46.88: 1630 (40%); 52.11: 2443 (60%); 58.372: 3256 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 4067 (100%) | 0: 4069 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0315, 0.0458, 0.06, 0.0869 | 0.0315: 3257 (80%); 0.0458: 2445 (60%); 0.06: 1636 (40%); 0.0869: 852 (21%) | 0.0315: 823 (20%); 0.0458: 1633 (40%); 0.06: 2451 (60%); 0.0869: 3264 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0821, -0.0569, -0.0444, -0.0348 | -0.0821: 3259 (80%); -0.0569: 2455 (60%); -0.0444: 1644 (40%); -0.0348: 818 (20%) | -0.0821: 823 (20%); -0.0569: 1633 (40%); -0.0444: 2442 (60%); -0.0348: 3258 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 4070 (100%); 2: 856 (21%) | 0: 2753 (68%); 2: 3437 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 25, 41, 57, 68 | 25: 3268 (80%); 41: 2468 (61%); 57: 1632 (40%); 68: 891 (22%) | 25: 848 (21%); 41: 1680 (41%); 57: 2467 (61%); 68: 3285 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.5% | 0.0119, 0.0176, 0.0256, 0.0415 | 0.0119: 3194 (78%); 0.0176: 2406 (59%); 0.0256: 1603 (39%); 0.0415: 803 (20%) | 0.0119: 814 (20%); 0.0176: 1602 (39%); 0.0256: 2405 (59%); 0.0415: 3205 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.1855, 0.3408, 0.6225, 0.8136 | 0.1855: 3256 (80%); 0.3408: 2442 (60%); 0.6225: 1629 (40%); 0.8136: 815 (20%) | 0.1855: 815 (20%); 0.3408: 1628 (40%); 0.6225: 2442 (60%); 0.8136: 3256 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 27.9, 65.72, 99.1, 150.3 | 27.9: 3256 (80%); 65.72: 2441 (60%); 99.1: 1629 (40%); 150.3: 815 (20%) | 27.9: 816 (20%); 65.72: 1628 (40%); 99.1: 2443 (60%); 150.3: 3256 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -3.424, -0.8398, 0.705, 3.4397 | -3.424: 3256 (80%); -0.8398: 2442 (60%); 0.705: 1629 (40%); 3.4397: 814 (20%) | -3.424: 814 (20%); -0.8398: 1628 (40%); 0.705: 2445 (60%); 3.4397: 3256 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 19.096, 34.082, 68.646, 82.774 | 19.096: 3256 (80%); 34.082: 2442 (60%); 68.646: 1628 (40%); 82.774: 814 (20%) | 19.096: 814 (20%); 34.082: 1628 (40%); 68.646: 2442 (60%); 82.774: 3256 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 24.482, 39.316, 61.394, 76.714 | 24.482: 3256 (80%); 39.316: 2442 (60%); 61.394: 1628 (40%); 76.714: 814 (20%) | 24.482: 814 (20%); 39.316: 1628 (40%); 61.394: 2442 (60%); 76.714: 3256 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 22.986, 39.79, 59.118, 75.972 | 22.986: 3256 (80%); 39.79: 2443 (60%); 59.118: 1628 (40%); 75.972: 814 (20%) | 22.986: 814 (20%); 39.79: 1629 (40%); 59.118: 2442 (60%); 75.972: 3256 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 16.908, 38.226, 56.938, 77.744 | 16.908: 3256 (80%); 38.226: 2442 (60%); 56.938: 1628 (40%); 77.744: 814 (20%) | 16.908: 814 (20%); 38.226: 1628 (40%); 56.938: 2442 (60%); 77.744: 3256 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 17 | 4: 3436 (84%); 8: 2598 (64%); 13: 1662 (41%); 17: 905 (22%) | 4: 894 (22%); 8: 1637 (40%); 13: 2581 (63%); 17: 3382 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 18 | 5: 3345 (82%); 9: 2565 (63%); 13: 1799 (44%); 18: 887 (22%) | 5: 917 (23%); 9: 1684 (41%); 13: 2458 (60%); 18: 3429 (84%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 44.01, 48.636, 52.25, 56.306 | 44.01: 3257 (80%); 48.636: 2442 (60%); 52.25: 1632 (40%); 56.306: 814 (20%) | 44.01: 815 (20%); 48.636: 1628 (40%); 52.25: 2445 (60%); 56.306: 3256 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1587, 0.4206, 0.6865, 0.8611 | 0.1587: 3264 (80%); 0.4206: 2448 (60%); 0.6865: 1654 (41%); 0.8611: 822 (20%) | 0.1587: 816 (20%); 0.4206: 1638 (40%); 0.6865: 2445 (60%); 0.8611: 3260 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.95, 17.446, 20.71, 26.09 | 14.95: 3257 (80%); 17.446: 2442 (60%); 20.71: 1629 (40%); 26.09: 824 (20%) | 14.95: 823 (20%); 17.446: 1628 (40%); 20.71: 2449 (60%); 26.09: 3279 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.95, 17.446, 20.71, 26.09 | 14.95: 3257 (80%); 17.446: 2442 (60%); 20.71: 1629 (40%); 26.09: 824 (20%) | 14.95: 823 (20%); 17.446: 1628 (40%); 20.71: 2449 (60%); 26.09: 3279 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8562, 0.8908, 0.9254, 0.9629 | 0.8562: 3256 (80%); 0.8908: 2444 (60%); 0.9254: 1633 (40%); 0.9629: 820 (20%) | 0.8562: 817 (20%); 0.8908: 1634 (40%); 0.9254: 2451 (60%); 0.9629: 3268 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.7, 0.83, 0.95, 1.19 | 0.7: 3290 (81%); 0.83: 2491 (61%); 0.95: 1656 (41%); 1.19: 824 (20%) | 0.7: 834 (20%); 0.83: 1655 (41%); 0.95: 2478 (61%); 1.19: 3271 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0175, 0.0433, 0.0787, 0.1286 | 0.0175: 3257 (80%); 0.0433: 2443 (60%); 0.0787: 1630 (40%); 0.1286: 818 (20%) | 0.0175: 821 (20%); 0.0433: 1630 (40%); 0.0787: 2444 (60%); 0.1286: 3256 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 45.885, 77.5555, 120.993, 204.7478 | 45.885: 3256 (80%); 77.5555: 2442 (60%); 120.993: 1628 (40%); 204.7478: 814 (20%) | 45.885: 814 (20%); 77.5555: 1628 (40%); 120.993: 2442 (60%); 204.7478: 3256 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.3264, 74.7516, 115.5234, 196.8453 | 43.3264: 3256 (80%); 74.7516: 2442 (60%); 115.5234: 1628 (40%); 196.8453: 814 (20%) | 43.3264: 814 (20%); 74.7516: 1628 (40%); 115.5234: 2442 (60%); 196.8453: 3256 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 41.2983, 71.2452, 110.9349, 188.296 | 41.2983: 3256 (80%); 71.2452: 2442 (60%); 110.9349: 1628 (40%); 188.296: 814 (20%) | 41.2983: 814 (20%); 71.2452: 1628 (40%); 110.9349: 2442 (60%); 188.296: 3256 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 48.106, 80.5304, 126.0746, 212.3358 | 48.106: 3256 (80%); 80.5304: 2442 (60%); 126.0746: 1628 (40%); 212.3358: 814 (20%) | 48.106: 814 (20%); 80.5304: 1628 (40%); 126.0746: 2442 (60%); 212.3358: 3256 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 50.3164, 84.0145, 131.4655, 220.333 | 50.3164: 3256 (80%); 84.0145: 2442 (60%); 131.4655: 1628 (40%); 220.333: 814 (20%) | 50.3164: 814 (20%); 84.0145: 1628 (40%); 131.4655: 2442 (60%); 220.333: 3256 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 4070 (100%) | 0: 3676 (90%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 4070 (100%) | 0: 3658 (90%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0778, -0.0287, 0.0175, 0.0666 | -0.0778: 3255 (80%); -0.0287: 2442 (60%); 0.0175: 1629 (40%); 0.0666: 815 (20%) | -0.0778: 817 (20%); -0.0287: 1628 (40%); 0.0175: 2443 (60%); 0.0666: 3256 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -71.032, -57.618, -44.476, -30.898 | -71.032: 3256 (80%); -57.618: 2442 (60%); -44.476: 1628 (40%); -30.898: 814 (20%) | -71.032: 814 (20%); -57.618: 1628 (40%); -44.476: 2442 (60%); -30.898: 3256 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.5646, 0.8395, 1.0644, 1.3646 | 0.5646: 3228 (79%); 0.8395: 2421 (59%); 1.0644: 1614 (40%); 1.3646: 807 (20%) | 0.5646: 808 (20%); 0.8395: 1616 (40%); 1.0644: 2421 (59%); 1.3646: 3228 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 3370 (83%); 5: 2696 (66%); 7: 1930 (47%); 9: 1105 (27%) | 3: 981 (24%); 5: 1730 (43%); 7: 2505 (62%); 9: 3401 (84%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.1% | 0.1923, 0.2348, 0.2852, 0.3707 | 0.1923: 3227 (79%); 0.2348: 2423 (60%); 0.2852: 1615 (40%); 0.3707: 808 (20%) | 0.1923: 807 (20%); 0.2348: 1615 (40%); 0.2852: 2420 (59%); 0.3707: 3227 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 8, 9 | 3: 3434 (84%); 5: 2762 (68%); 8: 1614 (40%); 9: 1194 (29%) | 3: 925 (23%); 5: 1630 (40%); 8: 2839 (70%); 9: 3362 (83%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0235, 0.0323, 0.0428, 0.0622 | 0.0235: 3235 (79%); 0.0323: 2431 (60%); 0.0428: 1615 (40%); 0.0622: 808 (20%) | 0.0235: 809 (20%); 0.0323: 1619 (40%); 0.0428: 2426 (60%); 0.0622: 3230 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 3377 (83%); 5: 2724 (67%); 7: 1954 (48%); 9: 1089 (27%) | 3: 951 (23%); 5: 1700 (42%); 7: 2505 (62%); 9: 3456 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.1% | -0.2166, -0.0618, 0.0675, 0.2607 | -0.2166: 3227 (79%); -0.0618: 2421 (59%); 0.0675: 1615 (40%); 0.2607: 807 (20%) | -0.2166: 807 (20%); -0.0618: 1615 (40%); 0.0675: 2421 (59%); 0.2607: 3227 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.1% | 2, 4, 6, 9 | 2: 3464 (85%); 4: 2618 (64%); 6: 1877 (46%); 9: 835 (21%) | 2: 1008 (25%); 4: 1810 (44%); 6: 2501 (61%); 9: 3533 (87%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.3% |
| 8k_item_5_02_filed_within_7d | 3.5% |
| above_avwap_20high | 18.0% |
| above_avwap_20low | 81.7% |
| above_avwap_252low | 74.1% |
| above_avwap_50low | 81.5% |
| above_cam_r3 | 38.5% |
| above_cam_r4 | 28.6% |
| above_cpr | 47.7% |
| above_pivot | 47.5% |
| above_prev_high | 32.9% |
| above_prev_high_clearance_atr_05 | 13.3% |
| above_prev_low | 63.7% |
| above_r1 | 31.3% |
| above_r2 | 16.3% |
| above_vwap | 50.1% |
| above_wood_p | 47.6% |
| ad_rising | 53.0% |
| adx_cross_up | 0.6% |
| adx_cross_up_20 | 0.6% |
| adx_di_bear | 53.5% |
| adx_di_bull | 46.5% |
| adx_strong | 10.1% |
| adx_trending | 48.0% |
| ao_cross_dn | 0.4% |
| ao_cross_up | 0.3% |
| ao_positive | 49.6% |
| ao_twin_peaks_bull | 16.7% |
| at_key_fib | 11.6% |
| at_key_fib_wide | 29.2% |
| avwap_20high_loss_recent_3d | 30.3% |
| avwap_20high_reclaim_recent_3d | 14.5% |
| avwap_20low_loss_recent_3d | 14.2% |
| avwap_20low_reclaim_recent_3d | 28.0% |
| avwap_252low_loss_recent_3d | 4.3% |
| avwap_252low_reclaim_recent_3d | 14.7% |
| avwap_50low_loss_recent_3d | 8.7% |
| avwap_50low_reclaim_recent_3d | 23.1% |
| bb_10_20_above_mid | 48.9% |
| bb_10_20_expanding | 21.7% |
| bb_10_20_pctb_gt_75 | 8.7% |
| bb_10_20_pctb_gt_8 | 6.1% |
| bb_10_20_pctb_gt_85 | 4.2% |
| bb_10_20_pctb_gt_9 | 3.0% |
| bb_10_20_pctb_gt_95 | 1.9% |
| bb_10_20_pctb_lt_05 | 4.5% |
| bb_10_20_pctb_lt_1 | 5.9% |
| bb_10_20_pctb_lt_15 | 7.5% |
| bb_10_20_pctb_lt_2 | 10.0% |
| bb_10_20_pctb_lt_25 | 12.8% |
| bb_10_20_reclaim_from_lower_recent_3d | 3.9% |
| bb_10_20_reclaim_from_upper_recent_3d | 4.1% |
| bb_10_20_squeeze | 48.5% |
| bb_10_20_touch_lower | 5.4% |
| bb_10_20_touch_upper | 2.7% |
| bb_20_15_above_mid | 48.1% |
| bb_20_15_expanding | 31.1% |
| bb_20_15_pctb_gt_75 | 21.8% |
| bb_20_15_pctb_gt_8 | 14.3% |
| bb_20_15_pctb_gt_85 | 8.0% |
| bb_20_15_pctb_gt_9 | 4.0% |
| bb_20_15_pctb_gt_95 | 2.3% |
| bb_20_15_pctb_lt_05 | 5.1% |
| bb_20_15_pctb_lt_1 | 6.9% |
| bb_20_15_pctb_lt_15 | 10.2% |
| bb_20_15_pctb_lt_2 | 16.7% |
| bb_20_15_pctb_lt_25 | 25.4% |
| bb_20_15_reclaim_from_lower_recent_3d | 24.8% |
| bb_20_15_reclaim_from_upper_recent_3d | 27.4% |
| bb_20_15_squeeze | 31.2% |
| bb_20_15_touch_lower | 5.5% |
| bb_20_15_touch_upper | 3.0% |
| bb_20_20_above_mid | 48.1% |
| bb_20_20_expanding | 31.1% |
| bb_20_20_pctb_gt_75 | 10.0% |
| bb_20_20_pctb_gt_8 | 4.0% |
| bb_20_20_pctb_gt_85 | 2.0% |
| bb_20_20_pctb_gt_9 | 1.3% |
| bb_20_20_pctb_gt_95 | 0.9% |
| bb_20_20_pctb_lt_05 | 2.3% |
| bb_20_20_pctb_lt_1 | 3.1% |
| bb_20_20_pctb_lt_15 | 4.5% |
| bb_20_20_pctb_lt_2 | 6.9% |
| bb_20_20_pctb_lt_25 | 12.2% |
| bb_20_20_reclaim_from_lower_recent_3d | 6.6% |
| bb_20_20_reclaim_from_upper_recent_3d | 6.7% |
| bb_20_20_squeeze | 15.9% |
| bb_20_20_touch_lower | 2.3% |
| bb_20_20_touch_upper | 1.0% |
| bearish_engulfing | 4.4% |
| bearish_pin_bar | 3.6% |
| below_avwap_20high | 82.0% |
| below_avwap_20low | 18.2% |
| below_avwap_252low | 25.9% |
| below_avwap_50low | 18.4% |
| below_cam_s3 | 43.2% |
| below_cam_s4 | 32.0% |
| below_cpr | 52.4% |
| below_ema_20 | 51.9% |
| below_ema_200 | 53.3% |
| below_ema_200_break_recent_5d | 5.1% |
| below_ema_20_break_recent_5d | 15.5% |
| below_ema_21 | 52.0% |
| below_ema_21_break_recent_5d | 14.7% |
| below_ema_50 | 52.5% |
| below_ema_50_break_recent_5d | 7.3% |
| below_ema_9 | 52.0% |
| below_ema_9_break_recent_5d | 36.4% |
| below_prev_high | 66.7% |
| below_prev_low | 36.0% |
| below_prev_low_clearance_atr_05 | 16.6% |
| below_s1 | 34.3% |
| below_s2 | 18.5% |
| below_sma_20 | 51.9% |
| below_sma_200 | 53.5% |
| below_sma_21 | 51.6% |
| below_sma_50 | 51.8% |
| below_sma_9 | 50.8% |
| below_vwap | 49.9% |
| blowoff_recent_3d | 0.3% |
| break_52w_high | 0.0% |
| break_52w_high_clearance_atr_05 | 0.0% |
| break_52w_high_confirmed_today | 0.1% |
| break_52w_low | 0.4% |
| bullish_engulfing | 4.2% |
| bullish_pin_bar | 3.7% |
| capitulation_recent_3d | 0.6% |
| ceo_buy | 0.8% |
| cfo_buy | 0.5% |
| chandelier_long_bullish | 64.2% |
| chandelier_long_flip_dn | 4.9% |
| chandelier_short_bearish | 64.5% |
| chandelier_short_flip_up | 4.0% |
| classification_change_from_tech | 57.1% |
| classification_change_to_defensive | 42.9% |
| close_above_open | 47.0% |
| close_below_open | 53.0% |
| close_in_bottom_40pct_of_range | 44.5% |
| close_in_top_40pct_of_range | 42.2% |
| cluster_buy | 0.5% |
| cmf_cross_dn | 4.1% |
| cmf_cross_up | 4.0% |
| cmf_negative | 44.5% |
| cmf_positive | 55.4% |
| concentrated_sell | 6.3% |
| cpr_narrow | 88.2% |
| cpr_narrow_tight | 26.2% |
| cup_handle_detected | 14.7% |
| cup_handle_neckline_break_retest_long | 6.1% |
| dc10_breakout_dn | 4.6% |
| dc10_breakout_dn_1pct | 6.9% |
| dc10_breakout_up | 1.9% |
| dc10_breakout_up_1pct | 3.9% |
| dc10_new_high | 5.2% |
| dc10_strong_breakout_dn | 1.9% |
| dc10_strong_breakout_up | 0.7% |
| dc20_breakout_dn | 2.9% |
| dc20_breakout_up | 1.2% |
| dc20_new_high | 4.0% |
| dc20_resistance_break_retest_strong | 20.7% |
| dc20_support_break_retest_strong | 21.6% |
| defensive_leadership | 54.9% |
| director_only_buy | 3.5% |
| doji | 3.1% |
| double_bottom_detected | 12.9% |
| double_top_detected | 15.8% |
| dpi_elevated | 48.3% |
| drying_volume_on_down_turn | 35.0% |
| drying_volume_on_up_turn | 31.8% |
| ema_20_50_bearish | 51.5% |
| ema_20_50_bullish | 48.5% |
| ema_20_50_death_cross | 0.5% |
| ema_20_50_golden_cross | 0.3% |
| ema_50_200_bearish | 52.3% |
| ema_50_200_bullish | 47.7% |
| ema_50_200_death_cross | 0.4% |
| ema_50_200_golden_cross | 0.2% |
| ema_9_21_bearish | 50.9% |
| ema_9_21_bullish | 49.1% |
| ema_9_21_death_cross | 1.3% |
| ema_9_21_golden_cross | 0.9% |
| evening_star | 8.6% |
| flag_bear_break_retest_short | 0.8% |
| flag_bear_broke | 0.9% |
| flag_bear_detected | 0.0% |
| flag_bull_break_retest_long | 2.3% |
| flag_bull_broke | 2.5% |
| flag_bull_detected | 0.4% |
| force_index_cross_dn | 12.6% |
| force_index_cross_up | 10.7% |
| force_index_positive | 47.1% |
| gap_dn_1_5pct | 8.3% |
| gap_dn_2pct | 5.1% |
| gap_up_1_5pct | 7.9% |
| gap_up_2pct | 4.6% |
| hammer | 3.5% |
| head_shoulders_bottom_detected | 4.4% |
| head_shoulders_top_detected | 4.6% |
| house_cluster_buy | 4.3% |
| house_cluster_sell | 4.9% |
| htf_aligned_bear | 40.6% |
| htf_aligned_bull | 35.8% |
| htf_disagreement | 1.9% |
| hull_bearish | 51.5% |
| hull_bullish | 48.5% |
| hull_flip_dn | 13.1% |
| hull_flip_up | 10.9% |
| ichi_above_cloud | 42.4% |
| ichi_above_cloud_break_recent_5d | 3.6% |
| ichi_below_cloud | 46.1% |
| ichi_below_cloud_break_recent_5d | 5.2% |
| ichi_cloud_thick | 86.2% |
| ichi_tk_bearish | 50.3% |
| ichi_tk_bullish | 47.8% |
| ichi_tk_cross_dn | 1.1% |
| ichi_tk_cross_up | 1.1% |
| ichi_weekly_above_cloud | 38.3% |
| ichi_weekly_below_cloud | 33.7% |
| ichi_weekly_in_cloud | 28.0% |
| in_reversal_window | 2.1% |
| inside_bar | 8.1% |
| inside_cpr | 1.0% |
| inside_kc | 94.1% |
| insider_cluster_active | 20.5% |
| institutional_buy | 89.7% |
| institutional_negative | 4.4% |
| institutional_persistence_growing | 43.5% |
| institutional_persistence_strong | 59.6% |
| institutional_strong_buy | 80.0% |
| inverted_cup_handle_detected | 10.4% |
| is_friday | 20.1% |
| is_halloween_period | 50.3% |
| is_halloween_period_first_day | 0.2% |
| is_january | 8.2% |
| is_january_extended | 11.6% |
| is_monday | 18.0% |
| is_pre_holiday | 3.9% |
| is_summer_period | 49.7% |
| is_totm_window | 33.4% |
| is_totm_window_first_day | 9.2% |
| is_week_open | 20.4% |
| kc_touch_lower | 4.6% |
| kc_touch_upper | 4.2% |
| large_dollar_buy | 0.9% |
| macd_12_26_9_bearish | 50.6% |
| macd_12_26_9_bullish | 49.4% |
| macd_12_26_9_crossover_dn | 5.8% |
| macd_12_26_9_crossover_up | 4.6% |
| macd_8_21_5_bearish | 53.0% |
| macd_8_21_5_bullish | 47.0% |
| macd_8_21_5_crossover_dn | 53.0% |
| macd_8_21_5_crossover_up | 47.0% |
| marubozu_bear | 1.3% |
| marubozu_bull | 1.5% |
| mfi_broad_overbought | 11.2% |
| mfi_broad_oversold | 10.8% |
| mfi_overbought | 2.3% |
| mfi_oversold | 2.0% |
| monthly_above_sma_12 | 46.6% |
| monthly_above_sma_6 | 46.9% |
| monthly_bias_bear | 46.4% |
| monthly_bias_bull | 39.9% |
| monthly_momentum_pos | 48.0% |
| morning_star | 5.6% |
| near_52w_high | 4.8% |
| near_52w_high_95pct | 17.6% |
| near_52w_high_retest_long | 0.3% |
| near_52w_low | 1.4% |
| near_52w_low_105pct | 8.0% |
| near_52w_low_retest_short | 0.4% |
| near_avwap_20high_atr_05x | 41.2% |
| near_avwap_20high_atr_10x | 74.9% |
| near_avwap_20high_atr_15x | 91.4% |
| near_avwap_20high_atr_20x | 97.5% |
| near_avwap_20low_atr_05x | 36.5% |
| near_avwap_20low_atr_10x | 70.4% |
| near_avwap_20low_atr_15x | 87.3% |
| near_avwap_20low_atr_20x | 94.6% |
| near_avwap_252low_atr_05x | 14.7% |
| near_avwap_252low_atr_10x | 31.3% |
| near_avwap_252low_atr_15x | 41.3% |
| near_avwap_252low_atr_20x | 48.3% |
| near_avwap_50low_atr_05x | 25.2% |
| near_avwap_50low_atr_10x | 50.5% |
| near_avwap_50low_atr_15x | 64.6% |
| near_avwap_50low_atr_20x | 73.6% |
| near_cam_r3 | 8.1% |
| near_cam_s3 | 10.6% |
| near_cam_s4 | 11.5% |
| near_fib_236 | 7.2% |
| near_fib_382 | 4.3% |
| near_fib_500 | 3.6% |
| near_fib_618 | 3.8% |
| near_fib_786 | 6.0% |
| near_pivot | 7.3% |
| near_prev_close | 8.2% |
| near_prev_high | 7.9% |
| near_prev_low | 11.2% |
| near_r1 | 8.8% |
| near_r1_wide | 42.1% |
| near_r2 | 6.8% |
| near_r2_wide | 30.5% |
| near_s1 | 11.9% |
| near_s1_wide | 42.8% |
| near_s2 | 8.4% |
| near_s2_wide | 34.7% |
| near_s3 | 4.1% |
| near_wood_r1 | 7.1% |
| near_wood_s1 | 9.0% |
| news_uses_polygon_score | 22.9% |
| obv_bearish | 51.2% |
| obv_bullish | 48.8% |
| obv_diverge_bull | 12.6% |
| obv_falling | 51.3% |
| obv_rising | 48.7% |
| outside_bar | 9.1% |
| pead_negative_surprise | 17.3% |
| pead_positive_surprise | 22.4% |
| pin_bar | 7.3% |
| po3_accumulation_active | 43.3% |
| po3_bearish | 7.5% |
| po3_bullish | 6.8% |
| po3_manipulation_sweep_down | 13.5% |
| po3_manipulation_sweep_up | 9.5% |
| po3_mmbm_setup | 1.1% |
| po3_mmsm_setup | 2.3% |
| po3_sweep_above_prior_high | 51.4% |
| po3_sweep_below_prior_low | 54.9% |
| ppo_bullish | 47.1% |
| ppo_crossover_dn | 6.5% |
| ppo_crossover_up | 4.3% |
| pre_fomc_d0 | 2.2% |
| pre_fomc_d1 | 2.2% |
| pre_fomc_window | 4.4% |
| price_above_dema | 46.7% |
| price_above_ema_20 | 48.1% |
| price_above_ema_200 | 46.7% |
| price_above_ema_200_break_recent_5d | 3.7% |
| price_above_ema_20_break_recent_5d | 12.4% |
| price_above_ema_21 | 48.0% |
| price_above_ema_21_break_recent_5d | 11.8% |
| price_above_ema_50 | 47.5% |
| price_above_ema_50_break_recent_5d | 5.6% |
| price_above_ema_9 | 48.0% |
| price_above_ema_9_break_recent_5d | 31.8% |
| price_above_hull | 47.5% |
| price_above_sma_200 | 46.5% |
| price_above_sma_21 | 48.4% |
| price_above_sma_50 | 48.2% |
| price_above_tema | 46.9% |
| price_below_dema | 53.3% |
| price_below_hull | 52.5% |
| price_below_tema | 53.1% |
| psar_bullish | 46.7% |
| psar_flip_dn | 12.3% |
| psar_flip_up | 8.6% |
| r1_break_retest_long | 57.6% |
| recent_blowoff_at_r3 | 0.1% |
| recent_capitulation_at_s3 | 0.1% |
| resistance_break_retest | 26.2% |
| risk_off_regime_bond_signal | 21.6% |
| risk_off_regime_bond_signal_strong | 7.6% |
| risk_off_regime_gold_signal | 39.0% |
| risk_on_regime_bond_signal | 43.5% |
| risk_on_regime_bond_signal_strong | 19.2% |
| roc_positive | 48.1% |
| roc_turning_dn | 7.6% |
| roc_turning_up | 5.4% |
| rsi_14_bullish | 48.0% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 1.8% |
| rsi_14_cross_dn_overbought_recent_3d | 13.1% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.8% |
| rsi_14_cross_up_oversold_recent_3d | 11.4% |
| rsi_14_extreme_os | 0.1% |
| rsi_14_overbought | 2.7% |
| rsi_14_oversold | 1.7% |
| rsi_14_rising | 46.8% |
| rsi_21_bullish | 47.8% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_21_cross_dn_overbought_recent_3d | 5.4% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 4.7% |
| rsi_21_extreme_os | 0.0% |
| rsi_21_overbought | 1.4% |
| rsi_21_oversold | 0.9% |
| rsi_21_rising | 46.8% |
| rsi_2_bullish | 47.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 39.0% |
| rsi_2_cross_dn_overbought_recent_3d | 47.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 32.4% |
| rsi_2_cross_up_oversold_recent_3d | 39.9% |
| rsi_2_extreme_ob | 22.8% |
| rsi_2_extreme_os | 28.4% |
| rsi_2_overbought | 35.3% |
| rsi_2_oversold | 41.2% |
| rsi_2_rising | 46.8% |
| rsi_9_bullish | 48.1% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 6.5% |
| rsi_9_cross_dn_overbought_recent_3d | 23.4% |
| rsi_9_cross_up_extreme_os_recent_3d | 4.6% |
| rsi_9_cross_up_oversold_recent_3d | 20.4% |
| rsi_9_extreme_ob | 0.2% |
| rsi_9_extreme_os | 0.3% |
| rsi_9_overbought | 3.0% |
| rsi_9_oversold | 3.0% |
| rsi_9_rising | 46.8% |
| s1_break_retest_short | 56.4% |
| sc_13d_filed_within_30d | 2.1% |
| sc_13g_filed_within_30d | 3.2% |
| sector_outperforming_spy | 37.6% |
| sector_underperforming_spy | 62.4% |
| shooting_star | 2.9% |
| sma_20_50_bullish | 49.7% |
| sma_20_50_golden_cross | 1.0% |
| sma_50_200_bullish | 48.4% |
| sma_50_200_golden_cross | 0.2% |
| sma_9_21_bullish | 50.1% |
| sma_9_21_golden_cross | 0.9% |
| smc_bos_bearish | 14.4% |
| smc_bos_bullish | 13.9% |
| smc_bos_retest_long | 3.8% |
| smc_bos_retest_short | 3.5% |
| smc_breaker_block_bearish | 17.1% |
| smc_breaker_block_bullish | 21.6% |
| smc_choch_bearish | 5.6% |
| smc_choch_bullish | 4.3% |
| smc_equal_highs_swept | 3.8% |
| smc_equal_lows_swept | 4.1% |
| smc_fvg_bearish_active | 33.4% |
| smc_fvg_bullish_active | 35.0% |
| smc_fvg_retest_long_zone | 7.3% |
| smc_fvg_retest_short_zone | 7.9% |
| smc_in_discount_zone | 58.5% |
| smc_in_premium_zone | 55.1% |
| smc_inverse_fvg_bearish | 77.2% |
| smc_inverse_fvg_bullish | 75.4% |
| smc_liquidity_swept_dn | 1.4% |
| smc_liquidity_swept_up | 1.3% |
| smc_mitigation_block_long | 0.9% |
| smc_mitigation_block_short | 1.4% |
| smc_ob_bearish_active | 36.7% |
| smc_ob_bullish_active | 31.8% |
| smc_ote_long_zone | 6.8% |
| smc_ote_short_zone | 6.3% |
| squeeze_fire_dn | 4.4% |
| squeeze_fire_up | 3.3% |
| squeeze_in | 25.1% |
| squeeze_positive | 48.8% |
| stoch_bearish_cross | 17.1% |
| stoch_broad_overbought | 22.9% |
| stoch_broad_oversold | 21.0% |
| stoch_bullish_cross | 12.5% |
| stoch_overbought | 14.5% |
| stoch_oversold | 13.2% |
| stochrsi_cross_dn | 32.4% |
| stochrsi_cross_up | 32.1% |
| stochrsi_overbought | 18.0% |
| stochrsi_oversold | 22.5% |
| supertrend_bearish | 2.0% |
| supertrend_bullish | 98.0% |
| supertrend_flip_dn | 1.9% |
| supertrend_flip_recent_long_5d | 2.5% |
| supertrend_flip_recent_short_5d | 2.1% |
| supertrend_flip_up | 0.4% |
| support_break_retest | 26.9% |
| tema_above_dema | 50.5% |
| tema_cross_dn | 1.8% |
| tema_cross_up | 1.7% |
| three_black_crows | 6.4% |
| three_white_soldiers | 5.3% |
| triangle_apex_break_retest_long | 16.9% |
| triangle_ascending_detected | 7.4% |
| triangle_descending_detected | 6.3% |
| uo_overbought | 0.4% |
| uo_oversold | 0.2% |
| usd_strengthening | 23.7% |
| usd_weakening | 11.5% |
| vix_band_high | 43.2% |
| vix_band_low | 33.7% |
| vix_band_mid | 23.2% |
| vix_term_backwardation | 9.2% |
| vix_term_contango | 90.8% |
| vol_above_avg | 33.2% |
| vol_below_avg | 66.8% |
| vol_spike_12x | 19.5% |
| vol_spike_15x | 10.1% |
| vol_spike_17x | 7.0% |
| vol_spike_2x | 4.1% |
| vol_spike_2x_on_down_day_recent_3d | 2.3% |
| vol_spike_2x_on_up_day_recent_3d | 2.1% |
| vol_spike_3x | 1.5% |
| vp_above_value_area | 25.0% |
| vp_below_value_area | 23.1% |
| vp_close_above_poc | 51.2% |
| vp_close_below_poc | 48.8% |
| vp_in_value_area | 51.9% |
| week_open_gap_down_15pct | 1.5% |
| week_open_gap_up_15pct | 1.6% |
| weekly_above_ema_10 | 47.9% |
| weekly_above_ema_20 | 46.6% |
| weekly_bias_bear | 49.3% |
| weekly_bias_bull | 43.7% |
| weekly_momentum_pos | 48.4% |
| williams_r_overbought | 7.7% |
| williams_r_oversold | 10.2% |
| williams_r_rising | 46.9% |
| within_pead_window | 38.7% |
| within_post_deletion_window | 7.2% |
| within_post_inclusion_window | 1.8% |
| within_pre_rebalance_window | 1.3% |
| xs_avoid_high_ivol | 70.4% |
| xs_avoid_high_max | 73.0% |
| xs_high_beta_decile | 27.4% |
| xs_low_beta_bottom_quintile | 27.4% |
| xs_low_beta_decile | 16.5% |
| xs_low_beta_decile_entry_recent_5d | 0.3% |
| xs_low_beta_top_quintile | 16.5% |
| xs_momentum_bottom_decile | 14.1% |
| xs_momentum_bottom_quintile | 25.0% |
| xs_momentum_top_decile | 12.4% |
| xs_momentum_top_quintile | 20.7% |
| xs_quality_bottom_quintile | 21.3% |
| xs_quality_top_quintile | 21.6% |
| xs_quality_top_tercile | 41.4% |
| year_high_break_retest_long | 7.2% |
| year_low_break_retest_short | 5.5% |
| yoy_surprise_high | 51.8% |
| yoy_surprise_negative | 38.2% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.2% |
| committed_growth_holders | 91.2% |
| corp_donations_1y | 7.5% |
| corp_donations_count_1y | 7.5% |
| corp_donations_unique_pacs | 7.5% |
| cot_rut_commercials_pctile_3y | 53.1% |
| cot_rut_mmoney_pctile_3y | 53.1% |
| cup_handle_depth_pct | 21.7% |
| days_since_classification_change | 0.2% |
| days_since_deletion | 8.5% |
| days_since_inclusion | 13.9% |
| days_to_next_holiday | 64.0% |
| days_to_rebalance | 11.2% |
| dpi_30d_avg | 95.3% |
| dpi_recent | 95.3% |
| earnings_announcement_return | 90.6% |
| earnings_eps_yoy_growth | 94.3% |
| flag_bull_pole_move_pct | 0.4% |
| gov_contracts_4q_sum | 39.8% |
| gov_contracts_last_qtr_amount | 39.8% |
| gov_contracts_qoq_growth | 39.8% |
| head_shoulders_magnitude_pct | 8.7% |
| insider_director_buyers_30d | 5.0% |
| insider_officer_buyers_30d | 5.0% |
| insider_total_shares_bought_30d | 5.0% |
| insider_unique_buyers_30d | 5.0% |
| inverted_cup_handle_height_pct | 17.1% |
| lobbying_amount_1y | 70.2% |
| lobbying_amount_q | 70.2% |
| lobbying_amount_yoy | 70.2% |
| monthly_momentum_6m | 97.0% |
| otc_short_ratio_recent | 95.3% |
| otc_volume_recent | 95.3% |
| pair_half_life | 91.8% |
| pair_max_abs_zscore | 91.8% |
| pair_zscore_signed | 91.8% |
| pct_from_avwap_20high | 96.0% |
| pct_from_avwap_20low | 94.3% |
| pct_from_avwap_252low | 96.2% |
| pct_from_avwap_50low | 95.9% |
| persistent_holders_4q | 91.2% |
| persistent_holders_8q | 91.2% |
| sc_13g_latest_percent_owned | 1.7% |
| search_volume_index_recent | 77.1% |
| search_volume_observations | 77.1% |
| search_volume_zscore_30d | 77.1% |
| sector_etf_return_20d | 2.1% |
| spy_return_20d | 2.1% |
| total_active_holders | 91.2% |
| triangle_breakdown_pct | 6.3% |
| triangle_breakout_pct | 7.4% |
| xs_quality_decile | 63.4% |
| xs_quality_gross_profitability | 63.4% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.994), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.997), `double_top_peak` (0.998), `entry_stop_long` (0.997), `entry_stop_short` (0.999), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.994), `fib_ext_162` (0.991), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.997), `ichi_kijun` (1.0), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.991), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.982), `monthly_sma_6` (0.995), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.998), `s2` (0.998), `s3` (0.997), `supertrend_value` (0.996), `swing_high` (0.996), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.996), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.966), `year_low` (0.969)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P3 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     1 = 1
offline gradings   0 level-combinations x 24 exits = 0 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  0 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 0 + 0 = 1 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 655 census axes join it only when REGISTERED at the T3 band review.
