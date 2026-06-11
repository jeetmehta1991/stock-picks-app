# B705 — ICT Cluster: Adversarial Review of External Reviewer's Proposal

<!-- Source: STAGE_4_ICT_CLUSTER_WALKS.md + backtest/signals/ict_producers.py + backtest/signals/multi_timeframe.py + backtest/signals/smc_ict.py per CHECKLIST #77 -->

**Owner directive pattern (continuing B702 discipline):** don't trust blindly; source-verify each claim against actual code before accepting or rejecting.

**Author:** Claude
**Date:** 2026-06-11
**Discipline:** [feedback_audit_recommendations_against_existing_directives](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_audit_recommendations_against_existing_directives.md) + [feedback_walk_step3_must_read_producer_source](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_walk_step3_must_read_producer_source.md).

---

## 1. Adversarial verdicts by claim (source-verified)

### Claim — PO3 producer-name collision (`compute_po3_signal` vs `compute_po3_signals`) is a class-of-bug warning (reviewer's "Pattern S / CC-A escalation")

**Source-verified state:**
- `compute_po3_signal` (singular) lives at [multi_timeframe.py:194](backtest/signals/multi_timeframe.py#L194). Emits: `po3_bullish`, `po3_bearish`, `po3_close_position`, `po3_sweep_below_prior_low`, `po3_sweep_above_prior_high`. Consumed by ICT-1/2/3/4.
- `compute_po3_signals` (plural) lives at [ict_producers.py:46](backtest/signals/ict_producers.py#L46). Emits: `po3_accumulation_active`, `po3_manipulation_sweep_down/up`, **`po3_mmbm_setup`**, **`po3_mmsm_setup`**, `po3_accum_range_pct`. Consumed by ICT-5/6 MMBM/MMSM.
- **Key sets are DISJOINT.** Both producers wire correctly to non-overlapping consumers. The CC-A "wrong producer traced" scare was a discovery-time mis-association, not a runtime mis-wiring.

**Adversarial verdict:** **REVIEWER'S "CLASS-OF-BUG WARNING" STANDS; THE SPECIFIC PO3 INSTANCE IS A DEFENSIVE-ENGINEERING SMELL, NOT A LIVE BUG.** No silent-wiring exists today, but the nominal-name collision is unsafe — a future developer adding `po3_*` signals can easily mis-trace which producer feeds which consumer. The reviewer's escalation to **class-wide producer-name-collision audit** is correct; the framing of "this specific PO3 case is a silent bug" overstates today's state.

**Action:** ship the class-wide audit (CC-A escalation) but mark CC-A specifically as RESOLVED — code works correctly today.

---

### Claim — PO3 detection is a single-bar reversal pattern; "accumulation/manipulation/distribution" framing is mythology not substance

**Source-verified state ([multi_timeframe.py:244-253](backtest/signals/multi_timeframe.py#L244)):**
```python
po3_bull = bool(
    sweep_below                    # today_low ≤ prev_day_low * (1 + 0.001)
    and t_close > t_open           # bullish close
    and close_position > 0.66      # close in upper third of today's range
)
```
Three conditions on TODAY's bar + one reference to YESTERDAY's low. No multi-bar "accumulation phase," no "manipulation" beyond a sweep tag, no "distribution" beyond a strong close. The docstring's "Accumulation → Manipulation → Distribution" framing **does not appear in the detection**.

**Adversarial verdict:** **REVIEWER 100% CORRECT.** PO3 is a single-bar sweep-and-strong-close candle. The reviewer's Part 2 framing ("strip the ICT mythology and ask whether there's a mechanically real effect underneath") is the right lens for this cluster.

---

### Claim — MMBM/MMSM is PO3 with a tighter accumulation-range gate

**Source-verified state ([ict_producers.py:46-93](backtest/signals/ict_producers.py#L46)):**
```python
po3_mmbm_setup = (
    accum_range_pct <= 0.05         # 5-bar range ≤ 5% of mean_close
    AND today_low < range_low        # sweep below 5-bar low
    AND today_close > range_low      # closed back above sweep level
    AND today_close > today_open     # bullish close
)
```
MMBM adds the **5-bar tight-accumulation pre-condition** that PO3 (singular) lacks. PO3 only references the prior day's low.

**Adversarial verdict:** **REVIEWER'S CONSOLIDATION CLAIM PARTIALLY CORRECT.** Mechanism class is the same (sweep + reversal); parameterization is distinct enough that MMBM fires are likely a STRICT SUBSET of PO3 fires (every MMBM is a PO3 but not every PO3 is an MMBM). **This is the testable consolidation question — run the gate-redundancy diagnostic.** If MMBM is a deterministic subset (Pattern W), it's a candidate for deletion or for parameter-folding into PO3 (similar to the B682 EV-3/EV-4 deletion pattern).

---

### Claim (HIGHEST-IMPACT) — Turtle Soup inherits a 90-bar (4-month) recency window from SMC; this is the single highest-value tighten

**Source-verified state:**
- Turtle Soup fires on `smc_liquidity_swept_dn` ([screener.py:3667](backtest/signals/screener.py#L3667)).
- `smc_liquidity_swept_dn` is emitted by `compute_smc_signals` in [smc_ict.py](backtest/signals/smc_ict.py); the default recency parameter is **`event_recency_bars: int = 90`** ([smc_ict.py:81](backtest/signals/smc_ict.py#L81)).
- The helper `_most_recent_event_within` ([smc_ict.py:51](backtest/signals/smc_ict.py#L51)) returns the most-recent non-zero event within 90 bars. The docstring even states the empirical rationale: "a 90-bar recency window catches the most-recent BOS in ~30% of days (vs ~0% with a 5-bar tail)."

**That empirical rationale (catching events for SMC strategies' purposes) is at odds with Turtle Soup's actual thesis.** Turtle Soup per Raschke 1996 *Street Smarts* is a **stop-run reversal** — the sweep and the reversal entry should be within a few bars. A sweep that happened up to 4 months ago is not a stop-run that's still pricing in today.

**Adversarial verdict:** **REVIEWER 100% CORRECT — THIS IS THE SINGLE HIGHEST-LEVERAGE CODE FINDING IN THE REVIEW.** Turtle Soup currently fires on stale sweeps that haven't been the "active liquidity event" for months. The recency window needs to be strategy-specific: SMC uses 90 (its strategies want a stale-but-known anchor); Turtle Soup needs 1-5 bars.

**Action:** wire a Turtle Soup-specific `smc_liquidity_swept_recent_5bar` (or similar) signal. Don't change the SMC default (which would break SMC strategies). NEW positive signal name; same-class fix as B608/B609 F2 "never use `not s.get(key)` pattern — add a positive symmetric signal" per [feedback_never_use_NOT_s_get_pattern](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_never_use_NOT_s_get_pattern.md).

---

### Claim — The cluster has no empirical foundation and the cube cannot validate it

**Source-verified state:**
- [STAGE_4_ICT_CLUSTER_WALKS.md:53](STAGE_4_ICT_CLUSTER_WALKS.md#L53) Pattern Q (already in doc, NOT new from reviewer): "no empirical-backtest citation for 10 of 12 strategies. Only Turtle Soup (SMC-style cross-source canonical via Raschke 1996) has any peer-reviewable methodology anchor. The other 10 are owner-trusted inline-spec wirings."
- [STAGE_4_ICT_CLUSTER_WALKS.md:16](STAGE_4_ICT_CLUSTER_WALKS.md#L16): "a cube PASS_CUBE label does NOT validate the underlying ICT methodology; only that the gate fires enough for statistical sampling."

**Adversarial verdict:** **REVIEWER'S DOMINANT FRAMING IS A SHARPER VERSION OF WHAT THE DOC ALREADY SAYS.** The doc admits Pattern Q + the cube-validation caveat. The reviewer's contribution is the upgrade in severity: from "documentation honesty" to "the cluster's existence question is unresolved and cube deferral cannot resolve it." That upgrade is **defensible** because:
1. The doc's "cube settles" disposition repeated across multiple strategies treats the cube as a neutral arbiter — but for a no-prior cluster, in-sample PASS is indistinguishable from overfit.
2. With C2 multiple-testing correction still open + C5 survivorship still open + C6 cost/slippage still open, even a cube PASS is a weak signal.

**My counter-position to reviewer:** the resolution path isn't "delete the cluster" — it's "consolidate the mechanism-overlapping reskins to ~2 strategies (sweep-reversal + gap-fill), so the cube hypothesis count matches the actual hypothesis count." That's structurally what the reviewer recommends but framed as discipline, not existence-judgment.

---

### Claim — Consolidate 10 sweep-reversal strategies to 1 well-built strategy per direction

**Source-verified state:** the 10 strategies the reviewer claims share the sweep-reversal mechanism:
- ICT-1/2 PO3 (prior-day sweep)
- ICT-3/4 PO3-HTF (PO3 + weekly_bias gate)
- ICT-5/6 MMBM/MMSM (5-bar tight-range + sweep)
- ICT-7/8 Turtle Soup (smc 90-bar liquidity_swept + above_prev_low + bullish close)
- ICT-9/10 Judas Swing (Turtle Soup + near_pivot ±0.30% gate)

**Mechanism overlap analysis:**
- PO3 vs MMBM: PO3 references prior-day low; MMBM references 5-bar low. **Different anchor — not deterministic subset.**
- PO3 vs PO3-HTF: HTF adds `weekly_bias_bull` AND-gate to PO3. **PO3-HTF fires are a STRICT SUBSET of PO3 fires** (Pattern W candidate). Testable via fire-overlap measurement.
- Turtle Soup vs PO3: different sweep source (90-bar liquidity vs prior-day low). **Different anchor — not subset.**
- Judas Swing vs Turtle Soup: Judas Swing adds `near_pivot` gate to Turtle Soup's primitives. **Judas Swing fires are a STRICT SUBSET of Turtle Soup fires** (Pattern W candidate).

**Adversarial verdict:** **REVIEWER'S "ONE MECHANISM" CLAIM IS A SLIGHT OVERSIMPLIFICATION.** There are at least 3 distinct sweep anchors (prior-day low, 5-bar range low, 90-bar SMC liquidity zone). After the Turtle Soup recency fix (1-5 bars), the anchors converge somewhat — Turtle Soup-with-tight-recency may collapse onto PO3 — but pre-fix they are distinct. **My counter-position:** consolidation is the right discipline but the right N is empirical, not pre-emptive. Run the redundancy diagnostic AFTER Turtle Soup recency fix; the diagnostic decides N.

The reviewer's HTF and Judas-Swing subset claims (Pattern W candidates) are testable now without waiting for B660 — fire-overlap measurement on the existing signal cache.

---

### Claim — Week-opening-gap-fill (ICT-11/12) is mechanically distinct + properly conditioned testable

**Source-verified state ([ict_producers.py:96-155](backtest/signals/ict_producers.py#L96)):**
```python
week_open_gap_up_15pct = (today_open / prev_close - 1) >= 0.015 if is_week_open else False
```
No upper bound. No earnings/news filter. No trend-direction conditioning.

**Adversarial verdict:** **REVIEWER 100% CORRECT.** Mechanically distinct from sweep-reversal (this is gap-mean-reversion). All three reviewer-flagged conditioning gaps are real:
1. **No upper bound** — mixes fillable retail gaps with news-driven repricings.
2. **No earnings filter** — earnings-day gaps are repricing events with documented PEAD continuation (Bernard-Thomas 1989), the opposite of mean-reversion.
3. **No trend context** — fading gap-ups in a strong uptrend fights the trend.

**Action:** confronting-test BEFORE the conditional fix (per [feedback_no_rushing_per_strategy_tweak](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_no_rushing_per_strategy_tweak.md)). Use the `conditional_add_test` harness from B701: test (gap_band 1.5-3% only) AND-required, then test earnings-filter AND-required, then test trend-context conditioning. Each tested in isolation, then composed.

---

### Claim — Strip "institutional flow / market maker" framing from docstrings BEFORE cube (CC-B Pattern R fix)

**Source-verified state ([screener.py:3170-3220](backtest/signals/screener.py#L3170)):** PO3 + MMBM + MMSM docstrings reference "Market Maker Buy/Sell Model," "stop-hunt then distribute upward," "institutional accumulation" — but the producers contain ZERO flow-data inputs (no Quiver, no SEC, no 13F). They fire on candle structure.

**Adversarial verdict:** **REVIEWER 100% CORRECT AND THE PRE-CUBE-BLOCKING RATIONALE IS SHARPER THAN THE DOC'S CC-B.** The doc's CC-B treats this as honesty hygiene. The reviewer's deeper point — the framing is the rhetorical cover that prevents the existence question — is the right escalation. Strip the language; the strategies become "another single-bar reversal pattern" and the cluster's roster bloat becomes visible.

**Action:** pre-cube docstring fix on all 6 PO3-family strategies (ICT-1/2/3/4/5/6). LOCAL change per [feedback_local_changes_default_global_needs_approval](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_local_changes_default_global_needs_approval.md).

---

## 2. Summary of Adversarial Verdicts

| Reviewer claim | My verified verdict | Action |
|---|---|---|
| PO3 producer-name collision is a silent bug | SCARE NOT BUG — disjoint keys, both wire correctly today. But CLASS-WIDE audit recommendation has merit | Class-wide audit ticket; CC-A specific case = NOT-A-BUG |
| PO3 detection is single-bar reversal vs mythology framing | 100% CORRECT | Pre-cube docstring fix |
| MMBM/MMSM is PO3 with extra gates | PARTIALLY CORRECT — different sweep anchor (5-bar vs prior-day) | Pattern W subset-test BEFORE consolidation decision |
| Turtle Soup 90-bar recency is wrong for stop-run thesis | 100% CORRECT — HIGHEST-LEVERAGE FINDING IN REVIEW | Wire a Turtle Soup-specific tight-recency signal (1-5 bars); DON'T change SMC default |
| Cluster has no empirical foundation, cube cannot validate | SHARPER VERSION OF DOC'S OWN PATTERN Q | Consolidation discipline; not deletion |
| Consolidate 10 sweep-reversal to 1 per direction | OVERSIMPLIFIED — 3 distinct sweep anchors today; may collapse to 2 post-Turtle-Soup-recency-fix | Redundancy diagnostic AFTER recency fix |
| Week-opening-gap-fill needs upper-bound + earnings + trend filter | 100% CORRECT | Confronting tests BEFORE refactor |
| Strip institutional-flow docstring framing pre-cube | 100% CORRECT — sharper "rhetorical cover" rationale | Pre-cube docstring fix on ICT-1/2/3/4/5/6 |

---

## 3. Implementation plan (16 tickets across 5 phases)

### Phase -1: Source-verification gate (THIS BATCH)
Already done above — 5 reviewer claims source-verified.

### Phase 0: Highest-leverage pre-cube fixes (ship next 1-2 turns; owner-approval required)
1. **`S4-B705-ICT-TURTLE-SOUP-RECENCY-FIX`** — wire Turtle Soup-specific tight-recency signal. NEW signal `smc_liquidity_swept_recent_5bar_dn/_up` parallel to existing 90-bar variant. Turtle Soup + Judas Swing consume the new variant. SMC strategies continue using existing 90-bar signal. **THIS IS THE SINGLE HIGHEST-LEVERAGE CODE CHANGE FROM THE REVIEW.**
2. **`S4-B705-ICT-PATTERN-R-DOCSTRING-FIX`** — strip "institutional flow / market maker / accumulation" language from ICT-1/2/3/4/5/6 docstrings. LOCAL per [feedback_local_changes_default_global_needs_approval]. Pre-cube blocking per CC-B + reviewer's "rhetorical cover" escalation.

### Phase 1: Subset/redundancy measurements (no code change; uses existing tools)
3. **`S4-B705-ICT-PO3-HTF-SUBSET-TEST`** — measure fire-overlap of ICT-3/4 vs ICT-1/2 to confirm Pattern W deterministic-subset claim. If subset > 0.95 → recommend deletion of ICT-3/4 (parameterize as `require_htf_bias` arg on ICT-1/2).
4. **`S4-B705-ICT-JUDAS-SWING-SUBSET-TEST`** — measure fire-overlap of ICT-9/10 vs ICT-7/8 (Judas Swing adds `near_pivot ±0.30%` gate to Turtle Soup primitives). If subset > 0.95 → recommend deletion of ICT-9/10.
5. **`S4-B705-ICT-MMBM-PO3-OVERLAP-TEST`** — measure fire-overlap ICT-5/6 vs ICT-1/2. Different sweep anchor; expect lower overlap than HTF/Judas. Decides whether MMBM stays distinct or folds.

### Phase 2: Consolidation feasibility (post-B660-land + post-recency-fix)
6. **`S4-B705-ICT-CONSOLIDATION-REDUNDANCY-RUN`** — run `gate_redundancy_diagnostic` across the post-recency-fix sweep-reversal family. Decides actual N for cube.
7. **`S4-B705-ICT-CROSS-CLUSTER-SMC-ABLATION`** — supersedes/refines `S4-ICT-CLUSTER-PATTERN-N-CROSS-CLUSTER-CUBE-ABLATION-WITH-SMC` (B687). Treats post-consolidation ICT + SMC sweep-reversal as ONE hypothesis family for C2 multiple-testing correction.

### Phase 3: Week-opening-gap-fill confronting tests (separate mechanism; runnable now)
8. **`S4-B705-WEEK-GAP-SIZE-BAND-TEST`** — `conditional_add_test` adding `gap_pct < 0.03` upper bound to ICT-11/12. Test alone first.
9. **`S4-B705-WEEK-GAP-EARNINGS-FILTER-TEST`** — `conditional_add_test` adding "no earnings ann in last 2d" gate. Test alone.
10. **`S4-B705-WEEK-GAP-TREND-CONTEXT-TEST`** — `conditional_add_test` adding direction-vs-trend gate. Test alone.
11. **`S4-B705-WEEK-GAP-COMPOSED-REFACTOR`** — IF all 3 confronting tests PASS, compose the conditioned variants. LOCAL change per scope discipline.

### Phase 4: Trigger optimization (post-consolidation, post-confronting-tests)
12. **`S4-B705-ICT-SURVIVOR-TRIGGER-TUNE`** — run `trigger_followthrough` + `sweep_threshold` tools on the consolidated sweep-reversal survivor. Watch OOS persistence — overfitting signature is in-sample-only improvement.

### Phase 5: Defensive-engineering / class-of-bug audit
13. **`S4-B705-PRODUCER-NAME-COLLISION-CLASS-AUDIT`** — static check: any pair of producers whose names differ only by pluralization/casing AND emit signal keys with shared prefixes. CC-A escalation reviewer recommended. Catches future po3_signal/po3_signals near-misses cluster-wide.
14. **`S4-B705-ICT-PATTERN-S-SHELL-AUDIT`** — surface ICT-5/6/11/12 hardcoded params (accum_window=5, tight_range=0.05, gap_threshold=1.5%) at the call site. Refactor to explicit-gate composition. Lower priority than 1-3.

### Phase 6: Already-queued (no B705 action)
15. **`S5-MULTIPLE-TESTING-CORRECTION`** — cross-cluster effective hypothesis count. Updated post-Phase-2 consolidation: ICT effective N drops from 12 to ~3-5 depending on subset-test results.
16. **`S4-CC-A-RESOLVED-MARK`** — explicit RESOLVED tag on the PO3 producer-name CC-A finding in the cluster doc: producers wire correctly today; reviewer's class-of-bug warning shipped as ticket #13 above.

---

## 4. CHECKLIST compliance

Applied: #45 (per-recommendation pre-flight via source-verification before adversarial verdict), #67 (per-turn doc sync — this report + queue ticket adds coming together), #69 (test pyramid scope — no code changes in this batch, doc-only review), #77 (canonical source headers + verified file paths), #94 (per-turn EXECUTION_QUEUE update — coming next), #100 (final-result drift-guard for adversarial review), #105 (Step-3 producer source-read for [multi_timeframe.py](backtest/signals/multi_timeframe.py), [ict_producers.py](backtest/signals/ict_producers.py), [smc_ict.py](backtest/signals/smc_ict.py), [screener.py](backtest/signals/screener.py)). N/A: #71 (no fork integration), #75 (no commit-pyramid for doc-only).
