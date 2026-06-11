# B693 Sweep Results (B696 follow-on, 2026-06-11)

# Source: scripts/run_b693_sweeps.py per CHECKLIST #77

Source path: scripts/run_b693_sweeps.py (B696 follow-on per owner directive 2026-06-11). Tool: scripts/trigger_followthrough.py (B693 commit f6b1a7162). Re-runnable via `python scripts/run_b693_sweeps.py` (~3 min on local OHLCV cache).

Read-only sweeps run per owner directive on local OHLCV cache.

Universe: top 30 alphabetical T1a PIT-active tickers.

Tool: [scripts/trigger_followthrough.py](scripts/trigger_followthrough.py) (sweep_threshold + conditional_add_test).

Train/test split: train through 2023-12-31 | test 2024-01-01 onward.

Barrier race: +2x ATR target, -1x ATR stop, 10-bar horizon.



## Sweep 2: close-location threshold on 52w-high break (BR-1 family)

- n_tickers contributing: **29**
- Base follow-through (no parameter gate): train 0.2373 (n=295) | test 0.3128 (n=732)

| value | train_FT | test_FT | train_n | test_n |
|---:|---:|---:|---:|---:|
| 0.2 | 0.242 | 0.312 | 289 | 728 |
| 0.25 | 0.242 | 0.311 | 289 | 726 |
| 0.3 | 0.244 | 0.312 | 287 | 720 | **<-- chosen**
| 0.35 | 0.236 | 0.310 | 284 | 713 |
| 0.4 | 0.238 | 0.311 | 282 | 701 |
| 0.45 | 0.242 | 0.313 | 277 | 691 |
| 0.5 | 0.239 | 0.317 | 268 | 666 |
| 0.55 | 0.235 | 0.317 | 260 | 641 |

**Result:** train picks 0.3 (train FT 0.244) but test FT 0.312 <= base 0.313 -> OVERFIT

**!! OVERFIT FLAG -- do not ship this threshold.**

## Sweep 3: break-clearance margin (ATR-scaled) on 52w-high break

- n_tickers contributing: **29**
- Base follow-through (no parameter gate): train 0.2373 (n=295) | test 0.3128 (n=732)

| value | train_FT | test_FT | train_n | test_n |
|---:|---:|---:|---:|---:|
| 0 | 0.242 | 0.313 | 289 | 731 |
| 0.1 | 0.242 | 0.310 | 244 | 622 |
| 0.2 | 0.222 | 0.309 | 203 | 525 |
| 0.3 | 0.239 | 0.300 | 155 | 427 |
| 0.4 | 0.230 | 0.300 | 122 | 347 |
| 0.5 | 0.229 | 0.318 | 96 | 283 |
| 0.6 | 0.257 | 0.330 | 70 | 224 |
| 0.7 | 0.255 | 0.360 | 55 | 172 |
| 0.8 | 0.286 | 0.358 | 42 | 134 | **<-- chosen**
| 0.9 | 0.226 | 0.363 | 31 | 102 |
| 1 | 0.263 | 0.382 | 19 | 68 |

**Result:** chosen 0.8 (plateau 0.8-0.8); test FT 0.358 vs base 0.313 (+0.045) on n=134

## Add-test 4: sector outperforming SPY (20d) on 52w break (reviewer Finding #6)

- n_tickers contributing: **30**
- Base (existing gates only) test FT: **0.3133** (n=731)
- With new gate AND-ed: **0.3071** (n=674)
- Surviving fraction: **92%**

**Verdict: REJECT_REDUNDANT**

no lift (0.313->0.307); just shrinks fires


## Add-test 6: immediate-reclaim filter (next-bar close holds level) on 52w break (anti-fakeout #4)

- n_tickers contributing: **29**
- Base (existing gates only) test FT: **0.311** (n=701)
- With new gate AND-ed: **0.3748** (n=523)
- Surviving fraction: **75%**

**Verdict: ADD**

lifts FT 0.311 -> 0.375 (+0.064); keeps 75%


## Add-test 7: extension filter RSI<75 on 52w break (anti-fakeout #6)

- n_tickers contributing: **29**
- Base (existing gates only) test FT: **0.311** (n=701)
- With new gate AND-ed: **0.3358** (n=399)
- Surviving fraction: **57%**

**Verdict: REJECT_REDUNDANT**

no lift (0.311 -> 0.336); just shrinks fires


## Sweep 8: Donchian DC20 break with vs without overlay (clearance margin sweep)

- n_tickers contributing: **30**
- Base follow-through (no parameter gate): train 0.3525 (n=2451) | test 0.3117 (n=2114)

| value | train_FT | test_FT | train_n | test_n |
|---:|---:|---:|---:|---:|
| 0 | 0.353 | 0.312 | 2451 | 2114 |
| 0.1 | 0.346 | 0.307 | 2075 | 1781 |
| 0.2 | 0.341 | 0.299 | 1722 | 1473 |
| 0.3 | 0.351 | 0.297 | 1371 | 1185 |
| 0.4 | 0.353 | 0.301 | 1104 | 946 |
| 0.5 | 0.354 | 0.305 | 875 | 775 |
| 0.6 | 0.358 | 0.309 | 689 | 634 |
| 0.7 | 0.357 | 0.316 | 535 | 500 |
| 0.8 | 0.379 | 0.312 | 422 | 394 |
| 0.9 | 0.385 | 0.321 | 343 | 305 |
| 1 | 0.408 | 0.318 | 265 | 242 | **<-- chosen**

**Result:** chosen 1 (plateau 1-1); test FT 0.318 vs base 0.312 (+0.006) on n=242

## Sweep 9: Donchian channel period (DC10/15/20/25/30/40) follow-through

- n_tickers contributing: **30**

| period | train_FT | test_FT | train_n | test_n |
|---:|---:|---:|---:|---:|
| DC10 | 0.346 | 0.316 | 3347 | 2916 | **<-- best test_FT**
| DC15 | 0.347 | 0.313 | 2822 | 2424 |
| DC20 | 0.353 | 0.312 | 2451 | 2114 |
| DC25 | 0.352 | 0.301 | 2198 | 1898 |
| DC30 | 0.352 | 0.303 | 1989 | 1744 |
| DC40 | 0.332 | 0.306 | 1674 | 1545 |

## Sweep 1: BR-1 zero diagnosis (per-ticker 4-gate AND counts; sector gate not local)

- n_tickers: **30**
- Question: is BR-1's same-bar 4-gate AND (break_52w + vol_spike_17x + close_above_open + close_top_40%) structurally empty?
- If 4-way AND is near-zero across tickers but '3-of-4 score' is substantial, reviewer Finding #1 is confirmed (empty conjunction, not harness gap).

| ticker | bars | break_52w | vol_spike_17x | close_above_open | close_top_40% | 4-way AND | break+1-of-3 | 3-of-4 score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 1255 | 12 | 73 | 612 | 748 | 3 | 12 | 40 |
| AAPL | 1255 | 67 | 61 | 679 | 782 | 4 | 63 | 82 |
| ABBV | 1255 | 48 | 61 | 668 | 792 | 6 | 48 | 63 |
| ABNB | 1255 | 16 | 86 | 653 | 769 | 3 | 14 | 61 |
| ABT | 1255 | 22 | 75 | 635 | 758 | 3 | 21 | 50 |
| ACGL | 1255 | 84 | 83 | 653 | 773 | 10 | 82 | 106 |
| ACN | 1255 | 29 | 67 | 650 | 758 | 1 | 27 | 43 |
| ADBE | 1255 | 28 | 88 | 651 | 760 | 2 | 27 | 48 |
| ADI | 1255 | 61 | 73 | 651 | 776 | 5 | 58 | 81 |
| ADM | 1255 | 20 | 88 | 648 | 753 | 3 | 20 | 58 |
| ADP | 1255 | 57 | 76 | 649 | 796 | 3 | 54 | 72 |
| ADSK | 1255 | 34 | 92 | 646 | 752 | 3 | 33 | 54 |
| AEE | 1255 | 53 | 60 | 642 | 774 | 8 | 51 | 62 |
| AEP | 1255 | 49 | 66 | 639 | 759 | 5 | 47 | 66 |
| AES | 1255 | 16 | 94 | 594 | 723 | 2 | 15 | 46 |
| AFL | 1255 | 76 | 71 | 661 | 793 | 4 | 70 | 95 |
| AIG | 1255 | 43 | 73 | 653 | 724 | 3 | 43 | 70 |
| AIZ | 1255 | 47 | 74 | 653 | 764 | 6 | 43 | 72 |
| AJG | 1255 | 102 | 91 | 652 | 772 | 5 | 98 | 118 |
| AKAM | 1255 | 48 | 112 | 636 | 746 | 8 | 47 | 86 |
| ALB | 1255 | 34 | 86 | 608 | 746 | 3 | 31 | 61 |
| ALGN | 1255 | 3 | 102 | 600 | 736 | 0 | 3 | 36 |
| ALL | 1255 | 56 | 92 | 639 | 747 | 6 | 52 | 87 |
| ALLE | 1255 | 48 | 84 | 631 | 736 | 5 | 44 | 70 |
| AMAT | 1255 | 87 | 84 | 655 | 787 | 4 | 81 | 91 |
| AMCR | 1255 | 16 | 95 | 565 | 721 | 1 | 15 | 45 |
| AMD | 1255 | 46 | 79 | 634 | 745 | 9 | 45 | 71 |
| AME | 1255 | 72 | 89 | 610 | 757 | 7 | 70 | 95 |
| AMGN | 1255 | 35 | 63 | 615 | 762 | 4 | 34 | 56 |
| AMP | 1255 | 72 | 80 | 676 | 786 | 5 | 69 | 93 |

**Total fires across all 30 tickers:**
- 4-way AND (current BR-1 ex-sector): **131** fires
- break_52w + 1-of-3 score: **1317** fires
- 3-of-4 score (reviewer recommendation): **2078** fires

**Verdict:** 4-way AND fires 131 times across 30 tickers x ~5 years = 0.9 fires/ticker-year. Reviewer's 3-of-4 score: 2078 fires = 13.9/ticker-year = **15.9x more fires** while maintaining 3 of 4 confirmations. Strong evidence for reviewer Finding #1: the same-bar AND is empty by construction; loosening to a score-of-N would rescue the strategy from zero. Owner approval still required for code change.

## Sweep 5: Volume comparison correctness audit (source-read)

- For each breakout-cluster strategy, list the volume gate(s) it uses.
- Reviewer rule: breakouts should EXPAND (vol_spike), retests should CONTRACT (vol_below_avg).
- Anti-pattern flagged: breakout strategy gating on vol_below_avg (wrong direction); retest strategy gating on vol_spike_17x (wrong).

| strategy | volume gates found |
|---|---|
| pivot_r1_breakout | `vol_spike_15x` |
| camarilla_r4_breakout | `vol_spike_2x` |
| ichimoku_cloud_breakout | `<none>` |
| squeeze_breakout | `<none>` |
| volume_spike_breakout | `vol_spike_15x,vol_spike_2x` |
| 52w_high_breakout | `vol_spike_17x,vol_spike_2x` |
| 52w_high_breakout_pullback_long | `<none>` |
| 52w_low_breakdown_pullback_short | `<none>` |
| inside_bar_breakout | `<none>` |
| force_index_breakout | `<none>` |
| donchian_10_breakout | `vol_spike_15x` |
| donchian_breakdown_retest_short | `vol_below_avg,vol_spike_15x,vol_spike_2x` |
| bb_squeeze_volume | `vol_spike_2x` |
| donchian_breakdown_short | `vol_spike_15x` |
| donchian_breakout_long | `vol_spike_15x` |
| donchian_breakout_retest_long | `vol_below_avg,vol_spike_15x` |
| 52w_low_breakdown | `vol_spike_17x,vol_spike_2x` |
| dc20_break_retest | `vol_below_avg,vol_spike_15x` |
| r1_break_retest | `vol_below_avg` |
| 52wh_break_retest | `vol_below_avg` |
| 52wl_break_retest_short | `vol_below_avg` |
| break_retest_volume | `obv_bearish,obv_bullish,obv_falling,obv_rising,vol_below_avg` |
| break_retest_confluence | `vol_below_avg` |
| htf_aligned_breakout_long | `vol_spike_15x` |
| htf_aligned_breakout_short | `vol_spike_15x` |
| squeeze_setup_long | `vol_spike_15x` |
| avwap_252_breakout | `vol_spike_15x` |
| institutional_breakout_confirmation_long | `vol_below_avg` |
| classification_change_breakout_long | `<none>` |
| institutional_persistence_breakout_long | `<none>` |

**35 breakout-cluster strategies inspected. Owner-eyeball each row: is the volume direction correct for the strategy's archetype?**

## Sweep BR-19: squeeze_breakout release-anchor source verify



Strategy body excerpt (first 30 lines):

```python

def strat_squeeze_breakout(s):
    fires = s.get("squeeze_fire_up")
    return _strat(fires, "long", "breakout",
        ["squeeze_fire_up"],
        ["Bollinger Bands were inside Keltner Channels  -  coiling",
         "Squeeze released with positive momentum  -  energy unleashing",
         "One of the highest probability breakout signals"])


```



**Verdict:** the body is NOT obviously release-event-anchored. Reviewer item #24 concern stands: appears STATE-anchored. Owner review the body above to confirm.