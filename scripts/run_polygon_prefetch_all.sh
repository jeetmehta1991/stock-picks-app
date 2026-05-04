#!/bin/bash
# scripts/run_polygon_prefetch_all.sh — Run all 4 Polygon prefetch scripts in order.
#
# Pre-requisite: smoke_test_polygon.py must pass first.
#
# Run from laptop:
#   bash scripts/run_polygon_prefetch_all.sh
#
# Estimated wall time: ~4-7 hours total
#   - smoke test: ~5 min
#   - OHLCV daily: ~30-60 min
#   - reference: ~5-10 min
#   - corp actions: ~5-10 min
#   - news: ~3-5 hours (largest)
#
# Safe to interrupt and resume — each script has checkpointing.

set -e  # exit on any error

cd "$(dirname "$0")/.."  # go to repo root

echo "=========================================="
echo "Polygon Prefetch — Sprint 1 Phase 0.A"
echo "=========================================="
echo ""

echo "[Step 1/5] Smoke test"
python scripts/smoke_test_polygon.py
echo ""

echo "[Step 2/5] Daily OHLCV (~30-60 min)"
python scripts/prefetch_polygon_ohlcv_daily.py
echo ""

echo "[Step 3/5] Reference details (~5-10 min)"
python scripts/prefetch_polygon_reference.py
echo ""

echo "[Step 4/5] Corporate actions (~5-10 min)"
python scripts/prefetch_polygon_corp_actions.py
echo ""

echo "[Step 5/5] News (~3-5 hours; largest)"
python scripts/prefetch_polygon_news.py
echo ""

echo "=========================================="
echo "All Polygon prefetch complete."
echo ""
echo "Next steps:"
echo "  1. Review backtest/data/cache/polygon/ contents"
echo "  2. Verify size:  du -sh backtest/data/cache/polygon/"
echo "  3. Commit to main:"
echo "       git add backtest/data/cache/polygon/"
echo "       git commit -m 'Sprint 1: Polygon prefetch (~484 tickers, 5y daily OHLCV + ref + corp actions + news)'"
echo "       git push origin main"
echo "=========================================="
