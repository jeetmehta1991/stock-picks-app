"""Pin tests for scripts/mean_reversion_edge_prior_test.py per Batch 758 +
B755-COUNCIL TIER 1.3 ticket.

# Source: scripts/mean_reversion_edge_prior_test.py (B758 build)
# per CHECKLIST #77 + #106 (council TIER 1.3 ticket)

Locks in the edge-prior test contract: trigger definitions, forward-return
math, verdict thresholds, and aggregate verdict logic.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.mean_reversion_edge_prior_test import (
    HORIZONS,
    TRIGGERS,
    _assign_aggregate_verdict,
    _assign_trigger_verdict,
    _compute_forward_returns,
)


# ---------------------------------------------------------------------------
# Pin 1: HORIZONS contains 5/10/20 day standard horizons (canonical
# mean-reversion holding periods per Connors 2009)
# ---------------------------------------------------------------------------
def test_pin1_horizons_canonical():
    assert HORIZONS == [5, 10, 20]


# ---------------------------------------------------------------------------
# Pin 2: At least 12 triggers covering each Cluster A oscillator family
# (RSI 2x, Stoch 2x, MFI 2x, BB 2x, Williams 2x, UO 2x = 12)
# ---------------------------------------------------------------------------
def test_pin2_triggers_cover_all_oscillator_families():
    names = {n for n, _, _ in TRIGGERS}
    assert len(names) == len(TRIGGERS), "Trigger names must be unique"
    # Each family at least one LONG + one SHORT
    families = {
        "rsi": ["rsi_14_lt_30_long", "rsi_14_gt_70_short"],
        "stoch": ["stoch_k_lt_20_long", "stoch_k_gt_80_short"],
        "mfi": ["mfi_lt_20_long", "mfi_gt_80_short"],
        "bb": ["bb_lower_touch_long", "bb_upper_touch_short"],
        "williams": ["williams_r_lt_neg80_long", "williams_r_gt_neg20_short"],
        "uo": ["ultimate_osc_lt_30_long", "ultimate_osc_gt_70_short"],
    }
    for fam, expected in families.items():
        for e in expected:
            assert e in names, f"Family {fam} missing trigger {e}"


# ---------------------------------------------------------------------------
# Pin 3: Trigger predicates are callable + return bool
# ---------------------------------------------------------------------------
def test_pin3_trigger_predicates_callable():
    for name, direction, predicate in TRIGGERS:
        assert callable(predicate), f"{name} predicate not callable"
        # Predicate should handle empty dict gracefully
        result = predicate({})
        # Result should be bool-like
        assert result is True or result is False or result in (0, 1)


# ---------------------------------------------------------------------------
# Pin 4: Direction values are valid (long or short only)
# ---------------------------------------------------------------------------
def test_pin4_direction_values_valid():
    for name, direction, _ in TRIGGERS:
        assert direction in ("long", "short"), f"{name} has invalid direction {direction}"


# ---------------------------------------------------------------------------
# Pin 5: _compute_forward_returns math on a synthetic uptrend (LONG)
# 10-bar series with 1% daily uptrend. Entry at bar 0 -> next-day open
# at bar 1, exit at bar 1+5=6 close. Should be ~5% positive.
# ---------------------------------------------------------------------------
def test_pin5_forward_returns_long_uptrend():
    # Build 30-bar synthetic OHLC with 1% daily up
    prices = [100.0 * (1.01 ** i) for i in range(30)]
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.005 for p in prices],
        "low": [p * 0.995 for p in prices],
        "close": prices,
        "volume": [1e6] * 30,
    }, index=pd.date_range("2024-01-01", periods=30))
    out = _compute_forward_returns(df, entry_idx=0, direction="long")
    # 5-day: enter at bar 1 (price 100*1.01=101.01), exit at bar 6 (100*1.01^6=106.15)
    # ret = (106.15 - 101.01) / 101.01 = 0.05091 -> ~509 bps (compound, not simple)
    assert 5 in out
    assert 450 < out[5] < 550, f"Expected ~509bps (compound 1%/day x 5d), got {out[5]}"
    assert 10 in out
    # 10-day cumulative ~ 1.01^11 / 1.01^1 = 1.01^10 = 1.1046; ~1046bps
    assert out[10] > out[5], "10-day return should exceed 5-day in uptrend"


# ---------------------------------------------------------------------------
# Pin 6: _compute_forward_returns SHORT direction inverts sign
# ---------------------------------------------------------------------------
def test_pin6_forward_returns_short_inverts_sign():
    prices = [100.0 * (1.01 ** i) for i in range(30)]
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.005 for p in prices],
        "low": [p * 0.995 for p in prices],
        "close": prices,
        "volume": [1e6] * 30,
    }, index=pd.date_range("2024-01-01", periods=30))
    long_out = _compute_forward_returns(df, entry_idx=0, direction="long")
    short_out = _compute_forward_returns(df, entry_idx=0, direction="short")
    # SHORT in uptrend should be negative; magnitude equal to LONG
    for H in [5, 10, 20]:
        if H in long_out and H in short_out:
            assert abs(long_out[H] + short_out[H]) < 1e-6, (
                f"LONG and SHORT returns should mirror; H={H}, "
                f"long={long_out[H]}, short={short_out[H]}"
            )


# ---------------------------------------------------------------------------
# Pin 7: _assign_trigger_verdict EDGE_EXISTS threshold
# ---------------------------------------------------------------------------
def test_pin7_trigger_verdict_edge_exists():
    stats = {
        "n_signals": 100,
        "hit_rate_10d": 0.55,
        "mean_pnl_10d_bps": 15.0,
        "sharpe_10d": 0.08,
    }
    assert _assign_trigger_verdict(stats) == "EDGE_EXISTS"


# ---------------------------------------------------------------------------
# Pin 8: _assign_trigger_verdict INSUFFICIENT_DATA when n_signals < 30
# ---------------------------------------------------------------------------
def test_pin8_trigger_verdict_insufficient_data():
    stats = {
        "n_signals": 25,
        "hit_rate_10d": 0.99,
        "mean_pnl_10d_bps": 100.0,
        "sharpe_10d": 0.5,
    }
    assert _assign_trigger_verdict(stats) == "INSUFFICIENT_DATA"


# ---------------------------------------------------------------------------
# Pin 9: _assign_trigger_verdict EDGE_NULL when stats are at coin-flip
# (this is the most important verdict per peer-reviewer concern)
# ---------------------------------------------------------------------------
def test_pin9_trigger_verdict_edge_null_at_coin_flip():
    stats = {
        "n_signals": 1000,
        "hit_rate_10d": 0.50,
        "mean_pnl_10d_bps": 1.0,
        "sharpe_10d": 0.001,
    }
    assert _assign_trigger_verdict(stats) == "EDGE_NULL"


# ---------------------------------------------------------------------------
# Pin 10: _assign_trigger_verdict EDGE_NEGATIVE when worse than coin-flip
# ---------------------------------------------------------------------------
def test_pin10_trigger_verdict_edge_negative():
    stats = {
        "n_signals": 500,
        "hit_rate_10d": 0.45,
        "mean_pnl_10d_bps": -10.0,
        "sharpe_10d": -0.05,
    }
    assert _assign_trigger_verdict(stats) == "EDGE_NEGATIVE"


# ---------------------------------------------------------------------------
# Pin 11: _assign_aggregate_verdict CONFIRMED when 3+ EDGE_EXISTS
# ---------------------------------------------------------------------------
def test_pin11_aggregate_verdict_confirmed():
    triggers = [
        {"verdict": "EDGE_EXISTS"}, {"verdict": "EDGE_EXISTS"},
        {"verdict": "EDGE_EXISTS"}, {"verdict": "EDGE_NULL"},
        {"verdict": "INSUFFICIENT_DATA"},
    ]
    assert _assign_aggregate_verdict(triggers) == "MEAN_REVERSION_EDGE_CONFIRMED"


# ---------------------------------------------------------------------------
# Pin 12: _assign_aggregate_verdict NULL when all EDGE_NULL
# (the council peer-reviewer hypothesis)
# ---------------------------------------------------------------------------
def test_pin12_aggregate_verdict_null_when_all_null():
    triggers = [
        {"verdict": "EDGE_NULL"} for _ in range(12)
    ]
    assert _assign_aggregate_verdict(triggers) == "MEAN_REVERSION_EDGE_NULL"


# ---------------------------------------------------------------------------
# Pin 13: _assign_aggregate_verdict INSUFFICIENT_DATA if all triggers insufficient
# ---------------------------------------------------------------------------
def test_pin13_aggregate_verdict_insufficient_data():
    triggers = [
        {"verdict": "INSUFFICIENT_DATA"} for _ in range(12)
    ]
    assert _assign_aggregate_verdict(triggers) == "INSUFFICIENT_DATA"


# ---------------------------------------------------------------------------
# Pin 14: Specific trigger predicate semantics. rsi_14<30 should be True
# when rsi_14=25, False when rsi_14=50.
# ---------------------------------------------------------------------------
def test_pin14_rsi_14_lt_30_predicate_semantics():
    # Find the trigger
    trig = [(n, d, p) for n, d, p in TRIGGERS if n == "rsi_14_lt_30_long"][0]
    _, _, predicate = trig
    assert predicate({"rsi_14": 25.0}) is True
    assert predicate({"rsi_14": 50.0}) is False
    assert predicate({"rsi_14": 29.99}) is True
    # Default value: when key absent, default=50 -> False
    assert predicate({}) is False


# ---------------------------------------------------------------------------
# Pin 15: bb_lower_touch predicate
# ---------------------------------------------------------------------------
def test_pin15_bb_lower_touch_predicate():
    trig = [(n, d, p) for n, d, p in TRIGGERS if n == "bb_lower_touch_long"][0]
    _, _, predicate = trig
    assert predicate({"bb_20_20_touch_lower": True}) is True
    assert predicate({"bb_20_20_touch_lower": False}) is False
    assert predicate({}) is False
