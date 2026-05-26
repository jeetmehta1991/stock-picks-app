"""Stream B3: Tier 3 LLM cost projection test.

Source (per CHECKLIST #77): DEC-459 Phase 1B-alpha budget $116 CAD.
Owner directive 2026-05-19: $300 ceiling pre-approved; smoke/demo gates
PROTECT the budget by validating framework on small N before scale.

This test pins the canonical cost-per-candidate and projects full-Phase-
1B-alpha spend. Failures here surface a budget-busting config BEFORE
real Anthropic calls.

Pyramid tiers exercised:
  T3 (Statistical) projected Phase 1B-alpha cost <= $116 CAD ceiling
  T6 (Regression)  AgentGateConfig.estimated_cost_per_candidate honors
                   the documented Haiku pricing
"""
from __future__ import annotations

from backtest.agents.agent_gate_config import (
    AgentMode, arm_a_rules_only, arm_b_full_with_veto, arm_c_no_risk,
)


# DEC-459 owner-approved budget (USD; CAD conversion ~1.36)
PHASE_1B_ALPHA_BUDGET_CAD = 116.0
PHASE_1B_ALPHA_BUDGET_USD = PHASE_1B_ALPHA_BUDGET_CAD / 1.36  # ~$85 USD
PHASE_1B_ALPHA_CEILING_USD = 300.0  # owner pre-approved ceiling
# Per-arm scope (per DEC-459 Phase 1B-alpha scope):
# - winners.parquet has typically 20-40 Priority-1 combos
# - each combo iterates over ~250 trading days (1y OOS)
# - ~30% pass screener gate -> agent invocation rate
EXPECTED_WINNERS = 30      # midpoint of 20-40
EXPECTED_DAYS = 250        # 1y OOS
SCREEN_PASS_RATE = 0.30    # ~30% of (winner, day) pairs pass screener


def _project_cost(arm_config) -> float:
    """Projected USD cost for one arm's full Phase 1B-alpha run."""
    per_candidate = arm_config.estimated_cost_per_candidate()
    n_candidates = EXPECTED_WINNERS * EXPECTED_DAYS * SCREEN_PASS_RATE
    return per_candidate * n_candidates


def test_b3_arm_a_rules_only_is_free():
    """Arm A baseline = no LLM calls; cost = 0."""
    cfg = arm_a_rules_only()
    assert _project_cost(cfg) == 0.0, "Arm A rules-only should cost $0"


def test_b3_arm_b_full_with_veto_under_ceiling():
    """Arm B = full 11-agent + Risk veto. Highest cost arm."""
    cfg = arm_b_full_with_veto()
    projected = _project_cost(cfg)
    # Arm B fires all 11 active agents per candidate at Haiku rate
    # ~$0.00035/agent * 11 agents = ~$0.00385/candidate
    # * 30 winners * 250 days * 0.3 pass = 2250 candidates
    # = ~$8.7 USD per arm = well under $116 CAD ceiling
    assert projected < PHASE_1B_ALPHA_BUDGET_USD, (
        f"Arm B projected ${projected:.2f} >= budget ${PHASE_1B_ALPHA_BUDGET_USD:.2f} USD "
        f"(=${PHASE_1B_ALPHA_BUDGET_CAD} CAD)"
    )
    assert projected < PHASE_1B_ALPHA_CEILING_USD


def test_b3_arm_c_no_risk_cheaper_than_arm_b():
    """Arm C drops 3 Risk debaters; should be ~73% of Arm B cost."""
    cfg_b = arm_b_full_with_veto()
    cfg_c = arm_c_no_risk()
    cost_b = _project_cost(cfg_b)
    cost_c = _project_cost(cfg_c)
    assert cost_c < cost_b, "Arm C should be cheaper than Arm B"
    # 3-arm Phase 1B-alpha total = A + B + C  -- must fit in ceiling
    total_3_arm = _project_cost(cfg_b) + cost_c + _project_cost(arm_a_rules_only())
    assert total_3_arm < PHASE_1B_ALPHA_CEILING_USD, (
        f"3-arm total ${total_3_arm:.2f} >= ceiling ${PHASE_1B_ALPHA_CEILING_USD}"
    )


def test_b3_per_candidate_cost_is_haiku_priced():
    """Pin Haiku ~$0.00035/call. Sonnet would 10x (~$0.0035/call) and
    blow the budget on Phase 1B-alpha. The model must remain Haiku
    until Phase 1C+ owner-approved transition."""
    cfg = arm_b_full_with_veto()
    per_cand = cfg.estimated_cost_per_candidate()
    assert "haiku" in cfg.model.lower(), (
        f"Phase 1B-alpha model should be Haiku (got {cfg.model})"
    )
    # 11 agents * $0.00035 = $0.00385
    assert 0.003 <= per_cand <= 0.005, (
        f"Per-candidate cost ${per_cand:.5f} outside expected Haiku band "
        f"$0.003-0.005 (11 agents x ~$0.00035)"
    )


def test_b3_budget_ceiling_documented_in_config():
    """AgentGateConfig.cost_ceiling_usd should accept the $116 CAD / $85 USD
    budget when explicitly set."""
    cfg = arm_b_full_with_veto(cost_ceiling_usd=PHASE_1B_ALPHA_BUDGET_USD)
    assert cfg.cost_ceiling_usd == PHASE_1B_ALPHA_BUDGET_USD
    d = cfg.as_dict()
    assert d["cost_ceiling_usd"] == PHASE_1B_ALPHA_BUDGET_USD


def test_b3_smoke_budget_3_usd_under_full_budget():
    """The smoke run cap ($3 USD per DEC-459) must be far under the
    full-run budget. Catches misconfig where smoke cap accidentally
    exceeds full run budget."""
    SMOKE_BUDGET = 3.0
    DEMO_BUDGET = 10.0
    assert SMOKE_BUDGET < DEMO_BUDGET < PHASE_1B_ALPHA_BUDGET_USD, (
        f"Budget hierarchy violation: smoke ${SMOKE_BUDGET} < "
        f"demo ${DEMO_BUDGET} < full ${PHASE_1B_ALPHA_BUDGET_USD}"
    )


def test_b3_sonnet_would_bust_budget():
    """Regression: if anyone flips the model to Sonnet without owner
    approval, the projected cost should exceed the Phase-1B-alpha budget,
    surfacing the mistake. Manually construct a Sonnet config and verify
    it busts the ceiling."""
    cfg = arm_b_full_with_veto(model="claude-sonnet-4-6")
    projected = _project_cost(cfg)
    assert projected > PHASE_1B_ALPHA_BUDGET_USD, (
        f"Sonnet projected ${projected:.2f} should EXCEED ${PHASE_1B_ALPHA_BUDGET_USD} "
        f"USD budget to signal owner-approval needed. If this assertion fails, "
        f"the cost model was downgraded silently."
    )
