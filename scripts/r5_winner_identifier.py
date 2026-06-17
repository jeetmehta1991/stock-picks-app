"""B895 (2026-06-18) - R5 winner identifier with soft-score + Best-of-26 collapse.

# Source: PATH_TO_PHASE_1B_ALPHA.md section 3 (Best-of-26 collapse EXIT-AXIS-ONLY +
# soft-score formula) + section 2.2 (AUTO-FAIL screens; DEC-612/613/614 B890) +
# Council 19 verdict 2026-06-18 (B895 scaffold).

Council 15 corrected Council 14: collapse is EXIT-AXIS ONLY (never strategy-axis).
B807 latent-collapse audit empirically forbids strategy-axis collapse (97.5%%
phi<0.30 across 4-7 latent-factor hypotheses).

CLI:
    python scripts/r5_winner_identifier.py \\
        --cube <r5-cube.parquet> \\
        --output-winners <winners.csv> \\
        --output-rejects <rejects.csv> \\
        [--min-sharpe 0.7] [--apply-auto-fail] [--tier {1,2,3,all}]

Soft-score formula (PATH_TO_PHASE_1B_ALPHA.md section 3):
    soft_score = 0.30 * normalized(sharpe)
               + 0.25 * normalized(calmar)
               + 0.20 * normalized(profit_factor)
               + 0.15 * normalized(dsr)
               + 0.10 * (1 - cost_sensitivity)

B895 SHIP STATUS: scaffold + soft-score formula + AUTO-FAIL screen wrappers.
DEFER to B896 (post-R5): Best-of-26 collapse fill-in (needs actual cube data);
priority-tier quantile thresholds (needs distribution); AGENT-CANDIDATE tagging.
"""
# Source: PATH_TO_PHASE_1B_ALPHA.md sections 2.2+2.3+3 + Council 15 corrections (B889) +
#         backtest/config.py PASSING_CRITERIA + MEAN_REVERSION_STRATEGIES (B890) +
#         backtest/results/metrics.py _eval_cost_sensitivity_gate / _eval_chow_gate /
#         _eval_adf_gate (B890).
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

SOFT_SCORE_WEIGHTS: dict[str, float] = {
    "sharpe": 0.30,
    "calmar": 0.25,
    "profit_factor": 0.20,
    "dsr": 0.15,
    "cost_sensitivity": 0.10,
}

PRIORITY_TIER_1_QUANTILE = 0.90
PRIORITY_TIER_2_QUANTILE = 0.70


def compute_soft_score(row: Any, normalizers: dict[str, tuple[float, float]] | None = None) -> float:
    """B888 4-metric soft-score per PATH_TO_PHASE_1B_ALPHA.md section 3.

    normalizers: dict of metric -> (min, max) for min-max normalization.
                 If None, uses raw values (assumes pre-normalized cube).
    """
    if normalizers is None:
        sharpe = float(row.get("sharpe_oos", row.get("sharpe", 0.0)) or 0.0)
        calmar = float(row.get("calmar", 0.0) or 0.0)
        pf = float(row.get("profit_factor", row.get("pf", 0.0)) or 0.0)
        dsr = float(row.get("deflated_sharpe", row.get("dsr", 0.0)) or 0.0)
        cost_sens = float(row.get("cost_sensitivity_ratio", 1.0) or 1.0)
    else:
        def _norm(metric: str, val: float) -> float:
            lo, hi = normalizers.get(metric, (0.0, 1.0))
            if hi <= lo:
                return 0.0
            return max(0.0, min(1.0, (val - lo) / (hi - lo)))

        sharpe = _norm("sharpe", float(row.get("sharpe_oos", 0.0) or 0.0))
        calmar = _norm("calmar", float(row.get("calmar", 0.0) or 0.0))
        pf = _norm("profit_factor", float(row.get("profit_factor", 0.0) or 0.0))
        dsr = _norm("dsr", float(row.get("deflated_sharpe", 0.0) or 0.0))
        cost_sens = float(row.get("cost_sensitivity_ratio", 1.0) or 1.0)

    return (
        SOFT_SCORE_WEIGHTS["sharpe"] * sharpe
        + SOFT_SCORE_WEIGHTS["calmar"] * calmar
        + SOFT_SCORE_WEIGHTS["profit_factor"] * pf
        + SOFT_SCORE_WEIGHTS["dsr"] * dsr
        + SOFT_SCORE_WEIGHTS["cost_sensitivity"] * (1.0 - cost_sens)
    )


def apply_auto_fail_screens(df: Any) -> Any:
    """Apply B890 DEC-612/613/614 AUTO-FAIL screens.

    Returns df with new columns:
        - auto_fail_cost_sensitivity (bool)
        - auto_fail_chow (bool)
        - auto_fail_adf_mean_rev (bool)
        - auto_fail_any (bool)
    """
    try:
        from backtest.config import MEAN_REVERSION_STRATEGIES, PASSING_CRITERIA
    except ImportError:
        # B895 stub fallback - allow script to run before backtest installed
        MEAN_REVERSION_STRATEGIES = set()
        PASSING_CRITERIA = {
            "min_cost_sensitivity_ratio": 0.5,
            "chow_test_p_max": 0.05,
            "chow_post_break_sharpe_min": 0.3,
            "adf_test_p_max_mean_reversion": 0.10,
        }

    # DEC-612: Cost-sensitivity (sharpe_at_20bps / sharpe_at_0bps >= threshold)
    if "cost_sensitivity_ratio" in df.columns:
        df["auto_fail_cost_sensitivity"] = (
            df["cost_sensitivity_ratio"] < PASSING_CRITERIA["min_cost_sensitivity_ratio"]
        )
    else:
        df["auto_fail_cost_sensitivity"] = False

    # DEC-613: Chow break-point (p < 0.05 AND post-break sharpe < 0.3)
    if "chow_p_value" in df.columns and "post_break_sharpe" in df.columns:
        df["auto_fail_chow"] = (
            (df["chow_p_value"] < PASSING_CRITERIA["chow_test_p_max"])
            & (df["post_break_sharpe"] < PASSING_CRITERIA["chow_post_break_sharpe_min"])
        )
    else:
        df["auto_fail_chow"] = False

    # DEC-614: ADF stationarity (mean-rev only; non-stationary = no edge)
    if "adf_p_value" in df.columns and "strategy" in df.columns:
        is_mean_rev = df["strategy"].isin(MEAN_REVERSION_STRATEGIES)
        adf_stale = df["adf_p_value"] > PASSING_CRITERIA["adf_test_p_max_mean_reversion"]
        df["auto_fail_adf_mean_rev"] = is_mean_rev & adf_stale
    else:
        df["auto_fail_adf_mean_rev"] = False

    df["auto_fail_any"] = (
        df["auto_fail_cost_sensitivity"]
        | df["auto_fail_chow"]
        | df["auto_fail_adf_mean_rev"]
    )
    return df


def collapse_best_of_26(df: Any, axis: str = "exit_method") -> Any:
    """Per (strategy, regime), pick best soft-scored exit_method.

    PATH_TO_PHASE_1B_ALPHA.md section 3 Council 15 correction:
    collapse is EXIT-AXIS ONLY, never strategy-axis. The 218 strategies
    are NOT 4-7 latent factors with reskins; they are 218 distinct
    hypothesis tests (B807 latent-collapse audit empirical verdict).
    """
    if axis != "exit_method":
        raise ValueError(
            f"Council 15 (B889) correction: collapse must be exit_method axis only. "
            f"Got axis={axis!r}. See PATH_TO_PHASE_1B_ALPHA.md section 3."
        )
    if "soft_score" not in df.columns:
        df["soft_score"] = df.apply(compute_soft_score, axis=1)

    grouped = df.sort_values("soft_score", ascending=False).groupby(
        ["strategy", "regime"], as_index=False
    ).first()
    return grouped


def assign_priority_tier(df: Any) -> Any:
    """T1: top 10%% by soft-score AND passes AUTO-FAIL. T2: top 30%% with regime PASS. T3: rest."""
    if "soft_score" not in df.columns:
        df["soft_score"] = df.apply(compute_soft_score, axis=1)
    if "auto_fail_any" not in df.columns:
        df = apply_auto_fail_screens(df)

    t1_threshold = df["soft_score"].quantile(PRIORITY_TIER_1_QUANTILE)
    t2_threshold = df["soft_score"].quantile(PRIORITY_TIER_2_QUANTILE)

    def _tier(row: Any) -> str:
        if row["auto_fail_any"]:
            return "T3"
        if row["soft_score"] >= t1_threshold:
            return "T1"
        if row["soft_score"] >= t2_threshold:
            return "T2"
        return "T3"

    df["priority_tier"] = df.apply(_tier, axis=1)
    return df


def main() -> int:
    parser = argparse.ArgumentParser(
        description="R5 winner identifier (soft-score + Best-of-26 + AUTO-FAIL).",
    )
    parser.add_argument("--cube", type=Path, required=True, help="R5 cube parquet path.")
    parser.add_argument("--output-winners", type=Path, required=True)
    parser.add_argument("--output-rejects", type=Path, required=True)
    parser.add_argument("--min-sharpe", type=float, default=0.7)
    parser.add_argument("--apply-auto-fail", action="store_true", default=True)
    parser.add_argument("--tier", choices=["1", "2", "3", "all"], default="all")
    args = parser.parse_args()

    if not args.cube.exists():
        print(
            f"ERROR: R5 cube not found at {args.cube}. R5 has not yet completed "
            "per PATH_TO_PHASE_1B_ALPHA.md section 1 (Wed AWS run; Thu AM extraction). "
            "This script's scaffold is ready; fill on R5 completion (B896+).",
            file=sys.stderr,
        )
        return 1

    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("pandas required; install via requirements.txt") from e

    df = pd.read_parquet(args.cube)
    df = apply_auto_fail_screens(df) if args.apply_auto_fail else df
    df["soft_score"] = df.apply(compute_soft_score, axis=1)
    collapsed = collapse_best_of_26(df, axis="exit_method")
    tiered = assign_priority_tier(collapsed)

    winners = tiered[~tiered["auto_fail_any"] & (tiered["sharpe_oos"] >= args.min_sharpe)]
    rejects = tiered[tiered["auto_fail_any"] | (tiered["sharpe_oos"] < args.min_sharpe)]

    if args.tier != "all":
        winners = winners[winners["priority_tier"] == f"T{args.tier}"]

    args.output_winners.parent.mkdir(parents=True, exist_ok=True)
    args.output_rejects.parent.mkdir(parents=True, exist_ok=True)
    winners.to_csv(args.output_winners, index=False)
    rejects.to_csv(args.output_rejects, index=False)
    print(f"[B895] Winners: {len(winners)} -> {args.output_winners}")
    print(f"[B895] Rejects: {len(rejects)} -> {args.output_rejects}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
