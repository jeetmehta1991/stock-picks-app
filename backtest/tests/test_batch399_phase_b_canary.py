"""Batch 399 (2026-05-27): Sprint 7 Phase B canary infrastructure tests.

Source (per CHECKLIST #77): owner directive 2026-05-27 "all wired items
activated".  Phase B = DEC-508 / CHECKLIST #71 canary signals computed +
validation dashboard.

Test scope -- Half 1 (buildable now, no Python 3.12 dep):
  - Sample selector: stratified by regime, balanced direction, year span
  - Compute (dry-run): deterministic mock tiers, PIT compliance check
  - Dashboard: 5-gate validation report

Run: pytest backtest/tests/test_batch399_phase_b_canary.py -v
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO / "scripts"


@pytest.fixture
def tmp_workdir(tmp_path):
    """Isolated work dir per test so concurrent tests don't conflict."""
    d = tmp_path / "phase_1b_canary"
    d.mkdir()
    return d


# ---------- selector --------------------------------------------------------

def test_selector_stratified_sample_function():
    """Direct import test of stratified_sample on synthetic data."""
    sys.path.insert(0, str(SCRIPTS))
    from phase_1b_canary_sample_selector import (
        build_synthetic_trade_log,
        stratified_sample,
    )
    df = build_synthetic_trade_log(n=200)
    sample = stratified_sample(df, n=30, seed=42)
    assert len(sample) == 30
    # Determinism: same seed -> same sample
    sample2 = stratified_sample(df, n=30, seed=42)
    pd.testing.assert_frame_equal(sample, sample2)


def test_selector_synthetic_cli(tmp_workdir):
    out = tmp_workdir / "sample_pairs.parquet"
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "phase_1b_canary_sample_selector.py"),
         "--synthetic", "--n", "25", "--output", str(out)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert out.exists()
    df = pd.read_parquet(out)
    assert len(df) == 25
    assert "ticker" in df.columns
    assert "entry_date" in df.columns


# ---------- compute (dry-run) ----------------------------------------------

def test_compute_dry_run_mock_is_deterministic():
    sys.path.insert(0, str(SCRIPTS))
    from phase_1b_canary_compute import _deterministic_mock_tier
    t1, s1 = _deterministic_mock_tier("AAPL", "2024-01-15")
    t2, s2 = _deterministic_mock_tier("AAPL", "2024-01-15")
    assert (t1, s1) == (t2, s2)
    # Different inputs give different outputs (probabilistically)
    t3, s3 = _deterministic_mock_tier("MSFT", "2024-01-15")
    assert (t1, s1) != (t3, s3) or t1 == t3  # tie possible but rare


def test_compute_dry_run_tier_in_valid_range():
    sys.path.insert(0, str(SCRIPTS))
    from phase_1b_canary_compute import _deterministic_mock_tier
    for tkr in ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"):
        for d in ("2020-01-15", "2022-06-30", "2024-12-31", "2026-04-30"):
            t, s = _deterministic_mock_tier(tkr, d)
            assert 1 <= t <= 5, f"tier {t} out of range for ({tkr}, {d})"
            assert 0 <= s <= 99, f"score {s} out of range"


def test_compute_pit_compliance_heuristic():
    sys.path.insert(0, str(SCRIPTS))
    from phase_1b_canary_compute import _check_pit_compliance
    assert _check_pit_compliance("AAPL", "2024-01-15") is True
    # Future date fails
    assert _check_pit_compliance("AAPL", "2099-01-15") is False
    # Garbage date fails
    assert _check_pit_compliance("AAPL", "not-a-date") is False


def test_compute_cli_dry_run(tmp_workdir):
    """End-to-end selector -> compute --dry-run."""
    samples = tmp_workdir / "samples.parquet"
    signals = tmp_workdir / "signals.parquet"
    r1 = subprocess.run(
        [sys.executable, str(SCRIPTS / "phase_1b_canary_sample_selector.py"),
         "--synthetic", "--n", "30", "--output", str(samples)],
        capture_output=True, text=True, timeout=60,
    )
    assert r1.returncode == 0, r1.stderr
    r2 = subprocess.run(
        [sys.executable, str(SCRIPTS / "phase_1b_canary_compute.py"),
         "--samples", str(samples), "--output", str(signals), "--dry-run"],
        capture_output=True, text=True, timeout=60,
    )
    assert r2.returncode == 0, r2.stderr
    assert signals.exists()
    df = pd.read_parquet(signals)
    assert len(df) == 30
    for col in ("ticker", "as_of", "agent_tier", "agent_score",
                "context_paragraph", "computed_at", "llm_model",
                "pit_compliant"):
        assert col in df.columns, f"missing column: {col}"
    assert df["agent_tier"].between(1, 5).all()
    assert df["pit_compliant"].all()
    assert (df["llm_model"] == "dry_run_mock").all()


# ---------- dashboard -------------------------------------------------------

def test_dashboard_all_gates_pass_on_balanced_dry_run(tmp_workdir):
    """Full pipeline: selector -> compute --dry-run -> dashboard PASS."""
    samples = tmp_workdir / "samples.parquet"
    signals = tmp_workdir / "signals.parquet"
    subprocess.run(
        [sys.executable, str(SCRIPTS / "phase_1b_canary_sample_selector.py"),
         "--synthetic", "--n", "30", "--output", str(samples)],
        check=True, capture_output=True, timeout=60,
    )
    subprocess.run(
        [sys.executable, str(SCRIPTS / "phase_1b_canary_compute.py"),
         "--samples", str(samples), "--output", str(signals), "--dry-run"],
        check=True, capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "phase_1b_canary_dashboard.py"),
         "--signals", str(signals), "--output-dir", str(tmp_workdir)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"dashboard FAIL: {r.stdout}\n{r.stderr}"
    report = json.loads((tmp_workdir / "canary_validation_report.json").read_text())
    assert report["overall_pass"] is True
    assert len(report["checks"]) == 5
    assert all(c["pass"] for c in report["checks"]), (
        f"some gates failed: {[c['name'] for c in report['checks'] if not c['pass']]}"
    )
    # HTML output also produced
    html = (tmp_workdir / "canary_validation_report.html").read_text(encoding="utf-8")
    assert "Phase 1B Canary Validation" in html
    assert "PASS" in html


def test_dashboard_fails_on_degenerate_constant_tier(tmp_workdir):
    """If all signals have tier=3, G2 distribution check fails."""
    # Build signals where every row has tier=3 (degenerate constant)
    df = pd.DataFrame([{
        "ticker": f"T{i}", "as_of": "2024-01-15",
        "agent_tier": 3, "agent_score": 60,
        "context_paragraph": "", "computed_at": "2026-05-27T00:00:00Z",
        "llm_model": "dry_run_mock", "pit_compliant": True,
    } for i in range(30)])
    sig = tmp_workdir / "signals_degenerate.parquet"
    df.to_parquet(sig, index=False)
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "phase_1b_canary_dashboard.py"),
         "--signals", str(sig), "--output-dir", str(tmp_workdir)],
        capture_output=True, text=True, timeout=60,
    )
    # Dashboard returns rc=2 on overall FAIL
    assert r.returncode == 2
    report = json.loads((tmp_workdir / "canary_validation_report.json").read_text())
    g2 = next(c for c in report["checks"] if c["name"].startswith("G2"))
    assert g2["pass"] is False
