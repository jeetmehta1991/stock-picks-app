"""B1059 A1 fire-rate baseline scaling pyramid test (PIVOT #36 catch).

# Source: HONEST-FINDING PIVOT #36 Phase D B1058 HALTed at Phase 1
# because B1019 A1 fire-rate used B660 full-universe baseline against
# single-ticker NVDA Phase 1 fires. 88 strategies flagged anomalous
# (ratio < 0.5) -> false HALT-CRITICAL. Per Council 158 Option-1 +
# CHECKLIST #77.

B1059 fix: monitor accepts --total-tickers-active and
--baseline-universe-size; scales expected_fpy by ratio before A1
comparison. Phase 1=1 -> baseline scales to 1/503 = 0.002 of full;
Phase 4=503 -> ratio=1.0 (no scaling; original behavior).
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MONITOR_PATH = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
LAUNCH_SCRIPT = REPO / "scripts" / "launch_r5_master_4y_v2.sh"


def test_b1059_monitor_accepts_total_tickers_active_arg():
    """B1059 PIVOT #36: monitor must accept --total-tickers-active arg
    for A1 baseline scaling."""
    content = MONITOR_PATH.read_text()
    assert "--total-tickers-active" in content, (
        "B1059 PIVOT #36 fix: B1019 monitor must accept "
        "--total-tickers-active arg per Council 158"
    )


def test_b1059_monitor_accepts_baseline_universe_size_arg():
    """B1059: monitor must accept --baseline-universe-size for denominator."""
    content = MONITOR_PATH.read_text()
    assert "--baseline-universe-size" in content, (
        "B1059: monitor must accept --baseline-universe-size arg per "
        "Council 158 (default 503 = T1a baseline)"
    )


def test_b1059_monitor_scales_baseline_by_ratio():
    """B1059 PIVOT #36 fix: monitor scales expected_fpy by ratio of
    active/baseline universe sizes before A1 comparison."""
    content = MONITOR_PATH.read_text()
    # Check for scaling logic
    assert ("total_tickers_active" in content and
            "baseline_universe_size" in content), (
        "B1059: monitor must compute scale from both args"
    )
    assert "scale = float(args.total_tickers_active)" in content, (
        "B1059: scale must be float division of active / baseline"
    )
    assert "v * scale" in content, (
        "B1059: baseline values must be multiplied by scale factor"
    )


def test_b1059_launch_script_passes_active_ticker_count():
    """B1059: launch script must pass --total-tickers-active to monitor
    based on phase ticker count (NCNT variable)."""
    content = LAUNCH_SCRIPT.read_text()
    assert "--total-tickers-active" in content, (
        "B1059: launch script must pass --total-tickers-active to monitor"
    )
    # NCNT is computed from TICKERS in run_phase function
    assert "--baseline-universe-size 503" in content, (
        "B1059: launch script must specify baseline-universe-size=503 (T1a)"
    )


def test_b1059_pivot_36_lineage_documented():
    """B1059: PIVOT #36 fix lineage must be documented in monitor code."""
    content = MONITOR_PATH.read_text()
    assert "PIVOT #36" in content, (
        "B1059: PIVOT #36 lineage must be in monitor.py docstring/comments"
    )
    assert "B1059" in content, "B1059 batch lineage must be referenced"


def test_b1059_phase_4_unchanged_when_active_equals_baseline():
    """B1059 regression guard: Phase 4 (active=baseline=503) must produce
    NO scaling so A1 behavior is identical to pre-B1059."""
    content = MONITOR_PATH.read_text()
    # The scaling is gated on active != baseline
    assert ("args.total_tickers_active != args.baseline_universe_size"
            in content), (
        "B1059: scaling must only fire when active != baseline; "
        "Phase 4 (active=503=baseline) must skip scaling for regression "
        "compatibility"
    )
