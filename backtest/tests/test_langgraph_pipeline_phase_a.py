"""Sprint 7 Phase A: langgraph_pipeline.py scaffold tests.

Source (per CHECKLIST #77 canonical-source attribution): Sprint 7 Batch 349
2026-05-25. Scaffold tests for the Phase 1B-alpha LangGraph pipeline wrapper.

Pyramid tiers exercised:
  T1 (Unit)        Phase1BAlphaConfig dataclass + as_dict()
  T1 (Unit)        build_pipeline() returns expected descriptor shape
  T1 (Unit)        active-agents -> selected_analysts label mapping
  T2 (Smoke)       run_phase_1b_alpha() writes manifest.json
  T3 (Integration) vendor scaffold present at vendored/tradingagents/

These tests do NOT require langgraph/langchain installed - they exercise the
pure-Python wiring layer. Real LangGraph propagate() invocation tests come
in subsequent Sprint 7 batches (require Python 3.10-3.13 and pip install -e
of the vendor).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from backtest.agents.agent_gate_config import (
    AgentGateConfig,
    AgentMode,
    arm_a_rules_only,
    arm_b_full_with_veto,
    arm_c_no_risk,
)
from backtest.agents.langgraph_pipeline import (
    Phase1BAlphaConfig,
    _VENDORED_ROOT,
    _ensure_vendor_on_path,
    build_pipeline,
    run_phase_1b_alpha,
)

REPO = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------
# T3 - Integration: vendor scaffold present
# ---------------------------------------------------------------------
def test_vendor_scaffold_present():
    """vendored/tradingagents/ must exist with LICENSE + tradingagents package."""
    assert _VENDORED_ROOT.exists(), f"vendored/tradingagents not found at {_VENDORED_ROOT}"
    assert (_VENDORED_ROOT / "LICENSE").exists()
    assert (_VENDORED_ROOT / "tradingagents").is_dir()
    assert (_VENDORED_ROOT / "tradingagents" / "__init__.py").exists()


def test_vendor_path_insertion_idempotent():
    import sys
    n_before = sum(1 for p in sys.path if "tradingagents" in p)
    _ensure_vendor_on_path()
    _ensure_vendor_on_path()
    n_after = sum(1 for p in sys.path if "tradingagents" in p)
    assert n_after >= 1
    assert n_after <= n_before + 1


# ---------------------------------------------------------------------
# T1 - Unit: Phase1BAlphaConfig
# ---------------------------------------------------------------------
def test_phase1b_config_defaults(tmp_path):
    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "winners.parquet",
        output_dir=tmp_path / "out",
    )
    assert cfg.agent_gate.mode == AgentMode.RULES_ONLY
    assert cfg.llm_model == "claude-haiku-4-5-20251001"
    assert cfg.llm_temperature == 0.0
    assert cfg.smoke_mode is False


def test_phase1b_config_as_dict_roundtrip(tmp_path):
    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "w.parquet",
        output_dir=tmp_path / "o",
        agent_gate=arm_a_rules_only(),
        smoke_mode=True,
    )
    d = cfg.as_dict()
    assert "agent_gate" in d
    assert d["smoke_mode"] is True
    assert d["llm_temperature"] == 0.0


def test_phase1b_config_accepts_all_three_arms(tmp_path):
    for arm_fn in (arm_a_rules_only, arm_b_full_with_veto, arm_c_no_risk):
        cfg = Phase1BAlphaConfig(
            winners_parquet=tmp_path / "w.parquet",
            output_dir=tmp_path / "o",
            agent_gate=arm_fn(),
        )
        assert isinstance(cfg.agent_gate, AgentGateConfig)


# ---------------------------------------------------------------------
# T1 - Unit: build_pipeline()
# ---------------------------------------------------------------------
def test_build_pipeline_descriptor_shape(tmp_path):
    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "w.parquet",
        output_dir=tmp_path / "o",
        agent_gate=arm_a_rules_only(),
    )
    desc = build_pipeline(cfg)
    for key in ("mode", "active_agents", "selected_analysts", "llm_model",
                "llm_temperature", "vendor_present"):
        assert key in desc, f"missing key: {key}"
    assert desc["vendor_present"] is True


def test_build_pipeline_full_with_veto_includes_all_analysts():
    """FULL_WITH_VETO mode activates all 11 agents incl. 3 analysts; selected_analysts
    maps the 3 analysts to upstream's 'market'/'fundamentals'/'news' labels."""
    cfg = Phase1BAlphaConfig(
        winners_parquet=Path("nonexistent.parquet"),
        output_dir=Path("/tmp/out_test"),
        agent_gate=arm_b_full_with_veto(),
    )
    desc = build_pipeline(cfg)
    assert set(desc["selected_analysts"]) == {"market", "fundamentals", "news"}
    # Researchers / Trader / Risk debaters are not in upstream's selected_analysts
    # vocab (they're nodes in the graph, not analyst types)
    assert "bull_researcher" in desc["active_agents"]
    assert "bull_researcher" not in desc["selected_analysts"]


def test_build_pipeline_rules_only_has_empty_active():
    cfg = Phase1BAlphaConfig(
        winners_parquet=Path("nonexistent.parquet"),
        output_dir=Path("/tmp/out_rules"),
        agent_gate=arm_a_rules_only(),
    )
    desc = build_pipeline(cfg)
    assert desc["active_agents"] == []
    assert desc["selected_analysts"] == []


# ---------------------------------------------------------------------
# T2 - Smoke: run_phase_1b_alpha()
# ---------------------------------------------------------------------
def test_run_phase_1b_alpha_writes_manifest(tmp_path):
    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "w.parquet",  # nonexistent on purpose
        output_dir=tmp_path / "out",
        smoke_mode=True,
    )
    result = run_phase_1b_alpha(cfg)
    assert result["manifest_path"].exists()
    manifest = json.loads(result["manifest_path"].read_text())
    assert "config" in manifest
    assert "pipeline" in manifest
    assert manifest["n_tickers_planned"] == 0
    assert manifest["propagate_invoked"] is False
    assert "api_key_present" in manifest


def test_run_phase_1b_alpha_counts_tickers_from_winners_parquet(tmp_path):
    import pandas as pd
    winners = tmp_path / "winners.parquet"
    pd.DataFrame({"ticker": ["AAPL", "MSFT", "AAPL", "GOOG"], "combo_id": ["x"]*4}).to_parquet(winners)
    cfg = Phase1BAlphaConfig(
        winners_parquet=winners,
        output_dir=tmp_path / "out",
        smoke_mode=True,
    )
    result = run_phase_1b_alpha(cfg)
    assert result["n_tickers_planned"] == 3  # unique AAPL, MSFT, GOOG


def test_run_phase_1b_alpha_respects_max_tickers(tmp_path):
    import pandas as pd
    winners = tmp_path / "winners.parquet"
    pd.DataFrame({"ticker": ["A", "B", "C", "D", "E"], "combo_id": ["x"]*5}).to_parquet(winners)
    cfg = Phase1BAlphaConfig(
        winners_parquet=winners,
        output_dir=tmp_path / "out",
        smoke_mode=True,
        max_tickers=2,
    )
    result = run_phase_1b_alpha(cfg)
    assert result["n_tickers_planned"] == 2


def test_run_phase_1b_alpha_propagate_fn_not_called_in_smoke(tmp_path):
    called = []
    def fake_propagate(state, ticker, date):
        called.append((ticker, date))
        return ({}, "BUY")
    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "w.parquet",
        output_dir=tmp_path / "out",
        smoke_mode=True,
    )
    run_phase_1b_alpha(cfg, propagate_fn=fake_propagate)
    assert called == []  # smoke mode short-circuits


def test_run_phase_1b_alpha_propagate_fn_invoked_when_not_smoke(tmp_path):
    """Non-smoke mode plus propagate_fn marks propagate_invoked True even
    though scaffold doesn't iterate winners yet - this pin prevents silent
    regression when iteration is implemented."""
    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "w.parquet",
        output_dir=tmp_path / "out",
        smoke_mode=False,
    )
    def stub_propagate(state, ticker, date):
        return ({}, "BUY")
    result = run_phase_1b_alpha(cfg, propagate_fn=stub_propagate)
    assert result["propagate_invoked"] is True
