#!/usr/bin/env python3
"""Batch 525 (2026-05-31) -- laptop-portable environment verifier.

Source: per CHECKLIST #77 + owner directive 2026-05-31 ("git as source
of truth, no drift on new laptop").
Queue row: EXECUTION_QUEUE.md item DET1 (follow-on to Batch 520 CI pin).

Run this BEFORE any engine work on a fresh machine. It verifies:

  (1) every == pin in requirements.txt matches the installed version
      (the lock is the source of truth -- a drift here means
      `pip install -r requirements.txt` resolved differently than
      expected; common causes: a pre-existing venv, conflicting
      transitive dep, OS-specific wheel)

  (2) the SHA-256 indicator fingerprints emitted by
      `scripts/check_platform_determinism.py` match the committed
      baseline for the current OS
      (Windows -> backtest/tests/fixtures/platform_determinism_windows.json
       Linux   -> backtest/tests/fixtures/platform_determinism_linux.json)
      Any mismatch is a DET1 regression -- the new environment will
      produce DIFFERENT engine output than the locked baseline.

Exit codes:
  0  -- everything matches; safe to run the engine.
  1  -- pin mismatch (re-run `pip install -r requirements.txt --upgrade`
        OR drop the venv + recreate from scratch)
  2  -- fingerprint mismatch (env-specific FP math drift; investigate
        before trusting any engine output)

Usage:
  python scripts/verify_environment.py
  python scripts/verify_environment.py --pins-only
  python scripts/verify_environment.py --fingerprints-only

**HAND-RUN-ONLY (B1704).** Nothing invokes this automatically - no Stop hook, no
pre-commit, no launcher. An audit found 12 of 16 gate scripts in this state, so
presence is NOT enforcement (CHECKLIST #224). Run it explicitly and read its exit
code; if you need it to bind, wire it and say where.
"""
from __future__ import annotations

import argparse
import importlib.metadata as md
import json
import platform
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REQUIREMENTS = REPO / "requirements.txt"
FIXTURES = REPO / "backtest" / "tests" / "fixtures"

# Map distribution name on PyPI -> module name used by importlib (most
# match; the few that don't go in PIN_NAME_OVERRIDES).
PIN_NAME_OVERRIDES = {
    "python-dateutil": "python-dateutil",
    "pytz":            "pytz",
}


def _parse_requirements_pins() -> dict[str, str]:
    """Read requirements.txt and return {pkg: version} for every == pin.

    Loose pins (`>=`, `~=`, `<`) are surfaced separately by the test
    suite; this function returns only the strict == set.
    """
    pins: dict[str, str] = {}
    pat = re.compile(r"^([A-Za-z0-9_\-\.]+)==([0-9A-Za-z\.\-_]+)\s*$")
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = pat.match(line)
        if m:
            pins[m.group(1).lower()] = m.group(2)
    return pins


def _installed_version(pkg: str) -> str | None:
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return None


def check_pins() -> tuple[bool, list[str]]:
    """Returns (all_ok, list_of_problem_lines)."""
    pins = _parse_requirements_pins()
    problems: list[str] = []
    for pkg, locked in pins.items():
        installed = _installed_version(pkg)
        if installed is None:
            problems.append(
                f"MISSING  {pkg:30s} locked={locked:15s} (not installed)"
            )
        elif installed != locked:
            problems.append(
                f"DRIFT    {pkg:30s} locked={locked:15s} installed={installed}"
            )
    return (len(problems) == 0), problems


def check_fingerprints() -> tuple[bool, list[str]]:
    """Compare current platform's indicator fingerprints vs committed
    baseline for the same OS. Returns (all_ok, mismatches).
    """
    sys.path.insert(0, str(REPO))
    from scripts.check_platform_determinism import run as run_harness
    current = run_harness()
    baseline_path = FIXTURES / f"platform_determinism_{platform.system().lower()}.json"
    if not baseline_path.exists():
        return False, [
            f"No baseline for current OS at {baseline_path.name}. Generate "
            f"via `python scripts/check_platform_determinism.py "
            f"--output {baseline_path}` then commit.",
        ]
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    expected = baseline["indicator_fingerprints"]
    actual = current["indicator_fingerprints"]
    mismatches: list[str] = []
    for name, exp_hash in expected.items():
        got = actual.get(name, "MISSING")
        if got != exp_hash:
            mismatches.append(
                f"  - {name:30s} expected={exp_hash[:16]}... "
                f"got={got[:16]}..."
            )
    return (len(mismatches) == 0), mismatches


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pins-only", action="store_true")
    p.add_argument("--fingerprints-only", action="store_true")
    args = p.parse_args()

    run_pins = not args.fingerprints_only
    run_fps  = not args.pins_only

    print(f"=== Environment verification ===")
    print(f"OS:     {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Repo:   {REPO}")
    print()

    exit_code = 0

    if run_pins:
        print("[1/2] Checking requirements.txt pins vs installed versions...")
        ok, problems = check_pins()
        if ok:
            pins = _parse_requirements_pins()
            print(f"      OK -- all {len(pins)} == pins match installed.")
        else:
            print(f"      FAIL -- {len(problems)} pin issue(s):")
            for p_ in problems:
                print(f"        {p_}")
            print("\n      Fix: drop your venv + `pip install -r requirements.txt`")
            exit_code = 1
        print()

    if run_fps and exit_code == 0:
        print("[2/2] Checking platform determinism fingerprints vs baseline...")
        ok, mismatches = check_fingerprints()
        if ok:
            print("      OK -- all indicators match the committed baseline.")
        else:
            print(f"      FAIL -- {len(mismatches)} indicator mismatch(es):")
            for m in mismatches:
                print(m)
            print("\n      Fix: investigate the diverging library "
                  "(usually numpy/pandas/numba). The engine WILL produce "
                  "different trades than the locked baseline until this "
                  "is resolved.")
            exit_code = 2
        print()

    if exit_code == 0:
        print("=== Environment verified. Safe to run the engine. ===")
    else:
        print(f"=== Verification FAILED (exit {exit_code}). ===")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
