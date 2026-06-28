"""Batch 537 (2026-06-01) -- OPT-B panel-style technical signal computation.

Source: per CHECKLIST #77 + owner directive 2026-06-01 "execute a b c d
sequentially".
Queue: EXECUTION_QUEUE.md OPT-B (cross-ticker vectorization).

# B1068 PIVOT #39 BLACKOUT WARNING (Council 168 2026-06-28):
# This panel does NOT emit the post-B609/B634/B721/B722 EMA-family
# signals: below_ema_{9,20,21,50,200} (122 consumer strategies),
# *_break_recent_5d (18 consumers), ema_{9_21,20_50,50_200}_bearish (4).
# DO NOT re-enable skip='ema_sma' in screener.py until this panel is
# extended to emit these signals OR the consumer strategies are migrated.
# The blackout caused 30% of PIVOT #39 SUSPECT SILENT strategies on B1063
# Phase 1 NVDA (sub-agent investigation report:
# output_audit/b1068_pivot_39_suspect_silent_investigation.md).
# Future panel-extension work tracked as B1069+ EXECUTION_QUEUE item.

CURRENT (per-ticker, technical.py):
    For each (ticker, as_of):
        df = ohlcv up to as_of for one ticker        # slice per call
        compute_rsi(df)   -> {rsi_2, rsi_9, rsi_14, rsi_21, ...}
        compute_ema_sma(df) -> {ema_8, ema_20, sma_50, ...}
        compute_returns(df) -> {pct_change_5d, ...}
        ... 29 indicator functions total per ticker per bar
    Result: 388 tickers x 29 functions x 1044 bars = ~11.7M function calls

PANEL (this module):
    For each as_of:
        close_panel = DataFrame[date_idx, ticker_cols] (full universe close)
        compute_rsi_panel(close_panel, as_of)  -> {ticker: rsi_dict}
        compute_ema_sma_panel(close_panel, as_of) -> {ticker: ema_dict}
        ...
    Result: 1044 bars x 5 panel functions = ~5K pandas vectorized ops

Each panel function computes the indicator for ALL tickers simultaneously
using one vectorized pandas operation (Series-of-Series math). For RSI:

    delta = close_panel.diff()              # vectorized across all cols
    gain  = delta.clip(lower=0).ewm(...)    # vectorized
    loss  = (-delta.clip(upper=0)).ewm(...) # vectorized
    rsi   = 100 - 100 / (1 + gain/loss)     # panel DataFrame of RSI values
    last_row = rsi.iloc[as_of_idx]          # Series indexed by ticker

Per-ticker math is identical (parity-guaranteed). Speedup comes from
removing the Python per-ticker function-call loop + amortising
pandas/numpy overhead across many tickers per call.

NOT YET WIRED into screen_universe. This module ships the
infrastructure + parity tests; wire-in is OPT-B Phase 6 follow-on.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def _safe_float(v, default: float) -> float:
    """Mirror technical._safe_float for parity."""
    try:
        if v is None or pd.isna(v):
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# RSI (4 periods: 2, 9, 14, 21) -- panel-vectorized Wilder smoothing
# ---------------------------------------------------------------------------

def compute_rsi_panel(
    close_panel: pd.DataFrame,
    as_of_idx: Optional[int] = None,
) -> dict[str, dict]:
    """Vectorized RSI computation across all tickers.

    Args:
        close_panel: DataFrame with rows=date_idx, cols=ticker_symbols,
                      values=close prices. Must have at least max(periods)+2
                      rows for the longest-period window.
        as_of_idx:   Row index to extract (default = last row). Allows
                      caller to slice without rebuilding the panel.

    Returns: {ticker: {rsi_2, rsi_2_oversold, ..., rsi_21_extreme_ob}}.
             Empty dict per ticker when insufficient history.

    Matches technical.compute_rsi output schema bit-for-bit (when
    `_HAS_TA` is False; same Wilder smoothing path).
    """
    if close_panel is None or close_panel.empty or len(close_panel) < 3:
        return {ticker: {} for ticker in close_panel.columns}
    if as_of_idx is None:
        as_of_idx = len(close_panel) - 1
    if as_of_idx < 1:
        return {ticker: {} for ticker in close_panel.columns}

    out: dict[str, dict] = {ticker: {} for ticker in close_panel.columns}
    delta = close_panel.diff()  # vectorized across all ticker columns
    for p in (2, 9, 14, 21):
        if as_of_idx < p + 1:
            continue
        # Wilder smoothing: alpha = 1/p, adjust=False -- matches
        # technical.compute_rsi exactly.
        gain = delta.clip(lower=0).ewm(alpha=1 / p, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / p, adjust=False).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - 100 / (1 + rs)
        # Extract just the two rows the per-ticker producer emits (last + prev)
        last_row = rsi.iloc[as_of_idx]
        prev_row = rsi.iloc[as_of_idx - 1]
        for ticker in close_panel.columns:
            v = _safe_float(last_row.get(ticker), 50.0)
            pv = _safe_float(prev_row.get(ticker), 50.0)
            out[ticker][f"rsi_{p}"]            = round(v, 2)
            out[ticker][f"rsi_{p}_oversold"]   = v < 30
            out[ticker][f"rsi_{p}_overbought"] = v > 70
            out[ticker][f"rsi_{p}_bullish"]    = v > 50
            out[ticker][f"rsi_{p}_rising"]     = v > pv
            out[ticker][f"rsi_{p}_extreme_os"] = v < 20
            out[ticker][f"rsi_{p}_extreme_ob"] = v > 80
    return out


# ---------------------------------------------------------------------------
# Simple Returns -- batch P10 5/10/20-day pct_change
# ---------------------------------------------------------------------------

def compute_simple_returns_panel(
    close_panel: pd.DataFrame,
    as_of_idx: Optional[int] = None,
) -> dict[str, dict]:
    """Vectorized 5/10/20-day pct_change across all tickers.

    Matches technical.compute_simple_returns output schema:
      pct_change_5d, pct_change_10d, pct_change_20d as floats in fractional
      units (0.025 = 2.5%).
    """
    if close_panel is None or close_panel.empty:
        return {ticker: {} for ticker in close_panel.columns}
    if as_of_idx is None:
        as_of_idx = len(close_panel) - 1
    out: dict[str, dict] = {ticker: {} for ticker in close_panel.columns}
    for lookback in (5, 10, 20):
        if as_of_idx < lookback:
            continue
        # pct_change vectorized: (close[as_of] - close[as_of-lookback]) / close[as_of-lookback]
        current = close_panel.iloc[as_of_idx]
        prior = close_panel.iloc[as_of_idx - lookback]
        denom = prior.replace(0, np.nan)
        ret = (current - prior) / denom
        for ticker in close_panel.columns:
            v = _safe_float(ret.get(ticker), 0.0)
            out[ticker][f"pct_change_{lookback}d"] = round(v, 4)
    return out


# ---------------------------------------------------------------------------
# EMA / SMA panel
# ---------------------------------------------------------------------------

def compute_ema_sma_panel(
    close_panel: pd.DataFrame,
    as_of_idx: Optional[int] = None,
) -> dict[str, dict]:
    """Vectorized EMA + SMA across all tickers.

    Matches `technical.compute_ema_sma` schema EXACTLY:
      Pairs: (9, 21), (20, 50), (50, 200)
      Keys per pair: ema_<f>_<s>_bullish, _golden_cross, _death_cross,
                     sma_<f>_<s>_bullish, _golden_cross,
                     price_above_ema_<f>, price_above_ema_<s>,
                     price_above_sma_<s>
    Schema-parity verified by test_batch538_parity_gate.
    """
    if close_panel is None or close_panel.empty:
        return {ticker: {} for ticker in close_panel.columns}
    if as_of_idx is None:
        as_of_idx = len(close_panel) - 1
    out: dict[str, dict] = {ticker: {} for ticker in close_panel.columns}
    last_close = close_panel.iloc[as_of_idx]
    prev_close = close_panel.iloc[as_of_idx - 1] if as_of_idx >= 1 else last_close

    # Pre-compute the unique spans we'll need (vectorized once each)
    spans_needed = {9, 21, 20, 50, 200}
    ema_levels: dict[int, tuple[pd.Series, pd.Series]] = {}
    sma_levels: dict[int, tuple[pd.Series, pd.Series]] = {}

    for span in spans_needed:
        if as_of_idx < span + 1:
            continue
        ema_full = close_panel.ewm(span=span, adjust=False).mean()
        ema_levels[span] = (ema_full.iloc[as_of_idx],
                            ema_full.iloc[as_of_idx - 1])
        sma_full = close_panel.rolling(span).mean()
        sma_levels[span] = (sma_full.iloc[as_of_idx],
                            sma_full.iloc[as_of_idx - 1])

    for fast, slow in ((9, 21), (20, 50), (50, 200)):
        if slow not in ema_levels or fast not in ema_levels:
            continue
        if slow not in sma_levels or fast not in sma_levels:
            continue
        ef_last, ef_prev = ema_levels[fast]
        es_last, es_prev = ema_levels[slow]
        sf_last, sf_prev = sma_levels[fast]
        ss_last, ss_prev = sma_levels[slow]
        for ticker in close_panel.columns:
            efv = _safe_float(ef_last.get(ticker), 0.0)
            esv = _safe_float(es_last.get(ticker), 0.0)
            efp = _safe_float(ef_prev.get(ticker), 0.0)
            esp = _safe_float(es_prev.get(ticker), 0.0)
            sfv = _safe_float(sf_last.get(ticker), 0.0)
            ssv = _safe_float(ss_last.get(ticker), 0.0)
            sfp = _safe_float(sf_prev.get(ticker), 0.0)
            ssp = _safe_float(ss_prev.get(ticker), 0.0)
            close = _safe_float(last_close.get(ticker), 0.0)
            sigs = out[ticker]
            sigs[f"ema_{fast}_{slow}_bullish"]      = efv > esv
            sigs[f"ema_{fast}_{slow}_golden_cross"] = efv > esv and efp <= esp
            sigs[f"ema_{fast}_{slow}_death_cross"]  = efv < esv and efp >= esp
            sigs[f"sma_{fast}_{slow}_bullish"]      = sfv > ssv
            sigs[f"sma_{fast}_{slow}_golden_cross"] = sfv > ssv and sfp <= ssp
            sigs[f"price_above_ema_{fast}"]         = close > efv
            sigs[f"price_above_ema_{slow}"]         = close > esv
            sigs[f"price_above_sma_{slow}"]         = close > ssv
    return out


# ---------------------------------------------------------------------------
# Aggregator: all panel signals for a given as_of
# ---------------------------------------------------------------------------

def compute_panel_signals_for_as_of(
    close_panel: pd.DataFrame,
    as_of_idx: Optional[int] = None,
) -> dict[str, dict]:
    """Run all available panel indicators + merge into per-ticker dicts.

    Currently supports the SUBSET of compute_all_signals that's
    cleanly vectorizable: RSI (4 periods), simple_returns (3 windows),
    EMA (5 spans), SMA (3 periods). ~50 keys per ticker out of the
    ~270 total signals.

    Wire-in plan (OPT-B Phase 6 follow-on):
      1. screen_universe pre-builds close_panel from per-ticker OHLCV cache.
      2. Calls compute_panel_signals_for_as_of once per as_of.
      3. For each ticker, merges panel signals into the per-ticker
         signals dict BEFORE compute_all_signals runs the remaining
         (non-vectorized) indicators.
      4. compute_all_signals skips RSI/EMA/SMA/returns (already populated).

    Expected speedup: ~50 of 270 signals vectorized = ~20% reduction in
    per-bar compute time, ON TOP of OPT-A. Future Phase 7+ extends to
    more indicators (Bollinger, ATR, MACD all naturally panel-compatible).
    """
    if close_panel is None or close_panel.empty:
        return {}
    if as_of_idx is None:
        as_of_idx = len(close_panel) - 1
    out: dict[str, dict] = {ticker: {} for ticker in close_panel.columns}
    for fn in (compute_rsi_panel, compute_simple_returns_panel,
                compute_ema_sma_panel):
        try:
            partial = fn(close_panel, as_of_idx=as_of_idx)
        except Exception:
            continue
        for ticker, sigs in partial.items():
            out[ticker].update(sigs)
    return out


__all__ = [
    "compute_rsi_panel",
    "compute_simple_returns_panel",
    "compute_ema_sma_panel",
    "compute_panel_signals_for_as_of",
]
