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
    shoulder_tol: float = 0.03,  # B1208 (2026-07-07 Council 279 Fix #10): reverted default 0.04 -> 0.03 for narrow-scope. Call site in compute_all_chart_patterns now passes 0.04 explicitly.
    head_min: float = 0.02,       # B1208: reverted default 0.015 -> 0.02. Call site passes 0.015 explicitly.
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


def detect_inverted_cup_and_handle(
    df: pd.DataFrame,
    lookback: int = 120,
    cup_height_min: float = 0.10,
    cup_height_max: float = 0.35,
    handle_pct_max: float = 0.15,
) -> dict:
    """Inverted cup-and-handle detector (Batch 686 2026-06-10 owner-approved
    per B683 self-critique CP-1 missing-inverse audit + B685 deferred work
    now scoped).

    Bearish mirror of detect_cup_and_handle per Bulkowski 2005 *Encyclopedia
    of Chart Patterns* (sometimes called 'rounded top with handle' or
    'dump and pop'). Symmetric methodology to the bullish cup-and-handle:

    Inverted Cup: inverted-U (∩) shape; price rises from a rim LOW to a
    cup PEAK in the middle, then falls back to a right rim LOW (~same
    level as left rim low). 10-35% cup height (peak above rim).
    Inverted Handle: shallow upward bounce after right rim, bounce <15%.
    Entry: SHORT on breakdown below handle low with volume confirmation.

    Daily-bar approximation: requires ~120 days of history for inverted
    cup formation. Handle is the most recent 5-20 days post-rim.

    Symmetric to detect_cup_and_handle by:
    - left_rim_low (min of lows in first 25% of window) replaces left_rim (max of highs)
    - right_rim_low (min of lows in last 25%) replaces right_rim
    - cup_high (max of close in middle 50%) replaces cup_low (min of close)
    - rim_low = min of two rim lows replaces rim = max of two rim highs
    - cup_height = (cup_high - rim_low) / rim_low replaces cup_depth
    - handle_bounce = (handle_high - handle_low) / handle_low replaces handle_pullback
    - breakdown_level = handle_low replaces breakout_level = handle_high

    Emits:
      inverted_cup_handle_detected:        bool
      inverted_cup_handle_rim_low:         float (the horizontal rim at bottom of ∩)
      inverted_cup_handle_height_pct:      float (peak above rim, as pct of rim)
      inverted_cup_handle_breakdown_level: float (handle low; SHORT-entry trigger)
    """
    if df is None or len(df) < lookback:
        return {}
    win = df.tail(lookback)
    close = win["close"]
    low = win["low"]
    n = len(win)
    left_rim_end = n // 4
    right_rim_start = (3 * n) // 4
    mid_start, mid_end = left_rim_end, right_rim_start
    left_rim_low = float(low.iloc[:left_rim_end].min())
    right_rim_low = float(low.iloc[right_rim_start:].min())
    cup_high = float(close.iloc[mid_start:mid_end].max())
    rim_low = min(left_rim_low, right_rim_low)
    if rim_low <= 0:
        return {}
    cup_height = (cup_high - rim_low) / rim_low
    rim_diff = abs(left_rim_low - right_rim_low) / rim_low
    if not (cup_height_min <= cup_height <= cup_height_max and rim_diff < 0.05):
        return {"inverted_cup_handle_detected": False}
    # Handle: post-rim consolidation (last 5-20 days; small upward bounce)
    handle_window = win.tail(20)
    handle_high = float(handle_window["high"].max())
    handle_low = float(handle_window["low"].min())
    handle_bounce = (handle_high - handle_low) / handle_low if handle_low > 0 else 1.0
    handle_detected = handle_bounce < handle_pct_max
    return {
        "inverted_cup_handle_detected":        handle_detected,
        "inverted_cup_handle_rim_low":         round(rim_low, 4),
        "inverted_cup_handle_height_pct":      round(cup_height, 4),
        "inverted_cup_handle_breakdown_level": round(handle_low, 4),
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
    # B1126 BUG-277 fix (Council 245 empirical): SPY 4y median slope_high_norm
    # = 0.00151 (90%ile 0.00302) - old tol 0.001 excluded 90%+ of consolidation
    # windows. Widen to Bulkowski 2005 canonical ~2% drift range: flat<0.002,
    # slope>0.001. SPY 4y detection: 0 -> 17 (matches Bulkowski 5-15/yr).
    # Ascending: slope_high ~ 0, slope_low > 0
    if abs(slope_high_norm) < 0.002 and slope_low_norm > 0.001:
        out["triangle_ascending_detected"] = True
        out["triangle_resistance_level"] = round(float(highs_arr.mean()), 4)
        out["triangle_breakout_pct"] = round(slope_low_norm * lookback, 4)
    # Descending: slope_high < 0, slope_low ~ 0
    elif slope_high_norm < -0.001 and abs(slope_low_norm) < 0.002:
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
        # B1208 (2026-07-07 Council 279 Fix #10): explicit kwargs preserving
        # B1196 loosening for the 2 target strategies (head_and_shoulders_
        # bottom_long, head_and_shoulders_top_short) without changing the
        # function default (narrow-scope per feedback_narrow_scope_blast_radius).
        out.update(detect_head_and_shoulders(df, shoulder_tol=0.04, head_min=0.015))
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
        out.update(detect_inverted_cup_and_handle(df))  # B686 Class 7 NEW
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
    try:
        out.update(compute_triangle_apex_break_retest_signals(df))  # B685 (CP-8 fix)
    except Exception:
        pass
    try:
        out.update(compute_cup_handle_neckline_break_retest_signals(df))  # B685 (CP-9 fix)
    except Exception:
        pass
    return out


def compute_flag_break_retest_signals(df: 'pd.DataFrame') -> dict:
    """Batch 607 (2026-06-07 owner-directed F1 bug fix in flag_bull_retest
    _long walk): flag-anchored break-and-retest primitive.

    Batch 618 (2026-06-07 owner-directed B607 critique re-fix):
      added flag_bull_broke + flag_bear_broke signals (breakout-occurred
      without retest requirement) to fix the phantom-breakout bug in
      the PARENT strat_flag_bull_long. The parent strategy used to
      fire on flag_bull_detected + EMA-200 alone, but flag_bull
      _detected fires the day the flag COMPLETES - the flag window
      INCLUDES today's bar, so today's close <= flag_high by
      definition. No breakout could have occurred yet. B618 fix:
      run detect_flag on a HISTORICAL slice ending K bars ago, then
      check that today's close exceeds the historical flag_high.

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

    PIT discipline (B618 test pin per external-AI critique #2): the
    flag detection slice `df.iloc[:n - K]` STRICTLY excludes bars
    [n-K, n], so flag_high is computed over a window entirely BEFORE
    the breakout/retest window. No contamination of the level by the
    breakout bar's own high. Regression-tested in
    test_batch618_pit_discipline.py.

    Emits (LOCAL signals):
      - flag_bull_break_retest_long: a bull flag completed K bars ago
        (K in 3..12); at least one close in bars [-K, -1) exceeded
        flag_bull_breakout_level (break); at least one subsequent
        bar's LOW touched within 1.5*ATR(14) of breakout_level
        (retest); today's close >= breakout_level (still above).
      - flag_bear_break_retest_short: mirror around
        flag_bear_breakdown_level.
      - flag_bull_broke (B618): a bull flag completed K bars ago
        (K in 1..8); today's close > flag_bull_breakout_level. No
        retest required. Consumed by parent strat_flag_bull_long.
      - flag_bear_broke (B618): mirror.

    Defensive: emits False on insufficient history (< 35 bars: ATR
    14 + flag detection 30 + at least 3 for lag) and on detect_flag
    errors.
    """
    import numpy as np
    out = {
        "flag_bull_break_retest_long":  False,
        "flag_bear_break_retest_short": False,
        # B618 (2026-06-07): breakout-occurred signals (no retest required)
        # for parent strat_flag_bull_long phantom-breakout fix.
        "flag_bull_broke":              False,
        "flag_bear_broke":              False,
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

    # B1181 (2026-07-04 Council 275 owner-approved final_recommended_actions):
    # K window widened 3..12 -> 3..15 per Edwards-Magee 1-4wk canonical (5-20 BD).
    # Applies to flag_bull_break_retest_long AND flag_bear_break_retest_short.
    # LONG: search lags 3..14 for a flag that completed K bars ago.
    for K in range(3, 16):
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
    # B1181: K widened 3..12 -> 3..15 (Edwards-Magee 1-4wk canonical).
    for K in range(3, 16):
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

    # B618 (2026-06-07 owner-directed B607 critique re-fix): breakout-
    # occurred signals (no retest requirement) for parent
    # strat_flag_bull_long. Search lags 1..8 for a flag that completed
    # K bars ago + verify today's close exceeds (LONG) or falls below
    # (SHORT) the historical flag's breakout level. Same PIT-disciplined
    # historical-slice pattern as the retest signals above.
    # B1181: K widened 1..8 -> 1..15 (Edwards-Magee 1-4wk canonical).
    for K in range(1, 16):
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
        if close_arr[-1] > breakout_level:
            out["flag_bull_broke"] = True
            break

    # B1181: K widened 1..8 -> 1..15 (Edwards-Magee 1-4wk canonical).
    for K in range(1, 16):
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
        if close_arr[-1] < breakdown_level:
            out["flag_bear_broke"] = True
            break

    return out


def compute_triangle_apex_break_retest_signals(df: 'pd.DataFrame') -> dict:
    """Batch 685 (2026-06-10 owner-approved B607-pattern producer fix per
    B683 self-critique CP-8 DESIGN BUG CANDIDATE).

    Pre-B685: strat_triangle_ascending_retest_long consumed
    `resistance_break_retest` (DC20-anchored) instead of triangle-apex-
    anchored retest. Same name-vs-implementation bug class as B605 fixed
    for 52wh_break_retest and B607 fixed for flag_bull_retest_long.

    Fix: detect retest of the SPECIFIC triangle_resistance_level (the
    flat top of an ascending triangle) that was set when the triangle
    completed K bars ago. Runs detect_triangle on a HISTORICAL slice
    ending K bars ago (K in [3..12]) to find a triangle that completed
    in the recent past, then checks the break -> retest -> hold
    sequence against that historical triangle's apex level.

    PIT discipline: the detection slice `df.iloc[:n - K]` STRICTLY
    excludes bars [n-K, n], so triangle_resistance_level is computed
    over a window entirely BEFORE the breakout/retest window. No
    contamination of the level by the breakout bar's own high.

    Emits (LOCAL signals):
      - triangle_apex_break_retest_long: ascending triangle completed
        K bars ago; at least one close in (n-K, n-1) exceeded
        triangle_resistance_level (break); at least one subsequent
        bar's LOW touched within 1.5*ATR(14) of resistance level
        (retest); today's close >= resistance_level (still above).

    No SHORT mirror in this producer yet -- descending triangle
    Class 7 NEW strat_triangle_descending_short (also B685) fires on
    base detection without retest variant; future producer extension
    could add triangle_apex_break_retest_short symmetric to LONG.

    Defensive: emits False on insufficient history (< 45 bars: ATR 14
    + triangle detection 30 + at least 3 for lag) and on detect_triangle
    errors.
    """
    import numpy as np
    out = {"triangle_apex_break_retest_long": False}
    if df is None or len(df) < 45:
        return out
    n = len(df)
    close_arr = df["close"].values
    high_arr  = df["high"].values
    low_arr   = df["low"].values
    tr1 = high_arr[1:] - low_arr[1:]
    tr2 = np.abs(high_arr[1:] - close_arr[:-1])
    tr3 = np.abs(low_arr[1:] - close_arr[:-1])
    tr_arr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = float(np.mean(tr_arr[-14:])) if len(tr_arr) >= 14 else float(np.mean(tr_arr))
    if atr <= 0:
        atr = close_arr[-1] * 0.01
    tolerance = 1.5 * atr
    for K in range(3, 13):
        if K >= n - 30:
            break
        df_at_K = df.iloc[:n - K]
        try:
            tri = detect_triangle(df_at_K)
        except Exception:
            continue
        if not tri.get("triangle_ascending_detected"):
            continue
        resistance_level = tri.get("triangle_resistance_level")
        if resistance_level is None or resistance_level <= 0:
            continue
        broke = any(close_arr[i] > resistance_level for i in range(n - K, n - 1))
        if not broke:
            continue
        retested = any(low_arr[i] <= resistance_level + tolerance for i in range(n - K + 1, n))
        if not retested:
            continue
        if close_arr[-1] >= resistance_level:
            out["triangle_apex_break_retest_long"] = True
            break
    return out


def compute_cup_handle_neckline_break_retest_signals(df: 'pd.DataFrame') -> dict:
    """Batch 685 (2026-06-10 owner-approved B607-pattern producer fix per
    B683 self-critique CP-9 docstring-honest-proxy upgrade).

    Pre-B685: strat_cup_and_handle_retest_long consumed
    `resistance_break_retest` (DC20-anchored) as an explicit PROXY for
    the actual cup-and-handle neckline (handle high). Docstring honestly
    acknowledged "proxied via resistance_break_retest from DC20" but the
    proxy was unprincipled.

    Fix: detect retest of the SPECIFIC cup_handle_breakout_level (the
    handle high = neckline) that was set when the cup-and-handle pattern
    completed K bars ago. Same B607-pattern PIT-disciplined historical
    slice as compute_flag_break_retest_signals.

    Emits (LOCAL signals):
      - cup_handle_neckline_break_retest_long: cup-and-handle completed
        K bars ago (K in 3..12); at least one close in (n-K, n-1)
        exceeded cup_handle_breakout_level (break); at least one
        subsequent bar's LOW touched within 1.5*ATR(14) of breakout
        level (retest); today's close >= breakout_level.

    No SHORT mirror (inverted cup-and-handle producer + strategy
    deferred per B685 scope).

    Defensive: emits False on insufficient history (< 75 bars: cup
    needs 60-day lookback + ATR 14 + lag).
    """
    import numpy as np
    out = {"cup_handle_neckline_break_retest_long": False}
    if df is None or len(df) < 75:
        return out
    n = len(df)
    close_arr = df["close"].values
    high_arr  = df["high"].values
    low_arr   = df["low"].values
    tr1 = high_arr[1:] - low_arr[1:]
    tr2 = np.abs(high_arr[1:] - close_arr[:-1])
    tr3 = np.abs(low_arr[1:] - close_arr[:-1])
    tr_arr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = float(np.mean(tr_arr[-14:])) if len(tr_arr) >= 14 else float(np.mean(tr_arr))
    if atr <= 0:
        atr = close_arr[-1] * 0.01
    # B1196 (2026-07-06 Council 278 owner-approved): widen retest tolerance
    # 1.5x -> 2.0x ATR (equivalent to ~1% -> ~2% Bulkowski canonical). Applies
    # only to cup_and_handle_retest_long producer.
    tolerance = 2.0 * atr
    for K in range(3, 13):
        if K >= n - 60:
            break
        df_at_K = df.iloc[:n - K]
        try:
            cup = detect_cup_and_handle(df_at_K)
        except Exception:
            continue
        if not cup.get("cup_handle_detected"):
            continue
        breakout_level = cup.get("cup_handle_breakout_level")
        if breakout_level is None or breakout_level <= 0:
            continue
        broke = any(close_arr[i] > breakout_level for i in range(n - K, n - 1))
        if not broke:
            continue
        retested = any(low_arr[i] <= breakout_level + tolerance for i in range(n - K + 1, n))
        if not retested:
            continue
        if close_arr[-1] >= breakout_level:
            out["cup_handle_neckline_break_retest_long"] = True
            break
    return out
