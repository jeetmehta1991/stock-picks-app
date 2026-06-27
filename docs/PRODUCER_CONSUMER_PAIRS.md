# Producer-Consumer Pairs Registry

# Source: Council 139 Option-8 HYBRID Layer A per owner directive
# 2026-06-28 "How will we address the misses in design vs armed? I don't
# want to keep demanding adversarial reviews." per CHECKLIST #77 + #124.

## Purpose

**The structural fix for `feedback_monitor_design_vs_operational_gap` recurrence.**

This registry is the SINGLE SOURCE OF TRUTH for every producer-consumer pair
in the codebase where a script/module emits an artifact (JSON/CSV/parquet/log)
that another script/module consumes. Schema drift between producer and
consumer = silent miss class (B1010 + B1019 + B1042-Layer-1+2 lineage).

`backtest/tests/test_schema_contracts.py` auto-derives schema-contract tests
from this registry. ANY change to a producer's output schema OR consumer's
read schema must update this registry + the test pyramid will FAIL until both
sides match.

## Status discipline (Council 139 Layer D)

- `DESIGNED-NOT-VERIFIED` — code shipped but operational contract not proven
  via evidence artifact
- `OPERATIONALLY-VERIFIED` — schema contract test in pyramid PASS + linked
  evidence artifact (smoke output / AWS sentinel / integration test PASS)

Default for new entries is `DESIGNED-NOT-VERIFIED`. Promotion requires
explicit evidence link.

## Registry

| # | Producer file:line | Output artifact | Consumer file:line | Schema keys | Status | Evidence |
|---|---|---|---|---|---|---|
| 1 | `backtest/engine/backtest.py:584-605` | `engine_state.json` | `scripts/b1019_phase_1_runtime_monitor.py:76,98,197` | `simulated_day` (int), `cells_completed` (int), `status` (str: "running"\|"complete") | OPERATIONALLY-VERIFIED | `backtest/tests/test_b1043_blocker_fixes.py::test_b1043_f01_*` + B1043 F-01 fix |
| 2 | `backtest/results/writer.py:111` | `signal_fire_rates.json` (env-gated `EMIT_RAW_SIGNAL_FIRES=1`) | (analyzer; manual) | per-strategy raw fire counts | DESIGNED-NOT-VERIFIED | B901 ships; no automated consumer test |
| 3 | `backtest/data/signal_loader.py:inject_*_signals` (10 funcs) | screener `signals` dict mutated in-place | `backtest/signals/screener.py:screen_instrument` | per-source keys (e.g., `concentrated_sell`, `news_sentiment_score`, etc.) | OPERATIONALLY-VERIFIED | B1042 Audit-B verdict (10/10 wired); B1034 fix for concentrated_sell |
| 4 | `backtest/engine/backtest.py:564` | `trade_log_checkpoint.csv` | `scripts/b1019_phase_1_runtime_monitor.py:_check_a1_fire_rate`, `_check_b2_schema` | columns: `strategy`, `ticker`, `entry_date`, `exit_date`, `exit_method` | OPERATIONALLY-VERIFIED | B1043 F-04 fix (csv/parquet dispatch by extension) |
| 5 | (file) `output_audit/fire_count_measured_b660_full_universe.json` | B660 baseline | `scripts/b1019_phase_1_runtime_monitor.py:_load_baseline` | top-level `results` (list) -> per item `strategy`, `n_fires_long`, `n_fires_short`, `n_fires_avoid`, `calendar_year_span` | OPERATIONALLY-VERIFIED | B1043 F-03 fix |
| 6 | `backtest/results/writer.py:write_trade_log` | `trade_log.parquet` | `backtest/results/metrics.py:compute_strategy_metrics`, dashboards, sub-agent #5 walk-forward, B1019 post-run analyzer | columns: `strategy`, `ticker`, `entry_date`, `exit_date`, `direction`, `regime`, `exit_reason`, `entry_price`, `exit_price`, `category`, `confidence_tier`, `sector` | OPERATIONALLY-VERIFIED | Phase C v1 + v2 smoke runs produced + consumed |
| 7 | `backtest/results/writer.py:write_strategy_regime_matrix` | `strategy_regime_matrix.json` | dashboard generators | per-strategy x per-regime metrics | DESIGNED-NOT-VERIFIED | downstream readers exist but no schema-contract test |
| 8 | `backtest/results/writer.py:portfolio_metrics` | `portfolio_metrics.json` | `dashboard_phase_1a/data.js` | DEC-095 schema: `return`, `sharpe`, `max_dd`, `alpha`, `beta` | DESIGNED-NOT-VERIFIED | dashboard consumes but no schema-lock test |
| 9 | `backtest/engine/multiple_testing_correction.py` | `EXPLORATORY_STRATEGIES` set | `backtest/results/metrics.py::compute_strategy_metrics` | set of strategy name strings | OPERATIONALLY-VERIFIED | B1042 Audit-B verdict + EXPLORATORY tag downstream consumed |
| 10 | `backtest/config.py:SMC_PHASE` | global constant | `backtest/signals/smc_ict.py:compute_smc_signals` | str: "B-CANARY" \| "PRODUCTION" | OPERATIONALLY-VERIFIED | B1038 + B1041 tests in `test_b1038_smc_phase_canary.py` |
| 11 | `vendored/smartmoneyconcepts/` package | library namespace (smc.fvg, smc.ob, etc.) | `backtest/signals/smc_ict.py` + `backtest/tests/test_smc_spof_sentinel.py` | methods: `swing_highs_lows`, `ob`, `fvg`, `bos_choch`, `liquidity`, `retracements` | OPERATIONALLY-VERIFIED | B1039 SPOF sentinel test (15 tests) + Phase C v2 SMARTMONEYCONCEPTS_STATUS=1 sentinel |
| 12 | `backtest/util/holdout_guard.py` | `assert_no_holdout_intrusion()` function | `backtest/run_phase1a.py:main` (post-B1043) | callable raises HoldoutViolationError | OPERATIONALLY-VERIFIED | B1043 Sub-B fix + `test_b1043_subb_holdout_guard_wired_in_engine_entry` |
| 13 | AWS user-data sentinels (BOOT, PYTHON_VERSION, etc.) | S3 sentinel files | `scripts/launch_r5_master_4y_v2.sh` polling + Claude-side polling | filename + small text content | DESIGNED-NOT-VERIFIED | 14 sentinels documented at code-level but no automated reader |
| 14 | `scripts/b1019_phase_1_runtime_monitor.py` | `b1019_monitor.log` (stdout) | `scripts/launch_r5_master_4y_v2.sh` HALT-CRITICAL grep + watcher | string `"HALT-CRITICAL"` prefix | OPERATIONALLY-VERIFIED | B1042 + B1043 watcher logic + grep |
| 15 | `scripts/b1019_a5_phase_1_preflight_coverage_check.py` | `b1019_a5_preflight_report.json` | (launch script post-B1043; analyzer) | preflight gate result | DESIGNED-NOT-VERIFIED | B1043 F-07 invocation; downstream consumer not enforced |

## Future expansion (Phase 2 next batch)

Sweep codebase for remaining pairs:
- Signal-loader → producer key contracts (per-source: news, insider, institutional, etc.)
- Exit manager → trade outcome schema
- Regime classifier → daily regime sequence consumed by writer
- Dashboard data feeds (data.js + data.json)
- Engine env-check stub JSONs (8 ORPHAN by-design per B1042 Audit-C)

Target ~40 pairs total for full coverage.

## Schema-contract test pattern

For each registry row, `backtest/tests/test_schema_contracts.py` asserts:

1. **Producer emits canonical sample** — call producer with minimal valid
   inputs; capture artifact
2. **Consumer parses sample** — call consumer's reader on artifact; assert
   no exception
3. **All schema keys present** — assert artifact contains all keys in
   `Schema keys` column
4. **Consumer references all producer keys** — grep consumer source for
   key names; assert no orphan keys (forward-compat allowance)

Adding a new producer-consumer pair requires:
1. Add row to this registry
2. Verify schema test passes locally
3. Status starts at `DESIGNED-NOT-VERIFIED`
4. Promote to `OPERATIONALLY-VERIFIED` only when evidence link added
   (smoke output / AWS sentinel / integration test PASS)
