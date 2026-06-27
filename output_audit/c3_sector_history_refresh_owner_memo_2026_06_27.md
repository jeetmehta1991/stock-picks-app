# C-3 Sector History Refresh — Owner-Action Memo (B902-A wiring audit finding)

# Source: W4 wiring audit B1033 + Council 130 Option-7 C-3 surface per
# owner directive 2026-06-27 "Category C and phase C execute. Council
# this." + L88 exception scope per CLAUDE.md per CHECKLIST #77.

## Summary

`Backtesting universe/sector_history.csv` has been stale since 2023-03-17 (1190 days as of 2026-06-27). Per W4 wiring audit, 10 `classification_change_*` strategies in screener.py depend on this data being current. Per CLAUDE.md L88 exception, Wikipedia + general internet browsing is permitted for ONE-TIME assembly of historical universe membership files **but** requires owner spot-check before commit.

## Why owner-action required

Per CLAUDE.md HARD RULE + L88 caveat (iii):
- Wikipedia/general-internet browsing for historical assembly is laptop-local only
- Manual verification before commit is REQUIRED
- Owner must spot-check at least 4 of 4 high-impact reclassifications vs S&P DJI press releases (per prior L88 application precedent)

Claude can attempt research within L88 exception scope BUT cannot autonomously commit GICS reclassifications without owner spot-check. Per `feedback_audit_recommendations_against_existing_directives` + L88 caveat (iii).

## What needs to be refreshed

| Field | Source priority | Last update | Status |
|---|---|---|---|
| GICS sector reclassifications | S&P DJI press releases (primary) | 2023-03-17 | 1190 days STALE |
| Symbol additions / removals | Wikipedia list_of_S&P_500_companies Table 1 (fallback per L88) | varies | Master Dedup CSV is 53 days stale; same problem class |
| Effective dates | S&P DJI annual rebalances + special index events | varies | Needs annual review |

## Recommended approach (3 options)

### Option-3a: Claude researches under L88 exception + surfaces patch for owner spot-check
- Claude greps S&P DJI press releases (paid; needs API key OR manual browse) + Wikipedia Table 1 historical data
- Output: proposed CSV update + change list per ticker
- Owner spot-checks (≥4 high-impact reclassifications) per L88 caveat (iii)
- Owner commits if verified

### Option-3b: Defer to next universe refresh batch (per P1-UNIVERSE-REFRESH-POST-R5)
- Bundle with T1a quarterly + T2/T3 monthly refresh
- Single coordinated batch with consistent S&P DJI source attribution
- Per Council 120 verdict (refresh post-R5)

### Option-3c: Sprint-1 manual research as separate workstream
- Owner researches independently
- Updates CSV via standard refresh script
- Per CLAUDE.md cadence (T1a quarterly = ~2026-08-05 due)

## Council 130 lean: Option-3b (DEFER to P1-UNIVERSE-REFRESH-POST-R5)

**Rationale:**
- 10 `classification_change_*` strategies are LOW PRIORITY (not in critical R5 launch path)
- Sector reclassifications are SLOW EVENTS (~few per year)
- Bundling with quarterly refresh avoids duplicate manual research overhead
- Per Council 120 P1-UNIVERSE-REFRESH-POST-R5 ticket already queued

**Risk:**
- 10 strategies operate on stale GICS until refresh
- Acceptable risk: classification changes are rare; stale data biases toward FALSE-NEGATIVE (strategy doesn't fire on legitimate sector change) which is the safer error per `feedback_no_a_priori_strategy_pruning` analog

## Owner-action checklist (when ready to execute)

```
[ ] Decide Option-3a (Claude research) vs Option-3b (defer to refresh) vs Option-3c (Sprint-1)
[ ] If 3a: provide S&P DJI access OR approve Wikipedia-only fallback per L88
[ ] If 3a: spot-check ≥4 reclassifications per L88 caveat (iii)
[ ] If 3a: approve commit OR direct refinements
[ ] If 3b: confirm bundling into P1-UNIVERSE-REFRESH-POST-R5
[ ] If 3c: owner-self-research timeline
```

## Cross-references

- CLAUDE.md L88 (Wikipedia/general-internet exception for one-time historical assembly)
- CLAUDE.md CHECKLIST #19 (refresh quarterly)
- L89 (SNDK 9-month delay precedent)
- P1-UNIVERSE-REFRESH-POST-R5 ticket (Council 120)
- B902-A-DATA-GAP sector_history.csv stale entry
- 10 `classification_change_*` strategies in screener.py
- `scripts/refresh_sector_history.py` scaffold (exists; needs events.json input per L88)

## Status

🔴 **OWNER DECISION** — Council 130 recommends Option-3b (defer to P1-UNIVERSE-REFRESH-POST-R5 bundle). Awaiting owner direction.
