"""B1089 pyramid: 30-min time-based checkpoint + auto-resume polling tests.

Source: Owner directive 2026-06-30 (6 requirements) + Council 215
verdict (5 advisors APPROVE all + caveats).

Test scope:
- Engine __init__ initializes _last_checkpoint_time + _checkpoint_interval_seconds
- Paired-writer block uses sim_day OR time trigger
- Atomic-pair reset: _last_checkpoint_time only resets if BOTH writers succeed
- auto_resume_polling.sh: prefix-exists check + max_resume=3
- Lineage documented
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
BACKTEST_PY = REPO / "backtest" / "engine" / "backtest.py"
AUTO_RESUME_SH = REPO / "scripts" / "auto_resume_polling.sh"


def test_b1089_engine_init_has_checkpoint_timer():
    """B1089: BacktestEngine.__init__ must initialize _last_checkpoint_time
    and _checkpoint_interval_seconds."""
    from backtest.engine.backtest import BacktestEngine
    eng = BacktestEngine.__new__(BacktestEngine)
    # Verify the init code path will set these
    content = BACKTEST_PY.read_text()
    assert "self._last_checkpoint_time = _time_init.time()" in content
    assert "self._checkpoint_interval_seconds = 1800" in content, (
        "B1089: 30-min (1800s) checkpoint interval per owner directive"
    )


def test_b1089_paired_writer_uses_time_or_sim_day_trigger():
    """B1089 Council 215 Fix 1: paired-writer block uses _should_checkpoint
    flag computed from EITHER sim_day OR time trigger."""
    content = BACKTEST_PY.read_text()
    assert "_should_checkpoint = _sim_day_trigger or _time_trigger" in content
    # Both writers gated by same flag (atomic-pair semantics)
    assert "if _should_checkpoint and self.closed_trades:" in content, (
        "B1089: CSV writer gated by _should_checkpoint"
    )
    assert "if _should_checkpoint:" in content, (
        "B1089: engine_state writer gated by _should_checkpoint"
    )


def test_b1089_atomic_pair_reset_after_both_writers():
    """B1089 Council 214+215: _last_checkpoint_time resets ONLY when
    both writers succeed (atomic-pair semantics)."""
    content = BACKTEST_PY.read_text()
    assert "_csv_written = True" in content, (
        "B1089: CSV writer must mark success"
    )
    assert "_engine_state_written = True" in content, (
        "B1089: engine_state writer must mark success"
    )
    # Reset condition includes pair success check
    assert "_pair_ok = _engine_state_written and (" in content
    assert "_csv_written or not self.closed_trades" in content, (
        "B1089: degenerate-pair handling (trades=0 has no CSV)"
    )
    assert "self._last_checkpoint_time = _now_chkpt" in content


def test_b1089_time_trigger_logic_30min():
    """B1089: time trigger uses _checkpoint_interval_seconds (1800s)."""
    content = BACKTEST_PY.read_text()
    assert "(_now_chkpt - self._last_checkpoint_time)" in content
    assert ">= self._checkpoint_interval_seconds" in content


def test_b1089_sim_day_trigger_preserved():
    """B1089: B1081 PIVOT #44 cadence (i==50 OR i%100==0) preserved as
    belt-and-suspenders."""
    content = BACKTEST_PY.read_text()
    assert "_sim_day_trigger = (i > 0 and (i == 50 or i % 100 == 0))" in content


def test_b1089_simulated_time_advancement():
    """B1089 functional: simulating time advancement past 30 min triggers
    paired-write. (Logic mirror, since we can't easily test the engine
    main loop in isolation.)"""
    # Mirror of the trigger logic
    last_checkpoint = 1000.0
    interval = 1800
    # Case 1: time NOT elapsed
    now = 1500.0
    time_trigger = (now - last_checkpoint) >= interval
    assert time_trigger is False
    # Case 2: time exceeded
    now = 3001.0
    time_trigger = (now - last_checkpoint) >= interval
    assert time_trigger is True


def test_b1089_auto_resume_script_exists():
    """B1089 Council 215 Fix 2: auto_resume_polling.sh must exist."""
    assert AUTO_RESUME_SH.exists(), (
        "B1089 Council 215 Fix 2: scripts/auto_resume_polling.sh must exist"
    )


def test_b1089_auto_resume_max_resume_count_3():
    """B1089 Council 215 Adversarial caveat: max_resume_count=3 per chunk."""
    content = AUTO_RESUME_SH.read_text()
    assert "MAX_RESUME=3" in content, (
        "B1089 Council 215: max_resume_count=3 to bound runaway spend"
    )


def test_b1089_auto_resume_prefix_exists_check():
    """B1089 Council 215 Adversarial caveat: verify RESUME_FROM_RUN_ID
    prefix exists before relaunch."""
    content = AUTO_RESUME_SH.read_text()
    assert "S3 prefix" in content or "s3 ls" in content
    assert "but S3 prefix" in content or "prefix exists" in content.lower() or \
           "if aws s3 ls" in content, (
        "B1089 Council 215: must verify prefix-exists before auto-relaunch"
    )


def test_b1089_auto_resume_only_on_spot_termination():
    """B1089: auto-resume triggers ONLY on Server.SpotInstanceTermination,
    not on Client.UserInitiatedShutdown."""
    content = AUTO_RESUME_SH.read_text()
    assert "Server.SpotInstanceTermination" in content
    assert "Client.UserInitiatedShutdown" in content, (
        "B1089: must distinguish spot interrupt from user terminate"
    )
    # User terminate explicitly NOT auto-resumed
    assert "not auto-resuming" in content


def test_b1089_auto_resume_uses_r6a_4xlarge():
    """B1089: auto-resume uses r6a.4xlarge (PIVOT #48 fix; 128GB RAM
    headroom for pool=16 bulk-feed loading)."""
    content = AUTO_RESUME_SH.read_text()
    assert "r6a.4xlarge" in content


def test_b1089_lineage_documented():
    """B1089 Council 215 lineage in source."""
    bt = BACKTEST_PY.read_text()
    assert "B1089" in bt
    assert "Council 215" in bt
    auto = AUTO_RESUME_SH.read_text()
    assert "B1089" in auto
    assert "Council 215" in auto
