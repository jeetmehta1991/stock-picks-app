# POST-CONFIG BATTERY REPORT - output_b2197_sw20sp20_sw20sp20

Source: output_audit/postconfig_ledger.json + output_audit/output_b2197_sw20sp20_sw20sp20_grid_auto.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_report.py; per CHECKLIST #77.

| step | class | status | evidence (truncated) |
|---|---|---|---|
| 1_cube_sanity | AUTO | **DONE** | run_postconfig: cube_exists=PASS(2544 rows); one_strategy=PASS(1 strategies); M2_exits_per_entry_vs_registry=PASS(cube [24] vs registry-now 24 (a diff |
| 2_grade_with_config_params | AUTO | **DONE** | AUTO (B2177): graded at manifest swing=20 span=20 -> output_b2197_sw20sp20_sw20sp20_grid_auto.json |
| 3_outlier_discrepancy_sweep | AUTO | **DONE** | AUTO (B2192): mechanical core executed by the battery (M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded exits) + the grader's union diagnosis-l |
| 4_three_leg_spot_check | AUTO | **DONE** | AUTO (B2177): spot_check_trades --n 50 at manifest params; ; wrote output_audit/output_b2197_sw20sp20_sw20sp20_spot_check.json |
| 6b_equivalence_class_check | AUTO | **DONE** | AUTO (B2192): the grader collapses identical outcomes - 17 combos carried across 97 distinct outcome classes in output_b2197_sw20sp20_sw20sp20_grid_au |
| 5_adversarial_lens_review | JUDGMENT | SKIPPED | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together |
| 6_post_fix_recheck | JUDGMENT | SKIPPED | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together |
| 7_implement_in_engine | JUDGMENT | SKIPPED | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together |
| 8_verdict_with_denominators | JUDGMENT | SKIPPED | PENDING-WAVE-REVIEW (b2197_sw20sp20): the wave-level review batch performs this step across all arms together |

**All AUTO steps DONE: True**

**Grid** {'P1_swing_length': 20, 'P6_span': 20} - carried 17 / distinct 97
**Best cell** is_ci_lo 0.107 (below the 0.333 noise floor) | is_sharpe 0.551 | fires 88 | exit hybrid_50pct_target | verdict BELOW_POWER_FLOOR
