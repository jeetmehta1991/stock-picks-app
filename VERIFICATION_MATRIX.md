# VERIFICATION_MATRIX.md

**Generated:** see `scripts/build_verification_matrix.py`. Per-item ground truth for ALL visible DECs + BUGs in scope (IMPLEMENTED / DECIDED / DEFERRED / UNKNOWN tiers; SUPERSEDED + OBSOLETE hidden by the dashboard are excluded). Surfaces both engine-consumption gaps AND classification anomalies (DECIDED/DEFERRED items that ARE engine-consumed - either misclassified or accidentally pre-wired).

Columns:
- `engine`: did the function containing the source tag execute during the canonical AAPL backtest under coverage? YES = engine-consumed (function body had at least one executed line); LAZY-WIRED = file at 0% coverage but imported by a module that ran (import chain exists, conditional path not exercised by this small backtest  -  treat as wired until a larger backtest disproves); FUNC-DEAD = function exists in active module but body never executed; NO = tagged file at 0% with no live importer anywhere (real wiring gap); N/A = no source tag found (methodology/scope decision, no code expected).
- 13 pyramid tier columns: YES if any test file in that tier references the ID.

Canonical backtest: `python -m coverage run backtest/run_phase1a.py --no-agents --no-git --tickers AAPL --start 2023-01-01 --end 2023-06-30`


## Summary

- Total items audited: **746** (scope-expanded 2026-05-14 per owner directive  -  now covers ALL visible DECs + BUGs, not just IMPLEMENTED tier)

**By promotion tier:**
- IMPLEMENTED: 357
- DECIDED: 213
- DEFERRED: 174
- UNKNOWN: 2

**By coverage-driven engine status:**
- Engine YES (executed): **156**
- Engine LAZY-WIRED (all tagged files wired via lazy import chains): **3** (import chain exists; condition gating the call not met in this small backtest)
- Engine PARTIAL-ORPHAN (some tags wired, primary helper file orphaned): **0** (DEC is mentioned in a wired file but the actual helper module has no live importer  -  real gap)
- Engine FUNC-DEAD (function exists but never executed): **60**
- Engine NO (all tagged files orphaned): **0** (real wiring gap  -  helper file imported nowhere in the engine path)
- Engine DECLARED-ONLY (module-level tag in config; symbol not consumed externally): **109** (constant declared but no other executing file uses it  -  deferred-feature config that hasn't been wired yet)
- Engine N/A (no code expected): **418**

### Classification anomalies (tier vs engine mismatch): **56**

| ID | Tier | Engine | Note |
|---|---|---|---|
| `DEC-015` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-019` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-078A` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-089` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-092` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-095` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-100` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-119` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-120` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-123` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-131` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-134` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-141` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-142` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-144` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-145` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-148` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-159` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-175` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-201` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-206` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-209` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-210` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-211` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-212` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-214` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-225` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-227` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-232` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-233` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-241` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-246` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-249` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-255` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-258` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-260` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-279` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-280` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-284` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-287` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-321` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-330` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-333` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-334` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-352` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-366` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-392` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-396` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-400` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-420` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-461` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-606` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `DEC-590` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-083` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-271` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |
| `BUG-228` | IMPLEMENTED | FUNC-DEAD | IMPLEMENTED but engine never reaches the tagged code - wiring gap |

### Pyramid coverage gaps (count of engine-consumed items missing per tier)

- `unit`: **0** items lack a reference in this tier's test files
- `smoke`: **147** items lack a reference in this tier's test files
- `integration`: **0** items lack a reference in this tier's test files
- `system`: **154** items lack a reference in this tier's test files
- `functional`: **154** items lack a reference in this tier's test files
- `regression`: **155** items lack a reference in this tier's test files
- `data_integrity`: **155** items lack a reference in this tier's test files
- `performance`: **158** items lack a reference in this tier's test files
- `acceptance`: **153** items lack a reference in this tier's test files
- `property`: **158** items lack a reference in this tier's test files
- `snapshot`: **156** items lack a reference in this tier's test files
- `contract`: **147** items lack a reference in this tier's test files
- `compatibility`: **158** items lack a reference in this tier's test files

### Engine-consumption gaps detail

| ID | engine | evidence | unit | integration |
|---|---|---|---|---|
| `DEC-015` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-019` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-078A` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-089` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-092` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-095` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-100` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-119` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-120` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-123` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-131` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-134` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-141` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-142` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-144` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-145` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-148` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-159` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-175` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-201` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-206` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-209` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-210` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-211` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-212` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-214` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-225` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-227` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-232` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-233` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-241` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-246` | FUNC-DEAD | function in backtest/results/quant_audit.py never executed | YES | YES |
| `DEC-249` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-255` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-258` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-260` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-279` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-280` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-284` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-287` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-321` | FUNC-DEAD | function in backtest/data/universe.py never executed | YES | YES |
| `DEC-330` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-333` | FUNC-DEAD | function in backtest/data/sentiment.py never executed | YES | YES |
| `DEC-334` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-352` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-366` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-392` | FUNC-DEAD | function in backtest/data/universe.py never executed | YES | YES |
| `DEC-396` | FUNC-DEAD | function in backtest/data/smart_money.py never executed | YES | YES |
| `DEC-400` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-420` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |
| `DEC-461` | FUNC-DEAD | function in backtest/data/smart_money.py never executed | YES | YES |
| `DEC-606` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `DEC-590` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `BUG-027` | FUNC-DEAD | function in backtest/engine/improvements.py never executed | YES | YES |
| `BUG-083` | FUNC-DEAD | function in backtest/data/smart_money.py never executed | YES | YES |
| `BUG-186` | FUNC-DEAD | function in backtest/data/smart_money.py never executed | YES | YES |
| `BUG-271` | FUNC-DEAD | function in backtest/data/smart_money.py never executed | YES | YES |
| `BUG-228` | FUNC-DEAD | function in backtest/data/cache.py never executed | YES | YES |
| `BUG-241` | FUNC-DEAD | function in backtest/data/smart_money.py never executed | YES | YES |
| `BUG-135` | FUNC-DEAD | function in backtest/results/metrics.py never executed | YES | YES |

| ID | engine | unit | smoke | integration | system | functional | regression | data_integrity | performance | acceptance | property | snapshot | contract | compatibility |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `DEC-001` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-002` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-003` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-004` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-005` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-006` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-007` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-008` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-009` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-010` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-011` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-012` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-013` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-015` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-018` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-019` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-021` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-027` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-028` | N/A | no | no | no | YES | no | no | no | no | no | no | no | no | no |
| `DEC-029` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-029-A` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-029-B` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-029-C` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-031` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-033` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-034` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-035` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-036` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-037` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-038` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-039` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-040` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-041` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-043` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-045` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
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
| `DEC-057` | YES | YES | no | YES | no | YES | no | no | no | no | no | no | no | no |
| `DEC-058` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-059` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-060` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-061` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-062` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-067` | YES | YES | no | YES | no | YES | no | no | no | no | no | no | no | no |
| `DEC-070` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-071` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-072` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-073` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-074` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-075` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-076` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-078` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-078A` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-078B` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-079` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-081` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-082` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-083` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-084` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-085` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-086` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-087` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-088` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-089` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-090` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-091` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-092` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-093` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-094` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-095` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-096` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-097` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-098` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-100` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-102` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-106` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-107` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-108` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-110` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-111` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-112` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-113` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-114` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-116` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-117` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-118` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-119` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-120` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-121` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-122` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-123` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-124` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-125` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-126` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-127` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-128` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-129` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-130` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-131` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-132` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-133` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-134` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-135` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-136` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-138` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-139` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-141` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-142` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-143` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-144` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-145` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-146` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-147` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-148` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-149` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-150` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-151` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-152` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-153` | YES | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-155` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-156` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-157` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-158` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-159` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-160` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-161` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-162` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-163` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-164` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-166` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-167` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-168` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-169` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-170` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-171` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-172` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-173` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-174` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-175` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-176` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-177` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-178` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-179` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-180` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-181` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-182` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-183` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-184` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-185` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-187` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-188` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-189` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
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
| `DEC-201` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-202` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-203` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-204` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-205` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-206` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-207` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-208` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-209` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-210` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-211` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-212` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-213` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-214` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-215` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-216` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-217` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-218` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-219` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-220` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-222` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-225` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-227` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-228` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-229` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-230` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-231` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-232` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-233` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-234` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-235` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-236` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-237` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-238` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-239` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-240` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-241` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-242` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-243` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-244` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-245` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-246` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-247` | YES | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-248` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-249` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-250` | YES | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-251` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-252` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-253` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-254` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-255` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-256` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-257` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-258` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-259` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-260` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-261` | N/A | no | no | no | no | no | YES | no | no | no | no | no | no | no |
| `DEC-262` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-263` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-265` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-266` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-267` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-268` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-269` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-270` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-271` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-272` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-273` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-274` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-275` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-276` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-277` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-278` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-279` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-280` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-281` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-282` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-283` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-284` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-285` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-286` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-287` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-289` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-290` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-291` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-292` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-293` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-294` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-295` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-296` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-297` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-298` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-301` | YES | YES | YES | YES | no | no | YES | no | no | no | no | no | no | no |
| `DEC-302` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-303` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-304` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
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
| `DEC-317` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-318` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-319` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-320` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-321` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-323` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-324` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-325` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-328` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-329` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-330` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-331` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-332` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-333` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-334` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-335` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-338` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-339` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-340` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-341` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-343` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-344` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-345` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-347` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-348` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-349` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-350` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-352` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-353` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-354` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-355` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-356` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-357` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-358` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-359` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-360` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-361` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-362` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-363` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-364` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-365` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-366` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-367` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-368` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-369` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-370` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-371` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-372` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-373` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-374` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-375` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-376` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-377` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-378` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-379` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-380` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-381` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-382` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-383` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-384` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-385` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-386` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-387` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-388` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-389` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-390` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-391` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-392` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-393` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-394` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-395` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-396` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-398` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-399` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-400` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-401` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-402` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-403` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-404` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-405` | YES | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-406` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-407` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-408` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-409` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-410` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-411` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-413` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-414` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-415` | YES | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-416` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-417` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-418` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-419` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-420` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-421` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-422` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-423` | YES | YES | no | YES | no | no | no | no | no | no | no | no | YES | no |
| `DEC-425` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-426` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-427` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-428` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-429` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-430` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-431` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-432` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-433` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-434` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-435` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-436` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-437` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-438` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-439` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-440` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-441` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-442` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-443` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-444` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-445` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-446` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-447` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-448` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-449` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-450` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-451` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-453` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-454` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-455` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-456` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-457` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-458` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-459` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-460` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-461` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-462` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-463` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-464` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-465` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-466` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-467` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-468` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-486` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-487` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-488` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-477` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-478` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-479` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-483` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-484` | DECLARED-ONLY | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-485` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-490` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-489` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
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
| `DEC-491` | YES | YES | no | YES | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-492` | YES | YES | no | YES | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-493` | YES | YES | no | YES | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-496` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-495` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-494` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-497` | YES | YES | YES | YES | YES | no | no | YES | no | no | no | no | no | no |
| `DEC-498` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-499` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-500` | N/A | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-501` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-502` | DECLARED-ONLY | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-503` | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| `DEC-508` | N/A | YES | no | YES | YES | no | YES | no | no | no | no | no | no | no |
| `DEC-507` | YES | YES | no | YES | YES | no | YES | no | no | no | no | no | no | no |
| `DEC-506` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-505` | YES | YES | YES | YES | YES | YES | no | no | no | no | no | YES | YES | no |
| `DEC-610` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-609` | N/A | no | no | no | no | no | no | YES | no | no | no | no | no | no |
| `DEC-608` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-607` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-606` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-605` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-597` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-598` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-599` | N/A | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-600` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-601` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-602` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-603` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-604` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-596` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-594` | YES | YES | no | YES | YES | no | no | YES | no | YES | no | YES | YES | no |
| `DEC-595` | N/A | no | YES | no | YES | no | no | no | no | no | no | no | no | no |
| `DEC-591` | N/A | no | no | no | YES | no | no | YES | no | no | no | no | no | no |
| `DEC-592` | N/A | no | no | no | no | no | no | YES | no | no | no | no | no | no |
| `DEC-593` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-589` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-590` | FUNC-DEAD | YES | no | YES | YES | no | no | no | no | no | no | no | no | no |
| `DEC-504` | YES | YES | no | YES | no | no | no | YES | no | YES | no | no | no | no |
| `BUG-001` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-002` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-003` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-004` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-005` | LAZY-WIRED | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-006` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-007` | N/A | no | no | YES | no | no | YES | no | no | no | no | no | no | no |
| `BUG-008` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-009` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-010` | LAZY-WIRED | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-011` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-012` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-013` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-014` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-015` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-016` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-017` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-018` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-019` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-020` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-021` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-022` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-023` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-024` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-026` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-027` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-028` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-029` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-030` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-031` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-032` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-033` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-034` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-035` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-036` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-037` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-038` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-039` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-040` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-041` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-043` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-045` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-046` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-047` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-048` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-049` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-050` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-051` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-052` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-054` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-055` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-056` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-057` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-058` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-059` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-060` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-061` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-063` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-064` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-065` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-066` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-068` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-069` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-070` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-071` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-073` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-074` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-075` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-076` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-077` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-078` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-079` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-080` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-081` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-082` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-083` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-084` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-085` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-086` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-087` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-088` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-089` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-090` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-091` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-092` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-093` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-094` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-095` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-096` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-097` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-098` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-099` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-100` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-101` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-102` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-103` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-104` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-105` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-106` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-107` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-108` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-109` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-110` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-111` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-112` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-113` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-113` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-178` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-179` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-180` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-182` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-184` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-186` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-187` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-188` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-189` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-190` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-191` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-199` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-200` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-202` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-203` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-270` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-271` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-272` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-273` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-274` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-275` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-276` | LAZY-WIRED | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-279` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-281` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-282` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-283` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-284` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-214` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-215` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-216` | N/A | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-217` | DECLARED-ONLY | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-218` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-219` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-220` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-221` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-222` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-223` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-224` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-225` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-205` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-206` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-210` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-212` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-226` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-227` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-228` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
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
| `BUG-241` | FUNC-DEAD | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-242` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
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
| `BUG-116` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
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
| `BUG-138` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
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
