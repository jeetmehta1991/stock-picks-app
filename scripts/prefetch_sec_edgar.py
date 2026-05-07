"""scripts/prefetch_sec_edgar.py — Pre-fetch SEC EDGAR filings per ticker.

Pass 53 Day-9 v8h Tier A12 + B1-B4 (owner-approved 2026-05-07 "All tiers do
it now"). Replaces ad-hoc per-form prefetches with a single comprehensive
script covering existing + new form types.

Form types:
  Existing (top-up to 100% coverage):
    4         — insider transactions
    8-K       — material event disclosures
    SC 13D    — activist 5%+ holder
    SC 13G    — passive 5%+ holder
  NEW (Tier B):
    10-K      — annual report
    10-Q      — quarterly report
    DEF 14A   — proxy statement
    S-1, S-1/A — IPO registration / amendments
    SC 13D/A  — activist amendments
    SC 13G/A  — passive amendments

Output: data_prefetch/sec_edgar/<form_safe>/<TICKER>.parquet
Schema: ticker, cik, form, filing_date, accession_number, primary_doc

Source: SEC EDGAR submissions JSON (https://data.sec.gov/submissions/CIK<10digit>.json)
        — requires CIK lookup which we have from Polygon reference cache.

Run:
    python scripts/prefetch_sec_edgar.py                            # all forms × Master Universe
    python scripts/prefetch_sec_edgar.py --tickers AAPL MSFT       # explicit
    python scripts/prefetch_sec_edgar.py --forms 10-K 10-Q          # form filter
    python scripts/prefetch_sec_edgar.py --limit-tickers 5          # smoke test
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import requests


# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# SEC EDGAR requires a User-Agent identifying the requester (compliance).
SEC_USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "stock-picks-app jeetmehta1991+sec@gmail.com",
)
HEADERS = {"User-Agent": SEC_USER_AGENT, "Accept": "application/json"}

OUT_ROOT = Path("data_prefetch/sec_edgar")

# Form types to fetch + on-disk subdirectory mapping (safe filename)
FORM_DIRS = {
    "4":        "4",
    "8-K":      "8_K",
    "SC 13D":   "SC_13D",
    "SC 13G":   "SC_13G",
    "10-K":     "10_K",       # NEW
    "10-Q":     "10_Q",       # NEW
    "DEF 14A":  "DEF_14A",    # NEW
    "S-1":      "S_1",        # NEW
    "S-1/A":    "S_1_A",      # NEW
    "SC 13D/A": "SC_13D_A",   # NEW
    "SC 13G/A": "SC_13G_A",   # NEW
}


REFERENCE_INDEX = Path("data_prefetch/polygon/reference_index.parquet")
LEGACY_REFERENCE_INDEX = Path(
    "data_prefetch/polygon/legacy_archive_pass53/reference_index.parquet"
)


def load_cik_map() -> dict[str, str]:
    """Build ticker → CIK lookup from Polygon reference cache."""
    for p in [REFERENCE_INDEX, LEGACY_REFERENCE_INDEX]:
        if p.exists():
            df = pd.read_parquet(p)
            if "ticker" in df.columns and "cik" in df.columns:
                # Normalize CIK to 10-digit zero-padded
                cik_map = {}
                for _, row in df.iterrows():
                    cik_raw = str(row["cik"]).strip() if pd.notna(row.get("cik")) else ""
                    if cik_raw and cik_raw.lower() not in ("nan", "none", ""):
                        cik_map[str(row["ticker"]).upper()] = cik_raw.zfill(10)
                if cik_map:
                    return cik_map
    return {}


def fetch_submissions(cik: str, retries: int = 3) -> Optional[dict]:
    """Fetch SEC EDGAR submissions JSON for a given CIK."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(min(2 ** attempt, 10))
                continue
            return None
        except requests.RequestException:
            time.sleep(min(2 ** attempt, 10))
    return None


def parse_filings_for_form(
    submissions: dict,
    form_filter: str,
    ticker: str,
    cik: str,
) -> pd.DataFrame:
    """Extract filings of a specific form type from EDGAR submissions JSON."""
    recent = submissions.get("filings", {}).get("recent", {}) or {}
    forms = recent.get("form", []) or []
    filing_dates = recent.get("filingDate", []) or []
    accession_numbers = recent.get("accessionNumber", []) or []
    primary_docs = recent.get("primaryDocument", []) or []
    rows = []
    for i, form in enumerate(forms):
        if form == form_filter:
            rows.append({
                "ticker":           ticker,
                "cik":              cik,
                "form":             form,
                "filing_date":      filing_dates[i] if i < len(filing_dates) else "",
                "accession_number": accession_numbers[i] if i < len(accession_numbers) else "",
                "primary_doc":      primary_docs[i] if i < len(primary_docs) else "",
            })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    return df


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--tickers", nargs="+", default=None,
                   help="Explicit tickers to fetch")
    p.add_argument("--forms", nargs="+", default=None,
                   help="Form types to fetch (default: all)")
    p.add_argument("--limit-tickers", type=int, default=None,
                   help="Limit total tickers (smoke testing)")
    p.add_argument("--rate-sleep", type=float, default=0.15,
                   help="Sleep between submissions calls (seconds; SEC suggests <10 req/s)")
    p.add_argument("--skip-existing", action="store_true",
                   help="Skip ticker+form pairs that already have a parquet")
    return p.parse_args()


def main():
    args = parse_args()

    # Build form list
    forms = args.forms if args.forms else list(FORM_DIRS.keys())
    invalid = [f for f in forms if f not in FORM_DIRS]
    if invalid:
        print(f"ERROR: unknown forms: {invalid}")
        return 1

    # Build ticker list
    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
    else:
        master = Path(
            "Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv"
        )
        df_uni = pd.read_csv(master, comment="#")
        tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())
    if args.limit_tickers:
        tickers = tickers[: args.limit_tickers]

    cik_map = load_cik_map()
    if not cik_map:
        print("ERROR: no CIK map available. Run prefetch_polygon_reference.py first.")
        return 1

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for f in forms:
        (OUT_ROOT / FORM_DIRS[f]).mkdir(parents=True, exist_ok=True)

    print(f"=== SEC EDGAR Prefetch ===")
    print(f"Tickers: {len(tickers)}  Forms: {len(forms)}  Total fetches: {len(tickers)}")
    print(f"User-Agent: {SEC_USER_AGENT}")
    print(f"CIK map size: {len(cik_map)}")
    print()
    sys.stdout.flush()

    success = 0
    no_cik = 0
    no_data = 0
    fail = 0
    t0 = time.time()

    for i, ticker in enumerate(tickers, 1):
        cik = cik_map.get(ticker)
        if cik is None:
            no_cik += 1
            if i % 50 == 0 or i <= 5:
                print(f"[{i}/{len(tickers)}] {ticker} ... NO CIK")
                sys.stdout.flush()
            continue

        # Skip-existing logic: only skip if ALL requested forms already on disk
        if args.skip_existing:
            all_present = all(
                (OUT_ROOT / FORM_DIRS[f] / f"{ticker}.parquet").exists()
                for f in forms
            )
            if all_present:
                continue

        submissions = fetch_submissions(cik)
        if submissions is None:
            fail += 1
            if i <= 5:
                print(f"[{i}/{len(tickers)}] {ticker} ... FETCH FAILED")
                sys.stdout.flush()
            continue

        wrote_any = False
        for f in forms:
            out_path = OUT_ROOT / FORM_DIRS[f] / f"{ticker}.parquet"
            if args.skip_existing and out_path.exists():
                continue
            df = parse_filings_for_form(submissions, f, ticker, cik)
            if df.empty:
                # Still write an empty parquet so coverage check is not skewed
                if not out_path.exists():
                    pd.DataFrame(
                        columns=["ticker", "cik", "form", "filing_date",
                                 "accession_number", "primary_doc"]
                    ).to_parquet(out_path, index=False)
                continue
            df.to_parquet(out_path, index=False)
            wrote_any = True

        if wrote_any:
            success += 1
        else:
            no_data += 1

        if i % 50 == 0 or i <= 5:
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(tickers) - i) / rate if rate > 0 else 0
            print(f"[{i}/{len(tickers)}] {ticker} ... OK  "
                  f"(rate {rate:.1f} tk/s, ETA {eta/60:.1f} min)")
            sys.stdout.flush()

        time.sleep(args.rate_sleep)

    elapsed = time.time() - t0
    print()
    print(f"=== SEC EDGAR Prefetch Complete ===")
    print(f"  Success (>=1 form found): {success}")
    print(f"  No data (CIK valid but no filings of requested forms): {no_data}")
    print(f"  No CIK in map: {no_cik}")
    print(f"  Fetch failed: {fail}")
    print(f"  Wall time: {elapsed/60:.1f} min")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
