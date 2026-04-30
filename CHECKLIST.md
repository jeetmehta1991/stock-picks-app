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
