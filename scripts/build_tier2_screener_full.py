"""
scripts/build_tier2_screener_full.py — DEC-103/DEC-494 Pass 53 FULL global SCREENER.

Replaces the curated-seeds approach (build_tier2_screener.py) with a full global scan
of Polygon's ticker database to identify ALL qualifying T2 spinoffs/IPOs in 2010-2026.

Pipeline:
  Step 1 (this script):
    - Paginate /v3/reference/tickers?type=CS&active=true|false (full common stock listing)
    - For each candidate ticker NOT in T1 (T1a + T1c):
        Fetch /v3/reference/tickers/{ticker} for list_date + market_cap + sic_description
        Apply DEC-103 thresholds:
          IPO:     market_cap >$10B + ≥90 days since list_date
          Spinoff: market_cap >$5B + list_date within 12 months of separation
                   (for Pass 53 simplicity, use $5B threshold for any list_date in window)
        Emit B++ row if qualifies.
  Step 2 (separate run): prefetch_polygon_ohlcv_daily.py --tickers <T2 universe>

Output: Backtesting universe/Tier 2 Universe_Spinoffs and Recent IPOs_<actual_start> to May 2026.csv

DEC-103 inclusion criteria:
  Spinoff: child ticker market_cap > $5B within 12 months of separation
  IPO:     issuer market_cap > $10B with ≥90 days trading history
  Window:  2010-01-01 → today (Pass 53 owner-approved)
  Exclude: T1 members (T1a + T1c)

Estimated wall time: ~10-25 minutes for ~10k-15k common stock tickers (Polygon Stocks Starter unlimited rate; 0.05s sleep between calls).

Usage:
  python scripts/build_tier2_screener_full.py            # dry run
  python scripts/build_tier2_screener_full.py --write    # write CSV
  python scripts/build_tier2_screener_full.py --max-candidates 500  # limit for testing
"""
import os
import sys
import time
import argparse
import requests
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POLYGON_KEY = os.environ.get("POLYGON_API_KEY", "")
if not POLYGON_KEY:
    print("ERROR: POLYGON_API_KEY not set in env")
    sys.exit(1)

BASE_URL = "https://api.polygon.io"
REPO = Path(__file__).resolve().parent.parent
T2_CSV = REPO / "Backtesting universe" / "Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv"
T1A_CSV = REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
T1C_CSV = REPO / "Backtesting universe" / "Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv"

WINDOW_START = date(2010, 1, 1)
WINDOW_END = date.today()
MIN_SPINOFF_CAP_B = 5.0
MIN_IPO_CAP_B = 10.0
MIN_DAYS = 90

TIMEOUT = 30


def polygon_format(t: str) -> str:
    if "-" in t:
        prefix, _, suffix = t.rpartition("-")
        if len(suffix) == 1 and suffix.isalpha():
            return f"{prefix}.{suffix}"
    return t


def load_t1_tickers() -> set:
    t1 = set()
    for path in [T1A_CSV, T1C_CSV]:
        if path.exists():
            df = pd.read_csv(path, comment="#")
            t1.update(df["Symbol"].dropna().str.strip().str.upper().tolist())
    return t1


def fetch_paginated_tickers(active_flag: str) -> list[dict]:
    """Paginate /v3/reference/tickers for active=true or active=false, type=CS."""
    url = f"{BASE_URL}/v3/reference/tickers"
    params = {
        "apiKey": POLYGON_KEY,
        "type": "CS",
        "active": active_flag,
        "limit": 1000,
        "order": "asc",
        "sort": "ticker",
    }
    all_results = []
    page = 0
    while True:
        page += 1
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException as e:
            print(f"    Page {page} failed: {e}")
            break
        if r.status_code != 200:
            print(f"    Page {page} HTTP {r.status_code}: {r.text[:200]}")
            break
        data = r.json()
        results = data.get("results", []) or []
        all_results.extend(results)
        next_url = data.get("next_url")
        if not next_url:
            break
        url = next_url
        params = {"apiKey": POLYGON_KEY}
        if page % 5 == 0:
            print(f"    Page {page}: cumulative {len(all_results)} listings (active={active_flag})")
        time.sleep(0.05)
    return all_results


def get_ticker_metadata(ticker: str) -> dict | None:
    api_t = polygon_format(ticker)
    url = f"{BASE_URL}/v3/reference/tickers/{api_t}"
    try:
        r = requests.get(url, params={"apiKey": POLYGON_KEY}, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        return r.json().get("results", {})
    except Exception:
        return None


def sic_to_gics(sic_desc: str) -> str:
    if not sic_desc:
        return ""
    s = sic_desc.lower()
    if any(x in s for x in ["petroleum", "oil & gas", "mining", "natural gas"]):
        return "Energy"
    if any(x in s for x in ["bank", "insurance", "financial", "investment", "securities", "broker"]):
        return "Financials"
    if any(x in s for x in ["computer", "software", "semiconductor", "electronic", "data proc"]):
        return "Information Technology"
    if any(x in s for x in ["pharmaceutical", "biolog", "medical", "health", "hospital", "laboratory analytical"]):
        return "Health Care"
    if any(x in s for x in ["retail", "restaurant", "apparel", "automobile", "hotel", "leisure", "leather", "motor vehicle parts", "motorcycles", "men's", "carpets"]):
        return "Consumer Discretionary"
    if any(x in s for x in ["food", "beverage", "tobacco", "household", "personal care", "perfumes", "cosmetics"]):
        return "Consumer Staples"
    if any(x in s for x in ["real estate", "reit"]):
        return "Real Estate"
    if any(x in s for x in ["telecommunications", "broadcast", "cable", "media", "publishing", "telephone communications"]):
        return "Communication Services"
    if any(x in s for x in ["electric", "utility", "water supply"]):
        return "Utilities"
    if any(x in s for x in ["chemical", "metals", "paper", "construction material"]):
        return "Materials"
    if any(x in s for x in ["industrial", "transportation", "manufactur", "construction", "machinery", "aerospace", "pumps", "business services"]):
        return "Industrials"
    return ""


def main():
    ap = argparse.ArgumentParser(description="Tier 2 FULL SCREENER (DEC-103/494 Pass 53)")
    ap.add_argument("--write", action="store_true", help="Write CSV (default dry run)")
    ap.add_argument("--max-candidates", type=int, default=None,
                    help="Limit candidate count for testing (default: full scan)")
    args = ap.parse_args()

    print("=" * 70)
    print("Tier 2 FULL Global SCREENER — DEC-103/494 Pass 53")
    print("=" * 70)
    print(f"Window: {WINDOW_START} → {WINDOW_END}")
    print(f"Filters: spinoff cap >${MIN_SPINOFF_CAP_B}B / IPO cap >${MIN_IPO_CAP_B}B + ≥{MIN_DAYS}d history")

    t1_set = load_t1_tickers()
    print(f"T1 (T1a + T1c) ticker set: {len(t1_set)} (excluded from T2)")

    print(f"\n[1/2] Paginating /v3/reference/tickers (active=true + active=false)...")
    active_listings = fetch_paginated_tickers("true")
    print(f"  Active CS listings: {len(active_listings)}")
    delisted_listings = fetch_paginated_tickers("false")
    print(f"  Delisted CS listings: {len(delisted_listings)}")
    all_listings = active_listings + delisted_listings
    # Dedupe by ticker
    seen = set()
    unique_listings = []
    for r in all_listings:
        t = r.get("ticker", "").strip().upper()
        if t and t not in seen:
            seen.add(t)
            unique_listings.append(r)
    print(f"  Total unique CS listings: {len(unique_listings)}")

    # Filter to non-T1 candidates
    candidates = [r for r in unique_listings if r.get("ticker", "").strip().upper() not in t1_set]
    print(f"  Non-T1 candidates: {len(candidates)}")
    if args.max_candidates:
        candidates = candidates[:args.max_candidates]
        print(f"  Limited to first {len(candidates)} for testing")

    print(f"\n[2/2] Per-ticker detail lookup (list_date + market_cap)...")
    qualifying = []
    earliest_list_date = None
    skipped_no_meta = 0
    skipped_no_list_date = 0
    skipped_pre_window = 0
    skipped_history = 0
    skipped_cap = 0
    checked = 0
    start_ts = time.time()

    for r in candidates:
        ticker = r.get("ticker", "").strip().upper()
        meta = get_ticker_metadata(ticker)
        checked += 1
        if checked % 100 == 0:
            elapsed = time.time() - start_ts
            rate = checked / elapsed if elapsed > 0 else 0
            eta = (len(candidates) - checked) / rate if rate > 0 else 0
            print(f"    [{checked}/{len(candidates)}] qualifying so far: {len(qualifying)} (rate {rate:.1f} t/s, ETA {eta/60:.1f}min)")
        time.sleep(0.05)
        if not meta:
            skipped_no_meta += 1
            continue
        list_date_str = meta.get("list_date", "")
        if not list_date_str:
            skipped_no_list_date += 1
            continue
        try:
            list_d = datetime.strptime(list_date_str, "%Y-%m-%d").date()
        except Exception:
            skipped_no_list_date += 1
            continue
        if list_d < WINDOW_START:
            skipped_pre_window += 1
            continue
        if (WINDOW_END - list_d).days < MIN_DAYS:
            skipped_history += 1
            continue
        cap = meta.get("market_cap")
        if not cap:
            skipped_cap += 1
            continue
        cap_b = cap / 1e9
        # Apply $5B threshold (the lower of spinoff/IPO; recent listings rarely classifiable
        # as spinoff vs IPO without per-event metadata)
        if cap_b < MIN_SPINOFF_CAP_B:
            skipped_cap += 1
            continue
        # Tag spinoff vs IPO heuristically (cap >= $10B = IPO, $5-10B = spinoff/recent-IPO)
        reason = f"recent_listing_{list_d.year}" if cap_b >= MIN_IPO_CAP_B else f"spinoff_or_ipo_{list_d.year}"
        if earliest_list_date is None or list_d < earliest_list_date:
            earliest_list_date = list_d
        qualifying.append({
            "Symbol": ticker,
            "Company": meta.get("name", ""),
            "Sector": sic_to_gics(meta.get("sic_description") or ""),
            "added_date": list_d.isoformat(),
            "removed_date": "",
            "MarketCapB": round(cap_b, 2),
            "Tier2Reason": reason,
        })

    elapsed = time.time() - start_ts
    print(f"\n{'=' * 70}")
    print(f"T2 FULL SCREENER RESULT")
    print(f"{'=' * 70}")
    print(f"Wall time: {elapsed/60:.1f} min")
    print(f"Candidates checked: {checked}")
    print(f"  Skipped no metadata (404): {skipped_no_meta}")
    print(f"  Skipped no list_date: {skipped_no_list_date}")
    print(f"  Skipped pre-2010 listing: {skipped_pre_window}")
    print(f"  Skipped insufficient history (<90d): {skipped_history}")
    print(f"  Skipped cap < $5B: {skipped_cap}")
    print(f"\nQualifying T2 tickers: {len(qualifying)}")
    if earliest_list_date:
        print(f"Earliest list_date in qualifying: {earliest_list_date}")

    if not qualifying:
        print("No qualifying T2 tickers identified.")
        return 0

    df = pd.DataFrame(qualifying).drop_duplicates(subset=["Symbol"]).sort_values(["MarketCapB"], ascending=False).reset_index(drop=True)

    print(f"\nTop 30 by MarketCapB:")
    print(df[["Symbol", "Company", "Sector", "added_date", "MarketCapB", "Tier2Reason"]].head(30).to_string(index=False))

    if args.write:
        cols = ["Symbol", "Company", "Sector", "added_date", "removed_date", "MarketCapB", "Tier2Reason"]
        df = df[[c for c in cols if c in df.columns]]
        # Re-sort by Symbol for canonical CSV
        df = df.sort_values("Symbol").reset_index(drop=True)
        # Update filename if earliest list_date changed (per Q4 owner directive)
        new_start_str = earliest_list_date.strftime("%b %Y") if earliest_list_date else "Sep 2014"
        new_filename = f"Tier 2 Universe_Spinoffs and Recent IPOs_{new_start_str} to May 2026.csv"
        new_path = REPO / "Backtesting universe" / new_filename
        header_lines = [
            f"# {new_filename.replace('.csv','')} - DEC-103/494 Pass 53 FULL SCREENER output",
            f"# Built: {date.today().isoformat()} via Polygon /v3/reference/tickers global pagination + per-ticker detail",
            f"# Approach: full global scan ({checked} non-T1 candidates checked); filter by DEC-103 thresholds (cap >=$5B for any recent listing; >=$10B tagged as IPO).",
            "# T1 (T1a + T1c) excluded.",
            f"# Window: {WINDOW_START} -> {WINDOW_END}",
            "# SCHEMA: Symbol, Company, Sector (GICS), added_date (Polygon list_date), removed_date (NULL = currently active), MarketCapB, Tier2Reason",
            "# PIT FILTER: (added_date IS NULL OR added_date <= as_of) AND (removed_date IS NULL OR removed_date > as_of)",
        ]
        # If filename changed, write to new and remove old
        if new_filename != T2_CSV.name:
            print(f"\n[FILENAME CHANGE] earliest list_date {earliest_list_date} → renaming to: {new_filename}")
            with open(new_path, "w", encoding="utf-8", newline="") as f:
                for line in header_lines:
                    f.write(line + "\n")
                df.to_csv(f, index=False)
            print(f"\nWrote {len(df)} rows to {new_path}")
            print(f"NOTE: Old file {T2_CSV.name} should be git rm-ed and the new file git add-ed.")
        else:
            with open(T2_CSV, "w", encoding="utf-8", newline="") as f:
                for line in header_lines:
                    f.write(line + "\n")
                df.to_csv(f, index=False)
            print(f"\nWrote {len(df)} rows to {T2_CSV}")
    else:
        print(f"\nDry run — pass --write to save to {T2_CSV}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
