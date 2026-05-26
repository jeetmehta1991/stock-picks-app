"""Batch 363 silent-gap fix: smart_money_score called unconditionally.

Source (per CHECKLIST #77 canonical-source attribution):
- Owner approval 2026-05-25 of Batch 362c root-cause diagnosis:
  backtest.py:1308 gated smart_money_score on QUIVER_API_KEY env var,
  but the function reads from data_prefetch/quiver/ cache only
  (NO live API per DEC-497 HARD CUT line 132 of smart_money.py).
  Result: 2026-05-24 Phase 1A-beta trade_log had 0% fire rate on
  smart_money_score / congressional_signal / insider_signal /
  institutional_signal -- invalidating DEC-124 confluence cells +
  "smart money lift >=3pp" passing criterion.

Code path:
- Pre-fix (backtest.py:1308): if os.environ.get("QUIVER_API_KEY"):
                              sm = smart_money_score(...)
- Post-fix: sm = smart_money_score(...) unconditionally; try/except
            falls back to sentinel zeros on hard exception.

Pyramid tiers exercised:
  T1 (Unit)        smart_money_score is called from _process_day even
                   when QUIVER_API_KEY is unset
  T6 (Regression)  source-code pin: 'QUIVER_API_KEY' must NOT appear
                   as a gate on smart_money_score in backtest.py
"""
from __future__ import annotations

import inspect
import os
from datetime import date
from unittest.mock import patch

import pytest


def test_batch363_no_quiver_api_key_gate_on_smart_money():
    """Regression pin: the QUIVER_API_KEY env-var gate on
    smart_money_score MUST be removed. If the test fails, someone
    re-introduced the silent-gap bug."""
    from backtest.engine import backtest as bt_mod
    src = inspect.getsource(bt_mod)
    # The string 'QUIVER_API_KEY' must NOT appear anywhere near the
    # smart_money_score call site as a gate. We check there's no
    # line that contains BOTH 'QUIVER_API_KEY' AND 'smart_money_score'
    # within a few lines of each other.
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if "smart_money_score(ticker" in line:
            # Check the previous 5 lines for the gate pattern
            window = "\n".join(lines[max(0, i-5):i])
            assert "QUIVER_API_KEY" not in window, (
                f"Batch 363 silent-gap regression: smart_money_score at "
                f"backtest.py line {i+1} is again gated on QUIVER_API_KEY. "
                f"The function reads from prefetch cache only and should be "
                f"called unconditionally."
            )


def test_batch363_smart_money_score_callable_without_api_key():
    """Functional check: smart_money_score must work cache-only (no env)."""
    from backtest.data.smart_money import smart_money_score
    # Clear the env var if set
    saved = os.environ.pop("QUIVER_API_KEY", None)
    try:
        # Should not raise; should return a dict with the expected keys
        result = smart_money_score("AAPL", date(2024, 6, 15))
        assert isinstance(result, dict)
        # Whether or not cache exists for this ticker, the function returns
        # a well-formed dict with the contract keys
        for key in ("composite_signal", "score", "congressional_signal",
                    "insider_signal", "institutional_signal"):
            assert key in result, f"smart_money_score missing contract key: {key}"
    finally:
        if saved is not None:
            os.environ["QUIVER_API_KEY"] = saved


def test_batch363_smart_money_default_sentinel_on_exception():
    """Engine fallback: if smart_money_score raises, the engine uses
    sentinel zeros instead of crashing."""
    from backtest.engine import backtest as bt_mod
    src = inspect.getsource(bt_mod)
    # Pin the fallback try/except + sentinel default
    assert 'sm = {"composite_signal": "none"' in src, (
        "Batch 363 fix: sentinel default must remain as fallback when "
        "smart_money_score raises an unexpected exception"
    )
    assert "smart_money_score failed for" in src, (
        "Batch 363 fix: warning log on smart_money_score exception"
    )


def test_batch363_smart_money_score_dict_keys_match_engine_assignment():
    """The keys the engine reads from sm (sm.get('score'),
    sm.get('congressional_signal'), etc.) must be present in
    smart_money_score()'s return dict."""
    from backtest.data.smart_money import smart_money_score
    saved = os.environ.pop("QUIVER_API_KEY", None)
    try:
        result = smart_money_score("NONEXISTENT_TICKER", date(2024, 6, 15))
        # The engine assignments per backtest.py:1710-1716 read these keys:
        engine_keys = ["score", "congressional_signal", "insider_signal",
                       "institutional_signal", "composite_signal"]
        for k in engine_keys:
            assert k in result, f"engine reads sm.get({k!r}) but key missing"
    finally:
        if saved is not None:
            os.environ["QUIVER_API_KEY"] = saved
