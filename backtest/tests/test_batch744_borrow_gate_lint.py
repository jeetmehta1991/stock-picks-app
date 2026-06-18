# Source: B713 Phase 0 + Decision 3 build #4 + Decision 5 Cat 1 + owner-approved "push forward" 2026-06-13 per CHECKLIST #77
"""B744 pin tests: borrow-gate lint enabled cluster-wide.

The lint (scripts/borrow_gate_lint.py) scans backtest/signals/screener.py and
asserts every short-emitting strategy:
  1. References `_short_borrow_trap_active(s)` in its function body.
  2. Declares `"borrow_ok"` in its signals_used list (signals_used_short for _strat3).
  3. (Dual strategies only) does NOT declare `"borrow_ok"` in the LONG branch.

PREREQUISITE: B740 (26 pure-short) + B741 (25 pure-short) + B742 (31 dual) +
B743 (30 dual) = 112 short strategies converted to explicit gate.

This pin is the final lock-in for the explicit-gate invariant. B718d (planned)
removes the inspect.currentframe path from `_strat`/`_strat3` helpers; this pin
guarantees the invariant holds at every pyramid invocation.

Failure modes the lint catches:
- New short strategy added without explicit gate
- Someone removes the gate from an existing strategy
- Future refactor accidentally drops `borrow_ok` from signals_used
- Dual strategy author mistakenly puts borrow_ok in the LONG branch
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from scripts.borrow_gate_lint import (
    LintReport,
    ShortStrategy,
    audit_screener,
    format_report,
)


def test_b744_pin1_live_screener_has_zero_violations():
    """The PRIMARY invariant: live screener.py must have zero borrow-gate
    violations. If this fails, the introducer must either add the explicit
    gate OR document why the strategy is exempted (e.g., direction='avoid').
    """
    rep = audit_screener("backtest/signals/screener.py")
    assert isinstance(rep, LintReport)
    assert not rep.violations, (
        "borrow-gate lint violations (auto-introduced after B718b cohort):\n"
        + format_report(rep)
    )


def test_b744_pin2_short_strategy_count_matches_b718b_cohort():
    """Cluster-wide head-count: 51 pure-short + 61 dual _strat3 = 112 short-emitting
    strategies post-B718b. This number locks until B718d (which only removes
    inspect.currentframe; doesn't change roster).
    """
    rep = audit_screener("backtest/signals/screener.py")
    pure = [s for s in rep.short_strategies if not s.is_dual]
    dual = [s for s in rep.short_strategies if s.is_dual]
    # B899 migration: B874 deleted camarilla_rsi_obv_short (pure-short)
    # + camarilla_rsi_obv (dual). 51->50 pure, 61->60 dual, 112->110 total.
    assert len(pure) == 50, f"expected 50 pure-short (B740+B741 post-B874); got {len(pure)}"
    assert len(dual) == 60, f"expected 60 dual _strat3 (B742+B743 post-B874); got {len(dual)}"
    assert len(rep.short_strategies) == 110


def test_b744_pin3_synthetic_missing_gate_caught(tmp_path):
    """SANITY: write a synthetic screener.py with a violation and confirm the
    lint detects it. Guards against the lint silently passing when it
    shouldn't.
    """
    bad = tmp_path / "bad_screener.py"
    bad.write_text(textwrap.dedent('''
        def _strat(fires, direction, category, signals_used, ctx):
            return {"fires": fires, "direction": direction}

        def strat_bad_short(s):
            fires = s.get("trigger", False)
            return _strat(fires, "short", "test",
                          ["trigger"],
                          ["bad: no borrow gate"])
    '''), encoding="utf-8")
    rep = audit_screener(bad)
    assert len(rep.violations) == 1
    assert rep.violations[0].name == "strat_bad_short"
    assert not rep.violations[0].has_borrow_gate
    assert not rep.violations[0].has_borrow_ok_declared


def test_b744_pin4_synthetic_clean_strategy_passes(tmp_path):
    """SANITY: a strategy that DOES declare the gate passes the lint."""
    good = tmp_path / "good_screener.py"
    good.write_text(textwrap.dedent('''
        def _short_borrow_trap_active(s):
            return s.get("days_to_cover", 0.0) > 5.0

        def _strat(fires, direction, category, signals_used, ctx):
            return {"fires": fires, "direction": direction, "signals_used": signals_used}

        def strat_good_short(s):
            fires = s.get("trigger", False) and not _short_borrow_trap_active(s)
            return _strat(fires, "short", "test",
                          ["trigger", "borrow_ok"],
                          ["clean: explicit gate at call site"])
    '''), encoding="utf-8")
    rep = audit_screener(good)
    assert len(rep.violations) == 0
    assert len(rep.short_strategies) == 1
    assert rep.short_strategies[0].name == "strat_good_short"
    assert rep.short_strategies[0].has_borrow_gate
    assert rep.short_strategies[0].has_borrow_ok_declared


def test_b744_pin5_synthetic_dual_with_borrow_ok_in_long_branch_caught(tmp_path):
    """SANITY: a dual `_strat3` that mistakenly declares borrow_ok in the LONG
    branch signals_used (4th arg) must be flagged. Borrow gate is SHORT-only.
    """
    misplaced = tmp_path / "misplaced.py"
    misplaced.write_text(textwrap.dedent('''
        def _short_borrow_trap_active(s):
            return s.get("days_to_cover", 0.0) > 5.0

        def _strat3(fl, fs, category, sl, ss, bl, bs):
            return {"fires": fl or fs}

        def strat_misplaced(s):
            fl = s.get("long_trig", False)
            fs = s.get("short_trig", False) and not _short_borrow_trap_active(s)
            return _strat3(fl, fs, "test",
                ["long_trig", "borrow_ok"],     # WRONG: borrow_ok in LONG branch
                ["short_trig", "borrow_ok"],    # correct: borrow_ok in SHORT branch
                ["long bullet"],
                ["short bullet"])
    '''), encoding="utf-8")
    rep = audit_screener(misplaced)
    assert len(rep.violations) == 1
    assert rep.violations[0].name == "strat_misplaced"
    # body has both the gate AND the declaration (in short list); the violation
    # is the misplaced one in the long list
    assert rep.violations[0].has_borrow_gate
    assert rep.violations[0].has_borrow_ok_declared


def test_b744_pin6_format_report_runs_on_live_and_synthetic():
    """The format_report helper produces non-empty output for both clean
    (live) AND violation cases.
    """
    live = audit_screener("backtest/signals/screener.py")
    out_live = format_report(live)
    assert "BORROW-GATE LINT" in out_live
    assert "files=1" in out_live
    assert "OK:" in out_live  # passes today

    fake = LintReport(
        short_strategies=[
            ShortStrategy(name="strat_fake", line=1, is_dual=False,
                          has_borrow_gate=False, has_borrow_ok_declared=False),
        ],
        violations=[
            ShortStrategy(name="strat_fake", line=1, is_dual=False,
                          has_borrow_gate=False, has_borrow_ok_declared=False),
        ],
        files_scanned=1,
    )
    out_fail = format_report(fake)
    assert "VIOLATIONS:" in out_fail
    assert "strat_fake" in out_fail
