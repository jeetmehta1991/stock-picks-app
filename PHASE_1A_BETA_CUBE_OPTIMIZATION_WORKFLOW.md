# Phase 1A-beta Cube Optimization Workflow

**Locked 2026-05-28** (owner directive: "Lock the above. ... Create a new reference md file").

**Status.** Canonical reference for how (strategy × exit × regime) cube data flows from a Phase 1A-beta cube run through optimization → owner review → implementation → re-validation → the 1A-α owner gate. Authoritative across re-run iterations. Stage 1 (the AWS cube run) is the only stage that is environment-specific; Stages 2-6 are platform-agnostic and re-used on every iteration.

---

## Source attribution (per CHECKLIST #77)

- **Owner directive 2026-05-28:** "We need to view the cube at a strategy×exit cell level only, not aggregated. Optimize strategies and exits as per earlier frameworks."
- **Unified view locked** through owner Q&A across 2026-05-28 turns (Stages 1-6 + dashboard expectations).
- **Underlying script SSOTs:**
  - `scripts/optimize_strategies_from_cube.py` — Batch 388 (9 dimensions per-strategy) + Batch 391 `analyze_exit_methods()` (3 layers per-exit) + Batch 389 `producer_zero_reaudit()` (3-bucket quiet-strategy classification including COMPOUND_RESTRICTIVE).
  - `scripts/aws_batch395_merge.py` — Batch 395 (5-AWS-batch merge + inline cube rebuild per Batch 359).
  - `scripts/rebuild_cube_from_trade_log.py` — Batch 359 (fallback cube rebuild from trade_log + OHLCV cache; called by merge inline; usable standalone).
  - `backtest/engine/exit_strategies.py::run_exit_comparison` — cube engine.
  - `scripts/build_dashboard_phase_1a.py` — dashboard build (Sprint 6.5, Batch 177).

## Core principle (do not violate)

**Unit of analysis: `(strategy × exit_method × regime)` CELL.** Live: `len(ALL_STRATEGIES) × len(EXIT_STRATEGIES) × 7 regimes = 185 × 25 × 7 = 32,375 cells`. No batch-aggregated PnL anywhere. Aggregation is the trap; cells are the answer (`feedback_strategy_x_exit_cell_analysis.md`).

DEC-426 5-Gate validity per cell: `n ≥ 30`, `p < 0.05` Bonferroni-corrected over 4,625 cells/regime, `PSR ≥ 0.95`, `t ≥ 3.4`, `R:R ≥ 2.0`. CLAUDE.md 11 criteria layered on top per cell.

No a-priori pruning (`project_no_apriori_strategy_pruning.md`): a strategy may be deprecated only if its 25-exit cube row shows 0 PASS cells in any regime AND 0/25 exits fire `n ≥ 30` in any regime.

---

## Stage 1 — Cube run

**Action.** Run Phase 1A-beta engine across the full universe (~1937 tickers × ~5y × 185 strategies × 25 exits). 5-batch AWS orchestration via `scripts/aws_batch395_*.py` is the canonical execution path; single-machine Hetzner remains the fallback.

**Outputs (per batch, before merge):**
- `outputs/batch_N/trade_log.csv` (fires with `signals_at_entry` JSON)
- `outputs/batch_N/trade_exit_detail.csv` (cube rows: one per `trade × exit_method`)
- `outputs/batch_N/skipped_trades.csv` (gate-rejection reasons)
- `outputs/batch_N/_COMPLETE` (sentinel)
- `forensic/batch_N.json` (per-batch verdict from `aws_batch395_forensic_per_batch.py`)

**Merge (`scripts/aws_batch395_merge.py --bucket <name> --upload-final`):**
- Produces `output_phase_1a_beta_aws_merged/trade_log.csv` + `trade_exit_detail.csv` + `skipped_trades.csv`.
- If cube file missing post-merge, inline call to `rebuild_cube_from_trade_log.py` regenerates it (Batch 359 path closes the legacy gap where `merge_batch_outputs.py` dropped trade_exit_detail).

**Dashboard view/expectations:**
- All 13 existing tabs (Overview / 1. Strategies / 2. Regime / 3. MAE/MFE / 4. Equity / 5. Walk-fwd / 6. Smart-$ / 7. Sector / 8. Skipped / 9. CircuitBreakers / Exits / Trades / Raw JSON) are STALE during run; do not regenerate until merge completes.
- **NEW Overview widget "Run Status"** consumes per-batch `_COMPLETE` sentinels + forensic JSON: shows `5/5 _COMPLETE`, per-batch wall-time, forensic verdict per batch (PASS/WARN/ABORT). Visible during run; settles when merge lands.
- **Refresh trigger (post-merge):** `python scripts/build_dashboard_phase_1a.py --source output_phase_1a_beta_aws_merged`.

---

## Stage 2 — Optimizer

**Command:**
```bash
python scripts/optimize_strategies_from_cube.py \
    --input-dir output_phase_1a_beta_aws_merged \
    --output-dir output_optimization_candidates_<YYYY_MM_DD>
```

**Two analytical lenses on the same cells (single script, single invocation):**

### Lens A — per-strategy 9 dimensions (Batch 388)

For each fired strategy + each quiet strategy:

| Dim | Question | Key memory / DEC |
|---|---|---|
| A | Entry-gate thresholds — which clauses are BINDING vs LOOSE? | DEC-422 |
| B | **Compound logic — AND-clause individual fire rates + pairwise correlations** | **← COMPOUND_RESTRICTIVE optimizations originate here** |
| C | Regime applicability — per-regime DEC-426 5-Gate verdict | CLAUDE.md #11 |
| D | Best exit pairing — best exit by Sharpe per strategy | shared with Lens B Layer 2 |
| E | Position sizing tier — Sharpe → tier mapping recommendation | CLAUDE.md sizing table |
| F | Universe filtering — per-sector / cap_band verdict | DEC-303 |
| G | Hold-duration limits — empirical hold-days distribution | DEC-521 |
| H | Cooldown / re-entry — post-stop re-entry behavior | DEC-018 |
| I | Macro overlay — per-macro-regime verdict | DEC-348 |

### Lens B — per-exit 3 layers (Batch 391 `analyze_exit_methods`)

| Layer | What it produces | Action implied |
|---|---|---|
| L1 — per-exit aggregate | Across all 185 strategies that used each of 25 exits: aggregate Sharpe, PF, WR, n. Ranks exits with `n_strategies_paired ≥ 5` gate. | Top-5 = default-good exits for new strategies; bottom-5 = deprecation candidates only if L2 confirms 0 PASS cells anywhere. |
| L2 — per-(strategy × exit) cell verdict | Each cell `n ≥ 5`: Sharpe + DEC-426 5-Gate. PASS cells become `STRATEGY_EXIT_OVERRIDE` candidates. | Direct evidence for deployed config per strategy. Feeds Phase 1B-α winners list. |
| L3 — within-family variant ranking | `time_stop` (10d/20d/class_time_stop), `r_multiple` (2r/3r), `trailing` (5/10/15pct), `atr_trail` (1x/2x/mae_conditional/vix_conditional), `chandelier`, `breakeven`, `partial` (multi_tier_partial/hybrid_50pct_target). | Per-family default + per-strategy override. |

### Bucket classification (Batch 389 `producer_zero_reaudit`)

For quiet (zero-fire) strategies, three buckets:
- **PRODUCER_LAYER_ZERO_LIKELY** — gate keys' truthy emission absent from empirical signal corpus → producer-layer fix required.
- **COMPOUND_RESTRICTIVE** — individual clauses DO emit truthy, but the AND-compound never satisfies → Dim B compound restructure or Dim A threshold loosening.
- **SKIPPED_AT_ENGINE** — appears in `skipped_trades` → downstream gate (likely already removed by Batches 377/383/384/386; re-check binding gate).

Phase 1A-beta single-batch baseline (2026-05-26) showed ~106 COMPOUND_RESTRICTIVE strategies. Post-AWS-cube re-audit will produce the live count + per-strategy gate-keys table.

**Dashboard view/expectations:**
- All 13 existing tabs refresh against the merged AWS cube. Expected counts: ~29k trades, ~85-100 fired strategies of 185, ~32,375 cells computed.
- **NEW "Optimizer Status" widget on Overview** — last-run timestamp, input/output dirs, runtime, summary.md top-line proposals.

---

## Stage 3 — Outputs

Three reviewable artifacts emitted to `output_optimization_candidates_<YYYY_MM_DD>/`:

| Output file | Dashboard view (new unless noted) |
|---|---|
| `optimization_summary.md` (living) | **NEW tab "Optimizer Summary"** — server-side render. Top blocks: bucket counts + L1 exit ranking + L2 PASS-cell table + L3 family-winner mapping + top proposals. |
| `optimization_candidates_<strategy>.json` (~85-100 files) | **NEW tab "Candidates"** — per-strategy drill-down sidebar. Shows 9-dim findings + L2 winning-exit cells per regime + L3 family-winner mapping + proposed changes. Per-change approval radio: Approved / Rejected / Deferred / Awaiting. State persists to `approvals.json`. |
| `producer_zero_reaudit.json` | **NEW tab "Quiet Strategies"** — 3-column layout PRODUCER_LAYER_ZERO_LIKELY / COMPOUND_RESTRICTIVE / SKIPPED_AT_ENGINE. Per-strategy gate-keys + per-clause empirical fire rate + Dim B compound-restriction analysis. COMPOUND_RESTRICTIVE highlighted as priority. |
| (master cell table — derived) | **NEW tab "Cell Verdict Cube"** — 32,375 cells (185×25×7 regimes), sortable by Sharpe/PF/WR/n/p/PSR, filterable by `cell_verdict ∈ {PASS, FAIL, INSUFFICIENT_SAMPLE}` and regime. PASS highlighted. **Single source of cell-level truth.** |

**Existing tab auto-mappings:**
- **2. Regime** — per-regime PASS-cell counts (Dim C).
- **Exits** — L1 aggregate ranking (renders Batch 391 L1 output directly).
- **8. Skipped** — gate-rejection reasons joined with `producer_zero_reaudit.json` bucketing.
- **7. Sector** — Dim F per-sector cell verdicts.
- **3. MAE/MFE** — MAE-of-winners distribution feeding `atr_trail_mae_conditional` recommendation.

---

## Stage 4 — Owner review + per-change approval

**Owner interacts with the Candidates tab.** No bulk approvals. Each candidate change has status: Approved / Rejected / Deferred / Awaiting.

**Six change classes the owner approves from:**
1. `STRATEGY_EXIT_OVERRIDE` — per L2 PASS cell
2. Entry-gate threshold loosening — per Dim A BINDING analysis
3. Compound-logic restructure — per Dim B (priority queue: 106 CR strategies)
4. Sizing tier remap — per Dim E
5. `STRATEGY_REGIME_AFFINITY` — per Dim C (re-engaged in 1B-α; Phase 1A-β bypassed via `--no-regime-affinity`)
6. Roster deprecation — only if cell shows 0 PASS in any regime, per `project_no_apriori_strategy_pruning` empirical-only rule

**Dashboard view:**
- **Candidates tab** counts header: "N Approved / N Rejected / N Deferred / N Awaiting" with class filter.
- **Cell Verdict Cube tab** — PASS cells mapped to an approved change show green check; rejected show red.
- **dashboard_stage_2** — DEC count climbs as approved changes get logged (Stage 5).

---

## Stage 5 — Implementation batches

**Discipline (per `feedback_path_c_min_batch_size`):** bundle 5+ approved changes per batch. Per-DEC unit-test isolation preserved; integration + e2e pyramid runs once per batch (per `feedback_pyramid_per_addressal` + `feedback_pyramid_full_13_tiers_mandatory`).

**Touch points:**
- `backtest/config.py` — `STRATEGY_EXIT_OVERRIDE`, `STRATEGY_REGIME_AFFINITY`, `PASSING_CRITERIA`, sizing tier mappings.
- `backtest/signals/screener.py` — `strat_<name>` per-strategy threshold + compound-logic edits.
- `backtest/engine/exit_strategies.py` — only if exit-method behavior itself changes (rare).
- `backtest/config.py::DEPRECATED_STRATEGIES` / `STRATEGIES_DISABLED_MISSING_PRODUCER` — for deprecations (empirical only).

**Per-push gates:** full 13-tier pyramid + `feedback_pyramid_no_exceptions` (no doc/data carve-outs) + CHECKLIST #67 doc-sync per turn (commit & push within same turn).

**Dashboard view:**
- **dashboard_stage_2** — new DEC IDs created per change with `RESOLVED-DECIDED` or `RESOLVED-IMPLEMENTED` status linking back to the candidate JSON that motivated each.
- **Overview "Last Implementation Batch" widget** — batch number, commit SHA, summary of changes applied.
- **Candidates tab** — approved candidates' status flips to "Implemented (batch N, commit SHA)".
- **NEW "Pyramid badge" top-of-page** — last full 13-tier result. Green if all 13 passed; red with failed-tier name otherwise. Mandatory pre-push state.

---

## Stage 6 — Re-run + walk-forward + 1A-α gate

**Re-run:** modified roster + `--vectorized-cube-exits ON` (post-Batches 412+413; expected ~20-25% engine wall-time saved when both Tiers are activated). Activation only after current cube validates that Tier 1+2 produce byte-identical results.

**Walk-forward (DEC-505):** rolling 3y in-sample / 1y out-of-sample per cell. Walk-forward Sharpe ≥ 0.7 OOS in ≥1 regime is the per-cell gate.

**1A-α owner gate (per CLAUDE.md):** ≥1 strategy passing rules-only Sharpe ≥ 0.7 OOS in ≥1 regime → GATE OPEN → $300 Phase 1B-α agent overlay budget eligible to commit.

**Loop condition:** loop Stage 4 → Stage 5 → Stage 6 until cell verdicts stabilize (PASS-cell count delta < 5% iter-over-iter) AND 1A-α gate passes.

**Dashboard view:**
- All 13 tabs refreshed against the new cube. Each implemented change has a **"Lift" column** on Candidates tab showing predicted-vs-actual metric movement.
- **5. Walk-fwd tab** becomes load-bearing — renders DEC-505 IS/OOS per cell.
- **NEW "1A-α Gate" widget on Overview** — single badge: `GATE LOCKED` (red) / `GATE OPEN` (green) + count of strategies passing the threshold.
- **Cell Verdict Cube tab** re-rendered; PASS-cell count diff vs prior run = primary loop-stability metric.

---

## Dashboard build-script touch points (Batch 415+ work, post owner-approval)

Implementation queue once owner approves dashboard expansion:

| File | Change |
|---|---|
| `scripts/build_dashboard_phase_1a.py` | Extend to load `output_optimization_candidates_<date>/` files. Emit `data.js` payload sections for: Optimizer Summary / Candidates / Quiet Strategies / Cell Verdict Cube / 1A-α Gate widget / Run Status widget / Last Implementation Batch widget / Pyramid badge. |
| `dashboard_phase_1a/index.html` | 4 new `<button class="tab-btn">` entries + 4 new `<div class="tab-pane">` sections. New Overview-tab widget HTML. |
| `scripts/build_dashboard_stage_2.py` | Extend to consume `approvals.json` so each DEC has auditable link to the candidate JSON + approval timestamp. |
| `backtest/tests/test_dashboard_phase_1a.py` (new or extend) | Test-pin per `feedback_doc_count_drift_must_be_test_pinned`: `test_dashboard_phase_1a_tab_count` asserts 17 tabs after expansion (13 existing + 4 new). `test_dashboard_phase_1a_cube_cell_count` asserts cells = `len(ALL_STRATEGIES) × 25 × 7` re-derived live, not hardcoded. |

---

## What this workflow REPLACES

- The earlier 5-step "post-merge workflow" (covered Stages 1-3 only; superseded by this 6-stage view).
- All batch-aggregated PnL reporting (e.g., `all_regimes_negative_pnl` checks in `aws_batch395_forensic_per_batch.py`). The forensic script's batch-level WARN remains useful for in-flight kill-switch (catastrophic engine crashes; circuit breaker), but its findings do NOT inform optimization. Cell-level cube findings do.

## What this workflow does NOT cover

- Phase 1B-α agent overlay (TradingAgents pipeline, $300 Haiku budget) — kicks in only after 1A-α gate passes.
- Stage 3+ archived watchlist (DEC-495) — out of scope until Stage 3 papertrading.
- Stage 4 live trading (broker fills, email approval, scaled deployment).
- Universe construction (T1a/T1b/T1c/T2/T3 + ETFs) — Sprint 0A territory, prerequisite to any cube run.

---

## Cross-references

- `PHASE_1A_BETA_STATUS.md` — run state, per-strategy data references, run-readiness table.
- `CLAUDE.md` — 1A-α owner gate (Sharpe ≥ 0.7 OOS), 11 passing criteria, DEC-426 5-Gate config.
- `CHECKLIST.md` — #67 doc sync per turn, #69 full 13-tier pyramid, #77 source attribution, #85 visible pre-flight, #91 monitoring must act.
- `LEARNINGS.md` — L149 (spec without build), L162 (monitoring without action).
- Feedback memory: `feedback_strategy_x_exit_cell_analysis` (cell-level mandate), `project_no_apriori_strategy_pruning`, `feedback_path_c_min_batch_size`, `feedback_pyramid_full_13_tiers_mandatory`, `feedback_doc_count_drift_must_be_test_pinned`, `feedback_no_write_only_md_files`.
