# Stock Picks & Automated Trading System
**Stage:** 2 — Strategy Validation | **Phase:** 1B — Full backtest in progress
**Repo:** jeetmehta1991/stock-picks-app
**Docs:** `PROJECT_PLAN.md` (full detail) | `CHECKLIST.md` (pre-action) | `LEARNINGS.md` (lessons)

---

## Critical Rules

- **MANDATORY PRE-FLIGHT CHECKLIST (Pass 52 owner directive — no exceptions):** Every recommendation in every response must be preceded by a visible pre-flight verification block applying the full CHECKLIST.md (currently 55 items). Format:
  - Pre-flight executes BEFORE the recommendation is stated, not after
  - Each applicable checklist item explicitly noted as ✅ / ⚠ / 🔴 with brief evidence (grep output, audit cross-reference, project scope check)
  - Items NOT applicable to a given recommendation must be explicitly marked N/A — silent skipping is not allowed
  - If ANY item fails (returns 🔴), HALT — do not draft the recommendation; report the failure and ask for direction
  - Critical findings surfaced during pre-flight (existing-code violations, scope conflicts, prior-art duplicates, phase-scope errors) must be reported BEFORE the recommendation, with the recommendation revised to incorporate the finding
  - End-of-response compliance statement (per CHECKLIST #45) is the per-response gate; it does NOT replace per-recommendation pre-flight gates
  - Past failures: 6+ consecutive lapses in DEC-422 framework drafting (Pass 52 turns 1-6) where end-of-response self-check missed errors that pre-flight would have caught (sector concentration entry-vs-exit, phase scope, dynamic-vs-static framing, dimensional coverage gaps, hardcoded strategy count, hold-duration-as-input, schema missing R:R/ROI/profit factor, existing-code DEC-353 violation in fixed_3r_2r). Owner caught all 6 with common-sense questions. The pre-flight gate is the systematic fix.
  - Applies to: new recommendations, revisions to prior recommendations, scope expansions, batch reviews, framework proposals, sub-decision logging, schema/field additions
  - Does NOT apply to: pure logging actions (committing already-approved decisions to audit), git operations, simple acknowledgments, owner-direction responses where Claude is asking clarification rather than recommending

- **ALL decisions need explicit owner approval before implementation. No exceptions.**
- **All API runs costing money: small test batch → manual review → owner approval → scale. NEVER jump from "data ready" to "full run". Past mistakes (L86, L95) cost $150 in discarded work — same pattern, different operation, same outcome unless this discipline is mandatory. See CHECKLIST #13, #22, #23, #29.**
- Never change rules, filters, thresholds, or parameters without approval. Recommend only.
- Think through every action completely before suggesting it. Anticipate edge cases.
- Never jump ahead of the current phase. One instruction at a time.
- If something can go wrong, flag it proactively.
- Point-in-time data enforcement is non-negotiable.
- **Never use `git reset --hard` without running `git status` first. This has destroyed data twice (L49, L77).**
- **Run CHECKLIST.md before every suggestion or execution.**
- **MANDATORY (Pass 52): every response must end with a visible CHECKLIST compliance statement enumerating which items applied and were satisfied. No exceptions. If checklist was not consulted before responding, the response itself is non-compliant. Owner has authorized ending conversation if this rule is repeatedly violated.**
- For every proposed change, always provide a recommendation with clear reasoning and tradeoffs before waiting for approval.
- After every audit, validate by RUNNING CODE — not reading it.
- Run `backtest/tests/test_integration.py` and `backtest/tests/test_unit.py` before every phase run and after every significant code change (36/36 must pass).
- **Fork-first architecture** — for every new component, identify battle-tested libraries before proposing custom code. Default to forking unless integration cost > rebuild cost OR requirement is genuinely novel to this project. Custom code reserved for what's UNIQUE to our system (signal computation, agent prompts, risk context, earnings_tolerant logic, PIT semantics, validation methodology, the specific 72 strategies). Per L103: read library source before recommending. Per DEC-045 (RESOLVED Pass 27): use this approach across all phases. Already-adopted forks: smartmoneyconcepts (ICT), TradingAgents (multi-agent), QuantStats (analytics), Streamlit (dashboard), ib_async (broker), freezegun (tests), OpenBB+Polygon (fundamentals).

---

## Repo Structure

```
backtest/
  config.py              # universe, regimes, thresholds, position sizing
  run_phase1a.py         # entry point — --phase, --tickers, --no-news, --no-git flags
  data/
    cache.py             # Parquet cache + filelock for parallel writes
    universe.py          # 3-tier universe: get_sp500_constituents, get_extended_universe, get_full_live_universe
    sp500_tickers.csv    # Tier 1 — quarterly refresh via scripts/refresh_sp500_universe.py
    extended_universe.csv # Tier 2 — monthly refresh (Stage 3+)
    momentum_watchlist.csv # Tier 3 — monthly refresh (Stage 3+)
    fetcher.py           # yfinance OHLCV + fundamentals (Wikipedia REMOVED — L88)
    macro.py             # FRED yield curve, VIX (from OHLCV cache), DXY (UUP proxy)
    sentiment.py         # AAII, CNN Fear & Greed
    smart_money.py       # congressional, insider, 13F
  signals/
    technical.py         # 274 signal fields
    screener.py          # 60 strategies, 7 categories
  engine/
    backtest.py          # main loop, incremental checkpoints every 100 days
    exit_manager.py      # trailing stop + 5 circuit breakers
    exit_strategies.py   # 12 exit methods
    regime_filter.py     # classify_regime: bull/neutral/bear/crisis
    improvements.py      # walk-forward, transaction costs, slippage, survivorship
  agents/pipeline.py     # 6-agent pipeline (Haiku Phase 1B, Sonnet Phase 1C+)
  results/
    metrics.py           # 9 passing criteria + per-regime verdict matrix
    writer.py            # trade_log, backtest_results, strategy_regime_matrix.json
    site_generator.py    # daily site_picks JSON
scripts/
  generate_batch_splits.py     # prints 5-batch commands + 1-ticker test commands
  merge_batch_outputs.py       # merge 5 outputs, re-compute metrics, validate
  prepopulate_cache_index.py   # pre-fill index.json before parallel runs
  refresh_sp500_universe.py    # quarterly S&P 500 refresh (laptop only, slickcharts.com)
  refresh_extended_universe.py # monthly Tier 2 refresh (laptop only)
  build_momentum_watchlist.py  # monthly Tier 3 refresh (laptop only)
  validate_phase1b_data.py     # pre-run data completeness check
PROJECT_PLAN.md   # comprehensive reference — read first
CHECKLIST.md      # pre-action checklist — 21 items including universe refresh
LEARNINGS.md      # 89 lessons — L88: no Wikipedia, L89: universe staleness
```

---

## Passing Criteria (9 overall + per-regime verdict)

All 9 must pass overall for a strategy to advance. Additionally, each strategy gets a per-regime verdict (PASS/FAIL/INSUFFICIENT_DATA) for each of the 7 historical regimes. A strategy valid in crisis but not bull is deployed only during crisis — this is intentional.

| # | Criterion | Threshold |
|---|---|---|
| 1 | Win rate | ≥55% (high-vol sectors: ≥50%) |
| 2 | Profit factor | >1.3 (high-vol: >1.2) |
| 3 | Expected value | >0 |
| 4 | Win/loss ratio | >1.0 |
| 5 | Max drawdown | <20 pct-points (high-vol: <25) |
| 6 | Total ROI | >0% |
| 7 | Smart money lift | ≥3pp win rate improvement |
| 8 | Macro correlation | ≥5pp win rate diff |
| 9 | Min trades | ≥100 overall, ≥30 per regime |
| 10 | Per-regime verdict | PASS in ≥1 regime (not universal pass required) |

---

## Key Design Decisions

- **Risk profile:** medium-high risk, high return. Buy dips including in crisis.
- **Regime classification (real-time):** bull/neutral/bear/crisis via 20-day realised vol + SPY vs 200 EMA
- **Per-regime strategy library:** different strategies for different regimes — not universal strategies
- **Position sizing:** EXCEPTIONAL 5%, VERY HIGH 4%, HIGH 3%, MEDIUM-HIGH 1.5%, MEDIUM 0.75%, LOW skip
- **Exit:** atr_trail_1x (1× ATR trailing stop, checked against intraday low) — won 20/29 in Phase 1A v3 archive
- **Phase 1A restored Pass 53:** rules + smart money baseline (no agents) precedes Phase 1B agent overlay. Phase 1A → 1A-α (rules-only cube) → 1A-β (full-scale dry-run) → 1B (agents added) → 1B-α (combined cube). Owner gate at 1A-α (rules-only Sharpe ≥ 0.7 OOS) before $300 1B-α budget commits. See PROJECT_PLAN §3.6-3.10 + DETAILED_PROJECT_PLAN Parts 7.5/7.6/7.7.
- **Email** (not Telegram) for all trade approvals in Stage 4
- **Intraday trading:** completely separate future project — out of scope
- **Agent pipeline:** 6 agents (Technical, Fundamental, Sentiment, Risk, Bull/Bear Debate, Decision) at temperature=0. Haiku for Phase 1B (~$116 CAD). Sonnet for Phase 1C+.
- **News sentiment:** not_available at free tier. Proceed Phase 1B without news. Add Unusual Whales in Phase 1C instead.

---

## Approved Rules

| Rule | Value |
|---|---|
| Open position cap | Removed from backtest |
| Daily loss limit | Removed from backtest |
| Correlation filter | Removed from backtest |
| Regime hard blocks | Removed — crisis flagged but longs allowed (buy-the-dip) |
| One trade per ticker | Removed — all strategies fire independently |
| Crisis regime longs | Allowed at 50% size — flagged as `regime=crisis_CRISIS_FLAG` |
| Max candidates/day | 10 |
| Position sizing | Tiered: 5/4/3/1.5/0.75% by confidence tier |
| Agent tier upgrade | score ≥75 upgrades one tier |
| Agent tier downgrade | score ≤40 downgrades one tier |

---

## HARD RULES — Never Violate

### Git Safety
- **NEVER run `git reset --hard` without `git status` first.** Has destroyed data twice (L49, L77).
- **NEVER run any git destructive command during or after parallel batch runs without checking status.**
- All code goes to `claude-updates` branch, merged to main via push.

### Push & PAT Pattern (Pass 52 owner-approved Option 3)
- Repo URL: `https://github.com/jeetmehta1991/stock-picks-app.git`
- **Authentication:** Personal Access Token (PAT) cached in sandbox session.
- **Lifecycle (Option 3 per Pass 52 owner directive):**
  1. Owner issues a long-lived PAT (30-90 day expiration) at session start
  2. Claude caches PAT to `~/.git-credentials` for in-session reuse
  3. Sandbox is ephemeral — `/home/claude` resets between work sessions
  4. Owner re-pastes PAT at start of each new session
  5. Owner revokes PAT when project is paused or done
- **PAT settings (recommended):**
  - Name: `claude-sandbox-YYYY-MM-DD` or similar timestamp
  - Expiration: 30 days (re-issuable; long enough to avoid re-prompting per session, short enough to limit blast radius if leaked)
  - Type: Fine-grained PAT preferred over classic
  - Scope: Repository = `jeetmehta1991/stock-picks-app` only
  - Permissions: Repository → Contents = Read and write; Metadata = Read-only (auto-set)
- **Hard rules — NEVER violate:**
  - **NEVER commit the PAT to any tracked file.** PAT lives only in `~/.git-credentials` (untracked) or in the active session's `git remote set-url` config.
  - **NEVER write the PAT to any file under `/home/claude/stock-picks-app/`** (the repo working tree). That file would get caught by `git add` someday and pushed publicly.
  - **NEVER paste the PAT into AUDIT.md, LEARNINGS.md, CLAUDE.md, or any other repo file.** The pattern is documented here; the secret never is.
  - After each push, immediately reset the remote URL to remove the PAT from `.git/config` (which `git remote set-url <PAT-URL>` may have written): `git remote set-url origin https://github.com/jeetmehta1991/stock-picks-app.git`
- **Push cadence:** at meaningful checkpoints (theme closures, significant work milestones), not after every commit. Reduces re-issuance friction.
- **If push is rejected (remote ahead):** `git fetch origin main` → review remote commits → `git rebase origin/main` if file-change sets disjoint → push again. NEVER force-push without explicit owner approval.
- **Recovery if PAT compromised:** owner revokes PAT at github.com/settings/personal-access-tokens. Issues new one. Repaste in new session.

### Data Sources
- **NEVER use Wikipedia.** Historically blocked in Codespaces; not point-in-time; fragile (L88). Same fragility applies on local VS Code.
  - S&P 500 → `backtest/data/sp500_tickers.csv` refreshed quarterly via `scripts/refresh_sp500_universe.py` on LAPTOP using slickcharts.com
  - Never propose `pd.read_html('https://en.wikipedia.org/...')` for any purpose.
  - **One-time historical scrape exception (Pass 53 owner-granted, scoped):** Wikipedia + general internet browsing is permitted for ONE-TIME assembly of historical universe membership files (`historical_membership.csv`, `russell_1000_membership.csv`, `nasdaq_100_membership.csv`, `index_rebalance_events.parquet`) under these conditions: (i) laptop-local execution only, (ii) fallback source — primary is S&P DJI press releases / FTSE Russell / Nasdaq, (iii) manual verification before commit, (iv) not runtime — these scrapes happen pre-Sprint-1 to assemble static CSV inputs, never inside the backtest hot path. See AUDIT.md Pass 53 entries for exception scope details.

### CSV-first data architecture (Pass 53 owner directive — HARD RULE)
- **All input data and output data must live in CSV files (or Parquet for nested/binary data per DEC-491). No data should live exclusively in the codebase.** The code pulls data from CSV files; CSV is the source of truth.
- **Applies to:** universe lists (T1a/T1b/T1c/T2/T3 + ETFs), sector mappings, ticker overrides, calendar events, trade outputs, metrics outputs, regime classifications, strategy registers — anything that is data rather than parameter/logic/threshold.
- **Distinction from configuration:** Numerical thresholds (TRAILING_STOP percent, LIQUIDITY mins, position sizing tiers, slippage bps) and methodological choices (regime classifier formulas, statistical gates) ARE configuration/logic, NOT data — these can stay in code/config files. The line: if it's a *list of items*, *map of attributes*, or *historical record*, it's data → CSV. If it's a *behavior parameter* or *formula*, it's logic → code/config.
- **Past violations being corrected:** `ETFS_FULL` hardcoded in `universe.py` → `tier1_etfs.csv` (DEC-494 / commit `e257d160`). `etf_sectors` dict in `universe.py:get_sector_map()` → migrate to read from `tier1_etfs.csv` Sector column (queued). `SECTOR_OVERRIDES` dict in `scripts/refresh_sp500_universe.py` → could move to CSV (queued).
- **Apply when:** writing new modules that introduce hardcoded ticker lists / sector dicts / event calendars / known-good outputs; reviewing existing modules during sprint planning; adding new universe tiers or strategy categories. If you find yourself typing a Python list of tickers or a dict of attributes longer than 5 entries, stop and put it in a CSV instead.

### Universe Management
- `sp500_tickers.csv` must be refreshed quarterly (CHECKLIST item 19). If last commit >90 days old, flag before any run.
- New spinoffs above $10B market cap → add to Tier 2 immediately, don't wait for S&P 500 inclusion (SNDK waited 9 months — L89).
- Tier 2 (extended universe): monthly refresh in live trading.
- Tier 3 (momentum watchlist): monthly refresh in live trading, static for backtesting.

### Strategy Changes
- No strategy or rule changes without explicit owner approval. Every threshold, filter, and parameter change requires sign-off.
- The per-regime verdict system means a strategy that fails in one regime is NOT discarded — it is tagged for the regimes where it passes.

### Pre-Recommendation Checklist Application (Pass 52 owner-mandated standing rule)
**MANDATORY: Apply the full CHECKLIST.md as a pre-condition gate before stating EVERY recommendation. No exceptions.**

- Before each recommendation in any response, explicitly reference and verify each applicable checklist item.
- Items not applicable to a given recommendation must still be referenced (mark as N/A with reason). The act of referencing each item is what catches errors — skipping the reference is what allows pattern-match-without-verification failures.
- Verification format: per-recommendation pre-flight block showing checklist items + status + evidence (grep output, cross-references, math). NOT deferred to end-of-response compliance statement.
- End-of-response compliance statement (#45) remains required, but it is post-hoc. The pre-flight per-recommendation block is what actually catches errors before they become stated recommendations.
- This rule applies to: recommendations, proposed schemas, threshold values, scope claims, framework designs, dimensional inventories, ANY assertion of "this is what we should do." Does NOT apply to: factual answers to direct questions, verification reports of code state, status updates.
- Pattern lineage: 6 consecutive lapses in DEC-422 framework drafting (Pass 52) caught by owner because end-of-response compliance was post-hoc. Owner mandate: pre-flight per recommendation is the only way to make verification automatic.
- If a checklist item flags an issue, the recommendation must be REVISED before stated. Surfacing findings in pre-flight is success, not failure — it's the system working.
