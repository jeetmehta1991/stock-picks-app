"""Batches 352-354: forensic_phase1a_beta_recat.py regression tests.

Source (per CHECKLIST #77): owner directive 2026-05-25 "Start with forensic
batches." Tests pin the forensic analysis script so re-running it against
the Phase 1A-beta trade_log produces stable verdicts.

Pyramid tiers exercised:
  T1 (Unit)        summarize_strategy(0 trades) returns QUIET verdict
  T1 (Unit)        summarize_strategy(N>=20 trades) returns NORMAL verdict
  T1 (Unit)        per_strategy_verdict_against_criteria flags n<30 as INSUFFICIENT
  T1 (Unit)        per_strategy_verdict_against_criteria selects overall vs per-regime
                   threshold band based on n
  T1 (Unit)        Profit factor with no losses returns inf
  T2 (Smoke)       Script runs end-to-end on real Phase 1A-beta trade_log
  T6 (Regression)  Bucket lists in script match the forensic doc exactly
                   (UN_DEPRECATED_23 has 23 entries; Cat-A 14; Cat-B 20; Cat-C 16)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).parent.parent.parent
SCRIPT = REPO / "scripts" / "forensic_phase1a_beta_recat.py"
sys.path.insert(0, str(REPO / "scripts"))
import forensic_phase1a_beta_recat as fp  # type: ignore  # noqa: E402


# ---------------------------------------------------------------------
# T6 - Regression: bucket-list integrity
# ---------------------------------------------------------------------
def test_un_deprecated_23_has_23_entries():
    assert len(fp.UN_DEPRECATED_23) == 23


def test_cat_a_has_14_entries():
    assert len(fp.CAT_A_TIGHT) == 14


def test_cat_b_has_20_entries():
    assert len(fp.CAT_B_DATA_MISSING) == 20


def test_cat_c_has_16_entries():
    assert len(fp.CAT_C_INVESTIGATE) == 16


def test_bucket_strategy_names_are_unique_per_bucket():
    for name, bucket in fp.BUCKETS.items():
        assert len(bucket) == len(set(bucket)), f"duplicate in {name}"
    assert len(fp.UN_DEPRECATED_23) == len(set(fp.UN_DEPRECATED_23))


# ---------------------------------------------------------------------
# T1 - Unit: summarize_strategy
# ---------------------------------------------------------------------
def test_summarize_strategy_zero_trades_is_quiet():
    df = pd.DataFrame({"strategy": [], "win": [], "pnl_pct": [], "hold_days": []})
    r = fp.summarize_strategy(df, "missing")
    assert r["n_trades"] == 0
    assert r["verdict"] == "QUIET"


def test_summarize_strategy_rare_for_1_to_19_trades():
    df = pd.DataFrame({
        "strategy": ["x"] * 5,
        "win":      [True, False, True, True, False],
        "pnl_pct":  [1.0, -0.5, 0.5, 1.5, -1.0],
        "hold_days":[5, 5, 5, 5, 5],
    })
    r = fp.summarize_strategy(df, "x")
    assert r["n_trades"] == 5
    assert r["verdict"] == "RARE"
    assert r["wr_pct"] == 60.0


def test_summarize_strategy_normal_for_20plus_trades():
    df = pd.DataFrame({
        "strategy": ["x"] * 25,
        "win":      [True] * 25,
        "pnl_pct":  [1.0] * 25,
        "hold_days":[5] * 25,
    })
    r = fp.summarize_strategy(df, "x")
    assert r["n_trades"] == 25
    assert r["verdict"] == "NORMAL"


# ---------------------------------------------------------------------
# T1 - Unit: per_strategy_verdict_against_criteria
# ---------------------------------------------------------------------
def test_criteria_verdict_quiet_when_no_trades():
    df = pd.DataFrame({"strategy": [], "win": [], "pnl_pct": []})
    v = fp.per_strategy_verdict_against_criteria(df, "x")
    assert v["verdict"] == "QUIET"


def test_criteria_verdict_insufficient_for_small_n():
    df = pd.DataFrame({
        "strategy": ["x"] * 10,
        "win":      [True] * 10,
        "pnl_pct":  [1.0] * 10,
    })
    v = fp.per_strategy_verdict_against_criteria(df, "x")
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["criteria_band"] == "per_regime"
    assert v["n"] == 10


def test_criteria_band_overall_when_n_at_or_above_100():
    df = pd.DataFrame({
        "strategy": ["x"] * 100,
        "win":      [True] * 60 + [False] * 40,
        "pnl_pct":  [2.0] * 60 + [-1.0] * 40,
    })
    v = fp.per_strategy_verdict_against_criteria(df, "x")
    assert v["criteria_band"] == "overall"


def test_criteria_band_per_regime_when_n_below_100():
    df = pd.DataFrame({
        "strategy": ["x"] * 50,
        "win":      [True] * 30 + [False] * 20,
        "pnl_pct":  [2.0] * 30 + [-1.0] * 20,
    })
    v = fp.per_strategy_verdict_against_criteria(df, "x")
    assert v["criteria_band"] == "per_regime"


def test_criteria_profit_factor_inf_when_no_losses():
    df = pd.DataFrame({
        "strategy": ["x"] * 30,
        "win":      [True] * 30,
        "pnl_pct":  [1.0] * 30,
    })
    v = fp.per_strategy_verdict_against_criteria(df, "x")
    # Wins-only -> PF = inf
    assert v["pf"] == "inf"


# ---------------------------------------------------------------------
# T1 - Unit: regime_breakdown
# ---------------------------------------------------------------------
def test_regime_breakdown_returns_per_regime_aggregates():
    df = pd.DataFrame({
        "strategy": ["a", "a", "b", "b"],
        "regime":   ["bull", "bear", "bull", "bear"],
        "win":      [True, False, True, False],
        "pnl_pct":  [1.0, -2.0, 0.5, -1.0],
    })
    r = fp.regime_breakdown(df)
    assert "regimes" in r
    assert "bull" in r["regimes"]
    assert "bear" in r["regimes"]
    assert r["regimes"]["bull"]["n_trades"] == 2
    assert r["regimes"]["bear"]["n_trades"] == 2


def test_regime_breakdown_worst_drivers_sorted_ascending_by_sum():
    df = pd.DataFrame({
        "strategy": ["a"] * 3 + ["b"] * 3,
        "regime":   ["bear"] * 6,
        "win":      [False, False, False, True, True, False],
        "pnl_pct":  [-5.0, -3.0, -2.0, 1.0, 1.0, -0.5],
    })
    r = fp.regime_breakdown(df)
    drivers = r["worst_regime_drivers"]["bear"]
    # Strategy 'a' has sum_pp = -10; 'b' has sum_pp = 1.5; 'a' should be first
    assert drivers[0]["strategy"] == "a"
    assert drivers[0]["sum_pp"] == -10.0


# ---------------------------------------------------------------------
# T2 - Smoke: end-to-end script run
# ---------------------------------------------------------------------
def test_smoke_script_runs_end_to_end(tmp_path):
    tl = REPO / "output_phase_1a_beta_merged_local" / "trade_log.csv"
    if not tl.exists():
        pytest.skip("Phase 1A-beta trade_log not present")
    out = tmp_path / "audit_out"
    result = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--trade-log", str(tl),
         "--output-dir", str(out)],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"script failed: {result.stderr!r}"
    json_path = out / "phase1a_beta_recat.json"
    md_path = out / "phase1a_beta_recat.md"
    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text())
    # Expected top-level keys
    for k in ("buckets", "un_deprecated_23", "passing_criteria_verdicts",
              "regime_breakdown"):
        assert k in payload, f"missing key: {k}"
    # Should have all 3 buckets
    assert set(payload["buckets"].keys()) == {
        "Cat-A_Tight", "Cat-B_Data-Missing", "Cat-C_Investigate"
    }
    # Un-deprecated 23 must report 23 strategies
    assert payload["un_deprecated_23"]["n_in_bucket"] == 23
