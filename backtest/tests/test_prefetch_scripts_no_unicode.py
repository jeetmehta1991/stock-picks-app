"""Pass 53 Day-9 v8h evening regression: prevent Unicode emoji in
prefetch scripts from re-introducing Windows cp1252 console crashes.

Sister rule to test_phase1a_runner_no_unicode.py — that test guards the
production runner; THIS test extends the same discipline to ALL
prefetch scripts in scripts/. Pattern lineage:

  - 2026-05-07 P1.runner integration test caught backtest/run_phase1a.py
    Unicode bug (emoji icons crashed cp1252 console) — fixed in
    8d2641edf with regression test test_phase1a_runner_no_unicode.py.
  - 2026-05-07 evening: prefetch_quiver.py BG bsu432hbt FAILED with
    UnicodeEncodeError on \\u2705 (heavy check) at line 231 — same bug
    class, narrower scope (P1.runner test didn't cover prefetch scripts).
  - L150 pyramid dimension-coverage gap: when one script has a regression
    test, sibling scripts in the same role need the same coverage. This
    test extends the dimension to all prefetch_*.py + refresh_*.py +
    smoke_test_*.py + build_*.py scripts.

A prefetch script that prints non-ASCII to stdout/stderr will crash on
Windows cp1252 console (default encoding for legacy Windows shells).
GitHub Actions / Codespaces use UTF-8 so they don't catch the bug.
This test catches it BEFORE the script runs.

Scope:
  - All scripts/prefetch_*.py
  - All scripts/refresh_*.py
  - All scripts/build_*.py
  - All scripts/smoke_test_*.py
  - scripts/run_*.sh ARE excluded (shell scripts, not Python)

Allowed exceptions (must be in DOCSTRING only — pyflakes treats docstrings
as comments and they don't print at runtime):
  - Module-level docstrings
  - Function docstrings

NOT allowed:
  - print() statement strings
  - logger.info/warning/error string args
  - f-strings outside docstrings
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _python_scripts_in_scope() -> list[Path]:
    """Return all Python prefetch/refresh/build/smoke scripts."""
    if not SCRIPTS_DIR.exists():
        return []
    patterns = ["prefetch_*.py", "refresh_*.py", "build_*.py", "smoke_test_*.py"]
    files = []
    for pat in patterns:
        files.extend(SCRIPTS_DIR.glob(pat))
    return sorted(files)


def _strip_docstrings(source: str) -> str:
    """Roughly remove triple-quoted docstrings so test only flags
    runtime-printable Unicode. Conservative — keeps ALL non-docstring
    code intact (including comments, which CAN contain unicode safely
    since # is consumed by Python lexer before encoding).
    """
    import re
    # Triple-quoted strings (both ''' and """) — non-greedy
    pattern = r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
    return re.sub(pattern, "", source)


def test_no_python_scripts_in_scope_means_test_misconfigured():
    """Sanity check — if scripts/ has no prefetch/refresh/build files,
    something is wrong and this test won't catch anything."""
    files = _python_scripts_in_scope()
    assert len(files) >= 5, (
        f"Expected at least 5 prefetch/refresh/build/smoke scripts, "
        f"found {len(files)}. Test scope may be misconfigured."
    )


@pytest.mark.parametrize("script_path", _python_scripts_in_scope(),
                          ids=lambda p: p.name)
def test_prefetch_script_no_unicode_in_runtime_strings(script_path: Path):
    """Each prefetch / refresh / build / smoke-test script must contain
    only ASCII characters in code that can print at runtime (i.e.
    everything except docstrings).

    Catches Unicode emoji / dashes / arrows in print() / f-strings /
    logger calls that would crash on Windows cp1252 console.
    """
    text = script_path.read_text(encoding="utf-8")
    code_no_docstrings = _strip_docstrings(text)
    bad_chars = set()
    for ch in code_no_docstrings:
        if ord(ch) > 127 and ch not in ("\n", "\r", "\t"):
            bad_chars.add(ch)
    assert not bad_chars, (
        f"{script_path.name} contains non-ASCII characters {bad_chars} "
        f"in runtime-printable code. Will crash on Windows cp1252 console "
        f"(prefetch BG-runner regression). Use ASCII labels like "
        f"[OK]/[FAIL]/[WARN]/-> instead of emoji/em-dashes/arrows. "
        f"OK to use these chars inside triple-quoted docstrings ONLY."
    )
