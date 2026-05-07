# OPEN_INVESTIGATIONS.md — Canonical flag tracker

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

## INV-016 — Finnhub news 509 files = S&P-500-only (NOT expanded to Master Universe) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; comprehensive prefetch deep-dive audit
- **Observation:** `backtest/data/cache/finnhub_news/` has exactly 509 files. The script `scripts/prefetch_finnhub_news.py` line ~31 reads `from backtest.data.universe import get_sp500_constituents, ETFS_FULL` and uses S&P 500 + ETFs only. Same pattern as old Quiver per-ticker (which is now being fixed by `bsu432hbt` BG). Needs the same Master-Universe-expansion treatment.
- **Why not blocking:** Free-tier Finnhub returns near-empty for older dates; current cache is ~2025-Mar 2026 only. Phase 1A baseline doesn't depend on Finnhub news (Polygon news is primary). Phase 1B+ news-sentiment strategies could benefit from cross-source.
- **Severity:** HIGH for owner's "broad everything" — known stale prefetch script + stale universe scope.
- **Status:** open
- **Next action:**
  - Update `scripts/prefetch_finnhub_news.py` to read Master Universe CSV (1937) instead of S&P 500
  - Switch to `data_prefetch/finnhub/` canonical Sprint 0A path
  - Re-prefetch (~6-8h on free tier 60/min)
  - Confirm Finnhub subscription tier — free returns minimal historical; basic paid tier needed for >1y lookback
- **Joint:** INV-015 (Alpha Vantage same pattern); CHECKLIST #76 (column-(b) verification — paper audit would have reported coverage % vs S&P only, not flagged the universe-mismatch as separate concern).

---

## INV-017 — Polygon dividends/splits canonical paths each have 1 file (vs 1500+ tickers actually pay/split) (Pass 53 Day-9 v8h evening)

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

## INV-023 — Quiver BG `bsu432hbt` died from second Unicode emoji bug at line 231 — completed congressional only (1/7 endpoints) (Pass 53 Day-9 v8h evening)

- **Discovered:** 2026-05-07 evening; Quiver BG failed with exit code 1 at end of congressional fetch
- **Observation:** `scripts/prefetch_quiver.py` had MULTIPLE Unicode chars in print statements: `✓` (✓ at line 197 — fixed earlier in `33b93fec`), `✅` (✅ line 231), `⚠` (⚠ lines 234, 243), `❌` (❌ line 237), `—` em-dash (lines 182, 208, 209, 212, 217). Earlier fix at line 197 was incomplete — line 231 ✅ crash was the FATAL exit. The em-dash and other emoji fired as `UnicodeEncodeError` in Windows cp1252 console; the inner-loop em-dash crashes were caught by the outer `except Exception` and logged as "ERROR on TICKER" (misleading — the data was actually saved before the print crash).
- **Why not blocking long-term:** Data integrity intact. `save_ticker_data()` runs BEFORE the failing print, so data files were saved + checkpoints updated for every ticker. Verification: 1941 congressional parquet files vs 1921 checkpoint entries — files >= checkpoint, all good. The "ERROR on TICKER" log lines were save-then-print-crash events; data WAS persisted.
- **Severity:** HIGH at the moment — Phase 1A blockers re-emerged. After the BG died, only 1 of 7 endpoints actually progressed (congressional 1921/1937). The 6 remaining (insider/institutional/gov_contracts/lobbying/wallstreetbets/wikipedia) are STILL at 509 baseline. INV-003 (Quiver re-prefetch) re-opens.
- **Status:** RESOLVING THIS COMMIT
- **Next action:**
  - Bulk-replace ALL Unicode chars in print statements with ASCII labels (DONE this commit)
  - Generalize regression test from runner-only (`test_phase1a_runner_no_unicode.py`) to all prefetch/refresh/build/smoke scripts (`test_prefetch_scripts_no_unicode.py` — DONE this commit)
  - Re-launch BG to resume from checkpoint state (congressional ~done; will progress to insider/institutional/gov_contracts/lobbying/wallstreetbets; wikipedia ghost will skip per INV-013)
  - Estimated remaining wall time: ~6 endpoints × 1428 tickers × 1.2s = ~2.9 hours
- **Joint:** P1.runner regression (commit `8d2641edf`) — same bug class but narrower scope (didn't cover prefetch scripts); L150 (pyramid dimension-coverage gap meta-pattern: when one script has a regression test, sibling scripts in same role need the same coverage); CHECKLIST #75 strict pyramid (this fix MUST run pyramid before push); CHECKLIST #74 (this INV entry in same commit as the fix); INV-013 (wikipedia ghost — same BG); INV-003 (Quiver re-prefetch — re-opens).

---

*Last updated: 2026-05-07 evening (Pass 53 Day-9 v8h ongoing)*
