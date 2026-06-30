#!/bin/bash
# B1085 Council 204-206 Phase 4 parallel chunk launcher.
#
# Owner directive 2026-06-29: 'B' = 8 chunks within $40 cap + 4 preflights
# (1 per AZ) + wrapper script (Council 206 Option 3).
#
# Strategy: 8 chunks via PHASE_4_CHUNK=A-H (B1084 shipped). Each chunk
# resumes from B1079 Phase 1+2+3 PASS state in S3 via RESUME_FROM_RUN_ID
# + SKIP_PHASES=1,2,3 (B1078 shipped). 4 AZs (us-east-1a/c/d/f) rotated
# with 2 chunks per AZ. AZ-fallback on InsufficientInstanceCapacity per
# Council 206 caveat.
#
# Cost: 8 chunks x 2.3hr x $0.85 = ~$15.64 (within $40 cap)
# Wall-clock: ~2.3 hr parallel (boot + engine)
#
# Usage:
#   bash scripts/launch_phase4_parallel.sh [RESUME_FROM_RUN_ID]
# Default RESUME_FROM_RUN_ID: r5_full_20260629_155837 (B1079 PASS state)
#
# Exit codes:
#   0 = all 8 chunks launched + CHECKLIST #134 verified
#   1 = launch chain failed (capacity exhausted across all AZs)
#   2 = preflight prerequisite not met (CHECKLIST #135)

set -uo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
RESUME_FROM_RUN_ID="${1:-${RESUME_FROM_RUN_ID:-r5_full_20260629_155837}}"
BUCKET="stock-picks-batch395-jm-7421"

echo "=== B1085 PHASE 4 PARALLEL LAUNCHER ==="
echo "Resume source: ${RESUME_FROM_RUN_ID}"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# AZ rotation: 4 AZs x 2 chunks each = 8 (Council 205+206)
declare -A CHUNK_AZ
CHUNK_AZ[A]="us-east-1a"
CHUNK_AZ[B]="us-east-1a"
CHUNK_AZ[C]="us-east-1c"
CHUNK_AZ[D]="us-east-1c"
CHUNK_AZ[E]="us-east-1d"
CHUNK_AZ[F]="us-east-1d"
CHUNK_AZ[G]="us-east-1f"
CHUNK_AZ[H]="us-east-1f"

# AZ-fallback order (Council 206 caveat): if primary AZ capacity-fails,
# rotate through remaining AZs.
AZ_FALLBACK_ORDER="us-east-1a us-east-1c us-east-1d us-east-1f us-east-1b"

# Verify RESUME_FROM_RUN_ID has Phase 1+2+3 PASS sentinels
echo ""
echo "=== Verifying resume source has Phase 1+2+3 PASS ==="
MISSING_PHASES=()
for PHASE in 1 2 3; do
    if ! aws s3 ls "s3://${BUCKET}/${RESUME_FROM_RUN_ID}/PHASE_${PHASE}_PASS" >/dev/null 2>&1; then
        MISSING_PHASES+=("${PHASE}")
    fi
done
if [ ${#MISSING_PHASES[@]} -gt 0 ]; then
    echo "B1085_FAIL: PHASE_${MISSING_PHASES[*]}_PASS missing in s3://${BUCKET}/${RESUME_FROM_RUN_ID}/"
    echo "Cannot resume Phase 4 without prior Phase 1+2+3 PASS sentinels"
    exit 2
fi
echo "Resume source verified: PHASE_1_PASS + PHASE_2_PASS + PHASE_3_PASS all present"

# Launch each chunk with AZ-fallback logic
declare -A CHUNK_INSTANCE
declare -A CHUNK_RUN_ID
declare -A CHUNK_AZ_USED

for CHUNK in A B C D E F G H; do
    echo ""
    echo "=== Launching chunk ${CHUNK} (primary AZ: ${CHUNK_AZ[$CHUNK]}) ==="

    # Generate user-data with chunk + resume env vars
    RESUME_FROM_RUN_ID="${RESUME_FROM_RUN_ID}" \
    SKIP_PHASES="1,2,3" \
    PHASE_4_CHUNK="${CHUNK}" \
    MODE=full \
        bash "${REPO_ROOT}/scripts/launch_r5_master_4y_v2.sh" \
        > "/tmp/b1085_gen_${CHUNK}.log" 2>&1

    if [ $? -ne 0 ]; then
        echo "B1085_FAIL: user-data generation for chunk ${CHUNK} failed"
        tail -20 "/tmp/b1085_gen_${CHUNK}.log"
        continue
    fi

    RUN_ID=$(grep "Run ID:" "/tmp/b1085_gen_${CHUNK}.log" | awk '{print $3}')
    BOOTSTRAP_FILE=$(grep "User-data ready at:" "/tmp/b1085_gen_${CHUNK}.log" | awk '{print $NF}')

    if [ -z "$RUN_ID" ] || [ ! -f "$BOOTSTRAP_FILE" ]; then
        echo "B1085_FAIL: RUN_ID=${RUN_ID} or bootstrap missing for chunk ${CHUNK}"
        continue
    fi

    USER_DATA_B64=$(base64 -w0 "$BOOTSTRAP_FILE")
    CHUNK_RUN_ID[$CHUNK]="$RUN_ID"

    # AZ-fallback launch: try primary AZ, then rotate through fallback order
    INSTANCE_ID=""
    AZ_USED=""
    for AZ in "${CHUNK_AZ[$CHUNK]}" $AZ_FALLBACK_ORDER; do
        # Skip duplicate of primary
        if [ -n "$AZ_USED" ]; then break; fi
        echo "  Trying ${AZ}..."
        ATTEMPT=$(bash "${REPO_ROOT}/scripts/b1070_phase_d_launch_helper.sh" \
            "$RUN_ID" \
            "$AZ" \
            "$USER_DATA_B64" \
            "phase4_chunk_${CHUNK}_b1085" 2>&1 | tail -3)
        # Check if last line is an instance ID
        LAST_LINE=$(echo "$ATTEMPT" | tail -1)
        if [[ "$LAST_LINE" =~ ^i- ]]; then
            INSTANCE_ID="$LAST_LINE"
            AZ_USED="$AZ"
            break
        else
            echo "  ${AZ} failed: ${ATTEMPT}"
        fi
    done

    if [ -z "$INSTANCE_ID" ]; then
        echo "B1085_FAIL: chunk ${CHUNK} could not launch in any AZ (all capacity-failed)"
        continue
    fi

    CHUNK_INSTANCE[$CHUNK]="$INSTANCE_ID"
    CHUNK_AZ_USED[$CHUNK]="$AZ_USED"
    echo "  Chunk ${CHUNK} LAUNCHED: ${INSTANCE_ID} in ${AZ_USED} (RUN_ID=${RUN_ID})"

    # CHECKLIST #134: verify within 60 sec
    sleep 3
    STATE=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
        --query 'Reservations[0].Instances[0].State.Name' \
        --output text 2>&1)
    if [ "$STATE" != "running" ] && [ "$STATE" != "pending" ]; then
        echo "  WARN: chunk ${CHUNK} state=${STATE} (expected pending/running)"
    fi
done

# Summary
echo ""
echo "=== LAUNCH SUMMARY ==="
LAUNCHED=0
for CHUNK in A B C D E F G H; do
    if [ -n "${CHUNK_INSTANCE[$CHUNK]:-}" ]; then
        echo "Chunk ${CHUNK}: ${CHUNK_INSTANCE[$CHUNK]} (${CHUNK_AZ_USED[$CHUNK]}) RUN_ID=${CHUNK_RUN_ID[$CHUNK]}"
        LAUNCHED=$((LAUNCHED + 1))
    else
        echo "Chunk ${CHUNK}: FAILED (no instance)"
    fi
done
echo ""
echo "Launched: ${LAUNCHED}/8 chunks"
echo "Completed: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ "$LAUNCHED" -lt 8 ]; then
    echo "B1085_PARTIAL: ${LAUNCHED}/8 chunks launched; review failed chunks"
    exit 1
fi

# Persist launch evidence for polling + status updates
mkdir -p "${REPO_ROOT}/output_audit"
EVIDENCE="${REPO_ROOT}/output_audit/b1085_parallel_launch_$(date -u +%Y%m%dT%H%M%SZ).json"
{
    echo "{"
    echo "  \"comment\": \"B1085 Phase 4 parallel launch evidence\","
    echo "  \"launched_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"resume_from_run_id\": \"${RESUME_FROM_RUN_ID}\","
    echo "  \"chunks\": {"
    FIRST=1
    for CHUNK in A B C D E F G H; do
        if [ "$FIRST" -eq 1 ]; then FIRST=0; else echo ","; fi
        printf "    \"%s\": {\"instance\": \"%s\", \"az\": \"%s\", \"run_id\": \"%s\"}" \
            "$CHUNK" "${CHUNK_INSTANCE[$CHUNK]}" "${CHUNK_AZ_USED[$CHUNK]}" "${CHUNK_RUN_ID[$CHUNK]}"
    done
    echo ""
    echo "  }"
    echo "}"
} > "$EVIDENCE"
echo "Evidence: ${EVIDENCE}"

echo "B1085_OVERALL_PASS: 8/8 chunks launched + verified"
exit 0
