# B710 — Pivot Cluster: Adversarial Review of External Reviewer's 4th-Pass Proposal

<!-- Source: STAGE_4_PIVOT_CLUSTER_WALKS.md + output_audit/fire_count_measured_b660_full_universe.json per CHECKLIST #77 -->

**Owner-pattern (B702/B705 discipline):** source-verify each claim before accepting. This is the **4th** external reviewer pass on the pivot cluster, and the doc has matured significantly (the reviewer's framing acknowledges this).

**Date:** 2026-06-12
**Discipline:** [feedback_audit_recommendations_against_existing_directives](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_audit_recommendations_against_existing_directives.md) + [feedback_no_prior_edge_consolidate_before_tune](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_no_prior_edge_consolidate_before_tune.md)

---

## 1. Source-verification: reviewer's measured numbers vs B660 actual

B660 measurement file at [output_audit/fire_count_measured_b660_full_universe.json](output_audit/fire_count_measured_b660_full_universe.json) covers 2020-2026 (6.41 yr × ~503 T1a tickers). Per-year normalization confirms every reviewer-cited number to ±0.1%:

| Strategy | B660 total (L/S) | Per-year (L/S) | Reviewer claim (L/S/yr) | Accuracy |
|---|---|---|---|---|
| W8 cpr_narrow_bullish | 37,297 / 12,641 | **5,820 / 1,972** | 5,817 / 1,971 | ✓ EXACT |
| W8a cpr_narrow_momentum | 80,342 / 54,243 | **12,534 / 8,463** | 12,530 / 8,460 | ✓ EXACT |
| W8b cpr_narrow_momentum_short | 0 / 89,138 | **0 / 13,906** | 0 / 13,902 | ✓ EXACT |
| W2 shooting_star_short | 0 / 1,309 | **0 / 204** | 0 / 204 | ✓ EXACT |
| W4 pivot_s3_capitulation | 15 / 0 | **2.3 / 0** | "0 SHORT" | ✓ EXACT |
| W6 pivot_r1_breakout | 8,740 / 1,875 | **1,364 / 292** | 1,363 / 292 | ✓ EXACT |
| W7 pivot_r2_continuation | 859 / 77 | **134 / 12** | 134 / 12 | ✓ EXACT |
| W9 camarilla_s3_bounce | 111 / 312 | **17 / 49** | 17 / 49 | ✓ EXACT |
| W10 camarilla_r4_breakout | 4,897 / 5,711 | **764 / 891** | 764 / 891 | ✓ EXACT |

The reviewer's claims are not estimates or sketches — they are arithmetic against the measurement file. The evidentiary basis is the strongest of any review in this series.

---

## 2. Adversarial verdicts by claim

### Claim — Fire-count ceiling missing (HIGHEST-LEVERAGE NEW FINDING)
**Reviewer position:** The fire-count gate has a floor (≥30/yr) but no ceiling. W8/W8a/W8b at 5.8k/12.5k/13.9k per year fire ~25-28 times per name per year — "roughly every two weeks on every stock. That is not a signal; it is a near-permanent state classification." A strategy firing 12k×/yr passes the ≥30 floor trivially while being the LEAST selective. The B654 W8 redundancy fix dropped fire count from 34k → 10.7k, which the doc calls "validates the redundancy thesis" — but 10.7k is still a state flag.

**Source-verified state:** B660 file confirms exactly. The pivot doc carries W8/W8a/W8b all as **"✅ PASS"** (verified by reading the cluster-state table head). Only W8 is "REOPENED"; W8a/W8b are not. Yet they fire 2× and 2.4× more often than W8.

**Adversarial verdict:** **REVIEWER 100% CORRECT — SINGLE HIGHEST-LEVERAGE FINDING IN THE 4TH PASS.** The verdict logic is structurally one-sided: floor-only gates pass anything above 30/yr regardless of whether 30 or 30,000. A strategy firing every 2 weeks per name is mechanically NOT a selective signal — it's a state flag. The B654 partial fix (W8 only) corroborates this: same-class W8a/W8b were never touched, and they fire MORE than pre-fix W8.

**Action:** wire a fire-count CEILING into `scripts/measure_fire_count.py` verdict logic. Owner-recommended initial threshold: **5,000/yr per direction** (~10/name/yr at T1a~500). At 5k ceiling: W8 LONG (5.8k) flagged TOO-FREQUENT_BORDERLINE; W8a (12.5k LONG, 8.5k SHORT) and W8b (13.9k SHORT) flagged TOO-FREQUENT_FAIL. CC-2 three_white_soldiers needs spot-check too (~8-10k/yr suspected).

---

### Claim — W8a/W8b should also be REOPENED on same logic as W8
**Reviewer position:** The doc REOPENED W8 (correctly) but bannered W8a/W8b ✅ PASS. The B654 fix logic — "fires every 2-4 days per name, so the gate is a near-permanent state flag" — applies AS-OR-MORE strongly to W8a (12.5k/yr = every ~10 trading days/name) and W8b (13.9k/yr).

**Adversarial verdict:** **REVIEWER CORRECT.** Symmetric REOPEN is required. The doc's own justification for W8 REOPEN ("absolute result 10.7k means strategy is still a state flag") is satisfied a fortiori by W8a/W8b.

**Action:** REOPEN W8a + W8b in the pivot cluster-state table; queue separate redundancy-audits for the broader cpr_narrow family (cpr_narrow + cpr_narrow_momentum + cpr_narrow_momentum_short — all consuming the loose 0.15 threshold).

---

### Claim — C1 timeframe finding (intraday pivots on daily bars) still unaddressed after 4 cycles
**Reviewer position:** The original C1 finding was that floor-trader pivots, Camarilla, and CPR are intraday tools applied to daily bars — the level the strategy signals on no longer exists at next-day-open entry. The doc codified this as CHECKLIST(r) but never applied it to any strategy. Now the measured CPR over-firing corroborates it indirectly: 12k fires/yr is exactly what you'd expect when a daily close is compared to a daily-recomputed pivot — the band is too loose for daily-bar precision.

**Adversarial verdict:** **REVIEWER 100% CORRECT — STRUCTURAL FINDING UNADDRESSED FOR 4 CYCLES.** CHECKLIST(r) is a rule on paper; no pivot strategy has been moved to intraday bars OR honestly reframed as a daily-momentum signal. The over-firing is the symptom of exactly the problem CHECKLIST(r) describes.

**Action:** binary decision required per pivot family (Floor-trader / Camarilla / CPR): (a) **move to intraday bars** (requires intraday OHLCV prefetch — substantial infra) OR (b) **honestly reframe** docstrings + signal names as "daily-bar derived support/resistance" + drop pivot-precision language. Owner-decision needed; the deferral is the largest structural debt in the cluster.

---

### Claim — Dual-wrapper dead-side audit: W4 0-SHORT, W7 12-SHORT are not validated duals
**Reviewer position:** Measured LONG/SHORT splits reveal "dual" strategies whose short (or long) side is effectively dead. W4 pivot_s3_capitulation fires 15 L / 0 S in 6.4yr — short side never fired once. W7 pivot_r2_continuation fires 134 L / 12 S per year — short side at 12/yr is FAIL_FIRE_STARVED. These are effectively single-direction strategies wearing a `_strat3` dual wrapper, and their short-side gates have never been validated against a single fire.

**Adversarial verdict:** **REVIEWER 100% CORRECT.** Per [Step 1.5 avoid-branch dead-code check](CHECKLIST.md) (B641 codification), this is exactly the failure mode the rule was designed to catch — but it was applied to source-code presence, not measured-fire absence. The audit needs to extend to runtime behavior.

**Action:** systematic LONG-vs-SHORT split audit across all `_strat3` dual strategies. For each: if direction-K fires <30/yr (FAIL_FIRE_STARVED threshold), tag direction-K as EXPLORATORY or split off as `strat_X_<long|short>_only`. Affected by reviewer's specific naming: W4 (0 SHORT), W7 (12 SHORT), W9 (17 LONG borderline). Likely also affects strategies outside pivot cluster.

---

### Claim — PASS_CUBE label semantics overstated
**Reviewer position:** The cluster-state table's ✅ PASS reads as validation. PASS_CUBE only means "fires enough to measure" — not "has edge." None of the 8 PASS strategies has been through cube return evaluation (C2/C3/C5/C6 all open). Honest label is "PASS_FIRE_COUNT, edge-validation pending."

**Adversarial verdict:** **REVIEWER CORRECT — DOC LABEL CHOICE OVERSTATES.** The doc states the caveat in PROSE elsewhere (e.g., "PASS_CUBE does NOT validate the underlying methodology"), but the TABLE bannered with ✅ green checkmarks visually conveys validation. Same pattern as ICT cluster reviewer flagged. Per [feedback_no_prior_edge_consolidate_before_tune](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_no_prior_edge_consolidate_before_tune.md), cube PASS for unvalidated-edge strategies is overfit-pass, not edge-pass.

**Action:** rename column in cluster-state table from "PASS / FAIL" to "FIRE_COUNT_PASS / FIRE_COUNT_FAIL"; keep edge-PASS for post-cube. Replaces ✅ with neutral "MEASURED-OK" tag.

---

### Claim — Per-strategy entry-tuning items for measured survivors

**Reviewer's specific recommendations (verbatim, condensed):**

| Strategy | Per-yr fires (L/S) | Reviewer's tuning recommendations |
|---|---|---|
| W1 bullish_engulfing_support | 254 / 274 | (1) Body-engulf not close-engulf + gap-driven-engulfing guard; (2) ATR-scaled support-proximity tolerance, swept; (3) **reclaim confirmation** — enter on bar AFTER engulfing that holds above engulfing high, NOT on engulfing bar itself |
| W3 pivot_s1_bounce | 255 / 111 | (1) **Reclaim-bar entry** (close back above S1 after tagging, not the touch); (2) ATR-scaled proximity band, swept; (3) volume-dry-up on pullback into S1 (selling exhaustion / Bulkowski supply-absorption) |
| W6 pivot_r1_breakout | 1,364 / 292 | (1) Replace fixed-volume-multiple with **RVOL z-score**; (2) **ATR-scaled break-clearance margin** above R1 (separates real break from one-tick poke); (3) test whether MACD-STATE gate is delaying entry past clean breakout — drop if no conditional edge |
| W7 pivot_r2_continuation | 134 / 12 | **SUBTRACTIVE de-gating** — W7 over-gated; run redundancy diagnostic on ADX vs EMA-stack (both assert "trending up"); drop the redundant one to raise fire count without losing selectivity |
| W9 camarilla_s3_bounce | 17 / 49 | Reclaim-bar entry + volume dry-up apply as for W3; structural ceiling is C1 timeframe (Camarilla is explicitly intraday — Nick Stott's bond-desk method) |
| W10 camarilla_r4_breakout | 764 / 891 | ATR-clearance margin + RVOL z-score adds apply (as for W6) |

**Adversarial verdict:** **ENDORSED IN FULL for the genuine survivors (W1, W3, W6, W9, W10).** Each ticking item is a documented pattern from prior reviewer feedback applied to a specific strategy:
- Reclaim-bar entry = same pattern as B701 CC-6 doji "fire on up-resolution, not on the doji" + B697 BR-1 anti-fakeout
- RVOL z-score + ATR-clearance = same pattern as B697 BR-1 + B698 BR-1 anti-fakeout-producer adds
- Volume dry-up = same pattern as B650 W5 Wyckoff Spring vol gate + B654 W8 redundancy-fix
- Subtractive de-gating for over-gated strategies = same pattern as B656 T3 RSI-50 drop + B654 W8 noop drop

These are not new ideas — they are CONSISTENT APPLICATION of the discipline the cluster has already developed, to strategies where it hasn't yet been applied. Endorsed; queued as per-strategy tickets.

**My counter-position:** all tuning gated behind **OOS-persistence watchdog** (`S4-B708-OOS-WATCHDOG-TOOL-WIRING` from B708 audit) — reviewer's own caveat. For a pivot cluster with C1 timeframe structural debt and no peer-reviewed daily-bar pivot edge, in-sample improvement risks fitting noise. Train/test split mandatory.

---

## 3. Summary of Adversarial Verdicts

| Reviewer claim | My verified verdict | Action |
|---|---|---|
| Fire-count ceiling missing (W8/W8a/W8b 5.8k-13.9k/yr) | **100% CORRECT — HIGHEST-LEVERAGE FINDING** | Wire ceiling into measure_fire_count.py verdict logic |
| W8a/W8b should also be REOPENED | CORRECT — symmetric application of W8 REOPEN rationale | Mark REOPENED in pivot cluster-state table |
| C1 timeframe finding unaddressed for 4 cycles | 100% CORRECT — structural debt | Binary decision per family: intraday OR honest reframe |
| Dual-wrapper dead-side audit (W4 0-SHORT, W7 12-SHORT) | CORRECT — Step 1.5 needs runtime extension | Cluster-wide split audit |
| PASS_CUBE label overstates | CORRECT — same as ICT cluster pattern | Rename column to FIRE_COUNT_PASS |
| W1/W3/W6/W7/W9/W10 entry-tuning | ENDORSED — consistent application of established discipline | Per-strategy tickets gated behind OOS watchdog |

---

## 4. Implementation Plan (15 tickets across 5 phases)

### Phase 0: Fire-count ceiling (highest-leverage, cheap)
1. **`S4-B710-FIRE-COUNT-CEILING-VERDICT-LOGIC`** — wire `--ceiling-per-year-per-direction` arg (default 5,000) into `measure_fire_count.py`; flag TOO-FREQUENT_BORDERLINE at 0.8×ceiling and TOO-FREQUENT_FAIL above. Re-run on B660 data; expected catches: W8 LONG, W8a both, W8b SHORT, possibly cpr_narrow_bullish SHORT.

### Phase 1: REOPEN + redundancy diagnostic on confirmed over-firers
2. **`S4-B710-W8A-W8B-REOPEN-+-CPR-FAMILY-REDUNDANCY-RUN`** — mark W8a/W8b REOPENED; run `gate_redundancy_diagnostic` on full cpr_narrow family with measured B660 data underneath.
3. **`S4-B710-W9-FAMILY-REDUNDANCY-RUN`** — W9/W9b/W9c reskins; per reviewer "W9b/c are W9 + RSI/OBV, almost certainly redundant". Measured W9b at 4 L / 14 S per year (FAIL_FIRE_STARVED) confirms over-gating.
4. **`S4-B710-W7-ADX-VS-EMA-REDUNDANCY-DIAGNOSTIC`** — does ADX add conditional information over EMA-stack? Likely redundant.

### Phase 2: C1 timeframe decision (binary, deferred 4 cycles)
5. **`S4-B710-PIVOT-FAMILY-INTRADAY-VS-REFRAME-DECISION`** — owner-decision ticket: (a) move to intraday bars or (b) honest reframe + signal-name change. Applies to floor-trader pivot family + Camarilla family + CPR family. Largest structural debt; no further deferral.

### Phase 3: Dual-wrapper dead-side audit (Step 1.5 runtime extension)
6. **`S4-B710-DUAL-WRAPPER-DEAD-SIDE-AUDIT-CLUSTER-WIDE`** — extend Step 1.5 from source-code to runtime: any `_strat3` dual strategy where direction-K measures <30/yr → flag direction-K EXPLORATORY or split into single-direction registry entry. Specific affected: W4 SHORT (0), W7 SHORT (12), W9 LONG (17).

### Phase 4: Per-strategy entry-tuning on genuine survivors (gated behind OOS watchdog)
7. **`S4-B710-W1-RECLAIM-BAR-ENTRY-+-BODY-ENGULF-+-GAP-GUARD`** — three reviewer-named adds for W1; OOS-watchdog-gated.
8. **`S4-B710-W3-RECLAIM-BAR-ENTRY-+-VOL-DRY-UP`** — reclaim-bar + Bulkowski vol-dry-up on S1 pullback.
9. **`S4-B710-W6-RVOL-Z-SCORE-+-ATR-CLEARANCE-+-DROP-MACD-IF-NO-EDGE`** — three reviewer-named adds for W6 breakout.
10. **`S4-B710-W7-SUBTRACTIVE-DE-GATING-ADX-OR-EMA`** — rare pivot strategy where tune is subtractive.
11. **`S4-B710-W9-RECLAIM-BAR-+-VOL-DRY-UP`** — same pattern as W3 + W1.
12. **`S4-B710-W10-ATR-CLEARANCE-+-RVOL-Z-SCORE`** — breakout tuning per W6 pattern.

### Phase 5: Doc-level fixes
13. **`S4-B710-PASS-CUBE-LABEL-RENAME`** — cluster-state column "PASS / FAIL" → "FIRE_COUNT_PASS / FIRE_COUNT_FAIL"; ✅ → "MEASURED-OK".
14. **`S4-B710-W4-W9B-W9C-CONSOLIDATION-VS-EXPLORATORY-DISPOSITION`** — fire-starved set already EXPLORATORY in doc; surface explicit "consolidation candidate" disposition for W9b/W9c (reviewer: "right action is consolidation, not tuning").

### Phase 6: Already-queued infrastructure
15. **`S4-B708-OOS-WATCHDOG-TOOL-WIRING`** is a PREREQUISITE for Phase 4 — confirmed in B708 audit, queued.

---

## 5. What was already in the doc and didn't need re-queuing

Reviewer correctly acknowledged the doc is mature on these:
- PRELIMINARY revert (correctly retracted verdict-reversal over-claim)
- CHANGES-MERGED vs VALIDATED-RESOLUTIONS distinction (sharp honesty fix)
- Inverted-prioritization confession ("strategies are cleaner; the answer to 'does any of this make money' is no closer")
- W3 pin_bar + W10 R3→R4 rename (validated fixes)
- Per-regime-clustered counts requirement for B660 (right ask)

These are NOT B710 tickets — they are already-shipped doc improvements.

---

## 6. CHECKLIST compliance

Applied: #45 (per-recommendation pre-flight; source-verified each measured number before adversarial verdict), #67 (per-turn doc sync — banner + queue tickets + this doc together), #69 (test pyramid scope — doc-only review batch; no code changes), #77 (canonical source headers + verified B660 file path), #94 (per-turn EXECUTION_QUEUE update — 15 tickets coming), #100 (final-result drift-guard for adversarial review), #105 (Step-3 producer source + measurement file end-to-end read).
