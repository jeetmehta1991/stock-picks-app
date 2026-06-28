"""B1057 B+C fixes: dataset naming hotfix + phase-timing instrumentation.

# Source: HONEST-FINDING PIVOT #34 (B1055 naming bug confirmed via B1056
# forensics) + Council 153 Option D + Council 154 Option-2 per CHECKLIST #77.

Tests guard against:
- Phantom dataset names in pool init pre-warm (B fix)
- Missing per-day phase-timing logs (C instrumentation)
"""
from __future__ import annotations

import inspect
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_b1057_pool_init_prewarms_REAL_quiver_datasets():
    """B1057 PIVOT #34 fix: _pool_init must pre-warm the actual dataset
    names used in smart_money.py call sites.

    B1055 had a typo: pre-warmed 'insidertrading' (phantom; only used by
    pre-warm code itself) and 'sec13f' (real but not the hot path).
    Real hot datasets per smart_money.py:498/675/1640/1807:
      insiders + sec13fchanges (HOT 1M + 500k rows)
      sec13f + patentmomentum + corporatedonors (cold but real)
    """
    from backtest.signals import screener
    source = inspect.getsource(screener)
    # Find _pool_init body
    pool_init_start = source.find("def _pool_init(")
    pool_init_end = source.find("\ndef ", pool_init_start + 1)
    body = source[pool_init_start:pool_init_end]
    # Real datasets must be pre-warmed
    for ds in ("insiders", "sec13fchanges"):
        assert f'"{ds}"' in body, (
            f"B1057 PIVOT #34 fix: _pool_init must pre-warm '{ds}' "
            f"(actual hot dataset per smart_money.py call sites)"
        )
    # Phantom name must NOT be referenced (the B1055 typo)
    # We allow it in comments/docs but NOT in actual pre-warm calls
    # (which use double-quoted strings inside _load_quiver_bulk(...))
    assert 'load_quiver_bulk("insidertrading")' not in body, (
        "B1057 PIVOT #34: 'insidertrading' is a PHANTOM dataset (Quiver "
        "API endpoint path, not the cache key). Use 'insiders' instead."
    )


def test_b1057_pool_init_covers_all_smart_money_call_sites():
    """B1057: pre-warm must cover ALL datasets actually loaded by
    smart_money.py to maximize amortization."""
    from backtest.signals import screener
    pool_source = inspect.getsource(screener)
    pool_init_start = pool_source.find("def _pool_init(")
    pool_init_end = pool_source.find("\ndef ", pool_init_start + 1)
    body = pool_source[pool_init_start:pool_init_end]
    # All datasets called from smart_money.py
    expected = {"insiders", "sec13fchanges", "sec13f",
                "patentmomentum", "corporatedonors"}
    missing = [ds for ds in expected if f'"{ds}"' not in body]
    assert not missing, (
        f"B1057 pre-warm missing datasets: {missing}. "
        f"Expected coverage per smart_money.py grep: {sorted(expected)}"
    )


def test_b1057_process_day_has_phase_timing_instrumentation():
    """B1057 C-instrumentation: _process_day must emit PHASE_TIMING logs
    at key checkpoints so next forensics can decompose the silent gap."""
    from backtest.engine import backtest as _bt
    source = inspect.getsource(_bt)
    # Find _process_day function
    pd_start = source.find("def _process_day(")
    pd_end = source.find("\n    def ", pd_start + 1)
    body = source[pd_start:pd_end] if pd_end > 0 else source[pd_start:]
    assert "PHASE_TIMING" in body, (
        "B1057 C-fix: _process_day must emit PHASE_TIMING logs for "
        "per-day wall-clock decomposition (per B1056 forensics)"
    )
    # Required checkpoints
    for marker in ("PHASE_TIMING day=%s start",
                   "PHASE_TIMING day=%s ohlcv_pit_built",
                   "PHASE_TIMING day=%s exits_done",
                   "PHASE_TIMING day=%s screen_done"):
        assert marker in body, (
            f"B1057 missing PHASE_TIMING marker: {marker!r}"
        )


def test_b1057_phase_timing_is_info_level():
    """B1057: PHASE_TIMING logs must be INFO-level (visible without flags)."""
    from backtest.engine import backtest as _bt
    source = inspect.getsource(_bt)
    # PHASE_TIMING markers should all use logger.info, not debug
    assert "logger.info(\"PHASE_TIMING" in source, (
        "B1057: PHASE_TIMING logs must use logger.info for visibility"
    )


def test_b1057_pivot_34_lineage_documented():
    """B1057: PIVOT #34 fix lineage documented in code."""
    from backtest.signals import screener
    source = inspect.getsource(screener)
    assert "PIVOT #34" in source or "pivot #34" in source.lower(), (
        "B1057: PIVOT #34 lineage must be in screener.py _pool_init docstring"
    )
    assert "B1057" in source, "B1057 batch lineage must be referenced"
