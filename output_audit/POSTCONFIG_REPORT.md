# POST-CONFIG ANALYSIS - all configs, all findings

Source: output_audit/postconfig_ledger.json plus each config's _grid_auto.json and _spot_check.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_doc.py; per CHECKLIST #77.

REGENERATED WHOLE at every config landing. Replaces the per-config report cards (B2198/B2208), which reported step STATUS rather than step FINDINGS.

## How much confidence these checks earn

**Across the entire ledger (105 entries), 524 named checks have run and 1 have ever returned non-PASS.**

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

_320 ranked outcomes across 32 graded configs; 297 distinct signatures._

**Best within each depth tier** (the comparison a rank order hides):

| tier | best is_ci_lo | at n | rows |
|---|---|---|---|
| DEEP | +0.098 | 128 | 106 |
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

## Index - 32 graded config(s), newest first

| config | best is_ci_lo | fires | starved | steps run |
|---|---|---|---|---|
| output_b2399_step2_sw50sp50_step2_sw50sp50 | -0.026 | 325 | 29/300 | 5/9 |
| output_b2197_sw50sp150_sw50sp150 | 0.437 | 10 | 190/300 | 5/9 |
| output_b2197_sw50sp100_sw50sp100 | -0.023 | 25 | 200/300 | 5/9 |
| output_b2197_sw50sp50_sw50sp50 | 1.25 | 14 | 200/300 | 5/9 |
| output_b2197_sw50sp20_sw50sp20 | 0.93 | 14 | 200/300 | 5/9 |
| output_b2197_sw50sp9_sw50sp9 | 0.724 | 25 | 200/300 | 5/9 |
| output_b2197_sw5sp150_sw5sp150 | 0.019 | 76 | 40/300 | 5/9 |
| output_b2197_sw5sp100_sw5sp100 | 0.027 | 77 | 40/300 | 5/9 |
| output_b2197_sw5sp50_sw5sp50 | -0.005 | 220 | 45/300 | 5/9 |
| output_b2197_sw5sp20_sw5sp20 | -0.005 | 140 | 45/300 | 5/9 |
| output_b2197_sw5sp9_sw5sp9 | 0.098 | 128 | 45/300 | 5/9 |
| output_b2197_sw10sp150_sw10sp150 | -0.11 | 119 | 40/300 | 5/9 |
| output_b2197_sw10sp100_sw10sp100 | -0.12 | 174 | 40/300 | 5/9 |
| output_b2197_sw10sp50_sw10sp50 | -0.042 | 156 | 45/300 | 5/9 |
| output_b2197_sw10sp20_sw10sp20 | -0.07 | 110 | 41/300 | 5/9 |
| output_b2197_sw10sp9_sw10sp9 | -0.014 | 68 | 42/300 | 5/9 |
| output_b2197_sw30sp150_sw30sp150 | 1.214 | 11 | 106/300 | 5/9 |
| output_b2197_sw30sp100_sw30sp100 | 0.816 | 12 | 100/300 | 5/9 |
| output_b2197_sw30sp50_sw30sp50 | 0.816 | 12 | 100/300 | 5/9 |
| output_b2197_sw30sp20_sw30sp20 | 0.816 | 12 | 100/300 | 5/9 |
| output_b2197_sw30sp9_sw30sp9 | 0.687 | 22 | 95/300 | 5/9 |
| output_b2197_sw20sp150_sw20sp150 | -0.114 | 80 | 77/300 | 5/9 |
| output_b2197_sw20sp100_sw20sp100 | -0.036 | 66 | 77/300 | 5/9 |
| output_b2197_sw20sp50_sw20sp50 | 0.025 | 62 | 77/300 | 5/9 |
| output_b2197_sw20sp21_sw20sp21 | 0.107 | 88 | 77/300 | 5/9 |
| output_b2197_sw20sp20_sw20sp20 | 0.107 | 88 | 77/300 | 5/9 |
| output_b2197_sw20sp9_sw20sp9 | 0.044 | 71 | 77/300 | 5/9 |
| output_b2190_sw5_sw5 | 0.123 | 74 | 40/300 | 5/9 |
| output_b2190_sw10_sw10 | -0.091 | 92 | 45/300 | 5/9 |
| output_b2177_sw50_sw50 | -0.508 | 33 | 225/300 | 5/9 |
| output_b2183_sw30_sw30 | 0.362 | 11 | 106/300 | 5/9 |
| output_b2174_sw20_sw20 | -0.196 | 79 | 82/300 | 3/9 |

## Per-config findings

### output_b2399_step2_sw50sp50_step2_sw50sp50

**Configuration:** P1_swing_length=50, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.026** (is_sharpe 0.145, 325 fires, exit trailing_15pct). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 50, span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2399_step2_sw50sp50_step2_sw50sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **29 (10%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 73 graded and ranked; 21 carried across 104 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.026 | 0.145 | 325 | trailing_15pct | 1 | cm=False brk=0.05 age=None tail=2 |
| 2 | -0.047 | 0.303 | 148 | hybrid_50pct_target | 4 | cm=True brk=0.03 age=250 tail=20 |
| 3 | -0.047 | 0.186 | 339 | hybrid_50pct_target | 2 | cm=False brk=0.03 age=None tail=20 |
| 4 | -0.047 | 0.186 | 338 | hybrid_50pct_target | 1 | cm=False brk=0.03 age=None tail=5 |
| 5 | -0.047 | 0.175 | 397 | hybrid_50pct_target | 2 | cm=False brk=0.05 age=None tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2399_step2_sw50sp50_step2_sw50sp50_grid_auto.json._

### output_b2197_sw50sp150_sw50sp150

**Configuration:** P1_swing_length=50, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.437** (is_sharpe 3.083, 10 fires, exit fixed_4r_2r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 50, span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp150_sw50sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **190 (63%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 110 graded and ranked; 14 carried across 44 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.437 | 3.083 | 10 | fixed_4r_2r | 5 | cm=True brk=0.02 age=250 tail=20 |
| 2 | -0.164 | 1.083 | 38 | chandelier_3x | 1 | cm=True brk=None age=None tail=2 |
| 3 | -0.205 | 2.057 | 27 | r_multiple_3r | 1 | cm=False brk=0.02 age=None tail=2 |
| 4 | -0.205 | 0.932 | 43 | chandelier_3x | 1 | cm=True brk=None age=None tail=3 |
| 5 | -0.218 | 1.885 | 30 | r_multiple_3r | 1 | cm=False brk=0.03 age=None tail=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp150_sw50sp150_grid_auto.json._

### output_b2197_sw50sp100_sw50sp100

**Configuration:** P1_swing_length=50, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.023** (is_sharpe 2.292, 25 fires, exit r_multiple_3r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 50, span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp100_sw50sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked; 14 carried across 42 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.023 | 2.292 | 25 | r_multiple_3r | 1 | cm=False brk=0.02 age=None tail=2 |
| 2 | -0.032 | 2.49 | 21 | r_multiple_3r | 1 | cm=True brk=0.02 age=None tail=2 |
| 3 | -0.058 | 2.087 | 28 | r_multiple_3r | 1 | cm=False brk=0.03 age=None tail=2 |
| 4 | -0.077 | 2.229 | 24 | r_multiple_3r | 1 | cm=True brk=0.03 age=None tail=2 |
| 5 | -0.083 | 2.269 | 24 | r_multiple_3r | 1 | cm=True brk=0.02 age=None tail=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp100_sw50sp100_grid_auto.json._

### output_b2197_sw50sp50_sw50sp50

**Configuration:** P1_swing_length=50, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 1.25** (is_sharpe 4.301, 14 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 50, span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp50_sw50sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked; 14 carried across 42 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 1.25 | 4.301 | 14 | time_stop_10d | 1 | cm=True brk=0.01 age=None tail=3 |
| 2 | 1.189 | 3.724 | 19 | time_stop_10d | 1 | cm=True brk=0.02 age=None tail=2 |
| 3 | 1.11 | 3.427 | 22 | time_stop_10d | 1 | cm=True brk=0.02 age=None tail=3 |
| 4 | 1.044 | 3.929 | 15 | time_stop_10d | 3 | cm=True brk=0.01 age=None tail=20 |
| 5 | 1.013 | 3.26 | 23 | time_stop_10d | 3 | cm=True brk=0.02 age=None tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp50_sw50sp50_grid_auto.json._

### output_b2197_sw50sp20_sw50sp20

**Configuration:** P1_swing_length=50, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.93** (is_sharpe 3.915, 14 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 50, span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp20_sw50sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked; 21 carried across 41 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.93 | 3.915 | 14 | time_stop_10d | 2 | cm=True brk=0.01 age=None tail=3 |
| 2 | 0.759 | 3.592 | 15 | time_stop_10d | 3 | cm=True brk=0.01 age=None tail=20 |
| 3 | 0.578 | 2.7 | 24 | time_stop_10d | 1 | cm=True brk=0.02 age=None tail=3 |
| 4 | 0.563 | 1.865 | 32 | fixed_4r_2r | 1 | cm=True brk=0.05 age=None tail=3 |
| 5 | 0.551 | 1.84 | 32 | fixed_4r_2r | 1 | cm=False brk=0.02 age=None tail=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp20_sw50sp20_grid_auto.json._

### output_b2197_sw50sp9_sw50sp9

**Configuration:** P1_swing_length=50, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.724** (is_sharpe 2.82, 25 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 50, span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw50sp9_sw50sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **200 (67%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 100 graded and ranked; 20 carried across 42 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.724 | 2.82 | 25 | time_stop_10d | 1 | cm=True brk=0.02 age=None tail=3 |
| 2 | 0.661 | 2.706 | 26 | time_stop_10d | 3 | cm=True brk=0.02 age=None tail=20 |
| 3 | 0.656 | 1.93 | 33 | fixed_4r_2r | 1 | cm=False brk=0.02 age=None tail=3 |
| 4 | 0.597 | 1.851 | 34 | fixed_4r_2r | 3 | cm=False brk=0.02 age=None tail=20 |
| 5 | 0.472 | 1.651 | 37 | fixed_4r_2r | 1 | cm=False brk=0.03 age=None tail=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw50sp9_sw50sp9_grid_auto.json._

### output_b2197_sw5sp150_sw5sp150

**Configuration:** P1_swing_length=5, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.019** (is_sharpe 0.508, 76 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 5, span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp150_sw5sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 18 carried across 132 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.019 | 0.508 | 76 | earnings_blackout | 1 | cm=True brk=0.02 age=120 tail=5 |
| 2 | 0.007 | 0.394 | 120 | earnings_blackout | 2 | cm=False brk=0.02 age=None tail=5 |
| 3 | 0.001 | 0.486 | 77 | earnings_blackout | 2 | cm=True brk=0.02 age=120 tail=20 |
| 4 | -0.01 | 0.458 | 82 | earnings_blackout | 3 | cm=True brk=0.02 age=None tail=5 |
| 5 | -0.018 | 0.39 | 109 | earnings_blackout | 1 | cm=False brk=0.02 age=120 tail=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp150_sw5sp150_grid_auto.json._

### output_b2197_sw5sp100_sw5sp100

**Configuration:** P1_swing_length=5, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.027** (is_sharpe 0.513, 77 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 5, span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp100_sw5sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 24 carried across 132 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.027 | 0.513 | 77 | earnings_blackout | 1 | cm=True brk=0.02 age=120 tail=5 |
| 2 | 0.009 | 0.491 | 78 | earnings_blackout | 2 | cm=True brk=0.02 age=120 tail=20 |
| 3 | -0.002 | 0.463 | 83 | earnings_blackout | 3 | cm=True brk=0.02 age=None tail=5 |
| 4 | -0.017 | 0.439 | 86 | earnings_blackout | 2 | cm=True brk=0.02 age=180 tail=20 |
| 5 | -0.049 | 0.523 | 103 | breakeven_plus_trail | 4 | cm=True brk=0.03 age=None tail=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp100_sw5sp100_grid_auto.json._

### output_b2197_sw5sp50_sw5sp50

**Configuration:** P1_swing_length=5, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.005** (is_sharpe 0.402, 220 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 5, span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp50_sw5sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 20 carried across 124 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.005 | 0.402 | 220 | breakeven_plus_trail | 2 | cm=True brk=None age=180 tail=20 |
| 2 | -0.017 | 0.402 | 208 | breakeven_plus_trail | 1 | cm=True brk=None age=180 tail=5 |
| 3 | -0.018 | 0.428 | 178 | breakeven_plus_trail | 1 | cm=True brk=0.05 age=None tail=20 |
| 4 | -0.021 | 0.48 | 139 | breakeven_plus_trail | 4 | cm=True brk=0.05 age=None tail=3 |
| 5 | -0.022 | 0.392 | 215 | breakeven_plus_trail | 2 | cm=True brk=None age=None tail=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp50_sw5sp50_grid_auto.json._

### output_b2197_sw5sp20_sw5sp20

**Configuration:** P1_swing_length=5, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.005** (is_sharpe 0.49, 140 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 5, span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp20_sw5sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 27 carried across 125 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.005 | 0.49 | 140 | breakeven_plus_trail | 4 | cm=True brk=0.05 age=None tail=3 |
| 2 | -0.01 | 0.525 | 115 | breakeven_plus_trail | 4 | cm=True brk=0.03 age=None tail=3 |
| 3 | -0.014 | 0.444 | 162 | breakeven_plus_trail | 2 | cm=True brk=0.05 age=None tail=5 |
| 4 | -0.023 | 0.419 | 178 | breakeven_plus_trail | 1 | cm=True brk=0.05 age=None tail=10 |
| 5 | -0.024 | 0.417 | 181 | breakeven_plus_trail | 1 | cm=True brk=0.05 age=None tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp20_sw5sp20_grid_auto.json._

### output_b2197_sw5sp9_sw5sp9

**Configuration:** P1_swing_length=5, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.098** (is_sharpe 0.6, 128 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 5, span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw5sp9_sw5sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 20 carried across 126 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.098 | 0.6 | 128 | breakeven_plus_trail | 4 | cm=True brk=0.05 age=None tail=3 |
| 2 | 0.083 | 0.626 | 105 | breakeven_plus_trail | 4 | cm=True brk=0.03 age=None tail=3 |
| 3 | 0.072 | 0.431 | 287 | breakeven_plus_trail | 1 | cm=True brk=None age=None tail=20 |
| 4 | 0.066 | 0.482 | 189 | breakeven_plus_trail | 1 | cm=True brk=0.05 age=None tail=10 |
| 5 | 0.064 | 0.456 | 222 | breakeven_plus_trail | 2 | cm=True brk=None age=180 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw5sp9_sw5sp9_grid_auto.json._

### output_b2197_sw10sp150_sw10sp150

**Configuration:** P1_swing_length=10, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.11** (is_sharpe 0.282, 119 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 10, span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp150_sw10sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 20 carried across 131 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.11 | 0.282 | 119 | hybrid_50pct_target | 3 | cm=False brk=None age=None tail=2 |
| 2 | -0.118 | 0.258 | 135 | hybrid_50pct_target | 3 | cm=False brk=None age=120 tail=20 |
| 3 | -0.132 | 0.244 | 134 | hybrid_50pct_target | 1 | cm=False brk=None age=120 tail=3 |
| 4 | -0.133 | 0.268 | 115 | hybrid_50pct_target | 1 | cm=False brk=None age=120 tail=2 |
| 5 | -0.14 | 0.324 | 177 | breakeven_plus_trail | 1 | cm=False brk=None age=None tail=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp150_sw10sp150_grid_auto.json._

### output_b2197_sw10sp100_sw10sp100

**Configuration:** P1_swing_length=10, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.12** (is_sharpe 0.34, 174 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 10, span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp100_sw10sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 19 carried across 127 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.12 | 0.34 | 174 | breakeven_plus_trail | 1 | cm=False brk=None age=None tail=5 |
| 2 | -0.127 | 0.362 | 154 | breakeven_plus_trail | 3 | cm=False brk=None age=180 tail=20 |
| 3 | -0.131 | 0.337 | 161 | breakeven_plus_trail | 1 | cm=False brk=0.05 age=None tail=20 |
| 4 | -0.141 | 0.402 | 124 | breakeven_plus_trail | 3 | cm=True brk=None age=180 tail=20 |
| 5 | -0.141 | 0.344 | 161 | breakeven_plus_trail | 3 | cm=False brk=None age=250 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp100_sw10sp100_grid_auto.json._

### output_b2197_sw10sp50_sw10sp50

**Configuration:** P1_swing_length=10, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.042** (is_sharpe 0.422, 156 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 10, span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp50_sw10sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 16 carried across 128 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.042 | 0.422 | 156 | breakeven_plus_trail | 1 | cm=False brk=0.05 age=None tail=10 |
| 2 | -0.042 | 0.419 | 157 | breakeven_plus_trail | 1 | cm=False brk=0.05 age=None tail=20 |
| 3 | -0.051 | 0.4 | 172 | breakeven_plus_trail | 1 | cm=False brk=None age=None tail=5 |
| 4 | -0.056 | 0.416 | 162 | breakeven_plus_trail | 1 | cm=True brk=None age=None tail=10 |
| 5 | -0.059 | 0.421 | 153 | breakeven_plus_trail | 3 | cm=False brk=None age=180 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp50_sw10sp50_grid_auto.json._

### output_b2197_sw10sp20_sw10sp20

**Configuration:** P1_swing_length=10, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.07** (is_sharpe 0.47, 110 fires, exit breakeven_plus_trail). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 10, span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp20_sw10sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **41 (14%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 259 graded and ranked; 18 carried across 129 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.07 | 0.47 | 110 | breakeven_plus_trail | 1 | cm=True brk=0.05 age=None tail=10 |
| 2 | -0.07 | 0.466 | 112 | breakeven_plus_trail | 1 | cm=True brk=0.05 age=None tail=20 |
| 3 | -0.078 | 0.357 | 102 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=120 tail=2 |
| 4 | -0.081 | 0.397 | 156 | breakeven_plus_trail | 3 | cm=False brk=None age=180 tail=20 |
| 5 | -0.084 | 0.344 | 105 | hybrid_50pct_target | 3 | cm=False brk=0.05 age=None tail=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp20_sw10sp20_grid_auto.json._

### output_b2197_sw10sp9_sw10sp9

**Configuration:** P1_swing_length=10, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.014** (is_sharpe 0.714, 68 fires, exit class_time_stop). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 10, span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw10sp9_sw10sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **42 (14%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 258 graded and ranked; 16 carried across 138 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.014 | 0.714 | 68 | class_time_stop | 3 | cm=False brk=0.02 age=None tail=2 |
| 2 | -0.016 | 0.408 | 204 | breakeven_plus_trail | 1 | cm=False brk=None age=None tail=20 |
| 3 | -0.021 | 0.433 | 181 | breakeven_plus_trail | 1 | cm=True brk=None age=None tail=10 |
| 4 | -0.023 | 0.402 | 203 | breakeven_plus_trail | 1 | cm=False brk=None age=None tail=10 |
| 5 | -0.024 | 0.428 | 183 | breakeven_plus_trail | 1 | cm=True brk=None age=None tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw10sp9_sw10sp9_grid_auto.json._

### output_b2197_sw30sp150_sw30sp150

**Configuration:** P1_swing_length=30, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 1.214** (is_sharpe 4.807, 11 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 30, span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp150_sw30sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **106 (35%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 194 graded and ranked; 35 carried across 65 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 1.214 | 4.807 | 11 | time_stop_10d | 5 | cm=False brk=0.01 age=250 tail=20 |
| 2 | 0.671 | 1.99 | 14 | earnings_blackout | 5 | cm=True brk=0.03 age=120 tail=20 |
| 3 | 0.195 | 1.733 | 23 | time_stop_20d | 5 | cm=False brk=0.02 age=250 tail=20 |
| 4 | 0.146 | 2.493 | 11 | time_stop_20d | 5 | cm=False brk=0.03 age=60 tail=20 |
| 5 | 0.102 | 0.716 | 48 | hybrid_50pct_target | 3 | cm=False brk=None age=250 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp150_sw30sp150_grid_auto.json._

### output_b2197_sw30sp100_sw30sp100

**Configuration:** P1_swing_length=30, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.816** (is_sharpe 4.103, 12 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 30, span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp100_sw30sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **100 (33%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 200 graded and ranked; 43 carried across 67 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.816 | 4.103 | 12 | time_stop_10d | 5 | cm=False brk=0.01 age=250 tail=20 |
| 2 | 0.644 | 1.83 | 16 | earnings_blackout | 5 | cm=True brk=0.02 age=250 tail=20 |
| 3 | 0.604 | 1.849 | 15 | earnings_blackout | 5 | cm=True brk=0.03 age=120 tail=20 |
| 4 | 0.431 | 1.875 | 11 | earnings_blackout | 5 | cm=True brk=0.02 age=180 tail=20 |
| 5 | 0.398 | 1.653 | 14 | earnings_blackout | 5 | cm=False brk=0.02 age=120 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp100_sw30sp100_grid_auto.json._

### output_b2197_sw30sp50_sw30sp50

**Configuration:** P1_swing_length=30, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.816** (is_sharpe 4.103, 12 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 30, span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp50_sw30sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **100 (33%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 200 graded and ranked; 43 carried across 68 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.816 | 4.103 | 12 | time_stop_10d | 5 | cm=False brk=0.01 age=250 tail=20 |
| 2 | 0.644 | 1.83 | 16 | earnings_blackout | 5 | cm=True brk=0.02 age=250 tail=20 |
| 3 | 0.604 | 1.849 | 15 | earnings_blackout | 5 | cm=True brk=0.03 age=120 tail=20 |
| 4 | 0.431 | 1.875 | 11 | earnings_blackout | 5 | cm=True brk=0.02 age=180 tail=20 |
| 5 | 0.398 | 1.653 | 14 | earnings_blackout | 5 | cm=False brk=0.02 age=120 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp50_sw30sp50_grid_auto.json._

### output_b2197_sw30sp20_sw30sp20

**Configuration:** P1_swing_length=30, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.816** (is_sharpe 4.103, 12 fires, exit time_stop_10d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 30, span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp20_sw30sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **100 (33%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 200 graded and ranked; 43 carried across 74 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.816 | 4.103 | 12 | time_stop_10d | 5 | cm=False brk=0.01 age=250 tail=20 |
| 2 | 0.701 | 1.702 | 22 | earnings_blackout | 5 | cm=False brk=0.02 age=250 tail=20 |
| 3 | 0.604 | 1.849 | 15 | earnings_blackout | 5 | cm=True brk=0.03 age=120 tail=20 |
| 4 | 0.504 | 1.706 | 15 | earnings_blackout | 5 | cm=True brk=0.02 age=250 tail=20 |
| 5 | 0.431 | 1.875 | 11 | earnings_blackout | 5 | cm=True brk=0.02 age=180 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp20_sw30sp20_grid_auto.json._

### output_b2197_sw30sp9_sw30sp9

**Configuration:** P1_swing_length=30, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.687** (is_sharpe 1.684, 22 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 30, span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw30sp9_sw30sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **95 (32%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 195 graded and ranked; 37 carried across 75 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.687 | 1.684 | 22 | earnings_blackout | 5 | cm=False brk=0.02 age=250 tail=20 |
| 2 | 0.493 | 1.714 | 15 | earnings_blackout | 5 | cm=False brk=0.02 age=180 tail=20 |
| 3 | 0.469 | 3.846 | 11 | time_stop_10d | 5 | cm=False brk=0.01 age=250 tail=20 |
| 4 | 0.444 | 1.706 | 14 | earnings_blackout | 5 | cm=True brk=0.03 age=120 tail=20 |
| 5 | 0.222 | 1.497 | 13 | earnings_blackout | 5 | cm=False brk=0.02 age=120 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw30sp9_sw30sp9_grid_auto.json._

### output_b2197_sw20sp150_sw20sp150

**Configuration:** P1_swing_length=20, P6_span=150

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.114** (is_sharpe 0.357, 80 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 20, span 150, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp150_sw20sp150_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked; 18 carried across 92 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.114 | 0.357 | 80 | hybrid_50pct_target | 3 | cm=False brk=None age=250 tail=20 |
| 2 | -0.117 | 0.349 | 77 | hybrid_50pct_target | 1 | cm=False brk=None age=None tail=2 |
| 3 | -0.12 | 0.31 | 95 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=5 |
| 4 | -0.123 | 0.35 | 79 | hybrid_50pct_target | 1 | cm=False brk=None age=250 tail=3 |
| 5 | -0.128 | 0.366 | 68 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp150_sw20sp150_grid_auto.json._

### output_b2197_sw20sp100_sw20sp100

**Configuration:** P1_swing_length=20, P6_span=100

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.036** (is_sharpe 0.465, 66 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 20, span 100, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp100_sw20sp100_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked; 21 carried across 91 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.036 | 0.465 | 66 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=2 |
| 2 | -0.04 | 0.433 | 75 | hybrid_50pct_target | 1 | cm=False brk=None age=None tail=2 |
| 3 | -0.05 | 0.431 | 77 | hybrid_50pct_target | 3 | cm=False brk=None age=250 tail=20 |
| 4 | -0.051 | 0.471 | 65 | hybrid_50pct_target | 4 | cm=False brk=None age=180 tail=20 |
| 5 | -0.052 | 0.46 | 67 | hybrid_50pct_target | 4 | cm=False brk=0.05 age=250 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp100_sw20sp100_grid_auto.json._

### output_b2197_sw20sp50_sw20sp50

**Configuration:** P1_swing_length=20, P6_span=50

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.025** (is_sharpe 0.535, 62 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 20, span 50, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp50_sw20sp50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked; 19 carried across 92 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.025 | 0.535 | 62 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=2 |
| 2 | 0.02 | 0.462 | 88 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=5 |
| 3 | 0.01 | 0.53 | 63 | hybrid_50pct_target | 4 | cm=False brk=0.05 age=250 tail=20 |
| 4 | 0.0 | 0.488 | 73 | hybrid_50pct_target | 3 | cm=False brk=None age=250 tail=20 |
| 5 | -0.008 | 0.48 | 72 | hybrid_50pct_target | 1 | cm=False brk=None age=250 tail=3 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp50_sw20sp50_grid_auto.json._

### output_b2197_sw20sp21_sw20sp21

**Configuration:** P1_swing_length=20, P6_span=21

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.107** (is_sharpe 0.551, 88 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 20, span 21, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp21_sw20sp21_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked; 17 carried across 97 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.107 | 0.551 | 88 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=5 |
| 2 | 0.083 | 0.605 | 64 | hybrid_50pct_target | 3 | cm=False brk=0.05 age=250 tail=20 |
| 3 | 0.073 | 0.597 | 63 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=250 tail=3 |
| 4 | 0.061 | 0.493 | 93 | hybrid_50pct_target | 2 | cm=False brk=0.05 age=None tail=20 |
| 5 | 0.042 | 0.569 | 60 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=250 tail=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp21_sw20sp21_grid_auto.json._

### output_b2197_sw20sp20_sw20sp20

**Configuration:** P1_swing_length=20, P6_span=20

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.107** (is_sharpe 0.551, 88 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 20, span 20, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp20_sw20sp20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked; 17 carried across 97 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.107 | 0.551 | 88 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=5 |
| 2 | 0.083 | 0.605 | 64 | hybrid_50pct_target | 3 | cm=False brk=0.05 age=250 tail=20 |
| 3 | 0.073 | 0.597 | 63 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=250 tail=3 |
| 4 | 0.061 | 0.493 | 93 | hybrid_50pct_target | 2 | cm=False brk=0.05 age=None tail=20 |
| 5 | 0.042 | 0.569 | 60 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=250 tail=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp20_sw20sp20_grid_auto.json._

### output_b2197_sw20sp9_sw20sp9

**Configuration:** P1_swing_length=20, P6_span=9

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.044** (is_sharpe 1.576, 71 fires, exit r_multiple_2r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 20, span 9, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2197_sw20sp9_sw20sp9_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **77 (26%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 223 graded and ranked; 18 carried across 100 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.044 | 1.576 | 71 | r_multiple_2r | 1 | cm=False brk=0.03 age=None tail=5 |
| 2 | -0.002 | 0.399 | 112 | hybrid_50pct_target | 2 | cm=False brk=None age=None tail=20 |
| 3 | -0.008 | 0.504 | 66 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=250 tail=3 |
| 4 | -0.015 | 0.467 | 75 | hybrid_50pct_target | 1 | cm=False brk=None age=250 tail=3 |
| 5 | -0.032 | 0.499 | 64 | hybrid_50pct_target | 3 | cm=False brk=None age=180 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2197_sw20sp9_sw20sp9_grid_auto.json._

### output_b2190_sw5_sw5

**Configuration:** P1_swing_length=5, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.123** (is_sharpe 0.625, 74 fires, exit earnings_blackout). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 5, span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2190_sw5_sw5_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **40 (13%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 250 graded and ranked; 20 carried across 132 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.123 | 0.625 | 74 | earnings_blackout | 1 | cm=True brk=0.02 age=120 tail=5 |
| 2 | 0.102 | 0.6 | 75 | earnings_blackout | 2 | cm=True brk=0.02 age=120 tail=20 |
| 3 | 0.086 | 0.479 | 118 | earnings_blackout | 2 | cm=False brk=0.02 age=None tail=5 |
| 4 | 0.078 | 0.553 | 81 | earnings_blackout | 3 | cm=True brk=0.02 age=None tail=5 |
| 5 | 0.071 | 0.489 | 106 | earnings_blackout | 1 | cm=False brk=0.02 age=120 tail=5 |

_Top 5 of the ranking; the full list is in output_audit/output_b2190_sw5_sw5_grid_auto.json._

### output_b2190_sw10_sw10

**Configuration:** P1_swing_length=10, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.091** (is_sharpe 0.746, 92 fires, exit fixed_4r_2r). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 10, span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2190_sw10_sw10_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **45 (15%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 245 graded and ranked; 16 carried across 133 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.091 | 0.746 | 92 | fixed_4r_2r | 1 | cm=False brk=0.02 age=None tail=10 |
| 2 | -0.092 | 0.379 | 162 | breakeven_plus_trail | 1 | cm=False brk=0.05 age=None tail=10 |
| 3 | -0.092 | 0.377 | 163 | breakeven_plus_trail | 1 | cm=False brk=0.05 age=None tail=20 |
| 4 | -0.133 | 0.246 | 133 | hybrid_50pct_target | 3 | cm=False brk=None age=120 tail=20 |
| 5 | -0.136 | 1.136 | 77 | r_multiple_3r | 3 | cm=False brk=0.02 age=250 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2190_sw10_sw10_grid_auto.json._

### output_b2177_sw50_sw50

**Configuration:** P1_swing_length=50, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.508** (is_sharpe 0.889, 33 fires, exit chandelier_3x). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 50, span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2177_sw50_sw50_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **225 (75%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 75 graded and ranked; 19 carried across 29 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.508 | 0.889 | 33 | chandelier_3x | 1 | cm=True brk=None age=None tail=3 |
| 2 | -0.616 | 0.899 | 29 | chandelier_3x | 1 | cm=True brk=None age=None tail=2 |
| 3 | -0.623 | 0.752 | 35 | chandelier_3x | 3 | cm=True brk=None age=None tail=20 |
| 4 | -0.628 | 0.86 | 28 | chandelier_3x | 1 | cm=True brk=0.05 age=None tail=3 |
| 5 | -0.681 | 0.793 | 29 | chandelier_3x | 3 | cm=True brk=0.05 age=None tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2177_sw50_sw50_grid_auto.json._

### output_b2183_sw30_sw30

**Configuration:** P1_swing_length=30, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo 0.362** (is_sharpe 2.757, 11 fires, exit time_stop_20d). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 5 of 9 steps ran.** The 4 judgment steps (5_adversarial_lens_review, 6_post_fix_recheck, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 30, span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2183_sw30_sw30_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **106 (35%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 184 graded and ranked; 46 carried across 61 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | 0.362 | 2.757 | 11 | time_stop_20d | 5 | cm=False brk=0.02 age=120 tail=20 |
| 2 | 0.244 | 1.755 | 10 | earnings_blackout | 5 | cm=True brk=0.03 age=120 tail=20 |
| 3 | 0.113 | 2.135 | 14 | time_stop_20d | 5 | cm=False brk=0.02 age=180 tail=20 |
| 4 | 0.031 | 1.967 | 15 | time_stop_20d | 5 | cm=False brk=0.03 age=120 tail=20 |
| 5 | 0.0 | 1.797 | 17 | time_stop_20d | 5 | cm=False brk=0.02 age=250 tail=20 |

_Top 5 of the ranking; the full list is in output_audit/output_b2183_sw30_sw30_grid_auto.json._

### output_b2174_sw20_sw20

**Configuration:** P1_swing_length=20, P6_span=200

**STEP-1 RANKING (no gates applied - owner ruling B1608): best cell is_ci_lo -0.196** (is_sharpe 0.282, 79 fires, exit hybrid_50pct_target). Step-1 admission is min-trades >= 10 plus this ranked list; is_ci_lo is the RANKING KEY, not a gate. A ranked cell is a CANDIDATE for Step-2 validation, not a validated edge - its height is partly the search itself. (S6-B2409: the former selection-noise-floor framing is retired.)

**Completeness: 3 of 9 steps ran.** The 6 judgment steps (3_outlier_discrepancy_sweep, 5_adversarial_lens_review, 6_post_fix_recheck, 6b_equivalence_class_check, 7_implement_in_engine, 8_verdict_with_denominators) are NOT automated and remain outstanding - this evidence package is incomplete by design, which is different from clean.

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
- Sampled with seed 20260816 at this config's own parameters (swing 20, span 200, close_mitigation False, tail_n 20).
- CAVEAT worth stating: the re-derivation uses the SAME parameter set as the engine, so it catches wiring and data faults, NOT a wrong parameter choice. Full per-trade rows: output_audit/output_b2174_sw20_sw20_spot_check.json.

**Is the sample large enough to mean anything? (step 2 funnel)**

- 300 parameter combinations enumerated.
- **82 (27%) STARVED in-sample** - no exit cleared the minimum trade count, so they were never graded. A sample-size fact, not a quality verdict.
- 218 graded and ranked; 22 carried across 89 distinct outcome classes after equivalence collapse (combinations differing only in a saturated parameter are the SAME fire set, so counting rows overstates the evidence - L473).

| rank | is_ci_lo | is_sharpe | fires | exit | class size | combination |
|---|---|---|---|---|---|---|
| 1 | -0.196 | 0.282 | 79 | hybrid_50pct_target | 3 | cm=False brk=None age=250 tail=20 |
| 2 | -0.198 | 0.275 | 76 | hybrid_50pct_target | 1 | cm=False brk=None age=None tail=2 |
| 3 | -0.205 | 0.274 | 78 | hybrid_50pct_target | 1 | cm=False brk=None age=250 tail=3 |
| 4 | -0.236 | 0.286 | 66 | hybrid_50pct_target | 4 | cm=False brk=None age=180 tail=20 |
| 5 | -0.24 | 0.268 | 65 | hybrid_50pct_target | 1 | cm=False brk=0.05 age=None tail=2 |

_Top 5 of the ranking; the full list is in output_audit/output_b2174_sw20_sw20_grid_auto.json._

