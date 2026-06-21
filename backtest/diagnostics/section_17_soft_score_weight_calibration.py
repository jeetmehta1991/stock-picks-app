# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 17 + Section 13.4 DEC #1
# per CHECKLIST #77.
"""B966 (2026-06-20): Phase P1 batch 26 - Section 17 soft_score_weight_calibration.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 row 17 + DEC #1 (Section 13.4)
# + Council 67 4/4 verdict per owner directive 2026-06-20 'Continue council
# this. Continue without stopping till all sections in P1 are done.' per
# CHECKLIST #77.

PURPOSE
-------
Section 17 = Soft-score weight calibration per PATH Section 13.3 row 17:
  'Soft-score weight calibration via null'
  'Weights derived from null-distribution variance, NOT hand-tuned (Quant);
   revisit at Phase 1C as Bayesian posterior'

DEC #1 (PATH Section 13.4):
  Soft-score reweight to 0.35/0.30/0.23/0.12 + DSR/cost-sens promoted from
  soft-ingredients to MULTIPLICATIVE GATES.

  Weight mapping per DEC #1:
    0.35 -> sharpe (normalized)
    0.30 -> calmar (normalized)
    0.23 -> profit_factor (normalized)
    0.12 -> [4th ingredient; DEC #1 does not specify; placeholder]

PRE-BUILD CHECK (Council 67 Executor + Contrarian hardening, executed):
  PATH Section 13.4 DEC #1 weights: 0.35 / 0.30 / 0.23 / 0.12 confirmed
    (sum = 1.00 OK)
  Section 16 (B965) null injection script BUILT same turn (calibration
    depends on null distribution from R5 cube + nulls).
  R5 null distribution: NOT YET AVAILABLE (R5 cube not launched).
  Contrarian hardening: machine-readable placeholder flag (placeholder=True,
    do_not_use_for_winner_selection=True) so downstream consumers HALT not
    silently consume. First Principles hardening: weights are priors with
    sigma=infinity until null distribution arrives.
  Build APPROVED.

CALIBRATION METHODOLOGY (post-R5, future):
  1. Run R5 cube including 5 null strategies (Section 16 inject).
  2. Compute null distribution for sharpe / calmar / profit_factor / [4th].
  3. Compute variance(metric | null) for each ingredient.
  4. Weight_i proportional to 1 / variance_i (inverse-variance weighting).
  5. Normalize weights to sum to 1.0.
  6. Cross-check: high-variance metrics get LOW weight (noise-dominated;
     unreliable for winner selection); low-variance metrics get HIGH weight
     (signal-stable; reliable for ranking).
  7. Document weights in DEC #1 amendment + revisit Phase 1C as Bayesian
     posterior (variance(metric | null) prior + variance(metric | observed
     winners) likelihood).

OUTPUT SCHEMA per strategy (identical across all 219 - framework-level state):
{
  "weights": {
    "sharpe": 0.35,
    "calmar": 0.30,
    "profit_factor": 0.23,
    "fourth_ingredient_unspecified": 0.12,
  },
  "weights_sum": 1.00,
  "weight_source": "DEC #1 placeholder (PATH Section 13.4)",
  "placeholder": True,
  "do_not_use_for_winner_selection": True,
  "calibration_method_pending": "null_distribution_variance_inverse",
  "calibration_status": "pre_r5_static_weights_pending_null_calibration",
  "fourth_ingredient_status": "unspecified_per_DEC_1_pending_owner_decision",
  "fourth_ingredient_candidates": ["sortino", "win_rate", "psr", "expectancy"],
  "calibration_dependency": "section_16_negative_control_canary",
  "phase_1c_revisit_method": "bayesian_posterior",
  "method": "static_placeholder_pre_r5",
  "source": "PATH_TO_PHASE_1B_ALPHA.md Section 13.4 DEC #1",
  "limitation": str,
  "memory_rule_reference": str,
}
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent.parent

# DEC #1 canonical weights (PATH Section 13.4; amended B969 owner-approved
# 2026-06-21 per Council 70+71 DEFER + RENORMALIZE verdict).
# Renormalized from 0.35/0.30/0.23 (sum 0.88) divided by 0.88 = 0.4 / 0.34 /
# 0.26. The 4th-ingredient slot (was 0.12) is REMOVED; 4th derived post-R5
# from null-distribution variance per Council 38 Quant directive in single
# joint calibration pass (ticket S5-NULL-CALIB-SOFT-SCORE-4TH-INGREDIENT).
DEC_1_WEIGHTS: dict[str, float] = {
    "sharpe": 0.40,
    "calmar": 0.34,
    "profit_factor": 0.26,
}

# Observer columns shipped in R5 cube for empirical 4th-ingredient
# comparison per Council 70 mandate. NOT weighted; NOT used for
# winner-selection until post-R5 null calibration ticket closes.
OBSERVER_COLUMNS: tuple[str, ...] = (
    "sharpe_stability",   # cross-regime sigma/mu inverted; complements gate #11
    "ulcer_index",        # sqrt(mean(drawdown**2)); depth x duration
    "tail_ratio",         # |p95(returns)| / |p05(returns)|; fat-tail
    "k_ratio",            # Kestner 1996; equity curve linearity
)


def _weights_sum() -> float:
    """Sum of DEC #1 weights; must be 1.0."""
    return round(sum(DEC_1_WEIGHTS.values()), 4)


def extract_section_17_for_strategy(strategy: str) -> dict[str, Any]:
    """Extract Section 17 soft_score_weight_calibration for a single strategy.

    The payload is framework-level (identical across all 219 strategies pre-R5)
    but emitted per-strategy for dossier consistency. Post-R5, an amended
    DEC #1 ledger will populate calibrated weights from null distribution.

    method='static_placeholder_pre_r5'.
    """
    weights_sum = _weights_sum()
    assert abs(weights_sum - 1.0) < 1e-6, (
        f"DEC #1 weights must sum to 1.0; got {weights_sum}"
    )

    return {
        "weights": dict(DEC_1_WEIGHTS),
        "weights_sum": weights_sum,
        "weight_source": "DEC #1 renormalized 3-ingredient (PATH Section 13.4 B969 amendment)",
        "n_ingredients": 3,
        "is_renormalized_from_4_ingredient_draft": True,
        "calibration_method_pending": "null_distribution_variance_inverse",
        "calibration_status": "3_ingredient_renormalized_post_r5_null_calibration_pending",
        "fourth_ingredient_status": "deferred_post_r5_per_council_70_71_owner_approved_2026_06_21",
        "fourth_ingredient_observer_columns": list(OBSERVER_COLUMNS),
        "observer_column_status": "pending_r5_cube_launch",
        "observer_column_values": {col: None for col in OBSERVER_COLUMNS},
        "calibration_dependency": "section_16_negative_control_canary",
        "post_r5_ticket": "S5-NULL-CALIB-SOFT-SCORE-4TH-INGREDIENT",
        "phase_1c_revisit_method": "bayesian_posterior",
        "method": "renormalized_3_ingredient_post_r5_deferred_4th",
        "source": "PATH_TO_PHASE_1B_ALPHA.md Section 13.4 DEC #1 (B969 amendment)",
        "limitation": (
            "DEC #1 weights are RENORMALIZED 3-ingredient (0.40/0.34/0.26) "
            "per B969 Council 70+71 owner-approved 2026-06-21 'DEFER + "
            "RENORMALIZE' verdict. The original 4-weight draft (0.35/0.30/"
            "0.23/0.12) had an UNSPECIFIED 4th ingredient slot; pre-R5 "
            "selection from B966 candidates (sortino/win_rate/psr/"
            "expectancy) was REJECTED by Council 69 4/4 as gate-redundant "
            "(criteria #1/#3/#12) or DEC #6 collision-prone. Observer "
            "columns (sharpe_stability/ulcer_index/tail_ratio/k_ratio) "
            "shipped in R5 cube for empirical comparison; 4th ingredient + "
            "weight derived JOINTLY post-R5 from null-distribution "
            "variance per Council 38 Quant directive (ticket "
            "S5-NULL-CALIB-SOFT-SCORE-4TH-INGREDIENT). No winner-selection "
            "role for observer columns until ticket closes. DSR + cost-sens "
            "remain MULTIPLICATIVE GATES per DEC #1 (preserved from "
            "original; CLAUDE.md criterion #14 + DEC-612 AUTO-FAIL #1)."
        ),
        "memory_rule_reference": (
            "Council 70 4/4 UNANIMOUS DEFER + RENORMALIZE per "
            "feedback_no_apriori_strategy_pruning extended to metrics + "
            "Council 38 Quant null-distribution-derived weights directive. "
            "Council 71 4/4 (delta) execution scope per "
            "feedback_pyramid_no_exceptions + feedback_wired_means_engine_"
            "consumed. B969 owner-approved 2026-06-21 with corrective "
            "directive 'Council is supposed to enumerate and provide "
            "final recommendation. Both are needed' codified as "
            "CHECKLIST #115."
        ),
    }


def populate_section_17_for_dossier(strategy: str, dossier_path: Path) -> None:
    """Populate Section 17 soft_score_weight_calibration slot in dossier.json."""
    with open(dossier_path) as f:
        dossier = json.load(f)
    section_payload = extract_section_17_for_strategy(strategy)
    sections = dossier.setdefault("sections", {})
    sections["section_17_soft_score_weight_calibration"] = section_payload
    with open(dossier_path, "w") as f:
        json.dump(dossier, f, indent=2, default=str)
