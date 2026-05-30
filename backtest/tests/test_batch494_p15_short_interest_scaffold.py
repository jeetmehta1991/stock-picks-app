"""Batch 494 (2026-05-30) -- P15 FINRA short-interest producer scaffold.

Source: per CHECKLIST #77 (test extensively).
Queue row: EXECUTION_QUEUE.md item P15.
Producer module: backtest/signals/short_interest.py.

Two-part test suite:

  (1) Data-gap pin: confirm data_prefetch/finra/ does NOT exist today,
      so the queue row's BLOCKED-NOT-PREFETCHED status is empirically
      grounded. When the fetcher script runs and the cache lands, this
      test surfaces the change explicitly.

  (2) Producer math + shape: validate compute_short_interest_signals
      via mock DataFrame injection. The producer is wired and ready
      to consume data the moment the fetcher lands.

When the prefetch ships, the only follow-on work is:
  - run the fetcher
  - flip the data-gap test to assert presence
  - register the new sleeve strategies in ALL_STRATEGIES
  - wire compute_short_interest_signals into the screener call path

No production code changes outside the new module.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
FINRA_DIR = REPO / "data_prefetch" / "finra"


# ---------------------------------------------------------------------------
# Data-gap pin (BLOCKED-NOT-PREFETCHED state)
# ---------------------------------------------------------------------------

def test_batch494_p15_finra_cache_not_present_today():
    """As of 2026-05-30 no FINRA prefetch has run. Pin the empirical
    state so the queue row reflects reality.

    When the prefetch runs and this directory appears, this assertion
    flips, surfacing the change in CI.
    """
    assert not FINRA_DIR.exists(), (
        f"FINRA cache directory {FINRA_DIR} now exists -- the prefetch "
        f"ran. Update queue row P15 to PARTIAL-RESOLVED + flip this "
        f"assertion to existence."
    )


def test_batch494_p15_producer_module_importable():
    """Even with no data, the module must import without raising
    (graceful empty pattern per L86)."""
    from backtest.signals.short_interest import (
        compute_short_interest_signals,
        EXPECTED_COLS,
    )
    assert callable(compute_short_interest_signals)
    assert set(EXPECTED_COLS) == {
        "settlement_date", "short_interest",
        "shares_outstanding", "avg_daily_volume",
    }


def test_batch494_p15_producer_returns_empty_on_missing_cache():
    """Cache miss -> {} (NOT raise). Strategies degrade quietly."""
    from backtest.signals.short_interest import compute_short_interest_signals
    out = compute_short_interest_signals("AAPL", date(2024, 1, 15))
    assert out == {}, (
        "Producer must return empty dict on cache miss, not raise"
    )


# ---------------------------------------------------------------------------
# Producer math via mock-DataFrame injection
# ---------------------------------------------------------------------------

def _mock_si_df(rows):
    """Build a producer-compatible DataFrame from row tuples
    (settlement_date, short_interest, shares_outstanding, avg_daily_volume).
    """
    return pd.DataFrame(rows, columns=[
        "settlement_date", "short_interest",
        "shares_outstanding", "avg_daily_volume",
    ])


def test_batch494_p15_producer_computes_short_interest_pct():
    """SI = 30M, SO = 100M -> short_interest_pct = 0.30."""
    from backtest.signals.short_interest import compute_short_interest_signals
    df = _mock_si_df([
        (date(2024, 1, 15), 30_000_000.0, 100_000_000.0, 2_000_000.0),
    ])
    out = compute_short_interest_signals("ZZZZ", date(2024, 1, 20), df=df)
    assert out["short_interest_pct"] == pytest.approx(0.30, abs=1e-6)


def test_batch494_p15_producer_computes_days_to_cover():
    """SI = 30M, ADV = 2M -> days_to_cover = 15."""
    from backtest.signals.short_interest import compute_short_interest_signals
    df = _mock_si_df([
        (date(2024, 1, 15), 30_000_000.0, 100_000_000.0, 2_000_000.0),
    ])
    out = compute_short_interest_signals("ZZZZ", date(2024, 1, 20), df=df)
    assert out["days_to_cover"] == pytest.approx(15.0, abs=1e-4)


def test_batch494_p15_producer_uses_pit_filter():
    """Only snapshots with settlement_date <= as_of count; latest of
    those is the 'current' snapshot."""
    from backtest.signals.short_interest import compute_short_interest_signals
    df = _mock_si_df([
        (date(2024, 1, 1),  10_000_000.0, 100_000_000.0, 1_000_000.0),
        (date(2024, 1, 15), 30_000_000.0, 100_000_000.0, 2_000_000.0),
        (date(2024, 2, 1),  50_000_000.0, 100_000_000.0, 1_500_000.0),  # future
    ])
    # as_of = Jan 20 -> Feb 1 row is in the future + filtered out
    out = compute_short_interest_signals("ZZZZ", date(2024, 1, 20), df=df)
    assert out["short_interest_pct"] == pytest.approx(0.30, abs=1e-6)
    assert out["short_interest_observations"] == 2


def test_batch494_p15_producer_handles_no_shares_outstanding_gracefully():
    """SO = 0 -> omit short_interest_pct, still emit days_to_cover."""
    from backtest.signals.short_interest import compute_short_interest_signals
    df = _mock_si_df([
        (date(2024, 1, 15), 30_000_000.0, 0.0, 2_000_000.0),
    ])
    out = compute_short_interest_signals("ZZZZ", date(2024, 1, 20), df=df)
    assert "short_interest_pct" not in out
    assert out["days_to_cover"] == pytest.approx(15.0, abs=1e-4)


def test_batch494_p15_producer_handles_no_adv_gracefully():
    """ADV = 0 -> omit days_to_cover, still emit short_interest_pct."""
    from backtest.signals.short_interest import compute_short_interest_signals
    df = _mock_si_df([
        (date(2024, 1, 15), 30_000_000.0, 100_000_000.0, 0.0),
    ])
    out = compute_short_interest_signals("ZZZZ", date(2024, 1, 20), df=df)
    assert out["short_interest_pct"] == pytest.approx(0.30, abs=1e-6)
    assert "days_to_cover" not in out


def test_batch494_p15_producer_empty_past_returns_empty():
    """All observations after as_of -> {}."""
    from backtest.signals.short_interest import compute_short_interest_signals
    df = _mock_si_df([
        (date(2024, 2, 1), 30_000_000.0, 100_000_000.0, 2_000_000.0),
    ])
    out = compute_short_interest_signals("ZZZZ", date(2024, 1, 20), df=df)
    assert out == {}


def test_batch494_p15_producer_carries_observation_count_and_date():
    """Diagnostic fields land for downstream coverage reporting."""
    from backtest.signals.short_interest import compute_short_interest_signals
    df = _mock_si_df([
        (date(2024, 1, 1),  10_000_000.0, 100_000_000.0, 1_000_000.0),
        (date(2024, 1, 15), 20_000_000.0, 100_000_000.0, 1_500_000.0),
        (date(2024, 1, 31), 30_000_000.0, 100_000_000.0, 2_000_000.0),
    ])
    out = compute_short_interest_signals("ZZZZ", date(2024, 2, 5), df=df)
    assert out["short_interest_observations"] == 3
    assert out["short_interest_settlement_date"] == date(2024, 1, 31)


# ---------------------------------------------------------------------------
# Strategy-level pin (sleeve strategies NOT yet in ALL_STRATEGIES)
# ---------------------------------------------------------------------------

def test_batch494_p15_sleeve_strategies_not_yet_registered():
    """Pin: the new sleeve names land in ALL_STRATEGIES only after the
    prefetch runs + the wiring batch fires. If they appear today (no
    data) the cube would compute zero-trade cells across them.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    sleeve_names = {"squeeze_setup_long", "short_borrow_trap_avoid"}
    in_registry = sleeve_names.intersection(set(ALL_STRATEGIES.keys()))
    assert not in_registry, (
        f"Sleeve strategies {in_registry} registered before prefetch -- "
        f"cube would compute degenerate cells. Run prefetch first, then "
        f"register."
    )
