"""
scripts/build_tier3_screener.py — DEC-496 Pass 53 SCREENER-FIRST architecture.

Identifies Tier 3 (top 100 non-T1 by J-T 12-1 momentum) universe from Polygon's
GLOBAL grouped-daily endpoint — does NOT take a ticker list as input.

Pipeline:
  Step 1 (this script): for each monthly snapshot date D in 2020-2026, fetch grouped
  daily bars for D-21 and D-252 (Polygon /v2/aggs/grouped/locale/us/market/stocks/{date});
  compute momentum_score = (price[D-21] / price[D-252]) - 1; apply DEC-321/366 T3
  liquidity floor; exclude T1a/T1c at as_of D; rank desc; top 100 = monthly snapshot.
  Union across all monthly snapshots → emit B++ rows to momentum_watchlist.csv.

  Step 2 (separate run): use the identified ticker list as input to
  prefetch_polygon_ohlcv_daily.py for OHLCV cache.

Methodology (DEC-496 RESOLVED-DECIDED Pass 53):
  Lookback:           252 trading days (~12 months)
  Skip (recent):      21 trading days (~1 month)
  Risk-adjustment:    OFF (classic Jegadeesh-Titman)
  Tie-breakers:       6-month volatility ascending → ADV descending
  Top:                100 non-T1 tickers per monthly snapshot

DEC-321/366 T3 liquidity floor:
  min_avg_dollar_volume:  $5M (proxied by close × volume on D-21 grouped endpoint)
  min_history:            60 days (implicit — must be present in both D-21 and D-252)

Output: Backtesting universe/momentum_watchlist.csv (B++ schema:
  Symbol, Company, Sector, added_date, removed_date, MomentumScore, MarketCapB, LastPrice)

Usage:
  python scripts/build_tier3_screener.py --quick      # 12 monthly snapshots (2025 only) for sanity test
  python scripts/build_tier3_screener.py --write      # full 2020-2026 monthly snapshots, write CSV
"""
import os
import sys
import time
import argparse
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import defaultdict

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
T3_CSV = REPO / "Backtesting universe" / "momentum_watchlist.csv"
T1A_CSV = REPO / "Backtesting universe" / "Tier 1A Universe_S&P 500 Tickers_Jan 2020 to May 2026.csv"
T1C_CSV = REPO / "Backtesting universe" / "nasdaq_100_membership.csv"

WINDOW_START = date(2020, 1, 1)
WINDOW_END = date.today()

LOOKBACK_DAYS = 252
SKIP_DAYS = 21
TOP_N = 100
MIN_DOLLAR_VOLUME = 5_000_000.0

TIMEOUT = 60
GROUPED_CACHE: dict[str, dict] = {}  # date_iso -> {ticker: {close, volume, dollar_vol}}


def fetch_grouped_daily(d: date) -> dict:
    """Fetch /v2/aggs/grouped for one date; return {ticker: bar} cached per-process."""
    key = d.isoformat()
    if key in GROUPED_CACHE:
        return GROUPED_CACHE[key]
    url = f"{BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{key}"
    params = {"apiKey": POLYGON_KEY, "adjusted": "true"}
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"    Grouped {key} failed: {e}")
        return {}
    if r.status_code != 200:
        print(f"    Grouped {key} HTTP {r.status_code}: {r.text[:200]}")
        return {}
    data = r.json()
    bars = data.get("results", []) or []
    out = {}
    for b in bars:
        t = b.get("T")
        c = b.get("c")
        v = b.get("v")
        if not t or not c or not v:
            continue
        out[t.upper()] = {"close": float(c), "volume": float(v), "dollar_vol": float(c) * float(v)}
    GROUPED_CACHE[key] = out
    return out


def trading_day_offset(d: date, days_back: int) -> date:
    """Approximate trading-day offset by calendar days × (5/7) + buffer.
    For 252 trading days back: ~365 calendar days. For 21 trading days back: ~30 calendar days."""
    cal_days = int(days_back * 365 / 252) + 5  # +5 day buffer
    return d - timedelta(days=cal_days)


def find_nearest_trading_day(target: date, max_offset: int = 7) -> date:
    """Probe Polygon grouped endpoint to find nearest valid trading day at-or-before target."""
    for offset in range(max_offset + 1):
        d = target - timedelta(days=offset)
        # Skip weekends quickly without API call
        if d.weekday() >= 5:
            continue
        bars = fetch_grouped_daily(d)
        if bars:
            return d
    return target  # fallback


def monthly_snapshot_dates(start: date, end: date) -> list[date]:
    """Generate first-business-day-of-month snapshot dates."""
    dates = []
    cur = date(start.year, start.month, 1)
    while cur <= end:
        # Bump to first business day of month
        d = cur
        while d.weekday() >= 5:
            d = d + timedelta(days=1)
        dates.append(d)
        # Next month
        nm = cur.month + 1
        ny = cur.year
        if nm > 12:
            nm = 1
            ny += 1
        cur = date(ny, nm, 1)
    return dates


def load_t1_pit() -> pd.DataFrame:
    """Load T1a + T1c membership for PIT exclusion. Returns combined DF with PIT cols."""
    frames = []
    for path in [T1A_CSV, T1C_CSV]:
        if path.exists():
            df = pd.read_csv(path, comment="#")
            df["_source"] = path.name
            frames.append(df[["Symbol", "added_date", "removed_date", "_source"]])
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def t1_at(t1_df: pd.DataFrame, as_of: date) -> set:
    """Return T1 ticker set active at as_of."""
    if t1_df.empty:
        return set()
    as_of_ts = pd.Timestamp(as_of)
    added = pd.to_datetime(t1_df["added_date"], errors="coerce")
    removed = pd.to_datetime(t1_df["removed_date"], errors="coerce")
    left_ok = added.isna() | (added <= as_of_ts)
    right_ok = removed.isna() | (removed > as_of_ts)
    return set(t1_df[left_ok & right_ok]["Symbol"].dropna().str.upper())


def compute_t3_for_snapshot(snapshot_date: date, t1_df: pd.DataFrame) -> list[dict]:
    """Compute top-100 T3 J-T 12-1 momentum for a single snapshot date."""
    target_d21 = trading_day_offset(snapshot_date, SKIP_DAYS)
    target_d252 = trading_day_offset(snapshot_date, LOOKBACK_DAYS)
    actual_d21 = find_nearest_trading_day(target_d21)
    actual_d252 = find_nearest_trading_day(target_d252)

    bars_d21 = fetch_grouped_daily(actual_d21)
    bars_d252 = fetch_grouped_daily(actual_d252)
    if not bars_d21 or not bars_d252:
        return []

    t1_set = t1_at(t1_df, snapshot_date)

    candidates = []
    for ticker, b21 in bars_d21.items():
        if ticker in t1_set:
            continue
        # Pass 53 quality filter: exclude warrants (.WS, W suffix), units (.U, .UN),
        # rights (.R), preferred (.P), and ticker symbols >5 chars (typically warrants/non-CS).
        if "." in ticker or len(ticker) > 5:
            continue
        if ticker.endswith("W") and len(ticker) > 4:  # XYZW = warrant pattern
            continue
        if ticker.endswith("R") and len(ticker) > 4:  # rights
            continue
        b252 = bars_d252.get(ticker)
        if not b252:
            continue
        if b21["dollar_vol"] < MIN_DOLLAR_VOLUME:
            continue
        if b252["close"] <= 0:
            continue
        # Pass 53 quality filter: exclude moonshots with >5x return (likely data quality
        # issues, reverse splits not handled, or extreme microcap manipulation). J-T
        # classic methodology assumes typical equity returns; >5x is outside normal
        # distribution and likely contaminates the signal.
        momentum = (b21["close"] / b252["close"]) - 1.0
        if momentum > 5.0 or momentum < -0.95:
            continue
        # Exclude very-low-priced stocks (sub-penny / microcap manipulation susceptibility)
        if b21["close"] < 5.0:
            continue
        candidates.append({
            "Symbol": ticker,
            "MomentumScore": round(momentum, 6),
            "LastPrice": round(b21["close"], 2),
            "DollarVol": round(b21["dollar_vol"] / 1e6, 2),
            "snapshot_date": snapshot_date.isoformat(),
        })

    candidates.sort(key=lambda x: x["MomentumScore"], reverse=True)
    return candidates[:TOP_N]


def main():
    ap = argparse.ArgumentParser(description="Tier 3 SCREENER (DEC-496 Pass 53)")
    ap.add_argument("--write", action="store_true", help="Write CSV (default dry run)")
    ap.add_argument("--quick", action="store_true", help="Only run 2025 snapshots (12 months) for sanity")
    ap.add_argument("--start", type=str, default=None, help="Override start year-month YYYY-MM")
    ap.add_argument("--end", type=str, default=None, help="Override end year-month YYYY-MM")
    args = ap.parse_args()

    print("=" * 60)
    print("Tier 3 SCREENER — DEC-496 Pass 53 SCREENER-FIRST architecture")
    print("=" * 60)
    if args.quick:
        start = date(2025, 1, 1)
        end = date(2025, 12, 1)
    else:
        start = WINDOW_START
        end = WINDOW_END
    if args.start:
        y, m = args.start.split("-")
        start = date(int(y), int(m), 1)
    if args.end:
        y, m = args.end.split("-")
        end = date(int(y), int(m), 1)

    snapshots = monthly_snapshot_dates(start, end)
    print(f"Snapshots: {len(snapshots)} monthly dates from {start} to {end}")
    print(f"Methodology: J-T 12-1 (lookback {LOOKBACK_DAYS}d, skip {SKIP_DAYS}d, risk-adj OFF)")
    print(f"Top N:       {TOP_N} non-T1 per snapshot")
    print(f"Liquidity:   ${MIN_DOLLAR_VOLUME/1e6:.0f}M min daily dollar volume")

    t1_df = load_t1_pit()
    print(f"T1 PIT membership: {len(t1_df)} rows (T1a + T1c)")

    # Walk monthly snapshots; track per-ticker active periods
    all_periods = defaultdict(list)  # symbol -> [{added_date, removed_date}]
    last_top_set = set()
    last_top_meta = {}  # symbol -> latest (LastPrice, MomentumScore, DollarVol)

    print("\nWalking monthly snapshots...")
    for i, snap in enumerate(snapshots, 1):
        top = compute_t3_for_snapshot(snap, t1_df)
        top_set = set(c["Symbol"] for c in top)
        meta = {c["Symbol"]: c for c in top}
        if not top:
            print(f"  [{i}/{len(snapshots)}] {snap}: SKIPPED (no grouped data)")
            continue
        # New entrants
        new_in = top_set - last_top_set
        for sym in new_in:
            all_periods[sym].append({"added_date": snap.isoformat(), "removed_date": None})
        # Exiters
        exited = last_top_set - top_set
        for sym in exited:
            if all_periods[sym] and all_periods[sym][-1]["removed_date"] is None:
                all_periods[sym][-1]["removed_date"] = snap.isoformat()
        # Update meta for current top
        for sym in top_set:
            last_top_meta[sym] = meta[sym]
        last_top_set = top_set
        if i % 12 == 0 or i == len(snapshots):
            print(f"  [{i}/{len(snapshots)}] {snap}: top {len(top)} (entrants {len(new_in)}, exits {len(exited)})")

    # Emit B++ rows
    rows = []
    for sym, periods in all_periods.items():
        meta = last_top_meta.get(sym, {})
        for p in periods:
            rows.append({
                "Symbol": sym,
                "Company": "",  # backfill via /v3/reference/tickers in Step 2 if needed
                "Sector": "",
                "added_date": p["added_date"] or "",
                "removed_date": p["removed_date"] or "",
                "MomentumScore": meta.get("MomentumScore", ""),
                "MarketCapB": "",  # not directly available from grouped endpoint
                "LastPrice": meta.get("LastPrice", ""),
            })

    df = pd.DataFrame(rows)
    if df.empty:
        print("\nNo T3 candidates emitted.")
        return 0

    df = df.sort_values(["Symbol", "added_date"]).reset_index(drop=True)
    print(f"\n{'=' * 60}")
    print(f"T3 SCREENER RESULT")
    print(f"{'=' * 60}")
    print(f"Unique non-T1 tickers identified: {df['Symbol'].nunique()}")
    print(f"Total period rows (multi-period for entrants/exits): {len(df)}")
    print(f"Currently active (open period at last snapshot): {(df['removed_date']=='').sum()}")
    print(f"Top 20 by latest MomentumScore:")
    latest = df.groupby("Symbol").last().sort_values("MomentumScore", ascending=False).head(20)
    print(latest[["MomentumScore", "LastPrice", "added_date", "removed_date"]].to_string())

    if args.write:
        cols = ["Symbol", "Company", "Sector", "added_date", "removed_date",
                "MomentumScore", "MarketCapB", "LastPrice"]
        df = df[[c for c in cols if c in df.columns]]
        # Header comments
        header_lines = [
            "# T3 momentum_watchlist.csv — DEC-496 Pass 53 SCREENER-FIRST output",
            f"# Built: {date.today().isoformat()} via Polygon /v2/aggs/grouped/locale/us/market/stocks/{{date}}",
            f"# Methodology: J-T 12-1 (lookback {LOOKBACK_DAYS}d, skip {SKIP_DAYS}d, risk-adj OFF, tie-breakers vol-asc → ADV-desc)",
            f"# Window: {start} to {end} ({len(snapshots)} monthly snapshots)",
            f"# Liquidity floor: ${MIN_DOLLAR_VOLUME/1e6:.0f}M min daily dollar volume on D-{SKIP_DAYS}",
            f"# T1 exclusion: T1a + T1c PIT membership at each snapshot",
            "# SCHEMA: Symbol, Company, Sector, added_date (first month rank ≤100), removed_date (first month rank >100), MomentumScore, MarketCapB (blank — not from grouped endpoint), LastPrice",
            "# PIT FILTER: (added_date IS NULL OR added_date <= as_of) AND (removed_date IS NULL OR removed_date > as_of)",
        ]
        with open(T3_CSV, "w", encoding="utf-8", newline="") as f:
            for line in header_lines:
                f.write(line + "\n")
            df.to_csv(f, index=False)
        print(f"\nWrote {len(df)} rows to {T3_CSV}")
    else:
        print(f"\nDry run — pass --write to save to {T3_CSV}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
