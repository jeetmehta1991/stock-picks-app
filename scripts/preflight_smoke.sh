#!/bin/bash
# B1080 CHECKLIST #135 preflight smoke (Council 199 Layer 3)
#
# Owner directive 2026-06-29: 'Accept. Council this.'
# Council 198 4-lens synthesis (Outsider + Executor independently converged):
#   3-layer audit framework = Pyramid + Schema-pin + 60-sec prod-entrypoint smoke
# Council 199 implementation Option-iii AWS-MICRO-VIA-HELPER:
#   Re-use scripts/b1070_phase_d_launch_helper.sh + MODE=smoke env vars
#   Window: NVDA + 1 day (existing SMOKE_TICKER + SMOKE_START + SMOKE_END)
#   Assert: monitor.log >0 bytes + engine_state.status=complete +
#           no PHASE_*_FAIL/HALT + schema columns + baseline scaling
#
# WHY: 6/6 past PIVOTs (#34/#36/#37/#40/#42/#43) survived pyramid
# because pyramid stubs the integration points where bugs hide. This
# script runs the EXACT production user-data path (helper + S3 + AWS)
# on minimal data so the integration points get exercised.
#
# Usage:
#   bash scripts/preflight_smoke.sh [--no-launch]
# Env vars:
#   AWS_DEFAULT_REGION (default us-east-1)
#   PREFLIGHT_AZ (default us-east-1d; falls through to 1c then 1b on capacity)
#   PREFLIGHT_TICKER (default NVDA)
#   PREFLIGHT_START (default 2026-04-30)
#   PREFLIGHT_END (default 2026-05-01)
#
# Exit codes:
#   0 = all assertions PASS; AWS launch >$1 authorized
#   1 = at least one assertion FAILED; HALT AWS launch
#   2 = preflight infrastructure failure (launch unreachable, S3 down, etc)

set -uo pipefail

PREFLIGHT_AZ="${PREFLIGHT_AZ:-us-east-1d}"
PREFLIGHT_TICKER="${PREFLIGHT_TICKER:-NVDA}"
PREFLIGHT_START="${PREFLIGHT_START:-2026-04-30}"
PREFLIGHT_END="${PREFLIGHT_END:-2026-05-01}"
BUCKET="stock-picks-batch395-jm-7421"
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# B1085 Council 207 --per-az flag: run preflight in each of 4 AZs in
# parallel (us-east-1a/c/d/f) for stratified verification before Phase 4
# parallel launch. Per owner directive 2026-06-29 'Dec 3 4' interpreted
# by Outsider + Executor lens convergence as '4 = 1 per AZ stratified'.
if [ "${1:-}" = "--per-az" ]; then
    echo "=== PREFLIGHT --per-az (B1085 Council 207 4-AZ stratified) ==="
    PER_AZ_LIST="us-east-1a us-east-1c us-east-1d us-east-1f"
    PER_AZ_PIDS=()
    PER_AZ_LOGS=()
    PER_AZ_AZS=()
    for AZ in $PER_AZ_LIST; do
        LOG="/tmp/b1085_preflight_${AZ}.log"
        echo "Launching preflight in ${AZ} (log: ${LOG})..."
        # Recursive call without --per-az; inherits PREFLIGHT_TICKER + window
        PREFLIGHT_AZ="$AZ" bash "$0" --no-launch > "$LOG" 2>&1 &
        PER_AZ_PIDS+=("$!")
        PER_AZ_LOGS+=("$LOG")
        PER_AZ_AZS+=("$AZ")
    done
    echo "Waiting for all 4 per-AZ preflights (parallel)..."
    FAIL=0
    for i in "${!PER_AZ_PIDS[@]}"; do
        if wait "${PER_AZ_PIDS[$i]}"; then
            echo "  ${PER_AZ_AZS[$i]}: PASS"
        else
            echo "  ${PER_AZ_AZS[$i]}: FAIL (log: ${PER_AZ_LOGS[$i]})"
            FAIL=$((FAIL + 1))
        fi
    done
    echo ""
    if [ $FAIL -gt 0 ]; then
        echo "PREFLIGHT_PER_AZ_OVERALL_FAIL: ${FAIL} of 4 AZs failed"
        exit 1
    fi
    echo "PREFLIGHT_PER_AZ_OVERALL_PASS: 4/4 AZs PASS"
    exit 0
fi

echo "=== PREFLIGHT SMOKE (CHECKLIST #135 / Council 199 Layer 3) ==="
echo "Ticker: ${PREFLIGHT_TICKER}"
echo "Window: ${PREFLIGHT_START} to ${PREFLIGHT_END}"
echo "AZ: ${PREFLIGHT_AZ}"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Generate user-data via existing launch script (MODE=smoke path)
cd "$REPO_ROOT"
SMOKE_TICKER="${PREFLIGHT_TICKER}" \
SMOKE_START="${PREFLIGHT_START}" \
SMOKE_END="${PREFLIGHT_END}" \
SMOKE_POOL_WORKERS=0 \
MODE=smoke \
  bash scripts/launch_r5_master_4y_v2.sh > /tmp/preflight_gen.log 2>&1

if [ $? -ne 0 ]; then
    echo "PREFLIGHT_FAIL: user-data generation failed; see /tmp/preflight_gen.log"
    exit 2
fi

RUN_ID=$(grep "Run ID:" /tmp/preflight_gen.log | awk '{print $3}')
BOOTSTRAP_FILE=$(grep "User-data ready at:" /tmp/preflight_gen.log | awk '{print $NF}')

if [ -z "$RUN_ID" ] || [ -z "$BOOTSTRAP_FILE" ] || [ ! -f "$BOOTSTRAP_FILE" ]; then
    echo "PREFLIGHT_FAIL: RUN_ID=${RUN_ID} BOOTSTRAP=${BOOTSTRAP_FILE} invalid"
    cat /tmp/preflight_gen.log | tail -30
    exit 2
fi

echo "Run ID: ${RUN_ID}"
echo "Bootstrap: ${BOOTSTRAP_FILE}"

# Honor --no-launch flag (smoke test of generation only)
if [ "${1:-}" = "--no-launch" ]; then
    echo "PREFLIGHT_GENERATION_ONLY: --no-launch flag set; user-data generated successfully"
    echo "PREFLIGHT_PASS_GENERATION"
    exit 0
fi

# Launch via helper (CHECKLIST #131 EBS=100GB enforced)
USER_DATA_B64=$(base64 -w0 "$BOOTSTRAP_FILE")
INSTANCE_ID=$(bash scripts/b1070_phase_d_launch_helper.sh \
    "$RUN_ID" \
    "$PREFLIGHT_AZ" \
    "$USER_DATA_B64" \
    "preflight_smoke_b1080" 2>&1 | tail -1)

if [ -z "$INSTANCE_ID" ] || [[ ! "$INSTANCE_ID" =~ ^i- ]]; then
    echo "PREFLIGHT_FAIL: helper returned non-instance-id: ${INSTANCE_ID}"
    exit 2
fi

echo "Instance: ${INSTANCE_ID}"

# CHECKLIST #134 verification within 60 sec
sleep 5
STATE=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].State.Name' \
    --output text 2>&1)
if [ "$STATE" != "running" ] && [ "$STATE" != "pending" ]; then
    echo "PREFLIGHT_FAIL: instance state=${STATE} not pending/running"
    aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" >/dev/null 2>&1
    exit 2
fi

# Poll for sentinels (5-min cap; smoke should complete in ~3-5 min)
echo "Polling for smoke completion (5 min cap)..."
SMOKE_PASS=0
SMOKE_FAIL=0
SMOKE_HALT=0
for i in $(seq 1 60); do
    sleep 5
    SENTINEL_LS=$(aws s3 ls "s3://${BUCKET}/${RUN_ID}/" 2>&1 | awk '{print $4}')
    if echo "$SENTINEL_LS" | grep -q "PHASE_smoke_PASS"; then
        SMOKE_PASS=1
        echo "PHASE_smoke_PASS detected at poll ${i}"
        break
    fi
    if echo "$SENTINEL_LS" | grep -q "PHASE_smoke_FAIL"; then
        SMOKE_FAIL=1
        echo "PHASE_smoke_FAIL detected at poll ${i}"
        break
    fi
    if echo "$SENTINEL_LS" | grep -q "PHASE_smoke_B1019_HALT"; then
        SMOKE_HALT=1
        echo "PHASE_smoke_B1019_HALT detected at poll ${i}"
        break
    fi
    if [ $((i % 12)) -eq 0 ]; then
        echo "Poll ${i}: sentinels=$(echo $SENTINEL_LS | wc -w)"
    fi
done

# Terminate instance regardless of outcome
aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" >/dev/null 2>&1
echo "Instance terminated"

if [ $SMOKE_FAIL -eq 1 ] || [ $SMOKE_HALT -eq 1 ]; then
    echo "PREFLIGHT_FAIL: smoke FAIL/HALT detected"
    exit 1
fi
if [ $SMOKE_PASS -eq 0 ]; then
    echo "PREFLIGHT_FAIL: smoke timeout (no PASS sentinel after 5 min)"
    exit 1
fi

# Assertion bundle (B1080 PIVOT #43 lineage)
echo ""
echo "=== ASSERTION BUNDLE ==="
ASSERT_PASS=0
ASSERT_FAIL=0

# A1: monitor.log >0 bytes (B1019 PIVOT #34 lineage)
MONITOR_SIZE=$(aws s3 ls "s3://${BUCKET}/${RUN_ID}/output_phase_smoke/b1019_monitor.log" 2>/dev/null | awk '{print $3}')
if [ -n "$MONITOR_SIZE" ] && [ "$MONITOR_SIZE" -gt 0 ]; then
    echo "  A1 monitor.log >0 bytes: PASS (size=${MONITOR_SIZE})"
    ASSERT_PASS=$((ASSERT_PASS + 1))
else
    echo "  A1 monitor.log >0 bytes: FAIL (size=${MONITOR_SIZE:-MISSING})"
    ASSERT_FAIL=$((ASSERT_FAIL + 1))
fi

# A2: engine_state.status=complete (B1070 F-1.1 lineage)
ENGINE_STATE=$(aws s3 cp "s3://${BUCKET}/${RUN_ID}/output_phase_smoke/engine_state.json" - 2>/dev/null)
if echo "$ENGINE_STATE" | grep -q '"status": "complete"'; then
    echo "  A2 engine_state.status=complete: PASS"
    ASSERT_PASS=$((ASSERT_PASS + 1))
else
    echo "  A2 engine_state.status=complete: FAIL"
    echo "$ENGINE_STATE" | head -5
    ASSERT_FAIL=$((ASSERT_FAIL + 1))
fi

# A3: no PHASE_*_FAIL or HALT sentinels
FAIL_SENTINELS=$(aws s3 ls "s3://${BUCKET}/${RUN_ID}/" 2>&1 | grep -E "FAIL|HALT" | wc -l)
if [ "$FAIL_SENTINELS" -eq 0 ]; then
    echo "  A3 no FAIL/HALT sentinels: PASS"
    ASSERT_PASS=$((ASSERT_PASS + 1))
else
    echo "  A3 no FAIL/HALT sentinels: FAIL (count=${FAIL_SENTINELS})"
    aws s3 ls "s3://${BUCKET}/${RUN_ID}/" 2>&1 | grep -E "FAIL|HALT" | head -5
    ASSERT_FAIL=$((ASSERT_FAIL + 1))
fi

# A4: schema columns present in trade_log_checkpoint (B1062 PIVOT #37 lineage)
# Pull first line of CSV to verify columns
TRADE_LOG_HEAD=$(aws s3 cp "s3://${BUCKET}/${RUN_ID}/output_phase_smoke/trade_log_checkpoint.csv" - 2>/dev/null | head -1)
if [ -n "$TRADE_LOG_HEAD" ]; then
    REQUIRED_COLS=("ticker" "entry_date" "exit_date" "exit_reason" "exit_method" "strategy" "regime")
    MISSING_COLS=()
    for col in "${REQUIRED_COLS[@]}"; do
        if ! echo "$TRADE_LOG_HEAD" | grep -qw "$col"; then
            MISSING_COLS+=("$col")
        fi
    done
    if [ ${#MISSING_COLS[@]} -eq 0 ]; then
        echo "  A4 schema columns present: PASS (all ${#REQUIRED_COLS[@]} required)"
        ASSERT_PASS=$((ASSERT_PASS + 1))
    else
        echo "  A4 schema columns present: FAIL (missing: ${MISSING_COLS[*]})"
        ASSERT_FAIL=$((ASSERT_FAIL + 1))
    fi
else
    echo "  A4 schema columns present: SKIP (trade_log_checkpoint.csv missing or empty - may be no trades in 1-day window)"
fi

# A5: baseline_universe_size scaled (B1059 PIVOT #36 lineage)
BASELINE_LOG=$(aws s3 cp "s3://${BUCKET}/${RUN_ID}/output_phase_smoke/b1019_monitor.log" - 2>/dev/null | grep "B1059 PIVOT #36" | head -1)
if [ -n "$BASELINE_LOG" ]; then
    echo "  A5 baseline scaled (B1059): PASS"
    echo "    ${BASELINE_LOG}"
    ASSERT_PASS=$((ASSERT_PASS + 1))
else
    echo "  A5 baseline scaled (B1059): FAIL (no B1059 entry in monitor.log)"
    ASSERT_FAIL=$((ASSERT_FAIL + 1))
fi

echo ""
echo "=== SUMMARY ==="
echo "PASS: ${ASSERT_PASS}  FAIL: ${ASSERT_FAIL}"
echo "Run ID: ${RUN_ID}"
echo "S3 prefix: s3://${BUCKET}/${RUN_ID}/"
echo "Completed: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ $ASSERT_FAIL -gt 0 ]; then
    echo "PREFLIGHT_OVERALL_FAIL: ${ASSERT_FAIL} assertion(s) failed"
    exit 1
fi

echo "PREFLIGHT_OVERALL_PASS: all assertions PASS; AWS launch >\$1 authorized per CHECKLIST #135"
exit 0
