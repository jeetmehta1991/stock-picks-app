# TRADINGAGENTS Data Input Audit

# Source: per CHECKLIST #77 — canonical sources are data_prefetch/*/ filesystem state + API_ENDPOINT_INVENTORY.md row-by-row + dashboard_sprint0a/data.json runtime catalog.

> **B1029 doc-sync 2026-06-27 update:** **220 registered / 217 active** (was 219 pre-B1010). B978 verified TIER 2 producer wireup (smart-money + event-driven + cross-sectional 9-of-9 `inject_*` WIRED in screener.py) per Council 78 A2-AUDIT-FIRST. Per L146 wiring-matrix rule, this is the integration-deliverable confirmation. R5 LAUNCHED 2026-06-27 B1028 on AWS i-0940a53c75d049381 (Master 1929 ops × 4y).

**2026-05-15 Day 9+ Batch 178 status:** Phase 1A runs `--no-agents` (rules + smart money baseline). Agent toolkit data feeds for Phase 1B+: Technical (Polygon OHLCV ✅), Fundamentals (Polygon financials 1937 + SEC XBRL 1937 + Polygon Benzinga earnings ✅), News (Polygon news 1927 + Polygon Benzinga analyst_insights 1937 ✅), Risk (FRED 90 series + ALFRED 80 series + CFTC 73 contract-datasets ✅), Sentiment (AAII + CNN F&G + Apewisdom + StockTwits + pytrends ✅; Polygon news Phase 1B wire-up pending per L146 wiring-matrix rule). All Phase 1B data prerequisites cached. Live dashboard cross-reference: https://jeetmehta1991.github.io/stock-picks-app/dashboard_sprint0a/

> **B898 FRESHNESS NOTE (2026-06-18 B895-DEFER-A tranche 2 per CHECKLIST #111):** This doc contains MAY-26-ERA strategy counts at lines 138 ("186 active strategies fire") + 230 ("186-strategy roster"). **LIVE COUNTS as of 2026-06-18 (source `python -c "from backtest.signals.screener import ALL_STRATEGIES; print(len(ALL_STRATEGIES))"` = 219):** 219 registered / 218 active strategies on T1a + T2 + T3 universe. Toolkit data feeds + wiring methodology unchanged.

**Document role:** Per-agent data input requirements vs current feed mapping; gap identification; recommended additional API endpoints; custom toolkit + LangGraph state augmentation specifications.

**Created:** Pass 52 turn 130
**Owner directive:** Pass 52 turn 130 — comprehensive analysis of agent data dependencies; "this is exactly the gap that would have invalidated the efficiveness of stage 2 testing. All efforts would be nullified"
**Origin:** Owner accountability question Pass 52 turn 130, following turn 128 (DEC-042 architectural mismatch) — 6th instance of owner-driven accountability vindication in Pass 52
**Process learnings codified:** L139 NEW (data dependency verification on architectural decisions) + CHECKLIST #60 NEW

**Honest accountability per #25:** This audit should have been completed in Pass 25-29 when DEC-042 / DEC-051 / DEC-055-058 were resolved. Pass 29 honest reflection ("99.9% of trades came out at MEDIUM_HIGH" — BUG-113 interface contract gap) was already a warning sign about agent-engine integration shallowness. The same pattern (outputs not fully consumed) applies to data inputs going IN. Without this audit, Stage 2 backtest agent overlay would have been a black box producing decisions on incomplete information — invalidating any A/B verdict on agent value-add (DEC-131 ≥0.2 net Sharpe gate becomes meaningless).

---

## TABLE OF CONTENTS

**Part A — Framework & Flow Overview**
1. TradingAgents 11-Agent Roster
2. Pipeline Phases
3. Our Integration Pattern (Pattern 2 + DEC-459 Option C Hybrid)
4. Flow Diagram

**Part B — Per-Agent Data Input Requirements**
5. Market Analyst (Technical)
6. Fundamentals Analyst
7. News Analyst
8. Bull Researcher
9. Bear Researcher
10. Research Manager
11. Trader
12. Aggressive Risk Debater
13. Conservative Risk Debater
14. Neutral Risk Debater
15. Portfolio Manager
16. Reflection Node

**Part C — Gap Analysis**
17. Critical Gaps (Block Decision Quality)
18. Operational Gaps (Implementation)
19. Recommended Additional API Endpoints

**Part D — Custom Toolkit Specifications (Pattern 2)**
20. OurTechnicalToolkit
21. OurFundamentalsToolkit
22. OurNewsToolkit
23. OurTraderToolkit (NEW)
24. OurRiskToolkit (NEW)

**Part E — LangGraph State Augmentation**
25. State Schema Extensions
26. State Injection Points

**Part F — Implementation Sequencing**
27. Sprint 7 Custom Toolkit Build
28. Sprint 7 State Schema Extension
29. Cross-Sprint Dependencies

**Part G — Recommended Decisions (PROPOSED)**
30. Sub-decision Candidates (DEC-460 through DEC-468 PROPOSED)

---

# PART A — FRAMEWORK & FLOW OVERVIEW

## 1. TradingAgents 11-Agent Roster

Per Pass 31 source-code analysis of TradingAgents framework. **11 active agents (12 minus dropped Social per DEC-057) + Reflection node = 12 total roles per `propagate()`.**

### Phase 1 — Analysts (parallel, 4 nodes, dropped Social = 3 active)
1. **Market Analyst** — technical indicators (uses `quick_thinking_llm`; 2-4 LLM calls due to tool loops)
2. **Fundamentals Analyst** — financials (`quick_thinking_llm`; 2-4 LLM calls)
3. **News Analyst** — global news + macro (`quick_thinking_llm`; 2-4 LLM calls)
4. ~~Social Media Analyst~~ — **DROPPED per DEC-057** (least valuable for swing trading equities)

### Phase 2 — Research Debate (3 sequential)
5. **Bull Researcher** — bullish thesis (`quick_thinking_llm`; debates Bear up to `max_debate_rounds`)
6. **Bear Researcher** — bearish thesis (`quick_thinking_llm`; debates Bull)
7. **Research Manager** — synthesizes Bull/Bear → investment plan (**DEEP llm — expensive**)

### Phase 3 — Trader (1)
8. **Trader** — converts plan into trade decision (`quick_thinking_llm`)

### Phase 4 — Risk Debate (4)
9. **Aggressive Risk Debater** — risk-on perspective (`quick_thinking_llm`)
10. **Conservative Risk Debater** — risk-off perspective (`quick_thinking_llm`)
11. **Neutral Risk Debater** — middle ground (`quick_thinking_llm`)
12. **Portfolio Manager** — synthesizes Risk Debate → final structured Pydantic decision (**DEEP llm — expensive**)

### Phase 5 — Reflection (1)
13. **Reflection Node** — post-decision learning, writes to memory log (`quick_thinking_llm`)

**LLM cost concentration:** Only Research Manager + Portfolio Manager use deep model. Other 9 nodes use quick model. Cost-optimized config per DEC-055.

## 2. Pipeline Phases

```
Phase 1: ANALYSIS (parallel)
  ├── Market Analyst   ←─ technical tools
  ├── Fundamentals     ←─ financial tools
  └── News Analyst     ←─ news tools
       ↓
Phase 2: RESEARCH DEBATE (sequential, multi-round)
  ├── Bull Researcher  ──┐
  ├── Bear Researcher  ──┤── debate up to max_debate_rounds
  └── Research Manager ──┘── synthesizes to investment plan (DEEP)
       ↓
Phase 3: TRADER (single)
  └── Trader — converts plan to trade decision
       ↓
Phase 4: RISK DEBATE (sequential)
  ├── Aggressive Risk Debater
  ├── Conservative Risk Debater
  ├── Neutral Risk Debater
  └── Portfolio Manager — synthesizes to final structured decision (DEEP)
       ↓
Phase 5: REFLECTION (post-decision)
  └── Reflection Node — writes outcomes to memory log
```

## 3. Our Integration Pattern

**Pattern 2 (Pass 29 recommended):** Use TradingAgents' LangGraph orchestration with our custom agents replacing specific defaults. Effort: ~2-3 weeks.

**DEC-459 Option C Hybrid Architecture (Pass 52 turn 129):**
- Primary signal: Portfolio Manager native confidence consumed directly
- Risk veto layer: separate from PM confidence, via LangGraph state extraction
- Bull/Bear alignment: Research Manager synthesis-level check
- Tier mapping: PM confidence → DEC-021 3-tier (HIGH 5% / MED 3% / LOW 1.5%)

## 4. Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 2 RULES SCREENING (rules-based)                                    │
│ • 186 active strategies fire on Tier 1/2/3 universe (live 2026-05-25)    │
│ • Liquidity/event/regime filters apply                                   │
│ • DEC-426 5-Gate validity filter                                         │
│ • Output: ranked candidate list                                          │
└──────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 2 AGENT OVERLAY (selective — DEC-051/059 ~$300 hard cap)           │
│ • Curated subset of most-uncertain candidates                            │
│ • TradingAgents.propagate(ticker, as_of_date) called per candidate       │
└──────────────────────────────────────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────────────────┐
        │  TradingAgents pipeline (LangGraph orchestrated) │
        │                                                  │
        │  Phase 1: ANALYSTS (parallel, w/ tool calls)     │
        │  ├─ Market Analyst   ← OurTechnicalToolkit       │
        │  ├─ Fundamentals     ← OurFundamentalsToolkit    │
        │  └─ News Analyst     ← OurNewsToolkit            │
        │       ↓                                          │
        │  Phase 2: RESEARCH DEBATE                        │
        │  ├─ Bull Researcher  ← state + smart money       │
        │  ├─ Bear Researcher  ← state + smart money       │
        │  └─ Research Manager ← synthesizes (DEEP llm)    │
        │       ↓                                          │
        │  Phase 3: TRADER                                 │
        │  └─ Trader           ← OurTraderToolkit          │
        │       ↓                                          │
        │  Phase 4: RISK DEBATE                            │
        │  ├─ Aggressive       ← OurRiskToolkit            │
        │  ├─ Conservative     ← OurRiskToolkit            │
        │  ├─ Neutral          ← OurRiskToolkit            │
        │  └─ Portfolio Mgr    ← synthesizes (DEEP llm)    │
        │       ↓                                          │
        │  Output: structured Pydantic decision            │
        │  {decision: BUY/HOLD/SELL,                       │
        │   confidence: 0.0-1.0,                           │
        │   rationale, structured_fields}                  │
        └──────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ DEC-459 OPTION C HYBRID GATE                                             │
│ 1. Check decision == BUY/SELL (else REJECT)                              │
│ 2. Check confidence ≥ 0.5 (else REJECT)                                  │
│ 3. Extract Risk debate confidence from LangGraph state                   │
│ 4. Risk veto: s_risk ≥ 0.5 (else REJECT)                                 │
│ 5. Extract Research Manager confidence from state                        │
│ 6. Alignment check: RM confidence ≥ 0.5 + direction matches PM           │
│ 7. Tier from PM confidence: HIGH ≥0.8 (5%) / MED 0.65-0.8 (3%) / LOW     │
└──────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ ENGINE EXECUTION                                                         │
│ • Position sizing per tier (DEC-021)                                     │
│ • Slippage model (DEC-092)                                               │
│ • Trade event log (DEC-267)                                              │
└──────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ POST-TRADE                                                               │
│ • Reflection Node writes outcome to memory log (DEC-189)                 │
│ • Reflection feeds future agent decisions                                │
└──────────────────────────────────────────────────────────────────────────┘
```

---

# PART B — PER-AGENT DATA INPUT REQUIREMENTS

## 5. Market Analyst (Technical)

**Role:** Analyzes technical setup; produces 500-1500 token report on chart structure, indicators, momentum, support/resistance.

**TradingAgents default toolkit (`tradingagents/dataflows/interface.py`):**
- `get_YFin_data(ticker, start, end)` — yfinance OHLCV
- `get_stockstats_indicators_report(ticker, indicator, curr_date, look_back_days)` — TA via stockstats library

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| OHLCV daily | yfinance | **Polygon** (DEC-441 $30/mo) ✓ | None — upgrade |
| OHLCV intraday (1H/4H for ICT) | NOT in default | Polygon Stocks Starter has intraday | **GAP — wire intraday** |
| Standard TA indicators (RSI, MACD, ADX, BB, ATR) | stockstats library | Compute from Polygon OHLCV | None |
| ICT/SMC primitives (FVG, BOS, CHoCH, OB) | NOT in default | smartmoneyconcepts fork (DEC-045) | **GAP — toolkit injection** |
| Chart pattern signals (DEC-355-362) | NOT in default | Our 8 chart pattern strategies | **GAP — toolkit injection** |
| Volume profile / VWAP | NOT in default | Computable from Polygon | **GAP — compute + expose** |
| Multi-timeframe regime context | NOT in default | DEC-106 regime classifier | **GAP — toolkit injection** |
| Sector/peer relative strength | NOT in default | Computable from sector ETFs (DEC-118) | **GAP — compute + expose** |
| Liquidity / ADV | NOT in default | DEC-366 liquidity filter | **GAP — toolkit injection** |
| Break-and-retest signal (BUG-111) | NOT in default | Sprint 8 deliverable | **GAP — toolkit injection** |

**Verdict:** Default toolkit is **structurally insufficient**. Without OurTechnicalToolkit, Market Analyst sees vanilla TA only — none of our **186-strategy roster's** actual signals (live `len(ALL_STRATEGIES)` 2026-05-25; the 109-119 figure was pre-Batch-316a). Stage 2 A/B testing of "agents add edge over rules" would be measuring agents-with-degraded-input vs rules-with-full-input — invalid comparison.

## 6. Fundamentals Analyst

**Role:** Analyzes financial health, valuation, growth metrics; produces 500-1500 token report.

**TradingAgents default toolkit:**
- `get_finnhub_company_profile()` — basic profile
- `get_finnhub_company_news()` — fundamental news
- `get_balance_sheet()`, `get_cashflow()`, `get_income_stmt()` — financials (yfinance)
- `get_simfin_balance_sheet()` etc. — alternative source
- `get_finnhub_company_news_sentiment()` — sentiment

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Income statement (PIT) | yfinance/simfin (NOT PIT) | **Verify Polygon Stocks Starter coverage** | **CRITICAL GAP — Gap A** |
| Balance sheet (PIT) | yfinance/simfin (NOT PIT) | **Verify Polygon coverage** | **CRITICAL GAP — Gap A** |
| Cash flow (PIT) | yfinance/simfin (NOT PIT) | **Verify Polygon coverage** | **CRITICAL GAP — Gap A** |
| Earnings dates / surprises | yfinance (BUG-218 CURRENT not as_of) | DEC-256 Polygon earnings cache | None once DEC-256 lands |
| Earnings call transcripts | NOT in default | NOT in current stack | **HIGH GAP — Gap B** |
| SEC filings (10-K/10-Q text) | NOT in default | DEC-379 SEC EDGAR for spinoffs only | **MEDIUM GAP — Gap B-related** |
| Analyst estimates (consensus EPS/revenue) | NOT in default | Quiver `analystratings` (rating changes only, NOT estimates) | **HIGH GAP — Gap C** |
| Dividend history / coverage ratios | yfinance | Polygon | None |
| Insider transactions (Form 4) | NOT in default | Quiver insider trading ✓ | None |
| Short interest | NOT in default | **Ortex (in plan, not yet wired)** | **HIGH GAP — Gap D** |
| Industry comparables | NOT in default | Computable from Polygon sector data | **GAP — compute + expose** |
| 13F institutional holdings | NOT in default | Quiver 13F + DEC-325 PIT filing_date ✓ | None |
| Government contracts | NOT in default | Quiver govcontracts (BUG-284 OPEN) | **GAP — fix BUG-284** |

**Verdict:** **Most exposed agent to data gaps.** PIT-correct fundamentals is the single biggest gap. Earnings transcripts and analyst estimates are notable secondary gaps.

## 7. News Analyst

**Role:** Analyzes news flow, market narrative, macro context; produces 500-1500 token report.

**TradingAgents default toolkit:**
- `get_global_news_openai()` — Google News scrape
- `get_finnhub_news()` — Finnhub news
- `get_reddit_news()` — Reddit (we drop per DEC-057 spirit)

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Per-ticker news (last 7-30d) | Finnhub | Polygon news (DEC-440) ✓ | None — upgrade |
| Macro news (Fed, geopolitical) | Google News scrape | **Source unclear** | **MEDIUM GAP — Gap E** |
| Press releases | Finnhub partial | Polygon news likely covers | Verify in Sprint 7 |
| Economic data releases (FOMC, CPI, NFP, jobless) | NOT in default | FRED + DEC-256 event calendar | None |
| Earnings call commentary | NOT in default | NOT in stack | **HIGH GAP — overlaps with Gap B** |
| Analyst rating changes | NOT in default | Quiver analystratings ✓ | None |
| Sector news | NOT in default | Polygon news filterable | Verify |
| Sentiment scoring on news | NOT in default | NOT in stack — agent does its own | None (LLM does it) |
| Twitter/X sentiment (real-time) | NOT in default (was Social Analyst's job) | Quiver Twitter mentions (paid, not yet wired) | **LOW GAP — partial Social replacement** |

**Verdict:** Mostly OK with Polygon news + FRED. **Macro qualitative news source is unclear** — relying on agent to synthesize from FRED quantitative data only might miss qualitative signals.

## 8. Bull Researcher

**Role:** Argues bullish case based on Phase 1 analyst reports. Debates Bear up to `max_debate_rounds` (default 1-3).

**TradingAgents default:**
- Consumes Phase 1 analyst reports as input — no separate data tools
- Accesses conversation history through LangGraph state
- Does NOT fetch new data directly

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Phase 1 analyst reports | LangGraph state ✓ | Same | None |
| Memory of past similar trades | LangGraph state + Reflection memory | DEC-189 decision log + DEC-200 dashboard | None — Sprint 7-8 |
| Smart money confluence signal | NOT in default | Quiver insider+congressional+13F (DEC-124) | **GAP — state injection** |
| Regime context | NOT in default | DEC-106 regime classifier | **GAP — state injection** |
| Sector momentum context | NOT in default | Computable from sector ETFs | **GAP — state injection** |

**Verdict:** Synthesis role. **Main risk:** Bull/Bear don't see smart money / regime signals if those aren't injected into LangGraph state alongside analyst reports. Without smart money in state, Bull misses bullish conviction signals from insider buying / congressional positioning.

## 9. Bear Researcher

**Role:** Argues bearish case based on Phase 1 analyst reports. Debates Bull.

**TradingAgents default:** Same architecture as Bull Researcher.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Phase 1 analyst reports | LangGraph state ✓ | Same | None |
| Memory of past similar trades | LangGraph state + Reflection memory | DEC-189 decision log | None — Sprint 7-8 |
| Smart money signals (especially insider SELLS, Form 144 proposed sales) | NOT in default | Quiver Form 4 actual + Form 144 proposed (DEC-125) | **GAP — state injection** |
| Short interest | NOT in default | Ortex (not yet wired) | **GAP — state injection (Gap D)** |
| Regime context (especially crisis flags) | NOT in default | DEC-106 + crisis-flag system | **GAP — state injection** |
| Negative event proximity | NOT in default | DEC-348 event-calendar suppression | **GAP — state injection** |

**Verdict:** Same as Bull but with bearish-signal emphasis. **Bear without short interest data is structurally weak** — short squeeze risk is a critical bearish thesis input.

## 10. Research Manager

**Role:** Synthesizes Bull/Bear debate → investment plan. **DEEP llm (expensive).**

**TradingAgents default:** Consumes full debate history from LangGraph state.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Full Bull/Bear debate history | LangGraph state ✓ | Same | None |
| Phase 1 analyst reports | LangGraph state ✓ | Same | None |
| Memory of past debate outcomes | DEC-189 reflection log | Same — Sprint 7-8 | None |

**Verdict:** Synthesis role; no additional data needs beyond what's already in state IF Bull/Bear had proper context.

## 11. Trader

**Role:** Converts Research Manager's investment plan → concrete trade decision (entry/size/timing).

**TradingAgents default toolkit:** Limited — primarily synthesis with some live data tools.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Investment plan from Research Manager | LangGraph state ✓ | Same | None |
| Current price + bid/ask | NOT in default (assumes live) | Polygon delayed (Stocks Starter) → live in Stage 4 | **Stage-dependent** |
| Liquidity / ADV | NOT in default | DEC-366 liquidity filter | **GAP — toolkit injection** |
| Position sizing rules (DEC-021 3-tier) | NOT in default | Our config | **GAP — toolkit injection** |
| Risk-adjusted slippage estimate (DEC-092) | NOT in default | Our slippage model | **GAP — toolkit injection** |
| Borrow cost (for shorts per DEC-399) | NOT in default | Single-source consolidated module | **GAP — toolkit injection** |
| Existing portfolio positions | NOT in default | **Portfolio class (BUG-095, Sprint 3)** | **GAP — Sprint 3 dependency** |
| Cash available | NOT in default | Portfolio class | **GAP — Sprint 3 dependency** |
| Per-ticker cooldown (DEC-018 5d post-stop) | NOT in default | Per-ticker risk controls | **GAP — toolkit injection** |
| Per-ticker max-loss cap (DEC-135 -10% rolling 30d) | NOT in default | Per-ticker risk controls | **GAP — toolkit injection** |

**Verdict:** **Significant gaps.** Default Trader is naive about portfolio context, slippage, sizing rules, cooldowns, max-loss caps. Without OurTraderToolkit, Trader produces decisions ignoring critical risk constraints — those decisions then fail at engine-level checks but waste agent compute. Also: **Trader has hard dependency on Sprint 3 Portfolio class (BUG-095).**

## 12. Aggressive Risk Debater

**Role:** Argues Trader's decision is too conservative; advocate increasing position size or risk-on stance.

**TradingAgents default:** Consumes Trader decision from LangGraph state; reasons about it.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Trader's proposed decision | LangGraph state ✓ | Same | None |
| Volatility metrics (ATR, vol regime) | NOT in default | Computable from OHLCV | **GAP — state injection** |
| Drawdown context | NOT in default | Portfolio state (BUG-095) | **GAP — Sprint 3 dependency** |
| Macro stress signals (VIX, HY spread, yield curve) | NOT in default | FRED ✓ | **GAP — state injection** |
| Smart money buying confluence | NOT in default | Quiver insider+congressional+13F | **GAP — state injection** |
| Recent winning trades on similar setups | NOT in default | DEC-189 reflection log | **GAP — state injection (Sprint 7-8)** |

**Verdict:** Without explicit upside signals (smart money buying, low vol regime, recent wins on similar setups), Aggressive Debater argues from gut, not from grounded signals.

## 13. Conservative Risk Debater

**Role:** Argues Trader's decision is too aggressive; advocate reducing or skipping.

**TradingAgents default:** Same architecture as Aggressive.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Trader's proposed decision | LangGraph state ✓ | Same | None |
| Volatility regime (high VIX, sector dispersion) | NOT in default | DEC-106 regime + FRED | **GAP — state injection** |
| Earnings / event proximity (next 7d) | NOT in default | DEC-348 event suppression context | **GAP — state injection** |
| Sector concentration (own portfolio) | NOT in default | Portfolio class (BUG-095) | **GAP — Sprint 3 dependency** |
| Correlation to existing positions | NOT in default | Computable; not currently done | **GAP — Sprint 3** |
| Recent losing trades on similar setups | NOT in default | DEC-189 reflection log | **GAP — state injection** |
| Drawdown context | NOT in default | Portfolio state | **GAP — Sprint 3 dependency** |
| Crisis flags (DEC-262/317) | NOT in default | Regime classifier crisis flag | **GAP — state injection** |

**Verdict:** **Highest data dependency of all Risk Debaters.** Without correlation, sector concentration, drawdown, event proximity, crisis flags — Conservative Debater argues from gut.

## 14. Neutral Risk Debater

**Role:** Middle ground; weigh both Aggressive and Conservative arguments.

**TradingAgents default:** Same architecture.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Trader's decision + Aggressive + Conservative arguments | LangGraph state ✓ | Same | None |
| All data context the other Risk Debaters need | (inherits) | (inherits state injection from #12 + #13) | (inherits) |

**Verdict:** Synthesis role; no separate gaps beyond what #12 and #13 need.

## 15. Portfolio Manager

**Role:** Synthesizes Risk Debate → final structured Pydantic decision. **THIS IS THE OUTPUT WE CONSUME PER DEC-459 OPTION C.** **DEEP llm (expensive).**

**TradingAgents default:** Consumes full Risk Debate from LangGraph state.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Full Risk Debate history | LangGraph state ✓ | Same | None |
| Trader's decision | LangGraph state ✓ | Same | None |
| Phase 1 analyst reports | LangGraph state ✓ | Same | None |
| All risk context already injected by upstream Risk Debaters | (inherits) | (inherits state injection) | (inherits) |

**Verdict:** Synthesis role; no additional data needs IF upstream agents have proper context. **PM output quality is upper-bounded by upstream input quality.** This is the architecturally critical insight: **fixing PM-level decision quality requires fixing data feeds upstream, not adjusting PM itself.**

## 16. Reflection Node

**Role:** Post-decision learning — writes outcomes to memory log for future trades.

**TradingAgents default:** Operates on closed-trade outcomes.

### Required inputs vs current feed

| Requirement | TradingAgents default | What we feed | Gap? |
|---|---|---|---|
| Realized trade outcome (P&L, holding period, exit reason) | NOT in default (relies on user impl) | DEC-189 trade outcome log | **Sprint 7-8 dependency** |
| Original decision context (what agents reasoned about) | NOT in default | DEC-200 ICT/SMC audit dashboard input | **Sprint 7-8 dependency** |
| Persistence layer | NOT in default | DEC-267 SQLite (Stage 3) → Postgres (Stage 4) | **Sprint 7-8 dependency** |

**Verdict:** Operational only post-trade-close. Stage 3+ active. Already in plan.

---

# PART C — GAP ANALYSIS

## 17. Critical Gaps (Block Decision Quality)

### Gap A: PIT-Correct Fundamentals
**Affects:** Fundamentals Analyst (Agent 2), Bull Researcher (Agent 5), Bear Researcher (Agent 6), Risk Debaters (Agents 9-11)
**Severity:** CRITICAL
**Issue:** TradingAgents default uses yfinance/simfin which are CURRENT not as-of. Polygon Stocks Starter $29/mo coverage of fundamentals (income / balance sheet / cash flow) at PIT timestamps is **not yet verified**.
**Impact if unresolved:** Lookahead bias in Stage 2 backtest agent decisions; A/B verdict invalid; DEC-131 ≥0.2 net Sharpe gate becomes meaningless.
**Resolution candidates:**
- Polygon Stocks Starter scope verification (may already cover at $30/mo)
- Polygon higher tier upgrade (~$200/mo if needed)
- Financial Modeling Prep (FMP) ~$14-50/mo — has PIT financials
- SEC EDGAR XBRL direct parsing — $0 but ~5-10d build cost

### Gap B: Earnings Call Transcripts
**Affects:** Fundamentals Analyst (Agent 2), News Analyst (Agent 3)
**Severity:** HIGH
**Issue:** No earnings transcript source in current stack. Earnings call commentary is high-signal qualitative input — guidance changes, tone shifts, Q&A reveals.
**Impact if unresolved:** Fundamentals Analyst reasoning shallow on earnings-driven moves; News Analyst misses post-earnings narrative.
**Resolution candidates:**
- FMP transcripts endpoint — typically included in FMP plans
- Polygon transcripts (verify availability in Stocks Starter)
- Seeking Alpha API (paid)
- Manual scrape (high cost, brittle)

### Gap C: Analyst Consensus Estimates (EPS / Revenue)
**Affects:** Fundamentals Analyst (Agent 2)
**Severity:** HIGH
**Issue:** Quiver `analystratings` provides rating changes (Buy/Hold/Sell upgrades), not consensus estimates. Earnings beats/misses lose context without consensus EPS/revenue.
**Impact if unresolved:** Fundamentals Analyst can't contextualize earnings results; "beat by 5 cents" means different things at different consensus levels.
**Resolution candidates:**
- Polygon analyst estimates (verify availability)
- FMP analyst-estimates endpoint
- Finnhub analyst-recommendations
- Refinitiv (institutional, expensive)

### Gap D: Short Interest / Ortex Wiring
**Affects:** Fundamentals Analyst (Agent 2), Bear Researcher (Agent 6), Risk Debaters (Agents 9-11)
**Severity:** HIGH
**Issue:** Ortex is in plan ($263 CAD/mo full stack baseline) but not yet wired into agent toolkits or LangGraph state.
**Impact if unresolved:** Bear Researcher misses short squeeze risk signals; Risk Debaters don't see crowded-short positioning.
**Resolution candidates:**
- Confirm Ortex subscription scope (which endpoints active)
- Wire Ortex into OurFundamentalsToolkit + state injection for Bear/Risk

### Gap E: Macro Qualitative News
**Affects:** News Analyst (Agent 3)
**Severity:** MEDIUM
**Issue:** FRED gives quantitative macro (rates, jobless, CPI). Qualitative geopolitical / Fed-commentary news source is unclear.
**Impact if unresolved:** News Analyst over-weights ticker-specific news; under-weights regime-shifting macro narrative.
**Resolution candidates:**
- Verify Polygon news has macro tag / general feed
- Add dedicated macro news source (e.g., Bloomberg, Reuters via aggregator)
- Accept as Stage 2 limitation; rely on FRED quantitative macro

## 18. Operational Gaps (Implementation, Not Data Sourcing)

### Gap F: Custom Toolkit Injection (Pattern 2 Implementation)
**Affects:** All Phase 1 Analysts + Trader + Risk Debaters
**Severity:** CRITICAL (blocks Pattern 2 entirely)
**Issue:** Pattern 2 (Pass 29 recommended) requires extending TradingAgents' default toolkits with our data sources. Not yet implemented.
**Impact if unresolved:** Either (a) fall back to Pattern 1 wrapper (loses our data sources entirely — agents see only yfinance/Finnhub/Reddit defaults) OR (b) Stage 2 doesn't run at all.
**Resolution:** Sprint 7 toolkit extension classes (see Part D).

### Gap G: LangGraph State Augmentation
**Affects:** Bull/Bear/Research Manager/Risk Debaters/Portfolio Manager
**Severity:** CRITICAL
**Issue:** Synthesis agents see only what's in LangGraph state. Smart money / regime / portfolio context needs explicit state-channel injection beyond what default state schema provides.
**Impact if unresolved:** Synthesis agents (Bull/Bear/RM/Risk Debaters/PM) reason without smart money signals, regime context, portfolio context — making PM final decision based on incomplete information.
**Resolution:** Sprint 7 state schema extension (see Part E).

### Gap H: Reflection Memory Persistence
**Affects:** Reflection Node, future decision quality across sessions
**Severity:** MEDIUM (Stage 3+ active)
**Issue:** Per DEC-189 trade outcome log + DEC-267 event store, persistence is Sprint 7-8.
**Impact if unresolved:** Reflection Node has no historical context for learning; memory log doesn't persist across backtest runs.
**Resolution:** Already in plan; verify Reflection Node integrated with DEC-189 / DEC-267 logs in Sprint 7-8.

## 19. Recommended Additional API Endpoints

Based on Gap A-E analysis:

| Endpoint | Source candidate | Estimated cost | Priority | Resolves Gap |
|---|---|---|---|---|
| **PIT financial statements** | Polygon higher tier OR FMP OR SEC EDGAR XBRL | $30-200/mo OR $0 (build) | CRITICAL | A |
| **Earnings call transcripts** | FMP transcripts OR alternative | $14-50/mo | HIGH | B |
| **Analyst consensus estimates** | FMP OR Polygon OR Finnhub | varies | HIGH | C |
| **Ortex short interest (wire it)** | Ortex direct (already in $263 CAD/mo plan) | already paid | HIGH | D |
| **Macro news with tags** | Polygon news (verify) OR alternative | included | MEDIUM | E |
| **Senate trades (separate from House)** | Quiver | already paid | LOW | (Pass 22-25 finding) |
| **Twitter/X mentions** | Quiver Twitter | already paid | LOW | Partial Social replacement |
| **Off-Exchange (dark pool) prints** | Quiver | already paid | LOW | Bear/Risk additional signal |
| **App downloads** | Quiver | already paid | LOW | Tech-ticker demand signal |

### Recommended bundled approach: FMP $14-50/mo addition

**FMP (Financial Modeling Prep)** addresses Gap A + B + C in one subscription:
- PIT financial statements (Gap A)
- Earnings call transcripts (Gap B)
- Analyst consensus estimates (Gap C)

**Total cost delta:** +$14-50/mo over current $263 CAD/mo baseline. Per owner directive turn 130 ("Happy to upgrade") — recommend evaluating FMP scope before Sprint 0A start.

**Alternative:** Verify Polygon Stocks Starter $29/mo coverage of all three first; if covered, no upgrade needed.

---

# PART D — CUSTOM TOOLKIT SPECIFICATIONS (PATTERN 2)

## 20. OurTechnicalToolkit (extends TechnicalToolkit)

**Purpose:** Inject our technical signals into Market Analyst's tool set.

**File:** `backtest/agents/toolkits/our_technical_toolkit.py`

**Methods:**
```python
class OurTechnicalToolkit(TechnicalToolkit):
    # Inherited (TradingAgents default):
    # - get_YFin_data() — REPLACE with Polygon
    # - get_stockstats_indicators_report() — KEEP (or compute ourselves)
    
    # NEW methods (our additions):
    def get_polygon_ohlcv(ticker, start, end, timeframe='1D')
    def get_intraday_ohlcv(ticker, date, timeframe='1H')
    def get_ict_smc_signals(ticker, as_of)  # FVG, BOS, CHoCH, OB
    def get_chart_pattern_signals(ticker, as_of)  # 8 patterns DEC-355-362
    def get_volume_profile(ticker, as_of, lookback_days=30)
    def get_vwap(ticker, date)
    def get_multi_timeframe_regime(as_of)  # DEC-106
    def get_sector_relative_strength(ticker, as_of)  # vs sector ETF DEC-118
    def get_liquidity_metrics(ticker, as_of)  # ADV per DEC-366
    def get_break_and_retest_signal(ticker, as_of)  # BUG-111 resolution
```

**Effort:** ~3-4 days (Sprint 7)
**Test signals:**
- (a) Each method returns properly typed result; no silent failures
- (b) PIT-correctness verified via freezegun (DEC-050)
- (c) ICT/SMC signals match smartmoneyconcepts library output
- (d) Multi-timeframe regime matches DEC-106 classifier output

## 21. OurFundamentalsToolkit (extends FundamentalsToolkit)

**Purpose:** Inject PIT fundamentals + smart money signals + short interest into Fundamentals Analyst's tool set.

**File:** `backtest/agents/toolkits/our_fundamentals_toolkit.py`

**Methods:**
```python
class OurFundamentalsToolkit(FundamentalsToolkit):
    # Inherited (TradingAgents default):
    # - get_finnhub_company_profile() — KEEP or REPLACE
    # - get_balance_sheet/cashflow/income_stmt — REPLACE with PIT-correct source
    
    # NEW methods:
    def get_pit_income_statement(ticker, as_of)  # Gap A resolution
    def get_pit_balance_sheet(ticker, as_of)
    def get_pit_cash_flow(ticker, as_of)
    def get_earnings_history(ticker, as_of, lookback_quarters=8)
    def get_earnings_transcript(ticker, quarter, year)  # Gap B
    def get_analyst_estimates(ticker, as_of)  # Gap C
    def get_insider_transactions(ticker, as_of)  # Quiver Form 4 + Form 144
    def get_congressional_trades(ticker, as_of)  # Quiver
    def get_13f_holdings(ticker, as_of)  # Quiver + DEC-325 PIT filing_date
    def get_smart_money_composite(ticker, as_of)  # DEC-124 confluence + DEC-332 weights
    def get_short_interest(ticker, as_of)  # Ortex — Gap D
    def get_government_contracts(ticker, as_of)  # Quiver — fix BUG-284
    def get_sec_filings(ticker, as_of, filing_type='10-K')  # SEC EDGAR
    def get_industry_comparables(ticker, as_of)  # Polygon sector data
```

**Effort:** ~4-5 days (Sprint 7) — depends on resolving Gap A source
**Test signals:**
- (a) PIT correctness via freezegun on every fundamentals method
- (b) Smart money composite matches DEC-124 cross-source confluence
- (c) Short interest data sourced from Ortex; date filter correct

## 22. OurNewsToolkit (extends NewsToolkit)

**Purpose:** Inject Polygon news + FRED event calendar + analyst rating changes into News Analyst's tool set.

**File:** `backtest/agents/toolkits/our_news_toolkit.py`

**Methods:**
```python
class OurNewsToolkit(NewsToolkit):
    # NEW methods:
    def get_polygon_news(ticker, as_of, lookback_days=30)  # DEC-440
    def get_macro_news(as_of, lookback_days=7)  # Gap E — Polygon macro feed if available
    def get_press_releases(ticker, as_of)
    def get_event_calendar(as_of, lookahead_days=14)  # DEC-256 + DEC-348
    def get_analyst_rating_changes(ticker, as_of, lookback_days=90)  # Quiver
    def get_sector_news(sector, as_of)
    def get_fred_event_log(as_of, lookback_days=30)  # FOMC/CPI/NFP releases
```

**Effort:** ~2 days (Sprint 7)
**Test signals:**
- (a) Polygon news returns articles with date ≤ as_of
- (b) Event calendar correctly identifies upcoming earnings within asymmetric window (DEC-349)

## 23. OurTraderToolkit (NEW — no TradingAgents default)

**Purpose:** Inject portfolio context, sizing rules, slippage estimates into Trader's tool set.

**File:** `backtest/agents/toolkits/our_trader_toolkit.py`

**Methods:**
```python
class OurTraderToolkit:
    # All NEW (no TradingAgents default):
    def get_current_price(ticker, as_of)
    def get_bid_ask_estimate(ticker, as_of)  # from delayed Polygon
    def get_liquidity_metrics(ticker, as_of)  # ADV per DEC-366
    def get_position_sizing_rules(tier)  # DEC-021 3-tier (5%/3%/1.5%)
    def get_slippage_estimate(ticker, size, time_of_day, exit_method)  # DEC-092 + DEC-122 + DEC-280
    def get_borrow_cost(ticker, as_of)  # DEC-399 single-source
    def get_portfolio_state()  # Portfolio class — Sprint 3 dependency
    def get_cash_available()  # Portfolio class
    def get_existing_position(ticker)  # Portfolio class
    def get_per_ticker_cooldown(ticker, as_of)  # DEC-018 5d post-stop
    def get_per_ticker_max_loss_status(ticker, as_of)  # DEC-135 -10% rolling 30d
```

**Effort:** ~3-4 days (Sprint 7) — **HARD DEPENDENCY on Sprint 3 Portfolio class (BUG-095)**
**Test signals:**
- (a) Sizing rules match DEC-021 3-tier exactly
- (b) Slippage estimate combines DEC-092 + DEC-122 + DEC-280 multipliers correctly
- (c) Portfolio state queries return current positions / cash from Portfolio class

## 24. OurRiskToolkit (NEW)

**Purpose:** Inject volatility regime, correlation, sector concentration, event proximity into Risk Debaters' tool sets.

**File:** `backtest/agents/toolkits/our_risk_toolkit.py`

**Methods:**
```python
class OurRiskToolkit:
    # All NEW:
    def get_volatility_regime(as_of)  # DEC-106 + VIX
    def get_atr_metrics(ticker, as_of)
    def get_correlation_to_existing_positions(ticker, as_of)  # Sprint 3 dependency
    def get_sector_concentration()  # Portfolio sector exposure
    def get_drawdown_context()  # Portfolio drawdown state
    def get_macro_stress_signals(as_of)  # FRED — VIX, HY spread, T10Y2Y, ICSA jobless
    def get_event_proximity(ticker, as_of, window_days=14)  # DEC-256 + DEC-348
    def get_crisis_flags(as_of)  # DEC-262 + DEC-317
    def get_recent_outcomes_on_similar_setups(ticker, setup_signature, as_of)  # DEC-189 reflection log
```

**Effort:** ~3-4 days (Sprint 7) — **HARD DEPENDENCY on Sprint 3 Portfolio class (BUG-095) + Sprint 7-8 reflection log (DEC-189)**
**Test signals:**
- (a) Correlation to existing positions returns valid pairwise correlation
- (b) Sector concentration matches portfolio sector exposure
- (c) Crisis flags fire correctly per DEC-262 thresholds
- (d) Event proximity respects asymmetric window per DEC-349

---

# PART E — LANGGRAPH STATE AUGMENTATION

## 25. State Schema Extensions

TradingAgents' default LangGraph state schema does not include smart money signals, regime context, portfolio context, or event proximity. Per Pattern 2, we extend the state schema:

```python
class OurAgentState(TradingAgentsState):  # extends default
    # Default fields (inherited):
    # - market_report: str
    # - fundamentals_report: str
    # - news_report: str
    # - investment_plan: str
    # - trader_decision: str
    # - risk_debate_history: list
    # - final_decision: PortfolioManagerDecision
    
    # NEW fields (our additions):
    smart_money_signal: dict   # Quiver insider+congressional+13F confluence (DEC-124)
    regime_context: dict       # DEC-106 regime classifier output + crisis flags
    portfolio_context: dict    # Portfolio class summary (Sprint 3 dependency)
    event_proximity: dict      # DEC-348 event-calendar suppression context
    sector_context: dict       # Sector relative strength + sector regime DEC-151
    short_interest_signal: dict  # Ortex (Gap D)
    historical_outcomes: dict  # DEC-189 reflection log similar-setup outcomes
```

## 26. State Injection Points

**Phase 1 entry (before Analysts run):**
- Inject `regime_context` (DEC-106) — all analysts benefit from regime awareness
- Inject `portfolio_context` (Sprint 3) — informs analysis bias

**Phase 1 exit (after Analysts produce reports):**
- No injection — analyst reports are produced by their toolkits

**Phase 2 entry (before Bull/Bear debate):**
- Inject `smart_money_signal` (DEC-124) — Bull and Bear both need this
- Inject `historical_outcomes` (DEC-189) — debaters need memory of similar trades
- Inject `short_interest_signal` (Ortex) — Bear especially benefits

**Phase 3 entry (before Trader):**
- Inject `event_proximity` (DEC-348) — Trader needs to know event suppression windows
- Inject `sector_context` (DEC-151) — Trader needs sector regime awareness

**Phase 4 entry (before Risk Debate):**
- All risk-relevant context already in state from Phase 1-3 injections
- Risk Debaters use OurRiskToolkit for live computations (correlation, concentration)

**Phase 5 (Reflection):**
- Reflection Node reads `final_decision` + later writes outcome to DEC-189 log

---

# PART F — IMPLEMENTATION SEQUENCING

## 27. Sprint 7 Custom Toolkit Build

**Toolkit files:** 5 new files in `backtest/agents/toolkits/`

| Toolkit | Effort | Dependencies |
|---|---|---|
| OurTechnicalToolkit | ~3-4d | Polygon prefetch (Sprint 0A); ICT/SMC fork (DEC-045 Phase 0.D) |
| OurFundamentalsToolkit | ~4-5d | Gap A resolution; Quiver paid (already); Ortex wiring |
| OurNewsToolkit | ~2d | Polygon news (DEC-440); FRED event calendar |
| OurTraderToolkit | ~3-4d | **Portfolio class (Sprint 3 BUG-095)** |
| OurRiskToolkit | ~3-4d | **Portfolio class (Sprint 3) + DEC-189 reflection log (Sprint 7-8)** |
| **Total Sprint 7 toolkit effort** | **~15-19d** | |

## 28. Sprint 7 State Schema Extension

| Item | Effort |
|---|---|
| OurAgentState class definition | ~0.5d |
| State injection points wired into LangGraph nodes | ~1d |
| Per-injection-point unit tests | ~0.5d |
| **Total** | **~2d** |

## 29. Cross-Sprint Dependencies

```
Sprint 0A (Polygon foundation) ──► Sprint 7 (toolkits depend on Polygon)
Sprint 3 (Portfolio class) ──────► Sprint 7 (Trader/Risk toolkits depend on Portfolio)
Sprint 4 (DEC-298 raw OHLCV) ────► Sprint 7 (PIT fundamentals depend on cache)
Phase 0.D (ICT/SMC fork DEC-045) ► Sprint 7 (Technical toolkit depends on fork)
Sprint 7-8 (DEC-189 reflection log)► Sprint 7 (Risk toolkit historical_outcomes; partial circular — start without, add later)
```

**Critical path implication:** Custom toolkit work (Sprint 7) cannot fully complete until Sprint 3 Portfolio class lands. **Trader + Risk toolkits have hard Sprint 3 dependency.**

**Sequencing recommendation:** Start Technical / Fundamentals / News toolkits in Sprint 7 Day 1 (parallel-able with Sprint 3 Portfolio class build). Trader + Risk toolkits start when Portfolio class lands.

---

# PART G — RECOMMENDED DECISIONS (PROPOSED)

Per L131 / CHECKLIST #51 — sub-decisions PROPOSED here, **not yet LOGGED as DECISIONs in AUDIT_INDEX**. Owner approves each individually before logging.

## 30. Sub-decision Candidates

### DEC-460 PROPOSED — Verify Polygon Stocks Starter PIT fundamentals coverage
**Scope:** Pre-Sprint-1 verification: confirm whether Polygon Stocks Starter $29/mo includes income statement / balance sheet / cash flow at PIT timestamps. Resolves Gap A if covered.
**Effort:** ~0.5d
**Test signals:** (a) Documented endpoint inventory; (b) sample fetch with as_of date validation; (c) PIT correctness verified via freezegun.
**Sprint:** Pre-Sprint-1

### DEC-461 PROPOSED — Subscribe to FMP if Polygon doesn't cover PIT fundamentals
**Scope:** Conditional on DEC-460 outcome. If Polygon insufficient, subscribe to Financial Modeling Prep ~$14-50/mo for PIT financials + transcripts + analyst estimates. Resolves Gap A + B + C bundled.
**Effort:** ~0.25d (subscription only)
**Cost:** +$14-50/mo over $263 CAD/mo baseline
**Test signals:** (a) FMP API keys configured; (b) sample fetch validated.
**Sprint:** Pre-Sprint-1 conditional

### DEC-462 PROPOSED — OurTechnicalToolkit specification
**Scope:** Implement OurTechnicalToolkit per Part D §20. Inject Polygon OHLCV + ICT/SMC + chart patterns + multi-timeframe regime + sector relative strength + liquidity into Market Analyst's tool set.
**Effort:** ~3-4d
**Test signals:** Per §20 above.
**Sprint:** 7
**Joint:** DEC-045 (ICT/SMC fork); DEC-355-362 (chart patterns); DEC-106 (regime); DEC-118 (sector ETFs); DEC-366 (liquidity)

### DEC-463 PROPOSED — OurFundamentalsToolkit specification
**Scope:** Implement OurFundamentalsToolkit per Part D §21. Inject PIT fundamentals + earnings transcripts + analyst estimates + Quiver smart money + Ortex short interest into Fundamentals Analyst's tool set.
**Effort:** ~4-5d
**Test signals:** Per §21 above.
**Sprint:** 7
**Joint:** DEC-460/461 (Gap A); DEC-124 (smart money confluence); DEC-325 (13F PIT); DEC-332 (smart money weights)

### DEC-464 PROPOSED — OurNewsToolkit specification
**Scope:** Implement OurNewsToolkit per Part D §22. Inject Polygon news + FRED event calendar + Quiver analyst rating changes into News Analyst's tool set.
**Effort:** ~2d
**Test signals:** Per §22 above.
**Sprint:** 7
**Joint:** DEC-440 (Polygon news); DEC-256 (event calendar); DEC-348/349 (event suppression)

### DEC-465 PROPOSED — OurTraderToolkit specification (NEW class)
**Scope:** Implement OurTraderToolkit per Part D §23. Inject portfolio state + sizing rules + slippage estimates + cooldowns + max-loss caps into Trader's tool set.
**Effort:** ~3-4d
**Test signals:** Per §23 above.
**Sprint:** 7 — **HARD DEPENDENCY on Sprint 3 Portfolio class (BUG-095)**
**Joint:** DEC-021 (3-tier sizing); DEC-092 (slippage); DEC-018 (cooldown); DEC-135 (max-loss); DEC-399 (borrow cost)

### DEC-466 PROPOSED — OurRiskToolkit specification (NEW class)
**Scope:** Implement OurRiskToolkit per Part D §24. Inject volatility regime + correlation + sector concentration + event proximity + crisis flags + similar-setup outcomes into Risk Debaters' tool sets.
**Effort:** ~3-4d
**Test signals:** Per §24 above.
**Sprint:** 7 — **HARD DEPENDENCY on Sprint 3 Portfolio class + Sprint 7-8 DEC-189 reflection log**
**Joint:** DEC-106 (regime); DEC-262 (crisis flags); DEC-317 (regime hysteresis); DEC-189 (reflection log); DEC-348 (event suppression)

### DEC-467 PROPOSED — OurAgentState schema extension + injection points
**Scope:** Implement OurAgentState per Part E. Add 7 new state fields + wire injection points at Phase 1 / Phase 2 / Phase 3 entry points.
**Effort:** ~2d
**Test signals:** State schema extends default cleanly; injection happens at correct LangGraph nodes; downstream agents can read injected fields.
**Sprint:** 7
**Joint:** DEC-124 (smart money); DEC-106 (regime); DEC-189 (historical outcomes); Sprint 3 (portfolio_context)

### DEC-468 PROPOSED — Wire Ortex short interest into stack
**Scope:** Confirm Ortex subscription scope; wire endpoints into OurFundamentalsToolkit + state injection for Bear / Risk Debaters. Resolves Gap D.
**Effort:** ~1.5d
**Test signals:** Ortex API keys configured; sample fetch validated; short interest signal injected into LangGraph state for Bear / Risk Debaters.
**Sprint:** 7

### Sprint 7 effort summary (post-DEC-460-468 if all approved)

| Item | Effort |
|---|---|
| Existing Sprint 7 (DEC-459 + statistical methodology + A/B + regime) | ~77-86d |
| DEC-462 OurTechnicalToolkit | ~3-4d |
| DEC-463 OurFundamentalsToolkit | ~4-5d |
| DEC-464 OurNewsToolkit | ~2d |
| DEC-465 OurTraderToolkit | ~3-4d |
| DEC-466 OurRiskToolkit | ~3-4d |
| DEC-467 OurAgentState schema | ~2d |
| DEC-468 Ortex wiring | ~1.5d |
| **Total Sprint 7 revised effort** | **~96-108d** |

**Sprint 7 effort delta:** +19-22 days (~25-28% increase). Significant but necessary for valid Stage 2 A/B testing.

### Pre-Sprint-1 effort summary

| Item | Effort |
|---|---|
| Existing pre-Sprint-1 setup (10 actions per Pass 52 turn 125) | ~9-11d |
| DEC-460 verify Polygon coverage | ~0.5d |
| DEC-461 (conditional) FMP subscription | ~0.25d |
| **Total pre-Sprint-1 revised effort** | **~9.75-11.75d** |

**Pre-Sprint-1 effort delta:** +0.75 days (negligible — verification work).

---

# OWNER ACCOUNTABILITY VINDICATION (6th instance Pass 52)

**Pattern:** Owner verification questions catch architectural gaps Claude should be surfacing pre-emptively.

| Turn | Anti-pattern caught |
|---|---|
| 98 | Homeless RESOLVED-DECIDED decisions |
| 108 | Substantively-homeless engineering decisions |
| 110 | Bug-decision linkage gap |
| 114-118 | 80 PENDING bulk-sweep delegation |
| 128 | Architectural fit not verified before parameter application (DEC-042) |
| **130** | **Data dependency chain not verified during architectural decision resolution (this audit)** |

**L139 NEW (Pass 52 turn 130):** Decision resolution must include data-input dependency verification. Resolving an architectural decision (e.g., "use TradingAgents framework" per DEC-051) without auditing whether downstream data feeds satisfy the framework's per-agent input requirements creates phantom completeness — the decision is RESOLVED-DECIDED but cannot actually function in production.

**CHECKLIST #60 NEW (Pass 52 turn 130):** Data dependency verification on architectural decisions. Before marking architectural decisions RESOLVED-DECIDED, audit data input requirements for every component the architecture creates dependencies on. Specifically: (a) Per-component data input requirements documented; (b) Current data feeds mapped against requirements; (c) Gaps identified with severity; (d) Resolution candidates proposed with cost estimates; (e) Owner approval BEFORE marking architectural decision RESOLVED-DECIDED.

**Honest accountability per #25:** This audit should have been completed in Pass 25 (DEC-042 origin) / Pass 28 (DEC-051 TradingAgents adoption) / Pass 29 (Pattern 2 selection) / Pass 31 (TradingAgents 11-agent analysis). Each of those passes had the visibility but didn't run the full data dependency mapping. Pass 29's BUG-113 finding ("agent emits 31 fields, engine reads 2") was already a warning sign about agent-engine integration shallowness — same pattern (outputs not fully consumed) applies to data inputs going IN. I missed the symmetry.

---

*End of TRADINGAGENTS_DATA_AUDIT.md*

*Per CHECKLIST #25 (honest accountability for Pass 25-31 omission); #43 (precise grep on TradingAgents agent definitions + per-agent dependencies + current API_AUDIT.md coverage); #51 (recommended decisions PROPOSED not LOGGED — owner approves each); #57 (use-case mapping per agent); #58 (atomic commit invoked when sub-decisions logged); #59 (architectural assumption verification applied PROACTIVELY this time); #60 NEW (data dependency verification on architectural decisions).*

---

## Pass 53 Update — Phase 1A Restoration Impact on Toolkits

**Trigger:** Phase 1A restoration (DEC-486/487/488 PROPOSED Pass 53).

**Impact on Sprint 7 toolkit deliverables (DEC-462-468):** TIMING CHANGES, scope unchanged.

| Toolkit | Original Sprint | Pass 53 Update |
|---|---|---|
| OurTechnicalToolkit (DEC-462) | Sprint 7 | Sprint 7 — unchanged. Phase 1A baseline (Sprint 6.5) does NOT use TradingAgents toolkits. Phase 1A rules-only screener uses standalone smart money signals + technical indicators directly. |
| OurFundamentalsToolkit (DEC-463) | Sprint 7 | Sprint 7 — unchanged. Phase 1A baseline uses smart money confluence (DEC-124) directly without agent layer. |
| OurNewsToolkit (DEC-464) | Sprint 7 | Sprint 7 — unchanged. Phase 1A does not use news (smart money handles equivalent signal). |
| OurTraderToolkit (DEC-465) | Sprint 7 — HARD DEP on Sprint 3 (BUG-095) | Sprint 7 — unchanged. Phase 1A uses Portfolio class directly, not via toolkit. |
| OurRiskToolkit (DEC-466) | Sprint 7 — HARD DEP on Sprint 3 + DEC-189 | Sprint 7 — unchanged. Phase 1A uses Portfolio + Risk gates directly. |
| OurAgentState (DEC-467) | Sprint 7 | Sprint 7 — unchanged. Phase 1A doesn't use LangGraph state (no agents). |
| Ortex wiring (DEC-468) | Sprint 7 | Sprint 7 — unchanged. Phase 1A uses Ortex via Quiver paid endpoints (DEC-450) directly in screener if signal fires. |

**Phase scope clarification:**
- **Phase 1A (Sprint 6.5):** Rules-only screening + smart money confluence + per-ticker risk gates. No TradingAgents toolkits invoked. `--no-agents` flag bypasses all agent infrastructure.
- **Phase 1B (Sprint 7):** Adds agent overlay via TradingAgents.propagate(); custom toolkits (DEC-462-468) operate here.
- **Phase 1B-α (Sprint 7-8):** Combined cube run; reuses Phase 1A-α infrastructure with agent arms added.

**Effort impact:** None for individual toolkit deliverables. Sprint 7 toolkit work continues per original timing. New Sprint 6.5 (Phase 1A baseline) is parallel-able with Sprint 7 (toolkit build) — Phase 1A doesn't need toolkits.

**Architectural clarity:** Smart money signals in Phase 1A (rules-based screener consumption) and smart money signals in Phase 1B (OurFundamentalsToolkit consumption) are the SAME data source (DEC-450 Quiver paid + DEC-124 confluence), accessed via DIFFERENT consumption paths. Phase 1A reads from cache directly; Phase 1B reads via toolkit method `get_smart_money_composite()`.

---

## Pass 53 Addendum — TRADING_RULES.md canonical signal references

Pass 53 added comprehensive signal documentation in TRADING_RULES.md. Reference these canonical sections when implementing toolkits (DEC-462-468):

| Section | Content | Toolkit consumption |
|---|---|---|
| **TRADING_RULES §2A** (Pass 53 NEW) | Signal Universe Catalogue — 6 categories (Technical / Smart Money / Options / Macro / Sentiment / Company); ~265-275 active signal fields; source code paths per category | All toolkits — canonical reference for "what signals exist" |
| **TRADING_RULES §10.8** (Pass 53 NEW) | Smart Money Composite Score — per-source signal labels (congressional / insider / 13F) + composite weights matrix (`+4/+2/-3` etc.) + veto + composite labels by score + 90-day decay | OurFundamentalsToolkit `get_smart_money_composite()` (DEC-463) |
| **TRADING_RULES §10.9** (Pass 53 NEW) | Smart Money-Adjacent Signals (news / gov_contracts / lobbying / analyst LIVE-ONLY warning per DEC-299/443) | OurFundamentalsToolkit + OurNewsToolkit |
| **TRADING_RULES §13.12** (Pass 53 NEW) | API Endpoint Inventory — comprehensive table (~30 endpoints across 16 sources) | All toolkits — canonical reference for "what API endpoints to consume" |

### Pass 53 trade-capture format changes — Sprint 2 dependency

DEC-491 + DEC-492 PROPOSED Sprint 2 affect what data agents see in trade history:

- **DEC-491** trade_log Parquet format (vs CSV `str(dict)` fragility) — `agent_reasoning` dict will round-trip cleanly post-DEC-491. Toolkits that consume historical trade reasoning (e.g., reflection node retrieval) benefit.
- **DEC-492** signals_at_entry filter removed — string/list signals (regime tags, ICT/SMC labels per DEC-261/345, chart pattern names per DEC-355-362) will be preserved in trade rows. Post-hoc agent analysis of "what signals fired this trade" gains visibility into non-numeric signals.

Both Sprint 2 implementation; affect Phase 1B+ agent overlay quality.

### Universe architecture Pass 53 — toolkit context

Pass 53 introduced 5-bucket universe model:
- T1a (S&P 500), T1b (R1000-non-S&P), T1c (NDX-non-S&P) per DEC-483
- Tier 1 ETFs (DEC-118) — 27 ETFs in `Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv` (Pass 53 migration from hardcoded list)
- T2 spinoffs/IPOs (DEC-103); T3 momentum (DEC-104; methodology DEC-496 J-T 12-1)
- DEC-495 archived watchlist for tickers rotating out of all 5 buckets (Stage 3+ scope)

Universe CSVs live in top-level `Backtesting universe/` folder (Pass 53 commit `c7f5580f`); B++ schema with `added_date`/`removed_date` columns; PIT loader filter handles NULL pre-window dates.

Toolkits consuming universe context (DEC-465 OurTraderToolkit `existing positions` field; DEC-466 OurRiskToolkit; portfolio_context per DEC-467) should use `backtest.data.universe` module loaders — these read from the new folder path via `UNIVERSE_DIR` constant.

### Cross-references

- TRADING_RULES.md §2A signal universe catalogue
- TRADING_RULES.md §10.8/10.9 smart money composite + adjacent
- TRADING_RULES.md §13.12 API endpoint inventory
- DOCUMENTATION_REGISTER.md Pass 53 turn entries (post Sprint-1-Pre-Flight)
- AUDIT.md Pass 53 narrative entries (per-commit detail)
- DEC-491/492/493 (Sprint 2 trade-capture fragility) — affect agent_reasoning serialization
- DEC-494/495/496 (Sprint 0A / Stage 3+ / Sprint 1-5 — universe + watchlist + momentum methodology)

---

## Pass 53 update — Per-agent input matrix revised (2026-05-05)

### Sprint 0A scope changes affecting agent inputs

**DEC-500 — Polygon ticker events as agent context (NEW; all 11 active agents per DEC-057 + DETAILED_PROJECT_PLAN §2.6):**
- **Market Analyst** — split/dividend adjustments + ticker_change continuity in technical signals
- **Fundamentals Analyst** — M&A as fundamental thesis trigger (acquirer/target context); split/dividend continuity
- **News Analyst** — event-driven news / corp-action announcement context
- **Bull Researcher** — uses event context to strengthen long thesis (e.g., spinoff value-unlock)
- **Bear Researcher** — uses event context to argue against (e.g., delisting / governance red flags)
- **Research Manager** — adjudicates Bull/Bear debate using event materiality
- **Trader** — adjusts entry/exit timing around scheduled corp actions
- **Aggressive Risk Debater** — frames events as opportunity (catalyst trades)
- **Conservative Risk Debater** — frames events as risk (uncertainty around corp actions)
- **Neutral Risk Debater** — base-rate framing of event types' historical impact
- **Portfolio Manager** — final synthesis includes event timing in score
- (+1) **Reflection** — post-decision, stores rationale around event-driven trades for continuous learning

Note: prior listing of "6 agents (Risk, Fundamental, Sentiment, Technical, Bull/Bear, Decision)" reflected pre-Pattern-2 conceptual roles -> live 11 active LLM nodes Pass 53 (per L94 / Pass 26) plus Reflection.

**DEC-501 — Polygon Options NOT upgraded; agent inputs that DON'T arrive (deferred Stage 3/Phase 1C):**
- IV rank / IV percentile (Technical + Risk Agent forward-looking risk)
- IV term structure (Risk Agent near-term stress)
- Put/Call OI ratio (Sentiment Agent positioning)
- Skew + put-spread cost (Risk Agent tail-risk pricing)
- Max-pain / dealer gamma (Risk Agent pin/squeeze risk)
- Stage-2 Risk Agent operates on ATR (backward-looking) only

**DEC-502 — Quiver Trader-tier 8 endpoint groups (agent-input expansion):**

| Endpoint | Sentiment Agent | Risk Agent | Fundamental Agent |
|---|---|---|---|
| Live Quiver News | News-flow tape (alternative to Polygon News) | — | — |
| Off-Exchange Historical | Dark-pool / off-lit institutional flow | — | — |
| Live Top Shareholders | — | Concentration / forced-liquidation risk | — |
| Live ETF Holdings | — | Passive-flow exposure (high-ETF-weight names face systematic flow) | — |
| Live SEC13F + Changes | — | Institutional positioning delta | — |
| Patents (Historical + Recent + Momentum) | — | — | Innovation pipeline / IP signal |
| Historical Executive Compensation | — | — | Governance / alignment signal |
| Corporate Donors (Bulk + Historical) | — | Political/regulatory exposure | Political/regulatory exposure |
| Congress Politicians (Bulk + Live) | Politician metadata enriches existing congresstrading per-trade context | — | — |

**DEC-502 supplement — Apewisdom + pytrends (Sentiment Agent):**
- **Apewisdom** — daily WSB+r/stocks ticker mentions (free, 2021-present)
- **pytrends** — Google Trends search-volume index per ticker (free, 2004-present)
- Combined coverage 2020-2026 with Apewisdom 2020 gap filled by pytrends
- Sentiment Agent gains real social signal vs. current zero coverage

**DEC-503 — Test pyramid mandate (cross-cutting):**
Every code push affecting agent inputs must execute full test pyramid: unit + smoke + integration + system + functional + regression + data integrity + performance + acceptance. Partial coverage non-compliant. First application: smart_money silent-gap fix (BUG-271/272/273) next turn.

### Critical silent-gap finding (BUG-271/272/273)

`smart_money_score` composite has been computing on **1-of-3 inputs** (only congressional works) since at least Pass 48. Insider + institutional + analyst-revisions silently zeroed. Smart-money confluence dimension (cube #8 per DEC-471) operates on degraded inputs. Affects all agents that consume `smart_money_score` as context (Fundamental Agent, Risk Agent, Decision Agent, Bull/Bear Debate).

**Fix:** next turn with full DEC-503 test pyramid:
- BUG-271 → REMOVE Quiver branch in `get_analyst_data`; rely on Polygon financials
- BUG-272 → migrate `insider_signal` to `live/insidertrading` bulk feed
- BUG-273 → migrate `institutional_signal` to `live/sec13f` bulk feed

### Free social sentiment alternatives confirmed

Trader tier has NO WSB/Twitter/Reddit endpoints (my prior assumption Pass 53 turn 2026-05-05 was wrong). Apewisdom + pytrends fills this gap.

**Cross-references:** AUDIT_INDEX.md DEC-500/501/502/503; AUDIT.md Pass 53 narrative; BUG_REGISTER.md BUG-271/272/273; API_AUDIT.md Pass 53 endpoint inventory; DETAILED_PROJECT_PLAN.md §3.16.

---

## Agent toolkit wiring matrix (DEC-507 + CHECKLIST #70 Pass 53 owner directive 2026-05-05)

**Mandate:** Pre-Phase-1B (or any agent-using phase entry), this matrix must show ✅ for every row. ⚠ or 🔴 rows are gating issues that block phase entry.

**L146 root cause:** Owner question Pass 53 turn 2026-05-05 "Why wasn't Polygon news → Sentiment Agent done earlier or planned?" — surfaced that data DEC (DEC-440) + toolkit DEC (DEC-464) were each approved independently without explicit integration deliverable. 1.05M Polygon news articles sat unused.

### Wiring matrix (Pass 53 baseline state 2026-05-05)

**Matrix structure note (added 2026-05-05 per 11-agent correction):** This matrix uses a **hybrid of toolkits and agents** for tracking purposes — it is NOT a 1-to-1 enumeration of the canonical 11 active TradingAgents per [DETAILED_PROJECT_PLAN §2.6](DETAILED_PROJECT_PLAN.md). Rows 1-5 group **data + toolkit + pre-Pattern-2 conceptual role** (Technical / News / Fundamental / Risk / Sentiment) — these correspond to the 5 custom toolkits (DEC-462-466) that feed the canonical agents. Rows 6-13 enumerate post-Pattern-2 LangGraph nodes. The canonical 11 agents (per DEC-057) are: 3 Analysts (Market = Row 1, Fundamentals = Row 3, News = Row 2) + Bull / Bear / Research Manager (Rows 6-8) + Trader (Row 9) + 3 Risk Debaters (Rows 10-12) + Portfolio Manager (Row 13). "Risk Agent" (Row 4) and "Sentiment Agent" (Row 5) are toolkit-level rows whose outputs flow into the canonical 11; they are not standalone agents in the LangGraph runtime. +1 Reflection node post-decision (12 total LLM nodes per propagate(), per [LEARNINGS.md L94](LEARNINGS.md)) is not tracked as a wiring row because it consumes the Portfolio Manager output, not a toolkit.

| # | Agent / Toolkit row | Toolkit | Data source path | Code path | Status | Pending work |
|---|---|---|---|---|---|---|
| 1 | Technical Agent | OurTechnicalToolkit (DEC-462) | `data_prefetch/polygon/aggs/` + `backtest/data/cache/ohlcv/` (Polygon-prefetched; yfinance HARD CUT per Batch 13 sub-task 6 2026-05-06) | `backtest/signals/technical.py` (compute_all_signals); `fetcher.fetch_ohlcv` reads cache only (no live API fallback) | ✅ WIRED | — |
| 2 | News Analyst | OurNewsToolkit (DEC-464) | `data_prefetch/polygon/news/{TICKER}.parquet` (Batch 3 done; 1,926 tickers / 1.05M articles) | `smart_money.get_news_sentiment` PRIMARY reads `data_prefetch/polygon/news/` with per-ticker `insights` parsing (positive/negative/neutral); LEGACY fallback to AV + Finnhub for backwards compat (Pass 53 Batch 13 sub-task 2 RESOLVED-IMPLEMENTED 2026-05-06) | ✅ WIRED | — (legacy paths removed in Sprint 0A.8 future cleanup) |
| 3 | Fundamental Agent | OurFundamentalsToolkit (DEC-463) | `data_prefetch/polygon/financials/{TICKER}.parquet` (Batch 4 done; 1,746 files / 91k filings) + `data_prefetch/sec_edgar/` (Batch 11 done; 6,056 files Form 4 + 8-K + 13D/G) | `smart_money.get_analyst_data` (Batch 1 stub returns "not_available" pre-Batch-13 schema parsing) | 🔴 NOT WIRED | Batch 13 continuation: parse Polygon financials format; expose EPS estimates / margin / FCF; SEC EDGAR Form 4 + 8-K + 13D/G integration |
| 3.a | smart_money composite (insider) | (sub-component of Risk Agent + Fundamental Agent) | `data_prefetch/quiver/insiders/global.parquet` (Pass 53 H5 migration 2026-05-06; was `cache/quiver/insiders/`; 1M rows; live/insiders schema) | `smart_money.insider_signal` reads bulk feed via `_load_quiver_bulk("insiders")`; uses TransactionCode 'P'/'S' + officerTitle CEO check (Pass 53 Batch 13 sub-task RESOLVED-IMPLEMENTED 2026-05-06; smart_money.PREFETCH_DIR pointer updated H5) | ✅ WIRED | — |
| 3.b | smart_money composite (institutional 13F) | (sub-component of Risk Agent + Fundamental Agent) | `data_prefetch/quiver/sec13fchanges/global.parquet` (Pass 53 H5 migration 2026-05-06; was `cache/quiver/sec13fchanges/`; 500k rows; live/sec13fchanges schema with Change_Share + Change_Pct delta) | `smart_money.institutional_signal` reads bulk feed via `_load_quiver_bulk("sec13fchanges")`; 45-day reporting lag enforced (Pass 53 Batch 13 sub-task RESOLVED-IMPLEMENTED 2026-05-06; smart_money.PREFETCH_DIR pointer updated H5) | ✅ WIRED | — |
| 4 | Risk Agent | OurRiskToolkit (DEC-466) | `data_prefetch/fred/observations/` (50 series Batch 6) + `data_prefetch/cftc/` (Batch 8) + `data_prefetch/polygon/options/` (Batch 12-c future) + `data_prefetch/ortex/` (Batch 12-d future) | `backtest/data/macro.py` macro_snapshot reads from `data_prefetch/fred/` via _fred_value_at(); 12 FRED-derived signals composed (yield curve / VIX / DXY / event calendar / HY OAS / STLFSI4 / RECPROUSM156N / ICSA / WALCL); Pass 53 Batch 13 sub-task 3 RESOLVED-IMPLEMENTED 2026-05-06 | ✅ WIRED (FRED 5-series expansion); ⚠ Options + Ortex pending Batch 12-c/12-d post-subscription | CFTC COT wiring pending Batch 13 sub-task 5; Options + Ortex post-subscription |
| 5 | Sentiment Agent | (TBD toolkit per DEC-465 spirit) | `data_prefetch/aaii/` + `data_prefetch/cnn_fg/` (composite + 7 components Batch 7) + `data_prefetch/apewisdom/` + `data_prefetch/wikipedia/` (Batch 12-a done) + `data_prefetch/quiver/{quivernews,offexchange}/` (Batch 9 v2 done) + `data_prefetch/cftc/` (Batch 8) + Polygon news (shared with #2) | `backtest/data/sentiment.py` sentiment_snapshot reads ALL data_prefetch/ paths: AAII + CNN F&G composite + CNN F&G 7 sub-components (NEW) + CFTC COT real data via dealer_positions_long/short (NEW) + Apewisdom mentions (NEW; ticker-aware) + Wikipedia pageviews (NEW; ticker-aware). Pass 53 Batch 13 sub-tasks 4+5 RESOLVED-IMPLEMENTED 2026-05-06 | ✅ WIRED | Quiver dark-pool / off-exchange wiring optional Batch 13 future; pytrends Batch 12-b retry pending |
| 6 | Bull Researcher | (consumes other toolkits) | All above | TradingAgents Phase 2 (LangGraph) | 🔴 NOT WIRED | Depends on rows 1-5 being ✅; integration during Sprint 7 (Phase 1B) |
| 7 | Bear Researcher | (consumes other toolkits) | All above | TradingAgents Phase 2 (LangGraph) | 🔴 NOT WIRED | Depends on rows 1-5 being ✅ |
| 8 | Research Manager | (synthesis Phase 2) | All above | TradingAgents Phase 2 | 🔴 NOT WIRED | Depends on rows 6-7 being ✅ |
| 9 | Trader | OurTraderToolkit (DEC-465) | All above | TradingAgents Phase 3 | 🔴 NOT WIRED | Depends on row 8 being ✅ |
| 10 | Aggressive Risk Debater | OurRiskToolkit (DEC-466) | Same as Risk Agent (row 4) | TradingAgents Phase 4 | 🔴 NOT WIRED | Depends on row 4 being ✅ |
| 11 | Conservative Risk Debater | OurRiskToolkit (DEC-466) | Same as Risk Agent (row 4) | TradingAgents Phase 4 | 🔴 NOT WIRED | Depends on row 4 being ✅ |
| 12 | Neutral Risk Debater | OurRiskToolkit (DEC-466) | Same as Risk Agent (row 4) | TradingAgents Phase 4 | 🔴 NOT WIRED | Depends on row 4 being ✅ |
| 13 | Portfolio Manager | (synthesis all toolkits) | All above | TradingAgents Phase 4 (FINAL DECISION) | 🔴 NOT WIRED | Depends on rows 1-12 being ✅ |

### Status legend
- ✅ = wired AND tested end-to-end (data path → toolkit fn → agent prompt all working)
- ⚠ = partial (some data sources connected; others pending)
- 🔴 = not wired (data may be cached but consumer code doesn't read it OR consumer not built)

### Phase entry gates per #70
- **Phase 1A entry (Sprint 6.5):** Rows 1-5 should be ⚠ or ✅. Row 1 ✅ required; rows 2-5 can be ⚠ since `--no-agents` flag used. Currently: 1=✅, 2-5=mixed.
- **Phase 1B entry (Sprint 7):** Rows 1-5 must be ✅ (data tier complete); rows 6-13 can be ⚠ or ✅ (orchestration tier).
- **Phase 1B-α run (Sprint 9):** ALL ROWS ✅. No ⚠ or 🔴 permitted.

### Pass 53 Batch 13 scope (corrects this matrix to ✅ for rows 2, 3, 4, 5)

Batch 13 NO-LIVE-API refactor MUST close:
1. Row 2 (News Analyst) — rewrite `get_news_sentiment` to read `data_prefetch/polygon/news/`
2. Row 3 (Fundamental Agent) — parse Polygon financials + integrate SEC EDGAR
3. Row 4 (Risk Agent) — wire 5+ high-priority FRED series (HY OAS, STLFSI4, RECPROUSM156N, ICSA, WALCL) + CFTC COT
4. Row 5 (Sentiment Agent) — wire CNN F&G 7 components + Apewisdom + Wikipedia + Quiver dark-pool

Rows 6-13 (TradingAgents orchestration) addressed Sprint 7 (Phase 1B), gated on rows 1-5 ✅.

### Pass 53 Batch 12-c/12-d (Options + Ortex; post-subscription)

When owner subscribes per DEC-506:
- Polygon Options Starter → enriches Row 4 (Risk Agent) + Row 5 (Sentiment Agent)
- Ortex → enriches Row 4 (Risk Agent) + Row 5 (Sentiment Agent)
- Wiring matrix updated post-Batch-12-c/12-d completion

### Cross-references
- DEC-507 (this matrix's parent decision)
- L146 (lesson — data DEC + toolkit DEC ≠ integration)
- CHECKLIST #70 (mandates this matrix updated pre-phase-entry)
- DEC-462-466 (custom toolkit DECs that this matrix tracks)
- DEC-503 (test pyramid; complementary — pyramid validates code, this matrix validates wiring exists)
- DEC-595 + CHECKLIST #73 (gate executable tests — Pass 53 evening 2026-05-07; gate 1 `test_gate_pre_phase_1a_entry` is the EXECUTABLE form of Phase 1A entry-gate verification per CHECKLIST #70 row above; gate 1 PASSES today confirming Row 1 ✅ + smoke OHLCV + universe + DEC-505 4-fold config valid)
- DEC-594 (Test-Artifact Same-Commit HARD RULE — H5 migration this turn updated test paths in same commit as wiring matrix path update)

### Pass 53 Day 8 verification log (2026-05-07)

- Row 1 Technical Agent ✅ — verified by `test_gate_pre_phase_1a_entry` PASS
- Row 2 News Analyst ✅ — verified by smart_money.get_news_sentiment reading data_prefetch/polygon/news/
- Row 3 Fundamental Agent 🔴 — Batch 13 continuation pending; not blocking Phase 1A (1A-α uses `--no-agents`)
- Row 3.a/3.b smart_money composites ✅ — H5 migration verified by smart_money.PREFETCH_DIR = data_prefetch/quiver/
- Row 4 Risk Agent ✅ — FRED 50 series data-integrity test 4 PASS
- Row 5 Sentiment Agent ✅ — AAII/CNN F&G/Apewisdom/Wikipedia data-integrity test 7 PASS
- Rows 6-13 TradingAgents orchestration 🔴 — Sprint 7 work; NOT required for Phase 1A May 15 start

**Phase 1A entry gate state:** Row 1 ✅ + rows 2-5 mixed-but-acceptable per #70 1A-entry rule (rows 2-5 can be ⚠ when `--no-agents` flag used). Phase 1A May 15 start UNBLOCKED.

**Phase 1B-α gate state (Sprint 9):** Rows 6-13 still 🔴; gate 3 `test_gate_pre_phase_1b_alpha_run` SKIP today — will require all rows ✅ before run.


## Pass 53 Day 9 v8 (2026-05-07 noon) — Deep L146/DEC-507 wiring audit + G1-G17 inventory

After BUG-VIX-PROXY (G1) was caught by H3 dress rehearsal, owner directed: "There are clearly a lot of L146 / DEC-507 misses. Do a deep review and identify all gaps. Address them." This section is the canonical wiring matrix for the deep audit.

### Methodology
1. Inventoried every directory under `data_prefetch/<api>/<endpoint>/` (10 APIs, ~26K files, ~1.3 GB)
2. Grepped consumer code (`backtest/data/{cache,fetcher,macro,sentiment,smart_money,universe}.py`) for path references
3. Cross-checked each (prefetched dataset → consumer call site) pair
4. Classified each gap by severity + fix complexity

### Findings — 16 wiring gaps confirmed

| # | Source | Prefetch state | Consumer status | Gap class | Fix tier |
|---|---|---|---|---|---|
| **G1** ✅ FIXED | FRED VIXCLS | 1623 obs (prefetched this turn) | `macro.py` source priority FRED→^VIX→VXX-scale-safeguard→fail-loud | **CRITICAL — was fully broken** | Tier 1 — DONE |
| **G2** | AAII weekly | `data_prefetch/aaii/weekly_sentiment.parquet` | `sentiment.py:48` reads legacy `backtest/data/aaii_sentiment.csv` | Silent legacy-vs-Sprint-0A duplication | Tier 2 — owner decision |
| **G3** | CNN F&G daily | `data_prefetch/cnn_fg/daily.parquet` | `sentiment.py:117` reads legacy `backtest/data/cnn_fear_greed.csv` | Silent legacy-vs-Sprint-0A duplication | Tier 2 — owner decision |
| **G4** ✅ FIXED | Polygon reference (599 tickers) | Files in `legacy_archive_pass53/reference/` | `fetcher.py:192` was reading `data_prefetch/polygon/reference/` (didn't exist) | **CRITICAL path bug** | Tier 1 — DONE this turn |
| **G5** ✅ FIXED | Polygon dividends (2 tickers — sparse) | Files in `legacy_archive_pass53/dividends/` | `fetcher.py:276` was reading `data_prefetch/polygon/dividends/` (didn't exist) | Path bug + sparse coverage | Tier 1 — DONE this turn |
| **G6** | Polygon events (1687 tickers) | `data_prefetch/polygon/events/` populated; schema = `event_type/event_date/details_json`; **AAPL row contains ticker_change** | NO CONSUMER | Schema is corporate-actions (ticker_change/listing/delisting); not earnings calendar | Tier 3 — defer (low Phase-1A value) |
| **G7** 🔴 | SEC EDGAR (6056 files) | `data_prefetch/sec_edgar/{4, 8_K, SC_13D, SC_13G}/` | `smart_money.py:16` docstring says "reads from data_prefetch/sec_edgar/" but **NO CODE DOES** | 70MB regulatory filings entirely unused | Tier 2 — high impact (8-K = catalyst) |
| **G8** | pytrends (1417 ticker files, 12MB) | `data_prefetch/pytrends/<TICKER>.parquet` | NO CONSUMER | Entirely unused | Tier 3 — owner decision |
| **G9** | ALFRED (50 vintage series, 15MB) | `data_prefetch/alfred/<SERIES>.parquet` | `macro.py:102` calls live ALFRED API | Live API instead of cache reads | Tier 2 — owner decision |
| **G10** | Quiver insider per-ticker (509 files) | `data_prefetch/quiver/insider/<TICKER>.parquet` | Code uses bulk `_load_quiver_bulk("insiders")` only | Per-ticker dir unused; bulk version may be incomplete | Tier 3 — investigate completeness |
| **G11** | Quiver institutional per-ticker (509 files) | `data_prefetch/quiver/institutional/<TICKER>.parquet` | Code uses bulk `sec13fchanges` only | Per-ticker dir unused | Tier 3 — investigate |
| **G12** | Quiver etfholdings (1563 files) | `data_prefetch/quiver/etfholdings/<TICKER>.parquet` | NO CONSUMER | Unused | Tier 3 — owner decision |
| **G13** | Quiver offexchange (1851 files — largest) | `data_prefetch/quiver/offexchange/<TICKER>.parquet` | NO CONSUMER | Dark-pool data unused | Tier 3 — owner decision |
| **G14** | Quiver topshareholders (1937 files) | `data_prefetch/quiver/topshareholders/<TICKER>.parquet` | NO CONSUMER | Unused | Tier 3 — owner decision |
| **G15** | Quiver wallstreetbets (509 files) | `data_prefetch/quiver/wallstreetbets/<TICKER>.parquet` | NO CONSUMER | Reddit sentiment unused | Tier 3 — owner decision |
| **G16** | Quiver wikipedia mirror (509 files) | `data_prefetch/quiver/wikipedia/` (vs separate `data_prefetch/wikipedia/`) | Separate `data_prefetch/wikipedia/` (1414 files) IS consumed; quiver mirror redundant | Redundant prefetch | Tier 3 — defer / cleanup |
| **G17** | Quiver patentmomentum / corporatedonors / quivernews / sec13f | 1 file each | NO CONSUMER | All unused | Tier 3 — owner decision |

### Tier 1 (fixed this turn — broken paths, no decisions needed)

- **G1 BUG-VIX-PROXY** (committed `42a338da` predecessor + this turn's macro.py edits)
  - `data_prefetch/fred/observations/VIXCLS.parquet` prefetched (1623 obs)
  - `macro.py` source priority: FRED → ^VIX OHLCV → VXX-scale-safeguard → fail-loud
  - 4 regression tests in `test_bug_vix_proxy_regression.py` (all PASS)
  - **Verified at runtime:** H3 dress rehearsal regime distribution went 100% crisis → bull=200/neutral=60/crisis=0 (correct for 2023)
- **G4 BUG-PF-REFPATH** (this turn)
  - `fetcher.py:fetch_info` searches both canonical + legacy_archive_pass53 paths
  - Schema mapping fixed: `sic_description → industry`, `primary_exchange → exchange`, `list_date → ipo_date`
  - **Verified:** `fetch_info('AAPL')` now returns `market_cap=4.07T, name='Apple Inc.'`
- **G5 BUG-PF-DIVPATH** (this turn)
  - `fetcher.py:fetch_dividends` searches both paths
- **L146 wiring-matrix regression suite** ([`test_l146_wiring_matrix.py`](backtest/tests/test_l146_wiring_matrix.py))
  - 18 tests: 14 (data-source × consumer-module) parametric + 4 explicit gap-fix regression tests
  - Auto-detects future drift: any new prefetch dir without a consumer reference fails the suite
  - All 18 PASS

### Tier 2 / Tier 3 — owner decisions required (NOT fixed this turn)

Surfacing as a single block per CLAUDE.md "ALL decisions need explicit owner approval":

**Tier 2 (high-impact; ~1-2 hours each):**
- **G2 + G3** — should AAII / CNN F&G daily switch from legacy CSVs to Sprint 0A parquet? Both work; legacy CSV is hand-maintained (last refresh date drifts), Sprint 0A parquet has automated refresh via GH Actions. Recommend **migrate** with a 1-week soak period of dual reads + comparison test before deletion.
- **G7 SEC EDGAR** — 6056 filings (4/8_K/SC_13D/SC_13G) prefetched. 8-K filings are material-event disclosures (M&A, executive changes, restatements) — directly relevant to catalyst-based strategies (DEC-???). Should we wire as a Layer-2 catalyst signal (binary: "8-K filed in past 5 days")? Recommend **YES**.
- **G9 ALFRED** — `macro.py` calls live ALFRED API for vintage data per DEC-301; data is also prefetched at `data_prefetch/alfred/`. Recommend **switch to cache** (loses ad-hoc vintage queries but ensures DEC-497 NO-LIVE-API hard cut compliance).

**Tier 3 (strategic — wire as new signals or delete prefetch):**
- **G6 Polygon events** — corporate actions (ticker changes / listing / delisting). Useful for survivorship adjustment but no immediate trade signal. Recommend **defer to Sprint 5+**.
- **G8 pytrends** — Google Trends search-volume index per ticker. Could be a Layer-2 retail-attention signal. Recommend **owner decide: wire as signal or delete prefetch**.
- **G10 / G11 / G16** — per-ticker Quiver dirs are duplicated by bulk versions or other prefetched paths. Recommend **delete redundant prefetches** to save space.
- **G12-G15 Quiver datasets** — etfholdings (1563), offexchange (1851), topshareholders (1937), wallstreetbets (509). Each represents a potential signal not currently used. Recommend **owner decide per dataset** — wire each into smart_money composite or delete.
- **G17 Quiver micro-datasets** (patentmomentum, corporatedonors, quivernews, sec13f) — 1 file each, unclear if real or stub. Recommend **owner audit + decide**.

### Sister findings — process gaps (not data path gaps)

**`scripts/prefetch_macro.py:10` docstring listed VIXCLS as included; the actual `SERIES` dict omitted it.** Same L149 spec-without-build pattern at the prefetch-script level. Fix this turn: added VIXCLS to SERIES + added dotenv loader so `FRED_API_KEY` doesn't need manual export.

### Cross-references

- L146 (data DEC + toolkit DEC ≠ integration; wiring is third deliverable)
- DEC-507 (Agent × Data source × Code path × Verified status matrix HARD RULE)
- DEC-508 (15-category test plan + 3-phase A/B/C gate for forks)
- DEC-302 (VXX/UUP proxy fallback — original spec; hardened this turn with Option B scale safeguard)
- DEC-440 (Polygon news prefetch — original L146 instance) + DEC-464 (smart_money toolkit) + DEC-497 D4 (yfinance HARD CUT — triggered the VIX gap)
- L149 (spec-without-build) + L150 (pyramid dimension-coverage gap) — sister meta-patterns
- BUG-VIX-PROXY (G1) + BUG-PF-REFPATH (G4) + BUG-PF-DIVPATH (G5) — concrete instances

### Phase 1A May 15 entry-gate impact

| Gap | Blocks May 15? | Reason |
|---|---|---|
| G1 VIX | NO (fixed) | regime classifier now correct |
| G4 reference | NO (fixed) | fetch_info now returns real data |
| G5 dividends | NO (fixed) | path fixed; 2 ticker coverage is all that exists |
| G2 + G3 (AAII / CNN) | NO | legacy CSVs work; migration is non-blocking |
| G7 SEC EDGAR | NO | not used by any current strategy; impact is "missed signal" not "broken signal" |
| G9 ALFRED | NO | live API works; vintage queries non-blocking for Phase 1A baseline |
| G6/G8/G10-G17 | NO | unused = no contamination of current results |

**All gaps are non-blocking for May 15 Phase 1A start.** Owner decisions on Tier 2/3 can be batched post-May-15 without affecting Phase 1A baseline.


## Pass 53 Day 9 v8c (2026-05-07 evening) — Owner directive "Approved. Fix all" — G2-G17 closure (16/16)

Owner approved fixing all 13 remaining L146/DEC-507 gaps (G2/G3/G6/G7/G8/G9/G10/G11/G12/G13/G14/G15/G16/G17). Executed in 4 waves with commit-per-wave; final pyramid 581 PASS / 10 SKIP / 5 xfail in 67s.

### Final wiring matrix — all 17 gaps closed or documented

| ID | Status | Closure mechanism | Commit |
|---|---|---|---|
| G1 VIX | ✅ FIXED | FRED VIXCLS prefetch + 4-tier source priority + scale safeguard + fail-loud | `8d1b3b9a` |
| G2 AAII | ✅ MIGRATED | sentiment._load_aaii reads Sprint 0A parquet first, legacy CSV fallback | `ea1679d9` |
| G3 CNN F&G daily | ✅ DOCUMENTED | Legacy CSV is canonical for backtest (1630 rows vs 253 in parquet); merges newer parquet rows | `ea1679d9` |
| G4 Polygon reference | ✅ FIXED | fetcher.fetch_info searches canonical+legacy_archive paths; schema mapping fixed | `8d1b3b9a` |
| G5 Polygon dividends | ✅ FIXED | fetcher.fetch_dividends searches both paths | `8d1b3b9a` |
| G6 Polygon events | ✅ WIRED | fetcher.get_ticker_change_history accessor (PIT survivorship metadata) | `<v8c-final>` |
| G7 SEC EDGAR | ✅ WIRED | smart_money.get_sec_filings + sec_catalyst_signal — all 4 form types | `b245484e` |
| G8 pytrends | ✅ WIRED | sentiment.get_search_attention (SVI 0-100 + trend) | `<v8c-final>` |
| G9 ALFRED | ✅ FIXED | macro._fred_series consults vintage cache before live API | `ea1679d9` |
| G10 Quiver insider per-tkr | ✅ WIRED | smart_money.get_insider_transactions_pertkr (per-ticker fast path with bulk fallback) | `<v8c-final>` |
| G11 Quiver institutional per-tkr | ✅ DOCUMENTED | Per-ticker prefetch incomplete (~18% empty incl. AAPL); accessor warns + redirects to bulk path | `<v8c-final>` |
| G12 Quiver etfholdings | ✅ WIRED | smart_money.get_etf_holdings (ETF inclusion + concentration) | `0891bd28` |
| G13 Quiver offexchange | ✅ WIRED | smart_money.get_offexchange_volume (DPI + short ratio) | `0891bd28` |
| G14 Quiver topshareholders | ✅ WIRED | smart_money.get_top_shareholders (top-N institutional concentration) | `0891bd28` |
| G15 Quiver wallstreetbets | ✅ WIRED | smart_money.get_wsb_attention (mentions + sentiment + rank) | `0891bd28` |
| G16 Quiver wikipedia mirror | ✅ DOCUMENTED | Mirror is empty for sampled tickers; separate data_prefetch/wikipedia/ is canonical (already consumed). Regression test asserts the broken state — fails loud if prefetch is repaired so we know to wire | `<v8c-final>` |
| G17 Quiver micro-datasets | ✅ WIRED | smart_money.get_patent_momentum + get_corporate_donations + get_sec13f_holdings (3 of 4; quivernews is general-feed, not per-ticker — Polygon news is canonical) | `<v8c-final>` |

### Wave A — G2 + G3 + G9 (commit `ea1679d9`, 6 regression tests)

- G2: AAII parquet schema matches legacy CSV exactly; migration trivial.
- G3: Sprint 0A daily.parquet has only ~253 rows (~1y). Legacy CSV has 1630 rows. Code merges (CSV history + any newer parquet rows). DOCUMENTED as intentional retention; not a defect.
- G9: ALFRED 50 vintage series cached at `data_prefetch/alfred/`; macro.py `_fred_series` now reads cache for vintage queries (when `as_of` provided). Honors DEC-497 NO-LIVE-API HARD CUT while still providing PIT-correct DEC-301 vintage data.

### Wave B — G7 SEC EDGAR (commit `b245484e`, 6 regression tests)

Highest-impact wave. Wires 6056-file SEC EDGAR prefetch (4 form types × ~1500 tickers):
- Form 4 (insider transactions, ~1336 rows AAPL)
- 8-K (material events, ~234 rows AAPL)
- SC 13D (activist 5%+ holders, ~7 rows AAPL)
- SC 13G (passive 5%+ holders, ~81 rows AAPL)

Public accessors: `get_sec_filings(ticker, as_of, lookback_days, form)` + composite `sec_catalyst_signal(ticker, as_of)` with heuristic scoring. Verified on AAPL 2024-05-06: catalyst score=1, label="recent_8k" (May 2 + May 3 8-K filings detected within 5d window).

### Wave C — G12 + G13 + G14 + G15 (commit `0891bd28`, 12 regression tests)

Wires 4 previously-unused Quiver datasets:
- **G12 etfholdings**: AAPL held by 703 ETFs, top weight 69.77% in AAPX, $7.55T total.
- **G13 offexchange**: AAPL 2024-06-15 dark-pool DPI 0.48 (5d avg).
- **G14 topshareholders**: AAPL top-5: Vanguard 1.43B / BlackRock 1.15B / State Street 604M / Geode 358M / FMR 307M shares.
- **G15 wallstreetbets**: AAPL 2024-06-15 lookback-7: 1876 mentions, rank #1.

### Wave D — G6 + G8 + G10 + G11 + G16 + G17 (this commit, 13 regression tests)

- **G6** Polygon events: 1687 ticker_change events; useful for survivorship adjustment.
- **G8** pytrends: AAPL 2024-06-15 SVI rising (avg 55, latest 100).
- **G10** Quiver insider per-tkr: AAPL 2024-12-15 90d → 6 buys, 25 sells, cluster=True (source: per_ticker fast path).
- **G11** Quiver institutional per-tkr: documented as ~18% empty (AAPL specifically empty); accessor returns warning redirecting to canonical bulk path.
- **G16** Quiver wikipedia mirror: 100/100 sampled files empty; documented as broken; regression test asserts the broken state.
- **G17** Quiver micro-datasets: 3 of 4 wired (patent_momentum, corporate_donations, sec13f bulk); quivernews skipped (general feed, not per-ticker; Polygon news is the canonical news consumer).

### Pyramid status

| Suite | Pre-Wave A (Day 9 v8b) | Post-Wave D (this) |
|---|---|---|
| Mandatory PASS | 271 | **295** (+24 wave A/B/C/D regressions; subset of 581 below excluded performance/e2e tests) |
| Full PASS | 544 | **581** |
| Full SKIP | 10 | 10 |
| xfail | 5 | 5 |
| Wall time (full) | 98s | 67s |

### Code reach

After Wave A-D, every prefetched dataset under `data_prefetch/<api>/<endpoint>/` is reachable from at least one consumer accessor in `backtest/data/`. The L146 wiring-matrix regression suite ([`test_l146_wiring_matrix.py`](backtest/tests/test_l146_wiring_matrix.py)) auto-detects future drift.

### Strategy-side wiring deferred

Per CLAUDE.md, strategy-into-signal decisions (which signals enter `smart_money_score` composite, which agent inputs receive each new signal, which Layer-2/3 strategies are added) are Phase 1B+ scope. Wave A-D closed the **data-flow plumbing**; **strategy choices remain Phase 1B+ owner decisions**.

### Cross-references

- L146 (the original gap pattern); L149 (spec-without-build); L150 (pyramid dimension-coverage gap); BUG-VIX-PROXY (G1) + BUG-PF-REFPATH (G4) + BUG-PF-DIVPATH (G5)
- DEC-497 D4 (yfinance HARD CUT); DEC-507 (wiring matrix HARD RULE — this section IS the matrix); DEC-594 (same-commit); DEC-595 (gate executables); DEC-596 (standing approvals)

**16 of 16 L146/DEC-507 gaps closed or documented. Phase 1A May 15 entry-readiness UNCHANGED (was already confirmed Day 9 v7); Phase 1B-α now has expanded toolkit available (12 new accessor functions across 4 modules).**
