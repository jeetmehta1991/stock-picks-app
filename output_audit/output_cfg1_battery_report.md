# POST-CONFIG BATTERY REPORT - output_cfg1

Source: output_audit/postconfig_ledger.json + output_audit/output_cfg1_grid_auto.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_report.py; per CHECKLIST #77.

| step | class | status | evidence (truncated) |
|---|---|---|---|
| 1_cube_sanity | AUTO | **DONE** | pre-wave1 grading, B1576-B1615 |
| 2_grade_with_config_params | AUTO | **DONE** | pre-wave1 grading, B1576-B1615 |
| 3_outlier_discrepancy_sweep | AUTO | **DONE** | pre-wave1 grading, B1576-B1615 |
| 4_three_leg_spot_check | AUTO | **SKIPPED** | B2136 status corrected DONE -> SKIPPED: the status contradicted its own evidence, which says this cannot be applied retroactively. B1702 - the three-l |
| 6b_equivalence_class_check | AUTO | **DONE** | B1702 - EXECUTED: cfg1 10 classes / 12 members, cfg2 10 classes / 21 members; every class holds exactly ONE (fires, exit, sharpe) outcome. PASS both. |
| 5_adversarial_lens_review | JUDGMENT | DONE | B1615/B1619 - the cfg1/cfg2 lens pass is what SURFACED the tail_n band defect (0 of 50 groups moved at 10->20) and the equivalence-class defect (top 1 |
| 6_post_fix_recheck | JUDGMENT | SKIPPED | B1702 - same as wave 1: the B1682 regime_flip fix changes cube GENERATION, not grading, so re-grading an existing cube cannot revive the exit. cfg1/cf |
| 7_implement_in_engine | JUDGMENT | DONE | B1702 - verify_engine_implemented.py exit 0, 6 of 6 parameters reach the engine. Config-independent: it audits the code path, not the run. |
| 8_verdict_with_denominators | JUDGMENT | DONE | B1702 - rendered in the POST RUN CONFIG TABLE (table_c). cfg1: 300 combos / 181 no-exit / 34 no-Sharpe / 85 graded / 48 distinct / PASS 0. cfg2: 300 / |

**All AUTO steps DONE: False**

**NO AUTO GRID** - step 2 produced no artifact.
