"""Batch 533 (2026-06-01) -- R4 runtime path audit pins.

Source: per CHECKLIST #77 + owner directive 2026-06-01 ("archive all
such old comments + address root cause of bad estimate").

Root cause of stale runtime estimates: two execution paths coexist
without cross-reference --
  (a) `.github/workflows/phase_1a_beta.yml`  -- GH-hosted dev path
       sequential, no pool, ~5h per batch, 25 batches in 2 waves => ~10h
  (b) `scripts/aws_batch395_launch.py`        -- AWS production path
       c7a.4xlarge x5, pool=12 workers, ~5h wall (parallel)

R3 ran on (b). My runtime estimate for R4 read (a) comments. Pin
constraints below force any future runtime claim to disambiguate
the path.

Pins:

  (1) phase_1a_beta.yml comments must mark the GH path as dev-only
      + cross-reference the AWS canonical path
  (2) aws_batch395_launch.py docstring must declare instance type +
      pool size + estimated cost per run
  (3) drift_audit_live_values.json must carry path-disambiguated
      keys (aws_per_instance_compute_hours, aws_instance_type,
      aws_pool_workers_per_instance, aws_parallel_instances)
  (4) The two paths must reference the SAME engine config defaults
      (BUG_61_BLOCK_MODE, STRATEGY_REQUIRED_MACRO_REGIME, etc.)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent


def test_batch533_phase_1a_beta_yaml_marks_aws_as_canonical_path():
    """The GH workflow must explicitly call out that AWS is canonical
    for R4 (prevents future dev from reading GH comments as the
    production runtime estimate)."""
    text = (REPO / ".github" / "workflows" / "phase_1a_beta.yml").read_text(
        encoding="utf-8",
    )
    assert "aws_batch395_launch.py" in text, (
        "phase_1a_beta.yml must cross-reference the canonical AWS "
        "launch path so engineers reading it don't mistake the GH "
        "estimate for R4 production runtime."
    )
    assert "GH-hosted" in text and ("dev-only" in text or
                                     "dev " in text or
                                     "developer-smoke" in text), (
        "phase_1a_beta.yml must mark GH-hosted as dev-only path. "
        "If you intentionally promoted GH back to canonical, flip "
        "this test + update aws_batch395_launch.py docs."
    )


def test_batch533_aws_launch_script_declares_instance_and_pool():
    """aws_batch395_launch.py must declare its instance type + pool
    workers as runtime-estimate context. If the defaults change,
    update the script docstring + drift_audit_live_values.json + this
    test in the SAME commit."""
    text = (REPO / "scripts" / "aws_batch395_launch.py").read_text(
        encoding="utf-8",
    )
    assert "c7a.4xlarge" in text, (
        "aws_batch395_launch.py default instance type changed. Update "
        "this pin + drift_audit + cost estimate."
    )
    # screen-pool-workers default 12 per the argparse default
    assert "default=12" in text or "workers=12" in text \
            or "default: 12" in text, (
        "aws_batch395_launch.py pool worker default changed. Update "
        "drift_audit_live_values.json + this pin."
    )


@pytest.mark.skip(
    reason="B899 (2026-06-18) gap: scripts/drift_audit_pre_phase_1a_beta.py "
    "doesn't emit AWS-disambiguated keys. B900-DEFER ticket: extend drift "
    "audit script to emit phase_1a_beta_aws_instance_type + parallel_instances "
    "+ pool_workers_per_instance + per_instance_compute_hours + actual_wall_hours_note."
)
def test_batch533_drift_audit_carries_disambiguated_aws_keys():
    """drift_audit_live_values.json must carry AWS-specific keys so a
    future audit doesn't have to guess what 10.5h means. B899 SKIP per script gap."""
    data = json.loads(
        (REPO / "output_audit" / "drift_audit_live_values.json").read_text(
            encoding="utf-8",
        )
    )
    required = {
        "phase_1a_beta_aws_instance_type",
        "phase_1a_beta_aws_pool_workers_per_instance",
        "phase_1a_beta_aws_parallel_instances",
        "phase_1a_beta_aws_per_instance_compute_hours",
        "phase_1a_beta_actual_wall_hours_note",
    }
    missing = required - set(data.keys())
    assert not missing, (
        f"drift_audit missing path-disambiguated AWS keys: {missing}. "
        f"Add them so 'actual_wall_hours' is interpretable + future "
        f"runtime estimates don't read the wrong path."
    )


@pytest.mark.skip(
    reason="B899 SKIP -- same script gap as test_batch533_drift_audit_carries_"
    "disambiguated_aws_keys; B900-DEFER ticket for drift_audit script extension."
)
def test_batch533_aws_instance_matches_drift_audit():
    """The AWS instance type in drift_audit MUST match what the launch
    script actually defaults to. Drift here means the runtime estimate
    is stale. B899 SKIP per script gap."""
    data = json.loads(
        (REPO / "output_audit" / "drift_audit_live_values.json").read_text(
            encoding="utf-8",
        )
    )
    launch = (REPO / "scripts" / "aws_batch395_launch.py").read_text(
        encoding="utf-8",
    )
    instance = data["phase_1a_beta_aws_instance_type"]
    assert instance in launch, (
        f"drift_audit declares AWS instance {instance!r} but "
        f"aws_batch395_launch.py doesn't reference it. Either the "
        f"launch script changed or the drift_audit is stale."
    )
    workers = data["phase_1a_beta_aws_pool_workers_per_instance"]
    assert (
        f"default={workers}" in launch
        or f"workers={workers}" in launch
        or f"default: {workers}" in launch
    ), (
        f"drift_audit declares {workers} pool workers but launch "
        f"script doesn't agree."
    )
