"""B895 (2026-06-18) - B882 Sharpe-band decision tree evaluator.

# Source: PATH_TO_PHASE_1B_ALPHA.md section 1 (6-day path Thursday AM) +
# output_audit/r5_precommit_decision_tree.md (B882 pre-commit decision tree
# locked 2026-06-17). This script is the executor for the decision tree:
# given an R5 OOS Sharpe ratio (overall + per-regime), it emits a routing
# decision per the bands defined in B882.

Council 19 (B895) prioritized this script as the smallest blast-radius
scaffold that unblocks Thursday AM owner sign-off on R5 routing.

CLI:
    python scripts/eval_r5_sharpe_band.py \\
        --r5-summary <path-to-r5-cube-summary.parquet> \\
        --output <output.json> \\
        [--dry-run]

Decision bands per B882 + PATH_TO_PHASE_1B_ALPHA.md sections 7+10:
    sharpe_oos >= 1.0       -> GO_LIVE_STAGE_5 (skip Phase 1B-alpha; agents add 0 value above 1.0 baseline)
    0.7 <= sharpe_oos < 1.0 -> PHASE_1B_ALPHA  (canonical path; $300 Haiku budget)
    0.5 <= sharpe_oos < 0.7 -> CONDITIONAL_PHASE_1B_ALPHA (owner-gated; soft-score top decile only)
    sharpe_oos < 0.5        -> STOP (B882 honest fallback per Contrarian Council 14;
                                     defer Phase 1B-alpha; re-architect with clean post-2026 OOS slice)
"""
# Source: PATH_TO_PHASE_1B_ALPHA.md sections 1+6+10 + r5_precommit_decision_tree.md (B882) +
#         Council 19 verdict 2026-06-18 (B895 ship plan).
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROUTING_DECISION_GO_LIVE = "GO_LIVE_STAGE_5"
ROUTING_DECISION_PHASE_1B_ALPHA = "PHASE_1B_ALPHA"
ROUTING_DECISION_CONDITIONAL = "CONDITIONAL_PHASE_1B_ALPHA"
ROUTING_DECISION_STOP = "STOP"


def evaluate_sharpe_band(
    sharpe_oos: float,
    sharpe_per_regime: dict[str, float] | None = None,
) -> dict[str, Any]:
    """B882 decision tree: map OOS Sharpe to routing decision.

    Args:
        sharpe_oos: R5 OOS overall Sharpe ratio.
        sharpe_per_regime: optional dict of regime->Sharpe for per-regime check.

    Returns:
        dict with keys: action (str), band (str), rationale (str),
        sharpe_oos (float), n_regimes_passing (int), passed_regimes (list[str]).
    """
    n_regimes_passing = 0
    passed_regimes: list[str] = []
    if sharpe_per_regime:
        # B891 DEC-611: min_regimes_passing = 1 per CLAUDE.md canonical
        for regime, sharpe in sharpe_per_regime.items():
            if sharpe >= 0.7:
                n_regimes_passing += 1
                passed_regimes.append(regime)

    if sharpe_oos >= 1.0:
        action = ROUTING_DECISION_GO_LIVE
        band = ">=1.0"
        rationale = (
            "OOS Sharpe at or above industry-canonical 1.0 threshold; "
            "Phase 1B-alpha agent overlay is unlikely to add value above this "
            "baseline (DEC-131 gate requires agent_sharpe - rules_sharpe >= 0.2). "
            "Recommend skip Phase 1B-alpha; proceed directly to Stage 5 SWAP "
            "loop on winning cells."
        )
    elif sharpe_oos >= 0.7:
        action = ROUTING_DECISION_PHASE_1B_ALPHA
        band = "0.7-1.0"
        rationale = (
            "OOS Sharpe in canonical Phase 1B-alpha trigger band. Per "
            "PATH_TO_PHASE_1B_ALPHA.md section 1: launch $300 Haiku run on "
            "Priority-1 (deployment-optimized cells) + AGENT-CANDIDATE-tag-only "
            "subset (~60% Haiku budget savings vs blanket P1)."
        )
    elif sharpe_oos >= 0.5:
        action = ROUTING_DECISION_CONDITIONAL
        band = "0.5-0.7"
        rationale = (
            "OOS Sharpe below 0.7 canonical gate but above 0.5 honest-stop "
            "floor. Per Council 14 Contrarian dissent: this band is at risk "
            "of researcher-DoF overfit (R4 0.419 OOS came from 800+ batches "
            "against same holdout). Conditional path: run Phase 1B-alpha on "
            "top decile by soft-score only (~22 cells), with strict DEC-131 "
            "mid-run abort if agent_sharpe minus rules_sharpe < 0.0 at 25%% "
            "completion. Owner ratification required before launch."
        )
    else:
        action = ROUTING_DECISION_STOP
        band = "<0.5"
        rationale = (
            "OOS Sharpe below honest-stop floor. B882 + Contrarian Council 14 "
            "verdict: defer Phase 1B-alpha. Per PATH_TO_PHASE_1B_ALPHA.md "
            "section 10 honest fallback: re-architect via clean post-2026 "
            "forward-test window (Contrarian's prescription becomes actionable "
            "post-failure). Do NOT spend $300 Haiku budget on a sub-edge baseline."
        )

    return {
        "action": action,
        "band": band,
        "rationale": rationale,
        "sharpe_oos": sharpe_oos,
        "n_regimes_passing": n_regimes_passing,
        "passed_regimes": passed_regimes,
    }


def load_r5_summary(path: Path) -> dict[str, Any]:
    """Load R5 summary parquet/json. B895 stub - schema verification deferred to B896 when R5 lands.

    Expected schema (per cube_populator.py post-B889):
        - sharpe_oos (float)
        - max_drawdown_pct (float)
        - total_roi_pct (float)
        - sharpe_by_regime (dict[str, float])
    """
    if not path.exists():
        raise FileNotFoundError(
            f"R5 summary not found at {path}. R5 has not yet completed per "
            "PATH_TO_PHASE_1B_ALPHA.md section 1 timeline (Wed AWS run, Thu AM "
            "extraction). Use --dry-run to test decision tree on hypothetical Sharpe."
        )

    if path.suffix == ".json":
        with open(path) as f:
            data: dict[str, Any] = json.load(f)
            return data

    # Parquet path - import lazily to avoid hard dep
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("pandas required for parquet input; install or use --dry-run") from e

    df = pd.read_parquet(path)
    if "sharpe_oos" not in df.columns:
        raise KeyError(
            f"R5 summary at {path} missing required 'sharpe_oos' column. "
            f"Found columns: {list(df.columns)}. Verify cube_populator.py "
            "schema after R5 completes."
        )

    row = df.iloc[0]
    sharpe_per_regime = {}
    for col in df.columns:
        if col.startswith("sharpe_") and col not in ("sharpe_oos", "sharpe_daily"):
            regime = col.replace("sharpe_", "")
            sharpe_per_regime[regime] = float(row[col])

    return {
        "sharpe_oos": float(row["sharpe_oos"]),
        "sharpe_per_regime": sharpe_per_regime,
        "max_drawdown_pct": float(row.get("max_drawdown_pct", float("nan"))),
        "total_roi_pct": float(row.get("total_roi_pct", float("nan"))),
    }


def write_routing_decision(decision: dict[str, Any], output: Path) -> None:
    """Write routing decision JSON to output path."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(decision, f, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B882 Sharpe-band decision tree evaluator for R5 OOS routing.",
    )
    parser.add_argument(
        "--r5-summary",
        type=Path,
        help="Path to R5 summary parquet/json (omit with --dry-run).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output_audit/r5_routing_decision.json"),
        help="Output JSON path for routing decision.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test decision tree on hypothetical Sharpe (interactive).",
    )
    parser.add_argument(
        "--dry-run-sharpe",
        type=float,
        help="Hypothetical Sharpe value for --dry-run mode.",
    )
    args = parser.parse_args()

    if args.dry_run:
        sharpe = args.dry_run_sharpe if args.dry_run_sharpe is not None else 0.42
        print(f"[B895 DRY-RUN] Testing decision tree on sharpe_oos={sharpe}")
        decision = evaluate_sharpe_band(sharpe)
        print(json.dumps(decision, indent=2))
        return 0

    if args.r5_summary is None:
        print("ERROR: --r5-summary required when not in --dry-run mode", file=sys.stderr)
        return 1

    summary = load_r5_summary(args.r5_summary)
    decision = evaluate_sharpe_band(
        summary["sharpe_oos"],
        summary.get("sharpe_per_regime"),
    )
    write_routing_decision(decision, args.output)
    print(f"[B895] Routing decision written to {args.output}")
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
