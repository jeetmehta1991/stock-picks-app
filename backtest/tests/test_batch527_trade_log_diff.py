"""Batch 527 (2026-05-31) -- trade_log diff tool tests.

Source: per CHECKLIST #77.
Queue rows: DET1 cross-platform verification + #9 R3-vs-R4 cube
comparison.

Pins:

  (1) Identical trade_logs -> zero diffs across all three subsystems
      (set summary, per-column, roster).
  (2) Set summary correctly identifies A-only / B-only / both.
  (3) Exact-column diff fires on single-cell mismatch.
  (4) Float-tolerance respects rtol + atol (sub-tolerance diff
      counts as in-tol; out-of-tol counted accurately).
  (5) Roster diff identifies gained / lost / changed (strategy, regime)
      cells with correct delta sign.
  (6) Composite-key fallback works when trade_id is missing
      (uses ticker + entry_date + strategy).
  (7) Diff is symmetric -- A vs B common count == B vs A common count.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


def _sample_trade_log(n: int = 10, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "trade_id":        [f"T{i:04d}" for i in range(n)],
        "ticker":          rng.choice(["AAPL", "MSFT", "AMZN"], n),
        "entry_date":      pd.date_range("2024-01-01", periods=n, freq="D"),
        "exit_date":       pd.date_range("2024-01-05", periods=n, freq="D"),
        "direction":       ["long"] * n,
        "strategy":        rng.choice(["bollinger_tight", "pead_long"], n),
        "regime":          rng.choice(["bull", "neutral"], n),
        "sector":          ["Technology"] * n,
        "category":        ["momentum"] * n,
        "confidence_tier": ["HIGH"] * n,
        "exit_reason":     ["trailing_stop"] * n,
        "win":             rng.integers(0, 2, n),
        "entry_price":     rng.uniform(100, 200, n),
        "exit_price":      rng.uniform(100, 200, n),
        "pnl_pct":         rng.normal(0.01, 0.03, n),
        "pnl_dollar":      rng.normal(100, 300, n),
        "hold_days":       rng.integers(1, 30, n),
    })
    return df


def test_batch527_identical_logs_show_no_diff():
    from scripts.diff_trade_logs import run_diff
    import tempfile
    df = _sample_trade_log(10)
    with tempfile.TemporaryDirectory() as td:
        a = Path(td) / "a.csv"
        b = Path(td) / "b.csv"
        df.to_csv(a, index=False)
        df.to_csv(b, index=False)
        result = run_diff(a, b)
    assert result["set_summary"]["in_a_not_b"] == 0
    assert result["set_summary"]["in_b_not_a"] == 0
    assert result["set_summary"]["in_both"] == 10
    for col, st in result["col_diffs"]["exact"].items():
        assert st["n_diff"] == 0, f"exact col {col} false-fires"
    for col, st in result["col_diffs"]["tol"].items():
        assert st.get("n_out_of_tol", 0) == 0, (
            f"tol col {col} false-fires"
        )
    assert result["roster_diff"]["cells_gained"] == []
    assert result["roster_diff"]["cells_lost"] == []
    assert result["roster_diff"]["cells_changed"] == []


def test_batch527_set_summary_identifies_a_only_and_b_only():
    from scripts.diff_trade_logs import set_level_summary
    a = _sample_trade_log(10)
    b = _sample_trade_log(10).copy()
    # Mutate B so trade_ids 0-4 stay shared, 5-9 become NEW keys
    b.loc[5:9, "trade_id"] = [f"X{i:04d}" for i in range(5)]
    summary = set_level_summary(a, b)
    assert summary["in_both"] == 5
    assert summary["in_a_not_b"] == 5
    assert summary["in_b_not_a"] == 5


def test_batch527_exact_diff_fires_on_single_cell_mismatch():
    from scripts.diff_trade_logs import per_column_diff_stats
    a = _sample_trade_log(10)
    b = a.copy()
    b.loc[3, "strategy"] = "different_strategy_xyz"
    out = per_column_diff_stats(a, b)
    assert out["exact"]["strategy"]["n_diff"] == 1
    sample = out["exact"]["strategy"]["samples"]
    assert any(s["a"] != s["b"] for s in sample)


def test_batch527_tol_diff_respects_rtol_and_atol():
    from scripts.diff_trade_logs import per_column_diff_stats
    a = _sample_trade_log(10)
    b = a.copy()
    # Add a sub-tolerance perturbation: 1e-10 < float_atol (default 1e-9)
    b["pnl_pct"] = b["pnl_pct"] + 1e-10
    out = per_column_diff_stats(a, b, float_rtol=1e-6, float_atol=1e-9)
    assert out["tol"]["pnl_pct"]["n_out_of_tol"] == 0, (
        "sub-atol perturbation should be in-tolerance"
    )
    # Now add a clearly-out-of-tol perturbation
    b["pnl_pct"] = a["pnl_pct"] + 0.5
    out2 = per_column_diff_stats(a, b, float_rtol=1e-6, float_atol=1e-9)
    assert out2["tol"]["pnl_pct"]["n_out_of_tol"] == 10
    assert out2["tol"]["pnl_pct"]["max_abs_diff"] == pytest.approx(0.5,
                                                                    rel=1e-3)


def test_batch527_roster_diff_identifies_gained_lost_changed():
    from scripts.diff_trade_logs import roster_diff
    a = _sample_trade_log(20, seed=1)
    b = _sample_trade_log(20, seed=2)
    # Force a known cell-count delta
    a.loc[a.index[:5], "strategy"]  = "alpha"
    a.loc[a.index[:5], "regime"]    = "bull"
    b.loc[b.index[:10], "strategy"] = "alpha"
    b.loc[b.index[:10], "regime"]   = "bull"
    out = roster_diff(a, b)
    alpha_bull = [c for c in (out["cells_gained"] + out["cells_lost"]
                                + out["cells_changed"])
                   if c["cell"][0] == "alpha" and c["cell"][1] == "bull"]
    assert len(alpha_bull) == 1
    cell = alpha_bull[0]
    assert cell["n_a"] == 5
    assert cell["n_b"] == 10
    assert cell["delta"] == 5


def test_batch527_composite_key_fallback_when_trade_id_missing():
    """When trade_id column is absent, the diff falls back to
    (ticker, entry_date, strategy) composite. Verifies the fallback
    aligns + scores correctly."""
    from scripts.diff_trade_logs import set_level_summary, per_column_diff_stats
    a = _sample_trade_log(10).drop(columns=["trade_id"])
    b = a.copy()
    s = set_level_summary(a, b)
    assert s["in_both"] == 10
    out = per_column_diff_stats(a, b)
    # All cells must align -> zero diffs
    for col, st in out["exact"].items():
        assert st["n_diff"] == 0


def test_batch527_diff_is_symmetric_on_common_count():
    """A vs B common count == B vs A common count."""
    from scripts.diff_trade_logs import set_level_summary
    a = _sample_trade_log(10, seed=1)
    b = _sample_trade_log(15, seed=2)
    s_ab = set_level_summary(a, b)
    s_ba = set_level_summary(b, a)
    assert s_ab["in_both"] == s_ba["in_both"]
    assert s_ab["in_a_not_b"] == s_ba["in_b_not_a"]
    assert s_ab["in_b_not_a"] == s_ba["in_a_not_b"]


def test_batch527_diff_handles_nan_correctly():
    """Both NaN in a tol column should NOT count as out-of-tolerance.
    Mixed NaN (one NaN, one number) should be tracked separately."""
    from scripts.diff_trade_logs import per_column_diff_stats
    a = _sample_trade_log(10)
    b = a.copy()
    # Set both NaN in row 0
    a.loc[0, "pnl_dollar"] = np.nan
    b.loc[0, "pnl_dollar"] = np.nan
    # Mixed NaN in row 5
    a.loc[5, "pnl_dollar"] = np.nan  # B keeps original number
    out = per_column_diff_stats(a, b)
    stats = out["tol"]["pnl_dollar"]
    assert stats["either_nan"] == 1, (
        f"expected 1 either_nan row (idx 5); got {stats['either_nan']}"
    )
    # Both-NaN row should NOT contribute to either_nan
    assert stats["n_valid"] == 8  # 10 - both_nan(1) - either_nan(1)


def test_batch527_script_is_operator_run_not_engine_wired():
    """SCAFFOLD invariant: diff_trade_logs is an operator-run tool;
    NOT imported anywhere in the engine call path."""
    repo = Path(__file__).resolve().parent.parent.parent
    targets = [
        repo / "backtest" / "engine" / "backtest.py",
        repo / "backtest" / "signals" / "screener.py",
        repo / "backtest" / "run_phase1a.py",
    ]
    for tgt in targets:
        if not tgt.exists():
            continue
        text = tgt.read_text(encoding="utf-8")
        assert "diff_trade_logs" not in text, (
            f"Batch 527 diff tool wired into {tgt.name}. Operator-only "
            f"tool -- if intentional wire-in, flip this test."
        )
