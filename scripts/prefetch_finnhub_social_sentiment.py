"""scripts/prefetch_finnhub_social_sentiment.py - Pass 53 v8h+1 owner-approved 2026-05-08.

Finnhub /stock/social-sentiment endpoint. Aggregates Reddit + Twitter mentions
per ticker per day. Replaces pytrends as the cross-platform retail-attention
signal source.

Endpoint: https://finnhub.io/api/v1/stock/social-sentiment?symbol={ticker}
Returns daily Reddit + Twitter mention counts + positive/negative sentiment.

Output: data_prefetch/finnhub/social_sentiment/{ticker}.parquet
        Columns: atTime, source, mention, positiveScore, negativeScore,
                 positiveMention, negativeMention, score
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


def _load_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
KEY = os.environ.get("FINNHUB_API_KEY", "")
if not KEY:
    print("ERROR: FINNHUB_API_KEY not set")
    sys.exit(1)

BASE = "https://finnhub.io/api/v1/stock/social-sentiment"
TIMEOUT = 20
RATE_LIMIT_SLEEP = 1.1  # Finnhub free: 60 req/min => ~1 req/s defensively

CACHE_ROOT = Path("data_prefetch/finnhub/social_sentiment")
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
CHECKPOINT = CACHE_ROOT / "_checkpoint.json"


def fetch(ticker: str) -> tuple[list, str | None]:
    try:
        r = requests.get(BASE, params={"symbol": ticker, "token": KEY}, timeout=TIMEOUT)
    except requests.RequestException as e:
        return [], f"REQUEST_EXC:{type(e).__name__}"
    if r.status_code == 401:
        return [], "AUTH_401"
    if r.status_code == 403:
        return [], "TIER_403"  # may be premium-locked for some tickers
    if r.status_code == 429:
        time.sleep(30)
        return [], "RATE_LIMITED"
    if r.status_code != 200:
        return [], f"HTTP_{r.status_code}"
    try:
        body = r.json()
    except Exception:
        return [], "BAD_JSON"
    rows = []
    for source_name in ("reddit", "twitter"):
        for entry in (body.get(source_name) or []):
            rows.append({
                "atTime": entry.get("atTime"),
                "source": source_name,
                "mention": entry.get("mention"),
                "positiveScore": entry.get("positiveScore"),
                "negativeScore": entry.get("negativeScore"),
                "positiveMention": entry.get("positiveMention"),
                "negativeMention": entry.get("negativeMention"),
                "score": entry.get("score"),
            })
    return rows, None


def save(rows: list, ticker: str) -> int:
    out = CACHE_ROOT / f"{safe_filename_stem(ticker)}.parquet"
    if not rows:
        pd.DataFrame().to_parquet(out)
        return 0
    df = pd.DataFrame(rows)
    if "atTime" in df.columns:
        df["atTime"] = pd.to_datetime(df["atTime"], errors="coerce")
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
    ap.add_argument("--batch-size", type=int, default=100)
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
    print(f"=== Finnhub social_sentiment: {len(remaining)} remaining / {len(tickers)} total ===")

    batch = 0
    for i, t in enumerate(remaining, 1):
        print(f"  [{i}/{len(remaining)}] {t} ... ", end="", flush=True)
        rows, err = fetch(t)
        if err == "TIER_403":
            print("TIER_LOCKED (skipping)")
            done.add(t)
            save_checkpoint(done)
            time.sleep(RATE_LIMIT_SLEEP)
            continue
        if err:
            print(f"ERROR {err}")
            time.sleep(RATE_LIMIT_SLEEP)
            continue
        save(rows, t)
        done.add(t)
        save_checkpoint(done)
        batch += 1
        print(f"OK rows={len(rows)}")
        if not args.no_git and batch % args.batch_size == 0:
            git_commit(f"Finnhub social_sentiment batch {batch // args.batch_size}")
        time.sleep(RATE_LIMIT_SLEEP)

    if not args.no_git and batch > 0:
        git_commit(f"Finnhub social_sentiment final ({batch} fetched)")
    print(f"\nDONE. cached={len(done)}/{len(tickers)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
