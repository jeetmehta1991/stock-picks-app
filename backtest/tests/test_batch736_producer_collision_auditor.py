# Source: B708 reviewer offer + B705 ICT PO3 finding + Decision 3 build #3 owner-approval per CHECKLIST #77
"""B736 pin tests: producer-collision auditor (static AST analysis).

The auditor flags two collision classes:
1. NAME-COLLISION: compute_X vs compute_Xs (pluralization), case-only, near-miss
2. KEY-COLLISION: two producers writing the same string key to out[] / result[]

These pin tests exercise the auditor against synthetic source on disk (via tmp
dir) AND verify the live `backtest/signals/` audit returns the known PO3
pluralization collision but no NEW name-collisions appear (regression guard).
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from scripts.producer_collision_audit import (
    AuditReport,
    audit_signals_dir,
    format_report,
)


# --------------------------------------------------------------------------
# Synthetic-source helpers
# --------------------------------------------------------------------------
def _write(dir_path: Path, name: str, body: str) -> Path:
    f = dir_path / name
    f.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return f


# --------------------------------------------------------------------------
# Pin tests
# --------------------------------------------------------------------------
def test_b736_pin1_no_producers_no_collisions(tmp_path):
    """Empty signals dir -> empty audit, no errors."""
    rep = audit_signals_dir(tmp_path)
    assert isinstance(rep, AuditReport)
    assert rep.producers == []
    assert rep.name_collisions == []
    assert rep.key_collisions == []


def test_b736_pin2_detects_pluralization_name_collision(tmp_path):
    """compute_foo_signal (singular) in module A + compute_foo_signals (plural)
    in module B must be flagged as a pluralization collision (the B705 case).
    """
    _write(tmp_path, "a.py", '''
        def compute_foo_signal(df):
            out = {}
            out["a"] = 1
            return out
    ''')
    _write(tmp_path, "b.py", '''
        def compute_foo_signals(df):
            out = {}
            out["b"] = 2
            return out
    ''')
    rep = audit_signals_dir(tmp_path)
    assert len(rep.name_collisions) == 1, (
        f"must detect 1 pluralization collision; got {len(rep.name_collisions)} -> {rep.name_collisions}"
    )
    nc = rep.name_collisions[0]
    assert nc.kind == "pluralization"
    assert nc.distance == 1
    assert {nc.fn_a.name, nc.fn_b.name} == {"compute_foo_signal", "compute_foo_signals"}


def test_b736_pin3_detects_key_collision(tmp_path):
    """Two producers writing the same key 'foo' -> KeyCollision."""
    _write(tmp_path, "a.py", '''
        def compute_a(df):
            out = {}
            out["foo"] = 1
            out["a_only"] = 2
            return out
    ''')
    _write(tmp_path, "b.py", '''
        def compute_b(df):
            out = {}
            out["foo"] = 99   # collision
            out["b_only"] = 3
            return out
    ''')
    rep = audit_signals_dir(tmp_path)
    keys = {kc.key for kc in rep.key_collisions}
    assert "foo" in keys, f"must detect 'foo' key collision; got keys={keys}"
    # a_only and b_only are emitted by only one producer -> no collision
    assert "a_only" not in keys
    assert "b_only" not in keys


def test_b736_pin4_ignores_within_module_function_pairs(tmp_path):
    """compute_x and compute_xs in the SAME module are NOT flagged
    (intentional return-shape ladder, not cross-module risk).
    """
    _write(tmp_path, "single.py", '''
        def compute_x(df):
            return {"a": 1}
        def compute_xs(df):
            return {"b": 2}
    ''')
    rep = audit_signals_dir(tmp_path)
    assert rep.name_collisions == [], (
        f"within-module pairs must NOT be flagged; got {rep.name_collisions}"
    )


def test_b736_pin5_case_only_collision(tmp_path):
    """compute_FOO vs compute_foo -> case collision."""
    _write(tmp_path, "a.py", '''
        def compute_Foo(df):
            return {"x": 1}
    ''')
    _write(tmp_path, "b.py", '''
        def compute_foo(df):
            return {"y": 2}
    ''')
    rep = audit_signals_dir(tmp_path)
    assert len(rep.name_collisions) == 1
    assert rep.name_collisions[0].kind == "case"


def test_b736_pin6_format_report_runs_without_error(tmp_path):
    """format_report on a synthetic audit must produce non-empty output."""
    _write(tmp_path, "a.py", 'def compute_foo_signal(df):\n    return {"k": 1}\n')
    _write(tmp_path, "b.py", 'def compute_foo_signals(df):\n    return {"k2": 2}\n')
    rep = audit_signals_dir(tmp_path)
    s = format_report(rep)
    assert "NAME COLLISIONS" in s
    assert "KEY COLLISIONS" in s
    assert "compute_foo_signal" in s


def test_b736_pin7_live_signals_dir_known_po3_collision_only():
    """Regression guard: live `backtest/signals/` must contain the known PO3
    pluralization collision (compute_po3_signal vs compute_po3_signals) AND
    no NEW name collisions. If a new producer-name collision lands, this test
    flips red and the introducer must rename or document why both must coexist.
    """
    rep = audit_signals_dir("backtest/signals")
    # We expect exactly 1 collision: the known PO3 case
    po3_pair = {"compute_po3_signal", "compute_po3_signals"}
    matched = [nc for nc in rep.name_collisions
               if {nc.fn_a.name, nc.fn_b.name} == po3_pair]
    assert len(matched) == 1, (
        f"PO3 pluralization collision must remain visible (B705 finding); got "
        f"{[(nc.fn_a.name, nc.fn_b.name) for nc in rep.name_collisions]}"
    )
    # No OTHER collisions allowed without explicit owner decision
    others = [nc for nc in rep.name_collisions
              if {nc.fn_a.name, nc.fn_b.name} != po3_pair]
    assert others == [], (
        f"new producer-name collision detected (not previously seen); "
        f"introducer must rename or document. Found: "
        f"{[(nc.fn_a.name, nc.fn_b.name, nc.kind) for nc in others]}"
    )
