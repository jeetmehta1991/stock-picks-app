#!/usr/bin/env bash
# B1568 / S6-B1565d -- observed wall-clock A/B for demand pruning.
#
# Everything shipped in B1565-B1567 is justified by a DERIVED number: a
# twice-concordant 95.8pct per-call saving on compute_all_signals, which is
# 14.3pct of profile runtime -> ~13.7pct. No end-to-end run has ever been timed
# with pruning armed. This script produces the observed number, or shows the
# derivation was wrong -- which is worth knowing before building the 27.2pct
# SMC version on the same assumption.
#
# Identical config twice, SEQUENTIALLY on an idle box, differing only in
# DEMAND_PRUNING. Sequential and solo because B1558's 3,696s was measured under
# 3-way contention and absolute per-call times have varied 3.3x across
# processes this session (L401) -- a contended or parallel A/B would measure
# scheduling noise, not pruning.
set -u
cd "$(dirname "$0")/.."
LOG=output_audit/b1568_ab.log
: > "$LOG"

run_one() {
  local tag="$1" prune="$2" outdir="$3"
  local t0 t1
  t0=$(date +%s)
  DEMAND_PRUNING="$prune" \
  STRATEGY_SUBSET_FILE=output_audit/_subset_one.txt \
  SMC_SWING_LENGTH=20 STRAT_EMA_SPAN=200 \
  PYTHONPATH=. python backtest/run_phase1a.py \
    --tickers-file output_audit/_ab5.txt \
    --phase 1a-beta --cube-isolation \
    --no-agents --no-news --no-git --no-walk-forward \
    --screen-pool-workers 0 \
    --start 2024-05-05 --end 2026-05-05 \
    --max-run-hours 2.0 \
    --output-dir "$outdir" > "output_audit/b1568_${tag}.log" 2>&1
  local rc=$?
  t1=$(date +%s)
  # Completion is an ARTIFACT, never an exit code (L410): a run once finished
  # every sim-day and wrote no cube.
  local cube="$outdir/trade_exit_detail.csv"
  local rows="ABSENT"
  [ -f "$cube" ] && rows=$(wc -l < "$cube")
  echo "TAG=$tag PRUNE=$prune EXIT=$rc ELAPSED=$((t1-t0)) CUBE_ROWS=$rows" >> "$LOG"
}

# OFF first so any first-run warmup cost (imports, JIT) lands on the BASELINE
# and cannot flatter the pruned arm.
run_one off 0 output_ab_off
run_one on  1 output_ab_on

echo "DONE" >> "$LOG"
