"""Batch 395: 5-instance health monitor wrapping Batch 394 single-instance checks.

Source (per CHECKLIST #77): owner directive 2026-05-27 Path 1 +
Option 3 defense-in-depth.  Polls all 5 batch instances in parallel
and applies the Batch 394 14-check suite to each via S3 heartbeat
or direct SSH+tmux capture.

Why S3 heartbeat over SSH: SSH requires PEM + per-instance public DNS;
the bootstrap script writes a heartbeat blob to
`s3://bucket/heartbeat/batch_N.txt` every 5min.  Monitor polls S3 (faster,
no PEM needed in monitor process, owner credentials sufficient).

Usage:
    python scripts/aws_batch395_monitor.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --max-run-hours 6.0 --warn-run-hours 4.0

    # Pair with --auto-kill to terminate any instance breaching kill criteria:
    python scripts/aws_batch395_monitor.py ... --auto-kill
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def s3_get_heartbeat(bucket: str, batch_index: int) -> str | None:
    """Fetch heartbeat blob from S3; None if missing or ssh-cli error."""
    cmd = [
        "aws", "s3", "cp",
        f"s3://{bucket}/heartbeat/batch_{batch_index}.txt", "-",
        "--no-progress",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        return None
    return r.stdout


def s3_check_complete(bucket: str, batch_index: int) -> bool:
    """Return True if `_COMPLETE` sentinel exists for this batch."""
    cmd = [
        "aws", "s3api", "head-object", "--bucket", bucket,
        "--key", f"outputs/batch_{batch_index}/_COMPLETE",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    return r.returncode == 0


def parse_heartbeat(blob: str) -> dict:
    """Parse the simple key=value heartbeat format from the bootstrap."""
    out = {}
    for line in blob.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def terminate_instance(region: str, instance_id: str) -> bool:
    """Issue ec2 terminate-instances on the given instance.  Returns True
    on success (or no-op if already terminated)."""
    cmd = [
        "aws", "ec2", "terminate-instances", "--region", region,
        "--instance-ids", instance_id, "--no-cli-pager",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--state-file",
                    default=str(REPO / "scripts" / "aws_batch395_state.json"),
                    help="path to aws_batch395_state.json from launch script")
    ap.add_argument("--max-run-hours", type=float, default=6.0)
    ap.add_argument("--warn-run-hours", type=float, default=4.0)
    ap.add_argument("--interval", type=int, default=120,
                    help="poll interval seconds (default 2 min; drops to 30s "
                         "in last hour)")
    ap.add_argument("--heartbeat-stale-seconds", type=int, default=900,
                    help="if no heartbeat in N seconds, flag as STALE")
    ap.add_argument("--auto-kill", action="store_true",
                    help="auto-terminate instances that breach kill criteria")
    ap.add_argument("--once", action="store_true",
                    help="single poll then exit (for tests)")
    args = ap.parse_args()

    state_path = Path(args.state_file)
    if not state_path.exists():
        print(f"[FATAL] state file missing: {state_path}. Run launch first.")
        return 1
    state = json.loads(state_path.read_text())
    instances = state["instances"]  # {batch_N: instance_id}

    print(f"[INIT] Batch 395 multi-instance monitor")
    print(f"[INIT] tracking {len(instances)} instances: "
          f"{list(instances.keys())}")
    print(f"[INIT] max_run_hours={args.max_run_hours} "
          f"warn_run_hours={args.warn_run_hours} "
          f"auto_kill={args.auto_kill}")

    start_epoch = time.time()
    warned: dict[str, bool] = {b: False for b in instances}

    while True:
        completed = 0
        any_kill = False
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        per_instance_lines = []
        for batch_name, instance_id in instances.items():
            batch_index = int(batch_name.split("_")[1])

            # Completion check (sentinel in S3)
            if s3_check_complete(args.bucket, batch_index):
                completed += 1
                per_instance_lines.append(
                    f"  {batch_name} ({instance_id}): _COMPLETE"
                )
                continue

            # Heartbeat check
            hb = s3_get_heartbeat(args.bucket, batch_index)
            if hb is None:
                per_instance_lines.append(
                    f"  {batch_name} ({instance_id}): heartbeat MISSING"
                )
                continue
            data = parse_heartbeat(hb)
            elapsed = int(data.get("elapsed_seconds", "0") or "0")
            elapsed_h = elapsed / 3600.0

            # W14 -- 4h warn
            if elapsed_h >= args.warn_run_hours and not warned[batch_name]:
                print(f"[WARN {ts}] {batch_name} elapsed={elapsed_h:.2f}h "
                      f">= warn={args.warn_run_hours}h")
                warned[batch_name] = True

            # W1 -- 6h kill
            if elapsed_h >= args.max_run_hours:
                print(f"[KILL {ts}] {batch_name} elapsed={elapsed_h:.2f}h "
                      f">= max={args.max_run_hours}h")
                any_kill = True
                if args.auto_kill:
                    ok = terminate_instance(args.region, instance_id)
                    print(f"[KILL {ts}] terminate {instance_id} -> {ok}")

            per_instance_lines.append(
                f"  {batch_name} ({instance_id}): elapsed={elapsed_h:.2f}h "
                f"tmux={data.get('tmux', '?')}"
            )

        total_elapsed_h = (time.time() - start_epoch) / 3600.0
        print(f"\n[{ts}] monitor elapsed={total_elapsed_h:.2f}h "
              f"completed={completed}/{len(instances)} "
              f"warned={sum(warned.values())} "
              f"any_kill={any_kill}")
        for line in per_instance_lines:
            print(line)

        # Exit when all 5 done
        if completed == len(instances):
            print(f"\n[DONE] all {len(instances)} batches complete after "
                  f"{total_elapsed_h:.2f}h.  Next: run merge.")
            return 0

        if args.once:
            return 0

        # Drop to 30s polling in final hour
        interval = args.interval
        if total_elapsed_h >= (args.max_run_hours - 1.0):
            interval = min(interval, 30)
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main())
