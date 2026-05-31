"""Batch 523 (2026-05-31) -- VERIFICATION_MATRIX regen drift-pin.

Source: per CHECKLIST #77 + EXECUTION_QUEUE.md item AU3
(`5-pattern-audit-verification-matrix-scripts-layer-extension`).
Builds on Batch 459 (matrix-builder dual-source coverage merge).

Why this batch ships:
  Batch 459 added the scripts/* layer to the matrix scan + the
  merge of multiple `coverage_report_*.json` files. It did NOT
  trigger a regen. Batch 523 captures the optimizer canonical run
  (`python -m coverage run scripts/optimize_strategies_from_cube.py
  --input-dir output_batch395_final`) into a local-only
  `coverage_report_optimizer.json`, runs
  `python scripts/build_verification_matrix.py` to merge both
  reports, and commits the regenerated matrix.

This test pins:

  (1) verification_matrix.json schema (top-level `items` dict + each
      item has `kind` + `engine` + `evidence`)
  (2) BUG-018 stays FUNC-DEAD (the optimizer canonical run did NOT
      flip it to YES; the Bonferroni call site is reached in the
      optimizer driver but the specific guarded branch isn't --
      this is the known cube-multiple-comparison correction edge)
  (3) total item count >= 700 (we expect ~736 visible after Batch
      499 dashboard refresh; drift below 700 means dashboard data.js
      lost rows OR matrix builder dropped a tier)
  (4) engine status distribution is non-degenerate (must have at
      least one of each: YES, FUNC-DEAD, NO; a regen that wipes
      one of these is almost certainly a builder regression)
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent
MATRIX_JSON = REPO / "verification_matrix.json"
MATRIX_MD = REPO / "VERIFICATION_MATRIX.md"


@pytest.fixture(scope="module")
def matrix() -> dict:
    if not MATRIX_JSON.exists():
        pytest.skip(
            f"verification_matrix.json missing -- regen via "
            f"`python scripts/build_verification_matrix.py`."
        )
    return json.loads(MATRIX_JSON.read_text(encoding="utf-8"))


def test_batch523_verification_matrix_md_exists():
    assert MATRIX_MD.exists(), (
        f"VERIFICATION_MATRIX.md absent at {MATRIX_MD}. Regen via "
        f"`python scripts/build_verification_matrix.py`."
    )
    # MD shouldn't be empty
    assert MATRIX_MD.stat().st_size > 1000, (
        f"VERIFICATION_MATRIX.md is suspiciously small "
        f"({MATRIX_MD.stat().st_size} bytes) -- regen probably crashed."
    )


def test_batch523_matrix_json_schema(matrix):
    assert isinstance(matrix, dict)
    assert "items" in matrix and "generated_at" in matrix
    items = matrix["items"]
    assert isinstance(items, dict)
    assert len(items) >= 700, (
        f"Matrix item count = {len(items)} < 700 floor. Either dashboard "
        f"data.js shrank (improbable) or builder dropped a tier. "
        f"Re-check builder + dashboard before bumping the floor."
    )
    sample_key = next(iter(items))
    sample = items[sample_key]
    required_fields = {"kind", "engine", "evidence"}
    assert required_fields.issubset(sample.keys()), (
        f"Schema regression at {sample_key}: missing "
        f"{required_fields - set(sample.keys())}"
    )


def test_batch523_bug_018_stays_func_dead_after_optimizer_coverage(matrix):
    """BUG-018 (Bonferroni multiple-comparison guard) was the canonical
    AU10 example of a coverage-source-gap masquerading as a wiring-gap.
    Batch 523 captured the optimizer canonical run -- if Bonferroni
    actually executes there, BUG-018 should flip YES; if not, FUNC-DEAD
    persists for a deeper reason (the specific branch isn't taken in
    the small-cube optimization run). Either outcome is informative.
    """
    items = matrix["items"]
    if "BUG-018" not in items:
        pytest.skip("BUG-018 not in matrix (dashboard may have hidden it)")
    eng = items["BUG-018"]["engine"]
    # Pin to current observed state. Flipping this test is the right
    # signal that the optimizer run now exercises the Bonferroni branch.
    assert eng == "FUNC-DEAD", (
        f"BUG-018 engine status changed: {eng} (was FUNC-DEAD). If "
        f"intentional (e.g. optimizer canonical run now reaches the "
        f"Bonferroni branch after a fix), update this pin + close "
        f"AU10 follow-on in EXECUTION_QUEUE.md."
    )


def test_batch523_engine_distribution_non_degenerate(matrix):
    """Each canonical engine status must have at least one item.
    A regen that wipes any of these is almost certainly a builder
    regression -- the verdict lattice should always populate."""
    eng_counts = Counter(v["engine"] for v in matrix["items"].values())
    must_have = {"YES", "FUNC-DEAD", "NO", "N/A"}
    missing = [s for s in must_have if eng_counts.get(s, 0) == 0]
    assert not missing, (
        f"Engine status(es) missing from regen: {missing}. "
        f"Distribution: {dict(eng_counts)}"
    )


def test_batch523_engine_status_lattice_complete(matrix):
    """The engine-status lattice is fixed (Batch 466 STATUS_INTERPRETATION).
    Surface any value that escapes the allowed set so a builder change
    that introduces a new label fires a test rather than silently
    contaminating downstream consumers."""
    allowed = {
        "YES", "LAZY-WIRED", "PARTIAL-ORPHAN", "FUNC-DEAD",
        "NO", "DECLARED-ONLY", "N/A",
    }
    actual = set(v["engine"] for v in matrix["items"].values())
    illegal = actual - allowed
    assert not illegal, (
        f"Matrix contains unknown engine status(es): {illegal}. "
        f"Either extend STATUS_INTERPRETATION (per Batch 466) + "
        f"this allow-list, OR fix the builder to only emit canonical "
        f"values."
    )


def test_batch523_coverage_report_optimizer_gitignored():
    """The per-canonical-run coverage JSONs are local-only by design
    (see Batch 459 + .gitignore comment). Regression guard: if a future
    commit accidentally adds coverage_report_*.json patterns to the
    repo, this fires."""
    gi = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert "coverage_report_*.json" in gi, (
        f"Batch 523 .gitignore guard for coverage_report_*.json "
        f"missing. Re-add the pattern -- raw coverage JSONs bloat "
        f"the repo (~3MB each)."
    )
    assert ".coverage_*" in gi, (
        f"Batch 523 .gitignore guard for .coverage_* missing. "
        f"Re-add to keep per-canonical-run coverage db files local."
    )
