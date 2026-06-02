#!/usr/bin/env python3
"""Batch 539 (2026-06-02) -- OPT-D pre-compute signals script.

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-D.

For each (ticker, as_of) pair in the backtest window, run
compute_all_signals on the OHLCV slice + write the resulting dict as
a row in `data_prefetch/precomputed_signals/<ticker>.parquet`. The
backtest engine then reads these rows at O(1) (post-Batch-541 wire-in)
instead of recomputing.

Trade-offs:
  + Backtest wall drops 10-50x (compute is amortized)
  + Re-runs (walk-forward, parameter sweeps) become near-instant
  - One-time pre-compute is itself expensive (similar wall to one
    backtest run)
  - Storage: ~270 signals x ~5K dates x 1937 tickers x 8 bytes = ~21GB
    parquet total
  - Stale: if config/strategies change indicator definitions, must
    re-pre-compute

Run:
  python scripts/precompute_signals.py --tickers AAPL,MSFT \\
      --start 2024-01-01 --end 2024-06-30

  # Full universe (post-OPT-A+B; ~5h on c7a.16xlarge):
  python scripts/precompute_signals.py --tickers ALL \\
      --start 2020-01-02 --end 2026-04-30
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backtest.signals.precomputed_cache import PRECOMPUTED_DIR
from backtest.signals.technical import compute_all_signals


def _load_ticker_ohlcv(ticker: str, cache_dir: Path) -> pd.DataFrame:
    """Load full OHLCV history for a ticker from Polygon cache."""
    safe = ticker.replace(".", "-").upper()
    path = cache_dir / f"{safe}.parquet"
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(path)
        # Normalize date column
        if "date" in df.columns:
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"]).set_index("date")
        return df.sort_index()
    except Exception:
        return pd.DataFrame()


def precompute_ticker(
    ticker: str,
    ohlcv: pd.DataFrame,
    start: date,
    end: date,
) -> pd.DataFrame:
    """Pre-compute signals for one ticker across [start, end].

    Returns DataFrame with columns = ["as_of_date"] + all ~270 signal
    keys. Rows = one per trading date in the window.

    Skips dates where ohlcv has insufficient history (compute_all_signals
    returns {} when len(df) < 10).
    """
    if ohlcv.empty:
        return pd.DataFrame()
    rows = []
    # Restrict to in-window trading dates that exist in OHLCV
    in_window = ohlcv.loc[
        (ohlcv.index.date >= start) & (ohlcv.index.date <= end)
    ]
    for ts in in_window.index:
        as_of = ts.date()
        slice_ = ohlcv.loc[:ts]  # PIT-safe: only up-to-and-including as_of
        signals = compute_all_signals(slice_)
        if signals:
            row = {"as_of_date": as_of, **signals}
            rows.append(row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tickers", required=True,
                    help='Comma-separated ticker list, or "ALL" for full '
                         'universe (Master Dedup CSV)')
    ap.add_argument("--start", required=True, type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    help="window start date YYYY-MM-DD")
    ap.add_argument("--end", required=True, type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    help="window end date YYYY-MM-DD")
    ap.add_argument("--ohlcv-cache-dir", type=Path,
                    default=REPO / "data_prefetch" / "polygon" / "ohlcv",
                    help="path to Polygon OHLCV per-ticker parquet cache")
    ap.add_argument("--output-dir", type=Path, default=PRECOMPUTED_DIR,
                    help="where to write per-ticker precompute parquets")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip tickers that already have a parquet "
                         "(idempotent re-run after partial)")
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.tickers.upper() == "ALL":
        # Read Master Dedup CSV
        master = REPO / "Backtesting universe" / "Master Dedup Universe.csv"
        if not master.exists():
            print(f"ERROR: master universe CSV not found at {master}",
                  file=sys.stderr)
            return 2
        df_master = pd.read_csv(master, comment="#")
        tickers = df_master["Symbol"].astype(str).tolist()
    else:
        tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]

    print(f"=== OPT-D pre-compute signals ===")
    print(f"Tickers:    {len(tickers)} ({tickers[:5]}{'...' if len(tickers) > 5 else ''})")
    print(f"Window:     {args.start} -> {args.end}")
    print(f"OHLCV cache:{args.ohlcv_cache_dir}")
    print(f"Output:     {args.output_dir}")
    print(f"Skip exist: {args.skip_existing}")
    print()

    n_done = n_skipped = n_missing = n_error = 0
    t0 = time.perf_counter()
    for i, ticker in enumerate(tickers, 1):
        safe = ticker.replace(".", "-").upper()
        out_path = args.output_dir / f"{safe}.parquet"
        if args.skip_existing and out_path.exists():
            n_skipped += 1
            continue
        ohlcv = _load_ticker_ohlcv(ticker, args.ohlcv_cache_dir)
        if ohlcv.empty:
            n_missing += 1
            continue
        try:
            df = precompute_ticker(ticker, ohlcv, args.start, args.end)
            if df.empty:
                n_missing += 1
                continue
            df.to_parquet(out_path, index=False)
            n_done += 1
        except Exception as e:
            print(f"  ERROR {ticker}: {e!r}", file=sys.stderr)
            n_error += 1
            continue
        if i % 25 == 0 or i == len(tickers):
            elapsed = time.perf_counter() - t0
            rate = i / elapsed
            eta_remaining = (len(tickers) - i) / max(rate, 0.001)
            print(f"  [{i:>5d}/{len(tickers)}] done={n_done} skipped={n_skipped} "
                  f"missing={n_missing} error={n_error} "
                  f"rate={rate:.2f} tk/s ETA={eta_remaining/60:.1f}m")

    elapsed = time.perf_counter() - t0
    print()
    print(f"=== SUMMARY ===")
    print(f"Total tickers:    {len(tickers)}")
    print(f"Precomputed:      {n_done}")
    print(f"Skipped (exist):  {n_skipped}")
    print(f"Missing OHLCV:    {n_missing}")
    print(f"Errors:           {n_error}")
    print(f"Wall time:        {elapsed/60:.1f}m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
