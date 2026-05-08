"""scripts/prefetch_stocktwits.py - Pass 53 v8h+1 owner-approved 2026-05-08.

StockTwits public API (no auth required for streams). Replaces pytrends
as the Twitter-side retail-attention signal source.

Endpoint: https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json
Returns recent messages with user-tagged sentiment (Bullish/Bearish/None)
and trending stream metadata.

Rate limit: 200 req/hour for public (unauthenticated) usage.
Output: data_prefetch/stocktwits/{ticker}.parquet
        Columns: id, body, created_at, sentiment, user_id, user_username,
                 likes_total, conversation_count

Smoke: python scripts/prefetch_stocktwits.py --tickers AAPL TSLA --no-git
Full:  python scripts/prefetch_stocktwits.py --batch-size 50
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts._prefetch_utils import safe_filename_stem  # noqa: E402

BASE = "https://api.stocktwits.com/api/2/streams/symbol"
TIMEOUT = 20
RATE_LIMIT_SLEEP = 18.5  # 200 req/hour = ~1 req per 18s defensively
HEADERS = {"User-Agent": "stock-picks-app retail-sentiment/1.0"}

CACHE_ROOT = Path("data_prefetch/stocktwits")
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
CHECKPOINT = CACHE_ROOT / "_checkpoint.json"


def fetch(ticker: str) -> tuple[list, str | None]:
    url = f"{BASE}/{ticker}.json"
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    except requests.RequestException as e:
        return [], f"REQUEST_EXC:{type(e).__name__}"
    if r.status_code == 404:
        return [], None  # ticker not on StockTwits
    if r.status_code == 429:
        time.sleep(60)
        return [], "RATE_LIMITED"
    if r.status_code != 200:
        return [], f"HTTP_{r.status_code}"
    try:
        body = r.json()
    except Exception:
        return [], "BAD_JSON"
    msgs = body.get("messages") or []
    rows = []
    for m in msgs:
        entities = m.get("entities") or {}
        sentiment_obj = entities.get("sentiment") if isinstance(entities, dict) else None
        sentiment_val = sentiment_obj.get("basic") if isinstance(sentiment_obj, dict) else None
        user = m.get("user") or {}
        likes = m.get("likes") or {}
        conv = m.get("conversation") or {}
        rows.append({
            "id": m.get("id"),
            "body": (m.get("body") or "")[:500],
            "created_at": m.get("created_at"),
            "sentiment": sentiment_val,
            "user_id": user.get("id") if isinstance(user, dict) else None,
            "user_username": user.get("username") if isinstance(user, dict) else None,
            "likes_total": likes.get("total", 0) if isinstance(likes, dict) else 0,
            "conversation_count": conv.get("replies", 0) if isinstance(conv, dict) else 0,
        })
    return rows, None


def save(rows: list, ticker: str) -> int:
    out = CACHE_ROOT / f"{safe_filename_stem(ticker)}.parquet"
    if not rows:
        pd.DataFrame().to_parquet(out)
        return 0
    df = pd.DataFrame(rows)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df.to_parquet(out, index=False)
    return out.stat().st_size


def load_checkpoint() -> set[str]:
    if not CHECKPOINT.exists():
        return set()
    try:
        return set(json.loads(CHECKPOINT.read_text()))
    except Exception:
        return set()


def save_checkpoint(done: set[str]) -> None:
    CHECKPOINT.write_text(json.dumps(sorted(done)))


def git_commit(msg: str) -> None:
    subprocess.run(["git", "add", "--", str(CACHE_ROOT)], capture_output=True)
    r = subprocess.run(["git", "commit", "-m", msg, "--", str(CACHE_ROOT)],
                        capture_output=True, text=True)
    if "nothing to commit" in r.stdout:
        return
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, text=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", default=None)
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--no-git", action="store_true")
    args = ap.parse_args()

    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
    else:
        csv = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
        df = pd.read_csv(csv, comment="#")
        tickers = sorted(df["Symbol"].dropna().str.strip().str.upper().unique())

    done = load_checkpoint()
    remaining = [t for t in tickers if t not in done]
    print(f"=== StockTwits: {len(remaining)} remaining / {len(tickers)} total ===")
    print(f"   rate-limit budget: 200 req/h => est wall time: {len(remaining)*RATE_LIMIT_SLEEP/3600:.1f} h")

    batch = 0
    for i, t in enumerate(remaining, 1):
        print(f"  [{i}/{len(remaining)}] {t} ... ", end="", flush=True)
        rows, err = fetch(t)
        if err:
            print(f"ERROR {err}")
            time.sleep(RATE_LIMIT_SLEEP)
            continue
        save(rows, t)
        done.add(t)
        save_checkpoint(done)
        batch += 1
        print(f"OK msgs={len(rows)}")
        if not args.no_git and batch % args.batch_size == 0:
            git_commit(f"StockTwits batch {batch // args.batch_size}")
        time.sleep(RATE_LIMIT_SLEEP)

    if not args.no_git and batch > 0:
        git_commit(f"StockTwits final ({batch} fetched)")
    print(f"\nDONE. cached={len(done)}/{len(tickers)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
