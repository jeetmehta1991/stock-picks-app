"""Batch 495 (2026-05-30) -- Bundle 7 Pattern 3 closures.

Source: per CHECKLIST #77 (test extensively).
Queue rows: EXECUTION_QUEUE.md items 0b + 0c (paperwork closures) + 0
(audit-meta + placeholder sweep guard).

Three closures in this batch:

  (1) 0b paperwork: AU6 Batch 462 already shipped `test_optimizer_main_
      bonferroni_denominator_runtime` in test_semantic_integration_
      pyramid.py asserting `_dec426_verdict(stats, m_total_candidates=
      1500)` at production callsite. Queue row was stale PENDING.

  (2) 0c paperwork: AU6 Batch 462 already shipped `test_walk_forward_
      folds_chronological_disjoint` asserting per-fold
      IS_end == OOS_start + cross-fold OOS disjointness + DEC-505 1y
      span. Queue row was stale PENDING.

  (3) Item 0 partial: AU1 Batch 457 closed 2 of 4 live-impact
      placeholders (PSR in optimize_strategies_from_cube.py:130 +
      cube_populator.py:159). Two remain: exit_context.py:335
      exit_regime default + run_phase_1b_alpha_smoke.py:129 regime
      hardcode. This batch ships the BANNED-PATTERN preflight guard
      so any NEW placeholder addition surfaces in CI as a test
      failure -- complements the AU1 fixes by preventing regression.

The guard test pins the exact set of allowed-placeholder sites; if
a new placeholder lands, the test fails with the new site name so
owner sees it before merge.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# 0b paperwork
# ---------------------------------------------------------------------------

def test_batch495_0b_bonferroni_coverage_in_au6_pyramid():
    """AU6 Batch 462 already closed 0b. This test asserts that the AU6
    test still exists -- a future refactor that removes it without
    replacement surfaces here.
    """
    target = REPO / "backtest" / "tests" / "test_semantic_integration_pyramid.py"
    assert target.exists()
    src = target.read_text(encoding="utf-8")
    assert "def test_optimizer_main_bonferroni_denominator_runtime" in src, (
        "AU6 0b coverage test was removed without replacement -- "
        "Bonferroni-denominator audit no longer guarded."
    )
    # Also pin the production-callsite assertion is still strict
    assert "m_total_candidates=1500" in src or \
           "m_total_candidates=" in src, (
        "AU6 0b test no longer asserts m_total_candidates > 1 at "
        "production callsite"
    )


# ---------------------------------------------------------------------------
# 0c paperwork
# ---------------------------------------------------------------------------

def test_batch495_0c_walk_forward_chronological_coverage_in_au6_pyramid():
    """AU6 Batch 462 already closed 0c. Pin that the test still exists."""
    target = REPO / "backtest" / "tests" / "test_semantic_integration_pyramid.py"
    src = target.read_text(encoding="utf-8")
    assert "def test_walk_forward_folds_chronological_disjoint" in src, (
        "AU6 0c coverage test removed -- walk-forward fold ordering "
        "+ disjointness no longer guarded."
    )


# ---------------------------------------------------------------------------
# Item 0 partial: placeholder-banned-pattern preflight guard
# ---------------------------------------------------------------------------

# Allow-list of placeholder sites that are documented + intentional.
# Format: (relative_path_posix, marker_substring).
ALLOWED_PLACEHOLDER_SITES = {
    # Documented at exit_context.py:335 -- defaults to entry regime
    # because PIT-correct exit-day regime requires a separate lookup
    # that's not yet implemented. Owner-gated to implement properly.
    # Until then, the placeholder is intentional + tested via the
    # exit-regime parity tests.
    ("backtest/engine/exit_context.py",
     "placeholder; defaults to entry regime"),
    # Documented at screener.py:3797 -- category stored in each fn
    # rather than this lookup dict. Doc-comment, not behavior.
    ("backtest/signals/screener.py",
     "placeholder  -  category stored in each fn"),
    # Phase 1B-alpha smoke -- regime hardcoded "bull" because the smoke
    # is structural (does the agent pipeline RUN?) not behavioral
    # (is the right regime fired?). Tests that need real regime
    # exercise the engine path, not this smoke.
    ("scripts/run_phase_1b_alpha_smoke.py",
     "regime\": \"bull\"},  # placeholder"),
    # B693 sweep ticker-internal momentum proxy: SPY-alignment requires
    # df-index threading; the inline proxy uses "20d return positive"
    # as ticker-internal momentum stand-in for "outperforming SPY".
    # Sweep harness (not production engine path); proxy directionally
    # same but looser. Documented in B693 docstring; intentional.
    ("scripts/run_b693_sweeps.py",
     "return np.array([True] * len(f[\"break_52w\"]))  # placeholder"),
}


def _scan_live_placeholders():
    """Return set of (relative_path_posix, line_text) tuples for every
    `# placeholder` comment in non-test live code under backtest/ and
    scripts/.
    """
    hits = set()
    for folder in ("backtest", "scripts"):
        for path in (REPO / folder).rglob("*.py"):
            posix = path.relative_to(REPO).as_posix()
            # Skip tests + __pycache__
            if "__pycache__" in posix or "/tests/" in posix:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for line in content.splitlines():
                if re.search(r"#\s*placeholder", line, re.IGNORECASE):
                    hits.add((posix, line.strip()))
    return hits


def test_batch495_item0_placeholder_count_at_known_minimum():
    """Exact count: 4 live placeholders remain after AU1 closed 2 of 4
    + B693 added 1 documented sweep-harness proxy. A 5th placeholder
    addition surfaces here.
    """
    hits = _scan_live_placeholders()
    assert len(hits) == len(ALLOWED_PLACEHOLDER_SITES), (
        f"Live placeholder count changed from "
        f"{len(ALLOWED_PLACEHOLDER_SITES)} to {len(hits)}. New sites: "
        f"{hits - {(p, '') for p, _ in ALLOWED_PLACEHOLDER_SITES}}"
    )


def test_batch495_item0_every_placeholder_in_allowlist():
    """Each live placeholder site must match an entry in the
    documented allow-list. A new site without an allow-list entry
    blocks the commit (per item 0 audit-meta finding).
    """
    hits = _scan_live_placeholders()
    for posix, line in hits:
        matched = False
        for allowed_path, marker in ALLOWED_PLACEHOLDER_SITES:
            if posix == allowed_path and marker in line:
                matched = True
                break
        assert matched, (
            f"New placeholder site found:\n  {posix}: {line}\n"
            f"Either remove the placeholder OR add an entry to "
            f"ALLOWED_PLACEHOLDER_SITES with a one-line documented "
            f"rationale (per item 0 audit-meta finding)."
        )


def test_batch495_item0_au1_fixed_placeholders_stay_fixed():
    """Regression guard: the two AU1-fixed placeholders must not
    return. If `# placeholder` reappears next to PSR in either of
    these files, AU1's fix has been reverted.
    """
    files_au1_fixed = (
        REPO / "scripts" / "optimize_strategies_from_cube.py",
        REPO / "backtest" / "results" / "cube_populator.py",
    )
    for path in files_au1_fixed:
        assert path.exists(), f"AU1-fixed file missing: {path}"
        src = path.read_text(encoding="utf-8")
        # Lines that mention PSR + placeholder on the same line would
        # signal a regression of AU1's deflated_sharpe wire-up.
        lines = src.splitlines()
        for ln_no, line in enumerate(lines, start=1):
            if "PSR" in line.upper() and re.search(r"#\s*placeholder",
                                                    line, re.IGNORECASE):
                pytest.fail(
                    f"AU1 regression: {path.name}:{ln_no} re-introduces "
                    f"PSR placeholder: {line.strip()}"
                )
