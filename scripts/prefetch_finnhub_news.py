"""
scripts/prefetch_finnhub_news.py — Pre-fetch Finnhub news sentiment per ticker.

Downloads company news and computes daily sentiment score.
Free tier: 60 calls/minute, ~1 year lookback per call.
Strategy: fetch in annual batches (2022, 2023, 2024) per ticker.

Run from laptop (Codespaces may block Finnhub):
  python scripts/prefetch_finnhub_news.py

Progress saved every 50 tickers — safe to interrupt and resume.
"""

import os
import sys
import time
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
# INV-016 fix Pass 53 v8h+1 owner-approved 2026-05-08: read Master Universe
# (1937) instead of S&P 500 + ETFs only (~509). Falls back to legacy scope
# if Master Universe CSV not present.
from backtest.data.universe import get_sp500_constituents, ETFS_FULL


def _load_master_universe() -> list[str] | None:
    """Master Universe Deduplicated CSV; returns None if not found."""
    csv = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
    if not csv.exists():
        return None
    df = pd.read_csv(csv, comment="#")
    return sorted(df["Symbol"].dropna().str.strip().str.upper().unique())

FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "")
if not FINNHUB_KEY:
    print("ERROR: FINNHUB_API_KEY not set")
    sys.exit(1)

CACHE_DIR = Path("backtest/data/cache/finnhub_news")
CHECKPOINT_FILE = Path("backtest/data/cache/finnhub_news_checkpoint.json")
RATE_LIMIT_SLEEP = 1.1   # 60 calls/min = 1 per second, use 1.1 for safety
COMMIT_EVERY = 50

# Annual batches - free tier handles ~1 year per call
# Finnhub free tier: ~1 year lookback from today (April 2026)
# 2022-2024 returns empty results on free tier - only fetch recent data
# This covers our OOS period (2025-Mar 2026) which is most critical
BATCHES = [
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-03-31"),
]


def fetch_news(ticker: str, from_date: str, to_date: str) -> list:
    url = (
        f"https://finnhub.io/api/v1/company-news"
        f"?symbol={ticker}&from={from_date}&to={to_date}"
        f"&token={FINNHUB_KEY}"
    )
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json() if r.text.strip() else []
            elif r.status_code == 429:
                print(f"  Rate limited - waiting 60s")
                time.sleep(60)
            else:
                return []
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(10)
    return []


def score_sentiment(article: dict) -> float:
    """
    Use Finnhub native sentiment score if available (superior NLP model).
    Falls back to keyword scoring only if Finnhub sentiment not present.
    Finnhub returns: sentiment field with score (-1 to 1) and magnitude.
    """
    # Prefer Finnhub native sentiment
    if "sentiment" in article and article["sentiment"] is not None:
        s = article["sentiment"]
        if isinstance(s, dict) and "score" in s:
            return float(s["score"])
        if isinstance(s, (int, float)):
            return float(s)

    # Keyword fallback
    headline = article.get("headline", "")
    summary = article.get("summary", "")
    text = f"{headline} {summary}".lower()
    positive = ["beat", "exceed", "strong", "growth", "record", "surge",
                "upgrade", "outperform", "buy", "bullish", "profit", "gain",
                "positive", "raised", "above", "better"]
    negative = ["miss", "below", "weak", "decline", "loss", "cut", "downgrade",
                "underperform", "sell", "bearish", "negative", "warning",
                "concern", "risk", "fall", "drop", "lower", "lawsuit", "fraud"]
    pos = sum(1 for w in positive if w in text)
    neg = sum(1 for w in negative if w in text)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


def process_ticker(ticker: str) -> pd.DataFrame:
    """Fetch news for all batches and compute daily sentiment."""
    all_articles = []
    for from_date, to_date in BATCHES:
        articles = fetch_news(ticker, from_date, to_date)
        all_articles.extend(articles)
        time.sleep(RATE_LIMIT_SLEEP)

    if not all_articles:
        return pd.DataFrame()

    rows = []
    for a in all_articles:
        ts = a.get("datetime", 0)
        if not ts:
            continue
        dt = pd.Timestamp(ts, unit="s").date()
        score = score_sentiment(a)
        rows.append({"date": dt, "sentiment": score, "headline": a.get("headline","")[:100]})

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])

    # Aggregate to daily: mean sentiment + article count
    daily = df.groupby("date").agg(
        sentiment_mean=("sentiment", "mean"),
        article_count=("sentiment", "count")
    ).reset_index()
    return daily


# NOTE: If BATCHES dates changed, delete checkpoint file to force re-download
# rm backtest/data/cache/finnhub_news_checkpoint.json

def load_checkpoint(batch: int = 0) -> list:
    key = f"batch_{batch}" if batch > 0 else "all"
    if CHECKPOINT_FILE.exists():
        data = json.loads(CHECKPOINT_FILE.read_text())
        if isinstance(data, dict):
            return data.get(key, [])
        return data  # legacy format
    return []


def save_checkpoint(done: list, batch: int = 0):
    key = f"batch_{batch}" if batch > 0 else "all"
    existing = {}
    if CHECKPOINT_FILE.exists():
        try:
            existing = json.loads(CHECKPOINT_FILE.read_text())
            if not isinstance(existing, dict):
                existing = {"all": existing}
        except:
            existing = {}
    existing[key] = done
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(existing))


def git_commit(message: str):
    """Path-restricted commit per INV-041 - only stages the finnhub_news
    cache + checkpoint, prevents capturing unrelated staged files."""
    import subprocess
    cache_path = "backtest/data/cache/finnhub_news/"
    cp_path = "backtest/data/cache/finnhub_news_checkpoint.json"
    subprocess.run(["git", "add", "--", cache_path, cp_path], capture_output=True)
    subprocess.run(["git", "commit", "-m", message, "--", cache_path, cp_path],
                    capture_output=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, default=0,
        help='Batch 1-5 for GitHub Actions (0=all, default)')
    args = parser.parse_args()

    master = _load_master_universe()
    if master:
        universe = master
        print(f"INV-016 fix: loaded {len(universe)} tickers from Master Universe Deduplicated CSV")
    else:
        sp500 = get_sp500_constituents(500)
        universe = list(dict.fromkeys(sp500 + ETFS_FULL))
        print(f"Master Universe CSV not found; falling back to S&P 500 + ETFs ({len(universe)})")

    # Split into 5 batches for GitHub Actions 6-hour limit
    if args.batch > 0:
        batch_size = len(universe) // 5 + 1
        start = (args.batch - 1) * batch_size
        end = min(args.batch * batch_size, len(universe))
        universe = universe[start:end]
        print(f"Batch {args.batch}/5: tickers {start+1}-{end} ({len(universe)} tickers)")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    done = load_checkpoint(args.batch)
    remaining = [t for t in universe if t not in done]

    print(f"Finnhub news pre-fetch")
    print(f"Universe: {len(universe)} | Done: {len(done)} | Remaining: {len(remaining)}")
    print(f"Batches: {BATCHES}")
    print()

    batch_count = 0
    for i, ticker in enumerate(remaining):
        df = process_ticker(ticker)
        out_file = CACHE_DIR / f"{ticker.replace('-','_')}.parquet"
        if df.empty:
            pd.DataFrame().to_parquet(out_file)
        else:
            df.to_parquet(out_file, index=False)

        done.append(ticker)
        save_checkpoint(done, args.batch)
        batch_count += 1

        n = len(df) if not df.empty else 0
        print(f"  [{i+1}/{len(remaining)}] {ticker}: {n} daily sentiment rows")

        if batch_count % COMMIT_EVERY == 0:
            print(f"\n  Committing batch of {COMMIT_EVERY}...")
            git_commit(f"Finnhub news pre-fetch: batch {batch_count//COMMIT_EVERY}")
            print(f"  Committed.\n")

    git_commit(f"Finnhub news batch {args.batch}: complete ({len(universe)} tickers)")
    print("\nFinnhub news pre-fetch complete.")


if __name__ == "__main__":
    main()
