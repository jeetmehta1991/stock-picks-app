"""Sprint 7 Phase A custom toolkits package.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Part D (DEC-507
wiring matrix). Each of the 11 agents in TauricResearch/TradingAgents
receives a custom toolkit that bridges to our project's existing data
layer (data_prefetch/, backtest/signals/, backtest/data/,
backtest/engine/regime_filter).

Sprint 7 Phase A (Batch 350) scope:
- OurTechnicalToolkit (Market Analyst)         - implemented (5 methods)
- OurFundamentalsToolkit (Fundamentals Analyst) - implemented (5 methods)
- OurNewsToolkit (News Analyst)                - implemented (3 methods)
- OurTraderToolkit (Trader)                    - SCAFFOLD; HARD DEP on BUG-095 Portfolio
- OurRiskToolkit (Risk Debaters)               - SCAFFOLD; HARD DEP on BUG-095 Portfolio

Each toolkit exposes deterministic methods that read from cached data
sources (PIT-correct by construction; no live API). Per Stage 2 HARD CUT
NO-LIVE-API rule, methods that would require live API on a cache-miss
return an empty dict / sentinel rather than fetch.
"""
from backtest.agents.toolkits.our_technical_toolkit import OurTechnicalToolkit
from backtest.agents.toolkits.our_fundamentals_toolkit import OurFundamentalsToolkit
from backtest.agents.toolkits.our_news_toolkit import OurNewsToolkit
from backtest.agents.toolkits.our_trader_toolkit import OurTraderToolkit
from backtest.agents.toolkits.our_risk_toolkit import OurRiskToolkit
from backtest.agents.toolkits.state_augmentation import (
    AugmentedAgentState,
    build_augmented_state,
)

__all__ = [
    "OurTechnicalToolkit",
    "OurFundamentalsToolkit",
    "OurNewsToolkit",
    "OurTraderToolkit",
    "OurRiskToolkit",
    "AugmentedAgentState",
    "build_augmented_state",
]
