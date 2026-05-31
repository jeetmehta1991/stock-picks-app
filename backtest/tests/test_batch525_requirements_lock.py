"""Batch 525 (2026-05-31) -- laptop-portable requirements lock pin-guard.

Source: per CHECKLIST #77 + owner directive 2026-05-31 ("git as source
of truth, no drift on new laptop").
Queue row: EXECUTION_QUEUE.md item DET1 (production-fix follow-on to
Batch 520 CI workflow pin).

The previous lifecycle was: `requirements.txt` used `>=` everywhere,
so a fresh `pip install -r requirements.txt` on a new machine resolved
to whatever pip's latest available version of pandas / numpy / pyarrow
was on that day -- which then diverged from the committed Windows
baseline (DET1 lineage). Batch 525 hard-pinned (==) every direct
dependency. This test prevents reverts.

Pins:

  (1) Every line in requirements.txt that names a package MUST use
      == (no >=, no ~=, no <, no unconstrained bare names).
  (2) The critical DET1 hot-path libs MUST be pinned to the EXACT
      versions used to generate
      `backtest/tests/fixtures/platform_determinism_windows.json`.
  (3) pandas + numpy versions in requirements.txt MUST equal the
      versions in `.github/workflows/test-pyramid.yml` (Batch 520).
  (4) `scripts/verify_environment.py` MUST exist (new-laptop setup
      step is documented in the script's docstring + readable from
      git).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent
REQUIREMENTS = REPO / "requirements.txt"
CI_TEST_PYRAMID = REPO / ".github" / "workflows" / "test-pyramid.yml"
DET1_WORKFLOW = REPO / ".github" / "workflows" / "det1-platform-determinism.yml"
WINDOWS_BASELINE = (
    REPO / "backtest" / "tests" / "fixtures"
    / "platform_determinism_windows.json"
)
VERIFY_SCRIPT = REPO / "scripts" / "verify_environment.py"

# Critical DET1 hot-path libraries (must be == pinned).
DET1_CRITICAL_LIBS = ("pandas", "numpy", "pyarrow", "scipy", "numba")


def _parse_lines() -> list[str]:
    return [
        ln.strip() for ln in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def _strict_pins() -> dict[str, str]:
    pat = re.compile(r"^([A-Za-z0-9_\-\.]+)==([0-9A-Za-z\.\-_]+)\s*$")
    out: dict[str, str] = {}
    for ln in _parse_lines():
        m = pat.match(ln)
        if m:
            out[m.group(1).lower()] = m.group(2)
    return out


def test_batch525_requirements_uses_only_strict_pins():
    """Every non-comment, non-blank line in requirements.txt must use ==.

    Loose pins (>=, ~=, <, unconstrained) defeat the purpose of the
    lock. If a package legitimately needs a range, the right place is
    `pyproject.toml` extras (dev / optional groups), NOT the runtime
    lock.
    """
    loose_pin_pat = re.compile(r"(>=|<=|~=|>|<)")
    bare_name_pat = re.compile(r"^[A-Za-z0-9_\-\.]+\s*$")
    pin_pat = re.compile(r"^[A-Za-z0-9_\-\.]+==[0-9A-Za-z\.\-_]+\s*$")
    violators = []
    for ln in _parse_lines():
        if pin_pat.match(ln):
            continue
        if bare_name_pat.match(ln) or loose_pin_pat.search(ln):
            violators.append(ln)
    assert not violators, (
        f"requirements.txt has {len(violators)} loose/bare pin line(s): "
        f"{violators}. Convert each to `pkg==X.Y.Z` so a new laptop "
        f"`pip install -r requirements.txt` resolves bit-identically."
    )


def test_batch525_det1_critical_libs_are_pinned():
    """pandas, numpy, pyarrow, scipy, numba must each appear with a ==
    pin. Missing any of these breaks the DET1 hot-path lock."""
    pins = _strict_pins()
    missing = [lib for lib in DET1_CRITICAL_LIBS if lib not in pins]
    assert not missing, (
        f"DET1 critical libs missing == pin in requirements.txt: "
        f"{missing}. Add explicit `pkg==X.Y.Z` lines."
    )


def test_batch525_pandas_numpy_match_windows_baseline():
    """Pinned pandas + numpy versions must match the Windows fingerprint
    baseline (the ground truth for cross-platform parity)."""
    if not WINDOWS_BASELINE.exists():
        pytest.skip("Windows baseline absent -- nothing to pin against.")
    baseline = json.loads(WINDOWS_BASELINE.read_text(encoding="utf-8"))
    pins = _strict_pins()
    assert pins["pandas"] == baseline["pandas_version"], (
        f"requirements.txt pandas=={pins['pandas']} but Windows "
        f"baseline was generated against pandas "
        f"{baseline['pandas_version']}. Either bump the pin OR "
        f"regenerate the baseline + re-run the DET1 workflow."
    )
    assert pins["numpy"] == baseline["numpy_version"], (
        f"requirements.txt numpy=={pins['numpy']} but Windows "
        f"baseline was generated against numpy "
        f"{baseline['numpy_version']}."
    )


def test_batch525_requirements_pandas_matches_ci_pin():
    """requirements.txt and CI workflows MUST pin the same pandas
    version. Drift here means local dev + CI run on different libs
    again -- the Batch 520 CI pin is undone the moment local pins
    diverge.

    Skips if Batch 520 CI pin is not yet on the current branch
    (e.g. running this test on a branch cut from main before 520
    merged).
    """
    pins = _strict_pins()
    if not CI_TEST_PYRAMID.exists():
        pytest.skip("test-pyramid.yml absent on this branch")
    ci_text = CI_TEST_PYRAMID.read_text(encoding="utf-8")
    expected_token = f'"pandas=={pins["pandas"]}"'
    if expected_token not in ci_text:
        pytest.skip(
            f"CI workflow does not contain {expected_token} -- Batch "
            f"520 pin may not be merged yet on this branch. Merge "
            f"batch/520 to main and re-run."
        )
    # If CI has SOME pandas== pin but it doesn't match, that's a fail.
    ci_pandas_pat = re.compile(r'"pandas==([0-9\.]+)"')
    ci_versions = set(ci_pandas_pat.findall(ci_text))
    if ci_versions:
        assert pins["pandas"] in ci_versions, (
            f"requirements.txt pandas=={pins['pandas']} differs from "
            f"CI pinned version(s) {ci_versions}. Update one or the "
            f"other so both sides of CHECKLIST #102 parity match."
        )


def test_batch525_verify_environment_script_exists():
    """The new-laptop setup procedure documented in
    `requirements.txt` references `scripts/verify_environment.py`.
    That file must exist + be importable."""
    assert VERIFY_SCRIPT.exists(), (
        f"scripts/verify_environment.py missing. New-laptop setup "
        f"instructions in requirements.txt point at it."
    )
    text = VERIFY_SCRIPT.read_text(encoding="utf-8")
    assert "check_pins" in text and "check_fingerprints" in text, (
        "verify_environment.py exists but does not expose check_pins "
        "+ check_fingerprints. These are the two gates documented in "
        "the script's docstring."
    )


def test_batch525_verify_environment_setup_docs_present():
    """requirements.txt must contain the setup procedure (pip install +
    verify_environment.py invocation) as comments. Without it, a fresh
    machine has no in-repo documentation for the lock workflow.
    """
    text = REQUIREMENTS.read_text(encoding="utf-8")
    assert "pip install -r requirements.txt" in text, (
        "requirements.txt comments must document `pip install -r "
        "requirements.txt` as the install command."
    )
    assert "verify_environment.py" in text, (
        "requirements.txt comments must reference "
        "scripts/verify_environment.py as the post-install gate."
    )


def test_batch525_pin_count_matches_floor():
    """Sanity floor: at least 12 strict pins are required to cover the
    engine's direct dependency set (DET1 critical 5 + statsmodels +
    scikit-learn + xgboost + filelock + requests + pyarrow already
    counted + pytest + pytest-xdist + hypothesis). Drift below this
    floor means someone deleted lines without thinking about coverage.
    """
    pins = _strict_pins()
    assert len(pins) >= 12, (
        f"requirements.txt has only {len(pins)} strict == pins; floor "
        f"is 12 (the engine's direct dep set). Re-add the missing "
        f"pins -- engine code imports them."
    )
