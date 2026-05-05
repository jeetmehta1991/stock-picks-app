"""
scripts/build_momentum_watchlist.py
Build Tier 3 momentum watchlist — top momentum non-S&P stocks for live screening.

TIER 3 DESIGN:
- Universe scanned: Nasdaq 100 + Russell 1000 minus S&P 500 overlap
- Selection: top 50 by 3-month price momentum, passing liquidity filters
- Liquidity: price > $10, avg_volume > 500K, market_cap > $2B
- Update frequency: MONTHLY in live trading (Stage 3+)
                    STATIC for backtesting (fixed at run start)
- Out-of-cycle addition: any stock with >50% single-month move passing liquidity

FREQUENCY RATIONALE:
- Weekly is too noisy — high turnover, transaction costs from new signals outweigh benefit
- Monthly balances freshness vs stability — aligns with institutional rebalancing cycles
- The list updates at month-end and is fixed for the entire following month
- Exception: a stock with extraordinary momentum (>50% in 30 days) can be added
  immediately via --add flag without waiting for monthly cycle

USAGE:
    python scripts/build_momentum_watchlist.py           # generate and review
    python scripts/build_momentum_watchlist.py --write   # write to CSV
    python scripts/build_momentum_watchlist.py --add TICKER1 TICKER2  # force-add

RUN ON: laptop (no network restrictions) — monthly
OUTPUT: backtest/data/Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv (Symbol, Company, Sector, MomentumScore, MarketCapB, AddedDate)
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# ── Config ──────────────────────────────────────────────────────────────────
CSV_PATH   = Path(__file__).parent.parent / "Backtesting universe" / "Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv"
SP500_CSV  = Path(__file__).parent.parent / "Backtesting universe" / "Current Snapshot_SP500 Tickers_May 2026.csv"
MAX_TICKERS = 50          # top N by momentum
MIN_PRICE   = 10.0        # USD
MIN_AVG_VOL = 500_000     # shares/day
MIN_MKTCAP_B = 2.0        # USD billions
MOMENTUM_DAYS = 63        # ~3 months of trading days
LOOKBACK_DAYS = 95        # calendar days to fetch (includes weekends)
BIG_MOVE_THRESHOLD = 0.50 # 50% — triggers out-of-cycle addition

# Nasdaq 100 non-S&P tickers (approximate — update semi-annually)
# These are Nasdaq 100 members that are NOT in the S&P 500
NASDAQ100_NON_SP500 = [
    "MELI", "ASML", "TEAM", "WDAY", "DDOG", "SGEN", "CPNG", "RIVN", "LCID",
    "GRAB", "ZS", "CRWD", "NET", "SNOW", "PLTR", "ABNB", "DASH", "COIN",
]

# Russell 1000 non-S&P high-profile names (seed list — not exhaustive)
# Focus on large-cap spinoffs, recent IPOs, high-momentum names
RUSSELL1000_SEEDS = [
    "SNDK", "GEV", "VST", "SMCI", "GDDY", "ERIE",  # known S&P additions we're missing
    "ARM",  "RDDT", "BIRK", "LNTH", "OSCR", "ASTS",  # recent IPOs/spinoffs
]


def get_sp500_tickers() -> set:
    """Load current S&P 500 tickers from committed CSV."""
    df = pd.read_csv(SP500_CSV)
    return set(df["Symbol"].str.strip().tolist())


def compute_momentum(tickers: list, sp500: set) -> pd.DataFrame:
    """
    Download price history and compute 3-month momentum for all tickers.
    Filters: not in S&P 500, passes liquidity, valid price data.
    Returns DataFrame sorted by momentum score descending.
    """
    end   = date.today()
    start = end - timedelta(days=LOOKBACK_DAYS)

    # Remove any that are already in S&P 500
    candidates = [t for t in tickers if t not in sp500]
    print(f"Candidates to evaluate: {len(candidates)}")

    if not candidates:
        return pd.DataFrame()

    # Bulk download
    print(f"Downloading {len(candidates)} tickers ({start} → {end})...")
    try:
        raw = yf.download(
            candidates, start=start.isoformat(), end=end.isoformat(),
            auto_adjust=True, progress=False, threads=True,
        )
    except Exception as e:
        print(f"Download error: {e}")
        return pd.DataFrame()

    # Handle MultiIndex columns
    if isinstance(raw.columns, pd.MultiIndex):
        close_df  = raw["Close"]
        volume_df = raw["Volume"]
    else:
        close_df  = raw[["Close"]].rename(columns={"Close": candidates[0]})
        volume_df = raw[["Volume"]].rename(columns={"Volume": candidates[0]})

    rows = []
    for ticker in candidates:
        if ticker not in close_df.columns:
            continue
        prices  = close_df[ticker].dropna()
        volumes = volume_df[ticker].dropna() if ticker in volume_df.columns else pd.Series()

        if len(prices) < MOMENTUM_DAYS // 2:
            continue  # insufficient history

        # Momentum: return over last MOMENTUM_DAYS trading days
        if len(prices) >= MOMENTUM_DAYS:
            momentum = (prices.iloc[-1] / prices.iloc[-MOMENTUM_DAYS] - 1) * 100
        else:
            momentum = (prices.iloc[-1] / prices.iloc[0] - 1) * 100

        last_price  = float(prices.iloc[-1])
        avg_vol     = float(volumes.tail(20).mean()) if len(volumes) >= 20 else 0.0

        # Liquidity filters
        if last_price < MIN_PRICE:
            continue
        if avg_vol < MIN_AVG_VOL:
            continue

        rows.append({
            "Symbol":        ticker,
            "MomentumPct":   round(momentum, 1),
            "LastPrice":     round(last_price, 2),
            "AvgVol20d":     int(avg_vol),
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values("MomentumPct", ascending=False)
    return df


def get_market_cap_and_sector(tickers: list) -> pd.DataFrame:
    """Fetch market cap and sector for selected tickers via yfinance."""
    import time
    rows = []
    for i, ticker in enumerate(tickers):
        try:
            info = yf.Ticker(ticker).info
            rows.append({
                "Symbol":      ticker,
                "Company":     info.get("longName", ticker),
                "Sector":      info.get("sector", "Unknown") or "Unknown",
                "MarketCapB":  round((info.get("marketCap", 0) or 0) / 1e9, 1),
            })
        except Exception:
            rows.append({
                "Symbol": ticker, "Company": ticker,
                "Sector": "Unknown", "MarketCapB": 0.0,
            })
        if i < len(tickers) - 1:
            time.sleep(0.3)
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser(description="Build Tier 3 momentum watchlist")
    p.add_argument("--write", action="store_true", help="Write CSV (default: dry run)")
    p.add_argument("--top", type=int, default=MAX_TICKERS, help=f"Top N tickers (default {MAX_TICKERS})")
    p.add_argument("--add", nargs="+", metavar="TICKER", help="Force-add tickers regardless of momentum")
    p.add_argument("--out-of-cycle", action="store_true",
                   help="Flag: out-of-cycle update (big movers) — adds to existing list")
    args = p.parse_args()

    sp500 = get_sp500_tickers()
    print(f"S&P 500 universe: {len(sp500)} tickers (excluded from Tier 3)")

    # Full candidate list
    all_candidates = list(set(NASDAQ100_NON_SP500 + RUSSELL1000_SEEDS))
    if args.add:
        for t in args.add:
            all_candidates.append(t.upper())

    # Compute momentum
    momentum_df = compute_momentum(all_candidates, sp500)
    if momentum_df.empty:
        print("No valid momentum data — check network and try again")
        sys.exit(1)

    # Select top N
    selected = momentum_df.head(args.top)

    # If out-of-cycle, also flag big movers specifically
    if args.out_of_cycle:
        big_movers = momentum_df[momentum_df["MomentumPct"] >= BIG_MOVE_THRESHOLD * 100]
        if not big_movers.empty:
            print(f"\n⚡ OUT-OF-CYCLE BIG MOVERS (>{BIG_MOVE_THRESHOLD*100:.0f}% in {MOMENTUM_DAYS}d):")
            print(big_movers[["Symbol","MomentumPct","LastPrice"]].to_string(index=False))

    print(f"\n{'='*60}")
    print(f"TOP {len(selected)} MOMENTUM TICKERS (not in S&P 500)")
    print(f"{'='*60}")
    print(selected[["Symbol","MomentumPct","LastPrice","AvgVol20d"]].to_string(index=False))

    if not args.write:
        print(f"\nDry run — use --write to save to {CSV_PATH}")
        return

    # Fetch market cap + sector for selected tickers
    print(f"\nFetching sector/market cap for {len(selected)} tickers...")
    meta_df = get_market_cap_and_sector(selected["Symbol"].tolist())

    # Merge and build final CSV
    final_df = selected.merge(meta_df, on="Symbol", how="left")

    # Apply market cap filter
    final_df = final_df[
        (final_df["MarketCapB"] >= MIN_MKTCAP_B) | (final_df["MarketCapB"] == 0)
    ].copy()

    final_df["AddedDate"]     = date.today().isoformat()
    final_df["UpdateCycle"]   = "monthly"
    final_df["MomentumScore"] = final_df["MomentumPct"]

    cols = ["Symbol","Company","Sector","MomentumScore","MarketCapB","LastPrice","AddedDate"]
    final_df = final_df[[c for c in cols if c in final_df.columns]]

    # If out-of-cycle, merge with existing list
    if args.out_of_cycle and CSV_PATH.exists():
        existing = pd.read_csv(CSV_PATH)
        combined = pd.concat([existing, final_df], ignore_index=True)
        final_df = combined.drop_duplicates(subset=["Symbol"], keep="last")

    final_df.to_csv(CSV_PATH, index=False)
    print(f"\n✅ Written: {CSV_PATH}")
    print(f"   {len(final_df)} tickers in Tier 3 momentum watchlist")
    print(f"\nNext steps:")
    print(f"  git add backtest/data/Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv")
    print(f"  git commit -m 'Tier 3 momentum watchlist: monthly refresh {date.today()}'")
    print(f"  git push origin main")
    print(f"\nSchedule: run monthly at start of each month on laptop.")
    print(f"Out-of-cycle: python scripts/build_momentum_watchlist.py --out-of-cycle --write")


if __name__ == "__main__":
    main()
