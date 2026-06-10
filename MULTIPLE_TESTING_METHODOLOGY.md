# Multiple-Testing Correction Methodology — Stage-D Cube Selection Policy

**Status:** APPROVED B667 (2026-06-09 owner-approved all 6 decisions). Implementation module `backtest/engine/multiple_testing_correction.py` ships in B667 with 19 unit + integration test pins (test_batch667_multiple_testing_correction.py). The Stage-D cube selection step integration ships in B668 (separate batch since it requires cube-replay infrastructure changes).

**Originally:** DRAFT — Batch 666 (2026-06-09 owner-approved foundational re-prioritization commitment per B665 critique #9 + #7).

**B667 outcome — owner-approved decisions:**

| # | Question | Approved decision |
|---|---|---|
| 1 | Which correction(s)? | **COMPOSE** (deflated-Sharpe Bailey-LdP + Hansen SPA + BH-FDR sanity check) |
| 2 | Family-size N? | **219 deployable** (excludes EXPLORATORY via `cube_eligible_for_multiple_testing` flag) |
| 3 | Per-regime vs overall? | **Both, independently corrected** |
| 4 | EXPLORATORY treatment? | **Exclude from family-size count, keep in cube scoring** (W5 + W5m return False from `cube_eligible_for_multiple_testing`) |
| 5 | Per-direction scope? | **Per-direction families** (LONG + SHORT corrected separately) |
| 6 | C2 + R8 sequencing? | **Separately, R8 second** |

**B667 implementation surfaces all 6 decisions in code:**
- Decision 1 → `cube_select_with_multiple_testing()` orchestrator calls all 3 correction functions
- Decision 2 + 4 → `EXPLORATORY_STRATEGIES` constant + `cube_eligible_for_multiple_testing()` lookup; family-size N is computed per group as deployable-count
- Decision 3 + 5 → `cube_select_with_multiple_testing()` groups inputs by `(direction, regime)` before applying correction
- Decision 6 → walk-forward integration deferred; no R8-specific code in B667

**B668 SHIPPED (2026-06-09 owner-approved "Wire now"):** cube replay path integration via parallel artifact pattern.

- New module `backtest/results/cube_compose_verdict.py` wraps `cube_select_with_multiple_testing()` for trade-log aggregation
- `backtest/results/writer.py` emits `cube_compose_verdict.csv` alongside the existing DEC-578 `verdict_cube.csv`
- Architecture: **PARALLEL artifact** — does NOT replace 7-gate Gate 2 (Bonferroni) or Gate 3 (DSR); reviewer + cube tooling can A/B compare
- Per cell output columns: `strategy, direction, regime, sharpe_raw, n_trades, deflated_sharpe, deflated_sharpe_pvalue, spa_pvalue, bh_fdr_significant, passes_compose`
- Discrepancy diagnostic: writer log reports `discrepancy (BH vs COMPOSE) = N` count where BH-FDR significance disagrees with COMPOSE PASS verdict
- Test pyramid: 9 B668 cycle pins (test_batch668_cube_compose_integration.py) + 19 B667 + 842 unit+integration = 870/870 green
- Critical pin: test_batch668_exploratory_does_not_inflate_deployable_family_size verifies Decision 4 (W5+W5m in trade log don't change deployable strategies' deflated Sharpe in the writer-output path)

**Replacing the 7-gate Gate 2 + Gate 3 with COMPOSE** is a future B-N decision per `feedback_local_changes_default_global_needs_approval` (would touch load-bearing 7-gate path used by ~5 test files); not done in B668.

**B669+ next steps:**
- B669 — execute survivorship harness against W5 + W5m post-B660 land (per Decision 1 sequencing)
- B670+ — once Stage-D cube re-runs with the new `cube_compose_verdict.csv` artifact, update STAGE_4_PIVOT_CLUSTER_WALKS.md + STAGE_4_SMART_MONEY_CLUSTER_WALKS.md per-strategy FINAL STATUS blocks with multiple-testing-aware Sharpe ratios + discrepancy report

**Source:** External-AI 2nd-wave critique C2 (Pass 53 B641 audit) + 2nd-wave-redux critique #7 (Pass 53 B665) + queue tickets `S5-MULTIPLE-TESTING-CORRECTION` + `S5-DO-NOT-DEPLOY-MULTIPLE-TESTING-RECONCILIATION`.

**Audience:** External reviewer (continuity from STAGE_4_PIVOT_CLUSTER_WALKS.md cycle) + owner + future Claude. Pre-reading: this doc assumes familiarity with the [STAGE_4_PIVOT_CLUSTER_WALKS.md "Process Meta" section](STAGE_4_PIVOT_CLUSTER_WALKS.md#process-meta--ticket-arithmetic--foundational-re-prioritization-per-2nd-wave-redux-9-owner-approved-b665).

---

## Why this document exists

At 222 registered strategies × 26 exit methods × 7 historical regimes = 40,404 (strategy × exit × regime) cells in the Stage-D cube, **any cube selection step that picks "PASS" cells based on per-cell statistics is selection-bias contaminated by construction.** The probability that a single cell would appear to PASS by chance alone, even when every strategy is in fact useless, is non-trivial. Without correction:

- Family-wise error rate (FWER) bloats to near-certainty across 40,404 tests
- False discovery rate (FDR) is bounded only by the chance level α (typically 5%) → potentially 2,020 false-positive cells out of 40,404
- Per-strategy Sharpe ratios that look "passing" (e.g., ≥1.0) on a single backtest random-draw will fail OOS at a rate uncalibrated to the family size

**Reviewer's critique C2 (verbatim):** *"Multiple-testing / overfitting at 220 strategies on shared feature set; no FDR / SPA / deflated-Sharpe correction. Gates cube selection step."*

**Reviewer's critique #7 (B665 follow-up):** *"W5m being registered-but-not-deployed still consumes statistical budget — it makes the deflated-Sharpe bar higher for every other strategy. A strategy you've pre-decided not to trade should be excluded from the multiple-testing universe, not sitting in it inflating the correction."*

The combined ask: correct the cube selection for multiple testing + reconcile the DO-NOT-DEPLOY universe-inclusion question + scope the per-regime vs overall correction interaction.

---

## Policy decisions required (this draft surfaces; owner approves)

### Decision 1: Which correction(s)?

Three families of corrections are mature literature. Each addresses a different threat model.

| Correction | Threat model | Strengths | Weaknesses |
|---|---|---|---|
| **Bonferroni / Holm-Bonferroni** | FWER (≥1 false discovery in family) | Trivially conservative; no parameters | Overcorrects at scale; not used in financial-strategy literature |
| **Benjamini-Hochberg (BH-FDR)** | FDR (expected fraction of false discoveries) | Standard in genomics + Multiple-testing-rich domains; well-behaved at scale | Assumes test independence (we have correlated returns); BH-FDR yates more permissive |
| **Hansen Superior Predictive Ability (SPA, 2005)** | Equal Predictive Ability null vs ≥1 strategy outperforms | Hansen 2005 JF; specifically designed for trading-rule comparison; bootstrap-based; handles correlation | Computationally heavy; sensitive to bootstrap parameters |
| **Bailey-Lopez-de-Prado Deflated Sharpe Ratio (2014)** | Per-strategy Sharpe inflated by selection bias | Bailey-LdP 2014 JoPM; the standard in quant-strategy multiple-testing; corrects Sharpe for known family size + best-Sharpe statistic; closed-form | Single-strategy correction (not multi-strategy FWER); Bailey-LdP "deflate" is one Sharpe at a time |

**Recommended policy: COMPOSE.**
- **Deflated Sharpe (Bailey-LdP) for per-strategy reporting** — corrects the published Sharpe of each PASS strategy for the multiple-testing context (family size + max-Sharpe-among-N)
- **Hansen SPA for the PASS/FAIL adjudication** — the cube selection decision uses the SPA p-value vs the equal-predictive-ability null; only strategies with SPA p < α (typically 0.05) PASS
- **BH-FDR as a sanity check** — separate per-direction (LONG vs SHORT) BH-FDR pass on Sharpe rankings; if it disagrees with SPA, surface as discrepancy for owner review

This composition gates a PASS verdict on TWO independent statistical tests + reports a multiple-testing-aware Sharpe. Survivorship across all three is a strong evidentiary base.

**Alternative policy: SPA-only.** Simpler; faster; standard in the trading-rule literature. The trade-off: no per-strategy deflated Sharpe number to publish; reviewer can't reconcile reported Sharpe with multiple-testing-aware Sharpe.

**Alternative policy: Bonferroni-only.** Trivially conservative; if any strategy passes Bonferroni at 40,404 cells, the result is highly defensible. Trade-off: would likely reject every strategy in the current cube (over-conservative).

**Owner decision needed: COMPOSE / SPA-only / Bonferroni-only / other.**

### Decision 2: Family size N — what counts as a hypothesis?

The deflated-Sharpe + SPA formulas both require N = number of independent strategies tested. The choice affects how aggressive the correction is. Four candidates:

| N value | Definition | Implication |
|---|---|---|
| **N = 222 registered** | All `ALL_STRATEGIES` keys | Most conservative; includes EXPLORATORY + DO-NOT-DEPLOY + disabled — but disabled never produce results so this is mathematically equivalent to N=221 active |
| **N = 221 active** | All cube-eligible (excludes disabled `dxy_headwind`) | Standard interpretation; what the cube actually scores |
| **N = 219 deployable** | Active minus EXPLORATORY (W5 + W5m) | Per critique #7: strategies pre-decided not to deploy shouldn't inflate the correction for strategies you WILL deploy |
| **N = 1,716 (effective)** | Per M9 effective_strategy_count factor (accounting for correlated returns via Bailey-LdP haircut) | Adjusts for the fact that 222 strategies on shared OHLCV features have correlated tests; effective N is smaller |

**Recommended policy: N = 219 deployable** for the deflated-Sharpe + SPA p-value calculation. EXPLORATORY strategies are still scored (so they get a published Sharpe + verdict) but their inclusion in the family-size count would penalize deployable strategies for the existence of strategies that won't be deployed.

This addresses critique #7 directly: registered-but-DO-NOT-DEPLOY strategies do NOT raise the bar for strategies you actually want to deploy.

**Auxiliary auditing:** the M9 effective_strategy_count (~1,716 → far higher than 219 deployable) is computed separately as a correlation-haircut diagnostic. If effective N >> 219, that's a flag that the strategies are highly correlated and the deflated-Sharpe may still under-correct. Surfaced for owner review, not auto-applied.

**Owner decision needed: 222 / 221 / 219 / 1716 / other.**

### Decision 3: Per-regime vs overall scope

The Stage-D cube has TWO PASS verdicts: per-regime (PASS in ≥1 regime) and overall. Per-regime samples are smaller (typically n=30-100 trades); overall is larger (n=100-1000+ trades). The multiple-testing correction has TWO natural scopes:

| Scope | Family size | Implication |
|---|---|---|
| **Per-regime correction** | 219 deployable × 7 regimes = 1,533 hypotheses | Each (strategy × regime) verdict gets its own deflated Sharpe + SPA p-value; per-regime PASS bar is HIGH |
| **Overall correction** | 219 deployable hypotheses | Each strategy's OVERALL verdict gets a deflated Sharpe + SPA p-value; per-regime verdicts are reported but not corrected |
| **Hierarchical correction** | Bonferroni-by-regime (α/7) within each regime + overall family at α | Two-stage testing; stricter than per-regime alone |
| **Both: overall AND per-regime, independently corrected** | Two separate correction families | Strategies PASS overall if their overall deflated-Sharpe survives; PASS per-regime if their per-regime deflated-Sharpe survives in any regime |

**Recommended policy: Both, independently corrected.** This matches the cube's existing dual-verdict structure (overall AND per-regime). Per critique #4 (B665 #4): "B660 must report per-regime clustered counts (NOT a single annualized smear), so the strategy verdicts can be evaluated against the regime-by-regime min_trades=30 per-regime threshold rather than the easier overall ≥100 floor."

The dual-correction lets the cube surface:
- Strategies that PASS overall (broad-base alpha)
- Strategies that PASS only in specific regimes (regime-specialist alpha)
- Strategies that PASS neither (FAIL)
- Strategies where per-regime PASS conflicts with overall FAIL (regime-mix instability — flag for further review)

**Owner decision needed: per-regime only / overall only / hierarchical / both / other.**

### Decision 4: EXPLORATORY strategy treatment

W5 (`pivot_s3_capitulation`) and W5m (`pivot_r3_blowoff_short`) are marked EXPLORATORY per B644 / B645 / B652. W5m additionally has a DO-NOT-DEPLOY gate keyed on M10 + S5-MULTIPLE-TESTING-CORRECTION shipping (i.e., this document).

Per critique #7: EXPLORATORY strategies registered "for cube-replay coverage" still consume multi-testing budget if included in the correction family.

| Treatment | Implication |
|---|---|
| **Exclude EXPLORATORY from family-size count** | N = 219 instead of 221; EXPLORATORY strategies still scored + reported, but their inclusion doesn't penalize deployable strategies |
| **Include EXPLORATORY in family-size count** | N = 221; consistent with "registered = hypothesis"; preserves cube-replay coverage scoring; raises the deflated-Sharpe bar for everyone |
| **De-register EXPLORATORY at C2 ship** | N = 219; EXPLORATORY strategies excluded from cube entirely; loses dataflow + cube-replay coverage |

**Recommended policy: Exclude EXPLORATORY from family-size count, keep them in cube scoring.** Closes the critique #7 circularity (W5m being registered raises the bar for the C2 correction it's gated on) without losing the dataflow/cube-replay coverage that the registered-for-coverage rationale was supposed to preserve.

**Implementation:** add a `cube_eligible_for_multiple_testing: bool` flag per strategy; defaults to True; set False on EXPLORATORY-marked strategies. The deflated-Sharpe + SPA computations exclude strategies with this flag set False from the family-size count. The strategies still get scored individually + appear in cube outputs; they just don't count toward the correction family.

**Owner decision needed: exclude / include / de-register / other.**

### Decision 5: Per-direction (LONG vs SHORT) correction scope

Strategies are LONG, SHORT, AVOID, or DUAL. The cube treats each direction as a separate scoring path (LONG and SHORT of a dual strategy get separate Sharpe ratios + verdicts). The multiple-testing correction can be:

| Scope | Family sizes | Implication |
|---|---|---|
| **All directions in one family** | N = 219 deployable × ~1.5 (avg directions per strategy) = ~330 | Single deflated-Sharpe + SPA family covering all directional verdicts |
| **Per-direction families (LONG/SHORT separate)** | LONG family ~219; SHORT family ~80 (only ~80 strategies have SHORT direction) | LONG + SHORT scored independently; SHORT family is smaller so SHORT verdicts have a less-conservative bar; this matches the actual market-microstructure asymmetry per `feedback_asymmetric_data_sources_break_mechanical_inverse` + CHECKLIST (m) |

**Recommended policy: Per-direction families.** LONG and SHORT strategies have different base rates (equity-drift bias, squeeze risk, borrow costs), different sample sizes (most strategies are LONG-only), and different alpha sources. A unified family-size N=330 would lump structurally different statistical environments together.

**Owner decision needed: unified / per-direction / other.**

---

## DO-NOT-DEPLOY universe-inclusion policy (critique #7 explicit resolution)

The critique #7 circularity: W5m is DO-NOT-DEPLOY *until* the C2 correction lands; but the C2 correction's family size includes W5m by virtue of its registration; so W5m raises the bar for the correction it's gated on.

**Three operations interact:** (1) strategy registration in `ALL_STRATEGIES`; (2) cube scoring (which strategies get verdicts); (3) multiple-testing family-size count.

**Recommended decoupling:**
1. **Registration** = strategy can fire in the screener + produce candidate trades (no change)
2. **Cube scoring** = strategy gets per-(regime × exit) Sharpe + verdict in cube output (no change)
3. **Multiple-testing family-size count** = strategy contributes to N in the correction formulas (NEW: gated on `cube_eligible_for_multiple_testing` flag per Decision 4 above)

This gives 3 separate states a strategy can be in:
- **REGISTERED + SCORED + COUNTED** (default for active deployable strategies)
- **REGISTERED + SCORED + UN-COUNTED** (EXPLORATORY + DO-NOT-DEPLOY)
- **REGISTERED + UN-SCORED + UN-COUNTED** (DISABLED, e.g., `dxy_headwind` due to missing producer)

The W5m circularity is resolved: W5m is REGISTERED + SCORED + UN-COUNTED. Its Sharpe is still computed + reported for the eventual M10 + C2 unlock test, but its presence does not raise the bar for the rest of the family.

---

## Walk-forward integration with R8

`S5-REGIME-WALK-FORWARD-VALIDATION` (R8) is queued separately and gates whether regime-gating itself is OOS-net-positive. The multiple-testing correction interacts with walk-forward in three ways:

1. **Each walk-forward window is its own multiple-testing family** — if you split 2020-2026 into expanding windows (e.g., train on 2020-2022, test on 2023; train on 2020-2023, test on 2024), each test window's PASS verdicts should be corrected against the family of strategies tested in that window.
2. **The aggregate walk-forward Sharpe** (averaging per-window Sharpes) gets its own deflated-Sharpe correction using N = 219 deployable.
3. **Consistency check:** strategies that PASS in-sample but FAIL walk-forward are the curve-fit signal. Multiple-testing-corrected in-sample PASS minus walk-forward FAIL is a stricter discoverability bar than either alone.

**Owner decision needed:** does C2 + R8 ship together (joint policy) or separately (sequential)?

**Recommended policy: separately, R8 second.** C2 methodology can be drafted + implemented without R8 + cube-replay infrastructure changes; R8 is a cube-replay reconfiguration that depends on the C2 family-size + scope decisions already being made. Reverse order would create coupling.

---

## Implementation skeleton (preview only; ships in a later batch)

```python
# backtest/engine/multiple_testing_correction.py (PREVIEW — owner-approved policy version ships separately)

from dataclasses import dataclass
from typing import Sequence

@dataclass
class StrategyResult:
    name: str
    direction: str  # "long" / "short" / "avoid" / "dual"
    sharpe: float
    n_trades: int
    cube_eligible_for_multiple_testing: bool  # NEW per Decision 4

def deflated_sharpe_bailey_lopez_de_prado(
    sharpe: float,
    n_trades: int,
    family_size: int,
    expected_max_sharpe: float = None,  # if None, derived from family_size
) -> tuple[float, float]:
    """Returns (deflated_sharpe, p_value_vs_null)."""
    ...

def hansen_spa_pvalue(
    strategy_returns: Sequence[Sequence[float]],
    null_returns: Sequence[float] = None,  # benchmark; if None, zero-return null
    n_bootstrap: int = 1000,
) -> float:
    """Returns SPA p-value vs equal-predictive-ability null."""
    ...

def benjamini_hochberg_fdr(
    pvalues: Sequence[float],
    alpha: float = 0.05,
) -> Sequence[bool]:
    """Returns per-strategy pass/fail under BH-FDR at level alpha."""
    ...

def cube_select_with_multiple_testing(
    results: Sequence[StrategyResult],
    correction_policy: str = "compose",  # "compose" / "spa_only" / "bonferroni"
    family_size_scope: str = "deployable",  # per Decision 2
    per_regime: bool = True,  # per Decision 3
    per_direction: bool = True,  # per Decision 5
) -> dict:
    """Returns dict of {strategy: pass_verdict} with multiple-testing applied."""
    ...
```

---

## Open questions for owner decision

| # | Question | Recommended | Alternatives |
|---|---|---|---|
| 1 | Correction family — which | COMPOSE (deflated-Sharpe + SPA + BH-FDR sanity check) | SPA-only / Bonferroni-only |
| 2 | Family size N | N = 219 deployable (excludes EXPLORATORY + DO-NOT-DEPLOY from count) | 222 / 221 / 1716 effective |
| 3 | Per-regime vs overall | Both, independently corrected | per-regime only / overall only / hierarchical |
| 4 | EXPLORATORY treatment | Exclude from family-size count, keep in cube scoring (introduces `cube_eligible_for_multiple_testing` flag) | Include / de-register |
| 5 | Per-direction scope | Per-direction families (LONG + SHORT separate) | Unified |
| 6 | C2 + R8 sequencing | Separately, R8 second | Joint policy |

**Once owner-approved, the implementation batch ships with:**
- `backtest/engine/multiple_testing_correction.py` (the 3 correction functions + composer)
- `cube_eligible_for_multiple_testing` flag on every strategy (defaults from EXPLORATORY status)
- Cube selection step updated to call `cube_select_with_multiple_testing(...)`
- Per-addressal pyramid + unit tests for each correction function + integration test for the cube selection path
- Stage-D cube replay against the new selection path

---

## Outstanding queue tickets affected by this policy

| Ticket | Effect |
|---|---|
| `S5-MULTIPLE-TESTING-CORRECTION` | This document IS the methodology; closes when policy approved + implementation batch ships |
| `S5-DO-NOT-DEPLOY-MULTIPLE-TESTING-RECONCILIATION` | Closed by Decisions 4 + 5 (the `cube_eligible_for_multiple_testing` flag) |
| `S5-W8-POST-B654-REMAINING-REDUNDANCY-AUDIT` | W8 will be subject to the deflated-Sharpe correction post-C2 ship; the 3-of-4-gate redundancy will produce a Sharpe that gets penalized in the deflated calculation |
| `S5-REGIME-WALK-FORWARD-VALIDATION` (R8) | Ships separately per Decision 6 |
| `S5-MARGINAL-CONTRIBUTION-SCORING` (C3) | Independent of C2; ships separately |
| `B660` (in flight) | Provides the empirical Sharpe ratios that C2 will correct; must land before any deflated-Sharpe number is meaningful |

---

## End of C2 methodology draft

**Status:** AWAITING owner approval on 6 policy decisions before implementation ships.

**Next step after owner approval:**
1. Implementation batch (test-first per `feedback_pyramid_per_addressal`): unit tests for each correction function → SPA + BH-FDR + deflated-Sharpe pure-math implementations → cube selection integration → pyramid green
2. Re-run Stage-D cube with the corrected selection step
3. Document the diff: how many strategies PASS pre-correction vs post-correction; surface per-strategy deflated-Sharpe + SPA p-value
4. Update `STAGE_4_PIVOT_CLUSTER_WALKS.md` + `STAGE_4_SMART_MONEY_CLUSTER_WALKS.md` per-strategy FINAL STATUS blocks with multiple-testing-aware Sharpe ratios

**Reviewer-relevant note:** this draft addresses critique C2 (B641) + critique #7 (B665) AT THE METHODOLOGY LEVEL. The reviewer's specific concerns — registered-but-not-deployed budget consumption, family-size choice, per-regime vs overall — are each surfaced as explicit policy decisions rather than buried in implementation choices.
