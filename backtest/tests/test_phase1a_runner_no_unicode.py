"""Pass 53 Day-9 v8h P1.runner regression: prevent Unicode emoji in
production runner from re-introducing Windows cp1252 console crash.

Caught 2026-05-07 P1.runner integration test:
  python backtest/run_phase1a.py --no-agents --start ... --end ...
  → UnicodeEncodeError: 'charmap' codec can't encode character '\\u274c'
  (this is ❌ — emoji icon used in validate_env())

Would have blocked Phase 1A May 15 launch on Windows. Fixed by replacing
emoji icons (✅ ⚠ ❌ → → — • ℹ️) with ASCII-safe equivalents
([OK] [WARN] [FAIL] -> - * [INFO]).

This test guards against re-introduction by scanning run_phase1a.py for
any non-ASCII printable characters in print() / logger output paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "backtest" / "run_phase1a.py"


def test_phase1a_runner_ascii_safe():
    """run_phase1a.py must contain only ASCII characters in code body
    (excluding docstrings which are unicode-safe in Python source but
    safer to keep ASCII for Windows console compat)."""
    text = RUNNER.read_text(encoding="utf-8")
    # Identify any character with codepoint > 127
    bad_chars = set()
    for ch in text:
        if ord(ch) > 127 and ch != "\n" and ch != "\r":
            bad_chars.add(ch)
    assert not bad_chars, (
        f"run_phase1a.py contains non-ASCII characters {bad_chars} — "
        f"will crash on Windows cp1252 console (P1.runner regression). "
        f"Use ASCII labels like [OK]/[FAIL]/[WARN] instead of emoji."
    )


def test_phase1a_runner_imports_cleanly():
    """run_phase1a.py module must import without errors (catch import-time
    syntax issues)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_phase1a_test", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    # Don't actually run main(); just verify it loads
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        # main() may sys.exit; ignore if argparse-driven exit
        pass
    assert hasattr(mod, "main"), "run_phase1a.py missing main() entry point"
    assert hasattr(mod, "validate_env")
    assert hasattr(mod, "validate_lookahead")
    assert hasattr(mod, "phase1a_quality_gate")
