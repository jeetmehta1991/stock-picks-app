"""Batch 600 (2026-06-05) -- Stage 4 walk of strat_volume_spike_breakout
_retest (dual) per owner directives 2026-06-05.

Owner directives applied (answers A + C + D + E approved; B skipped
per refined recommendation to preserve differentiator vs donchian
retest pair):
  (a) Added bullish-bar + strong-close gates (close_above_open +
      close_in_top_40pct_of_range and mirrors).
  (c) Replaced standard resistance_break_retest / support_break_retest
      with B594 LOCAL strong variants dc20_resistance_break_retest
      _strong / dc20_support_break_retest_strong.
  (d) Replaced cumulative above_vwap with Brian Shannon (2022) AVWAP:
        LONG : above_avwap_20low
        SHORT: NOT above_avwap_20high
  (e) Regime affinity: relies on Batch 291 direction-aware default.

SKIPPED (b): vol_spike_2x retained as the deliberate differentiator vs
the donchian retest pair which uses vol_below_avg. Two distinct retest
playbooks now coexist:
  - donchian retest pair (B596 walked): Bulkowski supply-absorption
    thesis on LOWER volume.
  - volume_spike_breakout_retest (B600 walked): high-conviction 2x-volume
    retest accumulation/distribution.

Pins:
  (1) LONG fires with all 5 new gates True
  (2) SHORT fires with all 5 new gates True
  (3) Legacy 3-gate fixture (resistance_break_retest + vol_spike_2x +
      above_vwap) does NOT fire post-B600
  (4) NO CONVERGENCE vs donchian_breakout_retest_long: same trigger dict
      that fires volume_spike_breakout_retest LONG should NOT fire
      donchian_breakout_retest_long (because the latter requires
      vol_below_avg, while this fixture has vol_spike_2x True and
      vol_below_avg False)
  (5) Regime default LONG = {bull, neutral}; SHORT = {bear, crisis,
      neutral}
  (6) ALL_STRATEGIES count preserved at 217
"""
from __future__ import annotations

import pytest


def test_batch600_long_fires_5_gates():
    """Pin (1)."""
    from backtest.signals.screener import strat_volume_spike_breakout_retest
    s = {
        "dc20_resistance_break_retest_strong": True,
        "vol_spike_2x": True,
        "above_avwap_20low": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    out = strat_volume_spike_breakout_retest(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch600_short_fires_5_gates():
    """Pin (2)."""
    from backtest.signals.screener import strat_volume_spike_breakout_retest
    s = {
        "dc20_support_break_retest_strong": True,
        "vol_spike_2x": True,
        "below_avwap_20high": True,  # B612 refactor: positive signal
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out = strat_volume_spike_breakout_retest(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch600_legacy_3_gate_fixture_blocked():
    """Pin (3): legacy fixture (resistance_break_retest + vol_spike_2x
    + above_vwap) does NOT fire post-B600."""
    from backtest.signals.screener import strat_volume_spike_breakout_retest
    s = {
        "resistance_break_retest": True,
        "vol_spike_2x": True,
        "above_vwap": True,
    }
    assert strat_volume_spike_breakout_retest(s)["fires"] is False, (
        "B600 added 2 new gates + swapped 2; legacy fixture must not fire"
    )


def test_batch600_no_convergence_vs_donchian_retest_pair_long():
    """Pin (4) LONG: fixture that fires volume_spike_breakout_retest LONG
    (vol_spike_2x True, vol_below_avg implicit False) must NOT fire
    donchian_breakout_retest_long (which requires vol_below_avg).
    Preserves the differentiator post-B600."""
    from backtest.signals.screener import (
        strat_volume_spike_breakout_retest,
        strat_donchian_breakout_retest_long,
    )
    s = {
        "dc20_resistance_break_retest_strong": True,
        "vol_spike_2x": True,
        # vol_below_avg implicitly False (a dict without key returns None on .get())
        "above_avwap_20low": True,
        "macd_12_26_9_bullish": True,
        "close_above_open": True,
        "close_in_top_40pct_of_range": True,
    }
    out_vsbr = strat_volume_spike_breakout_retest(s)
    out_dbrl = strat_donchian_breakout_retest_long(s)
    assert out_vsbr["fires"] is True, "vol_spike retest LONG must fire"
    assert out_dbrl["fires"] is False, (
        "donchian retest LONG requires vol_below_avg - must NOT fire on "
        "the high-conviction 2x-volume retest fixture (no convergence)"
    )


def test_batch600_no_convergence_vs_donchian_retest_pair_short():
    """Pin (4) SHORT mirror."""
    from backtest.signals.screener import (
        strat_volume_spike_breakout_retest,
        strat_donchian_breakdown_retest_short,
    )
    s = {
        "dc20_support_break_retest_strong": True,
        "vol_spike_2x": True,
        "below_avwap_20high": True,  # B612 refactor: positive signal
        "macd_12_26_9_bullish": False,
        "close_below_open": True,
        "close_in_bottom_40pct_of_range": True,
    }
    out_vsbr = strat_volume_spike_breakout_retest(s)
    out_dbrs = strat_donchian_breakdown_retest_short(s)
    assert out_vsbr["fires"] is True
    assert out_dbrs["fires"] is False, (
        "donchian retest SHORT requires vol_below_avg - must NOT fire here"
    )


def test_batch600_regime_default_long_bull_neutral():
    """Pin (5) LONG."""
    from backtest.engine.regime_selector import (
        STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime,
    )
    assert "volume_spike_breakout_retest" not in STRATEGY_REGIME_AFFINITY
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "volume_spike_breakout_retest", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "volume_spike_breakout_retest", r, direction="long"
        ) is False


def test_batch600_regime_default_short_bear_crisis_neutral():
    """Pin (5) SHORT."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "volume_spike_breakout_retest", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "volume_spike_breakout_retest", "bull", direction="short"
    ) is False


def test_batch600_all_strategies_count_preserved_at_217():
    """Pin (6): subsequent batches added; current count 221."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
