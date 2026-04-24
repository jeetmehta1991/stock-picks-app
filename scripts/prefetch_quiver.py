"""
scripts/prefetch_quiver.py — Pre-fetch all Quiver data for Phase 1B backtest.

Downloads and caches to Parquet:
  - Congressional trades (2020-2024)
  - Insider trades (2020-2024)
  - Institutional 13F (2020-2024)
  - Government contracts (2020-2024)
  - Lobbying data (2020-2024)
  - Wikipedia page views (2020-2024)
  - WallStreetBets mentions (2020-2024)

Run from laptop (Codespaces blocks api.quiverquant.com):
  python scripts/prefetch_quiver.py

Progress is saved every 50 tickers — safe to interrupt and resume.
"""

import os
import sys
import time
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import date

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.data.universe import get_sp500_constituents, ETFS_FULL

# --- Config ---
QUIVER_TOKEN = os.environ.get("QUIVER_API_KEY", "")
if not QUIVER_TOKEN:
    print("ERROR: QUIVER_API_KEY not set")
    sys.exit(1)

BASE_URL = "https://api.quiverquant.com/beta"
HEADERS = {"Authorization": f"Token {QUIVER_TOKEN}"}
CACHE_DIR = Path("backtest/data/cache/quiver")
CHECKPOINT_FILE = Path("backtest/data/cache/quiver_checkpoint.json")
DATE_START = date(2020, 1, 1)
DATE_END = date(2024, 12, 31)
RATE_LIMIT_SLEEP = 1.2  # seconds between calls
COMMIT_EVERY = 50       # commit to git every N tickers

ENDPOINTS = {
    "congressional": f"{BASE_URL}/historical/congresstrading/{{ticker}}",
    "insider":       f"{BASE_URL}/historical/insidertrading/{{ticker}}",
    "institutional": f"{BASE_URL}/historical/institutional/{{ticker}}",
    "gov_contracts": f"{BASE_URL}/historical/govcontracts/{{ticker}}",
    "lobbying":      f"{BASE_URL}/historical/lobbying/{{ticker}}",
    "wikipedia":     f"{BASE_URL}/historical/wikipedia/{{ticker}}",
    "wallstreetbets":f"{BASE_URL}/historical/wallstreetbets/{{ticker}}",
}

DATE_FIELDS = {
    "congressional": "Date",
    "insider":       "Date",
    "institutional": "Date",
    "gov_contracts": "Date",
    "lobbying":      "Date",
    "wikipedia":     "Date",
    "wallstreetbets":"Date",
}


def fetch_with_retry(url: str, max_retries: int = 3) -> list:
    """Fetch URL with retry on rate limit or network error."""
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                return r.json() if r.text.strip() else []
            elif r.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"  Rate limited — waiting {wait}s")
                time.sleep(wait)
            elif r.status_code == 404:
                return []  # ticker not covered
            else:
                print(f"  HTTP {r.status_code}: {r.text[:80]}")
                time.sleep(5)
        except Exception as e:
            print(f"  Network error (attempt {attempt+1}): {e}")
            time.sleep(10)
    return []


def save_ticker_data(ticker: str, data_type: str, records: list):
    """Save records to Parquet. Saves empty file if no records."""
    out_dir = CACHE_DIR / data_type
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{ticker.replace('-','_')}.parquet"

    if not records:
        # Save empty DataFrame with standard columns
        pd.DataFrame().to_parquet(out_file)
        return

    df = pd.DataFrame(records)

    # Filter to date range
    date_col = DATE_FIELDS.get(data_type)
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df[
            (df[date_col] >= pd.Timestamp(DATE_START)) &
            (df[date_col] <= pd.Timestamp(DATE_END))
        ]

    df.to_parquet(out_file, index=False)


def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {dt: [] for dt in ENDPOINTS}


def save_checkpoint(checkpoint: dict):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint))


def git_commit(message: str):
    """Commit and push current cache state."""
    import subprocess
    cmds = [
        ["git", "add", "backtest/data/cache/quiver/"],
        ["git", "add", "backtest/data/cache/quiver_checkpoint.json"],
        ["git", "commit", "-m", message],
        ["git", "push", "origin", "main"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"  Git warning: {result.stderr[:100]}")


def main():
    # Build universe
    sp500 = get_sp500_constituents(500)
    universe = list(dict.fromkeys(sp500 + ETFS_FULL))
    print(f"Universe: {len(universe)} instruments")
    print(f"Data types: {list(ENDPOINTS.keys())}")
    print(f"Date range: {DATE_START} to {DATE_END}")
    print(f"Cache dir: {CACHE_DIR}")
    print()

    checkpoint = load_checkpoint()
    total_done = 0

    for data_type, url_template in ENDPOINTS.items():
        done_tickers = set(checkpoint.get(data_type, []))
        remaining = [t for t in universe if t not in done_tickers]

        print(f"\n{'='*60}")
        print(f"Fetching: {data_type} — {len(remaining)} remaining / {len(universe)} total")
        print(f"{'='*60}")

        batch_count = 0
        for i, ticker in enumerate(remaining):
            url = url_template.format(ticker=ticker)
            records = fetch_with_retry(url)
            save_ticker_data(ticker, data_type, records)
            checkpoint[data_type].append(ticker)
            save_checkpoint(checkpoint)
            batch_count += 1
            total_done += 1

            status = f"✓ {records if isinstance(records, int) else len(records) if records else 0} records"
            print(f"  [{i+1}/{len(remaining)}] {ticker}: {status}")

            # Commit every COMMIT_EVERY tickers
            if batch_count % COMMIT_EVERY == 0:
                print(f"\n  Committing {batch_count} tickers...")
                git_commit(f"Quiver pre-fetch: {data_type} batch ({batch_count} tickers)")
                print(f"  Committed.\n")

            time.sleep(RATE_LIMIT_SLEEP)

        # Final commit for this data type
        print(f"\nCompleted {data_type} — committing...")
        git_commit(f"Quiver pre-fetch: {data_type} complete ({len(universe)} tickers)")

    print(f"\nAll Quiver data pre-fetched and committed.")
    print(f"Cache location: {CACHE_DIR}/")


if __name__ == "__main__":
    main()
