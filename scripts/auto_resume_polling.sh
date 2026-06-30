#!/bin/bash
# B1089 Council 215 Fix 2: auto-resume polling with spot-interruption recovery.
#
# Owner directive 2026-06-30:
#   "In case of spot terminations, resume the run from the same progress
#    status. Automatically"
#   "No more errors"
#
# Council 215 Adversarial caveats:
#   - Verify RESUME_FROM_RUN_ID S3 prefix exists before relaunch (no
#     infinite-loop on empty resume)
#   - max_resume_count=3 per chunk (bounded runaway spend)
#
# Council 215 Process: this script ARMS in same turn as launch per
# CHECKLIST #138. Detects Server.SpotInstanceTermination and triggers
# automatic relaunch with RESUME_FROM_RUN_ID=<old_RUN_ID> +
# PHASE_4_CHUNK=<same> + INSTANCE_TYPE=r6a.4xlarge.
#
# Per CHECKLIST #135: relies on existing preflight (≤24hr).
# Per CHECKLIST #138: this IS the mandatory polling task per launch.
#
# Usage:
#   bash scripts/auto_resume_polling.sh /tmp/b1089_chunks.csv
# Input file format: CHUNK,INSTANCE_ID,AZ,RUN_ID (one chunk per line)

set -uo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
BUCKET="stock-picks-batch395-jm-7421"
CHUNKS_FILE="${1:-/tmp/b1089_chunks.csv}"
MAX_RESUME=3
POLL_INTERVAL=300   # 5 min
MAX_CAP=$((20 * 3600 / POLL_INTERVAL))   # 20 hr cap

# Resume count tracker (per chunk)
declare -A RESUME_COUNT
declare -A CHUNK_DONE

echo "=== B1089 AUTO-RESUME POLLING (Council 215 Fix 2) ==="
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Chunks file: $CHUNKS_FILE"
echo "Max resume per chunk: $MAX_RESUME"
echo "Poll interval: ${POLL_INTERVAL}s"

if [ ! -f "$CHUNKS_FILE" ]; then
    echo "B1089_FAIL: chunks file not found: $CHUNKS_FILE"
    exit 2
fi

for POLL in $(seq 1 $MAX_CAP); do
    RUNNING=0
    TERMINATED=0
    COMPLETE=0
    NEEDS_RELAUNCH=()

    while IFS=, read -r CHUNK INST AZ RUN; do
        [ -z "$CHUNK" ] && continue
        # Skip already-completed chunks
        if [ "${CHUNK_DONE[$CHUNK]:-0}" = "1" ]; then
            COMPLETE=$((COMPLETE + 1))
            continue
        fi

        STATE=$(aws ec2 describe-instances --instance-ids "$INST" --query 'Reservations[0].Instances[0].State.Name' --output text 2>&1)
        REASON=$(aws ec2 describe-instances --instance-ids "$INST" --query 'Reservations[0].Instances[0].StateReason.Code' --output text 2>&1)

        if [ "$STATE" = "running" ]; then
            RUNNING=$((RUNNING + 1))
            # Check for PASS sentinel = chunk complete
            if aws s3 ls "s3://${BUCKET}/${RUN}/PHASE_4_PASS" >/dev/null 2>&1; then
                CHUNK_DONE[$CHUNK]=1
                COMPLETE=$((COMPLETE + 1))
                echo "$(date -u +%H:%M:%SZ) CHUNK $CHUNK PASS detected (terminating instance)"
                aws ec2 terminate-instances --instance-ids "$INST" >/dev/null 2>&1
            fi
            # Check for FAIL or HALT = critical alert (no auto-resume)
            if aws s3 ls "s3://${BUCKET}/${RUN}/PHASE_4_FAIL" >/dev/null 2>&1 || \
               aws s3 ls "s3://${BUCKET}/${RUN}/PHASE_4_B1019_HALT" >/dev/null 2>&1; then
                echo "$(date -u +%H:%M:%SZ) ALERT CHUNK $CHUNK FAIL/HALT detected - manual intervention"
            fi
        elif [ "$STATE" = "terminated" ] || [ "$STATE" = "stopped" ]; then
            TERMINATED=$((TERMINATED + 1))
            # Auto-resume only on Server.SpotInstanceTermination
            if [ "$REASON" = "Server.SpotInstanceTermination" ]; then
                CUR_RESUME=${RESUME_COUNT[$CHUNK]:-0}
                if [ "$CUR_RESUME" -lt "$MAX_RESUME" ]; then
                    # Council 215 Adversarial: verify S3 prefix exists before relaunch
                    if aws s3 ls "s3://${BUCKET}/${RUN}/" >/dev/null 2>&1; then
                        echo "$(date -u +%H:%M:%SZ) CHUNK $CHUNK SPOT_INTERRUPT auto-resume attempt $((CUR_RESUME + 1))/$MAX_RESUME (from $RUN)"
                        NEEDS_RELAUNCH+=("$CHUNK,$INST,$AZ,$RUN")
                    else
                        echo "$(date -u +%H:%M:%SZ) CHUNK $CHUNK SPOT_INTERRUPT but S3 prefix $RUN missing - skip"
                    fi
                else
                    echo "$(date -u +%H:%M:%SZ) CHUNK $CHUNK SPOT_INTERRUPT max_resume_count=$MAX_RESUME reached - giving up"
                fi
            elif [ "$REASON" = "Client.UserInitiatedShutdown" ]; then
                # User terminated; don't auto-resume
                CHUNK_DONE[$CHUNK]=2
                echo "$(date -u +%H:%M:%SZ) CHUNK $CHUNK user-terminated; not auto-resuming"
            fi
        fi
    done < "$CHUNKS_FILE"

    # Process needed relaunches
    for ENTRY in "${NEEDS_RELAUNCH[@]:-}"; do
        [ -z "$ENTRY" ] && continue
        IFS=, read -r CHUNK OLD_INST OLD_AZ OLD_RUN <<< "$ENTRY"
        RESUME_COUNT[$CHUNK]=$((${RESUME_COUNT[$CHUNK]:-0} + 1))

        # Generate user-data with resume parameters
        PHASE_4_ONLY=1 PHASE_4_CHUNK="$CHUNK" RESUME_FROM_RUN_ID="$OLD_RUN" MODE=full \
            bash "${REPO_ROOT}/scripts/launch_r5_master_4y_v2.sh" \
            > "/tmp/b1089_chunk_${CHUNK}_resume.log" 2>&1
        NEW_RUN=$(grep "Run ID:" "/tmp/b1089_chunk_${CHUNK}_resume.log" | awk '{print $3}')
        BOOTSTRAP=$(grep "User-data ready at:" "/tmp/b1089_chunk_${CHUNK}_resume.log" | awk '{print $NF}')
        if [ -z "$NEW_RUN" ] || [ ! -f "$BOOTSTRAP" ]; then
            echo "  Auto-resume CHUNK $CHUNK user-data gen FAILED"
            continue
        fi
        USER_DATA_B64=$(base64 -w0 "$BOOTSTRAP")

        # Try AZs in rotation (prefer original then fallback)
        for AZ in "$OLD_AZ" us-east-1c us-east-1d us-east-1f us-east-1b us-east-1a; do
            RES=$(INSTANCE_TYPE=r6a.4xlarge bash "${REPO_ROOT}/scripts/b1070_phase_d_launch_helper.sh" \
                "$NEW_RUN" "$AZ" "$USER_DATA_B64" "phase4_chunk_${CHUNK}_b1089_autoresume" 2>&1 | tail -1)
            if [[ "$RES" =~ ^i- ]]; then
                echo "  Auto-resume CHUNK $CHUNK NEW_INSTANCE=$RES az=$AZ run_id=$NEW_RUN"
                # B1090 PIVOT #49 fix (Council 217): replace inline Python
                # CSV update with sed (bash-native; no subshell path drift).
                # Council 217 Contrarian: use | delimiter not / to avoid
                # special-char escaping issues in instance IDs.
                # Pattern: match line starting with CHUNK, replace entire line.
                sed -i "s|^${CHUNK},.*|${CHUNK},${RES},${AZ},${NEW_RUN}|" "$CHUNKS_FILE"
                break
            fi
        done
    done

    # Periodic summary
    if [ $((POLL % 3)) -eq 0 ]; then
        echo "$(date -u +%H:%M:%SZ) POLL $POLL: running=$RUNNING terminated=$TERMINATED complete=$COMPLETE"
    fi

    # Exit conditions
    TOTAL_CHUNKS=$(wc -l < "$CHUNKS_FILE")
    if [ "$COMPLETE" -eq "$TOTAL_CHUNKS" ]; then
        echo "$(date -u +%H:%M:%SZ) ALL $TOTAL_CHUNKS CHUNKS COMPLETE - exit"
        break
    fi

    sleep $POLL_INTERVAL
done

echo "Polling done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
