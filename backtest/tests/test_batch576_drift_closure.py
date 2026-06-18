"""Batch 576 (2026-06-04) -- close the approvals.json drift per
owner directive 2026-06-04: "We have 355 strategies in stage 4
approvals, while the strategy roster doc showws 205, why this drift?
Shouldnt both be the same? This is the drift you should be addressing
proactively."

Investigation surfaced 3 facts:
  - approvals.json had 355 ROWS but only 124 unique strategies (multiple
    change-class rows per strategy)
  - ALL_STRATEGIES has 205; 81 strategies had NO approvals row (the
    drift)
  - 2 ghost strategies in approvals NOT in ALL_STRATEGIES:
    (a) lead_lag_sector_rotation - registered via non-ALL_STRATEGIES
        path (screen_lead_lag_sector() at screener.py:4096); the real
        engine roster is 206 not 205
    (b) news_sentiment_shift_short - Class 7 Approved B571 awaiting
        wiring

B576 backfills `Class 0 QUIET_NO_CANDIDATES` rows for the 81 quiet
strategies + ships scripts/backfill_quiet_strategies.py + extends the
strategy-roster generator to surface Stage 4 status per strategy +
documents the lead_lag architectural gotcha.

Pins:

  (1) backfill script runs + closes the drift (every ALL_STRATEGIES
      strategy has >= 1 approvals row)
  (2) backfilled rows have change_class=0, change_class_name=
      'QUIET_NO_CANDIDATES', dimension_source='drift_backfill_b576'
  (3) backfilled rows are status='Awaiting' with status_set_by=
      'system_drift_backfill'
  (4) lead_lag_sector_rotation is recognized as a legitimate ghost
      (registered via screen_lead_lag_sector special path)
  (5) approvals.json post-backfill has at least 205 unique strategies
      (covers ALL_STRATEGIES) + may have ghosts for special paths
      and queued Class 7
  (6) Class 0 rows have config_touch_point=n/a indicating no Stage 5
      action implied (just visibility)
  (7) STRATEGY_ROSTER.md shows the new "Stage 4 Status" column with
      0 strategies marked "no_approvals_row"
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
APPROVALS = Path("C:/tmp/r4_optimization_candidates/approvals.json")
BACKFILL = REPO / "scripts" / "backfill_quiet_strategies.py"
ROSTER_DOC = REPO / "STRATEGY_ROSTER.md"
ROSTER_SCRIPT = REPO / "scripts" / "build_strategy_roster.py"


def _have_inputs():
    return APPROVALS.exists() and BACKFILL.exists()


pytestmark = pytest.mark.skipif(
    not _have_inputs(),
    reason="R4 cube approvals.json absent",
)


@pytest.fixture(scope="module")
def post_backfill():
    """Run backfill against live + return current data. Idempotent
    (re-runs print 'no drift to close' when already backfilled)."""
    rc = subprocess.run(
        [sys.executable, str(BACKFILL), "--approvals", str(APPROVALS)],
        capture_output=True, text=True, timeout=60,
    )
    assert rc.returncode == 0, f"backfill failed: {rc.stderr[-2000:]}"
    return json.loads(APPROVALS.read_text(encoding="utf-8"))


def test_batch576_drift_closed(post_backfill):
    """Pin (1) + (5)."""
    from backtest.signals.screener import ALL_STRATEGIES
    approval_strats = {r["strategy"] for r in post_backfill["approvals"]}
    all_strats = set(ALL_STRATEGIES.keys())
    missing = all_strats - approval_strats
    assert not missing, (
        f"drift NOT closed: {len(missing)} strategies still missing "
        f"approvals rows: {sorted(missing)[:5]}"
    )


def test_batch576_quiet_rows_schema(post_backfill):
    """Pin (2) + (3) + (6).

    B622 update: some drift_backfill rows have had their status flipped
    from 'Awaiting' to 'Implemented' by subsequent batches (when a quiet
    strategy got walked or wired in). Test relaxed to accept either
    Awaiting or Implemented as valid post-B576 states; the schema-pin
    properties (change_class=0, change_class_name, status_set_by,
    config_touch_point) still hold."""
    quiet = [r for r in post_backfill["approvals"]
             if r["dimension_source"] == "drift_backfill_b576"]
    assert quiet, "expected at least one QUIET_NO_CANDIDATES row"
    for r in quiet:
        assert r["change_class"] == 0
        assert r["change_class_name"] == "QUIET_NO_CANDIDATES"
        assert r["status"] in ("Awaiting", "Implemented"), (
            f"row status {r['status']!r} for {r['strategy']!r} -- expected "
            f"Awaiting (initial) or Implemented (post-walk)"
        )
        # B622 update: post-walk rows may have status_set_by re-stamped
        # by owner_jeet when status flips Awaiting -> Implemented.
        assert r["status_set_by"] in ("system_drift_backfill", "owner_jeet")
        assert "n/a" in r["config_touch_point"]


def test_batch576_ghost_strategies_legitimate(post_backfill):
    """Pin (4): the 2 known ghosts are legitimate non-ALL_STRATEGIES
    registrations."""
    from backtest.signals.screener import ALL_STRATEGIES
    approval_strats = {r["strategy"] for r in post_backfill["approvals"]}
    ghosts = approval_strats - set(ALL_STRATEGIES.keys())
    # Known legitimate ghosts (B622 fixture-drift repair + B839 update):
    legitimate_ghosts = {
        "lead_lag_sector_rotation",        # non-ALL_STRATEGIES path
        "news_sentiment_shift_short",      # B571 Class 7 Approved awaiting wiring
        "donchian_20_breakout_retest",     # B599 deletion (owner directive
                                           #   B596 convergence option 2);
                                           #   explicit pair donchian_breakout_retest_long
                                           #   + donchian_breakdown_retest_short carries
                                           #   the semantics
        "hull_rsi_short",                  # B722 deletion (Pattern W
                                           #   deterministic-duplicate post-B718 tightening;
                                           #   strat_hull_rsi SHORT branch carries
                                           #   the semantics)
        "evening_star_short",              # B639 deletion (Stage 4 walk
                                           #   morning_star option a; standalone became
                                           #   strict subset of strat_morning_star SHORT
                                           #   post option-2 reconcile-to-reversal)
        "po3_htf_aligned_long",            # B722 deletion (HYBRID Pattern F;
                                           #   strict subset of strat_po3_bullish on
                                           #   weekly_bias_bull axis)
        "po3_htf_aligned_short",           # B722 deletion (same as long mirror)
        "squeeze_setup_event_only_long",   # B620 deletion (~2.5 fires/yr
                                           #   FAIL_FIRE_STARVED; A/B question
                                           #   answerable post-cube from squeeze_setup
                                           #   _long trade log filter)
        "buyback_8k_recent_long",          # B682 deletion (CC-B 8-K
                                           #   population-mixing M&A Item 1.01
                                           #   SM-4 feasibility-failure carry)
        "volume_spike_breakout_retest",    # B682 deletion (B620 precedent +
                                           #   B621 0.01/yr FAIL_FIRE_STARVED estimator)
        "camarilla_r3_breakout",           # B641 RENAME to camarilla_r4_breakout
                                           #   (Camarilla source-system re-anchor;
                                           #   R3=fade per Slim Khan/Nick Scott;
                                           #   R4=breakout level)
        "institutional_capitulation_short",# B670 deletion (Pattern C
                                           #   STRENGTHENED + 2 Class 7 NEW
                                           #   replacements wired)
        "institutional_distribution_short",# B670 deletion (same)
        "camarilla_rsi_obv",               # B874 deletion (S4-B754-A-19
                                           #   Pattern W council 5-lens
                                           #   option A2; deterministic
                                           #   strict-subset of W9 dual)
        "camarilla_rsi_obv_short",         # B874 deletion (same META-PATTERN;
                                           #   literal-duplicate-pair with
                                           #   dual SHORT branch)
    }
    # Every ghost should be either a known legitimate one OR a Class 7
    # owner-added candidate awaiting wiring (dimension_source == 'owner_added')
    for g in ghosts:
        g_rows = [r for r in post_backfill["approvals"] if r["strategy"] == g]
        is_known = g in legitimate_ghosts
        is_owner_added_class7 = any(
            r["change_class"] == 7 and r["dimension_source"] == "owner_added"
            for r in g_rows
        )
        assert is_known or is_owner_added_class7, (
            f"unexpected ghost strategy: {g} (not in known legitimate set "
            f"and not a Class 7 owner-added candidate)"
        )


@pytest.mark.skip(
    reason="B894 (2026-06-18 Council 18) SCRUBBED 'Stage 4 Status' column "
    "from STRATEGY_ROSTER.md per CHECKLIST #111: source data (approvals.json) "
    "was stale (pre-B722/B874). Column will be restored post-R5 with fresh data."
)
def test_batch576_roster_doc_shows_stage_4_column(post_backfill):
    """Pin (7) - regen roster + check the Stage 4 Status column exists
    + 0 rows have 'no_approvals_row'.

    B899 STATUS: SKIPPED. The column was intentionally removed by B894 Council
    18 because its data source (approvals.json) was stale (pre-B722/B874).
    Per CHECKLIST #111: 'anything that lies is worse than absent.' Will be
    restored post-R5 cube execution with fresh data sources.
    """
    rc = subprocess.run(
        [sys.executable, str(ROSTER_SCRIPT)],
        capture_output=True, text=True, timeout=60,
    )
    assert rc.returncode == 0, f"roster regen failed: {rc.stderr[-2000:]}"
    doc = ROSTER_DOC.read_text(encoding="utf-8")
    assert "Stage 4 Status" in doc, "Stage 4 Status column missing"
    assert "no_approvals_row" not in doc, (
        "STRATEGY_ROSTER.md still has 'no_approvals_row' entries - "
        "drift not fully closed in roster doc"
    )


def test_batch576_backfill_idempotent(post_backfill):
    """Re-running backfill is a no-op when drift already closed."""
    rc = subprocess.run(
        [sys.executable, str(BACKFILL), "--approvals", str(APPROVALS)],
        capture_output=True, text=True, timeout=60,
    )
    assert rc.returncode == 0
    assert "No drift to close" in rc.stdout or "no drift" in rc.stdout.lower()


def test_batch576_lead_lag_special_path_documented():
    """Pin (4) - architectural gotcha documented in STRATEGY_ROSTER.md."""
    doc = ROSTER_DOC.read_text(encoding="utf-8")
    assert "lead_lag_sector_rotation" in doc
    assert "screen_lead_lag_sector" in doc
    assert "Architectural gotcha" in doc or "architectural gotcha" in doc
