# OPEN_INVESTIGATIONS.md — Canonical flag tracker

## 2026-05-15 Day 9+ Batches 172-178 status

Three new investigation findings from the prefetch sweep (no new INV-NNN slots — each closed within the session):
1. **Wikipedia REST per-IP throttle <1 req/0.5s** — captured as L153 (rate-limit lesson) + Batches 174/176/178 ratchet 0.5s → 3s → 5s; final coverage 99.9%. 2 stragglers still 429-blocked, retry on next refresh.
2. **Inventory truth-up gap (25 ACCESSIBLE_NOT_CACHED stale rows)** — captured as L154 (empirical-not-declarative lesson); all reconciled in Batches 172-175.
3. **Polygon grouped daily 403 NOT_AUTHORIZED on Starter** — inventory claimed ACCESSIBLE; reclassified TIER_BLOCKED in Batch 172. Not a real prefetch gap; per-ticker OHLCV aggregation (H1 DONE) covers the liquidity-ranking use case.

Open investigations from prior sessions (INV-001..047) remain in their existing slots below.

---

Investigation items flagged but not yet resolved. **Not bugs** (those go in `BUG_REGISTER.md`). **Not deferred specs** (those go in `AUDIT_BACKLOG.md`). This is for "we noticed something odd; not blocking; want to remember."

Format per entry:
- `INV-NNN` — short title
- **Discovered:** date + commit + how it was caught
- **Observation:** what we saw
- **Why not blocking:** why it doesn't stop Phase 1A
- **Status:** open / in-progress / resolved / wontfix
- **Next action / owner of decision** (optional)

---

## INV-001 — Trade-level regime=100% neutral in smoke v4 (Pass 53 Day-9 v8g)

- **Discovered:** 2026-05-07; smoke v4 cross-regime run (bg `b3giyk7i1`, commit `df3762fd`)
- **Observation:** 5-tkr × 4y (2020-2024) smoke produced 77 closed trades, **all with `regime_at_entry = "neutral"`**. Yet screener-day classification across the same window correctly showed all 4 regimes: bull 450 / neutral 772 / bear 46 / crisis 36 days.
- **Status:** ✅ **RESOLVED 2026-05-07 (Pass 53 Day-9 v8h P1.C5 investigation)**
- **Root cause:** Inspection of `output_smoke_v4_cross_regime/skipped_trades.csv` showed **3503 of 3921 skips with reason `level_6_halt_dd_-0.173` to `-0.243`** — the DEC-515 Level 6 portfolio drawdown circuit breaker firing. All 77 trades opened in **January 2022 only** (entry_date 2022-01-03 to 2022-01-31). Jan 2022 VIX was 17-28 / SPY mixed → neutral regime classification (correct per DEC-316 classifier rules: crisis ≥40, bear ≥30 + SPY-down, bull <20 + SPY-up, else neutral). After Jan 2022 the small 5-ticker portfolio drew down >15% (Level 6 trigger threshold), the halt activated, and the small portfolio could not recover above the 5% recovery threshold for the rest of the 4-year window.
- **NOT A BUG:** This is DEC-515 working correctly at tiny universe scale + a real early-2022 bear-market drawdown. The trade-level regime=100% neutral is a correct artifact of all-entries-in-Jan-2022 + Jan-2022-was-neutral.
- **Phase 1A implication:** At full 1937-tkr scale, portfolio drawdown calculation aggregates across orders of magnitude more positions; Level 6 trigger far less likely to fire from concentrated early-2022 losses; recovery far more likely. Pattern will not replicate.
- **Verification path:** When Phase 1A baseline runs at full scale, trade-level regime distribution should span all 4 regimes (bull/neutral/bear/crisis) in proportion to entry-day market state. If Phase 1A still shows 100% neutral, re-investigate.

---

## INV-002 — Polygon dividends + splits coverage = 2 files each (Pass 53 Day-9 v8g audit)

- **Discovered:** 2026-05-07; comprehensive prefetch audit
- **Observation:** `data_prefetch/polygon/legacy_archive_pass53/dividends/` and `splits/` each contain only **2 ticker files** (vs target 1937 in Master Universe). Far below other Polygon endpoint coverage (news 99%, financials 90%, events 87%).
- **Why not blocking:** No current strategy depends on dividend yield or split-adjusted historical data — engine reads adjusted closes from cache/ohlcv. But Phase 1B+ strategies that need dividend yield as a signal will hit empty data.
- **Status:** open — proposed re-prefetch (see PREFETCH_COVERAGE_AUDIT.md)
- **Next action:** owner approval to re-fetch via Polygon `/v3/reference/dividends` + `/v3/reference/splits` for full 1937-tkr universe.

---

## INV-003 — Quiver per-ticker prefetches at 26.3% coverage (509/1937)

- **Discovered:** 2026-05-07; comprehensive prefetch audit
- **Observation:** `data_prefetch/quiver/{congressional, gov_contracts, insider, institutional, lobbying, wallstreetbets, wikipedia}/` each have **509 ticker files** — exactly 26.3% of the 1937 Master Universe. Pattern strongly suggests these were prefetched at an earlier Sprint 0A stage when universe was 509 tickers, not re-run after universe grew to 1937.
- **Why not blocking:** S&P 500 + most major NASDAQ-100 names are likely included; smaller-cap T2/T3 names are missing. Phase 1A baseline using T1 (~600 tickers active) is well-covered. Phase 1B+ T2/T3 strategy testing will see incomplete data.
- **Status:** open — proposed re-prefetch
- **Next action:** owner approval to re-prefetch at 1937-tkr scope.

---

## INV-004 — Polygon reference prefetch at 30.9% coverage (599/1937)

- **Discovered:** 2026-05-07; comprehensive prefetch audit
- **Observation:** Only 599 ticker reference files in `legacy_archive_pass53/reference/`. Used by `fetcher.fetch_info()` for sector/cap/IPO/exchange. After the G4 path fix (Day-9 v8b), ~30% of universe gets real data; ~70% fall back to `sector="Unknown" market_cap=0`.
- **Why not blocking:** Universe sector data canonically comes from B++ schema CSVs (T1a, T1c, ETFs, T2, T3) which include Sector. fetcher.fetch_info is a secondary source. But market_cap=0 for ~70% of universe is a real gap if any strategy filters by cap.
- **Status:** open — proposed re-prefetch
- **Next action:** owner approval to re-prefetch reference for full 1937-tkr universe.

---

## INV-005 — Several Quiver datasets prefetched as 1 global file only

- **Discovered:** 2026-05-07; comprehensive prefetch audit
- **Observation:** `corporatedonors`, `patentmomentum`, `quivernews`, `sec13f` (full holdings), `insiders` (bulk), `sec13fchanges` (bulk) are each stored as 1 global file. For some this is correct (insiders bulk is the canonical source); for others it might miss per-ticker coverage Quiver may offer (`patentmomentum` per-ticker history, `corporatedonors` per-ticker political donor map).
- **Why not blocking:** Bulk files contain all data; per-ticker access is just a performance/UX concern. `get_corporate_donations()` filters by ticker at read time which works.
- **Status:** open — investigate whether Quiver offers per-ticker endpoints with richer detail than bulk slice.
- **Next action:** check Quiver API docs for per-ticker variants of these endpoints.

---

## INV-006 — Quiver wikipedia mirror is empty (sampled 100/100 files empty)

- **Discovered:** 2026-05-07; L146 audit (Day-9 v8b)
- **Observation:** `data_prefetch/quiver/wikipedia/` has 509 files but all empty (verified 100/100 sampled). The separate `data_prefetch/wikipedia/` (1414 files, populated) is the canonical Wikipedia pageviews source used by `sentiment.get_wikipedia_pageviews`.
- **Why not blocking:** Canonical separate source is functional; Quiver mirror is redundant + broken.
- **Status:** open — defer cleanup
- **Next action:** delete `data_prefetch/quiver/wikipedia/` directory OR re-prefetch correctly. Owner decision.

---

## INV-007 — Quiver institutional per-ticker ~18% empty (incl. AAPL)

- **Discovered:** 2026-05-07; DEC-512 audit Day-9 v8f
- **Observation:** `data_prefetch/quiver/institutional/` has 509 ticker files but ~18% sampled empty. AAPL specifically is empty. Bulk `sec13fchanges` works correctly.
- **Why not blocking:** `institutional_signal()` reads bulk path (sec13fchanges); per-ticker dir is unused for trade decisions.
- **Status:** open — defer cleanup
- **Next action:** investigate why per-ticker prefetch failed for these tickers; either re-run or remove.

---

## INV-008 — `get_etf_holdings` + `get_top_shareholders` source data has no PIT dimension

- **Discovered:** 2026-05-07; PIT audit Day-9 v8g Batch 7
- **Observation:** Source parquets for these accessors have no `Date` column. Files are CURRENT snapshots only. Using these in a backtest at past as_of leaks future ownership/ETF inclusion changes.
- **Why not blocking:** Documented in docstrings as no-PIT-dimension; recommended substitute (`institutional_signal()` via sec13fchanges) is PIT-correct and works.
- **Status:** open — defer to Sprint 7+
- **Next action:** when re-prefetching, request Quiver historical snapshots (one per quarter or month) so a Date dimension can be added.

---

## INV-009 — Sync small-test of paginated-global scripts can overwrite background-job output

- **Discovered:** 2026-05-07 (Pass 53 Day-9 v8h prefetch session)
- **Observation:** I ran `python scripts/prefetch_polygon_corp_actions.py --tickers AAPL` to smoke-test the script while it was already running in the background as job `bswwwh1w5` (no --tickers, doing global pagination). The script writes to a SINGLE shared file `data_prefetch/polygon/dividends/all_dividends.parquet` rather than appending. The single-AAPL test (20 rows) overwrote the global pull's output. Re-launched as `b4jd6ij18` to recover.
- **Why not blocking:** Splits file (`all_splits.parquet`) was unaffected (smoke test was dividends-only); re-run recovered the dividend data.
- **Status:** open — process / habit fix
- **Next action:**
  - When verifying a script, prefer scripts that write per-ticker (so parallel writes don't conflict) OR run smoke test on a non-conflicting output dir
  - Add a flag to scripts that write singletons (e.g. `--out-suffix _smoketest`) to redirect output during testing
  - Update CHECKLIST.md #13/#22 to explicitly call out shared-file scripts as a parallelism trap

---

## INV-010 — VVIX not on FRED (CBOE-only series)

- **Discovered:** 2026-05-07 (Pass 53 Day-9 v8h Tier C2 FRED prefetch)
- **Observation:** Tried to fetch VVIX (vol of VIX) from FRED — series ID `VVIXCLS` returns 400 Bad Request. CBOE provides VVIX directly but doesn't release it to FRED.
- **Why not blocking:** DEC-513 #7 spec calls for VIX3M + VVIX, but VIX3M (VXVCLS) was successfully fetched. VVIX is one signal of many.
- **Status:** open — defer
- **Next action:** if VVIX needed, fetch from CBOE direct (https://www.cboe.com/us/options/market_statistics/historical_data/) or via Polygon if they expose ^VVIX as a ticker. Add to data_prefetch/cboe/ if needed.

---

## INV-012 — Most Tier B5-B10 Quiver endpoints don't exist in public API

- **Discovered:** 2026-05-07 (Pass 53 Day-9 v8h endpoint discovery)
- **Observation:** Direct API probing of Quiver Trader endpoints I had assumed existed:
  - 404: `historical/iposcalendar`, `historical/spacs`, `historical/optionsflow/{ticker}`, `historical/earningsbeats/{ticker}`, `historical/dividends/{ticker}`, `historical/splits/{ticker}`
  - 200 but 0 records: `historical/twitter/AAPL`
  - 200 with sparse current data: `live/spacs` (2 records), `live/twitter` (1 record)
- **Why not blocking:** These were aspirational endpoints from PREFETCH_COVERAGE_AUDIT.md Tier B5-B10. Their absence means we proceed with current Quiver coverage (16 datasets prefetched). Equivalent signals available from other sources:
  - Dividends/splits: Polygon (already prefetched)
  - Twitter sentiment: skip (Quiver feed empty); could build via X API direct in Phase 1B+ if needed
  - Options flow: would require Polygon Options subscription (Stocks Starter doesn't include)
  - IPO calendar: Polygon `/v3/reference/tickers` filtered by list_date in last 90d (derivable from existing ref prefetch)
- **Status:** resolved — endpoints unavailable; PREFETCH_COVERAGE_AUDIT.md Tier B5-B10 marked as "not available" rather than queued
- **Next action:** update PREFETCH_COVERAGE_AUDIT.md with this discovery + remove Tier B5-B10 from active queue

---

## INV-011 — CFTC Treasury contract names different in TFF dataset

**Status update 2026-05-07 evening:** RESOLVED via commit `c236105c`. Real
contract names: `UST 10Y NOTE` / `UST 5Y NOTE` / `UST 2Y NOTE` / `UST BOND`
/ `ULTRA UST BOND` / `DJIA x $5`. CFTC coverage now 19/20.

---

## INV-013 — Quiver wikipedia checkpoint/data mismatch (Pass 53 Day-9 v8h)

- **Discovered:** 2026-05-07 evening; Quiver BG status check
- **Observation:**
  - Earlier this session (Tier E1, commit `8f45fe33`): I DELETED `data_prefetch/quiver/wikipedia/` because all 509 files were empty (resolving INV-006).
  - The Quiver checkpoint at `data_prefetch/quiver/_checkpoint.json` still lists 509 tickers as "done" for wikipedia endpoint.
  - The currently-running BG `bsu432hbt` will hit the wikipedia endpoint last (sequential by endpoint) and will **skip these 509 tickers** thinking they're complete — but no data files exist on disk.
  - Result: wikipedia endpoint coverage = 0 files / 1937 target unless intervened.
- **Why not blocking:** Phase 1A baseline doesn't depend on Quiver wikipedia (separate `data_prefetch/wikipedia/` is the canonical source, populated 1414 files via different prefetch). Quiver wikipedia mirror was redundant before being empty.
- **Status:** open
- **Next action:**
  - Wait for current BG (`bsu432hbt`) to complete (~4 hours)
  - After completion: edit checkpoint to remove all wikipedia entries
  - Re-run Quiver script with checkpoint cleared for wikipedia → fetch all 1937
  - OR: leave as-is permanently (separate data_prefetch/wikipedia/ is the canonical source for engine consumers via `sentiment.get_wikipedia_pageviews`)
  - **Recommendation: leave as-is.** No engine consumer reads from `data_prefetch/quiver/wikipedia/` (verified L146 audit Day-9 v8b INV-006); the canonical source is `data_prefetch/wikipedia/` (1414 files, populated). Re-fetching the redundant Quiver mirror has no value.

- **Discovered:** 2026-05-07 (Pass 53 Day-9 v8h Tier C3 CFTC prefetch)
- **Observation:** Tried to fetch CFTC TFF positioning for "10-YEAR U.S. TREASURY NOTES" / "5-YEAR" / "2-YEAR" / "ULTRA U.S. TREASURY BONDS" / "E-MINI DJIA (X $5)" — all returned 0 rows. Other contracts (e-mini SP500, NDX, RUT, VIX, fed funds, currencies, commodities) all worked fine.
- **Why not blocking:** 13/18 contracts fetched successfully. Treasury futures positioning is nice-to-have for rate-driven strategies; we have rate level/spread data from FRED (DGS10/DGS5/DGS2/T10Y2Y).
- **Status:** RESOLVED — INV-011 fix landed in `18e93c00` with corrected names.
- **Next action:** none — superseded by INV-011 resolution.

---

## INV-014 — DEC-491 trade_log.parquet write silently degrades to CSV-only (Pass 53 Day-9 v8h)

- **Discovered:** 2026-05-07 evening; Phase 1A dry-run output (BG `bo1zvd4xk`)
- **Observation:** Engine logs `WARNING: trade_log.parquet write failed (Cannot write struct type 'agent_reasoning' with no child field to Parquet. Consider adding a dummy child field.); CSV only`. The `agent_reasoning` column is an empty struct (no child fields) when `run_agents=False`, which pyarrow rejects. DEC-491 architecture intent is Parquet PRIMARY + CSV serialized; runtime is silently degrading to CSV-only.
- **Why not blocking:** CSV fallback works; engine continues; trade-log content is preserved. DEC-491 was about resilience — the fallback IS the resilience working. But the architectural goal of Parquet-as-primary is degraded for any agents-disabled run (which is Phase 1A baseline, dry-run, and the Phase 1A no-agents path per `--no-agents` flag).
- **Severity:** medium. Phase 1A `--no-agents` runs (the most common pre-Phase-1B configuration) will skip the Parquet write every time. Downstream Parquet consumers (anyone reading `trade_log.parquet` directly per DEC-491) will silently miss data.
- **Status:** open
- **Next action:**
  - Fix in `backtest/results/writer.py` DEC-491 block: when serializing object columns with empty dicts/lists, replace `{}` with `None` (or `{"_": None}` if pyarrow needs a child) before to_parquet
  - Add data-integrity test asserting `trade_log.parquet` is written (not just `trade_log.csv`) for `--no-agents` runs
  - Or simpler: drop the `agent_reasoning` column entirely from the Parquet write when it's a uniform-empty-struct (preserve in CSV)
- **Joint:** DEC-491 (the rule that motivated parquet-primary); CHECKLIST #74 (this INV entry honoring same-commit flag rule); the dry-run was the (b) functional-verification step that caught this — example of CHECKLIST #76's column-(b) catching a bug an inventory-only audit would miss.

---

## INV-015 — Alpha Vantage news cached only 25 files (alphabetical mid-letter range) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; comprehensive prefetch deep-dive audit per owner directive
- **Observation:** `backtest/data/cache/av_news/` has only 25 files spanning alphabetical range C..D + X (CCI, CMI, COST, CRWD, CSGP, CSX, CTRA, CVS, D, DAL, DAY, DE, DFS, DG, DHI, DHR, DLR, DLTR, DPZ, DRI, DVA, DVN, DXCM, FANG, XRAY). Looks like a partial-batch run that died after the C..D letter range, with one orphan X (FANG/XRAY may have been from a different batch). The script `scripts/prefetch_alphavantage_news.py` is configured for 4 batches × 127 tickers each = 508 total but only 25 landed.
- **Why not blocking:** Phase 1A baseline doesn't depend on AV news (sentiment overlay is Phase 1B+). Currently active news source for any consumer: Polygon news (1926/1937, 99.4%).
- **Severity:** HIGH for owner's "broad everything" directive — major under-coverage of an API we have a key for.
- **Status:** open
- **Next action:**
  - Verify AlphaVantage API key still works (smoke fetch one ticker)
  - Check checkpoint file for last-completed ticker
  - Re-launch prefetch for full 1937 Master Universe (~10-15h on free tier 25 calls/min, 500/day = need premium tier OR multi-day run)
  - Confirm subscription tier with owner before launching (free tier = 500 calls/day caps full universe at ~4 days; premium tier removes this)
- **Joint:** owner directive 2026-05-07 ("download broad everything"); INV-016 (Finnhub same pattern); CHECKLIST #76 (column-(b) verification surfaced this — paper-only audit would have just reported "AV news cached" without count check).

---

## INV-016 — RESOLVED 2026-05-09 v8h+1 — Finnhub news Master Universe expansion complete (Pass 53)

- **Discovered:** 2026-05-07 evening; comprehensive prefetch deep-dive audit
- **Observation:** `backtest/data/cache/finnhub_news/` has exactly 509 files. The script `scripts/prefetch_finnhub_news.py` line ~31 reads `from backtest.data.universe import get_sp500_constituents, ETFS_FULL` and uses S&P 500 + ETFs only. Same pattern as old Quiver per-ticker (which is now being fixed by `bsu432hbt` BG). Needs the same Master-Universe-expansion treatment.
- **Why not blocking:** Free-tier Finnhub returns near-empty for older dates; current cache is ~2025-Mar 2026 only. Phase 1A baseline doesn't depend on Finnhub news (Polygon news is primary). Phase 1B+ news-sentiment strategies could benefit from cross-source.
- **Severity:** HIGH for owner's "broad everything" — known stale prefetch script + stale universe scope.
- **Status:** RESOLVED 2026-05-09 v8h+1.
- **Resolution evidence:**
  - `scripts/prefetch_finnhub_news.py` patched (commit `7a175f7c2`) to read Master Universe Deduplicated CSV (1937 tickers); falls back to legacy scope if CSV absent.
  - `_load_env()` helper added (commit `302779f4e`) so BG runners load `.env` automatically.
  - `git_commit()` tightened to path-restricted (INV-041 fix carried forward).
  - BG `blk7obzpy` completed: cache now has **1941 ticker files** (was 509 = ~3.8× expansion). Spot check: TSLA 16 rows, AAPL 0 rows (free-tier API returns near-empty for tickers without recent news, expected).
  - Free-tier Finnhub note: minimal historical lookback per ticker; paid Basic tier (~$30/mo) needed for >1y range. Within the free-tier window, full Master Universe is now covered.
- **Joint:** INV-015 (Alpha Vantage same pattern - still SURFACED; needs premium); CHECKLIST #76 (column-(b) verification surfaced this); CHECKLIST #78 (per-addressal pyramid run for this RESOLVED transition).

---

## INV-017 — RESOLVED 2026-05-08 — Polygon dividends/splits/IPOs prefetched at full historical universe (Pass 53 Day-9 v8h+1)

- **Status:** RESOLVED 2026-05-08; `scripts/prefetch_polygon_corp_actions_full.py` paginated all available history.
- **Result:**
  - Dividends: 100,000 records across 10,984 tickers (paginated; may have hit max_pages=100 cap; data covers our 1937 universe + much more)
  - Splits: 27,590 records across 18,909 tickers
  - IPOs: 6,264 records
- **Output:** `data_prefetch/polygon/{dividends_full,splits_full,ipos_full}/` with per-ticker shards + global `all.parquet`
- **Joint:** Tier H3 (P1) — DONE; original INV below preserved as historical reference.

---

## INV-017-original — Polygon dividends/splits canonical paths each have 1 file (vs 1500+ tickers actually pay/split) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; comprehensive prefetch deep-dive audit
- **Observation:** `data_prefetch/polygon/dividends/` = 1 file. `data_prefetch/polygon/splits/` = 1 file. `legacy_archive_pass53/dividends/` = 2 files, `legacy_archive_pass53/splits/` = 2 files. Master Universe = 1937 tickers; estimate 1500+ pay dividends and 50-100+ split per year. The `scripts/prefetch_polygon_corp_actions.py` exists but apparently never completed at universe scope.
- **Why not blocking:** Phase 1A doesn't trade dividend strategies (60-strategy baseline is technical-only). Phase 1B+ dividend-yield strategies blocked.
- **Severity:** HIGH for Phase 1B; informational for Phase 1A.
- **Status:** open
- **Next action:**
  - Re-launch `scripts/prefetch_polygon_corp_actions.py` at full Master Universe scope
  - Verify it writes to canonical `data_prefetch/polygon/dividends/` + `data_prefetch/polygon/splits/`
  - ~2-3h wall clock per the audit estimate
- **Joint:** PREFETCH_COVERAGE_AUDIT.md row "Polygon dividends/splits"; CHECKLIST #76 (column-b verification confirmed at-most-1-file per dir).

---

## INV-018 — Polygon snapshot/market_status/reference_meta stub dirs (2-3 files each — likely smoke-test artifacts) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; comprehensive prefetch deep-dive audit
- **Observation:** `data_prefetch/polygon/snapshot/` = 2 files. `data_prefetch/polygon/market_status/` = 2 files. `data_prefetch/polygon/reference_meta/` = 3 files. These dirs exist (created by some test scaffold or G6/G16 wiring) but are not actually populated as part of any canonical prefetch flow. Either: (a) leftover from smoke-test runs, or (b) failed-launch attempts of new prefetch scripts.
- **Why not blocking:** Real-time-only endpoints (snapshot, market status) cannot be prefetched historically. Reference_meta is a low-priority static dataset.
- **Severity:** LOW (housekeeping).
- **Status:** open
- **Next action:**
  - Inspect file contents to determine origin
  - If smoke-test artifacts: delete dirs OR document as "test-output-staging" in canonical doc
  - If real data: identify the populating mechanism + add to canonical script set
  - Decide on going-forward strategy: daily-snapshot capture going forward (cron job) OR explicit decision-not-to-cache
- **Joint:** CHECKLIST #76 column-(b) — paper audit would have reported "snapshot dir exists" without verifying file count; running ls revealed the stub state.

---

## INV-019 — ALFRED 7-series gap behind FRED (recent Tier C additions did not propagate to vintage cache) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; FRED↔ALFRED filesystem diff
- **Observation:** Diff shows ALFRED missing 7 series that FRED has: DCOILWTICO, DTWEXBGS, INDPRO, RSAFS, TB3SMFFM, VIXCLS, VXVCLS. These are exactly the Tier C additions made in this Pass 53 session via `prefetch_macro.py` extension — they were added to FRED prefetch but the equivalent ALFRED prefetch script (which mirrors FRED with vintage realtime_start parameter) was not updated.
- **Why not blocking:** ALFRED vintages are needed only for revision-aware strategies (Phase 1C+). Phase 1A baseline reads FRED current series.
- **Severity:** MEDIUM (Phase 1C blocker; non-blocking for Phase 1A/1B).
- **Status:** open
- **Next action:**
  - Locate canonical ALFRED prefetch script (NOT in `scripts/` per current inventory — orphan-script issue per INV-021)
  - Mirror the 7 new FRED series into ALFRED with `realtime_start` + `realtime_end` parameters
  - ~5 min wall clock
- **Joint:** INV-021 (orphan prefetch scripts); INV-020 (canonical-source rule violated for FRED prefetch script).

---

## INV-020 — `prefetch_macro.py` SERIES dict (21 entries) ≠ actual cache (57 series) — script doc out-of-sync with state (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; read of `scripts/prefetch_macro.py` + filesystem walk
- **Observation:** `scripts/prefetch_macro.py` SERIES dict has 21 entries (yield_curve, fed_funds, unemployment, cpi, ..., gold_price). Actual `data_prefetch/fred/observations/` has 57 parquet files. The 36-series gap (e.g. AAA, BAMLC0A0CM, DGS1, GDP, PAYEMS, MORTGAGE30US, NFCI, STLFSI4, etc.) was populated by **some other mechanism not visible in the canonical prefetch script** — could be older script versions deleted from `scripts/`, an inline GH Actions workflow doing extra fetches, manual one-off runs, or notebook-driven prefetch.
- **Why not blocking:** Series ARE cached and consumable. The issue is **canonical-source-of-truth violation** (CHECKLIST #76 / DEC-456-style integrity rule): the prefetch script is supposed to be the documented source of what's prefetched. When the script disagrees with the cache, refresh / re-prefetch / debugging cycles will follow the wrong canonical source.
- **Severity:** MEDIUM (process / operational risk).
- **Status:** open
- **Next action:**
  - Update `scripts/prefetch_macro.py` SERIES dict to enumerate ALL 57 cached series + the additional 25-30 recommended in the deep-dive audit
  - Add a self-check in `main()`: after fetching, scan `data_prefetch/fred/observations/` for series NOT in SERIES dict and warn (catches manual additions going forward)
  - Add a regression test: `test_prefetch_macro_series_dict_matches_cache` — verifies SERIES.values() superset of cached parquet stems
- **Joint:** INV-021 (orphan scripts — same root); CHECKLIST #76 (canonical-source verification was the column-(b) probe that surfaced this); DEC-456 (data integrity rule).

---

## INV-021 — Orphan cache directories without canonical prefetch scripts (AAII / CNN F&G / FRED-extras / ALFRED / pytrends / Wikipedia) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; `scripts/prefetch_*.py` ↔ `data_prefetch/*/` cross-inventory
- **Observation:** Multiple cache directories in `data_prefetch/` are populated but have NO matching prefetch script in `scripts/` AND NO matching workflow in `.github/workflows/`:
  - `data_prefetch/aaii/weekly_sentiment.parquet` — no `prefetch_aaii.py`
  - `data_prefetch/cnn_fg/daily.parquet` + 7 components — no `prefetch_cnn_fg.py`
  - `data_prefetch/alfred/` 50 series — no `prefetch_alfred.py`
  - `data_prefetch/pytrends/` 1417 files — no `prefetch_pytrends.py`
  - `data_prefetch/wikipedia/` 1414 files — no `prefetch_wikipedia.py`
  - `data_prefetch/cftc/` 19 contracts — has script `prefetch_cftc_cot.py` (resolved this case)
  - 36 of 57 FRED series — `prefetch_macro.py` only enumerates 21 (INV-020)
- **Why not blocking:** Caches are populated and consumable. The data is there.
- **Severity:** MEDIUM (operational debt — when refresh is needed, no canonical entry-point exists; team-knowledge dependency).
- **Status:** open
- **Next action:**
  - Author canonical prefetch scripts for each orphan source (5 scripts: aaii, cnn_fg, alfred, pytrends, wikipedia)
  - Each script reads existing cache → extracts series/ticker list → re-fetches at canonical schema → writes canonical path
  - Add to `.github/workflows/` for periodic refresh
  - Pyramid + smoke per CHECKLIST #75 strict
  - Estimated ~6-8h aggregate
- **Joint:** INV-020 (FRED variant); INV-019 (ALFRED variant — extension of this); CHECKLIST #44 (data-consumption audit must include runtime probe — same root pattern).

---

## INV-022 — Legacy `backtest/data/cache/quiver/` directory empty but not deleted (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; legacy cache walk
- **Observation:** `backtest/data/cache/quiver/` = 0 files. The Quiver migration to `data_prefetch/quiver/` (Sprint 0A canonical path per L146) deleted contents but left the parent directory. Empty dir is harmless but signals incomplete migration cleanup.
- **Why not blocking:** Trivial.
- **Severity:** LOW (housekeeping).
- **Status:** open
- **Next action:** delete the empty directory + add `.gitignore` entry to ensure it doesn't reappear; OR document explicitly in canonical doc that it's a deprecated path.
- **Joint:** L146 wiring matrix (Quiver migration); INV-020/021 (canonical-source-of-truth pattern).

---

## INV-023 — RESOLVED 2026-05-08 v8h+1 — Quiver BG Unicode emoji bug fixed; all 7 endpoints completed (Pass 53)

- **Discovered:** 2026-05-07 evening; Quiver BG failed with exit code 1 at end of congressional fetch
- **Observation:** `scripts/prefetch_quiver.py` had MULTIPLE Unicode chars in print statements: `✓` (✓ at line 197 — fixed earlier in `33b93fec`), `✅` (✅ line 231), `⚠` (⚠ lines 234, 243), `❌` (❌ line 237), `—` em-dash (lines 182, 208, 209, 212, 217). Earlier fix at line 197 was incomplete — line 231 ✅ crash was the FATAL exit. The em-dash and other emoji fired as `UnicodeEncodeError` in Windows cp1252 console; the inner-loop em-dash crashes were caught by the outer `except Exception` and logged as "ERROR on TICKER" (misleading — the data was actually saved before the print crash).
- **Why not blocking long-term:** Data integrity intact. `save_ticker_data()` runs BEFORE the failing print, so data files were saved + checkpoints updated for every ticker. Verification: 1941 congressional parquet files vs 1921 checkpoint entries — files >= checkpoint, all good. The "ERROR on TICKER" log lines were save-then-print-crash events; data WAS persisted.
- **Severity:** HIGH at the moment — Phase 1A blockers re-emerged. After the BG died, only 1 of 7 endpoints actually progressed (congressional 1921/1937). The 6 remaining (insider/institutional/gov_contracts/lobbying/wallstreetbets/wikipedia) are STILL at 509 baseline. INV-003 (Quiver re-prefetch) re-opens.
- **Status:** RESOLVED 2026-05-08 v8h+1.
- **Resolution evidence:**
  - All 7 Quiver endpoints fully cached: congressional 1941, gov_contracts 1941, insider 1941, institutional 1941, lobbying 1941, wallstreetbets 1941, plus housetrading/senatetrading/spacs/topshareholders/twitter all at 1937.
  - `test_prefetch_scripts_no_unicode.py` now enforces ASCII-only runtime strings across all prefetch scripts (T0 regression gate).
  - StockTwits prefetch (added Pass 53 v8h+1) caught at hook layer because it had a `≈` Unicode char; fixed before commit.
- **Joint:** P1.runner regression (commit `8d2641edf`); L150 (pyramid dimension-coverage gap); CHECKLIST #74/#75; INV-013 (wikipedia ghost — same BG); INV-003 (Quiver re-prefetch closed).

---

## INV-024 — Quiver gov_contracts field set REFRAMED — gap at API level not our prefetch (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-07 evening (initial); REFRAMED 2026-05-08 morning after probe via `probe_api_catalog.py`
- **Observation (REVISED):** `data_prefetch/quiver/gov_contracts/AAPL.parquet` contains 4 columns: `Ticker, Amount (STRING), Qtr (int), Year (int)`. **The Quiver `/historical/govcontracts/{ticker}` API itself returns ONLY these 4 fields** (probe-confirmed 2026-05-08). My initial INV-024 hypothesis (that the API returns DateSigned / AwardingAgency / DepartmentDescription / ContractDescription and our prefetch was filtering them out) was WRONG — that hypothesis came from training-data memory, not API docs.
- **Status:** REFRAMED.
- **Why:** Daily-granularity government contracts + agency + description requires a different source. Options:
  1. **USAspending.gov direct** (free, public) — `api.usaspending.gov/api/v2/award/...` provides daily contract-level data with full fields
  2. **SEC EDGAR 8-K material events** — companies disclose major contract wins; structured via XBRL when material
  3. **Polygon Benzinga news** — analyst-quality contract-win coverage
- **Action:**
  - Add USAspending.gov to API inventory + probe its endpoints
  - This is no longer a prefetch fix; it's a NEW source addition
- **Joint:** **CHECKLIST #77** (this is the canonical example of memory-based catalog hypothesis being wrong); INV-035 (sister: many Quiver endpoints I assumed exist actually don't at our tier).
- **Why blocking:** Quarterly aggregates (`Qtr+Year`) cannot do PIT cutoff at daily resolution — strategies like "buy on gov-contract win within last 5 days" cannot be implemented. Lost AwardingAgency means "DOD-contract premium" strategies impossible. Lost Amount-as-numeric means aggregation requires runtime str→numeric coercion.
- **Severity:** CRITICAL for any strategy using gov_contracts as a signal. Phase 1A baseline doesn't directly use, but smart_money composite (Phase 1A baseline) calls `get_gov_contracts_signal()` which returns a signal derived from this data.
- **Status:** open
- **Next action:**
  - Read Quiver API response schema for `/historical/govcontracts/{ticker}` (probe one ticker, compare to docs)
  - Edit `prefetch_quiver.py` `save_ticker_data()` and the gov_contracts-specific path to preserve all returned fields
  - Fix Amount type to numeric
  - Re-prefetch all 1937 (~1-2h)
  - This is in addition to current BG `b3xny7m35` which is finishing the OLD 4-field schema — owner approval needed before second BG
- **Joint:** owner directive 2026-05-07 evening (the "time column missing" example); CHECKLIST #76 column-(b) probe surfaced this; INV-014 (DEC-491 sister field-loss pattern); BG `b3xny7m35` (currently re-prefetching with INSUFFICIENT field set — will need re-do).

---

## INV-025 — SEC EDGAR all 11 forms cached as filing-metadata-only (primary_doc not parsed; lost transaction-level fields) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** All 11 SEC EDGAR per-form parquets have schema `[ticker, cik, form, filing_date, accession_number, primary_doc]` — only filing metadata. The `primary_doc` is a URL to the actual filing XML/HTML. Without parsing that doc, we have no Form 4 transaction details (shares/price/officer/director-flag), no 8-K item numbers (1.01 acquisition / 2.02 results / 5.02 officer change / 8.01 other), no SC 13D holder positions, no 10-K/Q line items.
- **Why blocking:** "Filing-event-happened" signals work (e.g. 8-K within last 5 days = catalyst), but actionable signals like "insider bought >$1M of stock" or "13D activist with 10%+ stake" require the structured content. Phase 1B-π (insider/activist overlays) blocked.
- **Severity:** HIGH for Phase 1B; informational for Phase 1A (baseline doesn't parse 8-K item details).
- **Status:** open
- **Next action:**
  - Two paths:
    1. Parse `primary_doc` XML/HTML for each filing (~1700 tickers × 11 forms × N filings) — expensive
    2. Use SEC EDGAR full-text-search + structured XBRL feeds — faster
  - Recommended path 2; estimate 20-30h infrastructure build + initial fetch
- **Joint:** PREFETCH_COVERAGE_AUDIT field-level matrix; CHECKLIST #76; INV-014/INV-024 (sister field-loss pattern).

---

## INV-026 — Polygon financials cached as JSON-string (line items not extracted) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** `data_prefetch/polygon/financials/AAPL.parquet` schema has `financials_json` column as a STRING. The Polygon `/vX/reference/financials` API returns income statement / balance sheet / cash flow as nested structured data. We're storing the JSON dump as a string — must `json.loads()` at read time AND walk the nested schema to extract revenue/EPS/FCF/etc.
- **Why blocking:** Cannot do `df.query("revenue > 1e10")`-style filtering. Every consumer must json-parse + nested-key-extract. Significant runtime cost + brittle.
- **Severity:** MEDIUM (data IS there, just inefficient access).
- **Status:** open
- **Next action:**
  - Local processing — no new API calls. Walk all 1746 financials parquets, json-parse, extract key line items into separate columns (revenue, gross_profit, operating_income, net_income, eps_basic, eps_diluted, total_assets, total_liabilities, stockholders_equity, cash_from_operations, capex, free_cash_flow), preserve the raw JSON for audit
  - ~30 min processing + write back
- **Joint:** PREFETCH_COVERAGE_AUDIT field-level matrix; sister to INV-025 for SEC EDGAR.

---

## INV-027 — RESOLVED 2026-05-08 v8h+1 — Polygon news per-ticker `insights` array preserved (Pass 53)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** Polygon `/v2/reference/news` returns each article with an `insights` array containing per-ticker {ticker, sentiment, sentiment_reasoning} entries. For multi-ticker articles (e.g. "AAPL beats but MSFT disappoints"), the per-ticker sentiments differ. Our cached schema has only article-level `sentiment` + `sentiment_reasoning` — for multi-ticker articles, we lose the per-ticker breakdown.
- **Why blocking:** Reduces signal precision for sentiment overlays. Multi-ticker articles common (sector pieces, earnings season, M&A coverage).
- **Severity:** HIGH for sentiment-overlay strategies; informational for Phase 1A.
- **Status:** RESOLVED 2026-05-08 v8h+1.
- **Resolution evidence:**
  - `prefetch_polygon_news.py` updated to preserve `insights[]` as JSON-encoded `insights_json` column (commit `7a175f7c2`).
  - Checkpoint reset; full backfill re-prefetch completed in 47 min (1924 / 1937 tickers; 449 MB total cache).
  - Per-AAPL spot check: 21,626 articles with 3,557 (16.4%) populating `insights_json` — matches expected rate of multi-ticker articles.
  - Contract test `test_contract_polygon_news_shape` (in `test_contract.py`) now asserts `insights_json` column presence.
- **Joint:** PREFETCH_COVERAGE_AUDIT field-level matrix; sister to INV-024 (Quiver gov_contracts field loss).

---

## INV-028 — OHLCV cache missing `vwap` + `transactions` count from Polygon aggregates (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** `backtest/data/cache/ohlcv/AAPL.parquet` has 6 columns: date, open, high, low, close, volume. Polygon `/v2/aggs/ticker/{t}/range/1/day/{from}/{to}` response returns: `t, o, h, l, c, v, vw (vwap), n (transactions count)`. We're losing 2 fields per bar.
- **Why blocking:** VWAP useful for execution-cost modeling (slippage benchmark). Transactions count proxies liquidity — useful for ranking liquidity-adjusted strategies (DEC-321 tier 3 liquidity floor uses ADV but transactions/day is more granular).
- **Severity:** MEDIUM (data not lost; just need to re-prefetch with new fields).
- **Status:** open
- **Next action:**
  - Edit `prefetch_polygon_ohlcv_daily.py` to capture `vw` + `n` fields
  - Re-prefetch (1937 × 6 years = ~6-8h)
- **Joint:** field-level matrix; CHECKLIST #76 column-(b) probe surfaced this.

---

## INV-029 — Polygon events captures only ticker_change (lost splits/dividends/delisting/merger event types) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** `data_prefetch/polygon/events/AAPL.parquet` contains 1 row with `event_type=ticker_change`. Polygon `/v3/reference/tickers/{t}/events` accepts `?types=` query parameter and returns event types: `ticker_change, splits, dividends, delisting, name_change, merger`. Current prefetch is filtering to ticker_change only.
- **Why blocking:** Event-driven signals (post-split price-action, dividend-ex-day strategies, M&A arbitrage) blocked.
- **Severity:** MEDIUM for Phase 1B+; non-blocking for Phase 1A.
- **Status:** open
- **Next action:**
  - Verify Polygon API param syntax (probe 1 ticker w/ `?types=ticker_change,splits,dividends,delisting,name_change,merger`)
  - Edit `prefetch_polygon_corp_actions.py` or `events` script to fetch all types
  - Re-prefetch (~1h, fast endpoint)
- **Joint:** field-level matrix.

---

## INV-030 — RESOLVED 2026-05-08 — Polygon reference extended fields prefetched (Pass 53 Day-9 v8h+1)

- **Status:** RESOLVED 2026-05-08; `scripts/prefetch_polygon_reference_extended.py` re-fetched 1937 tickers with all extended fields.
- **Result:** 1686/1937 OK (251 failed = delisted, expected). Field population:
  - total_employees: 1641 (97.3%)
  - composite_figi: 1515 (89.9%)
  - description: 1658 (98.4%)
  - branding_json (logo + icon URLs): 1561 (92.6%)
  - address_json, phone_number, share_class_figi, round_lot also captured
- **Output:** `data_prefetch/polygon/reference_extended/{ticker}.parquet` + `_index.parquet`
- **Joint:** Tier H4 P2 — DONE.

---

## INV-030-original — Polygon reference missing address/branding/employees/FIGI/description (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** `data_prefetch/polygon/reference/AAPL.parquet` has 16 fields. Polygon `/v3/reference/tickers/{t}` actually returns: `address (street/city/state/zip), branding (logo_url, icon_url), total_employees, phone_number, description, composite_figi, share_class_figi, round_lot, market_cap` (have), `share_class_shares_outstanding` (have), `weighted_shares_outstanding` (have).
- **Why blocking:** FIGI useful for cross-source matching (Polygon/SEC/Bloomberg). Total_employees + description useful for LLM-agent prompts. Address useful for geographic/local-economy strategies. Branding (logo_url) useful for dashboard.
- **Severity:** LOW-MEDIUM (Phase 1B+ enrichment).
- **Status:** open
- **Next action:**
  - Add missing fields to `prefetch_polygon_reference.py` `fetch_ticker_reference()`
  - Re-prefetch (~1h, fast endpoint, data already at 1686/1937 = 87%)
- **Joint:** field-level matrix.

---

## INV-031 — Quiver congressional missing District/State/Industry/Sector/Filing fields (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** Quiver `/historical/congresstrading/{ticker}` returns 16+ fields per Quiver docs. Our cached schema has 16 cols but missing: `District` (congressional district number), `State` (state abbreviation), `Industry` (industry classification), `Sector` (sector classification), `Filing` (URL to filing).
- **Why blocking:** Senator-vs-rep sub-signals, regional concentration signals, industry-affiliated trades — all need the missing dimensions.
- **Severity:** MEDIUM (Phase 1B refinement); non-blocking for Phase 1A baseline composite.
- **Status:** open
- **Next action:**
  - Probe one congressional API call to verify which fields the API returns
  - Edit `prefetch_quiver.py` save logic for congressional endpoint
  - Re-prefetch (currently mid-flight in BG `b3xny7m35` — won't be in this run)
- **Joint:** INV-024 (sister Quiver field loss); BG `b3xny7m35` state.

---

## INV-032 — Alpha Vantage news cache aggregated daily — lost per-article detail (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** `backtest/data/cache/av_news/CCI.parquet` schema: `date, sentiment_mean, sentiment_weighted, article_count, bullish_count, bearish_count, max_relevance, sentiment_direction`. AV `NEWS_SENTIMENT` API returns per-article: title, url, time_published, authors, summary, banner_image, source, category_within_source, source_domain, topics, overall_sentiment_score, overall_sentiment_label, ticker_sentiment[]. We're aggregating to daily — lost ALL per-article info.
- **Why blocking:** Cannot reconstruct which articles, who wrote them, what they said. LLM-agent context can't read the actual text. Can't do per-article sentiment analysis with our own NLP.
- **Severity:** MEDIUM-HIGH (Phase 1B+ news strategies blocked at the article level).
- **Status:** open
- **Next action:**
  - Edit `prefetch_alphavantage_news.py` to preserve raw articles (with one daily-rollup as derived view, not as primary cache)
  - Re-prefetch full (~10-15h, AV free 25/min limits)
- **Joint:** INV-015 (AV news under-coverage at 25 files — same prefetch needs full rebuild anyway); INV-027 (Polygon news sister field loss).

---

## INV-033 — STRING date columns across 8+ caches (typing gap, not data gap) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; field-level deep-dive
- **Observation:** Multiple cached parquets have `date` / `Date` / `time` / `TransactionDate` / `snapshot_date` / `report_date` columns stored as STRING (object) instead of pandas datetime64. Affected: Wikipedia per-ticker, pytrends per-ticker, Quiver sec13fchanges, Quiver offexchange, Quiver corporatedonors, Quiver patentmomentum, Quiver gov_contracts (lacks Date entirely — INV-024), CNN F&G `date` field, Apewisdom `snapshot_date`, CFTC `report_date`.
- **Why blocking:** Functional — engine can `pd.to_datetime` at read time — but represents prefetch type-info loss during write. Also: PIT cutoff queries (`df[df.date <= as_of]`) work correctly only if string format is ISO-8601 lexically-sortable.
- **Severity:** LOW (typing — engineering hygiene; current consumers all coerce at read time).
- **Status:** open
- **Next action:**
  - Write a one-time migration script that walks each affected cache + coerces date columns to datetime64
  - Or: edit each prefetcher to write datetime64 directly going forward (preferred — fix root cause)
  - ~1h
- **Joint:** field-level matrix; sister to INV-020 (canonical-source rule violation pattern).

---

## INV-034 — Polygon Indices Basic ACTIVATED but tier gives only 2 of 13 wanted indices (Pass 53 Day-9 v8h+1 2026-05-08 — REFRAMED)

- **Discovered:** 2026-05-08 morning (initial); REFRAMED 2026-05-08 afternoon after owner activated Indices Basic and re-probe
- **Observation (REVISED):** Owner activated Indices Basic. Re-probe finds 2 indices accessible at our tier:
  - ✅ I:NDX, I:COMP (Massive's own indices — work)
  - 🔴 I:VIX, I:SPX, I:DJI, I:RUT, I:VIX9D, I:VIX3M, I:VVIX, I:OEX (still 403 — likely CBOE/S&P licensing gate beyond Indices Basic)
  - ⚠ I:MID, I:SML, I:NYA (probe returned 200 single-day but EMPTY for full date range — odd, may need different request format)
- **Why:** Indices Basic appears to give Massive's own indices but NOT CBOE-licensed (VIX family) or S&P-licensed (SPX/DJI/RUT). FRED VIXCLS / VXVCLS remain primary VIX source.
- **Severity:** REDUCED. NDX + COMP are useful adds; VIX comes from FRED.
- **Status:** RESOLVED-PARTIAL — Indices Basic active, partial coverage; high-value indices still gated.
- **Next action:** verify with owner whether the 11 blocked indices require additional licensing fees beyond Basic plan.
- **Joint:** **INV-038** (companion finding); BUG-VIX-PROXY (FRED is workaround); INV-010 (VVIX deferred).

---

## INV-038 — RESOLVED 2026-05-08 v8h+1 — Polygon Indices Basic license tier discovered + activated; 2/13 covered (Pass 53)

- **Discovered:** 2026-05-08 morning; `probe_api_catalog.py` returned 403 NOT_AUTHORIZED for I:SPX, I:DJI, I:RUT, I:VIX, I:VIX9D, I:VIX3M, I:VVIX, I:OEX (all major indices). Only I:NDX returned 200 (anomaly).
- **Observation:** Owner activated Polygon Indices Basic 2026-05-08. Re-probe finds 2 of 13 wanted indices accessible at our tier (I:NDX, I:COMP). The 11 others (VIX/SPX/DJI/RUT family) require additional CBOE/S&P licensing fees beyond Basic.
- **Resolution:** RESOLVED-PARTIAL per INV-034 reframing. The activation step is complete; the licensing-gate constraint is empirical and structural. FRED VIXCLS / VXVCLS remain primary VIX source; BUG-VIX-PROXY documented as data-source choice not bug.
- **Status:** RESOLVED 2026-05-08 v8h+1.
- **Joint:** **INV-034** (companion finding, RESOLVED-PARTIAL); BUG-VIX-PROXY (FRED workaround documented); INV-010 (VVIX gap accepted as deferred).

---

## INV-035 — RESOLVED — Finnhub key added 2026-05-08; 13/20 endpoints accessible at free tier (Pass 53 Day-9 v8h+1 2026-05-08)

- **Status:** RESOLVED — owner added FINNHUB_API_KEY to .env 2026-05-08 afternoon.
- **Re-probe results (free tier):**
  - ✅ Free + working: quote, profile2, peers, insider-transactions, insider-sentiment, recommendation, eps_surprise, calendar/earnings, calendar/ipo, calendar/economic, company-news, financials-reported, metric (13)
  - 🔴 Premium-only: price-target, social-sentiment, upgrade-downgrade, eps-estimate, revenue-estimate, dividend, split (7)
- **Action:** new prefetch script `scripts/prefetch_finnhub_full.py` to author for the 13 free endpoints across full universe. ~6-10h fetch wall (free tier 60/min × 13 endpoints × 1937 tickers).
- **Joint:** INV-016 (Finnhub news S&P-only stale — to re-do as part of full Finnhub prefetch).

---

## INV-035-old — replaced by RESOLVED entry above (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08 morning; `probe_api_catalog.py` skipped Finnhub block because `os.environ.get("FINNHUB_API_KEY")` returned empty string.
- **Observation:** Owner stated 2026-05-07 they have a Finnhub key. The key is not in `.env` accessible to scripts. Either: (a) key was set in a different env file, (b) key was at one point but removed, (c) key needs to be added.
- **Why blocking:** Finnhub is a multi-source API for analyst recommendations / price targets / EPS surprises / insider sentiment / social sentiment / pattern scans / IPO calendar / economic calendar — Phase 1B+ overlay-strategy enabler. Without key, no probe possible, no prefetch.
- **Severity:** MEDIUM (Phase 1B overlay; non-blocking for Phase 1A).
- **Status:** open — owner action pending.
- **Next action:** owner adds `FINNHUB_API_KEY=<value>` to `.env`. Re-run probe; if 200, update API_ENDPOINT_INVENTORY.md with Finnhub catalog + plan an extend prefetch.
- **Joint:** INV-016 (Finnhub news prefetch S&P-only — sister); CHECKLIST #77.

---

## INV-036 — 13 Quiver endpoints in `API_AUDIT.md` don't exist at our Trader tier (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08 morning; `probe_api_catalog.py` returned 404 for the following endpoints I had assumed exist (per API_AUDIT.md training-data memory):
  - `/historical/wikipedia/{t}` 404
  - `/historical/patentmomentum/{t}` 404 (only bulk works)
  - `/historical/appratings/{t}` 404
  - `/historical/sec13fchanges/{t}` 404 (only `/live/sec13fchanges` works)
  - `/historical/insidertrading/{t}` 404 (correct name is `/live/insiders`)
  - `/historical/earningsbeats/{t}` 404
  - `/historical/redditpoliticians/{t}` 404
  - `/historical/reddittendies/{t}` 404
  - `/historical/snptrend/{t}` 404
  - `/historical/swaps/{t}` 404
  - `/historical/googletrends/{t}` 404
  - `/historical/linkedindata/{t}` 404
  - `/historical/iposcalendar/{t}` 404
  - `/historical/optionsflow/{t}` 404
  - `/historical/estimates/{t}` 404
- **Observation:** API_AUDIT.md Tier 1 framework had a `L131` "Honest knowledge limit" disclaimer — but the disclaimer was not enforced. Multiple audits inherited this assumed-endpoint list and propagated it through 3 passes without verification.
- **Why not blocking:** None of these endpoints were ever consumed by our engine — they were aspirational additions in audit docs. No real consumer crashes. But they polluted gap-analysis and recommendation lists.
- **Severity:** LOW (informational + canonical-doc cleanup).
- **Status:** open
- **Next action:**
  - Update `API_AUDIT.md` Quiver section to reflect probe-confirmed endpoint set (only working: congresstrading, senatetrading, housetrading, govcontracts, lobbying, wallstreetbets, twitter, spacs, plus live insiders/sec13f/sec13fchanges/offexchange/topshareholders-bulk-only/etfholdings/corporatedonors/quivernews/patentmomentum-bulk).
  - Confirm ENDPOINTS NEW that DO work and we don't currently fetch:
    - **`/historical/senatetrading/{t}`** — separate from congress; senate-only with `Senator` field — NEW
    - **`/historical/housetrading/{t}`** — house-only — NEW
    - **`/historical/spacs/{t}`** — SPAC mention timeline — NEW
- **Joint:** CHECKLIST #77 (this is the canonical case for the new rule); CHECKLIST #51 (honest knowledge limit); INV-024 (reframing — same root pattern).

---

## INV-037 — Polygon Filings + Fundamentals endpoints (10-K Sections / 13-F / 8-K Text / Form 3/4 / Income Stmt / Balance Sheet / Cash Flow / Ratios / Float / Short Interest / Short Volume) require Stocks Plus tier — NOT our Stocks Starter (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08 morning; `probe_api_catalog.py` returned 404 for all `/stocks/v1/filings/...` and `/stocks/v1/fundamentals/...` endpoints despite being listed in `massive.com/docs/llms.txt` Stocks section.
- **Observation:** Massive's llms.txt catalogs the FULL Stocks feature set including Filings (10-K Sections, 13-F, 8-K Text, Form 3/4, SEC EDGAR Index, Risk Categories, Risk Factors) + Fundamentals (Balance Sheets, Cash Flow, Float, Income Statements, Ratios, Short Interest, Short Volume). However probe shows all paths I guessed return 404 — these features require Stocks **Plus** or higher tier, NOT Stocks Starter.
- **Why blocking:** my prior INV-025 (SEC EDGAR filing-metadata-only) and INV-026 (Polygon financials JSON unparsed) recommendations assumed Polygon could be the structured-fundamentals provider. That assumption is wrong at our tier.
- **Mitigation discovered same probe:** SEC EDGAR XBRL `companyfacts` + `frames` endpoints (FREE, public) provide the same structured fundamentals + filing data we need. INV-025/026 fix path is **SEC XBRL direct, not Polygon Filings**.
- **Severity:** MEDIUM (was P1 blocker for INV-025/026; now mitigated via SEC XBRL).
- **Status:** open — pivot recommendation to SEC XBRL.
- **Next action:**
  - Author `scripts/prefetch_sec_xbrl.py`: per-ticker `companyfacts` (`data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`) + selected `frames` (`data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/CY{year}Q{quarter}.json`).
  - For each ticker: 1 companyfacts call → structured time-series of every XBRL line item.
  - ~1937 tickers × 1 call each + ~50-100 frames calls = manageable.
- **Joint:** INV-025 (SEC EDGAR filing-metadata-only — XBRL solves part of this); INV-026 (financials_json — XBRL provides structured); CHECKLIST #77.

---

## INV-039 — Polygon Benzinga partner data 5/7 endpoints accessible at our tier (rich data) (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08 afternoon; smoke-test of `prefetch_polygon_benzinga.py` with auto-probe.
- **Observation:** Benzinga is a paid Polygon partner add-on. Probe with AAPL (single ticker) finds:
  - ✅ analyst_insights: 132 records
  - ✅ ratings: 1508 records
  - ✅ earnings: 62 records
  - ✅ guidance: 31 records
  - ✅ firm_details: 658 records
  - 🔴 consensus: 404 (URL guess wrong; need to find correct path)
  - 🔴 news: 403 (premium add-on beyond our tier)
- **Significance:** **MAJOR Phase 1B+ signal opportunity**. Analyst recommendations + ratings + price targets + guidance are high-value for momentum + reversal + earnings strategies. Combined with eps_surprise (already in cache from Quiver insider): comprehensive earnings-event signal.
- **Status:** open; full prefetch P1.
- **Next action:** full universe prefetch of 5 working endpoints. Estimated 5 endpoints × 1937 tickers × 0.2s sleep = ~30 min wall clock per endpoint, ~2.5h aggregate. Probe `consensus` URL alternatives.
- **Joint:** PREFETCH_COVERAGE_AUDIT.md Tier H11.

---

## INV-040 — Quiver senate/house/spacs endpoints WORK at our tier — major data we never fetched (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08 afternoon; smoke of `prefetch_quiver_new_endpoints.py`.
- **Observation:** Smoke with AAPL/MSFT/GOOGL/NVDA/SPY yields rich data:
  - senatetrading: AAPL 212 / MSFT 136 / GOOGL 27 / NVDA 87 / SPY 27 records — separate from congresstrading
  - housetrading: AAPL 479 / MSFT 457 / GOOGL 166 / NVDA 335 / SPY 33 records — biggest dataset
  - spacs: AAPL 108 / MSFT 100 / GOOGL 0 / NVDA 32 / SPY 303 records — SPAC mention timeline
- **Significance:** Senate-only / House-only sub-feeds enable chamber-specific signals. SPAC feed enables SPAC-related strategies for T2 (recent IPOs / spinoffs). Quiver Trader plan included these all along — never fetched until now.
- **Status:** open; full prefetch P1.
- **Next action:** full universe prefetch (~40 min × 3 endpoints = ~2h aggregate at 1.2s sleep). Quiver rate-limit safe.
- **Joint:** API_AUDIT.md Quiver section needs update to reflect probe-confirmed endpoint set; sister to INV-036.

---

## INV-041 — SEC XBRL prefetch script `git_commit()` captures all staged files, not just cache dir (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08 morning; my Tier-1 batch commit was rejected/lost; investigation showed staged files were captured by `prefetch_sec_xbrl.py`'s background `git_commit()` calls under "SEC XBRL prefetch: batch N" messages
- **Observation:** `scripts/prefetch_sec_xbrl.py` `git_commit()` runs `git add data_prefetch/sec_xbrl/` then `git commit -m "..."` — but `git commit` without `-- <paths>` commits ALL staged files in the index. So if I had OTHER files staged (e.g. new prefetch scripts, data caches), the BG's commit captured them under the misleading "SEC XBRL: batch 5" message.
- **Why not blocking:** Data is preserved on origin/main. Just confusing commit narrative.
- **Severity:** LOW (process / housekeeping).
- **Status:** RESOLVED 2026-05-10 v8h+1 (path-restricted commit pattern landed in 4 scripts; regression test pins the pattern).
- **Resolution:** Updated `git_commit()` in 4 scripts to use `git commit -m message -- <cache_path>` form which restricts the commit to the named paths only (preventing capture of unrelated staged files):
  - `prefetch_sec_xbrl.py` - now `git commit -m message -- str(CACHE_DIR)`
  - `prefetch_polygon_benzinga.py` - now `git commit -m message -- str(CACHE_ROOT)`
  - `prefetch_alphavantage_news.py` - now `git commit -m message -- backtest/data/cache/av_news/ av_news_checkpoint.json`
  - `prefetch_quiver.py` - now `git commit -m message -- backtest/data/cache/quiver/ quiver_checkpoint.json`
  - 7 sister scripts already had the pattern (prefetch_quiver_new_endpoints, prefetch_polygon_options_full, prefetch_polygon_indicators, prefetch_finnhub_*, prefetch_stocktwits) - left untouched.
- **Regression test:** `backtest/tests/test_inv041_path_restricted_commits.py` (5 tests) pins the pattern via regex scan of all 11 in-scope scripts. New scripts must follow the same pattern; the test will catch regressions.
- **Verification:** 5/5 tests PASS post-fix.
- **Joint:** PREFETCH_COVERAGE_AUDIT.md Tier H execution; sister to git-flow hygiene rules; CHECKLIST #74 (every observation logged); CHECKLIST #78 (per-addressal pyramid - new test file lands same-commit per DEC-594).

---

## INV-042 — FRED series DEXJPUS returns 500 — likely deprecated (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08; FRED API retry confirmed persistent 500 for series_id `DEXJPUS` while DEXUSUK / DEXCAUS / DEXSZUS / DEXUSEU all returned 200 with 1583 obs each.
- **Observation:** DEXJPUS was the JPY/USD exchange rate. May have been renamed or deprecated. FRED doc page would clarify.
- **Why not blocking:** USDJPY is fetched from Polygon Forex Basic (12/12 OK). FRED currency cross alternatives (DEXSZUS = CHF, DEXUSEU = EUR, DEXCAUS = CAD, DEXUSUK = GBP) all work.
- **Severity:** LOW (alternative source available).
- **Status:** open — research correct series ID.
- **Next action:** check FRED series search for "JPY US" / "Japanese yen" — likely renamed to DEXUSJP or similar. Update `prefetch_macro.py` SERIES dict.
- **Joint:** Tier H15 execution; FRED retry 4/5 succeeded (DEXJPUS only failure).

---

## INV-043 — Windows-reserved filenames break corp_actions per-ticker save (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08; corp_actions BG `b07b0rg5j` wrote `dividends_full/PRN.parquet` and `ipos_full/CON.parquet` — Windows reserves PRN (parallel port) and CON (console) as device names; git couldn't open them on push.
- **Observation:** Reserved Windows device names cannot be filenames: `CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9`. Polygon tickers `PRN` and `CON` (real public companies) hit this.
- **Severity:** MEDIUM — blocks any per-ticker save on Windows for tickers matching these names.
- **Status:** RESOLVING THIS COMMIT
- **Fix landed this commit:**
  - Renamed `PRN.parquet` -> `PRN_.parquet` and `CON.parquet` -> `CON_.parquet`
  - Added `safe_filename_stem()` helper to `scripts/prefetch_polygon_corp_actions_full.py` that appends `_` for any ticker matching reserved Windows names
- **Action propagation needed:** apply same `safe_filename_stem()` pattern to other prefetch scripts that save per-ticker parquets (Quiver, SEC EDGAR, Finnhub) — only triggers if those datasets contain `PRN/CON/AUX/NUL/COM*/LPT*` tickers, which is rare but possible
- **Joint:** sister to INV-041 (script process bugs); CHECKLIST #5 (proactive flagging — caught at push time, not write time).

---

## INV-044 — SEC EDGAR per-form coverage capped at 1683 by CIK-map gap (254 tickers no CIK) (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08; B1-redo BG `b2an5z5lx` summary: 1670 SUCCESS / 13 no-data / **254 no CIK in map** / 0 errors. Per-form counts unchanged (10_K: 1683, 10_Q: 1683, 8_K: 1715, etc.) because the 254 missing tickers don't have CIK in our reference cache.
- **Observation:** SEC EDGAR top-up requires CIK lookup. CIK map sourced from `data_prefetch/polygon/reference/` (1686 tickers via `b9xczleu2` BG). The 254 universe-tickers-without-CIK include delisted (ABMD/ALXN/AGN/etc.) and possibly newer T2/T3 names where Polygon reference doesn't carry the CIK.
- **Severity:** MEDIUM (Phase 1B+ filing-overlay coverage capped at ~87%; Phase 1A baseline doesn't depend on SEC EDGAR per-form metadata directly).
- **Status:** open
- **Next action:**
  - Probe SEC EDGAR submissions endpoint with ticker (instead of CIK lookup) to find CIK for missing 254 — `data.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={t}` returns CIK from ticker
  - Or: use SEC EDGAR's `company_tickers.json` master list (one-fetch, has all tickers + CIKs)
  - After CIK map expanded, re-run `prefetch_sec_edgar.py` to capture missing 254
- **Joint:** INV-030 (Polygon reference 251 delisted = same root); SEC XBRL `prefetch_sec_xbrl.py` had similar 251 no-CIK skips.

---

## INV-045 — Stale numerical claims in reference docs (cross-doc count drift) (Pass 53 Day-9 v8h+1 2026-05-08 evening)

- **Discovered:** 2026-05-08 evening; owner asked dashboard decision-count check → analysis showed AUDIT_INDEX header claimed 354 decisions but table actually had 520 (+166 drift).
- **Observation:** Multiple reference docs carry numerical claims in prose (e.g. `Total: N decision entries`, `N canonical bugs`) that drift from the structured-data reality below them. Detected at audit:
  - AUDIT_INDEX.md: 354 claimed, 520 actual (+166 drift)
  - BUG_REGISTER.md: 148 claimed, 152 actual (+4 drift)
- **Severity:** MEDIUM (any consumer reading the header gets wrong counts; test_doc_count_consistency was tolerating upward drift).
- **Status:** RESOLVED 2026-05-10 v8h+1 (sync_doc_counts.py + tightened consistency test landed; auto-cron 2-hour drift sweep operational since 2026-05-08; per-turn doc sync per CHECKLIST #67/#79 keeps registers aligned).
- **Fix landed:**
  - `scripts/sync_doc_counts.py` (NEW) - reads source-of-truth tables, regenerates header claims; supports `--check` (CI gate) and `--update` (fix mode)
  - `test_audit_index_decision_count_matches_table` tightened to fail on drift in BOTH directions (was downward-only); threshold 5%
  - One-shot `--update` ran 2026-05-08 evening: AUDIT_INDEX 354 -> 520; BUG_REGISTER 148 -> 152
- **Action propagation needed:**
  - Add `python scripts/sync_doc_counts.py --check` to pre-commit hook (analogous to `preflight.py`) so future drift is caught at commit-time
  - Or: make sync_doc_counts.py auto-run + commit before tests on every push
- **Joint:** CHECKLIST #34 (count-derived fields regenerate from source); CHECKLIST #36 (numerical claims regenerated at write time); CHECKLIST #74 (this INV in same commit as fix); test_doc_count_consistency.py (catches future drift).

---

## INV-046 — Phase 1A smoke surfaces single-trade PnL > 100% (engine bug candidate) (Pass 53 Day-9 v8h+1 2026-05-08)

- **Discovered:** 2026-05-08 evening, full pyramid run after 13-layer expansion.
- **Observation:** `test_e2e_phase1a_smoke.py::test_g1_pnl_realistic` asserts `df['pnl_pct'].abs().max() < 100`. In the smoke fixture's 397-trade run, max PnL hit **106.06%** (single trade exceeds 100% absolute). Most trades are normal 1-10%, but at least one trade has a runaway return.
- **Why blocking for Phase 1A:** A trade returning >100% PnL means either (a) survivorship leak (closing on a multi-bagger split-adjusted price), (b) position-sizing extreme letting >1x leverage through, (c) fill bug (entry vs exit price computed against different splits/dividends), or (d) the realism floor itself is wrong (e.g., genuinely 0DTE options-like instruments could exceed 100%, but Phase 1A is equity-only so they shouldn't).
- **Severity:** HIGH — Phase 1A May 15 launch should not run on an engine that produces unrealistic single-trade returns. Either fix the engine OR document the finding + raise the realism floor with rationale.
- **Status:** RESOLVED-DOCUMENTED 2026-05-10 (Pass 53 v8h+1)
- **Resolution:** Diagnostic confirmed NOT a bug. Offending trade: NVDA `ichimoku_cloud_breakout` 2023-02-21 -> 2023-08-09, entry $20.74 / exit $42.74 / +106% / 169-day hold / trailing_stop exit. Cache verification: NVDA close 2023-02-21 raw $20.655 -> 2023-08-09 raw $42.554 = +106.02% (matches engine within slippage). This is the 2023 NVDA AI rally captured correctly by a momentum strategy with trailing-stop exit. Realism floor of 100% was set before NVDA/SMCI 2023 became observable in the smoke fixture window.
- **Action taken:**
  - Raised abs cap from 100% to 300% (catches genuine engine bugs like decimal/split errors at 10x+ but allows real momentum runs)
  - Added rapidity gate: PnL > 100% with hold_days < 30 = "real bug" pattern (split-adjust, fill-side, decimal mistakes); legitimate momentum trades that big take time to develop
  - Test hardened: `test_g1_pnl_realistic` now asserts both the absolute cap and the rapidity gate
  - DEC-607 logged for traceability of the threshold change
- **Verification:** per-addressal pyramid 159/159 PASS (unit+integration+smoke+regression+system layers); same-commit rule per DEC-594 satisfied (test change + INV update + DEC log + AUDIT narrative + CAV-078 in same commit).
- **Joint:** test_e2e_phase1a_smoke.py G1 gate; Phase 1A May 15 launch dependency CLEARED.

---

## INV-047 — Quiver `etfholdings` refresh dead-end; existing 1563 files are static snapshot (Pass 53 Day-9 v8h+1 2026-05-10)

- **Discovered:** 2026-05-10 owner-approved option-1 etfholdings refresh; probe phase per CHECKLIST #77.
- **Observation:** All Quiver Trader plan candidate paths return 404:
  - `/historical/etfholdings/{ticker}` -> 404
  - `/live/etfholdings/{ticker}` -> 404
  - `/historical/etfHoldings/{ticker}` (camelCase) -> 404
  - `/etfholdings/{ticker}` (no version prefix) -> 404
  - Polygon `/v3/reference/tickers/{etf}/etfs` -> 404
  - Polygon `/v3/reference/etfs/{ticker}` -> 404
  - Polygon `/v3/reference/etfs/{ticker}/holdings` -> 404
- **Why we have data anyway:** existing 1563 cached files at `data_prefetch/quiver/etfholdings/` came from an unknown / deprecated endpoint that no longer responds. Schema (5 cols: ETF Symbol, Holding Name, Holding Symbol, % of ETF, Value $) suggests an "ETFs that hold this ticker" reverse-lookup, possibly from a deprecated Quiver path or an ad-hoc prior fetch.
- **Why not blocking:** etfholdings is P2 criticality (Phase 1B+ ETF flow proxy). Phase 1A baseline doesn't consume etfholdings data. Static snapshot is acceptable for Phase 1B+ research while data-source decision is pending.
- **Severity:** LOW for Phase 1A; MEDIUM for Phase 1B+ (signal staleness over time).
- **Status:** OPEN — deferred to Phase 1B+ pending owner decision on data source.
- **Resolution paths (owner choice):**
  - **(a) Accept static snapshot** as-is (zero cost; data freshness limited to last unknown fetch date) — current default per CAV-077.
  - **(b) Subscribe to paid 3rd-party** — FMP (~$30/mo), EOD Historical Data (~$30/mo), or etfdb.com data API (~$50/mo). Best-quality option but $360-600/yr for a P2 signal.
  - **(c) Build scraping infra** against etf.com / etfdb.com public pages — cheap but fragile; would create downstream maintenance burden contra owner's "no downstream issues" rule.
  - **(d) Owner-side query** to Quiver support requesting the correct endpoint for our Trader plan — zero cost but unbounded latency; Quiver may not have the endpoint at all.
- **Joint:** CHECKLIST #77 (canonical-source rule — caught the 404 honestly instead of fabricating an endpoint); CAV-077 (this static-snapshot caveat); DEC-606 sister exclusion pattern (Finnhub financials_reported permanently excluded due to superior alternative; etfholdings has no equivalent superior alternative at zero cost).

---

*Last updated: 2026-05-10 v8h+1 — INV-046 RESOLVED-DOCUMENTED (DEC-607); INV-047 logged (etfholdings dead-end); CAV-077 added; INV-048 logged (H22 date-typing residual gap)*

---

## INV-048 — H22 date-typing residual gap: polygon ohlcv_daily / indicators / ALFRED realtime_* still object dtype (Pass 53 Day-9 v8h+1 2026-05-10)

- **Discovered:** 2026-05-10 H22 verify pass; empirical scan of newly-added caches post-J2 broad sweep.
- **Observation:** 3 caches have date-related columns stored as `object` dtype rather than `datetime64`:
  - `data_prefetch/polygon/ohlcv_daily/<TICKER>.parquet` — `date` column = Python `date` objects (object dtype). Source: prefetch script writes `df["date"] = pd.to_datetime(...).dt.date` which produces date objects, not Timestamp.
  - `data_prefetch/polygon/indicators/{ema_*,sma_*,macd,rsi_14}/<TICKER>.parquet` — `date` column = `object`. Same pattern.
  - `data_prefetch/alfred/<SERIES>.parquet` — `date` IS datetime64 ✅ but `realtime_start` + `realtime_end` are `object`.
- **Functional impact:** minor; pd Timestamp comparisons against date objects work transparently; engine PIT loader uses `pd.to_datetime` defensively. Sortability and groupby work. The strict per-J2 spec calls for `datetime64` consistency, which is not met for these 3 caches.
- **Why deferred from H22 to follow-up:** migration touches ~13K parquet files (1937 OHLCV + 11622 indicators + 80 ALFRED) - high blast radius. Per CHECKLIST #78 per-addressal pyramid mandate, separate addressal with isolated pyramid is cleaner than bundling into H22 verify.
- **Severity:** LOW (functionally transparent at engine level; spec-consistency only).
- **Status:** OPEN — deferred to migration addressal post-Phase-1A (or before, if owner-prioritized).
- **Recommended action:**
  - (A) Defer past Phase 1A May 15 launch; engine works on object-dtype dates today (default).
  - (B) Run a one-shot migration script reading + coercing + rewriting all ~13K parquets (~5-10 min wallclock; compression-preserving).
  - (C) Update prefetch scripts to write datetime64 going forward + run migration on existing.
- **Joint:** J2 H22 broad sweep (7033 prior cases done; this is residual); CHECKLIST #78 per-addressal pyramid (the reason this is its own INV instead of bundled into H22 verify).


## INV-049 — AVOID-tier confidence trades fire at 39% of executed trades (Pass 53 Day 9+ 2026-05-16 Phase 1A baseline)

- **Observation:** Phase 1A baseline (67-tkr canonical run, output_phase_1a_launch/) closed 225 trades over 1044 days. Per-confidence-tier breakdown: HIGH 136 / **AVOID 88** / EXCEPTIONAL 1. AVOID tier accounts for **39% of all trades** despite the documented gate semantics that AVOID = skip entry. Average PnL for AVOID trades: -2.70% (worst of all tiers). Average PnL for HIGH: +0.68%. The system would be net positive if AVOID-tier trades were genuinely blocked at entry.
- **Two hypotheses:**
  1. **Entry-gate bypass bug** — the AVOID tier label is computed correctly but the engine's entry filter doesn't skip on it. Look at `backtest/engine/backtest.py` candidate-evaluation flow for tier checks.
  2. **Post-entry tier downgrade** — trades enter at HIGH tier but the confidence_tier column reflects the LATEST tier (re-evaluated mid-hold). In that case the column is misleading: AVOID is an outcome, not an entry decision.
- **Evidence to disambiguate:** check whether `confidence_tier` is the entry-time tier or current/exit-time tier. If schema doc says entry-time → bug. If exit-time → schema rename to `confidence_tier_at_exit` + add `confidence_tier_at_entry`.
- **Phase 1A-β impact:** if this is bug #1, fixing it could materially improve baseline P&L. If hypothesis #2, no engine fix needed but trade_log schema needs disambiguation.
- **Joint:** DEC-021 tier mapping; DEC-061/062 tier-to-size modifier; F-008 position sizing tiers; CLAUDE.md Approved Rules "Position sizing: tiered 5/4/3/1.5/0.75% by confidence tier".


## INV-050 — Walk-forward folds suppressed when --no-git active (Pass 53 Day 9+ 2026-05-16 Phase 1A baseline)

- **Observation:** Phase 1A baseline `improvements_summary.json` reports `walk_forward_summary: {total: 0, robust: 0, overfit: 0}`. With 4-year OOS window (2022-05-05 → 2026-05-05) + 1-year folds per DEC-505, expected 3-4 folds. Root cause: `run_phase1a.py:208`:

      walk_forward=not args.no_git,  # suppress per-batch WF - run on merged result only

  This suppresses walk-forward intentionally for parallel-batch mode (where merge would re-compute), but the canonical baseline run also used `--no-git` (single batch). Walk-forward thus did not run on the baseline output even though the run was not a parallel-batch fragment.
- **Phase 1A-β impact:** the 5 parallel batches will correctly suppress WF and the merge_batch_outputs.py step will re-compute it. But the baseline gap is real — re-run with `--walk-forward-only` flag (if exists) or run on merged baseline output.
- **Recommended action:** Decouple WF suppression from `--no-git`. Add explicit `--no-walk-forward` flag. Re-run WF on baseline output as a separate post-processing step.
- **Joint:** DEC-505 (4-fold WF + Polygon cache window); DEC-109 (rolling 5yr/1yr walk-forward); `backtest/run_phase1a.py:208`; `scripts/merge_batch_outputs.py`.


## INV-051 — Regime-stratified CV stratifier collapses to neutral-only (Pass 53 Day 9+ 2026-05-16 Phase 1A baseline)

- **Observation:** Phase 1A baseline `regime_stratified_summary.json` shows:

      proportions:   {calm: 0.0, neutral: 1.0, volatile: 0.0, crisis: 0.0}
      per_regime:
        calm:     0 train,  0 test, INSUFFICIENT_SAMPLE
        neutral: 40 train, 17 test, INSUFFICIENT_SAMPLE
        volatile: 0 train,  0 test, INSUFFICIENT_SAMPLE
        crisis:   0 train,  0 test, INSUFFICIENT_SAMPLE

  But the per-trade `regime` column has 123 bull / 45 bear / 57 neutral. The stratifier is mapping ALL trades into the `neutral` regime bucket for cross-val purposes. Either the stratifier uses a different regime-naming convention (calm/neutral/volatile/crisis vs bull/neutral/bear/crisis) without translation, OR the stratifier inputs are unfiltered NaN-defaulting to neutral.
- **Phase 1A-β impact:** Phase 1A-β cube populator (DEC-422) needs per-regime stratification. If stratifier doesn't map correctly, the verdict cube will under-resolve regime cells.
- **Recommended action:** Locate stratifier code (likely `backtest/results/metrics.py:compute_regime_stratified_summary` or similar). Verify regime label vocabulary alignment with per-trade `regime` column. Map bull/bear/neutral/crisis → calm/neutral/volatile/crisis if that's the intended translation, OR rename one side to consolidate.
- **Joint:** F-006 regime taxonomy (4 types); DEC-106 8-input classifier; DEC-422 cube populator.


## INV-052 — Dispersion circuit breaker fires z-score 379 outlier (Pass 53 Day 9+ 2026-05-16 Phase 1A baseline)

- **Observation:** Phase 1A baseline `circuit_breaker_log.csv` shows 74 dispersion-CB activations over 4 years. Real-world activations are at z=3-7 (extreme but plausible). One activation on 2022-06-09 reports **z_score=379.0763** with `today_dispersion=1.732546`. A z-score of 379 implies dispersion is 379 standard deviations above mean — physically impossible. Almost certainly a numerical edge case: very small stddev in rolling window (e.g., division-by-near-zero) or NaN handling.
- **Phase 1A-β impact:** at 1937-ticker scope, dispersion calc may hit similar edge cases more often. Could cause spurious entry blocks or stop-out cascades.
- **Recommended action:** Find the dispersion-CB calc site. Add guard: if rolling stddev < epsilon (e.g., 1e-6), skip z-score calc or cap at z=10. Or use median absolute deviation (MAD) as more robust denominator.
- **Joint:** DEC-128 dispersion circuit breaker; engine `dispersion_cb_triggered_dec128` event tag.


## INV-053 — Entry funnel rejects 99.87% of candidates (172544 skipped vs 225 executed) (Pass 53 Day 9+ 2026-05-16 Phase 1A baseline)

- **Observation:** Phase 1A baseline 4-year run rejected **172,544 candidate trades** vs 225 executed. Rejection rate **99.87%**. Top reasons:
  - 46,607 (27%): `portfolio_gate_max_open_positions_10_reached`
  - 45,601 (26%): `vol_target_scaled_1.5x`
  - ~33,000 (19%): event suppression (NFP/CPI/FOMC/earnings d-2 → d+1)
  - remainder: liquidity / regime / cooldown / etc.

  **Interpretation:** the system is generating ~770 candidates/day on average but most days are gated out. With a 10-position cap (DEC-070-adjacent), once 10 positions are open new candidates are skipped regardless of merit. The `vol_target_scaled_1.5x` reason is harder to parse — appears to be a per-trade sizing decision rather than a skip.
- **Phase 1A-β impact:** At 1937-ticker scope, candidate volume scales ~30×. Even at same 0.13% acceptance, expect ~6,750 executed trades over 4 years (vs 225 in baseline). That's a meaningful sample for Bonferroni validity per strategy. **But:** the portfolio_gate_max_open_positions_10 cap is independent of universe size — it will continue to be the dominant gate. Consider raising the position cap for 1A-β to let more trades through.
- **Recommended action:**
  - (A) Audit the funnel — confirm each rejection reason is correct semantically (e.g., is `vol_target_scaled_1.5x` actually a skip or a sizing event mis-tagged as skip).
  - (B) Document the max-open-positions=10 cap's interaction with universe size. Consider tier-aware scaling (e.g., cap=20 at full universe) for Phase 1A-β.
  - (C) Add a "rejection-reason concentration" metric to detect when one gate dominates abnormally.
- **Joint:** DEC-070 portfolio-level exit logic (the 10-cap origin); DEC-348 event suppression windows; CLAUDE.md "Max candidates/day: 10".
