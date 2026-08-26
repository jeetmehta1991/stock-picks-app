# POST-CONFIG BATTERY REPORT - output_b2016_e1_sw10_span50

Source: output_audit/postconfig_ledger.json + output_audit/output_b2016_e1_sw10_span50_grid_auto.json (written by scripts/run_postconfig.py); rendered by scripts/postconfig_report.py; per CHECKLIST #77.

| step | class | status | evidence (truncated) |
|---|---|---|---|
| 1_cube_sanity | AUTO | **DONE** | B2034: 1 strategy, exits/entry [26], 138 entries, mega-caps NVDA+MSFT+TSLA present, cfg stamp 10/50 verified in-cube. Launched from 1151d777d with the |
| 2_grade_with_config_params | AUTO | **DONE** | B2034: tighten_breaker_block.py --swing-length 10 --min-n 10 -> output_audit/b2034_e1_sw10_span50_grid.json (post-S6-B2018c grader). Union diagnosis l |
| 3_outlier_discrepancy_sweep | AUTO | **DONE** | B2034: entries==grid max (138==138). Verdicts of 300: {184 NO_EXIT_SELECTABLE / 101 BELOW_POWER_FLOOR / 15 ZERO_FIRES}; rankable 101, carried 17, dist |
| 4_three_leg_spot_check | AUTO | **SKIPPED** | B2136 status corrected DONE -> SKIPPED (the status contradicted its own evidence). B2034: spot_check_trades.py --n 50 --swing-length 10 --ema-span 50: |
| 6b_equivalence_class_check | AUTO | **DONE** | B2034: top-10 carries 17 combinations across 10 DISTINCT outcome classes (45 distinct among 101 rankable) - the B1615 class-carry is active; no two ca |
| 5_adversarial_lens_review | JUDGMENT | DONE | B2034 lenses: (silent degradation) regime_flip cap-branch 100pct - extends S6-B2018a, unchanged by design (frozen engine for comparability). (duplicat |
| 6_post_fix_recheck | JUDGMENT | N/A | B2034: no fix shipped against this arm's pipeline this batch (the S6-B2018c grader fix predates this grade and is what it ran on). |
| 7_implement_in_engine | JUDGMENT | N/A | B2034: nothing admitted - admission is STEP 4 after the STEP-2 disjoint-ticker validation, which is the next owner gate (compute approval needed: ~344 |
| 8_verdict_with_denominators | JUDGMENT | DONE | B2034 verdict: sw10_span50 produced 138 fires on 50 tickers / 1y. CROSS-ARM (sw10 pair, cross-arm only per L376/L382): baseline span200 is_ci_lo -0.08 |

**All AUTO steps DONE: False**

**NO AUTO GRID** - step 2 produced no artifact.
