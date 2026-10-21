# S6-B3237 - regime-entry evidence, per side, IN-SAMPLE (B3139q-r88)

Source: `output_audit/b3237_direction_regime_audit_is.json` - scripts/direction_disaggregated_regime_audit.py --trade-log output_r5_merged_1_7/trade_log.csv --window is. Window: 17730 in-sample rows of 23043 for the 17 audited entries (5313 holdout-entered rows excluded - the holdout read is the owner's).

R5 is a Phase 1A-beta cube: run_phase1a.py turns the regime affinity OFF for phase 1a-beta, so every side traded in every regime that occurred and both sets below are OBSERVED (R5's window holds no crisis day). The entries bind only Phase-1B deployment - campaign engine runs are 1a-beta too.

KEEP = the side's trades in the entry's regimes; REMOVE = the side's trades in its default regimes (long: bull, neutral; short: every regime). Cells: trades @ mean net % per trade. 'prefers' is a display cut, not a gate: a gap of at least 0.5 points with at least 30 trades in each set (both CHOSEN, ARBITRARY-PENDING-JUSTIFICATION).

15 limiting two-sided entries (force_index_breakout and smc_bos_retest_entry admit every regime and are not listed).

| entry | regimes | long KEEP | long REMOVE | long prefers | short KEEP | short REMOVE | short prefers |
|---|---|---|---|---|---|---|---|
| adx_initiation | bear | 3 @ -7.12 | 11 @ -2.98 | too few | 4 @ -3.46 | 24 @ -2.62 | too few |
| avwap_252_breakout | bear, neutral | 783 @ +0.75 | 437 @ -1.17 | KEEP | 356 @ -5.98 | 617 @ -4.31 | REMOVE |
| awesome_oscillator | bear | 226 @ +2.78 | 167 @ -1.03 | KEEP | 107 @ -4.14 | 364 @ -3.21 | REMOVE |
| bollinger_tight | bull | 86 @ +1.02 | 98 @ +1.44 | no gap | 79 @ -1.07 | 123 @ -1.77 | KEEP |
| camarilla_s3_bounce | bear, crisis, neutral | 43 @ -1.54 | 61 @ +3.03 | REMOVE | 13 @ -3.98 | 64 @ -4.76 | too few |
| cmf_flip | bear, neutral | 873 @ +0.26 | 537 @ -0.62 | KEEP | 330 @ -4.32 | 936 @ -3.14 | REMOVE |
| macd_fast_crossover | bull | 557 @ -2.01 | 573 @ -1.91 | no gap | 1026 @ -2.27 | 1569 @ -2.45 | no gap |
| parabolic_sar_flip | bear | 405 @ +3.00 | 209 @ -1.89 | KEEP | 145 @ -2.79 | 603 @ -3.23 | no gap |
| ppo_crossover | bear | 381 @ +0.65 | 214 @ -0.46 | KEEP | 119 @ +1.83 | 599 @ -0.77 | KEEP |
| prev_day_low_bounce | bear, neutral | 106 @ -2.52 | 181 @ +2.28 | REMOVE | 45 @ -5.05 | 147 @ -2.52 | REMOVE |
| smc_inverse_fvg | bear, bull, neutral | 303 @ +1.21 | 145 @ +0.76 | no gap | 419 @ -4.79 | 419 @ -4.79 | no gap |
| supertrend_macd | bull | 18 @ +5.87 | 19 @ +4.99 | too few | 189 @ -1.32 | 357 @ -3.56 | KEEP |
| tema_dema | bear | 455 @ +3.05 | 266 @ -0.40 | KEEP | 202 @ -2.19 | 701 @ -2.92 | KEEP |
| ultimate_oscillator | bull | 98 @ +0.34 | 98 @ +0.34 | no gap | 111 @ -0.11 | 291 @ -2.59 | KEEP |
| williams_stoch_dual | bear | 117 @ -2.28 | 114 @ -1.64 | REMOVE | 86 @ -2.18 | 331 @ -2.72 | KEEP |

Tally: long KEEP: 6; long REMOVE: 3; long no gap: 4; long too few: 2; short KEEP: 6; short REMOVE: 4; short no gap: 3; short too few: 2
