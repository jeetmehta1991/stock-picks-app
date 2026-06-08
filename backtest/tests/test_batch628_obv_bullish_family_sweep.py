"""Batch 628 (2026-06-08) -- bundled family-bug sweep per CHECKLIST
#105 (n) on `not s.get("obv_bullish")` pattern across 7 strategies +
F2 docstring for strat_camarilla_s3_bounce (the originating walk).

Source: backtest/signals/screener.py (B628 swaps in 7 strategies);
backtest/signals/technical.py:obv_bullish + obv_bearish (B617
producer pair). Per CHECKLIST #77 source-of-truth declaration.

Owner directive 2026-06-08: "B" (option B from B628 walk surface -
bundled family sweep + F2 doc for the originating strategy).

The 7 strategies swept (`not s.get("obv_bullish")` -> `s.get(
"obv_bearish", False)`):
  1. strat_pivot_s1_bounce SHORT
  2. strat_camarilla_s3_bounce SHORT (originating; also gets F2 doc)
  3. strat_mfi_oversold SHORT
  4. strat_keltner_lower SHORT
  5. strat_bullish_engulfing_support SHORT
  6. strat_camarilla_rsi_obv SHORT (partial - 2nd silent-gap on
     cmf_positive remains; cmf-family follow-up batch needed)
  7. strat_camarilla_rsi_obv_short (partial; same caveat)

PENDING CMF-FAMILY FOLLOW-UP: 4 strategies use `not s.get(
"cmf_positive")` pattern - same family-bug pattern; requires
producer-additive `cmf_negative` to be added to compute_volume
before sweep. Surfaced for owner approval; not actioned in B628.

Pins:
  (1) strat_pivot_s1_bounce SHORT fires with obv_bearish
  (2) strat_pivot_s1_bounce SHORT silent-gap closed
  (3) strat_camarilla_s3_bounce SHORT fires with obv_bearish
  (4) strat_camarilla_s3_bounce SHORT silent-gap closed
  (5) strat_mfi_oversold SHORT fires with obv_bearish
  (6) strat_mfi_oversold SHORT silent-gap closed
  (7) strat_keltner_lower SHORT fires with obv_bearish
  (8) strat_keltner_lower SHORT silent-gap closed
  (9) strat_bullish_engulfing_support SHORT fires with obv_bearish
  (10) strat_bullish_engulfing_support SHORT silent-gap closed
  (11) strat_camarilla_rsi_obv SHORT obv-half fires correctly
  (12) strat_camarilla_rsi_obv_short obv-half fires correctly
  (13) family-bug sweep complete: no active-code instance of
       `not s.get("obv_bullish")` remains in screener.py
  (14) ALL_STRATEGIES count unchanged at 221
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


# ----- 1. pivot_s1_bounce -----

def test_batch628_pivot_s1_short_fires_with_obv_bearish():
    """Pin (1)."""
    from backtest.signals.screener import strat_pivot_s1_bounce
    s = {"near_r1": True, "shooting_star": True, "obv_bearish": True}
    out = strat_pivot_s1_bounce(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch628_pivot_s1_short_silent_gap_closed():
    """Pin (2)."""
    from backtest.signals.screener import strat_pivot_s1_bounce
    s = {"near_r1": True, "shooting_star": True}  # obv_bearish ABSENT
    assert strat_pivot_s1_bounce(s)["fires"] is False


# ----- 2. camarilla_s3_bounce -----

def test_batch628_camarilla_s3_short_fires_with_obv_bearish():
    """Pin (3)."""
    from backtest.signals.screener import strat_camarilla_s3_bounce
    s = {"near_cam_r3": True, "rsi_14": 70, "obv_bearish": True}
    out = strat_camarilla_s3_bounce(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch628_camarilla_s3_short_silent_gap_closed():
    """Pin (4)."""
    from backtest.signals.screener import strat_camarilla_s3_bounce
    s = {"near_cam_r3": True, "rsi_14": 70}  # obv_bearish ABSENT
    assert strat_camarilla_s3_bounce(s)["fires"] is False


# ----- 3. mfi_oversold -----

def test_batch628_mfi_oversold_short_fires_with_obv_bearish():
    """Pin (5)."""
    from backtest.signals.screener import strat_mfi_oversold
    s = {"mfi_overbought": True, "near_r1": True, "obv_bearish": True}
    out = strat_mfi_oversold(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch628_mfi_oversold_short_silent_gap_closed():
    """Pin (6)."""
    from backtest.signals.screener import strat_mfi_oversold
    s = {"mfi_overbought": True, "near_r1": True}
    assert strat_mfi_oversold(s)["fires"] is False


# ----- 4. keltner_lower -----

def test_batch628_keltner_lower_short_fires_with_obv_bearish():
    """Pin (7)."""
    from backtest.signals.screener import strat_keltner_lower
    s = {"kc_touch_upper": True, "shooting_star": True, "obv_bearish": True}
    out = strat_keltner_lower(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch628_keltner_lower_short_silent_gap_closed():
    """Pin (8)."""
    from backtest.signals.screener import strat_keltner_lower
    s = {"kc_touch_upper": True, "shooting_star": True}
    assert strat_keltner_lower(s)["fires"] is False


# ----- 5. bullish_engulfing_support -----

def test_batch628_bullish_engulfing_short_fires_with_obv_bearish():
    """Pin (9)."""
    from backtest.signals.screener import strat_bullish_engulfing_support
    s = {"bearish_engulfing": True, "near_r1": True, "obv_bearish": True}
    out = strat_bullish_engulfing_support(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch628_bullish_engulfing_short_silent_gap_closed():
    """Pin (10)."""
    from backtest.signals.screener import strat_bullish_engulfing_support
    s = {"bearish_engulfing": True, "near_r1": True}
    assert strat_bullish_engulfing_support(s)["fires"] is False


# ----- 6 + 7. camarilla_rsi_obv duo (partial F1 only; cmf gate untouched) -----

def test_batch628_camarilla_rsi_obv_short_obv_half_fires():
    """Pin (11): obv_bearish swap works on the dual (cmf gate still uses
    `not cmf_positive` silent-gap PENDING follow-up; provide cmf_positive
    absent to satisfy that gate too)."""
    from backtest.signals.screener import strat_camarilla_rsi_obv
    s = {
        "near_cam_r3": True,
        "rsi_14": 70,
        "obv_bearish": True,
        # cmf_positive ABSENT - the pending silent-gap gate
    }
    out = strat_camarilla_rsi_obv(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch628_camarilla_rsi_obv_short_single_fires():
    """Pin (12): standalone strat_camarilla_rsi_obv_short fires when
    obv_bearish True + cmf_positive absent."""
    from backtest.signals.screener import strat_camarilla_rsi_obv_short
    s = {
        "near_cam_r3": True,
        "rsi_14": 70,
        "obv_bearish": True,
    }
    out = strat_camarilla_rsi_obv_short(s)
    assert out["fires"] is True and out["direction"] == "short"


# ----- Family-bug sweep completeness -----

def test_batch628_obv_bullish_family_sweep_complete():
    """Pin (13): grep screener.py for active `not s.get("obv_bullish")`
    in code paths (NOT docstrings/comments). Should return 0 instances.
    Docstring/comment occurrences that describe the historical fix are
    allowed."""
    screener_path = Path("backtest/signals/screener.py")
    src = screener_path.read_text(encoding="utf-8")
    lines = src.splitlines()
    pattern = re.compile(r'not s\.get\("obv_bullish"')
    active = []
    for i, line in enumerate(lines):
        if not pattern.search(line):
            continue
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        # Heuristic: docstrings won't have `and`/`or`/`=` near the regex
        if not re.search(r'(\band\b|\bor\b|=\s*\()', line):
            continue
        active.append((i + 1, line.strip()))
    assert not active, (
        f"B628 family-bug sweep INCOMPLETE: {len(active)} active code "
        f"instances of `not s.get(obv_bullish)` remain:\n"
        + "\n".join(f"  L{n}: {l}" for n, l in active)
    )


def test_batch628_all_strategies_count_unchanged():
    """Pin (14): pure refactor; no add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
