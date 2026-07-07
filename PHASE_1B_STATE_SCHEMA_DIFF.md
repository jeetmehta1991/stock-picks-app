<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1233 2026-07-07 doc-sync sweep -->

<!-- 🟢 COUNCIL 278-287 SYNC BANNER (B1233 2026-07-07) — READ FIRST BEFORE THIS DOC -->
> **Doc-sync status:** This document may contain references stale as of 2026-06-27 or earlier. The current state below overrides any stale references in the body until the next full-rewrite.
>
> **Current canonical values (as of 2026-07-07 B1231):**
> - `len(ALL_STRATEGIES) = 219` (was 220 pre-B1189 DELETE of dxy_headwind_multinational_short; was 221 pre-B874)
> - `STRATEGIES_DISABLED_MISSING_PRODUCER = set()` (was `{dxy_headwind_multinational_short}` pre-B1189)
> - Active strategies for Phase 1A-β cube: 219; cube cells 219×26 = 5,694
> - Test count: **858 passed, 2 skipped** on `test_unit.py + test_integration.py`
> - **CHECKLIST items:** #1–#157 (added #151-#157 in Councils 279-285)
> - **LEARNINGS lessons:** through L202 (added L197-L202 in Councils 279-285)
> - **Latest batch:** B1231 (Council 285)
>
> **Recent Council 278-287 milestones (chronological):**
> - Council 278 (B1188-B1204): 40 SKIP strategies loosened per CSV recommendations
> - Council 279 (B1205-B1210): 11 silent misses remediated + L197 + CHECKLIST #151-#153
> - Council 280 (B1211-B1213): News coverage refined (84.2%) + CHECKLIST #154 codified
> - Council 281 (B1214-B1216): short_interest_pct producer bug + institutional 30% gap surfaced
> - Council 282 (B1217-B1219): Cross-audit 192 strategies + CHECKLIST #155
> - Council 283 (B1220-B1223): 5 more producer audits + comprehensive report
> - Council 284 (B1224-B1228): All 25+ producers audited + historical 2020-2023 spot-check + L201 + CHECKLIST #156
> - Council 285 (B1229-B1231): 2 critical bugs FIXED with graceful degradation + L202 + CHECKLIST #157
> - Council 287 (B1232-B1236 in progress): Stage 4 walks archived + doc-sync sweep
>
> **Stage 4 walks: ARCHIVED 2026-07-07 to `archive/2026-07-07-stage-4-walks-complete/`** (Council 121+ 2026-06-27 owner-approved completion). Any `STAGE_4_*.md` reference in this doc now points to archived location.
>
> **Producer coverage (all 25+ producers audited Councils 280-284):**
> - news_sentiment 84.2% / short_interest_dtc 97.7% / **short_interest_pct 0%** (bug; graceful-degradation fix in B1229) / pead 85% / insider 18.8% (event-rarity) / **institutional_signal 85%** (B1230 corrected from B1216's 30% misattribution) / congressional 67.7% / sec_edgar 97.7% / search_volume 99.2% / index_rebalance 10.5% (event) / earnings_yoy 78.9% / cot_positioning 100% / cross_asset 100% (5 fns) / calendar_effects 100% / macro_events 100% / OHLCV-derived (chart_patterns/technical/dec513/multi_timeframe/cross_sectional/ict_producers/volume_profile/smc_ict/pairs_trading) all 100% (bounded by ~84% OHLCV cache)
> - **Critical historical finding (B1227):** news_sentiment 0% in 2020; short_interest_dtc 0% in 2020; institutional 0% in 2020-2021. Backtest interpretation must annotate producer coverage TIMELINE.
>
> **Sprint 5 tickets queued (post-Council 285 priorities):**
> - S5-B1214-SHARES-OUTSTANDING (HIGH; 1 strategy; 1d) - remove B1229 fallback when data ships
> - S5-B1216-INSTITUTIONAL-13F (MED after B1230 correction; 1 strategy; 1-2d) - expand T1a persistence file
> - S5-B1212-SECONDARY-NEWS (MED; 6 strategies; 2d) - Finnhub/AlphaVantage fallback
>
> **Comprehensive coverage report:** `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

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
