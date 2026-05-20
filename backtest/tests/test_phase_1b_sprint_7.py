"""Tests for Phase 1B Sprint 7 modules (Batch 245)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.agents.agent_gate_config import (
    AgentGateConfig,
    AgentMode,
    arm_a_rules_only,
    arm_b_full_with_veto,
    arm_c_no_risk,
)
from backtest.results.ab_orchestrator import (
    compute_combo_ab,
    evaluate_dec_131_gate,
    orchestrate_ab_run,
)


def test_rules_only_has_zero_agents():
    cfg = arm_a_rules_only()
    assert len(cfg.active_agents()) == 0
    assert cfg.mode == AgentMode.RULES_ONLY


def test_full_with_veto_has_11_agents():
    cfg = arm_b_full_with_veto()
    assert len(cfg.active_agents()) == 12  # 11 + reflection
    assert "aggressive_debater" in cfg.active_agents()


def test_no_risk_excludes_risk_debaters():
    cfg = arm_c_no_risk()
    agents = cfg.active_agents()
    assert "aggressive_debater" not in agents
    assert "conservative_debater" not in agents
    assert "neutral_debater" not in agents
    assert "trader" in agents
    assert "portfolio_manager" in agents


def test_estimated_cost_zero_for_rules_only():
    cfg = arm_a_rules_only()
    assert cfg.estimated_cost_per_candidate() == 0.0


def test_estimated_cost_higher_for_full_than_no_risk():
    full = arm_b_full_with_veto()
    no_risk = arm_c_no_risk()
    assert full.estimated_cost_per_candidate() > no_risk.estimated_cost_per_candidate()


def test_as_dict_serializes_all_fields():
    cfg = arm_b_full_with_veto(cost_ceiling_usd=100.0)
    d = cfg.as_dict()
    assert d["mode"] == "full_with_veto"
    assert d["cost_ceiling_usd"] == 100.0
    assert "active_agents" in d
    assert "estimated_cost_per_candidate" in d


def test_consensus_required_mode_excludes_reflection():
    cfg = AgentGateConfig(mode=AgentMode.CONSENSUS_REQUIRED)
    agents = cfg.active_agents()
    assert "reflection" not in agents
    assert "portfolio_manager" in agents


def test_dec_131_absolute_pass():
    assert evaluate_dec_131_gate(0.20, 1.0)
    assert evaluate_dec_131_gate(0.21, 1.0)


def test_dec_131_absolute_fail():
    assert not evaluate_dec_131_gate(0.10, 1.0)


def test_dec_131_relative_pass_at_low_rules_sharpe():
    assert evaluate_dec_131_gate(0.05, 0.3)


def test_dec_131_negative_delta_fails():
    assert not evaluate_dec_131_gate(-0.1, 1.0)


def test_compute_combo_ab_returns_three_arms():
    rng = np.random.RandomState(7)
    trades_a = pd.DataFrame({"pnl_pct": rng.normal(0.5, 1.0, 30)})
    trades_b = pd.DataFrame({"pnl_pct": rng.normal(0.8, 1.0, 30)})
    trades_c = pd.DataFrame({"pnl_pct": rng.normal(0.6, 1.0, 30)})
    result = compute_combo_ab(
        {"rules_only": trades_a, "full_with_veto": trades_b, "no_risk": trades_c},
        combo_id="rsi__atr__bull",
    )
    assert len(result.arms) == 3
    assert result.combo_id == "rsi__atr__bull"
    assert result.verdict in ("INSUFFICIENT_DATA", "AGENT_ADDS", "AGENT_HURTS", "NEUTRAL")


def test_compute_combo_ab_insufficient_when_n_below_threshold():
    trades = pd.DataFrame({"pnl_pct": [1.0] * 10})
    result = compute_combo_ab(
        {"rules_only": trades, "full_with_veto": trades, "no_risk": trades},
        combo_id="rsi__atr__bull",
    )
    assert result.verdict == "INSUFFICIENT_DATA"


def test_compute_combo_ab_manifest_hash_deterministic():
    rng = np.random.RandomState(7)
    trades = pd.DataFrame({"pnl_pct": rng.normal(0.5, 1.0, 30)})
    r1 = compute_combo_ab(
        {"rules_only": trades, "full_with_veto": trades, "no_risk": trades},
        combo_id="X__Y__Z",
    )
    r2 = compute_combo_ab(
        {"rules_only": trades, "full_with_veto": trades, "no_risk": trades},
        combo_id="X__Y__Z",
    )
    assert r1.manifest_hash == r2.manifest_hash


def test_orchestrate_ab_run_empty_winners():
    out = orchestrate_ab_run(pd.DataFrame(), {})
    assert out.empty


def test_orchestrate_ab_run_with_winners_returns_per_combo_rows(tmp_path):
    winners = pd.DataFrame({
        "combo_id": ["rsi__atr__bull", "mfi__trail__neutral"],
        "n_trades": [50, 40],
        "sharpe":   [1.2, 0.9],
        "priority": ["P1", "P1"],
    })
    rng = np.random.RandomState(7)
    trade_logs = {
        "rules_only": pd.DataFrame({
            "combo_id": ["rsi__atr__bull"] * 30 + ["mfi__trail__neutral"] * 30,
            "pnl_pct":  list(rng.normal(0.5, 0.8, 60)),
        }),
        "full_with_veto": pd.DataFrame({
            "combo_id": ["rsi__atr__bull"] * 30 + ["mfi__trail__neutral"] * 30,
            "pnl_pct":  list(rng.normal(0.7, 0.8, 60)),
        }),
        "no_risk": pd.DataFrame({
            "combo_id": ["rsi__atr__bull"] * 30 + ["mfi__trail__neutral"] * 30,
            "pnl_pct":  list(rng.normal(0.6, 0.8, 60)),
        }),
    }
    out = orchestrate_ab_run(winners, trade_logs, output_path=tmp_path / "ab.parquet")
    assert len(out) == 2
    assert (tmp_path / "ab.parquet").exists()
    assert "verdict" in out.columns
    assert "net_sharpe_full_minus_rules" in out.columns
