"""
scripts/smoke_test_polygon.py — Verify Polygon Stocks Starter endpoints work before mass prefetch.

Tests 5 representative endpoints on 5 representative tickers (~5 minutes wall time).

Endpoints tested:
  1. /v2/aggs/ticker/{T}/range/1/day/...  (daily OHLCV — DEC-441 backbone)
  2. /v3/reference/tickers/{T}             (ticker reference — DEC-257 fundamentals partial)
  3. /v3/reference/splits                  (corporate actions — DEC-441 PIT correctness)
  4. /v3/reference/dividends               (corporate actions — DEC-441 PIT correctness)
  5. /v2/reference/news?ticker={T}         (news — DEC-440 supersedes Finnhub)

Run from laptop:
  python scripts/smoke_test_polygon.py

Exits 0 on full success; non-zero with diagnostic detail on any failure.
This script MUST pass before running prefetch scripts.
"""

import os
import sys
import time
import requests
from datetime import date, timedelta
from pathlib import Path

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # ok if dotenv not installed; assume env vars set

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set in environment or .env file")
    print("Add to .env:  POLYGON_API_KEY=your_key_here")
    sys.exit(1)

BASE_URL = "https://api.polygon.io"
TIMEOUT = 30  # seconds per call

# Test sample: diverse cap/sector representation
TEST_TICKERS = ["AAPL", "MSFT", "GOOGL", "JPM", "XOM"]

# Test date window (recent enough to have data, old enough to avoid weekend issues)
END_DATE = date.today() - timedelta(days=7)
START_DATE = END_DATE - timedelta(days=30)


def test_endpoint(name: str, url: str, expected_keys: list = None) -> tuple[bool, str]:
    """Call endpoint, verify 200 response and expected response shape."""
    try:
        params = {"apiKey": POLYGON_KEY}
        r = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        return False, f"Request failed: {e}"

    if r.status_code != 200:
        return False, f"HTTP {r.status_code}: {r.text[:200]}"

    try:
        data = r.json()
    except ValueError as e:
        return False, f"Invalid JSON: {e}"

    if expected_keys:
        missing = [k for k in expected_keys if k not in data]
        if missing:
            return False, f"Missing expected keys: {missing}; got keys: {list(data.keys())}"

    return True, f"OK (response size: {len(r.content)} bytes)"


def run_smoke_test():
    """Run all 5 endpoint tests; return overall pass/fail."""
    results = []
    print(f"=== Polygon Stocks Starter Smoke Test ===")
    print(f"API key: {POLYGON_KEY[:8]}... (masked)")
    print(f"Test window: {START_DATE} to {END_DATE}")
    print(f"Test tickers: {TEST_TICKERS}")
    print()

    # Test 1: Daily OHLCV aggregates
    print("[1/5] Testing daily OHLCV aggregates (/v2/aggs)...")
    for ticker in TEST_TICKERS:
        url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{START_DATE}/{END_DATE}"
        passed, msg = test_endpoint(f"aggs:{ticker}", url, expected_keys=["status", "results"])
        # Stocks Starter is 15-min delayed but historical aggs should always work
        results.append((f"aggs/{ticker}", passed, msg))
        print(f"  {ticker}: {'OK' if passed else '[FAIL]'} {msg}")
        time.sleep(0.1)

    # Test 2: Ticker reference details
    print("\n[2/5] Testing ticker reference (/v3/reference/tickers)...")
    for ticker in TEST_TICKERS:
        url = f"{BASE_URL}/v3/reference/tickers/{ticker}"
        passed, msg = test_endpoint(f"ref:{ticker}", url, expected_keys=["status", "results"])
        results.append((f"reference/{ticker}", passed, msg))
        print(f"  {ticker}: {'OK' if passed else '[FAIL]'} {msg}")
        time.sleep(0.1)

    # Test 3: Splits
    print("\n[3/5] Testing splits (/v3/reference/splits)...")
    url = f"{BASE_URL}/v3/reference/splits?ticker=AAPL&limit=10"
    passed, msg = test_endpoint("splits", url, expected_keys=["status", "results"])
    results.append(("splits", passed, msg))
    print(f"  splits: {'OK' if passed else '[FAIL]'} {msg}")
    time.sleep(0.1)

    # Test 4: Dividends
    print("\n[4/5] Testing dividends (/v3/reference/dividends)...")
    url = f"{BASE_URL}/v3/reference/dividends?ticker=AAPL&limit=10"
    passed, msg = test_endpoint("dividends", url, expected_keys=["status", "results"])
    results.append(("dividends", passed, msg))
    print(f"  dividends: {'OK' if passed else '[FAIL]'} {msg}")
    time.sleep(0.1)

    # Test 5: News
    print("\n[5/5] Testing news (/v2/reference/news)...")
    for ticker in TEST_TICKERS[:2]:  # only test 2 tickers for news (often limited)
        url = f"{BASE_URL}/v2/reference/news?ticker={ticker}&limit=10"
        passed, msg = test_endpoint(f"news:{ticker}", url, expected_keys=["status", "results"])
        results.append((f"news/{ticker}", passed, msg))
        print(f"  {ticker}: {'OK' if passed else '[FAIL]'} {msg}")
        time.sleep(0.1)

    # Summary
    print("\n=== SUMMARY ===")
    total = len(results)
    passed_count = sum(1 for _, p, _ in results if p)
    failed = [r for r in results if not r[1]]

    print(f"Tests passed: {passed_count}/{total}")

    if failed:
        print(f"\nFAILURES ({len(failed)}):")
        for name, _, msg in failed:
            print(f"  - {name}: {msg}")
        print("\n*** SMOKE TEST FAILED ***")
        print("Do NOT proceed with prefetch until failures resolved.")
        sys.exit(1)

    print("\n[OK] ALL ENDPOINTS WORKING")
    print("Polygon Stocks Starter subscription verified for Sprint 1 prefetch scope.")
    print("\nNext steps:")
    print("  1. Run: python scripts/prefetch_polygon_ohlcv_daily.py")
    print("  2. Run: python scripts/prefetch_polygon_reference.py")
    print("  3. Run: python scripts/prefetch_polygon_corp_actions.py")
    print("  4. Run: python scripts/prefetch_polygon_news.py")
    print("  Or:    bash scripts/run_polygon_prefetch_all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(run_smoke_test())
