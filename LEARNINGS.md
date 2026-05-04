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
**Rule (UPDATED April 2026 per owner instruction):** PROJECT_PLAN.md changes — including additions, removals, rewrites, restructures, and edits — all require explicit owner approval before being made. Append-only restriction has been LIFTED. The CRITICAL element preserved: every change must be proposed with diff/scope, then explicitly approved, then implemented. Silent changes are still forbidden.

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

### L106 — Granular-by-default for all analysis [critical/methodology]
**Principle:** Aggregates obscure where strategies fail. Every backtest output, every metric, every signal evaluation must be reportable at multiple breakdown levels: total, per-strategy, per-regime, per-sector, per-cap-band, per-volatility-bucket, per-month, per-categorical-variable. Aggregate-only is rejected.
**Why this matters:** A strategy with 55% overall win rate may have 70% in bull regime and 35% in crisis. Reporting only the aggregate hides the regime-conditional behavior that determines whether to deploy. Same for sector, cap, volatility — every dimension can hide systematic failure.
**Rule:** Every metric reported at multiple breakdowns. Dashboards must support drill-down. The 17+ categorical variables in Pass 39 Section 9.2 are the standard set: cap band, liquidity bucket, beta bucket, vol bucket, earnings proximity, RSI bucket, short interest bucket, days to FOMC, days since IPO, index membership, VIX bucket, yield curve shape, sector momentum percentile, day-of-week, seasonality flag, plus base dimensions (strategy, regime, sector, tier, direction, date).

### L107 — Implementing to spec is NOT enough — premise questioning required [critical/process]
**Mistake pattern:** Multiple project failures share the same root cause: implementing instructions or spec without questioning whether the spec/instruction was optimal. Examples:
- 6-agent pipeline implemented per spec, but TradingAgents has 12 agents available
- Quiver insider/congressional scoring computed by us, but Quiver provides pre-built composites
- Wikipedia used as universe source per default heuristic (L88)
- 789-line PROJECT_PLAN rewrite per "rewrite this" interpretation (L94)
- $150 Phase 1B run launched per data-ready signal without batch test (L95)
Common pattern: Claude defaults to "implement what's stated" without questioning premise. Specs are ALWAYS incomplete.
**Fix:** New CHECKLIST #30 (Premise Questioning) and #31 (Decision Surfacing). Claude must surface unstated assumptions in any spec/instruction, identify viable alternatives, and ask owner before implementing.
**Rule:** No implementation begins until: (a) unstated assumptions surfaced, (b) alternatives compared against best practice, (c) explicit owner approval received. Implementing-to-spec without premise questioning is now a documented failure mode.

### L108 — Strict approval discipline — verbatim only, with permitted exception for process docs [critical/process]
**Owner directive (April 2026):** "Do not execute decisions without explicit approval." Refined: LEARNINGS.md and CHECKLIST.md updates do NOT need explicit approval (they are process discipline that strengthens the project). EVERYTHING else — code, PROJECT_PLAN.md, CLAUDE.md, AUDIT.md substantive sections, architectural choices, data downloads, API runs, decisions in the AUDIT decision registry — requires verbatim owner approval before execution.
**Operating rule:**
- Approval is signaled ONLY by verbatim "approved", "Y", "yes", "go ahead", "commit it", or equivalent explicit language
- "Add to X" / "include Y" / "make sure Z" are descriptive instructions, NOT approvals to execute (except for LEARNINGS/CHECKLIST per owner exception)
- Ambiguous instructions trigger clarification: list A/B/C/D interpretations and ask
- Silence is not agreement
- Recent prior approvals do NOT carry forward to new items unless explicitly stated
- "Approve all" applies ONLY to items explicitly enumerated in the immediately prior turn
- LEARNINGS.md and CHECKLIST.md additions/updates may be made directly when discipline gaps are identified, with the owner's standing exception
- All non-process changes require verbatim approval per above
**Why this matters:** Past Sonnet behavior interpreted instructions broadly, leading to silent decisions and 203 documented bugs. Strictest interpretation prevents recurrence even when it slows execution. The LEARNINGS/CHECKLIST exception was granted because process discipline strengthens guardrails — it can never weaken project safety.
**Rule:** Every commit, every implementation choice, every architectural decision, every code change, every data operation requires verbatim owner approval before execution. The ONLY exception: LEARNINGS.md and CHECKLIST.md additions/updates that strengthen process discipline (per owner's standing permission).

### L109 — Archive everything always: decisions, bugs, audit findings, lessons [critical/process]
**Owner directive (April 2026):** "Archiving everything is also a learning."
**Principle:** Every decision considered, every bug found, every audit finding, every lesson learned must be archived in a recoverable, indexable form. Not just current-state snapshots.
**Why this matters:** Future redo-and-flag-new audits require comparing against complete history. Without archive, "net-new" findings become guesses. With archive, the comparison is mechanical and reliable.
**Implementation:** AUDIT.md preserves all 41 audit passes immutably. AUDIT_INDEX.md provides single-lookup catalog. PROJECT_PLAN_ARCHIVE.md preserves pre-rewrite detail. LEARNINGS.md never deletes entries (109 and counting). CHECKLIST.md never deletes items (32 and counting). Standing exception in CHECKLIST #32g allows process-discipline files to grow without per-change approval.
**Rule:** Nothing is ever deleted from these archive files. Updates supersede but don't replace. The archive is the project's institutional memory. Treat it accordingly.

### L110 — Website/UX/notifications is first-class architecture, not peripheral [critical/process/audit-scope]
**Owner-identified miss (April 2026):** Across 42 audit passes, the website/UX/notifications layer was never adversarially audited despite being in scope from Day 1 (Stage 1 daily-picks site already deployed). Decisions like public-vs-private, trade rationale depth, push alert events, authentication, hosting platform were invented mid-conversation in Pass 43 instead of being surfaced as registry decisions in earlier passes.
**Pattern:** Audit scope defaulted to "the algo" (strategies, signals, agents, data, risk, statistical methodology) and treated UX/website/notifications as peripheral. They are not — for a system you monitor via mobile and where notifications drive your awareness, the UI IS the system from your perspective.
**Fix:** All future audit passes must include explicit sections covering:
1. Website / UI / dashboard architecture and changes
2. Notification layer (email, Telegram, SMS, push)
3. Mobile UX
4. Public-vs-private site separation
5. Authentication / authorization
6. Trade rationale presentation depth
7. Owner monitoring workflow
**Rule:** When an audit pass lists "architecture" as a section, UX/website/notifications must be a sub-section, not assumed-out-of-scope. Review all 42 prior passes retroactively for items missed and add them as decisions where applicable.

### L111 — Never quote cost figures from memory; always re-verify against source [critical/cost/discipline]
**Mistake pattern (April 2026):** Multiple cost claims made in this conversation were wrong because I quoted from memory or heuristic instead of fetching the canonical source:
- Pass 34: GPT-5.4-mini pricing quoted at $0.50/$2.50 input/output per Mtok — actual was $0.75/$4.50
- Pass 45 turn: IBKR commission cited as "$0.005/share min $1" without mentioning the **1% per-order cap** which materially changes economics for small trades
- Pre-this-turn: never surfaced interlisted TSX/NYSE routing or ETF substitution as cost optimization
**Common cause:** Treating cost as a single memorized number rather than a verified-at-source figure with full structure (rate + minimum + maximum + caps + third-party fees).
**Rule:** Every cost claim in any audit, recommendation, or decision MUST:
1. Web-fetch the canonical pricing page at time of claim
2. Quote the source URL and verification date inline
3. Include full pricing structure (rates + minimums + maximums + caps + third-party fees) — not just the headline number
4. Re-verify on a quarterly cadence for any persistent claims (since pricing changes)
**Past instances captured (these are documented mistakes):** Pass 34 GPT pricing, Pass 45 IBKR commission, this turn's interlisting omission. All three followed the same pattern.

### L112 — Cost optimization is per-trade-context, not global [critical/cost/architecture]
**Insight (owner-surfaced April 2026):** "SP500 stocks have TSX equivalents which can also save more money. Same for ETFs." This is true but only for specific contexts: Canadian dual-listed names (RY/TD/SHOP/BMO etc.) and US-index ETFs that have TSX equivalents (SPY→XSP/VFV, QQQ→XQQ/ZQQ).
**Principle:** The cheapest execution venue depends on (security, account currency, account type, trade size, position purpose). There is no single "cheapest broker" or "cheapest exchange" — only cheapest-for-this-trade.
**Variables that matter per trade:**
- Security availability on multiple exchanges (interlisted yes/no)
- Per-exchange commission rate, minimum, AND maximum-per-order cap
- FX conversion cost (avoided if security trades natively in account currency)
- Liquidity / bid-ask spread on each exchange
- Account type tax treatment (TFSA/RRSP withholding rules differ for US vs CAD listed)
- Position size (cap-binding for small trades, per-share-rate-binding for large)
**Rule:** System must reason about routing per trade, not assume a default. Implement as a routing module that takes trade-context inputs and returns optimal venue + currency. Captured as DECISIONS-253/254/255.

### L113 — Pair cost claims with source URL and verification date [critical/cost/auditing]
**Reinforcement of L111 with documentation requirement:** Every cost figure in any project document (PROJECT_PLAN, AUDIT pass, decision register, dashboards) must be paired with:
- Source URL where the figure was obtained
- Date of last verification
- Pricing structure detail (rate, min, max, third-party fees)
**Why:** Pricing changes. Six months from now, IBKR rates may shift, GPT costs may drop, TSX commission caps may revise. Without sourcing + dating, future Claude sessions or owner reviews cannot tell which figures are stale.
**Rule:** Cost figures without source+date are treated as untrustworthy. Future audits should flag undated cost claims for re-verification.

### L114 — When decision queue exceeds ~50, queue management itself becomes the bottleneck [critical/process/scalability]
**Observation (Pass 47, April 2026):** Decision count grew 116 → 185 → 200 → 206 → 253 → 257 → 294 across audit passes. At 227 PENDING decisions, owner cannot reasonably approve one-by-one — the management of the queue overwhelms the substance of the decisions.
**Failure mode:** Decisions accumulate faster than they resolve. Each new sweep adds 30-50 findings while resolution rate is ~2-5/turn. Queue grows monotonically. Eventually queue management dominates project work.
**Rule:** When PENDING decision queue exceeds 50, switch from per-decision approval to BATCH approvals by impact/cost theme. Use the triage matrix to enable "approve all in this band" workflows. Don't keep adding to a queue that nobody can process.
**Mechanism:** Triage matrix (impact/cost ratio) + bulk-approve-by-band + delegation of low-stakes decisions (defaults Claude can apply autonomously per CHECKLIST exception).
**Captured as:** DECISION-291 (triage-based bulk approval).

### L115 — Adversarial sweeps must be scheduled, not on-demand [critical/process/cadence]
**Observation (Pass 47):** Each comprehensive adversarial sweep yields 30-50 new findings. Three sweeps in a month yields 90-150 new decisions, far exceeding the resolution rate.
**Rule:** Schedule comprehensive sweeps quarterly (or per phase transition), NOT at every owner request. Between sweeps, only specific-trigger reviews (new bug, phase transition, owner question) — these produce ≤5 new decisions per pass.
**Why:** Continuous adversarial mode is structurally infeasible because the decision-resolution rate is much slower than the decision-discovery rate. Bounded cadence keeps the system tractable.
**Pre-conditions for next adversarial sweep:** Current PENDING queue triaged + bulk-approved down to <50 PENDING. Without that, additional findings only worsen the queue.

### L114 — Per-response CHECKLIST compliance must be visible, not just internalized [critical/process]
**Mistake:** During Round 1 audit work (Pass 52 Groups α + β), CHECKLIST.md was read once at session start and not restated per response. CHECKLIST.md line 4 explicitly requires: "State compliance visibly: 'Checklist: ✅ [each item]'". I treated this as a one-time gate rather than a per-response gate. Owner had to explicitly remind mid-session ("I hope you're referring to the checklist in all your responses").
**Why this matters:** The act of restating compliance forces a re-read, which catches mistakes earlier. Silent compliance ≠ verified compliance — the same pattern that produced 203 bugs (read-not-run testing). For doc-edit work specifically, the relevant items (CHECKLIST #1 thoroughness, #4 actually-helps, #5 what-can-go-wrong, #15 verify-by-running, #25 contradict-when-needed, #26 verify-assumptions, #27 stay-on-question, #28 retroactive-learning, #32 strict-approval) all silently went unchecked across multiple responses.
**Fix:** Every substantive response must include a visible CHECKLIST compliance block listing the items relevant to that response. For trivial responses (acknowledgments, clarifications), one-line check sufficient. For decision-resolution or code-edit responses, full list of applicable items with checkmarks.
**Rule:** No multi-step or impactful response is complete without a visible CHECKLIST compliance statement. The format is verifiable by the owner — not "I checked everything" but "Checklist: ✅ #1 thoroughness, ✅ #5 risk flagged, ✅ #15 verified-by-running."

### L115 — Inherited bugs in working files must be flagged the moment they surface, not silently fixed [critical/process]
**Mistake:** During Group β TRIAGE edits, I discovered the count headers were inflated by 11 (TRIAGE claimed 274 PENDING when AUDIT_INDEX.md had 263). The drift existed on origin/main before this session. I fixed the math, noted it in the commit message, and moved on — but did not (a) immediately add to LEARNINGS or CHECKLIST, (b) suggest a rule to prevent recurrence, or (c) check if the same drift pattern existed in other count fields elsewhere in the project.
**Why this matters:** Inherited bugs that go unflagged compound. The TRIAGE count drift had been propagating across multiple Sonnet sessions undetected. Without an explicit LEARNINGS entry, the next session that touches TRIAGE will inherit my partial fix and possibly drift again. Per CHECKLIST #28 (Retroactive Learning Application): "When mistakes are identified... Add to LEARNINGS.md... Add to CHECKLIST.md if recurring failure mode... Re-audit current conversation for other instances... Surface explicitly to the owner."
**Fix:** Added L115 + L116 to LEARNINGS, plus CHECKLIST #34 (count-derived-fields-must-regenerate-from-source-of-truth).
**Rule:** Any time an inherited bug is discovered during work — even if the fix is trivial — the discovery must be (a) added to LEARNINGS the same response, (b) checked against other instances in the same session, (c) surfaced explicitly to the owner. Not noted in a commit message and forgotten.

### L116 — Numerical claims must be verified at use, not inherited [critical/discipline]
**Mistake:** In the Group α handoff document I claimed "Net change: +121 / −41 lines" — a number generated by a prior session's git diff. I propagated this number into my handoff doc without re-running git diff against the actual sandbox state. The number happened to remain correct, but only by coincidence. Same pattern as L111 (cost figures from memory): treating a number as a fixed fact rather than a verified-at-use figure.
**Why this matters:** Numerical claims in handoff documents become evidence the laptop side checks against ("expected diff stat: ..."). If the number drifts because of intermediate edits, the laptop verification will fail and confidence in the handoff erodes. Worse, owner trust degrades when handoff numbers don't match reality.
**Fix:** Every numerical claim in any handoff, audit, or commit message must be regenerated at write time. No copying numbers from prior context.
**Rule:** Numbers in deliverables (line counts, decision counts, file counts, test counts, costs, percentages) require re-verification immediately before they're written. If verification cannot be done in-context, the number is omitted or marked as "approximate (last verified [date])." Same discipline as L111 (cost figures) extended to all numerical claims.

### L117 — Strategy-universe scope must be verified before any A/B framework or backtest decision [critical/methodology]
**Mistake (this session):** Presented Round 1 Batch 2 A/B framework decisions (DEC-205-209) without first verifying the strategy universe in scope. ICT/SMC strategies are explicitly in scope per DECISION-045 (joshyattridge/smartmoneyconcepts library) and Phase 0.D in PROJECT_PLAN, but I did not surface this when defining arm structures. Owner had to ask "are we testing ICT?" — should have been my question to owner, not the reverse.
**Why this matters:** The A/B framework with 4 arms (rules / full-agents / no-Risk / no-Bull-Bear) treats "rules" as a single coherent baseline, but rules ≠ rules+ICT. If ICT is added in Phase 0.D after the A/B framework is locked, the arm definitions become inconsistent. Worse, the 300-paired-trade sample size (DEC-207) was computed against a strategy universe that may not match the actual deployed universe.
**Why this matters more broadly:** Same pattern as L107 (premise questioning) and L103 (architectural recommendations without reading source). I knew the project documentation existed (AUDIT.md, PROJECT_PLAN.md, AUDIT_INDEX.md) but didn't grep for "ICT" or "smart money concepts" before presenting the A/B framework. CHECKLIST #30 (premise questioning) violated.
**Fix:** Added L117 + CHECKLIST #38 (strategy-universe verification before A/B / backtest decisions).
**Rule:** Before presenting any A/B framework, backtest design, or sample-size calculation, list every strategy class in the deployed-and-planned universe (technical, ICT/SMC, fundamental, smart-money, options, macro, sentiment, etc.) and verify each is accounted for in the framework. If a strategy class is in PROJECT_PLAN but not yet implemented, the framework must accommodate its future addition.

### L118 — Multi-timeframe ICT methodology decision is undecided and not in registry [critical/methodology/scope-gap]
**Owner-surfaced gap (this session):** Owner asked whether ICT strategies require mapping on higher timeframes and triggering trades on daily. The system currently fetches daily bars only (yfinance `interval="1d"`, no override in `backtest/data/cache.py`). PROJECT_PLAN does not specify ICT timeframe scope. DECISION-045 chose smartmoneyconcepts library but the library is timeframe-agnostic — the choice did not force the answer.
**Methodology impact:** Standard ICT methodology requires HTF (weekly/daily) bias + LTF (1h/15m/5m) entry. ICT applied to daily bars only abandons multi-timeframe context that is core to the methodology. Most ICT practitioners would not call daily-only ICT a faithful implementation.
**Why this matters:** Backtest results from daily-only ICT may produce poor signal quality not because ICT doesn't work but because the methodology is incomplete. Could lead to false negatives (rejecting ICT as a strategy class) or false confidence (accepting weakened signals as the "true" ICT performance).
**Fix:** New decision DECISION-343 to be added: "ICT/SMC timeframe scope — daily-only vs weekly-HTF + daily-trigger vs full multi-timeframe with intraday entries." Decision must be made before Phase 0.D begins (currently no firm date but is post-Stage-1 backtest).
**Rule:** Whenever a methodology library is adopted (DEC-045 chose smartmoneyconcepts), the accompanying methodology decisions (timeframe scope, parameter selection, signal aggregation) must be surfaced as separate decisions — not assumed by default.

### L119 — Always grep CLAUDE.md / AUDIT.md / PROJECT_PLAN before proposing to add a 'new' principle [critical/process]
**Mistake (this session):** Owner directed regime-conditional project philosophy ("we're looking for what works best in what regime, not universal strategies"). I responded by asking interpretation A/B/C, proposing to write to CLAUDE.md and PROJECT_PLAN, treating it as new ground. Owner had to ask "is this a part of the audit document?" prompting me to grep — which immediately found that CLAUDE.md lines 121, 134, 142, 189 already explicitly state per-regime strategy library philosophy ("different strategies for different regimes — not universal strategies"), DECISION-025 documents regime-conditional weighting since Pass 19, BUG-129 and BUG-175 capture the gaps, AUDIT.md has detailed analysis in sections 4.8 and 45.6.3.
**Why this matters:** This is wasted owner attention. Worse, my proposal was about to bloat CLAUDE.md with redundant content, possibly creating contradictions with already-documented language. Same root cause as L107 (premise questioning) and L117 (strategy-universe verification before A/B framework decisions): I made a recommendation without reading what was already in the project.
**Common pattern across L107, L117, L119:** Claude proposes new content / new direction / new framework without first grepping the existing project for prior art. CHECKLIST #26 (Assumption Validation) was supposed to catch this — "verify via web_search, file read, or code execution before recommending." Reading CLAUDE.md is one of the cheapest verifications possible — should be reflex.
**Fix:** Added L119 + CHECKLIST #40 (project-prior-art grep before recommending any new principle / direction / framework).
**Rule:** Before responding to any owner direction that proposes a new principle, philosophy, framework, or architectural approach, grep CLAUDE.md + PROJECT_PLAN.md + AUDIT.md + AUDIT_INDEX.md for the relevant terms FIRST. If prior art exists, surface it before proposing additions. Treat new-principle recommendations as a search problem before a writing problem.

### L120 — Handoff pre-flight must explicitly check for dirty working tree, not just remote sync [critical/process]
**Mistake (this session):** Round 1 handoff document specified pre-flight checks for git remote sync (`git fetch`, `git log origin/main..main`, `git log main..origin/main`, `git rev-parse HEAD`) but did NOT explicitly check for dirty working tree (uncommitted changes / untracked files). When laptop ran the pre-flight, the output showed 480+ modified Parquet files (Phase 1B cache download in-progress) plus an untracked `0,` artifact. Patch would have applied cleanly to the doc files but a careless `git add -A` could have included the cache files in the Round 1 commit.
**Why this matters:** "Synced with origin" ≠ "ready for new commit." A working tree can have:
  (a) unrelated uncommitted work that must be preserved (Phase 1B cache) — must commit/stash first
  (b) untracked artifacts (the `0,` file) — must clean up
  (c) tracked-but-uncommitted config (`.claude/settings.local.json`) — must gitignore or skip
Each of these is a separate concern that the standard remote-sync check does not catch.
**Fix:** Added L120 + CHECKLIST #41 (handoff pre-flight must include `git status --short` check; non-empty output halts the handoff for owner reconciliation).
**Rule:** Every handoff document's pre-flight section MUST include `git status --short` as a check. Output must be empty (or contain only files we explicitly intend to modify) before patch application proceeds. Non-empty status halts the handoff for owner-driven reconciliation. CHECKLIST #16 said to run git status before git commands; this generalizes it specifically to handoff pre-flights.

### L121 — Prior-art grep must search both DEC and BUG, not just DEC [process/discipline]
**Mistake (this session, Pass 52, twice):** Twice in this session I proposed new decisions for gaps that were already documented. First: DEC-346 categorical matrix overlapped existing DEC-066/100 (caught by owner). Second: proposed DEC-349 for API endpoint inventory + agent-feed mapping; owner asked "is it part of existing audit?" — grep revealed BUG-190 (Quiver endpoints not prefetched, OPEN since Pass 18) and BUG-191 (no prefetch validation, CRITICAL OPEN since Pass 18) covered most of it.
**Why this matters:** The audit catalog is large. Decisions and bugs are tracked separately even though stored in the same INDEX file. A decision-only grep misses bug-tracked gaps. Multi-pass audits accumulate prior art across both categories; failing to search both wastes time and produces duplicate tracking.
**Fix:** Added CHECKLIST #42. Prior-art grep MUST include both DEC and BUG searches for any topic before proposing a new entry.
**Rule:** Before any new decision/bug proposal, run both:
- `grep "DECISION-" AUDIT_INDEX.md | grep -i "<keyword>"`  
- `grep "BUG-" AUDIT_INDEX.md | grep -i "<keyword>"`
Both required. Refines #40.

### L122 — When asked "is X already in audit," check audit BEFORE proposing X [critical/process]
**Mistake (Pass 52, third occurrence in single session):** Owner asked about testing/batch discipline. Three relevant decisions (DEC-098, DEC-221, DEC-222, DEC-265) and CHECKLIST #29 (STOP-EARLY-ON-BUDGET) plus L86/L95/L102 all extensively cover the topic. I should have surfaced these first instead of treating it as a new question. Pattern repeats from earlier same-session: DEC-346 categorical (overlap with DEC-066/100), DEC-349 endpoint inventory (overlap with BUG-190/191).
**Why this matters:** Owner has been reminding me to refer to audit each time. Each repetition wastes attention and erodes trust in claude-side discipline. The audit is the source of truth; my proposing things that are already there means I'm reading the audit shallowly.
**Fix:** When owner's prompt contains words like "is it already audited," "already flagged," "have we tracked this," — STOP. Do NOT continue drafting. Run grep on AUDIT_INDEX, AUDIT.md, LEARNINGS.md, CHECKLIST.md for the topic FIRST. Show owner the prior art that exists. THEN respond.
**Rule:** Owner phrasing "is X in audit / already flagged / already tracked" = mandatory full-search first. No proposal until search completes. Refines L121 (which only added BUG search) — this adds the discipline of recognizing the trigger phrase.

### L123 — Audit by reading code is insufficient for data-consumption logic [critical/process]
**Mistake (Pass 52, owner-flagged):** 40+ audit passes did not catch BUG-270/271/272/273/274/275/276/277 — eight HIGH-severity bugs in smart-money data consumption code. Each is a schema mismatch, type mismatch, or empty-cache issue that is invisible to read-audit unless the auditor has both code AND actual data shape in front of them. Owner spent $150 on a Phase 1B agent run where every smart-money signal was silently broken.
**Why this matters:** Data-consumption code passes static review — types check out, exception handlers exist, code reads as normal. The bug only manifests when the cache schema doesn't match the code's column-name/type assumption. Reading is insufficient. Running on real data is required.
**Fix:** L123 + CHECKLIST #44. For any data-consumption code under audit:
  1. Identify the cache file/source the function reads
  2. Verify cache is populated for at least 1 known ticker (e.g., AAPL)
  3. Call the function with that ticker, date inside cache range
  4. Assert return is non-default
  5. If default returned: investigate schema/type/filter assumption mismatch
**Rule:** Audit of data-consumption code is incomplete without runtime execution. 90 minutes of runtime-probe discipline (Stage 5.5) caught 5 bugs that 40+ read-audit passes missed.

## L124 (Pass 52) — Mandatory per-response checklist compliance statement (owner-elevated rule)

**Trigger:** Owner Pass 52 direction — "Make referring to checklist compulsory every time you respond. Add this mandatory requirement to claude md if not already present."

**Why this matters:** Existing CLAUDE.md line "Run CHECKLIST.md before every suggestion or execution" was insufficient — it could be silently violated without the response itself being visibly non-compliant. Owner has had to remind multiple times to refer to checklist + audit. The fix elevates the rule to per-response visibility: every response must end with a compliance statement enumerating which items were satisfied. If absent, the response itself is non-compliant and easier to flag.

**Rule (CLAUDE.md elevated, CHECKLIST #45 added):** Every response — full or partial — must end with a visible "CHECKLIST: ✅ compliance" block. Items not relevant to the turn can be omitted; items applied must be explicitly listed. Exception: pure tool-use turns with no user-facing prose still close with a compliance statement before yielding.

**Past mistakes corrected:** Pass 52 itself had ~3 lapses where I drafted deliverables before running CHECKLIST #43 prior-art grep, requiring re-work. Per-response compliance statement makes the discipline visible-by-default.

**Pair:** L124 + CHECKLIST #45. Owner has authorized strong action if the rule is repeatedly violated.

## L125 (Pass 52) — Strategy/feature coverage checks must cross-reference PROJECT_PLAN.md alongside AUDIT.md and code (owner directive)

**Trigger:** Owner Pass 52 — "strategy coverage check - should be mapped against audit and project plan both."

**Why this matters:** I previously performed strategy-coverage checks by walking screener.py + AUDIT_INDEX only. This misses scope that was DESIGNED in PROJECT_PLAN.md but never implemented in code or logged in audit. Such drift is invisible to my prior check pattern. PROJECT_PLAN is the design-intent source of truth; gaps relative to PROJECT_PLAN are previously-committed scope that drifted out, distinct from gaps the audit might flag.

**Rule (CHECKLIST #46):** For any strategy/feature/signal coverage question, the check must include three sources:
1. **Code grep** (e.g., `screener.py`, `technical.py`, `exit_strategies.py`) — current implementation state
2. **AUDIT_INDEX grep** — what's been logged as bug or decision
3. **PROJECT_PLAN.md grep** — what was DESIGNED to exist

A gap is real if any of: (a) audit logs it as gap, (b) PROJECT_PLAN specifies it but code doesn't implement, (c) practitioner research says it should exist (lowest priority — yields to PROJECT_PLAN when conflict).

**Past mistake corrected:** Pass 52 side-note responses to owner ("ALL price action strategies including retest?", "S/R for institutional interest?") only checked code + audit. Did not check PROJECT_PLAN. Findings were valid but incomplete — may have under-counted gaps or proposed new decisions for things already in PROJECT_PLAN scope.

**Pair:** L125 + CHECKLIST #46. Per owner standing exception for process-discipline files.

## L126 (Pass 52) — Prior-art grep must scan AUDIT.md FULL TEXT, not just AUDIT_INDEX.md table

**Trigger:** Owner Pass 52 — "You missed pending decisions in audit md yet again." 3rd recurrence this session.

**Why this matters:** AUDIT_INDEX.md has ~1-line summaries per decision/bug. AUDIT.md has the substantive content including:
- Pass 39 Section 9 strategy-category gap inventory (DEC-099 + 11 categories + 17+ categorical breakdowns)
- BUG-139 through BUG-167 inline-only bug entries (29 strategy/signal gap bugs)
- Pass 13 retest section (full retest semantics + BUG-111 context)
- Pass 39 Section 18 plain-English strategy listings

**Past mistakes (Pass 52, 3 recurrences):**
1. Stage 5.5 initial 5 candidates — 3 were duplicates of BUG-185/186/053+181 (caught by checking only after drafting)
2. AUDIT_RESOLVED.md proposal — already addressed by AUDIT_INDEX (caught only via conversation_search of prior session)
3. DEC-350/351/352/354 logged Pass 52 — DEC-351 = duplicate of BUG-147/151; DEC-354 = merged into DEC-099; all detected only when owner re-prompted "you missed pending decisions in audit md yet again"

**Common root cause:** grep targeted AUDIT_INDEX table only; INDEX has short labels not substantive content. The 11-category gap audit (Pass 39 Section 9) is ~80 lines of detail in AUDIT.md but only 4 one-liners in INDEX. Easy to miss.

**Rule (CHECKLIST #47):** Prior-art grep for any new bug/decision proposal must include:
1. AUDIT_INDEX.md grep (existing CHECKLIST #43 — top-line table)
2. **AUDIT.md FULL TEXT grep** (new — substantive content)
3. PROJECT_PLAN.md grep (existing CHECKLIST #46)
4. Code grep
A finding only counts as "no prior art" when ALL FOUR sources confirm absence. INDEX is necessary but not sufficient.

**Pair:** L126 + CHECKLIST #47.

## L127 (Pass 52) — Enumerating in prose ≠ logging as decision (owner directive)

**Trigger:** Owner Pass 52 — caught me with: "I want each and every price action strategy to be tested!!!!!!!!! CRITICAL AND MOST IMPORTANT REQUIREMENT!" after I had listed 7 chart pattern classes in Pass 52 prose during Stage 6 / strategy-coverage discussion but never converted them into logged decisions. Owner had to ask the direct question to surface the gap.

**Why this matters:** Audit reports, deliverables, and chat responses are different artifacts than the audit catalog. Information in deliverable prose is owner-readable but NOT decision-tracked. Future passes can search AUDIT_INDEX/AUDIT.md for "what's logged" and miss anything that lived only in prose. The catalog is authoritative; the prose is communication.

**Pattern of failure:** During Pass 52 specifically, three lapses:
1. Stage 5.5 initial bug candidates drafted before prior-art grep (caught by CHECKLIST #43)
2. AUDIT_RESOLVED.md file proposal made before conversation_search of prior sessions (caught by CHECKLIST #43 extension)
3. **Chart pattern enumeration listed in prose but not logged as decisions (caught only by direct owner pushback)**

The common root: I treat "I mentioned it" as equivalent to "it's in the audit." It's not.

**Rule (CHECKLIST #48):** Any time a response contains a list of:
- "things to do" / "gaps" / "patterns to add" / "questions to consider" / "items remaining"

The same response must convert each enumerated item into one of:
- A logged decision (DEC-N PENDING) in AUDIT_INDEX + substantive section in AUDIT.md
- A logged bug (BUG-N OPEN) similarly
- An explicit deferral with reasoning ("not logging because [reason]") — and even then, the deferral itself should be discoverable

**Pair:** L127 + CHECKLIST #48. Per owner standing exception for process-discipline files.

**Past reference:** This is L121-L126 family — all about "log things properly." L127 closes a specific recurrence pattern (prose-to-decision conversion).

## L128 (Pass 52) — Caveats must be collected in LIMITATIONS_CAVEATS_ASSUMPTIONS.md, not buried in audit prose (owner directive)

**Trigger:** Owner Pass 52 directive — "Document all caveats. Create a separate limitations/caveats/assumptions md file and keep adding to it."

**Why this matters:** AUDIT.md had 56 mentions of "caveat" and "honest caveat" scattered across 20,000+ lines. Caveats inline in audit prose are invisible to stakeholder review. A live trading system that ships with known biases must be transparent about them — but only if those biases are surfaced in one discoverable place. A 2.0 Sharpe is a different claim if the system has documented survivorship bias than if it doesn't. Reporting must reference the caveats file alongside any backtest result.

**Rule (CHECKLIST #49):** Every time a decision resolves WITH CAVEATS, or a runtime probe surfaces a known limitation, or a methodology choice has an honest tradeoff:
1. Log the caveat in LIMITATIONS_CAVEATS_ASSUMPTIONS.md as CAV-NNN entry
2. Cross-reference from the source decision/bug entry in AUDIT.md
3. Append-only — never delete; mark RESOLVED Pass N if the underlying issue resolves
4. Format requirements: Source / Status / Caveat / Operational impact / Forward-link

**Past mistake corrected:** Pre-Pass-52, 56 caveats were buried in audit prose with no consolidated registry. Stakeholders reading audit reports could miss the cumulative bias profile of the system. L128 closes the gap.

**Pair:** L128 + CHECKLIST #49. Per owner standing exception for process-discipline files.

## L129 (Pass 52) — Caveats/assumptions/limitations also inline in PROJECT_PLAN.md for readability (owner directive, additive to L128)

**Trigger:** Owner Pass 52 — "Retain caveats/assumptions/limitations inline in the project plan for readability."

**Why this matters:** L128/CHECKLIST #49 created LIMITATIONS_CAVEATS_ASSUMPTIONS.md (CAV-NNN registry, 24 entries Pass 52). That file is audit-grade — append-only, formal cross-references, full operational impact descriptions. Useful for audit walkthroughs and stakeholder review of system biases. **But PROJECT_PLAN.md is the working document** — the place owner reads to understand current scope and decisions. Caveats living only in a separate file mean someone reading PROJECT_PLAN sees only the "happy path" — what the system DOES, without the constraints under which it operates.

**Rule (CHECKLIST #50):** When a section of PROJECT_PLAN.md describes a feature, methodology, or data source that has a known caveat/limitation/assumption from CAV-NNN registry:
1. The caveat must ALSO appear inline in PROJECT_PLAN.md at the relevant section
2. Use a brief inline call-out — not the full operational-impact text (that stays in CAV file)
3. Format: "*Caveat: [short description] (CAV-NNN)*" inside the section, not in a separate appendix
4. Cross-reference the CAV-NNN ID so the reader can dive deeper if needed
5. When a decision RESOLVES a caveat, BOTH places update (the inline note becomes "Resolved Pass N — see CAV-NNN" rather than disappearing — preserves historical context for re-reading)

**Past mistake corrected:** Pre-this-rule, PROJECT_PLAN read as "we use yfinance OHLCV with adjusted-close; we use current S&P 500 list; PIT correctness is non-negotiable" — three statements that look mutually consistent. **They are not** — DEC-298 + DEC-303 caveats are exactly the kind of "non-negotiable" violations the project tolerates as Phase 1 acceptable. Reader of PROJECT_PLAN alone misses this. Inline caveats fix the readability gap.

**Distinction from L128:** L128/CHECKLIST #49 = formal registry (LIMITATIONS_CAVEATS_ASSUMPTIONS.md); audit-grade. L129/CHECKLIST #50 = readability inline (PROJECT_PLAN.md); stakeholder-grade. Both required; neither sufficient alone.

**Pair:** L129 + CHECKLIST #50. Per owner standing exception for process-discipline files.

## L130 (Pass 52) — Do not infer approval beyond owner's explicit statement (owner pushback)

**Trigger:** Owner Pass 52 — "NEW DEC-364 - approved you rec. NEW DEC-365 - approved you rec. NEW DEC-366 - approved you rec. Were these approvals given or you are inferring?"

**Honest answer:** No, those approvals were not given. I inferred them.

**What happened:**
- Owner's prior turn said only: "Tier 3 - expand to 100. Add lithium, base metals ETFs as well"
- I had proposed DEC-363/364/365/366 in the response BEFORE that owner message
- Owner's two-directive message was a NARROW directive (Tier 3 size + lithium/base metals additions)
- I logged DEC-363 as "owner-approved" with 8 ETFs (LIT + DBB + COPX + USO + UNG + DBC + DBA + CPER) when owner approved 2-3 (lithium + base metals)
- I logged DEC-364 as "owner-approved" with full Tier 2+3 backtesting activation when owner approved only Tier 3 size
- I logged DEC-365 (Russell expansion) as approved based on an earlier-turn directional statement ("no need to restrict to just top 500 tickers") that was a question-phase remark, not an explicit approval
- I logged DEC-366 (liquidity floor) as approved with no owner statement at all about liquidity floor

**Why this matters:** Process integrity depends on the boundary between "Claude proposed X" and "owner approved X" being crisp. When Claude logs proposals as approvals, the audit becomes unreliable — a future review cannot trust that "owner-approved" labels mean what they say. Worse: caveats that ride on those decisions (CAV-025 through CAV-031) all assume the parent decision is approved, which compounds the misrepresentation.

**Pattern relationship to L127/CHECKLIST #48:**
- L127/#48: Enumerating in prose ≠ logging as decision (failure to convert prose to logged decisions)
- **L130/#51 (NEW): Owner's narrow directive ≠ blanket approval of broader proposal (failure in opposite direction — over-converting)**

Both are boundary-discipline failures around what's officially decided vs informally discussed. L127 covers the under-logging direction; L130 covers the over-logging direction.

**Rule (CHECKLIST #51):** Before logging any decision as "owner-approved":
1. Identify the EXACT verbatim owner directive that approves it
2. Quote it (or its substance) in the decision entry: "Per owner directive: '[verbatim]'"
3. If the owner directive is narrower than my proposal:
   - Log only what was explicitly approved (narrow scope)
   - Keep the broader proposal as PROPOSED (not approved) with a note that it AWAITS OWNER APPROVAL
4. "Agree with recs on rest" only refers to recommendations made BEFORE that statement, not after — and only refers to recommendations the owner could see at that point in conversation
5. Silence is not approval. Owner not addressing a proposal explicitly = it remains PROPOSED, not approved
6. Directional statements during question/exploration phases ("no need to restrict to just top 500") are DIRECTIONAL, not APPROVAL. They guide subsequent proposals; they do not authorize specific implementations.

**Past failure documented:** Pass 52 commit `f3e43580` logged DEC-363/364/365/366 as "owner-approved" — corrected this turn. CAV-025 through CAV-031 status downgraded from ACTIVE to PROVISIONAL where the parent decision was not actually approved.

**Pair:** L130 + CHECKLIST #51. Per owner standing exception for process-discipline files.

## L131 (Pass 52, fifth process recurrence) — Ambiguous owner directives default to lower-impact action; never infer approval

**Trigger:** Owner Pass 52 — said "Lets proceed" after I presented 6 Theme 3 recommendations. I interpreted as "approve all 6 + proceed with logging 13 sub-decisions" (logged commit 36a55f08, 13 new decisions, 5 new caveats). Owner clarified meaning: "lets go through the next batch" (move to Theme 4 without approving Theme 3). I rolled back commit 36a55f08.

**Why this matters:** L130/CHECKLIST #51 (added Pass 52 commit 3297c690) explicitly forbids inferring approval beyond owner's direct words. I just violated that rule on the very next batch. This is the FIFTH Pass 52 process recurrence:
1. Stage 5.5 candidates drafted before prior-art grep
2. AUDIT_RESOLVED.md proposal before conversation_search
3. Chart pattern enumeration listed in prose but not logged
4. DEC-365/366 + broadened scope of DEC-363/364 logged as approved when only narrow directives given
5. **THIS ONE — "Lets proceed" interpreted as approval rather than "move on"**

**Pattern root cause:** Brief owner directives have multiple valid interpretations. "Lets proceed", "Continue", "Move on", "Next" can all mean either (a) execute current batch + advance, or (b) advance without executing current batch. I default-assume (a) because it's higher-throughput; owner often means (b) for review-pace control.

**Rule (CHECKLIST #52):** When an owner directive is ambiguous between "execute then advance" vs "advance without executing":
1. Default to LOWER-IMPACT interpretation (advance without executing)
2. If genuinely uncertain, ASK explicitly with the two interpretations before acting
3. Bias toward ask over assume — one extra clarification round is cheaper than rolling back logged decisions
4. Brief directives like "proceed", "continue", "move on", "next", "go", "ok" almost always mean "advance, don't execute" when prior turn was a recommendation set awaiting approval

**Specific patterns to recognize:**
- Prior turn ended with explicit approval ask ("Standing by for owner direction") → "proceed" likely means "advance without approval"
- Prior turn ended with implementation plan ("Will execute these now") → "proceed" likely means "go ahead"
- Owner uses words like "approve", "go ahead", "do it", "yes" → execute
- Owner uses words like "proceed", "continue", "next", "move on" → advance, do not execute
- When in doubt: ASK

**Pair:** L131 + CHECKLIST #52. Per owner standing exception for process-discipline files.

**Honest meta-observation:** L130/CHECKLIST #51 was supposed to fix this class of error. It didn't, because the failure mode shifted from "inferring approval from silence" to "inferring approval from ambiguous brief directive." L131/CHECKLIST #52 narrows the gap further. If a sixth recurrence happens, the pattern is structural and warrants a more aggressive default (e.g., ALWAYS confirm before any commit involving formal logging).

## L132 (Pass 52, sixth process recurrence — pattern: industry-heuristic-without-scope-check) — Grounded-recommendation format mandatory

**Trigger:** Owner Pass 52 — caught three out of five DEC-082/083/085 recommendations with factual errors:
- DEC-082 proposed thresholds for 2008/2020 periods our backtest doesn't cover (cache: 2021-2024)
- DEC-083 proposed 300-trade floor that excludes legitimate event-driven strategies (~25 trades for spinoff cases)
- DEC-085 listed 5 macro indicators when `backtest/data/macro.py` already pulls 9

Owner: "Given the errors in your recommendations, how can i be sure you are thinking through your recommendations deeply, broadly and comprehensively. I am not a tech person so i cant verify your suggestion for bugs and code"

**Why this matters:** This is the sixth Pass 52 process recurrence and a NEW pattern class — not "logging without approval" (L130/L131) but "generating plausible-sounding recommendations from industry pattern-matching without verifying scope/feasibility/existing-infrastructure fit." The failure mode is invisible to surface-level review and undermines owner trust because recommendations sound expert while being factually wrong.

Pattern of all 6 Pass 52 process recurrences:
1. Stage 5.5 candidates drafted before prior-art grep (L114-L120)
2. AUDIT_RESOLVED.md proposal before conversation_search (L120 expansion)
3. Chart pattern enumeration listed in prose but not logged (L127)
4. DEC-365/366 + broadened DEC-363/364 logged as approved when only narrow directives given (L130)
5. "Lets proceed" interpreted as approval rather than "move on" (L131)
6. **THIS ONE — Industry-heuristic recommendations without scope/feasibility/infrastructure check (L132)**

**Pattern root cause:** Recommendations sound authoritative because they're industry-pattern-matched ("best practice is min 300 trades for Bonferroni"), but pattern-matching to general quant practice ≠ pattern-matching to OUR specific 4-year × 509-ticker × 2021-2024 system. Industry-correct ≠ project-correct.

**Rule (CHECKLIST #53):** Every recommendation must include grounded-recommendation evidence in the response itself, before stating the recommendation:
1. **CURRENT STATE** — paste actual grep output of relevant code, not summary. ("`backtest/data/macro.py` SERIES_MAP currently has: VIX, DGS10, T10Y2Y, FEDFUNDS, UNRATE, CPIAUCSL, T10YIE, BAA10Y, DXY = 9 series")
2. **PROJECT SCOPE** — date range, universe size, period coverage from cache + PROJECT_PLAN ("Cache covers 2021-01-04 to 2024-12-31 across 495 tickers")
3. **SCOPE FIT CHECK** — explicit yes/no with math ("Recommendation X requires 2008 data → cache has no 2008 → does NOT fit current scope")
4. **EXISTING INFRASTRUCTURE CHECK** — does anything already do part of this? ("DEC-085 macro factors duplicate `macro.py` — must extend, not replace")
5. **FEASIBILITY MATH** — for any numeric threshold, compute what it implies for our data ("300 trades over 4 years × 509 tickers requires ~5 fires/year/ticker — daily-frequency strategies easily reach this; event-driven (~0.05 fires/year/ticker) cannot")

If any of the 5 cannot be answered: flag the recommendation as `UNVERIFIED — pattern-match only` rather than presenting it as confident.

**Confidence labels recalibrated:**
- "Verified: [list of grep checks performed]" — concrete verification
- "Pattern-matched: [industry source]" — heuristic, not project-specific
- NEVER present a "Confidence: HIGH" label without showing the verification work

**Pair:** L132 + CHECKLIST #53. Per owner standing exception for process-discipline files.

**Honest meta-observation:** Five prior process recurrences targeted "logging discipline" (when/whether to log). This recurrence targets "recommendation discipline" (whether the recommendation is grounded). Different failure surface. L132/CHECKLIST #53 is the first rule addressing recommendation quality directly. If this rule's introduction is followed by another grounded-recommendation failure, the pattern would warrant: every numeric threshold or scope-dependent claim in a recommendation must be preceded by a Python computation cell showing the math, treated as a hard procedural requirement.

## L133 (Pass 52) — Test-run audit gate: empirical validation of recommendations before full implementation (owner directive)

**Trigger:** Owner Pass 52 directive: "audit recommendations after limited-sample test run... after we prefetch ALL OHCLV and API data within agreed scope. When - after we are done reviewing the entire audit file. What's the audit checklist after the run? Agreed. But i want to log your recommendation, decision, and your suggestion on what we should be testing and output on run and binary on Test_Mismatch"

**Why this matters:** Sixth Pass 52 process recurrence (L132) was about recommendations being industry-pattern-matched without scope/feasibility checks. Even with grounded-recommendation format (CHECKLIST #53), recommendations remain theoretical until validated against actual system behavior. The test-run gate makes empirical validation a hard precondition before any full implementation. Catches errors that survive code-grep + scope-check + feasibility-math because those checks are static; only running the system reveals what actually happens.

**Sequence (mandatory order):**
1. **Full data prefetch** complete per agreed scope (DEC-410 API audit, all OHLCV including DEC-411 2018-extension, all API endpoints scoped in)
2. **All themes reviewed** — every audit decision walked through with owner approval/rejection
3. **Limited-sample test run** — 10 tickers × 60 days × current strategies → produces actual trade logs, signal fires, regime tags, metrics
4. **Per-decision validation table** — for EVERY owner-approved decision, document:
   - Decision ID
   - The recommendation (what we said we'd do)
   - The suggested test signal/output (what we expect to see in test data if rec is correct)
   - Binary TEST_MISMATCH flag (true/false based on test output vs expectation)
5. **TEST_MISMATCH triage** — recommendations failing the test require investigation/revision before full implementation; recommendations passing proceed to implementation

**Rule (CHECKLIST #54):** Decisions in AUDIT_INDEX.md must include three additional fields populated when ready for test-run validation:
- `test_signal` — what to look for in test output (e.g., "DEC-388 VIX SMA: regime classifier output should NOT flip more than 2x per month in test sample, vs current behavior of flipping ~5x per month")
- `test_output_expected` — concrete expected value or pattern (e.g., "regime_change_count <= 2 over 60-day window")
- `test_mismatch_action` — what we do if test fails (e.g., "investigate VIX threshold sensitivity; may need 7-day SMA instead of 5-day")

**Output document:** `AUDIT_TEST_RUN_RESULTS.md` — generated AFTER test run completes. One row per owner-approved decision. Reviewable by owner (binary pass/fail clear without technical interpretation).

**Pair:** L133 + CHECKLIST #54. Per owner standing exception for process-discipline files.

**Retroactive scope (Pass 52 owner directive amendment):** Per owner directive "you should apply this retroactively as well for all decisions already in the index file" — DEC-417 scope is ALL ~419 decisions in AUDIT_INDEX.md, not just Pass 52 ones. Older decisions logged in earlier passes (Pass 38/39/40/etc.) also need test_signal/test_output_expected/test_mismatch_action populated. Effort ~35 hrs total. Older decisions may be flagged `OBSOLETE_BY_TEST_RUN` if system has evolved since original logging.

**Honest meta-observation:** This rule is the strongest defense yet against my pattern-match-without-verification failure mode. CHECKLIST #43 (prior-art grep) catches duplicates. CHECKLIST #46 (three-source check) catches scope misfits. CHECKLIST #53 (grounded-recommendation format) catches feasibility errors. CHECKLIST #54 (test-run audit) catches everything that survives the first three by requiring empirical confirmation. If a recommendation passes all four checks AND survives test-run validation, it's genuinely deployment-ready.

## L134 (Pass 52) — Phase scope check: distinguish patch-level vs system-design-level decisions

**Trigger:** Pass 52 four-turn architectural recurrence pattern. Owner caught:
1. Sector concentration entry vs exit category error (DEC-070)
2. Phase 1B-α vs Stage 3+ scope error (DEC-070)
3. Static-vs-dynamic exit framing (Theme 7)
4. **Single-dimension regime slicing vs multi-dimensional optimization framework (DEC-068/069 vs DEC-422)**

**Why this matters:** L132/CHECKLIST #53 grounded format catches static checks (current state grep, scope, feasibility, infrastructure) but misses **architectural framing.** Decisions like DEC-068 ("add bootstrap CI") and DEC-069 ("per-regime exit selection") were getting walked through as patches when they were actually pieces of a larger system-design question (DEC-422: full dimensional space optimization). Walking patches one at a time obscures that the right answer requires reframing the system level.

**Owner directive verbatim:** "Phase 1 is not a patch. Its to identify best strategies in the entire possible dimensional space before we add an AI agent on top of it."

**Rule (CHECKLIST #55):** Before walking through a Phase 1B-α decision, explicitly ask:

1. **Is this decision patch-level or system-design-level?**
   - **Patch-level:** Fixes a specific bug, adds a specific metric, addresses a known gap. Stand-alone scope. Belongs in normal batch review.
   - **System-design-level:** Defines what the phase delivers, how outputs are structured, what dimensions the analysis covers. Cannot be batched with patches; needs focused walkthrough as its own decision.

2. **If system-design-level:** does it warrant its own decision rather than being subsumed into a patch decision? Examples:
   - DEC-422 (dimensional space optimization) is system-design-level → its own decision
   - DEC-068 (bootstrap CI) is patch-level → normal batch
   - DEC-069 (per-regime exit) was framed as patch-level but actually proposed system-design-level changes (per-regime selection mechanism) → got SUPERSEDED when DEC-422 captured the broader frame

3. **Architecture-fit check:** does this recommendation operate at the right level of abstraction for what the system needs to do? Or am I pattern-matching to a textbook concept that fits a different system architecture?

**Pair:** L134 + CHECKLIST #55. Per owner standing exception for process-discipline files.

**Honest meta-observation:** L132/CHECKLIST #53 (grounded format) and L133/CHECKLIST #54 (test-run audit) are static-check rules. L134/CHECKLIST #55 is the first rule about WHICH FRAMING level a decision belongs to. The four architectural recurrences in Pass 52 weren't caught by static checks because they were framing errors, not factual errors. Going forward: when a decision involves a phase deliverable (Phase 0/1B/2/3/4), explicitly classify patch vs system-design BEFORE the grounded-format walkthrough. If it's system-design-level and not yet logged as such, propose elevating it to its own decision before continuing the patch-level batch review.

**Pattern lineage Pass 52:**
- L114-L131: logging discipline rules
- L132/CHECKLIST #53: grounded-recommendation format (recommendation quality)
- L133/CHECKLIST #54: test-run audit gate (empirical validation)
- L134/CHECKLIST #55 (THIS): phase scope check (architectural framing)

These four rules form the layered defense:
1. CHECKLIST #43/#46/#47: prior-art + three-source + full-text (catch duplicates)
2. CHECKLIST #53: grounded-recommendation format (catch scope/feasibility errors)
3. CHECKLIST #54: test-run audit (catch empirical-failure errors)
4. CHECKLIST #55: phase scope check (catch architectural-framing errors)

If this rule is itself followed by a fifth-class architectural recurrence, the right fix is probably "slow down on recommendations" not another checklist item.

## L135 (Pass 52) — Phase scope filter discipline: only log decisions affecting current focus phases

**Trigger:** Owner Pass 52 verbatim: "in all decisions and bugs, we will only focus on those that affect phase 1 and 2 for the time being" → clarified to "Phase 0 and 2. Interpretation B" (Phase 0 sub-phases + Stage 2; Stage 3/4/5 OUT of scope).

Caught lapse: Theme 6 (DEC-129/130/132) approved as Stage 3→4 gates when scope filter was implicit. Same L132/L134 root pattern.

**Why this matters:** L132/CHECKLIST #53 (grounded format) catches static scope errors. L134/CHECKLIST #55 (phase scope check) catches patch-vs-system-design errors. **L135/CHECKLIST #56 catches FORWARD-LOOKING vs CURRENT-FOCUS errors:** decisions that are technically correct for Stage 3+ but irrelevant to current Phase 0+Stage 2 focus.

**Rule (CHECKLIST #56):** Every decision walkthrough must include explicit scope-filter check:
1. **What phase does this decision primarily affect?** (Phase 0 sub-phase / Stage 1 / Stage 2 / Stage 3 / Stage 4 / Stage 5)
2. **Is that phase in current owner-defined focus?** (current focus per Pass 52: Phase 0 + Stage 2)
3. **If NOT in focus:** mark DEFERRED_TO_<TARGET_STAGE>; do not approve in current batch
4. **If IN focus:** proceed with normal walkthrough

**Catches:** Stage 3+ scope decisions getting batched with Phase 0/Stage 2 patches; future-deployment concerns leaking into current backtest validation work.

**Layered defense expanded to 6 levels (Pass 52):**
- CHECKLIST #43/#46/#47: catch duplicates (prior-art + three-source + full-text)
- CHECKLIST #53: catch scope/feasibility errors (grounded-recommendation format)
- CHECKLIST #54: catch empirical-failure errors (test-run audit gate)
- CHECKLIST #55: catch architectural-framing errors (phase scope = patch vs system-design)
- **CHECKLIST #56 (NEW): catch focus-phase scope-filter errors (Stage 3+ vs current Phase 0+Stage 2)**
- Owner adversarial review (informal, ongoing): catches everything else

**Pair:** L135 + CHECKLIST #56. Per owner standing exception for process-discipline files.

**Honest meta-observation:** This is the seventh Pass 52 process recurrence (per L132 lineage). Pattern of process-discipline rules is now substantial:
- L114-L131: logging discipline
- L132: grounded-recommendation format (scope/feasibility)
- L133: test-run audit gate (empirical validation)
- L134: phase scope check (architectural framing)
- **L135 (THIS): focus-phase scope filter (forward-looking deferral)**

Each new rule addresses a different surface of the same underlying L132 root cause: pattern-matching to "what a good system should have" without checking what THIS system, at THIS phase, actually needs. Owner's catches are increasingly subtle scope errors that broader rules don't catch.

If a 7th-class architectural recurrence emerges after L135, the right fix is no longer additional procedural rules — it's an explicit pre-walkthrough scope-clarification step where I ask owner before walking through any phase-deliverable decision: "what phases are in current focus?"

## L136 (Pass 52) — Use-case mapping discipline: design recommendations against THIS system's actual use cases, not generic best-practice templates

**Trigger:** Owner Pass 52 turn 16 verbatim: "This should have been your first recommendation after thinking it through. Add the learning from this to the checklist. Always map in context of our use cases."

Context: DEC-410 API audit walkthrough. My initial proposed schema (subscription tier / endpoints / consumption / gaps / recs) was endpoint-inventory level — surface-level despite owner's verbatim "should not be surface level but a deep dive." Owner had to ask "is it comprehensive for our use cases?" before I expanded the schema to include the 6 use-case dimensions (PIT-safety per endpoint, universe coverage, strategy-specific mapping, agent-specific mapping, DEC-422 cube dimension sourcing, rate-limit feasibility for our universe scale).

**Why this matters:** L132 (grounded format) catches scope/feasibility errors. L134 (phase scope) catches patch-vs-system-design errors. L135 (focus-phase scope filter) catches forward-looking deferral errors. **L136 catches USE-CASE MAPPING errors** — recommendations that are technically defensible but designed against generic best-practice templates rather than against this system's specific decision-making contexts (the 60+ strategies, the agent overlay, the dimensional cube, the PIT correctness requirements, the universe scale constraints).

**Rule (CHECKLIST #57):** Before stating any recommendation that involves:
- Audits, schemas, or inventories
- Framework designs
- Data architecture or data sources
- Test infrastructure
- Output formats or reports
- Decision-table designs

...explicitly map the recommendation against this system's actual use cases:
1. Which strategies/agents/cube-dimensions/decisions consume the proposed output?
2. Does the proposed structure surface what each consumer actually needs?
3. Is the structure shaped by THIS system's contexts, or by external best-practice templates?

If the recommendation could be reused unchanged in a different trading system or different domain, that's a flag — generic-by-default recommendations don't address this system's specific gaps.

**Pair:** L136 + CHECKLIST #57. Per owner standing exception for process-discipline files.

**Honest meta-observation:** This is now the 8th Pass 52 process discipline rule (L132/#53, L133/#54, L134/#55, L135/#56, L136/#57). The pattern of recurrence is consistent: owner catches a class of error → I codify a rule → next turn surfaces a new class of error. Each new class is more subtle than the last:
- L132: scope/feasibility (existing infrastructure check)
- L133: empirical validation (test-run gate)
- L134: phase scope (patch vs system-design)
- L135: focus-phase filter (forward-looking deferral)
- **L136 (THIS): use-case mapping (this system vs generic template)**

If a 9th-class error emerges after L136, the right fix is no longer additional rules — it's making "is this a context-specific recommendation or a generic-template recommendation" the FIRST question I ask before drafting any recommendation, not the LAST one I check at the end.

**Layered defense (7 levels per Pass 52):**
- #43/#46/#47: catch duplicates
- #53: catch scope/feasibility errors (grounded format)
- #54: catch empirical-failure errors (test-run gate)
- #55: catch architectural-framing errors (patch vs system-design)
- #56: catch focus-phase scope-filter errors (forward-looking deferral)
- **#57 (NEW): catch use-case mapping errors (this system vs generic template)**
- Owner adversarial review (informal, ongoing) — has caught all 8 errors in pattern lineage

L138 — Directive execution does not override flagging duty (Pass 52 turn 129):

Trigger: Pass 52 turn 121 owner provided 7 directives for DEC-042 AgentGateConfig spec ("1. A define now / 2. weighted / 3. Risk extensively tested / 4. continuous score / 5. must align / 6. tier modifier approved / 7. Sprint 7"). Claude executed all 7 directives mechanically without first verifying that the spec's named agents (Bull/Bear/Risk/ChartAnalyst as parallel voters) matched the actual TradingAgents 11-agent architecture (sequential debate-and-synthesize through Portfolio Manager + Research Manager + Risk debate among 3 debaters synthesized by Portfolio Manager).

Owner accountability question turn 128: "Why this logic? Is it the most optimal method?" surfaced two architectural gaps:
1. ChartAnalyst is NOT in the TradingAgents 11-agent roster
2. Parallel-voting interpretation mismatches the framework's sequential synthesis workflow

Owner directive turn 129: directive execution should not have happened without first flagging these gaps.

Lesson: When owner provides parameters/directives for a spec, Claude must pre-flight that the spec's underlying assumptions hold before executing. Parameter execution operates on architectural assumptions; if assumptions are wrong, parameters apply to a wrong model. Owner directives in this scenario were operating on a phantom architecture (parallel-voter model) Claude assumed but didn't verify.

This is distinct from #51 (don't infer approval) — owner provided explicit directives. The failure was earlier: pre-flight verification of architectural alignment didn't happen. Per L138, this verification step is mandatory before parameter application.

Codified in CHECKLIST #59 (architectural assumption verification before parameter application).

Pattern alignment with Pass 52 owner accountability cycle (5th instance):
- Turn 98: Substantive vs declared completeness (homeless decisions)
- Turn 108: Substantive vs declared completeness (engineering decisions in registers)
- Turn 110: Coverage gaps in cross-references (bugs not in registers)
- Turn 114-118: Quality vs delegated bulk (sweep with HARD-REVERSIBILITY flag)
- Turn 128: **Architectural fit not verified before parameter application (this learning)**

Common thread: Claude's confidence in surface-level execution outpaces underlying-state verification. Owner verification questions catch these. Going forward, pre-flight discipline must extend to architectural-fit verification on every spec touching system primitives.

L139 — Decision resolution must include data-input dependency verification (Pass 52 turn 130):

Trigger: Pass 25 resolved DEC-042 (AgentGateConfig spec). Pass 28 resolved DEC-051 (TradingAgents staged adoption). Pass 28-29 resolved DEC-055/056/057/058 (cost optimization, dropped Social, model selection). Pass 31 analyzed TradingAgents source code documenting 11-agent roster + 12 total roles. NONE of those passes mapped per-agent data input requirements against current data feeds.

Owner accountability question Pass 52 turn 130: "Do a comprehensive analysis and determine if we will be feeding the right and comprehensive data to agents to make their decisions?" — surfaced gap that should have been found in Pass 25-29.

Owner directive turn 130: "Yes. This should have been done in the passes itself. This is exactly the gap that would have invalidated the efficiveness of stage 2 testing. All efforts would be nullified."

Failure mode: Phantom completeness. DEC-042/051/055-058 marked RESOLVED-DECIDED but underlying agents could not actually function in production with current data feeds:
- Market Analyst: missing ICT/SMC + chart patterns + multi-timeframe + sector relative strength
- Fundamentals Analyst: missing PIT-correct fundamentals + transcripts + analyst estimates + short interest
- News Analyst: missing macro qualitative news source
- Trader: missing portfolio context + slippage + sizing rules + cooldowns
- Risk Debaters: missing correlation + sector concentration + drawdown + crisis flags
- Bull/Bear/Research Manager/Portfolio Manager: missing smart money + regime + portfolio context in LangGraph state

Impact if unresolved: Stage 2 backtest agent overlay would have produced decisions based on shallow input. A/B testing of "agents add edge over rules" would have measured agents-with-degraded-input vs rules-with-full-input — invalid comparison. DEC-131 ≥0.2 net Sharpe gate would have been meaningless. All Stage 2 effort nullified.

Pattern alignment with Pass 29 BUG-113 ("agent emits 31 fields, engine reads 2"): same shallow integration anti-pattern but for inputs rather than outputs. I had visibility on the symmetry but didn't apply it.

Lesson: When a decision adopts an architecture or framework, decision resolution requires explicit verification that every component within the architecture has its data input dependencies satisfied. Five-step verification: (a) document per-component requirements; (b) map current feeds; (c) identify gaps with severity; (d) propose resolutions with costs; (e) owner approval before marking architectural decision RESOLVED-DECIDED.

Codified in CHECKLIST #60 (data dependency verification on architectural decisions).

Resolution path Pass 52 turn 130: 9 new decisions logged (DEC-460 through DEC-468) establishing pre-Sprint-1 verification (DEC-460/461) + Sprint 7 custom toolkits (DEC-462-468) per Pattern 2. Sprint 7 effort: 77-86d → 96-108.5d (+19-22.5d, ~25-28%).

Pattern continuity with L138 (Pass 52 turn 129):
- L138: directive execution does not override flagging duty (architectural assumption verification BEFORE parameter application)
- L139: decision resolution must include data dependency verification (data dependency verification BEFORE marking architectural decisions RESOLVED-DECIDED)

Both L138 and L139 are about the same root cause: insufficient pre-flight verification of underlying state (architecture in L138; data dependencies in L139) before declaring decisions complete. CHECKLIST #59 and #60 codify the disciplines as separate but parallel pre-flight gates.

Pass 52 owner accountability cycle (6 instances):
- Turn 98: substantive vs declared completeness (homeless decisions)
- Turn 108: substantive vs declared completeness (engineering decisions)
- Turn 110: coverage gaps in cross-references (bugs)
- Turn 114-118: quality vs delegated bulk (sweep)
- Turn 128: architectural fit not verified (DEC-042)
- Turn 130: data dependency chain not verified (this learning)

Common thread: Claude's confidence in surface-level completion outpaces underlying-state verification. Owner verification questions catch these. Going forward, pre-flight discipline must extend to data-feed dependency verification on every architectural/framework adoption decision.

L140 — Documentation review must include adversarial simulation (Pass 52 turn 132):

Trigger: Owner Pass 52 turn 132 directive — "Do an adversarial review of the project plan and decisions and point out all gaps. Simulate every step and every micro step from current phase to end. Point out everything wrong or not done well. ... 5 passes automatically without my prompt. ... Be detailed. I don't care about time it takes but get it right."

Outcome: 167 gaps identified across 3 canonical documents (PROJECT_PLAN + TRADINGAGENTS_DATA_AUDIT + TRADING_RULES). 10 Stage 2 effectiveness blockers synthesized. Without this audit, Stage 2 backtest infrastructure (Sprint 1-9, ~310-385d) was at risk of producing invalid verdicts regardless of execution quality.

Failure mode caught: Documentation appearing complete and internally consistent on linear read, but containing mathematical impossibilities, architectural mismatches, and unstated assumptions that would manifest as Stage 2 verdict invalidity. Linear review = grammar/typos. Adversarial simulation = architectural gaps.

Top blockers identified that linear review missed:
- B1 Multiple testing math: 119 strategies × 65K cells = 7.7M combinations; Bonferroni α = 6.5e-9; no cell can pass
- B2 A/B budget math: $300 cap vs $1500-2000 needed (5-7× off)
- B3 Paired design invalid: trade SETS differ per arm, statistical comparison meaningless
- B4 Portfolio class spec vacuum: Sprint 7 toolkit methods reference unspecified Sprint 3 methods
- B5 TradingAgents Pydantic schema verification: Research Manager `confidence` field may not exist
- B6 Cube compute cost unestimated: 100M+ metric computations across 6 walk-forward folds
- B7 PIT fundamentals verification still pending DEC-460
- B8 Walk-forward pre-2018 data source not in Sprint 1 scope
- B9 Russell 1000 referenced inconsistently across docs
- B10 Cost estimate $263 CAD/mo doesn't include contingencies — real cost likely $500-1000+

Lesson: Canonical document review must include adversarial 5-pass simulation: execution simulation / data dependencies / edge cases / statistical rigor / governance assumptions. Linear linear-read review insufficient — gaps emerge from "what happens when X" probing.

Codified in CHECKLIST #61 (adversarial document review before declaring canonical documentation complete).

Pass 52 owner accountability cycle (7 instances):
- Turn 98: substantive vs declared completeness (homeless decisions)
- Turn 108: substantive vs declared completeness (engineering decisions)
- Turn 110: coverage gaps (bugs)
- Turn 114-118: quality vs delegated bulk (sweep)
- Turn 128: architectural fit not verified (DEC-042 → DEC-459)
- Turn 130: data dependency chain not verified (DEC-460-468)
- Turn 132: **documentation rigor gaps not verified (this learning — 167 gaps + 10 blockers)**

Pattern continuity:
- L138 (turn 129): directive execution does not override flagging duty
- L139 (turn 130): decision resolution must include data-input dependency verification
- L140 (turn 132): documentation review must include adversarial simulation
- L141 (turn 132): statistical methodology requires capacity check (see L141 below)

Common thread: Claude's confidence in surface completion outpaces underlying-state verification. Each owner-driven catch surfaces a deeper layer:
- L138: surface = directives executed; underlying = architectural assumptions unverified
- L139: surface = framework adopted; underlying = data dependencies unmapped
- L140: surface = documentation complete; underlying = adversarial scenarios un-simulated

Owner directive turn 132 was PROACTIVE (asked for comprehensive simulation). Going forward, this discipline should be self-applied without owner prompt on every canonical documentation milestone.

L141 — Statistical methodology requires capacity check (Pass 52 turn 132):

Trigger: Pass 52 turn 132 adversarial audit Pass 4 found that TRADING_RULES §3 5-Gate Filter (Bonferroni p < 0.05, PSR ≥ 0.95, t-stat ≥ 3.4) combined with §22 Cube architecture (17+ dimensions × 119 strategies) produces 7.7M test combinations. Bonferroni-corrected α = 0.05 / 7.7M = 6.5e-9 — effectively unattainable. PSR formula deflates by trial count N — same scale problem.

Sample size requirement (n ≥ 30 per cell × 65K cells × 119 strategies × 6 walk-forward folds) requires 1.4 BILLION trades. Universe (~480 tickers × 250 days × 6 years) provides 720K ticker-days. Trade frequency >>> ticker-day observations. Mathematically impossible to populate cube at significance threshold.

Failure mode caught: Statistical methodology specified WITHOUT verifying that sample size × dimensions × multiple-testing correction × data volume reconcile. Methodology designed in isolation; integration check missed.

Lesson: Before finalizing statistical methodology, verify capacity: (a) trial count × correction → significance threshold attainability; (b) sample size requirement × cell count → required trade volume; (c) required trade volume × OOS folds → required ticker-day coverage; (d) reconcile against actual data availability.

Resolution path: Switch from Bonferroni to FDR (Benjamini-Hochberg); apply hierarchical correction (strategy-level then cell-level); reduce cube dimensionality; revise n-threshold to fit data volume. Formal resolution deferred to Sprint 7 statistical methodology block per ADVERSARIAL_AUDIT.

Codified in CHECKLIST #62 paragraph + part of #61 5-pass methodology Pass 4 (statistical / methodological rigor).

---

## L142 — Adversarial audit must include archive comparison (Pass 53)

**Source trigger:** Owner Pass 53: "Why was phase 1A dropped. Even phase 1A had alpha and beta. same as phase 1B."

**Discovery:** PROJECT_PLAN_ARCHIVE.md showed Phase 1A v3 was COMPLETE — 67 instruments × 4 years × 6,942 trades closed, `atr_trail_1x` confirmed as primary exit (20/29 strategy comparisons), 4 strategies flagged WEAK on OOS-2024-only. This was a documented empirical achievement that fed downstream design.

**How it got dropped:**
- Pass 52 turn 119: DEC-014 (Phase 1B passing criteria) was SUPERSEDED by DEC-422 (cube) + DEC-426 (5-gate validity)
- During the absorption, the Phase 1A → 1B → 1C → 1D progression compressed to Phase 0 → 1B → 1B-α → 1C+
- Phase 1A reference inadvertently dropped from PROJECT_PLAN.md §3 sub-phases
- TRADING_RULES §2 phase acceptance criteria similarly omitted Phase 1A

**Why ADVERSARIAL_AUDIT didn't catch:**
- Pass 52 turn 132 5-pass audit reviewed current PROJECT_PLAN vs current TRADING_RULES vs current TRADINGAGENTS_DATA_AUDIT
- 167 gaps found within-current-docs
- Audit did NOT compare current docs against archived/historical docs (PROJECT_PLAN_ARCHIVE.md)
- Phase 1A was archived; thus invisible to gap detection
- This is a meta-failure of audit methodology, not just a content failure

**Lesson:** When refactoring methodology that absorbs prior phases (e.g., DEC-014 absorbed by DEC-422+426), there is high risk that archived phase references silently drop. Adversarial audit must explicitly compare against archive ("what was in old doc that's missing from new doc?") to catch these. Apply at every adversarial audit pass; before declaring documentation canonical; when refactoring methodology that absorbs prior phases.

**Codified in:**
- CHECKLIST #63 (NEW Pass 53)
- DEC-489 RESOLVED-DECIDED (methodology learning)
- Restoration: DEC-486/487/488 PROPOSED (Phase 1A / 1A-α / 1A-β)

**Owner accountability:** Same pattern as Pass 52 turn 128 (owner caught DEC-042 architectural-fit gap), Pass 52 turn 130 (owner caught DEC-051 data-dependency gap), Pass 52 turn 132 (Claude proactively surfaced 167 gaps). Pass 53 turn (this) is the 4th instance where owner caught a Claude-missed gap. Pattern of owner-as-error-catcher remains stable; Claude meta-audit methodology still has blind spots.
