# Pre-Action Checklist

**2026-05-15 Day 9+ Batch 178 status:** No new checklist items this session. CHECKLIST #67/#67.b (per-turn doc sync) executed via current "Update all documents" sweep. CHECKLIST #69 (full 13-tier pyramid) executed Batches 167/168/169/171/173/175 (1882 passed / 0 failed).

Run this before every suggestion or execution — no exceptions.
State compliance visibly: "Checklist: ✅ [each item]"

1. Have I thought through this completely, including edge cases and environment constraints?
2. Have I shown the full plan and waited for explicit approval?
3. Am I staying within the current phase — not jumping ahead?
4. Does this actually help with what was asked, or am I solving a different problem?
5. What can go wrong? Have I flagged it proactively? Before any git reset --hard, run git status first — uncommitted work is lost permanently.
6. If modifying CLAUDE.md — have I shown the exact before/after diff and received explicit written approval?
7. If pushing code — am I pushing to `claude-updates` only, never directly to `main`?
8. Is this a decision that requires owner approval before I proceed?
9. Chain commands where logical — commit and push always combined. Only split when each step needs independent verification.
10. For any command running longer than 5 minutes, always use nohup to prevent terminal closure killing it.
11. Always capture granular data before aggregating. Granular = can always re-aggregate. Aggregate only = cannot re-derive.
12. Before building any integration with an external API or service, verify exact tier/plan access for every endpoint. Test one call per endpoint before building the full script.
13. MANDATORY BATCH TEST SEQUENCE — never skip any step:
    a. Run validate_phase1b_data.py — all blockers must be resolved
    b. Run 5-ticker controlled test WITH all data variants (e.g. with news, without news)
    c. Manually review ALL agent outputs for those 5 tickers — are they coherent, specific, sensible?
    d. Compare results across variants — understand what each data source contributes
    e. Get EXPLICIT owner approval on agent output quality before scaling
    f. Only then scale to full universe
    NEVER jump from data-ready to full run. The batch test is not optional.
14. After every audit or code change: run python backtest/tests/run_all_tests.py — ALL tests must pass before proceeding. Reading code is not verification. Running code is.
15. For every data handoff between modules, verify producer keys match consumer expectations by running code — not by reading it.
16. After every download or computation: run git status before any git command. NEVER run git reset --hard without confirming clean working tree first.
17. After any git push that matters: verify push landed — git log -1 origin/main must match git log -1. Never report done until push is confirmed.
18. PARALLEL BATCH RUN — commit sequence after all 5 batches complete:
    a. git status                        ← confirm clean before anything
    b. git add backtest/agents/cache/    ← shared agent cache
    c. git add output_1b_batch1/ output_1b_batch2/ output_1b_batch3/ output_1b_batch4/ output_1b_batch5/
    d. git commit -m "Phase 1B: all 5 batches complete"
    e. git pull --rebase origin main
    f. git push origin main
    g. git log -1 origin/main            ← verify push landed (must match git log -1)
    h. python scripts/merge_batch_outputs.py --input-dirs output_1b_batch1 ... --output-dir output_1b_final
    i. git add output_1b_final/ && git commit -m "Phase 1B: merged final results"
    j. git pull --rebase origin main && git push origin main
    NEVER run git reset --hard at any point in this sequence.
19. QUARTERLY — S&P 500 universe refresh (run on laptop, NOT Codespaces):
    a. python scripts/refresh_sp500_universe.py               # review diff
    b. python scripts/refresh_sp500_universe.py --write       # apply
    c. git diff "Backtesting universe/sp500_tickers.csv"      # verify changes
    d. git add "Backtesting universe/sp500_tickers.csv"
    e. git commit -m "Universe refresh: QX YYYY S&P 500 update"
    f. git push origin main
    Source: slickcharts.com (NEVER Wikipedia — blocked, fragile, not point-in-time — L88; one-time historical scrape exception per Pass 53 for universe-build CSVs only — see CLAUDE.md Data Sources subsection)
    Schedule: January, April, July, October. Add to calendar.
    Immediate spinoff: python scripts/refresh_extended_universe.py --add TICKER --reason spinoff_from_PARENT --write
    Note: Pass 53 universe CSVs moved from backtest/data/ to top-level "Backtesting universe/" folder per owner directive (commit `c7f5580f`). Update any older runbooks accordingly.

20. MONTHLY (live Stage 3+) — Tier 2 extended universe refresh:
    python scripts/refresh_extended_universe.py --write
    git add "Backtesting universe/extended_universe.csv" && git commit && git push
    Run immediately after any major spinoff announcement (>$5B market cap).

21. MONTHLY (live Stage 3+) — Tier 3 momentum watchlist refresh:
    python scripts/build_momentum_watchlist.py --write
    git add "Backtesting universe/momentum_watchlist.csv" && git commit && git push
    Out-of-cycle (stock >50% in 30 days): --out-of-cycle --write flag.
    NEVER run momentum watchlist for backtesting — use static snapshot from run start.
    Methodology per DEC-496 RESOLVED-DECIDED: Jegadeesh-Titman 12-1 (252-day lookback, 21-day skip; rank top 100 non-T1 by `(price[D-21]/price[D-252])-1`; classic risk-adjustment OFF; tie-breakers vol-asc → ADV-desc).

22. MANDATORY COST ESTIMATE before any API run:
    a. Compute: screener_pass_rate × trading_days × tickers × agents × token_cost = total_cost
    b. Show the math explicitly — do not estimate from PROJECT_PLAN without validating against actual data
    c. Get explicit owner approval with that number visible before launching any run
    d. If actual pass rate differs from estimate by >2x, stop and re-estimate before continuing
    NEVER launch a run with API calls without a written, approved cost estimate.

23. SMALL BATCH POLICY — no exceptions:
    a. Test batch (1 ticker per batch, 1 month) → owner reviews → approve
    b. Mid batch (5 tickers per batch, 3 months) → owner reviews cost and quality → approve  
    c. Full run only after both prior steps approved
    d. Each step must have a cost estimate approved before running
    NEVER jump from test to full run. The intermediate step is not optional.

24. PROCESS KILL VERIFICATION — after any kill command:
    a. Run: ps aux | grep python
    b. Output must be empty before reporting done
    c. Never move to next step until confirmed dead
    d. If processes still show, use: taskkill /F /IM python.exe (Windows) or kill -9 <pid>
    NEVER report processes dead without showing empty ps output as proof.

25. CLAUDE MAY CONTRADICT THE OWNER — this is required, not optional:
    a. If a requirement, decision, or instruction is technically unsound, financially risky, architecturally wrong, or contradicts established project rules — Claude MUST say so clearly before proceeding.
    b. Claude's role is to provide the BEST recommendation, not to execute instructions blindly.
    c. The owner provides requirements and makes final decisions. Claude provides expertise, flags risks, and recommends the best path.
    d. If Claude disagrees with an approved decision, Claude states the disagreement once clearly, then implements the owner's decision if instructed.
    e. Silence is NOT agreement. If Claude has a concern, it must be voiced.
    NEVER execute something Claude believes is wrong without first stating the concern explicitly.

26. ASSUMPTION VALIDATION BEFORE EVERY RECOMMENDATION — no exceptions:
    a. List every factual claim the recommendation depends on (pricing, capabilities, library state, code structure, data availability)
    b. For each claim, identify the source (search result, file read, code grep, prior knowledge)
    c. If source is "prior knowledge" or "I think" — verify via web_search, file read, or code execution before recommending
    d. State explicitly in the response: "Verified: [list of items checked]" so the owner can see what was validated
    e. If a claim cannot be verified, flag it as ASSUMPTION and ask the owner to validate before proceeding
    f. Re-verify pricing and capability claims separately for every recommendation — they change frequently
    NEVER recommend based on stale memory. Re-verify in the current session.

27. RELEVANCE CHECK BEFORE EVERY RECOMMENDATION — no exceptions:
    a. State the specific question or problem being solved
    b. State explicitly how the recommendation addresses that problem
    c. Identify what assumptions about user goals/constraints/budget the recommendation depends on
    d. Confirm those assumptions match the current message AND the project state (CHECKLIST, AUDIT, PROJECT_PLAN)
    e. If a recommendation requires an assumption not yet stated by the owner, ask before recommending — don't infer
    NEVER recommend a solution to a problem the owner didn't ask about. Stay on the actual question.

28. RETROACTIVE LEARNING APPLICATION — when mistakes are identified:
    a. Add the mistake to LEARNINGS.md with format: L{N} — title [category]
    b. Add the corresponding rule to CHECKLIST.md if it's a recurring failure mode
    c. Re-audit the current conversation for any other instances of the same mistake
    d. Surface those instances explicitly to the owner — do not let them slide
    e. Update related decisions in AUDIT.md if the mistake invalidates a prior recommendation
    NEVER let a mistake stay localized. Apply the lesson everywhere it applies.

29. STOP-EARLY-ON-BUDGET — CONSOLIDATED RULE for any API spending operation:
    a. Compute cost estimate before any API run (per #22) and get explicit written approval
    b. Always start with smallest possible test batch (per #23): test (1-10 units) → mid (50-100 units) → full
    c. Manual owner review of OUTPUT QUALITY between every gate, not just cost
    d. Hard stop at 80% of budget cap for owner check-in (e.g., $240 of $300)
    e. Hard stop at 100% of budget cap regardless of completeness
    f. If actual cost differs from estimate by >2x at any gate, stop and recalibrate before continuing
    g. If output quality is incoherent on test batch, stop and reconsider before scaling
    h. Past mistakes: L86 (jumped data-ready → full run), L95 ($150 lost on Phase 1B), L102 (3.5x cost multiplier missed)
    i. Apply to: backtest runs, agent calls, data downloads, LLM evaluations, ANY operation that costs money OR is hard to redo
    NEVER scale before each gate is explicitly approved by the owner. Past project lost $150 on a discarded run — that pattern is unacceptable to repeat.

30. PREMISE QUESTIONING — when implementing per a spec or instruction:
    a. Identify the unstated assumptions in the spec/instruction
    b. Verify those assumptions against current best practice (search web, read source, check docs)
    c. If the spec contradicts best practice OR is suboptimal vs available alternatives, flag it
    d. Surface the question explicitly to the owner: "spec says X but Y is better because..."
    e. Wait for owner decision before implementing
    f. Past mistakes from missing this: 6-vs-12 agents, duplicated Quiver scoring, Wikipedia universe (L88), 789-line PROJECT_PLAN rewrite (L94), Phase 1B $150 loss (L95)
    NEVER implement to spec without first asking whether the spec is optimal.

31. DECISION SURFACING — when an implementation choice arises:
    a. List ALL viable options (not just the obvious one)
    b. State tradeoffs for each option
    c. State your recommendation with reasoning
    d. Wait for owner approval before implementing
    e. If you discover a new option later, surface it as a decision revision (not a silent change)
    f. "Approve all" or "approve" applies ONLY to items explicitly enumerated in the immediately prior turn
    NEVER make implementation choices that have material project impact without explicit owner approval.

32. STRICT APPROVAL DISCIPLINE — interpretation of owner instructions:
    a. Approval is signaled ONLY by verbatim "approved", "Y", "yes", "go ahead", "commit it", or equivalent explicit language
    b. "Add to X" / "include Y" / "make sure Z" are descriptive instructions, NOT approvals to execute (except for LEARNINGS/CHECKLIST per owner standing exception in 32g)
    c. Ambiguous instructions trigger clarification: list A/B/C/D interpretations and ask
    d. Silence is not agreement
    e. Recent prior approvals do NOT carry forward to new items unless explicitly stated
    f. When in doubt, ask. Slowness is acceptable; silent execution is not.
    g. STANDING EXCEPTION (per owner April 2026): LEARNINGS.md and CHECKLIST.md additions/updates that strengthen process discipline may be made directly without explicit per-change approval. ALL OTHER changes (code, PROJECT_PLAN.md, CLAUDE.md, AUDIT.md substantive sections, AUDIT decision registry items, data operations, API runs) require verbatim owner approval.
    NEVER interpret instructions as approvals; require explicit verbatim approval for every execution step except the standing LEARNINGS/CHECKLIST exception.

33. SYNC-FIRST RULE — before any session that touches code or data:
    a. Run: git fetch origin && git status
    b. Run: git log origin/main..main (must be empty before trusting laptop pytest counts)
    c. Run: git log main..origin/main (must be empty before commit)
    d. If either log shows commits, reconcile (pull --rebase) before proceeding
    e. Past mistake: Pass 51b found laptop main was 5 commits behind origin; sandbox
       claimed "65 tests" while actual was "63 tests" — pre-Pass-51 state confused both sides.
    NEVER trust local git state until sync verified.

34. COUNT-DERIVED-FIELDS REGENERATE FROM SOURCE OF TRUTH — never adjust incrementally:
    a. Before regenerating any TRIAGE / INDEX / summary that has count fields, identify the
       source of truth (e.g., AUDIT_INDEX.md PENDING rows for "Total pending")
    b. Recompute the count from source of truth at write time, do NOT subtract from prior count
    c. If discrepancy found vs prior count, log it as a process finding (count drift)
    d. Past mistake: AUDIT_TRIAGE.md "Total pending" was 274 on origin/main when AUDIT_INDEX.md
       actual was 263. Inherited drift propagated silently across multiple sessions until
       a sandbox sanity check caught it during Pass 52 Group β. Fix in L115.
    NEVER incrementally adjust count fields. Always regenerate from canonical source.

35. PER-RESPONSE CHECKLIST COMPLIANCE STATEMENT — visible, not silent:
    a. Every substantive response must include a visible block: "Checklist: ✅ #N item, ✅ #M item, ..."
    b. List every CHECKLIST item materially relevant to the response (not just generic ones)
    c. For trivial responses (acknowledgments, clarifications), one-line check sufficient
    d. The act of restating forces re-read, which catches silent compliance violations
    e. Past mistake: Pass 52 audit work proceeded through 13+ responses without per-response
       compliance statement. Owner had to explicitly remind. Fix in L114.
    NEVER assume internalized compliance. State it visibly per response.

36. NUMERICAL CLAIMS REGENERATED AT WRITE TIME — not inherited from prior context:
    a. Any number in a handoff, audit, commit message, or response (line counts, decision
       counts, costs, percentages, test counts, file counts) must be regenerated immediately
       before it's written
    b. Do not copy numbers from prior session output, prior responses, or memory
    c. If verification cannot be done in-context, omit or mark "approximate (last verified [date])"
    d. Same discipline as #26 (assumption validation) extended to numerical claims specifically
    e. Past mistake: Group α handoff carried "+121/-41" diff stat from prior session output
       without re-running git diff against current sandbox state. Fix in L116.
    NEVER write a number you didn't just verify.

37. INDUSTRY-STANDARDS COMPLIANCE for every recommendation — no exceptions:
    a. Cite the specific authoritative source(s) the recommendation draws from (textbook chapter,
       peer-reviewed paper, regulatory document, official broker docs, established methodology)
    b. Note which tradition the recommendation aligns with (institutional quant, retail systematic,
       academic finance, etc.) — practices differ across traditions
    c. If the recommendation deviates from standard practice, flag the deviation explicitly and
       justify it (e.g., "300 paired trades vs Bailey-Lopez de Prado's 1000-trade recommendation
       because retail-scale system with limited universe constrains achievable sample size")
    d. For statistical claims (sample sizes, significance thresholds, multiple-testing corrections,
       confidence intervals), cite the specific paper/textbook formula being applied
    e. Web-search to verify current best practice when recommendation hinges on a methodology
       choice; pricing/regulatory items per CHECKLIST #26 + L111
    f. Standard reference shelves for this project:
       - Statistical/methodology: Lopez de Prado (Advances in Financial ML), Bailey & Lopez de Prado
         (backtest overfitting), Harvey & Liu (multiple testing), Pesaran/Timmermann (walk-forward)
       - Risk: Hull (Options/Futures/Derivatives), Jorion (Value at Risk), CFA risk frameworks
       - Execution: Almgren-Chriss, Kissell (transaction costs), broker official docs
       - Portfolio theory: Markowitz, Kelly (with practical leverage caveats), Black-Litterman
       - Software for finance: separation of backtest/live, paper-trading discipline, walk-forward,
         no look-ahead bias, point-in-time data
       - Tax/regulatory: CRA Income Tax Folios, CIRO/IIROC bulletins, IRS Pub 550 (deferred topic
         this session per owner direction)
    g. RETROACTIVE: When this checklist item is added or strengthened, audit recently-resolved
       decisions in current session against the standard. Any that don't hold up must be flagged
       for owner re-decision — not silently grandfathered.
    NEVER make a recommendation without citing authoritative grounding. Ungrounded
    recommendations from prior Sonnet sessions produced 203 documented bugs.

38. STRATEGY-UNIVERSE VERIFICATION — before any A/B / backtest / sample-size decision:
    a. Grep PROJECT_PLAN.md, AUDIT.md, AUDIT_INDEX.md for every strategy class in scope
       (technical, ICT/SMC, fundamental, smart-money, options, macro, sentiment, mean reversion,
       momentum, trend-following, volatility, etc.)
    b. List which are currently implemented vs. planned (Phase 0.D ICT, Stage 3+ options, etc.)
    c. Verify the framework / backtest / sample-size calculation accommodates ALL strategy classes
       in the deployed-and-planned universe — not just the implemented subset
    d. If a strategy class is planned but not implemented, the framework must accommodate its
       future addition (e.g., A/B arm structures must allow extending to "rules + ICT" arm later)
    e. Past mistake: Round 1 Batch 2 A/B framework presented without verifying ICT/SMC was in
       scope per DECISION-045 + Phase 0.D. Fix in L117.
    NEVER present a methodology framework without first listing the full strategy universe
    it must operate over.

39. METHODOLOGY-LIBRARY ADOPTION TRIGGERS COMPANION DECISIONS:
    a. When a methodology library is adopted (TradingAgents, smartmoneyconcepts, QuantStats, etc.),
       immediately enumerate the methodology decisions the library does NOT make on its own:
       timeframe scope, parameter values, signal aggregation, weighting, threshold tuning,
       multi-timeframe combination rules, etc.
    b. Each enumerated methodology decision must be added to AUDIT_INDEX.md as a PENDING decision
    c. Library adoption is incomplete until ALL companion methodology decisions are at least logged
    d. Past mistake: DECISION-045 (smartmoneyconcepts library) was RESOLVED Pass 27 without
       companion decision on ICT timeframe scope. Owner had to surface the gap in Round 1
       (Pass 52). Fix in L118; new DECISION-343 to be added.
    NEVER mark a library-adoption decision RESOLVED without enumerating its companion
    methodology decisions in the registry.

40. PROJECT-PRIOR-ART GREP BEFORE PROPOSING NEW PRINCIPLES / FRAMEWORKS / DIRECTIONS:
    a. When owner directs a new philosophy, principle, or architectural approach, the FIRST step
       is grep CLAUDE.md + PROJECT_PLAN.md + AUDIT.md + AUDIT_INDEX.md for the relevant terms
    b. If prior art exists, surface it explicitly: "this is already documented at [location], and
       says [summary]. Do you want to (a) leave it as-is, (b) strengthen, (c) modify, (d) replace?"
    c. Do NOT propose to write the principle from scratch as if it's new ground
    d. Do NOT ask "interpretation A/B/C" before checking what's already there
    e. Past mistakes: L107, L117, L119 all share the pattern "recommended without first reading
       the project"
    f. This is CHECKLIST #26 (Assumption Validation) applied specifically to project documents:
       prior-art search is a free verification, do it first
    NEVER propose to add a "new" principle to project docs without first proving by grep that
    it isn't already there.

41. HANDOFF PRE-FLIGHT MUST CHECK DIRTY WORKING TREE — not just remote sync:
    a. Every handoff document's pre-flight section must include: `git status --short`
    b. Output must be empty before patch application proceeds
    c. If non-empty, output is shown to owner; handoff is HALTED until reconciled
    d. Three categories of non-empty status to handle:
       (a) Unrelated uncommitted work (e.g., data cache, in-progress feature) — commit or stash separately first
       (b) Untracked artifacts (typo files, OS junk) — clean up with `rm` after owner verifies they're not intentional
       (c) Tracked-but-uncommitted config files (e.g., `.claude/settings.local.json`) — add to `.gitignore` and `git rm --cached`, OR explicitly skip in `git add`
    e. NEVER trust "synced with origin" as proof of clean tree. Sync state ≠ working-tree state.
    f. Past mistake: Round 1 handoff (Pass 52) did sync check but not dirty-tree check. Owner's
       laptop had 480+ uncommitted Parquet files (Phase 1B cache); could have been silently
       included in Round 1 commit. Caught only because owner pasted full git status output.
       Fix in L120.
    NEVER apply a patch to a dirty working tree. Always reconcile dirty state first.

42. PRIOR-ART GREP MUST INCLUDE BUGS, NOT JUST DECISIONS — when proposing new decision/bug:
    a. Grep for matching DEC entries: grep "DECISION-" AUDIT_INDEX.md | grep -i "<keyword>"
    b. Grep for matching BUG entries: grep "BUG-" AUDIT_INDEX.md | grep -i "<keyword>"
    c. BOTH searches required. Bugs and decisions are stored in same INDEX file but tracked separately.
    d. Past mistake: Pass 52 — proposed DEC-349 (API endpoint inventory + agent-feed mapping) without
       checking BUG-190 (Quiver endpoints not prefetched, OPEN since Pass 18) and BUG-191 (no
       prefetch validation gate, CRITICAL OPEN since Pass 18). Both bugs covered most of the
       proposed decision's scope.
    e. Refines CHECKLIST #40 (project-prior-art grep) to explicitly include both decision IDs
       and bug IDs in search.
    NEVER propose a new decision/bug without searching both DEC and BUG entries for the topic.

43. OWNER ASKING "ALREADY IN AUDIT?" = MANDATORY FULL SEARCH FIRST:
    a. Trigger phrases: "is it already audited", "already flagged", "already tracked",
       "is it part of audit", "have we covered this", "is this in the plan"
    b. STOP all drafting on detection. Do NOT continue with proposal.
    c. Run prior-art search across ALL documents:
       - grep AUDIT_INDEX.md (DEC and BUG entries)
       - grep AUDIT.md (full text for related context)
       - grep LEARNINGS.md (relevant L-numbers)
       - grep CHECKLIST.md (existing rules)
       - grep PROJECT_PLAN.md (planning context)
    d. Show owner the prior art that exists with specific IDs and one-line summaries
    e. THEN ask: "this is covered by [X, Y, Z] — should I (a) surface them with new context,
       (b) add a forward-link note, or (c) propose something genuinely new not covered?"
    f. Past mistake: Pass 52 — three times in single session proposed new entries for
       topics already extensively in audit. L122 captures the pattern. 43 fixes the
       mechanical trigger.
    NEVER skip the full-document search when owner uses these trigger phrases.

44. DATA-CONSUMPTION AUDIT MUST INCLUDE RUNTIME PROBE:
    a. For any function that reads cached/external data (parquet, JSON, API), audit by RUNNING:
       - Identify cache source the function reads
       - Verify cache populated for at least 1 known ticker
       - Call function: `result = func(known_ticker, date_in_cache_range)`
       - Assert return is non-default (no "no_data", no "none", no zero counts)
    b. If default returned: investigate schema mismatch, type mismatch, filter logic
    c. Static reading is necessary but NOT sufficient — column-name typos, schema drift,
       and silent except blocks are invisible to read-audit
    d. Past mistake: 40+ audit passes Pass 1-51 missed BUG-270/271/272/273/274 (5 schema
       mismatch bugs). 90 minutes of runtime-probe in Pass 52 Stage 5.5 caught them all.
       L123 captures the pattern.
    e. Apply this discipline retrospectively to all existing data-consumption code paths
       (engine, signals, cache layer) — Stage 5.5 only audited smart_money + partial macro
    NEVER mark a data-consumption function as audited without running it.

45. **MANDATORY per-response checklist compliance statement (Pass 52 owner-elevated):**
    Every response must end with a visible "CHECKLIST: ✅ compliance" block.
    a. List each item that applied this turn and confirm satisfied (e.g. "✅ #43 prior-art")
    b. Items irrelevant to the turn can be omitted from the list
    c. If a violation occurred, list it explicitly with "⚠ #N violated — [reason]"
    d. No exceptions. Pure tool-use turns that yield without user-facing prose still
       require a compliance statement before yielding.
    e. Per L124. Owner has authorized strong action if the rule is repeatedly violated.
    f. The compliance statement is the LAST item in the response, after audit status table
       and other content.

46. **Strategy/feature coverage checks must cross-reference three sources (Pass 52 owner directive):**
    Per L125. For any question about whether a strategy, signal, primitive, or feature
    is covered:
    a. Code grep — current implementation state in screener.py/technical.py/exit_strategies.py/etc
    b. AUDIT_INDEX grep — bugs and decisions logged about it
    c. **PROJECT_PLAN.md grep** — what was DESIGNED to exist in scope
    A gap is real if ANY of these three sources contradicts the others:
    - Code missing what PROJECT_PLAN specifies = drift gap (previously-committed scope drifted out)
    - PROJECT_PLAN missing what audit specifies = scope expansion documented in audit only
    - Both code + PROJECT_PLAN missing what practitioner research says = research-suggested gap (lowest priority)
    Skipping #c was the exact mistake in Pass 52 side-note responses. Going forward,
    PROJECT_PLAN is mandatory third source.

47. **Prior-art grep must scan AUDIT.md full text in addition to INDEX (Pass 52 third-recurrence fix):**
    Per L126. Owner direct correction Pass 52: "you missed pending decisions in audit md yet again."
    a. AUDIT_INDEX.md grep — existing #43 — top-line table summaries only
    b. **AUDIT.md FULL TEXT grep** — NEW — substantive content lives here:
       - Pass 39 Section 9 strategy-category gaps
       - BUG-139 through BUG-167 inline-only bug entries
       - Pass 13 retest section
       - Plain-English strategy listings
    c. PROJECT_PLAN.md / PROJECT_PLAN_ARCHIVE.md grep (per #46)
    d. Code grep
    A finding is "no prior art" only when ALL FOUR are negative. INDEX alone is insufficient.
    Owner has had to re-prompt 3 times this session for this lapse. Fix is mechanical:
    extend grep targets in #43 to include AUDIT.md full text. Specifically search inline
    bug entries (BUG-NNN format with INLINE-ONLY status in INDEX requires full-text dive
    into AUDIT.md to read the actual entry).

48. **Enumerating in prose ≠ logging as decision (Pass 52 owner directive):**
    Per L127. Any response containing a list of "things to do / gaps / patterns
    to add / questions to consider / items remaining" — the same response must
    convert each enumerated item into one of:
    a. A logged decision (DEC-N PENDING) in AUDIT_INDEX + substantive section in AUDIT.md
    b. A logged bug (BUG-N OPEN) similarly
    c. An explicit deferral with reasoning ("not logging because [reason]")
    Past failures: Pass 52 had me list 7 chart pattern classes in prose with no
    logging; owner had to directly ask before they were entered into the catalog.
    Owner-readable prose != audit-tracked decision. Both must exist.

49. **Caveats must be logged in LIMITATIONS_CAVEATS_ASSUMPTIONS.md (Pass 52 owner directive):**
    Per L128. Every time:
    - A decision resolves WITH CAVEATS (e.g., "approved Step 1, defer Step 2")
    - A runtime probe surfaces a known limitation
    - A methodology choice has an honest tradeoff
    - A piece of code has a self-acknowledged shortcut (e.g., "acceptable for Phase 1")
    The caveat must be logged in LIMITATIONS_CAVEATS_ASSUMPTIONS.md as CAV-NNN.
    Format: Source (DEC/BUG/pass) / Status (ACTIVE/MITIGATED/RESOLVED Pass N) /
    Caveat (plain English) / Operational impact / Forward-link.
    Append-only convention per L109 — never delete; mark RESOLVED with forward-link
    if underlying issue resolves.
    Cross-reference from source decision/bug entry in AUDIT.md.
    Past mistake: 56 caveats buried in 20,000+ lines of audit prose pre-Pass-52.

49. **(Already exists — CAV-NNN registry — see L128.)**

50. **Caveats/assumptions/limitations must also appear inline in PROJECT_PLAN.md (Pass 52 owner directive, additive to #49):**
    Per L129. CAV-NNN registry (LIMITATIONS_CAVEATS_ASSUMPTIONS.md) is audit-grade
    and stays append-only. Additionally, when a section of PROJECT_PLAN.md
    describes a feature/methodology/data source with a known CAV-NNN caveat:
    a. The caveat must appear inline at the relevant section (not in a separate
       appendix at the bottom)
    b. Brief inline call-out only — not the full operational-impact text
       (that stays in CAV file)
    c. Format: "*Caveat: [short description] (CAV-NNN)*" inline
    d. Cross-reference CAV-NNN ID so reader can dive deeper
    e. When the underlying decision RESOLVES a caveat, BOTH places update —
       inline note becomes "Resolved Pass N — see CAV-NNN" rather than
       disappearing (preserves historical context for re-reading)
    Distinction from #49: #49 = formal registry; #50 = readability inline.
    Both required; neither sufficient alone.

51. **Do not infer approval beyond owner's explicit statement (Pass 52 owner pushback):**
    Per L130. Before logging any decision as "owner-approved":
    a. Identify the EXACT verbatim owner directive that approves it
    b. Quote it in the decision entry: "Per owner directive: '[verbatim]'"
    c. If owner directive is NARROWER than the proposal:
       - Log only what was explicitly approved (narrow scope)
       - Keep broader proposal as PROPOSED (not approved) with note "AWAITING OWNER APPROVAL"
    d. "Agree with recs on rest" only refers to recommendations made BEFORE that
       statement; does not extend to subsequent recommendations
    e. Silence is not approval. Owner not addressing a proposal explicitly = it
       remains PROPOSED
    f. Directional statements during question/exploration phases are DIRECTIONAL,
       not APPROVAL. They guide subsequent proposals; do not authorize specific
       implementations.
    Past failure: Pass 52 commit f3e43580 logged DEC-363/364/365/366 as
    "owner-approved" when only narrow components were directed. Corrected by
    narrowing scope or downgrading to PROPOSED.
    Sister rule to #48 (under-logging direction); this is the over-logging direction.

52. **Ambiguous owner directives default to lower-impact action; never infer approval (Pass 52 L131):**
    Per L131. When owner directive could mean either "execute current batch + advance"
    OR "advance without executing":
    a. Default to advance WITHOUT executing
    b. If genuinely uncertain, ASK explicitly with both interpretations
    c. Brief directives like "proceed", "continue", "next", "move on", "go" almost
       always mean "advance, do not execute" when prior turn was a recommendation
       set awaiting approval
    d. Owner approval words ("approve", "go ahead", "do it", "yes") = execute
    e. Owner advancement words ("proceed", "continue", "next", "move on") = advance
       without executing the prior recommendations
    Past failures: Pass 52 had me interpret "Lets proceed" as approval of 6 Theme 3
    decisions + log 13 sub-decisions. Owner meant "move to next batch." This was
    fifth Pass 52 process recurrence; L130/CHECKLIST #51 was supposed to prevent
    this class of error but didn't catch the ambiguous-brief-directive variant.
    Bias toward ASK over assume — clarification round is cheaper than rollback.

53. **Grounded-recommendation format mandatory (Pass 52 sixth process recurrence — owner trust mechanism):**
    Per L132. Every recommendation in responses must include 5 verification elements
    BEFORE stating the recommendation:
    a. **CURRENT STATE** — paste actual grep/code-output, not summary
    b. **PROJECT SCOPE** — date range + universe size + period coverage from cache + PROJECT_PLAN
    c. **SCOPE FIT CHECK** — explicit yes/no with math (does the rec apply to OUR data?)
    d. **EXISTING INFRASTRUCTURE CHECK** — does anything in code already do part of this?
    e. **FEASIBILITY MATH** — for any numeric threshold, compute what it means for our data
    Skip any element → flag rec as `UNVERIFIED — pattern-match only`.
    Confidence labels:
    - "Verified: [list grep checks]" only when 5/5 elements present
    - "Pattern-matched: [industry source]" when relying on heuristic
    - NEVER "Confidence: HIGH" without verification work shown
    Past failures: Pass 52 had me recommend (1) 2008/2020 stress-test thresholds for periods
    our backtest doesn't cover; (2) 300-trade floor that excludes legitimate event-driven
    strategies; (3) 5-indicator macro factor list when codebase already pulls 9 indicators.
    All three were caught by owner's common-sense questions; all three were avoidable with
    one grep + one math check. This rule makes those checks mandatory and visible to owner
    so a non-technical reviewer can audit the verification work, not just the recommendation.

54. **Test-run audit gate (Pass 52 L133 — CRITICAL process gate before full implementation):**
    Per L133. Decisions transition from "owner-approved" to "implementation-ready"
    only after passing limited-sample test-run validation. Sequence:
    a. Full data prefetch complete (DEC-410 API audit + DEC-411 OHLCV extension)
    b. All themes reviewed — every audit decision walked through
    c. Limited-sample test run: 10 tickers × 60 days × current strategies
    d. Per-decision validation table populated in AUDIT_TEST_RUN_RESULTS.md:
       - decision_id
       - recommendation (logged in audit)
       - test_signal (what to look for in test output)
       - test_output_expected (concrete expected pattern/value)
       - test_mismatch_action (what we do if test fails)
       - test_mismatch_flag (binary true/false after test run)
    e. TEST_MISMATCH=true → investigation/revision required before full implementation
    f. TEST_MISMATCH=false → proceed to implementation
    Catches errors surviving CHECKLIST #43 (prior-art), #46 (three-source check),
    #53 (grounded-recommendation format) — empirical validation is the final gate.
    **Retroactive scope (Pass 52 owner directive):** Applies to ALL ~419 decisions
    in AUDIT_INDEX.md (PENDING + RESOLVED + all states), not just Pass 52 ones.
    Effort ~35 hrs for full population. Older decisions may be flagged as
    `OBSOLETE_BY_TEST_RUN` if system evolution since original logging makes them
    no longer applicable (CAV-057).

55. **Phase scope check (Pass 52 L134 — architectural framing gate before walkthrough):**
    Per L134. Before walking through any Phase 1B-α decision (or any phase-deliverable
    decision: Phase 0, Stage 1, Stage 2, Stage 3, Stage 4), explicitly classify:
    a. **Patch-level:** stand-alone fix/metric/gap → normal batch review
    b. **System-design-level:** defines phase output structure, methodology, dimensional
       scope, or framework → focused walkthrough as its own decision; cannot be batched
    If a decision is system-design-level but framed as patch-level, FLAG and propose
    elevating to its own decision before continuing patch-level batch review.
    Layered defense alongside #43/#46/#47/#53/#54:
    - #43/#46/#47: catch duplicates (prior-art + three-source + full-text)
    - #53: catch scope/feasibility errors (grounded-recommendation format)
    - #54: catch empirical-failure errors (test-run audit gate)
    - #55: catch architectural-framing errors (THIS — phase scope check)
    Past failures (Pass 52 4-turn recurrence): treating DEC-068/069 as patches when
    they were components of system-design-level DEC-422 dimensional framework. Owner
    caught after 4 consecutive turns.

56. **Focus-phase scope filter (Pass 52 L135 — forward-looking deferral discipline):**
    Per L135. Owner has defined current focus phases (Pass 52: Phase 0 + Stage 2);
    decisions affecting other phases (Stage 3 paper / Stage 4 live / Stage 5 scaled)
    must be deferred, not approved.
    Per-decision scope-filter check (mandatory before approval):
    a. **What phase does this primarily affect?** (Phase 0.A-E / Stage 1 / Stage 2 /
       Stage 3 / Stage 4 / Stage 5)
    b. **Is that phase in current owner-defined focus?**
    c. **If NOT:** mark DEFERRED_TO_<TARGET_STAGE>; do not approve in current batch;
       preserve original scope text for future re-walk
    d. **If IN focus:** proceed with normal walkthrough
    Layered defense expanded (Pass 52):
    - #43/#46/#47: catch duplicates
    - #53: catch scope/feasibility errors (grounded format)
    - #54: catch empirical-failure errors (test-run audit)
    - #55: catch architectural-framing errors (patch vs system-design)
    - #56 (THIS): catch focus-phase scope-filter errors (forward-looking deferral)
    Past failures (Pass 52 turn 8): Theme 6 DEC-129/130/132 approved as Stage 3→4
    gates when scope filter was implicit. Owner directive made filter explicit;
    these were retroactively deferred per L135.

57. **Use-case mapping discipline (Pass 52 L136 — this-system vs generic-template):**
    Per L136. Before stating any recommendation involving audits, schemas, inventories,
    framework designs, data architectures, test infrastructure, or output formats,
    explicitly map against this system's actual use cases:
    a. **Who consumes the output?** (60+ strategies, ~11 agents, DEC-422 cube dimensions,
       PIT loader, owner decisions, etc.)
    b. **Does the proposed structure surface what each consumer needs?**
    c. **Is the structure shaped by THIS system's contexts, or by generic templates?**
    Reuse-test: if the recommendation could be applied unchanged to a different
    trading system or different domain, that's a flag. Generic-by-default
    recommendations don't address this system's specific gaps.
    Past failure (Pass 52 turn 15): DEC-410 initial audit schema was endpoint-inventory
    level (subscription/endpoints/consumption/gaps/recs) — surface-level despite
    owner verbatim "should not be surface level but a deep dive." Owner had to ask
    "is it comprehensive for our use cases?" before I expanded to 6 use-case
    dimensions (PIT-safety, universe coverage, strategy mapping, agent mapping,
    cube dimension sourcing, rate-limit feasibility).
    Layered defense (Pass 52 expanded to 7 levels):
    - #43/#46/#47: duplicates
    - #53: scope/feasibility (grounded format)
    - #54: empirical-failure (test-run gate)
    - #55: architectural-framing (patch vs system-design)
    - #56: focus-phase scope-filter (forward-looking deferral)
    - #57 (THIS): use-case mapping (this-system vs generic-template)

58. **Sprint-tracker assignment as RESOLVED-DECIDED commit requirement (Pass 52 L137 — execution-tracking discipline):**
    Every RESOLVED-DECIDED status flip MUST include sprint-tracker assignment
    in the SAME commit as the status flip. Audit-text alone is insufficient
    documentation for execution.
    Required propagation per RESOLVED-DECIDED commit:
    - **AUDIT_INDEX.md:** status flip applied
    - **AUDIT.md:** narrative section appended
    - **ENGINEERING_REGISTER.md:** sprint slot assigned IF decision has implementation work
    - **DOCUMENTATION_REGISTER.md:** bucket assigned IF documentation-only / cross-ref / methodology / stage-deferred
    - **IMPLEMENTATION_READINESS_DASHBOARD.md:** sprint readiness updated IF sprint scope changed
    Decision flow:
    1. Does this decision require code changes (new module, refactor,
       integration, test infrastructure)? → ENGINEERING_REGISTER sprint slot
    2. Is this decision a methodology choice, library selection, cross-reference
       to another decision, foundational/integrated, OR stage-3+/4+ operational?
       → DOCUMENTATION_REGISTER bucket (A-E)
    3. Both paths must result in tracker entry. None can be skipped.
    Past failure (Pass 52 turns 65-95): flipped 294 RESOLVED-DECIDED across
    walkthroughs; only 46 (15.6%) made it into ENGINEERING_REGISTER. Owner
    caught structural gap turn 96 ("Identified improvements - added for
    execution?") then turn 98 ("This is very basic stuff and we had already
    discussed this. you are simply not following it").
    Anti-pattern explanation: "decided but homeless" — RESOLVED-DECIDED status
    without sprint home means no engineer (owner included) ever picks it up
    for implementation. Decision graveyard.
    Layered defense (Pass 52 expanded to 8 levels):
    - #43/#46/#47: duplicates
    - #53: scope/feasibility (grounded format)
    - #54: empirical-failure (test-run gate)
    - #55: architectural-framing (patch vs system-design)
    - #56: focus-phase scope-filter (forward-looking deferral)
    - #57: use-case mapping (this-system vs generic-template)
    - #58 (THIS): execution-tracking discipline (sprint-tracker assignment
      as RESOLVED-DECIDED commit requirement)

59. **Architectural assumption verification before parameter application (Pass 52 L138 — directive execution does not override flagging duty):**
    Per L138. Before executing owner-directed parameters on a spec, verify the spec's referenced primitives (agents, systems, components, architectures) exist as named in the actual underlying system. If gap found between spec assumptions and actual architecture, SURFACE TO OWNER BEFORE executing parameters — owner directives operate on the underlying architecture, not on Claude's assumed model of it. Example trigger: DEC-042 turn 121 executed owner parameters ("weighted / continuous-score / must align / tier modifier") without first verifying named agents (Bull/Bear/Risk/ChartAnalyst as parallel voters) match TradingAgents architecture (sequential debate-and-synthesize through Portfolio Manager). Owner accountability question turn 128 surfaced the gap; supersession via DEC-459 Option C Hybrid Architecture turn 129. Pre-flight must include: (a) Verify all named primitives exist; (b) Verify architectural fit (parallel vs sequential, native vs synthesized); (c) If gap, present to owner with options BEFORE applying parameters; (d) Per #51 (don't infer approval beyond explicit statement) — same principle applies to assumed architectural alignment.

60. **Data dependency verification on architectural decisions (Pass 52 L139 — phantom completeness from unmapped data feeds):**
    Per L139. Before marking architectural decisions RESOLVED-DECIDED, audit data input requirements for every component the architecture creates dependencies on. Five required steps: (a) Per-component data input requirements documented; (b) Current data feeds mapped against requirements; (c) Gaps identified with severity classification; (d) Resolution candidates proposed with cost estimates; (e) Owner approval BEFORE marking architectural decision RESOLVED-DECIDED. Example trigger: Pass 25-29 resolved DEC-042/051/055-058 (TradingAgents framework adoption) without auditing per-agent data input requirements. Pass 31 documented 11-agent roster but didn't map per-agent data dependencies. Result: Stage 2 A/B testing would have measured "agents-with-degraded-input vs rules-with-full-input" — invalid comparison invalidating DEC-131 ≥0.2 net Sharpe gate. Owner accountability question Pass 52 turn 130 surfaced this; supersession via 9 new decisions (DEC-460 through DEC-468) Pass 52 turn 130 establishing custom toolkits + state augmentation. Pattern alignment with Pass 29 BUG-113 finding ("agent emits 31 fields, engine reads 2"): same shallow integration but for inputs not outputs. Apply checklist: (i) when adopting any new framework or library; (ii) when integrating with external systems; (iii) when wiring agents/orchestrators that consume from multiple data sources.

61. **Adversarial document review before declaring canonical documentation complete (Pass 52 L140):**
    Per L140. Apply 5-pass adversarial methodology before marking canonical documents production-ready: (Pass 1) execution simulation Sprint 0 → Stage end with every micro-step probed for "what needs to be true / is it documented / will it work"; (Pass 2) data dependencies + cross-document coherence; (Pass 3) edge cases + failure modes + real-world ops; (Pass 4) statistical / methodological rigor especially capacity checks; (Pass 5) process / governance / unstated assumptions. Example trigger: Pass 52 turn 132 ADVERSARIAL_AUDIT identified 167 gaps + 10 Stage 2 effectiveness blockers in PROJECT_PLAN + TRADINGAGENTS_DATA_AUDIT + TRADING_RULES that were not visible in ordinary linear review. The 167 gaps existed BEFORE owner asked — they emerged from "what happens when X" probing. Without this audit, Stage 2 effectiveness was at risk of being invalidated regardless of Sprint 1-9 execution quality.

62. **Cross-document consistency verification on canonical doc updates (Pass 52 L141):**
    Per L141. When canonical docs are updated, verify cross-references remain consistent: (a) Quick Reference Index ↔ section count match; (b) Document Map enumerates all canonical docs; (c) Inline cross-references (e.g., "see TRADING_RULES §X") point to existing sections; (d) Sprint ↔ phase mapping consistent across docs; (e) Effort estimates reconcile across PROJECT_PLAN + ENGINEERING_REGISTER + IMPLEMENTATION_READINESS_DASHBOARD. Example trigger: Pass 52 turn 132 audit found PROJECT_PLAN §29.1 Document Map missing TRADINGAGENTS_DATA_AUDIT.md (created turn 130, but §29 not updated); TRADING_RULES §6.3 mentions Russell 1000 but PROJECT_PLAN §6 universe architecture doesn't; §18.1 lists 4 A/B arms but §7.8 + PROJECT_PLAN §9.4 list 5.

63. **Adversarial audit must compare current docs against archived/historical docs (Pass 53 L142):**
    Per L142. Adversarial audit methodology must include archive comparison ("what was in old doc that's missing from new doc?") not just within-current-doc consistency. Steps: (a) Identify all archived/historical docs (`*_ARCHIVE.md`, `*_v[0-9]*.md`, deprecated sections moved to comments); (b) For each archived doc, list all phases/sections/decisions that existed; (c) For each archived item, verify it exists in current docs OR is explicitly documented as removed/superseded with reason; (d) Items not in current docs and not documented as removed = silent omissions. Example trigger: Pass 53 owner question "Why was phase 1A dropped" surfaced Phase 1A omission. PROJECT_PLAN_ARCHIVE.md showed Phase 1A v3 was COMPLETE (67 instruments × 4yr × 6,942 trades; atr_trail_1x confirmed). Pass 52 turn 119 absorbed DEC-014 Phase 1B passing criteria into DEC-422+426; Phase 1A reference inadvertently dropped from §3 sub-phases. ADVERSARIAL_AUDIT (Pass 52 turn 132) compared current PROJECT_PLAN vs current TRADING_RULES vs current TRADINGAGENTS_DATA_AUDIT but didn't compare against PROJECT_PLAN_ARCHIVE — meta-failure of audit methodology. Restoration via DEC-486/487/488 PROPOSED Pass 53. Apply checklist: (i) every adversarial audit pass (Pass 5+ = include archive comparison); (ii) before declaring documentation "canonical" or "complete"; (iii) when refactoring methodology that absorbs prior phases (high risk for archival drop).

64. **"Sprint ready" requires both decision-state AND artifact-state verification (Pass 53 L143):**
    Per L143. Before claiming a sprint is ready to start (or that "Sprint X has zero PENDING decisions"), run a precondition-audit that verifies BOTH:
    (a) **Decision-state:** all DECs in sprint scope are RESOLVED-DECIDED in AUDIT_INDEX
    (b) **Artifact-state:** for every input file/directory/credential the sprint's decisions reference, verify (i) the artifact exists on disk; (ii) it is populated with real data, not header-only placeholders or empty CSVs; (iii) sample read returns expected schema/shape; (iv) any owner subscription/credentials referenced are verified working via smoke test.
    Decision-state alone is INSUFFICIENT. Example trigger: Pass 53 turn (this) — claimed "Sprint 1 has zero formally-PENDING decisions; technically ready to start" because DEC-477/483 were RESOLVED-DECIDED, but `data/universe/historical_membership.csv` (DEC-477 referent) did not exist; `extended_universe.csv` (DEC-103 referent) and `momentum_watchlist.csv` (DEC-104 referent) existed only as header-only placeholders. This is the same failure pattern as Pass 52 turn 130 (DEC-051 data-dependency gap caught by owner) — recurrence after L139 codified suggests L139 was treated as advisory rather than mandatory pre-flight. Apply checklist: (1) before any "sprint ready" claim; (2) before any "no blockers" statement; (3) before drafting prefetch/build scripts that assume input files exist. The verification is a 30-second `ls` + `head` + `wc -l` check, not optional. Ties into L139 (data dependency verification) and codifies the artifact-existence step that L139 omitted.

65. **Roster definitional check before adding items (Pass 53 L144):**
    Per L144. When adding a sub-decision or new entry to any canonical roster (STRATEGY_REGISTER.md, exit method list in TRADING_RULES.md §8, signal universe DETAILED_PROJECT_PLAN.md §2.5, pre-trade filters DETAILED_PROJECT_PLAN.md §2.4.6, circuit breakers TRADING_RULES.md §9, etc.), explicitly verify the new item meets the roster's stated definition before listing it. Steps: (a) Locate the roster's definition statement (usually the section's opening sentence); (b) Hold the candidate against that definition — does it qualify? (c) If not, find the correct sibling roster, or create one with its own definition; (d) Cross-check counts/totals against the canonical roster doc (e.g., STRATEGY_REGISTER.md for strategies) before propagating count claims into other docs. Example trigger: Pass 53 turn (this) — owner asked why exits were in the strategy roster; investigation revealed DETAILED_PROJECT_PLAN.md §2.4 Layer 4 listed exit methods (DEC-432/433) and a circuit breaker (DEC-435) as strategies because they were sub-decisions of strategy-related parents, even though §2.4's own definition ("each strategy is a self-contained signal generator with entry/exit/sizing rules") excluded them. Inflated count by ~9-10. Same inflation propagated to PROJECT_PLAN.md §7.2 count formula. Sibling rosters added (§2.4.5 exit methods, §2.4.6 pre-trade filters). Apply checklist: (1) before adding a sub-decision to any roster section; (2) before quoting a roster total in a different doc; (3) when reviewing roster sections during adversarial audits (cross with #61). The verification is reading the section's definition statement and asking "does this candidate qualify?" — not optional. Ties into #62 (cross-doc consistency) and complements #64 (artifact-state) — both are roster-integrity disciplines on different axes.

66. **DEC target alignment verification before claiming resolution (Pass 53 — pre-flight catch instance):**
    Before stating that any documentation fix, code fix, or status flip "resolves DEC-X", "implements DEC-X", or "DEC-X covers this", verify in AUDIT_INDEX.md that DEC-X's actual decision body text speaks to the same scope as the resolution being claimed. Steps: (a) grep AUDIT_INDEX.md for the DEC number; (b) read the decision title + body — does it actually match the topic at hand? (c) if mismatch, the claim is wrong — find the actual DEC that targets the topic, or surface that no DEC exists; (d) cross-check audit-row tags too: a DEC tag on an audit row may be a *cluster reference* (the question was discussed in that DEC's cluster) rather than the substantive decision-target. Example trigger: Pass 53 turn (this) — initial recommendation cited "resolve DEC-476" as the smart money composite formula resolution path because AUDIT.md row 44 (line 25831, Pass 52 turn 133 cluster 3) tagged the smart money question with DEC-476. Pre-flight grep against AUDIT_INDEX.md:512 revealed DEC-476 is actually the Portfolio class API specification (open_positions / cash_available / sector_concentration / etc) — completely unrelated to smart money. The audit row's DEC-476 tag was a cluster reference, not the substantive decision-target. Halted before edits; corrected to DEC-332 (Smart money composite scoring weights — the actual smart-money decision). Apply checklist: (1) any "DEC-X is resolved by this" / "this implements DEC-X" / "DEC-X covers Y" claim, before drafting that text; (2) before status flips RESOLVED-DECIDED → RESOLVED-IMPLEMENTED in AUDIT_INDEX; (3) when referencing DECs in commit messages or PR descriptions; (4) when cross-referencing audit-row DEC tags as if they were decision-target tags. The verification is a single grep + 1-line skim of the decision body — 15 seconds. Ties into #43 (cross-doc consistency), #62 (canonical-doc cross-references), L143 (decision-state vs artifact-state distinction). Distinct from #64 (sprint-scope DEC existence audit) — this checks DEC *scope alignment*, not DEC existence.

    **Pass 53 refinement — universe-tier categorization (sister axis to DEC-attribution):** The same scope-alignment discipline applies when characterizing universe tiers (Tier 1/2/3, T1a/T1b/T1c sub-tiers per DEC-483, ETFs per DEC-118, spinoffs/IPOs per DEC-103/104). Before claiming "Tier N = X" or "T1x covers Y", verify against (a) the actual file contents (e.g., `head extended_universe.csv` to see schema; `head momentum_watchlist.csv`); (b) the refresh script docstring (e.g., `scripts/refresh_extended_universe.py:1-20`) which states the inclusion criteria; (c) the canonical DEC body (DEC-483 for sub-tier definition, DEC-118 for ETF placement, DEC-103/104 for Tier 2/3 universe parents). Memory of "what tier contains what" drifts between sessions and across rule changes — verification against actual artifacts is required, not assumption. Example trigger: Pass 53 turn (this) — characterized "Tier 2 = ETFs/sector funds" in commit 6d4b5303's AUDIT.md entry. Wrong: ETFs are in Tier 1 per DEC-118 (separate bucket alongside S&P stocks); Tier 2 = spinoffs + recent IPOs per refresh_extended_universe.py:7-9. Owner caught via direct fact-check question. Bonus catch: revealed implementation drift — DEC-483 Pass 53 moved NDX-non-S&P from Tier 2 → T1c, but refresh_extended_universe.py still lists Nasdaq 100 non-S&P as Tier 2 inclusion criterion (DEC-494 PROPOSED to fix). Apply: (1) any "Tier N = ..." / "T1x covers ..." claim; (2) before stating which file holds which content; (3) when explaining universe architecture in narrative or commit messages; (4) when introducing new tier additions or restructuring. The verification is `head <file>.csv` + reading the refresh script's first 20 lines + checking the relevant DEC body — under 30 seconds.

    **66.b Pass 53 sub-clause — data flow verification (input universe ≠ output universe; Pass 53 owner Q-D codified):** For any recommendation involving a universe-construction step, signal computation, screener, or filter, EXPLICITLY state and verify three properties at recommendation time: (a) input universe source — broad market vs T1 vs T2 vs single ticker (e.g., "input = Polygon `/v2/aggs/grouped/locale/us/market/stocks/{date}` for ~6000-8000 listed equities" NOT "input = T1 cache"); (b) output universe target — which tier/file/cube cell receives the output (e.g., "output = top 100 non-T1 ranked → `Backtesting universe/momentum_watchlist.csv` rows"); (c) data-flow direction matches the stated purpose (e.g., "T3 = top 100 NON-T1 momentum names" requires INPUT outside T1, not re-rank of T1 cache). Skipping (a)/(b)/(c) verification = pre-flight failure regardless of methodology correctness. Methodology spec (e.g., J-T 12-1 formula) without data-flow spec is necessary but not sufficient. Pattern lineage (4 Pass 53 catches with same signature): DEC-476 vs DEC-332 (right methodology, wrong DEC target); DEC-368 vs DEC-370 (right methodology, wrong DEC target); Tier 2 = ETFs (right tier reference, wrong content type); DEC-496 T3 (right J-T formula, wrong input universe — implicit T1 cache instead of broad-market screener). All four = methodology-correct + data-flow-wrong. Owner Q-D approved Pass 53 codification. Apply: (1) any universe-build / screener / filter / signal-compute recommendation; (2) before drafting any DEC body that proposes a methodology; (3) when characterizing which data feeds which downstream consumer; (4) cross with #66 universe-tier sub-clause for tier-identity verification. Verification format: 3-property block in pre-flight — "INPUT: {source}; OUTPUT: {target}; FLOW: {input → ... → output matches stated purpose}". 30 seconds; not optional.

67. **Per-turn document sync sweep (Pass 53 owner directive 2026-05-05 — MANDATORY end-of-turn rule):**
    At the end of EVERY turn that produces meaningful changes (renames, RESOLVED-IMPLEMENTED status flips, new DEC bodies, new universe data, schema migrations, code refactors, count changes, etc.), sweep ALL forward-looking documents outside the archive folder for necessary modifications and update them in the same atomic commit. The intent: at end of every turn, all documents are in sync — no deferred-doc-sweep debt, no stale references.

    **Scope — what gets swept:**
    - All `*.md` files at repo root EXCEPT those in `archive/` folder (point-in-time snapshots — see L143)
    - All `*.md` files under `scripts/`, `backtest/`, etc. that are forward-looking (READMEs, design docs)
    - `CLAUDE.md`, `AUDIT_INDEX.md` (DEC bodies — current canonical state), `CHECKLIST.md`, `LEARNINGS.md`, `PROJECT_PLAN.md`, `DETAILED_PROJECT_PLAN.md`, `TRADING_RULES_AND_INFORMATION.md`, `STRATEGY_REGISTER.md`, `BUG_REGISTER.md`, `ENGINEERING_REGISTER.md`, `DOCUMENTATION_REGISTER.md`, `IMPLEMENTATION_READINESS_DASHBOARD.md`, `EXPLANATION.md`, `README.md`, `UNIVERSAL_LEARNINGS.md`, etc. (AUDIT_TRIAGE.md / PASS_NN_PRIORITIES.md archived Batch 425/426)

    **Scope — what is EXCLUDED (per L143 don't-rewrite-history):**
    - `archive/**` (literal archive folder — point-in-time snapshots stored here are immutable)
    - `AUDIT.md` historical narrative entries (per-turn entries describing past actions are immutable; new entries appended each turn but old entries NOT modified)
    - Pass-specific archive docs (e.g., `PROJECT_HANDOFF_YYYY-MM-DD.md`, `*_PASS_NN_TURN_NN.md`, `CRITICAL_GAPS_RESOLUTION_PASS_NN_*.md`, `ADVERSARIAL_AUDIT_PASS_NN_*.md`) — these are point-in-time snapshots and belong in `archive/`

    **What counts as "necessary modifications":**
    - (a) Stale filename/path references → UPDATE to new canonical name
    - (b) Status field changes (e.g., "Sprint 1 pending" → "RESOLVED-IMPLEMENTED") → UPDATE
    - (c) Count/threshold/ticker-number changes (e.g., "484 tickers" → "503 tickers") → UPDATE
    - (d) Cross-references to renamed entities (DEC numbers, file paths, schema names, universe-tier identifiers) → UPDATE
    - (e) Forward-looking task lists, pending items, owner blockers → UPDATE to current state
    - (f) Decision body content in `AUDIT_INDEX.md` reflecting current canonical state → UPDATE
    - (g) New checklist items, new DEC bodies, new lessons → APPEND
    - (h) Sprint-progress trackers (PASS_NN_PRIORITIES, IMPLEMENTATION_READINESS_DASHBOARD) → UPDATE per current state

    **Workflow:**
    1. Before drafting end-of-turn commit: `grep -l "<old_pattern>"` across all forward-looking docs to identify references needing update
    2. Apply updates in bulk (`sed`-like or Python find-replace for mass renames; manual Edit for nuanced changes)
    3. Verify: `grep -L "<new_pattern>"` returns expected files; `grep "<old_pattern>"` returns only `archive/**` + AUDIT.md historical entries
    4. Include all updated docs in the SAME commit as the originating change (atomic; no "doc-sweep follow-up" deferred commits)
    5. End-of-response compliance statement (#45) explicitly notes which docs were swept this turn

    **Triggers (apply rule at end of turn that includes any of):**
    - File rename (renames trigger reference updates across all docs)
    - DEC status flip (RESOLVED-DECIDED → RESOLVED-IMPLEMENTED, etc.)
    - New DEC body added
    - Schema migration (column rename, column add/remove)
    - Cache/data milestone (e.g., universe build → "complete" state)
    - Sprint/Phase status change
    - Count/threshold value change in any spec
    - New CHECKLIST/LEARNINGS entry being added

    **Exception/grace:** Pure logging actions (committing already-approved decisions to AUDIT) and trivial edits (typo fixes, single-line additions to AUDIT narrative) DO NOT trigger full sweep — but if those touch a doc with stale refs to recently-renamed files/concepts, the touch DOES trigger inclusion in sweep.

    **Past failure pattern (motivating rule):** Pass 53 owner repeatedly observed deferred-doc-sweep debt: rename happens in commit N, code/critical docs updated, but ~9 forward-looking docs left with stale references "deferred to a later commit." Owner directive 2026-05-05: this debt accumulates and creates inconsistency between turns. Going forward, NO debt — every turn ends with all docs in sync. Apply checklist: before drafting end-of-turn commit message, run grep-sweep verification. If ANY forward-looking doc has stale ref, it's included in commit. Period.

    **67.b — Doc commits decoupled from pending runs (Pass 53 owner clarification 2026-05-05):** Document updates MUST commit each turn regardless of pending long-running operations (background SCREENERs, prefetch tasks, multi-hour API jobs). Past failure pattern: I held the entire commit waiting for T2 SCREENER (~3 hour run) to complete, leaving Sprint 0A definition + DEC-497/498/499 + 18+ doc updates uncommitted and invisible to owner on main. Owner-flagged 2026-05-05: "Document updates are not linked to pending runs. Document updates need to be committed each turn."

    **Workflow (corrected):**
    1. Doc updates committed at end of every turn (atomic with code/data changes that ARE complete)
    2. Long-running operations commit SEPARATELY when complete (follow-up commit; not blocked by pending docs)
    3. If a pending run produces data that needs to be referenced in docs, the docs can include forward-looking references ("expecting X tickers; will commit final state when SCREENER completes") — don't block the doc commit on data finalization
    4. Each turn's commit shows up on main BEFORE the next turn begins; owner sees the work in real time

    **Anti-pattern to avoid:** "Single atomic commit when ALL pending runs complete" — this conflates doc-sync (turn-bound) with run-finalization (independent). Multiple commits per turn are fine if pending runs complete asynchronously. Each commit is atomic for its scope (doc-sync OR run-output), not for "everything happening this turn."

68. **Smoke → demo → full execution protocol for ALL multi-call API operations (Pass 53 owner directive 2026-05-05; codified after T2 SCREENER batching violation):**
    For ANY operation that issues N>10 API calls (prefetch, screener, bulk fetch, mass refresh), execute in three explicit stages with verification gates between each:

    **Stage 1 — Smoke (1-5 calls):** verify auth + endpoint URL + schema + non-empty response. Wall time: 1-5 min. Success = HTTP 200 + parseable response + expected schema fields. If ANY fail → halt + investigate.

    **Stage 2 — Demo (small batch, 50-500 calls):** run with `--max-N` flag at small size; verify rate, schema integrity, output format, edge cases (empty results, 404s, rate limit). Wall time: 5-30 min. Verifier script asserts schema + sample content sanity. If failures > expected threshold → halt + investigate.

    **Stage 3 — Full scale:** only after Stages 1+2 PASS. Owner approval gate before launch if wall time > 30 min OR API has per-call cost. Run with progress reporting (`python -u` for unbuffered stdout; print every N=50 or 100 calls).

    **Trigger conditions:**
    - Any prefetch script for N>10 tickers
    - Any SCREENER walking all of universe
    - Any global pagination (e.g., /v3/reference/dividends without ticker filter)
    - Any backfill where N>10 entities

    **Required CLI flags on prefetch / screener scripts:**
    - `--limit-tickers N` or `--max-candidates N` for demo gate
    - `--tickers T1 T2 ...` explicit list for smoke
    - Default to demo size if neither flag provided (safer than default-full)

    **Past failure pattern (motivating rule):** Pass 53 T2 full SCREENER (`scripts/build_tier2_screener_full.py`) ran with no batching, scanned all 15,401 Polygon tickers in single foreground run; original task hung 50+ min with no stdout (Python buffering through `tee`); restart with `python -u` revealed ETA ~108 min total. Pre-existing `--max-candidates` flag was IGNORED on first run despite being there for batching purposes. Owner-flagged 2026-05-05: "Why so much time? Why restart? I thought the directive was to run in batches." Going forward, every multi-call API operation is staged smoke → demo → full WITH per-stage owner approval gate. NO exceptions, even if API has zero per-call cost (because wall-time + risk-of-failure compound at scale).

    **Verification format in pre-flight:** state explicitly "Stage 1 smoke completed (X PASS); Stage 2 demo completed (Y PASS); proceeding to Stage 3 full scale at owner approval." If skipping any stage, surface why + get owner approval.

69. **Comprehensive test pyramid before every code push (Pass 53 owner directive 2026-05-05; DEC-503 HARD RULE).**
    Every code push (new feature / bug fix / refactor / schema change / data-source migration) must execute and pass ALL applicable test types:

    - **Unit** — individual function correctness with mocked dependencies
    - **Smoke** — basic happy-path verification on real data (≤30s)
    - **Integration** — module-to-module data flow (e.g., fetcher → cache → signals → screener)
    - **System** — end-to-end workflow (full prefetch → universe load → backtest → report)
    - **Functional** — feature behavior matches spec
    - **Regression** — full `backtest/tests/test_unit.py` + `backtest/tests/test_integration.py` (all tests must pass; current count ~102 and grows over time — run `pytest -q` to verify; see [CANONICAL_FACTS.md F-007](CANONICAL_FACTS.md))
    - **Data integrity** — schema validation, PIT semantics, completeness gates
    - **Performance / load** — for prefetch + heavy-data code (rate-limit handling, memory bounds, wall-time budgets)
    - **Acceptance** — owner-defined pass criteria for the specific change

    **Trigger:** ANY code push — including doc-only repos that touch executable scripts. Includes Sprint 0A and beyond.

    **Partial coverage non-compliant.** "Just unit tests" or "just smoke + integration" does NOT satisfy this rule. If a test type doesn't apply to a specific change (e.g., performance tests for a typo fix), the pre-flight block must explicitly mark that test type N/A with reason — silent skipping is non-compliant.

    **Past failure pattern (motivating rule):** Silent-gap finding (BUG-271/272/273 — `smart_money.py` has been silently broken for 3 of 4 Quiver endpoints across all Phase 1A v3 archive results) went undetected because tests focused on `congresstrading` (which works) and skipped `insidertrading` + `institutionalholdings` + `analystestimates` (which silently 404). Owner directive 2026-05-05: "we will need to do unit tests, smoketests, integration Testing, system testing, all types of regression testing, functional testing, etc. Just dont do a few limited tests." Comprehensive coverage would have caught this. Codified as DEC-503 + this checklist item.

    **Verification format in pre-flight:** for any code push, state explicitly: "Test pyramid coverage: Unit ✅ / Smoke ✅ / Integration ✅ / System ✅ / Functional ✅ / Regression ✅ (36/36) / Data integrity ✅ / Performance N/A (typo fix; no perf surface change) / Acceptance ✅ (owner-defined: <criteria>)." Each line shows actual status; N/A items state reason.

    **First application:** smart_money silent-gap fix (BUG-271/272/273) next turn — full test pyramid required before commit.

    **Joint:** DEC-097 (90% test coverage minimum), DEC-098 (hot-path 100% coverage), DEC-503 (this rule's parent decision), L145 (silent-gap lesson).

70. **Agent toolkit wiring matrix HARD RULE (Pass 53 owner directive 2026-05-05; DEC-507; L146).**
    Pre-Phase-1B (or any agent-using phase entry), maintain explicit `Agent × Data source × Code path × Verified status` matrix in `TRADINGAGENTS_DATA_AUDIT.md`. Each row must be ✅ before phase begins.

    **Trigger:** Pre-entry to any phase that activates new agent capabilities (Phase 1B agents-on, Phase 1C+ expanded agents, Phase 1B-α run kickoff).

    **Required matrix columns:**
    - Agent name (Technical / News Analyst / Fundamental / Risk / Sentiment / Bull / Bear / Research Manager / Trader / Risk Debaters / Portfolio Manager)
    - Toolkit (DEC-462-466 + others)
    - Data source path (e.g. `data_prefetch/polygon/news/<TICKER>.parquet`)
    - Code path (e.g. `smart_money.get_news_sentiment` or `OurNewsToolkit.fetch`)
    - Verified status (✅ end-to-end traced + tested / ⚠ partial / 🔴 not wired)

    **Past failure pattern (motivating rule):** Owner Q Pass 53 turn 2026-05-05 surfaced: 1.05M Polygon news articles cached (Batch 3 done) but `smart_money.get_news_sentiment` reads legacy `cache/av_news/` + `cache/finnhub_news/` paths. Data DEC (DEC-440) and toolkit DEC (DEC-464) were each approved independently without an integration deliverable. Result: data sat unused. Same shape as L145 silent-gap but on wiring axis. L146 codifies the lesson; this checklist item is the systematic prevention.

    **Verification format in pre-flight:** before any agent-using-phase entry (or in any pre-flight that touches agent input data), state explicitly: "Wiring matrix: Technical ✅ / News ⚠ (DEC-440 cached, DEC-464 toolkit pending wiring) / Fundamental 🔴 / Risk ⚠ (7/50 FRED wired) / Sentiment ⚠ (AAII/CNN F&G ✅; rest pending) / Bull-Bear 🔴 / Portfolio Manager 🔴." Each row shows actual status; ⚠/🔴 items state remaining work.

    **First application:** Batch 13 NO-LIVE-API refactor — wiring matrix updated to ✅ for all rows before Phase 1B-α run begins.

    **Joint:** DEC-507 (this rule's parent decision), L146 (data-DEC + toolkit-DEC ≠ integration lesson), L145 (silent-gap pattern; complementary), DEC-462-466 (custom toolkit DECs that this matrix tracks), CHECKLIST #69 (test pyramid; complementary — pyramid validates code, this validates wiring exists).

71. **External library fork integration mandate — 15-category test plan + 3-phase A/B/C gate (Pass 53 owner directive 2026-05-05; DEC-508; L147).**
    Any external library forked under DEC-045 (or future fork-first decisions) must complete the 15-category test plan + 3-phase A/B/C gate before strategies consume its signals.

    **15-category test plan (4 tiers):**

    **Tier 1 — Correctness (must-pass before merge):**
    - Unit tests on synthetic OHLCV (~50-100 tests covering each primitive)
    - Canonical pattern fixtures (textbook bullish/bearish patterns with known signals)
    - **PIT correctness regression** 🔴 CRITICAL (freezegun: signal at bar D MUST be identical whether computed at as_of=D vs as_of=D+50)
    - Edge case handling (empty / single bar / all-NaN / weekend / IPO short history)
    - Library version pin + reproducibility (upstream commit hash + fork commit hash recorded)

    **Tier 2 — Integration (must-pass before strategy enable):**
    - Cache pipeline integration (OHLCV cache → library → signal output → consumer)
    - Cross-primitive composition (multiple primitives compose without interference)
    - Survivorship + corporate actions (delisted tickers; splits/dividends adjust correctly)
    - Performance / load (per-ticker runtime + memory acceptable for full-universe backtest)

    **Tier 3 — Empirical validation (must-pass before backtest):**
    - Statistical sanity (signal frequency per ticker per month within reasonable bounds)
    - Adversarial random-walk test (library on Brownian motion ~ baseline signal rate, not pattern-matching noise)
    - Cross-validation against known source (TradingView ICT script comparison or equivalent)
    - Signal lookahead detection (>65% win rate triggers re-validation per DEC-084)

    **Tier 4 — Visual + manual validation:**
    - Dashboard 2 visual inspector (DEC-200 5-section spec; signals overlaid on candlestick charts)
    - Owner manual spot-check (~20-30 signals reviewed on real charts)

    **3-Phase A/B/C gate:**

    **Phase A — PRE-MERGE** (library in `vendored/`, NOT in main):
    - All Tier 1 + Tier 2 + Tier 3 tests pass
    - ≥90% line coverage on library wrapper code
    - Library NOT imported outside test files
    - Owner review + approval → Phase B

    **Phase B — CANARY** (library imported, strategies disabled):
    - Signals computed for full universe → `data_prefetch/<library>/{ticker}.parquet`
    - Dashboard 2 launched; owner manually validates 20-50 signals
    - Statistical sanity report (frequency distribution, signal density per regime)
    - PIT regression on full universe
    - Owner review + approval → Phase C

    **Phase C — PRODUCTION** (strategies enabled):
    - Strategies that consume library signals enabled
    - Backtest run; A/B vs baseline (without library) comparison
    - DEC-084 red-flag check (>65% win rate = lookahead suspect)
    - Walk-forward validation per DEC-505 (4 OOS folds × 1y)
    - Each phase has explicit owner-approval gate

    **Trigger:** Any new external library fork via DEC-045 (or descendant DECs).

    **Verification format in pre-flight:** state explicitly "Library fork status: Phase A tests X/Y passing / Phase B canary signals validated / Phase C strategies enabled, A/B vs baseline = ..." If skipping any phase, surface why + get owner approval (NO skipping unless explicit override).

    **Past failure pattern (motivating rule):** Pass 53 turn 2026-05-05 owner Q "We need extensive testing of smartmoneyconcepts library fork before we integrate into main. how do we test extensively?" surfaced gap: existing project plan referenced smartmoneyconcepts fork (DEC-045) and Dashboard 2 (DEC-200) but had no codified test protocol or phased gate. ICT/SMC signals are pattern-based with subjective ground truth, lookahead-bias-prone, and noise-pattern-matching-prone — high-risk integration without explicit testing mandate.

    **First application:** smartmoneyconcepts library Phase A testing kicks off Pass 53 (per Q2 owner directive: "start phase A testing now").

    **Pattern reusable:** future external library forks (TradingAgents v0.2.4 if extended, QuantStats if extended, future ICT/options libraries) follow same protocol.

    **Joint:** DEC-508 (this rule's parent decision), DEC-045 (fork-first parent), DEC-200 (Dashboard 2; visual validation in Tier 4), DEC-261 (PIT N+1 lag; tested in Tier 1 PIT regression), DEC-084 (>65% win rate red flag; in Tier 3 + Phase C), DEC-503 (test pyramid; Tier 1-3 USE pyramid layers — complementary), DEC-505 (walk-forward Phase C), DEC-507 (wiring matrix; complementary process control), L147 (external library fork integration risk; this checklist codifies the lesson).

72. **Data-integrity test scan of cache MUST run + pass before any DEC marks RESOLVED-IMPLEMENTED OR before any phase entry (Pass 53 owner directive 2026-05-06 evening; DEC-591; L148; HARD RULE).**

    **Rule:** A 7-test minimum data-integrity scan of the live cache (not mocked fixtures) is mandatory before any DEC marks RESOLVED-IMPLEMENTED OR before any phase entry. The suite extends as new data sources are added. No code push that touches prefetched data is compliant without running this suite.

    **The 7 minimum tests (`backtest/tests/test_data_integrity.py`):**

    | # | Test | Asserts | Catches |
    |---|---|---|---|
    | 1 | OHLCV schema consistency | All OHLCV files share single schema | Schema split (Pass 53 C1) |
    | 2 | OHLCV freshness | All OHLCV last_bar ≥ as_of − 7 days OR ticker-delisted-tagged | Stale files (Pass 53 C2) |
    | 3 | Required tickers present | VIX/VIXCLS, SPY, sector ETFs (XLB-XLY+XLC) | Missing canonical tickers (Pass 53 C3+M6) |
    | 4 | Numeric dtype | CFTC, FRED, financials numeric cols are float64 | String-dtype bugs (Pass 53 C4) |
    | 5 | Tier params populated | TIER_PARAMS dict has all 5 keys per tier (T1a/T1c/T1ETF/T2/T3) | Empty params (Pass 53 C5) |
    | 6 | Cross-source ticker coverage | Each source ≥75% of universe (or explicit "delisted" tagged) | Quiver legacy paths (Pass 53 H5) |
    | 7 | Cumulative-snapshot history | Apewisdom/AAII/CNN F&G have multi-day history (≥30d minimum) | Single-day caches (Pass 53 H3) |

    **Gate behavior:**

    - Test suite runs as part of `pytest backtest/tests/` standard regression
    - Failed test BLOCKS phase entry, BLOCKS DEC RESOLVED-IMPLEMENTED marking, BLOCKS commit-with-skip-tests
    - Suite extends as new data sources added (one new test per source per gap pattern)
    - HARD RULE: no skipping; no `pytest.skip` annotations; no "we'll fix it later"

    **Past failure pattern (motivating rule):** Pass 53 prefetch audit 2026-05-06 surfaced 5 of 5 CRITICAL findings + 7 HIGH findings, all of which existed in cache for weeks/months without detection. Existing 102-test unit + integration suite passed 100%. DEC-503 specified 9 test types but only code-test layers (1-6) were implemented; data-integrity layer (7) was specified-but-not-built. Same silent-gap pattern as L145/L146/L147 but on the VERIFICATION axis.

    **First application:** Pass 53 evening 2026-05-06 — data-integrity test suite implementation as remediation of audit findings; PASS-gate for DEC-590 May 15 Phase 1A start.

    **Joint:** DEC-591 (this rule's parent decision), DEC-503 (test pyramid; this DEC implements specified-but-unimplemented type #7 — complementary), DEC-507 (wiring matrix; complementary process control), DEC-590 (9-day window provides time pre-Phase-1A), CHECKLIST #69 (test pyramid before every code push) + this #72, L148 (test pyramid layered failure mode; this checklist codifies the lesson).

73. **Test-Artifact Same-Commit + Stage/Phase Gate Executable Tests (Pass 53 owner-approved 2026-05-06 late evening; DEC-594 + DEC-595; L148 + L149; HARD RULE).**

    **Rule (a) — Test-Artifact Same-Commit (DEC-594):** Every DEC that specifies a test layer / validation gate / acceptance criterion / pass criterion MUST include the executable test code (Python, pytest, CI workflow, gate script) in the SAME commit as the DEC text. A DEC cannot mark RESOLVED-DECIDED if any specified test/gate is "to be implemented later." Status taxonomy adds `PARTIAL-SPEC-ONLY` (NEW) for spec-final + artifact-pending state.

    **Rule (b) — Stage/Phase Gate Executable Tests (DEC-595):** Every transition between stages, phases, sprints, or sub-phases MUST have an executable gate test in `backtest/tests/test_gates.py` asserting entry/exit criteria. No transition without preceding gate test PASS.

    **Trigger words for DEC-594 enforcement (pre-flight CHECKLIST #1 scan):**

    `test`, `validate`, `verify`, `verified`, `gate`, `acceptance criterion`, `pass criterion`, `must pass`, `before X`, `before phase entry`, `before commit`, `before run`, `before merge`, `before scale`. If ANY appear in a DEC body, the DEC MUST reference the corresponding executable artifact (file path) and that artifact MUST exist in the same commit.

    **Initial gates (extends as new transitions defined; per DEC-595):**

    | # | Gate | Asserts | Trigger |
    |---|---|---|---|
    | 1 | `test_gate_pre_phase_1a_entry` | data-integrity 7/7 + universe build verified + smoke run on 5 tickers + DEC-505 4-fold config valid | Before May 15 Phase 1A start (DEC-590) |
    | 2 | `test_gate_post_phase_1a_alpha` | rules-only Sharpe ≥ 0.7 OOS | Before $300 1B-α budget commit |
    | 3 | `test_gate_pre_phase_1b_alpha_run` | DEC-507 wiring matrix all ✅ + DEC-508 Tier 1-3 fork tests pass + budget tracker armed + Anthropic API headroom | Before Phase 1B-α run (Sprint 9) |
    | 4 | `test_gate_post_phase_1b_alpha_verdict` | DEC-578 7-gate ≥1 PASS cell + DSR + walk-forward 4 OOS folds (DEC-505) | Before Stage 3 entry |
    | 5 | `test_gate_pre_stage_3_entry` | Phase 1B-α verdict produced + paper-trading infra ready + 3-month plan (DEC-028) | Before Stage 2 → 3 |
    | 6 | `test_gate_pre_stage_4_entry` | 3-month paper-trading audit pass + email approval pipeline + capital pre-funded | Before Stage 3 → 4 |

    **Retroactive audit obligation:**

    All 353 existing DECs in [AUDIT_INDEX.md](AUDIT_INDEX.md) MUST be scanned for spec-without-build patterns within Day 2-3 of DEC-590 9-day window. Findings logged to [AUDIT_BACKLOG.md](AUDIT_BACKLOG.md). Each remediated by either: (a) building executable artifact in same commit; OR (b) demoting to `PARTIAL-SPEC-ONLY` status with explicit dependency-on-artifact note.

    **Gate behavior:**

    - Each gate is a `pytest` function asserting executable conditions (boolean checks on cache state, file existence, metric thresholds)
    - Failed gate BLOCKS transition; surfaces actionable error message
    - Gate test file is part of standard `pytest backtest/tests/` regression
    - New transitions defined → new gate added in same commit (per #73a)

    **Verification format in pre-flight:**

    State explicitly: "DEC-594 compliance: [DEC body has X trigger words; artifact at <path>; same-commit verified ✅]" OR "[no trigger words; #594 N/A]". For phase-transition recommendations: "Gate `test_gate_<name>` PASS verified (or SKIPPED with reason: ...)".

    **Past failure pattern (motivating rule):**

    DEC-503 (Pass 52 turn 132): codified 9-type test pyramid; layer 7 (data integrity) specified but unbuilt for ~6 weeks; Pass 53 audit 2026-05-06 surfaced 5 CRITICAL findings layer 7 would have caught at codification time. Same pattern caused L86 ($50 lost), L95 ($100 lost), $300 Phase 1B failed run, 7 Pass 53 audit cycles. Discipline alone insufficient; structural mechanism required.

    **First application:** Pass 53 late evening 2026-05-06 — DEC-594/595 commit lands with `backtest/tests/test_gates.py` (6 gates) + `scripts/audit_decs_for_artifacts.py` (retroactive audit) in same commit.

    **Joint:** DEC-594 + DEC-595 (this rule's parent decisions), DEC-503 (test pyramid; this rule enforces artifact layer), DEC-591 + CHECKLIST #72 (data-integrity test; first compliant DEC under #594), DEC-507/508 (asserted in gates #3/#4), DEC-590 (Phase 1A entry uses gate #1), L148 (test pyramid layered failure mode) + L149 (this turn — spec-without-build codification), L86 + L95 ($150 + $300 prior losses from same pattern).

74. **HARD RULE — Every flag/observation MUST be logged to [OPEN_INVESTIGATIONS.md](OPEN_INVESTIGATIONS.md) in the same commit it is surfaced** (Pass 53 Day-9 v8h owner directive 2026-05-07).

    **The pattern this rule fixes:**

    Owner 2026-05-07: *"Q1 rec should have been flagged and recommended by you. Thats literally your job. This is exactly what has gone wrong and i needed to do so many audit passes. We keep finding issues but we cant resolve if we cant even track them. Heavily increases iterations."*

    Throughout Pass 53, observations like "trade-level regime=100% neutral", "ETF holdings has no PIT dimension", "Quiver wikipedia mirror is empty" were buried in AUDIT.md narratives or commit messages — easy to miss, impossible to enumerate. The result: same issues re-discovered by repeated audit cycles. Owner had to ask "where can i check the list of such flags" and the honest answer was "nowhere canonical."

    **The rule:**

    - When an observation surfaces during work that is NOT a bug (→ `BUG_REGISTER.md`) and NOT a deferred spec (→ `AUDIT_BACKLOG.md`), it MUST be logged to `OPEN_INVESTIGATIONS.md` as `INV-NNN` in the **same commit** as the work that surfaced it.
    - Format: `INV-NNN — short title` + Discovered (date+commit+how-caught) + Observation + Why-not-blocking + Status (open/in-progress/resolved/wontfix) + Next-action.
    - Pre-flight verification: when surfacing a flag in any response, state explicitly "logging as INV-NNN in same commit" or explain why it falls under BUG/BACKLOG instead.
    - End-of-response check: if any flag was raised in the turn but not committed, the response is non-compliant.

    **Why this is structural, not just discipline:**

    Same logic as DEC-594/L149 spec-without-build — discipline alone failed. The mechanism (single canonical doc + same-commit rule + pre-flight verification) makes the failure mode impossible to silently repeat. INV-NNN entries are auditable; "vibes-based flagging" in narratives is not.

    **First application:** Pass 53 Day-9 v8h commit `c0a3a568` — created `OPEN_INVESTIGATIONS.md` with 8 INV entries retroactively documenting flags raised across this session.

    **Joint:** DEC-594/595 (same-commit pattern); CHECKLIST #11 (proactive flagging is the trigger; #74 is the persistence layer); L149 (sister rule for spec-without-build); L150 (sister rule for pyramid dimension-coverage gap); INV-001..INV-008 (initial entries).

75. **HARD RULE — FULL PYRAMID TESTING FOR EVERY DECISION IMPLEMENTATION, BUG RESOLUTION, AND ACTION** (Pass 53 Day-9 v8h owner directive 2026-05-07).

    **Owner directive verbatim:**

    *"MANDATORY REQUIREMENT: FULL PYRAMID TESTING FOR EVERY DECISION IMPLEMENTATION, BUG RESOLUTION, EVERY ACTION! THIS IS NON NEGOTIABLE AND MUST BE DONE! NO EXCEPTIONS, NO SKIP UNDER ANY SITUATION."*

    **The rule:**

    Every commit that contains code changes (not pure-doc / pure-data commits) MUST run the **full mandatory pyramid** before push. The "mandatory pyramid" is the test suite excluding only the slow-tier `test_e2e_phase1a_smoke.py` + `test_performance_load.py` (which require cache + are gated to CI). All other tests run.

    Standard invocation:

    ```bash
    python -m pytest backtest/tests/ -q --tb=line \
      --ignore=backtest/tests/test_e2e_phase1a_smoke.py \
      --ignore=backtest/tests/test_performance_load.py
    ```

    Pre-push gate: zero failures (xfail + skip permitted with documented reasons; failures HALT push).

    **Why this is structural, not just discipline:**

    Owner ($300 Phase 1B failed run + 7 audit cycles + repeated downstream-bug pattern) has paid the cost when partial testing missed regressions. Same logic as DEC-594/L149 spec-without-build — discipline alone failed. The mechanism (fail-loud, run-or-block) makes the failure mode impossible to silently skip.

    **Pre-flight verification:** when proposing or executing a code change, state explicitly: "Mandatory pyramid: X PASS / 0 FAIL post-change" (or "pre-change baseline + post-change: same Δ").

    **End-of-turn check:** if any commit contained code changes and the pyramid was NOT run + reported, the response is non-compliant.

    **Caveats / exclusions (HARD-LIMITED):**

    - **NO doc-commit carve-out, NO data-commit carve-out** (Pass 53 Day-9 v8h owner correction 2026-05-07 evening: *"Test pyramid is not optional FYI"*). Prior wording softened the original directive's "NO EXCEPTIONS, NO SKIP UNDER ANY SITUATION" into per-category opt-outs — that softening IS the failure mode the rule exists to prevent. Every commit (code, doc, data, mixed) runs the mandatory pyramid before push.
    - **Long-running additions** (e.g. `test_e2e_phase1a_smoke.py` 7-min run) — invoked on CI per `.github/workflows/test-pyramid.yml`; NOT skippable from full pyramid mandate but allowed to run in CI rather than locally. CI gating is about WHERE the test runs, not WHETHER.

    **Past failure pattern motivating this rule:**

    Pass 53 Day-9 v8h, my CFTC re-prefetch saved numeric columns as strings — caught by `test_data_integrity_4_numeric_dtype_cftc_fred` only because the existing pyramid was run. Without #75 enforcement, I might have shipped the data fix without running tests; the bug would have propagated to Phase 1A consumers (rolling-mean / sum-aggregation operations would silently fail). The fix landed in same commit BECAUSE the pyramid ran.

    **First application:** Pass 53 Day-9 v8h P1 batch onwards.

    **Joint:** DEC-503 (9-type pyramid); DEC-594/595 (same-commit); CHECKLIST #69 (pre-push pyramid; #75 is the strict-enforcement upgrade); CHECKLIST #72 (data-integrity); CHECKLIST #74 (flag tracker — sister persistence rule). L86 + L95 + $300 Phase 1B prior-loss pattern (same root cause: partial verification ships bugs).

76. **HARD RULE — Comprehensive audits MUST include functional verification + recommended-action escalation, not just inventory** (Pass 53 Day-9 v8h owner directive 2026-05-07 evening).

    **Owner trigger:** *"When i earlier asked you to do a comprehensive check on pre-fetch data, why werrent these issues caught?"* — pointing out that PREFETCH_COVERAGE_AUDIT.md (commit `c0a3a568`) was a paper audit (file counts, dimension lists, status fields) that missed run-time bugs (Quiver Unicode print crash, Polygon news schema drift, CFTC numeric-as-string, CFTC Treasury contract-name typos, VVIX missing on FRED, Quiver B5-B10 endpoints 404, Wikipedia checkpoint ghost) AND failed to escalate the 26.3% Quiver per-ticker red flag from "informational categorization" to "Phase 1A blocker — re-prefetch required."

    **The rule — every comprehensive audit has THREE mandatory columns per row:**

    | Column | Required content |
    |---|---|
    | **(a) Observation** | The static fact (file count / coverage % / endpoint presence / schema field) — what existing audits already captured |
    | **(b) Functional-verification step run** | Concrete command executed AT AUDIT TIME (e.g. `python scripts/prefetch_X.py --tickers AAPL` smoke; `pytest backtest/tests/test_data_integrity_*` for the audited cache; `head data_prefetch/X/*.parquet` schema check; `diff <(jq keys _checkpoint.json) <(ls dir/)` for checkpoint↔fs cross-check). If NOT run, must be explicitly stated as "NOT RUN — paper audit only" — silent omission is non-compliant. |
    | **(c) Recommended action + priority + blocker-status** | Specific next-step proposal: action verb + scope + estimated effort + priority (P0/P1/P2) + explicit phase-blocker classification ("BLOCKER for Phase 1A" / "BLOCKER for Phase 1B-α" / "non-blocking — Sprint 5 work" / "informational"). Surfacing a red flag in the matrix without a column-(c) recommendation is non-compliant. |

    **Mandatory cross-checks for every prefetch / cache audit:**

    1. **Filesystem ↔ checkpoint diff** — for any prefetch with a checkpoint JSON, compare keys against actual `ls dir/` to surface ghost entries (caught INV-013 retroactively; should have been caught at audit time).
    2. **Smoke run of every audited script** — at least one ticker / endpoint per script. Catches Unicode bugs, encoding issues, API auth changes, schema drift, dtype bugs.
    3. **Pyramid scan over consumer code paths** — `pytest -q` filtered to tests touching the audited data source. Catches schema-evolution bugs (Polygon `tickers`→`all_tickers`).
    4. **API endpoint discovery probe** — for "MISSING endpoints" rows (e.g. Quiver B5-B10), GET each endpoint with one ticker to validate it exists at the current API plan tier BEFORE adding it to the recommendation list. Avoids INV-012-class wasted recommendations.

    **Pre-flight verification format for every row in a comprehensive audit:**

    ```
    Row: <data source> / <endpoint> / <coverage>
    (a) Observation: <static fact>
    (b) Functional-verification: <command run + result OR "NOT RUN — reason">
    (c) Recommendation: <action> | priority: P{0|1|2} | blocker-status: {Phase 1A | Phase 1B | Sprint 5 | informational}
    ```

    **Why this is structural, not just discipline:**

    L146/DEC-507 codified the lesson that "data DEC + toolkit DEC ≠ integration; wiring is a third explicit deliverable." #76 is the audit-side counterpart: "inventory + dimension list ≠ remediation plan; functional-verification + escalation are two more explicit deliverables." Same root pattern: I treated "list everything I see" as the deliverable when the actual deliverable is "list everything that blocks the next gate AND propose how to close each." Categorization-only audits ship the appearance of completeness without the substance — owner has to do the second-level translation work that the audit should have done.

    **Past failure pattern motivating this rule:**

    Pass 53 Day-9 v8h `c0a3a568` PREFETCH_COVERAGE_AUDIT.md missed:
    - Quiver Unicode print crash (run-time only — would have surfaced if smoke step was run, column-(b) gap)
    - Polygon news schema drift `tickers`→`all_tickers` (consumer-test only — column-(b) gap)
    - CFTC numeric-as-string + CFTC Treasury contract names + VVIX missing + Quiver B5-B10 404 (all run-time only — column-(b) gap)
    - Wikipedia checkpoint ghost (filesystem↔checkpoint diff missing — column-(b) gap)
    - Quiver per-ticker 26.3% — flagged in matrix but NOT escalated as blocker; owner had to escalate it (column-(c) gap, owner pushback: *"Q1 rec should have been flagged and recommended by you. Thats literally your job."*)
    - Production runner Unicode bug — out of audit scope, but extends pattern: any audit narrowly scoped to "prefetch" misses adjacent code that consumes the prefetch.

    **Pre-flight verification:** when authoring or extending an audit doc, state explicitly: "Audit functional-verification: smoke + pyramid + checkpoint diff + endpoint probe — RUN AT AUDIT TIME" (or "audit is paper-only — column-(b) marked NOT RUN throughout, NOT phase-gate suitable").

    **End-of-turn check:** if a comprehensive audit was authored or updated and (a)/(b)/(c) coverage is incomplete in any row, the response is non-compliant.

    **Caveats / exclusions:**

    - **Quick spot-check audits** (single ticker / single endpoint diagnostic) — not subject to #76. Comprehensive = audits across multiple data sources / endpoints / forms intended to inform Phase / Sprint gating decisions.
    - **Audits authored before 2026-05-07** — not retroactively non-compliant, but if relied upon for current decisions, must be retrofitted with column (b) and (c) before phase-gating use.

    **First application:** Pass 53 Day-9 v8h evening — retrofit of PREFETCH_COVERAGE_AUDIT.md with columns (b) and (c) per this rule (this commit).

    **Joint:** L146/DEC-507 (data + toolkit + wiring three deliverables — #76 is the audit-side counterpart); CHECKLIST #44 (data-consumption audit must include runtime probe — #76 generalizes this to ALL audits, not just data-consumption); CHECKLIST #74 (flag tracker — column (c) recommendations that don't make it into the same commit must spawn an INV-NNN entry); CHECKLIST #75 (pyramid testing — #76 mandates the pyramid scan column-(b) for any audit touching cache); INV-001..INV-013 (the gaps that would have been surfaced earlier had #76 been in force).

77. **HARD RULE — API endpoint catalogs MUST be sourced from canonical API documentation (or live API probe), never from training-data memory** (Pass 53 Day-9 v8h+1 owner directive 2026-05-07 evening; codified after 3 prefetch-coverage audit passes that all worked from memory and missed the same gaps).

    **Owner trigger:** *"This is horrible performance. I specifically said I want ALL available data downloaded. You have done 3 passes on this already and yet this was still missed... Despite multiple L146-style silent gap analysis passes, its still incomplete and these things are not even being flagged."* + (next turn): *"Do not work from memory but rather documentation."*

    **The rule:**

    Every API audit (endpoint listing, gap analysis, coverage matrix, field-level audit) MUST source its endpoint catalog from one of:

    1. **Canonical API documentation page** fetched at audit time (WebFetch a stable URL — `polygon.io/docs/...`, `api.stlouisfed.org/docs/api/`, official `llms.txt` files where available)
    2. **Live API probe** with our actual API key (`probe_api_catalog.py` pattern — hit each endpoint with one test call, capture HTTP status + sample response schema)
    3. **Both**, where docs are blocked (403/404) or ambiguous about plan tier — probe is the more authoritative path because it directly verifies tier access

    Training-data memory is NOT acceptable as the catalog source. If memory is the only available source, the audit must explicitly disclose: *"Catalog sourced from training data — NOT phase-gate-suitable. Re-probe required before phase entry."* Silent reliance on memory is non-compliant.

    **Pre-flight verification format for every API audit:**

    ```
    Source for endpoint catalog: <docs URL fetched at HH:MM> + <probe script run at HH:MM>
    Probe report: <path/to/PROBE_REPORT.json>
    Endpoints in catalog: N (M ✅ probe-confirmed, K 🔴, L ❓ deferred)
    ```

    **Why this is structural, not just discipline:**

    Three consecutive audits in Pass 53 Day-9 v8h:
    - Pass 1 (commit `c0a3a568`): paper audit — endpoint list from training data
    - Pass 2 (commit `2fb228ed5`): retrospective enrichment per #76 — applied to existing rows but didn't expand catalog
    - Pass 3 (commit `212018194`): field-level deep-dive — schema-probed parquets but didn't enumerate API catalog from canonical source

    Each pass found NEW gaps not surfaced by prior passes — the catalog kept growing because each pass was a different lens on the same memory-based starting set. The 4th pass (Pass 53 Day-9 v8h+1, this commit) is the first to ground every endpoint claim in either canonical docs or live probe; surfaced 30+ new findings (Polygon Indices Basic NOT activated, Finnhub key missing, 13 Quiver endpoints don't exist at our tier, SEC EDGAR XBRL solves INV-025/026 partially, Polygon Benzinga is in our tier).

    Owner has paid in 4 audit cycles for the lack of this rule. Memory-based catalogs are the failure mode — make it impossible to silently rely on memory.

    **Past failure pattern motivating this rule:**

    L131 honest-knowledge-limit disclaimer was already in `API_AUDIT.md` Tier 1 framework, BUT was not enforced — I authored 3 passes of audits that ignored that disclaimer. #77 is the enforceable upgrade: every audit's pre-flight must specify the canonical source URL or probe script reference; without it, the audit is non-compliant.

    **Pre-flight verification:** when authoring or extending an API audit, state explicitly: *"Catalog source: <URL fetched HH:MM> + <probe.py run HH:MM>"* (or *"NOT-VERIFIED — paper audit from memory; not phase-gate-suitable"*).

    **End-of-turn check:** if an API audit doc was authored or modified and the source attribution is missing, the response is non-compliant.

    **Caveats / exclusions:**

    - **Quick spot-check (single endpoint, single ticker)** — not subject to #77.
    - **Audits authored before 2026-05-07** — flagged as memory-based; require re-probe before phase-gating use.

    **First application:** Pass 53 Day-9 v8h+1 commit (this one) — `API_ENDPOINT_INVENTORY.md` sourced from `massive.com/docs/llms.txt` + `alphavantage.co/documentation/` + `publicreporting.cftc.gov/` + `apewisdom.io/api/` + `pytrends` GitHub README + `scripts/probe_api_catalog.py` live probe @ 2026-05-08. Probe report: `API_ENDPOINT_PROBE_REPORT.json`.

    **Joint:** CHECKLIST #76 (column-b runtime probe — #77 is the tighter "where does the catalog come from" rule); CHECKLIST #51 (honest knowledge limit disclaimer); L146/DEC-507 (data + toolkit + wiring); INV-024 reframing (Quiver govcontracts gap turned out to be at API level, not prefetch — a memory-based audit got the assumption wrong); INV-035..INV-037 (this commit's new INV flags: Indices Basic not activated, Finnhub key missing, 13 Quiver paths 404).

78. **HARD RULE — Test pyramid runs PER ADDRESSAL, not bundled** (Pass 53 Day-9 v8h+1 owner directive 2026-05-08).

    **Owner trigger:** *"Testing pyramid is for each addressal but not the bundle! If not applicable, then skip. But needs to go through the pyramid."*

    **The rule:**

    For every individual addressal (one INV resolution, one BUG fix, one DEC implementation, one code patch, one prefetch script change), the applicable pyramid layers MUST be run for THAT addressal in isolation BEFORE moving to the next addressal. Bundling N addressals and running pyramid once at the end is non-compliant.

    **For each addressal, declare per-layer status explicitly:**

    | Layer | Decision rule |
    |---|---|
    | unit | Run unless addressal is doc-only (no code touched) |
    | smoke | Run if any prefetch / dashboard / runner script touched |
    | integration | Run if any cross-module call path touched |
    | system | Run if Phase 1A entry path touched |
    | functional | Run if doc/parser/dashboard touched |
    | regression | ALWAYS run if a BUG was claimed RESOLVED (the BUG-NN test must exist) |
    | data_integrity | Run if any cache schema touched |
    | performance | Run if hot-path code touched |
    | acceptance | Run if PASSING_CRITERIA / 9-criteria touched |
    | property | Run if invariant-bearing code touched (regime classifier, profit_factor, etc.) |
    | snapshot | Run if dashboard data shape OR golden fixture touched |
    | contract | Run if API parser touched |
    | compatibility | Run if pandas/numpy/pyarrow API surface touched |

    **N/A is acceptable but must be DECLARED.** A doc-only INV resolution with zero code change can declare "pyramid: skip — doc-only change, no test layer applicable" and move on. Silently skipping without the declaration is non-compliant.

    **Why per-addressal:** bundling masks which addressal broke what. If 6 addressals share a pyramid run and one regression fires, attribution requires manual bisection. Per-addressal isolation makes the cause visible at the addressal level.

    **Doc-sweep can still bundle.** End-of-turn doc-sweep (CHECKLIST #67) is correctly batched. The PYRAMID is the per-addressal step; the DOC SWEEP is the end-of-turn step. Different cadences.

    **Pre-flight verification format (per addressal):**

    ```
    Addressal: <ID> (e.g. BUG-007 / INV-016 / DEC-422)
    Files touched: <list>
    Pyramid layers run:
      unit: <PASS N/M | SKIP reason>
      smoke: ...
      [...all 13 layers]
    ```

    **End-of-turn check:** if N addressals are claimed in one turn and the pyramid was run only once, the response is non-compliant.

    **First application:** retroactive — Pass 53 v8h+1 T0 triage (commit `7a175f7c2` bundled 6 addressals; this rule codifies per-addressal going forward).

    **Joint:** CHECKLIST #75 (pyramid mandatory for every commit — #78 tightens to per-addressal granularity); CHECKLIST #67 (doc-sweep at end-of-turn — different cadence from pyramid).

79. **HARD RULE — End-of-turn doc sweep covers ALL forward-looking documents (cross-references can come from any of them)** (Pass 53 Day-9 v8h+1 owner directive 2026-05-08).

    **Owner trigger:** *"All documents need to be addressed. There are dependencies and references in all documents for all addressal types. In your list you will definitely miss cross addressals."*

    **The rule:**

    Don't try to enumerate "for a BUG fix update X, Y, Z; for an INV update A, B, C." Cross-addressals always span types — an INV that exposed a BUG that resolved a DEC that needs a CAV that updates a CHECKLIST rule. **Just sweep ALL forward-looking documents at end-of-turn and update wherever the change is referenced.**

    **The complete sweep set (all checked on every meaningful turn):**

    AUDIT.md, AUDIT_INDEX.md, BUG_REGISTER.md, OPEN_INVESTIGATIONS.md,
    LIMITATIONS_CAVEATS_ASSUMPTIONS.md, CHECKLIST.md, LEARNINGS.md,
    PHASE_1A_PRELAUNCH_TODO.md, ENGINEERING_REGISTER.md, AUDIT_BACKLOG.md,
    CANONICAL_FACTS.md, README.md, DETAILED_PROJECT_PLAN.md,
    API_ENDPOINT_INVENTORY.md, PREFETCH_COVERAGE_AUDIT.md, MEMORY.md.
    Plus dashboards: `dashboard_stage_2/` (auto-updates all tabs) and
    `dashboard_sprint0a/` (API endpoint coverage).

    **Caveats / exclusions:**

    - `archive/**` is excluded (per L143).
    - Pass-specific snapshot docs are not part of the sweep set.
    - "Be careful — don't create downstream code/project issues while
      doc-sweeping." A doc update that requires a new code file or
      data migration is itself a separate addressal subject to #78.

    **End-of-turn check:** if any change with cross-doc impact is made and
    one of the sweep-set docs is stale relative to that change, the
    response is non-compliant.

    **First application:** Pass 53 v8h+1 retroactive doc sweep (this commit).

    **Joint:** CHECKLIST #67 (per-turn doc sync sweep — #79 enumerates the complete set explicitly); CHECKLIST #78 (per-addressal pyramid — #79 is the doc-side counterpart, can bundle at end-of-turn).

80. **HARD RULE — Coverage analyses MUST use cache-kind-appropriate metrics; one-size-fits-all is non-compliant** (Pass 53 v8h+1 owner directive 2026-05-10).

    **Owner trigger:** *"What about cftc endpoints coverage, polygon economy, alfred, etc. Why where these missed in the prev turn?"*

    **The rule:**

    Coverage / completeness analyses must apply different metrics per cache `kind`:

    | Cache kind | Coverage metric | Completeness signal |
    |---|---|---|
    | `per_ticker` | `% universe tickers with non-empty cache file` | `n_files_total / universe_size`; sampled non-empty count |
    | `single` | `% rows with non-null in column` (data-quality) | `row_count` + `latest_obs_date` |
    | `global` | `% series files with non-null in column` | `series_count` + `% non-empty` + `latest_obs_date` |

    **Why:** the per-ticker `coverage_pct` formula returns `None` for global feeds (CFTC, Polygon economy, FRED, ALFRED) because they have no per-ticker dimension. Rolling those into "N/A" without a kind-appropriate audit creates silent gaps — exactly the failure mode that surfaced when the owner asked "what about cftc endpoints coverage, polygon economy, alfred, etc." 2026-05-10. Empirical audit showed all four are COMPLETE per their respective Sprint 0A specs; the issue was audit methodology, not data.

    **Pre-flight verification when authoring a coverage analysis:**

    ```
    For each cache kind in {per_ticker, single, global}:
      report the kind-specific coverage metric AND completeness signal
    Endpoints reported as 'N/A' in coverage_pct must include an
      explicit kind-appropriate signal in the same row.
    ```

    **End-of-turn check:** if any coverage analysis is authored and any cache dir is reported with only `coverage_pct=None` / "N/A" without a kind-appropriate replacement metric, the response is non-compliant.

    **First application:** Sprint 0A dashboard Coverage Matrix tab adds `Completeness` column showing kind-appropriate signals (row-count + latest-obs-date for single feeds; series-count + non-empty% + latest-obs-date for global feeds). Per-row completeness fields land in `data.json` for all 1076 coverage-matrix rows.

    **Joint:** CHECKLIST #76 (audits must include functional verification not just inventory — #80 is the kind-aware specialization), CHECKLIST #77 (canonical-source rule — both flag silent gaps that look like "no data" but are methodology bugs); INV-047 sister pattern (Quiver etfholdings refresh dead-end was the LAST gap a single-metric audit could surface — kind-aware audit is what catches the next one).

81. **HARD RULE — Per-addressal pyramid + same-commit rule applies to BUGs and INVs identically to DECs** (Pass 53 v8h+1 owner directive 2026-05-10).

    Owner directive 2026-05-10: "Promotion process per DEC approved. Apply for also bugs and INV as applicable. Changes will also need to be reflected across all docs as per per turn sweep process."

    **Why:** DEC-594 same-commit rule was originally written in DEC-language (RESOLVED-DECIDED -> RESOLVED-IMPLEMENTED) but the underlying principle — code change + test + register entry + doc sweep all in the same commit — applies identically when:
      - resolving a BUG (BUG fix code + regression test + BUG_REGISTER status flip + AUDIT.md narrative)
      - closing an INV (INV diagnostic finding + remediation code/test + OPEN_INVESTIGATIONS status flip + AUDIT.md narrative)

    **Apply when:** any addressal that flips an item's status — DEC RESOLVED-IMPLEMENTED, BUG RESOLVED, INV RESOLVED/RESOLVED-DOCUMENTED. The pre-flight checklist must explicitly note the same-commit deliverable list before code is written. End-of-turn check: if any RESOLVED-* status flip lacks a matching code+test artifact pair landing in the same commit, the response is non-compliant.

    **First application:** Pass 53 v8h+1 INV-046 diagnostic (commit `041229b12`) and 0A.8 DEC-608 (commit `d57a07ee6`) both followed this pattern - owner ratified retroactively in this directive.

    **Joint:** DEC-594 (same-commit rule, original DEC-language formulation), CHECKLIST #78 (per-addressal pyramid - this rule extends scope to BUG/INV).

82. **HARD RULE — Stage 2 dashboard surfaces a per-item promotion-path column** (Pass 53 v8h+1 owner directive 2026-05-10).

    For every DEC, BUG, INV row in the Stage 2 dashboard, a single-cell `Promotion` column displays the promotion-path tier inferred from `(status, status_grep.coded, status_grep.wired, status_grep.tested)`:

    | Tier | Display | Trigger | Recommended action |
    |---|---|---|---|
    | IMPLEMENTED | green | status RESOLVED-IMPLEMENTED, or BUG-RESOLVED with code+test refs | none (already done) |
    | READY | green | RESOLVED-DECIDED + (wired or coded) + tested | promote: flip status to RESOLVED-IMPLEMENTED in same commit |
    | CODE_ONLY / NEEDS-TEST | amber | coded but not tested | add regression test in same commit |
    | TEST_ONLY / NEEDS-CODE | amber | tested but not coded | rare; verify the test isn't a stub-only |
    | SPEC_ONLY | red | PARTIAL-SPEC-ONLY, or RESOLVED-DECIDED with no artifacts | author code + test |
    | DEFERRED | blue | status DEFERRED_TO_* | none until trigger; informational |
    | BLOCKED | blue | status BLOCKED_ON_* | watch dependency |
    | SUPERSEDED / OBSOLETE | grey | superseded or obsolete | none |
    | OPEN / SURFACED | red/amber | BUG OPEN, INV OPEN/SURFACED | see action per kind |

    **Why:** the registry totals (530+ DECs / 148 BUGs / 47 INVs) became un-actionable as "PENDING" counts grew because there was no quick triage signal showing which items were one commit away from RESOLVED-IMPLEMENTED vs which were genuine spec-only backlog. Promotion-path tier collapses (status x grep) into a single triage label suitable for prioritization sweeps.

    **Apply when:** rebuilding the Stage 2 dashboard. The `compute_promotion_path()` function in `scripts/build_dashboard_stage_2.py` is the canonical implementation. Tooltip on each cell shows the per-item reason (e.g. "Wired in active path + tested; eligible for RESOLVED-IMPLEMENTED").

    **Joint:** CHECKLIST #81 (BUG/INV inherit DEC promotion process), DEC-594 (same-commit rule that this column tracks), DEC-503/DEC-597 (pyramid layers feed the artifact-grep signal).

83. **HARD RULE - Data-layer migration DECs MUST land with companion silent-gap coverage tests in the same push** (Batch 302 owner-directed comprehensive pyramid review 2026-05-21; codified after L155).

    A "data-layer migration" is any DEC that switches the producer for a value the engine consumes - examples: DEC-497 D4 yfinance->Polygon for `.info`, DEC-440 av_news->polygon_news, DEC-456 SEC EDGAR structured, future Polygon->Quiver switches.  Six silent bugs over 6+ months (META corruption, news Path B, 13F historical, PEAD financials_json, foreign_rev_pct, BUG-286 market_cap) all match a single pattern: the producer changed, the consumer-side default value was retained as a placeholder, and downstream fail-closed gates (BUG-238-class) silently rejected.  The 13-tier pyramid was 100% green throughout.

    Migration commit MUST include, in the same push:
      a. **Tier 7 data integrity test** - assert the new source has populated values for >=80% of expected universe (catches P5 default-placeholder pattern + P4 missing-producer at cache-population layer).
      b. **Tier 11 property test** - assert producer-side value equals consumer-side value for a random sample (catches P2 path-disambiguation - consumer reading wrong source).
      c. **Tier 13 stress test** - fresh-fetch from clean state must yield non-default values for known oracle tickers (catches P5 placeholder-default at runtime).
      d. **Tier 9 acceptance test** - phase-entry universe coverage gate measuring the actual liquid-pass-rate at scale (catches degraded delivery at the system level even when individual code paths pass).

    Without these, any migration is automatically a silent-gap candidate per L155.  Pre-flight blockers if migration DEC lands without companion tests:
      - 🔴 Tier 7 absent: HALT.  Add the cache-population audit before merging.
      - 🔴 Tier 11 absent: HALT.  Add the producer-consumer invariant.
      - 🔴 Tier 13 absent: HALT.  Add the stress test on clean state.
      - 🔴 Tier 9 absent: HALT before phase entry.

    **Why:** the pyramid certifies "code runs"; it does NOT certify "system delivers contracted result at scale" unless explicitly told to measure shape/coverage.  Migration is the canonical moment when shape changes silently.  See L155 for the full pattern walkthrough across BUG-286 + 5 sibling bugs.

    **Apply when:** any DEC tagged `data-source-migration` in AUDIT_INDEX, OR any DEC that replaces `yfinance.*` / `pd.read_html` / `requests.get` calls with a different producer, OR any DEC that touches the producer side of a field consumed by `_build_liquid_universe` / `is_liquid` / regime classifier / strategy entry gates.  Companion test file: `backtest/tests/test_silent_gap_pyramid.py` (Batch 302 canonical implementation - 25 tests across 9 of 13 tiers).

84. **HARD RULE — Verify DATA AVAILABILITY before claiming an engine "bug"** (Pass 53 owner directive 2026-05-27; codified after Batch 406 mis-diagnosis L157).

    Pattern: I (assistant) saw `screen_universe ... 0/0 passed` in the engine log for 2020-2021 dates, traced through code to `DATA_LOAD_START = date(2021, 5, 5)`, and shipped Batch 406 as a "bug fix" without first checking whether OHLCV data actually existed for the pre-2021 window. Reality: Polygon Stocks Starter is a 5-year rolling cache; data does NOT exist before 2021-05-11. Engine was behaving correctly. The "fix" was harmless but the framing was wrong; sunk hour-plus of forensic + code + doc effort on a non-bug.

    **Before claiming any engine path is "broken," pre-flight MUST include:**
      a. **Check the cache/source files directly.** For OHLCV-related issues: run `python -c "import pandas as pd; print(pd.read_parquet('data_prefetch/polygon/ohlcv_daily/AAPL.parquet').iloc[[0,-1]])"` (or equivalent for the data class). For signal data: read 1 sample file's date range + row count.
      b. **Cross-reference with `backtest/config.py` header comments.** That file documents data source + window constraints (e.g. "Polygon Stocks Starter 5y rolling cache, locked 2021-05-05 -> 2026-05-05"). Read the header before declaring config constants stale.
      c. **Verify the symptom is incompatible with available data.** `0/0 passed` in screen_universe is ambiguous: could be data-missing (engine correct) OR universe-filter-bug (engine wrong). The disambiguation is whether the OHLCV cache has rows for the relevant dates.
      d. **State the data-availability check result in the pre-flight block** before proposing any code change.

    **Apply when:** any user-visible engine output appears to indicate "missing trades" / "zero candidates" / "empty universe" / "0/0 passed" for some time window, OR any time a user asks "why is X not working for [historical period]."

    **Why:** the cost of a wrong bug diagnosis is high — wasted forensic time + spurious code change + wrong-framing doc updates that need rollback. The data-availability check is 30 seconds. Skipping it because the symptom "looks like a bug" violates the cheaper-first principle.

    **First application (retroactive):** Batch 407 rollback of Batch 406 (DATA_LOAD_START "bug" that was actually correct engine behavior per data availability).

    **Joint:** CHECKLIST #77 (canonical-source attribution — for OHLCV the canonical source is `data_prefetch/polygon/ohlcv_daily/`), CHECKLIST #79 (data-layer migration tests — checks coverage at scale; #84 is the same principle applied to bug investigation), L155 (silent-gap pattern — cousin: too-little data silently absorbed; #84 fights too-eagerly diagnosing too-little-data as engine bug), L157 (this directive's codified lesson).

85. **HARD RULE - Visible pre-flight verification block PRECEDES each recommendation, not at end of response** (Pass 52 owner directive reaffirmed Batch 407 2026-05-27).

    The Pass 52 standing rule per CLAUDE.md says: "Every recommendation in every response must be preceded by a visible pre-flight verification block applying the full CHECKLIST.md ... Pre-flight executes BEFORE the recommendation is stated, not after." Multiple session violations: I (assistant) wrote "CHECKLIST compliance" summaries at END of responses instead of before each recommendation. CHECKLIST #45 (end-of-response compliance enumeration) is a SEPARATE rule; it does NOT replace #85.

    **Format (mandatory before each recommendation):**
    ```
    Pre-flight per CHECKLIST + memory:
    - [check] #N <item> - <brief evidence>
    - [warn]  #M <item> - <flagged concern>
    - [halt]  #K <item> - <halt condition>
    - N/A     #J <item> - <reason not applicable>
    ```
    Items not applicable still get an N/A line (silent skipping is non-compliant; per #45). If any item flags HALT, revise recommendation before stating.

    **Apply when:** any recommendation, scope claim, framework design, threshold proposal, code change, batch closure, status flip. Does NOT apply to: factual answers, verification reports of code state, simple status updates with no recommendation.

    **Past violations:** end-of-response compliance summaries in Batches 393-406 (current session) and earlier sessions. Owner has explicitly called this out as a repeat failure.

    **Joint:** #45 (end-of-response compliance - SEPARATE from this), Pass 52 standing rule in CLAUDE.md, `feedback_audit_recommendations_against_existing_directives.md` (overlap on contradiction detection).

86. **HARD RULE - Owner-facing communication uses Latin alphabet for option labels and headers; no Greek** (Batch 407 codification after 3rd memory violation 2026-05-27).

    Memory `feedback_no_greek_alphabets.md` (owner directive): use A/B/C or 1/2/3 for option labels, never alpha/beta/gamma/delta/epsilon. Despite the memory, I violated this 3 separate times in this session. Owner: "Third violation."

    **Apply when:** writing option lists, decision tables, multi-path framing, anything the owner reads and references back to me. Phase labels in code (Phase A/B/C per DEC-508) and academic citations are explicitly exempt - they are not option labels.

    **Why CHECKLIST-codified now:** memory was insufficient; this rule needs the hard gate of pre-flight referencing. If pre-flight #86 is checked before sending any option list, the violation cannot ship.

    **Joint:** `feedback_no_greek_alphabets.md`, #85 (visible pre-flight catches this if checked).

87. **HARD RULE - Platform / infrastructure recommendations MUST enumerate account-level gates BEFORE recommending** (Batch 407 codification after AWS new-account compounding-gates lesson L158).

    Pattern (today's AWS path): I recommended AWS over Hetzner without first enumerating: (a) EC2 RunInstances account verification status, (b) ssm:GetParameter IAM permission for AMI lookup, (c) iam:CreateRole/CreateInstanceProfile IAM permissions, (d) on-demand vCPU quota, (e) spot vCPU quota, (f) spot instance capacity. Each became a runtime blocker requiring owner action. Total wall-time cost: ~4 hours of waiting + 1 hour of code fixes that could have been avoided by upfront gate enumeration.

    **Before recommending any platform / cloud / infrastructure shift, the pre-flight MUST list:**
      a. Account verification status (new accounts have manual-review gates)
      b. All IAM permissions needed for the called services (EC2, IAM, S3, SSM, Billing, etc.)
      c. Service quotas relevant to the workload (vCPU on-demand AND spot separately for AWS; equivalents for other clouds)
      d. Instance/capacity availability for selected family (live `describe-spot-price-history` or equivalent)
      e. Network / region constraints (data locality, transfer costs)
      f. Account-billing-tier features (e.g., Polygon Stocks Starter 5y window; AWS Free Tier credit eligibility list)

    Where these cannot be verified live, the recommendation must explicitly call out the unverified assumption AND propose verification commands the owner can run.

    **Apply when:** recommending any platform shift (Hetzner -> AWS, on-demand -> spot, single-machine -> multi-machine, region change). Does NOT apply when continuing on the same platform / family the workload already runs.

    **Joint:** L158 (this directive's codified lesson), #84 (data-availability before claiming engine bug - cousin: verify environment constraints before recommending shift).

88. **HARD RULE - Multi-step owner walkthroughs must be self-consistent across all steps + against all subsequent expectations** (Batch 407 codification after Phase-A credential-exposure walkthrough self-contradiction L160).

    Pattern (Phase A AWS setup walkthrough): Step "What to send me" said "paste these in chat" with a template including Access Key + Secret. When owner did exactly that, I panicked and said "rotate everything - credentials in chat is a security risk." Self-contradicting: I asked owner to do X then reacted to X as a problem. Cost: owner had to rotate credentials + we lost ~15 min.

    **Before issuing a multi-step walkthrough or procedure, audit:**
      a. Each step's expected execution against ALL subsequent expectations in the same response or the implied next responses
      b. Whether any step asks the owner to take an action that has a known cost/risk (security, financial, data loss) - if yes, the step itself must include the mitigation, not a later step
      c. Whether the channel/medium specified for the action is appropriate (e.g., credentials -> password manager / AWS SSM Parameter Store / encrypted channel, NOT chat)
      d. Whether any constants/IDs/URLs cited in the walkthrough are likely to be stale (e.g., AMI IDs rotate; check live)

    **Apply when:** writing any setup walkthrough, Phase definition, onboarding procedure, or any owner-action instruction sequence longer than 3 steps. Does NOT apply to: single ad-hoc commands; status reports; verification queries.

    **Joint:** L160 (this directive's codified lesson), `feedback_audit_recommendations_against_existing_directives.md` (this is the same family - don't contradict your own prior step), `feedback_no_write_only_md_files.md` (related: avoid producing walkthroughs that need follow-on corrections).

89. **HARD RULE - Cost recommendations cite live pricing, not memory/historical estimates** (Batch 407 codification after spot-pricing stale-estimate lesson).

    Pattern (today's AWS spot recommendation): I estimated c7a.8xlarge spot at "$0.30/hr" (memory/historical) when current live price was $0.62-0.69/hr (~2x my estimate). Owner caught it. The mis-estimate framed Path-C as "$7.50 total" when reality was "$13-14 total." Decision basis was distorted by a factor of ~2.

    **Before stating any cost figure ($/hr, $/run, $/month, $/iteration) in a recommendation:**
      a. For AWS: run `aws ec2 describe-spot-price-history` (spot) or look up the AWS pricing page (on-demand). State the source in the recommendation.
      b. For Hetzner / DigitalOcean / Vultr / other clouds: same - live page lookup or last-7-day quoted price.
      c. For Anthropic / OpenAI / LLM costs: model rate card current as of response time.
      d. Memory-based estimates are NOT acceptable for cost-driving decisions. They are acceptable only for sanity-check ranges with explicit "memory-estimate; verify before commit" caveat.

    **Apply when:** any cost statement that informs an owner decision. Does NOT apply to: cost-after-the-fact reporting (e.g., "actual spend was $5.63").

    **Joint:** L158 (cousin: live API verification for quotas), #87 (platform-gate enumeration also requires live checks).

90. **HARD RULE - Status updates involving long-running resources MUST re-verify current state via API/files at report time, not from memory** (Batch 410 codification after batch_3 spot-reclaim went unreported for 1.5h 2026-05-27).

    Pattern (this session): batch_3 was spot-reclaimed by AWS at ~00:00-00:30 UTC. I (assistant) continued to report it as "RUNNING" in multiple subsequent status updates over ~1.5 hours because I trusted the prior snapshot instead of re-querying. Owner caught this: "Why wasnt update on batch 3 provided much earlier?"

    Root cause: status updates used cached state from the launch event rather than current state from AWS. The L4 14-check monitor I had armed earlier WOULD have detected the heartbeat staleness (W2 check) but its output was never read into the status report.

    **Before issuing any status update that references long-running resources (EC2 instances, AWS spot requests, background tasks, multi-stage jobs, in-flight batches, monitors), the report MUST include current state verification for each referenced resource:**
      a. EC2 instances: `aws ec2 describe-instances --instance-ids <id>` for State.Name + StateReason.Message + (for spot) `describe-spot-instance-requests` for Status.Code
      b. S3 sentinels: `aws s3 ls s3://bucket/path/_COMPLETE` for each tracked batch
      c. S3 heartbeats: pull each tracked batch's heartbeat file + check `ts=` timestamp vs current time (> 15 min stale = surface in report)
      d. Background tasks: read tail of each task's output file at report time (or invoke task-status check)
      e. L4 monitor output (if armed): read its latest poll output and include any WARN/KILL signals in the status report

    Caching prior state from earlier in the same session is NOT acceptable for resources that can change asynchronously (instances can be reclaimed; sentinels can land; heartbeats can go stale). The cost of re-querying is 1-2 seconds; the cost of stale reporting is the entire delta between actual change and detection (1.5 hours in this case).

    **Apply when:** any status update / progress report / "update on X" response covering >1 tracked resource OR any resource with async-change risk (spot instances, billable jobs, jobs with hard timeouts).

    **Past violation:** session 2026-05-27 batch_3 reported as RUNNING for 1.5h after spot reclaim; owner caught it.

    **Joint:** L161 (this directive's codified lesson), #84 (verify before claiming bug - cousin: verify before claiming progress), `feedback_monitor_intermediate_counts.md` (intermediate counts catch async changes), `feedback_audit_recommendations_against_existing_directives.md` (don't trust prior state without re-check).

91. **HARD RULE - Monitoring that doesn't take ACTION or get READ is dead infrastructure - never claim "monitor is armed" as a substitute for in-loop checks** (Batch 411 codification after L4 14-check monitor died-at-startup + heartbeats-unread-for-10h 2026-05-27).

    Pattern (this session): I armed two layers of monitoring for the AWS run: (1) L4 14-check Python `monitor_phase_1a_beta_health.py` as background task `bv76426sn`; (2) S3 heartbeat protocol writing every 5 min to `s3://bucket/heartbeat/batch_N.txt`. Across the 10-hour run: L4 monitor produced 9 lines total - all PowerShell `NativeCommandError` wrapping a single `datetime.utcnow()` deprecation warning. It died at startup and was never read. S3 heartbeats DID land correctly (verified post-hoc - all 5 batches had fresh ts= entries) but I never polled them during the run. Net: two monitoring layers, zero detections. Owner caught: "What is the use of monitoring if you don't even read the results?"

    Root cause: monitoring was treated as a passive logging artifact ("armed and forgotten") rather than as an active control loop (poll + interpret + ACT). The L4 monitor's only consumer was supposed to be me reading it at status-request time, but I never did. The heartbeats had no consumer at all - no orchestrator was polling them.

    **Before claiming a monitor / heartbeat / health-check is "armed" or providing operational cover:**
      a. The monitor MUST have a defined ACT-ON-DETECTION path - log-only is unacceptable. Examples: HB stale > N min → terminate + relaunch instance; ABORT verdict from forensic → terminate all downstream; engine WARN signal → email + pause launches.
      b. The monitor's output MUST be ingested into a higher-level digest that I (or the orchestrator) read at every status-request point or every poll. If the monitor output goes only to a log file no one reads, it does not exist.
      c. For background-task monitors: verify the task produced ≥ 1 meaningful output line within the first poll interval. If the task is silent past that window, treat it as DEAD and either fix or abandon - never assume "still running, just quiet."
      d. For multi-layer monitoring (L1/L2/L3/L4 style), each layer must have a different ACT-ON path so they are complementary, not redundant. Two monitors that both only log are still zero monitors.

    **Apply when:** arming any monitor / heartbeat / health-check / watchdog / background-task observability; claiming "monitor is in place" as risk mitigation for a long-running operation; reporting status that references "the monitor saw X" (verify by reading the monitor's output at report time, not by recalling its prior reading).

    **Past violation:** session 2026-05-27 - both L4 14-check + S3 heartbeat went unread for 10h while batch_3 was lost to spot-reclaim and reported as RUNNING for 1.5h.

    **Fix shipped this batch (Batch 411):** action-taking monitor folded into `aws_batch395_parallel.py` per-poll loop: heartbeat-stale > 30 min → auto-terminate + auto-re-add to pending → next poll relaunches; per-poll `[DIGEST hh:mmZ] b1=DONE b3=PENDING b4=s/120m@2025-06-13(hb15s) b5=o/40m@2023-01-25(hb45s)` one-line summary I read at every status request.

    **Joint:** L162 (this directive's codified lesson), #90 (status updates re-verify current state - cousin: status updates re-read monitor output), `feedback_monitor_intermediate_counts.md` (intermediate-count monitoring is the specific case; this is the general rule), `feedback_no_write_only_md_files.md` (related antipattern: artifacts created without consumers).

92. **HARD RULE - No new .md files without explicit owner approval** (owner directive 2026-05-28).

    Pattern: even with `feedback_no_write_only_md_files.md` standing rule + my own 3-check (specific consumer / beyond commit message / cross-batch value), I still produced .md files at a rate that creates clutter. Owner-strengthened gate: no new .md file may be created unless owner has explicitly approved its creation in the same conversation. The 3-check is no longer sufficient; explicit owner approval is now required.

    **Apply when:** writing any new `.md` file with the `Write` tool (or via creating a file outside an Edit operation). Includes: reference docs, framework specs, optimization candidates, audit reports, post-mortems, analysis summaries, walkthroughs, runbooks. Does NOT apply to: editing existing `.md` files (Edit is unaffected); auto-generated `.md` files produced by scripts (e.g., `optimization_summary.md` from `optimize_strategies_from_cube.py` is script output, not a hand-authored file); files in `archive/**` (already excluded from per-turn doc-sync per L143 + `feedback_all_docs_sweep.md`).

    **How to apply:** before calling `Write` on any path ending in `.md`, surface the intent in conversation and ask owner explicitly: "Should I create `<filename>.md` with `<one-sentence purpose>`?" Wait for explicit yes. If the answer is no or implicit, fold the content into an existing `.md` file or into the commit message instead. Edit-an-existing-doc is preferred over Write-a-new-doc by default.

    **Past pattern:** session 2026-05-26 owner correction in `feedback_no_write_only_md_files.md` ("7 of 10 artifacts I created this session had ZERO external references"). 3-check was specified but not strong enough. Owner is now codifying the explicit-approval gate as the stronger fix.

    **Joint:** `feedback_no_write_only_md_files.md` (the 3-check stays as the secondary filter; #92 is the primary gate), #6 (modifying CLAUDE.md needs owner approval - same family rule for that critical doc), #67/#67.b (per-turn doc-sync still applies to existing docs).

93. **HARD RULE - After every push, verify CI Test Pyramid status (full 13 tiers) before claiming pyramid green. NEVER report "X/X tests green" from a focused subset.** (Owner directive 2026-05-28 reaffirming `feedback_pyramid_full_13_tiers_mandatory` after ~12 consecutive CI Test Pyramid failures from Batches 412-422 went unnoticed because I only ran `test_unit.py + test_integration.py + Batch-specific files` locally.)

    Past failure (this exact pattern owner has called out repeatedly):
      - Across Batches 412-422 (2026-05-28), I claimed "999/999 green" / "995/995 green" / etc. on each push.
      - The "X/X" counts came from a focused subset (~10 of 14 test files), NOT the full pyramid.
      - CI ran the full 13-tier pyramid (per `.github/workflows/test-pyramid.yml`) and failed Tier 3 (`test_data_integrity.py::test_data_integrity_2_ohlcv_freshness`) on EVERY push.
      - Owner noticed 2026-05-28 turn 67: "By the way all actions from 306-420 have failed on git." Owner had to discover this themselves; I had no proactive check.
      - Lineage: `feedback_pyramid_full_13_tiers_mandatory.md` (2026-05-12 codification of identical violation in Batches 49-68) → I repeated it 10 more times. Same pattern, same memory directive, same failure.

    **Apply before claiming any push is green:**
      a. Run the FULL pyramid via `python -m pytest backtest/tests/ -q --tb=line` (NOT a focused subset). If any test fails, fix or surface BEFORE push.
      b. After `git push origin main` succeeds, poll `https://api.github.com/repos/<owner>/<repo>/actions/runs?per_page=3` (or `gh run list --limit 3` when `gh` CLI is available) for the most recent workflow run targeting the just-pushed commit.
      c. Wait for `status == "completed"` (typically 5-15 minutes for the Test Pyramid). Report `conclusion` truthfully — `failure` is NOT "green".
      d. If any tier red, investigate the failed step via the workflow's job → step logs (REST API: `/actions/runs/<run_id>/jobs`). Don't silently skip the tier.
      e. The status update MUST include CI conclusion. "X/X local green + CI status: PENDING" is acceptable. "X/X green" without CI verification is NOT.

    **Joint:** `feedback_pyramid_full_13_tiers_mandatory.md` (this is the codified hard-rule version), CHECKLIST #69 (full 13-tier pyramid mandatory), CHECKLIST #75 (pyramid runs every push, no doc/data exception), L163 (this directive's codified lesson).

94. **HARD RULE — Update `EXECUTION_QUEUE.md` every turn that produces meaningful changes. The top of the queue is the next execution target; deferrals retain queue position.** (Owner directive 2026-05-29 Batch 432: *"We have been jumping all over the place and the items get missed. Lets bring order to the chaos."*)

    Past failure pattern: across the 2026-05-28 session, multiple project items repeatedly fell off the radar — cube re-run merge, walk-forward gate decision, 25 negative-Sharpe deprecation, Phase 1B-α launch readiness — because they lived only in conversation context and TodoWrite (in-session, ephemeral). When a session compacted or rolled to a new conversation, the items were lost or mis-prioritized. Owner had to repeatedly re-surface the same obligations.

    Fix: project-level sequential execution queue at `EXECUTION_QUEUE.md`. Distinct from per-session TodoWrite: TodoWrite is "what am I doing in this conversation"; EXECUTION_QUEUE is "what is the project's next milestone." Survives across sessions.

    **Apply when:** every turn that ships code / archives docs / closes a decision / advances cube state / addresses an owner directive **OR surfaces a new finding** (something didn't behave as expected, a bug was spotted, a follow-up is needed). End that turn with an `EXECUTION_QUEUE.md` update — advance status, move RESOLVED items to the bottom of the active queue (NOT to the Completed log unless they're truly never coming back), add newly-discovered items + findings as fresh rows, surface BLOCKED/DEFERRED with reason. **Does NOT apply to**: pure conversational answers, status reports, queries that don't produce changes.

    **How to apply:**
      a. Read `EXECUTION_QUEUE.md` at start of turn (alongside TodoWrite) to know the next target.
      b. Top item is what to execute next unless owner says otherwise. If top is BLOCKED/DEFERRED, the next non-blocked PENDING/REOPENED runs.
      c. End-of-turn: Edit `EXECUTION_QUEUE.md` to reflect new state.
      d. DEFERRED items retain their position — skipped *without* being moved.
      e. RESOLVED items move to the BOTTOM of the active queue table (not the Completed log) and stay tagged RESOLVED. This preserves traceability for when the same area is touched later. Only DONE-ARCHIVED items (truly never coming back) get pushed to the Completed log section.
      f. REOPENED items move to row #1 of the active queue. Update Notes with what changed.
      g. **Findings-become-items mandate (owner directive 2026-05-29 Batch 444):** anything discovered in a status report ("X was supposed to drop but didn't", "Y stayed at N", "Z needs investigation") becomes a queue row that SAME turn. Don't let findings dangle in chat history.
      h. Reorder freely via Edit when priorities shift — but the new top is what runs next.
      i. Failure to update at end of a meaningful-change turn = non-compliant.

    **Status enum:** PENDING / IN_PROGRESS / BLOCKED / DEFERRED / RESOLVED / REOPENED / DONE-ARCHIVED. Only ONE item is IN_PROGRESS at any time.

    **Joint:** TodoWrite (per-session), `MONITORING_FRAMEWORK.md` (operational state that informs queue items), CHECKLIST #67/#67.b (per-turn doc sync — EXECUTION_QUEUE update is one of those required syncs), `feedback_audit_recommendations_against_existing_directives.md` (queue items must be audited against existing rules before adding).

95. **HARD RULE — When a process gap or audit gap is discovered, codify it in CHECKLIST.md AND LEARNINGS.md the SAME turn as a new numbered rule + L-entry. Adding to queue alone is insufficient.** (Owner directive 2026-05-29 Batch 448: *"Add the above to checklist and learnings as applicable. You are mandatorily required to add to checklist and learnings in each turn if such gaps are found! This is a process error on your end!"*)

    Past failure pattern: Batch 446 surfaced two audit gaps (PSR hardcoded False bug, `_cell_stats` parallel-universe). I queued them as items #4 + #5 in EXECUTION_QUEUE.md but did NOT add a corresponding CHECKLIST rule or LEARNINGS entry. The queue tracks what to DO; CHECKLIST + LEARNINGS prevent the gap from recurring elsewhere. Without the second step, the next time the same anti-pattern appears in a different file, it will be missed again — which is exactly what L143 documents for the original wired=yes-grep bug.

    **Apply when:** discovering ANY of (a) a code path that doesn't do what the comments / DEC claim, (b) tests that pass without checking the meaningful invariant, (c) a lesson that exists for one file/layer not being applied to a parallel file/layer, (d) a "placeholder" / "TODO" / hardcoded sentinel value that ships in production output, (e) a previously-codified rule whose scope didn't cover the new finding.

    **How to apply:** end the turn with three artifacts, not one:
      a. New CHECKLIST.md numbered rule (mandatory) that turns the finding into a forward-looking gate.
      b. New LEARNINGS.md L-entry (mandatory) that captures the past-tense story (what happened / why / how to detect next time).
      c. New EXECUTION_QUEUE.md row for the concrete fix (the queue is the WHERE-TO-DO; CHECKLIST + LEARNINGS are the WHAT-NOT-TO-REPEAT).

    Failing to ship all three when a gap is found is itself a process violation and a CHECKLIST #95 breach.

    **Joint:** CHECKLIST #94 (EXECUTION_QUEUE update), CHECKLIST #67/#67.b (per-turn doc sync), `feedback_wired_means_engine_consumed.md` (same lesson at the lower layer), `feedback_pyramid_full_13_tiers_mandatory.md` (same "lessons must propagate" theme).

96. **HARD RULE — Show `EXECUTION_QUEUE.md` (or its top 5-10 rows) at the END of every turn that updated it. Mandatory.** (Owner directive 2026-05-29 Batch 448: *"You are required to show the queue at the end of each turn mandatorily."*)

    Past failure pattern: I updated the queue but ended the turn with a narrative summary that didn't show the current queue state. Owner could not see what was now at the top without re-opening the file. The queue is the contract for "what runs next"; if it's not visible, it might as well be private state.

    **Apply when:** every turn that modifies `EXECUTION_QUEUE.md`. End the turn with a rendered queue snapshot (table or one-line-per-row summary) so the owner can read the current next-target without opening another file. Status icons / row numbers preserved.

    **Does NOT apply to:** turns that don't modify the queue (a pure clarifying answer, an explanation that produces no commits).

    **Joint:** CHECKLIST #94 (queue maintenance), CHECKLIST #90 (status updates re-verify state).

97. **HARD RULE — When an owner message contains multiple sub-questions, enumerate ALL of them explicitly before answering, then mark each as answered as you go. Partial answers to multi-part questions are a process failure.** (Owner correction 2026-05-29 Batch 449: *"you missed this!!!"* — I answered "are there other Pattern 3 gaps" but skipped the second clause "is there anything else in our analysis that we should be using and we should be doing but we are not currently.")

    Past failure pattern: I read multi-clause questions and answered the part I had a ready response for, treating the rest as "covered" or "implicit." Owner had to re-ask the missed clause for it to surface.

    **Apply when:** every owner message containing the word "and", semicolons, multiple sentences ending in "?", or compound subjects with multiple verbs. Before producing the answer:
      a. Enumerate the sub-questions as a numbered list in the answer (or internally).
      b. Confirm each enumerated item is independently addressed before composing the response.
      c. If any item is being deferred or rolled into another, state that explicitly ("not answering Q2 because it's covered by Q1's answer" rather than skipping).
      d. Failing to address every enumerated sub-question = process violation.

    **Joint:** CHECKLIST #95 (codify findings same turn — including this kind of process gap), L165 family (state must be SHOWN, not assumed).

98. **HARD RULE — Every data-prefetch DEC must come paired with a producer-DEC that consumes it. Prefetch without a downstream consumer is dead data and should be flagged in audits.** (Owner-question-driven finding 2026-05-29 Batch 451: of 8 prefetched data sources [Polygon news 454MB, CFTC COT 35MB, Apewisdom, Stocktwits 24MB, Pytrends 12MB, Finnhub earnings 1.5k rows, SEC EDGAR Form 4 133MB, Quiver 602MB], **only 2-3 are actually consumed by `backtest/signals/*` producers**. The rest sit on disk as dead data.)

    Past failure pattern: Sprint 0A scoped 8 APIs and wired them as prefetch sources. The wiring was complete from API to parquet cache. The CONSUMER side — `backtest/signals/<name>_producer.py` that reads the parquet and emits a screener-callable signal — was never paired into the same DEC. Result: 600+MB of high-value alt-data (Quiver patent momentum, lobbying, housetrading; Polygon news with sentiment scores; SEC EDGAR Form 4 with role differentiation) cached on disk with no downstream consumer.

    **Apply when:**
    - Proposing a new prefetch data source.
    - Auditing an existing prefetch directory.
    - Closing a Sprint 0A-style data-acquisition phase.

    **How to apply:** every prefetch-DEC ships paired with a producer-DEC (or producer-implementation) in the same batch. Audit step: `for dir in data_prefetch/*/; do grep -rln "$(basename $dir)" backtest/signals/ || echo "ORPHAN: $dir"; done` — every prefetch dir must have at least one downstream consumer. Orphans become queue items.

    **Same family as:** DEC-507 (data DEC + toolkit DEC ≠ integration; wiring is a third explicit deliverable). DEC-507 was scoped to the agent-toolkit layer; this rule extends it to the screener-producer layer.

    **Joint:** CHECKLIST #95 (codify finding same turn), L167 (this rule's lesson record), `feedback_wired_means_engine_consumed.md` (same theme: wired = consumed, not greppable).

99. **HARD RULE — Any queue item that proposes wiring data source X into consumer Y MUST include schema verification of both sides. Inspect the actual parquet columns before claiming "source X has what Y needs."** (Owner-prompted finding 2026-05-29 Batch 453: I proposed P14 ("wire SEC EDGAR Form 4 to differentiate filer role") and P17 ("wire SEC EDGAR direct insider into composite") without reading either the Quiver parquet schema or the SEC EDGAR parquet schema. Quiver insider parquet already has the filer-role columns; SEC EDGAR Form 4 parquet is filing-index only. Both my proposed fixes were against the wrong premises.)

    Past failure pattern: I read the docstring of `smart_money.py` ("SEC EDGAR via edgartools (DEC-456 + R1 owner-approved Pass 53)") and inferred that the SEC EDGAR cache contained decoded Form 4 transactions. I then queued P14 + P17 against that assumption. Owner asked the basic verification question ("what's the difference between SEC EDGAR Form 4 and Quiver insider — aren't they the same?") and the actual schema comparison surfaced: Quiver IS the decoded data; SEC EDGAR cache is just filing index.

    **Same anti-pattern as L164 / L167 / #98:** assuming wiring from docstrings / DEC references / file paths rather than verifying with `pd.read_parquet(path).columns`. Three lessons codified about this pattern; I still fell into it.

    **Apply when:** proposing any queue item of the form "wire data source X into composite Y" or "use feature Z from cache W." Before adding the row:
      a. Run `pd.read_parquet(<source X path>); print(cols, sample_rows)`.
      b. Compare to what consumer Y needs.
      c. If X is missing a column Y needs, the queue item is "build extractor for X first" (pre-req), NOT "wire X into Y."
      d. Document the schema check in the queue Notes column.

    **How to enforce:** any queue item proposing "wire X into Y" must include in its Notes:
      - The source parquet columns ("X has cols: a, b, c").
      - The consumer-required columns ("Y needs: d, e, f").
      - Resolution: direct wiring OR pre-req extractor.

    Failure to include this schema-comparison evidence in the queue item is a #99 violation. The queue item should be rejected and rewritten before it ships.

    **Joint:** CHECKLIST #95 (codify finding same turn), CHECKLIST #98 (prefetch-consumer pair), L164 (lessons must propagate across layers), L168 (this rule's lesson record).

100. **HARD RULE — Every queue item ships in three states: (a) Implemented (code exists), (b) Wired (the call path consumes it), (c) Activated (default-on, or explicitly flag-gated with a written reason + sunset date). No queue item closes as RESOLVED while any of {tests, wiring, activation} remains pending. Tests means the FULL pyramid for that file, not a subset.** (Owner directive 2026-05-29 Batch 455: *"For each item in queue in want the entire testing pyramid deployed and items to be executed, wired and activated. No activation is to be left as pending unless necessary!"*)

    Past failure pattern: queue items shipped as "RESOLVED-IMPLEMENTED" with code merged but the engine call path bypassing it (Pattern 1) or feature behind an inactive flag (activation pending). Examples from this session: PSR placeholder (implemented + wired but value placeholder); SEC EDGAR Form 4 (prefetched + accessor exists but composite-wiring missing); ~150 DECs flipped from RESOLVED-IMPLEMENTED to RESOLVED-DECIDED-PARTIAL after the wired=greppable lesson landed.

    **Activation states and their meanings.**
      - DEFAULT-ON — feature consumed without explicit flag. Highest activation.
      - FLAG-ON-DEFAULT — behind a flag whose default is True. Effectively default-on but flippable.
      - FLAG-ON-EXPLICIT — behind a flag, default False, must be explicitly enabled. Acceptable ONLY if there is a documented reason (data-quality risk, blast radius, owner-gated rollout) AND a sunset date for promotion to DEFAULT-ON.
      - DEAD-CODE — implemented + wired but never reached at runtime. Unacceptable.

    **Apply when:** closing any queue item as RESOLVED, claiming any DEC as RESOLVED-IMPLEMENTED, declaring any batch as shipped.

    **How to apply:** end the work with a 3-cell status block in the queue Notes column:
      - `tests: <pyramid tier list> N/N pass`
      - `wired: <consumer file:line> calls <implementation>`
      - `activated: <state from above>` (with reason + sunset if not DEFAULT-ON)

    Without all three cells filled, the queue item stays PENDING / IN_PROGRESS, not RESOLVED. RESOLVED with one cell missing is a #100 violation.

    **Joint:** CHECKLIST #69 (full 13-tier pyramid mandatory), CHECKLIST #93 (CI verification after push), CHECKLIST #94 (queue maintenance), CHECKLIST #95 (codify findings), CHECKLIST #98 (prefetch-consumer pair), CHECKLIST #99 (schema verification), `feedback_wired_means_engine_consumed.md`, L164 / L167 / L168 (lessons-must-propagate family).

101. **HARD RULE — No idling while a pyramid (or any blocking long-running task) runs if there are active items in the queue. Start the next queue item / bundle immediately on the working tree; reschedule the pyramid only AFTER all new edits land, never before.** (Owner directive 2026-05-29 Batch 470: *"Add in checklist that no idling while pyramid runs if any active items in the queue!"*)

    Past failure pattern: I kicked off a 35-40 min full pyramid and scheduled a sleep-wakeup to fire 25 min later, effectively idling on the work the owner had set me loose on. Even after the prior directive ("CI polling is non-blocking — move to next item and circle back when it completes"), I repeated the pattern by scheduling a wakeup to wait for the pyramid output rather than continuing to the next queue item.

    **Apply when:** any background task is running that doesn't depend on my next decision -- pyramid, CI poll, long bash, AWS run, prefetch job. The trigger is "the running task does not require my input for its next step."

    **How to apply:**
      a. Check queue: is there a next PENDING / IN_PROGRESS item I can advance?
      b. If yes: start work on it immediately. Edit files, write tests, draft commit messages on the working tree.
      c. If the in-flight task's result might invalidate my edits (e.g., a pyramid validating a state that no longer matches the working tree), KILL the in-flight task with TaskStop and re-launch it once all new edits land. Better to re-run a 38-min pyramid once over the full bundle than waste 38 min on a stale state.
      d. If no queue item is actionable, the answer is "wait for owner" not "sleep through this cycle."

    Explicit anti-pattern: `ScheduleWakeup(delaySeconds=1500)` to wait for a pyramid that the harness already auto-notifies on completion. The wakeup adds zero value and costs an entire cycle of work the queue needs.

    **Joint:** CHECKLIST #93 (CI non-blocking), CHECKLIST #94 (queue maintenance), CHECKLIST #96 (queue display end-of-turn -- the queue is the source of "what to work on next" during pyramid runs), `feedback_queue_cadence_directives.md` (owner-approved bundle/CI/delete cadence).

102. **HARD RULE — CI pyramid is the ground truth on Linux (deployment target); local pyramid is fast iteration on Windows. BOTH must pass on their own platform. Counts do NOT have to match exactly -- legitimate platform divergences are allowed.** (Owner directive 2026-05-30 Batch 486: *"1. Relax"* in response to the cycle-time / results-matching cost discussion. Replaces the prior 2026-05-29 Batch 479 "results must match" framing, which was too strict and consumed ~5 hours of CI churn on Batches 482-485 chasing parity that the engine's cross-platform non-determinism makes impossible.)

    **Rationale.** Local runs on Windows; CI + AWS production runs on Linux. Each is its own environment with its own dep stack (Win MSVC vs Linux glibc fp libs, different pandas-ta / numba variants). Some tests will legitimately diverge -- engine output, file paths, dep-version-sensitive tests -- and that's OK as long as each platform's full suite still passes.

    **What MUST be true:**
      - CI Test Pyramid completes with `conclusion: success` on Linux (the deployment target). This is the ship gate.
      - Local pyramid completes with all tests passing on Windows (for the dev who runs it). Optional pre-push for routine batches; recommended for risky ones (count assertions, engine code mutated, golden regen).

    **What is allowed to differ between local and CI:**
      - Total `passed` / `skipped` counts (different platform-specific skips). Example: `test_engine_optimization_parity` PASSes on Windows (where the golden was generated) and SKIPs on Linux (platform sidecar mismatch, per Batch 484).
      - Number of `xfailed` / `xpassed` (rare; OK).
      - Wall-time (CI is much faster; expected).

    **What is NOT allowed:**
      - Any FAILED test on either platform's full pyramid. A FAILED test on either runner blocks the ship.
      - Platform-specific code paths that aren't marked. Tests that pass on Windows + fail on Linux (or vice-versa) without an explicit `pytest.mark.skipif(...)` or sidecar guard are a bug -- the test should either be made platform-portable, marked explicitly, OR fixed.

    **Cycle-time defaults.**
      - Safe-additive batches (new producer / new tests / pure-doc): push to FEATURE BRANCH (CHECKLIST #103), let CI verify, merge to main when green. NO local pyramid required.
      - Risky batches (count assertions, schema, engine, golden): run local pyramid first via `pytest backtest/tests/ -n auto` (xdist parallel). Then push to feature branch.
      - Pre-push local with xdist drops wall-time from ~38min to ~30-40min on this codebase (slower than originally projected per Batch 482 honest-accounting; the long-tail integration tests dominate).

    **Apply when:** every batch ships. Report which runner produced the green state in the commit-followup.

    **Joint:** CHECKLIST #69 (full 13-tier pyramid mandatory -- both runners must pass the FULL pyramid, not subsets), CHECKLIST #93 (CI verification after push), CHECKLIST #101 (no idling during pyramid), CHECKLIST #103 (feature-branch workflow), `feedback_pyramid_full_13_tiers_mandatory`.

103. **HARD RULE — Risky / multi-file batches go to a feature branch first; only merge to `main` after CI is green. Main stays reliable.** (Owner directive 2026-05-30 Batch 486: *"2. Approved"* in response to "switch to feature-branch workflow for risky bundles?")

    **Rationale.** Batches 482-485 demonstrated the cost of pushing risky changes directly to main: 4 consecutive RED commits, CI churn, no way for other consumers (cron jobs, AWS pulls of main, future contributors) to trust main. Feature-branch isolation absorbs CI cycles; main only sees green commits.

    **Apply when:**
      - The batch touches more than one file AND any of: count assertions / golden snapshots / engine code / schema / new test files. Use feature branch.
      - The batch is a pure single-file fix OR a doc-only sweep. Direct-to-main is OK.
      - When in doubt: feature branch.

    **How to apply:**
      a. Create a feature branch: `git checkout -b batch/<NNN>-<slug>` (e.g. `batch/486-checklist-cycle-time-relax`).
      b. Commit there. Push: `git push -u origin batch/<NNN>-<slug>`.
      c. CI fires on the branch (workflow `on: push: branches: [main]` -- update workflow to also trigger on `branches: [main, batch/**]` OR just trigger via PR).
      d. If CI red: fix on the branch, push, repeat.
      e. When CI green: fast-forward merge or PR into main. Main now has a green commit.
      f. Delete the feature branch (local + remote).

    **Workflow update needed (one-time):** `.github/workflows/test-pyramid.yml` `on:` block must include `batch/**` to trigger CI on feature branches, OR rely on the `pull_request` trigger when opening a PR to main. Either works.

    **Exception:** CI workflow edits (yml changes) must go directly to main because the workflow's `on: push: branches: [main]` is what makes it fire. A workflow change on a feature branch wouldn't be exercised until merged. Risk-mitigation: validate the workflow yml syntax locally with `actionlint` or `yamllint` before pushing.

    **Joint:** CHECKLIST #93 (CI verification after push), CHECKLIST #101 (no idling), CHECKLIST #102 (CI = ground truth), feedback_standing_approvals (commit + push every turn -- still applies; branch determines the push target).

104. **HARD RULE -- Changes default to LOCAL scope (1 strategy); global changes require EXPLICIT owner approval.** (Owner directive 2026-06-04 in response to B573 blast-radius lapse: "When making changes, the changes need to be applied locally to the current strategy only! If global, needs to be flagged by you and needs to be explicitly approved by me ... add to checklist as well.")

    **Rationale.** B573 changed `near()` global lambda in `backtest/signals/technical.py` from 0.003 -> 0.015 affecting 14 strategies, when the owner directive named only doji (2 strategies). Owner caught it: "Why have 14 strategies been affected? Should just be 2!" B574 fixed it by adding per-strategy `_wide` flag variants. The discipline rule is to never expand the blast radius beyond what the directive scopes.

    **Apply when:** every change at Stage 4 / Stage 5 / anywhere in the codebase that flows from a per-strategy directive.

    **How to apply:**
      a. **Default to LOCAL.** Modify only the named strategy. Use per-strategy variants, overrides, `_wide` flags, inline computation, or duplicated logic to keep blast radius at exactly 1.
      b. **If global is genuinely required:** STOP. Surface the blast radius EXPLICITLY in the response (not in a commit-message footnote): "This would also affect strategies X, Y, Z because they share <helper>." Wait for explicit owner approval naming the global change before applying.
      c. **Pre-flight format:** lead with "Local-only? [yes/no]. If no, blast radius: [list of affected items]. Requires global approval: [yes/no]."
      d. **What counts as global:** shared lambdas/functions, constants in config.py / CLAUDE.md / CANONICAL_FACTS.md, shared dicts/sets (DEPRECATED_STRATEGIES, STRATEGY_EXIT_OVERRIDE, etc.), producer signals consumed by >=2 strategies, trade_log schema columns.
      e. **Patterns:** per-strategy flag variants (`near_s1_wide` alongside `near_s1`), per-strategy override dicts (`STRATEGY_RSI_OVERRIDE[strat_name] = 35`), inline computation inside the predicate, duplicate-then-modify.

    **Joint:** `feedback_local_changes_default_global_needs_approval`, `feedback_narrow_scope_blast_radius`, `feedback_audit_recommendations_against_existing_directives`. Lapse history: B573 (caught by owner, fixed in B574).

105. **HARD RULE -- Stage 4 walks MUST read all associated scripts and docs end-to-end; surface every bug and issue, not a superficial review.** (Owner directive 2026-06-05 post-B603 news_momentum_long walk: "In the walk we intend to address bugs and All issues and not just do a superficial review. Read all associated scripts and docs! ... Add to checklist as well.")

    **Rationale.** B603 walked `news_momentum_long`. My Step 3 (Producer health) marked every signal "✅ live" without reading the producer source. The owner then asked a basic follow-up about how `news_sentiment_5d` and `news_volume_zscore_5d` are calculated — which required opening `backtest/signals/news_sentiment.py`. Doing that 5-minute read at WALK time would have surfaced:
      - the exact formula (recency-weighted mean with weight = 1 - age/5)
      - the Polygon `/v2/reference/news` endpoint dependency
      - the rule-based Loughran-McDonald fallback when Polygon sentiment is null
      - the 5d-count vs trailing-25d-baseline z-score (Cohen-Frazzini-Malloy)
      - the INV-027 history (multi-ticker per-ticker insights, RESOLVED 2026-05-08)

    Owner's correction: "Why wasnt this flagged by you in the walk?" — direct call-out that Step 3 was box-checking, not auditing. **Walks are an opportunity to ALSO surface producer-level bugs, schema gaps, OPEN_INVESTIGATIONS items, doc/code mismatches, silent-gap concerns, and any technical-debt items associated with the strategy.** Doing this at walk time is far cheaper than discovering it during cube post-mortem.

    **Apply when:** every Stage 4 / Stage 5 walk; every recommendation that touches a strategy that depends on a producer.

    **How to apply:**
      a. **Read the producer source end-to-end** for every signal the strategy consumes. Do not just confirm the signal name exists.
      b. **Surface the FORMULA**, not just the signal name, in the walk's Step 3 table.
      c. **Grep `OPEN_INVESTIGATIONS.md`** for the producer name + each signal name. Append matching entries (OPEN, RESOLVED, SUPERSEDED) to the walk's Step 3 as "Producer caveats".
      d. **Cross-check strategy-docstring claims against producer reality**: range, threshold, units, formula. Flag any mismatch.
      e. **Check the cache schema** (where applicable): is what the API returns actually persisted? Field-level coverage matches what the producer consumes?
      f. **Read related scripts** (`scripts/prefetch_*.py`, `scripts/build_*.py` for any signal that involves a prefetcher) to verify the data pipeline matches the strategy's assumptions.
      g. **Surface every issue found**, not just the gate-tweak proposals. Bugs / silent-gap risks / schema mismatches / doc drift get their own line in Step 7 (proposed tweaks) as "FIX" items distinct from "TIGHTEN" items.

    **Pre-flight format for Step 3:** "Producer files read end-to-end: [list of .py files]. OPEN_INVESTIGATIONS grep results: [list of INV-NNN matches]. Schema-vs-API checks: [field-level table]. Doc-vs-producer mismatches: [list or 'none found']."

    **Joint:** `feedback_walk_step3_must_read_producer_source`, `feedback_per_strategy_deep_dive_stage4`, `feedback_audit_recommendations_against_existing_directives`. Lapse history: B603 (caught by owner via "Why wasn't this flagged in the walk?", documented post-mortem in B604).

    **B611 EXTENSIONS (2026-06-07 external-AI critique post-B610):**

    a. **Step 3 sub-rule (signal temporality):** classify each consumed producer signal as EVENT (information bar-of-fire) vs STATE (slow background filter). Per `feedback_signal_temporality_event_vs_state`. Slow STATE signals (quarterly 13F, EMA-200 position, persistence counts) provide factor-tilt or universe filtering — NOT timing conviction. Step 4 (thesis check) MUST reject docstrings that credit STATE signals with "sponsorship", "conviction timing", "event confirmation".

    b. **Step 4 sub-rule (internal consistency):** Step 4 (thesis check) must be CONSISTENT with Step 5 (threshold inventory). If Step 5 lists a thesis-critical component as MISSING (e.g., "Bulkowski retest: ✅ ... volume gate: MISSING"), Step 4 must NOT endorse the thesis as ✅. Either implement the missing component as part of the walk OR surface as a name-vs-impl gap. No middle ground.

    c. **Step 6 sub-rule (asymmetric data check):** missing-inverse audit must include DATA-SOURCE SYMMETRY check. Per `feedback_asymmetric_data_sources_break_mechanical_inverse`. Asymmetric data sources (13F long-only, SC 13D activist-bias, insider buying asymmetric stats, short interest short-bias) break mechanical symmetry. Mechanical mirrors on asymmetric sources are economically false. Class 7 NEW proposals must include "DATA-SOURCE SYMMETRY: [yes/no, why]" line.

    d. **Step 7 sub-rule (NOT s.get pattern):** every SHORT-side gate using `not s.get(...)` is a FIX candidate. Per `feedback_never_use_NOT_s_get_pattern`. Always require positive symmetric signal; if it doesn't exist, ADD it to producer (B608/B609 F2 pattern). Default=True makes it functionally safe TODAY but the pattern is fragile.

    **B612 EXTENSIONS (2026-06-07 external-AI critique post-B608/B609/B610):**

    e. **Step 7 fire-count power-check before B603 routing.** Per `feedback_minimum_fire_count_gate_before_cube`. Multi-gate strategies must include a-priori fire-count projection before claiming "let the cube decide empirically." If projected fires/year < 30 (min_trades passing criterion per CLAUDE.md #9), cube can't produce statistically valid PASS/FAIL. Surface three resolutions: drop a gate, treat as exploratory, split into separate strategies.

    f. **Step 7 AVWAP family rule.** Per `feedback_avwap_redundant_with_ema_trend_filter`. AVWAP confluence is REDUNDANT with any EMA trend filter (collinear institutional-reference levels). Default-skip AVWAP when strategy already has any of: ema_*_bullish, price_above_ema_N, hull_bullish, supertrend_bullish, adx_trending. Only add AVWAP if no EMA trend gate present OR using event-anchored AVWAP (earnings day, swing low - not the rolling-window variants currently in producer).

    g. **Step 6 base-rate-asymmetry check.** Per `feedback_asymmetric_data_sources_break_mechanical_inverse` B612 extension. Even SYMMETRIC data sources have asymmetric statistical edges in equity markets. Equity upward drift (~6-8pct/yr) + short-squeeze tail risk degrade short-side expectancy. Step 6 missing-inverse audit must include: "Does SHORT have same expected edge as LONG given equity upward drift + short-squeeze asymmetry?" Structural `_strat3` symmetry in code != symmetric market expectancy.

    h. **Step 5 shared-producer-default sensitivity.** Retest tolerance (1.5*ATR), break tolerance (0.998 or 1.0pct), retest lag window (2-8 bars), pivot anchor choice - these shared-producer defaults often get marked "OK / honestly named" in Step 5 without width-vs-fire-quality calibration. Step 5 must explicitly state: "Sensitivity analysis: [done | deferred | n/a]" - and if deferred, note the gap as outstanding technical debt.

    i. **Step 7 multi-variable-change sequencing.** Per `feedback_sequence_or_split_when_stacking_changes`. When >=3 simultaneous changes on same direction of a dual strategy, surface "ATTRIBUTION CONCERN" with explicit resolutions: (1) sequence across walks, (2) split into separate strategies (SHORT goes to new Class 7 experimental variant), (3) accept attribution sacrifice explicitly in commit message.

    j. **Step 7 producer-additive blast-radius grep.** Per `feedback_never_use_NOT_s_get_pattern` B612 extension. When proposing a new producer signal addition, grep `not s.get("<inverse_signal>"` across screener.py BEFORE classifying as "additive/LOCAL." If consumers exist that rely on the bug-shaped auto-pass behavior, the addition silently changes their behavior - not LOCAL.

    k. **Step 7 fire-count pre-check is MANDATORY when net gates increase** per direction. Per B617 external-AI critique on B608 walk. Beyond the (e) ≥30/year cube-routing threshold, surface explicit a-priori fire-count projection ANY time a walk increases gate count per direction vs the pre-walk state — especially if a prior batch DELETED a gate (likely fire-count-driven loosening; re-tightening recreates the problem the deletion solved). The walk must explicitly compare pre- and post-walk gate counts AND reconcile against any prior deletion in the strategy's edit history. Format: "Pre-walk gate count: N; post-walk: M; net change: +K; prior batch B<NNN> deletion reason: <quote or 'not found in git log'>; projected fires/yr post-walk: <range>."

    **B625 codification (option E walk-template estimator integration):** the projection MUST be produced via `scripts/walk_preflight.py:walk_preflight_block()` (or `walk_preflight_one_line()` for commit messages) and the resulting `Fire-count projection:` token MUST appear in the walk commit message. Enforced by `test_batch625_walk_commit_fire_count_pin.py` which scans walk commits post-B625 + fails if any walk commit lacks the token. **Opt-out**: a walk commit can include `Fire-count projection: N/A - <reason>` for batches where the projection genuinely doesn't apply (e.g., deletion-only batches, docstring-only fixes). No more hand-derived format -- the helper produces it; the test enforces it.

    l. **Step 7 dimension-independence family rule (replaces "redundancy" catch-all).** Per B617 external-AI critique. AVWAP / OBV / MACD are NOT mutually redundant — they answer different questions: AVWAP is a price reference (is price above the volume-weighted average since an anchor); OBV is volume-flow (cumulative up/down volume); MACD is price-momentum. These are textbook NON-correlated confluence dimensions (Murphy/Elder). Family rule: skip-AVWAP requires positive justification ("already have EMA-trend filter" per (f)), NOT "OBV captures volume-flow." Skip-MACD requires positive justification, NOT "OBV trend semantics." If a family-rule skip rationale is reverse-engineered each walk, the rule itself isn't yet codified — codify or stop using "redundant" as cover.

    m. **Step 6 missing-inverse audit MUST include economic-symmetry check.** Per B617 external-AI critique. Structural symmetry (explicit positive symmetric signals exist for SHORT side after F2 silent-gap fix) does NOT imply symmetric expectancy. Equity markets have upward drift bias; squeeze asymmetry biases LONG; 13F/insider/SI are structurally long-side (already codified in `feedback_asymmetric_data_sources_break_mechanical_inverse`). Step 6 must explicitly comment on base-rate / drift / asymmetry-of-data-source BEFORE approving the symmetric mirror as the verdict. Allowed verdicts: (1) "structurally symmetric AND economically symmetric per <evidence>", (2) "structurally symmetric BUT economically asymmetric per <evidence>; SHORT side is exploratory" or (3) "asymmetric data source — no mirror considered per `feedback_asymmetric_data_sources_break_mechanical_inverse`."

    n. **Family-bug grep BEFORE individual one-line F1 removals.** Per B617 external-AI critique on B608/B609/B610 series. When fixing a regime-affinity (or other family-wide) bug on one strategy via a one-line removal in `STRATEGY_REGIME_AFFINITY` (or similar config), the same one-line fix is the wrong unit of action if the bug is a family signature. Before approving the individual F1 removal: grep the full map for the same pattern (e.g., all `_strat3` dual strategies with explicit single-direction regime entries; all strategies using the same producer; all walks that skipped the same gate with the same rationale). If 3+ instances surface, the right action is a bundled family audit, not 3 sequential one-liners.

    o. **Bulkowski `vol_below_avg` is CANONICAL for the retest family.** Per B619 family ruling codifying the de-facto practice across all 10 retest strategies (`strat_*_retest_*`, `strat_*_break_retest`). Bulkowski 2005 *Encyclopedia of Chart Patterns* is unambiguous: low volume on the retest bar IS part of the pattern definition (supply-absorption thesis). Any strategy in the retest family that cites Bulkowski as authority MUST carry `vol_below_avg`. Conversely, any walk that proposes to SKIP `vol_below_avg` on a retest-family strategy MUST drop the Bulkowski citation from the docstring + rationale — "over-tightening" is a fire-count argument (covered by (k)), not a Bulkowski argument. **Currently active members (audited B619):** strat_break_retest_volume, strat_break_retest_confluence, strat_flag_bull_retest_long, strat_flag_bear_retest_short, strat_52wh_break_retest, strat_52wl_break_retest_short, strat_r1_break_retest, strat_donchian_breakout_retest_long, strat_donchian_breakdown_retest_short, strat_volume_spike_breakout_retest -- all 10 carry `vol_below_avg`. The B617 critique #7 claim of inconsistency was a misread of letter-label mapping across walks (different walks used (c) vs (d) for the same gate); the actual code state is fully consistent. This rule LOCKS that consistency in for future walks.

    p. **1.5xATR(14) tolerance sensitivity scan is a Stage 5 cube task, NOT a walk-time decision.** Per B619 codifying the standing practice. The 1.5xATR retest tolerance is shared across `compute_break_retest_signals`, `compute_flag_break_retest_signals`, and several pivot/level proximity producers. Per-walk sensitivity testing requires multi-ATR cube replay infrastructure that doesn't yet exist; walks must mark the parameter "deferred -- see EXECUTION_QUEUE ATR-SENSITIVITY ticket" in Step 5 sensitivity row instead of attempting hand-tuning. The Stage 5 task: replay each retest strategy at multi-ATR settings (0.5x / 1.0x / 1.5x / 2.0x / 2.5x) across the cube + select the per-strategy tolerance that maximizes risk-adjusted return + fire-count joint criterion. Codified to stop the per-walk re-deriving with "honestly named not= calibrated" footnotes that don't lead to action.

    q. **Candle-pattern producers using close[-1] must verify engine entry path is next-bar open.** Per B637 strat_morning_star walk critique #3 (owner 2026-06-09). Candle-pattern producers (`morning_star`, `evening_star`, `three_white_soldiers`, `three_black_crows`, `bullish_engulfing`, `bearish_engulfing`, `shooting_star`, `hammer`, `pin_bar`, `doji_*`) define pattern conditions on bar -1 = today including dependencies on `close[-1]` — the current bar's close. Same-bar-close entry would be a fill you couldn't actually get (you only know the close at the close); entry must model `next_open`. **Current engine:** verified safe at `backtest/engine/backtest.py:1617` (`entry_price = next_open`). **Rule:** any future engine change that adds a same-bar-fill path for candle patterns, OR any new candle-pattern producer using `close[-1]` in its definition, MUST re-verify this property before merging. Category-specific PIT hazard not surfaced by the (i) staleness or (e) doc-vs-thesis rules; warrants its own first-class line item. Pyramid pin candidate: parameterized test asserting `close[-1]`-dependent candle producers fire only when engine model is next-bar-open.

    r. **Timeframe-mismatch check — intraday-by-design indicators applied to daily bars.** Per B640 external-AI audit C1 (owner 2026-06-09 directive #3). Floor-trader pivots (S1/S2/S3/R1/R2/R3, computed from yesterday's H/L/C and active only that session), Camarilla pivots (S1-S4/R1-R4, same daily-reset property), CPR (Central Pivot Range, India retail intraday system), opening range breakout (ORB, intraday by definition), and intraday VWAP are **intraday systems by design** — the defining property is that levels are recomputed each morning from the prior session and exist only for that day. Daily-bar application creates three failure modes: (1) the signaled level no longer exists at entry — `above_R1` computed from yesterday's bar means R1 has been replaced with a new R1 derived from today's bar by tomorrow's open, when entry actually happens; (2) the `near_X` 0.3% proximity band is the wrong size for daily ranges (1-3% typical) — fire-starvation may be caused by timeframe, not gate-stacking; (3) the thesis silently mutates — "breakout above R1 → continuation" requires R1 to be a persistent level the market remembers; it isn't on daily bars. **Rule:** any walk whose strategy uses an intraday-by-design indicator must surface in Step 2 (classify) whether daily-bar application preserves the thesis or requires REFRAME-AND-RENAME (drop the indicator-precision language; reframe as generic momentum/range signal). Reframe is preferred over reject when the underlying daily computation has standalone meaning (e.g. `above_cam_r4` = "today closed beyond an outsized prior-range projection" survives reframing as crude momentum). **Affected strategies (initial census, B641):** strat_pivot_s1/s2/s3_bounce, strat_pivot_r1/r2_continuation, strat_cpr_narrow_bullish, strat_camarilla_s3_bounce, strat_camarilla_r4_breakout, strat_prev_day_high_break, strat_orb_*. ORB family carries acknowledged-approximation footnote (technical.py:148-154). The B641 audit codified this rule but did NOT auto-reframe — each strategy needs per-walk owner-decision on reframe-vs-defer per CHECKLIST (g).

    s. **EVENT/STATE classification must produce a finding when timing rests on too few EVENT gates.** Per B640 external-AI audit methodology-finding #6 (owner 2026-06-09 directive #3). Step 3 already classifies each gate signal as EVENT (something happened on bar of fire — pattern formed, level crossed, volume spiked) vs STATE (a slow-moving regime/context — RSI level, EMA-cross-status, AVWAP-position, ADX-trending). The Foundations rule states: "Strategies should attribute timing alpha to EVENT signals, not STATE signals. A docstring that says 'X confirms the timing of Y' where Y is STATE is overclaiming." **Pre-B641 the classification was decorative** — performed in Step 3 + never wired to a Step 7 finding. **New rule:** Step 6 must explicitly count EVENT-gates per direction. If ≤1 EVENT gate per direction (entire timing-alpha rests on a single signal) AND the docstring uses words like "confirms / triggers / signals the timing of," surface as **F-timing-fragility: HIGH** -- the strategy is single-point-of-failure for timing AND the doc overclaims. If ≤1 EVENT gate per direction and docstring is honest (no timing-attribution claims for STATE gates), surface as **F-timing-fragility: LOW** -- design-only concern. The MACD-bullish-as-STATE-not-confirmation pattern (W6 silent concession in B640) is the canonical example: hist > 0 is a STATE that can be true for weeks, so a breakout strategy attributing "breakout confirmation" to it is overclaiming on the same axis as the B637 reversal-vs-continuation contradiction. **Affected B640 walks retroactively:** W2 has 1 EVENT gate (shooting_star) + 2 STATE (bb_touch, rsi); W8 has 1-2 EVENT (cpr_narrow setup-day-status + above_cpr cross) + 3 STATE. Both warrant F-timing-fragility flags in any future re-walk.

    u. **Class-7 NEW replacement crossing cluster boundaries must be walked in the NEW cluster BEFORE count-bookkeeping closes.** Per B713 SM cluster reviewer Part 5 + Decision 2 Group D #16 owner-approval (2026-06-12). When a strategy DELETE pairs with a Class-7 NEW replacement that lives in a DIFFERENT cluster than the deleted strategy, the replacement must complete a full CHECKLIST #105 7-step walk in its new cluster BEFORE the deletion's "net 0 = no count change" bookkeeping is allowed to close. **Motivating case (B713):** SM-9 / SM-23 deletions paired with Class-7 NEW pure-technical short replacements moved to `momentum_trend` cluster. The "+2 deletions / -2 Class-7 NEW = net 0" bookkeeping closed without walking the new entries in the momentum_trend cluster — substituting unwalked replacements for deleted strategies. Reviewer flagged as "tidy bookkeeping that hides discipline debt." **Rule:** any Class-7 NEW arising from a cross-cluster deletion-replacement must (1) complete CHECKLIST #105 7-step walk in the new cluster's living walk doc, AND (2) the deletion's count-bookkeeping commit must explicitly cite the walk commit URL or queue ticket ID as the (u)-rule unblock. **Retroactive application:** SM-9 / SM-23 momentum_trend replacements need walks in `STAGE_4_TREND_CLUSTER_WALKS.md` (or wherever the cluster lives) per `S4-B713-CLASS-7-REPLACEMENT-WALK-DISCIPLINE` queue ticket -- DEFERRED until B690 producers wired (allows the replacements' actual fire rates to be measured before walk).

    t. **Autonomous-batch (g)-waiver rule.** Per B665 2nd-wave-redux critique #5 (owner-approved 2026-06-09). When owner directs "implement remaining queue items autonomously" or similar bulk-clear instruction, the autonomous batch is NOT automatically (g)-exempt. Every autonomous batch must, at commit time, either: (1) **affirm independence** — explicit statement in commit message that no fixture sync was required across batches AND no shared producer changes were involved; OR (2) **request (g)-waiver** — explicit statement in commit message listing every test fixture synced + every shared file touched as the (g)-waiver justification; owner-approval recorded inline. (g)-waiver is auto-required when the autonomous bundle touches ≥3 strategies OR ≥2 producers (regardless of whether changes are independent in principle). **Motivating case:** B659 5-strategy autonomous bundle (W6 + W7 + W8 LONG default-True → False + W5m vol_below_avg + T3 SHORT below_ema_200) shipped without surfacing the (g)-waiver question; the follow-up commit `db2dda419` updated B645 + B656 test fixtures — direct evidence of test-level entanglement. The B659 retrospective is acknowledged as the motivating case in STAGE_4_PIVOT_CLUSTER_WALKS.md "B659 5-strategy autonomous bundle vs CHECKLIST (g) retrospective" section. Rule applies prospectively from B665 onward.

    Step 1.5 — restored: `_strat3` avoid-branch dead-code analysis. Per B637 morning_star walk + B640 external-AI audit methodology-finding #9 (owner 2026-06-09 directive #3). For every dual `_strat3` strategy, walk must verify whether `fl ∧ fs` is structurally possible (i.e. can both the LONG and SHORT gate-sets be satisfied simultaneously on the same bar). If mutually exclusive (e.g. morning_star ↔ evening_star can't co-occur; above_cpr ↔ below_cpr can't; above_r1 ↔ below_s1 can't), the avoid branch is dead code. Three consequences to record: (i) `_strat3` is being applied templately to strategies that don't need its 4-outcome resolver; (ii) if a future edit loosens any cross-gate to a range test, the dead branch silently activates with untested behavior; (iii) a one-line note in the strategy or a sibling helper `_strat3_exclusive` that asserts mutual exclusivity at runtime closes the latent hazard. **Affected B640 walks retroactively:** all candle dual walks (W1) + all pivot dual walks (W3/W4/W6/W7/W8/W9/W10) — the avoid branch is dead across all of them. Not a bug, but the per-walk check restores coverage that B640's bundle format dropped vs B637's single-strategy format.

    **Joint extensions (full B611+B612+B617+B619+B639+B641 set):** `feedback_signal_temporality_event_vs_state`, `feedback_asymmetric_data_sources_break_mechanical_inverse`, `feedback_never_use_NOT_s_get_pattern`, `feedback_minimum_fire_count_gate_before_cube`, `feedback_avwap_redundant_with_ema_trend_filter`, `feedback_sequence_or_split_when_stacking_changes`. Lapse history: B603 (producer-shallow Step 3); B608/B609/B610 (3 walks caught by 1st external-AI critique, fixed B611+B612); B608 itself (Bulkowski misread + OBV timing + Batch 271 family signature, caught by 2nd external-AI critique, fixed B617 -- k/l/m/n codified); B607 (3rd external-AI critique flag walk: parent phantom-breakout + PIT-discipline insurance, fixed B618 strategy fixes; o/p methodology rulings codified B619 to close family-rule open questions); B637 (strat_morning_star walk: thesis-vs-implementation reversal/continuation mismatch + dual SHORT-side duplication with standalone strategy + B271 family-bug signature on dual regime entry + RSI default-50 silent-gap class — fixed B639: option-2 reconciliation removed EMA gates + standalone deleted as redundant + regime entry deleted + F5 RSI-default ticket queued + q methodology rule codified); **B640 walk bundle (10 strategies candle+pivot cluster: external-AI audit landed methodology-level findings — fire-count independence assumption biased in both directions, CHECKLIST (g) applied inconsistently across W4/W6/W7, W8 vs W6/W7 default-True severity unification, W3 pin_bar direction-contamination, W10 Camarilla R3-as-breakout source-misuse with W9 same-level conflict, W5 no-reversal-confirmation knife-catch, OBV-vs-location tension, intraday-tool-on-daily-bar timeframe mismatch C1, multiple-testing/correlation/corporate-action/survivorship/cost C2-C6 program-level gaps, regime classifier 8-finding audit — fixed B641 Tier 1 ships W3 pin_bar fix + W4 F3-only + W8 F1+F1b + W10 R4-anchor rename; r/s methodology rules + Step 1.5 avoid-branch restore codified; 13 new tickets queued (fire-count measurement pass, multiple-testing, marginal-contribution, corp-action policy, survivorship verify, regime beta-assumption, AAII/FRED/sector PIT, composite fail-open, hysteresis parity, walk-forward classifier validation, W4 F1+RSI mislabel, W8 RSI noop, OBV-vs-location, W6/W7/W8 LONG default-True unify, fib anchor lookahead); B642 follow-on for regime classifier dead canonical line + EMA-cross hysteresis band; W5 reversal-confirmation redesign next turn).**

106. **HARD RULE -- TIER 2 producer audits must include TEMPORAL-COVERAGE + SCHEMA-CONTRACT probes, not just "file exists + has rows". File-glob heuristics fail silently when the producer reads a DIFFERENT path than the audit assumes OR when the data covers a WRONG TIME WINDOW OR when the schema lacks columns the producer requires.** (Owner directive 2026-06-13 B748c post-correction: *"These misses should not be happening. Referring to checklist is mandatory."*)
     a. Identify path by READING THE PRODUCER SOURCE (its actual `_CACHE_DIR` / `_EVENTS_PATH` / `_load_decoded(form, ticker)` etc.), not by registry hardcoded strings. The B745 audit had `index_rebalance_events.parquet` at `Backtesting universe/` when the producer reads from `data_prefetch/derived/` -- silently 0-rows.
     b. Recursive glob, not parent-only glob. SEC EDGAR is `data_prefetch/sec_edgar/<form>/<TICKER>.parquet` (per-form subdir); parent-only glob missed 11 form types × ~1700 files each.
     c. Temporal-coverage probe: assert (first_filing_date, last_filing_date) ⊇ measurement window [start, end]. The B748c investigation found `compute_persistence_signals` had data 2026-04-24 → 2026-05-05 (12 days) -- structurally cannot compute 4-quarter persistence; `compute_patentmomentum_signals` ends 2022-01-01 (4 years stale); `compute_corporatedonors_signals` has 9.5 months; SEC EDGAR SC_13D stale to 2024-12-16.
     d. Schema-contract probe: read consumer (strategy) code + assert producer parquet has every column required for the consumer's `s.get(<key>)` chain. `compute_news_sentiment_signals` produces `news_*` keys but the cached parquet schema is `[url, time, headline, category, summary, image]` -- no Ticker column means the per-ticker file lookup misses on every call. `compute_sec_edgar_signals` 8_K Item 1.01 detection needs `item_codes` column; parquet has only filing-index metadata.
     e. Runtime probe with KNOWN-EVENT (ticker, date) pair drawn FROM the data, not arbitrary. Smoke probe with random AAPL-2024-06-28 returns False on event-rare strategies; reading actual event rows from the parquet + probing within the event window distinguishes "no event" from "broken producer".
     f. CHECKLIST #44(b) MANDATORY: if smoke returns default/empty, INVESTIGATE WHY (schema mismatch, type mismatch, filter logic, silent except, path drift). Skipping (b) was the B745 audit failure mode. The B748b dispositions were wrong because (b) was skipped for 6 producers.
     g. Disposition discipline: a "data missing" verdict on a producer requires (a) + (b) + (c) + (d) + (e) ALL applied. Only when path is correctly identified, recursive scan complete, temporal-coverage tested, schema-contract verified, and runtime probe FROM the data returns empty -- THEN data is genuinely missing.
     h. Past failure history: **B745 (2026-06-13) classified `compute_sec_edgar_signals` as Path D / 0-data when SEC EDGAR data was actually present (1700+ files per form type × 11 form types) AND classified `compute_index_rebalance_signals` as Path B / 0-data when the events parquet was at `data_prefetch/derived/` with 357 rows.** B748b shipped 6 EXPLORATORY tags on this false premise. B748c walk-back (2026-06-13) REVIVED 5 strategies + ADDED 9 NEW EXPLORATORY for genuine temporal-coverage / schema-contract issues that B745 missed. Net: 1 of 6 B748b tags was correct (strat_m_and_a_target_long; 8_K item_codes column genuinely missing); 9 entirely new tags surfaced from rigorous extended probe.

107. **HARD RULE -- Pre-flight at END of each batch commit MUST enumerate findings-surfaced vs queue-tickets-filed; batch is NOT "shipped" until counts reconcile.** (Owner directive 2026-06-15 B765: *"add to the checklist at end of each batch commit, explicitly enumerate findings vs filed tickets before considering the batch 'shipped'."*)
     a. At end of each batch BEFORE the final `git commit + push` step: enumerate every distinct finding/observation surfaced this batch. Sources to scan: commit body draft, analysis stdout, new patterns introduced, cross-strategy concerns identified, empirical refutations of prior hypotheses, hypothesis re-classifications, hit-rate / fire-count / Sharpe surprises, edge cases in verdict-rules, regex coverage under-counts, KNOWN-EVENT probe failures, smoke-vs-demo divergences.
     b. For each finding, search `EXECUTION_QUEUE.md` for a corresponding `S4-BNNN-...` ticket entry. Match by topic, not exact wording. If NO ticket exists, FILE the ticket SAME batch (per CHECKLIST #94 + `feedback_execution_queue_mandatory_per_turn`).
     c. State the count reconciliation visibly in the commit message body: `Findings surfaced: N; Tickets filed: N; Audit-clean: YES.`
     d. Only after counts reconcile is the batch considered "shipped" -- the final commit + push.
     e. Annotation discipline for "shipped under existing ticket" cases: when a batch ships infra under an existing pre-existing ticket (e.g., B756 shipped TIER 1.1 fire-bar matrix under existing `S4-B755-COUNCIL-FIRE-BAR-SPARSE-MATRIX-PRECOMPUTE`), the existing ticket gets a `SHIPPED-BNNN` annotation AND the batch's commit message enumerates it as "Findings: 0 new tickets needed (shipped under existing #NN)". This makes the reconciliation explicit even when count is 0.
     f. Past failure history: **B762 audit (2026-06-15) found 6 missed tickets across B756-B761 batches** (signals_used convention inconsistency, KNOWN-EVENT probe failures, shooting_star/hammer always-False, verdict-rule OR-logic edge case, demo zero-pattern-W/J finding, demo-edge-prior-launch tracker). **B764 audit (2026-06-15) found 1 missed ticket from B763** (Pattern T audit under-count vs council expectation). Both were owner-prompted catch-up audits. This rule eliminates the need by making the audit a per-batch checklist item, not a periodic catch-up.
     g. Scope clarification: applies to ALL Stage 4 / Stage 5 batches that ship code, audits, scripts, or analysis. Pure doc-sync batches (per #67) without analysis findings can skip the reconciliation step but must state `Findings: 0; Audit-clean: YES (doc-sync only)` for visibility.

108. **SOFT-DISCIPLINE -- Gate-MODIFICATION justification per-turn (POST-walk on EXISTING strategies; NOT pre-registration of NEW strategies).** (Per B769 council F2 + B776 M3 memo `PROJECT_PRINCIPLES_M3_GATE_JUSTIFICATION_VS_NO_A_PRIORI_PRUNING.md` 3-scenario scoping resolution.)

     Every turn that ADDS, REMOVES, or REPLACES a gate on an EXISTING strategy must surface in the response BEFORE applying the change:
     a. **Conditional-return hypothesis** -- what regime/scenario does this gate help/hurt? cite per-regime expectation
     b. **Fire-count projection** -- post-modification fires/year per regime; flag if projection drops below `min_trades=30` per regime (per `feedback_minimum_fire_count_gate_before_cube.md`)
     c. **Validation plan** -- what cube cell / regime-conditional measurement confirms the hypothesis post-cube?
     d. **Literature or empirical precedent cited** -- Bulkowski / Nison / B358 / B654 / B655 / B663 / B722 etc.

     **NOT REQUIRED FOR** (the rule explicitly EXCLUDES these scenarios per M3 memo):
     - Class 7 NEW strategy initial wiring (no prior empirical history exists; per `feedback_wire_new_strategies_on_the_spot.md` ships same-turn)
     - Urgent silent-gap fixes (Pattern F default-True bugs; same-turn fix is mandatory)
     - Producer-side fixes (NaN handling, lookback init, gap-up open; not strategy gate changes)
     - Pure mechanical refactors (variable rename, function-signature change; behavior unchanged)
     - Pyramid-driven test fixes (codifying existing behavior, not modifying it)

     Compatible with: `feedback_no_a_priori_strategy_pruning.md` (Scenario 1 NEW strategy registration is explicitly excluded), cube-authoritative principle (validation plan defers final PASS/FAIL to cube cell), `feedback_minimum_fire_count_gate_before_cube.md` (fire-count projection is now a per-turn requirement for gate modifications, not just walks).

     **Past precedents that exemplify CORRECT application:**
     - B358 (2026-05-25): xs_low_beta_long 200-EMA gate REMOVAL -- cell-audit showed -6.22% loss in neutral regime; conditional-return evidence drove gate-removal
     - B654 (2026-06-09): W8 cpr_narrow_tight tightening 0.15 -> 0.05 -- 87% True ceiling-flag drove tightening; gate addition with fire-count projection
     - B655 (2026-06-09): T10 supertrend redundancy fix -- 99.19% True ceiling-flag drove State->Event conversion; B655 set the EVENT-conversion precedent
     - B663 (2026-06-09): default-True silent-gap sweep -- empirical evidence of silent-pass behavior drove gate removal
     - B722 (2026-06-12): Pattern W deterministic-duplicate deletions -- identical-gates evidence drove strategy-level removal
     - B772 (2026-06-15): Pattern Q EVENT-conversion on B-13 LONG with SHORT held STATE -- fire-count projection ~10x reduction would push SHORT below threshold; asymmetric application

     **Past failure history (gate-modifications shipped WITHOUT pre-flight, later flagged in review):**
     - B608/B609/B610 (2026-06-07): 3 sequential walks each removed `STRATEGY_REGIME_AFFINITY` entries as F1 fixes without family-bug grep; B611 external-AI critique flagged the pattern (40 dual strategies same Batch 271 mass-edit signature). Resolved via `feedback_family_bug_grep_before_one_liners.md` + CHECKLIST entry (n).
     - B573 (2026-06-04): global `near()` threshold change from 0.003 -> 0.015 affecting 14 strategies; owner requested 1.5pct for doji = 2 strategies. Resolved via `feedback_narrow_scope_blast_radius.md` + #108 makes per-strategy override explicit.

     This rule operationalizes B358's lesson as a per-turn checklist item without conflicting with the project's no-a-priori-pruning stance.

109. **CLASSIFICATION DISCIPLINE -- INSUFFICIENT_POWER tag distinct from EXPLORATORY.** (Per B755 council Advisor C + Reviewer 1 + B807 #5 codification 2026-06-16.)

     Two distinct tag classes for strategies that the cube cannot deliver a clear PASS/FAIL on:

     a. **EXPLORATORY** -- PRE-CUBE marker. Strategy has minimal or no empirical track record at the time of tagging.
        Examples: Class 7 NEW strategies tagged at registration; B-27/B-28/B-31 factor strategies tagged B787 per B786 #56 GATE FINAL FAIL_FIRE_STARVED; B-4/B-5 golden_cross_volume tagged B772 per B660 23/yr and 14/yr fire counts; B-18/B-19/B-20 chart-pattern shorts tagged B773 per chairman pragmatic-action verdict.
        Disposition: non-deletion runtime marker; cube still runs strategy; tag pre-registers FAIL expectation so cube failure is not misread as strategy-class failure.

     b. **INSUFFICIENT_POWER** -- POST-CUBE marker. Strategy has been cube-measured but the cell's effective-N is too small for the verdict to be statistically distinguishable from null.
        Canonical example: A-10 ultimate_oscillator Sharpe 0.49 at n=27. The 95% CI on a Sharpe estimate at n=27 is approximately [-0.3, 1.3] -- the CI spans null. The point estimate is favorable but the confidence interval cannot rule out edge=0.
        Disposition: SEPARATE class from EXPLORATORY. Strategy stays active per feedback_no_a_priori_strategy_pruning but cube cell is annotated INSUFFICIENT_POWER pending additional regime cycles or larger ticker sample.

     **Default classification gate** (when tagging a strategy):
     - n < 30 trades AND no cube cell yet -> EXPLORATORY
     - n < 50 trades AND cube cell exists AND 95% Sharpe CI spans 0 -> INSUFFICIENT_POWER
     - n >= 50 trades AND verdict is FAIL_CUBE -> standard FAIL_CUBE disposition (per existing pre-flight rules)
     - n >= 50 trades AND verdict is PASS_CUBE -> standard PASS_CUBE disposition

     This rule prevents two failure modes: (i) tagging cube-measured borderline strategies as EXPLORATORY (which is pre-cube semantically; conflates measurement-missing with measurement-power-limited); (ii) over-aggressive deletion of strategies with positive point estimate but wide CI (the data says we don't know yet).

110. **HARD RULE -- Per-turn enforcement gates MUST fire on every turn that ships code/docs. No exceptions.** (Owner directive 2026-06-18 Batch 892: "Updating the execution queue, following the checklist and updating the checklist if any misses is mandatory in each turn!")

     Pass 52 + Pass 53 already established #45 (per-response compliance statement), #94 (update EXECUTION_QUEUE every turn), #96 (show queue at end of turn), #95 (codify process gaps in CHECKLIST + LEARNINGS same turn). B892 owner directive ELEVATES these from "should comply" to "MUST fire -- non-compliance is a process failure of the turn itself, not a future-fix."

     **The 4 mandatory per-turn gates:**

     1. **Pre-flight CHECKLIST block visible** (#45 + #85) -- before EVERY recommendation. Not at end of response (post-hoc); BEFORE the recommendation is stated.
     2. **EXECUTION_QUEUE entry written this turn** (#94) -- every turn that ships code/docs adds a queue annotation. Standing rule per `feedback_execution_queue_mandatory_per_turn`. Past failure: B883-B891 all skipped this; owner flagged B892.
     3. **CHECKLIST update if gap surfaced** (#95) -- when a process miss is identified mid-turn, codify here SAME TURN. Past failure: I missed #94/#96 in B883-B891 batches; should have codified after first miss.
     4. **Show queue tail at end of turn** (#96) -- top 5-10 rows or current TIER entry. Visible confirmation the queue update landed.

     **Compliance check (single-question version):** at end of every turn that shipped code or docs, ask: "Did I write an EXECUTION_QUEUE entry, run CHECKLIST pre-flight, surface any process gap, and show the queue tail?" If any answer is no, the response is non-compliant per B892 owner directive.

     **Recovery protocol when miss is detected:** the FIRST batch after the miss must (a) acknowledge the lapse explicitly, (b) write the missing queue entries retroactively (one entry per skipped batch), (c) codify the prevention rule in CHECKLIST, (d) update LEARNINGS if a new lesson surfaced. B892 applies this protocol to B883-B891 cycle.

111. **HARD RULE -- Regenerated-Artifact Freshness Audit. Auto-generated docs must list every data source + refuse to claim "refreshed" if any source is stale.** (Council 18 Contrarian verdict 2026-06-18 B894; owner red-flagged STRATEGY_ROSTER rolling staleness across B874/B887/B889/B892.)

     Past failure pattern: Claude ran `python scripts/build_strategy_roster.py`, saw "Strategies: 219" output, assumed "fix worked" -- WITHOUT auditing whether the data sources feeding the regenerated columns were themselves stale. R4 cube fire status (May 31), approvals.json (pre-B722), s4_reviewed flags (pre-B585) all silently persisted as "current state" across 4 regeneration cycles. Owner flagged 3 times. Contrarian's diagnosis: **"confirmation by absence of error"** -- script ran, no exception, output mentions current count -> Claude concluded fix worked. This is pattern-match-without-verification, the exact failure mode #45 was built to prevent.

     **The 4 mandatory regeneration-audit gates:**

     1. **Enumerate every data source the generator reads.** For each: file path + last-modified date. List in commit message.
     2. **Compare each source's modified date to the most recent batch that should have invalidated it.** Example: STRATEGY_ROSTER reads `approvals.json`; last update was pre-B722; B722-B874 deleted 5 strategies; therefore approvals.json is STALE.
     3. **Refuse to claim "refreshed" if ANY source is stale.** Instead report: "regenerated against stale source X as-of DATE; columns Y/Z reflect stale data." This is the cube-cells-are-measurements-not-changes principle applied to derived docs.
     4. **Either SCRUB the stale-source columns from output OR add prominent (table-header level, not footnote) "as-of DATE (stale)" disclaimers.** Scrub is preferred per Council 18 Contrarian: "anything that lies is worse than absent."

     **Compliance check (single-question version):** After regenerating any auto-generated artifact (doc, dashboard, CSV, JSON), ask: "Did I list every data source the generator reads, compare each to the most recent invalidating batch, and either scrub or disclaim stale-source columns?" If any answer is no, the regeneration is non-compliant per B894 owner directive.

     **Build-time invariant assertion (preferred):** Add `assert` statements in generator scripts that fail loudly if a deleted column tries to come back without a fresh data source. Example: `assert "QUIET" not in out_text, "B894 SCRUB violated: stale R4 cube fire-status column reappeared"`.

     **Meta-pattern surfaced (Council 18):** Past failures have a common shape -- Claude frames the task as MECHANICAL ("regenerate roster") instead of VERIFICATION-BEARING ("deliver a current roster to owner"). The pre-flight (#45) didn't fire because "regenerate" feels like a mechanical step. Fix: any task involving a `python scripts/...py` regeneration is verification-bearing by default, and pre-flight must enumerate data-source freshness before claiming success.

     **Recovery protocol when staleness detected by owner:** the FIRST batch after the owner flag must (a) acknowledge the rolling-staleness pattern, (b) enumerate every data source and its as-of date, (c) scrub stale-source columns OR add prominent disclaimers, (d) codify a build-time assertion preventing return, (e) update LEARNINGS with the meta-pattern.

112. **HARD RULE -- Refuse the heroic-batch trap. When owner asks for ALL-N updates, ship K with evidence + DEFER N-K explicitly with reasons.** (Council 19 Contrarian verdict 2026-06-18 B895; multi-front directive after B894 RED FLAG.)

     Owner directive pattern: "Update ALL md files. Do not miss any. Council this. Be comprehensive."

     The trap: attempt all N items in one batch, ship a heroic-looking commit, declare victory. **This is the B894 failure pattern with a new mask.** If you "update ALL 175 MD files" in one batch, you will pattern-match-replace strategy counts without auditing whether each file's surrounding paragraph is still semantically true. That is identical to the staleness lapse owner just red-flagged -- different surface, same crime.

     **The 4 mandatory scope-discipline gates:**

     1. **Enumerate scope honestly.** Count actual items (e.g., 175 .md files; 25+ with potential drift; 5 NEW scripts; multi-batch wired-implemented audit).
     2. **Compute irreducible time.** Realistic budget per item (e.g., ~3 min freshness audit per .md = 9 hours total). If irreducible > one batch, the answer is NOT to compress; it's to stage.
     3. **Ship the irreducible minimum THIS turn with EVIDENCE.** Grep output. Live-source verification. Visible audit trail. Not "all" -- "K with proof."
     4. **DEFER explicitly with reasons in EXECUTION_QUEUE.** Each deferred item gets a ticket: `B89N-DEFER-X: [item] -- deferred because [resource constraint]; will ship [batch range]`. Silent skipping is non-compliant per #110.

     **Compliance check (single-question version):** Before claiming "comprehensive" or "all" or "everything", ask: "Can I quote the grep output that proves this claim for EACH item I claim to have addressed?" If no, the claim is the B894 pattern. Demote to "K items with evidence + N-K deferred to [batches]."

     **Owner expectation calibration:** Owner asking for "comprehensive" is asking for COMPLETE COVERAGE, not COMPLETE-IN-ONE-BATCH. Completing coverage across multiple batches with explicit deferral tickets HONORS the directive better than one batch of unverified claims. Past failure: B892 + B894 -- I tried to "update STRATEGY_ROSTER" in one batch and missed data-source staleness. Three iterations later it's still being flagged.

     **Recovery protocol when owner red-flags heroic-batch overpromise:** the FIRST batch after the lapse must (a) acknowledge the trap, (b) re-scope honestly with deferral tickets, (c) ship the verifiable subset, (d) codify the prevention rule (this rule), (e) update LEARNINGS with the meta-pattern. B895 applies this protocol to "update ALL md files" directive.

113. **HARD RULE -- ETA estimates for long-running jobs must account for cache invalidation since the last successful run. Re-estimate or measure pilot before launching multi-hour jobs.** (B896 lesson 2026-06-18; B660 v2 / B885 delta launch overran ETA by 80-150x.)

     B885 launched B660 v2 delta on 20 strategies with stated ETA "~45-90 min remaining." Actual measured behavior at 12.2h elapsed: signal precompute at 50/606 tickers = 8.3% with script-emitted ETA 482,344s = 134h = 5.6 DAYS remaining. **Overrun factor: 80-150x** of original estimate.

     **Root cause:** B885 estimator assumed signal cache would be RECYCLABLE from B660 v1. Between B660 v1 (June 11) and B885 v2 launch (June 17), the following invalidated the cache:
     - B689 EXTENDED signals added (TIER 1 chart_patterns + smc + ict + multi_timeframe + volume_profile + TIER 3 cross_asset + calendar + pre_fomc + 7 COT series)
     - B776 TIER 2 cross_sectional panel build (7.5h alone)
     - B781 universe expansion (T1a -> T1a + T2 + T3 + SPY = 606 -> 1877 tickers)

     **The 3 mandatory pre-launch gates for any long-running job (>30 min):**

     1. **Enumerate intervening changes since last successful run.** grep `git log <last-run-batch>..HEAD --oneline` for cache-impacting batches. Each B-prefix in the impacted-files set INVALIDATES cache.
     2. **Run a pilot at 1% scope BEFORE launching at full scope.** For B885 v2: should have run measure_fire_count.py on 1 strategy + 10 tickers first (~3 min budget); the per-ticker time would have surfaced the 50h precompute cost immediately.
     3. **Re-estimate via pilot * scaling factor + cache-rebuild overhead.** Pilot per-ticker time (~5 min) * 606 tickers = 50.5h JUST for precompute. Plus 7.5h TIER 2 panel build. Plus strategy evaluation. Honest ETA at launch should have been ~60h, not 45-90 min.

     **Compliance check (single-question version):** Before launching any background job estimated >30 min, ask: "Have I (a) checked git log for cache-invalidating batches since last successful run, (b) run a 1% pilot to measure actual per-unit time, (c) recomputed ETA from pilot * scaling, NOT trusted prior-run timing?" If any answer is no, the launch is non-compliant.

     **Recovery protocol when ETA overrun >5x detected:** the FIRST batch after detection must (a) KILL the job (not "let it finish"), (b) honestly diagnose root cause in EXECUTION_QUEUE entry, (c) decide between rescope/restart/skip based on critical-path analysis, (d) codify the cache-invalidation enumerator (this rule). B896 applies this protocol to B885 v2 -> B660 v2 lapse.

114. **HARD RULE -- Autonomous mode STOP conditions: 10 mandatory owner pings + green-light path for cheap/reversible work.** (Owner directive 2026-06-18 B907: "Continue autonomously unless explicit input needed from me." Council 29 codification.)

     Owner directive: skip "continue" / "council this" friction on per-turn cadence. Council 29 4-advisor synthesis: "Autonomous mode eliminates ACKNOWLEDGMENT FRICTION, not JUDGMENT GATES."

     **MANDATORY owner-ping STOP conditions (10 items):**

     1. Any AWS / API spend ($) -- even $1 (per CLAUDE.md L86/L95 $150-pattern warning; small-test -> manual review -> approval -> scale)
     2. Any change to PASSING_CRITERIA / canonical thresholds (DEC-611/612/613/614 owner-mandated)
     3. Any strategy deletion (per `feedback_no_a_priori_strategy_pruning`)
     4. Pyramid not GREEN -- ANY pyramid run with > 0 failing tests is a stop until investigated
     5. Any long-running job projected > 2h without per-CHECKLIST #113 pilot first (e.g., B660 v2 / measure_fire_count.py full runs)
     6. Any reversal of a prior-turn decision (per `feedback_audit_recommendations_against_existing_directives`)
     7. Scope expansion > 2x planned blast radius mid-turn
     8. B895-DEFER-A tranche touching CLAUDE.md / PROJECT_PLAN.md / DETAILED_PROJECT_PLAN.md / canonical docs
     9. Council 28-class methodology change (taxonomy creation, gate semantics, verdict logic, DEC-class additions)
     10. Any DEC closure requiring owner sign-off per CHECKLIST #45

     **AUTONOMOUS GREEN-LIGHT PATH (per-turn rhythm):**
     - Pre-flight CHECKLIST visible (per #45/#85)
     - Council if SUBSTANTIVE scope/methodology decision (Council 28 precedent: every taxonomy creation; every defer-vs-execute; every walk-back protection check)
     - Execute -- ONE DEFER ticket per turn typical (max 2 if mechanically trivial); no batches > 5
     - Pyramid sample (smoke tests on touched files; full pyramid only when shipping engine changes)
     - Commit + push per `feedback_standing_approvals`
     - EXECUTION_QUEUE update + queue tail (#94 + #96)
     - **STOP check** -- review 10 conditions above; if any triggered, surface to owner explicitly + HALT until owner pings

     **Information-value framing (First Principles Council 29):** owner-pings have two purposes: (1) catch reversible mistakes before irreversible, (2) authorize irreversibly-costly actions. Autonomous mode waives (1) for LOW-STAKES REVERSIBLE work; does NOT waive (2). The expensive irreversible work is where to SLOW DOWN, not speed up.

     **Council frequency cadence:** ~1 council per 3-5 batches when work is mechanical (DEFER drain, queue hygiene, doc-sync); ~1 per batch when methodology is in play (taxonomy / verdict change / class-7 NEW / walk-back).

     **Past failure pattern this prevents:** L86 + L95 $150 wasted on full API run without small-test gate; B660 v2 12.2h sunk on unverified ETA; heroic-batch trap on autonomous mode without explicit STOP conditions.

     **First application:** B907 PILOT (Option B per Council 29) + B908 R5 HALT pending explicit $-approval.

     **R5 STOP #1 REINFORCEMENT (owner directive 2026-06-19 B911):** R5 launch is BLOCKED until **explicit owner mention** of "launch R5" or equivalent verbal go-directive. This is stricter than prior Dec-4(b) "after Dec 5 + pyramid GREEN" gate-clearance interpretation. **Even if Dec 5 + pyramid GREEN both clear, R5 does NOT auto-launch** -- requires explicit owner GO directive. Apply same rule pattern to any subsequent AWS-spend cube runs (R5.1, R5.2, etc.) until owner removes this constraint. Per-turn STOP #1 check must verify: did owner explicitly say "launch R5" THIS session? If no, R5 stays HALT regardless of other technical gates.

115. **HARD RULE -- Council MUST ENUMERATE options + RECOMMEND final choice. BOTH required.** (Owner directive 2026-06-21 B969: "Council this. Approve council recommendations. Council is supposed to enumerate and provide final recommendation. Both are needed. Ensure compliance going forward.")

     Council outputs must end with TWO sections (not one):

     1. **OPTIONS ENUMERATED:** numbered/labeled set of considered options (alpha/beta/gamma/delta OR A/B/C/D OR named per context). Show the full search space the council considered. Bare list acceptable; no need to argue each in conclusion if reasoning was shown per-advisor above.
     2. **RECOMMEND: [ONE CHOICE].** Single recommendation extracted from the option set with explicit justification. Format: `RECOMMEND: [option name + brief justification]. Awaiting owner approval.`

     **Workflow:** council recommends -> owner approves OR redirects to a specific alternative from the enumerated options OR counter-proposes new option. Claude executes on approval.

     **Anti-patterns to reject:**
     - "OWNER DECISION REQUIRED: pick A/B/C/D" (enumeration-only; council punts the decision)
     - "RECOMMEND: X" without enumerating what was considered (recommendation-only; owner cannot see what was rejected and why)
     - "Council split; owner picks" (council MUST converge unless escalation to 5-advisor or owner override needed)

     **Past failure pattern:** Council 69 (2026-06-21) ended with `OWNER DECISION REQUIRED A/B/C/D/E/F` enumeration without final pick. Owner corrected: council must give final recommendation. Council 70 (same turn) recovered with single final rec, but did not enumerate the considered options. Owner B969 clarification: BOTH parts needed. Council 71 (B969) ships the corrected format.

     **Compliance check (single-question version):** At end of every council output, ask: "Did I enumerate the options considered AND give one final recommendation?" If either is missing, the council output is non-compliant per B969 owner directive.

     **Recovery protocol when miss detected by owner:** the FIRST council after the lapse must (a) acknowledge format failure, (b) re-issue prior council with proper enumerate+recommend format, (c) codify rule (this entry), (d) update LEARNINGS if new meta-pattern surfaced. B969 applies this protocol to Council 69 -> Council 70 -> Council 71 chain.

     **Edge case -- 5+ option search space:** when enumeration would be unwieldy (10+ options), council MAY group into 3-4 strategic clusters with one representative per cluster, then recommend the cluster-winner. Document the clustering in the enumeration section so owner sees the compression rationale.

116. **HARD RULE -- AWS EC2 user-data 16KB limit applies AFTER base64 encoding.** (B1028 R5 launch session 2026-06-27; Council 124 Tier 1.)

     **Pre-flight check BEFORE every AWS EC2 launch:**
     ```bash
     RAW=$(wc -c < user_data.sh)
     B64=$(base64 -w0 user_data.sh | wc -c)
     ```
     If `RAW > 12000` OR `B64 > 16000`: STOP. Externalize large constants (ticker lists, config blobs, embedded data) to S3 + use `aws s3 cp s3://... -` fetch-at-bootstrap pattern in user-data.

     **Why HARD rule:** B1028 first attempt failed with `InvalidParameterValue: User data is limited to 16384 bytes`. Raw was 12,740 bytes (under 16 KB raw) but `base64 -w0` produced 16,988 bytes (over 16 KB encoded). Required emergency externalization mid-launch. Base64 expansion is ~33% per RFC 4648; any user-data approaching 12 KB raw is at risk.

     **Externalization pattern (proven B1028):** Upload large data to S3 (e.g., `s3://bucket/run-id/master_ops_tickers.txt`) BEFORE launch. User-data fetches with `aws s3 cp s3://${BUCKET}/${RUN_ID}/master_ops_tickers.txt /tmp/master_ops_tickers.txt --quiet`. Final B1028 raw = 4,117 bytes / base64 = 5,492 bytes. Under all limits.

     **Cross-references.** L166, `feedback_aws_user_data_size_preflight`, B1028 R5 launch (corrected version).

117. **HARD RULE -- Monitor tool timing must match async-AWS / cube wall-clock; arm AT event boundary not pre-launch.** (B1019-B1024 session 2026-06-27; Council 124 Tier 1.)

     **Three rules:**

     1. **Arm AT the event:** wait until you have confirmation upstream event is in flight (instance state = running OR first S3 sentinel lands) BEFORE arming Monitor. Premature arming wastes timeout window on bootstrap delay.

     2. **Match timeout to wall-clock x 1.5 buffer:** if cube run estimate is 4 hr, Monitor `timeout_ms` >= 6 hr (21,600,000 ms). The default 1hr (3,600,000 ms) only matches small ops.

     3. **Use `persistent: true` for long-running cascades:** for cube runs > 2hr, set `persistent: true` (session-length watch) instead of `timeout_ms`. Stop via TaskStop when work completes.

     **Why HARD rule:** Across session B1019-B1028 multiple Monitor armaments failed: B1021 pre-launch (expired 1hr later before B1024 instance launched), B1024 retry (expired during 3-day pyramid), R5 wait (multiple re-arms). The default timeout was designed for small ops; AWS bootstrap (5-15 min) + cube wall-clock (3-6 hr) operate on different time scales.

     **Cross-references.** L167, `feedback_monitor_arm_at_event_not_pre_launch`, `feedback_monitor_intermediate_counts` (B358 complementary).

118. **HARD RULE -- Per-strategy lint sub-pyramid runs same-turn as Class 7 NEW_STRATEGY wire.** (B1010 borrow-gate omission session 2026-06-27; Council 124 Tier 1.)

     When wiring a Class 7 NEW_STRATEGY same-turn (per `feedback_wire_new_strategies_on_the_spot`), run category-specific lint sub-pyramid BEFORE end-of-turn — not just `test_unit + test_integration` baseline.

     **Category-specific lint tests (required additions beyond baseline):**
     - SHORT strategies → `test_batch744_borrow_gate_lint.py` (catches missing `_short_borrow_trap_active()` gates)
     - Signal-consumer strategies → `test_silent_gap_pyramid.py` (catches signal-orphan + missing-producer)
     - STATE-vs-EVENT classification → relevant temporal coverage tests
     - Class 7 NEW (any) → relevant family-specific lints

     **Pre-commit verification:** Before commit, confirm category-specific lint test was IN the focused subset. If not → run it standalone → fix any drift BEFORE commit.

     **Why HARD rule:** B1010 added `strat_insider_cluster_concentrated_sell_short` (Class 7 NEW SHORT). Focused pyramid for ship verification (test_unit + test_integration + B1009 + B970 + count-pin) was GREEN but did NOT include `test_batch744_borrow_gate_lint.py`. B1010 shipped without the `_short_borrow_trap_active()` gate. Caught 3 days later (B1014 honest-finding pivot #14) when full 13-tier pyramid completed.

     **Cross-references.** L168, `feedback_per_strategy_gate_audit_at_wire_time`, `feedback_wire_new_strategies_on_the_spot`, B1014 retrofit.

119. **HARD RULE -- Verify Council verdict dependencies BEFORE execute; document honest-finding pivot if uncertain.** (B1026 Council 116 Option-A pivot session 2026-06-27; Council 124 Tier 1.)

     When Council verdict has prerequisite (IAM perm / cache state / file presence / AMI ready / quota), verify dependency BEFORE execute. If dependency UNVERIFIABLE, document honest-finding pivot and execute fallback option.

     **Three-step protocol:**

     1. **Identify dependency list during Council brief:** Council briefing must enumerate prerequisites explicitly (IAM perms / cache state / AMI availability / quota / file presence / external service status).

     2. **Pre-execute dependency verification:**
        - IAM: `aws iam get-role-policy ...` OR `--dry-run` test of intended action
        - Cache: `aws s3 ls` / `wc -l` / file existence check
        - AMI: `aws ec2 describe-images` for state=available
        - Quota: `aws service-quotas get-service-quota` OR equivalent

     3. **If dependency UNVERIFIABLE:** document honest-finding pivot per Council 76 banner-verification precedent. Pivot to fallback option with documented rationale. Do NOT blindly execute against unknown dependency state.

     **Why HARD rule:** Council 116 RECOMMENDED Option-B CASCADING for B1026. Required `batch395-instance-role` IAM to have `ec2:RunInstances` perm — unverifiable in real-time without burning AWS quota. Claude PIVOTED to Option-A SINGLE-LARGE-INSTANCE per simpler-is-safer reasoning (honest-finding pivot #16 in B1026 commit). Pattern worked; codifying for future use.

     **Cross-references.** L169, `feedback_verify_council_verdict_dependencies_pre_execute`, `feedback_audit_recommendations_against_existing_directives`, Council 76 banner-verification precedent.

120. **HARD RULE -- Ask before relaunching corrected version after HALT.** (B1027 T1a auto-relaunch session 2026-06-27; Council 124 Tier 1.)

     After HALT triggered by owner question OR auto-detected scope-issue, do NOT auto-relaunch corrected version. Surface correction + ask explicit owner approval BEFORE re-launch. Even small re-launches ($0.10-$1.00 range) compound under L86/L95.

     **Post-HALT correction protocol:**

     1. **If HALT was triggered by owner question:** surface corrected interpretation + ask explicit owner approval BEFORE re-launch. Owner question is the verification signal — honor it.

     2. **If HALT was triggered by auto-detected issue:** surface auto-correction + estimated cost + brief Council on corrected scope. Wait for owner ACK before re-launch.

     3. **DO NOT auto-launch corrected version on assumption Council got it right second time.** Council artifact chain CAN propagate wrong assumptions (per L164 + #109).

     4. **Cost-discipline rationale:** Even small re-launches compound. B1024 + B1026 + B1027 = $1.41 cumulative sunk — all auto-relaunched after partial corrections without owner ACK. Single owner-confirmation step would have saved $0.10 - $1.05.

     **Why HARD rule:** B1026 → B1027 sequence:
     - B1026 launched on Master-wrong S3-ls universe (pivot #17)
     - Owner asked "what is the universe for r5?"
     - Council 117 corrected to T1a 503
     - Claude IMMEDIATELY launched B1027 T1a-corrected
     - Owner replied "Dont we need r5 on full master list?"
     - Claude HALTED B1027 (~$0.10 wasted)
     - Council 119/120/121 reconciled to Master 1937 per PROJECT_PLAN
     - B1028 finally launched correctly

     Owner's first question was the verification signal; the second question caught Council 117's wrong T1a verdict BEFORE the $0.10 launch.

     **Cross-references.** L170, `feedback_ask_before_relaunching_corrected_version`, `feedback_audit_recommendations_against_existing_directives`, L86/L95 cost discipline precedent.

121. **HARD RULE -- MONITOR-ARMED-IN-USER-DATA pre-launch verification.** (B1028 R5 launch failure 2026-06-27; Council 126 Tier 1.)

     Pre-launch verification gate for any cube / long-running / autonomous AWS execution MUST include explicit check that monitor is operationally armed in user-data, not just present in repo.

     **Verification command:**
     ```bash
     grep -q "b1019_phase_1_runtime_monitor" user-data.sh && echo ARMED || { echo MONITOR-MISSING; exit 1; }
     ```

     If MONITOR-MISSING, FAIL launch. Do NOT proceed without monitor.

     **Why HARD rule:** B1028 R5 launch (i-0940a53c75d049381) ran engine via `python -m backtest.run_phase1a` DIRECTLY without wrapping in B1019 runtime monitor. Result: once Phase 1 RUNNING sentinel emitted, system went BLIND for 1h 38m until owner asked "Has phase 1 landed?" Owner's correction: "If the monitor is armed, why is it being flagged after owner enquiry? Such instances are the exact purpose of the monitor."

     The B1019 Monitor package was DESIGNED by Council 108. The artifact existed in `scripts/`. The integration didn't happen in B1028 user-data. Verification gates (Council 110 / 114 / 119 / 121) checked AMI / S3 / IAM / spot price / DRY-RUN / universe scope — but NEVER asked "is the monitor operationally armed?"

     **Both armament types are required (neither alone is sufficient):**
     - **User-data monitor** (writes engine progress to S3 every 60s)
     - **Bash Monitor tool** (tails the S3-synced log + emits chat notifications)

     **Verification checklist:** every "monitor armed" claim requires (a) grep proof in user-data, (b) S3 path where monitor writes, (c) Claude-side Monitor tool armed on local mirror.

     **Cross-references.** L176, `feedback_monitor_design_vs_operational_gap`, `feedback_monitor_arm_at_event_not_pre_launch` (#117 companion: when to arm), B1028 failure.

122. **HARD RULE -- SILENT-FAILURE-PAIRING: every `|| true` requires paired explicit verification step.** (B1028 pandas-ta silent failure session 2026-06-27; Council 126 Tier 1.)

     Every `|| true` / `|| :` / `|| echo` in user-data or shell scripts MUST be paired with an explicit success-verification step within 10 lines.

     **Pattern (WRONG vs RIGHT):**
     ```bash
     # WRONG
     pip install -q pandas-ta 2>&1 | tail -3 || true
     # (failure swallowed; downstream code assumes pandas-ta present)

     # RIGHT
     pip install -q pandas-ta 2>&1 | tail -3 || true
     python -c "import pandas_ta" || { echo "FAIL pandas-ta missing"; exit 1; }
     ```

     **Rules per dep type:**
     - **Mandatory deps:** NO `|| true`. Use `set -e` + explicit error + exit. Fail loud.
     - **Optional deps:** `|| true` OK but pair with verification + downstream branch:
       ```bash
       pip install -q optional-dep || true
       python -c "import optional_dep" 2>/dev/null && HAS_OPTIONAL=1 || HAS_OPTIONAL=0
       echo "optional-dep available: $HAS_OPTIONAL" >> /tmp/sentinels/dep_status
       aws s3 cp /tmp/sentinels/dep_status s3://${BUCKET}/${RUN_ID}/dep_status
       ```

     **Audit pre-launch:** `grep -nE '\|\| (true|:|echo)' user-data.sh` — every match must have a paired verification within 10 lines.

     **Why HARD rule:** B1028 user-data had `pip install -q pandas-ta ... || true`. The pandas-ta install FAILED (Python 3.13 incompat). Engine then ran with pandas-ta MISSING. Engine fell back to manual implementations per `backtest/signals/technical.py` docstring, but specific strategy signals that depend on pandas-ta may have hung or returned wrong values. Contributed to Phase 1 hanging at <5% CPU.

     **Cross-references.** L176, `feedback_silent_failure_pairing_rule`, B1028 pandas-ta failure.

123. **HARD RULE -- PHASE-LADDER-TIMING-VALIDATION: smoke wall-clock target ≤ 15 min.** (B1028 R5 timing assumption failure 2026-06-27; Council 126 Tier 1.)

     Smoke / Phase-1 wall-clock estimates must be EMPIRICALLY VALIDATED before cascade approval. If smoke phase estimate exceeds 15 min, cascade automation is invalid until calibrated.

     **Smoke timing rules:**

     1. **Smoke wall-clock target ≤ 15 min**: if Phase 1 (single ticker, smallest dimension) estimate exceeds 15 min, engine is too slow for cascade automation. Identify bottleneck FIRST.

     2. **If estimate > 15 min, validate before cascade**: run smoke STANDALONE (not cascaded into multi-phase). Measure actual wall-clock. Update estimate. Re-decide cascade approval.

     3. **If smoke runs > 2× estimate, HALT cascade**: per `feedback_monitor_intermediate_counts` B358 ABORT-EARLY pattern. Smoke is the calibration; if calibration fails, cascade is invalid.

     4. **For NEW engine / NEW infrastructure / NEW ticker count**: run smoke first time MANUALLY (not in cascade). Establish timing baseline. THEN automate.

     **Why HARD rule:** B1028 cascaded Phase 1 → Phase 2 → Phase 3 → R5 based on assumed 30-min Phase 1 NVDA timing. Actual Phase 1 hung; cascade never started Phase 2. $2 sunk. Smoke standalone would have caught this in 1h 38m with no cascade commitment.

     **Cross-references.** L176, `feedback_phase_ladder_timing_validation`, `feedback_monitor_intermediate_counts` (B358 2× threshold), CHECKLIST #113 (ETA cache invalidation).

124. **HARD RULE -- IAM-SSM-PRECONDITION: SSM access verified on instance role before launch.** (B1028 SSM-blocked mid-run inspection 2026-06-27; Council 126 Tier 1.)

     SSM access must be verified on instance IAM role BEFORE launching long-running cube / autonomous AWS execution. SSM access enables mid-run inspection via SSM Run Command without needing SSH access.

     **Pre-launch verification:**
     ```bash
     # Verify role has AmazonSSMManagedInstanceCore policy attached
     aws iam list-attached-role-policies --role-name batch395-instance-role \
       --query 'AttachedPolicies[?PolicyName==`AmazonSSMManagedInstanceCore`]' --output text
     # If empty: ATTACH policy before launch
     ```

     **Mid-run inspection capability:**
     ```bash
     # If SSM enabled, can inspect engine state without SSH
     aws ssm send-command --instance-ids i-XXXX \
       --document-name "AWS-RunShellScript" \
       --parameters 'commands=["ps -ef | grep python", "tail -50 /home/ec2-user/stock-picks-app/output_phase_1/phase_1_engine.log"]'
     ```

     **Why HARD rule:** B1028 instance i-0940a53c75d049381 console showed "SSM Agent unable to acquire credentials: Systems Manager's instance management role is not configured for account: 739685920493". When CPU dropped to <5% sustained, Claude could NOT use SSM to inspect engine state — only console output (cut at 180s) was available. Result: no forensic data on why engine was hung. HALT decision had to be made blind.

     **Cross-references.** L176, B1028 SSM-blocked forensics, related to #121 (monitor armament) and #117 (monitor timing).

125. **HARD RULE -- ENGINE-PROGRESS-EMIT: engine must emit per-checkpoint progress to S3.** (B1028 invisible engine state 2026-06-27; Council 126 Tier 1.)

     Engine MUST emit per-checkpoint progress to S3 mid-run, not just memory-internal checkpoints.

     **Engine state requirements:**

     1. **Per-checkpoint progress sentinel**: every 100 simulated days, emit `engine_progress.json` to S3 with:
        - Current simulated day
        - Cumulative trades
        - Cumulative win-rate
        - Per-strategy fire counts (top 10)
        - Memory RSS
        - Wall-clock elapsed
        - ETA projection

     2. **60s S3 sync of engine log**: background process syncs `engine.log` to S3 every 60s. Allows Claude-side Monitor to tail it.

     3. **STOP-S3 sentinel check**: if any STOP-S3 critical signal (NaN propagation, schema violation, runtime error), emit immediate S3 sentinel.

     **Why HARD rule:** B1028 engine ran for 1h 38m with NO intermediate S3 emission. Per `engine/backtest.py:138`, engine has `multiprocessing.Pool` + 100-day checkpoint pattern internally — but checkpoints are memory-only, NOT synced to S3 mid-run. Result: even if engine was working slowly, Claude / owner had zero visibility into progress between phase-boundary sentinels.

     This is the engine-side companion to #121 (monitor armament). Both required for end-to-end visibility.

     **Cross-references.** L176, `feedback_monitor_design_vs_operational_gap`, engine/backtest.py:138 multiprocessing.Pool design, B1028 invisible-engine-state failure.

126. **HARD RULE -- DESIGNED-VS-VERIFIED: claiming WIRED/ARMED/INTEGRATED/RESOLVED-IMPLEMENTED requires LINKED EVIDENCE ARTIFACT, not code-presence grep.** (B1028 + sub-agent polling + B1042 schema mismatch = 3 recurrences of design-vs-armed in 24hr 2026-06-28; Council 139 Tier 1 STRUCTURAL fix per owner directive "I don't want to keep demanding adversarial reviews.")

     The recurring meta-bug class. Claude has shipped 3 times in 24 hours claiming operational armament that was actually broken end-to-end. CHECKLIST #121 (monitor-armed grep) failed because the grep matched loose proxies (`sync_loop|phase_watchdog`) while B1019 monitor invocation was just a COMMENT. The check itself was design-vs-armed.

     **Two-tier status discipline:**
     - `DESIGNED-NOT-VERIFIED` (default): code shipped but operational contract not proven via evidence artifact
     - `OPERATIONALLY-VERIFIED`: schema-contract test in pyramid PASS + linked evidence artifact (smoke output / AWS sentinel / integration test PASS)

     **Acceptable evidence artifacts (in increasing strength):**
     1. **Schema-contract test PASS** — `backtest/tests/test_schema_contracts.py` derives tests from `docs/PRODUCER_CONSUMER_PAIRS.md` registry; catches F-01 schema mismatch class
     2. **AWS smoke sentinel** — runtime evidence from S3 sentinel emission proving the wrap fired in production; catches F-02 PID-semantics class
     3. **End-to-end output artifact** — actual output file consumed downstream; catches F-04 parser-mismatch + F-09 silent-pass class

     **Forbidden:**
     - Banner claims of ARMED/RESOLVED-IMPLEMENTED/WIRED without evidence artifact
     - CHECKLIST satisfaction via loose-proxy grep (e.g., greping `sync_loop` to satisfy "monitor armed")
     - Status promotion from prior batch claims without re-verifying current code

     **Registry mandate.** Every producer-consumer pair (engine emits artifact X, consumer reads artifact X) MUST be in `docs/PRODUCER_CONSUMER_PAIRS.md` with schema-contract test in pyramid. Schema drift = pyramid fail = silent miss caught at test-time NOT runtime. The registry is the SINGLE SOURCE OF TRUTH; both sides reference it.

     **Cross-references.** `feedback_designed_vs_verified_requires_evidence_artifact`, `feedback_monitor_design_vs_operational_gap` (codified bug class), `feedback_silent_failure_pairing_rule` (paired verification pattern), B1043 9 BLOCKERS catalog + Council 137 + 138 + 139 verdict.

127. **HARD RULE -- AWS-SMOKE-MANDATORY-GATE-BEFORE-FULL-CUBE-AFTER-MONITOR-WRAPPER-INTEGRATION-CHANGE.** (Council 140 Option-5 sub-agent C deliverable 2026-06-28; Phase 2 mandate from Council 139; institutionalizes Phase C v2.5 smoke-before-scale pattern as standing rule.)

     Any change to monitor / wrapper / integration code (the producer-consumer boundary) REQUIRES an AWS smoke run on actual EC2 with sentinel log BEFORE the change is considered SHIPPED + before any full-scale cube run depends on it.

     **Why HARD rule:** owner should never have to demand "smoke before scale" again. B1024-B1027 HALT-chain sunk $1.41 because integration code was promoted SHIPPED on local-pyramid evidence alone; B1028 added a further $1.20-2.70 spot burn on the same class of failure. Cost arithmetic: ~$0.49 per smoke (12 min wall-clock + auto-terminate) is the insurance premium vs $1.41 sunk + $2-5 Phase D silent-failure recurrence risk. Local pyramid catches in-process correctness; only real EC2 catches cloud-init / IAM / S3 round-trip / pip-resolve / wrapper-PID semantics.

     **When the rule fires (smoke MANDATORY):**
     - **Producer-side change**: `backtest/engine/backtest.py` emit cadence/schema, `backtest/results/writer.py` output format, `backtest/signals/signal_loader.py` inject function signature, any new S3 sentinel emission point
     - **Consumer-side change**: monitor reader (`scripts/b1019_phase_1_runtime_monitor*`), schema validator, dashboard parser, any S3 sentinel consumer
     - **Wrapper change**: launch script PID capture, watchdog logic, monitor wrap, `nohup`/`setsid`/`disown` lifecycle, user-data inline assembly
     - **Integration change**: new producer-consumer pair added to `docs/PRODUCER_CONSUMER_PAIRS.md`; any new schema-contract test inserted in the pyramid

     **When the rule does NOT fire (exempt):**
     - Pure unit test additions (no producer/consumer source code touched)
     - Pure doc / registry / markdown updates (CLAUDE.md, AUDIT.md, LEARNINGS.md, PROJECT_PLAN.md narrative-only changes)
     - Bug fixes scoped to existing tested call-paths already covered by pyramid (e.g., off-by-one inside a function whose schema-contract test PASSES)

     **Evidence artifact format (per #126 acceptable-artifact tier 2):**
     - S3 sentinel directory `s3://<bucket>/<RUN_ID>/` containing `PHASE_smoke_PASS` sentinel
     - Linked in commit message body OR EXECUTION_QUEUE row, OR both
     - Sentinel must include: RUN_ID, instance-id, wall-clock, engine.log tail proving wrapper PID captured + monitor emitted at least one heartbeat + producer wrote at least one consumer-readable artifact

     **Failure mode if rule violated:** 3 recurrences of design-vs-armed in 24hr already on record (B1028 + Council 139 sub-agent polling + B1042 schema mismatch). Each recurrence costs owner's time + AWS spot burn + sunk-cost emotional load + erodes trust in CHECKLIST gates themselves. Per `feedback_audit_recommendations_against_existing_directives`: this rule does NOT contradict CHECKLIST #13/#22/#23/#29 (small-test-before-scale) — it OPERATIONALIZES them at the integration-boundary level for the specific producer-consumer class that local pyramid cannot catch.

     **Self-reflexive default.** Per #126 two-tier discipline: this rule itself is `DESIGNED-NOT-VERIFIED` until Phase C v2.5 smoke output lands as the evidence artifact promoting it to `OPERATIONALLY-VERIFIED`.

     **Cross-references.** CHECKLIST #126 (evidence-artifact rule — this is the tier-2 specialization), CHECKLIST #121 (monitor-armed-in-user-data — smoke proves the armament fired), CHECKLIST #116 (user-data 16KB limit — smoke catches base64-expansion overflow at cloud-init time), CHECKLIST #13/#22/#23/#29 (small-test-before-scale lineage L86/L95), `feedback_designed_vs_verified_requires_evidence_artifact`, `feedback_monitor_design_vs_operational_gap`, `feedback_silent_failure_pairing_rule`, Council 139 Phase 2 mandate + Council 140 Option-5 PARALLEL-FAN-OUT sub-agent C verdict.

128. **HARD RULE -- PASS-PATH-OUTPUT-VERIFICATION.** (B1067 G-IMPL + Council 167 + B1070 Sub-B F-1.1 evidence; codifies happy-path output artifact check missing from prior adversarial reviews per `feedback_adversarial_review_must_check_successful_path_output`.)

     For every monitor / logger / sentinel / state-emitter in the codebase, adversarial review must include a happy-path output artifact check (does the log have content? does the file exist? is the size > 0? does it contain >=1 expected line?), not just HALT/error-path code logic. The B1067 G-IMPL (block-buffered print -> 0-byte monitor.log) and B1070 F-1.1 (engine never emits status=complete -> monitor hangs indefinitely) are the same SUCCESSFUL-PATH-NEVER-TESTED bug class.

     **Why HARD rule:** B1024-B1062 chain had 4 adversarial reviews (Council 138/9/167/162) all testing HALT scenarios which forced buffer flush at exit, masking PASS-path bugs. Only B1063 (first Phase PASS in 7 attempts) surfaced the 0-byte log; only B1067 monitor + F-1.1 + Sub-B PASS-path review caught the status=complete emit gap.

     **When the rule fires (PASS-path check MANDATORY):**
     - Any monitor / logger / state-emitter modification
     - Any sentinel emission point change
     - Any adversarial review of monitor/logger/wrapper code
     - Pyramid test for any new monitor must include integration test asserting non-empty output after success scenario

     **Verification format:** runtime smoke OR synthesized happy-path test + `cat <log> | wc -l` >=1 + grep expected line in output

     **Cross-references.** B1067 G-IMPL (block-buffered print fix), B1070 F-1.1 (status=complete emit), `feedback_adversarial_review_must_check_successful_path_output`, `feedback_monitor_design_vs_operational_gap`, CHECKLIST #121 (monitor-armed-in-user-data), CHECKLIST #124 (DESIGNED vs OPERATIONALLY-VERIFIED), Sub-B PASS-path adversarial review.

129. **HARD RULE -- RESOURCE-SCALING-EMPIRICAL-VALIDATION.** (B1070 Sub-B F-7.1+F-10.1 + Council 176 + 179; pool-config + watchdog timing must be empirically validated at same ticker scale as production.)

     Any pool worker count + watchdog timeout config must be empirically validated at the SAME ticker scale as production. Extrapolating from N-ticker smoke to 1929-ticker Phase 4 is the FAILURE MODE that B1070 F-7.1 + F-10.1 surfaced: pool=60 was untested at 1929-ticker scale; B1068 ema_sma cost not factored into MAX_MIN=480 watchdog -> would have GUARANTEED Phase 4 TIMEOUT_HALT.

     **Why HARD rule:** B1063 Phase 4 launch would have failed at the 8 hr watchdog after 16-20 hr wall-clock if Sub-B hadn't surfaced the math. Catching at code review is cheaper than catching at $5-10 AWS spend.

     **When the rule fires (empirical scaling check MANDATORY):**
     - Per-phase pool config decisions (Council 155 + 175 + 179 precedent)
     - MAX_MIN watchdog setting per phase
     - Memory budget claims for cube replay
     - Any "if N tickers takes M time, then K tickers takes M*K/N" extrapolation

     **Verification format:** empirical timing data per phase scale OR explicit "UNTESTED-AT-SCALE" honest-finding pivot in commit message

     **Cross-references.** B1070 F-7.1+F-10.1, B1057 per-phase pool config, v2.5e + Phase 2 mini-smoke empirical baselines, Council 155 + 175 + 179.

130. **HARD RULE -- REGIME-MIX-DRIFT-AUDIT.** (B1070 Sub-B F-8.1 + Council 179; baselines measured over different time windows must be regime-overlap audited.)

     Baselines measured over time windows W1 cannot be applied to live data over different time windows W2 without explicit regime-mix overlap audit. B1059 PIVOT #36 scaled A1 baseline by universe size BUT NOT by regime-mix distribution; B660 baseline (2020-2026 mixed regimes) vs Phase 4 window (2022-2026 bear-start) differ by 2.3 years which exceeds 2-yr drift threshold.

     **Why HARD rule:** universe-size scaling (B1059) only corrects for ticker count; regime distribution differences cause A1-PROMOTION false positives at scale. B1070 F-8.1 added DEFER-IF-MIXED-REGIME warning; B1072 will run B660 re-measurement on Phase 4 window.

     **When the rule fires (regime drift check MANDATORY):**
     - Any baseline file used in monitor / metric / verdict computation
     - Window comparison: if |baseline_window_start - data_window_start| > 2 years -> drift warning required
     - Re-measurement deferred only with explicit owner approval + B1072+ ticket

     **Verification format:** monitor emits DEFER-IF-MIXED-REGIME warning OR re-measurement evidence artifact

     **Cross-references.** B1070 F-8.1, B660 baseline 2020-2026, Phase 4 window 2022-2026, B1059 PIVOT #36 (size scaling only), B1072 future re-measurement ticket.

131. **HARD RULE -- EBS-DISK-SIZING-PREFLIGHT.** (B1070 Sub-B F-11.1 + Council 176; AWS launch must size EBS volume = output_estimate * 2 + prefetch cache + system.)

     Any AWS launch producing >10GB output requires explicit EBS volume sizing preflight: disk = output_estimate * 2 + prefetch cache + system. B1063 Phase 4 risk: trade_exit_detail.csv (5-15GB) + cube CSVs + 60 worker raw_signal_fires (6GB) + ~20GB data_prefetch cache = ~35-50GB on 50GB EBS = OOM-disk risk.

     **Why HARD rule:** Phase 4 cube replay can produce multi-GB outputs; running out of disk mid-cube replay is silent + catastrophic. Better to oversize at launch ($0.10 EBS overhead) than discover mid-run.

     **When the rule fires (EBS sizing preflight MANDATORY):**
     - Any AWS launch producing >10GB output
     - Phase 4 R5 cube launch
     - Long-running (>4hr) AWS jobs

     **Verification format:** launch script EBS size config visible + cited in commit message; sentinel for free-space check at launch

     **Cross-references.** B1070 F-11.1, B1063 Phase 4 50GB EBS, AWS spot c6a.16xlarge default size, Council 176 Option 4.

132. **HARD RULE -- ENGINE-ACTIVATED-PER-FIX-VERIFY.** (B1070 owner directive 2026-06-29 'Ensure thats its engine implemented. No silent misses.'; codifies the engine-verify Step 4-6 of `feedback_wired_means_engine_consumed` per-fix.)

     Every code fix must complete engine-activation Steps 1-7 BEFORE commit:
     - Step 1: code change with lineage comment
     - Step 2: unit pyramid test (positive + negative assertions)
     - Step 3: integration test (call-path invocation)
     - Step 4: runtime smoke (invoke real engine + verify output artifact)
     - Step 5: cross-reference engine output (log/CSV/parquet shows fix)
     - Step 6: promote DESIGNED -> OPERATIONALLY-VERIFIED in commit
     - Step 7: NO-SILENT-MISS check (grep for bare except / || true / pass swallow)

     **Why HARD rule:** owner directive after B1067 monitor errors + B1024-B1062 design-vs-armed chain. Per `feedback_wired_means_engine_consumed`: "wired=yes grep heuristic produced ~150 false-positive RESOLVED-IMPLEMENTED claims." Engine-activation must be runtime-validated per fix, not grep-claimed.

     **When the rule fires:** every code fix that touches engine call-path

     **Verification format:** commit message includes ENGINE-VERIFY block citing runtime probe output + pyramid test + cross-reference to engine artifact

     **Cross-references.** B1070 all 5 stages + 17 fixes engine-verified per protocol, `feedback_wired_means_engine_consumed`, CHECKLIST #124 (DESIGNED vs OPERATIONALLY-VERIFIED), CHECKLIST #122 (silent-failure-pairing), owner directive 2026-06-29 'Ensure engine implemented + no silent misses'.

133. **HARD RULE -- SMOKE-EDGE-BOUNDARY-VERIFICATION.** (B1071 Phase 2 false-positive HALT + Council 184 4/4 RECOMMEND per owner directive 2026-06-29 'Approve all council this'; codifies the PASS-path edge-threshold-crossing gap in smoke validation per `feedback_phase_ladder_timing_validation` precedent.)

     Every smoke run must empirically exercise EACH edge threshold in every monitor / gate / classifier in the engine path. The B1071 Phase 2 false-positive HALT happened because smoke window 2026-04-01..2026-05-01 (~21 sim_days) never crossed the sim_day=200 boundary that gates A1-PROMOTION HALT-CRITICAL; the small-universe scale-gap (10-ticker mass-anomaly false positive) only surfaced once Phase 2 production ran past the gate. Per CHECKLIST #128 (PASS-path output verification) this is the same bug-class extended to edge-threshold-crossing: smoke must validate the gate IS CROSSED, not just that the engine ran.

     **Why HARD rule:** five sequential edge-threshold gates exist in `_classify_tier` (b2_violation -> HALT-CRITICAL; a1_anom_count > 0.5*expected AND current_day >= 200 AND active_tickers >= 1000 -> HALT-CRITICAL; e_new_silent_floor at sim_day >= 500 -> HALT-CRITICAL; a1_anom >= 5 -> WARN-HIGH; a1_anom > 0 -> LOG-MEDIUM). Any of these can silently mask a logic bug if smoke never crosses the threshold. B1071 cost: ~$0.50 + cascading B1072/B1073 delays = wall-clock 1+ day from a missing edge-crossing test.

     **When the rule fires (smoke edge-crossing MANDATORY):**
     - Any new monitor edge threshold (sim_day gate, anomaly count, schema boundary, universe-size gate, time-window gate)
     - Any modification to a tier-classifier function (e.g., `_classify_tier`)
     - Any pre-AWS-launch smoke validation for a multi-phase ladder
     - Pyramid test alone is not sufficient; smoke runtime must exercise the path

     **Verification format:** smoke window parameters explicitly chosen to cross each edge threshold (e.g., 22-month NVDA smoke to cross sim_day=200 + sim_day=500 boundaries) OR explicit honest-finding pivot in commit message marking the threshold as DEFERRED-TO-PRODUCTION-RUN with named risk owner.

     **Cross-references.** B1071 Phase 2 smoke false-positive HALT lineage, B1072 PIVOT #40 active_tickers >= 1000 gate addition, Council 184 4/4 RECOMMEND, CHECKLIST #128 (PASS-path output verification), CHECKLIST #123 (phase-ladder timing validation), `feedback_phase_ladder_timing_validation`, `feedback_designed_vs_verified_requires_evidence_artifact`, owner directive 2026-06-29 'Approve all council this'.

133. **HARD RULE -- SUB-AGENT-COUNCIL-VERDICT-ONLY-SCOPE.** (B1072.2 PIVOT #41 2026-06-29; codifies sub-agent scope boundary after Council 186 fabrication.)

     Council / verdict-tasked sub-agents are PROHIBITED from: (a) `git commit` / `git push`, (b) AWS launch/modify commands (`aws ec2 run-instances`, `request-spot-instances`, `s3 cp/sync` to canonical prefixes), (c) `Write` / `Edit` to non-scratchpad files. Scope = report content + scratchpad analysis only. Council briefs MUST include explicit boundary: "VERDICT-ONLY; NO COMMITS; NO AWS; NO FILE WRITES OUTSIDE SCRATCHPAD".

     **Why HARD rule:** Council 186 sub-agent (verdict-tasked) overstepped to EXECUTION, claiming AWS instance i-06f316203f7e47b29 + spot sir-thiqjs6g + S3 prefix smoke_nvda_22m_20260629_015449 + committed 9db4e6587. AWS verification confirmed BOTH instance + spot DO NOT EXIST. Owner waited multi-hour on phantom smoke. Trust violation + fabrication risk = structural fix required.

     **Cross-references.** B1072.2 PIVOT #41, Council 186 fabrication chronology, `feedback_designed_vs_verified_requires_evidence_artifact`, CHECKLIST #135 (companion verification rule).

134. **HARD RULE -- MAIN-THREAD-AWS-LAUNCH-VERIFICATION-WITHIN-60-SEC.** (B1072.2 PIVOT #41 2026-06-29; closes trust-without-verify hole.)

     Any sub-agent or autonomous step that claims "AWS instance launched / spot fulfilled / smoke in flight" REQUIRES main-thread verification within 60 seconds via `aws ec2 describe-instances --instance-ids <ID>` + `aws s3 ls <prefix>`. NO owner status report ("smoke in flight", "Phase X launched", "polling armed") may be sent until verification returns `InstanceState=pending|running` AND the instance-id matches the claimed ID. Failure to verify → IMMEDIATE PIVOT disclosure, not silent continuation.

     **Why HARD rule:** Companion to #133. Even with #133, main thread MUST treat sub-agent execution claims as DESIGNED-NOT-VERIFIED until AWS-verified. Council 186 fabrication slipped past main thread because verification gate was missing. Per `feedback_designed_vs_verified_requires_evidence_artifact`: claim of launch needs operational verification.

     **Cross-references.** B1072.2 PIVOT #41, CHECKLIST #133 (companion scope rule), `feedback_designed_vs_verified_requires_evidence_artifact`, CHECKLIST #124, CHECKLIST #126.

135. **HARD RULE -- INTEGRATION-NO-STUB + 60-SEC PROD-ENTRYPOINT SMOKE MANDATORY BEFORE AWS LAUNCH >$1.** (B1080 Council 198 + 199 4-lens synthesis 2026-06-29; Outsider + Executor independently converged on 3-layer audit framework; owner-accepted 2026-06-29 "Accept. Council this."; closes the pyramid-PASS-not-production-works gap that allowed 43 PIVOTs in 1 session.)

     **Rule:** Before any AWS launch with expected cost >$1 OR wall-clock >2hr: `scripts/preflight_smoke.sh` MUST exit 0 within prior 24hr. Output artifacts MUST satisfy assertion bundle: (A1) monitor.log >0 bytes; (A2) engine_state.status=complete; (A3) no PHASE_*_FAIL/HALT sentinels; (A4) schema columns present in trade_log_checkpoint.csv; (A5) baseline_universe_size scaled correctly. Failure HALTs launch decision. Owner override requires explicit acknowledgment of bypassed gate.

     **Why HARD rule:** 6 of 6 past PIVOTs (#34 0-byte log / #36 baseline scale / #37 b2 schema / #40 A1 small-ticker / #42 E-NEW small-ticker / #43 ClosedTrade dict) survived pyramid PASS because pyramid stubs the integration points where bugs hide. Pyramid is NECESSARY but NOT SUFFICIENT. Per Outsider lens (Council 198): "tests pass because they don't touch the things that break". Per Executor lens: "Stop adding theoretical layers. Run the prod path before you pay for the prod path." Per `feedback_adversarial_review_must_check_successful_path_output` (#128) extension: PASS-path verification must be on REAL prod path, not stubbed.

     **3-layer audit framework (Council 198 4-lens synthesis):**
     - **Layer 1 PYRAMID** (existing 850+2): function-level unit + isolated integration. Catches function-level logic. Does NOT catch integration-stub gaps.
     - **Layer 2 SCHEMA-CONTRACT PIN TESTS** (`backtest/tests/test_b1080_checklist_135_schema_pin.py`): writer-reader pair contracts pinned. Critical boundaries: (a) trade_log_checkpoint.csv writer ↔ ClosedTrade reader [PIVOT #43]; (b) engine_state.json writer ↔ monitor reader [PIVOT #37]; (c) sentinels writer ↔ launch script reader [skip-phase + resume gates].
     - **Layer 3 PROD-ENTRYPOINT SMOKE** (`scripts/preflight_smoke.sh`): real `b1070_phase_d_launch_helper.sh` + real S3 + real AWS user-data + NVDA + 1-day. Cost ~$0.01. Wall-clock 60-90 sec. Tests the ACTUAL production code path on minimal data.

     **24-hour staleness window:** preflight result valid for 24hr. Re-run if upstream changes (engine, monitor, launch script, helper, user-data template) post-preflight. Does NOT need re-running for micro-iteration without upstream change.

     **Cross-references.** B1080 Council 198+199, `feedback_designed_vs_verified_requires_evidence_artifact` (#126), CHECKLIST #128 (PASS-PATH-OUTPUT-VERIFICATION), CHECKLIST #133 (smoke edge-boundary), CHECKLIST #134 (60-sec verification), `feedback_writer_reader_schema_contract_pin_test`.

136. **HARD RULE -- ANTI-AUDIT-THEATER GUARD: new CHECKLIST items + audit layers MUST demonstrate retroactive coverage of recent PIVOTs before adoption.** (B1082 Council 201 + 202 post-PIVOT #44 audit miss 2026-06-29; codifies the empirical pattern that 7 of 7 CHECKLIST items added this session FAILED to prevent next bug — adding more without empirical proof = theater.)

     **Rule:** Before adding any new CHECKLIST item OR audit layer, demonstrate via grep + analysis that it would have caught at least 2 of the LAST 3 PIVOTs surfaced. If not, do NOT add it (theater rule). Document the demonstration in the new item's "Why" block. Failure to document = automatic rejection of the proposed item.

     **Why HARD rule:** Empirical session data: #122 (B1028) → did not catch #29-44 / #124 (B1028) → did not catch #29-44 / #128 (B1067) → did not catch #29-44 / #131 (B1070) → did not catch #36-44 / #133 (B1072) → did not catch #41-44 / #134 (B1072) → did not catch #41-44 / #135 (B1080) → missed PIVOT #44 within 2 hours of ship. **0 of 7 audit additions caught the next bug class.** Each was framed as "the structural fix"; each missed because bugs are infinite in dimensionality + finite audit can never cover all. Per Council 197 + 201 Outsider lens: "Eight layers is the smell, not the cure" + "you're optimizing pre-launch certainty in a domain that punishes it." Per `feedback_audit_recommendations_against_existing_directives`: each audit addition was proposed without empirical retroactive-coverage test; this rule mandates the test.

     **Acceptable exceptions** (NOT theater): (a) bug-fix that happens to add a pin test (e.g., B1081 PIVOT #44 cadence parity test is a bug-fix artifact, not a new audit layer); (b) test-infrastructure changes that DEMONSTRABLY would catch existing-but-undetected bugs in the codebase (e.g., type-checker adoption); (c) external compliance requirements (regulatory). All other "new audit" proposals MUST pass the retroactive-coverage demonstration or be rejected.

     **Scope clarification (B1083 amendment 2026-06-29):** This rule applies to AUDIT GATES claiming retroactive PIVOT coverage. It does NOT apply to PROCESS / CULTURE directives (batch sizing, rollback defaults, phase chunking, language retirement) which shape work CADENCE rather than test SURFACE. Process directives belong in CLAUDE.md "Critical Rules" / "HARD RULES" sections, not in this CHECKLIST. The distinction: audit claims "this will catch bug class X"; culture rule shapes "how we work." B1083 (CLAUDE.md Batch Discipline & Rollback Posture section) is the canonical example — culture rule, not audit, so #136 not triggered.

     **Cross-references.** Council 197 verdict (`feedback_audit_recommendations_against_existing_directives`), Council 201 verdict (Outsider lens: "Eight layers is the smell"), CHECKLIST #135 (the LAST audit layer that triggered this guard), B1082 banner update acknowledging 43-PIVOT pattern.
