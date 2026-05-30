"""Batch 498 (2026-05-31) -- DET1 platform-determinism harness tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item DET1 (engine-cross-platform-
determinism).
Diagnostic: scripts/check_platform_determinism.py.

Per DET1 finding (Batch 484 CI logs 2026-05-30), the backtest engine
produces COMPLETELY DIFFERENT trade sets on Linux (CI / AWS) vs
Windows (local dev) -- not floating-point noise but different
(ticker, strategy, direction, dates) tuples. AWS production runs
Linux, so the Windows local-pyramid has been validating a DIFFERENT
engine output than what actually deploys.

This test framework:

  (1) Runs the platform-fingerprint harness on the current platform
      and dumps indicator-level SHA-256 hashes.
  (2) Compares against the committed baseline for the SAME platform
      (Windows now lives at fixtures/platform_determinism_windows.json;
      a future Linux baseline will live at .._linux.json).
  (3) When BOTH baselines exist, diffs them indicator-by-indicator
      and surfaces the FIRST mismatch (the prime suspect).

Workflow to root-cause DET1:

  - Owner approves: run `python scripts/check_platform_determinism.py
    --output backtest/tests/fixtures/platform_determinism_linux.json`
    on a Linux box (CI runner, AWS instance, Docker).
  - Commit the Linux fixture.
  - The cross-platform diff test below activates + names the first
    diverging indicator. That indicator's underlying library (numpy /
    pandas / pandas-ta / TA / ta-lib / numba-compiled SMC) is the
    fix target.
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURES = REPO / "backtest" / "tests" / "fixtures"


def _platform_baseline_path() -> Path:
    """Return the baseline file matching the current OS."""
    system = platform.system().lower()
    return FIXTURES / f"platform_determinism_{system}.json"


def _load_baseline(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _current_fingerprints() -> dict:
    from scripts.check_platform_determinism import run as run_harness
    return run_harness()


# ---------------------------------------------------------------------------
# Same-platform regression guard
# ---------------------------------------------------------------------------

def test_batch498_current_platform_baseline_matches():
    """Fingerprints on the CURRENT platform must match the committed
    baseline for that same platform. If they diverge, a library
    upgrade (numpy / pandas) has shifted numerics -- update the
    baseline AFTER confirming the new values are correct.
    """
    baseline_path = _platform_baseline_path()
    baseline = _load_baseline(baseline_path)
    if baseline is None:
        pytest.skip(
            f"No baseline for current platform at {baseline_path.name}; "
            f"run `python scripts/check_platform_determinism.py "
            f"--output {baseline_path}` then commit."
        )
    current = _current_fingerprints()
    # Compare indicator-level fingerprints exactly
    expected = baseline["indicator_fingerprints"]
    actual   = current["indicator_fingerprints"]
    mismatches = []
    for name, expected_hash in expected.items():
        actual_hash = actual.get(name, "MISSING")
        if expected_hash != actual_hash:
            mismatches.append((name, expected_hash, actual_hash))
    assert not mismatches, (
        f"Same-platform regression: {len(mismatches)} indicators "
        f"changed. First mismatch: {mismatches[0]}. Library upgrade "
        f"path: numpy {baseline['numpy_version']} -> "
        f"{current['numpy_version']}; pandas {baseline['pandas_version']} "
        f"-> {current['pandas_version']}."
    )


# ---------------------------------------------------------------------------
# Cross-platform diff (activates only when both baselines exist)
# ---------------------------------------------------------------------------

def test_batch498_cross_platform_diff_when_both_baselines_present():
    """Once a Linux baseline is committed alongside Windows, this test
    runs the diff that root-causes DET1. It does NOT FAIL if they
    differ -- DET1 is the known issue -- but it does PRINT the diff so
    the diagnostic surfaces in CI logs.

    To make this test ASSERT parity (after DET1 is fixed): flip the
    final `assert True` to `assert not divergences`.
    """
    win_path   = FIXTURES / "platform_determinism_windows.json"
    linux_path = FIXTURES / "platform_determinism_linux.json"
    if not (win_path.exists() and linux_path.exists()):
        pytest.skip(
            "Need BOTH platform baselines committed to run cross-platform "
            "diff. Missing: "
            + ", ".join(p.name for p in (win_path, linux_path)
                         if not p.exists())
        )
    win   = json.loads(win_path.read_text(encoding="utf-8"))
    linux = json.loads(linux_path.read_text(encoding="utf-8"))
    win_fps   = win["indicator_fingerprints"]
    linux_fps = linux["indicator_fingerprints"]
    divergences = []
    for name in sorted(set(win_fps) | set(linux_fps)):
        w = win_fps.get(name, "missing-win")
        l = linux_fps.get(name, "missing-linux")
        if w != l:
            divergences.append({
                "indicator": name,
                "windows":   w[:16],
                "linux":     l[:16],
            })
    # Print so CI logs surface the diagnostic, do not fail (DET1 known)
    if divergences:
        print(f"\nDET1 cross-platform divergences "
              f"({len(divergences)} indicators):")
        for d in divergences[:10]:
            print(f"  - {d['indicator']:30s} "
                  f"win={d['windows']}... linux={d['linux']}...")
    # Flip this assertion to `assert not divergences` once DET1 is fixed.
    assert True


# ---------------------------------------------------------------------------
# Harness self-test
# ---------------------------------------------------------------------------

def test_batch498_harness_runs_deterministically_in_process():
    """Two back-to-back invocations of the harness on the same process
    must return IDENTICAL fingerprints. Catches any accidental non-
    deterministic intermediate (e.g. dict-iteration order leaking
    into a hash)."""
    fp1 = _current_fingerprints()["indicator_fingerprints"]
    fp2 = _current_fingerprints()["indicator_fingerprints"]
    assert fp1 == fp2, (
        "Harness is non-deterministic in-process -- a hash dependency "
        "leaks somewhere in the pipeline."
    )


def test_batch498_harness_emits_known_indicators():
    """Pin the indicator set so a refactor that drops a hash from the
    output surfaces here."""
    fp = _current_fingerprints()["indicator_fingerprints"]
    required = {
        "close_raw", "close_pct_change", "close_log_returns",
        "close_ema_20", "close_sma_20", "close_std_20",
        "atr_14", "rsi_14", "bollinger_width_20",
    }
    missing = required - set(fp.keys())
    assert not missing, f"harness dropped indicators: {missing}"


def test_batch498_windows_baseline_present_and_well_formed():
    """The Windows baseline must exist + be loadable + carry every
    required indicator. Linux baseline absence is allowed (deferred
    until owner approves the run)."""
    path = FIXTURES / "platform_determinism_windows.json"
    assert path.exists(), f"Windows baseline missing at {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["system"] == "Windows"
    assert "indicator_fingerprints" in data
    assert len(data["indicator_fingerprints"]) >= 9
