"""Tests for Phase 1B-alpha launcher scripts (Batch 256)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]


def _make_winners_file(tmp_path, n_p1=5):
    winners = pd.DataFrame({
        "combo_id":      [f"strat{i}__atr__bull" for i in range(n_p1)],
        "strategy":      [f"strat{i}" for i in range(n_p1)],
        "exit_method":   ["atr_trail_1x"] * n_p1,
        "regime":        ["bull"] * n_p1,
        "n_trades":      [50] * n_p1,
        "win_rate":      [0.6] * n_p1,
        "sharpe":        [1.5] * n_p1,
        "priority":      ["P1"] * n_p1,
        "tickers_fired": [["AAPL"] for _ in range(n_p1)],
    })
    out_dir = tmp_path / "output_v2"
    out_dir.mkdir()
    winners.to_parquet(out_dir / "winners.parquet", index=False)
    return out_dir / "winners.parquet"


def _run_script(script_name, *args, cwd=None):
    return subprocess.run(
        [sys.executable, str(REPO / "scripts" / script_name), *args],
        capture_output=True, text=True, timeout=60, cwd=cwd or REPO,
    )


def test_smoke_help():
    r = _run_script("run_phase_1b_alpha_smoke.py", "--help")
    assert r.returncode == 0
    assert "budget-cap" in r.stdout


def test_demo_help():
    r = _run_script("run_phase_1b_alpha_demo.py", "--help")
    assert r.returncode == 0


def test_full_help():
    r = _run_script("run_phase_1b_alpha.py", "--help")
    assert r.returncode == 0
    assert "include-p2" in r.stdout


def test_full_rejects_over_300_cap():
    r = _run_script("run_phase_1b_alpha.py", "--budget-cap", "500", "--dry-run")
    assert r.returncode == 1
    assert "owner-approved" in r.stdout.lower() or "300" in r.stdout


def test_smoke_missing_winners(tmp_path):
    r = _run_script("run_phase_1b_alpha_smoke.py",
                    "--winners", str(tmp_path / "missing.parquet"),
                    cwd=tmp_path)
    assert r.returncode == 1


def test_smoke_with_valid_winners(tmp_path):
    winners_path = _make_winners_file(tmp_path)
    r = _run_script("run_phase_1b_alpha_smoke.py",
                    "--winners", str(winners_path),
                    "--output-dir", str(tmp_path / "smoke_out"),
                    "--dry-run")
    assert r.returncode == 0
    assert (tmp_path / "smoke_out" / "manifest.json").exists()


def test_demo_with_valid_winners(tmp_path):
    winners_path = _make_winners_file(tmp_path, n_p1=25)
    r = _run_script("run_phase_1b_alpha_demo.py",
                    "--winners", str(winners_path),
                    "--output-dir", str(tmp_path / "demo_out"),
                    "--dry-run")
    assert r.returncode == 0
    assert (tmp_path / "demo_out" / "manifest.json").exists()


def test_full_with_valid_winners(tmp_path):
    winners_path = _make_winners_file(tmp_path, n_p1=10)
    r = _run_script("run_phase_1b_alpha.py",
                    "--winners", str(winners_path),
                    "--output-dir", str(tmp_path / "full_out"),
                    "--dry-run",
                    "--budget-cap", "150")
    assert r.returncode == 0
    assert (tmp_path / "full_out" / "manifest.json").exists()
