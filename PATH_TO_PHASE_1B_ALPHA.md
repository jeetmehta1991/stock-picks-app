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
| B895-B917 | 2026-06-18/19 | R4 medium-risk strategy addressal + B912 producer probe + B913 micropilot 0-fires + B914 cohort audit anti-predictive + B915 walk template / Walk 1 of 6 / Council 35 DIAGNOSE-BEFORE-DISPOSE / B916 6-probes / B917 coverage map + stratified-sample retest |
| **B918** | **2026-06-19** | **PRODUCTION BUG screener.py:7979 `inst.get("new_pos")` -> `"new_positions"` (commit 82290e2c00 2026-05-25; 25 days in prod; affected 7 strategies incl. R4 May 31); owner-approved fix (a); regression test `test_b918_screener_institutional_new_positions_wiring`; pyramid GREEN (699 unit + 149 integration)** |
| **B919** | **2026-06-19** | **Post-fix micropilot still 0 fires -> SURFACED 4th MISS PATTERN: `measure_fire_count.py` lines 443-448 TIER 2 architectural deferral (~44 strategies untested by canonical tool); R4's screen_instrument path DOES exercise line 7979 fix (real R5 cube unblocked); validates Council 36 A1 wiring audit + Council 37 Outsider pre-flight self-test** |
| **B920** | **2026-06-19** | **Council 38 5-advisor 14-question comprehensive workflow synthesis + Council 39 5-advisor bug-catching methodology synthesis (THIS SECTION 13 added)** |

---

## 13. R5 Comprehensive Pre-Launch Workflow (Council 38 + Council 39 Synthesis)

# Source: B920 Council 38 (Contrarian + First Principles + Executor + Outsider + Expansionist/Quant) + Council 39 (5-advisor bug-catching panel) per owner directive 2026-06-19 ("Council 36 not comprehensive enough... we are not stuck in iterations over and over again. The project has been a mess till now"). Owner-approved Option (B) Synthesis Council 38 Path. Section additions per "Document everything comprehensively to ensure reference and compliance. Discipline to be enforced strictly! No exceptions."

**Binding Discipline (NOT overridable):**
- `feedback_mandatory_council_per_turn` (2026-06-19) — council BEFORE recommendations, not after; CHECKLIST per #110 enforcement mandatory
- `feedback_no_surface_level_audits` (2026-06-19) — every audit step end-to-end (source -> producer -> binding -> strategy -> engine -> output)
- `feedback_no_a_priori_strategy_pruning` (2026-05-25) — no deletions; DORMANT routing bucket preserves optionality
- Council 38 Outsider warning: "36 councils -> 0 shipped R5. Comprehensiveness IS the disease. Hard moratorium on workflow redesign until R5 ships."

### 13.1 The Synthesis — Three-Stream Architecture (replaces Council 36's 4 phases)

Council 36's linear 4-phase A->B->C->D was rejected by all 5 Council 38 advisors. The reformulation:

**Stream E (Evidence)** — deterministic scripts producing per-strategy `dossier.json` with 19 sections. No Claude in the loop. Outputs to content-addressed `evidence_store/<hash>/<section>.parquet`. Reproducible via `seed_registry.json`.

**Stream D (Decision)** — Claude reads dossiers in batches of 5 per `feedback_path_c_min_batch_size`, applies CHECKLIST, surfaces per-strategy recommendations to owner. Owner approves; code mutates.

**Stream V (Verification)** — pyramid runs per Stream-E-generator (one-time) + per Stream-D-batch (pre-commit). NOT per dossier section (would explode to 3,052 runs).

**Why three streams replace four phases:** R5 launch is not a phase; it is the moment Stream E reports "0 strategies have open decision items + pyramid green + Sharpe-delta projection positive" across the dossier set.

### 13.2 The 7 Phases (Executor's Operational Decomposition)

| Phase | Name | Runs | Owner gate file | Est hrs |
|---|---|---|---|---|
| **P0** | Platform spine + wiring + schema pins | `make r5-p0` | `output_audit/r5_p0_blockers.md` | 4-6 |
| **P1** | Universe diagnostics (Stream E fan-out, parallel 8-way) | `make r5-p1` | `output_audit/r5_p1_summary.md` | 8-12 |
| **P2** | No-delete reclassification (STRATEGY_STATUS enum apply) — **ABSORBS Type 2 Track A consolidation: redundancy_phi_matrix built on R4 cube data; cluster representatives stay ACTIVE; reskins flip to STRATEGY_STATUS=DEPRECATED. Honors B705 (`feedback_no_prior_edge_consolidate_before_tune`).** | `make r5-p2` | `output_audit/r5_p2_status_proposed.csv` | 6-8 |
| **P3** | Bug-batch fixes (autonomous fix loop, max 50 iterations) | `make r5-p3` | `output_audit/r5_p3_fix_log.md` | 16-24 |
| **P4** | Per-strategy walks (sampled; 30 stratified by cluster) | `make r5-p4-sample` | `output_audit/r5_p4_walk_outputs.parquet` | 20-30 |
| **P5** | R5 dry-run (1% sample cube validates pipeline) | `make r5-p5-dryrun` | `output_audit/r5_p5_dryrun_metrics.md` | 4-8 |
| **P6** | Full R5 launch on AWS (5,694 cells) | `make r5-p6-launch` | `output_r5_final/` | 60-90 (compute) |
| **P6.5** | Parameter refinement (Type 1 exit-param + Type 2 Track B gate-loosening on survivors) — see §13.15 | `make r5-p65-refine` | `output_audit/r5_p65_refinement_log.md` | 6-10 |
| **P7** | Stage 3 winner extraction (`scripts/optimize_strategies_from_cube.py`) | `make r5-p7-extract` | `output_audit/r5_p7_winners.md` | 2-4 |

**Total: ~126-192 wall-clock hours; ~32-44 owner-attention hours** (incl. P6.5 + P7).

**Makefile-orchestrated (`Makefile.r5` at repo root):** `make -j8` gives free parallelism; phases idempotent; owner can run individual phases.

### 13.3 19 Dossier Sections (Stream E Per-Strategy Output) — NO SURFACE-LEVEL

Each section traces END-TO-END (source -> producer -> binding -> strategy -> engine -> output). Surface-level greps + docstring reads are STARTING POINTS, not conclusions.

| # | Section | Depth requirement |
|---|---|---|
| 1 | Wiring trace via coverage | `coverage run` over canonical R4 backtest; assert strategy fn appears in `coverage.json` line-execution. NOT grep. |
| 2 | Gate-stacking + per-gate fire-rate | RUNTIME measurement from R4 trade_log (NOT a-priori estimator; estimator missed B660 by order of magnitude) |
| 3 | Inverse pair | EMPIRICAL probe (mechanical inverse, measure fire-count + crude WR); NOT literature speculation |
| 4 | Redundancy phi-correlation matrix | Pairwise trade-day Jaccard across 219 strategies |
| 5 | Regime affinity lineage from git log | Trace every regime-affinity addition/deletion to batch + rationale |
| 6 | Producer source extract + STATE/EVENT classification | AST scan; classify each signal; reject docstrings that overclaim for slow STATE |
| 7 | Temporal coverage probe | Per-year-per-strategy fire count (NOT mean — strategies firing 100x 2020 then 0 2021-2026 pass mean but are dead) |
| 8 | Data-source asymmetry tag | 13F long-only (B611), insider buy/sell asymmetry, short-interest contrarian — empirical not mechanical |
| 9 | R4 cube metrics (all 7 regimes) | **TWO-TRACK per B934 Council 45:** (a) R4-included strategies (~102; in `output_batch395_final/`): Sharpe + Sortino + Calmar + PF + max_DD + ROI + WR with bootstrap 90% CI. (b) Post-R4 additions (~117): null + `r4_status="post_r4_addition"` + `evidence_source="section_9b"`. Per Quant: point estimates alone are coin flips. |
| **9b** | **Pre-cube evidence (B934 Council 45 owner-approved addition)** | **For post-R4 additions (~117 strategies):** B907/B660 fire-count projection + Stage 4 walk batch reference per B883 ledger + EXPLORATORY/DORMANT/MEASUREMENT_DISPUTED status + attribution narrative per Section 13.7 gate #7. Defeats the laundering risk of "Section 9 NULL for 117"; makes 53% post-R4 gap auditable. **NEW dossier field:** `r5_inclusion_criterion ∈ {r4_metrics_passed, pre_cube_evidence_sufficient, deferred}`. |
| 10 | Cost-sensitivity ratio | DEC-612 `sharpe_at_20bps / sharpe_at_0bps >= 0.5` (MULTIPLICATIVE GATE per Quant; NOT soft-score ingredient) |
| 11 | Chow break point | DEC-613 (p<0.05 + post-break Sharpe<0.3 = dead-strategy false positive) |
| 12 | ADF p-value | DEC-614 regime-conditional on `MEAN_REVERSION_STRATEGIES` |
| 13 | Exit-axis best-26 vector + dispersion | Best-of-26 collapse + `iqr(sharpe_26)/median <= 1.5` dispersion gate (15th passing criterion); calibrate threshold from null distribution per Lo 2002 |
| 14 | Returns autocorrelation correction (Lo 2002) | Positive autocorr inflates Sharpe; correction applied; corrected-Sharpe must re-pass |
| 15 | Exit profitability fraction | `count(sharpe_exit > 0) / 26 >= 0.4` (>=40% of exits profitable; catches 1-of-26 lottery winners) |
| 16 | Negative-control canary status | 5 null strategies injected pre-Stream-E; framework must identify them; if not, framework miscalibrated |
| 17 | Soft-score weight calibration via null | Weights derived from null-distribution variance, NOT hand-tuned (Quant); revisit at Phase 1C as Bayesian posterior |
| 18 | Per-regime Sharpe dispersion | Strategy passing in 1 regime PF=2.0 + failing in 6 PF=0.5 has Simpson's-paradox risk in pooled metrics |
| 19 | Closest-passing-neighbor + family + cluster_id | Hierarchical clustering on sharpe-signature + signal-overlap + regime-bias |

### 13.4 6 DECs to Surface (Pre-R5)

| DEC | Description | Source |
|---|---|---|
| **DEC #1** | Soft-score reweight to 0.35/0.30/0.23/0.12 + DSR/cost-sens promoted from soft-ingredients to MULTIPLICATIVE GATES | First Principles + Quant |
| **DEC #2** | Dispersion gate `iqr(sharpe_26)/median <= 1.5` (15th passing criterion); calibrated from null-distribution | Executor + Quant |
| **DEC #3** | Coverage-based wiring definition (`coverage run` not grep) | Executor + First Principles |
| **DEC #4** | OOS seal protocol: 2020-2023 IS / 2024-2026 OOS; hash posted to AUDIT.md before any Stream D; roster freeze; post-seal-trial counting | Executor + Quant + First Principles |
| **DEC #5** | DSR N=5,694 specification (219 strategies x 26 exits, NOT 218; regime conditional not search) — Council 38 single biggest methodology hole. **B958 AMENDMENT (Council 63):** Phase 6.5 trial budget pre-registered (180 trials = 120 Type 1 + 60 Type 2 Track B); **N_effective = 5,874** for DSR computation post-P6.5. B957 retrospective audit measured walk-era contamination at 1.04x (negligible); pre-registration applies only forward. | Quant |
| **DEC #6** | PSR small-N companion gate (Bailey-Lopez de Prado 2012) — PSR per-strategy + DSR on family | Quant |

### 13.5 STRATEGY_STATUS Enum (No-Delete Enforcement)

```python
class StrategyStatus(str, Enum):
    ACTIVE = "active"                            # default; cube runs
    EXPLORATORY = "exploratory"                  # B652 marker; cube runs; flagged in dashboard
    NON_WINNER = "non_winner"                    # cube runs; flagged is_winner=False post-dedup
    DORMANT = "dormant"                          # cube SKIPS; preserves optionality
    DISABLED_MISSING_PRODUCER = "disabled_missing_producer"  # producer absent
    DEPRECATED = "deprecated"                    # RESERVED; owner-explicit-DEC-only
```

**Invariants enforced via pytest:**
- DORMANT requires owner-explicit DEC reactivation; 12-month auto-review timer surfaces re-walk batch
- DEPRECATED requires entry in `DEPRECATION_LEDGER.md` with owner-signed B-tag
- `STRATEGIES_DELETED_R5_ROUND = set()` always empty (asserted in pyramid)

### 13.6 OOS Seal Protocol (DEC #4)

| Step | Action |
|---|---|
| 1 | Freeze IS = 2020-2023 / OOS = 2024-2026 split before any Stream D batch |
| 2 | Hash OOS slice (parquet content hash) + post to AUDIT.md with timestamp |
| 3 | Stream E redacts 2024-2026 rows from dossier metrics until seal opens; Claude literally cannot see OOS data |
| 4 | Any post-seal roster change counted as new search trial in DSR N |
| 5 | OOS opens ONCE at R5 cube launch; Sharpe-delta measured (R5_OOS - R4_OOS), NOT (R5_full - R4_full) |
| 6 | Quant nuance: roster ITSELF was constructed using post-2024 information (B709); mitigation = roster freeze as new trial |

### 13.7 R5 Launch Gates (15 Boolean Conditions; Owner Reviews Gate Report)

1. `len(dossiers) == 219`
2. All strategies: `dossier.wiring_trace.coverage_hit == True`
3. All strategies: `dossier.data_consumption.path in {A, C}` (no Path-B/D unresolved)
4. All strategies: `dossier.inverse_pair.status in {exists, owner_waived, structurally_asymmetric}`
5. All strategies: `dossier.fire_count.projected_per_year >= 30 OR status == EXPLORATORY OR status == DORMANT`
6. All strategies: `dossier.gate_stacking_check == passed`
7. All strategies: `dossier.r4_to_r5_changes.attribution_documented == True`
8. `OOS_slice.integrity == sealed` (2024-2026 untouched since seal date)
9. `pyramid.full_13_tier == green` per `feedback_pyramid_full_13_tiers_mandatory`
10. `EXECUTION_QUEUE.open_items_blocking_r5 == 0`
11. **Stream V pyramid green on every Stream E generator** (Executor)
12. **OOS seal hash posted >=24h pre-Stream-D first batch** (Executor)
13. **PSR per-strategy > 0.95** (Quant)
14. **`seed_registry.json` published + Stream V reproduced 5 random strategies bit-identically** (Quant)
15. **Planted-bug canary caught by walk methodology** (Council 39 — owner injects bug Claude-blind; if walk doesn't catch it, walk methodology is theater)

**P6.5 ENTRY GATES (added by B958 Council 63):**

16. `r5_trial_log.json` committed to repo (P6 outputs frozen)
17. `oos_q2_plus_seal_hash` recorded in AUDIT.md (2026-Q2+ slice carved out + hash-pinned; held out for Phase 6.5)
18. `phase_6_5_trial_budget_remaining == 180` at P6 completion (budget unspent until P6.5 launches)
19. Council 7 reset DEC-PHASE-6.5-RESET (see §13.16) owner-countersigned
20. P6.5 trial classification pre-registered (which Type 1 sweeps + which Type 2 Track B qualifiers, before P6.5 fires any cell)

### 13.8 Honest R5 Targets (Factor-Zoo Base-Rate Anchored)

| Metric | Council 38 target | Anchor |
|---|---|---|
| Overall PASS strategies | **25-40** (NOT 70 — sales-pitch number) | McLean-Pontiff 2016 factor zoo ~10-18% survival |
| Per-regime PASS strategies | 100-140 (NOT 180) | Same anchor |
| Unique winners post-cluster-dedup | 30-60 | Cluster-derived |
| CORE portfolio (60% capital) | ~30 strategies | Intersection of 5 rankings |
| EDGE portfolio (25% capital) | ~30 strategies | Specialist metrics (CVaR_5, kelly-fraction-adjusted-Sharpe, event-window-conditional) |
| DIVERSIFY portfolio (15% capital) | ~15 strategies | Low correlation to CORE on trade-day overlap |
| Median Sharpe across 219 | >= 0.40 | R4 baseline ~0.25 |
| DSR >= 0.95 winners | >= 15 | Up from ~5 in R4 |
| Cost-sens >= 0.5 winners | >= 25 of the 30-60 | New multiplicative gate per DEC #1 |

**If miss >= 3 targets:** R5 INSUFFICIENT verdict; owner-gated diagnostic loop reopens P1-P4. R5 result REPLACES P0 platform validation; verdict feeds Council 40.

#### 13.8.1 PASS Criteria Detail (Concrete Threshold Stack)

**OVERALL PASS** = strategy clears ALL 14 canonical hard gates + ALL 9 AUTO-FAIL screens. **Per-regime PASS** = strategy passes per-regime thresholds in >=1 regime per DEC-611.

**Group A — Trade Distribution Quality (4 hard gates):**

| # | Criterion | Overall threshold | Per-regime threshold |
|---|---|---|---|
| 1 | win_rate | >=0.55 (HV sectors 0.50; defensive 0.58) | >=0.45 |
| 2 | profit_factor | >=1.3 | >=1.2 |
| 3 | expected_value | >0 | >0 |
| 4 | win_loss_ratio | >=1.0 | >=1.0 |

**Group B — Risk-Adjusted Quality (4 hard gates; NOT mutually redundant):**

| # | Criterion | Overall | Per-regime | Why not redundant |
|---|---|---|---|---|
| 5 | Sharpe ratio | >=1.0 | >=0.7 | Industry-canonical "decent"; penalizes upside vol too |
| 6 | Sortino ratio | >=1.0 | >=0.7 | Correct for R:R>=2.0 skewed dists (Sharpe over-penalizes wins) |
| 7 | Calmar (CAGR/maxDD) | >=0.5 | >=0.5 | PATH-AWARE (Sharpe is path-blind) |
| 8 | DSR (Deflated Sharpe) | >=0.95 | >=0.95 | Multi-testing-corrected; ANTI-OVERFITTING gate |

**Group C — Drawdown & ROI (2 hard gates):**

| # | Criterion | Threshold |
|---|---|---|
| 9 | max_drawdown | <=25% (HV 25%; defensive 20%) |
| 10 | total_roi | >0% |

**Group D — Sample-Size Power (1 hard gate; 2 sub-thresholds):**

| # | Criterion | Threshold |
|---|---|---|
| 11 | min_trades | >=100 overall / >=30 per-regime (matches DEC-426 5-Gate min_trades_per_cell) |

**Group F — Per-Regime Verdict (1 hard gate; DEC-611 ratified):**

| # | Criterion | Threshold |
|---|---|---|
| 12 | min_regimes_passing | >=1 of 7 regimes (CLAUDE.md canonical; was code drift to 2; DEC-611 reverted) |

**Group H — Smart Money + Macro (2 hard gates):**

| # | Criterion | Threshold |
|---|---|---|
| 13 | smart_money_lift | >=3pp WR diff (with vs without smart-money signal) |
| 14 | macro_correlation | >=5pp WR diff (favorable vs unfavorable macro regime) |

**AUTO-FAIL Screens (9 screens; 3 shipped B890-B891 + 6 NEW Council 38):**

| # | Screen | Threshold | Status |
|---|---|---|---|
| AF1 | Cost-sensitivity (DEC-612) | `sharpe_at_20bps / sharpe_at_0bps >= 0.5` | B890 SHIPPED |
| AF2 | Chow break-point (DEC-613) | p>=0.05 OR post-break Sharpe>=0.3 | B890 SHIPPED |
| AF3 | ADF stationarity (DEC-614, mean-rev only) | p>=0.10 | B890 SHIPPED |
| AF4 | DSR multiplicative gate (Council 38 DEC #1) | DSR>=0.95 (was soft-score ingredient; now hard gate) | DEC #1 surface pending |
| AF5 | Cost-sens multiplicative gate (Council 38 DEC #1) | cost_sens>=0.5 (was soft-score; now hard gate) | DEC #1 surface pending |
| AF6 | Dispersion gate (Council 38 DEC #2) | `iqr(sharpe_26)/median<=1.5`; null-distribution calibrated | DEC #2 surface pending |
| AF7 | PSR per-strategy (Council 38 DEC #6) | PSR>0.95 small-N companion to DSR | DEC #6 surface pending |
| AF8 | Exit profitability fraction (Council 38 dossier #15) | `count(sharpe_exit>0)/26 >= 0.4` (>=40% exits profitable) | P0 build pending |
| AF9 | Negative-control canary (Council 38 dossier #16) | Strategy NOT among 5 injected nulls | P0 build pending |

**Target rationale (factor-zoo base rate anchored; per Quant + Outsider):**

- McLean-Pontiff 2016: of ~400 published factors, ~30-50 survive proper OOS = **~10-13% survival**
- For 219 strategies hand-selected from literature (not random): **~15-20% survival -> 33-44 overall PASS**
- **25-40 is honest target.** 70 was sales-pitch from Council 36; rejected by Council 38
- Per-regime PASS broader: 100-140 of 219 (~46-64%)

#### 13.8.2 CORE / EDGE / DIVERSIFY Portfolio Architecture

**Per Council 38 Expansionist advisor.** Purpose: Phase 1B-alpha agents specialize -> 3 portfolios -> 3 agent profiles -> 3 reward functions -> 3 simultaneous Phase 1B-alpha launches.

**CORE Portfolio (~30 strategies; 60% capital):**

| Property | Value |
|---|---|
| Definition | Intersection of all 5 soft-score rankings (Sharpe-ranked + Calmar-ranked + PF-ranked + DSR-ranked + cost-sens-ranked) |
| Selection criteria | Top quartile on ALL 5 rankings simultaneously |
| Characteristic | Highest individual conviction; robust across metrics |
| Agent role | "Consensus alpha agents" - Phase 1B-alpha validates lift >= +0.2 Sharpe over rules-baseline (per DEC-131) |
| Example | Strategy with Sharpe=1.4, Calmar=0.8, PF=1.6, DSR=0.97, cost_sens=0.7 passes ALL 5 rankings in top quartile |

**EDGE Portfolio (~30 strategies; 25% capital):**

| Property | Value |
|---|---|
| Definition | Top performers on SPECIALIST metrics that CORE rankings don't see |
| Specialist metrics | CVaR_5 (5% Conditional VaR), Kelly-fraction-adjusted Sharpe (sizing-aware), event-window-conditional Sharpe (event-driven), time-in-market-adjusted return (capital efficiency) |
| Characteristic | STRUCTURAL diversifiers; bring DIFFERENT alpha than CORE |
| Agent role | "Specialist alpha agents" - trained to recognize event-window patterns + tail-risk shapes |
| Example | PEAD strategy with mediocre overall Sharpe=0.6 (fails CORE) BUT event-window-conditional Sharpe=2.5 (top EDGE); fires only after positive earnings surprises |

**DIVERSIFY Portfolio (~15 strategies; 15% capital):**

| Property | Value |
|---|---|
| Definition | Selected by LOW CORRELATION to CORE on trade-day overlap (Jaccard<0.3), regardless of absolute soft-score |
| Selection algorithm | `for strategy in (ALL_PASS - CORE - EDGE): overlap = jaccard(strategy.trade_days, CORE.trade_days); if overlap < 0.3 and strategy.sharpe > 0.5: DIVERSIFY.add(strategy)` then top-15 by lowest overlap |
| Characteristic | Reduce portfolio variance through ORTHOGONALITY; individually lower Sharpe but improve portfolio Sharpe via decorrelation |
| Agent role | "Portfolio construction overlay agents" - variance minimization at portfolio level |
| Example | Bear-regime mean-reversion strategy with Sharpe=0.7 (would fail CORE) BUT trades on DIFFERENT days than CORE (jaccard=0.15) - reduces portfolio drawdown during bull-regime corrections |

**Failure handling per portfolio:**

| Portfolio | Min size to deploy | If miss | Capital reallocation |
|---|---|---|---|
| CORE | >=15 | If <15: project's "edge premise" failed -> STOP gate | Defer Phase 1B-alpha |
| EDGE | >=10 | If <10: specialist metrics not surfacing edge -> deploy as CORE supplement | EDGE -> CORE (85% capital) |
| DIVERSIFY | >=5 | If <5: portfolio decorrelation impossible -> deploy CORE+EDGE only | DIVERSIFY -> CORE+EDGE (100% capital) |

**Total deployment: 75 strategies** (30 CORE + 30 EDGE + 15 DIVERSIFY) as subset of the 30-60 unique winners post-cluster-dedup (Section 13.8). Remaining winners (15-30 not selected) become AGENT-CANDIDATE pool for Phase 1B-alpha decision-support overlay.

**Why three portfolios (Expansionist rationale):**

| Aspect | CORE | EDGE | DIVERSIFY |
|---|---|---|---|
| Selection criteria | Intersection of 5 rankings | Specialist metrics | Low correlation to CORE |
| Conviction | Highest individual | High specialist | Lower individual; high portfolio |
| Diversification | Cross-metric | Cross-domain | Cross-trade-day |
| Agent profile | Consensus | Specialist | Portfolio construction |
| Capital allocation | 60% | 25% | 15% |
| Phase 1B-alpha reward function | Consensus Sharpe-lift | Event-window Sharpe-lift | Portfolio variance reduction |

### 13.9 Bug-Catching Framework (Council 39 5-Advisor Synthesis)

**Owner directive 2026-06-19:** "Bug catching overview is still too high level. Restricting to 4 recent gaps; producer and consumption bugs may still get missed. Need to address everything."

**Council 39 critical blind spot (all 5 advisors converged):** Claude is BOTH bug-injector AND self-grader. Framework must include INDEPENDENT verifier — owner-runnable diagnostic CLI + planted-bug canary.

#### 13.9.1 The Single Highest-Leverage Architectural Fix: Engine Path Unification

**Problem:** `backtest.py::screen_instrument` and `scripts/measure_fire_count.py` are divergent paths; B919 surfaced TIER 2 deferral. The dual-engine path IS the bug factory.

**Fix (Week 1 priority):**
- Extract `load_signals_for_ticker()` into `backtest/data/signal_loader.py` (canonical single entry path)
- Both `backtest.py::screen_instrument` and `measure_fire_count.py` import from it
- `backtest/tests/test_engine_parity.py` asserts both paths produce identical fire-counts on 5T x 20-date fixture
- Closes B919 (TIER 2 deferral) STRUCTURALLY; ~44 TIER 2-dependent strategies become testable

#### 13.9.2 Bug-Catching Tier 0 Mechanisms (Week 1 — Eliminate-at-Source)

| Mechanism | Closes | Day |
|---|---|---|
| Canonical `signal_loader.py` | B919 TIER 2 + B901 SMC class | Wed |
| YAML signal-key registry + AST pre-commit check | B918 dict-key typo class | Mon |
| Pre-push fire-count smoke on changed strategies | B913 gate-stacking class | Tue |
| Inverse-roster diff bot + walk template requires MEASURED fire-count | B915 Walk 1 missing-inverse class | Thu |

#### 13.9.3 Bug-Catching Tier 1 (Week 2 — Invariant Runtime + Independent Reviewer)

- Codify 20-invariant manifest in `backtest/invariants/manifest.yaml`
- `backtest/invariants/runtime.py` asserts invariants at engine startup
- Owner-runnable diagnostic CLI: `python scripts/probe.py --invariant E1|C1|C6|C4|C5` (deterministic, no Claude interpretation)
- Planted-bug canary: owner injects 1 silent bug into a producer (Claude-blind); Stage 4 walk must catch; if not, walk methodology is theater (R5 gate #15 above)

#### 13.9.4 Bug-Class Taxonomy (Council 39 Enumeration; 75+ classes)

**Producer-side (~25 classes):** Schema/contract bugs / PIT lookahead / silent-gap defaults / stale cache / survivorship bias / filing-lag violations / multi-version data source confusion / off-by-one rolling / NaN/inf propagation / empty DF handling / mutable defaults / cache invalidation / timezone confusion / float precision / producer crashes caught-and-empty / asymmetric data source confusion / symbol resolution failures (CDAY->DAY) / timezone/calendar drift / adjusted vs unadjusted price / OHLCV partial fill / unmasked NaN in rolling window / fillna propagation / Cython/numpy dtype mismatch / pandas merge cardinality / pyarrow schema drift.

**Consumption-side (~25 classes):** Dict-key typos (B918) / `not s.get(key)` patterns / comparison operator wrong direction / threshold hardcoded vs config drift / gate-stacking impossibility (B913) / type coercion (int vs bool vs float) / default values masking actual data / race producer-write/consumer-read / wrong as_of (t vs t+1) / engine wiring path divergence (B919) / test mocks divergent from production / per-strategy override conflicts with global / regime-conditional gate fires in wrong regime / multi-timeframe alignment / calendar gate wrong calendar / threshold ramp-down semantics / cube cell expects metric not in writer schema / dashboard expects field not in dossier / config drift across batches / hardcoded magic numbers / unit confusion (bps vs decimal) / signed vs unsigned numeric / int overflow in cumsum / boolean array indexing misuse / chained pandas assignment SettingWithCopyWarning.

**Architectural (~10 classes):** Engine path bypass (canonical vs alternate) / cache/index lookup divergence / backtest checkpoint resume / worker pool partition / AWS bootstrap install gap (B901 SMC) / CI bypass (`--no-verify`) / pre-commit hook bypass / test pyramid tier skipping / cube cell schema drift / dashboard data-source drift.

**Statistical (~10 classes):** Multiple-testing N misspecification (DSR N=5,694) / bootstrap not corrected for serial correlation / PIT split contaminated by feature engineering / OOS slice leak via informal awareness / survivorship bias in universe / look-ahead via composite signal smoothing / pseudo-OOS via Stage 4 walks feeding R5 / researcher degrees-of-freedom inflation / sample-size adequacy / per-regime sample-split logic.

**Data-layer (~10 classes):** Path-from-source recursive vs parent-only / temporal coverage gap (B917) / schema-contract probe missing (CHECKLIST #106) / KNOWN-EVENT runtime probe missing / #44(b) investigate-why skipped / data revision after seal / ticker rename map (CDAY->DAY) / holiday calendar drift / adjusted vs unadjusted price / universe membership PIT.

**Observability (~10 classes):** Silent producer failures at DEBUG (B273) / intermediate counts not emitted / per-100-day cumulative progress missing / heartbeat absence (process died) / cache miss rate not surfaced / no baseline comparison alarm / log level too low / trade log emit failure not raised / test coverage report missing / performance regression not detected.

#### 13.9.5 Detection Mechanism per Bug Class (Architecture-Level)

| Layer | Mechanism | When | Catches |
|---|---|---|---|
| Pre-commit | YAML signal-key registry + AST scan | Every commit | Dict-key typos / silent-gap defaults / type coercion / threshold drift |
| Pyramid Unit | 699+ tests + 30+ new invariants | Every commit | Schema contracts / config keys / API stability |
| Pyramid Integration | 149+ tests + engine parity test | Every commit | Engine path divergence / cache lookup |
| Pyramid Property | Hypothesis-based fuzz | Pre-push | Off-by-one / NaN propagation / edge cases |
| Pyramid Coverage | `coverage run` on canonical backtest | Pre-merge | Wiring traces / dead code / unwired strategies |
| Pyramid Data Integrity | Per-producer schema pin + temporal coverage | Daily (cron) | PIT lookahead / filing-lag / survivorship / stale cache |
| Pyramid Negative-Control | 5 null strategies injected | Per cube run | Framework calibration / silent-pass false positives |
| Pyramid Statistical | DSR N + bootstrap CI + null distribution | Per cube run | Multiple-testing / overfitting / look-ahead |
| Pyramid Architectural | Engine-paths-parity + AWS-bootstrap-install + CI-not-bypassed | Pre-deploy | Engine bypass / install gap / CI bypass |
| Runtime Invariants | `backtest/invariants/runtime.py` 20 invariants | Engine startup | Closed producer manifest / single entry path / fire-count power floor |
| Observability | Intermediate-count emitter + heartbeat + baseline alarm | Per-100-day during cube | Silent crashes / hangs / drift |
| Planted-Bug Canary | Owner-injected bug; framework must catch | Pre-R5 launch | Theater detection / walk methodology integrity |
| Owner CLI | `python scripts/probe.py --invariant X` deterministic | Owner-on-demand | Independent verification (no Claude interpretation) |
| Lineage Auto-Grown | Pattern library detection greps + false-positive rate tracking | Every walk | Recurrence of past bug classes |

#### 13.9.6 Pattern Library (Auto-Grown; Compounding Asset)

- Every bug found -> `pattern_<N>.json` (producer-type + symptom + detection-grep + fix-template + false-positive rate)
- Library auto-runs detection greps on every walk + every commit
- Dashboard shows "patterns prevented this turn" + "patterns prevented cumulative"
- After 50 patterns, library catches ~80% of new walk bugs pre-commit
- Day-1 seeds: `default-True-silent-gap`, `not-s-get-pattern`, `regime-affinity-mass-edit`, `gate-stacking-fire-starve`, `missing-inverse-mechanical-mirror`, `TIER-2-producer-deferral`, `asymmetric-data-source-mirror`, `STATE-vs-EVENT-temporality-mismatch`, `family-bug-grep-skip`, `wrong-dict-key-typo`.

#### 13.9.7 What This Bug Framework Does NOT Catch (Honesty per Brief)

- **Statistical methodology errors** beyond named ones (Bonferroni denominator on trade-sparse strategies, Chow on regime-coincidence). These need separate stream per DEC-508 Tier 3.
- **Strategy-research-design errors** (Pattern W subset, no-prior-edge clusters). These are Stage 4 walk quality, not bug-catching.
- **Adversarial market regime shifts post-R5.** Out of scope.
- **Doc drift after R5** (the framework itself rots). Needs 90-day predicate-rot detector at Phase 1C.
- **Unknown unknowns.** R5 will surface bug classes this framework didn't anticipate; that's what R5 is for. Council 40's methodology calibrates on what R5 actually broke.

### 13.10 Time Estimate (Honest)

| Estimate | Source | Caveat |
|---|---|---|
| 1 week | Outsider | Kill council 37; minimum-viable R5 |
| 10-14 days | Executor | 118-178h wall-clock; 30-40h owner-attention |
| 39 days | Expansionist | With platform + compounding assets |
| 90-115 turns | Quant | With statistical depth |

**Council 38 synthesis: ~2-3 weeks for Phase 0 + Phase 6 launch. Phase 1B-alpha follows after R5 verdict.**

**Honest caveat (Outsider):** 36 prior councils -> 0 shipped R5. Hard moratorium on workflow redesign until R5 ships. After R5, Council 40 calibrates on actual failures, not feared ones.

### 13.11 Discipline Enforcement (Strict; No Exceptions)

Per owner directive 2026-06-19 ("Discipline to be enforced strictly! No exceptions"):

1. **Mandatory council per turn** — every recommendation / verdict / disposition / methodology proposal preceded by Agent council call. Surfaced in response. Memory rule: `feedback_mandatory_council_per_turn`.
2. **CHECKLIST compliance per #110** — pre-flight visible block applying full CHECKLIST.md (currently 55+ items) before every recommendation. End-of-response compliance statement (#45) is per-response gate.
3. **No surface-level audits** — every audit traces END-TO-END (source -> producer -> binding -> strategy -> engine -> output). Memory rule: `feedback_no_surface_level_audits`.
4. **No-delete invariant** — `STRATEGIES_DELETED_R5_ROUND = set()` always empty; DEPRECATED requires owner-signed B-tag in `DEPRECATION_LEDGER.md`.
5. **OOS seal** — Claude literally cannot see 2024-2026 data until seal opens at R5 launch.
6. **Planted-bug canary gate** — owner injects bug; framework must catch; otherwise walk methodology is theater (R5 launch gate #15).
7. **Independent verifier** — owner-runnable diagnostic CLI for top 5 invariants (deterministic, no Claude interpretation).
8. **Hard moratorium on workflow redesign** — no Council 40+ on workflow until R5 ships. After R5, Council 40 calibrates on actual failures.
9. **Engine path unification** — single canonical `signal_loader.py`; both engines import; engine-parity pytest enforced.
10. **Pattern library auto-runs** — every commit; false-positive rate tracked per pattern; auto-deprecate >30% FP.

### 13.12 Integration Points

| Target | Integration |
|---|---|
| `backtest/engine/backtest.py` | cube_runner adapter (cube_runner orchestrates, backtest.py executes per-cell) |
| `backtest/results/metrics.py` | soft_score plugins (one per ranking); DSR/cost-sens become multiplicative gates (DEC #1) |
| `backtest/results/writer.py` | walk_card emission + autopsy emission + delta record emission |
| `STRATEGY_ROSTER.md` | Auto-included in cube_explorer (live link) |
| `EXECUTION_QUEUE.md` | Walk-card schema items auto-queue |
| `VERIFICATION_MATRIX.md` | Updated post-P0 (coverage-based wiring per DEC #3) |
| `dashboard_phase_1a/` | DEPRECATE post-B921; archive to `archive/dashboard_phase_1a_r4/` |
| `dashboard_stage_2/` | KEEP (DEC/BUG/INV registry — required for owner workflow) |
| `dashboard_sprint0a/` | KEEP (API coverage — read-only ops) |
| `dashboard_r5/` | NEW (single dashboard, 7 tabs; Cube heatmap + Winners + Cluster explorer + R4->R5 delta + Bug-fix attribution + Regime affinity + Fire-count diagnostic) |
| Phase 1B-alpha launch spec | Consumes CORE/EDGE/DIVERSIFY portfolios as agent tiers |

### 13.13 Failure Modes + Guardrails

| Failure | Detection | Guardrail |
|---|---|---|
| Silent-gap typo (B918 class) | `test_no_signal_key_typos` (AST registry cross-check) | Pre-commit hook blocks commit |
| Strategy silently fires 0 times | `test_every_strategy_fires_at_least_once_T1a_sample` | P0 fails; P1+ blocked |
| P3 autonomous fix breaks unrelated strategy | `test_r5_phase_gates::test_p3_done` (full pyramid) | Fix reverted; manual review queued |
| Median R4->R5 Sharpe delta negative | `r5_delta_analyzer.py` guardrail assertion | P6 blocked; revert candidate or accept w/ documented reason |
| Unique winners < 30 or > 60 | `r5_cluster_dedup.py` exit code 2 | Owner-tuned cluster threshold required |
| Cube cell convergence < 85% | P6 gate assertion | Partial-cube launch with explicit gap manifest |
| Owner skips P2 manual review | `"OWNER_APPROVED" in r5_p2_status_proposed.csv` | P3 won't run |
| Deprecation without ledger entry | `test_no_strategy_is_deprecated_without_owner_token` | No-delete invariant enforced |
| Cost-sensitivity not measured | P1 emits per-strategy 20bps shock estimate | Catches friction-killers at P1 not P6 |
| Compute crash mid-P6 | `r5_launch.py --checkpoint-every 100` | Resumable; no work lost |
| OOS slice leak | Claude reads-only redacted dossier until seal opens | Stream E redaction; checked in pyramid |
| Council fatigue (Outsider warning) | Hard moratorium per 13.11 #8 | Owner enforces |
| Framework rots post-R5 | 90-day predicate-rot detector | Phase 1C item |
| Stream E script bugs propagate to all 219 dossiers | Self-test on 5 known-good + 5 known-broken BEFORE running on 218 | Executor recommendation |
| DSR N misspecification | DEC #5 explicit N=5,694 (B958 amended to N_effective=5,874 post-P6.5) | Quant requirement |
| Planted-bug canary missed by walk | R5 launch gate #15 BLOCKS | Independent verifier |
| **P6.5 trial-budget overrun** | `r5_p65_trial_log.json` row count > 180 | P6.5 hard-abort + manual reset + owner countersign |
| **OOS-seal-bleed via accidental 2026-Q2+ access** | Pyramid test asserts no read of Q2+ files until P6.5 ends; `oos_q2_seal_hash` re-verified at P6.5 exit | Pre-commit hook + Stream V check |
| **P6.5 Track B qualifier-creep** (every failed strategy argued into qualifier set) | All 4 gates required (post-Bonferroni Sharpe in [0.55, 0.70] AND t-stat >= 2.0 AND OOS quartile >= 2 AND >=1 edge signal); operationalized as `is_track_b_qualifier(strategy_row)` function | Function-level unit test on synthetic borderline rows |
| **P6.5 Type 1 sweep beyond natural range** | Only documented literature ranges per parameter (ATR 0.5-2.0x, R:R 1.5-4.0, trail 0.5-3.0%); open-ended search BLOCKED | Pre-registered config; deviation requires DEC |

### 13.14 Memory Rules Codified This Session

- `feedback_mandatory_council_per_turn` (2026-06-19) — council BEFORE recommendations
- `feedback_no_surface_level_audits` (2026-06-19) — end-to-end audit traces

Both surface in pre-flight + EOT compliance statement per CHECKLIST #110.

---

### 13.15 Phase 6.5 Design (B958 Council 63 owner-approved 2026-06-20)

**Trigger:** Owner question 2026-06-20 "In any phases will we be undertaking parameter optimization so we improve the performance of the strategies? Council this." Council 61 surfaced PATH terminology hole (param-sweep vs cell-selection) + DSR-contamination fear. Council 62 corrected scope (rejecting owner's 28,500-cell pre-R5 sweep + 730-review FIRE_STARVED loosening as overfitting machines). Council 63 finalized design with B957 reassurance factored in (DSR contamination measured at 1.04x, NEGLIGIBLE).

**Owner's two-type taxonomy:**
- **Type 1: Exit parameter / gate optimizations** (ATR multiplier, R:R ratios, trail tightness)
- **Type 2: Strategy gate optimizations** similar to Stage 4 (RSI thresholds, EMA periods, gate add/remove, regime affinity)

**Council 63 Option (beta) two-track architecture:**

| Track | Timing | Phase | Scope |
|---|---|---|---|
| **Type 2 Track A — Redundancy consolidation** | **PRE-R5** | Absorbed into **P2 reclassification** | redundancy_phi_matrix (Section 4) built on R4 cube data; cluster representatives stay STRATEGY_STATUS=ACTIVE; reskins flip to DEPRECATED. Honors B705. |
| **Type 1 — Exit-param sweep** | **POST-R5** | New **P6.5** | 4-variant sweep within winning exit method only; documented literature ranges (ATR 0.5-2.0x; R:R 1.5-4.0; trail 0.5-3.0%); 120 trials cap (30 R5-survivors x 4 ATR variants). |
| **Type 2 Track B — Gate refinement on borderline survivors** | **POST-R5** | New **P6.5** | Survivor-only; ALL 4 GATES required for qualifier (Contrarian 3 + Outsider edge signal); 60 trials cap (20 borderline-with-edge survivors x 3 gate variants). |

**Total Phase 6.5 trial budget: 180 hard cap.** DEC #5 amended: N_effective = 5,874 for DSR post-P6.5.

**OOS seal preservation method (a):**

- 2026-Q2+ slice carved out at B958 commit; hash-pinned in AUDIT.md
- Sealed indefinitely; held out from Phase 6.5 refinement
- R5 (P5+P6) uses 2020-01-01 → 2026-Q1 (~6.25 years; exceeds 5-yr backtest floor)
- Method (b) "forward-only on post-R5 papertrade" considered + rejected (delays winner extraction >=6 months + introduces papertrade survivorship)

**Track B qualifier (4 gates; ALL required):**

```python
def is_track_b_qualifier(strategy_row) -> bool:
    return (
        0.55 <= strategy_row.post_bonferroni_sharpe <= 0.70
        and strategy_row.raw_t_stat >= 2.0
        and strategy_row.oos_quartile_rank >= 2
        and (
            strategy_row.smart_money_lift_pp >= 5.0
            or strategy_row.per_regime_pass_count >= 2
            or strategy_row.calmar >= 0.75
        )
    )
```

Expected qualifier count from R5: ~15-25 strategies (well under 60 cap).

**Type 1 trigger:** R5-survivor strategy whose winning exit method has documented natural sweep range in literature (ATR multiplier, R:R ratio, trail percent). No open-ended search. 4-variant sweeps only.

**Pre-registered Type 1 parameter ranges:**

| Exit parameter | Variants | Source |
|---|---|---|
| ATR multiplier | 0.5x / 1.0x / 1.5x / 2.0x | Wilder 1978 + Chande 1995 |
| R:R ratio | 1.5R / 2.0R / 3.0R / 4.0R | Van Tharp 1999 |
| Trail percent | 0.5% / 1.0% / 2.0% / 3.0% | Chandelier 1995 |

**P6.5 workflow:**

1. P6 R5 launch completes → output_r5_final/ frozen + committed
2. Stream V reproduces 5 random strategies bit-identical (per launch gate #14)
3. P6.5 entry checklist verified (gates 16-20 above)
4. Track B qualifiers identified via `is_track_b_qualifier()` over R5 results
5. Type 1 + Type 2 Track B trial cells fired against 2020-2026-Q1 IS slice (Q2+ sealed)
6. Refinement results merged with R5 baseline; DSR re-computed at N=5,874
7. Winner roster diff posted (R5-raw vs P6.5-refined) for owner review
8. P7 Stage 3 winner extraction runs `scripts/optimize_strategies_from_cube.py` (B388) on refined cube

**Failure-mode guardrails (added to §13.13):** trial-budget overrun, OOS-seal-bleed, Track B qualifier-creep, Type 1 sweep beyond natural range.

### 13.16 DEC-PHASE-6.5-RESET (Council 7 Binding Reset)

**Background:** Council 7 binding (2026-06-12) was: *"R5 → agents → papertrade. No changes."* Interpretation: R5 measures EXISTING parameters; no within-R5 nor post-R5 parameter changes.

**Owner directive 2026-06-20:** Phase 6.5 introduced (per §13.15) — pre-registered, budgeted exception to Council 7 binding. Council 7 status is RESET, not silently overridden.

**DEC-PHASE-6.5-RESET structure:**

1. **Rationale:** R5 produces measurement, not strategy changes (Council 7 default still holds for R5 itself); Phase 6.5 is the pre-registered, budgeted, post-R5 exception. Within-R5 mid-run tuning remains BANNED.
2. **Scope:** Phase 6.5 only. No within-R5 mid-run tuning. No Phase-7+ re-tuning (winner extraction is selection, not parameter change). No retroactive amendments to P6.5 protocol post-R5.
3. **Trial budget:** 180 hard cap (allocated 120 Type 1 + 60 Type 2 Track B per §13.15).
4. **OOS preservation:** 2026-Q2+ carve-out (method a per §13.15); sealed at B958 commit; hash recorded in AUDIT.md.
5. **Entry gates:** R5 (P6) complete + all 5 P6.5 entry gates (§13.7 gates 16-20) + owner countersign on `output_audit/r5_p65_owner_signoff.json`.
6. **Exit gates:** Trial log committed (`r5_p65_trial_log.json`) + DSR re-computed at N=5,874 + winner roster diff vs R5-raw posted + Stream V Phase-6.5 reproducibility verified.
7. **Owner signature workflow:** `output_audit/r5_p65_owner_signoff.json` produced by Phase-6.5 entry script with required fields: timestamp / OOS Q2+ hash / trial budget remaining / Council 63 verdict reference / owner-countersigned flag.

**Pre-flight gate:** Phase 6.5 launch script asserts all of (1)-(6) above; fails on any missing.

**Auditability:** Every Phase 6.5 trial cell logged in `r5_p65_trial_log.json` with (strategy, parameter, variant, before_metric, after_metric, IS-slice-confirmed). Post-hoc audit reproduces from this log + Q2+ seal hash.

**Council 7 LIFTED-FOR-P6.5 status:** logged in AUDIT.md per CHECKLIST #67 doc-sync requirement.

---
