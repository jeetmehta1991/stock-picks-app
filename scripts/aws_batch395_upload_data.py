"""Batch 395: one-time S3 upload of data_prefetch + universe csvs.

Source (per CHECKLIST #77): owner directive 2026-05-27 Path 1. Each
EC2 instance needs ~10GB of prefetch data to run a Phase 1A-beta cube
batch.  Rather than re-prefetching on every instance launch, upload
once to S3; instances sync from S3 in-region (free transfer).

Run this BEFORE the first batch395 launch.  Subsequent runs only need
to re-upload if prefetch data has changed (incremental sync).

Usage:
    python scripts/aws_batch395_upload_data.py --bucket stock-picks-batch395-jm-7421

    # Dry-run first to see what would be uploaded:
    python scripts/aws_batch395_upload_data.py --bucket ... --dry-run

Reads AWS credentials from ~/.aws/credentials (run `aws configure` first).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# What to sync to S3.  Order matters only for log readability.
SYNC_TARGETS = [
    # (local_path, s3_prefix, description)
    ("data_prefetch",       "data_prefetch",       "OHLCV + smart_money + sentiment + macro"),
    ("Backtesting universe", "Backtesting universe", "T1a/T1c/T2/T3 + ETF universe csvs"),
    ("data/cache",          "data/cache",          "info_cache.json + ticker overrides (optional)"),
]


def aws_s3_sync(local: Path, s3_uri: str, dry_run: bool, exclude: list[str]) -> int:
    """Wrap `aws s3 sync` with our standard flags + exclusions."""
    cmd = [
        "aws", "s3", "sync", str(local), s3_uri,
        "--no-progress",
    ]
    for ex in exclude:
        cmd.extend(["--exclude", ex])
    if dry_run:
        cmd.append("--dryrun")
    print(f"  $ {' '.join(cmd)}")
    return subprocess.call(cmd)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True,
                    help="S3 bucket name (no s3:// prefix)")
    ap.add_argument("--region", default="us-east-1",
                    help="AWS region (default us-east-1)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be uploaded; no actual transfer")
    ap.add_argument("--skip", default="",
                    help="Comma-separated targets to skip (data_prefetch / cache / universe)")
    args = ap.parse_args()

    skip = set(s.strip() for s in args.skip.split(",") if s.strip())

    # Default exclusions: huge / unnecessary / regenerable artifacts
    exclude = [
        "*.pyc", "__pycache__/*", ".git/*", ".pytest_cache/*",
        "*.log", "logs/*",
        # Skip historical Phase 1A-beta outputs (they are large and not needed
        # on AWS workers)
        "output_*/*", "output_*/**",
    ]

    print(f"[INIT] Batch 395 S3 upload")
    print(f"[INIT] bucket=s3://{args.bucket} region={args.region}")
    print(f"[INIT] dry_run={args.dry_run}")
    print()

    # Verify aws cli works (credentials configured?)
    rc = subprocess.call(
        ["aws", "s3api", "list-buckets",
         "--query", "Buckets[?Name=='" + args.bucket + "'].Name",
         "--output", "text"],
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    if rc != 0:
        print(f"[FATAL] `aws s3api list-buckets` failed (rc={rc}). "
              f"Run `aws configure` to set credentials.")
        return 1

    overall_t0 = time.time()
    failed = []
    for local_rel, s3_prefix, desc in SYNC_TARGETS:
        if local_rel.split("/")[0] in skip or local_rel in skip:
            print(f"[SKIP] {local_rel} ({desc})")
            continue
        local = REPO / local_rel
        if not local.exists():
            print(f"[WARN] local path missing, skipping: {local}")
            continue

        size_gb = sum(
            f.stat().st_size for f in local.rglob("*") if f.is_file()
        ) / (1024 ** 3)
        print(f"\n[SYNC] {local_rel} -> s3://{args.bucket}/{s3_prefix}/")
        print(f"       {desc}")
        print(f"       local size: {size_gb:.2f} GB")
        t0 = time.time()
        rc = aws_s3_sync(local, f"s3://{args.bucket}/{s3_prefix}/",
                        dry_run=args.dry_run, exclude=exclude)
        elapsed = time.time() - t0
        if rc != 0:
            print(f"[FAIL] sync rc={rc} after {elapsed:.0f}s")
            failed.append(local_rel)
        else:
            print(f"[OK] {local_rel} synced in {elapsed:.0f}s")

    overall = time.time() - overall_t0
    print(f"\n[DONE] total elapsed {overall:.0f}s")
    if failed:
        print(f"[FAIL] {len(failed)} targets failed: {failed}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
