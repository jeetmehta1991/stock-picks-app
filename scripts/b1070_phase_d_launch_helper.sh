#!/bin/bash
# B1070 Block-1 (Council 182 audit 2026-06-29) — Phase D R5 launch helper
# enforces EBS VolumeSize=100GB per CHECKLIST #131 EBS-DISK-SIZING-PREFLIGHT.
#
# Source: Sub-B F-11.1 finding (Phase 4 ~35-50GB output on 50GB EBS = OOM-
# disk risk; codified as CHECKLIST #131 but launch scripts continued using
# VolumeSize=50). Per `feedback_designed_vs_verified_requires_evidence_
# artifact`: codified rule + unimplemented in launch = DESIGNED-NOT-VERIFIED.
#
# Usage:
#   scripts/b1070_phase_d_launch_helper.sh <RUN_ID> <AZ> <USER_DATA_B64> <TAG>
#
# Replaces ad-hoc inline `aws ec2 run-instances` calls. All Phase D launches
# must use this helper OR explicit `VolumeSize=100` per CHECKLIST #131.
set -euo pipefail

RUN_ID="${1:?RUN_ID required}"
AZ="${2:?AZ required (us-east-1b/c/d/a/f)}"
USER_DATA_B64="${3:?USER_DATA_B64 required}"
TAG="${4:?TAG required (e.g. r5_full_b1071_phase_d)}"

declare -A AZ_SUBNET=(
    ["us-east-1b"]="subnet-0301c630e4693bae6"
    ["us-east-1c"]="subnet-082635ccb7752b1c1"
    ["us-east-1d"]="subnet-0941615be21e2e7af"
    ["us-east-1a"]="subnet-06ac2ee437b17a641"
    ["us-east-1f"]="subnet-0c24265a68a460ce7"
)

SUBNET="${AZ_SUBNET[$AZ]:?Unknown AZ $AZ}"

# B1070 Block-1: VolumeSize=100 (was 50; CHECKLIST #131 enforcement)
# Phase 4 output estimate:
#   trade_exit_detail.csv: 5-15GB (1929 tickers x ~25-50K trades x 25 exits)
#   cube CSVs + per-strategy outputs: ~5-10GB
#   engine.log: 1-2GB
#   data_prefetch cache: ~20GB
#   system: ~5GB
#   TOTAL: ~35-50GB; 100GB provides 2x safety margin per CHECKLIST #131.
aws ec2 run-instances \
    --image-id ami-08f44e8eca9095668 \
    --instance-type "${INSTANCE_TYPE:-c6a.16xlarge}" \
    --key-name batch395 \
    --security-group-ids sg-0de62cd41561ebc6b \
    --subnet-id "$SUBNET" \
    --iam-instance-profile Name=batch395-instance-role \
    --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":100,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
    --instance-market-options 'MarketType=spot,SpotOptions={MaxPrice=1.50,SpotInstanceType=one-time}' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$TAG}]" \
    --user-data "$USER_DATA_B64" \
    --query 'Instances[0].InstanceId' \
    --output text
