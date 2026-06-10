"""Batch 682 (2026-06-10) -- owner-approved code changes per B680 self-critique:

  1. BR-8 strat_dc20_break_retest: swap vol_spike_15x -> vol_below_avg
     (Bulkowski 2005 retest absorption thesis alignment)
  2. BR-15 strat_volume_spike_breakout_retest: DELETE per B620 precedent
     + B621 0.01/yr WORST FAIL_FIRE_STARVED estimator
  3. EV-3 strat_pead_long_high_yoy_growth_only: DELETE per Pattern W
     deterministic-subset of EV-1 (yoy >= +5% strict subset of yoy > 0)
  4. EV-4 strat_pead_short_negative_yoy_growth: DELETE per Pattern W
     symmetric to EV-3
  5. EV-7 strat_buyback_8k_recent_long: DELETE per B680 CC-B population-
     mixing concern + B673 SM-4 feasibility-failure carry (ANY-8-K-type
     proxy fires on M&A Item 1.01 mixing with buyback Item 8.01)

Owner approval 2026-06-10: 'BR-8 thesis-bug + BR-15 delete + EV-3/EV-4
deprecate + EV-7 delete-or-fix - these are pre-cube actions per the
self-critique; they need explicit owner approval to ship per
feedback_local_changes_default_global_needs_approval - Approved'

Strategy count impact: 222 -> 218 (-4 deletions; BR-8 swap is no-count-change).

Pins:

Deletions (4):
  (1) strat_volume_spike_breakout_retest no longer importable from screener
  (2) strat_pead_long_high_yoy_growth_only no longer importable from screener
  (3) strat_pead_short_negative_yoy_growth no longer importable from screener
  (4) strat_buyback_8k_recent_long no longer importable from screener

Registry removals (4):
  (5) 'volume_spike_breakout_retest' not in ALL_STRATEGIES
  (6) 'pead_long_high_yoy_growth_only' not in ALL_STRATEGIES
  (7) 'pead_short_negative_yoy_growth' not in ALL_STRATEGIES
  (8) 'buyback_8k_recent_long' not in ALL_STRATEGIES

Count attestation (1):
  (9) len(ALL_STRATEGIES) == 218

BR-8 thesis-fix verification (3):
  (10) strat_dc20_break_retest LONG fires on resistance_break_retest +
       vol_below_avg + adx_trending (post-B682 vol-below-avg swap)
  (11) strat_dc20_break_retest LONG does NOT fire on vol_spike_15x without
       vol_below_avg (pre-B682 design no longer wired)
  (12) strat_dc20_break_retest SHORT fires on support_break_retest +
       vol_below_avg + adx_trending (symmetric)
"""
from __future__ import annotations


# ================ Deletions (4) =====================================

def test_batch682_strat_volume_spike_breakout_retest_deleted():
    """Pin (1): strat_volume_spike_breakout_retest no longer importable."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_volume_spike_breakout_retest"), (
        "B682 deletion: strat_volume_spike_breakout_retest must be REMOVED"
    )


def test_batch682_strat_pead_long_high_yoy_growth_only_deleted():
    """Pin (2): strat_pead_long_high_yoy_growth_only no longer importable."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_pead_long_high_yoy_growth_only"), (
        "B682 deletion: strat_pead_long_high_yoy_growth_only must be REMOVED"
    )


def test_batch682_strat_pead_short_negative_yoy_growth_deleted():
    """Pin (3): strat_pead_short_negative_yoy_growth no longer importable."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_pead_short_negative_yoy_growth"), (
        "B682 deletion: strat_pead_short_negative_yoy_growth must be REMOVED"
    )


def test_batch682_strat_buyback_8k_recent_long_deleted():
    """Pin (4): strat_buyback_8k_recent_long no longer importable."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_buyback_8k_recent_long"), (
        "B682 deletion: strat_buyback_8k_recent_long must be REMOVED"
    )


# ================ Registry removals (4) =============================

def test_batch682_volume_spike_breakout_retest_not_in_registry():
    """Pin (5)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "volume_spike_breakout_retest" not in ALL_STRATEGIES


def test_batch682_pead_long_high_yoy_growth_only_not_in_registry():
    """Pin (6)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "pead_long_high_yoy_growth_only" not in ALL_STRATEGIES


def test_batch682_pead_short_negative_yoy_growth_not_in_registry():
    """Pin (7)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "pead_short_negative_yoy_growth" not in ALL_STRATEGIES


def test_batch682_buyback_8k_recent_long_not_in_registry():
    """Pin (8)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "buyback_8k_recent_long" not in ALL_STRATEGIES


# ================ Count attestation (1) ============================

def test_batch682_all_strategies_count_218():
    """Pin (9): ALL_STRATEGIES total count == 218 post-B682 deletions.
    Was 222 pre-B682; -4 deletions (BR-15 + EV-3 + EV-4 + EV-7);
    BR-8 vol-gate swap is no-count-change."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 218, (
        f"B682 strategy count drift: expected 218 post-deletions; "
        f"got {len(ALL_STRATEGIES)}"
    )


# ================ BR-8 thesis-fix verification (3) =================

def test_batch682_dc20_break_retest_long_fires_on_vol_below_avg():
    """Pin (10): BR-8 LONG fires on Bulkowski-aligned vol_below_avg gate
    (post-B682 swap; pre-B682 used vol_spike_15x which contradicted
    Bulkowski thesis)."""
    from backtest.signals.screener import strat_dc20_break_retest
    s = {
        "resistance_break_retest": True,
        "vol_below_avg":           True,
        "adx_trending":            True,
    }
    out = strat_dc20_break_retest(s)
    assert out["fires"] is True
    assert out["direction"] == "long"


def test_batch682_dc20_break_retest_long_no_fire_on_vol_spike_only():
    """Pin (11): BR-8 LONG does NOT fire with vol_spike_15x but NO
    vol_below_avg (verifies the pre-B682 high-volume retest design is
    no longer wired)."""
    from backtest.signals.screener import strat_dc20_break_retest
    s = {
        "resistance_break_retest": True,
        "vol_spike_15x":           True,  # pre-B682 gate (no longer consumed)
        "vol_below_avg":           False, # post-B682 gate ABSENT
        "adx_trending":            True,
    }
    out = strat_dc20_break_retest(s)
    assert out["fires"] is False, (
        "B682 BR-8 regression: strategy fired on vol_spike_15x without "
        "vol_below_avg; post-B682 design requires vol_below_avg (Bulkowski "
        "2005 retest absorption alignment)"
    )


def test_batch682_dc20_break_retest_short_fires_on_vol_below_avg():
    """Pin (12): BR-8 SHORT symmetric — fires on support_break_retest +
    vol_below_avg + adx_trending."""
    from backtest.signals.screener import strat_dc20_break_retest
    s = {
        "support_break_retest": True,
        "vol_below_avg":        True,
        "adx_trending":         True,
    }
    out = strat_dc20_break_retest(s)
    assert out["fires"] is True
    assert out["direction"] == "short"
