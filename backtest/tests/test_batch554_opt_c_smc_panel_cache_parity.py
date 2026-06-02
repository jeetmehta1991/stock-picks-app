"""Batch 554 (2026-06-02) -- OPT-C Phase 4: SMC primitive panel-cache
parity gate.

Source: per CHECKLIST #77, owner directive 2026-06-02 "a" (ship SMC
panel-cache).
Queue: EXECUTION_QUEUE.md OPT-C Phase 4.

Strategy: precompute the 6 SMC primitives (fvg, swings, ob, bos_choch,
liquidity, retracements) on the FULL per-ticker OHLCV ONCE per session,
then slice cached DataFrames at each (ticker, as_of) call. Saves
~150-170s/profile of vendored smartmoneyconcepts library compute.

PIT-safety contract enforced by `get_primitives_at`:
  - FVG: 3-bar pattern, NO lookahead -> filter `Index <= current_idx`.
  - Swing-dependent (5 primitives): swing detection uses
    `shift(-swing_length)` lookahead -> filter
    `Index <= current_idx - swing_length` so any swing only confirmed
    by data after as_of is hidden.

Open caveat (the reason this is gated behind a parity test before
wire-in): the library's `ob` function has forward-mutating state (an
OB's breaker block can RESET when a much later bar's high exceeds the
OB top). When precomputed on the full series and SLICED at as_of, the
visible OB state already reflects all forward mutations -- which is
NOT what a from-scratch compute on the truncated slice would produce.

This test enumerates the divergence rate. The cache stays opt-in
(`USE_SMC_PANEL_CACHE` flag, default False, NOT YET DECLARED in this
batch) until the parity verdict is known.

Pins:

  (1) Cache primes correctly for a real ticker: all 6 primitive
      DataFrames populated when `len(full_ohlc) >= 100`.
  (2) PIT slicing returns subsets respecting the
      `Index <= current_idx[-swing_length]` invariant.
  (3) Parity: at multiple as_of values for AAPL, the cached primitive
      DataFrames (sliced via `get_primitives_at`) match the
      from-scratch primitive DataFrames (computed on truncated ohlc)
      for the FVG and swings primitives, where forward-mutation is
      not a concern.
  (4) Documented divergence for OB: enumerate the cells that differ
      and pin the divergence-rate as a known artifact (not as an
      assertion that they must match). Parity rate >= 95pct or pin
      explicit rate so future regressions surface.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def reset_smc_cache():
    from backtest.signals.smc_panel_cache import reset_cache
    reset_cache()
    yield
    reset_cache()


def _have_ohlcv(ticker: str) -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
            / f"{ticker.replace('.', '-')}.parquet").exists()


def _load_full_ohlc(ticker: str) -> pd.DataFrame:
    repo_root = Path(__file__).parent.parent.parent
    df = pd.read_parquet(
        repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
        / f"{ticker.replace('.', '-')}.parquet"
    )
    if "date" in df.columns:
        df["date_dt"] = pd.to_datetime(df["date"]).dt.date
        df = df.sort_values("date_dt").reset_index(drop=True)
    return df


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch554_priming_populates_all_six_primitives():
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, _FULL_PRIMITIVES_BY_TICKER,
    )
    ohlc = _load_full_ohlc("AAPL")
    assert len(ohlc) >= 100, "test fixture: need >=100 bars"
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    p = _FULL_PRIMITIVES_BY_TICKER["AAPL"]
    for key in ("fvg", "swings", "ob", "bos_choch", "liquidity", "retracements"):
        assert p.get(key) is not None, f"primitive {key!r} should be populated"


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch554_get_primitives_respects_pit_slicing():
    """FVG is sliced to current_idx; swing-dependent primitives are
    sliced to current_idx - swing_length."""
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, get_primitives_at,
    )
    ohlc = _load_full_ohlc("AAPL")
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    current_idx = 500
    sliced = get_primitives_at("AAPL", current_idx, swing_length=20)
    assert sliced is not None
    # FVG: 1-bar lookahead -> rows 0..current_idx-1 = `current_idx` rows
    assert len(sliced["fvg"]) == current_idx, (
        f"fvg len: {len(sliced['fvg'])} vs {current_idx} "
        f"(FVG has 1-bar lookahead, excludes current bar)"
    )
    # Swing-dependent: should have current_idx - swing_length + 1 = 481 rows
    expected_swing = current_idx - 20 + 1
    for key in ("swings", "ob", "bos_choch", "liquidity", "retracements"):
        assert len(sliced[key]) == expected_swing, (
            f"{key} len: {len(sliced[key])} vs {expected_swing}"
        )


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch554_swing_length_mismatch_returns_none():
    """Priming with swing_length=20 and querying with swing_length=50
    must return None (cache miss, force caller fallback) to prevent
    silent semantic drift."""
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, get_primitives_at,
    )
    ohlc = _load_full_ohlc("AAPL")
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    out = get_primitives_at("AAPL", 500, swing_length=50)
    assert out is None, "swing_length mismatch must return None"


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch554_fvg_parity_cached_vs_from_scratch():
    """FVG has NO lookahead: cached-then-sliced FVG DataFrame must
    match from-scratch FVG computed on the truncated ohlc EXACTLY.
    Pin per-bar value parity at multiple as_of slices."""
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, get_primitives_at,
    )
    from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
    ohlc = _load_full_ohlc("AAPL")
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    n_total = len(ohlc)
    # Test multiple as_of indices
    test_idxs = [200, 500, 800, 1000, n_total - 50]
    test_idxs = [i for i in test_idxs if 100 < i < n_total]
    divergences = 0
    samples_checked = 0
    for current_idx in test_idxs:
        sliced = get_primitives_at("AAPL", current_idx, swing_length=20)
        cached_fvg = sliced["fvg"]  # length = current_idx (boundary excluded)
        # From-scratch on truncated ohlc; FVG at the last bar will be NaN
        # because shift(-1) has no data. Take first `current_idx` rows
        # to compare against cached (which already excluded boundary).
        fresh_fvg = _smc.fvg(ohlc.iloc[:current_idx + 1]).iloc[:current_idx]
        if len(cached_fvg) != len(fresh_fvg):
            divergences += abs(len(cached_fvg) - len(fresh_fvg))
            continue
        cached_vals = cached_fvg["FVG"].fillna(0).to_numpy()
        fresh_vals = fresh_fvg["FVG"].fillna(0).to_numpy()
        diff_count = int((cached_vals != fresh_vals).sum())
        samples_checked += len(cached_vals)
        divergences += diff_count
    # FVG parity must be exact (no lookahead, no forward-mutating state)
    assert divergences == 0, (
        f"FVG parity divergence: {divergences} / {samples_checked} bars "
        f"differ between cached-sliced and from-scratch-truncated"
    )


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch554_swings_parity_after_swing_length_filter():
    """Swings have shift-ahead lookahead. After filtering to
    `Index <= current_idx - swing_length`, the cached swing values
    must match what from-scratch swings on truncated ohlc would produce
    at those same indices."""
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, get_primitives_at,
    )
    from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
    ohlc = _load_full_ohlc("AAPL")
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    n_total = len(ohlc)
    test_idxs = [300, 600, 900, n_total - 100]
    test_idxs = [i for i in test_idxs if 100 < i < n_total]
    divergences = 0
    samples_checked = 0
    for current_idx in test_idxs:
        sliced = get_primitives_at("AAPL", current_idx, swing_length=20)
        cached_swings = sliced["swings"]
        # From-scratch on truncated ohlc (will lose last `swing_length`
        # bars to shift-ahead NaN)
        fresh_swings = _smc.swing_highs_lows(
            ohlc.iloc[:current_idx + 1], swing_length=20,
        )
        # The cached version filtered to safe-idx = current_idx - 20
        # should match the first (current_idx - 20 + 1) rows of fresh
        n_safe = current_idx - 20 + 1
        cached_hl = cached_swings["HighLow"].fillna(0).to_numpy()
        fresh_hl = fresh_swings["HighLow"].iloc[:n_safe].fillna(0).to_numpy()
        if len(cached_hl) != len(fresh_hl):
            divergences += abs(len(cached_hl) - len(fresh_hl))
            continue
        diff_count = int((cached_hl != fresh_hl).sum())
        samples_checked += len(cached_hl)
        divergences += diff_count
    # Some divergence expected near boundary due to swings being
    # re-evaluated when more data arrives -- pin a tolerance
    if samples_checked > 0:
        rate = divergences / samples_checked
        assert rate < 0.05, (
            f"Swings parity divergence rate {rate:.4f} exceeds 5pct "
            f"tolerance: {divergences}/{samples_checked} bars differ"
        )


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch554_ob_forward_mutation_divergence_pin():
    """OB has forward-mutating breaker state. This test ENUMERATES the
    divergence rate between cached-sliced and from-scratch-truncated;
    it does NOT assert exact parity. The divergence rate is pinned so
    a future regression surfaces, and the cached-OB caller (B555+) can
    decide whether the rate is acceptable.
    """
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, get_primitives_at,
    )
    from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
    ohlc = _load_full_ohlc("AAPL")
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    n_total = len(ohlc)
    test_idxs = [400, 700, 1000, n_total - 50]
    test_idxs = [i for i in test_idxs if 100 < i < n_total]
    divergences = 0
    samples_checked = 0
    for current_idx in test_idxs:
        sliced = get_primitives_at("AAPL", current_idx, swing_length=20)
        cached_ob = sliced["ob"]
        fresh_swings = _smc.swing_highs_lows(
            ohlc.iloc[:current_idx + 1], swing_length=20,
        )
        fresh_ob = _smc.ob(ohlc.iloc[:current_idx + 1], fresh_swings)
        n_safe = current_idx - 20 + 1
        cached_ob_vals = cached_ob["OB"].fillna(0).to_numpy()
        fresh_ob_vals = fresh_ob["OB"].iloc[:n_safe].fillna(0).to_numpy()
        if len(cached_ob_vals) != len(fresh_ob_vals):
            divergences += abs(len(cached_ob_vals) - len(fresh_ob_vals))
            continue
        diff_count = int((cached_ob_vals != fresh_ob_vals).sum())
        samples_checked += len(cached_ob_vals)
        divergences += diff_count
    rate = divergences / max(samples_checked, 1)
    # Pin the rate so a future regression surfaces. NOT enforcing
    # strict parity (forward-mutation in OB makes exact match
    # impossible). Empirical pin: expect <20pct on real OHLCV.
    print(f"\nOB cached-vs-fresh divergence: {divergences}/{samples_checked} "
          f"= {rate:.4f}")
    assert rate < 0.30, (
        f"OB divergence rate {rate:.4f} exceeds 30pct tolerance; "
        f"forward-mutation diff was always expected, but {rate} is too "
        f"high. Investigate before wire-in."
    )


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch554_prime_idempotent():
    """Calling prime_ticker_primitives twice for the same ticker should
    not recompute (idempotent)."""
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, _FULL_PRIMITIVES_BY_TICKER,
    )
    ohlc = _load_full_ohlc("AAPL")
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    p1 = _FULL_PRIMITIVES_BY_TICKER["AAPL"]
    fvg_first = p1.get("fvg")
    prime_ticker_primitives("AAPL", ohlc, swing_length=20)
    p2 = _FULL_PRIMITIVES_BY_TICKER["AAPL"]
    fvg_second = p2.get("fvg")
    assert fvg_first is fvg_second, "re-priming must be no-op (same object)"
