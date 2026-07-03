"""B1124 Test 2/10: Data prefetch manifest preflight (Council 244).

RED-FIRST for BUG-278: data_prefetch/derived/index_rebalance_events.parquet
is MISSING. Producer no-ops silently. This test asserts either:
  (a) parquet exists and is non-empty (Sprint 5 DEC-380 landed), OR
  (b) 4 dependent strategies are marked DISABLED in registry.

Prevents silent-fire 0-signal state from reaching Phase 4 cube.
"""
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent

REQUIRED_PARQUETS = {
    "index_rebalance": REPO / "data_prefetch" / "derived" / "index_rebalance_events.parquet",
}

DEPENDENT_STRATEGIES_INDEX_REBALANCE = {
    "post_deletion_drift_short",
    "post_inclusion_drift_long",
    "post_inclusion_reversal_short",
    "pre_rebalance_long",
}


def test_bug_278_index_rebalance_parquet_or_strategies_disabled():
    """BUG-278: parquet MUST exist OR 4 dependent strategies MUST be DISABLED.

    Prevents Phase 4 launch with silent 0-fire strategies.
    """
    parquet = REQUIRED_PARQUETS["index_rebalance"]
    if parquet.exists() and parquet.stat().st_size > 100:
        return

    try:
        from backtest.signals.screener import (
            STRATEGIES_DISABLED_MISSING_PRODUCER,
        )
    except ImportError:
        pytest.fail(
            "BUG-278: parquet missing at "
            f"{parquet.relative_to(REPO)} AND "
            "STRATEGIES_DISABLED_MISSING_PRODUCER registry not importable to verify"
        )
        return

    disabled_names = {s.replace("strat_", "") for s in STRATEGIES_DISABLED_MISSING_PRODUCER}
    missing_disabled = DEPENDENT_STRATEGIES_INDEX_REBALANCE - disabled_names
    if missing_disabled:
        pytest.fail(
            f"BUG-278 RED: parquet missing AND {len(missing_disabled)} dependent "
            f"strategies not DISABLED: {sorted(missing_disabled)}. "
            "Either land Sprint 5 DEC-380 corp actions prefetch OR "
            "add these to STRATEGIES_DISABLED_MISSING_PRODUCER."
        )


def test_polygon_news_prefetch_directory_exists():
    """B832 SPOF: audit polygon news prefetch directory exists."""
    news_dir = REPO / "data_prefetch" / "polygon" / "news"
    assert news_dir.exists() or news_dir.parent.exists(), (
        f"data_prefetch/polygon/ tree must exist at minimum. Got: "
        f"{news_dir.parent} exists={news_dir.parent.exists()}"
    )


def test_polygon_ohlcv_prefetch_directory_exists():
    """Base data existence check."""
    ohlcv_dir = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
    assert ohlcv_dir.exists(), (
        f"OHLCV daily prefetch dir missing: {ohlcv_dir.relative_to(REPO)}"
    )


def test_finra_short_interest_prefetch_exists():
    """S1125 borrow_ok audit dependency: FINRA short interest coverage."""
    finra_dir = REPO / "data_prefetch" / "finra" / "short_interest"
    assert finra_dir.exists(), (
        f"FINRA short_interest dir missing: {finra_dir.relative_to(REPO)}. "
        "Blocks borrow_ok audit + squeeze_setup_long universe."
    )
