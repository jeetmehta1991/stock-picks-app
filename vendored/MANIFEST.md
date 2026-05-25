# Vendored External Libraries

Per **DEC-045** (fork-first architecture; Pass 27 RESOLVED-DECIDED) + **DEC-508** + **CHECKLIST #71** (external library fork integration mandate Pass 53).

External libraries are forked into `vendored/` with pinned upstream commit hashes. They are NOT installed from PyPI directly — we use editable installs against this directory so the version is reproducibly locked.

## Forked libraries

### smartmoneyconcepts

| Field | Value |
|---|---|
| **Upstream URL** | https://github.com/joshyattridge/smartmoneyconcepts |
| **Upstream version (PyPI)** | 0.0.27 |
| **Pinned commit hash** | `1b62fd6c41e1f508e7ed76831a039fa4c82d42f6` |
| **Short hash** | `1b62fd6` |
| **Commit date** | 2026-04-03 |
| **Forked date** | 2026-05-05 (Pass 53 Sprint 0A Batch 15 kickoff) |
| **License** | MIT (see `vendored/smartmoneyconcepts/LICENSE`) |
| **Install** | `pip install -e vendored/smartmoneyconcepts` |
| **Phase A status** | IN PROGRESS — Tier 1 unit tests scaffolded; PIT regression scaffolded; ~10/100 tests written |
| **Phase B status** | NOT STARTED — pending Phase A completion + Dashboard 2 (DEC-200) |
| **Phase C status** | NOT STARTED — pending Phase B completion |

**API surface (smc class methods):**
- `fvg(ohlc, join_consecutive=False)` — Fair Value Gap detection
- `swing_highs_lows(ohlc, swing_length=50)` — Swing high/low identification (precursor to BOS/CHoCH)
- `bos_choch(...)` — Break of Structure / Change of Character
- `ob(...)` — Order Block
- `liquidity(ohlc, swing_highs_lows, range_percent=0.01)`
- `previous_high_low(ohlc, time_frame='1D')`
- `sessions(...)`
- `retracements(ohlc, swing_highs_lows)`

**Phase A test files:**
- `backtest/tests/test_smartmoneyconcepts_unit.py` — Tier 1 unit tests (synthetic OHLCV)
- `backtest/tests/test_smartmoneyconcepts_pit.py` — Tier 1 PIT correctness regression (freezegun)
- `backtest/tests/test_smartmoneyconcepts_integration.py` — Tier 2 integration (PENDING)
- `backtest/tests/test_smartmoneyconcepts_performance.py` — Tier 2 performance (PENDING)
- `backtest/tests/test_smartmoneyconcepts_statistical.py` — Tier 3 statistical sanity (PENDING)
- `backtest/tests/test_smartmoneyconcepts_adversarial.py` — Tier 3 adversarial random walk (PENDING)
- `backtest/tests/test_smartmoneyconcepts_xvalidation.py` — Tier 3 cross-validation (PENDING)

**Build sequence (Phase A → B → C per DEC-508 + CHECKLIST #71):**
1. Phase A — All Tier 1 + 2 + 3 tests pass; ≥90% coverage; library NOT imported outside test files; owner approval → Phase B
2. Phase B — Library imported; signals computed for full universe → `data_prefetch/ict_smc/{ticker}.parquet` but strategies disabled; Dashboard 2 (DEC-200) launched; owner validates 20-50 signals; PIT regression on full universe; owner approval → Phase C
3. Phase C — Strategies enabled; A/B vs baseline; DEC-084 lookahead red-flag check; walk-forward per DEC-505 (4 OOS folds × 1y)

**Reproducibility:**
To reproduce the exact library state at fork point:
```bash
cd vendored/smartmoneyconcepts
git checkout 1b62fd6c41e1f508e7ed76831a039fa4c82d42f6
```

If upstream commits made AFTER our pinned hash become relevant, owner approval required to update pin (re-running Phase A tests against new commit hash).

**License compliance:**
MIT licensed. Source attribution preserved in `vendored/smartmoneyconcepts/LICENSE`. Our project is fork-first per DEC-045; the fork is a TOOL we depend on, not a dependency we redistribute.

### tradingagents

| Field | Value |
|---|---|
| **Upstream URL** | https://github.com/TauricResearch/TradingAgents |
| **Upstream version (pyproject)** | 0.2.5 |
| **Pinned commit hash** | `61522e103e61601c553b4544abcd53fa7ebf9f1d` |
| **Short hash** | `61522e1` |
| **Commit date** | 2026-05-17 |
| **Commit subject** | `fix(llm): skip Anthropic effort kwarg on non-supporting models (#831)` |
| **Forked date** | 2026-05-25 (Pass 53 Sprint 7 Batch 349 kickoff) |
| **License** | Apache 2.0 (see `vendored/tradingagents/LICENSE`) |
| **Paper** | arXiv:2412.20138 (TauricResearch, UCLA/MIT, 2025) |
| **Install** | `pip install -e vendored/tradingagents` (requires Python 3.10-3.13; **NOT compatible with Python 3.14 today** because langchain-core 0.3.81 pulls C-extension deps that have no 3.14 wheels) |
| **Phase A status** | KICKOFF — source vendored; Tier 1 tests not yet written; langgraph_pipeline.py wrapper not yet built |
| **Phase B status** | NOT STARTED |
| **Phase C status** | NOT STARTED |

**Package layout (`vendored/tradingagents/tradingagents/`):**
- `agents/analysts/` — Market / Fundamentals / News / Social analyst nodes
- `agents/researchers/` — Bull / Bear research nodes (debate)
- `agents/managers/` — Research Manager + Portfolio Manager
- `agents/risk_mgmt/` — Aggressive / Conservative / Neutral risk debaters
- `agents/trader/` — Trader decision node
- `agents/utils/` — Memory / agent state / agent utilities
- `agents/schemas.py` — Pydantic schemas for AgentState
- `graph/` — LangGraph wiring (analyst_execution, conditional_logic, propagation, reflection, signal_processing, trading_graph, checkpointer)
- `dataflows/` — Built-in data adapters (alpha_vantage, reddit, stockstats, stocktwits, yfinance) — **NOTE: we override these with project-specific toolkits per DEC-507 wiring matrix; upstream dataflows are NOT used in our system**
- `llm_clients/` — Anthropic / OpenAI / Google adapters
- `default_config.py` — default agent prompts + model assignments

**Why this fork (per AUDIT.md L12681):**
"Already implements EXACTLY the architecture we built" (11-agent LangGraph: 3 analysts + Bull/Bear debate + Research Manager + Trader + 3 Risk Debaters + Portfolio Manager + Reflection). DEC-057 RESOLVED-DECIDED Pass 26 adopted upstream framework rather than maintaining our own. DEC-459 Option C Hybrid (Pass 53) integrates this framework as the 11-agent backbone, with our project-specific data toolkit injection via state augmentation per TRADINGAGENTS_DATA_AUDIT.md.

**Phase A scope (next batches):**
- Tier 1 unit tests: each graph node's pure function (input AgentState → output partial AgentState)
- Tier 1 schema tests: AgentState fields, transitions
- Tier 2 integration: `backtest/agents/langgraph_pipeline.py` wraps `TradingAgentsGraph` with our toolkit + data injection
- Tier 3 statistical: end-to-end decision repeatability with fixed seed; cost projection vs DEC-459 ~$116 CAD/Phase-1B-α budget
- Tier 4 dashboard: agent reasoning preview in Dashboard 3 (Stage 3 prep)

**Build sequence (Phase A → B → C per DEC-508 + CHECKLIST #71):**
1. Phase A — Vendor scaffold + Tier 1 unit tests + langgraph_pipeline.py wrapper compiles + smoke run on 1 ticker × 1 day with mocked LLM responses; owner approval → Phase B
2. Phase B — Real Anthropic API calls on 1-3 tickers × 5-10 days; cost-tracker confirms <$3 smoke budget; signal-to-decision round-trip validated; owner approval → Phase C
3. Phase C — Phase 1B-α full launch with winners.parquet × Phase 1A-β survivors; A/B vs rules-only baseline; DEC-505 walk-forward gate

**Python compatibility caveat (CRITICAL):**
TradingAgents v0.2.5 deps (`langchain-core>=0.3.81`, `langgraph>=0.4.8`) currently lack Python 3.14 wheels. Local development on 3.14 cannot `pip install -e vendored/tradingagents`. Phase 1B-α execution must run on Hetzner with Python 3.12 (or wait for upstream wheel publication). Local Phase A unit tests can mock LLM clients and exercise pure-Python graph wiring without requiring the full install.

**Reproducibility:**
```bash
cd vendored/tradingagents
git checkout 61522e103e61601c553b4544abcd53fa7ebf9f1d
```

**License compliance:**
Apache 2.0. Source attribution + NOTICE preserved in `vendored/tradingagents/LICENSE`. Per Apache 2.0 §4, redistribution of the source requires this LICENSE + NOTICE preservation; our use is internal (not redistribution).
