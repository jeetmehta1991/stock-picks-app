"""scripts/prefetch_polygon_corp_actions_full.py - Polygon dividends + splits + IPOs.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H3 P1.

Probe-confirmed working at our Stocks Starter tier:
  /v3/reference/dividends -> cash_amount, currency, declaration_date,
                              dividend_type, ex_dividend_date, frequency,
                              id, pay_date, record_date, ticker
  /v3/reference/splits    -> execution_date, id, split_from, split_to, ticker
  /vX/reference/ipos      -> ticker, last_updated, announced_date,
                              issuer_name, currency_code, max_shares_offered,
                              primary_exchange, security_type

Output:
  data_prefetch/polygon/dividends_full/all.parquet  (paginated all dividends)
  data_prefetch/polygon/splits_full/all.parquet     (paginated all splits)
  data_prefetch/polygon/ipos_full/all.parquet       (paginated all IPOs)
  Plus per-ticker filtered slices in dividends_full/{t}.parquet etc.
"""

from __future__ import annotations

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path

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

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set")
    sys.exit(1)

TIMEOUT = 30
RATE_LIMIT_SLEEP = 0.2  # Stocks Starter is unlimited; gentle


RESERVED_WIN = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}


def safe_filename_stem(ticker: str) -> str:
    """Avoid Windows-reserved filenames (CON/PRN/AUX/NUL/COM1-9/LPT1-9)."""
    safe = str(ticker).replace("-", "_")
    if safe.upper() in RESERVED_WIN:
        safe = safe + "_"
    return safe


def fetch_paginated(url: str, params: dict | None = None,
                     max_pages: int = 100) -> list[dict]:
    h = {"Authorization": f"Bearer {POLYGON_KEY}"}
    out: list[dict] = []
    next_url = url
    p = dict(params or {})
    pages = 0
    while next_url and pages < max_pages:
        r = requests.get(next_url, headers=h, params=p, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}: {r.text[:120]}")
            break
        data = r.json()
        results = data.get("results", []) or []
        out.extend(results)
        next_url = data.get("next_url")
        pages += 1
        p = {}
        time.sleep(RATE_LIMIT_SLEEP)
    return out


def main() -> int:
    base = Path("data_prefetch/polygon")
    base.mkdir(parents=True, exist_ok=True)

    print("=== Polygon corp actions (dividends + splits + IPOs) ===")

    # 1. ALL dividends (paginated; sort by ex_dividend_date desc)
    print("  Dividends ... ", end="", flush=True)
    divs = fetch_paginated("https://api.polygon.io/v3/reference/dividends",
                            params={"limit": 1000, "order": "asc",
                                     "sort": "ex_dividend_date"})
    if divs:
        df = pd.DataFrame(divs)
        for col in ("declaration_date", "ex_dividend_date", "pay_date", "record_date"):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        out_dir = base / "dividends_full"
        out_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_dir / "all.parquet", index=False)
        # Per-ticker shards
        for t, g in df.groupby("ticker"):
            g.to_parquet(out_dir / f"{safe_filename_stem(t)}.parquet", index=False)
        print(f"OK {len(df)} dividends across {df['ticker'].nunique()} tickers")
    else:
        print("EMPTY")

    # 2. ALL splits
    print("  Splits ... ", end="", flush=True)
    splits = fetch_paginated("https://api.polygon.io/v3/reference/splits",
                              params={"limit": 1000, "order": "asc",
                                       "sort": "execution_date"})
    if splits:
        df = pd.DataFrame(splits)
        if "execution_date" in df.columns:
            df["execution_date"] = pd.to_datetime(df["execution_date"], errors="coerce")
        out_dir = base / "splits_full"
        out_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_dir / "all.parquet", index=False)
        for t, g in df.groupby("ticker"):
            g.to_parquet(out_dir / f"{safe_filename_stem(t)}.parquet", index=False)
        print(f"OK {len(df)} splits across {df['ticker'].nunique()} tickers")
    else:
        print("EMPTY")

    # 3. ALL IPOs
    print("  IPOs ... ", end="", flush=True)
    ipos = fetch_paginated("https://api.polygon.io/vX/reference/ipos",
                            params={"limit": 1000, "order": "asc"})
    if ipos:
        df = pd.DataFrame(ipos)
        for col in ("announced_date", "ipo_date", "last_updated"):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        out_dir = base / "ipos_full"
        out_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_dir / "all.parquet", index=False)
        if "ticker" in df.columns:
            for t, g in df[df["ticker"].notna()].groupby("ticker"):
                g.to_parquet(out_dir / f"{safe_filename_stem(t)}.parquet", index=False)
        print(f"OK {len(df)} IPOs")
    else:
        print("EMPTY")

    print("\nCorp actions prefetch complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
