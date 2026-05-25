"""Phase 1B agent test pyramid (Batch 347+) — closes P1B-008 + P1B-009
test-coverage gaps from PHASE_1B_AUDIT_2026_05_25.md.

Coverage targets per audit doc:
  T1 Unit:        AgentGateConfig dataclass + 5 mode -> active_agents
                  composition + arm_a/b/c factory defaults + cost estimate
  T1 Unit:        pipeline._call_claude retry classification + jitter
                  (added Batch 346)
  T1 Unit:        pipeline._parse_json_response markdown/regex/empty paths
                  (added Batch 346)
  T3 Integration: _agent_cache_key collision invariants + cache round-trip
  T9 Acceptance:  AgentGateConfig mode active_agents matches DEC-459
                  Option C Hybrid spec

Per CHECKLIST #69 + DEC-503 + TESTING_PYRAMID_REFERENCE.md.
"""
from __future__ import annotations

import pytest


# =============================================================================
# AgentGateConfig dataclass + factory tests (P1B-009)
# =============================================================================


class TestAgentMode:
    """AgentMode enum semantics + DEC-459 Option C Hybrid arm-map."""

    def test_enum_values(self):
        from backtest.agents.agent_gate_config import AgentMode
        # 5 modes per DEC-459 Option C
        modes = {m.value for m in AgentMode}
        assert modes == {
            "full_with_veto", "no_risk", "analysts_only",
            "rules_only", "consensus_required",
        }

    def test_rules_only_has_zero_agents(self):
        from backtest.agents.agent_gate_config import AgentMode, _MODE_AGENTS
        assert _MODE_AGENTS[AgentMode.RULES_ONLY] == set()

    def test_full_with_veto_has_11_agents(self):
        from backtest.agents.agent_gate_config import AgentMode, _MODE_AGENTS
        # Per CLAUDE.md: 11 active agents + reflection = 12 nodes
        agents = _MODE_AGENTS[AgentMode.FULL_WITH_VETO]
        # 3 analysts + 3 research + 1 trader + 3 risk + 1 PM + 1 reflection = 12
        assert len(agents) == 12

    def test_full_with_veto_includes_3_analysts(self):
        from backtest.agents.agent_gate_config import AgentMode, _MODE_AGENTS
        agents = _MODE_AGENTS[AgentMode.FULL_WITH_VETO]
        for name in ("market_analyst", "fundamental_analyst", "news_analyst"):
            assert name in agents

    def test_full_with_veto_includes_3_risk_debaters(self):
        from backtest.agents.agent_gate_config import AgentMode, _MODE_AGENTS
        agents = _MODE_AGENTS[AgentMode.FULL_WITH_VETO]
        for name in ("aggressive_debater", "conservative_debater", "neutral_debater"):
            assert name in agents

    def test_no_risk_excludes_risk_debaters(self):
        from backtest.agents.agent_gate_config import AgentMode, _MODE_AGENTS
        agents = _MODE_AGENTS[AgentMode.NO_RISK]
        for name in ("aggressive_debater", "conservative_debater", "neutral_debater"):
            assert name not in agents, (
                f"NO_RISK mode must exclude {name} (Risk debater)"
            )

    def test_analysts_only_excludes_research_debate(self):
        from backtest.agents.agent_gate_config import AgentMode, _MODE_AGENTS
        agents = _MODE_AGENTS[AgentMode.ANALYSTS_ONLY]
        for name in ("bull_researcher", "bear_researcher", "research_manager"):
            assert name not in agents

    def test_consensus_required_includes_all_voting_agents(self):
        from backtest.agents.agent_gate_config import AgentMode, _MODE_AGENTS
        agents = _MODE_AGENTS[AgentMode.CONSENSUS_REQUIRED]
        # All non-reflection voting agents
        for name in (
            "market_analyst", "fundamental_analyst", "news_analyst",
            "bull_researcher", "bear_researcher", "research_manager",
            "trader", "aggressive_debater", "conservative_debater",
            "neutral_debater", "portfolio_manager",
        ):
            assert name in agents


class TestAgentGateConfig:
    """AgentGateConfig dataclass + helper methods."""

    def test_default_is_rules_only(self):
        from backtest.agents.agent_gate_config import AgentGateConfig, AgentMode
        cfg = AgentGateConfig()
        assert cfg.mode == AgentMode.RULES_ONLY

    def test_active_agents_returns_set(self):
        from backtest.agents.agent_gate_config import AgentGateConfig, AgentMode
        cfg = AgentGateConfig(mode=AgentMode.FULL_WITH_VETO)
        agents = cfg.active_agents()
        assert isinstance(agents, set)
        assert len(agents) == 12

    def test_is_active_membership(self):
        from backtest.agents.agent_gate_config import AgentGateConfig, AgentMode
        cfg = AgentGateConfig(mode=AgentMode.FULL_WITH_VETO)
        assert cfg.is_active("market_analyst") is True
        assert cfg.is_active("nonexistent_agent") is False

    def test_estimated_cost_haiku_vs_sonnet(self):
        from backtest.agents.agent_gate_config import AgentGateConfig, AgentMode
        haiku = AgentGateConfig(mode=AgentMode.FULL_WITH_VETO, model="claude-haiku-4-5-20251001")
        sonnet = AgentGateConfig(mode=AgentMode.FULL_WITH_VETO, model="claude-sonnet-4-6")
        # Sonnet is ~10x Haiku per CLAUDE.md
        haiku_cost = haiku.estimated_cost_per_candidate()
        sonnet_cost = sonnet.estimated_cost_per_candidate()
        assert sonnet_cost > haiku_cost
        assert 8 <= (sonnet_cost / haiku_cost) <= 12  # ~10x band

    def test_estimated_cost_rules_only_is_zero(self):
        from backtest.agents.agent_gate_config import AgentGateConfig, AgentMode
        cfg = AgentGateConfig(mode=AgentMode.RULES_ONLY)
        assert cfg.estimated_cost_per_candidate() == 0.0

    def test_as_dict_round_trip(self):
        from backtest.agents.agent_gate_config import AgentGateConfig, AgentMode
        cfg = AgentGateConfig(mode=AgentMode.FULL_WITH_VETO, veto_enabled=True,
                              cost_ceiling_usd=150.0)
        d = cfg.as_dict()
        # Schema check
        for k in ("mode", "consensus_threshold", "veto_enabled", "temperature",
                  "model", "max_candidates_per_day", "reflection_enabled",
                  "cost_ceiling_usd", "active_agents",
                  "estimated_cost_per_candidate"):
            assert k in d
        assert d["mode"] == "full_with_veto"
        assert d["cost_ceiling_usd"] == 150.0
        assert isinstance(d["active_agents"], list)
        assert d["active_agents"] == sorted(d["active_agents"])  # sorted


class TestArmFactories:
    """arm_a_rules_only / arm_b_full_with_veto / arm_c_no_risk."""

    def test_arm_a_rules_only(self):
        from backtest.agents.agent_gate_config import arm_a_rules_only, AgentMode
        cfg = arm_a_rules_only()
        assert cfg.mode == AgentMode.RULES_ONLY
        assert cfg.active_agents() == set()

    def test_arm_b_full_with_veto(self):
        from backtest.agents.agent_gate_config import arm_b_full_with_veto, AgentMode
        cfg = arm_b_full_with_veto()
        assert cfg.mode == AgentMode.FULL_WITH_VETO
        assert "aggressive_debater" in cfg.active_agents()
        assert "portfolio_manager" in cfg.active_agents()

    def test_arm_c_no_risk(self):
        from backtest.agents.agent_gate_config import arm_c_no_risk, AgentMode
        cfg = arm_c_no_risk()
        assert cfg.mode == AgentMode.NO_RISK
        assert "aggressive_debater" not in cfg.active_agents()
        assert "trader" in cfg.active_agents()  # Trader still present

    def test_arm_overrides_propagate(self):
        from backtest.agents.agent_gate_config import arm_b_full_with_veto
        cfg = arm_b_full_with_veto(cost_ceiling_usd=42.5, temperature=0.3)
        assert cfg.cost_ceiling_usd == 42.5
        assert cfg.temperature == 0.3

    def test_arm_a_b_c_have_distinct_modes(self):
        from backtest.agents.agent_gate_config import (
            arm_a_rules_only, arm_b_full_with_veto, arm_c_no_risk,
        )
        modes = {arm_a_rules_only().mode, arm_b_full_with_veto().mode,
                 arm_c_no_risk().mode}
        assert len(modes) == 3


# =============================================================================
# pipeline._agent_cache_key collision tests (P1B-008 partial)
# =============================================================================


class TestAgentCacheKey:
    """Cache-key generation: deterministic + collision-resistant."""

    def test_same_inputs_same_key(self):
        from backtest.agents.pipeline import _agent_cache_key
        from datetime import date
        k1 = _agent_cache_key("AAPL", date(2024, 1, 15), ["rsi_oversold"], "phase_1b")
        k2 = _agent_cache_key("AAPL", date(2024, 1, 15), ["rsi_oversold"], "phase_1b")
        assert k1 == k2

    def test_different_ticker_different_key(self):
        from backtest.agents.pipeline import _agent_cache_key
        from datetime import date
        k1 = _agent_cache_key("AAPL", date(2024, 1, 15), ["rsi_oversold"], "phase_1b")
        k2 = _agent_cache_key("MSFT", date(2024, 1, 15), ["rsi_oversold"], "phase_1b")
        assert k1 != k2

    def test_different_date_different_key(self):
        from backtest.agents.pipeline import _agent_cache_key
        from datetime import date
        k1 = _agent_cache_key("AAPL", date(2024, 1, 15), [], "phase_1b")
        k2 = _agent_cache_key("AAPL", date(2024, 2, 15), [], "phase_1b")
        assert k1 != k2

    def test_disable_news_changes_key(self):
        from backtest.agents.pipeline import _agent_cache_key
        from datetime import date
        k1 = _agent_cache_key("AAPL", date(2024, 1, 15), [], "phase_1b", disable_news=False)
        k2 = _agent_cache_key("AAPL", date(2024, 1, 15), [], "phase_1b", disable_news=True)
        assert k1 != k2

    def test_strategy_list_order_independent(self):
        from backtest.agents.pipeline import _agent_cache_key
        from datetime import date
        k1 = _agent_cache_key("AAPL", date(2024, 1, 15), ["a", "b", "c"], "p")
        k2 = _agent_cache_key("AAPL", date(2024, 1, 15), ["c", "b", "a"], "p")
        # Strategy list is sorted internally -> order-independent
        assert k1 == k2

    def test_handles_dict_strategies(self):
        """BUG-276 regression: strategies as list of dicts."""
        from backtest.agents.pipeline import _agent_cache_key
        from datetime import date
        # No raise on dict input
        k = _agent_cache_key(
            "AAPL", date(2024, 1, 15),
            [{"strategy_class": "rsi_oversold"}, {"strategy_class": "bollinger_lower"}],
            "phase_1b",
        )
        assert isinstance(k, str)
        assert len(k) > 0


class TestAgentCacheRoundTrip:
    """Cache save/load round-trip."""

    def test_save_load_roundtrip(self, tmp_path, monkeypatch):
        from backtest.agents import pipeline
        monkeypatch.setattr(pipeline, "AGENT_CACHE_DIR", tmp_path)
        payload = {"tech_score": 7, "summary": "bullish"}
        pipeline._save_agent_cache("test_key_123", payload)
        loaded = pipeline._load_agent_cache("test_key_123")
        assert loaded == payload

    def test_load_missing_returns_none(self, tmp_path, monkeypatch):
        from backtest.agents import pipeline
        monkeypatch.setattr(pipeline, "AGENT_CACHE_DIR", tmp_path)
        assert pipeline._load_agent_cache("nonexistent_key") is None

    def test_load_corrupt_returns_none(self, tmp_path, monkeypatch):
        from backtest.agents import pipeline
        monkeypatch.setattr(pipeline, "AGENT_CACHE_DIR", tmp_path)
        bad_file = tmp_path / "badkey.json"
        bad_file.write_text("not valid json {{{")
        assert pipeline._load_agent_cache("badkey") is None


# =============================================================================
# pipeline.py _call_claude API guard tests (P1B-008 partial; Batch 346 follow-up)
# =============================================================================


class TestCallClaude:
    """Guard tests on _call_claude that don't require ANTHROPIC_API_KEY."""

    def test_returns_none_without_api_key(self, monkeypatch):
        from backtest.agents import pipeline
        monkeypatch.setattr(pipeline, "ANTHROPIC_KEY", "")
        out = pipeline._call_claude("test", "claude-haiku")
        assert out is None


# =============================================================================
# pipeline.py _parse_json_response paths (P1B-008 partial; Batch 346 follow-up)
# =============================================================================


class TestParseJsonResponse:
    """Edge-case coverage of _parse_json_response beyond Batch 346 tests."""

    def test_pure_json_object(self):
        from backtest.agents.pipeline import _parse_json_response
        assert _parse_json_response('{"a": 1, "b": [2,3]}') == {"a": 1, "b": [2, 3]}

    def test_markdown_fenced_json_typed(self):
        from backtest.agents.pipeline import _parse_json_response
        out = _parse_json_response('```json\n{"key":"value"}\n```')
        assert out == {"key": "value"}

    def test_markdown_fenced_no_language(self):
        from backtest.agents.pipeline import _parse_json_response
        out = _parse_json_response('```\n{"key":"value"}\n```')
        assert out == {"key": "value"}

    def test_json_inside_prose(self):
        from backtest.agents.pipeline import _parse_json_response
        out = _parse_json_response('Here is the result: {"score": 7} based on analysis')
        assert out == {"score": 7}

    def test_completely_invalid_returns_empty(self):
        from backtest.agents.pipeline import _parse_json_response
        out = _parse_json_response('not json at all, just text')
        assert out == {}

    def test_truncated_json_returns_empty(self):
        from backtest.agents.pipeline import _parse_json_response
        out = _parse_json_response('{"a": 1, "b": [')  # truncated
        assert out == {}
