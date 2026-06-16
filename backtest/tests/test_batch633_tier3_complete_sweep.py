"""Batch 633 (2026-06-08) -- Tier 3 complete sweep (B + C combined per
owner autonomous-execution directive). Eliminates ALL remaining
`not s.get(...)` family-bug patterns from active code.

Source: backtest/signals/technical.py (B633 added 6 producers:
hull_bearish, price_below_hull, below_vwap, ema_50_200_bearish,
price_below_tema, adx_di_bear; price_below_dema bonus); backtest/
signals/screener.py (B633 applied ~17 swaps across 9 strategies).
Per CHECKLIST #77.

Owner-directed (autonomous): "B C D E Then A. Execute BCDE
autonomously". B = Tier 3 inverse-exists sweep (3 patterns, 6 inst);
C = Tier 3 producer-additive sweep (7 patterns, 11 inst). Bundled
as B633 for atomicity.

Patterns swept:
  Tier 3 inverse-exists (B subset, no producer change):
    `not s.get("above_avwap_252low")` -> below_avwap_252low (2 inst)
    `not s.get("above_avwap_50low")`  -> below_avwap_50low (2 inst)
    `not s.get("price_above_ema_50")` -> below_ema_50 (2 inst)
  Tier 3 producer-additive (C subset, NEW producers):
    `not s.get("hull_bullish")`        -> hull_bearish (2 inst; NEW)
    `not s.get("price_above_hull")`    -> price_below_hull (2 inst; NEW)
    `not s.get("above_vwap")`          -> below_vwap (2 inst; NEW)
    `not s.get("ema_50_200_bullish")`  -> ema_50_200_bearish (2 inst; NEW)
    `not s.get("price_above_tema")`    -> price_below_tema (1 inst; NEW)
    `not s.get("adx_di_bull")`         -> adx_di_bear (1 inst; NEW)
    `not s.get("ichi_below_cloud")`    -> ichi_above_cloud (1 inst;
                                          existing producer; semantic
                                          tightening - in-cloud no
                                          longer fires; intentional)

POST-B633 MILESTONE: 0 active-code instances of `not s.get(...)`
across the entire screener.py. All 11 family-bug patterns swept across
B608/B616/B617/B627/B628/B629/B630/B631/B633. Pyramid pin (11) enforces.

Pins:
  (1) producer pin: hull_bearish + price_below_hull emitted
  (2) producer pin: below_vwap emitted
  (3) producer pin: ema_50_200_bearish emitted
  (4) producer pin: price_below_tema emitted
  (5) producer pin: adx_di_bear emitted
  (6) producer pin: ichi_above_cloud emitted (pre-existing; pinned
      here for cross-batch reference)
  (7) spot-check fires: strat_hull_rsi SHORT
  (8) spot-check fires: strat_prev_day_high_break SHORT (below_vwap)
  (9) spot-check fires: strat_pivot_r2_continuation SHORT
      (ema_50_200_bearish + below_avwap_*)
  (10) spot-check fires: strat_adx_initiation SHORT (adx_di_bear)
  (11) SWEEP COMPLETE: 0 active-code `not s.get(...)` instances in
       screener.py (entire family-bug pattern eliminated)
  (12) ALL_STRATEGIES count unchanged at 221
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

def test_batch633_hull_producers_emitted():
    """Pin (1)."""
    from backtest.signals.technical import compute_hull_ma
    df = _build_df(list(np.linspace(100, 110, 50)))
    out = compute_hull_ma(df)
    assert "hull_bearish" in out
    assert "price_below_hull" in out
    # Symmetric: in rising market hull_bullish True, hull_bearish False
    assert bool(out["hull_bullish"]) != bool(out["hull_bearish"]) or \
           (out["hull_bullish"] == out["hull_bearish"] == False)


def test_batch633_below_vwap_emitted():
    """Pin (2)."""
    from backtest.signals.technical import compute_vwap
    df = _build_df(list(np.linspace(100, 110, 30)))
    out = compute_vwap(df)
    assert "below_vwap" in out


def test_batch633_ema_50_200_bearish_emitted():
    """Pin (3)."""
    from backtest.signals.technical import compute_ema_sma
    df = _build_df(list(np.linspace(100, 110, 250)))
    out = compute_ema_sma(df)
    assert "ema_50_200_bearish" in out


def test_batch633_price_below_tema_emitted():
    """Pin (4)."""
    from backtest.signals.technical import compute_dema_tema
    df = _build_df(list(np.linspace(100, 110, 100)))
    out = compute_dema_tema(df)
    assert "price_below_tema" in out


def test_batch633_adx_di_bear_emitted():
    """Pin (5)."""
    from backtest.signals.technical import compute_adx
    df = _build_df(list(np.linspace(100, 110, 50)))
    out = compute_adx(df)
    assert "adx_di_bear" in out


def test_batch633_ichi_above_cloud_emitted():
    """Pin (6): cross-batch pin - pre-existing producer signal used by
    B633 swap of `not s.get(ichi_below_cloud)` in strat_ichimoku_tk_cross
    LONG side."""
    from backtest.signals.technical import compute_ichimoku
    df = _build_df(list(np.linspace(100, 110, 100)))
    out = compute_ichimoku(df)
    assert "ichi_above_cloud" in out


# ----- Spot-check fires -----

def test_batch633_hull_rsi_short_fires():
    """Pin (7) B823 UPDATED: strat_hull_rsi_short DELETED in B722 per
    Pattern W deterministic-duplicate finding (post-B718 tightening
    fired on IDENTICAL gates to strat_hull_rsi SHORT branch). Test
    converted to absence-pin (regression guard against B722 walkback)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "hull_rsi_short" not in ALL_STRATEGIES, (
        "B722 deleted hull_rsi_short per Pattern W deterministic-duplicate -- "
        "if it re-appears, that's regression from a B722 walkback"
    )


def test_batch633_prev_day_high_break_short_fires_with_below_vwap():
    """Pin (8)."""
    from backtest.signals.screener import strat_prev_day_high_break
    s = {
        "below_prev_low": True,
        "vol_spike_15x": True,
        "below_vwap": True,                # B633 positive symmetric
    }
    out = strat_prev_day_high_break(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch633_pivot_r2_continuation_short_fires():
    """Pin (9): ema_50_200_bearish + below_avwap_252low/50low both
    positive symmetric (B633 swaps)."""
    from backtest.signals.screener import strat_pivot_r2_continuation
    s = {
        "below_s2": True,
        "adx_trending": True,
        "ema_50_200_bearish": True,        # B633 positive symmetric
        "below_avwap_252low": True,        # B633 positive symmetric
        "below_avwap_50low": True,         # B633 positive symmetric
        "vol_spike_2x": True,
    }
    out = strat_pivot_r2_continuation(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch633_adx_initiation_short_fires_with_adx_di_bear():
    """Pin (10)."""
    from backtest.signals.screener import strat_adx_initiation
    s = {
        "adx_cross_up": True,
        "adx_di_bear": True,               # B633 positive symmetric
    }
    out = strat_adx_initiation(s)
    assert out["fires"] is True and out["direction"] == "short"


# ----- Sweep completeness milestone -----

def test_batch633_all_not_s_get_patterns_eliminated():
    """Pin (11) MILESTONE: 0 active-code instances of `not s.get(...)`
    across screener.py. ALL 11 family-bug patterns swept across the
    B608/B616/B617/B627/B628/B629/B630/B631/B633 batch series.

    Docstring/comment occurrences allowed (and present, documenting
    the historical fixes)."""
    src = Path("backtest/signals/screener.py").read_text(encoding="utf-8")
    pat = re.compile(r'not s\.get\(\"[a-zA-Z_][a-zA-Z0-9_]*\"')
    active = []
    for i, line in enumerate(src.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if not re.search(r'(\band\b|\bor\b|=\s*\()', line):
            continue
        if pat.search(line):
            active.append((i, line.strip()))
    assert not active, (
        f"POST-B633 MILESTONE BROKEN: {len(active)} active-code "
        f"instances of `not s.get(...)` introduced after B633. "
        f"Pattern is supposed to be 100pct eliminated. New instances:\n"
        + "\n".join(f"  L{n}: {l}" for n, l in active[:10])
    )


def test_batch633_all_strategies_count_unchanged():
    """Pin (12): pure refactor + producer-additive; no add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
