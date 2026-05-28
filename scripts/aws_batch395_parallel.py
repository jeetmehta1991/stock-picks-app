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
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

HEARTBEAT_STALE_WARN_SEC = 600   # 10 min
HEARTBEAT_STALE_KILL_SEC = 1800  # 30 min: terminate + relaunch


def s3_check_complete(bucket: str, batch_index: int) -> bool:
    cmd = ["aws", "s3api", "head-object", "--bucket", bucket,
           "--key", f"outputs/batch_{batch_index}/_COMPLETE"]
    return subprocess.run(cmd, capture_output=True, timeout=30).returncode == 0


def read_heartbeat(bucket: str, batch_index: int) -> dict | None:
    """Batch 411: read heartbeat/batch_N.txt; return dict or None if missing."""
    cmd = ["aws", "s3", "cp",
           f"s3://{bucket}/heartbeat/batch_{batch_index}.txt", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None
    hb: dict = {}
    for line in r.stdout.splitlines():
        if line.startswith("ts="):
            hb["ts"] = line[3:].strip()
        elif line.startswith("elapsed_seconds="):
            hb["elapsed"] = int(line.split("=", 1)[1].strip())
        elif "screen_universe" in line:
            m = re.search(r"\[(\d{4}-\d{2}-\d{2})\]", line)
            if m:
                hb["engine_date"] = m.group(1)
    if hb.get("ts"):
        try:
            ts = datetime.fromisoformat(hb["ts"].replace("Z", "+00:00"))
            hb["age_sec"] = int(
                (datetime.now(timezone.utc) - ts).total_seconds())
        except Exception:
            hb["age_sec"] = None
    return hb


def terminate_instance(region: str, instance_id: str) -> None:
    """Batch 411: terminate a hung/reclaimed instance."""
    subprocess.run(
        ["aws", "ec2", "terminate-instances", "--region", region,
         "--instance-ids", instance_id, "--no-cli-pager"],
        capture_output=True, timeout=30,
    )


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
    if args.max_run_hours is not None:
        cmd.extend(["--max-run-hours", str(args.max_run_hours)])
    if args.warn_run_hours is not None:
        cmd.extend(["--warn-run-hours", str(args.warn_run_hours)])
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
    ap.add_argument("--max-run-hours", type=float, default=None,
                    help="forwarded to launch.py --max-run-hours (engine kill)")
    ap.add_argument("--warn-run-hours", type=float, default=None,
                    help="forwarded to launch.py --warn-run-hours (engine warn)")
    ap.add_argument("--poll-seconds", type=int, default=300)
    ap.add_argument("--max-hours", type=float, default=10.0,
                    help="overall runner timeout (default 10h)")
    ap.add_argument("--forensic", action="store_true", default=True,
                    help="Batch 409: run per-batch forensic check after each "
                         "_COMPLETE; ABORT downstream on major errors")
    ap.add_argument("--no-forensic", dest="forensic", action="store_false",
                    help="disable per-batch forensic check (not recommended)")
    ap.add_argument("--baseline-batch", type=int, default=1,
                    help="baseline batch index for forensic regression check")
    args = ap.parse_args()

    pending = [int(b.strip()) for b in args.batches.split(",")]
    print(f"[INIT] parallel runner: pending={pending}")
    print(f"[INIT] forensic={args.forensic} baseline_batch={args.baseline_batch}")
    deadline = time.time() + args.max_hours * 3600
    completed_with_forensic: set[int] = set()
    forensic_aborted: bool = False

    while pending and time.time() < deadline and not forensic_aborted:
        # Drop completed; run forensic if newly complete
        still = []
        for b in pending:
            if s3_check_complete(args.bucket, b):
                print(f"[DONE] batch_{b} _COMPLETE in S3")
                # Batch 409: run forensic check on this newly-completed batch
                if args.forensic and b not in completed_with_forensic:
                    completed_with_forensic.add(b)
                    print(f"[FORENSIC] running per-batch check on batch_{b}...")
                    fc = [
                        sys.executable,
                        str(REPO / "scripts" / "aws_batch395_forensic_per_batch.py"),
                        "--bucket", args.bucket,
                        "--batch", str(b),
                        "--baseline-batch", str(args.baseline_batch),
                    ]
                    fr = subprocess.run(fc, capture_output=False)
                    if fr.returncode == 2:
                        print(f"[FORENSIC ABORT] batch_{b} failed forensic checks")
                        print(f"[ABORT] per owner directive: terminating subsequent")
                        print(f"        batches; bug fix + relaunch ALL required.")
                        # Terminate any running batch395 instances
                        for inst in running_instances(args.region):
                            print(f"  terminating {inst['id']}")
                            subprocess.run(
                                ["aws", "ec2", "terminate-instances",
                                 "--region", args.region,
                                 "--instance-ids", inst["id"],
                                 "--no-cli-pager"],
                                capture_output=True, timeout=30,
                            )
                        forensic_aborted = True
                        break
                    elif fr.returncode == 1:
                        print(f"[FORENSIC WARN] batch_{b} has warnings; continuing")
                    else:
                        print(f"[FORENSIC PASS] batch_{b} healthy")
            else:
                still.append(b)
        pending = still
        if forensic_aborted:
            break
        if not pending:
            break

        # Find what's running
        instances = running_instances(args.region)
        running_idx = {i["batch_index"] for i in instances if i["batch_index"]}
        ondemand_busy = any(i["lifecycle"] != "spot" for i in instances)
        spot_busy = any(i["lifecycle"] == "spot" for i in instances)

        # Batch 411: per-poll heartbeat check + one-line digest.
        # Stale heartbeat > KILL threshold => terminate instance so its slot
        # frees and the next poll iteration relaunches via pending logic.
        digest_parts = []
        for inst in instances:
            b = inst["batch_index"]
            if b is None:
                continue
            hb = read_heartbeat(args.bucket, b)
            if hb is None:
                digest_parts.append(f"b{b}={inst['lifecycle'][:1]}/no-hb")
                continue
            age = hb.get("age_sec")
            ed = hb.get("engine_date", "?")
            el = hb.get("elapsed", 0)
            tag = inst["lifecycle"][:1]
            if age is None:
                digest_parts.append(f"b{b}={tag}/hb-bad")
            elif age > HEARTBEAT_STALE_KILL_SEC:
                print(f"[STALE-KILL] batch_{b} HB age={age}s > "
                      f"{HEARTBEAT_STALE_KILL_SEC}s; terminating {inst['id']}")
                terminate_instance(args.region, inst["id"])
                if b not in pending:
                    pending.append(b)
                digest_parts.append(f"b{b}={tag}/KILLED-stale")
            elif age > HEARTBEAT_STALE_WARN_SEC:
                digest_parts.append(
                    f"b{b}={tag}/WARN-stale({age}s)@{ed}")
            else:
                m = el // 60
                digest_parts.append(f"b{b}={tag}/{m}m@{ed}(hb{age}s)")

        for b in completed_with_forensic:
            digest_parts.append(f"b{b}=DONE")
        for b in pending:
            if b not in running_idx:
                digest_parts.append(f"b{b}=PENDING")

        print(f"[DIGEST {datetime.now(timezone.utc).strftime('%H:%MZ')}] "
              + " ".join(sorted(set(digest_parts))))
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
