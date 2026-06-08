"""Batch 630 (2026-06-08) -- mega-sweep option E per owner directive.
Closes 4 family-bug patterns surfaced in B629 broader-grep
assessment: 27 active-code instances of `not s.get(...)` swept to
positive symmetric signals + 2 producer-additive signals.

Source: backtest/signals/technical.py:supertrend_bearish (B630 add) +
below_sma_50/200 + below_sma_9/21 (B630 add to compute_ema_sma);
backtest/signals/screener.py (27 swaps). Per CHECKLIST #77.

Owner-directed: "E" (Tier 1 + Tier 2 mega-sweep from B630 surface).

Patterns swept (all eliminated from active code):
  Tier 1 (inverse signal already existed):
    `not s.get("price_above_ema_200")` -> `below_ema_200` (16 instances)
    `not s.get("macd_12_26_9_bullish")` -> `macd_12_26_9_bearish` (4 inst)
  Tier 2 (producer-additive; new signals added):
    `not s.get("price_above_sma_50")` -> `below_sma_50` (4 inst; NEW)
    `not s.get("supertrend_bullish")` -> `supertrend_bearish` (3 inst; NEW)

Pins:
  (1) below_sma_50 emitted by compute_ema_sma
  (2) below_sma_200 emitted (symmetric to price_above_sma_200)
  (3) supertrend_bearish emitted by compute_supertrend
  (4) below_sma_50 symmetric to price_above_sma_50
  (5) supertrend_bearish symmetric to supertrend_bullish
  (6) sweep complete: no active `not s.get("price_above_ema_200"`
  (7) sweep complete: no active `not s.get("macd_12_26_9_bullish"`
  (8) sweep complete: no active `not s.get("price_above_sma_50"`
  (9) sweep complete: no active `not s.get("supertrend_bullish"`
  (10) spot-check: strat_supertrend_macd SHORT fires with both
       supertrend_bearish + macd_bearish (double-swap strategy)
  (11) spot-check: strat_supertrend_macd_short fires
  (12) spot-check: strat_evening_star_short fires with below_sma_50
  (13) spot-check: strat_supertrend_ichimoku_adx SHORT fires with
       supertrend_bearish
  (14) ALL_STRATEGIES count unchanged at 221
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _build_df(closes, highs=None, lows=None, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if highs is None: highs = [c + 0.5 for c in closes]
    if lows is None: lows = [c - 0.5 for c in closes]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


# ----- Producer pins -----

def test_batch630_below_sma_50_emitted():
    """Pin (1)."""
    from backtest.signals.technical import compute_ema_sma
    n = 220
    df = _build_df(list(np.linspace(100, 110, n)))
    out = compute_ema_sma(df)
    assert "below_sma_50" in out


def test_batch630_below_sma_200_emitted():
    """Pin (2)."""
    from backtest.signals.technical import compute_ema_sma
    n = 220
    df = _build_df(list(np.linspace(100, 110, n)))
    out = compute_ema_sma(df)
    assert "below_sma_200" in out


def test_batch630_supertrend_bearish_emitted():
    """Pin (3)."""
    from backtest.signals.technical import compute_supertrend
    n = 50
    df = _build_df(list(np.linspace(100, 110, n)))
    out = compute_supertrend(df)
    assert "supertrend_bearish" in out


def test_batch630_below_sma_50_symmetric():
    """Pin (4): rising data -> price_above_sma_50=True, below_sma_50=False;
    falling -> opposite."""
    from backtest.signals.technical import compute_ema_sma
    n = 220
    df_up = _build_df(list(np.linspace(100, 130, n)))
    out_up = compute_ema_sma(df_up)
    assert bool(out_up["price_above_sma_50"]) is True
    assert bool(out_up["below_sma_50"]) is False
    df_dn = _build_df(list(np.linspace(130, 100, n)))
    out_dn = compute_ema_sma(df_dn)
    assert bool(out_dn["price_above_sma_50"]) is False
    assert bool(out_dn["below_sma_50"]) is True


def test_batch630_supertrend_bearish_symmetric():
    """Pin (5): supertrend_bearish is exactly the boolean inverse of
    supertrend_bullish (mutually exclusive + exhaustive)."""
    from backtest.signals.technical import compute_supertrend
    # Test across multiple price scenarios; assert mutual exclusivity
    for closes in [
        list(np.linspace(100, 130, 60)),   # rising
        list(np.linspace(130, 100, 60)),   # falling
        [100.0] * 60,                       # flat
    ]:
        df = _build_df(closes)
        out = compute_supertrend(df)
        assert bool(out["supertrend_bullish"]) != bool(out["supertrend_bearish"]), (
            f"supertrend_bullish + supertrend_bearish must be mutually "
            f"exclusive + exhaustive; got bullish={out['supertrend_bullish']}, "
            f"bearish={out['supertrend_bearish']}"
        )


# ----- Sweep-complete pins -----

_SCREENER_SRC = None

def _screener_src():
    global _SCREENER_SRC
    if _SCREENER_SRC is None:
        _SCREENER_SRC = Path("backtest/signals/screener.py").read_text(encoding="utf-8")
    return _SCREENER_SRC


def _active_instances(signal_name: str) -> list[tuple[int, str]]:
    src = _screener_src()
    pat = re.compile(rf'not s\.get\("{signal_name}"')
    active = []
    for i, line in enumerate(src.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if not re.search(r'(\band\b|\bor\b|=\s*\()', line):
            continue
        if pat.search(line):
            active.append((i, line.strip()))
    return active


@pytest.mark.parametrize("signal_name", [
    "price_above_ema_200",
    "macd_12_26_9_bullish",
    "price_above_sma_50",
    "supertrend_bullish",
])
def test_batch630_sweep_complete(signal_name):
    """Pins (6)-(9): no active-code `not s.get("<signal>")` remains.
    Docstring/comment occurrences allowed."""
    active = _active_instances(signal_name)
    assert not active, (
        f"B630 sweep INCOMPLETE for {signal_name}: {len(active)} "
        f"active instances remain:\n"
        + "\n".join(f"  L{n}: {l}" for n, l in active)
    )


# ----- Spot-check fires -----

def test_batch630_supertrend_macd_short_fires():
    """Pin (10): strat_supertrend_macd SHORT (double-swap)."""
    from backtest.signals.screener import strat_supertrend_macd
    s = {
        "supertrend_bearish": True,
        "macd_12_26_9_bearish": True,
        "adx": 25,
    }
    out = strat_supertrend_macd(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch630_supertrend_macd_short_standalone_fires():
    """Pin (11): strat_supertrend_macd_short (standalone)."""
    from backtest.signals.screener import strat_supertrend_macd_short
    s = {
        "supertrend_bearish": True,
        "macd_12_26_9_bearish": True,
        "adx": 25,
    }
    out = strat_supertrend_macd_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch630_evening_star_short_fires_with_below_sma_50():
    """Pin (12)."""
    from backtest.signals.screener import strat_evening_star_short
    s = {
        "evening_star": True,
        "rsi_14": 60,
        "below_sma_50": True,
    }
    out = strat_evening_star_short(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch630_supertrend_ichimoku_adx_short_fires():
    """Pin (13)."""
    from backtest.signals.screener import strat_supertrend_ichimoku_adx
    s = {
        "supertrend_bearish": True,
        "ichi_below_cloud": True,
        "adx_strong": True,
    }
    out = strat_supertrend_ichimoku_adx(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch630_all_strategies_count_unchanged():
    """Pin (14): pure refactor + producer-additive; no add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
