# VERIFICATION_MATRIX.md

**Generated:** see `scripts/build_verification_matrix.py`. Per-item ground truth for ALL visible DECs + BUGs in scope (IMPLEMENTED / DECIDED / DEFERRED / UNKNOWN tiers; SUPERSEDED + OBSOLETE hidden by the dashboard are excluded). Surfaces both engine-consumption gaps AND classification anomalies (DECIDED/DEFERRED items that ARE engine-consumed - either misclassified or accidentally pre-wired).

Columns:
- `engine`: did the function containing the source tag execute during the canonical AAPL backtest under coverage? YES = engine-consumed (function body had at least one executed line); LAZY-WIRED = file at 0% coverage but imported by a module that ran (import chain exists, conditional path not exercised by this small backtest  -  treat as wired until a larger backtest disproves); FUNC-DEAD = function exists in active module but body never executed; NO = tagged file at 0% with no live importer anywhere (real wiring gap); N/A = no source tag found (methodology/scope decision, no code expected).
- 13 pyramid tier columns: YES if any test file in that tier references the ID.

**Canonical runs (Batch 459 / AU3 dual-source coverage).** Run each of these before regenerating the matrix; the loader unions executed lines across every `coverage_report*.json` it finds in the repo root:

  1. `python -m coverage run --rcfile=.coveragerc-backtest backtest/run_phase1a.py --no-agents --no-git --tickers AAPL --start 2023-01-01 --end 2023-06-30 && python -m coverage json -o coverage_report.json`
  2. `python -m coverage run --rcfile=.coveragerc-optimizer scripts/optimize_strategies_from_cube.py --input-dir output_batch395_final --output-dir /tmp/optimizer_test && python -m coverage json -o coverage_report_optimizer.json` (extends matrix coverage to the cube-cell verdict pathway)

Add more coverage runs by writing additional `coverage_report_<tag>.json` files; the loader merges them automatically.


## Summary

- Total items audited: **736** (scope-expanded 2026-05-14 per owner directive  -  now covers ALL visible DECs + BUGs, not just IMPLEMENTED tier)

**By promotion tier:**
- IMPLEMENTED: 357
- DECIDED: 206
- DEFERRED: 152
- FUNC-DEAD: 19
- UNKNOWN: 2

**By coverage-driven engine status:**
- Engine YES (executed): **165**
- Engine LAZY-WIRED (all tagged files wired via lazy import chains): **6** (import chain exists; condition gating the call not met in this small backtest)
- Engine PARTIAL-ORPHAN (some tags wired, primary helper file orphaned): **105** (DEC is mentioned in a wired file but the actual helper module has no live importer  -  real gap)
- Engine FUNC-DEAD (function exists but never executed): **25**
- Engine NO (all tagged files orphaned): **27** (real wiring gap  -  helper file imported nowhere in the engine path)
- Engine DECLARED-ONLY (module-level tag in config; symbol not consumed externally): **17** (constant declared but no other executing file uses it  -  deferred-feature config that hasn't been wired yet)
- Engine N/A (no code expected): **391**

### Classification anomalies (tier vs engine mismatch): **33**

| ID | Tier | Engine | Note |
|---|---|---|---|
| `DEC-028` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-034` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-078B` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-118` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-122` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-261` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-262` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-267` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-318` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-319` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-433` | DEFERRED | YES | DEFERRED but helper executes in current-phase backtest - intentional pre-wire or misclassification? |
| `DEC-440` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-462` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-499` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-500` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-502` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-609` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-599` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-595` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-591` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-592` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-007` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-008` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-021` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-073` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-078` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-083` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-186` | DECIDED | YES | DECIDED claims no-code-expected but coverage shows engine consumption - reclassify to IMPLEMENTED? |
| `BUG-284` | IMPLEMENTED | NO | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-290` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-214` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-225` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-241` | DECIDED | YES | DECIDED claims no-code-expected but coverage shows engine consumption - reclassify to IMPLEMENTED? |

### Pyramid coverage gaps (count of engine-consumed items missing per tier)

- `unit`: **10** items lack a reference in this tier's test files
- `smoke`: **170** items lack a reference in this tier's test files
- `integration`: **6** items lack a reference in this tier's test files
- `system`: **171** items lack a reference in this tier's test files
- `functional`: **170** items lack a reference in this tier's test files
- `regression`: **169** items lack a reference in this tier's test files
- `data_integrity`: **171** items lack a reference in this tier's test files
- `performance`: **171** items lack a reference in this tier's test files
- `acceptance`: **171** items lack a reference in this tier's test files
- `property`: **171** items lack a reference in this tier's test files
- `snapshot`: **171** items lack a reference in this tier's test files
- `contract`: **171** items lack a reference in this tier's test files
- `compatibility`: **171** items lack a reference in this tier's test files

### Engine-consumption gaps detail

| ID | engine | evidence | unit | integration |
|---|---|---|---|---|
| `DEC-001` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-006` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-013` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-018` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_trader_toolkit.py has no live importer; another tagged file is wired (mentio... | YES | YES |
| `DEC-019` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-021` | PARTIAL-ORPHAN | primary helper backtest/live_trading/risk_overlay.py has no live importer; another tagged file is wired (mention-only, n... | YES | YES |
| `DEC-028` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | no |
| `DEC-034` | NO | every tagged file is orphaned (e.g. backtest/live_trading/risk_overlay.py) | no | no |
| `DEC-045` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | no | YES |
| `DEC-057` | PARTIAL-ORPHAN | primary helper backtest/agents/agent_gate_config.py has no live importer; another tagged file is wired (mention-only, no... | YES | YES |
| `DEC-062` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-067` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-076` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-078A` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-078B` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | no |
| `DEC-082` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-091` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-106` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_risk_toolkit.py has no live importer; another tagged file is wired (mention-... | YES | YES |
| `DEC-111` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-118` | NO | every tagged file is orphaned (e.g. backtest/agents/toolkits/our_technical_toolkit.py) | no | no |
| `DEC-122` | NO | every tagged file is orphaned (e.g. backtest/live_trading/ib_executor.py) | no | no |
| `DEC-123` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-124` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/state_augmentation.py has no live importer; another tagged file is wired (mentio... | YES | YES |
| `DEC-131` | PARTIAL-ORPHAN | primary helper backtest/agents/agent_gate_config.py has no live importer; another tagged file is wired (mention-only, no... | YES | YES |
| `DEC-142` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-144` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-153` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-175` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-179` | PARTIAL-ORPHAN | primary helper scripts/monitor_phase_1a_beta_health.py has no live importer; another tagged file is wired (mention-only,... | YES | YES |
| `DEC-189` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_risk_toolkit.py has no live importer; another tagged file is wired (mention-... | YES | YES |
| `DEC-206` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-207` | PARTIAL-ORPHAN | primary helper backtest/results/ab_orchestrator.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `DEC-209` | PARTIAL-ORPHAN | primary helper backtest/results/cube_populator.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-210` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-215` | PARTIAL-ORPHAN | primary helper backtest/results/ab_orchestrator.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `DEC-231` | PARTIAL-ORPHAN | primary helper backtest/live_trading/risk_overlay.py has no live importer; another tagged file is wired (mention-only, n... | YES | no |
| `DEC-246` | PARTIAL-ORPHAN | primary helper backtest/results/ab_orchestrator.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `DEC-247` | PARTIAL-ORPHAN | primary helper backtest/results/cube_populator.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-249` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-250` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-256` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-257` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-261` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | no |
| `DEC-262` | NO | every tagged file is orphaned (e.g. backtest/agents/toolkits/our_risk_toolkit.py) | no | no |
| `DEC-267` | NO | every tagged file is orphaned (e.g. backtest/paper_trading/paper_portfolio.py) | no | no |
| `DEC-280` | PARTIAL-ORPHAN | primary helper scripts/run_live_end_of_day.py has no live importer; another tagged file is wired (mention-only, not actu... | YES | YES |
| `DEC-284` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-295` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-298` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-302` | PARTIAL-ORPHAN | primary helper scripts/prefetch_polygon_corp_actions.py has no live importer; another tagged file is wired (mention-only... | YES | YES |
| `DEC-304` | PARTIAL-ORPHAN | primary helper scripts/refresh_economic_calendar.py has no live importer; another tagged file is wired (mention-only, no... | YES | YES |
| `DEC-317` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_risk_toolkit.py has no live importer; another tagged file is wired (mention-... | YES | YES |
| `DEC-318` | NO | every tagged file is orphaned (e.g. scripts/refresh_aaii_sentiment.py) | no | no |
| `DEC-319` | NO | every tagged file is orphaned (e.g. scripts/refresh_aaii_sentiment.py) | YES | YES |
| `DEC-321` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-325` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_fundamentals_toolkit.py has no live importer; another tagged file is wired (... | YES | YES |
| `DEC-334` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-348` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_risk_toolkit.py has no live importer; another tagged file is wired (mention-... | YES | YES |
| `DEC-349` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_risk_toolkit.py has no live importer; another tagged file is wired (mention-... | YES | YES |
| `DEC-353` | PARTIAL-ORPHAN | primary helper backtest/live_trading/ib_executor.py has no live importer; another tagged file is wired (mention-only, no... | YES | YES |
| `DEC-355` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_technical_toolkit.py has no live importer; another tagged file is wired (men... | YES | YES |
| `DEC-364` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-366` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_technical_toolkit.py has no live importer; another tagged file is wired (men... | YES | YES |
| `DEC-390` | PARTIAL-ORPHAN | primary helper scripts/refresh_aaii_sentiment.py has no live importer; another tagged file is wired (mention-only, not a... | YES | YES |
| `DEC-400` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-401` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-405` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-407` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-411` | FUNC-DEAD | function in backtest/signals/screener.py never executed | no | no |
| `DEC-415` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-420` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-422` | PARTIAL-ORPHAN | primary helper backtest/results/cube_populator.py has no live importer; another tagged file is wired (mention-only, not ... | no | YES |
| `DEC-423` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-425` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | no | YES |
| `DEC-426` | PARTIAL-ORPHAN | primary helper backtest/results/cube_metrics_tier_b.py has no live importer; another tagged file is wired (mention-only,... | YES | YES |
| `DEC-440` | FUNC-DEAD | function in backtest/signals/screener.py never executed | YES | YES |
| `DEC-441` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-450` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-453` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | no | YES |
| `DEC-456` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-459` | NO | every tagged file is orphaned (e.g. backtest/agents/agent_gate_config.py) | no | no |
| `DEC-461` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-462` | NO | every tagged file is orphaned (e.g. backtest/agents/agent_gate_config.py) | no | YES |
| `DEC-477` | PARTIAL-ORPHAN | primary helper scripts/build_index_rebalance_events.py has no live importer; another tagged file is wired (mention-only,... | YES | YES |
| `DEC-483` | PARTIAL-ORPHAN | primary helper scripts/refresh_extended_universe.py has no live importer; another tagged file is wired (mention-only, no... | YES | YES |
| `DEC-484` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-491` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-492` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-493` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-496` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-494` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-497` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-499` | FUNC-DEAD | function in backtest/data/universe.py never executed | YES | YES |
| `DEC-500` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | no |
| `DEC-501` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | no | YES |
| `DEC-502` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | YES | YES |
| `DEC-503` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-508` | PARTIAL-ORPHAN | primary helper scripts/phase_1b_canary_compute.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-507` | PARTIAL-ORPHAN | primary helper backtest/agents/langgraph_pipeline.py has no live importer; another tagged file is wired (mention-only, n... | YES | YES |
| `DEC-505` | PARTIAL-ORPHAN | primary helper backtest/util/holdout_guard.py has no live importer; another tagged file is wired (mention-only, not actu... | YES | YES |
| `DEC-609` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | no |
| `DEC-606` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_sprint0a.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `DEC-605` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_sprint0a.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `DEC-599` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_sprint0a.py) | no | no |
| `DEC-601` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_sprint0a.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `DEC-594` | PARTIAL-ORPHAN | primary helper scripts/audit_decs_for_artifacts.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `DEC-595` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | no |
| `DEC-591` | NO | every tagged file is orphaned (e.g. scripts/audit_decs_for_artifacts.py) | no | no |
| `DEC-592` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | no |
| `DEC-590` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `DEC-504` | PARTIAL-ORPHAN | primary helper scripts/generate_stage_d_tickers.py has no live importer; another tagged file is wired (mention-only, not... | YES | YES |
| `BUG-001` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-002` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-004` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-005` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-006` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-007` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | YES |
| `BUG-008` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | YES | YES |
| `BUG-009` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-010` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-011` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-012` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-015` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-018` | FUNC-DEAD | function in backtest/engine/backtest.py never executed | YES | YES |
| `BUG-021` | FUNC-DEAD | function in backtest/engine/exit_strategies.py never executed | YES | YES |
| `BUG-022` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-027` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `BUG-028` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-029` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-030` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-036` | NO | every tagged file is orphaned (e.g. scripts/revert_batch_69_phase_1.py) | no | YES |
| `BUG-037` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-045` | NO | every tagged file is orphaned (e.g. scripts/build_verification_matrix.py) | no | YES |
| `BUG-060` | FUNC-DEAD | function in backtest/signals/screener.py never executed | YES | YES |
| `BUG-061` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-073` | NO | every tagged file is orphaned (e.g. scripts/prepopulate_cache_index.py) | no | YES |
| `BUG-077` | FUNC-DEAD | function in backtest/signals/screener.py never executed | YES | YES |
| `BUG-078` | FUNC-DEAD | function in backtest/engine/exit_manager.py never executed | YES | YES |
| `BUG-080` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-083` | FUNC-DEAD | function in backtest/data/smart_money.py never executed | YES | YES |
| `BUG-095` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_risk_toolkit.py has no live importer; another tagged file is wired (mention-... | YES | YES |
| `BUG-110` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-111` | PARTIAL-ORPHAN | primary helper backtest/agents/toolkits/our_technical_toolkit.py has no live importer; another tagged file is wired (men... | YES | YES |
| `BUG-270` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-271` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-272` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-273` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-284` | NO | every tagged file is orphaned (e.g. backtest/agents/toolkits/our_fundamentals_toolkit.py) | no | YES |
| `BUG-286` | PARTIAL-ORPHAN | primary helper scripts/audit_trade_log_forensic.py has no live importer; another tagged file is wired (mention-only, not... | no | no |
| `BUG-290` | FUNC-DEAD | function in backtest/signals/screener.py never executed | no | no |
| `BUG-214` | FUNC-DEAD | function in backtest/engine/exit_manager.py never executed | YES | YES |
| `BUG-225` | FUNC-DEAD | function in backtest/engine/regime_filter.py never executed | YES | YES |
| `BUG-205` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-242` | PARTIAL-ORPHAN | primary helper scripts/build_dashboard_stage_2.py has no live importer; another tagged file is wired (mention-only, not ... | YES | YES |
| `BUG-116` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | YES |
| `BUG-135` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `BUG-138` | NO | every tagged file is orphaned (e.g. scripts/build_dashboard_stage_2.py) | no | YES |

| ID | engine | unit | smoke | integration | system | functional | regression | data_integrity | performance | acceptance | property | snapshot | contract | compatibility |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `DEC-001` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-002` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-003` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-004` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-005` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-006` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-007` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-008` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-009` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-010` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-011` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-012` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-013` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-015` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-018` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-019` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-021` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-027` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-028` | NO | no | no | no | YES | no | no | no | no | no | no | no | no | no |
| `DEC-029` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-029-A` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-029-B` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-029-C` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-031` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-033` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-034` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-035` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-036` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-037` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-038` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-039` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-040` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-041` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-043` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-045` | PARTIAL-ORPHAN | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-046` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-047` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-048` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-049` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-050` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-051` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-052` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-053` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-054` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-055` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-056` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-057` | PARTIAL-ORPHAN | YES | no | YES | no | YES | no | no | no | no | no | no | no | no |
| `DEC-058` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-059` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-060` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-061` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-062` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-067` | PARTIAL-ORPHAN | YES | no | YES | no | YES | no | no | no | no | no | no | no | no |
| `DEC-070` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-071` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-072` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-073` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-074` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-075` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-076` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-078` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-078A` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-078B` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-079` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-081` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-082` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-083` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-084` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-085` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-086` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-087` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-088` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-089` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-090` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-091` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-092` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-093` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-094` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-095` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-096` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-097` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-098` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-100` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-102` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-106` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-107` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-108` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-110` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-111` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-112` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-113` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-114` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-116` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-117` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-118` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-119` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-120` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-121` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-122` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-123` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-124` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-125` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-126` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-127` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-128` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-129` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-130` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-131` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-132` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-133` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-134` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-135` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-136` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-138` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-139` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-141` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-142` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-143` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-144` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-145` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-146` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-147` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-148` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-149` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-150` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-151` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-152` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-153` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-155` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-156` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-157` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-158` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-159` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-160` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-161` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-162` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-163` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-164` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-166` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-167` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-168` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-169` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-170` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-171` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-172` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-173` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-174` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-175` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-176` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-177` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-178` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-179` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-180` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-181` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-182` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-183` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-184` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-185` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-187` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-188` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-189` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-190` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-191` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-192` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-193` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-194` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-195` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-196` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-197` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-198` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-199` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-200` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-201` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-202` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-203` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-204` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-205` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-206` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-207` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-208` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-209` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-210` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-211` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-212` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-213` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-214` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-215` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-216` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-217` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-218` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-219` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-220` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-222` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-225` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-227` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-228` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-229` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-230` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-231` | PARTIAL-ORPHAN | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-232` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-233` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-234` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-235` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-236` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-237` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-238` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-239` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-240` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-241` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-242` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-243` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-244` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-245` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-246` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-247` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-248` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-249` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-250` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-251` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-252` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-253` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-254` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-255` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-256` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-257` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-258` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-259` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-260` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-261` | NO | no | no | no | no | no | YES | no | no | no | no | no | no | no |
| `DEC-262` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-263` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-265` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-266` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-267` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-268` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-269` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-270` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-271` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-272` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-273` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-274` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-275` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-276` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-277` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-278` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-279` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-280` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-281` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-282` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-283` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-284` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-285` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-286` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-287` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-289` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-290` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-291` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-292` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-293` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-294` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-295` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-296` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-297` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-298` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-301` | YES | YES | YES | YES | no | no | YES | no | no | no | no | no | no | no |
| `DEC-302` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-303` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-304` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-305` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-306` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-307` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-308` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-309` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-310` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-311` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-312` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-313` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-314` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-315` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-316` | YES | YES | no | YES | no | YES | YES | no | no | no | no | no | no | no |
| `DEC-317` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-318` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-319` | NO | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-320` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-321` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-323` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-324` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-325` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-328` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-329` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-330` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-331` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-332` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-333` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-334` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-335` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-338` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-339` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-340` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-341` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-343` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-344` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-345` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-347` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-348` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-349` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-350` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-352` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-353` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-354` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-355` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-356` | LAZY-WIRED | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-357` | LAZY-WIRED | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-358` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-359` | LAZY-WIRED | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-360` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-361` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-362` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-363` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-364` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-365` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-366` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-367` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-368` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-369` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-370` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-371` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-372` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-373` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-374` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-375` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-376` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-377` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-378` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-379` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-380` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-381` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-382` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-383` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-384` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-385` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-386` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-387` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-388` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-389` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-390` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-391` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-392` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-393` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-394` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-395` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-396` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-398` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-399` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-400` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-401` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-402` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-403` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-404` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-405` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-406` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-407` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-408` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-409` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-410` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-411` | FUNC-DEAD | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-413` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-414` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-415` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-416` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-417` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-418` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-419` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-420` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-421` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-422` | PARTIAL-ORPHAN | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-423` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-425` | PARTIAL-ORPHAN | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-426` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-427` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-428` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-429` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-430` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-431` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-432` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-433` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-434` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-435` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-436` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-437` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-438` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-439` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-440` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-441` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-442` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-443` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-444` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-445` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-446` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-447` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-448` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-449` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-450` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-451` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-453` | PARTIAL-ORPHAN | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-454` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-455` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-456` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-457` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-458` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-459` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-460` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-461` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-462` | NO | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-463` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-464` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-465` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-466` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-467` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-468` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-486` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-487` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-488` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-477` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-478` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-479` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-483` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-484` | PARTIAL-ORPHAN | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-485` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-490` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-489` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-469` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-470` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-471` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-472` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-473` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-474` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-475` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-476` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-480` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-481` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-491` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-492` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-493` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-496` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-495` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-494` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-497` | PARTIAL-ORPHAN | YES | YES | YES | YES | no | no | YES | no | no | no | no | no | no |
| `DEC-498` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-499` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-500` | NO | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-501` | PARTIAL-ORPHAN | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-502` | NO | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-503` | PARTIAL-ORPHAN | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| `DEC-508` | PARTIAL-ORPHAN | YES | no | YES | YES | no | YES | no | no | no | no | no | no | no |
| `DEC-507` | PARTIAL-ORPHAN | YES | no | YES | YES | no | YES | no | no | no | no | no | no | no |
| `DEC-506` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-505` | PARTIAL-ORPHAN | YES | YES | YES | YES | YES | no | no | no | no | no | YES | YES | no |
| `DEC-610` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-609` | NO | no | no | no | no | no | no | YES | no | no | no | no | no | no |
| `DEC-608` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-607` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-606` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-605` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-597` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-598` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-599` | NO | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-600` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-601` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-602` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-603` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-604` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-596` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-594` | PARTIAL-ORPHAN | YES | no | YES | YES | no | no | YES | no | YES | no | YES | YES | no |
| `DEC-595` | NO | no | YES | no | YES | no | no | no | no | no | no | no | no | no |
| `DEC-591` | NO | no | no | no | YES | no | no | YES | no | no | no | no | no | no |
| `DEC-592` | NO | no | no | no | no | no | no | YES | no | no | no | no | no | no |
| `DEC-593` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-589` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-590` | PARTIAL-ORPHAN | YES | no | YES | YES | no | no | no | no | no | no | no | no | no |
| `DEC-504` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | YES | no | YES | no | no | no | no |
| `BUG-001` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-002` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-003` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-004` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-005` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-006` | PARTIAL-ORPHAN | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-007` | NO | no | no | YES | no | no | YES | no | no | no | no | no | no | no |
| `BUG-008` | NO | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-009` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-010` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-011` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-012` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-013` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-014` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-015` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-016` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-017` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-018` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-019` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-020` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-021` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-022` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-023` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-024` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-026` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-027` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-028` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-029` | PARTIAL-ORPHAN | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-030` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-031` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-032` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-033` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-034` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-036` | NO | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-037` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-038` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-040` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-041` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-043` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-045` | NO | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-046` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-047` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-048` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-049` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-050` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-052` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-054` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-055` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-058` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-059` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-060` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-061` | PARTIAL-ORPHAN | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-063` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-064` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-065` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-066` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-068` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-069` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-070` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-071` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-073` | NO | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-074` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-075` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-077` | FUNC-DEAD | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-078` | FUNC-DEAD | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-079` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-080` | PARTIAL-ORPHAN | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-081` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-082` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-083` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-084` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-085` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-086` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-088` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-089` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-090` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-091` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-092` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-093` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-094` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-095` | PARTIAL-ORPHAN | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-096` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-097` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-098` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-099` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-100` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-101` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-102` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-103` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-104` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-106` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-107` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-110` | PARTIAL-ORPHAN | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-111` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-112` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-178` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-179` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-180` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-184` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-186` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-187` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-188` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-189` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-190` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-199` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-202` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-203` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-270` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-271` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-272` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-273` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-274` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-275` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-276` | LAZY-WIRED | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-279` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-281` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-282` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-283` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-284` | NO | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-286` | PARTIAL-ORPHAN | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-287` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-288` | LAZY-WIRED | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-289` | LAZY-WIRED | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-290` | FUNC-DEAD | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-214` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-215` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-216` | N/A | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-217` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-218` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-219` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-220` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-221` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-222` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-223` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-224` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-225` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-205` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-206` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-210` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-212` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-226` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-227` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-228` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-229` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-230` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-231` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-232` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-233` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-234` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-235` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-236` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-237` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-238` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-239` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-240` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-241` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-242` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-243` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-244` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-207` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-208` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-209` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-211` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-245` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-246` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-247` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-248` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-249` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-251` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-253` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-254` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-255` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-256` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-257` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-258` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-260` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-261` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-262` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-263` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-204` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-264` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-266` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-267` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-268` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-269` | N/A | no | no | YES | no | no | YES | no | no | no | no | no | no | no |
| `BUG-285` | DECLARED-ONLY | YES | no | YES | no | YES | no | no | no | no | no | no | no | no |
| `BUG-114` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-115` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-116` | NO | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-117` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-118` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-119` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-120` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-121` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-122` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-123` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-124` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-125` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-126` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-127` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-128` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-129` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-132` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-133` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-134` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-135` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-136` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-137` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-138` | NO | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-139` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-140` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-141` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-142` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-143` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-144` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-145` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-146` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-147` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-148` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-149` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-150` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-151` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-152` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-153` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-154` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-155` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-156` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-157` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-158` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-159` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-160` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-161` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-162` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-163` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-164` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-165` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-166` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-167` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-168` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-169` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-170` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-171` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-172` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-173` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-174` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-175` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-176` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-177` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-192` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-193` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-194` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-195` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-196` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-197` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-198` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
