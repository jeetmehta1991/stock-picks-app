"""Batch 395: generate 5-batch ticker splits for the full Phase 1A-beta cube.

Source (per CHECKLIST #77): owner directive 2026-05-27 Path 1 + AWS
5-batch parallelism.  Splits the full Master Dedup universe (1,937
tickers per `get_master_universe()`) into 5 roughly-equal lists for
parallel execution across 5 EC2 c7a.4xlarge instances.

Outputs:
    scripts/aws_batch395_splits.json -- 5 lists of tickers consumed by
        the bootstrap script via S3 sync.

Splitting strategy: deterministic sort then round-robin distribute.
Round-robin (vs contiguous slice) balances workload because tickers
are not uniformly active across the timeline -- contiguous slice puts
all the dense-history tickers in one batch, leaving another batch with
mostly-empty PIT-inactive tickers.

Usage:
    python scripts/aws_batch395_splits.py
    python scripts/aws_batch395_splits.py --verify  # only validate existing
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backtest.data.universe import get_master_universe


N_BATCHES = 5


def build_splits(tickers: list[str], n_batches: int = N_BATCHES) -> dict:
    """Round-robin distribute tickers across n_batches lists.

    Returns: {"batch_1": [...], "batch_2": [...], ...}
    """
    batches = {f"batch_{i+1}": [] for i in range(n_batches)}
    for idx, t in enumerate(tickers):
        batches[f"batch_{(idx % n_batches) + 1}"].append(t)
    return batches


def verify_splits(splits: dict, source_tickers: list[str]) -> list[str]:
    """Return list of validation errors; empty = pass."""
    errors = []
    all_in_splits = [t for k in sorted(splits.keys()) for t in splits[k]]
    src = set(source_tickers)
    in_splits = set(all_in_splits)
    if len(all_in_splits) != len(in_splits):
        errors.append(
            f"DUPLICATE tickers across batches "
            f"(total={len(all_in_splits)} unique={len(in_splits)})"
        )
    missing = src - in_splits
    if missing:
        errors.append(f"MISSING from splits: {sorted(missing)[:10]}...")
    extra = in_splits - src
    if extra:
        errors.append(f"EXTRA in splits (not in source): {sorted(extra)[:10]}...")
    # Size balance: no batch >5% larger than the smallest
    sizes = [len(splits[k]) for k in sorted(splits.keys())]
    if max(sizes) - min(sizes) > max(2, int(0.05 * max(sizes))):
        errors.append(
            f"IMBALANCED batch sizes: min={min(sizes)} max={max(sizes)} "
            f"(spread > 5%)"
        )
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "scripts" / "aws_batch395_splits.json"),
                    help="output path (default scripts/aws_batch395_splits.json)")
    ap.add_argument("--verify", action="store_true",
                    help="only verify existing splits file; do not rewrite")
    args = ap.parse_args()

    tickers = get_master_universe()
    if not tickers:
        print("[FATAL] get_master_universe() returned empty list")
        return 1
    print(f"[INFO] Master Universe: {len(tickers)} unique tickers")

    out_path = Path(args.out)

    if args.verify:
        if not out_path.exists():
            print(f"[FAIL] splits file missing: {out_path}")
            return 2
        splits = json.loads(out_path.read_text())
        errors = verify_splits(splits, tickers)
        if errors:
            for e in errors:
                print(f"[FAIL] {e}")
            return 3
        sizes = [len(splits[k]) for k in sorted(splits.keys())]
        print(f"[OK] splits valid: sizes={sizes} total={sum(sizes)}")
        return 0

    splits = build_splits(tickers)
    errors = verify_splits(splits, tickers)
    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return 4

    out_path.write_text(json.dumps(splits, indent=2))
    sizes = [len(splits[k]) for k in sorted(splits.keys())]
    print(f"[OK] wrote {out_path}")
    print(f"[OK] batch sizes: {sizes} (total {sum(sizes)})")
    print()
    print("Next step: upload to S3 alongside data_prefetch")
    print(f"  aws s3 cp {out_path} s3://<bucket>/aws_batch395_splits.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
