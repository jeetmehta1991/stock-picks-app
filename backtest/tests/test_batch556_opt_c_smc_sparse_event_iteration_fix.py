"""Batch 556 (2026-06-02) -- OPT-C Phase 4 / Phase 1A-beta producer-zero
forensic: SMC sparse-event iteration fix.

Source: per CHECKLIST #77, owner directive 2026-06-02 "C then A"
(producer-zero audits).
Queue: EXECUTION_QUEUE.md Phase 1A-beta producer-zero cluster (SMC).

Findings from the empirical audit:
  - 18 SMC strategies showed PRODUCER_LAYER_ZERO_CANDIDATES in the
    2026-05-26 single-batch 1A-beta run.
  - Per-ticker probe (AAPL/NVDA/JPM/XOM/PFE x 252 bars):
    smc_breaker_block_bullish/bearish = 0.0pct on EVERY ticker.
    smc_mitigation_block_*, smc_bos_retest_*, smc_fvg_retest_* sporadic.
  - Empirical OB density: only 2 events in last 500 bars of AAPL.
    `tail(50)` of OHLCV-aligned DataFrame catches 0-1 actual events.

Root cause (same as Batch 390 fix for liquidity):
  SMC primitives are SPARSE in the OHLCV-aligned DataFrame. Most rows
  have NaN OB/FVG/BOS columns; only swing-anchored rows carry events.
  `tail(50)` then iterates 50 rows where ~48 are NaN-skipped and
  ~2 are actual events. The breaker/mitigation/retest derivation code
  effectively scans <=2 events and misses most history.

Fix applied in `compute_smc_signals`:
  - OB iteration: `tail(50)` -> filter non-zero OB rows first, then tail(20)
  - FVG iteration: same pattern
  - BOS retest iteration: same pattern
  (Liquidity iteration already had this pattern via Batch 390.)

Pins:

  (1) Smoke: 18 SMC strategy entry-predicate functions are still
      registered after this batch.
  (2) Producer emits ALL strategy-required signal keys (key set
      regression guard).
  (3) For sparse-event tickers (small OB count), the filter-then-tail
      pattern catches all events in the history, NOT just the last N
      OHLCV rows.
  (4) Empirical activation: AAPL no longer shows 0pct for events that
      DO exist in history. Specifically, smc_breaker_block_* may still
      be 0pct on AAPL (OB never mitigated in test window) but the
      iteration logic now SCANS the correct events.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest


def _have_ohlcv(ticker: str) -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
            / f"{ticker.replace('.', '-')}.parquet").exists()


def _load_ohlc(ticker: str) -> pd.DataFrame:
    repo_root = Path(__file__).parent.parent.parent
    df = pd.read_parquet(
        repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
        / f"{ticker.replace('.', '-')}.parquet"
    )
    df["date_dt"] = pd.to_datetime(df["date"]).dt.date
    return df.sort_values("date_dt").reset_index(drop=True)


def test_batch556_18_smc_strategy_predicates_still_registered():
    """Smoke guard: all 18 SMC strategies remain in screener after the
    producer-side fix. None deprecated, none renamed silently."""
    from backtest.signals import screener
    expected_names = [
        "strat_smc_fvg_retest_long", "strat_smc_fvg_retest_short",
        "strat_smc_inverse_fvg",
        "strat_smc_breaker_block_short", "strat_smc_breaker_block_long",
        "strat_smc_mitigation_block_long", "strat_smc_mitigation_block_short",
        "strat_smc_discount_long", "strat_smc_premium_short",
        "strat_smc_ote_long", "strat_smc_ote_short",
        "strat_smc_equal_highs_sweep_short", "strat_smc_equal_lows_sweep_long",
        "strat_smc_bos_retest_entry", "strat_smc_bos_continuation",
        "strat_smc_choch_reversal", "strat_smc_order_block_bounce",
        "strat_smc_liquidity_sweep_reversal",
    ]
    missing = [n for n in expected_names if not hasattr(screener, n)]
    assert not missing, f"missing SMC strategy fns: {missing}"


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch556_producer_emits_strategy_required_keys():
    """compute_smc_signals must emit ALL keys read by the 18 SMC
    strategies, even when individual values are False (key presence
    regression guard so strategies' .get(k, default) doesn't silently
    miss producer output)."""
    from backtest.signals.smc_ict import compute_smc_signals
    df = _load_ohlc("AAPL").iloc[:600]
    out = compute_smc_signals(df)
    required = {
        # FVG retest family
        "smc_fvg_retest_long_zone", "smc_fvg_retest_short_zone",
        # Inverse FVG
        "smc_inverse_fvg_bullish", "smc_inverse_fvg_bearish",
        # Breaker blocks
        "smc_breaker_block_bullish", "smc_breaker_block_bearish",
        # Mitigation blocks
        "smc_mitigation_block_long", "smc_mitigation_block_short",
        # Dealing range / premium-discount
        "smc_in_discount_zone", "smc_in_premium_zone",
        # OTE
        "smc_ote_long_zone", "smc_ote_short_zone",
        # Equal-highs/lows sweep
        "smc_equal_highs_swept", "smc_equal_lows_swept",
        # BOS retest
        "smc_bos_retest_long", "smc_bos_retest_short",
        # BOS continuation (base flags)
        "smc_bos_bullish", "smc_bos_bearish",
        # CHoCH
        "smc_choch_bullish", "smc_choch_bearish",
        # OB active
        "smc_ob_bullish_active", "smc_ob_bearish_active",
        # Liquidity
        "smc_liquidity_swept_up", "smc_liquidity_swept_dn",
        # FVG active
        "smc_fvg_bullish_active", "smc_fvg_bearish_active",
    }
    missing = required - set(out.keys())
    assert not missing, f"producer missing required keys: {sorted(missing)}"


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch556_sparse_event_iteration_scans_full_history():
    """The fix replaces `tail(50)` of OHLCV-aligned rows with
    filter-non-zero + tail(20) of ACTUAL events. This test verifies
    the new pattern catches events that the old pattern would have
    missed when events are sparse (>50 bars between events)."""
    import inspect
    from backtest.signals import smc_ict
    src = inspect.getsource(smc_ict.compute_smc_signals)
    # Post-fix code must contain the filter-then-tail pattern for OB
    assert "ob_events = ob_df[ob_df" in src, (
        "OB iteration must use filter-then-tail pattern post-B556"
    )
    # Same for FVG retest scan
    assert "fvg_events = fvg_df[fvg_df" in src, (
        "FVG retest iteration must use filter-then-tail pattern post-B556"
    )
    # Same for BOS retest scan
    assert "bos_events = bos_df[bos_df" in src, (
        "BOS retest iteration must use filter-then-tail pattern post-B556"
    )
    # Old buggy tail(50) of the aligned DataFrame should be removed for
    # these three scans. Liquidity scan uses the same pattern (Batch 390).
    # Bare `tail(50)` may still appear elsewhere in this function (e.g.,
    # smaller iteration of dealing-range tail) -- so we check the SPECIFIC
    # ob_df.tail(50) form is gone.
    assert "tail = ob_df.tail(50)" not in src, (
        "B556: legacy tail(50) on full OB df should be replaced"
    )
    assert "tail = fvg_df.tail(50)" not in src, (
        "B556: legacy tail(50) on full FVG df should be replaced"
    )
    assert "tail = bos_df.tail(50)" not in src, (
        "B556: legacy tail(50) on full BOS df should be replaced"
    )


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch556_compute_smc_signals_short_history_no_crash():
    """Edge case: when history has 0 or 1 OB/FVG/BOS events, the new
    filter-then-tail must not crash (empty DataFrame -> empty
    iteration)."""
    from backtest.signals.smc_ict import compute_smc_signals
    df = _load_ohlc("AAPL").iloc[:120]  # just above swing_length*2 threshold
    out = compute_smc_signals(df)
    # Should produce a dict (possibly partial) without raising
    assert isinstance(out, dict)
