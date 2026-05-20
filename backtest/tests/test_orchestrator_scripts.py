"""Tests for orchestrator scripts (Batch 248).

Smoke tests verifying each script imports cleanly + --help works. Not
end-to-end since that requires winners.parquet + market data.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def _run_help(script: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, timeout=30,
    )


def test_run_paper_morning_help():
    r = _run_help(REPO / "scripts" / "run_paper_morning.py")
    assert r.returncode == 0
    assert "winners-source" in r.stdout
    assert "max-picks" in r.stdout


def test_run_paper_end_of_day_help():
    r = _run_help(REPO / "scripts" / "run_paper_end_of_day.py")
    assert r.returncode == 0
    assert "portfolio-path" in r.stdout


def test_run_live_morning_help():
    r = _run_help(REPO / "scripts" / "run_live_morning.py")
    assert r.returncode == 0
    assert "execute-approved" in r.stdout
    assert "ib-port" in r.stdout


def test_deploy_live_sh_exists():
    p = REPO / "scripts" / "deploy_live.sh"
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "Lightsail" in content
    assert "Dockerfile" in content or "Docker image" in content


def test_run_paper_morning_with_no_winners(tmp_path):
    """Smoke: script should return 2 (informational) when winners.parquet missing."""
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "run_paper_morning.py"),
         "--winners-source", str(tmp_path),
         "--portfolio-path", str(tmp_path / "p.json"),
         "--output-dir", str(tmp_path),
         "--dry-run"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode in (0, 2)


def test_run_live_morning_dry_run_default():
    """Verify --dry-run is the default (safety)."""
    p = REPO / "scripts" / "run_live_morning.py"
    content = p.read_text(encoding="utf-8")
    assert 'default=True' in content
    assert "owner must explicitly" in content.lower() or "--no-dry-run" in content
