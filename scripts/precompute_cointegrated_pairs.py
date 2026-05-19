"""
scripts/precompute_cointegrated_pairs.py — T5b cointegrated pairs precompute.

Builds PIT-correct quarterly snapshots of cointegrated T1a pairs for the
pairs_trading strategy family (Batch 229 module, [backtest/signals/pairs_trading.py]).

Per IMPLEMENTATION_PLAN.md Track T5b (owner-approved 2026-05-18):
- T1a S&P 500 active membership at each as_of (PIT-correct via B++ schema CSV)
- 252-day close history per ticker, from Polygon OHLCV cache
- Engle-Granger cointegration test + half-life filter [5, 30] days (post-HFT survival)
- Quarterly grain: 26 snapshots Q1 2020 -> Q2 2026 (~10-15h wallclock)
- Output: per-snapshot parquets + _index.parquet

USAGE:
  # Full historical 26-quarter precompute (~10-15h):
  python scripts/precompute_cointegrated_pairs.py

  # Single-snapshot smoke test:
  python scripts/precompute_cointegrated_pairs.py --as-of 2024-01-01

  # Limited test (3 snapshots):
  python scripts/precompute_cointegrated_pairs.py --max-snapshots 3

NEVER run while a backtest is in progress - CPU steal would slow the
running backtest significantly. Wait for batch procs to complete first.

Output paths:
  data_prefetch/derived/cointegrated_pairs_t1a/{YYYY-MM-DD}.parquet
  data_prefetch/derived/cointegrated_pairs_t1a/_index.parquet
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.signals.pairs_trading import find_cointegrated_pairs

T1A_CSV = REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
OHLCV_DIR = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
OUT_DIR = REPO / "data_prefetch" / "derived" / "cointegrated_pairs_t1a"
INDEX_PATH = OUT_DIR / "_index.parquet"

QUARTERLY_DATES = [
    # Q1 2020 through Q2 2026 (26 snapshots, 1st of each quarter)
    date(2020, 1, 1), date(2020, 4, 1), date(2020, 7, 1), date(2020, 10, 1),
    date(2021, 1, 1), date(2021, 4, 1), date(2021, 7, 1), date(2021, 10, 1),
    date(2022, 1, 1), date(2022, 4, 1), date(2022, 7, 1), date(2022, 10, 1),
    date(2023, 1, 1), date(2023, 4, 1), date(2023, 7, 1), date(2023, 10, 1),
    date(2024, 1, 1), date(2024, 4, 1), date(2024, 7, 1), date(2024, 10, 1),
    date(2025, 1, 1), date(2025, 4, 1), date(2025, 7, 1), date(2025, 10, 1),
    date(2026, 1, 1), date(2026, 4, 1),
]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_t1a_pit_universe(as_of: date) -> list[str]:
    """Load T1a active membership at as_of (PIT-correct via B++ schema)."""
    df = pd.read_csv(T1A_CSV, comment="#")
    df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce").dt.date
    df["removed_date"] = pd.to_datetime(df["removed_date"], errors="coerce").dt.date

    def is_active(row) -> bool:
        a = row["added_date"]
        r = row["removed_date"]
        # added_date NULL = active before window; otherwise <= as_of
        added_ok = pd.isna(a) or a <= as_of
        # removed_date NULL = currently active; otherwise > as_of
        removed_ok = pd.isna(r) or r > as_of
        return added_ok and removed_ok

    active = df[df.apply(is_active, axis=1)]
    return sorted(active["Symbol"].astype(str).str.strip().unique().tolist())


def load_close_history(ticker: str, end_date: date, days: int = 252) -> Optional[pd.Series]:
    """Load ticker close history for `days` trading days ending at end_date."""
    safe = ticker.replace(".", "-")
    path = OHLCV_DIR / f"{safe}.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        if df.empty or "close" not in df.columns:
            return None
        # Date column handling
        if "date" in df.columns:
            df["date_dt"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df.dropna(subset=["date_dt"])
            df = df[df["date_dt"] <= end_date].sort_values("date_dt")
            if len(df) < days:
                return None
            tail = df.tail(days)
            s = pd.Series(tail["close"].values, index=tail["date_dt"].values, name=ticker)
            return s
        else:
            # Index-based fallback
            if hasattr(df.index, "date"):
                df = df[df.index.date <= end_date]
            else:
                df = df[df.index <= end_date]
            if len(df) < days:
                return None
            return df["close"].tail(days).rename(ticker)
    except Exception as e:
        log(f"  load fail {ticker}: {e}")
        return None


def build_closes_matrix(tickers: list[str], end_date: date, days: int = 252) -> pd.DataFrame:
    """Build (date x ticker) close matrix for the snapshot universe."""
    serieses = []
    skipped = 0
    for t in tickers:
        s = load_close_history(t, end_date, days=days)
        if s is None or len(s) < days:
            skipped += 1
            continue
        serieses.append(s)
    if not serieses:
        return pd.DataFrame()
    closes = pd.concat(serieses, axis=1, join="inner")
    log(f"  closes matrix: {closes.shape[1]} tickers x {len(closes)} days (skipped {skipped} for insufficient history)")
    return closes


def precompute_snapshot(as_of: date, significance: float = 0.05,
                         min_hl: int = 5, max_hl: int = 30,
                         max_pairs: int = 100) -> Optional[pd.DataFrame]:
    """Precompute cointegrated pairs for a single as_of snapshot.

    Returns DataFrame with cols: as_of_date, ticker_a, ticker_b, hedge_ratio,
    intercept, adf_pvalue, half_life. Returns None on failure or zero-result.
    """
    log(f"snapshot {as_of}: loading T1a PIT universe")
    tickers = load_t1a_pit_universe(as_of)
    log(f"  {len(tickers)} active T1a tickers at {as_of}")
    if len(tickers) < 10:
        log(f"  SKIP: <10 tickers (too sparse for cointegration tests)")
        return None
    log(f"  loading 252-day close histories...")
    closes = build_closes_matrix(tickers, end_date=as_of, days=252)
    if closes.shape[1] < 10 or len(closes) < 252:
        log(f"  SKIP: insufficient data ({closes.shape})")
        return None
    log(f"  running find_cointegrated_pairs (O(N^2) = {closes.shape[1]*(closes.shape[1]-1)//2} tests)...")
    t0 = time.time()
    pairs = find_cointegrated_pairs(
        closes,
        significance=significance,
        min_half_life=min_hl,
        max_half_life=max_hl,
        max_pairs=max_pairs,
    )
    elapsed = time.time() - t0
    log(f"  {len(pairs)} pairs survived (top by ADF p-value, in {elapsed:.1f}s)")
    if not pairs:
        return None
    df = pd.DataFrame(pairs)
    df.insert(0, "as_of_date", str(as_of))
    return df


def main() -> int:
    p = argparse.ArgumentParser(description="T5b cointegrated pairs precompute")
    p.add_argument("--as-of", type=str, default=None,
                   help="Single snapshot date (YYYY-MM-DD); skips full quarterly sweep")
    p.add_argument("--max-snapshots", type=int, default=None,
                   help="Limit to first N quarterly snapshots (for testing)")
    p.add_argument("--significance", type=float, default=0.05,
                   help="ADF p-value threshold (default 0.05)")
    p.add_argument("--min-half-life", type=int, default=5,
                   help="Min half-life in days (default 5)")
    p.add_argument("--max-half-life", type=int, default=30,
                   help="Max half-life in days (default 30; post-HFT survival)")
    p.add_argument("--max-pairs", type=int, default=100,
                   help="Max pairs retained per snapshot (default 100, sorted by ADF p)")
    p.add_argument("--skip-existing", action="store_true",
                   help="Skip snapshots whose output parquet already exists")
    args = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.as_of:
        snapshots = [date.fromisoformat(args.as_of)]
    else:
        snapshots = QUARTERLY_DATES
    if args.max_snapshots:
        snapshots = snapshots[: args.max_snapshots]

    log(f"=" * 60)
    log(f"T5b precompute: {len(snapshots)} snapshot(s)")
    log(f"Output: {OUT_DIR.relative_to(REPO)}")
    log(f"=" * 60)

    t_start = time.time()
    index_rows = []
    written = 0
    skipped = 0
    failed = 0

    for snap in snapshots:
        out_path = OUT_DIR / f"{snap}.parquet"
        if args.skip_existing and out_path.exists():
            log(f"snapshot {snap}: SKIP (exists)")
            skipped += 1
            continue
        try:
            df = precompute_snapshot(
                snap,
                significance=args.significance,
                min_hl=args.min_half_life,
                max_hl=args.max_half_life,
                max_pairs=args.max_pairs,
            )
            if df is None or df.empty:
                log(f"snapshot {snap}: no pairs found; not writing")
                failed += 1
                continue
            df.to_parquet(out_path, index=False)
            log(f"  -> wrote {out_path.relative_to(REPO)} ({len(df)} pairs)")
            index_rows.append({
                "as_of_date": str(snap),
                "pair_count": len(df),
                "median_half_life": float(df["half_life"].median()),
                "median_adf_pvalue": float(df["adf_pvalue"].median()),
            })
            written += 1
        except Exception as e:
            log(f"snapshot {snap}: FAIL ({type(e).__name__}: {e})")
            failed += 1
            continue

    # Write/update index
    if index_rows:
        new_index = pd.DataFrame(index_rows)
        if INDEX_PATH.exists():
            existing = pd.read_parquet(INDEX_PATH)
            # Replace any rows for snapshots we just wrote
            existing = existing[~existing["as_of_date"].isin(new_index["as_of_date"])]
            combined = pd.concat([existing, new_index], ignore_index=True)
        else:
            combined = new_index
        combined = combined.sort_values("as_of_date").reset_index(drop=True)
        combined.to_parquet(INDEX_PATH, index=False)
        log(f"index updated: {INDEX_PATH.relative_to(REPO)} ({len(combined)} snapshots total)")

    elapsed = time.time() - t_start
    log(f"=" * 60)
    log(f"DONE. Written: {written}, skipped: {skipped}, failed: {failed}. "
        f"Total wallclock: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    return 0 if written > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
