"""scripts/aws_smoke_launch.py - R5 spot smoke launcher (B1296 Council 331).

# Source: per CHECKLIST #77 canonical-source; owner-approved spot-sequential
# plan B1294-B1295; smoke = interrupted-and-resumed 5-ticker cube run
# (doubles as Gate 7 interruption drill).

Design (no instance IAM role needed -- r5-runner cannot PassRole):
  - Instance pulls code+payload via presigned GET; pushes heartbeat/
    checkpoint/artifacts via presigned PUT (48h expiry).
  - Monitor v2 on-instance: 60s heartbeat loop (engine_state -> S3);
    IMDS spot-interruption watcher (2-min notice -> checkpoint tar -> S3).
  - Hard caps: --max-run-hours per mode + instance self-shutdown with
    InstanceInitiatedShutdownBehavior=terminate (billing physically stops).

Usage:
  python scripts/aws_smoke_launch.py            # launch smoke
  python scripts/aws_smoke_launch.py --resume   # relaunch pulling checkpoint
Gate 1 (user-data <=16KB b64) checked before any spend.
"""
from __future__ import annotations

import argparse
import base64
import sys

import boto3

BUCKET = "stock-picks-r5-jm-2026"
REGION = "us-east-1"
INSTANCE_TYPE = "c6a.16xlarge"
SPOT_MAX_PRICE = "1.40"  # USD/hr cap (on-demand ~2.45; typical spot ~0.9-1.1)
TICKERS = "AAPL,ABBV,BAC,BTU,DIA"
MAX_RUN_HOURS = "1.5"

USERDATA_TEMPLATE = r"""#!/bin/bash
exec > /var/log/r5smoke.log 2>&1
set -x
echo "R5SMOKE BOOT $(date -u +%FT%TZ)"
dnf install -y python3.11 python3.11-pip tar >/dev/null
mkdir -p /r5 && cd /r5
curl -sf -o code.tar "@CODE_GET@" && tar -xf code.tar && rm code.tar
curl -sf -o payload.tar "@PAYLOAD_GET@" && tar -xf payload.tar && rm payload.tar
python3.11 -m pip install --quiet -r requirements.txt
# resume support: pull checkpoint bundle if present (Gate 7 drill relaunch)
RESUME_ARGS=""
if [ "@RESUME@" = "1" ]; then
  curl -sf -o ckpt.tar "@CKPT_GET@" && tar -xf ckpt.tar && RESUME_ARGS="--resume-from-checkpoint output_smoke"
fi
# Monitor v2a: heartbeat loop (engine_state -> S3 every 60s) + B1300
# periodic checkpoint sync every 5th beat: manual terminates and hard
# crashes send NO IMDS notice, so on-notice-only shipping loses all
# progress. Worst-case loss is now <=5 min regardless of death mode.
( N=0; while true; do
    { echo "hb_utc=$(date -u +%FT%TZ)"; cat output_smoke/engine_state.json 2>/dev/null; } > /tmp/hb.txt
    curl -sf -X PUT -T /tmp/hb.txt "@HB_PUT@" || true
    N=$((N+1))
    if [ $((N % 5)) -eq 0 ] && [ -d output_smoke ]; then
      tar -cf /tmp/ckpt.tar output_smoke 2>/dev/null
      curl -sf -X PUT -T /tmp/ckpt.tar "@CKPT_PUT@" || true
    fi
    sleep 60
  done ) &
# Monitor v2b: IMDS spot-interruption watcher (2-min notice -> flush checkpoint)
( TOK=""; while true; do
    TOK=$(curl -sf -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
    if curl -sf -H "X-aws-ec2-metadata-token: $TOK" http://169.254.169.254/latest/meta-data/spot/instance-action | grep -q action; then
      echo "IMDS INTERRUPTION NOTICE $(date -u +%FT%TZ)"
      tar -cf /tmp/ckpt.tar output_smoke 2>/dev/null
      curl -sf -X PUT -T /tmp/ckpt.tar "@CKPT_PUT@" || true
      echo "checkpoint flushed on notice"
    fi
    sleep 5
  done ) &
export EMIT_RAW_SIGNAL_FIRES=1 PYTHONIOENCODING=utf-8
python3.11 -m backtest.run_phase1a --phase 1a-beta --tickers @TICKERS@ \
  --start 2022-05-05 --end 2026-05-05 --no-news --no-walk-forward --no-agents \
  --no-git --no-portfolio-cap --no-dd-halt --screen-pool-workers 1 \
  --max-run-hours @MAXH@ --warn-run-hours 1.2 --output-dir output_smoke $RESUME_ARGS
echo "ENGINE EXIT $? $(date -u +%FT%TZ)"
tar -cf /tmp/artifacts.tar output_smoke
curl -sf -X PUT -T /tmp/artifacts.tar "@ART_PUT@"
echo "R5SMOKE DONE $(date -u +%FT%TZ)"
{ echo "hb_utc=$(date -u +%FT%TZ)"; echo "SMOKE_COMPLETE"; } > /tmp/hb.txt
curl -sf -X PUT -T /tmp/hb.txt "@HB_PUT@"
shutdown -h now
"""


def presign(s3, method, key, expires=172800):
    if method == "get":
        return s3.generate_presigned_url("get_object",
                                         Params={"Bucket": BUCKET, "Key": key},
                                         ExpiresIn=expires)
    return s3.generate_presigned_url("put_object",
                                     Params={"Bucket": BUCKET, "Key": key},
                                     ExpiresIn=expires, HttpMethod="PUT")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    s3 = boto3.client("s3", region_name=REGION)
    subs = {
        "@CODE_GET@": presign(s3, "get", "payload/r5_code.tar"),
        "@PAYLOAD_GET@": presign(s3, "get", "payload/r5_payload.tar"),
        "@CKPT_GET@": presign(s3, "get", "smoke/ckpt.tar"),
        "@HB_PUT@": presign(s3, "put", "smoke/heartbeat.txt"),
        "@CKPT_PUT@": presign(s3, "put", "smoke/ckpt.tar"),
        "@ART_PUT@": presign(s3, "put", "smoke/artifacts.tar"),
        "@RESUME@": "1" if args.resume else "0",
        "@TICKERS@": TICKERS, "@MAXH@": MAX_RUN_HOURS,
    }
    ud = USERDATA_TEMPLATE
    for k, v in subs.items():
        ud = ud.replace(k, v)
    b64 = base64.b64encode(ud.encode()).decode()
    print(f"Gate 1: user-data raw={len(ud)}B b64={len(b64)}B (limit 16384)")
    if len(b64) > 16384:
        print("GATE 1 FAIL - externalize to S3 (B1044 pattern)")
        return 1
    print("Gate 3: monitor-in-userdata grep:",
          "PASS" if ("instance-action" in ud and "hb.txt" in ud) else "FAIL")

    ec2 = boto3.client("ec2", region_name=REGION)
    amis = ec2.describe_images(
        Owners=["amazon"],
        Filters=[{"Name": "name", "Values": ["al2023-ami-2023*-x86_64"]},
                 {"Name": "state", "Values": ["available"]}])
    ami = sorted(amis["Images"], key=lambda i: i["CreationDate"])[-1]["ImageId"]
    print("AMI:", ami)

    resp = ec2.run_instances(
        ImageId=ami, InstanceType=INSTANCE_TYPE, MinCount=1, MaxCount=1,
        InstanceMarketOptions={"MarketType": "spot", "SpotOptions": {
            "MaxPrice": SPOT_MAX_PRICE, "SpotInstanceType": "one-time",
            "InstanceInterruptionBehavior": "terminate"}},
        InstanceInitiatedShutdownBehavior="terminate",
        BlockDeviceMappings=[{"DeviceName": "/dev/xvda", "Ebs": {
            "VolumeSize": 40, "VolumeType": "gp3",
            "DeleteOnTermination": True}}],
        UserData=ud,
        TagSpecifications=[{"ResourceType": "instance", "Tags": [
            {"Key": "Name", "Value": "r5-smoke"}]}],
    )
    iid = resp["Instances"][0]["InstanceId"]
    print("LAUNCHED:", iid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
