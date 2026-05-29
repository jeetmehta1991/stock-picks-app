"""Shared silent-failure logger (Batch 458 / AU2 — generalised from
Batch 416 screener.py pattern).

The repo historically swallowed exceptions with `except Exception: pass`
inside producer wrappers. When a producer silently failed at universe
scale (1,937 tickers x 1,044 days), the failure was invisible: the
output dict was missing the producer's keys but no error appeared in
logs. Batch 416 introduced a screener-local one-shot logger; Batch 458
generalises it so every critical file uses the same helper.

Usage:
    from backtest.util.silent_failure_logger import (
        log_silent_failure, log_silent_empty,
    )

    try:
        out = some_producer(...)
        if out:
            signals.update(out)
        else:
            log_silent_empty("some_producer")
    except Exception as e:
        log_silent_failure("some_producer", e)

Both functions rate-limit to ONE log line per (component, exception-type)
per process so a producer that fails every day for 1,937 tickers does
not flood the log with millions of identical lines.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_SEEN_FAILURES: set = set()
_SEEN_EMPTIES: set = set()


def log_silent_failure(component_name: str, exc: BaseException) -> None:
    """Log the FIRST occurrence of `exc` from `component_name` in this
    process, then suppress further identical (component, exception-type)
    log lines.

    Used to replace `except Exception: pass` in producer wrappers so the
    failure mode surfaces in run logs without spamming.
    """
    key = (component_name, type(exc).__name__)
    if key in _SEEN_FAILURES:
        return
    _SEEN_FAILURES.add(key)
    logger.warning(
        "silent-failure (first occurrence; subsequent suppressed): "
        "component=%s exception=%s: %s",
        component_name, type(exc).__name__, exc,
    )


def log_silent_empty(component_name: str) -> None:
    """Log the FIRST empty-return from `component_name` in this process,
    then suppress. Used when a producer returns {} or None silently
    without raising — also a silent failure mode the engine can not see.
    """
    if component_name in _SEEN_EMPTIES:
        return
    _SEEN_EMPTIES.add(component_name)
    logger.warning(
        "silent-empty-return (first occurrence; subsequent suppressed): "
        "component=%s returned empty/falsy",
        component_name,
    )


def reset_for_tests() -> None:
    """Test-only helper: clear the seen-sets so a unit test can assert
    the first-occurrence behaviour deterministically."""
    _SEEN_FAILURES.clear()
    _SEEN_EMPTIES.clear()
