# Phase 1B AgentState schema diff (upstream vs our augmented)

> **B909 SUPERSEDED-BY-NOTICE (2026-06-19 per owner directive Dec-2 update in place):** This doc was authored Batch 351 (2026-05-25) and captures the AgentState schema diff at that point in time. Superseded-by-effect: **`PATH_TO_PHASE_1B_ALPHA.md`** (B894 canonical Phase 1B-α path) + **`backtest/agents/toolkits/state_augmentation.py`** (live code authoritative). This historical schema diff retained for batch-lineage traceability (B350/B351 Sprint 7); any divergence post-2026-05-25 not reflected here. Canonical state schema = live code; canonical Phase 1B-α path = PATH_TO_PHASE_1B_ALPHA.md.

**Source** (per CHECKLIST #77 canonical-source attribution):
- Upstream: `vendored/tradingagents/tradingagents/agents/utils/agent_states.py` (TauricResearch/TradingAgents v0.2.5 commit `61522e1`)
- Ours: `backtest/agents/toolkits/state_augmentation.py` (Sprint 7 Batch 350 + 351)
- Reconciliation: Batch 351 2026-05-25 — read upstream source verbatim, renamed our extension fields to match upstream where the schemas overlap, added the upstream-required init keys to `build_augmented_state()`.

**Created:** Sprint 7 Batch 351 2026-05-25
**Purpose:** Pin the field-name mapping between upstream `AgentState` and our `AugmentedAgentState` so the LangGraph nodes can read state we wrote, and we can read state the nodes wrote.

---

## Upstream AgentState (verbatim from agent_states.py)

```python
class AgentState(MessagesState):              # MessagesState contributes `messages` list
    company_of_interest:       str            # set by Propagator.create_initial_state
    asset_type:                str            # "stock" / "crypto" — default "stock"
    trade_date:                str            # ISO date as string
    sender:                    str            # last agent to set state
    market_report:             str
    sentiment_report:          str            # Social Analyst's slot (DEC-057 dropped Social
                                              # but upstream still names the slot "sentiment")
    news_report:               str
    fundamentals_report:       str
    investment_debate_state:   InvestDebateState  # Bull/Bear/Research-Manager subdict
    investment_plan:           str
    trader_investment_plan:    str            # Trader output (str, not dict)
    risk_debate_state:         RiskDebateState  # Aggressive/Conservative/Neutral subdict
    final_trade_decision:      str            # Portfolio Manager output (str, not dict)
    past_context:              str            # memory-log injection at run start
```

### Upstream sub-states

```python
class InvestDebateState(TypedDict):
    bull_history:        str
    bear_history:        str
    history:             str
    current_response:    str
    judge_decision:      str    # Research Manager's synthesis
    count:               int

class RiskDebateState(TypedDict):
    aggressive_history:                  str
    conservative_history:                str
    neutral_history:                     str
    history:                             str
    latest_speaker:                      str
    current_aggressive_response:         str
    current_conservative_response:       str
    current_neutral_response:            str
    judge_decision:                      str    # Portfolio Manager's synthesis
    count:                               int
```

## Upstream initial state (Propagator.create_initial_state)

```python
{
    "messages":                  [("human", company_name)],
    "company_of_interest":       company_name,
    "asset_type":                asset_type,            # default "stock"
    "trade_date":                str(trade_date),
    "past_context":              past_context,
    "investment_debate_state":   InvestDebateState({...all empties...}),
    "risk_debate_state":         RiskDebateState({...all empties...}),
    "market_report":             "",
    "fundamentals_report":       "",
    "sentiment_report":          "",
    "news_report":               "",
}
```

## Our AugmentedAgentState (Sprint 7 Batch 350 + 351 reconciled)

### Section A: upstream-identical keys (names MUST match)

We set these in `build_augmented_state` so the dict can drop directly into upstream `Propagator.create_initial_state(...)` equivalent path without name remap.

| Field | Type | Source | Stage where set |
|---|---|---|---|
| `company_of_interest` | str | ticker | run start |
| `asset_type` | str | "stock" | run start (hardcoded for swing-equity scope) |
| `trade_date` | str | as_of.isoformat() | run start |
| `past_context` | str | "" until DEC-189 reflection log ships | run start |

Upstream owns these write-once-during-graph keys; we declare them in the TypedDict for type-completeness only:

| Field | Type | Set by |
|---|---|---|
| `sender` | str | last agent to write state |
| `market_report` | str | Market Analyst node |
| `sentiment_report` | str | (DEC-057 dropped Social — slot stays empty) |
| `news_report` | str | News Analyst node |
| `fundamentals_report` | str | Fundamentals Analyst node |
| `investment_debate_state` | InvestDebateState | Bull/Bear/Research Manager nodes |
| `investment_plan` | str | Research Manager node |
| `trader_investment_plan` | str | Trader node |
| `risk_debate_state` | RiskDebateState | Aggressive/Conservative/Neutral debaters |
| `final_trade_decision` | str | Portfolio Manager node |

### Section B: our project extensions (no upstream conflict)

`build_augmented_state` populates these BEFORE the graph runs. The agents access them via tool calls dispatched through their custom toolkits (per DEC-507 wiring matrix).

| Extension field | Source toolkit | Audit reference |
|---|---|---|
| `ticker` | run-start input | convenience alias for `company_of_interest` |
| `as_of` | run-start input | convenience alias for `trade_date` |
| `smart_money_signal` | OurFundamentalsToolkit (insider + congressional + 13F) | DEC-124 confluence |
| `regime_context` | OurRiskToolkit.get_volatility_regime | DEC-106 |
| `portfolio_context` | OurTraderToolkit.get_portfolio_state | BUG-095 dependency |
| `event_proximity` | OurRiskToolkit.get_event_proximity | DEC-348 / 349 |
| `sector_context` | OurTechnicalToolkit.get_sector_relative_strength | DEC-118 |
| `short_interest_signal` | (Ortex pending — Gap D) | scaffold only |
| `historical_outcomes` | OurRiskToolkit.get_recent_outcomes_on_similar_setups | DEC-189 (scaffold) |

## Field-name changes applied in Batch 351

The Batch 350 declaration of `AugmentedAgentState` had 3 fields that did NOT match upstream. Renamed in Batch 351 to prevent silent state-write desync once the real graph runs:

| Batch 350 name (WRONG) | Batch 351 name (CORRECT) | Source |
|---|---|---|
| `trader_decision: str` | `trader_investment_plan: str` | agent_states.py line 67 |
| `risk_debate_history: list` | `risk_debate_state: dict` (RiskDebateState) | agent_states.py line 70 |
| `final_decision: dict` | `final_trade_decision: str` | agent_states.py line 73 |

Also added in Batch 351 (omitted in Batch 350):

| Added field | Reason |
|---|---|
| `company_of_interest`, `asset_type`, `trade_date`, `past_context` | Required by `Propagator.create_initial_state` — these are the entry-point keys |
| `sender`, `sentiment_report`, `investment_debate_state`, `investment_plan` | Upstream graph writes these; we need to declare them for type-completeness |

## What Batch 351 does NOT change

- The toolkit method signatures (5 toolkits' methods stay identical)
- The `build_augmented_state(ticker, as_of, toolkits)` argument signature
- The 9 project extension keys (Section B above)
- Cache-miss return shape (`{"error": "cache_miss"}` etc.)

So `test_toolkits_phase_a.py` from Batch 350 stays green; new tests in Batch 351 pin the upstream-key population behavior.

## Next-batch follow-on

When Hetzner runs Python 3.12 with `pip install -e vendored/tradingagents`, a `test_langgraph_propagate_integration.py` test should:
1. Import upstream `Propagator` + `TradingAgentsGraph`
2. Build our `AugmentedAgentState` via `build_augmented_state()`
3. Verify `Propagator.create_initial_state(company_name, trade_date, asset_type, past_context)` accepts those same keys
4. Pass the augmented dict through `TradingAgentsGraph.propagate(...)` with all LLM clients mocked at the `BaseChatModel` boundary
5. Assert that `final_trade_decision` (str) is populated with a parseable BUY / HOLD / SELL token

That test cannot run on Python 3.14 today (no langgraph wheels) — it's deferred to the Hetzner 3.12 environment per `vendored/MANIFEST.md` caveat.
