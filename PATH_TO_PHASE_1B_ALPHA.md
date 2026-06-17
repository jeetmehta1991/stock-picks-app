# Path to Phase 1B-alpha

# Source: Council 14 verdict (5 advisors + chairman synthesis) per owner directive 2026-06-17 "Council this. Be extremely thorough" on Phase 1B-alpha plan + threshold recommendations + metrics integration + dashboard optimizations + R4-R5 delta + R5 fine-tuning. Inputs: PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md (B887 doc-sync state), backtest/results/metrics.py (12 function inventory), backtest/config.py:451-535 (PASSING_CRITERIA threshold stack), dashboard_phase_1a + dashboard_stage_2 + dashboard_sprint0a (catalog), Council 7 binding directive ("R5 -> agents -> papertrade. No changes."), R4 baseline OOS Sharpe 0.419 vs 0.7 gate. Refactored into standalone doc B894 (2026-06-18) per owner directive "Create a new md file" + Executor Council 18 verdict (avoid 4-source drift). Original Council 14/15 batch lineage: B888 (synthesis) + B889 (corrections) + B890+B891 (implementation) + B894 (this doc).

**Status:** B888 synthesis owner-approved 2026-06-17; B889 Council 15 corrections owner-approved 2026-06-17/18; B890-B891 implementation shipped (DEC-611 / DEC-612 / DEC-613 / DEC-614 with 6 pin tests PASS); B894 (2026-06-18) extracted to standalone canonical doc.

**Binding constraints (NOT overridable in this doc):**
- Council 7: "R5 -> agents -> papertrade. No changes." All B888 augmentations are POST-R5 analytical lenses + ablation extraction, NOT gate replacements.
- `feedback_no_a_priori_strategy_pruning`: 218 active strategies; cube measures empirically.
- CLAUDE.md criterion #11 + design philosophy: "Per-regime strategy library: different strategies for different regimes - not universal strategies." A strategy valid in crisis but not bull is deployed only during crisis - this is intentional.
- DEC-426 5-Gate (n>=30, p<0.05 Bonferroni, PSR>=0.95, t>=3.4, R:R>=2.0) per-cell stays canonical.

---

## 1. The 6-Day Path (Tue -> Sun)

| Day | Action | Bottleneck | Cost |
|---|---|---|---|
| Tue (B888 day) | B660 v2 completes; Council 14 chairman verdict surfaced (B888); pre-commit Sharpe-band gate confirmed (B882 still authoritative); owner pre-approves $300 Haiku trigger condition | Owner pre-approval (15 min) | $0 |
| Tue PM -> Wed AM | G3 pyramid + G5 optimizer + #6 fire-bar matrix in sequence (~6-7h overnight; no parallelization to avoid CPU contention with B660 v2) | Compute | $0 |
| Wed | R5 launch on AWS c7a.8xlarge spot 3 instances x 5h = ~$7.80 (B884 instance-type decision) | AWS wall-clock 5-7h | $7.80 |
| Thu AM | Stage 3 winner extraction (`scripts/optimize_strategies_from_cube.py`); B882 decision-tree gate applied; B888 `r5_delta_analyzer.py` runs | **Owner attention (1h)** | $0 |
| Thu PM -> Sat | Phase 1B-alpha Haiku run on Priority-1 (deployment-optimized cells) + AGENT-CANDIDATE tag only; mid-run abort watchdog per DEC-131 lookahead | Compute (~37-40h); Haiku $50-150 | $50-150 |
| Sun | DEC-131 gate: agent_sharpe minus rules_sharpe >= 0.2 net on >=3 combos -> advance to Phase 1B full; or stop | Owner | $0 |

**Single sequential bottleneck:** Thursday AM owner sign-off on B882 Sharpe-band decision tree applied to R5 results.

---

## 2. Threshold Stack (POST-R5 ANALYTICAL LENS, not gate replacement)

**Existing 14-criteria + 3 AUTO-FAIL screens + DEC-426 5-Gate stack remains canonical** (no methodology change per Council 7). B888 adds a parallel **classification lens** for owner-facing winner identification + dashboard surfacing.

### 2.1 Full Threshold Taxonomy (Council 15 First Principles)

**Group A - Trade Distribution Quality (4 params):**

| Param | Value | Measures | Catches | Redundancy |
|---|---|---|---|---|
| `min_win_rate` | 0.45 per-regime | Fraction winning trades | "Fires often, mostly loses" | NOT redundant with PF (WR ignores magnitude) |
| `min_profit_factor` | 1.2 / 1.3 overall | Sum(wins) / Sum(losses) | "Wins small, losses huge" | NOT redundant with WR (PF captures magnitude) |
| `min_expected_value` | 0.0 | Mean per-trade P&L > 0 | Raw-dollar scale floor | Partial overlap with PF; cheap diagnostic |
| `min_win_loss_ratio` | 1.0 | Avg win / avg loss | Fragility shape | Partial overlap with PF; diagnostic |

**Group B - Risk-Adjusted Quality (4 params; NOT mutually redundant):**

| Param | Value | Measures | Why NOT redundant |
|---|---|---|---|
| `min_sharpe_overall` / per-regime | 1.0 / 0.7 | Excess return / total vol | Industry-canonical "decent"; penalizes upside vol |
| `min_sortino_overall` / per-regime | 1.0 / 0.7 | Excess return / DOWNSIDE vol | Correct for R:R>=2.0 skewed dists (Sharpe over-penalizes wins) |
| `min_calmar` | 0.5 | CAGR / max DD | PATH-AWARE (Sharpe is path-blind) |
| `min_deflated_sharpe` (DSR) | 0.95 | Multi-testing-corrected Sharpe | **Anti-overfitting gate** - most important at 39,676-cell denominator |

**Group C - Drawdown & ROI (2 params; B889 unified naming):**

| Param | Value | Surfaced as | Status |
|---|---|---|---|
| `max_drawdown` | 25.0 | `max_drawdown_pct` (writer + cube post-B889) + legacy `max_dd` alias | OK Computed + gated + UNIFIED B889 |
| `min_total_roi` | 0.0 | `total_roi_pct` (writer + cube post-B889) + legacy `total_roi` alias | OK Same |

**Group D - Sample-Size Power (2 params):**

| Param | Value | Why split |
|---|---|---|
| `min_trades` | 100 overall | BUG-31 codification of CLAUDE.md criterion #9 |
| `min_trades_per_regime` | 30 | Per-regime power floor; matches DEC-426 5-Gate min_trades_per_cell |

**Group E - Multiple-Testing & Significance (DEC-426 5-Gate per cell):**

| Gate | Value | Measures |
|---|---|---|
| n >= 30 | Sample size per cell | Statistical power |
| p < 0.05 Bonferroni over 39,676 | Significance after multi-testing | Anti-false-positive |
| PSR >= 0.95 | Probabilistic Sharpe Ratio | Prob(true Sharpe > 0) |
| t-stat >= 3.4 | Robustness | Small-sample correction |
| R:R >= 2.0 | Asymmetric payoff | Deliberate design choice |

**Group F - Per-Regime Verdict (1 param; B891 DEC-611 ratified):**

| Param | Value | Source |
|---|---|---|
| `min_regimes_passing` | **1** | CLAUDE.md criterion #11 canonical; DEC-611 owner-approved B891 (was code drift to 2 - corrected) |

**Group G - Audit Triggers (NOT gates; diagnostic flags):**

| Param | Value | Triggers |
|---|---|---|
| `audit_win_rate_above` | 0.65 | DEC-084 manual look-ahead inspection |
| `audit_profit_factor_above` | 1.5 | Same |

### 2.2 NEW AUTO-FAIL Screens (B890-B891 shipped; DEC-612/613/614)

| Screen | Threshold | Source | Catches |
|---|---|---|---|
| **Chow break-point** | p < 0.05 + post-break Sharpe < 0.3 | Expansionist + Contrarian Council 14 | Dead-strategy false positives (regime-coincidence; strategy died at 2022-06-13 rate-hike pivot, still coasting on pre-break trades) |
| **ADF stationarity** | p < 0.05 (mean-reverting equity curve) - REGIME-CONDITIONAL on mean-reversion strategies only | Expansionist Council 14 | Whip-saw non-compounders for mean-rev strategies |
| **Cost-sensitivity Sharpe** | `sharpe_at_20bps / sharpe_at_0bps >= 0.5` (degradation < 50%) | Built but never gated (Council 14) | Strategies that die under realistic slippage/commission |

**Implementation status (B890-B891):** 3 helper functions added to `metrics.py` (`_eval_cost_sensitivity_gate`, `_eval_chow_gate`, `_eval_adf_gate`); 4 new PASSING_CRITERIA keys added (`min_cost_sensitivity_ratio`, `chow_test_p_max`, `chow_post_break_sharpe_min`, `adf_test_p_max_mean_reversion`); 12-entry `MEAN_REVERSION_STRATEGIES` set for regime-conditional ADF; 5 pin tests passing (`test_batch890_*`).

### 2.3 B888 4-Metric Lens (Soft-Score Layer; NOT a gate replacement)

| Metric | B888 lens threshold | Rationale | Existing gate (unchanged) |
|---|---|---|---|
| **PSR** (Probabilistic Sharpe Ratio) | >= 0.95 with explicit n | Captures Sharpe + sample size + skew + kurtosis in one metric per Bailey-Lopez-de-Prado 2012 | `min_sharpe_overall` 1.0; `min_sharpe_per_regime` 0.7; `min_trades` 100/30 |
| **Calmar** (promoted from deflator to primary lens) | >= **1.0** (was 0.5 deflator) | Drawdown-resilient cells = agent-stable cells per Expansionist Council 14; Phase 1B-alpha agents over-weight recent losses -> drawdowns kill agent confidence loops | `min_calmar` 0.5 (unchanged canonical) |
| **DSR** with confidence interval | DSR > 0 with CI not arbitrary 0.95 | First Principles: DSR is the multiple-testing correction; raw threshold 0.95 + Bonferroni on top = double-counting | `min_deflated_sharpe` 0.95 (unchanged canonical) |
| **Per-regime PASS** | **>= 1** of 4 regimes (DEC-611) | Per CLAUDE.md core principle (per-regime not universal); Council 15 corrected Council 14's "3 of 4" error | `min_regimes_passing` 1 (DEC-611 ratified) |

---

## 3. Best Unique Strategy x Exit Identification (Best-of-26 Collapse + Soft-Score)

**Council 14 unanimous convergence:** 39,676 cells dilutes signal; collapse to deployment-optimized form. **Council 15 clarified:** collapse is EXIT-AXIS ONLY, never strategy-axis (B807 latent-collapse audit empirically forbids strategy-axis collapse - 97.5% phi<0.30 across 4-7 latent-factor hypotheses; 218 strategies are NOT 4-7 latent factors with reskins, they are 218 distinct hypothesis tests).

```python
# Pseudocode for scripts/r5_winner_identifier.py (B888 NEW)
for strategy in ALL_STRATEGIES:                       # 218 strategies
    for regime in REGIMES:                            # 7 regimes
        # Best-of-26 collapse (EXIT AXIS ONLY)
        best_cell = argmax(soft_score(cell) for cell in cells_for(strategy, regime))
        # -> 218 x 7 = 1,526 deployment-optimized cells (vs 39,676 raw)

# Soft-score formula (Expansionist Council 14)
def soft_score(cell):
    return (0.30 * normalized(cell.sharpe)
          + 0.25 * normalized(cell.calmar)
          + 0.20 * normalized(cell.profit_factor)
          + 0.15 * normalized(cell.dsr)
          + 0.10 * (1 - cell.cost_sensitivity))

# Rank by soft-score; emit Priority tiers
P1 = top-N% by soft-score AND passes all AUTO-FAIL screens (Chow + ADF + cost-sensitivity)
P2 = below P1 threshold but per-regime PASS in >=1 regime (DEC-611)
P3 = below P2; excluded from Phase 1B-alpha
```

**Output:** `output_audit/winners_r5_b888.parquet` with columns: `[strategy, regime, exit, soft_score, sharpe, calmar, psr, dsr, chow_pvalue, adf_pvalue, cost_sensitivity, priority_tier, agent_candidate_flag, delta_vs_r4]`.

**Asymmetric value (Expansionist):** soft-score ranking surfaces cells just-below ALL-criteria-pass thresholds (e.g., passes everything except 1 metric by 1pp) - these would die silently under current gate stack. With soft-score, they surface for owner review.

---

## 4. R4 -> R5 Delta Intelligence (FREE Ablation Study)

**Council 14 4-of-5 strongest insight:** R4 + R5 with cumulative B722/B874/B635/B886 changes = the most expensive controlled-ablation study ever assembled. Throwing it away by treating R5 as fresh verdict is throwing away the intelligence.

**B888 NEW script: `scripts/r5_delta_analyzer.py` (to be written before R5 launches).**

For each (strategy x exit x regime) cell present in both R4 and R5:

| Delta condition | Interpretation | Action |
|---|---|---|
| dSharpe >= +0.10 AND attributable to B722-B886 walk | Walk earned its keep | Promote strategy in Priority-1 |
| dSharpe <= -0.10 | Revert candidate; walk overfit | Surface for owner review; potential revert |
| \|dSharpe\| < 0.05 despite gate changes | Cosmetic walk | Document; no action |
| FAIL-overall -> PASS-per-regime flip | Tier-3 regime-specific deployer (NEW edge discovered) | Add to P2 tier (regime-conditional deployment) |

**Aggregation method (First Principles rigor):** per-cluster Kolmogorov-Smirnov test on Sharpe distribution shift across R4 vs R5. Unit of inference = cluster x regime, not raw per-cell (39,676 cell deltas are noise).

**Visualization:** new dashboard tab "R4-R5 Delta" (see section 5).

---

## 5. Dashboard Consolidation (3 -> 1)

**Council 14 First Principles + Outsider:** 3 dashboards fragment by phase rather than by question.

**B888 plan: build `dashboard_stage_4_cube_explorer/` consolidating 4 tabs:**

| Tab | Content | Source |
|---|---|---|
| 1. **Cell Verdict Cube** | Filterable by strategy/exit/regime; soft-score sorted; AUTO-FAIL flags visible; Priority tier badges | r5 trade logs + winners_r5_b888.parquet |
| 2. **R4-R5 Delta** | Per-cell delta-metrics heatmaps; cluster-regime KS test summary; walk-impact attribution | r5_delta_analyzer.py output |
| 3. **Walk-Impact** | Per-batch Stage 4 walk contribution to Sharpe delta (which walks earned their keep) | Delta analyzer aggregated by batch |
| 4. **Phase 1B-alpha Candidate** | AGENT-CANDIDATE vs MECHANICAL-PURE tagging; agent-overlay decision support | soft-score output + manual tagging |

**Deprecation plan:**
- `dashboard_phase_1a/` -- supersede with Cell Verdict Cube tab; archive after B888+5 batches
- `dashboard_stage_2/` -- supersede with EXECUTION_QUEUE + AUDIT_INDEX integration; archive after B888+5 batches
- `dashboard_sprint0a/` -- convert to static JSON reference data (no JS UI); not user-facing

---

## 6. metrics.py Integration (Sleeping Unicorns)

**Council 14 Expansionist + Contrarian:** metrics.py computes 12 functions; PASSING_CRITERIA reads 6. The 6 unused are the highest-leverage diagnostic gates. B890-B891 wired the top-3 (cost-sensitivity + Chow + ADF) as AUTO-FAIL screens; B891+ promotes the rest.

### 6.1 GATED (7 functions; ALL CORRECT)
`_sharpe`, `_sharpe_daily`, `_profit_factor`, `_max_drawdown`, `_calmar`, `_sortino_ratio`, `_deflated_sharpe`.

### 6.2 UNGATED (8 functions) + Promotion Plan

| Function | Current | Promote? | Wire cost | When | Action |
|---|---|---|---|---|---|
| `_cost_sensitivity_sharpe` | columns exist | **YES - HIGH** | ~10 lines | **B890 SHIPPED** | Gate: `sharpe_at_20bps / sharpe_at_0bps >= 0.5` |
| `_chow_test` | telemetry only | **YES - HIGH** | ~15 lines | **B890 SHIPPED** | Gate: structural break + post-break Sharpe < 0.3 -> FAIL |
| `_adf_test` | telemetry only | **YES - REGIME-COND** | ~15 lines | **B890 SHIPPED** | Gate for mean-rev strategies only (non-stationary equity = no edge) |
| `_kelly_criterion` | column exists | Sizing not gate | ~20 lines | B895+ | Stage 3 position-sizing input; hard FAIL on negative Kelly |
| `_event_window_breakdown` | columns exist | MEDIUM | ~10 lines | B895+ | Dashboard surface; advisory |
| `_event_conditional_win_rate` | columns exist | MEDIUM | ~10 lines | B895+ | Same |
| `_time_in_market_metrics` | column exists | LOW | ~5 lines | B895+ | Capital efficiency dashboard column |
| `_confidence_interval_95` | column exists | MEDIUM | ~10 lines | B895+ | Gate `ci_low > 0.50` for CI-aware WR |

---

## 7. Post-Stage-4 Target (Honest)

**Original Stage 2 BUILD PLAN target:** ">=10 Priority-1 combos identified -> Phase 1B-alpha."

**B888 corrected target (per Council 14 First Principles):** "By Sunday, produce a ranked list of <=50 deployment-optimized cells with R4-R5 delta-verified edge improvement and pass the Chow+ADF AUTO-FAIL screens."

If subset is **<30 cells** -> project's "218 strategies have edge" premise is empirically falsified. Response: fewer strategies, not more agents. Honest stop-gate.

If subset is **30-50 cells with verified delta improvement** -> Phase 1B-alpha launches restricted to AGENT-CANDIDATE-tagged cells only (per Expansionist per-cell triage), ~60% Haiku budget savings vs blanket P1 set.

---

## 8. Scripts to Build (B888 + Following Batches)

| Script | When | Effort | Status |
|---|---|---|---|
| `scripts/r5_delta_analyzer.py` | NOW (parallel to B660 v2) | ~2h Claude | B888 priority |
| `scripts/r5_winner_identifier.py` (soft-score + AUTO-FAIL screens) | Pre-R5 (or by Thursday AM) | ~3h Claude | B888-B889 |
| `scripts/eval_r5_sharpe_band.py` (B882 decision tree evaluator) | Pre-R5 | ~1h Claude | B889 |
| `scripts/dec131_mid_run_watchdog.py` (1B-alpha abort if lookahead detected) | Pre-1B-alpha | ~1h Claude | B890 |
| `dashboard_stage_4_cube_explorer/` build | Post-R5 | ~4-6h Claude | B891 |

**Total Claude effort:** ~11-13h across B888-B891. None block R5 launch except `r5_delta_analyzer.py` (which is built before R5 lands).

---

## 9. What Stays Vs What Changes

| Element | Status |
|---|---|
| Council 7 "R5 -> agents -> papertrade. No changes." directive | **UNCHANGED** |
| PASSING_CRITERIA 14-criteria + 3 AUTO-FAIL + DEC-426 5-Gate canonical | **UNCHANGED** (no methodology shift) |
| 218 active strategies; no a-priori cull (`feedback_no_a_priori_strategy_pruning`) | **UNCHANGED** |
| DEC-426 5-Gate (n>=30, p<0.05 Bonferroni, PSR>=0.95, t>=3.4, R:R>=2.0) | **UNCHANGED** |
| Phase 1B-alpha 11-agent pipeline + $300 Haiku budget | **UNCHANGED** |
| DEC-131 gate (agent_sharpe minus rules_sharpe >= 0.2 on >=3 combos) | **UNCHANGED** |
| `min_regimes_passing = 1` (CLAUDE.md canonical; was code drift to 2) | **B891 RATIFIED via DEC-611** |
| 3 AUTO-FAIL screens (Chow + ADF + cost-sensitivity) | **B890 SHIPPED via DEC-612/613/614** |
| **B888 lens** (4-metric + AUTO-FAIL screens applied to R5 OUTPUT) | **NEW** -- analytical only, no gate replacement |
| **R4-R5 delta analyzer** | **NEW** -- free ablation extraction |
| **Soft-score ranking + best-of-26 collapse** (EXIT-AXIS ONLY) | **NEW** -- winner identification methodology |
| **Consolidated dashboard** | **NEW** -- 3 -> 1 over B891+ |

---

## 10. Council 14 Diagnostic (Honest Risk Surface)

**Contrarian Council 14 dissent (preserved for honesty):**
- "R4 0.419 OOS came from researcher running 800+ batches against same holdout. True Sharpe possibly below 0.419 or negative."
- "39,676 cells x ~140 walk-mutations x 800 batches ~= 4.4M researcher DoF. At this trial count, Sharpe 1.0 overall = random noise. Honest threshold ~1.8-2.2."
- "Stage 4 walks were optimization round 1 against corrupted oracle. Round 2 needs clean OOS slice (2026-Q2 forward, sealed) before R5 means anything."

**Owner's binding response (Council 7):** "R5 -> agents -> papertrade. No changes." -- overrules the methodology-shift concern. B888 honors directive while extracting maximum delta-intelligence + lens-classification value from the R5 output.

**Honest fallback if R5 OOS Sharpe < 0.5:** B882 Sharpe-band decision tree triggers STOP. Defer Phase 1B-alpha. Re-architect via clean post-2026 forward-test window (Contrarian's prescription becomes actionable post-failure).

---

## 11. Cross-References

- **R5 decision tree:** [`output_audit/r5_precommit_decision_tree.md`](output_audit/r5_precommit_decision_tree.md) (B882)
- **R5 triage audit:** [`output_audit/r5_triage_audit_2026-06-17.md`](output_audit/r5_triage_audit_2026-06-17.md) (B883)
- **Day 1 progress:** [`output_audit/r5_day1_progress_2026-06-17.md`](output_audit/r5_day1_progress_2026-06-17.md) (B885)
- **Phase 1A-beta cube workflow (locked):** [`PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md`](PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md)
- **Stage 2/3/4 build plan (parent):** [`STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md`](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md) (section 10 collapsed to pointer per B894)
- **Build plan progress tracker:** [`BUILD_PLAN_PROGRESS.md`](BUILD_PLAN_PROGRESS.md)
- **Canonical project plan:** [`PROJECT_PLAN.md`](PROJECT_PLAN.md) + [`DETAILED_PROJECT_PLAN.md`](DETAILED_PROJECT_PLAN.md)
- **Decision audit:** AUDIT.md DEC-611 / DEC-612 / DEC-613 / DEC-614 (B890+B891)
- **Pin tests:** `backtest/tests/test_unit.py::test_batch890_*` (5 tests; ALL PASS)

---

## 12. Batch Lineage

| Batch | Date | Action |
|---|---|---|
| B882 | 2026-06-17 | Pre-commit Sharpe-band decision tree locked |
| B883 | 2026-06-17 | R5 triage audit (11 items runtime-probed) |
| B884 | 2026-06-17 | AWS c7a.8xlarge spot $7.80/run decided (G4 cheapest) |
| B885 | 2026-06-17 | Day 1 triage progress; G1 SHA pin + G2 strategy count assert + B660 v2 launch + #5 ghost finding |
| B886 | 2026-06-17 | Stage 5 SWAP #73-75 applied per B834 R4 cube verdicts |
| B887 | 2026-06-17 | Doc-sync STRATEGY_ROSTER + Phase 1A-beta cube workflow |
| **B888** | **2026-06-17** | **Council 14 synthesis: Path to Phase 1B-alpha (THIS PLAN)** |
| **B889** | **2026-06-17/18** | **Council 15 corrections (5 items: #1 regime gate 3->1, #2 max DD diagnosed, #3 collapse exit-axis-only, #4 lens framing, #5 metrics wiring plan)** |
| **B890** | **2026-06-18** | **Implementation: DEC-612 cost-sensitivity + DEC-613 Chow + DEC-614 ADF AUTO-FAIL gates; MEAN_REVERSION_STRATEGIES taxonomy; 5 pin tests** |
| **B891** | **2026-06-18** | **DEC-611 `min_regimes_passing` 2->1 ratified per CLAUDE.md canonical; banner table + workflow doc + AUDIT updates** |
| B892 | 2026-06-18 | Doc-hygiene sweep (STRATEGY_ROSTER generator fix + smoke archive + flag table + CHECKLIST #110) |
| B893 | 2026-06-18 | Archive 3 owner-approved stale .md files |
| **B894** | **2026-06-18** | **THIS DOC created (refactored from STAGE_2 section 10 standalone per owner directive + Executor Council 18); CHECKLIST #111 freshness audit codified; STRATEGY_ROSTER stale-column scrub option (A)** |
