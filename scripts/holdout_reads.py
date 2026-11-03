#!/usr/bin/env python
"""S6-B3395 (B3139q-r178): the Step-2 holdout-read doors' shared checks - ONE
definition for both offline readers, scripts/offline_holdout_read.py (the
depth read) and scripts/breadth_step2_read.py (the breadth read) (L593).

RUNBOOK RULES THIS MODULE MECHANIZES (census S6-B3344, cluster M-HOLD):
  * section 1.1 item 2 and F4 (census line 300): the Step-2 cell is COMMITTED
    before any holdout code path runs - step1_uncommitted refuses a Step-1
    artifact that is untracked, staged but not committed, or modified. The
    ordering IS the pre-registration: a read taken off an uncommitted
    artifact has no commit hash to show the cell preceded the read.
  * section 2.7 row 5 (census line 880): Step 2 refuses an unreconciled
    Step 1 - require_multiplicity, moved here from breadth_step2_read
    (S6-B2836a, B2839) so the depth read runs the check the breadth read
    has run since B2839. breadth_step2_read imports it back, so
    breadth_step2_read.require_multiplicity still resolves.

MEASURED before the change (B3139q-r177, scratchpad r177 prereg_all.py):
18 tracked artifacts carry a preregistration_candidate; 6 are unread and
not void; 2 of those 6 lack a multiplicity block, and both are for an
ADMITTED strategy the closed-strategy refusal already refuses - so the
multiplicity door changes the outcome of 0 of the 6 reads still possible.
12 of 12 tracked *_step1_is_surface files were committed and clean.

FAILS CLOSED (L642): git that cannot run, a path outside the repository, a
missing artifact - each is a refusal, never a pass.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The breadth reader's control strategy since B2678 (runbook section 3.5),
# shared with the depth reader's control comparison (S6-B3395, T6).
CONTROL_DEFAULT = "pead_long_high_yoy_growth_only"


def require_multiplicity(art: dict, source: str) -> None:
    """S6-B2836a (B2839): a Step-2 holdout read may only follow a Step-1 whose
    MULTIPLICITY BLOCK RECONCILED. Under the B2836 no-pruning ruling the full
    combination population touches the holdout, so the trials-count honesty
    lives entirely in Step-1's multiplicity instrument - and this reader
    previously never looked (found by the B2836 enforcement-map grep).
    FAIL CLOSED on the absent key (L642: the absent case is the case the
    guard exists for), and on any value other than True.
    """
    mult = art.get("multiplicity")
    if not isinstance(mult, dict) or "reconciles" not in mult:
        raise SystemExit(
            f"REFUSED: {source} carries NO multiplicity block - Step-1 must "
            "run the runbook section 1.4 multiplicity instrument before any holdout read "
            "(S6-B2836a; fail closed on absence)")
    if mult.get("reconciles") is not True:
        raise SystemExit(
            f"REFUSED: {source} multiplicity.reconciles = "
            f"{mult.get('reconciles')!r} - a non-reconciled Step-1 cannot "
            "feed a holdout read (S6-B2836a)")


def step1_uncommitted(path, *, root=None) -> str | None:
    """None when `path` is a Step-1 artifact that is tracked and clean in the
    repository; otherwise the refusal naming what is wrong.

    A staged-but-uncommitted new file is in git's index, so `ls-files` alone
    would pass it; `status --porcelain` shows it as 'A ', which refuses - the
    rule asks for a COMMIT, not a stage. `root` is the repository to check
    (the module's own repository unless a caller names another)."""
    rootp = Path(root or ROOT).resolve()
    p = Path(path)
    if not p.is_absolute():
        p = rootp / p
    try:
        rel = p.resolve().relative_to(rootp).as_posix()
    except ValueError:
        return (f"REFUSED (S6-B3395, runbook 1.1 item 2 / F4): {path} is outside "
                "the repository, so it cannot be committed - a holdout read rests "
                "on a Step-1 artifact committed BEFORE any holdout code path runs")
    if not p.exists():
        return f"REFUSED (S6-B3395): the Step-1 artifact {path} does not exist"
    try:
        tracked = subprocess.run(
            ["git", "-C", str(rootp), "ls-files", "--error-unmatch", "--", rel],
            capture_output=True, text=True, timeout=30)
        status = subprocess.run(
            ["git", "-C", str(rootp), "status", "--porcelain", "--", rel],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return (f"REFUSED (S6-B3395): git could not be run ({type(exc).__name__}) "
                "- the committed-artifact check fails closed (L642)")
    if tracked.returncode != 0:
        return (f"REFUSED (S6-B3395, runbook 1.1 item 2 / F4): {rel} is not tracked "
                "- commit the Step-1 artifact BEFORE any holdout code path runs; "
                "the commit is the pre-registration")
    if status.returncode != 0 or status.stdout.strip():
        return (f"REFUSED (S6-B3395, runbook 1.1 item 2 / F4): {rel} has uncommitted "
                f"changes ({status.stdout.strip()[:40]!r}) - the cell a read admits on "
                "must be the committed one")
    return None
