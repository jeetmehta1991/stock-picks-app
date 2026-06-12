# Source: B710 W6 reviewer anti-fakeout + B698 BR-1 ATR-clearance + S4-B717 ceiling routing per CHECKLIST #77
"""B727 pin tests: strat_monthly_bias_momentum_long ATR-clearance tightening.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* monthly_bias_momentum_long: 10,507/yr LONG = state-flag rate

B727 changes:
* compute_volume (technical.py) adds: above_prev_high_clearance_atr_05 + below_prev_low_clearance_atr_05
* strat_monthly_bias_momentum_long: above_prev_high -> above_prev_high_clearance_atr_05

Pattern: ATR-scaled clearance margin (close > prev_high + 0.5*ATR(14))
separates real break from one-tick poke. B698 BR-1 anti-fakeout reviewer
recommendation applied to monthly_bias_momentum ceiling routing.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.signals.screener import strat_monthly_bias_momentum_long
from backtest.signals.technical import compute_volume


def _build_df(n_bars=60, prev_high=100.0, today_close=101.0, atr=2.0):
    """Synthetic OHLCV with controlled prev_high and today_close."""
    rng = np.random.default_rng(42)
    closes = list(prev_high - 5 + rng.normal(0, atr * 0.5, n_bars - 2))
    highs = [c + 1 for c in closes]
    lows = [c - 1 for c in closes]
    volumes = list(1_000_000 + rng.normal(0, 100_000, n_bars - 2))
    # Yesterday's bar: high = prev_high
    closes.append(prev_high - 0.5)
    highs.append(prev_high)
    lows.append(prev_high - 2)
    volumes.append(1_000_000)
    # Today's bar
    closes.append(today_close)
    highs.append(today_close + 0.5)
    lows.append(today_close - 0.5)
    volumes.append(1_000_000)
    return pd.DataFrame({
        "open": closes, "close": closes, "high": highs, "low": lows, "volume": volumes
    })


# ---------------------------------------------------------------------------
# Pin 1: producer emits new ATR-clearance signals
# ---------------------------------------------------------------------------
def test_b727_pin1_producer_emits_atr_clearance_signals():
    """compute_volume must emit above_prev_high_clearance_atr_05 + below_prev_low_clearance_atr_05."""
    df = _build_df()
    result = compute_volume(df)
    assert "above_prev_high_clearance_atr_05" in result, (
        f"compute_volume must emit above_prev_high_clearance_atr_05; got keys missing"
    )
    assert "below_prev_low_clearance_atr_05" in result


# ---------------------------------------------------------------------------
# Pin 2: strategy consumes ATR-clearance gate (not bare above_prev_high)
# ---------------------------------------------------------------------------
def test_b727_pin2_strategy_consumes_atr_clearance_not_bare_gate():
    """strat_monthly_bias_momentum_long must require above_prev_high_clearance
    _atr_05, NOT bare above_prev_high."""
    # Bare-only: above_prev_high True but clearance False -> must NOT fire
    s_bare = {
        "monthly_bias_bull": True,
        "monthly_momentum_pos": True,
        "above_prev_high": True,
        "above_prev_high_clearance_atr_05": False,
    }
    result = strat_monthly_bias_momentum_long(s_bare)
    assert result["fires"] is False, (
        f"Should NOT fire on bare gate post-B727; got {result}"
    )

    # Clearance True -> should fire
    s_clearance = {
        "monthly_bias_bull": True,
        "monthly_momentum_pos": True,
        "above_prev_high_clearance_atr_05": True,
    }
    result = strat_monthly_bias_momentum_long(s_clearance)
    assert result["fires"] is True, f"Should fire on ATR-clearance gate; got {result}"


def test_b727_pin3_signals_used_declares_clearance_gate():
    """signals_used must declare above_prev_high_clearance_atr_05."""
    s = {
        "monthly_bias_bull": True,
        "monthly_momentum_pos": True,
        "above_prev_high_clearance_atr_05": True,
    }
    result = strat_monthly_bias_momentum_long(s)
    assert "above_prev_high_clearance_atr_05" in result["signals_used"]
    # Must NOT declare bare gate
    assert "above_prev_high" not in [
        sig for sig in result["signals_used"]
        if sig == "above_prev_high"
    ], "Must NOT declare bare above_prev_high post-B727"


# ---------------------------------------------------------------------------
# Pin 4: monthly bias gates still required
# ---------------------------------------------------------------------------
def test_b727_pin4_monthly_bias_gates_still_required():
    """Other 2 gates (monthly_bias_bull + monthly_momentum_pos) still required."""
    # Clearance True but monthly_bias_bull False
    s_no_bias = {
        "monthly_bias_bull": False,
        "monthly_momentum_pos": True,
        "above_prev_high_clearance_atr_05": True,
    }
    assert strat_monthly_bias_momentum_long(s_no_bias)["fires"] is False

    # Clearance True but monthly_momentum_pos False
    s_no_momentum = {
        "monthly_bias_bull": True,
        "monthly_momentum_pos": False,
        "above_prev_high_clearance_atr_05": True,
    }
    assert strat_monthly_bias_momentum_long(s_no_momentum)["fires"] is False
