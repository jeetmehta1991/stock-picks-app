# Universal Engineering Learnings
**Author:** Jeet Mehta
**First compiled:** April 2026
**Last refreshed:** 2026-05-15 Batch 178 — see LEARNINGS.md L151-L154 for 4 new pattern-level lessons distilled from the Phase 1A launch-readiness sweep (matrix/dashboard cyclic-dep oscillation; canonical-ID extraction needs suffix; Wikimedia REST rate-limit floor; inventory truth must be empirical not declarative).
**Purpose:** Distilled principles from real project mistakes. Apply to every future project regardless of domain.

Each principle is written as a universal rule, not a project-specific anecdote.

---

## PRINCIPLE 1 — Testing

### Never audit by reading. Audit by running.
Reading code that looks correct is not the same as code that works correctly. A data flow is only verified when a test asserts it end-to-end. Three comprehensive audits can miss a bug that one `print(result.keys())` would have caught in 30 seconds.

**Rule:** After every audit, write a test for every flagged item before closing it.

### Test inter-module data handoffs explicitly.
When function A produces data consumed by function B, the most dangerous bugs live at the boundary — mismatched key names, wrong data types, missing fields. These are invisible when you read each function independently.

**Rule:** For every producer → consumer boundary, write a test that calls the producer and asserts all expected keys are present with correct types.

### Time-series accumulation fields need multi-step tests.
A field named `max_adverse_excursion` implies accumulation over time. The code might compute it for only the current step. Reading the code you see the field name and assume it accumulates. Only a test that runs two time steps reveals it resets.

**Rule:** Any field that should accumulate across time must be tested across at least 2 time steps.

### Documentation without a test is a claim, not a guarantee.
A project plan that says "two walk-forward windows" while the code implements one is worse than no documentation — it creates false confidence. Every documented behaviour needs a test that asserts it.

**Rule:** For every documented system behaviour, have a corresponding test. If you can't write a test for it, the behaviour isn't well-defined enough.

### Build tests after audit 1, not after audit 4.
A test suite built after the first audit would have prevented 80% of the bugs found in audits 2, 3, and 4. Tests are permanent. Manual audits are point-in-time and always incomplete.

**Rule:** After completing the first working version of any module, immediately write integration tests before moving to the next module.

---

## PRINCIPLE 2 — APIs & External Data

### Verify API tier access before writing any code.
The most expensive mistake is building a full download script, running it against 500 records, and discovering the endpoint returns 0 records because it requires a paid tier. This wastes time, API rate limit, and money.

**Rule:** Before building any API integration: (1) check the documentation for tier requirements, (2) make one test call per endpoint, (3) verify data is returned, (4) only then build the script.

### Test date range coverage before building download pipelines.
An API can return 200 OK but empty results for historical date ranges the free tier doesn't cover. Always test the exact date range you need before building the full pipeline.

**Rule:** For any API with historical data, test: `fetch(ticker, from=earliest_date_you_need)`. Verify non-empty results before investing in the full pipeline.

### Check existing providers before adding new ones.
Before subscribing to a new API provider, inventory what your existing providers already offer. Alpha Vantage provided AI-powered news sentiment for free — the same data that was about to be purchased from Finnhub.

**Rule:** When you need new data, first check if any current provider already offers it via a different endpoint.

### Never run parallel git-push workflows.
Parallel jobs that all push to the same git branch will conflict. Only one push succeeds. The others fail silently or with cryptic errors. This caused 3+ reruns of data download jobs.

**Rule:** Never design parallel workflows where multiple jobs push to the same branch. Sequential is slower but always works. If parallel is needed, use separate branches and merge at the end.

---

## PRINCIPLE 3 — Data Integrity

### Pre-fetch all external data before any computation loop.
Any loop that calls an external API inside it — a backtest, a training loop, a processing pipeline — will be 10-100× slower than one that reads from local cache. The cost of building a pre-fetch layer is always worth it.

**Rule:** Before building any computation loop that would need external data, build the pre-fetch layer first. Cache everything to disk. The loop reads from disk only.

### Point-in-time data means point-in-time everywhere.
Using today's liquidity filter to decide which stocks were liquid in 2022 is a look-ahead bias. A stock that was liquid in January 2022 but became illiquid by 2024 must be removed from the 2024 screener — not retroactively from 2022.

**Rule:** Any filter, threshold, or decision that varies over time must be re-evaluated at the correct historical date, not applied once and frozen.

### Commit to git immediately after every download.
Any data not committed to a git repository is lost when the environment restarts, is shut down, or is provisioned fresh. This is especially true for cloud development environments.

**Rule:** Commit every downloaded file immediately. Never let uncommitted data accumulate across sessions.

### Hardcoded sample data presented as real data is worse than no data.
Nine hardcoded COT data points presented as real CFTC positioning data contaminated a sentiment scoring system. Fake data that looks real is far more dangerous than a missing data source — it creates confidence where none should exist.

**Rule:** If real data is unavailable, return a clearly labelled neutral/unavailable signal. Never substitute fabricated sample data.

---

## PRINCIPLE 4 — System Design

### Every data structure handoff needs explicit key documentation.
When a function returns a dict, the keys are an implicit interface contract. When the consuming function expects different keys, both sides look correct in isolation — the bug only appears at runtime.

**Rule:** Document the keys returned by every dict-producing function, and the keys expected by every dict-consuming function. Make mismatches impossible to miss.

### Agents should derive — not be told — what they are supposed to determine.
Giving an AI agent the classification rules it's supposed to apply defeats the purpose of using an agent. The agent will pattern-match to the rules rather than reason independently. This produces systematically biased outputs.

**Rule:** Never include the output mapping or decision rules in an agent's prompt. Agents derive scores. Mappings are applied in code afterward.

### Design for the complete data flow before building any component.
The most expensive refactoring is adding a field to a dataclass that is used in 8 different places. Sector tags were in the source CSV from day one but not added to the engine dataclasses until week 8 — requiring cascading changes to OpenTrade, ClosedTrade, backtest.py, pipeline.py, and universe.py.

**Rule:** Before writing the first line of any module, sketch the complete data flow: what goes in, what comes out, what fields need to exist at each stage.

### AI agents must use temperature=0 in deterministic systems.
An agent with temperature=1.0 (the default) can return different confidence tiers for identical inputs on different runs. A backtest must be reproducible. Non-deterministic agent outputs mean non-reproducible results.

**Rule:** Set temperature=0 for any AI agent call in a backtesting, evaluation, or analytical pipeline. Use temperature > 0 only in live, interactive contexts where variation is acceptable.

---

## PRINCIPLE 5 — Process & Workflow

### Checklists only work if they are run, not just documented.
A checklist that is documented but not enforced provides false security. Making the same mistake after adding it to a checklist is worse than not having a checklist — it means the checklist is theatre.

**Rule:** Before every significant action (code change, data download, API call, deployment), visibly confirm each checklist item. The checklist must be a gate, not a suggestion.

### Never build for an environment you haven't verified the user is using.
Building a PowerShell script for a user who consistently works in Git Bash — despite multiple prior failures in PowerShell — is a failure of observation. The correct answer was always one Git Bash command.

**Rule:** Before providing any command or script, identify the exact environment: OS, shell, working directory, available tools. The simplest working solution is always better than an elaborate one that doesn't fit the environment.

### Show cost estimates with the full calculation before running anything paid.
Giving a confident cost estimate that is 10× wrong erodes trust and wastes money. The estimate should show the formula, the assumptions, and the unit check.

**Rule:** Cost estimate format: `N calls × cost_per_call = $X (formula: [show it])`. Never give a round number without the underlying calculation.

### Never jump ahead of the current validated phase.
Running Phase 1B data downloads before Phase 1A results are reviewed is optimistic bias — assuming the earlier phase succeeded when it hasn't been confirmed. Each phase must be validated before the next begins.

**Rule:** Phase gates are not optional. Every phase must produce validated outputs before the next phase starts. Document the specific outputs that constitute "phase complete."

---

## PRINCIPLE 6 — Infrastructure

### Pin all package versions in environment configs.
`pip install pyarrow` installs whatever the latest version is. When the latest version changes, the environment breaks. This is especially critical in cloud development environments that rebuild on every start.

**Rule:** Always pin: `pyarrow==14.0.0` not `pyarrow`. Unpin only when intentionally upgrading.

### git reset --hard destroys uncommitted work permanently.
This is obvious in theory but kills data in practice when executed under time pressure. Uncommitted downloaded data is gone forever after a hard reset.

**Rule:** Before any `git reset --hard`, always run `git status` first. If there is uncommitted work, commit it. No exceptions.

### Sequential git operations are almost always correct. Parallel is almost always wrong.
Parallel git operations introduce race conditions on push. Sequential operations are slower but deterministic. The time saved by parallelism is always lost to debugging the failures.

**Rule:** Default to sequential for any workflow involving git push. Parallel only when outputs are isolated to separate branches with a merge step.

---

## PRINCIPLE 7 — Documentation

### Stale documentation is worse than no documentation.
A docstring that says "2020-2024 weekly history (260 readings)" when the actual data covers 2020-2026 (325 readings) trains readers to distrust all documentation in the codebase.

**Rule:** Update documentation at the same commit as the code it documents. Never commit a code change without updating the corresponding docstring, comment, or specification.

### Separate what-we-plan from what-the-code-does.
A project plan documents intent. Code implements reality. When they diverge, the code is the truth. Always label project plan documents as "intent" and maintain a separate "current state" section that reflects actual implementation.

**Rule:** Every project plan section should have a corresponding "implementation status" field that is updated when code is written, not when the plan is written.

---

## Summary — The 10 Rules That Would Prevent 90% of All Mistakes

1. **Test inter-module boundaries before trusting them** — producer/consumer key coherency
2. **Verify API tier and date range with one call before building any script**
3. **Pre-fetch all external data before any computation loop**
4. **Commit to git immediately after every download or significant computation**
5. **Run the checklist as a gate, not as a suggestion**
6. **Set temperature=0 for deterministic agent calls**
7. **Never give a cost estimate without showing the formula**
8. **git status before git reset --hard — always**
9. **Never run parallel workflows that push to the same branch**
10. **Write tests after audit 1, not after audit 4**

---

## PRINCIPLE 8 — Documentation Refactors and Archive Comparison (Pass 53)

### Refactors that absorb prior phases must explicitly enumerate preserved vs dropped content.

When a methodology decision absorbs prior phase content (e.g., DEC-014 Phase 1B passing criteria absorbed by DEC-422 cube + DEC-426 5-gate validity), there is high risk that the prior phase reference disappears from current documentation while only living in archives. Pass 52 turn 119 absorbed DEC-014 cleanly per methodology, but inadvertently dropped Phase 1A reference from PROJECT_PLAN §3 sub-phases. The archive (PROJECT_PLAN_ARCHIVE.md) preserved Phase 1A v3 as COMPLETE (67 instruments × 4yr × 6,942 trades), but the current docs no longer mentioned Phase 1A.

**Rule:** Any commit message containing "absorbed" or "supersession" or phase-taxonomy refactor must trigger an archive-comparison check. List what existed in archive before the refactor; list what exists in current docs after; flag every item not in the post-refactor docs as a deliberate-drop-with-justification or restore it. Codified in CHECKLIST #63.

### Adversarial audits must include archive comparison.

5-pass adversarial document review (Pass 52 turn 132) compared current PROJECT_PLAN against current TRADING_RULES against current TRADINGAGENTS_DATA_AUDIT — found 167 gaps. But it didn't compare against PROJECT_PLAN_ARCHIVE.md, so Phase 1A omission was invisible. This is a meta-failure of audit methodology, not just a content failure.

**Rule:** Archive comparison ("what was in old doc that's missing from new doc?") is a standard adversarial audit step, not optional. Apply at every adversarial audit pass; before declaring documentation canonical; especially when refactoring methodology that absorbs prior phases.

### The pattern: owner catches gaps audit missed.

4 instances during Pass 52-53 where owner question surfaced a gap that Claude's adversarial audit missed (DEC-042 architectural fit, DEC-051 data dependencies, 167 gaps in Pass 52 turn 132 — caught by Claude proactively, and Phase 1A omission). The pattern of owner-as-error-catcher is stable. Claude meta-audit methodology has blind spots that owner familiarity with project history reveals.

**Rule:** Treat owner's questions about "where did X go?" or "why isn't Y in here?" as high-priority signal. Owner has historical context that Claude's recent-conversation-window doesn't. Don't dismiss; verify against archives + history before responding.

---

## PRINCIPLE 9 — Pass 53 Cumulative Learnings (universe-build effort + comprehensive doc audit)

### CSV-first data architecture is non-negotiable.

Pass 53 owner directive: all input/output data lives in CSV files; no exclusively-codebase data. Past violation corrected: `ETFS_FULL` hardcoded list in `universe.py` migrated to `Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv` (DEC-494). Distinction: lists/mappings/records → CSV; thresholds/formulas/parameters → code. The line: if you find yourself typing a Python list of tickers or a dict of attributes longer than 5 entries, stop and put it in a CSV instead. Codified in CLAUDE.md HARD RULES.

**Rule:** Before writing any module that introduces hardcoded ticker lists, sector dicts, event calendars, or known-good-output lists, check CLAUDE.md CSV-first HARD RULE. If the content is data (not configuration), it goes in a CSV.

### Free historical financial data is genuinely scarce — accept the verification reality.

Pass 53 universe-build effort attempted to verify NDX 157-row CSV against external sources outside Wikipedia + Nasdaq IR (already used). 5 iteration batches × 2-3 sources/batch = 15 external fetches. Result: **2 useful sources, 13 dead ends**. Most secondary aggregators are paywalled past top-25 (stockanalysis.com Pro), Cloudflare-blocked for automated fetches (etfdb / barchart / yahoo / cnbc), marketing pages without raw data (Invesco), or 404s (URL drift over years). Same pattern for T1b Russell 1000 — Wikipedia inadequate, FTSE Russell paywalled via LSEG migration, Polygon doesn't have index membership endpoints.

**Rule:** When verifying external data, surface the verification reality honestly rather than continuing to fabricate fetches against dead URLs. Wikipedia + per-event press release sites (Nasdaq IR, S&P DJI, FTSE Russell free tier) are the practical free verification sources for indices. For paid-source-only data (Russell 1000 historical), defer to formal Sprint procurement rather than build with biased current-snapshot-only data.

### Sourcing wall pattern: Wikipedia adequate for indices, inadequate for events.

Pass 53 attempted Wikipedia for both Tier 1c (NDX-100 — adequate, rich changes table) and Tier 2 (spinoffs + IPOs — inadequate, no centralized list). Asymmetric Wikipedia coverage is a real constraint. Indices (S&P 500, NASDAQ-100) have community-maintained changes tables; ad-hoc events (spinoffs, IPOs, corporate actions) require per-event sources.

**Rule:** Wikipedia under L88 one-time scrape exception works for indices with structured changes tables. For events (spinoffs, IPOs, corporate actions, rebalance events), defer to authoritative event sources (Polygon corporate actions, SEC EDGAR Form 8-K, S&P DJI press releases per-event) — not Wikipedia.

### Scope realism — multi-stream owner directives need decomposition.

Pass 53 owner directive containing "Move folder + 5-iteration verification + 22-doc audit + TRADING_RULES expansion" was decomposed into 4 work streams; only Stream 1 (folder move) and Stream 4 (signal universe expansion) fit cleanly into single turns; Stream 2 (verification) ran 5 iterations across multiple turns; Stream 3 (audit) chunked into A/B/C/D for owner-paced execution. Trying to do all 4 streams in one turn would have produced shallow work on each.

**Rule:** When owner directive contains multiple substantive work streams, decompose explicitly + surface plan + execute one stream at a time. Don't conflate scope. Per CHECKLIST #51 default lower-impact, surface decomposition before action when unsure.

### Universe-tier categorization needs artifact verification, not memory.

Pass 53 made TWO tier-categorization errors: (1) assumed 484-CSV was during-testing-period intersection (caught by my own pre-flight via `refresh_sp500_universe.py` inspection); (2) characterized Tier 2 as "ETFs / sector funds" in commit `6d4b5303` (caught by owner via direct fact-check question). Both errors stemmed from relying on memory rather than verifying against actual file contents + refresh script docstrings.

**Rule:** Before claiming "Tier N = X" or "T1x covers Y", verify against (a) the actual CSV header/contents (`head <file>.csv`); (b) the refresh script docstring; (c) the canonical DEC body. Memory of "what tier contains what" drifts between sessions and across rule changes — verification against actual artifacts is required, not assumption. Codified in CHECKLIST #66 universe-tier refinement.

### DEC scope alignment must be verified before claiming resolution.

Pass 53 caught the DEC-476/DEC-332 attribution mistake (almost recommended "resolve DEC-476" for the smart money composite gap when DEC-476 is actually Portfolio class API spec — DEC-332 is the smart money composite decision). Caught by my own pre-flight grep against AUDIT_INDEX before edits.

**Rule:** Before stating "DEC-X resolves Y" / "this implements DEC-X" / "DEC-X covers Y", grep AUDIT_INDEX.md for DEC-X's actual decision title + body. Audit-row DEC tags can be cluster references, not decision-targets. Verification cost: 15 seconds. Codified in CHECKLIST #66.

### Multi-period schema rows handle re-entries naturally.

Pass 53 T1c CSV needs multi-period rows for tickers that left and re-joined NDX during 2020-2026 (CSGP, TTWO, WDC, SPLK). B++ schema with per-period rows + standard PIT loader filter `(added_date IS NULL OR added_date ≤ as_of) AND (removed_date IS NULL OR removed_date > as_of)` handles this naturally via SQL/pandas OR semantics. No code change needed. Verified via 3 test cases (period 1, gap, period 2).

**Rule:** When designing membership-history schema, multi-period rows per ticker are the correct representation — don't try to compress into single-row-per-ticker; standard OR-across-rows filter logic handles all the cases naturally.

### Owner manual-verification clause as L88 exception scope.

Pass 53 granted one-time L88 Wikipedia exception for universe-build scrape, scoped to (i) one-time historical, (ii) laptop-local, (iii) fallback only — primary remains authoritative source per index, (iv) manual verification before commit. The owner verification step (e.g., owner spot-checked WMT/PTON/NTES via Nasdaq IR press releases) is the gate that catches data quality issues before they're committed.

**Rule:** When granting an exception to a HARD RULE, scope it explicitly with manual-verification clause. The owner's spot-check authority is the actual safety mechanism, not the source itself.

### Data flow (input universe + output universe) must be specified at recommendation time — methodology spec alone is insufficient.

Pass 53 caught DEC-496 conceptual gap: J-T 12-1 momentum methodology was correctly specified (lookback=252, skip=21, classic risk-adjustment OFF, tie-breakers vol-asc → ADV-desc) but implicitly assumed input universe = existing T1 cache. Top 100 NON-T1 momentum names (T3 = non-T1 by definition per DEC-364) cannot be identified by ranking only T1 tickers — running J-T against T1-only defeats T3's purpose. Same gap for T2 spinoffs/IPOs: pre-Pass-53 `refresh_extended_universe.py` reads yfinance ticker info which lags new listings (L89 SNDK 9-month example); Polygon corporate-actions feed is the canonical screener source. Pattern lineage across 4 Pass 53 catches: DEC-476 vs DEC-332 (right methodology, wrong DEC target); DEC-368 vs DEC-370 (right methodology, wrong DEC target); Tier 2 = ETFs (right tier reference, wrong content type); DEC-496 T3 (right J-T formula, wrong input universe). All four = methodology-correct + data-flow-wrong. Owner caught the 4th, codified Q-D Pass 53.

**Rule:** When proposing any methodology / signal compute / screener / filter / universe construction, EXPLICITLY state at recommendation time three properties: (a) **INPUT** universe source — broad market vs T1 vs T2 vs single ticker (with endpoint or file path); (b) **OUTPUT** universe target — which tier/file/cube cell receives output; (c) **FLOW** — input → ... → output matches stated purpose. Methodology spec without data-flow spec is necessary but not sufficient. Verification format: 3-line block at recommendation time. Skipping (a)/(b)/(c) verification = pre-flight failure regardless of methodology correctness. Codified in CHECKLIST #66.b.
