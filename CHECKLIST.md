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
