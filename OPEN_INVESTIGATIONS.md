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

- **Discovered:** 2026-05-07 (Pass 53 Day-9 v8h Tier C3 CFTC prefetch)
- **Observation:** Tried to fetch CFTC TFF positioning for "10-YEAR U.S. TREASURY NOTES" / "5-YEAR" / "2-YEAR" / "ULTRA U.S. TREASURY BONDS" / "E-MINI DJIA (X $5)" — all returned 0 rows. Other contracts (e-mini SP500, NDX, RUT, VIX, fed funds, currencies, commodities) all worked fine.
- **Why not blocking:** 13/18 contracts fetched successfully. Treasury futures positioning is nice-to-have for rate-driven strategies; we have rate level/spread data from FRED (DGS10/DGS5/DGS2/T10Y2Y).
- **Status:** open — investigate
- **Next action:** query CFTC Socrata API without contract filter for one date to see how Treasury contracts are actually named in the dataset; update `prefetch_cftc_cot.py` CONTRACTS list with correct names; re-run.

---

*Last updated: 2026-05-07 evening (Pass 53 Day-9 v8h ongoing)*
