# Source: Decision 5 Cat 1 critical path + B713 Phase 0 + owner-approved "Run B740 + B741" 2026-06-13 per CHECKLIST #77
"""B741 pin tests: B718b second chunk -- remaining 25 of 51 pure-short
strategies converted to explicit `borrow_ok` borrow gate at call site.

Combined with B740, all 51 pure-short strategies now declare borrow_ok at
call site. Next: B742-B743 = 63 dual `_strat3` strategies (separate batches
since they require a different refactor pattern -- shared _strat3 helper edit
+ short-branch-only gate insertion).
"""
from __future__ import annotations

from backtest.signals.screener import ALL_STRATEGIES

# Strategies refactored in B741 (B718b second chunk)
B741_STRATEGIES = [
    "smc_breaker_block_short",
    "smc_mitigation_block_short",
    "smc_premium_short",
    "smc_ote_short",
    "smc_equal_highs_sweep_short",
    "turtle_soup_short",
    "judas_swing_short",
    "mmsm_short",
    "week_opening_gap_fill_down",
    "pead_short",
    "pead_short_negative_yoy_growth",
    "avwap_20high_rejection_short",
    "head_and_shoulders_top_short",
    "inverted_cup_and_handle_short",
    "triangle_descending_short",
    "flag_bear_retest_short",
    "simple_below_ema_50_short",
    "classification_change_to_defensive_short",
    "classification_change_from_tech_short",
    "vol_spike_2x_below_ema_50_short",
    "risk_off_bond_equity_short",
    "dxy_headwind_multinational_short",
    "pairs_mean_reversion_short",
    "news_momentum_short",
    "news_reversal_short",
]


def test_b741_pin1_count_matches_25():
    """B741 second chunk -- exactly 25 strategies refactored this batch."""
    assert len(B741_STRATEGIES) == 25


def test_b741_pin2_all_25_registered():
    """Every B741 strategy must remain in ALL_STRATEGIES."""
    missing = [s for s in B741_STRATEGIES if s not in ALL_STRATEGIES]
    assert not missing, f"missing from ALL_STRATEGIES: {missing}"


def test_b741_pin3_every_strategy_declares_borrow_ok_in_signals_used():
    """Each B741 strategy's signals_used must include `borrow_ok`."""
    s_permissive = _make_permissive_short_signal_dict()
    missing = []
    for name in B741_STRATEGIES:
        result = ALL_STRATEGIES[name](s_permissive)
        if "borrow_ok" not in result["signals_used"]:
            missing.append(name)
    assert not missing, (
        f"signals_used missing 'borrow_ok' on: {missing}"
    )


def test_b741_pin4_borrow_trap_blocks_short_via_explicit_gate():
    """days_to_cover=10.0 (>5.0 threshold) blocks every B741 strategy."""
    s_trapped = _make_permissive_short_signal_dict()
    s_trapped["days_to_cover"] = 10.0
    leaks = []
    for name in B741_STRATEGIES:
        result = ALL_STRATEGIES[name](s_trapped)
        if result["fires"]:
            leaks.append(name)
    assert not leaks, (
        f"borrow trap should block these strategies but they fired: {leaks}"
    )


def test_b741_pin5_combined_b740_b741_covers_all_50_pure_short_strategies():
    """B740 (25 post-B874 deletion of camarilla_rsi_obv_short) + B741 (25) = 50.
    Was 51 at B741 time; B874 deleted 1 pure-short reducing total to 50.

    Regression guard: if a new pure-short strategy is added later, this test
    fails and the author is forced to add it to the explicit-gate cohort.
    """
    import re
    src = open("backtest/signals/screener.py", encoding="utf-8").read()
    # count `_strat(<var>, "short"` occurrences
    pure_short_count = len(re.findall(r'_strat\([A-Za-z_]\w*,\s*"short"', src))
    expected = 50  # B899 migration: 51 -> 50 post-B874 camarilla_rsi_obv_short deletion
    assert pure_short_count == expected, (
        f"expected {expected} pure-short strategies in screener.py; got {pure_short_count}. "
        f"If a new pure-short was added, it must be added to either B740 or B741 cohort + given "
        f"explicit borrow_ok gate per S4-B713-INSPECT-CURRENTFRAME-REVERT discipline."
    )


def test_b741_pin6_every_pure_short_has_explicit_gate_at_call_site():
    """Cluster-wide regression: scan screener.py source and assert every
    pure-short strategy body contains `_short_borrow_trap_active(s)` (the
    explicit gate). The B718d removal of inspect.currentframe will rely on
    this property holding for all pure-short strategies.
    """
    import re
    src = open("backtest/signals/screener.py", encoding="utf-8").read()
    lines = src.splitlines()
    # find function bodies that end with `return _strat(..., "short", ...)`
    short_strategies_missing_gate = []
    in_function = None
    function_start = None
    for i, line in enumerate(lines):
        m = re.match(r"^def (strat_\w+)\(s\):\s*$", line)
        if m:
            # entering a new function -- close out previous
            in_function = m.group(1)
            function_start = i
            continue
        if in_function is None:
            continue
        if re.search(r'return _strat\([^,]+,\s*"short"', line):
            # this is a pure-short return; check the body has the gate
            body = "\n".join(lines[function_start:i + 1])
            if "_short_borrow_trap_active(s)" not in body:
                short_strategies_missing_gate.append(in_function)
            in_function = None
            function_start = None
            continue
        if re.search(r'^def (strat_\w+)\(s\):\s*$', line):
            # next function starts -- close prev without gate (was not short)
            in_function = None
            function_start = None
    assert not short_strategies_missing_gate, (
        f"pure-short strategies missing explicit gate at call site: {short_strategies_missing_gate}"
    )


# --------------------------------------------------------------------------
# Helpers (shared with test_batch740)
# --------------------------------------------------------------------------
def _make_permissive_short_signal_dict() -> dict:
    """Permissive SHORT signal dict; days_to_cover=0 so borrow gate clears."""
    return {
        # Borrow gate
        "days_to_cover": 0.0,
        # Candle
        "bearish_engulfing": True, "shooting_star": True, "bearish_pin_bar": True,
        # Trend / EMA
        "below_ema_50": True, "below_ema_200": True, "below_sma_50": True,
        "below_ema_200_break_recent_5d": True, "below_ema_50_break_recent_5d": True,
        # Volume
        "vol_spike_15x": True, "vol_spike_2x": True, "vol_below_avg": True,
        # Momentum
        "rsi_14": 25.0, "rsi_9": 25.0,
        "macd_bearish": True, "macd_bear_cross_recent": True,
        # SMC
        "smc_fvg_retest_short": True, "smc_breaker_block_short": True,
        "smc_mitigation_block_short": True, "smc_in_premium_zone": True,
        "smc_ote_short_window": True, "smc_equal_highs_swept_recent": True,
        "smc_liquidity_swept_recent_5bar_up": True,
        # ICT
        "turtle_soup_short": True, "judas_swing_short": True,
        "mmsm_short": True, "week_open_gap_up_15pct": True, "is_week_open": True,
        # PEAD
        "within_pead_window": True, "pead_negative_surprise": True,
        "earnings_eps_yoy_growth": -0.15, "earnings_announcement_return": -0.05,
        "days_since_last_earnings": 30,
        # AVWAP
        "above_avwap_20high": True,
        # Chart pattern
        "head_and_shoulders_top_detected": True,
        "inverted_cup_and_handle_detected": True,
        "triangle_descending_detected": True,
        "flag_bear_breakout_retest_short": True,
        "flag_bear_breakdown_level": 100.0,
        # Classification change
        "classification_change_to_defensive": True,
        "classification_change_from_tech": True,
        # Cross-asset
        "risk_off_regime_bond_signal_strong": True,
        "dxy_above_sma_50": True, "foreign_rev_pct": 0.5,
        # Pairs
        "pair_zscore": 2.5,
        # News
        "news_momentum_negative": True, "news_reversal_long": False,
        "news_sentiment_score_7d_extreme_positive": True,
        "news_sentiment_score_1d": -0.5, "news_sentiment_score_7d": 0.5,
        # Other
        "ema_50_below_200": True,
    }
