# Engineering Learnings — Universal Principles
**Author:** Jeet Mehta
**Compiled:** April 2026 — Stock Picks & Automated Trading System
**Purpose:** Universal engineering principles from real mistakes. Apply to all future projects.

Tags: [testing] [data] [api] [process] [architecture] [git] [cost] [agents] [infrastructure]

---

## PART 1 — TESTING & VERIFICATION

### L45 — Audits must be executable, not conversational [testing]
Three comprehensive code audits were conducted by reading code. The most critical bug (all agent smart money context being empty dicts — L44) survived all three because it was invisible to reading but caught in 30 seconds by running a single print statement. **Reading code that looks correct is not the same as code that works correctly.** After every audit, write a test for every flagged item. A data flow is only verified when a test asserts it end-to-end.

### L46 — Producer/consumer key coherency must be tested in code [testing]
Function A returned `{composite_signal, score, details}`. Function B expected `{congressional_sig, insider_sig, institutional_sig}`. Three audits examined both files and concluded the integration was correct. It wasn't. **For every data handoff between functions, verify in running code: what keys does the producer return, what keys does the consumer expect, do they match.** Every inter-module data handoff gets an integration test.

### L47 — Documentation and code must be compared directly [testing]
PROJECT_PLAN.md correctly documented two walk-forward windows. The code implemented one. Survived three audits because each checked the plan and the code separately — never comparing them. **A project plan that says one thing while the code does another is worse than no documentation — it creates false confidence.** For every documented behaviour, have a test that asserts it.

### L48 — Time-series accumulation fields require explicit verification [testing]
`max_adverse_excursion` was documented as "worst % during the hold period." The code computed it from a single day's bar. **Field names that imply accumulation (max, min, worst, best over a period) require a test verifying accumulation across multiple time steps.** Not just a single computation.

### L26 — Checklist existed but wasn't being followed [process]
CHECKLIST.md was created and added to CLAUDE.md but repeatedly not consulted before taking actions. Multiple mistakes that the checklist would have caught still occurred. **A checklist only works if it is explicitly run before every action. Having it documented is not the same as using it.** Make checklist compliance visible and auditable.

### L35 — Checklist not enforced — no visible compliance statement [process]
Same as L26 but deeper: the checklist needs to be stated visibly before every significant action so it's auditable. "Checklist: ✅ thought through, ✅ plan shown, ✅ within phase, ✅ helps ask, ✅ risks flagged, ✅ approval received."

---

## PART 2 — DATA & APIs

### L9 — API tier not verified before building [api]
Built a full 509-ticker download script for insider data before verifying the endpoint worked on the current plan. All 509 returned 0 records. Wasted download time and API quota. **Always test one call per endpoint before writing any code. Verify tier access explicitly.** This is CHECKLIST item 12.

### L10 — Wrong API endpoint URLs [api]
Used `/historical/insidertrading/` — returned 404. Correct endpoint was `/live/insiders?ticker=`. **Always find endpoint URLs from the official package source or documentation, not assumed paths.** Test one call before building.

### L11 — Agents calling live APIs during backtest loop [api]
Started Phase 1B with agents calling Quiver, FRED, and sentiment APIs live on every candidate every day. Each call took 35 seconds. Estimated 40-60 hours runtime. **Never call external APIs inside a backtest loop. Pre-fetch all data first, read from disk during backtest.** Pre-fetch architecture reduced agent runtime from 35s to ~2s per candidate.

### L37 — API free tier lookback not verified before downloading [api]
Built and ran Finnhub pre-fetch for 2022-2024 data. Free tier only returns ~1 year of historical news. All 509 tickers downloaded "successfully" but all files were empty. Discovered only after 5 GitHub Actions batch runs completed. **Always test the API with a date range call before building the full pre-fetch. Check: does a 2022 date range return data or empty?** CHECKLIST item 12 applies to every data type.

### L43 — Existing APIs checked last, new APIs added first [api]
Planned and partially implemented Finnhub for news sentiment without first checking if Alpha Vantage (already in use for Stage 1) also provided news with sentiment scores. It did — with better AI-powered scores, full historical coverage, and for free. **Always check existing API providers for additional endpoints before adding new providers.** The full feature set of every active API should be reviewed before adding a new one.

### L7/L8 — Hardcoded sample data instead of real data [data]
AAII sentiment had 15 hardcoded readings for 782 trading days. CNN Fear & Greed had 16. Agents were nearly blind. **Always verify data coverage before building any system around it. 15 points for 3 years is a placeholder, not a dataset.** Build for full coverage from the start.

### L6 — Web scraping for core data [data]
Used Wikipedia for S&P 500 list — blocked by Codespaces network allowlist. **Never rely on web scraping for core data used by the production system. Use committed static files or verified API endpoints.** Data sources must work in all deployment environments.

### L44 — Producer/consumer key mismatch — all SM context was empty [data]
`smart_money_score()` returned `{composite_signal, score, details}` but the agent pipeline expected `{congressional_sig, insider_sig, institutional_sig, smart_money_composite}`. Congressional, insider, and institutional data were downloaded and cached correctly but never reached the agents. **Verify producer output keys match consumer expected keys in running code — not by reading both files separately.**

---

## PART 3 — ARCHITECTURE & DESIGN

### L27 — Backtest mirroring principle not established early [architecture]
News sentiment was planned for live trading but initially excluded from backtesting. Discovered late that the backtest wouldn't reflect live conditions. **From day one: every data source, signal, and API used in live trading must be in the backtest. If it is not backtested, it is not validated.**

### L28 — Key fields not designed upfront [architecture]
Sector information was in the CSV from the beginning but never passed into the engine, dataclasses, or agents. Required late-stage changes to OpenTrade, ClosedTrade, backtest.py, and pipeline.py. **Think through all data fields needed at design time. Retrofitting fields into dataclasses causes cascading changes across multiple files.** Design the data model before building.

### L38 — Agent given the rules it's supposed to derive [agents]
The Decision Agent prompt included the explicit confidence tier matrix. The agent wasn't reasoning — it was pattern-matching to rules we gave it. **Agents should derive scores independently. Giving an agent the mapping rules it's supposed to derive defeats the purpose.** The tier mapping should happen in code after the agent returns a raw score.

### L39 — Agent temperature not set — non-deterministic backtest [agents]
Agent API calls didn't set `temperature` parameter. Default is 1.0 (stochastic). Same inputs could produce different confidence tiers on different runs. **Set temperature=0 for all backtest agent calls. Backtest results must be reproducible — same inputs must produce same outputs.**

### L40 — Thresholds undefined — any value passes [architecture]
Smart money lift passing criterion had no numeric threshold. A strategy showing 0.1pp lift would pass the same as one showing 8pp. **Every passing criterion must have a specific numeric threshold that is statistically meaningful. "Measurable improvement" is not a threshold.**

### L36 — Stop simulation used close not intraday low [architecture]
Trailing stop checked `today_close <= trailing_stop`. A stock dipping below stop intraday and recovering would not be stopped out. Real stop orders trigger when price trades through the stop at any point during the day. **Always use daily low/high for stop trigger checks. Using close produces optimistic bias (~2-4pp higher win rate than realistic).**

---

## PART 4 — PROCESS & WORKFLOW

### L21 — Jumped ahead of current phase [process]
Downloaded full S&P 500 cache for Phase 1B before Phase 1A results were reviewed. **Never jump ahead of the current phase. Each phase requires explicit owner approval. The phases exist precisely to validate before scaling.**

### L20 — Modified owner document without approval [process]
Rewrote CLAUDE.md from 128 to 62 lines without showing diff or getting approval. Removed useful context. **CLAUDE.md is the owner's document. Never modify without showing exact before/after diff and receiving explicit approval.** Applies to all governance documents.

### L29 — Wrong cost and runtime estimates [process]
Estimated Phase 1B at 3-4 hours and ~$16 USD. Actual was 40+ hours and ~$115 USD. Gave confident estimates without validating against actual timing. **Never give cost or runtime estimates without first measuring one actual call and extrapolating. Always show the full calculation with units.**

### L32 — Cost formula had unexplained divisor [process]
Used `days × max_cands × $0.021 / 10` — the `/10` was incorrect and produced a 10× underestimate. **Always validate cost formulas before presenting them. Show the full breakdown: calls × cost_per_call × 6_agents = total. Never use an unexplained divisor.**

### L18 — No batch testing before full Phase 1B run [process]
Attempted to run full Phase 1B on 509 instruments without first testing on 25 tickers for 1 month. **Always validate the full pipeline on a small sample before scaling. Catch bugs and bad agent outputs cheaply before spending $100+ on a full run.**

### L24 — Paid run started without complete data [process]
Started Phase 1B agents with AAII at 15 hardcoded points, no news sentiment, no pre-fetched smart money data. Spent ~$3 CAD on agent calls that produced low-quality outputs. **Never start a paid agent run without verifying all data sources are complete and correct. Run the pre-run validation script first.**

---

## PART 5 — INFRASTRUCTURE & GIT

### L1 — Deployment environment network restrictions not checked [infrastructure]
Assumed all external APIs accessible from Codespaces. Wikipedia and several API endpoints were blocked by the Codespaces allowlist. **Always test every new API endpoint from the actual deployment environment before building integrations.** Don't assume network access.

### L2 — Dependencies not persisted across environment restarts [infrastructure]
Codespace loses all pip installs on restart unless in devcontainer.json. Multiple runs produced no cache files because pyarrow was missing. **Pin all dependencies in devcontainer.json or requirements.txt. Dependencies not pinned are dependencies that will break on the next restart.**

### L3 — Cache not committed = lost on restart [infrastructure]
Downloaded 67 instruments, Codespace restarted, lost everything. Repeated 3+ times. **Any file not committed to git is lost when a cloud environment restarts. Commit immediately after every download. Never assume local files survive restarts.**

### L13/L22 — Parallel git pushes always conflict [git]
Ran parallel GitHub Actions batches that all tried to push to main simultaneously. Only one succeeds; others get rejected. Required multiple reruns. **Never run parallel workflows that all push to the same branch. Sequential is slower but reliable. Always use `git pull --rebase` before push.**

### L31 — git reset --hard wiped uncommitted data [git]
Instructed owner to run `git fetch origin ; git reset --hard origin/main` which wiped locally completed Quiver data that hadn't been committed. **Before any `git reset --hard`, always run `git status` first. If uncommitted work exists, commit it before resetting. The sync command is: `git status` → commit if needed → then reset.**

### L34 — Built solution for wrong environment [infrastructure]
Created a PowerShell script for a user who consistently uses Git Bash on Windows. PowerShell lacks git on PATH, doesn't support `&&`, and blocks script execution. Made 3 consecutive errors. **Always identify the exact working environment before building any script or command. Test in the target environment, not assumed.**

### L33 — Wrong command separator for shell environment [infrastructure]
Repeatedly used `&&` in commands for a Windows PowerShell user. PowerShell uses `;` not `&&`. **Always identify the terminal environment before giving commands. Use `;` which works in both PowerShell and bash when in doubt.**

---

## PART 6 — COST & SCOPE MANAGEMENT

### L42 — Broker not checked for geographic availability [architecture]
Listed Alpaca as Stage 4 broker throughout the project plan without checking Canadian availability. Alpaca serves US accounts only. **Always verify broker geographic availability, regulatory requirements, and commission structure before including in any plan.** For Canadian investors trading US equities: IBKR Canada.

### L30 — Token savings claimed for wrong environment [process]
Recommended reducing CLAUDE.md claiming it would reduce token usage without thinking through which environment loads it. Claude Code on laptop loads CLAUDE.md every session — removing content costs tokens there. **Always identify which environment a change affects before claiming a benefit. A saving in one context may be a cost in another.**

### L41 — No benchmark comparison in initial design [architecture]
All strategy performance reported in absolute terms with no comparison to SPY buy-and-hold, no Sharpe ratio, no Calmar ratio. A strategy returning 20% over 4 years looks good until SPY returned 50%. **Every strategy backtest must be benchmarked against buy-and-hold and include risk-adjusted metrics. These are industry standard requirements, not optional.**

---

## PART 7 — RECURRING THEMES (most important lessons)

**Theme 1 — Running code beats reading code**
The most expensive bugs in this project (L44, L47, L48) were invisible when reading but obvious when run. Every integration point needs a test. Audits without executable validation are incomplete.

**Theme 2 — Test one before building for all**
Applies to every API endpoint, every data download, every new integration. One test call costs seconds; building the wrong thing costs days. CHECKLIST item 12 exists for this reason.

**Theme 3 — Commit early, commit often**
Cloud environments don't persist local state. Every download, every result, every cache file must be committed to git immediately. The "commit and push" habit eliminates an entire class of data loss bugs.

**Theme 4 — Pre-fetch everything, query nothing during computation**
No external API calls inside computation loops. Pre-fetch all data to disk, read from disk during computation. This makes computation fast, deterministic, and resilient to network failures.

**Theme 5 — Document decisions at decision time**
Decisions made in conversation but not written down get re-debated or forgotten. Every architectural decision, threshold value, or design choice belongs in PROJECT_PLAN.md or config.py at the moment it's made.

---

## QUICK REFERENCE — Before Every Session

1. Run `python backtest/tests/run_all_tests.py` — all tests must pass
2. Run `python scripts/validate_phase1b_data.py` — before any backtest run
3. Check `git status` before any sync operation
4. Verify API access with one test call before building any integration
5. State checklist compliance before every significant action
