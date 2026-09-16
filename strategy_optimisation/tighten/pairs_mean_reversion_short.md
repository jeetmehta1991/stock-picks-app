# Table A - pairs_mean_reversion_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 0065a0651 at 2026-09-16 19:05:58 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** pairs | **status:** NOT-STARTED | **R5 fires:** 5698 | **surviving fires (T1):** 4461 (survives_pct 0.7829)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Table A - parameter inventory (the SS6 canonical shape, pre-R1)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close). The
R1 SPECS entry absorbs and supersedes this pre-R1 inventory - producer
knob rows below are placeholders it must fill.

| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|
| P1 | PRODUCER | pair_counterparty - emitted by backtest/signals/pairs_trading.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P2 | PRODUCER | ppo_signal - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; knobs INVENTORY-PENDING-R1 (SPECS) | INVENTORY-PENDING-R1 |
| P3 | STRATEGY | pair_count_active `> 0` [EXISTING-THRESHOLD] | `> 0` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4 | STRATEGY | pair_half_life `>= 5` [EXISTING-THRESHOLD] | `>= 5` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5 | STRATEGY | pair_zscore_signed `> 2` [EXISTING-THRESHOLD] | `> 2` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| pair_count_active | backtest/signals/pairs_trading.py +1 | `> 0` | 100.0% | 4 -> 3685 (83%); 6 -> 2991 (67%); 9 -> 1992 (45%); 14 -> 927 (21%) | looser (lower the threshold): RESIM - band from the SPECS entry (to be built) |
| pair_half_life | backtest/signals/pairs_trading.py +1 | `>= 5` | 100.0% | 7.12 -> 3569 (80%); 8.81 -> 2686 (60%); 10.27 -> 1788 (40%); 11.99 -> 899 (20%) | looser (lower the threshold): RESIM - band from the SPECS entry (to be built) |
| pair_zscore_signed | backtest/signals/pairs_trading.py +1 | `> 2` | 100.0% | 2.184 -> 3569 (80%); 2.3779 -> 2677 (60%); 2.6388 -> 1785 (40%); 3.0148 -> 893 (20%) | looser (lower the threshold): RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 17.66, 22.05, 26.85, 33.72 | 17.66: 3570 (80%); 22.05: 2679 (60%); 26.85: 1786 (40%); 33.72: 893 (20%) | 17.66: 895 (20%); 22.05: 1785 (40%); 26.85: 2677 (60%); 33.72: 3569 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 11.19, 14.03, 17.05, 21.53 | 11.19: 3570 (80%); 14.03: 2678 (60%); 17.05: 1786 (40%); 21.53: 896 (20%) | 11.19: 893 (20%); 14.03: 1790 (40%); 17.05: 2680 (60%); 21.53: 3570 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 24.02, 30.26, 34.72, 39.79 | 24.02: 3570 (80%); 30.26: 2678 (60%); 34.72: 1786 (40%); 39.79: 893 (20%) | 24.02: 895 (20%); 30.26: 1790 (40%); 34.72: 2679 (60%); 39.79: 3570 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 0.907, 3.4137, 7.1025, 14.4254 | 0.907: 3570 (80%); 3.4137: 2677 (60%); 7.1025: 1785 (40%); 14.4254: 893 (20%) | 0.907: 893 (20%); 3.4137: 1785 (40%); 7.1025: 2677 (60%); 14.4254: 3569 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.3888, 2.3588, 3.896, 6.5821 | 1.3888: 3569 (80%); 2.3588: 2677 (60%); 3.896: 1785 (40%); 6.5821: 893 (20%) | 1.3888: 893 (20%); 2.3588: 1785 (40%); 3.896: 2677 (60%); 6.5821: 3569 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.3888, 2.3588, 3.896, 6.5821 | 1.3888: 3569 (80%); 2.3588: 2677 (60%); 3.896: 1785 (40%); 6.5821: 893 (20%) | 1.3888: 893 (20%); 2.3588: 1785 (40%); 3.896: 2677 (60%); 6.5821: 3569 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.927, 2.308, 2.724, 3.346 | 1.927: 3570 (80%); 2.308: 2679 (60%); 2.724: 1785 (40%); 3.346: 894 (20%) | 1.927: 893 (20%); 2.308: 1785 (40%); 2.724: 2677 (60%); 3.346: 3569 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0646, 0.0947, 0.1303, 0.1797 | 0.0646: 3571 (80%); 0.0947: 2678 (60%); 0.1303: 1787 (40%); 0.1797: 894 (20%) | 0.0646: 893 (20%); 0.0947: 1785 (40%); 0.1303: 2677 (60%); 0.1797: 3569 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.4437, 0.7152, 0.8046, 0.8771 | 0.4437: 3569 (80%); 0.7152: 2677 (60%); 0.8046: 1785 (40%); 0.8771: 893 (20%) | 0.4437: 894 (20%); 0.7152: 1786 (40%); 0.8046: 2679 (60%); 0.8771: 3570 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0667, 0.0935, 0.1206, 0.1595 | 0.0667: 3573 (80%); 0.0935: 2678 (60%); 0.1206: 1785 (40%); 0.1595: 893 (20%) | 0.0667: 893 (20%); 0.0935: 1788 (40%); 0.1206: 2680 (60%); 0.1595: 3569 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.5749, 0.9132, 1.0359, 1.1529 | 0.5749: 3569 (80%); 0.9132: 2677 (60%); 1.0359: 1785 (40%); 1.1529: 893 (20%) | 0.5749: 893 (20%); 0.9132: 1785 (40%); 1.0359: 2679 (60%); 1.1529: 3570 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.089, 0.1247, 0.1607, 0.2127 | 0.089: 3569 (80%); 0.1247: 2677 (60%); 0.1607: 1788 (40%); 0.2127: 893 (20%) | 0.089: 893 (20%); 0.1247: 1789 (40%); 0.1607: 2677 (60%); 0.2127: 3569 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.5561, 0.8099, 0.9019, 0.9897 | 0.5561: 3569 (80%); 0.8099: 2677 (60%); 0.9019: 1785 (40%); 0.9897: 893 (20%) | 0.5561: 893 (20%); 0.8099: 1785 (40%); 0.9019: 2679 (60%); 0.9897: 3570 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0551, -0.03, -0.0087, 0.0157 | -0.0551: 3570 (80%); -0.03: 2677 (60%); -0.0087: 1788 (40%); 0.0157: 898 (20%) | -0.0551: 899 (20%); -0.03: 1787 (40%); -0.0087: 2679 (60%); 0.0157: 3580 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1368, 0.1627, 0.1923, 0.2514 | 0.1368: 3574 (80%); 0.1627: 2681 (60%); 0.1923: 1791 (40%); 0.2514: 892 (20%) | 0.1368: 887 (20%); 0.1627: 1780 (40%); 0.1923: 2670 (60%); 0.2514: 3569 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 4461 (100%) | 0: 4325 (97%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0201, 0.0637, 0.1321, 0.2113 | -0.0201: 3570 (80%); 0.0637: 2677 (60%); 0.1321: 1786 (40%); 0.2113: 893 (20%) | -0.0201: 894 (20%); 0.0637: 1787 (40%); 0.1321: 2677 (60%); 0.2113: 3569 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 4461 (100%); 1: 1813 (41%) | 0: 2648 (59%); 1: 3689 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2423, -0.2039, -0.1626, -0.1299 | -0.2423: 3569 (80%); -0.2039: 2691 (60%); -0.1626: 1789 (40%); -0.1299: 898 (20%) | -0.2423: 927 (21%); -0.2039: 1787 (40%); -0.1626: 2687 (60%); -0.1299: 3642 (82%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.5705, 0.6667, 0.7692 | 0.3013: 3583 (80%); 0.5705: 2704 (61%); 0.6667: 1961 (44%); 0.7692: 953 (21%) | 0.3013: 926 (21%); 0.5705: 1820 (41%); 0.6667: 2768 (62%); 0.7692: 3594 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2885, 0.4359, 0.6538, 0.891 | 0.2885: 3573 (80%); 0.4359: 2690 (60%); 0.6538: 1802 (40%); 0.891: 928 (21%) | 0.2885: 901 (20%); 0.4359: 1848 (41%); 0.6538: 2680 (60%); 0.891: 3619 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1195, -0.0268, 0.0357, 0.1461 | -0.1195: 3586 (80%); -0.0268: 2689 (60%); 0.0357: 1798 (40%); 0.1461: 900 (20%) | -0.1195: 896 (20%); -0.0268: 1785 (40%); 0.0357: 2687 (60%); 0.1461: 3572 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2372, 0.3974, 0.5192, 0.7244 | 0.2372: 3590 (80%); 0.3974: 2695 (60%); 0.5192: 1818 (41%); 0.7244: 905 (20%) | 0.2372: 900 (20%); 0.3974: 1821 (41%); 0.5192: 2704 (61%); 0.7244: 3624 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.141, 0.2692, 0.4423, 0.6538 | 0.141: 3580 (80%); 0.2692: 2684 (60%); 0.4423: 1796 (40%); 0.6538: 913 (20%) | 0.141: 894 (20%); 0.2692: 1824 (41%); 0.4423: 2677 (60%); 0.6538: 3570 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4904, -0.3214, -0.0978, 0.0988 | -0.4904: 3578 (80%); -0.3214: 2678 (60%); -0.0978: 1853 (42%); 0.0988: 926 (21%) | -0.4904: 896 (20%); -0.3214: 1810 (41%); -0.0978: 2688 (60%); 0.0988: 3586 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5449, 0.8013, 0.9551 | 0.3397: 3583 (80%); 0.5449: 2683 (60%); 0.8013: 1838 (41%); 0.9551: 1011 (23%) | 0.3397: 957 (21%); 0.5449: 1824 (41%); 0.8013: 2696 (60%); 0.9551: 3569 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.3333, 0.5897, 0.8526 | 0.109: 3614 (81%); 0.3333: 2714 (61%); 0.5897: 1812 (41%); 0.8526: 900 (20%) | 0.109: 899 (20%); 0.3333: 1794 (40%); 0.5897: 2726 (61%); 0.8526: 3623 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0646, -0.0565, -0.0356, 0 | -0.0646: 3628 (81%); -0.0565: 2732 (61%); -0.0356: 1806 (40%); 0: 1440 (32%) | -0.0646: 904 (20%); -0.0565: 1815 (41%); -0.0356: 2694 (60%); 0: 4380 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4038, 0.6667, 0.8846, 1 | 0.4038: 3576 (80%); 0.6667: 2700 (61%); 0.8846: 1801 (40%); 1: 1149 (26%) | 0.4038: 895 (20%); 0.6667: 1797 (40%); 0.8846: 2709 (61%); 1: 4461 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1603, 0.2885, 0.5833, 0.859 | 0.1603: 3599 (81%); 0.2885: 2688 (60%); 0.5833: 1792 (40%); 0.859: 938 (21%) | 0.1603: 906 (20%); 0.2885: 1793 (40%); 0.5833: 2742 (61%); 0.859: 3590 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0198, 0.0281, 0.0812, 0.1869 | -0.0198: 3596 (81%); 0.0281: 2731 (61%); 0.0812: 1799 (40%); 0.1869: 909 (20%) | -0.0198: 893 (20%); 0.0281: 1786 (40%); 0.0812: 2678 (60%); 0.1869: 3645 (82%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3974, 0.7586, 0.9167, 0.9679 | 0.3974: 3582 (80%); 0.7586: 2705 (61%); 0.9167: 1826 (41%); 0.9679: 1022 (23%) | 0.3974: 895 (20%); 0.7586: 1802 (40%); 0.9167: 2739 (61%); 0.9679: 3633 (81%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1169, 0.3739, 0.6026, 0.8231 | 0.1169: 3612 (81%); 0.3739: 2684 (60%); 0.6026: 1788 (40%); 0.8231: 897 (20%) | 0.1169: 920 (21%); 0.3739: 1815 (41%); 0.6026: 2711 (61%); 0.8231: 3573 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0141, 0.0917, 0.1603 | -0.0812: 4021 (90%); -0.0141: 2712 (61%); 0.0917: 1805 (40%); 0.1603: 896 (20%) | -0.0812: 903 (20%); -0.0141: 1799 (40%); 0.0917: 2693 (60%); 0.1603: 3586 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1885, -0.0345, 0.0356, 0.0941 | -0.1885: 3580 (80%); -0.0345: 2691 (60%); 0.0356: 1805 (40%); 0.0941: 896 (20%) | -0.1885: 918 (21%); -0.0345: 1787 (40%); 0.0356: 2677 (60%); 0.0941: 3598 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2564, 0.5256, 0.7308, 0.8846 | 0.2564: 3587 (80%); 0.5256: 2735 (61%); 0.7308: 1795 (40%); 0.8846: 911 (20%) | 0.2564: 907 (20%); 0.5256: 1793 (40%); 0.7308: 2684 (60%); 0.8846: 3623 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.4423, 0.6603, 0.8269 | 0.1795: 3581 (80%); 0.4423: 2708 (61%); 0.6603: 1801 (40%); 0.8269: 970 (22%) | 0.1795: 930 (21%); 0.4423: 1827 (41%); 0.6603: 2679 (60%); 0.8269: 3602 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0792, 0.1867, 0.3567, 0.7533 | 0.0792: 3574 (80%); 0.1867: 2682 (60%); 0.3567: 1786 (40%); 0.7533: 893 (20%) | 0.0792: 894 (20%); 0.1867: 1789 (40%); 0.3567: 2680 (60%); 0.7533: 3570 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.9% | 15, 55, 83, 117 | 15: 3566 (80%); 55: 2665 (60%); 83: 1776 (40%); 117: 888 (20%) | 15: 885 (20%); 55: 1772 (40%); 83: 2696 (60%); 117: 3537 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.8144, 2.2978, 2.871, 3.6057 | 1.8144: 3555 (80%); 2.2978: 2666 (60%); 2.871: 1778 (40%); 3.6057: 889 (20%) | 1.8144: 889 (20%); 2.2978: 1778 (40%); 2.871: 2666 (60%); 3.6057: 3555 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 19, 29, 40 | 8: 3581 (80%); 19: 2736 (61%); 29: 1868 (42%); 40: 971 (22%) | 8: 1004 (23%); 19: 1812 (41%); 29: 2725 (61%); 40: 3661 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3, 4 | 1: 3614 (81%); 2: 2803 (63%); 3: 1969 (44%); 4: 952 (21%) | 1: 1658 (37%); 2: 2492 (56%); 3: 3509 (79%); 4: 4461 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0133, -0.0049, 0.007, 0.0208 | -0.0133: 3572 (80%); -0.0049: 2678 (60%); 0.007: 1788 (40%); 0.0208: 899 (20%) | -0.0133: 897 (20%); -0.0049: 1787 (40%); 0.007: 2682 (60%); 0.0208: 3577 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6818, 25.9524, 26.5909, 27.2 | 24.6818: 3577 (80%); 25.9524: 2685 (60%); 26.5909: 1808 (41%); 27.2: 909 (20%) | 24.6818: 895 (20%); 25.9524: 1787 (40%); 26.5909: 2683 (60%); 27.2: 3569 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.943, -0.342, 0, 0.489 | -0.943: 3569 (80%); -0.342: 2679 (60%); 0: 1858 (42%); 0.489: 893 (20%) | -0.943: 894 (20%); -0.342: 1786 (40%); 0: 2702 (61%); 0.489: 3569 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.489, 0, 0.342, 0.943 | -0.489: 3569 (80%); 0: 2702 (61%); 0.342: 1786 (40%); 0.943: 894 (20%) | -0.489: 893 (20%); 0: 1858 (42%); 0.342: 2679 (60%); 0.943: 3569 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0461, -0.0125, 0.0148, 0.0566 | -0.0461: 3571 (80%); -0.0125: 2679 (60%); 0.0148: 1804 (40%); 0.0566: 894 (20%) | -0.0461: 906 (20%); -0.0125: 1788 (40%); 0.0148: 2684 (60%); 0.0566: 3572 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0713, 8.4606, 8.6733, 9.0086 | 8.0713: 3562 (80%); 8.4606: 2676 (60%); 8.6733: 1788 (40%); 9.0086: 894 (20%) | 8.0713: 899 (20%); 8.4606: 1785 (40%); 8.6733: 2673 (60%); 9.0086: 3567 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0, 1 | 0: 4439 (100%); 1: 1491 (33%) | 0: 2948 (66%); 1: 3918 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.5% | -1, 0 | -1: 4214 (94%); 0: 3524 (79%) | -1: 915 (21%); 0: 3630 (81%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0, 1 | 0: 4439 (100%); 1: 1567 (35%) | 0: 2872 (64%); 1: 3882 (87%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 5, 97, 277 | 2: 3823 (86%); 5: 2907 (65%); 97: 1785 (40%); 277: 905 (20%) | 2: 927 (21%); 5: 1829 (41%); 97: 2678 (60%); 277: 3569 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 85, 144 | 1: 3654 (82%); 4: 2772 (62%); 85: 1807 (41%); 144: 901 (20%) | 1: 1164 (26%); 4: 1866 (42%); 85: 2678 (60%); 144: 3576 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.1038, 0.2744, 0.7283, 1.6359 | -0.1038: 3569 (80%); 0.2744: 2678 (60%); 0.7283: 1785 (40%); 1.6359: 893 (20%) | -0.1038: 893 (20%); 0.2744: 1785 (40%); 0.7283: 2677 (60%); 1.6359: 3569 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.4191, 1.3605, 2.7554, 5.496 | 0.4191: 3569 (80%); 1.3605: 2677 (60%); 2.7554: 1785 (40%); 5.496: 893 (20%) | 0.4191: 893 (20%); 1.3605: 1785 (40%); 2.7554: 2677 (60%); 5.496: 3569 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | 0.2252, 0.9438, 1.9838, 4.2214 | 0.2252: 3569 (80%); 0.9438: 2677 (60%); 1.9838: 1785 (40%); 4.2214: 893 (20%) | 0.2252: 893 (20%); 0.9438: 1785 (40%); 1.9838: 2677 (60%); 4.2214: 3569 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.1313, 0.1537, 0.4942, 1.2482 | -0.1313: 3569 (80%); 0.1537: 2677 (60%); 0.4942: 1785 (40%); 1.2482: 893 (20%) | -0.1313: 893 (20%); 0.1537: 1785 (40%); 0.4942: 2677 (60%); 1.2482: 3569 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.4362, 1.6041, 3.3211, 6.5444 | 0.4362: 3569 (80%); 1.6041: 2677 (60%); 3.3211: 1785 (40%); 6.5444: 893 (20%) | 0.4362: 893 (20%); 1.6041: 1785 (40%); 3.3211: 2677 (60%); 6.5444: 3569 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.3926, 1.3195, 2.7487, 5.4556 | 0.3926: 3569 (80%); 1.3195: 2677 (60%); 2.7487: 1785 (40%); 5.4556: 893 (20%) | 0.3926: 893 (20%); 1.3195: 1785 (40%); 2.7487: 2677 (60%); 5.4556: 3569 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 50.86, 61.38, 68.99, 76.89 | 50.86: 3569 (80%); 61.38: 2678 (60%); 68.99: 1786 (40%); 76.89: 893 (20%) | 50.86: 893 (20%); 61.38: 1785 (40%); 68.99: 2678 (60%); 76.89: 3572 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.6% | 0.0093, 0.0232, 0.0466, 0.0838 | 0.0093: 3550 (80%); 0.0232: 2663 (60%); 0.0466: 1776 (40%); 0.0838: 887 (20%) | 0.0093: 891 (20%); 0.0232: 1778 (40%); 0.0466: 2665 (60%); 0.0838: 3554 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 10 | 0: 4461 (100%); 2: 2815 (63%); 4: 2044 (46%); 10: 988 (22%) | 0: 968 (22%); 2: 2091 (47%); 4: 2683 (60%); 10: 3572 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1091 | 0: 4461 (100%); 0.1091: 894 (20%) | 0: 3141 (70%); 0.1091: 3569 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.303, 0.5, 0.75 | 0: 4461 (100%); 0.303: 2677 (60%); 0.5: 2033 (46%); 0.75: 953 (21%) | 0: 1460 (33%); 0.303: 1785 (40%); 0.5: 2844 (64%); 0.75: 3599 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 8 | 0: 4461 (100%); 1: 3260 (73%); 3: 2017 (45%); 8: 927 (21%) | 0: 1201 (27%); 1: 1942 (44%); 3: 2785 (62%); 8: 3640 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 10 | 0: 4461 (100%); 2: 2815 (63%); 4: 2044 (46%); 10: 988 (22%) | 0: 968 (22%); 2: 2091 (47%); 4: 2683 (60%); 10: 3572 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 4461 (100%); 1: 3206 (72%); 3: 2034 (46%); 8: 906 (20%) | 0: 1255 (28%); 1: 1945 (44%); 3: 2780 (62%); 8: 3665 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.1217, 0.3095, 0.4542, 0.6667 | 0.1217: 3569 (80%); 0.3095: 2679 (60%); 0.4542: 1785 (40%); 0.6667: 951 (21%) | 0.1217: 893 (20%); 0.3095: 1785 (40%); 0.4542: 2677 (60%); 0.6667: 3608 (81%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3546, 0.7209 | 0: 4226 (95%); 0.3546: 1785 (40%); 0.7209: 893 (20%) | 0: 2001 (45%); 0.3546: 2677 (60%); 0.7209: 3569 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1526, 0.4167, 0.6857 | 0: 4258 (95%); 0.1526: 2677 (60%); 0.4167: 1792 (40%); 0.6857: 894 (20%) | 0: 1607 (36%); 0.1526: 1785 (40%); 0.4167: 2683 (60%); 0.6857: 3569 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1526, 0.4167, 0.6857 | 0: 4258 (95%); 0.1526: 2677 (60%); 0.4167: 1792 (40%); 0.6857: 894 (20%) | 0: 1607 (36%); 0.1526: 1785 (40%); 0.4167: 2683 (60%); 0.6857: 3569 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.15, 0, 0.1701 | -0.15: 3572 (80%); 0: 3221 (72%); 0.1701: 894 (20%) | -0.15: 893 (20%); 0: 3133 (70%); 0.1701: 3569 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6461, 0, 0.4899, 1.8347 | -0.6461: 3632 (81%); 0: 2708 (61%); 0.4899: 1785 (40%); 1.8347: 893 (20%) | -0.6461: 970 (22%); 0: 2343 (53%); 0.4899: 2680 (60%); 1.8347: 3569 (80%) | OFFLINE |
| pair_max_abs_zscore | backtest/signals/pairs_trading.py | 100.0% | 2.184, 2.3779, 2.6388, 3.0148 | 2.184: 3569 (80%); 2.3779: 2677 (60%); 2.6388: 1785 (40%); 3.0148: 893 (20%) | 2.184: 893 (20%); 2.3779: 1785 (40%); 2.6388: 2677 (60%); 3.0148: 3569 (80%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0006, 0.0401, 0.0727, 0.1111 | 0.0006: 3568 (80%); 0.0401: 2678 (60%); 0.0727: 1782 (40%); 0.1111: 892 (20%) | 0.0006: 893 (20%); 0.0401: 1783 (40%); 0.0727: 2679 (60%); 0.1111: 3569 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0165, 0.0634, 0.0976, 0.1471 | 0.0165: 3568 (80%); 0.0634: 2676 (60%); 0.0976: 1781 (40%); 0.1471: 892 (20%) | 0.0165: 893 (20%); 0.0634: 1785 (40%); 0.0976: 2680 (60%); 0.1471: 3569 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0076, 0.0205, 0.044, 0.0758 | -0.0076: 3570 (80%); 0.0205: 2676 (60%); 0.044: 1783 (40%); 0.0758: 894 (20%) | -0.0076: 891 (20%); 0.0205: 1785 (40%); 0.044: 2678 (60%); 0.0758: 3567 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 98.4% | 2.71, 5.9036, 8.3104, 11.93 | 2.71: 3511 (79%); 5.9036: 2633 (59%); 8.3104: 1755 (39%); 11.93: 879 (20%) | 2.71: 879 (20%); 5.9036: 1755 (39%); 8.3104: 2633 (59%); 11.93: 3511 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -6.602, 6.426, 21.494, 45.927 | -6.602: 3569 (80%); 6.426: 2677 (60%); 21.494: 1785 (40%); 45.927: 893 (20%) | -6.602: 893 (20%); 6.426: 1785 (40%); 21.494: 2677 (60%); 45.927: 3569 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0457, 0.0627, 0.0826, 0.1141 | 0.0457: 3573 (80%); 0.0627: 2677 (60%); 0.0826: 1786 (40%); 0.1141: 895 (20%) | 0.0457: 895 (20%); 0.0627: 1790 (40%); 0.0826: 2678 (60%); 0.1141: 3570 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1241, 0.2561, 0.407, 0.6111 | 0.1241: 3570 (80%); 0.2561: 2677 (60%); 0.407: 1785 (40%); 0.6111: 893 (20%) | 0.1241: 893 (20%); 0.2561: 1786 (40%); 0.407: 2677 (60%); 0.6111: 3569 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 0.6193, 1.5628, 2.2772, 3.3269 | 0.6193: 3569 (80%); 1.5628: 2677 (60%); 2.2772: 1785 (40%); 3.3269: 893 (20%) | 0.6193: 893 (20%); 1.5628: 1785 (40%); 2.2772: 2677 (60%); 3.3269: 3569 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.1644, 0.3007, 0.6395, 1.0822 | -0.1644: 3569 (80%); 0.3007: 2677 (60%); 0.6395: 1785 (40%); 1.0822: 893 (20%) | -0.1644: 893 (20%); 0.3007: 1785 (40%); 0.6395: 2677 (60%); 1.0822: 3569 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | 0.322, 1.0953, 1.7374, 2.6271 | 0.322: 3569 (80%); 1.0953: 2677 (60%); 1.7374: 1785 (40%); 2.6271: 893 (20%) | 0.322: 893 (20%); 1.0953: 1786 (40%); 1.7374: 2677 (60%); 2.6271: 3569 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 0.367, 4.62, 7.968, 12.201 | 0.367: 3569 (80%); 4.62: 2677 (60%); 7.968: 1785 (40%); 12.201: 893 (20%) | 0.367: 893 (20%); 4.62: 1785 (40%); 7.968: 2678 (60%); 12.201: 3569 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 52.96, 61.87, 67.33, 72.39 | 52.96: 3569 (80%); 61.87: 2677 (60%); 67.33: 1787 (40%); 72.39: 894 (20%) | 52.96: 895 (20%); 61.87: 1785 (40%); 67.33: 2677 (60%); 72.39: 3569 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 32.32, 54.83, 73.59, 91.84 | 32.32: 3569 (80%); 54.83: 2678 (60%); 73.59: 1786 (40%); 91.84: 894 (20%) | 32.32: 893 (20%); 54.83: 1785 (40%); 73.59: 2677 (60%); 91.84: 3570 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 53.1, 59.65, 63.82, 68.13 | 53.1: 3569 (80%); 59.65: 2679 (60%); 63.82: 1785 (40%); 68.13: 893 (20%) | 53.1: 895 (20%); 59.65: 1785 (40%); 63.82: 2677 (60%); 68.13: 3572 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 51.95, 64, 71.04, 77.37 | 51.95: 3569 (80%); 64: 2677 (60%); 71.04: 1785 (40%); 77.37: 893 (20%) | 51.95: 893 (20%); 64: 1785 (40%); 71.04: 2677 (60%); 77.37: 3570 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0304, 0.0429, 0.0572, 0.0868 | 0.0304: 3570 (80%); 0.0429: 2678 (60%); 0.0572: 1787 (40%); 0.0868: 899 (20%) | 0.0304: 896 (20%); 0.0429: 1800 (40%); 0.0572: 2677 (60%); 0.0868: 3574 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0757, -0.0575, -0.0436, -0.0345 | -0.0757: 3572 (80%); -0.0575: 2677 (60%); -0.0436: 1796 (40%); -0.0345: 902 (20%) | -0.0757: 903 (20%); -0.0575: 1787 (40%); -0.0436: 2679 (60%); -0.0345: 3570 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 4461 (100%); 2: 1171 (26%) | 0: 2754 (62%); 2: 3591 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 30, 45, 59, 71 | 30: 3595 (81%); 45: 2792 (63%); 59: 1811 (41%); 71: 913 (20%) | 30: 897 (20%); 45: 1833 (41%); 59: 2730 (61%); 71: 3616 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 99.1% | 0.0109, 0.0157, 0.0221, 0.0348 | 0.0109: 3525 (79%); 0.0157: 2650 (59%); 0.0221: 1768 (40%); 0.0348: 883 (20%) | 0.0109: 895 (20%); 0.0157: 1770 (40%); 0.0221: 2652 (59%); 0.0348: 3537 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.6251, 0.8157, 0.8883, 0.9335 | 0.6251: 3569 (80%); 0.8157: 2677 (60%); 0.8883: 1785 (40%); 0.9335: 894 (20%) | 0.6251: 893 (20%); 0.8157: 1785 (40%); 0.8883: 2679 (60%); 0.9335: 3570 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 24.9, 62.6, 105.9, 166.1 | 24.9: 3569 (80%); 62.6: 2677 (60%); 105.9: 1786 (40%); 166.1: 894 (20%) | 24.9: 894 (20%); 62.6: 1789 (40%); 105.9: 2677 (60%); 166.1: 3569 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 0.33, 2.8775, 6.14, 12.0961 | 0.33: 3571 (80%); 2.8775: 2677 (60%); 6.14: 1785 (40%); 12.0961: 893 (20%) | 0.33: 893 (20%); 2.8775: 1785 (40%); 6.14: 2677 (60%); 12.0961: 3569 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 53.93, 77.29, 87.52, 92.37 | 53.93: 3569 (80%); 77.29: 2677 (60%); 87.52: 1785 (40%); 92.37: 897 (20%) | 53.93: 893 (20%); 77.29: 1785 (40%); 87.52: 2678 (60%); 92.37: 3569 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 53.11, 79.85, 88.25, 92.58 | 53.11: 3569 (80%); 79.85: 2677 (60%); 88.25: 1787 (40%); 92.58: 894 (20%) | 53.11: 893 (20%); 79.85: 1785 (40%); 88.25: 2677 (60%); 92.58: 3569 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 28.98, 64.56, 85.86, 96.2 | 28.98: 3569 (80%); 64.56: 2677 (60%); 85.86: 1785 (40%); 96.2: 893 (20%) | 28.98: 893 (20%); 64.56: 1785 (40%); 85.86: 2678 (60%); 96.2: 3570 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 20.37, 59.88, 83.45, 99.42 | 20.37: 3569 (80%); 59.88: 2677 (60%); 83.45: 1785 (40%); 99.42: 893 (20%) | 20.37: 893 (20%); 59.88: 1786 (40%); 83.45: 2677 (60%); 99.42: 3570 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 12, 17 | 4: 3776 (85%); 8: 2732 (61%); 12: 1881 (42%); 17: 924 (21%) | 4: 1051 (24%); 8: 1920 (43%); 12: 2804 (63%); 17: 3721 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 18 | 5: 3685 (83%); 10: 2774 (62%); 14: 1849 (41%); 18: 972 (22%) | 5: 959 (21%); 10: 1942 (44%); 14: 2795 (63%); 18: 3800 (85%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 49.64, 55.96, 61.06, 66.18 | 49.64: 3571 (80%); 55.96: 2678 (60%); 61.06: 1785 (40%); 66.18: 894 (20%) | 49.64: 893 (20%); 55.96: 1787 (40%); 61.06: 2679 (60%); 66.18: 3569 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.127, 0.3413, 0.5794, 0.8175 | 0.127: 3576 (80%); 0.3413: 2682 (60%); 0.5794: 1800 (40%); 0.8175: 915 (21%) | 0.127: 899 (20%); 0.3413: 1796 (40%); 0.5794: 2698 (60%); 0.8175: 3569 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.44, 16.42, 18.73, 22.84 | 14.44: 3576 (80%); 16.42: 2682 (60%); 18.73: 1794 (40%); 22.84: 897 (20%) | 14.44: 893 (20%); 16.42: 1788 (40%); 18.73: 2683 (60%); 22.84: 3574 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.44, 16.42, 18.73, 22.84 | 14.44: 3576 (80%); 16.42: 2682 (60%); 18.73: 1794 (40%); 22.84: 897 (20%) | 14.44: 893 (20%); 16.42: 1788 (40%); 18.73: 2683 (60%); 22.84: 3574 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8478, 0.8749, 0.9094, 0.9595 | 0.8478: 3575 (80%); 0.8749: 2687 (60%); 0.9094: 1789 (40%); 0.9595: 893 (20%) | 0.8478: 901 (20%); 0.8749: 1787 (40%); 0.9094: 2677 (60%); 0.9595: 3580 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.77, 0.93, 1.09, 1.41 | 0.77: 3608 (81%); 0.93: 2681 (60%); 1.09: 1825 (41%); 1.41: 894 (20%) | 0.77: 910 (20%); 0.93: 1838 (41%); 1.09: 2677 (60%); 1.41: 3584 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0335, 0.0702, 0.1058, 0.166 | 0.0335: 3571 (80%); 0.0702: 2678 (60%); 0.1058: 1786 (40%); 0.166: 893 (20%) | 0.0335: 893 (20%); 0.0702: 1786 (40%); 0.1058: 2680 (60%); 0.166: 3570 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 50.8794, 81.9213, 127.0196, 215.4235 | 50.8794: 3569 (80%); 81.9213: 2677 (60%); 127.0196: 1785 (40%); 215.4235: 893 (20%) | 50.8794: 893 (20%); 81.9213: 1785 (40%); 127.0196: 2677 (60%); 215.4235: 3569 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 48.1353, 77.7779, 121.3233, 205.5359 | 48.1353: 3569 (80%); 77.7779: 2677 (60%); 121.3233: 1785 (40%); 205.5359: 893 (20%) | 48.1353: 893 (20%); 77.7779: 1785 (40%); 121.3233: 2677 (60%); 205.5359: 3569 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 44.9846, 73.604, 115.5143, 195.8736 | 44.9846: 3569 (80%); 73.604: 2677 (60%); 115.5143: 1785 (40%); 195.8736: 893 (20%) | 44.9846: 893 (20%); 73.604: 1785 (40%); 115.5143: 2677 (60%); 195.8736: 3569 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 53.2337, 85.4429, 132.3425, 224.458 | 53.2337: 3569 (80%); 85.4429: 2677 (60%); 132.3425: 1785 (40%); 224.458: 893 (20%) | 53.2337: 893 (20%); 85.4429: 1785 (40%); 132.3425: 2677 (60%); 224.458: 3569 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 55.4839, 89.0151, 138.0957, 232.8729 | 55.4839: 3569 (80%); 89.0151: 2677 (60%); 138.0957: 1785 (40%); 232.8729: 893 (20%) | 55.4839: 893 (20%); 89.0151: 1785 (40%); 138.0957: 2677 (60%); 232.8729: 3569 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 4461 (100%) | 0: 4012 (90%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 4461 (100%) | 0: 3986 (89%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0144, 0.0597, 0.0949, 0.1421 | 0.0144: 3570 (80%); 0.0597: 2677 (60%); 0.0949: 1785 (40%); 0.1421: 893 (20%) | 0.0144: 893 (20%); 0.0597: 1785 (40%); 0.0949: 2679 (60%); 0.1421: 3570 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -49.95, -25.26, -15.9, -9.9 | -49.95: 3569 (80%); -25.26: 2677 (60%); -15.9: 1785 (40%); -9.9: 894 (20%) | -49.95: 894 (20%); -25.26: 1785 (40%); -15.9: 2677 (60%); -9.9: 3569 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.6% | 0.5204, 0.8319, 1.0631, 1.3491 | 0.5204: 3553 (80%); 0.8319: 2665 (60%); 1.0631: 1777 (40%); 1.3491: 889 (20%) | 0.5204: 889 (20%); 0.8319: 1778 (40%); 1.0631: 2665 (60%); 1.3491: 3553 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 3637 (82%); 5: 2866 (64%); 7: 2062 (46%); 9: 1171 (26%) | 3: 1170 (26%); 5: 1963 (44%); 7: 2809 (63%); 9: 3803 (85%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.6% | 0.1816, 0.2203, 0.2652, 0.3366 | 0.1816: 3553 (80%); 0.2203: 2666 (60%); 0.2652: 1778 (40%); 0.3366: 890 (20%) | 0.1816: 892 (20%); 0.2203: 1777 (40%); 0.2652: 2665 (60%); 0.3366: 3553 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.6% | 3, 5, 7, 9 | 3: 3615 (81%); 5: 2871 (64%); 7: 1978 (44%); 9: 1036 (23%) | 3: 1189 (27%); 5: 1998 (45%); 7: 2932 (66%); 9: 3909 (88%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.6% | 0.0267, 0.0371, 0.0495, 0.0731 | 0.0267: 3560 (80%); 0.0371: 2670 (60%); 0.0495: 1784 (40%); 0.0731: 891 (20%) | 0.0267: 894 (20%); 0.0371: 1777 (40%); 0.0495: 2667 (60%); 0.0731: 3554 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.6% | 4, 6, 8, 10 | 4: 3695 (83%); 6: 2973 (67%); 8: 2223 (50%); 10: 1034 (23%) | 4: 1087 (24%); 6: 1815 (41%); 8: 2794 (63%); 10: 4441 (100%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.6% | -0.1595, -0.0105, 0.1322, 0.3367 | -0.1595: 3554 (80%); -0.0105: 2665 (60%); 0.1322: 1777 (40%); 0.3367: 889 (20%) | -0.1595: 889 (20%); -0.0105: 1778 (40%); 0.1322: 2665 (60%); 0.3367: 3553 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 3620 (81%); 5: 2828 (63%); 7: 1995 (45%); 9: 1117 (25%) | 3: 1195 (27%); 5: 2046 (46%); 7: 2852 (64%); 9: 3820 (86%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.5% |
| 8k_item_5_02_filed_within_7d | 3.5% |
| above_avwap_20high | 23.9% |
| above_avwap_20low | 87.9% |
| above_avwap_252low | 93.7% |
| above_avwap_50low | 89.7% |
| above_cam_r3 | 19.8% |
| above_cam_r4 | 12.1% |
| above_cpr | 52.7% |
| above_pivot | 47.1% |
| above_prev_high | 19.4% |
| above_prev_high_clearance_atr_05 | 7.6% |
| above_prev_low | 80.4% |
| above_r1 | 14.2% |
| above_r2 | 7.4% |
| above_vwap | 70.3% |
| above_wood_p | 58.5% |
| ad_rising | 66.0% |
| adx_cross_up | 4.7% |
| adx_cross_up_20 | 4.1% |
| adx_di_bear | 15.8% |
| adx_di_bull | 84.2% |
| adx_strong | 9.7% |
| adx_trending | 47.6% |
| ao_cross_dn | 1.5% |
| ao_cross_up | 1.9% |
| ao_positive | 86.6% |
| ao_twin_peaks_bull | 1.1% |
| at_key_fib | 8.5% |
| at_key_fib_wide | 19.5% |
| avwap_20high_loss_recent_3d | 39.1% |
| avwap_20high_reclaim_recent_3d | 12.6% |
| avwap_20low_loss_recent_3d | 7.8% |
| avwap_20low_reclaim_recent_3d | 9.9% |
| avwap_252low_loss_recent_3d | 3.4% |
| avwap_252low_reclaim_recent_3d | 4.5% |
| avwap_50low_loss_recent_3d | 6.0% |
| avwap_50low_reclaim_recent_3d | 6.6% |
| bb_10_20_above_mid | 77.9% |
| bb_10_20_expanding | 57.8% |
| bb_10_20_pctb_gt_75 | 53.6% |
| bb_10_20_pctb_gt_8 | 41.4% |
| bb_10_20_pctb_gt_85 | 26.7% |
| bb_10_20_pctb_gt_9 | 15.1% |
| bb_10_20_pctb_gt_95 | 8.3% |
| bb_10_20_pctb_lt_05 | 3.1% |
| bb_10_20_pctb_lt_1 | 4.9% |
| bb_10_20_pctb_lt_15 | 7.1% |
| bb_10_20_pctb_lt_2 | 9.3% |
| bb_10_20_pctb_lt_25 | 11.5% |
| bb_10_20_reclaim_from_lower_recent_3d | 4.2% |
| bb_10_20_reclaim_from_upper_recent_3d | 27.9% |
| bb_10_20_squeeze | 29.9% |
| bb_10_20_touch_lower | 3.5% |
| bb_10_20_touch_upper | 8.7% |
| bb_20_15_above_mid | 82.0% |
| bb_20_15_expanding | 69.6% |
| bb_20_15_pctb_gt_75 | 72.9% |
| bb_20_15_pctb_gt_8 | 70.0% |
| bb_20_15_pctb_gt_85 | 66.2% |
| bb_20_15_pctb_gt_9 | 61.2% |
| bb_20_15_pctb_gt_95 | 54.9% |
| bb_20_15_pctb_lt_05 | 7.5% |
| bb_20_15_pctb_lt_1 | 8.9% |
| bb_20_15_pctb_lt_15 | 10.0% |
| bb_20_15_pctb_lt_2 | 10.9% |
| bb_20_15_pctb_lt_25 | 12.2% |
| bb_20_15_reclaim_from_lower_recent_3d | 3.9% |
| bb_20_15_reclaim_from_upper_recent_3d | 22.5% |
| bb_20_15_squeeze | 30.0% |
| bb_20_15_touch_lower | 8.1% |
| bb_20_15_touch_upper | 55.0% |
| bb_20_20_above_mid | 82.0% |
| bb_20_20_expanding | 69.6% |
| bb_20_20_pctb_gt_75 | 67.5% |
| bb_20_20_pctb_gt_8 | 61.2% |
| bb_20_20_pctb_gt_85 | 52.2% |
| bb_20_20_pctb_gt_9 | 40.4% |
| bb_20_20_pctb_gt_95 | 28.2% |
| bb_20_20_pctb_lt_05 | 4.0% |
| bb_20_20_pctb_lt_1 | 5.5% |
| bb_20_20_pctb_lt_15 | 7.1% |
| bb_20_20_pctb_lt_2 | 8.9% |
| bb_20_20_pctb_lt_25 | 10.3% |
| bb_20_20_reclaim_from_lower_recent_3d | 3.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 29.8% |
| bb_20_20_squeeze | 15.4% |
| bb_20_20_touch_lower | 3.9% |
| bb_20_20_touch_upper | 25.6% |
| bearish_engulfing | 6.1% |
| bearish_pin_bar | 8.3% |
| below_avwap_20high | 76.1% |
| below_avwap_20low | 12.1% |
| below_avwap_252low | 6.3% |
| below_avwap_50low | 10.3% |
| below_cam_s3 | 38.0% |
| below_cam_s4 | 19.8% |
| below_cpr | 52.9% |
| below_ema_20 | 17.1% |
| below_ema_200 | 19.0% |
| below_ema_200_break_recent_5d | 5.2% |
| below_ema_20_break_recent_5d | 11.8% |
| below_ema_21 | 17.0% |
| below_ema_21_break_recent_5d | 11.8% |
| below_ema_50 | 13.4% |
| below_ema_50_break_recent_5d | 9.3% |
| below_ema_9 | 21.6% |
| below_ema_9_break_recent_5d | 16.3% |
| below_prev_high | 80.5% |
| below_prev_low | 19.5% |
| below_prev_low_clearance_atr_05 | 6.1% |
| below_s1 | 20.0% |
| below_s2 | 7.0% |
| below_sma_20 | 18.0% |
| below_sma_200 | 20.6% |
| below_sma_21 | 17.8% |
| below_sma_50 | 12.7% |
| below_sma_9 | 22.8% |
| below_vwap | 29.7% |
| blowoff_recent_3d | 2.2% |
| break_52w_high | 4.0% |
| break_52w_high_clearance_atr_05 | 1.1% |
| break_52w_high_confirmed_today | 13.4% |
| break_52w_low | 0.1% |
| bullish_engulfing | 1.3% |
| bullish_pin_bar | 7.6% |
| capitulation_recent_3d | 0.2% |
| ceo_buy | 0.3% |
| cfo_buy | 0.3% |
| chandelier_long_bullish | 88.0% |
| chandelier_long_flip_dn | 3.0% |
| chandelier_short_bearish | 25.4% |
| chandelier_short_flip_up | 2.6% |
| classification_change_from_tech | 84.6% |
| classification_change_to_defensive | 15.4% |
| close_above_open | 15.7% |
| close_below_open | 82.9% |
| close_in_bottom_40pct_of_range | 59.1% |
| close_in_top_40pct_of_range | 20.8% |
| cluster_buy | 0.2% |
| cmf_cross_dn | 5.0% |
| cmf_cross_up | 2.6% |
| cmf_negative | 24.1% |
| cmf_positive | 75.9% |
| concentrated_sell | 8.1% |
| cpr_narrow | 86.3% |
| cpr_narrow_tight | 22.1% |
| cup_handle_detected | 15.3% |
| cup_handle_neckline_break_retest_long | 18.6% |
| dc10_breakout_dn | 4.6% |
| dc10_breakout_dn_1pct | 7.5% |
| dc10_breakout_up | 16.7% |
| dc10_breakout_up_1pct | 33.5% |
| dc10_new_high | 40.7% |
| dc10_strong_breakout_dn | 1.6% |
| dc10_strong_breakout_up | 5.7% |
| dc20_breakout_dn | 2.7% |
| dc20_breakout_up | 15.7% |
| dc20_new_high | 39.1% |
| dc20_resistance_break_retest_strong | 48.1% |
| dc20_support_break_retest_strong | 3.1% |
| defensive_leadership | 45.7% |
| director_only_buy | 2.2% |
| doji | 8.2% |
| double_bottom_detected | 16.9% |
| double_top_detected | 18.7% |
| dpi_elevated | 51.0% |
| drying_volume_on_down_turn | 42.4% |
| drying_volume_on_up_turn | 7.4% |
| ema_20_50_bearish | 14.3% |
| ema_20_50_bullish | 85.7% |
| ema_20_50_death_cross | 0.9% |
| ema_20_50_golden_cross | 2.1% |
| ema_50_200_bearish | 33.9% |
| ema_50_200_bullish | 66.1% |
| ema_50_200_death_cross | 0.1% |
| ema_50_200_golden_cross | 0.9% |
| ema_9_21_bearish | 13.1% |
| ema_9_21_bullish | 86.9% |
| ema_9_21_death_cross | 1.7% |
| ema_9_21_golden_cross | 1.4% |
| evening_star | 4.3% |
| flag_bear_break_retest_short | 0.0% |
| flag_bear_broke | 0.0% |
| flag_bull_break_retest_long | 4.8% |
| flag_bull_broke | 5.3% |
| flag_bull_detected | 1.2% |
| force_index_cross_dn | 3.5% |
| force_index_cross_up | 2.4% |
| force_index_positive | 81.0% |
| gap_dn_1_5pct | 5.3% |
| gap_dn_2pct | 3.3% |
| gap_up_1_5pct | 12.2% |
| gap_up_2pct | 9.3% |
| hammer | 5.4% |
| head_shoulders_bottom_detected | 6.6% |
| head_shoulders_top_detected | 4.0% |
| house_cluster_buy | 4.4% |
| house_cluster_sell | 4.5% |
| htf_aligned_bear | 6.8% |
| htf_aligned_bull | 69.4% |
| htf_disagreement | 1.7% |
| hull_bearish | 22.1% |
| hull_bullish | 77.9% |
| hull_flip_dn | 2.9% |
| hull_flip_up | 2.8% |
| ichi_above_cloud | 82.7% |
| ichi_above_cloud_break_recent_5d | 17.3% |
| ichi_below_cloud | 8.1% |
| ichi_below_cloud_break_recent_5d | 5.6% |
| ichi_cloud_thick | 86.3% |
| ichi_tk_bearish | 13.0% |
| ichi_tk_bullish | 79.7% |
| ichi_tk_cross_dn | 1.4% |
| ichi_tk_cross_up | 2.4% |
| ichi_weekly_above_cloud | 62.1% |
| ichi_weekly_below_cloud | 19.1% |
| ichi_weekly_in_cloud | 18.7% |
| in_reversal_window | 2.8% |
| inside_bar | 16.5% |
| inside_cpr | 1.1% |
| inside_kc | 55.7% |
| insider_cluster_active | 13.8% |
| institutional_buy | 88.7% |
| institutional_negative | 5.3% |
| institutional_persistence_growing | 43.5% |
| institutional_persistence_strong | 60.6% |
| institutional_strong_buy | 80.2% |
| inverted_cup_handle_detected | 8.6% |
| is_friday | 21.3% |
| is_halloween_period | 54.9% |
| is_halloween_period_first_day | 0.8% |
| is_january | 10.8% |
| is_january_extended | 12.3% |
| is_monday | 19.0% |
| is_pre_holiday | 3.7% |
| is_summer_period | 45.1% |
| is_totm_window | 32.8% |
| is_totm_window_first_day | 8.9% |
| is_week_open | 21.2% |
| kc_touch_lower | 3.3% |
| kc_touch_upper | 47.9% |
| large_dollar_buy | 0.6% |
| macd_12_26_9_bearish | 24.9% |
| macd_12_26_9_bullish | 75.1% |
| macd_12_26_9_crossover_dn | 2.5% |
| macd_12_26_9_crossover_up | 2.4% |
| macd_8_21_5_bearish | 27.8% |
| macd_8_21_5_bullish | 72.2% |
| macd_8_21_5_crossover_dn | 3.8% |
| macd_8_21_5_crossover_up | 2.9% |
| marubozu_bear | 0.4% |
| marubozu_bull | 0.5% |
| mfi_broad_overbought | 37.4% |
| mfi_broad_oversold | 2.4% |
| mfi_overbought | 13.2% |
| mfi_oversold | 0.5% |
| monthly_above_sma_12 | 77.4% |
| monthly_above_sma_6 | 85.9% |
| monthly_bias_bear | 10.4% |
| monthly_bias_bull | 73.6% |
| monthly_momentum_pos | 74.5% |
| morning_star | 1.1% |
| near_52w_high | 25.0% |
| near_52w_high_95pct | 42.8% |
| near_52w_high_retest_long | 0.2% |
| near_52w_low | 0.3% |
| near_52w_low_105pct | 0.9% |
| near_52w_low_retest_short | 0.2% |
| near_avwap_20high_atr_05x | 56.1% |
| near_avwap_20high_atr_10x | 78.9% |
| near_avwap_20high_atr_15x | 90.1% |
| near_avwap_20high_atr_20x | 95.8% |
| near_avwap_20low_atr_05x | 14.7% |
| near_avwap_20low_atr_10x | 26.2% |
| near_avwap_20low_atr_15x | 38.8% |
| near_avwap_20low_atr_20x | 52.7% |
| near_avwap_252low_atr_05x | 4.3% |
| near_avwap_252low_atr_10x | 8.2% |
| near_avwap_252low_atr_15x | 12.7% |
| near_avwap_252low_atr_20x | 17.3% |
| near_avwap_50low_atr_05x | 7.7% |
| near_avwap_50low_atr_10x | 15.3% |
| near_avwap_50low_atr_15x | 23.5% |
| near_avwap_50low_atr_20x | 31.2% |
| near_cam_r3 | 10.7% |
| near_cam_s3 | 20.1% |
| near_cam_s4 | 13.0% |
| near_fib_236 | 7.2% |
| near_fib_382 | 3.9% |
| near_fib_500 | 2.6% |
| near_fib_618 | 2.0% |
| near_fib_786 | 1.4% |
| near_pivot | 19.5% |
| near_prev_close | 20.4% |
| near_prev_high | 11.0% |
| near_prev_low | 11.1% |
| near_r1 | 7.2% |
| near_r1_wide | 44.0% |
| near_r2 | 2.6% |
| near_r2_wide | 21.7% |
| near_s1 | 12.1% |
| near_s1_wide | 56.3% |
| near_s2 | 4.3% |
| near_s2_wide | 26.5% |
| near_s3 | 1.7% |
| near_wood_r1 | 14.7% |
| near_wood_s1 | 8.2% |
| news_uses_polygon_score | 28.3% |
| obv_bearish | 21.5% |
| obv_bullish | 78.5% |
| obv_diverge_bull | 4.9% |
| obv_falling | 29.8% |
| obv_rising | 70.2% |
| outside_bar | 7.8% |
| pead_negative_surprise | 12.8% |
| pead_positive_surprise | 28.8% |
| pin_bar | 15.9% |
| po3_accumulation_active | 25.3% |
| po3_bearish | 23.8% |
| po3_bullish | 2.8% |
| po3_manipulation_sweep_down | 4.0% |
| po3_manipulation_sweep_up | 10.6% |
| po3_mmbm_setup | 0.4% |
| po3_mmsm_setup | 5.9% |
| po3_sweep_above_prior_high | 58.2% |
| po3_sweep_below_prior_low | 39.2% |
| ppo_bullish | 74.3% |
| ppo_crossover_dn | 2.6% |
| ppo_crossover_up | 2.4% |
| pre_fomc_d0 | 3.6% |
| pre_fomc_d1 | 3.2% |
| pre_fomc_window | 6.8% |
| price_above_dema | 70.2% |
| price_above_ema_20 | 82.9% |
| price_above_ema_200 | 81.0% |
| price_above_ema_200_break_recent_5d | 13.0% |
| price_above_ema_20_break_recent_5d | 17.6% |
| price_above_ema_21 | 83.0% |
| price_above_ema_21_break_recent_5d | 17.2% |
| price_above_ema_50 | 86.6% |
| price_above_ema_50_break_recent_5d | 14.6% |
| price_above_ema_9 | 78.4% |
| price_above_ema_9_break_recent_5d | 25.2% |
| price_above_hull | 62.7% |
| price_above_sma_200 | 79.4% |
| price_above_sma_21 | 82.2% |
| price_above_sma_50 | 87.3% |
| price_above_tema | 57.7% |
| price_below_dema | 29.8% |
| price_below_hull | 37.3% |
| price_below_tema | 42.3% |
| psar_bullish | 78.3% |
| psar_flip_dn | 2.8% |
| psar_flip_up | 2.8% |
| r1_break_retest_long | 77.8% |
| recent_blowoff_at_r3 | 0.6% |
| recent_capitulation_at_s3 | 0.0% |
| resistance_break_retest | 61.8% |
| risk_off_regime_bond_signal | 17.6% |
| risk_off_regime_bond_signal_strong | 8.5% |
| risk_off_regime_gold_signal | 35.8% |
| risk_on_regime_bond_signal | 49.1% |
| risk_on_regime_bond_signal_strong | 23.1% |
| roc_positive | 81.1% |
| roc_turning_dn | 4.0% |
| roc_turning_up | 2.8% |
| rsi_14_bullish | 84.1% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 4.2% |
| rsi_14_cross_dn_overbought_recent_3d | 14.3% |
| rsi_14_cross_up_oversold_recent_3d | 0.5% |
| rsi_14_extreme_ob | 3.5% |
| rsi_14_overbought | 29.3% |
| rsi_14_oversold | 0.7% |
| rsi_14_rising | 36.4% |
| rsi_21_bullish | 86.2% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.9% |
| rsi_21_cross_dn_overbought_recent_3d | 8.0% |
| rsi_21_extreme_ob | 0.6% |
| rsi_21_overbought | 13.4% |
| rsi_21_oversold | 0.1% |
| rsi_21_rising | 36.4% |
| rsi_2_bullish | 65.1% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 46.9% |
| rsi_2_cross_dn_overbought_recent_3d | 42.8% |
| rsi_2_cross_up_extreme_os_recent_3d | 14.7% |
| rsi_2_cross_up_oversold_recent_3d | 19.1% |
| rsi_2_extreme_ob | 33.6% |
| rsi_2_extreme_os | 11.7% |
| rsi_2_overbought | 43.8% |
| rsi_2_oversold | 18.2% |
| rsi_2_rising | 36.4% |
| rsi_9_bullish | 82.1% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 13.8% |
| rsi_9_cross_dn_overbought_recent_3d | 19.4% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_9_cross_up_oversold_recent_3d | 2.1% |
| rsi_9_extreme_ob | 12.9% |
| rsi_9_extreme_os | 0.4% |
| rsi_9_overbought | 43.3% |
| rsi_9_oversold | 3.0% |
| rsi_9_rising | 36.4% |
| s1_break_retest_short | 22.4% |
| sc_13d_filed_within_30d | 2.6% |
| sc_13g_filed_within_30d | 4.5% |
| sector_outperforming_spy | 54.6% |
| sector_underperforming_spy | 45.4% |
| shooting_star | 5.4% |
| sma_20_50_bullish | 81.4% |
| sma_20_50_golden_cross | 2.4% |
| sma_50_200_bullish | 61.7% |
| sma_50_200_golden_cross | 0.7% |
| sma_9_21_bullish | 83.8% |
| sma_9_21_golden_cross | 2.2% |
| smc_bos_bearish | 5.6% |
| smc_bos_bullish | 24.9% |
| smc_bos_retest_long | 4.6% |
| smc_bos_retest_short | 3.1% |
| smc_breaker_block_bearish | 9.1% |
| smc_breaker_block_bullish | 33.9% |
| smc_choch_bearish | 1.6% |
| smc_choch_bullish | 8.7% |
| smc_equal_highs_swept | 6.7% |
| smc_equal_lows_swept | 2.2% |
| smc_fvg_bearish_active | 19.0% |
| smc_fvg_bullish_active | 67.7% |
| smc_fvg_retest_long_zone | 20.1% |
| smc_fvg_retest_short_zone | 3.6% |
| smc_in_discount_zone | 18.1% |
| smc_in_premium_zone | 91.3% |
| smc_inverse_fvg_bearish | 35.7% |
| smc_inverse_fvg_bullish | 95.9% |
| smc_liquidity_swept_dn | 2.0% |
| smc_liquidity_swept_up | 2.0% |
| smc_mitigation_block_long | 0.4% |
| smc_mitigation_block_short | 5.1% |
| smc_ob_bearish_active | 13.6% |
| smc_ob_bullish_active | 57.6% |
| smc_ote_long_zone | 2.6% |
| smc_ote_short_zone | 8.8% |
| squeeze_fire_dn | 2.0% |
| squeeze_fire_up | 1.1% |
| squeeze_in | 17.9% |
| squeeze_positive | 82.0% |
| stoch_bearish_cross | 21.6% |
| stoch_broad_overbought | 66.6% |
| stoch_broad_oversold | 8.8% |
| stoch_bullish_cross | 7.6% |
| stoch_overbought | 59.7% |
| stoch_oversold | 6.7% |
| stochrsi_cross_dn | 39.8% |
| stochrsi_cross_up | 15.6% |
| stochrsi_overbought | 43.7% |
| stochrsi_oversold | 19.8% |
| supertrend_bearish | 1.1% |
| supertrend_bullish | 98.9% |
| supertrend_flip_dn | 0.5% |
| supertrend_flip_recent_long_5d | 0.8% |
| supertrend_flip_recent_short_5d | 1.5% |
| supertrend_flip_up | 0.3% |
| support_break_retest | 5.4% |
| tema_above_dema | 77.5% |
| tema_cross_dn | 1.8% |
| tema_cross_up | 2.3% |
| three_black_crows | 2.0% |
| three_white_soldiers | 3.0% |
| triangle_apex_break_retest_long | 28.9% |
| triangle_ascending_detected | 11.3% |
| triangle_descending_detected | 3.9% |
| uo_overbought | 9.0% |
| uo_oversold | 0.5% |
| usd_strengthening | 20.6% |
| usd_weakening | 8.9% |
| vix_band_high | 33.3% |
| vix_band_low | 38.7% |
| vix_band_mid | 28.0% |
| vix_term_backwardation | 8.3% |
| vix_term_contango | 91.7% |
| vol_above_avg | 49.5% |
| vol_below_avg | 50.5% |
| vol_spike_12x | 31.4% |
| vol_spike_15x | 16.8% |
| vol_spike_17x | 11.5% |
| vol_spike_2x | 7.0% |
| vol_spike_2x_on_down_day_recent_3d | 2.8% |
| vol_spike_2x_on_up_day_recent_3d | 11.6% |
| vol_spike_3x | 1.7% |
| vp_above_value_area | 67.0% |
| vp_below_value_area | 3.8% |
| vp_close_above_poc | 85.6% |
| vp_close_below_poc | 14.4% |
| vp_in_value_area | 29.3% |
| week_open_gap_down_15pct | 1.7% |
| week_open_gap_up_15pct | 2.3% |
| weekly_above_ema_10 | 86.5% |
| weekly_above_ema_20 | 86.6% |
| weekly_bias_bear | 10.7% |
| weekly_bias_bull | 83.8% |
| weekly_momentum_pos | 83.9% |
| williams_r_overbought | 50.5% |
| williams_r_oversold | 8.5% |
| williams_r_rising | 24.0% |
| within_pead_window | 42.5% |
| within_post_deletion_window | 2.7% |
| within_post_inclusion_window | 2.8% |
| within_pre_rebalance_window | 1.4% |
| xs_avoid_high_ivol | 76.7% |
| xs_avoid_high_max | 62.9% |
| xs_high_beta_decile | 26.4% |
| xs_low_beta_bottom_quintile | 26.4% |
| xs_low_beta_decile | 18.1% |
| xs_low_beta_decile_entry_recent_5d | 0.8% |
| xs_low_beta_top_quintile | 18.1% |
| xs_momentum_bottom_decile | 9.4% |
| xs_momentum_bottom_quintile | 18.5% |
| xs_momentum_top_decile | 14.0% |
| xs_momentum_top_quintile | 25.2% |
| xs_quality_bottom_quintile | 20.6% |
| xs_quality_top_quintile | 19.6% |
| xs_quality_top_tercile | 41.4% |
| year_high_break_retest_long | 19.4% |
| year_low_break_retest_short | 0.0% |
| yoy_surprise_high | 55.6% |
| yoy_surprise_negative | 34.6% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 94.1% |
| committed_growth_holders | 94.1% |
| corp_donations_1y | 10.5% |
| corp_donations_count_1y | 10.5% |
| corp_donations_unique_pacs | 10.5% |
| cot_rut_commercials_pctile_3y | 57.1% |
| cot_rut_mmoney_pctile_3y | 57.1% |
| cup_handle_depth_pct | 22.8% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 5.0% |
| days_since_inclusion | 13.4% |
| days_to_next_holiday | 66.9% |
| days_to_rebalance | 8.0% |
| dpi_30d_avg | 96.1% |
| dpi_recent | 96.1% |
| earnings_announcement_return | 91.8% |
| earnings_eps_yoy_growth | 96.0% |
| flag_bull_pole_move_pct | 1.2% |
| gov_contracts_4q_sum | 41.7% |
| gov_contracts_last_qtr_amount | 41.7% |
| gov_contracts_qoq_growth | 41.7% |
| head_shoulders_magnitude_pct | 10.1% |
| insider_director_buyers_30d | 3.3% |
| insider_officer_buyers_30d | 3.3% |
| insider_total_shares_bought_30d | 3.3% |
| insider_unique_buyers_30d | 3.3% |
| inverted_cup_handle_height_pct | 19.0% |
| lobbying_amount_1y | 71.5% |
| lobbying_amount_q | 71.5% |
| lobbying_amount_yoy | 71.5% |
| monthly_momentum_6m | 97.7% |
| otc_short_ratio_recent | 96.1% |
| otc_volume_recent | 96.1% |
| pct_from_avwap_20high | 60.8% |
| pct_from_avwap_20low | 94.8% |
| pct_from_avwap_252low | 97.6% |
| persistent_holders_4q | 94.1% |
| persistent_holders_8q | 94.1% |
| sc_13g_latest_percent_owned | 2.2% |
| search_volume_index_recent | 76.8% |
| search_volume_observations | 76.8% |
| search_volume_zscore_30d | 76.8% |
| sector_etf_return_20d | 2.4% |
| spy_return_20d | 2.4% |
| total_active_holders | 94.1% |
| triangle_breakdown_pct | 3.9% |
| triangle_breakout_pct | 11.3% |
| xs_quality_decile | 63.9% |
| xs_quality_gross_profitability | 63.9% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (1.0), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.998), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.998), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.998), `entry_stop_short` (0.997), `fib_236` (0.999), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.998), `fib_ext_127` (0.997), `fib_ext_162` (0.995), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.998), `monthly_sma_12` (0.987), `monthly_sma_6` (0.997), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.999), `r1` (0.998), `r2` (0.998), `r3` (0.997), `s1` (0.998), `s2` (0.998), `s3` (0.998), `supertrend_value` (0.998), `swing_high` (0.998), `swing_low` (0.995), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.999), `vp_value_area_low` (0.995), `weekly_close` (0.998), `weekly_ema_10` (1.0), `weekly_ema_20` (0.998), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.982), `year_low` (0.951)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
