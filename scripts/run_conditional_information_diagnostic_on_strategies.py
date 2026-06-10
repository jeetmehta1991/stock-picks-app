"""B687 follow-on integration scaffold: run the conditional-information
gate diagnostic on actual strategies' gate signals + cube forward returns.

Per B687 external reviewer's stated next action:
  "Running this on T3 and T8 first (the two the trend doc cleared) is
  the cheapest way to confirm whether the cluster verdicts need revising
  before more clusters are walked on the same flawed criterion."

This script wires the B687 diagnostic to the cube's actual gate-signal
panel + forward-return data. Reads a parquet from output_audit (or any
specified path) that emits one row per (ticker, bar, strategy) cell
containing:
  - gate_name_1, gate_name_2, ...: boolean gate values
  - forward_return_Nday: realized forward return at N-day hold

Output: JSON report per strategy with per-gate verdict + strategy-level
verdict + recommended_core_gates.

CAVEATS (load-bearing, not boilerplate):
  - Diagnostic is PENDING-B660 + PENDING-cube-replay until B668's
    cube_compose_verdict.csv is populated with real return data.
    Until then this script runs on whatever forward-return panel is
    supplied; if that panel is biased (survivorship-uncorrected,
    cost-unadjusted, PIT-leaky) so is the diagnostic output.
  - First-priority targets per reviewer: T3 (hull_rsi) + T8
    (ichimoku_cloud_breakout) + post-fix W8 (cpr_narrow_tight). The
    --strategies flag lets owner add more once T3/T8/W8 verdicts return.
  - Smart-money cluster's Pattern F audit (S5-13F-SLEEVE-MARGINAL-
    CONTRIBUTION-TEST) is the next obvious target; the 13F sleeve
    "honest confluence" question is the same shape as T3/T8.

USAGE:
  Once cube data lands:

    python scripts/run_conditional_information_diagnostic_on_strategies.py \\
        --gate-panel output_audit/cube_gate_signal_panel.parquet \\
        --return-col forward_return_5day \\
        --strategies hull_rsi ichimoku_cloud_breakout cpr_narrow_tight \\
        --output output_audit/b687_diagnostic_t3_t8_w8.json

  Or to run on the full cluster:

    python scripts/run_conditional_information_diagnostic_on_strategies.py \\
        --gate-panel output_audit/cube_gate_signal_panel.parquet \\
        --return-col forward_return_5day \\
        --cluster trend \\
        --output output_audit/b687_diagnostic_trend_cluster.json

INTEGRATION TARGET (post-B660):
  - cube_compose_verdict.py B668 emits per-cell verdict + recommended
    multi-testing correction. The B687 diagnostic complements that by
    running BEFORE the cube selection step on the gate signals, so
    redundant gates are pruned (or strategies recommended for
    deprecation) PRIOR to the multi-testing correction inflating the
    family-size N with redundant hypothesis-test slots.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import numpy as np

from backtest.engine.conditional_information_gate_diagnostic import (
    StrategyDiagnosticResult,
    diagnose_strategy,
)


log = logging.getLogger(__name__)


# Strategy -> gate signal names. For T3/T8/W8 these come from the walk
# docs' Step 1 code-reads. Updated as new strategies become candidates
# for diagnostic application post-B660.
STRATEGY_GATES: dict[str, list[str]] = {
    # T3 hull_rsi (post-B656 4-gate per direction; LONG side shown)
    "hull_rsi": [
        "hull_bullish",
        "price_above_hull",
        "rsi_14_above_50",
        "price_above_ema_200",
    ],
    # T8 ichimoku_cloud_breakout (LONG side, 4-gate)
    "ichimoku_cloud_breakout": [
        "ichi_above_cloud",
        "tk_cross_up",
        "weekly_above_cloud",
        "price_above_ema_200",
    ],
    # W8 cpr_narrow_bullish post-B654 (4-gate)
    "cpr_narrow_bullish": [
        "cpr_narrow_tight",
        "above_cpr",
        "above_avwap_50low",
        "price_above_ema_200",
    ],
}

# Cluster -> strategy list (for --cluster flag convenience)
CLUSTER_STRATEGIES: dict[str, list[str]] = {
    "trend": [
        "hull_rsi",
        "ichimoku_cloud_breakout",
        # T1/T2/T6/T9/T10 gates will be added as cube data lands per
        # reviewer Finding #4 cluster-internal collinearity audit
    ],
    "pivot": [
        "cpr_narrow_bullish",
        # W1-W10 added as cube data lands
    ],
}


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run B687 conditional-information gate diagnostic on strategies"
    )
    parser.add_argument(
        "--gate-panel", type=Path, required=True,
        help="Path to parquet with one row per (ticker, bar, strategy) cell "
             "containing gate boolean columns + forward-return column."
    )
    parser.add_argument(
        "--return-col", type=str, required=True,
        help="Column name in the gate panel for the forward-return."
    )
    parser.add_argument(
        "--strategies", nargs="+", default=None,
        help="Explicit list of strategy names to diagnose. Each must "
             "have an entry in STRATEGY_GATES (or supply --gate-names)."
    )
    parser.add_argument(
        "--cluster", type=str, default=None, choices=list(CLUSTER_STRATEGIES.keys()),
        help="Run on all strategies in this cluster (alternative to --strategies)."
    )
    parser.add_argument(
        "--gate-names", nargs="+", default=None,
        help="Override STRATEGY_GATES lookup for a single strategy "
             "(use with --strategies pointing to one name)."
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="JSON output path for the diagnostic report."
    )
    parser.add_argument(
        "--strategy-col", type=str, default="strategy",
        help="Column name identifying the strategy in the gate panel "
             "(default: 'strategy')."
    )
    parser.add_argument("--z-hi", type=float, default=2.0)
    parser.add_argument("--true-rate-no-op", type=float, default=0.98)
    parser.add_argument("--min-n", type=int, default=30)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def _serialize_result(result: StrategyDiagnosticResult) -> dict:
    """Convert StrategyDiagnosticResult dataclass to JSON-safe dict."""
    return {
        "verdict": result.verdict,
        "recommended_core_gates": result.recommended_core_gates,
        "notes": result.notes,
        "per_gate": [asdict(g) for g in result.per_gate],
    }


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Resolve strategy list
    if args.cluster is not None:
        strategies = list(CLUSTER_STRATEGIES[args.cluster])
    elif args.strategies is not None:
        strategies = list(args.strategies)
    else:
        log.error("Specify either --strategies or --cluster")
        return 2

    # Lazy import pandas (heavy)
    try:
        import pandas as pd
    except ImportError:
        log.error("pandas is required for parquet read")
        return 2

    log.info("Loading gate panel from %s", args.gate_panel)
    if not args.gate_panel.exists():
        log.error(
            "Gate panel not found: %s\n"
            "PENDING-B660 + PENDING-cube-replay: this script expects "
            "the cube's per-cell gate-signal + forward-return panel which "
            "will be emitted by post-B660 cube replay via B668's "
            "cube_compose_verdict.py extension. Until then run with a "
            "synthetic panel for smoke-testing (see "
            "test_batch687_conditional_information_diagnostic.py for "
            "labeled-case generators).",
            args.gate_panel,
        )
        return 1

    df = pd.read_parquet(args.gate_panel)
    log.info("Gate panel: %d rows, %d cols", len(df), len(df.columns))

    if args.return_col not in df.columns:
        log.error(
            "Return column %r not in panel. Available: %s",
            args.return_col, list(df.columns)[:20],
        )
        return 2

    if args.strategy_col not in df.columns:
        log.error(
            "Strategy column %r not in panel. Available: %s",
            args.strategy_col, list(df.columns)[:20],
        )
        return 2

    report: dict[str, dict] = {
        "diagnostic_module": "backtest/engine/conditional_information_gate_diagnostic.py",
        "diagnostic_version": "B687-final-direct-conditional-comparison",
        "z_hi": args.z_hi,
        "true_rate_no_op": args.true_rate_no_op,
        "min_n": args.min_n,
        "gate_panel": str(args.gate_panel),
        "return_col": args.return_col,
        "PENDING_B660_caveat": (
            "Outputs are PENDING-B660 + PENDING-cube-replay until cube_compose_"
            "verdict.csv is populated with cost-adjusted (C6), survivorship-"
            "corrected (C5), PIT-clean forward returns. Until then results "
            "inherit the same biases as the underlying return panel."
        ),
        "strategies": {},
    }

    for strat in strategies:
        if args.gate_names is not None and len(strategies) == 1:
            gate_names = args.gate_names
        elif strat in STRATEGY_GATES:
            gate_names = STRATEGY_GATES[strat]
        else:
            log.warning(
                "Strategy %r not in STRATEGY_GATES; supply --gate-names "
                "or add to STRATEGY_GATES dict. Skipping.",
                strat,
            )
            report["strategies"][strat] = {
                "verdict": "SKIPPED",
                "reason": "gate_names not configured",
            }
            continue

        sub = df[df[args.strategy_col] == strat]
        if sub.empty:
            log.warning("No rows for strategy %r in panel; skipping", strat)
            report["strategies"][strat] = {
                "verdict": "SKIPPED",
                "reason": "no rows in panel",
            }
            continue

        missing = [g for g in gate_names if g not in sub.columns]
        if missing:
            log.warning(
                "Missing gate columns for %r: %s; skipping", strat, missing
            )
            report["strategies"][strat] = {
                "verdict": "SKIPPED",
                "reason": f"missing gate columns: {missing}",
            }
            continue

        gate_matrix = sub[gate_names].fillna(False).to_numpy().astype(bool)
        returns = sub[args.return_col].fillna(0.0).to_numpy().astype(float)

        log.info(
            "Diagnosing %s: n_rows=%d, n_gates=%d",
            strat, gate_matrix.shape[0], gate_matrix.shape[1],
        )
        try:
            result = diagnose_strategy(
                gate_matrix=gate_matrix,
                forward_returns=returns,
                gate_names=gate_names,
                true_rate_no_op=args.true_rate_no_op,
                z_hi=args.z_hi,
                min_n=args.min_n,
            )
        except Exception as e:
            log.exception("Diagnostic failed on %r: %s", strat, e)
            report["strategies"][strat] = {
                "verdict": "ERROR",
                "reason": str(e),
            }
            continue

        report["strategies"][strat] = _serialize_result(result)
        log.info(
            "  -> strategy_verdict=%s | core=%s | %s",
            result.verdict,
            result.recommended_core_gates,
            result.notes,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    log.info("Wrote diagnostic report to %s", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
