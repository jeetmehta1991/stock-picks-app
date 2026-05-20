"""Tests for scripts/extract_phase_1a_beta_winners.py (Batch 244)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "extract_phase_1a_beta_winners.py"


def _make_trade_log(tmp_path, n_per_strat=50, seed=7):
    rng = np.random.RandomState(seed)
    rows = []
    for strat, exit_m, regime, mu in [
        ("strat_winner", "atr_trail_1x", "bull", 2.0),
        ("strat_loser",  "fixed_stop",   "bear", -1.0),
        ("strat_mid",    "trailing",     "neutral", 0.5),
    ]:
        pnls = rng.normal(loc=mu, scale=0.8, size=n_per_strat)
        for p in pnls:
            rows.append({
                "strategy":    strat,
                "exit_method": exit_m,
                "regime":      regime,
                "pnl_pct":     float(p),
                "ticker":      "AAPL",
            })
    df = pd.DataFrame(rows)
    df.to_parquet(tmp_path / "trade_log.parquet", index=False)
    return df


def test_extract_script_smoke(tmp_path):
    _make_trade_log(tmp_path, n_per_strat=50)
    out_path = tmp_path / "winners.parquet"
    r = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--source", str(tmp_path),
         "--out", str(out_path)],
        capture_output=True, text=True, timeout=60,
    )
    # Exit code 0 or 2 (empty winners) both acceptable; we just want no crash
    assert r.returncode in (0, 2), f"unexpected exit {r.returncode}; stderr: {r.stderr}"
    assert out_path.exists()


def test_extract_script_missing_source(tmp_path):
    missing = tmp_path / "no_such"
    r = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--source", str(missing)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 1
    assert "source dir not found" in r.stderr.lower() or "no trade_log" in r.stderr.lower()


def test_extract_script_csv_fallback(tmp_path):
    rng = np.random.RandomState(7)
    rows = []
    for _ in range(40):
        rows.append({
            "strategy": "rsi", "exit_method": "atr", "regime": "bull",
            "pnl_pct": float(rng.normal(1.0, 0.5)), "ticker": "AAPL",
        })
    pd.DataFrame(rows).to_csv(tmp_path / "trade_log.csv", index=False)
    out_path = tmp_path / "winners.parquet"
    r = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--source", str(tmp_path),
         "--out", str(out_path)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode in (0, 2)
    assert out_path.exists()


def test_extract_script_include_p2_flag(tmp_path):
    _make_trade_log(tmp_path, n_per_strat=50)
    out_path = tmp_path / "winners.parquet"
    r = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--source", str(tmp_path),
         "--include-p2",
         "--out", str(out_path)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode in (0, 2)
