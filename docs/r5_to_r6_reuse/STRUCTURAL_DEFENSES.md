# Structural Defenses - R5 Session Build-Out for R6 Reuse

# Source: B1052 Council 145 R6 reuse documentation; sub-agent Bravo
# deliverable per owner mandate 2026-06-28 "Document the current workflow,
# processes, phases etc for reuse in r6. Ensure that its all coded and
# documented effectively for reuse. Be comprehensive." Per CHECKLIST #77.

## Purpose

This document catalogs the **six structural defense layers** built during the R5 session (B1042–B1051) to prevent the recurring `design-vs-armed` meta-bug class. Three recurrences in 24 hours (B1028, sub-agent polling false-positive, B1042 schema mismatch) drove owner directive 2026-06-28: "How will we address the misses in design vs armed? I don't want to keep demanding adversarial reviews." Council 139 + Council 140 produced the layered response codified here.

**R6 consumer:** R6 batch lead (first 3 batches) must read this document end-to-end before adding a single new producer, monitor, wrapper, or launch script. Each defense layer has a `How to use this in R6` section calling out the integration step.

## Cross-references

- Doc A (`R5_TO_R6_REUSE_INDEX.md`): document map + reading order
- Doc C (`CHECKLIST_INTEGRATION_GUIDE.md`): operational workflow stitching defenses together
- Doc D/E (sub-agent Charlie): launch-script reuse pattern + smoke gate cookbook
- Doc F (sub-agent Alpha): R5 batch lineage B1042–B1051 with commit IDs

---

## Layer 1: CHECKLIST #126 - Evidence-Artifact Rule

**Rule.** Any claim of `WIRED` / `ARMED` / `INTEGRATED` / `RESOLVED-IMPLEMENTED` requires a **linked evidence artifact**, not a code-presence grep.

**Why this exists.** Three 24-hour recurrences of the same meta-bug class:
1. **B1028:** banner said "monitor armed in user-data" - actual user-data contained the monitor invocation as a **comment** only. Sub-agent C polling for 1h+ saw the heartbeat-never-arrived because nothing ever fired.
2. **Sub-agent polling false-positive:** loose-proxy grep matching `sync_loop|phase_watchdog` satisfied "monitor armed" check while the B1019 monitor invocation was structurally absent.
3. **B1042 schema mismatch:** producer emitted `cells_completed` (int); consumer read `cell_count` (int). Local code-presence grep showed both sides "wired"; runtime broke silently.

**Two-tier status discipline.**
- `DESIGNED-NOT-VERIFIED` (default): code shipped but operational contract not proven via evidence.
- `OPERATIONALLY-VERIFIED`: schema-contract test in pyramid PASS **plus** linked evidence artifact (smoke output, AWS sentinel, or end-to-end integration output).

**Acceptable evidence artifact tiers** (increasing strength):
1. Schema-contract test PASS (Layer 4).
2. AWS smoke sentinel (Layer 2).
3. End-to-end output artifact actually consumed downstream.

**How to use this in R6.** Every R6 batch that claims to wire a producer-consumer pair MUST default the registry row to `DESIGNED-NOT-VERIFIED`. Promotion to `OPERATIONALLY-VERIFIED` is a separate explicit step requiring the artifact link in the commit body. Forbidden: banner promotion from a prior batch's claim without re-verification.

**Cross-references.** CHECKLIST.md #126, `feedback_designed_vs_verified_requires_evidence_artifact`, `feedback_monitor_design_vs_operational_gap`, Council 139 verdict.

---

## Layer 2: CHECKLIST #127 - AWS-Smoke-Mandatory-Gate

**Rule.** Any change to monitor / wrapper / integration code (the producer-consumer boundary) requires an **AWS smoke run** on real EC2 with a sentinel log BEFORE the change is considered SHIPPED and BEFORE any full-scale cube depends on it.

**Why this exists.** B1024–B1027 HALT-chain sunk $1.41 because integration code was promoted SHIPPED on local-pyramid evidence alone. B1028 added $1.20–2.70 spot burn on the same class of failure. Phase C v2.5 smoke caught the B1045 holdout-guard bug for **$0.49** versus an estimated $2–5 of Phase D burn plus 7–17 hours of debugging.

**Cost arithmetic.** ~$0.49 per smoke (12 min wall-clock + auto-terminate) is the insurance premium. Local pyramid catches in-process correctness; only real EC2 catches cloud-init, IAM, S3 round-trip, pip resolve, and wrapper-PID semantics.

**When the rule fires (smoke MANDATORY).**
- Producer-side change to `backtest/engine/backtest.py` emit cadence/schema, `backtest/results/writer.py` output format, `backtest/data/signal_loader.py` injector, any new S3 sentinel.
- Consumer-side change to `scripts/b1019_phase_1_runtime_monitor.py`, schema validator, dashboard parser.
- Wrapper change: launch-script PID capture, watchdog, monitor wrap, `nohup`/`setsid`/`disown` lifecycle, user-data inline assembly.
- Integration change: new row in `docs/PRODUCER_CONSUMER_PAIRS.md`, new schema-contract test in pyramid.

**When the rule does NOT fire (exempt).** Pure unit-test additions, pure doc/registry updates, bug fixes inside an already-tested call-path whose schema-contract test PASSES.

**How to use this in R6.** Every R6 wrapper/monitor change ends with an AWS smoke run sentinel link in the commit body. No exceptions, no "covered locally" override. R6's first batch should run the smoke gate end-to-end as the gate-validation exercise.

**Cross-references.** CHECKLIST.md #127, B1045 holdout-guard fix verdict, Phase C v2.5 sentinel output.

---

## Layer 3: Producer-Consumer Registry (`docs/PRODUCER_CONSUMER_PAIRS.md`)

**Artifact.** 42-row table indexing every producer-consumer relationship in the codebase where one module emits an artifact (JSON/CSV/parquet/log) that another module consumes.

**Why this exists.** B1042 Layer 1+2 schema mismatch (producer emitted `cells_completed` but consumer read `cell_count`) was invisible to grep-only verification. Schema drift between emit and consume is a silent miss class that local pyramid missed unless the schema itself is contract-tested.

**Schema.** Each row carries: producer `file:line`, output artifact, consumer `file:line`, schema keys, status (`DESIGNED-NOT-VERIFIED` vs `OPERATIONALLY-VERIFIED`), evidence link.

**Six categories swept** (B1044 Council 140 Option-5 fan-out, Sub-agent A scope):
1. Engine emit -> monitor / writer consumers
2. Signal-loader inject_* (10 funcs) -> screener consumers
3. Engine config -> engine consumers
4. Dashboard producers -> dashboard JS consumers
5. Writer outputs -> metrics / analyzers
6. Script utilities (correlation, lifecycle, roster, verification)

**Status discipline (Council 139 Layer D).** New rows default `DESIGNED-NOT-VERIFIED`. Promotion to `OPERATIONALLY-VERIFIED` requires the evidence link. As of B1051 the 42-row registry holds 16 OPERATIONALLY-VERIFIED rows (with explicit test or sentinel evidence) and 26 DESIGNED-NOT-VERIFIED rows.

**How to use this in R6.** Every new producer added in R6 MUST add a row to the registry **same turn** as wiring. Status defaults to `DESIGNED-NOT-VERIFIED`. The registry is the single source of truth - both sides of every producer-consumer relationship reference it.

**Cross-references.** `docs/PRODUCER_CONSUMER_PAIRS.md` rows 1–42, Council 139 Layer A verdict, B1042 schema-mismatch root cause.

---

## Layer 4: Schema-Contract Tests (52 tests)

**Artifacts.**
- `backtest/tests/test_schema_contracts.py` - Phase 1 baseline tests (15 rows x ~2 tests each)
- `backtest/tests/test_schema_contracts_phase2.py` - Phase 2 expansion (27 additional rows, patterns P2-A through P2-E)

**Why this exists.** Schema drift caught at test-time NOT runtime. Each registry row auto-derives a schema-contract test: producer emits keys X, consumer reads keys Y, test asserts X ⊇ Y. Drift on either side fails the pyramid before AWS spot is burned.

**Test patterns (Phase 2).**
- **P2-A:** Producer-side emit assertion (mock the producer, assert key set).
- **P2-B:** Consumer-side read assertion (mock the consumer, assert it tolerates schema).
- **P2-C:** Round-trip integration (real emit -> real consume on test fixture).
- **P2-D:** Status assertion (registry row must declare evidence link for OPERATIONALLY-VERIFIED).
- **P2-E:** Drift sentinel (file `mtime` newer than registry row triggers warning).

**Evidence artifact value.** A passing schema-contract test IS the tier-1 evidence artifact under #126. The registry row links to the test ID; the test ID links back to the row.

**How to use this in R6.** Adding a registry row automatically prompts a schema-contract test addition. R6's first batch should run `pytest backtest/tests/test_schema_contracts*.py -v` to confirm the gate is green before any wiring change.

**Cross-references.** Layer 3 registry, CHECKLIST #126 tier-1 evidence, B1044 Sub-agent A verdict.

---

## Layer 5: B1049 Variable-Scope Tests (`test_b1049_launch_script_var_scope.py`)

**Artifact.** Static-analysis test catching the `PHASE_DIR`-class variable-scope bug: a variable defined inside one bash function referenced outside it, which errors under `set -u` in the user-data heredoc context.

**Why this exists.** B1048 Phase D HALTED at preflight because `--output ${PHASE_DIR}/...` was referenced BEFORE `run_phase` had fired. The `set -uxo pipefail` directive in user-data turns unbound-variable into a hard error; the `|| true` fallback then emits a misleading sentinel (real failure is shell syntax, not application logic).

**Test technique.** AST-style split of `scripts/launch_r5_master_4y_v2.sh` at `run_phase` function boundary; assert every `${PHASE_DIR}` reference lies INSIDE the function block. Plus `bash -n` syntax-check on the rendered user-data and literal-path assertion against known-good paths.

**Honest-finding pivot lineage.** B1049 is PIVOT #29 of this session. Each pivot is documented as a CHECKLIST entry to prevent recurrence.

**How to use this in R6.** R6's launch script (whether a new file or a fork of `launch_r5_master_4y_v2.sh`) gets an equivalent variable-scope test. Pattern: identify scope boundaries -> grep references -> assert containment. The test runs as part of the launch-script pyramid sub-tier.

**Cross-references.** `feedback_silent_failure_pairing_rule`, CHECKLIST #122, B1048 HALT root cause.

---

## Layer 6: B1051 CLASS B–F Static-Analysis Tests (`test_b1051_launch_script_class_b_to_f.py`)

**Artifact.** Six classes of static-analysis tests covering bugs B1050 sub-agent found across the launch script + rendered user-data.

**Classes covered.**
- **C-1:** `master_tickers` Python injection robustness (handle comma OR newline separators).
- **C-3:** Master-tickers FAIL fallback sentinel source-file existence assertion.
- **C-4:** `pip install requirements.txt` paired with verification (every `|| true` requires an explicit success check per CHECKLIST #122).
- **C-5:** `nohup bash -c "$(date)"` deferred-substitution check (date binds to launch time, not nohup time).
- **A-2/A-3:** Missing `local` declarations inside bash functions (variable leak hygiene).
- **C-6/C-7/C-8:** Cosmetic issues (skipped - non-blocking).

**Test technique.** Regex-based static analysis on the launch script source plus the rendered user-data heredoc (`output_audit/_b1050_actual_userdata_full.sh`). No AWS or network required - runs in the unit pyramid.

**Why static analysis.** B1050 sub-agent verified empirically that several findings (C-1 newline-vs-comma) don't fire in the **current** S3 file format but would HALT Phase D if anyone regenerates the master with `\n.join()`. Static tests are pre-emptive defenses against format regression.

**How to use this in R6.** Each new launch script in R6 gets an equivalent CLASS B–F battery. Pattern: (i) render the user-data once and save; (ii) regex for known bug classes; (iii) skip with explanation when empirically-safe-now but bug-class-still-possible.

**Cross-references.** CHECKLIST #122 (silent-failure pairing), CHECKLIST #126 traceability requirement, B1050 sub-agent verdict.

---

## Extension Pattern: Adding a 7th Layer

If R6 needs a new structural defense:
1. **Identify the bug class.** Single recurrence is a coincidence; two recurrences is a pattern; three is a HARD-RULE candidate.
2. **Codify in CHECKLIST.** Add an entry under the next available number with: rule statement, why (incidents with batch IDs), when it fires, when it does NOT fire, evidence artifact format, self-reflexive default, cross-references.
3. **Build the artifact.** Test file, registry row, monitor script, or smoke gate.
4. **Add memory rule.** `feedback_<class_name>.md` linking the CHECKLIST item back to the source incidents.
5. **Update this document.** Add a "Layer 7" section using the template above.

---

## Failure-Mode Catalog: When Defenses Themselves Fail

- **Defense bypass via banner-claim.** Banner says "Layer 4 green" without re-running pyramid. Mitigation: CHECKLIST #126 forbids prior-batch promotion without re-verification.
- **Schema-contract test ships but registry row never added.** Mitigation: pyramid sub-tier P2-D asserts row-exists for every test ID.
- **AWS smoke ran but sentinel never written.** Mitigation: smoke gate requires `PHASE_smoke_PASS` sentinel; absence = HALT.
- **Static-analysis test skipped via `pytest.skip` with weak justification.** Mitigation: skip reason must include "empirically X as of YYYY-MM-DD" date pinning.
- **Memory rule edited away.** Forbidden under L86/L95 read-only rule. Memory rules accumulate; they don't get deleted.

---

## Cost-Benefit Summary

| Layer | Prevention scope | One-time cost | Per-batch cost | Failure cost averted |
|---|---|---|---|---|
| 1 (#126) | Banner-claim recurrence | 1 CHECKLIST entry | trivial (status discipline) | $1.41–$5+ per recurrence |
| 2 (#127) | Cloud-init / IAM / pip silent failure | 1 CHECKLIST entry + smoke harness | $0.49 per integration change | $2–5 Phase D burn + 7–17 hr debug |
| 3 (registry) | Schema drift invisibility | 42 rows audited | 1 row per new producer | Silent runtime failure mid-cube |
| 4 (52 tests) | Schema-contract drift | 52 tests written | auto-derived from registry | Silent runtime failure mid-cube |
| 5 (B1049) | Variable-scope HALT under `set -u` | 1 test file | 1 test per new launch script | Phase D HALT at preflight |
| 6 (B1051) | 7 launch-script bug classes | 1 test file | 1 battery per new launch script | Phase D HALT mid-run |

Maintenance cost: per-batch overhead is small (one registry row, one schema-contract test, one CHECKLIST status field). Failure cost averted is order-of-magnitude larger (sunk-cost AWS burn + hours of debug + erosion of trust in CHECKLIST gates).

---

## How to use this document in R6

**R6 batch 1.** Read this document end-to-end. Run `pytest backtest/tests/test_schema_contracts*.py backtest/tests/test_b1049_launch_script_var_scope.py backtest/tests/test_b1051_launch_script_class_b_to_f.py -v` to confirm all six layers are green before any code change.

**R6 batch 2.** Pick one structural defense to exercise end-to-end (e.g., add a new producer, add the registry row, write the schema-contract test, run the smoke gate). This validates that the gates fire on real work.

**R6 batch 3+.** Apply defaults: new producers default `DESIGNED-NOT-VERIFIED`; every monitor/wrapper/integration change runs the smoke gate; every launch-script edit triggers Layer 5+6 tests.

**Anti-pattern to avoid.** "We're moving fast, skip the gate." Owner directive 2026-06-28 explicitly forbids skipping. Each recurrence costs trust in the CHECKLIST system itself - that erosion compounds.

---

## Cross-reference summary

| Layer | CHECKLIST | Memory rule | Source batch | Test file |
|---|---|---|---|---|
| 1 | #126 | `feedback_designed_vs_verified_requires_evidence_artifact` | B1042 + Council 139 | (CHECKLIST item) |
| 2 | #127 | `feedback_monitor_design_vs_operational_gap` | Council 140 + B1045 | (CHECKLIST item) |
| 3 | #126 registry mandate | `feedback_designed_vs_verified_requires_evidence_artifact` | B1044 Sub-A | `docs/PRODUCER_CONSUMER_PAIRS.md` |
| 4 | #126 tier-1 evidence | (same as Layer 3) | B1044 | `backtest/tests/test_schema_contracts*.py` |
| 5 | #122 silent-failure pairing | `feedback_silent_failure_pairing_rule` | B1049 (PIVOT #29) | `backtest/tests/test_b1049_launch_script_var_scope.py` |
| 6 | #122 + #126 | (same as Layer 5) | B1050 + B1051 | `backtest/tests/test_b1051_launch_script_class_b_to_f.py` |

End of Doc B.
