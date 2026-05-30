"""Batch 497 (2026-05-31) -- Item 5 Tier B cube cell metrics expansion.

Source: per CHECKLIST #77 + EXECUTION_QUEUE.md item 5.
Companion to: backtest/results/cube_populator.py (Tier A landed in
Batch 489).

Tier B metrics SLICE existing trade_log columns to surface conditional
win-rates without re-running the cube. Each metric reads only columns
the writer already emits (verified against `output_batch395_final/
trade_log.csv` 46-col schema as of Batch 497).

Outputs per cell (all optional; emitted only when source column is
present + has >=2 distinct values, else gracefully omitted):

  wr_with_smart_money         : win-rate when smart_money_score > 0
  wr_without_smart_money      : win-rate when smart_money_score <= 0
  wr_lift_smart_money         : wr_with - wr_without (the criterion-7
                                signal that DEC-426 wants)
  n_with_smart_money / n_without_smart_money

  wr_by_days_to_earnings_band : dict {band: wr} where band in
                                ('<=5d', '6-15d', '16-45d', '>45d',
                                 'unknown')
  wr_by_confidence_tier       : dict {tier: wr}
  wr_by_macro_score_band      : dict {'negative','neutral','positive'}
  wr_by_aaii_signal           : dict {signal_value: wr}
  wr_by_circuit_breaker_level : dict {level: wr}
  wr_by_regime                : dict {regime: wr}

Future consumer: cube populator wires this into `compute_cell_metrics`
once Batch 489 merge lands (cube populator already returns a dict;
just `out.update(compute_tier_b_metrics(trades))`).

Why split from Batch 489: avoids merge conflict on cube_populator.py
while 489 awaits CI. This module is standalone + tested in isolation;
the wire-in is a follow-on one-liner.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Small primitive: safe win-rate from a boolean / 0-1 Series
# ---------------------------------------------------------------------------

def _safe_wr(series: pd.Series) -> Optional[float]:
    """Return win-rate as a 0..1 float, or None if series is empty."""
    if series is None or len(series) == 0:
        return None
    arr = series.dropna()
    if len(arr) == 0:
        return None
    return float((arr.astype(float) > 0.0).mean())


# ---------------------------------------------------------------------------
# Smart-money slice -- criterion 7 of the 11 PASSING_CRITERIA
# ---------------------------------------------------------------------------

def compute_smart_money_slice(trades: pd.DataFrame) -> dict:
    """Slice WR by smart_money_score sign.

    Per CLAUDE.md criterion 7: smart money lift = win-rate delta >= 3pp.
    This function exposes the lift so the cube verdict pipeline can
    evaluate it per cell.
    """
    if trades is None or trades.empty:
        return {}
    if "smart_money_score" not in trades.columns or \
       "win" not in trades.columns:
        return {}
    sm = pd.to_numeric(trades["smart_money_score"], errors="coerce")
    with_sm  = trades[sm > 0]
    without_sm = trades[sm <= 0]
    wr_w = _safe_wr(with_sm["win"])
    wr_wo = _safe_wr(without_sm["win"])
    out: dict = {
        "n_with_smart_money":    int(len(with_sm)),
        "n_without_smart_money": int(len(without_sm)),
    }
    if wr_w is not None:
        out["wr_with_smart_money"] = round(wr_w, 4)
    if wr_wo is not None:
        out["wr_without_smart_money"] = round(wr_wo, 4)
    if wr_w is not None and wr_wo is not None:
        out["wr_lift_smart_money"] = round(wr_w - wr_wo, 4)
    return out


# ---------------------------------------------------------------------------
# Days-to-earnings bucketing
# ---------------------------------------------------------------------------

def _days_to_earnings_band(d) -> str:
    if pd.isna(d):
        return "unknown"
    try:
        di = int(d)
    except (TypeError, ValueError):
        return "unknown"
    if di < 0:
        return "post_earnings"
    if di <= 5:
        return "0_to_5d"
    if di <= 15:
        return "6_to_15d"
    if di <= 45:
        return "16_to_45d"
    return "over_45d"


def compute_days_to_earnings_slice(trades: pd.DataFrame) -> dict:
    if trades is None or trades.empty:
        return {}
    if "days_to_earnings" not in trades.columns or \
       "win" not in trades.columns:
        return {}
    trades = trades.copy()
    trades["__band"] = trades["days_to_earnings"].apply(_days_to_earnings_band)
    bands = {}
    for band, sub in trades.groupby("__band", sort=False):
        wr = _safe_wr(sub["win"])
        if wr is not None:
            bands[str(band)] = {"wr": round(wr, 4), "n": int(len(sub))}
    return {"wr_by_days_to_earnings_band": bands} if bands else {}


# ---------------------------------------------------------------------------
# Generic group-by slice (used by all the remaining slices)
# ---------------------------------------------------------------------------

def _slice_by_col(
    trades: pd.DataFrame, col: str, key_in_out: str, min_per_group: int = 5,
) -> dict:
    """Generic 'group by `col`, emit dict {value: {wr, n}}' helper.

    Skips groups with fewer than `min_per_group` trades (avoids noisy
    cells in the by-group dict).
    """
    if trades is None or trades.empty:
        return {}
    if col not in trades.columns or "win" not in trades.columns:
        return {}
    groups: dict[str, dict] = {}
    for value, sub in trades.groupby(col, sort=False, dropna=False):
        if len(sub) < min_per_group:
            continue
        wr = _safe_wr(sub["win"])
        if wr is None:
            continue
        key = str(value) if not pd.isna(value) else "unknown"
        groups[key] = {"wr": round(wr, 4), "n": int(len(sub))}
    return {key_in_out: groups} if groups else {}


def compute_confidence_tier_slice(trades: pd.DataFrame) -> dict:
    return _slice_by_col(trades, "confidence_tier",
                          "wr_by_confidence_tier")


def compute_regime_slice(trades: pd.DataFrame) -> dict:
    return _slice_by_col(trades, "regime", "wr_by_regime")


def compute_aaii_signal_slice(trades: pd.DataFrame) -> dict:
    return _slice_by_col(trades, "aaii_signal", "wr_by_aaii_signal")


def compute_circuit_breaker_slice(trades: pd.DataFrame) -> dict:
    return _slice_by_col(trades, "circuit_breaker_level",
                          "wr_by_circuit_breaker_level")


def compute_sector_slice(trades: pd.DataFrame) -> dict:
    return _slice_by_col(trades, "sector", "wr_by_sector",
                          min_per_group=5)


# ---------------------------------------------------------------------------
# Macro score bucketing
# ---------------------------------------------------------------------------

def _macro_score_band(s) -> str:
    if pd.isna(s):
        return "unknown"
    try:
        sf = float(s)
    except (TypeError, ValueError):
        return "unknown"
    if sf < 0:
        return "negative"
    if sf > 0:
        return "positive"
    return "neutral"


def compute_macro_score_slice(trades: pd.DataFrame) -> dict:
    if trades is None or trades.empty:
        return {}
    if "macro_score" not in trades.columns or "win" not in trades.columns:
        return {}
    trades = trades.copy()
    trades["__band"] = trades["macro_score"].apply(_macro_score_band)
    bands = {}
    for band, sub in trades.groupby("__band", sort=False):
        wr = _safe_wr(sub["win"])
        if wr is not None:
            bands[str(band)] = {"wr": round(wr, 4), "n": int(len(sub))}
    return {"wr_by_macro_score_band": bands} if bands else {}


# ---------------------------------------------------------------------------
# Top-level aggregator
# ---------------------------------------------------------------------------

def compute_tier_b_metrics(trades: pd.DataFrame) -> dict:
    """Run every Tier B slice and merge into a single flat dict.

    Each slice degrades gracefully when its source column is absent so
    older trade_log files with smaller schemas still get partial
    results.
    """
    out: dict = {}
    out.update(compute_smart_money_slice(trades))
    out.update(compute_days_to_earnings_slice(trades))
    out.update(compute_confidence_tier_slice(trades))
    out.update(compute_regime_slice(trades))
    out.update(compute_aaii_signal_slice(trades))
    out.update(compute_circuit_breaker_slice(trades))
    out.update(compute_macro_score_slice(trades))
    out.update(compute_sector_slice(trades))
    return out


__all__ = [
    "compute_smart_money_slice",
    "compute_days_to_earnings_slice",
    "compute_confidence_tier_slice",
    "compute_regime_slice",
    "compute_aaii_signal_slice",
    "compute_circuit_breaker_slice",
    "compute_macro_score_slice",
    "compute_sector_slice",
    "compute_tier_b_metrics",
]
