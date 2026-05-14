# VERIFICATION_MATRIX.md

**Generated:** see `scripts/build_verification_matrix.py`. Per-item ground truth for the 343 IMPLEMENTED claims (DEC + BUG).

Columns:
- `engine`: did the function containing the source tag execute during the canonical AAPL backtest under coverage? YES = engine-consumed (function body had at least one executed line); LAZY-WIRED = file at 0% coverage but imported by a module that ran (import chain exists, conditional path not exercised by this small backtest — treat as wired until a larger backtest disproves); FUNC-DEAD = function exists in active module but body never executed; NO = tagged file at 0% with no live importer anywhere (real wiring gap); N/A = no source tag found (methodology/scope decision, no code expected).
- 13 pyramid tier columns: YES if any test file in that tier references the ID.

Canonical backtest: `python -m coverage run backtest/run_phase1a.py --no-agents --no-git --tickers AAPL --start 2023-01-01 --end 2023-06-30`


## Summary

- Total items audited: **357**
- Engine YES (executed): **290**
- Engine LAZY-WIRED (all tagged files wired via lazy import chains): **5** (import chain exists; condition gating the call not met in this small backtest)
- Engine PARTIAL-ORPHAN (some tags wired, primary helper file orphaned): **8** (DEC is mentioned in a wired file but the actual helper module has no live importer — real gap)
- Engine FUNC-DEAD (function exists but never executed): **1**
- Engine NO (all tagged files orphaned): **2** (real wiring gap — helper file imported nowhere in the engine path)
- Engine N/A (no code expected): **51**

### Pyramid coverage gaps (count of engine-consumed items missing per tier)

- `unit`: **56** items lack a reference in this tier's test files
- `smoke`: **282** items lack a reference in this tier's test files
- `integration`: **202** items lack a reference in this tier's test files
- `system`: **291** items lack a reference in this tier's test files
- `functional`: **290** items lack a reference in this tier's test files
- `regression`: **291** items lack a reference in this tier's test files
- `data_integrity`: **292** items lack a reference in this tier's test files
- `performance`: **294** items lack a reference in this tier's test files
- `acceptance`: **290** items lack a reference in this tier's test files
- `property`: **294** items lack a reference in this tier's test files
- `snapshot`: **294** items lack a reference in this tier's test files
- `contract`: **288** items lack a reference in this tier's test files
- `compatibility`: **294** items lack a reference in this tier's test files

### Engine-consumption gaps detail

| ID | engine | evidence | unit | integration |
|---|---|---|---|---|
| `DEC-082` | NO | every tagged file is orphaned (e.g. backtest/results/stress_tests.py) | no | no |
| `DEC-111` | PARTIAL-ORPHAN | primary helper backtest/results/rolling_sharpe_test.py has no live importer; another tagged file is wired (mention-only,... | no | no |
| `DEC-153` | NO | every tagged file is orphaned (e.g. backtest/engine/regime_stratified_split.py) | no | no |
| `DEC-250` | PARTIAL-ORPHAN | primary helper backtest/results/edge_decay.py has no live importer; another tagged file is wired (mention-only, not actu... | no | no |
| `DEC-405` | PARTIAL-ORPHAN | primary helper backtest/results/stress_tests.py has no live importer; another tagged file is wired (mention-only, not ac... | no | no |
| `DEC-415` | PARTIAL-ORPHAN | primary helper backtest/results/rolling_sharpe_test.py has no live importer; another tagged file is wired (mention-only,... | no | no |
| `DEC-422` | PARTIAL-ORPHAN | primary helper backtest/engine/regime_stratified_split.py has no live importer; another tagged file is wired (mention-on... | YES | YES |
| `DEC-423` | PARTIAL-ORPHAN | primary helper backtest/results/bootstrap_ci.py has no live importer; another tagged file is wired (mention-only, not ac... | no | no |
| `DEC-505` | PARTIAL-ORPHAN | primary helper backtest/engine/regime_stratified_split.py has no live importer; another tagged file is wired (mention-on... | YES | YES |
| `DEC-594` | PARTIAL-ORPHAN | primary helper backtest/engine/regime_stratified_split.py has no live importer; another tagged file is wired (mention-on... | no | YES |
| `BUG-075` | FUNC-DEAD | function in backtest/results/metrics.py never executed | no | YES |

| ID | engine | unit | smoke | integration | system | functional | regression | data_integrity | performance | acceptance | property | snapshot | contract | compatibility |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `DEC-001` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-006` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-013` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-015` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-018` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-019` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-021` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-028` | N/A | no | no | no | YES | no | no | no | no | no | no | no | no | no |
| `DEC-033` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-037` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-038` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-040` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-045` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-052` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-054` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-057` | YES | no | no | no | no | YES | no | no | no | no | no | no | no | no |
| `DEC-061` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-067` | YES | no | no | no | no | YES | no | no | no | no | no | no | no | no |
| `DEC-070` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-071` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-072` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-075` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-076` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-078` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-078A` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-081` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-082` | NO | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-083` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-084` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-085` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-087` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-088` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-089` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-091` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-092` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-095` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-098` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-100` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-102` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-106` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-107` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-108` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-110` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-111` | PARTIAL-ORPHAN | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-116` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-117` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-119` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-120` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-123` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-124` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-125` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-126` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-128` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-131` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-134` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-135` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-136` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-141` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-142` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-144` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-145` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-148` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-149` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-150` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-151` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-152` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-153` | NO | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-155` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-159` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-169` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-170` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-171` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-174` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-175` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-177` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-178` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-179` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-183` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-184` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-189` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-201` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-205` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-206` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-207` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-208` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-209` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-210` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-211` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-212` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-213` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-214` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-215` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-220` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-225` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-227` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-232` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-233` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-235` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-241` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-246` | LAZY-WIRED | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-247` | LAZY-WIRED | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-249` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-250` | PARTIAL-ORPHAN | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-251` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-253` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-254` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-255` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-256` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-257` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-258` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-259` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-260` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-261` | N/A | no | no | no | no | no | YES | no | no | no | no | no | no | no |
| `DEC-263` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-265` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-269` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-274` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-275` | N/A | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-277` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-279` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-280` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-284` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-287` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-290` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-295` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-298` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-301` | YES | YES | YES | no | no | no | YES | no | no | no | no | no | no | no |
| `DEC-302` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-303` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-304` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-305` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-307` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-308` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-309` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-311` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-312` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-314` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-315` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-316` | YES | YES | no | no | no | YES | YES | no | no | no | no | no | no | no |
| `DEC-317` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-318` | N/A | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-319` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-320` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-321` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-323` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-324` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-325` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-329` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-330` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-332` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-333` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-334` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-335` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-338` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-341` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-345` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-347` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-348` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-349` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-350` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-352` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-353` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-354` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-355` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-358` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-359` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-360` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-361` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-362` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-363` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-364` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-366` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-368` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-369` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-370` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-372` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-376` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-380` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-381` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-382` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-388` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-389` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-390` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-391` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-392` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-394` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-396` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-400` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-401` | LAZY-WIRED | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-402` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-403` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-404` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-405` | PARTIAL-ORPHAN | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-406` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-407` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-408` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-409` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-413` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-414` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-415` | PARTIAL-ORPHAN | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-416` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-420` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-422` | PARTIAL-ORPHAN | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-423` | PARTIAL-ORPHAN | no | no | no | no | no | no | no | no | no | no | no | YES | no |
| `DEC-431` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-432` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-435` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-437` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-438` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-439` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-440` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-441` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-446` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-450` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-453` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-456` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-458` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-460` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-461` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-462` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-464` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-465` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-466` | YES | no | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-468` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-477` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-478` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-479` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-483` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-484` | YES | YES | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-485` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-490` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-489` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-491` | YES | no | no | no | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-492` | YES | no | no | no | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-493` | YES | no | no | no | no | no | no | no | no | YES | no | no | YES | no |
| `DEC-496` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-494` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-497` | YES | no | YES | YES | YES | no | no | YES | no | no | no | no | no | no |
| `DEC-499` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-500` | N/A | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-501` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-502` | YES | YES | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-503` | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| `DEC-508` | N/A | YES | no | YES | YES | no | YES | no | no | no | no | no | no | no |
| `DEC-507` | YES | YES | no | YES | YES | no | YES | no | no | no | no | no | no | no |
| `DEC-506` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-505` | PARTIAL-ORPHAN | YES | YES | YES | YES | YES | no | no | no | no | no | YES | YES | no |
| `DEC-609` | N/A | no | no | no | no | no | no | YES | no | no | no | no | no | no |
| `DEC-608` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `DEC-606` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-605` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-599` | N/A | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-601` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-594` | PARTIAL-ORPHAN | no | no | YES | YES | no | no | YES | no | YES | no | YES | YES | no |
| `DEC-595` | N/A | no | YES | no | YES | no | no | no | no | no | no | no | no | no |
| `DEC-591` | N/A | no | no | no | YES | no | no | YES | no | no | no | no | no | no |
| `DEC-592` | N/A | no | no | no | no | no | no | YES | no | no | no | no | no | no |
| `DEC-593` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `DEC-590` | YES | no | no | no | YES | no | no | no | no | no | no | no | no | no |
| `DEC-504` | YES | YES | no | YES | no | no | no | YES | no | YES | no | no | no | no |
| `BUG-001` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-002` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-003` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-004` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-005` | LAZY-WIRED | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-006` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-007` | N/A | no | no | YES | no | no | YES | no | no | no | no | no | no | no |
| `BUG-008` | N/A | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-009` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-011` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-012` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-013` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-014` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-015` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-016` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-017` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-018` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-019` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-021` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-022` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-023` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-026` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-028` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-029` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-030` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-031` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-032` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-033` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-034` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-037` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-052` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-054` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-055` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-060` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-061` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-068` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-073` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-074` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-075` | FUNC-DEAD | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-077` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-078` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-079` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-080` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-081` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-083` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-090` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-095` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-096` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-101` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-102` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-103` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-104` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-106` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-110` | YES | YES | YES | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-111` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-178` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-179` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-180` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-270` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-271` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-272` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-273` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-274` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-275` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-276` | LAZY-WIRED | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-279` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-284` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-214` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-215` | YES | YES | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-216` | N/A | no | YES | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-217` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-218` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-221` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-222` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-224` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-225` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-205` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-226` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-227` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-228` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-230` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-231` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-232` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-233` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-234` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-235` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-236` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-237` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-238` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-239` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-240` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-242` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-244` | N/A | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-258` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
| `BUG-264` | YES | YES | no | no | no | no | no | no | no | no | no | no | no | no |
| `BUG-285` | YES | no | no | YES | no | YES | no | no | no | no | no | no | no | no |
| `BUG-133` | YES | no | no | YES | no | no | no | no | no | no | no | no | no | no |
