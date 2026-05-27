#!/bin/bash
# Batch 377: Phase 1A-beta health monitor (memory feedback
# `feedback_monitor_intermediate_counts.md` enforcement).
#
# Polls cumulative trade count from the engine's run.log every 5 minutes
# and EMITS an early-abort alert if trade count vs backtest-day ratio
# deviates >2x from baseline. Designed to be wrapped by Monitor tool so
# alerts arrive in chat.
#
# Usage (locally, watching Hetzner via ssh):
#   bash scripts/monitor_phase_1a_beta_health.sh \
#       --baseline-trades-per-day 7.13 \
#       --hetzner-session phase1a_single
#
# Baseline derivation: prior 1A-beta run produced 7,191 trades / 1008
# backtest days = 7.13 trades/day. For the NEXT 1A-beta run, expected
# rate should be at least 7-10/day with cap removal (Batch 377).
#
# Alert format (one line per check):
#   [healthy]  day=N trades=M rate=R baseline=B ratio=X
#   [WARN]     ratio < 0.5x baseline; investigate
#   [ABORT]    ratio < 0.3x baseline for 3 consecutive checks; recommend kill

BASELINE_TPD=7.13
SESSION="phase1a_single"
HOST="root@46.224.181.68"
WARN_RATIO=0.5
ABORT_RATIO=0.3
CONSECUTIVE_ABORT=3
INTERVAL_SEC=300  # 5 minutes

while [[ $# -gt 0 ]]; do
    case "$1" in
        --baseline-trades-per-day) BASELINE_TPD="$2"; shift 2;;
        --hetzner-session) SESSION="$2"; shift 2;;
        --host) HOST="$2"; shift 2;;
        --interval) INTERVAL_SEC="$2"; shift 2;;
        *) echo "[FATAL] unknown arg: $1" >&2; exit 1;;
    esac
done

echo "[INIT] Monitoring Hetzner tmux=$SESSION host=$HOST baseline_trades_per_day=$BASELINE_TPD"
echo "[INIT] WARN threshold=${WARN_RATIO}x baseline / ABORT threshold=${ABORT_RATIO}x for $CONSECUTIVE_ABORT consecutive checks"

abort_streak=0
while true; do
    # Extract current backtest day + cumulative trade count from latest log lines
    snapshot=$(ssh -o ConnectTimeout=15 "$HOST" "tmux capture-pane -p -t $SESSION -S -100 2>/dev/null | tail -50" 2>/dev/null || echo "")
    if [[ -z "$snapshot" ]]; then
        echo "[WARN] cannot read tmux session - may have ended"
        sleep "$INTERVAL_SEC"
        continue
    fi

    # Parse last screen_universe line for backtest date + day-of-run index
    last_date=$(echo "$snapshot" | grep -oE '\[20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]\]' | tail -1 | tr -d '[]')
    # Parse cumulative trade count - engine logs "trades=N" or similar
    cumulative=$(echo "$snapshot" | grep -oE 'open=[0-9]+ closed=[0-9]+' | tail -1)

    if [[ -z "$last_date" ]]; then
        echo "[WARN] no backtest-date marker found in last 50 log lines"
        sleep "$INTERVAL_SEC"
        continue
    fi

    # Approximate backtest day index (start = 2022-05-05)
    days_since_start=$(date -d "$last_date" +%s 2>/dev/null)
    start_epoch=$(date -d "2022-05-05" +%s 2>/dev/null)
    if [[ -n "$days_since_start" && -n "$start_epoch" ]]; then
        days_elapsed=$(( (days_since_start - start_epoch) / 86400 ))
        # Trading days approx = calendar days * 5/7
        trading_days=$(( days_elapsed * 5 / 7 ))
    else
        trading_days="?"
    fi

    # Trade count from open+closed tally if present
    open_n=$(echo "$cumulative" | grep -oE 'open=[0-9]+' | grep -oE '[0-9]+' || echo "0")
    closed_n=$(echo "$cumulative" | grep -oE 'closed=[0-9]+' | grep -oE '[0-9]+' || echo "0")
    cumulative_n=$(( open_n + closed_n ))

    if [[ "$trading_days" -gt 0 && "$cumulative_n" -gt 0 ]]; then
        rate=$(echo "scale=2; $cumulative_n / $trading_days" | bc)
        ratio=$(echo "scale=2; $rate / $BASELINE_TPD" | bc)
        status="healthy"
        if (( $(echo "$ratio < $ABORT_RATIO" | bc -l) )); then
            status="ABORT"
            abort_streak=$(( abort_streak + 1 ))
        elif (( $(echo "$ratio < $WARN_RATIO" | bc -l) )); then
            status="WARN"
            abort_streak=0
        else
            abort_streak=0
        fi
        echo "[$status] day=$last_date approx_trading_day=$trading_days cumulative_trades=$cumulative_n rate=${rate}tpd baseline=${BASELINE_TPD}tpd ratio=${ratio}x abort_streak=$abort_streak"
        if [[ "$abort_streak" -ge "$CONSECUTIVE_ABORT" ]]; then
            echo "[KILL-RECOMMENDED] ratio < ${ABORT_RATIO}x baseline for $CONSECUTIVE_ABORT consecutive checks. Recommend: ssh $HOST tmux kill-session -t $SESSION"
            # Don't auto-kill - leave decision to owner. But emit the loud signal.
        fi
    else
        echo "[init] day=$last_date - waiting for first trade fires"
    fi

    sleep "$INTERVAL_SEC"
done
