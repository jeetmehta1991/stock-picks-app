"""scripts/prefetch_alfred_mirror.py - mirror new FRED series to ALFRED with vintage.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H16 P2.

Reads SERIES dict from prefetch_macro.py (truth source), fetches each
series with realtime_start + realtime_end parameters to get vintage data,
saves to data_prefetch/alfred/{series_id}.parquet.

ALFRED endpoint = same as FRED but with realtime_* params.
"""

from __future__ import annotations

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

FRED_KEY = os.environ.get("FRED_API_KEY", "")
if not FRED_KEY:
    print("ERROR: FRED_API_KEY not set")
    sys.exit(1)

OUT_DIR = Path("data_prefetch/alfred")
EXISTING_FRED = Path("data_prefetch/fred/observations")
DATE_START = "2020-01-01"
DATE_END = "2026-12-31"
# ALFRED vintage query - request all revisions across full history.
# Per FRED docs, realtime_start='1776-07-04' (earliest) + realtime_end=today
# returns every revision/vintage ever published for the series.
RT_START = "1776-07-04"
RT_END = "9999-12-31"


def fetch_alfred(series_id: str) -> pd.DataFrame:
    url = "https://api.stlouisfed.org/fred/series/observations"
    p = {
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "observation_start": DATE_START,
        "observation_end": DATE_END,
        "realtime_start": RT_START,
        "realtime_end": RT_END,
    }
    r = requests.get(url, params=p, timeout=30)
    if r.status_code != 200:
        return pd.DataFrame()
    obs = r.json().get("observations", []) or []
    if not obs:
        return pd.DataFrame()
    df = pd.DataFrame(obs)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    return df


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Use FRED cache as truth source for which series to mirror
    if not EXISTING_FRED.exists():
        print("ERROR: FRED observations cache missing - run prefetch_macro.py first")
        return 1
    series_ids = sorted(
        f.stem for f in EXISTING_FRED.glob("*.parquet") if f.stem
    )
    # Skip if already in ALFRED
    existing_alfred = {f.stem for f in OUT_DIR.glob("*.parquet")}
    missing = [s for s in series_ids if s not in existing_alfred]
    print(f"=== ALFRED mirror prefetch ===")
    print(f"FRED series total: {len(series_ids)}")
    print(f"Already in ALFRED: {len(existing_alfred)}")
    print(f"To mirror: {len(missing)}")
    print()
    ok = 0
    for sid in missing:
        print(f"  {sid} ... ", end="", flush=True)
        try:
            df = fetch_alfred(sid)
            if df.empty:
                print("EMPTY")
                continue
            df.to_parquet(OUT_DIR / f"{sid}.parquet", index=False)
            print(f"OK {len(df)} obs")
            ok += 1
        except Exception as e:
            print(f"ERROR {e}")
        time.sleep(0.2)
    print(f"\nALFRED mirror: {ok}/{len(missing)} mirrored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
