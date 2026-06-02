"""Batch 539 (2026-06-02) -- OPT-D pre-computed signals cache MVP.

Source: per CHECKLIST #77 + owner directive 2026-06-01 "execute a b c d
sequentially" + 2 (continue autonomously into OPT-C / OPT-D).
Queue: EXECUTION_QUEUE.md OPT-D (pre-computed signals pipeline).

CURRENT (compute-on-demand per bar):
    For each (ticker, as_of) in backtest:
        df = ohlcv slice up to as_of
        signals = compute_all_signals(df)   # ~270 signals, ~25ms
    Result for full R4: 388 tkrs x 1044 bars x 25ms = ~10K minutes pure compute

PRE-COMPUTED (this scaffold):
    PHASE 1 (one-time, before backtest):
        scripts/precompute_signals.py walks each (ticker, date) tuple,
        runs compute_all_signals on each slice, writes the result to a
        single per-ticker parquet at:
            data_prefetch/precomputed_signals/<ticker>.parquet
        Columns: as_of_date + all ~270 signal keys
        Rows: one per backtest date in the precompute window

    PHASE 2 (at runtime):
        screen_instrument calls _load_precomputed_signals(ticker, as_of)
        FIRST. On cache HIT, returns the row as a dict (~O(1)). On MISS,
        falls back to compute_all_signals(df) per-ticker path.

    Expected speedup: 10-50x on backtest wall (compute is one-time cost
    amortized across re-runs). Walk-forward / IS-OOS re-runs become
    near-instant on the screen step.

NOT YET WIRED. This module ships the reader + cache schema; the
pre-compute script (Batch 540) + screener wire-in (Batch 541) are
separate batches.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

REPO = Path(__file__).resolve().parent.parent.parent
PRECOMPUTED_DIR = REPO / "data_prefetch" / "precomputed_signals"

# Module-level cache: {ticker: indexed-by-date DataFrame}
# First call per ticker loads the parquet + indexes by as_of_date for
# O(1) date lookup. Subsequent calls return cached frame.
_SIGNALS_BY_TICKER: dict[str, pd.DataFrame] = {}


def _load_signals_parquet(ticker: str) -> Optional[pd.DataFrame]:
    """Load + cache the per-ticker pre-computed signals parquet.

    Returns the DataFrame indexed by as_of_date (so lookups are O(1)),
    or None when no parquet exists yet (caller falls back to compute).
    """
    safe = ticker.replace(".", "-").upper()
    cached = _SIGNALS_BY_TICKER.get(safe)
    if cached is not None:
        return cached if not cached.empty else None
    path = PRECOMPUTED_DIR / f"{safe}.parquet"
    if not path.exists():
        # Cache the miss so we don't re-stat the filesystem
        _SIGNALS_BY_TICKER[safe] = pd.DataFrame()
        return None
    try:
        df = pd.read_parquet(path)
        if df.empty or "as_of_date" not in df.columns:
            _SIGNALS_BY_TICKER[safe] = pd.DataFrame()
            return None
        df = df.copy()
        df["as_of_date"] = pd.to_datetime(
            df["as_of_date"], errors="coerce").dt.date
        df = df.dropna(subset=["as_of_date"]).set_index("as_of_date")
        _SIGNALS_BY_TICKER[safe] = df
        return df
    except Exception:
        _SIGNALS_BY_TICKER[safe] = pd.DataFrame()
        return None


def load_precomputed_signals(ticker: str, as_of: date) -> Optional[dict]:
    """Return the pre-computed signal dict for (ticker, as_of) on cache
    HIT; None on MISS.

    Caller (screener.screen_instrument) checks for None + falls back to
    compute_all_signals(df) when missed. This preserves backward-compat
    for tickers / dates not yet pre-computed (e.g., production data
    refreshes).
    """
    df = _load_signals_parquet(ticker)
    if df is None or df.empty:
        return None
    if as_of not in df.index:
        return None
    row = df.loc[as_of]
    # Series.to_dict() returns numpy types for some columns; convert.
    raw = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    # Drop NaN values so consumer `.get(k, default)` returns default
    return {k: v for k, v in raw.items()
            if v is not None and not (isinstance(v, float) and pd.isna(v))}


def precompute_cache_info() -> dict:
    """Diagnostic info: which tickers have pre-computed parquets +
    how many dates each covers. Used by validators / dashboard."""
    out = {"dir_exists": PRECOMPUTED_DIR.exists(),
            "ticker_count": 0, "tickers": []}
    if not PRECOMPUTED_DIR.exists():
        return out
    files = sorted(PRECOMPUTED_DIR.glob("*.parquet"))
    out["ticker_count"] = len(files)
    out["tickers"] = [p.stem for p in files[:20]]
    return out


def _reset_signals_cache_for_tests():
    """Test-only helper: clear the module-level cache."""
    _SIGNALS_BY_TICKER.clear()


__all__ = [
    "PRECOMPUTED_DIR",
    "load_precomputed_signals",
    "precompute_cache_info",
    "_reset_signals_cache_for_tests",
]
