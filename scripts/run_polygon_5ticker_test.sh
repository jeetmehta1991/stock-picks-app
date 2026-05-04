#!/bin/bash
# scripts/run_polygon_5ticker_test.sh — Small-scale 5-ticker test BEFORE full prefetch.
#
# Per CHECKLIST #64 (artifact-state verification): test on real data at small scale
# before committing 4-7 hours of full-universe wall time.
#
# Test tickers: AAPL, MSFT, GOOGL, JPM, XOM (same 5 as smoke test for continuity)
# Wall time target: ~10-15 minutes total
#
# What this validates that smoke test does NOT:
#   1. Pagination handling (AAPL 5y news ≈ 3000 articles → multi-page)
#   2. Parquet write/read round-trip
#   3. Schema integrity end-to-end
#   4. Checkpointing logic creates valid checkpoint files
#   5. Empty-results detection (splits for our 5 tickers in 5y window)
#   6. Non-mega-cap behavior (XOM, JPM)
#   7. Per-ticker output file shape
#
# Output:
#   backtest/data/cache/polygon/{ohlcv_daily,reference,news}/{TICKER}.parquet  (5 each)
#   backtest/data/cache/polygon/splits/all_splits_test.parquet
#   backtest/data/cache/polygon/dividends/all_dividends_test.parquet
#   backtest/data/cache/polygon/reference_index.parquet
#   backtest/data/cache/polygon/_checkpoint_ohlcv.json
#   backtest/data/cache/polygon/_checkpoint_news.json
#
# Run from laptop:
#   bash scripts/run_polygon_5ticker_test.sh
#
# After completion, run:
#   python scripts/verify_polygon_test_output.py
# to inspect the parquet output and validate schema/content.

set -e
cd "$(dirname "$0")/.."  # repo root

TEST_TICKERS="AAPL MSFT GOOGL JPM XOM"

echo "=========================================="
echo "Polygon 5-Ticker Small-Scale Test"
echo "=========================================="
echo "Tickers: $TEST_TICKERS"
echo "Goal:    Validate prefetch+write+checkpoint pipeline on real data"
echo "         BEFORE running full 484-ticker prefetch."
echo ""

START_TIME=$(date +%s)

echo "[Step 1/4] Daily OHLCV (5 tickers, ~5y each)"
python scripts/prefetch_polygon_ohlcv_daily.py --tickers $TEST_TICKERS
echo ""

echo "[Step 2/4] Reference details (5 tickers)"
python scripts/prefetch_polygon_reference.py --tickers $TEST_TICKERS
echo ""

echo "[Step 3/4] Corporate actions (filtered to 5 tickers, _test suffix)"
python scripts/prefetch_polygon_corp_actions.py --tickers $TEST_TICKERS --test-suffix _test
echo ""

echo "[Step 4/4] News (5 tickers, full 5y — exercises pagination)"
python scripts/prefetch_polygon_news.py --tickers $TEST_TICKERS
echo ""

ELAPSED=$(($(date +%s) - START_TIME))
echo "=========================================="
echo "5-Ticker Test Complete"
echo "Wall time: $(($ELAPSED / 60))m $(($ELAPSED % 60))s"
echo ""
echo "Next:"
echo "  python scripts/verify_polygon_test_output.py"
echo "=========================================="
