#!/bin/bash
# 1-ticker pre-test — one ticker per batch, Jan 2022 only (~5 min each)
# Run before full Phase 1B to validate agent output quality
# Usage:
#   export ANTHROPIC_API_KEY=your_key_here
#   bash run_tests.sh

export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

source /c/Users/jeetm/Github/stock-picks-app/.venv/Scripts/activate

# Guard: refuse to run if API key is not set
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set."
  echo "Set it first: export ANTHROPIC_API_KEY=your_key_here"
  echo "Then re-run: bash run_tests.sh"
  exit 1
fi

echo "API key: SET"
echo "Starting 1-ticker pre-test — 5 batches simultaneously..."
echo ""

echo "Starting batch 1 test (AAPL)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers AAPL \
  --start 2022-01-01 --end 2022-01-31 \
  --output-dir output_1b_batch1_test \
  --no-git \
  > batch1_test.log 2>&1 &
echo "Batch 1 PID: $!"

echo "Starting batch 2 test (CVS)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers CVS \
  --start 2022-01-01 --end 2022-01-31 \
  --output-dir output_1b_batch2_test \
  --no-git \
  > batch2_test.log 2>&1 &
echo "Batch 2 PID: $!"

echo "Starting batch 3 test (JPM)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers JPM \
  --start 2022-01-01 --end 2022-01-31 \
  --output-dir output_1b_batch3_test \
  --no-git \
  > batch3_test.log 2>&1 &
echo "Batch 3 PID: $!"

echo "Starting batch 4 test (NVDA)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers NVDA \
  --start 2022-01-01 --end 2022-01-31 \
  --output-dir output_1b_batch4_test \
  --no-git \
  > batch4_test.log 2>&1 &
echo "Batch 4 PID: $!"

echo "Starting batch 5 test (XLE)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers XLE \
  --start 2022-01-01 --end 2022-01-31 \
  --output-dir output_1b_batch5_test \
  --no-git \
  > batch5_test.log 2>&1 &
echo "Batch 5 PID: $!"

echo ""
echo "All 5 tests launched. Monitor with: tail -f batch1_test.log"
echo "When all complete, run: bash run_commit.sh test"
