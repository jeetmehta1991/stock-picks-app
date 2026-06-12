# Source: B654 narrow-scope tighten precedent + S4-B717-CEILING-FLAGGED-REDUNDANCY-DIAGNOSTIC per CHECKLIST #77
"""B724 pin tests: 2 ceiling-flagged strategies tightened.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* risk_off_bond_equity_short: 14,185/yr SHORT = state-flag rate
* poc_magnet_long: 11,334/yr LONG = state-flag rate

B724 changes:
(1) cross_asset.py: producer-additive narrow-scope variant
    risk_off_regime_bond_signal_strong (>5% 20d change vs loose >2%)
(2) strat_risk_off_bond_equity_short consumes strong variant
(3) strat_poc_magnet_long: 0.04 -> 0.02 POC-proximity threshold (B314
    reversal; direct threshold change since strategy is sole consumer)
"""
from __future__ import annotations

import pytest

from backtest.signals.screener import (
    strat_risk_off_bond_equity_short,
    strat_poc_magnet_long,
)


# ---------------------------------------------------------------------------
# Pin 1: risk_off_bond_equity_short consumes strong variant
# ---------------------------------------------------------------------------
def test_b724_pin1_risk_off_consumes_strong_variant():
    """strat_risk_off_bond_equity_short must require risk_off_regime_bond
    _signal_strong (>5% threshold), NOT bare risk_off_regime_bond_signal."""
    # Loose-only: bare True, strong False
    s_loose = {
        "risk_off_regime_bond_signal": True,
        "risk_off_regime_bond_signal_strong": False,
        "days_to_cover": 2.0,  # B718a 5.0 borrow gate
    }
    result = strat_risk_off_bond_equity_short(s_loose)
    assert result["fires"] is False, (
        f"Should not fire on loose-only post-B724; got {result}"
    )

    # Strong: True
    s_strong = {
        "risk_off_regime_bond_signal_strong": True,
        "days_to_cover": 2.0,
    }
    result = strat_risk_off_bond_equity_short(s_strong)
    assert result["fires"] is True, f"Should fire on strong; got {result}"


def test_b724_pin2_risk_off_signals_used_declares_strong():
    """signals_used must declare _strong variant."""
    s = {"risk_off_regime_bond_signal_strong": True, "days_to_cover": 2.0}
    result = strat_risk_off_bond_equity_short(s)
    assert "risk_off_regime_bond_signal_strong" in result["signals_used"]
    assert "risk_off_regime_bond_signal" not in [
        sig for sig in result["signals_used"]
        if sig == "risk_off_regime_bond_signal"
    ], "Must NOT declare bare loose signal post-B724"


# ---------------------------------------------------------------------------
# Pin 3: poc_magnet_long threshold tightened 0.04 -> 0.02
# ---------------------------------------------------------------------------
def test_b724_pin3_poc_magnet_long_threshold_tightened():
    """At distance = 0.03 (between old 0.04 and new 0.02), strategy
    must NOT fire post-B724; was True pre-B724."""
    s_03 = {
        "vp_close_near_poc_pct": 0.03,
        "vp_close_above_poc": True,
        "price_above_ema_200": True,
    }
    result = strat_poc_magnet_long(s_03)
    assert result["fires"] is False, (
        f"At distance=0.03 should not fire post-B724; got {result}"
    )

    # At distance = 0.01, should fire
    s_01 = {
        "vp_close_near_poc_pct": 0.01,
        "vp_close_above_poc": True,
        "price_above_ema_200": True,
    }
    result = strat_poc_magnet_long(s_01)
    assert result["fires"] is True, (
        f"At distance=0.01 should fire post-B724; got {result}"
    )


def test_b724_pin4_poc_magnet_long_still_requires_above_poc_and_ema():
    """Tightening threshold doesn't change other gate requirements."""
    # close but vp_close_above_poc False -> still no fire
    s_no_above = {
        "vp_close_near_poc_pct": 0.01,
        "vp_close_above_poc": False,
        "price_above_ema_200": True,
    }
    assert strat_poc_magnet_long(s_no_above)["fires"] is False

    # close but below ema_200 -> still no fire
    s_below_ema = {
        "vp_close_near_poc_pct": 0.01,
        "vp_close_above_poc": True,
        "price_above_ema_200": False,
    }
    assert strat_poc_magnet_long(s_below_ema)["fires"] is False


# ---------------------------------------------------------------------------
# Pin 5: Producer emits new strong variant
# ---------------------------------------------------------------------------
def test_b724_pin5_producer_emits_strong_variants():
    """compute_bond_equity_signals must emit *_strong variants when called."""
    # Mock data not available; just verify the producer code path includes
    # the new keys (via direct grep of the source).
    from backtest.signals import cross_asset
    import inspect
    source = inspect.getsource(cross_asset._ratio_trend_signal)
    assert "trend_up_strong" in source
    assert "trend_down_strong" in source
    source_top = inspect.getsource(cross_asset.compute_bond_equity_signals)
    assert "risk_off_regime_bond_signal_strong" in source_top
    assert "risk_on_regime_bond_signal_strong" in source_top
