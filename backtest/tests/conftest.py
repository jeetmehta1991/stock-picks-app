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
                           markexpr, n_items, n_reported, n_deselected,
                           nodeid_selected=False):
    """S6-B3107b (B3108): the stamp pytest_sessionfinish writes, or None.

    MEASURED 2026-09-25: a `--collect-only` session over both tiers ran ZERO
    tests and wrote a GREEN stamp (n_tests 1546), because the old rule read
    only which FILES the collected items came from and the exit status. The
    same rule stamped a `-k` selection green whenever it kept one test from
    each file. Now: nothing is written unless the session covered both tiers
    UNSELECTED (no collect-only, no -k, no -m, nothing deselected); and it is
    GREEN only when the exit status is 0 AND every collected test reported a
    result - an interrupted run writes a RED stamp, never a green one.
    S6-B3130a (B3137): a session narrowed by NODE IDS (`file::test`) is a
    selection too - two named tests, one from each tier, would otherwise
    read as both tiers ran unselected and write a GREEN stamp (the pyramid
    gate's read-set re-run is exactly such a session)."""
    if not PYRAMID_TIERS <= set(files_run):
        return None
    if collectonly or keyword or markexpr or n_deselected or nodeid_selected:
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
        n_deselected=len(stats.get("deselected", [])),
        nodeid_selected=any("::" in str(a)
                            for a in (session.config.args or [])))
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


@pytest.fixture(autouse=True, scope="session")
def _workflow_state_out_isolated(tmp_path_factory):
    """S6-B3130a (B3139): inside a test session the prompt hook's derivation
    (scripts/build_workflow_state.py) writes its file copy to a temp path,
    never the production output_audit/workflow_state.json. MEASURED: that
    file was the only non-gate output_audit path the batch-2 full pyramid
    moved (output_audit/b3139_pyramid_batch2.out) - four tests drive the
    derivation - and the read-set re-run of one of them rewrote it again,
    so the gate read SUSPECT on every run. The variable rides os.environ,
    so the hook's child processes inherit it."""
    import os
    path = tmp_path_factory.mktemp("workflow_state") / "workflow_state.json"
    prev = os.environ.get("WORKFLOW_STATE_OUT")
    os.environ["WORKFLOW_STATE_OUT"] = str(path)
    try:
        yield path
    finally:
        if prev is None:
            os.environ.pop("WORKFLOW_STATE_OUT", None)
        else:
            os.environ["WORKFLOW_STATE_OUT"] = prev


@pytest.fixture(autouse=True, scope="session")
def _engine_owner_word():
    """S6-B3358 (B3139q-r140): the engine refuses to start without the owner's
    recorded launch word (backtest/run_phase1a.py _owner_word_refusals), so a
    test session's engine runs carry one - the S6-B3337 ruling 'your rec
    approved', which the launch-path fixtures already cite (test_b2116,
    _b2159_ok_manifest), recorded in the real ledger the engine reads. It
    rides os.environ, so child processes inherit it; a pin that needs NO word
    removes it (monkeypatch.delenv or an explicit env). A word already set
    before the session - an operator's own - is left alone. The key is
    scripts/owner_word.ENV_KEY, which test_b3358 checks this value against."""
    import json
    import os
    key = "OWNER_WORD_JSON"
    prev = os.environ.get(key)
    if prev is None:
        os.environ[key] = json.dumps({"ticket": "S6-B3337",
                                      "verbatim": "your rec approved"})
    try:
        yield
    finally:
        if prev is None:
            os.environ.pop(key, None)


_CFG_SNAPSHOT = pytest.StashKey[dict]()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_setup(item):
    """S6-B3386 (B3139q-r162b): before ANY fixture of the test runs, snapshot
    backtest.config's module object and its module-level containers - the
    objects a module that imported them by value holds (exit_manager's
    CIRCUIT_BREAKERS and TRAILING_STOP). A wrapper, not a fixture, so no
    fixture order can put a monkeypatch outside the bracket."""
    from backtest.tests.config_disk import container_snapshot
    item.stash[_CFG_SNAPSHOT] = container_snapshot()
    return (yield)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item, nextitem):
    """S6-B3386 (B3139q-r162b, CHECKLIST #209): after EVERY finalizer -
    monkeypatch's restore included - the test must leave those objects where
    it found them. MEASURED three times (L330, L484, L1002): an in-process
    importlib.reload(backtest.config) rebinds them, the polluter passes, and
    test_bug_30 / test_bug_232 fail later in the full suite while passing
    alone. Here the POLLUTER fails, by name, and the objects are put back so
    no later test inherits the damage."""
    result = yield
    from backtest.tests.config_disk import rebound_names, restore_snapshot
    snap = item.stash.get(_CFG_SNAPSHOT, None)
    moved = rebound_names(snap)
    if moved:
        restore_snapshot(snap)
        shown = ", ".join(moved[:8]) + (" ..." if len(moved) > 8 else "")
        raise AssertionError(
            f"S6-B3386 / #209: {item.nodeid} left backtest.config rebound - "
            f"{shown} ({len(moved)}) are no longer the objects modules imported "
            "by value hold, so every later test that patches one fails while "
            "passing alone (L330, L484). An in-process importlib.reload("
            "backtest.config) does this: set attributes for the test "
            "(monkeypatch.setattr; scripts/config_knobs.applied in a script), "
            "read a committed value with config_disk.disk_value, or reload in a "
            "child process. The objects were put back - only this test fails.")
    return result
