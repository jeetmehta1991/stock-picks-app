"""Batch 395: launch 5 c7a.4xlarge instances to run Phase 1A-beta cube in parallel.

Source (per CHECKLIST #77): owner directive 2026-05-27 Path 1 + AWS
$200 credit + Option 1 (on-demand first, spot later).

Each instance:
  - Gets BATCH395_INDEX (1..5) via user-data env vars
  - Boots from Ubuntu 24.04 LTS AMI
  - Runs scripts/aws_batch395_bootstrap.sh as user-data
  - Self-terminates on engine completion

Cost (on-demand): c7a.4xlarge in us-east-1 ~$0.86/hr.
  Expected: 4-5h per instance = ~$4-5 per instance = ~$20-25 per full run.

Usage:
    python scripts/aws_batch395_launch.py \\
        --bucket stock-picks-batch395-jm-7421 \\
        --key-pair batch395 \\
        --commit HEAD  # or a specific SHA

    # Spot instead of on-demand (40% cheaper, possible reclaim):
    python scripts/aws_batch395_launch.py ... --spot

Reads AWS credentials from ~/.aws/credentials.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Default Ubuntu 24.04 LTS AMI in us-east-1 (Canonical official).  Refresh by
# querying AWS Systems Manager Parameter Store:
#   aws ssm get-parameter --name \
#     /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id
# As of 2026-05-27: ami-0c80e2b6ccb9ad6d1 (subject to change).  Run with
# --resolve-ami-from-ssm to fetch the current one automatically.
DEFAULT_AMI_ID = "ami-0c80e2b6ccb9ad6d1"


def resolve_ami_from_ssm(region: str) -> str:
    """Query SSM for the latest Canonical Ubuntu 24.04 AMI in `region`."""
    cmd = [
        "aws", "ssm", "get-parameter", "--region", region,
        "--name", "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id",
        "--query", "Parameter.Value", "--output", "text",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise SystemExit(f"[FATAL] SSM query failed: {r.stderr}")
    return r.stdout.strip()


def ensure_security_group(region: str, name: str) -> str:
    """Ensure a security group exists allowing SSH from owner IP.

    Returns the security-group ID.  Idempotent.
    """
    # Find existing
    r = subprocess.run(
        ["aws", "ec2", "describe-security-groups", "--region", region,
         "--filters", f"Name=group-name,Values={name}",
         "--query", "SecurityGroups[0].GroupId", "--output", "text"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode == 0 and r.stdout.strip() and r.stdout.strip() != "None":
        return r.stdout.strip()

    # Get default VPC
    r = subprocess.run(
        ["aws", "ec2", "describe-vpcs", "--region", region,
         "--filters", "Name=isDefault,Values=true",
         "--query", "Vpcs[0].VpcId", "--output", "text"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise SystemExit("[FATAL] no default VPC found")
    vpc_id = r.stdout.strip()

    # Create SG
    r = subprocess.run(
        ["aws", "ec2", "create-security-group", "--region", region,
         "--group-name", name, "--vpc-id", vpc_id,
         "--description", "Batch 395 SSH ingress",
         "--query", "GroupId", "--output", "text"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise SystemExit(f"[FATAL] create-sg failed: {r.stderr}")
    sg_id = r.stdout.strip()
    print(f"[INFO] created security group {sg_id}")

    # Allow SSH from owner's current public IP only
    try:
        import urllib.request
        my_ip = urllib.request.urlopen("https://api.ipify.org", timeout=10).read().decode()
        cidr = f"{my_ip}/32"
    except Exception:
        cidr = "0.0.0.0/0"
        print("[WARN] could not detect owner IP; opening SSH to 0.0.0.0/0 -- TIGHTEN LATER")

    subprocess.run(
        ["aws", "ec2", "authorize-security-group-ingress", "--region", region,
         "--group-id", sg_id, "--protocol", "tcp", "--port", "22",
         "--cidr", cidr],
        check=True, capture_output=True, timeout=30,
    )
    print(f"[INFO] ssh ingress allowed from {cidr}")
    return sg_id


def ensure_instance_profile(region: str, role_name: str = "batch395-instance-role") -> str:
    """Ensure an IAM instance profile exists granting EC2 instances S3
    read/write to the bucket.  Returns the InstanceProfile name.

    Idempotent.  Requires the calling IAM user to have iam:* on this role.
    For simplicity, the bootstrap script uses AWS CLI on the instance which
    will use the instance metadata to find this role.
    """
    profile_name = role_name  # use same name for both
    # Check existing
    r = subprocess.run(
        ["aws", "iam", "get-instance-profile", "--instance-profile-name", profile_name],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode == 0:
        return profile_name

    print(f"[INFO] creating IAM role + instance profile: {role_name}")
    # 1. Trust policy
    trust_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    })
    subprocess.run(
        ["aws", "iam", "create-role", "--role-name", role_name,
         "--assume-role-policy-document", trust_policy],
        check=True, capture_output=True, timeout=30,
    )
    # 2. Attach policies needed by the bootstrap script
    for arn in (
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AmazonEC2FullAccess",  # for self-terminate
    ):
        subprocess.run(
            ["aws", "iam", "attach-role-policy", "--role-name", role_name,
             "--policy-arn", arn],
            check=True, capture_output=True, timeout=30,
        )
    # 3. Create instance profile + add role
    subprocess.run(
        ["aws", "iam", "create-instance-profile",
         "--instance-profile-name", profile_name],
        check=True, capture_output=True, timeout=30,
    )
    subprocess.run(
        ["aws", "iam", "add-role-to-instance-profile",
         "--instance-profile-name", profile_name, "--role-name", role_name],
        check=True, capture_output=True, timeout=30,
    )
    # Wait a few seconds for IAM eventual consistency
    print("[INFO] waiting 10s for IAM eventual consistency...")
    time.sleep(10)
    return profile_name


def build_user_data(batch_index: int, bucket: str, commit: str,
                    phase: str, start: str, end: str,
                    workers: int, repo_url: str) -> str:
    """Construct the user-data shell script.  Prepends env-var exports
    to the bootstrap content, then base64-encodes for AWS user-data."""
    bootstrap_path = REPO / "scripts" / "aws_batch395_bootstrap.sh"
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    header = (
        f"#!/bin/bash\n"
        f"export BATCH395_INDEX={batch_index}\n"
        f"export BATCH395_BUCKET={bucket}\n"
        f"export BATCH395_COMMIT={commit}\n"
        f"export BATCH395_PHASE={phase}\n"
        f"export BATCH395_START={start}\n"
        f"export BATCH395_END={end}\n"
        f"export BATCH395_WORKERS={workers}\n"
        f"export BATCH395_REPO_URL={repo_url}\n"
    )
    # Strip the shebang from the bootstrap content (header already has one)
    if bootstrap.startswith("#!"):
        bootstrap = bootstrap.split("\n", 1)[1]
    full = header + bootstrap
    return base64.b64encode(full.encode()).decode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True, help="S3 bucket name")
    ap.add_argument("--key-pair", required=True,
                    help="EC2 key pair name (Phase A Step 6)")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--commit", default="main",
                    help="git commit/branch to check out on each instance")
    ap.add_argument("--phase", default="1a-beta")
    ap.add_argument("--start", default="2020-01-02")
    ap.add_argument("--end", default="2026-04-30")
    ap.add_argument("--workers", type=int, default=12,
                    help="--screen-pool-workers per instance (default 12 of 16 vCPU)")
    ap.add_argument("--instance-type", default="c7a.4xlarge",
                    help="EC2 instance type (default c7a.4xlarge = 16 vCPU AMD)")
    ap.add_argument("--ami-id", default=None,
                    help="EC2 AMI id (default: resolve from SSM)")
    ap.add_argument("--repo-url",
                    default="https://github.com/jeetmehta1991/stock-picks-app.git")
    ap.add_argument("--security-group", default="batch395-ssh",
                    help="security group name (auto-created if missing)")
    ap.add_argument("--volume-gb", type=int, default=50,
                    help="root EBS volume size in GB")
    ap.add_argument("--spot", action="store_true",
                    help="use spot pricing (~40%% cheaper, possible reclaim)")
    ap.add_argument("--spot-max-price", default="0.30",
                    help="max spot bid price (default $0.30/hr)")
    ap.add_argument("--batches", type=int, default=5,
                    help="number of batches/instances to launch (default 5)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be launched; do not actually launch")
    args = ap.parse_args()

    if args.ami_id is None:
        print("[INFO] resolving latest Ubuntu 24.04 AMI from SSM...")
        ami_id = resolve_ami_from_ssm(args.region)
        print(f"[INFO] AMI: {ami_id}")
    else:
        ami_id = args.ami_id

    sg_id = ensure_security_group(args.region, args.security_group)
    profile_name = ensure_instance_profile(args.region)

    print(f"\n[INIT] Launching {args.batches} x {args.instance_type} "
          f"({'spot' if args.spot else 'on-demand'}) in {args.region}")
    print(f"[INIT] AMI={ami_id} SG={sg_id} IAM={profile_name}")
    print(f"[INIT] commit={args.commit} phase={args.phase} workers={args.workers}")
    print()

    launched = []
    for batch_index in range(1, args.batches + 1):
        user_data = build_user_data(
            batch_index, args.bucket, args.commit, args.phase,
            args.start, args.end, args.workers, args.repo_url,
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
            f"ResourceType=instance,Tags=[{{Key=batch,Value=batch395}},"
            f"{{Key=batch_index,Value={batch_index}}},"
            f"{{Key=Name,Value=batch395-instance-{batch_index}}}]",
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
            print(f"[DRY-RUN] batch_{batch_index}: would launch with cmd "
                  f"(user-data redacted, {len(user_data)} chars b64)")
            launched.append(("dry-run-batch-" + str(batch_index), "DRY", "DRY"))
            continue

        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print(f"[FAIL] batch_{batch_index} launch: {r.stderr}")
            continue
        instance_id = r.stdout.strip()
        print(f"[OK] batch_{batch_index}: launched {instance_id}")
        launched.append((f"batch_{batch_index}", instance_id, ""))

    if args.dry_run:
        return 0

    # Wait a moment then fetch public IPs
    print("\n[INIT] waiting 30s for instances to publish IPs...")
    time.sleep(30)

    print("\n=== Launched instances ===")
    for batch, instance_id, _ in launched:
        r = subprocess.run(
            ["aws", "ec2", "describe-instances", "--region", args.region,
             "--instance-ids", instance_id,
             "--query", "Reservations[0].Instances[0].PublicDnsName",
             "--output", "text"],
            capture_output=True, text=True, timeout=30,
        )
        dns = r.stdout.strip() if r.returncode == 0 else "pending"
        print(f"  {batch}: {instance_id}  ssh ubuntu@{dns}")

    print()
    print("Next steps:")
    print(f"  1. tail user-data log via ssh ubuntu@<dns> -i <pem>")
    print(f"     sudo tail -f /var/log/batch395-bootstrap.log")
    print(f"  2. monitor via: python scripts/aws_batch395_monitor.py "
          f"--bucket {args.bucket}")
    print(f"  3. when all 5 _COMPLETE sentinels in s3, merge via:")
    print(f"     python scripts/aws_batch395_merge.py --bucket {args.bucket}")

    # Write a session-state file for the monitor + merge to consume
    state = {
        "launched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bucket": args.bucket,
        "region": args.region,
        "commit": args.commit,
        "instances": {batch: instance_id for batch, instance_id, _ in launched},
    }
    state_path = REPO / "scripts" / "aws_batch395_state.json"
    state_path.write_text(json.dumps(state, indent=2))
    print(f"\n[INFO] state written to {state_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
