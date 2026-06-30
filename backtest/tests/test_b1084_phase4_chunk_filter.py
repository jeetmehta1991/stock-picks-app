"""B1084 Council 205+206: Phase 4 strategy-band chunk filter pyramid tests.

Source: Owner directive 2026-06-29 'B then 4 parallel (8 chunks within
$40 cap)' + Council 205 verdict (16 chunks rejected; 8 chunks within cap)
+ Council 206 caveats (chunk-H slice fix + sum=220 pin).

Tests verify:
- get_strategy_chunk returns correct slice for each chunk index
- All chunks sum to ALL_STRATEGIES total (no orphans per Council 206)
- Chunk-H (last) handles non-divisible total via min() truncation
- get_chunk_index_from_env parses A-H + 0-7
- PHASE_4_CHUNK env var integration in run_phase1a.py
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]


def test_b1084_get_strategy_chunk_function_exists():
    """B1084: get_strategy_chunk helper must exist in screener module."""
    from backtest.signals import screener
    assert hasattr(screener, "get_strategy_chunk"), (
        "B1084 Council 205+206: get_strategy_chunk must exist"
    )


def test_b1084_get_chunk_index_from_env_exists():
    """B1084: get_chunk_index_from_env helper must exist."""
    from backtest.signals import screener
    assert hasattr(screener, "get_chunk_index_from_env"), (
        "B1084: get_chunk_index_from_env must exist for PHASE_4_CHUNK parsing"
    )


def test_b1084_pivot_206_no_orphan_strategies():
    """B1084 Council 206 CRITICAL: sum of all 8 chunks == ALL_STRATEGIES
    total. Naive slicing (idx*27:(idx+1)*27) at 220 strategies would
    orphan 4. This pin asserts the helper handles non-divisible totals."""
    from backtest.signals.screener import ALL_STRATEGIES, get_strategy_chunk
    n_chunks = 8
    total_via_chunks = 0
    seen_keys = set()
    for i in range(n_chunks):
        chunk = get_strategy_chunk(i, n_chunks=n_chunks)
        total_via_chunks += len(chunk)
        # Disjoint check
        for k in chunk:
            assert k not in seen_keys, (
                f"B1084 chunk {i} overlap with prior chunk on key {k!r}"
            )
            seen_keys.add(k)
    assert total_via_chunks == len(ALL_STRATEGIES), (
        f"B1084 Council 206 SUM CHECK: chunks total {total_via_chunks} "
        f"!= ALL_STRATEGIES {len(ALL_STRATEGIES)} (orphans = "
        f"{len(ALL_STRATEGIES) - total_via_chunks})"
    )
    assert seen_keys == set(ALL_STRATEGIES.keys()), (
        "B1084 chunks must collectively cover ALL strategy keys"
    )


def test_b1084_chunk_h_slice_fix():
    """B1084 Council 206: chunk H (last; idx=7) must include final
    strategies via min() truncation, not orphan them."""
    from backtest.signals.screener import ALL_STRATEGIES, get_strategy_chunk
    chunk_h = get_strategy_chunk(7, n_chunks=8)
    all_keys = list(ALL_STRATEGIES.keys())
    last_key = all_keys[-1]
    assert last_key in chunk_h, (
        f"B1084 Council 206: last strategy {last_key!r} must be in "
        f"chunk H (else orphaned by naive slicing)"
    )


def test_b1084_chunk_index_out_of_range_raises():
    """B1084: chunk_idx >= n_chunks must raise ValueError."""
    from backtest.signals.screener import get_strategy_chunk
    with pytest.raises(ValueError, match="out of range"):
        get_strategy_chunk(8, n_chunks=8)
    with pytest.raises(ValueError, match="out of range"):
        get_strategy_chunk(-1, n_chunks=8)


def test_b1084_env_var_parsing_alpha():
    """B1084: PHASE_4_CHUNK=A through H must map to 0-7."""
    from backtest.signals.screener import get_chunk_index_from_env
    for i, ch in enumerate("ABCDEFGH"):
        os.environ["PHASE_4_CHUNK"] = ch
        try:
            assert get_chunk_index_from_env() == i, (
                f"B1084 PHASE_4_CHUNK={ch!r} must map to idx={i}"
            )
        finally:
            del os.environ["PHASE_4_CHUNK"]


def test_b1084_env_var_parsing_numeric():
    """B1084: PHASE_4_CHUNK=0-7 must accept numeric form."""
    from backtest.signals.screener import get_chunk_index_from_env
    for i in range(8):
        os.environ["PHASE_4_CHUNK"] = str(i)
        try:
            assert get_chunk_index_from_env() == i
        finally:
            del os.environ["PHASE_4_CHUNK"]


def test_b1084_env_var_unset_returns_none():
    """B1084: unset PHASE_4_CHUNK = None (no chunk filter active;
    backward-compat for non-chunked launches)."""
    from backtest.signals.screener import get_chunk_index_from_env
    os.environ.pop("PHASE_4_CHUNK", None)
    assert get_chunk_index_from_env() is None


def test_b1084_env_var_invalid_raises():
    """B1084: PHASE_4_CHUNK=I (out of A-H) or =8 (out of 0-7) raises."""
    from backtest.signals.screener import get_chunk_index_from_env
    for bad in ("I", "Z", "8", "-1", "invalid"):
        os.environ["PHASE_4_CHUNK"] = bad
        try:
            with pytest.raises(ValueError):
                get_chunk_index_from_env()
        finally:
            del os.environ["PHASE_4_CHUNK"]


def test_b1084_run_phase1a_imports_chunk_helpers():
    """B1084: run_phase1a.py must import + invoke chunk-filter helpers
    so PHASE_4_CHUNK env var actually filters at launch."""
    content = (REPO / "backtest" / "run_phase1a.py").read_text()
    assert "get_chunk_index_from_env" in content, (
        "B1084: run_phase1a.py must call get_chunk_index_from_env"
    )
    assert "get_strategy_chunk" in content, (
        "B1084: run_phase1a.py must call get_strategy_chunk"
    )
    assert "PHASE_4_CHUNK" in content, (
        "B1084: PHASE_4_CHUNK env var reference required"
    )


def test_b1084_lineage_documented():
    """B1084: Council 205+206 lineage referenced in source."""
    screener_content = (REPO / "backtest" / "signals" / "screener.py").read_text()
    assert "B1084" in screener_content
    assert "Council 205" in screener_content or "Council 206" in screener_content
    runphase_content = (REPO / "backtest" / "run_phase1a.py").read_text()
    assert "B1084 Council 206" in runphase_content


def test_b1084_chunk_distribution_documented():
    """B1084: distribution table (28/28/28/28/28/28/28/24 = 220) must
    be documented in source for owner-readable audit trail."""
    content = (REPO / "backtest" / "signals" / "screener.py").read_text()
    # Check distribution table or sum=220 documentation
    assert "220" in content, "B1084: 220-strategy total must be documented"
    assert "27.5" in content or "ceil division" in content, (
        "B1084: non-divisible chunk math must be explained in comments"
    )
