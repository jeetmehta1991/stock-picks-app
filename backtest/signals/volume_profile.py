"""Volume Profile / VPVR (Volume Profile Visible Range) — Track A
batch 233 parallel-safe module.

Batch 233 (2026-05-18 owner-approved deferred-items implementation;
parallel-safe with Batch 225 final rerun). Addresses the research
review item #7 (Volume Profile / VPVR / Point of Control).

Volume profile / Market Profile (Steidlmayer 1985 *Markets and Market
Logic*) characterizes price by VOLUME-AT-PRICE rather than the typical
time-series view. The key institutional reference levels are:

  - **Point of Control (POC)**: price bin with the highest volume in
    the period. Acts as a strong magnetic attractor — price tends to
    return to POC.
  - **Value Area (VA)**: contiguous price range containing 70% of
    period volume. Defined by Value Area High (VAH) and Value Area
    Low (VAL).
  - **Volume Nodes**: high-volume price levels = support/resistance
    where institutional activity accumulated.
  - **Low-Volume Nodes (LVN)**: price levels with little volume — price
    moves through them quickly with little reaction.

Practitioner sources:
  - Steidlmayer 1985 *Markets and Market Logic* (foundational)
  - Dalton-Jones-Dalton 1990 *Mind Over Markets* (Market Profile manual)
  - TradingSim 2026 Volume Profile Trading Strategies Guide
  - QuantVPS 2024 volume-profile institutional reference

Daily-bar approximation: true volume profile uses INTRADAY bars (5-min
or 30-min "TPO" letters) to build the price/volume distribution.
Daily-bar approximation: distribute each day's volume across the
day's range (assume uniform), accumulate over period_lookback days,
identify POC/VAH/VAL bins.

Strategy registration is deferred to post-Batch-225 follow-on batch.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def compute_volume_profile(
    df: pd.DataFrame,
    lookback_days: int = 60,
    n_bins: int = 40,
    value_area_pct: float = 0.70,
) -> dict:
    """Compute volume profile signals from daily OHLCV.

    Inputs:
      df:             DataFrame indexed by date with high / low / close /
                       volume columns
      lookback_days:  rolling window for profile construction (default 60)
      n_bins:         number of price bins to discretize the range (default 40)
      value_area_pct: contiguous-bin fraction defining Value Area (default 0.70)

    Returns dict:
      - vp_poc:                float - Point of Control (highest volume bin midprice)
      - vp_value_area_high:    float - upper bound of 70pct volume range
      - vp_value_area_low:     float - lower bound of 70pct volume range
      - vp_close_above_poc:    bool  - today's close above POC
      - vp_close_below_poc:    bool  - today's close below POC
      - vp_in_value_area:      bool  - today's close within VAH/VAL
      - vp_close_near_poc_pct: float - abs distance from POC as pct of POC
      - vp_naked_poc_distance: float - distance to nearest higher-period
                                       untested POC (if available)

    Returns empty dict on insufficient data (need >= lookback_days bars).
    """
    if df is None or df.empty or len(df) < lookback_days:
        return {}
    required = {"high", "low", "close", "volume"}
    if not required.issubset(set(df.columns)):
        return {}
    try:
        window = df.tail(lookback_days)
        # Discretize price range
        price_lo = float(window["low"].min())
        price_hi = float(window["high"].max())
        if price_hi <= price_lo:
            return {}
        bin_edges = np.linspace(price_lo, price_hi, n_bins + 1)
        bin_midpoints = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        bin_volumes = np.zeros(n_bins)
        # Distribute each day's volume across its price range uniformly
        for _, row in window.iterrows():
            row_hi = float(row["high"])
            row_lo = float(row["low"])
            row_vol = float(row["volume"])
            if row_hi <= row_lo or row_vol <= 0:
                continue
            # Find bins overlapping [row_lo, row_hi]
            for i in range(n_bins):
                b_lo, b_hi = bin_edges[i], bin_edges[i + 1]
                # Overlap fraction
                overlap_lo = max(b_lo, row_lo)
                overlap_hi = min(b_hi, row_hi)
                if overlap_hi > overlap_lo:
                    frac = (overlap_hi - overlap_lo) / (row_hi - row_lo)
                    bin_volumes[i] += row_vol * frac
        # POC = bin with max volume
        poc_idx = int(np.argmax(bin_volumes))
        poc = float(bin_midpoints[poc_idx])
        # Value Area: expand symmetrically from POC until contiguous bins
        # contain value_area_pct of total volume
        total_vol = float(bin_volumes.sum())
        if total_vol <= 0:
            return {}
        target_vol = total_vol * value_area_pct
        included = {poc_idx}
        running_vol = float(bin_volumes[poc_idx])
        up_idx = poc_idx + 1
        dn_idx = poc_idx - 1
        while running_vol < target_vol and (up_idx < n_bins or dn_idx >= 0):
            up_vol = float(bin_volumes[up_idx]) if up_idx < n_bins else -1.0
            dn_vol = float(bin_volumes[dn_idx]) if dn_idx >= 0 else -1.0
            if up_vol >= dn_vol and up_idx < n_bins:
                included.add(up_idx)
                running_vol += up_vol
                up_idx += 1
            elif dn_idx >= 0:
                included.add(dn_idx)
                running_vol += dn_vol
                dn_idx -= 1
            else:
                break
        va_lo_idx = min(included)
        va_hi_idx = max(included)
        vah = float(bin_edges[va_hi_idx + 1])
        val_ = float(bin_edges[va_lo_idx])
        close = float(df["close"].iloc[-1])
        out = {
            "vp_poc":                   round(poc, 4),
            "vp_value_area_high":       round(vah, 4),
            "vp_value_area_low":        round(val_, 4),
            "vp_close_above_poc":       close > poc,
            "vp_close_below_poc":       close < poc,
            "vp_in_value_area":         (val_ <= close <= vah),
            "vp_close_near_poc_pct":    round(abs(close - poc) / poc, 4) if poc > 0 else 0.0,
            "vp_above_value_area":      close > vah,
            "vp_below_value_area":      close < val_,
        }
        return out
    except Exception:
        return {}


def compute_period_pocs(
    df: pd.DataFrame,
    period_lookback: int = 252,
    n_periods: int = 6,
    n_bins: int = 40,
) -> list:
    """Compute period POCs (e.g. last 6 months) for naked-POC detection.

    Returns list of POC prices (chronological, oldest first). Useful for
    finding "naked" POCs that have not been retested - acts as magnetic
    levels for future price action.

    Defensive: returns [] when input too short.
    """
    if df is None or df.empty or len(df) < period_lookback:
        return []
    window = df.tail(period_lookback)
    chunk_size = max(1, len(window) // n_periods)
    pocs = []
    for i in range(n_periods):
        chunk = window.iloc[i * chunk_size: (i + 1) * chunk_size]
        if len(chunk) < 5:
            continue
        try:
            sub_signals = compute_volume_profile(chunk, lookback_days=len(chunk),
                                                   n_bins=n_bins)
            poc = sub_signals.get("vp_poc")
            if poc is not None:
                pocs.append(poc)
        except Exception:
            continue
    return pocs
