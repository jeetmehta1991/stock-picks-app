# Source: B710 reviewer fire-count-ceiling + S4-B717-CEILING-FLAGGED-REDUNDANCY-DIAGNOSTIC + B656 + B358 + B207 patterns per CHECKLIST #77
"""B718 pin tests: strat_hull_rsi_short tightened to symmetrically match
strat_hull_rsi SHORT branch (post-B656/B358/B207 hardening).

B710 reviewer's fire-count-ceiling finding (B717 measured): strat_hull_rsi_short
fired 20,333/yr SHORT = state-flag rate above the 5K/yr ceiling.

B718 changes per B656/B358/B207 patterns symmetric with the dual:
* DROP rsi_9<50 (B656: accidentally-safe near-no-op midpoint inequality)
* ADD adx>20 trend confirmation (B207: cuts whipsaws in choppy markets)
* ADD below_ema_200 regime gate (B358: bear-regime constraint)

PATTERN W finding surfaced: post-tightening, strat_hull_rsi_short fires
on identical gates as strat_hull_rsi SHORT branch -> deterministic
duplicates. Queued as S4-B718-HULL-RSI-SHORT-DELETION-DECISION-VS-DUAL
for owner triage.
"""
from __future__ import annotations

from backtest.signals.screener import strat_hull_rsi_short


def test_b718_hull_pin1_no_longer_consumes_rsi_9():
    """strat_hull_rsi_short must NOT depend on rsi_9 post-B718."""
    # All B718 gates True + low DTC, rsi_9 wildly varies; should fire regardless of rsi_9
    s_base = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25,
        "below_ema_200": True,
        "days_to_cover": 2.0,  # below B718a 5.0 borrow threshold
    }
    # rsi_9 missing
    result = strat_hull_rsi_short(s_base)
    assert result["fires"] is True, f"Expected fire with rsi_9 missing; got {result}"

    # rsi_9 = 80 (very high, no longer relevant)
    s = {**s_base, "rsi_9": 80}
    result = strat_hull_rsi_short(s)
    assert result["fires"] is True, f"rsi_9=80 should no longer block; got {result}"

    # rsi_9 = 20 (very low, no longer relevant either)
    s = {**s_base, "rsi_9": 20}
    result = strat_hull_rsi_short(s)
    assert result["fires"] is True, f"rsi_9=20 should also fire; got {result}"


def test_b718_hull_pin2_requires_adx_trend_confirmation():
    """strat_hull_rsi_short must require adx>20 (or adx_trending) post-B718."""
    s_base = {
        "hull_bearish": True,
        "price_below_hull": True,
        "below_ema_200": True,
        "days_to_cover": 2.0,
    }
    # No ADX at all -- should NOT fire
    result = strat_hull_rsi_short(s_base)
    assert result["fires"] is False, (
        f"strat_hull_rsi_short fired without adx>20 trend confirmation; got {result}"
    )

    # Low ADX (12) -- should NOT fire (12 < 20)
    s = {**s_base, "adx": 12}
    result = strat_hull_rsi_short(s)
    assert result["fires"] is False, f"Low adx=12 should not fire; got {result}"

    # adx=25 -- should fire
    s = {**s_base, "adx": 25}
    result = strat_hull_rsi_short(s)
    assert result["fires"] is True, f"adx=25 should fire; got {result}"

    # Fallback to adx_trending=True without numeric adx
    s = {**s_base, "adx_trending": True}
    result = strat_hull_rsi_short(s)
    assert result["fires"] is True, f"adx_trending=True should fire; got {result}"


def test_b718_hull_pin3_requires_below_ema_200_regime_gate():
    """strat_hull_rsi_short must require below_ema_200=True post-B718."""
    s = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25,
        "days_to_cover": 2.0,
    }
    # below_ema_200 missing -> should NOT fire
    result = strat_hull_rsi_short(s)
    assert result["fires"] is False, f"Without below_ema_200 should not fire; got {result}"

    # below_ema_200 False -> should NOT fire
    s2 = {**s, "below_ema_200": False}
    result = strat_hull_rsi_short(s2)
    assert result["fires"] is False, f"below_ema_200=False should not fire; got {result}"

    # below_ema_200 True -> should fire
    s3 = {**s, "below_ema_200": True}
    result = strat_hull_rsi_short(s3)
    assert result["fires"] is True, f"below_ema_200=True should fire; got {result}"


def test_b718_hull_pin4_signals_used_declares_adx_and_ema():
    """signals_used must declare adx>20 + price_below_ema_200 post-B718."""
    s = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25,
        "below_ema_200": True,
        "days_to_cover": 2.0,
    }
    result = strat_hull_rsi_short(s)
    assert "adx>20" in result["signals_used"], (
        f"signals_used must declare adx>20; got {result['signals_used']}"
    )
    assert "price_below_ema_200" in result["signals_used"], (
        f"signals_used must declare price_below_ema_200; got {result['signals_used']}"
    )
    # And must NOT declare rsi_9<50 (removed)
    assert "rsi_9<50" not in result["signals_used"], (
        f"signals_used must NOT declare rsi_9<50 (dropped B718); got {result['signals_used']}"
    )


def test_b718_hull_pin5_signals_used_count_increased_from_3_to_4():
    """Post-B718 strat_hull_rsi_short has 4 gates (was 3 pre-B718)."""
    s = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25,
        "below_ema_200": True,
        "days_to_cover": 2.0,
    }
    result = strat_hull_rsi_short(s)
    assert len(result["signals_used"]) == 4, (
        f"Expected 4 gates post-B718; got {len(result['signals_used'])}: {result['signals_used']}"
    )
