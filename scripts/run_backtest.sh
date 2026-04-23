#!/bin/bash
# Run backtest for any phase with nohup — survives Codespace timeout
#
# Usage:
#   Phase 1A (67 instruments, no agents, free):
#     nohup bash scripts/run_backtest.sh 1a > backtest_1a.log 2>&1 &
#     tail -f backtest_1a.log
#
#   Phase 1B (509 instruments, Haiku agents, ~$116 CAD):
#     nohup bash scripts/run_backtest.sh 1b > backtest_1b.log 2>&1 &
#     tail -f backtest_1b.log
#
#   Phase 1C (top strategies, Sonnet agents):
#     nohup bash scripts/run_backtest.sh 1c > backtest_1c.log 2>&1 &
#     tail -f backtest_1c.log

set -e

PHASE=${1:-1a}
OUTPUT_DIR="output_v2_${PHASE}"
LOG_FILE="backtest_${PHASE}.log"

echo "=== Backtest Phase ${PHASE^^} ==="
echo "Output: ${OUTPUT_DIR}/"
echo "Started: $(date -u '+%Y-%m-%d %H:%M UTC')"

# Sync latest code
git fetch origin
git reset --hard origin/main

# Install dependencies
pip install -r requirements.txt --break-system-packages -q

# Set agents flag — Phase 1A runs without agents (free)
if [ "$PHASE" = "1a" ]; then
    AGENT_FLAG="--no-agents"
    echo "Agents: DISABLED (free run)"
else
    AGENT_FLAG=""
    echo "Agents: ENABLED — ensure ANTHROPIC_API_KEY is set"
fi

# Run backtest
python -m backtest.run_phase1a \
    --phase "$PHASE" \
    $AGENT_FLAG \
    --output-dir "$OUTPUT_DIR"

# Commit results
echo "Committing results..."
git add "${OUTPUT_DIR}/" backtest/agents/cache/ 2>/dev/null || true
git commit -m "Phase ${PHASE^^} results — $(date -u '+%Y-%m-%d %H:%M UTC')"
git push origin main

echo "=== Complete — results committed to main ==="
