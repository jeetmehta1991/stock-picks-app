# Source: B710 reviewer fire-count-ceiling + S4-B717-CEILING-FLAGGED-REDUNDANCY-DIAGNOSTIC + B710 W1 strong-close pattern + B697 BR-1 anti-fakeout per CHECKLIST #77
"""B720 pin tests: PO3 producer close_position thresholds tightened.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* po3_bullish: 5,553/yr LONG (TOO_FREQUENT_FAIL above 5K ceiling)
* po3_bearish: 4,076/yr SHORT (BORDERLINE)
* po3_htf_aligned_long: 4,924/yr LONG (BORDERLINE)

B720 changes per B710 W1 strong-close + B697 BR-1 anti-fakeout patterns:
* LONG: close_position > 0.66 -> > 0.75 (upper 25% of range, not upper 34%)
* SHORT: close_position < 0.33 -> < 0.25 (lower 25% of range, not lower 33%)

Direct producer change per `feedback_narrow_scope_blast_radius`: po3_bullish
+ po3_bearish have ONLY 4 consumers (ICT-1/2/3/4 strategies); no other
dependencies. Parallel-variant pattern (B654/B718 cpr_narrow_tight) not
needed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.signals.multi_timeframe import compute_po3_signal


def _bar(open, high, low, close):
    return {"open": open, "high": high, "low": low, "close": close}


def _make_df(prev_bar, today_bar):
    return pd.DataFrame([prev_bar, today_bar])


# ---------------------------------------------------------------------------
# Pin 1: po3_bullish requires close_position > 0.75 (was 0.66)
# ---------------------------------------------------------------------------
def test_b720_pin1_po3_bullish_requires_close_in_upper_25pct():
    """At close_position = 0.70 (between old 0.66 and new 0.75), po3_bullish
    must be False post-B720; was True pre-B720."""
    # Setup: today's bar sweeps below prev_low, closes bullish, but close
    # position is 0.70 (upper 30% of range, not upper 25%).
    prev = _bar(100, 105, 95, 100)  # prev_low = 95
    # Today: low=90 (sweeps below 95), high=100, close=97 (close_pos=(97-90)/(100-90)=0.70)
    today = _bar(91, 100, 90, 97)
    df = _make_df(prev, today)
    result = compute_po3_signal(df)
    assert result.get("po3_bullish") is False, (
        f"po3_bullish should be False at close_position=0.70 post-B720; got {result}"
    )

    # At close_position = 0.80 (upper 20%), should fire
    today_strong = _bar(91, 100, 90, 98)  # close_pos=(98-90)/10=0.80
    df_strong = _make_df(prev, today_strong)
    result_strong = compute_po3_signal(df_strong)
    assert result_strong.get("po3_bullish") is True, (
        f"po3_bullish should be True at close_position=0.80 post-B720; got {result_strong}"
    )


# ---------------------------------------------------------------------------
# Pin 2: po3_bearish requires close_position < 0.25 (was 0.33)
# ---------------------------------------------------------------------------
def test_b720_pin2_po3_bearish_requires_close_in_lower_25pct():
    """At close_position = 0.30, po3_bearish must be False post-B720."""
    # Setup: today sweeps above prev_high, closes bearish, close_position 0.30
    prev = _bar(100, 105, 95, 100)  # prev_high = 105
    # Today: low=100, high=110 (sweeps above 105), close=103
    # close_pos = (103-100)/(110-100) = 0.30
    today = _bar(108, 110, 100, 103)
    df = _make_df(prev, today)
    result = compute_po3_signal(df)
    assert result.get("po3_bearish") is False, (
        f"po3_bearish should be False at close_position=0.30 post-B720; got {result}"
    )

    # At close_position = 0.20, should fire
    today_strong = _bar(108, 110, 100, 102)  # close_pos = 0.20
    df_strong = _make_df(prev, today_strong)
    result_strong = compute_po3_signal(df_strong)
    assert result_strong.get("po3_bearish") is True, (
        f"po3_bearish should be True at close_position=0.20 post-B720; got {result_strong}"
    )


# ---------------------------------------------------------------------------
# Pin 3: po3_close_position field still emitted (was, is)
# ---------------------------------------------------------------------------
def test_b720_pin3_po3_close_position_field_preserved():
    """po3_close_position numeric field still returned regardless of fire."""
    prev = _bar(100, 105, 95, 100)
    today = _bar(91, 100, 90, 97)
    df = _make_df(prev, today)
    result = compute_po3_signal(df)
    assert "po3_close_position" in result, "po3_close_position must still be emitted"
    assert isinstance(result["po3_close_position"], float)
    assert abs(result["po3_close_position"] - 0.70) < 0.01


# ---------------------------------------------------------------------------
# Pin 4: sweep_below + sweep_above signals still emitted (legacy fields)
# ---------------------------------------------------------------------------
def test_b720_pin4_po3_sweep_signals_preserved():
    """po3_sweep_below_prior_low + po3_sweep_above_prior_high signals still
    emitted as intermediate fields (B720 only changed close_position threshold,
    not sweep detection)."""
    prev = _bar(100, 105, 95, 100)
    today = _bar(91, 100, 90, 97)
    df = _make_df(prev, today)
    result = compute_po3_signal(df)
    assert result.get("po3_sweep_below_prior_low") is True
    assert result.get("po3_sweep_above_prior_high") is False


# ---------------------------------------------------------------------------
# Pin 5: Insufficient data returns empty dict (unchanged)
# ---------------------------------------------------------------------------
def test_b720_pin5_insufficient_data_returns_empty():
    """compute_po3_signal returns {} when df has fewer than 2 bars."""
    df = pd.DataFrame([_bar(100, 105, 95, 100)])
    result = compute_po3_signal(df)
    assert result == {}, "Should return empty dict with only 1 bar"
