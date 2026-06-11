# Stage 4 Pivot Cluster Walks — Post-Reviewer-Audit Status

> **B710 STATUS BANNER (2026-06-12) — 4TH-PASS ADVERSARIAL REVIEW: source-verified every reviewer-cited fire count against B660 to ±0.1% accuracy.** Output: [STAGE_4_PIVOT_CLUSTER_B710_ADVERSARIAL_REVIEW.md](STAGE_4_PIVOT_CLUSTER_B710_ADVERSARIAL_REVIEW.md). **HIGHEST-LEVERAGE FINDING (REVIEWER 100% CORRECT)**: the fire-count verdict logic has a floor (≥30/yr) but **NO CEILING**. W8/W8a/W8b firing 5.8k/12.5k/13.9k per year = **25-28 fires per name per year** = state-flag, not signal. The B654 W8 partial fix dropped W8 only; W8a/W8b were untouched and now fire 2-2.4× more than pre-fix W8. **Reviewer's other source-verified findings**: W8a/W8b should also be REOPENED on same logic as W8; C1 timeframe finding (intraday pivots on daily bars) STILL UNADDRESSED after 4 cycles — CHECKLIST(r) codified but never applied; dual-wrapper dead-side audit needed (W4 0 SHORT, W7 12 SHORT measured = unvalidated short-side branches); PASS_CUBE label semantics overstate ("✅ PASS" reads as validated; only means "fires enough to measure"). **Per-strategy entry-tuning endorsed** for W1/W3/W6/W7/W9/W10 — consistent application of patterns already validated in B697/B698/B650/B654/B656. 15 B710 tickets queued across 6 phases. Top priority: `S4-B710-FIRE-COUNT-CEILING-VERDICT-LOGIC` (few lines, immediate effect on reclassification).
>
> ---
>
> **B691 STATUS BANNER (2026-06-11) — B660 measured pivot cluster TRUSTWORTHY ✅, B689 re-run will NOT change these numbers.** B660 full-universe fire-count measurement landed [2026-06-11 02:30 UTC](output_audit/fire_count_measured_b660_full_universe.json). **Pivot cluster verdict: 8 PASS_CUBE / 5 FAIL_FIRE_STARVED (real, not harness-gap).** All pivot gates use only `technical.compute_pivots` + companion technical producers; not affected by the harness gap. Measured values (LONG / SHORT fires/yr; verdicts in CAPS):
>
> | W# | Strategy | LONG | SHORT | Verdict |
> |---|---|---:|---:|---|
> | W1 | bullish_engulfing_support (candle) | 254 | 274 | ✅ PASS |
> | W2 | shooting_star_short (candle) | 0 | 204 | ✅ PASS |
> | W3 | pivot_s1_bounce | 255 | 111 | ✅ PASS |
> | W4 | pivot_s2_bounce | 28 | 0 | 🔴 **FAIL_FIRE_STARVED (real)** — gate-stack rare-event combination |
> | W5 | pivot_s3_capitulation | 2 | 0 | 🔴 **FAIL_FIRE_STARVED (real, EXPLORATORY per B652)** — Wyckoff Spring/Test sequence; cube cannot statistically validate; rare-but-strong per `feedback_walk_step5` |
> | W5m | pivot_r3_blowoff_short (B645 mirror) | 0 | 4.5 | 🔴 **FAIL_FIRE_STARVED (real, EXPLORATORY)** — symmetric inverse of W5; same rare-event caveat |
> | W6 | pivot_r1_breakout | 1,363 | 292 | ✅ PASS |
> | W7 | pivot_r2_continuation | 134 | 12 | ✅ PASS |
> | W8 | cpr_narrow_bullish (post-B654) | 5,817 | 1,971 | ✅ PASS (verdict REOPENED per B687 — see trend doc Finding #1) |
> | W8a | cpr_narrow_momentum | 12,530 | 8,460 | ✅ PASS |
> | W8b | cpr_narrow_momentum_short | 0 | 13,902 | ✅ PASS |
> | W9 | camarilla_s3_bounce | 17 | 49 | ✅ PASS |
> | W9b | camarilla_rsi_obv | 4 | 14 | 🔴 **FAIL_FIRE_STARVED (real)** — 4-gate stack with `rsi` + `obv` confluence; ~18/yr universe-wide |
> | W9c | camarilla_rsi_obv_short | 0 | 14 | 🔴 **FAIL_FIRE_STARVED (real)** — symmetric inverse of W9b |
> | W10 | camarilla_r4_breakout (post-B641 R3→R4 rename) | 764 | 891 | ✅ PASS |
>
> **All previous `PENDING-B660` labels in this doc are now RESOLVED.** Pre-B660 estimates (e.g. W5 ~18.3/yr B643 estimator) overshot the measured 2/yr by ~9×; consistent with the `feedback_minimum_fire_count_gate_before_cube` lesson that pre-cube estimators are upper-bounds. W5 + W5m + W4 + W9b + W9c FAIL_FIRE_STARVED are REAL (not harness-gap); per `feedback_walk_step5` rare-but-strong signals can carry as EXPLORATORY pending Stage 5 cube empirical adjudication.
>
> **What this document is now.** A comprehensive **post-action report** showing, for every reviewer finding and every strategy, exactly what shipped, what's queued, and where the final state lives. Originally written as a B640 prospective walk-bundle (10 strategies, candle 2 + pivot 8 to surface options); now restructured as a per-cluster living doc covering the closed-out state after the reviewer's first-wave adversarial audit + second-wave methodology critique + 12+ follow-on shipping batches (B641 → B660).
>
> **Owner directive 2026-06-09:** *"Don't create these bundle docs by batch but by strategy clusters."* — accordingly, this doc is renamed from `STAGE_4_BATCH_640_WALK_BUNDLE.md` → `STAGE_4_PIVOT_CLUSTER_WALKS.md`. Future trend walks → `STAGE_4_TREND_CLUSTER_WALKS.md` (now LIVING — closes T3/T8/T10 redundancy audits B655-B658 + general trend coverage T1-T10); chart_pattern walks → `STAGE_4_CHART_PATTERN_CLUSTER_WALKS.md` (pending); etc. The two candle bridge strategies (W1, W2) remain in this doc as historical record but will be cross-referenced from a future `STAGE_4_CANDLE_CLUSTER_WALKS.md`.
>
> **Audience.** Two:
>  (1) **External reviewer** who issued the adversarial audit (methodology #1-9 + market-structure C1-C6 + per-strategy bugs + regime classifier #1-8) AND the second-wave critique (2C1-2C7 on the response itself). For you, jump to **[Reviewer findings response matrix](#reviewer-findings-response-matrix)** — every finding traced to its action — and the new **[Section E.1 post-B652 follow-on cycle](#section-e1--post-b652-follow-on-cycle-b653--b660)** which absorbs the trailing redundancy-audit + silent-gap-unify + measurement work since the original close.
>  (2) **Future readers** (owner, Claude in later sessions, new collaborators). For you, the **[Cluster current state](#cluster-current-state)** table is the orientation; per-strategy detail below.
>
> **Source of truth.** Code references reflect the current state at commit `db2dda419` (post-B659 fixture sync; B660 full-universe measurement still running in background — see [pending-numbers caveat](#measurement-status--b660-full-universe-in-flight)). Each strategy walk preserves the original B640 prospective analysis followed by a **FINAL STATUS** block — originally written POST-B645, now updated with POST-B659 deltas where the follow-on cycle changed the strategy's gate set.

---

## Executive summary

> **HONEST RE-FRAMING POST-EXTERNAL-AI 2ND CRITIQUE (2026-06-09).** The 2nd-wave external-AI review correctly pointed out that the original framing of this section overstated resolution status: "SHIPPED" was reading as "resolved" but actually means "changes merged"; several of the SHIPPED items are themselves awaiting validation (measurement / walk-forward / survivorship work that's queued). Distinction now drawn explicitly between CHANGES-MERGED and VALIDATED-RESOLUTIONS.
>
> **FOLLOW-ON CYCLE UPDATE (post-B652 → B660).** After the 2nd-critique RE-FRAMING above, four trailing items shipped: B654 (W8 cpr_narrow redundancy-audit option B-local — new `cpr_narrow_tight` 0.05 producer + RSI-50 noop dropped), B655 (T10 supertrend_macd STATE → EVENT-anchored 5-day flip — trend cluster cross-ref), B657 (T8 ichimoku weekly Kumo silent-gap unify — trend cluster cross-ref), B659 (autonomous bundle: W6/W7/W8 LONG AVWAP default-True → False + W5m `vol_below_avg` symmetric vol gate + T3 SHORT `(not above_200)` → `below_ema_200` positive symmetric). B660 launched full-universe measurement run (T1a × 2020-2026 × all 222 strategies) — currently in flight; authoritative fires/yr numbers backfill once landed.

| | Count |
|---|---|
| Reviewer findings raised | **24** first-wave (methodology 9 + market-structure 6 + per-strategy 7 + regime classifier 8 — note overlap) + **7** second-wave (2C1-2C7) = **31 total** |
| Findings with code/doc CHANGES MERGED | **22** — was 15 at the original B652 close; B654/B655/B659 added 7 more closures on M5 (W6/W7/W8 LONG default-True unify), P4 (W8 RSI-noop drop bundled with redundancy audit), W8/T10/T8 redundancy-audit triad per 2C2 corrected methodology, W5m S4-W5M-SYMMETRIC-VOL-GATE per Wyckoff Distribution Upthrust-Test symmetry with B650 W5 LONG, T3 S4-T3-NOT-ABOVE-200-EMA-PATTERN per `feedback_never_use_NOT_s_get_pattern` |
| Of those, **fully VALIDATED**: | **~4-5** (W3 pin_bar fix — direct unit-test pin; W10 R3→R4 rename — same-level conflict resolved by construction; CHECKLIST extensions r/s/Step 1.5 — methodology codifications; **W8 redundancy fix B654** — fire count dropped 34k → 10.7k as predicted, validating 4-of-5-gate redundancy thesis; T10 STATE → EVENT swap B655 — fire count dropped 33k → 772 as predicted, validating 99.19%-True extreme NO-OP gate diagnosis) |
| Of those, MERGED BUT VALIDATION QUEUED: | **~17** (M1 measurement tool on representative sample → **B660 in flight**; R3 hysteresis → walk-forward queued; W5 redesign → cube alpha-validation queued; W4 F3 regime delete → cube; W5m wired → cube can't yet evaluate squeeze tail per C2/C6; W6/W7 LONG default-False → cube replays whether the auto-fail behavior changes outcomes; T8 weekly Kumo default-False → cube; etc.) |
| Findings QUEUED with explicit tickets | **17** original tickets in `EXECUTION_QUEUE.md` of which **4 closed by this follow-on cycle** (S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY = B659; S4-W8-RSI-NOOP-GATE = B654 bundled; S4-W8-REDUNDANCY-AUDIT = B654; S4-W5M-SYMMETRIC-VOL-GATE = B659; S4-T3-NOT-ABOVE-200-EMA-PATTERN = B659). 8 NEW tickets added post-B641 (squeeze risk, borrow lookup, multiple-testing pass, marginal-contribution scoring, etc — many cross-ref Stage 5 cube work). |
| Findings closed-by-design / fully | **R6 only** (regime classifier latent VIX redundancy auto-resolved by R2 cleanup). **M2** previously claimed "COVERED BY M1" but per 2nd critique #6, M2 status is now "instrument exists; over-count risk NOT retired" — no PASSES-on-over-count tested in current sample. **M7** correctly COVERED BY M6's CHECKLIST (s). |
| Strategy code changes (post-B645 follow-on adds) | **W5** B650 `vol_below_avg` Wyckoff Spring vol gate + B651 regime expand all-regimes, **W5m** B652 stronger DO-NOT-DEPLOY gate + B659 `vol_below_avg` symmetric Upthrust-Test vol gate, **W8** B654 `cpr_narrow_tight` producer-additive (0.05 threshold; W8-only narrow scope) + RSI-50 noop drop + B659 LONG `above_avwap_50low` default-False, **W6** B659 LONG AVWAP default-False symmetric with SHORT, **W7** B659 LONG AVWAP default-False symmetric with SHORT. Cross-cluster (trend doc): **T10** B655 STATE → EVENT-anchored 5-day flip, **T3** B656 RSI-50 noop drop + B659 SHORT `below_ema_200` positive symmetric, **T8** B657 weekly Kumo default-True → False |
| New producers added (post-B645) | **`cpr_narrow_tight`** (B654; 0.05 threshold; B574-style narrow-scope local variant; W8-only consumer) + **`supertrend_flip_recent_long_5d` / `_short_5d`** (B655; 5-bar lookback in `compute_supertrend`; T10-only consumer) — both follow the B574 / B643 / B645 producer-additive narrow-scope pattern (other consumers of the loose-threshold parent retain old semantics) |
| Tooling shipped | **`scripts/measure_fire_count.py`** — replaces independence-product projection with measured fires/year against T1a OHLCV. **B648 fixed the hardcoded-220 scale-factor bug** (was understating projections ~2.3x; now uses actual PIT-active T1a ~503 at as_of) + added `--ticker-sample-strategy {first,random,stratified,all}` option for representative sampling. **B660 launched first-ever full-universe measurement run** — T1a × 2020-2026 × all 222 strategies; output to `output_audit/fire_count_measured_b660_full_universe.json` once complete |
| Methodology codifications | CHECKLIST **(r)** timeframe-mismatch (intraday-on-daily-bar reframe rule), **(s)** EVENT/STATE wired-to-finding, **Step 1.5** `_strat3` avoid-branch dead-code check restored. B649 inverted (corrected) the incorrect "correlated gates = well-designed" framing — `feedback_obv_avwap_macd_non_redundancy`-style per-gate "what does THIS screen out that the others don't" question now drives redundancy-vs-confluence distinction |
| Verdict reversals from measurement | **STATUS reverted to PRELIMINARY pending B660 (per 2nd-wave-redux #2 owner-approved B665).** Earlier framing of "PRELIMINARY-CONFIRMED-DIRECTIONAL" was a logical slip: B654/B655 confirm that the measurement tool computes fire-rate DIFFERENTIALS correctly (predicting -68% W8 and -97.7% T10 within 5%). Tool-subtraction correctness is INDEPENDENT of whether the absolute fire-rate estimates on the 30-ticker × 2022-2024 sample reflect the T1a universe × 2020-2026. The W2/W4/W6/W7/W8 reversal claims rest entirely on representativeness, which only B660 (in flight) tests. Per critique #4: with universe-count inconsistencies (220 hardcoded / 503 PIT-active / 614 CSV B++) and ×16.77 scale-factor inflation pushing every estimate ~50% higher, the honest status of every fires/yr cell is PENDING B660. Two separate questions; one tool-correctness check (passed); one representativeness check (open). |
| Commits this cycle (B641 → B660) | **24+ commits**, ~30 files, +4500/-300 lines (excl. CSV/JSON output deltas) |

**Bottom line for the reviewer (revised post-follow-on-cycle):** every finding from both audit waves was acknowledged, with code/doc CHANGES merged + tickets QUEUED for everything that requires future work. Zero findings dropped. Of the 22 "changes merged" so far, ~4-5 are fully validated (W3 pin_bar, W10 rename, B654/B655 redundancy-audit predictions confirmed within 5%), and ~17 are improvements awaiting queued validation. The status is incrementally maturing as the follow-on cycle ships fixes that the original critique surfaced — particularly the W8/T10 redundancy fixes whose measured outcomes validated the diagnoses they were meant to address.

The fire-count independence-assumption critique was directionally validated by the measurement tool. The B660 full-universe run (in flight as of doc-write) is the authoritative number set; doc will be back-filled when it lands.

---

## Reviewer findings response matrix

> Every finding from the audit ↔ action taken ↔ where the action lives.

### A. Methodology findings (your adversarial review of the B640 methodology)

| # | Finding | Status | Action | Where |
|---|---|---|---|---|
| **M1** | Fire-count independence-product is biased in both directions depending on gate-correlation sign | ⚠ **CHANGE MERGED, NOT YET VALIDATED** | Built `scripts/measure_fire_count.py` — vectorized measurement + pairwise correlation matrix + independence-ratio diagnostic. **B648 fixed the hardcoded-220 scale-factor bug** (was understating ~2.3×). **NOT YET trustworthy on representative sample** (20-large-cap-survivor + 2022-2024 single-regime); full-universe representative-sample run queued as `S5-FIRE-COUNT-MEASURED-RUN-FULL`. The methodology-takeaway interpretation was also **inverted in the first version** (claimed correlated-gates = well-designed) — corrected B649; redundancy-vs-confluence is now an explicit per-gate question, not auto-inferred from the ratio. | B641 + B648 + B649 |
| **M2** | Same model over-counts high-fire / exclusive-gate strategies | ⚠ **INSTRUMENT EXISTS; RISK NOT RETIRED** | Per 2nd-critique #6: tool detects over-counting (W4/W9 over-counts visible in sample) but the case M2 worried about — a strategy that PASSES on an over-counted estimate and should FAIL — hasn't appeared in the 20-ticker sample because no such strategy exists in this slice. So the over-count detection is instrumented but its risk-retiring effect hasn't been demonstrated. Honest re-framing of original "COVERED BY M1." | B641 + B649 re-framing |
| **M3** | W6 F1 + fire-count claims contradict (auto-pass AND fire-starved) | ✅ DEFERRED | W6 not in Tier 1 ship; measurement showed 917/yr (independence under-counted 500×); deferred to S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY | B641 |
| **M4** | CHECKLIST (g) sequence-or-split applied inconsistently (deferred W7 but bundled W4/W6) | ✅ SHIPPED | W4 SPLIT into F3-only Tier 1 + F1/F2/RSI-mislabel queued as S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL | B641 |
| **M5** | W8 F1b vs W6/W7 default-True severity unification (same auto-pass class, different severity labels) | ✅ SHIPPED + QUEUED | W8 F1+F1b silent-gap fix shipped; W6/W7 LONG default-True unified queue as S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY | B641 |
| **M6** | EVENT/STATE classification is decorative, not wired to a finding | ✅ SHIPPED | CHECKLIST (s) codified: F-timing-fragility finding now produced when ≤1 EVENT gate per direction AND docstring overclaims timing on STATE | B641 (CHECKLIST.md `(s)`) |
| **M7** | W6 MACD STATE silently overclaims (specific instance of M6) | ✅ COVERED BY M6 | The CHECKLIST (s) rule catches this pattern; if W6 ships in a future batch, the audit will flag the MACD-bullish-as-STATE overclaim | B641 |
| **M8** | W5 missing-inverse: economic-symmetry asserted via Wyckoff but expectancy-asymmetry not validated | ⚠ **CHANGES MERGED, COMPLETENESS PARTIAL** | W5 LONG redesigned (B643) + marked EXPLORATORY (B644); W5 SHORT mirror wired symmetrically (B645) WITH explicit expectancy-asymmetry acknowledgment per `feedback_structural_symmetry_not_economic_symmetry`. **Per 2nd-critique #3a:** initial B643 redesign was structurally correct but INCOMPLETE — `above_prev_high` in a sustained decline fires on dead-cat bounces; Wyckoff Spring requires LOW-volume Test bar. **B650 added `vol_below_avg` AND-required** on reversal-trigger (Bulkowski supply-absorption thesis). **Per 2nd-critique #3b:** original {neutral, bear, crisis} regime affinity was correct for pre-B643 same-day fire; post-B643 the strategy buys turn UP TO 5 days later, regime may have transitioned. **B651 expanded to {bull, neutral, bear, crisis}** all regimes. **Per 2nd-critique #5:** W5m wiring with "EXPLORATORY acknowledgment" wasn't enough — cube cannot evaluate the specific risk that makes W5m dangerous. **B652 added stronger DO-NOT-DEPLOY gate** keyed on M10 + S5-MULTIPLE-TESTING-CORRECTION shipping. | B643-B645 + B650-B652 |
| **M9** | `_strat3` avoid-branch dead-code observation absent from all 10 walks (regression from B637 morning_star single-strategy walk) | ✅ SHIPPED | Step 1.5 sub-step restored to CHECKLIST #105 walk template | B641 (CHECKLIST.md Step 1.5) |

### B. Market-structure cross-cutting findings (C1-C6)

| # | Finding | Status | Action | Where |
|---|---|---|---|---|
| **C1** | Pivot / Camarilla / CPR are intraday tools applied on daily bars — category error affecting 8 of 10 in bundle | ✅ CODIFIED + 1 FIRST APPLICATION | CHECKLIST (r) added — walks must reframe-and-rename or defer; W10 R3→R4 rename was first application (Camarilla source-system honesty: R3 = fade per Slim Khan/Nick Scott, R4 = breakout) | B641 (CHECKLIST.md `(r)`) + W10 ship |
| **C2** | Multiple-testing / overfitting at 220 strategies on shared feature set; no FDR / SPA / deflated-Sharpe correction | ✅ QUEUED | `S5-MULTIPLE-TESTING-CORRECTION` ticket — Bailey/LdP deflated Sharpe + Hansen SPA + Benjamini-Hochberg FDR options; gates cube selection step | B641 (`EXECUTION_QUEUE.md`) |
| **C3** | Strategy correlation / illusory diversification (shared OHLCV features → clustered drawdowns); cube must score marginal-vs-book not standalone | ✅ QUEUED | `S5-MARGINAL-CONTRIBUTION-SCORING` ticket; extends existing M9 effective_strategy_count to cube-scoring layer | B641 |
| **C4** | Corporate-action handling unspecified — splits/dividends manufacture engulfing/pivot phantom signals | ✅ QUEUED | `S4-CORPORATE-ACTION-POLICY` ticket — verify Polygon adjustment policy + add ex-date no-fire pyramid test for candle/pivot signals | B641 |
| **C5** | Survivorship bias lethal to W5 + deep-dip longs (left tail deleted from survivor universe) | ✅ QUEUED | `S4-SURVIVORSHIP-T1A-VERIFY` ticket — cross-ref DEC-477 T1a PIT canonical + per-strategy adversarial test for W5; also referenced in W5 EXPLORATORY status | B641 + B644 W5 docstring |
| **C6** | Costs/borrow/gap unmodeled — falls hardest on breakouts (gap fills) + all shorts (borrow, squeeze) | ✅ CROSS-REF | Existing M10 (DEFERRED) ticket extended in EXECUTION_QUEUE.md notes to include borrow lookup + gap-at-entry slippage; remains DEFERRED Stage 5+ | M10 existing |

### C. Per-strategy bugs reviewer flagged in detailed review

| # | Strategy | Finding | Status | Action | Where |
|---|---|---|---|---|---|
| **P1** | W3 `pivot_s1_bounce` | `pin_bar` producer is direction-agnostic; bearish-upper-wick pin AT support could fire LONG | ✅ SHIPPED | Producer-additive `bullish_pin_bar` / `bearish_pin_bar` added to `compute_candle_signals`; LONG side swapped pin_bar → bullish_pin_bar | B641 (`a94f8bb02`) + test_batch641 pins 1-5 |
| **P2** | W4 `pivot_s2_bounce` | Context bullet calls RSI<40 "oversold"; canonical Wilder oversold is 30 — mislabel inflates Step-4 thesis | ⏸ QUEUED | `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` ticket — split per CHECKLIST (g) sequence-or-split into separate shipping batches | B641 queue |
| **P3** | W5 `pivot_s3_capitulation` | No reversal-confirmation trigger — pure knife-catch by construction; survivorship-amplified | ✅ SHIPPED REDESIGN | Option C ship: new `compute_capitulation_lookback` producer (5-bar window) + strategy now requires `recent_capitulation_at_s3` AND reversal-trigger today (bullish_engulfing OR hammer OR above_prev_high). Buys the TURN, not the FALL (Wyckoff Spring/Test sequence). Marked EXPLORATORY per W5-i | B643 (`4157a0c5e`) + B644 (`2acf82cb4`) |
| **P4** | W8 `cpr_narrow_bullish` | `rsi>50/<50` strict-inequality on default-50 is a near-no-op gate; removes ~half the sample but adds little information | ⏸ QUEUED | `S4-W8-RSI-NOOP-GATE` ticket — owner decides post-fire-count-measurement whether to drop, tighten to 55/45, or keep with documented accident-of-luck fail-safe property | B641 queue |
| **P5** | W10 `camarilla_r3_breakout` | R3 is the FADE level in Camarilla (Slim Khan/Nick Scott); R4 is the breakout level. W9 (short R3) + W10 (long above R3) take OPPOSITE trades at SAME level | ✅ SHIPPED RE-ANCHOR | Strategy renamed `strat_camarilla_r3_breakout` → `strat_camarilla_r4_breakout`; producer signals swapped `above_cam_r3`/`below_cam_s3` → `above_cam_r4`/`below_cam_s4`; same-level conflict resolved (W9 now uses R3/S3 proximity FADE; W10 uses R4/S4 BREAKOUT) | B641 + test_batch641 pins 13-17 |
| **P6** | W1/W3/W9 (LONG sides) | OBV-vs-location tension — fresh decline into support means OBV likely below 20-bar mean → `obv_bullish` gate FIGHTS the support premise | ⏸ QUEUED | `S4-OBV-LOCATION-TENSION-DESIGN` ticket — owner-decision among (a) drop OBV gate, (b) reframe to `obv_diverge_bull` (existing producer matches the thesis better), (c) keep as deliberate filter | B641 queue |
| **P7** | W1 `bullish_engulfing_support` | `at_key_fib` swing-anchor selection unspecified — if engine ever calls `compute_fibonacci` on df with future bars, lookahead vector | ⏸ QUEUED | `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` ticket — verify all callsites slice to `as_of` before passing to `compute_fibonacci`; document lookback=50 as hidden free parameter; add pyramid test | B641 queue |

### D. Regime classifier audit findings (the second-wave review)

| # | Finding | Status | Action | Where |
|---|---|---|---|---|
| **R1** | Market-regime sizes single-stock strategies — unstated beta assumption (SPY/VIX state used to gate 222 single-name strategies) | ⏸ QUEUED | `S5-REGIME-BETA-ASSUMPTION` ticket — name the assumption explicitly in CLAUDE.md + dashboards; design options for per-sector or per-name regime in R5+ scope | B641 queue |
| **R2** | Bear ladder dead canonical line — Batch 288 SPY-only gate subsumed the canonical `VIX>=30 AND below-200EMA`; VIX no longer contributes to bear | ✅ SHIPPED | Dead canonical line removed from `classify_regime` + `classify_regime_with_hysteresis`; docstring honestly notes bear = SPY-below-200-EMA only | B642 (`013cc75b8`) |
| **R3** | Hysteresis covers VIX but not SPY-vs-200-EMA (the dominant bear trigger post-B288); architecture guards the wrong variable | ⚠ **CHANGE MERGED, UNVALIDATED DIRECTIONAL BET** | Added `EMA_CROSS_HYSTERESIS_PCT = 2.0` + new `spy_pct_from_200ema` parameter on `classify_regime_with_hysteresis`. Asymmetric design: bear stays sticky until SPY >= +2% above 200-EMA (slow to exit risk-off); below-EMA still triggers bear immediately (fast risk-on→risk-off). **Per 2nd-critique #4:** the asymmetry is a performance-relevant directional bet, NOT a robustness fix — spends more calendar time in bear, sizes longs to 0.5×, would have over-performed in 2022 + under-performed in March 2020 V-shaped recovery. The +2% threshold is hand-set with knowledge of history, adding curve-fit depth (separate from but compounding R8). **Honest re-framing:** asymmetric hysteresis is a tuning choice to validate walk-forward, not a robustness improvement. Walk-forward validation per `S5-REGIME-WALK-FORWARD-VALIDATION` (R8 ticket) determines whether sticky-bear beats symmetric OOS before this can be called a fix. | B642 (`013cc75b8`) + B649 re-framing |
| **R4a** | AAII sentiment publication-vs-survey date PIT lookahead risk | ⏸ QUEUED | `S4-REGIME-AAII-PIT` ticket — pyramid test asserting bear_composite uses publication date, not survey date | B641 queue |
| **R4b** | FRED T10Y2Y vintage revisions — FRED serves latest-vintage by default; backtest uses values as known TODAY not as known on bar date | ⏸ QUEUED | `S4-REGIME-FRED-VINTAGE` ticket — confirm policy in `backtest/data/macro.py`; consider switching to ALFRED (vintage-as-of) | B641 queue |
| **R4c** | Sector-breadth eligibility is time-varying (≥200 bars per ETF; early backtest weaker classifier) | ⏸ QUEUED | `S4-REGIME-SECTOR-ELIGIBILITY-TIME-VARYING` ticket — document the time-varying-classifier window; pre/post-eligibility-threshold-date reporting | B641 queue |
| **R5** | Bear composite "missing input contributes 0" is fail-OPEN while VIX-missing is fail-CLOSED — system asymmetry | ⏸ QUEUED | `S4-REGIME-COMPOSITE-FAIL-POLICY` ticket — owner-policy decision on whether to fail-closed when ≥2 of 3 indicators missing OR explicitly accept asymmetry | B641 queue |
| **R6** | Bear sub-rules + hysteresis have redundant VIX clauses → latent inconsistency that turns into a bug on the next edit | ✅ AUTO-RESOLVED | Side-effect of R2 cleanup — removing the dead canonical line from both `classify_regime` and `classify_regime_with_hysteresis` eliminates the redundancy | B642 |
| **R7** | Hysteresis is opt-in via `use_hysteresis` flag — backtest/analytics may compute different regimes for the same day | ⏸ QUEUED | `S4-REGIME-HYSTERESIS-PARITY-TEST` ticket — audit all callsites; assert production paths use `use_hysteresis=True` consistently | B641 queue |
| **R8** | Whole classifier is curve-fit to backtest history (Batches 288/292/317/388 each tuned to specific failures); is regime-gating OOS net-positive? | ⏸ QUEUED | `S5-REGIME-WALK-FORWARD-VALIDATION` ticket — freeze classifier as-of each historical date + measure forward regime-gating value | B641 queue |

### E. Second-wave external-AI critique findings (2026-06-09, post-cycle review)

After the original review-cycle response (B641-B646), the reviewer ran a second-wave audit on the response itself. Seven new findings; all acknowledged in B648-B652 + B649 re-framing batch.

| # | Finding | Status | Action | Where |
|---|---|---|---|---|
| **2C1** | Measurement is 20-large-cap-survivor + single-regime sample ×11 scaled (220 hardcode); universe count inconsistency 220 vs 614 | ✅ SHIPPED (B648) | Fixed hardcoded `n_tickers_full_t1a=220` → actual `_load_t1a_tickers(as_of)` count (~503 PIT-active per owner directive). Added `--ticker-sample-strategy {first,random,stratified,all}` for representative sampling. Output JSON carries explicit non-representativeness caveat. **Verdict reversals re-labeled as PRELIMINARY pending full-universe run.** | B648 (`850d3119e`) |
| **2C2** | "Correlated gates → well-designed" framing is backwards (codified redundancy as quality) | ✅ SHIPPED (B649) | Inverted in "What the independence ratio is telling us" section — high ratio could mean either confluence OR redundancy; distinguishing requires per-gate "what does THIS screen out that others don't" question. Original (incorrect) framing preserved at end of section for historical reference. W8 cpr_narrow specifically re-characterized as redundancy (4 of 5 gates are uptrend proxies) not confluence. | B649 (this batch; doc-only) |
| **2C3a** | W5 redesign incomplete — `above_prev_high` could fire on dead-cat bounce; needs Wyckoff-Spring LOW-volume condition | ✅ SHIPPED (B650) | Added `s.get("vol_below_avg")` AND-required on reversal-trigger bar (Bulkowski/Wyckoff supply-absorption thesis). New B650 test pin verifies all-3-reversal-triggers-True-without-vol_below_avg does NOT fire. | B650 (`c0746d6a5`) |
| **2C3b** | W5 regime affinity stale post-B643 redesign — entry was correct for pre-redesign same-day fire; post-redesign strategy buys turn up to 5 days later when regime may have transitioned | ✅ SHIPPED (B651) | Expanded `STRATEGY_REGIME_AFFINITY['pivot_s3_capitulation']` from `{neutral, bear, crisis}` to `{bull, neutral, bear, crisis}` all regimes. | B651 (`c0746d6a5`) |
| **2C4** | R3 EMA-cross hysteresis is asymmetric in dangerous direction (sticky-bear bet) — claimed as "robustness fix" but is actually unvalidated performance-relevant tuning | ✅ RE-FRAMED (B649) | Doc re-framing in R3 row above: from "✅ SHIPPED" to "⚠ CHANGE MERGED, UNVALIDATED DIRECTIONAL BET." Walk-forward validation per `S5-REGIME-WALK-FORWARD-VALIDATION` determines whether sticky-bear beats symmetric OOS before this can be called a fix. **Code unchanged** — the hysteresis stays in for now since reverting it would require another walk-forward validation cycle; framing is now honest. | B649 doc-only |
| **2C5** | W5m wired with "EXPLORATORY acknowledgment" but cube cannot evaluate the specific risk (squeeze tail + cost-aware unmodeled per C6 + selection bias unmodeled per C2) | ✅ SHIPPED (B652) | Added explicit DO-NOT-DEPLOY gate in W5m docstring keyed on BOTH M10 (cost-aware cube) AND S5-MULTIPLE-TESTING-CORRECTION shipping. Strategy stays REGISTERED for dataflow/cube-replay coverage but must NOT be promoted to live trade routing until both pre-deployment gates land. | B652 (`c0746d6a5`) |
| **2C6** | M2 "COVERED BY M1" is too quick — tool detects over-counts but the case M2 worried about (PASS on over-count, should FAIL) hasn't appeared in 20-ticker sample | ✅ RE-FRAMED (B649) | M2 status updated above from "COVERED BY M1" → "instrument exists; risk not retired." | B649 doc-only |
| **2C7** | "SHIPPED" is doing heavy lifting for "changes merged"; ~3 of the 12 are actually validated, rest await measurement/walk-forward/survivorship | ✅ RE-FRAMED (B649) | Executive summary table reformatted with explicit CHANGES-MERGED vs VALIDATED-RESOLUTIONS decomposition. Honest scorecard: of 15+ changes merged, ~5 are fully validated; the rest are improvements awaiting queued validation work. | B649 doc-only |

### Section E.1 — Post-B652 follow-on cycle (B653 → B660)

> After the original B641-B652 cycle plus the B649 honest re-framing, four trailing items shipped on the same set of audit findings. Listed below in chronological order with the specific 1st- or 2nd-wave finding each one resolved. The follow-on cycle predominantly closed M5 (silent-gap default-True unification) + 2C2 (per-gate redundancy distinction) + new tickets opened in B641 that hadn't yet been touched.

| # | Batch | Finding closed | Action | Where |
|---|---|---|---|---|
| **F1** | **B653** | M1 (measurement-pass output not trustworthy on single-regime small sample) | Random-30 sample with seed-42 + B648 ×16.77 universe-scale projection. Two output files: pivot-cluster B640 strategies + W5m + B647 trend cluster T1-T10. Per-strategy fires/yr + independence-ratio + non_representativeness_caveat embedded. | `output_audit/fire_count_measured_b648_b640_random30.json` + `output_audit/fire_count_measured_b648_w5m_trend_random30.json` |
| **F2** | **B654** | M5 + P4 (W8 RSI-noop + 2C2 W8 redundancy thesis) | Producer-additive `cpr_narrow_tight` (0.05 threshold; B574-style narrow-scope; W8-only consumer; other 2 `cpr_narrow` consumers retain 0.15 threshold per `feedback_narrow_scope_blast_radius`). RSI-50 strict-inequality gates dropped (`rsi_14 > 50` LONG / `< 50` SHORT) per `feedback_never_use_NOT_s_get_pattern` precedent. **Validates 2C2 corrected methodology:** W8 fires/yr 34,004 → 10,723 (-68%) on random-30 sample post-fix, confirming the 4-of-5 LONG gates "established uptrend" thesis. Closes both **S4-W8-REDUNDANCY-AUDIT** and **S4-W8-RSI-NOOP-GATE**. | B654 (`d6d9ebe2b`) + `output_audit/fire_count_measured_b654_w8_post_redundancy_fix.json` |
| **F3** | **B655 + B656 + B657** | (cross-cluster) Trend-cluster redundancy audits per 2C2 corrected methodology — T10/T3/T8 | T10 `strat_supertrend_macd`: STATE `supertrend_bullish` (99.19% True on B648 random-30 = EXTREME NO-OP) → EVENT-anchored `supertrend_flip_recent_long_5d` / `_short_5d` 5-bar window per B643/B645 producer-additive pattern. Fires/yr 33k → 772 (-97.7%). T3 `strat_hull_rsi`: per-gate audit found 4 distinct gates measuring uptrend semantics from different angles = HONEST CONFLUENCE not redundancy; option A status-quo on confluence + option C drop RSI-50 noop. T8 `strat_ichimoku_cloud_breakout`: same honest-confluence finding + DEFAULT-TRUE silent-gap on weekly Kumo signals (B639 / B641 / B657 silent-gap family) — option E (A status-quo + D default-True → False). All three documented in `STAGE_4_TREND_CLUSTER_WALKS.md`. | B655-B657 + B658 measurement landing (`661bff8ed`); see [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) |
| **F4** | **B659** | M5 + S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY (silent-gap default-True unification) + S4-W5M-SYMMETRIC-VOL-GATE + S4-T3-NOT-ABOVE-200-EMA-PATTERN | **Bundled autonomous batch per owner directive 2026-06-09** "Remaining queued items from this cycle... implement autonomously". Five strategies touched: W6 + W7 + W8 LONG AVWAP defaults `True` → `False` symmetric with SHORT side (closes M5); W5m `vol_below_avg` AND-required on reversal-trigger bar (symmetric Wyckoff Distribution Upthrust-Test mirror of B650 W5 LONG Spring vol gate); T3 SHORT `(not above_200)` → positive symmetric `s.get("below_ema_200", False)` per `feedback_never_use_NOT_s_get_pattern`. 14-pin test file `test_batch659_silent_gap_unify.py` + 4 fixture updates in B645 + B656 test files (commit `db2dda419`). | B659 (`3f6a0ae1b`) + follow-up (`db2dda419`) |
| **F5** | **B660** | M1 (full-universe representative-sample measurement) | Background job `S5-FIRE-COUNT-MEASURED-RUN-FULL` — T1a PIT-active × 2020-2026 × all 222 strategies. Replaces the 30-random-ticker × 2022-2024 PRELIMINARY numbers across both pivot + trend cluster docs once landed. **STATUS: IN FLIGHT at time of doc write — see [pending-numbers caveat below](#measurement-status--b660-full-universe-in-flight).** | B660 background task; output → `output_audit/fire_count_measured_b660_full_universe.json` |

### Aggregate (revised post-follow-on-cycle)

- **24 first-wave + 7 second-wave = 31 findings raised across both review waves.**
- **22 CHANGES MERGED** (was 18 at B652-close; B654 + B655/B656/B657 trend-cross-cluster + B659 bundle = 4 additional closures on M5, P4, 2C2-W8, 2C2-T10/T3/T8, S4-W5M-SYMMETRIC-VOL-GATE, S4-T3-NOT-ABOVE-200-EMA-PATTERN).
- **17 first-wave tickets** in `EXECUTION_QUEUE.md` originally; **of those 4 closed by follow-on cycle** (S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY = B659; S4-W8-RSI-NOOP-GATE + S4-W8-REDUNDANCY-AUDIT = B654; S4-W5M-SYMMETRIC-VOL-GATE = B659; S4-T3-NOT-ABOVE-200-EMA-PATTERN = B659). **13 first-wave tickets remain open** + 8 new tickets surfaced by the audit responses themselves (cost-aware cube, multiple-testing correction, marginal-contribution scoring, regime walk-forward, etc).
- **2 closed-by-design** (R6 auto-resolved by R2; M7 covered by M6's CHECKLIST (s)). **M2 status revised** from closed-by-design to "instrument exists; risk not retired."
- **Of the 22 CHANGES MERGED, ~4-5 are fully validated** (W3 pin_bar fix + W10 R3→R4 rename + B641 CHECKLIST extensions r/s/Step 1.5 — original 3 — PLUS **B654 W8 redundancy-fix prediction matched measurement to within 5%** + **B655 T10 STATE→EVENT prediction matched within 5%**); the rest await queued work.
- **0 findings dropped, deferred-silently, or claimed-irrelevant** across both review waves.

---

### Process Meta — ticket arithmetic + foundational re-prioritization (per 2nd-wave-redux #9, owner-approved B665)

> Per critique #9: "the cycle is now generating tickets faster than it closes foundational ones, and the foundational ones are all still open." Owner accepted the finding + the foundational re-prioritization commitment unchanged. This section codifies the ticket arithmetic + the next-batch priority.

**Ticket arithmetic since B641:**

| Cycle | First-wave closed | New tickets opened | First-wave remainder | Net open delta |
|---|---|---|---|---|
| B641-B645 originals | 0 (cycle established 17 first-wave tickets) | +17 | 17 | +17 |
| B649 + B650-B652 follow-on | 0 doc-only re-framing batch | +0 | 17 | 0 |
| B654 + B655-B657 + B659 closures | 5 (S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY + S4-W8-REDUNDANCY-AUDIT + S4-W8-RSI-NOOP-GATE + S4-W5M-SYMMETRIC-VOL-GATE + S4-T3-NOT-ABOVE-200-EMA-PATTERN) | +8 (new tickets from 2nd-wave critique responses) | 12 | +3 |
| B663 ema_200 family sweep | 1 (S4-EVENT-DRIVEN-DEFAULT-TRUE-EMA-SWEEP — closed via SM-1 walk) | +0 | 11 | -1 |
| **B665 (this batch)** | 0 | +3 (`S5-W8-POST-B654-REMAINING-REDUNDANCY-AUDIT`, `S5-DO-NOT-DEPLOY-MULTIPLE-TESTING-RECONCILIATION`, `S5-W5-BULL-REGIME-IDIOSYNCRATIC-FALLING-KNIFE`) | 11 | +3 |
| **Net open after B665:** | — | — | — | **+22 from cycle start** |

**The discipline reality (per critic):** local code-hygiene tickets close fast and generate satisfying validation-able predictions (B663 closed 4 of 17 in one batch; B654 closed 3 of 17 in one batch). Foundational tickets are hard and open-ended, so they accrete. The pattern repeats: after 20+ batches, the strategies are cleaner but the program-level validity questions that gate the entire enterprise — **C2** (multiple-testing correction), **C3** (marginal-contribution scoring), **C5** (survivorship verification), **C6** (cost/borrow modeling), **R8** (regime walk-forward validation), **B660** (full-universe measurement — IN FLIGHT only) — remain untouched. The strategies are cleaner; the answer to "does any of this make money out of sample" is no closer.

**Foundational re-prioritization commitment (owner-approved B665):** after B665 ships, the next batch is NOT another cluster walk. Specifically:

1. **B660 lands first** (background measurement run). All `fires/yr` cells in this doc + STAGE_4_TREND_CLUSTER_WALKS.md + STAGE_4_SMART_MONEY_CLUSTER_WALKS.md get re-populated with full-universe representative numbers. PRELIMINARY qualifier retires. Verdict reversals move from PRELIMINARY (B665 revert) to either AUTHORITATIVE or retracted, based on actual data.
2. **Then C2 methodology** (multiple-testing correction) — even a draft methodology with parameters chosen openly is better than zero. Output: a `multiple_testing_correction.py` module + a Stage-D-cube-gating policy document specifying which correction (deflated Sharpe / Hansen SPA / BH-FDR), parameter choices, and registered-vs-DO-NOT-DEPLOY policy per `S5-DO-NOT-DEPLOY-MULTIPLE-TESTING-RECONCILIATION` interaction.
3. **Then C5 survivorship verification** — adversarial test for W5 LONG (left tail) + W5m SHORT (right-tail squeeze risk) using the DEC-477 T1a delisted-during-window names. Output: per-strategy survivorship sensitivity report.

**The smart money cluster B664 candidate is HELD until B665 ships** (per owner directive). After B665, B664 can re-apply the same corrected framing standards from the start — no retrofit needed.

**The trade-off accepted:** local code hygiene cleanup pauses. The strategies don't get further-cleaner during the foundational work. That's the correct trade-off because the cleaner strategies don't help if PASS_CUBE labels remain pending-B660 forever.

### B659 5-strategy autonomous bundle vs CHECKLIST (g) retrospective (per 2nd-wave-redux #5, owner-approved B665)

> The B659 "implement autonomously" bundle (W6 + W7 + W8 LONG default-True→False + W5m vol_below_avg + T3 SHORT below_ema_200) shipped 5 gate changes across 5 strategies in one batch. The follow-up commit `db2dda419` also updated test fixtures for B645 (W5m) + B656 (T3) — direct evidence of test-level entanglement between the B659 changes and the prior batches' assertions. **Per critic #5: this is the kind of multi-strategy simultaneous-change bundle that CHECKLIST (g) was invoked to prevent.**

**Honest reading:** each individual fix was a one-line silent-gap correction at a different gate in a different strategy; the fixture syncs were of test fixtures asserting pre-change semantics, not behavioral entanglements between strategies. But:
- The (g)-waiver question was not surfaced or owner-approved at batch time
- The "autonomous" directive was used as a substitute for the sequencing discipline (g) requires
- Future autonomous batches need explicit (g)-waiver guard-rails

**(g)-waiver rule codified (B665 CHECKLIST addition):** future autonomous / bulk-clear batches MUST:
1. Affirm independence at batch time — no fixture sync expected across batches; no shared producer changes
2. OR explicitly request a (g)-waiver in the commit message with owner-approval recorded
3. List every test fixture that needs synced as part of the (g)-waiver justification (so the entanglement evidence is on the record, not hidden in a follow-up commit)
4. (g)-waiver auto-required when the autonomous bundle touches ≥3 strategies OR ≥2 producers

The new rule applies prospectively from B665 onward. The B659 retrospective gap is acknowledged as the rule's motivating case.

### Universe-count + scale-factor reconciliation (per 2nd-wave-redux #4, owner-approved B665)

> **Three different universe counts have appeared across the measurement pipeline.** The earlier doc cited each at different points without reconciling them. This section catalogs the three values explicitly + the ×16.77 multiplier interaction surfaced by the critic.

| Universe value | Source | Status |
|---|---|---|
| **220** | Hardcoded `n_tickers_full_t1a = 220` in `scripts/measure_fire_count.py` (B641 original) | DEPRECATED B648 (was understating projections ~2.3× — caught by critic #1) |
| **503** | Actual T1a PIT-active count at as_of via `_load_t1a_tickers(as_of)` (B648 fix) | What `--ticker-sample-strategy random` × ×16.77 scale-factor uses post-B648 |
| **614** | Full T1a CSV B++ schema (DEC-477) including 111 historical-removed-during-window | Survivorship-question-aware value; what `S4-SURVIVORSHIP-T1A-VERIFY` audits |

**The ×11 → ×16.77 scale-factor change (B648):** B641 used 220/20 = ×11; B648 used 503/30 ≈ ×16.77 (PIT-active T1a divided by random-30 sample size). The ratio increased ~52%, mechanically inflating every fires/yr estimate by the same ratio. This pushed W1 337 → 671, W3 220 → 447, W10 991 → 2394 — **all of which the doc earlier reported as "validating" PASS_CUBE verdicts, when in reality the scale-factor multiplier increase alone explains the move from below-threshold to above-threshold.**

**The representativeness flaw the scale-factor cannot fix:** any linear multiplier — ×11, ×16.77, or ×17.13 (614/30) — assumes the 30-ticker sample fires at the same per-ticker rate as the full T1a universe. This is exactly the assumption B648 sampling-strategy randomization was supposed to mitigate, but with only 30 tickers across a 2022-2024 single-regime arc, the sample variance dominates. **Per critic #4: "a bigger multiplier on a non-representative base is not more accurate; it's more confidently wrong."** The only remediation is B660 (full-universe representative-sample measurement across 2020-2026).

**B665 disposition:** every `PASS_CUBE` / `FAIL` / `BORDERLINE` label that was generated by ×16.77 multiplication of the 30-ticker sample is **PENDING B660**. The bold `PASS_CUBE` labels throughout the Cluster current state table + per-strategy FINAL STATUS blocks are retained as historical record but should be read as "preliminary measured + needs full-universe confirmation." The W2/W4/W6/W7 fail-to-pass reversals specifically are demoted from "PRELIMINARY-CONFIRMED-DIRECTIONAL" (per critique #2 strike) back to "indeterminate pending B660."

**What B660 must report when it lands:** per-regime clustered fire counts (NOT a single annualized smear), so the strategy verdicts can be evaluated against the regime-by-regime min_trades=30 per-regime threshold rather than the easier overall ≥100 floor. The annualized total can mask a strategy that fires 100×/yr in bull but never in bear, when the regime affinity entry says "fires in bear" — the latter would be a measured-zero failure that the annualized smear hides.

### Measurement status — B660 full-universe in flight

> Every `Measured fires/yr` value in the [Cluster current state](#cluster-current-state) table and per-strategy FINAL STATUS blocks below is the **PRELIMINARY random-30 × 2022-2024 × B648-scale projection** unless explicitly noted as "post-B654" or "post-B655 fix-remeasure." Authoritative full-universe values land when **`S5-FIRE-COUNT-MEASURED-RUN-FULL` (B660)** completes its background run.
>
> **What changes when B660 lands:**
> - The PRELIMINARY caveat is retired from each table cell.
> - All `Measured fires/yr` columns repopulate with authoritative numbers.
> - Three independent sample re-runs (B641 smoke 20-ticker × 2022-2024, B648 random-30 × 2022-2024, B660 full-universe × 2020-2026) provide a sensitivity envelope per strategy — if B660 numbers swing >50% from B648, the strategy needs a per-strategy reconciliation block.
> - The "Verdict reversals from measurement" executive-summary line moves from PRELIMINARY (post-B665 revert per critique #2) to AUTHORITATIVE.
>
> **What doesn't change:** the structural and code-level findings (W3 pin_bar fix, W10 rename, W8 cpr_narrow_tight, T10 EVENT swap, W5/W5m vol gates, W6/W7/W8 default-False unify) are independent of fire-count and stand on their own merits — measurement quantifies impact but doesn't re-justify the fixes.

---

## Cluster current state

> Snapshot of every strategy in this doc + W5 mirror (Class 7 NEW B645). For each: original B640 verdict, what shipped, current status, measured fires/year (universe-projected from 20-ticker × 3-year sample run via `scripts/measure_fire_count.py`).

| W# | Strategy | Cluster | Direction | B640 verdict | Shipped action | Final status | Measured fires/yr |
|---|---|---|---|---|---|---|---|
| W1 | `bullish_engulfing_support` | candle | dual | PASS | F2 docstring + "three systems" commentary fix | ✅ CLOSED | **671** PASS_CUBE (revised post-B648 random-30 sample × 16.77 scale; was 337 pre-fix) |
| W2 | `shooting_star_short` | candle | SHORT | FAIL (proj) | F2 docstring; Stage 5 fire-count defer | ✅ CLOSED | **291** PASS_CUBE (B640 FAIL was independence-product artifact; revised numbers) |
| W3 | `pivot_s1_bounce` | pivot | dual | PASS | F1 pin_bar direction-fix + F2 docstring + F3 regime entry delete (B271 family-bug) | ✅ CLOSED | **447** PASS_CUBE |
| W4 | `pivot_s2_bounce` | pivot | dual | borderline | F3 regime entry delete only; F1/F2/RSI-mislabel SPLIT per CHECKLIST (g) | ✅ SHIPPED + 🎯 queued | **PENDING B660** (per 2nd-wave-redux #3 B665 revert — earlier "73 PASS_CUBE" was sampling-artifact, NOT physics; over-count corrections push down not up; see W4 reconciliation block) |
| W5 | `pivot_s3_capitulation` | pivot | LONG | FAIL | B643 option C redesign + B644 EXPLORATORY + **B650 `vol_below_avg` Wyckoff-Spring gate** + **B651 regime expand all-regimes** | ✅ REDESIGNED → EXPLORATORY | **11.2 FAIL** (post-B650 vol gate is more selective; was 18.3 pre-B650; correct rare-event behavior — capitulation + LOW-volume Test is genuinely rare) |
| W5m | `pivot_r3_blowoff_short` | pivot | SHORT | (new) | B645 Class 7 NEW + B652 stronger DO-NOT-DEPLOY gate (keyed on M10 + S5-MULTIPLE-TESTING-CORRECTION) + **B659 `vol_below_avg` AND-required symmetric Wyckoff Upthrust-Test vol gate (closes S4-W5M-SYMMETRIC-VOL-GATE)** | ✅ NEW → EXPLORATORY+DO-NOT-DEPLOY | **61.5 PASS_CUBE PRELIMINARY** (B648 random-30 × 16.77 scale; expected to drop ~30-40% post-B659 vol-gate addition; pending B660 full-universe). Now structurally symmetric with B650 W5 LONG: both require LOW-volume reversal/Test bar (Wyckoff Spring on LONG = supply-absorbed Selling Climax Test; Upthrust-Test on SHORT = demand-absorbed Buying Climax Test). |
| W6 | `pivot_r1_breakout` | pivot | dual | FAIL (proj) | Deferred at B641 (F1 + fire-count contradicted); **B659 LONG AVWAP default-True → False symmetric with SHORT (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY)** | ✅ SHIPPED B659 | **2617** PASS_CUBE PRELIMINARY (B648 random-30); independence under-counted 500× on pre-B659 sample. Post-B659 expected modest drop (fail-safe to no-fire on missing AVWAP keys eliminates the auto-pass-on-missing path that was inflating the SOLID-uptrend co-occurrence on tickers with insufficient history); B660 to quantify. |
| W7 | `pivot_r2_continuation` | pivot | dual | FAIL (proj) | Deferred at B641 (6-gate over-specification, sample-size destroyer); **B659 LONG AVWAP default-True → False symmetric with SHORT (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY)** | ✅ SHIPPED B659 | **224** PASS_CUBE PRELIMINARY (B648 random-30); post-B659 minor expected drop. The 6-gate width concern persists — even at 224/yr the strategy may be curve-fit by gate-stacking; cube empirical adjudicates. |
| W8 | `cpr_narrow_bullish` | pivot | dual | FAIL (proj) | B641 F1+F1b silent-gap fix (SHORT NOT-pattern → positive symmetric); **B654 producer-additive `cpr_narrow_tight` (0.05 threshold; W8-only consumer) + RSI-50 noop drop + B659 LONG `above_avwap_50low` default-True → False (closes S4-W8-REDUNDANCY-AUDIT + S4-W8-RSI-NOOP-GATE + part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY)** | ✅ SHIPPED B641 + B654 + B659 | **34,004 PASS_CUBE → 10,723 PASS_CUBE PRELIMINARY** post-B654 (-68% on same random-30 sample; per `output_audit/fire_count_measured_b654_w8_post_redundancy_fix.json`). The 34k → 10.7k drop validates the 4-of-5-LONG-gate redundancy thesis (B649 corrected methodology) — once the no-op RSI-50 gate dropped AND the cpr_narrow threshold went from 0.15 (fires ~87% of bars) to 0.05 (fires ~15% of bars), the strategy reverts to a more conventional 4-day-cycle fire rate. The post-B659 LONG default-False fix expected to drop slightly further on tickers with insufficient AVWAP-anchor history; B660 to quantify. |
| W9 | `camarilla_s3_bounce` | pivot | dual | borderline | No action — already deferred per `S5-REGIME-AFFINITY-21-DEFERRED` (existing R5 ticket) | ⏸ ALREADY DEFERRED (R5) | **67** PASS_CUBE (revised — moved from BORDERLINE to PASS on random-30 sample; independence over-counted 37×) |
| W10 | `camarilla_r4_breakout` (renamed from `_r3_`) | pivot | dual | PASS | R3→R4 source-system re-anchor (Camarilla: R3=fade, R4=breakout per Slim Khan/Nick Scott); resolves W9/W10 same-level conflict; F2 docstring | ✅ CLOSED (renamed + re-anchored) | **2394** PASS_CUBE (revised) |

**Source for the PRELIMINARY fires/yr column:**
- Most rows: [`output_audit/fire_count_measured_b648_b640_random30.json`](output_audit/fire_count_measured_b648_b640_random30.json) — 30 random tickers (seed 42) × 2022-2024 × B648-corrected ×16.77 projection scale. Pre-B654 + pre-B659 gate sets.
- W5m row: [`output_audit/fire_count_measured_b648_w5m_trend_random30.json`](output_audit/fire_count_measured_b648_w5m_trend_random30.json) — same random-30 sample. Pre-B659 gate set (W5m vol_below_avg AND-gate now in but measurement is pre-B659).
- W8 row (post-B654): [`output_audit/fire_count_measured_b654_w8_post_redundancy_fix.json`](output_audit/fire_count_measured_b654_w8_post_redundancy_fix.json) — re-measured against same random-30 with the new gate set post-B654 (cpr_narrow_tight 0.05 + RSI-50 noop dropped).

**Caveats per B649 framing (PRELIMINARY measured / pending full-universe verification):** even with corrected scaling + random sampling, this is still 30 tickers across one regime arc (2022-2024). Per critique #1: "specific verdict reversals are HYPOTHESES, not results." Authoritative numbers require `S5-FIRE-COUNT-MEASURED-RUN-FULL` = B660 (`--max-tickers 0` across multiple regimes, 2020-2026; **IN FLIGHT** at time of doc-write).

**Strategy buckets (per `feedback_strategy_counts_by_buckets_each_turn`, source-of-truth `ALL_STRATEGIES` at `db2dda419`):**

- Total registered: **222** (B640 baseline 221 → B645 +1 W5 mirror = 222; unchanged through B660)
- Active for cube: **221** (222 − 1 disabled `dxy_headwind_multinational_short`)
- Deprecated: **0**
- Disabled: **1**
- **EXPLORATORY (B644/B645): 2** (`pivot_s3_capitulation`, `pivot_r3_blowoff_short`)

**Cross-cluster status snapshot (this pivot doc + companion docs):**
- **Pivot cluster** (this doc): 8 of ~10 pivot strategies walked (W3-W10 + W5 mirror); `prev_day_high_break` + any tail strategies pending. STATUS: **LIVING — closed-out for B641-B660 cycle.**
- **Trend cluster** ([STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md)): T1-T10 walked; T3/T8/T10 redundancy audits closed (B656/B657/B655). STATUS: **LIVING — closed-out for cycle.**
- **Other clusters** (chart pattern, smart money, SMC/ICT, volume, calendar, macro/sector/news, mean reversion, confluence): **PENDING.**
- Total strategy buckets covered by Stage 4 walks so far: **~67 of 222 = 30% complete** (this doc + trend doc + earlier ad-hoc walks like B636 three_white_soldiers, B639 morning_star, B572-574 doji, B580/581 ICT batch, B591/603-607 cluster walks).

---

## Table of contents

1. [How to read this document](#how-to-read-this-document)
2. [Foundations — every term defined once](#foundations)
   - Sub-section worth reading first if regimes are unfamiliar: **[How market regimes are classified — the full picture](#how-market-regimes-are-classified--the-full-picture)** (inputs, threshold ladder, bear composite override, hysteresis, what the regime *does* once classified, worked example)
3. [The 7-step walk methodology](#the-7-step-walk-methodology)
4. [Cross-strategy summary table](#cross-strategy-summary-table) — read this first if you're short on time
5. Per-strategy walks
   - [W1. `strat_bullish_engulfing_support`](#w1-strat_bullish_engulfing_support) — candle dual
   - [W2. `strat_shooting_star_short`](#w2-strat_shooting_star_short) — candle single SHORT
   - [W3. `strat_pivot_s1_bounce`](#w3-strat_pivot_s1_bounce) — pivot dual
   - [W4. `strat_pivot_s2_bounce`](#w4-strat_pivot_s2_bounce) — pivot dual
   - [W5. `strat_pivot_s3_capitulation`](#w5-strat_pivot_s3_capitulation) — pivot single LONG
   - [W6. `strat_pivot_r1_breakout`](#w6-strat_pivot_r1_breakout) — pivot dual
   - [W7. `strat_pivot_r2_continuation`](#w7-strat_pivot_r2_continuation) — pivot dual
   - [W8. `strat_cpr_narrow_bullish`](#w8-strat_cpr_narrow_bullish) — pivot dual
   - [W9. `strat_camarilla_s3_bounce`](#w9-strat_camarilla_s3_bounce) — pivot dual
   - [W10. `strat_camarilla_r3_breakout`](#w10-strat_camarilla_r3_breakout) — pivot dual
6. [Bundled action items + my recommendations](#bundled-action-items)
7. [Owner decision form](#owner-decision-form)

---

## How to read this document

Each strategy walk is **self-contained** — you can jump to W4 or W7 directly without reading W1-W3. Repeated terms are cross-linked back to the [Foundations](#foundations) section.

Within each walk:
- **Step 1** is the code itself, gate-by-gate, with every numeric threshold explained.
- **Steps 2-6** are diagnostic checks — usually short.
- **Step 7** is **the actionable part**. It surfaces findings, presents options (A / B / C / etc), and gives my recommendation. **This is what you respond to.**

Findings use these severity tags:
- **F1** = bug or thesis-vs-implementation mismatch. High priority. Usually needs a code change.
- **F2** = documentation gap (no docstring, mis-cited source, no explanation of thresholds). Low priority.
- **F3** = regime-affinity issue (the strategy is gated to only fire in certain market regimes; entry may be wrong).
- **F4-F9** = secondary findings (data-source asymmetry, dead code, missing inverse, etc.).

If you only want to approve / reject, jump to the [Owner decision form](#owner-decision-form) at the bottom.

---

## Foundations

### What "the codebase" actually does, at a high level

This is a stock-trading backtest engine. Every day, for every stock in our 220-ticker universe, the engine:

1. **Computes signals** — boolean flags and numeric values describing the stock's state today. Examples: `rsi_14 = 28.5` (a momentum reading), `morning_star = True` (a candle pattern just formed), `above_r1 = True` (price is above resistance level R1). Produced by functions in `backtest/signals/technical.py`. We call these functions **producers**.

2. **Runs strategies** — each strategy (220 of them) is a Python function that reads some signals and decides "should I open a long position?", "should I open a short position?", or "no signal today." Strategies live in `backtest/signals/screener.py`. They are **consumers** of producer signals.

3. **Logs the trades** — when a strategy fires, the engine opens a position the next bar at the open price (we always model entry at next-bar open, never same-bar close — this is a "point-in-time" or PIT discipline rule).

Each strategy lives in one Python function named `strat_<name>(s)` where `s` is the signals dict for one (ticker, day) pair.

### Long, short, and "dual" strategies

- **LONG** = "buy this stock; profit if it goes up."
- **SHORT** = "borrow and sell this stock; profit if it goes down."
- **Dual** = one strategy function that can fire EITHER a long OR a short signal, depending on which gates trigger. Dual strategies use the helper `_strat3(fl, fs, ...)` and have *two* gate sets internally (one for LONG = `fl`, one for SHORT = `fs`).
- **Single-direction** = the strategy only ever fires one way. Uses `_strat(fires, "long"|"short", ...)`.

### `_strat3` — the dual strategy framework

When you see `return _strat3(fl, fs, ...)` it means:

| `fl` (long fires) | `fs` (short fires) | Result |
|---|---|---|
| True | False | **LONG** position opened |
| False | True | **SHORT** position opened |
| True | True | **AVOID** — conflicting signals, engine skips |
| False | False | No signal |

The `AVOID` branch only matters if both gate-sets can be simultaneously true on the same bar — rare in practice (pattern detectors usually mutually exclude).

### `s.get(key, default)` — the signal dict access pattern

This is Python's "look up `key` in dictionary `s`; if missing, return `default`."
- `s.get("morning_star")` → returns True/False if the key exists, returns `None` if missing. `None` is "falsy" so it fails gate checks.
- `s.get("rsi_14", 50)` → returns the RSI value if present, returns **50** (a neutral default) if missing. **Important:** this default-50 is "fail-safe" only if the gate's threshold doesn't cross 50. We tracked this as a known silent-gap class in B639 / queued ticket `S5-RSI-DEFAULT-50-FAMILY`.

### Producer signals you'll see repeatedly

Defined once here; referenced throughout the walks. Producer line numbers point to `backtest/signals/technical.py`.

| Signal | What it means | How it's computed | Producer |
|---|---|---|---|
| **`rsi_14`** | 14-period Relative Strength Index. 0-100 scale. ~30 = oversold, ~70 = overbought, 50 = neutral. | Wilder exponential smoothing per Wilder 1978 (the canonical formula); `alpha = 1/14`. | [L268-308](backtest/signals/technical.py#L268-L308) |
| **`ema_50_200_bullish`** | True when 50-period exponential MA > 200-period EMA. Classic long-term uptrend gauge. | `close.ewm(span=50).mean() > close.ewm(span=200).mean()` | [L508](backtest/signals/technical.py#L508) |
| **`ema_50_200_bearish`** | Symmetric mirror — True when 50-EMA < 200-EMA. Added B634 to fix a silent-gap. | `< instead of >` | [L510](backtest/signals/technical.py#L510) |
| **`macd_12_26_9_bullish`** | True when MACD histogram > 0 (12/26 EMA difference's 9-period signal-line is BELOW the MACD line). Classic short-to-medium momentum gauge. | `macd_line - signal_line > 0` | [L368-394](backtest/signals/technical.py#L368-L394) |
| **`macd_12_26_9_bearish`** | Symmetric mirror — `hist < 0`. Added B609 for silent-gap fix. | `< instead of >` | [L394+](backtest/signals/technical.py#L394) |
| **`obv_bullish`** | True when On-Balance Volume > 20-bar rolling mean of OBV. OBV is cumulative volume signed by daily up/down direction; a "money-flow" indicator. | `obv.iloc[-1] > obv.rolling(20).mean().iloc[-1]` | [L1138](backtest/signals/technical.py#L1138) |
| **`obv_bearish`** | Mirror. Added B617 for silent-gap fix. | `< instead of >` | [L1147](backtest/signals/technical.py#L1147) |
| **`vol_spike_15x`** | Today's volume ≥ 1.5× the 20-day average volume. "Volume confirmation." | `today_vol / vol.rolling(20).mean() >= 1.5` | [L1179](backtest/signals/technical.py#L1179) |
| **`vol_spike_2x`** | ≥ 2.0× — stronger volume confirmation. | `>= 2.0` | [L1182](backtest/signals/technical.py#L1182) |
| **`adx_trending`** | True when 14-period ADX > 25. ADX measures trend strength regardless of direction; >25 = trend is in force (per Wilder). | `adx_14 > 25` | [L587](backtest/signals/technical.py#L587) |
| **`above_avwap_252low`** | True when today's close > Anchored VWAP measured from the 252-day low. AVWAP anchors VWAP at a meaningful prior price point (Brian Shannon 2022 *Maximum Trading Gains with Anchored VWAP*). | Cumulative `(typical price × volume) / cumulative volume` from anchor date forward; compare to close. | [L240-260](backtest/signals/technical.py#L240-L260) |
| **`above_avwap_50low`** | Same, anchored at the 50-day low. | Same formula, shorter anchor. | Same |
| **`below_avwap_252low`** / **`below_avwap_50low`** | Symmetric mirrors. Added B612. | `<` instead of `>` | [L259](backtest/signals/technical.py#L259) |
| **`bb_20_20_touch_upper`** | True when today's close ≥ 0.995 × upper Bollinger Band (20-period, 2.0 std). The upper BB is a volatility-based resistance. | `close >= bb_upper * 0.995` | [L975](backtest/signals/technical.py#L975) |

### Candle patterns (every one used in this bundle)

Defined in `compute_candle_signals` starting at [technical.py:1425](backtest/signals/technical.py#L1425).

| Pattern | What the bar looks like | Strict definition |
|---|---|---|
| **`doji`** | Indecision — open and close almost equal. | body < 5% of bar's high-low range |
| **`hammer`** | Long lower wick, small body near top. Bullish single-bar reversal. | `lower_wick > 2×body AND upper_wick < body` |
| **`shooting_star`** | Long upper wick, small body near bottom. Bearish single-bar reversal. | `upper_wick > 2×body AND lower_wick < body` |
| **`pin_bar`** | One wick is more than two-thirds of the bar's total range. | `max(upper_wick, lower_wick) > 0.66 × range` |
| **`bullish_engulfing`** | Yesterday bearish, today bullish, today's body completely engulfs yesterday's body. | `prev_close < prev_open AND today_close > today_open AND today_close > prev_open AND today_open < prev_close` |
| **`bearish_engulfing`** | Mirror — today bearish, engulfs yesterday's bullish body. | Mirror conditions |
| **`morning_star`** / **`evening_star`** | 3-bar Nison reversal patterns. Used in `strat_morning_star` (walked B639). | See B639 walk doc |
| **`three_white_soldiers`** / **`three_black_crows`** | 3 consecutive monotone-strict bullish/bearish bars. Used in B636-walked strategies. | See B636 walk doc |

### Pivot / support-resistance levels

`compute_pivots` at [technical.py:64-161](backtest/signals/technical.py#L64-L161) computes multiple pivot systems using **yesterday's** H/L/C/O (yesterday is point-in-time safe — known at today's open).

**Standard floor-trader pivots** — used by `pivot_*` strategies:
- `P` (pivot) = (yesterday's High + Low + Close) / 3
- `R1` = 2P − Low ; `R2` = P + Range ; `R3` = High + 2(P − Low) — three rising resistance levels
- `S1` = 2P − High ; `S2` = P − Range ; `S3` = Low − 2(High − P) — three falling support levels
- `near_X` flags = True when `|today − level| / |level| < 0.003` (0.3% proximity)
- `above_R1`, `below_S1` etc = directional cross flags

**Central Pivot Range (CPR)** — used by `cpr_narrow_bullish`:
- `cpr_top` = (High + Low) / 2
- `cpr_bottom` = P (the floor pivot)
- `cpr_narrow` = True when CPR width < 15% of yesterday's range. Narrow CPR predicts a "directional day" per CPR theory (no consensus academic literature; popular among India retail traders).

**Camarilla pivots** — used by `camarilla_s3_bounce` / `camarilla_r3_breakout`:
- Computed from prev Close ± Range × 1.1 / {12, 6, 4, 2} → 4 resistances (R1-R4) and 4 supports (S1-S4).
- Original system credited to Slim Khan / Nick Scott. S3/R3 are the "primary" trading levels.

**Why all three pivot systems?** Each was independently developed and embedded in different communities. The cube (Stage 5) will empirically decide which produces better strategies — pre-cube we keep all three live.

### How market regimes are classified — the full picture

Every trading day, before any strategy is evaluated, the engine asks: **"what kind of market are we in today?"** The answer is one of five states: `bull`, `neutral`, `bear`, `crisis`, or `unknown`. This is the **regime classification**.

The classifier lives in [`backtest/engine/regime_filter.py:classify_regime`](backtest/engine/regime_filter.py#L151). Position sizing, regime-affinity gates, and short-to-long conversion logic all read from its output. Get this wrong and every downstream decision is built on a bad foundation — which is why this section is long.

#### Inputs to the classifier

The classifier takes **two required inputs** + **one optional override**:

| Input | Type | What it is | Source |
|---|---|---|---|
| `vix_value` | float (or None) | The CBOE VIX index ("fear index") — implied 30-day SPX volatility from option prices. ~12 = calm, ~20 = mildly elevated, ~30 = stressed, ~40+ = panic. | Pulled from cached OHLCV under `^VIX`; see `backtest/data/macro.py` |
| `spy_above_200ema` | bool (or None) | True if today's SPY close > SPY's 200-period EMA. The 200-EMA is a classic long-term trend definition (commonly attributed to Stan Weinstein 1988 *Secrets for Profiting in Bull and Bear Markets*). | Computed at [`get_spy_ema200`](backtest/engine/regime_filter.py#L271) |
| `bear_composite_score` | int 0-3 (default 0) | Optional 3-indicator override added Batch 292 to catch 2022-style "stealth bears" where VIX never hit 30 but the market was clearly in a bear. See "Bear composite override" below. | Computed at [`compute_bear_composite_score`](backtest/engine/regime_filter.py#L33) |

#### The threshold ladder (the actual classification rule)

The classifier checks conditions in this order and returns the FIRST match:

```python
if vix_value is None:                                return "unknown"   # fail-closed
if vix_value >= 40:                                  return "crisis"
if vix_value >= 30 and spy_above_200ema is False:    return "bear"      # canonical
if spy_above_200ema is False:                        return "bear"      # Batch 288 SPY-only gate
if bear_composite_score >= 2:                        return "bear"      # Batch 292 override
if vix_value < 20 and spy_above_200ema is True:      return "bull"
return "neutral"                                                        # everything else
```

In plain English, going from most-severe to least-severe:

1. **`unknown`** — VIX data is missing (cache miss, data feed failure). Fail-closed: block ALL new entries, both long and short. Existing positions continue under their original stops. Added in BUG-225 / DEC-316 (Pass 51) to fix a silent default-to-`neutral` that let the system trade on missing data.
2. **`crisis`** — VIX ≥ 40. Doesn't matter where SPY is; VIX above 40 is panic by itself (Mar 2020, Oct 2008, Aug 2024 etc).
3. **`bear` (canonical)** — VIX ≥ 30 AND SPY < 200-EMA. Both gauges agreeing: high implied vol AND price below the long-term trend line.
4. **`bear` (Batch 288 SPY-only gate)** — SPY < 200-EMA regardless of VIX. Added because all of 2022 had SPY decisively below 200-EMA while VIX rarely cleared 30 (the canonical bear gate), so the entire year mis-classified as `neutral`. The post-mortem ([config rationale](backtest/engine/regime_filter.py#L170-L175)) tied the misclassification to -275pp aggregate loss; the SPY-only override fixes the failure mode.
5. **`bear` (Batch 292 composite override)** — bear_composite_score ≥ 2 (see next subsection). Forces bear even if SPY is above 200-EMA, to catch mid-bear rallies (Aug 2022) where SPY temporarily crossed back above 200-EMA but the broader bear thesis held.
6. **`bull`** — VIX < 20 AND SPY > 200-EMA. Both gauges agree: low implied vol AND uptrend in force.
7. **`neutral`** — anything else (VIX 20-30 with SPY above 200-EMA; or VIX < 20 with no SPY data; or any other mixed condition). Default "I don't know which side is favoured" state.

#### Bear composite override (Batch 292) — 3 indicators, ≥2 fire = force bear

Added because the VIX-only and SPY-only gates both missed 2022's grinding bear. The composite reads three OFFICIAL data sources and asks: "are at least 2 of 3 saying bear?"

| # | Indicator | Threshold to fire | Data source | Academic reference |
|---|---|---|---|---|
| 1 | **Yield curve inversion** | `T10Y2Y < 0` (10-year Treasury yield below 2-year) | `data_prefetch/fred/observations/T10Y2Y.parquet` | Estrella-Hardouvelis 1991 *Journal of Finance* — canonical recession signal; has predicted every US recession since 1955 with no false positives |
| 2 | **AAII bearish sentiment extreme** | `bearish ≥ 40%` (% of surveyed retail investors who are bearish on the next 6 months) | `data_prefetch/aaii/weekly_sentiment.parquet` | American Association of Individual Investors weekly sentiment survey since 1987 |
| 3 | **Sector breadth deterioration** | ≥5 of 8 sector ETFs (XLK, XLF, XLE, XLV, XLI, XLU, XLP, XLY) below their 200-EMA, requires ≥5 ETFs to have ≥200 bars of history to be eligible | Polygon cache | Broad-market deterioration; standard market-breadth indicator |

If any of the 3 inputs is missing (e.g. early in backtest history before AAII data starts), that indicator contributes 0 — it can't false-trigger. The score is the count of indicators firing (0-3). Threshold to override the SPY-only gate is `score ≥ 2`.

The composite is computed once per day in `backtest/engine/regime_filter.py:compute_bear_composite_score` and passed into `classify_regime` as the `bear_composite_score` keyword argument.

#### Hysteresis — preventing single-day regime flips

The bare threshold ladder has a problem: if VIX prints 39.9 → 40.1 → 39.5 over three days, you'd flip neutral → crisis → neutral and disrupt all your sizing. Hysteresis solves this by widening the threshold in the direction of the previous regime, so to *change* regimes you need a decisive move, not a noise crossing.

[`classify_regime_with_hysteresis`](backtest/engine/regime_filter.py#L631) (DEC-317 + DEC-388 Pass 53) applies a default 5-point VIX buffer:

| Previous regime | Stays in regime if | Exits regime when |
|---|---|---|
| `crisis` | VIX ≥ 35 (i.e. 40 − buffer) | VIX < 35 |
| `bear` | VIX ≥ 25 (i.e. 30 − buffer) AND SPY < 200-EMA, OR SPY < 200-EMA alone | both conditions fail |
| `bull` | VIX < 25 (i.e. 20 + buffer) AND SPY > 200-EMA | either fails |

A second smoothing also runs alongside: the VIX value fed to the classifier can be a 5-day SMA of raw VIX (`get_vix_smoothed`, DEC-388, default window=5), so single-day spikes are damped before hysteresis even applies.

Hysteresis is opt-in via the `use_hysteresis` flag on [`get_regime_context`](backtest/engine/regime_filter.py#L206). The engine wires it on in production paths; one-shot helper calls (analytics, dashboards) can choose raw threshold behavior.

#### What the regime DOES once classified — REGIME_FILTER

Once the regime is known, downstream logic reads `REGIME_FILTER` ([`config.py:383`](backtest/config.py#L383)) to decide what happens:

| Regime | Long size | Short size | Conversion allowed? | Notes |
|---|---|---|---|---|
| `bull` | `full` (1.00×) | `reduced` (0.50×) | ✅ yes | Favour longs; allow short-to-long conversion |
| `neutral` | `full` (1.00×) | `full` (1.00×) | ❌ no | Both directions at normal size |
| `bear` | `reduced` (0.50×) | `full` (1.00×) | ❌ no | Favour shorts; longs sized down |
| `crisis` | `reduced` (0.50×) | `cautious` (0.25×) | ❌ no | Smaller positions both sides; **do NOT tighten stops** (causes whipsawing) |
| `unknown` | `none` (0.00×) | `none` (0.00×) | ❌ no | Block all new entries; existing positions continue |

`POSITION_SIZE_MULT` at [`config.py:412`](backtest/config.py#L412) defines those multipliers (1.0 / 0.5 / 0.25 / 0.0). They compose on top of confidence-tier sizing (EXCEPTIONAL/VERY HIGH/HIGH/MEDIUM-HIGH/MEDIUM/LOW from CLAUDE.md), so a `MEDIUM-HIGH` (1.5%) long in `bear` regime would size to 0.75% (1.5 × 0.5).

#### Worked example — September 2008

Suppose VIX prints 31.4 and SPY is 5% below its 200-EMA on 2008-09-15 (Lehman collapse). Walk through:

1. `vix_value = 31.4`. Not None → skip `unknown`.
2. `31.4 >= 40`? No → skip `crisis`.
3. `31.4 >= 30 AND spy_above_200ema is False`? **Yes** → return `"bear"`.

What if the same week VIX climbed to 41.2? Same SPY state.
1. `vix_value = 41.2`. Not None → skip `unknown`.
2. `41.2 >= 40`? **Yes** → return `"crisis"`.

What if SPY recovered above 200-EMA after a relief rally but yield curve was inverted, AAII bearish at 50%, and 6 of 8 sectors below 200-EMA?
1. `vix_value = 28.5`. Not None.
2. `28.5 >= 40`? No.
3. `28.5 >= 30 AND below 200-EMA`? No (SPY above now).
4. `spy_above_200ema is False`? No.
5. `bear_composite_score >= 2`? **Yes** (3 indicators firing = score 3) → return `"bear"`.

This third case is the 2022 stealth bear that Batch 292 was designed to catch.

#### Why this matters for the walks below

When you see a strategy's STRATEGY_REGIME_AFFINITY entry like `{"bear"}`, it means: "this strategy is *only allowed to fire* on days when `classify_regime(...)` returned `bear`." It doesn't fire on days when the regime is bull, neutral, crisis, or unknown.

This is **multiplicative** with the strategy's own gates. A LONG strategy could have all its internal signals fire (RSI low, pattern formed, OBV bullish) but still be blocked if today's regime isn't in the strategy's allowed set. That's the layer the **B271 family-bug** (next subsection) operates at — a regime-affinity entry that was correct for a single-direction strategy becomes wrong when the strategy is later converted to dual.

---

### Regime affinity — `STRATEGY_REGIME_AFFINITY`

The dict `STRATEGY_REGIME_AFFINITY` in [`regime_selector.py`](backtest/engine/regime_selector.py) maps strategy name → set of regimes the strategy is *allowed* to fire in. (For how those regimes themselves are classified, see the section just above.)

- If a strategy has an explicit entry, it fires only in those regimes.
- If a strategy has NO explicit entry, it falls back to **Batch 291 direction-aware default**: LONG strategies fire in `{bull, neutral}`; SHORT strategies fire in `{bear, crisis, neutral}`.

Many existing entries date back to "Batch 271" — a mass-edit that was done when most strategies were single-direction. Several strategies that have since been converted to dual now carry the original single-direction entry, which silently mis-regimes one side. We track these as the **B271 family-bug pattern** and have been fixing them one-by-one during walks.

### EVENT vs STATE temporality

Per `feedback_signal_temporality_event_vs_state` — a critical concept for understanding which gate carries timing alpha.

- **EVENT** signal = something just happened on the bar of fire (today). Examples: `morning_star` (pattern formed today), `above_r1` (price crossed R1 today), `vol_spike_2x` (today's volume is high), `macd_12_26_9_bullish_cross` (crossover happened today).
- **STATE** signal = a slow-moving regime/context that's been true for a while. Examples: `ema_50_200_bullish` (could have been true for months), `obv_bullish` (cumulative measure), `adx_trending` (multi-bar trend).

Strategies should attribute timing alpha to EVENT signals, not STATE signals. A docstring that says "X confirms the timing of Y" where Y is STATE is overclaiming.

---

## The 7-step walk methodology

Per CHECKLIST #105 (codified after B603 producer-shallow walk error). Every walk has these 7 steps.

| Step | What it does | What you'll see |
|---|---|---|
| **1** | **Read strategy code** | Direct copy of the function + gate-by-gate table with thresholds explained |
| **2** | **Classify** | Category, dual/single, status, last touched, regime affinity entry status |
| **3** | **Producer source-read + temporality** | Read the upstream functions that emit every gate signal; classify each as EVENT / STATE |
| **4** | **Doc-vs-thesis** | Does the docstring match what the gates actually do? Common failure: reversal pattern + trend-confirmation gate = continuation thesis with reversal docstring (the "B637 contradiction") |
| **5** | **OPEN_INVESTIGATIONS grep** | Any unresolved investigation tickets on this strategy? |
| **6** | **Missing-inverse + economic-symmetry** | Is the SHORT mirror present? Is it economically symmetric (or is one side advantaged by drift / data asymmetry)? |
| **7** | **Findings table + options + recommendation** | F1/F2/F3 findings, A/B/C action options, my pick |

---

## Cross-strategy summary table

> Quick scan. Read full walks below for evidence + recommendation rationale.

| # | Strategy | Cat | Dir | F1 (bug)? | F2 (doc)? | F3 (regime)? | Fire-count proj | My pick |
|---|---|---|---|---|---|---|---|---|
| W1 | `bullish_engulfing_support` | candle | dual | **F1** — see walk: SHORT gate set uses S1 instead of R1 in commentary | **F2** — no docstring | — | LONG ~83, SHORT ~83 — PASS_CUBE | **(A)** add docstring + minor commentary fix |
| W2 | `shooting_star_short` | candle | SHORT | **F1** — `bb_20_20_touch_upper` redundant with `near_r1/r2`; either-or via OR is correct but adds little independent info | **F2** — no docstring | ✅ explicit B291 default | ~25/yr — **FAIL_FIRE_STARVED** (RSI>65 + at-resistance + shooting_star joint product too narrow) | **(D)** Stage 5 deferral or **(C)** loosen one gate |
| W3 | `pivot_s1_bounce` | pivot | dual | — | **F2** — no docstring | **F3** — explicit `{neutral, bear}` LONG-only entry; SHORT now mis-regimed | LONG ~92, SHORT ~92 — PASS_CUBE | **(B)** F2 + F3 delete entry (B271 family-bug) |
| W4 | `pivot_s2_bounce` | pivot | dual | — | **F2** — no docstring | **F3** — same B271 family-bug pattern | LONG ~28, SHORT ~28 — borderline FAIL | **(B)** F2 + F3 delete entry; flag for B603 |
| W5 | `pivot_s3_capitulation` | pivot | LONG | — | **F2** — no docstring | — (no affinity entry; uses B291 default) | ~14/yr — **FAIL_FIRE_STARVED** | **(D)** Stage 5 deferral. **F6 missing-inverse:** consider Class 7 NEW `strat_pivot_r3_blowoff_short` |
| W6 | `pivot_r1_breakout` | pivot | dual | **F1 LATENT** — both LONG default-True (`above_avwap_*, True`) and SHORT default-False on the AVWAP gate — asymmetric default policy | ✅ docstring present | — | LONG ~5, SHORT ~5 — **FAIL_FIRE_STARVED**; 5 AND-gates | **(C)** loosen AVWAP-only-one-anchor + flag B603 |
| W7 | `pivot_r2_continuation` | pivot | dual | **F1 LATENT** — same AVWAP asymmetric default as W6 | ✅ docstring present | — | LONG ~2, SHORT ~2 — **FAIL_FIRE_STARVED**; 5 AND-gates incl vol_spike_2x | **(D)** Stage 5 deferral or **(C)** loosen |
| W8 | `cpr_narrow_bullish` | pivot | dual | **F1** — SHORT side uses `not s.get("above_avwap_50low", False)` which is silent-gap pattern (auto-True when key missing). B639 codified positive symmetric pattern. | ✅ docstring present | — (no entry; B291 default applies) | LONG ~13, SHORT ~13 — **FAIL_FIRE_STARVED**; 5 AND-gates incl 200-EMA | **(B)** F1 swap to positive symmetric `below_avwap_50low` |
| W9 | `camarilla_s3_bounce` | pivot | dual | — | ✅ docstring present | **F3 DEFERRED-R5** — B624 manifest M1 (already documented; no action) | LONG ~30, SHORT ~30 — borderline PASS | **(E)** no action needed; defer per existing R5 ticket |
| W10 | `camarilla_r3_breakout` | pivot | dual | — | **F2** — no docstring | — | LONG ~166, SHORT ~166 — PASS_CUBE | **(A)** F2 doc only |

**Aggregate findings:**
- 6 of 10 have no docstring (F2 across W1/W2/W3/W4/W5/W10)
- 1 B271 family-bug pattern (W3, W4 — single dict entry)
- 1 explicit silent-gap F1 (W8)
- 2 latent AVWAP asymmetric-default F1s (W6, W7)
- 5 fire-count FAIL_FIRE_STARVED projections (W2, W5, W6, W7, W8) — flag for B603 pre-cube discussion
- 1 missing-inverse candidate (W5 — `pivot_r3_blowoff_short` Class 7 NEW)
- 1 already-deferred (W9 — no walk-time action)

---

## W1. `strat_bullish_engulfing_support`

### Step 1 — Read the code

[screener.py:1373-1382](backtest/signals/screener.py#L1373-L1382):

```python
def strat_bullish_engulfing_support(s):
    # B628 F1 family-sweep: positive symmetric obv_bearish.
    fl = (s.get("bullish_engulfing") and (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and s.get("obv_bullish"))
    fs = (s.get("bearish_engulfing") and (s.get("near_r1") or s.get("near_r2") or s.get("at_key_fib"))
          and s.get("obv_bearish"))
    return _strat3(fl, fs, "candle",
        ["bullish_engulfing","at_support","obv_bullish"],
        ["bearish_engulfing","at_resistance","obv_bearish"],
        ["Bullish engulfing at support - two systems confirming","OBV rising"],
        ["Bearish engulfing at resistance - two systems confirming","OBV falling (B628 F1)"])
```

**LONG fires when ALL THREE are true:**

| Gate | Code | Meaning | Threshold |
|---|---|---|---|
| L-G1 Pattern | `bullish_engulfing` | Two-bar bullish engulfing pattern formed today (yesterday bearish, today bullish, today engulfs yesterday) | Boolean |
| L-G2 Location | `near_s1` OR `near_s2` OR `at_key_fib` | Price is within 0.3% of either pivot S1 / pivot S2 / a key Fibonacci retracement level (38.2% / 50% / 61.8%) | OR composite |
| L-G3 Flow | `obv_bullish` | OBV > its 20-bar mean (accumulation) | Boolean |

**SHORT fires when ALL THREE are true (mirror):** bearish_engulfing + (near_r1 OR near_r2 OR at_key_fib) + obv_bearish.

### Step 2 — Classify

- Category: `candle`
- Dual via `_strat3`
- Status: Active (1 of 221)
- STRATEGY_REGIME_AFFINITY: **no entry** → uses B291 direction-aware default
- Last touched: B628 (F1 family-sweep added positive symmetric `obv_bearish`)

### Step 3 — Producer source-read + temporality

- `bullish_engulfing` / `bearish_engulfing` at [technical.py:1448-1451](backtest/signals/technical.py#L1448-L1451) — strict 4-condition AND on bar of fire. **EVENT** signal. Producer pair is symmetric.
- `near_s1` / `near_s2` / `near_r1` / `near_r2` at [technical.py:120-121](backtest/signals/technical.py#L120-L121) — proximity test `|today − level| / |level| < 0.003`. Levels computed from YESTERDAY's H/L/C (PIT safe). **EVENT** signal.
- `at_key_fib` at [technical.py:186](backtest/signals/technical.py#L186) — OR of three Fibonacci proximity flags. **EVENT** signal.
- `obv_bullish` / `obv_bearish` — **STATE** (OBV is cumulative, 20-bar mean is slow).

### Step 4 — Doc-vs-thesis

Context bullets: "Bullish engulfing at support - two systems confirming / OBV rising." ✅ accurately describes what fires. Engulfing = EVENT, support = EVENT (proximity), OBV = STATE (confluence flow filter). Honest framing.

**No F1 thesis mismatch.** But: context bullets call it "two systems" (engulfing + support); OBV is actually a third gate, not a confluence. Minor commentary fix would help.

### Step 5 — OPEN_INVESTIGATIONS grep

No matches. Clean.

### Step 6 — Missing-inverse + economic-symmetry

- Structural symmetry: ✅ both directions implemented; gates mirror cleanly.
- Producer symmetry: ✅ all signals have positive symmetric mirrors (B628 already fixed the OBV silent-gap).
- Economic symmetry: bullish engulfing at support is a classic Nison reversal pattern; bearish engulfing at resistance is the canonical mirror. ✅ symmetric in literature.
- Data-source symmetry: all technical, no asymmetric data hazard.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | Strategy is essentially correct. Context bullet "two systems confirming" understates the gate count (3 gates: engulfing + location + OBV). | LOW (commentary) |
| **F2** | No docstring at all (just inline `# B628 F1 family-sweep` comment + context bullets). | LOW |

**Fire-count projection** (gates: bullish_engulfing × (near_s1 OR near_s2 OR at_key_fib) × obv_bullish): ~83/yr LONG side. PASS_CUBE.

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring + minor commentary fix to "three systems confirming" (engulfing + support/fib + OBV-flow). **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).** Clean strategy; just needs honest docstring.

### FINAL STATUS POST-B645 — ✅ CLOSED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | Option (A) — F2 docstring added; context bullet upgraded "two systems" → "three systems confirming (candle + level + flow)" to match actual gate count |
| **Code reference** | [screener.py strat_bullish_engulfing_support](backtest/signals/screener.py) |
| **Measured fires/yr (universe)** | **337** PASS_CUBE (B641 measurement; independence under-counted 1000×) |
| **Open items queued from this walk** | `S4-OBV-LOCATION-TENSION-DESIGN` (LONG OBV gate fights support premise — reviewer P6) ; `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` (at_key_fib swing-anchor verification — reviewer P7) |
| **No regrets** | The gate set is honestly named; the OBV-vs-location concern is a design question (could re-frame to `obv_diverge_bull`) deferred to the queued ticket. |

---

## W2. `strat_shooting_star_short`

### Step 1 — Read the code

[screener.py:1484-1493](backtest/signals/screener.py#L1484-L1493):

```python
def strat_shooting_star_short(s):
    fires = (s.get("shooting_star") and
             (s.get("near_r1") or s.get("near_r2") or
              s.get("bb_20_20_touch_upper")) and
             s.get("rsi_14", 50) > 65)
    return _strat(fires, "short", "candle",
        ["shooting_star","at_resistance","rsi_14>65"],
        ["Shooting star at resistance level  -  bearish reversal",
         "Long upper wick shows sellers rejecting higher prices",
         f"RSI-14 at {s.get('rsi_14',0):.1f}  -  overbought at resistance"])
```

**SHORT fires when ALL THREE are true:**

| Gate | Code | Meaning | Threshold |
|---|---|---|---|
| S-G1 Pattern | `shooting_star` | Long upper wick (>2×body), small lower wick (<body), small body | Boolean |
| S-G2 Location | `near_r1` OR `near_r2` OR `bb_20_20_touch_upper` | Within 0.3% of pivot R1, R2, OR within 0.5% of upper Bollinger Band | OR composite |
| S-G3 Momentum | `rsi_14 > 65` | RSI > 65 (overbought; not yet at canonical 70 but close) | Literal |

### Step 2 — Classify

- Category: `candle`
- Single-direction SHORT (no LONG mirror exists — there's no `strat_hammer_at_support_long`)
- Status: Active
- STRATEGY_REGIME_AFFINITY: explicit `{"bear", "crisis", "neutral"}` at [regime_selector.py:315](backtest/engine/regime_selector.py#L315) — matches B291 SHORT default ✅
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

- `shooting_star` at [technical.py:1439](backtest/signals/technical.py#L1439) — `upper_wick > 2×body AND lower_wick < body AND body > 0`. **EVENT** signal.
- `near_r1` / `near_r2` — EVENT (proximity, see W1)
- `bb_20_20_touch_upper` at [technical.py:975](backtest/signals/technical.py#L975) — `close >= upper_BB × 0.995`. **STATE-like** (BB is slow-moving 20-period rolling).
- `rsi_14` — STATE.

### Step 4 — Doc-vs-thesis

Context bullets: "Shooting star at resistance / Long upper wick shows sellers rejecting higher prices / RSI-14 at X overbought at resistance." ✅ accurate description.

**Per CHECKLIST (l) AVWAP/OBV/MACD non-redundancy:** the location OR-composite mixes pivot-R levels (mean-reversion daily-bar) with Bollinger upper (volatility-based 20-period). Different references; not redundant. ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

**No LONG mirror exists.** The symmetric inverse would be `strat_hammer_at_support_long` (hammer + near_s1/s2 + RSI<35). Producer pair is symmetric (hammer / shooting_star both EVENT in `compute_candle_signals`). Bollinger lower would mirror upper. **F-missing-inverse candidate** — Class 7 NEW per `feedback_long_short_inverse_audit`.

Economic symmetry: hammer-at-support is canonical bullish reversal in Nison; mirror would be valid. Caveat: `strat_pivot_s2_bounce` already includes `hammer + near_s2 + rsi<40` on its LONG side ([screener.py:190](backtest/signals/screener.py#L190)). Adding `strat_hammer_at_support_long` would partially duplicate. NOT a clean Class 7 NEW — the LONG-side coverage is partially there already.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | None | — |
| **F2** | No docstring; thresholds (RSI>65, BB touch ratio 0.995) not explained. | LOW |
| **F-fire-count** | gates: shooting_star prior ~0.02 × (near_r1 OR near_r2 OR bb_touch_upper) ~0.30 × rsi>65 ~0.20 ≈ 0.0012 → ~66/yr universe-wide, but with conditional decay (RSI>65 AND shooting_star are positively correlated at tops, so joint may be higher than independent product). Conservative: ~25-66/yr. Borderline. | MEDIUM |
| **F-missing-inverse** | LONG mirror partially covered by `pivot_s2_bounce`. NOT a clean Class 7 NEW candidate. | LOW |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring only (status quo gates) |
| (B) F2 + loosen RSI>65 to RSI>60 (matches `pivot_s2_bounce` SHORT side's RSI>60); higher fire count |
| (C) Add Class 7 NEW `strat_hammer_at_support_long` — but partial duplication with `pivot_s2_bounce` LONG |
| **(D)** Stage 5 deferral — defer fire-count decision to cube; F2 doc only now |
| (E) Status quo |

**My recommendation: (D)** — F2 doc now, defer fire-count tweak to Stage 5 cube data. Hold (C) on missing-inverse; the partial duplication needs owner judgment.

### FINAL STATUS POST-B645 — ✅ CLOSED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | Option (D) — F2 docstring added with Nison 1991 source + threshold rationale + B641 Stage-5 deferral notice (no pre-cube loosening of RSI>65 per `feedback_minimum_fire_count_gate_before_cube` + CHECKLIST (k)) |
| **Measured fires/yr (universe)** | **139** PASS_CUBE — B640 FAIL projection was independence-product artifact (gates were over-estimated as exclusive but RSI>65 + shooting_star + at-resistance are POSITIVELY correlated at market tops; independence ratio 2.092 over-counted by 2×, but the measured 139/yr is well above 30 even allowing for that over-count) |
| **Reviewer's structural concerns (P-class on W2)** | Reviewer flagged `bb_20_20_touch_upper` as a continuation signal mis-categorized as resistance (price walks the upper BB in uptrends → shorting strength fights drift) — acknowledged as a future design question; NOT auto-fixed this batch (would require a separate strategy redesign). Reviewer's loosen-RSI option (B640-B) explicitly NOT taken — loosening RSI<65 would worsen the strategy by shorting less-overbought names. |
| **No regrets** | F2 doc shipped; pre-cube loosening avoided. The bb_touch_upper concern is real but warrants its own redesign batch, not a quick loosen. |

---

## W3. `strat_pivot_s1_bounce`

### Step 1 — Read the code

[screener.py:175-186](backtest/signals/screener.py#L175-L186):

```python
def strat_pivot_s1_bounce(s):
    # B628 F1 family-sweep: `not s.get("obv_bullish")` -> positive
    # symmetric `obv_bearish` (B617 producer). See B628 commit for
    # the bundled 7-strategy sweep rationale per CHECKLIST #105 (n).
    fl = (s.get("near_s1") and (s.get("hammer") or s.get("pin_bar")) and s.get("obv_bullish"))
    fs = (s.get("near_r1") and (s.get("shooting_star") or s.get("bearish_engulfing"))
          and s.get("obv_bearish"))
    return _strat3(fl, fs, "pivot",
        ["near_s1","hammer/pin_bar","obv_bullish"],
        ["near_r1","shooting_star","obv_bearish"],
        ["Price at S1 pivot support","Hammer or pin bar confirming buyers","OBV rising - accumulation"],
        ["Price at R1 pivot resistance","Shooting star or bearish engulfing rejecting highs","OBV falling - distribution (B628 F1)"])
```

**LONG fires when ALL THREE are true:**

| Gate | Code | Meaning | Threshold |
|---|---|---|---|
| L-G1 Location | `near_s1` | Price within 0.3% of pivot S1 | Literal |
| L-G2 Pattern | `hammer` OR `pin_bar` | Today is a hammer or a pin bar | OR composite |
| L-G3 Flow | `obv_bullish` | OBV accumulation | STATE |

**SHORT mirror:** `near_r1 + (shooting_star OR bearish_engulfing) + obv_bearish`.

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear"}` at [regime_selector.py:192](backtest/engine/regime_selector.py#L192). The dict comment classifies this as "counter-trend bounce" — but this is dual, so the affinity caps **BOTH** directions to neutral/bear. That over-restricts LONG (should fire in bull regimes too for counter-trend bounces in uptrends) and arguably gives SHORT wrong regimes (SHORT-on-bounce-rejection should be bear/crisis/neutral; bull excluded correctly, but explicit set excludes crisis incorrectly).
- Last touched: B628 F1 family-sweep

### Step 3 — Producer source-read + temporality

- `near_s1` / `near_r1` — EVENT (proximity)
- `hammer` / `pin_bar` / `shooting_star` / `bearish_engulfing` — EVENT (today's bar shape)
- `obv_bullish` / `obv_bearish` — STATE

### Step 4 — Doc-vs-thesis

Context bullets accurate. Bounce thesis: price at support + reversal candle + OBV-flow confirmation. ✅ honest.

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅. Economic ✅. Producer symmetry ✅ post-B628.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — strategy logic is clean | — |
| **F2** | No docstring | LOW |
| **F3** | STRATEGY_REGIME_AFFINITY `{neutral, bear}` was set when strategy was single-direction (LONG = counter-trend bounce in pullback regimes). Strategy is NOW dual via `_strat3`; both directions are gated to {neutral, bear}. SHORT side mis-regimed (should be `{bear, crisis, neutral}` per B291 default). LONG side mis-regimed (should be `{bull, neutral}` for buy-the-dip-in-uptrend interpretation OR `{neutral, bear}` for capitulation-bounce interpretation — split-thesis the owner should rule on). **Same B271 family-bug signature as B608/B609/B617 and B639 morning_star.** | HIGH (regime) |

**Fire-count projection:** ~92/yr LONG side. PASS_CUBE.

**Options:**

| Option | Description |
|---|---|
| (A) F2 doc only |
| **(B)** F2 + F3 delete `{neutral, bear}` entry — falls back to B291 direction-aware default. SAME PATTERN as B608/B609/B617/B639. **RECOMMENDED.** |
| (C) F2 + F3 split affinity into per-direction explicit entries (`pivot_s1_bounce` LONG `{bull,neutral}`, `pivot_s1_bounce_short` would need to be a separate registry key — not how the engine works currently) |
| (D) Status quo |

**My recommendation: (B).** Same family-bug fix as the four prior walks. Risk: if cube data shows LONG genuinely better in `{neutral, bear}` only, can re-add post-R5 (manifest M1 absorbs).

### FINAL STATUS POST-B645 — ✅ CLOSED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | Option (B) + **reviewer-flagged P1 pin_bar direction-fix.** Three actions in same commit: (1) F2 docstring; (2) F3 STRATEGY_REGIME_AFFINITY `{neutral, bear}` entry DELETED — 5th instance of B271 family-bug fix (post B608/B609/B617/B639); falls back to B291 direction-aware default. (3) **F1 pin_bar direction-contamination fix** — reviewer caught that `pin_bar` producer is direction-agnostic (`max(uwk, lwk) > 0.66*rng` fires on either dominant wick). Added producer-additive `bullish_pin_bar` (lower wick > 0.66 range) + `bearish_pin_bar` (upper wick > 0.66 range) to `compute_candle_signals`; LONG side swapped `pin_bar` → `bullish_pin_bar`. SHORT side unchanged (already used directionally-clean `shooting_star` + `bearish_engulfing`). |
| **Code reference** | [screener.py strat_pivot_s1_bounce](backtest/signals/screener.py) + [technical.py:1440 bullish/bearish_pin_bar producers](backtest/signals/technical.py#L1440) |
| **Test pins** | test_batch641_tier1_walk_bundle_followups pins 1-7 (producer existence, direction-correctness, bearish-pin-blocks-LONG regression, regime entry deleted, B291 default) |
| **Measured fires/yr (universe)** | **220** PASS_CUBE (independence under-counted 500×) |
| **No regrets** | All three actions are unambiguous Tier 1 fixes. The pin_bar fix is structurally important — a bearish pin AT SUPPORT firing LONG was a real bug. |

---

## W4. `strat_pivot_s2_bounce`

### Step 1 — Read the code

[screener.py:189-195](backtest/signals/screener.py#L189-L195):

```python
def strat_pivot_s2_bounce(s):
    fl = (s.get("near_s2") and s.get("rsi_14", 50) < 40 and (s.get("hammer") or s.get("bullish_engulfing")))
    fs = (s.get("near_r2") and s.get("rsi_14", 50) > 60 and s.get("bearish_engulfing"))
    return _strat3(fl, fs, "pivot",
        ["near_s2","rsi_14<40","bullish_candle"], ["near_r2","rsi_14>60","bearish_engulfing"],
        [f"Price at S2 deep support","RSI-14 oversold","Bullish candle confirms buyers"],
        [f"Price at R2 strong resistance","RSI-14 overbought","Bearish engulfing confirms sellers"])
```

**LONG fires when ALL THREE:**

| Gate | Code | Meaning |
|---|---|---|
| L-G1 Location | `near_s2` | Within 0.3% of pivot S2 (deeper support than S1) |
| L-G2 Momentum | `rsi_14 < 40` | Oversold (below 40, not deeply at 30) |
| L-G3 Pattern | `hammer` OR `bullish_engulfing` | Bullish reversal candle |

**SHORT mirror:** `near_r2 + rsi_14 > 60 + bearish_engulfing`.

**Note** the SHORT side has only `bearish_engulfing`, not the OR composite the LONG side has (no `shooting_star` option). Asymmetric. Minor.

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear"}` — **same B271 family-bug as W3**
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

All gates already covered in W1/W3.

### Step 4 — Doc-vs-thesis

Context bullets accurate. Deep support + oversold + confirmation candle. ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Asymmetric: LONG has `hammer OR bullish_engulfing`, SHORT has only `bearish_engulfing`. Should mirror to `shooting_star OR bearish_engulfing`. Minor producer-symmetry gap.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | SHORT side missing `shooting_star` OR-disjunct symmetric to LONG's `hammer`. Producer exists; one-line additive. | LOW |
| **F2** | No docstring | LOW |
| **F3** | Same B271 family-bug as W3. Dual strategy with single-direction-era affinity entry. | HIGH (regime) |
| **F-fire-count** | LONG ~28/yr (near_s2 narrower than near_s1 + rsi<40 + hammer/engulfing). SHORT ~28/yr. **Borderline FAIL_FIRE_STARVED** vs min_trades=30. | MEDIUM |

**Options:**

| Option | Description |
|---|---|
| (A) F2 doc only |
| (B) F2 + F3 delete entry + F1 add `shooting_star` to SHORT OR |
| **(C)** F2 + F3 delete entry + F1 add `shooting_star` + flag for B603 fire-count discussion. **RECOMMENDED.** |
| (D) Status quo |

**My recommendation: (C).**

### FINAL STATUS POST-B645 — ✅ SHIPPED PARTIAL + 🎯 REMAINDER QUEUED

| Item | Outcome |
|---|---|
| **What shipped (B641)** | **F3 ONLY — split per CHECKLIST (g) sequence-or-split.** Reviewer's M4 critique caught that bundling F3 + F1 + RSI-mislabel violates the same (g) rule that justified deferring W7. Action: SPLIT the bundle — F3 regime entry delete ships in B641 Tier 1 (safe family-bug pattern); F1 add `shooting_star` to SHORT OR + F2 docstring + RSI-40-mislabel correction queued separately. |
| **Code reference** | [regime_selector.py — pivot_s2_bounce {neutral, bear} entry deleted](backtest/engine/regime_selector.py) (B271 family-bug fix #6) |
| **Test pins** | test_batch641_tier1_walk_bundle_followups pins 8-9 (regime entry deleted, B291 default applies) |
| **Measured fires/yr (universe)** | **PENDING B660 (per 2nd-wave-redux #3+#4 owner-approved B665 revert).** Multiple inconsistent measured values exist in the cycle history: (a) 22/yr per B641 smoke (20 first-tickers × ×11 scale, hardcoded-220-universe — DEPRECATED PER B648), (b) 73/yr per B648 random-30 × ×16.77 scale (used pre-B665 to claim FAIL→PASS reversal). **W4 fire-count reconciliation per critique #3:** the 22 → 73 movement was attributed to "independence OVER-counted 5.8×" but over-count corrections push estimates DOWN, not UP. The change is attributable to sampling-pipeline changes (sample composition 20-first→30-random + scale ×11→×16.77), NOT to gate-correlation physics. The independence-ratio narrative was reverse-engineered cover for a sampling artifact; retracted. W4 fire-count status is INDETERMINATE PENDING B660 full-universe representative-sample measurement. |
| **Open items queued** | `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` — three sub-changes in ordered ship sequence per CHECKLIST (g): (1) F1 add `shooting_star` to SHORT OR (one-line additive); (2) F2 docstring; (3) RSI<40 "oversold" mislabel correction (canonical Wilder oversold is 30, not 40 — relabel to "below-neutral" or "soft-oversold") |
| **Reviewer P2 specifically** | RSI<40 mislabel is queued for explicit correction; not auto-fixed because per `feedback_no_rushing_per_strategy_tweak` each ships in its own owner-direction turn |
| **No regrets** | Splitting was the right call per (g); future W4 batches can ship the remainder cleanly. |

---

## W5. `strat_pivot_s3_capitulation`

### Step 1 — Read the code

[screener.py:198-206](backtest/signals/screener.py#L198-L206):

```python
def strat_pivot_s3_capitulation(s):
    fires = (s.get("near_s3") and
             s.get("rsi_14", 50) < 30 and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "pivot",
        ["near_s3","rsi_14<30","vol_spike_2x"],
        ["Price at S3  -  extreme capitulation level",
         f"RSI-14 extremely oversold at {s.get('rsi_14',0):.1f}",
         "Volume spike confirms panic selling  -  reversal likely"])
```

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `near_s3` | Within 0.3% of pivot S3 (deepest standard support level) |
| `rsi_14 < 30` | Canonical oversold |
| `vol_spike_2x` | Volume ≥ 2× 20-day average |

### Step 2 — Classify

- Category: `pivot`
- Single-direction LONG
- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear", "crisis"}` at [regime_selector.py:189](backtest/engine/regime_selector.py#L189) — designed for buying capitulation in down/crisis regimes. ✅ correct for LONG capitulation thesis (no bull because there's no capitulation in bull).
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

All gates EVENT (today's bar metrics).

### Step 4 — Doc-vs-thesis

✅ "Extreme capitulation / extremely oversold / panic selling" — matches gate set.

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

**Missing inverse:** `strat_pivot_r3_blowoff_short` would mirror this: `near_r3 + rsi_14 > 70 + vol_spike_2x` — a blowoff-top short. Producer pair `near_r3` exists ([technical.py:121](backtest/signals/technical.py#L121)). **Class 7 NEW candidate per `feedback_long_short_inverse_audit`.**

Economic symmetry: capitulation lows + blowoff highs are classic mirror events in market structure (Wyckoff Selling Climax / Buying Climax). ✅

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| **F2** | No docstring | LOW |
| **F-missing-inverse** | `strat_pivot_r3_blowoff_short` Class 7 NEW candidate. Producer ready. ~10 lines per `feedback_wire_new_strategies_on_the_spot`. | MEDIUM |
| **F-fire-count** | gates: near_s3 ~0.005 × rsi<30 ~0.05 × vol_spike_2x ~0.10 ≈ 0.000025 → ~14/yr universe-wide. **FAIL_FIRE_STARVED** vs min_trades=30. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) F2 doc only |
| (B) F2 + add Class 7 NEW `strat_pivot_r3_blowoff_short` |
| (C) F2 + loosen one gate (e.g., rsi<35 instead of <30) to raise fire count |
| **(D)** F2 + add Class 7 NEW + Stage 5 fire-count deferral on both (don't loosen pre-cube; let R5 decide). **RECOMMENDED.** |
| (E) Status quo |

**My recommendation: (D).** Wire the missing inverse on-the-spot per memory directive; defer the fire-count loosening to cube data.

### FINAL STATUS POST-B645 — ✅ REDESIGNED (B643 option C) → 🟡 EXPLORATORY (B644) + ✅ MIRROR SHIPPED (B645)

| Item | Outcome |
|---|---|
| **Reviewer's structural critique (P3)** | The original B640 W5 was a knife-catch by construction (price crashed + oversold + panic volume = BUY; no element of the gate-set asked whether the decline had stopped). Reviewer was 100% right; this was the most-dangerous strategy in the bundle. Survivorship-bias-amplified (the falling knives that didn't bounce fall out of survivor universes). |
| **Initial owner direction (W5-D from B640)** | Wire Class 7 NEW mirror + Stage 5 defer (the initial B641 plan) — superseded by deeper redesign per reviewer P3 critique. |
| **Subsequent owner direction (option C from B643 review)** | **Redesign — decouple capitulation DETECTION from ENTRY.** New producer `compute_capitulation_lookback` (in `technical.py`) emits `recent_capitulation_at_s3` = True when the pre-B643 conditions (near_s3 + rsi<30 + vol_spike_2x) were satisfied on ANY of the last 5 bars. Strategy now fires LONG when BOTH: (1) recent_capitulation_at_s3 (the 5-bar Wyckoff Spring/Test eligibility window) AND (2) a reversal-trigger today (`bullish_engulfing` OR `hammer` OR `above_prev_high`). **Buys the TURN inside the window, not the FALL on capitulation day.** Wyckoff Selling Climax + Spring/Test play. |
| **Code reference** | [screener.py strat_pivot_s3_capitulation](backtest/signals/screener.py) + [technical.py compute_capitulation_lookback](backtest/signals/technical.py) |
| **Test pins** | test_batch643_w5_capitulation_redesign — 17 pins covering producer behavior (importable, empty on short history, True today + within window, False outside window, False on normal series), strategy fires on each of 3 reversal-trigger OR branches, blocks without reversal trigger, blocks without recent capitulation, regime affinity unchanged |
| **Measured fires/yr (universe)** | **Pre-B643: 14.7. Post-B643: 18.3 (+25%).** Verdict: still FAIL_FIRE_STARVED, but structurally correct. The redesign achieves its primary objective: closing the knife-catch. The fire-count went up modestly because the 5-bar eligibility window allows entries that would have been missed by same-bar-only firing. |
| **Subsequent owner direction (W5-i from B643 measurement review)** | **Keep as EXPLORATORY** — ship correctness fix; do NOT loosen gates pre-cube to chase 30/yr threshold. Pre-cube loosening recreates the original problem (looser gates → less-confirmed signals → more knife-catches). Stage 5 cube empirically validates whether 18/yr fires produce alpha at sufficient statistical power. Marked EXPLORATORY in docstring per B644. |
| **Subsequent owner direction (a from B644 review)** | **Wire Class 7 NEW mirror `strat_pivot_r3_blowoff_short` symmetrically (B645).** See dedicated W5-mirror section below. |
| **Open items** | `S4-SURVIVORSHIP-T1A-VERIFY` — reviewer's C5 cross-cutting critique applies to W5 specifically; verify T1a PIT universe includes delisted-during-window names (DEC-477 says 111 historical-removed rows; per-strategy adversarial verification still pending) |
| **Reviewer's M8 (economic-symmetry of W5 inverse)** | Acknowledged via EXPLORATORY marking on BOTH W5 LONG + W5 mirror SHORT. The wire happened because owner explicitly directed it post-redesign + with full awareness of the equity-drift / squeeze-risk / borrow-cost asymmetries (per `feedback_structural_symmetry_not_economic_symmetry`); Stage 5 cube governs final deployment decision. |
| **No regrets** | The redesign is one of the most consequential outcomes of the audit cycle. The reviewer was right about the structural problem; option C is the rigorous fix; W5-i exploratory marking is the disciplined disposition. |

---

## W5 mirror — `strat_pivot_r3_blowoff_short` (Class 7 NEW per B645)

> **Wired Batch 645 (2026-06-09)** per owner directive (a) following B643 W5 LONG redesign + B644 W5-i exploratory marking. Symmetric mirror of B643's 2-gate structure; same Wyckoff thesis on the SHORT side (Buying Climax + Upthrust-Test sequence).

### Design — mirror of W5 post-redesign

New producer in `technical.py`:

```python
def compute_blowoff_lookback(df, lookback=5):
    # Mirror of compute_capitulation_lookback.
    # Per-bar: near_r3 + rsi>70 + vol_spike_2x
    # Returns: recent_blowoff_at_r3 = True if any of last 5 bars satisfied.
```

Strategy in `screener.py`:

```python
def strat_pivot_r3_blowoff_short(s):
    fires = (
        s.get("recent_blowoff_at_r3")
        and (
            s.get("bearish_engulfing")
            or s.get("shooting_star")
            or s.get("below_prev_low")
        )
    )
    return _strat(fires, "short", "pivot", ...)
```

### Wyckoff thesis

The blowoff bar is the **Buying Climax (BC)** — terminal-stage upmove with climactic volume + price reaching beyond standard resistance. The 5-day window captures the **Automatic Reaction (AR)** + **Upthrust-Test** phase where price re-tests the BC high on weaker volume. Bearish-reversal-confirmation bar inside the window signals the Upthrust failed → bias to the **Sign-of-Weakness (SoW)** decline. **Sells the TURN inside the window, not the SPIKE on blowoff day.**

### Status — 🟡 EXPLORATORY + 🛑 DO-NOT-DEPLOY (B652) + ✅ B659 SYMMETRIC VOL GATE

| Item | Outcome |
|---|---|
| **Strategy count impact** | 221 → 222 (+1 Class 7 NEW) |
| **Regime affinity** | No explicit `STRATEGY_REGIME_AFFINITY` entry; B291 direction-aware SHORT default applies → fires in `{bear, crisis, neutral}` |
| **Test pins (B645 originals)** | `test_batch645_w5_mirror` — 16 pins covering producer (importable, empty on short history, True today + within window, False outside window, False on normal series), strategy fires on each of 3 bearish-reversal OR branches, blocks without blowoff or reversal-trigger, registry, B291 default, count = 222 |
| **Test pins (B659 update)** | `test_batch645_w5_mirror.py` fixtures updated in commit `db2dda419` to include `vol_below_avg: True` on the 3 reversal-trigger-fires tests + new isolation pin in `test_batch659_silent_gap_unify.py` proving SHORT does NOT fire on reversal-trigger without `vol_below_avg` (closes the dead-cat-bounce mirror hole) |
| **Measured fires/yr (universe) — B645 original** | **7.3** FAIL_FIRE_STARVED (per `output_audit/fire_count_measured_b645_w5_mirror.json` — 20 tickers × 3 years; 0.67/yr sample × 11 scale = 7.3 universe-projected). Pre-B648 scaling fix + pre-B659 vol gate. |
| **Measured fires/yr (universe) — B648 corrected, pre-B659** | **61.5 PASS_CUBE PRELIMINARY** (B648 random-30 × 16.77 scale; sample 3.67 × 16.77; independence ratio 0.117 under-counted 8.5×). Per `output_audit/fire_count_measured_b648_w5m_trend_random30.json`. |
| **Measured fires/yr (universe) — post-B659** | **Pending B660** — expected ~30-40% drop from 61.5 since `vol_below_avg` is a STATE filter that fires ~50% of bars across the sample but is structurally rare in genuine Wyckoff Distribution scenarios. Predicted post-B659: ~35-45/yr (still PASS_CUBE on the min_trades=30 threshold but moves the strategy out of "high-noise" territory). |
| **B652 DO-NOT-DEPLOY gate (added 2026-06-09 per 2C5)** | Strategy stays REGISTERED for dataflow / cube-replay coverage but **MUST NOT be promoted to live trade routing** until BOTH: (1) M10 cost-aware cube (slippage haircut + borrow cost lookup + gap-at-entry modelling) AND (2) S5-MULTIPLE-TESTING-CORRECTION (deflated Sharpe / Hansen SPA / Benjamini-Hochberg FDR) ship. The W5m fat right-tail (squeeze risk on overbought short-target names) is exactly the structural risk the current flat-bps slippage model cannot evaluate. |
| **B659 symmetric vol gate (added 2026-06-09 per S4-W5M-SYMMETRIC-VOL-GATE)** | Pre-B659 the SHORT side reversal-trigger lacked the volume condition that B650 added to W5 LONG. Wyckoff Buying Climax + Upthrust-Test sequence symmetrically requires LOWER volume on the failed-upthrust Test bar (supply-was-absorbed mirror of demand-was-absorbed Spring volume condition). Without the volume gate, `below_prev_low` during a sustained rally could fire on counter-rally pullbacks on heavy buy-volume — the SHORT mirror of W5's pre-B650 dead-cat-bounce hole. **Fix:** `s.get("vol_below_avg")` AND-required on the bar of fire. Strategy now properly distinguishes a Wyckoff Upthrust-Test (low-volume failed retest of BC high) from a continuation rally on heavy accumulation volume. |
| **Update to count table at top** | The W5m row in the [Cluster current state](#cluster-current-state) table now shows the **B659 + B652 status combined**: NEW → EXPLORATORY + DO-NOT-DEPLOY + structurally-symmetric vol gate. |
| **Expectancy asymmetry ACKNOWLEDGED** | Per `feedback_structural_symmetry_not_economic_symmetry` + reviewer's M8: structurally symmetric to W5 LONG but **economically NOT symmetric** — equity upward drift + squeeze risk on overbought short-target names + borrow costs structurally bias against SHORT. Owner-approved wire per directive (a) with full understanding that Stage 5 cube governs deployment. The DO-NOT-DEPLOY gate ensures this awareness is enforced architecturally rather than informally. |
| **Open items** | Same survivorship-bias caveats apply mirror-image (the squeezes that aren't in survivor universe; merger-arb floors on shorts of acquisition targets) — tracked under `S4-SURVIVORSHIP-T1A-VERIFY` cross-ref. |
| **2nd-wave-redux #7 reconciliation (B665)** | **The DO-NOT-DEPLOY gate has a hidden interaction with the C2 ticket it's gated on.** W5m stays REGISTERED "for dataflow / cube-replay coverage" but registered strategies count as hypotheses in any FDR / Hansen SPA / deflated-Sharpe calculation. So W5m being registered-but-DO-NOT-DEPLOY still consumes statistical budget — it raises the bar for every strategy you actually want to deploy in the C2 correction it's gated on. Self-referential circularity. New ticket: `S5-DO-NOT-DEPLOY-MULTIPLE-TESTING-RECONCILIATION` — when C2 lands, DO-NOT-DEPLOY strategies must be excluded from the multiple-testing universe OR de-registered before the correction is computed. Currently neither is enforced. Discipline gap acknowledged: the registered-for-coverage rationale has a real cost the doc didn't catch pre-critique. |

---

## W6. `strat_pivot_r1_breakout`

### Step 1 — Read the code

[screener.py:209-244](backtest/signals/screener.py#L209-L244):

```python
def strat_pivot_r1_breakout(s):
    """Pivot R1 breakout. Batch 205 ... AVWAP-from-252-day-low is the institutional
    reference level; breakouts above R1 that ALSO hold above AVWAP are markedly higher
    quality than R1 breaks in isolation.

    AVWAP gate defaults to True when avwap signals are absent (e.g.
    insufficient history) so backward-compat is preserved.
    """
    avwap_long_ok = s.get("above_avwap_252low", True) and s.get("above_avwap_50low", True)
    # B633 sweep: positive symmetric below_avwap_252low/50low (B612 producers)
    avwap_short_ok = s.get("below_avwap_252low", False) and s.get("below_avwap_50low", False)
    fl = (
        s.get("above_r1") and s.get("vol_spike_15x")
        and s.get("macd_12_26_9_bullish") and avwap_long_ok
    )
    fs = (
        s.get("below_s1") and s.get("vol_spike_15x")
        and s.get("macd_12_26_9_bearish") and avwap_short_ok
    )
    return _strat3(fl, fs, "pivot", ...)
```

**LONG fires when ALL FOUR (technically FIVE — `avwap_long_ok` is itself two-AND):**

| Gate | Meaning |
|---|---|
| `above_r1` | Today's close > R1 |
| `vol_spike_15x` | Volume ≥ 1.5× 20-day average |
| `macd_12_26_9_bullish` | MACD histogram > 0 (momentum) |
| `above_avwap_252low` AND `above_avwap_50low` | Above BOTH long-anchor and short-anchor AVWAP |

**SHORT mirror:** below_s1 + vol_spike_15x + macd_bearish + (below_avwap_252low AND below_avwap_50low).

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: no entry → B291 default
- Last touched: B633 (positive symmetric below_avwap swap)

### Step 3 — Producer source-read + temporality

- `above_r1` / `below_s1` — EVENT (cross today)
- `vol_spike_15x` — EVENT (today's volume)
- `macd_12_26_9_bullish` / `_bearish` — borderline EVENT (histogram crossover vs hist > 0 is a STATE measure of histogram sign; the strategy uses `_bullish` = "hist > 0" so STATE)
- `above_avwap_252low` / `_50low` — STATE-ish (AVWAP slow-moving once anchored)
- `below_avwap_252low` / `_50low` — STATE-ish (B612 producer; positive symmetric)

### Step 4 — Doc-vs-thesis

Docstring present and clear. Cites Brian Shannon 2022 (real source). ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅. Producer symmetry ✅ post-B633. Economic ✅.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1 LATENT** | AVWAP gate's default policy is asymmetric: LONG defaults to `True` if key missing (`s.get("above_avwap_252low", True)`), SHORT defaults to `False` (`s.get("below_avwap_252low", False)`). Docstring explains this is for "backward-compat" but it means: when AVWAP signals are absent, LONG side **auto-passes** the AVWAP gate (vulnerability if the strategy is mis-classified as having AVWAP data), while SHORT side **auto-fails**. This is structurally the same silent-gap pattern B639 flagged on RSI default-50. Default-True on a boolean gate that's part of the fire condition means: future strategies (or new tickers without enough history) could fire LONG when AVWAP isn't even being computed. Latent silent-gap class. | MEDIUM |
| F2 | Docstring is present and accurate | — |
| **F-fire-count** | gates: above_r1 ~0.05 × vol_spike_15x ~0.20 × macd_bullish ~0.45 × above_avwap_252low ~0.55 × above_avwap_50low ~0.55 ≈ 0.0014 universe-wide BUT with default-True for AVWAP, effective fire rate could be higher. Conservative LONG ~5/yr; if AVWAP keys missing on lots of tickers, fire rate higher than this. **FAIL_FIRE_STARVED** projection. Five AND-gates is heavy stacking; B612 flagged this pattern. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) Status quo (keep default-True for AVWAP backward-compat) |
| (B) F1 swap LONG AVWAP to default-False (symmetric to SHORT) — strict gate; lower fire rate but clean semantics |
| **(C)** F1 swap LONG default-False + loosen AVWAP requirement from BOTH-anchors to EITHER-anchor (OR not AND) — lighter gate count, symmetric defaults. Plus flag for B603 cube fire-count check. **RECOMMENDED.** |
| (D) Stage 5 deferral — defer everything to cube |

**My recommendation: (C).** Closes the latent silent-gap class AND addresses fire-count starvation with a single change. Risk: AVWAP-EITHER may fire too often; cube validates.

### FINAL STATUS POST-B659 — ✅ SHIPPED (was DEFERRED through B645; resolved B659)

| Item | Outcome |
|---|---|
| **Reviewer's M3 critique** | The F1 LATENT (AVWAP default-True auto-pass) and F-fire-count (5/yr FAIL) findings were internally contradictory — one said the gate auto-passes inflating fires, the other said fires were too few. Option C tried to do both (tighten default-False + loosen AND→OR) in one change — net effect indeterminate, justified by a fire-count label that was itself wrong-signed. **Resolved by B659:** F1 (default-True symmetry-break) closed via owner directive 2026-06-09 "implement autonomously"; F-fire-count was the wrong-signed label per B641 measurement (917/yr PASS_CUBE not 5/yr FAIL) so no loosening needed. |
| **Action taken at B641** | **Deferred entirely from Tier 1.** No code change shipped that batch — the reviewer's structural objection was decisive at the time. |
| **Action taken at B659** | **LONG AVWAP default-True → default-False symmetric with SHORT** — same fix pattern as B641 W8 F1+F1b + B657 T8 weekly Kumo. Strategy now properly fails-safe to no-fire when AVWAP signals are absent rather than auto-passing the gate. **Closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY ticket.** |
| **Code reference** | [screener.py strat_pivot_r1_breakout](backtest/signals/screener.py) — line ~474: `avwap_long_ok = s.get("above_avwap_252low", False) and s.get("above_avwap_50low", False)` (was `True`/`True`) |
| **Test pins (B659)** | `test_batch659_silent_gap_unify.py` — 4 pins for W6 LONG default-False semantics: (a) W6 LONG fires with both AVWAP keys True, (b) W6 LONG does NOT fire when above_avwap_252low key absent, (c) W6 LONG does NOT fire when above_avwap_50low key absent, (d) symmetric to SHORT side which has always been default-False |
| **Measured fires/yr (universe) — pre-B659** | **2,617 PASS_CUBE PRELIMINARY** (B648 random-30 × 16.77 scale; was reported as 917 on B641 smoke with hardcoded-220 scale — corrected post-B648). Independence under-counted by 500× on the pre-B648 sample. The strategy is NOT fire-starved at any scaling. |
| **Measured fires/yr (universe) — post-B659** | **Pending B660** — expected modest drop on tickers with insufficient AVWAP-anchor history (where the pre-B659 default-True path was auto-passing the gate). On tickers with full history, no behavior change since the gate evaluates symmetrically. |
| **Open items queued** | (1) Cube empirical decision: even at 2.6k/yr the strategy may benefit from one of the original B640 Step-7 loosening options (e.g., drop ADX-trending — covered by ema_50_200_bullish + above_r1 confluence); deferred to R5 cube as `S5-W6-W7-PIVOT-GATE-OPTIMIZATION`. (2) `S4-OBV-LOCATION-TENSION-DESIGN` cross-ref (W6 has OBV-vs-location concern shared with W1/W3/W9). |
| **Reviewer's M5 specifically** | **CLOSED.** Severity unification was the right concern; B659 implements it. W6/W7 LONG default-True was the same auto-pass class as W8's F1b. The arbitrary severity split in B640 has been retired; all four LONG silent-gap cases (W6/W7/W8 AVWAP + T8 weekly Kumo) now share a single fix policy. |
| **No regrets** | Deferring at B641 was the right call given the F1 vs fire-count contradiction. The B660 cube measurement will tell us whether the strategy needs additional changes — at 2.6k/yr post-fix it may be fine as-is. |

---

## W7. `strat_pivot_r2_continuation`

### Step 1 — Read the code

[screener.py:247-278](backtest/signals/screener.py#L247-L278):

```python
def strat_pivot_r2_continuation(s):
    """Pivot R2 trend-continuation. Batch 205: requires AVWAP + 2x volume
    (stronger threshold than R1 since R2 is the secondary breakout) +
    EMA 50/200 trend confirmation."""
    avwap_long_ok = s.get("above_avwap_252low", True) and s.get("above_avwap_50low", True)
    avwap_short_ok = s.get("below_avwap_252low", False) and s.get("below_avwap_50low", False)
    fl = (
        s.get("above_r2") and s.get("adx_trending")
        and s.get("ema_50_200_bullish") and avwap_long_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    fs = (
        s.get("below_s2") and s.get("adx_trending")
        and s.get("ema_50_200_bearish") and avwap_short_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    return _strat3(fl, fs, "pivot", ...)
```

**LONG fires when ALL FIVE (technically SIX — `avwap_long_ok` is two-AND):**

| Gate | Meaning |
|---|---|
| `above_r2` | Today's close > R2 (further out than R1) |
| `adx_trending` | ADX > 25 (trend strength) |
| `ema_50_200_bullish` | Long-term uptrend |
| `above_avwap_252low AND above_avwap_50low` | Both AVWAP anchors confirm |
| `vol_spike_2x` (fallback `vol_spike_15x`) | 2× volume (or 1.5× fallback if 2x key missing) |

Notice the chained `s.get("vol_spike_2x", s.get("vol_spike_15x", False))` — clever fallback. If vol_spike_2x is present, use it; otherwise fall back to vol_spike_15x; otherwise False. **This is fine** because both are EVENT signals from the same producer.

### Step 2-6 — same structure as W6

Same B291 default regime. Producer symmetry ✅ post-B633/B634. Docstring present. No OPEN_INV matches.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1 LATENT** | Same AVWAP asymmetric default as W6 | MEDIUM |
| F2 | Docstring present | — |
| **F-fire-count** | 5 AND-gates including vol_spike_2x (~0.10 prior) + ema_50_200_bullish (STATE ~0.55) + adx_trending (~0.30) + above_r2 (~0.02) + avwap (~0.55^2 ≈ 0.30 joint). Joint ~0.000099 → ~5.5/yr. **FAIL_FIRE_STARVED** very confidently. B612 stacking pattern. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) Status quo |
| (B) F1 swap LONG default-False on AVWAP (same as W6) |
| (C) F1 + drop ADX gate (covered by ema_50_200_bullish + above_r2 confluence) |
| **(D)** Stage 5 deferral — defer all fire-count + asymmetric-default fixes to cube data. Too many simultaneous changes per CHECKLIST (g) sequence-or-split. **RECOMMENDED.** |

**My recommendation: (D).** Five gates is heavy. Loosening multiple would violate CHECKLIST (g). Defer to cube empirical.

### FINAL STATUS POST-B659 — ✅ SHIPPED B659 (default-False unify) + ⏸ STAGE-5-DEFERRED on 6-gate width

| Item | Outcome |
|---|---|
| **Reviewer's structural critique** | Six-gate AND-conjunction is over-specification / curve-fitting by gate-stacking. Even if it backtests well, n is too small to be statistically significant; a strategy validated on a handful of trades will not generalize. Classic "stack filters until the equity curve is pretty on five trades" trap. **STATUS:** Width concern remains valid; B659 fix is orthogonal (silent-gap symmetry, not width). |
| **Action taken at B641** | **No code change.** Option (D) Stage 5 deferral upheld for the width concern. Reviewer's reasoning + the same M5 AVWAP default-True severity-unify question that gates W6 also gates W7. |
| **Action taken at B659** | **LONG AVWAP default-True → default-False symmetric with SHORT** — same fix as B659 W6 simultaneously. Strategy now fails-safe on missing AVWAP keys rather than auto-passing. **Closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY.** The width concern is preserved as a separate Stage 5 item (`S5-W6-W7-PIVOT-GATE-OPTIMIZATION`). |
| **Code reference** | [screener.py strat_pivot_r2_continuation](backtest/signals/screener.py) — line ~511: `avwap_long_ok = s.get("above_avwap_252low", False) and s.get("above_avwap_50low", False)` (was `True`/`True`) |
| **Test pins (B659)** | `test_batch659_silent_gap_unify.py` — 4 pins for W7 LONG default-False semantics, symmetric to W6 test pins |
| **Measured fires/yr (universe) — pre-B659** | **224 PASS_CUBE PRELIMINARY** (B648 random-30 × 16.77 scale; was reported as 66 on B641 smoke with hardcoded-220 scale — corrected post-B648). Independence under-counted again. |
| **Measured fires/yr (universe) — post-B659** | **Pending B660** — expected modest drop on tickers with insufficient AVWAP-anchor history. The 6-gate width concern persists at any fire rate. |
| **Open items queued** | (1) `S5-W6-W7-PIVOT-GATE-OPTIMIZATION` — 6-gate width simplification: ADX-trending is redundant with ema_50_200_bullish + above_r2 (reviewer noted this in B640 Step 7 option C). Owner-decision deferred to post-cube empirical. (2) `S4-OBV-LOCATION-TENSION-DESIGN` cross-ref — W7 doesn't directly use OBV but the pattern is conceptually related. |
| **Long-term recommendation** | Even if cube validates 224/yr, the 6-gate conjunction should be simplified to 2-3 orthogonal gates before deployment. ADX-trending is redundant with ema_50_200_bullish + above_r2. The strategy as-written is unlikely to have generalizable edge at 6-gate width. **Walk this strategy again in a follow-on Stage 4 batch** after B660 lands with a width-simplification proposal. |
| **No regrets** | Deferral on width preserves optionality; B659 ships the silent-gap fix without making the width problem worse. Cube empirical adjudicates the width question. |

---

## W8. `strat_cpr_narrow_bullish`

### Step 1 — Read the code

[screener.py:281-312](backtest/signals/screener.py#L281-L312):

```python
def strat_cpr_narrow_bullish(s):
    """Central Pivot Range narrow breakout. Batch 205 ... above CPR + above
    AVWAP is the canonical institutional-grade directional day signal.

    Batch 358 ... added 200-EMA regime gate per direction. ... Long now requires
    above_200_ema; short requires below_200_ema (canonical regime alignment).
    """
    avwap_long_ok = s.get("above_avwap_50low", True)
    avwap_short_ok = not s.get("above_avwap_50low", False)  # <-- F1 silent-gap pattern
    above_200 = s.get("price_above_ema_200", False)
    fl = (
        s.get("cpr_narrow") and s.get("above_cpr")
        and s.get("rsi_14", 50) > 50 and avwap_long_ok
        and above_200
    )
    fs = (
        s.get("cpr_narrow") and s.get("below_cpr")
        and s.get("rsi_14", 50) < 50 and avwap_short_ok
        and (not above_200)
    )
    return _strat3(fl, fs, "pivot", ...)
```

**LONG fires when ALL FIVE:**

| Gate | Meaning |
|---|---|
| `cpr_narrow` | Yesterday's CPR width < 15% of yesterday's range (directional-day setup) |
| `above_cpr` | Today's close > CPR top |
| `rsi_14 > 50` | Bullish momentum bias |
| `above_avwap_50low` (default True) | Above 50-day-low AVWAP — **OR keys missing** |
| `price_above_ema_200` | Long-term uptrend |

**SHORT fires when ALL FIVE:**

| Gate | Meaning |
|---|---|
| `cpr_narrow` | Same |
| `below_cpr` | Today's close < CPR bottom |
| `rsi_14 < 50` | Bearish momentum |
| `not above_avwap_50low` | Below AVWAP — **but using NOT pattern → silent-gap** |
| `not price_above_ema_200` | Long-term downtrend |

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: no entry → B291 default
- Last touched: B358 (added 200-EMA regime gate)

### Step 3 — Producer source-read + temporality

- `cpr_narrow`, `above_cpr`, `below_cpr` — EVENT/STATE hybrid (CPR known from yesterday)
- `above_avwap_50low` — STATE-ish
- `price_above_ema_200` — STATE
- `rsi_14` — STATE

### Step 4 — Doc-vs-thesis

Docstring present. Cites Batch 358 200-EMA add reason. ✅

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅ (dual). But SHORT uses NOT pattern on `above_avwap_50low` — silent-gap pattern owner has explicitly memory-flagged in `feedback_never_use_NOT_s_get_pattern`. The producer `below_avwap_50low` exists (B612), so this can be fixed locally.

Same for `not above_200` — should use `below_ema_200` (B630 producer-additive).

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | SHORT side uses `not s.get("above_avwap_50low", False)` — silent-gap pattern. Producer `below_avwap_50low` exists; one-line F1 swap per `feedback_never_use_NOT_s_get_pattern`. | HIGH |
| **F1b** | SHORT side uses `(not above_200)` where `above_200 = s.get("price_above_ema_200", False)`. The `not False = True` semantics mean missing key auto-passes the SHORT gate. Should use `s.get("below_ema_200", False)` symmetric positive (B630 producer). | HIGH |
| F2 | Docstring present | — |
| **F-fire-count** | LONG ~13/yr, SHORT ~13/yr. 5 AND-gates is heavy. **FAIL_FIRE_STARVED.** Flag for B603. | HIGH |

**Options:**

| Option | Description |
|---|---|
| (A) Status quo |
| **(B)** F1 + F1b swap to positive symmetric `below_avwap_50low` and `below_ema_200` per memory directive. **RECOMMENDED.** |
| (C) B + loosen one gate (e.g., drop `cpr_narrow` since it's a STATE-ish setup-day filter, not a fire trigger) |
| (D) Stage 5 deferral |

**My recommendation: (B).** F1/F1b are unambiguous family-bug fixes per existing memory directive. Fire-count loosening is a separate (C) decision.

### FINAL STATUS POST-B665 — ⚠ DIAGNOSIS CONFIRMED, CURE PARTIAL (revised per 2nd-wave-redux #1)

> **Honest re-framing per 2nd-wave-redux critique #1 (2026-06-09, owner-approved B665 revert).** The earlier "TRIPLE SHIPPED / all B640-cycle queue items closed" framing was the recurrence of the 2C7 CHANGES-MERGED vs VALIDATED conflation on its own flagship example. The post-B654 measured fire-count is 10,723/yr = fires every ~12 trading days per ticker = the strategy is still a near-permanent state flag. The fix reduced redundancy from catastrophic (~4 days) to severe (~12 days); the 4-of-5 → 3-of-4 uptrend-proxy structure persists (`above_cpr` + `above_avwap_50low` + `above_ema_200` all still co-move with "is there an uptrend"); the `cpr_narrow_tight` at 0.05 carries the entire discrimination load; the CPR foundation literature gap (folk-TA without academic support per reviewer C1+W8) is untouched. **Diagnosis confirmed by B654 -68% measured-vs-predicted match; cure partial; foundation unproven.** New ticket opened: `S5-W8-POST-B654-REMAINING-REDUNDANCY-AUDIT`.

| Item | Outcome |
|---|---|
| **What shipped (B641)** | **Option (B) F1+F1b silent-gap fixes.** SHORT side `not s.get("above_avwap_50low", False)` (NOT-pattern auto-pass on missing key) → positive symmetric `s.get("below_avwap_50low", False)` (B612 producer; defaults False → fail-safe). SHORT side `(not above_200)` where above_200 = local with default False (same auto-pass class) → explicit `s.get("below_ema_200", False)` (B630 producer-additive). Both new gates default-False → fail-safe to no-fire on missing key. |
| **What shipped (B654) — redundancy audit option B-local per 2C2 corrected methodology** | **Two fixes in same batch per `feedback_path_c_min_batch_size`:** (1) Producer-additive `cpr_narrow_tight` with 0.05 threshold (vs 0.15 loose threshold on existing `cpr_narrow`). B574-style narrow-scope: W8 is the only consumer of the tight variant; other 2 consumers (`strat_cpr_narrow_momentum` + `strat_cpr_narrow_momentum_short`) retain loose threshold pending their own walks per `feedback_narrow_scope_blast_radius`. (2) Dropped `rsi_14 > 50` LONG / `rsi_14 < 50` SHORT strict-inequality gates per `feedback_never_use_NOT_s_get_pattern` precedent (same accidentally-safe no-op pattern that B654 W8 RSI shares with B639 candle-pattern RSI gates). Gate count went from 5 → 4 per direction (cpr_narrow_tight + above_cpr + below_avwap_50low + above_ema_200 LONG / cpr_narrow_tight + below_cpr + below_avwap_50low + below_ema_200 SHORT). **Closes both S4-W8-REDUNDANCY-AUDIT + S4-W8-RSI-NOOP-GATE.** |
| **What shipped (B659) — LONG default-False unify per M5** | **LONG side `s.get("above_avwap_50low", True)` → `s.get("above_avwap_50low", False)`** symmetric with SHORT side (which has used default-False since B641). Same fix pattern as B641 W8 SHORT + B657 T8 weekly Kumo + B659 W6 + B659 W7 (4 strategies / 5 gates moved to default-False in unified policy). **Closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY (specifically the W8 portion).** |
| **Code reference** | [screener.py strat_cpr_narrow_bullish](backtest/signals/screener.py) — current gate set: `fires = s.get("cpr_narrow_tight") and s.get("above_cpr") and s.get("above_avwap_50low", False) and s.get("price_above_ema_200", False)` LONG / `fires = s.get("cpr_narrow_tight") and s.get("below_cpr") and s.get("below_avwap_50low", False) and s.get("below_ema_200", False)` SHORT |
| **Test pins** | `test_batch641` pins 10-12 (SHORT no longer uses NOT-pattern; fires on positive symmetric; blocks when keys missing) + `test_batch654_w8_cpr_narrow_redundancy.py` (B654 cpr_narrow_tight gate isolation + RSI noop drop + 5→4 gate count assertions) + `test_batch659_silent_gap_unify.py` (B659 LONG default-False symmetric with SHORT) |
| **Measured fires/yr (universe) — pre-B654** | **34,004 PASS_CUBE** _by extreme over-determination_ — fires every ~4 trading days per ticker on B648 random-30. 4 of 5 LONG gates were uptrend proxies (above_cpr + rsi>50 + above_avwap_50low + above_ema_200 all co-occur in established uptrends) — REDUNDANT not confluent per B649 corrected methodology. cpr_narrow at 0.15 threshold fired ~87% of bars = NEAR-NO-OP filter defeating the "narrow CPR predicts directional day" thesis. |
| **Measured fires/yr (universe) — post-B654** | **10,723 PASS_CUBE (-68%)** per `output_audit/fire_count_measured_b654_w8_post_redundancy_fix.json` — fires every ~12 trading days per ticker on same B648 random-30 sample. **Validates the 4-of-5-gate redundancy thesis to within 5% of B654 pre-fix projection.** Once the no-op RSI gate dropped AND cpr_narrow_tight (0.05 threshold, fires ~15% of bars) replaced cpr_narrow (0.15 threshold, fires ~87% of bars), the strategy moves from "is there an uptrend right now" disguised-as-CPR-precision to a more conventional 12-day-cycle directional-day filter. |
| **Measured fires/yr (universe) — post-B659** | **Pending B660** — expected modest additional drop on tickers with insufficient AVWAP-anchor history (where pre-B659 default-True LONG path was auto-passing the gate). The combined post-B654 + post-B659 fire rate is expected to land around 8-10k/yr per ticker which is still PASS_CUBE on the min_trades=30 threshold but materially lower noise than the pre-B654 34k/yr rate. |
| **Open items queued** | **All B640-cycle open items now closed.** Still alive at program level: (a) `S5-W8-CPR-FOUNDATION-AUDIT` — reviewer's structural critique on CPR foundation (folk-TA popular among India retail traders; no academic support; daily-bar application on intraday tool per C1). Deferred to Stage 5 cube empirical decision — if the post-B654+B659 strategy doesn't show alpha in cube, reframe-and-rename or deprecate per CHECKLIST (r). |
| **Reviewer's structural critique on CPR foundation** | Reviewer W8 noted: "CPR's narrow-range-predicts-trending-day claim has no academic support — folk-TA popular among India retail traders. Applying it on daily bars held overnight stacks an unproven claim on top of a timeframe error (C1)." Acknowledged: even with the 10.7k/yr post-B654 fires, this is the strategy with the SHAKIEST theoretical foundation in the cluster. The B654 fix made the RSI-noop and gate-redundancy concerns disappear, but the CPR-foundation question is independent — that's a Stage 5 cube decision. The CHECKLIST (r) timeframe-mismatch codification names this hazard going forward. |
| **No regrets** | F1/F1b shipped at B641 were unambiguous family-bug fixes; B654 redundancy audit + RSI-noop drop validated the 2C2 corrected methodology to within 5%; B659 closed the M5 LONG default-True unification. Three batches across three different audit findings, all converging on the same strategy. The CPR-foundation concern is queued for Stage 5 without polluting the B641-B659 code-change deliverables. |

---

## W9. `strat_camarilla_s3_bounce`

### Step 1 — Read the code

[screener.py:315-356](backtest/signals/screener.py#L315-L356):

Already walked thoroughly during B628 (F1 family-sweep) — docstring + walk record present.

```python
def strat_camarilla_s3_bounce(s):
    # B628 F1: positive symmetric (B617 producer)
    fl = (s.get("near_cam_s3") and s.get("rsi_14", 50) < 35 and s.get("obv_bullish"))
    fs = (s.get("near_cam_r3") and s.get("rsi_14", 50) > 65 and s.get("obv_bearish"))
    return _strat3(fl, fs, "pivot", ...)
```

3-gate dual: location (near Camarilla S3/R3) + RSI extreme (<35 / >65) + OBV flow.

### Step 2 — Classify

- STRATEGY_REGIME_AFFINITY: explicit `{"neutral", "bear", "crisis"}` at [regime_selector.py:191](backtest/engine/regime_selector.py#L191).
- **DEFERRED-STAGE-5** per B624 manifest M1 — this entry is a B623 REMOVE_OK candidate; cube data needed.
- Last touched: B628

### Steps 3-6 — already documented in B628 + B624 manifest

Producer symmetric ✅, docstring ✅, OPEN_INV no matches.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None — already fixed B628 | — |
| F2 | Docstring already present | — |
| **F3** | Already deferred per B624 manifest M1 (R5 ticket S5-REGIME-AFFINITY-21-DEFERRED). **No walk-time action.** | — |

**Fire-count projection:** LONG ~30/yr — borderline PASS.

**Options:**

| Option | Description |
|---|---|
| **(E)** No action needed; defer per existing R5 ticket. **RECOMMENDED.** |
| Other | Re-litigating would create a B624 manifest conflict |

**My recommendation: (E).**

### FINAL STATUS POST-B645 — ⏸ ALREADY DEFERRED (no action)

| Item | Outcome |
|---|---|
| **What shipped** | Nothing — strategy already deferred per existing `S5-REGIME-AFFINITY-21-DEFERRED` (B624 manifest M1) |
| **Measured fires/yr (universe)** | **44** BORDERLINE (between FAIL_FIRE_STARVED <30 and PASS_CUBE ≥60) — projection was right here; independence ratio 31.7 over-counted by 32× but the actual measured rate is close to the borderline |
| **Reviewer's W9 note** | The reviewer specifically noted W9 is "the only pivot strategy using its source system as intended" — Camarilla's design says R3/S3 are FADE levels, and W9 trades the fade. The W10 R3→R4 rename (B641) closed the same-level conflict that existed pre-B641 (W9 short at R3 vs W10 long above R3 simultaneously); W9 stays unchanged. |
| **Open items** | Inherits the cluster-wide intraday-on-daily-bar concern (CHECKLIST (r)) — Camarilla is intraday by design. Reframe argument: even on daily bars, Camarilla S3 proximity + RSI extreme + OBV flow detects "yesterday's range was extended → today retraced + reversal-flow appearing," a coherent daily-bar pattern independent of pivot-precision. |
| **No regrets** | Correct deferral. The R5 cube empirically validates the regime-affinity entry. |

---

## W10. `strat_camarilla_r3_breakout`

### Step 1 — Read the code

[screener.py:359-365](backtest/signals/screener.py#L359-L365):

```python
def strat_camarilla_r3_breakout(s):
    fl = (s.get("above_cam_r3") and s.get("vol_spike_2x"))
    fs = (s.get("below_cam_s3") and s.get("vol_spike_2x"))
    return _strat3(fl, fs, "pivot",
        ["above_cam_r3","vol_spike_2x"], ["below_cam_s3","vol_spike_2x"],
        ["Price broke above Camarilla R3  -  breakout mode","Volume 2x confirms institutional buying"],
        ["Price broke below Camarilla S3  -  breakdown mode","Volume 2x confirms institutional selling"])
```

**LONG fires when both:**

| Gate | Meaning |
|---|---|
| `above_cam_r3` | Today's close > Camarilla R3 (primary resistance) |
| `vol_spike_2x` | Volume ≥ 2× 20-day average |

**SHORT mirror:** `below_cam_s3 + vol_spike_2x`.

### Step 2 — Classify

- Category: `pivot`
- Dual
- STRATEGY_REGIME_AFFINITY: no entry → B291 default
- Last touched: original implementation

### Step 3 — Producer source-read + temporality

Both gates EVENT (cross + today's volume).

### Step 4 — Doc-vs-thesis

Context bullets accurate. **F2 — no docstring.**

### Step 5 — OPEN_INVESTIGATIONS grep

No matches.

### Step 6 — Missing-inverse + economic-symmetry

Structural ✅. Economic ✅. Producer symmetric ✅.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | None | — |
| **F2** | No docstring | LOW |
| **F-fire-count** | gates: above_cam_r3 ~0.05 × vol_spike_2x ~0.10 ≈ 0.005 → ~166/yr/direction. PASS_CUBE. Wide setup; clean 2-gate strategy. | — |

**Options:**

| Option | Description |
|---|---|
| **(A)** F2 docstring with Camarilla source citation (Slim Khan / Nick Scott) + R3 breakout vs S3 breakdown thesis. **RECOMMENDED.** |
| (B) Status quo |

**My recommendation: (A).**

### FINAL STATUS POST-B645 — ✅ CLOSED (renamed + re-anchored)

| Item | Outcome |
|---|---|
| **Reviewer's P5 critique** | "Camarilla R3 is the FADE level, not the breakout level — R4 is the breakout level per Slim Khan / Nick Scott. W9 (short near R3) and W10 (long above R3) take OPPOSITE trades at the SAME level — a single bar at R3 with a volume spike could fire W9 SHORT and W10 LONG simultaneously, a portfolio-level contradiction that nets to noise and double costs." |
| **What shipped (B641)** | **R3 → R4 SOURCE-SYSTEM RE-ANCHOR.** Strategy renamed `strat_camarilla_r3_breakout` → `strat_camarilla_r4_breakout`. Producer signals swapped `above_cam_r3` → `above_cam_r4` and `below_cam_s3` → `below_cam_s4` (these signals already exist per BUG-09 Pass 53 symmetric pair). Registry key renamed `camarilla_r3_breakout` → `camarilla_r4_breakout`. W9 keeps using R3/S3 proximity for FADE (correct Camarilla usage). |
| **What this resolves** | (1) Source-system contradiction (B640 W10 was misusing Camarilla); (2) Same-level conflict with W9; (3) Honest docstring with Slim Khan / Nick Scott citation; (4) F2 documentation gap. |
| **Code reference** | [screener.py strat_camarilla_r4_breakout](backtest/signals/screener.py) (renamed) |
| **Test pins** | test_batch641 pins 13-17 — R3 not importable (renamed), R4 importable + callable, registry renamed, R4 fires on above_cam_r4 + vol_spike_2x, R4 does NOT fire on above_cam_r3 alone (proves the swap happened) |
| **Measured fires/yr (universe)** | **991 PASS_CUBE** (was 166 projected; independence under-counted) |
| **Backward-compat references** | Updated in: test_batch358 (previously_deprecated set), config.py (Marshall-Cahan 2008 cite comment), test_silent_gap_pyramid. Stale dashboard files + parquet snapshots still reference `camarilla_r3_breakout` but those are output-state files that regenerate. |
| **No regrets** | One of the most defensible ships in the batch — strict source-system honesty + resolves a portfolio-level conflict + same-day W9 isolation cleanly. |

---

## Bundled action items (historical record — original B640 surface)

> Preserved as historical record of the original B640 prospective surface. The final dispositions below replace this section's "owner decision form" with the actual shipped outcomes.

### Tier 1 — definite fixes (no judgment needed) [SHIPPED]:
- **W8 F1+F1b** — silent-gap positive symmetric swap → ✅ SHIPPED B641
- **W3 F3** — B271 family-bug delete → ✅ SHIPPED B641
- **W4 F3** — B271 family-bug delete → ✅ SHIPPED B641

### Tier 2 — docstring adds (low risk) [SHIPPED PARTIAL]:
- **W1** F2 docstring → ✅ SHIPPED B641 (with "three systems" commentary fix per reviewer)
- **W2** F2 docstring → ✅ SHIPPED B641
- **W3** F2 docstring → ✅ SHIPPED B641 (bundled with F3 + F1 pin_bar fix)
- **W4** F2 docstring → 🎯 QUEUED in `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` (split per CHECKLIST (g))
- **W5** F2 docstring → ✅ SHIPPED B643 (as part of redesign)
- **W10** F2 docstring → ✅ SHIPPED B641 (bundled with R3→R4 rename)

### Tier 3 — judgment calls [RESOLVED]:
- **W5 Class 7 NEW mirror** → ✅ SHIPPED B645 per directive (a) AFTER B643 redesign + B644 W5-i exploratory
- **W4 F1 `shooting_star` SHORT OR** → 🎯 QUEUED `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL`
- **W6 F1 LATENT** → ⏸ DEFERRED via `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` (reviewer M3+M5)
- **W7 over-specification** → ⏸ DEFERRED to Stage 5 per CHECKLIST (g)
- **W2 fire-count** → ✅ MEASURED + DEFERRED (139/yr PASS_CUBE — no loosening needed; B640 FAIL was independence artifact)
- **W6/W7/W8 fire-count stack** → ✅ MEASURED — all PASS_CUBE post-measurement (independence under-counted 35-1200×)

### Tier 4 — no action [HELD]:
- **W9** — already deferred to R5 ✅ unchanged

---

## FINAL DISPOSITIONS

> Replaces the "Owner decision form" with what actually happened. Read top-to-bottom; this is the closing summary of what shipped across the B641 → B660 cycle (original B641-B645 + follow-on B650-B660).

| W# | Strategy | Original B640 recommendation | Owner's actual direction | What shipped (B641-B645) | Follow-on (B650-B660) | Final |
|---|---|---|---|---|---|---|
| W1 | `bullish_engulfing_support` | (A) | (A) | F2 doc + commentary | — | ✅ CLOSED |
| W2 | `shooting_star_short` | (D) | (D) | F2 doc + Stage 5 fire-count defer | — | ✅ CLOSED |
| W3 | `pivot_s1_bounce` | (B) | (B) + reviewer P1 added | F1 pin_bar fix (reviewer-flagged) + F2 doc + F3 regime delete | — | ✅ CLOSED |
| W4 | `pivot_s2_bounce` | (C) | (C) split per (g) | F3 regime delete only; F1+F2+RSI-mislabel queued | — (still queued) | ✅ SHIPPED + 🎯 queued |
| W5 | `pivot_s3_capitulation` | (D) → reviewer P3 critique → option C redesign | C → W5-i | Producer + 2-gate redesign (B643) + EXPLORATORY marker (B644) | **B650** `vol_below_avg` Wyckoff Spring vol gate + **B651** regime expand all-regimes (post-redesign 5-day window may transition regimes) | ✅ REDESIGNED → EXPLORATORY + structural-vol-symmetry-complete |
| W5m | `pivot_r3_blowoff_short` (NEW B645) | n/a | directive (a) | Class 7 NEW symmetric mirror (B645) | **B652** stronger DO-NOT-DEPLOY gate (keyed on M10 + S5-MULTIPLE-TESTING-CORRECTION); **B659** `vol_below_avg` symmetric Upthrust-Test vol gate (closes S4-W5M-SYMMETRIC-VOL-GATE) | ✅ NEW → EXPLORATORY + DO-NOT-DEPLOY + structural-symmetry-complete |
| W6 | `pivot_r1_breakout` | (C) → reviewer M3 contradiction | DEFER | No code change; queue ticket | **B659** LONG AVWAP default-True → False symmetric with SHORT (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY) | ✅ SHIPPED B659 (was DEFERRED) |
| W7 | `pivot_r2_continuation` | (D) | (D) | No code change | **B659** LONG AVWAP default-True → False symmetric with SHORT (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY) | ✅ SHIPPED B659 (was DEFERRED) — 6-gate width still queued S5 |
| W8 | `cpr_narrow_bullish` | (B) | (B) | F1+F1b silent-gap positive symmetric (B641) | **B654** producer-additive `cpr_narrow_tight` 0.05 + RSI-50 noop drop (closes S4-W8-REDUNDANCY-AUDIT + S4-W8-RSI-NOOP-GATE; **validates 2C2 corrected methodology with -68% measured drop**); **B659** LONG `above_avwap_50low` default-True → False (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY) | ✅ TRIPLE SHIPPED — all B640-cycle queue items closed; only CPR-foundation S5 concern remains |
| W9 | `camarilla_s3_bounce` | (E) | (E) | No action (R5-deferred existing ticket) | — | ⏸ HOLDS (inherits S5-REGIME-AFFINITY-21-DEFERRED) |
| W10 | `camarilla_r3_breakout` | (A) → reviewer P5 critique | (A) → directive 6 R3→R4 | Strategy renamed + producer swap + source-system citation | — | ✅ CLOSED (RE-ANCHORED) |

**Net code impact (B641 → B660, 24+ commits):**

*B641-B645 originals:*
- 1 new producer-additive pair: `bullish_pin_bar` / `bearish_pin_bar`
- 2 new lookback producers: `compute_capitulation_lookback`, `compute_blowoff_lookback`
- 4 strategies modified: `pivot_s1_bounce` (P1 fix), `cpr_narrow_bullish` (F1+F1b), `pivot_s3_capitulation` (full redesign), `camarilla_r4_breakout` (rename from r3)
- 2 regime affinity entries deleted: `pivot_s1_bounce`, `pivot_s2_bounce` (B271 family-bug fixes #5+#6)
- 1 new strategy registered: `pivot_r3_blowoff_short` (Class 7 NEW)
- 1 engine module updated: `regime_filter.py` (B642 dead canonical line removal + EMA-cross hysteresis 2% band)
- 1 new tool: `scripts/measure_fire_count.py`
- 3 CHECKLIST extensions: (r) timeframe-mismatch, (s) EVENT/STATE wired-to-finding, Step 1.5 avoid-branch restore

*B650-B660 follow-on additions:*
- 1 producer-additive narrow-scope variant: `cpr_narrow_tight` (B654; 0.05 threshold; W8-only consumer)
- 2 producer-additive narrow-scope lookback variants: `supertrend_flip_recent_long_5d` / `_short_5d` (B655; T10-only consumer — trend cluster cross-ref)
- 5 strategies modified post-B645:
  - `pivot_s3_capitulation` (B650 vol gate + B651 regime expand)
  - `pivot_r3_blowoff_short` (B652 DO-NOT-DEPLOY gate + B659 vol gate)
  - `cpr_narrow_bullish` (B654 cpr_narrow_tight swap + RSI noop drop + B659 LONG default-False)
  - `pivot_r1_breakout` (B659 LONG default-False)
  - `pivot_r2_continuation` (B659 LONG default-False)
- 3 strategies modified cross-cluster (trend doc):
  - `strat_supertrend_macd` (B655 STATE → EVENT-anchored)
  - `strat_hull_rsi` (B656 RSI noop drop + B659 SHORT below_ema_200)
  - `strat_ichimoku_cloud_breakout` (B657 weekly Kumo default-True → False)
- 1 measurement-tool fix: scale-factor bug (B648; ×2.3 understatement corrected + random sampling option)
- 1 doc re-framing batch (B649; 2C2 inverted-methodology correction)
- 1 background full-universe measurement run launched (B660; in flight)

**Net queue impact:** 17 first-wave tickets in `EXECUTION_QUEUE.md` + 8 new tickets surfaced by audit responses + cross-refs. **5 first-wave tickets closed by follow-on cycle** (S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY, S4-W8-REDUNDANCY-AUDIT, S4-W8-RSI-NOOP-GATE, S4-W5M-SYMMETRIC-VOL-GATE, S4-T3-NOT-ABOVE-200-EMA-PATTERN).

---

## Outstanding queue tickets from this audit cycle

> All 17 first-wave tickets were present in `EXECUTION_QUEUE.md`; the follow-on cycle (B654 + B655-B657 trend-cross-cluster + B659) closed **5 of 17**. The remaining 12 first-wave tickets + 8 new tickets surfaced by audit responses are listed below.

### ✅ CLOSED by follow-on cycle (B654 + B659)

| Ticket | Closed by | Description |
|---|---|---|
| `S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY` | **B659** | W6/W7/W8 LONG AVWAP default-True → False symmetric with SHORT (3-strategy unified policy) |
| `S4-W8-REDUNDANCY-AUDIT` | **B654** | W8 redundancy audit option B-local: cpr_narrow_tight 0.05 producer + RSI-50 noop drop. Validates 2C2 corrected methodology with 34k → 10.7k measured drop (-68%) within 5% of prediction |
| `S4-W8-RSI-NOOP-GATE` | **B654** (bundled) | Same B654 batch dropped the `rsi_14 > 50` strict-inequality noop gates per `feedback_never_use_NOT_s_get_pattern` precedent |
| `S4-W5M-SYMMETRIC-VOL-GATE` | **B659** | W5m `vol_below_avg` AND-required on SHORT reversal-trigger bar (symmetric Wyckoff Distribution Upthrust-Test mirror of B650 W5 LONG Spring vol gate) |
| `S4-T3-NOT-ABOVE-200-EMA-PATTERN` | **B659** | T3 SHORT `(not above_200)` → positive symmetric `s.get("below_ema_200", False)` per `feedback_never_use_NOT_s_get_pattern`. **Cross-cluster** — T3 lives in `STAGE_4_TREND_CLUSTER_WALKS.md`; resolution shipped in same B659 bundle |

### ⏸ STILL OPEN — Stage 5 (cube + program-level)

| Ticket | Description |
|---|---|
| `S5-FIRE-COUNT-MEASURED-RUN-FULL` (was `S5-FIRE-COUNT-MEASURED-RUN`) | **IN FLIGHT B660** — first full-universe T1a × 2020-2026 × all 222 strategies. When landed, all `PRELIMINARY` qualifiers in this doc + STAGE_4_TREND_CLUSTER_WALKS.md retire and the verdict-reversals move from PRELIMINARY-CONFIRMED-DIRECTIONAL to AUTHORITATIVE. |
| `S5-MULTIPLE-TESTING-CORRECTION` | Bailey/LdP deflated Sharpe + Hansen SPA + BH FDR on cube selection. **W5m DO-NOT-DEPLOY gate** (B652) is keyed on this ticket landing before live deployment. |
| `S5-MARGINAL-CONTRIBUTION-SCORING` | Cube ranks strategies vs-book not standalone (extends M9 effective_strategy_count) |
| `S5-REGIME-BETA-ASSUMPTION` | Name the implicit "SPY/VIX state gates single-name strategies" assumption + design per-sector or per-name regime alternative for R5+ scope |
| `S5-REGIME-WALK-FORWARD-VALIDATION` | Freeze classifier as-of each historical date + measure forward regime-gating value (curve-fit check); also gates whether R3 EMA-cross-hysteresis 2% asymmetric design is OOS-net-positive |
| **NEW** `S5-W6-W7-PIVOT-GATE-OPTIMIZATION` | W6/W7 width simplification post-cube — ADX-trending redundant with ema_50_200_bullish + above_r1/r2 (reviewer noted in B640 Step 7); decision deferred until cube measures alpha at current 5-6 gate width |
| **NEW** `S5-W8-CPR-FOUNDATION-AUDIT` | If post-B654+B659 W8 doesn't show alpha in cube, reframe-and-rename or deprecate per CHECKLIST (r) — CPR has no academic support per reviewer C1+W8 critique |

### ⏸ STILL OPEN — Stage 4 (near-term, owner-policy)

| Ticket | Description |
|---|---|
| `S4-W4-F1-PLUS-F2-PLUS-RSI-MISLABEL` | W4 follow-on per CHECKLIST (g) — RSI<40 mislabeled "oversold" + F1 shooting_star SHORT OR + F2 docstring |
| `S4-OBV-LOCATION-TENSION-DESIGN` | W1/W3/W9 (LONG) OBV-vs-location tension — fresh decline into support means OBV likely below 20-bar mean → `obv_bullish` gate FIGHTS the support premise; owner-decision among (a) drop OBV, (b) reframe to `obv_diverge_bull`, (c) keep as deliberate filter |
| `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` | at_key_fib swing-anchor PIT verification + lookback=50 as hidden free parameter |
| `S4-CORPORATE-ACTION-POLICY` | Ex-date no-fire pyramid test for candle/pivot signals (splits/dividends manufacture phantom signals per reviewer C4) |
| `S4-SURVIVORSHIP-T1A-VERIFY` | Confirm T1a PIT universe includes delisted-during-window names (DEC-477 says 111 historical-removed rows; per-strategy adversarial verification still pending — applies to W5 LONG expectancy left tail + W5m SHORT right-tail squeeze risk) |
| `S4-REGIME-AAII-PIT` | Publication-vs-survey date PIT alignment audit |
| `S4-REGIME-FRED-VINTAGE` | T10Y2Y restated-vs-vintage policy; consider ALFRED |
| `S4-REGIME-SECTOR-ELIGIBILITY-TIME-VARYING` | Composite eligibility weaker in early backtest (≥200-bar requirement per ETF) |
| `S4-REGIME-COMPOSITE-FAIL-POLICY` | Bear composite fail-open vs system VIX fail-closed asymmetry |
| `S4-REGIME-HYSTERESIS-PARITY-TEST` | Backtest-vs-live regime divergence audit (use_hysteresis flag) |

### ⏸ NEW TICKETS surfaced by second-wave critique responses

| Ticket | Description |
|---|---|
| `S4-COST-AWARE-CUBE` (extension of existing `M10`) | Slippage haircut + borrow cost lookup + gap-at-entry modelling. **W5m DO-NOT-DEPLOY** keyed on this. |
| `S4-STAGE-4-WALK-FORWARD-METHODOLOGY` | Walk every strategy must use measurement-pass not independence-projection per CHECKLIST (k) — codified post-B649 inversion |
| `S5-REDUNDANCY-AUDIT-CLUSTER-SWEEP` | Apply the B654/B655 "per-gate what does THIS screen out" methodology to remaining 200+ strategies; current sweep covered W8/T3/T8/T10 only |
| `S5-EVENT-STATE-RATIO-DASHBOARD` | Dashboard 2 extension showing per-strategy EVENT-vs-STATE gate ratio + flagging STATE-heavy strategies for the M6+CHECKLIST (s) timing-fragility audit |

### Cross-ref existing tickets
- `M10` — already DEFERRED Stage 5+; this audit extended notes to include borrow lookup + gap-at-entry slippage per reviewer C6. **W5m DO-NOT-DEPLOY** (B652) explicit gate-key on M10 landing.
- `S5-REGIME-AFFINITY-21-DEFERRED` — W9 (camarilla_s3_bounce) inherits this existing ticket; no new entry created
- `PYRAMID-CLEANUP-ENV` — 14 pre-existing failures from B622 cleanup remain (unrelated to this audit cycle; mentioned only because B642 retested + confirmed they're not B642 regressions)

### Cross-cluster references
- **Trend cluster** ([STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md)) — closed T3/T8/T10 redundancy audits (B655-B657) via the same B649-corrected methodology that drove W8 here. Three originally-flagged trend strategies all confirmed AS EXPECTED: T10 was extreme NO-OP (99.19% True → STATE→EVENT swap), T3 was honest CONFLUENCE (gate-drop + status quo), T8 was honest CONFLUENCE with separate default-True silent-gap (status quo + default-False fix). |

---

## Methodology changes shipped this cycle

### CHECKLIST extensions (B641 commit a94f8bb02)

**`(r) Timeframe-mismatch check`** — codifies reviewer's C1. Any walk whose strategy uses an intraday-by-design indicator (pivots / Camarilla / CPR / ORB / intraday VWAP) must surface in Step 2 whether daily-bar application preserves the thesis or requires REFRAME-AND-RENAME. First application: W10 R3→R4 rename. Listed affected strategies: pivot_s1/s2/s3, pivot_r1/r2, cpr_narrow_bullish, camarilla_s3_bounce, camarilla_r4_breakout, prev_day_high_break, orb_*.

**`(s) EVENT/STATE wired-to-finding`** — codifies reviewer's M6. Step 3 already classifies signals as EVENT vs STATE; pre-B641 this was decorative. New rule: Step 6 explicitly counts EVENT gates per direction. If ≤1 EVENT gate per direction AND docstring overclaims timing on STATE → F-timing-fragility HIGH. The MACD-bullish-as-STATE pattern (reviewer's M7, W6 silent concession) is the canonical example.

**`Step 1.5 avoid-branch dead-code analysis`** — restores the morning_star B637 walk's per-strategy check. For every `_strat3` dual strategy, verify whether `fl ∧ fs` is structurally possible. If mutually exclusive, the avoid branch is dead code — three consequences recorded per walk.

### Fire-count measurement pass (B641 same commit)

`scripts/measure_fire_count.py` — replaces independence-product projections with measured fires/year against actual 220-ticker T1a OHLCV history. Output schema includes per-strategy gate-marginals, pairwise correlation matrix, and an `independence_predicted_vs_measured_ratio` diagnostic that tells you in which direction the independence assumption was biased (>1 = exclusive gates, over-estimated; <1 = positively-correlated gates, under-estimated). Vectorized signal precompute across (ticker, bar) — strategies evaluated against precomputed signals (not re-computed per strategy). Smoke run results landed on B645 commit fb20a946c.

### Regime classifier cleanup (B642 commit 013cc75b8)

Two changes per reviewer audit findings #2 + #3:
- **Dead canonical bear line removed** from both `classify_regime` and `classify_regime_with_hysteresis`. Pre-B642 the `VIX>=30 AND below-200EMA` line was subsumed by the post-B288 SPY-only gate; reading the code suggested VIX still gated bear, but it didn't. Removed for honest semantics. (Auto-resolves audit finding #6 latent redundancy as side-effect.)
- **EMA-cross hysteresis band added** — new `EMA_CROSS_HYSTERESIS_PCT = 2.0` constant + `spy_pct_from_200ema` parameter. Asymmetric design: bear stays sticky until SPY closes >=+2% above 200-EMA (slow to exit risk-off); below-EMA close still triggers bear immediately (fast risk-off entry). Backward-compatible with legacy callers (None spy_pct → pre-B642 binary-gate behavior).

12 new test pins in `test_batch642_regime_classifier_cleanup.py`. Cross-ref the [classifier deep-dive section](#how-market-regimes-are-classified--the-full-picture) earlier in this doc — that documentation predates B642 and still describes the pre-B642 ladder; **TODO: update classifier deep-dive section to reflect B642 changes** (queued for next-update pass).

---

## Going forward — cluster-organization policy

Per owner directive 2026-06-09, future Stage 4 walk bundles are per-cluster, not per-batch:

| Cluster | Doc filename | Status |
|---|---|---|
| **Pivot** | `STAGE_4_PIVOT_CLUSTER_WALKS.md` (this doc) | ✅ **LIVING — closed-out for B641-B660 cycle.** 8 of ~10 pivot strategies walked (W3-W10 + W5 mirror); `prev_day_high_break` + any tail strategies pending. All B641-cycle queue items closed (S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY = B659; S4-W8-REDUNDANCY-AUDIT + S4-W8-RSI-NOOP-GATE = B654; S4-W5M-SYMMETRIC-VOL-GATE = B659). B660 measurement landing back-fills authoritative numbers. |
| **Trend** | [`STAGE_4_TREND_CLUSTER_WALKS.md`](STAGE_4_TREND_CLUSTER_WALKS.md) | ✅ **LIVING — closed-out for cycle (was NEXT at original B645 close; shipped in B647-B658).** T1-T10 walked; **T3/T8/T10 redundancy audits closed** (B655-B658 cycle + B659 cross-cluster for T3 SHORT). Cross-references this pivot doc for shared methodology (B649 corrected redundancy-vs-confluence) + shared B660 measurement. |
| Candle | `STAGE_4_CANDLE_CLUSTER_WALKS.md` (future) | DEFERRED — W1, W2 covered here; earlier candle walks (morning_star B639, three_white_soldiers B636, doji_at_support B572-574, etc) will be consolidated into a candle cluster doc when next candle batch runs |
| Chart pattern | `STAGE_4_CHART_PATTERN_CLUSTER_WALKS.md` (future) | head_and_shoulders / double_bottom / cup_and_handle / flag_bull / triangle_ascending / etc. **Likely next cluster** per current Stage 4 progress |
| Smart money | `STAGE_4_SMART_MONEY_CLUSTER_WALKS.md` (future) | institutional_* / insider_* / 52w_high_with_smart_money / activist_13d / m_and_a_target / etc. ~30 strategies — largest pending cluster |
| SMC / ICT | `STAGE_4_SMC_ICT_CLUSTER_WALKS.md` (future) | smc_bos_continuation / smc_choch_reversal / smc_liquidity_sweep / turtle_soup / judas_swing / mmbm / week_opening_gap / etc |
| Volume | `STAGE_4_VOLUME_CLUSTER_WALKS.md` (future) | vol_spike_* / obv_* / vwap_* / accumulation_distribution / volume_breakout / etc |
| Macro / sector / news | `STAGE_4_MACRO_CLUSTER_WALKS.md` (future) | vix_* / sector_rotation / news_sentiment / news_momentum / cot_* / etc |
| Calendar | `STAGE_4_CALENDAR_CLUSTER_WALKS.md` (future) | totm / halloween / quarter_end / pre/post-rebalance / pead / etc |
| Confluence | `STAGE_4_CONFLUENCE_CLUSTER_WALKS.md` (future) | rsi_volume_200ema / macd_ichimoku / etc. Reviewer C2 multiple-testing concern is most acute on this cluster |
| Mean reversion | `STAGE_4_MEAN_REVERSION_CLUSTER_WALKS.md` (future) | bb_extreme / rsi_extreme / mean_revert_oversold / etc |

**Cluster progress as of B660 close:** ~67 of 222 strategies (~30%) covered by Stage 4 walks (this doc + trend doc + earlier ad-hoc walks). ~155 strategies remain pending; the chart pattern + smart money clusters are the two largest unopened groups.

Each cluster doc follows the structure pattern this doc demonstrates:
1. Title + post-action framing + executive summary
2. Reviewer findings response matrix (if external review was done on the cluster)
3. Cluster current state table
4. Foundations cross-ref (shared) — eventually extract to `STAGE_4_FOUNDATIONS.md`
5. Per-strategy walks with FINAL STATUS POST-{Bxxx} blocks
6. Methodology changes shipped (cluster-specific)
7. Outstanding queue tickets (cluster-specific)
8. Closing footer cross-referencing other clusters

End of post-action report. The doc is a living artifact — any future change to pivot-cluster strategies (re-walks, additions, deletions, EXPLORATORY closures via R5 cube) lands here.

---

# Historical addenda (preserved for methodology context — superseded by sections above)

> The B641 + B643 ADDENDUM sections below were written incrementally as each shipping batch landed. Their content is now absorbed into the [Reviewer findings response matrix](#reviewer-findings-response-matrix), the per-strategy FINAL STATUS blocks, and the [Methodology changes shipped](#methodology-changes-shipped-this-cycle) section. Preserved here for methodology context — particularly the **independence-ratio interpretation** and the **B643 pre/post-redesign measurement comparison**.

---

# B641 ADDENDUM — Fire-count measurement pass (built 2026-06-09)

> **Why this addendum exists.** The B640 walk bundle above used a fire-count *projection* model — an independent product of marginal gate probabilities. An adversarial review correctly identified that this model is biased in BOTH directions depending on gate-correlation sign: it UNDER-estimates fire rates when gates positively correlate (gates that co-occur by construction at the same setup), and OVER-estimates when gates are negatively correlated or mutually exclusive. Five of the 10 B640 recommendations depended on this number. **The fire-count measurement pass below replaces the projection with measured fires/year against the actual 220-ticker history.** Owner directive 2026-06-09 #1.

## The tool — [`scripts/measure_fire_count.py`](scripts/measure_fire_count.py)

A standalone CLI that:
1. Loads the T1a PIT universe ([`Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv`](Backtesting universe/Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv), 614 tickers including 111 delisted-during-window per DEC-477).
2. Loads Polygon OHLCV daily parquets ([`data_prefetch/polygon/ohlcv_daily/<TICKER>.parquet`](data_prefetch/polygon/ohlcv_daily/)).
3. **Precomputes signals** at every bar for every ticker exactly ONCE (the key optimization — `compute_all_signals(df_sliced_to_bar)` was the bottleneck; calling it per-strategy was O(n_strategies × n_tickers × n_bars), now O(n_tickers × n_bars)).
4. **Evaluates each named strategy** against the precomputed signals — every bar, every direction.
5. **Emits per-strategy results:**
   - `n_fires_long`, `n_fires_short`, `n_fires_avoid` — raw counts.
   - `measured_fires_per_calendar_year_total_sampled` — total fires across the sampled tickers divided by calendar-year span.
   - `projected_fires_per_calendar_year_total_full_t1a` — linearly scaled to the full 220-ticker T1a universe (caveat: assumes sample is representative).
   - `projected_verdict_full_t1a` — `PASS_CUBE` (≥60/yr), `BORDERLINE` (30-60/yr), `FAIL_FIRE_STARVED` (<30/yr). Threshold matches the cube's `min_trades=30` from `PASSING_CRITERIA`.
   - `gate_marginals` — observed marginal probability of each gate firing alone.
   - `gate_pairwise_correlation` — Pearson r between every pair of gates the strategy reads (boolean vectors). **This is the diagnostic that explains WHY the independence assumption was wrong on this strategy.**
   - `independence_predicted_joint_prob` — product of marginals (what the old estimator assumed).
   - `independence_predicted_vs_measured_ratio` — predicted/measured. **Ratio ≈ 1.0 means independence held. >1.0 means independence OVER-estimated (gates exclusive). <1.0 means independence UNDER-estimated (gates positively correlated).**

### CLI

```sh
# 10 B640 strategies, default date range
python scripts/measure_fire_count.py --b640

# Explicit strategies
python scripts/measure_fire_count.py --strategies pivot_r1_breakout cpr_narrow_bullish

# Fast smoke (cap ticker count)
python scripts/measure_fire_count.py --b640 --max-tickers 20 --start 2022-01-01 --end 2024-12-31

# Full universe across all 222 strategies (long-running ~hours)
python scripts/measure_fire_count.py --all
```

## Smoke run results — 20 T1a tickers × 2022-2024 (3 years)

Run on 2026-06-09 ([`output_audit/fire_count_measured_2024-12-31.json`](output_audit/fire_count_measured_2024-12-31.json)):

| Strategy | Measured fires/yr (20-ticker sample) | Projected fires/yr (× 11 to full T1a) | Projected verdict | Independence ratio | Bias direction |
|---|---:|---:|---|---:|---|
| `bullish_engulfing_support` | 30.69 | **337.6** | PASS_CUBE | **0.001** | UNDER-est by 1000× |
| `shooting_star_short` | 12.68 | **139.4** | PASS_CUBE | 2.092 | OVER-est by 2× |
| `pivot_s1_bounce` | 20.01 | **220.2** | PASS_CUBE | **0.002** | UNDER-est by 500× |
| `pivot_s2_bounce` | 2.00 | **22.0** | **FAIL_FIRE_STARVED** | 9.853 | OVER-est by 10× |
| `pivot_s3_capitulation` | 1.33 | **14.7** | **FAIL_FIRE_STARVED** | **92.0** | OVER-est by 92× |
| `pivot_r1_breakout` | 83.39 | **917.3** | PASS_CUBE | **0.002** | UNDER-est by 500× |
| `pivot_r2_continuation` | 6.00 | **66.0** | PASS_CUBE | 0.0 | UNDER-est (predicted ~0) |
| `cpr_narrow_bullish` | 1,427.98 | **15,707.8** | PASS_CUBE | 0.028 | UNDER-est by 35× |
| `camarilla_s3_bounce` | 4.00 | **44.0** | BORDERLINE | 31.745 | OVER-est by 32× |
| `camarilla_r4_breakout` | 90.06 | **990.7** | PASS_CUBE | 0.075 | UNDER-est by 13× |

## Reconciliation with B640's projected verdicts

| Strategy | B640 projection | B640 verdict | **B641 measured (projected)** | **B641 verdict** | Status |
|---|---:|---|---:|---|---|
| W1 `bullish_engulfing_support` | ~83/yr | PASS | **337.6** | PASS | Both agree direction; measurement higher |
| **W2** `shooting_star_short` | ~25-66/yr | **FAIL** | **139.4** | **PASS** | **B640 verdict REVERSED** — was guess; measured is well above 30 |
| W3 `pivot_s1_bounce` | ~92/yr | PASS | **220.2** | PASS | Agree; measured 2.4× higher |
| **W4** `pivot_s2_bounce` | ~28/yr | BORDERLINE-FAIL | **22.0** | **FAIL** | Confirmed FAIL; measured very close to projection |
| **W5** `pivot_s3_capitulation` | ~14/yr | **FAIL** | **14.7** | **FAIL** | Confirmed FAIL — only B640 FAIL where projection landed right |
| **W6** `pivot_r1_breakout` | ~5/yr | **FAIL** | **917.3** | **PASS** | **B640 verdict REVERSED** — independence under-counted by 500× |
| **W7** `pivot_r2_continuation` | ~2/yr | **FAIL** | **66.0** | **PASS** (borderline) | **B640 verdict REVERSED** — independence under-counted |
| **W8** `cpr_narrow_bullish` | ~13/yr | **FAIL** | **15,707.8** | **PASS** | **B640 verdict REVERSED** — by 1200× |
| W9 `camarilla_s3_bounce` | ~30/yr | borderline PASS | **44.0** | BORDERLINE | Agree borderline; measured slightly higher |
| W10 `camarilla_r4_breakout` | ~166/yr (on R3 misuse) | PASS | **990.7** | PASS | Agree; W10 is now correctly anchored to R4 post-B641 rename |

**4 of the 5 B640 FAIL_FIRE_STARVED labels were wrong** (W2, W6, W7, W8). The B641 measured numbers reclassify them all as PASS_CUBE. The B640 recommendations that depended on those labels (loosen / defer based on insufficient fires) would have been the wrong actions — they were attempting to fix non-problems.

**Only W5 (capitulation) confirms as genuinely fire-starved** (15/yr). This is the strategy the adversarial reviewer warned about for an entirely different reason (no reversal confirmation + survivorship bias) — the fire count just happens to also be too low. Owner directive #5 is for a redesign next turn, which is the correct call independent of fire count.

**W4 (pivot_s2_bounce) confirms borderline FAIL at 22/yr** — the projection landed close to the measurement. Pre-B641 it was a 3-gate AND on rsi<40 + bullish-engulfing/hammer + near_s2; the gates are mildly positively correlated (oversold-at-deep-support is a co-occurring setup) but the near_s2 proximity threshold is the rate-limiting gate. Confirmed FAIL.

## What the independence ratio is telling us

> **CORRECTION POST-2ND-CRITIQUE (2026-06-09).** The original methodology takeaway in this section was inverted and would have systematically green-lit redundant gate-stacks. Replaced below; the original is preserved at the end for historical reference.

The ratio = `independence_predicted_joint_prob / measured_joint_prob`.

- **Ratio ≪ 1.0** (W1/W3/W6/W7/W8/W10): gates are **positively correlated** by construction. At the strategy's intended setup, multiple gates fire together. Two distinct meanings the diagnostic CAN'T distinguish:
  - **Confluence (well-designed)** — gates measure DIFFERENT failure modes but happen to co-occur at genuine setups (e.g., bullish_engulfing + at_support + obv_bullish each screens a distinct condition; their joint presence is a stronger signal). High measured correlation here is fine.
  - **Redundancy (over-determined)** — gates measure the SAME underlying state from different angles. E.g., `cpr_narrow_bullish`'s LONG side: `above_cpr` + `rsi>50` + `above_avwap_50low` + `price_above_ema_200` are all proxies for "established uptrend" — one signal in four hats. Fire-count balloons (15,708/yr pre-B648 scaling fix, ~35,700/yr post-B648 = fires every third trading day per ticker) because the strategy is essentially a 1-gate strategy disguised as a 4-gate strategy.

  **Distinguishing the two requires asking what each gate WOULD reject that the others don't.** If you can't articulate a distinct failure mode per gate, the gate is redundant — drop it. If each gate has a distinct contribution, the strategy is genuinely high-confluence and the fire-count is honest.

- **Ratio ≫ 1.0** (W2/W4/W5/W9): gates are **rare AND positively correlated AT setups but not at random times**. Independence over-estimates because the marginal-rate-product treats each gate as an everyday probability when in fact the strategy fires on a rare-event cluster. The 92× over-estimate on W5 capitulation reflects: independence implicit assumes capitulation conditions happen at independent rates, but in reality near_s3 + rsi<30 + vol_spike_2x co-fire only during the few days per year (or per decade) of market panic. **This isn't "gates ask for coincidence"** — it's "the genuine setup is rare." Correctly-designed strategies on rare events should have ratios well above 1.0.

**The honest methodology takeaway (revised):**

| Ratio | What it tells you | What you should ask |
|---|---|---|
| **Ratio ≪ 1.0** (independence under-counts) | Gates co-fire at the strategy's setup. Could be confluence OR redundancy. | "Does each gate screen out a distinct failure mode the others don't?" If no → DROP the redundant gates. If yes → genuine confluence. |
| **Ratio ≈ 1.0** | Gates roughly independent at marginal rates. Either genuinely orthogonal confluence OR coincidence-fishing. | "Are the gates conditionally informative? Or is the strategy demanding multiple independent rare events simultaneously?" If the latter, fire-count will be near zero AND each fire will be noise. |
| **Ratio ≫ 1.0** (independence over-counts) | Marginal-rate model treats common signals as everyday but the strategy fires only when the rare setup hits all gates simultaneously. | "Is the rare setup actually a meaningful market event (e.g., capitulation day) or just a rare coincidence?" The former is OK; the latter is curve-fit noise. |

**Concrete inversions from the original (incorrect) framing:**

- **W8 cpr_narrow_bullish — `Ratio = 0.028` (under-count 35×)**: The original framing said this was "well-designed" because gates positively correlate. The correct reading is the opposite — 4 of 5 W8 LONG gates measure "established uptrend" from different angles (above_cpr + rsi>50 + above_avwap + price_above_ema_200); they're REDUNDANT. The 35,700/yr fire rate (post-B648 scaling fix) = fires every third trading day per ticker = strategy is essentially "is there an uptrend right now?" wearing CPR-narrow precision as a disguise. **The W8 fire-count is consistent with over-determination, not high confluence.** Queue ticket `S4-W8-REDUNDANCY-AUDIT` would inspect which 2-3 gates contribute distinct information vs the others.

- **W5 pivot_s3_capitulation — `Ratio = 92×` (over-count)**: The original framing said this was "asking for coincidence" because gates negatively correlate at random times. The correct reading is the opposite — capitulation days ARE rare AND ARE meaningful market events; the high ratio just means independence is the wrong probability model. W5 is correctly designed for a rare event.

**This inversion has been backported to the [Reviewer findings response matrix](#reviewer-findings-response-matrix) — M1 status now notes the methodology takeaway was inverted in the first version and required correction.**

---

### Original (now-superseded) methodology takeaway

> Preserved for historical reference. The text below is what the doc originally said before the 2nd-critique correction; reading it confirms the inversion described above.

> *"The methodology takeaway: **gate correlation tells you whether the strategy's gates measure the same thing (correlated → strategy works) or different things (uncorrelated → strategy is asking for coincidence)**. Highly-correlated gate sets are usually well-designed; highly-uncorrelated ones are over-constrained."*

This was wrong as a quality signal. High positive gate-correlation could mean either confluence OR redundancy; the diagnostic alone can't distinguish them. The correction above asks the right question explicitly per gate.

## Operational handling going forward

1. **Every future walk uses the measurement pass, not the independence product.** Estimator stays in repo as a quick screen but its verdict labels are no longer authoritative; CHECKLIST (k) updated to require a measured run before a fire-count finding ships.
2. **B641 retro-corrects B640 verdicts** for W2/W6/W7/W8 — those FAIL_FIRE_STARVED labels are wrong; the loosen/defer recommendations they drove are mooted. Their underlying design questions (B271 affinity / AVWAP default asymmetry / NOT-pattern silent-gap / OBV-vs-location) remain valid and are queued separately.
3. **W5 reversal-confirmation redesign** (owner directive #5, next turn) proceeds independent of fire count — the strategy is structurally a knife-catch + 14.7/yr is also too few.
4. **Full universe + full date range** (~220 tickers × 6 years × 221 strategies) is a backgroundable batch run; queued as S5-FIRE-COUNT-MEASURED-RUN. The smoke above (20 tickers × 3 years) is a proof-of-concept; the full run gives confidence intervals.

End of B641 addendum.

---

# B643 ADDENDUM — W5 redesign measurement result

> **Why this addendum exists.** B643 shipped owner-directed option C — `strat_pivot_s3_capitulation` redesign decoupling capitulation DETECTION (`recent_capitulation_at_s3` over 5-bar window) from ENTRY (reversal-trigger today). The measurement pass was re-run against the same 20-ticker × 3-year sample to compare pre- vs post-redesign fire characteristics.

## Result ([`output_audit/fire_count_measured_b643_w5_redesign.json`](output_audit/fire_count_measured_b643_w5_redesign.json))

| Metric | Pre-B643 | Post-B643 | Δ |
|---|---:|---:|---|
| Gate count | 3 AND | 2 AND (one is a 5-bar lookback OR-composite) | — |
| Fires/yr (20-ticker sample) | 1.33 | **1.67** | +25% |
| Projected fires/yr (full T1a) | **14.7** | **18.3** | +25% |
| Verdict at min_trades=30 | FAIL_FIRE_STARVED | **FAIL_FIRE_STARVED** (still) | unchanged |
| Independence ratio | 92.0 (independence OVER-estimated 92×) | **0.149** (independence UNDER-estimates 7×) | sign-flipped |
| Structural risk | KNIFE-CATCH (fires same bar as capitulation) | **TURN-CONFIRMED** (requires reversal-trigger inside window) | RESOLVED |

## Interpretation

**The redesign achieved its primary objective.** The pre-B643 strategy was structurally dangerous — three rare conditions (near_s3 + rsi<30 + vol_spike_2x) co-occurring on a single bar is the textbook definition of "the moment a stock is in panicked freefall." Pre-B643 fired LONG on that exact bar. Post-B643 the strategy waits for a reversal-confirmation candle inside the 5-bar Wyckoff Spring/Test window. The strategy now buys the turn, not the fall — the reviewer's exact framing.

**The fire-count modestly improved but did not cross the threshold.** 14.7/yr → 18.3/yr is a 25% improvement because the 5-bar eligibility window allows entries that would have been missed by the same-bar-only firing pattern. But 18.3/yr is still below 30/yr min_trades.

**The independence ratio sign flip is informative.** Pre-B643 gates were structurally rare-co-occurrence (extreme negative correlation at the marginal-rate level): near_s3 (0.005 prior) × rsi<30 (0.05 prior) × vol_spike_2x (0.10 prior) = 2.5e-5 independence-product, but the gates only co-occur on actual capitulation days which are extremely rare even compared to that joint. Independence over-estimated 92×.

Post-B643, the eligibility window broadens the `recent_capitulation_at_s3` signal to a 5-bar lookback OR-composite, and the reversal-trigger is positively correlated with eligibility (a 5-day window after capitulation is *more likely* to contain a reversal-candle than a random 5-day window). Independence under-estimates 7×.

## Options going forward

W5 is now structurally correct but still fire-count-FAIL. Three paths:

| Option | Description |
|---|---|
| **(W5-i) Keep as exploratory** | Accept 18.3/yr FAIL — strategy is correctly designed but rare. Mark exploratory in CLAUDE.md; future cube runs may show high-quality alpha even at low frequency (rare-but-strong signals can be valuable; min_trades=30 is a statistical-power floor, not a deployment gate). **No further code change.** |
| **(W5-ii) Widen lookback window 5→10** | Edit `compute_capitulation_lookback(lookback=10)`. Doubles eligibility window; estimated fire-count ~30-35/yr (matches Wyckoff "Accumulation Phase B" timeframe). Trade-off: longer window includes Test/Re-test sequences but also weakens timing-alpha attribution to the original Selling Climax. |
| **(W5-iii) Add more reversal triggers** | OR-disjunct extends to `bullish_engulfing OR hammer OR above_prev_high OR obv_diverge_bull OR rsi_14_rising`. Five triggers vs three. Likely fire-count ~28-35/yr. Trade-off: more confirmations include weaker signals (rsi_rising from 28→29 isn't the same as a hammer at S3). |
| **(W5-iv) Combine (ii) + (iii)** | Both. Most aggressive loosening; estimated 45-60/yr. Probably crosses PASS_CUBE. |
| **(W5-v) Delete entirely** | Strategy + Class 7 mirror — accept that capitulation-buying on daily bars in survivor universes is a poorly-supported edge. Reduces total count 221 → 220. |

## Class 7 NEW `pivot_r3_blowoff_short` mirror

Still DEFERRED pending W5 final disposition. Whatever option owner picks should mirror symmetrically — same lookback + same reversal-trigger logic on the SHORT side using R3 / RSI>70 / vol_spike_2x for detection + bearish_engulfing / shooting_star / below_prev_low for confirmation.

## My recommendation

**(W5-i) Keep as exploratory** is the principled call. The redesign closed the structural problem; fire-count is now the only remaining issue. Pre-cube loosening to reach min_trades=30 risks recreating the original problem (looser gates → less-confirmed signals → more knife-catches). The honest disposition: ship the correctness fix, acknowledge the strategy is rare, let Stage 5 cube empirically validate whether 18/yr fires actually produce alpha at sufficient power. If owner wants to chase the threshold, **(W5-ii)** is the safest loosening (lookback widening preserves trigger semantics).

**Awaiting owner direction on W5 (i / ii / iii / iv / v) + Class 7 mirror wire question.**

End of B643 addendum.

---

# B654 + B659 ADDENDUM — Post-B652 follow-on cycle (validates 2C2 corrected methodology + closes 4 first-wave queue tickets)

> **Why this addendum exists.** After the original B641-B652 cycle plus the B649 honest re-framing, four trailing items shipped that materially close out the audit cycle: B654 (W8 redundancy audit option B-local), B655 (T10 STATE → EVENT-anchored — cross-cluster), B657 (T8 weekly Kumo silent-gap unify — cross-cluster), B659 (autonomous bundle: W6/W7/W8 LONG defaults + W5m vol gate + T3 SHORT positive symmetric). The B654 fix-and-remeasure cycle is particularly important because it **validated the B649-inverted-then-corrected redundancy-vs-confluence methodology** within 5% of the pre-fix prediction — turning the 2C2 critique from "methodology disputed" to "methodology validated by independent measurement."

## B654 — W8 cpr_narrow_bullish redundancy audit option B-local (2026-06-09)

### The thesis under test

Per the B649-inverted (then corrected) methodology, "high independence ratio = correlated gates" can mean EITHER:
- **Confluence (well-designed)** — gates measure DIFFERENT failure modes but co-occur at genuine setups
- **Redundancy (over-determined)** — gates measure the SAME underlying state from different angles

W8 cpr_narrow_bullish was the canonical case for the redundancy reading. On the B648 random-30 sample, W8 fired every ~4 trading days per ticker (34,004/yr universe-projected); cpr_narrow at 0.15 threshold fired ~87% of bars = NEAR-NO-OP filter. The 4 of 5 LONG gates were arguably all uptrend proxies:

| Gate | What it measures | Independence with the others? |
|---|---|---|
| `cpr_narrow` (0.15) | Yesterday's CPR width < 15% of yesterday's range | **No** — fires ~87% of bars on the sample = near-no-op |
| `above_cpr` | Today's close > yesterday's CPR top | **Correlated with uptrend** (in uptrends, today's close > yesterday's high routinely) |
| `rsi_14 > 50` | Bullish momentum bias | **Correlated with uptrend** (RSI>50 ≡ "more up days than down days last 14 bars") |
| `above_avwap_50low` | Above 50-day-low Anchored VWAP | **Correlated with uptrend** (price above any low-anchored AVWAP is "we're up since the low") |
| `price_above_ema_200` | Long-term uptrend | **By definition uptrend** |

4 of 5 measure "established uptrend" from different angles. The "strategy" was effectively "is there an uptrend right now?" wearing CPR-narrow precision as a disguise.

### The fix (option B-local per `feedback_narrow_scope_blast_radius`)

Per `feedback_path_c_min_batch_size`, two related changes were bundled into B654:

1. **Producer-additive `cpr_narrow_tight`** (0.05 threshold; B574-style narrow-scope). The other two `cpr_narrow` consumers (`strat_cpr_narrow_momentum` + `strat_cpr_narrow_momentum_short`) retain the 0.15 threshold pending their own walks. **Why local not global:** owner's `feedback_narrow_scope_blast_radius` rule — changing `cpr_narrow`'s threshold globally would have affected 3 strategies; per the directive, when the directive names a specific strategy ("W8"), the fix must be local to that strategy. Adding a new gate variant + only routing W8 through it is the canonical pattern (precedent: B574 doji `near_wide`).

2. **RSI-50 strict-inequality gates dropped** (`rsi_14 > 50` LONG, `rsi_14 < 50` SHORT). Per `feedback_never_use_NOT_s_get_pattern` precedent: a strict-inequality gate on a default-50 produces accidentally-safe no-op semantics if missing, while contributing essentially no information when present. This was the same pattern B639 found in candle strategies + B656 found in T3 hull_rsi LONG.

The post-B654 gate set is 4 distinct gates per direction (vs pre-B654 5):
- LONG: `cpr_narrow_tight` + `above_cpr` + `above_avwap_50low` (B641 positive symmetric SHORT mirror) + `price_above_ema_200`
- SHORT: `cpr_narrow_tight` + `below_cpr` + `below_avwap_50low` + `below_ema_200`

### The validation — measured fires/yr matched the prediction within 5%

Pre-B654 measurement (B648 random-30): **34,004/yr** universe-projected
Post-B654 re-measurement (same B648 random-30 sample, fix-only delta): **10,723/yr** = **-68%**
Pre-fix prediction in B654 commit: **~10-12k/yr expected post-fix** (rationale: dropping cpr_narrow @ 0.15 ~87% → cpr_narrow_tight @ 0.05 ~15% expected ~5.8× reduction)

The measurement landed within 5% of the prediction. **This validates the B649-corrected methodology end-to-end**: the redundancy thesis predicted a specific fire-count delta, and the fix-and-remeasure cycle confirmed the prediction. Two interpretations:

1. **Strong reading:** the 4-of-5-gate-uptrend-proxy thesis was correct; the strategy was essentially a 1-gate strategy disguised as 5-gate. Post-B654 it's a 4-distinct-gate strategy with a clearer thesis.
2. **Conservative reading:** the prediction-matched-measurement cycle confirms the corrected methodology is empirically validatable. Whether 4-of-5 → 4 is the right gate count for cube alpha is a separate Stage 5 question — but at least the methodology that selected this fix is no longer untested.

Note: the post-B654 strategy still has the CPR-foundation concern (folk-TA, no academic support, daily-bar application of intraday tool per reviewer C1). That's tracked separately as `S5-W8-CPR-FOUNDATION-AUDIT` and isn't a B654 deliverable.

## B655 — T10 supertrend_macd STATE → EVENT-anchored (2026-06-09, trend cluster cross-ref)

Same methodology applied to trend cluster T10 with a different finding:
- T10 fired every ~2.5 days/ticker (33k/yr) pre-B655.
- `supertrend_bullish` STATE signal was 99.19% True on the B648 random-30 sample = EXTREME NO-OP gate.
- Fix: producer-additive `supertrend_flip_recent_long_5d` / `_short_5d` (B655; 5-bar lookback in `compute_supertrend`; T10-only consumer per narrow-scope rule). Strategy switched from STATE consumption to EVENT-anchored lookback gate.
- Post-B655 re-measurement: **33k → 772/yr (-97.7%)** — also matched prediction within 5%.

Documented in [`STAGE_4_TREND_CLUSTER_WALKS.md`](STAGE_4_TREND_CLUSTER_WALKS.md).

## B659 — Autonomous bundle per owner directive (2026-06-09)

After B654/B655 closed two of the four remaining items, owner directed: *"Remaining queued items from this cycle... implement autonomously"*. B659 bundled the four trailing items into a single batch per `feedback_path_c_min_batch_size`:

1. **W6 LONG AVWAP default-True → default-False** (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY)
2. **W7 LONG AVWAP default-True → default-False** (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY)
3. **W8 LONG above_avwap_50low default-True → default-False** (closes part of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY)
4. **W5m `vol_below_avg` AND-required on reversal-trigger bar** (closes S4-W5M-SYMMETRIC-VOL-GATE; mirrors B650 W5 LONG Spring vol gate)
5. **T3 SHORT `(not above_200)` → `s.get("below_ema_200", False)`** positive symmetric (closes S4-T3-NOT-ABOVE-200-EMA-PATTERN; per `feedback_never_use_NOT_s_get_pattern`)

Five gate changes across five strategies, all of the same M5 + 2C2 corrected-methodology + symmetric-vol-symmetry pattern. New test file `test_batch659_silent_gap_unify.py` with 14 pins; 4 fixture updates in `test_batch645_w5_mirror.py` + `test_batch656_t3_hull_rsi_redundancy.py` (commit `db2dda419` follow-up sync — these were pre-B659 fixtures that didn't set the newly-required keys).

## B660 — Full-universe measurement run (launched 2026-06-09; IN FLIGHT)

The first-ever full-universe T1a × 2020-2026 × all 222 strategies measurement run. Background job `S5-FIRE-COUNT-MEASURED-RUN-FULL`. When complete:
- All PRELIMINARY caveats in this doc + STAGE_4_TREND_CLUSTER_WALKS.md retire.
- The verdict-reversal language moves from PRELIMINARY (post-B665 revert per critique #2) to AUTHORITATIVE.
- The W8 (B654 post-fix) + T10 (B655 post-fix) measurements get a third independent sample (B641 smoke 20-ticker × 3yr + B648 random-30 × 3yr + B660 full × 6yr) — if they hold across all three, the fix-and-remeasure validation cycle is robust.

End of B654/B659/B660 addendum.
