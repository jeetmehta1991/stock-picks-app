"""Batch 508 (2026-05-31) -- DET1 workflow_dispatch step tests.

Source: per CHECKLIST #77 + owner directive 2026-05-31.
Queue row: EXECUTION_QUEUE.md item DET1.
Workflow: .github/workflows/det1-platform-determinism.yml.

Test surface is intentionally narrow: the YAML file exists, parses,
declares workflow_dispatch, calls the harness script, and commits the
expected fixture path. CI itself validates the workflow runs end-to-end
when owner triggers it.
"""
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "det1-platform-determinism.yml"


def test_batch508_workflow_file_exists():
    assert WORKFLOW.exists(), f"DET1 workflow not at {WORKFLOW}"


def test_batch508_workflow_is_valid_yaml():
    """Parses as YAML without error."""
    try:
        import yaml
    except ImportError:
        pytest.skip("pyyaml not installed; YAML validation skipped")
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "jobs" in data
    # PyYAML parses bare `on:` as boolean True (truthy YAML quirk).
    # Accept either the string key 'on' or the Python bool True.
    assert ("on" in data) or (True in data), (
        f"workflow missing 'on:' trigger; keys={list(data.keys())}"
    )


def test_batch508_workflow_declares_workflow_dispatch():
    src = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in src


def test_batch508_workflow_runs_harness_with_linux_fixture_output():
    src = WORKFLOW.read_text(encoding="utf-8")
    assert "scripts/check_platform_determinism.py" in src
    assert "backtest/tests/fixtures/platform_determinism_linux.json" in src


def test_batch508_workflow_commits_back_to_branch():
    """Workflow must `git commit` + `git push` so the fixture lands in
    the repo without manual operator intervention."""
    src = WORKFLOW.read_text(encoding="utf-8")
    assert "git commit" in src
    assert "git push" in src
    # Permissions block needed for github-actions[bot] push
    assert "contents: write" in src


def test_batch508_workflow_target_branch_input_present():
    """Owner picks branch via workflow_dispatch input."""
    src = WORKFLOW.read_text(encoding="utf-8")
    assert "target_branch" in src
    assert "inputs.target_branch" in src
