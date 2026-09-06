# POST-CONFIG ANALYSIS - all configs, all findings

Source: output_audit/postconfig_ledger.json plus each config's _grid_auto.json, _spot_check.json and _lenses.json (written by scripts/run_postconfig.py) and output_audit/postconfig_landings.jsonl (written by scripts/postconfig_landing.py); rendered by scripts/postconfig_doc.py; per CHECKLIST #77.

REGENERATED WHOLE at every config landing - by the landing supervisor the engine itself invokes (B2520), so a cube that lands by ANY launch path reaches this document. Replaces the per-config report cards (B2198/B2208), which reported step STATUS rather than step FINDINGS.

## How much confidence these checks earn

**Across the entire ledger (126 entries), 904 named checks have run and 5 have ever returned non-PASS.**

## Landings - what the supervisor recorded (B2520)

21 cube(s) landed through the supervisor; **1 not yet reported to the owner** (output_icg_step2_span9_step2_span9).

| cube | landed | via | battery exit | blocking | WARN/FAIL findings | committed | pushed | reported |
|---|---|---|---|---|---|---|---|---|
| output_icg_step2_span9_step2_span9 | 2026-09-06T18:55:21 | engine-hook | 0 | none | 0 | adfba9d5d | True | **NO** |
| output_icg_cfg1_rerun_cfg1_rerun | 2026-09-05T01:17:34 | engine-hook | 0 | none | 0 | d85126201 | True | yes 2026-09-06T05:40:01 |
| output_icg_span100_rerun_span100 | 2026-09-04T12:26:03 | engine-hook | 0 | none | 0 | 0f0e440e6 | True | yes 2026-09-04T12:27:40 |
| output_icg_minq2_minq2 | 2026-09-04T10:54:23 | engine-hook | 0 | none | 0 | f9f2331c9 | True | yes 2026-09-04T11:28:26 |
| output_icg_minq3_minq3 | 2026-09-04T08:07:23 | engine-hook | 0 | none | 0 | 2e85e7d9e | True | yes 2026-09-04T08:28:13 |
| output_icg_minq6_minq6 | 2026-09-04T05:12:47 | engine-hook | 0 | none | 0 | eff36c19b | True | yes 2026-09-04T05:27:31 |
| output_icg_lookback8_lookback8 | 2026-09-04T02:57:37 | engine-hook | 0 | none | 0 | e6ee52ce0 | True | yes 2026-09-04T03:26:39 |
| output_icg_lookback6_lookback6 | 2026-09-04T00:23:35 | engine-hook | 0 | none | 0 | 6425598fb | True | yes 2026-09-04T00:26:36 |
| output_icg_lookback3_lookback3 | 2026-09-03T19:11:37 | engine-hook | 0 | none | 0 | 50257e198 | True | yes 2026-09-03T19:38:59 |
| output_icg_mult1.25_mult1.25 | 2026-09-03T12:49:03 | engine-hook | 0 | 6_post_fix_recheck | 1: selection_margin WARN: rank-1 [breakeven_plus_trail] is_ci_lo -0.297 vs rank-2 [hybrid_50pct_target] -0.297: margin 0.000 between exits; WARN < 0.05 (selection at noise level) | False | False | yes 2026-09-03T14:52:20 |
| output_icg_mult1.0_mult1.0 | 2026-09-03T09:41:39 | engine-hook | 0 | none | 0 | 388db03c0 | True | yes 2026-09-03T14:52:20 |
| output_icg_minq8_minq8 | 2026-09-03T06:13:18 | engine-hook | 0 | none | 0 | 47363d1e7 | True | yes 2026-09-03T14:52:20 |
| output_icg_lookback2_lookback2 | 2026-09-03T04:00:41 | engine-hook | 0 | none | 0 | f1861a9a4 | True | yes 2026-09-03T14:52:20 |
| output_icg_mult1.5_mult1.5 | 2026-09-03T01:45:20 | engine-hook | 0 | none | 0 | 5b3e3c8fa | True | yes 2026-09-03T14:52:20 |
| output_icg_span150_span150 | 2026-09-02T23:31:07 | engine-hook | 0 | none | 0 | 1946b3605 | True | yes 2026-09-03T14:52:20 |
| output_icg_span100_span100 | 2026-09-02T21:16:40 | engine-hook | 0 | 6_post_fix_recheck | 1: empty_signals_share WARN: 313 of 374 trade_log rows carry an empty signals_at_entry (S6-B2512 class) | 7c20103da | True | yes 2026-09-03T14:52:19 |
| output_icg_span50_span50 | 2026-09-02T16:46:26 | engine-hook | 0 | none | 0 | bafb5118e | True | yes 2026-09-02T17:08:14 |
| output_icg_span20_span20 | 2026-09-02T12:46:15 | engine-hook | 2 | 1_cube_sanity | 0 | fb885e91e | True | yes 2026-09-02T13:04:31 |
| output_icg_span9_span9 | 2026-09-02T10:38:38 | engine-hook | 2 | 2_grade_with_config_params, 4_three_leg_spot_check, 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine, 8_verdict_with_denominators | 1: spot_check_disagreements WARN: no spot-check artifact - step 4 produced nothing to read | 3745e05dc | True | yes 2026-09-02T11:23:02 |
| output_icg_cfg1 | 2026-09-02T07:45:46 | manual | 0 | none | 1: empty_signals_share WARN: 23 of 373 trade_log rows carry an empty signals_at_entry (S6-B2512 class) | 42ca9c20f | True | yes 2026-09-02T07:47:02 |
| output_b2174_sw20_sw20 | 2026-09-01T20:08:36 | manual | 0 | none | 1: selection_margin WARN: rank-1 [close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 -> hybrid_50pct_target] is_ci_lo -0.196 vs rank-2 [close_mitigation=False break_pct_max=None age_bars_max=None tail_n=2 -> hybrid_50pct_target] -0.198: margin 0.002 between outcome classes; WARN < 0.05 (selection at noise level) | False | False | yes 2026-09-02T02:27:00 |


## TABLE D - STEP-1 RANKED LIST (top 20)

_Step-1 ranked list. `is_ci_lo` is the RANKING KEY, not a gate - Step-1 admission is min-trades >= 10 plus this list, with NO gates applied (owner ruling B1608). `n` = fires in-sample, placed beside the sort key on purpose. `tier` = DEEP n>=100 / MID 30-99 / THIN 10-29. `dup` = this row's (ci_lo, sharpe, n, exit) signature appears in more than one config - one discovery, several parameter pairs, NOT independent confirmations. `cls` = equivalence-class size. Nothing here is filtered._

**RANK IS NOT TRUSTWORTHINESS.** A conservative lower bound still favours a tight small sample over a noisy deep one; read `n` and `tier` beside every rank.

**HOW `exit` WAS CHOSEN, AND BY WHICH RULER.** Step 1 picks each cell's exit by SHARPE alone - a cheap ranking pass (owner ruling B1605) - while this table RANKS by is_ci_lo. Two different objectives, disclosed because a row can lead on is_ci_lo while carrying the exit that won on Sharpe. Step 2 re-ranks ALL exits by gates passed and is the admission criterion; it has not run. **24 exit methods are registered; 22 are effective per cell** - next_pivot_target is refused on boundary-spanning cells (B2014, flagged by npt_excluded_identity_boundary) and 1 more is collapsed as byte-identical to a survivor (B1593). 24 - 1 - 1 = 22.

| # | config | sw | sp | exit | is_ci_lo | n | tier | dup | is_sharpe | cls | holdout_n | full_period_n | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | b2197_sw50sp50_sw50sp50 | 50 | 50 | time_stop_10d | +1.250 | 14 | THIN | - | 4.301 | 1 | 0 | 14 | BELOW_POWER_FLOOR |
| 2 | b2197_sw30sp150_sw30sp150 | 30 | 150 | time_stop_10d | +1.214 | 11 | THIN | - | 4.807 | 5 | 0 | 11 | BELOW_POWER_FLOOR |
| 3 | b2197_sw50sp50_sw50sp50 | 50 | 50 | time_stop_10d | +1.189 | 19 | THIN | - | 3.724 | 1 | 0 | 19 | BELOW_POWER_FLOOR |
| 4 | b2197_sw50sp50_sw50sp50 | 50 | 50 | time_stop_10d | +1.110 | 22 | THIN | - | 3.427 | 1 | 0 | 22 | BELOW_POWER_FLOOR |
| 5 | b2197_sw50sp50_sw50sp50 | 50 | 50 | time_stop_10d | +1.044 | 15 | THIN | - | 3.929 | 3 | 0 | 15 | BELOW_POWER_FLOOR |
| 6 | b2197_sw50sp50_sw50sp50 | 50 | 50 | time_stop_10d | +1.013 | 23 | THIN | - | 3.260 | 3 | 0 | 23 | BELOW_POWER_FLOOR |
| 7 | b2197_sw50sp50_sw50sp50 | 50 | 50 | time_stop_10d | +0.993 | 13 | THIN | - | 4.127 | 1 | 0 | 13 | BELOW_POWER_FLOOR |
| 8 | b2197_sw50sp20_sw50sp20 | 50 | 20 | time_stop_10d | +0.930 | 14 | THIN | - | 3.915 | 2 | 0 | 14 | BELOW_POWER_FLOOR |
| 9 | b2197_sw30sp20_sw30sp20 | 30 | 20 | time_stop_10d | +0.816 | 12 | THIN | 1 of 3 | 4.103 | 5 | 0 | 12 | BELOW_POWER_FLOOR |
| 10 | b2197_sw30sp50_sw30sp50 | 30 | 50 | time_stop_10d | +0.816 | 12 | THIN | 2 of 3 | 4.103 | 5 | 0 | 12 | BELOW_POWER_FLOOR |
| 11 | b2197_sw30sp100_sw30sp100 | 30 | 100 | time_stop_10d | +0.816 | 12 | THIN | 3 of 3 | 4.103 | 5 | 0 | 12 | BELOW_POWER_FLOOR |
| 12 | b2197_sw50sp20_sw50sp20 | 50 | 20 | time_stop_10d | +0.759 | 15 | THIN | - | 3.592 | 3 | 0 | 15 | BELOW_POWER_FLOOR |
| 13 | b2197_sw50sp9_sw50sp9 | 50 | 9 | time_stop_10d | +0.724 | 25 | THIN | - | 2.820 | 1 | 0 | 25 | BELOW_POWER_FLOOR |
| 14 | b2197_sw30sp20_sw30sp20 | 30 | 20 | earnings_blackout | +0.701 | 22 | THIN | - | 1.702 | 5 | 0 | 22 | BELOW_POWER_FLOOR |
| 15 | b2197_sw30sp9_sw30sp9 | 30 | 9 | earnings_blackout | +0.687 | 22 | THIN | - | 1.684 | 5 | 0 | 22 | BELOW_POWER_FLOOR |
| 16 | b2197_sw30sp150_sw30sp150 | 30 | 150 | earnings_blackout | +0.671 | 14 | THIN | - | 1.990 | 5 | 0 | 14 | BELOW_POWER_FLOOR |
| 17 | b2197_sw50sp9_sw50sp9 | 50 | 9 | time_stop_10d | +0.661 | 26 | THIN | - | 2.706 | 3 | 0 | 26 | BELOW_POWER_FLOOR |
| 18 | b2197_sw50sp9_sw50sp9 | 50 | 9 | fixed_4r_2r | +0.656 | 33 | MID | - | 1.930 | 1 | 0 | 33 | BELOW_POWER_FLOOR |
| 19 | b2197_sw30sp50_sw30sp50 | 30 | 50 | earnings_blackout | +0.644 | 16 | THIN | 1 of 2 | 1.830 | 5 | 0 | 16 | BELOW_POWER_FLOOR |
| 20 | b2197_sw30sp100_sw30sp100 | 30 | 100 | earnings_blackout | +0.644 | 16 | THIN | 2 of 2 | 1.830 | 5 | 0 | 16 | BELOW_POWER_FLOOR |

_520 ranked outcomes across 52 graded configs; 494 distinct signatures._

**Best within each depth tier** (the comparison a rank order hides):

| tier | best is_ci_lo | at n | rows |
|---|---|---|---|
| DEEP | +0.428 | 3509 | 306 |
| MID | +0.656 | 33 | 138 |
| THIN | +1.250 | 14 | 76 |

### TABLE D-2 - THE SIX SWEPT AXES

_The SIX swept axes for the same rows, same order - join on `#`. P1 swing_length, P2 close_mitigation (False = production, mitigate on high/low), P3 tail_n, P4 age_bars_max (None = production, no cap), P5 break_pct_max (None = production, no cap), P6 span. `npt_excl` = next_pivot_target was refused on this cell as boundary-spanning (B2014), which is one of the two exits missing from 24._

| # | config | P1 swing | P2 close_mit | P3 tail_n | P4 age_bars | P5 break_pct | P6 span | npt_excl |
|---|---|---|---|---|---|---|---|---|
| 1 | b2197_sw50sp50_sw50sp50 | 50 | True | 3 | None | 0.01 | 50 | True |
| 2 | b2197_sw30sp150_sw30sp150 | 30 | False | 20 | 250 | 0.01 | 150 | None |
| 3 | b2197_sw50sp50_sw50sp50 | 50 | True | 2 | None | 0.02 | 50 | None |
| 4 | b2197_sw50sp50_sw50sp50 | 50 | True | 3 | None | 0.02 | 50 | True |
| 5 | b2197_sw50sp50_sw50sp50 | 50 | True | 20 | None | 0.01 | 50 | True |
| 6 | b2197_sw50sp50_sw50sp50 | 50 | True | 20 | None | 0.02 | 50 | True |
| 7 | b2197_sw50sp50_sw50sp50 | 50 | True | 2 | None | 0.01 | 50 | None |
| 8 | b2197_sw50sp20_sw50sp20 | 50 | True | 3 | None | 0.01 | 20 | None |
| 9 | b2197_sw30sp20_sw30sp20 | 30 | False | 20 | 250 | 0.01 | 20 | None |
| 10 | b2197_sw30sp50_sw30sp50 | 30 | False | 20 | 250 | 0.01 | 50 | None |
| 11 | b2197_sw30sp100_sw30sp100 | 30 | False | 20 | 250 | 0.01 | 100 | None |
| 12 | b2197_sw50sp20_sw50sp20 | 50 | True | 20 | None | 0.01 | 20 | None |
| 13 | b2197_sw50sp9_sw50sp9 | 50 | True | 3 | None | 0.02 | 9 | True |
| 14 | b2197_sw30sp20_sw30sp20 | 30 | False | 20 | 250 | 0.02 | 20 | None |
| 15 | b2197_sw30sp9_sw30sp9 | 30 | False | 20 | 250 | 0.02 | 9 | None |
| 16 | b2197_sw30sp150_sw30sp150 | 30 | True | 20 | 120 | 0.03 | 150 | None |
| 17 | b2197_sw50sp9_sw50sp9 | 50 | True | 20 | None | 0.02 | 9 | True |
| 18 | b2197_sw50sp9_sw50sp9 | 50 | False | 3 | None | 0.02 | 9 | True |
| 19 | b2197_sw30sp50_sw30sp50 | 30 | True | 20 | 250 | 0.02 | 50 | None |
| 20 | b2197_sw30sp100_sw30sp100 | 30 | True | 20 | 250 | 0.02 | 100 | None |

## Index - 52 graded config(s), newest first

| config | best is_ci_lo | fires | starved | steps closed (DONE+N/A of 9; the gate's own is_closed) |
|---|---|---|---|---|
| output_icg_step2_span9_step2_span9 | 0.428 | 3509 | 0/24 exits | 9/9 |
| output_icg_cfg1_rerun_cfg1_rerun | -0.106 | 373 | 0/24 exits | 9/9 |
| output_icg_span100_rerun_span100 | -0.078 | 374 | 0/24 exits | 9/9 |
| output_icg_minq2_minq2 | -0.051 | 402 | 0/24 exits | 9/9 |
| output_icg_minq3_minq3 | -0.084 | 385 | 0/24 exits | 9/9 |
| output_icg_minq6_minq6 | 0.043 | 255 | 0/24 exits | 9/9 |
| output_icg_lookback8_lookback8 | 0.038 | 329 | 0/24 exits | 9/9 |
| output_icg_lookback6_lookback6 | 0.07 | 342 | 0/24 exits | 9/9 |
| output_icg_lookback3_lookback3 | -0.134 | 338 | 0/24 exits | 9/9 |
| output_icg_mult1.25_mult1.25 | -0.297 | 301 | 0/24 exits | 9/9 |
| output_icg_mult1.0_mult1.0 | -0.091 | 450 | 0/24 exits | 9/9 |
| output_icg_span100_span100 | 0.062 | 374 | 0/24 exits | 9/9 |
| output_icg_minq8_minq8 | 0.054 | 256 | 0/24 exits | 9/9 |
| output_icg_lookback2_lookback2 | -0.075 | 323 | 0/24 exits | 9/9 |
| output_icg_mult1.5_mult1.5 | -0.223 | 266 | 0/24 exits | 9/9 |
| output_icg_span150_span150 | -0.11 | 371 | 0/24 exits | 9/9 |
| output_icg_span50_span50 | -0.067 | 405 | 0/24 exits | 9/9 |
| output_icg_span20_span20 | -0.015 | 531 | 0/24 exits | 9/9 |
| output_icg_span9_span9 | 0.167 | 609 | 0/24 exits | 9/9 |
| output_icg_cfg1 | -0.087 | 373 | 0/24 exits | 9/9 |
| output_b2174_sw20_sw20 | -0.196 | 79 | 82/300 combinations | 9/9 |
| output_b2399_step2_sw50sp50_step2_sw50sp50 | -0.026 | 325 | 29/300 combinations | 9/9 |
| output_b2197_sw50sp150_sw50sp150 | 0.437 | 10 | 190/300 combinations | 9/9 |
| output_b2197_sw50sp100_sw50sp100 | -0.023 | 25 | 200/300 combinations | 9/9 |
| output_b2197_sw50sp50_sw50sp50 | 1.25 | 14 | 200/300 combinations | 9/9 |
| output_b2197_sw50sp20_sw50sp20 | 0.93 | 14 | 200/300 combinations | 9/9 |
| output_b2197_sw50sp9_sw50sp9 | 0.724 | 25 | 200/300 combinations | 9/9 |
| output_b2197_sw5sp150_sw5sp150 | 0.019 | 76 | 40/300 combinations | 9/9 |
| output_b2197_sw5sp100_sw5sp100 | 0.027 | 77 | 40/300 combinations | 9/9 |
| output_b2197_sw5sp50_sw5sp50 | -0.005 | 220 | 45/300 combinations | 9/9 |
| output_b2197_sw5sp20_sw5sp20 | -0.005 | 140 | 45/300 combinations | 9/9 |
| output_b2197_sw5sp9_sw5sp9 | 0.098 | 128 | 45/300 combinations | 9/9 |
| output_b2197_sw10sp150_sw10sp150 | -0.11 | 119 | 40/300 combinations | 9/9 |
| output_b2197_sw10sp100_sw10sp100 | -0.12 | 174 | 40/300 combinations | 9/9 |
| output_b2197_sw10sp50_sw10sp50 | -0.042 | 156 | 45/300 combinations | 9/9 |
| output_b2197_sw10sp20_sw10sp20 | -0.07 | 110 | 41/300 combinations | 9/9 |
| output_b2197_sw10sp9_sw10sp9 | -0.014 | 68 | 42/300 combinations | 9/9 |
| output_b2197_sw30sp150_sw30sp150 | 1.214 | 11 | 106/300 combinations | 9/9 |
| output_b2197_sw30sp100_sw30sp100 | 0.816 | 12 | 100/300 combinations | 9/9 |
| output_b2197_sw30sp50_sw30sp50 | 0.816 | 12 | 100/300 combinations | 9/9 |
| output_b2197_sw30sp20_sw30sp20 | 0.816 | 12 | 100/300 combinations | 9/9 |
| output_b2197_sw30sp9_sw30sp9 | 0.687 | 22 | 95/300 combinations | 9/9 |
| output_b2197_sw20sp150_sw20sp150 | -0.114 | 80 | 77/300 combinations | 9/9 |
| output_b2197_sw20sp100_sw20sp100 | -0.036 | 66 | 77/300 combinations | 9/9 |
| output_b2197_sw20sp50_sw20sp50 | 0.025 | 62 | 77/300 combinations | 9/9 |
| output_b2197_sw20sp21_sw20sp21 | 0.107 | 88 | 77/300 combinations | 9/9 |
| output_b2197_sw20sp20_sw20sp20 | 0.107 | 88 | 77/300 combinations | 9/9 |
| output_b2197_sw20sp9_sw20sp9 | 0.044 | 71 | 77/300 combinations | 9/9 |
| output_b2190_sw5_sw5 | 0.123 | 74 | 40/300 combinations | 9/9 |
| output_b2190_sw10_sw10 | -0.091 | 92 | 45/300 combinations | 9/9 |
| output_b2177_sw50_sw50 | -0.508 | 33 | 225/300 combinations | 9/9 |
| output_b2183_sw30_sw30 | 0.362 | 11 | 106/300 combinations | 9/9 |

## Per-config findings

### output_icg_step2_span9_step2_span9

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.428** (is_sharpe 0.516, 3509 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 4616 of 4616 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 3509 | breakeven_plus_trail | 0.516 | 0.428 |
| p7_11 | p7=11 p8=5 | 1220 | r_multiple_2r | 0.875 | 0.543 |
| p7_14 | p7=14 p8=5 | 1168 | r_multiple_2r | 0.898 | 0.561 |
| p7_5 | p7=5 p8=5 | 2150 | r_multiple_2r | 0.65 | 0.395 |
| p8_6 | p7=3 p8=6 | 3474 | breakeven_plus_trail | 0.517 | 0.429 |

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569/B2612): grade_institutional_config at manifest min_consecutive_quarters=4 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=9 -> output_icg_step2_span9_step2_span9_grid_auto.json; Step-2 gate verdict present: step2 block: FAIL on breakeven_plus_trail; free levels reproduction-gated -> output_icg_step2_span9_step2_span9_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=SKIP; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=4 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=9; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_step2_span9_step2_span9_spot_check.json; precompute_dir institu |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_step2_span9_step2_span9_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | DONE | engine check PASS on a Step-2 cube: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_step2_span9_step2_span9_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 84216 IS rows (110784 cube rows, 26568 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo 0.428 is_sharpe 0.516 fires 3509 - Step-2 admission on the IS-selected exit breakeven_plus_trail: holdout n 1107 of full-period 4616, holdout sharpe 0.757, gates 5 of 6 PASS -> FAIL; pre-registered exit regime_flip MISMATCH - disclosed, not re-rolled (S6-B2409: clearing the six live gates IS qualification) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 110784 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, META, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/r5_universe_544.txt (verifier is non- | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | c5433575308b564c | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2022-05-05 .. 2026-05-04 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 26568 entries past 2025-05-05 (not declared a Step-1 cube | SKIP **<-- NOT PASS** | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha ed51dce782ea | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 110784 cube rows across 6 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 9, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_step2_span9_step2_span9_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2026-05-05 > HO_START 2025-05-05 -> Step-2 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 1107 of 4616 entries in the holdout (Step-2 cube: the holdout is graded separately, never ranked on) |
| period_concentration | INFO | max year share 0.34 (2025) over 5 years of 4616 entries; WARN > 0.6 |
| ticker_concentration | INFO | top-5 tickers carry 0.04 of 4616 entries across 498 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo 0.428 vs rank-2 [earnings_blackout] 0.319: margin 0.109 between exits; WARN < 0.05 (selection at noise level); Step-2 cube: the IS selection names the admission exit (ruling 2i), so a noise margin is a live risk at any sign |
| empty_signals_share | INFO | 0 of 4616 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/4616 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_step2_span9_step2_span9_spot_check.json |
| min_trades_floor | INFO | 4616 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.428 | 0.516 | 3509 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | 0.319 | 0.387 | 3509 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | 0.308 | 0.414 | 3509 | fixed_4r_2r | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | 0.286 | 0.382 | 3509 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | 0.284 | 0.402 | 3509 | time_stop_20d | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_step2_span9_step2_span9_grid_auto.json._

### output_icg_cfg1_rerun_cfg1_rerun

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.106** (is_sharpe 0.241, 373 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 373 of 373 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 373 | breakeven_plus_trail | 0.241 | -0.106 |
| p7_11 | p7=11 p8=5 | 72 | breakeven_plus_trail | -0.213 | -1.024 |
| p7_14 | p7=14 p8=5 | 63 | breakeven_plus_trail | -0.103 | -0.951 |
| p7_5 | p7=5 p8=5 | 169 | breakeven_plus_trail | 0.199 | -0.318 |
| p8_6 | p7=3 p8=6 | 369 | breakeven_plus_trail | 0.219 | -0.131 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=4 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200 -> output_icg_cfg1_rerun_cfg1_rerun_grid_auto.json; free levels reproduction-gated -> output_icg_cfg1_rerun_cfg1_rerun_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=4 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_cfg1_rerun_cfg1_rerun_spot_check.json; precompute_dir instituti |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_cfg1_rerun_cfg1_rerun_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_cfg1_rerun_cfg1_rerun_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 8952 IS rows (8952 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.106 is_sharpe 0.241 fires 373 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 8952 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 0eb31cbeb4e3825c | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 3f6e5471db81 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 8952 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_cfg1_rerun_cfg1_rerun_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 373 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.40 (2025Q1) over 5 quarters of 373 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.09 of 373 entries across 133 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.106 vs rank-2 [hybrid_50pct_target] -0.318: margin 0.212 between exits; WARN < 0.05 (selection at noise level); INFO not WARN - rank-1 is_ci_lo -0.106 is not above zero, so nothing is selectable and a narrow margin is not a selection risk (S6-B2581b) |
| empty_signals_share | INFO | 0 of 373 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/373 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_cfg1_rerun_cfg1_rerun_spot_check.json |
| min_trades_floor | INFO | 373 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.106 | 0.241 | 373 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.318 | -0.033 | 373 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.462 | -0.161 | 373 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.531 | -0.294 | 373 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.549 | -0.137 | 373 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_cfg1_rerun_cfg1_rerun_grid_auto.json._

### output_icg_span100_rerun_span100

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.078** (is_sharpe 0.281, 374 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 374 of 374 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 374 | breakeven_plus_trail | 0.281 | -0.078 |
| p7_11 | p7=11 p8=5 | 77 | breakeven_plus_trail | 0.19 | -0.601 |
| p7_14 | p7=14 p8=5 | 70 | breakeven_plus_trail | 0.145 | -0.676 |
| p7_5 | p7=5 p8=5 | 177 | breakeven_plus_trail | 0.206 | -0.325 |
| p8_6 | p7=3 p8=6 | 370 | breakeven_plus_trail | 0.259 | -0.103 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=4 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=100 -> output_icg_span100_rerun_span100_grid_auto.json; free levels reproduction-gated -> output_icg_span100_rerun_span100_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=4 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=100; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_span100_rerun_span100_spot_check.json; precompute_dir instituti |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_span100_rerun_span100_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_span100_rerun_span100_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 8976 IS rows (8976 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.078 is_sharpe 0.281 fires 374 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 8976 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 98bd1da4854f9a54 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha c560c6faba51 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 8976 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 100, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_span100_rerun_span100_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 374 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.41 (2025Q1) over 5 quarters of 374 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.08 of 374 entries across 144 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.078 vs rank-2 [hybrid_50pct_target] -0.341: margin 0.263 between exits; WARN < 0.05 (selection at noise level); INFO not WARN - rank-1 is_ci_lo -0.078 is not above zero, so nothing is selectable and a narrow margin is not a selection risk (S6-B2581b) |
| empty_signals_share | INFO | 0 of 374 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/374 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_span100_rerun_span100_spot_check.json |
| min_trades_floor | INFO | 374 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.078 | 0.281 | 374 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.341 | -0.059 | 374 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.47 | -0.172 | 374 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.611 | -0.207 | 374 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.634 | -0.399 | 374 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_span100_rerun_span100_grid_auto.json._

### output_icg_minq2_minq2

**Configuration:** P4_min_consecutive_quarters=2, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.051** (is_sharpe 0.28, 402 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 402 of 402 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 402 | breakeven_plus_trail | 0.28 | -0.051 |
| p7_11 | p7=11 p8=5 | 74 | breakeven_plus_trail | -0.238 | -1.041 |
| p7_14 | p7=14 p8=5 | 63 | breakeven_plus_trail | -0.123 | -0.97 |
| p7_5 | p7=5 p8=5 | 188 | breakeven_plus_trail | 0.267 | -0.217 |
| p8_6 | p7=3 p8=6 | 398 | breakeven_plus_trail | 0.26 | -0.073 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=2 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200 -> output_icg_minq2_minq2_grid_auto.json; free levels reproduction-gated -> output_icg_minq2_minq2_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=2 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_minq2_minq2_spot_check.json; precompute_dir institutional_persi |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_minq2_minq2_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_minq2_minq2_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 9648 IS rows (9648 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.051 is_sharpe 0.28 fires 402 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 9648 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 1a7a6797bcc3523a | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 15abec9a3e12 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 9648 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_minq2_minq2_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 402 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.38 (2025Q1) over 5 quarters of 402 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.09 of 402 entries across 138 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.051 vs rank-2 [hybrid_50pct_target] -0.274: margin 0.223 between exits; WARN < 0.05 (selection at noise level); INFO not WARN - rank-1 is_ci_lo -0.051 is not above zero, so nothing is selectable and a narrow margin is not a selection risk (S6-B2581b) |
| empty_signals_share | INFO | 0 of 402 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/402 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_minq2_minq2_spot_check.json |
| min_trades_floor | INFO | 402 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.051 | 0.28 | 402 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.274 | -0.006 | 402 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.424 | -0.197 | 402 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.466 | -0.179 | 402 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.51 | -0.21 | 402 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_minq2_minq2_grid_auto.json._

### output_icg_minq3_minq3

**Configuration:** P4_min_consecutive_quarters=3, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.084** (is_sharpe 0.259, 385 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 385 of 385 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 385 | breakeven_plus_trail | 0.259 | -0.084 |
| p7_11 | p7=11 p8=5 | 72 | breakeven_plus_trail | -0.213 | -1.024 |
| p7_14 | p7=14 p8=5 | 63 | breakeven_plus_trail | -0.103 | -0.951 |
| p7_5 | p7=5 p8=5 | 176 | breakeven_plus_trail | 0.197 | -0.308 |
| p8_6 | p7=3 p8=6 | 381 | breakeven_plus_trail | 0.237 | -0.108 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=3 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200 -> output_icg_minq3_minq3_grid_auto.json; free levels reproduction-gated -> output_icg_minq3_minq3_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=3 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_minq3_minq3_spot_check.json; precompute_dir institutional_persi |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_minq3_minq3_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_minq3_minq3_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 9240 IS rows (9240 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.084 is_sharpe 0.259 fires 385 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 9240 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 2be7a5881f975367 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha f02c5c1ec77d | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 9240 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_minq3_minq3_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 385 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.40 (2025Q1) over 5 quarters of 385 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.09 of 385 entries across 136 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.084 vs rank-2 [hybrid_50pct_target] -0.334: margin 0.250 between exits; WARN < 0.05 (selection at noise level); INFO not WARN - rank-1 is_ci_lo -0.084 is not above zero, so nothing is selectable and a narrow margin is not a selection risk (S6-B2581b) |
| empty_signals_share | INFO | 0 of 385 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/385 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_minq3_minq3_spot_check.json |
| min_trades_floor | INFO | 385 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.084 | 0.259 | 385 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.334 | -0.057 | 385 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.463 | -0.169 | 385 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.485 | -0.252 | 385 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.542 | -0.235 | 385 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_minq3_minq3_grid_auto.json._

### output_icg_minq6_minq6

**Configuration:** P4_min_consecutive_quarters=6, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.043** (is_sharpe 0.446, 255 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 255 of 255 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 255 | breakeven_plus_trail | 0.446 | 0.043 |
| p7_11 | p7=11 p8=5 | 83 | breakeven_plus_trail | 0.518 | -0.195 |
| p7_14 | p7=14 p8=5 | 82 | breakeven_plus_trail | 0.521 | -0.195 |
| p7_5 | p7=5 p8=5 | 142 | breakeven_plus_trail | 0.355 | -0.215 |
| p8_6 | p7=3 p8=6 | 241 | breakeven_plus_trail | 0.407 | -0.013 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=6 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200 -> output_icg_minq6_minq6_grid_auto.json; free levels reproduction-gated -> output_icg_minq6_minq6_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=6 growth_lookback_quarters=4 growth_multiple=1.1 ema_span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_minq6_minq6_spot_check.json; precompute_dir institutional_persi |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_minq6_minq6_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_minq6_minq6_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 6120 IS rows (6120 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo 0.043 is_sharpe 0.446 fires 255 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6120 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 925b23baeb1bdb91 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha ebc4be3cb78b | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 6120 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_minq6_minq6_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 255 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.36 (2025Q1) over 5 quarters of 255 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.15 of 255 entries across 99 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo 0.043 vs rank-2 [hybrid_50pct_target] -0.192: margin 0.235 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 255 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/255 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_minq6_minq6_spot_check.json |
| min_trades_floor | INFO | 255 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.043 | 0.446 | 255 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.192 | 0.132 | 255 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.358 | -0.022 | 255 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.463 | -0.185 | 255 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.579 | -0.135 | 255 | time_stop_20d | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_minq6_minq6_grid_auto.json._

### output_icg_lookback8_lookback8

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=8, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.038** (is_sharpe 0.4, 329 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 329 of 329 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 329 | breakeven_plus_trail | 0.4 | 0.038 |
| p7_11 | p7=11 p8=5 | 75 | breakeven_plus_trail | 0.548 | -0.205 |
| p7_14 | p7=14 p8=5 | 70 | breakeven_plus_trail | 0.629 | -0.14 |
| p7_5 | p7=5 p8=5 | 144 | breakeven_plus_trail | 0.269 | -0.291 |
| p8_6 | p7=3 p8=6 | 322 | breakeven_plus_trail | 0.391 | 0.024 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=4 growth_lookback_quarters=8 growth_multiple=1.1 ema_span=200 -> output_icg_lookback8_lookback8_grid_auto.json; free levels reproduction-gated -> output_icg_lookback8_lookback8_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=4 growth_lookback_quarters=8 growth_multiple=1.1 ema_span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_lookback8_lookback8_spot_check.json; precompute_dir institution |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_lookback8_lookback8_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_lookback8_lookback8_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 7896 IS rows (7896 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo 0.038 is_sharpe 0.4 fires 329 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 7896 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | f7f648b920a9141c | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha d04f474f7db5 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 7896 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_lookback8_lookback8_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 329 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.33 (2025Q1) over 5 quarters of 329 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.12 of 329 entries across 123 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo 0.038 vs rank-2 [hybrid_50pct_target] -0.301: margin 0.339 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 329 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/329 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_lookback8_lookback8_spot_check.json |
| min_trades_floor | INFO | 329 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.038 | 0.4 | 329 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.301 | -0.013 | 329 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.316 | -0.073 | 329 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.425 | -0.128 | 329 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.465 | -0.235 | 329 | trailing_15pct | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_lookback8_lookback8_grid_auto.json._

### output_icg_lookback6_lookback6

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=6, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.07** (is_sharpe 0.425, 342 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 342 of 342 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 342 | breakeven_plus_trail | 0.425 | 0.07 |
| p7_11 | p7=11 p8=5 | 66 | breakeven_plus_trail | 0.29 | -0.461 |
| p7_14 | p7=14 p8=5 | 61 | regime_flip | 0.491 | -0.46 |
| p7_5 | p7=5 p8=5 | 169 | breakeven_plus_trail | 0.146 | -0.364 |
| p8_6 | p7=3 p8=6 | 329 | breakeven_plus_trail | 0.391 | 0.027 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=4 growth_lookback_quarters=6 growth_multiple=1.1 ema_span=200 -> output_icg_lookback6_lookback6_grid_auto.json; free levels reproduction-gated -> output_icg_lookback6_lookback6_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=4 growth_lookback_quarters=6 growth_multiple=1.1 ema_span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_lookback6_lookback6_spot_check.json; precompute_dir institution |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_lookback6_lookback6_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_lookback6_lookback6_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 8208 IS rows (8208 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo 0.07 is_sharpe 0.425 fires 342 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 8208 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | ddc7be657aa92805 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha dcf39dfaa0d6 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 8208 cube rows across 2 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_lookback6_lookback6_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 342 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.35 (2025Q1) over 5 quarters of 342 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.10 of 342 entries across 127 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo 0.07 vs rank-2 [regime_flip] -0.14: margin 0.210 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 342 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/342 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_lookback6_lookback6_spot_check.json |
| min_trades_floor | INFO | 342 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.07 | 0.425 | 342 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.14 | 0.272 | 342 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.186 | 0.096 | 342 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.406 | -0.109 | 342 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.448 | 0.085 | 342 | time_stop_10d | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_lookback6_lookback6_grid_auto.json._

### output_icg_lookback3_lookback3

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=3, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.134** (is_sharpe 0.231, 338 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 338 of 338 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 338 | breakeven_plus_trail | 0.231 | -0.134 |
| p7_11 | p7=11 p8=5 | 98 | trailing_10pct | -0.161 | -0.637 |
| p7_14 | p7=14 p8=5 | 93 | trailing_10pct | -0.085 | -0.564 |
| p7_5 | p7=5 p8=5 | 202 | breakeven_plus_trail | 0.144 | -0.336 |
| p8_6 | p7=3 p8=6 | 319 | breakeven_plus_trail | 0.21 | -0.169 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest min_consecutive_quarters=4 growth_lookback_quarters=3 growth_multiple=1.1 ema_span=200 -> output_icg_lookback3_lookback3_grid_auto.json; free levels reproduction-gated -> output_icg_lookback3_lookback3_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional at manifest min_consecutive_quarters=4 growth_lookback_quarters=3 growth_multiple=1.1 ema_span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_lookback3_lookback3_spot_check.json; precompute_dir institution |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_lookback3_lookback3_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 declared knobs read from the environment + consumer lists match the tree |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_lookback3_lookback3_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 8112 IS rows (8112 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.134 is_sharpe 0.231 fires 338 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 8112 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 42d69f3d759d662b | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 75ba284693c3 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 8112 cube rows across 2 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 declared knobs read from the environment + consumer l | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_lookback3_lookback3_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 338 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.39 (2025Q1) over 5 quarters of 338 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.10 of 338 entries across 129 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.134 vs rank-2 [hybrid_50pct_target] -0.285: margin 0.151 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 338 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/338 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_lookback3_lookback3_spot_check.json |
| min_trades_floor | INFO | 338 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.134 | 0.231 | 338 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.285 | -0.006 | 338 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.382 | -0.09 | 338 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.562 | -0.142 | 338 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.604 | -0.358 | 338 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_lookback3_lookback3_grid_auto.json._

### output_icg_mult1.25_mult1.25

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.25, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.297** (is_sharpe 0.092, 301 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 301 of 301 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 301 | breakeven_plus_trail | 0.092 | -0.297 |
| p7_11 | p7=11 p8=5 | 113 | breakeven_plus_trail | -0.168 | -0.793 |
| p7_14 | p7=14 p8=5 | 100 | breakeven_plus_trail | -0.018 | -0.665 |
| p7_5 | p7=5 p8=5 | 174 | breakeven_plus_trail | -0.163 | -0.683 |
| p8_6 | p7=3 p8=6 | 284 | breakeven_plus_trail | 0.076 | -0.329 |

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.25 span=200 -> output_icg_mult1.25_mult1.25_grid_auto.json; free levels reproduction-gated -> output_icg_mult1.25_mult1.25_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_mult1.25_mult1.25_spot_check.json; precompute_dir institutional |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 1 WARN / 0 FAIL / 8 INFO -> output_icg_mult1.25_mult1.25_lenses.json; findings: selection_margin WARN: rank-1 [breakeven_plus_trail] is_ci_lo -0.297 vs rank-2 [hybrid_50pct_target] -0.297: marg |
| 6_post_fix_recheck | DONE | B2580 hand disposition 2026-09-03 13:33: selection_margin WARN rechecked with evidence (#196). MEASURED from output_icg_mult1.25_mult1.25_grid_auto.json: rank-1 [breakeven_plus_trail] is_sharpe 0.092 is_ci_lo -0.297 and rank-2 [hybrid_50pct_target] is_sharpe -0.002 is_ci_lo -0.297 on 7224 IS rows / 301 fires - the WARN is CORRECT: the two exits are not separable. CONSEQUENCE BOUNDED, not dismissed: Step 1 produces a RANKING with no admission (B1608 owner ruling), and this config's rank-1 is_ci_lo is NEGATIVE, so it is not a Step-2 candidate under EITHER ordering - the tie is between two indistinguishably unprofitable exits, and no downstream decision reads the order. No re-run and no parameter change follow. MECHANISM for the next instance (so this is not an executed-once judgment, L752): S6-B2581b - the selection_margin lens takes rank-1 is_ci_lo < 0 as INFO with this reasoning, since nothing is being selected at Step 1 / prior: 1 lens finding(s) need a recheck with evidence (#196): selection_margin WARN |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_mult1.25_mult1.25_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 7224 IS rows (7224 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.297 is_sharpe 0.092 fires 301 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 7224 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 6f9fcbf9c0563678 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 503558bc8249 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 7224 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_mult1.25_mult1.25_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 1 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 301 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.40 (2025Q1) over 5 quarters of 301 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.11 of 301 entries across 123 tickers; WARN > 0.30 |
| selection_margin | WARN **<-- NOT INFO** | rank-1 [breakeven_plus_trail] is_ci_lo -0.297 vs rank-2 [hybrid_50pct_target] -0.297: margin 0.000 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 301 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; MEASURED 0/301 (0.0%) from replay_atr_fallback.json) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_mult1.25_mult1.25_spot_check.json |
| min_trades_floor | INFO | 301 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.297 | 0.092 | 301 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.297 | -0.002 | 301 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.467 | -0.161 | 301 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.659 | -0.398 | 301 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.7 | -0.289 | 301 | time_stop_20d | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_mult1.25_mult1.25_grid_auto.json._

### output_icg_mult1.0_mult1.0

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.0, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.091** (is_sharpe 0.224, 450 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 450 of 450 landed fires covered (coverage 1.0); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 450 | breakeven_plus_trail | 0.224 | -0.091 |
| p7_11 | p7=11 p8=5 | 74 | breakeven_plus_trail | -1.006 | -1.99 |
| p7_14 | p7=14 p8=5 | 51 | breakeven_plus_trail | -1.053 | -2.231 |
| p7_5 | p7=5 p8=5 | 281 | breakeven_plus_trail | 0.176 | -0.234 |
| p8_6 | p7=3 p8=6 | 450 | breakeven_plus_trail | 0.224 | -0.091 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.0 span=200 -> output_icg_mult1.0_mult1.0_grid_auto.json; free levels reproduction-gated -> output_icg_mult1.0_mult1.0_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_mult1.0_mult1.0_spot_check.json; precompute_dir institutional_p |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 9 run: 0 WARN / 0 FAIL / 9 INFO -> output_icg_mult1.0_mult1.0_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (9 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_mult1.0_mult1.0_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 10800 IS rows (10800 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.091 is_sharpe 0.224 fires 450 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 10800 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 52dad07a84554e93 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 903983b77412 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 10800 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_mult1.0_mult1.0_spot_check.json.

**Adversarial lenses (step 5) - 9 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 450 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.37 (2025Q1) over 5 quarters of 450 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.08 of 450 entries across 156 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.091 vs rank-2 [hybrid_50pct_target] -0.257: margin 0.166 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 450 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | INFO | ATR proxy on 0.0% of replayed trades (<= 5%; INFERRED from the empty signals_at_entry share 0.0% (pre-B2574 cube, no replay_atr_fallback.json)) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_mult1.0_mult1.0_spot_check.json |
| min_trades_floor | INFO | 450 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.091 | 0.224 | 450 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.257 | -0.012 | 450 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.501 | -0.235 | 450 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.513 | -0.298 | 450 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.571 | -0.233 | 450 | time_stop_20d | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_mult1.0_mult1.0_grid_auto.json._

### output_icg_span100_span100

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.062** (is_sharpe 0.438, 374 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6b_equivalence_class_check, 7_implement_in_engine, 8_verdict_with_denominators). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | B2574 hand disposition 2026-09-03 07:18: both legs ran; verdict NOT COMPARABLE - 313 of 374 closed trades carry an empty signals_at_entry (S6-B2512 class: the raw vars(t) checkpoint writers bypassed dumps_signals and a datetime.date repr defeated the reader -> {}), so the cube replay priced ATR exits on the 2%-of-price proxy for 83.7% of trades (> the 5% REPLAY_ATR_FALLBACK_WARN_RATE floor); free-level grader coverage 0.1631 vs floor 0.95 -> NOT_COMPARABLE (output_icg_span100_span100_free_levels.json, levels []); the family grid output_icg_span100_span100_grid_auto.json ranks exits priced on proxy ATR and is not comparable across ATR exits / prior: AUTO (B2520/B2569): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.1 span=100 -> output_icg_span100_span100_grid_auto.json; free levels reproduction-gated -> output_icg_span100_span100_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=100; n_sampled 50 seed 42: 49 agree / 0 DISAGREE / 1 skipped; execution failures 0; empty records 43; legs A/B disagree 0; artifact output_icg_span100_span100_spot_check.json |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 1 WARN / 0 FAIL / 7 INFO -> output_icg_span100_span100_lenses.json; findings: empty_signals_share WARN: 313 of 374 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| 6_post_fix_recheck | DONE | B2574 hand disposition 2026-09-03 07:18: empty_signals_share WARN rechecked with evidence (#196) - cause found and fixed two-sided (backtest/util/signals_serde.py _dt_repr_to_iso rescue + backtest/engine/backtest.py closed_trade_rows on all three checkpoint writers; pins test_b2574_*); consequence MEASURED: 313 of 374 closed trades carry an empty signals_at_entry (S6-B2512 class: the raw vars(t) checkpoint writers bypassed dumps_signals and a datetime.date repr defeated the reader -> {}), so the cube replay priced ATR exits on the 2%-of-price proxy for 83.7% of trades (> the 5% REPLAY_ATR_FALLBACK_WARN_RATE floor); engine now persists replay_atr_fallback.json and the battery lens replay_atr_proxy FAILs above the floor; remedy = rerun spec output_audit/b2574_icg_span100_rerun_spec.json queued behind the chain (output_icg_span100_rerun_span100) / prior: 1 lens finding(s) need a recheck with evidence (#196): empty_signals_share WARN |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | N/A | B2574 hand disposition 2026-09-03 07:18: NOT COMPARABLE - a verdict cannot be drawn from this cube (313 of 374 closed trades carry an empty signals_at_entry (S6-B2512 class: the raw vars(t) checkpoint writers bypassed dumps_signals and a datetime.date repr defeated the reader -> {}), so the cube replay priced ATR exits on the 2%-of-price proxy for 83.7% of trades (> the 5% REPLAY_ATR_FALLBACK_WARN_RATE floor)); superseded by the span100 rerun landing (output_icg_span100_rerun_span100), which carries the verdict / prior: AUTO (B2520) VERDICT (denominators from output_icg_span100_span100_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 8976 IS rows (8976 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo 0.062 is_sharpe 0.438 fires 374 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 8976 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | c00c2853c9cb4d33 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 916bac8d6dad | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 8976 cube rows across 2 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 49 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 100, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_span100_span100_spot_check.json.

- 43 sampled trades carried an EMPTY signals_at_entry record (S6-B2512 class) - the re-derivation could still decide them from the precompute, but the engine's own record is missing.

**Adversarial lenses (step 5) - 9 lenses, 2 WARN/FAIL** (step basis: declared --step1-cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 374 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.41 (2025Q1) over 5 quarters of 374 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.08 of 374 entries across 144 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo 0.062 vs rank-2 [hybrid_50pct_target] -0.232: margin 0.294 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | WARN **<-- NOT INFO** | 313 of 374 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| replay_atr_proxy | FAIL **<-- NOT INFO** | NOT COMPARABLE: cube replay used the 2pct-of-price ATR proxy on 83.7% of trades (> 5% engine threshold; INFERRED from the empty signals_at_entry share 83.7% (pre-B2574 cube, no replay_atr_fallback.json)) - the exit ranking is a different population from a cube with signals (S6-B2512 / B2574); re-land under the B2574 engine before comparing |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 49 agree / 0 DISAGREE / 1 skipped in output_icg_span100_span100_spot_check.json |
| min_trades_floor | INFO | 374 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.062 | 0.438 | 374 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.232 | 0.061 | 374 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.472 | -0.175 | 374 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.619 | 0.198 | 374 | r_multiple_2r | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.622 | -0.114 | 374 | fixed_4r_2r | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_span100_span100_grid_auto.json._

### output_icg_minq8_minq8

**Configuration:** P4_min_consecutive_quarters=8, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.054** (is_sharpe 0.452, 256 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 256 of 256 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 256 | breakeven_plus_trail | 0.452 | 0.054 |
| p7_11 | p7=11 p8=5 | 128 | breakeven_plus_trail | 0.679 | 0.118 |
| p7_14 | p7=14 p8=5 | 128 | breakeven_plus_trail | 0.679 | 0.118 |
| p7_5 | p7=5 p8=5 | 155 | breakeven_plus_trail | 0.356 | -0.178 |
| p8_6 | p7=3 p8=6 | 231 | breakeven_plus_trail | 0.42 | -0.005 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest minq=8 lookback=4 multiple=1.1 span=200 -> output_icg_minq8_minq8_grid_auto.json; free levels reproduction-gated -> output_icg_minq8_minq8_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_minq8_minq8_spot_check.json |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 0 WARN / 0 FAIL / 8 INFO -> output_icg_minq8_minq8_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (8 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_minq8_minq8_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 6144 IS rows (6144 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo 0.054 is_sharpe 0.452 fires 256 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6144 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | f21e2c066a5a6718 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha aae8b76ff9a7 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 6144 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_minq8_minq8_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 256 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.36 (2025Q1) over 5 quarters of 256 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.14 of 256 entries across 106 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo 0.054 vs rank-2 [hybrid_50pct_target] -0.264: margin 0.318 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 256 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_minq8_minq8_spot_check.json |
| min_trades_floor | INFO | 256 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.054 | 0.452 | 256 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.264 | 0.05 | 256 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.39 | -0.063 | 256 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.451 | -0.173 | 256 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.495 | -0.123 | 256 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_minq8_minq8_grid_auto.json._

### output_icg_lookback2_lookback2

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=2, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.075** (is_sharpe 0.305, 323 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 323 of 323 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 323 | breakeven_plus_trail | 0.305 | -0.075 |
| p7_11 | p7=11 p8=5 | 138 | breakeven_plus_trail | 0.141 | -0.432 |
| p7_14 | p7=14 p8=5 | 138 | breakeven_plus_trail | 0.141 | -0.432 |
| p7_5 | p7=5 p8=5 | 196 | breakeven_plus_trail | 0.304 | -0.178 |
| p8_6 | p7=3 p8=6 | 295 | breakeven_plus_trail | 0.329 | -0.073 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest minq=4 lookback=2 multiple=1.1 span=200 -> output_icg_lookback2_lookback2_grid_auto.json; free levels reproduction-gated -> output_icg_lookback2_lookback2_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_lookback2_lookback2_spot_check.json |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 0 WARN / 0 FAIL / 8 INFO -> output_icg_lookback2_lookback2_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (8 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_lookback2_lookback2_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 7752 IS rows (7752 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.075 is_sharpe 0.305 fires 323 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 7752 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 89ce3e74927e84f3 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 23649af0cf70 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 7752 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_lookback2_lookback2_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 323 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.40 (2025Q1) over 5 quarters of 323 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.12 of 323 entries across 116 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.075 vs rank-2 [earnings_blackout] -0.309: margin 0.234 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 323 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_lookback2_lookback2_spot_check.json |
| min_trades_floor | INFO | 323 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.075 | 0.305 | 323 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.309 | -0.056 | 323 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.397 | -0.096 | 323 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.447 | -0.136 | 323 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.552 | -0.218 | 323 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_lookback2_lookback2_grid_auto.json._

### output_icg_mult1.5_mult1.5

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.5, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.223** (is_sharpe 0.176, 266 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 266 of 266 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 266 | breakeven_plus_trail | 0.176 | -0.223 |
| p7_11 | p7=11 p8=5 | 147 | breakeven_plus_trail | 0.187 | -0.323 |
| p7_14 | p7=14 p8=5 | 143 | breakeven_plus_trail | 0.24 | -0.274 |
| p7_5 | p7=5 p8=5 | 189 | breakeven_plus_trail | 0.248 | -0.213 |
| p8_6 | p7=3 p8=6 | 240 | breakeven_plus_trail | 0.145 | -0.281 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.5 span=200 -> output_icg_mult1.5_mult1.5_grid_auto.json; free levels reproduction-gated -> output_icg_mult1.5_mult1.5_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_mult1.5_mult1.5_spot_check.json |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 0 WARN / 0 FAIL / 8 INFO -> output_icg_mult1.5_mult1.5_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (8 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_mult1.5_mult1.5_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 6384 IS rows (6384 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.223 is_sharpe 0.176 fires 266 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6384 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 29d723fb616e0433 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 2755df6a3726 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 6384 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_mult1.5_mult1.5_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 266 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.35 (2025Q1) over 5 quarters of 266 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.13 of 266 entries across 115 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.223 vs rank-2 [hybrid_50pct_target] -0.382: margin 0.159 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 266 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_mult1.5_mult1.5_spot_check.json |
| min_trades_floor | INFO | 266 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.223 | 0.176 | 266 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.382 | -0.077 | 266 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.445 | -0.135 | 266 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.631 | -0.381 | 266 | trailing_15pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.67 | -0.399 | 266 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_mult1.5_mult1.5_grid_auto.json._

### output_icg_span150_span150

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.11** (is_sharpe 0.24, 371 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 371 of 371 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 371 | breakeven_plus_trail | 0.24 | -0.11 |
| p7_11 | p7=11 p8=5 | 75 | breakeven_plus_trail | -0.078 | -0.837 |
| p7_14 | p7=14 p8=5 | 68 | breakeven_plus_trail | -0.064 | -0.848 |
| p7_5 | p7=5 p8=5 | 173 | breakeven_plus_trail | 0.15 | -0.357 |
| p8_6 | p7=3 p8=6 | 367 | breakeven_plus_trail | 0.217 | -0.136 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520/B2569): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.1 span=150 -> output_icg_span150_span150_grid_auto.json; free levels reproduction-gated -> output_icg_span150_span150_free_levels.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=150; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_span150_span150_spot_check.json |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 0 WARN / 0 FAIL / 8 INFO -> output_icg_span150_span150_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (8 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_span150_span150_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 8904 IS rows (8904 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.11 is_sharpe 0.24 fires 371 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 8904 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 7ca27ece4c312eed | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 9fe8cf55046c | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 8904 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 150, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_span150_span150_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 371 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.39 (2025Q1) over 5 quarters of 371 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.08 of 371 entries across 137 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.11 vs rank-2 [hybrid_50pct_target] -0.305: margin 0.195 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 371 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_span150_span150_spot_check.json |
| min_trades_floor | INFO | 371 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.11 | 0.24 | 371 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.305 | -0.026 | 371 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.441 | -0.143 | 371 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.52 | -0.207 | 371 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.574 | -0.338 | 371 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_span150_span150_grid_auto.json._

### output_icg_span50_span50

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.067** (is_sharpe 0.288, 405 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 405 of 405 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 405 | breakeven_plus_trail | 0.288 | -0.067 |
| p7_11 | p7=11 p8=5 | 88 | breakeven_plus_trail | -0.028 | -0.811 |
| p7_14 | p7=14 p8=5 | 74 | breakeven_plus_trail | 0.052 | -0.772 |
| p7_5 | p7=5 p8=5 | 204 | breakeven_plus_trail | 0.194 | -0.313 |
| p8_6 | p7=3 p8=6 | 401 | breakeven_plus_trail | 0.266 | -0.092 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.1 span=50 -> output_icg_span50_span50_grid_auto.json; graded 24 exits on 9720 IS rows (9720 total, holdout rows 0); best breakeven_plus_trail is_ci_lo -0.067 is_sharpe 0.288 fires 405; wrote C:\Users\jeetm\Github\s |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=50; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_span50_span50_spot_check.json |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 0 WARN / 0 FAIL / 8 INFO -> output_icg_span50_span50_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (8 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_span50_span50_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 9720 IS rows (9720 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.067 is_sharpe 0.288 fires 405 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 9720 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | ca58e55236f09341 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha e6fb62a60c58 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence) / run_wave verified 9720 cube rows across 1 leg(s | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 50, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_span50_span50_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 405 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.40 (2025Q1) over 5 quarters of 405 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.08 of 405 entries across 148 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.067 vs rank-2 [hybrid_50pct_target] -0.344: margin 0.277 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 405 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_span50_span50_spot_check.json |
| min_trades_floor | INFO | 405 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.067 | 0.288 | 405 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.344 | -0.071 | 405 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.455 | -0.061 | 405 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.495 | -0.205 | 405 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.586 | -0.282 | 405 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_span50_span50_grid_auto.json._

### output_icg_span20_span20

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.015** (is_sharpe 0.3, 531 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 531 of 531 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 531 | breakeven_plus_trail | 0.3 | -0.015 |
| p7_11 | p7=11 p8=5 | 146 | breakeven_plus_trail | -0.15 | -0.792 |
| p7_14 | p7=14 p8=5 | 121 | breakeven_plus_trail | -0.033 | -0.714 |
| p7_5 | p7=5 p8=5 | 288 | breakeven_plus_trail | 0.075 | -0.379 |
| p8_6 | p7=3 p8=6 | 525 | breakeven_plus_trail | 0.286 | -0.031 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.1 span=20 -> output_icg_span20_span20_grid_auto.json; graded 24 exits on 12744 IS rows (12744 total, holdout rows 0); best breakeven_plus_trail is_ci_lo -0.015 is_sharpe 0.3 fires 531; wrote C:\Users\jeetm\Github\s |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=20; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_span20_span20_spot_check.json |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 0 WARN / 0 FAIL / 8 INFO -> output_icg_span20_span20_lenses.json |
| 6_post_fix_recheck | N/A | no lens finding (8 lenses, 0 WARN / 0 FAIL) -> nothing to recheck; N/A on evidence |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_span20_span20_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 12744 IS rows (12744 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.015 is_sharpe 0.3 fires 531 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 12744 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe |  | PASS | absent = the abandoned A-C chunk universe (L445) |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 20, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_span20_span20_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 0 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 531 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.36 (2025Q1) over 5 quarters of 531 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.08 of 531 entries across 148 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.015 vs rank-2 [hybrid_50pct_target] -0.231: margin 0.216 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 531 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_span20_span20_spot_check.json |
| min_trades_floor | INFO | 531 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.015 | 0.3 | 531 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.231 | 0.013 | 531 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.282 | 0.068 | 531 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.424 | -0.155 | 531 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.526 | -0.262 | 531 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_span20_span20_grid_auto.json._

### output_icg_span9_span9

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.167** (is_sharpe 0.489, 609 fires, exit regime_flip). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 609 of 609 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 609 | regime_flip | 0.489 | 0.167 |
| p7_11 | p7=11 p8=5 | 176 | breakeven_plus_trail | 0.041 | -0.528 |
| p7_14 | p7=14 p8=5 | 145 | regime_flip | 0.206 | -0.474 |
| p7_5 | p7=5 p8=5 | 340 | regime_flip | 0.253 | -0.181 |
| p8_6 | p7=3 p8=6 | 603 | regime_flip | 0.473 | 0.149 |

**Completeness: 9 of 9 steps closed** (6 DONE with evidence, 3 N/A with a reason: 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2520): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.1 span=9 -> output_icg_span9_span9_grid_auto.json; graded 24 exits on 14616 IS rows (14616 total, holdout rows 0); best regime_flip is_ci_lo 0.167 is_sharpe 0.489 fires 609; wrote C:\Users\jeetm\Github\stock-pic / prior: family institutional_committed_growth_long: manifest arms[0] lacks ['min_consecutive_quarters', 'growth_lookback_quarters', 'growth_multiple'] (neither the INST_*/STRAT_EMA_SPAN env keys nor the plain keys) (fail closed, L642) |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS / battery re-run 2026-09-02 11:01: DONE - AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2520): spot_check_institutional --n 50 at manifest span=9; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 0; legs A/B disagree 0; artifact output_icg_span9_span9_spot_check.json / prior: family institutional_committed_growth_long: manifest arms[0] lacks ['min_consecutive_quarters', 'growth_lookback_quarters', 'growth_multiple'] (neither the INST_*/STRAT_EMA_SPAN env keys nor the plain keys) (fail closed, L642) |
| 5_adversarial_lens_review | DONE | AUTO (B2520): lenses 8 run: 1 WARN / 0 FAIL / 7 INFO -> output_icg_span9_span9_lenses.json; findings: spot_check_disagreements WARN: no spot-check artifact - step 4 produced nothing to read / battery re-run 2026-09-02 11:01: DONE - AUTO (B2520): lenses 8 run: 1 WARN / 0 FAIL / 7 INFO -> output_icg_span9_span9_lenses.json; findings: selection_margin WARN: rank-1 [regime_flip] is_ci_lo 0.167 vs rank-2 [breakeven_plus_trail] 0.134: margin 0.033 b |
| 6_post_fix_recheck | N/A | DISPOSITIONED B2540 (human, with evidence): N/A on evidence, not waived. The single lens finding is selection_margin WARN - rank-1 regime_flip is_ci_lo 0.167 against rank-2 breakeven_plus_trail 0.134, a margin of 0.033 - and S6-B2409 (owner ruling 2026-08-30) RETIRED the 0.333 selection-noise floor and the ROBUST/PROVISIONAL split in their entirety, so margin is a REPORTED number that gates nothing. There is no fix to re-derive and therefore no recheck to run; the same disposition on the same reasoning was recorded for output_b2174_sw20_sw20. The margin is carried into the landing report so the owner sees it rather than having it disappear into an N/A. Prior row: 1 lens finding(s) need a recheck with evidence (#196): selection_margin WARN / prior: 1 lens finding(s) need a recheck with evidence (#196): spot_chec |
| 6b_equivalence_class_check | N/A | 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence / prior: family institutional_committed_growth_long: manifest arms[0] lacks ['min_consecutive_quarters', 'growth_lookback_quarters', 'growth_multiple'] (neither the INST_*/STRAT_EMA_SPAN env keys nor the plain keys) (fail closed, L642) |
| 7_implement_in_engine | N/A | Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) / prior: family institutional_committed_growth_long: manifest arms[0] lacks ['min_consecutive_quarters', 'growth_lookback_quarters', 'growth_multiple'] (neither the INST_*/STRAT_EMA_SPAN env keys nor the plain keys) (fail closed, L642) |
| 8_verdict_with_denominators | DONE | AUTO (B2520) VERDICT (denominators from output_icg_span9_span9_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 14616 IS rows (14616 cube rows, 0 holdout rows); rank-1 [regime_flip] is_ci_lo 0.167 is_sharpe 0.489 fires 609 - Step-1: ranking only, no admission (B1608) / prior: no grid artifact - step 2 produced nothing to derive a verdict from (family institutional_committed_growth_long: manifest arms[0] lacks ['min_consecutive_quarters', 'growth_lookback_quarters', 'growth_multiple'] (neither the INST_*/STRAT_EMA_SPAN env keys nor the plain keys) (fail closed, L642)) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 14616 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 9, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_span9_span9_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 1 WARN/FAIL** (step basis: declared --step1-cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 609 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.34 (2025Q1) over 5 quarters of 609 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.09 of 609 entries across 148 tickers; WARN > 0.30 |
| selection_margin | WARN **<-- NOT INFO** | rank-1 [regime_flip] is_ci_lo 0.167 vs rank-2 [breakeven_plus_trail] 0.134: margin 0.033 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 609 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_span9_span9_spot_check.json |
| min_trades_floor | INFO | 609 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.167 | 0.489 | 609 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | 0.134 | 0.423 | 609 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.068 | 0.161 | 609 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.146 | 0.252 | 609 | time_stop_10d | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.274 | -0.024 | 609 | class_time_stop | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_span9_span9_grid_auto.json._

### output_icg_cfg1

**Configuration:** P4_min_consecutive_quarters=4, P5_growth_lookback_quarters=4, P6_growth_multiple=1.1, P9_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.087** (is_sharpe 0.263, 373 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**FREE-LEVEL GRADES (B2569, reproduction-gated every landing):** reproduction 350 of 373 landed fires covered (coverage -); IS window only, holdout never read (grade_free_levels_institutional).

| level | knobs | IS fires | selected exit | is_sharpe | is_ci_lo |
|---|---|---|---|---|---|
| baseline_p7_3 | p7=3 p8=5 | 350 | breakeven_plus_trail | 0.312 | -0.043 |
| p7_11 | p7=11 p8=5 | 65 | breakeven_plus_trail | -0.161 | -0.993 |
| p7_14 | p7=14 p8=5 | 56 | breakeven_plus_trail | -0.04 | -0.911 |
| p7_5 | p7=5 p8=5 | 159 | breakeven_plus_trail | 0.274 | -0.251 |
| p8_6 | p7=3 p8=6 | 346 | breakeven_plus_trail | 0.29 | -0.068 |

**Completeness: 9 of 9 steps closed** (8 DONE with evidence, 1 N/A with a reason: 6b_equivalence_class_check). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | output_audit/output_icg_cfg1_grid_auto.json - roster_core.evaluate per exit (24 exits, n=373 each), config IS production (P4=4 P5=4 P6=1.10 P9=200, the baseline); best breakeven_plus_trail is_sharpe 0.263 is_ci_lo -0.087; written under the B2505 contract keys / battery re-run 2026-09-02 07:45: DONE - AUTO (B2520): grade_institutional_config at manifest minq=4 lookback=4 multiple=1.1 span=200 -> output_icg_cfg1_grid_auto.json; graded 24 exits on 8952 IS rows (8952 total, holdout rows 0); best breakeven_plus_trail is_ci_lo -0.087 is_sharpe 0.263 fires 373; wrote C:\Users\jeetm\Github\s |
| 3_outlier_discrepancy_sweep | DONE | fresh sweep: 0 dup (ticker,entry,exit) rows (measured 0); pnl range [-50.24, 108.17] pct, 0 beyond winsorize 300 (battery M5); every one of 24 exits carries exactly 373==373 rows (uniform 373) / battery re-run 2026-09-02 07:45: DONE - AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | 50-trade gate re-derivation from signals_at_entry (random_state=42): 45 of 50 reproduce the OR gate; the 5 failures widened to the FULL population = 23 of 373 EMPTY signals dicts, exactly the 23 trades closed pre-kill and restored across the resume boundary -> S6-B2512 (UNKNOWN - RCA NEEDED, 3 mechanisms refuted by probes). EMA leg not re-derived (engine-computed; population cross-validated at B2504) / battery re-run 2026-09-02 07:45: DONE - AUTO (B2520): spot_check_institutional --n 50 at manifest span=200; n_sampled 50 seed 42: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; empty records 6; legs A/B disagree 0; artifact output_icg_cfg1_spot_check.json |
| 5_adversarial_lens_review | DONE | the spot-check anomaly was hunted adversarially: hypotheses tested and REFUTED by execution - open-book restore round-trips 816 keys; kill-era flush shape round-trips 4/4 keys; closed-trade parser delegates to signals_serde (B1260). Cause filed UNKNOWN not guessed (S6-B2512). Also: M10 gate_receipt SKIP identified as a launch-path finding (run_phase1a direct, not run_wave) - closed for the NEXT launch (b2207a goes through run_wave, receipt verified present) / battery re-run 2026-09-02 07:45: DONE - AUTO (B2520): lenses 8 run: 1 WARN / 0 FAIL / 7 INFO -> output_icg_cfg1_lenses.json; findings: empty_signals_share WARN: 23 of 373 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| 6_post_fix_recheck | DONE | re-check RUN, not waived (#196): enumerated this cycle's fixes - B2490/B2492/B2502 (cap gates on active hours; guard/kill accounting only), B2498 (prescreen fallback jaccard), B2505 (Table D axis registry) - and swept for shipped conclusions resting on pre-fix behaviour. The only cube-coupled claim is the resume manifest's cube-equivalence-at-defaults, held by test_b2484 (span default 200 pinned) and the completed run's M1-M7 checks; the grid/battery/free-level artifacts read pnl+hold, which no fix in the cycle touches. RESULT: 0 shipped conclusions require re-derivation - a re-check that finds nothing is a finding, not a skip (B2460). / battery re-run 2026-09-02 07:45: OPEN - 1 lens finding(s) need a recheck with evidence (#196): empty_signals_share WARN |
| 6b_equivalence_class_check | N/A | N/A (B2520 migration, L721): no equivalence classes exist to carry - baseline config carried no subset-safe equivalence classes to propagate - class_size=1 recorded on every ranked row in the grid artifact; the free-level re-scores that DO carry classes live in output_audit/b2504_free_levels_institutional.json (S6-B2501, graded separately) / battery re-run 2026-09-02 07:45: N/A - 1 combination per cube (the swept parameters live in the precompute the engine consumed); equivalence collapse requires >= 2 combinations - N/A on evidence |
| 7_implement_in_engine | DONE | trivially satisfied for a BASELINE: the config IS production (every value the built-in default), so the engine already implements it; battery step7_engine_implemented PASS exit 0 / battery re-run 2026-09-02 07:45: N/A - Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: 4 of 4 swept parameters anchored in the engine path (precompute INST_* x3 + screener STRAT_EMA_SPAN; code-presence check) |
| 8_verdict_with_denominators | DONE | VERDICT: baseline Step-1 reference measured - best of 24 exits (breakeven_plus_trail) at is_sharpe 0.263 / is_ci_lo -0.087 on n=373 IS fires over 200 tickers x 1 year; 0 of 24 exits reach a positive ci_lo; this is the comparison bar for the 16 variant configs, per the ruled Step-1 rank-only design (no gates, B1608) / battery re-run 2026-09-02 07:45: DONE - AUTO (B2520) VERDICT (denominators from output_icg_cfg1_grid_auto.json): 24 of 24 exits RANKED at min-trades >= 10 on 8952 IS rows (8952 cube rows, 0 holdout rows); rank-1 [breakeven_plus_trail] is_ci_lo -0.087 is_sharpe 0.263 fires 373 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 8952 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit\_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | af35ab7fc09b5b2b | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-01 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | no gate_receipt.json - cube predates B2169 or was launched A | SKIP **<-- NOT PASS** | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | 4 of 4 swept parameters anchored in the engine path (precomp | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 42 at this config's own parameters (ema_span 200, min_committed_growth 3, fallback_min_increased 5) by scripts/spot_check_institutional.py (B2520).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_icg_cfg1_spot_check.json.

- 6 sampled trades carried an EMPTY signals_at_entry record (S6-B2512 class) - the re-derivation could still decide them from the precompute, but the engine's own record is missing.

**Adversarial lenses (step 5) - 8 lenses, 1 WARN/FAIL** (step basis: manifest window.end 2025-05-05 <= HO_START 2025-05-05 -> Step-1 cube; family institutional_committed_growth_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 373 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.40 (2025Q1) over 5 quarters of 373 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.09 of 373 entries across 133 tickers; WARN > 0.30 |
| selection_margin | INFO | rank-1 [breakeven_plus_trail] is_ci_lo -0.087 vs rank-2 [hybrid_50pct_target] -0.285: margin 0.198 between exits; WARN < 0.05 (selection at noise level) |
| empty_signals_share | WARN **<-- NOT INFO** | 23 of 373 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_icg_cfg1_spot_check.json |
| min_trades_floor | INFO | 373 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 24 exits enumerated (population field `per_exit`).
- **0 (0%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 24 graded and ranked, collapsing to 1 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 1 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.087 | 0.263 | 373 | breakeven_plus_trail | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 2 | -0.285 | -0.001 | 373 | hybrid_50pct_target | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 3 | -0.462 | -0.161 | 373 | trailing_10pct | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 4 | -0.53 | -0.293 | 373 | earnings_blackout | 1 | min_committed_growth=3 fallback_min_increased=5 |
| 5 | -0.549 | -0.137 | 373 | regime_flip | 1 | min_committed_growth=3 fallback_min_increased=5 |

_Top 5 of the ranking; the full list is in output_audit/output_icg_cfg1_grid_auto.json._

### output_b2174_sw20_sw20

**Configuration:** P1_swing_length=20, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.196** (is_sharpe 0.282, 79 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=20 span=200 -> output_b2174_sw20_sw20_grid_auto.json / battery re-run 2026-09-01 20:08: DONE - AUTO (B2177): graded at manifest swing=20 span=200 -> output_b2174_sw20_sw20_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS / prior: PENDING-WAVE-REVIEW (b2174_sw20): the wave-level review batch performs this step across all arms together / battery re-run 2026-09-01 20:08: DONE - AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; M2_exits_per_entry_vs_registry=PASS; M3_fill_date=PASS; M4_holdout_touch=PASS; M5_pnl_integrity=PASS; M7_degraded_exits=PASS |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2174_sw20_sw20_spot_check.json / battery re-run 2026-09-01 20:08: DONE - AUTO (B2177): spot_check_trades --n 50 at manifest swing=20 span=200; n_sampled 50 seed 20260816: 50 agree / 0 DISAGREE / 0 skipped; execution failures 0; artifact output_b2174_sw20_sw20_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2174_sw20): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=218, NO_EXIT_SELECTABLE=82. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. / battery re-run 2026-09-01 20:08: DONE - AUTO (B2520): lenses 8 run: 1 WARN / 0 FAIL / 7 INFO -> output_b2174_sw20_sw20_lenses.json; findings: selection_margin WARN: rank-1 [close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 -> hybrid_50p |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2174_sw20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. / battery re-run 2026-09-01 20:08: OPEN - 1 lens finding(s) need a recheck with evidence (#196): selection_margin WARN |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 10 ranked outcome classes carry 22 parameter combinations; 89 distinct outcome classes among 300 combinations enumerated in output_b2174_sw20_sw20_grid_auto.json / prior: PENDING-WAVE-REVIEW (b2174_sw20): the wave-level review batch performs this step across all arms together / battery re-run 2026-09-01 20:08: DONE - AUTO (B2192): the grader collapses identical outcomes - 10 ranked outcome classes carry 22 parameter combinations; 89 distinct outcome classes among 300 combinations enumerated in output_b2174_sw20_sw20_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2174_sw20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. / battery re-run 2026-09-01 20:08: N/A - Step-1 ranking cube; admission happens at Step 2; nothing to implement. Engine check PASS: exit 0; PASS - every swept parameter reaches the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2174_sw20): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=218, NO_EXIT_SELECTABLE=82. No ranking, no qualifier, no admission is derivable from this config. / battery re-run 2026-09-01 20:08: DONE - AUTO (B2520) VERDICT (denominators from output_b2174_sw20_sw20_grid_auto.json): 300 combinations enumerated: 218 BELOW_POWER_FLOOR, 82 NO_EXIT_SELECTABLE; rank-1 [close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 -> hybrid_50pct_target] is_ci_lo -0.196 is_sharpe 0.282 fires 79 - Step-1: ranking only, no admission (B1608) |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2712 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | bb3984d740f34536 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-22 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 619049ff06b5 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 20, ema_span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2174_sw20_sw20_spot_check.json.

**Adversarial lenses (step 5) - 8 lenses, 1 WARN/FAIL** (step basis: declared --step1-cube; family smc_breaker_block_long)

| lens | level | evidence |
|---|---|---|
| holdout_untouched | INFO | 0 of 113 entries at/after HO_START 2025-05-05 (Step-1 cube: any touch is a leak, B1718 class) |
| period_concentration | INFO | max quarter share 0.32 (2024Q3) over 5 quarters of 113 entries; WARN > 0.5 |
| ticker_concentration | INFO | top-5 tickers carry 0.16 of 113 entries across 83 tickers; WARN > 0.30 |
| selection_margin | WARN **<-- NOT INFO** | rank-1 [close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 -> hybrid_50pct_target] is_ci_lo -0.196 vs rank-2 [close_mitigation=False break_pct_max=None age_bars_max=None tail_n=2 -> hybrid_50pct_target] -0.198: margin 0.002 between outcome classes; WARN < 0.05 (selection at noise level) |
| empty_signals_share | INFO | 0 of 113 trade_log rows carry an empty signals_at_entry (S6-B2512 class) |
| direction_consistency | INFO | directions ['long'] (one strategy, one direction expected) |
| spot_check_disagreements | INFO | 50 agree / 0 DISAGREE / 0 skipped in output_b2174_sw20_sw20_spot_check.json |
| min_trades_floor | INFO | 113 distinct entries; the live gates need holdout >= 15 and full-period >= 75 (applied by the grader, not here) |

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **82 (27%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 218 graded and ranked, collapsing to 89 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 22 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.196 | 0.282 | 79 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 |
| 2 | -0.198 | 0.275 | 76 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=2 |
| 3 | -0.205 | 0.274 | 78 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=3 |
| 4 | -0.236 | 0.286 | 66 | hybrid_50pct_target | 4 | close_mitigation=False break_pct_max=None age_bars_max=180 tail_n=20 |
| 5 | -0.24 | 0.268 | 65 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2174_sw20_sw20_grid_auto.json._

### output_b2399_step2_sw50sp50_step2_sw50sp50

**Configuration:** P1_swing_length=50, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.026** (is_sharpe 0.145, 325 fires, exit trailing_15pct). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (8 DONE with evidence, 1 N/A with a reason: 6_post_fix_recheck). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=50 span=50 -> output_b2399_step2_sw50sp50_step2_sw50sp50_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2399_step2_sw50sp50_step2_sw50sp50_spot_check.json |
| 5_adversarial_lens_review | DONE | S6-B2443 PILOT (owner-approved). 6 lenses run against the grid artifact. MATERIAL FINDING (lens 1): psr is INERT AS A DISCRIMINATOR on this config - of 198 graded rows the value is computable on only 85 and ABSENT on 113, and where computable it takes exactly TWO values, 0.9893 and 1.0, BOTH above the 0.95 bar. All 113 psr-gate failures are absence, not a low value (metrics.py:521/540 return None on insufficient_sample / denominator_invalid). So psr never rejects a row on significance - it functions as a SECOND SAMPLE-SIZE gate overlapping min_trades. It IS fail-closed on absence (roster_core.py:249), which is correct. CONSEQUENCE: after owner ruling D2 removed BH-FDR at the grid stage and S6-B2409 retired the selection-noise floor, psr was the last significance-style control - and it cannot discriminate, so this 300-combination search has NO effective multiplicity control. Lens 2: HO/IS ratio 2.59x (1.152 vs 0.445) on 41 holdout trades with BOTH ci_lo below zero (-0.415 HO, -0.385 IS) - the L636 shape. Lens 3: exit selection is IN-SAMPLE (select_exit calls in_sample()) - no leak. Lens 4: exit time_stop_10d, 21 effective exits, 2 collapsed. Lens 5: the '3 qualifiers' are TWO distinct outcomes - tail_n 10 and 20 are byte-identical (1.152/41/180), tail_n 2 is weaker (1.035/35/150); the owner-retained tail_n=20 is in the stronger pair. Lens 6: 300 enumerated / 198 graded / 3 PASS rows / 2 distinct outcomes. |
| 6_post_fix_recheck | N/A | S6-B2443 PILOT: step 5 surfaced findings but NO CODE FIX - psr and the gate behave exactly as designed (fail-closed on absence); the finding is about what the gate can DISCRIMINATE, which is an interpretation and a programme-design question, not a defect to patch. Nothing was changed, so there is nothing to re-run. N/A is recorded rather than DONE because claiming a recheck that did not happen is the exact class this pilot exists to expose. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 21 combos carried across 104 distinct outcome classes in output_b2399_step2_sw50sp50_step2_sw50sp50_grid_auto.json |
| 7_implement_in_engine | DONE | S6-B2443 PILOT: EXECUTED scripts/verify_engine_implemented.py - exit 0, 'PASS - every swept parameter reaches the engine', 6 of 6 ENGINE-IMPLEMENTED (P1 swing_length, P2 close_mitigation, P3 tail_n, P4 age_bars_max, P5 break_pct_max, P6 ema span), 0 GRADER-ONLY. |
| 8_verdict_with_denominators | DONE | S6-B2443 PILOT, re-derived from the grid artifact this batch: 300 combinations enumerated; 102 cut BEFORE grading (29 NO_EXIT_SELECTABLE + 73 BELOW_POWER_FLOOR), so the HONEST DENOMINATOR is 198 graded; 3 PASS rows = 2 DISTINCT OUTCOMES = 1 distinct parameter set ignoring tail_n. FAIL attribution over the 195 FAIL rows (a row can fail several): pooled_sharpe 179, psr 113 (all by ABSENCE), min_trades_full_period 28, min_trades_holdout 23, sortino 20, profit_factor 5. Verdict: ONE qualifying parameter set of 198 graded, carried by 41 holdout trades, with the multiplicity caveat from lens 1 attached. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 10488 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | MSFT, GOOGL, TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/r5_universe_544.txt (verifier is non- | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 1888ec463d863cf0 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2022-05-06 .. 2026-04-30 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 3120 entries past 2025-05-05 (not declared a Step-1 cube | SKIP **<-- NOT PASS** | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 77d9da3e802a | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 19 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 50, ema_span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2399_step2_sw50sp50_step2_sw50sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **29 (10%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 271 graded and ranked, collapsing to 104 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 21 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.026 | 0.145 | 325 | trailing_15pct | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=2 sortino=1.737 psr=1.0 profit_factor=2.223 payoff=2.73 expectancy=6.2514 win_rate=0.449 p=0.0077498330916893265 gates={'pooled_sharpe': False, 'profit_factor': True, 'sortino': True, 'psr': True, 'min_trades_holdout': True, 'min_trades_full_period': True} gates_passed=5 |
| 2 | -0.047 | 0.303 | 148 | hybrid_50pct_target | 4 | close_mitigation=True break_pct_max=0.03 age_bars_max=250 tail_n=20 sortino=999.0 psr=1.0 profit_factor=2.328 payoff=1.04 expectancy=4.1921 win_rate=0.69 p=0.023615591200037936 gates={'pooled_sharpe': False, 'profit_factor': True, 'sortino': True, 'psr': True, 'min_trades_holdout': True, 'min_trades_full_period': True} gates_passed=5 |
| 3 | -0.047 | 0.186 | 339 | hybrid_50pct_target | 2 | close_mitigation=False break_pct_max=0.03 age_bars_max=None tail_n=20 sortino=2.052 psr=1.0 profit_factor=2.12 payoff=0.91 expectancy=3.0907 win_rate=0.7 p=0.004641593196346641 gates={'pooled_sharpe': False, 'profit_factor': True, 'sortino': True, 'psr': True, 'min_trades_holdout': True, 'min_trades_full_period': True} gates_passed=5 |
| 4 | -0.047 | 0.186 | 338 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.03 age_bars_max=None tail_n=5 sortino=2.017 psr=1.0 profit_factor=2.092 payoff=0.91 expectancy=3.0471 win_rate=0.697 p=0.005578254781933748 gates={'pooled_sharpe': False, 'profit_factor': True, 'sortino': True, 'psr': True, 'min_trades_holdout': True, 'min_trades_full_period': True} gates_passed=5 |
| 5 | -0.047 | 0.175 | 397 | hybrid_50pct_target | 2 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=20 sortino=2.348 psr=1.0 profit_factor=2.016 payoff=1.0 expectancy=3.1091 win_rate=0.669 p=0.0019491173483872398 gates={'pooled_sharpe': False, 'profit_factor': True, 'sortino': True, 'psr': True, 'min_trades_holdout': True, 'min_trades_full_period': True} gates_passed=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2399_step2_sw50sp50_step2_sw50sp50_grid_auto.json._

### output_b2197_sw50sp150_sw50sp150

**Configuration:** P1_swing_length=50, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.437** (is_sharpe 3.083, 10 fires, exit fixed_4r_2r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=50 span=150 -> output_b2197_sw50sp150_sw50sp150_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw50sp150_sw50sp150_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp150): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=110, NO_EXIT_SELECTABLE=190. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 14 combos carried across 44 distinct outcome classes in output_b2197_sw50sp150_sw50sp150_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp150): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=110, NO_EXIT_SELECTABLE=190. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1248 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | ece4286154f597a8 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-10 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 2a8e74ff0980 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 50, ema_span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp150_sw50sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **190 (63%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 110 graded and ranked, collapsing to 44 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 14 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.437 | 3.083 | 10 | fixed_4r_2r | 5 | close_mitigation=True break_pct_max=0.02 age_bars_max=250 tail_n=20 |
| 2 | -0.164 | 1.083 | 38 | chandelier_3x | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=2 |
| 3 | -0.205 | 2.057 | 27 | r_multiple_3r | 1 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=2 |
| 4 | -0.205 | 0.932 | 43 | chandelier_3x | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=3 |
| 5 | -0.218 | 1.885 | 30 | r_multiple_3r | 1 | close_mitigation=False break_pct_max=0.03 age_bars_max=None tail_n=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp150_sw50sp150_grid_auto.json._

### output_b2197_sw50sp100_sw50sp100

**Configuration:** P1_swing_length=50, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.023** (is_sharpe 2.292, 25 fires, exit r_multiple_3r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=50 span=100 -> output_b2197_sw50sp100_sw50sp100_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw50sp100_sw50sp100_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp100): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 14 combos carried across 42 distinct outcome classes in output_b2197_sw50sp100_sw50sp100_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp100): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1224 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 23e1c38815d3ce10 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 36f18508655c | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 50, ema_span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp100_sw50sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked, collapsing to 42 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 14 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.023 | 2.292 | 25 | r_multiple_3r | 1 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=2 |
| 2 | -0.032 | 2.49 | 21 | r_multiple_3r | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=2 |
| 3 | -0.058 | 2.087 | 28 | r_multiple_3r | 1 | close_mitigation=False break_pct_max=0.03 age_bars_max=None tail_n=2 |
| 4 | -0.077 | 2.229 | 24 | r_multiple_3r | 1 | close_mitigation=True break_pct_max=0.03 age_bars_max=None tail_n=2 |
| 5 | -0.083 | 2.269 | 24 | r_multiple_3r | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp100_sw50sp100_grid_auto.json._

### output_b2197_sw50sp50_sw50sp50

**Configuration:** P1_swing_length=50, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 1.25** (is_sharpe 4.301, 14 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=50 span=50 -> output_b2197_sw50sp50_sw50sp50_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw50sp50_sw50sp50_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp50): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 14 combos carried across 42 distinct outcome classes in output_b2197_sw50sp50_sw50sp50_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp50): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1224 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 328d52d9b5ee41fc | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 7b386d33f75c | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 50, ema_span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp50_sw50sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked, collapsing to 42 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 14 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 1.25 | 4.301 | 14 | time_stop_10d | 1 | close_mitigation=True break_pct_max=0.01 age_bars_max=None tail_n=3 |
| 2 | 1.189 | 3.724 | 19 | time_stop_10d | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=2 |
| 3 | 1.11 | 3.427 | 22 | time_stop_10d | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=3 |
| 4 | 1.044 | 3.929 | 15 | time_stop_10d | 3 | close_mitigation=True break_pct_max=0.01 age_bars_max=None tail_n=20 |
| 5 | 1.013 | 3.26 | 23 | time_stop_10d | 3 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp50_sw50sp50_grid_auto.json._

### output_b2197_sw50sp20_sw50sp20

**Configuration:** P1_swing_length=50, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.93** (is_sharpe 3.915, 14 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=50 span=20 -> output_b2197_sw50sp20_sw50sp20_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw50sp20_sw50sp20_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp20): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 21 combos carried across 41 distinct outcome classes in output_b2197_sw50sp20_sw50sp20_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp20): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1224 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 7aadc0a797c20d13 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 5208475e8330 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 50, ema_span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp20_sw50sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked, collapsing to 41 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 21 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.93 | 3.915 | 14 | time_stop_10d | 2 | close_mitigation=True break_pct_max=0.01 age_bars_max=None tail_n=3 |
| 2 | 0.759 | 3.592 | 15 | time_stop_10d | 3 | close_mitigation=True break_pct_max=0.01 age_bars_max=None tail_n=20 |
| 3 | 0.578 | 2.7 | 24 | time_stop_10d | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=3 |
| 4 | 0.563 | 1.865 | 32 | fixed_4r_2r | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=3 |
| 5 | 0.551 | 1.84 | 32 | fixed_4r_2r | 1 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp20_sw50sp20_grid_auto.json._

### output_b2197_sw50sp9_sw50sp9

**Configuration:** P1_swing_length=50, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.724** (is_sharpe 2.82, 25 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=50 span=9 -> output_b2197_sw50sp9_sw50sp9_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw50sp9_sw50sp9_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp9): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 20 combos carried across 42 distinct outcome classes in output_b2197_sw50sp9_sw50sp9_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw50sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw50sp9): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=100, NO_EXIT_SELECTABLE=200. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1248 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 974453a972160c5f | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-10 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 4104804d27e8 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 50, ema_span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp9_sw50sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked, collapsing to 42 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 20 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.724 | 2.82 | 25 | time_stop_10d | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=3 |
| 2 | 0.661 | 2.706 | 26 | time_stop_10d | 3 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=20 |
| 3 | 0.656 | 1.93 | 33 | fixed_4r_2r | 1 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=3 |
| 4 | 0.597 | 1.851 | 34 | fixed_4r_2r | 3 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=20 |
| 5 | 0.472 | 1.651 | 37 | fixed_4r_2r | 1 | close_mitigation=False break_pct_max=0.03 age_bars_max=None tail_n=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp9_sw50sp9_grid_auto.json._

### output_b2197_sw5sp150_sw5sp150

**Configuration:** P1_swing_length=5, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.019** (is_sharpe 0.508, 76 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=5 span=150 -> output_b2197_sw5sp150_sw5sp150_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw5sp150_sw5sp150_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp150): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 18 combos carried across 132 distinct outcome classes in output_b2197_sw5sp150_sw5sp150_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp150): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6480 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 24d432bb5f0594e3 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 9315cc295ff6 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 5, ema_span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp150_sw5sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 260 graded and ranked, collapsing to 132 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 18 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.019 | 0.508 | 76 | earnings_blackout | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=120 tail_n=5 |
| 2 | 0.007 | 0.394 | 120 | earnings_blackout | 2 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=5 |
| 3 | 0.001 | 0.486 | 77 | earnings_blackout | 2 | close_mitigation=True break_pct_max=0.02 age_bars_max=120 tail_n=20 |
| 4 | -0.01 | 0.458 | 82 | earnings_blackout | 3 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=5 |
| 5 | -0.018 | 0.39 | 109 | earnings_blackout | 1 | close_mitigation=False break_pct_max=0.02 age_bars_max=120 tail_n=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp150_sw5sp150_grid_auto.json._

### output_b2197_sw5sp100_sw5sp100

**Configuration:** P1_swing_length=5, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.027** (is_sharpe 0.513, 77 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=5 span=100 -> output_b2197_sw5sp100_sw5sp100_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw5sp100_sw5sp100_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp100): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 24 combos carried across 132 distinct outcome classes in output_b2197_sw5sp100_sw5sp100_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp100): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6576 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 39ef288d4e4b7204 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 0c3543bd532e | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 5, ema_span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp100_sw5sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 260 graded and ranked, collapsing to 132 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 24 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.027 | 0.513 | 77 | earnings_blackout | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=120 tail_n=5 |
| 2 | 0.009 | 0.491 | 78 | earnings_blackout | 2 | close_mitigation=True break_pct_max=0.02 age_bars_max=120 tail_n=20 |
| 3 | -0.002 | 0.463 | 83 | earnings_blackout | 3 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=5 |
| 4 | -0.017 | 0.439 | 86 | earnings_blackout | 2 | close_mitigation=True break_pct_max=0.02 age_bars_max=180 tail_n=20 |
| 5 | -0.049 | 0.523 | 103 | breakeven_plus_trail | 4 | close_mitigation=True break_pct_max=0.03 age_bars_max=None tail_n=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp100_sw5sp100_grid_auto.json._

### output_b2197_sw5sp50_sw5sp50

**Configuration:** P1_swing_length=5, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.005** (is_sharpe 0.402, 220 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=5 span=50 -> output_b2197_sw5sp50_sw5sp50_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw5sp50_sw5sp50_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp50): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 20 combos carried across 124 distinct outcome classes in output_b2197_sw5sp50_sw5sp50_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp50): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6696 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 8e833d65ab04ee56 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha cff52504e875 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 5, ema_span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp50_sw5sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 255 graded and ranked, collapsing to 124 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 20 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.005 | 0.402 | 220 | breakeven_plus_trail | 2 | close_mitigation=True break_pct_max=None age_bars_max=180 tail_n=20 |
| 2 | -0.017 | 0.402 | 208 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=None age_bars_max=180 tail_n=5 |
| 3 | -0.018 | 0.428 | 178 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=20 |
| 4 | -0.021 | 0.48 | 139 | breakeven_plus_trail | 4 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=3 |
| 5 | -0.022 | 0.392 | 215 | breakeven_plus_trail | 2 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp50_sw5sp50_grid_auto.json._

### output_b2197_sw5sp20_sw5sp20

**Configuration:** P1_swing_length=5, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.005** (is_sharpe 0.49, 140 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=5 span=20 -> output_b2197_sw5sp20_sw5sp20_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw5sp20_sw5sp20_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp20): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 27 combos carried across 125 distinct outcome classes in output_b2197_sw5sp20_sw5sp20_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp20): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6888 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | d002e6ebcff52e16 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 088d72a9e041 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 5, ema_span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp20_sw5sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 255 graded and ranked, collapsing to 125 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 27 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.005 | 0.49 | 140 | breakeven_plus_trail | 4 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=3 |
| 2 | -0.01 | 0.525 | 115 | breakeven_plus_trail | 4 | close_mitigation=True break_pct_max=0.03 age_bars_max=None tail_n=3 |
| 3 | -0.014 | 0.444 | 162 | breakeven_plus_trail | 2 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=5 |
| 4 | -0.023 | 0.419 | 178 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=10 |
| 5 | -0.024 | 0.417 | 181 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp20_sw5sp20_grid_auto.json._

### output_b2197_sw5sp9_sw5sp9

**Configuration:** P1_swing_length=5, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.098** (is_sharpe 0.6, 128 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=5 span=9 -> output_b2197_sw5sp9_sw5sp9_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw5sp9_sw5sp9_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp9): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 20 combos carried across 126 distinct outcome classes in output_b2197_sw5sp9_sw5sp9_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw5sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw5sp9): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 7296 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | e140fe36dbb34674 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha f7a7412523b4 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 5, ema_span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp9_sw5sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 255 graded and ranked, collapsing to 126 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 20 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.098 | 0.6 | 128 | breakeven_plus_trail | 4 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=3 |
| 2 | 0.083 | 0.626 | 105 | breakeven_plus_trail | 4 | close_mitigation=True break_pct_max=0.03 age_bars_max=None tail_n=3 |
| 3 | 0.072 | 0.431 | 287 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=20 |
| 4 | 0.066 | 0.482 | 189 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=10 |
| 5 | 0.064 | 0.456 | 222 | breakeven_plus_trail | 2 | close_mitigation=True break_pct_max=None age_bars_max=180 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp9_sw5sp9_grid_auto.json._

### output_b2197_sw10sp150_sw10sp150

**Configuration:** P1_swing_length=10, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.11** (is_sharpe 0.282, 119 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=10 span=150 -> output_b2197_sw10sp150_sw10sp150_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw10sp150_sw10sp150_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp150): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 20 combos carried across 131 distinct outcome classes in output_b2197_sw10sp150_sw10sp150_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp150): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 4464 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 9175944a65014673 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 8d3036a6aa90 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 10, ema_span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp150_sw10sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 260 graded and ranked, collapsing to 131 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 20 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.11 | 0.282 | 119 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=2 |
| 2 | -0.118 | 0.258 | 135 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=120 tail_n=20 |
| 3 | -0.132 | 0.244 | 134 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=120 tail_n=3 |
| 4 | -0.133 | 0.268 | 115 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=120 tail_n=2 |
| 5 | -0.14 | 0.324 | 177 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp150_sw10sp150_grid_auto.json._

### output_b2197_sw10sp100_sw10sp100

**Configuration:** P1_swing_length=10, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.12** (is_sharpe 0.34, 174 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=10 span=100 -> output_b2197_sw10sp100_sw10sp100_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw10sp100_sw10sp100_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp100): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 19 combos carried across 127 distinct outcome classes in output_b2197_sw10sp100_sw10sp100_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp100): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 4368 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 44ad8d59f1ce7c5e | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha c496ccacc4db | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 10, ema_span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp100_sw10sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 260 graded and ranked, collapsing to 127 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 19 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.12 | 0.34 | 174 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=5 |
| 2 | -0.127 | 0.362 | 154 | breakeven_plus_trail | 3 | close_mitigation=False break_pct_max=None age_bars_max=180 tail_n=20 |
| 3 | -0.131 | 0.337 | 161 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=20 |
| 4 | -0.141 | 0.402 | 124 | breakeven_plus_trail | 3 | close_mitigation=True break_pct_max=None age_bars_max=180 tail_n=20 |
| 5 | -0.141 | 0.344 | 161 | breakeven_plus_trail | 3 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp100_sw10sp100_grid_auto.json._

### output_b2197_sw10sp50_sw10sp50

**Configuration:** P1_swing_length=10, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.042** (is_sharpe 0.422, 156 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=10 span=50 -> output_b2197_sw10sp50_sw10sp50_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw10sp50_sw10sp50_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp50): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 16 combos carried across 128 distinct outcome classes in output_b2197_sw10sp50_sw10sp50_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp50): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=45, ZERO_FIRES=5. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 4392 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 00386e97d634cc7b | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 060907ffb5e9 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 10, ema_span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp50_sw10sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 255 graded and ranked, collapsing to 128 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 16 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.042 | 0.422 | 156 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=10 |
| 2 | -0.042 | 0.419 | 157 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=20 |
| 3 | -0.051 | 0.4 | 172 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=5 |
| 4 | -0.056 | 0.416 | 162 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=10 |
| 5 | -0.059 | 0.421 | 153 | breakeven_plus_trail | 3 | close_mitigation=False break_pct_max=None age_bars_max=180 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp50_sw10sp50_grid_auto.json._

### output_b2197_sw10sp20_sw10sp20

**Configuration:** P1_swing_length=10, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.07** (is_sharpe 0.47, 110 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=10 span=20 -> output_b2197_sw10sp20_sw10sp20_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw10sp20_sw10sp20_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp20): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=259, NO_EXIT_SELECTABLE=41. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 18 combos carried across 129 distinct outcome classes in output_b2197_sw10sp20_sw10sp20_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp20): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=259, NO_EXIT_SELECTABLE=41. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 4512 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 03967e9e33bdcf13 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 7de2dde0f58a | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 10, ema_span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp20_sw10sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **41 (14%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 259 graded and ranked, collapsing to 129 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 18 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.07 | 0.47 | 110 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=10 |
| 2 | -0.07 | 0.466 | 112 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=20 |
| 3 | -0.078 | 0.357 | 102 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=120 tail_n=2 |
| 4 | -0.081 | 0.397 | 156 | breakeven_plus_trail | 3 | close_mitigation=False break_pct_max=None age_bars_max=180 tail_n=20 |
| 5 | -0.084 | 0.344 | 105 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp20_sw10sp20_grid_auto.json._

### output_b2197_sw10sp9_sw10sp9

**Configuration:** P1_swing_length=10, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.014** (is_sharpe 0.714, 68 fires, exit class_time_stop). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=10 span=9 -> output_b2197_sw10sp9_sw10sp9_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw10sp9_sw10sp9_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp9): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=258, NO_EXIT_SELECTABLE=42. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 16 combos carried across 138 distinct outcome classes in output_b2197_sw10sp9_sw10sp9_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw10sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw10sp9): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=258, NO_EXIT_SELECTABLE=42. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 4896 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 08ce25597f8b6119 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 65403ac4ef78 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 10, ema_span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp9_sw10sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **42 (14%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 258 graded and ranked, collapsing to 138 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 16 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.014 | 0.714 | 68 | class_time_stop | 3 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=2 |
| 2 | -0.016 | 0.408 | 204 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=20 |
| 3 | -0.021 | 0.433 | 181 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=10 |
| 4 | -0.023 | 0.402 | 203 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=10 |
| 5 | -0.024 | 0.428 | 183 | breakeven_plus_trail | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp9_sw10sp9_grid_auto.json._

### output_b2197_sw30sp150_sw30sp150

**Configuration:** P1_swing_length=30, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 1.214** (is_sharpe 4.807, 11 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=30 span=150 -> output_b2197_sw30sp150_sw30sp150_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw30sp150_sw30sp150_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp150): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=194, NO_EXIT_SELECTABLE=106. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 35 combos carried across 65 distinct outcome classes in output_b2197_sw30sp150_sw30sp150_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp150): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=194, NO_EXIT_SELECTABLE=106. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2040 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | d2a332392ce3c3fc | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-09 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha c7d2050b1b36 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 30, ema_span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp150_sw30sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **106 (35%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 194 graded and ranked, collapsing to 65 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 35 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 1.214 | 4.807 | 11 | time_stop_10d | 5 | close_mitigation=False break_pct_max=0.01 age_bars_max=250 tail_n=20 |
| 2 | 0.671 | 1.99 | 14 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.03 age_bars_max=120 tail_n=20 |
| 3 | 0.195 | 1.733 | 23 | time_stop_20d | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=250 tail_n=20 |
| 4 | 0.146 | 2.493 | 11 | time_stop_20d | 5 | close_mitigation=False break_pct_max=0.03 age_bars_max=60 tail_n=20 |
| 5 | 0.102 | 0.716 | 48 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp150_sw30sp150_grid_auto.json._

### output_b2197_sw30sp100_sw30sp100

**Configuration:** P1_swing_length=30, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.816** (is_sharpe 4.103, 12 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=30 span=100 -> output_b2197_sw30sp100_sw30sp100_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw30sp100_sw30sp100_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp100): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=200, NO_EXIT_SELECTABLE=100. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 43 combos carried across 67 distinct outcome classes in output_b2197_sw30sp100_sw30sp100_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp100): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=200, NO_EXIT_SELECTABLE=100. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1944 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 9bb0b39cea0180a9 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 6d59236f64c7 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 30, ema_span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp100_sw30sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **100 (33%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 200 graded and ranked, collapsing to 67 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 43 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.816 | 4.103 | 12 | time_stop_10d | 5 | close_mitigation=False break_pct_max=0.01 age_bars_max=250 tail_n=20 |
| 2 | 0.644 | 1.83 | 16 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.02 age_bars_max=250 tail_n=20 |
| 3 | 0.604 | 1.849 | 15 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.03 age_bars_max=120 tail_n=20 |
| 4 | 0.431 | 1.875 | 11 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.02 age_bars_max=180 tail_n=20 |
| 5 | 0.398 | 1.653 | 14 | earnings_blackout | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=120 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp100_sw30sp100_grid_auto.json._

### output_b2197_sw30sp50_sw30sp50

**Configuration:** P1_swing_length=30, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.816** (is_sharpe 4.103, 12 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=30 span=50 -> output_b2197_sw30sp50_sw30sp50_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw30sp50_sw30sp50_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp50): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=200, NO_EXIT_SELECTABLE=100. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 43 combos carried across 68 distinct outcome classes in output_b2197_sw30sp50_sw30sp50_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp50): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=200, NO_EXIT_SELECTABLE=100. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1944 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 7426924e675ef4c2 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha df557df1e6b7 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 30, ema_span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp50_sw30sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **100 (33%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 200 graded and ranked, collapsing to 68 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 43 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.816 | 4.103 | 12 | time_stop_10d | 5 | close_mitigation=False break_pct_max=0.01 age_bars_max=250 tail_n=20 |
| 2 | 0.644 | 1.83 | 16 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.02 age_bars_max=250 tail_n=20 |
| 3 | 0.604 | 1.849 | 15 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.03 age_bars_max=120 tail_n=20 |
| 4 | 0.431 | 1.875 | 11 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.02 age_bars_max=180 tail_n=20 |
| 5 | 0.398 | 1.653 | 14 | earnings_blackout | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=120 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp50_sw30sp50_grid_auto.json._

### output_b2197_sw30sp20_sw30sp20

**Configuration:** P1_swing_length=30, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.816** (is_sharpe 4.103, 12 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=30 span=20 -> output_b2197_sw30sp20_sw30sp20_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw30sp20_sw30sp20_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp20): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=200, NO_EXIT_SELECTABLE=100. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 43 combos carried across 74 distinct outcome classes in output_b2197_sw30sp20_sw30sp20_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp20): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=200, NO_EXIT_SELECTABLE=100. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1968 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | f139a4d48c03a9ae | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 41e46b82dd1b | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 30, ema_span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp20_sw30sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **100 (33%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 200 graded and ranked, collapsing to 74 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 43 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.816 | 4.103 | 12 | time_stop_10d | 5 | close_mitigation=False break_pct_max=0.01 age_bars_max=250 tail_n=20 |
| 2 | 0.701 | 1.702 | 22 | earnings_blackout | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=250 tail_n=20 |
| 3 | 0.604 | 1.849 | 15 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.03 age_bars_max=120 tail_n=20 |
| 4 | 0.504 | 1.706 | 15 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.02 age_bars_max=250 tail_n=20 |
| 5 | 0.431 | 1.875 | 11 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.02 age_bars_max=180 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp20_sw30sp20_grid_auto.json._

### output_b2197_sw30sp9_sw30sp9

**Configuration:** P1_swing_length=30, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.687** (is_sharpe 1.684, 22 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=30 span=9 -> output_b2197_sw30sp9_sw30sp9_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw30sp9_sw30sp9_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp9): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=195, NO_EXIT_SELECTABLE=95, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 37 combos carried across 75 distinct outcome classes in output_b2197_sw30sp9_sw30sp9_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw30sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw30sp9): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=195, NO_EXIT_SELECTABLE=95, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2064 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 7c853ec451ce9636 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha c67969dab0b2 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 30, ema_span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp9_sw30sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **95 (32%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 205 graded and ranked, collapsing to 75 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 37 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.687 | 1.684 | 22 | earnings_blackout | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=250 tail_n=20 |
| 2 | 0.493 | 1.714 | 15 | earnings_blackout | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=180 tail_n=20 |
| 3 | 0.469 | 3.846 | 11 | time_stop_10d | 5 | close_mitigation=False break_pct_max=0.01 age_bars_max=250 tail_n=20 |
| 4 | 0.444 | 1.706 | 14 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.03 age_bars_max=120 tail_n=20 |
| 5 | 0.222 | 1.497 | 13 | earnings_blackout | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=120 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp9_sw30sp9_grid_auto.json._

### output_b2197_sw20sp150_sw20sp150

**Configuration:** P1_swing_length=20, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.114** (is_sharpe 0.357, 80 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=20 span=150 -> output_b2197_sw20sp150_sw20sp150_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw20sp150_sw20sp150_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp150): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 18 combos carried across 92 distinct outcome classes in output_b2197_sw20sp150_sw20sp150_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp150): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp150): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2640 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 7e9b5bc0140ae6f2 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-22 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha dee210fdae5c | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 20, ema_span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp150_sw20sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked, collapsing to 92 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 18 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.114 | 0.357 | 80 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 |
| 2 | -0.117 | 0.349 | 77 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=2 |
| 3 | -0.12 | 0.31 | 95 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=5 |
| 4 | -0.123 | 0.35 | 79 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=3 |
| 5 | -0.128 | 0.366 | 68 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp150_sw20sp150_grid_auto.json._

### output_b2197_sw20sp100_sw20sp100

**Configuration:** P1_swing_length=20, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.036** (is_sharpe 0.465, 66 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=20 span=100 -> output_b2197_sw20sp100_sw20sp100_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw20sp100_sw20sp100_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp100): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 21 combos carried across 91 distinct outcome classes in output_b2197_sw20sp100_sw20sp100_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp100): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp100): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2568 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 0a093f626abfebdc | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-22 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 235cb9e9bd5c | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 20, ema_span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp100_sw20sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked, collapsing to 91 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 21 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.036 | 0.465 | 66 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=2 |
| 2 | -0.04 | 0.433 | 75 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=2 |
| 3 | -0.05 | 0.431 | 77 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 |
| 4 | -0.051 | 0.471 | 65 | hybrid_50pct_target | 4 | close_mitigation=False break_pct_max=None age_bars_max=180 tail_n=20 |
| 5 | -0.052 | 0.46 | 67 | hybrid_50pct_target | 4 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp100_sw20sp100_grid_auto.json._

### output_b2197_sw20sp50_sw20sp50

**Configuration:** P1_swing_length=20, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.025** (is_sharpe 0.535, 62 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=20 span=50 -> output_b2197_sw20sp50_sw20sp50_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw20sp50_sw20sp50_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp50): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 19 combos carried across 92 distinct outcome classes in output_b2197_sw20sp50_sw20sp50_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp50): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2472 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 436c6f689b13bc3f | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-22 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha d7c666455823 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 20, ema_span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp50_sw20sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked, collapsing to 92 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 19 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.025 | 0.535 | 62 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=2 |
| 2 | 0.02 | 0.462 | 88 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=5 |
| 3 | 0.01 | 0.53 | 63 | hybrid_50pct_target | 4 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=20 |
| 4 | 0.0 | 0.488 | 73 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=20 |
| 5 | -0.008 | 0.48 | 72 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp50_sw20sp50_grid_auto.json._

### output_b2197_sw20sp21_sw20sp21

**Configuration:** P1_swing_length=20, P6_span=21

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.107** (is_sharpe 0.551, 88 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=20 span=21 -> output_b2197_sw20sp21_sw20sp21_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw20sp21_sw20sp21_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp21): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp21): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 17 combos carried across 97 distinct outcome classes in output_b2197_sw20sp21_sw20sp21_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp21): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp21): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2520 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | ce0921c7ff3c441e | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-22 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 96d68043d9ec | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 20, ema_span 21, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp21_sw20sp21_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked, collapsing to 97 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 17 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.107 | 0.551 | 88 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=5 |
| 2 | 0.083 | 0.605 | 64 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=20 |
| 3 | 0.073 | 0.597 | 63 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=3 |
| 4 | 0.061 | 0.493 | 93 | hybrid_50pct_target | 2 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=20 |
| 5 | 0.042 | 0.569 | 60 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp21_sw20sp21_grid_auto.json._

### output_b2197_sw20sp20_sw20sp20

**Configuration:** P1_swing_length=20, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.107** (is_sharpe 0.551, 88 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=20 span=20 -> output_b2197_sw20sp20_sw20sp20_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw20sp20_sw20sp20_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 17 combos carried across 97 distinct outcome classes in output_b2197_sw20sp20_sw20sp20_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2544 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | ba3c1053266d3dad | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-22 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 42de2e89ded3 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 20, ema_span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp20_sw20sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked, collapsing to 97 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 17 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.107 | 0.551 | 88 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=5 |
| 2 | 0.083 | 0.605 | 64 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=20 |
| 3 | 0.073 | 0.597 | 63 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=3 |
| 4 | 0.061 | 0.493 | 93 | hybrid_50pct_target | 2 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=20 |
| 5 | 0.042 | 0.569 | 60 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp20_sw20sp20_grid_auto.json._

### output_b2197_sw20sp9_sw20sp9

**Configuration:** P1_swing_length=20, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.044** (is_sharpe 1.576, 71 fires, exit r_multiple_2r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=20 span=9 -> output_b2197_sw20sp9_sw20sp9_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw20sp9_sw20sp9_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp9): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 18 combos carried across 100 distinct outcome classes in output_b2197_sw20sp9_sw20sp9_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2197_sw20sp9): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2197_sw20sp9): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=223, NO_EXIT_SELECTABLE=77. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 2688 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | ef3e7d64ae2a5a2d | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-22 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha a8cf53716a06 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 20, ema_span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp9_sw20sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked, collapsing to 100 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 18 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.044 | 1.576 | 71 | r_multiple_2r | 1 | close_mitigation=False break_pct_max=0.03 age_bars_max=None tail_n=5 |
| 2 | -0.002 | 0.399 | 112 | hybrid_50pct_target | 2 | close_mitigation=False break_pct_max=None age_bars_max=None tail_n=20 |
| 3 | -0.008 | 0.504 | 66 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=250 tail_n=3 |
| 4 | -0.015 | 0.467 | 75 | hybrid_50pct_target | 1 | close_mitigation=False break_pct_max=None age_bars_max=250 tail_n=3 |
| 5 | -0.032 | 0.499 | 64 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=180 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp9_sw20sp9_grid_auto.json._

### output_b2190_sw5_sw5

**Configuration:** P1_swing_length=5, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.123** (is_sharpe 0.625, 74 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=5 span=200 -> output_b2190_sw5_sw5_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2190_sw5_sw5_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2190_sw5): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2190_sw5): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 20 combos carried across 132 distinct outcome classes in output_b2190_sw5_sw5_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2190_sw5): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2190_sw5): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=250, NO_EXIT_SELECTABLE=40, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 6408 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | NVDA, MSFT, TSLA, AAPL | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | e7523517eec1c7c0 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha dc735c2ffff2 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 5, ema_span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2190_sw5_sw5_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 260 graded and ranked, collapsing to 132 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 20 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.123 | 0.625 | 74 | earnings_blackout | 1 | close_mitigation=True break_pct_max=0.02 age_bars_max=120 tail_n=5 |
| 2 | 0.102 | 0.6 | 75 | earnings_blackout | 2 | close_mitigation=True break_pct_max=0.02 age_bars_max=120 tail_n=20 |
| 3 | 0.086 | 0.479 | 118 | earnings_blackout | 2 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=5 |
| 4 | 0.078 | 0.553 | 81 | earnings_blackout | 3 | close_mitigation=True break_pct_max=0.02 age_bars_max=None tail_n=5 |
| 5 | 0.071 | 0.489 | 106 | earnings_blackout | 1 | close_mitigation=False break_pct_max=0.02 age_bars_max=120 tail_n=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2190_sw5_sw5_grid_auto.json._

### output_b2190_sw10_sw10

**Configuration:** P1_swing_length=10, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.091** (is_sharpe 0.746, 92 fires, exit fixed_4r_2r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=10 span=200 -> output_b2190_sw10_sw10_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2190_sw10_sw10_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2190_sw10): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=245, NO_EXIT_SELECTABLE=45, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2190_sw10): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 16 combos carried across 133 distinct outcome classes in output_b2190_sw10_sw10_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2190_sw10): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2190_sw10): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=245, NO_EXIT_SELECTABLE=45, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 4560 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | MSFT, TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 19ab315150000ae3 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-05-02 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha b7c6937272d2 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 10, ema_span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2190_sw10_sw10_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 255 graded and ranked, collapsing to 133 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 16 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.091 | 0.746 | 92 | fixed_4r_2r | 1 | close_mitigation=False break_pct_max=0.02 age_bars_max=None tail_n=10 |
| 2 | -0.092 | 0.379 | 162 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=10 |
| 3 | -0.092 | 0.377 | 163 | breakeven_plus_trail | 1 | close_mitigation=False break_pct_max=0.05 age_bars_max=None tail_n=20 |
| 4 | -0.133 | 0.246 | 133 | hybrid_50pct_target | 3 | close_mitigation=False break_pct_max=None age_bars_max=120 tail_n=20 |
| 5 | -0.136 | 1.136 | 77 | r_multiple_3r | 3 | close_mitigation=False break_pct_max=0.02 age_bars_max=250 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2190_sw10_sw10_grid_auto.json._

### output_b2177_sw50_sw50

**Configuration:** P1_swing_length=50, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.508** (is_sharpe 0.889, 33 fires, exit chandelier_3x). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=50 span=200 -> output_b2177_sw50_sw50_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2177_sw50_sw50_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2177_sw50): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=75, NO_EXIT_SELECTABLE=225. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2177_sw50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 19 combos carried across 29 distinct outcome classes in output_b2177_sw50_sw50_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2177_sw50): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2177_sw50): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=75, NO_EXIT_SELECTABLE=225. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 960 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 166cdeb615064c61 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-10 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 8a6feb010318 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 40 of 40 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 50, ema_span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2177_sw50_sw50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **225 (75%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 75 graded and ranked, collapsing to 29 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 19 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.508 | 0.889 | 33 | chandelier_3x | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=3 |
| 2 | -0.616 | 0.899 | 29 | chandelier_3x | 1 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=2 |
| 3 | -0.623 | 0.752 | 35 | chandelier_3x | 3 | close_mitigation=True break_pct_max=None age_bars_max=None tail_n=20 |
| 4 | -0.628 | 0.86 | 28 | chandelier_3x | 1 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=3 |
| 5 | -0.681 | 0.793 | 29 | chandelier_3x | 3 | close_mitigation=True break_pct_max=0.05 age_bars_max=None tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2177_sw50_sw50_grid_auto.json._

### output_b2183_sw30_sw30

**Configuration:** P1_swing_length=30, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.362** (is_sharpe 2.757, 11 fires, exit time_stop_20d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 9 of 9 steps closed** (7 DONE with evidence, 2 N/A with a reason: 6_post_fix_recheck, 7_implement_in_engine). Every step is dispositioned; nothing is outstanding on this cube.

| step | status | evidence / reason (never truncated) |
|---|---|---|
| 1_cube_sanity | DONE | the named checks are tabulated below by risk question |
| 2_grade_with_config_params | DONE | AUTO (B2177): graded at manifest swing=30 span=200 -> output_b2183_sw30_sw30_grid_auto.json |
| 3_outlier_discrepancy_sweep | DONE | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-loss gate and ci_lo-led ranking; judgment residue rides the wave review |
| 4_three_leg_spot_check | DONE | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2183_sw30_sw30_spot_check.json |
| 5_adversarial_lens_review | DONE | PENDING-WAVE-REVIEW (b2183_sw30): the wave-level review batch performs this step across all arms together // S6-B2460 WAVE REVIEW PERFORMED. MEASURED over the grid artifact: 300 combinations enumerated, 0 reached grading. Cut distribution: BELOW_POWER_FLOOR=184, NO_EXIT_SELECTABLE=106, ZERO_FIRES=10. ADVERSARIAL QUESTION: is a zero-graded result real, or an artifact of the pipeline? EVIDENCE IT IS REAL: the cuts are three DISTINCT upstream reasons and their proportions VARY across the wave with swing width (sw50 loses 225 of 300 to NO_EXIT_SELECTABLE where sw5 loses 40) - a pipeline defect would fail uniformly and for one reason. FINDING: the configuration searched a space in which no combination clears the sample-size floor; that is a result about the parameter band, not a failure of the grader. |
| 6_post_fix_recheck | N/A | PENDING-WAVE-REVIEW (b2183_sw30): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - step 5 produced a FINDING but no FIX (nothing in the grader or producer was changed), so there is no shipped conclusion to re-derive. |
| 6b_equivalence_class_check | DONE | AUTO (B2192): the grader collapses identical outcomes - 46 combos carried across 61 distinct outcome classes in output_b2183_sw30_sw30_grid_auto.json |
| 7_implement_in_engine | N/A | PENDING-WAVE-REVIEW (b2183_sw30): the wave-level review batch performs this step across all arms together // S6-B2460: N/A on evidence - 0 of 300 combinations returned PASS, so nothing was selected and there is no parameter set to wire into the engine. |
| 8_verdict_with_denominators | DONE | PENDING-WAVE-REVIEW (b2183_sw30): the wave-level review batch performs this step across all arms together // S6-B2460 VERDICT: 0 of 300 enumerated combinations reached grading; the honest denominator for any performance claim about this config is ZERO, not 300. Cut distribution: BELOW_POWER_FLOOR=184, NO_EXIT_SELECTABLE=106, ZERO_FIRES=10. No ranking, no qualifier, no admission is derivable from this config. |

**Is this the right data?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| cube produced rows | 1680 rows | PASS | zero rows = the config ran and emitted nothing |
| exactly one strategy in the cube | 1 strategies | PASS | more than 1 = the strategy-subset filter leaked |
| mega-caps present in the universe | TSLA | PASS | absent = the abandoned A-C chunk universe (L445) |
| universe artifact verified | exit 0 on output_audit/_sweep_200.txt (verifier is non-block | PASS | FAIL = the ticker list is not what was intended |
| cube content hash | 4671bb950ef25501 | PASS | a repeat across configs = two configs produced identical cubes, so one knob did nothing |
| entry-date span actually simulated | entries 2024-05-06 .. 2025-04-11 | PASS | a short span = the run did not cover its window |
| every entry carries one row per registered exit | cube [24] vs registry-now 24 (a differing single value = an | PASS | a shortfall = exits silently dropped from the cube |

**Did anything leak from the future?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| entries at or after the LOCKED holdout start | 0 entries at/after HO_START 2025-05-05 in a STEP-1 cube | PASS | any non-zero = the holdout was contaminated and the run is void |
| fills that preceded their own entry | 0 fills before entry | PASS | any non-zero = look-ahead in execution |
| pre-launch receipt matches the run manifest | receipt matches manifest sha 8c12dc6fce15 | PASS | mismatch = this run is not the run that was gated |

**Does the arithmetic reproduce?**

| check | measured | outcome | what would have been alarming |
|---|---|---|---|
| NaN/inf PnL, and values beyond the winsorize bound | 0 NaN/inf | PASS | NaN/inf = arithmetic corruption; beyond-bound is disclosure only, clipped at grade time |
| exit methods that silently fell back to another | degraded map (B1623 measure-not-assume): {'reverse_signal': | PASS | each mapping = an exit you paid to test and did not actually test |
| rows claiming DONE whose evidence contradicts it | 0 row(s) claim DONE with contradicting evidence | PASS | any non-zero = the ledger is lying about itself |
| grading ran at this config's own parameters | exit 0 | PASS | non-zero = the grid was never produced |
| independent spot check ran | exit 0 | PASS | non-zero = no re-derivation happened |
| engine-side implementation check exit code | exit 0 | PASS | non-zero = the wiring is absent |

**Independent re-derivation of sampled trades (step 4)**

- 50 of 50 sampled trades re-derived to the SAME fire/no-fire decision as the engine; 0 disagreed; 0 execution failures.
- Sampled with seed 20260816 at this config's own parameters (swing_length 30, ema_span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2183_sw30_sw30_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 combinations enumerated (population field `results`).
- **106 (35%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 194 graded and ranked, collapsing to 61 distinct outcome classes (step 6b: combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473); the top 10 classes carry 46 combinations forward to Step 2 (tighten_breaker_block.py:449-454).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.362 | 2.757 | 11 | time_stop_20d | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=120 tail_n=20 |
| 2 | 0.244 | 1.755 | 10 | earnings_blackout | 5 | close_mitigation=True break_pct_max=0.03 age_bars_max=120 tail_n=20 |
| 3 | 0.113 | 2.135 | 14 | time_stop_20d | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=180 tail_n=20 |
| 4 | 0.031 | 1.967 | 15 | time_stop_20d | 5 | close_mitigation=False break_pct_max=0.03 age_bars_max=120 tail_n=20 |
| 5 | 0.0 | 1.797 | 17 | time_stop_20d | 5 | close_mitigation=False break_pct_max=0.02 age_bars_max=250 tail_n=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2183_sw30_sw30_grid_auto.json._

