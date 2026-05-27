"""Batch 403 (2026-05-27): sequential batch launcher for AWS quota-bound runs.

When AWS account on-demand quota is 32 vCPU (one c7a.8xlarge at a time),
parallel 4-batch launch fails with VcpuLimitExceeded.  This runner
launches the remaining batches one at a time, waiting on S3 _COMPLETE
sentinel before launching the next.

Usage:
    python scripts/aws_batch395_sequential.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --key-pair batch395 \\
        --ami-id ami-0fc0d6e8d70ab2d42 \\
        --batches 3,4,5 \\
        --instance-type c7a.8xlarge \\
        --workers 24 \\
        --commit 9deb91b95

For each batch in --batches list (in order):
  1. Check if S3 _COMPLETE sentinel already exists -> skip
  2. Check if instance is already running for this batch -> wait
  3. Otherwise launch via aws_batch395_launch.py --batch-start N --batches 1
  4. Poll S3 every 5 min until _COMPLETE appears
  5. Move to next

Exits 0 when all batches complete, 1 on hard failure.

Source (per CHECKLIST #77): owner directive 2026-05-27 path 2
(spot + on-demand mix) collapsed to sequential after VcpuLimitExceeded
on parallel attempt.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def s3_check_complete(bucket: str, batch_index: int) -> bool:
    cmd = [
        "aws", "s3api", "head-object", "--bucket", bucket,
        "--key", f"outputs/batch_{batch_index}/_COMPLETE",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def has_running_instance_for_batch(batch_index: int, region: str) -> str | None:
    """Return instance_id if a running/pending instance is tagged batch_index=N."""
    cmd = [
        "aws", "ec2", "describe-instances", "--region", region,
        "--filters",
        "Name=tag:batch,Values=batch395",
        f"Name=tag:batch_index,Values={batch_index}",
        "Name=instance-state-name,Values=pending,running",
        "--query", "Reservations[0].Instances[0].InstanceId",
        "--output", "text",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    out = r.stdout.strip()
    return out if out and out != "None" else None


def launch_batch(args, batch_index: int) -> bool:
    """Invoke aws_batch395_launch.py for a single batch.  Returns True on launch
    success (instance_id returned)."""
    cmd = [
        sys.executable, str(REPO / "scripts" / "aws_batch395_launch.py"),
        "--bucket", args.bucket,
        "--key-pair", args.key_pair,
        "--ami-id", args.ami_id,
        "--instance-type", args.instance_type,
        "--workers", str(args.workers),
        "--commit", args.commit,
        "--batch-start", str(batch_index),
        "--batches", "1",
    ]
    print(f"[LAUNCH] batch_{batch_index}: {' '.join(cmd[1:])}")
    r = subprocess.run(cmd, capture_output=False)
    return r.returncode == 0


def wait_for_complete(bucket: str, batch_index: int, poll_seconds: int,
                       max_hours: float) -> bool:
    """Poll S3 every poll_seconds until _COMPLETE present or timeout."""
    start = time.time()
    deadline = start + max_hours * 3600
    print(f"[WAIT] batch_{batch_index}: polling _COMPLETE every {poll_seconds}s "
          f"(max {max_hours}h)")
    while time.time() < deadline:
        if s3_check_complete(bucket, batch_index):
            elapsed_h = (time.time() - start) / 3600.0
            print(f"[OK] batch_{batch_index} _COMPLETE after {elapsed_h:.2f}h")
            return True
        time.sleep(poll_seconds)
    print(f"[FAIL] batch_{batch_index} timed out after {max_hours}h")
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--key-pair", required=True)
    ap.add_argument("--ami-id", required=True)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--instance-type", default="c7a.8xlarge")
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--commit", default="main")
    ap.add_argument("--batches", default="3,4,5",
                    help="comma-separated batch indices to launch in order")
    ap.add_argument("--poll-seconds", type=int, default=300,
                    help="S3 _COMPLETE poll interval (default 5 min)")
    ap.add_argument("--max-batch-hours", type=float, default=6.0,
                    help="max hours per batch before giving up (matches "
                         "engine's 6h wall-time kill)")
    args = ap.parse_args()

    batch_indices = [int(b.strip()) for b in args.batches.split(",")]
    print(f"[INIT] sequential runner: batches={batch_indices}")
    print(f"[INIT] type={args.instance_type} workers={args.workers} "
          f"commit={args.commit}")

    for batch_index in batch_indices:
        # Skip if already _COMPLETE in S3
        if s3_check_complete(args.bucket, batch_index):
            print(f"[SKIP] batch_{batch_index}: _COMPLETE already in S3")
            continue

        # Check if an instance is already running for this batch
        running = has_running_instance_for_batch(batch_index, args.region)
        if running:
            print(f"[WAIT] batch_{batch_index}: instance {running} already "
                  f"running; waiting for _COMPLETE")
        else:
            ok = launch_batch(args, batch_index)
            if not ok:
                print(f"[FAIL] batch_{batch_index}: launch failed")
                return 1

        # Wait for _COMPLETE
        if not wait_for_complete(args.bucket, batch_index, args.poll_seconds,
                                 args.max_batch_hours):
            return 2

    print(f"\n[DONE] all batches {batch_indices} complete")
    print(f"[NEXT] run python scripts/aws_batch395_merge.py "
          f"--bucket {args.bucket} --upload-final")
    return 0


if __name__ == "__main__":
    sys.exit(main())
