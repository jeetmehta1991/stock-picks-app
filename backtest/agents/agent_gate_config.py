"""Agent gate config (Batch 245 / DEC-459 Option C Hybrid).

Phase 1B Sprint 7 infrastructure - parallel-safe with Phase 1A-alpha procs
(NEW file, no engine touch).

Per DEC-459 (RESOLVED-DECIDED, supersedes DEC-042): hybrid agent-gating
config that lets owner pick from 5 modes per Phase 1B-alpha A/B arm:

  MODE_FULL_WITH_VETO        : 11 agents run; Risk Manager veto active.
                               Trader decision -> Risk debate -> PM final.
                               Most agent participation; highest cost.
  MODE_NO_RISK               : 11 agents minus Risk Debaters (3 nodes off).
                               Trader -> PM direct. ~70% of full cost.
                               Tests Risk debate marginal value.
  MODE_ANALYSTS_ONLY         : 3 analysts (Market/Fundamental/News) only.
                               Their consensus -> Trader -> PM. ~40% cost.
                               Tests if research layer alone adds value.
  MODE_RULES_ONLY            : Zero agents. Baseline arm. $0 spend.
                               (Same as Phase 1A-alpha; included for A/B
                               comparison parity.)
  MODE_CONSENSUS_REQUIRED    : All-or-nothing - agents must reach unanimous
                               BUY for trade entry (else skip). Conservative.

Used by ab_orchestrator.py to drive 3-arm Phase 1B-alpha A/B:
  Arm A (rules_only)        : MODE_RULES_ONLY
  Arm B (full_with_veto)    : MODE_FULL_WITH_VETO
  Arm C (no_risk)           : MODE_NO_RISK

Joint with:
  - DEC-216 (A/B orchestrator wiring; PARTIAL-IMPL pre-this-module)
  - DEC-131 (agent value-add gate: agent_sharpe - rules_sharpe >= 0.2)
  - DEC-462-468 (LangGraph state augmentation per TRADINGAGENTS_DATA_AUDIT.md)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AgentMode(str, Enum):
    """Five agent-pipeline routing modes per DEC-459 Option C Hybrid."""
    FULL_WITH_VETO     = "full_with_veto"
    NO_RISK            = "no_risk"
    ANALYSTS_ONLY      = "analysts_only"
    RULES_ONLY         = "rules_only"
    CONSENSUS_REQUIRED = "consensus_required"


# Per-mode agent activation map (which of 11 agent nodes participates)
# 11 agents per DEC-057: 3 analysts + Bull/Bear/RM + Trader + 3 Risk +
# Portfolio Manager + Reflection (post-trade).
_MODE_AGENTS = {
    AgentMode.FULL_WITH_VETO: {
        "market_analyst", "fundamental_analyst", "news_analyst",
        "bull_researcher", "bear_researcher", "research_manager",
        "trader",
        "aggressive_debater", "conservative_debater", "neutral_debater",
        "portfolio_manager",
        "reflection",  # post-decision
    },
    AgentMode.NO_RISK: {
        "market_analyst", "fundamental_analyst", "news_analyst",
        "bull_researcher", "bear_researcher", "research_manager",
        "trader",
        "portfolio_manager",
        "reflection",
    },
    AgentMode.ANALYSTS_ONLY: {
        "market_analyst", "fundamental_analyst", "news_analyst",
        "trader",
        "portfolio_manager",
    },
    AgentMode.RULES_ONLY: set(),  # zero agents
    AgentMode.CONSENSUS_REQUIRED: {
        "market_analyst", "fundamental_analyst", "news_analyst",
        "bull_researcher", "bear_researcher", "research_manager",
        "trader",
        "aggressive_debater", "conservative_debater", "neutral_debater",
        "portfolio_manager",
    },
}


@dataclass
class AgentGateConfig:
    """Per-run agent pipeline config.

    Per DEC-459 RESOLVED-DECIDED. Joint with DEC-131 (gate) + DEC-216
    (orchestrator). Used by ab_orchestrator.py and Phase 1B agent pipeline.
    """
    mode: AgentMode = AgentMode.RULES_ONLY
    consensus_threshold: float = 1.0  # for CONSENSUS_REQUIRED; 1.0 = unanimous
    veto_enabled: bool = True  # Risk Manager can veto trader; ignored if no Risk Debaters in mode
    temperature: float = 0.0  # LLM temp; canonical 0 per CLAUDE.md
    model: str = "claude-haiku-4-5-20251001"  # Phase 1B = Haiku; 1C = Sonnet
    max_candidates_per_day: int = 10  # CLAUDE.md approved rule
    reflection_enabled: bool = True  # post-decision reflection node
    cost_ceiling_usd: Optional[float] = None  # halt run if cumulative spend > ceiling

    def active_agents(self) -> set[str]:
        """Return set of agent node names active in this mode."""
        return set(_MODE_AGENTS.get(self.mode, set()))

    def is_active(self, agent_name: str) -> bool:
        """Check whether a specific agent participates in this mode."""
        return agent_name in self.active_agents()

    def estimated_cost_per_candidate(self) -> float:
        """Rough cost estimate per candidate evaluation (USD).

        Per CLAUDE.md: Haiku ~$0.00035 per agent call * N agents.
        Sonnet ~10x Haiku.
        """
        n_agents = len(self.active_agents())
        per_call = 0.00035 if "haiku" in self.model.lower() else 0.0035
        return n_agents * per_call

    def as_dict(self) -> dict:
        """Serialize for logging + manifest tracking."""
        return {
            "mode":                   self.mode.value,
            "consensus_threshold":    self.consensus_threshold,
            "veto_enabled":           self.veto_enabled,
            "temperature":            self.temperature,
            "model":                  self.model,
            "max_candidates_per_day": self.max_candidates_per_day,
            "reflection_enabled":     self.reflection_enabled,
            "cost_ceiling_usd":       self.cost_ceiling_usd,
            "active_agents":          sorted(self.active_agents()),
            "estimated_cost_per_candidate": round(self.estimated_cost_per_candidate(), 5),
        }


# Convenience factories per Phase 1B-alpha 3-arm A/B
def arm_a_rules_only(**overrides) -> AgentGateConfig:
    """Arm A baseline - no agents. Phase 1A-alpha parity."""
    return AgentGateConfig(mode=AgentMode.RULES_ONLY, **overrides)


def arm_b_full_with_veto(**overrides) -> AgentGateConfig:
    """Arm B full 11-agent pipeline with Risk veto."""
    return AgentGateConfig(mode=AgentMode.FULL_WITH_VETO, **overrides)


def arm_c_no_risk(**overrides) -> AgentGateConfig:
    """Arm C - 11 agents minus Risk Debaters."""
    return AgentGateConfig(mode=AgentMode.NO_RISK, **overrides)
