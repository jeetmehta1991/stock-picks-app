"""Batch 532 (2026-06-01) -- Phased R4 runner + abort harness tests.

Source: per CHECKLIST #77 + memory `feedback_monitor_intermediate_counts.md`.
Queue: EXECUTION_QUEUE.md item #9 R4 cube run.

Pins:

  (1) Phase targets table covers pilot / wave_a / wave_b
  (2) Gate 1 (total_trades): below half-floor -> abort
  (3) Gate 2 (zero_fire_strategies): >20% registered = 0 trades -> abort
  (4) Gate 4 (p17_signal_emission): zero P17 fires in pilot = OK; zero
      in wave_a or wave_b = abort
  (5) Verdict logic: PROCEED only when all hard gates pass
  (6) Module imports clean
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


def _synthetic_phase_trades(n: int, n_strats: int = 50,
                              with_p17: bool = True) -> pd.DataFrame:
    """Build a synthetic phase trade_log."""
    import numpy as np
    rng = np.random.default_rng(seed=42)
    strats = [f"strat_{i}" for i in range(n_strats)]
    if with_p17:
        strats.extend(["activist_13d_long", "m_and_a_target_long"])
    return pd.DataFrame({
        "ticker":    rng.choice(["AAPL", "MSFT", "AMZN"], n),
        "strategy":  rng.choice(strats, n),
        "regime":    "bull",
        "pnl_pct":   rng.normal(0.01, 0.03, n),
        "hold_days": rng.integers(1, 30, n),
        "win":       rng.integers(0, 2, n),
    })


def _write_batch_dirs(tmp_path: Path, trades: pd.DataFrame,
                       n_batches: int = 2) -> list[Path]:
    """Split trades across N batch dirs."""
    dirs = []
    chunk_size = len(trades) // n_batches if n_batches else 0
    for i in range(n_batches):
        d = tmp_path / f"output_phase_1a_beta_batch{i+1}"
        d.mkdir()
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < n_batches - 1 else len(trades)
        sub = trades.iloc[start:end] if start < len(trades) else trades.iloc[0:0]
        sub.to_csv(d / "trade_log.csv", index=False)
        dirs.append(d)
    return dirs


def test_batch532_imports_clean():
    from scripts import phased_r4_run as m
    assert callable(m.run_phase)


def test_batch532_phase_targets_table_covers_three_phases():
    from scripts.phased_r4_run import PHASE_TARGETS
    assert set(PHASE_TARGETS.keys()) == {"pilot", "wave_a", "wave_b"}
    # Pilot has fewest batches, wave_b expects most cumulative trades
    assert PHASE_TARGETS["pilot"][0] == 2
    assert PHASE_TARGETS["wave_a"][0] == 10
    assert PHASE_TARGETS["wave_b"][0] == 13
    # Trade floors increase per phase
    assert PHASE_TARGETS["pilot"][1] < PHASE_TARGETS["wave_a"][1]
    assert PHASE_TARGETS["wave_a"][1] < PHASE_TARGETS["wave_b"][1]


def test_batch532_gate_1_below_half_floor_fails(tmp_path):
    """500-floor pilot: 200 trades < 250 half-floor -> gate 1 FAIL."""
    from scripts.phased_r4_run import gate_1_total_trades
    trades = _synthetic_phase_trades(n=200)
    g = gate_1_total_trades(trades, "pilot")
    assert g["pass"] is False
    assert g["floor"] == 500


def test_batch532_gate_1_above_half_floor_passes(tmp_path):
    """Pilot half-floor is 250; 600 trades > 250 -> pass."""
    from scripts.phased_r4_run import gate_1_total_trades
    trades = _synthetic_phase_trades(n=600)
    g = gate_1_total_trades(trades, "pilot")
    assert g["pass"] is True


def test_batch532_gate_2_zero_fire_strategies_below_threshold_pass():
    """If fired-strategy set covers >80% of registered, gate 2 passes."""
    from scripts.phased_r4_run import gate_2_zero_fire_strategies
    from backtest.signals.screener import ALL_STRATEGIES
    # Build trades that cover >80% of registered strategies
    strats = list(ALL_STRATEGIES.keys())[:int(0.85 * len(ALL_STRATEGIES))]
    trades = pd.DataFrame({"strategy": strats * 3})
    g = gate_2_zero_fire_strategies(trades, "pilot")
    assert g["pass"] is True
    assert g["pct_zero"] < 0.20


def test_batch532_gate_2_too_many_silent_strategies_fail():
    """If <80% of registered fire, gate 2 FAILS (producer-zero cluster)."""
    from scripts.phased_r4_run import gate_2_zero_fire_strategies
    from backtest.signals.screener import ALL_STRATEGIES
    # Only 30% of strategies have trades
    strats = list(ALL_STRATEGIES.keys())[:int(0.30 * len(ALL_STRATEGIES))]
    trades = pd.DataFrame({"strategy": strats * 3})
    g = gate_2_zero_fire_strategies(trades, "pilot")
    assert g["pass"] is False


def test_batch532_gate_4_p17_zero_in_pilot_is_soft_ok():
    """Pilot: 0 P17 fires is OK (small sample, rare event)."""
    from scripts.phased_r4_run import gate_4_p17_signal_emission
    trades = _synthetic_phase_trades(n=500, with_p17=False)
    g = gate_4_p17_signal_emission(trades)
    assert g["n_p17_trades"] == 0
    assert g["pass"] is True


def test_batch532_run_phase_proceed_on_healthy_pilot(tmp_path):
    """Healthy pilot returns PROCEED verdict."""
    from scripts.phased_r4_run import run_phase
    from backtest.signals.screener import ALL_STRATEGIES
    # Build trades that hit >80% strategy coverage + above floor
    strats = list(ALL_STRATEGIES.keys())[:int(0.85 * len(ALL_STRATEGIES))]
    trades = pd.DataFrame({
        "ticker":    ["AAPL"] * len(strats) * 5,
        "strategy":  strats * 5,
        "regime":    ["bull"] * len(strats) * 5,
        "pnl_pct":   [0.01] * len(strats) * 5,
        "hold_days": [5] * len(strats) * 5,
        "win":       [1] * len(strats) * 5,
    })
    dirs = _write_batch_dirs(tmp_path, trades, n_batches=2)
    result = run_phase("pilot", dirs)
    assert result["verdict"] == "PROCEED", (
        f"healthy pilot got {result['verdict']}: {result['reason']}; "
        f"gates: {result['gates']}"
    )


def test_batch532_run_phase_abort_on_catastrophic_trade_drop(tmp_path):
    """Pilot with only 50 trades (well below 250 half-floor) -> ABORT."""
    from scripts.phased_r4_run import run_phase
    trades = _synthetic_phase_trades(n=50)
    dirs = _write_batch_dirs(tmp_path, trades, n_batches=2)
    result = run_phase("pilot", dirs)
    assert result["verdict"] == "ABORT"
    assert "1_total_trades" in result["reason"]


def test_batch532_invalid_phase_choice_rejected():
    """Phase target table only defines pilot/wave_a/wave_b."""
    from scripts.phased_r4_run import PHASE_TARGETS
    assert "wave_c" not in PHASE_TARGETS
    assert "invalid" not in PHASE_TARGETS


def test_batch532_script_not_wired_into_engine():
    """The phased runner is operator-run (post-batch analysis); not
    consumed by engine call path."""
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
        assert "phased_r4_run" not in text, (
            f"phased_r4_run wired into {tgt.name} -- it's an "
            f"operator analysis tool; flip this test if intentional."
        )
