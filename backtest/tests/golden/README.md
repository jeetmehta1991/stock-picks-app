<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1236 2026-07-07 doc-sync sweep -->

<!-- COUNCIL 278-287 SYNC BANNER (B1236 2026-07-07) — CLAUDE.md is the master status doc; body already partially synced (line 95 updated B1205) -->
> **CLAUDE.md is source-of-truth per L143.** Line 95 strategy count already updated B1205 (220 -> 219 post-B1189). This banner is here for consistency with the 46 other synced docs.
>
> Current canonical values as of 2026-07-07 (B1231):
> - 219 strategies registered; STRATEGIES_DISABLED_MISSING_PRODUCER empty
> - Test count: 858 passed, 2 skipped
> - CHECKLIST #1-#157, LEARNINGS L1-L202
> - Latest batch: B1235 (Council 287 doc-sync in progress)
> - Councils 278-287: 40 SKIP loosen + 11 silent misses fixed + 25+ producer audits + 2 critical bugs FIXED
> - Stage 4 walks archived to `archive/2026-07-07-stage-4-walks-complete/`
> - 3 Sprint 5 tickets queued
> - Comprehensive coverage report: `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# Golden fixtures - acceptance + snapshot pyramid layers

Pass 53 v8h+1 owner-mandated 2026-05-08.

## Contract

This directory holds known-good output fixtures used by acceptance and
snapshot tests:

| File | Source | Test |
|---|---|---|
| `phase_1a_baseline.json` | First successful Phase 1A run | `test_acceptance_phase_1a_golden_fixture_scaffolded` |
| `phase_1a_metrics.parquet` | Phase 1A 9-criteria matrix | numerical drift checks |

## When to regenerate

Regenerate a fixture only when the underlying calculation INTENTIONALLY
changes (e.g. an AUDIT.md decision adjusts a threshold). The regeneration
must:

1. Reference the AUDIT.md decision in the commit message
2. Update the related snapshot test's tolerance / floor
3. Pass owner review (snapshot drift is intentional, not regression)

## Why this exists today (before the run)

The acceptance test layer must be PRESENT pre-Phase-1A to keep the pyramid
honest. Today it asserts the fixture directory is set up. When the first
real Phase 1A baseline lands, drop the JSON here and the test auto-lights
up the numerical assertions.
