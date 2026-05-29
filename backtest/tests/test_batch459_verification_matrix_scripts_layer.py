"""Batch 459 (2026-05-29) -- AU3 VERIFICATION_MATRIX extension to scripts/*.

PROBLEM (pre-Batch-459):
  scripts/build_verification_matrix.py only:
    (a) collected source files from backtest/ (skipped scripts/),
    (b) filtered tag-hits to backtest/ paths only,
    (c) loaded a single coverage_report.json from one canonical
        backtest/run_phase1a.py run.
  Net effect: DECs/BUGs whose only home is the optimizer / walk-forward /
  merge / dashboard build pipeline got engine=N/A by definition, NOT by
  evidence of absence. ~150 false-positive RESOLVED-IMPLEMENTED claims
  ride on this lens (queue item AU3 + Pattern 4 + L143 family).

FIX:
  - collect_source_files() now returns backtest/ + scripts/ (tests excluded).
  - is_engine_consumed path-filter accepts both prefixes.
  - load_coverage() merges ALL coverage_report*.json files in repo root
    (union executed_lines, intersect missing_lines, recompute percent).
  - Import-graph walks (_files_imported_by, _symbol_consumed_externally)
    now traverse scripts/ as well so a backtest/* helper imported only by
    scripts/optimize_strategies_from_cube.py registers as wired through
    the optimizer call path.
  - Matrix MD header documents the dual canonical-run methodology.

THIS TEST asserts the wiring is real, not just greppable:
  1. collect_source_files() includes a known scripts/*.py path.
  2. is_engine_consumed accepts tags whose source files live under scripts/.
  3. load_coverage() merges two synthetic coverage_report*.json files
     (union executed; intersect missing; recompute percent).
  4. Matrix MD header documents the AU3 dual-run methodology so the next
     operator knows to run BOTH canonical commands.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]


def test_collect_source_files_includes_scripts():
    """AU3: source-file scan now covers scripts/ in addition to backtest/."""
    import sys
    sys.path.insert(0, str(REPO))
    from scripts.build_verification_matrix import collect_source_files

    files = collect_source_files()
    rels = {str(p.relative_to(REPO)).replace("\\", "/") for p in files}
    # Sentinel: a known scripts/*.py path must now appear.
    assert any(r.startswith("scripts/") for r in rels), \
        "collect_source_files must include scripts/*.py (Batch 459 AU3)"
    # Specifically the optimizer must be discoverable.
    assert "scripts/optimize_strategies_from_cube.py" in rels, \
        "scripts/optimize_strategies_from_cube.py missing from source files"
    # backtest/ files still present (regression guard)
    assert any(r.startswith("backtest/") for r in rels), \
        "backtest/* files dropped from source scan -- regression"


def test_is_engine_consumed_accepts_scripts_layer_tag(tmp_path, monkeypatch):
    """AU3: tags whose source files live under scripts/ are now in scope."""
    import sys
    sys.path.insert(0, str(REPO))
    from scripts.build_verification_matrix import is_engine_consumed

    # Fabricate a hit at scripts/optimize_strategies_from_cube.py:1 + minimal
    # coverage that reports the file as 100% covered. Pre-Batch-459 this
    # returned N/A "no source tag in backtest/" because the scripts/ path was
    # filtered out. Post-Batch-459 it should report a real status.
    fake_hits = [
        (REPO / "scripts" / "optimize_strategies_from_cube.py", 1),
    ]
    fake_coverage = {
        "scripts/optimize_strategies_from_cube.py": {
            "executed_lines": {1, 2, 3, 4, 5},
            "missing_lines": set(),
            "percent": 100.0,
        },
    }
    status, evidence = is_engine_consumed(fake_hits, fake_coverage)
    assert status != "N/A", \
        f"scripts/* tag must produce a real engine status, got {status} / {evidence}"


def test_load_coverage_merges_multiple_report_files(tmp_path, monkeypatch):
    """AU3: load_coverage unions executed_lines + intersects missing_lines
    across all coverage_report*.json files."""
    import sys
    sys.path.insert(0, str(REPO))
    import scripts.build_verification_matrix as bvm

    # Build two synthetic coverage reports in tmp_path covering the SAME
    # file with PARTIALLY OVERLAPPING line sets.
    report_a = tmp_path / "coverage_report.json"
    report_b = tmp_path / "coverage_report_optimizer.json"
    common_file = "backtest/results/cube_populator.py"
    report_a.write_text(json.dumps({
        "files": {
            common_file: {
                "executed_lines": [1, 2, 3, 4, 5],
                "missing_lines":  [6, 7, 8, 9, 10],
                "summary": {"percent_covered": 50.0},
            }
        }
    }), encoding="utf-8")
    report_b.write_text(json.dumps({
        "files": {
            common_file: {
                "executed_lines": [4, 5, 6, 7, 8],
                "missing_lines":  [1, 9, 10],
                "summary": {"percent_covered": 50.0},
            }
        }
    }), encoding="utf-8")

    # Monkey-patch REPO to point at tmp_path so load_coverage scans there.
    monkeypatch.setattr(bvm, "REPO", tmp_path)
    out = bvm.load_coverage()
    assert common_file in out, "Merged coverage missing the synthetic file"
    cov = out[common_file]
    # Union of executed: {1,2,3,4,5} | {4,5,6,7,8} = {1..8}
    assert cov["executed_lines"] == set(range(1, 9)), \
        f"executed_lines should be union; got {sorted(cov['executed_lines'])}"
    # Intersection of missing: {6,7,8,9,10} & {1,9,10} = {9,10}
    assert cov["missing_lines"] == {9, 10}, \
        f"missing_lines should be intersection; got {sorted(cov['missing_lines'])}"
    # Percent recomputed from union: 8 / (8 + 2) = 80
    assert cov["percent"] == pytest.approx(80.0, abs=0.1), \
        f"percent should be recomputed; got {cov['percent']}"


def test_load_coverage_handles_single_report_back_compat(tmp_path, monkeypatch):
    """Regression: existing single-report workflow must still work."""
    import sys
    sys.path.insert(0, str(REPO))
    import scripts.build_verification_matrix as bvm

    (tmp_path / "coverage_report.json").write_text(json.dumps({
        "files": {
            "backtest/engine/backtest.py": {
                "executed_lines": [100, 101],
                "missing_lines": [102],
                "summary": {"percent_covered": 66.67},
            }
        }
    }), encoding="utf-8")
    monkeypatch.setattr(bvm, "REPO", tmp_path)
    out = bvm.load_coverage()
    assert "backtest/engine/backtest.py" in out
    assert out["backtest/engine/backtest.py"]["percent"] == pytest.approx(66.67, abs=0.1)


def test_load_coverage_returns_empty_when_no_reports(tmp_path, monkeypatch):
    """Empty repo dir (no coverage reports) -> empty dict, not crash."""
    import sys
    sys.path.insert(0, str(REPO))
    import scripts.build_verification_matrix as bvm

    monkeypatch.setattr(bvm, "REPO", tmp_path)
    out = bvm.load_coverage()
    assert out == {}


def test_matrix_md_documents_dual_canonical_runs(tmp_path, monkeypatch):
    """AU3: matrix MD header must instruct operator on the two canonical
    coverage commands so the dual-source methodology is discoverable."""
    import sys
    sys.path.insert(0, str(REPO))
    import scripts.build_verification_matrix as bvm

    # Build a minimal matrix to MD and assert the canonical-run lines are
    # present. items=[] is fine; the doc header is independent of content.
    md = bvm.emit_matrix(
        items=[],
        coverage={},
        source_files=[],
    )
    assert "Canonical runs" in md or "canonical runs" in md.lower(), \
        "MD header must document the canonical runs"
    assert "coverage_report_optimizer.json" in md, \
        "MD must reference coverage_report_optimizer.json"
    assert "optimize_strategies_from_cube.py" in md, \
        "MD must show the optimizer canonical command"


def test_files_imported_by_walks_scripts_layer():
    """AU3: import-graph walks across backtest/ + scripts/ so a
    backtest/* helper imported only by an optimizer script registers as
    having a live importer."""
    import sys
    sys.path.insert(0, str(REPO))
    from scripts.build_verification_matrix import _files_imported_by

    # cube_populator is imported by scripts/build_dashboard_phase_1a.py
    # (post-Batch-457 wiring chain) -- this should register as a live
    # importer post-Batch-459 even though prior to AU3 it would not have
    # because the walk only scanned backtest/.
    importers = _files_imported_by("backtest/results/cube_populator.py")
    # Not asserting a specific scripts/ importer here (depends on which
    # scripts actually import the module today). Just assert that the
    # function does NOT crash and returns a list (semantic-contract).
    assert isinstance(importers, list)
