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
    - `CLAUDE.md`, `AUDIT_INDEX.md` (DEC bodies — current canonical state), `CHECKLIST.md`, `LEARNINGS.md`, `PROJECT_PLAN.md`, `DETAILED_PROJECT_PLAN.md`, `TRADING_RULES_AND_INFORMATION.md`, `STRATEGY_REGISTER.md`, `BUG_REGISTER.md`, `ENGINEERING_REGISTER.md`, `DOCUMENTATION_REGISTER.md`, `IMPLEMENTATION_READINESS_DASHBOARD.md`, `PASS_NN_PRIORITIES.md` (current Pass), `EXPLANATION.md`, `README.md`, `UNIVERSAL_LEARNINGS.md`, `AUDIT_TRIAGE.md`, etc.

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
