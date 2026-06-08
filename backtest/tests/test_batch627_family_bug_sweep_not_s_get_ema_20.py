"""Batch 627 (2026-06-08) -- bundled family-bug sweep per CHECKLIST
#105 (n): 2 remaining `not s.get("price_above_ema_20")` instances
fixed (strat_awesome_oscillator SHORT + strat_stoch_oversold SHORT).
B626 fixed the 3rd (strat_force_index_breakout SHORT).

Source: backtest/signals/screener.py:strat_awesome_oscillator (B627)
+ backtest/signals/screener.py:strat_stoch_oversold (B627). Per
CHECKLIST #77 source-of-truth declaration.

Owner directive 2026-06-08: "2" (family-bug sweep option from B626
close). Per CHECKLIST (n): 3+ instances of the same pattern = bundled
family audit, not N sequential one-liners.

Pins:
  (1) awesome_oscillator SHORT fires with below_ema_20 (post-B627
      positive symmetric)
  (2) awesome_oscillator SHORT silent-gap closed: missing below_ema_20
      blocks (pre-B627 silent-gap auto-fired via not s.get)
  (3) awesome_oscillator LONG unchanged behavior
  (4) stoch_oversold SHORT fires with below_ema_20
  (5) stoch_oversold SHORT silent-gap closed: missing below_ema_20 blocks
  (6) stoch_oversold LONG unchanged behavior
  (7) family-bug grep returns 0 active code-path instances of
      `not s.get("price_above_ema_20")` (sweep complete)
  (8) ALL_STRATEGIES count unchanged at 221
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


# ----- strat_awesome_oscillator -----

def test_batch627_ao_short_fires_with_below_ema_20():
    """Pin (1)."""
    from backtest.signals.screener import strat_awesome_oscillator
    s = {"ao_cross_dn": True, "below_ema_20": True}
    out = strat_awesome_oscillator(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch627_ao_short_silent_gap_closed():
    """Pin (2): missing below_ema_20 must block (pre-B627 auto-fired
    via not s.get(price_above_ema_20))."""
    from backtest.signals.screener import strat_awesome_oscillator
    s = {
        "ao_cross_dn": True,
        # below_ema_20 ABSENT - pre-B627 silent-gap auto-fired
    }
    assert strat_awesome_oscillator(s)["fires"] is False, (
        "B627 F1 silent-gap fix: SHORT must NOT fire when below_ema_20 "
        "is absent (pre-B627 used `not s.get(price_above_ema_20)` which "
        "auto-passed)"
    )


def test_batch627_ao_long_unchanged():
    """Pin (3): LONG side unchanged by family-bug sweep."""
    from backtest.signals.screener import strat_awesome_oscillator
    s = {"ao_cross_up": True, "price_above_ema_20": True}
    out = strat_awesome_oscillator(s)
    assert out["fires"] is True and out["direction"] == "long"


# ----- strat_stoch_oversold -----

def test_batch627_stoch_short_fires_with_below_ema_20():
    """Pin (4)."""
    from backtest.signals.screener import strat_stoch_oversold
    s = {
        "stoch_overbought": True,
        "stoch_bearish_cross": True,
        "below_ema_20": True,
    }
    out = strat_stoch_oversold(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch627_stoch_short_silent_gap_closed():
    """Pin (5)."""
    from backtest.signals.screener import strat_stoch_oversold
    s = {
        "stoch_overbought": True,
        "stoch_bearish_cross": True,
        # below_ema_20 ABSENT
    }
    assert strat_stoch_oversold(s)["fires"] is False, (
        "B627 F1 silent-gap fix: SHORT must NOT fire when below_ema_20 "
        "is absent"
    )


def test_batch627_stoch_long_unchanged():
    """Pin (6)."""
    from backtest.signals.screener import strat_stoch_oversold
    s = {
        "stoch_oversold": True,
        "stoch_bullish_cross": True,
        "price_above_ema_20": True,
    }
    out = strat_stoch_oversold(s)
    assert out["fires"] is True and out["direction"] == "long"


# ----- Family-bug sweep complete -----

def test_batch627_family_bug_sweep_complete_no_active_pattern_remains():
    """Pin (7): grep screener.py for active `not s.get("price_above_ema_20"`
    -- only docstring/comment occurrences allowed (NOT inside code
    expressions). Sweep should leave 0 active instances."""
    screener_path = Path("backtest/signals/screener.py")
    src = screener_path.read_text(encoding="utf-8")
    # Find all matches, then classify each line as code vs docstring/comment
    pattern = re.compile(r'not s\.get\("price_above_ema_20"')
    lines = src.splitlines()
    active_matches = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            # Classify: skip lines that are inside a docstring or are
            # a comment. Heuristic: if the line stripped starts with
            # `#` or is inside a quoted string the regex shouldn't be
            # part of a Python expression. The pattern itself contains
            # `s.get(` which is code-like, so the simplest classifier
            # is: skip if the regex match is INSIDE a quoted-string on
            # the same line (i.e., docstring narrative) - detected by
            # the absence of `=` or `and`/`or` keywords before the match.
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            # Docstring or string-literal heuristic: if the line is
            # purely text content (no Python operators near the match),
            # it's in a docstring.
            # We test for active-code by requiring the pattern is
            # part of an `and` / `or` expression or an assignment.
            if not re.search(r'(\band\b|\bor\b|=\s*\(|=\s*\\)', line):
                continue
            active_matches.append((i + 1, line.strip()))
    assert not active_matches, (
        f"B627 family-bug sweep INCOMPLETE: {len(active_matches)} "
        f"active code-path instances of `not s.get(price_above_ema_20)` "
        f"remain:\n" + "\n".join(f"  L{n}: {l}" for n, l in active_matches)
    )


def test_batch627_all_strategies_count_unchanged():
    """Pin (8): pure refactor; no add/delete."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221
