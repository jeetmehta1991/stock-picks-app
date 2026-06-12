# Source: Decision 5 Cat 1 critical path + B713 Phase 0 + owner-approved Option A "option a" 2026-06-13 per CHECKLIST #77
"""B742 pin tests: dual `_strat3` first chunk -- 31 of 61 strategies converted
to explicit `borrow_ok` borrow gate on the SHORT branch at call site.

Per owner-approved Option A: consistent with B740/B741 pattern. Each dual
strategy now:
1. Appends `and not _short_borrow_trap_active(s)` to its SHORT fires variable
   (the 2nd positional arg to `_strat3(...)`).
2. Declares `borrow_ok` in `signals_used_short` (5th positional arg).
3. LONG branch UNCHANGED -- direction="long" is not gated by borrow trap.

Test discipline:
- pin1: count = 31
- pin2: all 31 registered
- pin3: SHORT-side fire under permissive bearish signals declares borrow_ok
- pin4: LONG-side fire under permissive bullish signals does NOT declare borrow_ok
- pin5: days_to_cover=10.0 + permissive bearish signals -> SHORT cannot fire
- pin6: days_to_cover=10.0 + permissive bullish signals -> LONG can still fire (gate is SHORT-only)
"""
from __future__ import annotations

from backtest.signals.screener import ALL_STRATEGIES

B742_STRATEGIES = [
    "pivot_s1_bounce",
    "pivot_s2_bounce",
    "pivot_r1_breakout",
    "pivot_r2_continuation",
    "cpr_narrow_bullish",
    "camarilla_s3_bounce",
    "camarilla_r4_breakout",
    "prev_day_high_break",
    "prev_day_low_bounce",
    "macd_crossover",
    "macd_fast_crossover",
    "hull_rsi",
    "williams_r_oversold",
    "roc_burst",
    "awesome_oscillator",
    "stochrsi_oversold",
    "ppo_crossover",
    "ultimate_oscillator",
    "golden_cross_50_200",
    "golden_cross_9_21",
    "golden_cross_20_50",
    "parabolic_sar_flip",
    "tema_dema",
    "ichimoku_tk_cross",
    "ichimoku_cloud_breakout",
    "adx_initiation",
    "supertrend_macd",
    "rsi_oversold",
    "rsi21_slow",
    "mfi_oversold",
    "cmf_flip",
]


def test_b742_pin1_count_matches_31():
    assert len(B742_STRATEGIES) == 31


def test_b742_pin2_all_31_registered():
    missing = [s for s in B742_STRATEGIES if s not in ALL_STRATEGIES]
    assert not missing, f"missing: {missing}"


def test_b742_pin3_short_branch_declares_borrow_ok_when_fires():
    """When the SHORT branch fires (permissive bearish signals + clean borrow),
    signals_used must contain `borrow_ok`.
    """
    s = _permissive_bearish_dict()
    found_short_fire = []
    for name in B742_STRATEGIES:
        r = ALL_STRATEGIES[name](s)
        if r["fires"] and r["direction"] == "short":
            assert "borrow_ok" in r["signals_used"], (
                f"{name} fired SHORT but signals_used missing borrow_ok: {r['signals_used']}"
            )
            found_short_fire.append(name)
    assert found_short_fire, (
        "Expected at least 1 of 31 to fire SHORT under permissive bearish signals; "
        "if zero, the bearish dict may be missing keys -- but at least confirm gate behaves correctly."
    )


def test_b742_pin4_long_branch_does_not_declare_borrow_ok_when_fires():
    """When the LONG branch fires (permissive bullish signals), signals_used
    must NOT contain `borrow_ok` -- the gate is SHORT-only.
    """
    s = _permissive_bullish_dict()
    found_long_fire = []
    for name in B742_STRATEGIES:
        r = ALL_STRATEGIES[name](s)
        if r["fires"] and r["direction"] == "long":
            assert "borrow_ok" not in r["signals_used"], (
                f"{name} fired LONG but signals_used CONTAINS borrow_ok (should be SHORT-only): {r['signals_used']}"
            )
            found_long_fire.append(name)
    assert found_long_fire, (
        "Expected at least 1 of 31 to fire LONG under permissive bullish signals"
    )


def test_b742_pin5_borrow_trap_blocks_short_branch():
    """days_to_cover=10.0 + permissive bearish signals -> SHORT does NOT fire."""
    s = _permissive_bearish_dict()
    s["days_to_cover"] = 10.0
    short_leaks = []
    for name in B742_STRATEGIES:
        r = ALL_STRATEGIES[name](s)
        if r["fires"] and r["direction"] == "short":
            short_leaks.append(name)
    assert not short_leaks, f"borrow trap should block SHORT but these fired: {short_leaks}"


def test_b742_pin6_borrow_trap_does_not_block_long_branch():
    """days_to_cover=10.0 + permissive bullish signals -> LONG can still fire
    (the borrow gate is SHORT-only; LONG branch is unaffected by design).
    """
    s = _permissive_bullish_dict()
    s["days_to_cover"] = 10.0  # high DTC, but we are going LONG -- not blocked
    long_fires = []
    for name in B742_STRATEGIES:
        r = ALL_STRATEGIES[name](s)
        if r["fires"] and r["direction"] == "long":
            long_fires.append(name)
    assert long_fires, (
        f"At least 1 LONG fire expected despite high DTC (gate is SHORT-only); got 0"
    )


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _permissive_bearish_dict() -> dict:
    return {
        "days_to_cover": 0.0,
        # Pivot SHORT branch
        "near_r1": True, "near_r2": True, "near_r3": True, "near_r4": True,
        "near_camarilla_r4": True,
        # Candle bearish
        "shooting_star": True, "bearish_engulfing": True, "bearish_pin_bar": True,
        "below_prev_low": True, "below_prev_day_low": True,
        # OBV / MFI / Stoch
        "obv_bearish": True, "mfi_overbought": True, "cmf_negative": True,
        "stochrsi_overbought": True, "stoch_bearish_cross": True,
        # Momentum bearish
        "rsi_14": 75.0, "rsi_21": 75.0, "rsi_9": 75.0, "rsi_14_falling": True,
        "macd_bearish": True, "macd_bear_cross_recent": True,
        "ppo_bearish": True, "williams_r": -10, "roc_12": -10,
        "awesome_oscillator_bearish": True, "ultimate_oscillator_bearish": True,
        # Trend bearish
        "below_ema_50": True, "below_ema_200": True, "below_sma_50": True,
        "below_ema_200_break_recent_5d": True,
        "death_cross_50_200_recent": True, "death_cross_9_21_recent": True,
        "death_cross_20_50_recent": True,
        # Trend systems
        "supertrend_bearish": True, "supertrend_flip_recent_short_5d": True,
        "ichi_below_cloud": True, "ichi_tk_bearish_cross": True,
        "ichi_below_cloud_break_recent_5d": True,
        "psar_flip_dn": True, "adx_trending": True, "adx_initiation_down": True,
        "tema_dema_bearish": True,
        # CPR
        "cpr_narrow_tight": True, "cpr_narrow": True,
    }


def _permissive_bullish_dict() -> dict:
    return {
        "days_to_cover": 0.0,
        # Pivot LONG branch
        "near_s1": True, "near_s2": True, "near_s3": True, "near_s4": True,
        "near_camarilla_s3": True,
        # Candle bullish
        "hammer": True, "bullish_engulfing": True, "bullish_pin_bar": True,
        "above_prev_high": True, "above_prev_day_high": True,
        # OBV / MFI / Stoch
        "obv_bullish": True, "mfi_oversold": True, "cmf_positive": True,
        "stochrsi_oversold": True, "stoch_bullish_cross": True,
        # Momentum bullish
        "rsi_14": 25.0, "rsi_21": 25.0, "rsi_9": 25.0, "rsi_14_rising": True,
        "macd_bullish": True, "macd_bull_cross_recent": True,
        "ppo_bullish": True, "williams_r": -90, "roc_12": 10,
        "awesome_oscillator_bullish": True, "ultimate_oscillator_bullish": True,
        # Trend bullish
        "price_above_ema_50": True, "price_above_ema_200": True, "above_sma_50": True,
        "price_above_ema_200_break_recent_5d": True,
        "golden_cross_50_200_recent": True, "golden_cross_9_21_recent": True,
        "golden_cross_20_50_recent": True,
        # Trend systems bullish
        "supertrend_bullish": True, "supertrend_flip_recent_long_5d": True,
        "ichi_above_cloud": True, "ichi_tk_bullish_cross": True,
        "ichi_above_cloud_break_recent_5d": True,
        "psar_flip_up": True, "adx_trending": True, "adx_initiation_up": True,
        "tema_dema_bullish": True,
        # CPR
        "cpr_narrow_tight": True, "cpr_narrow": True,
    }
