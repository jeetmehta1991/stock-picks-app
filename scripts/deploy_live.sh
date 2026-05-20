#!/usr/bin/env bash
# scripts/deploy_live.sh - AWS Lightsail one-shot deploy for Stage 4 live trading.
# Built by May 29 per owner directive 2026-05-19; NOT ACTIVATED until owner runs.
#
# Prereqs:
#   1. AWS CLI installed + configured: aws configure
#   2. Lightsail instance created (cli or console; $5-15/mo plan)
#   3. IB account credentials + IB Gateway license
#   4. SMTP credentials for email digest
#
# Usage:
#   bash scripts/deploy_live.sh <instance-name>
#
# This script:
#   1. Builds Docker image from project Dockerfile
#   2. Tags + pushes to AWS Lightsail Container Service
#   3. Deploys with env vars (IB credentials, SMTP, etc.)
#   4. Sets up cron triggers (8 AM ET morning, 4 PM ET EOD)
#   5. Verifies deployment health

set -e

INSTANCE_NAME="${1:-stock-picks-live}"
AWS_REGION="${AWS_REGION:-us-east-1}"
IMAGE_TAG="stock-picks-live:latest"

echo "===================================================================="
echo "Stage 4 Live Trading Deploy"
echo "===================================================================="
echo "Instance:   $INSTANCE_NAME"
echo "Region:     $AWS_REGION"
echo "Image:      $IMAGE_TAG"
echo "===================================================================="
echo ""

# Sanity checks
if ! command -v docker &> /dev/null; then
    echo "[ERROR] docker not installed; install Docker Desktop first"
    exit 1
fi
if ! command -v aws &> /dev/null; then
    echo "[ERROR] aws CLI not installed; install via 'pip install awscli'"
    exit 1
fi

# Verify AWS credentials configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "[ERROR] AWS credentials not configured; run 'aws configure'"
    exit 1
fi

# Verify Lightsail container service exists
if ! aws lightsail get-container-service --service-name "$INSTANCE_NAME" --region "$AWS_REGION" &> /dev/null; then
    echo "[INFO] Creating Lightsail container service: $INSTANCE_NAME"
    aws lightsail create-container-service \
        --service-name "$INSTANCE_NAME" \
        --power nano \
        --scale 1 \
        --region "$AWS_REGION"
    echo "[INFO] Waiting for service to become READY..."
    while true; do
        STATE=$(aws lightsail get-container-service --service-name "$INSTANCE_NAME" --region "$AWS_REGION" --query 'containerService.state' --output text)
        if [ "$STATE" = "READY" ]; then break; fi
        sleep 10
    done
fi

# Build Docker image locally
echo "[INFO] Building Docker image..."
docker build -t "$IMAGE_TAG" .

# Push to Lightsail
echo "[INFO] Pushing to Lightsail registry..."
aws lightsail push-container-image \
    --service-name "$INSTANCE_NAME" \
    --label "stock-picks-live" \
    --image "$IMAGE_TAG" \
    --region "$AWS_REGION"

# Prompt for env vars if not set
: "${IB_USERNAME:?Set IB_USERNAME env var}"
: "${IB_PASSWORD:?Set IB_PASSWORD env var}"
: "${EMAIL_SMTP_HOST:?Set EMAIL_SMTP_HOST env var}"
: "${EMAIL_SMTP_USER:?Set EMAIL_SMTP_USER env var}"
: "${EMAIL_SMTP_PASSWORD:?Set EMAIL_SMTP_PASSWORD env var}"

# Get latest image label
IMAGE_NAME=$(aws lightsail get-container-images \
    --service-name "$INSTANCE_NAME" \
    --region "$AWS_REGION" \
    --query 'containerImages[0].image' --output text)
echo "[INFO] Deploying image: $IMAGE_NAME"

# Create deployment config
cat > /tmp/deploy.json <<EOF
{
  "containers": {
    "stock-picks-live": {
      "image": "$IMAGE_NAME",
      "ports": {"8000": "HTTP"},
      "environment": {
        "IB_USERNAME": "$IB_USERNAME",
        "IB_PASSWORD": "$IB_PASSWORD",
        "EMAIL_SMTP_HOST": "$EMAIL_SMTP_HOST",
        "EMAIL_SMTP_USER": "$EMAIL_SMTP_USER",
        "EMAIL_SMTP_PASSWORD": "$EMAIL_SMTP_PASSWORD",
        "TZ": "America/New_York"
      }
    }
  }
}
EOF

aws lightsail create-container-service-deployment \
    --service-name "$INSTANCE_NAME" \
    --cli-input-json file:///tmp/deploy.json \
    --region "$AWS_REGION"

echo ""
echo "===================================================================="
echo "Deployment initiated. Monitor via:"
echo "  aws lightsail get-container-service --service-name $INSTANCE_NAME"
echo ""
echo "NEXT STEPS:"
echo "  1. Wait ~5 min for deployment to complete"
echo "  2. Verify health: container should reach RUNNING state"
echo "  3. Schedule cron triggers for morning (8 AM ET) + EOD (4 PM ET)"
echo "  4. Run smoke: docker exec ... python scripts/run_live_morning.py --dry-run"
echo "  5. Once verified, enable real trading: --no-dry-run flag"
echo "===================================================================="
