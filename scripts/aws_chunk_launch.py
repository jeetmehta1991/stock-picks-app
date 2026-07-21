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
import subprocess
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
# B1326 (Council 358, B4): install the vendored smartmoneyconcepts package so
# the bare `import smartmoneyconcepts` (vendored __init__) resolves on cloud.
# Local venv has it pip-installed; cloud only had the vendored dir -> the 22
# SMC/ICT strategies were silent (B1317). setup.py is tracked -> -e install works.
python3.11 -m pip install --quiet -e vendored/smartmoneyconcepts/ || echo "SMC_VENDORED_INSTALL_FAILED"
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
# B1328 (Council 360): HARD pre-engine gate - abort with ZERO engine spend if
# the env is bad (smc_active / calendar / code_sha). Every batch refuses to
# spend on a broken environment (owner directive).
if ! python3.11 scripts/preengine_gate.py output_chunk@N@/env_fingerprint.json "@EXPECT_SHA@"; then
  { echo "hb_utc=$(date -u +%FT%TZ)"; echo "CHUNK@N@_GATEFAIL"; } > /tmp/hb.txt
  curl -sf -X PUT -T /tmp/hb.txt "@HB_PUT@"
  curl -sf -X PUT -T /var/log/r5chunk.log "@LOG_PUT@" || true
  shutdown -h now
fi
TICK=$(cat chunk_tickers.txt)
python3.11 -m backtest.run_phase1a --phase 1a-beta --tickers "$TICK" \
  --start 2022-05-05 --end 2026-05-05 --no-news --no-walk-forward --no-agents \
  --no-git --no-portfolio-cap --no-dd-halt --cube-isolation --screen-pool-workers @POOL@ \
  --max-run-hours @MAXH@ --warn-run-hours 7.0 --output-dir output_chunk@N@ $RESUME_ARGS
echo "ENGINE EXIT $? $(date -u +%FT%TZ)"
tar -cf /tmp/artifacts.tar output_chunk@N@
curl -sf -X PUT -T /tmp/artifacts.tar "@ART_PUT@"
# B1312 FIX (class-level, generalization mandate): the completion marker must
# reflect ACTUAL window completion, not mere process exit. --max-run-hours and
# spot-interruption leave engine_state status='running' (backtest.py:1082 emits
# 'complete' ONLY after the full window finalizes). Writing CHUNK_COMPLETE
# unconditionally fooled the auto-resume controller -- chunk 2 capped at day 669
# (67%) yet was marked COMPLETE, so resumes=0 and the run stopped short. Gate the
# marker on status; emit CAPPED (which the controller treats as resume-needed)
# for every non-complete exit. Applies to all chunks + future spot runs.
ST=$(python3.11 -c "import json;print(json.load(open('output_chunk@N@/engine_state.json')).get('status',''))" 2>/dev/null)
DY=$(python3.11 -c "import json;print(json.load(open('output_chunk@N@/engine_state.json')).get('simulated_day',''))" 2>/dev/null)
if [ "$ST" = "complete" ]; then
  { echo "hb_utc=$(date -u +%FT%TZ)"; echo "CHUNK@N@_COMPLETE day=$DY"; } > /tmp/hb.txt
else
  { echo "hb_utc=$(date -u +%FT%TZ)"; echo "CHUNK@N@_CAPPED day=$DY status=$ST"; } > /tmp/hb.txt
fi
curl -sf -X PUT -T /tmp/hb.txt "@HB_PUT@"
# B1324 (Council 356): always upload the bootstrap/run log so failures are
# DIAGNOSABLE off-instance (no SSM in the presigned-URL pattern). Without this,
# a bootstrap failure is a black box (chunk-8 smoke produced empty output with
# no visible cause).
curl -sf -X PUT -T /var/log/r5chunk.log "@LOG_PUT@" || true
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
    # B1336 (freeze mechanism): the pre-engine gate's expected code SHA.
    # Default = git HEAD (ad-hoc smokes). Frozen batch sequences MUST pass the
    # sequence SHA (e.g. --expect-sha e846b6d2c) so the on-instance gate
    # validates against the frozen tar, not whatever HEAD has advanced to
    # (L212 -- the B1333 plan promised this flag before it existed).
    ap.add_argument("--expect-sha", default=None,
                    help="expected code SHA for the pre-engine gate "
                         "(default: current git HEAD)")
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
        "@LOG_PUT@": presign(s3, "put", f"chunk{n}/r5chunk.log"),
        "@CKPT_PUT@": presign(s3, "put", f"chunk{n}/ckpt.tar"),
        "@ART_PUT@": presign(s3, "put", f"chunk{n}/artifacts.tar"),
        "@RESUME@": "1" if args.resume else "0",
        "@POOL@": POOL_WORKERS, "@MAXH@": MAX_RUN_HOURS,
        # B1328/B1336: expected code SHA for the on-instance pre-engine gate.
        # --expect-sha (frozen sequences) overrides the HEAD default.
        "@EXPECT_SHA@": (args.expect_sha or subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip())[:12],
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
