"""B695 (2026-06-11): launch EC2 instances to run B660 fire-count measurement
across ticker shards with B694 multiprocessing.

Pattern adapted from scripts/aws_batch395_launch.py (B395 / 2026-05-27).
Same Ubuntu 24.04 AMI, same IAM role, same security group, same S3 bucket.
The difference is the bootstrap (aws_b660_bootstrap.sh) which runs
measure_fire_count.py with --n-workers + --ticker-subset instead of
run_phase1a.

Cost (on c7a.4xlarge spot @ ~$0.40/hr in us-east-1):
  Smoke (1 instance x 30 tickers x 6 months): ~10 min, ~$0.10
  Full (5 instances x ~100 tickers each x 6.41 cal yrs): ~2.4h per instance,
    ~$2/instance x 5 = ~$10 spot maximum.
  Per owner $10 budget cap directive 2026-06-11.

Usage:
    # Smoke (1 instance, owner-defined ticker list)
    python scripts/aws_b660_launch.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --key-pair batch395 \\
        --shards 1 \\
        --smoke-tickers AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA \\
        --start 2024-01-01 --end 2024-06-30 \\
        --spot

    # Full (5 instances, splits.json from S3)
    python scripts/aws_b660_launch.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --key-pair batch395 \\
        --shards 5 \\
        --start 2020-01-01 --end 2026-05-31 \\
        --spot

Reads AWS credentials from ~/.aws/credentials. Same IAM role
batch395-instance-role used by B395 grants S3 read/write + EC2
terminate (for self-termination).
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Same SSM-resolved AMI as B395 (Canonical Ubuntu 24.04 LTS)
DEFAULT_AMI_ID = "ami-0c80e2b6ccb9ad6d1"


def resolve_ami_from_ssm(region: str) -> str:
    cmd = [
        "aws", "ssm", "get-parameter", "--region", region,
        "--name", "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id",
        "--query", "Parameter.Value", "--output", "text",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise SystemExit(f"[FATAL] SSM query failed: {r.stderr}")
    return r.stdout.strip()


def existing_security_group(region: str, name: str) -> str:
    """B695 reuses B395's security group. Fails fast if absent (we
    don't auto-create here -- if the SG was deleted, run B395's launcher
    once to recreate it, or pass --security-group <existing>)."""
    r = subprocess.run(
        ["aws", "ec2", "describe-security-groups", "--region", region,
         "--filters", f"Name=group-name,Values={name}",
         "--query", "SecurityGroups[0].GroupId", "--output", "text"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0 or not r.stdout.strip() or r.stdout.strip() == "None":
        raise SystemExit(
            f"[FATAL] security group '{name}' not found in {region}. "
            f"Either pass --security-group <name> or recreate via B395 launcher."
        )
    return r.stdout.strip()


def existing_instance_profile(name: str = "batch395-instance-role") -> str:
    """B695 reuses B395's IAM role. Same policies (S3FullAccess +
    EC2FullAccess for self-terminate)."""
    r = subprocess.run(
        ["aws", "iam", "get-instance-profile", "--instance-profile-name", name],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise SystemExit(
            f"[FATAL] IAM instance profile '{name}' not found. "
            f"Either pass --instance-profile <name> or run B395 launcher once to create it."
        )
    return name


def build_user_data(
    shard_index: int, bucket: str, commit: str, start: str, end: str,
    n_workers: int, repo_url: str,
    smoke_tickers: str | None = None,
    splits_key: str = "aws_b660_splits.json",
    output_key_prefix: str = "b660_outputs",
) -> str:
    bootstrap_path = REPO / "scripts" / "aws_b660_bootstrap.sh"
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    header = (
        f"#!/bin/bash\n"
        f"export B660_INDEX={shard_index}\n"
        f"export B660_BUCKET={bucket}\n"
        f"export B660_COMMIT={commit}\n"
        f"export B660_START={start}\n"
        f"export B660_END={end}\n"
        f"export B660_N_WORKERS={n_workers}\n"
        f"export B660_REPO_URL={repo_url}\n"
        f"export B660_SPLITS_KEY={splits_key}\n"
        f"export B660_OUTPUT_KEY_PREFIX={output_key_prefix}\n"
    )
    if smoke_tickers:
        header += f'export B660_TICKERS="{smoke_tickers}"\n'
    if bootstrap.startswith("#!"):
        bootstrap = bootstrap.split("\n", 1)[1]
    full = header + bootstrap
    return base64.b64encode(full.encode()).decode()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--key-pair", required=True)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--commit", default="main")
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--end", default="2026-05-31")
    ap.add_argument("--n-workers", type=int, default=14,
                    help="--n-workers per instance (default 14 of 16 vCPU on c7a.4xlarge)")
    ap.add_argument("--instance-type", default="c7a.4xlarge")
    ap.add_argument("--ami-id", default=None)
    ap.add_argument("--repo-url",
                    default="https://github.com/jeetmehta1991/stock-picks-app.git")
    ap.add_argument("--security-group", default="batch395-ssh",
                    help="reused from B395; --security-group <name> to override")
    ap.add_argument("--instance-profile", default="batch395-instance-role",
                    help="reused from B395")
    ap.add_argument("--volume-gb", type=int, default=50)
    ap.add_argument("--spot", action="store_true",
                    help="use spot pricing (~40%% cheaper, possible reclaim)")
    ap.add_argument("--spot-max-price", default="0.30",
                    help="max spot bid price (default $0.30/hr; on-demand ~$0.86)")
    ap.add_argument("--shards", type=int, default=5,
                    help="number of shards/instances to launch (default 5)")
    ap.add_argument("--shard-start", type=int, default=1,
                    help="first shard index (default 1)")
    ap.add_argument("--smoke-tickers", default=None,
                    help="SMOKE: comma-separated ticker list (bypasses splits.json)")
    ap.add_argument("--splits-key", default="aws_b660_splits.json",
                    help="S3 key for splits.json (in bucket root)")
    ap.add_argument("--output-key-prefix", default="b660_outputs",
                    help="S3 prefix for output JSONs + logs + heartbeats")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.ami_id is None:
        print("[INFO] resolving latest Ubuntu 24.04 AMI from SSM...")
        ami_id = resolve_ami_from_ssm(args.region)
        print(f"[INFO] AMI: {ami_id}")
    else:
        ami_id = args.ami_id

    sg_id = existing_security_group(args.region, args.security_group)
    profile_name = existing_instance_profile(args.instance_profile)

    print(f"\n[INIT] Launching {args.shards} x {args.instance_type} "
          f"({'spot' if args.spot else 'on-demand'}) in {args.region}")
    print(f"[INIT] AMI={ami_id} SG={sg_id} IAM={profile_name}")
    print(f"[INIT] commit={args.commit} n_workers={args.n_workers}")
    print(f"[INIT] start={args.start} end={args.end}")
    if args.smoke_tickers:
        print(f"[INIT] SMOKE MODE: tickers={args.smoke_tickers}")
    print()

    launched = []
    shard_start = max(1, int(args.shard_start))
    for shard_index in range(shard_start, shard_start + args.shards):
        user_data = build_user_data(
            shard_index, args.bucket, args.commit, args.start, args.end,
            args.n_workers, args.repo_url,
            smoke_tickers=args.smoke_tickers,
            splits_key=args.splits_key,
            output_key_prefix=args.output_key_prefix,
        )
        cmd = [
            "aws", "ec2", "run-instances", "--region", args.region,
            "--image-id", ami_id,
            "--instance-type", args.instance_type,
            "--key-name", args.key_pair,
            "--security-group-ids", sg_id,
            "--iam-instance-profile", f"Name={profile_name}",
            "--user-data", user_data,
            "--block-device-mappings",
            json.dumps([{
                "DeviceName": "/dev/sda1",
                "Ebs": {"VolumeSize": args.volume_gb, "VolumeType": "gp3"},
            }]),
            "--tag-specifications",
            f"ResourceType=instance,Tags=[{{Key=batch,Value=b660}},"
            f"{{Key=shard_index,Value={shard_index}}},"
            f"{{Key=Name,Value=b660-shard-{shard_index}}}]",
            "--query", "Instances[0].InstanceId", "--output", "text",
        ]
        if args.spot:
            cmd.extend([
                "--instance-market-options",
                json.dumps({
                    "MarketType": "spot",
                    "SpotOptions": {
                        "MaxPrice": args.spot_max_price,
                        "SpotInstanceType": "one-time",
                    },
                }),
            ])
        if args.dry_run:
            print(f"[DRY-RUN] shard_{shard_index}: would launch (user-data {len(user_data)} chars b64)")
            launched.append((f"shard_{shard_index}", "DRY", "DRY"))
            continue
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print(f"[FAIL] shard_{shard_index} launch: {r.stderr}")
            continue
        instance_id = r.stdout.strip()
        print(f"[OK] shard_{shard_index}: launched {instance_id}")
        launched.append((f"shard_{shard_index}", instance_id, ""))

    if args.dry_run:
        return 0

    print("\n[INIT] waiting 30s for instances to publish IPs...")
    time.sleep(30)

    print("\n=== Launched instances ===")
    for shard, instance_id, _ in launched:
        r = subprocess.run(
            ["aws", "ec2", "describe-instances", "--region", args.region,
             "--instance-ids", instance_id,
             "--query", "Reservations[0].Instances[0].PublicDnsName",
             "--output", "text"],
            capture_output=True, text=True, timeout=30,
        )
        dns = r.stdout.strip() if r.returncode == 0 else "pending"
        print(f"  {shard}: {instance_id}  ssh ubuntu@{dns}")

    print()
    print("Monitor:")
    print(f"  aws s3 ls s3://{args.bucket}/{args.output_key_prefix}/ --recursive")
    print(f"  aws s3 cp s3://{args.bucket}/{args.output_key_prefix}/heartbeat_<N>.txt -")
    print()
    print("Merge when all sentinels present:")
    print(f"  python scripts/aws_b660_merge.py --bucket {args.bucket} --output-key-prefix {args.output_key_prefix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
