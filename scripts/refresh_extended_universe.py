"""
scripts/refresh_extended_universe.py
Build and refresh Tier 2 extended universe — spinoffs, large non-S&P stocks, 
Nasdaq 100 non-S&P members above $10B market cap.

TIER 2 DESIGN:
- Spinoffs: any company above $5B market cap within 12 months of spinoff
- Nasdaq 100 non-S&P: large liquid names not yet in S&P 500
- Recent IPOs: above $10B market cap with 90+ days of trading history
- Update frequency: MONTHLY for live trading (Stage 3+)
                    NOT needed for backtesting

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
OUTPUT: backtest/data/extended_universe.csv (Symbol, Company, Sector, MarketCapB, Tier2Reason, AddedDate)
"""
import argparse
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# ── Config ──────────────────────────────────────────────────────────────────
CSV_PATH   = Path(__file__).parent.parent / "backtest" / "data" / "extended_universe.csv"
SP500_CSV  = Path(__file__).parent.parent / "backtest" / "data" / "sp500_tickers.csv"
MIN_MKTCAP_SPINOFF_B = 5.0   # spinoffs above $5B
MIN_MKTCAP_GENERAL_B = 10.0  # general Tier 2 additions above $10B
MIN_PRICE   = 5.0
MIN_AVG_VOL = 200_000

# Seed list — major non-S&P stocks warranting Tier 2 inclusion
# This is curated by the monthly review, not auto-generated
# Includes: known spinoffs, large Nasdaq/NYSE non-S&P names, major ETFs already in ETFS_FULL
TIER2_SEEDS = {
    # Recent spinoffs (2024-2026) — should be in Tier 2 immediately
    "SNDK":  "spinoff_from_WDC_2025",
    "GEV":   "spinoff_from_GE_2024",
    "SOLV":  "spinoff_from_Honeywell_2024",
    "KVUE":  "spinoff_from_JNJ_2023",

    # Large Nasdaq non-S&P (Nasdaq 100 members above $50B not in S&P 500)
    "MELI":  "nasdaq100_non_sp500",
    "ASML":  "nasdaq100_non_sp500",

    # High-momentum non-S&P names above $10B (add as discovered)
    "VST":   "high_momentum_energy",
    "SMCI":  "ai_infrastructure",
}


def get_sp500_tickers() -> set:
    df = pd.read_csv(SP500_CSV)
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
        existing_df = pd.read_csv(CSV_PATH)
        existing_tickers = set(existing_df["Symbol"].tolist())
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
            result["AddedDate"]   = (
                existing_df[existing_df["Symbol"] == ticker]["AddedDate"].values[0]
                if ticker in existing_tickers else date.today().isoformat()
            )
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

    cols = ["Symbol","Company","Sector","MarketCapB","Tier2Reason","AddedDate"]
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
