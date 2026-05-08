"""scripts/prefetch_polygon_options_full.py - Tier H10 endpoint 1 full rollout.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08.

Fetches /v3/reference/options/contracts for ALL Master-Universe tickers, with
checkpointing + path-restricted git commits. Endpoint 2 (per-contract daily
OHLCV) is NOT included - that requires a separate scope decision (TB-class
storage projection).

Output:
  data_prefetch/polygon/options_chains/{ticker}.parquet
  data_prefetch/polygon/options_chains/_checkpoint.json

Run:
  python scripts/prefetch_polygon_options_full.py --batch-size 100
  python scripts/prefetch_polygon_options_full.py --tickers AAPL TSLA --no-git  (smoke)
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

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

BASE = "https://api.polygon.io"
TIMEOUT = 30
RATE_LIMIT_SLEEP = 0.6
MAX_PAGES = 100  # SPY/QQQ have >10K contracts; raised from smoke cap of 10

CACHE_ROOT = Path("data_prefetch/polygon/options_chains")
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
CHECKPOINT_FILE = CACHE_ROOT / "_checkpoint.json"


def fetch_options_chain(underlying: str) -> tuple[list, int, str | None]:
    """Returns (contracts, http_pages, error_or_None)."""
    url = f"{BASE}/v3/reference/options/contracts"
    params = {
        "underlying_ticker": underlying,
        "expired": "false",
        "limit": 1000,
        "apiKey": POLYGON_KEY,
    }
    contracts: list = []
    pages = 0
    next_url: str | None = None
    while pages < MAX_PAGES:
        try:
            if next_url:
                r = requests.get(next_url + f"&apiKey={POLYGON_KEY}", timeout=TIMEOUT)
            else:
                r = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            return (contracts, pages, f"REQUEST_EXC: {type(e).__name__}")
        pages += 1
        if r.status_code == 401:
            return (contracts, pages, "AUTH_401")
        if r.status_code == 403:
            return (contracts, pages, "TIER_403")
        if r.status_code == 429:
            time.sleep(60)
            continue
        if r.status_code == 404:
            return ([], pages, None)  # no chain for this ticker
        if r.status_code != 200:
            return (contracts, pages, f"HTTP_{r.status_code}")
        body = r.json()
        results = body.get("results") or []
        contracts.extend(results)
        next_url = body.get("next_url")
        if not next_url:
            break
        time.sleep(RATE_LIMIT_SLEEP)
    return (contracts, pages, None)


def save(contracts: list, underlying: str) -> int:
    out = CACHE_ROOT / f"{safe_filename_stem(underlying)}.parquet"
    if not contracts:
        pd.DataFrame().to_parquet(out)
        return 0
    df = pd.DataFrame(contracts)
    if "expiration_date" in df.columns:
        df["expiration_date"] = pd.to_datetime(df["expiration_date"], errors="coerce")
    df.to_parquet(out, index=False)
    return out.stat().st_size


def load_checkpoint() -> set[str]:
    if not CHECKPOINT_FILE.exists():
        return set()
    try:
        return set(json.loads(CHECKPOINT_FILE.read_text()))
    except Exception:
        return set()


def save_checkpoint(done: set[str]) -> None:
    CHECKPOINT_FILE.write_text(json.dumps(sorted(done)))


def git_commit(message: str) -> None:
    """Path-restricted commit per INV-041 fix."""
    cache_path = str(CACHE_ROOT)
    subprocess.run(["git", "add", "--", cache_path], capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", message, "--", cache_path],
        capture_output=True, text=True,
    )
    if "nothing to commit" in result.stdout:
        return
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, text=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)


def load_universe() -> list[str]:
    csv = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
    df = pd.read_csv(csv, comment="#")
    return sorted(df["Symbol"].dropna().str.strip().str.upper().unique())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", default=None,
                    help="Explicit tickers (overrides universe)")
    ap.add_argument("--batch-size", type=int, default=100,
                    help="Tickers per git commit batch")
    ap.add_argument("--no-git", action="store_true")
    args = ap.parse_args()

    tickers = args.tickers if args.tickers else load_universe()
    done = load_checkpoint()
    remaining = [t for t in tickers if t not in done]
    print(f"=== Polygon Options chain reference: {len(remaining)} remaining / {len(tickers)} total ===")

    batch_count = 0
    errors: list[tuple[str, str]] = []

    for i, t in enumerate(remaining, 1):
        print(f"  [{i}/{len(remaining)}] {t} ... ", end="", flush=True)
        contracts, pages, err = fetch_options_chain(t)
        if err:
            errors.append((t, err))
            print(f"ERROR {err} (pages={pages})")
            time.sleep(RATE_LIMIT_SLEEP)
            continue
        n = len(contracts)
        save(contracts, t)
        done.add(t)
        save_checkpoint(done)
        batch_count += 1
        print(f"OK contracts={n} pages={pages}")

        if not args.no_git and batch_count % args.batch_size == 0:
            git_commit(f"Polygon Options chain ref: batch {batch_count // args.batch_size} ({batch_count} tickers)")

        time.sleep(RATE_LIMIT_SLEEP)

    if not args.no_git and batch_count > 0:
        git_commit(f"Polygon Options chain ref: final ({batch_count} tickers fetched)")

    print()
    print(f"DONE. cached={len(done)}/{len(tickers)} errors={len(errors)}")
    if errors[:10]:
        print("First errors:")
        for t, e in errors[:10]:
            print(f"  {t}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
