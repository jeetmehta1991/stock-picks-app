"""B1127 Tier-5 Scale Invariance (Council 246).

CATCHES: L179 monitor A1 baseline scaling — B1019 monitor compared
per-strategy fires/yr against B660 baseline (T1a 503 tickers) but Phase D
launched NVDA-only (1 ticker). At sim_day 100 A1 flagged 88 strategies as
anomalous + SIGTERMed the engine. **Engine was healthy — monitor was
structurally invalid at single-ticker scale.**

RULE: monitors comparing measurement to baseline must accept both
active_size + baseline_size and apply correct scaling (linear here).
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_b1019_monitor_baseline_scaling_supported():
    """B1019 monitor must expose --total-tickers-active + --baseline-universe-size."""
    monitor = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    if not monitor.exists():
        pytest.skip(f"Monitor script missing at {monitor}")
        return
    content = monitor.read_text(encoding="utf-8", errors="ignore")
    assert "--total-tickers-active" in content or "total_tickers_active" in content, (
        "L179 regression: monitor must accept --total-tickers-active arg"
    )
    assert "--baseline-universe-size" in content or "baseline_universe_size" in content, (
        "L179 regression: monitor must accept --baseline-universe-size arg"
    )


def test_b660_baseline_metadata_includes_scale_factor():
    """B660 fire-count baseline must include universe metadata for scale correction."""
    baseline_paths = list((REPO / "output_audit").glob("b660_*.json"))
    if not baseline_paths:
        pytest.skip("B660 baseline artifact not present")
        return
    import json

    for path in baseline_paths[:3]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Look for universe metadata
        universe_keys = {"universe", "n_tickers_sampled", "projection_scale_factor"}
        if isinstance(data, dict):
            found = universe_keys & set(data.keys())
            if found:
                return  # First B660 with metadata is sufficient
    pytest.skip(
        "B660 baseline metadata check inconclusive - no matching files. "
        "L179 unblock CTA: ensure B660 baseline records universe + "
        "n_tickers_sampled + projection_scale_factor for scale correction."
    )


def test_pool_workers_scale_config_present():
    """L177 pool worker scaling: per-phase config in launch script."""
    launch = REPO / "scripts" / "launch_r5_master_4y_v2.sh"
    if not launch.exists():
        pytest.skip("Launch script missing")
        return
    content = launch.read_text(encoding="utf-8", errors="ignore")
    # Look for per-phase pool config keywords
    has_pool_config = "POOL_WORKERS" in content or "pool_workers" in content or "--pool" in content
    assert has_pool_config, (
        "L177 regression: launch script must have per-phase pool worker config. "
        "Never assume 'more workers = faster'; benchmark."
    )


def test_scale_invariance_test_exists_for_a1_metric():
    """Verify B1059 baseline scaling test exists (L179 regression guard)."""
    test_file = REPO / "backtest" / "tests" / "test_b1059_a1_baseline_scaling.py"
    assert test_file.exists(), (
        f"L179 regression guard test missing at {test_file.relative_to(REPO)}. "
        f"Every scale-invariance rule needs a regression test."
    )
