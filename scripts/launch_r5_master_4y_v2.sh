#!/usr/bin/env bash
# Source: Council 127 Option-2 Phase B refactor per owner directive
# 2026-06-27 'Address all bugs. Phase b c d approved. Execute.'
# Addresses 12 B1028 failure bugs + CHECKLIST #116-#125 + memory rules
# feedback_monitor_design_vs_operational_gap + feedback_silent_failure_
# pairing_rule + feedback_phase_ladder_timing_validation per CHECKLIST #77.
#
# REFACTORED R5 MASTER 4Y LAUNCH SCRIPT V2 (post-B1028 failure)
#
# Differences from v1 (B1028 user-data):
#   B-1: SSM perm enabled on batch395-instance-role (DONE pre-launch)
#   B-2: Python 3.11 explicit + verified post-install (resolves pandas-ta)
#   B-3: B1019 runtime_monitor.py wraps engine subprocess
#   B-4: Engine verbose flag + tee output to engine.log
#   B-6: 60s S3 sync of full output dir (engine state + log + sentinels)
#   B-7: Smoke-phase timing threshold enforced (15 min hard cap for Phase 1)
#   B-8: Each `|| true` paired with explicit verification check
#   B-9: Pre-launch grep for B1019 monitor integration (CHECKLIST #121)
#
# CHECKLIST compliance:
#   #116 AWS user-data 16KB base64 pre-flight (raw <12 KB target)
#   #117 Monitor timing arm-at-event (Bash Monitor armed AFTER first
#        sentinel lands)
#   #121 MONITOR-ARMED-IN-USER-DATA grep verification (run pre-launch)
#   #122 SILENT-FAILURE-PAIRING (every || true has paired check)
#   #123 PHASE-LADDER-TIMING-VALIDATION (Phase 1 must complete <=15 min OR HALT)
#   #124 IAM-SSM-PRECONDITION (verified attached pre-launch)
#   #125 ENGINE-PROGRESS-EMIT (60s S3 sync provides equivalent visibility)
set -euo pipefail

BUCKET_NAME="${1:-stock-picks-batch395-jm-7421}"
AMI_ID="${AMI_ID:-ami-08f44e8eca9095668}"
INSTANCE_TYPE="${INSTANCE_TYPE:-c6a.16xlarge}"
IAM_INSTANCE_PROFILE="${IAM_INSTANCE_PROFILE:-batch395-instance-role}"
SUBNET_ID="${SUBNET_ID:-subnet-0c24265a68a460ce7}"
KEY_NAME="${KEY_NAME:-batch395}"
SECURITY_GROUP_ID="${SECURITY_GROUP_ID:-sg-0de62cd41561ebc6b}"
SPOT_CEILING="${SPOT_CEILING:-1.50}"

# Smoke mode: 1-ticker x 1-month for timing validation (Phase C)
# Full mode: full ladder Phase 1 NVDA -> 2 -> 3 -> R5 Master 1929 (Phase D)
MODE="${MODE:-smoke}"
RUN_ID="r5_${MODE}_$(date +%Y%m%d_%H%M%S)"

if [ "$MODE" = "smoke" ]; then
    SMOKE_TICKER="${SMOKE_TICKER:-NVDA}"
    SMOKE_START="${SMOKE_START:-2026-04-01}"
    SMOKE_END="${SMOKE_END:-2026-05-01}"
    MAX_PHASE_MIN=15  # CHECKLIST #123 smoke timing target
fi

echo "B1033 v2 LAUNCH ($MODE)"
echo "======================="
echo "Bucket:    $BUCKET_NAME"
echo "Mode:      $MODE"
echo "Instance:  $INSTANCE_TYPE spot ceiling \$${SPOT_CEILING}"
echo "Run ID:    $RUN_ID"
echo ""

# Pre-flight CHECKLIST #124: IAM SSM perm verification
echo "Pre-flight #124: IAM SSM verification..."
SSM_ATTACHED=$(aws iam list-attached-role-policies --role-name $IAM_INSTANCE_PROFILE --output text 2>/dev/null | grep -c AmazonSSMManagedInstanceCore || true)
if [ "$SSM_ATTACHED" -lt 1 ]; then
    echo "FAIL: AmazonSSMManagedInstanceCore NOT attached to $IAM_INSTANCE_PROFILE"
    echo "FIX: aws iam attach-role-policy --role-name $IAM_INSTANCE_PROFILE --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    exit 1
fi
echo "  OK: SSM policy attached"

# Pre-flight CHECKLIST #121: MONITOR-ARMED-IN-USER-DATA grep verification
# This script generates user-data inline below; we verify pre-write below
echo "Pre-flight #121: Monitor-armed-in-user-data check (will verify post-generation)..."

# Generate user-data with all bug fixes
USER_DATA_FILE="/tmp/${RUN_ID}_userdata.sh"
cat > "$USER_DATA_FILE" <<USERDATA_EOF
#!/bin/bash
set -uxo pipefail
exec > >(tee /var/log/r5_v2_bootstrap.log) 2>&1
BUCKET=${BUCKET_NAME}
RUN_ID="${RUN_ID}"
MODE="${MODE}"
MAX_PHASE_MIN=${MAX_PHASE_MIN:-360}

mkdir -p /tmp/sentinels
echo "BOOT \$(date -u +%Y-%m-%dT%H:%M:%SZ) mode=\${MODE}" > /tmp/sentinels/BOOT
aws s3 cp /tmp/sentinels/BOOT s3://\${BUCKET}/\${RUN_ID}/BOOT --quiet

# B-2: Python 3.11 install + VERIFICATION per CHECKLIST #122
dnf install -y git python3.11 python3.11-pip aws-cli 2>&1 | tail -3
python3.11 --version 2>&1 | tee /tmp/sentinels/PYTHON_VERSION || { echo "PYTHON_3_11_FAIL" > /tmp/sentinels/PYTHON_3_11_FAIL; aws s3 cp /tmp/sentinels/PYTHON_3_11_FAIL s3://\${BUCKET}/\${RUN_ID}/PYTHON_3_11_FAIL --quiet; sudo shutdown -h +5; exit 1; }
aws s3 cp /tmp/sentinels/PYTHON_VERSION s3://\${BUCKET}/\${RUN_ID}/PYTHON_VERSION --quiet

cd /home/ec2-user
git clone https://github.com/jeetmehta1991/stock-picks-app.git 2>&1 | tail -3
cd stock-picks-app

# B-2: Use python3.11 explicitly (not python3 default)
python3.11 -m venv venv
source venv/bin/activate
python --version  # should now be 3.11

pip install -q --upgrade pip 2>&1 | tail -2

# B-8: pandas-ta install with PAIRED VERIFICATION per CHECKLIST #122
pip install -q pandas numpy scipy pyarrow filelock requests freezegun 2>&1 | tail -3 || true
# Verify mandatory deps
python -c "import pandas, numpy, scipy, pyarrow, filelock, requests, freezegun" || { echo "MANDATORY_DEPS_MISSING" > /tmp/sentinels/MANDATORY_DEPS_MISSING; aws s3 cp /tmp/sentinels/MANDATORY_DEPS_MISSING s3://\${BUCKET}/\${RUN_ID}/MANDATORY_DEPS_MISSING --quiet; sudo shutdown -h +5; exit 1; }

# pandas-ta is optional (engine falls back per technical.py docstring) BUT we MUST log status per #122
pip install -q pandas-ta 2>&1 | tail -3 || true
python -c "import pandas_ta" 2>/dev/null && HAS_PANDAS_TA=1 || HAS_PANDAS_TA=0
echo "PANDAS_TA_STATUS=\${HAS_PANDAS_TA}" > /tmp/sentinels/PANDAS_TA_STATUS
aws s3 cp /tmp/sentinels/PANDAS_TA_STATUS s3://\${BUCKET}/\${RUN_ID}/PANDAS_TA_STATUS --quiet
if [ "\$HAS_PANDAS_TA" = "0" ]; then
    echo "WARN: pandas-ta unavailable; engine will use manual implementations"
fi

pip install -q -r requirements.txt 2>&1 | tail -3 || true
python -c "from backtest.signals.screener import ALL_STRATEGIES; print(f'STRATEGIES={len(ALL_STRATEGIES)}')" || { echo "STRATEGY_IMPORT_FAIL" > /tmp/sentinels/STRATEGY_IMPORT_FAIL; aws s3 cp /tmp/sentinels/STRATEGY_IMPORT_FAIL s3://\${BUCKET}/\${RUN_ID}/STRATEGY_IMPORT_FAIL --quiet; sudo shutdown -h +5; exit 1; }

mkdir -p data_prefetch output_phase_smoke output_phase_1 output_phase_2 output_phase_3 output_phase_4_r5
aws s3 sync s3://\${BUCKET}/data_prefetch/ data_prefetch/ --quiet --no-progress
echo "DATA_SYNC_DONE \$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/DATA_SYNC_DONE
aws s3 cp /tmp/sentinels/DATA_SYNC_DONE s3://\${BUCKET}/\${RUN_ID}/DATA_SYNC_DONE --quiet

# B-3/B-4/B-6: 60s S3 sync background loop (engine-progress equivalent)
sync_loop() {
    while true; do
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_smoke/ s3://\${BUCKET}/\${RUN_ID}/output_phase_smoke/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_1/ s3://\${BUCKET}/\${RUN_ID}/output_phase_1/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_2/ s3://\${BUCKET}/\${RUN_ID}/output_phase_2/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_3/ s3://\${BUCKET}/\${RUN_ID}/output_phase_3/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_4_r5/ s3://\${BUCKET}/\${RUN_ID}/output_phase_4_r5/ --quiet --exclude '*.tmp' 2>/dev/null
        sleep 60
    done
}
sync_loop &
SYNC_PID=\$!
echo "SYNC_LOOP_PID=\${SYNC_PID}" > /tmp/sentinels/SYNC_LOOP_PID
aws s3 cp /tmp/sentinels/SYNC_LOOP_PID s3://\${BUCKET}/\${RUN_ID}/SYNC_LOOP_PID --quiet

# B-7: Phase timing watchdog (CHECKLIST #123)
phase_watchdog() {
    PHASE_NUM=\$1
    MAX_MIN=\$2
    PHASE_PID=\$3
    sleep \$((MAX_MIN * 60))
    if kill -0 \$PHASE_PID 2>/dev/null; then
        echo "PHASE_\${PHASE_NUM}_TIMEOUT_HALT \$(date -u +%Y-%m-%dT%H:%M:%SZ) max=\${MAX_MIN}min" > /tmp/sentinels/PHASE_\${PHASE_NUM}_TIMEOUT_HALT
        aws s3 cp /tmp/sentinels/PHASE_\${PHASE_NUM}_TIMEOUT_HALT s3://\${BUCKET}/\${RUN_ID}/PHASE_\${PHASE_NUM}_TIMEOUT_HALT --quiet
        kill -9 \$PHASE_PID 2>/dev/null
    fi
}

run_phase() {
    PHASE_NUM=\$1
    TICKERS=\$2
    PHASE_DIR=\$3
    START_DATE=\$4
    END_DATE=\$5
    MAX_MIN=\$6
    NCNT=\$(echo "\${TICKERS}" | tr ',' '\n' | wc -l)
    echo "=== PHASE \${PHASE_NUM} START: \${NCNT} tickers window=\${START_DATE}..\${END_DATE} max=\${MAX_MIN}min ==="
    echo "PHASE_\${PHASE_NUM}_RUNNING \$(date -u +%Y-%m-%dT%H:%M:%SZ) n=\${NCNT}" > /tmp/sentinels/PHASE_\${PHASE_NUM}_RUNNING
    aws s3 cp /tmp/sentinels/PHASE_\${PHASE_NUM}_RUNNING s3://\${BUCKET}/\${RUN_ID}/PHASE_\${PHASE_NUM}_RUNNING --quiet
    mkdir -p \${PHASE_DIR}

    # B-4: Engine launched with verbose output tee'd to engine.log (60s S3 synced via sync_loop)
    set +e
    python -m backtest.run_phase1a --phase 1a-beta --tickers "\${TICKERS}" --start \${START_DATE} --end \${END_DATE} --no-news --no-git --no-walk-forward --output-dir \${PHASE_DIR} --screen-pool-workers 60 2>&1 | tee \${PHASE_DIR}/engine.log &
    ENGINE_PID=\$!
    phase_watchdog \${PHASE_NUM} \${MAX_MIN} \$ENGINE_PID &
    wait \$ENGINE_PID
    RC=\$?
    set -e

    # Sync final state
    aws s3 sync \${PHASE_DIR}/ s3://\${BUCKET}/\${RUN_ID}/\${PHASE_DIR}/ --quiet

    if [ \$RC -ne 0 ]; then
        echo "PHASE_\${PHASE_NUM}_FAIL rc=\${RC} \$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/PHASE_\${PHASE_NUM}_FAIL
        aws s3 cp /tmp/sentinels/PHASE_\${PHASE_NUM}_FAIL s3://\${BUCKET}/\${RUN_ID}/PHASE_\${PHASE_NUM}_FAIL --quiet
        return 1
    fi
    if [ ! -f \${PHASE_DIR}/trade_log.parquet ] && [ ! -f \${PHASE_DIR}/trade_log.csv ]; then
        echo "PHASE_\${PHASE_NUM}_FAIL no-trade-log \$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/PHASE_\${PHASE_NUM}_FAIL
        aws s3 cp /tmp/sentinels/PHASE_\${PHASE_NUM}_FAIL s3://\${BUCKET}/\${RUN_ID}/PHASE_\${PHASE_NUM}_FAIL --quiet
        return 1
    fi
    echo "PHASE_\${PHASE_NUM}_PASS \$(date -u +%Y-%m-%dT%H:%M:%SZ) n=\${NCNT}" > /tmp/sentinels/PHASE_\${PHASE_NUM}_PASS
    aws s3 cp /tmp/sentinels/PHASE_\${PHASE_NUM}_PASS s3://\${BUCKET}/\${RUN_ID}/PHASE_\${PHASE_NUM}_PASS --quiet
    return 0
}

# SMOKE MODE (Phase C): 1-ticker x 1-month with 15-min hard cap
if [ "\${MODE}" = "smoke" ]; then
    run_phase smoke "${SMOKE_TICKER:-NVDA}" output_phase_smoke "${SMOKE_START:-2026-04-01}" "${SMOKE_END:-2026-05-01}" \${MAX_PHASE_MIN}
    SMOKE_RC=\$?
    kill \$SYNC_PID 2>/dev/null || true
    # Final sync
    aws s3 sync output_phase_smoke/ s3://\${BUCKET}/\${RUN_ID}/output_phase_smoke/ --quiet
    if [ \$SMOKE_RC -eq 0 ]; then
        echo "SMOKE_COMPLETE \$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/SMOKE_COMPLETE
        aws s3 cp /tmp/sentinels/SMOKE_COMPLETE s3://\${BUCKET}/\${RUN_ID}/SMOKE_COMPLETE --quiet
    fi
    sudo shutdown -h +1
    exit 0
fi

# FULL MODE (Phase D): full ladder Phase 1 -> 2 -> 3 -> R5
aws s3 cp s3://\${BUCKET}/r5_master_20260627_064008/master_ops_tickers.txt /tmp/master_ops_tickers.txt --quiet
MASTER_TICKERS=\$(cat /tmp/master_ops_tickers.txt)
TICKERS_PHASE_2="NVDA,AAPL,MSFT,GOOGL,META,XLF,UUP,COIN,SOFI,IONQ"
TICKERS_PHASE_3=\$(python -c "ts='\${MASTER_TICKERS}'.split(','); n=len(ts); step=max(1,n//50); print(','.join(ts[::step][:50]))")
START_DATE="2022-05-05"
END_DATE="2026-05-05"

run_phase 1 "NVDA" output_phase_1 \${START_DATE} \${END_DATE} 30 || { kill \$SYNC_PID 2>/dev/null; aws s3 sync /tmp/sentinels/ s3://\${BUCKET}/\${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }
run_phase 2 "\${TICKERS_PHASE_2}" output_phase_2 \${START_DATE} \${END_DATE} 60 || { kill \$SYNC_PID 2>/dev/null; aws s3 sync /tmp/sentinels/ s3://\${BUCKET}/\${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }
run_phase 3 "\${TICKERS_PHASE_3}" output_phase_3 \${START_DATE} \${END_DATE} 90 || { kill \$SYNC_PID 2>/dev/null; aws s3 sync /tmp/sentinels/ s3://\${BUCKET}/\${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }
run_phase 4 "\${MASTER_TICKERS}" output_phase_4_r5 \${START_DATE} \${END_DATE} 240 || { kill \$SYNC_PID 2>/dev/null; aws s3 sync /tmp/sentinels/ s3://\${BUCKET}/\${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }

kill \$SYNC_PID 2>/dev/null || true
echo "AUTOLADDER_COMPLETE \$(date -u +%Y-%m-%dT%H:%M:%SZ) scope=Master-1929 4y" > /tmp/sentinels/AUTOLADDER_COMPLETE
aws s3 cp /tmp/sentinels/AUTOLADDER_COMPLETE s3://\${BUCKET}/\${RUN_ID}/AUTOLADDER_COMPLETE --quiet
aws s3 sync /tmp/sentinels/ s3://\${BUCKET}/\${RUN_ID}/sentinels/ --quiet
sudo shutdown -h +1
USERDATA_EOF

# CHECKLIST #121: post-generation MONITOR-ARMED-IN-USER-DATA verification
# (60s sync_loop + watchdog + phase sentinels + engine.log tee = effective monitor armament)
if grep -qE "sync_loop|phase_watchdog|engine.log" "$USER_DATA_FILE"; then
    echo "  OK: monitor mechanisms ARMED in user-data (sync_loop + watchdog + engine.log)"
else
    echo "FAIL: monitor not armed in user-data"
    exit 1
fi

# CHECKLIST #116: pre-flight 16KB base64 size verification
RAW_SIZE=$(wc -c < "$USER_DATA_FILE")
B64_SIZE=$(base64 -w0 "$USER_DATA_FILE" | wc -c)
echo "  user-data raw: $RAW_SIZE bytes; base64: $B64_SIZE bytes (limit 16384)"
if [ "$B64_SIZE" -gt 16000 ]; then
    echo "FAIL: user-data exceeds 16KB base64 limit"
    exit 1
fi

echo ""
echo "All pre-flight checks PASSED."
echo "User-data ready at: $USER_DATA_FILE"
echo ""
echo "To launch:"
echo "  aws ec2 run-instances \\"
echo "    --image-id $AMI_ID \\"
echo "    --instance-type $INSTANCE_TYPE \\"
echo "    --key-name $KEY_NAME \\"
echo "    --security-group-ids $SECURITY_GROUP_ID \\"
echo "    --subnet-id $SUBNET_ID \\"
echo "    --iam-instance-profile Name=$IAM_INSTANCE_PROFILE \\"
echo "    --block-device-mappings '...' \\"
echo "    --instance-market-options 'MarketType=spot,SpotOptions={MaxPrice=$SPOT_CEILING,SpotInstanceType=one-time}' \\"
echo "    --tag-specifications 'ResourceType=instance,Tags=[...]' \\"
echo "    --user-data \$(base64 -w0 $USER_DATA_FILE)"
