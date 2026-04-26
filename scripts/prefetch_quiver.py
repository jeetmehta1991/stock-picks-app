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
DATE_END = date(2026, 3, 31)
RATE_LIMIT_SLEEP = 1.2  # seconds between calls
COMMIT_EVERY = 50       # commit to git every N tickers

ENDPOINTS = {
    "congressional": f"{BASE_URL}/historical/congresstrading/{{ticker}}",
    "insider":       f"{BASE_URL}/live/insiders?ticker={{ticker}}",
    "institutional": f"{BASE_URL}/live/sec13f?ticker={{ticker}}",
    "gov_contracts": f"{BASE_URL}/historical/govcontracts/{{ticker}}",
    "lobbying":      f"{BASE_URL}/historical/lobbying/{{ticker}}",
    "wikipedia":     f"{BASE_URL}/historical/wikipedia/{{ticker}}",
    "wallstreetbets":f"{BASE_URL}/historical/wallstreetbets/{{ticker}}",
}

DATE_FIELDS = {
    "congressional": "TransactionDate",
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
    """Commit and push current cache state with rebase to prevent rejections."""
    import subprocess
    # Add and commit
    subprocess.run(["git", "add",
                    "backtest/data/cache/quiver/",
                    "backtest/data/cache/quiver_checkpoint.json"],
                   capture_output=True)
    result = subprocess.run(["git", "commit", "-m", message],
                            capture_output=True, text=True)
    if "nothing to commit" in result.stdout:
        return
    # Rebase before push to avoid rejection from parallel runs
    rebase = subprocess.run(["git", "pull", "--rebase", "origin", "main"],
                            capture_output=True, text=True)
    if rebase.returncode != 0:
        print(f"  Git rebase warning: {rebase.stderr[:100]}")
    push = subprocess.run(["git", "push", "origin", "main"],
                          capture_output=True, text=True)
    if push.returncode != 0:
        print(f"  Git push warning: {push.stderr[:100]}")


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

    # Congressional already complete — skip if all 509 done
    if len(checkpoint.get("congressional", [])) >= 509:
        print("Congressional: already complete — skipping")

    for data_type, url_template in ENDPOINTS.items():
        done_tickers = set(checkpoint.get(data_type, []))
        if len(done_tickers) >= 509:
            print(f"Skipping {data_type} — already complete ({len(done_tickers)} tickers)")
            continue

        remaining = [t for t in universe if t not in done_tickers]

        print(f"\n{'='*60}")
        print(f"Fetching: {data_type} — {len(remaining)} remaining / {len(universe)} total")
        print(f"{'='*60}")

        batch_count = 0
        for i, ticker in enumerate(remaining):
            try:
                url = url_template.format(ticker=ticker)
                records = fetch_with_retry(url)
                save_ticker_data(ticker, data_type, records)
                checkpoint[data_type].append(ticker)
                save_checkpoint(checkpoint)
                batch_count += 1
                total_done += 1

                n = len(records) if isinstance(records, list) else 0
                print(f"  [{i+1}/{len(remaining)}] {ticker}: ✓ {n} records")

                # Commit every COMMIT_EVERY tickers
                if batch_count % COMMIT_EVERY == 0:
                    print(f"\n  Committing {batch_count} tickers...")
                    git_commit(f"Quiver pre-fetch: {data_type} batch {batch_count//COMMIT_EVERY}")
                    print(f"  Committed.\n")

                time.sleep(RATE_LIMIT_SLEEP)

            except KeyboardInterrupt:
                print(f"\nInterrupted at {ticker} — saving checkpoint and committing...")
                git_commit(f"Quiver pre-fetch: {data_type} interrupted at {ticker}")
                raise
            except Exception as e:
                print(f"  ERROR on {ticker}: {e} — skipping and continuing")
                time.sleep(5)
                continue

        # Final commit for this data type — retry push up to 3 times
        print(f"\nCompleted {data_type} — committing...")
        for attempt in range(3):
            git_commit(f"Quiver pre-fetch: {data_type} complete ({len(universe)} tickers)")
            # Verify push succeeded
            import subprocess
            check = subprocess.run(
                ["git", "log", "--oneline", "-1", "origin/main"],
                capture_output=True, text=True
            )
            local = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True, text=True
            )
            if check.stdout.strip() == local.stdout.strip():
                print(f"  ✅ Push confirmed on origin/main")
                break
            else:
                print(f"  ⚠️  Push may have failed (attempt {attempt+1}/3) — retrying...")
                import time as _t; _t.sleep(5)
        else:
            print(f"\n  ❌ PUSH FAILED after 3 attempts for {data_type}")
            print(f"  DO NOT RUN git reset --hard")
            print(f"  Run manually: git add backtest/data/cache/quiver/ && git commit -m 'manual push' && git pull --rebase origin main && git push origin main")

    print(f"\nAll Quiver data pre-fetched and committed.")
    print(f"Cache location: {CACHE_DIR}/")
    print(f"\n⚠️  IMPORTANT: Run 'git status' before any git reset --hard")
    print(f"   If files show as modified/untracked, commit them first!")


if __name__ == "__main__":
    main()
