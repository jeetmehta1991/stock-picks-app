# POST-CONFIG BATTERY REPORT - output_b2114_ref

Source: output_audit/postconfig_ledger.json + output_audit/output_b2114_ref_grid_auto.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_report.py; per CHECKLIST #77.

| step | class | status | evidence (truncated) |
|---|---|---|---|
| 1_cube_sanity | AUTO | **DONE** | run_postconfig: cube_exists=PASS(2280 rows); one_strategy=PASS(1 strategies); M2_exits_per_entry_vs_registry=PASS(cube [24] vs registry-now 24 (a diff |
| 2_grade_with_config_params | AUTO | **DONE** | b2118_ref_grid.json: swing-length 20 (the run's own), min-n 10; 10 ranking rows, best is_ci_lo -0.077 (is_sharpe 0.547, 93 fires, breakeven_plus_trail |
| 3_outlier_discrepancy_sweep | AUTO | **DONE** | grader's built-in union diagnosis-loss gate did not abort; ranking led by is_ci_lo (post-B2117a artifact emits the key); battery M5 0 NaN/inf + 0 beyo |
| 4_three_leg_spot_check | AUTO | **DONE** | b2118_ref_spot_check.json: 50/50 producer re-derivation agree (100.0pct), 0 trades with failed execution checks (swing 20 / span 200) |
| 6b_equivalence_class_check | AUTO | **DONE** | grader collapses identical outcomes: 19 combos -> 27 distinct outcome rows across exits; ranking rows carry class_size (max 4; rank-1 class_size 2 = t |
| 5_adversarial_lens_review | JUDGMENT | DONE | reviewed this batch: every graded cell is_ci_lo NEGATIVE (best -0.077), all far below the 0.333 noise floor - the STATE gate produces no rankable edge |
| 6_post_fix_recheck | JUDGMENT | SKIPPED | no fix arose from step 5 - nothing to recheck |
| 7_implement_in_engine | JUDGMENT | SKIPPED | comparator cube - nothing selected for implementation; the conversion itself is B2114, already shipped with its own pin |
| 8_verdict_with_denominators | JUDGMENT | DONE | VERDICT: the STATE-gate reference best cell reaches is_ci_lo -0.077 across 10 graded ranking rows (19 combos, 27 distinct outcomes) from 95 baseline f |

**All AUTO steps DONE: True**

**NO AUTO GRID** - step 2 produced no artifact.
