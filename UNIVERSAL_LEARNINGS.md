# Universal Engineering Learnings
**Author:** Jeet Mehta
**First compiled:** April 2026
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
