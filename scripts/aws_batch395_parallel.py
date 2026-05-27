"""Batch 404 (2026-05-27): parallel batch runner using on-demand + spot slots.

AWS new-account quota = 32 vCPU on-demand AND 32 vCPU spot, separately.
So we can run 1 on-demand + 1 spot c7a.8xlarge in parallel = 2 boxes,
~6h total for 4 batches vs 12h sequential.

Polls S3 + EC2 every 5 min.  For each pending batch, launches on the
first free slot (on-demand or spot).  Continues until all batches done.

Usage:
    python scripts/aws_batch395_parallel.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --key-pair batch395 \\
        --ami-id ami-0fc0d6e8d70ab2d42 \\
        --batches 4,5 \\
        --commit 9deb91b95
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def s3_check_complete(bucket: str, batch_index: int) -> bool:
    cmd = ["aws", "s3api", "head-object", "--bucket", bucket,
           "--key", f"outputs/batch_{batch_index}/_COMPLETE"]
    return subprocess.run(cmd, capture_output=True, timeout=30).returncode == 0


def running_instances(region: str) -> list[dict]:
    """Return list of running batch395 instances with their lifecycle + batch_index."""
    cmd = [
        "aws", "ec2", "describe-instances", "--region", region,
        "--filters",
        "Name=tag:batch,Values=batch395",
        "Name=instance-state-name,Values=pending,running",
        "--query", "Reservations[].Instances[].{Id:InstanceId,"
        "Lifecycle:InstanceLifecycle,Idx:Tags[?Key=='batch_index']|[0].Value}",
        "--output", "text",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    out = []
    for line in r.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 3:
            # AWS --output text sorts keys alphabetically: Id, Idx, Lifecycle
            iid, idx, lifecycle = parts[0], parts[1], parts[2]
            out.append({
                "id": iid,
                "lifecycle": lifecycle if lifecycle != "None" else "on-demand",
                "batch_index": int(idx) if idx not in ("None", "") else None,
            })
    return out


def launch_one(args, batch_index: int, use_spot: bool) -> bool:
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
    if use_spot:
        cmd.extend(["--spot", "--spot-max-price", args.spot_max_price])
    print(f"[LAUNCH] batch_{batch_index} {'spot' if use_spot else 'on-demand'}")
    return subprocess.run(cmd, capture_output=False).returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--key-pair", required=True)
    ap.add_argument("--ami-id", required=True)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--instance-type", default="c7a.8xlarge")
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--commit", default="main")
    ap.add_argument("--batches", default="4,5",
                    help="comma-separated batch indices to launch")
    ap.add_argument("--spot-max-price", default="0.90")
    ap.add_argument("--poll-seconds", type=int, default=300)
    ap.add_argument("--max-hours", type=float, default=10.0,
                    help="overall timeout (default 10h)")
    args = ap.parse_args()

    pending = [int(b.strip()) for b in args.batches.split(",")]
    print(f"[INIT] parallel runner: pending={pending}")
    deadline = time.time() + args.max_hours * 3600

    while pending and time.time() < deadline:
        # Drop completed
        still = []
        for b in pending:
            if s3_check_complete(args.bucket, b):
                print(f"[DONE] batch_{b} _COMPLETE in S3")
            else:
                still.append(b)
        pending = still
        if not pending:
            break

        # Find what's running
        instances = running_instances(args.region)
        running_idx = {i["batch_index"] for i in instances if i["batch_index"]}
        ondemand_busy = any(i["lifecycle"] != "spot" for i in instances)
        spot_busy = any(i["lifecycle"] == "spot" for i in instances)

        print(f"[STATE] running={instances} ondemand_busy={ondemand_busy} "
              f"spot_busy={spot_busy} pending={pending}")

        # Launch one batch per free slot
        for batch in list(pending):
            if batch in running_idx:
                continue  # already running
            if not ondemand_busy:
                if launch_one(args, batch, use_spot=False):
                    ondemand_busy = True
                    time.sleep(15)  # let AWS register
                    continue
            if not spot_busy:
                if launch_one(args, batch, use_spot=True):
                    spot_busy = True
                    time.sleep(15)
                    continue
            # Both slots busy
            break

        time.sleep(args.poll_seconds)

    if pending:
        print(f"[TIMEOUT] still pending after {args.max_hours}h: {pending}")
        return 1
    print(f"\n[DONE] all batches complete")
    print(f"[NEXT] python scripts/aws_batch395_merge.py "
          f"--bucket {args.bucket} --upload-final")
    return 0


if __name__ == "__main__":
    sys.exit(main())
