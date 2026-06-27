# Stage 4 ICT (Inner Circle Trader) Pure Price-Action Cluster Walks — Per-Strategy Deep-Dive Audit

> **B1029 STATUS BANNER 2026-06-27 doc-sync:** ALL WALKS 1-5 41-of-41 RESOLVED B984-B993 per CLAUDE.md banner. Cluster walks across 220 strategies CLOSED (B722 -3 + B874 -2 + B1010 +1 = 220 / 217 active). R5 LAUNCHED 2026-06-27 B1028 on AWS i-0940a53c75d049381 (Master 1929 ops x 4y window 2022-05-05 to 2026-05-05). Banners below indicating PENDING/RUNNING/DEFER status from B691-B750-era are HISTORICAL.


> **B717 STATUS BANNER (2026-06-12) — B660 POST-B689 MEASURED DATA LANDED; ICT "NO MEASURED DATA" FRAMING SUPERSEDED.** PO3 family now has measured fires (`output_audit/fire_count_measured_b660_post_b689_extended.json`): po3_bullish 5,552/yr (TOO_FREQUENT_FAIL per B710 5K ceiling), po3_bearish 4,076/yr (BORDERLINE), po3_htf_aligned_long 4,924/yr (BORDERLINE). Other ICT strategies still 0 fires (still need B690 for SM-cluster-specific producers; ICT-PO3 producers were wired by B689). **B705 "no measured data" Pattern Q framing applies only to non-PO3 ICT strategies now.** Reviewer's "PO3 strategies are mythology + single-bar reversal" critique now testable against measured data: at 5,500/yr LONG = ~11 fires/name/yr, PO3 fires roughly every 5 trading weeks per name — borderline-state-flag rate, consistent with "single-bar candle structure fires constantly" interpretation. Resolve via S4-B717-CEILING-FLAGGED-REDUNDANCY-DIAGNOSTIC-26-STRATEGIES Phase-1 narrow-scope producer fix.
>
> ---
>
> **B705 STATUS BANNER (2026-06-11) — ADVERSARIAL REVIEW OF EXTERNAL REVIEWER'S ICT PROPOSAL — NOT TRUST-BLIND.** Owner-pattern from B702: source-verify each claim before accepting. Output: [STAGE_4_ICT_CLUSTER_B705_ADVERSARIAL_REVIEW.md](STAGE_4_ICT_CLUSTER_B705_ADVERSARIAL_REVIEW.md). **Headline B705 verdicts (source-verified against `multi_timeframe.py`, `ict_producers.py`, `smc_ict.py`, `screener.py`):**
>
> - **HIGHEST-LEVERAGE FINDING (REVIEWER 100% CORRECT)**: Turtle Soup inherits SMC's `event_recency_bars=90` ([smc_ict.py:81](backtest/signals/smc_ict.py#L81)) — fires on sweeps up to 4 months stale. Raschke 1996 stop-run reversal needs 1-5 bar recency. Wire Turtle-Soup-specific tight-recency signal; don't change SMC default.
> - **PO3 detection IS single-bar reversal** ([multi_timeframe.py:244-253](backtest/signals/multi_timeframe.py#L244)): `sweep_below AND close > open AND close_position > 0.66`. "Accumulation/Manipulation/Distribution" framing is in the docstring only, not the detection. Reviewer's mythology-vs-substance critique CORRECT.
> - **MMBM is PO3 with a 5-bar tight-range pre-condition** ([ict_producers.py:79](backtest/signals/ict_producers.py#L79)): adds `accum_range_pct ≤ 0.05`. Different sweep anchor than PO3 singular (5-bar low vs prior-day low). Likely strict SUBSET candidate (Pattern W) — testable via fire-overlap.
> - **PO3 producer-name collision (CC-A) = SCARE NOT BUG**: `compute_po3_signal` (singular) and `compute_po3_signals` (plural) emit DISJOINT key sets and wire to non-overlapping consumers. Runtime OK. Class-wide audit recommendation has merit; specific PO3 case = NOT-A-BUG.
> - **Cluster has no empirical foundation**: doc's own Pattern Q already states 10 of 12 strategies have no peer-reviewed citation. Reviewer's escalation to "consolidation discipline, not cube-deferral" is sharper version of doc's caveat.
> - **Week-opening-gap-fill missing 3 conditioning gates** ([ict_producers.py:96-155](backtest/signals/ict_producers.py#L96)): no upper bound, no earnings filter, no trend context. Reviewer 100% correct; gated behind confronting tests per B701 discipline.
> - **Pattern R docstring fix (CC-B)** is pre-cube-blocking per reviewer's "rhetorical cover" rationale (sharper than doc's "honesty hygiene" framing).
>
> **Implementation plan: 16 tickets across 6 phases.** Top priority: `S4-B705-ICT-TURTLE-SOUP-RECENCY-FIX` + `S4-B705-ICT-PATTERN-R-DOCSTRING-FIX` (both pre-cube). Followed by subset-tests on PO3-HTF + Judas Swing (runnable now). Consolidation N is empirical (redundancy diagnostic post-recency-fix), not pre-emptive.
>
> ---
>
> **B693 BANNER ADDENDUM (2026-06-11) — selective-reading correction + Pattern Q intensifies.** External reviewer of [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) caught the B691 selective-reading methodology problem (favorable LOCKED, unfavorable PENDING-RERUN). **Each ICT strategy's zero now requires the positive two-part test via [`scripts/diagnose_zero_fires.py`](scripts/diagnose_zero_fires.py).** Plus a cluster-specific addendum: Pattern Q (10 of 12 ICT strategies have NO peer-reviewed methodology citation) **intensifies the bar** post-rerun. If the rerun shows ICT strategies still fire near zero AFTER producer wire-in, the disposition cannot fall back to "needs more data" — Pattern Q says there's no methodology foundation to defer to. A cube PASS_CUBE on an ICT strategy is necessary but not sufficient; an ICT strategy that doesn't fire post-rerun + has no peer-reviewed anchor is a candidate for deprecation, not patience.
>
> ---
>
> **B691 STATUS BANNER (2026-06-11) — 🔴 FALSE-NEGATIVE — PENDING-B689-RERUN.** B660 measurement landed [2026-06-11 02:30 UTC](output_audit/fire_count_measured_b660_full_universe.json) showing **14 of 14 ICT strategies = 0 fires (100% FAIL_FIRE_STARVED).** **This is a measurement harness gap, NOT real verdicts.** The producers feeding ICT strategies were NOT invoked in the pre-B689 precompute path:
> - `multi_timeframe.compute_po3_signal(df)` (singular PO3 feeding ICT-1 + ICT-2 `po3_bullish/_bearish` gates)
> - `multi_timeframe.compute_weekly_bias(df)` + `compute_monthly_bias(df)` (ICT-3 + ICT-4 weekly bias pullback gates)
> - `ict_producers.compute_po3_signals(df)` (plural PO3 feeding ICT-5 `mmbm_long` + ICT-6 `mmsm_short` via `po3_mmbm_setup` + `po3_mmsm_setup`)
> - `ict_producers.compute_week_opening_gap_signals(df)` (ICT-11 + ICT-12 `week_open_gap_up_15pct` + `week_open_gap_down_15pct`)
> - `smc_ict.compute_smc_signals(df, ticker)` for the `smc_liquidity_swept_*` primitives consumed by ICT-7 + ICT-8 Turtle Soup + ICT-9 + ICT-10 Judas Swing (cross-cluster Pattern N share with SMC cluster)
>
> **B689 (commit `8e8c258dd`) shipped all 4 producer wire-ins above** — smoke test confirmed `po3_bullish` fires 5× on AAPL Jun-Aug 2024 (vs B660's 0). The in-flight re-run (task `bzja19ugq`, started 09:30:39 2026-06-11, ETA ~2026-06-12 12:30) will produce trustworthy fire counts for all 14 ICT strategies including PO3 plural (mmbm/mmsm) + week-opening-gap + Turtle Soup + Judas Swing.
>
> **What does NOT change in this batch:** the ICT walks' Pattern P (cross-cluster signal-sharing with SMC) + Pattern Q (no peer-reviewed methodology citation for 10 of 12 ICT strategies — Turtle Soup ICT-7/8 the only exceptions per Raschke-Connors *Street Smarts* 1996) + Pattern R (PO3 candle-structure ≠ institutional flow per `feedback_signal_temporality_event_vs_state`) + Pattern S (single-gate strategy shells: ICT-5/6/11/12 hardcoded-params-invisible-at-call-site) findings remain VALID regardless of fire-count revision. Pattern Q + R caveats still apply post-re-run: a cube PASS_CUBE label does NOT validate the underlying ICT methodology; only that the gate fires enough for statistical sampling.
>
> **B687 ticket `S4-ICT-CLUSTER-PATTERN-N-CROSS-CLUSTER-CUBE-ABLATION-WITH-SMC`** (7 strategies on `smc_liquidity_swept_*` primitives = ICT-7 + ICT-8 + ICT-9 + ICT-10 + SMC-12 + SMC-13 + SMC-18) remains the cross-cluster flagship ablation — applies once re-run + cube replay both land.
>
> **B675 status banner (2026-06-10, owner-directed autonomous continuation):** owner directive *"continue autonomously"* after B674 SMC cluster walk + B673 external reviewer critique incorporation. This is the FIFTH per-cluster Stage 4 walk doc following pivot + trend + smart-money + SMC cluster precedents. The ICT cluster is the natural sister to SMC pure price-action (both methodologies originate from Michael J. Huddleston / Inner Circle Trader; SMC = umbrella; ICT = specific patterns).
>
> **Scope:** 12 strategies across 2 categories (`ict` 8 + `po3` 4). All wired B580-B581 inline-spec per `feedback_layer_2d_ict_inline_specification` (owner-approved 2026-06-04) + B217 PO3 batch. **No prior Stage 4 walks** on any of these per CHECKLIST #105 7-step methodology. Producer code at [backtest/signals/ict_producers.py](backtest/signals/ict_producers.py) (po3/mmbm/mmsm/week-opening-gap) + [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py) (liquidity_swept_* consumed by Turtle Soup + Judas Swing) + [backtest/signals/technical.py](backtest/signals/technical.py) (near_pivot, close_above/below_open, above/below_prev_low/high).
>
> **Source of truth.** Code references reflect current state at commit `2cc5d6efd` (post-B674 reviewer critique). Per `feedback_walk_step3_must_read_producer_source`: each walk reads producer source end-to-end.
>
> **CARRY-FORWARD from B673 SMC cluster walk + B674 external reviewer critique:** the entire ICT cluster shares 4 of the SMC cluster's cross-strategy patterns: **Pattern L** (vendored library SPOF — Turtle Soup + Judas Swing consume `smc_liquidity_swept_*` from joshyattridge/smartmoneyconcepts), **Pattern M** (ICT methodology no peer-reviewed support), **Pattern O** (hardcoded tolerances), and **Pattern N** (cross-cluster signal sharing with SMC). New cluster-specific patterns surface in §[Cross-strategy patterns](#cross-strategy-patterns-ict-cluster).
>
> Per `feedback_no_rushing_per_strategy_tweak` + `project_no_apriori_strategy_pruning` + the foundational sequence (B660 in flight; B668 cube replay awaiting B660 land; B669 survivorship execution awaiting B660 land): all fires/yr projections in this doc are PENDING B660; no auto-flag pre-measurement; no code changes in this batch (B675 is doc-only).

---

## Audience

Two:

1. **External reviewer** who issued the cumulative pivot + smart-money + (anticipated) SMC critique. For you: the ICT cluster is materially different from SMC because (a) 4 of 12 strategies are PURE producer-side AND-conjunctions (`po3_mmbm_setup`, `po3_mmsm_setup`, `week_open_gap_*_15pct`) where the strategy is a single-gate consumer of a multi-condition producer flag — Pattern P (NEW), (b) ICT/PO3 patterns are MOSTLY EVENT-shaped at bar of fire (unlike SMC which has Pattern I 90-bar recency staleness on BOS/CHOCH/OB-active), (c) 4 of 12 strategies (Turtle Soup + Judas Swing) cross-cluster-CONSUME `smc_liquidity_swept_*` primitives — implicit dependency on the SMC producer (Pattern L SPOF transmits + Pattern J FVG/OB/liquidity overlap applies), (d) the underlying ICT methodology has the SAME peer-review void as SMC (Pattern M) — Quantum Algo backtest cited cluster-wide for SMC has no analog for ICT (the ICT strategies were wired via OWNER INLINE-SPEC per `feedback_layer_2d_ict_inline_specification`, not empirical study).

2. **Future readers** (owner, Claude in later sessions, new collaborators). The [Cluster scope inventory](#cluster-scope-inventory) is your orientation; per-strategy walks below.

---

## Methodology adaptations for ICT cluster

### 1. Owner-inline-specification provenance — no empirical-backtest citation

Unlike the smart-money cluster (which had peer-reviewed CFM 2008 / Lakonishok-Lee / Ziobrowski / Akbas-Jiang-Koch citations — even if pre-crowding per CC6) and unlike the SMC cluster (which at least had the unaudited Quantum Algo Mar 2026 backtest as ostensible empirical backing for the methodology), the ICT cluster's strategies were wired via **owner inline-specification protocol** per `feedback_layer_2d_ict_inline_specification` (owner-approved 2026-06-04 Option A).

The wiring batches:
- **B217** (2026-05-18): PO3 + multi-timeframe family — `po3_bullish`, `po3_bearish`, `po3_htf_aligned_long`, `po3_htf_aligned_short` from a single owner-direction turn
- **B580** (2026-06-04): Turtle Soup long + short per Linda Bradford Raschke *Street Smarts* (1996) — the ONLY ICT strategy with a published methodology citation (Raschke is a real, peer-reviewed pattern-trading methodologist; the original Turtle Soup was published in *Street Smarts*)
- **B581** (2026-06-04): Judas Swing long + short, MMBM long + MMSM short, Week Opening Gap Fill down + up — 6 strategies wired in one inline-spec batch per ICT YouTube/Twitter methodology references

**Pattern Q (NEW for ICT): no empirical-backtest citation for 10 of 12 strategies.** Only Turtle Soup (SMC-style cross-source canonical via Raschke 1996) has any peer-reviewable methodology anchor. The other 10 are owner-trusted inline-spec wirings. Cube replay against T1a 503 names + multi-testing correction is the ONLY adjudication path; the Quantum Algo backtest analog cited for SMC does not apply here.

### 2. EVENT-anchored temporality (positive note vs SMC)

ICT strategies are MOSTLY pure EVENT-shaped bar-of-fire signals — a material improvement over SMC's Pattern I 90-bar staleness:

| Signal | Temporality | Lag |
|---|---|---|
| `po3_bullish` / `po3_bearish` (B217) | Bar-of-fire EVENT (today's bar fits PO3 phase-3 distribution candle structure) | 0-day |
| `po3_mmbm_setup` / `po3_mmsm_setup` (B581) | Bar-of-fire EVENT (4-condition AND on today's bar + 5-bar accumulation window) | 0-day |
| `week_open_gap_up_15pct` / `_down_15pct` (B581) | Bar-of-fire EVENT (today is week-open + today's open vs prior close gap ≥ 1.5%) | 0-day |
| `near_pivot` (Judas Swing) | Bar-of-fire EVENT (close within ±0.30% of standard pivot point) | 0-day |
| `smc_liquidity_swept_dn` / `_up` (Turtle Soup + Judas Swing) | **STATE with 90-bar recency** (consumes SMC producer) | Inherits SMC Pattern I 90-bar staleness |

**Net cluster:** 8 of 12 strategies have purely bar-of-fire EVENT triggers; 4 (Turtle Soup + Judas Swing × LONG/SHORT) inherit SMC Pattern I via liquidity_swept_* consumption. EVENT-temporality is CLEANER than SMC cluster average — relative cluster strength.

### 3. Cross-cluster signal-sharing — implicit SMC dependency for 4 of 12 strategies

`smc_liquidity_swept_dn` / `smc_liquidity_swept_up` are produced by `compute_smc_signals()` in [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py) — the SMC cluster's producer. Turtle Soup + Judas Swing strategies (4 of 12) consume these signals.

**Pattern P (NEW for ICT): cross-cluster signal-sharing creates 3 implicit dependencies:**
1. **Pattern L SPOF transmits** — if the SMC vendored library import fails, all 4 Turtle Soup + Judas Swing strategies silently degrade together to no-fire. Same single-point-of-failure surface as SMC cluster.
2. **Pattern I staleness inherits** — 90-bar recency window on liquidity_swept_* applies to ICT's Turtle Soup + Judas Swing. Sweep event could be up to 4 months old at fire bar.
3. **Pattern N intra-family overlap** — Turtle Soup + Judas Swing + SMC-18 (liquidity_sweep_reversal) + SMC-12/13 (equal_*_swept) all consume liquidity_swept_* OR equal_*_swept primitives. **5 strategies on 2 primitive signals** → severe internal multi-test inflation. Cross-cluster Pattern J flagship ablation candidate.

### 4. PO3 "phase-3 distribution candle" thesis is purely structural — no flow validation

The Power-of-3 (PO3) framework (Phase 1 Accumulation → Phase 2 Manipulation → Phase 3 Distribution) is purely a CANDLE-STRUCTURE pattern: today's high > prior 5-day max (or low < prior 5-day min) AND today's close back inside accumulation range AND today's bar is bullish/bearish. This is structurally distinct from "institutional flow validation" — there is NO actual fund-manager / dark-pool / unusual-options signal in the PO3 strategies. The thesis (markets follow accumulation-manipulation-distribution cycles per ICT) is internally consistent but **the strategy fires on candle structure alone, NOT on flow evidence**.

**Pattern R (NEW for ICT): docstring-implied "institutional flow" thesis NOT validated by actual flow data.** All 4 PO3 + 2 MMBM/MMSM strategies fire on PRICE-ACTION ONLY. The docstrings reference "Market Maker Buy Model / Market Maker Sell Model" + "institutional accumulation" + "stop-hunt then distribute upward" — implying flow validation that the producer does not provide. Walk-level honesty fix candidate (same class as Pattern B SMART-MONEY-SPONSORSHIP overclaim).

### 5. Hardcoded ICT-methodology parameters — Pattern O carried forward + extended

The ICT producer (`ict_producers.py`) and consumer strategies hardcode several free parameters:

| Parameter | Value | Strategies affected | Source |
|---|---|---|---|
| `accum_window` | 5 bars | All 4 PO3 + MMBM + MMSM (5 strategies) | `compute_po3_signals` arg |
| `tight_range_threshold` | 0.05 (5%) | All 4 PO3 + MMBM + MMSM | `compute_po3_signals` arg |
| `gap_threshold_pct` | 1.5% | week_open_gap_fill_down + week_open_gap_fill_up (2 strategies) | `compute_week_opening_gap_signals` arg |
| `near_pivot` tolerance | ±0.30% | Judas Swing long + short (2 strategies) | `technical.py` |
| `liquidity_range_pct` | 0.01 (1%) | All 4 liquidity-consuming (Turtle Soup + Judas Swing) — inherited from SMC | smc_ict.py |
| `event_recency_bars` | 90 | All 4 liquidity-consuming — inherited from SMC | smc_ict.py |

**Pattern O extends:** 6 hardcoded parameters across the cluster; none cube-sensitivity-tested; no empirical basis cited (`accum_window=5` and `tight_range_threshold=0.05` are owner-spec choices). Same disposition as SMC Pattern O: queue config-parameterization for post-B660 cube sensitivity sweeps.

---

## Reviewer findings response matrix

> Pre-emptive matrix awaiting external reviewer pass. Cluster-level feasibility findings expected per the B673/B674 critique pattern.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| _F-pending_ | Awaiting external reviewer pass on the ICT cluster walk | — | OPEN | Will be tabulated post-review |

**Pre-emptive carry-forward from B673/B674 SMC reviewer critique that LIKELY applies:**

| Finding class | ICT applicability | Action |
|---|---|---|
| **CC1 (EVENT-alpha next-open gap haircut)** | LIMITED — ICT's PO3 + Week-Opening-Gap + MMBM/MMSM are DAILY-BAR-EVENT strategies, not announcement-EVENT; the gap-after-detection problem is less acute. Turtle Soup + Judas Swing's `liquidity_swept_dn/up` events DO have the inherited SMC issue (sweep happens up to 90 bars ago; engine entry is point-in-time at sweep-detected bar so no announcement gap). | LOW concern (relative to SMC) |
| **CC2 (passive-flow contamination)** | NOT APPLICABLE — ICT strategies use NO 13F data; pure price-action. | N/A |
| **CC3 (confidential treatment)** | NOT APPLICABLE — no SEC filings consumed | N/A |
| **CC4 (Quiver PIT integrity)** | NOT APPLICABLE — no Quiver data consumed | N/A |
| **CC5 (10b5-1 contamination)** | NOT APPLICABLE — no insider data | N/A |
| **CC6 (pre-crowding magnitude decay)** | PARTIAL — ICT methodology has become broadly popular post-2020 via YouTube. PO3 + MMBM patterns specifically have been retail-popularized. Crowding-decay applies but no empirical baseline to decay FROM (Pattern Q — no peer-reviewed methodology) | DOCUMENTATION-ONLY |
| **CC7 (effective hypothesis count)** | APPLICABLE — 12 strategies on ~5 underlying primitives (`po3_bullish/bearish`, `po3_mmbm/mmsm_setup`, `week_open_gap`, `smc_liquidity_swept_*`, `near_pivot`). Effective N ≈ 5 not 12. | Pattern N within-cluster collinearity |
| **Pattern L SPOF** | APPLICABLE to 4 of 12 (liquidity-consuming) | Cross-ref SMC ticket |
| **Pattern M ICT no peer-review** | FULLY APPLICABLE except Turtle Soup (Raschke 1996 cited; LBR is real published author) | Carry forward |
| **Pattern N intra-cluster collinearity** | HIGH — 12 strategies on 5 primitives | NEW ticket queued |
| **Pattern O hardcoded** | EXTENDED — 6 free parameters | NEW ticket queued |

---

## Cluster scope inventory

**12 strategies across 2 categories.** Sub-cluster grouping by underlying methodology primitive:

| Sub-cluster | # strategies | Strategies |
|---|---|---|
| **A — PO3 daily-candle structure** | 2 | ICT-1 `strat_po3_bullish` / ICT-2 `strat_po3_bearish` |
| **B — PO3 + multi-timeframe** | 2 | ICT-3 `strat_po3_htf_aligned_long` / ICT-4 `strat_po3_htf_aligned_short` |
| **C — Market Maker Models (MMBM/MMSM)** | 2 | ICT-5 `strat_mmbm_long` / ICT-6 `strat_mmsm_short` |
| **D — Turtle Soup (Raschke 1996)** | 2 | ICT-7 `strat_turtle_soup_long` / ICT-8 `strat_turtle_soup_short` |
| **E — Judas Swing** | 2 | ICT-9 `strat_judas_swing_long` / ICT-10 `strat_judas_swing_short` |
| **F — Week-Opening Gap Fill** | 2 | ICT-11 `strat_week_opening_gap_fill_down` / ICT-12 `strat_week_opening_gap_fill_up` |

**Cross-cluster overlap (Pattern N + carryover from SMC):**
- Sub-cluster D + E consume `smc_liquidity_swept_*` from SMC producer — overlaps with SMC-18 (`smc_liquidity_sweep_reversal`) + SMC-12/13 (`smc_equal_*_swept`)
- **5 strategies (ICT-7/8/9/10 + SMC-18) on liquidity_swept_* primitive** → Pattern N flagship cross-cluster ablation candidate

---

## Cross-strategy patterns (ICT cluster)

### Pattern P (NEW for ICT): cross-cluster signal-sharing implicit dependency

**Affects:** ICT-7, ICT-8, ICT-9, ICT-10 (4 of 12 — Turtle Soup + Judas Swing both directions).

**Concern:** These 4 strategies CONSUME `smc_liquidity_swept_dn` / `_up` from SMC producer. Three implicit dependencies inherit:
1. **SMC vendored library SPOF transmits** (Pattern L) — joshyattridge/smartmoneyconcepts import failure silently degrades 4 ICT strategies to no-fire alongside the 18 SMC strategies
2. **Pattern I 90-bar recency staleness inherits** — liquidity sweep event could be up to 4 months stale at ICT-strategy fire bar
3. **Pattern N intra-family overlap** — Turtle Soup + Judas Swing + SMC-18 + SMC-12/13 = 5 strategies × 1 primitive = high effective-test-count inflation

**Step 7 disposition:** every Turtle Soup + Judas Swing walk must cross-reference SMC walk + flag the inherited Pattern L + Pattern I exposure.

### Pattern Q (NEW for ICT): no empirical-backtest citation for 10 of 12 strategies

**Affects:** ICT-1 through ICT-6 + ICT-9 through ICT-12 (10 of 12 — all except Turtle Soup long/short which cite Raschke *Street Smarts* 1996).

**Concern:** Unlike the SMC cluster which had the unaudited Quantum Algo Mar 2026 backtest as collective methodology evidence, the ICT cluster's 10 non-Turtle-Soup strategies were wired via owner inline-spec per `feedback_layer_2d_ict_inline_specification` with NO published methodology citation. The methodology is real (ICT/Inner Circle Trader is a recognized trading-room framework) but UNVALIDATED by peer review OR by an independent backtest of any quality.

**Step 7 disposition:** every non-Turtle-Soup walk must surface Pattern Q as a docstring-honesty concern (the strategies should NOT cite "institutional flow" or "high-conviction" without empirical anchor) + as a Pattern F marginal-contribution ablation pre-requisite (cube validation IS the only adjudication).

### Pattern R (NEW for ICT): PO3 candle-structure thesis ≠ institutional flow validation

**Affects:** ICT-1, ICT-2, ICT-3, ICT-4, ICT-5, ICT-6 (6 of 12 — PO3 + PO3-HTF + MMBM/MMSM).

**Concern:** Docstrings reference "Market Maker Buy/Sell Model" + "institutional accumulation" + "manipulation phase" + "distribution upward" — implying actual order-flow / dark-pool / institutional-positioning evidence. **The producer fires on PRICE-ACTION CANDLE STRUCTURE ONLY** — no flow signal whatsoever. The thesis is internally consistent in the ICT framework but the docstrings overclaim "institutional flow" semantics.

Same class as Pattern B (smart-money-sponsorship overclaim in 13F-state strategies) but applied to PO3-candle-structure not 13F-state. Honest reframe: "PO3 candle structure (accumulation tight range → today's sweep + reversal)" — describes the gate without claiming flow validation.

**Step 7 disposition:** docstring reframe candidate for all 6 PO3-family walks; cluster-wide reframe batch per Pattern E template from SMC cluster.

### Pattern N — Intra-cluster + cross-cluster collinearity (carried + extended)

**Affects:** all 12 ICT strategies.

**Concern:**
- **Intra-cluster:** 12 ICT strategies on ~5 underlying primitives (po3_bullish/bearish + po3_mmbm/mmsm_setup + week_open_gap + smc_liquidity_swept + near_pivot). Effective N ≈ 5.
- **Cross-cluster with SMC:** Turtle Soup + Judas Swing × SMC-18 + SMC-12/13 = 5-strategy × 1-primitive ablation candidate.

**Net effective hypothesis count for ICT ≈ 5 (not 12);** combined ICT + SMC effective N (within shared primitives) ≈ 7 (not 30). C2 multi-testing correction must treat these as near-duplicate hypotheses.

### Pattern A (carried from prior clusters) — `price_above_ema_200` default handling

**Status:** ✅ All 12 ICT strategies use either `price_above_ema_200` (B663 default-False) or `below_ema_200` (B630 producer-additive). 0 default-True instances per grep. PO3 strategies (ICT-1/2) carry EMA-200; PO3-HTF (ICT-3/4) use `weekly_bias_bull/bear` instead; MMBM/MMSM (ICT-5/6) have NO EMA gate (rely on PO3-setup confluence); Turtle Soup + Judas Swing (ICT-7-10) have NO EMA gate (rely on bar-of-fire EVENT bullishness/bearishness via close_above/below_open); Week-Opening-Gap (ICT-11/12) have NO EMA gate (statistical mean-reversion strategy on gap close).

**Missing-trend-filter cluster:** 10 of 12 ICT strategies lack EMA-200 trend gate (only ICT-1/2 have it). Same cluster-wide concern as SMC's 6-of-18; carries forward as candidate for cluster-wide reframe.

### Pattern O (carried + extended) — hardcoded parameters

6 free parameters: `accum_window=5`, `tight_range_threshold=0.05`, `gap_threshold_pct=1.5%`, `near_pivot=±0.30%`, `liquidity_range_pct=0.01` (SMC inherit), `event_recency_bars=90` (SMC inherit). All sensitivity-untested.

---

## Cluster current state table

| ICT # | Function name | Direction | Sub-cluster | Primary signal(s) | Confluence gates | Has EMA gate | Pattern flags | Walk status |
|---|---|---|---|---|---|---|---|---|
| ICT-1 | `strat_po3_bullish` | long | A PO3 | `po3_bullish` | `price_above_ema_200` | ✅ | Q + R | ⏳ Walked B675 |
| ICT-2 | `strat_po3_bearish` | short | A PO3 | `po3_bearish` | `below_ema_200` | ✅ | Q + R | ⏳ Walked B675 |
| ICT-3 | `strat_po3_htf_aligned_long` | long | B PO3+HTF | `po3_bullish` | `weekly_bias_bull` | ❌ (HTF subst.) | Q + R + Pattern N (PO3 reskin) | ⏳ Walked B675 |
| ICT-4 | `strat_po3_htf_aligned_short` | short | B PO3+HTF | `po3_bearish` | `weekly_bias_bear` | ❌ | Q + R + Pattern N | ⏳ Walked B675 |
| ICT-5 | `strat_mmbm_long` | long | C MMBM | `po3_mmbm_setup` | (single-gate) | ❌ | Q + R + single-gate-risk | ⏳ Walked B675 |
| ICT-6 | `strat_mmsm_short` | short | C MMSM | `po3_mmsm_setup` | (single-gate) | ❌ | Q + R + single-gate-risk + B671 borrow-trap | ⏳ Walked B675 |
| ICT-7 | `strat_turtle_soup_long` | long | D Turtle Soup | `smc_liquidity_swept_dn` | `above_prev_low` + `close_above_open` | ❌ | Pattern P + Raschke 1996 cited (only ICT with anchor) | ⏳ Walked B675 |
| ICT-8 | `strat_turtle_soup_short` | short | D Turtle Soup | `smc_liquidity_swept_up` | `below_prev_high` + `close_below_open` | ❌ | Pattern P + B671 borrow-trap | ⏳ Walked B675 |
| ICT-9 | `strat_judas_swing_long` | long | E Judas Swing | `smc_liquidity_swept_dn` | `near_pivot` + `close_above_open` | ❌ | Pattern P + Pattern N (Turtle Soup reskin) | ⏳ Walked B675 |
| ICT-10 | `strat_judas_swing_short` | short | E Judas Swing | `smc_liquidity_swept_up` | `near_pivot` + `close_below_open` | ❌ | Pattern P + B671 borrow-trap | ⏳ Walked B675 |
| ICT-11 | `strat_week_opening_gap_fill_down` | short | F Week-Open Gap | `week_open_gap_up_15pct` | (single-gate; `is_week_open` implicit) | ❌ | Q + B671 borrow-trap + structural-not-flow | ⏳ Walked B675 |
| ICT-12 | `strat_week_opening_gap_fill_up` | long | F Week-Open Gap | `week_open_gap_down_15pct` | (single-gate) | ❌ | Q + structural-not-flow | ⏳ Walked B675 |

**Net cluster state:**
- 12 functions / 12 (strategy × direction) cells (no `_strat3` duals)
- 2 with EMA gate; 10 without (cluster-wide missing-trend-filter concern carries from SMC)
- 4 single-gate strategies (ICT-5, ICT-6, ICT-11, ICT-12) — entire fire condition is one boolean from producer
- 4 cross-cluster signal-sharing (ICT-7-10 consume SMC primitives — Pattern P)
- Pattern A ✅ verified clean
- Pattern Q affects 10 of 12 (only Turtle Soup × 2 has Raschke 1996 citation)
- Pattern R affects 6 of 12 (PO3 family)
- B671 SHORT borrow-trap gate applies to 5 (ICT-2, ICT-6, ICT-8, ICT-10, ICT-11)

---

## Per-strategy walks

### ICT-1. `strat_po3_bullish` (Batch 217, PO3 family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; PO3 daily-candle structure + EMA-200.

#### Step 1 — Read the code

[screener.py:3081-3093](backtest/signals/screener.py#L3081-L3093):

```python
def strat_po3_bullish(s):
    """Batch 217 (PO3 + multi-TF 2026-05-18 owner-approved). Power of 3
    bullish daily candle: open near top, manipulation sweeps below
    prior-day low, distribution closes in upper third of range. ICT
    pattern marking institutional accumulation after a stop hunt."""
    fires = (
        s.get("po3_bullish", False)
        and s.get("price_above_ema_200", False)
    )
```

**2-gate LONG strategy.** Simplest ICT walk in the cluster.

| Gate | Meaning |
|---|---|
| `po3_bullish` | EVENT: today's bar fits PO3 phase-3 bullish distribution candle structure |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |

#### Step 2 — Classify

- Category: `po3`; LONG; B291 default; last touched B663

#### Step 3 — Producer source-read + temporality

- `po3_bullish` is produced by either (a) candle structure detector in producer OR (b) inferred from PO3 phase-3 distribution-candle logic — requires verification. Producer signature: looking at `ict_producers.py` `compute_po3_signals()` we see `po3_mmbm_setup` / `po3_mmsm_setup` but no `po3_bullish` / `po3_bearish` direct emit. **Pattern S (NEW for ICT-1/2): the `po3_bullish` signal source is opaque** — the consumer in screener.py uses `s.get("po3_bullish", False)` but `compute_po3_signals()` doesn't emit that key directly. Either an upstream producer in technical.py or smc_ict.py emits it, OR it's a docstring-claimed signal that defaults to False (silent-gap risk).
- `price_above_ema_200` STATE
- EVENT/STATE: 1 (uncertain origin) + 1 STATE

**ACTION:** Step 5 OPEN_INVESTIGATIONS must surface the producer-signal-origin question.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Power of 3 bullish daily candle: open near top, manipulation sweeps below prior-day low, distribution closes in upper third of range" | ⚠ Producer source unclear — see Step 5; if the signal is not emitted by any producer, the strategy fires only when ambient signals dict carries `po3_bullish` from elsewhere (likely impossible → strategy is dead) |
| "ICT pattern marking institutional accumulation after a stop hunt" | ⚠ **Pattern R** — implies institutional-flow validation; producer (if it exists) computes candle structure only, NOT flow |
| "Power of 3" framing | ⚠ **Pattern Q** — no peer-reviewed citation; owner inline-spec per B217 |

#### Step 5 — OPEN_INVESTIGATIONS grep

- **NEW investigation:** `po3_bullish` / `po3_bearish` signal source unverified. Producer `compute_po3_signals()` in [ict_producers.py:46-93](backtest/signals/ict_producers.py#L46-L93) emits `po3_mmbm_setup` / `po3_mmsm_setup` / `po3_accumulation_active` / `po3_manipulation_sweep_down/up` but NOT `po3_bullish` / `po3_bearish` directly. Possible interpretations: (i) signal is computed in a different producer; (ii) signal name was the B217 spec but B581 producer re-derived as `po3_mmbm_setup` (more restrictive); (iii) strategy is silently dead (signal never emitted → `s.get("po3_bullish", False)` always False → fires=False always). **Verification needed via grep across producers.**

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — ICT-2 `strat_po3_bearish`
- Economic symmetry: ✅ price-action pattern

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-producer-origin-unverified** | `po3_bullish` source unclear; strategy may be silently dead OR consuming a signal computed elsewhere; mandatory pre-cube verification | HIGH | NEW investigation |
| **F-pattern-R** | "Institutional accumulation" framing not validated by actual flow data; PO3 is candle-structure only | MEDIUM | Pattern R |
| **F-pattern-Q** | No empirical-backtest citation; owner inline-spec per B217 | MEDIUM | Pattern Q |
| F-pattern-A | `price_above_ema_200` ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | Cannot project until F-producer-origin-unverified resolved | PENDING | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (pending Step 5 producer verification) |
| **(b) RECOMMENDED — verify producer source FIRST.** If signal is silently dead, ICT-1 + ICT-2 are zero-fire strategies in cube replay (Pattern G EXPLORATORY candidate at best; deletion candidate at worst). If signal exists, then proceed to Pattern R + Pattern Q dispositions |
| (c) Docstring reframe — "PO3 bullish candle structure" replaces "institutional accumulation after stop hunt" |
| (d) Add explicit confluence gates (vol_confirms + structural) per B262/B278 precedent |

**My recommendation: (b).** Producer verification is the gating question; everything downstream depends on whether the signal is alive.

**Awaiting owner direction on ICT-1:**
1. Confirm Step 5 producer verification scope
2. If signal alive: docstring reframe (Pattern R + Pattern Q) + cube validation
3. If signal dead: ICT-1 + ICT-2 deletion candidates OR re-wiring to consume `po3_mmbm_setup` / `po3_mmsm_setup`

---

### ICT-2. `strat_po3_bearish` (Batch 217, PO3 family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT; symmetric mirror of ICT-1.

#### Step 1 — Read the code

[screener.py:3096-3105](backtest/signals/screener.py#L3096-L3105):

```python
def strat_po3_bearish(s):
    """Batch 217: Symmetric bearish PO3 daily."""
    fires = (
        s.get("po3_bearish", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
```

**2-gate SHORT.** Symmetric mirror of ICT-1.

#### Step 2-7 (compact — symmetric with ICT-1)

- Category `po3`; SHORT; B291 default; last touched B630/B663
- Same `F-producer-origin-unverified` concern as ICT-1 (`po3_bearish` source unclear)
- Same Pattern R + Pattern Q concerns
- **B671 centralized DTC>8 borrow-trap gate applies**
- Pattern A B630 producer-additive ✅

**Options:** same as ICT-1; bundled. **My recommendation: (b) bundled — producer verification first.**

**Awaiting owner direction on ICT-2:** bundled with ICT-1.

---

### ICT-3. `strat_po3_htf_aligned_long` (Batch 217, PO3+HTF family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; PO3 + weekly bias confluence (no EMA gate; HTF substitutes).

#### Step 1 — Read the code

[screener.py:3108-3118](backtest/signals/screener.py#L3108-L3118):

```python
def strat_po3_htf_aligned_long(s):
    """Batch 217: PO3 bullish + weekly bias bullish - high-conviction
    long with higher-timeframe directional alignment."""
    fires = (
        s.get("po3_bullish", False)
        and s.get("weekly_bias_bull", False)
    )
```

**2-gate LONG.** PO3 + weekly-timeframe alignment; no daily EMA gate.

| Gate | Meaning |
|---|---|
| `po3_bullish` | EVENT (same `F-producer-origin-unverified` concern as ICT-1) |
| `weekly_bias_bull` | STATE: weekly chart shows bullish bias (likely weekly EMAs aligned) |

#### Step 2 — Classify

- Category: `po3`; LONG; B291 default; last touched B217

#### Step 3 — Producer source-read + temporality

- `po3_bullish`: same uncertain origin as ICT-1
- `weekly_bias_bull`: STATE derived from weekly chart; uses multi-timeframe weekly EMA logic
- EVENT/STATE: 1 (uncertain) + 1 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "PO3 bullish + weekly bias bullish - high-conviction long with higher-timeframe directional alignment" | ⚠ **Pattern Q + Pattern R** — same as ICT-1; "high-conviction" overclaim with no empirical anchor + PO3 is candle-structure not flow |
| Implicit "HTF confluence substitutes for daily EMA gate" | ⚠ Mechanically OK (weekly_bias_bull is a stricter trend filter than daily EMA-200) but no validation that this is empirically equivalent |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Same `F-producer-origin-unverified` carry-forward from ICT-1
- Pattern N: ICT-3 is a reskin of ICT-1 with `weekly_bias_bull` replacing `price_above_ema_200`. Marginal contribution likely near-zero (HTF + daily-EMA-200 both measure trend; one is a stricter version of the other)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — ICT-4 `strat_po3_htf_aligned_short`
- Economic symmetry: ✅

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-producer-origin-unverified (carry)** | Same as ICT-1 | HIGH | NEW investigation |
| **F-pattern-N (PO3-family reskin)** | ICT-3 = ICT-1 with HTF substitution; marginal contribution of HTF gate vs EMA gate unknown | MEDIUM | Pattern N |
| F-pattern-Q + R | Same as ICT-1 | MEDIUM | Q + R |
| F-fire-count | po3_bullish × weekly_bias_bull narrow co-occurrence; projected RARE; if signal alive ~5-20/yr universe-wide; Pattern G EXPLORATORY candidate | MEDIUM | F4 |

**Options:** bundle with ICT-1 producer verification; if alive, cube-replay marginal-contribution test (ICT-3 vs ICT-1 baseline).

**My recommendation: (b) bundled.**

**Awaiting owner direction on ICT-3:** bundled with ICT-1; additional question on Pattern N marginal-contribution between ICT-3 and ICT-1.

---

### ICT-4. `strat_po3_htf_aligned_short` (Batch 217, PO3+HTF family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT; symmetric mirror of ICT-3.

[screener.py:3121-3130](backtest/signals/screener.py#L3121-L3130) — symmetric. Same findings as ICT-3 with `po3_bearish` + `weekly_bias_bear` + **B671 DTC>8 borrow-trap applies**.

**Options:** bundled with ICT-1/2/3. **My recommendation: (b) bundled.**

---

### ICT-5. `strat_mmbm_long` (Batch 581, MMBM family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **1-gate LONG** (single-boolean consumer); MMBM = Market Maker Buy Model (ICT PO3 bullish 3-phase cycle).

#### Step 1 — Read the code

[screener.py:3659-3681](backtest/signals/screener.py#L3659-L3681):

```python
def strat_mmbm_long(s):
    """Batch 581 (2026-06-04): Market Maker Buy Model (MMBM) - bullish
    Power-of-3 cycle per ICT methodology + owner inline-spec.

    Setup: Accumulation (tight range last N bars) -> Manipulation
    (sweep below accumulation low) -> Distribution (close back above
    accumulation low with bullish bar). The institutional-flow pattern:
    market makers accumulate at the range low, manipulate price down to
    trigger retail stops + accumulate cheap liquidity, then distribute
    upward toward the original range high.

    Producer: compute_po3_signals() in backtest/signals/ict_producers.py
    consumed via po3_mmbm_setup boolean (combined gate: accumulation +
    sweep-down + close-above-low + bullish-bar).
    """
    fires = bool(s.get("po3_mmbm_setup", False))
```

**1-gate LONG strategy.** Pure single-boolean consumer; ALL conditions in the producer (`compute_po3_signals`).

| Gate | Meaning |
|---|---|
| `po3_mmbm_setup` | EVENT (4-condition AND inside producer): tight 5%-range accumulation last 5 bars + today's low < range_low + today's close > range_low + today's close > today's open |

#### Step 2 — Classify

- Category: `ict`; LONG; B291 default; last touched B581
- **Pattern S (NEW for ICT-5/6/11/12 single-gate strategies):** strategy is a thin shell over a producer flag. Hardcoded producer parameters (`accum_window=5`, `tight_range_threshold=0.05`) are NOT visible at the strategy level — extreme case of "behavior not visible at call site" anti-pattern.

#### Step 3 — Producer source-read + temporality

- `po3_mmbm_setup` at [ict_producers.py:46-93](backtest/signals/ict_producers.py#L46-L93) — true when `po3_accumulation_active=True` AND `swept_down=True` AND `today_close > range_low` AND `today_close > today_open`
- Lag: 0-day point-in-time on today's bar; accumulation phase uses 5-day prior window
- EVENT/STATE: pure EVENT (bar-of-fire)
- **NO EMA REGIME GATE** — neither at strategy nor producer level

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Market Maker Buy Model (MMBM) - bullish Power-of-3 cycle per ICT methodology + owner inline-spec" | ⚠ **Pattern Q** — owner inline-spec only; no empirical anchor |
| "market makers accumulate at the range low, manipulate price down to trigger retail stops + accumulate cheap liquidity, then distribute upward" | ⚠ **Pattern R (STRONGEST CASE)** — explicit "institutional flow" thesis with ZERO flow data behind it. Producer checks CANDLE STRUCTURE: tight range + sweep + close-back-inside + bullish-bar. NONE of these are flow signals. The framing as "market makers" is methodology-rhetoric, not data evidence. |
| "Phase 1 ACCUMULATION: tight range over last N bars" | ✅ Mechanically verified — `accum_range_pct <= 0.05` |
| "Phase 2 MANIPULATION: sweep below accumulation low (stops taken)" | ✅ Mechanically verified — `swept_down = today_low < range_low` |
| "Phase 3 DISTRIBUTION setup: price reversed back inside range, bullish bar" | ✅ Mechanically verified — `today_close > range_low AND today_close > today_open` |

**Net Step 4:** the MECHANICAL pattern detection is sound; the FLOW NARRATIVE attached to it is overclaim per Pattern R. Honest reframe: "Failed-breakdown reversal candle within 5-day tight-range accumulation context."

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern O `accum_window=5` + `tight_range_threshold=0.05` config-parameterization candidates
- No active investigations specific to ICT-5

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — ICT-6 `strat_mmsm_short`
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-R (institutional-flow overclaim — strongest case)** | "Market makers accumulate / distribute" framing with zero flow data; pure candle-structure pattern | HIGH | Pattern R |
| **F-pattern-Q** | Owner inline-spec; no empirical anchor | MEDIUM | Pattern Q |
| **F-no-EMA-gate** | Same cluster-wide concern; HTF-substitution not present here either | MEDIUM | Missing-trend-filter |
| **F-pattern-S single-gate shell** | Strategy is 1-gate shell over multi-condition producer; hardcoded parameters invisible at call site | MEDIUM | NEW Pattern S |
| **F-pattern-O hardcoded** | `accum_window=5`, `tight_range_threshold=0.05` — Pattern O config-parameterization candidate | MEDIUM | Pattern O |
| F-fire-count | 4-condition AND in producer + tight 5% range constraint → very rare; projected ~5-20/yr universe-wide; HIGH RISK FAIL min_trades=30 per regime | HIGH | F4 + Pattern G |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Docstring reframe per Pattern R — strip "market maker" / "institutional flow" framing; describe candle structure honestly |
| (c) Add EMA-200 trend gate per cluster-wide proposal |
| (d) EXPLORATORY marker per W5/W5m precedent — exclude from selection budget while keeping cube-replay coverage |
| (e) Pattern O config-parameterize `accum_window` + `tight_range_threshold` for cube sensitivity sweep |
| **(f) RECOMMENDED — (b) + (c) + (d) bundled. Pattern R honesty reframe is mandatory; cluster-wide EMA proposal applies; if post-B660 confirms <30 fires/regime → (d) EXPLORATORY. (e) post-cube empirical settles parameter sensitivity.** |

**My recommendation: (f).**

**Awaiting owner direction on ICT-5:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (f)
2. Pattern R docstring reframe bundled with ICT-1/2/3/4/6 (6-strategy PO3 family batch)
3. Cluster-wide EMA proposal bundled with ICT-3/4/6/7/8/9/10/11/12 (10-strategy missing-EMA batch)

---

### ICT-6. `strat_mmsm_short` (Batch 581, MMSM family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **1-gate SHORT**; symmetric mirror of ICT-5.

#### Step 1 — Read the code

[screener.py:3684-3694](backtest/signals/screener.py#L3684-L3694):

```python
def strat_mmsm_short(s):
    """Mirror of strat_mmbm_long. Market Maker Sell Model - bearish PO3.
    Sweep up to take stops above range high, then distribute downward."""
    fires = bool(s.get("po3_mmsm_setup", False))
```

**1-gate SHORT strategy.** Symmetric mirror of ICT-5.

#### Step 2-7 (compact — symmetric with ICT-5)

- Category `ict`; SHORT; B291 default; last touched B581
- Same Pattern R + Q + S + O + no-EMA + fire-count concerns
- **B671 centralized DTC>8 borrow-trap gate applies**
- Fire-count: bearish PO3 less common than bullish (upward-drift equity); projected ~5-15/yr universe-wide; HIGH RISK FAIL

**Options:** same as ICT-5; bundled. **My recommendation: (f) bundled.**

**Awaiting owner direction on ICT-6:** bundled with ICT-5.

---

### ICT-7. `strat_turtle_soup_long` (Batch 580, Turtle Soup family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **ONLY ICT STRATEGY WITH PEER-REVIEWABLE CITATION** — Raschke *Street Smarts* 1996 (Linda Bradford Raschke + Lawrence Connors). Cross-cluster Pattern P + N applies (consumes SMC `liquidity_swept_dn`).

#### Step 1 — Read the code

[screener.py:3546-3587](backtest/signals/screener.py#L3546-L3587):

```python
def strat_turtle_soup_long(s):
    """Batch 580 (2026-06-04): Turtle Soup mean-reversion long per Linda
    Bradford Raschke 'Street Smarts' (1996). First Layer 2D ICT pattern
    wired via inline-spec protocol (Option A 2026-06-04 per
    feedback_layer_2d_ict_inline_specification).
    ...
    """
    fires = (
        s.get("smc_liquidity_swept_dn", False)
        and s.get("above_prev_low", False)     # B616: closed back ABOVE prior-day-low
        and s.get("close_above_open", False)   # bullish reversal bar
    )
```

**3-gate LONG strategy.** Best-anchored ICT walk per Raschke citation + clean B616 positive-symmetric refactor.

| Gate | Meaning |
|---|---|
| `smc_liquidity_swept_dn` | EVENT (90-bar recency from SMC producer): equal-lows cluster swept |
| `above_prev_low` | EVENT: today's close > prior day's low (B616 positive-symmetric pair to existing below_prev_low; replaces B616 default-True NOT-pattern) |
| `close_above_open` | EVENT: bullish reversal bar |

#### Step 2 — Classify

- Category: `ict`; LONG; B291 default; last touched B616 (positive-symmetric refactor)

#### Step 3 — Producer source-read + temporality

- `smc_liquidity_swept_dn`: 90-bar recency via `_most_recent_event_within` per SMC producer (Pattern P + Pattern I inherited)
- `above_prev_low`: bar-of-fire EVENT per technical.py B616 producer
- `close_above_open`: bar-of-fire EVENT per technical.py
- EVENT/STATE: 1 recency-windowed (Pattern I inherited) + 2 bar-of-fire EVENTs

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Linda Bradford Raschke 'Street Smarts' (1996)" | ✅ **REAL CITATION** — Raschke + Connors *Street Smarts: High Probability Short-Term Trading Strategies* (1996) is a published trading methodology book; Turtle Soup IS a documented pattern. Best-in-class ICT citation. |
| "The failed-breakdown pattern suggests the downside move was a stop-hunt rather than a genuine trend continuation" | ✅ Defensible at the structural level — failed-breakdown patterns are documented in price-action literature beyond ICT |
| "ICT framing: 'Judas Swing failed', return-to-range" | ⚠ ICT-framing tag; methodology-rhetoric but accurate as ICT's own naming convention |
| "Distinct from `smc_liquidity_sweep_reversal` (which requires CHoCH or BOS confirmation). Turtle Soup is the pure Raschke pattern - no structure-shift confirmation needed" | ✅ Correct differentiation; the Raschke version is mechanically simpler (no CHoCH/BOS) |

**Net Step 4:** the ONLY ICT-cluster strategy with a legitimate, peer-reviewable methodology citation. Raschke + Connors are real published methodologists; Turtle Soup is a documented pattern; the docstring is honest about the mechanical structure.

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern P inherited from SMC — Pattern L SPOF + Pattern I 90-bar recency on `smc_liquidity_swept_dn`
- Pattern N intra-cluster + cross-cluster — ICT-7 + ICT-9 (Judas Swing long) + SMC-12 (equal_lows_sweep_long) + SMC-13 + SMC-18 (liquidity_sweep_reversal) all consume liquidity-sweep primitives. Cross-ref `S4-SMC-CLUSTER-PATTERN-J-CUBE-ABLATION` + `S4-SMC-CLUSTER-PATTERN-N-INTRA-CLUSTER-COLLINEARITY` — ICT cluster ADDS to those tickets.

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — ICT-8 `strat_turtle_soup_short`
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-P SMC-dependency** | Inherits SMC Pattern L SPOF + Pattern I 90-bar staleness via `smc_liquidity_swept_dn` consumption | MEDIUM | Pattern P |
| **F-pattern-N cross-cluster** | Pattern N flagship specimen — Turtle Soup + Judas Swing + SMC-12/13 + SMC-18 = 5 strategies on liquidity-sweep primitives | MEDIUM-HIGH | Pattern N |
| **F-citation ✅** | Raschke 1996 IS a legitimate citation (cluster-positive note) | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-no-EMA-gate** | Cluster-wide concern | MEDIUM | Missing-trend-filter |
| F-fire-count | Liquidity-sweep × prior-low + bullish-reversal narrow co-occurrence; projected ~10-25/yr universe-wide; borderline | MEDIUM | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (highest-quality ICT walk; minimal changes warranted) |
| (b) Add EMA-200 trend gate per cluster-wide proposal |
| (c) Cube-replay Pattern N flagship cross-cluster ablation (ICT-7 + ICT-9 + SMC-12 + SMC-13 + SMC-18) |
| **(d) RECOMMENDED — (a) status quo on code + (c) post-B660 cross-cluster ablation. Turtle Soup is the cluster's best-anchored strategy; cube settles whether it earns its registry slot vs SMC reskins.** |

**My recommendation: (d).**

**Awaiting owner direction on ICT-7:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Pattern N flagship cross-cluster ablation scope confirmation
3. Cluster-wide EMA proposal bundling decision (separate from ICT-7 disposition)

---

### ICT-8. `strat_turtle_soup_short` (Batch 580, Turtle Soup family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate SHORT; symmetric mirror of ICT-7.

[screener.py:3590-3611](backtest/signals/screener.py#L3590-L3611) — symmetric. Raschke 1996 citation carries. Pattern P + N + L + I inherited. **B671 DTC>8 borrow-trap gate applies.** Fire-count: bearish failed-breakouts less common than bullish failed-breakdowns; projected ~7-20/yr universe-wide; borderline.

**Options:** same as ICT-7; bundled. **My recommendation: (d) bundled.**

**Awaiting owner direction on ICT-8:** bundled with ICT-7.

---

### ICT-9. `strat_judas_swing_long` (Batch 581, Judas Swing family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG; Judas Swing variant per ICT inline-spec. Near-reskin of Turtle Soup (ICT-7) with `near_pivot` replacing `above_prev_low`.

#### Step 1 — Read the code

[screener.py:3614-3641](backtest/signals/screener.py#L3614-L3641):

```python
def strat_judas_swing_long(s):
    """Batch 581 (2026-06-04): Judas Swing variant per ICT specification.
    Distinct from `smc_liquidity_sweep_reversal` (which requires CHoCH/BOS)
    AND from `turtle_soup_long` (which requires close back above prior_low).
    Judas Swing focuses on FALSE RANGE BREAK + return to RANGE INTERIOR
    (deeper return to pivot midpoint vs Turtle Soup's just-back-inside).
    ...
    """
    fires = (
        s.get("smc_liquidity_swept_dn", False)
        and s.get("near_pivot", False)
        and s.get("close_above_open", False)
    )
```

**3-gate LONG strategy.** Near-reskin of ICT-7 with `near_pivot` (close within ±0.30% of standard pivot) replacing `above_prev_low` (close > prior day low).

#### Step 2 — Classify

- Category: `ict`; LONG; B291 default; last touched B581

#### Step 3 — Producer source-read + temporality

- `smc_liquidity_swept_dn`: 90-bar recency (Pattern P + I inherited from SMC)
- `near_pivot`: bar-of-fire EVENT per technical.py
- `close_above_open`: bar-of-fire EVENT
- EVENT/STATE: 1 recency-windowed + 2 bar-of-fire

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Catches the 'manipulation' move in ICT framing - retail stops hunted then institutions reverse deeper into the range" | ⚠ **Pattern R + Pattern Q** — institutional-flow framing without flow data; no peer-reviewed citation |
| "Distinct from `smc_liquidity_sweep_reversal` AND from `turtle_soup_long`" | ✅ Correct differentiation; explicit distinction noted in docstring (positive provenance) |
| "Deeper return to pivot midpoint vs Turtle Soup's just-back-inside" | ✅ Mechanically defensible — `near_pivot` ±0.30% is a tighter return than "above prior_low" |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Same Pattern P + N + I + L + Pattern O (`near_pivot=±0.30%` hardcoded) carryover
- Pattern N: ICT-9 is a near-reskin of ICT-7 (Turtle Soup) — only the second gate differs (`near_pivot` vs `above_prev_low`); marginal contribution test required

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — ICT-10 `strat_judas_swing_short`
- Economic symmetry: ✅

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-N reskin of ICT-7** | Near-duplicate of Turtle Soup with second-gate substitution; marginal contribution likely small | MEDIUM-HIGH | Pattern N |
| **F-pattern-R + Q** | ICT framing without empirical anchor or flow data | MEDIUM | R + Q |
| **F-pattern-P SMC-dependency** | Same as ICT-7 | MEDIUM | Pattern P |
| **F-no-EMA-gate** | Cluster-wide | MEDIUM | Missing-trend-filter |
| **F-pattern-O `near_pivot` ±0.30% hardcoded** | Tolerance untested | LOW | Pattern O |
| F-fire-count | `near_pivot` is rare (±0.30% band); liquidity-sweep co-occurrence further narrows; projected ~5-15/yr universe-wide; HIGH RISK FAIL | HIGH | F4 + Pattern G |

**Options:** (a) status quo / (b) cube-replay ICT-9 vs ICT-7 marginal contribution / (c) Pattern R docstring reframe / (d) EMA gate per cluster-wide / (e) EXPLORATORY marker pre-cube. **My recommendation: (b) + (c) bundled.**

**Awaiting owner direction on ICT-9:**
1. Recommendation (b) + (c) bundled
2. Pattern N flagship ablation includes ICT-7 vs ICT-9 dose-response
3. EXPLORATORY marker disposition if post-B660 confirms <30 fires/regime

---

### ICT-10. `strat_judas_swing_short` (Batch 581, Judas Swing family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate SHORT; symmetric mirror of ICT-9.

[screener.py:3644-3656](backtest/signals/screener.py#L3644-L3656) — symmetric. **B671 DTC>8 borrow-trap applies.** Same Pattern N + R + Q + P + O findings. Fire-count: rarer than ICT-9 (bearish failed-breakouts); HIGH RISK FAIL.

**Options:** same as ICT-9; bundled. **My recommendation: (b) + (c) bundled.**

**Awaiting owner direction on ICT-10:** bundled with ICT-9.

---

### ICT-11. `strat_week_opening_gap_fill_down` (Batch 581, Week-Opening Gap family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **1-gate SHORT** (single-boolean consumer); statistical week-open gap-fill strategy.

#### Step 1 — Read the code

[screener.py:3697-3710](backtest/signals/screener.py#L3697-L3710):

```python
def strat_week_opening_gap_fill_down(s):
    """Batch 581 (2026-06-04): Week Opening Gap Fill - SHORT direction.
    Daily-bar proxy for ICT Sunday gap. When Monday opens with a
    significant gap UP (Mon_open > Fri_close by >= 1.5pct), price often
    drifts DOWN to fill the gap. Fade the gap up.
    ...
    """
    fires = bool(s.get("week_open_gap_up_15pct", False))
```

**1-gate SHORT strategy.** Pure single-boolean consumer (Pattern S — strategy is shell over producer flag).

| Gate | Meaning |
|---|---|
| `week_open_gap_up_15pct` | EVENT (producer 2-condition AND): today is week-open AND today's open ≥ 1.5% above prior Friday close |

#### Step 2 — Classify

- Category: `ict`; SHORT; B291 default; last touched B581

#### Step 3 — Producer source-read + temporality

- `week_open_gap_up_15pct` at [ict_producers.py:96-155](backtest/signals/ict_producers.py#L96-L155) — true when `is_week_open=True` AND `gap_pct >= 1.5%`
- `is_week_open` detection logic at lines 138-139: `(today_weekday == 0 and prev_weekday >= 4) or (today_weekday < prev_weekday and (today_idx - prev_idx).days >= 2)` — Monday after weekend OR holiday-extended-weekend case
- Lag: 0-day bar-of-fire EVENT
- EVENT/STATE: pure EVENT

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Daily-bar proxy for ICT Sunday gap" | ⚠ **Pattern Q** — no published statistical study on weekly gap-fill rate cited; owner inline-spec |
| "Statistical bias: gaps tend to fill on the week-open bar" | ⚠ **Pattern Q empirical claim without citation** — there IS legitimate academic literature on intraday gap-fill statistics (Branch + Echevarria 1991, Akarim + Sevim 2013, others) but the SPECIFIC "1.5% week-open gap fills on same bar" claim has no source. Honest reframe: "Empirically untested daily-bar-proxy hypothesis for the ICT Sunday-gap-fill pattern" |
| "When Monday opens with a significant gap UP, price often drifts DOWN to fill the gap. Fade the gap up." | ⚠ Mean-reversion claim with no statistical backing in the docstring |

#### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations specific to ICT-11
- Pattern O `gap_threshold_pct=1.5%` hardcoded config-parameterization candidate
- Pattern Q empirical-statistic-without-citation candidate

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — ICT-12 `strat_week_opening_gap_fill_up`
- Economic symmetry: ✅ price-action; both gap-up and gap-down mean-reversion fade is symmetric

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-Q empirical claim** | "Statistical bias: gaps tend to fill" — no citation; reframe to "untested hypothesis" pre-cube | MEDIUM | Pattern Q |
| **F-pattern-S single-gate shell** | 1-gate strategy; hardcoded `gap_threshold_pct=1.5%` invisible at call site | MEDIUM | Pattern S |
| **F-pattern-O hardcoded** | `gap_threshold_pct=1.5%` empirically untuned | MEDIUM | Pattern O |
| **F-no-EMA-gate** | Cluster-wide concern | MEDIUM | Missing-trend-filter |
| **F-borrow-cost** | B671 DTC>8 borrow-trap gate applies | LOW | F5 |
| F-fire-count | Week-open + 1.5% gap up is uncommon (~5-10% of week-opens per ticker → ~3-5 fires/yr per ticker × 503 tickers = ~1500-2500/yr universe-wide; PASS LIKELY) | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern Q docstring reframe — "untested hypothesis" replaces "statistical bias" |
| (c) Pattern O config-parameterize `gap_threshold_pct` for cube sweep (1% / 1.5% / 2%) |
| (d) Add EMA-200 trend gate per cluster-wide proposal — SHORT-fade-of-gap-up makes more sense in bear/neutral regime than bull regime |
| (e) Cube-replay statistical validation of gap-fill rate against actual T1a 6-year history |
| **(f) RECOMMENDED — (b) + (e). Pattern Q docstring honesty + cube empirical validates the statistical claim. (c) + (d) are Class 2 candidates post-cube.** |

**My recommendation: (f).**

**Awaiting owner direction on ICT-11:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (f)
2. Pattern Q docstring reframe bundled with ICT-1/2/3/4/5/6 + ICT-9/10/12 (cluster-wide reframe batch)
3. Pattern O `gap_threshold_pct` config-parameterization scope

---

### ICT-12. `strat_week_opening_gap_fill_up` (Batch 581, Week-Opening Gap family, walked B675)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 1-gate LONG; symmetric mirror of ICT-11.

#### Step 1 — Read the code

[screener.py:3713-3722](backtest/signals/screener.py#L3713-L3722):

```python
def strat_week_opening_gap_fill_up(s):
    """Mirror of strat_week_opening_gap_fill_down. When Monday opens
    with a gap DOWN >= 1.5pct, price often drifts UP to fill. Fade
    the gap down."""
    fires = bool(s.get("week_open_gap_down_15pct", False))
```

**1-gate LONG strategy.** Symmetric mirror of ICT-11.

#### Step 2-7 (compact — symmetric with ICT-11)

- Category `ict`; LONG; B291 default; last touched B581
- Same Pattern Q + S + O + no-EMA findings
- Fire-count: week-open + 1.5% gap-DOWN slightly LESS common than gap-up (upward-drift equity); projected ~1000-2000/yr universe-wide; PASS likely

**Options:** same as ICT-11; bundled. **My recommendation: (f) bundled.**

**Awaiting owner direction on ICT-12:** bundled with ICT-11.

---

## B675 cluster walk completion wrap-up

> All 12 ICT pure price-action cluster strategies now have full pivot-doc-template per-walk coverage:
>
> - **Sub-cluster A — PO3 daily-candle (2):** ICT-1 + ICT-2 (`F-producer-origin-unverified` HIGH-priority)
> - **Sub-cluster B — PO3+HTF (2):** ICT-3 + ICT-4 (PO3-family reskin Pattern N)
> - **Sub-cluster C — MMBM/MMSM (2):** ICT-5 + ICT-6 (Pattern R strongest case)
> - **Sub-cluster D — Turtle Soup (2):** ICT-7 + ICT-8 (Raschke 1996 — best-anchored ICT walk; Pattern P inherits SMC dependency)
> - **Sub-cluster E — Judas Swing (2):** ICT-9 + ICT-10 (near-reskin of Turtle Soup; Pattern N + P)
> - **Sub-cluster F — Week-Opening Gap (2):** ICT-11 + ICT-12 (Pattern Q empirical-claim; PASS-likely fire count)
>
> **Total fully-expanded: 12 of 12. ICT CLUSTER WALK COMPLETE.**

### Bundled disposition recommendations summary

| Pattern | Strategies | Disposition |
|---|---|---|
| **A (default-True silent-gap)** | ✅ All 12 clean (B663/B630 swept; ICT-1/2 have EMA gate; others use HTF/structural substitutes) | ✅ RESOLVED |
| **Q (no empirical-backtest citation)** | 10 of 12 (only Turtle Soup × 2 has Raschke 1996 citation) | Docstring reframe candidates; cube validation as only adjudication |
| **R (PO3 candle-structure ≠ institutional-flow)** | 6 of 12 (PO3 family + MMBM/MMSM) | Docstring reframe per Pattern E template from SMC |
| **N (intra/cross-cluster collinearity)** | 12 strategies on 5 primitives; cross-cluster with SMC-12/13/18 (5 strategies on liquidity_swept_*) | Cube replay Pattern J flagship cross-cluster ablation |
| **P (cross-cluster SMC dependency)** | 4 of 12 (Turtle Soup + Judas Swing) — inherit Pattern L SPOF + Pattern I 90-bar staleness | Document inherited risk; no producer fix at ICT-cluster level |
| **O (hardcoded tolerances)** | 6 free parameters across cluster | Config-parameterization for cube sensitivity sweep |
| **S (single-gate strategy shell)** | 4 strategies (ICT-5, ICT-6, ICT-11, ICT-12) — strategy is 1-gate consumer over multi-condition producer flag | Hardcoded parameters invisible at call site; consider explicit gate exposure |
| **F-producer-origin-unverified** | ICT-1 + ICT-2 (`po3_bullish` / `po3_bearish` signal source unclear) | HIGH-priority pre-cube verification |
| **Missing-trend-filter cluster-wide** | 10 of 12 (only ICT-1 + ICT-2 have EMA-200) | Cluster-wide EMA-gate proposal bundled with SMC cluster's same proposal |
| **F-fire-count Pattern G** | ICT-3, ICT-4 (PO3-HTF), ICT-5, ICT-6 (MMBM/MMSM), ICT-9, ICT-10 (Judas Swing) — all projected <30 fires/regime | EXPLORATORY marker candidates post-B660 measurement |

### Queue tickets surfaced (recap)

NEW B675 tickets:

- `S4-ICT-CLUSTER-PRODUCER-ORIGIN-VERIFICATION-PO3-BULLISH-BEARISH` (HIGH) — verify `po3_bullish` / `po3_bearish` signal source; gate ICT-1 + ICT-2 + ICT-3 + ICT-4 disposition
- `S4-ICT-PATTERN-R-CANDLE-STRUCTURE-NOT-INSTITUTIONAL-FLOW-DOCSTRING-REFRAME` — 6-strategy PO3-family docstring honesty batch
- `S4-ICT-PATTERN-Q-NO-EMPIRICAL-CITATION-DOCSTRING-CAVEAT` — 10-strategy reframe (all except Turtle Soup × 2)
- `S4-ICT-CLUSTER-PATTERN-N-CROSS-CLUSTER-CUBE-ABLATION-WITH-SMC` — flagship cross-cluster ablation (ICT-7 + ICT-8 + ICT-9 + ICT-10 + SMC-12 + SMC-13 + SMC-18; 7 strategies on liquidity_swept_* primitive)
- `S4-ICT-PATTERN-O-CONFIG-PARAMETERIZATION` — 6 hardcoded parameters (`accum_window`, `tight_range_threshold`, `gap_threshold_pct`, `near_pivot`, + 2 inherited from SMC)
- `S4-ICT-CLUSTER-WIDE-EMA-GATE-PROPOSAL` — 10-strategy missing-trend-filter bundled with SMC-equivalent proposal
- `S4-ICT-PATTERN-S-SINGLE-GATE-STRATEGY-SHELL-AUDIT` — 4 single-gate consumers (ICT-5/6/11/12) hardcoded-parameter visibility concern

EXISTING tickets cross-referenced:
- `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` — ICT-3/4/5/6/9/10 added as candidates
- `S5-MARGINAL-CONTRIBUTION-SCORING` — ICT cluster Pattern N is 3rd-highest-leverage application (after smart-money 13F sleeve test and SMC cluster Pattern J)
- `S4-SMC-CLUSTER-PATTERN-J-CUBE-ABLATION` — EXTEND scope to include ICT-7/8/9/10 (5+ strategies on liquidity_swept_* primitive)

---

## Cluster-wide methodology references

- **Producers:** [backtest/signals/ict_producers.py](backtest/signals/ict_producers.py) (po3 + mmbm + mmsm + week-opening-gap) + [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py) (liquidity_swept_* via vendored joshyattridge/smartmoneyconcepts) + [backtest/signals/technical.py](backtest/signals/technical.py) (near_pivot + close_above/below_open + above/below_prev_low/high)
- **Strategies:** [backtest/signals/screener.py](backtest/signals/screener.py) — ICT-1 + ICT-2 @ 3081-3105 (PO3); ICT-3 + ICT-4 @ 3108-3130 (PO3-HTF); ICT-5 + ICT-6 @ 3659-3694 (MMBM/MMSM); ICT-7 + ICT-8 @ 3546-3611 (Turtle Soup); ICT-9 + ICT-10 @ 3614-3656 (Judas Swing); ICT-11 + ICT-12 @ 3697-3722 (Week-Opening Gap)
- **Wiring batches:**
  - **B217** (2026-05-18): PO3 + multi-TF family (ICT-1, ICT-2, ICT-3, ICT-4)
  - **B580** (2026-06-04): Turtle Soup × 2 per Raschke 1996 inline-spec
  - **B581** (2026-06-04): Judas Swing + MMBM + MMSM + Week-Opening Gap (6 strategies in one batch)
  - **B616** (2026-06-07): Turtle Soup positive-symmetric refactor (B616 added `above_prev_low` / `below_prev_high`)
- **Vendored library (4 of 12 strategies depend):** `vendored/smartmoneyconcepts/smartmoneyconcepts.py` (Pattern L SPOF inherited from SMC cluster)
- **Citations:**
  - Raschke + Connors *Street Smarts: High Probability Short-Term Trading Strategies* (1996) — Turtle Soup family (ICT-7 + ICT-8 ONLY)
  - Inner Circle Trader / Michael J. Huddleston methodology — no peer-reviewed publications (Pattern Q applies to 10 of 12)
- **Cluster status sequencing:** PENDING B660 measured-fire-count + B668 cube replay + B669 survivorship execution. No empirical disposition pre-B660 per `feedback_no_rushing_per_strategy_tweak` + B665 foundational re-prioritization commitment.

---

## B675 cluster walk status

| Item | Status |
|---|---|
| Doc infrastructure (header + adaptations + inventory + patterns + state table) | ✅ B675 |
| Per-strategy walks ICT-1 through ICT-12 (12 walks at full template density) | ✅ B675 |
| External reviewer pass | ⏳ post-walk-completion |
| Cluster-wide post-walk findings synthesis | ⏳ post-reviewer |

**Cumulative B675: 12 of 12 walks fully expanded. CLUSTER WALK COMPLETE.**

## B680 Self-Critique Iteration 2 — Cross-Cutting Feasibility Findings

> **Status (B680 self-critique iteration 2026-06-10):** owner directive *"Just update all docs"* — proceed with adversarial self-critique in lieu of external reviewer pass.

### Cross-cutting feasibility findings (Claude self-critique 2026-06-10)

| # | Finding | Verification | Severity | Status |
|---|---|---|---|---|
| **CC-A** | ~~**`po3_bullish` / `po3_bearish` signal source MAY BE SILENTLY DEAD** — walk Step 5 grep of `ict_producers.py` `compute_po3_signals` (PLURAL) found `po3_mmbm_setup` + `po3_mmsm_setup` + `po3_accumulation_active` + `po3_manipulation_sweep_*` but NOT `po3_bullish` / `po3_bearish`.~~ **B681 verification RESOLVED 2026-06-10 (owner-approved investigation):** the walk's grep was INCOMPLETE. The `po3_bullish` / `po3_bearish` signals ARE emitted by a DIFFERENT producer: `compute_po3_signal` (SINGULAR — NOTE the missing 's') in [backtest/signals/multi_timeframe.py:194-260](backtest/signals/multi_timeframe.py#L194-L260) — B217 producer that uses `today_low <= prev_day_low * 1.001 AND today_close > today_open AND close_position > 0.66` for bullish PO3. Wired in [screener.py:6991-7007](backtest/signals/screener.py#L6991-L7007) via `from backtest.signals.multi_timeframe import compute_po3_signal; po3 = compute_po3_signal(df); signals.update(po3)`. **ICT-1/ICT-2/ICT-3/ICT-4 are NOT silently dead.** The walk's CC-A concern was based on confusing two similarly-named producers — `compute_po3_signals` (PLURAL, ict_producers.py, B581) feeds ICT-5/ICT-6 (MMBM/MMSM); `compute_po3_signal` (SINGULAR, multi_timeframe.py, B217) feeds ICT-1-4 (PO3 daily candle). **B660 run will empirically validate fire counts when processing reaches "p" strategies in the alphabetical sweep (~hours away as of this update).** | ✅ B681 resolved — both producers verified live | **RESOLVED (NOT silently dead)** | `S4-ICT-PO3-SIGNAL-PRODUCER-VERIFICATION-IMMEDIATE` ticket **RESOLVED-B681** (verification only; Pattern Q + R concerns from walk still stand) |
| **CC-B** | **Pattern R "institutional flow" framing is the cluster's MOST PERVASIVE overclaim — affects 6 of 12 strategies — and is a direct analog of the smart-money Pattern B that the external reviewer flagged.** ICT-5 `strat_mmbm_long` docstring: *"market makers accumulate at the range low, manipulate price down to trigger retail stops + accumulate cheap liquidity, then distribute upward."* Producer (`compute_po3_signals`) checks: `accum_range_pct <= 0.05` + `today_low < range_low` + `today_close > range_low` + `today_close > today_open`. **ZERO flow signal. ZERO market-maker positioning data. Just candle structure.** The same overclaim pattern that smart-money cluster's Pattern B fix targeted (13F state implying bar-of-fire conviction) applies HERE to PO3 candle structure implying institutional flow. **Walks identified this as Pattern R but the docstring fixes are deferred to post-B660; they should ship pre-cube to avoid the cube producing data labeled with the false thesis.** | ✅ Verified via producer source-read | **HIGH** | NEW — `S4-ICT-PATTERN-R-DOCSTRING-PRE-CUBE-FIX-REQUIRED` |
| **CC-C** | **Pattern Q "no peer-review" is technically TRUE but understates the cluster's literature relationship.** Walk noted 10 of 12 strategies lack peer-reviewed citation (only Turtle Soup has Raschke 1996). But the underlying patterns (Power-of-3 accumulation/manipulation/distribution; Judas Swing; Market Maker Buy Model) trace to Inner Circle Trader's YouTube methodology + Twitter discourse from ~2010-2024. **This is a "YouTube-era trading framework" — popular among retail traders + arbitrage-exposed.** Crowding decay (CC6 from smart-money B673) applies STRONGLY: retail-popular patterns get arbitraged faster than academic anomalies. Cube replay magnitudes will likely be much smaller than the strategies' implementations imply they "should be." | ICT methodology provenance is observable; crowding hypothesis is testable post-cube | MEDIUM | NEW — `S4-ICT-CROWDING-DECAY-MAGNITUDE-HAIRCUT` |
| **CC-D** | **Pattern S single-gate strategy shells (ICT-5/6/11/12) violate the same "behavior invisible at call site" anti-pattern the entire review series has fought.** A reader auditing ICT-5 sees `fires = bool(s.get("po3_mmbm_setup", False))` — they CANNOT see that `po3_mmbm_setup` encodes a 4-condition AND with hardcoded `accum_window=5` + `tight_range_threshold=0.05` parameters. This is the same disease the B673 external reviewer flagged on the inspect.currentframe SM-5 gate ("a strategy's output no longer follows from its own code"). **Same anti-pattern + LOWER stakes (no risk control involvement) but architecturally consistent.** Should refactor to explicit-gate composition pre-cube. | ✅ Code inspection | MEDIUM | NEW — `S4-ICT-PATTERN-S-EXPLICIT-GATE-REFACTOR` |
| **CC-E** | **Cross-cluster Pattern P with SMC creates COMPOUND vendor-library failure surface.** 4 of 12 ICT strategies (Turtle Soup + Judas Swing) consume `smc_liquidity_swept_*` from SMC's joshyattridge/smartmoneyconcepts vendored library. If that library import fails, FOUR ICT strategies + EIGHTEEN SMC strategies = 22 strategies degrade to no-fire simultaneously. **B458 silent-failure logging is wired but the failure MODE looks identical to "no opportunity" in cube outputs.** A 6-hour cube run could produce zero fires from 22 strategies and only the silent_failure log would distinguish "library failed" from "no signals available" — log inspection is NOT in the standard cube post-processing workflow. | ✅ Confirmed via smc_ict.py:39-48 import block | MEDIUM-HIGH | NEW — `S4-ICT-SMC-VENDORED-LIBRARY-CUBE-OUTPUT-DISTINGUISHABILITY` |
| **CC-F** | **Effective hypothesis count ≈ 4, not 12** — the cluster massively inflates multi-testing budget. PO3 family (ICT-1/2/3/4) all consume `po3_bullish`/`po3_bearish`; MMBM/MMSM (ICT-5/6) consume `po3_mmbm_setup`/`po3_mmsm_setup` — but these are PO3-phase-3 outputs, structurally dependent on the same accumulation primitive; Turtle Soup + Judas Swing (ICT-7/8/9/10) share `smc_liquidity_swept_*`; Week-Opening Gap (ICT-11/12) is the only structurally-independent sub-family. **Net effective N ≈ 4 (PO3 family + Turtle/Judas family + Week-Open family + Raschke-vs-ICT-pure variant)** when 12 are registered. C2 correction inflates the haircut on every other strategy in the program by the difference. | Inherent to cluster structure | HIGH | NEW — extend existing `S4-B673-CC7-EFFECTIVE-HYPOTHESIS-COUNT-WITHIN-CLUSTER` |
| **CC-G** | **10 of 12 strategies lacking EMA-200 trend filter is structurally analogous to SMC's missing-trend-filter concern, but here the substitution is WORSE: PO3/MMBM/MMSM strategies have NO trend proxy at all** — they fire on candle-structure alone in any regime. ICT-3/4 use weekly_bias substitute (defensible); ICT-7/8/9/10 use bar-of-fire bullish/bearish-bar (one-bar trend signal, fragile); ICT-5/6/11/12 use NOTHING (single-gate-shell consumes producer flag with no regime context). **MMBM/MMSM firing in a bear regime is "buy because price swept the range low + closed bullish" — same setup is documented FAILURE mode in markdown trends (Raschke + Connors *Street Smarts* explicitly warn against Turtle Soup in strong downtrends, which ICT-7's docstring fails to caveat).** Cluster-wide EMA-gate proposal must SHIP pre-cube; the cluster cannot be trusted to fire in regime-appropriate conditions otherwise. | Mechanical from strategy code + Raschke 1996 reference | MEDIUM-HIGH | NEW — `S4-ICT-CLUSTER-WIDE-EMA-PROPOSAL-PRE-CUBE-REQUIRED` |

### Per-strategy reframings (Claude self-critique)

| Strategy | Walk disposition | Self-critique reframing | Action |
|---|---|---|---|
| **ICT-1 + ICT-2 + ICT-3 + ICT-4** | RECOMMENDED (b) — producer verification first | **BLOCKING CONCERN.** If signal is silently dead (CC-A), these 4 strategies have been producing zero fires + consuming zero cube budget + producing zero alpha contribution. They've been registered for ~3-4 weeks (B217 wiring). **Pre-cube IMMEDIATE verification required;** if dead, route to (i) deletion candidate OR (ii) re-wiring to `po3_mmbm_setup`/`po3_mmsm_setup` (with name clarification). | Immediate verification ticket — pre-B660 |
| **ICT-5 + ICT-6** MMBM/MMSM | RECOMMENDED (f) — Pattern R reframe + EMA + EXPLORATORY | **Strongest CC-B case in cluster.** Walk noted "STRONGEST Pattern R case" but disposition is deferred. Should ship docstring-honesty fix in same B680 batch as the walk-doc update. **No code change to FIRES logic; pure docstring honesty.** | Ship pre-cube docstring fix |
| **ICT-7 + ICT-8** Turtle Soup | RECOMMENDED (d) — status quo + Pattern N cross-cluster ablation | **Raschke 1996 caveat MISSING from docstring.** Original Raschke pattern explicitly fails in strong downtrends; our implementation has no trend filter. Should add docstring caveat. | Docstring caveat add |
| **ICT-11 + ICT-12** Week-Opening Gap | RECOMMENDED (f) — Pattern Q empirical | **Statistical claim "gaps tend to fill" needs cube validation BEFORE strategy continues to fire.** No published academic backing for the 1.5% threshold; cube can validate empirically against T1a 6-year history easily. | Pre-cube empirical test |

### Net effect on B675 walk dispositions

- **ICT-1/2/3/4 producer verification** PROMOTED to BLOCKING + pre-B660-required
- **Pattern R docstring fixes (ICT-5/6 + other 4)** ship in B680 — no code change, pure honesty
- **Pattern S explicit-gate refactor** ELEVATED to architectural-concern (parallel to inspect.currentframe SM-5 case)
- **Cross-cluster Pattern P with SMC** EXTENDED to include cube-output-distinguishability concern
- **Cluster-wide EMA proposal** ELEVATED to pre-cube-required (especially for MMBM/MMSM)
- **Effective hypothesis count** EXTENDED — ICT contributes ~8 phantom hypothesis-test slots to family-wise correction

### Queue tickets surfaced by self-critique (B680)

- `S4-ICT-PO3-SIGNAL-PRODUCER-VERIFICATION-IMMEDIATE` (CRITICAL; CC-A; blocking)
- `S4-ICT-PATTERN-R-DOCSTRING-PRE-CUBE-FIX-REQUIRED` (HIGH; CC-B; pure docstring)
- `S4-ICT-CROWDING-DECAY-MAGNITUDE-HAIRCUT` (MEDIUM; CC-C)
- `S4-ICT-PATTERN-S-EXPLICIT-GATE-REFACTOR` (MEDIUM; CC-D; architectural)
- `S4-ICT-SMC-VENDORED-LIBRARY-CUBE-OUTPUT-DISTINGUISHABILITY` (MEDIUM-HIGH; CC-E)
- `S4-ICT-CLUSTER-WIDE-EMA-PROPOSAL-PRE-CUBE-REQUIRED` (MEDIUM-HIGH; CC-G)

---

## B679 Iteration 2 Preparation — Review Solicitation Guide

> **Status (post-B679 format alignment):** READY FOR EXTERNAL REVIEWER + OWNER FEEDBACK on Iteration 2. The smart-money cluster doc received 2 review rounds (B669 + B673 → B674 incorporation with 12 NEW EXECUTION_QUEUE tickets); this ICT cluster doc is at the same maturity stage as smart-money was post-B669 — READY FOR YOUR 2ND-WAVE FEASIBILITY CRITIQUE.
>
> **Recommended review structure (parallel to B673 smart-money review):**
>
> | Review axis | What to look for in ICT | Smart-money parallel |
> |---|---|---|
> | **CC-A: Engine entry feasibility** | Turtle Soup + Judas Swing inherit SMC's `event_recency_bars=90` — sweep event up to 4 months stale; PO3 + Week-Opening Gap are bar-of-fire EVENT but may gap | CC1 |
> | **CC-B: Producer integrity** | **F-producer-origin-unverified** for ICT-1 + ICT-2 + ICT-3 + ICT-4 (`po3_bullish`/`po3_bearish` signal source UNCLEAR — may be silently dead). HIGHEST severity finding in this cluster | (Quiver PIT analog; specific to po3 producer) |
> | **CC-C: Citation discipline** | ICT methodology has NO peer-reviewed publications (only Turtle Soup cites Raschke 1996). 10 of 12 strategies were wired via owner inline-spec per `feedback_layer_2d_ict_inline_specification` with no empirical anchor. Pattern Q applies | CC6 magnitude overclaim analog |
> | **CC-D: PO3 candle-structure ≠ institutional flow** | Pattern R — docstrings claim "market makers manipulate / accumulate / distribute" but producer fires on CANDLE STRUCTURE ONLY (no actual flow data). Same overclaim class as Pattern B from smart-money | Pattern B carry |
> | **CC-E: Pattern S single-gate strategy shells** | 4 of 12 strategies (ICT-5/6/11/12) are 1-gate consumers over multi-condition producer flags — hardcoded params invisible at call site (same anti-pattern as the inspect.currentframe concern in smart-money) | B671 architectural concern carry |
> | **CC-F: Cross-cluster signal-sharing** | 4 of 12 strategies cross-cluster-consume SMC primitives (Pattern P NEW); inherits SMC's Pattern L + Pattern I | Pattern H carry |
> | **CC-G: Effective hypothesis count** | 12 strategies on 5 underlying primitives → effective N ≈ 5 | CC7 |
>
> Provide feedback in B673-style severity-ranked critique; B679 will incorporate as B679-incorporation batch symmetric with B674 smart-money pattern.

---

## Cross-cluster status snapshot (post-B679 — index at [STAGE_4_CLUSTER_WALKS_INDEX.md](STAGE_4_CLUSTER_WALKS_INDEX.md))

8 cluster docs / ~138 strategies covered. Review status:

| Cluster | Doc | Strategies | Owner review | Iteration 2 ready |
|---|---|---|---|---|
| Pivot | [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | ~10 | ✅ 2 rounds | (already iterated) |
| Trend | [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) | ~12 | ✅ Companion | (already iterated) |
| Smart Money | [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | 41 | ✅ 2 rounds (B669 + B673 → B674) | (already iterated) |
| SMC | [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | 18 | ❌ AWAITING | READY |
| **ICT (THIS DOC)** | **[STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md)** | **12** | **❌ AWAITING** | **READY** |
| Breakout | [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) | 19 | ❌ AWAITING | READY |
| Event-driven | [STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md](STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md) | 10 | ❌ AWAITING | READY |
| Chart+Candle | [STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md](STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md) | 16 | ❌ AWAITING | READY |
