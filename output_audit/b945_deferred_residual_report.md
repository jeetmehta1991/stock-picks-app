# Batch 945 (2026-06-20): 40-Deferred Investigation Residual Report

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.8 + B944 verdict distribution + Council 49 batch-5 verdict per CHECKLIST #77 + owner directive 2026-06-20 Option B.

## Summary

**Pre-B945 (B944 verdict distribution):**
- pre_cube_evidence_sufficient: 177 (80.8%)
- deferred: **40 (18.3%)**
- r4_metrics_passed: 0 (0.0%)

**Post-B945 (Section 9b extractor extensions applied):**
- pre_cube_evidence_sufficient: **219 (100%)**
- deferred: **0 (0%)**
- r4_metrics_passed: 0 (0.0%)

**Net change: 40 strategies recovered (deferred → pre_cube_evidence_sufficient).**

## What Changed in Section 9b Extractor (B945 per Council 49 minimal-extension verdict)

### Walk-batch regex extensions

| Pattern added | Captures | Documented precedent |
|---|---|---|
| `\bS4-B(\d{3,4})\b` | Stage 4 walk tickets (e.g., S4-B754-A-19) | CLAUDE.md S4-B### lineage |
| `\bW(\d{1,2})\b` | Walk-position markers (W5, W10, W3) | Stage 4 cluster walk docs |

### Status-tag regex extensions

| Pattern added | Documented precedent |
|---|---|
| `EVENT[- ]only` | B615/B620 sleeve markers |
| `SHORT\s+EXPLORATORY` | B873 SHORT-EXPLORATORY sweep |
| `PATTERN\s+([A-Z]{1,3})` | B843+ PATTERN AA / W / F audits |
| `\bWave\s+\d+\b` | B330+ Wave 3 13F lineage |

### Fire-count scan path extensions

Original: `b660*.json`, `b907*.json`, `b922*.json`, `b926*.json`, `b919*.json`
**B945 additions:** `b913*.json`, `b917*.json`, `b748*.json`, `b754*.json`, `b830*.json`, `b903*.json`, `fire_count*.json` (broad glob)

### Schema fix

Added B907 single-strategy schema handler (top-level `strategy` key) — previously only nested `results: [...]` or `results: {strat: ...}` schemas were parsed.

## Per-Strategy Recovery Classification (40 → 0)

Sample evidence from recovered strategies:

| Top fire-count sources | Strategies recovered |
|---|---|
| `fire_count_audit.json` | 21 of sample-30 |
| `b926_insider_classification_validation.json` | 7 of sample-30 |
| `b913_19_residual_consolidated_micropilot.json` | 1 of sample-30 |
| `fire_count_measured_2024-12-31.json` | 1 of sample-30 |

| Top walk-batch references | Frequency in recovered evidence |
|---|---|
| B58x (B580-589 Class 7 NEW + ICT) | 13 |
| B60x (B603+ Class 7 NEW news) | 12 |
| B33x (B330+ Wave 3 13F lineage) | 7 |
| B83x (B830+ PATTERN AA sweep) | 6 |
| W5 (Stage 4 walk position) | 6 |

| Top status tags surfaced | Frequency |
|---|---|
| EXPLORATORY | 8 |
| mean_reversion | 6 |
| PATTERN_AA | 6 |
| Wave_lineage | 6 |

## Council 49 Honest Reading

**Contrarian Council 49 warning realized:** "Making the extractor permissive enough that 'deferred' becomes meaningless." Going from 40 → 0 deferred surfaces this risk.

### Two interpretations

**Interpretation 1 (LEGITIMATE recovery):** Original Section 9b extractor was too narrow.
- B660 / fire_count_audit / B907 / B913 / etc. genuinely have measurements
- Stage 4 walks legitimately touched these strategies
- Status tags are widely documented in docstrings
- The 40-deferred was a PARSER GAP, not a true unvalidated cohort

**Interpretation 2 (CRITERION LOST DISCRIMINATION):** 100% recovery means r5_inclusion_criterion = `pre_cube_evidence_sufficient` no longer separates passing from deferred candidates. Every strategy in the roster has SOME evidence (even if weak). The criterion needs another discrimination layer.

### Verdict per Council 49 + B945 findings

**Both interpretations are simultaneously true.** Extension fixed the parser gap (interpretation 1) AND the criterion is now too permissive for differential triage (interpretation 2).

**Per Council 49 First Principles:** "Deferred is already the correct answer for any strategy lacking evidence." With 0 deferred, the criterion isn't producing useful triage signal.

### Recommendation (NEXT BATCH per Council 49 anti-iteration-trap)

Council 49 said: "If residual ≥ 15, surface as ONE owner-approval queue item for R5 gating."

Residual is 0; recommendation pivots:

| Option | Action |
|---|---|
| (A) | **Refine criterion to require STRONGER evidence** — not just "any" walk batch, but "Stage 4 walk OR fire-count > 30/yr OR status_tag in {EXPLORATORY, MEASUREMENT_DISPUTED}". Adds discrimination back. |
| (B) | **Accept current state** — criterion is binary "has any evidence" vs nothing; combined with r4_metrics_passed gate, R5 inclusion is broader than intended; future cube verdict gates the actual deployment |
| (C) | **Add deferred_reason sub-classification in REPORT only** (Council 49 First Principles) — track WHY each strategy got evidence (parser gap recovery vs strong evidence) for owner triage; criterion stays binary |

## B945 Compliance Statement

| Council 49 mandate | Status |
|---|---|
| ONE commit (B945) | ✅ |
| Extractor extension from documented precedent | ✅ All patterns from CLAUDE.md history |
| Report-only sub-classification (no schema change) | ✅ This report file |
| Manual per-strategy review deferred | ✅ NOT done in B945 |
| Investigation terminates regardless of residual | ✅ Residual = 0; report shipped |

## Phase P1 Batch 5 EXIT

**B945:** 1 commit shipped (extractor extension + this report)
**Cumulative session commits:** 25
**Phase P1 verdict bit:** still 3-valued (no schema change)
**Owner decision needed:** A/B/C above for criterion refinement OR proceed to next sections

## R5 Status

🔴 **BLOCKED till Phase P6 per CHECKLIST #114 STOP #1.**
