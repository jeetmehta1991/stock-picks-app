# Source: Decision 5 Cat 1 critical path + B713 Phase 0 + owner-approved Option A "option a" 2026-06-13 per CHECKLIST #77
"""B743 pin tests: dual `_strat3` second chunk -- remaining 30 of 61 dual
strategies converted to explicit `borrow_ok` borrow gate on the SHORT branch.

Combined with B740 + B741 + B742, ALL 112 short-emitting strategies (51 pure-short
+ 61 dual _strat3) now declare borrow_ok at call site + carry explicit
`_short_borrow_trap_active(s)` gate. B736 registration-time borrow-gate lint
is now fully unblocked.

Includes a cluster-wide invariant: scan screener.py and assert every function
body whose return path contains `_strat3` AND mentions `direction="short"`
output path also contains `_short_borrow_trap_active(s)`.
"""
from __future__ import annotations

from backtest.signals.screener import ALL_STRATEGIES

B743_STRATEGIES = [
    "bollinger_lower",
    "bollinger_tight",
    "keltner_lower",
    "stoch_oversold",
    "volume_spike_breakout",
    "force_index_breakout",
    "donchian_10_breakout",
    "morning_star",
    "bullish_engulfing_support",
    "rsi_volume_200ema",
    "macd_ichimoku",
    "bb_squeeze_volume",
    "pivot_fib_confluence",
    "golden_cross_volume",
    "cpr_narrow_momentum",
    "camarilla_rsi_obv",
    "supertrend_ichimoku_adx",
    "williams_stoch_dual",
    "dc20_break_retest",
    "r1_break_retest",
    "break_retest_volume",
    "break_retest_confluence",
    "smc_inverse_fvg",
    "smc_bos_retest_entry",
    "smc_bos_continuation",
    "smc_choch_reversal",
    "smc_order_block_bounce",
    "smc_liquidity_sweep_reversal",
    "avwap_252_breakout",
    "avwap_50_reclaim",
]


def test_b743_pin1_count_matches_30():
    assert len(B743_STRATEGIES) == 30


def test_b743_pin2_all_30_registered():
    missing = [s for s in B743_STRATEGIES if s not in ALL_STRATEGIES]
    assert not missing, f"missing: {missing}"


def test_b743_pin3_combined_strat3_count_is_61():
    """B742 (31) + B743 (30) = 61 total dual `_strat3` strategies.

    Cluster-wide regression guard: if a new dual strategy is added later,
    this test fails and the author is forced to add it to either cohort
    AND give it explicit gate per the S4-B713 discipline.
    """
    import re
    src = open("backtest/signals/screener.py", encoding="utf-8").read()
    strat3_count = len(re.findall(r'return _strat3\(', src))
    expected = 61
    assert strat3_count == expected, (
        f"expected {expected} dual _strat3 strategies; got {strat3_count}. "
        f"If a new dual strategy was added, it must be added to either B742 or B743 cohort "
        f"+ given explicit borrow_ok gate on its SHORT branch per S4-B713-INSPECT-CURRENTFRAME-REVERT."
    )


def test_b743_pin4_every_strat3_function_carries_explicit_short_gate():
    """Cluster-wide regression: every function body ending with `return _strat3(...)`
    must contain `_short_borrow_trap_active(s)` (the explicit short-branch gate).

    B718d removal of inspect.currentframe from _strat3 helper relies on this
    invariant holding for all dual strategies.
    """
    import re
    src = open("backtest/signals/screener.py", encoding="utf-8").read()
    lines = src.splitlines()
    missing_gate = []
    in_function = None
    function_start = None
    for i, line in enumerate(lines):
        m = re.match(r"^def (strat_\w+)\(s\):\s*$", line)
        if m:
            in_function = m.group(1)
            function_start = i
            continue
        if in_function is None:
            continue
        if "return _strat3(" in line:
            body = "\n".join(lines[function_start:i + 1])
            if "_short_borrow_trap_active(s)" not in body:
                missing_gate.append(in_function)
            in_function = None
            function_start = None
            continue
    assert not missing_gate, (
        f"dual _strat3 strategies missing explicit SHORT gate: {missing_gate}"
    )


def test_b743_pin5_short_branch_declares_borrow_ok_when_fires():
    s = _permissive_bearish_dict()
    found = []
    for name in B743_STRATEGIES:
        r = ALL_STRATEGIES[name](s)
        if r["fires"] and r["direction"] == "short":
            assert "borrow_ok" in r["signals_used"], (
                f"{name} fired SHORT but signals_used missing borrow_ok: {r['signals_used']}"
            )
            found.append(name)
    assert found, "expected >=1 SHORT fire under permissive bearish signals"


def test_b743_pin6_borrow_trap_blocks_short_branch():
    s = _permissive_bearish_dict()
    s["days_to_cover"] = 10.0
    leaks = [n for n in B743_STRATEGIES if ALL_STRATEGIES[n](s)["fires"] and ALL_STRATEGIES[n](s)["direction"] == "short"]
    assert not leaks, f"borrow trap should block SHORT but these fired: {leaks}"


def test_b743_pin7_long_branch_unaffected_by_borrow_trap():
    """LONG branch fires under high DTC -- gate is SHORT-only."""
    s = _permissive_bullish_dict()
    s["days_to_cover"] = 10.0
    longs = [
        n for n in B743_STRATEGIES
        if ALL_STRATEGIES[n](s)["fires"] and ALL_STRATEGIES[n](s)["direction"] == "long"
    ]
    assert longs, "expected >=1 LONG fire despite DTC=10 (gate is SHORT-only)"


# --------------------------------------------------------------------------
def _permissive_bearish_dict() -> dict:
    return {
        "days_to_cover": 0.0,
        # Bollinger SHORT
        "below_bollinger_lower": False, "above_bollinger_upper": True,
        "bollinger_distance_pct": 0.05, "bb_width_pct": 0.05, "bb_squeeze_active": True,
        # Keltner
        "above_keltner_upper": True, "below_keltner_lower": False,
        # Stoch
        "stoch_overbought": True, "stoch_bearish_cross": True,
        # Volume
        "vol_spike_15x": True, "vol_spike_2x": True, "vol_below_avg": True,
        "below_volume_breakout_high": True, "above_volume_breakout_high": False,
        "force_index_bearish": True, "below_donchian_lower_recent_3d": True,
        # Candle bearish
        "evening_star": True, "bearish_engulfing_support": False,
        "bearish_engulfing": True,
        # MACD / Ichimoku
        "macd_bearish": True, "macd_bear_cross_recent": True,
        "ichi_below_cloud": True, "ichi_below_cloud_break_recent_5d": True,
        "weekly_below_cloud": True, "below_kumo_top": True,
        # BB squeeze
        "bb_squeeze_release_down": True,
        # Pivot fib
        "near_pivot_resistance_fib": True,
        # Golden cross volume (SHORT = death cross + volume)
        "death_cross_volume_short": True,
        # CPR
        "cpr_narrow_tight": True, "cpr_narrow": True,
        # Camarilla
        "near_camarilla_r4": True,
        # Supertrend confluence
        "supertrend_bearish": True, "ichi_below_cloud_break_recent_5d": True,
        "adx_trending": True,
        # Williams stoch
        "williams_r": -10, "stoch_overbought": True,
        # Break retest
        "resistance_break_retest": True, "dc20_break_retest_short": True,
        "r1_break_retest_short": True, "below_avwap_252low": True,
        "above_avwap_50": False,
        # Trend
        "below_ema_50": True, "below_ema_200": True, "below_sma_50": True,
        "below_ema_200_break_recent_5d": True,
        # 200 EMA gate
        "price_above_ema_200": False,
        # Momentum
        "rsi_14": 75.0, "rsi_21": 75.0, "rsi_9": 75.0,
        # SMC SHORT
        "smc_inverse_fvg_short": True, "smc_bos_short_recent": True,
        "smc_bos_short_retest_active": True, "smc_choch_short_recent": True,
        "smc_order_block_short_bounce": True, "smc_liquidity_sweep_short_reversal": True,
        # AVWAP
        "below_avwap_252low": True, "above_avwap_50": False,
        "avwap_50_rejection_short": True,
    }


def _permissive_bullish_dict() -> dict:
    return {
        "days_to_cover": 0.0,
        # Bollinger LONG
        "below_bollinger_lower": True, "above_bollinger_upper": False,
        "bb_squeeze_active": True, "bb_squeeze_release_up": True,
        # Keltner
        "below_keltner_lower": True,
        # Stoch
        "stoch_oversold": True, "stoch_bullish_cross": True,
        # Volume
        "vol_spike_15x": True, "vol_spike_2x": True,
        "above_volume_breakout_high": True, "force_index_bullish": True,
        "above_donchian_upper_recent_3d": True,
        # Candle bullish
        "morning_star": True, "bullish_engulfing": True,
        "bullish_engulfing_support": True,
        # MACD / Ichimoku
        "macd_bullish": True, "macd_bull_cross_recent": True,
        "ichi_above_cloud": True, "ichi_above_cloud_break_recent_5d": True,
        "weekly_above_cloud": True, "above_kumo_bottom": True,
        # Pivot fib
        "near_pivot_support_fib": True,
        # Golden cross volume
        "golden_cross_50_200_recent": True, "vol_spike_15x": True,
        # CPR
        "cpr_narrow_tight": True, "cpr_narrow": True,
        # Camarilla
        "near_camarilla_s3": True,
        # Supertrend confluence
        "supertrend_bullish": True, "ichi_above_cloud_break_recent_5d": True,
        "adx_trending": True,
        # Williams stoch
        "williams_r": -90, "stoch_oversold": True,
        # Break retest
        "support_break_retest": True, "dc20_break_retest_long": True,
        "r1_break_retest_long": True, "above_avwap_252high": True,
        # Trend bullish
        "price_above_ema_50": True, "price_above_ema_200": True, "above_sma_50": True,
        "price_above_ema_200_break_recent_5d": True,
        # Momentum
        "rsi_14": 25.0, "rsi_21": 25.0, "rsi_9": 25.0,
        # SMC LONG
        "smc_inverse_fvg_long": True, "smc_bos_long_recent": True,
        "smc_bos_long_retest_active": True, "smc_choch_long_recent": True,
        "smc_order_block_long_bounce": True, "smc_liquidity_sweep_long_reversal": True,
        # AVWAP
        "above_avwap_252high": True, "above_avwap_50": True,
        "avwap_50_reclaim_long": True,
    }
