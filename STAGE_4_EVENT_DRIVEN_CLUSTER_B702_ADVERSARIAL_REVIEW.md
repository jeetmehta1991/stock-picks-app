# B702 — Event-Driven Cluster: Adversarial Review of External Reviewer's Proposal

**Owner directive (2026-06-11):**
> "Dont trust blindly. Do another review of the suggestions and provide your own adverserial feedback against current status. Then provide an implementation plan."

**Author:** Claude (per owner directive — adversarial counter-position, not endorsement)
**Status:** Source-verified against `backtest/signals/pead.py`, `backtest/engine/backtest.py:_process_day`, `backtest/signals/screener.py:screen_instrument`, `data_prefetch/polygon/financials/*.parquet` schema, `data_prefetch/finnhub/earnings/*.parquet` schema, `data_prefetch/finnhub/calendar_earnings.parquet` schema (1500 rows).
**Discipline:** Verify each reviewer claim against actual code/cache state BEFORE accepting. Same `feedback_audit_recommendations_against_existing_directives` + `feedback_walk_step3_must_read_producer_source` discipline applied to chart-pattern cluster (B617/B699).

---

## 0. Scope of Reviewer's Proposal (recap)

External reviewer proposed for the event-driven cluster (PEAD EV-1/EV-2 + buyback EV-5/EV-7 + acquisition EV-6 + pre-FOMC drift + earnings-window strategies):
1. **Three PIT hazards** for earnings data: **H1** announcement-date re-anchor, **H2** value-restatement (bitemporal), **H3** same-bar gap contamination.
2. **Phase-0 black-box producer audit** (same harness as B699/B700 chart-pattern cluster — `earnings_feed_pit_audit.py` + 3-producer validator).
3. **SUE replacement** for current YoY-growth surprise proxy.
4. **Gap-conditioning** on PEAD entries (skip same-bar large gap).
5. **Pre-FOMC drift** strategy refactor (Lucca-Moench-style, beta-conditioned, Cieslak-Pang yield-curve gating).
6. **EV-3 deletion criticism** — reviewer disagrees with B682 delete of `strat_pead_long_high_yoy_growth_only`.
7. **Cross-cluster effective hypothesis count (Pattern N)** Bonferroni inflation check.
8. **Two reviewer-supplied tool files** — content not in current context; owner to re-paste for me to save.

---

## 1. Adversarial Verdicts by Claim (source-verified, not pattern-matched)

### Claim H1 — Announcement-date re-anchor hazard
**Reviewer position:** PEAD producer is exposed to vendor re-stamping the announcement date on later pulls; current run could see a different date than a future re-run, producing different `days_since_last_earnings` and `within_pead_window` values.

**Source-verified state:**
- `pead.py:165` calls `load_quarterly_eps(ticker)` which reads `data_prefetch/polygon/financials/<TICKER>.parquet`.
- `load_quarterly_eps` at lines 121-122 uses `r["filing_date"]` — this is the **Polygon `filing_date` field**, sourced from SEC EDGAR submission timestamps (per Polygon Financials API documentation).
- SEC EDGAR filings are **immutable post-filing**: the original accession-number filing-date remains unchanged forever; restatements appear as NEW filings with new accession numbers and new filing dates.
- `data_prefetch/finnhub/calendar_earnings.parquet` (1500 rows; has `date` column) — this **IS** the type of feed the reviewer's H1 hazard targets. But `grep finnhub backtest/signals/*.py` returns **NO MATCHES** — Finnhub data is consumed by zero signal-producers; the parquet exists from a historical prefetch experiment.

**Adversarial verdict:** **H1 LARGELY REFUTED for current event-driven producers.** The hazard targets a cache the producers don't read. The hazard would become real only if a future producer wires in Finnhub's calendar feed, OR if Polygon began retroactively rewriting filing-dates (unlikely; would also break SEC's audit chain).

**Caveat I owe the reviewer:** if Polygon's prefetch script (`scripts/prefetch_polygon_financials.py` per repo layout) ever pulls a different `filing_date` for a given accession on later re-pulls (vendor data-quality bug, not SEC semantic change), the producer **could** experience H1 via the prefetch cache replacing prior values. The audit-harness validation against ground truth (H1 test producer that re-anchors a single quarter) **is still valuable** for catching that vendor-side regression. Endorse Phase-0 audit but downgrade the EXPECTED hit rate.

---

### Claim H2 — Value restatement hazard (bitemporal)
**Reviewer position:** Producer could fire on a restated EPS value that wasn't known at original announcement, biasing PEAD signal toward restated-up firms.

**Source-verified state:**
- `data_prefetch/polygon/financials/<TICKER>.parquet` schema (sampled via `pd.read_parquet`): one row per filing with `financials_json` containing a single set of values per fiscal_period. **No restatement history is cached** — the prefetch keeps the most recent value seen, overwriting prior values.
- This means: if Polygon re-pulled a restated value, the prefetch cache would already contain only the restated value. The producer would still pick it up — but only because the prefetch (not the producer) decided to overwrite. The producer has no path to peek at a value it doesn't know about.
- `_safe_eps` at `pead.py:41-71` extracts a single `diluted_earnings_per_share.value`. No "as_of_known_from" / "known_from_date" key exists in the JSON schema we cache.

**Adversarial verdict:** **H2 IS A PREFETCH-LEVEL HAZARD, NOT A PRODUCER-LEVEL HAZARD.** The reviewer's tool is targeting the wrong layer. The right fix is at the prefetch boundary — either (a) snapshot prefetch results at fixed cadence and never overwrite, or (b) accept that backtest EPS reflects most-recent-known-value (typical industry practice; explicitly trade off PIT-purity for cache simplicity). The producer audit harness will not detect H2 because the input cache is already collapsed.

**What audit harness CAN catch at H2 layer:** a producer bug where the YoY comparison reads BOTH current and prior quarter from `most_recent` instead of from a `same-quarter-prior-year` lookup. That's a different failure mode (logical, not bitemporal). The B312-PEAD fix at `pead.py:201-206` already covers this — verified via `prior_year_match.empty` guard.

---

### Claim H3 — Same-bar gap contamination
**Reviewer position:** PEAD producer's `earnings_announcement_return = close[T+1] / close[T-1] - 1` could be computed on the announcement bar itself (T) using future bars, producing a look-ahead bias.

**Source-verified state:** This is the **most rigorously testable** of the three. Trace:
1. `backtest/engine/backtest.py:824` — `sliced = df[df.index.date <= as_of]` slices OHLCV to ≤ as_of BEFORE the per-day signal compute.
2. `screener.py:6893` — `pead = compute_pead_signals(ticker, df, as_of)` passes the pre-sliced df.
3. `pead.py:247-253` — `if pos + 1 < len(ohlcv_df): post_close = ohlcv_df["close"].iloc[pos + 1]`.
4. **Implication:** if `as_of == filing_date`, then `pos = len(ohlcv_df) - 1`, so `pos + 1 == len(ohlcv_df)`, the guard fails, `ann_ret` is not set, `pead_positive_surprise` is not set, the strategy cannot fire.
5. **First fire-eligible bar is as_of == filing_date + 1** (one trading day after filing), at which point `close[T+1]` is the close of `as_of` itself — already-realized, not future.
6. **Entry convention:** the engine fires the strategy at close[as_of] and executes the entry at open[as_of+1] (next-bar-open). So there is a SECOND bar of buffer between signal computation and trade entry.

**Adversarial verdict:** **H3 STRUCTURALLY REFUTED at producer level.** The engine's pre-slice + the producer's `pos + 1 < len(ohlcv_df)` guard + next-bar-open execution jointly prevent lookahead. The reviewer's H3 hazard model assumes a different engine call convention (full-history df + same-bar execution) that this engine does not use.

**What CAN still go wrong (residual concerns):**
- (a) **`filing_date` interpretation drift**: Polygon's `filing_date` is SEC EDGAR filing date, typically 1-3 trading days AFTER the earnings press release. The "announcement-day return" misnomer is real — the metric actually measures a return centered on the SEC filing, not the press release. This is a **measurement-quality issue**, not lookahead. Real PEAD literature (Bernard-Thomas 1989) uses the actual press-release date, which is closer to Finnhub's `date` field (but we established Finnhub is not consumed).
- (b) **Reanalysis with full-history df** (if a researcher ever calls `compute_pead_signals` outside the engine with an un-sliced df): would re-introduce H3 risk. The function's signature does not enforce slicing — it's a CALLER contract, not a producer-internal guarantee.

**Concrete refinement to reviewer's H3 audit:** the harness should construct a callable wrapper that passes pre-sliced OHLCV (matching the engine's convention) AND a wrapper that passes full OHLCV — and verify the producer's output is identical in both cases. If they differ, the producer is implicitly relying on the engine to slice — fragile.

---

### Claim — SUE replacement for current YoY-growth surprise proxy
**Reviewer position:** YoY EPS growth is a weaker sorting variable than Standardized Unexpected Earnings (SUE) — the Bernard-Thomas canonical signal. Replace `earnings_eps_yoy_growth` with `sue_zscore` computed against analyst-consensus estimates.

**Source-verified state:**
- `pead.py:18-25` explicitly acknowledges this: "Polygon Stocks Starter does NOT provide consensus EPS estimates (would be needed for the SUE z-score formulation), this module uses the Bernard-Thomas variant which only requires reported EPS."
- `data_prefetch/finnhub/calendar_earnings.parquet` (1500 rows) HAS `epsEstimate` column.
- `data_prefetch/finnhub/earnings/<TICKER>.parquet` (4 rows per ticker) HAS `estimate` column.

**Adversarial verdict:** **CORRECT IN PRINCIPLE — INFRA-COST UNDERSTATED.** SUE is canonical; the swap is theoretically motivated. But the reviewer doesn't price the infra cost:
1. Finnhub's `calendar_earnings.parquet` is 1500 rows — that's a **point-in-time CALENDAR snapshot**, not a historical estimate timeline. To compute historical SUE, we need **per-quarter-end consensus snapshots** going back to the start of the backtest window (2020). Finnhub free tier ≠ that.
2. Refinitiv I/B/E/S or Zacks consensus is the institutional standard. Polygon Stocks Starter ≠ that. Polygon Advanced (paid tier) ≠ that either.
3. Cross-sectional decile-ranking (`xs_sue_decile`) requires per-day full-universe lift via `cross_sectional.py` — new producer, new tests, new prefetch.
4. The current YoY-growth proxy has the documented Bernard-Thomas-variant precedent (Garfinkel-Hribar-Hsiao 2024) — non-canonical but published-defensible.

**My counter-position:** **SUE is a tier-3 priority, not tier-1.** First validate that the current YoY-proxy fires at the rate it should (B660 measurement; in flight on AWS) and produces empirical alpha in the Stage 5 cube. If the YoY proxy passes Phase 1A-α at sufficient fire-count, the marginal SUE benefit is small and the infra cost large — defer. If the YoY proxy fails for measurement reasons (too few fires, too high noise), THEN reconsider SUE with the explicit infra-spend tradeoff to owner.

---

### Claim — Gap-conditioning (skip large same-bar gap on PEAD entries)
**Reviewer position:** Add `gap_pct < threshold` gate to PEAD strategies; large gaps already absorbed the drift, so post-gap entry has no edge.

**Source-verified state:**
- `screener.py:6700-6708` — `_strategy_gap_check` (BUG-060) already enforces gap-rejection on entry **independently of strategy**. Generic ATR-gap-fraction cap is applied universe-wide (multiplier configured per direction).
- The reviewer's proposal is to add a SECOND, PEAD-specific gap gate on top of the existing generic one.

**Adversarial verdict:** **PRESENTED AS FACT, NOT EVIDENCE-BACKED.** PEAD-specific gap-conditioning is mixed in the literature: some research (e.g., Brandt et al. 2008, "Earnings Announcement Risk") finds that gap-up earnings days have STRONGER drift; others (e.g., Hou et al. 2011, "Earnings Surprises") find weaker. The reviewer asserts the negative-correlation case without citation.

**My counter-position:** **TEST FIRST, REFACTOR SECOND.** Use the existing `conditional_add_test` confronting-test harness (B701 same format as `run_b700_candle_diagnostics.py` Diagnostic 2) to test whether `gap_pct < X` AND-ed with current PEAD gates lifts FT. Same `train through 2023 / test 2024+` split. If lift is positive and significant, codify; if neutral or negative, REJECT and document the negative result. Do not refactor on reviewer's prior. Tickets:
- **EV-GAP-CONDITIONING-TEST** — confronting test for `gap_pct < 0.02` AND-required on `strat_pead_long`.
- **EV-GAP-CONDITIONING-TEST-SHORT** — same for `strat_pead_short` (sign-symmetric; check separately).

---

### Claim — Pre-FOMC drift strategy refactor
**Reviewer position:** Refactor `pre_fomc_drift_long` to use Lucca-Moench beta conditioning + Cieslak-Pang 2024 yield-curve gating.

**Source-verified state (B702 same-turn grep `screener.py:2927-2966`):**
- `strat_pre_fomc_long_sleeve` exists (B224): gate = `pre_fomc_d1 AND price_above_ema_200`. No beta-conditioning.
- `strat_pre_fomc_quality_momentum_long` exists (B224): gate = `pre_fomc_d1 AND xs_momentum_top_decile AND price_above_ema_200`. No beta-conditioning.
- Producer: `pre_fomc_d1` flags the day BEFORE FOMC announcement.

**Reviewer's "refactor" is actually ADDITIVE** — adds beta-conditioning to an existing strategy family. Reframing matters: not a fix to broken code, an extension.

**Adversarial verdict:** **REVIEWER UNDERPLAYS HAZARD.** Lucca-Moench (2015 *Journal of Finance*) documents pre-FOMC drift **at the SPX index level** — ~50bps in the 24h pre-FOMC window. Single-stock pre-FOMC drift is **much thinner** literature (Bernile-Hu-Tang 2016 explores cross-section but finds heterogeneous loadings). Adding a beta filter (high-beta = expected to capture more of the index drift) is a **plausible deduction**, but it is not a documented stand-alone alpha source for single stocks. Cieslak-Pang 2024 yield-curve conditioning further narrows the regime to ~10-15% of FOMC events — small effective sample.

**My counter-position:** **single-stock pre-FOMC drift may have no edge regardless of beta-conditioning. The micro-strategy risks fitting an index-level effect onto single tickers.** Two-step gate before any refactor:
1. **Confronting test #1**: SPY-level pre-FOMC drift on 2020-2026 — does the canonical Lucca-Moench effect SURVIVE in the post-2015 sample (Mueller-Tahbaz-Salehi 2017 found it weakened)? If SPY-level effect is dead, single-stock derivative is dead a fortiori.
2. **Confronting test #2**: single-stock per-beta-decile pre-FOMC drift on 2020-2026 — does high-beta single-stock pre-FOMC drift exceed SPY-level drift?

Only if BOTH (1) and (2) survive does the refactor cost (beta-computation infra, Cieslak-Pang yield-curve conditioning) earn its budget. Tickets:
- **EV-FOMC-SPY-CONFIRMATION** — SPY pre-FOMC return analysis 2020-2026 vs Lucca-Moench 1994-2011 baseline.
- **EV-FOMC-SINGLE-STOCK-BETA-DECILE** — per-decile beta conditioning analysis on T1a universe pre-FOMC.

---

### Claim — EV-3 deletion criticism
**Reviewer position:** B682 deleted `strat_pead_long_high_yoy_growth_only` (EV-3). Reviewer disagrees — argues EV-3 captures a "better population" (high-YoY-growth firms) than EV-1.

**Source-verified state:**
- B682 commit history in CLAUDE.md: "EV-3 strat_pead_long_high_yoy_growth_only DELETED per Pattern W deterministic-subset of EV-1".
- Pattern W is documented in `feedback_audit_recommendations_against_existing_directives.md`: when strategy B fires IFF strategy A fires AND additional condition C, B is a DETERMINISTIC SUBSET of A on axis C; deletion is justified because every B trade is already an A trade, no marginal information.
- For EV-3 vs EV-1: EV-1 fires when `within_pead_window AND pead_positive_surprise`. EV-3 fires when `within_pead_window AND yoy_surprise_high`. Since `pead_positive_surprise = (yoy_growth > 0 AND ann_ret > 0.02)`, and `yoy_surprise_high = (yoy_growth > 0.X)` for some X > 0, the subset claim is: every EV-3 fire is a fire of EV-1 IFF yoy_surprise_high implies pead_positive_surprise. **This is NOT mechanically true** — EV-3 doesn't require `ann_ret > 0.02`. So EV-3 can fire when EV-1 doesn't.

**Adversarial verdict:** **REVIEWER'S CRITICISM IS PARTIALLY VALID — B682 DELETION RATIONALE WAS LOGICALLY INCOMPLETE.**

**Source verification (B702 same-turn grep):** `screener.py:3856-3896` deletion comment EXPLICITLY ACKNOWLEDGES the asymmetry:
> "EV-1's ann_ret > +2% gate adds a narrowing axis EV-3 lacks, but the YoY-axis subset relationship holds."

The comment then concludes: "Cube replay would produce near-identical per-trade Sharpe by construction."

**My critique of the rationale:** "YoY-axis subset relationship holds" → TRUE (yoy >= 5% implies yoy > 0). But that establishes only that EV-3's YoY values are a subset of EV-1's YoY values, NOT that EV-3's FIRE EVENTS are a subset of EV-1's FIRE EVENTS. Because EV-1 requires the ADDITIONAL `ann_ret > +2%` gate, EV-3 fires include cases where EV-1 doesn't fire (high yoy_growth firms whose announcement-day move was weak).

**The "Cube replay would produce near-identical per-trade Sharpe by construction" claim is unverified.** It's true only if (a) the EV-3 population is dominated by cases that EV-1 also fires on (high yoy AND ann_ret > 0.02 simultaneously), OR (b) the per-trade Sharpe is invariant to the ann_ret axis. Neither was tested at B682.

**However, my counter-counter-position:** the deletion may be EMPIRICALLY defensible even if LOGICALLY incomplete. The B682 owner-approval was made KNOWING the asymmetry was acknowledged in the comment. The implicit assumption is that high YoY-growth firms tend to also have positive announcement-day reactions (i.e., yoy_growth and ann_ret are positively correlated post-earnings) — which is a documented PEAD finding (Bernard-Thomas 1989: the surprise sign predicts the announcement-day move). If the correlation is strong, EV-3 ≈ EV-1 ∩ {yoy >= 5%}, a near-subset that the cube can sweep as a YoY-threshold parameter on EV-1.

**Resolution path:** This is an EMPIRICAL question that the B660 in-flight run (which still has EV-3 in its strategy list as of pre-deletion state? — verify with run-config) can settle. Or a 1-day query against the existing PEAD signal cache.

**Tickets for owner triage:**
- **EV-3-DELETION-EMPIRICAL-VERIFY** — measure correlation between yoy_surprise_high (yoy >= 5%) and pead_positive_surprise (yoy > 0 AND ann_ret > 0.02) on T1a 2020-2026. If correlation >= 0.85, B682 deletion is empirically defensible and stands. If correlation < 0.7, the deletion removed a distinct population — recommend revert + re-register EV-3/EV-4.
- **EV-3-DELETION-RATIONALE-CORRECT** — IF revert needed, also amend the deletion comment to remove "deterministic strict subset" framing (use "near-subset under empirical correlation" if the data supports it).

**Reviewer wins on the logical critique. Owner-direction needed on empirical verification + possible revert.**

---

### Claim — Phase 0 producer audit (black-box harness, same as B699/B700)
**Reviewer position:** Run an `earnings_feed_pit_audit.py` harness — three reference producers (clean / restated / repaint-prone) and verify the auditor classifies them correctly.

**Source-verified state:** The harness exists in concept (reviewer provided the file content earlier; not in current context). The B699/B700 chart-pattern parallel **worked very well** — it produced concrete REFUTATIONS (CP-2 not PHANTOM) and concrete CONFIRMATIONS (CP-1 MISS) that re-ordered owner's priority queue.

**Adversarial verdict:** **ENDORSED with scoped expectation adjustment.** Even though my H1/H2/H3 source-verification found the structural exposure weaker than the reviewer asserts (H2 wrong layer; H3 structurally refuted), the audit harness still has value because:
1. It catches **regressions** if a future producer change re-introduces the hazards (e.g., someone removes the pre-slice in the engine; someone wires Finnhub).
2. It catches **producer-internal logical bugs** that the source-read inspection doesn't easily find (e.g., the YoY-comparison bug class).
3. It provides a **published-defensible PIT-correctness audit trail** when external researchers ask "how do you know your PEAD signal isn't lookahead?"

The harness is worth shipping; the EXPECTED hit-rate I project is lower than the reviewer implies. Approve.

---

### Claim — Cross-cluster effective hypothesis count (Pattern N) Bonferroni inflation
**Reviewer position:** With chart-pattern cluster (17 keys) + candle cluster + event-driven cluster + future clusters, the effective hypothesis count for Stage 5 cube significance testing is much higher than the strategy count — collinear strategies inflate naive denominators.

**Adversarial verdict:** **ENDORSED IN FULL.** This is the right discipline, and it's been queued in EXECUTION_QUEUE as **S5-MULTIPLE-TESTING-CORRECTION** (per B641 ticket). The reviewer is correct that the cross-cluster denominator matters; this is a Stage 5 cube concern, not a Stage 4 walk concern. Move to cube-side methodology. No Stage 4 batch action.

---

## 2. Summary of Adversarial Verdicts

| Claim | Reviewer assertion | My verified verdict | Action |
|---|---|---|---|
| H1 date re-anchor | High hazard | LARGELY REFUTED (wrong cache) | Endorse audit-harness for regression-guard; downgrade priority |
| H2 value restatement | High hazard | WRONG LAYER (prefetch, not producer) | Move concern to prefetch boundary discussion |
| H3 gap contamination | High hazard | STRUCTURALLY REFUTED (engine pre-slice + guard + next-bar-open) | Audit harness STILL catches regressions; keep |
| SUE replacement | High priority | CORRECT IN PRINCIPLE, INFRA-EXPENSIVE | Tier-3 defer; revisit if YoY-proxy fails cube |
| Gap-conditioning | Endorsed as fact | NOT EVIDENCE-BACKED | Confronting test BEFORE refactor (per B701 discipline) |
| Pre-FOMC refactor | Endorsed | UNDERPLAYED HAZARD (no single-stock alpha proven) | 2-step confronting test BEFORE refactor |
| EV-3 deletion criticism | Reviewer disagrees with B682 | POSSIBLY CORRECT — needs source-grep verification | HIGHEST PRIORITY — verify EV-3 implementation |
| Phase-0 producer audit | High priority | ENDORSED for regression-guard + audit trail | Approve, ship harness |
| Cross-cluster Pattern N | Endorsed | ENDORSED IN FULL | Already queued as S5-MULTIPLE-TESTING-CORRECTION |

---

## 3. Implementation Plan

### Phase -1: Source-read verification gate (BEFORE reviewer's Phase 0)
Per `feedback_walk_step3_must_read_producer_source.md` — verify producer/code reality before tool-building.

**Tickets (run in this turn / next turn):**
1. **EV-3-DELETION-VERIFY** — grep B682 commit + read actual EV-3 implementation (`strat_pead_long_high_yoy_growth_only`) at the deletion point. Verify whether `ann_ret > 0.02` was part of EV-3's gate. If yes → deletion stands; if no → reviewer wins, queue revert ticket.
2. **EV-FOMC-STRATEGY-AUDIT** — grep `strat_pre_fomc` and related (does it exist? what does it fire on? is beta computed?). Verify the strategy state the reviewer assumes.
3. **EV-PREFETCH-IMMUTABILITY-AUDIT** — does `scripts/prefetch_polygon_financials.py` overwrite or append? Does it ever pull a different `filing_date` for the same accession-number? (Tests vendor-side H1 residual.)

### Phase 0: Black-box producer audit (reviewer's harness + my scope refinements)
Once the 2 tool files are re-pasted by owner:
4. **EV-PHASE-0-HARNESS-SAVE** — save `earnings_feed_pit_audit.py` + `validate_earnings_feed_pit_audit.py` to `scripts/`.
5. **EV-PHASE-0-HARNESS-VALIDATE** — run validator; same 3/3 PASS gate as B699 chart-pattern validator earned trust before deployment.
6. **EV-PHASE-0-PRODUCTION-AUDIT** — run harness against `compute_pead_signals` for each of (within_pead_window, pead_positive_surprise, pead_negative_surprise, earnings_eps_yoy_growth, earnings_announcement_return) under three OHLCV-slice conventions: (a) engine-style pre-sliced, (b) full-history un-sliced, (c) full-history with simulated forward-bar peek. Verify (a) is CLEAN, (b) and (c) match (a) OR are flagged.
7. **EV-PHASE-0-PRODUCER-COMMENT-PIN** — pin the slicing assumption in `pead.py` docstring as a CALLER CONTRACT, so future callers don't violate it.

### Phase 1: Confronting tests (BEFORE strategy refactors)
Per `feedback_no_rushing_per_strategy_tweak.md` + B701 confronting-test discipline:
8. **EV-GAP-CONDITIONING-TEST** — `conditional_add_test` for `gap_pct < 0.02` AND-required on `strat_pead_long`. 30 alphabetical T1a tickers, train through 2023, test 2024+. Report FT lift.
9. **EV-GAP-CONDITIONING-TEST-SHORT** — same for `strat_pead_short`.
10. **EV-FOMC-SPY-CONFIRMATION** — SPY pre-FOMC 24h return on 2020-2026 vs Lucca-Moench 1994-2011 baseline. Use FOMC calendar from FRED if available; manually-curated calendar if not.
11. **EV-FOMC-SINGLE-STOCK-BETA-DECILE** — per-beta-decile pre-FOMC drift on T1a 2020-2026, conditional on #10 surviving.

### Phase 2: Strategy refactors (ONLY if confronting tests pass)
12. **EV-PEAD-GAP-CONDITIONING-WIRE** — only if EV-GAP-CONDITIONING-TEST passes; wire as LOCAL change per `feedback_local_changes_default_global_needs_approval`.
13. **EV-FOMC-REFACTOR** — only if both FOMC confronting tests pass; otherwise mark FOMC strategies EXPLORATORY per B652 W5m precedent and DEFER until cube validation.

### Phase 3: Tier-3 deferred (revisit post-Stage-5)
14. **EV-SUE-INFRA-SCOPE** — when YoY-proxy cube verdict is in, evaluate SUE swap cost-benefit. Owner-gated.
15. **EV-RESTATEMENT-PREFETCH-BOUNDARY** — design discussion for prefetch-layer H2 mitigation (if owner wants strict bitemporal PIT).

### Phase 4: Already-queued (no B702 action)
16. **S5-MULTIPLE-TESTING-CORRECTION** — cross-cluster effective hypothesis count; Stage 5 cube methodology; B641 queue.

---

## 4. Tool-file save status

The 2 reviewer-supplied tool files (`earnings_feed_pit_audit.py` + `validate_earnings_feed_pit_audit.py`) are NOT in current context — they were in the prior conversation but the summary did not preserve their full content.

**Action required from owner:** re-paste both file contents in next message; I will save to `scripts/` and run the validator under the EV-PHASE-0-HARNESS-VALIDATE ticket. Until then, Phase-0 production audit is blocked.

---

## 5. End-of-turn delta summary

- **3 reviewer claims source-verified REFUTED or WEAKER than asserted:** H1 (wrong cache), H2 (wrong layer), H3 (structurally refuted).
- **1 reviewer criticism possibly CORRECT against B682:** EV-3 deletion needs source-verification (HIGHEST PRIORITY for next turn).
- **2 reviewer-asserted strategy refactors GATED behind confronting tests:** gap-conditioning, pre-FOMC.
- **1 reviewer-asserted SUE swap moved to TIER-3:** infra-cost not priced.
- **2 reviewer artifacts ENDORSED:** Phase-0 harness + cross-cluster Pattern N.
- **1 owner action needed:** re-paste 2 tool files so save + validate can proceed.
- **Implementation plan:** 16 tickets across 4 phases, with explicit Phase -1 source-read gate BEFORE Phase 0 harness build.

## 6. CHECKLIST compliance statement

Applied items: #45 (response compliance), #67 (per-turn doc sync), #69 (test pyramid scope — no code changes this turn), #77 (canonical source pinned for prior B701 scripts), #94 (per-turn EXECUTION_QUEUE update — coming next), #100 (final-result drift-guard for adversarial review), #105 (Step 3 producer-source read for pead.py + screener.py + backtest.py). Items not applicable: #75 (no commit pyramid since no code changes), #71 (no fork integration). Findings surfaced PRE-recommendation per Pass 52 mandate. End-of-response compliance statement also coming with commit.
