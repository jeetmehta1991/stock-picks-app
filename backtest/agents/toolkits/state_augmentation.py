"""State augmentation - bridges our toolkits into TradingAgents AgentState.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Part E (Sections
25-26: State Schema Extensions + State Injection Points).

The upstream TradingAgentsState (vendored/tradingagents/agents/utils/
agent_states.py) is a dict-like state propagated through the LangGraph.
Per Pattern 2, we extend it with our project-specific fields BEFORE the
graph runs - the agents see these via state['key'] in their tool calls.

Sprint 7 Phase A (Batch 350): defines the augmented schema as a TypedDict
+ a builder function that calls our 5 toolkits to populate each field.

State injection points (per audit):
  - Phase 1 entry: regime_context + portfolio_context
  - Phase 2 entry: smart_money_signal + historical_outcomes + short_interest
  - Phase 3 entry: portfolio_context (refreshed; e.g., after Phase 2 decision)
  - Phase 4 entry: regime_context (refreshed)

This module provides the build_augmented_state() that materializes the
fields once per (ticker, as_of); the real runtime injection happens in
langgraph_pipeline.run_phase_1b_alpha after wiring to upstream
TradingAgentsGraph.propagate().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, TypedDict


class AugmentedAgentState(TypedDict, total=False):
    """Type-hinted dict mirroring upstream AgentState + our extensions.

    Upstream fields (inherited from TradingAgentsState):
      - market_report:        str
      - fundamentals_report:  str
      - news_report:          str
      - investment_plan:      str
      - trader_decision:      str
      - risk_debate_history:  list[dict]
      - final_decision:       dict (Pydantic-equivalent)

    Our additions per DEC-462-468 + audit Part E:
    """
    # Upstream (declared here as Optional for unit-test convenience)
    market_report: str
    fundamentals_report: str
    news_report: str
    investment_plan: str
    trader_decision: str
    risk_debate_history: list
    final_decision: dict

    # Our project-specific extensions
    ticker: str
    as_of: str  # ISO date string
    smart_money_signal: dict
    regime_context: dict
    portfolio_context: dict
    event_proximity: dict
    sector_context: dict
    short_interest_signal: dict
    historical_outcomes: dict


@dataclass
class StateBuilderToolkits:
    """Bundle of the 5 toolkits used to populate the augmented state.

    Kept as a separate dataclass so the langgraph_pipeline + tests can
    inject mocked / partial toolkit instances without rewriting the
    builder logic.
    """
    technical: Any  # OurTechnicalToolkit
    fundamentals: Any  # OurFundamentalsToolkit
    news: Any  # OurNewsToolkit
    trader: Any  # OurTraderToolkit
    risk: Any  # OurRiskToolkit


def build_augmented_state(
    ticker: str,
    as_of: date,
    toolkits: StateBuilderToolkits,
    sector_etf: str | None = None,
) -> AugmentedAgentState:
    """Materialize the augmented state for a (ticker, as_of) pair.

    Calls each toolkit method that doesn't require LLM context, returning
    a dict suitable for state-injection into the LangGraph propagate call.

    Args:
        ticker: equity symbol
        as_of: trading date
        toolkits: bundle of 5 toolkit instances
        sector_etf: optional sector ETF for relative-strength (defaults to
            SPY if None)

    Returns AugmentedAgentState (TypedDict). Upstream report fields
    (market_report / fundamentals_report / etc.) are left absent here -
    they get populated by the analyst nodes in the graph itself.
    """
    sector_etf = sector_etf or "SPY"
    state: AugmentedAgentState = {
        "ticker": ticker,
        "as_of": as_of.isoformat(),
    }

    # Regime context (DEC-106) - injected at Phase 1 entry
    state["regime_context"] = toolkits.risk.get_volatility_regime(as_of)

    # Portfolio context (BUG-095 scaffolded) - injected at Phase 1 + Phase 3
    state["portfolio_context"] = toolkits.trader.get_portfolio_state()

    # Smart money composite (DEC-124) - injected at Phase 2 (Bull/Bear debate)
    insider = toolkits.fundamentals.get_insider_transactions(ticker, as_of)
    congress = toolkits.fundamentals.get_congressional_trades(ticker, as_of)
    inst = toolkits.fundamentals.get_13f_holdings(ticker, as_of)
    state["smart_money_signal"] = {
        "insider": insider,
        "congressional": congress,
        "institutional": inst,
    }

    # Event proximity (DEC-348/349) - injected at Phase 1 + Phase 4 (Risk)
    state["event_proximity"] = toolkits.risk.get_event_proximity(as_of)

    # Sector context - injected at Phase 1
    state["sector_context"] = toolkits.technical.get_sector_relative_strength(
        ticker, sector_etf, as_of
    )

    # Short interest (Gap D - Ortex pending, scaffold for now)
    state["short_interest_signal"] = {
        "ticker": ticker, "as_of": as_of.isoformat(), "scaffold_pending_ortex": True
    }

    # Historical outcomes (DEC-189 reflection log scaffold)
    state["historical_outcomes"] = toolkits.risk.get_recent_outcomes_on_similar_setups(
        ticker, "default_signature", as_of
    )

    return state
