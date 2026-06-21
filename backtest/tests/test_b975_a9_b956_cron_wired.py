"""B975 A9 wiring test (2026-06-21 Council 77 P1 Bucket A item A9):
verify scripts/populate_all_dossiers.py wires the b956 findings-triage
queue builder at end-of-run.

Closes B971 'c' classification (orphan script needs wiring) for
b956_build_findings_triage_queue.py.

Source-grep pin only - does NOT execute the full populate_all_dossiers
because that takes minutes. Source pin catches regression if a future
refactor silently removes the call.
"""
from __future__ import annotations

from pathlib import Path


def test_b975_a9_populate_all_dossiers_imports_b956_main():
    """populate_all_dossiers.py end-of-run hook must import b956 main."""
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "scripts" / "populate_all_dossiers.py").read_text(
        encoding="utf-8"
    )
    assert (
        "from scripts.b956_build_findings_triage_queue import main as _b956_main"
        in src
    ), (
        "B975 A9 regression: populate_all_dossiers must import b956 main "
        "for end-of-run triage queue refresh"
    )


def test_b975_a9_populate_all_dossiers_invokes_b956_main():
    """populate_all_dossiers.py must invoke _b956_main() after final stats."""
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "scripts" / "populate_all_dossiers.py").read_text(
        encoding="utf-8"
    )
    assert "_b956_rc = _b956_main()" in src, (
        "B975 A9 regression: populate_all_dossiers must invoke _b956_main() "
        "as the end-of-run cron hook"
    )


def test_b975_a9_b956_failure_is_non_fatal():
    """The end-of-run b956 hook must be wrapped in try/except so a triage
    queue builder failure does not fail the full-roster population run."""
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "scripts" / "populate_all_dossiers.py").read_text(
        encoding="utf-8"
    )
    # Find the b956 invocation block
    needle = "_b956_rc = _b956_main()"
    idx = src.find(needle)
    assert idx > 0, "b956 invocation not found"
    # Look backward for the enclosing try: within 500 chars
    preamble = src[max(0, idx - 500): idx]
    assert "try:" in preamble, (
        "B975 A9 regression: b956 cron call must be inside a try/except "
        "block to remain non-fatal per Council 77 wiring contract"
    )
    # Look forward for the except: within 500 chars
    postamble = src[idx: idx + 800]
    assert "except Exception" in postamble, (
        "B975 A9 regression: b956 cron call must catch Exception for "
        "non-fatal degraded operation"
    )
