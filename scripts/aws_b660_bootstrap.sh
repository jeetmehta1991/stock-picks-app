#!/bin/bash
# B695 (2026-06-11): EC2 bootstrap to run measure_fire_count.py on a per-
# instance ticker shard with B694 multiprocessing (--n-workers).
#
# Pattern adapted from scripts/aws_batch395_bootstrap.sh (B395). Same
# Ubuntu 24.04 AMI, same IAM role (batch395-instance-role), same S3
# sync pattern, same tmux-based engine launch + S3 heartbeat + self-
# terminate. The DIFFERENCE is which Python script is run inside the
# tmux session: measure_fire_count.py instead of run_phase1a.
#
# Env vars provided by launch script (via user-data):
#   B660_INDEX     - 1..5 (which shard this instance handles)
#   B660_BUCKET    - S3 bucket name (e.g. stock-picks-batch395-jm-7421)
#   B660_COMMIT    - git commit SHA / branch (default: main)
#   B660_START     - --start date (default: 2020-01-01)
#   B660_END       - --end date (default: 2026-05-31)
#   B660_N_WORKERS - --n-workers (default: 14 of 16 vCPU on c7a.4xlarge)
#   B660_REPO_URL  - git clone URL (default jeetmehta1991/stock-picks-app)
#   B660_TICKERS   - SMOKE MODE: comma-separated ticker list (bypasses splits)
#   B660_SPLITS_KEY - S3 key for splits.json (default aws_b660_splits.json)
#   B660_OUTPUT_KEY_PREFIX - S3 prefix for output files (default b660_outputs/)
#
# Exits 0 on success, non-zero on failure (instance stays up for diagnosis).
# Auto-terminates self at end on success.
set -euo pipefail
exec > >(tee /var/log/b660-bootstrap.log) 2>&1
echo "[$(date)] B660 (B695) bootstrap START -- index=${B660_INDEX:?} bucket=${B660_BUCKET:?}"

# Defaults
: "${B660_START:=2020-01-01}"
: "${B660_END:=2026-05-31}"
: "${B660_N_WORKERS:=14}"
: "${B660_COMMIT:=main}"
: "${B660_REPO_URL:=https://github.com/jeetmehta1991/stock-picks-app.git}"
: "${B660_SPLITS_KEY:=aws_b660_splits.json}"
: "${B660_OUTPUT_KEY_PREFIX:=b660_outputs}"

# Phase 1: system prereqs (same as B395)
echo "[$(date)] Installing system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3.12 python3.12-venv python3-pip git unzip tmux \
    build-essential libatlas-base-dev

# AWS CLI v2 (Ubuntu ships v1)
if ! command -v aws &>/dev/null; then
    curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
    cd /tmp && unzip -q awscliv2.zip && ./aws/install
    cd /
fi
echo "[$(date)] aws-cli: $(aws --version 2>&1)"

# Phase 2: clone repo + checkout target commit
echo "[$(date)] Cloning repo..."
cd /opt
git clone "$B660_REPO_URL" stock-picks-app
cd stock-picks-app
git checkout "$B660_COMMIT"
echo "[$(date)] On commit: $(git rev-parse HEAD)"

# Phase 3: python venv + deps
echo "[$(date)] Installing python deps..."
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# B696 (2026-06-11) fix: install vendored smartmoneyconcepts library. Without
# this, the smc_ict producer silently fails with ModuleNotFoundError, and
# all 18 SMC strategies + ICT-7/8/9/10 (Turtle Soup + Judas Swing) emit
# zero fires regardless of underlying signal. This was discovered during the
# B695 smoke run -- exactly what the smoke gate exists to catch per
# CHECKLIST #13. The requirements.txt header documents the manual install
# step but the B395 bootstrap (which this script was adapted from) didn't
# include it because B395 ran run_phase1a which doesn't gate on SMC signals.
if [ -d vendored/smartmoneyconcepts ]; then
    echo "[$(date)] Installing vendored smartmoneyconcepts library..."
    pip install -e vendored/smartmoneyconcepts/
else
    echo "[$(date)] WARNING: vendored/smartmoneyconcepts/ not present -- SMC producer will silent-fail" >&2
fi
echo "[$(date)] python: $(python --version)"

# Phase 4: pull prefetch data from S3 (instance IAM role grants read access)
echo "[$(date)] Syncing data_prefetch/ from s3://$B660_BUCKET/data_prefetch/..."
mkdir -p data_prefetch
aws s3 sync "s3://$B660_BUCKET/data_prefetch/" data_prefetch/ \
    --no-progress --only-show-errors

# Universe csvs
mkdir -p "Backtesting universe"
aws s3 sync "s3://$B660_BUCKET/Backtesting universe/" "Backtesting universe/" \
    --no-progress --only-show-errors

echo "[$(date)] Data sync complete. Disk usage:"
df -h /

# Phase 5: determine ticker subset for this shard
# Smoke override: when B660_TICKERS is set in user-data env, use it directly
if [ -n "${B660_TICKERS:-}" ]; then
    TICKERS_CSV="$B660_TICKERS"
    echo "[$(date)] SMOKE MODE: using env-supplied ticker list ($(echo "$TICKERS_CSV" | tr ',' '\n' | wc -l) tickers)"
else
    echo "[$(date)] Resolving tickers for shard_${B660_INDEX}..."
    aws s3 cp "s3://$B660_BUCKET/$B660_SPLITS_KEY" /tmp/b660_splits.json \
        --no-progress --only-show-errors
    TICKERS_CSV=$(python -c "
import json
splits = json.load(open('/tmp/b660_splits.json'))
key = f'shard_${B660_INDEX}'
print(','.join(splits[key]))
")
fi
TICKER_COUNT=$(echo "$TICKERS_CSV" | tr ',' '\n' | wc -l)
echo "[$(date)] Shard $B660_INDEX -> $TICKER_COUNT tickers"

# Convert comma-separated TICKERS_CSV to space-separated for the
# --ticker-subset CLI flag (nargs='+' takes space-separated args).
TICKERS_SPACE=$(echo "$TICKERS_CSV" | tr ',' ' ')

# Phase 6: launch measure_fire_count.py in tmux
OUTPUT_FILE="output_audit/b660_shard_${B660_INDEX}.json"
mkdir -p output_audit
echo "[$(date)] Launching measure_fire_count.py in tmux session b660_shard..."
tmux new-session -d -s b660_shard bash -lc "
    cd /opt/stock-picks-app
    source .venv/bin/activate
    # B939 (2026-06-20) Council 47 explicit-intent declaration per
    # Council 46 Option B sequencing. TIER 2 producer injection enabled
    # for Phase P1 production fire-count measurements. Adding ~44
    # TIER 2-dependent strategies that were silenced pre-B922.
    # Comparability vs B660 v1 outputs: NOT preserved here (B660 v1
    # was pre-B922 baseline; replay would require --no-tier2).
    python scripts/measure_fire_count.py \\
        --all \\
        --ticker-subset $TICKERS_SPACE \\
        --n-workers $B660_N_WORKERS \\
        --start $B660_START \\
        --end $B660_END \\
        --include-tier2 \\
        --output $OUTPUT_FILE \\
        2>&1 | tee /var/log/b660-engine.log
    echo \"[ENGINE-DONE \$?] \$(date)\" >> /var/log/b660-engine.log
"

# Phase 7: poll tmux session; report progress to S3 every 5 min
echo "[$(date)] Engine launched. Polling completion..."
START_EPOCH=$(date +%s)
while tmux has-session -t b660_shard 2>/dev/null; do
    ELAPSED=$(( $(date +%s) - START_EPOCH ))
    {
        echo "ts=$(date -u +%FT%TZ)"
        echo "shard_index=$B660_INDEX"
        echo "elapsed_seconds=$ELAPSED"
        echo "tmux=alive"
        tail -3 /var/log/b660-engine.log 2>/dev/null || true
    } | aws s3 cp - "s3://$B660_BUCKET/$B660_OUTPUT_KEY_PREFIX/heartbeat_$B660_INDEX.txt" \
        --no-progress --only-show-errors 2>&1 || true
    sleep 300
done
ELAPSED=$(( $(date +%s) - START_EPOCH ))
echo "[$(date)] Engine session ended after ${ELAPSED}s"

# Phase 8: upload output to S3
echo "[$(date)] Uploading $OUTPUT_FILE to s3://$B660_BUCKET/$B660_OUTPUT_KEY_PREFIX/shard_${B660_INDEX}.json..."
aws s3 cp "$OUTPUT_FILE" \
    "s3://$B660_BUCKET/$B660_OUTPUT_KEY_PREFIX/shard_${B660_INDEX}.json" \
    --no-progress --only-show-errors || true

# Logs
aws s3 cp /var/log/b660-engine.log \
    "s3://$B660_BUCKET/$B660_OUTPUT_KEY_PREFIX/shard_${B660_INDEX}_engine.log" \
    --no-progress --only-show-errors || true
aws s3 cp /var/log/b660-bootstrap.log \
    "s3://$B660_BUCKET/$B660_OUTPUT_KEY_PREFIX/shard_${B660_INDEX}_bootstrap.log" \
    --no-progress --only-show-errors || true

# Sentinel
echo "$(date -u +%FT%TZ) elapsed=${ELAPSED}s" | \
    aws s3 cp - "s3://$B660_BUCKET/$B660_OUTPUT_KEY_PREFIX/shard_${B660_INDEX}_COMPLETE" \
    --no-progress --only-show-errors

# Phase 9: self-terminate
echo "[$(date)] Self-terminating..."
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)
if [ -n "$TOKEN" ]; then
    INSTANCE_ID=$(curl -sH "X-aws-ec2-metadata-token: $TOKEN" \
        http://169.254.169.254/latest/meta-data/instance-id)
    aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" \
        --region us-east-1 --no-cli-pager || true
fi
echo "[$(date)] B660 (B695) Bootstrap DONE"
