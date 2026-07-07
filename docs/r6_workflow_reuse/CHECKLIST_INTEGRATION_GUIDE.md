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

# CHECKLIST Integration Guide - Producer-Consumer Registry, Monitor Wiring, and R6 Onboarding

# Source: B1052 Council 145 R6 reuse documentation; sub-agent Bravo
# deliverable per owner mandate 2026-06-28 "Document the current workflow,
# processes, phases etc for reuse in r6. Ensure that its all coded and
# documented effectively for reuse. Be comprehensive." Per CHECKLIST #77.

## Purpose

This document is the **operational stitching** between CHECKLIST #126, CHECKLIST #127, the producer-consumer registry, the schema-contract test pyramid, and the monitor-wiring workflow. Doc B (`STRUCTURAL_DEFENSES.md`) explains **what** each defense layer is; this document explains **how** they integrate end-to-end and **how R6 onboards** without bypassing them.

**R6 consumer.** R6 batch lead (first 3 batches) uses this document as the procedural runbook: every workflow step below maps to a concrete file edit, test invocation, or AWS smoke run. The anti-pattern catalog at the end calls out the failure modes seen in R5.

**Cross-references.**
- Doc A (`R5_TO_R6_REUSE_INDEX.md`): document map and reading order
- Doc B (`STRUCTURAL_DEFENSES.md`): the six defense layers in detail
- Doc D/E (sub-agent Charlie): launch-script reuse pattern + smoke-gate cookbook
- Doc F (sub-agent Alpha): batch lineage B1042–B1051 with commit IDs
- `docs/PRODUCER_CONSUMER_PAIRS.md`: 42-row registry (single source of truth)
- `CHECKLIST.md` #116–#127: AWS launch family

---

## Status Taxonomy

All registry rows and all CHECKLIST claims of WIRED / ARMED / INTEGRATED carry one of two status values:

### `DESIGNED-NOT-VERIFIED` (default for any new row or new claim)

- Code is shipped.
- Operational contract has NOT been proven via evidence artifact.
- Banner statements MUST surface this status (no silent omission).
- Forbidden uses: claiming the artifact is consumed in production; promoting downstream consumers to "wired" before the upstream is verified.

### `OPERATIONALLY-VERIFIED`

- Schema-contract test in pyramid PASSes for this producer-consumer pair, **AND**
- A linked evidence artifact exists (smoke output, AWS sentinel, or end-to-end integration output consumed downstream).
- Evidence link must be in the registry row's Evidence column **and** in the commit body that promoted the status.

**Promotion is a separate explicit step.** No batch ever auto-promotes a prior batch's `DESIGNED-NOT-VERIFIED` row to `OPERATIONALLY-VERIFIED` without re-running the evidence-generating step in the current batch's pyramid or smoke.

---

## Evidence Artifact Types (CHECKLIST #126 tiers)

In increasing strength:

### Tier 1 - Schema-contract test PASS

- File: `backtest/tests/test_schema_contracts.py` or `test_schema_contracts_phase2.py`.
- Coverage: producer emits key set X; consumer reads key set Y; assertion X ⊇ Y.
- Catches: schema drift on either side at pyramid time.
- Best for: pure in-process producer-consumer pairs (no AWS, no cloud-init, no sentinel).

### Tier 2 - AWS smoke sentinel

- Format: `s3://<bucket>/<RUN_ID>/PHASE_smoke_PASS` sentinel file.
- Contents: RUN_ID, instance-id, wall-clock duration, engine.log tail proving wrapper PID captured, monitor heartbeat emitted, producer wrote at least one consumer-readable artifact.
- Catches: cloud-init failures, IAM permission gaps, S3 round-trip latency, pip-resolve regressions, wrapper-PID semantics (the B1028 / B1042 / B1045 class).
- Cost: ~$0.49 per smoke (12 min wall-clock + auto-terminate).

### Tier 3 - End-to-end output artifact consumed downstream

- Format: actual output file (trade_log, equity_curve, dashboard payload) consumed by an actual downstream reader, with the consumer's output in turn observable.
- Catches: silent-pass failures, parser mismatches (F-04 class), zero-trade-day false negatives.
- Best for: full Phase D evidence after smoke proves cloud plumbing.

---

## Registry Workflow

The operational sequence for adding a new producer-consumer pair (any R6 wiring change):

### Step 1. Add a registry row

File: `docs/PRODUCER_CONSUMER_PAIRS.md`.

Columns (left to right): row index, producer `file:line`, output artifact path/name, consumer `file:line`, schema key list with types, status (default `DESIGNED-NOT-VERIFIED`), evidence link (default blank).

Same-turn as the wiring code change. The registry IS the contract.

### Step 2. Write the schema-contract test

File: `backtest/tests/test_schema_contracts_phase2.py` (or a new `phase3` file if R6 introduces a new category).

Pattern: pick P2-A through P2-E based on the boundary type (producer-mock, consumer-mock, round-trip, status-assertion, drift-sentinel).

Test ID convention: `test_p2_<category>_<row_index>_<short_name>`. Link the test ID in the registry Evidence column once it PASSes.

### Step 3. Run the pyramid

Command: `pytest backtest/tests/test_schema_contracts*.py -v`.

Required: all schema-contract tests PASS. The new test PASS is the tier-1 evidence artifact for this row.

### Step 4. AWS smoke (if change-class is monitor/wrapper/integration per #127)

When required: producer-side emit cadence/schema, consumer-side reader, wrapper PID capture, watchdog, monitor wrap, user-data assembly, OR new registry row that crosses an integration boundary.

When NOT required: pure unit-test addition, pure doc update, bug fix scoped to already-tested call-path.

Output: `s3://<bucket>/<RUN_ID>/PHASE_smoke_PASS` sentinel; sentinel URL goes in commit body.

### Step 5. Promote status

Edit registry row status `DESIGNED-NOT-VERIFIED` -> `OPERATIONALLY-VERIFIED`. Fill Evidence column with test ID (tier 1) or sentinel URL (tier 2) or output artifact path (tier 3). Commit message references the promotion explicitly.

---

## Memory Rule Integration

Three memory rules form the doctrine layer above CHECKLIST #126 / #127:

### `feedback_designed_vs_verified_requires_evidence_artifact`

- Origin: Council 139 verdict 2026-06-28.
- Rule: every WIRED/ARMED/INTEGRATED claim defaults `DESIGNED-NOT-VERIFIED` until evidence link exists.
- Operational artifact: CHECKLIST #126.

### `feedback_monitor_design_vs_operational_gap`

- Origin: B1028 failure 2026-06-27.
- Rule: designed monitor ≠ armed monitor; verify operational armament via heartbeat presence, not source-code presence.
- Operational artifact: CHECKLIST #117 + #121 + #127.

### `feedback_silent_failure_pairing_rule`

- Origin: B1028 pandas-ta install silent failure 2026-06-27.
- Rule: every `|| true` in shell/bash requires a paired explicit success check.
- Operational artifact: CHECKLIST #122; enforced statically by B1051 CLASS C-4 test.

These three rules are **read-only memory** per L86/L95: they cannot be edited away. They accumulate; they don't get pruned.

---

## Anti-Patterns Catalog (R5 incidents)

The following behaviors are forbidden - each maps to a specific R5 recurrence.

### Anti-pattern 1: Code-presence grep alone

**Example.** "I greped `sync_loop|phase_watchdog` and matched - monitor is armed."
**Why forbidden.** Loose-proxy grep matched COMMENT lines in B1028 user-data while the monitor invocation was structurally absent.
**Correct.** Heartbeat in monitor log + S3 sentinel + smoke output. Code-presence grep is necessary but not sufficient.

### Anti-pattern 2: Banner-claim promotion across batches

**Example.** "Prior batch said RESOLVED-IMPLEMENTED so it's still resolved."
**Why forbidden.** Three of the four DESIGNED-NOT-VERIFIED entries promoted to OPERATIONALLY-VERIFIED across B1010–B1042 were promoted on stale banners, not re-verification.
**Correct.** Re-verify in the current batch. If the verification step doesn't run this batch, status remains as the prior batch left it.

### Anti-pattern 3: Smoke skipped because "covered locally"

**Example.** "Local pyramid is green so we don't need AWS smoke for this monitor change."
**Why forbidden.** B1024–B1027 HALT-chain ($1.41 sunk) happened on monitor changes that passed local pyramid.
**Correct.** CHECKLIST #127 lists which change-classes require smoke. No exceptions.

### Anti-pattern 4: Skipping a static-analysis test with weak justification

**Example.** "Skip B1051 C-1 newline-format test, file is comma-separated anyway."
**Why forbidden.** Empirical-now ≠ structurally-safe. Format regression would HALT Phase D mid-run.
**Correct.** Skip with date-pinned justification: `"empirically comma-separated as of YYYY-MM-DD; defensive only if file regenerates with \\n.join()"`.

### Anti-pattern 5: Documentation IS the work

**Example.** "I wrote the structural-defense doc; the defense exists."
**Why forbidden.** Per `feedback_no_write_only_md_files`, write-only docs are forbidden. The defense exists when the test PASSes and the smoke gate fires.
**Correct.** Documentation references the test ID and the smoke sentinel; both must exist as referenced artifacts.

### Anti-pattern 6: Bypassing the smoke gate "to move fast"

**Example.** "We need to launch Phase D today; skip the smoke."
**Why forbidden.** Owner directive 2026-06-28 explicitly forbids skipping. Each recurrence erodes trust in the CHECKLIST system itself.
**Correct.** $0.49 + 12 min wall-clock is non-negotiable insurance.

---

## CHECKLIST #116–#127 Family Cross-Reference (AWS Launch Family)

The structural defenses sit inside a broader CHECKLIST family covering AWS launch end-to-end. Each item below has a memory rule and a batch lineage; refer to `CHECKLIST.md` for full text.

| # | Rule | Source batch | Memory rule |
|---|---|---|---|
| 116 | AWS user-data 16KB limit (post-base64 33% expansion) | B1028 first attempt | `feedback_aws_user_data_size_preflight` |
| 117 | Monitor arm AT event boundary, not pre-launch | B1021 | `feedback_monitor_arm_at_event_not_pre_launch` |
| 118 | Per-strategy lint sub-pyramid at wire-time | B1010 + B1014 | `feedback_per_strategy_gate_audit_at_wire_time` |
| 119 | Verify Council verdict prerequisites BEFORE execute | Council 116 | `feedback_verify_council_verdict_dependencies_pre_execute` |
| 120 | Do NOT auto-relaunch corrected version after HALT | B1027 | `feedback_ask_before_relaunching_corrected_version` |
| 121 | Designed monitor ≠ armed monitor | B1028 | `feedback_monitor_design_vs_operational_gap` |
| 122 | Every `|| true` paired with success check | B1028 pandas-ta | `feedback_silent_failure_pairing_rule` |
| 123 | Phase-ladder timing validation empirically | B1028 Phase 1 | `feedback_phase_ladder_timing_validation` |
| 124 | (reserved) | - | - |
| 125 | (reserved) | - | - |
| **126** | **Evidence-artifact rule (the meta-defense)** | Council 139 | `feedback_designed_vs_verified_requires_evidence_artifact` |
| **127** | **AWS smoke mandatory gate** | Council 140 sub-C | (anchored to #126) |

The family covers: user-data size limits, monitor timing, gate audits, dependency verification, HALT discipline, design-vs-armed defenses, silent-failure pairing, ladder validation, and the meta-rules #126/#127 enforcing evidence linkage and pre-scale smoke.

---

## R6 Onboarding Workflow

The first three R6 batches MUST NOT skip these gates. Suggested sequence:

### R6 batch 1 - Gate validation (no code change)

1. Read Doc A, Doc B, Doc C end-to-end.
2. Run pyramid: `pytest backtest/tests/test_schema_contracts*.py backtest/tests/test_b1049_launch_script_var_scope.py backtest/tests/test_b1051_launch_script_class_b_to_f.py -v`.
3. Verify all six structural defenses green.
4. Confirm `docs/PRODUCER_CONSUMER_PAIRS.md` registry reads cleanly (42 rows, status column populated for every row).
5. Output: a "gates-green" baseline commit, no functional code change.

### R6 batch 2 - Walk one end-to-end producer-consumer cycle

Pick the smallest available producer-consumer pair (e.g., a new sentiment signal, a new dashboard tab) and walk it end-to-end:

1. Add the registry row (status `DESIGNED-NOT-VERIFIED`).
2. Write the schema-contract test.
3. Run pyramid (test PASSes).
4. If the change crosses an integration boundary per #127, run AWS smoke.
5. Promote registry row to `OPERATIONALLY-VERIFIED` with evidence link.
6. Commit. The commit body must reference: registry row #, schema-contract test ID, smoke sentinel URL (if applicable).

This batch exercises the full workflow and validates that R6 understands the gates operationally, not just textually.

### R6 batch 3 - First "real" wiring change

Now apply the workflow to a real R6 deliverable. By this batch, the defaults should feel automatic:
- Every new producer adds a registry row same-turn as the code change.
- Every change touching the producer-consumer boundary runs the smoke gate.
- Every launch-script edit triggers Layer 5 (variable-scope) + Layer 6 (CLASS B–F static) tests.

If batch 3 ships without firing the gates, owner directive applies: investigate why the workflow felt skippable and codify the next CHECKLIST entry preventing recurrence.

---

## How to use this document in R6

**As a runbook.** When a new producer-consumer pair appears, follow the Registry Workflow section verbatim.

**As a reference.** When unsure whether the smoke gate fires, consult the "When the rule fires" subsection of Layer 2 in Doc B.

**As a doctrine refresher.** When an R6 batch contemplates "moving fast" or "skipping the gate," re-read the Anti-Patterns Catalog. Each anti-pattern maps to a specific R5 cost ($1.41 sunk, 7–17 hours debugged, owner trust eroded). The gates are non-negotiable not because they are bureaucratic but because they are the only thing standing between R6 and recurrence.

End of Doc C.
