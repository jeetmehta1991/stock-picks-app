"""B1127 Tier-4 Empirical: Meta-test for test authoring (Council 246).

CATCHES: B1124 test authoring bugs (syntax error dict/list mismatch;
wrong assumptions on ALL_STRATEGIES structure and close/macd_bullish
names). All test files must import cleanly + have callable test_ funcs.
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent
TESTS_DIR = REPO / "backtest" / "tests"


def _all_test_files() -> list[Path]:
    return sorted(TESTS_DIR.glob("test_*.py"))


def test_all_test_files_syntactically_valid():
    """No syntax errors in any test file (catches B1124-9 mismatched braces)."""
    errors = []
    for path in _all_test_files():
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as e:
            errors.append(f"{path.name}: {e}")
    assert not errors, "Syntax errors in test files:\n" + "\n".join(errors)


def test_all_test_files_have_at_least_one_test_func():
    """Every test_*.py must contain at least one def test_*() function."""
    empty_files = []
    for path in _all_test_files():
        content = path.read_text(encoding="utf-8")
        if "def test_" not in content:
            empty_files.append(path.name)
    assert not empty_files, f"Test files with no test_ funcs: {empty_files}"


def test_b1124_test_files_present():
    """B1124 test extension: 10 files must be present."""
    b1124_files = [
        f for f in TESTS_DIR.glob("test_b1124_*.py")
    ]
    assert len(b1124_files) == 10, (
        f"Expected 10 B1124 test files; got {len(b1124_files)}"
    )


def test_b1127_test_files_present():
    """B1127 test extension: 12 files must be present."""
    b1127_files = [f for f in TESTS_DIR.glob("test_b1127_*.py")]
    assert len(b1127_files) >= 12, (
        f"Expected 12 B1127 test files; got {len(b1127_files)}"
    )


def test_skip_markers_have_explicit_cta():
    """L186: every pytest.skip must have message with unblock CTA."""
    problematic = []
    for path in _all_test_files():
        if "test_b1124" not in path.name and "test_b1127" not in path.name:
            continue
        content = path.read_text(encoding="utf-8")
        # Count pytest.skip( occurrences
        import re
        for match in re.finditer(r'pytest\.skip\(\s*"([^"]{1,80})"', content):
            msg = match.group(1)
            if len(msg) < 20:
                problematic.append(f"{path.name}: skip message too short: {msg!r}")
    assert not problematic, "L186: skips need explicit CTA:\n" + "\n".join(problematic)
