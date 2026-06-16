"""Batch 358 gate-fix tests: Bucket B bear-block + Bucket C BAB gate removal.

Source (per CHECKLIST #77 canonical-source attribution):
- Owner approval 2026-05-25 of cell-audit PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md
  Bucket B + Bucket C recommendations
- Code paths modified: backtest/signals/screener.py
  - strat_hull_rsi (line ~313): added price_above_ema_200 to long; not-above to short
  - strat_cpr_narrow_bullish (line ~231): same per-direction 200-EMA regime gate
  - strat_cpr_narrow_momentum (line ~994): same per-direction 200-EMA regime gate
  - strat_xs_low_beta_long (line ~1487): REMOVED price_above_ema_200 gate per
    Frazzini-Pedersen full-sample BAB application
- Empirical motivation: PHASE_1A_BETA_STAGE_D_LOSER_CELL_AUDIT.md cells
  hull_rsi -1371pp, cpr_narrow_bullish -1671pp, cpr_narrow_momentum -355pp,
  xs_low_beta_long -187pp neutral

Pyramid tiers exercised:
  T1 (Unit) Per-strategy: gate fires only in approved regime
  T6 (Regression) Pin the specific gate logic change so future edits cannot
                  silently un-do the fix
"""
from __future__ import annotations

import pytest

from backtest.signals.screener import (
    strat_hull_rsi,
    strat_cpr_narrow_bullish,
    strat_cpr_narrow_momentum,
    strat_xs_low_beta_long,
)


def _hull_rsi_bull_signals(*, above_200: bool):
    """Signal dict that satisfies all Hull-RSI gates EXCEPT the regime gate.
    B722 STATE -> EVENT conversion: price_above_ema_200 ->
    price_above_ema_200_break_recent_5d. B656 dropped rsi_9>50/<50 no-op gate.
    """
    return {
        "hull_bullish":                          True,
        "price_above_hull":                      True,
        "hull_bearish":                          False,
        "price_below_hull":                      False,
        "adx":                                   25.0,
        "adx_trending":                          True,
        "price_above_ema_200_break_recent_5d":   above_200,  # B722 EVENT
        "below_ema_200_break_recent_5d":         False,
    }


def _hull_rsi_bear_signals(*, below_200: bool):
    """B722 EVENT-form: below_ema_200_break_recent_5d for SHORT regime gate."""
    return {
        "hull_bullish":                          False,
        "price_above_hull":                      False,
        "hull_bearish":                          True,
        "price_below_hull":                      True,
        "adx":                                   25.0,
        "adx_trending":                          True,
        "price_above_ema_200_break_recent_5d":   False,
        "below_ema_200_break_recent_5d":         below_200,  # B722 EVENT
    }


# ---------------------------------------------------------------------
# T1 - Unit: hull_rsi
# ---------------------------------------------------------------------
def test_hull_rsi_long_fires_in_bull_regime():
    """Long leg: fires when all bullish conditions met AND above 200-EMA."""
    result = strat_hull_rsi(_hull_rsi_bull_signals(above_200=True))
    assert result["fires"] is True
    assert result["direction"] == "long"


def test_hull_rsi_long_BLOCKED_in_bear_regime():
    """Batch 358 fix: long leg must NOT fire below 200-EMA even if other
    conditions are met (was firing pre-fix -> -1371pp loss in audit).
    B722: regime gate now EVENT (recent_5d break)."""
    result = strat_hull_rsi(_hull_rsi_bull_signals(above_200=False))
    assert result["fires"] is False


def test_hull_rsi_short_fires_in_bear_regime():
    """Short leg: fires when bearish conditions met AND below 200-EMA.
    B722 EVENT-form: below_ema_200_break_recent_5d."""
    result = strat_hull_rsi(_hull_rsi_bear_signals(below_200=True))
    assert result["fires"] is True
    assert result["direction"] == "short"


def test_hull_rsi_short_BLOCKED_in_bull_regime():
    """Batch 358 fix: short leg must NOT fire above 200-EMA.
    B722 EVENT-form: SHORT requires below_ema_200_break_recent_5d=True."""
    result = strat_hull_rsi(_hull_rsi_bear_signals(below_200=False))
    assert result["fires"] is False


# ---------------------------------------------------------------------
# T1 - Unit: cpr_narrow_bullish
# ---------------------------------------------------------------------
def _cpr_bullish_long_signals(*, above_200: bool):
    """B654 narrow-scope: cpr_narrow -> cpr_narrow_tight (0.05 threshold).
    B641 F1b: below_ema_200 positive symmetric for SHORT side."""
    return {
        "cpr_narrow_tight":     True,   # B654
        "above_cpr":            True,
        "rsi_14":               60.0,
        "above_avwap_50low":    True,
        "below_avwap_50low":    False,
        "price_above_ema_200":  above_200,
        "below_ema_200":        False,
    }


def _cpr_bullish_short_signals(*, below_200: bool):
    return {
        "cpr_narrow_tight":     True,   # B654
        "below_cpr":            True,
        "rsi_14":               40.0,
        "above_avwap_50low":    False,
        "below_avwap_50low":    True,   # B641 F1
        "price_above_ema_200":  False,
        "below_ema_200":        below_200,  # B641 F1b
    }


def test_cpr_narrow_bullish_long_fires_in_bull_regime():
    result = strat_cpr_narrow_bullish(_cpr_bullish_long_signals(above_200=True))
    assert result["fires"] is True
    assert result["direction"] == "long"


def test_cpr_narrow_bullish_long_BLOCKED_in_bear_regime():
    result = strat_cpr_narrow_bullish(_cpr_bullish_long_signals(above_200=False))
    assert result["fires"] is False


def test_cpr_narrow_bullish_short_fires_in_bear_regime():
    result = strat_cpr_narrow_bullish(_cpr_bullish_short_signals(below_200=True))
    assert result["fires"] is True
    assert result["direction"] == "short"


def test_cpr_narrow_bullish_short_BLOCKED_in_bull_regime():
    result = strat_cpr_narrow_bullish(_cpr_bullish_short_signals(below_200=False))
    assert result["fires"] is False


# ---------------------------------------------------------------------
# T1 - Unit: cpr_narrow_momentum
# ---------------------------------------------------------------------
def _cpr_momentum_long_signals(*, above_200: bool):
    """B654 narrow-scope: cpr_narrow -> cpr_narrow_tight (0.05 threshold).
    B641 F1b: below_ema_200 positive symmetric for SHORT."""
    return {
        "cpr_narrow_tight":      True,   # B654
        "above_cpr":             True,
        "rsi_14":                60.0,
        "macd_12_26_9_bullish":  True,
        "macd_12_26_9_bearish":  False,
        "price_above_ema_200":   above_200,
        "below_ema_200":         False,
    }


def _cpr_momentum_short_signals(*, below_200: bool):
    return {
        "cpr_narrow_tight":      True,   # B654
        "below_cpr":             True,
        "rsi_14":                40.0,
        "macd_12_26_9_bullish":  False,
        "macd_12_26_9_bearish":  True,
        "price_above_ema_200":   False,
        "below_ema_200":         below_200,  # B641 F1b
    }


def test_cpr_narrow_momentum_long_fires_in_bull_regime():
    result = strat_cpr_narrow_momentum(_cpr_momentum_long_signals(above_200=True))
    assert result["fires"] is True
    assert result["direction"] == "long"


def test_cpr_narrow_momentum_long_BLOCKED_in_bear_regime():
    result = strat_cpr_narrow_momentum(_cpr_momentum_long_signals(above_200=False))
    assert result["fires"] is False


def test_cpr_narrow_momentum_short_fires_in_bear_regime():
    result = strat_cpr_narrow_momentum(_cpr_momentum_short_signals(below_200=True))
    assert result["fires"] is True
    assert result["direction"] == "short"


def test_cpr_narrow_momentum_short_BLOCKED_in_bull_regime():
    result = strat_cpr_narrow_momentum(_cpr_momentum_short_signals(below_200=False))
    assert result["fires"] is False


# ---------------------------------------------------------------------
# T1 - Unit: xs_low_beta_long (Bucket C gate removal)
# ---------------------------------------------------------------------
def test_xs_low_beta_long_fires_regardless_of_regime():
    """Batch 358 Bucket C: regime gate REMOVED per Frazzini-Pedersen
    full-sample BAB literature. Strategy must fire whenever core
    factor signals are present, irrespective of 200-EMA status.
    B788 STATE -> EVENT conversion: xs_low_beta_decile (STATE) replaced
    by xs_low_beta_decile_entry_recent_5d (EVENT rank-crossing)."""
    base = {
        "xs_low_beta_decile_entry_recent_5d":  True,  # B788 EVENT
        "xs_avoid_high_ivol":                  True,
    }
    # Above 200-EMA
    result = strat_xs_low_beta_long({**base, "price_above_ema_200": True})
    assert result["fires"] is True
    # Below 200-EMA - was BLOCKED pre-fix; now fires per BAB application
    result = strat_xs_low_beta_long({**base, "price_above_ema_200": False})
    assert result["fires"] is True
    # Key absent (sentinel default) - should still fire
    result = strat_xs_low_beta_long(base)
    assert result["fires"] is True


def test_xs_low_beta_long_blocked_when_not_in_decile():
    """Strategy still blocked when core factor signal absent."""
    result = strat_xs_low_beta_long({
        "xs_low_beta_decile":  False,
        "xs_avoid_high_ivol":  True,
        "price_above_ema_200": True,
    })
    assert result["fires"] is False


def test_xs_low_beta_long_blocked_when_high_ivol():
    """Strategy still blocked when xs_avoid_high_ivol is False (i.e., the
    name IS in the high-IVOL exclusion zone)."""
    result = strat_xs_low_beta_long({
        "xs_low_beta_decile":  True,
        "xs_avoid_high_ivol":  False,
        "price_above_ema_200": True,
    })
    assert result["fires"] is False


# ---------------------------------------------------------------------
# T6 - Regression: pin the source-code changes so future edits cannot
# silently undo the gate fix.
# ---------------------------------------------------------------------
def test_batch358_regression_hull_rsi_gates_pinned():
    import inspect
    from backtest.signals import screener
    src = inspect.getsource(screener.strat_hull_rsi)
    assert "above_200" in src
    assert "Batch 358" in src


def test_batch358_regression_cpr_narrow_bullish_gates_pinned():
    import inspect
    from backtest.signals import screener
    src = inspect.getsource(screener.strat_cpr_narrow_bullish)
    assert "above_200" in src
    assert "Batch 358" in src


def test_batch358_regression_cpr_narrow_momentum_gates_pinned():
    import inspect
    from backtest.signals import screener
    src = inspect.getsource(screener.strat_cpr_narrow_momentum)
    assert "above_200" in src
    assert "Batch 358" in src


def test_batch358_regression_xs_low_beta_long_gate_removed():
    """Pin that the price_above_ema_200 gate is REMOVED from the long
    leg's `fires =` expression. The literal `s.get("price_above_ema_200"...)`
    must not appear inside the function body."""
    import inspect
    from backtest.signals import screener
    src = inspect.getsource(screener.strat_xs_low_beta_long)
    assert "Batch 358" in src
    # The 'fires =' assignment block must not gate on price_above_ema_200
    fires_block_start = src.index("fires = (")
    fires_block_end = src.index(")", fires_block_start)
    fires_block = src[fires_block_start:fires_block_end]
    assert "price_above_ema_200" not in fires_block, (
        "Bucket C fix: price_above_ema_200 gate must be removed from "
        "xs_low_beta_long. The 'fires =' block contains it: " + fires_block
    )
