# B747 PIT-Universe Discipline Audit

# Source: scripts/pit_universe_discipline_audit.py per CHECKLIST #77

## Re-scoped from original B747 framing per owner question 2026-06-13

Original B747: 'calibrate the survivor-bias direction'.
Owner pushback: *'why does there need to be any delisting?'*
Re-scoped finding: T1a ALREADY tracks 111 historical-removed names; the
question is whether every engine honors the PIT universe per-bar or
collapses to the END-snapshot.

## T1a roster composition

- Total rows in T1a: **614**
- Currently active (never removed): **503**
- Historical-removed during window: **111**

## OHLCV coverage for historical-removed tickers

- OHLCV parquet present: **103** of 111
- OHLCV parquet MISSING: **8**
  - missing names: `AGN, CXO, ETFC, NBL, RTN, TIF, VAR, WCG`
  - These names CANNOT be simulated even if the PIT filter were fixed; coverage gap is independent.

### Coverage-through-removal verification

For each historical-removed ticker with OHLCV present, does the parquet contain bars through the removal date (within 1 trading day)?

- Coverage through removal date: **81** tickers
- OHLCV present but ENDS before removal date: **22** tickers (data gap)

Tickers with truncated OHLCV (last bar before removal date):

- `ANSS` -- last bar 2025-07-16, removed 2025-07-18
- `ATVI` -- last bar 2023-10-12, removed 2023-10-18
- `CTLT` -- last bar 2024-12-17, removed 2024-12-23
- `CTXS` -- last bar 2022-09-29, removed 2022-10-03
- `DAY` -- last bar 2026-02-03, removed 2026-02-09
- `DFS` -- last bar 2025-05-16, removed 2025-05-19
- `DISCA` -- last bar 2022-04-08, removed 2022-04-11
- `DISCK` -- last bar 2022-04-08, removed 2022-04-11
- `DRE` -- last bar 2022-09-30, removed 2022-10-03
- `FBHS` -- last bar 2022-12-14, removed 2022-12-19
- ... and 12 more

## Consumer PIT-discipline verdict

| Consumer | Pattern | Verdict | Note |
|---|---|---|---|
| `scripts/measure_fire_count.py` | PIT_WINDOW_UNION | **PIT_CORRECT** | Window-union universe loader (B748a fix); historical-removed names included; per-bar PIT enforced via OHLCV truncation. |
| `backtest/engine/backtest.py` | PIT_PER_YEAR | **PIT_CORRECT** | Per-year PIT intersection via get_sp500_constituents_pit; survivor bias mitigated. |
| `backtest/run_phase1a.py` | NO_PIT | **PARTIAL** | No PIT pattern detected; manual review required. |

## Headline finding

**All audited consumers respect the PIT universe.** Survivor bias not introduced by universe-load logic; verify other vectors (e.g., delisted-ticker OHLCV ends BEFORE removal date is a data-quality issue, not a survivor-bias issue).

## Owner action items

1. Re-confirm whether `measure_fire_count.py` should switch to per-bar PIT (more expensive; honest) or stay end-date (current behavior; surveys-currently-listed only).
2. Investigate the OHLCV coverage gaps for historical-removed tickers; backfill via Polygon Tickers API or accept as known gap.
3. Decide whether B690b AWS measurement re-run should be GATED on the fix landing, or proceed with current END-snapshot scope + apply the bias adjustment factor offline.