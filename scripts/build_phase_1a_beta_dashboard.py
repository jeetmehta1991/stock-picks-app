"""Build dashboard_phase_1a_beta/data.json from the Phase 1A-beta run output.

Source: per CHECKLIST #77 canonical-source attribution. Owner directive
2026-05-24 (Batch 313): build a per-(strategy x exit x regime x classifier)
dashboard so the cube can be explored visually.

Reads: output_phase_1a_beta_merged_local/{trade_log.csv, per_cell_is_oos.csv,
per_strategy_is_oos.csv, backtest_results.csv, walk_forward_validation.csv}

Writes: dashboard_phase_1a_beta/data.json (~5-10 MB) with pre-computed cube
slices indexed by classifier so the front-end can filter without re-reducing
the 7,191-trade trade_log.

Cube dimensions surfaced:
  - strategy (66)
  - exit_reason (17)
  - regime (3: bull / bear / neutral)
  - sector (11 GICS)
  - direction (long / short)
  - confidence_tier (LOW..EXCEPTIONAL)

Per-cell aggregates: n_trades, wins, win_rate, mean_pnl_pct, sum_pnl_pct,
median_hold_days, best/worst trade, IS vs OOS split.

Owner framework (per directive 2026-05-24): we are NOT looking for universal
strategies. The dashboard surfaces best (strategy x exit x classifier) combos
per regime/sector/etc. - the per-classifier cube the user described as
"the best combinations for each regime, ticker, all other variables".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))  # so `from backtest.signals.screener import ...` works
IN_DIR = REPO / "output_phase_1a_beta_merged_local"
OUT_DIR = REPO / "dashboard_phase_1a_beta"

IS_END = pd.Timestamp("2024-06-30")
OOS_START = pd.Timestamp("2024-07-01")


def _generate_is_oos_csvs(trade_log: pd.DataFrame, out_dir: Path) -> None:
    """Batch 376: generate per_cell_is_oos.csv + per_strategy_is_oos.csv
    from trade_log when those files are missing (single-batch outputs
    don't always emit them). Idempotent - skips if files already exist."""
    pcio = out_dir / "per_cell_is_oos.csv"
    psio = out_dir / "per_strategy_is_oos.csv"
    if pcio.exists() and psio.exists():
        return
    tl = trade_log.copy()
    tl["entry_dt"] = pd.to_datetime(tl["entry_date"], errors="coerce")
    tl["is_in_sample"] = tl["entry_dt"] <= IS_END
    # per_cell = strategy x exit_reason x regime
    if "exit_reason" in tl.columns:
        groups = ["strategy", "exit_reason", "regime"]
    else:
        groups = ["strategy", "regime"]
    if not pcio.exists():
        cell = tl.groupby(groups + ["is_in_sample"]).agg(
            n_trades=("pnl_pct", "size"),
            wins=("win", lambda s: int(s.astype(bool).sum())),
            sum_pnl_pct=("pnl_pct", "sum"),
            mean_pnl_pct=("pnl_pct", "mean"),
        ).reset_index()
        cell.to_csv(pcio, index=False)
    if not psio.exists():
        strat = tl.groupby(["strategy", "is_in_sample"]).agg(
            n_trades=("pnl_pct", "size"),
            wins=("win", lambda s: int(s.astype(bool).sum())),
            sum_pnl_pct=("pnl_pct", "sum"),
            mean_pnl_pct=("pnl_pct", "mean"),
        ).reset_index()
        strat.to_csv(psio, index=False)


def _agg(df: pd.DataFrame, group_cols: list) -> list:
    """Group + aggregate; return list of records for JSON."""
    if df.empty or not all(c in df.columns for c in group_cols):
        return []
    g = df.groupby(group_cols, dropna=False).agg(
        n=("pnl_pct", "count"),
        wins=("win", lambda x: int((x.astype(bool)).sum())),
        mean_pnl=("pnl_pct", "mean"),
        sum_pnl=("pnl_pct", "sum"),
        median_hold=("hold_days", "median"),
        best=("pnl_pct", "max"),
        worst=("pnl_pct", "min"),
    ).reset_index()
    g["win_rate"] = (g["wins"] / g["n"] * 100).round(1)
    g["mean_pnl"] = g["mean_pnl"].round(2)
    g["sum_pnl"] = g["sum_pnl"].round(1)
    g["median_hold"] = g["median_hold"].round(1)
    g["best"] = g["best"].round(2)
    g["worst"] = g["worst"].round(2)
    return g.to_dict(orient="records")


def _split_is_oos(tl: pd.DataFrame) -> tuple:
    """Return (IS subset, OOS subset)."""
    tl = tl.copy()
    tl["entry_dt"] = pd.to_datetime(tl["entry_date"])
    is_df = tl[tl["entry_dt"] <= IS_END]
    oos_df = tl[tl["entry_dt"] >= OOS_START]
    return is_df, oos_df


def main():
    # Batch 376: --input-dir flag for re-targeting against fresher runs
    # (single-batch outputs land in output_phase_1a_beta_single_local/
    # by default; multi-batch merged outputs in output_phase_1a_beta_merged_local/).
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=str(IN_DIR),
                        help="Phase 1A-beta output directory")
    parser.add_argument("--output-dir", default=str(OUT_DIR),
                        help="Dashboard output directory")
    args = parser.parse_args()
    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)

    if not in_dir.exists():
        print(f"ERROR: {in_dir} missing - re-run Phase 1A-beta or download merged output")
        sys.exit(1)
    out_dir.mkdir(exist_ok=True)

    trade_log = pd.read_csv(in_dir / "trade_log.csv", low_memory=False)
    # Batch 376: generate per_cell + per_strategy IS_OOS if missing
    _generate_is_oos_csvs(trade_log, in_dir)
    per_cell = pd.read_csv(in_dir / "per_cell_is_oos.csv")
    per_strategy = pd.read_csv(in_dir / "per_strategy_is_oos.csv")
    backtest_results = pd.read_csv(in_dir / "backtest_results.csv", low_memory=False)
    walk_forward = pd.read_csv(in_dir / "walk_forward_validation.csv", low_memory=False)

    is_df, oos_df = _split_is_oos(trade_log)

    print(f"Loaded {len(trade_log)} trades ({len(is_df)} IS + {len(oos_df)} OOS)")

    # ------------------------------------------------------------------
    # Overview metrics
    # ------------------------------------------------------------------
    n = len(trade_log)
    n_wins = int(trade_log["win"].astype(bool).sum())
    overview = {
        "n_trades":        n,
        "n_wins":          n_wins,
        "win_rate":        round(100 * n_wins / n, 1) if n else 0,
        "mean_pnl_pct":    round(trade_log["pnl_pct"].mean(), 2),
        "sum_pnl_pct":     round(trade_log["pnl_pct"].sum(), 1),
        "median_hold_days":round(trade_log["hold_days"].median(), 1),
        "best_trade":      round(trade_log["pnl_pct"].max(), 2),
        "worst_trade":     round(trade_log["pnl_pct"].min(), 2),
        "n_strategies":    int(trade_log["strategy"].nunique()),
        "n_exits":         int(trade_log["exit_reason"].nunique()),
        "n_tickers":       int(trade_log["ticker"].nunique()),
        "is_n":            len(is_df),
        "oos_n":           len(oos_df),
        "is_mean_pnl":     round(is_df["pnl_pct"].mean(), 2) if len(is_df) else None,
        "oos_mean_pnl":    round(oos_df["pnl_pct"].mean(), 2) if len(oos_df) else None,
        "is_sum":          round(is_df["pnl_pct"].sum(), 1) if len(is_df) else None,
        "oos_sum":         round(oos_df["pnl_pct"].sum(), 1) if len(oos_df) else None,
    }

    # ------------------------------------------------------------------
    # Per-cube slices: strategy x classifier
    # ------------------------------------------------------------------
    slices = {
        "by_strategy":            _agg(trade_log, ["strategy"]),
        "by_exit_reason":         _agg(trade_log, ["exit_reason"]),
        "by_regime":              _agg(trade_log, ["regime"]),
        "by_sector":              _agg(trade_log, ["sector"]),
        "by_direction":           _agg(trade_log, ["direction"]),
        "by_confidence_tier":     _agg(trade_log, ["confidence_tier"]),

        # 2-D cubes
        "strategy_x_exit":        _agg(trade_log, ["strategy", "exit_reason"]),
        "strategy_x_regime":      _agg(trade_log, ["strategy", "regime"]),
        "strategy_x_sector":      _agg(trade_log, ["strategy", "sector"]),
        "strategy_x_direction":   _agg(trade_log, ["strategy", "direction"]),
        "exit_x_regime":          _agg(trade_log, ["exit_reason", "regime"]),

        # 3-D headline cube
        "strategy_x_exit_x_regime": _agg(trade_log, ["strategy", "exit_reason", "regime"]),
    }

    # IS / OOS split for the headline cube
    slices_is_oos = {
        "strategy_x_exit_IS":   _agg(is_df, ["strategy", "exit_reason"]),
        "strategy_x_exit_OOS":  _agg(oos_df, ["strategy", "exit_reason"]),
    }

    # ------------------------------------------------------------------
    # Survivor + underperformer rosters
    # ------------------------------------------------------------------
    survivors = []
    for _, row in per_cell.iterrows():
        if row.get("is_n", 0) >= 1 and row.get("oos_n", 0) >= 10 and \
           row.get("is_sum_pp", 0) > 0 and row.get("oos_sum_pp", 0) > 0:
            survivors.append({
                "strategy":     row["strategy"],
                "exit_reason":  row["exit_reason"],
                "is_n":         int(row["is_n"]),
                "is_sum_pp":    round(float(row["is_sum_pp"]), 1),
                "oos_n":        int(row["oos_n"]),
                "oos_wr_pct":   round(float(row["oos_wr_pct"]), 1),
                "oos_mean_pct": round(float(row["oos_mean_pct"]), 2),
                "oos_sum_pp":   round(float(row["oos_sum_pp"]), 1),
            })
    survivors.sort(key=lambda r: -r["oos_sum_pp"])

    underperformers = []
    for _, row in per_strategy.iterrows():
        if row.get("oos_n", 0) >= 5 and row.get("oos_sum_pp", 0) < 0:
            underperformers.append({
                "strategy":    row["strategy"],
                "is_n":        int(row.get("is_n", 0)),
                "is_sum_pp":   round(float(row.get("is_sum_pp", 0)), 1),
                "oos_n":       int(row["oos_n"]),
                "oos_wr_pct":  round(float(row.get("oos_wr_pct", 0)), 1),
                "oos_mean_pct":round(float(row.get("oos_mean_pct", 0)), 2),
                "oos_sum_pp":  round(float(row["oos_sum_pp"]), 1),
            })
    underperformers.sort(key=lambda r: r["oos_sum_pp"])

    # ------------------------------------------------------------------
    # Quiet strategies (active in roster but fired 0 trades)
    # ------------------------------------------------------------------
    try:
        from backtest.signals.screener import ALL_STRATEGIES
        from backtest.config import DEPRECATED_STRATEGIES
        active = set(ALL_STRATEGIES.keys()) - DEPRECATED_STRATEGIES
        fired = set(trade_log["strategy"].unique())
        quiet = sorted(active - fired)
    except Exception:
        quiet = []

    # ------------------------------------------------------------------
    # Walk-forward summary
    # ------------------------------------------------------------------
    wf_summary = []
    if "verdict" in walk_forward.columns:
        wf_summary = walk_forward[["strategy", "verdict"]].to_dict(orient="records")[:200]

    # ------------------------------------------------------------------
    # Write data.json
    # ------------------------------------------------------------------
    out = {
        "generated_at":    pd.Timestamp.now().isoformat(timespec="seconds"),
        "phase":           "1A-beta",
        "source":          str(IN_DIR.relative_to(REPO)),
        "overview":        overview,
        "slices":          slices,
        "slices_is_oos":   slices_is_oos,
        "survivors":       survivors,
        "underperformers": underperformers,
        "quiet_strategies": quiet,
        "walk_forward":    wf_summary,
        "is_window":       "2022-01..2024-06",
        "oos_window":      "2024-07..2026-04",
    }

    data_path = out_dir / "data.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(out, f, default=str, indent=1)

    print(f"Wrote {data_path} ({data_path.stat().st_size // 1024} KB)")
    print(f"Slices: {len(slices)} 1D/2D/3D cubes + IS/OOS splits")
    print(f"Survivors: {len(survivors)} (strategy x exit) cells IS+OOS-positive n>=10")
    print(f"Underperformers: {len(underperformers)} strategies OOS-negative n>=5")
    print(f"Quiet strategies: {len(quiet)} active but zero trades")


if __name__ == "__main__":
    main()
