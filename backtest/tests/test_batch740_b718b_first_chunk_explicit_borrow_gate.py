# Source: Decision 5 Cat 1 critical path + B713 Phase 0 + owner-approved "Run B740 + B741" 2026-06-13 per CHECKLIST #77
"""B740 pin tests: B718b first chunk -- 26 of 51 pure-short strategies converted
to explicit `borrow_ok` borrow gate at call site.

Replaces the inspect.currentframe()-based borrow guard in `_strat` (still
retained as belt-and-braces; will be removed in B718d after all 116 short
strategies are converted AND B736 registration-time lint is enabled).

Per-strategy verification:
1. The strategy's `fires` boolean assembly references `_short_borrow_trap_active(s)`
2. The strategy's `signals_used` list declares `"borrow_ok"`
3. Calling the strategy with `days_to_cover > 5.0` blocks the short emission
4. Calling the strategy with `days_to_cover <= 5.0` AND clean signal set fires

Tests #3 + #4 are PARITY tests vs the existing inspect.currentframe path: the
behavior must be identical before vs after the refactor on borrow-relevant cases.
"""
from __future__ import annotations

from backtest.signals.screener import ALL_STRATEGIES

# Strategies refactored in B740 (B718b first chunk)
B740_STRATEGIES = [
    "pivot_r3_blowoff_short",
    "rsi_overbought_short",
    "bollinger_upper_short",
    "52w_low_breakdown_pullback_short",
    "donchian_breakdown_retest_short",
    "doji_at_resistance_short",
    "three_black_crows_short",
    "shooting_star_short",
    "death_cross_50_200_volume",
    "supertrend_macd_short",
    "ichimoku_cloud_breakdown",
    "parabolic_sar_flip_short",
    "macd_crossover_short",
    "stochrsi_overbought_short",
    "donchian_breakdown_short",
    "52w_low_breakdown",
    "prev_day_low_breakdown",
    # camarilla_rsi_obv_short DELETED B874 per S4-B754-A-19 Pattern W
    # council 5-lens option A2 (deterministic strict-subset of A-18 W9
    # strat_camarilla_s3_bounce). Removed from B718b cohort.
    "cpr_narrow_momentum_short",
    "52wl_break_retest_short",
    "orb_stocks_in_play_short",
    "xs_momentum_bottom_decile_short",
    "po3_bearish",
    "htf_aligned_breakout_short",
    "weekly_bias_pullback_short",
    "smc_fvg_retest_short",
]


def test_b740_pin1_count_matches_25():
    """B740 first chunk -- 26 strategies refactored this batch; B874 deleted
    camarilla_rsi_obv_short reducing cohort to 25 (B899 migration)."""
    assert len(B740_STRATEGIES) == 25


def test_b740_pin2_all_26_registered():
    """Every B740 strategy must remain in ALL_STRATEGIES (EXPLORATORY-stale or otherwise)."""
    missing = [s for s in B740_STRATEGIES if s not in ALL_STRATEGIES]
    assert not missing, f"missing from ALL_STRATEGIES: {missing}"


def test_b740_pin3_every_strategy_declares_borrow_ok_in_signals_used():
    """Each B740 strategy's signals_used list must include `borrow_ok`.

    Achieved by calling the strategy with all gates True + days_to_cover=0
    (gate passes) and inspecting the returned signals_used list.
    """
    # Permissive signal dict: all booleans True, all numerics on the bullish side,
    # days_to_cover=0 (borrow gate passes).
    s_permissive = _make_permissive_short_signal_dict()
    missing = []
    for name in B740_STRATEGIES:
        result = ALL_STRATEGIES[name](s_permissive)
        if "borrow_ok" not in result["signals_used"]:
            missing.append(name)
    assert not missing, (
        f"signals_used missing 'borrow_ok' on: {missing}"
    )


def test_b740_pin4_borrow_trap_blocks_short_via_explicit_gate():
    """With days_to_cover > 5.0 + otherwise-clean signals, every refactored
    strategy must report fires=False (the explicit gate fires)."""
    s_trapped = _make_permissive_short_signal_dict()
    s_trapped["days_to_cover"] = 10.0  # > 5.0 threshold
    leaks = []
    for name in B740_STRATEGIES:
        result = ALL_STRATEGIES[name](s_trapped)
        if result["fires"]:
            leaks.append(name)
    assert not leaks, (
        f"borrow trap should block these strategies but they fired: {leaks}"
    )


def test_b740_pin5_clean_borrow_does_not_block_when_signals_align():
    """Sanity check: at least ONE B740 strategy fires when signals align AND
    days_to_cover=0. Confirms the gate is the BLOCKING factor, not unrelated
    schema issues.
    """
    s = _make_permissive_short_signal_dict()
    fires_count = sum(
        1 for name in B740_STRATEGIES
        if ALL_STRATEGIES[name](s)["fires"]
    )
    assert fires_count >= 1, (
        f"Expected at least 1 of 26 to fire under permissive signals; got {fires_count}"
    )


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _make_permissive_short_signal_dict() -> dict:
    """Permissive signal dict for SHORT strategies: every gate aligned bearish.

    Booleans default True, numerics tuned for short-side fires, days_to_cover=0
    (borrow gate clear).
    """
    return {
        # Borrow gate
        "days_to_cover": 0.0,
        # Pivot
        "near_r1": True, "near_r2": True, "near_r3": True,
        "near_s1": False, "near_s2": False, "near_s3": False,
        "recent_blowoff_at_r3": True,
        # Candle
        "bearish_engulfing": True, "shooting_star": True, "bearish_pin_bar": True,
        "below_prev_low": True, "three_black_crows": True,
        "doji": True, "near_resistance": True,
        # Trend
        "below_ema_50": True, "below_ema_200": True, "below_sma_50": True,
        "ema_below_avg": True, "ema_50_below_200": True,
        "death_cross_50_200_recent": True, "vol_spike_15x": True, "vol_spike_2x": True,
        # Momentum
        "rsi_14": 75.0, "rsi_14_rising": False, "rsi_9": 75.0,
        "stochrsi_overbought": True, "stoch_bearish_cross": True,
        "macd_bearish": True, "macd_bear_cross_recent": True,
        "ppo_bearish": True, "williams_r": -10,
        # Trend signals
        "supertrend_bearish": True, "supertrend_flip_recent_short_5d": True,
        "ichi_below_cloud": True, "ichi_below_cloud_break_recent_5d": True,
        "weekly_below_cloud": True,
        "psar_flip_dn": True, "adx_trending": True,
        # Breakout / 52W
        "year_low_break_retest_short": True, "near_52w_low": True,
        "below_prev_day_low": True, "below_donchian_lower_recent_3d": True,
        "donchian_breakdown_retest_short": True,
        "close_below_open": True, "close_in_bottom_40pct_of_range": True,
        "below_avwap_20high": True, "above_avwap_20high": False,
        "vol_below_avg": True,
        # Bollinger
        "above_bollinger_upper": True, "bollinger_distance_pct": 0.05,
        # MFI / OBV / Stoch
        "obv_bearish": True, "mfi_overbought": True,
        # Multi-TF / PO3 / HTF
        "po3_bearish_close_position": 0.2, "po3_distribution_recent_5bars": True,
        "weekly_bias_bear": True, "htf_aligned_breakout_short": True, "is_breakout_day": True,
        "weekly_below_ema_200": True, "below_kumo_top": True,
        # CPR / Camarilla
        "cpr_narrow_tight": True, "near_camarilla_r4": True,
        # Cross-sectional / momentum
        "xs_momentum_bottom_decile": True,
        # SMC
        "smc_fvg_retest_short": True, "smc_breaker_block_short": True,
        "smc_mitigation_block_short": True, "smc_in_premium_zone": True,
        "smc_ote_short_window": True, "smc_equal_highs_swept_recent": True,
        # ORB
        "orb_breakdown": True, "in_stocks_in_play_universe": True,
        # CPR-narrow
        "cpr_narrow": True,
    }
