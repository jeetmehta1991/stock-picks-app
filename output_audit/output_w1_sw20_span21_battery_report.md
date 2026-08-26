# POST-CONFIG BATTERY REPORT - output_w1_sw20_span21

Source: output_audit/postconfig_ledger.json + output_audit/output_w1_sw20_span21_grid_auto.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_report.py; per CHECKLIST #77.

| step | class | status | evidence (truncated) |
|---|---|---|---|
| 1_cube_sanity | AUTO | **DONE** | B1680 - 1 strategy, [26] exits/entry, mega-caps present |
| 2_grade_with_config_params | AUTO | **DONE** | B1678 - graded at the config's own swing_length |
| 3_outlier_discrepancy_sweep | AUTO | **DONE** | B1680 - diag loss 0.0pct, band gate PASS, regime_flip finding |
| 4_three_leg_spot_check | AUTO | **DONE** | B1634 - three-leg, 100pct on all legs |
| 6b_equivalence_class_check | AUTO | **DONE** | B1700 - EXECUTED: 10 classes / 16 members per config; every class holds exactly ONE (fires, exit, sharpe) outcome and class_size == len(members). PASS |
| 5_adversarial_lens_review | JUDGMENT | DONE | B1680 - 11 lenses; regime_flip CONFIRMED finding |
| 6_post_fix_recheck | JUDGMENT | SKIPPED | B1700 - the B1682 regime_flip fix changes cube GENERATION, not grading. MEASURED: 302/320 rows carry the bare 'regime_flip' label, baked in at run tim |
| 7_implement_in_engine | JUDGMENT | DONE | B1700 - EXECUTED verify_engine_implemented.py: 6 of 6 reach the engine, 0 grader-only. exit 0. |
| 8_verdict_with_denominators | JUDGMENT | DONE | B1690 - 300 combos / 90-87 gradable / 49-46 distinct / PASS 0-1 |

**All AUTO steps DONE: True**

**NO AUTO GRID** - step 2 produced no artifact.
