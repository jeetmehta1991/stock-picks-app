"""Batch 471 (2026-05-29) -- P13 pytrends search-volume producer.

Reads weekly Google Trends search-volume index per ticker
(`data_prefetch/pytrends/<TICKER>.parquet`) and emits per-(ticker, as_of)
volume z-score signals.

Source data layout (verified 2026-05-29 per CHECKLIST #99):
  cols: ticker, date (weekly cadence), search_volume_index (0..100), query_label
  coverage: 5+ years across 1417 tickers (per repo state 2026-05-29)

Signal emitted:
  search_volume_zscore_30d   -- z-score of last 4 weekly observations vs
                                 trailing 26-week (~6mo) baseline mean+std.
                                 Positive = unusually high search interest;
                                 negative = unusually low.

  search_volume_index_recent -- last observed weekly index (0..100). Used
                                 as raw context, not a fire condition.

Academic context:
  Da-Engelberg-Gao 2011 RFS "In Search of Attention" -- Google search-volume
  z-scores predict short-horizon stock returns (attention-induced demand
  effect ~2-4 weeks).

Returns empty dict when ticker file missing or insufficient history.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


_PYTRENDS_DIR = Path(__file__).parent.parent.parent / "data_prefetch" / "pytrends"


def compute_search_volume_signals(ticker: str, as_of: date) -> dict:
    """Compute search-volume signals for a ticker as-of a date.

    Returns dict with optional keys:
      - search_volume_index_recent:  int (most recent weekly index 0..100)
      - search_volume_zscore_30d:    float (last 4 weeks vs trailing 26 weeks)
      - search_volume_observations:  int (count of weekly observations used)

    Returns {} on data miss / insufficient history.
    """
    safe_ticker = ticker.replace(".", "-")
    path = _PYTRENDS_DIR / f"{safe_ticker}.parquet"
    if not path.exists():
        return {}
    try:
        df = pd.read_parquet(path)
    except Exception:
        return {}
    if df.empty or "date" not in df.columns \
            or "search_volume_index" not in df.columns:
        return {}
    try:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["d"] = df["date"].dt.date
        df = df[df["d"] <= as_of].sort_values("d")
    except Exception:
        return {}
    if df.empty:
        return {}
    values = pd.to_numeric(df["search_volume_index"], errors="coerce").dropna()
    if len(values) < 5:
        return {}
    last_idx = int(values.iloc[-1])
    # 4-week recent window vs trailing 26-week baseline (excluding the 4-week
    # recent window so the z-score is "recent vs prior baseline").
    if len(values) < 30:
        # Not enough history for a clean 4 vs 26 split; return raw index only.
        return {
            "search_volume_index_recent": last_idx,
            "search_volume_observations": int(len(values)),
        }
    recent = values.iloc[-4:]
    baseline = values.iloc[-30:-4]
    mu = float(baseline.mean())
    sd = float(baseline.std(ddof=1)) if len(baseline) > 1 else 0.0
    recent_mean = float(recent.mean())
    zscore = ((recent_mean - mu) / sd) if sd > 0 else 0.0
    return {
        "search_volume_index_recent": last_idx,
        "search_volume_zscore_30d":   round(float(zscore), 4),
        "search_volume_observations": int(len(values)),
    }
