"""Batch 566 (2026-06-03) -- Stage 4 step 1 of 4 per
PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md.

Source: per CHECKLIST #77, owner directive 2026-06-03 "lets start as
per PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md".

`scripts/extract_proposed_changes.py` parses per-strategy candidate
JSONs from a cube-optimizer output dir + producer_zero_audit.json,
emits atomic rows by the 6 change classes (workflow lines 326-336).

Pins:

  (1) extractor exits 0 against the R4 cube optimizer outputs
  (2) row count is non-zero
  (3) ALL six valid change_class values (1..6) are integers in 1..6
  (4) every row has the required keys
  (5) candidate_id is stable across reruns (idempotent)
  (6) Class 5 (REGIME_AFFINITY) is preserved (workflow line 337: auto-DEFERRED
      in Phase 1A-beta, but it must still be EXTRACTED for the approvals
      ledger so transition to Phase 1B-alpha unblocks it)
  (7) Class 6 (DEPRECATION) candidates come ONLY from
      PRODUCER_LAYER_ZERO_LIKELY bucket (workflow line 335 empirical-only
      gate; COMPOUND_RESTRICTIVE + SKIPPED_AT_ENGINE buckets get other
      change classes)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
CAND_DIR = Path("C:/tmp/r4_optimization_candidates")
OUT_FILE = CAND_DIR / "r4_proposed_changes.json"

VALID_CLASSES = {1, 2, 3, 4, 5, 6}
REQUIRED_KEYS = {
    "candidate_id",
    "strategy",
    "change_class",
    "change_class_name",
    "dimension_source",
    "change_detail",
    "structured",
    "rationale_metrics",
    "config_touch_point",
}


def _have_r4_cube_outputs() -> bool:
    """Skip these tests gracefully on machines without the R4 cube
    optimizer output dir (e.g. CI runners, fresh clones)."""
    return CAND_DIR.exists() and (
        CAND_DIR / "producer_zero_post_cube_audit.json"
    ).exists()


pytestmark = pytest.mark.skipif(
    not _have_r4_cube_outputs(),
    reason="R4 cube optimizer outputs absent (C:/tmp/r4_optimization_candidates)",
)


@pytest.fixture(scope="module")
def proposed_changes():
    """Run the extractor and return the parsed rows."""
    rc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "extract_proposed_changes.py"),
            "--input-dir", str(CAND_DIR),
            "--output",    str(OUT_FILE),
        ],
        capture_output=True, text=True, timeout=60,
    )
    assert rc.returncode == 0, (
        f"extractor exit code {rc.returncode}; stderr:\n{rc.stderr}"
    )
    assert OUT_FILE.exists(), f"extractor did not write {OUT_FILE}"
    return json.loads(OUT_FILE.read_text(encoding="utf-8"))


def test_batch566_extractor_exit_zero(proposed_changes):
    """Pin (1): extractor succeeds end-to-end."""
    assert isinstance(proposed_changes, list)


def test_batch566_row_count_nonzero(proposed_changes):
    """Pin (2): at least some atomic rows surfaced. R4 has 351; we use
    >100 as the regression guard (loose, so adding/removing 50 rows
    doesn't trip the pin)."""
    assert len(proposed_changes) > 100, (
        f"expected >100 atomic rows; got {len(proposed_changes)}. "
        f"If extractor logic shrank legitimately, update this pin."
    )


def test_batch566_change_class_valid(proposed_changes):
    """Pin (3): every row's change_class is integer in 1..6."""
    bad = [
        r for r in proposed_changes
        if not (isinstance(r["change_class"], int) and r["change_class"] in VALID_CLASSES)
    ]
    assert not bad, f"{len(bad)} rows have invalid change_class; first: {bad[:1]}"


def test_batch566_required_keys_present(proposed_changes):
    """Pin (4): every row has the required keys."""
    for r in proposed_changes:
        missing = REQUIRED_KEYS - set(r.keys())
        assert not missing, (
            f"row {r.get('candidate_id')} missing keys: {missing}"
        )


def test_batch566_candidate_id_idempotent(proposed_changes):
    """Pin (5): rerunning extractor produces the same candidate_id set
    (no Date.now()/uuid in the id derivation)."""
    rc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "extract_proposed_changes.py"),
            "--input-dir", str(CAND_DIR),
            "--output",    str(OUT_FILE.with_name("r4_proposed_changes_rerun.json")),
        ],
        capture_output=True, text=True, timeout=60,
    )
    assert rc.returncode == 0
    rerun = json.loads(
        OUT_FILE.with_name("r4_proposed_changes_rerun.json").read_text(encoding="utf-8")
    )
    ids_a = {r["candidate_id"] for r in proposed_changes}
    ids_b = {r["candidate_id"] for r in rerun}
    assert ids_a == ids_b, (
        f"candidate_id set drifted between runs; "
        f"a-only: {(ids_a - ids_b)}, b-only: {(ids_b - ids_a)}"
    )


def test_batch566_class5_preserved_for_1b_alpha(proposed_changes):
    """Pin (6): Class 5 REGIME_AFFINITY rows exist + carry pass_regimes
    structured field. Workflow line 337: they get DEFERRED in step 2,
    but extraction must preserve them so Phase 1B-alpha transition can
    auto-unblock."""
    class5 = [r for r in proposed_changes if r["change_class"] == 5]
    # R4 had 1 Class 5 (pead_long_high_yoy_growth_only); future R-iterations
    # may add more, so allow >=1
    assert class5, "expected at least one Class 5 row"
    for r in class5:
        assert r["dimension_source"] == "dimension_c_regime"
        # Structured should have either pass_regimes or per_regime_verdicts
        s = r.get("structured", {})
        assert "pass_regimes" in s or "per_regime_verdicts" in s


def test_batch566_class6_only_from_plzl(proposed_changes):
    """Pin (7): Class 6 ROSTER_DEPRECATION rows come ONLY from
    PRODUCER_LAYER_ZERO_LIKELY (workflow line 335 empirical-only gate).
    Compound-restrictive + skipped-at-engine strategies get different
    change classes - they're not automatic Class 6 candidates."""
    pz = json.loads(
        (CAND_DIR / "producer_zero_post_cube_audit.json").read_text(encoding="utf-8")
    )
    plzl_set = set(pz["buckets"].get("PRODUCER_LAYER_ZERO_LIKELY", []))
    cr_set = set(pz["buckets"].get("COMPOUND_RESTRICTIVE", []))
    sae_set = set(pz["buckets"].get("SKIPPED_AT_ENGINE", []))
    class6_strats = {r["strategy"] for r in proposed_changes if r["change_class"] == 6}
    assert class6_strats == plzl_set, (
        f"Class 6 strategies should match PLZL bucket exactly. "
        f"Diff: Class6-only={class6_strats - plzl_set}; "
        f"PLZL-only={plzl_set - class6_strats}"
    )
    # And NOT include CR/SAE strats automatically
    leaked = (class6_strats & cr_set) | (class6_strats & sae_set)
    assert not leaked, (
        f"Class 6 leaked CR/SAE strategies that should have other classes: {leaked}"
    )
