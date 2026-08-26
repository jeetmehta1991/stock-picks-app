# POST-CONFIG BATTERY REPORT - output_b2016_e1_sw20

Source: output_audit/postconfig_ledger.json + output_audit/output_b2016_e1_sw20_grid_auto.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_report.py; per CHECKLIST #77.

| step | class | status | evidence (truncated) |
|---|---|---|---|
| 1_cube_sanity | AUTO | **DONE** | B2018: 1 strategy, exits/entry [26], 105 entries, run at frozen_sha b94d377fa (B2016). MSFT+TSLA present; NVDA ABSENT-BY-ZERO-FIRES: the same tickers- |
| 2_grade_with_config_params | AUTO | **DONE** | B2018: tighten_breaker_block.py --swing-length 20 --min-n 10 -> output_audit/b2018_e1_sw20_grid.json. Union diagnosis loss 0pct (105/105). REQUIRED A  |
| 3_outlier_discrepancy_sweep | AUTO | **DONE** | B2018: cube entries == grid max fires (105==105). Verdicts of 300 rows: {208 NO_EXIT_SELECTABLE / 45 BELOW_POWER_FLOOR / 47 ZERO_FIRES} - ZERO combina |
| 4_three_leg_spot_check | AUTO | **SKIPPED** | B2136 status corrected DONE -> SKIPPED (the status contradicted its own evidence). B2018: verify_spotcheck_coverage.py smc_breaker_block_long exit 0;  |
| 6b_equivalence_class_check | AUTO | **N/A** | B2018: no ranked top-N exists to de-duplicate - 0 combinations carried in this arm. The check has no object; it re-arms the moment any grid carries ca |
| 5_adversarial_lens_review | JUDGMENT | DONE | B2018 all lenses: (fail-crash) grader loader vs string-dated cache file - FIXED+pinned this batch; family enumerated (5 more un-coerced set_index('dat |
| 6_post_fix_recheck | JUDGMENT | DONE | B2018: the one fix this config surfaced (grader loader) re-ran through the FULL grade of both cubes - successful completion at 0pct diagnosis loss is  |
| 7_implement_in_engine | JUDGMENT | N/A | B2018: nothing admitted - the E1 P1 verdict is CROSS-ARM and waits for sw30+sw50 (L376/L382); within-arm tightening carried 0 combos. |
| 8_verdict_with_denominators | JUDGMENT | DONE | B2018 verdict: sw20 produced 105 fires on 50 tickers / 1y (precheck floor 10: passed at 49 baseline fires / 21 tickers). Within-arm tightening NOT GRA |

**All AUTO steps DONE: False**

**NO AUTO GRID** - step 2 produced no artifact.
