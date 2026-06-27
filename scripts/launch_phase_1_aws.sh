#!/usr/bin/env bash
# Source: Council 112 Action-5 COMPREHENSIVE bundle per owner directive
# 2026-06-27 'Approve all. Proceed. Arm monitor. Council this.' per
# CHECKLIST #77.
#
# Phase 1 AWS cloud smoke launch script
# - 1x c6a.4xlarge spot instance
# - NVDA single-ticker x full 217-strategy x 26-exit cube x full 6.41yr
# - ~30 min runtime expected, ~$0.20 spot cost
# - B1019 Monitor armed inside instance + S3-sync log to laptop
#
# PRECONDITIONS (owner-confirmed B1020 audit):
#   - AWS account active + IAM role with EC2/S3/CloudWatch permissions
#   - S3 bucket provisioned (default: change BUCKET_NAME below)
#   - AMI / Docker image ready with venv + pandas-ta + scipy + freezegun
#   - aws cli installed locally + credentials configured (aws configure)
#
# USAGE:
#   bash scripts/launch_phase_1_aws.sh <BUCKET_NAME>
#
# CONFIGURATION (edit before first run):
#   BUCKET_NAME           - S3 bucket for cache + results
#   AMI_ID                - Pre-built AMI with deps installed
#   IAM_INSTANCE_PROFILE  - IAM role with S3 + CloudWatch perms
#   SUBNET_ID             - VPC subnet for instance
#   KEY_NAME              - SSH key for emergency access (optional)
#   SECURITY_GROUP_ID     - Security group with outbound HTTPS
#
# COST CAP: hard ceiling at $2 (B1019 monitor halts at >10x baseline cost)
set -euo pipefail

BUCKET_NAME="${1:-stock-picks-phase-1-aws}"
AMI_ID="${AMI_ID:-ami-CHANGEME}"
INSTANCE_TYPE="c6a.4xlarge"
IAM_INSTANCE_PROFILE="${IAM_INSTANCE_PROFILE:-stock-picks-phase-1-role}"
SUBNET_ID="${SUBNET_ID:-subnet-CHANGEME}"
KEY_NAME="${KEY_NAME:-stock-picks-phase-1-key}"
SECURITY_GROUP_ID="${SECURITY_GROUP_ID:-sg-CHANGEME}"

PHASE_1_TICKER="${PHASE_1_TICKER:-NVDA}"
PHASE_1_OUTPUT_DIR="output_phase_1_aws"
RUN_ID="phase_1_$(date +%Y%m%d_%H%M%S)"

echo "B1021 PHASE 1 AWS LAUNCH"
echo "========================"
echo "Bucket:    $BUCKET_NAME"
echo "Ticker:    $PHASE_1_TICKER"
echo "Instance:  $INSTANCE_TYPE (spot)"
echo "Run ID:    $RUN_ID"
echo ""

# Step 1: Upload local cache to S3
echo "Step 1: S3 cache upload (~3 GB; ~10-20 min at home BW)..."
aws s3 sync backtest/data/cache/ s3://${BUCKET_NAME}/cache/ \
    --exclude "*.tmp" --exclude "__pycache__/*" --no-progress
aws s3 sync data_prefetch/ s3://${BUCKET_NAME}/data_prefetch/ \
    --exclude "*.tmp" --exclude "__pycache__/*" --no-progress
echo "Step 1 OK"
echo ""

# Step 2: Generate user-data bootstrap script
echo "Step 2: Generating user-data bootstrap..."
cat > /tmp/${RUN_ID}_userdata.sh <<'BOOTSTRAP_EOF'
#!/bin/bash
set -euxo pipefail
exec > >(tee /var/log/phase_1_bootstrap.log) 2>&1

# Pull repo + cache from S3
cd /home/ec2-user
git clone https://github.com/jeetmehta1991/stock-picks-app.git
cd stock-picks-app

# Pull cache from S3
aws s3 sync s3://BUCKET_PLACEHOLDER/cache/ backtest/data/cache/
aws s3 sync s3://BUCKET_PLACEHOLDER/data_prefetch/ data_prefetch/

# Activate Python env (assumes AMI has venv pre-built at /opt/venv)
source /opt/venv/bin/activate || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || true

# Phase 0 audit (re-verify on AWS instance)
python scripts/b1019_a5_phase_1_preflight_coverage_check.py \
    --ticker TICKER_PLACEHOLDER --start 2020-01-01 --end 2026-06-22 \
    --output output_phase_1_aws/preflight_check.json

# Start runtime monitor in background
mkdir -p output_phase_1_aws
python scripts/b1019_phase_1_runtime_monitor.py \
    --engine-state output_phase_1_aws/engine_state.json \
    --trade-log output_phase_1_aws/trade_log.parquet \
    --baseline output_audit/b660_fire_count_measured.json \
    --checkpoint-cadence 100 \
    --total-days 1610 \
    --total-cells 5642 \
    --poll-seconds 30 \
    > output_phase_1_aws/runtime_monitor.log 2>&1 &
MONITOR_PID=$!

# Sync monitor log to S3 every 60s (background)
(while kill -0 $MONITOR_PID 2>/dev/null; do
    aws s3 cp output_phase_1_aws/runtime_monitor.log \
        s3://BUCKET_PLACEHOLDER/RUNID_PLACEHOLDER/runtime_monitor.log
    sleep 60
done) &
SYNC_PID=$!

# Launch Phase 1 cube
python -m backtest.run_phase1a \
    --phase 1a-beta \
    --tickers TICKER_PLACEHOLDER \
    --no-news \
    --no-git \
    --no-walk-forward \
    --output-dir output_phase_1_aws \
    --screen-pool-workers 16

# Final sync
kill $SYNC_PID 2>/dev/null || true
aws s3 sync output_phase_1_aws/ s3://BUCKET_PLACEHOLDER/RUNID_PLACEHOLDER/results/

# Self-terminate
sudo shutdown -h +1
BOOTSTRAP_EOF

sed -i "s|BUCKET_PLACEHOLDER|$BUCKET_NAME|g" /tmp/${RUN_ID}_userdata.sh
sed -i "s|TICKER_PLACEHOLDER|$PHASE_1_TICKER|g" /tmp/${RUN_ID}_userdata.sh
sed -i "s|RUNID_PLACEHOLDER|$RUN_ID|g" /tmp/${RUN_ID}_userdata.sh
echo "Step 2 OK"
echo ""

# Step 3: Request spot instance
echo "Step 3: Requesting c6a.4xlarge spot instance..."
SPOT_REQUEST_OUTPUT=$(aws ec2 request-spot-instances \
    --spot-price "0.25" \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification "{
        \"ImageId\": \"$AMI_ID\",
        \"InstanceType\": \"$INSTANCE_TYPE\",
        \"KeyName\": \"$KEY_NAME\",
        \"SubnetId\": \"$SUBNET_ID\",
        \"SecurityGroupIds\": [\"$SECURITY_GROUP_ID\"],
        \"IamInstanceProfile\": {\"Name\": \"$IAM_INSTANCE_PROFILE\"},
        \"UserData\": \"$(base64 -w0 /tmp/${RUN_ID}_userdata.sh)\"
    }")
SPOT_REQUEST_ID=$(echo "$SPOT_REQUEST_OUTPUT" | jq -r '.SpotInstanceRequests[0].SpotInstanceRequestId')
echo "Spot request ID: $SPOT_REQUEST_ID"
echo ""

# Step 4: Watch for instance + sync log back
echo "Step 4: Watching for spot instance + monitor log..."
echo "Monitor log will sync to: s3://${BUCKET_NAME}/${RUN_ID}/runtime_monitor.log"
echo "Pull locally with: aws s3 cp s3://${BUCKET_NAME}/${RUN_ID}/runtime_monitor.log output_phase_1_aws/"
echo ""
echo "DONE. Monitor: aws s3 cp s3://${BUCKET_NAME}/${RUN_ID}/runtime_monitor.log -"
echo "Cost ceiling: \$2 (auto-halt at >10x baseline per B1019 STOP-S3)"
echo ""
echo "Final results pull (after run completes ~30 min):"
echo "  aws s3 sync s3://${BUCKET_NAME}/${RUN_ID}/results/ output_phase_1_aws/"
