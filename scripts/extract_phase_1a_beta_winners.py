"""scripts/extract_phase_1a_beta_winners.py

Phase 1A-beta winners extraction (Batch 244 / DEC-422 wiring).

Reads a Phase 1A-beta trade_log (parquet preferred, CSV fallback per DEC-491
hybrid), groups by (strategy x exit_method x regime), applies cube_populator
verdict (11-criteria + DEC-426 5-Gate), and writes winners.parquet with P1/P2/P3
priority tiers.

Output is consumed by:
  - Phase 1B-alpha (agents applied to P1 winners only)
  - Stage 3 paper trading daily-picks generator
  - Dashboard 3 (Phase 1A-beta verdict view)

Usage:
  python scripts/extract_phase_1a_beta_winners.py
  python scripts/extract_phase_1a_beta_winners.py --source output_v2 \
      --include-p2 --out output_v2/winners.parquet

Exit codes:
  0  - winners.parquet written; >=1 P1 combo found
  1  - trade_log missing or unreadable
  2  - 0 P1 combos found (informational; still writes empty parquet)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.results.cube_populator import (
    extract_winners,
    populate_cube,
)


def load_trade_log(source_dir: Path) -> pd.DataFrame:
    """Load trade_log from source_dir; prefer parquet, fall back to CSV."""
    parquet_path = source_dir / "trade_log.parquet"
    csv_path = source_dir / "trade_log.csv"
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path)
        except Exception as exc:
            print(f"[WARN] parquet read failed ({exc}); falling back to CSV", file=sys.stderr)
    if csv_path.exists():
        return pd.read_csv(csv_path)
    raise FileNotFoundError(f"No trade_log.parquet or trade_log.csv in {source_dir}")


def main() -> int:
    p = argparse.ArgumentParser(description="Extract Phase 1A-beta winners")
    p.add_argument("--source", default="output_v2",
                   help="Source dir containing trade_log (default: %(default)s)")
    p.add_argument("--out", default=None,
                   help="Output parquet path (default: {source}/winners.parquet)")
    p.add_argument("--include-p2", action="store_true",
                   help="Include P2 (per-regime PASS but failed 5-Gate) in winners")
    p.add_argument("--include-p3", action="store_true",
                   help="Include P3 (no-edge) - only for analysis, not 1B-alpha input")
    args = p.parse_args()

    source_dir = REPO / args.source
    out_path = Path(args.out) if args.out else source_dir / "winners.parquet"

    if not source_dir.exists():
        print(f"[ERROR] source dir not found: {source_dir}", file=sys.stderr)
        return 1
    try:
        trade_log = load_trade_log(source_dir)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if trade_log.empty:
        print("[WARN] trade_log empty; writing empty winners.parquet")
        pd.DataFrame().to_parquet(out_path, index=False)
        return 2

    print(f"[INFO] loaded {len(trade_log)} trades from {source_dir}")

    try:
        cube = populate_cube(trade_log)
    except ValueError as exc:
        print(f"[ERROR] populate_cube failed: {exc}", file=sys.stderr)
        return 1

    print(f"[INFO] cube has {len(cube)} (strategy x exit x regime) cells")
    counts = cube["priority"].value_counts().to_dict()
    print(f"[INFO] priority distribution: {counts}")

    # Build winners with selected priority filter
    filter_tiers = ["P1"]
    if args.include_p2:
        filter_tiers.append("P2")
    if args.include_p3:
        filter_tiers.append("P3")
    winners = extract_winners(cube, priority_filter=tuple(filter_tiers))

    print(f"[INFO] {len(winners)} winners selected (tiers: {filter_tiers})")
    if len(winners) == 0:
        print("[WARN] zero P1 combos - Phase 1B-alpha has no targets")
        winners.to_parquet(out_path, index=False)
        return 2

    # Sort by priority then sharpe (already done in populate_cube; preserve here)
    winners.to_parquet(out_path, index=False)
    print(f"[OK] wrote {out_path.relative_to(REPO) if out_path.is_relative_to(REPO) else out_path} ({len(winners)} rows)")

    # Surface top 5 for quick owner inspection
    top5 = winners.head(5)[["combo_id", "n_trades", "win_rate", "sharpe", "priority"]]
    print("\nTop 5 winners (priority + sharpe):")
    print(top5.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
