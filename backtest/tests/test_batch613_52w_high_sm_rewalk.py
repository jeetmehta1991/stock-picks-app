"""Batch 613 (2026-06-07) -- MEDIUM-priority re-walk of
strat_52w_high_breakout_with_smart_money_long per 13F-state-staleness
audit follow-up to B611/B612 critique.

Owner directive: "F1 + F2a + F3b + a + i" + "I am unsure of b and want
to A/B test that too."

Changes applied:
  F1: docstring reframed to honest EVENT/STATE framing - 13F STATE half
      is slow eligibility (90d persistence + DEC-325 45-day lag), EVENT
      half (insider_cluster_active / cfo_buy / large_dollar_buy) carries
      bar-of-fire timing alpha. George-Hwang 2004 52w-high anomaly is
      the price-momentum thesis.
  F2a: _has_smart_money_buy composite docstring rewritten in B612 to
      tag components EVENT vs STATE; this batch removes false "confluence"
      framing from the consumer strategy too.
  F3b: strat_52w_low_breakdown_with_smart_money_short DELETED. 13F is
      SEC long-only by rule (asymmetric data violates mechanical inverse
      per feedback_asymmetric_data_sources_break_mechanical_inverse).
      _has_smart_money_sell helper ALSO deleted (4/5 components never
      emitted by producer - silent-gap).
  (a): close_in_top_40pct_of_range gate added to LONG (B589-family
       standardization for momentum breakouts).
  (b A/B twin): NEW strategy strat_52w_high_breakout_with_smart_money_
      vol_below_long - identical to LONG but vol_spike_12x replaced with
      vol_below_avg (Bulkowski 2005 retest absorption hypothesis test).

Pins:
  (1) LONG fires with all 5 new gates True (including top-40pct + vol_spike_12x)
  (2) LONG silent-gap closed: missing close_in_top_40pct_of_range blocks
  (3) LONG silent-gap closed: missing vol_spike_12x blocks
  (4) LONG still requires _has_smart_money_buy (composite gate)
  (5) B-twin fires with vol_below_avg (NOT vol_spike_12x)
  (6) B-twin DOES NOT fire when only vol_spike_12x is True (must have vol_below_avg)
  (7) B-twin silent-gap closed: missing close_in_top_40pct_of_range blocks
  (8) SHORT mirror strat_52w_low_breakdown_with_smart_money_short REMOVED
      from screener module symbols
  (9) _has_smart_money_sell helper REMOVED from screener module symbols
  (10) Registry: SHORT key removed, B-twin key added (net 0; total 221)
  (11) ALL_STRATEGIES count preserved at 221 (-1 SHORT + 1 B-twin = 0)
"""
from __future__ import annotations

import pytest


def test_batch613_long_fires_5_gates():
    """Pin (1): LONG with new strong-close gate + smart-money buy fires."""
    from backtest.signals.screener import strat_52w_high_breakout_with_smart_money_long
    s = {
        "near_52w_high_95pct": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_spike_12x": True,
        # smart-money EVENT half present
        "insider_cluster_active": True,
    }
    out = strat_52w_high_breakout_with_smart_money_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch613_long_silent_gap_closed_top_40pct():
    """Pin (2): missing close_in_top_40pct_of_range blocks (B613 (a))."""
    from backtest.signals.screener import strat_52w_high_breakout_with_smart_money_long
    s = {
        "near_52w_high_95pct": True,
        "close_above_open": True,
        # close_in_top_40pct_of_range ABSENT - B613 (a) gate must default False
        "vol_spike_12x": True,
        "insider_cluster_active": True,
    }
    assert strat_52w_high_breakout_with_smart_money_long(s)["fires"] is False


def test_batch613_long_silent_gap_closed_vol_spike():
    """Pin (3): missing vol_spike_12x blocks."""
    from backtest.signals.screener import strat_52w_high_breakout_with_smart_money_long
    s = {
        "near_52w_high_95pct": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        # vol_spike_12x ABSENT
        "insider_cluster_active": True,
    }
    assert strat_52w_high_breakout_with_smart_money_long(s)["fires"] is False


def test_batch613_long_requires_smart_money_buy():
    """Pin (4): all technicals True but NO smart-money component -> blocked."""
    from backtest.signals.screener import strat_52w_high_breakout_with_smart_money_long
    s = {
        "near_52w_high_95pct": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_spike_12x": True,
        # NO smart-money signal True
    }
    assert strat_52w_high_breakout_with_smart_money_long(s)["fires"] is False


def test_batch613_b_twin_fires_with_vol_below_avg():
    """Pin (5): B-twin fires on vol_below_avg (Bulkowski hypothesis)."""
    from backtest.signals.screener import (
        strat_52w_high_breakout_with_smart_money_vol_below_long,
    )
    s = {
        "near_52w_high_95pct": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_below_avg": True,
        "cfo_buy": True,
    }
    out = strat_52w_high_breakout_with_smart_money_vol_below_long(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch613_b_twin_does_not_fire_on_vol_spike_only():
    """Pin (6): A/B isolation - same gates EXCEPT vol_below_avg replaces
    vol_spike_12x. If only vol_spike_12x is True, B-twin must NOT fire."""
    from backtest.signals.screener import (
        strat_52w_high_breakout_with_smart_money_vol_below_long,
    )
    s = {
        "near_52w_high_95pct": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
        "vol_spike_12x": True,           # A-twin gate, NOT B-twin gate
        # vol_below_avg ABSENT
        "insider_cluster_active": True,
    }
    assert strat_52w_high_breakout_with_smart_money_vol_below_long(s)["fires"] is False


def test_batch613_b_twin_silent_gap_closed_top_40pct():
    """Pin (7)."""
    from backtest.signals.screener import (
        strat_52w_high_breakout_with_smart_money_vol_below_long,
    )
    s = {
        "near_52w_high_95pct": True,
        "close_above_open": True,
        # close_in_top_40pct_of_range ABSENT
        "vol_below_avg": True,
        "cfo_buy": True,
    }
    assert strat_52w_high_breakout_with_smart_money_vol_below_long(s)["fires"] is False


def test_batch613_short_mirror_deleted():
    """Pin (8): strat_52w_low_breakdown_with_smart_money_short removed."""
    from backtest.signals import screener
    assert not hasattr(screener, "strat_52w_low_breakdown_with_smart_money_short"), (
        "B613 F3b: SHORT mirror must be deleted (asymmetric-data violation "
        "per feedback_asymmetric_data_sources_break_mechanical_inverse)"
    )


def test_batch613_has_smart_money_sell_helper_deleted():
    """Pin (9): _has_smart_money_sell composite removed."""
    from backtest.signals import screener
    assert not hasattr(screener, "_has_smart_money_sell"), (
        "B613 F3b helper cleanup: 4/5 sell-side components were never "
        "emitted by smart_money.py producer; helper had no surviving "
        "consumer after SHORT mirror deletion"
    )


def test_batch613_registry_short_removed_btwin_added():
    """Pin (10)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "52w_low_breakdown_with_smart_money_short" not in ALL_STRATEGIES, (
        "SHORT mirror registry key must be removed"
    )
    assert "52w_high_breakout_with_smart_money_vol_below_long" in ALL_STRATEGIES, (
        "B-twin registry key must be added"
    )
    assert "52w_high_breakout_with_smart_money_long" in ALL_STRATEGIES, (
        "Original LONG strategy still present"
    )


def test_batch613_all_strategies_count_preserved_at_221():
    """Pin (11): B613 is -1 SHORT + 1 B-twin = net 0."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 220
