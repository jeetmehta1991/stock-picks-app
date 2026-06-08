"""Batch 629 (2026-06-08) -- cmf-family bundled sweep per CHECKLIST
#105 (n) on `not s.get("cmf_positive")` pattern across 4 strategies.

Source: backtest/signals/technical.py (B629 added cmf_negative
producer; symmetric to cmf_positive); backtest/signals/screener.py
(B629 swaps in 4 strategies). Per CHECKLIST #77.

Owner-directed B629 closes the cmf_positive silent-gap pattern
surfaced in B628 follow-up. Producer-additive: cmf_negative added to
compute_volume; grep clean (B628 confirmed only 4 strategies
referenced the pattern).

The 4 strategies swept (`not s.get("cmf_positive")` -> `s.get(
"cmf_negative", False)`):
  1. strat_prev_day_low_bounce SHORT (was screener.py L375)
  2. strat_williams_r_oversold SHORT (was screener.py L464)
  3. strat_camarilla_rsi_obv SHORT (was L1446; 2nd silent-gap from B628)
  4. strat_camarilla_rsi_obv_short (was L1696; 2nd silent-gap from B628)

Pins:
  (1) producer emits cmf_negative
  (2) cmf_negative is True when CMF < 0 (symmetric to cmf_positive
      True when CMF > 0)
  (3) prev_day_low_bounce SHORT fires with cmf_negative
  (4) prev_day_low_bounce SHORT silent-gap closed
  (5) williams_r_oversold SHORT fires with cmf_negative
  (6) williams_r_oversold SHORT silent-gap closed
  (7) camarilla_rsi_obv SHORT fully fires (BOTH B628 obv-fix + B629
      cmf-fix gates positive)
  (8) camarilla_rsi_obv_short fully fires
  (9) sweep complete: 0 active-code instances of `not s.get(
      "cmf_positive")` remain
  (10) ALL_STRATEGIES count unchanged at 221
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None:
        opens = closes[:]
    if volumes is None:
        volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


# ----- Producer pins -----

def test_batch629_producer_emits_cmf_negative():
    """Pin (1)."""
    from backtest.signals.technical import compute_volume
    n = 30
    closes = list(np.linspace(110, 100, n))   # declining -> CMF likely negative
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    assert "cmf_negative" in out, "B629 producer must emit cmf_negative"


def test_batch629_cmf_negative_symmetric_to_positive():
    """Pin (2): cmf_negative + cmf_positive are mutually exclusive for
    nonzero CMF. (At CMF == 0 exactly, both are False - acceptable
    since both use strict inequalities.)

    CMF = sum((close-low - high+close) / (high-low) * vol) / sum(vol)
        = sum(((2c - h - l) / (h - l)) * vol) / sum(vol)
    For CMF > 0 need close BIASED TOWARD HIGH within bar.
    For CMF < 0 need close BIASED TOWARD LOW within bar."""
    from backtest.signals.technical import compute_volume
    n = 30
    closes = list(np.linspace(100, 110, n))
    # close biased TOWARD HIGH -> CMF positive
    highs_up = [c + 0.1 for c in closes]   # close very near high
    lows_up = [c - 1.0 for c in closes]    # far from low
    df_up = _build_df(closes, highs_up, lows_up)
    out_up = compute_volume(df_up)
    assert bool(out_up["cmf_positive"]) is True
    assert bool(out_up["cmf_negative"]) is False
    # close biased TOWARD LOW -> CMF negative
    highs_dn = [c + 1.0 for c in closes]   # far from high
    lows_dn = [c - 0.1 for c in closes]    # close very near low
    df_dn = _build_df(closes, highs_dn, lows_dn)
    out_dn = compute_volume(df_dn)
    assert bool(out_dn["cmf_positive"]) is False
    assert bool(out_dn["cmf_negative"]) is True


# ----- 1. prev_day_low_bounce -----

def test_batch629_prev_day_low_bounce_short_fires():
    """Pin (3)."""
    from backtest.signals.screener import strat_prev_day_low_bounce
    s = {"near_prev_high": True, "shooting_star": True, "cmf_negative": True}
    out = strat_prev_day_low_bounce(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch629_prev_day_low_bounce_short_silent_gap_closed():
    """Pin (4)."""
    from backtest.signals.screener import strat_prev_day_low_bounce
    s = {"near_prev_high": True, "shooting_star": True}  # cmf_negative ABSENT
    assert strat_prev_day_low_bounce(s)["fires"] is False


# ----- 2. williams_r_oversold -----

def test_batch629_williams_r_oversold_short_fires():
    """Pin (5)."""
    from backtest.signals.screener import strat_williams_r_oversold
    s = {
        "williams_r": -15,         # >-20 -> overbought-side condition
        "price_above_ema_200": False,
        "cmf_negative": True,
    }
    out = strat_williams_r_oversold(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch629_williams_r_oversold_short_silent_gap_closed():
    """Pin (6)."""
    from backtest.signals.screener import strat_williams_r_oversold
    s = {
        "williams_r": -15,
        "price_above_ema_200": False,
        # cmf_negative ABSENT
    }
    assert strat_williams_r_oversold(s)["fires"] is False


# ----- 3 + 4. camarilla_rsi_obv (dual + standalone) -----

def test_batch629_camarilla_rsi_obv_short_full_positive_signals():
    """Pin (7): both B628 obv-fix AND B629 cmf-fix gates use positive
    symmetric signals."""
    from backtest.signals.screener import strat_camarilla_rsi_obv
    s = {
        "near_cam_r3": True,
        "rsi_14": 70,
        "obv_bearish": True,
        "cmf_negative": True,
    }
    out = strat_camarilla_rsi_obv(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch629_camarilla_rsi_obv_short_standalone_full_positive():
    """Pin (8)."""
    from backtest.signals.screener import strat_camarilla_rsi_obv_short
    s = {
        "near_cam_r3": True,
        "rsi_14": 70,
        "obv_bearish": True,
        "cmf_negative": True,
    }
    out = strat_camarilla_rsi_obv_short(s)
    assert out["fires"] is True and out["direction"] == "short"


# ----- Family-bug sweep completeness -----

def test_batch629_cmf_family_sweep_complete():
    """Pin (9): grep screener.py for active code instances of
    `not s.get("cmf_positive")`. Should return 0."""
    src = Path("backtest/signals/screener.py").read_text(encoding="utf-8")
    pattern = re.compile(r'not s\.get\("cmf_positive"')
    active = []
    for i, line in enumerate(src.splitlines()):
        if not pattern.search(line):
            continue
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if not re.search(r'(\band\b|\bor\b|=\s*\()', line):
            continue
        active.append((i + 1, line.strip()))
    assert not active, (
        f"B629 cmf-family sweep INCOMPLETE: {len(active)} active "
        f"instances of `not s.get(cmf_positive)` remain:\n"
        + "\n".join(f"  L{n}: {l}" for n, l in active)
    )


def test_batch629_all_strategies_count_unchanged():
    """Pin (10)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
