"""Correlation cap + beta-neutralization helpers.

Batch 223 (2026-05-18 owner-approved research review Section C #2 + #4).

1. Correlation cap (Carver 2015 *Systematic Trading* Ch 10 Instrument
   Diversification Multiplier): at trade entry, refuse / halve position
   if |corr| > threshold with any open position. Closes the gap on
   our position-sizing axis - we size each position independently
   without correlation accounting.

2. Beta-neutralization helper (stub, opt-in via LIVE_TRADING_RULES
   beta_hedge_enabled flag). Computes the SPY-short overlay size
   targeting portfolio_gross_beta * 0.5. Owner decision required
   before enabling - changes the goal from absolute-return to
   alpha-vs-SPY framing.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

import numpy as np
import pandas as pd


def correlation_with_open_positions(
    candidate_ticker: str,
    ohlcv_dict: dict,
    open_tickers: Iterable[str],
    as_of: date,
    lookback_days: int = 60,
) -> dict:
    """Compute max absolute correlation between candidate and any open
    position over the lookback window.

    Returns dict:
      - max_abs_corr:        float in [0, 1] (max |corr| with any open pos)
      - max_corr_ticker:     str (ticker driving the max)
      - n_compared:          int (open positions with overlapping history)
      - any_correlated:      bool (max_abs_corr > 0.7)

    Returns max_abs_corr=0.0 when no open positions or no overlapping
    history (defensive - signals "no correlated peer found").
    """
    open_list = [t for t in open_tickers if t != candidate_ticker]
    if not open_list or candidate_ticker not in ohlcv_dict:
        return {"max_abs_corr": 0.0, "max_corr_ticker": None,
                "n_compared": 0, "any_correlated": False}
    cand_df = ohlcv_dict.get(candidate_ticker)
    if cand_df is None or cand_df.empty or "close" not in cand_df.columns:
        return {"max_abs_corr": 0.0, "max_corr_ticker": None,
                "n_compared": 0, "any_correlated": False}
    # Slice to as_of-or-before + lookback_days
    try:
        if hasattr(cand_df.index, "date"):
            cand_sliced = cand_df[cand_df.index.date <= as_of].tail(lookback_days + 1)
        else:
            cand_sliced = cand_df[cand_df.index <= as_of].tail(lookback_days + 1)
    except Exception:
        return {"max_abs_corr": 0.0, "max_corr_ticker": None,
                "n_compared": 0, "any_correlated": False}
    if len(cand_sliced) < 20:
        return {"max_abs_corr": 0.0, "max_corr_ticker": None,
                "n_compared": 0, "any_correlated": False}
    cand_ret = cand_sliced["close"].pct_change().dropna()
    max_corr = 0.0
    max_ticker = None
    n_compared = 0
    for t in open_list:
        pos_df = ohlcv_dict.get(t)
        if pos_df is None or pos_df.empty or "close" not in pos_df.columns:
            continue
        try:
            if hasattr(pos_df.index, "date"):
                pos_sliced = pos_df[pos_df.index.date <= as_of].tail(lookback_days + 1)
            else:
                pos_sliced = pos_df[pos_df.index <= as_of].tail(lookback_days + 1)
        except Exception:
            continue
        if len(pos_sliced) < 20:
            continue
        pos_ret = pos_sliced["close"].pct_change().dropna()
        # Align on common index
        common = pd.concat([cand_ret, pos_ret], axis=1, join="inner").dropna()
        if len(common) < 20:
            continue
        try:
            corr_val = float(common.iloc[:, 0].corr(common.iloc[:, 1]))
        except Exception:
            continue
        if pd.isna(corr_val):
            continue
        n_compared += 1
        abs_c = abs(corr_val)
        if abs_c > max_corr:
            max_corr = abs_c
            max_ticker = t
    return {
        "max_abs_corr":   round(max_corr, 4),
        "max_corr_ticker": max_ticker,
        "n_compared":     n_compared,
        "any_correlated": max_corr > 0.7,
    }


def correlation_size_multiplier(
    max_abs_corr: float,
    skip_threshold: float = 0.85,
    halve_threshold: float = 0.70,
) -> float:
    """Convert max correlation into a sizing multiplier.

    Logic (Carver 2015 IDM-inspired):
      - |corr| >= 0.85 -> 0.0 (skip; effectively block entry)
      - 0.70 <= |corr| < 0.85 -> 0.5 (halve position)
      - |corr| < 0.70 -> 1.0 (no adjustment)
    """
    if max_abs_corr >= skip_threshold:
        return 0.0
    if max_abs_corr >= halve_threshold:
        return 0.5
    return 1.0


def gross_portfolio_beta(
    open_positions: dict,
    ohlcv_dict: dict,
    benchmark: str = "SPY",
    as_of: Optional[date] = None,
    lookback_days: int = 252,
) -> float:
    """Compute gross portfolio beta vs benchmark.

    Sum of (position_weight * position_beta_vs_benchmark) across all
    open positions. Used by beta-neutralization overlay.

    Returns 0.0 on missing benchmark / no positions / insufficient history.
    """
    if not open_positions or benchmark not in ohlcv_dict:
        return 0.0
    bench_df = ohlcv_dict[benchmark]
    if bench_df is None or bench_df.empty:
        return 0.0
    try:
        if hasattr(bench_df.index, "date") and as_of is not None:
            bench_sliced = bench_df[bench_df.index.date <= as_of].tail(lookback_days + 1)
        else:
            bench_sliced = bench_df.tail(lookback_days + 1)
    except Exception:
        return 0.0
    if len(bench_sliced) < 60:
        return 0.0
    bench_ret = bench_sliced["close"].pct_change().dropna()
    bench_var = float(bench_ret.var())
    if bench_var <= 0:
        return 0.0
    total_weight = sum(open_positions.values())
    if total_weight <= 0:
        return 0.0
    gross_beta = 0.0
    for ticker, weight in open_positions.items():
        if ticker == benchmark or weight <= 0:
            continue
        pos_df = ohlcv_dict.get(ticker)
        if pos_df is None or pos_df.empty:
            continue
        try:
            if hasattr(pos_df.index, "date") and as_of is not None:
                pos_sliced = pos_df[pos_df.index.date <= as_of].tail(lookback_days + 1)
            else:
                pos_sliced = pos_df.tail(lookback_days + 1)
        except Exception:
            continue
        if len(pos_sliced) < 60:
            continue
        pos_ret = pos_sliced["close"].pct_change().dropna()
        common = pd.concat([pos_ret, bench_ret], axis=1, join="inner").dropna()
        if len(common) < 60:
            continue
        cov_val = float(common.iloc[:, 0].cov(common.iloc[:, 1]))
        beta = cov_val / bench_var
        gross_beta += (weight / total_weight) * beta
    return round(float(gross_beta), 4)
