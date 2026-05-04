#!/bin/bash
# Commit all batch outputs after run completes
# Usage: bash run_commit.sh test   (for pre-test outputs)
#        bash run_commit.sh full   (for full run outputs)

export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

source /c/Users/jeetm/Github/stock-picks-app/.venv/Scripts/activate

MODE=${1:-test}

if [ "$MODE" = "test" ]; then
  DIRS="output_1b_batch1_test output_1b_batch2_test output_1b_batch3_test output_1b_batch4_test output_1b_batch5_test"
  MSG="Phase 1B: 1-ticker pre-test results (AAPL/CVS/JPM/NVDA/XLE)"
elif [ "$MODE" = "full" ]; then
  DIRS="output_1b_batch1 output_1b_batch2 output_1b_batch3 output_1b_batch4 output_1b_batch5"
  MSG="Phase 1B: all 5 batches complete (509 tickers)"
else
  echo "Usage: bash run_commit.sh test|full"
  exit 1
fi

echo "Step 1: git status"
git status

echo ""
echo "Step 2: Adding agent cache..."
git add backtest/agents/cache/ 2>/dev/null || echo "No agent cache to add"

echo "Step 3: Adding output dirs..."
for dir in $DIRS; do
  if [ -d "$dir" ]; then
    git add "$dir/"
    echo "  Added: $dir"
  else
    echo "  Skipped (not found): $dir"
  fi
done

echo ""
echo "Step 4: Committing..."
git commit -m "$MSG"

echo ""
echo "Step 5: Pull then push..."
git pull --rebase origin main
git push origin main

echo ""
echo "Step 6: Verifying push landed..."
git log -1 origin/main
git log -1

echo ""
if [ "$MODE" = "full" ]; then
  echo "Step 7: Merging batch outputs..."
  python scripts/merge_batch_outputs.py \
    --input-dirs output_1b_batch1 output_1b_batch2 output_1b_batch3 output_1b_batch4 output_1b_batch5 \
    --output-dir output_1b_final
  git add output_1b_final/
  git commit -m "Phase 1B: merged final results"
  git pull --rebase origin main
  git push origin main
  echo "Merge complete. Share with Claude for review."
else
  echo "Done. Share the commit with Claude for review."
fi
