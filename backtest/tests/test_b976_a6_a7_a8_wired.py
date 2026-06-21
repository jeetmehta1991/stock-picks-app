"""B976 A6+A7+A8 wiring tests (2026-06-21 Council 77 P1 Bucket A):
verify scripts/populate_all_dossiers.py wires dossier_self_test
(pre-flight), build_walk_verdict_ledger_v2 + stream_v_verify_reproducibility
(end-of-run) per same cadence as A9 b956 cron.

Closes B971 'c' classification for three orphan scripts.

Source-grep pins - does NOT execute full populate_all_dossiers (minutes).
"""
from __future__ import annotations

from pathlib import Path


def _read_populate_all_dossiers_source() -> str:
    repo = Path(__file__).resolve().parents[2]
    return (repo / "scripts" / "populate_all_dossiers.py").read_text(
        encoding="utf-8"
    )


# -----------------------------------------------------------------------------
# A6: dossier_self_test pre-flight
# -----------------------------------------------------------------------------


def test_b976_a6_populate_imports_dossier_self_test_main():
    src = _read_populate_all_dossiers_source()
    assert (
        "from scripts.dossier_self_test import main as _dossier_self_test_main"
        in src
    ), (
        "B976 A6 regression: populate_all_dossiers must import "
        "dossier_self_test main for pre-flight gate"
    )


def test_b976_a6_populate_invokes_dossier_self_test_main():
    src = _read_populate_all_dossiers_source()
    assert "_self_test_rc = _dossier_self_test_main()" in src, (
        "B976 A6 regression: populate_all_dossiers must invoke "
        "_dossier_self_test_main() as PRE-FLIGHT gate"
    )


def test_b976_a6_dossier_self_test_is_pre_flight_not_post():
    """The dossier self-test must run BEFORE list_strategies_for_dossier
    is called (pre-flight gate per Council 38 Outsider mandate)."""
    src = _read_populate_all_dossiers_source()
    pre_flight_idx = src.find("_self_test_rc = _dossier_self_test_main()")
    list_strategies_idx = src.find("strategies = list_strategies_for_dossier()")
    assert pre_flight_idx > 0 and list_strategies_idx > 0
    assert pre_flight_idx < list_strategies_idx, (
        "B976 A6 regression: dossier_self_test must run BEFORE "
        "list_strategies_for_dossier per Council 38 Outsider pre-flight mandate"
    )


# -----------------------------------------------------------------------------
# A8: build_walk_verdict_ledger_v2 end-of-run
# -----------------------------------------------------------------------------


def test_b976_a8_populate_imports_ledger_v2_main():
    src = _read_populate_all_dossiers_source()
    assert (
        "from scripts.build_walk_verdict_ledger_v2 import main as _ledger_v2_main"
        in src
    ), (
        "B976 A8 regression: populate_all_dossiers must import "
        "build_walk_verdict_ledger_v2 main for end-of-run refresh"
    )


def test_b976_a8_populate_invokes_ledger_v2_main():
    src = _read_populate_all_dossiers_source()
    assert "_ledger_v2_rc = _ledger_v2_main()" in src, (
        "B976 A8 regression: populate_all_dossiers must invoke "
        "_ledger_v2_main() as end-of-run refresh"
    )


# -----------------------------------------------------------------------------
# A7: stream_v_verify_reproducibility end-of-run
# -----------------------------------------------------------------------------


def test_b976_a7_populate_imports_stream_v_main():
    src = _read_populate_all_dossiers_source()
    assert (
        "from scripts.stream_v_verify_reproducibility import main as _stream_v_main"
        in src
    ), (
        "B976 A7 regression: populate_all_dossiers must import "
        "stream_v_verify_reproducibility main"
    )


def test_b976_a7_populate_invokes_stream_v_main():
    src = _read_populate_all_dossiers_source()
    assert "_stream_v_rc = _stream_v_main()" in src, (
        "B976 A7 regression: populate_all_dossiers must invoke "
        "_stream_v_main() as post-Stream-E regression check"
    )


def test_b976_a7_stream_v_runs_after_populate_loop():
    """Stream V verification must run AFTER the populate loop completes,
    not before (post-Stream-E regression per PATH 13.7)."""
    src = _read_populate_all_dossiers_source()
    stream_v_idx = src.find("_stream_v_rc = _stream_v_main()")
    populate_loop_end = src.find("Population COMPLETE")
    assert stream_v_idx > 0 and populate_loop_end > 0
    assert stream_v_idx > populate_loop_end, (
        "B976 A7 regression: Stream V must run AFTER populate loop "
        "completes (post-Stream-E regression check per PATH 13.7)"
    )


# -----------------------------------------------------------------------------
# Non-fatal contract for all three hooks
# -----------------------------------------------------------------------------


def test_b976_all_three_hooks_are_non_fatal():
    """All three new hooks (A6/A7/A8) must be wrapped in try/except
    so a failure does not abort populate_all_dossiers. Verifies the
    'failure is non-fatal' contract documented in each wiring block."""
    src = _read_populate_all_dossiers_source()
    needles = [
        "_self_test_rc = _dossier_self_test_main()",
        "_ledger_v2_rc = _ledger_v2_main()",
        "_stream_v_rc = _stream_v_main()",
    ]
    for needle in needles:
        idx = src.find(needle)
        assert idx > 0, f"hook missing: {needle}"
        preamble = src[max(0, idx - 600): idx]
        postamble = src[idx: idx + 800]
        assert "try:" in preamble, (
            f"B976 regression: {needle} must be inside try block "
            "(non-fatal contract)"
        )
        assert "except Exception" in postamble, (
            f"B976 regression: {needle} must catch Exception "
            "(non-fatal contract)"
        )
