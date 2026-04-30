# Universal Engineering Learnings
**Author:** Jeet Mehta
**Compiled:** April 2026 — Stock Picks & Automated Trading System
**Purpose:** Universal principles derived from real mistakes. Apply to every future project regardless of domain.

Each lesson states: what went wrong, the universal principle it teaches, and the rule to follow going forward.

---

## 1. TESTING & VERIFICATION

**The single biggest source of bugs in this project was the assumption that reading correct-looking code means the code works correctly. Every critical bug was invisible when reading and obvious when run.**

### Read code to understand. Run code to verify.
Three comprehensive audits missed a bug where all agent smart money context was empty dicts. The bug was caught in 30 seconds by running one print statement. Audits conducted by reading code are incomplete audits. Every integration point needs an executable test. A data flow is only verified when a test asserts it end-to-end.
**Rule:** After every audit, write a test for every flagged item. "It looks right" is not verification.

### Test producer/consumer interfaces explicitly in code.
Function A returned keys `{composite_signal, score, details}`. Function B expected `{congressional_sig, insider_sig, institutional_sig}`. Three audits examined both files and concluded the integration was correct. It wasn't. The mismatch was only caught by running: `assert all(k in result for k in expected_keys)`.
**Rule:** For every data handoff between functions, write a test: what does the producer return, what does the consumer expect, do they match.

### Compare documentation against code directly, not separately.
The project plan correctly documented two walk-forward windows. The code implemented one. Survived three audits because each audit checked the plan and the code separately. A plan that says one thing while the code does another is worse than no plan — it creates false confidence.
**Rule:** For every documented behaviour, have a test that asserts it. Documentation without a test is a claim, not a guarantee.

### Time-series accumulation requires multi-step tests.
`max_adverse_excursion` was documented as "worst % during the hold period." The code computed it from a single day's bar. Only running the backtest across multiple days would reveal this. Field names implying accumulation (max, min, worst, best) require tests across multiple time steps.
**Rule:** Any field computed over time must be tested with at least 2 time periods to verify accumulation works.

### Validate that cached results actually contain data.
A pre-fetch process ran successfully for 509 tickers with no errors. All resulting files were ~1012 bytes — empty DataFrames. The download appeared to succeed. Empty response ≠ failed call. Successful process exit ≠ successful data retrieval.
**Rule:** After every pre-fetch, spot-check: open 3-5 random output files and verify they contain rows. Assert minimum row count in the pre-fetch completion check.

### Test the complete workflow at small scale before building for all.
Alpha Vantage appeared to allow 25 calls/minute. Built a 509-ticker pre-fetch assuming this rate limit. The actual limit was 25 calls/day. Discovered only after building the complete pipeline and attempting to run it.
**Rule:** Before building any pipeline, run the complete workflow end-to-end for 5-10 units. Measure: time per unit, quota consumed, data quality. Then extrapolate to full scale. Never extrapolate from documentation alone.

### Run integration tests before every significant operation.
A master test runner (`run_all_tests.py`) must pass before every backtest run, after every code change, and after every data download. Tests that existed but weren't run before the Phase 1B partial run would have caught 3 of the 4 critical bugs found.
**Rule:** Tests only work if they are run. Make running tests the first step of every session, not an optional final step.

---

## 2. DATA PIPELINES & APIs

**The pattern that caused the most wasted time: building complete pipelines before validating that the underlying API or data source actually provides what was assumed.**

### Pre-fetch everything. Never call APIs inside computation loops.
The initial design called external APIs live inside the backtest loop — one call per candidate per day. With 509 instruments × 782 days × 10 candidates × 6 agents, this was millions of API calls. Each took ~35 seconds. Estimated runtime: 40-60 hours. Pre-fetch architecture reduced this to ~2 seconds per candidate.
**Rule:** If a function calls an external API and is called inside a loop, refactor immediately: extract the call, pre-fetch to disk, read from disk inside the loop. Zero network calls during computation.

### Download granular data. Aggregate on demand.
Initially stored composite signals (`congressional_signal: "buy"`) instead of raw records (which representative, how much, when, party). When age-weighting and Senate/House distinction were later needed, full re-downloads were required.
**Rule:** Store the most granular data available. Aggregates can always be computed from granular data. Granular data cannot be recovered from aggregates.

### Verify the API tier before building, not after.
Built a complete 509-ticker insider download script, ran it, and got 0 records for all tickers. The Hobbyist tier didn't include insider data. Discovered only after the full run.
**Rule:** Before writing any integration code: make one real API call per endpoint per tier, verify it returns the expected data, then build.

### Verify ALL dimensions of API limits — not just rate limits.
Alpha Vantage free tier: "25 calls/minute." Built pipeline with 13-second sleeps between calls. Actual limit: 25 calls/day total. Quota exhausted after 4 tickers. One limit being acceptable doesn't mean all limits are acceptable.
**Rule:** For any API, verify: calls per minute, calls per day, calls per month, data lookback window, records per call, geographic restrictions, tier-specific endpoint access.

### Verify API data structure before building the consumer.
Built complete Quiver integration before verifying column names in the API response. Discovered column name mismatches between documentation and actual response only during pipeline testing.
**Rule:** `print(response.json())` — one real call, print the full response — before writing any code that consumes it.

### Use existing integrations before adding new ones.
Built a complete Finnhub news sentiment pipeline before checking whether Alpha Vantage (already integrated for Stage 1) provided news sentiment. It did — with better AI scores and full historical coverage, for free.
**Rule:** Before adding any new external dependency, audit every existing integration for additional capabilities. Maintain a capability inventory of every active API.

### Static committed files beat live API calls for stable reference data.
Multiple attempts to fetch the S&P 500 constituent list dynamically failed in different environments. Committing `sp500_tickers.csv` as a static file took 5 minutes and worked everywhere.
**Rule:** If data changes less than monthly, use a committed static file. It works offline, in all environments, is version-controlled, and is instant to read.

### Never assume data quality. Verify every source.
Every data source in this project had issues: yfinance adjusted prices differ from on-screen prices; Quiver had inconsistent column names; AAII initially had only 15 hardcoded sample points; economic calendar was missing 2 years of events; COT data was fabricated.
**Rule:** For every data source: (1) check for missing dates, (2) check for NaN values, (3) verify date coverage, (4) verify column names match documentation, (5) spot-check 3-5 values against a known reference.

### Point-in-time violations are invisible to reading — test them explicitly.
Multiple point-in-time violations (using future data in backtests) survived several code reviews. They require explicit tests: given a specific historical date, assert that no returned data has a date after the query date.
**Rule:** For every data source used in backtesting, write a point-in-time test with a known historical date. Run it as part of the standard test suite.

---

## 3. ARCHITECTURE & SYSTEM DESIGN

**The pattern here: architectural decisions made under time pressure, without thinking through downstream consequences, created cascading rework weeks later.**

### Design the data model before building any pipeline.
Sector information existed in the CSV from the start but was never included in the engine, dataclasses, or agents. Adding it later required changes to OpenTrade, ClosedTrade, backtest.py, and pipeline.py — four files that all had to change together.
**Rule:** Before writing any code, define all fields in every data structure. Ask: what data will downstream consumers need? Design the schema first, implement second.

### Every passing criterion must have a specific numeric threshold.
Smart money lift was defined as "measurable improvement." Any positive value passed — including 0.1pp on 3 trades. The criterion was meaningless until redefined as "≥ 3pp with minimum 30 trades per bucket."
**Rule:** Every criterion in a validation system must be a specific number with a minimum sample size. "Better" is not a criterion. "≥ X% improvement with minimum N samples" is.

### Check every rule for consistency with every other rule.
The project philosophy was "buy dips in crisis markets." A circuit breaker blocked all new longs when VIX > 40. These rules directly contradicted each other and coexisted undetected through multiple audits.
**Rule:** For every new rule, explicitly check: does this contradict any existing rule? Maintain a brief rules consistency summary. Document the resolution when a contradiction is found.

### Every rule must have a clear logical justification.
A 40-day forced exit was added without a logical justification. If a trailing stop hasn't triggered, the trade is working or neutral. There's no logical reason to exit. The rule was removed when this was identified.
**Rule:** Before adding any rule: state its logical trigger. "What market condition does this rule respond to?" If the answer is "nothing — it's just a limit," reconsider the rule.

### Measure position-weighted returns, not equal-weighted returns.
All backtest trades were computed with equal dollar weight. EXCEPTIONAL tier (5% of capital) and MEDIUM-HIGH tier (1.5%) contributed equally to reported ROI. The "total ROI" figure was meaningless as a portfolio metric.
**Rule:** Define reference capital at the start. Apply real position sizes to all P&L calculations. Report both per-trade metrics and portfolio-level weighted metrics.

### Verify that the right statistical formula is used for the right data frequency.
Sharpe ratio used `sqrt(252)` for annualisation — correct for daily returns. Our returns were per-trade with variable hold periods. The correct annualisation for per-trade returns uses `sqrt(trades_per_year)`.
**Rule:** Before using any statistical formula, verify: what data frequency does this formula assume? Per-trade, daily, weekly, and monthly series each require different treatment.

### A backtesting system must be fully deterministic and offline.
VIX and DXY were fetched via live yfinance calls inside macro_snapshot(), which was called 782 times during the backtest. Any network failure would break the run mid-way. Different runs could return slightly different data.
**Rule:** Before starting any backtest run, verify zero network calls will be made during execution. Pre-load all data at startup. The backtest loop must be pure computation on local data.

### Universe filters must be applied at the relevant point in time.
The liquidity filter (price > $5, volume > 500k) was applied once at January 2022. A stock that became illiquid by 2024 was still traded through 2026.
**Rule:** Any filter that defines what's eligible must be re-applied at the frequency of change. For annual rebalancing: re-check annually. Time-varying eligibility requires time-varying filtering.

### In multi-stage pipelines, each stage must be independent of others.
The confidence tier required "congressional + insider" signals to reach EXCEPTIONAL. Agents received those same signals as evaluation inputs. The gating logic and the evaluator used identical data — the tier constrained the agents; the agents were supposed to be independent evaluators.
**Rule:** Map all data dependencies in a multi-stage pipeline. If stage N uses the same data to both gate and evaluate stage N+1, redesign one of the stages.

### Fabricated data must never feed into any scoring system.
Nine hardcoded COT sample readings were used as if they were real CFTC institutional positioning data. These fed into sentiment scores which fed into agents. The system was partly making decisions based on invented data.
**Rule:** All data in any decision system must be traceable to its actual source. If real data is unavailable, return "not_available" and exclude it from scoring. Never substitute fabricated values.

### Backtests must mirror live trading scenarios exactly.
News sentiment was planned for live trading but excluded from the initial backtest. The backtest didn't reflect what live trading would actually do. Discovered late — required re-downloading all news data.
**Rule:** From day one: every data source, signal, and API used in live trading must be used in backtesting. If it is not backtested, it is not validated.

---

## 4. PROCESS & DECISIONS

**The pattern: good decisions made, then not immediately documented, then partially forgotten or contradicted. Good checklists created, then not consulted.**

### Document decisions immediately — not later.
Multiple design decisions (remove correlation filter, remove position caps, AVOID tier behaviour, ATR multiplier change) were approved in conversation but written to PROJECT_PLAN.md sessions later. During the gap, the decision existed only in conversation history.
**Rule:** Decision → document → commit. All in the same response. Never let more than one exchange pass between approval and documentation.

### A checklist only works if it is visibly executed before every action.
CHECKLIST.md was created with 13 items. Multiple mistakes that the checklist would have caught still occurred afterward. The checklist was documented but not consulted. Making the execution visible ("Checklist: ✅ item 1 ✅ item 2...") forces the habit.
**Rule:** State checklist compliance explicitly before every significant action. This takes 10 seconds and prevents hours of rework.

### One logical change per commit. Never batch unrelated changes.
Multiple sessions made 5-8 changes in one commit. When something broke, it was impossible to identify which change caused it. Each commit should be independently reversible.
**Rule:** One concept per commit. If a session produces 5 fixes, make 5 commits. The overhead is seconds; the debugging savings can be hours.

### Never give cost or time estimates without measuring first.
Estimated Phase 1B at "$16 CAD, 3-4 hours." Actual: $116 CAD, 40+ hours. The estimate was given confidently based on a formula with an unexplained divisor, without measuring one actual agent call.
**Rule:** Format every estimate: "One unit = X time / $Y cost. Total = N units × X = Z time / N × $Y = $Z. Assumptions: [list]." If you can't show this calculation, you don't have an estimate — you have a guess.

### Verify tool availability before recommending it.
Recommended PowerShell scripts without verifying git was on PATH. Recommended Alpaca as the broker without verifying Canadian availability. Both required correction after the user attempted to use them.
**Rule:** Before any recommendation: (1) does it work in the user's OS and environment, (2) is it available in their country, (3) are there simpler existing alternatives.

### Every leap ahead of the current phase is a risk.
Downloaded full S&P 500 cache for Phase 1B before Phase 1A results were reviewed. Phases exist precisely to validate before scaling. Jumping ahead skips validation and creates work that may need to be redone.
**Rule:** Never advance to the next phase without explicit approval. Every phase must earn the right to proceed.

### Living documents need periodic end-to-end review, not just incremental updates.
The project plan accumulated 45 documented flags across 4 audits — stale dates, wrong broker, contradictory rules, missing data sources. Incremental updates don't catch contradictions between sections written at different times.
**Rule:** After every batch of 3+ design decisions, re-read all affected sections end-to-end and check for contradictions with the new decisions.

### Update docstrings in the same commit as the code they describe.
After changing survivorship bias from flat to hold-adjusted, the docstring still said "2% annual haircut." After removing COT data, the function docstring still described COT inputs. Stale docstrings are worse than no docstrings — they actively mislead.
**Rule:** Every commit that changes function behaviour must update the corresponding docstring. No exceptions.

---

## 5. GIT & VERSION CONTROL

**Three separate incidents of the same mistake: git reset --hard destroying hours of downloaded data. This class of mistake is preventable with one habit.**

### git status before any destructive git command. Always.
`git reset --hard origin/main` was given three times after downloads completed, each time destroying uncommitted data. The command appeared twice in the learnings document before the third occurrence.
**Rule:** `git reset --hard` is permanently destructive. It is banned from any instruction unless `git status` was run immediately before and confirmed "nothing to commit, working tree clean." No exceptions.

### Verify push success — exit code 0 doesn't mean the push landed.
The prefetch script printed "All data committed" after the download, but the final git push had been silently rejected. The script reported success when the push had failed.
**Rule:** After any critical git push, verify: `git log -1 origin/main` must match `git log -1`. If they differ, the push failed. Never report "done" until push is confirmed.

### Parallel workflows that share a git branch always conflict.
Parallel GitHub Actions batches all tried to push to main simultaneously. Only one succeeds; others are rejected. Required 3+ reruns. Sequential execution that takes 4 hours is better than parallel execution that takes 6 hours due to reruns.
**Rule:** For workflows that must share a git branch, use sequential execution. Parallelism is only safe when outputs are completely independent.

### Always use rebase before push, never merge.
`git pull --rebase origin main` before every push prevents the diverged-branch rejections that caused multiple failed pushes throughout this project.
**Rule:** The correct sync sequence: `git add` → `git commit` → `git pull --rebase origin main` → `git push`. Never `git pull` (creates merge commits). Never `git push` without rebase first.

### Commit immediately after every download. Never rely on local state.
Downloaded 67 instruments, Codespace restarted, lost everything. Repeated multiple times. Cloud environments don't persist local state. Any file not committed to git is a file that can disappear.
**Rule:** Commit every 50 records during long downloads. Commit immediately when a download completes. Never assume local files survive a session end.

---

## 6. INFRASTRUCTURE & ENVIRONMENTS

**The pattern: assuming the development environment has the same capabilities as the target environment. It never does.**

### Test in the target environment before building for it.
Assumed all APIs were accessible from Codespaces. Wikipedia scraping and several API endpoints were blocked by the Codespaces allowlist. Built integrations that worked locally but failed in the actual execution environment.
**Rule:** Before building any integration, test the specific network call from the actual execution environment (Codespaces, GitHub Actions, VPS) — not from a local machine.

### Pin all dependency versions. Unpinned dependencies will break.
Codespace lost all pip installs on restart unless in devcontainer.json. Multiple runs produced no cache files because pyarrow was missing. Even with devcontainer.json, unpinned versions can break when a new version is released.
**Rule:** Pin all dependency versions (`pyarrow==14.0.0` not `pyarrow`). This prevents unexpected version upgrades from breaking the environment.

### Build for the user's actual environment, not the assumed one.
Created a PowerShell script for a user who consistently used Git Bash. PowerShell doesn't have git on PATH, doesn't support `&&`, and blocks script execution by default. Made 3 consecutive errors before admitting the script was wrong.
**Rule:** Identify the exact terminal environment before writing any script or command. Ask if unsure. The simplest correct solution (one Git Bash command) beats an elaborate wrong solution (PowerShell script).

### Verify broker/service geographic availability before recommending.
Listed Alpaca as the broker throughout the project plan. Alpaca doesn't support Canadian accounts. Discovered only during Stage 4 planning.
**Rule:** For any service recommendation: check geographic availability, regulatory requirements, and commission structure for the user's specific country before recommending.

---

## 7. AGENTS & AI SYSTEMS

**Specific lessons for systems that use LLMs as decision-making components.**

### Agents must score independently — don't give them the rules they're scoring against.
The Decision Agent prompt included the explicit confidence tier matrix (EXCEPTIONAL = 85+, VERY HIGH = 70-84...). The agent pattern-matched to the rules rather than independently evaluating signal quality.
**Rule:** Agents derive scores independently. Tier mappings happen in code after the agent returns a raw score. Never include the scoring rubric in the agent prompt.

### Set temperature=0 for backtest agents. Results must be reproducible.
Agent API calls didn't set the temperature parameter. Default is 1.0 (stochastic). The same inputs could produce different confidence tiers on different runs, making Phase 1B results non-reproducible.
**Rule:** temperature=0 for all backtest and batch processing agent calls. temperature>0 only for live trading where some variation is acceptable.

### Include prompt version in cache keys. Invalidate when prompts change.
The agent cache key was `hash(ticker + date + strategies + phase)`. When agent prompts changed substantially, the cache key didn't change — stale cached results from old prompts were served with the new code.
**Rule:** Include `PROMPT_VERSION` in every cache key. Increment the version whenever any agent prompt changes materially. The prompt is part of the computation.

### Agents need portfolio context to make portfolio-aware decisions.
Each agent call was completely independent. An agent evaluating a new NVDA long had no knowledge of existing NVDA positions, sector concentration, or portfolio drawdown. In a portfolio system, each trade decision is marginal — it depends on current exposure.
**Rule:** Pass portfolio context (open positions, sector concentration, existing position in ticker, current drawdown) to any agent making trade entry decisions.

### A "debate" between two agents requires two independent API calls.
The Bull/Bear debate was implemented as one API call asking the model to argue both sides. One model cannot genuinely argue against itself — it will have a bias toward the overall signal direction.
**Rule:** Genuine independent perspectives require independent API calls with independent context. Two calls, each primed differently, produce real debate. One call playing both sides produces the appearance of debate.

---

## 8. STATISTICS & VALIDATION

**Lessons specific to backtesting and statistical validation of trading systems.**

### Single walk-forward window is insufficient — use at least two.
Walk-forward with one IS/OOS split allows a strategy to appear ROBUST due to luck. Two windows requiring both to pass is the minimum for credible validation.
**Rule:** Minimum two walk-forward windows. ROBUST = passes both. Passing one = WEAK. Document the IS and OOS periods for each window.

### Measure isolated effects — control for confounders.
Smart money lift was computed as win rate of HIGH tier minus LOW tier trades. But high-tier trades also have more strategies firing. The lift measured strategy quality + smart money quality combined — not smart money quality in isolation.
**Rule:** To measure the effect of variable X, compare groups that differ only in X. Hold all other variables constant.

### Minimum sample sizes must be defined and applied consistently.
Three different minimum trade counts appeared in the codebase: 30, 100, and 500 — set at different times without a coherent framework. Applied inconsistently: IS period had 30 (too low), OOS had 500 (too high).
**Rule:** Define minimum sample sizes from a statistical framework: minimum N to detect effect size E at significance level α with power β. Apply consistently across all evaluations.

### Report confidence intervals, not just point estimates.
Win rates were reported as single numbers (55.3%) without confidence intervals. On 100 trades, the 95% CI is (45%, 65%). The true win rate could easily be below 50% — indistinguishable from random chance.
**Rule:** Always report win rates with 95% confidence intervals. Flag any strategy where the lower CI bound is below 50%.

---

## QUICK REFERENCE — Before Every Session

1. **Run tests:** `python backtest/tests/run_all_tests.py` — all must pass
2. **Validate data:** `python scripts/validate_phase1b_data.py` — before any backtest
3. **Check git:** `git status` — before any git command, especially before reset
4. **State checklist:** "Checklist: ✅ thought through ✅ plan shown ✅ approved ✅ risks flagged ✅ no destructive ops without safety check"
5. **One call first:** test any API endpoint with one real call before building the pipeline
6. **Measure before estimating:** time one unit, multiply, show the calculation

---

## THE FIVE MOST EXPENSIVE MISTAKES IN THIS PROJECT

1. **L49/L77 — git reset --hard destroyed downloaded data twice.** Several hours of Quiver downloads lost. Fix: git status before any reset.

2. **L44 — Producer/consumer key mismatch — all agent SM context was empty for entire development period.** Congressional, insider, institutional data was downloaded and cached correctly but never reached the agents. Fix: integration tests on every data handoff.

3. **L11 — Live API calls inside backtest loop.** Would have made Phase 1B take 40-60 hours and cost 5× more. Fix: pre-fetch everything before computation starts.

4. **L45 — Three audits conducted by reading code — all missed the same critical bugs.** Fix: every audit finding gets an executable test.

5. **L68 — Circuit breaker blocked all longs in crisis — directly contradicted the core buy-the-dip philosophy.** The most important market regime (crisis) was completely excluded from long trades. Fix: rules consistency check whenever a new rule is added.

---

## ADDENDUM — Process Mistakes Caught in Real Time

### L86 — Jumped from data-ready to full run without batch test [process]
**Mistake:** After confirming all Quiver data was downloaded and validation passed, immediately moved to instructions for running Phase 1B at full scale. Skipped the mandatory batch test step entirely — the step that exists specifically to catch agent quality issues cheaply before spending $116 CAD.
**Principle:** "Data is ready" does not mean "ready to run." The batch test is not a formality — it is the only way to verify that agents produce coherent, specific, useful output before paying for 509 instruments × 782 days of agent calls.
**Rule:** The sequence is always: validate data → 5-ticker controlled test → manual agent review → owner approval → scale. Never jump from validate to scale. Checklist item 13 was added specifically for this.

### L87 — Controlled comparison test not designed upfront [process]
**Mistake:** We had AV news data for 5 tickers. Rather than designing a controlled A/B test (run 5 tickers with news, run same 5 without news, compare agent outputs systematically), the news data was treated as a binary — either complete or skip.
**Principle:** When you have partial data coverage, use it to design a controlled comparison. Partial coverage is an opportunity to isolate the contribution of each data source before scaling.
**Rule:** When any data source is partially available, run the batch test both with and without that source. Document the difference in agent outputs and confidence tiers. This validates the data source's contribution before committing to full download costs.

### L88 — NEVER USE WIKIPEDIA AS A DATA SOURCE [infrastructure]
**Mistake:** Wikipedia was used (and proposed multiple times) as the source for S&P 500 constituent lists.
**Why it fails:** Blocked in Codespaces (HTTP 403). No API — HTML scraping breaks on page restructuring. Not a primary source — Wikipedia itself copies from S&P press releases. No historical point-in-time data. Rate limited with no SLA.
**Fix:** Use slickcharts.com (free, stable, no auth), S&P official press releases (authoritative, free), or a paid provider (Quiver, Polygon) for production. The static committed CSV (`sp500_tickers.csv`) refreshed quarterly via slickcharts.com is the correct pattern.
**Rule:** Wikipedia is never a valid data source for any production pipeline. Document in CLAUDE.md and refuse any future proposal that uses Wikipedia for data.

### L89 — Universe staleness is a systematic blind spot, not a one-time fix [architecture]
**Mistake:** After replacing Wikipedia with a static CSV, no refresh schedule or process was attached to it. The CSV went stale immediately — SNDK missed 9 months, GEV missed 12+ months, SMCI, VST, GDDY, ERIE all missing.
**Principle:** A static universe list without a refresh process is a time bomb. Every static list goes stale. The question is not whether but when.
**Fix:** Three-tier architecture with defined refresh frequencies: Tier 1 (S&P 500) quarterly, Tier 2 (extended/spinoffs) monthly for live trading, Tier 3 (momentum watchlist) monthly for live trading. Scripts, GitHub Actions workflows, and CHECKLIST items attached to each tier.
**Rule:** Never commit a universe list without a refresh script and a scheduled review process documented in CHECKLIST.md.

### L93 — NEVER suggest git checkout -- . or git clean without first checking untracked files [critical/infrastructure]
**Mistake:** Claude told the owner to run `git checkout -- .` to resolve unstaged changes, without first checking what untracked files existed on the laptop. This command would have deleted the entire full Phase 1B run output (output_1b_batch1 through output_1b_batch5 and all log files) since they were untracked — destroying hours of compute and API spend with no recovery path.
**Fix:** Before suggesting ANY destructive git command (checkout --, clean, reset --hard, stash), Claude must first ask the owner to run `git status` and share the output, then audit every untracked file before proceeding.
**Rule:** If a full run is in progress or recently completed, assume output folders are untracked until proven otherwise. Never suggest destructive git commands without explicit confirmation of what will be affected.

### L94 — PROJECT_PLAN.md is append-only without explicit permission [critical/documentation]
**Mistake:** Commit 38e7ee2 did a "complete rewrite" of PROJECT_PLAN.md removing 789 lines — all 60 strategy descriptions, full API stack tables, signal universe (274 fields), confidence tier logic, website design, stage roadmaps, rules tables, and 24 numbered sections. This was done without owner permission.
**Fix:** All removed content restored in April 2026 by appending pre-rewrite sections back to current file.
**Rule:** PROJECT_PLAN.md is APPEND-ONLY. Claude may only add new content or update existing content. Removing or rewriting any section requires explicit owner permission. If a rewrite is needed, propose the specific changes and wait for approval before touching the file.

### L95 — Always compute cost estimate before any run. No exceptions. [critical/cost]
**Mistake:** Full Phase 1B run launched without validating actual screener pass rate against cost estimate. PROJECT_PLAN.md estimated 8 candidates/day but crisis regime passed 28/day — a 3.5x multiplier that was never checked. Result: $150 spent on an incomplete run.
**Fix:** Before any run involving API calls, compute: screener_pass_rate × trading_days × batches × agents × token_cost = total_cost. Show the math. Get explicit owner approval with that number visible.
**Rule:** No run starts without a written cost estimate approved by the owner. This is non-negotiable regardless of how confident Claude is in the estimate.

### L96 — Verify all processes are dead before moving on. Show proof. [critical/infrastructure]
**Mistake:** Told owner processes were killed, moved on without verifying. Processes continued running, accruing API charges for hours after the supposed kill.
**Fix:** After any kill command, always run `ps aux | grep python` and paste the output. Only confirm processes are dead when the output is empty. Never report done until proof is shown.
**Rule:** Process kill must be verified with empty ps output before any subsequent action. No exceptions.

### L97 — Risk Agent locked to floor in sustained crisis — zero variance, zero value [agent/design]
**Finding:** In a sustained crisis regime (Jan-Oct 2022), the Risk Agent scored exactly 2/10 on every single trade across 34,727 trades. Zero variance. It detected "high VIX = crisis" and applied a floor uniformly with no differentiation between individual trade quality.
**Implication:** In crisis regime, the Risk Agent adds cost but no signal. It cannot differentiate good crisis trades from bad ones.
**Phase 1C fix:** Risk Agent should score relative to crisis baseline — "is this trade better or worse than the average crisis-regime entry?" not "is this a good trade in absolute terms?" Add a regime-relative scoring mode.

### L98 — Agent upgrade threshold (75) was never reachable in crisis regime [agent/design]
**Finding:** Maximum agent score observed across 34,727 trades was 42. The upgrade threshold is 75. No trade ever came close to being upgraded. 99.9% of trades were downgraded.
**Implication:** Phase 1B agent calls in crisis regime produced near-zero differentiation at significant cost.
**Phase 1C fix:** Calibrate agent score thresholds against observed score distributions before deployment. If max observed score is 42, an upgrade threshold of 75 means agents will never upgrade anything — the threshold is miscalibrated.

### L99 — Trade inflation 3.5x — 500-trade minimum is effectively 143 independent positions [data/design]
**Finding:** 34,727 total trades = only ~9,900 unique ticker+date decisions. Multiple strategies fire on the same ticker+date, creating 3.5x row inflation. The 500-trade minimum per strategy in PROJECT_PLAN assumes independent trades — but 500 rows may represent only ~143 genuinely independent positions.
**Phase 1C fix:** Either (a) deduplicate to one position per ticker per day before evaluating strategy criteria, or (b) recalibrate the minimum to 1,750 rows (equivalent to 500 independent positions at 3.5x inflation factor). Both require owner approval before implementation.

### L100 — Recommendations made without validating underlying assumptions [critical/process]
**Mistake:** Across audit Passes 26-34, multiple recommendations were given based on stale memory or untested assumptions. Pass 26 estimated live agent cost at "$13-40/month" without counting actual LLM nodes per propagate(). Pass 28 recommended "Pattern 2 custom agents" without reading TradingAgents source. Pass 31 quoted GPT-5.4-mini at "$0.50/$2.50" — actual is $0.75/$4.50. Pass 32 estimated propagate() cost at "$0.18" without counting tool-use loops; real is $0.30-0.50.
**Why this matters:** Each error compounded. The user had to push back three times to get to the right cost answer. A real backtest run with these numbers would have gone over budget by 2-5x — a direct repeat of the L95 mistake (Phase 1B cost overrun).
**Fix:** New CHECKLIST item #26 — Assumption Validation Before Every Recommendation. List every factual claim, source it, verify if uncertain, state "Verified:" explicitly in response.
**Rule:** No recommendation goes out without explicit validation of all factual claims it depends on. Pricing especially — re-verify in the current session, not from memory.

### L101 — Recommendations made without checking current question relevance [critical/process]
**Mistake:** Pass 28 recommended Pattern 2 custom agents (multi-week effort) when user had not asked for custom agent integration — they had asked about cost. Pass 31 recommended cost-optimized config but framed it as if the user was already using TradingAgents (they were not — 772 lines of custom code that didn't import the framework). Each recommendation drifted from the actual question.
**Why this matters:** Recommendations that don't address the actual question waste owner's time and energy reviewing them. They compound: each off-topic recommendation generates cascade decisions that also don't address the original need.
**Fix:** New CHECKLIST item #27 — Relevance Check Before Every Recommendation. State the specific question, state how the recommendation addresses it, confirm assumptions match the current message.
**Rule:** Recommendations must directly trace back to the owner's stated question. If they don't, ask before recommending.

### L102 — Cost estimates given without counting actual LLM call multipliers [critical/cost]
**Mistake:** Pass 26 said "6 agents × $0.02 per call." Reality: 11+ LLM nodes per propagate() because (a) Bull/Bear and Risk debaters are separate nodes, not bundled "agents," (b) each Analyst makes 2-4 LLM calls due to LangChain tool-use loops (initial → tool call → interpret → maybe retry), (c) Reflection node post-decision adds another call. Naive node counting misses tool loops. Real cost is 2-3x naive estimates.
**Why this matters:** With $300 budget hardcap, 2-3x cost error = budget blown. Past project (L95) had identical pattern: estimate based on "candidates × agents × cost" without measuring actual tool-loop multipliers, ended up 5x over.
**Fix:** Cost estimates for any LLM-orchestrator framework must include: (a) explicit count of LangChain/LangGraph nodes by reading setup.py, (b) tool-use loop multiplier (typically 2-4x per analyst node), (c) debate round multiplier, (d) verified pricing from current source.
**Rule:** No LLM cost estimate is final until it explicitly accounts for tool-loop multipliers and debate rounds, with source-verified pricing.

### L103 — Recommended frameworks/libraries without reading their source code [critical/architecture]
**Mistake:** Pass 28 said TradingAgents Pattern 2 (custom agents extending theirs) was "best of both worlds." Pass 31 reading their actual code revealed Pattern 2 is much harder than claimed because their analysts use LangGraph tool nodes, not injected context. Recommendation was based on README skim, not source read.
**Why this matters:** Architectural recommendations that cannot be implemented as described waste implementation time and create broken integrations. Same pattern that caused L44 (producer/consumer key mismatch — three audits read code but not enough of it).
**Fix:** Before recommending integration with any external framework, clone the repo and read at least: (a) the main entry-point file, (b) the file containing the orchestration/setup code, (c) one example agent/component file. Confirm the integration pattern is actually supported.
**Rule:** No "fork existing library" recommendation without reading the library's actual source structure first. README skim is insufficient.

### L104 — Past project mistakes (Sonnet development) must inform Path B validation [critical/process]
**Mistake (about to repeat unless prevented):** The Sonnet-driven development of this project produced 203 bugs because Claude built without validating assumptions and tested only by reading. User explicitly named this risk: "I do not want to make the same mistakes again."
**Why this matters:** Path B (GPT-5.4-mini, ~1,800 candidates, $300) was recommended quickly. It needs the same validation discipline being added in CHECKLIST 26-28 BEFORE it becomes a final decision.
**Fix:** Validate every assumption in Path B explicitly: pricing source-verified, sample size statistically defensible, framework integration pattern confirmed by code reading, success criteria defined upfront, kill switches in place per CHECKLIST 22 (cost estimate) and 23 (small batch).
**Rule:** Major path decisions must pass Assumption Validation (CHECKLIST 26) and Relevance Check (CHECKLIST 27) before being locked in. The recommendation is not final until validation is shown.

### L105 — Budget batch discipline must be applied to EVERY API operation, not just the one we just lost money on [critical/cost]
**Mistake pattern:** Each time a budget mistake happens (L86, L95, L102), the rule gets added retroactively for the SPECIFIC operation. Then a new operation comes along (Phase 0.A prefetch, agent backtest, etc.) and the discipline doesn't transfer because it was framed for the prior context.
**Why this matters:** Path B agent backtest has a $300 hard cap. Phase 0.A prefetch will have its own cost. Phase 0.C TradingAgents integration will have its own cost. Each is a NEW chance to repeat the L95 mistake unless the discipline is applied universally, not per-operation.
**Fix:** CHECKLIST #29 added — STOP-EARLY-ON-BUDGET as consolidated cross-reference rule. CLAUDE.md elevated to top-of-mind. Apply to: backtest runs, agent calls, data downloads, LLM evaluations, any operation costing money OR hard to redo.
**Rule:** Every API spending operation must follow the same discipline: cost estimate → smallest test batch → manual review → mid batch → manual review → scale, with hard stops at 80% and 100% of budget. Owner explicitly approves at each gate. No exceptions, no operation-specific carveouts.
