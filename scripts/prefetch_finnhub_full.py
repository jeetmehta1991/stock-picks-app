"""scripts/prefetch_finnhub_full.py - Finnhub free-tier full prefetch.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08 (after FINNHUB_API_KEY added).

Probe-confirmed accessible at FREE tier (13 endpoints):
  /quote, /stock/profile2, /stock/peers, /stock/insider-transactions,
  /stock/insider-sentiment, /stock/recommendation, /stock/earnings (eps_surprise),
  /calendar/earnings, /calendar/ipo, /calendar/economic, /company-news,
  /stock/financials-reported, /stock/metric

Probe-confirmed PREMIUM (skipped, 7 endpoints):
  /stock/price-target, /stock/social-sentiment, /stock/upgrade-downgrade,
  /stock/eps-estimate, /stock/revenue-estimate, /stock/dividend, /stock/split

Output: data_prefetch/finnhub/{endpoint}/{ticker}.parquet (per-ticker
endpoints) + data_prefetch/finnhub/{endpoint}.parquet (global cal endpoints)

Free tier rate limit: 60 calls/min = 1.1s sleep
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))


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

FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "")
if not FINNHUB_KEY:
    print("ERROR: FINNHUB_API_KEY not set")
    sys.exit(1)

CACHE_ROOT = Path("data_prefetch/finnhub")
CHECKPOINT_FILE = CACHE_ROOT / "_checkpoint.json"
TIMEOUT = 30
RATE_LIMIT_SLEEP = 1.1  # 60/min ceiling

DATE_FROM = "2020-01-01"
DATE_TO = "2026-12-31"

# Per-ticker endpoints (1937 fetches each)
PER_TICKER_ENDPOINTS = [
    ("quote", "/quote"),
    ("profile2", "/stock/profile2"),
    ("peers", "/stock/peers"),
    ("insider_transactions", "/stock/insider-transactions"),
    ("insider_sentiment", "/stock/insider-sentiment"),
    ("recommendation", "/stock/recommendation"),
    ("earnings", "/stock/earnings"),
    ("company_news", "/company-news"),
    ("financials_reported", "/stock/financials-reported"),
    ("metric", "/stock/metric"),
]

# Global endpoints (one fetch covers all)
GLOBAL_ENDPOINTS = [
    ("calendar_earnings", "/calendar/earnings", {"from": DATE_FROM, "to": DATE_TO}),
    ("calendar_ipo", "/calendar/ipo", {"from": DATE_FROM, "to": DATE_TO}),
    ("calendar_economic", "/calendar/economic", {"from": DATE_FROM, "to": DATE_TO}),
]


def fetch_endpoint(path: str, params: dict) -> dict | list | None:
    url = f"https://finnhub.io/api/v1{path}"
    p = {**params, "token": FINNHUB_KEY}
    try:
        r = requests.get(url, params=p, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            time.sleep(60)
            r = requests.get(url, params=p, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
        return None
    except Exception:
        return None


def to_dataframe(data) -> pd.DataFrame:
    """Best-effort flatten of Finnhub response shapes."""
    if data is None:
        return pd.DataFrame()
    if isinstance(data, list):
        return pd.DataFrame(data) if data else pd.DataFrame()
    if isinstance(data, dict):
        # Common shapes: {"data": [...], ...} or {"earnings": [...]}
        for key in ("data", "earnings", "financials", "ipoCalendar",
                    "economicCalendar", "earningsCalendar"):
            if key in data and isinstance(data[key], list):
                return pd.DataFrame(data[key])
        # Single-record (e.g. quote, profile2) - wrap as 1-row DataFrame
        # Filter out symbol/ticker repetition
        return pd.DataFrame([data])
    return pd.DataFrame()


def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_checkpoint(cp: dict) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(cp))


def git_commit_paths(message: str, paths: list[str]) -> None:
    """Commit specific paths only (avoids capturing unrelated staged files —
    INV-041 fix)."""
    import subprocess
    for p in paths:
        subprocess.run(["git", "add", "--", p], capture_output=True)
    result = subprocess.run(["git", "commit", "-m", message] + ["--"] + paths,
                            capture_output=True, text=True)
    if "nothing to commit" in result.stdout:
        return
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, text=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", default=None)
    ap.add_argument("--batch-size", type=int, default=100)
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--global-only", action="store_true",
                    help="Only fetch global (calendar) endpoints")
    ap.add_argument("--per-ticker-only", action="store_true",
                    help="Skip global; fetch per-ticker only")
    args = ap.parse_args()

    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    cp = load_checkpoint()

    # 1. Global endpoints (fast)
    if not args.per_ticker_only:
        print("=== Global endpoints ===")
        for label, path, params in GLOBAL_ENDPOINTS:
            print(f"  {label} ... ", end="", flush=True)
            data = fetch_endpoint(path, params)
            if data is not None:
                df = to_dataframe(data)
                out = CACHE_ROOT / f"{label}.parquet"
                if df.empty:
                    pd.DataFrame().to_parquet(out)
                    print("EMPTY")
                else:
                    df.to_parquet(out, index=False)
                    print(f"OK {len(df)} rows")
            else:
                print("FAIL")
            time.sleep(RATE_LIMIT_SLEEP)
        if not args.no_git:
            git_commit_paths("Finnhub global endpoints prefetch",
                              [str(CACHE_ROOT)])

    if args.global_only:
        return 0

    # 2. Per-ticker endpoints
    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
    else:
        master_csv = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
        df_uni = pd.read_csv(master_csv, comment="#")
        tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())

    print(f"\n=== Per-ticker endpoints ({len(PER_TICKER_ENDPOINTS)} x {len(tickers)} tickers) ===")
    for label, path in PER_TICKER_ENDPOINTS:
        out_dir = CACHE_ROOT / label
        out_dir.mkdir(parents=True, exist_ok=True)
        done = set(cp.get(label, []))
        remaining = [t for t in tickers if t not in done]
        print(f"\n--- {label} --- {len(remaining)} remaining / {len(tickers)}")
        batch_count = 0
        for i, ticker in enumerate(remaining, 1):
            params = {"symbol": ticker}
            if label in ("insider_sentiment", "company_news"):
                params["from"] = DATE_FROM
                params["to"] = DATE_TO
            elif label == "metric":
                params["metric"] = "all"
            print(f"  [{i}/{len(remaining)}] {ticker} ... ", end="", flush=True)
            try:
                data = fetch_endpoint(path, params)
                df = to_dataframe(data)
                out = out_dir / f"{ticker.replace('-', '_')}.parquet"
                if df.empty:
                    pd.DataFrame().to_parquet(out)
                    print("EMPTY")
                else:
                    df.to_parquet(out, index=False)
                    print(f"OK {len(df)}")
                cp.setdefault(label, []).append(ticker)
                save_checkpoint(cp)
                batch_count += 1
                if not args.no_git and batch_count % args.batch_size == 0:
                    git_commit_paths(
                        f"Finnhub: {label} batch {batch_count // args.batch_size}",
                        [str(out_dir), str(CHECKPOINT_FILE)],
                    )
            except Exception as e:
                print(f"ERROR {e}")
            time.sleep(RATE_LIMIT_SLEEP)
        if not args.no_git and batch_count > 0:
            git_commit_paths(f"Finnhub: {label} final ({batch_count} fetched)",
                              [str(out_dir), str(CHECKPOINT_FILE)])
        print(f"  {label} done: {len(cp.get(label, []))}")

    print("\nFinnhub full prefetch complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
