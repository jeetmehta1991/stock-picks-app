"""Batch 503 (2026-05-31) -- M6 Path-2 YoY-growth earnings surprise.

Source: per CHECKLIST #77 + owner directive 2026-05-31 "resolve
everything else autonomously".
Queue row: EXECUTION_QUEUE.md item M6.

Path-2 ships per owner unblock decision: cheap path that switches the
"earnings surprise" definition from analyst-surprise (epsActual vs
epsEstimate, BLOCKED by data gap per Batch 493) to YoY-growth surprise
(this-Q EPS vs same-Q-prior-year EPS, AVAILABLE via existing
`backtest/signals/pead.py::compute_pead_signals` which already computes
`earnings_eps_yoy_growth` per Bernard-Thomas 1989 PEAD framework).

Bernard-Thomas predicts post-earnings-announcement drift in the
direction of the surprise. Without analyst estimates, YoY EPS growth
serves as a proxy: stocks reporting much-improved EPS vs same-quarter
prior year exhibit the same drift pattern (per Foster-Olsen-Shevlin
1984 "Earnings Releases, Anomalies, and the Behavior of Security
Returns").

Producer + sleeve strategies SCAFFOLDING; sleeves NOT registered in
ALL_STRATEGIES yet (per CLAUDE.md "ALL decisions need explicit owner
approval"). Owner one-line approval -> register both sleeves; cube
re-run then evaluates them empirically.

Sleeve strategies (defined here, registration deferred):
  pead_long_high_yoy_growth_only  : entry filter yoy_growth >= +0.05
  pead_short_negative_yoy_growth  : entry filter yoy_growth <= -0.05

The +/- 5% thresholds are owner-tunable per `Path-2 unblock #3` in the
queue note.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

import pandas as pd


# Owner-tunable thresholds (per PROJECT_PLAN.md PEAD framework)
YOY_GROWTH_LONG_THRESHOLD  =  0.05   # +5% YoY surprise -> long sleeve
YOY_GROWTH_SHORT_THRESHOLD = -0.05   # -5% YoY surprise -> short sleeve


def compute_yoy_surprise_signal(
    ticker: str,
    ohlcv_df: pd.DataFrame,
    as_of: date,
    long_threshold: float = YOY_GROWTH_LONG_THRESHOLD,
    short_threshold: float = YOY_GROWTH_SHORT_THRESHOLD,
    drift_window_days: int = 60,
) -> dict:
    """Compute YoY-growth-surprise signal dict.

    Reads `compute_pead_signals(ticker, ohlcv_df, as_of)` from pead.py
    + maps `earnings_eps_yoy_growth` into the high/negative surprise
    booleans the sleeve strategies use as entry filters.

    Returns dict with these keys (all optional; absent if data missing):
      earnings_eps_yoy_growth        : float (delegated from PEAD)
      days_since_last_earnings       : int (delegated from PEAD)
      within_pead_window             : bool (delegated from PEAD)
      yoy_surprise_high              : bool (yoy_growth >= long_threshold)
      yoy_surprise_negative          : bool (yoy_growth <= short_threshold)
      yoy_surprise_threshold_long    : float (the threshold used)
      yoy_surprise_threshold_short   : float (the threshold used)

    Empty input / missing PEAD data -> empty dict (no raise).
    """
    from backtest.signals.pead import compute_pead_signals
    pead = compute_pead_signals(
        ticker, ohlcv_df, as_of,
        drift_window_days=drift_window_days,
    )
    if not pead or "earnings_eps_yoy_growth" not in pead:
        return {}
    yoy = float(pead["earnings_eps_yoy_growth"])
    out = {
        "earnings_eps_yoy_growth":     round(yoy, 4),
        "yoy_surprise_high":           bool(yoy >= long_threshold),
        "yoy_surprise_negative":       bool(yoy <= short_threshold),
        "yoy_surprise_threshold_long": float(long_threshold),
        "yoy_surprise_threshold_short": float(short_threshold),
    }
    if "days_since_last_earnings" in pead:
        out["days_since_last_earnings"] = pead["days_since_last_earnings"]
    if "within_pead_window" in pead:
        out["within_pead_window"] = pead["within_pead_window"]
    return out


# Sleeve-strategy "definitions" -- NOT registered in ALL_STRATEGIES.
# Owner one-line approval converts these dicts into screener registrations.
SLEEVE_DEFINITIONS = {
    "pead_long_high_yoy_growth_only": {
        "direction": "long",
        "category":  "earnings",
        "entry_filter": (
            "compute_yoy_surprise_signal(ticker, df, as_of).get("
            "'yoy_surprise_high', False) AND compute_pead_signals(...)."
            "get('within_pead_window', False)"
        ),
        "rationale": (
            "Bernard-Thomas 1989 PEAD + Foster-Olsen-Shevlin 1984. Long the "
            "post-announcement drift for stocks with YoY EPS growth >= +5%. "
            "Drift window 60 trading days. Surrogate for analyst-surprise "
            "definition (M6 Path-1 BLOCKED by no estimate data per Batch 493)."
        ),
    },
    "pead_short_negative_yoy_growth": {
        "direction": "short",
        "category":  "earnings",
        "entry_filter": (
            "compute_yoy_surprise_signal(ticker, df, as_of).get("
            "'yoy_surprise_negative', False) AND compute_pead_signals(...)."
            "get('within_pead_window', False)"
        ),
        "rationale": (
            "Same Bernard-Thomas drift pattern, short side. YoY EPS growth "
            "<= -5% -> sustained negative drift through 60-day window."
        ),
    },
}


__all__ = [
    "YOY_GROWTH_LONG_THRESHOLD",
    "YOY_GROWTH_SHORT_THRESHOLD",
    "compute_yoy_surprise_signal",
    "SLEEVE_DEFINITIONS",
]
