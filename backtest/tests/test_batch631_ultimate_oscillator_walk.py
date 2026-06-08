"""Batch 631 (2026-06-08) -- Stage 4 walk of strat_ultimate_oscillator
per CHECKLIST #105; last of 4 B623 REMOVE_OK regime-affinity candidates.

Source: backtest/signals/screener.py:strat_ultimate_oscillator (B631
F1+F2+a); backtest/signals/technical.py:compute_ultimate_oscillator
(Larry Williams 1976 UO producer); below_sma_200 (B630 producer).
Per CHECKLIST #77.

Owner-directed C option: F1 (silent-gap fix) + F2 (uo_overbought
producer-symmetric polish) + (a) B589-family bullish/bearish bar gate.

Pins:
  (1) LONG fires with 3-gate set (uo_oversold + price_above_sma_200
      + close_above_open)
  (2) SHORT fires with 3-gate set (uo_overbought + below_sma_200
      + close_below_open)
  (3) F1 silent-gap closed: missing below_sma_200 key blocks SHORT
      (pre-B631 would have auto-passed via `not s.get(price_above
      _sma_200)`)
  (4) F2 polish: SHORT now uses uo_overbought (symmetric with LONG's
      uo_oversold); raw `uo > 70` check removed
  (5) (a) bullish-bar gate: missing close_above_open blocks LONG
  (6) (a) bearish-bar gate: missing close_below_open blocks SHORT
  (7) LONG fires via Connors RSI(2)<5 alternative path
  (8) SHORT fires via Connors RSI(2)>95 alternative path
  (9) LAST `not s.get("price_above_sma_200")` active-code instance
      eliminated (sweep complete for this Tier 3 pattern)
  (10) ALL_STRATEGIES count unchanged at 221
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


def test_batch631_long_fires_3_gates():
    """Pin (1)."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        "uo_oversold": True,
        "price_above_sma_200": True,
        "close_above_open": True,
    }
    out = strat_ultimate_oscillator(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch631_short_fires_3_gates():
    """Pin (2)."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        "uo_overbought": True,              # B631 F2 positive symmetric
        "below_sma_200": True,              # B631 F1 positive symmetric
        "close_below_open": True,           # B631 (a)
    }
    out = strat_ultimate_oscillator(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch631_short_silent_gap_closed():
    """Pin (3): missing below_sma_200 must block SHORT (pre-B631 the
    `not s.get(price_above_sma_200)` silent-gap auto-fired)."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        "uo_overbought": True,
        # below_sma_200 ABSENT - pre-B631 silent-gap auto-fired
        "close_below_open": True,
    }
    assert strat_ultimate_oscillator(s)["fires"] is False, (
        "B631 F1 silent-gap fix: SHORT must NOT fire when below_sma_200 "
        "is absent (pre-B631 used `not s.get(price_above_sma_200)`)"
    )


def test_batch631_short_uses_uo_overbought_not_raw_threshold():
    """Pin (4): F2 polish - SHORT must use the producer's uo_overbought
    signal (symmetric with LONG's uo_oversold). Raw `s.get("uo", 50) > 70`
    check was removed."""
    from backtest.signals.screener import strat_ultimate_oscillator
    # uo_overbought True (semantically uo > 70) but uo numerical absent
    s = {
        "uo_overbought": True,
        "below_sma_200": True,
        "close_below_open": True,
    }
    assert strat_ultimate_oscillator(s)["fires"] is True
    # Even if uo numeric is BELOW 70, uo_overbought=True (producer-
    # set) fires - confirming the strategy now consumes the producer
    # signal, not the raw threshold.
    s_with_uo = dict(s); s_with_uo["uo"] = 50
    assert strat_ultimate_oscillator(s_with_uo)["fires"] is True


def test_batch631_long_bullish_bar_required():
    """Pin (5): (a) close_above_open must block LONG when absent."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        "uo_oversold": True,
        "price_above_sma_200": True,
        # close_above_open ABSENT
    }
    assert strat_ultimate_oscillator(s)["fires"] is False


def test_batch631_short_bearish_bar_required():
    """Pin (6)."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        "uo_overbought": True,
        "below_sma_200": True,
        # close_below_open ABSENT
    }
    assert strat_ultimate_oscillator(s)["fires"] is False


def test_batch631_long_connors_rsi_2_alternative():
    """Pin (7): LONG fires via Connors RSI(2)<5 OR-clause (Batch 206
    stacking; uo_oversold ABSENT but rsi_2<5 should still fire)."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        # uo_oversold ABSENT
        "rsi_2": 3,                        # < 5
        "price_above_sma_200": True,
        "close_above_open": True,
    }
    out = strat_ultimate_oscillator(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch631_short_connors_rsi_2_alternative():
    """Pin (8): SHORT fires via rsi_2>95 OR-clause."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        # uo_overbought ABSENT
        "rsi_2": 97,                       # > 95
        "below_sma_200": True,
        "close_below_open": True,
    }
    out = strat_ultimate_oscillator(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch631_price_above_sma_200_pattern_eliminated():
    """Pin (9): LAST `not s.get("price_above_sma_200")` instance is
    gone from active code. Sweep complete for this Tier 3 pattern.
    Docstring/comment occurrences allowed."""
    src = Path("backtest/signals/screener.py").read_text(encoding="utf-8")
    pat = re.compile(r'not s\.get\("price_above_sma_200"')
    active = []
    for i, line in enumerate(src.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if not re.search(r'(\band\b|\bor\b|=\s*\()', line):
            continue
        if pat.search(line):
            active.append((i, line.strip()))
    assert not active, (
        f"B631 F1 should eliminate the LAST `not s.get(price_above_sma"
        f"_200)` active-code instance; got:\n"
        + "\n".join(f"  L{n}: {l}" for n, l in active)
    )


def test_batch631_all_strategies_count_unchanged():
    """Pin (10): pure refactor + producer-signal symmetry polish + bar
    gate; no add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
