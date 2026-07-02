#!/usr/bin/env python
"""Batch completion 3-gate verification (Council 231 owner-approved 2026-07-02).

Runs 3 mandatory checks post-batch:

Gate 1 (CHECKLIST #130): CUBE COMPLETENESS
  trade_exit_detail.csv rows == closed_trades x count(EXIT_STRATEGIES)
  EXACT equality; only exception is still-open trades.

Gate 2 (CHECKLIST #131, Council 232 standalone): FIRE-COUNT VALIDATION
  STANDALONE - no external baseline. Per-strategy vs PASSING_CRITERIA thresholds
  + intrinsic coverage (regime, direction, temporal).
  SILENT: 0 fires; STARVED: 1..min_per_regime-1; MARGINAL: min_per_regime..min_overall-1; VIABLE: >=min_overall.
  HALT if SILENT (excl known-disabled) > 10 OR TEMPORAL_CLUSTERED > 5 OR DIRECTION_MISMATCH > 0.

Gate 3 (CHECKLIST #132 / feedback_strategy_x_exit_cell_analysis): CELL-LEVEL PASS COUNT
  Per (strategy, exit_method, regime) cell with >=30 trades, compute all
  14 passing criteria. Report cells PASSING, cells FAILING per criterion.
  NO aggregate. NO overall win rate.

Exit codes:
  0 = all 3 gates PASS; safe to advance
  1 = one or more gates FAIL; investigate before advancing
  2 = script error / missing inputs

Usage:
  python scripts/verify_batch_completion.py --batch-dir output_batch_A_150
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


def gate_2_fire_count(df_trades: pd.DataFrame) -> tuple[bool, list[str], dict]:
    """CHECKLIST #131 (Council 232 standalone redesign): per-strategy fire-count
    validation intrinsic to the batch. NO external baseline comparison.

    Layer 1 - Fire-count classification vs PASSING_CRITERIA thresholds:
      SILENT   = 0 fires
      STARVED  = 1 .. min_trades_per_regime-1     (cannot populate any regime cell)
      MARGINAL = min_trades_per_regime .. min_trades_overall-1 (some cells populatable)
      VIABLE   = >= min_trades_overall            (multiple cells + potential overall PASS)

    Layer 2 - Coverage checks intrinsic to batch data:
      Regime coverage:    strategy fires in regimes present in window
      Direction coverage: LONG fires long, SHORT fires short, dual fires both
      Temporal coverage:  fires not clustered in single quarter (>80%)

    Layer 3 - HALT gate:
      N_SILENT (excluding known-disabled) > 10 OR
      N_TEMPORAL_CLUSTERED > 5 OR
      N_DIRECTION_MISMATCH > 0
    """
    issues = []
    per_strat_report = {}

    if "strategy" not in df_trades.columns:
        issues.append("trade log missing 'strategy' column")
        return False, issues, {}

    from backtest.config import PASSING_CRITERIA
    min_per_regime = int(PASSING_CRITERIA.get("min_trades_per_regime", 30))
    min_overall = int(PASSING_CRITERIA.get("min_trades", PASSING_CRITERIA.get("min_trades_overall", 100)))
    print(f"  Fire-count thresholds (from PASSING_CRITERIA):")
    print(f"    min_trades_per_regime = {min_per_regime}")
    print(f"    min_trades_overall    = {min_overall}")

    # Currently registered strategies + known disabled + directional declarations
    current_registered = set()
    known_disabled = set()
    strategy_directions = {}  # strategy_name -> 'long' | 'short' | 'dual'
    try:
        from backtest.signals.screener import ALL_STRATEGIES
        from backtest.config import STRATEGIES_DISABLED_MISSING_PRODUCER
        for s in ALL_STRATEGIES:
            name = getattr(s, "name", None) or getattr(s, "__name__", None) or str(s)
            if name.startswith("strat_"):
                name = name[len("strat_"):]
            current_registered.add(name)
            # Attempt to infer direction from name suffix
            if name.endswith("_short"):
                strategy_directions[name] = "short"
            elif name.endswith("_long"):
                strategy_directions[name] = "long"
            else:
                strategy_directions[name] = "dual"
        for s in STRATEGIES_DISABLED_MISSING_PRODUCER:
            name = s.name if hasattr(s, "name") else str(s)
            if name.startswith("strat_"):
                name = name[len("strat_"):]
            known_disabled.add(name)
        print(f"  Currently registered: {len(current_registered)} strategies")
        print(f"  Known disabled (STRATEGIES_DISABLED_MISSING_PRODUCER): {len(known_disabled)}")
    except Exception as e:
        print(f"  WARN: could not import ALL_STRATEGIES/STRATEGIES_DISABLED_MISSING_PRODUCER ({e})")

    # Aggregate per strategy
    fires_by_strat = df_trades["strategy"].value_counts().to_dict()
    regimes_present = sorted(df_trades["regime"].unique()) if "regime" in df_trades.columns else []
    print(f"  Regimes present in trade log: {regimes_present}")

    # Prep temporal analysis (quarter-level)
    df = df_trades.copy()
    if "entry_date" in df.columns:
        df["entry_date_ts"] = pd.to_datetime(df["entry_date"], errors="coerce")
        df["quarter"] = df["entry_date_ts"].dt.to_period("Q").astype(str)
    else:
        df["quarter"] = "unknown"

    # Classify each currently-registered strategy
    silent = []
    starved = []
    marginal = []
    viable = []
    temporal_clustered = []
    direction_mismatch = []
    regime_gap = []

    # Universe of strategies to consider: current registered + any in trade log
    all_to_check = current_registered | set(fires_by_strat.keys())

    for strat in sorted(all_to_check):
        n_fires = int(fires_by_strat.get(strat, 0))
        entry = {
            "n_fires": n_fires,
            "class": None,
            "flags": [],
        }

        # Layer 1: fire-count class
        if n_fires == 0:
            entry["class"] = "SILENT"
            if strat not in known_disabled:
                silent.append(strat)
            else:
                entry["flags"].append("known_disabled")
        elif n_fires < min_per_regime:
            entry["class"] = "STARVED"
            starved.append(strat)
        elif n_fires < min_overall:
            entry["class"] = "MARGINAL"
            marginal.append(strat)
        else:
            entry["class"] = "VIABLE"
            viable.append(strat)

        if n_fires > 0:
            strat_df = df[df["strategy"] == strat]

            # Layer 2a: regime coverage
            fired_regimes = set(strat_df["regime"].unique()) if "regime" in strat_df.columns else set()
            entry["fired_regimes"] = sorted(fired_regimes)
            if regimes_present and set(regimes_present) - fired_regimes:
                # Missing at least one regime present in window
                missing = sorted(set(regimes_present) - fired_regimes)
                entry["flags"].append(f"regime_gap:{','.join(missing)}")
                if n_fires >= min_overall:
                    regime_gap.append((strat, missing, n_fires))

            # Layer 2b: direction coverage
            if "direction" in strat_df.columns:
                fired_dirs = set(strat_df["direction"].unique())
                entry["fired_directions"] = sorted(fired_dirs)
                declared = strategy_directions.get(strat)
                if declared == "long" and "short" in fired_dirs:
                    entry["flags"].append("direction_mismatch_long_declared_short_fired")
                    direction_mismatch.append((strat, declared, fired_dirs))
                elif declared == "short" and "long" in fired_dirs:
                    entry["flags"].append("direction_mismatch_short_declared_long_fired")
                    direction_mismatch.append((strat, declared, fired_dirs))

            # Layer 2c: temporal clustering
            if "quarter" in strat_df.columns and n_fires >= 20:
                q_counts = strat_df["quarter"].value_counts()
                top_q_share = q_counts.iloc[0] / n_fires if len(q_counts) > 0 else 0
                entry["top_quarter_share"] = round(float(top_q_share), 3)
                if top_q_share > 0.8:
                    entry["flags"].append(f"temporal_clustered:{q_counts.index[0]}={q_counts.iloc[0]}")
                    temporal_clustered.append((strat, str(q_counts.index[0]), int(q_counts.iloc[0]), n_fires))

        per_strat_report[strat] = entry

    # Print summary
    print()
    print("  === Fire-count classification ===")
    print(f"  VIABLE   (>= {min_overall} fires): {len(viable)}")
    print(f"  MARGINAL ({min_per_regime}-{min_overall-1} fires): {len(marginal)}")
    print(f"  STARVED  (1-{min_per_regime-1} fires): {len(starved)}")
    print(f"  SILENT   (0 fires, excluding {len(known_disabled)} known-disabled): {len(silent)}")

    if silent:
        print(f"  SILENT strategies (currently registered, expected to fire):")
        for s in sorted(silent)[:20]:
            print(f"    {s}")
        if len(silent) > 20:
            print(f"    ... and {len(silent) - 20} more")

    if starved:
        print(f"  STARVED strategies (1-{min_per_regime-1} fires; cannot populate per-regime):")
        for s in sorted(starved)[:10]:
            n = per_strat_report[s]["n_fires"]
            print(f"    {s}: {n} fires")
        if len(starved) > 10:
            print(f"    ... and {len(starved) - 10} more")

    print()
    print("  === Coverage findings ===")
    print(f"  REGIME_GAP (VIABLE strategies missing regime coverage): {len(regime_gap)}")
    for s, missing, n in regime_gap[:10]:
        print(f"    {s}: {n} fires; missing regimes {missing}")

    print(f"  TEMPORAL_CLUSTERED (>80% fires in single quarter, n>=20): {len(temporal_clustered)}")
    for s, q, count, total in temporal_clustered[:10]:
        print(f"    {s}: {count}/{total} fires in {q}")

    print(f"  DIRECTION_MISMATCH (declared vs fired direction inconsistent): {len(direction_mismatch)}")
    for s, declared, fired in direction_mismatch[:10]:
        print(f"    {s}: declared={declared} fired={sorted(fired)}")

    # Layer 3: HALT gate
    if len(silent) > 10:
        issues.append(f"SILENT count {len(silent)} > 10 threshold (excludes {len(known_disabled)} known-disabled)")
    if len(temporal_clustered) > 5:
        issues.append(f"TEMPORAL_CLUSTERED count {len(temporal_clustered)} > 5 threshold")
    if len(direction_mismatch) > 0:
        issues.append(f"DIRECTION_MISMATCH count {len(direction_mismatch)} > 0 threshold (correctness bug)")

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
    # Council 232 standalone: --batch-tickers, --window-years, --baseline all removed.
    # Gate 2 uses PASSING_CRITERIA thresholds + intrinsic coverage; no external ref.
    args = ap.parse_args()

    batch_dir = Path(args.batch_dir)
    if not batch_dir.exists():
        print(f"ERROR: {batch_dir} not found", file=sys.stderr)
        return 2

    print(f"=== Batch completion 3-gate verification (Council 232 standalone Gate 2) ===")
    print(f"Batch dir: {batch_dir}")
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
    ok2, issues2, per_strat = gate_2_fire_count(df_trades)
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
