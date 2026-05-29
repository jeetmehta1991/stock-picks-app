"""Batch 458 (2026-05-29) -- AU2 silent-exception sweep tests.

PROBLEM (pre-Batch-458):
  51 silent `except: pass` / `except: continue` blocks were sprinkled across
  the critical engine + signal + results pipeline. The Batch 416 pattern
  (private to screener.py) addressed only the screener producer-call layer.
  Other files (smc_ict.py + exit_strategies.py vectorized-import) still
  swallowed exceptions silently, which masked queue item #3
  (PRODUCER_LAYER_ZERO_LIKELY for the 6 SMC strategies).

FIX:
  - New `backtest/util/silent_failure_logger.py` exposes
    `log_silent_failure(component, exc)` and `log_silent_empty(component)`
    -- rate-limited to one log line per (component, exception-type) per
    process.
  - smc_ict.py: 8 silent excepts -> 8 `log_silent_failure(...)` calls
    (covers FVG / OB / BOS-CHoCH / liquidity / retracement / dealing-range
    compute paths + the smartmoneyconcepts library import).
  - screener.py: 13 producer wrappers (pead, insider_buying,
    institutional_persistence, macro_events, chart_patterns,
    index_rebalance, pairs_trading, news_sentiment, calendar_effects,
    cross_asset, volume_profile, multi_timeframe,
    cross_sectional_features) gain logging via the EXISTING Batch 416
    `_log_silent_producer_failure` private helper.
  - exit_strategies.py: 1 vectorized-import fallback gains logging.

  Total: 22 of 51 silent excepts converted to one-shot-logged. The other
  29 are category-(a) defensive justified (date/datetime arithmetic
  fallbacks, dependency-import alt-library cascades) and remain
  intentionally silent per CHECKLIST #100.

THIS TEST asserts:
  1. The shared helper logs exactly ONCE per (component, exception-type)
     pair across many invocations.
  2. log_silent_empty likewise dedupes per component name.
  3. reset_for_tests() restores fresh state between tests.
  4. Two distinct exception types from the same component log SEPARATELY.
  5. Two distinct components with the same exception type log SEPARATELY.
  6. smc_ict.py compute path actually invokes the logger when the
     library raises (semantic-integration, not greppable-string check).

CHECKLIST coverage:
  #69 test pyramid (unit + semantic-integration tier)
  #100 every queue item ships tests + wired + activated
"""
from __future__ import annotations

import logging

import pandas as pd
import pytest

from backtest.util.silent_failure_logger import (
    log_silent_failure,
    log_silent_empty,
    reset_for_tests,
)


@pytest.fixture(autouse=True)
def _reset_seen_sets():
    reset_for_tests()
    yield
    reset_for_tests()


def test_log_silent_failure_first_occurrence_then_suppressed(caplog):
    caplog.set_level(logging.WARNING,
                      logger="backtest.util.silent_failure_logger")
    exc = ValueError("synthetic")
    log_silent_failure("test_component_a", exc)
    log_silent_failure("test_component_a", exc)
    log_silent_failure("test_component_a", exc)
    relevant = [
        r for r in caplog.records
        if "test_component_a" in r.getMessage()
    ]
    assert len(relevant) == 1, \
        f"Expected exactly 1 log line; got {len(relevant)}: {[r.getMessage() for r in relevant]}"


def test_log_silent_empty_first_occurrence_then_suppressed(caplog):
    caplog.set_level(logging.WARNING,
                      logger="backtest.util.silent_failure_logger")
    log_silent_empty("test_component_b")
    log_silent_empty("test_component_b")
    log_silent_empty("test_component_b")
    relevant = [
        r for r in caplog.records
        if "test_component_b" in r.getMessage()
    ]
    assert len(relevant) == 1


def test_two_distinct_exception_types_log_separately(caplog):
    caplog.set_level(logging.WARNING,
                      logger="backtest.util.silent_failure_logger")
    log_silent_failure("comp_c", ValueError("first"))
    log_silent_failure("comp_c", TypeError("second"))
    relevant = [
        r for r in caplog.records
        if "comp_c" in r.getMessage()
    ]
    assert len(relevant) == 2


def test_two_distinct_components_same_exc_log_separately(caplog):
    caplog.set_level(logging.WARNING,
                      logger="backtest.util.silent_failure_logger")
    log_silent_failure("comp_d", ValueError("x"))
    log_silent_failure("comp_e", ValueError("x"))
    relevant = [
        r for r in caplog.records
        if r.getMessage().startswith("silent-failure")
        and ("comp_d" in r.getMessage() or "comp_e" in r.getMessage())
    ]
    assert len(relevant) == 2


def test_reset_for_tests_clears_dedup_state(caplog):
    caplog.set_level(logging.WARNING,
                      logger="backtest.util.silent_failure_logger")
    log_silent_failure("comp_f", ValueError("first"))
    log_silent_failure("comp_f", ValueError("first-again"))
    pre_reset_count = sum(
        1 for r in caplog.records if "comp_f" in r.getMessage()
    )
    assert pre_reset_count == 1
    reset_for_tests()
    log_silent_failure("comp_f", ValueError("post-reset"))
    post_reset_count = sum(
        1 for r in caplog.records if "comp_f" in r.getMessage()
    )
    assert post_reset_count == 2, "reset_for_tests must allow re-logging"


# ---------------------------------------------------------------------
# Semantic-integration: smc_ict.py actually wires the logger
# ---------------------------------------------------------------------
def test_smc_ict_compute_path_invokes_logger_on_library_failure(caplog,
                                                                  monkeypatch):
    """Monkey-patch `_smc.fvg` to raise -- the Batch 458 wiring should
    convert that raise into a one-shot log line via the shared helper.
    Asserts the call path is exercised end-to-end, not just greppable."""
    caplog.set_level(logging.WARNING,
                      logger="backtest.util.silent_failure_logger")
    import backtest.signals.smc_ict as smc_module

    if not getattr(smc_module, "_SMC_AVAILABLE", False):
        pytest.skip("smartmoneyconcepts library unavailable in this env")

    # Valid-shape OHLC with sufficient history so the early-return guards
    # let the function enter the wrapped try block.
    import numpy as np
    n = 250
    rng = np.random.RandomState(0)
    base = 100 + np.cumsum(rng.normal(0.0, 1.0, n))
    ohlc = pd.DataFrame({
        "open":  base,
        "high":  base + 0.5,
        "low":   base - 0.5,
        "close": base + rng.normal(0.0, 0.2, n),
    })

    # Replace the library's fvg call with one that raises -- this exercises
    # the `except Exception as _e: log_silent_failure("smc_ict.fvg_compute", _e)`
    # wiring directly.
    class _BrokenSMC:
        def fvg(self, *args, **kwargs):
            raise RuntimeError("synthetic fvg failure")
        def swing_highs_lows(self, *args, **kwargs):
            raise RuntimeError("synthetic swings failure")
        def ob(self, *args, **kwargs):
            raise RuntimeError("synthetic ob failure")
        def bos_choch(self, *args, **kwargs):
            raise RuntimeError("synthetic bos_choch failure")
        def liquidity(self, *args, **kwargs):
            raise RuntimeError("synthetic liquidity failure")
        def retracements(self, *args, **kwargs):
            raise RuntimeError("synthetic retracements failure")

    monkeypatch.setattr(smc_module, "_smc", _BrokenSMC())
    smc_module.compute_smc_signals(ohlc)

    smc_records = [
        r for r in caplog.records
        if r.getMessage().startswith("silent-failure")
        and "smc_ict" in r.getMessage()
    ]
    assert len(smc_records) >= 1, \
        f"Expected at least one smc_ict.* silent-failure log; got {smc_records}"


def test_smc_ict_import_path_succeeds_or_logs():
    """The smc_ict.py module-level import either succeeds (library present)
    OR it logged the import failure via the shared helper. Greppable string
    'log_silent_failure' must appear in the module source so the wiring is
    not removable without test regression."""
    from pathlib import Path
    src = Path("backtest/signals/smc_ict.py").read_text(encoding="utf-8")
    assert "log_silent_failure" in src, \
        "smc_ict.py must call log_silent_failure (Batch 458 AU2 wiring)"
    # Count the call sites: import + 7 compute blocks = 8 total
    n = src.count("log_silent_failure(")
    assert n >= 8, f"Expected >=8 log_silent_failure call sites in smc_ict.py, got {n}"


def test_exit_strategies_vectorized_import_logger_wired():
    """Batch 458 wired the vectorized-import fallback to the shared logger."""
    from pathlib import Path
    src = Path("backtest/engine/exit_strategies.py").read_text(encoding="utf-8")
    assert "log_silent_failure" in src
    assert "exit_strategies_vectorized.import" in src


def test_screener_producer_wrappers_logger_call_sites():
    """Batch 458 added _log_silent_producer_failure calls to 13 new screener
    producer wrappers (on top of the 3 Batch 416 sites). Verify total
    call-site count meets minimum."""
    from pathlib import Path
    src = Path("backtest/signals/screener.py").read_text(encoding="utf-8")
    # Batch 416 added a few; Batch 458 adds 12 more (chart, calendar,
    # cross_asset, volume_profile, multi_timeframe, news_sentiment,
    # pairs_trading, pead, insider_buying, persistence, macro_events,
    # index_rebalance, cross_sectional_features). The total call-site
    # count should be >=15.
    n = src.count("_log_silent_producer_failure(")
    assert n >= 15, f"Expected >=15 _log_silent_producer_failure calls, got {n}"
