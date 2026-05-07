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
- **Why not blocking:** Small 5-ticker test with 77 trades. At Phase 1A scale (1937 tickers, expected 50-200K trades) the pattern most likely won't replicate. May simply be that these 5 tickers (AAPL/JPM/XOM/TSLA/SPY) only had screen-passing setups during neutral periods.
- **Status:** open
- **Next action:** if Phase 1A baseline run also shows trades-only-in-neutral, this is a real bug — investigate engine code path that records `regime_at_entry` on OpenTrade vs ClosedTrade.

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

*Last updated: 2026-05-07 (Pass 53 Day-9 v8h)*
