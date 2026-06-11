"""B695 (2026-06-11): generate scripts/aws_b660_splits.json for sharded B660
re-run on AWS.

Splits the PIT-active T1a universe (~503 tickers at as_of=2026-05-31) into
N roughly-equal alphabetical shards. Each shard becomes one EC2 instance's
ticker subset.

Why alphabetical: deterministic, reproducible, no per-shard randomness to
trip up bit-equality with a re-run. Sector-stratified sharding is a future
refinement; for B660 alphabetical is fine because every shard runs the
SAME set of 222 strategies and the per-strategy fire counts are summed
across shards in the merge step.

Usage:
    # Generate splits + upload to S3
    python scripts/aws_b660_splits.py --bucket stock-picks-batch395-jm-7421 --shards 5 --upload
    # Or generate to local file only
    python scripts/aws_b660_splits.py --shards 5 --output scripts/aws_b660_splits.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
T1A_PATH = REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"


def load_pit_active_t1a(as_of: date) -> list[str]:
    import pandas as pd
    df = pd.read_csv(T1A_PATH, comment="#")
    added = pd.to_datetime(df["added_date"], errors="coerce").dt.date
    removed = pd.to_datetime(df["removed_date"], errors="coerce").dt.date
    mask = ((added.isna()) | (added <= as_of)) & ((removed.isna()) | (removed > as_of))
    df = df[mask]
    return sorted(df["Symbol"].astype(str).str.upper().unique().tolist())


def split_alphabetical(tickers: list[str], n_shards: int) -> dict[str, list[str]]:
    """Round-robin alphabetical split. Shard 1 gets [0, n, 2n, ...], shard 2
    gets [1, n+1, 2n+1, ...], etc. This balances cap-tiers across shards
    (alphabetical first-N would concentrate large-caps in early shards)."""
    splits = {f"shard_{i + 1}": [] for i in range(n_shards)}
    for i, t in enumerate(tickers):
        splits[f"shard_{(i % n_shards) + 1}"].append(t)
    return splits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shards", type=int, default=5)
    ap.add_argument("--as-of", default="2026-05-31",
                    help="PIT date for T1a filter")
    ap.add_argument("--output", default=None,
                    help="Local file output (default scripts/aws_b660_splits.json)")
    ap.add_argument("--bucket", default=None,
                    help="If set, upload to s3://<bucket>/aws_b660_splits.json")
    ap.add_argument("--s3-key", default="aws_b660_splits.json")
    ap.add_argument("--upload", action="store_true",
                    help="Upload to S3 (requires --bucket)")
    args = ap.parse_args()

    as_of = date.fromisoformat(args.as_of)
    tickers = load_pit_active_t1a(as_of)
    print(f"T1a PIT-active at {as_of}: {len(tickers)} tickers")
    if not tickers:
        raise SystemExit("[FATAL] empty universe; check T1A CSV path / PIT filter")

    splits = split_alphabetical(tickers, args.shards)
    for k, v in splits.items():
        print(f"  {k}: {len(v)} tickers  (first 5: {v[:5]})")

    output_path = Path(args.output) if args.output else REPO / "scripts" / "aws_b660_splits.json"
    output_path.write_text(json.dumps(splits, indent=2))
    print(f"\n[OK] wrote {output_path}")

    if args.upload:
        if not args.bucket:
            raise SystemExit("[FATAL] --upload requires --bucket")
        cmd = ["aws", "s3", "cp", str(output_path),
               f"s3://{args.bucket}/{args.s3_key}",
               "--no-progress"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise SystemExit(f"[FATAL] s3 upload failed: {r.stderr}")
        print(f"[OK] uploaded to s3://{args.bucket}/{args.s3_key}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
