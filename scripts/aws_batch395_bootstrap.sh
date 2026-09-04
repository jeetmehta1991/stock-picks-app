#!/bin/bash
# Batch 395 EC2 bootstrap (runs on each instance at boot via user-data).
#
# Source (per CHECKLIST #77): owner directive 2026-05-27 Path 1 + AWS
# Spot/on-demand orchestration. Each c7a.4xlarge instance receives this
# as user-data; it runs once at boot, fully unattended.
#
# Env vars provided by launch script (via user-data):
#   BATCH395_INDEX     - 1..5 (which batch this instance handles)
#   BATCH395_BUCKET    - S3 bucket name (e.g. stock-picks-batch395-jm-7421)
#   BATCH395_COMMIT    - git commit SHA to check out (default: HEAD of main)
#   BATCH395_PHASE     - phase arg to run_phase1a (default: 1a-beta)
#   BATCH395_START     - --start date (default: 2020-01-02)
#   BATCH395_END       - --end date (default: 2026-04-30)
#   BATCH395_WORKERS   - --screen-pool-workers (default: 12)
#
# Exits 0 on success, non-zero on failure (instance stays up for diagnosis).
# Auto-terminates self at end on success.
set -euo pipefail
exec > >(tee /var/log/batch395-bootstrap.log) 2>&1
echo "[$(date)] Batch 395 bootstrap START -- index=${BATCH395_INDEX:?} bucket=${BATCH395_BUCKET:?}"

# Defaults
: "${BATCH395_PHASE:=1a-beta}"
: "${BATCH395_START:=2020-01-02}"
: "${BATCH395_END:=2026-04-30}"
: "${BATCH395_WORKERS:=12}"
: "${BATCH395_COMMIT:=main}"
: "${BATCH395_REPO_URL:=https://github.com/jeetmehta1991/stock-picks-app.git}"
# Batch 405 (2026-05-27 owner directive): wall-time guard override.
# Default 6h KILL is auto-set by run_phase1a for --phase=1a-beta.
# Pass BATCH395_MAX_HOURS to override (engine's --max-run-hours).
# Empty/unset means defaults apply.
: "${BATCH395_MAX_HOURS:=}"
: "${BATCH395_WARN_HOURS:=}"

# Phase 1: system prereqs
echo "[$(date)] Installing system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3.12 python3.12-venv python3-pip git unzip tmux \
    build-essential libatlas-base-dev

# AWS CLI v2 (Ubuntu ships v1; v2 has better S3 sync perf)
if ! command -v aws &>/dev/null; then
    curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
    cd /tmp && unzip -q awscliv2.zip && ./aws/install
    cd /
fi
echo "[$(date)] aws-cli: $(aws --version 2>&1)"

# Phase 2: clone repo + checkout target commit
echo "[$(date)] Cloning repo..."
cd /opt
git clone "$BATCH395_REPO_URL" stock-picks-app
cd stock-picks-app
git checkout "$BATCH395_COMMIT"
echo "[$(date)] On commit: $(git rev-parse HEAD)"

# Phase 3: python venv + deps
echo "[$(date)] Installing python deps..."
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# B901 (2026-06-18) fix: install vendored smartmoneyconcepts library. Without
# this, the smc_ict producer silently fails with ModuleNotFoundError, and
# all 18 SMC strategies + ICT-7/8/9/10 (Turtle Soup + Judas Swing) emit
# zero fires regardless of underlying signal. This is the SAME bug B696
# fixed in aws_b660_bootstrap.sh -- but the B696 author wrongly assumed
# "B395 bootstrap doesn't need it because run_phase1a doesn't gate on SMC."
# Council 23 (2026-06-18) verified: R4 May 31 ran run_phase1a via THIS
# bootstrap with 18 SMC strategies registered AND ZERO SMC trades fired.
# Diagnosed via B900 audit (output_audit/b900_r4_quiet_low_fire_audit.json):
# top 6 R4_QUIET_BUT_FIRES_POST_B689 are ALL smc_* strategies (16631 / 9054
# / 5676 / 4622 / 3429 / 3351 fires/yr in B660-ext vs 0 in R4 trades).
if [ -d vendored/smartmoneyconcepts ]; then
    echo "[$(date)] Installing vendored smartmoneyconcepts library..."
    pip install -e vendored/smartmoneyconcepts/
else
    echo "[$(date)] WARNING: vendored/smartmoneyconcepts/ not present -- SMC producer will silent-fail" >&2
fi
# numba may fail on python3.14 -- requirements has python_version<'3.14' constraint
echo "[$(date)] python: $(python --version)"
# B901 verification: confirm smc import succeeds before launching engine.
# B2587 (#245 / L759 sweep): the timestamp came from a command substitution
# INSIDE the double-quoted -c argument. Take it outside, and single-quote the
# python so nothing in it is substitutable.
SMC_TS=$(date)
python -c 'from vendored.smartmoneyconcepts.smartmoneyconcepts import smc; print("SMC library import OK")' 2>&1 && echo "[$SMC_TS] SMC library import OK" || {
    echo "[$(date)] FATAL: SMC library import FAILED -- aborting R5 launch to prevent R4-style silent-quiet bug" >&2
    exit 1
}

# B901 (DEFER-I): enable raw-signal fire emission so R5 outputs per-strategy
# pre-filter fire counts alongside trade_log. Council 23 verdict: this is the
# self-instrumentation that prevents another dual-harness divergence post-cube.
# Sidecar file: output/raw_signal_fires.<PID>.csv per worker; merge via
# scripts/merge_batch_outputs.py.
export EMIT_RAW_SIGNAL_FIRES=1
echo "[$(date)] EMIT_RAW_SIGNAL_FIRES=1 set (R5 will emit per-strategy raw fire counts)"

# Phase 4: pull prefetch data from S3 (instance IAM role grants read access)
echo "[$(date)] Syncing data_prefetch/ from s3://$BATCH395_BUCKET/data_prefetch/..."
mkdir -p data_prefetch
aws s3 sync "s3://$BATCH395_BUCKET/data_prefetch/" data_prefetch/ \
    --no-progress --only-show-errors

# Universe csvs (small but required)
mkdir -p "Backtesting universe"
aws s3 sync "s3://$BATCH395_BUCKET/Backtesting universe/" "Backtesting universe/" \
    --no-progress --only-show-errors

# Optional cache (info_cache, etc.) -- speeds up first day but not required
if aws s3 ls "s3://$BATCH395_BUCKET/data/cache/" &>/dev/null; then
    mkdir -p data/cache
    aws s3 sync "s3://$BATCH395_BUCKET/data/cache/" data/cache/ \
        --no-progress --only-show-errors || true
fi
echo "[$(date)] Data sync complete. Disk usage:"
df -h /

# Phase 5: determine ticker subset for this batch
# Batch 534+ smoke override: when BATCH395_TICKERS is set in user-data
# env, use it directly instead of splits.json. Lets us run a tiny
# smoke (30 tickers x 6 months) for empirical pace measurement.
if [ -n "${BATCH395_TICKERS:-}" ]; then
    TICKERS="$BATCH395_TICKERS"
    echo "[$(date)] SMOKE MODE: using env-supplied ticker list"
else
    echo "[$(date)] Resolving tickers for batch_${BATCH395_INDEX}..."
    aws s3 cp "s3://$BATCH395_BUCKET/aws_batch395_splits.json" /tmp/splits.json \
        --no-progress --only-show-errors
    # B2604 (S6-B2587b, #245/L759): the index reaches python as ARGV, never by
    # bash substitution inside a double-quoted -c argument. Single quotes mean
    # bash substitutes nothing in the program text.
    TICKERS=$(python -c '
import json, sys
splits = json.load(open("/tmp/splits.json"))
key = "batch_" + sys.argv[1]
print(",".join(splits[key]))
' "$BATCH395_INDEX")
fi
TICKER_COUNT=$(echo "$TICKERS" | tr ',' '\n' | wc -l)
echo "[$(date)] Batch $BATCH395_INDEX -> $TICKER_COUNT tickers"

# Phase 6: launch the engine in tmux. Tmux lets the monitor SSH-attach
# from owner laptop while engine runs unattended.
OUTPUT_DIR="output_batch395_${BATCH395_INDEX}"
mkdir -p "$OUTPUT_DIR"
echo "[$(date)] Launching engine in tmux session phase1a_single..."
# Batch 405: optionally override wall-time guards (default 6h kill).
WALL_TIME_ARGS=""
if [ -n "$BATCH395_MAX_HOURS" ]; then
    WALL_TIME_ARGS="--max-run-hours $BATCH395_MAX_HOURS"
fi
if [ -n "$BATCH395_WARN_HOURS" ]; then
    WALL_TIME_ARGS="$WALL_TIME_ARGS --warn-run-hours $BATCH395_WARN_HOURS"
fi
echo "[$(date)] wall-time override: ${WALL_TIME_ARGS:-(default 4h warn / 6h kill)}"

tmux new-session -d -s phase1a_single bash -lc "
    cd /opt/stock-picks-app
    source .venv/bin/activate
    python -m backtest.run_phase1a \\
        --phase $BATCH395_PHASE \\
        --no-agents --no-git --no-walk-forward \\
        --tickers '$TICKERS' \\
        --start $BATCH395_START --end $BATCH395_END \\
        --screen-pool-workers $BATCH395_WORKERS \\
        --output-dir $OUTPUT_DIR \\
        $WALL_TIME_ARGS \\
        2>&1 | tee /var/log/batch395-engine.log
    echo \"[ENGINE-DONE \$?] \$(date)\" >> /var/log/batch395-engine.log
"

# Phase 7: poll tmux session; report progress to S3 every 5 min for monitor
echo "[$(date)] Engine launched. Polling completion..."
START_EPOCH=$(date +%s)
while tmux has-session -t phase1a_single 2>/dev/null; do
    ELAPSED=$(( $(date +%s) - START_EPOCH ))
    # Heartbeat to S3 every 5 min so monitor can detect a hung instance
    {
        echo "ts=$(date -u +%FT%TZ)"
        echo "batch_index=$BATCH395_INDEX"
        echo "elapsed_seconds=$ELAPSED"
        echo "tmux=alive"
        tail -2 /var/log/batch395-engine.log 2>/dev/null || true
    } | aws s3 cp - "s3://$BATCH395_BUCKET/heartbeat/batch_$BATCH395_INDEX.txt" \
        --no-progress --only-show-errors 2>&1 || true
    sleep 300
done
ELAPSED=$(( $(date +%s) - START_EPOCH ))
echo "[$(date)] Engine session ended after ${ELAPSED}s"

# Phase 8: upload outputs to S3
echo "[$(date)] Uploading $OUTPUT_DIR/ to s3://$BATCH395_BUCKET/outputs/batch_$BATCH395_INDEX/..."
aws s3 sync "$OUTPUT_DIR/" "s3://$BATCH395_BUCKET/outputs/batch_$BATCH395_INDEX/" \
    --no-progress --only-show-errors

# Upload engine log too (for post-run forensics)
aws s3 cp /var/log/batch395-engine.log \
    "s3://$BATCH395_BUCKET/outputs/batch_$BATCH395_INDEX/batch395-engine.log" \
    --no-progress --only-show-errors || true
aws s3 cp /var/log/batch395-bootstrap.log \
    "s3://$BATCH395_BUCKET/outputs/batch_$BATCH395_INDEX/batch395-bootstrap.log" \
    --no-progress --only-show-errors || true

# Sentinel file -- merge script polls for these to know all 5 are done
echo "$(date -u +%FT%TZ) elapsed=${ELAPSED}s" | \
    aws s3 cp - "s3://$BATCH395_BUCKET/outputs/batch_$BATCH395_INDEX/_COMPLETE" \
    --no-progress --only-show-errors

# Phase 9: self-terminate. AWS Free Tier eligible accounts get $7 budget alert
# from Phase A; this instance has used its share, terminate to stop charges.
echo "[$(date)] Self-terminating..."
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)
if [ -n "$TOKEN" ]; then
    INSTANCE_ID=$(curl -sH "X-aws-ec2-metadata-token: $TOKEN" \
        http://169.254.169.254/latest/meta-data/instance-id)
    aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" \
        --region us-east-1 --no-cli-pager || true
fi
echo "[$(date)] Bootstrap DONE"
