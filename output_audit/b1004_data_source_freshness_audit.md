# Source: CLAUDE.md banner "Latest pyramid" / Sprint 0A data_prefetch directory inventory per CHECKLIST #77.

# B1004 — Data-Source Freshness Audit (2026-06-22)

**Source:** Council 101 Option-8 5-turn standing approval T2/5
**Status:** Audit-only; refresh requires explicit owner approval (CHECKLIST #13 expensive-job)

---

## Freshness inventory

| Source | Files | Last refresh | Days stale | Refresh cost class |
|---|---:|---:|---:|---|
| `polygon` | 76,492 | 2026-06-02 | 20 | $ (Polygon Stocks Starter; per-API cost) |
| `sec_edgar` | 18,709 | 2026-06-14 | 8 | FREE (SEC public filings) |
| `sec_edgar_decoded` | 4,342 | 2026-06-14 | 8 | FREE (decoded local) |
| `finra` | 1,926 | 2026-05-31 | 22 | FREE (FINRA short interest) |
| `derived` | 17 | 2026-05-27 | 26 | LOCAL (re-compute from cache) |
| `fred` | 102 | 2026-05-25 | 28 | FREE (FRED API) |
| `wikipedia_revisions` | 1,412 | 2026-05-16 | 37 | FREE (laptop-local per L88 exception) |
| `aaii` | 2 | 2026-05-10 | 43 | FREE (AAII Investor Sentiment) |
| `cftc` | 73 | 2026-05-10 | 43 | FREE (CFTC COT) |
| `stocktwits` | 1,939 | 2026-05-09 | 44 | $ (API rate-limited) |
| `quiver` | 26,195 | 2026-05-09 | 44 | $$ (Quiver Trader subscription) |
| `finnhub` | 18,324 | 2026-05-09 | 44 | $ (Finnhub API) |
| `alfred` | 80 | 2026-05-08 | 45 | FREE (ALFRED FRED archived) |
| `apewisdom` | 9 | 2026-05-08 | 45 | FREE (ApeWisdom public) |
| `cnn_fg` | 9 | 2026-05-08 | 45 | FREE (CNN Fear & Greed scrape) |
| `pytrends` | 1,417 | 2026-05-08 | 45 | FREE (pytrends; rate-limited) |
| `sec_xbrl` | 1,663 | 2026-05-08 | 45 | FREE (SEC XBRL) |
| `wikipedia` | 1,414 | 2026-05-08 | 45 | FREE (per L88 laptop-local) |

**Total cached files:** 153,610 across 18 sources.

---

## R5-launch-readiness implications

### Sources requiring refresh BEFORE R5 (PIT-critical):

| Source | Why critical | Recommended refresh |
|---|---|---|
| `polygon` | OHLCV + financials + corporate actions; 20 days stale acceptable for R5 (most cells use cached daily data through 2026-06-02) | Optional pre-R5; ship-ready as-is for backtest window ending 2026-Q1 |
| `finra` | Short interest data drives Pattern S + SM-5 borrow-guard; 22 days stale = misses 2 bi-monthly cycles | Owner-approved refresh recommended if R5 launches |
| `fred` | Yield curve + macro indicators; 28 days stale acceptable (FRED updates weekly; rolling 2-4 week lag normal) | Optional |
| `quiver` | 13F + insider + congressional; 44 days stale = misses 1 quarter of 13F filings | Owner-approved refresh recommended ($$ cost) |
| `finnhub` | Earnings calendar + estimates; 44 days stale = misses Q2 2026 prints | Owner-approved refresh recommended ($ cost) |

### Sources acceptable as-is for R5:

| Source | Rationale |
|---|---|
| `sec_edgar` + `sec_edgar_decoded` | 8 days fresh; recent updates capture 8-K filings + 13D/13G activist activity |
| `aaii` + `cftc` + `cnn_fg` | Survey/sentiment data; 43-45 days lag acceptable for sentiment overlay |
| `pytrends` + `apewisdom` + `stocktwits` | Social/search data; cube treats these as auxiliary signals (not primary edge) |
| `wikipedia*` | Universe-membership PIT data; refresh quarterly per CHECKLIST #19 (last quarterly refresh ~2026-05-08 within 90-day window) |
| `derived` | Internal computed (correlation_matrix_t1a, cointegrated_pairs_t1a, institutional_persistence_t1a); regen on demand from upstream caches |

---

## Refresh-cost summary

| Tier | Sources | Total cost estimate | Owner-approval required? |
|---|---|---|---|
| FREE | sec_edgar, finra, fred, alfred, apewisdom, cnn_fg, pytrends, sec_xbrl, wikipedia, aaii, cftc, wikipedia_revisions | $0 | Low (still per CHECKLIST #13 batch protocol) |
| $ | polygon, finnhub, stocktwits | ~$50-150 (per refresh) | HIGH (per CLAUDE.md L86/L95 + CHECKLIST #13/22/23/29) |
| $$ | quiver | ~$50-100 (subscription) | HIGH |

**Total full-refresh estimate:** $100-300 (cost) + 4-12 hours (runtime).

---

## Recommended actions (owner-decision)

### Path A: Pre-R5 minimal refresh (FREE sources only)
- Refresh sec_edgar / finra / fred / aaii / cftc / cnn_fg / apewisdom / cnn_fg
- Cost: $0; runtime ~1-2 hours
- Outcome: R5 launches with current FREE sentiment + macro + insider data

### Path B: Pre-R5 full refresh (FREE + $ + $$ sources)
- Refresh all 18 sources
- Cost: $100-300; runtime 4-12 hours
- Outcome: R5 launches with all sources at <7 days stale

### Path C: Defer refresh; launch R5 with current cache
- Accept 20-45 days stale across sources
- Cost: $0; runtime 0
- Outcome: R5 measures cube on 2026-05-08 to 2026-06-14 universe state
- Risk: PEAD-class strategies miss latest earnings; FINRA-gated SHORT strategies miss latest short-interest

### Path D: Defer refresh + DEC-PHASE-6.5-RESET refresh schedule
- Pre-register refresh schedule for post-R5 cube re-measurement
- Match R5 launch cadence (e.g., monthly cube refresh)

---

## Standing-approval-scope compliance

This audit is doc-only / read-only. **No refresh executed.** All refresh decisions require explicit owner approval per:
- CHECKLIST #13 (API cost approval gate)
- CHECKLIST #22, #23, #29 (expensive-job protocol)
- CLAUDE.md L86/L95 ($150 in discarded work past incidents — "small test batch → manual review → owner approval → scale")
- `feedback_local_changes_default_global_needs_approval`

---

## Cross-references

- CLAUDE.md banner (last refresh status)
- CHECKLIST.md #13 (expensive-job protocol)
- CHECKLIST.md #19 (universe quarterly refresh)
- LEARNINGS.md L86 / L95 (API-cost-discarded incidents)
- `output_audit/b997_session_handoff_summary.md` (prior session deliverable)
- `output_audit/b995_inv_057_058_fix_batch_prep.md` (Polygon parquet inspection)

**Status:** Audit complete; ready for owner-decision on refresh approach (Path A/B/C/D).
