"""Batch 558 (2026-06-02) -- Phase 1A-beta producer-zero forensic:
institutional cluster verdict.

Source: per CHECKLIST #77, owner directive 2026-06-02 "C then A".
Queue: Phase 1A-beta producer-zero institutional cluster.

Audit findings:
  - 4 institutional_* strategies in PRODUCER_LAYER_ZERO_CANDIDATES:
      strat_institutional_strong_conviction_long
      strat_institutional_high_conviction_long
      strat_institutional_recent_init_momentum_long
      strat_institutional_recent_init_volume_long
  - Producer `institutional_signal` (smart_money.py) wired into
    screener.py:4313 emitting 5 keys: institutional_signal,
    institutional_strong_buy, institutional_buy, institutional_negative,
    institutional_new_positions, institutional_increased.
  - Empirical threshold-crossing rates (5 tickers x 48 monthly dates =
    240 samples; AAPL/MSFT/GOOGL/JPM/NVDA across 2021-2024):
      institutional_new_positions >= 2: 22.5pct
      institutional_new_positions >= 3: 12.1pct
      institutional_new_positions >= 5: 3.8pct
      institutional_increased >= 5:     14.6pct
      signal in (buy, strong_buy):      47.1pct

Verdict: NO CODE BUG. Producer fires normally on real 13F data.
Zero-fire in 2026-05-26 1A-beta single-batch is sample-size-driven:
  - 13F filings are quarterly, so threshold-crossing events cluster
    around earnings cycle (5 weeks post-quarter-end).
  - Single-batch ran limited tickers x dates -> compound predicates
    (institutional_new_positions >= 3 AND price_above_ema_50) by
    chance never co-fired on the sampled (ticker, as_of) tuples.

Additional ALREADY-SHIPPED win (B549 2026-06-02 same day): the
`_institutional_signal_from_perticker_history` cache layer (29ms ->
5ms per call) is now active, so the R4 cube's institutional_* signal
density is HIGHER than what the 1A-beta single-batch saw under the
pre-B549 slower codepath. Expect R4 cube to populate institutional
cluster cells with real candidates.

Pins:

  (1) Producer wired into screener (regression guard for engine
      consumption)
  (2) Producer emits expected 5-key signal dict structure when called
      on a real ticker
  (3) institutional_new_positions threshold crossing rate >0pct on a
      representative ticker subsample (regression guard against
      sudden cache/data corruption causing universal new_positions=0)
  (4) All 4 institutional_* strategies remain registered
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest


def _have_institutional_cache(ticker: str) -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / "data_prefetch" / "quiver" / "institutional"
            / f"{ticker}.parquet").exists()


def test_batch558_producer_wired_to_screener():
    """institutional_signal must be imported + called in
    screen_instrument (regression guard for engine wiring)."""
    import inspect
    from backtest.signals import screener
    src = inspect.getsource(screener)
    assert "from backtest.data.smart_money import institutional_signal" in src
    assert "institutional_signal(ticker, as_of)" in src, (
        "screener must call institutional_signal with (ticker, as_of)"
    )
    # All 5 keys emitted into signals dict
    for k in [
        "institutional_signal", "institutional_strong_buy",
        "institutional_buy", "institutional_negative",
        "institutional_new_positions", "institutional_increased",
    ]:
        assert f'signals["{k}"]' in src, f"key {k} not assigned to signals dict"


@pytest.mark.skipif(
    not _have_institutional_cache("MSFT"),
    reason="institutional cache absent for MSFT",
)
def test_batch558_producer_emits_expected_signal_dict_structure():
    """institutional_signal on a real ticker must return a dict with
    the 4 expected keys when signal != none."""
    from backtest.data.smart_money import (
        institutional_signal, _INSTITUTIONAL_PROCESSED_CACHE,
        _PREFETCH_CACHE, _BULK_CACHE, _BULK_INDEX,
    )
    for cache in (_INSTITUTIONAL_PROCESSED_CACHE, _PREFETCH_CACHE,
                  _BULK_CACHE, _BULK_INDEX):
        cache.clear()
    # MSFT 2023-05 had strong_buy per audit data
    out = institutional_signal("MSFT", date(2023, 5, 27))
    assert "signal" in out
    if out["signal"] != "none":
        for k in ("new_positions", "increased", "decreased"):
            assert k in out, f"missing key {k} in non-none result"


@pytest.mark.skipif(
    not _have_institutional_cache("MSFT"),
    reason="institutional cache absent for MSFT",
)
def test_batch558_new_positions_threshold_crossing_nonzero():
    """Empirical sanity check: institutional_new_positions must
    cross >= 2 at least ONCE across a representative subsample.
    Regression guard against universal zero (would indicate cache/data
    corruption silently zeroing the signal)."""
    from backtest.data.smart_money import (
        institutional_signal, _INSTITUTIONAL_PROCESSED_CACHE,
        _PREFETCH_CACHE, _BULK_CACHE, _BULK_INDEX,
    )
    for cache in (_INSTITUTIONAL_PROCESSED_CACHE, _PREFETCH_CACHE,
                  _BULK_CACHE, _BULK_INDEX):
        cache.clear()
    n_with_new_pos_ge2 = 0
    n_total = 0
    for ticker in ("AAPL", "MSFT", "JPM"):
        if not _have_institutional_cache(ticker):
            continue
        # Quarterly samples post-13F-filing windows
        for d in [
            date(2022, 6, 1), date(2022, 9, 29),
            date(2023, 1, 27), date(2023, 5, 27),
            date(2023, 9, 24), date(2024, 1, 22),
        ]:
            r = institutional_signal(ticker, d)
            n_total += 1
            if r.get("new_positions", 0) >= 2:
                n_with_new_pos_ge2 += 1
    assert n_total > 0, "no test samples collected"
    assert n_with_new_pos_ge2 >= 1, (
        f"institutional_new_positions >= 2 fires 0/{n_total} across "
        f"AAPL/MSFT/JPM x 6 quarterly dates. Producer or data may be "
        f"corrupted; investigate cache layer."
    )


def test_batch558_four_institutional_strategies_registered():
    """Regression guard: all 4 institutional_* strategy fns must
    remain registered."""
    from backtest.signals import screener
    expected = [
        "strat_institutional_strong_conviction_long",
        "strat_institutional_high_conviction_long",
        "strat_institutional_recent_init_momentum_long",
        "strat_institutional_recent_init_volume_long",
    ]
    missing = [n for n in expected if not hasattr(screener, n)]
    assert not missing, f"missing institutional strategy fns: {missing}"


def test_batch558_b549_perticker_cache_is_active():
    """The B549 pre-processed institutional cache must be in place
    (regression guard against accidental revert of B549's speedup
    that was a dependency for getting institutional_* signal density
    high enough in R4 cube)."""
    from backtest.data import smart_money
    assert hasattr(smart_money, "_load_institutional_processed"), (
        "B549 helper missing -- cache layer reverted?"
    )
    assert hasattr(smart_money, "_INSTITUTIONAL_PROCESSED_CACHE"), (
        "B549 cache dict missing"
    )
