# TRIAGE_PREP_2026_05_19.md — Pre-drafted recommendations for T3+T4 triage session

**Purpose:** Pre-drafted per-item recommendations for the triage session scheduled tomorrow morning (2026-05-19). Owner can approve / reject / modify each call quickly instead of starting from scratch.

**Scope correction:** Originally framed as "4 PROPOSED + 22 open INVs." Verified 2026-05-19: the 🔴 markers in `AUDIT_BACKLOG.md` are all properly-deferred P3/P4 backlog items with Pass 53 review cycle CLOSED per DEC-589 — they're parked, not actively pending. Actual scope = **31 open INVs** from OPEN_INVESTIGATIONS.md after the 7 reclassifications landed in `9b261b3f9` 2026-05-18.

**Decision states:**
- `fix-now` — Stage 2 blocker; immediate engine fix needed
- `promote-to-BUG` — engine bug; add to BUG_REGISTER.md, fix in Stage 2
- `convert-to-DEC` — needs strategic decision; promote to AUDIT_INDEX as DEC
- `defer` — not urgent for Stage 2; revisit Phase 1B/1C+/Stage 3
- `wontfix` — superseded / no engine consumer / canonical source elsewhere

---

## TIER 1 — Stage 2 blockers (5 items — recommend address before T0 close-out lands)

### INV-014: `trade_log.parquet` silent CSV-only degrade on `--no-agents`
- **Recommendation:** **promote-to-BUG → fix-now (before T0)**
- **Why:** Phase 1A baseline runs are `--no-agents`; this is the configuration we just ran. DEC-491 says Parquet is PRIMARY. T0 merge would silently miss Parquet outputs for current Phase 1A-α batches. Fix is small: in [backtest/results/writer.py](backtest/results/writer.py) DEC-491 block, replace empty `agent_reasoning` struct with `None` (or drop column from Parquet write entirely when uniform-empty).
- **Effort:** ~15 min fix + same-commit data-integrity test
- **Blast radius:** small (single function in writer.py); not engine-critical path
- **Risk if deferred:** T0 dashboards may show only CSV data; verification matrix may flag missing parquet artifacts

### INV-050: Walk-forward folds suppressed under `--no-git`
- **Recommendation:** **promote-to-BUG → fix-now (before T0)**
- **Why:** [backtest/run_phase1a.py:208](backtest/run_phase1a.py#L208) `walk_forward=not args.no_git` couples WF to a flag that has no semantic relationship. All Phase 1A-α batches just ran with `--no-git --no-walk-forward` (intentional WF suppression at per-batch level — merged result should get WF). Fix: decouple. Add explicit `--no-walk-forward` flag (already present, redundant); remove `not args.no_git` coupling; run WF on merged output at T0.
- **Effort:** ~10 min (one-line fix + run WF as part of T0 close-out script)
- **Blast radius:** zero (run_phase1a.py CLI args only; no engine logic touched)
- **Risk if deferred:** Phase 1A-α verdict missing WF analysis → cannot validate "rules-only Sharpe ≥ 0.7 OOS" robustly

### INV-051: Regime-stratified CV stratifier collapses to neutral-only
- **Recommendation:** **promote-to-BUG → fix-now (before T0)**
- **Why:** Per-trade `regime` column has bull/bear/neutral but stratifier reports all-neutral. Vocabulary mismatch between `calm/neutral/volatile/crisis` (stratifier expects) vs `bull/neutral/bear/crisis` (engine emits). DEC-422 cube populator depends on per-regime stratification. Without fix, cube under-resolves regime cells.
- **Effort:** ~30 min (locate stratifier code, add mapping bull→calm, bear→volatile, crisis→crisis, neutral→neutral; add unit test)
- **Blast radius:** medium (metrics.py or similar; touches cube populator)
- **Risk if deferred:** Phase 1A-α verdict missing per-regime breakdown; DEC-422 cube broken

### INV-052: Dispersion CB z-score 379 outlier
- **Recommendation:** **promote-to-BUG → fix-now (before T0)**
- **Why:** Numerical edge case: 1 of 74 dispersion-CB activations had z=379 (physically impossible; division-by-near-zero in rolling stddev). At 642-tkr scope likely fires more often (more tickers → more outlier denominators). Could cascade into spurious entry blocks. Fix: add guard `if rolling_std < 1e-6: skip` or cap z at 10.
- **Effort:** ~20 min (find dispersion-CB calc site, add epsilon guard, add regression test with synthetic flat-vol input)
- **Blast radius:** low (one circuit-breaker calc site)
- **Risk if deferred:** Phase 1A-α may see false-positive halts; verdict noise

### INV-053: Entry funnel 99.87% rejection rate
- **Recommendation:** **convert-to-DEC + investigate at T0** (not a bug, a tuning question)
- **Why:** 172,544 rejections vs 225 executed trades. Top reason: `portfolio_gate_max_open_positions_10_reached` (27%). The 10-position cap is universe-size-independent — at 642-tkr scope (T1a-α) the cap is even more restrictive. Owner-decision: keep at 10 OR scale with universe (e.g., 20 at 642 tkrs, 30 at 1937).
- **Effort:** ~30 min investigation post-T0 (audit rejection-reason concentration; recommendation report)
- **Blast radius:** none (purely analytical, not code change)
- **Risk if deferred:** none structurally; just may want to revisit position-cap before Phase 1A-β

---

## TIER 2 — Coverage / data gaps (15 items — recommend defer to dedicated data-quality sprint)

### INV-019: ALFRED 7-series gap behind FRED
- **Recommendation:** **defer** to Phase 1C+ sprint
- **Why:** Phase 1A/1B reads FRED current series. ALFRED vintages only matter for revision-aware strategies (Phase 1C+).

### INV-020: `prefetch_macro.py` SERIES dict (21) ≠ cache (57)
- **Recommendation:** **defer** but **bundle with INV-021** as one operational-debt sprint
- **Why:** Caches populated; canonical-source-of-truth violation but functional.

### INV-021: 5 orphan cache dirs without prefetch scripts (aaii/cnn_fg/alfred/pytrends/wikipedia)
- **Recommendation:** **defer** to operational-debt sprint (bundle with INV-020 + INV-022)
- **Why:** ~6-8h aggregate authoring; no Phase 1A impact.

### INV-022: Legacy `backtest/data/cache/quiver/` empty dir
- **Recommendation:** **wontfix** (housekeeping; harmless empty dir)
- **Why:** Cost of delete ≈ cost of leaving. Bundle with INV-021 if we ever do housekeeping pass.

### INV-024: Quiver gov_contracts field set (REFRAMED — needs USAspending)
- **Recommendation:** **convert-to-DEC** for Phase 1B+ data-source addition (NEW source: USAspending.gov)
- **Why:** Phase 1A baseline composite smart_money signal works without contract-detail. Phase 1B+ contract-detail strategies need new source.

### INV-025: SEC EDGAR filing-metadata-only (mitigated by INV-037 SEC XBRL)
- **Recommendation:** **convert-to-DEC** linking SEC XBRL prefetch as canonical (INV-037's pivot)
- **Why:** SEC XBRL covers structured fundamentals + filing data at free tier. Original 20-30h infra build was overestimated when SEC XBRL is the better solution. Estimate ~6-10h.

### INV-026: Polygon financials JSON-string (line items not extracted)
- **Recommendation:** **defer** (~30 min one-shot extraction script; not urgent)
- **Why:** Data is cached, just needs extraction pass. No Phase 1A impact (Phase 1A doesn't use Polygon fundamentals).

### INV-028: OHLCV missing `vwap` + `transactions`
- **Recommendation:** **defer** to Phase 1B+ (~6-8h re-prefetch)
- **Why:** Useful for slippage modeling and liquidity ranking; not Phase 1A blocker.

### INV-029: Polygon events filtered to ticker_change only
- **Recommendation:** **defer** to Phase 1B+ (~1h re-prefetch)
- **Why:** Event-driven strategies are Phase 1B+; Phase 1A doesn't use.

### INV-031: Quiver congressional missing District/State/Industry/Sector/Filing fields
- **Recommendation:** **defer** to Phase 1B refinement
- **Why:** Regional/industry sub-signals are Phase 1B+; baseline composite signal works.

### INV-032: Alpha Vantage news daily aggregation (per-article lost)
- **Recommendation:** **wontfix** OR **defer** pending owner-paid-tier decision
- **Why:** Polygon news (1.05M articles preserved with insights_json) supersedes. AV news at 25 files (INV-015) is already a smaller signal; aggregation loss less material than missing files.

### INV-033: STRING date columns across 8+ caches
- **Recommendation:** **defer** (~1h migration, engineering hygiene)
- **Why:** Functional — engine coerces at read time. No data loss, just typing inconsistency.

### INV-036: 13 Quiver endpoints don't exist at Trader tier
- **Recommendation:** **wontfix** (update API_AUDIT.md to mark as not-available; canonical-source verification done)
- **Why:** No real consumer crashes. Polluted gap-analysis docs; cleanup is the fix.

### INV-039: Polygon Benzinga 5/7 endpoints accessible (major P1 signal opportunity)
- **Recommendation:** **convert-to-DEC** for Phase 1B+ data source addition
- **Why:** Analyst insights / ratings / earnings / guidance / firm_details — high-value Phase 1B+ signal. ~2.5h aggregate full-universe fetch.

### INV-040: Quiver senate/house/spacs endpoints work — never fetched
- **Recommendation:** **convert-to-DEC** for Phase 1B+ data source addition (~2h prefetch)
- **Why:** Chamber-specific congressional signals + SPAC timeline for T2 universe. Phase 1B+ value.

---

## TIER 3 — Smaller cleanups + edge cases (8 items — recommend bundle as low-priority backlog)

### INV-005: Quiver bulk vs per-ticker endpoint variants
- **Recommendation:** **defer** (probe Quiver docs for richer per-ticker variants; ~2h research)

### INV-008: `get_etf_holdings` + `get_top_shareholders` no PIT dimension
- **Recommendation:** **defer** to Sprint 7+ (PIT snapshots require Quiver historical-snapshot subscription)

### INV-009: Sync small-test overwrite hazard (paginated-global scripts)
- **Recommendation:** **convert-to-DEC + add CHECKLIST item** (process / habit fix)
- **Why:** Already documented in body; codify via CHECKLIST #80 (proposed): "Smoke-test paginated-global scripts in isolated output dir, never against canonical path."

### INV-010: VVIX not on FRED (CBOE-only)
- **Recommendation:** **defer** — alternative path documented (CBOE direct or Polygon)
- **Why:** VVIX is one signal of many; VIX3M (working) covers same regime use case.

### INV-015: Alpha Vantage news 25 files
- **Recommendation:** **wontfix** (paid premium tier required; Polygon news covers)
- **Why:** Free tier 500 calls/day caps at ~4 days for full universe. Polygon news 1.05M articles with insights_json is superior coverage.

### INV-018: Polygon snapshot/market_status/reference_meta stub dirs
- **Recommendation:** **defer** to housekeeping sprint (bundle with INV-021/INV-022)
- **Why:** 2-3 files each; smoke-test artifacts. Delete OR document; either is fine.

### INV-042: FRED DEXJPUS deprecated (500 error)
- **Recommendation:** **defer** — Polygon Forex Basic USDJPY working
- **Why:** Alternative source covers; just doc cleanup.

### INV-044: SEC EDGAR per-form coverage capped at 1683 (CIK gap 254)
- **Recommendation:** **defer** to Phase 1B+ pre-flight (use SEC `company_tickers.json` master list)
- **Why:** Phase 1A baseline doesn't depend on SEC EDGAR per-form. Phase 1B+ filing overlay needs CIK expansion. ~1h to expand CIK map.

### INV-047: Quiver `etfholdings` dead-end
- **Recommendation:** **defer** to Phase 1B+ (accept static snapshot for now per CAV-077)
- **Why:** P2 signal; static snapshot acceptable for research. Owner-paid-tier decision (FMP/EOD/etfdb) deferred.

### INV-048: H22 date-typing residual (polygon ohlcv_daily / indicators / ALFRED realtime_*)
- **Recommendation:** **defer** to post-Phase-1A migration
- **Why:** Functionally transparent; engine coerces. ~5-10 min migration when scheduled.

---

## TIER 4 — Already-partial-resolution status (1 item — recommend close)

### INV-034: Polygon Indices Basic activated 2/13 (RESOLVED-PARTIAL)
- **Recommendation:** **mark RESOLVED-PARTIAL-FINAL** with note that remaining 11 indices require additional CBOE/S&P licensing fees
- **Why:** Empirical structural constraint. FRED VIXCLS/VXVCLS workaround documented. Owner has the data needed to decide if licensing fee is worth the 11 missing indices; defer that as a separate Phase 1B+ business decision.

---

## Summary counts (proposed disposition)

| Disposition | Count | INVs |
|---|---|---|
| **fix-now (before T0)** | 4 | INV-014, 050, 051, 052 |
| **convert-to-DEC + investigate at T0** | 1 | INV-053 |
| **convert-to-DEC (Phase 1B+ data sources)** | 4 | INV-024, 025, 039, 040 |
| **convert-to-DEC + add CHECKLIST item** | 1 | INV-009 |
| **defer** (proper backlog) | 16 | INV-005, 008, 010, 018, 019, 020, 021, 026, 028, 029, 031, 033, 042, 044, 047, 048 |
| **wontfix** | 4 | INV-015, 022, 032, 036 |
| **mark RESOLVED-PARTIAL-FINAL** | 1 | INV-034 |
| **TOTAL** | 31 | |

---

## Recommended sequence for tomorrow morning

1. **Approve TIER 1 fix-now items** (INV-014, 050, 051, 052) — these block clean T0 close-out. ~75 min implementation time (15+10+30+20) + pyramid each = ~3-4h aggregate. Could run while T1a procs still finishing.
2. **Convert-to-DEC items** (INV-024, 025, 039, 040, 053, 009) → batch into Pass 53 follow-on DECs (DEC-608 through DEC-613-ish range). Just log; build in Phase 1B+.
3. **Defer + wontfix batch** (20 items) → bulk-edit OPEN_INVESTIGATIONS.md status fields; no implementation needed.
4. **Mark INV-034 RESOLVED-PARTIAL-FINAL** — single edit.

**Effort estimate:** ~30 min for #2-4 (pure doc work), ~3-4h for #1 (real engine fixes).

---

## CHECKLIST compliance for this prep doc

- ✅ #45 — compliance via tomorrow's session, not this doc itself
- ✅ #67 — doc landing same-turn as prep work
- ✅ #69 — N/A (this is prep; no code changes)
- ✅ #74 — same-commit flag preserved
- ✅ #77 — canonical-source verification used (grep + actual file reads, not memory)
