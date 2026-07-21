# B1339 — Free local diagnostics: COIN activation semantics + flag_bull_long silent-drop (corrects B1333)

**Council 366 · 2026-07-21 · owner "review Fable feedback + implement all, approve all" · engine unchanged since batch-1 SHA e846b6d2c (verified: `git diff --stat e846b6d2c HEAD -- backtest/` = 4 new test files only) so all traces below are bit-equivalent to the frozen tar. Zero spend.**

Resolves the two owner-gated FREE items from Fable's B1334 review before batch 2. Every claim is tagged EXECUTED / DERIVED.

---

## 1. COIN "anomaly" — RESOLVED: annual year-start PIT membership (NOT a bug, NOT warmup)

**Fable hypothesis (B1334):** "engine computes indicators only from membership start => ~150-bar warmup => 2026-01" and/or T1c membership should count. **DISPROVEN.**

**EXECUTED evidence:**
- T1a membership dates (CSV): COIN `added_date=2025-05-19`, SNDK `added_date=2025-11-28`, MU/WDC `added_date=NaN` (always-active).
- OHLCV cache: COIN = **1255 rows** (full window, = MU) — so it is NOT a warmup/data-availability limit; indicators compute fine.
- `get_sp500_constituents_pit()` at each year-start:
  | year-start | COIN | SNDK | MU | WDC |
  |---|---|---|---|---|
  | 2022–2025-01-01 | False | False | True | True |
  | 2026-01-01 | **True** | **True** | True | True |
- First-trade dates (batch-1 trade_log): COIN `2026-01-02`, SNDK `2026-01-02`, MU/WDC/AAPL/... `2022-05-05`.

**Root cause (EXECUTED, backtest.py:393–418):** the engine builds `_annual_liquid[year]` from PIT S&P membership snapshotted at **year-start**. A T1a-master ticker is eligible in year Y only if it was an S&P member on Y-01-01. COIN (added 2025-05-19) and SNDK (added 2025-11-28) are both False at 2025-01-01, True at 2026-01-01 → both become eligible only from 2026 → **both first-trade 2026-01-02**. This is why two tickers with very different add-dates and data depth land on the identical first-trade date — the common cause is the annual snapshot, not warmup.

**Verdict:** PIT-SAFE (never trades a non-member; no lookahead). **Batch 1 is VALID on this axis — no re-run needed.** The owner's specific tickers are correct: MU/WDC full-window; SNDK correctly limited to its post-membership window.

**Genuine limitation surfaced (owner decision, NOT a batch-1 blocker):** annual (year-start) granularity means a mid-year entrant waits until the next Jan to become eligible, losing up to ~11 months of legitimate in-membership trading (COIN loses ~May–Dec 2025). This systematically under-counts the ~111 mid-window T1a entrants — conservatively. → ticket **S6-B1339-PIT-GRANULARITY** (options: keep annual for speed / refine to monthly / refine to daily). Does not affect always-active tickers (all 20 batch-2 tickers are always-active — zero exposure).

---

## 2. flag_bull_long silent-drop — B1333 Cat-2 RCA is WRONG; true mechanism identified

**B1333 claim:** "flag_bull_long fired 140× but ALL 140 fire-bars were red candles → dropped by the Batch-263 directional-confirmation gate (close_above_open)." **Fable doubted it (p≈2⁻¹⁴⁰). CONFIRMED WRONG.**

**EXECUTED evidence:**
- raw fires (batch-1 `raw_signal_fires.*.csv`, summed across 16 workers): flag_bull_long = **140** (matches B1333); golden_cross_50_200=34, flag_bull_retest=39, smc_mitigation=28.
- `skipped_trades.csv`: flag_bull_long = **0 rows** (never reached engine-level skip logging — the confirmation-gate `continue` at screener.py:8803 is silent, not logged).
- Independent trace (MU/NVDA/WDC/AAPL, 1003 days each, correct producer merge `compute_all_signals` + `compute_all_chart_patterns`): flag_bull_broke∧ema200 fires **97×** → confirmation gate **59 PASS (green)** / **38 DROP (red)**. So the gate drops **~39%, not 100%.** "All 140 red" is false.
- 9 chart_pattern strategies DID trade in batch 1 (triangle_ascending_long, double_bottom_long, cup_and_handle_long, …) → chart signals ARE merged; not a systemic engine bug.
- cube-isolation (batch-1 mode) BYPASSES the candidate cap (backtest.py:1763: `candidates if self.cube_isolation else candidates[:self.max_cands]`) → in isolation "every valid signal opens a trade." So 0 trades ⇒ **0 gate-surviving candidates in the actual run.**

**The tension (the real finding):** 140 raw fires, my trace says ~60% of flag_bull_broke bars are green (should survive the gate), yet the run produced 0 gate-survivors. The raw counter (screener.py:8793) and the trade-generation pass are therefore **not the same evaluation set** — the "140" counts fires at a point whose relationship to candidate-eligible fires is unverified (per-worker, pre-gate, possibly a different pass). **This is exactly the counter-semantics trap (CHECKLIST #162): B1333 equated raw-fires with tradeable-signals and built a false mechanism on top.**

**Verdict:** B1333 Cat-2 = **UNVERIFIED/WRONG, retracted.** flag_bull_long's 0-trades is a coverage/diagnostic question (raw-counter semantics + 10-ticker sparsity), **NOT a data-integrity bug producing wrong trades.** Batch 1's TRADED strategies are valid; the SILENT set is a measurement question that re-opens at larger scale. **Batch 1 does not need a re-run on this basis.**

**Remaining (needs a diagnostic build, not a static trace):** the exact 140→0 within the real screen_instrument pass. Requires per-stage drop instrumentation in the engine — which would change code_sha, so it goes in a **diagnostic-only build (separate SHA, never merged with the frozen sequence)**, or is deferred until silent strategies are re-measured at full universe. → ticket **S6-B1339-DROP-LOGGING** (add confirmation-gate + counter-point drop logging; runs AFTER the frozen sequence or on a diagnostic SHA).

---

## 3. Disposition of remaining Fable B1334 / B1332 flags

| Item | Status |
|---|---|
| B1334 #1 freeze mechanism | SHIPPED B1336 (--sha / --expect-sha / --expected-sha + tests) |
| B1334 #2 Cat-2 RCA wrong | RESOLVED here (retracted + corrected) |
| B1334 #3 smoke HEAD-compare | SHIPPED B1336 (--expected-sha) |
| B1334 #4 batch-1 outputs uncommitted | SHIPPED B1337 (output_batches/batch_1/) |
| B1334 #5 cost model unverified | SHIPPED B1339 (cost_projection.py: measure-and-project + budget hard-stop; honestly refuses to project on 1 point) |
| B1334 #6 stale premerge-RCA memory | RESOLVED B1339 (memory updated: $1 cross-check MOOT for same-platform/same-SHA merges) |
| B1334 seq (5) batch-2 roster | SHIPPED B1339 (20 sector-stratified, disjoint, all always-active → zero PIT-granularity exposure) |
| B1332 (a) earnings_blackout worst-DD | ticket S6-B1332-EARNINGS-DD (post-R5 exit analysis; owner "if exit bad, remove post-R5" — retain) |
| B1332 (b) max_drawdown_pct additive-pp | ticket S6-DD-UNITS (decide additive vs compounded before winners analysis) |
| B1332 (c) portfolio return meaningless in isolation | ticket S6-ISO-PORTFOLIO-SUPPRESS (caveat/suppress those merge-summary fields) |
| B1332 (d) small-sample win=1.0/PF=999 cells | monitor at full scale (look-ahead check) |
| SPY benchmark traded (244) | ticket S6-SPY-BENCHMARK-EXCLUDE (SPY is the benchmark, not a strategy universe member; decide exclude-from-tradeable vs benign) |

---

## Batch-2 readiness (all pre-conditions now met)

- Roster: 20 tickers, sector-stratified (~2/11 GICS), disjoint from batch 1, **all always-active** (no COIN-class annual-PIT exposure). `output_batches/batch_2_roster.json`.
- Manifest: `output_batches/run_manifest_batch2.json` (frozen_sha e846b6d2c, isolation true, nyse_mcal) → gates through prelaunch_gate.
- Cost: batch-1 measured 18.0 min engine / $0.30 for 10 tkr. Model needs batch-2 as the 2nd point before projecting the ladder (honest — refuses a 1-point guess). Spent $0.30 / $50.
- **Still owner-gated: explicit typed go for batch 2** (feedback_no_auto_launch_batch_b). Batch 2 becomes the 2nd cost data point.
