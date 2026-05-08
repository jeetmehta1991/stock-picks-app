"""Pass 53 Day-9 v8h+1: tests for scripts/preflight.py enforcement gate.

Verifies that the preflight script correctly DETECTS the rule violations
it claims to detect. If preflight ever silently passes a violation, this
test fails and CI catches it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = REPO_ROOT / "scripts" / "preflight.py"


def run_preflight(paths: list[Path]) -> tuple[int, str]:
    args = [sys.executable, str(PREFLIGHT), "--paths"] + [str(p) for p in paths]
    r = subprocess.run(args, capture_output=True, text=True, cwd=REPO_ROOT)
    return r.returncode, r.stdout + r.stderr


def test_preflight_passes_on_clean_file(tmp_path: Path):
    f = tmp_path / "clean_script.py"
    f.write_text(
        '"""Docstring with em-dash - is fine."""\n'
        'print("hello world")\n',
        encoding="utf-8",
    )
    code, out = run_preflight([f])
    assert code == 0, f"preflight should pass clean file; got {code}: {out}"


def test_preflight_blocks_em_dash_in_scripts(tmp_path: Path):
    # Simulate a file in scripts/ via name pattern; preflight checks the path
    scripts_dir = REPO_ROOT / "scripts"
    f = scripts_dir / "_test_em_dash_temp.py"
    try:
        f.write_text(
            '"""Docstring."""\n'
            f'x = "hello {chr(0x2014)} world"  # em-dash in runtime\n',
            encoding="utf-8",
        )
        code, out = run_preflight([f])
        assert code == 1, f"preflight should BLOCK em-dash in scripts/; got {code}"
        assert "em-dash" in out.lower() or "0x2014" in out
    finally:
        if f.exists():
            f.unlink()


def test_preflight_blocks_unicode_in_runtime(tmp_path: Path):
    f = tmp_path / "bad_unicode.py"
    # Place file outside scripts/ to isolate C1 (unicode-in-runtime) from C2 (em-dash)
    f.write_text(
        '"""Docstring."""\n'
        f'msg = "hello {chr(0x2705)} done"  # check-mark in runtime\n',
        encoding="utf-8",
    )
    code, out = run_preflight([f])
    assert code == 1, f"preflight should BLOCK unicode in runtime; got {code}: {out}"


def test_preflight_blocks_dashboard_without_canonical_source(tmp_path: Path):
    f = tmp_path / "dashboard_test_temp.py"
    f.write_text(
        '"""A dashboard but with no source-of-truth declaration."""\n'
        'x = 1\n',
        encoding="utf-8",
    )
    code, out = run_preflight([f])
    assert code == 1, f"preflight should BLOCK dashboard_* without canonical-source; got {code}: {out}"


def test_preflight_passes_dashboard_with_canonical_source(tmp_path: Path):
    f = tmp_path / "dashboard_clean_temp.py"
    f.write_text(
        '"""A dashboard. Source: API_ENDPOINT_INVENTORY.md per CHECKLIST #77."""\n'
        'x = 1\n',
        encoding="utf-8",
    )
    code, out = run_preflight([f])
    assert code == 0, f"preflight should PASS dashboard with canonical-source; got {code}: {out}"


def test_preflight_blocks_prefetch_with_unrestricted_commit(tmp_path: Path):
    scripts_dir = REPO_ROOT / "scripts"
    f = scripts_dir / "prefetch__test_unrestricted_commit.py"
    try:
        f.write_text(
            '"""prefetch script with unrestricted git commit."""\n'
            'import subprocess\n'
            'subprocess.run(["git", "commit", "-m", "all staged"], capture_output=True)\n',
            encoding="utf-8",
        )
        code, out = run_preflight([f])
        assert code == 1, f"preflight should BLOCK unrestricted git commit in prefetch_*; got {code}"
    finally:
        if f.exists():
            f.unlink()


def test_preflight_existence_required():
    """The preflight script itself must exist and be runnable."""
    assert PREFLIGHT.exists(), "scripts/preflight.py must exist"
    r = subprocess.run([sys.executable, str(PREFLIGHT), "--all"],
                        capture_output=True, text=True, cwd=REPO_ROOT)
    # --all may pass or fail depending on repo state; just verify it runs
    assert r.returncode in (0, 1), f"preflight --all should return 0 or 1; got {r.returncode}"
