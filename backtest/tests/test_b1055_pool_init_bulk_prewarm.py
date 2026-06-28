"""B1055 pool init bulk pre-warm pyramid test (PIVOT #32 catch).

# Source: HONEST-FINDING PIVOT #32 Phase D B1054 Phase 1 timeout. Engine
# log showed bulk-feed reloads per sim_day. Root cause: pool workers'
# _BULK_CACHE was empty at first screen_instrument call. Fix: pre-warm
# Quiver bulk + ETF universe in _pool_init. Per CHECKLIST #126 + #127
# + Council 150 Option B + Council 151 Option-3 per CHECKLIST #77.

Tests guard against regressions in pool init pre-warm pattern.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCREENER = REPO / "backtest" / "signals" / "screener.py"


def test_b1055_pool_init_prewarms_quiver_bulk_feeds():
    """B1055 PIVOT #32 fix: _pool_init must pre-warm Quiver bulk feeds
    (insidertrading + sec13f) so per-sim_day cache miss doesn't fire.

    Without pre-warm, each pool worker's first screen_instrument call
    triggers ~10-15 sec parquet read of 1.5M total rows. With 60 workers
    + per-day pool dispatch, this scales to ~20 sec/day overhead.
    """
    content = SCREENER.read_text()
    # Find _pool_init function definition
    assert "def _pool_init(" in content, "_pool_init must exist in screener.py"
    # Extract body (simple regex; function ends at next 'def ' at column 0)
    pool_init_start = content.find("def _pool_init(")
    pool_init_end = content.find("\ndef ", pool_init_start + 1)
    body = content[pool_init_start:pool_init_end] if pool_init_end > 0 else content[pool_init_start:]
    # Pre-warm assertions
    assert "_load_quiver_bulk" in body, (
        "B1055 PIVOT #32 fix: _pool_init must call _load_quiver_bulk "
        "for insidertrading + sec13f datasets to pre-warm cache. "
        "Without this, per-sim_day overhead is ~20s (vs 3-5s target)."
    )
    assert '"insidertrading"' in body or "'insidertrading'" in body, (
        "B1055: must pre-warm insidertrading bulk feed"
    )
    assert '"sec13f"' in body or "'sec13f'" in body, (
        "B1055: must pre-warm sec13f bulk feed"
    )


def test_b1055_pool_init_prewarms_etf_universe():
    """B1055 PIVOT #32 fix: _pool_init must pre-warm ETF universe so
    'Loaded 28 Tier 1 ETFs' log doesn't fire per sim_day call site."""
    content = SCREENER.read_text()
    pool_init_start = content.find("def _pool_init(")
    pool_init_end = content.find("\ndef ", pool_init_start + 1)
    body = content[pool_init_start:pool_init_end] if pool_init_end > 0 else content[pool_init_start:]
    assert "from backtest.data.universe import ETFS_FULL" in body, (
        "B1055: _pool_init must import ETFS_FULL to trigger universe.py "
        "module load + get_etfs_full() call ONCE per worker spawn "
        "instead of per sim_day"
    )


def test_b1055_pool_init_preserves_existing_prewarms():
    """B1055: existing pre-warms (insider_buying + index_rebalance) must
    remain. Regression catcher."""
    content = SCREENER.read_text()
    pool_init_start = content.find("def _pool_init(")
    pool_init_end = content.find("\ndef ", pool_init_start + 1)
    body = content[pool_init_start:pool_init_end] if pool_init_end > 0 else content[pool_init_start:]
    assert "_load_insiders_global" in body, (
        "B1055: existing insider_buying pre-warm must remain"
    )
    assert "_load_events" in body, (
        "B1055: existing index_rebalance pre-warm must remain"
    )


def test_b1055_smart_money_load_quiver_bulk_exists():
    """B1055: backtest.data.smart_money._load_quiver_bulk must be
    importable + callable per Council 151 cache-determinism."""
    from backtest.data.smart_money import _load_quiver_bulk, _BULK_CACHE
    assert callable(_load_quiver_bulk)
    # Cache must be a dict (per-process global)
    assert isinstance(_BULK_CACHE, dict)


def test_b1055_universe_etfs_full_loads_at_module_level():
    """B1055: importing backtest.data.universe.ETFS_FULL must trigger
    the load (verifies pre-warm strategy works)."""
    from backtest.data.universe import ETFS_FULL
    assert isinstance(ETFS_FULL, list)
    # Per CLAUDE.md: 28 ETFs in current snapshot
    assert len(ETFS_FULL) > 0, "ETFS_FULL must load on import (pre-warm path)"


def test_b1055_pivot_32_lineage_documented():
    """B1055: PIVOT #32 fix must be documented in _pool_init docstring
    for future readers per CHECKLIST #126 evidence-artifact rule."""
    content = SCREENER.read_text()
    assert "PIVOT #32" in content or "pivot #32" in content.lower(), (
        "B1055: PIVOT #32 lineage must be documented in code"
    )
    assert "B1055" in content, "B1055 batch lineage must be documented"
