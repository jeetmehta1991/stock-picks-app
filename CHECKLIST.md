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

136. **ANTI-AUDIT-THEATER GUARD (B1447: DOWNGRADED from HARD RULE to reporting obligation -- the retroactive-coverage REQUIREMENT was REMOVED by owner directive 2026-08-04).** (B1082 Council 201 + 202 post-PIVOT #44 audit miss 2026-06-29; codifies the empirical pattern that 7 of 7 CHECKLIST items added this session FAILED to prevent next bug — adding more without empirical proof = theater.)

     **Rule (B1447 AMENDMENT 2026-08-04, owner directive "remove"): the retroactive-coverage REQUIREMENT is REMOVED. A new item is NO LONGER rejected for failing to show it would have caught 2 of the last 3 PIVOTs.**

     What remains is a REPORTING obligation, not a gate: when a new item is added, state what it would and would not have caught, so its expected value is visible. An item whose retroactive coverage is zero may still be added -- novel failure classes have no prior instances BY DEFINITION, which is exactly why they are novel.

     **Why removed.** The requirement was empirically load-bearing in the wrong direction. Between 2026-07-23 and 2026-08-04 the session recorded EIGHT LEARNINGS entries (L263-L270) and added ZERO CHECKLIST items; CHECKLIST.md went untouched for ~90 batches. The mechanism (L271): #136 rejects an item lacking retroactive coverage, and Phase 5.2 routes anything an EXISTING item should have caught to "compliance failure, record in the L-entry instead". Together they form a RATCHET -- every individual miss is either too novel to prove coverage or too covered to need an item, so the checklist can never grow. Four of those eight misses were genuinely new classes and became #164-#167 only after the owner intervened.

     **What the guard was right about, and is retained below:** adding layers is not free, and "this is the structural fix" is a claim to distrust. That is now carried by the reporting obligation and by the acceptable-exceptions list, not by a rejection gate.

     **Why HARD rule:** Empirical session data: #122 (B1028) → did not catch #29-44 / #124 (B1028) → did not catch #29-44 / #128 (B1067) → did not catch #29-44 / #131 (B1070) → did not catch #36-44 / #133 (B1072) → did not catch #41-44 / #134 (B1072) → did not catch #41-44 / #135 (B1080) → missed PIVOT #44 within 2 hours of ship. **0 of 7 audit additions caught the next bug class.** Each was framed as "the structural fix"; each missed because bugs are infinite in dimensionality + finite audit can never cover all. Per Council 197 + 201 Outsider lens: "Eight layers is the smell, not the cure" + "you're optimizing pre-launch certainty in a domain that punishes it." Per `feedback_audit_recommendations_against_existing_directives`: each audit addition was proposed without empirical retroactive-coverage test; this rule mandates the test.

     **Acceptable exceptions** (NOT theater): (a) bug-fix that happens to add a pin test (e.g., B1081 PIVOT #44 cadence parity test is a bug-fix artifact, not a new audit layer); (b) test-infrastructure changes that DEMONSTRABLY would catch existing-but-undetected bugs in the codebase (e.g., type-checker adoption); (c) external compliance requirements (regulatory). All other "new audit" proposals MUST pass the retroactive-coverage demonstration or be rejected.

     **Scope clarification (B1083 amendment 2026-06-29):** This rule applies to AUDIT GATES claiming retroactive PIVOT coverage. It does NOT apply to PROCESS / CULTURE directives (batch sizing, rollback defaults, phase chunking, language retirement) which shape work CADENCE rather than test SURFACE. Process directives belong in CLAUDE.md "Critical Rules" / "HARD RULES" sections, not in this CHECKLIST. The distinction: audit claims "this will catch bug class X"; culture rule shapes "how we work." B1083 (CLAUDE.md Batch Discipline & Rollback Posture section) is the canonical example — culture rule, not audit, so #136 not triggered.

     **Cross-references.** Council 197 verdict (`feedback_audit_recommendations_against_existing_directives`), Council 201 verdict (Outsider lens: "Eight layers is the smell"), CHECKLIST #135 (the LAST audit layer that triggered this guard), B1082 banner update acknowledging 43-PIVOT pattern.

137. **HARD RULE -- PHASE-4-DIRECT-TARGET: chunks SHOULD skip Phase 1/2/3 invocations when only Phase 4 cube needed.** (B1087 Council 211 Fix C + owner directive 2026-06-30 "We do not need phase 2 and 3 anymore at this stage".)

     **Rule:** When `PHASE_4_ONLY=1` env var is set (or equivalent), `scripts/launch_r5_master_4y_v2.sh` MUST skip `run_phase 1`, `run_phase 2`, `run_phase 3` invocations entirely. Phase 4 runs FRESH for the chunk's strategy band (or with `--resume-from-checkpoint` if checkpoint exists per CHECKLIST #135 writer-pair invariant). Reduces wrapper surface area + removes timing-cascade risk from intermediate-phase sentinel-sync failures.

     **Retroactive coverage demo (per #136 ANTI-AUDIT-THEATER):** This is a PROCESS directive (work cadence), not an audit gate. Per #136 scope clarification: not triggered.

     **Cross-references.** B1087 Council 211 Fix C, CLAUDE.md Batch Discipline & Rollback Posture section, CHECKLIST #135 (Layer 3 preflight gate).

138. **HARD RULE -- MANDATORY POLLING TASK PER AWS LAUNCH: every AWS spot/on-demand launch (initial OR re-launch) MUST arm a background Bash polling task in the same turn.** (B1088 Council 212 verdict 2026-06-30 + owner META question "Why didn't you notify automatically?" after 2.5-hr blind window on B1087 wave-1 spot reclamation cascade.)

     **Rule:** Within the SAME turn as an AWS launch via `aws ec2 run-instances` (direct OR via helper `b1070_phase_d_launch_helper.sh` OR wrapper `launch_phase4_parallel.sh`):
     (a) MUST `Bash` with `run_in_background: true` a polling task that calls `aws ec2 describe-instances` + `aws s3 ls <RUN_ID-prefix>/` every 5-15 min;
     (b) Polling task MUST emit task-notification on: instance state change (running → terminated/stopped), PHASE_N_FAIL sentinel, PHASE_N_B1019_HALT sentinel, spot-interruption detection (state=terminated + StateReason=Server.SpotInstanceTermination);
     (c) Turn MUST NOT end before polling task armed; verify via TaskList before turn-end;
     (d) Re-launches DO NOT inherit polling from prior launches — each launch arms its OWN polling task tied to its OWN RUN_ID(s).

     **Why HARD rule:** B1087 wave-1 cascade (6 chunks reclaimed 13:13-13:33Z in us-east-1f) went undetected for ~2.5 hr because ScheduleWakeup-based 15-min cadence only fires on IDLE conversation; active back-and-forth (PIVOT #47 fix work + owner messages) suppressed cadence firing. Background Bash polling fires REGARDLESS of conversation activity. Prior launches B1075/77/78/79/86-wave-1 all had background polling armed (`bpco4qd2p` / `bcazlr1rt` / `bts8yvqzo` / `b064z69j5` / `b6vfw38ze`); B1087 wave-1 relaunch FORGOT to arm — inconsistent infrastructure use.

     **Retroactive coverage demo (per #136 ANTI-AUDIT-THEATER):** Would armed background polling have caught PIVOT #44 (B1079 spot interrupt)? YES. PIVOT #45 (preflight race)? NO (race detected during sequential run; not a launch monitoring issue). PIVOT #46 (quota exhaustion)? NO (quota fail detected at launch time; not post-launch). PIVOT #47 (resume crash)? NO (engine crash, would have caught via PHASE_4_FAIL sentinel polling). B1087 wave-1 spot reclamation (this incident)? YES. 2 of last 3 spot/state-change incidents → passes #136 retroactive coverage threshold for a NEW HARD RULE.

     **Acceptable exceptions:** smoke launches <$1 expected cost where wall-clock <5 min (e.g., `preflight_smoke.sh --per-az` 4 t3.micros) — these self-terminate within polling window; manual polling sufficient.

     **Cross-references.** Council 212 verdict, B1087 wave-1 cascade evidence (`output_audit/b1087_wave1_relaunch_evidence_2026_06_30.json`), CHECKLIST #134 (60-sec-launch-verification companion), CHECKLIST #135 (preflight gate companion), `feedback_designed_vs_verified_requires_evidence_artifact`.

139. **HARD RULE -- ENV-CONFIG-DRIFT AUDIT: when execution environment changes, audit engine argparse auto-sets + env var defaults for environment-specific behavior.** (B1093 Council 227 Q4 verdict 2026-07-02 + Batch A PIVOT #50 wall-time guard kill.)

     **Rule:** Before launching a batch/run in a NEW or CHANGED execution environment (AWS→laptop, laptop→AWS, cloud→CI, container→VM, one instance type→another with different memory/CPU profile), MUST audit `backtest/run_phase1a.py` argparse auto-sets + any relevant env vars for environment-mismatched defaults. Specifically verify:
     (a) **Wall-time guards** (`--max-run-hours`, `--warn-run-hours`) — cloud runs may auto-set aggressive caps for cost control; laptop runs need higher caps or explicit CLI override.
     (b) **Memory limits** (`--memory-cap-mb`, DEC-179) — instance-specific; must exceed peak observed on new environment.
     (c) **Parallelism defaults** (`--screen-pool-workers`) — pool=16 on 4-vCPU laptop is contention; pool=1 on 32-vCPU is under-utilization.
     (d) **Log rotation / disk quotas** — cloud has ephemeral disk; laptop has 1 TB but log dirs grow fast.
     (e) **Cost guards** (`--max-cost-usd` when present) — designed for AWS; irrelevant on laptop but may reject-early.

     **Enforcement:** every batch launch in a NEW environment MUST include a pre-flight block explicitly enumerating each of (a)-(e) with the value in effect + verification against expected wall-clock / memory / cost profile. Missing enumeration → HALT before launch.

     **Why HARD rule:** Batch A on laptop (2026-07-01) hit `--max-run-hours=6.0` auto-set at run_phase1a.py:320-328 (designed as Batch 394 AWS runaway-cost guard 2026-05-27) and self-killed at day=720/1044 (68.9%). Owner had asked "why wasn't this flagged in reviews and audits" — because no CHECKLIST item covered env-config drift. All 3 recent councils (224 Path B batching, 225 health check cadence, 226 recovery path) audited data-quality + throughput + memory but NOT engine argparse defaults. Same audit-theater pattern as CHECKLIST #128 warns against: new checks that don't retroactively catch prior PIVOTs.

     **Retroactive coverage demo (per #136 ANTI-AUDIT-THEATER):** Would env-config-drift audit have caught PIVOT #48 (c6a.4xlarge memory pressure)? YES — instance type change laptop→c6a would have surfaced (b) memory + (c) parallelism defaults mismatch. PIVOT #49 (CSV update bug in auto_resume_polling.sh)? NO — script bug, not env-config drift. PIVOT #50 (Batch 394 6-hr guard on laptop)? YES — this rule targets it directly. 2 of last 3 PIVOTs → passes #136 retroactive coverage threshold for a NEW HARD RULE.

     **Acceptable exceptions:** re-launches in the SAME environment with the SAME instance type + config as a prior launch that completed successfully — the env is already validated; audit not required.

     **Cross-references.** Council 227 Q4 verdict, Batch A recovery lineage (B1093 auto-set 6.0→48.0 + explicit CLI overrides in `laptop_launch_batch_a.ps1` / `laptop_launch_batch_b.ps1` / `laptop_resume_batch_a_detached.ps1`), `feedback_banner_is_status_not_scope_authority` (analogous drift pattern between docs and code), CHECKLIST #128 (ANTI-AUDIT-THEATER precedent), CHECKLIST #124 (DESIGNED vs OPERATIONALLY-VERIFIED — env defaults are DESIGNED for one env, OPERATIONALLY-VERIFIED in another only after this audit).

140. **HARD RULE -- CUBE EXIT FAN-OUT EQUALS count(EXIT_STRATEGIES) PER CLOSED TRADE.** (Owner directive 2026-07-02 Council 231.)

     **Rule:** For every cube-mode batch completion (Phase 1A-β or similar), `trade_exit_detail.csv` row count MUST equal exactly `closed_trades × count(EXIT_STRATEGIES)`. Not "≥ N methods". Not "≥ N rows". EXACT equality. Only exception: trades still open at engine end (not-yet-exited) — those legitimately have no cube fan-out.

     **Enforcement:**
     - Post-batch verification MUST compute: `expected = closed_trades × len(EXIT_STRATEGIES)`; `actual = len(trade_exit_detail_df)`; verify `abs(expected - actual) == 0`.
     - Currently `count(EXIT_STRATEGIES) = 26` (Batch 487 SM2 smart_money_reversal); test-pin per CHECKLIST #74 doc-count-drift rule.
     - Open trades excluded via `df_closed = df_trades[df_trades["status"] == "closed"]` OR equivalent — count only closed.
     - If actual < expected → cube fan-out silently drops (producer/registration bug). HALT + investigate.
     - If actual > expected → duplicate emission bug. HALT + investigate.

     **Why HARD rule:** Cube purpose is per-(strategy × exit × regime) empirical measurement of the 14 passing criteria. If ANY exit method silently drops for ANY trade, affected cells have artificially small sample size → statistical verdicts unreliable → Phase 1B-α winner selection made on incomplete evidence. Weaker thresholds (≥N methods, ≥N% rows) hide silent-drop bugs that only surface post-4-day-Batch-B when recovery cost is maximal. Owner correction 2026-07-02 Council 231 after Council 230 audit set "≥15 exit methods" threshold: "If condition is greater than 15 exit methods, its incorrect. Needs to be equal to the count all exit methods for each trade. No exceptions."

     **Retroactive coverage demo (per #136 ANTI-AUDIT-THEATER):** Would EQUAL-count rule have caught prior PIVOTs? PIVOT #34 (block-buffered print silent PASS-path)? NO (different bug class). PIVOT #37 (writer-reader schema exit_reason vs exit_method)? YES — schema mismatch would surface as cube emission failures reducing actual < expected. PIVOT #50 (Batch 394 6-hr guard)? NO (different bug class). 1-of-3 → passes #136 retroactive threshold for a NEW HARD RULE targeting a specific bug class (cube emission integrity).

     **Acceptable exceptions:** none for closed trades. Only open-trades at engine end.

     **Cross-references.** `feedback_cube_exit_count_must_equal_registered`, `feedback_strategy_x_exit_cell_analysis` (aggregate meaningless — precursor rule), `project_phase_1a_beta_is_exit_cube` (owner-directive origin 2026-05-25 that "every entry must simulate every exit"), Council 231 verdict, CHECKLIST #74 (count-drift test-pin), CHECKLIST #131 (companion fire-count validation).

141. **HARD RULE -- FIRE-COUNT VALIDATION IN EVERY BATCH GATE (STANDALONE).** (Owner directive 2026-07-02 Council 231 + Council 232 standalone revision.)

     **Rule:** Every batch completion gate MUST include per-strategy fire-count validation that is STANDALONE - intrinsic to the batch, NO external baseline comparison. Prior draft used B660 baseline; owner rejected 2026-07-02 Council 232: "Check 2 needs to be changed. Nothing on comparison to a baseline. Needs to be standalone." External baseline is stale + universe-mismatched; intrinsic validation against PASSING_CRITERIA thresholds + coverage checks is the correct standard.

     **Layer 1 - Fire-count classification (vs PASSING_CRITERIA thresholds):**
     - `n_fires` = unique trade entries per strategy in trade_log
     - **SILENT:** n_fires == 0
     - **STARVED:** 1 <= n_fires < min_trades_per_regime (currently 30) - cannot populate any per-regime cell
     - **MARGINAL:** min_trades_per_regime <= n_fires < min_trades_overall (currently 100) - some cells populatable, overall PASS impossible
     - **VIABLE:** n_fires >= min_trades_overall - multiple cells populatable, potential overall PASS

     **Layer 2 - Coverage checks (intrinsic to batch data):**
     - **Regime coverage:** for each regime present in trade log's regime column, VIABLE strategies should have >= 1 fire (or be per-regime affinity restricted).
     - **Direction coverage:** strategies with `_long` suffix must fire long-only; `_short` suffix short-only; dual-suffix any. Mismatch = correctness bug.
     - **Temporal coverage:** for strategies with n_fires >= 20, verify no single quarter has > 80% of fires (indicator of intermittent producer or gate flip).

     **Layer 3 - HALT gate:**
     - `N_SILENT (excluding STRATEGIES_DISABLED_MISSING_PRODUCER) > 10` -> HALT
     - `N_TEMPORAL_CLUSTERED > 5` -> HALT
     - `N_DIRECTION_MISMATCH > 0` -> HALT (correctness bug)

     **Why HARD rule:** A strategy that fires 0 times over the batch window may be either (a) genuinely disabled or (b) silently broken (producer not wired, schema drift, PIVOT-#37-class). Standalone validation using PASSING_CRITERIA thresholds distinguishes fire-count adequacy for the very metrics the cube will compute, and intrinsic coverage checks (regime, direction, temporal) surface producer + gate issues without needing an external reference file that decays over time as strategies + universes drift. Owner correction 2026-07-02 Council 232: baseline-based check "Nothing on comparison to a baseline. Needs to be standalone."

     **Retroactive coverage demo (per #136 ANTI-AUDIT-THEATER):** Would standalone fire-count validation have caught PIVOT #37 (writer-reader schema)? YES - schema drift shows as strategies with n_fires=0 for affected exits. PIVOT #38 (retracted) and pre-B1068 panel-blackout? YES - 30%+ silent strategies would have surfaced without needing baseline. PIVOT #48 (c6a memory pressure)? NO. PIVOT #50 (Batch 394 guard-kill)? NO. 2-of-4 recent PIVOTs -> passes #136 retroactive threshold for a NEW HARD RULE.

     **Acceptable exceptions:** strategies explicitly listed in `STRATEGIES_DISABLED_MISSING_PRODUCER` count as SILENT but do NOT contribute to HALT threshold. STARVED and MARGINAL strategies are reported but don't fail; those are legitimate cube-mode observations of low-fire strategies.

     **Cross-references.** `feedback_batch_gate_includes_fire_count_validation` (updated to standalone), Council 232 verdict, `feedback_monitor_intermediate_counts` (in-run version), `feedback_data_consumption_audit_must_apply_checklist_44b` (silent-empty investigation), CHECKLIST #130 (companion cube completeness rule), `PASSING_CRITERIA` config source of thresholds.

142. **HARD RULE -- AUTONOMOUS SCRIPTS MUST ADD NOT OVERWRITE HAND-CRAFTED WORK.** (Owner directive 2026-07-03 Council 260 + L188.)

     **Trigger.** Every autonomous CSV/doc-updating script author (or reviewer) must verify BEFORE run.

     **Rule.** Autonomous loop scripts that touch multiple CSV columns must classify each target column as:
       (a) SAFE-TO-WRITE: column this script owns/created (script populates freely)
       (b) READ-ONLY: column populated by upstream/hand-crafted work (never overwrite)
       (c) APPEND-ONLY: column mixes hand-crafted + auto content (append new markers only)

     For each write target: verify pre-existing content is NOT more specific than what script produces. If script's output is generic template + column has specific hand-crafted text, DO NOT OVERWRITE.

     **Root cause history.** Council 243 Turn 9 autonomous loop (B1123) overwrote 129 strategies' `final_recommended_actions` column (populated by Council 237 B1118 with specific extractions from `recommendation` column) with generic gate-count-based templates. Bug was silent until owner spotted specific-vs-generic discrepancy 25+ batches later. 87 strategies were then marked SKIP_GENERIC_TEMPLATE by autonomous executor because parseable specificity had been destroyed by the earlier loop.

     **Retroactive coverage demo (per #136).** Would this rule have caught Council 243 Turn 9 overwrite? YES - script would need explicit column classification declaring `final_recommended_actions` READ-ONLY. Would it have caught Council 237 truncation? YES - extractor writes to `final_recommended_actions`, must verify against `recommendation` column length before writing shorter version.

     **Enforcement.** Add pre-flight check to autonomous scripts: sample 3-5 rows before write, verify script output is not shorter/less-specific than existing column content. Log any overwrite attempts to output_audit/.

     **Cross-references.** L188 (LEARNINGS.md); Council 260 diagnostic (B1149); Council 262 (B1152) parser multi-format; Council 263 (B1153) truncation-safe extraction fallback; `feedback_no_silent_misses`.


143. **HARD RULE -- SESSION MISTAKES MUST BE CODIFIED IN CHECKLIST SAME-TURN.** (Owner directive 2026-07-03 Council 263.)

     **Trigger.** Every session/turn that produces a MISTAKE (bug, design flaw, silent-miss, wrong assumption caught by owner) must codify the lesson in CHECKLIST as a new numbered item + LEARNINGS.md as new L<N> lesson, SAME TURN.

     **Rule.** After every mistake surfaces (whether via pyramid failure, owner catch, retroactive audit, or self-detection):
       1. Analyze root cause (Council perspective adversarial + producer author + auditor)
       2. Add to LEARNINGS.md as L<N> with universal principle + rule + cross-references
       3. Add to CHECKLIST.md as new numbered item with trigger + rule + retroactive coverage demo + cross-references
       4. Commit BOTH updates in the same batch as the mistake discovery

     **Rationale.** Without codification, lessons decay. Same mistake pattern repeats next session. Owner-caught mistakes are the highest-signal instances - MUST become permanent checklist items.

     **Retroactive coverage demo.** Would this rule have prevented Council 243 Turn 9 overwrite bug? Not directly (rule didn't exist yet), but with rule in place, PRIOR similar mistakes (L177 phantom-name, L179 baseline scaling, L180 schema drift) each would have generated CHECKLIST items forcing pre-flight checks in future scripts.

     **Session mistakes catalog this session (2026-07-03) codified this turn:**
       - L188 -> CHECKLIST #142 (Turn 9 auto-loop overwrite)
       - L189 pending: WIDEN_PERCENT multi-format assumption (Council 262 B1152)
       - L190 pending: truncation-safe extraction (Council 263 B1153)

     **Cross-references.** L188/L189/L190; Council 260/262/263; `feedback_no_silent_misses`; L181 (investigation-only turns still require doc sweep).


144. **HARD RULE -- TRUNCATION-SAFE EXTRACTION FROM CANONICAL SOURCE COLUMNS.** (Owner directive 2026-07-03 Council 263.)

     **Trigger.** Every extractor script that reads from a canonical source column (e.g., `recommendation`, `final_recommended_actions`) and writes a derived column must be TRUNCATION-SAFE.

     **Rule.** Extractors must:
       (a) NEVER truncate at delimiters that appear inside parenthetical annotations. Example: `LOOSEN: vol_spike_15x (1.5x) -> vol_spike_12x (1.2x) OR vol_above_avg AND widen X` — truncating at "(1;" via naive semicolon-boundary loses the target signal.
       (b) When splitting by regex, verify the split doesn't cut off mid-clause. Use full-sentence or full-clause boundaries only.
       (c) When derived column length < source column length, log a warning and preserve original in secondary column for audit.

     **Enforcement.** Autonomous executors must have a FALLBACK RULE: if derived column action text detects truncation markers (e.g., `(\d[.\d]?\s*;\s*(widen|drop))` pattern), re-parse from the original source column.

     **Retroactive coverage demo.** avwap_20high_rejection_short SKIP_UNCLASSIFIED bug (Council 263): Council 237 B1118 truncated `LOOSEN: vol_spike_15x (1.5x) -> vol_spike_12x` at semicolon inside parenthesis, saving only `vol_spike_15x (1;`. Truncation-safe rule + fallback would have caught this + fully auto-executed.

     **Cross-references.** Council 263 B1153; `apply_csv_loosen_autonomous.py` fallback rule; L190 (pending).


145. **HARD RULE -- DIFF/AUDIT COLUMNS MUST MERGE ALL CHANGE TYPES.** (Owner directive 2026-07-03 Council 264.)

     **Trigger.** Every derived diff/audit column generator author (or reviewer) must verify BEFORE run.

     **Rule.** Diff columns that report changes to source code / config / data must:
       (a) Detect ALL change types independently (signal ADD/REMOVE, numeric threshold widening/narrowing, producer-side changes, config-arm changes)
       (b) Concatenate all detected changes into single composite view
       (c) NEVER suppress one change type because another is present
       (d) Include applied-edits detail from execution_comments when available

     **Rationale.** Owner audit depends on complete diff visibility. If diff column shows only signal changes when both signal AND threshold changed, owner infers threshold change was NOT applied.

     **Root cause history.** avwap_20high_rejection_short had BOTH vol_spike_15x -> vol_spike_12x replacement (B1153) AND abs(pct_from_20h) < 1.0 -> < 2.0 widening (B1152). Diff column showed only signal replacement. Owner asked "why was widen abs(pct_from_avwap) < 1% -> < 2% not implemented" - was implemented, diff column misled.

     **Retroactive coverage demo (per #136).** Would this rule have caught the B1152 partial-visibility bug? YES - rule requires enumerate-all-change-types.

     **Enforcement.** Diff column generators must have a merged-summary logic. Test with sample rows that have MULTIPLE change types applied.

     **Cross-references.** L191; Council 264 B1154; `add_updated_producer_signals_columns.py`; L188/L189/L190 (related autonomous-script rules).


146. **HARD RULE -- AUTONOMOUS SCRIPTS MUST TOUCH EXECUTION_QUEUE.MD PER COMMIT.** (Owner directive 2026-07-03 Council 264 + L192.)

     **Trigger.** Every autonomous script that produces git commits.

     **Rule.** Autonomous scripts that commit changes MUST:
       (a) Append a brief entry to EXECUTION_QUEUE.md per commit (batch#, strategy, applied edits)
       (b) Include EXECUTION_QUEUE.md in `git add` for that commit
       (c) Fail loudly if EXECUTION_QUEUE.md is not writable

     **Rationale.** CHECKLIST #67 per-turn doc sweep applies to EVERY commit. Silent auto-commits without doc entries are per-strategy silent misses.

     **Retroactive coverage demo (per #136).** Would this rule have caught B1145 auto-executor's 10 commits missing doc-sweep? YES - rule requires explicit EXECUTION_QUEUE write per auto-commit.

     **Enforcement.** Regression test test_recent_batches_touch_execution_queue enforces this via git-log commit inspection.

     **Cross-references.** L192; Council 264 B1154; CHECKLIST #67; L181 (investigation-only turns still require doc sweep).


147. **HARD RULE -- AUTONOMOUS SCRIPT CONTROL-FLOW MUST TRY RECOMMENDATION-COLUMN FALLBACK BEFORE SKIP SHORT-CIRCUIT.** (Owner directive 2026-07-03 Council 265 + L193.)

     **Trigger.** Every autonomous script that classifies input then applies short-circuit logic based on classification.

     **Rule.** When classify_action() returns SKIP_* class, script MUST attempt recommendation-column fallback (re-classify from richer source) BEFORE any `continue` / short-circuit. Placement of fallback code AFTER SKIP-short-circuit is a silent bug because SKIP cases never reach the fallback.

     **Rationale.** Multiple parser bugs (Council 260/262/263/265) surfaced strategies where action_text was truncated/missing but recommendation column had specific parseable text. Fallback placement matters.

     **Root cause history.** B1156 initial fix placed rec-fallback AFTER SKIP short-circuit (`if classification.startswith("SKIP"): continue`). Fallback never ran for SKIP cases. Bug caught when 9 strategies with parseable rec-column edits remained SKIP after B1156. Moving fallback BEFORE SKIP short-circuit yielded 9 SPECIFIC_DONE in retry.

     **Retroactive coverage demo (per #136).** Would this rule have caught B1156 flow-order bug? YES - rule requires fallback-before-shortcircuit; explicit test.

     **Enforcement.** Autonomous scripts must document control-flow order: (1) initial classify, (2) rec-fallback, (3) status-based short-circuit, (4) apply edits. Any deviation logged for audit.

     **Cross-references.** L193; Council 265 B1157; CHECKLIST #142/#143/#144.


148. **HARD RULE -- MARGINAL TIER STRATEGIES MUST NOT BE LOOSENED.** (Owner directive 2026-07-04 Council 268 + L194.)

     **Trigger.** Every loosening/widening/gate-drop decision on a strategy.

     **Rule.** Before applying any loosening edit to a strategy:
       (1) Read strategy's n_fires from CSV
       (2) Classify tier: CRITICAL (0) / HIGH (1-15) / MED (16-30) / MARGINAL (>30)
       (3) If tier == MARGINAL: REJECT loosening; mark DONE_B<n>_MARGINAL_NO_LOOSEN with reason
       (4) If tier == BORDERLINE (n=31-33): default reject; escalate to owner

     **Rationale.** Strategies above MARGINAL boundary (n > 30) are already firing above PASSING_CRITERIA min_trades_per_regime=30 threshold. Loosening = over-firing / dilution / false-positive amplification.

     **Retroactive coverage demo (per #136).** Would this rule have caught B1139 avwap_252_breakout loosen at n=32 (2 fires above MARGINAL boundary)? YES - rule requires tier check; n=32 = MARGINAL / BORDERLINE.

     **Enforcement.** Autonomous scripts must have tier-check gate before applying LOOSEN edits. Manual review must verify tier per strategy pre-edit.

     **Retroactive concerns to review:**
       avwap_252_breakout (n=32, DONE_B1139): loosened 2 fires above MARGINAL - owner may want revert

     **Cross-references.** L194; Council 268 B1162; CHECKLIST #67/#143; PASSING_CRITERIA; Council 237 tier definitions.


149. **HARD RULE -- ATTEMPT AUTONOMOUS FIRST; MANUAL REVIEW ONLY FOR NOVEL DECISIONS.** (Owner directive 2026-07-04 Council 270 + L195.)

     **Trigger.** Every "manual review" task where each item follows repeatable patterns.

     **Rule.** Before starting manual review:
       (1) Sample 3-5 items to identify decision templates
       (2) If patterns are repeatable (numeric widen / signal replace / OR expand / STATUS_QUO): extract to autonomous rules FIRST
       (3) Manual review is ONLY justified for items requiring novel judgment not fitting any rule
       (4) After 3 consecutive "manual" batches showing common patterns: STOP + extract to autonomous

     **Rationale.** Manual work masquerading as "review" is often autonomous work not yet extracted. Repetition burns time + introduces inconsistency + violates autonomous-first design.

     **Retroactive coverage demo (per #136).** Would this rule have prevented B1158-B1165 "manual" batches? YES - rule requires 3-batch pattern audit; 4 templates (numeric widen, direct-threshold, OR-expand, STATUS_QUO) would have been extracted after B1160.

     **Enforcement.** When starting a "manual review" round, first log: "sampled N items, distinct patterns observed: [list]". If <=4 patterns and >5 items to process: extract patterns as rules.

     **Cross-references.** L195; Council 270 B1166; CHECKLIST #142/#143/#147; B1158-B1165 batch history.


150. **HARD RULE -- NO INVENTION: AMBIGUOUS CSV RECOMMENDATIONS REQUIRE OWNER APPROVAL.** (Owner directive 2026-07-04 Council 271 + L196.)

     **Trigger.** Every attempt to translate a CSV recommendation into code changes.

     **Rule.** Before applying ANY loosening edit verify:
       (a) Signal name mentioned in CSV EXISTS in producer output (grep verify)
       (b) Threshold value in CSV MATCHES actual source value (not close-enough)
       (c) Enumerated set uses EXACT names from CSV
       (d) Directional widening (LONG/SHORT symmetric) is EXPLICITLY stated
       (e) Drop specifies EXACTLY which gate(s) - "1-2" is NOT specific

     If ANY fail: STOP + mark PENDING_OWNER_REVIEW + await approval.

     **Rationale.** "Manual review" is when owner reviews ambiguity, NOT when script or reviewer INVENTS solutions.

     **Root cause history (B1158-B1165):** 8 of 19 strategies had inventions. Full list in L196.

     **Retroactive coverage demo (per #136).** Rule catches all 8 inventions.

     **Cross-references.** L196; Council 271 B1167; CHECKLIST #142/#143/#149.


151. **HARD RULE -- CSV METADATA COLUMNS MUST BE GIT-VERIFIED, NOT STAMPED.** (Owner directive 2026-07-04 Council 274 + L197.)

     **Trigger.** Every enrichment script that populates CSV columns (change_from_original, updated_producer_signals, etc.) claiming reflect code state.

     **Rule.** Before stamping a metadata column with "batch X did Y":
       (a) Resolve batch_ref -> ALL matching git commits (not just first)
       (b) For each commit, run git diff against strategy body in target file
       (c) Only stamp "widened" / "loosened" / "changed" when git-diff shows actual delta
       (d) Categorize NO-CHANGE cases explicitly (STATUS_QUO, UNIVERSE_EXPAND deferred, AUDIT_COMPLETE, PRODUCER_CASCADE, SECONDARY, MARGINAL_NO_LOOSEN)
       (e) Distinguish consumer (screener.py) change vs producer (technical.py / smc_ict.py / chart_patterns.py / universe.py / etc.)

     **Rationale.** B1148 Council 259 add_updated_producer_signals_columns.py stamped "numeric threshold widened in {batch}" on ALL DONE_B* rows without git-diff check. Result: 48 of 67 rows FALSE (72% wrong). Owner caught 4 examples (cpr_narrow_momentum, donchian_breakdown_retest_short, smc_choch_reversal, squeeze_setup_long) all UNIVERSE_EXPAND rec but showed "threshold widened" text.

     **Retroactive coverage demo (per #136).** Rule requires git-diff verification -> would have caught all 48 false stamps in B1148 immediately.

     **Enforcement.** Any script populating change_from_original / updated_producer_signals must call git diff-tree per batch_ref, per strategy. No exceptions. See scripts/fix_change_from_original_and_gate_structure.py canonical implementation.

     **Cross-references.** L197; Council 274 B1169; CHECKLIST #67/#128/#136/#150.


152. **HARD RULE -- GATE STRUCTURE COLUMN MUST SHOW LOGICAL FORMULA NOT COMMA LIST.** (Owner directive 2026-07-04 Council 274 + L197.)

     **Trigger.** Every CSV column that documents "current strategy gate stack" (updated_producer_signals or equivalent).

     **Rule.** Column value MUST be a logical AND/OR/NOT formula:
       (a) Extract each `fires = (...)` or `fl = (...) fs = (...)` block from source
       (b) Substitute s.get("X") -> X, replace `and` -> AND, `or` -> OR, `not` -> NOT
       (c) Preserve parenthetical grouping (e.g., `A AND (B OR C)`, not `A,B,C`)
       (d) For dual LONG/SHORT: format as `LONG: (...) | SHORT: (...)`
       (e) Layered patterns (`layer1_positioning`, `layer2_catalyst`): substitute layer definitions inline

     **Rationale.** CSV comma-list `bearish_engulfing,below_prev_low,recent_blowoff_at_r3,shooting_star,vol_below_avg` HIDES gate structure. Reviewer cannot distinguish 5-AND vs 3-AND-with-OR-composite. Owner example: pivot_r3_blowoff_short shown as 5-comma-list but actually `recent_blowoff_at_r3 AND vol_below_avg AND (bearish_engulfing OR shooting_star OR below_prev_low) AND NOT short_borrow_trap` = 3-gate structure.

     **Retroactive coverage demo (per #136).** Would have surfaced pivot_r3_blowoff_short 2-vs-5 gate confusion in owner review before it reached the CSV column drift stage.

     **Enforcement.** scripts/fix_change_from_original_and_gate_structure.py canonical formula extractor. All future column-population scripts inherit or reference this pattern.

     **Cross-references.** L197; Council 274 B1169; CHECKLIST #150/#151.


153. **HARD RULE -- FINAL_RECOMMENDED_ACTIONS MUST ALIGN WITH EXECUTION_STATUS INTENT.** (Owner directive 2026-07-04 Council 274 + L197.)

     **Trigger.** Every DONE / SKIP / PENDING classification decision.

     **Rule.** Action tag semantics MUST match execution_status:
       (a) [LOOSEN_GATE] / [LOOSEN_THRESHOLD] / [DROP_GATE] -> requires consumer/screener.py code change -> execution_status must show DONE_B<n>_<CHANGE>
       (b) [UNIVERSE_EXPAND] -> DO NOT execute in Batch A; mark DONE_B<n>_UNIVERSE_EXPAND (no code change)
       (c) [AUDIT_DATA] -> not a code change; mark DONE_B<n>_AUDIT_COMPLETE with audit-verification batch ref
       (d) [FIX_PRODUCER] -> producer file change (technical.py / smc_ict.py / etc.); mark DONE_B<n>_PRODUCER_CASCADE
       (e) Mixed-tag rec (e.g., "[LOOSEN_GATE] + [FIX_PRODUCER] + [UNIVERSE_EXPAND]"): split into ordered sub-actions; execution_comments must enumerate which sub-action was done in which batch

     **Rationale.** Owner surfaced squeeze_setup_long example: final rec was "[CRITICAL] [AUDIT_DATA] URGENT FINRA prefetch coverage across Batch A; [UNIVERSE_EXPAND] Batch B / T3 high-SI names" - marked DONE_B1146_AUDIT_COMPLETE (correct for AUDIT_DATA sub-action) BUT change_from_original stamped as "numeric threshold widened" (FALSE - no code change happened; AUDIT-only fulfillment). Rule requires sub-action tracking to prevent this drift.

     **Retroactive coverage demo (per #136).** Rule would have caught all 48 CHECKLIST #151 mis-stamps by requiring sub-action enumeration per action tag.

     **Enforcement.** CSV populators must decompose action-tag lists into ordered sub-actions BEFORE marking DONE. If any sub-action pending: status is PENDING_SUB_<tag>.

     **Cross-references.** L197; Council 274 B1169; CHECKLIST #150/#151/#152.


154. **HARD RULE -- DATA-SOURCE COVERAGE AUDIT BEFORE "PRODUCER VERIFIED" CLAIMS.** (Owner directive 2026-07-07 Council 280 + L199.)

     **Trigger.** Every audit report claiming "producer verified working" for a data-source-dependent signal (news sentiment, options, insider, institutional, corporate action, calendar).

     **Rule.** Before publishing "PRODUCER VERIFIED WORKING" verdict:
       (a) Sample must be REPRESENTATIVE of the target universe (not mega-cap-only)
       (b) Sample size must be >= 25 tickers OR >= 10% of universe (whichever larger)
       (c) Temporal robustness: test across >= 4 dates spanning >= 12 months
       (d) Report per-ticker coverage rate + per-date coverage rate + effective universe
       (e) Distinguish 3 categories: ALWAYS_COVERED / PARTIAL / ALWAYS_ZERO
       (f) Save canonical measurement to output_audit/<producer>_coverage_<universe>.json
       (g) If effective universe < 90%, queue Sprint 5 secondary-source ticket

     **Rationale.** B1204 news_sentiment audit was mega-cap-only (8 tickers, 1 date). Reported "PRODUCER VERIFIED WORKING" without noting coverage bias. B1209 25-non-mega-sample corrected to 48% but was also incomplete. B1211 full 133-ticker x 4-date audit found 84.2% effective universe with 15.8% zero-coverage. Each smaller sample gave misleading verdict.

     **Retroactive coverage demo (per #136).** Rule catches B1204 miss immediately: 8 tickers < 25 minimum + single date < 4 minimum + mega-cap-only fails representativeness. Would have required B1211-scale audit before "producer verified" claim.

     **Enforcement.** scripts/measure_news_coverage_batch_a.py is canonical template for new coverage audits. Copy pattern for options/insider/institutional/corporate-action producers.

     **Cross-references.** L199; Council 280 B1211-B1213; CHECKLIST #106 (data-consumption audit) + #128 (adversarial happy-path); scripts/measure_news_coverage_batch_a.py; output_audit/news_coverage_batch_a.json.


155. **HARD RULE -- BLOCKED_UPSTREAM CLASSIFICATION FOR DATA-GAP-STRATEGIES.** (Owner directive 2026-07-07 Council 282 + L200.)

     **Trigger.** Every strategy whose upstream producer data-source coverage is <30% OR whose primary signal is never emitted (regardless of data existence).

     **Rule.** Classify per strategy:
       (a) `BLOCKED_UPSTREAM_<PRODUCER>` = producer never emits primary signal (0% coverage). Strategy code correct; upstream data gap prevents firing.
       (b) `COVERAGE_LIMITED_<PRODUCER>` = producer emits but effective universe <50%. Strategy fires only on subset.
       (c) `EVENT_RARITY_<PRODUCER>` = producer works but signal inherently rare (Form 4 filings, corporate actions). Not a data bug.
       (d) `UNAFFECTED` = strategy doesn't depend on audited producer.

     **When to apply:**
       - After CHECKLIST #154 producer coverage audit
       - Before assuming a strategy's low fire count is a code-loosening issue
       - Before recommending strategy changes if upstream data may be the constraint

     **Rationale.** B1188-B1203 Council 278 loosened 40 strategies to improve fire counts. B1217 cross-audit found 20 institutional strategies fire on only ~30% of Batch A due to 13F data gap - loosening these strategies has BOUNDED uplift potential until data gap fixed. squeeze_setup_long marked BLOCKED_UPSTREAM_SHORT_INTEREST_PCT because producer literally can never emit primary signal.

     **Retroactive coverage demo (per #136).** Rule catches: Council 278 loosening of 20 institutional strategies would have been flagged as COVERAGE_LIMITED_INSTITUTIONAL first - owner could have prioritized 13F data fix before loosening.

     **Enforcement.** scripts/cross_audit_strategies_vs_coverage.py canonical implementation. Run after any CHECKLIST #154 producer audit to update strategy classifications.

     **Cross-references.** L200; Council 282 B1217-B1219; CHECKLIST #154; scripts/cross_audit_strategies_vs_coverage.py; output_audit/strategy_vs_producer_coverage_matrix.json.


156. **HARD RULE -- TEMPORAL COVERAGE CHECK FOR HISTORICAL BACKTESTS.** (Owner directive 2026-07-07 Council 284 + L201.)

     **Trigger.** Every producer coverage audit intended to inform a backtest that spans multiple years.

     **Rule.** Coverage audit MUST include historical dates matching the backtest window:
       (a) Test at LEAST 1 date per year in backtest window (e.g., 2020-2024 = 5 dates minimum)
       (b) Report per-year effective universe separately - not aggregated
       (c) Flag producers with year-over-year coverage transition (e.g., "absent in 2020, 80% from 2021+")
       (d) Backtest interpretation for coverage-transitioning years must annotate FALSE-NEGATIVE risk

     **Rationale.** Council 280-283 audits used 2024-only dates. B1227 historical spot-check found:
       - news_sentiment 0/20 in 2020, 80%+ from 2021+
       - short_interest_dtc 0/20 in 2020, 100% from 2021+
       - institutional 13F 0/20 in 2020 AND 2021, 30% from 2022+

     Data-dependent strategies had ZERO effective universe in 2020-2021 - not because of strict gates, but because upstream data source did not exist yet. Aggregated audit numbers (84%, 30%) HIDE this timeline.

     **Retroactive coverage demo (per #136).** Rule catches: Council 278 loosening of institutional strategies (B1173/B1174/B1197) - would have been flagged as ZERO effective universe in 2020-2021 backtest years.

     **Enforcement.** scripts/measure_producer_coverage.py accepts --historical-dates flag (extension pending). Ad-hoc B1227 template for now.

     **Cross-references.** L201; Council 284 B1227-B1228; CHECKLIST #154 (representative sampling) + #155 (BLOCKED_UPSTREAM classification); output_audit/historical_dates_producer_spotcheck.json.


157. **HARD RULE -- AUDIT-PATH TRACING FOR PRODUCERS WITH MULTIPLE FUNCTIONS.** (Owner directive 2026-07-07 Council 285 + L202.)

     **Trigger.** Every producer coverage audit where the module has 2+ compute_ or detect_ functions that emit signals with similar naming.

     **Rule.** Before running coverage audit, verify the ACTUAL consumer path:
       (a) Find a strategy that uses the signal
       (b) Grep for the signal name in signal_loader.py to find the inject_* function
       (c) Grep for the inject function body to find the compute_* function it calls
       (d) Audit THAT compute_ function, NOT a similar-named one from the same module
       (e) Multiple compute_ functions -> multiple audits (one per data path)

     **Rationale.** B1216 audited compute_persistence_signals (30% coverage) but strategies actually use institutional_buy which comes from institutional_signal (via inject_institutional_signals, 85% coverage). Misclassified 19 of 20 strategies as coverage-limited when they were actually fine.

     **Retroactive coverage demo (per #136).** Rule catches: B1216 would have required tracing "institutional_buy" from strategy -> signal_loader.inject_institutional_signals -> smart_money.institutional_signal (bulk + per-ticker), NOT institutional_persistence_consumer.compute_persistence_signals.

     **Enforcement.** Audit report must include "trace_verification" field showing the strategy -> inject_fn -> compute_fn chain.

158. **HARD RULE -- PRE-RUN ENVIRONMENT-FINGERPRINT PARITY (per chunk/run; MANDATORY before any mergeable multi-run).** (Owner directive 2026-07-18 Council 339 + L207 + L208.)

     **Trigger.** Any backtest run that will be MERGED with sibling runs (multi-chunk R5, local+AWS splits, any distributed cube), OR any run launched on a machine/environment not identical to the one that produced the sibling artifacts.

     **Rule.** Before a run burns compute:
       (a) Emit `scripts/env_fingerprint.py --emit <output_dir>/env_fingerprint.json` at launch (captures trading-day-grid total + hash, calendar backend, key package versions, code SHA).
       (b) A `calendar_backend != nyse_mcal` fingerprint is a WARNING at emit and a HALT before a production/mergeable run (it means the degraded Mon-Fri fallback, L207).
       (c) Before MERGING chunks, run `scripts/env_fingerprint.py --check <dir1>/env_fingerprint.json <dir2>/...` -- any mismatch on grid_total / grid_hash / calendar_backend is a HARD HALT; mismatched chunks re-run on the correct grid before merge (merge_batch_outputs.py enforces this automatically).

     **Rationale.** B1305/B1306: chunk 1 ran the Mon-Fri fallback grid (1043 days) while AWS chunks ran the correct NYSE grid (1002); a silent semantic fallback (L207) + a resume decision that optimized per-run internal consistency without cross-run reconciliation (L208) locked ~25pct of the universe onto the wrong, incompatible grid -- caught only when the owner asked about the merge, after days of compute. No mechanical gate existed for cross-environment run parity because multi-environment execution was new this session.

     **Retroactive coverage demo (per #136).** Would have caught: (1) the chunk-1 calendar defect (parity --check at chunk-2 launch flags grid 1043 vs 1002); (2) L207 itself (emit --warn shows calendar_backend=monfri_fallback locally); (3) any future package/precision drift across a distributed run. Verified live B1307: --check correctly HALTs on the chunk1(1043,monfri) vs local(1003,nyse) mismatch.

     **Enforcement.** Executable, not prose: `scripts/env_fingerprint.py` (pin-tested); merge_batch_outputs.py calls --check on all input dirs and aborts on mismatch.

     **Cross-references.** L202; Council 285 B1230; CHECKLIST #154/#155/#156.

159. **HARD RULE -- PRE-ENGINE HALT + COVERAGE SMOKE (executable env+coverage gate before/after every cloud batch).** (Owner-approved B1328/B1330 2026-07-20; formalized B1335 -- prior batches cited "#159" informally without this entry existing, itself a numbering-drift miss.)

     **Trigger.** Every cloud batch/chunk launch and every batch analysis.

     **Rule.** (a) At boot, BEFORE the engine spends: `scripts/preengine_gate.py <fingerprint> <expected_sha>` -- abort + shutdown (CHUNK_GATEFAIL) unless smc_active=True AND calendar_backend=nyse_mcal AND code_sha==expected. (b) After the run: `scripts/coverage_smoke.py --analyze <dir>` must PASS all checks: fanout==fired*26, ZERO cross-strategy portfolio-gate skips (isolation), smc_active, code_sha parity, all CORE producer families firing, log clean of tracebacks/silent-failures. (c) Determinism (`--determinism`) and merge-append (`--merge-check`) validated once per sequence.

     **Rationale/Retroactive (per #136).** Caught, pre-spend or pre-scale: the stale 07-17 cloud tar, the SMC ModuleNotFoundError (22 silent strategies), code_sha=unknown, and (in chunk 2 retrospect) the shared-portfolio contamination. Four smoke iterations ~ $2 vs the ~$17+days burned before these gates existed.

     **Enforcement.** Executable: preengine_gate.py (in launcher user-data), coverage_smoke.py (pin-tested test_b1323/test_b1330); merge parity via env_fingerprint.MERGE_CRITICAL (test_b1332).

160. **HARD RULE -- MEASUREMENT-SEMANTICS FREEZE (run-manifest before any multi-hour/cost-bearing run).** (Owner-approved B1335 2026-07-20; from the B1334 waste retrospective.)

     **Trigger.** Any run costing money or >1h wall-clock, and any multi-run sequence whose outputs will be merged.

     **Rule.** A `run_manifest.json` pins: frozen code SHA, isolation mode, calendar backend, universe/ticker list (disjointness across sequence batches), budget cap + projection. `scripts/prelaunch_gate.py` must PASS before launch. Changing ANY pinned field mid-sequence invalidates prior batches -> restart the sequence (cheap-batches-first makes this affordable).

     **Rationale/Retroactive (per #136).** Chunk 1 (~5 days laptop) and chunk 2 (~$15-17) were both obsoleted by post-hoc semantics changes (isolation decision, calendar, code fixes) -- launches preceded settled semantics. This gate makes that ordering physically impossible.

     **Enforcement.** Executable: prelaunch_gate.py wired into aws_chunk_launch (refuses launch without passing manifest).

161. **HARD RULE -- ARTIFACT-PROVENANCE PRE-FLIGHT (verify deployable artifacts LOCALLY before instance spend).** (Owner-approved B1335 2026-07-20.)

     **Trigger.** Any launch consuming a pre-staged artifact (code tar, data payload, ticker list).

     **Rule.** Every deployable artifact carries provenance (baked SHA / timestamp sidecar). The launcher verifies the S3 artifact's SHA against the manifest's frozen SHA LOCALLY, before `run_instances` -- not only on-instance after boot cost. Stale artifact = HALT + rebuild instruction.

     **Rationale/Retroactive (per #136).** The 5.8GB whole-repo tar went stale (07-17) and burned chunk 2 + 3 smoke attempts; detection happened on-instance (after boot spend) or post-run. Same family: the false CHUNK2_COMPLETE marker (B1312) and stale heartbeats (B1300) -- artifacts must be provenance-checked at point of use.

     **Enforcement.** Executable: build_r5_code_tar writes CODE_SHA into the tar + a .sha sidecar to S3; prelaunch_gate compares sidecar vs manifest pre-spend.

162. **HARD RULE -- COUNTER-SEMANTICS VERIFICATION (before any counter/metric is used as RCA evidence).** (Owner-approved B1335 2026-07-20.)

     **Trigger.** Any RCA, coverage claim, or fire-rate analysis that cites a counter, log tally, or emitted metric.

     **Rule.** First verify WHAT the counter measures: (a) which pipeline stage (pre- or post- which gates?); (b) per-process/per-worker aggregation semantics; (c) single- or multi-pass counting. State the verified measurement point alongside the number. A conclusion built on an unverified counter is a hypothesis (skill B1335 Rule 3), never a root cause.

     **Rationale/Retroactive (per #136).** `_RAW_SIGNAL_FIRE_COUNTER` counts BEFORE the screener's confirmation gates (screener.py:8793) and per-worker -- "140 raw fires -> 0 trades" was mis-read as a red-candle-gate RCA (B1333, overturned B1334). Also the B660 fire-count estimator class (independent-product vs measured).

     **Enforcement.** Judgment-tier rule with a mechanical assist: RCA queue entries citing counters must name the verified measurement point; fresh-eyes review cadence (skill B1335 Rule 4) audits this.

**#163 (B1354, Council 373) - RENDERED-ARTIFACT END-TO-END VERIFICATION.** A deliverable that RENDERS (dashboard, report page, chart, HTML/PDF) is verified by LOADING it, not by confirming its data was written. Before telling the owner it is live/ready: (a) enumerate ALL local assets index.html references (script src / link href) + confirm each present AND deployed (missing renderer -> silent "loading"); (b) fetch the deployed URL + every asset -> assert 200, not-stuck-loading, >=1 data section non-empty; (c) re-run the FULL check after ANY fix, not just the thing fixed. Tool: scripts/verify_dashboard.py --dir <d> [--url <deployed>]. Lineage: ~8 sequential dashboard errors (missing app.js/404/empty tabs) that engine-oriented pyramid+checklists never caught because nothing rendered the artifact (L218). Retroactive #136: would have caught missing-app.js (asset check), Pages-404 (live check), empty-survivor-tabs (data-presence).

**#164 (B1446, owner-directed) - ROUTED WORK BECOMES TRACKABLE TICKETS, NOT PROSE.** Any artifact or turn that ENUMERATES FUTURE WORK -- a routing table, a candidate list, a "remaining N" count, a deferred queue -- must produce EXECUTION_QUEUE tickets with (a) an S6-xxx ID, (b) the ITEM NAMES inlined, (c) a disposition. A paragraph saying "remaining 173, routed by the same rule: 68/66/28/11" is a RECORD, not a ticket: it is not greppable per item, cannot be closed individually, and cannot be cross-checked against later state. **Enforcement (mechanical):** the per-turn doc->queue cross-check must grep the artifact's own routing KEYS and item NAMES against EXECUTION_QUEUE.md; any routed item absent from the queue is a silent miss. **Lineage:** B1410 routed 177 strategies into four buckets and recorded only the counts; the population was invisible for ~30 batches until the owner asked (B1444/B1445). **Retroactive (#136):** would have caught the B1248 doc-only findings (9), the B1251 5-gap lenient reading, and this.

**#165 (B1446, owner-directed - "No arbitrary decisions. That's an absolute red flag") - EVERY SELECTION RULE MUST BE JUSTIFIED OR DECLARED.** Whenever code or analysis CHOOSES among candidates -- which duplicate survives, which exit is canonical, which threshold, which ticker sample, which tie-break -- the selection criterion must be stated inline AND justified on a measured basis, or explicitly labelled `ARBITRARY-PENDING-JUSTIFICATION` and ticketed. Convenience defaults (first match, largest N, alphabetical, insertion order) are arbitrary unless argued. **Rule:** an arbitrary rule may be used to make progress ONLY if (a) it is labelled as such in the same message it produces a number, and (b) a ticket exists to replace it. Publishing a number produced by an unjustified rule without that label is a Truth-Standard violation, because the number carries implied authority the method does not have. **Lineage:** B1444 de-dup picked each cluster's survivor by LARGEST TRADE SET -- a size heuristic with no performance basis -- while the canonical pipeline uses eigenvalue effective-N; six strategies were nearly decommissioned on it (S6-B1445b). **Retroactive (#136):** would have caught the exit-argmax naive selection (L227), the `first` ticker-sample default (B648), and this.

**#166 (B1446) - A GREP THAT RETURNS ZERO IS EVIDENCE ABOUT THE PATTERN UNTIL PROVEN OTHERWISE.** Before reporting an absence from a search, prove the pattern CAN match: run it against a known-present instance, or invert it (search a substring that must exist). "0 hits" from an unvalidated pattern is UNVERIFIED, never "it is not there". **Lineage:** B1444 grepped `"LOOSEN / STARVED"` (spaces around the slash, JSON-key format) against a file writing `LOOSEN/STARVED`; 0 hits was reported to the owner as a confirmed miss, written into LEARNINGS L270, and committed -- all false, retracted B1445. **Retroactive (#136):** would have caught the `wired=yes` grep heuristic (~150 false RESOLVED claims) and the B975 BLIND-SPOT-3 false positive.

**#167 (B1446, owner-surfaced) - REJECTION ON DIRECTION MUST REDIRECT, NEVER DROP.** When a router rejects a candidate because it is the WRONG KIND of change (tighten proposed on a starved strategy, loosen on a high-fire one), the item must be re-routed to the opposite queue, not `continue`d out of the pipeline. **Lineage:** `build_r6_change_list.py:89-92` dropped 10 strategies into no queue at all; owner: "if it's not tightening it's loosening, why skip?" (S6-B1445a). **Retroactive (#136):** same family as the B1410 prose-only routing (#164) and the B984/B975 disable-instead-of-investigate pattern.

**#168 (B1464, from L292) - A BYPASS SHIPS WITH THE CAPABILITY IT EXISTS TO ENABLE.** When a flag DISABLES a safeguard so that something else can be measured or collected, the batch that ships the bypass must ALSO ship that something else, or an EXECUTION_QUEUE ticket for it linked from the bypass's own comment. A bypass whose counterpart never lands silently converts a designed measurement into lost data, and it does so invisibly because the bypass keeps working exactly as written. **Enforcement:** any diff adding a `no_*` / `skip_*` / `bypass_*` / `disable_*` flag must, in the same commit, either implement the enabled capability or cite the ticket ID in the flag's docstring. **Lineage:** `backtest/engine/backtest.py:129` bypassed `STRATEGY_REGIME_AFFINITY` at Batch 384 with the rationale "cube measures per-regime cell verdicts empirically" -- the per-regime verdict is canonical criterion #11, which B1456 found was never implemented anywhere (L289). For ~1,000 batches the cube deliberately traded every strategy in every regime, including regimes each disclaims, and the grading pipeline pooled it all into one Sharpe -- averaging away precisely the signal the bypass was collecting. **Retroactive (#136):** would have caught the B901 `EMIT_RAW_SIGNAL_FIRES` flag (shipped before its consumer), the B1035 `SMC_PHASE` silent-kill, and this.

**#169 (B1464, from L303) - AFTER ANY LOOSENING, RE-RUN THE REGISTRATION-TIME REDUNDANCY AUDIT.** Removing a gate to un-starve a strategy can collapse it onto a DIFFERENT registered strategy, creating a duplicate that no performance gate will ever surface -- because de-dup runs downstream of the performance filter and therefore only ever compares winners. Every loosening batch ends by running `scripts/audit_registration_redundancy.py` and dispositioning any new pair at jaccard >= 0.95. **Enforcement (mechanical):** `test_b1463_no_new_near_identical_pairs` pins the known set; a new duplicate fails the pyramid. **Lineage:** Council 278's loosening campaign produced at least two collapses that sat undetected until B1463 -- B1194 dropped the smart_money requirement from `squeeze_breakout_with_smart_money_long`, leaving bare `squeeze_fire_up` and making it identical to `squeeze_breakout` (jaccard 0.9982); B1197 changed `institutional_insider_combo_long` from AND to OR, converging it onto `rsi_oversold_with_smart_money_long` (0.9993). In both cases the loosening deleted the ONLY gate that made the strategy distinct. This binds S6-OPT-196, which will loosen across a 196-strategy backlog. **Retroactive (#136):** would have caught the B874 `camarilla_rsi_obv` duplicate-pair, the `macd_crossover`/`macd_crossover_short` jaccard-1.000 pair, and both Council 278 collapses.

**#170 (B1470, owner-approved S6-B1467a) - THE ENFORCED TIER IS RE-VALIDATED INSIDE A FULL RUN.** A test gate that runs a SUBSET certifies only that the subset passes IN THAT SUBSET. It cannot detect order-dependence, shared-state pollution, or fixture leakage from the files it skips -- so a subset gate must periodically be re-run INSIDE the complete suite, and its result compared. Tiers are declared in `backtest/tests/pyramid_tiers.py` (GATE / QUARANTINE / EXTENDED, asserted to partition the suite by `test_b1470_pyramid_tiers_partition_the_suite`). **Enforcement:** before any phase launch or roster promotion, run the full suite and confirm every GATE test still passes there; a GATE test that passes alone and fails in-suite is a BLOCKER, not a curiosity. **Lineage:** the enforced command ran 2 of 431 files reporting `894 passed` while the full suite reported 172 failed / 11 errors -- and 2 of those failures were GATE tests (`test_integration.py` BUG-30 and BUG-232) that pass in isolation in 0.74s. The gate's green certified "these pass when nothing else has run" (L313, S6-B1468a). **Retroactive (#136):** would have caught the B1465 `test_batch743` pins (red, unrun, no start date), the stale-fixture class generally, and this.

**#171 (B1473, from L286+L302) - CONTENT GOES IN THE GENERATOR, NEVER IN THE GENERATED FILE.** If a file carries a do-not-edit banner, editing it is a defect regardless of how correct the content is: the banner is a machine-enforceable contract and the next regeneration is its enforcement. **Lineage:** the B1455 bear-stress caveat was written into `PHASE_1B_ROSTER.md` and committed; the next regeneration silently reverted it, undoing a published retraction (L286). Separately a fix that lived only in an inline probe never reached `measure_roster_breadth_and_alpha.py`, so the doc published N_eff figures I had already retracted (L302). **Enforcement:** after any change intended to appear in a generated artifact, RE-RUN the generator and diff its output before claiming the change is made.

**#172 (B1473, from L285+L299) - VERIFY THE RENDERED ARTIFACT AND NAME ITS CARDINALITY.** (a) For any generated deliverable the verification target is the RENDERED output, not the data structure behind it - a summary counter and the table it summarises are two renderings and can disagree (`PHASE_1B_ROSTER.md` shipped with its table saying NEEDS CREATION on the same 5 rows its summary called zero, L285). (b) When a collection has more than one legitimate count, state WHICH at every use and assert it against the deliverable set - "the roster" is 13 graded cells, 17 strategies, or 22 legs, and B1461 computed breadth over 13 while reporting it as the roster's (L299). Extends #163 from dashboards to every generated doc.

**#173 (B1473, from L306+L311+L319) - LONG JOBS AND MUTATING SCRIPTS: CAPTURE FULLY, GATE EXPLICITLY.** (a) Any command running more than a few minutes writes its FULL output to a file; apply `tail`/`head` when READING the file, never to the pipe when producing it - a 38-minute full-suite run was piped through `tail -12` and its 172 failing test names were destroyed at write time, costing a second 38-minute run (L311). (b) A script that MUTATES a tracked artifact must gate the commit describing the mutation (`script && git commit`), never sit beside it - the B1472 patch script asserted and exited having changed nothing while the commit proceeded and published "QUARANTINE 75 -> 71" (L319). (c) After changing a shared artifact, run the test files that REFERENCE the changed names (`grep -rln <name> backtest/tests/`), and establish the baseline with `git stash` BEFORE attributing any failure to your change (L306).

**#174 (B1473, from L314) - A DIAGNOSTIC MUST READ ITS OWN PROBE, AND PROVE THE PROBE RAN.** Never infer a specific result from an aggregate signal that has other contributors, and never interpret a search whose probe can be silently skipped. **Lineage:** `bisect_test_polluter.py` ran `pytest -x [chunk] [probe]` and read the verdict from the run-wide summary; `-x` aborted at the first of 172 unrelated failures so the probe never executed, and the summary's failure text reflected those failures - producing a confident conclusion from a run that tested nothing (L314). **Enforcement:** assert the probe's own result line is present; an absent result is INCONCLUSIVE, never a pass.

**#175 (B1473, from L288+L294+L297) - SHIP THE DIAGNOSTIC BESIDE THE HEADLINE NUMBER.** A pass-count invites "is the bar right?" and cannot answer it. Every gate-screen result publishes (a) the SENSITIVITY CURVE across the threshold, (b) a LEAVE-ONE-OUT contribution table, and (c) for any roster used in portfolio construction, EFFECTIVE BREADTH beside the cell count. **Lineage:** 23 was reported at one Sharpe threshold for weeks; the curve shows marginal yield is steepest exactly at the bar (L288). Leave-one-out showed `profit_factor` and `sortino` uniquely reject ZERO cells, so a "five-gate screen" is three and its apparent defence-in-depth is correlation (L294). De-dup by (ticker, entry_date) Jaccard measures SIGNAL overlap and says nothing about RETURN correlation: 13 cells behave like ~2.9 independent bets (L297).

**#176 (B1473, from L291+L295+L300+L309) - MEASURE THE DIRECTION; DO NOT DERIVE IT, AND DO NOT GENERALISE FROM ONE.** (a) When a change alters BOTH a threshold and the sample a statistic is computed on, the net direction is not derivable by inspection - report the CHURN (in/out), never only the net (L291). (b) A count is meaningless without its FUNNEL STAGE; intermediate counts move opposite to final counts whenever a later stage is sample-size sensitive, and BH-FDR always is - I sized an option at "union = 37" from the gate stage when end-to-end it was fewer (L295). (c) An implausible coefficient is a SPECIFICATION ALARM, not a finding - a market beta of 6.2 on an equity strategy meant the series was trade VOLUME, not returns (L300). (d) One observation licenses a hypothesis, never a characterisation: "exit selection is noise" came from a single pair; across 32 replicates it is 94% STABLE (L309).

**#177 (B1473, from L298) - POPULATION COUNTS COME FROM A SUM-ASSERTING PARTITION.** Any headcount of a registry (strategies, tests, tickets) is published only from a script that partitions the FULL population into disjoint buckets and ASSERTS the sum equals the total. An unconstrained count is an opinion and can drift indefinitely without ever contradicting anything. **B1478 amendment:** the sum-assertion is necessary and NOT sufficient -- it catches missing and duplicated members, never MISCLASSIFIED ones. When a new category is added to config, the partition that reads config must gain it in the SAME batch, and every figure quoted in one statement must come from ONE run of ONE artifact: mixing a config count (12 disabled) with a script count (196 backlog) hid a 3-member misclassification behind a passing assertion (L328). **Lineage:** "147 of 154 failing strategies were never tuned" was repeated across batches; the partition gives 222 = 17 roster + 9 retired + 196 backlog, and neither 147 nor 154 reproduces (L298).

**#178 (B1473, from L287+L290+L293+L305) - NAME AND WIRE CONFIGURATION HONESTLY.** (a) Name a gate for what it COMPUTES, not for the config key it borrows - `sharpe_per_regime` computes ONE pooled Sharpe and the misnomer propagated a false premise to the owner (L287). (b) When config exposes tiered thresholds, DECLARE which tier the gate set implements and justify per-key deviations; the live set silently mixed per-regime and overall bars on one pooled sample (L290). (c) "Alive" means CAN REJECT SOMETHING, never IS MENTIONED SOMEWHERE - a mention-based liveness check is defeated by the diagnostic code written to investigate the dead key (L293). (d) When a document's item FORMAT changes, the counter changes in the same batch, verified against an independently derived expected value (L305).

**#179 (B1473, from L307+L317+L318) - INVARIANTS: ONE SOURCE, CONSTRUCTOR-LEVEL CHANGES, PINS LAST.** (a) An invariant asserted in more than one place has more than one truth - derive it once and import it; a duplicated pin halves protection, because the first copy to fail gets fixed and the second silently records the old world (L317). (b) When a strategy stops being bidirectional, change its CONSTRUCTOR (`_strat3` -> `_strat`), not just its branch value: a neutered branch keeps every structural property other tests assert about the old shape (L307). (c) When a count pin fails, the pin is the LAST thing to change - ask what the delta MEANS first, or a detector becomes a rubber stamp; raising 51 -> 53 before fixing the cause would have buried a live compliance gap (L318).

**#180 (B1473, from L304+L316) - ATTRIBUTE BEFORE INVESTIGATING; UNTRIAGED IS NOT STALE.** (a) Before blaming a PRODUCER for a cross-strategy anomaly, read BOTH consumers' gate expressions - two strategies sharing entries is far more often shared gates than a broken signal, and a producer hypothesis sends the investigation to the wrong file (L304). (b) A red test outside the enforced gate is UNTRIAGED, not presumed bit-rot: triage separates stale-pin from real-finding from lint-violation, and the "old failing tests are rot" prior let an S4-B713 compliance gap sit unreported for 12 days (L316).

**#181 (B1473, from L308+L315) - USE WHAT THE PIPELINE ACCIDENTALLY GIVES YOU, AND LABEL BEFORE PRUNING.** (a) When a pipeline SELECTS among options per unit then grades the winner, any pair of near-duplicate units is a FREE REPLICATE of the selection step - duplicates are usually treated as waste to delete, but they are the only within-pipeline measurement of its own reliability. Measure them before deleting them (L308). (b) When a measurement shows a published status OVERSTATES certainty, the first fix is to correct the STATUS, not to act on the underlying items: labelling is reversible, preserves the evidence, and states the uncertainty where readers meet it (L315).

**#182 VERDICT DENOMINATOR RULE (B1503).** Before stating any verdict about an object (strategy,
producer, module, dataset), enumerate that object's FULL parameter/dimension space and mark each
entry TESTED or UNTESTED. The verdict sentence MUST name its denominator - "0 of 20 combinations
across 2 of 6 producers", never "it fails". A verdict whose scope exceeds the measured scope is a
Truth-Standard violation even when every underlying number is EXECUTED, because the evidence
classes tag PROVENANCE and not SCOPE.

*Anti-theatre check (#136) - retroactive catches:* (1) B1502 "cannot clear the Sharpe bar" on 2 of
6 producers; (2) B1500 "16 of 41 strategies have nothing to tighten", concluded about PRODUCERS
having enumerated only GATE EXPRESSIONS; (3) B1500 "16 untunable" propagated into a revised
Phase-1 population of 25, a planning number derived from an over-scoped verdict. Does NOT overlap
#165 (invented numbers) or L361 (scope of ACTION) - this covers scope of CONCLUSION.

**#183 PRODUCER-OPTIMISATION ARTIFACT STANDARD (B1510, owner-locked).** Every strategy entering
S6-OPT-196 is reported through `scripts/producer_variant_table.py` in ONE 3-section artifact, so
results are comparable across strategies and nothing is reported ad hoc:

- **Section 1 - BOOLEAN FORMULA.** PRODUCER LAYER (P1..PN: the assignment, what it emits, and its
  PARAMETER with the production value) then STRATEGY LAYER (how the P-outputs combine, each clause
  tagged with the P it came from). Header states it is READ from source, never recalled.
- **Section 2 - TABLE A, parameter inventory.** Per P-id: producer, parameter, production value,
  band tested, subset-safe (free vs needs-resim), status, why-this-band, and a source-line
  `evidence` field. Required fields are test-pinned.
- **Section 3 - TABLE B, combination results.** GATED (6): pooled_sharpe, profit_factor, sortino,
  psr, min_trades_holdout, min_trades_full_period. DIAGNOSTIC (5): win_rate, payoff, expectancy,
  p, ci_lo. CONTEXT (4): fires, holdout n, full-period n, exit chosen in-sample.
- **Computed, never hand-written:** the #182 denominator, FULL FACTORIAL, combinations run,
  percent covered, and the free-vs-resim split.
- **`validate_spec()` blocks generation on formula<->Table A drift** in either direction; a SPEC
  without a `formula` is rejected. Pinned by `test_b1510_producer_artifact_standard`.

*Anti-theatre check (#136) - retroactive catches:* (1) B1507 P6 band silently narrowed to [50,200]
with no stated rule - the `derivation` + `evidence` fields make that unwritable; (2) B1502 "cannot
clear the bar" on 2 of 6 producers - the computed denominator catches it; (3) B1500 "16 of 41
untunable" concluded from gate expressions - Section 1's PRODUCER LAYER forces the producer read
before any verdict.

**#184 FACTORIAL NEVER TRAVELS ALONE (B1523, owner directive).** Any statement of a strategy's
combination factorial - in chat, a doc, or a commit message - MUST be immediately preceded by that
strategy's boolean PRODUCER formula (plan SS6.1 / CHECKLIST #183 Section 1). Use
`python scripts/producer_variant_table.py --strategy <name> --factorial`, which emits the formula
and the factorial together and **cannot emit one without the other**; the coupling lives in the
tool, not in remembering.

*Rationale:* a bare "4,000 combinations" is unreadable on its own - it invites argument about the
number rather than inspection of the structure that produces it, and it hides which parameters are
FIRE-ADDING (needing their own engine run) versus subset-safe (deriving offline). Showing the
formula first makes `20 engine runs x 200 offline = 4,000` self-evident.

*Anti-theatre check (#136) - retroactive catches:* (1) B1513 "8000 combinations across 26 exits?" -
the owner could not verify 4,000 without re-deriving the structure; (2) B1507 "why only 40
combinations" - the coverage fraction was invisible without the parameter classes; (3) B1517 "have
all 4000 been accounted for" - answering required the FIRE-ADDING vs subset-safe split, which only
the formula makes visible.

**#185 MONITOR-ARMED GATE (B1545, owner-directed).** A long-running job is not launched until its
REPORTING PATH TO THE OWNER is armed **in the same turn**: a scheduled status check (CronCreate) and
a completion PushNotification, deleted when the job ends. **MECHANICALLY ENFORCED** -
`scan_unmonitored_launch()` in `scripts/verify_turn_compliance.py` blocks any turn that backgrounds
a long runner without an arming call after the last user message.

*Why mechanical:* plan SS9 item 13 stated this in prose and I violated it THREE times after writing
it (L385 sentinel wrote only to a log; L392 exception-only instead of scheduled; L420 the A/B run
with no monitor at all). A rule applied only when remembered is not a control.

*Anti-theatre check (#136) - retroactive catches:* (1) B1544's A/B launch, no monitor at all;
(2) B1514's ladder, armed but exception-only so a tripped sentinel reached no one until asked;
(3) B1530's scaling arms, which died silently with no completion path. Pinned BOTH directions by
`test_b1545_monitor_armed_gate` - unmonitored trips, same-turn-armed passes.

**#186 MONITOR CADENCE, NOT JUST EXISTENCE (B1548, owner directive "ensure this never ever happens
again").** The arming call for any long-running job must promise BOTH a **PERIODIC** report
("every hour" / "hourly") AND that it is **UNCONDITIONAL** ("do not withhold", "silence is correct
only when nothing is running"). **Exception-only alerting does NOT satisfy the monitor requirement.**

*Why this exists on top of #185:* #185 asserts a monitor EXISTS. I then armed exception-only
monitoring anyway and #185 PASSED - the control existed, it just did not do what was asked. Armed
wrongly four times: L385 (wrote only to a log), L392 (exception-only), L420 (none at all), L424
(exception-only again, past #185).

*Mechanically enforced:* `scan_unmonitored_launch()` inspects the CronCreate prompt and rejects a
launch whose monitor lacks both markers. Pinned BOTH directions by
`test_b1545_monitor_armed_gate` - exception-only trips, periodic-unconditional passes.

*Anti-theatre check (#136):* retroactively catches L392, L424, and the first `4a528196` arming in
B1546 - all of which passed the existence check while leaving the owner uninformed.

The six items below were cited 94 times before being defined - drafted from
their LIVE gates (B2023) and merged on owner approval 2026-08-23 (B2030).
### #187 — UNIVERSE ARTIFACT VERIFIED AT LAUNCH (B1602 / L445)

**A config launch without a verified universe once cost 3.3 h × 2 searching an abandoned
A–C chunk** — 380 of 381 tickers started with A, B or C and nobody had looked at the list.

Any `run_phase1a.py` launch requires `verify_universe_artifact.py <tickers-file>
--compare-cube <baseline cube>` run **in the same turn**, exit 0, with the verdict pasted.
A deliberately narrow file (a timing slice) is permitted only with its narrowness stated
in writing where the run is recorded.

*Enforced by:* `scan_unverified_universe` (`verify_turn_compliance.py:589`), blocking.
*Lineage:* L445; `r5_universe_381.txt`; the B2018 Stop-hook fire on the sw30/sw50 launch.

### #188 — A MISS ACKNOWLEDGED IS A MISS RECORDED (B1573 / L-Phase-5 arc)

**Acknowledging a miss in prose is not recording it.** A response that admits an error,
a stale claim, or a skipped step and moves on leaves the miss with no durable artifact —
the exact failure Phase 5 exists to prevent.

Any turn whose response acknowledges a miss must, in the same turn, carry the Phase-5
artifacts: LEARNINGS entry + CHECKLIST item or explicit "compliance failure against item
N" + EXECUTION_QUEUE ticket + fix-or-ticket (+ mechanism per #236).

*Enforced by:* `scan_unrecorded_miss` (`verify_turn_compliance.py:3883`), blocking.
*Lineage:* B1577 (the gate's first catch: a monitor tick acknowledging nothing).

### #189 — NO UNTESTED CAUSE (B1587 / L455)

**A hypothesis presented as a finding is a fabrication, and a wrong cause is worse than
no cause — it closes the investigation.** L455's "probable cause is the warmup guard" was
disproven by one command; the affected rows sat at bars 799–1158.

If a cause can be tested with a command you already know how to run, RUN IT before naming
the cause. If it cannot be tested cheaply, the cause is **UNKNOWN — RCA NEEDED**, ticketed.
A causal claim never enters a durable artifact without EXECUTED evidence beside it.

*Enforced by:* `scan_unverified_cause` (`verify_turn_compliance.py:393`), blocking on
cause-language with no run-evidence language in the same turn.
*Lineage:* L455; the B2019 misattribution (L617) is the newest instance of the class.

### #190 — A FIX TOUCHES ITS DOWNSTREAM ARTIFACT (B1602)

**A commit whose message says FIX / DEFECT / RCA and touches no downstream artifact is
either self-contained or an unrecorded invalidation — and the reader cannot tell which.**

Any FIX-class commit must touch a downstream artifact or a queue entry; a genuinely
self-contained fix states "self-contained" in its queue row, which satisfies the gate.
(Companion of #196, which governs re-checking conclusions the fix invalidates.)

*Enforced by:* the FIX-commit scan (`verify_turn_compliance.py:563`), blocking.

### #191 — ANCHOR THE RULE (B1597 / L464)

**A rule recorded only in LEARNINGS is a story, not a gate.** Measured: 24 L-entries
stated a generalized rule; 18 were referenced in neither CHECKLIST nor the skill — a
75 % orphan rate — and every orphaned rule decayed while every scripted rule held.

Every L-entry stating a generalized rule MUST, in the same turn, be anchored by a NEW
CHECKLIST item citing the L-number, or an explicit citation of an EXISTING item that
already covers it.

*Enforced by:* `scan_orphan_rule` (`verify_turn_compliance.py:464`), blocking.
*Lineage:* L464; carried in SKILL.md ("ANCHOR-THE-RULE RULE").

### #192 — AN ANCHOR IS A HOME, NOT A MENTION (B1599 / L466)

**Claiming a rule is anchored because an entry MENTIONS an item number is the anchoring
defect one level up.** L465 was called anchored because it mentioned #190 and #191;
neither item stated its rule — the mention pointed at a house with nobody home.

When citing an existing item as a rule's anchor, the cited item must actually STATE the
rule (or be amended in the same turn so it does). A number in prose is not an anchor.

*Tier:* judgment (prose) — no scan can tell a home from a mention. *Durability backstop:*
`test_b1971_no_new_dangling_checklist_citation` (shrink-only ratchet: a citation of an
undefined item can never be newly introduced).

### #193 — ARTIFACT PROVENANCE: characterise the contents, never trust the name (B1572 / L445)

Before any artifact becomes an input to analysis or a run:
1. **Open it and characterise its CONTENTS.** Never infer scope from a filename, a
   row count, or the doc that pointed at it.
2. **Reconcile against the artifact every other consumer uses.** Divergent counts
   for "the same" baseline mean someone is on a different artifact.
3. **Universes/entity lists — run the mechanical check:**
   `python scripts/verify_universe_artifact.py <file> --compare-cube <cube.csv>`
   Flags alphabetical skew, mega-cap absence, narrow coverage, provenance mismatch.
4. **Deliberate narrowness is fine — STATE IT** in the consuming doc. Unstated
   narrowness is the defect.

**Retroactive coverage (#136):** catches the B1571 `r5_universe_381.txt` miss on all
four checks; would also have caught any chunk-vs-merged substitution in the R5 rung
series. **Lineage:** a doc rule said "derive from the BASELINE ARTIFACT" (L378) and
was followed to an abandoned alphabetical chunk — 380/381 tickers starting A-C, no
MSFT/NVDA/GOOGL, 248 tickers the real baseline never ran.

**Extension (L478): a provenance correction is a SWEEP, not an edit.** When an artifact turns out
to be the wrong one, the number identifying it has already propagated - into cost estimates,
exclusion counts, and owner rulings. Fixing only where it was caught leaves the document
INTERNALLY CONTRADICTORY, which is worse than uniformly wrong: one reader gets 544 and another
gets 381 and neither sees a conflict. **Grep the NUMBER, not the file you were looking at** - and
RE-MEASURE every derived quantity rather than find-replacing it (41-of-381 was 22-of-544;
find-replace would have produced '41 of 544', a figure that never existed).

### #194 — ACKNOWLEDGED MISS => LEARNINGS ENTRY, SAME TURN (B1573 / L446)

**If a response admits an error, it gets an L-entry in that same turn.** Severity is not the filter.

Trigger phrases (any of): "I was wrong", "retract", "correction", "my error", "my bug",
"that was misleading", "I should have", "caught by preflight/the hook".

**Then, per Phase 5, one of:**
- a NEW CHECKLIST item (must pass #136 retroactive-coverage), OR
- an explicit note "compliance failure against existing item N".
Silence on both is the violation.

**Mechanically enforced:** `scan_unrecorded_miss()` in `scripts/verify_turn_compliance.py` blocks
turn-end when acknowledgement language appears without LEARNINGS.md being modified.

**Retroactive coverage (#136):** catches all 12 unrecorded misses enumerated in L446, including
the 5th instance of the monitor-cadence class (L420/L424) and the twice-repeated commit-message
shell-quoting error. **Lineage:** big findings got entries, small ones did not - and the small
recurring ones are precisely what a written record prevents.

### #195 — NO UNTESTED CAUSE: run the probe or say UNKNOWN (B1587 / L455)

**A hypothesis presented as a finding is a fabrication.** Labelling it "probable" does
not fix it - the reader still receives a cause.

1. If a cause can be tested with a command you know how to run, **RUN IT FIRST**.
2. If it cannot be tested cheaply, say the cause is **UNKNOWN** — and **TICKET IT**
   as `UNKNOWN - RCA NEEDED` in EXECUTION_QUEUE (owner directive 2026-08-16).
   Stating UNKNOWN without a ticket turns an open question into a closed one:
   the investigation stops and nothing records that it must resume.
3. **Never** put an untested cause in a durable artifact (queue, LEARNINGS, doc,
   commit message) - those are read later by people who will not re-derive your
   confidence.
4. A wrong cause is worse than none: it closes the investigation.

**Mechanically enforced:** `scan_unverified_cause()` in `scripts/verify_turn_compliance.py`
blocks turn-end on cause language without evidence language in the same turn.

**Retroactive coverage (#136):** catches L455 (the `i<250` warmup-guard hypothesis,
disproved by one command); L450 (a stall "explained" by falling RAM before CPU was
sampled); and L438 (a network call inferred from a log string without reading the callee).

### #196 — AFTER A FIX, RE-CHECK WHAT WAS ALREADY DECIDED (B1595 / L462)

**A fix can invalidate a conclusion the defect itself left intact.** While the bug stood, the
numbers were self-consistent; correcting it breaks that consistency for anything already shipped.

After ANY defect fix, before moving on:
1. **Enumerate the SHIPPED conclusions that depended on the old behaviour** — rosters, grids,
   docs, decisions. Grep for them; do not recall them.
2. **MEASURE the overlap.** Do not assume a fix is purely additive.
3. **Ticket every affected conclusion for re-derivation**, or state explicitly why it survives.

**Retroactive coverage (#136):** B1593's `regime_flip` fix landed on Phase 1B roster row 2
`xs_momentum_with_smart_money_long` — one of only TWO ROBUST cells — whose backtested numbers were
`time_stop_20d`'s. The fix means deploying it would run logic never measured. Also catches B1589
(the 17pct Sharpe correction re-scaling every roster Sharpe against a 1.0 gate) and B1562 (the
end-anchored coverage change altering which tickers any prior run would have served).

### #197 — A RULE RECORDED ONLY IN LEARNINGS IS A STORY, NOT A GATE (B1596 / L464)

**MEASURED this session: 24 L-entries state a generalised rule; 18 are referenced in
NEITHER CHECKLIST nor the skill — a 75pct orphan rate.**

LEARNINGS is read when someone goes looking. CHECKLIST and the skill are read every turn.
An unanchored rule gets rediscovered by repeating the failure that produced it.

**Every L-entry that states a generalised rule MUST, the same turn, be anchored by:**
- a NEW CHECKLIST item citing the L-number, OR
- an explicit citation of an EXISTING item that already covers it.

**THE TEST (sharpened by L466): "if someone reads the CHECKLIST, will they encounter
this rule?"** — NOT "does this entry mention a checklist item". **Citing a rule is not
anchoring a rule.** An L-entry that references existing items is still an orphan when its
OWN generalised rule has no home. L465 mentioned #190 and #191 and was still an orphan,
because neither item carried its rule.

**Anchor to an EXISTING item when the new rule REFINES it** (as L466 refines this item);
open a NEW item only when the rule is genuinely distinct. One item per L-entry would bloat
the checklist into something nobody reads — which is this item's own failure mode.

**Mechanically checked:** `scan_orphan_rule()` in `scripts/verify_turn_compliance.py`.

**ENFORCEMENT TIERS (L468) — "anchored" is not "enforced".** Measured across this session's
additions: 3 AUTO-GATED, 1 tooled-but-manual, 3 prose-only. A CHECKLIST item is CONSULTED;
only a gate is ENFORCED. **When adding an item, state which tier it is in**, and promote it
to a gate if the rule is mechanically decidable. #187 and #190 were promoted in B1602;
#192 and #193 are judgement rules and stay prose — that limit is stated, not hidden.

**Retroactive coverage (#136):** flags all 18 orphans from this session — L433, L434, L435,
L436, L437, L439, L441, L444, L447, L448, L449, L451, L453, L454, L457, L459, L460, L461.
Every rule that HELD this session had a script behind it (#182, #185/#186, #187, #188, #189);
the ones that decayed were prose.

### #198 — WRITING A STANDARD: WALK THE FULL LIFECYCLE, NOT THE MIDDLE (B1598 / L465)

**A standard written from one traversal captures that traversal, not the process.**

The post-config standard was written immediately after an analysis, so it encoded the
analysis just performed — and omitted BOTH bookends: the pre-launch checks (universe
provenance, RAM ceiling, sweep-knob differentiation) and the post-fix re-check. Those
were invisible to the author because they had already happened.

**When writing or revising any standard, walk the FULL lifecycle and ask what is done
at each boundary:**
1. **BEFORE** — what must be verified so the work is not wasted?
2. **DURING** — what is being encoded (this is what you remember, because it is where
   the effort was).
3. **AFTER** — what must be re-checked because this cycle changed something?

**Then place each check where it will be READ IN TIME.** A pre-launch check filed under
post-config analysis is read too late to run — placement decides whether a check fires
(owner correction 2026-08-16).

**Retroactive coverage (#136):** catches the 5-step post-config standard (missing both
bookends AND the adversarial review), and the runbook's original §11 which documented
rationale without a runnable command sequence (L433).

### #199 — A CORRECTION DOWNSTREAM OF A GENERATOR IS TEMPORARY (B1600 / L467)

**Regenerating an artifact from a stale input does not refresh it — it re-imports every
defect the input still carries, including ones already fixed downstream.**

The Phase 1B roster's `regime_flip` label was corrected by hand (B1596). Re-deriving the
roster **re-selected `regime_flip` and re-applied the wrong label**, because the R5 cube
predates the fix and still holds time-stop data in that column.

**Before correcting any generated artifact, decide and RECORD where the fix belongs:**
1. **In the GENERATOR** — survives regeneration.
2. **In its INPUT** — survives, but usually means re-running something expensive.
3. **In the OUTPUT only** — temporary; the next regeneration reverts it. Legitimate ONLY
   when paired with a written note saying so.

**Picking silently is the failure mode.** And always **diff before promoting** a regenerated
artifact over a corrected one — overwriting directly reverts corrections while appearing to
improve the file.

**Retroactive coverage (#136):** catches the B1596 roster relabel, and any future
regeneration from the pre-B1593 cubes.

**Extension (L479): a CORRECT artifact in front of a WRONG generator is armed, not safe.**
`_sweep_100.txt` was right - rebuilt by hand from the 544 baseline - while `build_sweep_100.py`
still READ `r5_universe_381.txt`, the abandoned A-C chunk. Re-running the committed builder
would have replaced a correct universe with one sharing **31 of 100** tickers, and the runbook
said *"Rebuild ONLY if the 381-universe changes"* - the very trigger that would have fired it.
**After correcting an output, open the thing that PRODUCES it in the same turn.**

### #200 — PARSE THE WHOLE FILE BEFORE APPENDING; A GREEN CHECK ON UNPARSEABLE INPUT IS A SILENT SKIP (B1603 / L469)

**Two failures, one root: reading the TAIL of a collection instead of parsing it.**

1. **NUMBERING.** CHECKLIST items #187-#193 were appended without deriving the true maximum —
   a legacy item **192** already existed. The tail showed only my own additions.
2. **FORMAT.** LEARNINGS entries were written as `### L435 — title` when the convention is a
   bare `### L434`. **34 entries became invisible to
   `test_b1486_claude_md_banner_counts_are_fresh`**, which therefore "passed" for ~30 turns
   while the banner sat 34 entries stale.

**Before appending to any numbered or formatted collection:**
- **Derive the current MAX by parsing the WHOLE file**, never by reading its end.
- **Derive the existing FORMAT the same way**, and match it — do not invent one.
- **Check the parser that consumes it.** If a test extracts items by regex, confirm your
  addition MATCHES that regex.

**A green check on an unparseable input is not a pass — it is a silent skip.** A test that
cannot see your work will never fail on it. When adding to a collection a test reads, verify
the test's count CHANGED.

**And a MATCH COUNT is not evidence of presence (L472).** `grep -c` returned **12** for a
rule that was ABSENT - `202` matches inside `2026` and `2020`. Short numeric needles collide
with dates, versions and IDs everywhere in this repo. **Grep for the STRUCTURE that would
contain the thing** - a heading, a full identifier with its prefix - **and prefer an exact
`in` test over a count.** A count answers "how many strings matched", never "is it there".

**Retroactive coverage (#136):** catches the #192 collision, the 34 invisible L-entries, and
the ~30 turns of falsely-green banner checks.

### #201 — COST AND QUANTITY CLAIMS MUST BE COMPUTED, NOT ASSERTED (B1605 / L470)

**PROVENANCE HALF (S6-B1705e / B1801, owner-approved) - COMPUTED FROM WHAT?**

**`#201` asks whether a quantity was computed. It never asks what FROM.** `2.422` came out of
`rng.normal(1, 3, 30)` inside my own boundary probe and **satisfied `#201` completely**, because
*"measured"* was true of the arithmetic and false of the meaning. That probe's one real finding was
the BOUNDARY (n=29 -> None, n=30 -> a value); **the number measured nothing and was quoted as though
it did.**

- **Any number quoted from a probe names its input.** A figure from `rng`, `random`, or a hand-made
  fixture is labelled **SYNTHETIC at the point of quotation** - not in a footnote, not in the
  method, where the number is.
- Enforced by `scan_synthetic_provenance`: a decimal in measurement language + a generator in the
  tool calls + no `SYNTHETIC` label. **The escape is one word**, which is the whole point - the
  label was the only thing missing when `2.422` was retracted.
- **It cannot tell which number came from which call** and does not pretend to. It asks the cruder
  question - *this turn ran a generator and quoted a figure as measured; say which.*
- **A synthetic probe can still produce a real finding.** The boundary was one. **Separate the
  STRUCTURE a fixture demonstrates from the VALUE it produces** - the first can be evidence, the
  second almost never is.

**Item #195 covers untested CAUSES. It never covered unmeasured NUMBERS — and numbers drive
decisions at least as directly.**

*"Costs nothing — same runtime"* was stated about a **3-year** window against a **2-year**
baseline. It cost **50% more**: 5.00 h vs 3.33 h per config, ~50 h vs ~33 h for the sweep.
**The arithmetic was one multiplication**, and the owner had specified the 2-year window on
runtime grounds in the first place.

**The recurring shape is substituting a RATE for a TOTAL.** Cost per sim-day was identical
either way — that part was true — but there were 1.5× as many days. Same class as quoting a
per-call ratio as a wall-clock saving (L432), a spot RAM reading as a ceiling (three times),
or a cold JIT timing as steady state.

**Before any claim of the form "costs nothing / same / negligible / free / roughly the same":
do the arithmetic and SHOW it.** If you cannot, drop the claim.

**Mechanically enforced:** `scan_unmeasured_quantity()` in `scripts/verify_turn_compliance.py`.

**Retroactive coverage (#136):** catches the "costs nothing" claim verbatim, and the three
rate-for-total substitutions above.

### #202 — READ THE SPEC BEFORE REPORTING THE RESULT (B1608 / L471)

**Every verification habit in this repo checks code against REALITY — does it run, does it
reproduce, is the artifact right. None checks code against INTENT.**

`tighten_breaker_block.py` applied all six admission gates and emitted PASS/FAIL, while
plan section 10.1 specifies Step 1 produces **"ranked combinations"** and Step 2 produces
**"gate verdicts"**. "0 PASS across 400 combinations" was reported as a Step-1 result when
**Step 1 can never produce a PASS**. Not a bad result — a category error.

**Before reporting what any component produced:**
1. **Read what its phase is SPECIFIED to produce** — in the plan, not from memory.
2. **If the output shape does not match the spec**, that is a DEFECT in the code or the
   plan. Say so. Do not report the number.
3. **When a design was decided earlier, re-read the decision.** Reconstructing it from
   conversation produces a worse version — this drifted across ~20 turns before the owner
   caught it.

**Retroactive coverage (#136):** catches the "0 PASS" reports, and the drift where Step 1's
window and universe were re-argued from scratch while section 10.1 already held the answer.

### #203 — A SWEPT LEVEL THAT CHANGES NOTHING IS A WASTED DIMENSION (B1610 / L473)

**MECHANICALLY GATED:** `python scripts/verify_grid_bands.py <grid.json>` — exit 2 on any
adjacent level pair that moves the outcome in <10pct of parameter groups.

P3 `tail_n` was swept at `[3, 5, 10, 20]` through **400 graded combinations across two
configs** before the owner asked why three levels returned the same 68 fires.

**MEASURED when the question was finally asked:**

| | cfg1 | cfg2 |
|---|---|---|
| `tail_n` 10 -> 20 changes the outcome | **0 of 50 groups** | 2 of 50 groups |
| 200 combinations -> distinct outcomes | **57** | 79 |
| redundant | **72pct** | 60pct |

**The band was not broken — it was MISPLACED.** `tail_n` moves fires from 4 to 420 across
its full range, but the four sampled levels admit 39.8 / 68.8 / **98.6 / 100.0** pct. The
region that discriminates is **1-3, below the band's floor**; `tail_n=2` alone cuts 73pct.

**Root cause is documentary.** The plan's own derivation for P3 reads *"measured rank of
qualifying event was 1-4 (B1501); band spans that."* **It does not span that** — its floor
is 3, the top of the measured range. Nothing compared a band to its own stated derivation,
and nothing checked afterwards whether each level had done anything.

**Deeper cause: `tail_n` is COLLINEAR with `age_bars_max`** — Spearman **+0.881** between
event rank and age in bars (median age 49 bars at rank 1, 416 at rank 5, 750 at rank 10).
Both cap RECENCY, one in events and one in bars. So `age_bars_max=180` had already removed
every high-rank event and `tail_n` had nothing left to cut. **The three top-ranked
combinations are not merely equal in count — they are the SAME 68 FIRES**, which is also why
their Sharpe and `ci_lo` were byte-identical.

**Before reporting a grid:** run the band check. **After any re-band:** re-grade — for a
SUBSET-SAFE parameter that is offline and **MEASURED at 15.3 s per config**, not an engine run.

**Declare the PRODUCTION ANCHOR** (`--anchor tail_n=20`). An anchor is carried so the baseline
reproduces, not to discriminate; without a way to say "inert on purpose" the gate fires forever
on a deliberate retention, and a gate that always fires is a gate nobody reads.

**Retroactive coverage (#136):** B1544 (*"uncapping was a no-op"* — a shipped change with zero
effect, found only after the fact); S6-B1576b (*"a 20-config sweep could silently run 20
IDENTICAL configs and nothing would surface it"* — the same class at config level, raised as a
concern and never given a test); B1541 (a cache that existed but was OFF).

**EXTENSION (B1691 / L495): an ASYMMETRIC band needs a stated reason that is not "I think this
direction wins".**

`swing_length` was banded `[10, 20, 30, 50]` - **ONE level below production, TWO above** - because
I believed higher `swing_length` means fewer, more significant swings and less noise, so I sampled
the direction I expected to win. **A band shaped by a directional hypothesis cannot test that
hypothesis; it can only confirm it.** If the optimum sits below 10, the band reports "lower was
worse" having never looked.

`tail_n` above is the same failure with a measured outcome: it floored at 3, was re-banded to
`[1,2,3,5,10,20]`, and **2 - a level that had not previously existed - won BOTH wave-1 top-10s.**
I re-banded that parameter and did not ask the same question of its neighbour. Band is now
`[5, 10, 20, 30, 50]`.

**The test: could this band return an answer you did not expect?** If every level sits on the side
you predict wins, the search is a confirmation, not a measurement.

### #204 — CHECK THE UNITS ON BOTH SIDES OF A RATIO (B1610 / L458)

`trades_per_year = 252 / avg_hold` divided **252 TRADING days** by a **CALENDAR-day** hold.
Every annualised Sharpe in the project was **17.1pct too low**; correcting it moved cfg2's best
from 1.860 to 2.239 and PASS from 5 to 9. The formula was never wrong-looking — both sides are
"days".

**Whenever a constant meets a measured quantity, name the unit of each out loud before
dividing.** Calendar vs trading days, bars vs sessions, per-call vs wall-clock, rate vs total.
The rate-vs-total instance of this class is #201.

### #205 — A WRAPPER OR MECHANICAL REWRITE MUST PIN THE UNWRAPPED PATH (B1610 / L440, L452)

(a) **Rewriting N call sites mechanically ships a test that the NO-OP path is byte-identical.**
33 producer guards were added at once; a single inverted guard would have silently deleted
every signal, and the only thing that could catch it is pinning the full key count (512) with
an empty skip set.

(b) **Overriding a dunder makes every internal use of that operator recursive.** `GuardedSignals`
overrode `__contains__`, whose own body began `if key not in self` — infinite recursion, caught
on the test's first run. Inside a class that overrides `in` / `[]` / `len` / `==`, call the base
explicitly (`dict.__contains__(self, key)`).

*Not its own item per the anti-theater guard (#136): (b) has ONE instance, so it rides with (a)
rather than inflating the checklist.*

**Extension (L480): a VARIANT must call the same helper as the base.** When adding a
parameterised variant of existing behaviour, extract ONE function and call it from both paths.
A copy-pasted variant loop is free to drift from the base - which is how `regime_flip` (L461)
and the grader-vs-engine gap (L475) happened. Assert the helper is called from BOTH sites, or
'shared' is an intention rather than a fact.

### #206 - A LENS IS DEFINED BY ITS QUESTION, NOT BY THE AXIS IT FIRST PAID OFF ON (B1611 / L474)

The post-config anomaly sweep already carried a duplicate-collapse lens - *"are 'distinct'
columns byte-identical?"* - and it had already found **26 exits collapsing to 23 effective**.
The identical question asked of the PARAMETER axis would have found `tail_n` immediately.
**It was never asked.** The lens was written against the axis where it was discovered and
stayed there, so a grid whose levels collapsed 3-into-1 passed an anomaly sweep whose entire
purpose is catching collapse.

**When a check earns its place, enumerate every axis its question applies to** - exits,
parameters, tickers, dates, regimes - **and either apply it or record why it does not.**

**And a lens SET is only ever complete relative to the failures you have already had (L487).**
After each defect, map it against the existing lenses; if none names it, the set is short by
one. The adversarial review ran **7** lenses while four of this session's dominant classes -
Executability, Fail-open, Self-referential verification, Completion-vs-artifact - had no lens
and shipped anyway. **A lens list that grows after a failure is being used; one that never
grows is decoration.**
Writing a general test against one axis converts it into a special case, silently.

**Extension (L481):** when a rule is discovered, SWEEP for its other instances the same turn. L475 was recorded, anchored in #207 and gated - with the gate scoped to SWEPT PARAMETERS, so it could never have found the identical defect sitting in the exit layer. An anchored rule with a narrow gate feels like closure and is not.

**Retroactive coverage (#136):** `tail_n` 3-of-4 levels inert (L473) despite the exits lens
existing; the `regime_flip` silent degradation (L461), where "does anything fall back without
saying so" was asked of producers but not of exit methods; the B1119 doc-sweep suspension,
where the per-turn sweep was applied to code turns but not to CSV-analysis turns.

### #207 - A SWEPT PARAMETER THE ENGINE CANNOT APPLY IS NOT A RESULT (B1612 / L475)

**MECHANICALLY GATED:** `python scripts/verify_engine_implemented.py` - exit 2 when a swept
parameter is neither engine-reachable nor DECLARED unimplemented with an open ticket.

Offline grading is what makes a 4,000-combination sweep affordable. It is also why the search
space can contain gates **the engine cannot apply**: the grader will happily simulate a filter
that exists only inside itself, and every number it produces will be internally consistent.

**MEASURED: 4 of 6 swept parameters were GRADER-ONLY** - `close_mitigation` (never passed to
`_smc.ob`), `tail_n` (hardcoded `.tail(20)`), `age_bars_max` (the breaker loop has no age filter
at all), `break_pct_max` (zero engine occurrences). Only `swing_length` and the EMA span reach
the engine, both through `config` env knobs.

**Two traps this closes.** First, a *near-miss name*: `event_recency_bars=90` exists in the same
function and looks like the age cap - it governs a DIFFERENT signal (`smc_ob_bullish_active`),
not the breaker loop. Second, an *absence has no token to grep*, so P4's check asserts the loop
contains no age filter rather than matching a string.

**Before admitting any swept combination:** implement its parameters in the engine, then re-run
and confirm the cube reproduces the graded fire set. Otherwise the live strategy does not
reproduce its own backtest.

**Retroactive coverage (#136):** `regime_flip` (L461) - numbers carrying a label whose logic
never ran, the same defect one stage later; the "wired means engine-consumed" class where a
grep for code presence produced ~150 false RESOLVED claims; B1335 rule 2, MECHANISM-EXISTENCE,
which required evidence a cited mechanism exists but was never pointed at swept parameters.

**Extension (L477): the gate must fire in BOTH directions, and a one-ticker probe cannot
judge a parameter.** When B1616 gave P2-P5 their wiring, this check failed just as loudly as
it would on a regression - the table said NOT-IMPLEMENTED and the source disagreed. A
one-directional check would have gone quietly green and left the table lying the other way.
**And `close_mitigation` scored 0 of 123 bars on AAPL** (`_smc.ob` returns byte-identical frames
for True/False across its first 1,000 bars) while moving the signal on **44 of 624 ticker-bars
across 8 tickers** - trusting the one-ticker result would have meant 'fixing' working code.
The 25-ticker sampling floor applies to *"does this knob do anything"*, not only to coverage:
both are questions about a DISTRIBUTION.

### #208 - AN INDEPENDENT RE-IMPLEMENTATION VALIDATES FIDELITY TO DATA, NEVER TO PRODUCTION (B1614 / L476)

`spot_check_trades.py` states its method as *"deliberately independent of the engine"* and
re-derives every producer from raw parquet. It reported **100/100 agreement on both configs**
while **four of six swept parameters did not exist in the engine at all**.

**It could not have found them.** The checker takes `tail_n`, `close_mitigation`, `break_pct_max`
and `age_bars_max` as ARGUMENTS - exactly as the grader does - so when it agreed, two pieces of
the same author's code agreed with each other. **The independence that makes it trustworthy for
one failure class is precisely what makes it blind to another:** it catches transcription errors,
PIT violations and threshold mistakes; it structurally cannot catch *"production does not do this
at all."*

**Every audit needs at least one check that CALLS THE PRODUCTION PATH** - not a re-derivation of
it. Re-derivation answers *"is the computation faithful to the data?"* Only invoking production
answers *"is this what the system will actually do?"*

**And TWO legs are not enough (L487).** A re-derivation compared against a recorded artifact
can only report THAT they disagree - never which is wrong - and a shared assumption is
invisible to both. **Three legs localise:** re-derivation + engine + recorded output. Any two
agreeing identifies the third as the defect. `spot_check_trades` ran two legs and reported
**100/100** while four swept parameters did not exist in the engine at all.

**And a citation can be a near-miss name.** P4's evidence field read `smc_ict.py:252
(event_recency_bars, S6-B1500a)`. Line 252 is `_smc.ob(ohlc, swings)`, which takes no such
argument, and `event_recency_bars` governs `smc_ob_bullish_active` - a DIFFERENT signal - while
the breaker loop has no age filter at all. **The citation grep-confirms and means something
else**, so the table read as though P4 had an engine anchor. Verify a citation by opening the
line, not by matching the name (L472's mirror: a match is not evidence of the RIGHT presence).

**Retroactive coverage (#136):** the 100/100 spot check while P2-P5 were grader-only; `regime_flip`
(L461), whose cube column was internally consistent and never compared to what the exit function
executed; the `wired=yes` grep heuristic that produced ~150 false RESOLVED claims.

### #209 - A TEST THAT CORRUPTS GLOBAL STATE IS A DEFECT EVEN WHEN IT PASSES (B1626 / L484)

My B1625 test called `importlib.reload(backtest.config)` to check that a config stamp follows the
configured value. A reload builds a **NEW module object**; anything holding a reference to the old
one silently diverges. `test_bug_30` and `test_bug_232` - unrelated, untouched - failed.

**A test that mutates process-wide state turns a green suite into a lottery on ordering.** It can
pass in isolation, pass in CI, and fail the day someone adds a file above it alphabetically.

**Set attributes directly and restore them in `finally`.** Never `importlib.reload` a config or
registry module inside a test. Never leave an env var, a module attribute, a cache, or a
module-level singleton changed on exit. If a test needs a different global, it owns restoring it.

**Retroactive coverage (#136):** today's reload breaking two unrelated tests; S6-B1601e
(`test_b1255_turn_gate_verifier` became sensitive to LIVE repo state and failed whenever an
unanchored L-entry was in flight); L449 (the miss gate scanned the whole transcript and fired on
compliant turns) - all three are a check coupled to state it does not own.

### #210 - REPLACE THE WHOLE FUNCTION; DO NOT PATCH BY OFFSET (B1626 / L484)

Repairing that same test, my patch computed an `end` offset from `t.index(anchor, start)` - the
anchor matched an **earlier** occurrence, and the replacement duplicated a block into a
`SyntaxError` caught at collection.

**In a file of thousands of lines, string-offset surgery is not a safe edit.** Replace a whole
function or a whole block bounded by its `def`, assert the replaced region is unique, and
`ast.parse` the result before writing.

**Retroactive coverage (#136):** today's duplicated block; B1614's dropped closing brace in
`producer_variant_table.py` (a mechanical string replace that broke the module, caught by the
pyramid); the CHECKLIST numbering collision where #187-#193 were appended while a legacy 192
already existed.

### #211 - A CLASSIFIER IN FRONT OF A GATE MUST FAIL CLOSED (B1626 / L485, L482, L483, L481)

`scan_orphan_rule` classified an L-entry as rule-bearing by looking for one of **three exact
phrases** (`generalised rule`, `generalized rule`, `**rule:**`). Anything worded differently was
"narrative" and skipped. MEASURED: **L481, L482, L483 and L484 all state generalised rules, none
contain those strings, and all four went unanchored across four consecutive turns while the gate
reported clean.**

**A gate that only fires when I use its vocabulary fires when I am already thinking in its terms -
exactly when it is least needed.**

**When a gate must decide whether a thing is in scope, the default answer is YES.** Being excused
requires an explicit written opt-out (`**record-of-fact**`), because a decision someone had to
write down is auditable and a default is not.

**This is the same shape as every defect this week** - each was a component that failed OPEN and
produced a number instead of an error: a comment satisfying a code check (L482), a missing
parameter skipped by the band gate (L482), a wrong file found by the grader (L482), a dropped
ticker vanishing (L483), an exit falling back to a time stop (L481), a gate scoring "unknown"
higher than "known bad" (L484). **Where the open default cannot be removed, replace the assumption
with a measurement (L483).**

**Retroactive coverage (#136):** this gate missing 4 of 4; `verify_grid_bands` dropping an absent
parameter and printing PASS; `verify_engine_implemented` matching a token inside a comment.

### #212 - A LONG RUN MUST SURVIVE ITS PARENT, AND BE PROVEN TO (B1627 / L486)

`nohup ... &` from the tool harness does NOT detach: the parent shell exits, the child dies with
it, the output directory is empty, and the harness reports **exit code 0**. MEASURED: a 2-year
smoke was killed at **simulated day 25 of 504** and reported success.

**Before any multi-hour launch, DEMONSTRATE the mechanism on a short job:** launch it, let the
turn end, and confirm from a LATER turn that the process is still alive (`Get-Process`) and the
log mtime is advancing. A launch mechanism that has not survived a turn boundary in THIS session
is unproven, regardless of how it worked before.

**Retroactive coverage (#136):** today's day-25 kill; S6-B1535b (a shell-function wrapper turned a
process kill into EXIT=127); S6-B1529a/S6-B1535a (both concurrency arms produced no valid
measurement after the launcher died).

**Companion:** the same launch must arm its monitor in the SAME invocation (#185) - not as a
preceding step, and never retroactively for a job that has already ended.

### #213 - A CHECK'S SUFFICIENCY CAN BE A FUNCTION OF A FLAG (B1632 / L487)

Asked what the 50-trade spot check covers, the honest answer turned out to be **"enough, because
of a flag"**. `smc_breaker_block_long` gates on two OHLCV-derived signals, so OHLCV coverage looks
complete - but **tier GATES ENTRY** (LOW -> 0.0 size -> the trade is SKIPPED, L418/B1544), which
would make `smart_money_score` an unchecked ENTRY input. It is not one, solely because
`backtest.py:2379-2380` sets `size_pct = CUBE_ISOLATION_SIZE_PCT` under `--cube-isolation`.

**Flip that flag and the same check becomes insufficient, silently.** At Phase 1B, with tier
sizing live and the full roster running, OHLCV-only coverage stops being adequate and nothing in
the check would say so.

**When a verification is judged sufficient, write down WHICH CONFIGURATION makes it sufficient**,
and re-open the question whenever that configuration changes. A coverage claim without its
conditions is a claim about one run, presented as a property of the check.

**Retroactive coverage (#136):** `--cube-isolation` bypassing tier sizing (this instance);
`USE_SMC_PANEL_CACHE=False` keeping an 11.5pct divergence dormant, so every reproduction check
holds only while the flag is off (B1542); `STRATEGY_SUBSET_FILE` being the gate that enables demand
pruning, so omitting it loses BOTH savings silently and every timing measurement with it (L432).

### #214 - A CHECK MUST DECLARE WHAT IT CANNOT VERIFY (B1634 / L488)

The 50-trade spot check re-derives producers from OHLCV. For `smc_breaker_block_long` that is
complete coverage - **because the strategy reads two price-derived signals, not because the check
is thorough.** Applied unchanged to a smart-money, news, earnings or short-interest strategy, the
same check would certify a trade **without ever reading the input that gated it**, and the output
would look identical to a real verification.

**MEASURED: 185 of 222 strategies have at least one input the spot check cannot verify.**

**A verification must declare its own coverage, compare it against what the subject actually
reads, and REFUSE to certify the gap.** `scripts/verify_spotcheck_coverage.py` does this per
strategy and is fail-CLOSED (#211): an unclassified key counts as unverifiable, because an
unrecognised input is exactly the one nobody thought about. **Widening the classifier to silence a
flag is how a fail-closed gate dies** - each key was added only after reading what it is.

**This generalises #213.** #213 says a check's sufficiency can depend on a FLAG; this says it can
equally depend on the SUBJECT. Both mean the same discipline: sufficiency is a claim about a
configuration and a subject, never a property of the check alone.

**Retroactive coverage (#136):** the OHLCV-only spot check reporting 100/100 while four swept
parameters did not exist in the engine (L476); `--cube-isolation` bypassing tier so smart-money is
not an entry input HERE but is at Phase 1B (L487); the B1039 producer audits that measured one
signal family and were quoted as coverage of a strategy.

### #215 - A CLAIM ABOUT CODE STRUCTURE REQUIRES OPENING THE CODE (B1635 / L489)

**MECHANICALLY GATED:** `scan_unverified_structure` blocks a turn that asserts something is
**wired / not wired / implemented / absent / never called / hardcoded / grader-only** without a
single `Read`, `Grep`, `Bash`, `PowerShell` or `Glob` call in that turn.

This is the NARROW, honest version of *"verify against code, not documentation"*. The skill states
that rule in **4 places and gated it in none** - which is how `wired=yes` as a grep result produced
**~150 false RESOLVED claims**, and how `regime_flip` read a key nothing ever wrote for its entire
life. A gate cannot read whether a claim came from code; it CAN refuse a structural claim from a
turn that never opened a file.

**"I don't know" and "UNVERIFIED" both pass.** Only unsupported certainty is blocked.

**Retroactive coverage (#136):** the `wired=yes` heuristic (~150 false RESOLVED); B1593's
`regime_flip` fix asserted "threaded via signals_at_entry" in a comment while nothing wrote the key
(L481); my own claim that 4 of 9 scanners were unwired, which was wrong and came from a naive
substitution rather than reading `main()` (L489).

### #216 - THE RESPONSE LEDGER IS NOT THE LEDGER (B1635 / L489)

Owner: *"you were also supposed to ticket each rec in prev turn Q1 to Q5 but that was missed."*
Correct. B1634 produced **5 queue rows** covering Q1, Q3 and Q5 - **Q2 and Q4 got a disposition in
the RESPONSE table and nowhere else.** VERIFIED: no B1634 row mentions the engine leg, the lenses,
the orphan gate or the backlog sweep.

**The response is ephemeral.** It is not in the repo, not greppable next session, and not what
CHECKLIST #94 means by *"the queue is the ANCHOR"*. A disposition that exists only in chat is the
*findings-without-tickets* failure applied to dispositions instead of findings - and it is easier
to miss, because writing the row in the response FEELS like recording it.

**Every row of the end-of-turn LEDGER must have a corresponding EXECUTION_QUEUE row in the same
turn** - including rows whose disposition is "already done in a previous batch", which is exactly
the kind that gets summarised in prose and lost.

**Retroactive coverage (#136):** B1634's Q2/Q4 (this instance); B1119's 22-batch doc-sync
suspension, where work happened and the record did not; the B1248 review whose 9 findings were
doc-only until #94 was written.

### #217 - A PIPELINE'S EXIT CODE IS THE LAST STAGE'S, NOT THE GATE'S (B1637 / L490)

`python scripts/prelaunch_gate.py ... 2>&1 | tail -12; echo $?` printed **0** while the gate had
crashed with an `AttributeError`. `$?` was `tail`'s status. The traceback was visible in the output
and the exit code said PASS - and an automated caller would have seen only the code.

**When you are checking whether a gate PASSED, run it bare and read its own exit code.** No pipe,
no `tail`, no `head`. If output must be trimmed, capture the status first (`rc=$?`) and trim after.

This is the *Completion-vs-artifact* lens (L486) in its cheapest form: **the command returned, the
work did not happen.**

**Retroactive coverage (#136):** this instance; the 2-year smoke that reported **exit 0** after its
child was killed at simulated day 25 of 504 (L486); the `|| true` class that CHECKLIST #122 exists
for, where a silenced failure becomes a success.

### #218 - AN ARTIFACT A TEST READS IS PART OF THE TEST (B1638 / L491)

`test_b1610_inert_swept_level_is_detected` pins the historical **0-of-50** measurement by reading
`output_audit/b1589_cfg1_grid.json` and `b1608_cfg2_grid.json`. Both were **UNTRACKED**. The test
guards with `if not q.exists(): continue`, so **on a fresh clone it would skip and report GREEN** -
and a skip is indistinguishable from a pass in a summary line.

**A pin test whose evidence is not committed is a pin holding nothing.** This is fail-open one
level up: not a check that passes on bad input, but one that passes on ABSENT input.

**If a test cites a file, commit that file in the same batch.** Same reasoning as #124 - a claim
needs a linked evidence artifact - extended: the artifact must survive a clone.

**Retroactive coverage (#136):** these two grids (this instance); the AWS git-hook shims that do
not travel with a clone and must be installed by hand; `_sweep_100.txt` being correct while its
BUILDER read the abandoned chunk (L479) - in all three the repo does not carry what the check needs.

### #219 - A CONCURRENCY FIT IS `free - N x peak >= headroom`, NOT `N x peak < free` (B1646 / L492)

Launching wave 1 I checked `2 x 3,223 = 6,446 < 7,705 free` and called it a fit. **That treats the
workers as the only consumer of the free pool.** MEASURED six minutes later: free **1,920 MB**,
margin **-1,303** against the floor, with the workers merely at their expected size.

**Free memory is not a budget you may spend to zero.** The OS, its cache, and every resident
process draw on the same pool, and the figure moves - it read 6,847 / 7,813 / 8,258 / 8,031 /
7,856 / 7,940 / 7,823 / 7,787 / 7,705 across nine hourly samples.

**Compute `free - (N x peak)` and require an explicit headroom**, then RE-MEASURE after launch
rather than trusting the projection - the breach here appeared ~2 minutes in and would have been
invisible to a pre-launch check alone.

**And a HALT is a decision to stop ADVANCING, not automatically to destroy what is running.**
Killing a live run is irreversible; declare the halt, hold the next unit of work, report the
evidence, and let the owner choose.

**Retroactive coverage (#136):** this launch; the "3-config ceiling" derived at ~9 GB free that no
longer held at 6.5 GB (L486-adjacent, B1627); the pool=3 manifest entry that would have put EIGHT
processes against a 2-process measurement.

### #220 - A TEST MUST ASSERT BEHAVIOUR, NOT SHAPE (B1681 / L493)

Three tests in one session passed while the thing they guarded did not work, each asserting
something ABOUT the code instead of running it:

| test | asserted | why it passed anyway |
|---|---|---|
| B1593 original | two STRINGS appear in source | they did; nothing connected them, and `regime_flip` stayed a time stop for its whole life |
| B1622 replacement | `count(getattr(self, "_regime_by_date", None)) == 2` | there ARE two - **both fallback branches**, neither necessarily the path that RUNS |
| `test_b1610` pin | reads two grid JSONs | they were UNTRACKED, so a fresh clone SKIPS and reports green (#218) |

**The progression is the point:** *does the code say the words* -> *does the code have the shape*
-> still never *does this execute*. Each fix made the assertion more sophisticated and none made it
BEHAVIOURAL.

**Every pin test must, at minimum, run the thing and assert an OUTPUT that differs when the fix is
absent.** A count, a presence check, a signature check, a substring - all are proxies, and a proxy
can be satisfied by code that does nothing. If the behaviour is only observable in an expensive
artifact, say so in the test and add the cheap end-to-end that *is* affordable; a skipped
assertion and a passed one are indistinguishable in a summary line.

**Extension (L494): enumerate every PRECONDITION, and prove each arrives from the REAL caller.**
`exit_regime_flip` needs a regime series AND `entry_regime`; B1622 supplied one and the exit stayed
a time stop on 302 of 302 trades. **A fix that supplies N-1 of N required inputs is
indistinguishable from no fix** - and the isolated test hand-fed the missing half, hiding the
defect inside its own fixture.

**Retroactive coverage (#136):** all three rows above - and the only thing that caught the live
defect was building a cube and reading `exit_reason`.

### #221 - A RECORD THAT DESCRIBES CODE IS CHECKED AGAINST THAT CODE, MECHANICALLY (B1692 / L496)

Not a new rule - **the mechanical half of the GENERALIZATION MANDATE**, added because the prose
half failed three times in one session while the mandate sat in context.

Any hand-maintained artifact that describes code - a parameter table, a run manifest, a band, a
capability flag, a count - is registered in `scripts/verify_describing_artifacts.py` with the CODE
that is its authority. The turn gate runs it. **Adding such an artifact without registering it is
itself the defect.**

Compare **coverage, not order**: every real drift was a MISSING level, never a reordering. Fail
**CLOSED** on an unreadable authority - "could not check" has scored above "checked and found bad"
too many times this session.

**And the rule this serves: naming a failure class is not closing it.** When you write "this is the
third time X happened", that sentence is the trigger for a class-level gate in the SAME turn - not
a third instance fix with better commentary.

**Retroactive coverage (#136):** the `tail_n` band that denied the level which won both wave-1
top-10s; the `engine_implemented` flags stale since B1616; the manifest grid stale through two
separate band changes.

### #222 - A CONSTANT IS NOT A VALUE UNTIL YOU CHECK THE CALLER (B1698 / L497)

`roster_core.MIN_N = 30` is a DEFAULT. `tighten_breaker_block` passes `min_n=10`, so the floor that
applied was 10 and **zero cells ever hit it** - while I explained 70pct of the grid with it.

**Before citing any threshold, gate or limit as the one in force: grep its call sites and read what
is actually passed.** A module-level constant tells you the default and nothing about the run.

**Corollary - AN APPROVAL INHERITS ITS RATIONALE.** The owner approved a band prune on this wrong
mechanism. When the rationale is withdrawn the approval does not survive it: revert, re-derive,
re-ask. The owner approved an argument, not a diff.

**And when a verdict column exists, SPLIT BY IT before explaining an aggregate.** 210 "ungradable"
was 179 `NO_EXIT_SELECTABLE` + 31 `FAIL` + **0** `BELOW_POWER_FLOOR` - three different causes, and
the one I named had a count of zero.

**Retroactive coverage (#136):** this prune; the `regime_flip` fix that supplied 1 of 2 required
inputs (L494); the "3-config RAM ceiling" quoted from a measurement taken at different free memory.

### #223 - GATES THAT AUDIT REPORTING DO NOT AUDIT WORK (B1699 / L498)

`verify_turn_compliance.py` had TEN gates and **not one asked whether mandatory work RAN** - they
all check how it is reported or committed. A turn could skip an entire mandatory sequence and pass
every gate. **That is why "the rule was already written" kept being true while the rule kept not
happening.**

For any MANDATORY sequence, the artifact that proves it ran is a **ledger with a terminal
disposition per step**, checked mechanically. Silence is not a disposition. **B2520 AMENDMENT (owner
ruling 2026-09-01, L736): neither is SKIPPED.** From B1699 to B2520 this line read *"SKIPPED-with-reason
is"*, and that clause is what let nine steps be pre-written SKIPPED against a review batch that never
existed (L721). The only dispositions are DONE-with-evidence and N/A-with-a-reason; a step that could
not run is FAIL or OPEN and BLOCKS until a human dispositions it with evidence. See #288.
Items outside scope are marked N/A **in the ledger**, never filtered out of the scan - an exclusion
you cannot see is a fail-open.

**And: ticketing the need for a gate is not building the gate.** "Needs mechanical enforcement" in
a queue row is another sentence. Build it in the same turn, or say plainly that you did not.

**When a new gate fails, the first hypothesis is that the GATE IS RIGHT.** Seeding the ledger DONE,
or editing the pin test it trips, makes everything green in one edit and destroys the only
mechanism that was working.

**Retroactive coverage (#136):** the post-config sequence skipped four times; the drift class named
three times and fixed as instances; the GENERALIZATION MANDATE satisfied in letter by stating a
class while leaving siblings open. **B2520 addendum:** by 2026-09-01 the owner had asked SIX times
(B2177, B2192, B2198/B2208, B2211, S6-B2436, S6-B2515) and received six instance fixes, each closing
the one mechanism that had just failed while its siblings stayed open - the class is closed at #288.

### #224 - A GATE NOBODY CALLS IS DOCUMENTATION WITH AN EXIT CODE (B1702 / L499)

MEASURED: **16 gate scripts, 4 with an automatic caller, 12 built and never wired** - including
`prelaunch_gate.py`, which the skill describes as *"launcher-wired"* and which nothing invokes.

**Building a gate is half the work; the wire is the other half, and it belongs in the SAME turn.**
State the invoker explicitly - Stop hook, pre-commit, launcher - or label the script
**HAND-RUN-ONLY** so nobody mistakes it for enforcement. "It exists and returns the right exit
code" is not enforcement.

**And confession is not remediation.** Disclosing a gap in prose - "I built it and didn't turn it
on" - buys the credit of having seen it while leaving it open. The disclosure gets a TICKET and a
fix in the same turn, or it is not a disclosure, it is a hedge.

**Corollary on pin tests:** when a new gate makes an old assertion false, ask whether the property
got MORE true or less. Updating a test to a superseded contract is legitimate; editing one to hide
a live failure is not.

**Retroactive coverage (#136):** `verify_postconfig_complete` (built B1699, wired B1702 only after
the owner asked); `prelaunch_gate` still unwired; `verify_engine_implemented` / `verify_grid_bands`
/ `verify_spotcheck_coverage`, each built during this sweep and each hand-run only.

### #225 - AN ANALYSIS-ONLY TURN PASSES EVERY GATE AND CAN STILL BE A SILENT MISS (B1705 / L500)

MEASURED: three consecutive turns produced **ten findings and zero tickets**. Every mechanical gate
passed, because **Gate B triggers on MODIFIED TRACKED FILES** and those turns changed nothing on
disk. **Findings arrive in prose, and prose leaves no mtime.**

This is **B1119 recurring** - 22 batches of silent doc-sync lapse, for the identical reason, fixed
at the time with a sentence saying investigation-only turns still require the sweep. The sentence
did not survive.

**A turn that states a defect, a remediation, a recommendation, or an unknown owes a ticket in that
same turn - whether or not any file changed.** The trigger must read the RESPONSE, not the working
tree: scan for remediation language ("not built", "needs", "should be", "remediation:", "the fix
is") and require a matching queue entry.

**And the upstream cause: compressing work into fewer tool calls.** Reading part of a file, quoting
a constant instead of its call site, building an artifact without grepping the queue first. When
context runs short the corner that gets cut is verification - **so the response must say which
reads were partial**, rather than presenting a partial read as a finding.

**Retroactive coverage (#136):** the `OOS_MIN_N` two-floor bug (untickcted); the Step-1 holdout
breach (unticketed); `table_c`'s PASS column, re-introduced despite `S6-B1610f` already describing
it; B1119's original 22-batch lapse.

### #226 - BEFORE TRUSTING A GATE'S PASS, PROVE IT CAN FAIL (B1707 / L501)

**EXTENSION (B1836 / L561) - A SILENT GATE AND A CORRECT ONE ARE THE SAME OBSERVATION.**

**MEASURED while replacing `#201`'s mechanism: three bugs, none visible on reading, two of which
made the gate SILENT.** The clause splitter split on every `.`, so `169.347` became `169` and `347`
and **no clause ever contained a decimal**. The decimal matcher refused a sentence-final number, so
the gate went quiet on **the shape of its own recorded incident**.

- **That is why the fail arm is not optional.** A gate that has been broken into silence produces
  exactly the output of a gate that is working. **No amount of reading separates them** - only
  running the case it is supposed to catch.
- **ONE PATTERN, ONE DEFINITION.** The third bug: the decimal regex lived at TWO sites and I
  corrected one, so a pre-filter kept rejecting what the fixed loop would have caught. **A
  duplicated pattern is a divergence waiting for someone to fix half of it** - B1812's shape, where
  `keep_code` guarded one strip of two and the second consumed what the first preserved. Pin that
  there is exactly one definition.
- **Retroactive (`#136`):** B1812 (`keep_code`, one of two strips), B1798 (`_verdict_hits` raw `in`
  at one site), B1832 (`_DECIMAL` at two sites). **Three divergences, three half-fixes.**

**AMENDED B1951 (L597) - AN ENUMERATION NEEDS A CONTROL FROM OUTSIDE ITS OWN
SAMPLE.** A pattern written to enumerate a population encodes the examples that
were visible when it was written. **Four instances in one session, every one
running clean and returning a plausible number:** B1938 (occurrences vs
functions, 4 against 2), B1944 (a corpus dict omitted), B1945d (`^### L` while
the file also uses `## L`, missing 89 of 502), B1950 (escapes by one syntactic
shape, 6 of at least 9 - **missing three fixed in the two preceding batches**).

- **The quantity is right and only the POPULATION is short**, so nothing in the
  output says so - worse than an unmeasured guess, which at least looks like one.
- **Name a member you know exists and did NOT look at while writing the
  pattern, then assert the enumeration finds it.** B1950 would have failed
  instantly against `record-of-fact`.
- **Prefer a STRUCTURAL bound to a syntactic one.** B1950's escapes were
  unenumerable by regex and perfectly bounded by "every text-reading gate".

**AMENDED B1937 (L592) - IT IS NOT ONLY DUPLICATED PATTERNS. A GUARD COUNTS TOO.**
`safe_write_py` parses a candidate before writing, so a syntax error leaves the
file untouched. B1936 routed `test_unit.py` through it and wrote
`gate_incident_corpus.py` with a plain `write_text` **three lines earlier in the
same script** - SyntaxError, module stopped importing, **8 tests failed at
collection.**

- **Four instances this session, every one found by the enforcement layer firing
  on legitimate work:** B1904 (word-bounded both sides on evidence for one),
  B1905 (B1820 fixed the JSON artifact, not the table rendering it), B1925
  (B1880's heredoc strip in one launch detector, not its sibling), B1936
  (`safe_write_py` on one file of two).
- **Each fix was CORRECT where it landed.** The failure is that **the unit of
  the change was smaller than the unit of the defect**, and nothing in making a
  fix asks how many sites it governs.
- **Count the sites and PIN the count.** B1925's pin asserts the strip
  expression appears **at least twice** - that assertion is the whole remedy.

**EXTENSION (B1840 / L562) - THE PROOF IS ITSELF A PROBE, AND NOTHING WAS CHECKING IT.**

**EXTENSION (B1862 / L568) - PROVE-IT-CAN-FAIL APPLIES TO A SEARCH, NOT JUST A GATE.**

**MEASURED: watching a 200-ticker run for fires with `[0-9]+/200 passed` returned nothing, and I
reported "still in warmup" TWICE.** The screener's denominator is the PIT-ACTIVE universe - **185,
not the file's 200** - so the run had been firing on every one of 29 screen-days. **The monitor
carried the same pattern and would have reported "no fires" every 11 minutes, unattended,
confirming a launch blocker backwards.**

- **An empty result is indistinguishable from a wrong pattern**, exactly as a silent gate is
  indistinguishable from a working one (L561). **Only a POSITIVE CONTROL separates them.**
- **Mechanism: `scripts/grep_control.py`.** `search_with_control(pattern, haystack, control)`
  RAISES rather than returning `[]` when the pattern fails a control taken from the real data.
- **Retroactive (`#136`):** the `/200` denominator (B1861), `4,869` matched as a decimal when it
  carried commas (L556), and B1832's decimal matcher refusing a sentence-final number. **Three
  searches whose emptiness was read as absence.**

**EXTENSION (B1859 / L567) - A TICKET NAMES ONE GUARD; THE EXPRESSION HAS TWO.**

**MEASURED: `S6-B1847a` reported one defect in `(?<!\d)[.;](?!\d)` - the trailing guard split
file extensions. I fixed that guard and shipped a regex whose OTHER guard was also broken, and
older:** `(?<!\d)` refused to split a sentence ENDING in a decimal, so a figure inherited a source
from the next sentence. **Deleting it fixed both** - `(?!\w)` had made it redundant.

- **A ticket describes the symptom someone NOTICED.** A compound predicate has as many failure
  modes as it has terms. **Evaluate EVERY term against a case table before editing, and put the
  table in the commit** - the 6-case table here was computed BEFORE the edit, and it is what showed
  the first fix still failing 1 of 6.
- **Retroactive (`#136`):** B1812 (`keep_code` guarded one strip of two), B1798 (`_verdict_hits`
  raw `in` at one site), B1858 (this). **L561 names the duplication half - one pattern in two
  places. This is its inverse: two guards in one place, of which I examined one.**

**MEASURED: the fail-arm proof for the control-character gate was defeated by the control-character
bug it was testing.** The probe was written through a heredoc; the escape collapsed; the file landed
with a real `0x08`; **the gate's OLD arm caught it and printed `1 failed`** - so the run looked like
proof while **both new arms sat unexercised**.

- **`#226` says prove a gate can fail. It did not say the proof is above verification.** A probe
  states a precondition about its own input, and an unstated one is a claim. **Fourth instance of
  L556** after `4,869` (commas, not decimals), `jaccard 0.9993` (no measurement word), and
  `observed=` (did not bypass the miss precondition). **Each returned a flattering answer.**
- **ASSERT WHICH MESSAGE FIRES, NOT THE EXIT STATUS.** `1 failed` was accepted until the assertion
  TEXT was read, and it named **a different arm's line number**. A fail arm must name the message it
  expects.
- **EVERY FAIL ARM NEEDS A SILENT CASE.** A gate that fires on everything also fires on the probe.
  The must-NOT-fire probes are what proved ARM B keys on an `re` receiver rather than the method
  name - `t.split("\x1e")` is a plain string split and a first draft would have flagged it.
- **A GATE THAT RAISES WHILE BUILDING ITS OFFENDER MESSAGE IS SILENT ON EXACTLY ITS TARGET CASE.**
  ARM A used `n.lineno` on an `ast.Module`, which has none. Clean input never reaches that line,
  **so the repo passed and the arm looked healthy** - and the real instance fixed that same turn was
  a MODULE docstring. **Reading it would not have shown this; only the fail arm did.**

**EXTENSION (B1802 / L551) - A FAILING NEGATIVE ARM USUALLY MEANS YOUR MODEL IS WRONG.**

**MEASURED: `S6-B1705d`'s arm 4 failed because I had read the CALLER and not the function.** The
grader does `is_m = rc.in_sample(sub)`, so I concluded that was the enforcement point; in fact
`select_exit` slices `in_sample()` itself and says so in its docstring. Bypassing the caller's
filter bypassed nothing.

- **The positive arms cannot catch this.** They exercise the happy path, identical whether the
  mechanism sits at the call site or one level in. **Only the negative arm makes you NAME where the
  mechanism is - because you cannot break what you cannot locate.**
- **Two readings of a failing negative arm, and the second is more likely:** *the code does not do
  what you thought* / **your model of WHERE it does it is wrong.**
- **Re-read the function before changing the test.** Weakening the arm until it passes leaves
  something indistinguishable from never having written one - `#253`/L550's instinct in a new place.
- **A failing arm is a finding.** Retargeting this one produced a correction to an OPEN ticket:
  `S6-B1705c`'s *"there is no enforcement"* is true of the RANKING, false of the exit choice.

The `#225` gate returned `None` and looked green. It called `_entry_text`, **which does not
exist**, over `_read_entries()`, which returned **zero entries** - so the missing function was never
reached. **A gate returning "clean" over an empty input is indistinguishable from a gate that
works.**

**Feed every new gate a case it MUST reject, and watch it reject.** A gate never observed failing
has not been tested, it has been run. This matters most here because every response-scanning gate
(`#201`, `#215`, verdict denominators) reads `sys.stdin` via `_read_entries` and sees **nothing**
outside the Stop hook - they cannot be exercised by an ordinary invocation.

**And the companion rule: VERIFY YOUR OWN CLAIMED ACTIONS.** I wrote *"Reverting."* and did not
revert; the dead gate was still in the file a turn later. **Narrating an action is not performing
it** - when a response claims a state change (reverted, deleted, disabled, wired), the next command
confirms it, because the check costs one line and the false claim costs a commit.

**Retroactive coverage (#136):** this inert gate; the "reverted" prune that WAS run but was only
confirmed by luck; the `regime_flip` fix declared DONE while supplying 1 of 2 required inputs; the
post-config gate built and left uninvoked.

### #227 - COMPARING TWO RANKINGS MEANS COMPUTING THE RANK CORRELATION (B1716 / L502)

I compared in-sample and holdout rankings with a **top-10 overlap count**, got **0 of 10**, and
called it *"the signature of noise"*. The actual Spearman was **-0.779 / -0.865 at p < 0.001**.

**Zero overlap is consistent with rho = 0 AND with rho = -1, and those have opposite remedies.**
Noise means the search finds nothing; inversion means the pipeline systematically prefers what
fails. On the wrong reading I recommended ranking on in-sample Sharpe - which at rho = -0.8 selects
the WORST out-of-sample combinations.

**Compute rho (and its p-value, and the sign-agreement rate) before interpreting any two orderings.**
An overlap count discards direction and magnitude, which are exactly what decide the next action.

**And a corollary: a HALT declared on a wrong diagnosis is still worth declaring** - stopping was
right, the reason given was not. Re-state the reason when it changes rather than leaving the
original standing.

**Retroactive coverage (#136):** this finding; the "tail_n band moves 0 of 50 groups" reading that
needed the marginal-effect measure to become actionable; the cfg1-vs-cfg2 top-10 comparison that
counted shared rows rather than measuring agreement.

### #228 - A TRUE ANSWER TO A DIFFERENT QUESTION IS STILL A MISS (B1722 / L503)

Asked what had been done about CONTEXT COMPRESSION, I listed nine enforcement hooks. Every one
existed and worked. **Not one addressed the cause** - they catch symptoms. The response was fully
true and completely off-target.

**That is what makes this class dangerous: no evidence check can catch it.** Every number was
measured, every artifact real. The defect is the MAPPING from question to answer, not the content -
which is why the Truth Standard, the pyramid and all ten turn-gates pass a response like this.

**Before answering, restate the question in your own words, then check the answer against the
restatement rather than against the work you happen to have done.** If the response would be
equally true had the question been different, it is not an answer to this one.

**Second-order rule, which the owner had to point out separately: acknowledging a substitution
inside the same response that commits it is NOT recording it.** Every miss owes a LEARNINGS entry
plus a CHECKLIST or skill change in the SAME turn - including misses about how a question was
answered, not only misses about code.

**Retroactive coverage (#136):** this substitution; *"have all the hooks been built"* answered with
the 2 that were rather than the 7 that were not, until re-asked; the 30-turn audit answered with 3
turns.

### #229 - A LIMITATION YOU HAVE NOT TESTED IS AN OMISSION YOU HAVE NOT NOTICED (B1729 / L504)

I told the owner the execution-discipline skill loads as *"12 of 644 lines"*, framed the missing
the missing 632 as structural, and offered a design trade-off to work around it. **Invoking it delivers all
all 644.** The truncated copy I reasoned from was cut by COMPACTION - the re-invocation said
first line. **There was never a ceiling; there was an un-run tool call.**

**Before describing anything as a limitation - of a tool, a format, a budget, an API, a file
size - run the cheapest probe that distinguishes a LIMIT from an OMISSION.** Here that probe was
"invoke it and count", and it was available the whole time.

**The tell is a mechanism that explains your own failures.** Mine converted a fixable omission into
a property of the system, was self-consistent, fit every observation, and was wrong. **A story that
accounts for why you keep missing things deserves more scepticism than one that does not**, because
it is the one you have a motive to believe.

**Cost here:** the 632 lines hold `#182` verdict-scope, POST-FIX RE-CHECK, B1446
no-arbitrary-decisions, the tripwire table and anchor-the-rule - five rules violated this session
while being described to the owner as structurally unavailable.

**Retroactive:** this; the "response-scanning gates cannot be tested" conclusion that a
`TURN_GATE_TRANSCRIPT` argument dissolved (B1713); the "26-way exit selection causes the inversion"
hypothesis disproven by one group-by (B1717).

### #230 - A CLAIM ABOUT A CAPABILITY IS A CLAIM, AND NEEDS THE SAME EVIDENCE (B1731 / L505)

The Truth Standard's four evidence classes are stated in terms of DATA - counts, coverage, fire
rates, test totals. **Every worked example is a measurement.** So claims about the SYSTEM ITSELF
slip past: what a tool can load, what a format permits, what a budget allows, what a context window
holds. They feel like background rather than findings.

**MEASURED consequence:** I would never publish a cell count without running it. I published *"the
skill loads as 12 of 644 lines"* having run nothing - and offered the owner a design trade-off
built on it. Invoking the skill delivers all 644.

**Before stating what any tool, format, file, interface or limit CAN or CANNOT do, run the probe
that settles it, or label it UNVERIFIED.** The evidence classes apply unchanged; capability claims
are not a lighter category.

**EXTENSION (B1736 / L506) - TWO MORE SHAPES, AND THE ITEM'S OWN DIAGNOSIS APPLIED TO ITSELF.**
The three examples above are all about TOOLS. Two further shapes slipped past for that reason:
**(a) ARTIFACT SCHEMA** - proposing a split by a column an artifact does not have; **(b) COST** -
"seconds / cheap / one command", which is a quantitative claim already covered by `#201` had the
connection been reachable. **Four instances in one session, the last two AFTER this item existed.**
The item was read and applied to the shape its examples showed. **A rule is learned from its
EXAMPLES, not its abstraction** - so pick examples that differ in surface and agree only in
mechanism. Trigger: **before proposing any probe, name the ARTIFACT and the FIELD it needs, and say
whether you have opened it.**

**And this is a COMPLIANCE failure, not a new class** - Truth Standard rule 1 already says an
UNVERIFIED claim stated as fact is a fabrication. This item exists because the rule's examples all
pointed at data and I read the scope narrowly. **A rule whose examples share one shape gets applied
to that shape only.**

### #231 - A RULE WITHOUT A MECHANISM IS NOT SHIPPED (B1739 / L507)

**Owner directive: prose alone will not suffice - a rule earns its place only when something
enforces it.** THREE consecutive rules shipped as prose and needed the owner to ask before a gate
existed: B1723 (skill dropped from a 3-artifact request), B1725 (skills documented, never invoked),
B1736 (`#230` extension with no hook).

**Every turn that edits CHECKLIST.md or SKILL.md must also touch
`scripts/verify_turn_compliance.py` or `backtest/tests/test_unit.py`** - or state **PROSE-ONLY**
and say why a mechanism is not possible. Enforced by `scan_prose_only_rule()`.

**And the companion: a gate that checks a CATEGORY was touched does not check that every MEMBER was
handled.** `#225` fired only when the queue was UNTOUCHED, so one ticket satisfied it while other
findings in the same turn went unrecorded - the same any-vs-each gap the per-skill invocation gate
had. **Whenever a rule says "each" or "every", the gate must COUNT, not merely detect.** Enforced by
`scan_findings_vs_tickets()`, which counts distinct finding markers against S6-xxx rows added.

**What this would and would not have caught:** it catches all three prose-only instances above and
the one-ticket-for-three-findings turns. It does NOT judge whether the ticket written is the RIGHT
ticket - that stays judgment.

### #232 - A SILENT FALLBACK IS A PERMANENT FAILURE (B1744 / L508)

B1743's hook change shipped green and **did nothing for two sessions including a restart**. PROVEN
cause: the hook writes to a **cp1252** stdout on Windows; `SKILL.md` holds U+2192 / U+2264 /
em-dashes; the write raised `UnicodeEncodeError` at position 1695 - and **the `except Exception:`
I had added served the 12-bullet summary instead**, every turn, silently.

**The fallback written to make it safe is what made the failure invisible.** This is CHECKLIST #122
(`|| true` needs a paired success-check) at a larger scale, in code written while explicitly
reasoning about failure modes.

**Any `except` that substitutes a DEGRADED output must announce itself** - log to stderr, or make
the degraded output visibly say it is degraded. A fallback that looks like success will be served
forever.

**And verify through the REAL invocation path.** I tested with `input='{}'` through a UTF-8 pipe
and got 716 lines; the harness uses a cp1252 console and got 9. **Same script, different path,
opposite result.** For anything invoked by a harness - hooks, subprocesses, CI - reproduce its
**encoding, its stdin and its working directory**, not the convenient shell equivalent.

**Fix pattern:** write BYTES through `sys.stdout.buffer` with an explicit `utf-8` encode; never let
a console codepage decide whether a payload survives.

### #233 - ENCODE THE STEM, AND TEST THE GATE ON A PARAPHRASE (B1748 / L509)

`NARRATION_MARKERS` held `"reverted"`. The error it was built for said **`"Reverting."`** - and
`"reverted"` is not a substring of `"reverting"`. **The gate could never have caught the incident
that produced it.**

**When a rule is encoded as string matching, the strings come from the sentence you remember
writing - one sample of the class.** Encode the **stem** (`revert` + ed/ing/s/d), not the
conjugation.

**And test every marker gate against a PARAPHRASE of the incident, never its exact words.** The
exact words are the one phrasing that will not recur. A gate that passes only on its own lineage
example is fitted to a single string.

**Companion (2nd instance, with B1713/L501): a check whose input can only arrive from live plumbing
cannot be validated.** `scan_response_gates` read only `_assistant_text(entries)` and could not be
handed a recorded response, so the replay harness could not exercise it. **Every gate takes an
injectable input for its evidence source.**

**What this would and would not have caught:** it catches `E1` and any future marker gate written
from one remembered phrasing. It does NOT catch a gate whose CONCEPT is wrong - only its spelling.

**Measured consequence:** the replay scored **1 of 8** before these fixes and **2 of 8** after.

### #234 - RULES SAYING "EACH" GO THROUGH require_each (B1751 / L510)

**Five instances of one class, each patched alone:** `#225` on an untouched queue · the per-skill
gate satisfied by any Skill call · the runner stopping at the first violation · Phase 5 counting
queue rows only · and `scan_false_skill_status` **defined and never wired**.

**`if category_touched: pass` is the natural way to write a check, and it is wrong whenever the
rule says *each*.** Patching instances leaves the class open - which the GENERALIZATION MANDATE
calls non-compliant.

**Any rule whose wording contains "each" or "every" is expressed through
`require_each(rule, {member: satisfied})`** in `scripts/verify_turn_compliance.py`. It takes a
**dict** so every member must be enumerated - one cannot be silently omitted - and it names the
**missing members**, never "something is missing".

**Companion detection signal: count the occurrences of every gate's name.** One occurrence = the
definition only = never called. That check is one line and would have caught instance 5 two turns
earlier, on a file where 12-of-16-unwired had already been measured once.

**Phase-5 application:** `scan_miss_capture_complete` requires **LEARNINGS + CHECKLIST-or-explicit-
citation + queue ticket** on any stated miss, enumerated through the primitive.

### #235 - CITING A RULE IS NOT THE RULE RUNNING (B1753 / L511)

**MEASURED:** `#224` - *a gate nobody calls is not enforcement* - was a checklist paragraph plus
ten docstring banners **for its entire life**. No `scan_` function for unwired gates ever existed.
It was cited by number, repeatedly, as though citing it were the same as it working - **in the same
turn an unwired gate shipped underneath it**.

**A rule number in a response reads like evidence and is not.** `#224`, `#226` and `#231` were all
cited while the failures they describe kept recurring, because none had a mechanism until late.

**Before citing any CHECKLIST item as protection, name the function or test that enforces it - or
say explicitly that it is judgment-only.** An item with no named mechanism is a description of a
failure, not a defence against one.

**Companion, from the same turn:** when asked to CONFIRM coverage, MEASURE it. A 10-errors x
4-artifacts table took one command and found **9 of 10 complete with one real gap** - which the
assertion "yes, all covered" would have missed.

### #236 - PHASE 5 IS FIVE MEMBERS; THE FIFTH IS THE MECHANISM (B1756 / L512 / L513)

**A fully compliant Phase-5 remediation can leave its class unenforced.** B1702 touched LEARNINGS,
CHECKLIST, EXECUTION_QUEUE, `test_unit.py` and `verify_turn_compliance.py` - passed every rule -
and its remediation was **ten docstring labels**. The next day the same class produced a gate that
was defined, proven 5/5, committed and never wired.

**Phase 5's four steps never asked for a mechanism.** "Fix" means fix the INSTANCE. `#231` checks
that code MOVED, not that the CLASS is enforced.

**Fifth member, required: a `scan_`, a pin test, or an explicit `JUDGMENT-ONLY: <reason>`.**
Enforced via `require_each` so four-of-five cannot pass.

**Evidence it is not optional (L512):** between two catches of the same omission, the full skill -
containing ANCHOR-THE-RULE, which states the rule - was auto-injected on **every turn**. The
behaviour did not change. **A 14-line scanner caught both.**

**Companion:** the Phase-6 retroactive sweep has **no gate** and has run **zero times
autonomously** this session.

### #237 — RETROACTIVE SWEEP ON EVERY NEW RULE AND EVERY CLASS FIX (B1757 / L512-arc)

**A rule added without sweeping for existing instances leaves the siblings the
GENERALIZATION MANDATE calls non-compliant; a class fixed at one site leaves the site you
were not chasing.** The sweep that found these seven items missing was itself a #237 sweep.

Any turn that adds or tightens a rule, or fixes an instance of a defect class, states in
the response **what ELSE was scanned for this class, and what it found** — naming the
search executed, with a zero-findings answer stated as such (a zero is a finding).

*Enforced by:* the retro-sweep scan (`verify_turn_compliance.py:3426`), blocking.
*Lineage:* B1970 (the collector had the same bold-requirement as the gate being fixed);
B1971 (the sweep that found this item undefined); L603/L605.

### #238 - THE COMPLIANCE STATEMENT MUST CITE ITEMS, NOT EXIST (B1758 / L514)

**`check_compliance_marker` asserted only `commit_made and not marker`** - that a compliance BLOCK
is present. **It never asked which items were applied.** So a block naming nothing passed on every
turn, and any checklist item without its own mechanism was enforced solely by remembering to
consult it - **which is the failure the checklist exists to prevent**.

**The statement must cite at least two CHECKLIST items by number and carry a per-item status.**
Enforced by `scan_compliance_is_content`.

**And the meta-lesson (L514): a defect phrased as an ANSWER is still a defect.** `S6-B1757c`
recorded this exact finding tagged **ANSWERED**, with no mechanism and no `JUDGMENT-ONLY` -
violating `#236` one turn after `#236` was written. The `#236` gate missed it because its trigger
vocabulary covers MISS markers, not answers. **A gate's trigger vocabulary is narrower than its
class until proven otherwise - and fixing one gate's vocabulary does not fix the others'.**

### #239 - STEM EVERY MARKER LIST, AND SWEEP THEM ALL AT ONCE (B1759 / L515)

**MEASURED: against the real finding text - *"...which is the failure itself"* -
`scan_miss_capture_complete` stayed QUIET.** Zero of nine `MISS_MARKERS` matched while `fail` and
`failure` were both present. The defect went unticketed as a miss.

**Third instance of the class `L509` named.** That lesson said *encode the stem* - and I fixed
`NARRATION_MARKERS` only.

**A marker list is a CLAIM ABOUT HOW A CLASS WILL BE WORDED.** Enumerating remembered phrasings is
guessing; stem the root and the conjugations come free.

**Sweep result (18 lists, 13 unstemmed):** legitimately literal - `SKILL_TRIGGERS` (phrases the
owner types), `OPEN_EVIDENCE` (tool names). **Same defect, ticketed:** `FIX_MARKERS`,
`REMEDIATION_MARKERS`, `RECO_MARKERS`, `OBJECTION_MARKERS`, `RETRO_TRIGGERS`.

**And the meta-rule: a fix applied to the instance in front of you is not applied to the class.**
`L509` stated the class correctly and one member got patched. **Stating a class is not sweeping
it** - which is why `#237` is a gate now and not a paragraph.

### #240 - A GATE'S PROOF USES THE VERBATIM INCIDENT, NEVER SELF-DERIVED PROBES (B1760 / L516)

**EXTENSION (B1805 / L552) - ONE INCIDENT PROVES ONE PATH.**

**MEASURED: `scan_response_gates` passed this sweep every run of the session on one sentence -
*"Reverting."* - while 5 of 12 tense variants went unmatched.** `revert` is the only one of its six
verbs not ending in `e`, so it is the only one for which the naive `stem + "ing"` produced a real
word. **The single verb the incident used was the single verb the expansion handled correctly.**

- **A gate whose markers are GENERATED carries an incident per generation BRANCH**, recorded in
  `EXTRA_INCIDENTS` and asserted by `test_b1805_extra_incident_branches`.
- **At least one recorded branch must be a must-be-QUIET case.** A corpus of only must-fire entries
  cannot detect a gate that fires on everything - and this one also tripped on *"undocumented"*,
  *"hardwired"*, *"wireless"* and *"deleterious"*. **A gate can be too tight and too loose at once,
  and one incident shows neither.**
- **`#240` and `#241` were both satisfied here.** One asks whether the gate fires on its motivating
  words; the other whether it has a seam. **Neither asks whether the incident reaches more than one
  branch.**

**MEASURED: probe strings were built from the marker list of the gate under test.** The test proved
**the list matches itself** and could never detect the case that matters - a real phrasing the list
omits. Five gates passed 4/4 and 5/5 this way and stayed silent on the words that caused them.

**`#226` (prove it can fail) is NECESSARY AND NOT SUFFICIENT.** A synthetic negative satisfies it
while every positive remains self-derived.

**Every gate carries an entry in `scripts/gate_incident_corpus.py`: the VERBATIM text from the turn
where the failure occurred, plus the STATE that turn was in.** Pinned by
`test_b1760_gates_fire_on_real_incidents`. **A gate with no corpus entry is unproven regardless of
how many probes pass.**

**Corollary (B1760, MEASURED):** `scan_uninspected_constant` accepted a `text=` parameter and
ignored it in two separate places. **A seam that is never exercised is indistinguishable from no
seam** - which is why the corpus, not the signature, is the proof.

### #241 - A GATE THAT CANNOT BE ASKED A QUESTION IS NOT PROVEN (B1761 / L517)

**MEASURED across 38 gates: 27 have no injectable text; 14 of those are `scan_` gates.** They read
the live transcript only, so their pin tests can assert nothing but `gate([]) == []` - **which
passes identically for a correct gate, an inverted gate, and a gate wired to nothing.**
`scan_false_skill_status` was defined, proven 5/5, reported live, and had never run.

**Every new `scan_` gate takes an injectable `text=` (and any state it reads) so it can be
exercised on fixed input.** Existing seamless gates are ticketed, not grandfathered.

**And the symmetric error, which is the one that nearly did damage (L517):** a harness that
supplies a gate LESS state than its incident had **manufactures false failures**. The first sweep
reported 4 broken gates; **3 were correct and starved.** Before ticketing a gate as silent,
supply the incident's full text and state - **a harness reporting on itself is the same defect in
the opposite direction.**

**EXTENSION (B1798 / L549) - TWO MORE FACES OF THE SAME ERROR, BOTH IN ONE TURN:**

- **THE EMPTY PROBE.** A probe whose input never loaded printed `VERDICT words present : []` and
  `truncation markers : []`. **Every list empty because `entries` was 0** - which renders
  identically to *"nothing matched, so it is a false positive"*, the conclusion I was already
  leaning toward. **An empty measurement is not a negative result.** Print the INPUT SIZE beside
  every marker list; `entries loaded: 0` is the tell and it costs one line.
- **THE OVER-SUPPLIED STATE.** Testing whether a bare `JUDGMENT-ONLY` satisfies Phase-5 member 5
  returned PASS in BOTH arms, because `_artifact_touched` was live - **the turn was editing the very
  files that satisfy that member.** The route under test was unreachable. **When both arms of a
  probe agree, suspect the probe before believing the result.**
- **The symmetry, stated once:** STARVING a gate manufactures false failures; OVER-SUPPLYING it
  manufactures false passes. **Neither is a measurement of the gate.**

### #242 - EACH NEW NUMBERED RULE NAMES ITS OWN ENFORCER (B1762 / L518)

**MEASURED: `#231`'s gate asks whether a CODE FILE was touched this turn, not whether THIS rule got
a mechanism.** Touching `verify_turn_compliance.py` or `test_unit.py` for any reason silences it. In
B1761 both were touched, so a turn shipping an ungated rule passed the gate built to catch ungated
rules - **any-vs-each at the FILE level: a category was touched, no member verified.**

**The unit of enforcement is the RULE, not the file.** Every CHECKLIST item or SKILL section added
in a turn must name its enforcing function or pin test **in the same clause as its number**, or
carry an explicit `JUDGMENT-ONLY` / `PROSE-ONLY` waiver saying why no mechanism is possible.

**Enforced by `scan_ungated_addition`**, wired into the Stop-hook pre-pass and pinned by its corpus
entry - whose verbatim incident is the line I actually wrote: *"L516 + L517, CHECKLIST #240 + #241,
SKILL section, 8 queue rows."*

**Construction note (B1762b):** the first version matched within a +/-220 character window, so **one
mechanism mention satisfied every number in a short response**. Proximity is not attribution -
**scope the check to the clause.** Found by probing a HALF-gated pair, which a self-derived probe
would never have constructed.

### #243 - EVERY GATE HAS A CORPUS ENTRY OR A DOCUMENTED EXEMPTION (B1762 / L518)

**MEASURED: 17 of 25 `scan_` gates had no corpus entry and nothing failed.**
`test_b1760_gates_fire_on_real_incidents` iterates OVER the corpus, so it validates only what is
already there - **it checks gates IN the corpus, never that a gate IS in it.** Any-vs-each inside
the test written to fix circular proofs, one turn after `require_each` existed to close that class.

**Enforced by `test_b1762_every_scan_gate_has_a_corpus_entry`:** every `scan_` gate carries a
verbatim incident, or appears in an `EXEMPT` dict with a REASON and a ticket. The dict is the
`require_each` shape - **a gate cannot be silently omitted, only explicitly excused**, and the
exemption is visible at review time. Shrinking it is `S6-B1761b` / `S6-B1761c`.

### #244 - A UNIVERSAL RULE NEEDS AN EACH-SHAPED CHECK (B1763 / L519)

**MEASURED: `require_each` existed from B1751 and two fresh any-vs-each defects shipped in the two
turns after it.** Availability is not adoption - **a primitive nobody reaches for is a library, not
a guardrail.**

**If the message a gate EMITS states "each" or "every", the check behind it routes through
`require_each`** - so every member is enumerated and the missing ones are NAMED - or the gate
carries an `EXEMPT` entry with a reason. **Enforced by
`test_b1763_universal_rules_use_require_each`**, which fails on any NEW universally-worded gate that
hand-rolls the check.

**Signal discipline, which is half the item.** The obvious signal - grep gate bodies for
`each`/`every` - flags **13 of 16** and is WRONG: marker lists use `any()` correctly, because a
detector *should* match on any marker. **Gate on the EMITTED MESSAGE, not the body.** That returns 6
candidates carrying three different dispositions: already-each-shaped (convert), count-based
(cannot enumerate), single-member (indirection without coverage). **One grep result is not one
finding.**

**Companion rule (L519): a deferral carries its reason.** `S6-B1762f` was ticketed as *"candidate
for the next enforcement batch"* - no blocker, no cap cited, unreadable later as blocked vs
deprioritised vs forgotten. **And it was the deepest of three items; the two shallow ones shipped
first.** Depth loses to closability at end of turn unless the ordering is forced.

**EXTENSION (B1798 / L549) - A TICKET DESCRIBING A DEFECT DOES NOT STOP THE DEFECT.** `S6-B1774e`
sat OPEN for several batches stating *"12 DETECTION SITES STILL ON RAW `in`"*. It was re-read during
the B1795 end-to-end pass and deliberately held OPEN with a good reason - *"needs the stems-vs-word-
bounds call `#239` describes"*. **Then the exact defect it predicted blocked a turn: `'classified'`
matched inside `'reclassified'`.**

**Deferred-with-a-good-reason and unfixed are the same state from the defect's point of view.** When
a ticket names a live defect class in machinery you are actively relying on, the deferral is not
neutral - **it is a decision to accept the next incident**, and it should be written down as that.

### #245 - NEVER PASS A MESSAGE THROUGH A DOUBLE-QUOTED SHELL ARGUMENT (B1765 / L520)

**THIS RAN.** A commit message written to WARN about destructive commands contained backticked
examples; bash substituted them and **`git reset --hard` executed**. `git reflog` records
`reset: moving to HEAD`; the index was cleared, unstaged tracked files reverted, and the commit
captured 1 file instead of 2.

**Third instance of the CLAUDE.md git-safety hard rule (L49, L77), and the first that was never
typed as a command.** Prose about a destructive command is indistinguishable from the command
inside double quotes.

**Use `git commit -F -` with a QUOTED heredoc (`<<'MSG'`)** - it performs no substitution. Never
`-m "..."` for any message that could contain a backtick or `$(`. **Enforced by
`scan_shell_substitution`**, wired into the Stop-hook pre-pass and pinned by its corpus entry, whose
incident is the verbatim command that ran the reset.

**Detection note:** the tell was `preflight: checking 1 file(s)` in output I had already scrolled
past. **A successful commit hash and a clean `git status` were both consistent with the damage** -
only re-reading the ARTIFACT (`git show --stat`, then the on-disk file) surfaced it.

### #246 - STEM LISTS AND WHOLE-WORD LISTS NEED OPPOSITE MATCHERS (B1767 / L521)

**A cost gate blocked a clean turn because `QUANT_CLAIMS` held `"free"` and the response said
"chosen FREELY per row".** Plain `q in low` substring matching.

**This is `#239`/L515 with the sign flipped.** L515 said *encode the STEM* - so `_MISS_STEMS`
matching inside longer words ("fail" -> "failure") is CORRECT. **The opposite defect is a WHOLE
WORD whose meaning changes inside another word.** One matcher cannot serve both, and applying
either blindly breaks half the lists.

**`STEM_LISTS` is the explicit register**; anything absent is matched WORD-BOUNDED via
`_marker_hits`, because that is the safe default - an over-tight marker misses a hit, an over-loose
one blocks a clean turn.

**Boundaries are necessary and NOT sufficient (the same batch, caught by the negative control):**
word-bounded `"free"` still fired on *"free RAM above the floor"* and would fire on *"free tier"*.
**A marker whose bare form is ambiguous needs its CONTEXT in the marker** (`"is free"`,
`"for free"`), not a tighter matcher. **The half-fix would have shipped as complete.**

**Retroactive sweep: 64 markers across 22 lists match inside longer words - mostly deliberate
stems.** The sweep yields CANDIDATES, not defects (`#244`'s lesson, one batch later), so remaining
conversions are ticketed per-list rather than swept.

**Corollary, and it inverts how `#241` was framed:** `scan_unmeasured_quantity` had no `text=` seam,
so it could only be pinned as `gate([]) == []` - **a seamless gate cannot have its FALSE POSITIVES
reproduced either.** Seams were argued for as protection against gates that MISS. **The gate that
misfires is the one that most needs to be askable.** Corpus entries may therefore carry
`must_fire=False` as REGRESSION entries.

### #247 - CHECK THE RECORD CAN STORE THE DISTINCTION YOU JUST DREW (B1766 / L522)

**When you explain your own behaviour with a distinction, verify the artifact that is supposed to
hold it actually has a field for it.**

**MEASURED:** having told the owner that `S6-B1762f` was ticketed *"with no reason attached"*, I
recorded it as a lapse of discipline. **It is 38 of 38** - no OPEN row in the queue states why it is
open, because there is no field for a reason and no vocabulary separating **blocked /
deprioritised / not-started**. **A confession about discipline was really a missing column, and the
confession is what stopped me looking.**

**ANTI-AUDIT-THEATER (#136) - retroactively catches:**
1. **L519 / `S6-B1762f`** - deferral filed with no reason; diagnosed as carelessness, was schema.
2. **L514 / `S6-B1757c`** - a defect filed as `ANSWERED`; the queue had no way to record *answered
   but not remediated*, so one label absorbed both.
3. **B1766** - 0 of 38 OPEN rows carry a reason; 132 distinct labels across 641 rows.

**MECHANISM: `scan_queue_vocabulary` (attached B1769, the turn the ruling landed).** This item
shipped JUDGMENT-ONLY because the vocabulary was unruled - building a gate against my own unapproved
proposal would have been `#242`'s failure with the authority invented. **Owner ruled 2026-08-19;
the promised mechanism is now attached**, which is the behaviour a `JUDGMENT-ONLY` tag is supposed
to produce rather than a permanent excuse.

### #248 - THE BACKTICK RULE IS ABOUT SHELL ARGUMENTS, NOT COMMIT MESSAGES (B1768 / L523)

**`#245` was written one batch ago and I violated it immediately** - not in a commit message, but in
`python -c "...backticks..."`. Bash performs command substitution in ANY double-quoted argument;
`git commit -m` was merely where it first bit.

**I fixed the instance and named the class wrong.** That is the GENERALIZATION MANDATE failure the
skill already forbids, committed against my own rule, one batch after writing it.

**The rule: never put backticks or `$(` inside ANY double-quoted shell argument** - `-m`, `-c`,
`-F`, `--message`, `echo`, anything. **Write the content with the Write tool and run the file**, or
use a quoted heredoc (`<<'EOF'`). Enforced by `scan_shell_substitution` (widened from
`git commit|tag` to any `python -c` / `-m` / `--message` double-quoted argument).

**Detection note:** this instance was caught by bash itself (`unexpected EOF while looking for
matching backtick`) and nothing ran. **The B1765 instance was NOT caught - it ran `git reset
--hard`.** The difference was pure luck about whether the substituted text happened to parse.

### #249 - THE QUEUE IS UPDATED EVERY TURN, AND AN EMPTY TURN IS DECLARED (B1769 / L524)

**Owner directive 2026-08-19, mechanically gated.** Every turn adds the queue row(s) its work
earned. **Enforced by `scan_queue_not_updated`.**

**The closed vocabulary** is `DONE / DROPPED / BLOCKED / DEFERRED / OPEN / RUNNING`; priority lives
in its own column as `P0/P1/P2`; **every non-terminal class states WHY**, and a placeholder reason
(`TBD`, `N/A`, `REASON-NOT-RECORDED`) is REJECTED - **enforced by `scan_queue_vocabulary`**, which
routes through `require_each` so each offending row is named. A seventh class is a ruling, not a
convenience: **"any text satisfies the slot" is precisely how 132 distinct labels accumulated
across the ledger's 688 rows.**

**THE ESCAPE HATCH IS PART OF THE RULE, not a weakness in it.** A mandatory per-turn gate recreates
the pressure that produced the drift - on a queue-free turn the options become skip, **fabricate a
row (the one thing CLAUDE.md forbids outright)**, or coin a new quasi-class. So the gate accepts:

    NO-QUEUE-CHANGE: <reason>

which makes an empty turn a **recorded decision** instead of a silent gap or an invented row. It is
visible in the response and greppable afterwards, so over-use is measurable - the same posture as
`.stop_exempt`: **a disclosure, not a workaround.**

**Migration note (688 rows, B1769):** 39.4pct of classes were INFERRED from row text and every one
is tagged; **none is claimed as exact**. The council's proposed blanket `DEFERRED` default was
rejected on measurement - 71.7pct of prose rows record COMPLETED work, so it would have
manufactured ~134 fake open items.

### #250 - DECOMPOSE A POOLED CORRELATION WITHIN GROUPS BEFORE THEORISING (B1770 / L525)

**MEASURED:** the `-0.8` IS/OOS rank correlation decomposed to a weighted within-exit `-0.342 /
-0.419` - **about half of it was the exit selector**, exactly as `L502` hypothesised. The other half
is **concentrated in a single exit** (`next_pivot_target`, n=68/83, `rho = -0.73`), while other
exits sit near zero or positive.

**A pooled statistic can be dominated by BETWEEN-group structure that says nothing about the
within-group relationship** (Simpson's paradox). Before explaining a surprising pooled correlation,
**split it by every group label already present in the rows** - here the `exit` column was sitting
in the same records the whole time.

**And the reason this matters beyond statistics: the two readings have different owners.** A
selection artifact is a METHODOLOGY defect fixed by changing how candidates are picked. A single
member inverting is a PROPERTY of that member. Acting on the pooled number alone would have applied
the wrong remedy to half the problem.

**MECHANISM: JUDGMENT-ONLY.** No gate can know which columns are group labels for a given analysis;
this is an analysis habit, not a mechanical check. Recorded as a decision, per `#236`.

### #251 - A SILENT FALLBACK MAKES ONE NAME INTO TWO EXITS; CHECK ITS MIX OVER TIME (B1771 / L526)

**MEASURED: `next_pivot_target` was 100pct silent-fallback for ELEVEN CONSECUTIVE QUARTERS** (5,050
trades) because `signals_at_entry` was not persisted before 2025-02-06, then dropped to ~20-40pct.
**The exit is a different exit either side of that date**, so any IS/OOS comparison spanning it
compares a 3x-ATR fixed target against a pivot exit. **Rank instability is mechanically guaranteed.**

**For every exit or signal consumer with a fallback branch, plot the fallback share BY PERIOD.** A
stable overall rate hides a step function, and a step function inside the sample window invalidates
every cross-period comparison that uses it.

**Ask what ELSE reads the same field.** `exit_regime_flip` also consumes `signals_at_entry` and is
`regime_flip_max_days_20` on **100pct of trades in both periods** - it never flips, and is a
`time_stop_20d` duplicate under another name.

**And check that remediation advice names a real mechanism.** B1748's error text says to select
`fixed_target_3atr`; **no such exit is registered.** A cross-check against it matched an EMPTY SET
and reported a meaningless agreement figure.

**A "0 of N" or "100pct of N" result is a SCHEMA question before it is a finding.**

**MECHANISM: JUDGMENT-ONLY** for the general habit; the concrete instances are ticketed
(`S6-B1771b`, `S6-B1771c`, `S6-B1771d`) and none is fixed without owner approval, since changing an
exit is a rule change.

### #252 - MEASURE DEGRADED EXITS PER CUBE; NEVER MAINTAIN THE LIST BY HAND (B1772 / L527)

**MEASURED on 217,724 trades: 3 of 26 exits fire a reason unrelated to their own name**
(`regime_flip` never flips - 100pct `max_days_20`; `smart_money_reversal` is 98.7pct a trail-safety
fallback; `reverse_signal` is 96.1pct a plain ATR trailing stop), **1 shows a temporal identity
step**, and **10 pairs are outcome-duplicates - `exits_effective ~ 16 of 26`.**

**The runbook's caveat said `regime_flip` was a time stop *pre-B1593*. It still is.** A
hand-maintained list of degraded exits goes stale silently, so run
`scripts/measure_degraded_exits.py <cube>` as part of every post-config pass.

**Consequence: "best of 26" is best of ~16, and the 0.369 selection-noise floor was calibrated for
best-of-26.** A floor measured on a family 38pct larger than the real one is the wrong floor, and it
gates the Phase 1B roster.

**Construction rules this cost (both found by RUNNING the lens, not reading it):**
- **Flag MISMATCH, not consistency.** `time_stop_20d` firing `time_stop_20d` is the exit working; a
  lens flagging 14 of 26 including correct ones is noise.
- **Match on STEMS.** Exact tokens called `atr_trail_1x -> atr_trailing_stop` a mismatch because
  `trail != trailing` - **`#239` again, inside a check written minutes after citing it.**

**Companion (P0, same class): substring containment is not word matching.**
`audit_findings_ticketed.py` corroborated findings with `w in queue`; raising the threshold 1-of-3
to 2-of-3 reduced the defect without removing it. **Third instance this session** after `#246`
(free/freely) and the B1769 placeholder check. Enforced by `test_b1772_word_boundary_matcher`.

### #253 - HARDEN THE EXEMPTION, NOT JUST THE TRIGGER (B1773 / L528)

**EXTENSION (B1799 / L550) - AN EXEMPTION KEYED ON INTENT IS KEYED ON NOTHING.**

**MEASURED: I shadowed `_read_entries` three batches after building the test that forbids it**, and
the tempting fix was to exempt *"deliberate wrappers that alias the original first"* - a real Python
idiom, an accurate description of what I had written, and **an opening any accidental shadow can
walk through by adding one alias line.** The test sees the SHAPE; it can never see the INTENT.

- **An exemption may be keyed only on an OBSERVABLE property**, never on a claim about why the
  author wrote the code.
- **When your own gate blocks your own fix, change the FIX.** Restructuring took one rename.
  Weakening the check is faster and is indistinguishable afterwards from never having had it.
- **If the gate is genuinely wrong, that is a separate finding** with its own evidence and its own
  turn - not a clause appended to the change it is currently blocking.
- **The pressure is local and cumulative:** the wrapper was chosen because restructuring looked
  expensive; the exemption was then attractive because the wrapper was already written. Each step
  reasonable, the destination a gate disarmed by its own author.

**MEASURED: 67 of 268 markers across 33 lists collide with a real longer word** in the project's own
vocabulary. Most are harmless or deliberate (`_MISS_STEMS` matching *missing* is `#239` working).
**17 collide with their own NEGATION**, in two kinds: 5 word-internal (*measured* inside
*unmeasured*) and **12 phrase-level (*executed* inside *never executed*), which word boundaries
cannot fix at all.**

**B1767 hardened the TRIGGER (`_marker_hits`) and left the EXEMPTION on raw `in`. That is the wrong
half.** A loose trigger over-fires and is noticed at once; **a loose exemption lets violations
through silently.** Whenever a gate has an escape clause, the escape needs the STRICTER matcher.

**Use `_affirms()` for any evidence/proof exemption:** the marker must appear as a whole word AND be
un-negated within its own clause. Enforced by `test_b1773_exemptions_are_negation_aware`.

**Construction rules this cost, all found by RUNNING the helper:**
- **Look both ways.** Backward-only missed *"the benchmark was NOT executed"*.
- **Clamp to the clause.** A flat window crossed a sentence boundary and rejected a genuine
  affirmation because the PREVIOUS sentence was negative.

**And the testing rule (L528, twice in one turn):** build probes FROM the live marker list. I
declared this defect *"confirmed live"* from a probe whose trigger never fired, then probed
`PROOF_PHRASES` with two words absent from it. **A test whose input cannot engage the code proves
nothing, and reads exactly like a pass.**

### #254 - INSPECTION EVIDENCE COMES FROM READS, NEVER FROM WRITES (B1774 / L529)

**MEASURED: writing any file exempted a turn from the uncosted-probe gate.** `file_path` is an
`OPEN_EVIDENCE` marker and every `Write`/`Edit` carries one, so **no data need ever have been read.**
A narrower hole preceded it: a `Write` whose CONTENT merely mentioned *grep* also satisfied the
exemption - **`#B1738` fixed mention-vs-use for the RESPONSE side and left the TOOL side untouched.**

**Before matching any evidence marker against tool text, drop mutating calls whole and blank
authored payload fields** (`_tool_invocations`). Verify BOTH directions: a real `Read` must still
exempt, and a `Write` followed by a `Read` must still exempt.

**Companion rule - do not call work manual until you have tested that it is.** `S6-B1773f` claimed
the remaining match sites *"each need a judgment call; a sweep cannot decide"*. **The control flow
decides it**: `if <match>: return []` is an EXEMPTION, `if not <match>: return []` is a DETECTION.
16 sites classified mechanically - 4 and 12. **Asserting that something cannot be automated, without
trying, is the same armchair claim as asserting a mechanism exists without checking.**

**And check a flagged site before converting it.** `scan_unverified_structure` was flagged purely
for not calling `_affirms`; it uses a set intersection on tool NAMES - exact matching, no exposure.
**The absence of a fix is not the presence of a defect.**

### #255 - PRINT THE SAMPLE IDENTIFIER BEFORE JOINING TWO MEASUREMENTS (B1775 / L530)

**MEASURED: I explained `rho = -0.73` with a defect from a different cube.** The persistence gap was
real in `output_batch_A_150`; the rho came from the `b1715`/`b1718` grids, whose fire counts
(302 / 320) identify them as **wave 1** - which carries genuine pivots on both sides of 2025-02-06
and has **no gap at all**. Both measurements were correct. **The join was assumed.**

**Before combining two results, print the identifier of the sample each came from** - a row count, a
fire count, a manifest hash. It took one line here. **A shared subject is not a shared sample:** two
artifacts in one directory, about one strategy and one exit, from different runs.

**And confirm on a SECOND dataset before writing the lesson.** This was caught only because the
post-config sweep ran on wave 1 and reported **no temporal step** across a window straddling the
boundary - contradicting the entry. **A finding and the lesson written from it are the same
evidence, not two.**

### #256 - A TICKET IS A CLAIM ABOUT A PAST MOMENT; RE-DERIVE BEFORE WORKING IT (B1776 / L531)

**EXTENSION (B1827 / L559) - A FIGURE YOU REPEAT IS RE-DERIVED, NOT CARRIED.**

`#256` says re-derive a TICKET's number before working it. **The same applies to a number you keep
telling the owner.** MEASURED: I reported the `#201` gate as *"roughly six false positives"* across
several turns; it is **5 mechanical false positives and 2 SUBSTANTIVE catches**, and the gate has
never been wrong about the concern.

- **Check which way your error points.** *"Six false positives"* supported the conclusion I had
  already stated - **do not patch this again**. The corrected figure supports the opposite. **An
  error that argues for what you already decided is the one you are least likely to re-derive.**
- **No gate covers this.** `#258` is scoped to LEDGER counts (`tickets closed`, `open tickets`);
  a repeated non-ledger figure matches none of its claims. **Gap, not failure** - and detecting an
  arbitrary repeated figure is `JUDGMENT-ONLY`, because tracing a number to the computation that
  produced it is not recoverable from the transcript.
- **Retroactive (`#136`):** *"271 closed in 48h"* (was 13), *"641 rows"* (was 688), *"64
  strategy-optimisation tickets"* (was 66), *"six false positives"* (was 5+2). **Four carried
  figures, four wrong.**

**MEASURED: 6 of the 21 open enforcement tickets described a world that no longer existed**
(`"4 hooks remain"` -> all four built and wired; `"11 gates unwired"` -> 0 of 43; `"vocabulary
unruled"` -> ruled and migrated; `"14 uncorroborated"` -> its matcher replaced underneath it).
**None was wrong when written.**

**60 of 69 open tickets carry a NUMBER**, and in the queue a past-tense measurement reads exactly
like a present fact. **Repeating a stale one in a response is a Truth-Standard violation with a
paper trail that looks like evidence.**

**Before acting on or citing any ticket, re-derive its number.** Enforced by
`scripts/audit_ticket_staleness.py`, which prints today's value for each probeable claim, and pinned
by `test_b1776_ticket_staleness_probes_are_live` - which also holds two conditions the repo must
keep true (**0 gates defined-but-never-referenced**, **0 queue classes outside the ruled
vocabulary**).

**And do not report stale-ticket closures as progress.** Of the six, two closed because the work
landed and four because the QUESTION changed shape - their concerns live on in other rows.
**Closing a stale framing is bookkeeping.**

### #257 - A DERIVED COUNT MUST NAME AND TEST ITS ASSUMPTION (B1777 / L532)

**MEASURED: I reported "271 closed in 48h". The real figure is 13.** The other 268 were WRITTEN as
DONE - records of work finished in the same turn, which never transitioned. I computed
`created - open = closed`, **arithmetic valid only if every ticket starts open. 87pct do not.**

**Before reporting any derived count, state the assumption it rests on and test it.** One query over
first-rows would have caught this.

**And count MEMBERS, not CATEGORIES.** I reported "21 open enforcement tickets"; **6 of those
tickets hold 62 work items** (one alone holds 22). A ticket is itself a category - **the any-vs-each
defect at the ledger level.**

**DONE claims are verified against git, never against their own prose:** run
`scripts/audit_done_claims.py`, which joins ticket -> batch -> commit -> files-changed. Current
state: **66.0pct CODE_BACKED, 25.9pct ANALYSIS_ONLY, 3.4pct UNSUPPORTED, 4.6pct NO_COMMIT**, with
**27 tickets on batches that have no commit at all** and 3 rows verified as claiming code that
shipped in a different batch.

**ANALYSIS_ONLY is legitimate and must stay a separate verdict.** An analysis turn produces a number
and a lesson, not a diff. **Calling every doc-only DONE a false claim would be the same
category-to-claim leap as the 271** - one council advisor did exactly that, reading 87pct born-DONE
as "87pct fabrication".

### #258 - DONE IS SELF-REPORTED; CLOSED IS VERIFIED AGAINST CODE (B1778 / L533)

**OWNER RULING 2026-08-20:** *"Done isn't closure. Closed is only to be marked once you have
verified their work against the actual code and code log and not on documentation which is highly
likely to be incorrect."*

**`DONE` is no longer terminal.** It means *reported finished, unverified*. **`CLOSED` is written
only by `scripts/promote_verified_closed.py`**, which reads verdicts from `audit_done_claims.py`
(ticket -> batch -> commit -> files changed) and never the ticket's own prose. A turn may not write
`CLOSED`.

Applied to 649 rows: **388 CLOSED, 149 DONE, 96 OPEN, 261 not verified closed.** The open count
RISING is the ruling working, not a regression.

**`DROPPED` is never promoted.** The dry run tried to promote 4 dropped rows on code evidence from
their batch - evidence belonging to other rows in the same commit. **That manufactures completion
for abandoned work.**

**AND A LEDGER COUNT IN A RESPONSE MUST HAVE BEEN COMPUTED THAT TURN.** Enforced by
`scan_unverified_count`. *"317 created, 271 already closed"* was 13; `created - open = closed`
assumed every ticket starts open and **87pct are written already-DONE**. **~30 gates scan PROSE for
marker strings and a number carries no marker**, so none could see it.

### #259 - A LITERAL CONTROL CHARACTER CORRUPTS A REGEX SILENTLY (B1778 / L533)

**MEASURED, third occurrence this session:** `\b` written through a bash heredoc becomes a literal
**backspace (0x08)**. `scan_unverified_count` returned `[]` on the exact sentence it was built for,
and - far worse - `scripts/build_phase_1b_roster.py:156` carried `r"_short<BS>\s*="`, so
**`is_dual()`'s check could never match and the B1454 fix in its own docstring was partially inert.**
After repair it detects **60 dual strategies**.

**A gate returning clean over a corrupted pattern is indistinguishable from a gate that works** -
`L501`, arriving through the ENCODING rather than the logic.

**Never write a regex through a bash heredoc; use the Write tool.** Enforced by
`test_b1778_no_control_chars_in_gate_scripts`, which scans every `scripts/*.py` for control bytes
outside comments. **Line 940 of `verify_turn_compliance.py` has carried a comment recording this
same defect since B1721b - recorded, never gated.**

### #260 - SHOW EVERY CLASS OR CITE NO TOTAL (B1779 / L534)

**MEASURED: I reported "388 CLOSED / 149 DONE / 96 OPEN ... 261 of 649".** Three of SEVEN classes
against a total covering all seven. **The owner caught it with addition: 388+149+96 = 633.** And the
figures were themselves wrong - lifted from the migration script's TRANSITION counts, not the
ledger's final state (actual: 390 / 153 / 95, total 662).

**A class breakdown is reported in FULL or without a total.** Enforced by
`scan_partial_distribution`, which sums the listed classes against any cited total and names the
omitted ones.

**`scan_unverified_count` could not catch this** - it asks whether A computation ran, and one had.
**It cannot ask whether the number came from the RIGHT computation.** State which computation a
number came from, not merely that one occurred.

**AND THE VERIFICATION LESSON (L534): symbol-level checking of ticket claims produced ZERO
findings.** 105 apparent misses became 33 after fixing my own index, then 0 on inspection - all
parse artifacts (`tail_n=2`, `roster_core.select_exit`, a command line). **A symbol existing beside
a call site does not prove a claim like "X blocks Y"; only running it does.** A code-claiming ticket
earns CLOSED through its PIN TEST, executed. Rows that cannot be re-verified after the fact stay
DONE - **a visible state, not a gap.**

### #261 - PROVE A RESPONSE-SCANNING GATE ON A REALISTIC RESPONSE (B1780 / L535)

**MEASURED: `scan_partial_distribution` blocked its own author's next turn with a fabricated
finding.** It harvested class counts from every table in a long response, summed them into a figure
no sentence claimed (295), and paired it with `of 1937` - **the Master universe ticker count**. It
even reported `Unlisted class(es): []`, meaning nothing was partial.

**I proved it on five cases, every one a single short sentence.** `#240` demanded the verbatim
incident and I supplied it - **but the incident was one line, and a one-line probe cannot exercise a
WINDOWING bug.** `#240` governs the CONTENT of a probe; this item governs its SHAPE.

**Every response-scanning gate is proven against a multi-paragraph response** containing several
tables and numbers from unrelated subjects. Pinned for this gate by the `long_response` case in
`test_b1779_partial_distribution_gate`.

**Companion rule: a gate that pairs two figures must require PROXIMITY.** A distribution and its
total are stated together; anything else is the gate inventing a relationship.

**And the honest note (L535): in three consecutive turns a wrong count produced a gate, which missed
the next wrong count, which produced a second gate, whose first live act was a wrong count.** When
the machinery starts reproducing the defect it was built to stop, **the next gate is not the
answer.**

### #262 - A RULE LEARNED ON ONE GATE MUST BE CARRIED, NOT RE-LEARNED (B1783 / L536)

**MEASURED: of 15 text-reading gates, 2 had B1742's final-block scoping, 2 had B1738's code-span
stripping, and 13 had NEITHER.** Both rules reached exactly the gate they were learned on. That is
how B1781 came to fire on a LEARNINGS entry which merely RECORDED a defect.

**`_response_text()` now carries both**, plus fenced-block and blockquote stripping - because
**documenting a failure must not trip the gate for that failure, or the lesson can never be written
down.** Every response-scanning gate uses it.

**Enforced by `test_b1783_response_gates_inherit_text_scoping`**, which pins the known-unconverted
set so it cannot GROW: a NEW gate reading assistant text must call the helper. Shrinking the set is
`S6-B1783b`.

**The generalised rule, and this session recorded it at FIVE scales:** one marker list stemmed while
twelve kept the defect (`L515`); one trigger hardened while its exemption stayed loose (`L528`); one
instance patched while its class stayed open (`L519`); one gate's scoping lesson not reaching the
gate built three turns later (`L536`); and the ledger counting categories rather than members
(`L532`). **When a rule is learned, ask what will CARRY it to the next instance - a shared helper, a
primitive, or a test that pins the set. Prose in LEARNINGS carries nothing.**

### #263 - THE LEDGER HAS SIX MUTUALLY EXCLUSIVE CLASSES (B1784 / L537)

**OWNER RULING 2026-08-20:** *"Lets use those 6 classes itself. Replace DONE with EXECUTED. Done
will be moved to EXECUTED after verifying each ticket comprehensively. All CLOSED tickets will be
under EXECUTED. I want mutually exclusive groups."*

```
EXECUTED   verified against code and the change log     terminal
DROPPED    deliberately not doing                       terminal
BLOCKED    cannot proceed
DEFERRED   could proceed, chose not to
OPEN       queued, unstarted, or UNVERIFIED
RUNNING    in flight
```

**There is no "finished but unverified" state.** A row is EXECUTED or it is still work. A turn may
never write EXECUTED - only a verification pass may promote into it.

**WHY THIS ITEM EXISTS: I reported SEVEN classes by unioning two rulings.** B1769 ruled six with
DONE terminal; B1778 added CLOSED and **retired nothing**, so two overlapping terminal-ish states
coexisted and I reported their union as a taxonomy. **A classification is a PARTITION, not a list of
labels in use.**

**When a ruling ADDS a class, name what it RETIRES.** An addition that retires nothing makes the
partition quietly coarser, and the overlap survived two turns of counts being reported off it.

**Enforced by `scan_queue_vocabulary`** against the six, and by
`test_b1776_ticket_staleness_probes_are_live` which fails on any class outside them.

### #264 - A BUILD CLAIM MUST NAME THE ARTIFACT IT BUILT (B1787 / L538)

**MEASURED: of 134 tickets from the last 48h claiming to BUILD something, 54 name a gate, test or
script that verifiably exists, 0 are genuinely missing, and 79 (59pct) name NOTHING CHECKABLE.**

**The limit is not the verification, it is that most build claims are unfalsifiable as written.** A
row saying *"the gate is now wired"* cannot be checked; *"`scan_x` wired, pinned by `test_bN_y`"*
can be, in one command.

**Every ticket claiming to build, wire, add or fix code names the artifact** - a `scan_`/`check_`
function, a `test_bNNN_` name, or a file path. Verified by
`scratchpad/verify_build_claims.py`-style joins against the live codebase, never against the batch
commit (`#257`: a batch carries several rows, so its diff is the wrong entity).

**HARNESS DISCIPLINE, which cost three false findings here.** `0 LANDED` was the tell each time:
- stripping `_` as markdown emphasis destroyed every snake_case identifier (17 false MISSING)
- globbing `scripts/*.py` only made `backtest/` artifacts read as absent (4 false MISSING)
- exact test-name matching missed prefix references (1 false MISSING)

**A suspiciously clean result is a bug in the harness until proven otherwise.** Fourth time this
session a large finding collapsed on inspection.

**AND: adjacency asserts a relationship.** Reporting *"92 awaiting verification"* beside *"96 work
items"* implied they were comparable; they are different sets, neither containing the other.
**Numbers placed together are read as related even when no sentence says so.**

### #265 - PROMOTION NEEDS A BATCH-SPECIFIC CODE ARTIFACT (B1788 / L539)

**A row earns EXECUTED only on evidence tied to the batch that claimed it:**
- a `scan_`/`check_` gate that is DEFINED and WIRED, or
- a `test_bNNN` present in a test file (prefix match).

**These do NOT count:**
- **LEARNINGS or CHECKLIST references** - they are the prose the owner's ruling excludes. My first
  pass promoted **85 rows** on exactly this before it was caught.
- **A file mention.** `technical.py` predates most rows naming it by months; *"the file exists"*
  proves the file exists. **Absence is still a strong negative; presence is not evidence.**

**MEASURED across 168 rows awaiting verification: 20 promoted, 148 stay OPEN, and 145 of those name
no wired gate and no `test_bNNN` at all** - nothing to verify against. Same shape as `#264`'s 59pct,
on a different population.

**The burden of proof sits on PROMOTION.** Owner: *"if anything to be done even potentially, keep
them open."* A row stays OPEN by default and must earn EXECUTED - the opposite of the 600 rows where
DONE was written at the moment of intent and never revisited.

**Run `scripts/verify_awaiting_rows.py`**; every promoted row carries its evidence and every flagged
row carries what is missing, so neither verdict is a bare assertion.

### #266 - AN ANALYSIS ROW HAS NO CODE TO VERIFY (B1790 / L540)

**MEASURED: of 148 rows that named no artifact, 138 belong to batches whose commit touched NO CODE
AT ALL.** Spot-checked by hand: `B1512: engine timing COMPLETE (42.9 min)` changed `CLAUDE.md`,
`EXECUTION_QUEUE.md` and `LEARNINGS.md` and nothing else. **A measurement turn's output is a number
and a lesson.**

**`#258`'s ruling - EXECUTED means verified against code, never documentation - is correct for build
rows and UNSATISFIABLE BY CONSTRUCTION for analysis rows.** 138 rows are permanently ineligible for
the only terminal state that fits them. **This is a category error in the ledger, not a backlog.**

**AWAITING OWNER RULING (`S6-B1790c`).** The options are `DROPPED` (implies abandonment - the work
happened), `OPEN` forever (makes OPEN useless as a queue), or `EXECUTED` on the analysis artifact
(reverses the ruling). **Do not pick one silently** - the six classes exist because states were
being invented, and choosing here without a ruling repeats that.

**AND NAME A VERDICT TO ITS EVIDENCE.** `CODE_LANDED_IN_BATCH` is deliberately not `VERIFIED`: a
batch carries several rows, so it proves the BATCH produced durable code, not that THIS row's claim
is that code. **B1777's error was asking about the batch and reporting it as an answer about the
row.** Verify via `scripts/verify_open_via_diff.py`.

### #267 - STOP AT THE SECOND FAILED HAND-CHECK (B1791 / L541)

**MEASURED: four classifiers, hand-checked samples failing 3-of-4 then 3-of-5.** Fable's rule -
*two failed attempts at the same fix means the diagnosis is wrong* - applied two attempts before I
stopped. **Each patch made the classifier narrower without making it right.**

**The wrong assumption was that "nothing pending" is detectable by keyword.** The distinction is
grammatical MOOD, not vocabulary: *"I measured X"* and *"measure X"* share every content word.

**When a classifier fails a second hand-check, stop and present the options** - hand-verify in
batches, accept the population as permanently OPEN, or have the owner accept a sampled error rate.
**A fifth regex is not an option, it is momentum.**

**COMPANION: A VERIFIER MUST NOT READ ITS PREDECESSOR'S ANNOTATIONS.** Every pass since B1769
PREPENDED text to these rows, so a row now leads with ~430 characters of prior verdicts before its
own content. **The first classifier scored that** - grading its own homework, and worsening with
each pass. Strip prior annotations before classifying (`original_text()` in
`scripts/verify_analysis_rows_complete.py`).

**AND THE PART THAT HELD: nothing was written.** Four wrong classifiers, zero corrupted rows,
because every pass was a DRY RUN followed by a hand-check before `--write`.

### #268 - A CLASSIFIER INHERITS ITS AUTHOR'S MODEL OF THE DATA (B1792 / L542)

**MEASURED: hand-reading 20 rows gave 2 complete, 17 open work, 1 misclassified - a 10pct
completion rate.** Four classifiers had promoted between 17 and 57 of the same population.

**They failed because they were built on the wrong premise.** `#266` framed these rows as *analysis
whose artifact was documentation*, so every classifier hunted for a recorded result. **The rows are
actually TASKS WITH VERBS** - *"Run first"*, *"needs resimulation"*, *"Build the harvester"*,
*"Owner approval required"* - work written down and never started. **Any result-like text a
classifier found was incidental**: `20/24/26` scored as a measurement inside *"if results look
anomalous, run a diff"*.

**Before building a classifier, hand-read a sample and state what the population IS.** A wrong model
of the data cannot be patched by refining the pattern - four attempts proved that (`#267`).

**A COMPLETED ANALYSIS ROW HAS A RECOGNISABLE SHAPE:** a finding plus its consequence, and no verb
pointing forward. *"Cliff SHARP; band NOT extended; sweep stays 20 engine runs."* **A definitive
NEGATIVE is a completed result** - it closes the question.

**AND HAND-READING FINDS WHAT NO CHECKER LOOKS FOR.** `S6-B1532c` states its own blocker and sat as
OPEN for months; the completeness checkers never asked whether the CLASS was right.

### #269 - SCORE A CLASSIFIER ON THE MINORITY CLASS, NOT ON ACCURACY (B1793 / L543)

**MEASURED: the completeness classifier scores 17/20 = 85pct overall and 0/3 = 0pct on the classes
that matter.** 17 of 20 rows are OPEN and it defaults to OPEN, so **a constant function scores
85pct on this sample.** All the accuracy is the majority class.

**Report recall on the class that changes an outcome.** An overall accuracy on an imbalanced sample
is not a weak signal, it is a misleading one - and **85pct was the first number printed**, the one I
would have reported. What exposed it was the SHAPE of the disagreements: three errors, all of them
non-OPEN.

**Keep the hand-read verdicts as labelled ground truth** (`scripts/hand_verified_rows.py`), each with
the phrase that decided it. **A classifier is unproven until it reproduces verdicts a human reached
by reading** - the corpus pattern of `#240`, moved from gates to classifiers. Enforced by
`test_b1793_classifier_scored_against_hand_labels`.

**And RECORD a metric you cannot meet; do not enforce it.** The test asserts a range on recall
rather than a floor, because demanding a floor the classifier cannot reach invites loosening the
labels to pass - the exact failure the corpus exists to prevent.

### #270 - NO HALF MEASURES: READ THE WHOLE ARTIFACT BEFORE JUDGING IT (B1794 / L544)

**EXTENSION (B1807 / L554) - TRUNCATION COUNTS ONLY WHERE IT IS APPLIED TO THE SOURCE.**

**MEASURED: three display trims on a compliant turn were read as a partial read** -
`pytest -q | tail -3`, `grep foo file | head -6`, `sed -n '/def x/,/^def /p' f | tail -22`.
**Everything after a `|` has already seen the whole input.**

- **Count truncation only in the PRE-PIPE segment.** `sed -n 'N,Mp' file` is the file-sampling
  idiom and is what the original incident used; a PATTERN range reads a whole region and is not
  sampling.
- **Third false positive from this gate.** Fix it rather than live with it: I had started reading
  its output as noise and reaching for the *"end to end"* escape to clear it. **That escape is an
  assertion - using it to silence a false positive makes it a lie the next time it matters.**
- **The gate was never wrong about its own shape.** The false positives came from the marker being
  a PROXY for the concept - `head -` standing in for *"you sampled"* - and the proxy admitted cases
  the concept excludes. `#239`'s family: the marker is not the thing.

**OWNER DIRECTIVE 2026-08-20:** *"You are supposed to analyze anything - not just tickets, but
documents or even code - end to end. No half measures."*

**MEASURED: I read 20 of 141 rows and projected the rate. Sample 10pct complete; population 72pct -
wrong SEVEN-FOLD.** The population is SORTED: `B1503-B1541` are planning rows, `B1576-B1782` are
measurement records. **A contiguous slice of a sorted list is not a sample.**

**Before stating a verdict over a set, read every member of it.** Enforced by `scan_partial_read`,
which fires when a turn states a population verdict while its tool calls show truncation
(`head -N`, `[:300]`, `--show`, *"batch 1 of"*). Say *"end to end"* or *"in full"* only when it is
true - the gate takes that as the assertion it is.

**THE CONTAMINATION IS NOT LOCAL.** `hand_verified_rows.py`, the labelled ground truth built from
those 20 rows and used to score four classifiers, is 20 planning rows presented as representative of
141. **Right about each row, wrong about the population.**

**AND CAREFUL WORK ON A SUBSET READS EXACTLY LIKE CAREFUL WORK.** Each of the 20 verdicts was
correct; 20 sounds like a respectable sample. **The error was never in a row - it was in
generalising from a slice**, which no amount of care inside the slice can detect.

### #271 - COUNT TICKETS, NOT ROWS (B1795 / L545)

**AMENDED B2525 (L737): the rule is right and its GATE sees one surface only.**
`scan_row_vs_ticket` reads response prose about the EXECUTION_QUEUE ledger. MEASURED: the same
defect landed on a different append log - `output_audit/postconfig_landings.jsonl` - read by a
different module, and nothing was watching. I printed *"undelivered now: 6"* from a raw
comprehension over rows carrying `reported_to_owner=false`; the record is append-only and
`postconfig_landing.undelivered()` takes the LAST event per cube, so the answer is **0** - six
historical false rows superseded by later true rows for two cubes.

**So #271 extends to EVERY append log, not just the ledger: one authoritative reader per log, and
every consumer calls it.** If you are writing a comprehension over an append log's rows, you are
asking the file a question only its reducer can answer. Known readers: `scripts/queue_state.py`
(the queue, per distinct ticket, last row wins) and `postconfig_landing.undelivered_events()`
(landings, last event per cube).

Mechanism: `test_b2524_landings_record_has_one_authoritative_reader` asserts no module outside the
reducer counts the flag - MEASURED 0 hits across 373 of 374 `scripts/*.py` (the reducer's own
module excluded), pattern validated against a planted instance (#166). The PROSE form - a bare
cardinal in a summary sentence - stays JUDGMENT-ONLY: no scan reads a number's intended
population.

**MEASURED: `EXECUTION_QUEUE.md` holds 823 rows for 721 distinct tickets.** Closing a ticket APPENDS
a row rather than editing the old one, so **81 ids carry 2+ rows and 74 are in contradictory states -
57 are EXECUTED AND OPEN at once.**

**Every queue count quoted this session was row-level while being called ticket-level.** A row count
is wrong by an unbounded amount and reads exactly like a right one.

**Count only via `scripts/queue_state.py`** - one reader, last row wins, per distinct id. Enforced by
`scan_row_vs_ticket`, which fires on a queue-class count whose method names no dedup.

**The invariant is asserted, not assumed:** last-row-wins is sound only while no terminal row is
followed by a non-terminal one for the same id. `test_b1795_queue_counts_are_per_ticket` checks that
every run (currently 0 violations). **If it ever fails, every count derived from the ledger is
wrong**, not just the new one.

**AND EXCLUSIVE LABELS ARE NOT EXCLUSIVE ASSIGNMENT.** The six classes were made mutually exclusive
as vocabulary while 69 tickets sat in two of them. **Fixing the names did nothing to the data, and
was reported as though it had.**

### #272 - A CLASSIFIER OVER A POPULATION HAS NO DEFAULT BRANCH (B1795 / L546)

**JUDGMENT-ONLY: no mechanism.** Detecting a semantically-wrong `else` requires knowing which
members the author actually examined, which is not in the source. Recorded as judgment rather than
left to look gated - per `#236`.

**MEASURED: an `else` promoted 140 tickets when 36 had been classified.** 104 tickets nobody had
read were marked EXECUTED by the script enforcing `#270`, the rule against judging a set you have
not read.

**Every member is named in exactly one list, and the script asserts `named == population` and
REFUSES TO WRITE on mismatch.** v2 printed `110 == 110` before touching a byte. **A default branch
is a silent verdict on everything you forgot to think about.**

**Applies past ticket scripts** - any sweep that assigns a disposition, label, or status across a set:
migrations, classifiers, bulk edits, roster builders.

### #239 AMENDMENT - MATCH THE SHAPE, NOT THE DIALECT (B1796 / L548)

**`#239` says stem the root so conjugations come free. That covers `verify`/`verified`/`verifying`.
It does NOT cover the same claim written in another domain's words.**

**MEASURED: `scan_partial_read` fired on 2 of 10 realistic verdict sentences - 0 of 8 for code and
documents.** *"All 138 rows are complete"*, *"there are no other call sites"* and *"no document
outside archive/ still references it"* are ONE claim in three vocabularies. **Stemming cannot bridge
them - the words share no root.**

**Three rungs, and enumeration is the bottom one:**

| rung | covers |
|---|---|
| enumerate phrasings | only what you remembered |
| stem the root (`#239`) | conjugations |
| match the SHAPE (B1796) | dialects - the same claim in another domain's words |

**Before adding a word to a matcher, ask which rung it is on.** If two domains express the same
claim with disjoint vocabulary, the matcher is on the wrong rung and adding words will not fix it.
Matching the grammatical shape - a universal quantifier with a state verb, or a negative existential
- covered all three domains at once: **11 of 11 fire, 0 of 7 false positives.**

**Amended into `#239` rather than minted as `#274`:** this is the next rung of `#239`'s own ladder,
not a new class. Precedent - B1599 anchored L466 by amending `#191`.

### #273 - NAMING AN ENFORCER IS NOT BEING ENFORCED (B1796 / L547)

**`#242` requires an added rule to NAME its mechanism. Nothing checked the mechanism COVERS the
rule's declared scope.**

**MEASURED: `#270` declares *"tickets, documents, or CODE"*; its gate fired on 2 of 10 realistic
verdict sentences - both tickets, ZERO of eight for code and documents.** The bullet claiming
enforcement shipped in the same turn as the gate that did not deliver it.

**When a rule declares N domains, its pin test carries a case PER DOMAIN** - so the coverage claim
is true by test, not by assertion. For `#270` that is
`test_b1796_partial_read_covers_every_declared_domain` (11 fire-cases across 3 domains, 5
quiet-cases).

**MECHANISED FOR THIS INSTANCE; JUDGMENT-ONLY IN GENERAL** (per `#236`): extracting the declared
domains from arbitrary rule prose and proving reachability is not something a scan can do. The
durable part is the habit - **"Enforced by X" is a factual claim about X, subject to the Truth
Standard like any number.**

**Any-vs-each, one level up.** `#234` asks whether every MEMBER of a rule was handled; this asks
whether every DOMAIN of a rule is reachable by its enforcer.

### #274 - EVERY TURN REPORTS THE TICKET COUNTS BY GROUP (B1803, owner directive 2026-08-21)

**Owner:** *"Always provide a count of tickets by groups at the end of the turn. similar to skills
invoked."*

**Same standing as the SKILLS INVOKED block - every turn, no exceptions**, including analysis-only
and question-answering turns. The queue is the anchor (`#94`), and its state was invisible between
turns unless the owner asked.

- **All SIX classes, each with a number:** EXECUTED / DROPPED / BLOCKED / DEFERRED / OPEN / RUNNING.
  **A class named without a count reports nothing; a class omitted lets silence stand in for zero.**
- **Derive it with `python scripts/queue_state.py`** - per DISTINCT TICKET, last row wins. The ledger
  is an APPEND LOG (853 rows for 751 tickets at B1803), so **a row-level count is wrong by an
  unbounded amount and reads exactly like a right one** (`#271`).
- **Show the delta when tickets changed state**, so the block reports movement and not only a level.
- Enforced by `scan_ticket_counts_missing`, which reports WHICH classes are missing via
  `require_each` (`#234`) rather than a bare pass/fail.

### #275 - A RESPONSE GATE MUST NOT ASSUME HOW THE RESPONSE IS FORMATTED (B1806 / L553)

**Two gates blocked a turn that had complied with both. Both defects were in the gates.**

**POSITION.** B1732 moved a block-locating gate from the FIRST occurrence of its header to the LAST,
because an earlier mention shifted the window off the real block - and inherited the mirror bug. A
later prose mention then opened the window PAST a complete block: **all three members listed, all
three reported missing.**

- **The block is wherever the MEMBERS are.** Use `_best_block_window`: try every occurrence, keep
  the window satisfying the most. **A positional heuristic encodes a habit of formatting and
  silently inverts the moment the formatting changes.**

**FENCING.** `_response_text` strips fenced blocks so documenting a defect cannot trip the gate for
that defect (B1781). **A gate demanding a TABLE OF NUMBERS must pass `keep_code=True`** - a table
belongs in a fence, and `scan_ticket_counts_missing` reported 5 of 6 classes missing while all six
were on screen.

- **`keep_code` must skip the INLINE strip too**, because a fence is backticks. The first version
  guarded only the fenced-block regex and changed nothing - **an inert fix that re-running caught
  and reasoning would not have.**
- Mention-vs-use stays the DEFAULT; `keep_code` is opt-in, and safe only where a mention cannot
  satisfy the gate - here it cannot, because a mention of the class names carries no numbers.

### #276 - A GATE'S OWN DIAGNOSTIC IS NOT EVIDENCE ABOUT THE TURN (B1811 / L555)

**EXTENSION (B1812 / L556) - CHECK THE SHAPE OF THE TEXT BEFORE REGEXING IT.**

**MEASURED: the B1811 strip turned 183 chars of tool text into 84.** Tool text is ONE line -
`json.dumps(input)` joined by spaces - so an unanchored `\[\d+/\d+\][^\n]*` consumed the whole
corpus after the first `[1/1]` inside any quoted string. **The strip written to stop a gate reading
its own message made every tool-text gate blind instead** - strictly worse, because the false
positive it fixed was visible and the blindness was not.

- **A gate report is LINE-ANCHORED; an echo inside a JSON string is not.** Strip lines that START
  with the header or a `[N/M]` marker; touch nothing else.
- **Assert the lossless case.** `test_b1812` requires `_strip_gate_echo(tool) == tool` for tool text
  carrying an embedded quote. A strip is defined as much by what it must NOT remove.
- **A regex applied to text whose shape you have not checked is a claim about that shape.** This one
  claimed newlines that never existed.

**MEASURED: the only occurrence of `rng.` in the transcript was `scan_synthetic_provenance`'s own
violation message**, which quotes `rng.normal(1,3,30)` to explain itself. The Stop hook feeds the
report back, the next turn's tool calls echo it, and **firing once seeds the evidence for firing
again** - on a turn whose every quoted decimal was a real measurement.

- **Strip prior turn-gate reports from BOTH readers** before scanning (`_strip_gate_echo`, applied
  in `_tool_text` and `_response_text`). A previous report describes the machinery, never the turn.
- **Third instance of the shape:** B1732 (self-description shifted the gate's own window), B1738
  (a response listing trigger words fired the gate), B1811. **B1738's fix guarded the RESPONSE and
  this echo arrived through TOOL text** - a rule learned on one reader did not travel to the other
  (L536), so it belongs in the shared helper.
- **Writing a vivid diagnostic has a cost.** Quoting the trigger vocabulary makes the message clear
  and makes the gate self-triggering. Keep the vividness; strip the echo.

### #276b - AN INJECTION SEAM MUST TRAVEL THE SAME PIPELINE AS THE LIVE PATH (B1811 / L555)

**`#241` says a gate that cannot be asked is not proven. This is the corollary: a seam that answers
a DIFFERENT QUESTION than the live path proves nothing about it - and looks exactly like a passing
test.**

**MEASURED: ten call sites wrote `_tool_text(entries) if tool_text is None else tool_text`**, so an
injected value skipped every scrub the live path applies. The first probe of the B1811 fix therefore
exercised a path production never takes and reported clean for that reason.

- **The override belongs INSIDE the helper**, not at the call site: `_tool_text(entries, tool_text)`
  scrubs either way, exactly as `_response_text(entries, text)` already did.
- **A test asserts the bypass cannot return** - `test_b1811_gate_echo_is_not_evidence` greps for the
  old expression.

### #277 - AN ARTIFACT MUST CARRY THE KEY IT WAS RANKED, SELECTED OR FILTERED ON (B1820 / L558)

**MEASURED: `step1_ranking` emitted `sharpe` - the HOLDOUT measurement - as its first field and
omitted `is_sharpe`, the key it actually ranks on.** So the artifact showed exactly what the defect
B1718 fixed would have produced. **The separation was real and unverifiable from its own output.**

**It was load-bearing:** the plan sets `m = 41` on that separation being airtight and states a leak
forces `m = 820`, *"roughly 20x tighter and almost certainly admit nothing"*.

- **Emit the ordering key, first, beside the value it is not.** Keeping the holdout Sharpe as a
  MEASUREMENT is right; presenting it where the ranking key belongs is not.
- **Enforced by `test_b1820_step1_ranking_emits_its_ranking_key`:** the emitter carries the key, the
  sort still uses it, and on a real artifact the rows are ordered by it.
- **The general test: could a reader tell this artifact from one produced by the bug?** If not, the
  artifact is not evidence regardless of whether the code is correct.
- **Retroactive (`#136`):** `S6-B1770e` (regrade artifacts carry neither `is_sharpe` nor `sharpe`,
  so they graded nothing); `S6-B1580c` (no `swing_length`/`config` column, so a cube cannot be
  attributed to the run that made it); `S6-B1705j` (a PASS column on a step that has no gates).
  **Three prior instances, same shape: the output cannot answer the question asked of it.**

### #278 - AN ASSERTED CONSEQUENCE IS A CLAIM. COMPUTE IT. (B1833 / L560)

**MEASURED: both retractions in one turn were consequences I asserted without computing.**
*"Re-running wave 1 would not fix it"* needed a `git log`; *"the lever costs ~2x runtime"* needed
`100 x 2 = 200 x 1`. **Each took under a minute once attempted, and neither was attempted** - a
consequence feels like reasoning rather than a claim.

- **A consequence carries the same evidence burden as a measurement.** *"X follows from Y"* is a
  claim about X, and the fact that Y is verified does not verify it.
- **Check which way it points.** Both errors favoured the position I already held - *don't spend the
  5.8 h*, *the lever is expensive*. `#256`-ext covers a figure you REPEAT; **this covers one you
  assert for the FIRST time**, which no rule reached.
- **No gate claims this ground.** `#201`'s `QUANT_CLAIMS` are cost-is-FREE phrasings, `#258` is
  ledger counts. **Gap, not failure** - and detection is `JUDGMENT-ONLY`, since recognising "this
  sentence asserts a consequence" is semantic.
- **Retroactive (`#136`):** the re-run advice (B1814), the ~2x runtime (B1817), the plan's
  *"enforced mechanically ... a file path"* that never existed (`S6-B1705c`), and B1775's residual
  attributed to a persistence gap on an assumed join. **Four asserted consequences, four wrong.**



### #279 - AN EXCLUSION REGISTER NEEDS A CHECK IN BOTH DIRECTIONS (B1916 / L587)

Any list of things deliberately left out - **disabled, exempt, deferred,
waived, quarantined** - is a claim about the world at the moment it was
written. **The world moves; the list does not.**

**L619 extension (B2071): "decision-gated" / "needs owner approval" is itself
an exemption reason and carries this item's burden.** Before presenting an
item as blocked on the owner, verify it against the approval-requiring
classes (rule/threshold/parameter changes, paid runs, launches, strategy
changes) - an offline analysis on cached artifacts belongs to none of them.
B2067 halted a whole goal partly on such a mislabel; the one-sentence re-read
disproved it. Detection is JUDGMENT-ONLY (no scan classifies gatedness);
durability is this citation plus the L619 entry.

**Both assertions are required:**

1. **Nothing uncovered** - every member of the population is either handled or
   explicitly excused with a reason. (`require_each`; this half usually exists.)
2. **Nothing excused that no longer needs it** - no entry names something that
   is now handled. **This half is usually missing**, because a stale exemption
   never fails anything: the work runs, the tests pass, and the register
   quietly claims a gap that already closed. **The recorded state drifts
   PESSIMISTIC while everything stays green.**

**Mechanically enforced** for the gate corpus by the redundancy assertion in
`test_b1762_every_scan_gate_has_a_corpus_entry`.

- **Retroactive (`#136`):** **B1916** - three `EXEMPT` entries excused as
  *"incident text not preserved"* while all three carried cases in
  `EXTRA_INCIDENTS`, found the first time the reverse check ran. **B1035** -
  `B975`/`B984` strategy disablements REVERSED after runtime probes confirmed
  both producers exist and emit non-zero values. **B1494** - six de-dup
  disables reverted. **Three registers, three instances, one decay.**
- **Also watch the excuse itself, not just its age.** Two entries said *"no
  seam"* about **pure functions** - the corpus could not EXPRESS a positional
  signature, and that limit was recorded as a property of the gates. **An
  exemption's reason can be wrong on the day it is written.**

**AMENDED B1935 (L591) - THE REASON IS A TESTABLE CLAIM, SO TEST IT.** Decay is
the mild case. Measured over one session this register went **15 -> 6 and NOT
ONE removal was because the work got done**: 3 entries stale, 3 excused as *"no
seam"* while drivable, 2 excused as *"undocumented trigger"* while importable,
2 excused as unseamed **while a PASSING TEST in the same repo drove them**.

- **The disproof of four of the five reasons was already committed** at the
  moment each reason was written. That is not decay; it is an unverified claim.
- **`require_each` proves an entry HAS a reason. It cannot prove the reason is
  true**, and the two look identical in review.
- **Before writing "cannot be tested / no seam / not available", CALL IT.**
  `#222`'s rule, applied to an exclusion instead of a threshold.


### #280 - A COUNT IS NOT A SET: NAME THE MEMBERS OR THE QUERY (B1965 / L601)

A row recording **how many** without recording **which** cannot be completed -
only re-measured. And `#271`/L600 says the re-measurement is a different set
under the same name, with no original list to check against.

**Every row stating a count of rows / tickets / gates / batches must carry
either a member id or the query that selects them.** `46 of 60 OPEN tickets,
per queue_state` is complete; `3 ROWS: their batch changed code` is not.

- **An anonymous count is not WRONG, it is UNUSABLE.** 3 rows really did change
  code without adding a definition. No amount of re-checking recovers which 3.
- **Distinguish from a stale count** (`#256`): stale is wrong and re-deriving
  fixes it; anonymous is right and re-deriving replaces it.
- **Mechanically enforced** by `scan_count_without_members`, which reads rows
  ADDED this turn.
- **Retroactive (`#136`):** MEASURED over 62 OPEN rows - **13 state a count, 7
  name no member**: `S6-B1589c` (7 gates), `S6-B1636a` (195 gates), `S6-B1788d`
  (145 rows), `S6-B1788e` (3 rows), `S6-B1790d` (3 rows), `S6-B1794d` (38
  rows), `S6-B1901a` (3 rows). **Prevention is one gate; the retro-fit is seven
  fresh classifications.**


### #281 - A GENERATED ARTIFACT OLDER THAN ITS GENERATOR IS A MEMORY (B1974 / L607)

A committed artifact produced by a script is STALE the moment any of its
generators changes - no judgement about whether the change "should" have
mattered. `PHASE_1B_ROSTER.md` sat 7 generator-commits stale with a wrong
gate-2 count, and nothing noticed **because its headline was unchanged**: a
stale artifact keeps the SHAPE of a measurement while being a memory.

- Before citing any generated artifact, compare its last commit against its
  generators' - or check its freshness stamp.
- When editing a generator, run the control BEFORE the edit: a single
  post-change regeneration cannot separate your diff from drift already there.
- An output-preserving generator change leaves the artifact byte-identical
  and never re-committed; a freshness STAMP (sha256 of the generator sources
  the run executed) is the exit that is not a no-op commit.

**Enforced by** `test_b1974_generated_artifact_is_not_older_than_its_generator`
(register `_B1974_GENERATED`; grow it as artifacts gain generators).
**Batch re-exam lineage (B1446 rule 5):** the one genuinely new class in the
L602-L613 batch; the other ten are covered by the items their entries cite.

### #282 - THE PER-TURN REPORTING CONTRACT IS OWNER-SPECIFIED, TABULAR, AND GATED (B2039 / L618)

Owner directives 2026-08-21 + 2026-08-23, combined: every turn's close reports

1. **Ticket counts as a TABLE** - all six ledger classes, each with a number, a
   per-class DELTA since the previous report, and the turn's ticket OUTCOMES
   (which ids moved, to what state) - derived from `scripts/queue_state.py`
   (per distinct ticket, last row wins), never a row count and never prose.
2. **Skills status naming FULLY INVOKED vs not** - all three project skills,
   each with an explicit status (FULLY LOADED / TRIGGERED-NOT-INVOKED /
   NOT-TRIGGERED); silence cannot distinguish "not triggered" from "skipped".
3. **CHECKLIST compliance with per-item status** - at least two items cited by
   number, each with its own state, per #238.

A format directive from the owner is a SPEC for every future response, not a
suggestion for the next one - encode it as a gate the same turn (the B2039
lesson: the six-numbers rule was gated while the tabular half lived only in
the directive's wording, and prose counts passed for two days).

*Enforced by:* the `tabular with a delta column` member of
`scan_ticket_counts_missing` (verify_turn_compliance.py, require_each) plus
the existing `scan_missing_skill_confirmation` and `scan_compliance_is_content`.

### #283 - A NAME-KEYED TERMINAL ARTIFACT ON DISK AT LAUNCH IS THE PRIOR ATTEMPT'S (B2193 / L649)

Before launching (or waiting on) any run whose status artifact is keyed by a reused name
(wave summary, completion sentinel, verdict file): an existing terminal artifact under that
name was written by a PRIOR attempt and will shadow the live run for every reader polling it.
The launcher archives it (evidence preserved, path cleared) at launch; a reader about to act
on a terminal verdict checks the artifact is YOUNGER than the run it describes (heartbeat
comparison). Measured: the B2192 chain halted on sw50's killed-parallel-era
INCOMPLETE_MAX_LEGS summary while the live resumed run was at sim day 110. Sibling of #281
(artifact older than its generator); here the artifact is older than its RUN.

*Enforced by:* run_wave.py archive_stale_summary() at launch, pinned by
test_b2193_stale_wave_summary_is_archived_at_launch.

### #284 - AN ANALYSIS THAT RUNS PER EVENT IS RENDERED PER EVENT (B2198 / L651)

When a directive requires an analysis after every occurrence of an event (per config, per
landing, per batch), the per-event RENDER of that analysis is part of the mechanism - not
something the reporter remembers to write. Checking that the analysis RAN is a boolean and
answers a different question than the reader is asking. Measured: the post-config battery
auto-ran on every landing with its steps recorded, and the owner never saw a per-config
result because every report verified the run and quoted one number. Ship the renderer with
the runner, and have the runner invoke it at the same moment it announces completion.

*Enforced by:* scripts/postconfig_doc.py, rendered by scripts/postconfig_landing.py
(`render_report`) on EVERY landing - the supervisor the engine itself invokes from
backtest/run_phase1a.py `_postconfig_landing_hook` and that run_wave.py calls idempotently, then
re-renders after its own leg evidence lands (B2520 / #288; the earlier text *imported by
run_wave.py:289 at arm completion* described the run_wave-only wiring that left direct and resume
launches with no render at all - cfg1, S6-B2515).
(S6-B2310 CORRECTION: previously named `postconfig_report.py invoked from run_wave.py` -
MEASURED, nothing invokes that file; it is a hand-run CLI. L499/#224.)
pinned by test_b2198_battery_result_is_rendered_not_only_written (both directions) and
test_b2520_report_renders_every_family_and_names_open_steps.

### #286 - FIND THE BRANCH THAT EMITS A STRING BEFORE FILING IT AS WRONG (B2266 / L688)

A message's audience is not everyone who sees the tool fire - it is whoever reached the line that
prints it, and those differ exactly when the emitter sits behind a branch. Advice text is
branch-specific by nature, so judging it on the string alone manufactures defects out of accurate
parts. MEASURED: a gate's *'create .stop_exempt'* line was drafted as misleading advice on a
correct reading of the control flow; the line is emitted only from `_main_legacy`, the one path
where the hatch works. Locate the enclosing function first - one command. Sibling of #276b, which
asks the same path question about injection seams rather than about text.
JUDGMENT-ONLY for detection (the artifact is identical whether or not the branch was checked);
durability via this item and the L688 SKILL.md bullet.
### #285 - A LOCKED FORMAT IS PRINTED, NEVER RETYPED (B2199 / L652)

When an artifact's format is declared LOCKED, every presentation of it comes from the
command that renders it - not from retyping into a response. Retyping is a second,
unreviewed renderer, and its omissions read as editorial trimming rather than as data
loss. Measured: Table C is locked at 12 columns and was quoted three times as 9,
dropping `P1-P6 bands tested` - the column separating a config that searched 18
parameter values from one that searched 2. Applies to Table A/B/C, the roster, the
post-config report card, and any format a batch declares locked.

*Enforced by:* scripts/show_table_c.py (prints the locked table from the graded
artifacts), pinned by test_b2199_table_c_is_printed_with_every_locked_column.


### #188 - A TEST'S LITERAL EXPECTED-SET CITES ITS DERIVATION (S6-B2306, council-chosen remedy 2026-08-27)

When a test asserts a hardcoded set/list of expected values, it must either BUILD that set from a defining source in-code (parse, import, glob) or carry a comment naming where the set came from.

*Why:* a pin's expected set was seeded from OBSERVED output - verdict strings seen in step-1 grids - which never exercised the gate branch, so `PASS` and `FAIL` were missing and the pin failed against a CORRECT codebase (L697). The observed population and the DEFINED population are different columns.

*Why this is a checklist line and NOT a gate:* the council was 0 of 5 in favour of building one. First Principles: *'each hardcodes the literal shape of one caught bug into infra that runs every turn forever'*; the Executor: *'a checklist line catches this at write-time, forever, for free - a gate catches it at commit-time at the cost of another gate a future agent has to reason about, corpus-maintain, and debug when it false-positives.'* The detection question (was this literal typed from a definition or from a sample) is undetectable - both compile to the same tuple.

*Enforced by:* authored practice at pin-writing time. **NOT mechanised, deliberately.**


### #287 - TOTAL INSTRUMENT SILENCE THAT ENDS NORMALLY MEANS THE MACHINE STOPPED, NOT THE CODE (L731 / S6-B2488)

**Trigger:** any long-running job that appears to have hung - a stalled
counter, a frozen heartbeat, a phase duration wildly out of family.

**Before diagnosing a code defect, ask the operating system.** A hang leaves
PARTIAL evidence: some threads advance, exception handlers fire, logs
dribble. **Total silence that then ENDS NORMALLY is not a hang** - it is a
process that was not running, and a process can stop running with no bug in
it. On Windows one command settles it:
`Get-WinEvent -ProviderName Microsoft-Windows-Kernel-Power` over the window;
Event 42 is entering sleep, 107 is resume, 187 is an explicit
SetSuspendState call.

**MEASURED (B2481 cfg1):** a screen day reported dur=55213.961s against a
66 s median. The machine slept 3 seconds after the last heartbeat and woke
15.3 hours later; real compute was about 32 seconds. Because `time.time()`
counts suspended time, the cap killed a HEALTHY run at elapsed_hours=16.10.
I published a code-defect RCA first, then a GIL hypothesis which its own
probe refuted (a genuinely GIL-holding call still yielded 8pct of beats;
this yielded exactly 0pct - **exactly zero is a different signature**).

**Two rules follow.**
(a) **No in-process watchdog crosses a suspend.** Thread, subprocess, signal
handler and cron are all frozen. L637's "outside the guarded flow" has a
THIRD property beyond control flow and scheduler: the machine being powered.
Design for TOLERATE, not prevent - a run cannot refuse an explicit user
suspend and should not try.
(b) **Any wall-clock figure that GATES something must state suspended and
active separately.** Sweep siblings when you fix one: B2490 fixed the
supervisor's reporting and left the in-loop cap - the guard that actually
fired - reading raw wall-clock, closed only by B2492.

**Sibling rule (L732):** after fixing any wall-clock / timing / resource
measurement, grep the IDENTIFIER tree-wide - not the file - and sort hits into
GATES vs REPORTS. MEASURED class for this incident: 5 sites - 2 gating in the
live engine (fixed B2490+B2492), 2 gating in AWS-era scripts off the current
path (recorded), 1 diagnostic (the 7 PHASE_TIMING markers, deliberately left:
this item's boundary is 'gates something'). A pin written against the code you
just changed confirms the patch, not the property.

**Third rule (L733):** a docstring's POSITIVE claims get verified against the
body; its NEGATIVE claims get believed, because an exclusion describes inputs
the code never sees. When a detector's docstring says what it will NOT fire on,
compute the boundary at the LIVE parameter values and state the numbers there.
MEASURED on this incident's own fix: "a slow disk never registers as a suspend"
against a 150 s threshold at the live 30 s interval, where a 180 s stall is
credited 150 s. **A detector that cannot separate two causes must not be wired
to a control that assumes it can** - reporting is safe, gating is not.

**Pins:** test_b2490 x2, test_b2492, test_b2495, test_b2496.

**#226 SCOPE EXTENSION (L734):** prove-it-can-fail extends from pins to
DESIGNS - before presenting any rule/threshold/mechanism recommendation,
evaluate it on the motivating incident's own numbers. One function call.
MEASURED: the 3x wall backstop survived two owner presentations with a
written case-against and died on f(16.10, 15.32, 4.0) - prose reasons about
a rule, the matrix runs it. Mechanism: test_b2502's boundary matrix, pinned
to the incident's real numbers; test_b2508 holds this rule in the skill.

### #288 - A MANDATORY POST-EVENT SEQUENCE IS INVOKED BY THE EVENT'S PRODUCER, AND EVERY STEP IS RECORDED OR THE LANDING BLOCKS (B2520 / L736)

**Trigger:** any sequence a directive requires "after every X" (config landing, batch completion,
wave arm) - and, separately, any owner question of the form *"why did this not run automatically?"*
asked a SECOND time about the same mechanism.

**Owner ruling 2026-09-01 (verbatim):** *"Once the config lands, i want it to run automatically no
exceptions and share results with me."* Four rules follow, each with its mechanism named:

(a) **The PRODUCER of the event invokes the sequence** - not an orchestrator that some launch shapes
bypass. The post-config battery is invoked from `backtest/run_phase1a.py::_postconfig_landing_hook`
the moment `trade_exit_detail.csv` is written, through ONE supervisor (`scripts/postconfig_landing.py`)
that every launch path shares: engine hook, `run_wave.py` (idempotent per cube fingerprint, so a real
engine's wave call is a no-op and a substitute engine's is THE landing), and a manual call. Opting out
is an explicit `POSTCONFIG_LANDING=0`, logged. The hook fires once the cube file exists; a run that
dies before writing one is the monitor's case (L641, absence of an ending reads as DEAD), not the
battery's, and a supervisor pointed at a directory with no cube prints FAIL and exits 2.

(b) **Every step is written to the ledger on every run.** DONE with evidence, N/A with a reason, or
FAIL / OPEN - **SKIPPED is not a disposition and is in no terminal set**
(`verify_postconfig_complete.py::terminal_for` returns {DONE, N/A} for every step; `is_closed` also
requires the evidence / reason text). The four "judgment" steps are NOT exempt: an eight-lens battery
runs step 5 and writes `<cube>_lenses.json`; step 6 is OPEN while any lens finding lacks a recheck and
N/A-on-evidence when there is none; step 7 checks that every swept parameter reaches the engine, by
step number; step 8's verdict is computed from the grid artifact WITH its denominators. A step that
cannot run FAILs and blocks. A terminal row is never downgraded by a re-run; the re-run's result is
appended beside it for a human to disposition (`run_postconfig.py::merge_row`), and a re-run never
truncates the evidence already on the row.

(c) **Grading is family-aware and fails CLOSED.** `run_postconfig.py::FAMILIES` maps a cube's strategy
to its grader + spot-check; a cube with no registered family gets FAIL on every graded step, never a
quiet pass (the institutional family - `grade_institutional_config.py` + `spot_check_institutional.py`
- was added because cfg1 landed with no grader and its grid was hand-built at B2511).

(d) **The result reaches the owner mechanically.** Each landing is appended to
`output_audit/postconfig_landings.jsonl` with `reported_to_owner: false`; the turn preamble
(`inject_tier3_discipline.py::undelivered_landings_banner`) lists every undelivered landing with its
findings untruncated; the Stop hook (`verify_turn_compliance.py::scan_undelivered_landing`) BLOCKS the
turn until a `LANDING REPORT: <cube>` block appears in the final response, and marks it reported only
then; the ONE report (`output_audit/POSTCONFIG_REPORT.md`) carries a Landings section; the supervisor
commits and pushes the ledger, report and per-cube artifacts (never the cube directory) and raises a
desktop toast. The channel the owner reads is the response, so the response is what the gate checks.

**MEASURED (B2520):** the owner asked six times (B2177, B2192, B2198/B2208, B2211, S6-B2436,
S6-B2515) and got six instance fixes. The six mechanisms, each of which had to fail for a landing to
go unreported: wiring location (battery invoked only from run_wave, so direct and resume launches ran
nothing - cfg1 had no gate receipt); phantom deferral (nine steps pre-written SKIPPED
"PENDING-WAVE-REVIEW" for a review batch that never existed, L721); family-conditional grading that
passed silently on an unregistered strategy; an all-or-nothing ledger write that recorded nothing
when one check crashed; judgment steps designed never to auto-run; and no delivery channel at all.
Each fix closed the mechanism that had just failed; the GENERALIZATION MANDATE was satisfied in
letter every time. **A mechanism the owner has asked about more than once is a class defect - count
the asks (L736).**

**Pins (all EXECUTED at B2520):** test_b2520_engine_hook_lands_every_cube,
test_b2520_battery_records_all_nine_steps_and_fails_closed,
test_b2520_battery_and_gate_share_one_step_list_and_one_terminal_set,
test_b2520_landing_supervisor_is_idempotent_per_fingerprint,
test_b2520_stop_hook_blocks_until_a_landing_is_reported,
test_b2520_turn_preamble_lists_undelivered_landings,
test_b2520_report_renders_every_family_and_names_open_steps,
test_b2520_asserts_non_execution_reads_assertions_not_mentions,
test_b2520_merge_row_never_truncates_and_never_downgrades_terminal,
test_b2520_institutional_grader_golden_on_cfg1, test_b2520_institutional_spot_check_artifact_schema;
retargeted: test_b2116, test_b2211, test_b2439, test_b2440, test_b2450.

**NOT yet exercised on a real landing:** the git-push and toast paths - every landing so far ran
`--no-git --no-notify`, and `commit_and_push` is covered only by the stub arms of the idempotence
pin (S6-B2520g). Amends #223 (SKIPPED clause retired) and #284 (enforcement note).
### #289 - A UNIFORM VALUE ACROSS EVERY ROW IS A PARSER HYPOTHESIS (B2520p / L724)

**Before quoting any tally, distribution or coverage figure from an extractor written in the same
turn, print ONE RAW ROW of the thing being parsed.** One command, and it settles what no amount of
re-reading the extractor will.

**The trigger is UNIFORMITY, not a particular value.** L724(2) named 0pct and 100pct; those are the
loud cases. The general form is one value for EVERY member of a heterogeneous population - `{None:
8}` across eight different checks, `0` for every row, `True` for every field. Real data about
different things does not agree perfectly, so perfect agreement is evidence about the READER first.

**A dict-shaped tally hides this better than a percentage.** `{None: 8}` renders as output, not as
an error; `0 of 8` at least invites the question. Watch tallies, Counters and groupbys hardest.

**And it lands most easily inside a VERIFICATION pass.** A probe written precisely because some
other source was not trusted inherits none of that suspicion - the scepticism was spent on the
source, and the instrument replacing it arrives unexamined (L679).

MEASURED (B2520p): asked whether all nine post-config steps ran on config 1, I tallied adversarial-
lens severities on a guessed field name (`severity`; the artifact uses `level`). The tally read
`{None: 8}` and would have reported **0 WARN / 0 FAIL** on a step whose one real finding is an open
ticket. Printing one raw row showed the correct field immediately; the corrected tally is 1 WARN /
7 INFO.

Would have caught: the B2419 13F decile pass (0 of 1849 from `ast.literal_eval` on JSON), and this
instance. Would NOT have caught a parser that yields plausible VARIED values from the wrong field -
that is #276b's path question, not this one.

Mechanism: DETECTION is JUDGMENT-ONLY - no scan knows which field name suits an artifact. Durability
pinned by `test_b2520p_uniform_value_is_a_parser_hypothesis_is_anchored`, which asserts the rule
survives in both CHECKLIST.md and LEARNINGS.md. This item also repairs L724's ANCHOR: it was cited
in SKILL.md and in no CHECKLIST item, which is the orphan-rule shape ANCHOR-THE-RULE exists to stop.

### #290 - A CHECK OWED EVERY LANDING IS DONE ONLY WHEN A SUPERVISOR RUNS IT UNPROMPTED (B2569 / L752)

**The moment an analysis check is invented, run, or approved for ANY config's landed cube, the same
turn does one of exactly two things: wires it into the post-config battery (a family-runner leg
that FAILS closed), or files a ticket naming the battery gap.** "Executed once" + "the tool exists"
+ "it is documented" is the three-part disguise of an unwired check - none of those three runs it
on the NEXT landing.

**The trigger is the words "per config", "per landing", "every strategy", or membership in a
pre-registered band.** If the design counts a measurement as part of every config's grade (the
P7/P8 free levels were counted in the 17-config band's coverage), then producing it once, at
strategy level, on a different cube shape, is the N1 class bug - not a cheaper substitute.

**The band-side companion (SS0.7):** free grading tightens only, so every looser-than-production
level in a PERSISTED parameter's band is engine-only BY CONSTRUCTION and must be either scheduled
WITH a proven actuation mechanism (the env knob must reach the gate - grep it, L751's three links)
or struck with NOT-MEASURED-BY-DESIGN and a reason. Banded-unscheduled-unrunnable rows advertise
coverage the programme cannot deliver.

MEASURED (B2569): S6-B2501's free-level grading existed as a correct tool (B2504), a registered
family battery (B2520), and a pre-registered manifest (B2527) - three consecutive batches, zero
wiring, four configs landed ungraded. Wired at B2569 (`step2_free_levels`, reproduction-gated:
every covered landed trade must re-pass the production gate offline before any level is believed);
retro-run reproduced all 4 landed cubes exactly (609/531/405/350-of-373 with the 23 S6-B2512 rows
counted, never silently failed).

Mechanism: `run_postconfig.run_institutional` free-levels leg + `_GRADER_CHECKS` routing + pins
test_b2569_battery_runs_free_levels_on_every_institutional_landing /
test_b2569_free_level_reproduction_gate_and_specs_derivation. DETECTION of new unwired checks is
JUDGMENT-ONLY; the pin holds the wiring that exists.

### #291 - A SCRIPT WITH A STRAT CONSTANT IS THE FIRST INSTANCE OF A PORTABILITY CLASS; REGISTRATION IS CHECKED AT LAUNCH (B2573 / L754)

**Any grader, spot-check, verifier, or table renderer written for ONE strategy (a `STRAT`
constant, a hardcoded key set, a family-specific env knob) is an adapter member behind ONE
family contract - params_from_env / grade / free_levels / spot_check / engine_anchors - and the
LAUNCH gate refuses a spec whose strategy has no complete adapter.** A battery that fails closed
at LANDING has already spent the engine's hours; the refusal belongs before the spend.

**The trigger is writing or reusing anything that names a strategy in code, OR copying a
per-family script for the next family.** The copy is the tell: the second copy is the moment the
contract should have been extracted (B2504 grade_institutional_config.py was that moment).

**Pre-flight for a new strategy (until S6-B2573a/b ship): run the runbook SS11.1 ON-RAMP table
R1-R9 and paste each probe's output - a missing item is a STOP.** Every mechanism a runbook step
cites is named with its file or marked PROPOSED-NOT-BUILT (B1335 rule 2 applies to runbooks).

**MEASURED 2026-09-02 (B2573):** FAMILIES 2 of 219; 7 of 9 battery/runbook scripts one-strategy;
0 of 4 launch-path scripts check registration; the runbook had no ordered list, smc commands at 4
generic sites, 5 stale numbers, and a documented launch command that is not the live path.
Tickets S6-B2573a-i carry the class fixes; none are built. Detection is JUDGMENT-ONLY until the
S6-B2573a adapter pin exists; the pin holds the contract that exists.
