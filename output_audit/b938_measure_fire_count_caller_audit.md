# Batch 938 (2026-06-19): measure_fire_count.py Caller Audit + `--no-tier2` Escape Hatch

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 46 batch 2 commit 3 per CHECKLIST #77 (canonical-source declaration) + owner directive 2026-06-19 Option A. Outsider Council 44+46 strict warning: "Default-ON flag-flip: SEPARATE batch. Caller audit is its own work."

## Purpose

Before Phase P1 batch 3 can flip `--include-tier2` from default-OFF to
default-ON, this audit catalogs ALL existing callers of
`scripts/measure_fire_count.py` + classifies each by behavior dependency.

## Caller Inventory

### CRITICAL CALLERS (behavior changes if default flips)

| Caller | Path | Current flag usage | Risk if default flips |
|---|---|---|---|
| **AWS B660 bootstrap** | `scripts/aws_b660_bootstrap.sh` | NO flag (implicit OFF) | **HIGH** — production cron-like batch that runs measure_fire_count on AWS EC2 tmux. Currently measures pre-TIER 2 fires (102-strategy roster ish). Default-flip would silently enable TIER 2 on all ~219 strategies, changing fire counts. |
| **B660 launch** | `scripts/aws_b660_launch.py` | NO flag | **HIGH** — launcher for bootstrap; same exposure |
| **build_fire_bar_matrix** | `scripts/build_fire_bar_matrix.py` | NO flag | **MEDIUM** — fire-bar matrix diagnostic; behavior change downstream |
| **mean_reversion_edge_prior_test** | `scripts/mean_reversion_edge_prior_test.py` | NO flag | **MEDIUM** — prior test scaffold; behavior change |
| **diagnose_zero_fires** | `scripts/diagnose_zero_fires.py` | NO flag | **MEDIUM** — diagnostic tool; would change zero-fire-strategy classification |
| **checklist_106_cluster_a_producer_audit** | `scripts/checklist_106_cluster_a_producer_audit.py` | NO flag | **LOW** — one-off audit; non-recurring |
| **pit_universe_discipline_audit** | `scripts/pit_universe_discipline_audit.py` | NO flag | **LOW** — one-off audit |
| **b917_coverage_map_rescue_retest** | `scripts/b917_coverage_map_rescue_retest.py` | NO flag | **LOW** — diagnostic shipped during Phase P0 |

### EXPLICIT-FLAG CALLERS (safe; opt-in)

| Caller | Path | Current flag |
|---|---|---|
| **B922 validation micropilot** | `output_audit/b922_tier2_optin_validation.json` (post-run; was invoked with `--include-tier2`) | OPT-IN |
| **B926 validation micropilot** | `output_audit/b926_insider_classification_validation.json` (was invoked with `--include-tier2`) | OPT-IN |
| **B922 parity test** | `backtest/tests/test_b922_tier2_optin_bypass_parity.py` | (validates CLI flag presence) |

### REFERENCE-ONLY (no behavior dependency)

| File | Reason |
|---|---|
| `CLAUDE.md`, `CHECKLIST.md` | Documentation |
| `EXECUTION_QUEUE.md`, `OPEN_INVESTIGATIONS.md` | Audit log |
| `STAGE_4_CLUSTER_WALKS_INDEX.md` | Index doc |
| Various test files | Test references; no production behavior dependency |

## Risk Assessment

**HIGH-risk callers (2):** AWS B660 bootstrap + launch — production batch infra; default-flip silently changes fire-count outputs.

**MEDIUM-risk callers (3):** Diagnostic scripts; behavior change would propagate to derived data files.

**LOW-risk callers (3):** One-off audit scripts; re-running is owner-driven.

## Mitigation (B938 deliverables)

### 1. `--no-tier2` Escape Hatch (THIS COMMIT)

Per Outsider Council 44+46: add `--no-tier2` flag BEFORE default-flip.
Post-flip, callers that want pre-B922 behavior can add `--no-tier2`.

**CLI contract change:**
- Before: `--include-tier2` opt-in (default OFF)
- After (B938): `--include-tier2` + `--no-tier2` both available;
  `--no-tier2` overrides `--include-tier2` if both passed
- Phase P1 batch 3 (B939+): default flips to ON; callers needing OFF
  add `--no-tier2`

### 2. Caller Update Plan (BATCH 3 PREREQUISITE; NOT THIS COMMIT)

Before flipping default:
- [ ] AWS B660 bootstrap: add `--no-tier2` if pre-B922 behavior desired,
      OR remove flag for new TIER 2 behavior
- [ ] AWS B660 launch: same as bootstrap
- [ ] build_fire_bar_matrix: explicit owner decision needed
- [ ] mean_reversion_edge_prior_test: re-evaluate prior with TIER 2 fires
- [ ] diagnose_zero_fires: TIER 2 ON should be intent for "diagnose"
- [ ] checklist_106 + pit_universe + b917: one-offs; explicit `--no-tier2` if re-run

### 3. Backward-Compatibility Test (BATCH 3)

Per Outsider: `--no-tier2` reproduces pre-B922 output byte-identical.
Test framework: invoke measure_fire_count with `--no-tier2` on the
B922 fixture inputs; assert output matches pre-B922 baseline parity.

## Council 46 Compliance

| Council 46 mandate | Status |
|---|---|
| Caller audit findings doc | ✅ This file |
| `--no-tier2` escape hatch added | ✅ B938 CLI change |
| Default-OFF preserved this commit | ✅ |
| Backward-compat test framework | ⏳ B939+ (batch 3) |
| Default-ON flip | ⏳ B939+ (batch 3) |

## Phase P1 Batch 2 EXIT (commits B936-B938)

| Commit | Deliverable | Pyramid |
|---|---|---|
| B936 | Section 9b pre-cube evidence extractor (closes Council 45 design) | 1063 GREEN |
| B937 | Section 6 STATE/EVENT AST extractor + override JSON | 1076 GREEN |
| **B938** | Caller audit + `--no-tier2` escape hatch | TBD |

## Owner Decision Required for Phase P1 Batch 3

| Option | Action |
|---|---|
| (A) | **Approve batch 3 to flip `--include-tier2` default-ON** with explicit `--no-tier2` callers updated where needed (AWS bootstrap critical) |
| (B) | Update AWS bootstrap to use explicit `--include-tier2` FIRST; THEN flip default |
| (C) | Keep default-OFF permanently; require all dossier-building callers to set `--include-tier2` explicitly |
| (D) | Different direction |

**Council 46 recommendation:** (B) explicit-then-flip. Updates AWS bootstrap to declare intent BEFORE default changes.

---

## B939 RESOLUTION (2026-06-20; owner-approved Option B + Council 47)

Owner chose Option B; Council 47 verdict per-caller flag choices. All HIGH+MEDIUM-risk callers updated this commit.

### Per-caller flag updates SHIPPED (B939)

| Caller | Risk | Flag chosen | Rationale (Council 47) |
|---|---|---|---|
| `scripts/aws_b660_bootstrap.sh` | HIGH | `--include-tier2` | Production infrastructure; Phase P1 needs full coverage; TIER 2 IS production reality post-Phase-P0 |
| `scripts/aws_b660_launch.py` | HIGH | (docstring update) | Launcher; spawns bootstrap which carries flag |
| `scripts/diagnose_zero_fires.py` | MEDIUM | `include_tier2_producers=True` | Must distinguish "zero from gate-stacking" vs "zero from TIER 2 deferral" — without TIER 2 ON, structurally cannot answer its own question |
| `scripts/build_fire_bar_matrix.py` | MEDIUM | `include_tier2_producers=True` | Coverage diagnostic; truncating ~44 TIER 2-dependent strategies makes matrix non-representative of production engine path |
| `scripts/mean_reversion_edge_prior_test.py` | MEDIUM | `include_tier2_producers=False` (EXPLICIT) | STATISTICAL BASELINE artifact; prior computed pre-B922 with TIER 2 deferred; flipping silently re-bases prior + invalidates downstream Bayesian updates. Queue separate ticket to recompute prior with TIER 2 if Phase P1 needs it. |

### LOW-risk callers NOT updated (one-off audit scripts)

`checklist_106_cluster_a_producer_audit.py`, `pit_universe_discipline_audit.py`, `b917_coverage_map_rescue_retest.py` — explicit `--include-tier2` to be added if re-invoked. Per Council 47: defer; non-recurring scripts.

### Reference-only files (no behavior dependency)

CLAUDE.md / CHECKLIST.md / EXECUTION_QUEUE.md / OPEN_INVESTIGATIONS.md / PATH_TO_PHASE_1B_ALPHA.md + test files — documentation/audit only.

### Risk mitigation per Council 47

- **AWS first run = validation gate.** Cannot test pre-launch.
- **Pre-AWS pre-flight:** `aws_b660_launch.py --dry-run` locally; verify argv assembly + log lines.
- **Post-AWS Monitor:** intermediate per-shard fire counts; baseline-compare vs prior shard outputs (expect ~44 new strategies contributing); ABORT EARLY if total fires deviate >5× from projection.
- **Tag:** B939 commit tagged `phase-p1-batch-3-commit-1-aws-tier2-explicit` for forensic recovery.

### B940 NEXT (default-flip)

- Single-LOC argparse change: `--include-tier2` default OFF → ON
- Optionally rename to `--tier2/--no-tier2` BooleanOptionalAction for cleaner ergonomics
- Backward-compat test: invoke `measure_fire_count.py --no-tier2 <small-shard>`; assert fire-count matches pre-B922 baseline within tolerance on pinned strategy subset
- Pyramid green required pre-push
- Cleanup of redundant `--include-tier2` in B939 callers queued as B941 (separate; do NOT bundle into B940 per Council 47 anti-drift)

---

## B941 CLEANUP RESOLUTION (2026-06-20; owner-approved Option A)

Owner chose Option A (cleanup all redundant `--include-tier2` flags).

### B941 SCOPE NARROWED (honest finding)

During B941 execution, discovered that Council 47's "redundant" framing conflated two layers:

1. **CLI flag layer:** `--include-tier2` argparse default flipped to True via B940 resolution logic (`not args.no_tier2`). CLI invocations without flag now default to TIER 2 ON.
2. **FUNCTION parameter layer:** `_precompute_signals_for_ticker(include_tier2_producers=False)` — **still False at function level**. Removing explicit `True` from direct function calls would silently DISABLE TIER 2.

**B941 cleanup applies ONLY to layer 1 (CLI):**

| Caller | B941 Action | Reason |
|---|---|---|
| `scripts/aws_b660_bootstrap.sh` | `--include-tier2` CLI flag REMOVED | Redundant post-B940 CLI default-flip; comment notes `--no-tier2` to restore B660 v1 baseline |
| `scripts/diagnose_zero_fires.py` | **KEPT** `include_tier2_producers=True` | Function default still False; removing would silently break diagnostic intent |
| `scripts/build_fire_bar_matrix.py` | **KEPT** `include_tier2_producers=True` | Function default still False; removing would silently break coverage matrix |
| `scripts/mean_reversion_edge_prior_test.py` | **KEPT** `include_tier2_producers=False` | Explicit escape hatch for statistical baseline preservation per Council 47 |

### B942 OPTIONAL FUTURE WORK (separate batch)

If owner wants function-parameter default also flipped:
- `_precompute_signals_for_ticker(include_tier2_producers=False)` → default True
- Worker arg tuple resolution + downstream functions update
- Direct callers (diagnose_zero_fires + build_fire_bar_matrix) can then drop explicit `True`
- Mean-rev prior keeps explicit `False`
- ~15 LOC change across measure_fire_count.py
- Separate council on whether this drift is worth removing 2 explicit `True` declarations

**Council 47 anti-drift verdict applies:** function-default-flip is its own scope. Defer unless owner explicitly requests.

