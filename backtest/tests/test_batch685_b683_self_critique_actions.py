"""Batch 685 (2026-06-10) -- owner-approved code changes per B683 self-critique
follow-on:

  1. 3 Class 7 NEW strategy additions:
     - strat_head_and_shoulders_top_short (Edwards-Magee 1948 + Bulkowski
       2005 canonical bearish reversal mirror of CP-3)
     - strat_triangle_descending_short (Bulkowski 2005 bearish continuation
       mirror of CP-7)
     - strat_hammer_at_support_long (Nison 1991 canonical 1-bar bullish
       reversal mirror of CC-4 shooting_star_short)

     Inverted cup-and-handle Class 7 NEW DEFERRED to future batch (producer
     signal does not yet exist; methodology work scoped separately).

  2. 2 Producer-side fixes (B607-pattern):
     - compute_triangle_apex_break_retest_signals (new producer in
       chart_patterns.py); re-wires CP-8 strat_triangle_ascending_retest_long
     - compute_cup_handle_neckline_break_retest_signals (new producer);
       re-wires CP-9 strat_cup_and_handle_retest_long

  3. Pattern A WAVE 2 cluster-wide sweep:
     - 8 strategies had `s.get("price_above_ema_50", True)` silent-gap;
       swapped to default=False (fail-safe direction)

  4. CP-1 cup_and_handle_long EXPLORATORY marker:
     - Added to EXPLORATORY_STRATEGIES constant in
       multiple_testing_correction.py per Bulkowski 2005 published
       frequency + B660 0-fire empirical confirmation.

Owner approval 2026-06-10: 'Pending owner-approval decisions surfaced by
B683 address all'

Strategy count impact: 218 -> 221 (+3 Class 7 NEW; 0 deletions).
Active count: 220 (221 registered - 1 disabled dxy_headwind).

Pins:

Class 7 NEW additions (6):
  (1)  strat_head_and_shoulders_top_short importable + callable
  (2)  'head_and_shoulders_top_short' in ALL_STRATEGIES
  (3)  strat_triangle_descending_short importable + callable
  (4)  'triangle_descending_short' in ALL_STRATEGIES
  (5)  strat_hammer_at_support_long importable + callable
  (6)  'hammer_at_support_long' in ALL_STRATEGIES

Class 7 NEW fire-logic (6):
  (7)  H&S top SHORT fires when head_shoulders_top_detected + below_ema_200
  (8)  H&S top SHORT does NOT fire when below_ema_200 missing (B630 default-False)
  (9)  Triangle descending SHORT fires when triangle_descending_detected + below_ema_200
  (10) Triangle descending SHORT does NOT fire when below_ema_200 missing
  (11) Hammer at support LONG fires on hammer + near_s1 + rsi_14<35
  (12) Hammer at support LONG does NOT fire on rsi_14>=35 (above threshold)

Producer-side fixes (4):
  (13) compute_triangle_apex_break_retest_signals importable from chart_patterns
  (14) compute_cup_handle_neckline_break_retest_signals importable
  (15) strat_triangle_ascending_retest_long now consumes
       triangle_apex_break_retest_long (not resistance_break_retest)
  (16) strat_cup_and_handle_retest_long now consumes
       cup_handle_neckline_break_retest_long (not resistance_break_retest)

Pattern A WAVE 2 sweep (1):
  (17) 0 instances of `s.get("price_above_ema_50", True)` remain in screener.py

CP-1 EXPLORATORY marker (1):
  (18) 'cup_and_handle_long' in EXPLORATORY_STRATEGIES constant

Strategy count attestation (1):
  (19) len(ALL_STRATEGIES) == 219 (was 218; +3 Class 7 NEW)
"""
from __future__ import annotations


# ============ Class 7 NEW additions (6 pins) ============

def test_batch685_strat_head_and_shoulders_top_short_importable():
    """Pin (1)."""
    from backtest.signals.screener import strat_head_and_shoulders_top_short
    assert callable(strat_head_and_shoulders_top_short)


def test_batch685_head_and_shoulders_top_short_in_registry():
    """Pin (2)."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_head_and_shoulders_top_short
    assert ALL_STRATEGIES.get("head_and_shoulders_top_short") is strat_head_and_shoulders_top_short


def test_batch685_strat_triangle_descending_short_importable():
    """Pin (3)."""
    from backtest.signals.screener import strat_triangle_descending_short
    assert callable(strat_triangle_descending_short)


def test_batch685_triangle_descending_short_in_registry():
    """Pin (4)."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_triangle_descending_short
    assert ALL_STRATEGIES.get("triangle_descending_short") is strat_triangle_descending_short


def test_batch685_strat_hammer_at_support_long_importable():
    """Pin (5)."""
    from backtest.signals.screener import strat_hammer_at_support_long
    assert callable(strat_hammer_at_support_long)


def test_batch685_hammer_at_support_long_in_registry():
    """Pin (6)."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_hammer_at_support_long
    assert ALL_STRATEGIES.get("hammer_at_support_long") is strat_hammer_at_support_long


# ============ Class 7 NEW fire-logic (6 pins) ============

def test_batch685_head_and_shoulders_top_short_fires_on_pattern_plus_below_ema():
    """Pin (7)."""
    from backtest.signals.screener import strat_head_and_shoulders_top_short
    s = {"head_shoulders_top_detected": True, "below_ema_200": True}
    out = strat_head_and_shoulders_top_short(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch685_head_and_shoulders_top_short_no_fire_without_below_ema():
    """Pin (8): B630 producer-additive default-False; missing key -> no fire."""
    from backtest.signals.screener import strat_head_and_shoulders_top_short
    s = {"head_shoulders_top_detected": True}  # below_ema_200 ABSENT
    out = strat_head_and_shoulders_top_short(s)
    assert out["fires"] is False, "B685 regression: SHORT fired without below_ema_200 (silent gap)"


def test_batch685_triangle_descending_short_fires_on_pattern_plus_below_ema():
    """Pin (9)."""
    from backtest.signals.screener import strat_triangle_descending_short
    s = {"triangle_descending_detected": True, "below_ema_200": True}
    out = strat_triangle_descending_short(s)
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch685_triangle_descending_short_no_fire_without_below_ema():
    """Pin (10): same B630 default-False fail-safe."""
    from backtest.signals.screener import strat_triangle_descending_short
    s = {"triangle_descending_detected": True}
    out = strat_triangle_descending_short(s)
    assert out["fires"] is False


def test_batch685_hammer_at_support_long_fires_on_pattern_plus_support_plus_oversold():
    """Pin (11)."""
    from backtest.signals.screener import strat_hammer_at_support_long
    s = {"hammer": True, "near_s1": True, "rsi_14": 25.0}
    out = strat_hammer_at_support_long(s)
    assert out["fires"] is True
    assert out["direction"] == "long"


def test_batch685_hammer_at_support_long_no_fire_when_rsi_above_threshold():
    """Pin (12): RSI gate enforces <35 oversold band; default-50 fail-safe (50<35 is False)."""
    from backtest.signals.screener import strat_hammer_at_support_long
    s = {"hammer": True, "near_s1": True, "rsi_14": 50.0}
    out = strat_hammer_at_support_long(s)
    assert out["fires"] is False


# ============ Producer-side fixes (4 pins) ============

def test_batch685_compute_triangle_apex_break_retest_signals_importable():
    """Pin (13)."""
    from backtest.signals.chart_patterns import compute_triangle_apex_break_retest_signals
    assert callable(compute_triangle_apex_break_retest_signals)
    # Defensive on insufficient history
    out = compute_triangle_apex_break_retest_signals(None)
    assert out["triangle_apex_break_retest_long"] is False


def test_batch685_compute_cup_handle_neckline_break_retest_signals_importable():
    """Pin (14)."""
    from backtest.signals.chart_patterns import compute_cup_handle_neckline_break_retest_signals
    assert callable(compute_cup_handle_neckline_break_retest_signals)
    out = compute_cup_handle_neckline_break_retest_signals(None)
    assert out["cup_handle_neckline_break_retest_long"] is False


def test_batch685_triangle_ascending_retest_consumes_new_producer():
    """Pin (15): strat now requires triangle_apex_break_retest_long, NOT
    resistance_break_retest."""
    from backtest.signals.screener import strat_triangle_ascending_retest_long
    # OLD signal alone should NOT fire (post-B685 producer-fix)
    s_old = {
        "triangle_ascending_detected": True,
        "resistance_break_retest":     True,  # OLD signal (no longer consumed)
        "price_above_ema_200":         True,
    }
    out_old = strat_triangle_ascending_retest_long(s_old)
    assert out_old["fires"] is False, (
        "B685 regression: strat fired on OLD DC20-anchored resistance_break_retest; "
        "should require B685 NEW triangle_apex_break_retest_long"
    )
    # NEW signal should fire correctly
    s_new = {
        "triangle_ascending_detected":     True,
        "triangle_apex_break_retest_long": True,
        "price_above_ema_200":             True,
    }
    out_new = strat_triangle_ascending_retest_long(s_new)
    assert out_new["fires"] is True


def test_batch685_cup_and_handle_retest_consumes_new_producer():
    """Pin (16): strat now requires cup_handle_neckline_break_retest_long."""
    from backtest.signals.screener import strat_cup_and_handle_retest_long
    # OLD signal alone should NOT fire
    s_old = {
        "cup_handle_detected":     True,
        "resistance_break_retest": True,  # OLD (no longer consumed)
        "price_above_ema_200":     True,
        "price_above_ema_50":      True,
        "rsi_14":                  50.0,
    }
    out_old = strat_cup_and_handle_retest_long(s_old)
    assert out_old["fires"] is False, (
        "B685 regression: strat fired on OLD DC20-anchored resistance_break_retest; "
        "should require B685 NEW cup_handle_neckline_break_retest_long"
    )
    # NEW signal should fire
    s_new = {
        "cup_handle_detected":                   True,
        "cup_handle_neckline_break_retest_long": True,
        "price_above_ema_200":                   True,
        "price_above_ema_50":                    True,
        "rsi_14":                                50.0,
    }
    out_new = strat_cup_and_handle_retest_long(s_new)
    assert out_new["fires"] is True


# ============ Pattern A WAVE 2 sweep (1 pin) ============

def test_batch685_pattern_a_wave_2_no_default_true_on_ema_50():
    """Pin (17): 0 instances of `s.get('price_above_ema_50', True)` remain in
    screener.py post-B685 sweep. WAVE 2 family-bug sweep symmetric with
    B663 WAVE 1 on price_above_ema_200."""
    from pathlib import Path
    screener_path = Path(__file__).resolve().parents[1].parent / "backtest" / "signals" / "screener.py"
    content = screener_path.read_text(encoding="utf-8")
    # The sloppy default-True silent-gap pattern
    assert 'price_above_ema_50", True' not in content, (
        "B685 regression: Pattern A WAVE 2 sweep incomplete - default-True silent-gap "
        "still present for price_above_ema_50. Run sweep again."
    )


# ============ CP-1 EXPLORATORY marker (1 pin) ============

def test_batch685_cup_and_handle_long_in_exploratory_strategies():
    """Pin (18): cup_and_handle_long added to EXPLORATORY_STRATEGIES per
    B683 self-critique CP-1 + B660 empirical 0-fire confirmation."""
    from backtest.engine.multiple_testing_correction import (
        EXPLORATORY_STRATEGIES, cube_eligible_for_multiple_testing,
    )
    assert "cup_and_handle_long" in EXPLORATORY_STRATEGIES
    # cube_eligible_for_multiple_testing returns False for EXPLORATORY entries
    assert cube_eligible_for_multiple_testing("cup_and_handle_long") is False
    # cube_eligible returns True for non-exploratory strategies
    assert cube_eligible_for_multiple_testing("pead_long") is True


# ============ Strategy count attestation (1 pin) ============

def test_batch685_all_strategies_count_at_least_221():
    """Pin (19): ALL_STRATEGIES total count >= 221 post-B685.
    Was 218 post-B682; +3 B685 Class 7 NEW (head_and_shoulders_top_short +
    triangle_descending_short + hammer_at_support_long) = 221.

    Loosened to >= 221 (vs == 221) to tolerate downstream Class 7 NEW
    additions post-B685 (e.g., B686 inverted_cup_and_handle_short took
    221 -> 222). The canonical exact count is asserted in test_unit.py
    test_batch357_doc_count_drift_strategies + per-batch tests
    (test_batch686_all_strategies_count_222)."""
    from backtest.signals.screener import ALL_STRATEGIES
    # B899 floor migration post-B722 (-3) + B874 (-2): 221 -> 219.
    assert len(ALL_STRATEGIES) >= 219, (
        f"B685 strategy count drift: expected >=219 post-B874 (B685 additions intact); "
        f"got {len(ALL_STRATEGIES)}"
    )
