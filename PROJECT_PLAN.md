# Stock Picks & Automated Trading System
**Owner:** Jeet Mehta
**Repo:** github.com/jeetmehta1991/stock-picks-app
**Updated:** April 2026 (post-Pass-38 architectural consolidation)

> Companion docs: `AUDIT.md` (decision/bug ledger, 38 passes) · `CHECKLIST.md` (29 pre-action rules) · `LEARNINGS.md` (105 universal lessons) · `CLAUDE.md` (top-of-mind rules) · `PROJECT_PLAN_ARCHIVE.md` (pre-April-2026 detail)

---

## 1. What This Is

An algorithmic swing trading system for US equities that combines rule-based strategy screening with a multi-agent AI overlay for trade conviction scoring. Goal: high ROI with medium-high risk profile, accepting drawdowns in exchange for stronger returns. Buys dips during volatile and crisis markets when most signals are unfavorable.

**In scope:** Long swing trades (1-30 day holds) on S&P 500 + extended universe (~600-650 tickers). Short trades in non-bull regimes only.
**Out of scope:** Intraday trading (separate future project). Crypto, forex, options as primary instruments.
**Status (Apr 2026):** Phase 0 design complete. Phase 0 implementation pending start.

---

## 2. Five-Stage Roadmap

| Stage | Name | Capital | Duration | Goal |
|---|---|---|---|---|
| 1 | Strategy Discovery (DONE) | $0 | 6mo | Daily picks website. Done. |
| 2 | Strategy Validation (CURRENT) | $0 | 4-6mo | Backtest 60 strategies, prove edge over rules-only baseline |
| 3 | Paper Trading | $0 | 3-6mo | IBKR paper account, validate live mechanics match backtest |
| 4 | Small Live | $10K-$25K | 6-12mo | Real money, conservative size, email approval per trade |
| 5 | Scaled Live | $50K+ | ongoing | Full automation, scaled position sizes, full agent layer |

Stage gate criteria: each stage must show statistically meaningful edge before progressing. Detailed gates in Section 11.

---

## 3. Phase 0 — The Pre-Backtest Architecture Build

Phase 0 prepares the codebase for the Stage 2 backtest. Five sub-phases:

| Phase | Topic | Duration | Key deliverables |
|---|---|---|---|
| 0.A | Prefetch & data foundation | ~8 weeks | Repair Quiver before cancellation, evaluate Polygon News, build PIT loader, OpenBB fundamentals integration, S&P 500 historical CSV (DECISION-052) |
| 0.B | Portfolio class | 1 week | Position state, sizing logic, portfolio-aware decisions |
| 0.C | Engine + TradingAgents framework adoption | 3 weeks | Migrate from custom 6-agent pipeline to forked TradingAgents (DECISION-051 REVISED-3, Pattern 1) |
| 0.D | Modern signals via fork | ~6 weeks | smartmoneyconcepts (ICT, MIT-licensed) instead of custom build, earnings momentum, calendar |
| 0.E | Validation & smoke gates | parallel | freezegun PIT regression tests, characterization tests on retained custom code |

**Total Phase 0:** ~15-16 weeks. **Total path to live:** 8-12 months.

Detailed bug fixes happen during the phase that owns each bug (per Pass 38 Part B Section B triage plan).

---

## 4. Stage 2 Backtest — The $300 Two-Stage Plan

Per DECISION-051 REVISED-3, DECISION-058 REVISED, DECISION-059, DECISION-060.

### Stage 1: Rules-Only Baseline ($0)

Full 4-year × 509-ticker backtest. Strategies + signals + position sizing + PIT correctness + walk-forward + transaction costs + slippage. **No agents in the loop.** Outputs baseline performance: Sharpe, drawdown, hit rate, regime-conditioned breakdowns. Free.

### Stage 2: Selective Agent Overlay (~$300 hard cap)

Run TradingAgents framework via GPT-5.4-mini on a curated subset of ~1,800 candidates:
- ~1,200 high-tier strategy trades (5%/4% confidence)
- ~300 earnings-window trades (±5 days)
- ~150 regime-transition trades (crisis flagged or regime change ±5 days)
- ~150 random control sample for comparison

Compare agent decisions to Stage 1 rules-only decisions. Measure: do agents add Sharpe/win-rate improvement, or just noise?

**Mandatory smoke test gating per DECISION-060 + CHECKLIST #29:**

| Gate | Trigger | Action |
|---|---|---|
| Smoke test | First 10 candidates (~$2) | Owner manually reviews agent outputs, approves before scaling |
| Mid batch | First 100 candidates (~$15-20) | Owner reviews actual cost vs estimate; if >2× off, stop and recalibrate |
| 80% spend | $240 cumulative | Owner explicitly approves continuation |
| Hard stop | $300 cumulative | Stop regardless of completeness |
| Quality kill | Smoke test outputs incoherent | Stop, switch model or abandon Stage 2 |

### Stage 3: Live Trading Adoption

If Stage 2 shows agents add edge → integrate TradingAgents in live with Sonnet+Haiku (~$40-50/month).
If Stage 2 shows agents don't add edge → drop agents, run rules-only in live (saves the agent cost).

---

## 5. Universe Architecture — Three Tiers

| Tier | Source | Refresh | Purpose |
|---|---|---|---|
| 1 | S&P 500 (slickcharts.com → static CSV) | Quarterly | Core universe, ~500 tickers |
| 2 | Extended (spinoffs, recent IPOs, momentum leaders) | Monthly (Stage 3+) | ~50-100 additions |
| 3 | Momentum watchlist (custom screen) | Monthly (Stage 3+) | ~50 high-momentum names |

Total live universe: ~600-650 tickers. Wikipedia banned per L88.

---

## 6. Strategy Universe — 60 Strategies, 7 Categories

| Category | Count | Examples |
|---|---|---|
| Momentum / Trend | 12 | 50/200 SMA cross, breakout from base, sector momentum rotation |
| Mean Reversion | 10 | Oversold bounce, RSI divergence, Bollinger reversion |
| Smart Money | 8 | Congressional cluster buy, insider cluster buy, 13F accumulation |
| Volatility | 7 | VIX spike fade, IV crush, post-earnings drift |
| Fundamental | 8 | Earnings momentum, analyst upgrade clusters, buyback announcements |
| Macro / Regime | 6 | Yield curve trades, crisis dip-buying, sector rotation |
| Event-Driven | 9 | Spinoffs, M&A arbitrage, post-IPO drift, earnings PEAD |

Strategy attributes:
- **`earnings_tolerant`** (DECISION-013 REVISED): PEAD and earnings-momentum strategies ignore earnings proximity. Others reduce size 0.75× within 7 days, 0.5× within 3 days.
- **Confidence tier**: 5%, 4%, 3%, or 1.5% position size based on signal quality
- Strategies marked CVD-dependent dropped per DECISION-046 (daily OHLCV cannot produce real CVD)

Strategy details preserved in PROJECT_PLAN_ARCHIVE.md sections 5 and 6. New strategies added during Phase 0.D via forked smartmoneyconcepts library (ICT/SMC patterns) per DECISION-045.

---

## 7. Signal Universe — ~220 Fields Per Instrument Per Day

Reduced from old 274 fields by:
- Dropping CVD fields (DECISION-046)
- Removing duplicate cross-instrument signals
- Adding ICT/SMC fields from smartmoneyconcepts library (Phase 0.D)

Categories: technical (~80 fields), fundamental (~40), smart money (~30), options (~25, Stage 3+), macro (~25), sentiment (~20).

Full field-level spec preserved in PROJECT_PLAN_ARCHIVE.md section 9.

---

## 8. Confidence Tiers, Position Sizing, Tier Adjustment

### Stage 1 (rule-based preliminary tier)

Based on signal counts and smart money:

| Tier | Triggers | Position size |
|---|---|---|
| EXCEPTIONAL | 3+ strategies fire AND congressional cluster buy AND insider cluster buy | 5% of capital |
| VERY HIGH | 2+ strategies fire AND 1+ smart money signal | 4% |
| HIGH | 2+ strategies fire OR 1 strategy + smart money | 3% |
| MEDIUM-HIGH | 1 strategy fire + supporting context | 1.5% |
| MEDIUM | 1 strategy fire alone | 1% (Stage 3+ only) |
| LOW / AVOID | Below minimum or contradicted | watch-only |

### Stage 2 (TradingAgents 5-tier overlay) — DECISION-061 Option 1

TradingAgents Portfolio Manager outputs Buy/Overweight/Hold/Underweight/Sell. Maps to tier adjustment:
- **Buy** → upgrade preliminary tier by 1 level
- **Overweight** → priority flag within tier (stay in tier, prioritize for execution)
- **Hold** → no change
- **Underweight** → downgrade preliminary tier by 1 level
- **Sell** → downgrade to AVOID (do not trade)

AVOID tier never upgrades regardless of agent rating.

### Position size multiplier stack

```
position_size = base × tier_multiplier × earnings_modifier × vol_targeted × drawdown_modifier
```

- `tier_multiplier`: 5%, 4%, 3%, 1.5%, 1%, or 0 per table above
- `earnings_modifier`: 1.0 if earnings_tolerant=True, else 0.75 within 7d / 0.5 within 3d
- `vol_targeted`: pending DECISION-023 (inverse-ATR sizing)
- `drawdown_modifier`: pending DECISION-022 (step function at -5/-10/-15%)

Floor: any combined multiplier < 0.10% is skipped as below_minimum_size.

---

## 9. Agent Architecture — TradingAgents Framework

Per DECISION-051 REVISED-3 (staged adoption) + DECISION-055 (cost-optimized config) + DECISION-057 (drop Social) + DECISION-058 REVISED (GPT-5.4-mini for backtest, Sonnet+Haiku for live).

### 11 agents per propagate() (12 minus dropped Social)

| Group | Agents | Role |
|---|---|---|
| Analysts (3) | Market, Fundamentals, News | Each makes 2-4 LLM calls due to tool-use loops. Quick LLM tier. |
| Researchers (2) | Bull, Bear | Debate up to `max_debate_rounds` (default 1). Quick LLM. |
| Research Manager (1) | | Synthesizes Bull/Bear into investment plan. **Deep LLM tier.** |
| Trader (1) | | Composes transaction proposal. Quick LLM. |
| Risk Debaters (3) | Aggressive, Neutral, Conservative | Debate up to `max_risk_discuss_rounds` (default 1). Quick LLM. |
| Portfolio Manager (1) | | Final 5-tier decision. **Deep LLM tier.** |

Plus Reflection node (post-decision) writes to memory log. Quick LLM.

### LLM provider strategy

| Stage | Provider | Quick model | Deep model | Reason |
|---|---|---|---|---|
| Stage 2 backtest | OpenAI | GPT-5.4-mini | GPT-5.4-mini | Best budget tier reasoning, 99.7% structured output compliance, US-hosted |
| Stage 3+ live | Anthropic | Haiku 4.5 | Sonnet 4.6 | Quality matters for real money, known integration |

Estimated cost per propagate(): ~$0.16-0.18 with GPT-5.4-mini (Stage 2). Real cost validated by smoke test gate.

### Output schema mapping (DECISION-008/009/010/011/012 partial revisions, DECISION-062 pending)

| Old field (our 6-agent) | New equivalent (TradingAgents) |
|---|---|
| Decision Agent action | Portfolio Manager 5-tier rating |
| position_size_modifier (continuous 0-1.5) | DECISION-062: map 5-tier → multiplier (Buy=1.0, Overweight=0.85, Hold=skip, Underweight=0.5 shadow, Sell=skip) |
| Risk Agent trade_blocked | Sell rating = blocked |
| Bull/Bear debate_winner | Research Manager judge_decision |
| recommended_exit | NOT in TradingAgents output — keep our rules-based exit logic |

---

## 10. Data Sources by Stage

| Source | Stage 1-2 | Stage 3+ | Purpose | Cost |
|---|---|---|---|---|
| yfinance | ✓ | ✓ | OHLCV history | Free |
| Alpha Vantage | ✓ (basic) | (deprecated) | Stage 1 daily picks website only | Free tier |
| Polygon | (eval Phase 0.A) | ✓ | News, intraday, options chains | $30/month |
| OpenBB | ✓ | ✓ | Fundamentals (replaces scraping) | Free |
| Quiver | ✓ (final repair) | ✓ | Congressional, insider, gov contracts, lobbying | $50-100/month |
| Unusual Whales | — | ✓ (Phase 1C+) | Options flow | $50/month |
| Ortex | — | ✓ (Stage 3+) | Short interest, borrow rates | $40/month |
| FRED | ✓ | ✓ | Macro (yield curve, etc.) | Free |
| AAII / CNN F&G | ✓ | ✓ | Sentiment | Free |

Total live monthly: $117-195 with Quiver, $67-95 without (Quiver retention pending Phase 0.A repair completion).

---

## 11. Stage 2 → Stage 3 Validation Gates

Stage 2 must pass these gates before Stage 3 paper trading:

1. **Edge over baseline:** Stage 2 (with agents on curated subset) shows ≥3pp annualized return improvement over Stage 1 (rules-only) on the subset, or per-tier predictive accuracy at p<0.05
2. **Per-strategy minimum:** Each strategy generates ≥500 trades AND ≥143 independent positions (per L99 — 3.5× row inflation correction)
3. **Regime breakdown:** Performance positive in at least 2 of 4 regimes (bull, neutral, bear, crisis)
4. **Drawdown bounded:** Max drawdown ≤25% across full backtest
5. **Walk-forward consistency:** Out-of-sample Sharpe within 0.5 of in-sample
6. **Transaction costs honest:** Costs computed at actual broker spread + slippage per DECISION-040 PIT loader
7. **No look-ahead:** PIT regression tests via freezegun (DECISION-050) pass
8. **Agent score calibration:** Distribution of Portfolio Manager 5-tier output is roughly normal (not all Hold, not all extremes)

Detailed gate logic preserved in PROJECT_PLAN_ARCHIVE.md.

---

## 12. Risk Management Philosophy

**Core principle:** Buy dips in volatile and crisis markets. Most professional systems are forced out of crisis trades by drawdown rules; ours leans in within disciplined size constraints.

**Implemented (Phase 0 ready):**
- Tier-based position sizing (Section 8)
- Per-strategy stop methodology (12 exit methods, full detail in PROJECT_PLAN_ARCHIVE.md)
- Trailing stop + 5 circuit breakers
- Regime-conditional rules: shorts require VERY HIGH tier in bull regime; long size 0.5× in crisis
- earnings_tolerant strategy attribute (DECISION-013 REVISED)

**Pending decisions (Group C):**
- DECISION-018: cooldown after stop-out
- DECISION-019: liquidity filter timing
- DECISION-022: drawdown-aware position sizing (step function -5/-10/-15%)
- DECISION-023: vol-targeted (inverse-ATR) sizing
- DECISION-024: correlation-adjusted concentration limits

**Removed per prior approvals:**
- No open position caps or daily loss limits (replaced with crisis flagging)
- No correlation filter (replaced with regime-based context)
- No regime-based hard direction blocks
- No one-trade-per-ticker limit
- Mean reversion ATR multipliers raised from 0.5× to 1.0×

---

## 13. PIT Correctness — Non-Negotiable

Per DECISION-040: PointInTimeLoader structural framework wraps all data access during backtest. Every data fetch goes through the loader, which masks any future-dated rows. Regression tested via freezegun (DECISION-050) — fake "now" to past dates and assert no future leak.

This is the single most important architectural decision. Look-ahead bias killed prior efforts.

---

## 14. Workflow — Making Changes

Per CLAUDE.md + CHECKLIST.md (29 items):

1. **All decisions need explicit owner approval before implementation. No exceptions.** (CLAUDE.md)
2. **Recommendations require Assumption Validation** (CHECKLIST #26): list every factual claim, source it, verify if uncertain, state "Verified:" explicitly.
3. **Recommendations require Relevance Check** (CHECKLIST #27): state the question, state how the recommendation addresses it.
4. **Mistakes get added to LEARNINGS retroactively** (CHECKLIST #28).
5. **API runs follow STOP-EARLY-ON-BUDGET** (CHECKLIST #29): cost estimate → smallest test batch → manual review → mid → full, with hard stops at 80% and 100% of budget.
6. **PROJECT_PLAN.md changes require explicit owner approval** (L94 updated April 2026 — append-only restriction lifted, approval requirement preserved).
7. **AUDIT.md preserves full pass history.** Pass 38 Part B consolidated current state, but passes 1-37 remain immutable.

---

## 15. Tech Stack Summary

| Component | Choice | License | Source |
|---|---|---|---|
| Language | Python | — | — |
| Backtest engine | Custom (kept) | — | `backtest/engine/` |
| ICT / SMC signals | smartmoneyconcepts (joshyattridge, pin v0.0.27) | MIT | DECISION-045 |
| Fundamentals | OpenBB Platform + Polygon | OS | DECISION-005 |
| Performance analytics | QuantStats | Apache 2.0 | DECISION-047 |
| Dashboard (Stage 3+) | Streamlit | Apache 2.0 | DECISION-048 (deferred per 053) |
| IBKR integration | ib_async | BSD | DECISION-049 |
| Datetime mocking | freezegun | Apache 2.0 | DECISION-050 |
| S&P 500 historical | datasets/s-and-p-500-companies CSV | CC0 | DECISION-052 |
| Multi-agent orchestration | TradingAgents v0.2.4 (pin commit hash) | Apache 2.0 | DECISION-051 REVISED-3 |
| LLM (backtest) | OpenAI GPT-5.4-mini | proprietary API | DECISION-058 REVISED |
| LLM (live) | Anthropic Sonnet+Haiku 4.x | proprietary API | DECISION-058 REVISED |
| Storage | Parquet + filelock | OS | — |
| News | Polygon | $30/mo | DECISION-002 |
| PIT loader | Custom | — | DECISION-040 |
| Configuration | python-dotenv | OS | — |

All forks $0 licensing. Total monthly API cost (live trading): $117-195.

---

## 16. Current Status (April 2026)

**Done:**
- Stage 1 daily picks website (Phase 1A complete, deprecated as primary work)
- Comprehensive backtesting engine code (substantial — see `backtest/`)
- 38 audit passes producing 62 decisions and 206 documented bugs
- 5-tier confidence + position sizing + earnings_tolerant logic specified
- Architectural decisions for fork-existing strategy, TradingAgents adoption, GPT-5.4-mini for backtest, $300 budget with smoke test gating

**In progress:**
- Pass 38 architectural consolidation (this document is part of it)

**Next (sequenced, blocking):**
1. Resolve Group F decisions (4): 020 News API, 031 Codespace, 036 Audit cadence, 043 Retune framework
2. Resolve Group B decisions (3): 014 Phase 1B passing criteria, 015 Strategy correlation, 016 Threshold calibration
3. Resolve DECISION-062 (output schema translation when Group C resolves)
4. Bug triage Pass 1 — reclassify 206 bugs against new architecture in batches
5. Phase 0.A start: Quiver pre-cancellation repair scripts → Polygon News evaluation → prefetch pipeline

**Deferred:**
- HANDOFF.md generation (paused, owner request only)
- Group C/D/E decisions (parallel with Phase 0 implementation)

---

## 17. Cost Summary

### One-time
- Stage 2 backtest: ~$300 hard cap (DECISION-059)

### Monthly recurring (live trading, Stage 3+)
- Polygon: $30
- Quiver: $50-100 (pending Phase 0.A repair outcome)
- Anthropic agents: $40-50
- Hosting: $0-15
- Unusual Whales (Phase 1C+): $50
- Ortex (Stage 3+): $40
- **Total range:** $210-285/month at full stack

### Tools/libraries: $0 (all OS or built-in)

---

## 18. Open Items (Pointing to AUDIT.md for detail)

26 pending decisions across 7 groups (Pass 38 Part B Section A):
- Group B (3): Phase 1B-α validation methodology
- Group C (5): Risk management rules
- Group D (4): Strategy/regime adaptation
- Group E (5): Live trading operational
- Group F (4): Process/infrastructure
- Group G (2): Phase 0 sub-scope
- Group H (1): DECISION-062 output schema translation

206 bugs pending three-pass triage (Pass 38 Part B Section B):
- Pass 1: Reclassify against new architecture
- Pass 2: Prioritize by phase
- Pass 3: Fix during implementation with regression tests

---

## 19. Key Lessons Driving This Plan

Distilled from LEARNINGS.md (105 entries, full detail there):

- **L1**: Read code to understand. Run code to verify. Reading is never sufficient.
- **L11**: Pre-fetch everything. Never call APIs inside computation loops.
- **L44**: Producer/consumer key mismatch caught by zero of three audits — write integration tests on every data handoff.
- **L45**: Audits without tests catch zero bugs.
- **L86, L95, L102**: Cost overruns happen when batch test sequence is skipped.
- **L88**: Wikipedia is never a valid data source.
- **L94**: PROJECT_PLAN.md changes require explicit owner approval (append-only lifted April 2026).
- **L99**: 3.5× trade row inflation due to multi-strategy fires on same ticker — recalibrate sample size assumptions.
- **L100-L104**: Recommendations made without validating assumptions, without relevance check, without counting LLM call multipliers, without reading framework source.
- **L105**: Budget batch discipline must apply to EVERY API operation, not just the one that just lost money.

---

## 20. Glossary

- **Phase 0**: Pre-backtest architecture build (5 sub-phases A-E)
- **Phase 1B**: Old name for full backtest run (legacy term, now Stage 2)
- **Phase 1C**: Old name for agent integration (now part of Stage 2 / Stage 3 transition)
- **Stage 2**: Full backtest validation with new $300 two-stage plan
- **PIT**: Point-in-time. No future data leakage during backtest.
- **TradingAgents**: External LangGraph multi-agent framework (UCLA/MIT, Apache 2.0). Replaces our custom 6-agent pipeline.
- **Propagate()**: One TradingAgents decision cycle on one ticker on one date. ~11 LLM nodes, 15-22 actual LLM calls due to tool loops.
- **Smoke test gate**: Mandatory 10-candidate test before scaling per DECISION-060 + CHECKLIST #29.
- **earnings_tolerant**: Strategy attribute. Tolerant strategies trade through earnings; non-tolerant reduce size.
- **Tier**: Confidence tier (EXCEPTIONAL → AVOID). Drives position size.
- **5-tier rating**: TradingAgents Portfolio Manager output (Buy/Overweight/Hold/Underweight/Sell).
- **Group A-H**: Pending decision groups per Pass 37/38 Part B.

---

*End of PROJECT_PLAN.md current state. For pre-April-2026 detail (60-strategy descriptions, 274-field signal universe, full glossary, restored sections), see PROJECT_PLAN_ARCHIVE.md.*
