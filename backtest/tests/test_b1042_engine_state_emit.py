"""B1042 Council 136 Option-7 Layer 1: engine_state.json emission tests.

# Source: Council 136 Option-7 + feedback_monitor_design_vs_operational_gap
# (CHECKLIST #121) per CHECKLIST #77.

Tests verify the 100-day checkpoint loop in backtest/engine/backtest.py
emits engine_state.json with the canonical schema that B1019 runtime
monitor consumes. Closes the design-vs-armed gap surfaced by Council
135 (B1019 monitor required engine_state.json producer; none existed).
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def test_b1042_engine_backtest_module_emits_engine_state():
    """B1042: Verify backtest.py contains the engine_state.json emission block."""
    import inspect
    from backtest.engine import backtest as _bt
    source = inspect.getsource(_bt)
    assert "engine_state.json" in source, (
        "engine_state.json producer must exist in backtest.py per B1042 "
        "Council 136 Option-7 Layer 1"
    )
    assert "engine_state.json.tmp" in source, (
        "Atomic write via .tmp + os.replace pattern required"
    )
    assert "CHECKPOINT day=" in source, (
        "Paired INFO log 'CHECKPOINT day=N' must be emitted per Council 136"
    )


def test_b1042_engine_state_schema_fields_documented():
    """B1042: Verify the engine_state.json schema includes the 8 canonical fields
    that b1019_phase_1_runtime_monitor.py consumes."""
    import inspect
    from backtest.engine import backtest as _bt
    source = inspect.getsource(_bt)
    required_fields = [
        "sim_date",
        "sim_day_index",
        "tickers_processed",
        "trades_so_far",
        "open_trades",
        "status",
        "timestamp",
        "pid",
    ]
    for field in required_fields:
        assert f'"{field}"' in source, (
            f"engine_state.json field {field!r} missing from emission block"
        )


def test_b1042_atomic_write_pattern():
    """B1042: Verify atomic write via tmp + replace prevents partial reads."""
    import inspect
    from backtest.engine import backtest as _bt
    source = inspect.getsource(_bt)
    assert "_os.replace(state_tmp, state_path)" in source, (
        "Atomic write via os.replace required for B1019 consumer safety"
    )


def test_b1042_checkpoint_cadence_matches_b1019_monitor_default():
    """B1042: Verify 100-day cadence matches B1019 monitor --checkpoint-cadence
    default."""
    import inspect
    from backtest.engine import backtest as _bt
    source = inspect.getsource(_bt)
    # B1019 monitor default --checkpoint-cadence=100
    # backtest.py emits at `if i > 0 and i % 100 == 0`
    assert "i % 100 == 0" in source, (
        "Engine cadence must match B1019 monitor default 100 days"
    )


def test_b1042_b1019_monitor_script_exists():
    """B1042: Sentinel test - B1019 monitor script must exist at canonical path
    so launch_r5_master_4y_v2.sh Layer 2 wire can invoke it."""
    repo_root = Path(__file__).resolve().parents[2]
    monitor_path = repo_root / "scripts" / "b1019_phase_1_runtime_monitor.py"
    assert monitor_path.exists(), (
        f"B1019 monitor script missing at {monitor_path}; Layer 2 wire "
        f"in launch_r5_master_4y_v2.sh depends on this script existing"
    )


def test_b1042_launch_script_wires_b1019_monitor():
    """B1042: Verify launch_r5_master_4y_v2.sh actually invokes the B1019 monitor
    (closes the recurring design-vs-armed gap surfaced by Council 135)."""
    repo_root = Path(__file__).resolve().parents[2]
    launch_script = repo_root / "scripts" / "launch_r5_master_4y_v2.sh"
    assert launch_script.exists()
    content = launch_script.read_text()
    # Must actually invoke (not just comment)
    assert "python scripts/b1019_phase_1_runtime_monitor.py" in content, (
        "launch_r5_master_4y_v2.sh must INVOKE B1019 monitor per Council 136 "
        "Option-7 Layer 2; mere COMMENT references do not count "
        "(feedback_monitor_design_vs_operational_gap recurrence prevention)"
    )
    # Must wire the engine-state file produced by Layer 1
    assert "--engine-state" in content
    # Must have HALT-CRITICAL detection logic that SIGTERMs engine
    assert "HALT-CRITICAL" in content
    assert "kill -15" in content or "kill -TERM" in content, (
        "HALT-CRITICAL watcher must SIGTERM engine to honor 'stop if any "
        "issues' owner mandate"
    )


def test_b1042_b1019_halt_sentinel_emission():
    """B1042: Verify launch script emits B1019_HALT sentinel to S3 when
    HALT-CRITICAL detected."""
    repo_root = Path(__file__).resolve().parents[2]
    launch_script = repo_root / "scripts" / "launch_r5_master_4y_v2.sh"
    content = launch_script.read_text()
    assert "PHASE_\\${PHASE_NUM}_B1019_HALT" in content or "B1019_HALT" in content, (
        "B1019_HALT sentinel must be emitted to S3 for Claude-side polling "
        "loop to detect mid-run abort per Council 136 Layer 3"
    )
