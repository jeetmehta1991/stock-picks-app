<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1234 2026-07-07 doc-sync sweep -->

<!-- COUNCIL 278-287 SYNC BANNER (B1234 2026-07-07) - READ FIRST -->
> **Sync status:** Body may contain refs stale as of 2026-06-27 or earlier. Canonical current state (B1231):
> - `len(ALL_STRATEGIES) = 219` (post-B1189 DELETE dxy_headwind); `STRATEGIES_DISABLED_MISSING_PRODUCER = set()`
> - Test count: 858 passed, 2 skipped on test_unit + test_integration
> - CHECKLIST items #1-#157, LEARNINGS through L202, latest batch B1231
> - Councils 278-287: 40 strategies loosened + 11 silent misses remediated + 25+ producer coverage audits + historical timeline finding + 2 critical bugs FIXED via graceful degradation
> - Stage 4 walks: ARCHIVED to `archive/2026-07-07-stage-4-walks-complete/`
> - Sprint 5 tickets: 3 queued (S5-B1214 HIGH / S5-B1216 MED post-B1230 correction / S5-B1212 MED)
> - Comprehensive coverage report: `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

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
| 16 | `backtest/data/signal_loader.py:73 inject_news_sentiment_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `news_sentiment_mean` (float), `news_sentiment_5d` (float), `news_sentiment_shift` (float), `news_count_7d` (int) | DESIGNED-NOT-VERIFIED | B932 P0 commit 11/11; no per-key schema-contract test |
| 17 | `backtest/data/signal_loader.py:108 inject_institutional_persistence_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `institutional_persistence_growing` (bool), `institutional_persistence_strong` (bool), `persistence_quarters_buying` (int), `total_active_holders` (int) | DESIGNED-NOT-VERIFIED | B931 P0 commit 10/11; B906 MEASUREMENT_DISPUTED |
| 18 | `backtest/data/signal_loader.py:152 inject_short_interest_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `short_interest_pct` (float), `days_to_cover` (float) | DESIGNED-NOT-VERIFIED | B930 P0 commit 9/11; consumed by squeeze_setup_long + short_borrow_trap_avoid |
| 19 | `backtest/data/signal_loader.py:185 inject_search_volume_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `search_volume_index_recent` (float), `search_volume_pct_change_7d` (float), `search_volume_spike` (bool), `retail_attention_score` (float) | DESIGNED-NOT-VERIFIED | B929 P0 commit 8/11; pytrends per-ticker cache |
| 20 | `backtest/data/signal_loader.py:216 inject_earnings_surprise_yoy_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `yoy_surprise_high` (bool), `yoy_surprise_negative` (bool) | DESIGNED-NOT-VERIFIED | B928 P0 commit 7/11; df-dependency w/ PEAD |
| 21 | `backtest/data/signal_loader.py:246 inject_pead_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `days_since_last_earnings` (int), `within_pead_window` (bool), `earnings_eps_yoy_growth` (float), `earnings_announcement_return` (float), `pead_positive_surprise` (bool), `pead_negative_surprise` (bool) | DESIGNED-NOT-VERIFIED | B927 P0 commit 6/11; ohlcv_df dependency |
| 22 | `backtest/data/signal_loader.py:286 inject_classification_change_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `classification_changed_recent` (bool), `days_since_classification_change` (int), `classification_change_to_tech` (bool), `classification_change_to_defensive` (bool), `classification_change_from_tech` (bool) | DESIGNED-NOT-VERIFIED | B924 P0 commit 4/5; reads sector_history.csv (B910 staleness lineage) |
| 23 | `backtest/data/signal_loader.py:320 inject_insider_buying_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `insider_cluster_active` (bool), `insider_unique_buyers_30d` (int), `insider_total_shares_bought_30d` (float), `insider_director_buyers_30d` (int), `insider_officer_buyers_30d` (int) | DESIGNED-NOT-VERIFIED | B923 P0 commit 3/5; ~10 consumers |
| 24 | `backtest/data/signal_loader.py:357 inject_insider_signal_keys` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `concentrated_sell` (bool), `cfo_buy` (bool), `large_dollar_buy` (bool), `ceo_buy` (bool), `director_only_buy` (bool), `cluster_buy` (bool), `signal` (str), `buy_count` (int), `sell_count` (int) | OPERATIONALLY-VERIFIED | B1034 silent-gap fix; B1010 strat_insider_cluster_concentrated_sell_short consumer |
| 25 | `backtest/data/signal_loader.py:403 inject_institutional_signals` | screener `signals` dict keys | `backtest/signals/screener.py:screen_instrument` | `institutional_signal` (str), `institutional_strong_buy` (bool), `institutional_buy` (bool), `institutional_negative` (bool), `institutional_new_positions` (int), `institutional_increased` (int) | OPERATIONALLY-VERIFIED | B921 P0 commit 1/11; B918 `new_positions` bug fix; engine parity test |
| 26 | `backtest/engine/exit_manager.py:694 process_day_exits` | `ClosedTrade` dataclass instances | `backtest/engine/backtest.py:1050` | fields per `ClosedTrade` (line 101): `trade_id`, `entry_date`, `exit_date`, `exit_price`, `exit_reason`, `pnl_pct`, `hold_days`, `mae`, `mfe`, etc. | DESIGNED-NOT-VERIFIED | dataclass-level contract enforced at construction; no integration schema-test |
| 27 | `backtest/engine/exit_strategies.py:1487 EXIT_STRATEGIES` | dict mapping exit-method name → callable | `backtest/engine/backtest.py` cube-replay path + `backtest/results/writer.py` exit-comparison sub-pipeline | dict[str, Callable]; per-method returns base_result dict (entry_price, exit_price, entry_date, exit_date, exit_reason, direction, pnl_pct) | DESIGNED-NOT-VERIFIED | 26 exit methods (B487 SM2 + Batches 282-285); per-method unit tests but no registry-level schema lock |
| 28 | `backtest/engine/regime_filter.py:151 classify_regime` | regime-string sequence | `backtest/engine/backtest.py:953 get_regime_context` + downstream daily-regime emit | str: "bull" \| "neutral" \| "bear" \| "crisis" (per MARKET_REGIMES config) | OPERATIONALLY-VERIFIED | `test_batch642_regime_classifier_cleanup.py` + `test_acceptance_functional.py` |
| 29 | `backtest/engine/regime_selector.py:107 STRATEGY_REGIME_AFFINITY` | dict[strategy_name, set[regime_str]] | `backtest/engine/backtest.py:1288,1568,1957,2033 should_strategy_fire_in_regime` + `backtest/signals/screener.py` (gate references) | dict[str, set[str]]; values subset of {"bull","neutral","bear","crisis"} | OPERATIONALLY-VERIFIED | `test_batch417_regime_affinity.py` + `test_b953_section_05_regime_affinity_lineage.py` |
| 30 | `scripts/build_dashboard_phase_1a.py:577,587` | `dashboard_phase_1a/data.json` + `data.js` (`const STAGE2_DATA = ...`) | `dashboard_phase_1a/index.html` + `app.js` (browser fetch / window read) | 12-tab Phase 1A trade analysis payload (Sprint 6.5 deliverable) | DESIGNED-NOT-VERIFIED | dashboard renders but no schema-lock test on payload structure |
| 31 | `scripts/build_dashboard_stage_2.py:2138,2140` | `dashboard_stage_2/data.json` + `data.js` | `dashboard_stage_2/index.html` (browser) | DECs/BUGs/INVs registry payload (481 visible DECs / 250 visible BUGs / 731 matrix) | DESIGNED-NOT-VERIFIED | `test_batch419_dashboard_tabs.py` exists but does not lock full schema |
| 32 | `scripts/build_dashboard_sprint0a.py:1160,1165` | `dashboard_sprint0a/data.json` + `data.js` (`const DASHBOARD_DATA = ...`) | `dashboard_sprint0a/index.html` | API endpoint coverage payload (109 CACHED / 28 ACCESSIBLE_NOT_CACHED / 40 TIER_BLOCKED) | DESIGNED-NOT-VERIFIED | no schema lock |
| 33 | `backtest/results/writer.py:908-909` | `batch163_stub_results.json` | `backtest/tests/test_integration.py` + (manual review) | dict[stub_name, result_str_or_"FAILED:..."] | DESIGNED-NOT-VERIFIED | Batch 163 stub probe; consumer is test + manual |
| 34 | `backtest/results/writer.py:1064-1066` | `dec_constants_verification.json` | (manual review; no automated reader) | DEC constant import-verification dict | DESIGNED-NOT-VERIFIED | Batch 166 audit emitter; **ORPHAN candidate** — no automated downstream consumer |
| 35 | `backtest/results/writer.py:1076 portfolio_summary` | `portfolio_summary.json` | `backtest/results/metrics.py:compute_portfolio_summary` (producer) + dashboards/manual | per-portfolio summary dict | DESIGNED-NOT-VERIFIED | no schema-contract test |
| 36 | `backtest/results/writer.py:1097 equity_curve` | `equity_curve.parquet` | `scripts/analyst_overlay_from_trade_log.py` + `scripts/run_t0_close_out.py` + `scripts/merge_batch_outputs.py` + dashboards | columns: `date`, `equity` (from `portfolio.equity_curve` list-of-tuples) | DESIGNED-NOT-VERIFIED | `test_batch464_writer_outputs_registry.py` registers existence but not column lock |
| 37 | `backtest/results/writer.py:1103 benchmark_curve` | `benchmark_curve.parquet` | (analyzer; dashboards) | columns: `date`, `equity` (benchmark series) | DESIGNED-NOT-VERIFIED | paired with equity_curve; no schema-lock test |
| 38 | `scripts/build_ticker_lifecycle_events.py:49` | `data_prefetch/derived/ticker_lifecycle_events.parquet` | `backtest/tests/test_batch400_audit_status.py` + `backtest/tests/test_unit.py` (DEC-234/380 verification) | columns: per ticker lifecycle (corp-actions, delistings) | DESIGNED-NOT-VERIFIED | Batch 374 DEC-234/380; consumers exist in tests not engine path |
| 39 | `scripts/build_t1a_correlation_matrix.py:135` | T1a pair-wise correlation parquet at user-specified `--output` | (no automated grep-found consumer) | columns: `ticker_a`, `ticker_b`, `correlation` | DESIGNED-NOT-VERIFIED | **ORPHAN candidate** — Batch 374 B-3 precompute; no in-engine reader located via grep |
| 40 | `scripts/build_strategy_roster.py:797` | `STRATEGY_ROSTER.md` (repo root) | (owner manual review; per `feedback_strategy_roster_doc_maintenance` standing reference) | per-strategy table + SIGNAL_GLOSSARY section | OPERATIONALLY-VERIFIED | owner directive 2026-06-04 names this as canonical Stage 4 reference; consumed by Stage 4 walks |
| 41 | `scripts/build_verification_matrix.py:783,789` | `VERIFICATION_MATRIX.md` + `verification_matrix.json` | (manual review; CLAUDE.md ground-truth reference for wired=yes verification per `feedback_wired_means_engine_consumed`) | engine-consumption ground truth (coverage-driven) | OPERATIONALLY-VERIFIED | CLAUDE.md cites as replacing wired=yes grep heuristic |
| 42 | `scripts/build_walk_verdict_ledger_v2.py:203` | `output_audit/walk_verdict_ledger_v2.json` | (owner manual + per-strategy dossier builds; Council 88/95 etc. references) | walk verdict ledger payload | DESIGNED-NOT-VERIFIED | consumer is human review, not automated |

## Phase 2 expansion status (B1044 sub-agent A sweep)

Phase 2 (B1044 Council 140 Option-5 fan-out): expanded 15 → 42 pairs across 6 categories per Sub-agent A scope. Categories swept:

- **Category 1** (signal_loader inject_*): 10 rows (rows 16-25) — full coverage of all 10 `inject_*_signals` extraction functions from B921-B932 P0 commits.
- **Category 2** (exit_manager / exit_strategies): 2 rows (rows 26-27) — `process_day_exits` + `EXIT_STRATEGIES` registry of 26 methods.
- **Category 3** (regime_filter / regime_selector): 2 rows (rows 28-29) — `classify_regime` + `STRATEGY_REGIME_AFFINITY`.
- **Category 4** (Dashboard data feeds): 3 rows (rows 30-32) — phase_1a, stage_2, sprint0a dashboards.
- **Category 5** (writer engine env-check stubs): 5 rows (rows 33-37) — batch163_stub_results, dec_constants_verification, portfolio_summary, equity_curve, benchmark_curve. (B1042 Audit-C documented 8 ORPHAN by-design + 19 wired; 5 highest-value rows registered.)
- **Category 6** (scripts/build_* output artifacts): 5 rows (rows 38-42) — ticker_lifecycle_events, t1a_correlation_matrix, STRATEGY_ROSTER.md, VERIFICATION_MATRIX.md, walk_verdict_ledger_v2.

### Findings (orphan / asymmetric pairs surfaced)

- **Row 34** `dec_constants_verification.json` — emitter exists but no automated downstream consumer located via grep. Candidate ORPHAN-BY-DESIGN per B1042 Audit-C 8-stub class.
- **Row 39** `build_t1a_correlation_matrix.py` output parquet — no in-engine grep-found consumer. Batch 374 B-3 precompute was queued for engine path that did not ship. Candidate ORPHAN; owner should disposition: (a) wire consumer or (b) mark ORPHAN-BY-DESIGN in registry.
- **Row 2** (existing) `signal_fire_rates.json` and **Row 13** (existing) AWS sentinels remain `DESIGNED-NOT-VERIFIED`.

### Remaining Phase 3 sweep targets

- Per-data-source caches (`data_prefetch/<api>/<endpoint>/`) and their producers (refresh_*.py / scripts/build_*.py for tier universes / sector_history / aaii / fomc / etc.).
- The 8 ORPHAN-BY-DESIGN engine env-check stubs from B1042 Audit-C — register explicitly with `ORPHAN-BY-DESIGN` status if owner approves the category.
- Per-strategy producer chains (chart_patterns.py, candlestick.py, smc_ict.py etc.) → screener.py consumer pairs.

## Schema-contract test pattern

Tests live in TWO files:
- `backtest/tests/test_schema_contracts.py` — Phase 1 seed (11 tests; rows 1, 4, 5)
- `backtest/tests/test_schema_contracts_phase2.py` — Phase 2 expansion (43 tests; rows 2, 3, 6, 7, 8, 10, 12; Council 140 Option-5)

For each registry row, the tests assert:

1. **Producer emits canonical sample** — call producer with minimal valid
   inputs; capture artifact
2. **Consumer parses sample** — call consumer's reader on artifact; assert
   no exception
3. **All schema keys present** — assert artifact contains all keys in
   `Schema keys` column
4. **Consumer references all producer keys** — grep consumer source for
   key names; assert no orphan keys (forward-compat allowance)

### Phase 2 test patterns (Council 140 Option-5)

The Phase 2 module adds 5 standardized patterns invokable as parametrized
tests for fast expansion. Each pattern has explicit assertion + failure
message per `feedback_silent_failure_pairing_rule`.

**Pattern P2-A: inject_* function importability + signature contract**
```python
@pytest.mark.parametrize("fn_name,expected", INJECT_FUNCTIONS.items())
def test_schema_contract_inject_function_importable_and_signature(
        fn_name, expected):
    fn = getattr(signal_loader, fn_name)
    sig = inspect.signature(fn)
    assert list(sig.parameters)[0] == "signals"
```
Used for: 10 inject_*_signals functions in signal_loader.py (registry row 3).

**Pattern P2-B: producer docstring documents emitted keys**
```python
doc = inspect.getdoc(fn)
missing = [k for k in expected_keys if k not in doc]
assert not missing, "silent producer = B273/B1034 class"
```
Used for: any producer (catches B273/B1034 silent-gap failure class).

**Pattern P2-C: consumer-side grep reference**
```python
content = consumer_path.read_text()
assert "producer_name" in content
```
Used for: SMC_PHASE consumer in smc_ict.py + holdout_guard consumer in
run_phase1a.py + 10 inject_* consumers in screener.py.

**Pattern P2-D: producer constant value enum**
```python
assert config.SMC_PHASE in ("B-CANARY", "PRODUCTION")
```
Used for: SMC_PHASE flag (row 10).

**Pattern P2-E: producer behavior contract (raises on bad input)**
```python
with pytest.raises(HoldoutViolationError):
    assert_no_holdout_intrusion([intruder], caller_name="test")
with HoldoutUnlock("reason"):
    assert_no_holdout_intrusion([intruder], caller_name="test")  # accepts
```
Used for: holdout_guard (row 12).

Adding a new producer-consumer pair requires:
1. Add row to this registry
2. Pick the right pattern (P2-A through P2-E) for the contract
3. Add parametrized test entry in `test_schema_contracts_phase2.py`
4. Verify schema test passes locally
5. Status starts at `DESIGNED-NOT-VERIFIED`
6. Promote to `OPERATIONALLY-VERIFIED` only when evidence link added
   (smoke output / AWS sentinel / integration test PASS)
