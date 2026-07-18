"""scripts/aws_chunk_launch.py - R5 spot CHUNK launcher (B1303 Council 336).

# Source: per CHECKLIST #77 canonical-source; owner spot-sequential plan
# B1294; generalizes the smoke launcher (aws_smoke_launch.py) proven end-
# to-end incl. Gate 7 interrupt/resume (B1302).

Differences from smoke: pulls the chunk ticker list from S3 (presigned
GET, keeps user-data small), 16 screen-pool-workers (c6a.16xlarge =
64 vCPU), 8h hard cap, output_chunk<N>, S3 keys namespaced chunk<N>/.
Same Monitor v2 (60s heartbeat + 5-min periodic ckpt + IMDS watcher) and
self-terminate. --resume relaunches pulling the last checkpoint.

Usage: python scripts/aws_chunk_launch.py --chunk 2 [--resume]
"""
from __future__ import annotations

import argparse
import base64
import sys

import boto3

BUCKET = "stock-picks-r5-jm-2026"
REGION = "us-east-1"
INSTANCE_TYPE = "c6a.16xlarge"
SPOT_MAX_PRICE = "1.40"
MAX_RUN_HOURS = "8.0"
POOL_WORKERS = "16"

USERDATA_TEMPLATE = r"""#!/bin/bash
exec > /var/log/r5chunk.log 2>&1
set -x
echo "R5CHUNK@N@ BOOT $(date -u +%FT%TZ)"
dnf install -y python3.11 python3.11-pip tar >/dev/null
mkdir -p /r5 && cd /r5
curl -sf -o code.tar "@CODE_GET@" && tar -xf code.tar && rm code.tar
curl -sf -o payload.tar "@PAYLOAD_GET@" && tar -xf payload.tar && rm payload.tar
curl -sf -o chunk_tickers.txt "@TICKERS_GET@"
python3.11 -m pip install --quiet -r requirements.txt
RESUME_ARGS=""
if [ "@RESUME@" = "1" ]; then
  curl -sf -o ckpt.tar "@CKPT_GET@" && tar -xf ckpt.tar && RESUME_ARGS="--resume-from-checkpoint output_chunk@N@"
fi
# Monitor v2a: heartbeat every 60s + periodic checkpoint every 5th beat
( N=0; while true; do
    { echo "hb_utc=$(date -u +%FT%TZ)"; cat output_chunk@N@/engine_state.json 2>/dev/null; } > /tmp/hb.txt
    curl -sf -X PUT -T /tmp/hb.txt "@HB_PUT@" || true
    N=$((N+1))
    if [ $((N % 5)) -eq 0 ] && [ -d output_chunk@N@ ]; then
      tar -cf /tmp/ckpt.tar output_chunk@N@ 2>/dev/null
      curl -sf -X PUT -T /tmp/ckpt.tar "@CKPT_PUT@" || true
    fi
    sleep 60
  done ) &
# Monitor v2b: IMDS spot-interruption watcher (2-min notice -> flush ckpt)
( while true; do
    TOK=$(curl -sf -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
    if curl -sf -H "X-aws-ec2-metadata-token: $TOK" http://169.254.169.254/latest/meta-data/spot/instance-action | grep -q action; then
      echo "IMDS INTERRUPTION NOTICE $(date -u +%FT%TZ)"
      tar -cf /tmp/ckpt.tar output_chunk@N@ 2>/dev/null
      curl -sf -X PUT -T /tmp/ckpt.tar "@CKPT_PUT@" || true
    fi
    sleep 5
  done ) &
export EMIT_RAW_SIGNAL_FIRES=1 PYTHONIOENCODING=utf-8
# Gate 6 (CHECKLIST #158): emit environment fingerprint before the engine
# burns compute; a monfri_fallback backend here = degraded grid (L207).
mkdir -p output_chunk@N@
python3.11 scripts/env_fingerprint.py --emit output_chunk@N@/env_fingerprint.json || true
TICK=$(cat chunk_tickers.txt)
python3.11 -m backtest.run_phase1a --phase 1a-beta --tickers "$TICK" \
  --start 2022-05-05 --end 2026-05-05 --no-news --no-walk-forward --no-agents \
  --no-git --no-portfolio-cap --no-dd-halt --screen-pool-workers @POOL@ \
  --max-run-hours @MAXH@ --warn-run-hours 7.0 --output-dir output_chunk@N@ $RESUME_ARGS
echo "ENGINE EXIT $? $(date -u +%FT%TZ)"
tar -cf /tmp/artifacts.tar output_chunk@N@
curl -sf -X PUT -T /tmp/artifacts.tar "@ART_PUT@"
{ echo "hb_utc=$(date -u +%FT%TZ)"; echo "CHUNK@N@_COMPLETE"; } > /tmp/hb.txt
curl -sf -X PUT -T /tmp/hb.txt "@HB_PUT@"
shutdown -h now
"""


def presign(s3, method, key, expires=172800):
    op = "get_object" if method == "get" else "put_object"
    kw = {"Bucket": BUCKET, "Key": key}
    if method == "get":
        return s3.generate_presigned_url(op, Params=kw, ExpiresIn=expires)
    return s3.generate_presigned_url(op, Params=kw, ExpiresIn=expires,
                                     HttpMethod="PUT")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk", type=int, required=True)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    n = str(args.chunk)

    s3 = boto3.client("s3", region_name=REGION)
    ud = USERDATA_TEMPLATE
    subs = {
        "@N@": n,
        "@CODE_GET@": presign(s3, "get", "payload/r5_code.tar"),
        "@PAYLOAD_GET@": presign(s3, "get", "payload/r5_payload.tar"),
        "@TICKERS_GET@": presign(s3, "get", f"chunks/chunk{n}_tickers.txt"),
        "@CKPT_GET@": presign(s3, "get", f"chunk{n}/ckpt.tar"),
        "@HB_PUT@": presign(s3, "put", f"chunk{n}/heartbeat.txt"),
        "@CKPT_PUT@": presign(s3, "put", f"chunk{n}/ckpt.tar"),
        "@ART_PUT@": presign(s3, "put", f"chunk{n}/artifacts.tar"),
        "@RESUME@": "1" if args.resume else "0",
        "@POOL@": POOL_WORKERS, "@MAXH@": MAX_RUN_HOURS,
    }
    for k, v in subs.items():
        ud = ud.replace(k, v)
    b64 = base64.b64encode(ud.encode()).decode()
    print(f"Gate 1: user-data raw={len(ud)}B b64={len(b64)}B (limit 16384)")
    if len(b64) > 16384:
        print("GATE 1 FAIL - externalize to S3")
        return 1
    print("Gate 3 monitor-in-userdata:",
          "PASS" if ("instance-action" in ud and "hb.txt" in ud) else "FAIL")

    ec2 = boto3.client("ec2", region_name=REGION)
    amis = ec2.describe_images(
        Owners=["amazon"],
        Filters=[{"Name": "name", "Values": ["al2023-ami-2023*-x86_64"]},
                 {"Name": "state", "Values": ["available"]}])
    ami = sorted(amis["Images"], key=lambda i: i["CreationDate"])[-1]["ImageId"]

    resp = ec2.run_instances(
        ImageId=ami, InstanceType=INSTANCE_TYPE, MinCount=1, MaxCount=1,
        InstanceMarketOptions={"MarketType": "spot", "SpotOptions": {
            "MaxPrice": SPOT_MAX_PRICE, "SpotInstanceType": "one-time",
            "InstanceInterruptionBehavior": "terminate"}},
        InstanceInitiatedShutdownBehavior="terminate",
        BlockDeviceMappings=[{"DeviceName": "/dev/xvda", "Ebs": {
            "VolumeSize": 60, "VolumeType": "gp3", "DeleteOnTermination": True}}],
        UserData=ud,
        TagSpecifications=[{"ResourceType": "instance", "Tags": [
            {"Key": "Name", "Value": f"r5-chunk{n}"}]}],
    )
    print(f"LAUNCHED chunk{n}:", resp["Instances"][0]["InstanceId"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
