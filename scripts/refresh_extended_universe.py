"""
scripts/refresh_extended_universe.py
Build and refresh Tier 2 extended universe — spinoffs + recent IPOs above
$5B/$10B market cap respectively (DEC-103).

TIER 2 DESIGN (Pass 53 DEC-494 corrected — NDX-non-S&P removed; now T1c per DEC-483):
- Spinoffs: any company above $5B market cap within 12 months of spinoff (DEC-103)
- Recent IPOs: above $10B market cap with 90+ days of trading history (DEC-103)
- Update frequency: MONTHLY for live trading (Stage 3+)
                    NOT needed for backtesting

NOTE Pass 53 SCREENER-FIRST architecture (DEC-103/DEC-494/DEC-380):
This script's pre-Pass-53 approach (yfinance-based seed list + market cap validation)
is preserved as a stop-gap for laptop-local monthly refresh. Sprint 1 follow-up
will replace this with Polygon `/v3/reference/dividends|splits|tickers` corp-actions
feed as primary screener (yfinance lags new listings — L89 SNDK 9-month example).

MONTHLY RATIONALE (vs semi-annual):
- Spinoffs are added to Tier 2 immediately after listing (no waiting)
- But the monthly refresh catches any that were missed, validates liquidity,
  and removes names that have since been added to Tier 1 (S&P 500)
- Monthly aligns with the Tier 3 momentum watchlist refresh cadence
- Semi-annual is too infrequent — SNDK would have been missed for 3-6 months
  even with a semi-annual refresh vs only 0-4 weeks with monthly

USAGE:
    python scripts/refresh_extended_universe.py           # review only
    python scripts/refresh_extended_universe.py --write   # write CSV
    python scripts/refresh_extended_universe.py --add SNDK GEV --write  # immediate spinoff add

RUN ON: laptop monthly. Immediate run after any major spinoff announcement.
OUTPUT: Backtesting universe/extended_universe.csv (B++ schema: Symbol, Company, Sector, added_date, removed_date, MarketCapB, Tier2Reason)
"""
import argparse
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# ── Config ──────────────────────────────────────────────────────────────────
# Pass 53 folder move: universe CSVs live in top-level "Backtesting universe/"
CSV_PATH   = Path(__file__).parent.parent / "Backtesting universe" / "extended_universe.csv"
SP500_CSV  = Path(__file__).parent.parent / "Backtesting universe" / "sp500_tickers.csv"
MIN_MKTCAP_SPINOFF_B = 5.0   # spinoffs above $5B (DEC-103)
MIN_MKTCAP_IPO_B     = 10.0  # recent IPOs above $10B (DEC-103)
MIN_PRICE   = 5.0
MIN_AVG_VOL = 200_000

# Seed list — Tier 2 candidates: SPINOFFS + RECENT IPOs only (DEC-494 Pass 53 — NDX-non-S&P removed; now T1c per DEC-483).
# Curated by monthly review until Sprint 1 SCREENER-FIRST refactor (Polygon corp-actions feed) lands.
TIER2_SEEDS = {
    # Recent spinoffs (2023-2026) — should be in Tier 2 immediately
    "SNDK":  "spinoff_from_WDC_2025",
    "GEV":   "spinoff_from_GE_2024",
    "SOLV":  "spinoff_from_Honeywell_2024",
    "KVUE":  "spinoff_from_JNJ_2023",

    # High-momentum non-S&P names above $10B (add as discovered; verify they qualify as recent IPO or spinoff per DEC-103)
    "VST":   "high_momentum_energy",
    "SMCI":  "ai_infrastructure",
}


def get_sp500_tickers() -> set:
    df = pd.read_csv(SP500_CSV, comment='#')
    return set(df["Symbol"].str.strip().tolist())


def validate_ticker(ticker: str, sp500: set) -> dict | None:
    """
    Validate a ticker for Tier 2 inclusion.
    Returns None if it fails, dict with metadata if it passes.
    """
    if ticker in sp500:
        return None  # already in Tier 1

    try:
        tk   = yf.Ticker(ticker)
        info = tk.info

        market_cap_b = (info.get("marketCap", 0) or 0) / 1e9
        last_price   = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        avg_vol      = info.get("averageVolume", 0) or 0

        # Apply filters
        if market_cap_b < MIN_MKTCAP_SPINOFF_B:
            return None
        if last_price < MIN_PRICE:
            return None
        if avg_vol < MIN_AVG_VOL:
            return None

        return {
            "Symbol":     ticker,
            "Company":    info.get("longName", ticker),
            "Sector":     info.get("sector", "Unknown") or "Unknown",
            "MarketCapB": round(market_cap_b, 1),
            "LastPrice":  round(last_price, 2),
            "AvgVol":     int(avg_vol),
        }
    except Exception as e:
        print(f"  {ticker}: validation error — {e}")
        return None


def main():
    p = argparse.ArgumentParser(description="Refresh Tier 2 extended universe")
    p.add_argument("--write", action="store_true", help="Write CSV")
    p.add_argument("--add", nargs="+", metavar="TICKER",
                   help="Force-add tickers (spinoffs, immediate additions)")
    p.add_argument("--reason", default="manual_add",
                   help="Reason for force-add (e.g. spinoff_from_WDC)")
    args = p.parse_args()

    sp500 = get_sp500_tickers()
    print(f"S&P 500 universe: {len(sp500)} tickers (Tier 1 — excluded from Tier 2)")

    # Build candidate list from seeds + any force-adds
    candidates = dict(TIER2_SEEDS)
    if args.add:
        for t in args.add:
            candidates[t.upper()] = args.reason

    # Load existing CSV if present
    existing_df = pd.DataFrame()
    if CSV_PATH.exists():
        existing_df = pd.read_csv(CSV_PATH, comment='#')
        if "Symbol" in existing_df.columns:
            existing_tickers = set(existing_df["Symbol"].dropna().tolist())
        else:
            existing_tickers = set()
        print(f"Existing Tier 2 CSV: {len(existing_tickers)} tickers")
    else:
        existing_tickers = set()

    # Validate each candidate
    print(f"\nValidating {len(candidates)} candidates...")
    valid_rows = []
    promoted_to_tier1 = []

    for ticker, reason in candidates.items():
        time.sleep(0.3)
        if ticker in sp500:
            promoted_to_tier1.append(ticker)
            print(f"  {ticker}: promoted to S&P 500 (Tier 1) — removing from Tier 2")
            continue

        result = validate_ticker(ticker, sp500)
        if result:
            result["Tier2Reason"] = reason
            # Pass 53 B++ schema: added_date / removed_date (lowercase per standardization)
            if ticker in existing_tickers and "added_date" in existing_df.columns:
                prior = existing_df[existing_df["Symbol"] == ticker]["added_date"].values
                result["added_date"] = prior[0] if len(prior) else date.today().isoformat()
            else:
                result["added_date"] = date.today().isoformat()
            result["removed_date"] = ""  # NULL = currently active in Tier 2
            valid_rows.append(result)
            status = "existing" if ticker in existing_tickers else "NEW"
            print(f"  {ticker}: ✅ ${result['MarketCapB']:.1f}B  [{result['Sector']}]  ({status})")
        else:
            if ticker in existing_tickers:
                print(f"  {ticker}: ⚠️  failed validation — removing from Tier 2")
            else:
                print(f"  {ticker}: ❌ failed validation — not added")

    # Build result DataFrame
    result_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()

    print(f"\n{'='*60}")
    print(f"TIER 2 EXTENDED UNIVERSE SUMMARY")
    print(f"{'='*60}")
    print(f"Valid tickers:         {len(valid_rows)}")
    print(f"Promoted to S&P 500:   {len(promoted_to_tier1)} {promoted_to_tier1}")
    if not result_df.empty:
        print(f"Market cap range:      ${result_df['MarketCapB'].min():.1f}B — ${result_df['MarketCapB'].max():.1f}B")
        print(f"\nFinal list:")
        print(result_df[["Symbol","Company","Sector","MarketCapB","Tier2Reason"]].to_string(index=False))

    if not args.write:
        print(f"\nDry run — use --write to save to {CSV_PATH}")
        return

    # Pass 53 B++ canonical column order: Symbol,Company,Sector,added_date,removed_date,<extension cols>
    cols = ["Symbol","Company","Sector","added_date","removed_date","MarketCapB","Tier2Reason"]
    result_df = result_df[[c for c in cols if c in result_df.columns]]
    result_df.to_csv(CSV_PATH, index=False)
    print(f"\n✅ Written: {CSV_PATH} ({len(result_df)} tickers)")
    print(f"\nNext steps:")
    print(f"  git add backtest/data/extended_universe.csv")
    print(f"  git commit -m 'Tier 2 extended universe: monthly refresh {date.today()}'")
    print(f"  git push origin main")
    print(f"\nSchedule: run monthly. Run immediately after any major spinoff announcement.")
    print(f"Immediate spinoff: python scripts/refresh_extended_universe.py --add TICKER --reason spinoff_from_PARENT --write")


if __name__ == "__main__":
    main()
