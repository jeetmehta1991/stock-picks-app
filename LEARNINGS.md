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

### L49 — git reset --hard destroyed downloaded data twice [git]
**Mistake:** After Quiver gov_contracts/lobbying/wikipedia/wallstreetbets finished downloading (several hours of work), instructed owner to run `git fetch origin ; git reset --hard origin/main` before verifying the push had succeeded. The reset wiped all locally downloaded data. This exact mistake had already happened once and was documented as L31. It happened again.
**Root causes:**
1. The prefetch script's final push was silently failing (rejection due to diverged branches)
2. I gave `git reset --hard` without first checking `git status`
3. L31 existed in LEARNINGS.md but was not consulted before giving the command
**Rule:** NEVER give `git reset --hard` after any download or computation. The sequence is always: `git status` → if anything present, commit it first → then pull --rebase → then push. `git reset --hard` is only safe on a clean working tree with nothing to lose.
**Fix:** prefetch_quiver.py now verifies push succeeded after each data type and explicitly warns against `git reset --hard` if push failed.

---

## PART 8 — MISSING LESSONS (added April 25)

### L50 — Never call external APIs inside computation loops — pre-fetch everything [data] [api]
**Mistake:** The initial backtest design called Quiver, FRED, and sentiment APIs live inside the backtest loop — one call per candidate per day. With 509 instruments × 782 days × up to 10 candidates/day × 6 agents, this would have been millions of API calls. Each call took ~35 seconds. Estimated runtime: 40-60 hours.
**Principle:** Any data used repeatedly in computation must be downloaded once to disk before computation begins. During computation, read from disk only — never make network calls. This applies to backtesting, ML training, data pipelines, and any batch processing system.
**Rule:** If a function calls an external API and is called inside a loop, it must be refactored: extract the API call, pre-fetch to disk, then read from disk inside the loop.
**Impact here:** Pre-fetch architecture reduced agent runtime from ~35s to ~2s per candidate.

### L51 — Download granular data, not aggregates — you can always aggregate later [data]
**Mistake:** Initially stored only composite signals (e.g. `congressional_signal: "buy"`) rather than the raw underlying data (which representative, how much, when, what party). When we later needed to add congressional age-weighting, Senate vs House distinction, and amount-based weighting, we had to re-download everything.
**Principle:** Always download and store the most granular data available. Aggregates can be computed from granular data at query time. Granular data cannot be reconstructed from aggregates.
**Rule:** For every API response, store the complete raw record — not a summary. Add summary fields as computed columns on top of the raw data.
**Applies to:** Congressional trades (store each trade individually), insider filings (each Form 4), news articles (each article with sentiment score), earnings data (each estimate and revision).

### L52 — Validate API data structure before building the full pipeline [api]
**Mistake:** Built complete Quiver integration (checkpoint logic, parallel batches, commit logic) before verifying what the API actually returns in terms of column names, date formats, and data types. Discovered column name mismatches (`_get_quiver_data` vs `_load_prefetch` key differences) only during Phase 1B preparation.
**Principle:** Before building any data pipeline, make one real API call, print the full response, and verify every field you plan to use actually exists with the expected name and type.
**Rule:** `print(response.json())` before writing any code that consumes the response.

### L53 — Cache hits must be verified — empty cache is not the same as missing cache [data]
**Mistake:** Finnhub pre-fetch ran successfully (no errors, all 509 tickers "completed") but all resulting Parquet files were ~1012 bytes — empty DataFrames. The download appeared to succeed. Alpha Vantage pre-fetch showed the same pattern — 25 calls/day free tier exhausted after 4-5 tickers, rest returned empty with no error.
**Principle:** A successful API call that returns an empty response is not the same as a failed call. Always verify that downloaded files contain actual data, not just that the download process completed without errors.
**Rule:** After every pre-fetch, spot-check: open 3-5 random files and verify they contain rows. Add a validation step: `assert len(df) > 0, f"{ticker} cache is empty"`.

### L54 — Free API tier limits apply to the full project, not per-call [api]
**Mistake:** Alpha Vantage free tier says "25 calls/minute." We interpreted this as a rate limit and added 13-second sleeps between calls. The actual limit was 25 calls/day total. We exhausted the daily quota after 4-5 tickers (5 annual batches × ~5 tickers = ~25 calls).
**Principle:** For any API, verify ALL limit dimensions before building: calls per minute, calls per day, calls per month, data lookback window, records per call. One limit being acceptable doesn't mean the others are.
**Rule:** Test the complete workflow (not just one call) at small scale before building the full pipeline. Run 10 tickers first to estimate actual daily quota consumption.

### L55 — Static committed files beat network scraping for stable reference data [infrastructure]
**Mistake:** Multiple attempts to fetch the S&P 500 constituent list dynamically (Wikipedia scraping, yfinance, various APIs). Each failed in different deployment environments. The fix — committing `sp500_tickers.csv` as a static file — took 5 minutes and worked everywhere.
**Principle:** For data that changes infrequently (stock universe, sector classifications, exchange holidays, economic calendar dates), a committed static file is more reliable than any live API. It works offline, works in all environments, is version-controlled, and is instant to read.
**Rule:** If data changes less than once per month, consider a committed static file over a live API call.

### L56 — Point-in-time data violations are invisible until explicitly tested [data]
**Mistake:** Multiple point-in-time violations existed in the codebase (COT data using future data, economic calendar missing 2025 dates, survivorship bias not hold-adjusted) and survived multiple code reviews because they looked correct when reading the code.
**Principle:** Point-in-time violations — using data that wasn't available at the signal date — are the most damaging form of backtest bias and the hardest to spot by reading. They require explicit tests with known historical dates.
**Rule:** For every data source, write a test: given a specific historical date, assert that the returned data contains nothing from after that date. Run this test for dates both within and near the boundaries of the data coverage.

### L57 — Vague success criteria enable false positives [architecture]
**Mistake:** Smart money lift was defined as "measurable improvement" with no numeric threshold. Macro correlation was defined as "higher win rate in favourable regime" with no minimum. Any positive value would pass. A strategy showing 0.1pp improvement on 5 trades would pass the same as one showing 8pp on 200 trades.
**Principle:** Every criterion must have a specific numeric threshold AND a minimum sample size. "Better" is not a criterion. "≥ 3pp improvement with minimum 30 trades per bucket" is a criterion.
**Rule:** Before building any validation system, define every passing threshold in numbers. If you can't state the threshold as a number, the criterion is not defined.

### L58 — Designing for the happy path — no defensive validation [architecture]
**Mistake:** The initial backtest engine assumed all data was present and correct. When a Parquet file was empty, signals defaulted to zero. When an API returned nothing, the composite score defaulted to neutral. These silent defaults masked data quality issues that should have caused loud failures.
**Principle:** Build for data failures, not data success. Every data load should validate what it received. Silent defaults that hide missing data are more dangerous than loud crashes that expose them.
**Rule:** After every data load, assert minimum requirements: minimum row count, expected columns present, date range covers the backtest period, no all-NaN columns. Raise a clear error with the ticker and data type if validation fails.

### L59 — Reusing existing infrastructure beats building new [architecture]
**Mistake:** Built a complete Finnhub news sentiment pipeline (pre-fetch script, GitHub Actions workflow, checkpoint logic, Parquet storage, pipeline integration) before checking whether Alpha Vantage — already integrated for Stage 1 — provided the same capability. It did, with better AI-powered scores.
**Principle:** Before adding any new external dependency, audit every existing integration for additional capabilities. The cost of a new integration (API key management, rate limit handling, data format normalisation, failure modes) is rarely worth it if an existing provider covers the need.
**Rule:** Maintain a capability inventory of every active API. Check it before evaluating new providers.

### L60 — Assumptions about data quality are always wrong [data]
**Mistake:** Assumed yfinance adjusted prices were equivalent to point-in-time screen prices. Assumed Quiver congressional data had consistent column names across all endpoints. Assumed AAII survey data was complete. Each assumption was partially wrong.
**Principle:** Never assume data quality. Verify it. Every data source has its own quirks: missing dates, inconsistent column names, different handling of corporate actions, timezone issues, survivorship bias, look-ahead in adjustments.
**Rule:** For every new data source: (1) check for missing dates, (2) check for NaN values, (3) verify date coverage matches expectations, (4) verify column names match documentation, (5) spot-check 3-5 specific values against a known reference.
