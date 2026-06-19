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
