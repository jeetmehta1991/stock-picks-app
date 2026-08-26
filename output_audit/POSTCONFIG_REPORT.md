# POST-CONFIG ANALYSIS - all configs, all findings

Source: output_audit/postconfig_ledger.json plus each config's _grid_auto.json and _spot_check.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_doc.py; per CHECKLIST #77.

REGENERATED WHOLE at every config landing. Replaces the per-config report cards (B2198/B2208), which reported step STATUS rather than step FINDINGS.

## How much confidence these checks earn

**Across the entire ledger (82 entries), 140 named checks have run and 0 have ever returned non-PASS.**

**Read that as a caution, not a reassurance.** A check that has never failed has not been shown capable of failing, so an all-green battery is WEAK evidence. The checks that would carry real weight are ones with a demonstrated failure mode - a deliberately corrupted cube proving they trip. Until then, green means 'nothing obviously wrong was detected', never 'this cube is correct'.

## Index - 8 graded config(s), newest first

| config | best is_ci_lo | vs floor | fires | starved | steps run |
|---|---|---|---|---|---|
| output_b2197_sw20sp21_sw20sp21 | 0.107 | below | 88 | 77/300 | 5/9 |
| output_b2197_sw20sp20_sw20sp20 | 0.107 | below | 88 | 77/300 | 5/9 |
| output_b2197_sw20sp9_sw20sp9 | 0.044 | below | 71 | 77/300 | 5/9 |
| output_b2190_sw5_sw5 | 0.123 | below | 74 | 40/300 | 5/9 |
| output_b2190_sw10_sw10 | -0.091 | below | 92 | 45/300 | 5/9 |
| output_b2177_sw50_sw50 | -0.508 | below | 33 | 225/300 | 5/9 |
| output_b2183_sw30_sw30 | 0.362 | ABOVE | 11 | 106/300 | 5/9 |
| output_b2174_sw20_sw20 | -0.196 | below | 79 | 82/300 | 3/9 |

## Per-config findings

### output_b2197_sw20sp21_sw20sp21

**Configuration:** P1_swing_length=20, P6_span=21

**VERDICT: best cell is_ci_lo 0.107 BELOW the 0.333 selection-noise yardstick** (is_sharpe 0.551, 88 fires, exit hybrid_50pct_target). Its height is explainable by the search itself.

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

**VERDICT: best cell is_ci_lo 0.107 BELOW the 0.333 selection-noise yardstick** (is_sharpe 0.551, 88 fires, exit hybrid_50pct_target). Its height is explainable by the search itself.

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

**VERDICT: best cell is_ci_lo 0.044 BELOW the 0.333 selection-noise yardstick** (is_sharpe 1.576, 71 fires, exit r_multiple_2r). Its height is explainable by the search itself.

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

**VERDICT: best cell is_ci_lo 0.123 BELOW the 0.333 selection-noise yardstick** (is_sharpe 0.625, 74 fires, exit earnings_blackout). Its height is explainable by the search itself.

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

**VERDICT: best cell is_ci_lo -0.091 BELOW the 0.333 selection-noise yardstick** (is_sharpe 0.746, 92 fires, exit fixed_4r_2r). Its height is explainable by the search itself.

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

**VERDICT: best cell is_ci_lo -0.508 BELOW the 0.333 selection-noise yardstick** (is_sharpe 0.889, 33 fires, exit chandelier_3x). Its height is explainable by the search itself.

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

**VERDICT: best cell is_ci_lo 0.362 ABOVE the 0.333 selection-noise yardstick** (is_sharpe 2.757, 11 fires, exit time_stop_20d). A cell above the yardstick is a CANDIDATE for Step-2 validation, not a validated edge.

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

**VERDICT: best cell is_ci_lo -0.196 BELOW the 0.333 selection-noise yardstick** (is_sharpe 0.282, 79 fires, exit hybrid_50pct_target). Its height is explainable by the search itself.

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

