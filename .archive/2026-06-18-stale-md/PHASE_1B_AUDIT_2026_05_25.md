# Phase 1B Comprehensive Audit — 2026-05-25

**Source (per CHECKLIST #77 canonical-source attribution):**
- Code paths audited: `backtest/agents/pipeline.py` + `backtest/agents/agent_gate_config.py` + `scripts/run_phase_1b_alpha*.py`
- Spec docs cross-referenced: `TRADINGAGENTS_DATA_AUDIT.md` (DEC-507 wiring matrix), `PROJECT_PLAN.md §3.10`, `AUDIT_INDEX.md` (DECISION-459 status)

**Created:** Batch 345 (per owner directive "Do a comprehensive review of the Phase 1B code and run everything through the testing pyramid")
**Author:** Audit by Claude Code
**Status:** AUDIT FINDINGS — actionable defect list + 13-tier pyramid coverage matrix

## Executive summary

🔴 **Critical finding: Phase 1B-α is largely STUB code, not production-ready.** The current `scripts/run_phase_1b_alpha*.py` files validate config + budget + winners.parquet existence but **do not actually execute the 11-agent pipeline**. The required `langgraph_pipeline.py` and vendored TradingAgents library **do not exist** in this repo.

The 48-hour Phase 1B-α target communicated in the prior turn is **not achievable** with current code state. Building the missing infrastructure is multi-week Sprint 7 work per PROJECT_PLAN.md §3.10 estimate (76-85 engineering days, the largest sprint in the plan).

## What exists today

| Component | State | Purpose |
|---|---|---|
| `backtest/agents/pipeline.py` (795 lines) | ✅ Functional but **simplified 6-role architecture**, not 11-agent | Direct Anthropic API calls for Technical/Fundamental/Sentiment/Risk/Bull-Bear/Decision roles |
| `backtest/agents/agent_gate_config.py` (148 lines) | ✅ Functional | DEC-459 Option C Hybrid Architecture: 5 AgentMode types (FULL_WITH_VETO, NO_RISK, ANALYSTS_ONLY, RULES_ONLY, CONSENSUS_REQUIRED); arm A/B/C configs for A/B testing |
| `scripts/run_phase_1b_alpha_smoke.py` (100 lines) | ⛔ **STUB** — validates pre-flight only | Loads winners.parquet, estimates cost, writes manifest.json. **Does NOT execute agents.** Per line 92-94: "wire to LangGraph pipeline (deferred to post-1A-beta)" |
| `scripts/run_phase_1b_alpha_demo.py` (66 lines) | ⛔ **STUB** | Same pattern — pre-flight only |
| `scripts/run_phase_1b_alpha.py` (119 lines) | ⛔ **STUB** — explicit note at line 110-114 | "Full agent execution requires Phase 1B Sprint 7 langgraph_pipeline.py" |
| `TRADINGAGENTS_DATA_AUDIT.md` | ✅ Spec doc | DEC-507 11-agent × data-source wiring matrix; identifies all toolkit + state-injection gaps |
| `vendored/smartmoneyconcepts/` | ✅ Vendored | smc library for ICT/SMC chart signals |
| `vendored/tradingagents/` | ❌ **NOT VENDORED** | Required for the 11-agent LangGraph pipeline |

## What's missing

### A. Critical missing infrastructure

1. **`backtest/agents/langgraph_pipeline.py`** — the actual 11-agent LangGraph execution engine
2. **`vendored/tradingagents/`** — TradingAgents library fork per DEC-045 fork-first architecture
3. **`langgraph` Python package** — not in requirements.txt
4. **LangGraph state schema** per DEC-462-468 — augmented state dataclass with all the toolkit + risk-context + portfolio-state fields the 11 agents need

### B. Agent-data wiring gaps (per TRADINGAGENTS_DATA_AUDIT.md)

Per the DEC-507 wiring matrix, each of 11 agents has documented data dependencies. Current state has many GAPs marked:

**Market Analyst (Technical):** 8 GAPs
- OHLCV intraday (1H/4H for ICT) — Polygon Stocks Starter has it but not wired
- ICT/SMC primitives (FVG, BOS, CHoCH, OB) — smartmoneyconcepts fork vendored ✓ but not exposed via toolkit
- Chart pattern signals (DEC-355-362) — strategies exist but no toolkit injection
- Volume profile / VWAP — computable but not exposed
- Multi-timeframe regime context (DEC-106) — classifier exists, no toolkit injection
- Sector/peer relative strength — computable from sector ETFs (DEC-118)
- Liquidity / ADV (DEC-366) — filter exists, no toolkit injection
- Break-and-retest signal (BUG-111) — RESOLVED-IMPLEMENTED Batch 339; toolkit injection still needed

**Fundamentals Analyst:** 6 GAPs
- Income statement / Balance sheet / Cash flow PIT (CRITICAL Gap A) — Polygon Stocks Starter coverage NEEDS VERIFY
- Earnings call transcripts (HIGH Gap B) — not in current stack
- SEC filings (10-K/10-Q text; MEDIUM Gap B-related)
- Analyst estimates (consensus EPS/revenue; HIGH Gap C) — Quiver has rating changes only, not estimates
- Short interest (HIGH Gap D) — Ortex in plan, not wired
- Industry comparables — computable from Polygon sector data, not exposed
- Government contracts — BUG-284 OPEN

**News Analyst:** 2 GAPs
- Earnings call commentary (HIGH Gap B) — overlaps with Fundamentals B
- Macro news source (MEDIUM Gap E) — source unclear
- Twitter/X sentiment (LOW partial Social replacement) — Quiver Twitter paid, not wired

**Bull / Bear Researchers (debate):** 3 GAPs
- Smart money confluence signal (DEC-124) — exists, no state injection
- Regime context (DEC-106) — exists, no state injection
- Sector momentum context — computable, no state injection

**Trader:** 5 GAPs
- Liquidity / ADV (DEC-366), position sizing (DEC-021 3-tier), risk-adjusted slippage (DEC-092), borrow cost (DEC-399), per-ticker cooldown (DEC-018), per-ticker max-loss cap (DEC-135)
- Existing portfolio positions (BUG-095 — Portfolio class shipped Pass 53 Batch 20; toolkit injection still pending)
- Cash available — Portfolio dependency
- Risk debater quality, drawdown context — Portfolio dependency

**Risk Debaters (3):** Multiple GAPs around state injection per audit

**Portfolio Manager:** Multiple GAPs around portfolio state

**Reflection node:** Lower priority

### C. AgentGateConfig + A/B framework gaps

- DEC-216 A/B orchestrator integration partial
- DEC-211 per-agent ablation NOT implemented (state extraction needed)
- DEC-131 agent value-add gate (`agent_sharpe - rules_sharpe >= 0.2`) NOT enforced in code
- Continuous-Risk vs binary-veto A/B arm NOT implemented (REVISIT_AFTER_BACKTEST per DEC-459 directive #3)
- LangGraph state extraction for Risk debate confidence NOT implemented

### D. Pipeline.py (existing 6-role) gaps

Reviewed `pipeline.py` for correctness:

1. **No tests in `backtest/tests/`** specifically targeting `pipeline.py` — relies on graceful no-op when ANTHROPIC_API_KEY missing
2. **Cache pattern (`_agent_cache_key` / `_load_agent_cache` / `_save_agent_cache`)** uses file-based cache at `backtest/agents/cache/` — works but no eviction policy; current cache has ~7,000+ files
3. **`_call_claude`** has 1.5-sec delay for rate-limiting but no retry-with-backoff for transient API errors
4. **`_parse_json_response`** uses regex extraction — could fail silently on malformed JSON; would benefit from try/except wrapping that warns rather than returns empty dict
5. **`run_full_agent_pipeline`** orchestrates 6 sub-agents; output schema partially documented but not pinned by a typed dataclass; downstream consumers parse the dict shape ad-hoc

## 13-tier pyramid coverage for Phase 1B (current)

| Tier | Coverage | Notes |
|---|---|---|
| 1 Unit | 0% | No `test_pipeline.py` exists |
| 2 Smoke | 0% | No smoke test on agent_gate_config / pipeline |
| 3 Integration | 0% | No integration tests on agent-to-engine wiring |
| 4 System | 0% | Phase 1B-α full has never run |
| 5 Functional | 0% | No agent prompt validation against golden outputs |
| 6 Regression | N/A | No baseline to regress against |
| 7 Data integrity | Partial | TRADINGAGENTS_DATA_AUDIT.md exists as the wiring matrix (spec) but verification tests not built |
| 8 Performance | 0% | No cost/latency benchmark on the agent pipeline |
| 9 Acceptance | Partial | Cost ceilings ($3 / $10 / $50-150) defined; gate-pass criteria documented |
| 10 Contract | 0% | No API surface tests for `pipeline.py` or `agent_gate_config.py` |
| 11 E2E | 0% | Phase 1B-α end-to-end has never been executed |
| 12 Dashboard | N/A | Dashboard 3 spec (DEC-201) exists but not built |
| 13 Walk-forward | N/A | No agent-vs-rules walk-forward delta evaluation |

**Net coverage: ~5% across the 13 tiers.** This is a substantial Phase 1B engineering deliverable, not a verification gap to be closed in a single session.

## Critical bugs / logical errors / data issues found

### CRITICAL

| # | Issue | Evidence | Fix |
|---|---|---|---|
| **P1B-001** | langgraph_pipeline.py does not exist | `find . -name "langgraph*"` returns empty | Sprint 7 implementation deliverable |
| **P1B-002** | TradingAgents library not vendored | `vendored/` has only smartmoneyconcepts | Vendor TradingAgents per DEC-045 |
| **P1B-003** | All 3 Phase 1B-α scripts are STUBS | Source-code comments explicit at run_phase_1b_alpha.py:110-114 | Wire each to langgraph_pipeline.py once built |
| **P1B-004** | 30+ data wiring gaps per TRADINGAGENTS_DATA_AUDIT.md | Audit doc surveys 11 agents × ~3-5 GAPs each | Sprint 7 toolkit + state schema build |

### HIGH

| # | Issue | Evidence | Fix |
|---|---|---|---|
| **P1B-005** | pipeline.py's `_call_claude` lacks retry-with-backoff | No exception handler around `requests.post` | Add tenacity-style retry on transient 429/5xx |
| **P1B-006** | `_parse_json_response` returns empty dict silently on JSON parse failure | line 105 | Add explicit logger.warning + cache the failed payload for inspection |
| **P1B-007** | Agent cache has no eviction policy | ~7,000 files in `backtest/agents/cache/` | LRU eviction or TTL-based cleanup |
| **P1B-008** | No tests for `pipeline.py` | grep `test_pipeline` in `backtest/tests/` → empty | Add unit tests on each of 6 sub-agents with mocked responses |
| **P1B-009** | AgentGateConfig has no tests | grep `test_agent_gate` → empty | Add unit tests on the 5 AgentMode types + arm_a/b/c factory functions |

### MEDIUM

| # | Issue | Fix |
|---|---|---|
| **P1B-010** | `requirements.txt` missing `langgraph` package | Add when Sprint 7 begins |
| **P1B-011** | Phase 1B scripts use `if cfg is None: continue` which silently skips invalid arm names; should raise | Strict parsing |
| **P1B-012** | Budget estimate hardcodes "~50 trades per winning combo per arm" — empirical number from Phase 1A-β | Pull from trade_log.csv |
| **P1B-013** | `extract_phase_1a_beta_winners.py` exists per `scripts/` but never run on a Phase 1A-β output; winners.parquet schema unvalidated | Run it on the merged Phase 1A-β output + validate schema |
| **P1B-014** | DEC-131 agent value-add gate (`agent_sharpe - rules_sharpe >= 0.2`) not enforced in code | Add to Phase 1B-α post-analysis |

### LOW

| # | Issue | Fix |
|---|---|---|
| **P1B-015** | PROMPT_VERSION constant in pipeline.py never gets bumped automatically | Add CI hook or pre-commit |

## Recommended sequencing for Phase 1B-α activation

### Step 1: Honest re-scope owner conversation (THIS TURN)

- Acknowledge that Phase 1B-α is a SPRINT 7 work item (76-85 engineering days per PROJECT_PLAN.md §3.10), not 48-hour-achievable
- Either:
  - (a) Defer Phase 1B-α until proper Sprint 7 build
  - (b) Use the existing simplified 6-role `pipeline.py` for a "Phase 1B-α LITE" run on winners — get empirical agent-vs-rules data but with simpler architecture than the 11-agent spec
  - (c) Vendor TradingAgents now + spend the 76-85 days

### Step 2: If (b) is owner-approved — what to build

1. Wire `pipeline.py.run_full_agent_pipeline` into `scripts/run_phase_1b_alpha_smoke.py` (replace the stub with a real call)
2. Validate prompts against golden expected outputs on a small ticker subset
3. Run smoke ($3) → demo ($10) → full ($50-150) with real Anthropic API calls
4. Compare arm A (rules_only) vs arm B (full_with_veto) on the surviving Phase 1A-β winners

This is ~2-3 working days of focused work, not 48 hours but tractable.

### Step 3: If (a) or (c) — Sprint 7 build

Per PROJECT_PLAN.md §3.10, this is the planned multi-week effort. Sprint 7 work items include:
- Vendor TradingAgents
- Build `langgraph_pipeline.py`
- Build 5 toolkits (OurTechnicalToolkit, OurFundamentalsToolkit, OurNewsToolkit, OurTraderToolkit, OurRiskToolkit per Part D of audit)
- LangGraph state schema extension per Part E + DEC-462-468
- Wire all 30+ data sources per Part C gap analysis

## 13-tier pyramid for the existing pipeline.py (proposed Batch 346 scope)

If owner picks Option (b) above, the immediate test-pyramid work for `pipeline.py` + `agent_gate_config.py`:

| Tier | Specific tests to add |
|---|---|
| 1 Unit | 6 sub-agent runners × mocked Anthropic response × expected output shape (~12 tests) |
| 1 Unit | 5 AgentMode enums × correct active_agents() composition (~5 tests) |
| 1 Unit | _agent_cache_key collision tests (~3 tests) |
| 2 Smoke | Single-ticker single-as-of smoke (with mocked Anthropic) |
| 3 Integration | Cache load/save round-trip; cache_hit/cache_miss paths |
| 5 Functional | Each agent's prompt produces well-formed JSON; downstream parse succeeds |
| 6 Regression | Existing test suite stays green |
| 7 Data integrity | Each agent's input dict has expected keys present |
| 8 Performance | Cache hit < 1ms; Anthropic call < 30s p99 |
| 9 Acceptance | Match TRADINGAGENTS_DATA_AUDIT.md spec on which signals reach which agent |
| 10 Contract | `run_full_agent_pipeline` signature + return-shape pinned by typed dataclass |
| 11 E2E | Phase 1B-α LITE smoke run end-to-end on 1 winner × 5 days |
| 12 Dashboard | Skip (no dashboard for Phase 1B-α LITE) |
| 13 Walk-forward | Skip (no rerun comparison until full Phase 1B-α LITE landed) |

Total estimated new tests: ~40-60. Effort: ~1-2 working days.

## Owner decisions required

1. **Phase 1B-α scope decision:** (a) defer, (b) LITE via simplified pipeline.py, or (c) full Sprint 7 build?
2. **48h commitment:** Reduce to "Stage D + Phase 1A-β re-run complete in 48h" (achievable) OR keep "Phase 1B-α complete in 48h" with option (b) LITE accepted as scope?
3. **Bug fix prioritization:** Should I implement P1B-005 through P1B-009 (the HIGH-priority pipeline.py issues) in upcoming batches even if Phase 1B-α full build is deferred?
4. **Test pyramid build-out:** Spend the ~40-60-test ~1-2-day investment on pipeline.py + agent_gate_config.py NOW so the existing code is at least under-test? Even if we don't use the 11-agent path, the existing 6-role pipeline is reusable and currently 0% covered.

## Cross-reference with prior commitments

- BUILD_PLAN_PROGRESS.md "Day 8 (May 27)": "Phase 1A-β verdict extracted [PARTIAL]" + "Phase 1B-α smoke runner [DONE]" + "Phase 1B-α demo runner [DONE]" — DONE label was misleading; scripts exist but are STUBS not runnable pipelines
- BUILD_PLAN_PROGRESS.md "Day 9 (May 28)": "Phase 1B-α full runner [DONE]" + "Actually launched [PENDING]" — also misleading on [DONE] label
- AUDIT_INDEX `DECISION-459` Option C Hybrid: PARTIAL-IMPL-HELPER-ONLY status confirms the gap
- `feedback_wired_means_engine_consumed.md` memory rule: applies directly — "Engine wiring deferred" = NOT RESOLVED-IMPLEMENTED, but Phase 1B-α has been labeled as if it were resolved
