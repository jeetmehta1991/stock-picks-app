<!-- Source: per CHECKLIST #77 canonical-source; Council 305 B1264 2026-07-08; machine artifact: DATA_READINESS_AUDIT_2026-07-08.json; regenerate via `python scripts/data_readiness_audit.py` -->
# DATA READINESS AUDIT — pre-R5 scope-lock gate (B1264, owner decision B)

**Method:** programmatic scan (`scripts/data_readiness_audit.py`, re-runnable at every R5 ladder rung) — presence, ticker coverage vs the 1,937-symbol Master Dedup universe, temporal span (25-file sampling per CHECKLIST #154 floor), and known-critical field checks. Two script-side errors caught and fixed during the run (path phantom-names for quiver/sec_edgar dirs; a null-rate double-count) — numbers below are from the corrected run.

## Verdict: GREEN for the R5 window (2022-05 → 2026-05-05) with 3 known exceptions

| Source | Coverage | Span | Status |
|---|---|---|---|
| OHLCV (cache + polygon) | 99.5% of universe | 2021-05 → 2026-05-05/08 | ✅ covers R5 window + warmup; **2 months stale vs today** — fine for R5 (window ends 2026-05-05), refresh required before Phase 1B-α (P1-UNIVERSE-REFRESH-POST-R5, already queued) |
| FINRA short interest | 99.4% | 2021-06 → 2026-04-30 | ✅ with caveat: `shares_outstanding` **100% NULL** (confirmed at scale) — B1240 Finnhub profile2 fallback covers it (99.9%) |
| Finnhub profile2 / company_news | 99.9% | news sampled span 2018-07 → 2026-05 | ✅ NOTE: sampled news files reach back to 2018 for some tickers — better than the B1242 "2025+" belief; per-ticker timeline still varies (L201 discipline applies) |
| Polygon news / financials (earnings source) | 99.3% / 99.9% | — | ✅ earnings dates derive from financials filing_date (fetcher.py:244) |
| Quiver congressional / insider / institutional | 99.9% each (1,941 files) | — | ✅ |
| SEC EDGAR SC_13D / 8_K | 88.4% each (1,715/1,716 files) | — | ✅ acceptable (13D/8K filers are a subset of the universe by nature) |
| FRED VIXCLS (+ get_vix consumability probe) / T10Y2Y / AAII | 1,623 / 1,588 / 2,022 rows | — | ✅ VIX loads via the actual engine path |
| Derived: institutional_persistence_t1a / cointegrated_pairs_t1a | 5 snapshot files each (T1a-wide layout; per-ticker coverage metric N/A) | — | ⚠ B1216 30% ticker-gap finding stands (S5-B1216 open; B1230 graceful degradation active; 1 strategy) |
| **index_rebalance_events.parquet** | — | — | 🔴 **the ONLY missing artifact** (Council 236 blocker #1; DEC-370/DEC-380) — 4 strategies remain BLOCKED_UPSTREAM |

## Scope-lock decision points for owner

1. **index_rebalance_events**: run R5 with the 4 index-event strategies BLOCKED_UPSTREAM (they're already classified; parquet lands post-R5 per Sprint 5) **[recommended — do not let 4 strategies gate 215]**, or build the parquet first (adds days).
2. **S5-B1216 persistence gap**: accept B1230 degradation for R5 (1 strategy) **[recommended]**, or ship the expansion first.
3. **OHLCV staleness**: R5 runs on the existing window ending 2026-05-05 **[recommended — matches PROJECT_PLAN spec]**; universe+OHLCV refresh stays post-R5.

If all three recommendations accepted → **scope locks and the R5 phase ladder begins** (dry run 3-5 tickers → small 25-50 → mid ~150 → full, owner gate per rung).
