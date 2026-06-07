"""Chart patterns module — Phase 1C+ Wave 1 (DEC-355-362).

Batch 242 (2026-05-19 owner-approved Phase 1C+ implementation; parallel-safe
with Phase 1A-alpha 5-batch rerun in flight - NEW file, no engine touch).

Daily-bar pattern detection for classical chart patterns documented across
the technical analysis literature. Each detector takes a price-history
DataFrame (OHLC + volume) and returns a signals dict that the strategy
registry consumes.

Patterns implemented (DEC-355-362):
  1. Head and Shoulders (top + bottom inverse) - Edwards-Magee 1948
     "Technical Analysis of Stock Trends"; Bulkowski 2005 "Encyclopedia
     of Chart Patterns" Sharpe 0.7-1.1 with neckline-break entry
  2. Double Top / Double Bottom - same source; Sharpe 0.5-0.9
  3. Cup and Handle - O'Neil 1988 "How to Make Money in Stocks";
     CANSLIM methodology canonical, ~25-30% gain on handle breakout
  4. Bull Flag / Bear Flag - Edwards-Magee + Bulkowski; high-tight-flag
     post-consolidation breakout ~38% historical median
  5. Ascending / Descending / Symmetric Triangle - Bulkowski 2005;
     breakout direction follows trend ~70% of time

Each pattern detector:
  - Returns a dict with pattern_<name>_detected (bool), magnitude (float
    expressed as % of price), confirmation_level (float price), and
    direction (long/short).
  - Daily-bar approximation: true patterns often need intraday/multi-day
    confirmation. We use closing prices with rolling-window swing detection
    + volume confirmation thresholds calibrated for daily bars.

Strategy registration deferred to post-Phase-1A-alpha commit (touches
screener.py ALL_STRATEGIES dict). This module provides the detection +
helper functions consumed by strategy registrations.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def _find_swings(close: pd.Series, window: int = 5) -> tuple[list[int], list[int]]:
    """Find local maxima (highs) and minima (lows) in close series.

    Uses a window-based comparator: a point is a swing high if it's the
    maximum within +/- window bars, similarly for swing low.

    Returns: (highs_idx, lows_idx) — index positions into the series.
    """
    if close is None or len(close) < 2 * window + 1:
        return [], []
    highs, lows = [], []
    arr = close.values
    n = len(arr)
    for i in range(window, n - window):
        left = arr[i - window: i]
        right = arr[i + 1: i + window + 1]
        if arr[i] > left.max() and arr[i] > right.max():
            highs.append(i)
        elif arr[i] < left.min() and arr[i] < right.min():
            lows.append(i)
    return highs, lows


def detect_head_and_shoulders(
    df: pd.DataFrame,
    window: int = 5,
    shoulder_tol: float = 0.03,
    head_min: float = 0.02,
    lookback: int = 60,
) -> dict:
    """Head-and-shoulders top + inverse-bottom detector (DEC-355).

    A H&S top requires 3 consecutive swing highs where the middle is the
    highest (head) and the outer two (shoulders) are roughly symmetric
    in height (within shoulder_tol). The neckline = avg of the two lows
    between shoulders + head. Entry signal = close breaks below neckline
    (bearish for top) or above (bullish for inverse-bottom).

    Returns dict:
      head_shoulders_top_detected:    bool
      head_shoulders_top_neckline:    float
      head_shoulders_bottom_detected: bool (inverse)
      head_shoulders_bottom_neckline: float
      head_shoulders_magnitude_pct:   float (height of head as % of neckline)
    """
    if df is None or len(df) < lookback:
        return {}
    win = df.tail(lookback)
    close = win["close"]
    highs, lows = _find_swings(close, window=window)
    out = {"head_shoulders_top_detected": False,
           "head_shoulders_bottom_detected": False}
    # Need at least 3 swing highs for top, 3 lows for bottom
    if len(highs) >= 3:
        # Check the most recent 3 highs
        h1, h2, h3 = highs[-3], highs[-2], highs[-1]
        v1, v2, v3 = close.iloc[h1], close.iloc[h2], close.iloc[h3]
        # Middle (head) must be highest
        if v2 > v1 and v2 > v3:
            # Shoulders roughly symmetric
            shoulder_diff = abs(v1 - v3) / max(v1, v3) if max(v1, v3) > 0 else 1.0
            head_height = (v2 - max(v1, v3)) / max(v1, v3) if max(v1, v3) > 0 else 0
            if shoulder_diff < shoulder_tol and head_height >= head_min:
                # Neckline = avg of lows between h1+h2 and h2+h3
                lows_between = [l for l in lows if h1 < l < h3]
                if lows_between:
                    neckline = float(close.iloc[lows_between].mean())
                    out["head_shoulders_top_detected"] = True
                    out["head_shoulders_top_neckline"] = round(neckline, 4)
                    out["head_shoulders_magnitude_pct"] = round(head_height, 4)
    if len(lows) >= 3:
        l1, l2, l3 = lows[-3], lows[-2], lows[-1]
        v1, v2, v3 = close.iloc[l1], close.iloc[l2], close.iloc[l3]
        if v2 < v1 and v2 < v3:
            shoulder_diff = abs(v1 - v3) / max(v1, v3) if max(v1, v3) > 0 else 1.0
            head_depth = (min(v1, v3) - v2) / min(v1, v3) if min(v1, v3) > 0 else 0
            if shoulder_diff < shoulder_tol and head_depth >= head_min:
                highs_between = [h for h in highs if l1 < h < l3]
                if highs_between:
                    neckline = float(close.iloc[highs_between].mean())
                    out["head_shoulders_bottom_detected"] = True
                    out["head_shoulders_bottom_neckline"] = round(neckline, 4)
                    if "head_shoulders_magnitude_pct" not in out:
                        out["head_shoulders_magnitude_pct"] = round(head_depth, 4)
    return out


def detect_double_top_bottom(
    df: pd.DataFrame,
    window: int = 5,
    peak_tol: float = 0.02,
    min_separation: int = 10,
    lookback: int = 60,
) -> dict:
    """Double-top / double-bottom detector (DEC-356).

    Double top: 2 consecutive swing highs at roughly the same level
    (within peak_tol), separated by min_separation bars and an
    intervening trough. Confirmation = close breaks below the trough
    (bearish for top) or above the peak (bullish for bottom).
    """
    if df is None or len(df) < lookback:
        return {}
    win = df.tail(lookback)
    close = win["close"]
    highs, lows = _find_swings(close, window=window)
    out = {"double_top_detected": False, "double_bottom_detected": False}
    if len(highs) >= 2:
        h1, h2 = highs[-2], highs[-1]
        if (h2 - h1) >= min_separation:
            v1, v2 = close.iloc[h1], close.iloc[h2]
            diff = abs(v1 - v2) / max(v1, v2) if max(v1, v2) > 0 else 1.0
            if diff < peak_tol:
                # Find trough between
                lows_between = [l for l in lows if h1 < l < h2]
                if lows_between:
                    trough = float(close.iloc[lows_between].min())
                    out["double_top_detected"] = True
                    out["double_top_peak"] = round(max(v1, v2), 4)
                    out["double_top_neckline"] = round(trough, 4)
    if len(lows) >= 2:
        l1, l2 = lows[-2], lows[-1]
        if (l2 - l1) >= min_separation:
            v1, v2 = close.iloc[l1], close.iloc[l2]
            diff = abs(v1 - v2) / max(v1, v2) if max(v1, v2) > 0 else 1.0
            if diff < peak_tol:
                highs_between = [h for h in highs if l1 < h < l2]
                if highs_between:
                    peak = float(close.iloc[highs_between].max())
                    out["double_bottom_detected"] = True
                    out["double_bottom_trough"] = round(min(v1, v2), 4)
                    out["double_bottom_neckline"] = round(peak, 4)
    return out


def detect_cup_and_handle(
    df: pd.DataFrame,
    lookback: int = 120,
    cup_depth_min: float = 0.10,
    cup_depth_max: float = 0.35,
    handle_pct_max: float = 0.15,
) -> dict:
    """Cup-and-handle detector (DEC-357). O'Neil CANSLIM canonical pattern.

    Cup: U-shaped retracement of 10-35% from prior high. Right rim
    approximately = left rim height.
    Handle: shallow consolidation after right rim, retracement <15%.
    Entry: close breaks above handle high with volume confirmation.

    Daily-bar approximation: requires ~120 days of history for cup
    formation. Handle is the most recent 5-20 days post-rim.
    """
    if df is None or len(df) < lookback:
        return {}
    win = df.tail(lookback)
    close = win["close"]
    high = win["high"]
    n = len(win)
    # Cup boundaries: left rim = max in first 25% of window; right rim
    # = max in last 25%; cup low = min in middle 50%.
    left_rim_end = n // 4
    right_rim_start = (3 * n) // 4
    mid_start, mid_end = left_rim_end, right_rim_start
    left_rim = float(high.iloc[:left_rim_end].max())
    right_rim = float(high.iloc[right_rim_start:].max())
    cup_low = float(close.iloc[mid_start:mid_end].min())
    rim = max(left_rim, right_rim)
    if rim <= 0:
        return {}
    cup_depth = (rim - cup_low) / rim
    rim_diff = abs(left_rim - right_rim) / rim
    if not (cup_depth_min <= cup_depth <= cup_depth_max and rim_diff < 0.05):
        return {"cup_handle_detected": False}
    # Handle: post-rim consolidation (last 5-20 days)
    handle_window = win.tail(20)
    handle_high = float(handle_window["high"].max())
    handle_low = float(handle_window["low"].min())
    handle_pullback = (handle_high - handle_low) / handle_high if handle_high > 0 else 1.0
    handle_detected = handle_pullback < handle_pct_max
    return {
        "cup_handle_detected":       handle_detected,
        "cup_handle_rim":            round(rim, 4),
        "cup_handle_depth_pct":      round(cup_depth, 4),
        "cup_handle_breakout_level": round(handle_high, 4),
    }


def detect_flag(
    df: pd.DataFrame,
    flagpole_lookback: int = 20,
    flag_lookback: int = 10,
    flagpole_min_move: float = 0.10,
    flag_max_pullback: float = 0.05,
) -> dict:
    """Bull/bear flag detector (DEC-358). Edwards-Magee + Bulkowski.

    Flagpole: sharp +10% or -10% move within flagpole_lookback days.
    Flag: subsequent consolidation < 5% pullback within flag_lookback days.
    Entry: breakout above flag high (bull) or below flag low (bear).
    """
    if df is None or len(df) < flagpole_lookback + flag_lookback:
        return {}
    close = df["close"]
    n = len(close)
    pole_start = n - flagpole_lookback - flag_lookback
    pole_end = n - flag_lookback
    pole_close_start = float(close.iloc[pole_start])
    pole_close_end = float(close.iloc[pole_end])
    if pole_close_start <= 0:
        return {}
    pole_move = (pole_close_end - pole_close_start) / pole_close_start
    out = {"flag_bull_detected": False, "flag_bear_detected": False}
    if abs(pole_move) < flagpole_min_move:
        return out
    flag_window = df.tail(flag_lookback)
    flag_high = float(flag_window["high"].max())
    flag_low = float(flag_window["low"].min())
    flag_pullback = (flag_high - flag_low) / flag_high if flag_high > 0 else 1.0
    if flag_pullback >= flag_max_pullback:
        return out
    if pole_move > 0:
        out["flag_bull_detected"] = True
        out["flag_bull_pole_move_pct"] = round(pole_move, 4)
        out["flag_bull_breakout_level"] = round(flag_high, 4)
    else:
        out["flag_bear_detected"] = True
        out["flag_bear_pole_move_pct"] = round(pole_move, 4)
        out["flag_bear_breakdown_level"] = round(flag_low, 4)
    return out


def detect_triangle(
    df: pd.DataFrame,
    lookback: int = 30,
    min_touches: int = 2,
    convergence_tol: float = 0.7,
) -> dict:
    """Ascending / descending / symmetric triangle detector (DEC-359).

    Detects converging highs and lows. Ascending = flat top + rising lows.
    Descending = falling top + flat bottom. Symmetric = both converging.

    Slope ratio: |slope_top| / |slope_bottom| < convergence_tol distinguishes.
    Daily-bar approximation: requires 30+ days lookback.
    """
    if df is None or len(df) < lookback:
        return {}
    win = df.tail(lookback)
    highs_arr = win["high"].values.astype(float)
    lows_arr = win["low"].values.astype(float)
    n = len(win)
    x = np.arange(n)
    try:
        slope_high, intercept_high = np.polyfit(x, highs_arr, 1)
        slope_low, intercept_low = np.polyfit(x, lows_arr, 1)
    except Exception:
        return {}
    # Normalize slopes by mean price
    mean_price = float(win["close"].mean())
    if mean_price <= 0:
        return {}
    slope_high_norm = slope_high / mean_price
    slope_low_norm = slope_low / mean_price
    out = {"triangle_ascending_detected": False,
           "triangle_descending_detected": False,
           "triangle_symmetric_detected": False}
    # Ascending: slope_high ~ 0, slope_low > 0
    if abs(slope_high_norm) < 0.001 and slope_low_norm > 0.002:
        out["triangle_ascending_detected"] = True
        out["triangle_resistance_level"] = round(float(highs_arr.mean()), 4)
        out["triangle_breakout_pct"] = round(slope_low_norm * lookback, 4)
    # Descending: slope_high < 0, slope_low ~ 0
    elif slope_high_norm < -0.002 and abs(slope_low_norm) < 0.001:
        out["triangle_descending_detected"] = True
        out["triangle_support_level"] = round(float(lows_arr.mean()), 4)
        out["triangle_breakdown_pct"] = round(slope_high_norm * lookback, 4)
    # Symmetric: both converging
    elif slope_high_norm < -0.001 and slope_low_norm > 0.001:
        out["triangle_symmetric_detected"] = True
        out["triangle_apex_pct"] = round(abs(slope_high_norm) + slope_low_norm, 4)
    return out


def compute_all_chart_patterns(df: pd.DataFrame) -> dict:
    """One-shot aggregator: runs all 5 pattern detectors + merges results.

    Defensive on insufficient history (returns empty dict per detector,
    merged out is just whatever survived).
    """
    if df is None or df.empty:
        return {}
    out: dict = {}
    try:
        out.update(detect_head_and_shoulders(df))
    except Exception:
        pass
    try:
        out.update(detect_double_top_bottom(df))
    except Exception:
        pass
    try:
        out.update(detect_cup_and_handle(df))
    except Exception:
        pass
    try:
        out.update(detect_flag(df))
    except Exception:
        pass
    try:
        out.update(detect_triangle(df))
    except Exception:
        pass
    try:
        out.update(compute_flag_break_retest_signals(df))  # B607 F1
    except Exception:
        pass
    return out


def compute_flag_break_retest_signals(df: 'pd.DataFrame') -> dict:
    """Batch 607 (2026-06-07 owner-directed F1 bug fix in flag_bull_retest
    _long walk): flag-anchored break-and-retest primitive.

    Bug context (CHECKLIST #105 deep-read surfaced this):
      The original strat_flag_bull_retest_long (BUG-111 / Batch 329)
      was documented as "Bull flag + post-break retest" but consumed
      the DC20-anchored resistance_break_retest signal. The DC20
      max-CLOSE bore no relationship to the flag-high level (which
      is what should be retested per Edwards-Magee + Bulkowski).
      Same name-vs-implementation lie that B605 fixed for 52wh
      _break_retest and B606 fixed for r1_break_retest.

    Fix: detect retest of the SPECIFIC flag_bull_breakout_level (or
    flag_bear_breakdown_level) that was set when the flag completed.
    Runs detect_flag on a HISTORICAL slice ending K bars ago for K
    in [3..12] to find a flag that completed in the recent past,
    then checks the break->retest->hold sequence against that
    historical flag's breakout level.

    Emits (LOCAL signals consumed by strat_flag_bull_retest_long +
    Class 7 NEW strat_flag_bear_retest_short):
      - flag_bull_break_retest_long: a bull flag completed K bars ago
        (K in 3..12); at least one close in bars [-K, -1) exceeded
        flag_bull_breakout_level (break); at least one subsequent
        bar's LOW touched within 1.5*ATR(14) of breakout_level
        (retest); today's close >= breakout_level (still above).
      - flag_bear_break_retest_short: mirror around
        flag_bear_breakdown_level.

    Defensive: emits False on insufficient history (< 35 bars: ATR
    14 + flag detection 30 + at least 3 for lag) and on detect_flag
    errors.
    """
    import numpy as np
    out = {
        "flag_bull_break_retest_long":  False,
        "flag_bear_break_retest_short": False,
    }
    if df is None or len(df) < 35:
        return out

    n = len(df)
    close_arr = df["close"].values
    high_arr  = df["high"].values
    low_arr   = df["low"].values

    # ATR(14) vectorized (same as compute_break_retest_signals).
    tr1 = high_arr[1:] - low_arr[1:]
    tr2 = np.abs(high_arr[1:] - close_arr[:-1])
    tr3 = np.abs(low_arr[1:] - close_arr[:-1])
    tr_arr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = float(np.mean(tr_arr[-14:])) if len(tr_arr) >= 14 else float(np.mean(tr_arr))
    if atr <= 0:
        atr = close_arr[-1] * 0.01
    tolerance = 1.5 * atr

    # LONG: search lags 3..12 for a flag that completed K bars ago.
    for K in range(3, 13):
        if K >= n - 30:
            break
        df_at_K = df.iloc[:n - K]
        try:
            flag = detect_flag(df_at_K)
        except Exception:
            continue
        if not flag.get("flag_bull_detected"):
            continue
        breakout_level = flag.get("flag_bull_breakout_level")
        if breakout_level is None or breakout_level <= 0:
            continue
        # Break: any close in bars [n-K, n-1) (i.e. between flag end
        # and today exclusive) closed > breakout_level
        broke = any(close_arr[i] > breakout_level for i in range(n - K, n - 1))
        if not broke:
            continue
        # Retest: any subsequent bar (including today) had LOW within
        # 1.5*ATR of breakout_level
        retested = any(low_arr[i] <= breakout_level + tolerance for i in range(n - K + 1, n))
        if not retested:
            continue
        if close_arr[-1] >= breakout_level:
            out["flag_bull_break_retest_long"] = True
            break

    # SHORT mirror: bear flag K bars ago, breakdown, retest from below, today's close still below.
    for K in range(3, 13):
        if K >= n - 30:
            break
        df_at_K = df.iloc[:n - K]
        try:
            flag = detect_flag(df_at_K)
        except Exception:
            continue
        if not flag.get("flag_bear_detected"):
            continue
        breakdown_level = flag.get("flag_bear_breakdown_level")
        if breakdown_level is None or breakdown_level <= 0:
            continue
        broke = any(close_arr[i] < breakdown_level for i in range(n - K, n - 1))
        if not broke:
            continue
        retested = any(high_arr[i] >= breakdown_level - tolerance for i in range(n - K + 1, n))
        if not retested:
            continue
        if close_arr[-1] <= breakdown_level:
            out["flag_bear_break_retest_short"] = True
            break

    return out
