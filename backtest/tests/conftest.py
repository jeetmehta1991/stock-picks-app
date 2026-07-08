"""pytest conftest for backtest/tests.

# Source: B1039 Council 132 Item #3 Phase A >=90% coverage measurement.
# Per CHECKLIST #77.

B1038 introduced SMC_PHASE B-CANARY short-circuit at compute_smc_signals
entry. This causes 7 SMC test files (unit/pit/integration/performance/
statistical/adversarial/xvalidation) that exercise compute_smc_signals
semantics to return {} from all calls, leaving the function body (lines
128-433) uncovered.

This fixture auto-monkeypatches SMC_PHASE='PRODUCTION' for any test in
files matching test_smartmoneyconcepts_*.py + test_smc_* - semantic
tests bypass the canary gate; production-mode tests (test_b1038_*)
explicitly opt-out.
"""
from __future__ import annotations

import pytest


def pytest_sessionfinish(session, exitstatus):
    """B1254 (Council 300, S6-B1253-GATE-A1 owner-approved 2026-07-08):
    write .pyramid_stamp at repo root when a session that included BOTH
    pyramid tiers (test_unit.py + test_integration.py) finishes GREEN.

    scripts/preflight.py C6 reads this stamp and BLOCKS commits staging
    *.py files when the stamp is missing, red, or older than the newest
    staged .py file's mtime (tests must run AFTER the last code edit).

    Partial runs (single file / -k selections) do NOT write the stamp --
    only a full-pyramid session counts, per feedback_pyramid_no_exceptions.
    """
    import json
    import subprocess
    import time
    from pathlib import Path

    ran_files = {Path(str(item.fspath)).name for item in session.items}
    if not {"test_unit.py", "test_integration.py"} <= ran_files:
        return
    repo_root = Path(__file__).resolve().parents[2]
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except Exception:
        head = "unknown"
    stamp = {
        "timestamp": time.time(),
        "exitstatus": int(exitstatus),
        "green": int(exitstatus) == 0,
        "n_tests": len(session.items),
        "git_head": head,
    }
    try:
        (repo_root / ".pyramid_stamp").write_text(
            json.dumps(stamp), encoding="utf-8")
    except Exception:
        pass  # stamp write failure must never fail the test run itself


@pytest.fixture(autouse=True)
def _smc_phase_production_for_semantic_tests(request, monkeypatch):
    """Auto-monkeypatch SMC_PHASE='PRODUCTION' for SMC semantic tests.

    Applies to: test_smartmoneyconcepts_*.py + test_smc_spof_sentinel.py
    Does NOT apply to: test_b1038_smc_phase_canary.py (tests the canary
      gate itself + must observe B-CANARY default)
    """
    test_file = str(request.node.fspath)
    if "test_b1038_smc_phase_canary" in test_file:
        return  # B1038 tests must see B-CANARY default
    if "test_smartmoneyconcepts_" in test_file or "test_smc_spof_sentinel" in test_file:
        import backtest.config as _cfg
        monkeypatch.setattr(_cfg, "SMC_PHASE", "PRODUCTION")
