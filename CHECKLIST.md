# Pre-Action Checklist

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
    c. git diff backtest/data/sp500_tickers.csv               # verify changes
    d. git add backtest/data/sp500_tickers.csv
    e. git commit -m "Universe refresh: QX YYYY S&P 500 update"
    f. git push origin main
    Source: slickcharts.com (NEVER Wikipedia — blocked, fragile, not point-in-time — L88)
    Schedule: January, April, July, October. Add to calendar.
    Immediate spinoff: python scripts/refresh_extended_universe.py --add TICKER --reason spinoff_from_PARENT --write

20. MONTHLY (live Stage 3+) — Tier 2 extended universe refresh:
    python scripts/refresh_extended_universe.py --write
    git add backtest/data/extended_universe.csv && git commit && git push
    Run immediately after any major spinoff announcement (>$5B market cap).

21. MONTHLY (live Stage 3+) — Tier 3 momentum watchlist refresh:
    python scripts/build_momentum_watchlist.py --write
    git add backtest/data/momentum_watchlist.csv && git commit && git push
    Out-of-cycle (stock >50% in 30 days): --out-of-cycle --write flag.
    NEVER run momentum watchlist for backtesting — use static snapshot from run start.

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
