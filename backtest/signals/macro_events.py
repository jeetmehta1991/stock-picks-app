"""Macro event signals + pre-FOMC drift.

Batch 224 (2026-05-18 owner-approved research review Top-10 #9).

Pre-FOMC Drift: Lucca-Moench 2015 JF "The Pre-FOMC Announcement Drift"
documents +50bps/yr alpha concentrating in 24h preceding FOMC
announcements (1994-2011, replicated 2012-2015). Refined by
Cieslak-Pang 2024 conditional on yield-curve slope + VIX term structure.

Batch 191 currently SUPPRESSES trading around FOMC (event_window
d-1 + d=0). The research review argues this is the wrong direction
for the LONG sleeve - we should TRADE INTO the pre-FOMC window, not
out of it.

Implementation: this module emits pre_fomc_d1 / pre_fomc_d0 signals
into the per-ticker signals dict by reading the macro event calendar.
Pre-FOMC long strategy reads these + filters by quality (xs_momentum
top decile + 200-EMA gate). The engine's event suppression check
allows tagged-pre-fomc strategies to fire via the
STRATEGIES_BYPASS_EVENT_SUPPRESSION set (config.py).
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


_FOMC_CALENDAR_PATH = (
    Path(__file__).parent.parent.parent
    / "data_prefetch" / "fred" / "fomc_calendar.parquet"
)
_FOMC_CACHE: Optional[pd.DataFrame] = None


def _load_fomc_calendar() -> pd.DataFrame:
    """Lazy-load FOMC announcement-date calendar.

    Schema (typical FRED FOMC calendar): one row per FOMC meeting,
    columns include 'date' (announcement date) and optionally
    'meeting_type', 'rate_decision'. Returns empty DataFrame on miss.
    """
    global _FOMC_CACHE
    if _FOMC_CACHE is not None:
        return _FOMC_CACHE
    if not _FOMC_CALENDAR_PATH.exists():
        _FOMC_CACHE = pd.DataFrame()
        return _FOMC_CACHE
    try:
        df = pd.read_parquet(_FOMC_CALENDAR_PATH)
        # Normalize date column
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df.dropna(subset=["date"])
        _FOMC_CACHE = df
    except Exception:
        _FOMC_CACHE = pd.DataFrame()
    return _FOMC_CACHE


def compute_pre_fomc_signals(as_of: date) -> dict:
    """Emit pre-FOMC proximity signals for the current trading day.

    Reads the FOMC calendar and returns:
      - pre_fomc_d1: bool (next FOMC announcement is tomorrow,
        i.e. we are on the pre-announcement day)
      - pre_fomc_d0: bool (FOMC is today)
      - pre_fomc_window: bool (pre_fomc_d1 OR pre_fomc_d0)
      - days_until_fomc: int (positive = days until next; -1 if no upcoming)

    Returns empty dict when FOMC calendar unavailable.
    """
    cal = _load_fomc_calendar()
    if cal.empty or "date" not in cal.columns:
        return {}
    upcoming = cal[cal["date"] >= as_of].sort_values("date")
    if upcoming.empty:
        return {}
    next_fomc = upcoming.iloc[0]["date"]
    delta = (next_fomc - as_of).days
    return {
        "pre_fomc_d1":      delta == 1,
        "pre_fomc_d0":      delta == 0,
        "pre_fomc_window":  delta in (0, 1),
        "days_until_fomc":  int(delta),
    }


# B748b (2026-06-13 owner-approved): `compute_recent_8k_signal` DELETED.
# Per B745 finding-grade audit: zero consumers across the registry (no
# strategy in ALL_STRATEGIES consumed `recent_8k_filed` or `days_since_8k`).
# Codebase already flagged the producer as suspect at screener.py:3091.
# Data path (data_prefetch/sec_edgar/8_K/) was also 0 rows; producer was
# both data-empty AND consumer-empty (genuine orphan). Source preserved
# in git history at commit de0d7b522~1 if revival ever needed.
