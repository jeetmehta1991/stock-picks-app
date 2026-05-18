"""Empirical PBO check on the current trade log.

Batch 228 (housekeeping 2026-05-18 owner-approved). Computes the
Probability of Backtest Overfitting (PBO) across the active strategy
roster from the most recent backtest output. Source: Bailey-Borwein-
Lopez de Prado-Zhu 2017 *Journal of Computational Finance*.

Usage:
    python scripts/run_pbo_check.py [--source DIR] [--n-partitions 16]

Reads:
    {source}/trade_log.csv

Outputs:
    {source}/pbo_check.json    structured result
    + console summary

Interpretation:
    PBO < 0.4  -> "ok"        roster not overfit (IS winners tend to
                              OOS-win)
    0.4 <= PBO < 0.6 -> "warning"  borderline
    PBO >= 0.6 -> "overfit"   IS winners are no better than random OOS;
                              strategy selection process is broken

Run this BEFORE the final Phase 1A-beta rerun (Batch 225) to confirm
the current roster is not overfit. If PBO >= 0.6, deprecate more
strategies before rerun (a la Batch 218).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Add repo root to sys.path so backtest module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.results.cpcv import compute_pbo_cscv


def build_perf_matrix(trade_log: pd.DataFrame) -> pd.DataFrame:
    """Build per-strategy daily returns matrix from trade log.

    Rows = trade exit dates; columns = strategy names; values = pnl_pct.
    Trades from the same strategy on the same exit date are summed
    (aggregate exposure that day). Strategies with fewer than 30 trades
    are excluded (PBO needs reasonable per-strategy sample).
    """
    if trade_log is None or trade_log.empty:
        return pd.DataFrame()
    df = trade_log.copy()
    if "exit_date" not in df.columns or "pnl_pct" not in df.columns or "strategy" not in df.columns:
        return pd.DataFrame()
    df["__d__"] = pd.to_datetime(df["exit_date"]).dt.normalize()
    # Filter to strategies with >= 30 trades
    counts = df["strategy"].value_counts()
    eligible = counts[counts >= 30].index.tolist()
    df = df[df["strategy"].isin(eligible)]
    if df.empty:
        return pd.DataFrame()
    pivot = (
        df.groupby(["__d__", "strategy"])["pnl_pct"]
        .sum()
        .unstack(fill_value=0.0)
        .sort_index()
    )
    return pivot


def run_pbo_check(source_dir: Path, n_partitions: int = 16) -> dict:
    """Main entry point: load trade log, compute PBO, persist + print."""
    source_dir = Path(source_dir)
    trade_log_path = source_dir / "trade_log.csv"
    if not trade_log_path.exists():
        print(f"[FAIL] trade_log.csv missing at {trade_log_path}")
        return {"pbo": None, "interpretation": "trade_log_missing"}
    trade_log = pd.read_csv(trade_log_path)
    print(f"Loaded {len(trade_log):,} trades from {trade_log_path}")
    perf = build_perf_matrix(trade_log)
    print(f"Built perf matrix: {perf.shape} (rows=days, cols=strategies)")
    if perf.empty or perf.shape[1] < 2:
        result = {
            "pbo": None,
            "interpretation": "insufficient_strategies",
            "perf_shape": list(perf.shape),
            "verdict": "n/a",
        }
    else:
        result = compute_pbo_cscv(perf, n_partitions=n_partitions)
        result["perf_shape"] = list(perf.shape)
        result["strategies_evaluated"] = list(perf.columns)
        result["source_dir"] = str(source_dir)
        result["trade_count"] = int(len(trade_log))
    # Persist
    out_path = source_dir / "pbo_check.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    # Console summary
    print()
    print("=" * 60)
    print("PBO CHECK RESULT")
    print("=" * 60)
    print(f"  PBO:            {result.get('pbo')}")
    print(f"  Interpretation: {result.get('interpretation')}")
    print(f"  Verdict:        {result.get('verdict')}")
    print(f"  N combinations: {result.get('n_combinations', 'n/a')}")
    print(f"  Strategies:     {len(result.get('strategies_evaluated', []))}")
    print(f"  Output:         {out_path}")
    return result


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compute PBO (Probability of Backtest Overfitting) "
                    "on the current trade log via CSCV.")
    p.add_argument(
        "--source", type=str,
        default="output_phase_1a_beta_merged",
        help="Directory containing trade_log.csv (default: "
             "output_phase_1a_beta_merged)",
    )
    p.add_argument(
        "--n-partitions", type=int, default=16,
        help="CSCV partitions (Bailey 2017 default 16; must be even)",
    )
    return p


if __name__ == "__main__":
    args = _build_parser().parse_args()
    result = run_pbo_check(Path(args.source), n_partitions=args.n_partitions)
    sys.exit(0 if result.get("pbo") is not None else 1)
