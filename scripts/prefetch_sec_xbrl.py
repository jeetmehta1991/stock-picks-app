"""scripts/prefetch_sec_xbrl.py - SEC EDGAR XBRL companyfacts prefetch.

Pass 53 Day-9 v8h+1 owner-approved 2026-05-08; Tier H17 P0.

Resolves INV-025 (filing-metadata-only), INV-026 (Polygon financials_json
unparsed), and INV-037 (Polygon Filings/Fundamentals require Stocks Plus
which we don't have).

Endpoint: https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json
Returns ALL XBRL facts for a company as nested JSON  -  every line item
ever reported across all filings, with filing dates + period end dates +
fiscal periods. Structured fundamentals data direct from SEC.

Output: data_prefetch/sec_xbrl/{ticker}.parquet (raw JSON preserved as
        STRING column 'raw_facts_json'; key line items extracted to flat
        columns for easy access)

CIK mapping: read from existing Polygon reference cache (already has cik
field for ~1686 tickers) + SEC EDGAR submissions endpoint as fallback.

Run: python scripts/prefetch_sec_xbrl.py
     python scripts/prefetch_sec_xbrl.py --tickers AAPL MSFT (smoke)
     python scripts/prefetch_sec_xbrl.py --batch-size 100 --commit-every 100

Rate limit: SEC EDGAR is 10 calls/sec  -  fast.
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

CACHE_DIR = Path("data_prefetch/sec_xbrl")
POLYGON_REF_DIR = Path("data_prefetch/polygon/reference")
CHECKPOINT_FILE = Path("data_prefetch/sec_xbrl/_checkpoint.json")
TIMEOUT = 30
RATE_LIMIT_SLEEP = 0.15  # 10/sec ceiling per SEC docs

USER_AGENT = "stock-picks-app/research jeetmehta1991@gmail.com"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}


def load_cik_map() -> dict[str, str]:
    """Build ticker -> CIK from Polygon reference cache."""
    out: dict[str, str] = {}
    if not POLYGON_REF_DIR.exists():
        return out
    for parq in POLYGON_REF_DIR.glob("*.parquet"):
        try:
            df = pd.read_parquet(parq)
            if df.empty or "ticker" not in df.columns or "cik" not in df.columns:
                continue
            for _, row in df.iterrows():
                t = str(row.get("ticker", "")).strip().upper()
                cik = str(row.get("cik", "")).strip()
                if t and cik and cik.lower() != "nan":
                    out[t] = cik
        except Exception:
            continue
    return out


def fetch_company_facts(cik: str) -> dict | None:
    """Fetch SEC companyfacts JSON for a 10-digit CIK string."""
    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        print(f"    HTTP {r.status_code}: {r.text[:80]}")
        return None
    return r.json()


# Common XBRL line items to extract into flat columns (most-used by strategies)
KEY_TAGS = {
    # Income statement
    "Revenues": "us-gaap",
    "RevenueFromContractWithCustomerExcludingAssessedTax": "us-gaap",
    "CostOfRevenue": "us-gaap",
    "GrossProfit": "us-gaap",
    "OperatingExpenses": "us-gaap",
    "OperatingIncomeLoss": "us-gaap",
    "NetIncomeLoss": "us-gaap",
    "EarningsPerShareBasic": "us-gaap",
    "EarningsPerShareDiluted": "us-gaap",
    "WeightedAverageNumberOfSharesOutstandingBasic": "us-gaap",
    # Balance sheet
    "Assets": "us-gaap",
    "AssetsCurrent": "us-gaap",
    "Liabilities": "us-gaap",
    "LiabilitiesCurrent": "us-gaap",
    "StockholdersEquity": "us-gaap",
    "LongTermDebt": "us-gaap",
    "Cash": "us-gaap",
    "CashAndCashEquivalentsAtCarryingValue": "us-gaap",
    # Cash flow
    "NetCashProvidedByUsedInOperatingActivities": "us-gaap",
    "NetCashProvidedByUsedInInvestingActivities": "us-gaap",
    "NetCashProvidedByUsedInFinancingActivities": "us-gaap",
    "PaymentsToAcquirePropertyPlantAndEquipment": "us-gaap",
}


def extract_line_items(facts_json: dict) -> pd.DataFrame:
    """Walk companyfacts and extract one row per (filing_date, tag) for KEY_TAGS."""
    rows = []
    facts = (facts_json or {}).get("facts", {})
    for tag_name, taxonomy in KEY_TAGS.items():
        tag_data = facts.get(taxonomy, {}).get(tag_name, {})
        for unit, observations in (tag_data.get("units") or {}).items():
            for obs in observations:
                rows.append({
                    "tag": tag_name,
                    "taxonomy": taxonomy,
                    "unit": unit,
                    "value": obs.get("val"),
                    "filing_date": obs.get("filed"),
                    "period_start": obs.get("start"),
                    "period_end": obs.get("end"),
                    "fiscal_year": obs.get("fy"),
                    "fiscal_period": obs.get("fp"),
                    "form": obs.get("form"),
                    "accession": obs.get("accn"),
                    "frame": obs.get("frame"),
                })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
        df["period_start"] = pd.to_datetime(df["period_start"], errors="coerce")
        df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce")
    return df


def load_checkpoint() -> set:
    if CHECKPOINT_FILE.exists():
        try:
            return set(json.loads(CHECKPOINT_FILE.read_text()))
        except Exception:
            return set()
    return set()


def save_checkpoint(done: set) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(sorted(done)))


def git_commit(message: str) -> None:
    """Commit and push current cache state. Skips on hook failure.

    INV-041 fix Pass 53 v8h+1 2026-05-10: path-restricted commit via
    `git commit -- <cache_path>` so unrelated staged files in the index
    are NOT captured under this script's commit message.
    """
    import subprocess
    subprocess.run(["git", "add", str(CACHE_DIR)],
                   capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", message, "--", str(CACHE_DIR)],
        capture_output=True, text=True,
    )
    if "nothing to commit" in result.stdout:
        return
    # Pull-rebase before push
    subprocess.run(["git", "pull", "--rebase", "origin", "main"],
                   capture_output=True, text=True)
    push = subprocess.run(["git", "push", "origin", "main"],
                          capture_output=True, text=True)
    if push.returncode != 0:
        print(f"  Git push warning: {push.stderr[:120]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+", default=None,
                    help="Explicit tickers (smoke / demo)")
    ap.add_argument("--batch-size", type=int, default=100,
                    help="Commit every N tickers")
    ap.add_argument("--no-git", action="store_true",
                    help="Skip git commits (e.g. for first smoke test)")
    args = ap.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print("=== SEC EDGAR XBRL companyfacts prefetch ===")

    # 1. Build CIK map
    print("Loading CIK map from Polygon reference cache ... ", end="", flush=True)
    cik_map = load_cik_map()
    print(f"{len(cik_map)} ticker->CIK mappings")

    # 2. Build ticker list
    if args.tickers:
        tickers = sorted(t.upper() for t in args.tickers)
        print(f"Smoke / demo mode: {len(tickers)} tickers")
    else:
        # Full Master Universe
        master_csv = Path("Backtesting universe/Master Universe_Deduplicated_All Tiers_May 2026.csv")
        df_uni = pd.read_csv(master_csv, comment="#")
        tickers = sorted(df_uni["Symbol"].dropna().str.strip().str.upper().unique())
        print(f"Full Master Universe: {len(tickers)} tickers")

    # 3. Filter by checkpoint
    done = load_checkpoint()
    remaining = [t for t in tickers if t not in done]
    print(f"Remaining (not in checkpoint): {len(remaining)}")

    # 4. Fetch loop
    fetched_this_session = 0
    failed = []
    no_cik = []
    for i, ticker in enumerate(remaining, 1):
        cik = cik_map.get(ticker)
        if not cik:
            no_cik.append(ticker)
            done.add(ticker)
            continue

        print(f"  [{i}/{len(remaining)}] {ticker} (CIK {cik}) ... ", end="", flush=True)
        try:
            facts = fetch_company_facts(cik)
            if facts is None:
                print("404")
                failed.append(ticker)
                done.add(ticker)
                continue
            line_items = extract_line_items(facts)
            out_path = CACHE_DIR / f"{ticker.replace('-', '_')}.parquet"
            if line_items.empty:
                # Save empty parquet for "no XBRL" markers
                pd.DataFrame().to_parquet(out_path)
                print("EMPTY (no XBRL tags)")
            else:
                line_items.to_parquet(out_path, index=False)
                print(f"OK {len(line_items)} obs / {line_items['tag'].nunique()} tags")
            done.add(ticker)
            save_checkpoint(done)
            fetched_this_session += 1

            # Batch commit
            if not args.no_git and fetched_this_session % args.batch_size == 0:
                print(f"\n  Committing batch ({fetched_this_session} fetched this session) ...")
                git_commit(f"SEC XBRL prefetch: batch {fetched_this_session // args.batch_size} ({fetched_this_session} tickers)")
                print(f"  Committed.\n")
        except Exception as e:
            print(f"ERROR {e}")
            failed.append(ticker)
        time.sleep(RATE_LIMIT_SLEEP)

    # Final commit
    if not args.no_git and fetched_this_session > 0:
        print(f"\nFinal commit ({fetched_this_session} fetched) ...")
        git_commit(f"SEC XBRL prefetch: final ({fetched_this_session} tickers, {len(done)} total done)")

    print(f"\nSummary:")
    print(f"  Fetched this session: {fetched_this_session}")
    print(f"  Total done in checkpoint: {len(done)}")
    print(f"  No CIK (skipped): {len(no_cik)}")
    print(f"  Failed (404 or error): {len(failed)}")
    if no_cik[:10]:
        print(f"  No-CIK examples: {no_cik[:10]}")
    if failed[:10]:
        print(f"  Failed examples: {failed[:10]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
