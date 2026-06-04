"""Batch 580 (2026-06-04) -- wire Turtle Soup long + short per
Layer 2D ICT inline-spec protocol (Option A B579).

First ICT pattern wired via inline-chat specification per
feedback_layer_2d_ict_inline_specification (PENDING-FORM blocker
dropped B579). Owner spec 2026-06-04: 6 ICT strategies + 7
foundational concepts; audit showed 1 already wired (OTE), 2
wireable now (Turtle Soup + Judas Swing variant), 3 architecturally
blocked on daily-bar architecture (Silver Bullet / MMBM / Week-open
gap). Owner picked Turtle Soup first.

Source: Linda Bradford Raschke 'Street Smarts' (1996). Mean-reversion
fade of stop-hunt breakouts. Pre-dates and feeds into modern ICT
'Judas Swing' / liquidity-sweep-reversal framing; pure pattern
without structure-shift confirmation.

Strategy logic:
  LONG  fires when: smc_liquidity_swept_dn (downside sweep) AND
                    NOT below_prev_low (close back inside range) AND
                    close_above_open (bullish reversal bar)
  SHORT fires when: smc_liquidity_swept_up (upside sweep) AND
                    NOT above_prev_high (close back inside range) AND
                    close_below_open (bearish reversal bar)

Pins:

  (1) Both strategies registered in ALL_STRATEGIES
  (2) ALL_STRATEGIES count is now 207 (was 205 pre-B580)
  (3) LONG fires when all 3 conditions True
  (4) LONG does not fire when sweep missing
  (5) LONG does not fire when close still below prior low
  (6) LONG does not fire when bar is bearish (close_above_open False)
  (7) SHORT mirror correctness (fires when symmetric conditions True)
  (8) Direction = long / short respectively
  (9) Category = 'ict' (Layer 2D classification)
  (10) Long + short are independent (don't crosstalk on same bar)
"""
from __future__ import annotations


def test_batch580_both_registered():
    """Pin (1)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "turtle_soup_long" in ALL_STRATEGIES
    assert "turtle_soup_short" in ALL_STRATEGIES


def test_batch580_count_at_least_207():
    """Pin (2). Layer 2D first inline-spec ICT pattern moves count 205 -> 207.
    Use >= so later batches (B581 +6) don't trip this pin."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) >= 207


def test_batch580_long_fires_all_conditions_true():
    """Pin (3)."""
    from backtest.signals.screener import strat_turtle_soup_long
    out = strat_turtle_soup_long({
        "smc_liquidity_swept_dn": True,
        "below_prev_low": False,
        "close_above_open": True,
    })
    assert out["fires"] is True


def test_batch580_long_no_sweep_no_fire():
    """Pin (4): missing sweep -> no fire."""
    from backtest.signals.screener import strat_turtle_soup_long
    out = strat_turtle_soup_long({
        "smc_liquidity_swept_dn": False,
        "below_prev_low": False,
        "close_above_open": True,
    })
    assert out["fires"] is False


def test_batch580_long_below_prev_low_no_fire():
    """Pin (5): still below prior-day-low -> no fire (no return-to-range)."""
    from backtest.signals.screener import strat_turtle_soup_long
    out = strat_turtle_soup_long({
        "smc_liquidity_swept_dn": True,
        "below_prev_low": True,
        "close_above_open": True,
    })
    assert out["fires"] is False


def test_batch580_long_bearish_bar_no_fire():
    """Pin (6): bearish bar (close < open) -> no fire (no rejection)."""
    from backtest.signals.screener import strat_turtle_soup_long
    out = strat_turtle_soup_long({
        "smc_liquidity_swept_dn": True,
        "below_prev_low": False,
        "close_above_open": False,
    })
    assert out["fires"] is False


def test_batch580_short_mirror():
    """Pin (7)."""
    from backtest.signals.screener import strat_turtle_soup_short
    # All symmetric conditions True
    out = strat_turtle_soup_short({
        "smc_liquidity_swept_up": True,
        "above_prev_high": False,
        "close_below_open": True,
    })
    assert out["fires"] is True
    # Missing upside sweep
    out_no_sweep = strat_turtle_soup_short({
        "smc_liquidity_swept_up": False,
        "above_prev_high": False,
        "close_below_open": True,
    })
    assert out_no_sweep["fires"] is False


def test_batch580_directions():
    """Pin (8)."""
    from backtest.signals.screener import strat_turtle_soup_long, strat_turtle_soup_short
    out_l = strat_turtle_soup_long({
        "smc_liquidity_swept_dn": True,
        "below_prev_low": False,
        "close_above_open": True,
    })
    out_s = strat_turtle_soup_short({
        "smc_liquidity_swept_up": True,
        "above_prev_high": False,
        "close_below_open": True,
    })
    assert out_l["direction"] == "long"
    assert out_s["direction"] == "short"


def test_batch580_category_ict():
    """Pin (9): Layer 2D classification = 'ict'."""
    from backtest.signals.screener import strat_turtle_soup_long, strat_turtle_soup_short
    out_l = strat_turtle_soup_long({
        "smc_liquidity_swept_dn": True,
        "below_prev_low": False,
        "close_above_open": True,
    })
    out_s = strat_turtle_soup_short({
        "smc_liquidity_swept_up": True,
        "above_prev_high": False,
        "close_below_open": True,
    })
    assert out_l["category"] == "ict"
    assert out_s["category"] == "ict"


def test_batch580_no_crosstalk():
    """Pin (10): on a downside-sweep bar, LONG fires + SHORT does not.
    On an upside-sweep bar, SHORT fires + LONG does not."""
    from backtest.signals.screener import strat_turtle_soup_long, strat_turtle_soup_short
    # Downside sweep day
    s_down = {
        "smc_liquidity_swept_dn": True, "smc_liquidity_swept_up": False,
        "below_prev_low": False, "above_prev_high": True,
        "close_above_open": True, "close_below_open": False,
    }
    assert strat_turtle_soup_long(s_down)["fires"] is True
    assert strat_turtle_soup_short(s_down)["fires"] is False
    # Upside sweep day
    s_up = {
        "smc_liquidity_swept_dn": False, "smc_liquidity_swept_up": True,
        "below_prev_low": True, "above_prev_high": False,
        "close_above_open": False, "close_below_open": True,
    }
    assert strat_turtle_soup_long(s_up)["fires"] is False
    assert strat_turtle_soup_short(s_up)["fires"] is True
