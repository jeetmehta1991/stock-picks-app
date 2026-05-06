"""
scripts/build_tier2_screener.py — DEC-103/DEC-494 Pass 53 SCREENER-FIRST architecture.

PASS 53 IMPLEMENTATION NOTE: Polygon's /v3/reference/tickers listing endpoint does
NOT populate list_date in the listing response (verified 2026-05-05 — list_date
is blank in listing rows; only populated in /v3/reference/tickers/{ticker} detail).
list_date.gte/.lte filters on listing endpoint are silently ignored.

Pragmatic Pass 53 T2 build:
  Step 1 (curated seeds): validate known spinoff + recent-IPO tickers (TIER2_SEEDS
    from refresh_extended_universe.py) via /v3/reference/tickers/{ticker} for
    list_date + market_cap.
  Step 2 (cache discovery): scan our cached OHLCV files for tickers whose FIRST
    bar is later than 2021-05-15 (Polygon Stocks Starter window start + buffer);
    those are de facto recent listings within our backtest window. Cross-reference
    with /v3/reference/tickers/{ticker} for cap + name + sector.
  Step 3 (filter): apply DEC-103 thresholds (spinoff >$5B / IPO >$10B + ≥90d).
  Output: B++ rows to Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv

Future Sprint 1+: Full global SCREENER via paginated /v3/reference/tickers with
per-ticker detail lookup for list_date. Wall time ~30-60 min for ~10k tickers.
This is a follow-up enhancement; Pass 53 minimum is the curated+cache-discovery
hybrid above.

DEC-103 inclusion criteria:
  Spinoff: child ticker market_cap > $5B within 12 months of separation.
  IPO:     issuer market_cap > $10B with ≥90 days trading history.

Output: Backtesting universe/Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv (B++ schema:
  Symbol, Company, Sector, added_date, removed_date, MarketCapB, Tier2Reason)

Usage:
  python scripts/build_tier2_screener.py            # dry run
  python scripts/build_tier2_screener.py --write    # write CSV
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
OHLCV_DIR = REPO / "backtest" / "data" / "cache" / "polygon" / "ohlcv_daily"

WINDOW_START = date(2010, 1, 1)
WINDOW_END = date.today()
MIN_SPINOFF_CAP_B = 5.0
MIN_IPO_CAP_B = 10.0
MIN_IPO_DAYS = 90

# Polygon Stocks Starter cache window cutoff — first bar in OHLCV cache should
# be near this date for a ticker that existed throughout the 5y window.
# Tickers with first_bar_date significantly LATER than this are recent listings.
POLYGON_WINDOW_START = date(2021, 5, 15)  # 2021-05-06 was actual; +9 buffer
RECENT_LISTING_THRESHOLD = date(2021, 6, 1)  # de facto IPO/spinoff if first bar after this

# Curated seeds from refresh_extended_universe.py — known spinoffs + IPOs
TIER2_SEEDS = {
    "SNDK": "spinoff_from_WDC_2025",
    "GEV":  "spinoff_from_GE_2024",
    "SOLV": "spinoff_from_Honeywell_2024",
    "KVUE": "spinoff_from_JNJ_2023",
    "VLTO": "spinoff_from_Danaher_2023",
    "OTIS": "spinoff_from_UTX_2020",
    "CARR": "spinoff_from_UTX_2020",
    "VNT":  "spinoff_from_Fortive_2020",
    "AMTM": "spinoff_from_Leidos_2024",
    "VST":  "high_momentum_energy",
    "SMCI": "ai_infrastructure",
    "PLTR": "tech_listing_2020",
    "DASH": "tech_listing_2020",
    "ABNB": "tech_listing_2020",
    "CRWD": "tech_listing_2019",
    "SNOW": "tech_listing_2020",
    "DDOG": "tech_listing_2019",
    "U":    "tech_listing_2020",
    "NET":  "tech_listing_2019",
    "TEAM": "tech_listing_2015",
    "OKTA": "tech_listing_2017",
    "ZS":   "tech_listing_2018",
    "TWLO": "tech_listing_2016",
    "DOCU": "tech_listing_2018",
    "PINS": "tech_listing_2019",
    "LYFT": "tech_listing_2019",
    "UBER": "tech_listing_2019",
    "ZM":   "tech_listing_2019",
    "RIVN": "tech_listing_2021",
    "LCID": "tech_listing_2021",
    "ARM":  "tech_listing_2023",
    "REDDIT": "tech_listing_2024",
    "RDDT": "tech_listing_2024",
    "TOST": "tech_listing_2021",
    "AFRM": "tech_listing_2021",
    "COIN": "tech_listing_2021",
    "CVNA": "tech_listing_2017",
    "MRNA": "biotech_listing_2018",
    "BNTX": "biotech_listing_2019",
    "HOOD": "tech_listing_2021",
    "BABA": "international_listing_2014",
    "JD":   "international_listing_2014",
    "PDD":  "international_listing_2018",
    "MELI": "international_listing_2007",
    "SHOP": "international_listing_2015",
}


def polygon_format(t: str) -> str:
    if "-" in t:
        prefix, _, suffix = t.rpartition("-")
        if len(suffix) == 1 and suffix.isalpha():
            return f"{prefix}.{suffix}"
    return t


def get_ticker_metadata(ticker: str) -> dict | None:
    api_t = polygon_format(ticker)
    url = f"{BASE_URL}/v3/reference/tickers/{api_t}"
    try:
        r = requests.get(url, params={"apiKey": POLYGON_KEY}, timeout=30)
        if r.status_code != 200:
            return None
        return r.json().get("results", {})
    except Exception:
        return None


def load_t1_tickers() -> set:
    t1 = set()
    for path in [T1A_CSV, T1C_CSV]:
        if path.exists():
            df = pd.read_csv(path, comment="#")
            t1.update(df["Symbol"].dropna().str.strip().str.upper().tolist())
    return t1


def discover_recent_listings_from_cache(t1_set: set) -> list[str]:
    """Scan cached OHLCV files; tickers with first_bar > 2021-06-01 are de facto recent listings.
    Excludes T1 tickers."""
    recent = []
    if not OHLCV_DIR.exists():
        return recent
    for f in OHLCV_DIR.glob("*.parquet"):
        ticker = f.stem.upper()
        if ticker in t1_set:
            continue
        try:
            df = pd.read_parquet(f)
            if df.empty:
                continue
            first_date = pd.to_datetime(df["date"].min()).date()
            if first_date >= RECENT_LISTING_THRESHOLD:
                recent.append((ticker, first_date))
        except Exception:
            continue
    return recent


def sic_to_gics(sic_desc: str) -> str:
    if not sic_desc:
        return ""
    s = sic_desc.lower()
    if any(x in s for x in ["petroleum", "oil & gas", "mining", "natural gas"]):
        return "Energy"
    if any(x in s for x in ["bank", "insurance", "financial", "investment", "securities"]):
        return "Financials"
    if any(x in s for x in ["computer", "software", "semiconductor", "electronic", "data proc"]):
        return "Information Technology"
    if any(x in s for x in ["pharmaceutical", "biolog", "medical", "health", "hospital"]):
        return "Health Care"
    if any(x in s for x in ["retail", "restaurant", "apparel", "automobile", "hotel", "leisure"]):
        return "Consumer Discretionary"
    if any(x in s for x in ["food", "beverage", "tobacco", "household", "personal care"]):
        return "Consumer Staples"
    if any(x in s for x in ["real estate", "reit"]):
        return "Real Estate"
    if any(x in s for x in ["telecommunications", "broadcast", "cable", "media", "publishing"]):
        return "Communication Services"
    if any(x in s for x in ["electric", "utility", "water supply"]):
        return "Utilities"
    if any(x in s for x in ["chemical", "metals", "paper", "construction material"]):
        return "Materials"
    if any(x in s for x in ["industrial", "transportation", "manufactur", "construction", "machinery", "aerospace"]):
        return "Industrials"
    return ""


def validate_candidate(ticker: str, reason_hint: str = "", t1_set: set | None = None) -> dict | None:
    """Validate a single candidate via Polygon detail endpoint. Returns B++ row dict or None."""
    if t1_set and ticker in t1_set:
        return None
    meta = get_ticker_metadata(ticker)
    if not meta:
        return None
    cap = meta.get("market_cap")
    if not cap:
        return None
    cap_b = cap / 1e9
    list_date_str = meta.get("list_date", "")
    try:
        list_d = datetime.strptime(list_date_str, "%Y-%m-%d").date() if list_date_str else None
    except Exception:
        list_d = None

    # Apply DEC-103 thresholds — spinoff >$5B / IPO >$10B; for unclassified, use $5B floor
    is_spinoff = "spinoff" in reason_hint.lower()
    threshold = MIN_SPINOFF_CAP_B if is_spinoff else MIN_IPO_CAP_B
    if cap_b < threshold:
        return None

    # ≥90 days history check via list_date
    if list_d:
        days_since = (WINDOW_END - list_d).days
        if days_since < MIN_IPO_DAYS:
            return None

    return {
        "Symbol": ticker,
        "Company": meta.get("name", ""),
        "Sector": sic_to_gics(meta.get("sic_description") or ""),
        "added_date": list_d.isoformat() if list_d else "",
        "removed_date": "",
        "MarketCapB": round(cap_b, 2),
        "Tier2Reason": reason_hint or f"list_date_{list_d.year if list_d else 'unknown'}",
    }


def main():
    ap = argparse.ArgumentParser(description="Tier 2 SCREENER (DEC-103/494 Pass 53)")
    ap.add_argument("--write", action="store_true", help="Write CSV (default dry run)")
    args = ap.parse_args()

    print("=" * 60)
    print("Tier 2 SCREENER — DEC-103/494 Pass 53 (curated + cache-discovery hybrid)")
    print("=" * 60)
    print(f"Window: {WINDOW_START} → {WINDOW_END}")
    print(f"Filters: spinoff cap >${MIN_SPINOFF_CAP_B}B / IPO cap >${MIN_IPO_CAP_B}B + ≥{MIN_IPO_DAYS}d history")

    t1_set = load_t1_tickers()
    print(f"\nT1 (T1a + T1c) ticker set: {len(t1_set)} (excluded from T2)")

    # Step 1: validate curated seeds
    print(f"\n[1/2] Validating {len(TIER2_SEEDS)} curated seed tickers...")
    seed_rows = []
    for i, (ticker, reason) in enumerate(sorted(TIER2_SEEDS.items()), 1):
        row = validate_candidate(ticker, reason, t1_set)
        if row:
            seed_rows.append(row)
            print(f"  [{i}/{len(TIER2_SEEDS)}] {ticker} ✓ ${row['MarketCapB']:.1f}B  {row['Sector']}  ({reason})")
        else:
            print(f"  [{i}/{len(TIER2_SEEDS)}] {ticker} ✗ (excluded — T1, fails cap, or no metadata)")
        time.sleep(0.05)

    # Step 2: discover recent listings from OHLCV cache
    print(f"\n[2/2] Discovering recent listings from OHLCV cache (first_bar >= {RECENT_LISTING_THRESHOLD})...")
    recent = discover_recent_listings_from_cache(t1_set)
    print(f"  Found {len(recent)} non-T1 tickers with first_bar >= threshold")

    seen_seeds = {r["Symbol"] for r in seed_rows}
    discovery_rows = []
    for ticker, first_d in recent:
        if ticker in seen_seeds:
            continue
        row = validate_candidate(ticker, f"cache_discovery_{first_d.year}", t1_set)
        if row:
            discovery_rows.append(row)
            print(f"  ✓ {ticker} first_bar={first_d}  ${row['MarketCapB']:.1f}B  {row['Sector']}  ({row['Tier2Reason']})")
        time.sleep(0.05)

    all_rows = seed_rows + discovery_rows
    if not all_rows:
        print("\nNo qualifying T2 tickers identified.")
        return 0

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["Symbol"], keep="first")
    df = df.sort_values(["Tier2Reason", "Symbol"]).reset_index(drop=True)

    print(f"\n{'=' * 60}")
    print(f"T2 SCREENER RESULT: {len(df)} qualifying tickers ({len(seed_rows)} seeds + {len(discovery_rows)} discovery)")
    print(f"{'=' * 60}")
    print(df[["Symbol", "Company", "Sector", "added_date", "MarketCapB", "Tier2Reason"]].to_string(index=False))

    if args.write:
        cols = ["Symbol", "Company", "Sector", "added_date", "removed_date", "MarketCapB", "Tier2Reason"]
        df = df[[c for c in cols if c in df.columns]]
        header_lines = [
            "# T2 Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv — DEC-103/494 Pass 53 SCREENER-FIRST output",
            f"# Built: {date.today().isoformat()} via Polygon /v3/reference/tickers/{{ticker}} per-ticker detail + OHLCV cache discovery",
            "# Approach: curated TIER2_SEEDS validated against Polygon detail endpoint + cache-discovery (tickers whose first OHLCV bar >= 2021-06-01 are de facto recent listings within Polygon Stocks Starter 5y window).",
            f"# DEC-103 thresholds: spinoff cap >${MIN_SPINOFF_CAP_B}B / IPO cap >${MIN_IPO_CAP_B}B + ≥{MIN_IPO_DAYS}d history",
            "# T1 (T1a + T1c) excluded.",
            "# SCHEMA: Symbol, Company, Sector (GICS), added_date (Polygon list_date), removed_date (NULL = currently active), MarketCapB, Tier2Reason",
            "# PIT FILTER: (added_date IS NULL OR added_date <= as_of) AND (removed_date IS NULL OR removed_date > as_of)",
            "# FOLLOW-UP (Sprint 1+): full global SCREENER via paginated /v3/reference/tickers + per-ticker list_date lookup (~30-60 min wall time for ~10k tickers).",
        ]
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
