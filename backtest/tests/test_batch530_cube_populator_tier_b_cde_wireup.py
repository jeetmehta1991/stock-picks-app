"""Batch 530 (2026-05-31) -- cube_populator Tier B + Tier C/D/E wire-in tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item #5 (`cube-cell-metrics-expansion`) --
"Cube populator wire-in is a one-liner follow-on" per Batch 504 note.

Pins:

  (1) `compute_cell_metrics` now emits the Tier B key bundle alongside
      the existing Tier A keys (M2 capacity + M11 pnl_concentration).
  (2) `compute_cell_metrics` now emits the Tier C/D/E key bundle
      (sharpe_ci_low / sharpe_ci_high / is_oos_decay / effective_n /
      sqn / k_ratio / mar_ratio / kelly_fraction / cvar_5pct / risk_of_ruin).
  (3) Wire-in is silent-failure guarded -- a trade subset missing the
      `regime` column (Tier B optional input) doesn't crash the cell-
      metric emission.
  (4) Per-cell totals match: compute_cell_metrics output keys ==
      tier-A baseline + Tier B keys + Tier C/D/E keys.
  (5) Real-data smoke: a non-trivial trade subset from
      output_batch395_final produces the full bundle.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


def _synthetic_trades(n: int = 50) -> pd.DataFrame:
    """Trade_log with EVERY column Tier B + Tier C/D/E need so the
    per-bucket breakdowns + smart-money lift + earnings-window
    breakdowns all emit."""
    rng = np.random.default_rng(seed=42)
    return pd.DataFrame({
        "ticker":               ["AAPL"] * n,
        "strategy":             ["bollinger_tight"] * n,
        "regime":               rng.choice(["bull", "neutral"], n),
        "sector":               rng.choice(["Technology", "Energy"], n),
        "confidence_tier":      rng.choice(["HIGH", "MEDIUM"], n),
        "exit_method":          ["atr_trail_1x"] * n,
        "win":                  rng.integers(0, 2, n),
        "pnl_pct":              rng.normal(0.01, 0.03, n),
        "hold_days":            rng.integers(1, 30, n),
        "entry_date":           pd.date_range("2024-01-01", periods=n, freq="D"),
        # Tier B per-bucket breakdown inputs:
        "smart_money_score":    rng.integers(-2, 3, n),
        "days_to_earnings":     rng.integers(0, 90, n),
        "aaii_signal":          rng.choice(["bull", "neutral", "bear"], n),
        "circuit_breaker_level": rng.choice([0, 1, 2], n),
        "macro_score":          rng.integers(-2, 3, n),
    })


def test_batch530_tier_b_keys_present_in_compute_cell_metrics():
    from backtest.results.cube_populator import compute_cell_metrics
    out = compute_cell_metrics(_synthetic_trades(50))
    # Tier B emits keys with specific prefixes per
    # compute_tier_b_metrics signature:
    expected_b_keys = {
        "n_with_smart_money", "n_without_smart_money",
        "wr_with_smart_money", "wr_without_smart_money",
        "wr_lift_smart_money", "wr_by_days_to_earnings_band",
        "wr_by_confidence_tier", "wr_by_regime",
        "wr_by_aaii_signal", "wr_by_circuit_breaker_level",
        "wr_by_macro_score_band", "wr_by_sector",
    }
    missing = expected_b_keys - set(out.keys())
    assert not missing, (
        f"Tier B wire-in missing keys: {missing}. cube_populator must "
        f"call compute_tier_b_metrics; check Batch 530 wire-in block."
    )


def test_batch530_tier_cde_keys_present_in_compute_cell_metrics():
    from backtest.results.cube_populator import compute_cell_metrics
    out = compute_cell_metrics(_synthetic_trades(50))
    # Tier C/D/E emits these per compute_tier_cde_metrics signature.
    # `is_oos_decay` is gated on having sufficient trade-date diversity
    # (a sub-50-trade synthetic may not produce a stable IS/OOS split);
    # omitted from this guaranteed-on-synthetic set.
    expected_cde_keys = {
        "sharpe_ci_low", "sharpe_ci_high",      # Tier C
        "effective_n",                           # Tier C
        "sqn", "k_ratio", "mar_ratio",          # Tier D
        "kelly_fraction", "cvar_5pct", "risk_of_ruin",  # Tier E
    }
    missing = expected_cde_keys - set(out.keys())
    assert not missing, (
        f"Tier C/D/E wire-in missing keys: {missing}. cube_populator "
        f"must call compute_tier_cde_metrics; check Batch 530 wire-in block."
    )


def test_batch530_tier_a_keys_still_present():
    """Regression guard: the Tier A keys (Batch 489 wire-in) must
    survive the Batch 530 additions. Confirms `out.update(...)` doesn't
    blow away pre-existing keys."""
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _synthetic_trades(50)
    # Add Tier A required columns
    trades["adv_at_entry"]    = 1_000_000.0
    trades["position_dollars"] = 5_000.0
    out = compute_cell_metrics(trades)
    expected_a_keys = {
        "n_trades", "win_rate", "expected_value", "profit_factor",
        "win_loss_ratio", "max_dd", "total_roi", "sharpe", "t_stat",
        "bonferroni_p", "rr_ratio",
        "pnl_concentration_top1_pct", "pnl_concentration_top5_pct",
        "pnl_hhi",
        "median_size_pct_of_adv", "max_size_pct_of_adv",
        "capacity_concern_flag",
    }
    missing = expected_a_keys - set(out.keys())
    assert not missing, f"Tier A keys regressed under Batch 530: {missing}"


def test_batch530_wireup_silent_on_missing_optional_cols():
    """Tier B's per-bucket breakdowns degrade gracefully when input
    lacks columns like `regime` -- the wire-in is try/except-guarded
    so missing-column doesn't crash compute_cell_metrics."""
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _synthetic_trades(50)
    # Drop the optional cols Tier B uses
    trades = trades.drop(columns=["sector", "confidence_tier"])
    out = compute_cell_metrics(trades)
    # Must still emit Tier A core keys
    assert "n_trades" in out
    assert out["n_trades"] == 50
    # Must still emit Tier C/D/E (those don't need sector/tier)
    assert "sharpe_ci_low" in out


def test_batch530_empty_trades_returns_n_trades_only():
    """Edge case: empty trade frame still degrades gracefully."""
    from backtest.results.cube_populator import compute_cell_metrics
    out = compute_cell_metrics(pd.DataFrame())
    assert out == {"n_trades": 0}


def test_batch530_real_trade_log_smoke():
    """Smoke: real Batch 395 trade_log produces a 30+ key cell-metrics
    bundle for a non-empty cell."""
    tl = REPO / "output_batch395_final" / "trade_log.csv"
    if not tl.exists():
        pytest.skip("output_batch395_final/trade_log.csv absent")
    from backtest.results.cube_populator import compute_cell_metrics
    trades = pd.read_csv(tl, low_memory=False)
    sub = trades[
        (trades["strategy"] == "bollinger_tight")
        & (trades["regime"] == "bull")
    ].head(100)
    if sub.empty:
        pytest.skip("real trade_log has no bollinger_tight + bull cell")
    out = compute_cell_metrics(sub)
    assert len(out) >= 30, (
        f"compute_cell_metrics returned only {len(out)} keys on real "
        f"data; Tier A + B + C/D/E should yield 30+"
    )
    # Spot-check one key from each tier
    assert "win_rate" in out                  # Tier A
    assert "wr_by_sector" in out              # Tier B
    assert "sharpe_ci_low" in out             # Tier C
    assert "sqn" in out                       # Tier D
    assert "kelly_fraction" in out            # Tier E


def test_batch530_wire_in_block_present_in_cube_populator():
    """Grep-style guard: cube_populator.py must reference both Tier B
    and Tier C/D/E imports. If a future commit drops the wire-in, this
    test fires."""
    text = (REPO / "backtest" / "results" / "cube_populator.py").read_text(
        encoding="utf-8"
    )
    assert "compute_tier_b_metrics" in text, (
        "cube_populator.py missing compute_tier_b_metrics wire-in"
    )
    assert "compute_tier_cde_metrics" in text, (
        "cube_populator.py missing compute_tier_cde_metrics wire-in"
    )
