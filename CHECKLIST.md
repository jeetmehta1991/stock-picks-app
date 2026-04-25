# Pre-Action Checklist

Run this before every suggestion or execution — no exceptions.

1. Have I thought through this completely, including edge cases and environment constraints?
2. Have I shown the full plan and waited for explicit approval?
3. Am I staying within the current phase — not jumping ahead?
4. Does this actually help with what was asked, or am I solving a different problem?
5. What can go wrong? Have I flagged it proactively? Before any git reset --hard, run git status first — uncommitted work is lost permanently.
6. If modifying CLAUDE.md — have I shown the exact before/after diff and received explicit written approval?
7. If pushing code — am I pushing to `claude-updates` only, never directly to `main`?
8. Is this a decision that requires owner approval before I proceed?
9. Chain commands where logical — commit and push should always be combined. Only split commands when each step needs independent verification first.
10. For any command running longer than 5 minutes, always use nohup to prevent terminal closure killing it:
    nohup bash scripts/download_cache.sh > download.log 2>&1 &
    tail -f download.log
11. Always capture granular data before aggregating. Granular = can always re-aggregate. Aggregate only = cannot re-derive. Applies to data, outputs, cache, and API calls.
12. Before building any integration with an external API or service, verify exact tier/plan access for every endpoint needed. Test one call per endpoint before building the full script.
13. Always run a small batch test (25 tickers, 1 month) before scaling to full universe. Verify agent outputs, confidence tiers, and granular outputs are correct before spending on full run.
14. After every audit or code change: run python backtest/tests/run_all_tests.py — ALL tests must pass before proceeding. Reading code is not verification. Running code is. Reading code is not verification. Running code is.
15. For every data handoff between modules, verify producer keys match consumer expectations by running code — not by reading it. Verify agent outputs, confidence tiers, and granular outputs are correct before spending on full run. Granular = can always re-aggregate. Aggregate only = cannot re-derive. Applies to data, outputs, cache, and API calls.
