#!/usr/bin/env bash
# B1571 / S6-B1571a -- configs 1+2 CONCURRENTLY at full 100-ticker scale.
# Purpose is TWO measurements at once: real per-config cost at search scale,
# and the N=2 concurrency point. Both are currently unmeasured - every
# 1-strategy datum so far is 5 tickers.
set -u
cd "$(dirname "$0")/.."
LOG=output_audit/b1576_par.log
: > "$LOG"

run_cfg() {
  local n="$1" sw="$2" span="$3" t0 t1 rc rows cube
  t0=$(date +%s)
  STRATEGY_SUBSET_FILE=output_audit/_subset_one.txt \
  SMC_SWING_LENGTH="$sw" STRAT_EMA_SPAN="$span" \
  PYTHONPATH=. python backtest/run_phase1a.py \
    --tickers-file output_audit/_sweep_100.txt \
    --phase 1a-beta --cube-isolation \
    --no-agents --no-news --no-git --no-walk-forward \
    --screen-pool-workers 0 \
    --start 2024-05-05 --end 2026-05-05 \
    --max-run-hours 6.0 \
    --output-dir "output_cfg${n}" > "output_audit/b1576_cfg${n}.log" 2>&1
  rc=$?
  t1=$(date +%s)
  cube="output_cfg${n}/trade_exit_detail.csv"
  rows="ABSENT"; [ -f "$cube" ] && rows=$(wc -l < "$cube")
  echo "CFG=$n sw=$sw span=$span EXIT=$rc ELAPSED=$((t1-t0)) CUBE_ROWS=$rows" >> "$LOG"
}

# pool=0 each, so 2 processes ~ 2 cores of 10; RAM is the real ceiling.
run_cfg 1 20 200 &      # production baseline
run_cfg 2 10 50  &      # a distinct FIRE-ADDING corner
wait
echo "DONE" >> "$LOG"
