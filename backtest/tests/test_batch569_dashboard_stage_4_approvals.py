"""Batch 569 (2026-06-03) -- Stage 4 step 4 of 4 per
PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md.

Source: owner directive 2026-06-03 "lets start as per workflow".

`scripts/build_dashboard_phase_1a.py` Batch 569 extension: surfaces the
Stage 4 approvals.json contents in the dashboard data payload so the
12-tab Phase 1A dashboard's Candidates tab can render approval counts +
class filters + per-row status without re-fetching approvals.json
client-side.

Pins:

  (1) builder accepts --approvals flag without crashing when path is
      empty (defaults to <optimizer-dir>/approvals.json)
  (2) when approvals.json exists, data.json contains `stage_4_approvals`
      with present=True + non-empty summary + rows_lite
  (3) rows_lite length matches approvals.summary.total (no rows dropped)
  (4) each rows_lite entry has the lite-schema keys
  (5) max_severity reflects the highest-severity conflict on the row
      (blocker > warning > info; empty when no conflicts)
  (6) when approvals.json is absent, payload contains
      stage_4_approvals.present=False (graceful no-data fallback)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
CAND_DIR = Path("C:/tmp/r4_optimization_candidates")
APPROVALS = CAND_DIR / "approvals.json"
TRADE_LOG_DIR = Path("C:/tmp/r4_final")
DASH_DATA = REPO / "dashboard_phase_1a" / "data.json"


def _have_inputs() -> bool:
    return APPROVALS.exists() and TRADE_LOG_DIR.exists()


pytestmark = pytest.mark.skipif(
    not _have_inputs(),
    reason="R4 cube outputs absent (run B566/B567/B568 first)",
)


REQUIRED_LITE_KEYS = {
    "candidate_id", "strategy", "change_class", "change_class_name",
    "status", "n_conflicts", "max_severity", "dimension_source",
}


@pytest.fixture(scope="module")
def built_payload():
    rc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "build_dashboard_phase_1a.py"),
            "--source",        str(TRADE_LOG_DIR),
            "--optimizer-dir", str(CAND_DIR),
        ],
        capture_output=True, text=True, timeout=180,
    )
    assert rc.returncode == 0, (
        f"builder exit {rc.returncode}; stderr:\n{rc.stderr[-3000:]}"
    )
    return json.loads(DASH_DATA.read_text(encoding="utf-8"))


def test_batch569_builder_runs(built_payload):
    """Pin (1)."""
    assert isinstance(built_payload, dict)


def test_batch569_stage_4_present(built_payload):
    """Pin (2)."""
    sa = built_payload.get("stage_4_approvals")
    assert sa is not None, "stage_4_approvals key missing from payload"
    assert sa.get("present") is True, (
        f"stage_4_approvals.present should be True when approvals.json "
        f"exists; got {sa.get('present')}"
    )
    assert sa.get("summary", {}).get("total", 0) > 0
    assert len(sa.get("rows_lite", [])) > 0


def test_batch569_rows_lite_complete(built_payload):
    """Pin (3) - rows_lite should match summary.total exactly. No row
    silently dropped."""
    sa = built_payload["stage_4_approvals"]
    assert len(sa["rows_lite"]) == sa["summary"]["total"]


def test_batch569_rows_lite_schema(built_payload):
    """Pin (4)."""
    sa = built_payload["stage_4_approvals"]
    for r in sa["rows_lite"]:
        missing = REQUIRED_LITE_KEYS - set(r.keys())
        assert not missing, (
            f"rows_lite entry {r.get('candidate_id')} missing keys: {missing}"
        )


def test_batch569_max_severity_correctness(built_payload):
    """Pin (5) - max_severity = max severity across conflicts on the row.
    Cross-validate against approvals.json source of truth."""
    sa = built_payload["stage_4_approvals"]
    source = json.loads(APPROVALS.read_text(encoding="utf-8"))
    by_id = {r["candidate_id"]: r for r in source["approvals"]}
    sev_rank = {"blocker": 3, "warning": 2, "info": 1, "": 0}
    for lite in sa["rows_lite"]:
        full_row = by_id[lite["candidate_id"]]
        confs = full_row.get("conflicts", []) or []
        if not confs:
            assert lite["max_severity"] == "", (
                f"row {lite['candidate_id']} has no conflicts but "
                f"max_severity = {lite['max_severity']!r}"
            )
            continue
        actual_max = max(confs, key=lambda c: sev_rank.get(c["severity"], 0))["severity"]
        assert lite["max_severity"] == actual_max, (
            f"row {lite['candidate_id']} max_severity mismatch: "
            f"lite={lite['max_severity']}, actual={actual_max}"
        )


def test_batch569_no_data_graceful(tmp_path, monkeypatch):
    """Pin (6) - when approvals.json is absent, load_stage_4_approvals()
    returns present=False (graceful fallback).

    NOTE: tests the helper in-process; does NOT shell out to the builder.
    Earlier draft of this test ran the builder subprocess against a
    pytest tmp_path, which silently clobbered the real R4 dashboard
    data.json (builder hardcodes its output path). Fixed by importing
    + monkeypatching APPROVALS_PATH instead."""
    import importlib
    fake_opt = tmp_path / "opt"
    fake_opt.mkdir()
    fake_approvals = fake_opt / "approvals.json"
    # fake_approvals deliberately does NOT exist
    # Import the builder module and monkeypatch its APPROVALS_PATH
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        mod = importlib.import_module("build_dashboard_phase_1a")
        monkeypatch.setattr(mod, "APPROVALS_PATH", fake_approvals)
        out = mod.load_stage_4_approvals()
    finally:
        sys.path.pop(0)
    assert out["present"] is False, (
        f"absent approvals.json should -> present=False; got {out}"
    )
    assert out["rows_lite"] == []
    assert out["summary"] == {}
