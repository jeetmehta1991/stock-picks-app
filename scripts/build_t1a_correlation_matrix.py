"""Batch 374 Sprint 7 B-3: pair-wise OHLCV correlation matrix precompute.

Closes the deferred-method in `OurRiskToolkit.get_correlation_to_existing_
positions` (sentinel returned `max_correlation=None` because pair-wise
OHLCV correlation is expensive at runtime). This precompute job builds
a per-snapshot symmetric correlation matrix that the toolkit reads at
agent-call time.

Output schema: data_prefetch/derived/correlation_matrix_t1a/<YYYY-MM-DD>.parquet
  ticker_a    str  (sorted to A side; symmetric so only one half stored)
  ticker_b    str
  pearson_r   float64  (rolling-window correlation of log returns)
  n_obs       int      (overlapping trading days in window)
  window_days int      (formation window; default 60 ~= 3 months)

Methodology (per Pearson / Krauss 2017):
  1. Load T1a PIT-active tickers at as_of
  2. For each ticker: load <= as_of OHLCV from cache; compute log returns
  3. For each (A, B) pair within same sector AND across sectors (controls
     sector overlap): correlation of last `window_days` log returns
  4. Filter abs(r) >= corr_floor (default 0.5) to keep file small

Compute estimate (T1a ~614 tickers):
  ~190K candidate pairs (614 choose 2)
  ~1ms per pair (vectorized corr)
  Total: ~3-5 min per snapshot

Usage:
  python scripts/build_t1a_correlation_matrix.py --as-of 2024-01-01
  python scripts/build_t1a_correlation_matrix.py --smoke           # 10 mega-caps
"""
from __future__ import annotations

import argparse
import sys
from datetime import date as _date
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
OHLCV_DIR = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
T1A_CSV = REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
OUT_DIR = REPO / "data_prefetch" / "derived" / "correlation_matrix_t1a"

WINDOW_DAYS = 60
CORR_FLOOR  = 0.5


def _load_ticker_logret(ticker: str, as_of: _date, lookback: int) -> pd.Series | None:
    safe = ticker.replace(".", "-")
    p = OHLCV_DIR / f"{safe}.parquet"
    if not p.exists():
        return None
    try:
        df = pd.read_parquet(p)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df[df["date"] <= as_of].sort_values("date").tail(lookback + 1)
        if df.empty or "close" not in df.columns or len(df) < lookback // 2:
            return None
        log_ret = np.diff(np.log(df["close"].values.astype(float)))
        return pd.Series(log_ret, index=range(len(log_ret)))
    except Exception as exc:
        # DEC-231: log silent failures with context
        print(f"[WARN] {ticker}: parquet load failed exc={exc}")
        return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--as-of", default="2024-01-01")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--corr-floor", type=float, default=CORR_FLOOR)
    p.add_argument("--window-days", type=int, default=WINDOW_DAYS)
    args = p.parse_args()

    as_of = _date.fromisoformat(args.as_of)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{as_of.isoformat()}.parquet"

    if args.smoke:
        tickers = ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMZN", "JPM", "XOM",
                   "JNJ", "WMT"]
    else:
        if not T1A_CSV.exists():
            print(f"[ERROR] {T1A_CSV} missing")
            return 1
        df_t1a = pd.read_csv(T1A_CSV, comment="#")
        df_t1a["added_dt"] = pd.to_datetime(df_t1a.get("added_date"), errors="coerce").dt.date
        df_t1a["removed_dt"] = pd.to_datetime(df_t1a.get("removed_date"), errors="coerce").dt.date
        active = df_t1a[
            (df_t1a["added_dt"].isna() | (df_t1a["added_dt"] <= as_of))
            & (df_t1a["removed_dt"].isna() | (df_t1a["removed_dt"] > as_of))
        ]
        tickers = list(active["Symbol"].unique())

    print(f"[INFO] Universe: {len(tickers)} tickers; window={args.window_days}d; corr_floor={args.corr_floor}")

    log_returns = {}
    for t in tickers:
        s = _load_ticker_logret(t, as_of, args.window_days)
        if s is not None and len(s) >= args.window_days // 2:
            log_returns[t] = s.values[-args.window_days:]
    print(f"[INFO] Log returns loaded for {len(log_returns)}/{len(tickers)} tickers")

    valid = sorted(log_returns.keys())
    rows = []
    n_pairs = 0
    for a, b in combinations(valid, 2):
        ra, rb = log_returns[a], log_returns[b]
        n_common = min(len(ra), len(rb))
        if n_common < args.window_days // 2:
            continue
        ra_, rb_ = ra[-n_common:], rb[-n_common:]
        if np.std(ra_) < 1e-12 or np.std(rb_) < 1e-12:
            continue
        r = float(np.corrcoef(ra_, rb_)[0, 1])
        if not np.isfinite(r) or abs(r) < args.corr_floor:
            continue
        rows.append({
            "ticker_a":    a,
            "ticker_b":    b,
            "pearson_r":   round(r, 4),
            "n_obs":       int(n_common),
            "window_days": int(args.window_days),
        })
        n_pairs += 1
    print(f"[INFO] Kept {n_pairs} pairs (abs(r) >= {args.corr_floor})")

    df = pd.DataFrame(rows, columns=["ticker_a", "ticker_b", "pearson_r",
                                      "n_obs", "window_days"])
    df.to_parquet(out_path, index=False)
    print(f"[OK] Wrote {len(df)} correlation rows to {out_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
