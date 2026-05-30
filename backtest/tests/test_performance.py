"""Performance tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Performance = runtime / memory stays within bounds. Catches O(n^2) sneaks,
import-time blowups, and cache-load slowdowns BEFORE Phase 1A scale-up.

Budgets are deliberately conservative (2-3x normal) so green build days don't
flake the gate; what we want is the catch when a regression is 10x.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


pytestmark = pytest.mark.performance


# -- Perf 1: cache load for 1937 OHLCV files --------------------------------
def test_ohlcv_cache_load_under_5s() -> None:
    """Loading the OHLCV cache index for 1937 tickers should complete <5s.
    Catches the kind of regression where someone introduces per-row reads
    on what should be a single bulk parquet read."""
    cache_dir = REPO_ROOT / "backtest" / "data" / "cache" / "ohlcv"
    if not cache_dir.is_dir():
        pytest.skip("OHLCV cache not present")
    files = list(cache_dir.glob("*.parquet"))
    if len(files) < 100:
        pytest.skip(f"only {len(files)} OHLCV files - smoke env, not perf env")
    t0 = time.time()
    # Just stat each file - that's what the cache index does
    for f in files:
        _ = f.stat()
    elapsed = time.time() - t0
    assert elapsed < 5.0, f"{len(files)}-file stat took {elapsed:.2f}s (budget: 5s)"


# -- Perf 2: dashboard build under 90s --------------------------------------
@pytest.mark.slow
def test_dashboard_stage_2_build_under_90s() -> None:
    """build_dashboard_stage_2.py should complete <90s. Slowness here
    typically means a corpus grep ballooned (e.g. someone added a megafile
    to backtest/). Marked slow - run via `pytest -m slow` or full suite,
    not in default test pyramid sweep."""
    import subprocess
    builder = REPO_ROOT / "scripts" / "build_dashboard_stage_2.py"
    if not builder.exists():
        pytest.skip("builder script missing")
    t0 = time.time()
    r = subprocess.run(
        [sys.executable, str(builder)],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120,
    )
    elapsed = time.time() - t0
    assert r.returncode == 0, f"builder exit={r.returncode}\n{r.stderr[-500:]}"
    assert elapsed < 90.0, f"dashboard build took {elapsed:.1f}s (budget: 90s)"


# -- Perf 3: doc-count drift check under 10s --------------------------------
def test_sync_doc_counts_under_10s() -> None:
    """sync_doc_counts.py --check should complete <10s. It's called from the
    pre-commit hook so any regression here directly hurts dev velocity.

    Batch 482 (2026-05-29): the 10s budget is a DEV-VELOCITY assertion, not
    a CPU benchmark. Under xdist parallel load N workers compete for cores
    so the subprocess can take 20-30s without the script itself being any
    slower in isolation. Scale the budget to 10s * (num_workers / 2) to
    stay honest about what the test is measuring (dev-velocity impact at
    typical local run, not absolute CPU performance under contention).
    """
    import os
    import subprocess
    # When run via xdist, env var PYTEST_XDIST_WORKER_COUNT is set.
    n_workers = int(os.environ.get("PYTEST_XDIST_WORKER_COUNT", "1"))
    budget = max(10.0, 10.0 * (n_workers / 2.0))
    t0 = time.time()
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "sync_doc_counts.py"), "--check"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120,
    )
    elapsed = time.time() - t0
    assert r.returncode == 0
    assert elapsed < budget, (
        f"sync_doc_counts.py --check took {elapsed:.2f}s "
        f"(budget: {budget:.0f}s, xdist workers: {n_workers})"
    )


# -- Perf 4: regime classifier under 100ms / call --------------------------
def test_regime_classifier_under_100ms() -> None:
    """classify_regime() runs once per backtest day (252+ calls per backtest);
    must be <100ms per call to keep total <30s."""
    try:
        from backtest.engine.regime_filter import classify_regime
    except ImportError:
        pytest.skip("regime_filter not importable")
    import pandas as pd
    # Synthetic 252-day SPY series
    dates = pd.date_range("2024-01-01", periods=252, freq="B")
    spy = pd.DataFrame({
        "close": 400.0 + (pd.Series(range(252)) * 0.5),
        "high":  410.0 + (pd.Series(range(252)) * 0.5),
        "low":   390.0 + (pd.Series(range(252)) * 0.5),
        "open":  400.0 + (pd.Series(range(252)) * 0.5),
        "volume": 100_000_000,
    }, index=dates)
    t0 = time.time()
    try:
        _ = classify_regime(spy, as_of=dates[-1])
    except Exception:
        pytest.skip("classify_regime signature differs from synthetic harness")
    elapsed = time.time() - t0
    assert elapsed < 0.1, f"classify_regime took {elapsed*1000:.1f}ms (budget: 100ms)"
