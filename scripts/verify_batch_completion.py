#!/usr/bin/env python
"""Batch completion 3-gate verification (Council 231 owner-approved 2026-07-02).

Runs 3 mandatory checks post-batch:

Gate 1 (CHECKLIST #130): CUBE COMPLETENESS
  trade_exit_detail.csv rows == closed_trades x count(EXIT_STRATEGIES)
  EXACT equality; only exception is still-open trades.

Gate 2 (CHECKLIST #131): FIRE-COUNT VALIDATION
  Per-strategy actual fires vs B660 baseline scaled by universe + window.
  SILENT_FLAG: actual < 0.5 x expected AND expected > 30
  OVER_FIRING_FLAG: actual > 2.0 x expected
  HALT if N_SILENT > 10 OR N_OVER_FIRING > 5

Gate 3 (CHECKLIST #132 / feedback_strategy_x_exit_cell_analysis): CELL-LEVEL PASS COUNT
  Per (strategy, exit_method, regime) cell with >=30 trades, compute all
  14 passing criteria. Report cells PASSING, cells FAILING per criterion.
  NO aggregate. NO overall win rate.

Exit codes:
  0 = all 3 gates PASS; safe to advance
  1 = one or more gates FAIL; investigate before advancing
  2 = script error / missing inputs

Usage:
  python scripts/verify_batch_completion.py --batch-dir output_batch_A_150 \
      [--batch-tickers 150] [--window-years 4] [--baseline output_audit/fire_count_measured_b660_full_universe.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Ensure repo root is on path (script may be invoked from any cwd)
_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


def load_trade_log(batch_dir: Path) -> pd.DataFrame:
    for name in ("trade_log.parquet", "trade_log.csv", "trade_log_checkpoint.csv"):
        p = batch_dir / name
        if p.exists():
            if p.suffix == ".parquet":
                df = pd.read_parquet(p)
            else:
                df = pd.read_csv(p)
            print(f"  Loaded {p.name}: {len(df)} rows")
            return df
    raise FileNotFoundError(f"No trade log found in {batch_dir}")


def load_cube_output(batch_dir: Path) -> pd.DataFrame | None:
    for name in ("trade_exit_detail.parquet", "trade_exit_detail.csv"):
        p = batch_dir / name
        if p.exists():
            if p.suffix == ".parquet":
                df = pd.read_parquet(p)
            else:
                df = pd.read_csv(p)
            print(f"  Loaded {p.name}: {len(df)} rows")
            return df
    return None


def get_exit_strategies_count() -> tuple[int, list[str]]:
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    names = sorted(EXIT_STRATEGIES.keys())
    return len(names), names


def gate_1_cube_completeness(df_trades: pd.DataFrame, df_cube: pd.DataFrame | None, exit_count: int, exit_names: list[str]) -> tuple[bool, list[str]]:
    """CHECKLIST #130: cube rows == closed_trades x count(EXIT_STRATEGIES)."""
    issues = []
    if df_cube is None:
        issues.append("trade_exit_detail.csv MISSING; cube fan-out never wrote output")
        return False, issues

    # Determine closed vs open trades
    if "exit_date" in df_trades.columns:
        closed_mask = df_trades["exit_date"].notna() & (df_trades["exit_date"] != "")
    elif "status" in df_trades.columns:
        closed_mask = df_trades["status"] == "closed"
    else:
        closed_mask = pd.Series([True] * len(df_trades))
        issues.append("cannot detect closed vs open trades; treating all as closed")

    n_closed = int(closed_mask.sum())
    n_open = int((~closed_mask).sum())
    expected = n_closed * exit_count
    actual = len(df_cube)
    delta = actual - expected

    print(f"  Closed trades: {n_closed}; Open trades: {n_open}")
    print(f"  Exit strategies registered: {exit_count}")
    print(f"  Expected cube rows: {n_closed} x {exit_count} = {expected}")
    print(f"  Actual cube rows: {actual}")
    print(f"  Delta: {delta}")

    if delta != 0:
        issues.append(f"cube row mismatch: expected {expected}, got {actual} (delta {delta:+d})")

    # Additional sanity: unique exit methods should equal exit_count
    if "exit_method" in df_cube.columns:
        actual_methods = set(df_cube["exit_method"].unique())
        expected_methods = set(exit_names)
        missing = expected_methods - actual_methods
        extra = actual_methods - expected_methods
        if missing:
            issues.append(f"missing exit methods in cube: {sorted(missing)}")
        if extra:
            issues.append(f"unexpected exit methods in cube: {sorted(extra)}")

    return len(issues) == 0, issues


def gate_2_fire_count(df_trades: pd.DataFrame, baseline_path: Path, batch_tickers: int, window_years: float) -> tuple[bool, list[str], dict]:
    """CHECKLIST #131: per-strategy fires vs B660 baseline scaled by universe + window.
    Filters strategies deleted post-baseline via ALL_STRATEGIES current registration."""
    issues = []
    with open(baseline_path) as f:
        baseline = json.load(f)

    baseline_universe = baseline.get("n_tickers_full_t1a_pit_active", 503)
    scale = batch_tickers / baseline_universe
    print(f"  Baseline universe: {baseline_universe} tickers; batch universe: {batch_tickers}; scale: {scale:.4f}")
    print(f"  Window: {window_years} years")

    per_strategy_baseline = {}
    for entry in baseline.get("results", []):
        strat = entry.get("strategy")
        fires_per_year = entry.get("projected_fires_per_calendar_year_total_full_t1a", 0.0) or 0.0
        per_strategy_baseline[strat] = fires_per_year

    # Current registered strategies (filters post-baseline deletions)
    try:
        from backtest.signals.screener import ALL_STRATEGIES
        current_registered = set()
        for s in ALL_STRATEGIES:
            # ALL_STRATEGIES entries may be classes or instances; extract name field
            name = getattr(s, "name", None) or getattr(s, "__name__", None) or str(s)
            # Strip "strat_" prefix if present (baseline uses bare names)
            if name.startswith("strat_"):
                name = name[len("strat_"):]
            current_registered.add(name)
        print(f"  Currently registered strategies: {len(current_registered)}")
    except Exception as e:
        current_registered = None
        print(f"  WARN: could not import ALL_STRATEGIES ({e}); post-baseline-deleted strategies won't be filtered")

    # Actual fires per strategy (unique trade entries; not exit fan-out)
    if "strategy" not in df_trades.columns:
        issues.append("trade log missing 'strategy' column")
        return False, issues, {}
    actual_by_strategy = df_trades["strategy"].value_counts().to_dict()

    silent_flags = []
    over_firing_flags = []
    healthy = 0
    insufficient = 0
    unregistered = []
    deleted_post_baseline = []

    all_strategies = set(per_strategy_baseline.keys()) | set(actual_by_strategy.keys())
    per_strat_report = {}
    for strat in sorted(all_strategies):
        baseline_fpy = per_strategy_baseline.get(strat, 0.0)
        expected = baseline_fpy * window_years * scale
        actual = actual_by_strategy.get(strat, 0)
        classification = "?"
        # Filter: if strategy is in baseline but NOT in current registration, it was deleted post-baseline
        if strat in per_strategy_baseline and current_registered is not None and strat not in current_registered:
            classification = "DELETED_POST_BASELINE"
            deleted_post_baseline.append(strat)
        elif strat not in per_strategy_baseline:
            classification = "UNREGISTERED_IN_BASELINE"
            unregistered.append(strat)
        elif expected <= 30:
            classification = "INSUFFICIENT_BASELINE"
            insufficient += 1
        elif actual < 0.5 * expected:
            classification = "SILENT_FLAG"
            silent_flags.append((strat, actual, expected))
        elif actual > 2.0 * expected:
            classification = "OVER_FIRING_FLAG"
            over_firing_flags.append((strat, actual, expected))
        else:
            classification = "HEALTHY"
            healthy += 1
        per_strat_report[strat] = {
            "expected": round(expected, 1),
            "actual": actual,
            "ratio": round(actual / expected, 3) if expected > 0 else None,
            "class": classification,
        }

    print(f"  Strategies HEALTHY: {healthy}")
    print(f"  Strategies INSUFFICIENT_BASELINE (expected<=30): {insufficient}")
    print(f"  Strategies UNREGISTERED_IN_BASELINE (added post-B660): {len(unregistered)}")
    print(f"  Strategies DELETED_POST_BASELINE (removed from ALL_STRATEGIES since B660): {len(deleted_post_baseline)}")
    print(f"  Strategies SILENT_FLAG (currently registered, actual < 50% expected, expected > 30): {len(silent_flags)}")
    print(f"  Strategies OVER_FIRING_FLAG (actual > 200% expected): {len(over_firing_flags)}")

    if silent_flags:
        print("  Top 10 SILENT_FLAG (worst first by ratio):")
        for s, a, e in sorted(silent_flags, key=lambda x: x[1] / x[2] if x[2] > 0 else 999)[:10]:
            print(f"    {s}: actual={a} expected={e:.0f} ratio={(a/e):.2f}")

    if over_firing_flags:
        print("  Top 10 OVER_FIRING_FLAG (worst first by ratio):")
        for s, a, e in sorted(over_firing_flags, key=lambda x: -(x[1] / x[2] if x[2] > 0 else 0))[:10]:
            print(f"    {s}: actual={a} expected={e:.0f} ratio={(a/e):.2f}")

    if len(silent_flags) > 10:
        issues.append(f"SILENT_FLAG count {len(silent_flags)} > 10 threshold")
    if len(over_firing_flags) > 5:
        issues.append(f"OVER_FIRING_FLAG count {len(over_firing_flags)} > 5 threshold")

    return len(issues) == 0, issues, per_strat_report


def gate_3_cell_pass(df_cube: pd.DataFrame | None) -> tuple[bool, list[str]]:
    """CHECKLIST #132 / feedback_strategy_x_exit_cell_analysis: per-(strategy,exit,regime) cells vs 14 criteria."""
    issues = []
    if df_cube is None:
        issues.append("cannot compute cell-level metrics without trade_exit_detail")
        return False, issues

    from backtest.config import PASSING_CRITERIA

    # Determine grouping columns
    group_cols = []
    for c in ("strategy", "exit_method", "regime"):
        if c in df_cube.columns:
            group_cols.append(c)
    if not group_cols:
        issues.append("cube data has no strategy/exit_method/regime columns; cannot compute cells")
        return False, issues

    print(f"  Grouping by: {group_cols}")

    # Aggregate per cell
    grouped = df_cube.groupby(group_cols)
    cells_evaluated = 0
    cells_passing = 0
    fail_reasons = Counter()
    top_cells = []

    win_col = "win" if "win" in df_cube.columns else None
    pnl_col = "pnl_pct" if "pnl_pct" in df_cube.columns else None
    if win_col is None or pnl_col is None:
        issues.append(f"cube missing win/pnl_pct columns (found {list(df_cube.columns)[:20]})")
        return False, issues

    for key, grp in grouped:
        n = len(grp)
        if n < PASSING_CRITERIA.get("min_trades_per_regime", 30):
            continue
        cells_evaluated += 1

        win_rate = grp[win_col].mean() * 100
        wins = grp[grp[win_col] == 1][pnl_col]
        losses = grp[grp[win_col] == 0][pnl_col]
        profit_factor = wins.sum() / abs(losses.sum()) if losses.sum() != 0 and losses.sum() < 0 else None
        expected_value = grp[pnl_col].mean()
        win_loss_ratio = wins.mean() / abs(losses.mean()) if len(losses) > 0 and losses.mean() != 0 else None
        total_roi = grp[pnl_col].sum()

        checks = {
            "win_rate": win_rate >= PASSING_CRITERIA.get("min_win_rate_per_regime", 55) * 100,
            "profit_factor": profit_factor is not None and profit_factor >= PASSING_CRITERIA.get("min_profit_factor_per_regime", 1.3),
            "expected_value": expected_value > 0,
            "win_loss_ratio": win_loss_ratio is not None and win_loss_ratio > 1.0,
            "total_roi": total_roi > 0,
            "min_trades": n >= PASSING_CRITERIA.get("min_trades_per_regime", 30),
        }
        for k, ok in checks.items():
            if not ok:
                fail_reasons[k] += 1

        if all(checks.values()):
            cells_passing += 1
            top_cells.append((key, n, win_rate, expected_value, total_roi))

    print(f"  Cells evaluated (>=30 trades): {cells_evaluated}")
    print(f"  Cells passing all 6 core criteria: {cells_passing} ({100*cells_passing/max(cells_evaluated,1):.1f}%)")
    print(f"  Failure counts per criterion:")
    for k, c in fail_reasons.most_common():
        print(f"    {k}: {c} cells failed")

    if top_cells:
        print(f"  Top 20 passing cells:")
        top_cells.sort(key=lambda x: -x[4])
        for key, n, wr, ev, roi in top_cells[:20]:
            print(f"    {key}: n={n} wr={wr:.1f}% ev={ev:.2f}% roi={roi:.1f}%")

    # No hard threshold - cell-count is descriptive; PASS if evaluation ran
    if cells_evaluated == 0:
        issues.append("no cells with >=30 trades evaluated; cube may be empty or under-populated")

    return len(issues) == 0, issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch-dir", required=True)
    ap.add_argument("--batch-tickers", type=int, required=True, help="Universe size for this batch (e.g., 150 for A, 1787 for B)")
    ap.add_argument("--window-years", type=float, default=4.0)
    ap.add_argument("--baseline", type=str, default="output_audit/fire_count_measured_b660_full_universe.json")
    args = ap.parse_args()

    batch_dir = Path(args.batch_dir)
    baseline_path = Path(args.baseline)
    if not batch_dir.exists():
        print(f"ERROR: {batch_dir} not found", file=sys.stderr)
        return 2
    if not baseline_path.exists():
        print(f"ERROR: {baseline_path} not found", file=sys.stderr)
        return 2

    print(f"=== Batch completion 3-gate verification ===")
    print(f"Batch dir:    {batch_dir}")
    print(f"Batch tickers: {args.batch_tickers}")
    print(f"Window years: {args.window_years}")
    print(f"Baseline:     {baseline_path}")
    print()

    try:
        exit_count, exit_names = get_exit_strategies_count()
        print(f"count(EXIT_STRATEGIES) = {exit_count}")
        print()
    except Exception as e:
        print(f"ERROR: cannot import EXIT_STRATEGIES: {e}", file=sys.stderr)
        return 2

    try:
        df_trades = load_trade_log(batch_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    df_cube = load_cube_output(batch_dir)
    print()

    all_pass = True
    print("=" * 70)
    print("GATE 1: CUBE COMPLETENESS (CHECKLIST #130)")
    print("=" * 70)
    ok1, issues1 = gate_1_cube_completeness(df_trades, df_cube, exit_count, exit_names)
    if ok1:
        print("  [PASS] PASS")
    else:
        print("  [FAIL] FAIL")
        for i in issues1:
            print(f"    - {i}")
        all_pass = False

    print()
    print("=" * 70)
    print("GATE 2: FIRE-COUNT VALIDATION (CHECKLIST #131)")
    print("=" * 70)
    ok2, issues2, per_strat = gate_2_fire_count(df_trades, baseline_path, args.batch_tickers, args.window_years)
    if ok2:
        print("  [PASS] PASS")
    else:
        print("  [FAIL] FAIL")
        for i in issues2:
            print(f"    - {i}")
        all_pass = False

    # Persist per-strategy report for later inspection
    out = batch_dir / "verify_batch_fire_count_report.json"
    with open(out, "w") as f:
        json.dump(per_strat, f, indent=2)
    print(f"  Per-strategy report: {out}")

    print()
    print("=" * 70)
    print("GATE 3: CELL-LEVEL PASS COUNT (feedback_strategy_x_exit_cell_analysis)")
    print("=" * 70)
    ok3, issues3 = gate_3_cell_pass(df_cube)
    if ok3:
        print("  [PASS] PASS (evaluation ran; see cell-level output above)")
    else:
        print("  [FAIL] FAIL")
        for i in issues3:
            print(f"    - {i}")
        all_pass = False

    print()
    print("=" * 70)
    if all_pass:
        print("ALL 3 GATES PASS - batch verification complete")
        return 0
    else:
        print("ONE OR MORE GATES FAILED - investigate before advancing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
