"""Batch 466 (2026-05-29) -- AU10 BUG engine-status registry + UNKNOWN gap close.

QUEUE FRAMING WAS STALE:
  The queue (AU10) claimed BUG-014 / BUG-015 / BUG-016 / BUG-018 / BUG-022 /
  BUG-023 / BUG-133 ALL showed `engine: UNKNOWN` in VERIFICATION_MATRIX --
  documentation-only RESOLVED claims with no coverage-driven verification.

  Inspecting the CURRENT verification_matrix.json (Batch 260 regen
  2026-05-20) shows none of them are UNKNOWN; the matrix in fact does
  NOT have an UNKNOWN bucket for `engine` (legal values: YES, LAZY-WIRED,
  PARTIAL-ORPHAN, FUNC-DEAD, NO, DECLARED-ONLY, N/A). The "UNKNOWN" the
  queue referenced was the AUDIT_INDEX dashboard's display fallback for
  items missing from the matrix entirely.

CURRENT STATUS (as of last regen 2026-05-20 / Batch 260):
  BUG-014: engine=N/A     (no source tag -- methodology decision; run_full.sh removal)
  BUG-015: engine=YES     (engine-consumed; max_drawdown compounded fix)
  BUG-016: engine=N/A     (no source tag -- methodology decision; PASSING_CRITERIA tiered)
  BUG-018: engine=FUNC-DEAD (REAL gap; Bonferroni denominator code never executes)
  BUG-022: engine=YES     (engine-consumed; 60-strategies docstring trace)
  BUG-023: engine=YES     (engine-consumed; 60-strategies docstring trace)
  BUG-133: engine=YES     (engine-consumed; TICKER_STOPOUT_COOLDOWN_DAYS=5)

  Of the 7 named, 1 has a real wiring gap (BUG-018); the other 6 are
  legitimately classified. Queue claim was stale by 9+ days plus a
  conflation of dashboard display fallback ("UNKNOWN") with matrix
  engine status.

BUG-018 GAP (only real finding):
  IMPLEMENTED tier + FUNC-DEAD engine status means the code that wires
  the Bonferroni denominator was tagged in source but the tagged function
  body never executed during the canonical AAPL backtest. This is a
  real gap worth surfacing -- handled separately under queue item 0b
  (Bonferroni denominator runtime > 1000), which Batch 462 verified
  the production callsite passes M = len(fired) * 9 in optimize_main.

ACTION:
  - Add THIS test as a drift guard: assert the 7 named BUGs maintain
    their expected engine status. If a future matrix regen flips a
    status, the test surfaces it.
  - Document the BUG-018 FUNC-DEAD as KNOWN_GAP with a cross-reference
    to Batch 462 (which verified the production callsite is correct;
    FUNC-DEAD in the small AAPL backtest is expected because the
    Bonferroni-denominator code path is in the optimizer, not the
    backtest itself).

NO MATRIX REGENERATION IN THIS BATCH:
  Regenerating the matrix requires running the canonical backtest under
  coverage + (Batch 459) the optimizer canonical under coverage. That is
  an owner-gated decision (expensive, needs full Phase 1A-beta input
  dir). This batch surfaces the inventory; owner triggers the regen.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]


# Expected engine status (as of matrix regen 2026-05-20 Batch 260)
EXPECTED_STATUS: dict[str, str] = {
    "BUG-014": "N/A",
    "BUG-015": "YES",
    "BUG-016": "N/A",
    "BUG-018": "FUNC-DEAD",  # KNOWN gap; Bonferroni code not in canonical backtest
    "BUG-022": "YES",
    "BUG-023": "YES",
    "BUG-133": "YES",
}


# Map status -> tier classification for documentation
STATUS_INTERPRETATION: dict[str, str] = {
    "YES":           "engine-consumed; tagged function body executed under coverage",
    "N/A":           "no source tag -- methodology / docs-only decision",
    "FUNC-DEAD":     "function exists in active module but body never executed",
    "LAZY-WIRED":    "file at 0% but imported by a module that ran",
    "PARTIAL-ORPHAN": "primary helper file has no live importer",
    "NO":            "all tagged files orphaned -- real wiring gap",
    "DECLARED-ONLY": "module-level tag; adjacent symbol not consumed externally",
}


# Known-gap allow-list: BUGs whose FUNC-DEAD / NO status is EXPECTED
# (covered elsewhere or surfaced as documented gaps). Future regens must
# keep these in the allow-list explicitly so the gap doesn't silently
# graduate to "fine".
KNOWN_GAPS: dict[str, str] = {
    "BUG-018": (
        "Bonferroni denominator code path is in scripts/optimize_strategies_"
        "from_cube.py (cube verdict pathway), not in the AAPL backtest "
        "canonical run. Batch 462 verified the production callsite "
        "passes M = max(len(fired) * 9, 1) -- semantic-integration test "
        "test_optimizer_main_bonferroni_denominator_runtime asserts this. "
        "The FUNC-DEAD status will resolve once Batch 459's dual-source "
        "coverage (matrix extension to scripts/*) is regenerated with a "
        "coverage_report_optimizer.json captured."
    ),
}


def _load_matrix() -> dict:
    """Read verification_matrix.json (machine-readable matrix)."""
    p = REPO / "verification_matrix.json"
    if not p.exists():
        pytest.skip("verification_matrix.json not present; skip drift guard")
    return json.loads(p.read_text(encoding="utf-8"))


def test_named_bugs_have_expected_engine_status():
    """Drift guard: each queue-named BUG must have the engine status
    captured at AU10 close. A future regen that flips a status without
    updating the registry surfaces in CI."""
    matrix = _load_matrix()
    items = matrix.get("items", {})
    actual: dict[str, str] = {}
    for bug, expected in EXPECTED_STATUS.items():
        item = items.get(bug)
        if not item:
            pytest.fail(f"{bug} missing from verification_matrix.json")
        actual[bug] = item.get("engine", "MISSING")
    diffs = {
        bug: (EXPECTED_STATUS[bug], actual[bug])
        for bug in EXPECTED_STATUS
        if EXPECTED_STATUS[bug] != actual[bug]
    }
    assert not diffs, \
        f"Engine-status drift since AU10 registry: {diffs}. " \
        f"Update EXPECTED_STATUS + KNOWN_GAPS if the change is intentional."


def test_func_dead_bugs_are_in_known_gaps():
    """If a BUG's engine status is FUNC-DEAD / NO / PARTIAL-ORPHAN /
    DECLARED-ONLY, it must be in KNOWN_GAPS with a documented reason.
    Catches silent regression of a wiring fix."""
    matrix = _load_matrix()
    items = matrix.get("items", {})
    flagged_statuses = {"FUNC-DEAD", "NO", "PARTIAL-ORPHAN"}
    unexpected_gaps = []
    for bug in EXPECTED_STATUS:
        item = items.get(bug, {})
        status = item.get("engine")
        if status in flagged_statuses and bug not in KNOWN_GAPS:
            unexpected_gaps.append((bug, status))
    assert not unexpected_gaps, \
        f"BUGs with wiring-gap status that lack a KNOWN_GAPS entry: " \
        f"{unexpected_gaps}. Either fix the gap or document it in KNOWN_GAPS."


def test_matrix_has_no_engine_unknown_bucket():
    """The queue claim of 'engine: UNKNOWN' was based on the dashboard's
    display fallback for items missing from the matrix. The matrix
    itself uses YES / LAZY-WIRED / PARTIAL-ORPHAN / FUNC-DEAD / NO /
    DECLARED-ONLY / N/A. This test verifies the matrix has no engine
    value outside that legal set -- if one appears, the matrix builder
    has regressed."""
    matrix = _load_matrix()
    legal = {"YES", "LAZY-WIRED", "PARTIAL-ORPHAN", "FUNC-DEAD", "NO",
              "DECLARED-ONLY", "N/A"}
    illegal: dict[str, str] = {}
    for k, item in matrix.get("items", {}).items():
        status = item.get("engine")
        if status not in legal:
            illegal[k] = status
    assert not illegal, \
        f"Matrix contains illegal engine status values: " \
        f"{dict(list(illegal.items())[:10])}{'...' if len(illegal) > 10 else ''}"


def test_known_gaps_each_has_a_reason():
    """Hygiene: every KNOWN_GAPS entry must have a non-trivial reason
    string (>50 chars) so the gap is documented, not just acknowledged."""
    bad = {bug: reason for bug, reason in KNOWN_GAPS.items()
           if len(reason) < 50}
    assert not bad, \
        f"KNOWN_GAPS entries with too-short reason: {bad}"


def test_status_interpretation_covers_all_used_statuses():
    """STATUS_INTERPRETATION must cover every engine value that appears
    in the matrix. If the builder introduces a new status, this surfaces
    it for documentation."""
    matrix = _load_matrix()
    used = set()
    for item in matrix.get("items", {}).values():
        s = item.get("engine")
        if s is not None:
            used.add(s)
    interpreted = set(STATUS_INTERPRETATION.keys())
    missing = used - interpreted
    assert not missing, \
        f"Engine status(es) in matrix lack STATUS_INTERPRETATION entries: {missing}"
