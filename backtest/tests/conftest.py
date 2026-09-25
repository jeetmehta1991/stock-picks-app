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


PYRAMID_TIERS = frozenset({"test_unit.py", "test_integration.py"})
_REPORTED = ("passed", "failed", "skipped", "xfailed", "xpassed", "error")


def pyramid_stamp_decision(files_run, exitstatus, *, collectonly, keyword,
                           markexpr, n_items, n_reported, n_deselected):
    """S6-B3107b (B3108): the stamp pytest_sessionfinish writes, or None.

    MEASURED 2026-09-25: a `--collect-only` session over both tiers ran ZERO
    tests and wrote a GREEN stamp (n_tests 1546), because the old rule read
    only which FILES the collected items came from and the exit status. The
    same rule stamped a `-k` selection green whenever it kept one test from
    each file. Now: nothing is written unless the session covered both tiers
    UNSELECTED (no collect-only, no -k, no -m, nothing deselected); and it is
    GREEN only when the exit status is 0 AND every collected test reported a
    result - an interrupted run writes a RED stamp, never a green one."""
    if not PYRAMID_TIERS <= set(files_run):
        return None
    if collectonly or keyword or markexpr or n_deselected:
        return None
    green = int(exitstatus) == 0 and n_items > 0 and n_reported >= n_items
    return {"exitstatus": int(exitstatus), "green": green,
            "n_tests": int(n_items), "n_reported": int(n_reported)}


def pytest_sessionfinish(session, exitstatus):
    """B1254 (Council 300, S6-B1253-GATE-A1 owner-approved 2026-07-08):
    write .pyramid_stamp at repo root when a session that included BOTH
    pyramid tiers (test_unit.py + test_integration.py) finishes GREEN.

    scripts/preflight.py C6 reads this stamp and BLOCKS commits staging
    *.py files when the stamp is missing, red, or older than the newest
    staged .py file's mtime (tests must run AFTER the last code edit).

    Partial runs (single file / -k / -m selections, --collect-only) do NOT
    write the stamp -- only a full-pyramid session counts, per
    feedback_pyramid_no_exceptions. ENFORCED by pyramid_stamp_decision
    since S6-B3107b (B3108); before that this sentence was a claim the code
    did not keep - a collect-only session wrote a GREEN stamp.
    """
    import json
    import subprocess
    import time
    from pathlib import Path

    ran_files = {Path(str(item.fspath)).name for item in session.items}
    # S6-B3107b (B3108): decide from what RAN, not from what was collected.
    opt = session.config.option
    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    stats = getattr(tr, "stats", None) or {}
    item_ids = {item.nodeid for item in session.items}
    reported = {getattr(r, "nodeid", None) for cat in _REPORTED
                for r in stats.get(cat, [])} & item_ids
    decided = pyramid_stamp_decision(
        ran_files, exitstatus,
        collectonly=bool(getattr(opt, "collectonly", False)),
        keyword=getattr(opt, "keyword", "") or "",
        markexpr=getattr(opt, "markexpr", "") or "",
        n_items=len(item_ids), n_reported=len(reported),
        n_deselected=len(stats.get("deselected", [])))
    if decided is None:
        return
    repo_root = Path(__file__).resolve().parents[2]
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except Exception:
        head = "unknown"
    stamp = {"timestamp": time.time(), **decided, "git_head": head}
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
