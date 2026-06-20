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

# DEC #1 canonical weights (PATH Section 13.4)
DEC_1_WEIGHTS: dict[str, float] = {
    "sharpe": 0.35,
    "calmar": 0.30,
    "profit_factor": 0.23,
    "fourth_ingredient_unspecified": 0.12,
}


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
        "weight_source": "DEC #1 placeholder (PATH Section 13.4)",
        "placeholder": True,
        "do_not_use_for_winner_selection": True,
        "calibration_method_pending": "null_distribution_variance_inverse",
        "calibration_status": "pre_r5_static_weights_pending_null_calibration",
        "fourth_ingredient_status": "unspecified_per_DEC_1_pending_owner_decision",
        "fourth_ingredient_candidates": [
            "sortino", "win_rate", "psr", "expectancy",
        ],
        "calibration_dependency": "section_16_negative_control_canary",
        "phase_1c_revisit_method": "bayesian_posterior",
        "method": "static_placeholder_pre_r5",
        "source": "PATH_TO_PHASE_1B_ALPHA.md Section 13.4 DEC #1",
        "limitation": (
            "Weights are PLACEHOLDER per DEC #1 (PATH Section 13.4) NOT "
            "calibrated to R5 null distribution. The 4th ingredient is "
            "UNSPECIFIED in DEC #1 (only sharpe / calmar / profit_factor "
            "named); owner decision required pre-R5. Candidates: sortino "
            "(asymmetric vol penalty per CLAUDE.md #12), win_rate (intuitive "
            "robustness check), PSR (small-N companion to DSR per DEC #6), "
            "expectancy (raw E[trade]). do_not_use_for_winner_selection=True "
            "is a HARD GATE for downstream consumers: any system using these "
            "weights to rank R4/R5 winners is operating in pre-calibration "
            "mode and must FLAG verdicts as PROVISIONAL. Post-R5: null "
            "distribution variance(metric|null) computed across 5 null "
            "strategies (Section 16 inject); inverse-variance weighting "
            "amends DEC #1 weights with calibration_status="
            "'r5_null_distribution_calibrated'. Phase 1C: weights become "
            "Bayesian posterior combining null-prior + observed-winners-"
            "likelihood per DEC #1 First Principles guidance."
        ),
        "memory_rule_reference": (
            "Council 67 Contrarian hardening (B966): machine-readable "
            "placeholder flag (placeholder=True + do_not_use_for_winner_"
            "selection=True) so downstream consumers HALT not silently "
            "consume. Council 67 First Principles: weights are priors with "
            "sigma=infinity until null distribution arrives. "
            "feedback_no_write_only_md_files: this is consumed by R5 winner-"
            "selection code-paths (`backtest/results/metrics.py soft_score "
            "plugins` per PATH line 689)."
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
