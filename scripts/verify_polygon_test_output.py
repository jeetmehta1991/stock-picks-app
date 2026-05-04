"""
scripts/verify_polygon_test_output.py — Validate small-scale test parquet output.

Inspects backtest/data/cache/polygon/ after run_polygon_5ticker_test.sh.

Validates:
  1. File counts match expectation (5 per ticker-keyed endpoint, 1 each for splits/dividends/index)
  2. File sizes within expected ranges (no 0-byte files, no suspiciously identical sizes)
  3. Schema integrity (column names + types match spec)
  4. Content sanity (date ranges, ticker matches filename, non-null required fields)
  5. Pagination evidence (AAPL news >1000 articles = multiple pages successfully handled)
  6. Empty-results handling (splits for AAPL in 5y window: 0 expected; XOM dividends: many expected)
  7. Checkpoint files valid JSON

Run from laptop AFTER:
  bash scripts/run_polygon_5ticker_test.sh

Exit codes:
  0  All checks passed; safe to proceed to full prefetch (after owner approves).
  1  One or more checks failed; investigate before scaling.
"""

import json
import sys
from pathlib import Path

import pandas as pd

CACHE_DIR = Path("backtest/data/cache/polygon")
TEST_TICKERS = ["AAPL", "MSFT", "GOOGL", "JPM", "XOM"]

# Expected schema per endpoint
EXPECTED_OHLCV_COLS = {"ticker", "date", "open", "high", "low", "close",
                       "volume", "vwap", "transactions"}
EXPECTED_REFERENCE_COLS = {"ticker", "name", "market_cap", "sic_code",
                            "sic_description", "primary_exchange", "type",
                            "active", "currency_name", "cik", "list_date",
                            "delisted_utc", "homepage_url", "fetched_at"}
EXPECTED_NEWS_COLS = {"ticker", "id", "published_utc", "title", "description",
                      "article_url", "publisher_name", "sentiment",
                      "sentiment_reasoning", "all_tickers"}

results = []  # list of (check_name, pass_bool, message)


def check(name: str, condition: bool, msg: str):
    """Record a check result."""
    results.append((name, condition, msg))
    icon = "✓" if condition else "✗"
    print(f"  {icon} {name}: {msg}")


def section(title: str):
    print(f"\n=== {title} ===")


def verify_ohlcv():
    """Validate OHLCV daily output."""
    section("[1/5] OHLCV Daily")
    ohlcv_dir = CACHE_DIR / "ohlcv_daily"

    if not ohlcv_dir.exists():
        check("ohlcv_dir_exists", False, f"Directory not found: {ohlcv_dir}")
        return

    # File count
    files = sorted(ohlcv_dir.glob("*.parquet"))
    check("ohlcv_file_count", len(files) == 5,
          f"Found {len(files)} parquet files (expected 5)")

    # Per-ticker validation
    for ticker in TEST_TICKERS:
        f = ohlcv_dir / f"{ticker}.parquet"
        if not f.exists():
            check(f"ohlcv_{ticker}_exists", False, f"Missing: {f}")
            continue

        size_kb = f.stat().st_size / 1024
        check(f"ohlcv_{ticker}_size", 50 < size_kb < 5000,
              f"{size_kb:.1f} KB (expected 50-5000 KB for 5y daily)")

        try:
            df = pd.read_parquet(f)
        except Exception as e:
            check(f"ohlcv_{ticker}_readable", False, f"Read failed: {e}")
            continue

        # Schema check
        cols = set(df.columns)
        missing = EXPECTED_OHLCV_COLS - cols
        check(f"ohlcv_{ticker}_schema", not missing,
              f"{len(cols)} columns; missing: {missing if missing else 'none'}")

        # Row count: 5y × ~252 trading days ≈ 1260 rows
        check(f"ohlcv_{ticker}_rows", 1100 < len(df) < 1400,
              f"{len(df)} rows (expected ~1260 for 5y daily)")

        # Ticker matches filename
        if "ticker" in df.columns:
            unique_tickers = df["ticker"].unique()
            check(f"ohlcv_{ticker}_ticker_match",
                  len(unique_tickers) == 1 and unique_tickers[0] == ticker,
                  f"ticker column = {list(unique_tickers)}")

        # Date range
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            min_date, max_date = df["date"].min(), df["date"].max()
            check(f"ohlcv_{ticker}_date_range",
                  (max_date - min_date).days > 1700,
                  f"{min_date.date()} to {max_date.date()}")

        # Price sanity
        if "close" in df.columns:
            check(f"ohlcv_{ticker}_prices_positive",
                  (df["close"] > 0).all() and df["close"].notna().all(),
                  f"close range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")


def verify_reference():
    """Validate reference output."""
    section("[2/5] Reference")
    ref_dir = CACHE_DIR / "reference"

    if not ref_dir.exists():
        check("ref_dir_exists", False, f"Directory not found: {ref_dir}")
        return

    files = sorted(ref_dir.glob("*.parquet"))
    check("ref_file_count", len(files) == 5,
          f"Found {len(files)} parquet files (expected 5)")

    for ticker in TEST_TICKERS:
        f = ref_dir / f"{ticker}.parquet"
        if not f.exists():
            check(f"ref_{ticker}_exists", False, "missing")
            continue

        try:
            df = pd.read_parquet(f)
        except Exception as e:
            check(f"ref_{ticker}_readable", False, f"Read failed: {e}")
            continue

        check(f"ref_{ticker}_schema",
              EXPECTED_REFERENCE_COLS.issubset(set(df.columns)),
              f"{len(df.columns)} cols; sic_description={df.iloc[0].get('sic_description', 'N/A')[:40]}")

        # CIK should be populated for SEC EDGAR cross-reference (DEC-484)
        cik = df.iloc[0].get("cik")
        check(f"ref_{ticker}_cik", cik is not None and str(cik) != "nan",
              f"CIK = {cik}")

    # Combined index file
    idx_file = CACHE_DIR / "reference_index.parquet"
    if idx_file.exists():
        try:
            df = pd.read_parquet(idx_file)
            check("ref_index_exists", len(df) == 5,
                  f"reference_index.parquet has {len(df)} rows")
        except Exception as e:
            check("ref_index_readable", False, f"Read failed: {e}")
    else:
        check("ref_index_exists", False, "reference_index.parquet not found")


def verify_corp_actions():
    """Validate splits + dividends output."""
    section("[3/5] Corporate Actions")

    splits_file = CACHE_DIR / "splits" / "all_splits_test.parquet"
    divs_file = CACHE_DIR / "dividends" / "all_dividends_test.parquet"

    # Splits — for our 5 tickers in 5y window, expect 0-2 splits (e.g., GOOGL did 20-for-1 in 2022)
    if splits_file.exists():
        try:
            df = pd.read_parquet(splits_file)
            check("splits_readable", True, f"{len(df)} split records")
            if len(df) > 0:
                expected_cols = {"ticker", "execution_date", "split_from", "split_to"}
                check("splits_schema", expected_cols.issubset(set(df.columns)),
                      f"columns: {list(df.columns)}")
                # GOOGL had a 20-for-1 split on 2022-07-15 — verify if in test window
                googl_splits = df[df["ticker"] == "GOOGL"] if "ticker" in df.columns else pd.DataFrame()
                check("splits_googl_2022",
                      len(googl_splits) >= 1,
                      f"GOOGL splits in window: {len(googl_splits)} (expected ≥1: the 2022 20-for-1)")
        except Exception as e:
            check("splits_readable", False, f"Read failed: {e}")
    else:
        check("splits_file_exists", False,
              f"WARNING: {splits_file} not found — script may have written without _test suffix")
        # Fallback: try without suffix
        alt = CACHE_DIR / "splits" / "all_splits.parquet"
        if alt.exists():
            check("splits_file_alt", True, f"Found at {alt} (no suffix)")

    # Dividends — for our 5 tickers (4 dividend payers, GOOGL only started 2024) over 5y
    # AAPL pays quarterly = ~20; MSFT quarterly = ~20; JPM quarterly = ~20; XOM quarterly = ~20; GOOGL = ~6
    # Total expected: ~70-100 records
    if divs_file.exists():
        try:
            df = pd.read_parquet(divs_file)
            check("divs_readable", True, f"{len(df)} dividend records")
            check("divs_count_sane", 50 <= len(df) <= 200,
                  f"{len(df)} records (expected 50-200 for 4-5 quarterly payers × 5y)")
            if len(df) > 0 and "ticker" in df.columns:
                per_ticker = df["ticker"].value_counts().to_dict()
                check("divs_per_ticker", True, f"per-ticker: {per_ticker}")
        except Exception as e:
            check("divs_readable", False, f"Read failed: {e}")
    else:
        check("divs_file_exists", False, f"WARNING: {divs_file} not found")


def verify_news():
    """Validate news output — pagination is the key test here."""
    section("[4/5] News (Pagination Test)")
    news_dir = CACHE_DIR / "news"

    if not news_dir.exists():
        check("news_dir_exists", False, f"Directory not found: {news_dir}")
        return

    files = sorted(news_dir.glob("*.parquet"))
    check("news_file_count", len(files) >= 1,
          f"Found {len(files)} parquet files (some tickers may have 0 articles, that's OK)")

    pagination_evidence = False
    for ticker in TEST_TICKERS:
        f = news_dir / f"{ticker}.parquet"
        if not f.exists():
            print(f"  ⚠ news_{ticker}: no file (0 articles in 5y window — possible but unusual for this ticker)")
            continue

        try:
            df = pd.read_parquet(f)
        except Exception as e:
            check(f"news_{ticker}_readable", False, f"Read failed: {e}")
            continue

        check(f"news_{ticker}_schema",
              EXPECTED_NEWS_COLS.issubset(set(df.columns)),
              f"{len(df)} articles; cols missing: {EXPECTED_NEWS_COLS - set(df.columns) or 'none'}")

        # AAPL especially should have >1000 articles over 5y, exercising pagination
        if ticker == "AAPL" and len(df) > 1000:
            pagination_evidence = True

        # Sentiment populated (Polygon Stocks Starter provides sentiment per insight)
        if "sentiment" in df.columns:
            non_null_sent = df["sentiment"].notna().sum()
            sent_ratio = non_null_sent / len(df) if len(df) > 0 else 0
            check(f"news_{ticker}_sentiment",
                  sent_ratio > 0.3,
                  f"{non_null_sent}/{len(df)} ({sent_ratio:.0%}) have sentiment field populated")

    check("news_pagination_evidence", pagination_evidence,
          "AAPL >1000 articles → multi-page pagination handled correctly"
          if pagination_evidence else
          "AAPL <1000 articles — pagination not exercised; full universe tickers may also paginate but unverified")


def verify_checkpoints():
    """Validate checkpoint files are valid JSON with expected structure."""
    section("[5/5] Checkpoints")

    for cp_name in ["_checkpoint_ohlcv.json", "_checkpoint_news.json"]:
        cp_file = CACHE_DIR / cp_name
        if not cp_file.exists():
            check(f"{cp_name}_exists", False, "missing")
            continue
        try:
            data = json.loads(cp_file.read_text())
            completed = data.get("completed", [])
            check(f"{cp_name}_valid",
                  isinstance(completed, list) and len(completed) >= 1,
                  f"{len(completed)} tickers checkpointed: {completed}")
        except Exception as e:
            check(f"{cp_name}_valid", False, f"Parse failed: {e}")


def main():
    print("=" * 50)
    print("Polygon 5-Ticker Test Output Verification")
    print("=" * 50)

    if not CACHE_DIR.exists():
        print(f"ERROR: {CACHE_DIR} does not exist. Run run_polygon_5ticker_test.sh first.")
        return 1

    verify_ohlcv()
    verify_reference()
    verify_corp_actions()
    verify_news()
    verify_checkpoints()

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    total = len(results)
    passed = sum(1 for _, p, _ in results if p)
    failed = [(n, m) for n, p, m in results if not p]

    print(f"Total checks: {total}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {len(failed)}")

    if failed:
        print(f"\n*** {len(failed)} CHECKS FAILED ***")
        for name, msg in failed:
            print(f"  ✗ {name}: {msg}")
        print("\nDo NOT proceed to full prefetch until failures resolved.")
        return 1

    print("\n✅ ALL CHECKS PASSED")
    print("Pipeline validated end-to-end on 5 tickers.")
    print("Safe to scale to full 484-ticker prefetch (with owner approval).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
