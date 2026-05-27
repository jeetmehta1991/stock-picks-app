# Testing Pyramid Reference

**Status:** Canonical source-of-truth for the 13-tier test pyramid.
**Owner:** mandatory per DEC-503 + CHECKLIST #69 + feedback_pyramid_full_13_tiers_mandatory.md
**Created:** Batch 345 2026-05-25 in response to owner directive to "Create a new testing pyramid reference md document".

This document supersedes the 9-tier subset in CHECKLIST #69 by enumerating the **full 13 tiers** from `IMPLEMENTATION_PLAN.md` Track T2 + `BATCH_318_PROCESS_POOL_DESIGN.md`. Any partial-pyramid run must report partial status per memory rule.

---

## Why 13 tiers, not 9

CHECKLIST #69 lists 9 test types (Unit / Smoke / Integration / System / Functional / Regression / Data integrity / Performance / Acceptance). `IMPLEMENTATION_PLAN.md` Track T2 lists 13 (adds Contract / E2E / Dashboard regen / Walk-forward).

Both are correct — the 9 are CORE; the additional 4 are CHANGE-CLASS-DEPENDENT. The 13-tier framing applies when ANY of the additional surfaces is touched:
- **Contract** triggers on engine API signature change
- **E2E** triggers on multi-module integration touching the production run path
- **Dashboard regen** triggers when a verification-matrix dimension changes
- **Walk-forward** triggers on strategy / exit / sizing / regime classifier change

The 9-tier baseline applies to every push; the additional 4 are mandatory when their trigger matches.

---

## The 13 Tiers

### Tier 1 — Unit
**What it validates:** Individual function correctness with mocked dependencies; pure-function behavior.

**Trigger:** Every code push.

**Tools:** `pytest`, `unittest.mock`.

**Test location:** `backtest/tests/test_unit.py` + `backtest/tests/test_silent_gap_pyramid.py` (DEC-503 silent-gap regression suite).

**Pass criteria:** All assertions pass; no exception during execution; coverage ≥ 90% per DEC-097 (hot-path 100% per DEC-098).

**Example:** `test_batch290_cap_band_producer_micro` asserts `cap_band_from_market_cap(50_000_000) == "micro"`.

**Failure example caught:** PEAD `compute_pead_signals` returning empty dict on Schema-B OHLCV — caught by direct invocation with synthetic Schema-B input.

---

### Tier 2 — Smoke
**What it validates:** Basic happy-path on real data; runs in ≤30s; verifies code path doesn't error end-to-end on minimal real-world inputs.

**Trigger:** Every code push that touches engine call-path, producer, or strategy registration.

**Tools:** `pytest`, real OHLCV from `data_prefetch/polygon/ohlcv_daily/AAPL.parquet`.

**Example:** Smoke test in `scripts/smoke_test_screen_pool.py --tickers AAPL,MSFT,NVDA,TSLA,JPM,XOM,JNJ,V --start 2024-01-01 --end 2024-06-30`.

**Pass criteria:** Exit 0; output files produced; expected-shape trade_log.

**Failure example caught:** `numba` Python 3.14 incompatibility surfaced immediately on first Hetzner smoke run.

---

### Tier 3 — Integration
**What it validates:** Module-to-module data flow. E.g. `fetcher → cache → signals → screener`. Verifies that the contract between modules holds when real data flows.

**Trigger:** Every code push that touches multiple modules OR changes a module API.

**Tools:** `pytest`, real (cached) data feeding through actual call chain.

**Test location:** `backtest/tests/test_integration.py` (149+ tests).

**Pass criteria:** End-to-end module pipeline produces expected output shape + values.

**Failure example caught:** BUG-218 (yfinance fetch_info CURRENT not as_of) — surfaced by integration test that fed engine sector_history → screener and observed timeline mismatch.

---

### Tier 4 — System
**What it validates:** Full end-to-end workflow on a representative subset. Full prefetch → universe load → backtest → report. Typically 10 tickers × 1 year or 25 tickers × 90 days.

**Trigger:** Code push touching the engine main loop / Portfolio class / position sizing / regime classifier.

**Tools:** `pytest` (slow tests gated by `--slow` marker) OR `python -m backtest.run_phase1a --tickers <small_list>`.

**Pass criteria:** Full run completes; output validates against acceptance criteria.

**Example:** Stage A/B/C smoke runs in `output_smoke_stage*/` directories (5-tkr × 6-12mo each).

**Failure example caught:** BUG-287 (orphaned open trades on tickers that fall out of liquid universe) — system smoke surfaced 6 stuck shorts held 371-1239 days.

---

### Tier 5 — Functional
**What it validates:** Feature behavior matches spec. Specifically, does the strategy / signal / producer compute the value the SPEC says it should compute?

**Trigger:** Strategy registration; new signal producer; spec interpretation work.

**Tools:** `pytest`, paired against literature citations OR canonical reference implementation.

**Pass criteria:** Computed signal matches expected within acceptable tolerance.

**Example:** `test_batch301_market_cap_polygon_reference_wires_correctly` validates that fetch_info's `market_cap` field equals what Polygon's reference parquet says (within $1).

**Failure example caught:** PEAD `pead_positive_surprise` flag was being silently NOT-SET because of fiscal_year-as-string bug.

---

### Tier 6 — Regression
**What it validates:** Full existing test suite still passes. No previously-validated behavior breaks.

**Trigger:** EVERY code push without exception.

**Tools:** `pytest backtest/tests/test_unit.py backtest/tests/test_integration.py backtest/tests/test_silent_gap_pyramid.py -q` (~1000+ tests as of Batch 345).

**Pass criteria:** 100% pass rate. NO permitted regressions.

**Past failure:** Multi-batch pyramid drift in Batches 49-68 (claimed "pyramid green" but actually 3 of 13 tiers; owner caught + corrected via memory rule `feedback_pyramid_full_13_tiers_mandatory.md`).

---

### Tier 7 — Data Integrity
**What it validates:** Schema correctness, PIT semantics, cache completeness, producer-vs-consumer key alignment.

**Trigger:** Any data-source migration (DEC tagged `data-source-migration`), any DEC that replaces `yfinance.*` / `pd.read_html` / `requests.get` calls with a different producer, any DEC touching the producer side of fields consumed by `_build_liquid_universe` / `is_liquid` / regime classifier / strategy entry gates.

**Tools:** `pytest backtest/tests/test_silent_gap_pyramid.py` (Batch 302 canonical implementation; 25+ tests).

**Pass criteria:** Producer-emitted keys match consumer-read keys; schema validates; PIT semantics preserved (no future data leakage); ≥90% data coverage on universe.

**Past failure pattern caught (L145, L146, L147 lessons):** 6 silent bugs over 6 months (META corruption, news Path B, 13F historical, PEAD financials_json, foreign_rev_pct, BUG-286 market_cap) — producer changed, consumer kept default, fail-closed gate silently rejected. The 13-tier pyramid was 100% green on the other layers.

---

### Tier 8 — Performance / Load
**What it validates:** Wall-time + memory bounds; rate-limit handling for API operations; no >5% degradation vs prior baseline.

**Trigger:** Hot-path code change (signal compute, engine day loop, screener loop, exit_manager, parquet I/O); pool worker count change; prefetch script.

**Tools:** `cProfile` + `pstats` + wall-clock measurement against prior baseline.

**Pass criteria:** Single-call cost ≤ baseline + 5%; full-run wall-clock measured against the latest validated baseline.

**Example:** Batch 315a benchmark — `index_rebalance` 272μs → 1.1μs (241× faster) after module-level cache hoist.

---

### Tier 9 — Acceptance
**What it validates:** Owner-defined pass criteria for the specific change.

**Trigger:** EVERY code push; criteria stated in pre-flight block + commit message.

**Tools:** Whatever the owner-spec says (manual review, specific output match, dashboard regen comparison).

**Pass criteria:** Match the owner-specified criteria exactly.

**Example:** Batch 322 acceptance was "verdict-critical columns byte-identical between sequential and pool runs" — met via the smoke harness.

---

### Tier 10 — Contract
**What it validates:** Public API surface of changed modules; backward compatibility with downstream consumers.

**Trigger:** Engine API signature change (BacktestEngine constructor kwargs, screen_instrument signature, _process_day method); strategy registration interface; consumer-facing helper signatures.

**Tools:** `inspect.signature()` + source-grep + integration test asserting consumer code still imports cleanly.

**Pass criteria:** Existing call sites work; signature additions are keyword-only with safe defaults; signature removals require deprecation notice + 1-release grace period.

**Example:** Batch 322 added `screen_pool_workers: int = 0` to `BacktestEngine.__init__` — Contract pass because default preserves prior behavior, kwarg-only insertion.

---

### Tier 11 — E2E (End-to-end)
**What it validates:** Multi-module integration on the production run path. Phase 1A microsmoke: 5 tkrs × 90 days through the full `run_phase1a.py` CLI.

**Trigger:** Code push that touches engine OR producer OR strategy registration AND can be exercised end-to-end.

**Tools:** `python -m backtest.run_phase1a --phase 1a --tickers AAPL,MSFT,NVDA,TSLA,JPM --start 2024-01-01 --end 2024-03-31`.

**Pass criteria:** Full CLI exits 0; trade_log.csv emitted; expected file shape.

**Example:** Stage D Hetzner run is the E2E for Phase 1A-β scale.

---

### Tier 12 — Dashboard Regen
**What it validates:** Verification matrix / dashboard outputs still emit cleanly. Catches schema regressions in dashboard data sources.

**Trigger:** Any code change that affects:
- `verification_matrix.json` columns
- `dashboard_stage_2/data.json`
- `dashboard_phase_1a/data.json` (or `_beta/`, `_b/`)
- AUDIT_INDEX status counts

**Tools:** `python scripts/sync_doc_counts.py --update` + `python scripts/build_phase_1a_beta_dashboard.py` (if applicable).

**Pass criteria:** Doc counts in `sync_doc_counts.py` stay consistent; dashboards regenerate without error; matrix counts match registered DECs/BUGs/INVs.

**Past failure caught:** Pass 53 Batch 171 dashboard cyclical 1-count oscillation (L151) — fixed by ensuring matrix-id extraction stays in sync with register.

---

### Tier 13 — Walk-forward
**What it validates:** Out-of-sample generalization of strategy performance. 1 fold (IS / OOS split).

**Trigger:** Strategy registration, exit method registration, signal-producer change that affects firing rate, sizing logic change, regime classifier change.

**Tools:** `backtest.engine.improvements.run_walk_forward(trade_log)` + `walk_forward_to_df`.

**Pass criteria:** OOS verdict ROBUST or AT-RISK; if FRAGILE, owner reviews before merge.

**Example:** Phase 1A-β post-merge walk-forward 4-fold validation per DEC-505. Stage D + Phase 1A-β both invoke run_walk_forward at the end.

---

## Layer Matrix

| Tier | Name | Always-on? | Trigger if conditional |
|---|---|---|---|
| 1 | Unit | YES | — |
| 2 | Smoke | YES (when engine/code-path touched) | — |
| 3 | Integration | YES | — |
| 4 | System | NO | Engine main-loop / Portfolio / sizing / regime change |
| 5 | Functional | YES (when spec interpretation work) | Strategy / signal / spec change |
| 6 | Regression | YES | — |
| 7 | Data Integrity | NO | Data-source migration; producer-side change |
| 8 | Performance | NO | Hot-path change; pool/concurrency change; prefetch script |
| 9 | Acceptance | YES | — |
| 10 | Contract | NO | API signature change; consumer-facing helper change |
| 11 | E2E | NO | Multi-module engine change; production run path |
| 12 | Dashboard regen | NO | verification_matrix / dashboards / status counts change |
| 13 | Walk-forward | NO | Strategy / exit / sizing / regime classifier change |

**Always-on (apply to EVERY push):** Tier 1 (Unit), Tier 3 (Integration), Tier 6 (Regression), Tier 9 (Acceptance). Tier 2 (Smoke), Tier 5 (Functional) apply when their narrow scope matches.

**Conditional (must be invoked when trigger matches; silent skipping = non-compliant per memory rule):** Tiers 4, 7, 8, 10, 11, 12, 13.

---

## Pre-flight reporting format

For any code push, the pre-flight block MUST state coverage explicitly:

```
Test pyramid coverage:
  T1 Unit:        ✅ 956 passed
  T2 Smoke:       ✅ (local + Hetzner)
  T3 Integration: ✅ 149 passed
  T4 System:      ✅ (Stage D 150-tkr × 4y)
  T5 Functional:  ✅ (cap_band micro/small/mid/large/mega)
  T6 Regression:  ✅ 1,034 passed (test_unit + test_integration + test_silent_gap_pyramid)
  T7 Data Integrity: ✅ (producer-key audit; no orphans)
  T8 Performance: N/A (test-only batch; no perf surface change)
  T9 Acceptance:  ✅ (owner-defined: cap_band gates strat_january_effect_long)
  T10 Contract:   N/A (no API signature change)
  T11 E2E:        ✅ (Stage D Hetzner)
  T12 Dashboard:  N/A (no matrix dimension change)
  T13 Walk-forward: ✅ (run_walk_forward emits ROBUST/AT-RISK/FRAGILE matrix)
```

Per memory rule [`feedback_pyramid_full_13_tiers_mandatory.md`](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_pyramid_full_13_tiers_mandatory.md): **any partial-pyramid run MUST be explicitly reported as partial with N/A reason; silent skipping = non-compliant**.

---

## Past failure catalogue

| Failure | Pyramid layer that would have caught | What actually happened |
|---|---|---|
| BUG-286 market_cap fail-closed | T7 Data integrity | Producer changed (yfinance → Polygon); consumer kept market_cap=0 default; 96.5% of universe silently rejected. Layer 7 was specified-but-not-built when this landed; codified in Batch 302 silent_gap_pyramid. |
| BUG-287 stuck shorts | T4 System | 6 shorts held 371-1239d while underlying rallied 2-5×. Surfaced post-Phase-1A-β; system test on 1937 × 4y caught it. |
| BUG-288 PEAD trio | T5 Functional + T7 Data integrity | fiscal_year stored as STRING + Schema-B OHLCV; 3 strategies fired ZERO trades. Two compounding silent gaps. |
| Batch 218 deprecation reversal | T9 Acceptance | 23 strategies deprecated by literature; owner directive 2026-05-25 wanted empirical not a-priori filtering; un-deprecated in Batch 316a. |
| Multi-batch partial pyramid (49-68) | T6 Regression | 20 batches claimed "pyramid green" while running 3 of 13 tiers; owner caught + memory rule codified. |
| smart_money silent gap (BUG-271/272/273) | T7 Data integrity | 3 of 4 Quiver endpoints silently 404 across all Phase 1A v3 results; codified DEC-503 in response. |

---

## Pre-Launch Validation Suite (Phase 1A-β composite gate)

**Status:** Canonical composite gate for any Phase 1A-β full launch. Batch 367 (initial 6 phases) + Batch 393 (expansion to 11 phases) per owner directive 2026-05-25 + 2026-05-26.
**Source-of-truth:** [scripts/pre_launch_validation.py](scripts/pre_launch_validation.py).
**Invocation:** `python scripts/pre_launch_validation.py` (single CLI). Wall-time ~6-12 min.

The pre-launch suite is **NOT a replacement for the 13-tier pyramid**. It is a composite gate that selects high-leverage assertions from multiple tiers and bundles them under one CLI specifically for Phase 1A-β launch readiness. The 13-tier pyramid still runs on every commit; the pre-launch suite runs once before a multi-day full-universe run.

### The 11 phases

| Phase | Name | Tier home | Catches |
|---|---|---|---|
| 1 | Data Prerequisites Audit | T7 Data Integrity | Missing prefetch dirs/files before the multi-day run starts |
| 2 | Generalized Fire-Rate Gate | T7 Data Integrity | BUG-296-family smart-money silent gaps (Quiver endpoint 404s) |
| 3 | Config Independence Smoke | T2 Smoke / T11 E2E | Env-var-dependency drift (QUIVER_API_KEY-class gate that broke Batch 363) |
| 4 | Silent-Gap Regression Suite | T6 Regression | One assertion per known BUG-NNN fix; protects against re-regression |
| 5 | Cube Cell Coverage Gate | T11 E2E | `save_all_outputs` cube failures that leave `trade_exit_detail` empty |
| 6 | Doc/Code Alignment Gate | T12 Dashboard regen | Count drift in CLAUDE.md / CANONICAL_FACTS.md / VERIFICATION_MATRIX.md |
| 7 | Post-Run Validation | T9 Acceptance / T11 E2E | (POST-RUN ONLY) trade_log/cube/winners/signal-fire-rates emitted correctly |
| 8 | Cube Gate Enablement Check (393) | T10 Contract | Verifies all 5 Phase-1A-β cube auto-enables (Batches 377/383/384/386) fire in current code — catches the bug class where a flag is added but never auto-set |
| 9 | Generalized Producer Emit (393) | T7 Data Integrity | Sweeps every required boolean producer across ~400 ticker-bar samples; catches always-False bugs (squeeze_fire_up / smc_equal_swept class) BEFORE strategies depend on them |
| 10 | Strategy Wiring Audit Gate (393) | T7 Data Integrity | Gates on `scripts/strategy_wiring_audit.py`; HARD-FAIL on producer-consumer mismatch / default-trap / synthesize inconsistency / type incompatibility |
| 11 | Intermediate Monitor Armed (393+394) | T9 Acceptance | Verifies the intermediate health monitor is in place + (Batch 394) the 14-check Python monitor + engine wall-time kwargs + milestone telemetry tokens. Covers wall-time kill at 6h, log-staleness, crash signatures, trade-rate floor, 100-day milestone floor, per-strategy zero-fire detection, direction balance, top-strategy dominance, year-pace deviation, runaway open positions, memory cap, disk free, SSH reachability. |

Phase 7 is excluded from pre-launch sweep (it runs against a freshly-merged output dir after the run completes). The pre-launch CLI runs phases 1-6 + 8-11 = **10 phases**.

### Mistakes this suite is designed to catch (lineage)

The expansion in Batch 393 is direct lineage from the 361-trade Phase 1A-β collapse on 2026-05-25:
- **Phase 8 (Cube Gate Enablement)** — root cause: cube flags 377/383/384 existed in code but were missing the `--phase=1a-beta` auto-enable, so the cube run inherited Phase-1A defaults that gated 99.96% of candidates. Phase 8 grep-checks the auto-enable banners + kwargs every time.
- **Phase 9 (Generalized Producer Emit)** — root cause: `squeeze_fire_up`/`squeeze_fire_dn` had a formula bug (`delta = close - mid20 + ema20` instead of `close - mid20`) making both ALWAYS-False; `smc_equal_highs/lows_swept` did `tail(20)` before filtering to liquidity rows, so the filter saw zero match. Phase 9 sweeps each required producer across ~400 random (ticker, bar) samples — any always-False emit rate is HARD-FAIL.
- **Phase 10 (Wiring Audit Gate)** — root cause: 185 strategies / 1,243 producer keys; manual review can't keep up with refactor velocity. Phase 10 gates on `strategy_wiring_audit.py` which uses a 3-layer producer-key index (static regex + runtime introspection + hardcoded supplement) + 4-attempt consumer synthesis to detect mismatches.
- **Phase 11 (Intermediate Monitor)** — root cause: the 361-trade collapse was only visible after the 4-hour Hetzner run completed. Phase 11 verifies an intermediate monitor is armed with abort thresholds (trade-count-per-day floor, fire-rate floor) so collapse triggers early-abort. **Batch 394 expansion (2026-05-27)** added defense-in-depth: engine-side wall-time kill at 6h via `sys.exit(1)` after final checkpoint flush + external Python monitor with 14 distinct check classes (W1-W14) covering wall-time, log staleness, crash signatures, trade-rate floor, 100-day cumulative milestone floor, per-strategy zero-fire at 50% completion, direction balance, top-strategy dominance, year-boundary pace, runaway open positions, memory cap breaches, disk free, and SSH reachability. The engine also emits structured `[MILESTONE-YEAR]` / `[MILESTONE-100D]` / `elapsed_hours=` telemetry tokens that the monitor parses every poll.

### Joint with the 13-tier pyramid

Pre-launch suite ≠ replacement for the 13-tier pyramid. Both run on every Phase 1A-β-touching push:
1. **Per-commit:** full 13-tier pyramid per CHECKLIST #69.
2. **Pre-launch (additionally):** 10-phase pre-launch suite gates the full multi-day run.
3. **Post-run:** Phase 7 + walk-forward (T13) gate the merged output.

If any pre-launch phase FAILs, the Phase 1A-β launch is BLOCKED — owner must triage before launch.

---

## Joint with other rules

- **CHECKLIST #67 (per-turn doc sync):** dashboard regen (T12) feeds doc-sync sweep.
- **CHECKLIST #69 (pre-push pyramid):** this DOC is the canonical reference; #69 is the rule-link.
- **CHECKLIST #71 (DEC-508 fork integration):** Tier 1-3 fork tests are the pre-merge gate for any vendored library work.
- **CHECKLIST #72 (DEC-591 data integrity):** Tier 7 is mandated by this checklist item.
- **CHECKLIST #75 (DEC-594 same-commit):** test artifacts must land in the same commit as the code they test.
- **DEC-503 (parent decision)** for this pyramid framework.
- **DEC-507 (agent toolkit wiring matrix HARD RULE):** sister process control; not part of pyramid but complements integration testing for Phase 1B+.
- **L145 / L146 / L147 / L148** lessons captured in past silent gaps.

---

## Pyramid health metrics (current)

| Metric | Value |
|---|---|
| Total tests in pyramid | ~1,034 (988 unit/integration/silent-gap + 19 paper-trading + ~27 fixtures) |
| Tier 1 (Unit) tests | 682+ |
| Tier 3 (Integration) | 149 |
| Tier 7 (Data integrity / silent-gap) | 125+ |
| Latest pyramid run | Batch 345 — 988 passed |
| Last partial-pyramid drift incident | Batches 49-68 (corrected; memory rule live) |
| Pre-launch composite gate | 10 phases live (Batch 393); see [Pre-Launch Validation Suite](#pre-launch-validation-suite-phase-1a-β-composite-gate) section |
