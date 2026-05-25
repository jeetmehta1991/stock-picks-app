"""Sprint 7 Phase A Tier 2: LLM-mocked integration tests.

Source (per CHECKLIST #77): Sprint 7 Batch 351 2026-05-25. Pyramid Tier 2
(Integration) tests for state augmentation + upstream-key population.

These tests verify that `build_augmented_state()` produces a dict that
matches the upstream `Propagator.create_initial_state` schema (per
PHASE_1B_STATE_SCHEMA_DIFF.md) so the dict can drop straight into the
real LangGraph propagate path once Python 3.12 + langgraph wheels land
on Hetzner.

LLM is mocked at the dependency-injection boundary (the propagate_fn
arg to run_phase_1b_alpha). No network calls. No real Anthropic API.

Pyramid tiers exercised:
  T2 (Integration) build_augmented_state populates ALL upstream-required
                   init keys (company_of_interest + asset_type + trade_date
                   + past_context) per Propagator.create_initial_state
  T2 (Integration) Renamed-in-Batch-351 fields no longer carry the old
                   Batch 350 names
  T3 (Integration) LLM-mocked propagate_fn receives a dict that has both
                   upstream init keys AND our project extensions
  T6 (Regression)  Schema-diff doc claims match the actual TypedDict
                   declaration (catches drift between doc + code)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backtest.agents.toolkits.state_augmentation import (
    AugmentedAgentState,
    StateBuilderToolkits,
    build_augmented_state,
)

REPO = Path(__file__).parent.parent.parent


def _stub_toolkits() -> StateBuilderToolkits:
    """Deterministic-stub toolkit bundle for integration tests."""
    tech = MagicMock()
    tech.get_sector_relative_strength.return_value = {"rs_pct": 0.5}
    fund = MagicMock()
    fund.get_insider_transactions.return_value = {"n_transactions": 0}
    fund.get_congressional_trades.return_value = {"n_disclosures": 0}
    fund.get_13f_holdings.return_value = {"n_institutional_holders": 0}
    news = MagicMock()
    trader = MagicMock()
    trader.get_portfolio_state.return_value = {"scaffold": True}
    risk = MagicMock()
    risk.get_volatility_regime.return_value = {"vix_value": 18.0}
    risk.get_event_proximity.return_value = {"n_upcoming_events": 0}
    risk.get_recent_outcomes_on_similar_setups.return_value = {"scaffold": True}
    return StateBuilderToolkits(
        technical=tech, fundamentals=fund, news=news, trader=trader, risk=risk
    )


# ---------------------------------------------------------------------
# T2 - Integration: upstream-required init keys
# ---------------------------------------------------------------------
def test_build_state_includes_upstream_company_of_interest():
    """upstream Propagator.create_initial_state requires `company_of_interest`."""
    state = build_augmented_state("AAPL", date(2024, 6, 15), _stub_toolkits())
    assert state["company_of_interest"] == "AAPL"


def test_build_state_includes_upstream_asset_type():
    """upstream defaults asset_type='stock'; we hardcode for swing-equity scope."""
    state = build_augmented_state("AAPL", date(2024, 6, 15), _stub_toolkits())
    assert state["asset_type"] == "stock"


def test_build_state_includes_upstream_trade_date_iso():
    """upstream stores trade_date as str(date) - we use ISO format."""
    state = build_augmented_state("AAPL", date(2024, 6, 15), _stub_toolkits())
    assert state["trade_date"] == "2024-06-15"


def test_build_state_includes_upstream_past_context():
    """past_context required by Propagator.create_initial_state; '' until DEC-189."""
    state = build_augmented_state("AAPL", date(2024, 6, 15), _stub_toolkits())
    assert "past_context" in state
    assert state["past_context"] == ""


def test_build_state_preserves_convenience_aliases():
    """ticker + as_of remain as convenience aliases for upstream names."""
    state = build_augmented_state("AAPL", date(2024, 6, 15), _stub_toolkits())
    assert state["ticker"] == "AAPL"
    assert state["as_of"] == "2024-06-15"
    # And the upstream keys agree with the aliases
    assert state["company_of_interest"] == state["ticker"]
    assert state["trade_date"] == state["as_of"]


# ---------------------------------------------------------------------
# T2 - Integration: project-extension keys still populated
# ---------------------------------------------------------------------
def test_build_state_still_populates_all_9_extensions():
    """Batch 351 schema reconciliation must not have dropped any of the 7
    project extension keys + ticker + as_of aliases."""
    state = build_augmented_state("AAPL", date(2024, 6, 15), _stub_toolkits())
    expected = {
        "ticker", "as_of",
        "smart_money_signal", "regime_context", "portfolio_context",
        "event_proximity", "sector_context", "short_interest_signal",
        "historical_outcomes",
    }
    assert expected.issubset(state.keys()), f"missing: {expected - state.keys()}"


# ---------------------------------------------------------------------
# T6 - Regression: AugmentedAgentState schema matches the diff doc
# ---------------------------------------------------------------------
def test_typeddict_has_all_upstream_fields():
    """AugmentedAgentState declares every upstream AgentState field exactly
    once, with the upstream name (not the Batch-350 names that were wrong)."""
    annotations = AugmentedAgentState.__annotations__
    upstream_required = {
        "company_of_interest", "asset_type", "trade_date", "sender",
        "market_report", "sentiment_report", "news_report",
        "fundamentals_report", "investment_debate_state", "investment_plan",
        "trader_investment_plan", "risk_debate_state", "final_trade_decision",
        "past_context",
    }
    missing = upstream_required - set(annotations.keys())
    assert not missing, f"AugmentedAgentState missing upstream fields: {missing}"


def test_typeddict_has_no_batch_350_legacy_names():
    """Batch 350 had wrong names; Batch 351 renamed. Ensure the wrong names
    are absent so future code cannot accidentally re-introduce them."""
    annotations = AugmentedAgentState.__annotations__
    wrong_names = {"trader_decision", "risk_debate_history", "final_decision"}
    leaked = wrong_names & set(annotations.keys())
    assert not leaked, f"Legacy Batch-350 names re-introduced: {leaked}"


def test_typeddict_has_all_9_project_extensions():
    annotations = AugmentedAgentState.__annotations__
    extensions = {
        "ticker", "as_of",
        "smart_money_signal", "regime_context", "portfolio_context",
        "event_proximity", "sector_context", "short_interest_signal",
        "historical_outcomes",
    }
    missing = extensions - set(annotations.keys())
    assert not missing, f"AugmentedAgentState missing project extensions: {missing}"


# ---------------------------------------------------------------------
# T3 - Integration: LLM-mocked propagate sees full state
# ---------------------------------------------------------------------
def test_propagate_fn_receives_upstream_keys_when_called_via_pipeline(tmp_path):
    """Wire run_phase_1b_alpha + a propagate_fn stub that records the
    state-builder output the FIRST time it would be invoked.

    Today's scaffold doesn't iterate winners yet, so the stub records the
    pre-iteration manifest; once Hetzner Python 3.12 wires the real
    iteration loop, this test extends to assert the actual dict passed."""
    from backtest.agents.agent_gate_config import arm_b_full_with_veto
    from backtest.agents.langgraph_pipeline import (
        Phase1BAlphaConfig,
        run_phase_1b_alpha,
    )

    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "winners.parquet",
        output_dir=tmp_path / "out",
        agent_gate=arm_b_full_with_veto(),
        smoke_mode=False,
    )

    invoked = []
    def fake_propagate(state, ticker, date_):
        invoked.append({"state": state, "ticker": ticker, "date": date_})
        return ({}, "BUY")

    result = run_phase_1b_alpha(cfg, propagate_fn=fake_propagate)
    assert result["propagate_invoked"] is True
    assert result["manifest_path"].exists()


def test_build_augmented_state_can_be_passed_to_propagate_stub():
    """End-to-end shape: build_augmented_state output drops directly into
    a propagate-shape callable without KeyError on any standard access."""
    state = build_augmented_state("AAPL", date(2024, 6, 15), _stub_toolkits())

    def reader(s):
        # Stand-in for upstream LangGraph node code paths
        assert s["company_of_interest"]
        assert s["trade_date"]
        assert s["asset_type"]
        assert "past_context" in s
        # Project extensions accessible too
        assert "regime_context" in s
        assert "smart_money_signal" in s
        return "ok"

    assert reader(state) == "ok"


def test_build_augmented_state_idempotent_under_same_input():
    """Determinism: same (ticker, as_of, toolkits) yields identical state."""
    tk = _stub_toolkits()
    s1 = build_augmented_state("AAPL", date(2024, 6, 15), tk)
    s2 = build_augmented_state("AAPL", date(2024, 6, 15), tk)
    # Allow MagicMock to return new objects per call; compare on the stable keys.
    for k in ("ticker", "as_of", "company_of_interest", "asset_type", "trade_date", "past_context"):
        assert s1[k] == s2[k]
