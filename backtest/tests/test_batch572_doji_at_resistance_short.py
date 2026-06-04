"""Batch 572 (2026-06-04) -- wire strat_doji_at_resistance_short
per Stage 4 Candle cluster walk (B571 Class 7 NEW_STRATEGY
candidate identified; B572 executes the wiring on the spot per
feedback_wire_new_strategies_on_the_spot).

Source: per CHECKLIST #77, owner directive 2026-06-04 in chat:
  "Lets do only 1 strategy at a time! so right now only doji bull
  and bear needs to be executed this turn. continue"

The doji_at_support (long) strategy existed; its symmetric inverse
doji_at_resistance_short was missing despite all producer signals
being computed (near_r1 / near_r2 / at_key_fib / vol_spike_15x /
doji). Mirror of Nison's classical doji-at-support pattern at
resistance.

Pins:

  (1) strat_doji_at_resistance_short registered in ALL_STRATEGIES
  (2) ALL_STRATEGIES count is now 205 (was 204 pre-B572)
  (3) fires when all 4 conditions True (doji + at-resistance + vol)
  (4) does not fire when any condition is False
  (5) direction is 'short' (not 'long' - mirror correctness)
  (6) category is 'candle'
  (7) doji_at_support unchanged (no regression)
  (8) doji_at_support fires LONG, doji_at_resistance_short fires SHORT
      on the same doji + vol_spike day with mirrored level conditions
"""
from __future__ import annotations


def test_batch572_doji_at_resistance_short_registered():
    """Pin (1)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "doji_at_resistance_short" in ALL_STRATEGIES


def test_batch572_all_strategies_count_205():
    """Pin (2). Count assertion - rises when new strategies wire,
    matches feedback_doc_count_drift_must_be_test_pinned discipline."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 205, (
        f"ALL_STRATEGIES count = {len(ALL_STRATEGIES)}; expected 205 "
        f"after B572 wiring of doji_at_resistance_short. If count "
        f"increased legitimately (new strategy added), update this pin."
    )


def test_batch572_fires_when_all_conditions_true():
    """Pin (3): doji + near_r1 + vol_spike_15x -> fires."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    out = strat_doji_at_resistance_short({
        "doji": True,
        "near_r1_wide": True,
        "vol_spike_15x": True,
    })
    assert out["fires"] is True


def test_batch572_does_not_fire_without_doji():
    """Pin (4a): no doji -> no fire."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    out = strat_doji_at_resistance_short({
        "doji": False,
        "near_r1_wide": True,
        "vol_spike_15x": True,
    })
    assert out["fires"] is False


def test_batch572_does_not_fire_without_resistance():
    """Pin (4b): no resistance level proximity -> no fire."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    out = strat_doji_at_resistance_short({
        "doji": True,
        "near_r1_wide": False,
        "near_r2_wide": False,
        "at_key_fib_wide": False,
        "vol_spike_15x": True,
    })
    assert out["fires"] is False


def test_batch572_does_not_fire_without_volume_spike():
    """Pin (4c): doji + at resistance but no vol spike -> no fire."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    out = strat_doji_at_resistance_short({
        "doji": True,
        "near_r2_wide": True,
        "vol_spike_15x": False,
    })
    assert out["fires"] is False


def test_batch572_fires_at_key_fib_alternative():
    """Pin (4d): at_key_fib is the alternative resistance proxy
    (R1/R2 OR at_key_fib). Verify fib triggers when pivots don't."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    out = strat_doji_at_resistance_short({
        "doji": True,
        "near_r1_wide": False,
        "near_r2_wide": False,
        "at_key_fib_wide": True,
        "vol_spike_15x": True,
    })
    assert out["fires"] is True


def test_batch572_direction_is_short():
    """Pin (5): direction must be 'short' - mirror correctness."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    out = strat_doji_at_resistance_short({
        "doji": True,
        "near_r1_wide": True,
        "vol_spike_15x": True,
    })
    assert out["direction"] == "short"


def test_batch572_category_is_candle():
    """Pin (6)."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    out = strat_doji_at_resistance_short({
        "doji": True,
        "near_r1_wide": True,
        "vol_spike_15x": True,
    })
    assert out["category"] == "candle"


def test_batch572_long_variant_unchanged():
    """Pin (7): no regression on strat_doji_at_support."""
    from backtest.signals.screener import strat_doji_at_support
    out = strat_doji_at_support({
        "doji": True,
        "near_s1_wide": True,
        "vol_spike_15x": True,
    })
    assert out["fires"] is True
    assert out["direction"] == "long"


def test_batch572_mirror_invariant():
    """Pin (8): on a doji + vol_spike day, the LONG fires only at
    support, the SHORT fires only at resistance. No crosstalk.
    Updated B574: uses _wide flags exclusively per narrow-scope fix."""
    from backtest.signals.screener import (
        strat_doji_at_support, strat_doji_at_resistance_short,
    )
    # At support only
    s_at_support = {"doji": True, "vol_spike_15x": True,
                    "near_s1_wide": True, "near_r1_wide": False,
                    "at_key_fib_wide": False}
    assert strat_doji_at_support(s_at_support)["fires"] == True
    assert strat_doji_at_resistance_short(s_at_support)["fires"] == False
    # At resistance only
    s_at_resistance = {"doji": True, "vol_spike_15x": True,
                       "near_s1_wide": False, "near_s2_wide": False,
                       "near_r1_wide": True, "at_key_fib_wide": False}
    assert strat_doji_at_support(s_at_resistance)["fires"] == False
    assert strat_doji_at_resistance_short(s_at_resistance)["fires"] == True
