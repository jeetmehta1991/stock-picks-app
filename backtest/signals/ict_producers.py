"""Batch 581 (2026-06-04) -- custom ICT producers for Layer 2D
strategies that don't derive from the smartmoneyconcepts library.

Owner directive 2026-06-04 (inline-spec per
feedback_layer_2d_ict_inline_specification): wire MMBM/MMSM
(Accumulation -> Manipulation -> Distribution) and Week Opening Gap.

Producers exposed:

  compute_po3_signals(df, accum_window=5)
    Detects the 3-phase Power-of-3 cycle on DAILY bars:
      Phase 1 ACCUMULATION  - range-bound (tight pct-range over N bars)
      Phase 2 MANIPULATION  - sweep below/above accumulation range
      Phase 3 DISTRIBUTION  - reversal back into / through the range

    Emits:
      po3_accumulation_active     bool - last `accum_window` bars in tight range
      po3_manipulation_sweep_down bool - today's LOW pierced accumulation low
      po3_manipulation_sweep_up   bool - today's HIGH pierced accumulation high
      po3_mmbm_setup              bool - sweep down + close back above accum low + close>open (bullish PO3)
      po3_mmsm_setup              bool - sweep up + close back below accum high + close<open (bearish PO3)
      po3_accum_range_pct         float - accumulation range as % of mean price

  compute_week_opening_gap_signals(df)
    Detects week-open gap (Monday open vs prior Friday close).
    Daily-bar proxy for ICT "Sunday gap" since US equities don't trade
    over the weekend - the Friday-close-to-Monday-open gap is the
    closest analog.

    Emits:
      is_week_open                 bool - today is Monday or first trading day after weekend
      week_open_gap_up_pct         float - (Mon_open - Fri_close)/Fri_close * 100
      week_open_gap_down_pct       float - same but absolute value when negative
      week_open_gap_up_15pct       bool - Mon opened with gap up >= 1.5%
      week_open_gap_down_15pct     bool - Mon opened with gap down >= 1.5%

Both producers are ADDITIVE: their emitted signals are consumed only
by the new MMBM / MMSM / Week Opening Gap strategies. No existing
strategy is affected (local-scope per CHECKLIST #104).
"""
from __future__ import annotations

import pandas as pd


def compute_po3_signals(df: pd.DataFrame, accum_window: int = 5,
                        tight_range_threshold: float = 0.05) -> dict:
    """Power-of-3 phase detector.

    accum_window: bars to look back for accumulation phase (default 5)
    tight_range_threshold: max (high_max - low_min) / mean_close to qualify
                           as accumulation (default 0.05 = 5%)
    """
    out = {
        "po3_accumulation_active":     False,
        "po3_manipulation_sweep_down": False,
        "po3_manipulation_sweep_up":   False,
        "po3_mmbm_setup":              False,
        "po3_mmsm_setup":              False,
        "po3_accum_range_pct":         0.0,
    }
    if df is None or len(df) < accum_window + 1:
        return out
    # Today's bar
    today = df.iloc[-1]
    today_high   = float(today["high"])
    today_low    = float(today["low"])
    today_open   = float(today["open"])
    today_close  = float(today["close"])
    # Accumulation window: prior N bars (excluding today)
    window = df.iloc[-(accum_window + 1):-1]
    range_high = float(window["high"].max())
    range_low  = float(window["low"].min())
    mean_close = float(window["close"].mean())
    if mean_close <= 0:
        return out
    accum_range_pct = (range_high - range_low) / mean_close
    out["po3_accum_range_pct"] = round(accum_range_pct, 4)
    out["po3_accumulation_active"] = bool(accum_range_pct <= tight_range_threshold)
    if not out["po3_accumulation_active"]:
        return out  # no accumulation -> no PO3 setup possible
    # Phase 2: manipulation sweep
    swept_down = today_low < range_low
    swept_up   = today_high > range_high
    out["po3_manipulation_sweep_down"] = bool(swept_down)
    out["po3_manipulation_sweep_up"]   = bool(swept_up)
    # MMBM setup (bullish PO3): sweep down + reversal back above accum low + bullish bar
    if swept_down and today_close > range_low and today_close > today_open:
        out["po3_mmbm_setup"] = True
    # MMSM setup (bearish PO3): sweep up + reversal back below accum high + bearish bar
    if swept_up and today_close < range_high and today_close < today_open:
        out["po3_mmsm_setup"] = True
    return out


def compute_week_opening_gap_signals(df: pd.DataFrame,
                                     gap_threshold_pct: float = 1.5) -> dict:
    """Week-opening gap detector (daily-bar proxy for ICT Sunday gap).

    df must have a DatetimeIndex or 'date' column convertible to dates.
    Detects: today is first trading day of the week (Monday or
    Monday-equivalent after holidays) AND gap_pct between prior close
    and today's open exceeds threshold.

    gap_threshold_pct: minimum absolute gap (default 1.5%) to qualify
                       as a "significant" week-open gap worth fading.
    """
    out = {
        "is_week_open":             False,
        "week_open_gap_up_pct":     0.0,
        "week_open_gap_down_pct":   0.0,
        "week_open_gap_up_15pct":   False,
        "week_open_gap_down_15pct": False,
    }
    if df is None or len(df) < 2:
        return out
    # Determine today's day-of-week
    today_idx = df.index[-1]
    if not hasattr(today_idx, "weekday"):
        # Try to coerce
        try:
            today_idx = pd.to_datetime(today_idx)
        except Exception:
            return out
    today_weekday = today_idx.weekday()
    # Prior bar
    prev_idx = df.index[-2]
    if not hasattr(prev_idx, "weekday"):
        try:
            prev_idx = pd.to_datetime(prev_idx)
        except Exception:
            return out
    prev_weekday = prev_idx.weekday()
    # Is today the first trading day after the weekend?
    # In US equities: today is Mon (weekday 0) AND prev bar was Fri (weekday 4)
    # OR: today is Mon AND prev bar was Thu/Fri (long weekend / holiday Friday)
    # Simplest proxy: today weekday < prev weekday OR (prev weekday >= 4 and today weekday == 0)
    is_week_open = (today_weekday == 0 and prev_weekday >= 4) or \
                   (today_weekday < prev_weekday and (today_idx - prev_idx).days >= 2)
    out["is_week_open"] = bool(is_week_open)
    if not is_week_open:
        return out
    today_open = float(df.iloc[-1]["open"])
    prev_close = float(df.iloc[-2]["close"])
    if prev_close <= 0:
        return out
    gap_pct = (today_open - prev_close) / prev_close * 100.0
    threshold = float(gap_threshold_pct)
    if gap_pct > 0:
        out["week_open_gap_up_pct"]   = round(gap_pct, 3)
        out["week_open_gap_up_15pct"] = bool(gap_pct >= threshold)
    else:
        out["week_open_gap_down_pct"]   = round(abs(gap_pct), 3)
        out["week_open_gap_down_15pct"] = bool(abs(gap_pct) >= threshold)
    return out
