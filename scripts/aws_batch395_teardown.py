"""Batch 395: force-terminate any straggler instances tagged batch=batch395.

Source (per CHECKLIST #77): owner directive 2026-05-27 Path 1.  Most
instances self-terminate at end-of-bootstrap; this script is the
safety net for failures (engine hung, bootstrap crashed before reaching
the self-terminate call, etc.).  Idempotent.

Usage:
    python scripts/aws_batch395_teardown.py
    python scripts/aws_batch395_teardown.py --dry-run

Reads AWS credentials from ~/.aws/credentials.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys


def find_batch395_instances(region: str) -> list[dict]:
    """Find all running/pending instances tagged batch=batch395."""
    cmd = [
        "aws", "ec2", "describe-instances", "--region", region,
        "--filters",
        "Name=tag:batch,Values=batch395",
        "Name=instance-state-name,Values=pending,running,stopping,stopped",
        "--query",
        "Reservations[].Instances[].{Id:InstanceId,State:State.Name,"
        "Index:Tags[?Key=='batch_index']|[0].Value,"
        "LaunchTime:LaunchTime}",
        "--output", "json",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"[FATAL] describe-instances failed: {r.stderr}")
        return []
    return json.loads(r.stdout) if r.stdout.strip() else []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-stopped", action="store_true",
                    help="also terminate stopped instances (default: only "
                         "running/pending/stopping)")
    args = ap.parse_args()

    instances = find_batch395_instances(args.region)
    if args.include_stopped is False:
        instances = [i for i in instances
                     if i["State"] not in ("stopped",)]

    if not instances:
        print(f"[OK] no batch395 instances found in {args.region}")
        return 0

    print(f"[INFO] found {len(instances)} batch395 instance(s) in {args.region}:")
    for i in instances:
        print(f"  {i['Id']}  state={i['State']}  "
              f"batch_index={i.get('Index', '?')}  "
              f"launched={i['LaunchTime']}")

    if args.dry_run:
        print(f"[DRY-RUN] would terminate {len(instances)} instance(s)")
        return 0

    instance_ids = [i["Id"] for i in instances]
    cmd = [
        "aws", "ec2", "terminate-instances", "--region", args.region,
        "--instance-ids", *instance_ids, "--no-cli-pager",
        "--query", "TerminatingInstances[].{Id:InstanceId,Prev:PreviousState.Name,"
        "Curr:CurrentState.Name}", "--output", "table",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(r.stdout)
    if r.returncode != 0:
        print(f"[FAIL] terminate-instances: {r.stderr}")
        return 1
    print(f"[OK] terminated {len(instance_ids)} instance(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
