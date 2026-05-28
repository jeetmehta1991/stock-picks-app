# Phase 1A-beta cube — living status

**Single living doc.** Updated incrementally per batch. Supersedes the separate `PHASE_1A_BETA_OPTIMIZATION_FRAMEWORK.md` + `PHASE_1A_BETA_STAGE_D_PILOT_BATCH_381.md` + `STAGE_4_MONITORING_AUDIT.md` per owner directive 2026-05-26 (consolidate vs delete).

**Cross-ref:** [`PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md`](PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md) is the canonical reference for the cube → optimization → review → implementation → 1A-α-gate pipeline (locked 2026-05-28).

**Source attribution (per CHECKLIST #77):** owner directives across Batches 376-386 (cube optimization sequence) + Batch 372 framework decisions. Code SSOT: `backtest/engine/backtest.py` + `backtest/run_phase1a.py` + `scripts/monitor_phase_1a_beta_health.sh`. Data SSOT: companion JSON files in repo root.

---

## Run-readiness status

**Phase 1A-beta full re-run on Hetzner: PAUSED till further notice** (owner directive 2026-05-26).

| Component | Status | Evidence |
|---|---|---|
| Cube auto-enable flags | ✅ shipped | `[Batch 377/383/384/386]` banners in run_phase1a.py output |
| Engine cap removal | ✅ shipped | Batches 377 + 383 (cap + DD halt) |
| Engine gate removal | ✅ shipped | Batch 384 (regime affinity + event suppression) |
| Screener candidate throughput | ✅ shipped | Batch 386 (max-cands 30 → 200) |
| Surgical threshold tuning | ✅ shipped | Batch 385 (buyback_8k 3→5 days) |
| Intermediate-progress monitor | ✅ shipped (3 layers) | shell `scripts/monitor_phase_1a_beta_health.sh` (Batch 377 single-instance baseline) + Python `scripts/monitor_phase_1a_beta_health.py` (Batch 394 14-check expansion W1-W14 with engine-side wall-time kill + watchdog backup) + multi-instance wrapper `scripts/aws_batch395_monitor.py` (Batch 395, polls S3 heartbeats across 5 instances) |
| Engine wall-time guard | ✅ shipped | Batch 394: `--warn-run-hours 4.0` auto-WARN + `--max-run-hours 6.0` hard-kill `sys.exit(1)` with final checkpoint flush. Auto-set for `--phase=1a-beta`. |
| Cube-replay pool parallelism | ✅ shipped + activated | Batch 394: `_pool_cube_replay_worker` wraps `save_all_outputs` strategy-loop with `pool.starmap`; defers `_teardown_screen_pool` so same spawn pool services screen + cube. |
| Year + 100-day milestone telemetry | ✅ shipped + activated | Batch 394: engine emits `[MILESTONE-YEAR]` + `[MILESTONE-100D]` log lines with direction-balance, top-strategies, zero-fire counts. Monitor regex-parses both. |
| AWS 5-batch orchestration | ✅ shipped | Batch 395: 7 scripts (bootstrap.sh, upload_data.py, splits.py, launch.py, monitor.py, merge.py, teardown.py) for parallel cube run across 5 × c7a.4xlarge on AWS. |
| Action-taking monitor (HB-stale auto-kill + per-poll digest) | ✅ shipped | Batch 411 (2026-05-27): `aws_batch395_parallel.py` reads S3 heartbeats every poll; stale > 30min auto-terminates + re-queues; one-line `[DIGEST hh:mmZ b1=DONE ...]` digest line per poll replaces dead-monitor antipattern. Codified L162 / CHECKLIST #91. |
| Vectorized cube-exit fast path (Tier 1) | ✅ shipped, **flag DEFAULT OFF** | Batch 412 (2026-05-28): 9 Tier 1 methods in `exit_strategies_vectorized.py` (time_stop_10d/20d, class_time_stop, trailing_5/10/15pct, fixed_4r_2r, r_multiple_2r/3r). Dispatch via `USE_VECTORIZED_EXITS` flag in `exit_strategies.py`; CLI opt-in `--vectorized-cube-exits` in `run_phase1a.py`. Byte-identical to scalar (36 unit + 3 golden cube regression tests pass; 707 unit + 149 integration green). Targeted ~10-12% engine speedup. **Activation deferred till after current AWS run completes (owner directive).** Tier 2 (7 moderate methods) follows in Batch 413. |
| Vectorized cube-exit fast path (Tier 2) | ✅ shipped, **flag DEFAULT OFF** | Batch 413 (2026-05-28): 8 Tier 2 methods added to `exit_strategies_vectorized.py` (atr_trail_1x/2x, atr_trail_mae_conditional, break_even_at_1r, breakeven_plus_trail, chandelier_3x, mfe_lockin_trail, hybrid_50pct_target). DEC-311 rolling-ATR EWM preserved exactly via pandas idiom; phase-transition state machines (pre-1R/post-1R, pre-BE/post-BE, pre-target/post-target) vectorized via `_first_true(bool_array)` index then per-segment cumulative-max stop levels. Scalar asymmetry preserved: `hybrid_50pct_target` shorts have NO close-based hard stop (scalar `if direction == "long" and close <= stop:` only checks longs). 17 vectorized methods total (Tier 1 + Tier 2); Tier 3 (8 gnarly methods with external-signal lookups) deferred to Batch 414. **Cumulative speedup target when activated: ~20-25% engine wall** (3h → ~2.3h per batch). Tests: 70 unit + 3 golden cube regression + 707 unit + 149 integration = 929/929 green. |
| STRATEGY_EXIT_OVERRIDE per-cell winners (Batch 414) | ✅ shipped | Batch 414 (2026-05-28): 9 STRATEGY_EXIT_OVERRIDE entries derived from `output_batch395_final` cube + `optimize_strategies_from_cube.py` (Lens A Dim D best-exit-pairing). All 9 pair with `breakeven_plus_trail`, pass 4 of 5 DEC-426 gates (n≥30, p<0.05 Bonferroni, t≥3.4, R:R≥2.0; PSR<0.95) AND fire_rate ≥ 0.95 (Batch 266 cube-hardening guardrail). Strategies: `bollinger_tight`, `xs_momentum_top_decile` (updated from class_time_stop), `cmf_flip`, `monthly_bias_momentum_long` (updated from trail_pct=0.25), `xs_quality_top_quintile_long`, `pead_long`, `pairs_mean_reversion_long`, `adx_initiation`, `xs_low_beta_long` (updated from trail_pct=0.25). **NOT shipped:** 12 strategies that "won" with `earnings_blackout` in the same cube had fire_rate=0.000 (curve-fit on no_earnings_known fall-through; cube's signals_at_entry dict lacks ticker/strategy_name keys → `fetch_earnings_dates("")` returns []). Batch 415 follow-up: inject ticker into signals dict + re-run cube + re-evaluate. Walk-forward (DEC-505) is the next-Stage gate for the shipped 9. |
| Stage 6 walk-forward (Batch 414 cells) | ✅ executed; **1A-α GATE: LOCKED** | `scripts/walk_forward_batch414_cells.py` ran DEC-505 4-fold expanding-window walk-forward at (strategy × breakeven_plus_trail) CELL level. Results: `output_batch395_final/walk_forward_batch414_cells.json`. **All 9 strategies FAIL the 1A-α gate** (Sharpe ≥ 0.7 OOS in ≥1 regime). Best OOS Sharpe across 9 strategies × 4 folds = **0.419** (bollinger_tight fold_2). Cross-check: strategy-level `walk_forward_validation.csv` shows all 9 = `FAILS_BOTH` verdict. **Implication:** Phase 1B-α agent overlay ($300 Haiku budget per CLAUDE.md owner-gate rule) **NOT eligible to commit** on current cube. Notable: OOS Sharpe consistently exceeds IS Sharpe across most strategies (bull-market beta exposure in 2024-2026 OOS years), so the result is NOT a curve-fit signal but the cube ceiling is genuinely below 0.7. Loop back per locked-workflow Stage 4 → re-optimize entry-side (Dim A thresholds + Dim B compound-logic restructure for the 31 COMPOUND_RESTRICTIVE) → re-run cube → re-walk-forward. |
| Process-failure feedback memory | ✅ saved | `feedback_monitor_intermediate_counts.md` + `feedback_audit_recommendations_against_existing_directives.md` + `feedback_no_write_only_md_files.md` |
| Smoke validation (50-tkr × 3mo) | ✅ green | output_batch_386_smoke (0 cap / 0 DD / 0 regime / 0 event skips) |

## Auto-enabled cube flags (when `--phase=1a-beta`)

```
[Batch 377] --no-portfolio-cap       (Batch 203 cap @25 bypassed)
[Batch 383] --no-dd-halt             (DEC-515 Level 6 + drawdown_suspend bypassed)
[Batch 384] --no-regime-affinity     (Batch 203/293 affinity bypassed)
[Batch 384] --no-event-suppression   (DEC-348 FOMC/CPI/NFP/earnings bypassed)
[Batch 386] --max-cands 30 → 200     (screener output throughput raised)
Status: Agents: DISABLED | Max cands/day: 200
```

## What still applies in cube eval (intentional)

| Gate | Why kept | Source |
|---|---|---|
| Liquidity gate | Low-volume tickers are real-world non-tradable | `universe.py` filter |
| Ticker uniqueness | Cube replay already simulates exits per trade; concurrent same-ticker would skew | `backtest.py:1003` |
| Cash sufficiency | Engine cash math is invariant | `portfolio.py:373` |
| Stopout cooldown DEC-018 (5d) | Strategy-level rule, not a global throttle | `regime_selector.py` |
| no_next_bar | End-of-data edge | `backtest.py` |

---

## 99.96% rejection math (pre-Batch-377)

Phase 1A-beta single-batch baseline run (2026-05-26): ~970K candidates → 361 trades = 0.037% conversion. Compound gate filtering rejected 99.96%:

| Gate | Class | Was | Now |
|---|---|---|---|
| Portfolio cap (Batch 203) | Capital protection | min(25, regime_cap) | bypassed |
| DD halt (DEC-515 Level 6) | Capital protection | 15% DD halt | bypassed |
| Regime affinity | A-priori roster filter | STRATEGY_REGIME_AFFINITY | bypassed |
| Event suppression | Live news-risk | DEC-348 windows | bypassed |
| max-cands cap | Live agent cost | 30/day | 200/day |
| Per-strategy AND compound | Strategy logic | strategy-specific | surgical tune (1 done; rest deferred) |

---

## Empirical data references (data files)

The following JSON files contain machine-readable per-strategy data for the next-run analysis pipeline:

- `PHASE_1A_BETA_BEST_EXIT_PER_STRATEGY.json` — best exit method per fired strategy (Sharpe-proxy ranking, 17 strategies with cube n≥5; data derived from output_phase_1a_beta_single_local/ pre-Batch-369 run; will be regenerated post-Batch-382)
- `PHASE_1A_BETA_PRODUCER_ZERO_AUDIT.json` — per-strategy clause-fail audit for 49 PRODUCER_LAYER_ZERO strategies. CAVEAT: 9 of 49 were FALSE positives (Stage D pilot Batch 381 showed they actually produce candidates; cov=0% finding was downstream-rejection artifact). True count closer to 40.
- `PHASE_1A_BETA_THRESHOLD_OPTIMIZATION.json` — per-strategy gate-clause distance analysis (BINDING vs LOOSE per clause)
- `PHASE_1A_BETA_STAGE_D_PILOT_BATCH_381.json` — Stage D 150-tkr 1y pilot summary

## Stage D pilot validation (Batch 381 absorbed)

Stage D 150-tkr × 1y pilot (output_stage_d_batch381_pilot/) with `--no-portfolio-cap` only confirmed:
- 39 strategies fired (vs 31 in prior 4y baseline)
- Cap-saturation skips: 0 (was ~36,700 baseline)
- 21 NEW strategies firing including `ichimoku_cloud_breakout` (9; was 6,821 candidates → 0), `pivot_r1_breakout` (4; was 9,314 → 0), SMC family awakened

**New finding from pilot**: DEC-515 Level 6 DD halt fired repeatedly when cap removed (DD reached -22% to -36%). Resolved Batch 383 (`--no-dd-halt` auto-enabled).

---

## Per-strategy data (high-impact subset)

### Best-exit-per-strategy (pre-cube reference; regenerate post-Batch-382)

| strategy | best_exit | n | WR | PF | mean_pp | sharpe_proxy |
|---|---|---:|---:|---:|---:|---:|
| xs_low_beta_long | earnings_blackout | 28 | 75.0% | 3.39 | +13.32 | +2.37 |
| pre_fomc_long_sleeve | earnings_blackout | 6 | 83.3% | 23.73 | +8.25 | +1.76 |
| po3_bullish | earnings_blackout | 19 | 63.2% | 3.40 | +17.94 | +1.46 |
| pead_long | multi_tier_partial | 6 | 66.7% | 4.63 | +1.36 | +1.41 |
| xs_quality_top_quintile_long | trailing_15pct | 22 | 45.5% | 2.96 | +10.07 | +1.11 |
| xs_momentum_top_decile | earnings_blackout | 8 | 50.0% | 2.17 | +27.12 | +0.83 |
| orb_stocks_in_play_short | r_multiple_2r | 21 | 38.1% | 1.28 | +1.39 | +0.48 |
| vix_backwardation_long | (no positive-Sharpe exit) | 9 | 33.3% | 0.74 | -1.72 | -0.41 |

Per-strategy STRATEGY_EXIT_OVERRIDE updates deferred until post-Batch-382 empirical cube data per `project_no_apriori_strategy_pruning.md`.

### Top missing-producer binding keys (49 PRODUCER_LAYER_ZERO subset)

Per `PHASE_1A_BETA_PRODUCER_ZERO_AUDIT.json` clause-fail audit (caveat: Batch 381 pilot showed 9 of 49 are false positives):

| Missing/sparse key | Strategies blocked | Family root cause |
|---|---:|---|
| classification_changed_recent (cov=0%) | 7 | universe.py classification-change producer emit-rate audit |
| smc_bos_bearish (cov=0%) | 3 | vendored smartmoneyconcepts library |
| force_index_breakout (cov=0%) | 2 | technical.py producer key |
| smc_bos_bullish (cov=0%) | 2 | vendored smartmoneyconcepts library |

### Surgical threshold change (Batch 385)

`buyback_8k_recent_long`: `days_since_8k <= 3` → `<= 5`
Justification: Lopez-Lira-Tang 2023 5-day post-8K reaction window + empirical 86/86 fires at the 3-day boundary.

All other per-strategy threshold tuning **deferred** until post-Batch-382 empirical cube data (per `project_no_apriori_strategy_pruning.md`).

---

## Expected next-run characteristics (Batch 382 when unpaused)

- Universe: 1937 tickers × 4y (2022-05-05 → 2026-05-05)
- Engine: `--phase=1a-beta` auto-enables all 5 cube flags
- Wall time: ~10-15h on Hetzner CPX62
- Expected trade count: 5K-15K (vs prior 361)
- Expected strategies firing: 60+ (vs prior 31)
- Cube cells populated: 1,500+ (vs prior 425)
- Verdict cube: real n≥30 cells for first time (prior was 100% INSUFFICIENT_SAMPLE)
- Monitor: `scripts/monitor_phase_1a_beta_health.sh` armed for intermediate trade-count health (abort early at <0.5× baseline ratio)

---

## Post-Batch-382 work (queued, empirical-first)

Per `project_no_apriori_strategy_pruning.md`, all per-strategy tuning + roster decisions are deferred until empirical cube data exists:

1. Re-derive per-strategy best-exit-method from new trade_log
2. Threshold optimization for fired strategies (with statistical power)
3. Roster pruning recommendations (strategies that fired N≥30 but failed all DEC-426 5-Gate checks)
4. Phase 1B-α winners.parquet extraction
5. Owner gate at 1A-α (rules-only Sharpe ≥ 0.7 OOS) before $300 1B-α budget commits

---

## Cross-references

- Code: `backtest/engine/backtest.py` (cube flags) + `backtest/run_phase1a.py` (auto-enable)
- Monitor: `scripts/monitor_phase_1a_beta_health.sh`
- Drift audit: `scripts/drift_audit_pre_phase_1a_beta.py` (regenerates `PHASE_1A_BETA_PRE_RUN_ALIGNMENT_AUDIT.md`)
- Forensic baseline: `PHASE_1A_BETA_PER_STRAT_EXIT_FORENSIC.md` (CLAUDE.md PAUSE flag references this)
- Quant correctness: `QUANT_CORRECTNESS_AUDIT_DEC_246.md` (referenced by `backtest/results/ab_orchestrator.py` + `backtest/tests/test_unit.py`)
- Memory: `feedback_monitor_intermediate_counts.md`, `feedback_audit_recommendations_against_existing_directives.md`, `feedback_no_write_only_md_files.md`, `project_no_apriori_strategy_pruning.md`, `project_phase_1a_beta_is_exit_cube.md`
