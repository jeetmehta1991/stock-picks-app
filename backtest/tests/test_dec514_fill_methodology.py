"""DEC-514 backtest fill methodology — regression tests (Pass 53 Day-9 v8e).

Spec source: TRADING_RULES_AND_INFORMATION.md §11.

Tests the canonical helper `compute_fill_price()` plus end-to-end behavior
in each refactored exit strategy. Pre-DEC-514, every gap-through-stop bar
silently filled at `stop_price` instead of `bar_open` (real broker fill).
Post-DEC-514, gap-through events are correctly modeled.

Six rules — symmetric across long/short:
  Long stop:    low > stop                → None
                low ≤ stop ≤ open         → fill at stop
                open < stop (gap-through) → fill at open       (adverse)
  Long target:  high < target             → None
                high ≥ target ≥ open      → fill at target
                open > target (gap-up)    → fill at open       (favourable)
  Short stop:   high < stop               → None
                high ≥ stop ≥ open        → fill at stop
                open > stop (gap-up)      → fill at open       (adverse)
  Short target: low > target              → None
                low ≤ target ≤ open       → fill at target
                open < target (gap-down)  → fill at open       (favourable)
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from backtest.engine.exit_manager import compute_fill_price


# ---------------------------------------------------------------------------
# 12 canonical helper tests (3 cases × 4 (direction × level_type) combos)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("scenario,direction,level_type,level,bar_open,bar_high,bar_low,expected", [
    # Long stop @ 95
    ("long_stop_no_hit",        "long",  "stop",   95.0, 100, 101,  96, None),
    ("long_stop_intraday",      "long",  "stop",   95.0, 100, 101,  94, 95.0),
    ("long_stop_gap_through",   "long",  "stop",   95.0,  90,  91,  89, 90),    # FILL AT OPEN
    # Long target @ 105
    ("long_tgt_no_hit",         "long",  "target", 105.0, 100, 104,  99, None),
    ("long_tgt_intraday",       "long",  "target", 105.0, 100, 106,  99, 105.0),
    ("long_tgt_gap_up",         "long",  "target", 105.0, 110, 112, 109, 110),  # FILL AT OPEN (favourable)
    # Short stop @ 105
    ("short_stop_no_hit",       "short", "stop",   105.0, 100, 104,  99, None),
    ("short_stop_intraday",     "short", "stop",   105.0, 100, 106,  99, 105.0),
    ("short_stop_gap_through",  "short", "stop",   105.0, 110, 112, 109, 110),  # FILL AT OPEN
    # Short target @ 95
    ("short_tgt_no_hit",        "short", "target",  95.0, 100, 101,  96, None),
    ("short_tgt_intraday",      "short", "target",  95.0, 100, 101,  94, 95.0),
    ("short_tgt_gap_down",      "short", "target",  95.0,  90,  91,  89, 90),   # FILL AT OPEN (favourable)
])
def test_dec514_compute_fill_price_six_rules(
    scenario, direction, level_type, level, bar_open, bar_high, bar_low, expected
):
    actual = compute_fill_price(
        direction=direction, level_type=level_type, level=level,
        bar_open=bar_open, bar_high=bar_high, bar_low=bar_low,
    )
    assert actual == expected, (
        f"DEC-514 {scenario}: compute_fill_price returned {actual}, expected {expected}"
    )


# ---------------------------------------------------------------------------
# Edge-case: stop = open exactly (boundary)
# ---------------------------------------------------------------------------
def test_dec514_long_stop_equals_open_fills_at_stop():
    """Boundary: open == stop. Per spec: low ≤ stop ≤ open → fill at stop."""
    fill = compute_fill_price("long", "stop", 100.0, bar_open=100.0,
                                bar_high=100.5, bar_low=99.0)
    assert fill == 100.0


def test_dec514_long_target_equals_open_fills_at_target():
    fill = compute_fill_price("long", "target", 100.0, bar_open=100.0,
                                bar_high=101.0, bar_low=99.5)
    assert fill == 100.0


# ---------------------------------------------------------------------------
# Bad-input guards
# ---------------------------------------------------------------------------
def test_dec514_invalid_direction_raises():
    with pytest.raises(ValueError):
        compute_fill_price("flat", "stop", 100.0, 100, 101, 99)


def test_dec514_invalid_level_type_raises():
    with pytest.raises(ValueError):
        compute_fill_price("long", "trailing", 100.0, 100, 101, 99)


# ---------------------------------------------------------------------------
# End-to-end: each refactored exit_strategies.py function uses helper
# ---------------------------------------------------------------------------
def _gap_down_df(entry_price=100.0, gap_open=85.0, recover_close=86.0,
                 gap_low=84.0, n_pre_days=5, gap_day_idx=2):
    """Build a synthetic OHLCV DataFrame where bar `gap_day_idx` opens via
    overnight gap-down past a stop at ~95.
    """
    idx = pd.date_range("2023-01-02", periods=n_pre_days, freq="B")
    rows = []
    for i in range(n_pre_days):
        if i == gap_day_idx:
            rows.append({
                "open":  gap_open,
                "high":  gap_open + 0.5,
                "low":   gap_low,
                "close": recover_close,
                "volume": 1_000_000,
            })
        else:
            rows.append({
                "open":  entry_price,
                "high":  entry_price + 1.0,
                "low":   entry_price - 0.5,
                "close": entry_price + 0.2,
                "volume": 1_000_000,
            })
    return pd.DataFrame(rows, index=idx)


def test_dec514_e2e_atr_trail_gap_through_stop_fills_at_open():
    """Synthetic: long entry @ 100, ATR=2 → stop at ~98. Day 3 gaps to open=85.
    Pre-DEC-514: would fill at stop (~98). Post-DEC-514: must fill at 85."""
    from backtest.engine.exit_strategies import exit_atr_trail

    df = _gap_down_df(entry_price=100.0, gap_open=85.0, gap_low=84.0,
                      gap_day_idx=2)
    result = exit_atr_trail(df, date(2023, 1, 2), 100.0, "long",
                             atr=2.0, atr_mult=1.0)

    # Exit must be at the GAP open price, not at the stop
    assert result["exit_reason"] == "atr_trailing_stop"
    # Stop was ~98 (entry 100 - 1 ATR × 2). Open was 85. Fill must be 85.
    assert result["exit_price"] < 95.0, (
        f"DEC-514 regression: gap-through-stop filled at "
        f"{result['exit_price']} — should be near open=85 not stop=98"
    )
    assert result["exit_price"] == pytest.approx(85.0, abs=0.5)


def test_dec514_e2e_trailing_pct_gap_through_stop_fills_at_open():
    """exit_trailing_pct should also use the helper."""
    from backtest.engine.exit_strategies import exit_trailing_pct

    df = _gap_down_df(entry_price=100.0, gap_open=85.0, gap_low=84.0,
                      gap_day_idx=2)
    result = exit_trailing_pct(df, date(2023, 1, 2), 100.0, "long",
                                atr=2.0, trail_pct=0.10)

    # 10% trail stop = 90. Open = 85. Must fill at open.
    assert result["exit_reason"] == "trailing_stop"
    assert result["exit_price"] < 89.0, (
        f"DEC-514 regression: gap-through-stop in trailing_pct filled at "
        f"{result['exit_price']} — should be near open=85 not stop=90"
    )


def test_dec514_e2e_check_trailing_stop_hit_gap_through():
    """check_trailing_stop_hit when given today_open must use the helper."""
    from backtest.engine.exit_manager import check_trailing_stop_hit, OpenTrade

    t = OpenTrade(
        ticker="TEST", entry_date=date(2023, 1, 1), entry_price=100.0,
        direction="long", strategy="t", category="c", sector="Technology",
        initial_stop=95.0, trailing_stop=95.0, highest_close=100.0,
        regime_at_entry="bull",
    )
    # Bar gaps down: open=88 < trailing_stop=95
    fill = check_trailing_stop_hit(t, today_low=85.0, today_high=89.0,
                                    today_close=87.0, today_open=88.0)
    assert fill == 88.0, f"Expected fill at open=88; got {fill}"


def test_dec514_e2e_check_trailing_stop_hit_intraday_normal():
    """When open above stop and intraday low touches stop: fill at stop."""
    from backtest.engine.exit_manager import check_trailing_stop_hit, OpenTrade

    t = OpenTrade(
        ticker="TEST", entry_date=date(2023, 1, 1), entry_price=100.0,
        direction="long", strategy="t", category="c", sector="Technology",
        initial_stop=95.0, trailing_stop=95.0, highest_close=100.0,
        regime_at_entry="bull",
    )
    fill = check_trailing_stop_hit(t, today_low=94.0, today_high=99.0,
                                    today_close=96.0, today_open=98.0)
    assert fill == 95.0, f"Expected fill at stop=95; got {fill}"


def test_dec514_backwards_compat_legacy_callers():
    """Legacy callers of check_trailing_stop_hit (no today_open) preserve
    pre-DEC-514 behavior (fill at stop) — backwards-compat path."""
    from backtest.engine.exit_manager import check_trailing_stop_hit, OpenTrade

    t = OpenTrade(
        ticker="TEST", entry_date=date(2023, 1, 1), entry_price=100.0,
        direction="long", strategy="t", category="c", sector="Technology",
        initial_stop=95.0, trailing_stop=95.0, highest_close=100.0,
        regime_at_entry="bull",
    )
    fill = check_trailing_stop_hit(t, today_low=85.0, today_high=89.0,
                                    today_close=87.0)  # no today_open
    assert fill == 95.0  # legacy path returns stop


# ---------------------------------------------------------------------------
# Spec-completeness: verify all refactored exit_strategies are covered
# ---------------------------------------------------------------------------
def test_dec514_exit_strategies_import_helper():
    """exit_strategies.py must import compute_fill_price."""
    import backtest.engine.exit_strategies as es_mod
    assert hasattr(es_mod, "compute_fill_price"), (
        "exit_strategies.py does not import compute_fill_price — DEC-514 wiring incomplete"
    )
