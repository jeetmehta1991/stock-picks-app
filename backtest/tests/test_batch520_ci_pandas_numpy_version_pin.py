"""Batch 520 (2026-05-31) -- DET1 production fix: CI version-pin regression guard.

Source: per CHECKLIST #77 + EXECUTION_QUEUE.md DET1 production-fix line.

The DET1 cross-platform diff (Batch 518) showed that rsi_14 diverges sub-
epsilon between Windows-local (pandas 3.0.2 + numpy 2.4.4) and Linux CI
(pandas 3.0.3 + numpy 2.4.6). Batch 518c accepted the divergence via an
allow-list (ACCEPTED_DIVERGENT = {"rsi_14"}); Batch 520 closes it at the
root by pinning CI to the same versions as the committed Windows baseline.

This test prevents silent drift: if anyone edits the workflows back to
`pip install pandas numpy` (unpinned) the regression guard fires and
flags the change BEFORE CI runs the diff harness with mismatched libs.

Pinned versions (must match the Windows fingerprint baseline at
backtest/tests/fixtures/platform_determinism_windows.json):

  pandas == 3.0.2
  numpy  == 2.4.4
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent
WORKFLOWS = REPO / ".github" / "workflows"
PIN_PANDAS = "3.0.2"
PIN_NUMPY = "2.4.4"

# Workflows where the engine touches data: must pin both libs.
ENGINE_WORKFLOWS = (
    "test-pyramid.yml",
    "det1-platform-determinism.yml",
    "phase_1a_beta.yml",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_batch520_test_pyramid_pins_pandas_and_numpy():
    """test-pyramid.yml runs the full 13-tier pyramid on Linux. Its
    pandas/numpy must match the Windows baseline EXACTLY (no >= or ~=)
    so that the DET1 cross-platform diff stays clean."""
    text = _read(WORKFLOWS / "test-pyramid.yml")
    # Must reference the pinned versions at least once per job step
    # (matrix `pyramid` + `informational` job both install deps).
    assert text.count(f'"pandas=={PIN_PANDAS}"') >= 2, (
        f"test-pyramid.yml must pin pandas=={PIN_PANDAS} in both pyramid + "
        f"informational install steps; found "
        f"{text.count(f'\"pandas=={PIN_PANDAS}\"')}"
    )
    assert text.count(f'"numpy=={PIN_NUMPY}"') >= 2, (
        f"test-pyramid.yml must pin numpy=={PIN_NUMPY} in both pyramid + "
        f"informational install steps."
    )


def test_batch520_det1_workflow_pins_pandas_and_numpy():
    """The DET1 baseline-generator workflow MUST install the exact
    pinned versions so the Linux fingerprint it emits is bit-identical
    to the Windows baseline. Mismatched libs produce a phantom DET1."""
    text = _read(WORKFLOWS / "det1-platform-determinism.yml")
    assert f'"pandas=={PIN_PANDAS}"' in text, (
        f"det1-platform-determinism.yml must pin pandas=={PIN_PANDAS} -- "
        f"otherwise the Linux baseline reproduces the rsi_14 drift this "
        f"workflow exists to root-cause."
    )
    assert f'"numpy=={PIN_NUMPY}"' in text, (
        f"det1-platform-determinism.yml must pin numpy=={PIN_NUMPY}."
    )


def test_batch520_phase_1a_beta_pins_pandas_and_numpy():
    """phase_1a_beta.yml runs the actual cube. Its install steps
    (prepare + batch + merge) must use the pinned versions so the
    cube emitted on CI matches local-dev runs trade-for-trade."""
    text = _read(WORKFLOWS / "phase_1a_beta.yml")
    # 3 install steps -> 3 occurrences each
    assert text.count(f'"pandas=={PIN_PANDAS}"') >= 3, (
        f"phase_1a_beta.yml must pin pandas=={PIN_PANDAS} in prepare + "
        f"batch + merge install steps; found "
        f"{text.count(f'\"pandas=={PIN_PANDAS}\"')}"
    )
    assert text.count(f'"numpy=={PIN_NUMPY}"') >= 3, (
        f"phase_1a_beta.yml must pin numpy=={PIN_NUMPY} in prepare + "
        f"batch + merge install steps."
    )


def test_batch520_no_unpinned_pandas_in_engine_workflows():
    """Regression guard: catch reverts to `pip install pandas numpy`
    (unpinned) in any engine-touching workflow."""
    unpinned_pat = re.compile(
        r"pip install (?:(?!\"pandas==)[\w\-=\s\"]+\s+)?pandas\b(?!==)",
    )
    for name in ENGINE_WORKFLOWS:
        text = _read(WORKFLOWS / name)
        # Look for `pandas` token NOT immediately followed by ==
        matches = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped.startswith("pip install"):
                continue
            # Tokenize and check each token
            for token in stripped.split():
                if token == "pandas" or token.startswith("pandas "):
                    matches.append((line_no, line))
                    break
                if token == "pandas-ta" or token == "pandas-market-calendars":
                    continue  # OK; these are unpinned but not the core lib
        assert not matches, (
            f"{name} has unpinned `pandas` token(s) at line(s) "
            f"{[m[0] for m in matches]}: {[m[1] for m in matches]}. "
            f"All engine workflows must pin pandas=={PIN_PANDAS}."
        )


def test_batch520_pinned_versions_match_windows_baseline():
    """The pinned values here must match what the committed Windows
    baseline was generated against. If the baseline is regenerated
    against newer libs, update PIN_PANDAS + PIN_NUMPY here too."""
    baseline_path = (
        REPO / "backtest" / "tests" / "fixtures"
        / "platform_determinism_windows.json"
    )
    if not baseline_path.exists():
        pytest.skip("Windows baseline missing -- nothing to pin against")
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    assert data["pandas_version"] == PIN_PANDAS, (
        f"Pin mismatch: PIN_PANDAS={PIN_PANDAS} but Windows baseline was "
        f"generated against pandas {data['pandas_version']}. Either "
        f"regenerate the baseline against {PIN_PANDAS} OR bump PIN_PANDAS "
        f"+ all workflow pins to {data['pandas_version']}."
    )
    assert data["numpy_version"] == PIN_NUMPY, (
        f"Pin mismatch: PIN_NUMPY={PIN_NUMPY} but Windows baseline was "
        f"generated against numpy {data['numpy_version']}. Either "
        f"regenerate the baseline OR bump the pin."
    )
