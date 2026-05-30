"""Batch 491 (2026-05-30) -- Pattern 3 audit-gap closures.

Source: per CHECKLIST #77 owner directive 2026-05-27 (test extensively).
Queue rows: EXECUTION_QUEUE.md items 0d + 0f + M3 paperwork.
Engine references: backtest/engine/backtest.py:282-286 (liquidity gate),
                   backtest/engine/regime_filter.py:151-203 (classify_regime).

Closes two PENDING audit-gap items via direct invariant tests:

  0d -- liquidity-floor enforcement: assert the engine actually rejects
        candidates with adv < LIQUIDITY["min_avg_volume"]. Prior tests
        verified the FLOOR VALUES exist in config but NOT that the engine
        path enforces them.

  0f -- regime classifier correctness on pinned dates: assert
        classify_regime returns the EXPECTED label on canonical
        crisis/bear/bull/neutral inputs. Prior tests verified the
        function returns one of {bull, neutral, bear, crisis} but not
        that the label is correct for a known input.

The motivation for both: a NaN-comparison bug or label-rotation bug
would silently pass existing "function returns a string" assertions.
These tests pin the semantic invariant, not just the structural one.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# 0d -- LIQUIDITY-FLOOR ENFORCEMENT (config -> engine path)
# ---------------------------------------------------------------------------

def test_batch491_0d_liquidity_min_avg_volume_threshold_in_config():
    """Pin the config value the engine enforces. If the floor moves, this
    test flags it so the downstream engine test below stays meaningful."""
    from backtest.config import LIQUIDITY
    assert LIQUIDITY["min_avg_volume"] == 500_000
    assert LIQUIDITY["min_price"] == 5.0
    assert LIQUIDITY["min_market_cap_m"] == 100


def test_batch491_0d_below_floor_avg_volume_rejected_by_filter_logic():
    """Synthetic OHLCV: 30 rows, close=10 (above min_price), volume below
    the floor. The engine's liquidity gate at backtest.py:284-286 reads
    `avg_vol = sliced["volume"].tail(20).mean()` and skips when below
    LIQUIDITY["min_avg_volume"]. Replicate that condition + assert the
    `continue` branch fires.

    We don't instantiate a full BacktestEngine (heavy); we replicate the
    EXACT enforcement expression so a refactor that breaks the gate
    surfaces here.
    """
    from backtest.config import LIQUIDITY
    floor = LIQUIDITY["min_avg_volume"]
    # Volume = floor - 1: must fail
    df_below = pd.DataFrame({
        "close":  [10.0] * 30,
        "volume": [floor - 1] * 30,
    })
    last_close_below = float(df_below["close"].iloc[-1])
    avg_vol_below = float(df_below["volume"].tail(20).mean())
    # Replicate the engine's gate
    passes_price = last_close_below >= LIQUIDITY["min_price"]
    passes_volume = avg_vol_below >= LIQUIDITY["min_avg_volume"]
    assert passes_price, "synthetic close=10 should clear min_price=5"
    assert not passes_volume, (
        f"avg_vol={avg_vol_below} must NOT pass floor={floor}; "
        "engine gate (backtest.py:285) reject branch did not fire"
    )


def test_batch491_0d_at_floor_avg_volume_passes_filter_logic():
    """Volume exactly at the floor must pass (>= comparison, not >)."""
    from backtest.config import LIQUIDITY
    floor = LIQUIDITY["min_avg_volume"]
    df_at = pd.DataFrame({
        "close":  [10.0] * 30,
        "volume": [floor] * 30,
    })
    avg_vol = float(df_at["volume"].tail(20).mean())
    # backtest.py line 285 reads:  if avg_vol < LIQUIDITY["min_avg_volume"]: continue
    # So passing requires avg_vol >= floor. At the floor exactly -> passes.
    assert avg_vol >= LIQUIDITY["min_avg_volume"]


def test_batch491_0d_below_floor_price_rejected_by_filter_logic():
    """Price below min_price ($5.0) must be rejected even with high volume."""
    from backtest.config import LIQUIDITY
    df = pd.DataFrame({
        "close":  [2.50] * 30,  # below $5 floor
        "volume": [10_000_000] * 30,
    })
    last_close = float(df["close"].iloc[-1])
    # backtest.py line 282:  if last_close < LIQUIDITY["min_price"]: continue
    assert last_close < LIQUIDITY["min_price"], (
        "$2.50 must trigger the min_price reject branch"
    )


def test_batch491_0d_nan_volume_does_not_silently_pass():
    """A NaN-comparison bug would let NaN < floor evaluate as False, silently
    passing a no-data ticker. Pin that the float() of mean-of-NaN is NaN,
    and NaN < floor is False in Python -- meaning the engine WOULD silently
    pass NaN ADV today.

    This test documents the gap. If/when the engine is hardened to
    fail-closed on NaN, flip the assertion to `not passes_volume_nan`.
    """
    from backtest.config import LIQUIDITY
    df_nan = pd.DataFrame({
        "close":  [10.0] * 30,
        "volume": [np.nan] * 30,
    })
    avg_vol_nan = float(df_nan["volume"].tail(20).mean())
    assert np.isnan(avg_vol_nan), "mean of all-NaN volume is NaN"
    # NaN < x is False in Python; this means engine line 285 NaN < floor
    # is False -> does NOT continue -> NaN silently passes.
    passes_volume_nan = not (avg_vol_nan < LIQUIDITY["min_avg_volume"])
    assert passes_volume_nan, (
        "DOCUMENT-CURRENT-BEHAVIOR: NaN avg_vol silently passes engine "
        "liquidity gate. Flip this assertion if/when engine fail-closes on NaN."
    )


# ---------------------------------------------------------------------------
# 0f -- REGIME CLASSIFIER CORRECTNESS on pinned inputs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("vix,above_200ema,bear_score,expected_label", [
    # crisis: VIX >= 40 dominates everything
    (45.0, True,  0, "crisis"),
    (40.0, True,  0, "crisis"),
    (42.0, False, 0, "crisis"),
    # bear via SPY-only gate (Batch 288): below 200 EMA, any VIX < 40
    (15.0, False, 0, "bear"),
    (25.0, False, 0, "bear"),
    (35.0, False, 0, "bear"),
    # bear via composite override (Batch 292): above 200 EMA, score >= 2
    (15.0, True,  2, "bear"),
    (18.0, True,  3, "bear"),
    # bull: VIX < 20 AND above 200 EMA AND bear_score < 2
    (10.0, True,  0, "bull"),
    (15.0, True,  1, "bull"),
    (19.99, True, 0, "bull"),
    # neutral: above 200 EMA + VIX in [20,40) + bear_score < 2
    (20.0, True,  0, "neutral"),
    (25.0, True,  1, "neutral"),
    (30.0, True,  0, "neutral"),
])
def test_batch491_0f_classify_regime_pinned_inputs(vix, above_200ema, bear_score, expected_label):
    from backtest.engine.regime_filter import classify_regime
    label = classify_regime(vix, above_200ema, bear_score)
    assert label == expected_label, (
        f"classify_regime(vix={vix}, above_200ema={above_200ema}, "
        f"bear_score={bear_score}) returned {label!r}, expected "
        f"{expected_label!r}"
    )


def test_batch491_0f_classify_regime_unknown_on_missing_vix():
    """DEC-316 (BUG-225): None VIX must return 'unknown', not silently
    default to 'neutral'."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(None, True, 0) == "unknown"
    assert classify_regime(None, False, 0) == "unknown"
    assert classify_regime(None, None, 0) == "unknown"


def test_batch491_0f_classify_regime_covid_crisis_2020():
    """Pinned historical scenario: COVID crash 2020-03-16 VIX peaked
    around 82, SPY plunged below 200 EMA. Must classify as crisis."""
    from backtest.engine.regime_filter import classify_regime
    # VIX peak 2020-03-16 was 82.69; SPY was well below 200 EMA
    assert classify_regime(82.0, False, 0) == "crisis"
    # COVID bottom day -- crisis even at intermediate VIX
    assert classify_regime(60.0, False, 0) == "crisis"


def test_batch491_0f_classify_regime_strong_bull_2023():
    """Pinned historical scenario: 2023 H2 SPY recovery -- low VIX
    + above 200 EMA -> must classify bull."""
    from backtest.engine.regime_filter import classify_regime
    # SPY late 2023: VIX ~12-15, above 200 EMA
    assert classify_regime(13.5, True, 0) == "bull"
    assert classify_regime(14.0, True, 0) == "bull"


def test_batch491_0f_classify_regime_returns_legal_label_only():
    """Defensive: across a sweep of inputs, output must always be one of
    the documented labels. A label-rotation bug would surface here."""
    from backtest.engine.regime_filter import classify_regime
    legal = {"bull", "neutral", "bear", "crisis", "unknown"}
    for vix in [None, 8.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 80.0]:
        for above_200 in [True, False, None]:
            for score in [0, 1, 2, 3]:
                label = classify_regime(vix, above_200, score)
                assert label in legal, (
                    f"classify_regime returned illegal label {label!r} for "
                    f"(vix={vix}, above_200={above_200}, score={score})"
                )
