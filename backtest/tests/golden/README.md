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
