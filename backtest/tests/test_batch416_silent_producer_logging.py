"""Batch 416 (2026-05-28 owner-approved): regression test for the
silent-producer-failure logging helpers.

Why this test exists:
  The AWS Phase 1A-beta cube run found 0 smc_* keys in 29,159 fired-trade
  signals_at_entry dicts, despite compute_smc_signals returning 28 valid
  keys when called in isolation. The screener's try/except blocks
  swallowed the actual error without trace. Same family of silent-gap
  failure for classification_change_* and (partially) institutional_*
  producers.

  Batch 416 replaces the silent passes with rate-limited logging helpers
  _log_silent_producer_failure (for exceptions) and _log_silent_producer_empty
  (for empty-return). The next cube run will reveal the actual AWS-
  environment failure mode in the logs.

  This test pins the helpers' behavior so future refactors can't
  silently revert to the pre-Batch-416 swallowed-exception pattern.
"""
from __future__ import annotations

import logging

import pytest

from backtest.signals import screener as scr


@pytest.fixture(autouse=True)
def _reset_seen_failures():
    """Each test starts with empty seen-sets so rate-limiting doesn't
    leak between tests."""
    scr._SILENT_PRODUCER_SEEN_FAILURES.clear()
    scr._SILENT_PRODUCER_SEEN_EMPTIES.clear()
    yield
    scr._SILENT_PRODUCER_SEEN_FAILURES.clear()
    scr._SILENT_PRODUCER_SEEN_EMPTIES.clear()


def test_log_silent_producer_failure_emits_first_occurrence(caplog):
    """First call for a (producer, exception-type) pair must log."""
    caplog.set_level(logging.WARNING, logger="backtest.signals.screener")
    exc = ValueError("missing module")
    scr._log_silent_producer_failure("test_producer", exc)
    assert any("Batch 416 silent-producer failure" in r.message
                and "test_producer" in r.message
                and "ValueError" in r.message
                for r in caplog.records), (
        f"expected first-occurrence warning; got: "
        f"{[r.message for r in caplog.records]}")


def test_log_silent_producer_failure_rate_limits_same_key(caplog):
    """Subsequent calls for the SAME (producer, exception-type) must be
    suppressed to avoid log spam (1900+ tickers x N days = millions)."""
    caplog.set_level(logging.WARNING, logger="backtest.signals.screener")
    exc = ValueError("same error twice")
    scr._log_silent_producer_failure("test_producer", exc)
    scr._log_silent_producer_failure("test_producer", exc)
    scr._log_silent_producer_failure("test_producer", exc)
    warnings = [r for r in caplog.records
                if "Batch 416 silent-producer failure" in r.message]
    assert len(warnings) == 1, (
        f"expected exactly 1 log entry across 3 calls; got {len(warnings)}")


def test_log_silent_producer_failure_distinct_exception_types(caplog):
    """Different exception TYPES for the same producer should each log
    once (we want visibility into multi-mode failure)."""
    caplog.set_level(logging.WARNING, logger="backtest.signals.screener")
    scr._log_silent_producer_failure("test_p", ValueError("v"))
    scr._log_silent_producer_failure("test_p", KeyError("k"))
    scr._log_silent_producer_failure("test_p", RuntimeError("r"))
    warnings = [r for r in caplog.records
                if "Batch 416 silent-producer failure" in r.message]
    assert len(warnings) == 3


def test_log_silent_producer_empty_emits_first_occurrence(caplog):
    caplog.set_level(logging.WARNING, logger="backtest.signals.screener")
    scr._log_silent_producer_empty("smc_ict.compute_smc_signals")
    warnings = [r for r in caplog.records
                if "Batch 416 silent-producer empty-return" in r.message]
    assert len(warnings) == 1


def test_log_silent_producer_empty_rate_limits_same_producer(caplog):
    caplog.set_level(logging.WARNING, logger="backtest.signals.screener")
    for _ in range(5):
        scr._log_silent_producer_empty("smc_ict.compute_smc_signals")
    warnings = [r for r in caplog.records
                if "Batch 416 silent-producer empty-return" in r.message]
    assert len(warnings) == 1


def test_screener_call_sites_use_helpers_not_silent_pass():
    """Source-grep regression: ensure the Batch 416 call sites actually
    invoke the helpers, not the pre-Batch-416 `except: pass`.

    B975 (2026-06-21 Council 77 P1 Bucket A A5 incidental test-stale fix):
    classification_change + institutional_signal call sites moved from
    screener.py to backtest/data/signal_loader.py during B927-B928 engine
    path unification (commits 6/11 + 7/11 of the Council 43 sequence).
    Assertions split across both files to follow the moved code."""
    from pathlib import Path
    src_screener = Path(scr.__file__).read_text(encoding="utf-8")
    # smc_ict pair still in screener.py
    assert "_log_silent_producer_failure(\"smc_ict\"" in src_screener
    assert "_log_silent_producer_empty(\"smc_ict.compute_smc_signals\")" in src_screener
    # classification_change + institutional_signal now in signal_loader.py
    # per B927-B928 extraction.
    from backtest.data import signal_loader as sl
    src_loader = Path(sl.__file__).read_text(encoding="utf-8")
    assert "_log_silent_producer_failure(\"classification_change\"" in src_loader
    assert "_log_silent_producer_failure(\"institutional_signal\"" in src_loader
