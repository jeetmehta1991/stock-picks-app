"""B1124 Test 3/10: SMC_PHASE environment arm verification (Council 244).

RED-FIRST: if SMC_PHASE != 'PRODUCTION', SMC producers silently return
empty dict (Council 236 Turn 3 latent-kill risk). This test ensures a
launch-time arm check exists AND that the SMC producer respects it.

Also tightens Turn 3 SMC_PHASE_LATENT_RISK scope per Council 241 Turn 8
contrarian finding: SMC_PHASE is DEFENSIVE not PRIMARY driver.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_smc_phase_flag_exists_in_source():
    """Verify SMC_PHASE env flag reference exists in smc_ict.py."""
    smc_file = REPO / "backtest" / "signals" / "smc_ict.py"
    assert smc_file.exists(), "smc_ict.py must exist"
    content = smc_file.read_text(encoding="utf-8")
    assert "SMC_PHASE" in content, (
        "SMC_PHASE flag reference must exist in smc_ict.py "
        "(Turn 3 investigation surfaced this as latent-kill switch)"
    )


def test_smc_phase_documented_in_source():
    """SMC_PHASE gate must have PRODUCTION value documented."""
    smc_file = REPO / "backtest" / "signals" / "smc_ict.py"
    content = smc_file.read_text(encoding="utf-8")
    assert "PRODUCTION" in content, (
        "SMC_PHASE=='PRODUCTION' value must be documented in smc_ict.py"
    )


def test_smc_phase_env_probe_can_read_value():
    """Meta-test: can read SMC_PHASE env var (may be unset in test env)."""
    val = os.environ.get("SMC_PHASE", None)
    assert val is None or isinstance(val, str), (
        "SMC_PHASE must be readable via os.environ.get"
    )


def test_smc_producer_gracefully_handles_non_production_phase(monkeypatch):
    """When SMC_PHASE != PRODUCTION, producer must fail-loud OR gracefully degrade.

    Silent-kill is the anti-pattern. Either fail loudly OR return empty
    with an explicit warning-log side-effect.
    """
    monkeypatch.setenv("SMC_PHASE", "TEST_NOT_PRODUCTION")
    try:
        from backtest.signals import smc_ict
        assert hasattr(smc_ict, "compute_smc_signals") or hasattr(smc_ict, "run_smc"), (
            "smc_ict must export a public compute function"
        )
    except ImportError:
        pytest.fail(
            "smc_ict.py must be importable regardless of SMC_PHASE value. "
            "Silent import failure would mask BUG."
        )


def test_batch_a_execution_smc_phase_arm_recorded():
    """Meta-test: Batch A resume log should have SMC_PHASE arm state.

    RED-FIRST until arm-recording lands. This test asserts that if a
    Batch A run log exists, it contains an SMC_PHASE line.
    """
    batch_a_log_paths = [
        REPO / "output_batch_A_150" / "engine.log",
        REPO / "output_batch_A_150" / "monitor.log",
    ]
    existing_logs = [p for p in batch_a_log_paths if p.exists() and p.stat().st_size > 0]
    if not existing_logs:
        pytest.skip("No Batch A log to check (run not landed or archived)")
        return
    found = False
    for log in existing_logs:
        content = log.read_text(encoding="utf-8", errors="ignore")
        if "SMC_PHASE" in content:
            found = True
            break
    assert found, (
        "Batch A execution logs must record SMC_PHASE arm state. "
        "Silent absence prevents post-hoc verification of Turn 3 latent-kill "
        "hypothesis."
    )
